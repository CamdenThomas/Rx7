/*
 * climate.h — DCU climate + comfort state and logic
 *
 * Mirrors the ICU pattern: all logic lives here, testable off-target;
 * cu.ino is only the Teensy host. Uses the shared can_map.h (copied
 * beside this file, same rule as the ICU — when it changes, both bump).
 *
 * Scope (D-011, D-073, D-081): HVAC door servos + comfort bus switching.
 * The A/C compressor stays on the factory switch (D-012). Vents and heat
 * only; the blower feed is PMU O16 with the factory fan switch in the path.
 *
 * Climate memory: restored from SD on wake — the DCU needs NO constant
 * keep-alive. That settles V-056 (see D-191); F13 goes to the radar feed.
 */

#ifndef CLIMATE_H
#define CLIMATE_H

#include <stdint.h>
#include <string.h>
#include "can_map.h"

/* ------------- servo channels (H-002 carrier pin map) -------------
 * Hobby servos pulling the existing HVAC door cables. Pulse in
 * microseconds; travel calibrated per door at commissioning, endpoints
 * stored on SD with the climate memory.                               */
enum servo_ch { SRV_MODE = 0, SRV_BLEND, SRV_RECIRC, SRV_COUNT };

typedef struct {
    uint16_t us_min;      /* calibrated endpoint             */
    uint16_t us_max;
    uint16_t us_now;      /* commanded position              */
} servo_cal_t;

/* ------------- comfort switching (F10/F11 branches) ------------- */
enum comfort_ch {
    CMF_SEAT_HEAT_DRV = 0, CMF_SEAT_HEAT_PASS,
    CMF_SEAT_COOL_DRV,     CMF_SEAT_COOL_PASS,
    CMF_MIRROR_HEAT,
    CMF_COUNT              /* 5: the nozzles and de-icer are cancelled (D-329) */
};

/* Blower level -> the duty % the final stage is commanded to, and what 0x300
 * byte 1 reports (D-308). The centre knob, after a push, moves one level per
 * detent, 0-3 (panel.h, D-492). 0 is off, always. */
static inline uint8_t blower_duty_pct(uint8_t level)
{
    if (level > 3) level = 3;
    return (uint8_t)((level * 100u + 1u) / 3u);   /* 0, 33, 67, 100 */
}

/* ------------- the dash-light level (SN31, D-577, D-578) -------------
 * One level for the dash lamps (the stage on pin 11), the panel's own lights
 * (lights.h) and the Display Unit (0x300 byte 6). Set from the centre knob
 * after a one-second hold of its push (panel.h); kept in the climate memory,
 * so it survives a sleep and a key cycle. Never below DASH_PCT_MIN: the knob
 * cannot put the dash out at night. */
#define DASH_PCT_MAX     100      /* full - the default and what a reset gives (D-577) */
#define DASH_PCT_MIN      10      /* confirm on the car: the dimmest still readable    */
#define DASH_PCT_STEP      5      /* a detent; 19 detents from dimmest to full         */

static inline uint8_t dash_clamp(int pct)
{
    return (uint8_t)(pct < DASH_PCT_MIN ? DASH_PCT_MIN : (pct > DASH_PCT_MAX ? DASH_PCT_MAX : pct));
}

/* ------------- the display level (SN32, D-580) -------------
 * The Display Unit's own brightness, set from the screen knob after a click
 * (screen_knob.h) and sent in 0x400 byte 5; the display runs at its day level
 * times this. Kept in the climate memory beside the dash level. */
#define DISP_PCT_MAX     100      /* full - the default (D-580) */
#define DISP_PCT_MIN      10      /* D-580: 10-100 %            */
#define DISP_PCT_STEP      5      /* a detent                   */

static inline uint8_t disp_clamp(int pct)
{
    return (uint8_t)(pct < DISP_PCT_MIN ? DISP_PCT_MIN : (pct > DISP_PCT_MAX ? DISP_PCT_MAX : pct));
}

/* ------------- persistent state (mirrors the SD file) ------------- */
typedef struct {
    uint8_t  mode;         /* climate_mode_t                  */
    uint8_t  blower;       /* level 0..3; sent as duty % (D-308) */
    uint8_t  target_c;
    uint8_t  recirc;       /* 0 fresh, 1 recirc               */
    uint8_t  seat_heat;    /* b0-1 drv level, b2-3 pass       */
    uint8_t  seat_cool;    /* b0-1 drv, b2-3 pass             */
    uint8_t  dash_pct;     /* the dash-light level, DASH_PCT_MIN..100 (D-578); a file
                            * from before it is the wrong size and loads the defaults */
    uint8_t  disp_pct;     /* the Display Unit's level, DISP_PCT_MIN..100, from the screen
                            * knob (D-580); was padding, so 0 reads as full (disp_level) */
    servo_cal_t cal[SRV_COUNT];
    uint32_t crc;
} climate_mem_t;

/* ------------- live state ------------- */
typedef struct {
    climate_mem_t mem;
    int8_t   cabin_c;      /* cabin sensor; TEMP_INVALID until read */
    uint8_t  comfort_on[CMF_COUNT];
    uint8_t  key_pos;      /* from 0x100                      */
    uint8_t  pmu_alive;    /* counter watchdog                */
    uint16_t bus_current_ca;
} dcu_state_t;

/* ------------- the one hard rule (D-073) -------------
 * A seat is never heated and cooled at once. Enforced HERE, at the
 * lowest level, so no command path can bypass it.                     */
static inline void enforce_seat_interlock(dcu_state_t *s)
{
    uint8_t h = s->mem.seat_heat, c = s->mem.seat_cool;
    if ((h & 0x03) && (c & 0x03)) c &= (uint8_t)~0x03;  /* driver: heat wins */
    if ((h & 0x0C) && (c & 0x0C)) c &= (uint8_t)~0x0C;  /* passenger         */
    s->mem.seat_cool = c;
    s->comfort_on[CMF_SEAT_HEAT_DRV]  = (h & 0x03) != 0;
    s->comfort_on[CMF_SEAT_HEAT_PASS] = (h & 0x0C) != 0;
    s->comfort_on[CMF_SEAT_COOL_DRV]  = (c & 0x03) != 0;
    s->comfort_on[CMF_SEAT_COOL_PASS] = (c & 0x0C) != 0;
}

/* Comfort loads only with the engine running and the PMU alive — the bus
 * is 14 A of mostly resistive heat and the alternator question is real
 * (D-179).                                                             */
static inline uint8_t comfort_permitted(const dcu_state_t *s)
{
    return (uint8_t)(s->key_pos == KEY_RUN && s->pmu_alive);
}

/* Map climate mode to servo targets. Real geometry is calibrated; these
 * are the logical positions.                                           */
static inline void mode_to_servos(dcu_state_t *s)
{
    climate_mem_t *m = &s->mem;
    servo_cal_t   *v = m->cal;
    uint16_t span = (uint16_t)(v[SRV_MODE].us_max - v[SRV_MODE].us_min);
    switch (m->mode) {
        case CLIM_VENT:    v[SRV_MODE].us_now = v[SRV_MODE].us_min;                    break;
        case CLIM_HEAT:    v[SRV_MODE].us_now = (uint16_t)(v[SRV_MODE].us_min + span / 2); break;
        case CLIM_DEFROST: v[SRV_MODE].us_now = v[SRV_MODE].us_max;                    break;
        default:           /* OFF / AC: leave the door where it is */                   break;
    }
    uint8_t t = m->target_c < 16 ? 16 : (m->target_c > 30 ? 30 : m->target_c);
    span = (uint16_t)(v[SRV_BLEND].us_max - v[SRV_BLEND].us_min);
    v[SRV_BLEND].us_now = (uint16_t)(v[SRV_BLEND].us_min + (uint32_t)span * (uint8_t)(t - 16) / 14u);
    v[SRV_RECIRC].us_now = m->recirc ? v[SRV_RECIRC].us_max : v[SRV_RECIRC].us_min;
}

/* Local climate edges. NOT the 0x400 bit map (that is PK_* in can_map.h,
 * F-016). Since D-492 panel.h's panel_apply() sets the climate memory from
 * the centre knob's modes itself and no longer comes through here; these
 * stay for any other caller and are held by test_dcu section 3. Hatch /
 * fuel-door / defog are the PMU's (D-180) and never reach here.        */
#define KP_MODE     (1u << 0)
#define KP_TEMP_UP  (1u << 1)
#define KP_TEMP_DN  (1u << 2)
#define KP_RECIRC   (1u << 3)

static inline void apply_keypad(dcu_state_t *s, uint8_t pressed_edges)
{
    if (pressed_edges & KP_MODE)   /* VENT -> HEAT -> DEFROST -> VENT; any
                                    * out-of-cycle value (OFF, AC, corrupt)
                                    * lands safely on VENT               */
        s->mem.mode = (uint8_t)((s->mem.mode == CLIM_VENT || s->mem.mode == CLIM_HEAT)
                                ? s->mem.mode + 1 : CLIM_VENT);
    if ((pressed_edges & KP_TEMP_UP) && s->mem.target_c < 30) s->mem.target_c++;
    if ((pressed_edges & KP_TEMP_DN) && s->mem.target_c > 16) s->mem.target_c--;
    if (pressed_edges & KP_RECIRC) s->mem.recirc ^= 1u;
    mode_to_servos(s);
}

/* ------------- climate memory integrity (SD file) -------------
 * Pure logic, so it lives here and gets covered by 00-design/tests/test_dcu.cpp;
 * cu.ino only does the SD I/O around it.                              */
static inline uint32_t mem_crc(const climate_mem_t *m)
{
    const uint8_t *p = (const uint8_t *)m; uint32_t c = 0xA5A5A5A5u;
    for (size_t i = 0; i < sizeof *m - sizeof m->crc; i++) c = (c << 1) ^ (c >> 30) ^ p[i];
    return c;
}

static inline void mem_defaults(climate_mem_t *m)
{
    memset(m, 0, sizeof *m);
    m->mode = CLIM_VENT; m->target_c = 21; m->dash_pct = DASH_PCT_MAX; m->disp_pct = DISP_PCT_MAX;
    for (int i = 0; i < SRV_COUNT; i++) { m->cal[i].us_min = 1000; m->cal[i].us_max = 2000; }
}

/* The level the memory holds; 0 is a file written before the field (its padding) - full. */
static inline uint8_t disp_level(const climate_mem_t *m)
{
    return m->disp_pct ? disp_clamp(m->disp_pct) : (uint8_t)DISP_PCT_MAX;
}

#endif /* CLIMATE_H */

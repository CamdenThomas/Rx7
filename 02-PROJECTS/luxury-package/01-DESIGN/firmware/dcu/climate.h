/*
 * climate.h — DCU climate + comfort state and logic
 *
 * Mirrors the ICU pattern: all logic lives here, testable off-target;
 * dcu.ino is only the Teensy host. Uses the shared can_map.h (copied
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
    CMF_MIRROR_HEAT,       CMF_NOZZLE,           CMF_DEICER,
    CMF_COUNT
};

/* ------------- persistent state (mirrors the SD file) ------------- */
typedef struct {
    uint8_t  mode;         /* climate_mode_t                  */
    uint8_t  blower;       /* 0..3 — display only for now     */
    uint8_t  target_c;
    uint8_t  recirc;       /* 0 fresh, 1 recirc               */
    uint8_t  seat_heat;    /* b0-1 drv level, b2-3 pass       */
    uint8_t  seat_cool;    /* b0-1 drv, b2-3 pass             */
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

/* Keypad edges: 0x400 buttons per D-031. Bit map provisional until the
 * keypad doc is final. Hatch / fuel-door / defog are PMU-owned (D-180)
 * and ignored here.                                                    */
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
 * Pure logic, so it lives here and gets covered by tests/test_dcu.cpp;
 * dcu.ino only does the SD I/O around it.                              */
static inline uint32_t mem_crc(const climate_mem_t *m)
{
    const uint8_t *p = (const uint8_t *)m; uint32_t c = 0xA5A5A5A5u;
    for (size_t i = 0; i < sizeof *m - sizeof m->crc; i++) c = (c << 1) ^ (c >> 30) ^ p[i];
    return c;
}

static inline void mem_defaults(climate_mem_t *m)
{
    memset(m, 0, sizeof *m);
    m->mode = CLIM_VENT; m->target_c = 21;
    for (int i = 0; i < SRV_COUNT; i++) { m->cal[i].us_min = 1000; m->cal[i].us_max = 2000; }
}

#endif /* CLIMATE_H */

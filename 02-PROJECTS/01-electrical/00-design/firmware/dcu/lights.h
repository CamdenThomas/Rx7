/*
 * lights.h — the panel's and the left plate's lights (D-458, D-492, F-018)
 *
 * Two constant-current I2C LED drivers on the panel's bus (Wire, SDA 18 /
 * SCL 19, the ribbon's PNL_SDA / PNL_SCL, panel_ribbon 22 / 24):
 *   U2 on the panel board  IS31FL3236A, 36 channels, 0x3C (P192, D-458)
 *   the plate's driver     IS31FL3218 class, 18 channels, 0x54 (P199, D-492),
 *                          reached through DP-DCU-E 9 / 10
 * lights_step() is the rules - which channel glows how much - and is pure;
 * lights_write() turns the result into register writes through one call the
 * host supplies, lights_hal_write() (dcu.ino: Wire; tests: a mock).
 *
 * Owns (R6), from 02-PROJECTS/01-electrical/data:
 *   parts            P192 (the panel's driver and its ~24 LEDs), P199 (the plate's
 *                    driver and its five symbol LEDs)
 *   panel_ribbon     22 / 24 the I2C pair, 26 +5V_PNL the LED anodes
 *   can_fields       0x100 byte 3 (headlight state), 0x120 O4 (the rear defogger)
 *   ideas            I-001, I-004, I-005, I-006 (what glows when), kept by D-492
 *
 * The rules (D-458 as D-492 amends it; I-004, I-005):
 *   - the knob's ring, the four key symbols, the two window symbols and the two
 *     seat symbols glow only with the lights on - 0x100 byte 3 PARK or HEAD on a
 *     live PMU, as the dash is lit (L3-S1 8) - at the dimmed backlight level;
 *   - a key's symbol is at full whenever its function is on, lights or not:
 *     rear defog (O4 in a fresh 0x120), mirror defog, recirculate, and the
 *     fan-mode key while the centre knob sets the mode;
 *   - the seat level arcs show the level at any time: n LEDs of the heat (red)
 *     or cool (blue) side for level n, nothing at OFF;
 *   - the plate's five symbols follow the lights; the wink faces go to full
 *     while pressed once the PMU exports A8's state (F-009) - until then the
 *     host passes 0 and they follow the lights only (D-492).
 *   - "at any time" means the car awake: the PMU alive and the key not OFF.
 *     With the key out, only what follows the lights glows (a parked car with
 *     its park lamps on lights its dash, as the factory did) - confirm.
 *
 * THE CHANNEL MAPS ARE THE FIRMWARE'S, NOT YET THE BOARDS' (confirm against
 * Y20's redrawn panel sheet and Y21's plate sheet). The panel map keeps every
 * channel D-380's board (cad/panel, H-008) gave a light that survives D-492:
 * OUT1 defog, OUT4 the mode key, OUT5 recirculate, OUT6 / OUT8 a window each,
 * OUT24-35 the seat arcs (cool 3, 2, 1, heat 1, 2, 3); the fan and temperature
 * arcs (OUT10-23) are gone, the screen shows those, and their channels take the
 * ring and the seat symbols.
 *
 *   panel, IS31FL3236A (OUTn = pwm[n-1])      plate, IS31FL3218 (OUTn = pwm[n-1])
 *   OUT1      rear-glass defog symbol         OUT1  wink left face
 *   OUT2      mirror defog symbol             OUT2  wink right face
 *   OUT3      -                               OUT3  hatch release symbol
 *   OUT4      fan-mode symbol                 OUT4  fuel-door release symbol
 *   OUT5      recirculate symbol              OUT5  mirror stick symbol
 *   OUT6      window DRV symbol (switch cap)  OUT6-18  -
 *   OUT7      -
 *   OUT8      window PASS symbol (switch cap)
 *   OUT9      -
 *   OUT10-13  the centre knob's ring (4 LEDs)
 *   OUT14-16  -
 *   OUT17     driver seat symbol (knob centre, I-005)
 *   OUT18     passenger seat symbol
 *   OUT19-23  -
 *   OUT24-29  driver seat arc: cool 3, cool 2, cool 1, heat 1, heat 2, heat 3
 *   OUT30-35  passenger seat arc, the same order
 *   OUT36     -
 */

#ifndef DCU_LIGHTS_H
#define DCU_LIGHTS_H

#include <stdint.h>
#include <string.h>
#include "can_map.h"

/* ------------------------- the drivers ------------------------- */
#define LED_PANEL_ADDR     0x3C   /* IS31FL3236A, AD to GND (P192, panel_ribbon 22) */
#define LED_PLATE_ADDR     0x54   /* IS31FL3218 (P199): fixed address              */
#define LED_PANEL_CH       36
#define LED_PLATE_CH       18

/* IS31FL3236A registers (datasheet, Lumissil; confirm against the fitted part) */
#define IS3236_SHUTDOWN    0x00   /* bit0 1 = normal operation                */
#define IS3236_PWM1        0x01   /* 0x01-0x24: OUT1-OUT36 duty, 0-255        */
#define IS3236_UPDATE      0x25   /* write 0x00: PWM and control take effect  */
#define IS3236_CTRL1       0x26   /* 0x26-0x49: bit0 on, bits 2:1 current     */
#define IS3236_GLOBAL      0x4A   /* bit0 1 = every output off                */
/* IS31FL3218 registers */
#define IS3218_SHUTDOWN    0x00
#define IS3218_PWM1        0x01   /* 0x01-0x12: OUT1-OUT18                    */
#define IS3218_CTRL1       0x13   /* 0x13-0x15: one bit per output, 6 a byte  */
#define IS3218_UPDATE      0x16

/* ------------------------- the channel maps (0-based: OUTn is n - 1) ------------------------- */
#define LP_DEFOG           0      /* OUT1  */
#define LP_MIRROR_DEFOG    1      /* OUT2  */
#define LP_FAN_MODE        3      /* OUT4  */
#define LP_RECIRC          4      /* OUT5  */
#define LP_WIN_DRV         5      /* OUT6  */
#define LP_WIN_PASS        7      /* OUT8  */
#define LP_RING0           9      /* OUT10-OUT13 */
#define LP_RING_N          4
#define LP_SEAT_DRV_SYM    16     /* OUT17 */
#define LP_SEAT_PASS_SYM   17     /* OUT18 */
#define LP_ARC_DRV0        23     /* OUT24-OUT29: cool 3, 2, 1, heat 1, 2, 3 */
#define LP_ARC_PASS0       29     /* OUT30-OUT35 */

#define LQ_WINK_L          0      /* plate OUT1 */
#define LQ_WINK_R          1
#define LQ_HATCH           2
#define LQ_FUEL_DOOR       3
#define LQ_MIRROR          4
#define LQ_USED            5

/* ------------------------- levels (PWM, 0-255) ------------------------- */
#define LIGHT_FULL         255    /* a function on, a seat level; confirm on the faceplate */
#define LIGHT_BACK          40    /* confirm: "dimmed with the dash" (D-458, D-462). The
                                   * dash dimmer's duty (O20) is not on CAN, so the DCU
                                   * cannot follow the knob: a fixed night level until
                                   * the PMU exports it                                  */

typedef struct {
    uint8_t pmu_alive;             /* 0x100's counter advancing                      */
    uint8_t key_pos;               /* 0x100 byte 0                                   */
    uint8_t headlight;             /* 0x100 byte 3: HL_OFF / HL_PARK / HL_HEAD       */
    uint8_t rear_defog;            /* O4 on in a fresh 0x120                         */
    uint8_t mirror_defog;          /* mirror_defog_t.on (panel.h)                    */
    uint8_t recirc;                /* climate memory                                 */
    uint8_t fan_mode_active;       /* the centre knob sets the mode (KNOB_MODE)      */
    int8_t  seat_drv, seat_pass;   /* -3 .. +3, seat_pos() (panel.h)                 */
    uint8_t wink_l, wink_r;        /* pressed - 0 until the PMU exports A8 (F-009)   */
} lights_in_t;

typedef struct {
    uint8_t panel[LED_PANEL_CH];
    uint8_t plate[LED_PLATE_CH];
} lights_out_t;

/* The lights are on as the dash is: PARK or HEAD, on a PMU that is alive.
 * A stale 0x100 is dark - blank, never hold. */
static inline uint8_t lights_on(const lights_in_t *in)
{
    return (uint8_t)(in->pmu_alive && (in->headlight == HL_PARK || in->headlight == HL_HEAD));
}

/* A seat's arc: level n lights n LEDs of its side, counted out from the middle. */
static inline void seat_arc(uint8_t *arc, int8_t pos)
{
    for (int i = 0; i < 6; i++) arc[i] = 0;
    if (pos > 3) pos = 3;
    if (pos < -3) pos = -3;
    for (int n = 1; n <= pos; n++)  arc[2 + n] = LIGHT_FULL;     /* heat 1 is index 3 */
    for (int n = 1; n <= -pos; n++) arc[3 - n] = LIGHT_FULL;     /* cool 1 is index 2 */
}

static inline void lights_step(const lights_in_t *in, lights_out_t *out)
{
    memset(out, 0, sizeof *out);
    uint8_t back  = lights_on(in) ? LIGHT_BACK : 0;
    uint8_t awake = (uint8_t)(in->pmu_alive && in->key_pos != KEY_OFF);
    uint8_t *p = out->panel;

    for (int i = 0; i < LP_RING_N; i++) p[LP_RING0 + i] = back;
    p[LP_WIN_DRV] = back;        p[LP_WIN_PASS] = back;
    p[LP_SEAT_DRV_SYM] = back;   p[LP_SEAT_PASS_SYM] = back;

    p[LP_DEFOG]        = (awake && in->rear_defog)      ? LIGHT_FULL : back;
    p[LP_MIRROR_DEFOG] = (awake && in->mirror_defog)    ? LIGHT_FULL : back;
    p[LP_RECIRC]       = (awake && in->recirc)          ? LIGHT_FULL : back;
    p[LP_FAN_MODE]     = (awake && in->fan_mode_active) ? LIGHT_FULL : back;

    if (awake) {
        seat_arc(&p[LP_ARC_DRV0],  in->seat_drv);
        seat_arc(&p[LP_ARC_PASS0], in->seat_pass);
    }

    uint8_t *q = out->plate;
    q[LQ_HATCH] = back; q[LQ_FUEL_DOOR] = back; q[LQ_MIRROR] = back;
    q[LQ_WINK_L] = in->wink_l ? LIGHT_FULL : back;
    q[LQ_WINK_R] = in->wink_r ? LIGHT_FULL : back;
}

/* ------------------------- the register writes ------------------------- */
/* The one call the host supplies: an I2C write of n bytes, the first the register;
 * 1 on an acknowledge. */
uint8_t lights_hal_write(uint8_t addr, const uint8_t *buf, uint8_t n);

#define LIGHTS_CHUNK      12      /* bytes of data a transaction - inside Wire's 32-byte buffer */
#define LIGHTS_RETRY_MS 1000      /* a silent driver is re-initialised this often */

typedef struct {
    uint8_t  ok_panel, ok_plate;
    uint8_t  sent_panel[LED_PANEL_CH], sent_plate[LED_PLATE_CH];
    uint32_t t_init;
} lights_t;

/* Consecutive registers from reg (both parts auto-increment), in chunks. */
static inline uint8_t is31_write(uint8_t addr, uint8_t reg, const uint8_t *v, uint8_t n)
{
    uint8_t buf[LIGHTS_CHUNK + 1];
    for (uint8_t i = 0; i < n; i = (uint8_t)(i + LIGHTS_CHUNK)) {
        uint8_t m = (uint8_t)((n - i) < LIGHTS_CHUNK ? (n - i) : LIGHTS_CHUNK);
        buf[0] = (uint8_t)(reg + i);
        memcpy(&buf[1], &v[i], m);
        if (!lights_hal_write(addr, buf, (uint8_t)(m + 1))) return 0;
    }
    return 1;
}
static inline uint8_t is31_reg(uint8_t addr, uint8_t reg, uint8_t value)
{
    return is31_write(addr, reg, &value, 1);
}

/* Every channel at 0 PWM, enabled at full current (R_EXT sets IMAX, P192 / R1),
 * the part out of shutdown. */
static inline uint8_t lights_init_panel(lights_t *l)
{
    uint8_t v[LED_PANEL_CH];
    memset(v, 0, sizeof v);
    memset(l->sent_panel, 0, sizeof l->sent_panel);
    uint8_t ok = is31_write(LED_PANEL_ADDR, IS3236_PWM1, v, LED_PANEL_CH);
    memset(v, 0x01, sizeof v);                                 /* on, IMAX */
    ok = (uint8_t)(ok && is31_write(LED_PANEL_ADDR, IS3236_CTRL1, v, LED_PANEL_CH)
                      && is31_reg(LED_PANEL_ADDR, IS3236_GLOBAL, 0x00)
                      && is31_reg(LED_PANEL_ADDR, IS3236_UPDATE, 0x00)
                      && is31_reg(LED_PANEL_ADDR, IS3236_SHUTDOWN, 0x01));
    return l->ok_panel = ok;
}
static inline uint8_t lights_init_plate(lights_t *l)
{
    uint8_t v[LED_PLATE_CH];
    memset(v, 0, sizeof v);
    memset(l->sent_plate, 0, sizeof l->sent_plate);
    const uint8_t ctrl[3] = { 0x3F, 0x3F, 0x3F };
    uint8_t ok = (uint8_t)(is31_write(LED_PLATE_ADDR, IS3218_PWM1, v, LED_PLATE_CH)
                           && is31_write(LED_PLATE_ADDR, IS3218_CTRL1, ctrl, 3)
                           && is31_reg(LED_PLATE_ADDR, IS3218_UPDATE, 0x00)
                           && is31_reg(LED_PLATE_ADDR, IS3218_SHUTDOWN, 0x01));
    return l->ok_plate = ok;
}

/* Writes only what changed since the last acknowledged frame, then latches it
 * with the update register. A driver that does not answer is retried every
 * LIGHTS_RETRY_MS; the other keeps working. Returns the transactions sent. */
static inline int lights_write(lights_t *l, const lights_out_t *o, uint32_t now)
{
    int sent = 0;
    if ((!l->ok_panel || !l->ok_plate) && (uint32_t)(now - l->t_init) >= LIGHTS_RETRY_MS) {
        l->t_init = now;
        if (!l->ok_panel) { lights_init_panel(l); sent++; }
        if (!l->ok_plate) { lights_init_plate(l); sent++; }
    }
    if (l->ok_panel && memcmp(l->sent_panel, o->panel, LED_PANEL_CH)) {
        l->ok_panel = (uint8_t)(is31_write(LED_PANEL_ADDR, IS3236_PWM1, o->panel, LED_PANEL_CH)
                                && is31_reg(LED_PANEL_ADDR, IS3236_UPDATE, 0x00));
        if (l->ok_panel) memcpy(l->sent_panel, o->panel, LED_PANEL_CH);
        else l->t_init = now;                       /* retried a full LIGHTS_RETRY_MS later */
        sent++;
    }
    if (l->ok_plate && memcmp(l->sent_plate, o->plate, LED_PLATE_CH)) {
        l->ok_plate = (uint8_t)(is31_write(LED_PLATE_ADDR, IS3218_PWM1, o->plate, LQ_USED)
                                && is31_reg(LED_PLATE_ADDR, IS3218_UPDATE, 0x00));
        if (l->ok_plate) memcpy(l->sent_plate, o->plate, LED_PLATE_CH);
        else l->t_init = now;
        sent++;
    }
    return sent;
}

#endif /* DCU_LIGHTS_H */

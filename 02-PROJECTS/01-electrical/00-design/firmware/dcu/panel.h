/*
 * panel.h — the DCU's panel, windows, mirrors, release select and wake (F-017)
 *
 * Same pattern as climate.h: all logic here, testable off-target
 * (tests/test_dcu.cpp); dcu.ino only reads pins, writes pins and moves frames.
 *
 * Owns (R6), from 02-PROJECTS/01-electrical/data:
 *   panel_ribbon     the 3 x 3 key matrix, four encoders, the thumbstick (D-380)
 *   dcu_channels     SN17 mirrors · SN18 thumbstick · SN19 keys · SN20 encoders ·
 *                    SN21 wake · SN22 windows · SN23 release select ·
 *                    SN11 / SN12 NTCs · SN13 comfort current · SN15 servo sequencing
 *   can_fields       0x400 (sent here); 0x120 bit O4 read for mirror heat
 * Rulings: D-355 D-359 (luxury), D-360 D-363 D-369 D-370 D-379 D-380, and the
 * behaviour choices of D-442.
 *
 * Every number marked `confirm` is a bench or car figure nobody has measured
 * (R11); F6 commissions it.
 */

#ifndef PANEL_H
#define PANEL_H

#include <stdint.h>
#include <string.h>
#include <math.h>
#include "can_map.h"
#include "climate.h"

/* ------------------------- timing (ms) ------------------------- */
#define KEY_DEBOUNCE_SCANS        4      /* 4 scans of 5 ms = 20 ms stable       */
#define KEY_HELD_MS            1000      /* 0x400 bytes 2-3 (F-016)              */
#define PANEL_TX_HEARTBEAT_MS   500      /* 0x400: on change + 2 Hz              */
#define WAKE_REQ_MAX_MS        3000      /* wake line held at most this long     */
#define REPLAY_MS               300      /* a press made asleep, replayed awake  */
#define RELEASE_HOLD_MS        1500      /* > the PMU release pulse (hundreds of
                                          * ms, logic ACCESSORY) + 0x400 latency;
                                          * confirm against the PMU config       */
#define WINDOW_DEAD_MS          100      /* both relays at rest before reversing */
#define WINDOW_MAX_RUN_MS     10000      /* confirm: longer than a full glass travel */
#define MIRROR_DEAD_MS           50      /* bridges off while the clutch settles */
#define MIRROR_MAX_RUN_MS     10000      /* confirm against the head's full travel */
#define SERVO_SETTLE_MS         600      /* one servo moves at a time (D-379)    */
#define DCU_SLEEP_AFTER_MS    30000      /* D-248's 30 s                         */

/* the keys the PMU acts on by edge (0x400 note); the rest are levels */
#define PK_EDGE_KEYS   (PK_DEFOG | PK_HATCH | PK_FUEL_DOOR)
#define PK_RELEASE     (PK_HATCH | PK_FUEL_DOOR)

/* ------------------------- key matrix (SN19) -------------------------
 * ROW1 defog · hatch · fuel door / ROW2 mode · recirc · DRV up /
 * ROW3 DRV down · PASS up · PASS down. The PK_* order is the matrix
 * row-major, so the bit is row * 3 + column (F-016, D-380).            */
#define PANEL_ROWS 3
#define PANEL_COLS 3
static inline uint16_t matrix_bit(uint8_t row, uint8_t col)
{
    return (uint16_t)(1u << (row * PANEL_COLS + col));
}

typedef struct {
    uint8_t  integ[PK_COUNT];     /* debounce integrators              */
    uint16_t phys, phys_prev;     /* debounced physical keys           */
    uint16_t latched;             /* edge keys pressed while asleep    */
    uint16_t virt;                /* ...replayed once the PMU is up    */
    uint32_t virt_t0;
    uint8_t  wake_req;            /* SN21                              */
    uint32_t wake_t0;
    uint16_t eff, eff_prev;       /* what 0x400 reports, before release masking */
    uint32_t since[PK_COUNT];
    uint16_t held;
    uint16_t rel_sel;             /* PK_HATCH, PK_FUEL_DOOR or 0 (SN23) */
    uint32_t rel_t0;
    uint16_t rel_blocked;         /* release keys refused until let go  */
} panel_t;

/* Debounce one scan. raw: PK_* bits read this scan (matrix + thumbstick
 * press). Returns the keys newly down. */
static inline uint16_t keys_debounce(panel_t *p, uint16_t raw)
{
    p->phys_prev = p->phys;
    for (uint8_t i = 0; i < PK_COUNT; i++) {
        uint16_t b = (uint16_t)(1u << i);
        if (raw & b) { if (p->integ[i] < KEY_DEBOUNCE_SCANS) p->integ[i]++; }
        else         { if (p->integ[i] > 0) p->integ[i]--; }
        if (p->integ[i] == KEY_DEBOUNCE_SCANS) p->phys |= b;
        else if (p->integ[i] == 0)             p->phys &= (uint16_t)~b;
    }
    return (uint16_t)(p->phys & ~p->phys_prev);
}

/* Wake (D-355, SN21). A press with the PMU asleep pulls the wake line; the
 * edge keys pressed meanwhile are latched and replayed once it is alive, so
 * the first press after sleep is late, never lost. A PMU that does not
 * answer in WAKE_REQ_MAX_MS drops both: a hatch must not pop minutes later.
 * Returns the keys as 0x400 should see them. */
static inline uint16_t wake_step(panel_t *p, uint16_t pressed, uint8_t pmu_alive, uint32_t now)
{
    if (!pmu_alive) {
        if (pressed) {
            if (!p->wake_req) p->wake_t0 = now;
            p->wake_req = 1;
            p->latched |= (uint16_t)(pressed & PK_EDGE_KEYS);
        }
        if (p->wake_req && (uint32_t)(now - p->wake_t0) >= WAKE_REQ_MAX_MS) {
            p->wake_req = 0; p->latched = 0;
        }
        p->virt = 0;
        /* no new edge while nobody can act on it; a key already reported
         * stays down, so a CAN hiccup never makes a second edge */
        return (uint16_t)((p->phys & ~PK_EDGE_KEYS) | (p->phys & p->eff_prev & PK_EDGE_KEYS));
    }
    p->wake_req = 0;
    if (p->latched) { p->virt = p->latched; p->virt_t0 = now; p->latched = 0; }
    if (p->virt && (uint32_t)(now - p->virt_t0) >= REPLAY_MS) p->virt = 0;
    return (uint16_t)(p->phys | p->virt);
}

/* Held >= 1 s, per key, on what 0x400 reports. */
static inline uint16_t held_step(panel_t *p, uint16_t eff, uint32_t now)
{
    uint16_t rose = (uint16_t)(eff & ~p->eff_prev);
    p->held = 0;
    for (uint8_t i = 0; i < PK_COUNT; i++) {
        uint16_t b = (uint16_t)(1u << i);
        if (rose & b) p->since[i] = now;
        if ((eff & b) && (uint32_t)(now - p->since[i]) >= KEY_HELD_MS) p->held |= b;
    }
    return p->held;
}

/* Release select (D-370, SN23). The DCU grounds K3 (hatch) or K4 (fuel door)
 * BEFORE the PMU sees the key's edge, and holds it through the pulse. Never
 * both: a second release key while one is selected, or both at once, is
 * refused and kept out of 0x400 until it is let go, so the PMU never fires a
 * pulse the DCU has not steered. Call after the edge on eff; returns the
 * release bits to clear from 0x400. */
static inline uint16_t release_step(panel_t *p, uint16_t eff, uint16_t eff_pressed, uint32_t now)
{
    p->rel_blocked &= eff;                                  /* let go: unblocked */
    if (p->rel_sel && (uint32_t)(now - p->rel_t0) >= RELEASE_HOLD_MS && !(eff & p->rel_sel))
        p->rel_sel = 0;
    uint16_t np = (uint16_t)(eff_pressed & PK_RELEASE & ~p->rel_blocked);
    if (np) {
        if (p->rel_sel == 0 && np != PK_RELEASE && !(eff & PK_RELEASE & ~np)) {
            p->rel_sel = np; p->rel_t0 = now;
        } else if (p->rel_sel == np) {
            p->rel_t0 = now;                                /* the same key again */
        } else {
            p->rel_blocked |= np;
        }
    }
    return (uint16_t)(p->rel_blocked & eff);
}

/* One scan, the whole key path. Fills the 0x400 down / held bits. */
static inline uint16_t panel_keys_step(panel_t *p, uint16_t raw, uint8_t pmu_alive, uint32_t now,
                                       uint16_t *down_out, uint16_t *held_out)
{
    uint16_t pressed = keys_debounce(p, raw);
    uint16_t eff     = wake_step(p, pressed, pmu_alive, now);
    uint16_t eff_pr  = (uint16_t)(eff & ~p->eff_prev);
    uint16_t held    = held_step(p, eff, now);
    uint16_t refuse  = release_step(p, eff, eff_pr, now);
    p->eff_prev = eff;
    *down_out = (uint16_t)(eff & ~refuse);
    *held_out = (uint16_t)(held & ~refuse);
    return pressed;                         /* physical edges, for local use */
}

/* ------------------------- 0x400 sender ------------------------- */
typedef struct { uint16_t down, held; uint32_t last_tx; uint8_t counter; uint8_t sent; } keys_tx_t;

/* On change, and every PANEL_TX_HEARTBEAT_MS (0x400: on change + 2 Hz). */
static inline uint8_t panel_frame_due(keys_tx_t *t, uint16_t down, uint16_t held, uint32_t now,
                                      panel_keys_t *out)
{
    if (t->sent && down == t->down && held == t->held
        && (uint32_t)(now - t->last_tx) < PANEL_TX_HEARTBEAT_MS) return 0;
    memset(out, 0, sizeof *out);
    out->down = down; out->held = held; out->counter = t->counter++;
    t->down = down; t->held = held; t->last_tx = now; t->sent = 1;
    return 1;
}

/* ------------------------- encoders (SN20) ------------------------- */
#define ENC_STEPS_PER_DETENT 4           /* confirm with the chosen part */

typedef struct { uint8_t ab; int8_t sub; } enc_t;

/* ab: bit1 = A, bit0 = B. Clockwise is 00 -> 01 -> 11 -> 10 -> 00; if a knob
 * reads backwards, swap its A and B in pins.h. Returns -1, 0 or
 * +1 detent. A bounce reverses its own count, so it never adds a detent. */
static inline int8_t enc_step(enc_t *e, uint8_t ab)
{
    static const int8_t T[16] = { 0, +1, -1, 0, -1, 0, 0, +1, +1, 0, 0, -1, 0, -1, +1, 0 };
    ab &= 3u;
    e->sub = (int8_t)(e->sub + T[(e->ab << 2) | ab]);
    e->ab = ab;
    if (e->sub >= ENC_STEPS_PER_DETENT)  { e->sub = 0; return +1; }
    if (e->sub <= -ENC_STEPS_PER_DETENT) { e->sub = 0; return -1; }
    return 0;
}

/* A seat knob is one position, -3..+3: clockwise from OFF is heat 1-3,
 * anticlockwise cool 1-3, so heat and cool are never both on (D-073,
 * D-380). shift 0 = driver, 2 = passenger in the seat_heat / seat_cool bytes. */
static inline int8_t seat_pos(const climate_mem_t *m, uint8_t shift)
{
    uint8_t h = (uint8_t)((m->seat_heat >> shift) & 3u), c = (uint8_t)((m->seat_cool >> shift) & 3u);
    return h ? (int8_t)h : (int8_t)-(int8_t)c;
}
static inline void seat_set(climate_mem_t *m, uint8_t shift, int pos)
{
    if (pos > 3) pos = 3;
    if (pos < -3) pos = -3;
    uint8_t mask = (uint8_t)(3u << shift);
    m->seat_heat = (uint8_t)((m->seat_heat & ~mask) | ((pos > 0 ? pos : 0) << shift));
    m->seat_cool = (uint8_t)((m->seat_cool & ~mask) | ((pos < 0 ? -pos : 0) << shift));
}

/* The panel's knobs and climate keys onto the climate memory. Detents are
 * signed counts since the last call. */
static inline void panel_apply(dcu_state_t *s, uint16_t pressed,
                               int fan, int temp, int seat_drv, int seat_pass)
{
    uint8_t kp = 0;
    if (pressed & PK_HVAC_MODE) kp |= KP_MODE;
    if (pressed & PK_RECIRC)    kp |= KP_RECIRC;
    apply_keypad(s, kp);
    for (; temp > 0; temp--) apply_keypad(s, KP_TEMP_UP);
    for (; temp < 0; temp++) apply_keypad(s, KP_TEMP_DN);
    int b = (int)s->mem.blower + fan;
    s->mem.blower = (uint8_t)(b < 0 ? 0 : (b > 3 ? 3 : b));
    if (seat_drv)  seat_set(&s->mem, 0, seat_pos(&s->mem, 0) + seat_drv);
    if (seat_pass) seat_set(&s->mem, 2, seat_pos(&s->mem, 2) + seat_pass);
    enforce_seat_interlock(s);
}

/* Windows and mirrors move only in ACC or RUN with the PMU alive: the PMU
 * gates their power anyway (O1, O15), and nothing clicks with the key out. */
static inline uint8_t body_permitted(const dcu_state_t *s)
{
    return (uint8_t)(s->pmu_alive && (s->key_pos == KEY_ACC || s->key_pos == KEY_RUN));
}

/* ------------------------- windows (SN22, D-363) -------------------------
 * One side = two relays, K5/K6 driver, K7/K8 passenger. Up and down are
 * never driven together; a reversal rests both relays first (the motor is
 * braked at rest); a key held past WINDOW_MAX_RUN_MS stops the motor until
 * it is let go. Which relay lifts the glass is confirm until it moves.   */
typedef struct { int8_t dir; uint8_t timed_out; uint32_t t_off, t_start; } window_t;

static inline void window_step(window_t *w, uint8_t up, uint8_t dn, uint8_t permitted,
                               uint32_t now, uint8_t *out_up, uint8_t *out_dn)
{
    int8_t want = (int8_t)((up && !dn) ? 1 : ((dn && !up) ? -1 : 0));
    if (!permitted) want = 0;
    if (want == 0) w->timed_out = 0;
    if (w->timed_out) want = 0;
    if (want != w->dir) {
        if (w->dir != 0) { w->dir = 0; w->t_off = now; }
        else if ((uint32_t)(now - w->t_off) >= WINDOW_DEAD_MS) { w->dir = want; w->t_start = now; }
    }
    if (w->dir != 0 && (uint32_t)(now - w->t_start) >= WINDOW_MAX_RUN_MS) {
        w->dir = 0; w->t_off = now; w->timed_out = 1;
    }
    *out_up = (uint8_t)(w->dir > 0);
    *out_dn = (uint8_t)(w->dir < 0);
}

/* ------------------------- mirrors (SN17, SN18, D-359, D-360) -------------
 * Both heads share a motor common and a clutch line; each has its own motor
 * line. The clutch picks the axis, the polarity the direction; only the
 * selected side's line is driven, the other stays open, so only that
 * mirror moves. Which axis the clutch selects, and which way is which, are
 * confirm until W-332 and the bench.                                     */
enum { MIRROR_LEFT = 0, MIRROR_RIGHT = 1 };
enum { HB_OFF = 0, HB_LOW, HB_HIGH };        /* a DRV8962 half-bridge */
enum { AXIS_NONE = 0, AXIS_X, AXIS_Y };

#define MIRROR_CLUTCH_AXIS  AXIS_Y           /* confirm (W-332) */
#define MIRROR_SIGN_X       1                /* confirm on the bench */
#define MIRROR_SIGN_Y       1

typedef struct { uint16_t cx, cy, dead; } stick_cal_t;   /* commissioning, 12-bit ADC */
typedef struct { uint8_t common, left, right, clutch; } mirror_out_t;
typedef struct {
    uint8_t  side;                            /* toggled by the stick press */
    uint8_t  axis; int8_t dir;                /* what is running now */
    uint8_t  timed_out;
    uint32_t t_off, t_start;
} mirror_t;

static inline void stick_defaults(stick_cal_t *c) { c->cx = 2048; c->cy = 2048; c->dead = 400; }

/* The larger deflection past the dead band wins; the other axis is ignored. */
static inline void stick_read(const stick_cal_t *c, uint16_t x, uint16_t y, uint8_t *axis, int8_t *dir)
{
    int dx = (int)x - (int)c->cx, dy = (int)y - (int)c->cy;
    int ax = dx < 0 ? -dx : dx, ay = dy < 0 ? -dy : dy;
    if (ax <= (int)c->dead && ay <= (int)c->dead) { *axis = AXIS_NONE; *dir = 0; return; }
    if (ax >= ay) { *axis = AXIS_X; *dir = (int8_t)(dx > 0 ? MIRROR_SIGN_X : -MIRROR_SIGN_X); }
    else          { *axis = AXIS_Y; *dir = (int8_t)(dy > 0 ? MIRROR_SIGN_Y : -MIRROR_SIGN_Y); }
}

static inline void mirror_step(mirror_t *m, uint16_t pressed, uint8_t axis, int8_t dir,
                               uint8_t permitted, uint32_t now, mirror_out_t *o)
{
    if (pressed & PK_MIRROR_PRESS) m->side ^= 1u;
    if (!permitted) { axis = AXIS_NONE; dir = 0; }
    if (axis == AXIS_NONE) m->timed_out = 0;
    if (m->timed_out) { axis = AXIS_NONE; dir = 0; }
    uint8_t running = (uint8_t)(m->axis != AXIS_NONE);
    if (axis != m->axis || dir != m->dir || (pressed & PK_MIRROR_PRESS)) {
        if (running) { m->axis = AXIS_NONE; m->dir = 0; m->t_off = now; }
        else if (axis != AXIS_NONE && (uint32_t)(now - m->t_off) >= MIRROR_DEAD_MS) {
            m->axis = axis; m->dir = dir; m->t_start = now;
        }
    }
    if (m->axis != AXIS_NONE && (uint32_t)(now - m->t_start) >= MIRROR_MAX_RUN_MS) {
        m->axis = AXIS_NONE; m->dir = 0; m->t_off = now; m->timed_out = 1;
    }
    memset(o, 0, sizeof *o);                              /* all open */
    /* the clutch follows the wanted axis through the dead time, so it has
     * settled before the motor turns */
    uint8_t clutch_axis = m->axis != AXIS_NONE ? m->axis : axis;
    o->clutch = (uint8_t)(clutch_axis == MIRROR_CLUTCH_AXIS);
    if (m->axis == AXIS_NONE) return;
    uint8_t line = m->dir > 0 ? HB_HIGH : HB_LOW;
    o->common = m->dir > 0 ? HB_LOW : HB_HIGH;
    if (m->side == MIRROR_LEFT) o->left = line; else o->right = line;
}

/* ------------------------- HVAC servos (SN15, D-379) -------------------------
 * The servo rail is sized for one servo moving at a time. A servo is sent a
 * new pulse only after the last one has had SERVO_SETTLE_MS; 0 in applied[]
 * means never driven, so dcu.ino attaches it only on its first move.   */
typedef struct { uint16_t applied[SRV_COUNT]; uint8_t next, moving; uint32_t t_move; } servo_seq_t;

static inline int servo_seq_step(servo_seq_t *q, const servo_cal_t cal[SRV_COUNT], uint32_t now)
{
    if (q->moving && (uint32_t)(now - q->t_move) < SERVO_SETTLE_MS) return -1;
    q->moving = 0;
    for (uint8_t k = 0; k < SRV_COUNT; k++) {
        uint8_t i = (uint8_t)((q->next + k) % SRV_COUNT);
        if (q->applied[i] != cal[i].us_now) {
            q->applied[i] = cal[i].us_now;
            q->moving = 1; q->t_move = now;
            q->next = (uint8_t)((i + 1) % SRV_COUNT);
            return i;
        }
    }
    return -1;
}

/* ------------------------- analog inputs -------------------------
 * 12-bit ADC over 3.3 V. */
#define ADC_FULL       4095u
#define NTC_BETA       3950.0f           /* confirm - the chosen NTC's datasheet (SN11) */
#define NTC_R25        10000.0f
#define NTC_PULLUP     10000.0f

/* SN11 / SN12: 10 k pull-up to 3V3, NTC to ground. Open, shorted or
 * implausible reads TEMP_INVALID - blank, never a fake number. */
static inline int8_t ntc_to_c(uint16_t adc)
{
    if (adc <= 20u || adc >= ADC_FULL - 20u) return TEMP_INVALID;
    float r = NTC_PULLUP * (float)adc / (float)(ADC_FULL - adc);
    float t = 1.0f / (1.0f / 298.15f + logf(r / NTC_R25) / NTC_BETA) - 273.15f;
    if (t < -40.0f || t > 85.0f) return TEMP_INVALID;
    return (int8_t)(t < 0 ? t - 0.5f : t + 0.5f);
}

/* SN13: INA180A1 (gain 20) over 5 mOhm = 100 mV per amp, so one millivolt
 * is one 0x310 count (0.01 A). zero: the no-load reading, commissioning. */
static inline uint16_t comfort_current_ca(uint16_t adc, uint16_t zero)
{
    if (adc <= zero) return 0;
    return (uint16_t)(((uint32_t)(adc - zero) * 3300u) / ADC_FULL);
}

/* ------------------------- mirror heat (SN16, D-369) -------------------------
 * Mirror heat follows the rear defogger, as Mazda wires it (luxury D-332,
 * D-442): on while the PMU reports O4 on in 0x120, off when 0x120 is stale. */
#define PMU_OUT_DEFOG  3                 /* O4 = index 3 (0x120 bytes 2-4, LSB first) */

static inline uint8_t pmu_out_on(const pmu_outputs_t *m, uint8_t index)
{
    return (uint8_t)((m->out_state[index >> 3] >> (index & 7u)) & 1u);
}

/* ------------------------- sleep (D-248, D-350) ------------------------- */
static inline uint8_t sleep_due(const panel_t *p, uint8_t pmu_alive, uint32_t idle_ms)
{
    return (uint8_t)(!pmu_alive && !p->wake_req && !p->phys && !p->latched
                     && idle_ms >= DCU_SLEEP_AFTER_MS);
}

#endif /* PANEL_H */

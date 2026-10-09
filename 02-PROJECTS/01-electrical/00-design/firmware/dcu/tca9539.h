/*
 * tca9539.h — the TCA9539-Q1 I2C expander and the slow lines it carries:
 * the mirror driver, the PROFETs' diagnosis pins, CAN STB, power-good
 * (F-017, D-452)
 *
 * Same pattern as panel.h: the logic is here and tested off-target
 * (tests/test_dcu.cpp); the bus is four calls the host supplies, as bt817.h
 * does - dcu.ino implements them on Wire and pins 12 / 13, the tests mock them:
 *
 *   uint8_t exp_hal_write(uint8_t addr, const uint8_t *buf, uint8_t n)   1 = acknowledged
 *   uint8_t exp_hal_read(uint8_t addr, uint8_t reg, uint8_t *buf, uint8_t n)
 *   void    exp_hal_reset(uint8_t asserted)                              RESET is active low
 *   void    exp_hal_delay_us(uint32_t us)
 *
 * Owns (R6), from 02-PROJECTS/01-electrical/data:
 *   dcu_channels   SN17 (DRV8962 on P00-P10, INT 12, RESET 13), SN22 / SN16 (DEN,
 *                  DSEL on P11-P14), SN26 (STB on P15), SN24 (power-good on P16)
 * Rulings: D-360, D-379, D-452.
 *
 * TCA9539 registers (TI datasheet): input 0x00 / 0x01, output 0x02 / 0x03,
 * polarity 0x04 / 0x05, configuration 0x06 / 0x07 (1 = input). After a
 * reset every port is an input and the OUTPUT registers read 0xFF - so the
 * output registers are written low BEFORE any port is made an output, or
 * nSLEEP, every EN and STB would come up high for one transaction.
 */

#ifndef TCA9539_H
#define TCA9539_H

#include <stdint.h>
#include "pins.h"
#include "panel.h"

uint8_t exp_hal_write(uint8_t addr, const uint8_t *buf, uint8_t n);
uint8_t exp_hal_read(uint8_t addr, uint8_t reg, uint8_t *buf, uint8_t n);
void    exp_hal_reset(uint8_t asserted);
void    exp_hal_delay_us(uint32_t us);

/* A0 (pin 21) and A1 (pin 2) are tied to GND on the sheet, which is 0x74.
 * No record row states the strap: confirm when dcu_channels names it.     */
#define TCA9539_ADDR        0x74

#define TCA_REG_INPUT0      0x00
#define TCA_REG_OUTPUT0     0x02
#define TCA_REG_POLARITY0   0x04
#define TCA_REG_CONFIG0     0x06

#define EXP_RESET_HOLD_US     10      /* datasheet minimum is nanoseconds   */
#define EXP_RESET_RECOVER_US  10
#define EXP_POLL_MS          100      /* inputs read this often even with no INT */
#define EXP_RETRY_MS        1000      /* a silent expander is reset and re-tried */

/* DRV8962: OCPM is tied low on the sheet, so an over-current LATCHES the
 * bridges off and pulls nFAULT; nSLEEP low clears it (confirm against the
 * datasheet's OCPM / nSLEEP reset wording). The clear goes through the
 * expander's RESET: every port turns input, R35 pulls nSLEEP low, and the
 * driver sleeps until it is woken again - the same path as boot.          */
#define DRV_WAKE_MS            2      /* nSLEEP high to first EN: confirm (tWAKE) */
#define DRV_FAULT_REST_MS   1000      /* a fault rests this long before a clear   */
#define DRV_FAULT_MAX_CLEARS   3      /* per key cycle; then the mirrors stay off */

/* ------------------------- the driver ------------------------- */
typedef struct {
    uint16_t out;          /* what the output registers hold */
    uint16_t in;           /* last input read                */
    uint8_t  ok;           /* every transaction since init acknowledged */
} tca9539_t;

/* A register pair in one transaction: the TCA9539 moves to the pair's other
 * register after the first data byte. */
static inline uint8_t tca_write16(tca9539_t *x, uint8_t reg, uint16_t v)
{
    const uint8_t b[3] = { reg, (uint8_t)(v & 0xFF), (uint8_t)(v >> 8) };
    uint8_t ack = exp_hal_write(TCA9539_ADDR, b, 3);
    if (!ack) x->ok = 0;
    return ack;
}

/* Reads both input ports, which also clears INT. */
static inline uint8_t tca_read_inputs(tca9539_t *x)
{
    uint8_t b[2] = { 0, 0 };
    if (!exp_hal_read(TCA9539_ADDR, TCA_REG_INPUT0, b, 2)) { x->ok = 0; return 0; }
    x->in = (uint16_t)(b[0] | (b[1] << 8));
    return 1;
}

/* Boot, a silent expander, and the DRV8962's latched over-current all come
 * here: RESET pulsed, outputs written low (nSLEEP low, every EN off, STB low
 * = CAN normal), polarity plain, then the directions, then one read. */
static inline uint8_t exp_reset_init(tca9539_t *x)
{
    exp_hal_reset(1);
    exp_hal_delay_us(EXP_RESET_HOLD_US);
    exp_hal_reset(0);
    exp_hal_delay_us(EXP_RESET_RECOVER_US);
    x->ok = 1;
    x->out = 0;
    tca_write16(x, TCA_REG_OUTPUT0, 0);
    tca_write16(x, TCA_REG_POLARITY0, 0);
    tca_write16(x, TCA_REG_CONFIG0, EXP_INPUTS);
    tca_read_inputs(x);
    return x->ok;
}

/* Write the output word, only on a change. An enabled half-bridge whose IN
 * changes is first opened in a write of its own, so no single write flips a
 * live bridge from one rail to the other (mirror_step already rests the
 * bridges on a reversal - this holds even if it did not). */
static inline uint16_t exp_open_first(uint16_t prev, uint16_t next)
{
    static const uint16_t IN[3] = { EXP_MIR_IN1, EXP_MIR_IN2, EXP_MIR_IN3 };
    static const uint16_t EN[3] = { EXP_MIR_EN1, EXP_MIR_EN2, EXP_MIR_EN3 };
    uint16_t mid = prev;
    for (int i = 0; i < 3; i++)
        if ((prev & EN[i]) && (next & EN[i]) && ((prev ^ next) & IN[i])) mid &= (uint16_t)~EN[i];
    return mid;
}
static inline uint8_t exp_write_outputs(tca9539_t *x, uint16_t next)
{
    next &= (uint16_t)(EXP_OUTPUTS & ~EXP_CAN_STB);   /* STB is never raised (D-452) */
    if (next == x->out) return 1;
    uint16_t mid = exp_open_first(x->out, next);
    if (mid != x->out) { if (!tca_write16(x, TCA_REG_OUTPUT0, mid)) return 0; x->out = mid; }
    if (!tca_write16(x, TCA_REG_OUTPUT0, next)) return 0;
    x->out = next;
    return 1;
}

/* ------------------------- the DCU's word ------------------------- */
static inline uint16_t hb_bits(uint8_t hb, uint16_t in, uint16_t en)
{
    if (hb == HB_OFF) return 0;
    return (uint16_t)(en | (hb == HB_HIGH ? in : 0));
}

/* The output word from the mirror step. awake: nSLEEP high. live: the
 * driver is awake, settled and not faulted - otherwise every EN is off.
 * DEN / DSEL stay low (the IS lines are unread, D-452) and STB stays low,
 * always: the transceiver is in normal mode whenever the DCU runs.       */
static inline uint16_t exp_word(const mirror_out_t *mo, uint8_t awake, uint8_t live)
{
    uint16_t w = awake ? EXP_MIR_NSLEEP : 0;
    if (awake && live) {
        w |= hb_bits(mo->common, EXP_MIR_IN1, EXP_MIR_EN1);
        w |= hb_bits(mo->left,   EXP_MIR_IN2, EXP_MIR_EN2);
        w |= hb_bits(mo->right,  EXP_MIR_IN3, EXP_MIR_EN3);
        if (mo->clutch) w |= EXP_MIR_EN4;
    }
    return (uint16_t)(w & ~EXP_CAN_STB);
}

/* ------------------------- DRV8962 guard -------------------------
 * awake follows permitted (ACC / RUN with the PMU alive): asleep otherwise,
 * which is also the driver's low-power state. nFAULT is believed only once
 * the driver has been awake DRV_WAKE_MS. A fault opens everything; it is
 * cleared - the expander reset - only after DRV_FAULT_REST_MS AND with the
 * stick let go, so a held stick on a jammed head is not a retry loop; after
 * DRV_FAULT_MAX_CLEARS the mirrors stay off until the key is cycled.     */
enum { DRV_NONE = 0, DRV_CLEAR };

typedef struct {
    uint8_t  awake, fault, clears;
    uint32_t wake_t0, fault_t0;
} drv_guard_t;

static inline uint8_t drv_live(const drv_guard_t *g, uint32_t now)
{
    return (uint8_t)(g->awake && !g->fault && (uint32_t)(now - g->wake_t0) >= DRV_WAKE_MS);
}

static inline uint8_t drv_guard_step(drv_guard_t *g, uint8_t nfault_low, uint8_t permitted,
                                     uint8_t stick_idle, uint32_t now)
{
    if (!permitted) {                         /* key out or PMU gone: asleep, tries refilled */
        g->awake = 0; g->fault = 0; g->clears = 0;
        return DRV_NONE;
    }
    if (g->fault) {
        if (g->clears < DRV_FAULT_MAX_CLEARS && stick_idle
            && (uint32_t)(now - g->fault_t0) >= DRV_FAULT_REST_MS) {
            g->clears++; g->fault = 0; g->awake = 0;   /* the reset puts it to sleep */
            return DRV_CLEAR;
        }
        if (g->clears >= DRV_FAULT_MAX_CLEARS) g->awake = 0;   /* given up: asleep */
        return DRV_NONE;
    }
    if (!g->awake) { g->awake = 1; g->wake_t0 = now; return DRV_NONE; }
    if (nfault_low && (uint32_t)(now - g->wake_t0) >= DRV_WAKE_MS) {
        g->fault = 1; g->fault_t0 = now;
    }
    return DRV_NONE;
}

#endif /* TCA9539_H */

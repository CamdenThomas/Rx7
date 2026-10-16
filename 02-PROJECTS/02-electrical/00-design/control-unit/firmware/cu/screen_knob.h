/*
 * screen_knob.h — the screen knob: the Display Unit's pages and brightness (F-020)
 *
 * D-580 moved the Display Unit's page button onto a knob the DCU reads, and D-581
 * put that knob on the CUR. It is a detented encoder with a push on an I2C
 * encoder board (Adafruit 4991, a seesaw chip at 0x36) on the panel's I2C bus:
 * the board counts the detents itself, so a slow poll loses none. What it does:
 *   PAGES    by default - a detent steps the Display Unit's page, clockwise to
 *            the next; sent as a rolling count (0x400 byte 4), so the Display
 *            Unit steps by the difference and a lost frame loses no step;
 *   BRIGHT   after a click - anticlockwise brighter, clockwise dimmer, DISP_PCT_STEP
 *            a detent, DISP_PCT_MIN..100 (climate.h), kept in the climate memory
 *            and sent in 0x400 byte 5;
 * back to PAGES after SKNOB_REST_MS with no turn, or on a second click. A click is
 * a push let go before KEY_HELD_MS with no turn while it was down: a longer push is
 * a hold (0x400 byte 3 b6) - the Display Unit opens pairing on a 3 s one (D-494 as
 * D-580 amends it) - and changes nothing here. The push itself is PK_SCREEN_PUSH,
 * debounced and held with the other keys (panel.h).
 *
 * Pure, so 00-design/tests/test_dcu.cpp holds it; cu.ino moves the bytes.
 *
 * Owns (R6), from 02-PROJECTS/02-electrical/data:
 *   dcu_channels  SN32 (the knob, its board, its behaviour)
 *   can_fields    0x400/1 b6, 0x400/3 b6, 0x400/4 (the count), 0x400/5 (the level)
 *   parts         P219 (the encoder board)
 * Rulings: D-580, D-581, D-494 (pairing, its trigger amended).
 */

#ifndef SCREEN_KNOB_H
#define SCREEN_KNOB_H

#include <stdint.h>
#include "can_map.h"
#include "panel.h"      /* KEY_HELD_MS, and climate.h's display level */

/* ------------- the seesaw board (Adafruit 4991, its seesaw register map) ------------- */
#define SKNOB_ADDR          0x36   /* the board's default; apart from the panel's LED driver
                                    * (0x3C) and the plate's (0x54) - confirm against the
                                    * screen (P201) when it is picked */
#define SS_STATUS_BASE      0x00
#define SS_STATUS_HW_ID     0x01
#define SS_GPIO_BASE        0x01
#define SS_GPIO_DIRCLR_BULK 0x03
#define SS_GPIO_BULK        0x04
#define SS_GPIO_BULK_SET    0x05
#define SS_GPIO_PULLENSET   0x0B
#define SS_ENCODER_BASE     0x11
#define SS_ENCODER_DELTA    0x40   /* int32, big-endian; reading it clears it */
#define SKNOB_PUSH_PIN      24     /* the board's push, to ground with the pull-up on */
#define SKNOB_SIGN          (-1)   /* confirm on the bench: the board counts anticlockwise up,
                                    * as Adafruit's own example negates it */
/* A register is asked for on one pass of cu.ino's loop and read on the next, 5 ms on: the
 * seesaw needs time between the two (confirm against the board's own timing). */
#define SKNOB_RETRY_MS      1000   /* a silent board is set up again this often */
#define SKNOB_REST_MS       3000   /* D-580: back to pages after 3 s at rest */

/* The three writes that make the push an input with its pull-up: register pair, then
 * the pin mask big-endian. frame: 6 bytes. */
static inline void sknob_pin_frame(uint8_t *frame, uint8_t reg)
{
    uint32_t mask = (uint32_t)1u << SKNOB_PUSH_PIN;
    frame[0] = SS_GPIO_BASE; frame[1] = reg;
    frame[2] = (uint8_t)(mask >> 24); frame[3] = (uint8_t)(mask >> 16);
    frame[4] = (uint8_t)(mask >> 8);  frame[5] = (uint8_t)mask;
}
static const uint8_t SKNOB_SETUP_REGS[3] = { SS_GPIO_DIRCLR_BULK, SS_GPIO_PULLENSET, SS_GPIO_BULK_SET };

/* ENCODER_DELTA's four bytes: the detents since the last read, clockwise positive. */
static inline int sknob_delta(const uint8_t *b)
{
    int32_t raw = (int32_t)(((uint32_t)b[0] << 24) | ((uint32_t)b[1] << 16) | ((uint32_t)b[2] << 8) | b[3]);
    if (raw > 1000 || raw < -1000) return 0;          /* a garbled read, not a spin */
    return (int)raw * SKNOB_SIGN;
}

/* GPIO_BULK's four bytes: the push is down when its pin reads low. */
static inline uint8_t sknob_push(const uint8_t *b)
{
    uint32_t v = ((uint32_t)b[0] << 24) | ((uint32_t)b[1] << 16) | ((uint32_t)b[2] << 8) | b[3];
    return (uint8_t)!((v >> SKNOB_PUSH_PIN) & 1u);
}

/* ------------- what the knob sets ------------- */
enum { SKNOB_PAGES = 0, SKNOB_BRIGHT };

typedef struct {
    uint8_t  mode;          /* SKNOB_*                                   */
    uint8_t  count;         /* the page count, rolling (0x400 byte 4)    */
    uint8_t  push_prev;     /* the push as 0x400 reported it last scan   */
    uint8_t  turned;        /* a detent while the push was down          */
    uint32_t t_press;       /* the push went down                        */
    uint32_t t_last;        /* the last detent, press or release         */
} sknob_t;

/* One scan. down: 0x400's down bits (panel_keys_step), so the push is debounced and
 * masked as every key is; detents: clockwise positive, since the last call; level:
 * the climate memory's display level, stepped in BRIGHT. */
static inline void sknob_step(sknob_t *k, uint8_t *level, uint16_t down, int detents, uint32_t now)
{
    uint8_t push = (uint8_t)((down & PK_SCREEN_PUSH) != 0);
    if (k->mode == SKNOB_BRIGHT && !push && (uint32_t)(now - k->t_last) >= SKNOB_REST_MS)
        k->mode = SKNOB_PAGES;
    if (push && !k->push_prev) { k->t_press = now; k->turned = 0; k->t_last = now; }
    if (!push && k->push_prev) {
        if (!k->turned && (uint32_t)(now - k->t_press) < KEY_HELD_MS)
            k->mode = (uint8_t)(k->mode == SKNOB_PAGES ? SKNOB_BRIGHT : SKNOB_PAGES);
        k->t_last = now;
    }
    if (detents) {
        k->t_last = now;
        if (push) k->turned = 1;
        if (k->mode == SKNOB_PAGES) k->count = (uint8_t)(k->count + detents);
        else *level = disp_clamp((int)disp_clamp(*level ? *level : DISP_PCT_MAX) - detents * DISP_PCT_STEP);
    }
    k->push_prev = push;
}

#endif /* SCREEN_KNOB_H */

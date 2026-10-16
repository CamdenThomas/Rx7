/*
 * screen_knob_rx.h — the screen knob as the Display Unit hears it (D-580, F-020)
 *
 * The knob is the DCU's (on the CUR, D-581); the Display Unit only reads 0x400:
 *   byte 4  a rolling count of detents on pages - the page steps by the
 *           difference from the last frame, so a lost frame loses no step; the
 *           first frame after boot or a timeout only sets the reference;
 *   byte 5  the display level (dimming.h's dim_on_panel);
 *   byte 1 b6 the push - held SKNOB_PAIR_HOLD_MS with no detent and no level
 *           step opens pairing for 60 s (D-494, its trigger moved by D-580);
 *           once a hold, not again until it is let go.
 * On a timeout (TMO_PANEL_KEYS) the page and the level stay where they are.
 * Pure, so 00-design/tests/test_suite.cpp holds it; du.ino turns the steps into
 * cluster pages and the pairing into a link frame. Pin 25 (IC22) is no longer
 * read: the page button is gone.
 *
 * Owns (R6), from 02-PROJECTS/02-electrical/data:
 *   can_fields    0x400/1 b6, 0x400/4, 0x400/5
 *   icu_channels  IC22 (spare - not read)
 */

#ifndef ICU_SCREEN_KNOB_RX_H
#define ICU_SCREEN_KNOB_RX_H

#include <stdint.h>
#include "can_map.h"

#define SKNOB_PAIR_HOLD_MS 3000   /* D-580: "holding the knob's push for 3 s" */

typedef struct {
    uint8_t  have;          /* a reference count since boot or the last timeout */
    uint8_t  count;         /* byte 4 last frame                                */
    uint8_t  push;          /* the push down last frame                         */
    uint8_t  spent;         /* this hold has opened pairing, or was spoiled     */
    uint8_t  level;         /* byte 5 when the push went down                   */
    uint32_t t_push;
    uint32_t t_rx;          /* the last frame                                   */
} sknob_rx_t;

/* One frame. Returns the pages to step (signed); *pair set to 1 when this frame
 * completes a pairing hold. */
static inline int sknob_rx_frame(sknob_rx_t *r, const panel_keys_t *f, uint32_t now, uint8_t *pair)
{
    *pair = 0;
    if (r->have && (uint32_t)(now - r->t_rx) > TMO_PANEL_KEYS) r->have = 0;   /* a gap: new reference */
    int steps = r->have ? (int)(int8_t)(uint8_t)((uint8_t)f->screen_count - r->count) : 0;
    uint8_t push = (uint8_t)((f->down & PK_SCREEN_PUSH) != 0);
    if (push && (!r->push || !r->have)) { r->t_push = now; r->spent = 0; r->level = f->disp_pct; }
    if (push && (steps || f->disp_pct != r->level)) r->spent = 1;           /* turned: not a pairing hold */
    if (push && !r->spent && (uint32_t)(now - r->t_push) >= SKNOB_PAIR_HOLD_MS) { *pair = 1; r->spent = 1; }
    r->push = push;
    r->count = (uint8_t)f->screen_count;
    r->have = 1;
    r->t_rx = now;
    return steps;
}

#endif /* ICU_SCREEN_KNOB_RX_H */

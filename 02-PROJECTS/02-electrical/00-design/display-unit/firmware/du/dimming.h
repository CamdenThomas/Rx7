/*
 * dimming.h — the Display Unit's backlight follows the dash (D-577, F-019)
 *
 * One setting dims the dash lamps, the climate panel and this display: the
 * DCU's dash-light level, sent in 0x300 byte 6. IC14 (DP-ICU-A 2, the O20
 * bus through a divider to A7) says only whether the lights are on:
 *   - lights off: the display at its day level;
 *   - lights on:  the display at the level 0x300 last carried;
 *   - 0x300 stale (TMO_DCU_CLIMATE): the last level is kept, not dropped -
 *     a DCU that goes quiet at night does not flash the display to full;
 *   - no 0x300 since boot: the day level.
 * Since D-580 the screen knob sets the display's own level too (0x400 byte 5,
 * 10-100 %, kept on a timeout): the display runs at its day level times it,
 * and with the lights on the dash level scales that again; the floor stays.
 * Pure, so 00-design/tests/test_suite.cpp holds it; du.ino reads the pin and
 * writes the BT817's REG_PWM_DUTY.
 *
 * Owns (R6), from 02-PROJECTS/02-electrical/data:
 *   icu_channels  IC14 (the reference: on / off, A7)
 *   can_fields    0x300/6 (the dash-light duty, % 0-100), 0x400/5 (the display level)
 *   log_channels  LC52 (the level the display runs at, % - 0 with the lights off)
 */

#ifndef ICU_DIMMING_H
#define ICU_DIMMING_H

#include <stdint.h>

#define DIM_PWM_FULL      128   /* the BT817's REG_PWM_DUTY range is 0-128          */
#define DIM_PWM_MIN         8   /* confirm: the dimmest the panel is still readable  */

/* IC14 on its 12-bit ADC: the divider is the carrier sheet's - read on above
 * ON, off below OFF, the gap is the hysteresis. Thresholds as fractions of
 * full scale, chosen for a divider that puts 12-14 V near the top of the
 * range (confirm against the sheet's resistors and on the bench). */
#define IC14_ADC_FULL    4095
#define IC14_ON_COUNTS   (IC14_ADC_FULL * 2 / 5)
#define IC14_OFF_COUNTS  (IC14_ADC_FULL * 1 / 4)

typedef struct {
    uint8_t have;      /* a 0x300 seen since boot   */
    uint8_t pct;       /* its byte 6, 0..100         */
    uint8_t lights;    /* IC14 reads on              */
    uint8_t disp;      /* 0x400 byte 5, 10..100; 0 until a frame - read as full (D-580) */
} dim_t;

static inline void dim_on_panel(dim_t *d, uint8_t disp_pct)
{
    d->disp = disp_pct > 100 ? 100 : (disp_pct < 10 ? 10 : disp_pct);
}

static inline void dim_on_frame(dim_t *d, uint8_t dash_pct)
{
    d->pct = dash_pct > 100 ? 100 : dash_pct;
    d->have = 1;
}

static inline void dim_on_ic14(dim_t *d, uint16_t counts)
{
    if (counts >= IC14_ON_COUNTS) d->lights = 1;
    else if (counts <= IC14_OFF_COUNTS) d->lights = 0;
}

/* The level the display runs at, % - the log's LC52. */
static inline uint8_t dim_pct(const dim_t *d)
{
    if (!d->lights) return 0;
    return d->have ? d->pct : 100;
}

/* REG_PWM_DUTY for it: the day level times the knob's level with the lights
 * off, scaled again by the dash level with them on, never below DIM_PWM_MIN. */
static inline uint8_t dim_duty(const dim_t *d)
{
    uint32_t v = (uint32_t)DIM_PWM_FULL * (d->disp ? d->disp : 100u);   /* the knob's level */
    if (d->lights) v = v * dim_pct(d) / 100u;                            /* the dash's, with the lights */
    v = (v + 50u) / 100u;
    return (uint8_t)(v < DIM_PWM_MIN ? DIM_PWM_MIN : v);
}

#endif /* ICU_DIMMING_H */

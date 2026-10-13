/*
 * screen.h — what the panel's small screen says (I-001, I-004, D-492, F-018)
 *
 * The part is not chosen (P201: a 128 x 64-class green I2C module, a parts
 * round picks it). This is only the CONTENT of each page as a small struct a
 * display driver will render later; there is no graphics code and no driver
 * here. Pure, so 00-design/tests/test_dcu.cpp holds it.
 *
 * Owns (R6), from 02-PROJECTS/01-electrical/data:
 *   parts   P201 (the screen)
 *   ideas   I-001 ("at rest displays all knob information in a small condensed
 *           format ... when being controlled adjusts the screen to display only
 *           the current adjustment area"), I-002 and I-004 (no A/C mark, no
 *           recirculate mark, no FAN or SET TEMP labels, no dividing line; the
 *           outside air stays - "the two temp numbers"), kept by D-492
 *
 * The four pages:
 *   SCR_REST  the set temperature large, the fan bars, the mode word, the
 *             outside air - nothing else, no labels
 *   SCR_TEMP  the set temperature alone, large   (the knob turned, setting it)
 *   SCR_FAN   the fan bars alone                 (after a push)
 *   SCR_MODE  the mode word alone                (after the fan-mode key)
 * The page follows the centre knob (panel.h knob_t): FAN and MODE while it sets
 * them, TEMP while the temperature was turned within SCREEN_REST_MS, REST once
 * the knob has rested that long. A field not on the page is empty ("" or -1).
 * Units (°C) and the bars' drawing are the renderer's; the strings carry the
 * numbers and words only.
 */

#ifndef DCU_SCREEN_H
#define DCU_SCREEN_H

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "can_map.h"
#include "climate.h"
#include "panel.h"

enum { SCR_REST = 0, SCR_TEMP, SCR_FAN, SCR_MODE };

typedef struct {
    uint8_t page;          /* SCR_*                                                    */
    char    temp[4];       /* the set temperature, "16".."30"; "" when not on the page */
    int8_t  fan_bars;      /* bars lit, 0..fan_of; -1 when not on the page             */
    uint8_t fan_of;        /* bars drawn (FAN_LEVELS)                                  */
    char    mode[8];       /* "VENT" / "HEAT" / "DEFROST"; "" when not on the page     */
    char    outside[5];    /* outside air, "-40".."85"; "--" when the sensor is blank;
                            * "" when not on the page                                  */
} screen_t;

static inline const char *mode_word(uint8_t mode)
{
    switch (mode) {
    case CLIM_OFF:     return "OFF";
    case CLIM_VENT:    return "VENT";
    case CLIM_HEAT:    return "HEAT";
    case CLIM_DEFROST: return "DEFROST";
    default:           return "";        /* A/C: never shown (I-004), unreachable (D-211) */
    }
}

static inline uint8_t screen_page(const knob_t *k)
{
    if (k->mode == KNOB_FAN)  return SCR_FAN;
    if (k->mode == KNOB_MODE) return SCR_MODE;
    return k->temp_active ? SCR_TEMP : SCR_REST;
}

/* Call after panel_apply() in the same scan, so the knob's rest has been
 * applied. outside_c: the outside-air NTC (SN12), TEMP_INVALID when blank. */
static inline void screen_build(screen_t *s, const knob_t *k, const climate_mem_t *m, int8_t outside_c)
{
    memset(s, 0, sizeof *s);
    s->page = screen_page(k);
    s->fan_bars = -1;
    s->fan_of = FAN_LEVELS;
    uint8_t t = m->target_c < TEMP_MIN_C ? TEMP_MIN_C : (m->target_c > TEMP_MAX_C ? TEMP_MAX_C : m->target_c);
    uint8_t b = m->blower > FAN_LEVELS ? FAN_LEVELS : m->blower;
    if (s->page == SCR_REST || s->page == SCR_TEMP)
        snprintf(s->temp, sizeof s->temp, "%u", (unsigned)t);
    if (s->page == SCR_REST || s->page == SCR_FAN)
        s->fan_bars = (int8_t)b;
    if (s->page == SCR_REST || s->page == SCR_MODE)
        snprintf(s->mode, sizeof s->mode, "%s", mode_word(m->mode));
    if (s->page == SCR_REST) {
        if (outside_c == TEMP_INVALID) snprintf(s->outside, sizeof s->outside, "--");
        else snprintf(s->outside, sizeof s->outside, "%d", (int)outside_c);
    }
}

#endif /* DCU_SCREEN_H */

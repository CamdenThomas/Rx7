/*
 * channels.h — PMU channel table for the simulator
 *
 * ============================================================
 *  THE ONE FILE TO EDIT AFTER THE METER SESSION (T-014).
 *
 *  Every current below is an ESTIMATE unless marked MEASURED.
 *  Replace them with real numbers and the whole simulation becomes
 *  accurate at once - nothing else needs touching.
 * ============================================================
 *
 * Units: 0.01 A, matching CAN 0x130 and cluster_core.h.
 *
 * inrush   multiplier applied for INRUSH_MS after switch-on.
 *          Filament ~10x. Motors ~7x lugging, up to 10x stalled.
 *          Resistive (defog) ~1.3x cold. Electronics ~1x.
 */

#ifndef CHANNELS_H
#define CHANNELS_H

#include <stdint.h>

enum ChSrc : uint8_t { EST = 0, MEASURED = 1, DEAD = 2, RESERVED = 3 };

struct ChannelSpec {
    const char *name;
    uint16_t    steady;      /* 0.01 A                        */
    uint16_t    limit;       /* 0.01 A soft fuse, provisional */
    uint8_t     inrushX10;   /* multiplier x10 -> 100 = 10.0x */
    uint16_t    inrushMs;
    ChSrc       src;
};

/* ---- O1..O24 ---- */
static const ChannelSpec CH[24] = {
/*  name          steady  limit  inX10  ms   source     */
  { "MOTOR BUS",    0,    2500,   70,  400, EST      }, /* O1  sums pop-ups   */
  { "HEAD LOW",   300,     800,   15,   80, EST      }, /* O2  LED housings   */
  { "HEAD HIGH",  350,     900,   15,   80, EST      }, /* O3                 */
  { "DEFOG",     1150,    1600,   13, 2000, EST      }, /* O4  cold draws more*/
  { "FUEL PUMP",  200,     500,   30,  150, EST      }, /* O5  Carter P4070   */
  { "TAIL PARK",  440,     800,  100,   40, EST      }, /* O6  8 filaments    */
  { "BRAKE",      700,    1100,  100,   40, MEASURED }, /* O7  << MEASURED    */
  { "WIPE LOW",   400,    1500,   70,  300, EST      }, /* O8  braking ch     */
  { "WIPE HIGH",  550,    1500,   70,  300, EST      }, /* O9                 */
  { "ACCESSORY",  250,    1200,   20,  100, EST      }, /* O10 USB+head unit  */
  { "HORN",       600,    1000,   30,   80, EST      }, /* O11 pair           */
  { "IGNITION",   500,     800,   20,  100, EST      }, /* O12 coils          */
  { "LS ECU",       0,    1800,   10,    0, RESERVED }, /* O13 capped         */
  { "LS FAN",       0,    2500,   80,  500, RESERVED }, /* O14 capped         */
  { "COMFORT",      0,    2000,   15,  200, EST      }, /* O15 DCU switches   */
  { "BLOWER",       0,    2000,   80,  600, DEAD     }, /* O16 motor is DEAD  */
  { "TURN L",     340,     600,  100,   40, MEASURED }, /* O17 << MEASURED    */
  { "TURN R",     340,     600,  100,   40, MEASURED }, /* O18 << MEASURED    */
  { "REVERSE",    390,     600,  100,   40, EST      }, /* O19                */
  { "INTERIOR",   250,     500,  100,   40, EST      }, /* O20 PWM bus        */
  { "START RLY",   90,     150,   20,   50, EST      }, /* O21 coil only      */
  { "KEEPALIVE",   15,     100,   10,    0, EST      }, /* O22 latch          */
  { "SPARE 23",     0,     700,   10,    0, RESERVED },
  { "SPARE 24",     0,     700,   10,    0, RESERVED }
};

/* Channel indices, so the model reads like the schedule rather than
 * like an array of magic numbers. */
enum {
  O1_MOTOR=0, O2_HEAD_LO, O3_HEAD_HI, O4_DEFOG, O5_FUEL, O6_TAIL,
  O7_BRAKE,   O8_WIPE_LO, O9_WIPE_HI, O10_ACC,  O11_HORN, O12_IGN,
  O13_LS_ECU, O14_LS_FAN, O15_COMFORT,O16_BLOWER,
  O17_TURN_L, O18_TURN_R, O19_REVERSE,O20_INTERIOR,
  O21_START,  O22_KEEPALIVE, O23_SPARE, O24_SPARE
};

/* How many channel currents are still guesses. Printed at boot so the
 * number in front of you is never mistaken for measured data. */
inline int estimatedChannelCount() {
    int n = 0;
    for (int i = 0; i < 24; i++) if (CH[i].src == EST) n++;
    return n;
}

#endif /* CHANNELS_H */

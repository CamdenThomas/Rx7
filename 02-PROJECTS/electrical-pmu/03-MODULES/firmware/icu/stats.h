/*
 * stats.h — trip highlights and diagnostic accumulators
 *
 * Portable C++. Same file compiles for Teensy and the desktop simulator.
 *
 * WHAT THIS IS FOR
 *   Not lap times, not routes. This records the WORST MOMENT of every drive
 *   whether or not you were looking at the cluster, plus the slow-moving
 *   trends that tell you something is wearing out before it fails.
 *
 * PERSISTENCE
 *   trip[]     resets when the car wakes
 *   life[]     never resets. Written to SD, reloaded at boot.
 */

#ifndef STATS_H
#define STATS_H

#include <stdint.h>
#include <string.h>
#include "cluster_core.h"

struct Stats {
    /* ---- peaks, the highlight reel ---- */
    uint16_t maxRpm        = 0;
    uint16_t maxSpeed      = 0;
    int16_t  maxWaterC     = -128;
    int16_t  maxOilTempC   = -128;
    uint16_t maxOilPress   = 0;        /* 0.01 bar */
    uint16_t minOilPress   = 65535;    /* only sampled while running */
    uint16_t maxVoltsX10   = 0;
    uint16_t minVoltsX10   = 65535;
    uint16_t maxLatG       = 0;        /* 0.01 g, absolute */
    uint16_t maxAccelG     = 0;
    uint16_t maxBrakeG     = 0;
    int16_t  maxPitchUp    = 0;
    int16_t  maxPitchDown  = 0;

    /* ---- totals ---- */
    uint32_t runtimeSec    = 0;
    uint32_t idleSec       = 0;        /* running, speed 0 */
    uint32_t distanceX10   = 0;        /* tenths of a mile */
    uint32_t revSeconds    = 0;        /* seconds above REDLINE_RPM */
    uint32_t hotSeconds    = 0;        /* seconds above HOT_WATER_C */
    uint32_t lowOilSeconds = 0;        /* seconds below LOW_OIL_CBAR while running */
    uint16_t coldStarts    = 0;

    /* ---- fuel, see the honesty note below ---- */
    uint8_t  fuelPctStart  = 255;      /* 255 = not yet captured */
    uint8_t  fuelPctNow    = 0;
    uint32_t distAtFuelMark = 0;

    /* ---- faults ---- */
    uint16_t softFuseTrips = 0;
    uint8_t  lastTripCh    = 255;
    uint32_t lastTripSec   = 0;
    uint16_t sensorFaults  = 0;
    uint16_t canTimeouts   = 0;

    void reset() { *this = Stats(); }
};

/* thresholds */
static const uint16_t REDLINE_RPM   = 7000;
static const int16_t  HOT_WATER_C   = 105;
static const uint16_t LOW_OIL_CBAR  = 100;    /* 1.0 bar */
static const uint16_t RUNNING_RPM   = 400;
static const uint16_t COLD_START_C  = 40;

/* Tank capacity for the trip-average calculation. FB is ~60 L / 15.9 gal. */
static const uint16_t TANK_GAL_X10  = 159;

class StatsTracker {
public:
    Stats trip;
    Stats life;
    uint32_t lastTickMs = 0;
    uint32_t distAccum = 0;
    bool wasRunning = false;

    void begin(uint32_t nowMs) { lastTickMs = nowMs; }

    /* Call at ~1 Hz. Cheap. */
    void tick(const VehicleState &s, uint32_t nowMs) {
        uint32_t dt = (nowMs - lastTickMs) / 1000;
        if (dt == 0) return;
        lastTickMs += dt * 1000;

        bool running = s.rpm > RUNNING_RPM;

        if (!wasRunning && running && s.waterC < COLD_START_C) {
            trip.coldStarts++; life.coldStarts++;
        }
        wasRunning = running;

        /* Distance in tenths of a mile, computed ONCE per tick and applied
         * to both accumulators. At 1 Hz, (mph * 1s * 10) / 3600 truncates
         * to zero below 360 mph, so the remainder must carry over or no
         * distance is ever recorded. The regression suite caught this. */
        distAccum += (uint32_t)s.speed * dt * 10;
        uint32_t distStep = distAccum / 3600;
        distAccum %= 3600;

        Stats *tab[2] = { &trip, &life };
        for (int k = 0; k < 2; k++) {
            Stats &a = *tab[k];

            if ((uint16_t)s.rpm   > a.maxRpm)   a.maxRpm   = (uint16_t)s.rpm;
            if ((uint16_t)s.speed > a.maxSpeed) a.maxSpeed = (uint16_t)s.speed;
            if (s.sWater == SENSOR_OK && s.waterC   > a.maxWaterC)   a.maxWaterC   = (int16_t)s.waterC;
            if (s.sOilT  == SENSOR_OK && s.oilTempC > a.maxOilTempC) a.maxOilTempC = (int16_t)s.oilTempC;

            if (s.sOilP == SENSOR_OK) {
                if ((uint16_t)s.oilPressCbar > a.maxOilPress) a.maxOilPress = (uint16_t)s.oilPressCbar;
                if (running && (uint16_t)s.oilPressCbar < a.minOilPress)
                    a.minOilPress = (uint16_t)s.oilPressCbar;
            }
            if (s.sVolts == SENSOR_OK) {
                if ((uint16_t)s.voltsX10 > a.maxVoltsX10) a.maxVoltsX10 = (uint16_t)s.voltsX10;
                if ((uint16_t)s.voltsX10 < a.minVoltsX10) a.minVoltsX10 = (uint16_t)s.voltsX10;
            }
            if (s.sImu == SENSOR_OK) {
                uint16_t lat = (uint16_t)(s.latGx100 < 0 ? -s.latGx100 : s.latGx100);
                if (lat > a.maxLatG) a.maxLatG = lat;
                if (s.lonGx100 > 0 && (uint16_t)s.lonGx100 > a.maxAccelG)
                    a.maxAccelG = (uint16_t)s.lonGx100;
                if (s.lonGx100 < 0 && (uint16_t)(-s.lonGx100) > a.maxBrakeG)
                    a.maxBrakeG = (uint16_t)(-s.lonGx100);
                if (s.pitchDeg > a.maxPitchUp)   a.maxPitchUp   = (int16_t)s.pitchDeg;
                if (s.pitchDeg < a.maxPitchDown) a.maxPitchDown = (int16_t)s.pitchDeg;
            }

            if (running) {
                a.runtimeSec += dt;
                if (s.speed == 0) a.idleSec += dt;
                if (s.rpm > REDLINE_RPM)   a.revSeconds += dt;
                if (s.sWater == SENSOR_OK && s.waterC > HOT_WATER_C) a.hotSeconds += dt;
                if (s.sOilP == SENSOR_OK && s.oilPressCbar < LOW_OIL_CBAR)
                    a.lowOilSeconds += dt;
            }
            a.distanceX10 += distStep;

            if (s.sFuel == SENSOR_OK) {
                if (a.fuelPctStart == 255) {
                    a.fuelPctStart = (uint8_t)s.fuelPct;
                    a.distAtFuelMark = a.distanceX10;
                }
                a.fuelPctNow = (uint8_t)s.fuelPct;
            }
        }
    }

    void noteSoftFuseTrip(uint8_t channel, uint32_t sec) {
        trip.softFuseTrips++; life.softFuseTrips++;
        trip.lastTripCh = channel; life.lastTripCh = channel;
        trip.lastTripSec = sec;    life.lastTripSec = sec;
    }
    void noteSensorFault() { trip.sensorFaults++; life.sensorFaults++; }
    void noteCanTimeout()  { trip.canTimeouts++;  life.canTimeouts++;  }

    /* -------- fuel economy, honestly --------
     * There is no fuel flow sensor on a carburettor. The only measurable
     * quantity is tank level, so MPG is derived from level drop over
     * distance. That is noisy over short trips - the float sloshes - and
     * only meaningful across a large level change.
     *
     * Returns mpg x10, or 0 when the sample is too small to trust. */
    static uint16_t mpgX10(const Stats &a) {
        if (a.fuelPctStart == 255) return 0;
        int dropPct = (int)a.fuelPctStart - (int)a.fuelPctNow;
        if (dropPct < 10) return 0;               /* under 10% - not trustworthy */
        uint32_t miles10 = a.distanceX10 - a.distAtFuelMark;
        uint32_t galX100 = ((uint32_t)dropPct * TANK_GAL_X10) / 10;
        if (galX100 == 0) return 0;
        return (uint16_t)((miles10 * 100) / galX100);
    }
};

/* ---------------- CSV line, one per trip ---------------- */
inline int statsToCsv(const Stats &a, char *out, int cap) {
    uint16_t mpg = StatsTracker::mpgX10(a);
    return snprintf(out, cap,
        "%lu,%lu,%lu,%u,%u,%d,%d,%u,%u,%u,%u,%u,%u,%u,%d,%d,"
        "%lu,%lu,%lu,%u,%u,%u,%u,%u\n",
        (unsigned long)a.runtimeSec,
        (unsigned long)a.idleSec,
        (unsigned long)a.distanceX10,
        a.maxRpm, a.maxSpeed,
        a.maxWaterC, a.maxOilTempC,
        a.maxOilPress,
        a.minOilPress == 65535 ? 0 : a.minOilPress,
        a.maxVoltsX10,
        a.minVoltsX10 == 65535 ? 0 : a.minVoltsX10,
        a.maxLatG, a.maxAccelG, a.maxBrakeG,
        a.maxPitchUp, a.maxPitchDown,
        (unsigned long)a.revSeconds,
        (unsigned long)a.hotSeconds,
        (unsigned long)a.lowOilSeconds,
        a.coldStarts,
        a.softFuseTrips, a.lastTripCh,
        a.sensorFaults, mpg);
}

inline const char *statsCsvHeader() {
    return "runtime_s,idle_s,dist_x10,max_rpm,max_mph,max_water_c,max_oilt_c,"
           "max_oilp_cbar,min_oilp_cbar,max_v_x10,min_v_x10,"
           "max_lat_g_x100,max_accel_g_x100,max_brake_g_x100,"
           "max_pitch_up,max_pitch_dn,rev_s,hot_s,lowoil_s,cold_starts,"
           "fuse_trips,last_trip_ch,sensor_faults,mpg_x10\n";
}

/* ================= trip page =================
 * Lives here rather than in cluster_core.h because it needs Stats.
 * Read while parked, so a full redraw of the value column is fine.
 */
inline void drawTripPage(Framebuffer &fb, const Stats &a, uint16_t mpgX10) {
    const int LX = 30, VX = 300, TOP = 70, STEP = 32;
    const int RX = 420, RVX = 700;

    struct Row { const char *label; int value; int dec; const char *unit; };

    int minOil = (a.minOilPress == 65535) ? 0 : a.minOilPress;
    int minV   = (a.minVoltsX10 == 65535) ? 0 : a.minVoltsX10;
    int oilPsi = (minOil * 145) / 1000;
    int waterF = (a.maxWaterC   * 9) / 5 + 32;
    int oilTF  = (a.maxOilTempC * 9) / 5 + 32;

    Row left[10] = {
        { "MAX RPM",     a.maxRpm,          0, ""    },
        { "MAX SPEED",   a.maxSpeed,        0, "MPH" },
        { "MAX WATER",   waterF,            0, "F"   },
        { "MAX OIL T",   oilTF,             0, "F"   },
        { "MIN OIL P",   oilPsi,            0, "PSI" },
        { "MAX VOLTS",   a.maxVoltsX10,     1, "V"   },
        { "MIN VOLTS",   minV,              1, "V"   },
        { "DISTANCE",    (int)a.distanceX10,1, "MI"  },
        { "RUNTIME",     (int)(a.runtimeSec/60), 0, "MIN" },
        { "IDLE",        (int)(a.idleSec/60),    0, "MIN" }
    };
    Row right[10] = {
        { "PEAK LAT G",  a.maxLatG,         2, "G"   },
        { "PEAK ACCEL",  a.maxAccelG,       2, "G"   },
        { "PEAK BRAKE",  a.maxBrakeG,       2, "G"   },
        { "MAX CLIMB",   a.maxPitchUp,      0, "DEG" },
        { "MAX DESCENT", -a.maxPitchDown,   0, "DEG" },
        { "OVER REDLINE",(int)a.revSeconds, 0, "S"   },
        { "OVER TEMP",   (int)a.hotSeconds, 0, "S"   },
        { "LOW OIL",  (int)a.lowOilSeconds, 0, "S"   },
        { "FUSE TRIPS",  a.softFuseTrips,   0, ""    },
        { "MPG",         mpgX10,            1, ""    }
    };

    for (int i = 0; i < 10; i++) {
        int y = TOP + i * STEP;

        fb.fillRect(VX, y, 110, 16, C_BLACK);
        drawText(fb, left[i].label, LX, y, 2, C_MID);
        drawNum (fb, left[i].value, VX, y, 2, C_GREEN, left[i].dec);
        if (left[i].unit[0])
            drawText(fb, left[i].unit, VX + 78, y, 2, C_DIM);

        fb.fillRect(RVX, y, 110, 16, C_BLACK);
        drawText(fb, right[i].label, RX, y, 2, C_MID);
        drawNum (fb, right[i].value, RVX, y, 2, C_GREEN, right[i].dec);
        if (right[i].unit[0])
            drawText(fb, right[i].unit, RVX + 78, y, 2, C_DIM);
    }

    /* The three that actually matter get called out. They are the slow
     * trends that say something is wearing before it fails. */
    if (a.revSeconds || a.hotSeconds || a.lowOilSeconds)
        drawText(fb, "SEE OVER-LIMIT COUNTERS", RX, TOP + 10*STEP + 10, 2, C_AMBER);

    if (mpgX10 == 0)
        drawText(fb, "MPG NEEDS 10% TANK DROP", LX, TOP + 10*STEP + 10, 2, C_DIM);
}

#endif /* STATS_H */

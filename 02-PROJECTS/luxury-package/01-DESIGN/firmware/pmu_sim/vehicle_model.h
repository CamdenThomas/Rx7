/*
 * vehicle_model.h — a 1982 RX-7 that behaves like one
 *
 * Not random numbers. Every value follows the real relationship:
 *   - water temp warms on a curve and holds at thermostat
 *   - oil pressure falls with heat and rises with rpm
 *   - voltage dips on crank, recovers with the alternator
 *   - fuel burns proportional to rpm and load
 *   - turn signal current pulses with the flash
 *   - pop-ups take real time to travel
 *
 * That matters because the ICU is meant to display a car, and a display
 * fed by noise proves nothing about whether it reads well.
 *
 * Portable C++. No Arduino headers.
 */

#ifndef VEHICLE_MODEL_H
#define VEHICLE_MODEL_H

#include <stdint.h>
#include "channels.h"

enum KeyPos : uint8_t { K_OFF = 0, K_ACC, K_RUN, K_START };
enum HeadPos: uint8_t { H_OFF = 0, H_PARK, H_HEAD };
enum TurnPos: uint8_t { T_OFF = 0, T_LEFT, T_RIGHT, T_HAZARD };
enum WipePos: uint8_t { W_OFF = 0, W_INT, W_LOW, W_HIGH };
enum PopPos : uint8_t { P_DOWN = 0, P_RAISING, P_UP, P_LOWERING };

class Vehicle {
public:
    /* ---- driver inputs ---- */
    KeyPos  key   = K_OFF;
    HeadPos head  = H_OFF;
    TurnPos turn  = T_OFF;
    WipePos wipe  = W_OFF;
    bool    brake = false;
    bool    horn  = false;
    bool    reverse = false;
    bool    defog = false;
    int     throttle = 0;          /* 0..100, drives target rpm */

    /* ---- engine and drivetrain ---- */
    int  rpm = 0;
    int  speedMph = 0;
    bool running = false;
    uint32_t crankMs = 0;

    /* ---- thermal, 0.1 units for resolution ---- */
    int waterCx10  = 180;          /* 18.0 C ambient */
    int oilTempCx10 = 180;
    int oilPressCbar = 0;

    /* ---- electrical ---- */
    int voltsX10 = 124;            /* rested lithium */
    int fuelPctX10 = 720;

    /* ---- attitude ---- */
    int latGx100 = 0, lonGx100 = 0;
    int headingDeg = 0, pitchDeg = 0;

    /* ---- pop-ups ---- */
    PopPos popup = P_DOWN;
    int    popupTravelMs = 0;
    static const int POPUP_TRAVEL = 900;

    /* ---- channel state ---- */
    bool     chOn[24]      = {false};
    uint32_t chOnAtMs[24]  = {0};
    uint16_t chCurrent[24] = {0};
    uint8_t  chState[24]   = {0};      /* 0 off 1 on 2 tripped 3 retry */
    uint32_t chTripAtMs[24]= {0};

    /* ---- flags ---- */
    bool wOil=false, wTemp=false, wBatt=false, wBrake=false, wFuel=false;
    uint32_t nowMs = 0;
    bool turnPhase = false;            /* flasher on-phase */
    uint32_t lastFlashMs = 0;

    /* ============ the tick ============ */
    void update(uint32_t ms, uint32_t dtMs) {
        nowMs = ms;
        engine(dtMs);
        thermal(dtMs);
        electrical(dtMs);
        motion(dtMs);
        flasher();
        popups(dtMs);
        setChannels();
        currents();
        warnings();
    }

private:
    /* ---------------- engine ---------------- */
    void engine(uint32_t dt) {
        if (key == K_START) {
            crankMs += dt;
            rpm = 250;                                  /* cranking */
            if (crankMs > 900) running = true;          /* catches */
        } else if (key < K_RUN) {
            running = false; crankMs = 0;
        }

        if (!running) {
            if (key != K_START) rpm -= (int)(dt * 3);
            if (rpm < 0) rpm = 0;
            return;
        }

        /* idle rises when cold - a real cold-idle cam would do this */
        int idle = (waterCx10 < 500) ? 1400 : 850;
        int target = idle + (throttle * 68);
        if (target > 8200) target = 8200;

        /* spin up faster than it spins down, as an engine does */
        int gain = (target > rpm) ? 9 : 5;
        rpm += ((target - rpm) * (int)dt * gain) / 1000;
        if (rpm < 0) rpm = 0;
    }

    /* ---------------- thermal ----------------
     * Fractional accumulators. At 10 ms ticks the per-tick change is far
     * below 1, so plain integer maths truncates it to zero and nothing ever
     * warms up. The regression suite caught exactly that. */
    int32_t accWater = 0, accOil = 0, accVolts = 0;

    void thermal(uint32_t dt) {
        if (running) {
            int heat = 6 + (rpm / 400);
            int cool = 3 + (speedMph / 6) + (waterCx10 > 880 ? 40 : 0);
            accWater += (heat - cool) * (int)dt;
            waterCx10 += accWater / 900;
            accWater %= 900;

            int oilTarget = waterCx10 + 60 + (rpm / 90);
            accOil += (oilTarget - oilTempCx10) * (int)dt;
            oilTempCx10 += accOil / 6000;
            accOil %= 6000;
        } else {
            accWater -= (int)dt;
            if (waterCx10 > 180 && accWater < -60) { waterCx10--; accWater = 0; }
            accOil -= (int)dt;
            if (oilTempCx10 > 180 && accOil < -80) { oilTempCx10--; accOil = 0; }
        }
        if (waterCx10 < 180) waterCx10 = 180;
        if (waterCx10 > 1300) waterCx10 = 1300;

        if (!running) {
            oilPressCbar -= (int)dt / 2;
            if (oilPressCbar < 0) oilPressCbar = 0;
        } else {
            int visc = 1000 - (oilTempCx10 - 800) / 2;
            if (visc < 500) visc = 500;
            if (visc > 1200) visc = 1200;
            int target = (80 + (rpm * 62) / 100) * visc / 1000;
            if (target > 700) target = 700;
            int delta = ((target - oilPressCbar) * (int)dt) / 400;
            if (delta == 0 && target != oilPressCbar)
                delta = (target > oilPressCbar) ? 1 : -1;
            oilPressCbar += delta;
            if (oilPressCbar < 0)   oilPressCbar = 0;
            if (oilPressCbar > 800) oilPressCbar = 800;
        }
    }

    /* ---------------- electrical ---------------- */
    void electrical(uint32_t dt) {
        int target;
        if (key == K_START)      target = 98;
        else if (running)        target = 142;
        else if (key >= K_ACC)   target = 126;
        else                     target = 128;

        uint32_t total = 0;
        for (int i = 0; i < 24; i++) total += chCurrent[i];
        target -= (int)(total / 900);

        accVolts += (target - voltsX10) * (int)dt;
        voltsX10 += accVolts / 250;
        accVolts %= 250;
        if (voltsX10 < 80)  voltsX10 = 80;
        if (voltsX10 > 160) voltsX10 = 160;

        if (running) {
            uint32_t burn = 2 + (uint32_t)(rpm / 900) + (uint32_t)(throttle / 25);
            static uint32_t acc = 0;
            acc += burn * dt;
            while (acc > 900000) { acc -= 900000; if (fuelPctX10 > 0) fuelPctX10--; }
        }
    }

    /* ---------------- motion ---------------- */
    void motion(uint32_t dt) {
        int target = running ? (rpm / 62) : 0;
        if (!running) target = 0;
        int prev = speedMph;
        speedMph += ((target - speedMph) * (int)dt) / 700;
        if (speedMph < 0) speedMph = 0;

        /* longitudinal g from actual acceleration */
        int accel = (speedMph - prev) * 40;
        lonGx100 += ((accel - lonGx100) * (int)dt) / 200;
        if (brake && speedMph > 0) lonGx100 -= (int)dt / 3;
        if (lonGx100 >  100) lonGx100 =  100;
        if (lonGx100 < -100) lonGx100 = -100;

        /* lateral g from steering, implied by the turn stalk */
        int latTarget = 0;
        if (turn == T_LEFT)  latTarget = -(speedMph / 2);
        if (turn == T_RIGHT) latTarget =  (speedMph / 2);
        if (latTarget >  90) latTarget =  90;
        if (latTarget < -90) latTarget = -90;
        latGx100 += ((latTarget - latGx100) * (int)dt) / 400;

        /* heading follows the turn */
        if (turn == T_LEFT)  headingDeg -= (int)(dt * speedMph) / 900;
        if (turn == T_RIGHT) headingDeg += (int)(dt * speedMph) / 900;
        headingDeg = ((headingDeg % 360) + 360) % 360;
    }

    /* ---------------- flasher ---------------- */
    void flasher() {
        if (turn == T_OFF) { turnPhase = false; return; }
        if (nowMs - lastFlashMs > 333) {          /* 1.5 Hz */
            turnPhase = !turnPhase;
            lastFlashMs = nowMs;
        }
    }

    /* ---------------- pop-ups ---------------- */
    void popups(uint32_t dt) {
        bool want = (head == H_HEAD);
        if (want && popup == P_DOWN)   { popup = P_RAISING;  popupTravelMs = 0; }
        if (!want && popup == P_UP)    { popup = P_LOWERING; popupTravelMs = 0; }

        if (popup == P_RAISING || popup == P_LOWERING) {
            popupTravelMs += (int)dt;
            if (popupTravelMs >= POPUP_TRAVEL)
                popup = (popup == P_RAISING) ? P_UP : P_DOWN;
        }
    }

    /* ---------------- which channels are commanded ---------------- */
    void setChannels() {
        bool acc = (key >= K_ACC);
        bool run = (key >= K_RUN);

        bool want[24] = {false};
        want[O1_MOTOR]     = (popup == P_RAISING || popup == P_LOWERING);
        want[O2_HEAD_LO]   = (head == H_HEAD);
        want[O3_HEAD_HI]   = false;
        want[O4_DEFOG]     = defog && run;
        want[O5_FUEL]      = running || (key == K_START);
        want[O6_TAIL]      = (head >= H_PARK);
        want[O7_BRAKE]     = brake;
        want[O8_WIPE_LO]   = (wipe == W_LOW || wipe == W_INT);
        want[O9_WIPE_HI]   = (wipe == W_HIGH);
        want[O10_ACC]      = acc;
        want[O11_HORN]     = horn;
        want[O12_IGN]      = run;
        want[O15_COMFORT]  = run;
        want[O16_BLOWER]   = false;                    /* motor is dead */
        want[O17_TURN_L]   = turnPhase && (turn == T_LEFT  || turn == T_HAZARD);
        want[O18_TURN_R]   = turnPhase && (turn == T_RIGHT || turn == T_HAZARD);
        want[O19_REVERSE]  = reverse && run;
        want[O20_INTERIOR] = acc;
        want[O21_START]    = (key == K_START);
        want[O22_KEEPALIVE]= acc;

        for (int i = 0; i < 24; i++) {
            if (chState[i] == 2) {                     /* tripped, latched */
                if (nowMs - chTripAtMs[i] > 5000) chState[i] = 3;   /* retry */
                continue;
            }
            if (chState[i] == 3) {                     /* retry succeeds */
                chState[i] = want[i] ? 1 : 0;
                chOn[i] = want[i];
                if (want[i]) chOnAtMs[i] = nowMs;
                continue;
            }
            if (want[i] && !chOn[i]) chOnAtMs[i] = nowMs;
            chOn[i]   = want[i];
            chState[i] = want[i] ? 1 : 0;
        }
    }

    /* ---------------- current per channel ---------------- */
    void currents() {
        for (int i = 0; i < 24; i++) {
            if (chState[i] == 2) { chCurrent[i] = CH[i].limit; continue; }
            if (!chOn[i] || CH[i].src == DEAD || CH[i].src == RESERVED) {
                chCurrent[i] = 0; continue;
            }

            uint32_t base = CH[i].steady;

            /* channels whose draw actually varies */
            if (i == O1_MOTOR)   base = 950;                   /* two pop-ups  */
            if (i == O5_FUEL)    base = 180 + (uint32_t)(rpm / 120);
            if (i == O12_IGN)    base = 380 + (uint32_t)(rpm / 45);
            if (i == O4_DEFOG) {                               /* grid warms   */
                uint32_t on = nowMs - chOnAtMs[i];
                base = (on < 120000) ? 1150 - (on / 900) : 1020;
            }
            if (i == O20_INTERIOR) base = 250;

            /* inrush window */
            uint32_t since = nowMs - chOnAtMs[i];
            if (since < CH[i].inrushMs) {
                uint32_t k = CH[i].inrushX10;
                uint32_t decay = CH[i].inrushMs ? (CH[i].inrushMs - since) : 0;
                uint32_t mul = 10 + ((k - 10) * decay) / (CH[i].inrushMs ? CH[i].inrushMs : 1);
                base = base * mul / 10;
            }

            if (base > 65535u) base = 65535u;
            chCurrent[i] = (uint16_t)base;
        }
    }

    /* ---------------- warning lamps ---------------- */
    void warnings() {
        wOil   = running && oilPressCbar < 100;
        wTemp  = waterCx10 > 1050;
        wBatt  = running && voltsX10 < 130;
        wBrake = brake;
        wFuel  = fuelPctX10 < 120;
    }

public:
    /* Force a soft-fuse trip, so fault rendering can be exercised. */
    void tripChannel(int i) {
        if (i < 0 || i >= 24) return;
        chState[i] = 2;
        chTripAtMs[i] = nowMs;
    }
    void clearTrips() {
        for (int i = 0; i < 24; i++) if (chState[i] >= 2) chState[i] = 0;
    }
    uint32_t totalCurrent() const {
        uint32_t t = 0;
        for (int i = 0; i < 24; i++) t += chCurrent[i];
        return t;
    }
};

#endif /* VEHICLE_MODEL_H */

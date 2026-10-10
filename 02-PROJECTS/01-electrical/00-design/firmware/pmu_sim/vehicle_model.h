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
 * And it switches its outputs by the PMU's rules, held to the record (logic, rules, inputs):
 *   - FUEL_PUMP: START, the 3 s prime from ignition_on rising, then the oil gate - oil_ok
 *     latches on an A7 count BELOW OIL_MIN (the sender is open at 0 psi and falls with
 *     pressure, SP-787) and clears after 5 s continuously at or above it, or with ignition;
 *     an open sender is zero pressure, so the pump stops after the prime (D-461)
 *   - IGNITION: off only after 200 ms of a clean OFF / ACC (D-410)
 *   - ACCESSORY: A16 >= ACC, or the engine running - ignition_on && oil_ok (D-463)
 *   - INTERIOR: the dash illumination, A15 >= PARK at the dimmer's duty, never a door (D-462)
 *   - the voltage shed: COMFORT, INTERIOR, ACCESSORY, DEFOG off after 10 s continuously
 *     below 11.5 V, never counted during START, back above 12.0 V; ACCESSORY and INTERIOR
 *     never shed while the engine runs (rules voltage, D-463, D-476)
 *   - KEEP_ALIVE: awake on any wake; off 30 s after the last change with the key OFF, the
 *     doors closed and A8 idle; forced off 30 min after the key went OFF - except while the
 *     hazards are on, with no limit (rules sleep, D-248, D-464)
 * tests/test_suite.cpp sections 14 (the generated vectors) and 15 (the timers) hold it there.
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
/* The A15 ladder's five states (ladders A15): HEAD is HEAD_LO. 0x100 byte 3 carries only
 * OFF / PARK / HEAD, so pmu_sim sends HIGH and PASS as HEAD (can_fields 0x100/3). */
enum HeadPos: uint8_t { H_OFF = 0, H_PARK, H_HEAD, H_HIGH, H_PASS };
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
    bool    defog = false;         /* the panel key over CAN (logic DEFOG: panel_defog) */
    bool    door  = false;         /* A6 != CLOSED - any door open: a wake input, no lamp (D-462) */
    int     throttle = 0;          /* 0..100, drives target rpm */
    int     dimPct = 100;          /* the dimmer's duty on O20, % (logic INTERIOR) */

    /* ---- bench injection, as the ladder rig would put it on the pin ---- */
    int     a7Inject = -1;         /* a raw A7 count on the oil-pressure node; -1 = the model's own
                                    * sender. 1023 = an open sender or a broken wire (D-461) */
    int     voltsInjectX10 = 0;    /* hold the supply here (x10 V); 0 = the model's own */

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

    /* ---- the PMU's rules (logic FUEL_PUMP / IGNITION, rules voltage / sleep) ---- */
    static const int A7_OPEN  = 1000;          /* above: open = ZERO oil pressure, not a fault (inputs A7, D-461) */
    static const int A7_SHORT = 20;            /* below: short - still counts as oil_ok (D-249) */
    static const int OIL_MIN_COUNT = 700;      /* SIMULATOR PLACEHOLDER, ~217 ohm under the 100 ohm pull-up -
                                                * above SP-787's first mark (196.7 ohm, other-car). The real
                                                * OIL_MIN is read in the car at commissioning, never entered on
                                                * the bench (D-249) */
    static const uint32_t PRIME_MS      = 3000;    /* logic FUEL_PUMP: prime_timer < 3 s */
    static const uint32_t OIL_CLEAR_MS  = 5000;    /* oil_ok clears after 5 s continuously >= OIL_MIN */
    static const uint32_t IGN_OFF_MS    = 200;     /* logic IGNITION: a clean OFF / ACC for 200 ms */
    static const uint32_t SHED_DELAY_MS = 10000;   /* rules voltage: about 10 s below 11.5 V (D-463) */
    static const int SHED_BELOW_X10   = 115;       /* below 11.5 V */
    static const int SHED_RESTORE_X10 = 120;       /* back above 12.0 V - 0.5 V of hysteresis */
    static const uint32_t SLEEP_QUIET_MS  = 30000;            /* rules sleep: 30 s after the last change */
    static const uint32_t SLEEP_FORCED_MS = 30UL * 60 * 1000; /* 30 min with A16 == OFF (D-248) */
    static const uint32_t STARVE_MS = 1500;    /* MODEL FIGURE, not a record fact: the engine dies this
                                                * long after the pump stops */

    bool     ignitionOn = false;   /* the IGNITION channel's own state - logic's ignition_on */
    bool     oilOk      = false;   /* logic's oil_ok */
    bool     engineRuns = false;   /* ignition_on && oil_ok - what ACCESSORY and the shed read */
    bool     shed       = false;   /* the low-voltage shed is in force */
    bool     awake      = false;   /* KEEP_ALIVE (O22) */
    uint32_t primeMs = 0, oilHighMs = 0, ignOffMs = 0, lowVoltMs = 0;
    uint32_t quietMs = 0, keyOffMs = 0, starveMs = 0;

    /* the A7 count the PMU reads: the injected one, or the model's sender - open below
     * 5 psi, then SP-787's 60 / 110 psi marks on a straight line (other-car, a model only) */
    int a7Count() const {
        if (a7Inject >= 0) return a7Inject;
        int psi = oilPressCbar * 145 / 1000;               /* 1 bar = 14.5 psi */
        if (psi < 5) return 1023;
        int ohm = 188 - (psi * 772) / 1000;
        if (ohm < 60) ohm = 60;
        return 1023 * ohm / (ohm + 100);
    }

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
        setChannels(dtMs);
        currents();
        warnings();
    }

private:
    bool     ignWant = false, ignPrev = false;
    uint8_t  wakePrev = 0;

    /* ---------------- engine ---------------- */
    void engine(uint32_t dt) {
        if (key == K_START) {
            crankMs += dt;
            rpm = 250;                                  /* cranking */
            if (crankMs > 900) running = true;          /* catches */
        } else if (key < K_RUN) {
            crankMs = 0;
        }
        /* it runs on the IGNITION channel (the key, its 200 ms off-delay, a trip) and on fuel:
         * the pump stopped by the oil gate starves it (D-461) */
        if (running && key != K_START && chState[O12_IGN] != 1) running = false;
        if (running && chState[O5_FUEL] != 1) {
            starveMs += dt;
            if (starveMs >= STARVE_MS) running = false;
        } else {
            starveMs = 0;
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
        if (voltsInjectX10 > 0) { voltsX10 = voltsInjectX10; accVolts = 0; }

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
        /* HEAD is HEAD_LO or HEAD_HI; a PASS flash moves nothing - the pop-ups stay where
         * they are (rules pop-up-cycle names HEAD only) */
        if (head == H_PASS) { popupTravel(dt); return; }
        bool want = (head == H_HEAD || head == H_HIGH);
        if (want && popup == P_DOWN)   { popup = P_RAISING;  popupTravelMs = 0; }
        if (!want && popup == P_UP)    { popup = P_LOWERING; popupTravelMs = 0; }
        popupTravel(dt);
    }

    void popupTravel(uint32_t dt) {
        if (popup == P_RAISING || popup == P_LOWERING) {
            popupTravelMs += (int)dt;
            if (popupTravelMs >= POPUP_TRAVEL)
                popup = (popup == P_RAISING) ? P_UP : P_DOWN;
        }
    }

    /* ---------------- which channels are commanded ----------------
     * Held to the record's logic rows by tests/test_suite.cpp section 14 (logic_vectors.h,
     * generated from logic.csv): what this model has an input for must agree. The clauses
     * the generator leaves to hand-testing - the prime, the oil latch, the off-delay, the
     * shed, the sleep - are section 15. */
    static uint32_t upTo(uint32_t t, uint32_t dt, uint32_t cap) { return (t + dt > cap) ? cap : t + dt; }

    void setChannels(uint32_t dt) {
        bool acc   = (key >= K_ACC);
        bool run   = (key >= K_RUN);
        bool start = (key == K_START);
        bool hazard = (turn == T_HAZARD);

        /* IGNITION: on at A16 >= RUN, off only after a clean OFF / ACC for 200 ms (D-410).
         * ignition_on is the channel's own state, so a tripped O12 reads false. */
        if (run) { ignWant = true; ignOffMs = 0; }
        else     { ignOffMs = upTo(ignOffMs, dt, IGN_OFF_MS); if (ignOffMs >= IGN_OFF_MS) ignWant = false; }
        ignitionOn = ignWant && chState[O12_IGN] != 2;

        /* the prime: 3 s from ignition_on rising */
        if (ignitionOn && !ignPrev) primeMs = 0;
        else if (ignitionOn)        primeMs = upTo(primeMs, dt, PRIME_MS);
        ignPrev = ignitionOn;
        bool prime = ignitionOn && primeMs < PRIME_MS;

        /* the oil gate (D-461): oil pressure above OIL_MIN is a count BELOW OIL_MIN. It latches
         * there, and clears after 5 s continuously at or above it (an open sender among them),
         * or at once with ignition. A short (< 20) is below OIL_MIN, so it counts as oil_ok. */
        int a7 = a7Count();
        if (!ignitionOn)            { oilOk = false; oilHighMs = 0; }
        else if (a7 < OIL_MIN_COUNT) { oilOk = true;  oilHighMs = 0; }
        else {
            oilHighMs = upTo(oilHighMs, dt, OIL_CLEAR_MS);
            if (oilHighMs >= OIL_CLEAR_MS) oilOk = false;
        }
        engineRuns = ignitionOn && oilOk;

        /* the voltage shed (rules voltage, D-463): 10 s continuously below 11.5 V, never
         * counted during START; restored only above 12.0 V */
        if (start || voltsX10 >= SHED_BELOW_X10) lowVoltMs = 0;
        else lowVoltMs = upTo(lowVoltMs, dt, SHED_DELAY_MS);
        if (!shed && lowVoltMs >= SHED_DELAY_MS) shed = true;
        if (shed && voltsX10 > SHED_RESTORE_X10)  shed = false;

        /* KEEP_ALIVE (rules sleep, D-248, D-464). A wake is a wake-strip input going high;
         * the 30 s runs from the last change with the key OFF, the doors shut and A8 idle;
         * the 30 min runs while the key is OFF and is held at zero while the hazards are on,
         * so it restarts when they go off; a new wake restarts it too. After a forced sleep a
         * door still open does not wake it again - only an input going high does. */
        uint8_t wake = (uint8_t)((acc ? 1 : 0) | (run ? 2 : 0) | (door ? 4 : 0) | ((hazard || horn) ? 8 : 0));
        uint8_t rose = (uint8_t)(wake & ~wakePrev);
        quietMs  = (wake != wakePrev) ? 0 : upTo(quietMs, dt, SLEEP_QUIET_MS);
        keyOffMs = (key != K_OFF || hazard || rose) ? 0 : upTo(keyOffMs, dt, SLEEP_FORCED_MS);
        wakePrev = wake;
        if (rose) awake = true;
        else if (awake) {
            bool still = (key == K_OFF) && !door && !hazard && !horn;
            if (still && quietMs >= SLEEP_QUIET_MS)    awake = false;
            if (keyOffMs >= SLEEP_FORCED_MS)           awake = false;   /* never while hazard: held at zero */
        }

        bool want[24] = {false};
        want[O1_MOTOR]     = (popup == P_RAISING || popup == P_LOWERING);
        want[O2_HEAD_LO]   = (head == H_HEAD);
        want[O3_HEAD_HI]   = (head == H_HIGH || head == H_PASS);   /* logic HEAD_HIGH */
        want[O4_DEFOG]     = defog && acc;                         /* logic DEFOG: the A16 floor is ACC (D-350) */
        want[O5_FUEL]      = start || prime || engineRuns;         /* logic FUEL_PUMP (D-461) */
        want[O6_TAIL]      = (head == H_PASS) ? chOn[O6_TAIL] : (head >= H_PARK);   /* PASS holds */
        want[O7_BRAKE]     = brake;
        want[O8_WIPE_LO]   = (wipe == W_LOW || wipe == W_INT);
        want[O9_WIPE_HI]   = (wipe == W_HIGH);
        want[O10_ACC]      = acc || engineRuns;                    /* logic ACCESSORY (D-463); no release pulse here */
        want[O11_HORN]     = horn;
        want[O12_IGN]      = ignWant;
        want[O15_COMFORT]  = run;
        want[O16_BLOWER]   = false;                    /* motor is dead */
        want[O17_TURN_L]   = turnPhase && (turn == T_LEFT  || turn == T_HAZARD);
        want[O18_TURN_R]   = turnPhase && (turn == T_RIGHT || turn == T_HAZARD);
        want[O19_REVERSE]  = reverse && run;
        want[O20_INTERIOR] = (head == H_PASS) ? chOn[O20_INTERIOR] : (head >= H_PARK);  /* logic INTERIOR (D-462) */
        want[O21_START]    = start;
        want[O22_KEEPALIVE]= awake;

        if (shed) {                                    /* rules voltage (D-463, D-476) */
            want[O15_COMFORT] = false;
            want[O4_DEFOG]    = false;
            if (!engineRuns) { want[O10_ACC] = false; want[O20_INTERIOR] = false; }
        }

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
            if (i == O20_INTERIOR) base = 250u * (uint32_t)(dimPct < 0 ? 0 : dimPct > 100 ? 100 : dimPct) / 100u;

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

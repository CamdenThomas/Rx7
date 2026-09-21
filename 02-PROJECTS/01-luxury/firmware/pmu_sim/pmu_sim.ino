/*
 * pmu_sim.ino — PMU simulator on a spare Teensy 4.1
 *
 * Transmits CAN 0x100-0x130 exactly as the real PMU-24 DL will, driven by a
 * vehicle model that behaves like a 1982 RX-7. The ICU and DCU can then be
 * developed and demonstrated against a live bus months before the PMU is
 * configured or the car is wired.
 *
 * ============================================================
 *  AMP FIGURES ARE ESTIMATES until the meter session (T-014).
 *  All of them live in channels.h. Replace that one table and the
 *  whole simulation becomes accurate - nothing else changes.
 *  Two are already MEASURED: O7 brake 7.0 A, O17/O18 turn 3.4 A.
 * ============================================================
 *
 * SETUP
 *   1. Library Manager -> ACAN_T4
 *   2. Copy can_map.h from ../icu/ into this folder
 *   3. Wire CAN1 (pins 22/23) to a SN65HVD230, 120 ohm at each end of the bus
 *   4. Upload, Serial Monitor 115200, press ? for commands
 *
 * Works with NO transceiver too - it will report the TX failure and keep
 * running the model, so the console output is still useful.
 */

#include <ACAN_T4.h>
#include "can_map.h"
#include "vehicle_model.h"

Vehicle car;

static uint32_t lastTickMs = 0;
static uint8_t  counter100 = 0, counter110 = 0, counter120 = 0, counter130 = 0;
static uint8_t  muxChannel = 0;        /* 0x130 cycles all 24 */
static uint8_t  muxTrip    = 0;        /* 0x120 cycles trip flags */
static bool     canUp = false;
static bool     autoDrive = false;
static uint32_t driveMs = 0;

/* ---------------- CAN ---------------- */
static void sendFrame(uint16_t id, const void *payload) {
    if (!canUp) return;
    CANMessage f;
    f.id = id;
    f.len = 8;
    memcpy(f.data, payload, 8);
    ACAN_T4::can1.tryToSend(f);
}

static void txState() {
    pmu_state_t m = {};
    m.key_pos    = (uint8_t)car.key;
    m.wake_source = (car.key >= K_ACC ? WAKE_ACC : 0)
                  | (car.key >= K_RUN ? WAKE_RUN : 0)
                  | (car.turn == T_HAZARD ? WAKE_HAZARD : 0)
                  | (car.horn ? WAKE_HORN : 0);
    uint8_t fault = 0;
    for (int i = 0; i < 24; i++) if (car.chState[i] >= 2) fault |= FAULT_SOFTFUSE;
    if (car.voltsX10 < 115) fault |= FAULT_UNDERVOLT;
    if (car.voltsX10 > 150) fault |= FAULT_OVERVOLT;
    m.fault     = fault;
    m.headlight = (uint8_t)car.head;
    m.turn      = (uint8_t)car.turn;
    m.popup     = (uint8_t)car.popup;
    m.counter   = counter100++;
    sendFrame(ID_PMU_STATE, &m);
}

static void txPower() {
    pmu_power_t m = {};
    m.batt_mv  = (uint16_t)(car.voltsX10 * 100);
    m.total_ca = (uint16_t)(car.totalCurrent() / 10);   /* 0.01A -> 0.1A */
    m.charging = car.running ? 1 : 0;
    m.counter  = counter110++;
    sendFrame(ID_PMU_POWER, &m);
}

static void txOutputs() {
    pmu_outputs_t m = {};
    m.fuel_pct = (uint16_t)car.fuelPctX10;
    for (int i = 0; i < 24; i++)
        if (car.chState[i] == 1) m.out_state[i >> 3] |= (uint8_t)(1u << (i & 7));
    m.trip_index  = muxTrip;
    m.trip_status = car.chState[muxTrip];
    muxTrip = (uint8_t)((muxTrip + 1) % 24);
    m.counter = counter120++;
    sendFrame(ID_PMU_OUTPUTS, &m);
}

static void txChannel() {
    pmu_channel_t m = {};
    m.index      = muxChannel;
    m.current_ca = car.chCurrent[muxChannel];
    m.limit_ca   = CH[muxChannel].limit;
    m.status     = car.chState[muxChannel];
    m.counter    = counter130++;
    sendFrame(ID_PMU_CHANNEL, &m);
    muxChannel = (uint8_t)((muxChannel + 1) % 24);
}

/* ---------------- console ---------------- */
static void help() {
    Serial.println(F(
      "\n--- PMU SIMULATOR ---------------------------------------\n"
      " k0 k1 k2 k3   key OFF / ACC / RUN / START\n"
      " g <0-100>     throttle\n"
      " h0 h1 h2      headlights OFF / PARK / HEAD  (pop-ups follow)\n"
      " tl tr th to   turn LEFT / RIGHT / HAZARD / off\n"
      " w0 w1 w2 w3   wiper OFF / INT / LOW / HIGH\n"
      " b             brake toggle        n  horn toggle\n"
      " r             reverse toggle      d  defog toggle\n"
      " f <0-100>     fuel level %\n"
      " x <1-24>      trip that channel   c  clear all trips\n"
      " a             auto drive cycle on/off\n"
      " s             state dump          ?  this help\n"
      "----------------------------------------------------------"));
}

static void dump() {
    Serial.println();
    Serial.print(F("key "));    Serial.print(car.key);
    Serial.print(F("  rpm "));  Serial.print(car.rpm);
    Serial.print(F("  mph "));  Serial.print(car.speedMph);
    Serial.print(F("  water ")); Serial.print(car.waterCx10 / 10.0, 1);
    Serial.print(F("C  oilT ")); Serial.print(car.oilTempCx10 / 10.0, 1);
    Serial.print(F("C  oilP ")); Serial.print(car.oilPressCbar / 100.0, 2);
    Serial.print(F("bar  V ")); Serial.print(car.voltsX10 / 10.0, 1);
    Serial.print(F("  fuel ")); Serial.print(car.fuelPctX10 / 10.0, 1);
    Serial.print(F("%  total ")); Serial.print(car.totalCurrent() / 100.0, 2);
    Serial.println(F("A"));

    for (int i = 0; i < 24; i++) {
        if (!car.chState[i]) continue;
        Serial.print(F("  O")); Serial.print(i + 1);
        Serial.print(F(" ")); Serial.print(CH[i].name);
        Serial.print(F("  ")); Serial.print(car.chCurrent[i] / 100.0, 2);
        Serial.print(F("A / ")); Serial.print(CH[i].limit / 100.0, 2);
        Serial.print(F("A  "));
        Serial.print(car.chState[i] == 2 ? F("TRIPPED")
                   : car.chState[i] == 3 ? F("RETRY") : F("on"));
        if (CH[i].src == MEASURED) Serial.print(F("   [measured]"));
        Serial.println();
    }
}

static int readInt(const char *s) {
    int v = 0; bool any = false;
    for (const char *p = s; *p; p++)
        if (*p >= '0' && *p <= '9') { v = v * 10 + (*p - '0'); any = true; }
    return any ? v : -1;
}

static void command(char *line) {
    switch (line[0]) {
        case 'k': car.key = (KeyPos)(line[1] - '0'); break;
        case 'g': { int v = readInt(line + 1); if (v >= 0) car.throttle = v > 100 ? 100 : v; } break;
        case 'h': car.head = (HeadPos)(line[1] - '0'); break;
        case 't':
            if (line[1] == 'l') car.turn = T_LEFT;
            else if (line[1] == 'r') car.turn = T_RIGHT;
            else if (line[1] == 'h') car.turn = T_HAZARD;
            else car.turn = T_OFF;
            break;
        case 'w': car.wipe = (WipePos)(line[1] - '0'); break;
        case 'b': car.brake = !car.brake; break;
        case 'n': car.horn = !car.horn; break;
        case 'r': car.reverse = !car.reverse; break;
        case 'd': car.defog = !car.defog; break;
        case 'f': { int v = readInt(line + 1); if (v >= 0) car.fuelPctX10 = v * 10; } break;
        case 'x': { int v = readInt(line + 1); if (v >= 1 && v <= 24) {
                        car.tripChannel(v - 1);
                        Serial.print(F("tripped O")); Serial.println(v); } } break;
        case 'c': car.clearTrips(); Serial.println(F("trips cleared")); break;
        case 'a': autoDrive = !autoDrive; driveMs = 0;
                  Serial.println(autoDrive ? F("auto drive ON") : F("auto drive OFF")); break;
        case 's': dump(); break;
        default:  help(); break;
    }
}

static void pollSerial() {
    static char line[24]; static uint8_t n = 0;
    while (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '\n' || c == '\r') {
            if (n) { line[n] = 0; command(line); n = 0; }
        } else if (n < sizeof(line) - 1) {
            line[n++] = c;
        }
    }
}

/* ---------------- scripted drive ----------------
 * A repeatable cycle, so the cluster can be judged hands-off and two
 * firmware revisions can be compared against identical input. */
static void autoCycle(uint32_t dt) {
    if (!autoDrive) return;
    driveMs += dt;
    uint32_t t = driveMs / 1000;

    if      (t <  2) { car.key = K_ACC;  car.throttle = 0; }
    else if (t <  4) { car.key = K_START; }
    else if (t <  8) { car.key = K_RUN;  car.throttle = 0;  car.head = H_PARK; }
    else if (t < 14) { car.throttle = 35; car.turn = T_RIGHT; }
    else if (t < 20) { car.throttle = 70; car.turn = T_OFF; car.head = H_HEAD; }
    else if (t < 24) { car.throttle = 95; }
    else if (t < 28) { car.throttle = 20; car.brake = true; }
    else if (t < 32) { car.brake = false; car.throttle = 50; car.turn = T_LEFT; }
    else if (t < 36) { car.turn = T_OFF; car.wipe = W_LOW; car.defog = true; }
    else if (t < 40) { car.throttle = 0; car.wipe = W_OFF; }
    else if (t == 40) { car.tripChannel(O6_TAIL); }
    else if (t < 46) { /* watch the trip and retry */ }
    else { driveMs = 0; car.clearTrips(); car.key = K_OFF;
           car.head = H_OFF; car.defog = false; }
}

/* ---------------- setup ---------------- */
void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {}

    Serial.println(F("PMU-24 DL SIMULATOR"));
    Serial.print(F("channel currents still estimated: "));
    Serial.print(estimatedChannelCount());
    Serial.println(F(" of 24   <- fix in channels.h after T-014"));

    ACAN_T4_Settings settings(500 * 1000);          /* D-086 */
    const uint32_t err = ACAN_T4::can1.begin(settings);
    canUp = (err == 0);
    if (canUp) Serial.println(F("CAN1 up at 500 kbps"));
    else {
        Serial.print(F("CAN1 failed 0x")); Serial.println(err, HEX);
        Serial.println(F("Running model only - console still works."));
    }

    lastTickMs = millis();
    help();
}

/* ---------------- loop ---------------- */
void loop() {
    uint32_t now = millis();
    uint32_t dt  = now - lastTickMs;
    if (dt < 10) return;                 /* 100 Hz model */
    lastTickMs = now;

    pollSerial();
    autoCycle(dt);
    car.update(now, dt);

    /* transmit at the rates in CAN-MESSAGES.md */
    static uint32_t t100 = 0, t110 = 0, t120 = 0, t130 = 0;
    if (now - t100 >= 50)  { t100 = now; txState();   }   /* 20 Hz */
    if (now - t110 >= 100) { t110 = now; txPower();   }   /* 10 Hz */
    if (now - t120 >= 200) { t120 = now; txOutputs(); }   /*  5 Hz */
    if (now - t130 >= 200) { t130 = now; txChannel(); }   /*  5 Hz mux */

    /* heartbeat, and a periodic one-line summary */
    static uint32_t tPrint = 0;
    if (now - tPrint > 2000) {
        tPrint = now;
        digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
        Serial.print(F("rpm ")); Serial.print(car.rpm);
        Serial.print(F("  mph ")); Serial.print(car.speedMph);
        Serial.print(F("  H2O ")); Serial.print(car.waterCx10 / 10);
        Serial.print(F("C  oil ")); Serial.print(car.oilPressCbar / 100.0, 1);
        Serial.print(F("bar  ")); Serial.print(car.voltsX10 / 10.0, 1);
        Serial.print(F("V  load ")); Serial.print(car.totalCurrent() / 100.0, 1);
        Serial.println(F("A"));
    }
}

/*
 * dcu.ino — Teensy 4.1 host for the DCU (climate + comfort node)
 *
 * F-001 skeleton, mirroring icu.ino: this file is ONLY the host — CAN
 * plumbing, servo/MOSFET pins, SD persistence, timing. All logic lives
 * in climate.h and is testable off-target.
 *
 * Library: ACAN_T4 (NOT FlexCAN_T4 — same rule as the ICU).
 * Pins are provisional until the H-002 carrier PCB freezes them.
 */

#define DCU_FW_VERSION "0.1.0-dev"

#include <ACAN_T4.h>
#include <Servo.h>
#include <SD.h>
#include "climate.h"

/* ---- provisional pin map (H-002 owns the final one) ---- */
static const int PIN_SERVO[SRV_COUNT] = { 2, 3, 4 };
static const int PIN_COMFORT[CMF_COUNT] = { 5, 6, 7, 8, 9, 10, 11 };
static const int PIN_CABIN_NTC = A0;

Servo       servo[SRV_COUNT];
dcu_state_t dcu;

/* ---- CAN plumbing ---- */
static uint8_t  tx_counter_300 = 0, tx_counter_310 = 0;
static uint8_t  rx_counter_100 = 0, rx_counter_400 = 0, kp_prev = 0;
static uint32_t last_rx_100 = 0, last_tx_300 = 0, last_tx_310 = 0;
static uint32_t last_activity = 0;

static void send_climate() {
    dcu_climate_t m = {};
    m.mode       = dcu.mem.mode;
    m.blower     = dcu.mem.blower;
    m.target_c   = dcu.mem.target_c;
    m.cabin_c    = dcu.cabin_c;
    m.ac_request = 0;                    /* compressor is factory (D-012) */
    m.counter    = tx_counter_300++;
    CANMessage f; f.id = ID_DCU_CLIMATE; f.len = CAN_MSG_LEN;
    memcpy(f.data, &m, sizeof m);
    ACAN_T4::can2.tryToSend(f);
}

static void send_comfort() {
    dcu_comfort_t m = {};
    m.seat_heat      = dcu.mem.seat_heat;
    m.seat_cool      = dcu.mem.seat_cool;
    m.mirror_heat    = dcu.comfort_on[CMF_MIRROR_HEAT];
    m.nozzle_deice   = (uint8_t)(dcu.comfort_on[CMF_NOZZLE] | (dcu.comfort_on[CMF_DEICER] << 1));
    m.bus_current_ca = dcu.bus_current_ca;
    m.counter        = tx_counter_310++;
    CANMessage f; f.id = ID_DCU_COMFORT; f.len = CAN_MSG_LEN;
    memcpy(f.data, &m, sizeof m);
    ACAN_T4::can2.tryToSend(f);
}

static void dispatch(const CANMessage &f) {
    last_activity = millis();
    switch (f.id) {
    case ID_PMU_STATE: {
        pmu_state_t m; memcpy(&m, f.data, sizeof m);
        dcu.pmu_alive = can_counter_advanced(rx_counter_100, m.counter);
        rx_counter_100 = m.counter;
        dcu.key_pos = m.key_pos;
        last_rx_100 = millis();
        break; }
    case ID_KEYPAD: {
        keypad_t m; memcpy(&m, f.data, sizeof m);
        if (can_counter_advanced(rx_counter_400, m.counter)) {
            uint8_t edges = (uint8_t)(m.buttons & (uint8_t)~kp_prev);
            kp_prev = m.buttons;
            if (edges) { apply_keypad(&dcu, edges); enforce_seat_interlock(&dcu); }
        }
        rx_counter_400 = m.counter;
        break; }
    default: break;
    }
}

/* ---- SD climate memory (settles V-056: restore on wake, no keep-alive) ---- */
static const char *MEM_FILE = "dcu_mem.bin";

/* mem_crc / mem_defaults live in climate.h (tested on the desktop). */
static void mem_load() {
    File f = SD.open(MEM_FILE, FILE_READ);
    if (f && f.read((uint8_t *)&dcu.mem, sizeof dcu.mem) == (int)sizeof dcu.mem
          && dcu.mem.crc == mem_crc(&dcu.mem)) { f.close(); return; }
    if (f) f.close();
    mem_defaults(&dcu.mem);              /* missing/corrupt: safe defaults */
}
static void mem_save() {
    dcu.mem.crc = mem_crc(&dcu.mem);
    File f = SD.open(MEM_FILE, FILE_WRITE_BEGIN);
    if (f) { f.write((const uint8_t *)&dcu.mem, sizeof dcu.mem); f.close(); }
}

/* ---- outputs ---- */
static void apply_outputs() {
    uint8_t ok = comfort_permitted(&dcu);
    for (int i = 0; i < CMF_COUNT; i++)
        digitalWrite(PIN_COMFORT[i], (ok && dcu.comfort_on[i]) ? HIGH : LOW);
    for (int i = 0; i < SRV_COUNT; i++)
        servo[i].writeMicroseconds(dcu.mem.cal[i].us_now);
}

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {}
    Serial.print("DCU — Teensy host, firmware "); Serial.println(DCU_FW_VERSION);

    for (int i = 0; i < CMF_COUNT; i++) { pinMode(PIN_COMFORT[i], OUTPUT); digitalWrite(PIN_COMFORT[i], LOW); }
    for (int i = 0; i < SRV_COUNT; i++) servo[i].attach(PIN_SERVO[i]);

    if (!SD.begin(BUILTIN_SDCARD)) Serial.println("SD missing — defaults, no persistence");
    mem_load();
    dcu.cabin_c = TEMP_INVALID;
    mode_to_servos(&dcu);
    enforce_seat_interlock(&dcu);

    ACAN_T4_Settings settings(CAN_BITRATE);
    const uint32_t err = ACAN_T4::can2.begin(settings);
    Serial.print("CAN2 begin: 0x"); Serial.println(err, HEX);
}

void loop() {
    CANMessage f;
    while (ACAN_T4::can2.receive(f)) dispatch(f);

    uint32_t now = millis();
    if (now - last_rx_100 > TMO_PMU_STATE) dcu.pmu_alive = 0;   /* blank, never hold */
    if (now - last_tx_300 >= 200) { last_tx_300 = now; send_climate(); }   /* 5 Hz */
    if (now - last_tx_310 >= 500) { last_tx_310 = now; send_comfort(); }   /* 2 Hz */

    apply_outputs();

    /* Save on key-off edge: one write per shutdown, not on every twiddle. */
    static uint8_t last_key = KEY_OFF;
    if (last_key != KEY_OFF && dcu.key_pos == KEY_OFF) mem_save();
    last_key = dcu.key_pos;

    delay(5);
}

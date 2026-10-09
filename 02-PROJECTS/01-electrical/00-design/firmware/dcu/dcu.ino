/*
 * dcu.ino — Teensy 4.1 host for the DCU (climate, comfort, panel, windows,
 * mirrors, release select)
 *
 * Mirroring icu.ino: this file is ONLY the host — CAN plumbing, pins, SD
 * persistence, timing. All logic lives in climate.h and panel.h and is
 * testable off-target (tests/test_dcu.cpp).
 *
 * Library: ACAN_T4 (NOT FlexCAN_T4 — same rule as the ICU).
 * Pins are provisional until the H-002 carrier freezes them. The map below
 * needs 44 I/O besides CAN2: the mirror bridge sits on the bottom pads
 * 48-54, which are free only with no PSRAM fitted - H-002 settles it.
 */

#define DCU_FW_VERSION "0.3.1-dev"   /* can_map.h to the record (Y8); F-017: panel, 0x400 sent, windows, mirrors, release, wake */

#include <ACAN_T4.h>
#include <Servo.h>
#include <SD.h>
#include "climate.h"
#include "panel.h"

extern "C" uint32_t set_arm_clock(uint32_t frequency);   /* Teensy 4 core */

/* ---- provisional pin map (H-002 owns the final one) ---- */
static const int PIN_SERVO[SRV_COUNT]   = { 2, 3, 4 };              /* SN15 mode · blend · recirc */
static const int PIN_COMFORT[CMF_COUNT] = { 5, 6, 7, 8, 9 };        /* SN16, climate.h order      */
static const int PIN_BLOWER      = 10;                              /* SN14, PWM >= 20 kHz        */
static const int PIN_WAKE        = 11;                              /* SN21 -> DP-DCU 6           */
static const int PIN_CABIN_NTC   = A0;                              /* SN11 */
static const int PIN_OAT_NTC     = A1;                              /* SN12 */
static const int PIN_CURRENT     = A2;                              /* SN13 */
static const int PIN_JOY_PRESS   = 17;                              /* ribbon 19 */
static const int PIN_JOY_X       = A6;                              /* ribbon 17 */
static const int PIN_JOY_Y       = A7;                              /* ribbon 18 */
static const int PIN_WIN[4]      = { 22, 23, 24, 25 };              /* SN22: DRV up, DRV dn, PASS up, PASS dn -> DP-DCU-B 1-4 */
static const int PIN_REL_HATCH   = 26;                              /* SN23: K3 85, DP-DCU-B 10 */
static const int PIN_REL_FUEL    = 27;                              /* SN23: K4 85, DP-DCU-B 11 */
static const int PIN_ROW[PANEL_ROWS] = { 28, 29, 30 };              /* ribbon 3-5 */
static const int PIN_COL[PANEL_COLS] = { 31, 32, 33 };              /* ribbon 6-8 */
enum { ENC_FAN = 0, ENC_TEMP, ENC_SEAT_DRV, ENC_SEAT_PASS, ENC_COUNT };
static const int PIN_ENC_A[ENC_COUNT] = { 18, 34, 36, 38 };         /* ribbon 9, 11, 13, 15 */
static const int PIN_ENC_B[ENC_COUNT] = { 19, 35, 37, 39 };         /* ribbon 10, 12, 14, 16 */
/* SN17, DRV8962-Q1 in independent half-bridge mode: IN sets high/low, EN
 * off = open. Channel 4's IN is tied low on the carrier: its EN is the
 * clutch sink (D-360, D-379). */
static const int PIN_MIR_COM_IN = 48, PIN_MIR_COM_EN = 49;
static const int PIN_MIR_L_IN   = 50, PIN_MIR_L_EN   = 51;
static const int PIN_MIR_R_IN   = 52, PIN_MIR_R_EN   = 53;
static const int PIN_MIR_CLUTCH = 54;
#define WAKE_ACTIVE HIGH            /* confirm against the wake strip's input (SN21) */

/* ---- commissioning values (F6) ---- */
static stick_cal_t stick;           /* stick_defaults() until commissioned */
static const uint16_t CURRENT_ZERO = 0;   /* SN13 no-load reading */

Servo         servo[SRV_COUNT];
dcu_state_t   dcu;
panel_t       panel;
keys_tx_t     keys_tx;
window_t      win[2];
mirror_t      mirror;
servo_seq_t   servo_seq;

/* ---- encoders: sampled at 1 kHz, detents collected for the loop ---- */
static enc_t        enc[ENC_COUNT];
static volatile int enc_detents[ENC_COUNT];
static IntervalTimer enc_timer;

static void enc_isr() {
    for (int i = 0; i < ENC_COUNT; i++) {
        uint8_t ab = (uint8_t)((digitalRead(PIN_ENC_A[i]) << 1) | digitalRead(PIN_ENC_B[i]));
        enc_detents[i] += enc_step(&enc[i], ab);
    }
}
static int enc_take(int i) {
    noInterrupts(); int d = enc_detents[i]; enc_detents[i] = 0; interrupts();
    return d;
}

/* ---- key matrix: rows driven low one at a time, the rest left open ---- */
static uint16_t scan_matrix() {
    uint16_t raw = 0;
    for (int r = 0; r < PANEL_ROWS; r++) {
        for (int k = 0; k < PANEL_ROWS; k++) pinMode(PIN_ROW[k], INPUT);
        pinMode(PIN_ROW[r], OUTPUT); digitalWrite(PIN_ROW[r], LOW);
        delayMicroseconds(10);
        for (int c = 0; c < PANEL_COLS; c++)
            if (digitalRead(PIN_COL[c]) == LOW) raw |= matrix_bit((uint8_t)r, (uint8_t)c);
    }
    for (int k = 0; k < PANEL_ROWS; k++) pinMode(PIN_ROW[k], INPUT);
    if (digitalRead(PIN_JOY_PRESS) == LOW) raw |= PK_MIRROR_PRESS;
    return raw;
}

/* ---- CAN plumbing ---- */
static uint8_t  tx_counter_300 = 0, tx_counter_310 = 0;
static uint8_t  rx_counter_100 = 0;
static uint32_t last_rx_100 = 0, last_rx_120 = 0, last_tx_300 = 0, last_tx_310 = 0;
static uint32_t last_activity = 0;
static uint8_t  defog_on = 0;

static void send_frame(uint32_t id, const void *payload) {
    CANMessage f; f.id = id; f.len = CAN_MSG_LEN;
    memcpy(f.data, payload, CAN_MSG_LEN);
    ACAN_T4::can2.tryToSend(f);
}

static void send_climate() {
    dcu_climate_t m = {};
    m.mode       = dcu.mem.mode;
    m.blower     = blower_duty_pct(dcu.mem.blower);
    m.target_c   = dcu.mem.target_c;
    m.cabin_c    = dcu.cabin_c;
    m.ac_request = 0;                    /* compressor is factory (D-012) */
    m.outside_c  = ntc_to_c((uint16_t)analogRead(PIN_OAT_NTC));   /* SN12, blank when implausible */
    m.counter    = tx_counter_300++;
    send_frame(ID_DCU_CLIMATE, &m);
}

static void send_comfort() {
    dcu_comfort_t m = {};
    m.seat_heat      = dcu.mem.seat_heat;
    m.seat_cool      = dcu.mem.seat_cool;
    m.mirror_heat    = dcu.comfort_on[CMF_MIRROR_HEAT];
    m.bus_current_ca = dcu.bus_current_ca;
    m.counter        = tx_counter_310++;
    send_frame(ID_DCU_COMFORT, &m);
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
    case ID_PMU_OUTPUTS: {               /* mirror heat follows O4 (D-442) */
        pmu_outputs_t m; memcpy(&m, f.data, sizeof m);
        defog_on = pmu_out_on(&m, PMU_OUT_DEFOG);
        last_rx_120 = millis();
        break; }
    /* 0x400 is not received: the DCU reads the panel on its own ribbon and
     * SENDS 0x400 (D-355, F-016, F-017). */
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
static uint8_t hb_state[64];                            /* by EN pin; 0 = HB_OFF */
static void half_bridge(int in, int en, uint8_t hb) {
    if (hb_state[en] == hb) return;                     /* touch it only on a change */
    hb_state[en] = hb;
    digitalWrite(en, LOW);                               /* open before changing side */
    if (hb == HB_OFF) return;
    digitalWrite(in, hb == HB_HIGH ? HIGH : LOW);
    digitalWrite(en, HIGH);
}

static void all_outputs_off() {
    for (int i = 0; i < CMF_COUNT; i++) digitalWrite(PIN_COMFORT[i], LOW);
    for (int i = 0; i < 4; i++) digitalWrite(PIN_WIN[i], LOW);
    digitalWrite(PIN_REL_HATCH, LOW); digitalWrite(PIN_REL_FUEL, LOW);
    digitalWrite(PIN_MIR_COM_EN, LOW); digitalWrite(PIN_MIR_L_EN, LOW);
    digitalWrite(PIN_MIR_R_EN, LOW); digitalWrite(PIN_MIR_CLUTCH, LOW);
    memset(hb_state, 0, sizeof hb_state);
    analogWrite(PIN_BLOWER, 0);
}

static void apply_outputs(uint32_t now) {
    uint8_t ok = comfort_permitted(&dcu);
    for (int i = 0; i < CMF_COUNT; i++)
        digitalWrite(PIN_COMFORT[i], (ok && dcu.comfort_on[i]) ? HIGH : LOW);
    analogWrite(PIN_BLOWER, (int)blower_duty_pct(dcu.mem.blower) * 255 / 100);

    int i = servo_seq_step(&servo_seq, dcu.mem.cal, now);   /* one servo at a time (D-379) */
    if (i >= 0) {
        if (!servo[i].attached()) servo[i].attach(PIN_SERVO[i]);
        servo[i].writeMicroseconds(servo_seq.applied[i]);
    }
}

/* ---- sleep: rows held low so any key interrupts (D-380); the loop resumes
 * on a key or a CAN frame. The draw is measured at F6 against LD17. ---- */
static volatile uint8_t key_woke = 0;
static void col_isr() { key_woke = 1; }

static void dcu_sleep() {
    all_outputs_off();
    digitalWrite(PIN_WAKE, !WAKE_ACTIVE);
    for (int i = 0; i < SRV_COUNT; i++) if (servo[i].attached()) servo[i].detach();
    memset(servo_seq.applied, 0, sizeof servo_seq.applied);   /* re-attach one at a time */
    enc_timer.end();
    for (int r = 0; r < PANEL_ROWS; r++) { pinMode(PIN_ROW[r], OUTPUT); digitalWrite(PIN_ROW[r], LOW); }
    key_woke = 0;
    for (int c = 0; c < PANEL_COLS; c++) attachInterrupt(digitalPinToInterrupt(PIN_COL[c]), col_isr, FALLING);
    set_arm_clock(24000000);
    while (!key_woke && !ACAN_T4::can2.available()) asm volatile("wfi");
    set_arm_clock(600000000);
    for (int c = 0; c < PANEL_COLS; c++) detachInterrupt(digitalPinToInterrupt(PIN_COL[c]));
    for (int r = 0; r < PANEL_ROWS; r++) pinMode(PIN_ROW[r], INPUT);
    enc_timer.begin(enc_isr, 1000);
    last_activity = millis();
}

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {}
    Serial.print("DCU — Teensy host, firmware "); Serial.println(DCU_FW_VERSION);

    /* every output off before anything else runs */
    const int outs[] = { PIN_COMFORT[0], PIN_COMFORT[1], PIN_COMFORT[2], PIN_COMFORT[3], PIN_COMFORT[4],
                         PIN_WIN[0], PIN_WIN[1], PIN_WIN[2], PIN_WIN[3], PIN_REL_HATCH, PIN_REL_FUEL,
                         PIN_MIR_COM_IN, PIN_MIR_COM_EN, PIN_MIR_L_IN, PIN_MIR_L_EN,
                         PIN_MIR_R_IN, PIN_MIR_R_EN, PIN_MIR_CLUTCH, PIN_BLOWER };
    for (int p : outs) { pinMode(p, OUTPUT); digitalWrite(p, LOW); }
    pinMode(PIN_WAKE, OUTPUT); digitalWrite(PIN_WAKE, !WAKE_ACTIVE);
    analogWriteFrequency(PIN_BLOWER, 25000);
    for (int k = 0; k < PANEL_ROWS; k++) pinMode(PIN_ROW[k], INPUT);
    for (int c = 0; c < PANEL_COLS; c++) pinMode(PIN_COL[c], INPUT_PULLUP);
    pinMode(PIN_JOY_PRESS, INPUT_PULLUP);
    for (int i = 0; i < ENC_COUNT; i++) {
        pinMode(PIN_ENC_A[i], INPUT_PULLUP); pinMode(PIN_ENC_B[i], INPUT_PULLUP);
        enc[i].ab = (uint8_t)((digitalRead(PIN_ENC_A[i]) << 1) | digitalRead(PIN_ENC_B[i]));
    }
    analogReadResolution(12);
    stick_defaults(&stick);

    if (!SD.begin(BUILTIN_SDCARD)) Serial.println("SD missing — defaults, no persistence");
    mem_load();
    dcu.cabin_c = TEMP_INVALID;
    mode_to_servos(&dcu);
    enforce_seat_interlock(&dcu);

    ACAN_T4_Settings settings(CAN_BITRATE);
    const uint32_t err = ACAN_T4::can2.begin(settings);
    Serial.print("CAN2 begin: 0x"); Serial.println(err, HEX);
    enc_timer.begin(enc_isr, 1000);
}

void loop() {
    CANMessage f;
    while (ACAN_T4::can2.receive(f)) dispatch(f);

    uint32_t now = millis();
    if (now - last_rx_100 > TMO_PMU_STATE) dcu.pmu_alive = 0;    /* blank, never hold */
    if (now - last_rx_120 > TMO_PMU_OUTPUTS) defog_on = 0;

    /* panel: keys, then the release select, THEN 0x400 - K3/K4 are grounded
     * before the PMU can see the edge (D-370) */
    uint16_t down, held;
    uint16_t pressed = panel_keys_step(&panel, scan_matrix(), dcu.pmu_alive, now, &down, &held);
    if (pressed) last_activity = now;
    digitalWrite(PIN_REL_HATCH, panel.rel_sel == PK_HATCH     ? HIGH : LOW);
    digitalWrite(PIN_REL_FUEL,  panel.rel_sel == PK_FUEL_DOOR ? HIGH : LOW);
    digitalWrite(PIN_WAKE, panel.wake_req ? WAKE_ACTIVE : !WAKE_ACTIVE);
    panel_keys_t pk;
    if (dcu.pmu_alive && panel_frame_due(&keys_tx, down, held, now, &pk)) send_frame(ID_PANEL_KEYS, &pk);

    /* knobs and climate keys */
    panel_apply(&dcu, pressed, enc_take(ENC_FAN), enc_take(ENC_TEMP),
                enc_take(ENC_SEAT_DRV), enc_take(ENC_SEAT_PASS));
    dcu.comfort_on[CMF_MIRROR_HEAT] = defog_on;
    dcu.cabin_c = ntc_to_c((uint16_t)analogRead(PIN_CABIN_NTC));
    dcu.bus_current_ca = comfort_current_ca((uint16_t)analogRead(PIN_CURRENT), CURRENT_ZERO);

    /* windows (D-363) */
    uint8_t body = body_permitted(&dcu), up, dn;
    window_step(&win[0], (down & PK_WIN_DRV_UP) != 0,  (down & PK_WIN_DRV_DN) != 0,  body, now, &up, &dn);
    digitalWrite(PIN_WIN[0], up); digitalWrite(PIN_WIN[1], dn);
    window_step(&win[1], (down & PK_WIN_PASS_UP) != 0, (down & PK_WIN_PASS_DN) != 0, body, now, &up, &dn);
    digitalWrite(PIN_WIN[2], up); digitalWrite(PIN_WIN[3], dn);

    /* mirrors (D-359, D-360) */
    uint8_t axis; int8_t dir; mirror_out_t mo;
    stick_read(&stick, (uint16_t)analogRead(PIN_JOY_X), (uint16_t)analogRead(PIN_JOY_Y), &axis, &dir);
    mirror_step(&mirror, pressed, axis, dir, body, now, &mo);
    half_bridge(PIN_MIR_COM_IN, PIN_MIR_COM_EN, mo.common);
    half_bridge(PIN_MIR_L_IN,   PIN_MIR_L_EN,   mo.left);
    half_bridge(PIN_MIR_R_IN,   PIN_MIR_R_EN,   mo.right);
    digitalWrite(PIN_MIR_CLUTCH, mo.clutch ? HIGH : LOW);

    if (dcu.pmu_alive) {                 /* nothing on a sleeping bus */
        if (now - last_tx_300 >= 200) { last_tx_300 = now; send_climate(); }   /* 5 Hz */
        if (now - last_tx_310 >= 500) { last_tx_310 = now; send_comfort(); }   /* 2 Hz */
    }

    apply_outputs(now);

    /* Save on key-off edge: one write per shutdown, not on every twiddle. */
    static uint8_t last_key = KEY_OFF;
    if (last_key != KEY_OFF && dcu.key_pos == KEY_OFF) mem_save();
    last_key = dcu.key_pos;

    if (sleep_due(&panel, dcu.pmu_alive, now - last_activity)) dcu_sleep();

    delay(5);
}

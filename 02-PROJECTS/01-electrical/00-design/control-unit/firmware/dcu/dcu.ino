/*
 * dcu.ino — Teensy 4.1 host for the DCU (climate, comfort, panel, windows,
 * mirrors, release select)
 *
 * Mirroring icu.ino: this file is ONLY the host — CAN plumbing, pins, SD
 * persistence, timing. All logic lives in climate.h, panel.h, tca9539.h
 * (the expander and the DRV8962 guard), lights.h (the panel's and the left
 * plate's LED drivers) and screen.h (the screen's content) and is testable off-target
 * (00-design/tests/test_dcu.cpp).
 *
 * Library: ACAN_T4 (NOT FlexCAN_T4 — same rule as the ICU).
 * Pins: pins.h, which is dcu_channels.teensy_pin (D-452). All 42 edge pins
 * are used; the slow lines - the DRV8962 mirror driver, the PROFETs' DEN /
 * DSEL, CAN STB and the buck's power-good - are on the TCA9539-Q1 expander
 * U12 on Wire (18 / 19, INT 12, RESET 13), and the wake request and the
 * BTS3011TE STATUS lines on the second, U13 (Y11, D-577), through tca9539.h.
 */

#define DCU_FW_VERSION "0.8.0-dev"   /* D-580 / D-581 (F-020): the screen knob on the panel bus (0x36) - the Display Unit's pages and level in 0x400 bytes 4-5, its push b14 */
/* 0.7.0-dev: D-577 / D-578 (F-019): the dash-light stage on 11 at 200 Hz, the wake request and the STATUS lines on U13, 0x300 byte 6, the level on the centre knob's held push */
/* 0.6.0-dev: D-492 (F-018): the 4 x 3 matrix, the centre knob's modes, the mirror-defog key, the mirror select, the lights, the screen's content */
/* 0.5.0-dev: D-465: a release only with the car stopped (0x200 road speed 0, fresh), the select dropped 1.5 s after it is raised */
/* 0.4.0-dev: D-452 pin map: expander on Wire, fan encoder 40 / 41, CAN STB held low, DRV8962 fault clear (F-017) */

#include <ACAN_T4.h>
#include <Servo.h>
#include <SD.h>
#include <Wire.h>
#include "climate.h"
#include "panel.h"
#include "pins.h"
#include "tca9539.h"
#include "lights.h"
#include "screen.h"
#include "screen_knob.h"

extern "C" uint32_t set_arm_clock(uint32_t frequency);   /* Teensy 4 core */

/* ---- pins: pins.h (dcu_channels.teensy_pin) ---- */
static_assert(sizeof PIN_SERVO / sizeof PIN_SERVO[0] == SRV_COUNT, "one pin per servo");
static_assert(sizeof PIN_COMFORT / sizeof PIN_COMFORT[0] == CMF_COUNT, "one pin per comfort channel");
static_assert(sizeof PIN_ROW / sizeof PIN_ROW[0] == PANEL_ROWS && sizeof PIN_COL / sizeof PIN_COL[0] == PANEL_COLS,
              "the matrix is 4 x 3 (D-492)");
/* The wake request (SN21) is U13 P02: high turns the NPN on, which turns the 12 V
 * PMOS on; confirm against the wake strip's input. */

/* ---- commissioning values (F6) ---- */
static stick_cal_t stick;           /* stick_defaults() until commissioned */
static const uint16_t CURRENT_ZERO = 0;   /* SN13 no-load reading */

Servo         servo[SRV_COUNT];
tca9539_t     exp_io;               /* U12 */
tca9539_t     exp_io2;              /* U13: the wake request, the STATUS lines */
drv_guard_t   drv;                  /* the DRV8962 behind it */
dcu_state_t   dcu;
panel_t       panel;
keys_tx_t     keys_tx;
window_t      win[2];
mirror_t      mirror;
servo_seq_t   servo_seq;
knob_t        knob;                 /* the centre knob's mode (D-492) */
sknob_t       sknob;                /* the screen knob: pages and the display level (D-580) */
mirror_defog_t mdefog;              /* the mirror-defog key (D-492) */
lights_t      lights;               /* the panel's and the plate's LED drivers */
lights_in_t   light_in;
lights_out_t  light_out;
screen_t      scr;                  /* the screen's content - no driver yet (P201) */

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
    if (digitalRead(PIN_JOY_PRESS) == LOW)   raw |= PK_MIRROR_PRESS;
    if (digitalRead(PIN_CENTRE_PUSH) == LOW) raw |= PK_CENTRE_PUSH;
    return raw;
}

/* ---- CAN plumbing ---- */
static uint8_t  tx_counter_300 = 0, tx_counter_310 = 0;
static uint8_t  rx_counter_100 = 0;
static uint32_t last_rx_100 = 0, last_rx_120 = 0, last_tx_300 = 0, last_tx_310 = 0;
static uint32_t last_rx_200 = 0;     /* the ICU's 0x200: road speed, for the release interlock (D-465) */
static uint8_t  seen_200 = 0, speed_kph = 0xFF;
static uint32_t last_activity = 0;
static uint8_t  defog_on = 0;        /* O4 in 0x120: lights the rear-defog key (D-492) */
static uint8_t  headlight = HL_OFF;  /* 0x100 byte 3: the backlights follow it (D-458, D-492) */
static int8_t   outside_c = TEMP_INVALID;   /* SN12, read once a loop: 0x300 and the screen */

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
    m.outside_c  = outside_c;            /* SN12, blank when implausible */
    m.dash_pct   = dash_clamp(dcu.mem.dash_pct);   /* SN31: what the stage runs at (D-577) */
    m.counter    = tx_counter_300++;
    send_frame(ID_DCU_CLIMATE, &m);
}

static void send_comfort() {
    dcu_comfort_t m = {};
    m.seat_heat      = dcu.mem.seat_heat;
    m.seat_cool      = dcu.mem.seat_cool;
    m.mirror_heat    = dcu.comfort_on[CMF_MIRROR_HEAT];   /* the mirror-defog key's state (D-492) */
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
        headlight = m.headlight;
        last_rx_100 = millis();
        break; }
    case ID_ICU_SENSORS: {               /* road speed: a release only with the car stopped (D-465) */
        icu_sensors_t m; memcpy(&m, f.data, sizeof m);
        speed_kph = m.speed_kph;
        last_rx_200 = millis(); seen_200 = 1;
        break; }
    case ID_PMU_OUTPUTS: {               /* O4: the rear-defog key's light (D-492; D-442 had mirror heat follow it) */
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

/* ---- the expander's bus (tca9539.h's four calls) ---- */
uint8_t exp_hal_write(uint8_t addr, const uint8_t *buf, uint8_t n) {
    Wire.beginTransmission(addr);
    Wire.write(buf, n);
    return Wire.endTransmission() == 0;
}
uint8_t exp_hal_read(uint8_t addr, uint8_t reg, uint8_t *buf, uint8_t n) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    if (Wire.endTransmission(false) != 0) return 0;          /* repeated start */
    if (Wire.requestFrom(addr, n) != n) return 0;
    for (uint8_t i = 0; i < n; i++) buf[i] = (uint8_t)Wire.read();
    return 1;
}
void exp_hal_reset(uint8_t asserted) { digitalWrite(PIN_EXP_RESET, asserted ? LOW : HIGH); }
void exp_hal_delay_us(uint32_t us)   { delayMicroseconds(us); }

/* ---- the LED drivers' bus (lights.h's one call): the same Wire, out on the ribbon ---- */
uint8_t lights_hal_write(uint8_t addr, const uint8_t *buf, uint8_t n) {
    Wire.beginTransmission(addr);
    Wire.write(buf, n);
    return Wire.endTransmission() == 0;
}

/* ---- the screen knob (SN32, D-580): its seesaw board polled on the same Wire. One step a
 * pass, never waiting: ask for the detents, read them and ask for the push, read the push. ---- */
static uint8_t  sk_ok = 0, sk_phase = 0, sk_push = 0;
static int      sk_detents = 0;
static uint32_t sk_t_init = 0;

static uint8_t sk_write(const uint8_t *b, uint8_t n) {
    Wire.beginTransmission(SKNOB_ADDR);
    Wire.write(b, n);
    return Wire.endTransmission() == 0;
}
static uint8_t sk_read4(uint8_t *b) {
    if (Wire.requestFrom((uint8_t)SKNOB_ADDR, (uint8_t)4) != 4) return 0;
    for (int i = 0; i < 4; i++) b[i] = (uint8_t)Wire.read();
    return 1;
}
static void sknob_setup() {
    uint8_t f[6];
    sk_ok = 1; sk_phase = 0;
    for (int i = 0; i < 3; i++) { sknob_pin_frame(f, SKNOB_SETUP_REGS[i]); sk_ok &= sk_write(f, 6); }
}
static void sknob_service(uint32_t now) {
    if (!sk_ok) {
        sk_push = 0;
        if (now - sk_t_init >= SKNOB_RETRY_MS) { sk_t_init = now; sknob_setup(); }
        return;
    }
    uint8_t b[4];
    static const uint8_t ASK_DELTA[2] = { SS_ENCODER_BASE, SS_ENCODER_DELTA };
    static const uint8_t ASK_PUSH[2]  = { SS_GPIO_BASE, SS_GPIO_BULK };
    switch (sk_phase) {
    case 0:  sk_ok = sk_write(ASK_DELTA, 2); sk_phase = 1; break;
    case 1:  sk_ok = sk_read4(b);
             if (sk_ok) { sk_detents += sknob_delta(b); sk_ok = sk_write(ASK_PUSH, 2); }
             sk_phase = 2; break;
    default: sk_ok = sk_read4(b);
             if (sk_ok) sk_push = sknob_push(b);
             sk_phase = 0; break;
    }
    if (!sk_ok) { sk_push = 0; sk_t_init = now; Serial.println("screen knob (0x36) silent - retrying"); }
}
static int sknob_take() { int d = sk_detents; sk_detents = 0; return d; }

static volatile uint8_t exp_int = 0;                     /* INT: an input changed */
static void exp_isr() { exp_int = 1; }
static uint32_t exp_last_read = 0, exp_last_init = 0;

/* Both expanders from a reset: the RESET line is shared, so U13 is set up
 * after every pulse - boot, a silent U12, the DRV8962's fault clear. */
static void exp_init_both() {
    if (!exp_reset_init(&exp_io)) Serial.println("TCA9539 U12 silent - mirrors off, retrying");
    if (!exp2_init(&exp_io2))     Serial.println("TCA9539 U13 silent - no wake request, retrying");
}

/* A STATUS line falling (BTS3011TE: latched over-temperature or a short).
 * Read and reported, not acted on - which seat tripped is not told apart, and
 * the dash stage clears itself with IN low each PWM period (confirm, S-487). */
static void status_edges(uint16_t was, uint16_t now_in) {
    uint16_t fell = (uint16_t)(was & ~now_in);
    if (fell & EXP2_SEAT_STATUS) Serial.println("seat switch STATUS low (U13 P00)");
    if (fell & EXP2_DASH_STATUS) Serial.println("dash-light stage STATUS low (U13 P03)");
}

/* Inputs on INT (wired-OR: both are read, which clears both) or every
 * EXP_POLL_MS. A silent U12 is reset with U13 every EXP_RETRY_MS (the DRV8962
 * sleeps on its pull-down meanwhile); a silent U13 alone is re-set-up without
 * a reset, so the mirrors are not put to sleep for it. */
static void exp_service(uint32_t now) {
    if (now - exp_last_init >= EXP_RETRY_MS) {
        if (!exp_io.ok) { exp_last_init = now; exp_init_both(); }
        else if (!exp_io2.ok) { exp_last_init = now; exp2_init(&exp_io2); }
    }
    if (exp_int || now - exp_last_read >= EXP_POLL_MS) {
        exp_int = 0; exp_last_read = now;
        uint16_t was = exp_io.in;
        if (exp_io.ok && tca_read_inputs(&exp_io) && ((was ^ exp_io.in) & EXP_PG_5V) && !(exp_io.in & EXP_PG_5V))
            Serial.println("logic buck power-good low");
        uint16_t was2 = exp_io2.in;
        if (exp_io2.ok && exp2_read_inputs(&exp_io2)) status_edges(was2, exp_io2.in);
    }
}

/* ---- outputs ---- */
static void all_outputs_off() {
    for (int i = 0; i < CMF_COUNT; i++) digitalWrite(PIN_COMFORT[i], LOW);
    for (int i = 0; i < 4; i++) digitalWrite(PIN_WIN[i], LOW);
    digitalWrite(PIN_REL_HATCH, LOW); digitalWrite(PIN_REL_FUEL, LOW);
    exp_write_outputs(&exp_io, 0);      /* DRV8962 asleep, every EN off, STB low */
    exp2_write_outputs(&exp_io2, 0);    /* the wake request off */
    drv.awake = 0;
    analogWrite(PIN_BLOWER, 0);
}

static void apply_outputs(uint32_t now) {
    uint8_t ok = comfort_permitted(&dcu);
    for (int i = 0; i < CMF_COUNT; i++)
        digitalWrite(PIN_COMFORT[i], (ok && dcu.comfort_on[i]) ? HIGH : LOW);
    analogWrite(PIN_BLOWER, (int)blower_duty_pct(dcu.mem.blower) * 255 / 100);
    analogWrite(PIN_DASH, dash_pwm(dcu.mem.dash_pct));       /* SN31; re-muxes the pin after a sleep */

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
    pinMode(PIN_DASH, INPUT);           /* the stage's IN left to its 10 kOhm pull-up: full, as
                                         * in a reset, and no PWM to clock at 24 MHz - O20 is off
                                         * with the PMU asleep, so the lamps are dark anyway */
    is31_reg(LED_PANEL_ADDR, IS3236_SHUTDOWN, 0x00);   /* both LED drivers into shutdown;
                                                         * re-initialised on the way back */
    is31_reg(LED_PLATE_ADDR, IS3218_SHUTDOWN, 0x00);
    lights.ok_panel = lights.ok_plate = 0;
    for (int i = 0; i < SRV_COUNT; i++) if (servo[i].attached()) servo[i].detach();
    memset(servo_seq.applied, 0, sizeof servo_seq.applied);   /* re-attach one at a time */
    enc_timer.end();
    detachInterrupt(digitalPinToInterrupt(PIN_EXP_INT));
    for (int r = 0; r < PANEL_ROWS; r++) { pinMode(PIN_ROW[r], OUTPUT); digitalWrite(PIN_ROW[r], LOW); }
    key_woke = 0;
    for (int c = 0; c < PANEL_COLS; c++) attachInterrupt(digitalPinToInterrupt(PIN_COL[c]), col_isr, FALLING);
    attachInterrupt(digitalPinToInterrupt(PIN_CENTRE_PUSH), col_isr, FALLING);   /* the knob's push wakes too */
    set_arm_clock(24000000);
    while (!key_woke && !ACAN_T4::can2.available()) asm volatile("wfi");
    set_arm_clock(600000000);
    for (int c = 0; c < PANEL_COLS; c++) detachInterrupt(digitalPinToInterrupt(PIN_COL[c]));
    detachInterrupt(digitalPinToInterrupt(PIN_CENTRE_PUSH));
    lights.t_init = millis() - LIGHTS_RETRY_MS;   /* the LED drivers re-initialised on the next loop */
    sk_ok = 0; sk_t_init = millis() - SKNOB_RETRY_MS;   /* the screen knob set up again at once */
    for (int r = 0; r < PANEL_ROWS; r++) pinMode(PIN_ROW[r], INPUT);
    enc_timer.begin(enc_isr, 1000);
    attachInterrupt(digitalPinToInterrupt(PIN_EXP_INT), exp_isr, FALLING);
    exp_int = 1;                        /* read the inputs at once */
    last_activity = millis();
}

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {}
    Serial.print("DCU — Teensy host, firmware "); Serial.println(DCU_FW_VERSION);

    /* every output off before anything else runs; the expander held in
     * reset, so its ports are inputs: nSLEEP and STB sit on their pull-downs
     * (DRV8962 asleep, CAN transceiver in normal mode) */
    pinMode(PIN_EXP_RESET, OUTPUT); exp_hal_reset(1);
    const int outs[] = { PIN_COMFORT[0], PIN_COMFORT[1], PIN_COMFORT[2], PIN_COMFORT[3], PIN_COMFORT[4],
                         PIN_WIN[0], PIN_WIN[1], PIN_WIN[2], PIN_WIN[3], PIN_REL_HATCH, PIN_REL_FUEL,
                         PIN_BLOWER };
    for (int p : outs) { pinMode(p, OUTPUT); digitalWrite(p, LOW); }
    analogWriteFrequency(PIN_BLOWER, 25000);
    analogWriteFrequency(PIN_DASH, DASH_PWM_HZ);   /* QuadTimer1 ch 2 - pin 10's ch 0 keeps 25 kHz */
    analogWrite(PIN_DASH, dash_pwm(DASH_PCT_MAX)); /* full until the memory is read, as in a reset */
    for (int k = 0; k < PANEL_ROWS; k++) pinMode(PIN_ROW[k], INPUT);
    for (int c = 0; c < PANEL_COLS; c++) pinMode(PIN_COL[c], INPUT_PULLUP);
    pinMode(PIN_JOY_PRESS, INPUT_PULLUP);
    pinMode(PIN_CENTRE_PUSH, INPUT_PULLUP);
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

    /* the expander: STB written low and held - before CAN2 starts (D-452) */
    Wire.begin();                       /* SDA 18 / SCL 19 */
    Wire.setClock(100000);              /* panel_ribbon 22: the bus runs out on about 1 m of
                                         * ribbon to the LED drivers and the screen - 100 kHz
                                         * (confirm on the bench); was 400 kHz, expander only */
    pinMode(PIN_EXP_INT, INPUT_PULLUP); /* open drain, pulled up on the carrier as well */
    exp_last_init = millis();
    exp_init_both();
    attachInterrupt(digitalPinToInterrupt(PIN_EXP_INT), exp_isr, FALLING);
    lights.t_init = millis();
    if (!lights_init_panel(&lights)) Serial.println("panel LED driver (0x3C) silent - retrying");
    if (!lights_init_plate(&lights)) Serial.println("plate LED driver (0x54) silent - retrying");
    sk_t_init = millis();
    sknob_setup();
    if (!sk_ok) Serial.println("screen knob (0x36) silent - retrying");

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
     * before the PMU can see the edge (D-370); only with the car stopped, and
     * never longer than RELEASE_HOLD_MS (D-465). A stale 0x200 is not stopped,
     * unless the PMU is up and says the key is OFF (D-484: a key-off release). */
    panel.stopped = car_stopped(seen_200, now - last_rx_200, speed_kph, dcu.pmu_alive, dcu.key_pos);
    uint16_t down, held;
    sknob_service(now);                                     /* the screen knob's push and detents (D-580) */
    uint16_t raw = (uint16_t)(scan_matrix() | (sk_push ? PK_SCREEN_PUSH : 0));
    uint16_t pressed = panel_keys_step(&panel, raw, dcu.pmu_alive, now, &down, &held);
    if (pressed) last_activity = now;
    int sk_d = sknob_take();
    if (sk_d) last_activity = now;
    sknob_step(&sknob, &dcu.mem.disp_pct, down, sk_d, now); /* pages, or the display level after a click */
    digitalWrite(PIN_REL_HATCH, panel.rel_sel == PK_HATCH     ? HIGH : LOW);
    digitalWrite(PIN_REL_FUEL,  panel.rel_sel == PK_FUEL_DOOR ? HIGH : LOW);
    exp2_write_outputs(&exp_io2, panel.wake_req ? EXP2_WAKE : 0);   /* SN21 on U13 P02 (D-577) */
    panel_keys_t pk;
    if (dcu.pmu_alive && panel_frame_due(&keys_tx, down, held, (int8_t)sknob.count, disp_level(&dcu.mem), now, &pk))
        send_frame(ID_PANEL_KEYS, &pk);

    /* knobs and climate keys: the centre knob's modes, the seat knobs (D-492);
     * its push held a second sets the dash-light level (D-578) */
    knob_hold(&knob, held, now);
    panel_apply(&dcu, &knob, pressed, enc_take(ENC_CENTRE),
                enc_take(ENC_SEAT_DRV), enc_take(ENC_SEAT_PASS), now);
    mirror_defog_step(&mdefog, &dcu, pressed, now);         /* its own key (D-492) */
    dcu.cabin_c = ntc_to_c((uint16_t)analogRead(PIN_CABIN_NTC));
    outside_c   = ntc_to_c((uint16_t)analogRead(PIN_OAT_NTC));

    /* the screen's content (no driver yet, P201) and the lights (D-458, D-492) */
    screen_build(&scr, &knob, &dcu.mem, outside_c);
    light_in.pmu_alive       = dcu.pmu_alive;
    light_in.key_pos         = dcu.key_pos;
    light_in.headlight       = headlight;
    light_in.rear_defog      = defog_on;
    light_in.mirror_defog    = mdefog.on;
    light_in.recirc          = dcu.mem.recirc;
    light_in.fan_mode_active = (uint8_t)(knob.mode == KNOB_MODE);
    light_in.seat_drv        = seat_pos(&dcu.mem, 0);
    light_in.seat_pass       = seat_pos(&dcu.mem, 2);
    light_in.wink_l = light_in.wink_r = 0;                  /* the PMU's A8 export, F-009 */
    light_in.dash_pct        = dcu.mem.dash_pct;            /* one level with the lamps (D-577) */
    lights_step(&light_in, &light_out);
    lights_write(&lights, &light_out, now);
    dcu.bus_current_ca = comfort_current_ca((uint16_t)analogRead(PIN_CURRENT), CURRENT_ZERO);

    /* windows (D-363) */
    uint8_t body = body_permitted(&dcu), up, dn;
    window_step(&win[0], (down & PK_WIN_DRV_UP) != 0,  (down & PK_WIN_DRV_DN) != 0,  body, now, &up, &dn);
    digitalWrite(PIN_WIN[0], up); digitalWrite(PIN_WIN[1], dn);
    window_step(&win[1], (down & PK_WIN_PASS_UP) != 0, (down & PK_WIN_PASS_DN) != 0, body, now, &up, &dn);
    digitalWrite(PIN_WIN[2], up); digitalWrite(PIN_WIN[3], dn);

    /* mirrors (D-359, D-360): the DRV8962 on the expander, one head at a time */
    uint8_t axis; int8_t dir; mirror_out_t mo;
    stick_read(&stick, (uint16_t)analogRead(PIN_JOY_X), (uint16_t)analogRead(PIN_JOY_Y), &axis, &dir);
    exp_service(now);
    uint8_t nfault = exp_io.ok && !(exp_io.in & EXP_MIR_NFAULT);
    if (drv_guard_step(&drv, nfault, body, axis == AXIS_NONE, now) == DRV_CLEAR) {
        Serial.println("DRV8962 fault - cleared through the expander reset");
        exp_last_init = now;
        exp_init_both();                /* the reset is U13's too: the wake request re-set-up */
    }
    uint8_t live = (uint8_t)(exp_io.ok && drv_live(&drv, now));
    mirror_step(&mirror, pressed, axis, dir, (uint8_t)(body && live), now, &mo);
    if (exp_io.ok) exp_write_outputs(&exp_io, exp_word(&mo, drv.awake, live));

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

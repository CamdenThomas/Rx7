/*
 * icu.ino — Teensy 4.1 host for the ICU cluster
 *
 * Includes the SAME cluster_core.h that the desktop simulator uses.
 * Nothing in the renderer changes between the two. Only this file differs.
 *
 * DISPLAY (D-193): 1280x480 RGB332 through a BT817 EVE bridge — see
 * bt817.h. The BT817 scans its own RAM_G out to the panel; each frame we
 * push only the dirty tiles. If the BT817 never answers on SPI (not wired
 * yet), the sketch keeps running headless and reports timing over serial.
 *
 * MEMORY: the 1280x480 framebuffer is 614,400 B — bigger than any single
 * on-chip RAM bank, so it lives in EXTMEM (the two PSRAM chips soldered to
 * the Teensy 4.1 underside pads). WITHOUT PSRAM THE SKETCH HALTS AT BOOT
 * with a serial message. Solder the chips before flashing for real use.
 * EXTMEM is not zero-initialised at startup; setup() clears it.
 *
 * THE LOG AND THE LINK (D-493, D-494, BT3): the card in the Teensy's own slot holds
 * one folder per drive (log_store.h) - a drive is key-on to key-off, so it starts at
 * boot. Serial2 (RX 7, TX 8, D-377) at 921600 carries both the C3's $BAT lines
 * (radio_link.h) and the log link's frames (log_link.h); one decoder takes both. With
 * no card the cluster runs as before and the link answers ERR 3 - never a hang.
 * Until CAN is wired (F14) the log is fed the frames the ICU will send, built from
 * VehicleState, and the battery frames from the radio; log_can_frame() is the one
 * call the CAN receive and transmit paths make when they exist.
 */

/* Bump on every change that alters behaviour; log it in bringup_log and tag the
 * commit. Printed over serial at boot. ICU_FW_NUM is the same version for the link's
 * INFO record (LL03): major*10000 + minor*100 + patch. */
#define ICU_FW_VERSION "0.6.0-dev"   /* the log link: the card's three logs, Serial2 at 921600, the file side of log_link (BT3) */
#define ICU_FW_NUM     600

#include <SD.h>
#include "cluster_core.h"
#include "stats.h"
#include "bt817.h"
#include "radio_link.h"
#include "log_link.h"
#include "log_store.h"

EXTMEM Framebuffer fb;          /* 614 KB — PSRAM only */
Cluster      cluster;
VehicleState state;
Bt817        display;
StatsTracker tracker;

extern "C" uint8_t external_psram_size;   /* MB detected at startup, 0 = none */

uint32_t pushDirtyTiles() {
    return display.pushDirty(fb, TILE, TILES_X, TILES_Y, SCR_W);
}

/* ================= F-007 hooks - the persisted odometer and drive sequence =========
 * F-007 (Teensy EEPROM, wear-levelled, every 0.1 mi) is open. Until it lands both live
 * in RAM: the odometer starts at 0 each boot and the sequence is recovered from the
 * folders on the card (LogStore::begin), so no drive is ever overwritten. */
static uint32_t g_odo_base = 0;
static uint32_t odo_load()             { return 0; }   /* F-007 */
static uint32_t seq_load()             { return 0; }   /* F-007 */
static void     seq_save(uint32_t seq) { (void)seq; }  /* F-007: persist beside the odometer */
static uint32_t odo_x10()              { return g_odo_base + tracker.trip.distanceX10; }

/* ================= the card: LogFs over the Teensy SD library (SdFat) ================= */
class SdLogFs : public LogFs {
public:
    bool ok = false;
    bool present() override { return ok; }
    bool mkdir(const char *p) override { return SD.exists(p) || SD.mkdir(p); }
    bool exists(const char *p) override { return SD.exists(p); }
    bool remove(const char *p) override { return SD.remove(p); }
    int open(const char *p, int mode) override {
        int h = -1;
        for (int i = 0; i < N; i++) if (!used[i]) { h = i; break; }
        if (h < 0) return -1;
        if (mode == CREATE && SD.exists(p)) SD.remove(p);
        f[h] = SD.open(p, mode == RD ? FILE_READ : FILE_WRITE_BEGIN);
        if (!f[h]) return -1;
        used[h] = true;
        return h;
    }
    bool seek(int h, uint32_t pos) override { return valid(h) && f[h].seek(pos); }
    int32_t read(int h, void *b, uint32_t n) override { return valid(h) ? (int32_t)f[h].read(b, n) : -1; }
    int32_t write(int h, const void *b, uint32_t n) override { return valid(h) ? (int32_t)f[h].write((const uint8_t *)b, n) : -1; }
    int32_t size(int h) override { return valid(h) ? (int32_t)f[h].size() : -1; }
    bool flush(int h) override { if (!valid(h)) return false; f[h].flush(); return true; }
    void close(int h) override { if (valid(h)) { f[h].close(); used[h] = false; } }
    bool list(const char *dir, void (*cb)(const char *, bool, void *), void *ctx) override {
        File d = SD.open(dir);
        if (!d) return false;
        for (File e = d.openNextFile(); e; e = d.openNextFile()) { cb(e.name(), e.isDirectory(), ctx); e.close(); }
        d.close();
        return true;
    }
    uint8_t free_pct() override {        /* slow on a big FAT card: the store asks rarely */
        uint64_t t = SD.totalSize();
        return t ? (uint8_t)(100 - (SD.usedSize() * 100) / t) : 0;
    }
private:
    static const int N = 6;              /* three tiers open, a transfer, pulled.flg, mark */
    File f[N];
    bool used[N] = {};
    bool valid(int h) const { return h >= 0 && h < N && used[h]; }
};

/* ================= the link's two ends on this side ================= */
class Serial2Out : public LogOut {
public:
    size_t room() override { return (size_t)Serial2.availableForWrite(); }
    void write(const uint8_t *p, size_t n) override { Serial2.write(p, n); }
};

/* The RTC is "set" only once SET_TIME has set it and it has kept running since: the
 * mark lives in SNVS_LPGPR0, which loses power with the RTC (no coin cell yet, P202).
 * The floor catches the 2019-01-01 the core starts an unpowered RTC at. */
static const uint32_t RTC_SET_MAGIC = 0x52583754u;   /* "RX7T" */
static const uint32_t RTC_FLOOR     = 1700000000u;   /* 2023-11 */
static uint8_t  g_pair_state = LL_PAIR_CLOSED;
static uint32_t g_passkey = 0;

class IcuHost : public LogHost {
public:
    uint32_t odometer_x10() override { return odo_x10(); }
    uint16_t fw() override { return ICU_FW_NUM; }
    bool rtc_is_set() override { return SNVS_LPGPR0 == RTC_SET_MAGIC && rtc_get() >= RTC_FLOOR; }
    uint32_t rtc_unix() override { return rtc_get(); }
    void rtc_set(uint32_t t) override { ::rtc_set(t); SNVS_LPGPR0 = RTC_SET_MAGIC; }   /* the one state write (D-493) */
    void on_pairing(uint8_t s, uint32_t key, uint8_t secs) override {
        g_pair_state = s; g_passkey = key;
        /* the cluster's pairing screen is not drawn yet - the key goes to USB serial */
        if (s == LL_PAIR_OPEN) { Serial.printf("PAIRING: key %06lu, %u s left\n", (unsigned long)key, secs); }
        else Serial.printf("PAIRING: %s\n", s == LL_PAIR_BONDED ? "phone bonded" : s == LL_PAIR_FAILED ? "failed" : "closed");
    }
};

SdLogFs      card;
LogStore     store;
LogServer    server;
LogThinAccum thin;
Serial2Out   uart;
IcuHost      host;
ll_rx_t      rx;
radio_bat_t  g_bat;
uint32_t     g_bat_ms = 0;
bool         g_have_bat = false;

static uint8_t s2_tx[4096];   /* a whole credit window of DATA queues without blocking */
static uint8_t s2_rx[1024];

/* Every CAN frame the ICU sees or sends goes here: the thinned log's means and states,
 * and a 15-byte record in the full log. */
static void log_can_frame(uint32_t id, bool ext, const uint8_t *d, uint8_t len, uint32_t now) {
    thin.on_frame(id, ext, d, len, now);
    log_full_t r;
    r.ms = now; r.id = (uint16_t)id;
    r.flags = (uint8_t)((ext ? LOG_FULL_EXT : 0) | (id > 0xFFFFu ? LOG_FULL_WIDE : 0) | ((len & 15) << 4));
    memset(r.data, 0, 8);
    memcpy(r.data, d, len > 8 ? 8 : len);
    store.add_frame(r);
}

static void log_imu(int16_t lat, int16_t lon, int16_t vert, uint32_t now) {
    thin.on_imu(lat, lon, vert);
    log_full_t r = { now, 0, LOG_FULL_IMU, {} };
    memcpy(r.data, &lat, 2); memcpy(r.data + 2, &lon, 2); memcpy(r.data + 4, &vert, 2);
    store.add_frame(r);
}

static log_summary_t build_summary(uint32_t now) {
    const Stats &a = tracker.trip;
    log_summary_t s;
    memset(&s, 0, sizeof s);
    s.end_odo = odo_x10();
    s.duration_s = now / 1000;
    s.max_rpm = a.maxRpm; s.max_mph = a.maxSpeed;
    s.max_water_c = a.maxWaterC; s.max_oil_temp_c = a.maxOilTempC;
    s.max_oil_cbar = a.maxOilPress; s.min_oil_cbar = a.minOilPress;
    s.max_volts_x10 = a.maxVoltsX10; s.min_volts_x10 = a.minVoltsX10;
    s.max_lat_g = a.maxLatG; s.max_accel_g = a.maxAccelG; s.max_brake_g = a.maxBrakeG;
    s.max_pitch_up = a.maxPitchUp; s.max_pitch_down = a.maxPitchDown;
    s.runtime_s = a.runtimeSec; s.idle_s = a.idleSec; s.distance_x10 = a.distanceX10;
    s.rev_s = a.revSeconds; s.hot_s = a.hotSeconds; s.low_oil_s = a.lowOilSeconds;
    s.cold_starts = a.coldStarts; s.fuel_pct_start = a.fuelPctStart; s.fuel_pct_now = a.fuelPctNow;
    s.dist_at_fuel_mark = a.distAtFuelMark; s.fuse_trips = a.softFuseTrips;
    s.last_trip_ch = a.lastTripCh; s.last_trip_s = a.lastTripSec;
    s.sensor_faults = a.sensorFaults; s.can_timeouts = a.canTimeouts;
    return s;
}

/* Long press of the page button (LL02) - the button is not wired yet, so the bench
 * opens pairing from the USB console: 'p' pairs for 60 s, 'u' forgets every phone. */
static void link_pair(uint8_t window_s) {
    ll_pair_t p = { window_s };
    uint8_t f[16]; size_t n = ll_encode(f, sizeof f, LL_PAIR, &p, sizeof p);
    Serial2.write(f, n);
}
static void link_unbond() {
    uint8_t f[16]; size_t n = ll_encode(f, sizeof f, LL_UNBOND, nullptr, 0);
    Serial2.write(f, n);
}

/* Everything from the C3: $BAT lines and link frames, one byte at a time. */
static void link_rx(uint32_t now) {
    int budget = 512;
    while (Serial2.available() && budget--) {
        int r = ll_rx_feed(&rx, (uint8_t)Serial2.read());
        if (r == LL_RX_FRAME) server.on_frame(ll_rx_type(&rx), ll_rx_payload(&rx), ll_rx_plen(&rx), now);
        else if (r == LL_RX_LINE) {
            radio_bat_t b;
            if (radio_parse_bat(rx.line, strlen(rx.line), &b)) { g_bat = b; g_bat_ms = now; g_have_bat = true; }
        }
    }
}

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {}

    Serial.print("ICU cluster — Teensy host, firmware ");
    Serial.println(ICU_FW_VERSION);

    if (external_psram_size == 0) {
        while (true) {
            Serial.println("FATAL: no PSRAM detected — framebuffer needs the two");
            Serial.println("       soldered PSRAM chips (D-170). Halting.");
            delay(2000);
        }
    }
    Serial.print("PSRAM: "); Serial.print(external_psram_size); Serial.println(" MB");
    memset(&fb, 0, sizeof(fb));             /* EXTMEM is not auto-cleared */

    Serial.print("framebuffer bytes: ");
    Serial.println((uint32_t)sizeof(fb.buf));

    if (display.init(SCR_W, SCR_H))
        Serial.println("BT817: up, scanout running");
    else
        Serial.println("BT817: no answer on SPI — running headless");

    /* the radio link (D-493: 921600) and the card */
    Serial2.addMemoryForWrite(s2_tx, sizeof s2_tx);
    Serial2.addMemoryForRead(s2_rx, sizeof s2_rx);
    Serial2.begin(LL_BAUD);
    ll_rx_init(&rx);
    g_odo_base = odo_load();
    tracker.begin(millis());
    card.ok = SD.begin(BUILTIN_SDCARD);
    store.save_seq = seq_save;
    if (store.begin(&card, seq_load()) &&
        store.start_drive(millis(), odo_x10(), host.rtc_is_set() ? host.rtc_unix() : 0)) {
        Serial.printf("card: drive %lu, %u%% free\n", (unsigned long)store.seq, store.free_pct);
        store.write_summary(build_summary(millis()));
    } else {
        Serial.println("card: none - nothing is logged, the link answers err 3");
    }
    server.begin(&store, &uart, &host);

    cluster.layout();

    uint32_t t0 = micros();
    cluster.drawStatic(fb, true);
    uint32_t t1 = micros();
    uint32_t sent = pushDirtyTiles();
    uint32_t t2 = micros();

    Serial.print("static compose: "); Serial.print(t1 - t0); Serial.println(" us");
    Serial.print("static push:    "); Serial.print(t2 - t1); Serial.println(" us");
    Serial.print("static pixels:  "); Serial.println(sent);

    state.rpm = 900;  state.speed = 0;   state.waterC = 88;
    state.oilPressCbar = 450;            state.oilTempC = 95;
    state.fuelPct = 72;                  state.voltsX10 = 142;
}

void loop() {
    uint32_t now = millis();

    /* --- the link and the card: every pass, never blocking --- */
    link_rx(now);
    server.poll(now);
    store.tick(now);

    while (Serial.available()) {             /* bench console (USB), not the link */
        char c = (char)Serial.read();
        if (c == 'p') link_pair(LL_PAIR_WINDOW_S);
        if (c == 'u') link_unbond();
    }

    /* --- the log's inputs --- */
    static uint32_t t20 = 0, t50 = 0, tBat = 0, tSec = 0, tSum = 0;
    static uint8_t ctr = 0;
    if (now - t50 >= 20) {                   /* the IMU at 50 Hz (D-493) */
        t50 = now;
        log_imu((int16_t)state.latGx100, (int16_t)state.lonGx100, 0, now);
    }
    if (now - t20 >= 50) {                   /* 0x200 as the ICU will send it, 20 Hz */
        t20 = now;
        icu_sensors_t f = { (uint16_t)state.rpm, (int8_t)state.waterC, (int8_t)state.oilTempC,
                            (uint16_t)state.oilPressCbar, (uint8_t)((state.speed * 1609) / 1000), ctr++ };
        log_can_frame(ID_ICU_SENSORS, false, (const uint8_t *)&f, 8, now);
    }
    if (now - tBat >= 500) {                 /* 0x220 / 0x221 from the radio, 2 Hz */
        tBat = now;
        icu_batt_t a; icu_cells_t c;
        radio_build_frames(g_have_bat ? &g_bat : nullptr, now - g_bat_ms, &a, &c);
        a.counter = c.counter = ctr;
        log_can_frame(ID_ICU_BATT, false, (const uint8_t *)&a, 8, now);
        log_can_frame(ID_ICU_CELLS, false, (const uint8_t *)&c, 8, now);
    }
    if (now - tSec >= 1000) {                /* the thinned record, once a second */
        tSec += 1000;
        if (now - tSec >= 1000) tSec = now;
        tracker.tick(state, now);
        log_thin_t r;
        thin.finish(now, odo_x10(), 0 /* IC14 not read yet */, (uint8_t)cluster.page, &r);
        store.add_second(r);
    }
    if (now - tSum >= LOG_SUMMARY_MS) {      /* the summary, every minute */
        tSum = now;
        store.write_summary(build_summary(now));
    }

    /* --- the frame, at 30 Hz --- */
    static uint32_t tFrame = 0;
    if (now - tFrame < 33) return;
    tFrame = now;

    /* --- until CAN and sensors are wired, sweep for timing --- */
    static int rpm = 900, dir = 1;
    rpm += dir * 130;
    if (rpm > 8400) dir = -1;
    if (rpm < 800)  dir = 1;
    state.rpm = rpm;
    state.speed = rpm / 62;

    fb.clearDirty();
    uint32_t t0 = micros();
    cluster.update(fb, state);
    uint32_t t1 = micros();
    uint32_t sent = pushDirtyTiles();
    uint32_t t2 = micros();

    static uint32_t n = 0, sumC = 0, sumP = 0, worst = 0, worstPx = 0;
    sumC += (t1 - t0);
    sumP += (t2 - t1);
    if ((t2 - t0) > worst) { worst = t2 - t0; worstPx = sent; }
    n++;

    if (n >= 100) {
        Serial.print("compose avg "); Serial.print(sumC / n);
        Serial.print(" us   push avg "); Serial.print(sumP / n);
        Serial.print(" us   worst frame "); Serial.print(worst);
        Serial.print(" us ("); Serial.print(worstPx); Serial.println(" px)");
        Serial.printf("link: %lu frames in, %lu out, %lu bad crc   card: %s, drive %lu\n",
                      (unsigned long)server.frames_in, (unsigned long)server.frames_out,
                      (unsigned long)rx.bad_crc, store.card ? "ok" : "none", (unsigned long)store.seq);
        n = 0; sumC = 0; sumP = 0; worst = 0;
    }
}

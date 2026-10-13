/*
 * log_store.h — the ICU's card: three logs per drive, and the file side of the log
 * link (D-493, D-494, D-478, D-483; work BT3, B7, F-007)
 *
 * IMPLEMENTS (R6): the record's table `log_channels` (the thinned record, LC01-LC53,
 * 137 bytes, in log_thin_t below, field for field and in order) and the Teensy's side
 * of `log_link` (LL03, LL04, LL06-LL08, LL12-LL14: listing, transfers, ACK, SET_TIME,
 * INFO). The framing itself is log_link.h's. params log_thin_bytes_per_s (137) is
 * sizeof(log_thin_t). 00-design/firmware/tests/gen_log_vectors.py reads log_channels.csv and
 * 00-design/firmware/tests/test_loglink.cpp holds this header to it.
 *
 * Portable C++, no Arduino headers. The card is reached only through LogFs, which
 * icu.ino binds to the Teensy SD library (SdFat) and the tests bind to memory.
 *
 * ON THE CARD (D-493)
 *     /RX7/<seq>/summary.bin   the drive's summary, rewritten in place every minute
 *     /RX7/<seq>/thin.bin      one 137-byte record a second (log_channels)
 *     /RX7/<seq>/full.bin      every CAN frame (and the IMU at 50 Hz), 15 bytes each
 *     /RX7/<seq>/pulled.flg    what the app has acknowledged (below)
 *     /RX7/mark.bin            u32: every drive below this seq has summary and thin pulled
 *   <seq> is eight decimal digits, zero-padded ("00000042"), so the folders sort and stay
 *   8.3 names. The three tier files start with the 32-byte header (log_header_t, the
 *   fields in D-493's order); pulled.flg is the ICU's own and is never transferred.
 *   Records are flushed every second (B7's power-loss test proves the file whole to the
 *   last flushed second). Summaries and thinned logs are never deleted; a full log is
 *   deleted oldest first only while the card is more than three-quarters full.
 *
 * PULLED (LL08, D-478). pulled.flg holds, per tier, the length and CRC32 the app
 * acknowledged. A tier is pulled when that length is the file's length now: the thinned
 * and full logs only grow, so the open drive's tiers fall back to "not pulled" as soon as
 * a record is added, and a summary rewritten in place clears its own entry. Nothing is
 * ever deleted on the app's word.
 *
 * THE DRIVE SEQUENCE is persisted beside the odometer (F-007, D-493): LogStore calls
 * save_seq() at every drive start, and begin() takes what was saved. F-007 is open:
 * icu.ino's hook keeps it in RAM only, and begin() also takes the highest folder on the
 * card, so a lost sequence never overwrites a drive.
 */
#ifndef LOG_STORE_H
#define LOG_STORE_H

#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include "can_map.h"
#include "log_link.h"

#define LOG_FORMAT_VERSION    1
#define LOG_HEADER_LEN        32
#define LOG_CHANNELS          53        /* log_channels rows                       */
#define LOG_THIN_LEN          137       /* params log_thin_bytes_per_s             */
#define LOG_FULL_LEN          15        /* D-493: uptime ms, id, flags, 8 data     */
#define LOG_FLUSH_MS          1000u     /* D-493: flushed every second             */
#define LOG_SUMMARY_MS        60000u    /* D-493: the summary every minute         */
#define LOG_KEEP_FREE_PCT     25        /* D-493: full logs kept until 3/4 full    */
#define LOG_FULL_BUF          4096      /* RAM ahead of full.bin, ~1.3 s of frames */
#define LOG_PATH_MAX          40
#define LOG_ROOT              "/RX7"

/* ---------------- the file header (D-493), 32 bytes ---------------- */
typedef struct __attribute__((packed)) {
    char     magic[4];       /* "RX7L"                                        */
    uint8_t  version;        /* LOG_FORMAT_VERSION                            */
    uint8_t  tier;           /* LL_TIER_*                                     */
    uint32_t seq;
    uint32_t start_odo;      /* 0.1 mi                                        */
    uint32_t uptime_start;   /* ms since the ICU booted                       */
    uint32_t unix_start;     /* 0 when the RTC was unset                      */
    uint16_t record_len;     /* 137 thin, 15 full, sizeof(log_summary_t)      */
    uint32_t layout_crc;     /* CRC32 of the tier's layout string (below)     */
    uint8_t  _rsv[4];
} log_header_t;

/* ---------------- the thinned record: log_channels, LC01-LC53 ---------------- */
typedef struct __attribute__((packed)) {
    uint32_t time_ms;        /* LC01 ICU uptime                               */
    uint32_t odo_x10;        /* LC02 F-007, 0.1 mi                            */
    uint8_t  key_pos;        /* LC03 0x100/0                                  */
    uint8_t  wake;           /* LC04 0x100/1                                  */
    uint8_t  fault;          /* LC05 0x100/2                                  */
    uint8_t  headlight;      /* LC06 0x100/3                                  */
    uint8_t  turn;           /* LC07 0x100/4                                  */
    uint8_t  popup;          /* LC08 0x100/5                                  */
    uint8_t  input_fault;    /* LC09 0x100/6                                  */
    uint16_t batt_mv;        /* LC10 0x110/0-1, 1 s mean                      */
    uint16_t total_ca;       /* LC11 0x110/2-3, 0.1 A, 1 s mean               */
    uint8_t  charging;       /* LC12 0x110/4                                  */
    uint8_t  outputs[3];     /* LC13 0x120/2-4                                */
    uint8_t  trip_index;     /* LC14 0x120/5 · 0x120/6                        */
    uint8_t  trip_status;
    uint16_t ch_ca[22];      /* LC15 0x130, O1-O22, 0.01 A, last seen         */
    uint16_t lambda;         /* LC16 0x180 ext/0-1, 0.0001 λ, 1 s mean        */
    uint8_t  wb_flags;       /* LC17 0x180 ext/6                              */
    uint16_t rpm;            /* LC18 0x200/0-1, 1 s mean                      */
    uint16_t rpm_peak;       /* LC19 the highest 20 Hz sample in the second   */
    int8_t   water_c;        /* LC20 0x200/2                                  */
    int8_t   oil_temp_c;     /* LC21 0x200/3                                  */
    uint16_t oil_cbar;       /* LC22 0x200/4-5, 0.01 bar, 1 s mean            */
    uint8_t  speed_kph;      /* LC23 0x200/6, 1 s mean                        */
    uint8_t  sensor_valid;   /* LC24 0x210/0                                  */
    uint8_t  sensor_fault;   /* LC25 0x210/1                                  */
    uint8_t  can_health;     /* LC26 0x210/2                                  */
    uint8_t  telltales;      /* LC27 0x210/3                                  */
    uint16_t fuel_x10;       /* LC28 0x218/0-1, 0.1 %, 1 s mean               */
    uint8_t  fuel_valid;     /* LC29 0x218/2                                  */
    uint16_t pack_mv;        /* LC30 0x220/0-1                                */
    uint16_t cell_mv[4];     /* LC31 0x220/2-5 · 0x221/0-3                    */
    uint16_t spread_mv;      /* LC32 0x221/4-5                                */
    uint8_t  batt_flags;     /* LC33 0x220/6                                  */
    int16_t  batt_da;        /* LC34 0x222/0-1, 0.1 A - 0 until D-330 gives it */
    uint8_t  soc;            /* LC35 0x222/2                                  */
    int8_t   batt_c;         /* LC36 0x222/3                                  */
    uint8_t  clim_mode;      /* LC37 0x300/0                                  */
    uint8_t  blower;         /* LC38 0x300/1                                  */
    uint8_t  target_c;       /* LC39 0x300/2                                  */
    int8_t   cabin_c;        /* LC40 0x300/3                                  */
    uint8_t  ac_request;     /* LC41 0x300/4                                  */
    int8_t   outside_c;      /* LC42 0x300/5                                  */
    uint8_t  seat_heat;      /* LC43 0x310/0                                  */
    uint8_t  seat_cool;      /* LC44 0x310/1                                  */
    uint8_t  mirror_heat;    /* LC45 0x310/2                                  */
    uint16_t comfort_ca;     /* LC46 0x310/4-5, 0.01 A, 1 s mean              */
    uint8_t  radar[3];       /* LC47 0x320/0-2, the highest alert in the second */
    uint16_t keys_down;      /* LC48 0x400/0-1, OR of the second              */
    uint16_t keys_held;      /* LC49 0x400/2-3, OR of the second              */
    int16_t  acc_mean[3];    /* LC50 IC23, 0.01 g lateral, longitudinal, vertical */
    int16_t  acc_peak[3];    /* LC51 IC23, 0.01 g peak lateral, acceleration, braking */
    uint8_t  illum_pct;      /* LC52 IC14                                     */
    uint8_t  page;           /* LC53 IC22                                     */
} log_thin_t;

/* log_channels.bytes, LC01..LC53 in order: the thinned record's layout as the record
 * gives it. Its CRC32, as the string "LC01:4;LC02:4;...;LC53:1;", is the thin header's
 * layout_crc - the app refuses a file whose CRC it does not know (D-493). */
static const uint8_t LOG_CH_BYTES[LOG_CHANNELS] = {
    4, 4, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 3, 2, 44, 2, 1, 2, 2, 1, 1, 2, 1, 1, 1, 1, 1,
    2, 1, 2, 8, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 2, 2, 6, 6, 1, 1 };

/* ---------------- the full log record, 15 bytes ---------------- */
#define LOG_FULL_EXT    0x01    /* flags b0: a 29-bit extended id                  */
#define LOG_FULL_WIDE   0x02    /* flags b1: the id was wider than 16 bits (cut)    */
#define LOG_FULL_IMU    0x04    /* flags b2: an IMU sample, not a frame (id 0)      */
#define LOG_FULL_DLC(f) ((f) >> 4)
typedef struct __attribute__((packed)) {
    uint32_t ms;            /* ICU uptime                                        */
    uint16_t id;            /* the id's low 16 bits: every id on this bus fits,
                               0x180 ext is 0x00000180 (can_messages)             */
    uint8_t  flags;         /* LOG_FULL_*, b4-7 the DLC                          */
    uint8_t  data[8];       /* as received; an IMU sample is int16 lat, lon, vert, 0 */
} log_full_t;

/* ---------------- the summary (D-493), rewritten every minute ---------------- */
typedef struct __attribute__((packed)) {
    uint32_t seq, start_odo, end_odo, duration_s, unix_start, uptime_start;
    uint32_t time_set_unix;     /* the last SET_TIME applied in this drive, 0 none */
    uint32_t time_set_uptime;   /* ms, when                                        */
    uint32_t time_set_prev;     /* the RTC before it, 0 = it was unset (LL08)      */
    /* stats.h's trip figures (D-163) */
    uint16_t max_rpm, max_mph;
    int16_t  max_water_c, max_oil_temp_c;
    uint16_t max_oil_cbar, min_oil_cbar, max_volts_x10, min_volts_x10;
    uint16_t max_lat_g, max_accel_g, max_brake_g;
    int16_t  max_pitch_up, max_pitch_down;
    uint32_t runtime_s, idle_s, distance_x10, rev_s, hot_s, low_oil_s;
    uint16_t cold_starts;
    uint8_t  fuel_pct_start, fuel_pct_now;
    uint32_t dist_at_fuel_mark;
    uint16_t fuse_trips;
    uint8_t  last_trip_ch;
    uint32_t last_trip_s;
    uint16_t sensor_faults, can_timeouts;
} log_summary_t;

#define LOG_SUMMARY_LAYOUT \
    "seq,start_odo,end_odo,duration_s,unix_start,uptime_start,time_set_unix,time_set_uptime," \
    "time_set_prev:u32;max_rpm,max_mph:u16;max_water_c,max_oil_temp_c:i16;max_oil_cbar," \
    "min_oil_cbar,max_volts_x10,min_volts_x10,max_lat_g,max_accel_g,max_brake_g:u16;" \
    "max_pitch_up,max_pitch_down:i16;runtime_s,idle_s,distance_x10,rev_s,hot_s,low_oil_s:u32;" \
    "cold_starts:u16;fuel_pct_start,fuel_pct_now:u8;dist_at_fuel_mark:u32;fuse_trips:u16;" \
    "last_trip_ch:u8;last_trip_s:u32;sensor_faults,can_timeouts:u16;"
#define LOG_FULL_LAYOUT "ms:u32;id:u16;flags:u8;data:u8x8;"

/* pulled.flg - the ICU's own, never transferred */
typedef struct __attribute__((packed)) {
    char magic[4];                              /* "RX7P"                         */
    struct __attribute__((packed)) { uint32_t len, crc; } t[LL_TIERS];
} log_pulled_t;

static_assert(sizeof(log_header_t) == LOG_HEADER_LEN, "the header is 32 bytes (D-493)");
static_assert(sizeof(log_thin_t) == LOG_THIN_LEN, "the thinned record is 137 bytes (log_channels)");
static_assert(sizeof(log_full_t) == LOG_FULL_LEN, "the full-log record is 15 bytes (D-493)");
static_assert(sizeof(log_pulled_t) == 28, "pulled.flg");

static inline uint32_t log_thin_layout_crc(void)
{
    uint32_t c = LL_CRC32_INIT;
    char s[16];
    for (int i = 0; i < LOG_CHANNELS; i++) {
        int n = snprintf(s, sizeof s, "LC%02d:%u;", i + 1, (unsigned)LOG_CH_BYTES[i]);
        c = ll_crc32_update(c, s, (size_t)n);
    }
    return ll_crc32_final(c);
}

static inline uint32_t log_layout_crc(uint8_t tier)
{
    if (tier == LL_TIER_THIN) return log_thin_layout_crc();
    const char *s = tier == LL_TIER_SUMMARY ? LOG_SUMMARY_LAYOUT : LOG_FULL_LAYOUT;
    return ll_crc32(s, strlen(s));
}

static inline uint16_t log_record_len(uint8_t tier)
{
    return tier == LL_TIER_SUMMARY ? (uint16_t)sizeof(log_summary_t)
         : tier == LL_TIER_THIN    ? (uint16_t)LOG_THIN_LEN : (uint16_t)LOG_FULL_LEN;
}

static const char *const LOG_TIER_FILE[LL_TIERS] = { "summary.bin", "thin.bin", "full.bin" };

/* ======================================================================
 * LogFs - the card, as little of it as the store needs
 * ====================================================================== */
class LogFs {
public:
    enum { RD = 0, RW = 1, CREATE = 2 };   /* CREATE: a new, empty file, read-write */
    virtual ~LogFs() {}
    virtual bool    present() = 0;
    virtual bool    mkdir(const char *path) = 0;            /* true if it exists after */
    virtual bool    exists(const char *path) = 0;
    virtual bool    remove(const char *path) = 0;
    virtual int     open(const char *path, int mode) = 0;  /* a handle >= 0, or -1   */
    virtual bool    seek(int h, uint32_t pos) = 0;
    virtual int32_t read(int h, void *buf, uint32_t n) = 0;  /* bytes read, -1 error */
    virtual int32_t write(int h, const void *buf, uint32_t n) = 0;
    virtual int32_t size(int h) = 0;
    virtual bool    flush(int h) = 0;
    virtual void    close(int h) = 0;
    /* the names in a directory; cb is called once per entry */
    virtual bool    list(const char *dir, void (*cb)(const char *name, bool is_dir, void *ctx), void *ctx) = 0;
    /* free space in %. May be slow on a large FAT card: the store calls it at begin
     * and at each drive start only, and keeps the answer */
    virtual uint8_t free_pct() = 0;
};

static inline void log_path(char *buf, uint32_t seq, const char *file)
{
    if (file) snprintf(buf, LOG_PATH_MAX, LOG_ROOT "/%08lu/%s", (unsigned long)seq, file);
    else      snprintf(buf, LOG_PATH_MAX, LOG_ROOT "/%08lu", (unsigned long)seq);
}

/* "00000042" -> 42; anything that is not eight digits -> 0 */
static inline uint32_t log_parse_seq(const char *name)
{
    uint32_t v = 0;
    for (int i = 0; i < 8; i++) {
        if (name[i] < '0' || name[i] > '9') return 0;
        v = v * 10u + (uint32_t)(name[i] - '0');
    }
    return name[8] == 0 ? v : 0;
}

/* ======================================================================
 * LogThinAccum - one second of CAN frames and IMU samples into one log_thin_t
 * (log_channels: means for the analog channels, the peak RPM beside the mean, the
 * latest for states and bitfields, the per-channel currents as last seen, ORs for the
 * keys, the highest radar alert).
 *
 * A message that has not arrived for max(its timeout, 1 s) is blank in the record -
 * 0, or TEMP_INVALID for a temperature - never a held value (D-153); a mean with no
 * sample in the second is 0. The radar is on change and is held. LC34-LC36 stay 0
 * until 0x222 has a source (D-330, D-345).
 * ====================================================================== */
class LogThinAccum {
public:
    enum { M100, M110, M120, M130, M180, M200, M210, M218, M220, M221, M222, M300, M310, M320, M400, MCOUNT };

    LogThinAccum() { reset_all(); }

    void reset_all() {
        memset(&held, 0, sizeof held);
        for (int i = 0; i < MCOUNT; i++) seen_ms[i] = 0, ever[i] = false;
        held.water_c = held.oil_temp_c = held.cabin_c = held.outside_c = TEMP_INVALID;
        clear_second();
    }

    /* every frame the ICU sees, sent or received */
    void on_frame(uint32_t id, bool ext, const uint8_t *d, uint8_t len, uint32_t now_ms) {
        if (len < 8) return;
        int m = -1;
        if (ext) { if (id == 0x180) m = M180; }
        else switch (id) {
            case ID_PMU_STATE:   m = M100; break;
            case ID_PMU_POWER:   m = M110; break;
            case ID_PMU_OUTPUTS: m = M120; break;
            case ID_PMU_CHANNEL: m = M130; break;
            case ID_ICU_SENSORS: m = M200; break;
            case ID_ICU_HEALTH:  m = M210; break;
            case ID_ICU_BODY:    m = M218; break;
            case ID_ICU_BATT:    m = M220; break;
            case ID_ICU_CELLS:   m = M221; break;
            case ID_ICU_BATT_EXT:m = M222; break;
            case ID_DCU_CLIMATE: m = M300; break;
            case ID_DCU_COMFORT: m = M310; break;
            case ID_DCU_RADAR:   m = M320; break;
            case ID_PANEL_KEYS:  m = M400; break;
        }
        if (m < 0) return;
        seen_ms[m] = now_ms; ever[m] = true;
        switch (m) {
        case M100: memcpy(&held.key_pos, d, 7); break;                       /* bytes 0-6 */
        case M110: sum_batt += u16(d); sum_total += u16(d + 2); n110++; held.charging = d[4]; break;
        case M120: {
            memcpy(held.outputs, d + 2, 3);
            bool nonok = d[6] == CH_TRIPPED || d[6] == CH_RETRYING;
            if (nonok || !trip_nonok) { held.trip_index = d[5]; held.trip_status = d[6]; }
            if (nonok) trip_nonok = true;
            break; }
        case M130: if (d[0] < 22) held.ch_ca[d[0]] = u16(d + 1); break;
        case M180:
            held.wb_flags = d[6];
            /* AEMnet is big-endian; valid = byte 6 bit 7 set and byte 7 bit 6 clear */
            if ((d[6] & 0x80) && !(d[7] & 0x40)) { sum_lambda += (uint32_t)((d[0] << 8) | d[1]); n180++; }
            break;
        case M200: {
            uint16_t r = u16(d);
            sum_rpm += r; if (r > rpm_peak) rpm_peak = r;
            held.water_c = (int8_t)d[2]; held.oil_temp_c = (int8_t)d[3];
            sum_oil += u16(d + 4); sum_speed += d[6]; n200++;
            break; }
        case M210: memcpy(&held.sensor_valid, d, 4); break;
        case M218: sum_fuel += u16(d); n218++; held.fuel_valid = d[2]; break;
        case M220: held.pack_mv = u16(d); held.cell_mv[0] = u16(d + 2); held.cell_mv[1] = u16(d + 4); held.batt_flags = d[6]; break;
        case M221: held.cell_mv[2] = u16(d); held.cell_mv[3] = u16(d + 2); held.spread_mv = u16(d + 4); break;
        case M222: held.batt_da = (int16_t)u16(d); held.soc = d[2]; held.batt_c = (int8_t)d[3]; break;
        case M300: memcpy(&held.clim_mode, d, 6); break;                     /* LC37-LC42 */
        case M310: held.seat_heat = d[0]; held.seat_cool = d[1]; held.mirror_heat = d[2];
                   sum_comfort += u16(d + 4); n310++; break;
        case M320:
            if (!radar_this_s || d[0] >= radar_best[0]) memcpy(radar_best, d, 3);
            radar_this_s = true; memcpy(held.radar, d, 3);
            break;
        case M400: keys_down |= u16(d); keys_held |= u16(d + 2); break;
        }
    }

    /* the IMU (IC23), at 50 Hz: 0.01 g, lateral (+right), longitudinal (+accel), vertical */
    void on_imu(int16_t lat, int16_t lon, int16_t vert) {
        sum_acc[0] += lat; sum_acc[1] += lon; sum_acc[2] += vert; n_imu++;
        int16_t al = lat < 0 ? (int16_t)-lat : lat;
        if (al > peak_lat) peak_lat = al;
        if (lon > peak_acc) peak_acc = lon;
        if (lon < 0 && (int16_t)-lon > peak_brk) peak_brk = (int16_t)-lon;
    }

    /* Close the second: fill out and start the next one. */
    void finish(uint32_t now_ms, uint32_t odo_x10, uint8_t illum_pct, uint8_t page, log_thin_t *out) {
        static const uint16_t TMO[MCOUNT] = {
            TMO_PMU_STATE, TMO_PMU_POWER, TMO_PMU_OUTPUTS, TMO_PMU_OUTPUTS, 500, TMO_ICU_SENSORS,
            1000, TMO_ICU_BODY, TMO_ICU_BATT, TMO_ICU_BATT, TMO_ICU_BATT, TMO_DCU_CLIMATE,
            TMO_DCU_COMFORT, 0, TMO_PANEL_KEYS };
        bool live[MCOUNT];
        for (int m = 0; m < MCOUNT; m++) {
            uint32_t t = TMO[m] > 1000 ? TMO[m] : 1000;
            live[m] = ever[m] && (m == M320 || (uint32_t)(now_ms - seen_ms[m]) <= t);
        }
        log_thin_t r = held;
        r.time_ms = now_ms; r.odo_x10 = odo_x10;
        if (!live[M100]) memset(&r.key_pos, 0, 7);
        r.batt_mv  = n110 ? (uint16_t)(sum_batt / n110) : 0;
        r.total_ca = n110 ? (uint16_t)(sum_total / n110) : 0;
        if (!live[M110]) r.charging = 0;
        if (!live[M120]) { memset(r.outputs, 0, 3); r.trip_index = 0; r.trip_status = 0; }
        if (!live[M130]) memset(r.ch_ca, 0, sizeof r.ch_ca);
        r.lambda = n180 ? (uint16_t)(sum_lambda / n180) : 0;
        if (!live[M180]) r.wb_flags = 0;
        r.rpm = n200 ? (uint16_t)(sum_rpm / n200) : 0;
        r.rpm_peak = rpm_peak;
        r.oil_cbar = n200 ? (uint16_t)(sum_oil / n200) : 0;
        r.speed_kph = n200 ? (uint8_t)(sum_speed / n200) : 0;
        if (!live[M200]) { r.water_c = TEMP_INVALID; r.oil_temp_c = TEMP_INVALID; }
        if (!live[M210]) { r.sensor_valid = r.sensor_fault = r.can_health = r.telltales = 0; }
        r.fuel_x10 = n218 ? (uint16_t)(sum_fuel / n218) : 0;
        if (!live[M218]) r.fuel_valid = 0;
        if (!live[M220]) { r.pack_mv = 0; r.cell_mv[0] = r.cell_mv[1] = 0; r.batt_flags = 0; }
        if (!live[M221]) { r.cell_mv[2] = r.cell_mv[3] = 0; r.spread_mv = 0; }
        if (!live[M222]) { r.batt_da = 0; r.soc = 0; r.batt_c = 0; }
        if (!live[M300]) { memset(&r.clim_mode, 0, 6); r.cabin_c = TEMP_INVALID; r.outside_c = TEMP_INVALID; }
        r.comfort_ca = n310 ? (uint16_t)(sum_comfort / n310) : 0;
        if (!live[M310]) { r.seat_heat = r.seat_cool = r.mirror_heat = 0; }
        if (radar_this_s) memcpy(r.radar, radar_best, 3);
        r.keys_down = keys_down; r.keys_held = keys_held;
        for (int a = 0; a < 3; a++) r.acc_mean[a] = n_imu ? (int16_t)(sum_acc[a] / (int32_t)n_imu) : 0;
        r.acc_peak[0] = peak_lat; r.acc_peak[1] = peak_acc; r.acc_peak[2] = peak_brk;
        r.illum_pct = illum_pct; r.page = page;
        *out = r;
        clear_second();
    }

private:
    log_thin_t held;                    /* the latest of every state field */
    uint32_t seen_ms[MCOUNT];
    bool     ever[MCOUNT];
    uint32_t sum_batt, sum_total, sum_lambda, sum_rpm, sum_oil, sum_speed, sum_fuel, sum_comfort;
    uint16_t n110, n180, n200, n218, n310, n_imu;
    uint16_t rpm_peak;
    bool     trip_nonok, radar_this_s;
    uint8_t  radar_best[3];
    uint16_t keys_down, keys_held;
    int32_t  sum_acc[3];
    int16_t  peak_lat, peak_acc, peak_brk;

    static uint16_t u16(const uint8_t *p) { return (uint16_t)(p[0] | (p[1] << 8)); }

    void clear_second() {
        sum_batt = sum_total = sum_lambda = sum_rpm = sum_oil = sum_speed = sum_fuel = sum_comfort = 0;
        n110 = n180 = n200 = n218 = n310 = n_imu = 0;
        rpm_peak = 0; trip_nonok = false;
        /* the radar is on change: the state held now is in the next second too */
        radar_this_s = ever[M320]; memcpy(radar_best, held.radar, 3);
        keys_down = keys_held = 0;
        sum_acc[0] = sum_acc[1] = sum_acc[2] = 0;
        peak_lat = peak_acc = peak_brk = 0;
    }
};

/* ======================================================================
 * LogStore - the card: drives, tiers, pulled flags
 * ====================================================================== */
class LogStore {
public:
    LogFs   *fs = nullptr;
    void   (*save_seq)(uint32_t) = nullptr;   /* F-007: persist beside the odometer */
    bool     card = false;       /* present and writable; a failed write clears it   */
    uint32_t seq = 0;            /* the open drive, 0 = none                          */
    uint32_t last_seq = 0;       /* the highest drive there is                        */
    uint32_t mark = 1;           /* every drive below this has summary + thin pulled  */
    uint8_t  free_pct = 0;       /* as of begin / the last drive start                */
    uint32_t write_errors = 0;

    /* The card, and the sequence F-007 saved. False (and every call a no-op) without a
     * card - a missing card is LL_E_NO_CARD on the link, never a hang. */
    bool begin(LogFs *f, uint32_t persisted_seq) {
        fs = f; seq = 0; h_thin = h_full = h_sum = -1; fbuf_n = 0; np_valid = false;
        card = fs && fs->present() && fs->mkdir(LOG_ROOT);
        if (!card) return false;
        uint32_t lim[2] = { 0, 0 };   /* lowest, highest */
        fs->list(LOG_ROOT, scan_cb, lim);
        last_seq = lim[1] > persisted_seq ? lim[1] : persisted_seq;
        mark = lim[0] ? lim[0] : last_seq + 1;
        uint32_t m = 0;
        int h = fs->open(LOG_ROOT "/mark.bin", LogFs::RD);
        if (h >= 0) { if (fs->read(h, &m, 4) == 4 && m > mark && m <= last_seq + 1) mark = m; fs->close(h); }
        free_pct = fs->free_pct();
        return true;
    }

    /* Key on: a new drive (D-493). unix_now is 0 when the RTC is unset. */
    bool start_drive(uint32_t now_ms, uint32_t odo_x10, uint32_t unix_now) {
        if (!card) return false;
        if (seq) end_drive();
        free_pct = fs->free_pct();
        prune();
        uint32_t s = last_seq + 1;
        char p[LOG_PATH_MAX];
        log_path(p, s, nullptr);
        if (!fs->mkdir(p)) return fail();
        memcpy(hdr.magic, "RX7L", 4);
        hdr.version = LOG_FORMAT_VERSION; hdr.seq = s; hdr.start_odo = odo_x10;
        hdr.uptime_start = now_ms; hdr.unix_start = unix_now;
        memset(hdr._rsv, 0, sizeof hdr._rsv);
        int hs = create_tier(s, LL_TIER_SUMMARY), ht = create_tier(s, LL_TIER_THIN), hf = create_tier(s, LL_TIER_FULL);
        log_pulled_t pf; memset(&pf, 0, sizeof pf); memcpy(pf.magic, "RX7P", 4);
        if (hs < 0 || ht < 0 || hf < 0 || !write_pulled(s, &pf)) {
            if (hs >= 0) fs->close(hs);
            if (ht >= 0) fs->close(ht);
            if (hf >= 0) fs->close(hf);
            return fail();
        }
        h_sum = hs; h_thin = ht; h_full = hf;
        seq = s; last_seq = s; sum_acked = false; last_flush = now_ms;
        t_set_unix = t_set_uptime = t_set_prev = 0;
        np_valid = false;
        if (save_seq) save_seq(s);
        return true;
    }

    void add_second(const log_thin_t &r) {
        if (!seq) return;
        if (fs->write(h_thin, &r, sizeof r) != (int32_t)sizeof r) fail();
    }

    void add_frame(const log_full_t &f) {
        if (!seq) return;
        if (fbuf_n + sizeof f > sizeof fbuf) drain_full();
        memcpy(fbuf + fbuf_n, &f, sizeof f);
        fbuf_n += sizeof f;
    }

    /* The summary, rewritten in place (every minute and at key-off). The SET_TIME
     * fields are the store's own (note_time_set), whatever the caller passed. */
    void write_summary(log_summary_t s) {
        if (!seq) return;
        s.seq = seq; s.start_odo = hdr.start_odo; s.unix_start = hdr.unix_start; s.uptime_start = hdr.uptime_start;
        s.time_set_unix = t_set_unix; s.time_set_uptime = t_set_uptime; s.time_set_prev = t_set_prev;
        if (!fs->seek(h_sum, LOG_HEADER_LEN) || fs->write(h_sum, &s, sizeof s) != (int32_t)sizeof s) { fail(); return; }
        if (sum_acked) {   /* the app's copy is now older than the card's: not pulled */
            log_pulled_t pf;
            if (read_pulled(seq, &pf)) { pf.t[LL_TIER_SUMMARY].len = 0; pf.t[LL_TIER_SUMMARY].crc = 0; write_pulled(seq, &pf); }
            sum_acked = false;
        }
    }

    /* SET_TIME applied (LL08: "logged in the summary") */
    void note_time_set(uint32_t prev, uint32_t unix_time, uint32_t now_ms) {
        t_set_prev = prev; t_set_unix = unix_time; t_set_uptime = now_ms;
    }

    /* Call often: the flush every second (D-493, B7). */
    void tick(uint32_t now_ms) {
        if (!seq || (uint32_t)(now_ms - last_flush) < LOG_FLUSH_MS) return;
        last_flush = now_ms;
        drain_full();
        if (!seq) return;
        if (!fs->flush(h_thin) || !fs->flush(h_full) || !fs->flush(h_sum)) fail();
    }

    /* Key off, or a new drive. */
    void end_drive() {
        if (!seq) return;
        drain_full();
        if (seq) {
            fs->flush(h_thin); fs->flush(h_full); fs->flush(h_sum);
            fs->close(h_thin); fs->close(h_full); fs->close(h_sum);
        }
        h_thin = h_full = h_sum = -1;
        seq = 0; np_valid = false;
    }

    /* ---- the index, for the link ---- */

    int32_t tier_size(uint32_t s, uint8_t tier) {
        char p[LOG_PATH_MAX];
        if (tier >= LL_TIERS) return -1;
        log_path(p, s, LOG_TIER_FILE[tier]);
        int h = fs->open(p, LogFs::RD);
        if (h < 0) return -1;
        int32_t n = fs->size(h);
        fs->close(h);
        return n;
    }

    int open_tier(uint32_t s, uint8_t tier) {
        char p[LOG_PATH_MAX];
        if (tier >= LL_TIERS) return -1;
        log_path(p, s, LOG_TIER_FILE[tier]);
        return fs->open(p, LogFs::RD);
    }

    /* The LL04 entry for drive s; false if there is no such drive. */
    bool drive_item(uint32_t s, ll_item_t *it) {
        memset(it, 0, sizeof *it);
        if (!card || s == 0) return false;
        int h = open_tier(s, LL_TIER_THIN);
        if (h < 0) return false;
        log_header_t th;
        int32_t got = fs->read(h, &th, sizeof th);
        int32_t thin = fs->size(h);
        fs->close(h);
        if (got != (int32_t)sizeof th || memcmp(th.magic, "RX7L", 4) != 0) return false;
        int32_t sum = tier_size(s, LL_TIER_SUMMARY), full = tier_size(s, LL_TIER_FULL);
        it->seq = s; it->start_odo = th.start_odo; it->start_unix = th.unix_start;
        it->thin_len = (uint32_t)thin;
        it->summary_len = sum > 0 ? (uint16_t)sum : 0;
        it->full_len = full > 0 ? (uint32_t)full : 0;
        it->duration_s = thin > LOG_HEADER_LEN ? (uint32_t)(thin - LOG_HEADER_LEN) / LOG_THIN_LEN : 0;
        log_pulled_t pf;
        if (read_pulled(s, &pf)) {
            uint32_t len[LL_TIERS] = { it->summary_len, it->thin_len, it->full_len };
            for (int t = 0; t < LL_TIERS; t++)
                if (pf.t[t].len != 0 && pf.t[t].len == len[t]) it->pulled |= (uint8_t)(1u << t);
        }
        return true;
    }

    /* The app holds [0, len) of the tier with this CRC (an ACK that matched). */
    bool set_pulled(uint32_t s, uint8_t tier, uint32_t len, uint32_t crc) {
        log_pulled_t pf;
        ll_item_t before, after;
        bool had = drive_item(s, &before);
        if (!read_pulled(s, &pf)) return false;
        pf.t[tier].len = len; pf.t[tier].crc = crc;
        if (!write_pulled(s, &pf)) return false;
        if (s == seq && tier == LL_TIER_SUMMARY) sum_acked = true;
        /* keep the count without a rescan of the card (INFO asks every second) */
        if (np_valid && had && s != seq && drive_item(s, &after) &&
            (before.pulled & 3) != 3 && (after.pulled & 3) == 3 && np_cache) np_cache--;
        advance_mark();
        return true;
    }

    /* Drives whose summary or thinned log is not pulled (LL03); the open drive counts. */
    uint16_t not_pulled() {
        if (!card) return 0;
        if (!np_valid) {
            uint32_t n = 0;
            for (uint32_t s = mark; s <= last_seq; s++) {
                if (s == seq) continue;
                ll_item_t it;
                if (drive_item(s, &it) && (it.pulled & 3) != 3) n++;
            }
            np_cache = n; np_valid = true;
        }
        uint32_t n = np_cache + (seq ? 1 : 0);
        return n > 0xFFFF ? 0xFFFF : (uint16_t)n;
    }

    bool read_pulled(uint32_t s, log_pulled_t *pf) {
        char p[LOG_PATH_MAX];
        log_path(p, s, "pulled.flg");
        int h = fs->open(p, LogFs::RD);
        memset(pf, 0, sizeof *pf); memcpy(pf->magic, "RX7P", 4);
        if (h < 0) return exists_drive(s);      /* a drive without one: nothing pulled */
        int32_t n = fs->read(h, pf, sizeof *pf);
        fs->close(h);
        if (n != (int32_t)sizeof *pf || memcmp(pf->magic, "RX7P", 4) != 0) {
            memset(pf, 0, sizeof *pf); memcpy(pf->magic, "RX7P", 4);
        }
        return true;
    }

private:
    log_header_t hdr;
    int      h_thin = -1, h_full = -1, h_sum = -1;
    uint8_t  fbuf[LOG_FULL_BUF];
    uint32_t fbuf_n = 0;
    uint32_t last_flush = 0;
    bool     sum_acked = false;
    uint32_t t_set_unix = 0, t_set_uptime = 0, t_set_prev = 0;
    bool     np_valid = false;
    uint32_t np_cache = 0;

    static void scan_cb(const char *name, bool is_dir, void *ctx) {
        uint32_t *lim = (uint32_t *)ctx;
        uint32_t s = is_dir ? log_parse_seq(name) : 0;
        if (!s) return;
        if (lim[0] == 0 || s < lim[0]) lim[0] = s;
        if (s > lim[1]) lim[1] = s;
    }

    bool fail() {
        write_errors++;
        if (seq) { fs->close(h_thin); fs->close(h_full); fs->close(h_sum); }
        h_thin = h_full = h_sum = -1;
        seq = 0; card = false; fbuf_n = 0;
        return false;
    }

    bool exists_drive(uint32_t s) {
        char p[LOG_PATH_MAX];
        log_path(p, s, LOG_TIER_FILE[LL_TIER_THIN]);
        return fs->exists(p);
    }

    int create_tier(uint32_t s, uint8_t tier) {
        char p[LOG_PATH_MAX];
        log_path(p, s, LOG_TIER_FILE[tier]);
        int h = fs->open(p, LogFs::CREATE);
        if (h < 0) return -1;
        log_header_t x = hdr;
        x.tier = tier; x.record_len = log_record_len(tier); x.layout_crc = log_layout_crc(tier);
        if (fs->write(h, &x, sizeof x) != (int32_t)sizeof x || !fs->flush(h)) { fs->close(h); return -1; }
        return h;
    }

    bool write_pulled(uint32_t s, const log_pulled_t *pf) {
        char p[LOG_PATH_MAX];
        log_path(p, s, "pulled.flg");
        int h = fs->open(p, LogFs::CREATE);
        if (h < 0) return false;
        bool ok = fs->write(h, pf, sizeof *pf) == (int32_t)sizeof *pf && fs->flush(h);
        fs->close(h);
        return ok;
    }

    void drain_full() {
        if (!seq || fbuf_n == 0) return;
        if (fs->write(h_full, fbuf, fbuf_n) != (int32_t)fbuf_n) { fail(); return; }
        fbuf_n = 0;
    }

    void advance_mark() {
        uint32_t m = mark;
        while (m <= last_seq && m != seq) {
            ll_item_t it;
            if (drive_item(m, &it) && (it.pulled & 3) != 3) break;
            m++;
        }
        if (m == mark) return;
        mark = m;
        int h = fs->open(LOG_ROOT "/mark.bin", LogFs::CREATE);
        if (h >= 0) { fs->write(h, &mark, 4); fs->flush(h); fs->close(h); }
    }

    /* D-493: full logs are kept until the card is three-quarters full, oldest first.
     * Summaries and thinned logs are never deleted. At most 64 a drive start. */
    void prune() {
        int removed = 0;
        for (uint32_t s = 1; s <= last_seq && free_pct < LOG_KEEP_FREE_PCT && removed < 64; s++) {
            char p[LOG_PATH_MAX];
            log_path(p, s, LOG_TIER_FILE[LL_TIER_FULL]);
            if (fs->exists(p) && fs->remove(p)) { removed++; free_pct = fs->free_pct(); }
        }
    }
};

/* ======================================================================
 * LogServer - the Teensy's end of the link (LL06-LL08, LL12-LL14)
 *
 * One switch over the frame types the C3 can send; its default is ERR 1. Nothing in it
 * reaches an output, a setting or the flash (D-478); SET_TIME is the one state write
 * (D-493), through LogHost::rtc_set, and only when ll_time_should_set says so.
 * ====================================================================== */
class LogHost {
public:
    virtual ~LogHost() {}
    virtual uint32_t odometer_x10() = 0;
    virtual uint16_t fw() = 0;
    virtual bool     rtc_is_set() = 0;
    virtual uint32_t rtc_unix() = 0;
    virtual void     rtc_set(uint32_t unix_time) = 0;
    /* the radio's pairing state, for the cluster to show (added frame PAIRING) */
    virtual void     on_pairing(uint8_t state, uint32_t passkey, uint8_t secs_left) = 0;
};

class LogOut {
public:
    virtual ~LogOut() {}
    virtual size_t room() = 0;                          /* bytes the wire takes now */
    virtual void   write(const uint8_t *p, size_t n) = 0;
};

class LogServer {
public:
    enum { SV_IDLE = 0, SV_LIST, SV_PREFIX, SV_SEND, SV_VERIFY };
    LogStore *st = nullptr;
    LogOut   *out = nullptr;
    LogHost  *host = nullptr;
    uint8_t   state = SV_IDLE;
    uint32_t  credit = 0;
    uint32_t  frames_in = 0, frames_out = 0;

    void begin(LogStore *s, LogOut *o, LogHost *h) { st = s; out = o; host = h; stop(); credit = 0; end_valid = false; }

    /* One frame from the C3. */
    void on_frame(uint8_t type, const uint8_t *p, uint16_t n, uint32_t now) {
        frames_in++;
        switch (type) {
        case LL_LIST: {
            if (n != sizeof(ll_list_t)) { send_err(LL_E_OPCODE); break; }
            ll_list_t a; memcpy(&a, p, sizeof a);
            stop(); credit = 0; credit_ms = now;
            if (!st->card) { send_err(LL_E_NO_CARD); break; }
            list_unpulled = a.from_seq == 0;
            list_next = list_unpulled ? st->mark : a.from_seq;
            state = SV_LIST;
            break; }
        case LL_OPEN: {
            if (n != sizeof(ll_open_t)) { send_err(LL_E_OPCODE); break; }
            ll_open_t a; memcpy(&a, p, sizeof a);
            stop(); credit = 0; credit_ms = now;       /* a second OPEN aborts the first (LL07) */
            if (!st->card) { send_err(LL_E_NO_CARD); break; }
            if (a.tier >= LL_TIERS || (h = st->open_tier(a.seq, a.tier)) < 0) { send_err(LL_E_NO_DRIVE); break; }
            int32_t sz = st->fs->size(h);
            if (sz < 0 || a.offset > (uint32_t)sz) { stop(); send_err(LL_E_NO_DRIVE); break; }
            t_seq = a.seq; t_tier = a.tier; offset = a.offset; total = (uint32_t)sz;
            pos = 0; crc = LL_CRC32_INIT;
            state = SV_PREFIX;                         /* the CRC of [0, offset) first */
            break; }
        case LL_ACK: {
            if (n != sizeof(ll_ack_t)) { send_err(LL_E_OPCODE); break; }
            ll_ack_t a; memcpy(&a, p, sizeof a);
            if (state != SV_IDLE) { send_err(LL_E_BUSY); break; }
            if (!st->card) { send_err(LL_E_NO_CARD); break; }
            if (a.tier >= LL_TIERS || (h = st->open_tier(a.seq, a.tier)) < 0) { send_err(LL_E_NO_DRIVE); break; }
            if (end_valid && end_seq == a.seq && end_tier == a.tier) {
                st->fs->close(h); h = -1;
                if (a.crc32 != end_crc) { send_err(LL_E_CRC); break; }
                send_err(st->set_pulled(a.seq, a.tier, end_total, end_crc) ? LL_E_NONE : LL_E_NO_CARD);
                break;
            }
            /* no END this power cycle (the key went off between END and ACK): check the
             * whole file as it is now */
            int32_t sz = st->fs->size(h);
            if (sz < 0) { stop(); send_err(LL_E_NO_CARD); break; }
            t_seq = a.seq; t_tier = a.tier; total = (uint32_t)sz; pos = 0; crc = LL_CRC32_INIT;
            want_crc = a.crc32;
            state = SV_VERIFY;
            break; }
        case LL_ABORT:
            stop(); credit = 0;
            send_err(LL_E_ABORTED);
            break;
        case LL_SET_TIME: {
            if (n != sizeof(ll_set_time_t)) { send_err(LL_E_OPCODE); break; }
            ll_set_time_t a; memcpy(&a, p, sizeof a);
            bool was = host->rtc_is_set();
            uint32_t prev = was ? host->rtc_unix() : 0;
            if (ll_time_should_set(prev, was, a.unix_time)) {
                host->rtc_set(a.unix_time);
                st->note_time_set(prev, a.unix_time, now);
            }
            send_info(now);
            break; }
        case LL_PING:
            send_info(now);
            break;
        case LL_CREDIT: {
            if (n != sizeof(ll_credit_t)) { send_err(LL_E_OPCODE); break; }
            ll_credit_t a; memcpy(&a, p, sizeof a);
            credit += a.bytes;
            if (credit > 0x100000u) credit = 0x100000u;
            credit_ms = now;
            break; }
        case LL_PAIRING: {
            if (n != sizeof(ll_pairing_t)) { send_err(LL_E_OPCODE); break; }
            ll_pairing_t a; memcpy(&a, p, sizeof a);
            host->on_pairing(a.state, a.passkey, a.secs_left);   /* shown, nothing set */
            break; }
        default:
            send_err(LL_E_OPCODE);
            break;
        }
    }

    /* Call every loop: lists, streams and verifies a little at a time, never past the
     * credit, never more than the wire takes. */
    void poll(uint32_t now) {
        int lookups = 0;
        for (int budget = 0; budget < 16 && state != SV_IDLE; budget++) {
            if (out->room() < LL_FRAME_MAX) return;
            if ((state == SV_LIST || state == SV_SEND) && (uint32_t)(now - credit_ms) > LL_TIMEOUT_MS &&
                credit < need_credit()) {
                stop(); credit = 0;
                send_err(LL_E_ABORTED);                  /* LL14: no CREDIT for 5 s */
                return;
            }
            switch (state) {
            case SV_LIST: {
                if (list_next == 0 || list_next > st->last_seq) {
                    if (credit < sizeof(ll_item_t)) return;
                    ll_item_t end; memset(&end, 0, sizeof end);  /* seq 0 ends the list */
                    send(LL_ITEM, &end, sizeof end); credit -= sizeof end;
                    state = SV_IDLE;
                    return;
                }
                if (lookups >= 2) return;                /* four opens each: keep the loop free */
                ll_item_t it;
                lookups++;
                if (!st->drive_item(list_next, &it) || (list_unpulled && (it.pulled & 3) == 3)) { list_next++; break; }
                if (credit < sizeof it) { lookups = 2; return; }
                send(LL_ITEM, &it, sizeof it); credit -= sizeof it;
                list_next++;
                break; }
            case SV_PREFIX:
            case SV_VERIFY: {
                uint32_t stop_at = state == SV_PREFIX ? offset : total;
                if (pos < stop_at) {
                    uint8_t b[512];
                    uint32_t k = stop_at - pos > sizeof b ? (uint32_t)sizeof b : stop_at - pos;
                    if (!st->fs->seek(h, pos) || st->fs->read(h, b, k) != (int32_t)k) { stop(); send_err(LL_E_NO_CARD); return; }
                    crc = ll_crc32_update(crc, b, k);
                    pos += k;
                    break;
                }
                if (state == SV_PREFIX) {
                    ll_start_t s = { t_seq, t_tier, offset, total };
                    send(LL_START, &s, sizeof s);
                    state = SV_SEND;
                    break;
                }
                uint32_t got = ll_crc32_final(crc);      /* SV_VERIFY done */
                uint32_t s = t_seq; uint8_t t = t_tier;
                stop();
                if (got != want_crc) { send_err(LL_E_CRC); return; }
                send_err(st->set_pulled(s, t, total, got) ? LL_E_NONE : LL_E_NO_CARD);
                return; }
            case SV_SEND: {
                if (pos >= total) {
                    ll_end_t e = { ll_crc32_final(crc) };
                    end_valid = true; end_seq = t_seq; end_tier = t_tier; end_total = total; end_crc = e.crc32;
                    send(LL_END, &e, sizeof e);
                    stop();
                    return;
                }
                if (credit < need_credit()) return;
                uint32_t k = total - pos > LL_DATA_MAX ? LL_DATA_MAX : total - pos;
                if (k > credit - 4) k = credit - 4;      /* what the credit covers, never more */
                uint8_t b[LL_DATA_MAX];
                if (!st->fs->seek(h, pos) || st->fs->read(h, b, k) != (int32_t)k) { stop(); send_err(LL_E_NO_CARD); return; }
                crc = ll_crc32_update(crc, b, k);
                uint8_t f[LL_FRAME_MAX];
                size_t fn = ll_encode_data(f, sizeof f, pos, b, k);
                out->write(f, fn); frames_out++;
                credit -= 4 + k;
                pos += k;
                break; }
            }
        }
    }

    /* the INFO record (LL03) */
    void fill_info(ll_info_t *i, uint32_t now) {
        bool set = host->rtc_is_set();
        i->protocol = LL_PROTOCOL;
        i->fw = host->fw();
        i->odometer = host->odometer_x10();
        i->drive_count = st->card ? st->last_seq : 0;
        i->not_pulled = st->not_pulled();
        i->card_free = st->card ? st->free_pct : 0;
        i->rtc_set = set ? 1 : 0;
        i->unix_time = set ? host->rtc_unix() : 0;
        i->uptime_ms = now;
    }

private:
    int      h = -1;
    uint32_t list_next = 0;
    bool     list_unpulled = false;
    uint32_t credit_ms = 0;
    uint32_t t_seq = 0, offset = 0, pos = 0, total = 0, crc = 0, want_crc = 0;
    uint8_t  t_tier = 0;
    bool     end_valid = false;
    uint32_t end_seq = 0, end_total = 0, end_crc = 0;
    uint8_t  end_tier = 0;

    uint32_t need_credit() const {
        if (state == SV_LIST) return sizeof(ll_item_t);
        return 4 + 1;          /* an offset and at least one byte; DATA shrinks to the credit */
    }

    void stop() {
        if (h >= 0 && st && st->fs) st->fs->close(h);
        h = -1;
        state = SV_IDLE;
    }

    void send(uint8_t type, const void *p, size_t n) {
        uint8_t f[LL_FRAME_MAX];
        size_t fn = ll_encode(f, sizeof f, type, p, n);
        if (fn) { out->write(f, fn); frames_out++; }
    }

    void send_err(uint8_t e) { ll_err_t x = { e }; send(LL_ERR, &x, sizeof x); }

    void send_info(uint32_t now) { ll_info_t i; fill_info(&i, now); send(LL_INFO, &i, sizeof i); }
};

#endif /* LOG_STORE_H */

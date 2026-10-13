/*
 * test_loglink.cpp — desktop verification of the log link (BT3, D-493, D-494):
 * the UART framing and CRCs (icu/log_link.h), the card layout and the thinned record
 * (icu/log_store.h), and the Teensy's side of a pull - list, transfer under credit, a
 * broken transfer resumed, ACK, SET_TIME - through an in-memory card.
 *
 * The record is held here through log_vectors.h, which gen_log_vectors.py writes from
 * log_channels.csv, log_link.csv and params.csv (run.sh runs it first).
 *
 * Build (g++ on PATH):
 *   python3 gen_log_vectors.py && g++ test_loglink.cpp -o test_loglink -std=c++17 -O2 && ./test_loglink
 */
#include <cstdio>
#include <cstring>
#include <cstddef>
#include <map>
#include <set>
#include <string>
#include <vector>
#include "../display-unit/firmware/icu/log_link.h"
#include "../display-unit/firmware/icu/log_store.h"
#include "../display-unit/firmware/icu/radio_link.h"
#include "log_vectors.h"

static int passed = 0, failed = 0;
#define CHECK(c, msg) do { if (c) passed++; else { failed++; printf("  FAIL  %s  (line %d)\n", msg, __LINE__); } } while (0)

/* ---------------- an in-memory card ---------------- */
struct MemFs : LogFs {
    std::map<std::string, std::vector<uint8_t>> files;
    std::set<std::string> dirs;
    struct H { std::string path; uint32_t pos; int mode; bool open; };
    std::vector<H> hs;
    bool card = true, fail_writes = false;
    uint8_t freep = 80;
    int writes = 0;                 /* every byte-changing call */

    bool present() override { return card; }
    bool mkdir(const char *p) override { if (!card) return false; dirs.insert(p); return true; }
    bool exists(const char *p) override { return files.count(p) || dirs.count(p); }
    bool remove(const char *p) override { writes++; return files.erase(p) > 0; }
    int open(const char *p, int mode) override {
        if (!card) return -1;
        std::string s(p);
        size_t sl = s.rfind('/');
        if (sl != std::string::npos && sl > 0 && !dirs.count(s.substr(0, sl))) return -1;
        if (mode == RD && !files.count(s)) return -1;
        if (mode == CREATE) { files[s].clear(); writes++; }
        else if (mode == RW) files[s];
        hs.push_back({ s, 0, mode, true });
        return (int)hs.size() - 1;
    }
    H *get(int h) { return (h >= 0 && h < (int)hs.size() && hs[h].open) ? &hs[h] : nullptr; }
    bool seek(int h, uint32_t pos) override {
        H *x = get(h); if (!x || pos > files[x->path].size()) return false; x->pos = pos; return true;
    }
    int32_t read(int h, void *b, uint32_t n) override {
        H *x = get(h); if (!x || !card) return -1;
        auto &v = files[x->path];
        uint32_t k = x->pos >= v.size() ? 0 : (uint32_t)std::min<size_t>(n, v.size() - x->pos);
        if (k) memcpy(b, v.data() + x->pos, k);
        x->pos += k; return (int32_t)k;
    }
    int32_t write(int h, const void *b, uint32_t n) override {
        H *x = get(h); if (!x || x->mode == RD || fail_writes || !card) return -1;
        writes++;
        auto &v = files[x->path];
        if (x->pos + n > v.size()) v.resize(x->pos + n);
        memcpy(v.data() + x->pos, b, n); x->pos += n; return (int32_t)n;
    }
    int32_t size(int h) override { H *x = get(h); return x ? (int32_t)files[x->path].size() : -1; }
    bool flush(int h) override { return get(h) && card && !fail_writes; }
    void close(int h) override { if (H *x = get(h)) x->open = false; }
    bool list(const char *dir, void (*cb)(const char *, bool, void *), void *ctx) override {
        std::string d = std::string(dir) + "/";
        for (auto &s : dirs)
            if (s.compare(0, d.size(), d) == 0 && s.find('/', d.size()) == std::string::npos) cb(s.c_str() + d.size(), true, ctx);
        return true;
    }
    uint8_t free_pct() override { return freep; }
    std::vector<uint8_t> &file(uint32_t seq, const char *name) { char p[LOG_PATH_MAX]; log_path(p, seq, name); return files[p]; }
    int open_handles() { int n = 0; for (auto &h : hs) n += h.open; return n; }
};

/* ---------------- the wire, decoded ---------------- */
struct Frame { uint8_t type; std::vector<uint8_t> p; };
struct Sink : LogOut {
    std::vector<uint8_t> bytes;
    size_t cap = 1 << 20;
    size_t room() override { return cap; }
    void write(const uint8_t *p, size_t n) override { bytes.insert(bytes.end(), p, p + n); }
    std::vector<Frame> take() {
        std::vector<Frame> out; ll_rx_t rx; ll_rx_init(&rx);
        for (uint8_t b : bytes)
            if (ll_rx_feed(&rx, b) == LL_RX_FRAME)
                out.push_back({ ll_rx_type(&rx), std::vector<uint8_t>(ll_rx_payload(&rx), ll_rx_payload(&rx) + ll_rx_plen(&rx)) });
        bytes.clear();
        return out;
    }
};

struct Host : LogHost {
    bool set = false; uint32_t unix_now = 0; int sets = 0; uint32_t odo = 123456;
    uint8_t pair_state = 0; uint32_t passkey = 0;
    uint32_t odometer_x10() override { return odo; }
    uint16_t fw() override { return 600; }
    bool rtc_is_set() override { return set; }
    uint32_t rtc_unix() override { return unix_now; }
    void rtc_set(uint32_t t) override { unix_now = t; set = true; sets++; }
    void on_pairing(uint8_t s, uint32_t k, uint8_t) override { pair_state = s; passkey = k; }
};

template <class T> static void tx(LogServer &sv, uint8_t type, const T &v, uint32_t now) { sv.on_frame(type, (const uint8_t *)&v, sizeof v, now); }
static void tx0(LogServer &sv, uint8_t type, uint32_t now) { sv.on_frame(type, nullptr, 0, now); }
static void credit(LogServer &sv, uint16_t n, uint32_t now) { ll_credit_t c = { n }; tx(sv, LL_CREDIT, c, now); }
template <class T> static T as(const Frame &f) { T v; memset(&v, 0, sizeof v); memcpy(&v, f.p.data(), std::min(sizeof v, f.p.size())); return v; }
static int last_err(const std::vector<Frame> &fs) { for (auto it = fs.rbegin(); it != fs.rend(); ++it) if (it->type == LL_ERR) return it->p[0]; return -1; }

/* A drive with `secs` seconds of thinned log and some full-log frames. */
static void drive(LogStore &st, uint32_t t0, uint32_t odo, int secs)
{
    st.start_drive(t0, odo, 0);
    LogThinAccum acc;
    for (int s = 1; s <= secs; s++) {
        for (int k = 0; k < 20; k++) {
            uint32_t t = t0 + (uint32_t)(s - 1) * 1000 + (uint32_t)k * 50;
            icu_sensors_t f = { (uint16_t)(1000 + 37 * s + k), 88, 95, 420, (uint8_t)s, (uint8_t)k };
            acc.on_frame(ID_ICU_SENSORS, false, (const uint8_t *)&f, 8, t);
            log_full_t r = { t, ID_ICU_SENSORS, (uint8_t)(8 << 4), {} };
            memcpy(r.data, &f, 8);
            st.add_frame(r);
        }
        log_thin_t rec; acc.finish(t0 + (uint32_t)s * 1000, odo + (uint32_t)s, 40, 0, &rec);
        st.add_second(rec);
        st.tick(t0 + (uint32_t)s * 1000);
    }
    log_summary_t sm; memset(&sm, 0, sizeof sm); sm.duration_s = (uint32_t)secs;
    st.write_summary(sm);
}

/* Pull a tier from `offset`, the C3's way: grant `window` bytes, grant again what was
 * forwarded. Stops after `stop_after` data bytes (a break) if non-zero. Checks the
 * Teensy never sends past its credit and that offsets run on without a gap. */
struct Pull { std::vector<uint8_t> bytes; bool ended = false; uint32_t crc = 0; uint32_t total = 0; bool over_credit = false; bool gap = false; int err = -1; };
static Pull pull(LogServer &sv, Sink &w, uint32_t seq, uint8_t tier, uint32_t offset, uint16_t window, uint32_t stop_after, uint32_t &now)
{
    Pull r;
    ll_open_t o = { seq, tier, offset };
    tx(sv, LL_OPEN, o, now);
    credit(sv, window, now);
    int64_t outstanding = window;
    uint32_t expect = offset;
    for (int i = 0; i < 100000 && !r.ended; i++) {
        now += 1;
        sv.poll(now);
        uint32_t used = 0;
        for (auto &f : w.take()) {
            if (f.type == LL_START) r.total = as<ll_start_t>(f).total;
            if (f.type == LL_DATA) {
                uint32_t off; memcpy(&off, f.p.data(), 4);
                if (off != expect) r.gap = true;
                r.bytes.insert(r.bytes.end(), f.p.begin() + 4, f.p.end());
                expect = off + (uint32_t)(f.p.size() - 4);
                used += (uint32_t)f.p.size();
                outstanding -= (int64_t)f.p.size();
                if (outstanding < 0) r.over_credit = true;
            }
            if (f.type == LL_END) { r.ended = true; r.crc = as<ll_end_t>(f).crc32; }
            if (f.type == LL_ERR) { r.err = f.p[0]; return r; }
        }
        if (stop_after && r.bytes.size() >= stop_after) return r;
        if (used) { credit(sv, (uint16_t)used, now); outstanding += used; }
        if (sv.state == LogServer::SV_IDLE && !r.ended) break;
    }
    return r;
}

static std::vector<ll_item_t> list(LogServer &sv, Sink &w, uint32_t from, uint32_t &now, int *err = nullptr)
{
    std::vector<ll_item_t> out;
    ll_list_t l = { from };
    tx(sv, LL_LIST, l, now);
    credit(sv, 4096, now);
    for (int i = 0; i < 1000; i++) {
        now += 1; sv.poll(now);
        for (auto &f : w.take()) {
            if (f.type == LL_ERR && err) *err = f.p[0];
            if (f.type != LL_ITEM) continue;
            ll_item_t it = as<ll_item_t>(f);
            if (it.seq == 0) return out;
            out.push_back(it);
        }
        if (sv.state == LogServer::SV_IDLE) break;
    }
    return out;
}

int main()
{
    printf("-- log link verification (BT3, D-493, D-494) --\n");

    /* ---------- 1. the checksums ---------- */
    {
        const char *v = "123456789";
        CHECK(ll_crc16(0xFFFF, (const uint8_t *)v, 9) == 0x29B1, "CRC-16/CCITT-FALSE of 123456789 is 0x29B1");
        CHECK(ll_crc32(v, 9) == 0xCBF43926u, "CRC-32 of 123456789 is 0xCBF43926");
        CHECK(ll_crc32("", 0) == 0, "CRC-32 of nothing is 0");
        uint8_t big[1000]; for (int i = 0; i < 1000; i++) big[i] = (uint8_t)(i * 7 + 3);
        uint32_t c = LL_CRC32_INIT; c = ll_crc32_update(c, big, 333); c = ll_crc32_update(c, big + 333, 667);
        CHECK(ll_crc32_final(c) == ll_crc32(big, 1000), "CRC-32 in pieces is CRC-32 whole (a resumed transfer's prefix)");
        const uint8_t z[4] = { 0, 0, 0, 0 };
        CHECK(ll_crc32(z, 4) == 0x2144DF1Cu, "CRC-32 of four zero bytes is 0x2144DF1C");
    }

    /* ---------- 2. the record: log_channels, params, log_link ---------- */
    {
        CHECK(V_LOG_CHANNELS == LOG_CHANNELS, "53 channels, as log_channels has rows");
        CHECK(V_LOG_THIN_SUM == sizeof(log_thin_t), "sizeof(log_thin_t) is the sum of log_channels.bytes (from the CSV)");
        CHECK(V_PARAM_THIN == sizeof(log_thin_t), "and params log_thin_bytes_per_s");
        bool w = true; for (int i = 0; i < LOG_CHANNELS; i++) w = w && LOG_CH_BYTES[i] == V_LOG_CH_BYTES[i];
        CHECK(w, "LOG_CH_BYTES is log_channels.bytes, row for row");
        const size_t off[LOG_CHANNELS] = {
            offsetof(log_thin_t, time_ms), offsetof(log_thin_t, odo_x10), offsetof(log_thin_t, key_pos),
            offsetof(log_thin_t, wake), offsetof(log_thin_t, fault), offsetof(log_thin_t, headlight),
            offsetof(log_thin_t, turn), offsetof(log_thin_t, popup), offsetof(log_thin_t, input_fault),
            offsetof(log_thin_t, batt_mv), offsetof(log_thin_t, total_ca), offsetof(log_thin_t, charging),
            offsetof(log_thin_t, outputs), offsetof(log_thin_t, trip_index), offsetof(log_thin_t, ch_ca),
            offsetof(log_thin_t, lambda), offsetof(log_thin_t, wb_flags), offsetof(log_thin_t, rpm),
            offsetof(log_thin_t, rpm_peak), offsetof(log_thin_t, water_c), offsetof(log_thin_t, oil_temp_c),
            offsetof(log_thin_t, oil_cbar), offsetof(log_thin_t, speed_kph), offsetof(log_thin_t, sensor_valid),
            offsetof(log_thin_t, sensor_fault), offsetof(log_thin_t, can_health), offsetof(log_thin_t, telltales),
            offsetof(log_thin_t, fuel_x10), offsetof(log_thin_t, fuel_valid), offsetof(log_thin_t, pack_mv),
            offsetof(log_thin_t, cell_mv), offsetof(log_thin_t, spread_mv), offsetof(log_thin_t, batt_flags),
            offsetof(log_thin_t, batt_da), offsetof(log_thin_t, soc), offsetof(log_thin_t, batt_c),
            offsetof(log_thin_t, clim_mode), offsetof(log_thin_t, blower), offsetof(log_thin_t, target_c),
            offsetof(log_thin_t, cabin_c), offsetof(log_thin_t, ac_request), offsetof(log_thin_t, outside_c),
            offsetof(log_thin_t, seat_heat), offsetof(log_thin_t, seat_cool), offsetof(log_thin_t, mirror_heat),
            offsetof(log_thin_t, comfort_ca), offsetof(log_thin_t, radar), offsetof(log_thin_t, keys_down),
            offsetof(log_thin_t, keys_held), offsetof(log_thin_t, acc_mean), offsetof(log_thin_t, acc_peak),
            offsetof(log_thin_t, illum_pct), offsetof(log_thin_t, page) };
        size_t at = 0; int bad = 0;
        for (int i = 0; i < LOG_CHANNELS; i++) { if (off[i] != at) { bad++; printf("  LC%02d at %zu, the record says %zu\n", i + 1, off[i], at); } at += V_LOG_CH_BYTES[i]; }
        CHECK(bad == 0, "every field of log_thin_t starts where log_channels' running sum puts it");
        CHECK(sizeof(log_full_t) == 15 && sizeof(log_header_t) == 32, "the full-log record is 15 bytes, the header 32 (D-493)");
        CHECK(LL_BAUD == V_PARAM_BAUD, "the UART runs at params radio_uart_baud");

        CHECK(strcmp(LL_UUID_SERVICE, V_LL_UUID_SERVICE) == 0 && strcmp(LL_DEVICE_NAME, V_LL_DEVICE_NAME) == 0, "LL01: service UUID and name");
        CHECK(strcmp(LL_UUID_INFO, V_LL_UUID_INFO) == 0 && strcmp(LL_UUID_DRIVES, V_LL_UUID_DRIVES) == 0 &&
              strcmp(LL_UUID_CONTROL, V_LL_UUID_CONTROL) == 0 && strcmp(LL_UUID_DATA, V_LL_UUID_DATA) == 0 &&
              strcmp(LL_UUID_STATUS, V_LL_UUID_STATUS) == 0, "LL03-LL05, LL09, LL10: the characteristic UUIDs");
        CHECK(LL_LIST == V_LL_LIST && LL_OPEN == V_LL_OPEN && LL_ACK == V_LL_ACK && LL_ABORT == V_LL_ABORT &&
              LL_SET_TIME == V_LL_SET_TIME && LL_PING == V_LL_PING && LL_CREDIT == V_LL_CREDIT, "LL06-LL08, LL12: the opcodes");
        CHECK(LL_ITEM == V_LL_ITEM && LL_DATA == V_LL_DATA && LL_END == V_LL_END && LL_INFO == V_LL_INFO &&
              LL_ERR == V_LL_ERR, "LL13: the Teensy's frame types");
        CHECK(LL_TIER_SUMMARY == V_LL_TIER_SUMMARY && LL_TIER_THIN == V_LL_TIER_THIN && LL_TIER_FULL == V_LL_TIER_FULL, "LL07: tiers");
        CHECK(LL_S_IDLE == V_LL_S_IDLE && LL_S_LISTING == V_LL_S_LISTING && LL_S_SENDING == V_LL_S_SENDING &&
              LL_S_DONE == V_LL_S_DONE && LL_S_ERROR == V_LL_S_ERROR, "LL10: states");
        CHECK(LL_E_NONE == V_LL_E_NONE && LL_E_OPCODE == V_LL_E_OPCODE && LL_E_NO_DRIVE == V_LL_E_NO_DRIVE &&
              LL_E_NO_CARD == V_LL_E_NO_CARD && LL_E_BUSY == V_LL_E_BUSY && LL_E_ABORTED == V_LL_E_ABORTED &&
              LL_E_SILENT == V_LL_E_SILENT, "LL10: errors");
        CHECK(LL_DATA_MAX == V_LL_DATA_MAX && LL_DATA_MAX + 7 == V_LL_MTU, "LL13: 240 data bytes, LL09: MTU 247 carries them whole");
        CHECK(LL_TIMEOUT_MS == V_LL_TIMEOUT_S * 1000u && LL_TIMEOUT_MS == V_LL_SILENT_S * 1000u, "LL14: 5 s timeouts");
        CHECK(LL_PAIR_WINDOW_S == V_LL_PAIR_S && LL_TIME_SLACK_S == V_LL_TIME_SLACK_S && LL_PROTOCOL == V_LL_PROTOCOL, "LL02, LL08, LL03");
        /* the added types do not collide with the record's */
        const int added[] = { LL_PAIRING, LL_START, LL_PAIR, LL_UNBOND };
        const int record[] = { LL_LIST, LL_OPEN, LL_ACK, LL_ABORT, LL_SET_TIME, LL_PING, LL_CREDIT, LL_ITEM, LL_DATA, LL_END, LL_INFO, LL_ERR };
        int clash = 0; for (int a : added) for (int r : record) clash += a == r;
        CHECK(clash == 0 && LL_E_CRC > V_LL_E_SILENT, "the frame types and error added in BT3 collide with nothing in the record");
        CHECK(LL_LINE_MAX == RADIO_LINE_MAX, "the decoder takes a $ line as long as radio_link.h allows");
    }

    /* ---------- 3. framing: encode, decode, lines between, damage ---------- */
    {
        uint8_t buf[2048]; size_t n = 0;
        ll_open_t o = { 42, LL_TIER_THIN, 1234 };
        n += ll_encode(buf + n, sizeof buf - n, LL_OPEN, &o, sizeof o);
        char line[64];
        snprintf(line, sizeof line, "$BAT,13012,3251,3252,3254,3250,07*%02X\r\n", radio_xor("BAT,13012,3251,3252,3254,3250,07", 32));
        memcpy(buf + n, line, strlen(line)); n += strlen(line);
        uint8_t d[LL_DATA_MAX]; for (unsigned i = 0; i < LL_DATA_MAX; i++) d[i] = (uint8_t)(i == 10 ? 0xAA : i == 11 ? 0x55 : i == 12 ? '$' : i == 13 ? '\n' : i);
        size_t dn = ll_encode_data(buf + n, sizeof buf - n, 7777, d, LL_DATA_MAX);
        CHECK(dn == LL_FRAME_MAX, "a full DATA frame is LL_FRAME_MAX bytes on the wire");
        n += dn;
        n += ll_encode(buf + n, sizeof buf - n, LL_PING, nullptr, 0);
        CHECK(buf[0] == LL_SYNC0 && line[0] == '$', "a frame starts 0xAA, a line '$' (LL11)");

        ll_rx_t rx; ll_rx_init(&rx);
        std::vector<int> got; std::string gl; ll_open_t o2 = {}; uint32_t doff = 0; bool dsame = false;
        for (size_t i = 0; i < n; i++) {
            int r = ll_rx_feed(&rx, buf[i]);
            if (r == LL_RX_FRAME) {
                got.push_back(ll_rx_type(&rx));
                if (ll_rx_type(&rx) == LL_OPEN) memcpy(&o2, ll_rx_payload(&rx), sizeof o2);
                if (ll_rx_type(&rx) == LL_DATA) { memcpy(&doff, ll_rx_payload(&rx), 4); dsame = ll_rx_plen(&rx) == 4 + LL_DATA_MAX && memcmp(ll_rx_payload(&rx) + 4, d, LL_DATA_MAX) == 0; }
            }
            if (r == LL_RX_LINE) { got.push_back(-1); gl = rx.line; }
        }
        CHECK(got.size() == 4 && got[0] == LL_OPEN && got[1] == -1 && got[2] == LL_DATA && got[3] == LL_PING, "frame, line, frame, frame - in order, nothing lost");
        CHECK(o2.seq == 42 && o2.tier == LL_TIER_THIN && o2.offset == 1234, "OPEN's fields round-trip");
        CHECK(doff == 7777 && dsame, "DATA's offset and 240 bytes round-trip, 0xAA 0x55 '$' and newline inside it included");
        radio_bat_t b;
        CHECK(gl.size() == 36 && radio_parse_bat(gl.c_str(), gl.size(), &b) == 1 && b.pack_mv == 13012, "the $BAT line comes out whole and radio_link.h reads it");
        CHECK(rx.bad_crc == 0 && rx.frames == 3 && rx.lines == 1, "no false CRC failure");

        /* one corrupted byte: that frame is dropped, the next one is read */
        uint8_t c[64]; size_t cn = 0;
        ll_list_t l = { 9 };
        cn += ll_encode(c + cn, sizeof c - cn, LL_LIST, &l, sizeof l);
        c[6] ^= 0x01;
        const char *noise = "xyz";
        memcpy(c + cn, noise, 3); cn += 3;
        cn += ll_encode(c + cn, sizeof c - cn, LL_LIST, &l, sizeof l);
        ll_rx_init(&rx); int frames = 0; uint32_t seen = 0;
        for (size_t i = 0; i < cn; i++) if (ll_rx_feed(&rx, c[i]) == LL_RX_FRAME) { frames++; memcpy(&seen, ll_rx_payload(&rx), 4); }
        CHECK(frames == 1 && seen == 9 && rx.bad_crc == 1, "a corrupt CRC drops the frame whole; the next frame after noise is read");

        /* a length out of range is not followed */
        uint8_t bad[] = { 0xAA, 0x55, 0xFF, 0x7F, 0x01, 0x02 };
        ll_rx_init(&rx); for (uint8_t x : bad) ll_rx_feed(&rx, x);
        cn = ll_encode(c, sizeof c, LL_PING, nullptr, 0); frames = 0;
        for (size_t i = 0; i < cn; i++) frames += ll_rx_feed(&rx, c[i]) == LL_RX_FRAME;
        CHECK(rx.bad_len == 1 && frames == 1, "a length over LL_LEN_MAX is dropped at once and the next frame is read");

        /* a line cut short by a frame */
        ll_rx_init(&rx); const char *half = "$BAT,1300"; for (const char *p = half; *p; p++) ll_rx_feed(&rx, (uint8_t)*p);
        frames = 0; for (size_t i = 0; i < cn; i++) frames += ll_rx_feed(&rx, c[i]) == LL_RX_FRAME;
        CHECK(frames == 1 && rx.lines == 0, "a line cut short by 0xAA is dropped and the frame is read");

        /* a too-long line is dropped, the next one read */
        ll_rx_init(&rx); int lines = 0;
        for (int i = 0; i < 100; i++) lines += ll_rx_feed(&rx, i == 0 ? '$' : 'A') == LL_RX_LINE;
        lines += ll_rx_feed(&rx, '\n') == LL_RX_LINE;
        for (const char *p = line; *p; p++) lines += ll_rx_feed(&rx, (uint8_t)*p) == LL_RX_LINE;
        CHECK(lines == 1 && radio_parse_bat(rx.line, strlen(rx.line), &b) == 1, "an over-long line is dropped, the next good one read");

        CHECK(ll_encode(c, sizeof c, LL_DATA, d, LL_LEN_MAX) == 0, "a payload over LL_LEN_MAX is not encoded");
        CHECK(ll_encode(c, 5, LL_PING, nullptr, 0) == 0, "nor into a buffer too small");
    }

    /* ---------- 4. the phone's control write: six opcodes and nothing else (LL05) ---------- */
    {
        uint8_t v[16] = { 0 };
        int ok = 0;
        for (int op = 0; op < 256; op++) for (size_t n = 1; n <= 12; n++) {
            v[0] = (uint8_t)op; v[5] = 1;
            if (ll_control_check(v, n) >= 0) ok++;
        }
        CHECK(ok == 6, "exactly six (opcode, length) pairs are accepted");
        uint8_t open[10] = { LL_OPEN, 1, 0, 0, 0, LL_TIER_FULL, 0, 0, 0, 0 };
        CHECK(ll_control_check(open, 10) == LL_OPEN, "OPEN with its nine bytes is accepted");
        open[5] = 3;
        CHECK(ll_control_check(open, 10) == -1, "OPEN of tier 3 is rejected");
        uint8_t cr[3] = { LL_CREDIT, 0xFF, 0xFF };
        CHECK(ll_control_check(cr, 3) == -1, "CREDIT is the radio's own - the phone cannot send it");
        uint8_t pr[2] = { LL_PAIR, 60 };
        CHECK(ll_control_check(pr, 2) == -1 && ll_control_check(nullptr, 0) == -1, "nor PAIR, nor an empty write");
        uint8_t ping2[2] = { LL_PING, 0 };
        CHECK(ll_control_check(ping2, 2) == -1, "a known opcode with the wrong length is rejected");
    }

    /* ---------- 5. SET_TIME's rule (LL08) ---------- */
    {
        CHECK(ll_time_should_set(0, 0, 1790000000u) == 1, "an unset RTC is set");
        CHECK(ll_time_should_set(1790000000u, 1, 1790000002u) == 0, "2 s apart: left alone");
        CHECK(ll_time_should_set(1790000003u, 1, 1790000000u) == 1, "3 s apart: set");
        CHECK(ll_time_should_set(1790000000u, 1, 1790000000u) == 0, "equal: left alone");
        CHECK(ll_time_should_set(1790000000u, 1, 0) == 0 && ll_time_should_set(0, 0, 0) == 0, "zero is never applied");
    }

    /* ---------- 6. the thinned record: means, peaks, latest, ORs, blanks ---------- */
    {
        LogThinAccum a;
        uint32_t t = 10000;
        for (int k = 0; k < 20; k++) {
            icu_sensors_t s = { (uint16_t)(1000 + 100 * k), (int8_t)(80 + k), 95, (uint16_t)(400 + k), 60, (uint8_t)k };
            a.on_frame(ID_ICU_SENSORS, false, (const uint8_t *)&s, 8, t + 50 * k);
        }
        for (int k = 0; k < 10; k++) {
            pmu_power_t p = { (uint16_t)(k & 1 ? 14000 : 13000), 250, 1, { 0, 0 }, 0 };
            a.on_frame(ID_PMU_POWER, false, (const uint8_t *)&p, 8, t + 100 * k);
        }
        uint8_t wb[8] = { 0x27, 0x10, 0, 0, 0, 0, 0x80, 0x00 };   /* 10000 = 1.0000 λ, big-endian, valid */
        a.on_frame(0x180, true, wb, 8, t + 10);
        wb[0] = 0x28; wb[1] = 0xA0;                                /* 10400 */
        a.on_frame(0x180, true, wb, 8, t + 20);
        wb[0] = 0xFF; wb[7] = 0x40;                                /* not valid: not in the mean */
        a.on_frame(0x180, true, wb, 8, t + 30);
        a.on_frame(0x180, false, wb, 8, t + 30);                   /* a standard 0x180 is not the wideband */
        pmu_outputs_t o = { { 0, 0 }, { 1, 2, 3 }, 3, CH_ON, 0 };
        a.on_frame(ID_PMU_OUTPUTS, false, (const uint8_t *)&o, 8, t + 100);
        o.trip_index = 5; o.trip_status = CH_TRIPPED;
        a.on_frame(ID_PMU_OUTPUTS, false, (const uint8_t *)&o, 8, t + 300);
        o.trip_index = 7; o.trip_status = CH_ON;
        a.on_frame(ID_PMU_OUTPUTS, false, (const uint8_t *)&o, 8, t + 500);
        panel_keys_t pk = { PK_DEFOG, 0, { 0, 0, 0 }, 0 };
        a.on_frame(ID_PANEL_KEYS, false, (const uint8_t *)&pk, 8, t + 100);
        pk.down = PK_FUEL_DOOR; pk.held = PK_FUEL_DOOR;
        a.on_frame(ID_PANEL_KEYS, false, (const uint8_t *)&pk, 8, t + 600);
        pmu_channel_t ch = { 4, 1234, 2000, CH_ON, 0, 0 };
        a.on_frame(ID_PMU_CHANNEL, false, (const uint8_t *)&ch, 8, t + 200);
        dcu_radar_t rd = { 3, BAND_K, 1, { 0, 0, 0, 0 }, 0 };
        a.on_frame(ID_DCU_RADAR, false, (const uint8_t *)&rd, 8, t + 200);
        a.on_imu(50, 30, 100); a.on_imu(-80, -60, 100);
        log_thin_t r; a.finish(t + 1000, 55555, 40, 2, &r);
        CHECK(r.time_ms == t + 1000 && r.odo_x10 == 55555 && r.illum_pct == 40 && r.page == 2, "time, odometer, illumination and page as given");
        CHECK(r.rpm == 1950 && r.rpm_peak == 2900, "RPM: the 1 s mean beside the 20 Hz peak (LC18, LC19)");
        CHECK(r.water_c == 99 && r.oil_cbar == 409 && r.speed_kph == 60, "the latest water temp, the mean oil pressure and speed");
        CHECK(r.batt_mv == 13500 && r.total_ca == 250 && r.charging == 1, "0x110: means and the latest flag");
        CHECK(r.lambda == 10200 && r.wb_flags == 0x80, "lambda: big-endian AEMnet, mean of the valid frames only");
        CHECK(r.trip_index == 5 && r.trip_status == CH_TRIPPED, "LC14: the last non-ok trip in the second, not the last frame's");
        CHECK(r.outputs[0] == 1 && r.outputs[2] == 3, "LC13 the outputs as the frame");
        CHECK(r.keys_down == (PK_DEFOG | PK_FUEL_DOOR) && r.keys_held == PK_FUEL_DOOR, "LC48, LC49: OR of the second");
        CHECK(r.ch_ca[4] == 1234 && r.ch_ca[0] == 0, "LC15: per-channel current by the multiplex index");
        CHECK(r.radar[0] == 3 && r.radar[1] == BAND_K, "LC47: the radar frame");
        CHECK(r.acc_mean[0] == -15 && r.acc_mean[1] == -15 && r.acc_peak[0] == 80 && r.acc_peak[1] == 30 && r.acc_peak[2] == 60,
              "LC50, LC51: IMU means and the peak lateral, acceleration, braking");
        CHECK(r.key_pos == 0 && r.pack_mv == 0 && r.cabin_c == TEMP_INVALID && r.batt_da == 0 && r.soc == 0,
              "a message never seen is blank - 0, or TEMP_INVALID for a temperature; LC34-LC36 0 (D-330)");

        a.finish(t + 1900, 55556, 40, 2, &r);   /* nothing arrived in this (short) second */
        CHECK(r.rpm == 0 && r.rpm_peak == 0 && r.batt_mv == 0 && r.keys_down == 0 && r.acc_peak[0] == 0, "a second with no samples: means and ORs are 0, not held");
        CHECK(r.water_c == 99 && r.outputs[0] == 0, "a state is held while its message is within max(timeout, 1 s) - 0x200 at 950 ms - and 0x120 at 1400 ms is not");
        CHECK(r.radar[0] == 3, "the radar is on change: its state is held");
        a.finish(t + 3500, 55557, 40, 2, &r);
        CHECK(r.water_c == TEMP_INVALID && r.outputs[0] == 0 && r.trip_status == 0 && r.ch_ca[4] == 0 && r.wb_flags == 0,
              "past its timeout a message's fields blank - never a held value (D-153)");
        rd.alert_level = 5; a.on_frame(ID_DCU_RADAR, false, (const uint8_t *)&rd, 8, t + 3600);
        rd.alert_level = 1; a.on_frame(ID_DCU_RADAR, false, (const uint8_t *)&rd, 8, t + 3700);
        a.finish(t + 4500, 0, 0, 0, &r);
        CHECK(r.radar[0] == 5, "LC47: the highest alert in the second");
        a.finish(t + 5500, 0, 0, 0, &r);
        CHECK(r.radar[0] == 1, "and the state it ended on after that");
    }

    /* ---------- 7. the card: no card, a drive, the header ---------- */
    {
        MemFs fs; fs.card = false;
        LogStore st; Host host; Sink w; LogServer sv;
        CHECK(!st.begin(&fs, 0) && !st.card, "no card: begin says so");
        CHECK(!st.start_drive(0, 0, 0), "no card: no drive, no hang");
        log_thin_t r; memset(&r, 0, sizeof r); st.add_second(r); st.tick(5000);
        sv.begin(&st, &w, &host);
        uint32_t now = 0; int err = -1;
        list(sv, w, 0, now, &err);
        CHECK(err == LL_E_NO_CARD, "LIST without a card: ERR 3");
        ll_open_t o = { 1, 1, 0 }; tx(sv, LL_OPEN, o, now);
        CHECK(last_err(w.take()) == LL_E_NO_CARD, "OPEN without a card: ERR 3");
        tx0(sv, LL_PING, now);
        auto f = w.take();
        CHECK(f.size() == 1 && f[0].type == LL_INFO && as<ll_info_t>(f[0]).card_free == 0 && as<ll_info_t>(f[0]).drive_count == 0, "INFO still answers, with no card");
    }
    {
        MemFs fs; LogStore st;
        uint32_t saved = 0;
        st.save_seq = [](uint32_t s) { (void)s; };
        CHECK(st.begin(&fs, 6), "a card: begin");
        CHECK(st.start_drive(5000, 98765, 1790000000u) && st.seq == 7, "the drive after the persisted sequence (F-007)");
        (void)saved;
        auto &th = fs.file(7, "thin.bin");
        log_header_t h; memcpy(&h, th.data(), 32);
        CHECK(th.size() == 32 && memcmp(th.data(), "RX7L", 4) == 0, "thin.bin starts with RX7L and its 32-byte header");
        CHECK(th[4] == LOG_FORMAT_VERSION && th[5] == LL_TIER_THIN, "version at 4, tier at 5");
        uint32_t u; uint16_t rl;
        memcpy(&u, &th[6], 4);  CHECK(u == 7, "sequence at 6");
        memcpy(&u, &th[10], 4); CHECK(u == 98765, "start odometer at 10");
        memcpy(&u, &th[14], 4); CHECK(u == 5000, "uptime at start at 14");
        memcpy(&u, &th[18], 4); CHECK(u == 1790000000u, "unix time at start at 18");
        memcpy(&rl, &th[22], 2); CHECK(rl == 137, "record length at 22");
        memcpy(&u, &th[24], 4); CHECK(u == log_thin_layout_crc() && u != 0, "the channel table's CRC at 24");
        CHECK(fs.file(7, "full.bin")[5] == LL_TIER_FULL && fs.file(7, "summary.bin")[5] == LL_TIER_SUMMARY, "full.bin and summary.bin carry their tiers");
        CHECK(fs.file(7, "pulled.flg").size() == 28, "pulled.flg is written, nothing pulled");

        LogThinAccum a; log_thin_t r;
        for (int s = 1; s <= 3; s++) {
            log_full_t fr = { (uint32_t)(5000 + s), 0x200, 0x80, { 1, 2, 3, 4, 5, 6, 7, 8 } };
            st.add_frame(fr);
            a.finish(5000 + 1000u * s, 98765, 0, 0, &r); st.add_second(r);
            st.tick(5000 + 1000u * s);
        }
        CHECK(fs.file(7, "thin.bin").size() == 32 + 3 * 137, "three seconds: three 137-byte records");
        CHECK(fs.file(7, "full.bin").size() == 32 + 3 * 15, "and the frames flushed with them, 15 bytes each");
        st.end_drive();
        CHECK(fs.open_handles() == 0, "key off: every file closed");
        st.start_drive(9000, 98800, 0);
        CHECK(st.seq == 8, "the next drive is 8");
        LogStore st2; MemFs &same = fs;
        CHECK(st2.begin(&same, 0) && st2.last_seq == 8, "a lost sequence (F-007 open) is found from the folders on the card");
    }

    /* ---------- 8. a whole pull: list, transfer under credit, ACK ---------- */
    {
        MemFs fs; LogStore st; Host host; Sink w; LogServer sv;
        st.begin(&fs, 0);
        drive(st, 1000, 1000, 120);       /* drive 1, 2 minutes */
        drive(st, 200000, 2000, 30);      /* drive 2, open */
        sv.begin(&st, &w, &host);
        uint32_t now = 300000;

        auto items = list(sv, w, 0, now);
        CHECK(items.size() == 2 && items[0].seq == 1 && items[1].seq == 2, "LIST 0: both drives, oldest first, seq 0 ends it");
        CHECK(items[0].thin_len == 32 + 120 * 137 && items[0].duration_s == 120 && items[0].start_odo == 1000 && items[0].pulled == 0,
              "the entry's lengths, duration (records), start odometer, nothing pulled");
        CHECK(items[0].summary_len == 32 + sizeof(log_summary_t) && items[0].full_len == 32 + 120 * 20 * 15, "summary and full lengths");
        tx0(sv, LL_PING, now);
        CHECK(as<ll_info_t>(w.take()[0]).not_pulled == 2, "INFO before any ACK: two drives not pulled");

        Pull p = pull(sv, w, 1, LL_TIER_THIN, 0, 1000, 0, now);
        auto &file = fs.file(1, "thin.bin");
        CHECK(p.ended && p.bytes == file, "the thinned log arrives whole and in order");
        CHECK(!p.over_credit && !p.gap, "never past the credit, no gap in the offsets");
        CHECK(p.total == file.size(), "START carries the tier's length");
        CHECK(p.crc == ll_crc32(file.data(), file.size()), "END carries the CRC32 of the whole tier");

        ll_ack_t ack = { 1, LL_TIER_THIN, p.crc ^ 1 };
        tx(sv, LL_ACK, ack, now);
        CHECK(last_err(w.take()) == LL_E_CRC, "ACK with a wrong CRC: ERR 7");
        items = list(sv, w, 1, now);
        CHECK(!(items[0].pulled & 2), "and pulled stays clear (D-478)");
        ack.crc32 = p.crc;
        tx(sv, LL_ACK, ack, now);
        CHECK(last_err(w.take()) == LL_E_NONE, "ACK with the right CRC: ERR 0");
        items = list(sv, w, 1, now);
        CHECK(items[0].pulled == 2, "and the thin bit of pulled.flg is set");
        CHECK(fs.file(1, "thin.bin") == file, "nothing on the card was deleted or changed");

        Pull ps = pull(sv, w, 1, LL_TIER_SUMMARY, 0, 4096, 0, now);
        ack = { 1, LL_TIER_SUMMARY, ps.crc }; tx(sv, LL_ACK, ack, now); w.take();
        items = list(sv, w, 0, now);
        CHECK(items.size() == 1 && items[0].seq == 2, "LIST 0 after summary and thin are pulled: only the open drive");
        CHECK(st.mark == 2, "the mark moves past the pulled drive");
        tx0(sv, LL_PING, now);
        auto f = w.take();
        CHECK(f.size() == 1 && as<ll_info_t>(f[0]).not_pulled == 1 && as<ll_info_t>(f[0]).drive_count == 2, "INFO: two drives, one not pulled");

        /* the open drive: acknowledged, then it grows, and is not pulled any more */
        Pull p2 = pull(sv, w, 2, LL_TIER_THIN, 0, 2000, 0, now);
        ack = { 2, LL_TIER_THIN, p2.crc }; tx(sv, LL_ACK, ack, now); w.take();
        items = list(sv, w, 2, now);
        CHECK(items[0].pulled & 2, "the open drive's thinned log, acknowledged, reads pulled");
        log_thin_t r; memset(&r, 0, sizeof r); st.add_second(r);
        items = list(sv, w, 2, now);
        CHECK(!(items[0].pulled & 2), "one more second and it is not pulled again (the app opens at its offset)");
        Pull p3 = pull(sv, w, 2, LL_TIER_THIN, (uint32_t)p2.bytes.size(), 2000, 0, now);
        std::vector<uint8_t> joined = p2.bytes; joined.insert(joined.end(), p3.bytes.begin(), p3.bytes.end());
        CHECK(p3.ended && joined == fs.file(2, "thin.bin") && p3.crc == ll_crc32(joined.data(), joined.size()),
              "the tail from the last offset, and END's CRC covers the whole tier");

        /* a summary rewritten after its ACK is not pulled any more */
        Pull s2 = pull(sv, w, 2, LL_TIER_SUMMARY, 0, 4096, 0, now);
        ack = { 2, LL_TIER_SUMMARY, s2.crc }; tx(sv, LL_ACK, ack, now); w.take();
        items = list(sv, w, 2, now);
        CHECK(items[0].pulled & 1, "the open drive's summary, acknowledged");
        log_summary_t sm; memset(&sm, 0, sizeof sm); sm.max_rpm = 7100; st.write_summary(sm);
        items = list(sv, w, 2, now);
        CHECK(!(items[0].pulled & 1), "rewritten a minute later: not pulled");
    }

    /* ---------- 9. a pull broken at an offset and resumed (D-483) ---------- */
    {
        MemFs fs; LogStore st; Host host; Sink w; LogServer sv;
        st.begin(&fs, 0);
        drive(st, 1000, 500, 300);
        st.end_drive();
        sv.begin(&st, &w, &host);
        uint32_t now = 1000000;
        auto &file = fs.file(1, "full.bin");
        Pull a = pull(sv, w, 1, LL_TIER_FULL, 0, 3000, 20000, now);
        CHECK(!a.ended && a.bytes.size() >= 20000 && a.bytes.size() < file.size(), "the pull is cut off part way");
        tx0(sv, LL_ABORT, now);
        CHECK(last_err(w.take()) == LL_E_ABORTED && sv.state == LogServer::SV_IDLE, "ABORT: ERR 5, idle");
        /* a new power cycle: no memory of the first half */
        LogServer sv2; LogStore st2; st2.begin(&fs, 0); sv2.begin(&st2, &w, &host);
        Pull b = pull(sv2, w, 1, LL_TIER_FULL, (uint32_t)a.bytes.size(), 3000, 0, now);
        std::vector<uint8_t> all = a.bytes; all.insert(all.end(), b.bytes.begin(), b.bytes.end());
        CHECK(b.ended && !b.gap && all == file, "resumed at the last contiguous byte: the two halves are the file");
        CHECK(b.crc == ll_crc32(file.data(), file.size()), "END's CRC is of the whole tier, not the second half");
        /* ACK in the next power cycle, after END in this one was lost */
        LogServer sv3; LogStore st3; st3.begin(&fs, 0); sv3.begin(&st3, &w, &host);
        ll_ack_t ack = { 1, LL_TIER_FULL, b.crc };
        tx(sv3, LL_ACK, ack, now);
        for (int i = 0; i < 1000 && sv3.state != LogServer::SV_IDLE; i++) sv3.poll(++now);
        CHECK(last_err(w.take()) == LL_E_NONE, "an ACK with no END remembered: the ICU checks the file and accepts it");
        ll_item_t it; st3.drive_item(1, &it);
        CHECK(it.pulled == 4, "full pulled; summary and thin not");
        ack.crc32 ^= 0x10; ack.tier = LL_TIER_THIN;
        tx(sv3, LL_ACK, ack, now);
        for (int i = 0; i < 1000 && sv3.state != LogServer::SV_IDLE; i++) sv3.poll(++now);
        CHECK(last_err(w.take()) == LL_E_CRC, "and refuses one that does not match");

        /* a second OPEN aborts the first */
        Pull c = pull(sv3, w, 1, LL_TIER_FULL, 0, 1000, 500, now);
        Pull d = pull(sv3, w, 1, LL_TIER_THIN, 0, 4000, 0, now);
        CHECK(c.bytes.size() >= 500 && d.ended && d.bytes == fs.file(1, "thin.bin"), "a second OPEN aborts the first and starts its own (LL07)");
        ll_open_t bad = { 1, LL_TIER_THIN, (uint32_t)fs.file(1, "thin.bin").size() + 1 };
        tx(sv3, LL_OPEN, bad, now);
        CHECK(last_err(w.take()) == LL_E_NO_DRIVE, "OPEN past the end: ERR 2");
        bad = { 99, LL_TIER_THIN, 0 }; tx(sv3, LL_OPEN, bad, now);
        CHECK(last_err(w.take()) == LL_E_NO_DRIVE, "OPEN of a drive that is not there: ERR 2");
        ll_open_t atend = { 1, LL_TIER_SUMMARY, (uint32_t)fs.file(1, "summary.bin").size() };
        tx(sv3, LL_OPEN, atend, now);
        credit(sv3, 100, now);
        for (int i = 0; i < 100; i++) sv3.poll(++now);
        auto fr = w.take();
        CHECK(fr.size() == 2 && fr[0].type == LL_START && fr[1].type == LL_END &&
              as<ll_end_t>(fr[1]).crc32 == ll_crc32(fs.file(1, "summary.bin").data(), fs.file(1, "summary.bin").size()),
              "OPEN at the very end: START, END with the whole CRC, no DATA");
    }

    /* ---------- 10. credit: none, none for 5 s, the wire full ---------- */
    {
        MemFs fs; LogStore st; Host host; Sink w; LogServer sv;
        st.begin(&fs, 0); drive(st, 1000, 0, 10); st.end_drive();
        sv.begin(&st, &w, &host);
        uint32_t now = 50000;
        ll_open_t o = { 1, LL_TIER_THIN, 0 }; tx(sv, LL_OPEN, o, now);
        for (int i = 0; i < 100; i++) sv.poll(now + (uint32_t)i);
        auto fr = w.take();
        CHECK(fr.size() == 1 && fr[0].type == LL_START, "no credit: START, and not one DATA");
        credit(sv, 100, now + 100);
        for (int i = 0; i < 100; i++) sv.poll(now + 100 + (uint32_t)i);
        fr = w.take();
        uint32_t sent = 0; for (auto &f : fr) if (f.type == LL_DATA) sent += (uint32_t)f.p.size();
        CHECK(sent <= 100 && sent > 0, "100 bytes of credit: no more than 100 bytes of DATA payload");
        sv.poll(now + 100 + 5000);
        CHECK(sv.state == LogServer::SV_SEND && w.take().empty(), "4.9 s without credit: still waiting");
        sv.poll(now + 100 + 5001);
        CHECK(sv.state == LogServer::SV_IDLE && last_err(w.take()) == LL_E_ABORTED, "5 s without CREDIT: aborted, ERR 5 (LL14)");
        tx(sv, LL_OPEN, o, now + 6000);
        w.cap = 10;
        credit(sv, 60000, now + 6000);
        for (int i = 0; i < 100; i++) sv.poll(now + 6000 + (uint32_t)i);
        CHECK(w.take().size() == 0, "the UART's buffer full: nothing is written, nothing lost");
        w.cap = 1 << 20;
        for (int i = 0; i < 100; i++) sv.poll(now + 6100 + (uint32_t)i);
        CHECK(!w.take().empty(), "and it goes on when there is room");
    }

    /* ---------- 11. SET_TIME and INFO ---------- */
    {
        MemFs fs; LogStore st; Host host; Sink w; LogServer sv;
        st.begin(&fs, 0); st.start_drive(1000, 4242, 0);
        sv.begin(&st, &w, &host);
        tx0(sv, LL_PING, 2000);
        ll_info_t i = as<ll_info_t>(w.take()[0]);
        CHECK(i.protocol == 1 && i.fw == 600 && i.odometer == 123456 && i.rtc_set == 0 && i.unix_time == 0 && i.uptime_ms == 2000 && i.card_free == 80,
              "INFO: protocol 1, firmware, odometer, the RTC unset, uptime, card free");
        ll_set_time_t t = { 1790000000u };
        tx(sv, LL_SET_TIME, t, 3000);
        auto fr = w.take();
        CHECK(host.sets == 1 && host.unix_now == 1790000000u, "SET_TIME on an unset RTC: set");
        CHECK(fr.size() == 1 && fr[0].type == LL_INFO && as<ll_info_t>(fr[0]).rtc_set == 1 && as<ll_info_t>(fr[0]).unix_time == 1790000000u, "answered with INFO, the RTC now set");
        t.unix_time = 1790000002u; tx(sv, LL_SET_TIME, t, 4000); w.take();
        CHECK(host.sets == 1, "2 s off: left alone");
        t.unix_time = 1790000010u; tx(sv, LL_SET_TIME, t, 5000); w.take();
        CHECK(host.sets == 2 && host.unix_now == 1790000010u, "10 s off: set");
        log_summary_t sm; memset(&sm, 0, sizeof sm); st.write_summary(sm);
        log_summary_t back; memcpy(&back, fs.file(1, "summary.bin").data() + 32, sizeof back);
        CHECK(back.time_set_unix == 1790000010u && back.time_set_prev == 1790000000u && back.time_set_uptime == 5000 && back.start_odo == 4242,
              "and logged in the summary: the time set, the time before, when (LL08)");
        ll_pairing_t pg = { LL_PAIR_OPEN, 123456, 60 }; tx(sv, LL_PAIRING, pg, 6000);
        CHECK(host.pair_state == LL_PAIR_OPEN && host.passkey == 123456 && w.take().empty(), "PAIRING hands the passkey to the cluster, answers nothing");
    }

    /* ---------- 12. safe by shape: only SET_TIME sets anything, only ACK writes the card ---------- */
    {
        MemFs fs; LogStore st; Host host; Sink w; LogServer sv;
        st.begin(&fs, 0); drive(st, 1000, 0, 5); st.end_drive();
        sv.begin(&st, &w, &host);
        int writes0 = fs.writes, unknown = 0, answered_err1 = 0;
        uint8_t junk[300]; for (int i = 0; i < 300; i++) junk[i] = (uint8_t)(i * 31 + 7);
        uint32_t now = 100000;
        for (int type = 0; type < 256; type++) {
            if (type == LL_ACK || type == LL_SET_TIME) continue;
            const uint16_t lens[] = { 0, 1, 2, 4, 6, 9, 13, 27, 244 };
            for (uint16_t n : lens) {
                sv.on_frame((uint8_t)type, junk, n, now);
                credit(sv, 500, now);
                for (int k = 0; k < 50; k++) sv.poll(++now);
                tx0(sv, LL_ABORT, now);
                auto fr = w.take();
                bool known = type == LL_LIST || type == LL_OPEN || type == LL_ABORT || type == LL_PING ||
                             type == LL_CREDIT || type == LL_PAIRING;
                if (!known) { unknown++; for (auto &f : fr) if (f.type == LL_ERR && f.p[0] == LL_E_OPCODE) { answered_err1++; break; } }
            }
        }
        CHECK(fs.writes == writes0, "248 frame types x 9 lengths of junk: not one byte written to the card");
        CHECK(host.sets == 0, "and the clock never set");
        CHECK(unknown > 0 && answered_err1 == unknown, "every unknown type is answered ERR 1, the switch's default");
    }

    /* ---------- 13. a card filling up: full logs go oldest first, nothing else ---------- */
    {
        MemFs fs; LogStore st;
        st.begin(&fs, 0);
        for (int d = 0; d < 4; d++) drive(st, 1000u + 100000u * d, 0, 3);
        st.end_drive();
        fs.freep = 20;
        st.start_drive(900000, 0, 0);
        CHECK(!fs.exists("/RX7/00000001/full.bin") && fs.exists("/RX7/00000001/thin.bin") && fs.exists("/RX7/00000001/summary.bin"),
              "over three-quarters full: the oldest full log goes, its summary and thinned log stay (D-493)");
        ll_item_t it; st.drive_item(1, &it);
        CHECK(it.full_len == 0 && it.thin_len > 32, "and its entry says full_len 0");
    }

    /* ---------- 14. a card that fails mid-drive ---------- */
    {
        MemFs fs; LogStore st;
        st.begin(&fs, 0); st.start_drive(0, 0, 0);
        fs.fail_writes = true;
        log_thin_t r; memset(&r, 0, sizeof r);
        st.add_second(r);
        CHECK(!st.card && st.seq == 0 && st.write_errors == 1, "a failed write: the card is given up, no retry loop");
        st.add_second(r); st.tick(10000);
        CHECK(st.write_errors == 1, "and nothing more is tried");
    }

    printf("\n passed %d   failed %d\n", passed, failed);
    if (failed) { printf(" *** LOG LINK TESTS FAILED ***\n"); return 1; }
    printf(" ALL LOG LINK TESTS PASSED\n");
    return 0;
}

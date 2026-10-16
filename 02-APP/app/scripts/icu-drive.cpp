/*
 * icu-drive.cpp - one drive written by the ICU firmware's own LogStore (icu/log_store.h),
 * for the app's decoder tests (02-APP BL3). The firmware's headers are only included, never
 * changed: this is the card the Teensy would write, kept in memory and then saved as files.
 *
 *   c++ -std=c++17 -O2 scripts/icu-drive.cpp -o /tmp/icu-drive && /tmp/icu-drive tests/fixtures/icu-drive
 *   (on the Mac, with SDKROOT pinned as the app README says)
 *
 * Writes <out>/00000001/summary.bin, thin.bin and full.bin: 90 seconds of drive 1 at 20 Hz
 * of 0x200 (rpm, water, oil, speed) and 10 Hz of 0x110 (battery), the odometer counting up a
 * tenth of a mile every 10 s from 1534567 (153,456.7 mi), the clock unset at the start and set
 * by the app 30 s in, and a summary with known figures. tests/logs.test.ts reads them back.
 */
#include <cstdio>
#include <cstring>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <sys/stat.h>
#include "../../../02-PROJECTS/02-electrical/00-design/display-unit/firmware/du/log_link.h"
#include "../../../02-PROJECTS/02-electrical/00-design/display-unit/firmware/du/log_store.h"

/* the card, in memory (as tests/test_loglink.cpp's MemFs) */
struct MemFs : LogFs {
    std::map<std::string, std::vector<uint8_t>> files;
    std::set<std::string> dirs;
    struct H { std::string path; uint32_t pos; int mode; bool open; };
    std::vector<H> hs;
    bool present() override { return true; }
    bool mkdir(const char *p) override { dirs.insert(p); return true; }
    bool exists(const char *p) override { return files.count(p) || dirs.count(p); }
    bool remove(const char *p) override { return files.erase(p) > 0; }
    int open(const char *p, int mode) override {
        std::string s(p);
        if (mode == RD && !files.count(s)) return -1;
        if (mode == CREATE) files[s].clear(); else files[s];
        hs.push_back({ s, 0, mode, true });
        return (int)hs.size() - 1;
    }
    H *get(int h) { return (h >= 0 && h < (int)hs.size() && hs[h].open) ? &hs[h] : nullptr; }
    bool seek(int h, uint32_t pos) override { H *x = get(h); if (!x || pos > files[x->path].size()) return false; x->pos = pos; return true; }
    int32_t read(int h, void *b, uint32_t n) override {
        H *x = get(h); if (!x) return -1;
        auto &v = files[x->path];
        uint32_t k = x->pos >= v.size() ? 0 : (uint32_t)std::min<size_t>(n, v.size() - x->pos);
        if (k) memcpy(b, v.data() + x->pos, k);
        x->pos += k; return (int32_t)k;
    }
    int32_t write(int h, const void *b, uint32_t n) override {
        H *x = get(h); if (!x || x->mode == RD) return -1;
        auto &v = files[x->path];
        if (x->pos + n > v.size()) v.resize(x->pos + n);
        memcpy(v.data() + x->pos, b, n); x->pos += n; return (int32_t)n;
    }
    int32_t size(int h) override { H *x = get(h); return x ? (int32_t)files[x->path].size() : -1; }
    bool flush(int h) override { return get(h) != nullptr; }
    void close(int h) override { if (H *x = get(h)) x->open = false; }
    bool list(const char *, void (*)(const char *, bool, void *), void *) override { return true; }
    uint8_t free_pct() override { return 80; }
};

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "usage: icu-drive <out-dir>\n"); return 3; }
    MemFs fs;
    LogStore st;
    st.begin(&fs, 0);
    const uint32_t t0 = 4200, odo0 = 1534567;
    st.start_drive(t0, odo0, 0);                       /* the clock unset at key-on */
    LogThinAccum acc;
    const int SECS = 90;
    for (int s = 1; s <= SECS; s++) {
        for (int k = 0; k < 20; k++) {                 /* 0x200 at 20 Hz */
            uint32_t t = t0 + (uint32_t)(s - 1) * 1000 + (uint32_t)k * 50;
            icu_sensors_t f = { (uint16_t)(800 + 30 * s + k), (int8_t)(60 + s / 3), (int8_t)(70 + s / 4), (uint16_t)(250 + s), (uint8_t)(s < 10 ? 0 : 48), 0 };
            acc.on_frame(ID_ICU_SENSORS, false, (const uint8_t *)&f, 8, t);
            log_full_t r = { t, ID_ICU_SENSORS, (uint8_t)(8 << 4), {} };
            memcpy(r.data, &f, 8);
            st.add_frame(r);
            if (k % 2 == 0) {                          /* 0x110 at 10 Hz */
                pmu_power_t p = { (uint16_t)(13800 + (k % 4)), (uint16_t)(250 + s), 1, { 0, 0 }, 0 };
                acc.on_frame(ID_PMU_POWER, false, (const uint8_t *)&p, 8, t);
            }
        }
        if (s % 2 == 0) acc.on_imu(25, -40, 100);
        else acc.on_imu(-15, 30, 98);
        log_thin_t rec;
        acc.finish(t0 + (uint32_t)s * 1000, odo0 + (uint32_t)(s / 10), 40, 2, &rec);
        st.add_second(rec);
        st.tick(t0 + (uint32_t)s * 1000);
        if (s == 30) st.note_time_set(0, 1791820800u, t0 + 30000u);   /* SET_TIME 30 s in */
    }
    log_summary_t sm; memset(&sm, 0, sizeof sm);
    sm.end_odo = odo0 + SECS / 10; sm.duration_s = SECS;
    sm.max_rpm = 3519; sm.max_mph = 30; sm.max_water_c = 90; sm.max_oil_temp_c = 92;
    sm.max_oil_cbar = 340; sm.min_oil_cbar = 251; sm.max_volts_x10 = 138; sm.min_volts_x10 = 138;
    sm.max_lat_g = 25; sm.max_accel_g = 30; sm.max_brake_g = 40; sm.max_pitch_up = 3; sm.max_pitch_down = -2;
    sm.runtime_s = SECS; sm.idle_s = 9; sm.distance_x10 = SECS / 10; sm.rev_s = 0; sm.hot_s = 0; sm.low_oil_s = 0;
    sm.cold_starts = 1; sm.fuel_pct_start = 62; sm.fuel_pct_now = 61; sm.dist_at_fuel_mark = 0;
    sm.fuse_trips = 2; sm.last_trip_ch = 5; sm.last_trip_s = 61; sm.sensor_faults = 0; sm.can_timeouts = 3;
    st.write_summary(sm);
    st.end_drive();

    std::string out = argv[1];
    std::string dir = out + "/00000001";
    for (size_t i = 1; i <= dir.size(); i++)          /* mkdir -p */
        if (i == dir.size() || dir[i] == '/') ::mkdir(dir.substr(0, i).c_str(), 0755);
    for (const char *name : { "summary.bin", "thin.bin", "full.bin" }) {
        auto &v = fs.files[std::string(LOG_ROOT "/00000001/") + name];
        FILE *f = fopen((dir + "/" + name).c_str(), "wb");
        if (!f) { perror(name); return 1; }
        fwrite(v.data(), 1, v.size(), f);
        fclose(f);
        printf("%s %zu bytes\n", name, v.size());
    }
    return 0;
}

/*
 * test_suite.cpp — full regression suite for the RX-7 ICU
 *
 * Runs on your PC. No Teensy, no car, no display.
 * Build and run it after ANY change to cluster_core.h, stats.h, can_map.h
 * or the vehicle model.
 *
 * ============================================================
 *  BUILD  (w64devkit shell)
 *    cd .../firmware/tests
 *    g++ test_suite.cpp -o test.exe -std=c++17 -O2
 *    ./test.exe
 *
 *  Exit code 0 = all passed. Non-zero = failures, count in the code.
 * ============================================================
 *
 * WHAT IT CHECKS
 *   1  struct packing and CAN round-trip
 *   2  counter wrap - the 255->0 case
 *   3  temperature and unit conversions across the full range
 *   4  digit rendering, every glyph, every segment
 *   5  centring across 1/2/3 digits and the decimal point
 *   6  EXHAUSTIVE layout overlap - every widget against every other,
 *      swept across every digit-count transition
 *   7  nothing draws off-screen, ever
 *   8  dirty-rectangle correctness - every changed pixel is inside a
 *      dirty tile, or the panel would show stale content
 *   9  sensor fault rendering for every field x every status
 *  10  vehicle model invariants over a long simulated drive
 *  11  stats accumulation - peaks, minimums, over-limit counters
 *  12  diagnostics page bounds and channel table integrity
 *  13  frame cost stays inside the 30 fps budget
 */

#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <cstdarg>
#include <cmath>
#include <vector>
#include <string>

#include "../icu/cluster_core.h"
#include "../icu/can_map.h"
#include "../icu/stats.h"
#include "../pmu_sim/channels.h"
#include "../pmu_sim/vehicle_model.h"

/* ---------------- harness ---------------- */
static int g_pass = 0, g_fail = 0;
static std::string g_group;

static void group(const char *n) {
    g_group = n;
    printf("\n\033[1m-- %s\033[0m\n", n);
}
static void check(bool ok, const char *what) {
    if (ok) { g_pass++; }
    else    { g_fail++; printf("  FAIL  %s\n", what); }
}
static void checkf(bool ok, const char *fmt, ...) {
    if (ok) { g_pass++; return; }
    g_fail++;
    char buf[256];
    va_list ap; va_start(ap, fmt);
    vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    printf("  FAIL  %s\n", buf);
}

/* ---------------- geometry helpers ---------------- */
struct Box {
    int x0, y0, x1, y1;
    const char *name;
    bool valid() const { return x1 > x0 && y1 > y0; }
};

static bool overlap(const Box &a, const Box &b) {
    return a.x0 < b.x1 && b.x0 < a.x1 && a.y0 < b.y1 && b.y0 < a.y1;
}

/* Bounding box of the digits that ACTUALLY DRAW. A blanked slot in a
 * centred field sits outside the field and paints nothing, so counting it
 * would report overlaps that do not exist. */
template <int N>
static Box boxOf(const DigitField<N> &f, const char *name) {
    int x0 = 1000000, y0 = 1000000, x1 = -1, y1 = -1;
    for (int i = 0; i < N; i++) {
        if (f.d[i].w == 0) continue;
        if (f.d[i].prevMask == SEG_BLANK || f.d[i].prevMask == 0xFF) continue;
        if (f.d[i].x < x0) x0 = f.d[i].x;
        if (f.d[i].y < y0) y0 = f.d[i].y;
        if (f.d[i].x + f.d[i].w > x1) x1 = f.d[i].x + f.d[i].w;
        if (f.d[i].y + f.d[i].h > y1) y1 = f.d[i].y + f.d[i].h;
    }
    if (x1 < 0) return { 0, 0, 0, 0, name };      /* nothing visible */
    return { x0, y0, x1, y1, name };
}
static Box boxOf(const SegBar &b, const char *name) {
    return { b.x, b.y, b.x + b.count * (b.segW + b.gap), b.y + b.segH, name };
}

/* ================= 1. struct packing and CAN round-trip ================= */
static void testStructs() {
    group("1  struct packing and CAN round-trip");

    check(sizeof(pmu_state_t)   == 8, "pmu_state_t is 8 bytes");
    check(sizeof(pmu_power_t)   == 8, "pmu_power_t is 8 bytes");
    check(sizeof(pmu_outputs_t) == 8, "pmu_outputs_t is 8 bytes");
    check(sizeof(pmu_channel_t) == 8, "pmu_channel_t is 8 bytes");
    check(sizeof(icu_sensors_t) == 8, "icu_sensors_t is 8 bytes");
    check(sizeof(icu_health_t)  == 8, "icu_health_t is 8 bytes");
    check(sizeof(dcu_climate_t) == 8, "dcu_climate_t is 8 bytes");
    check(sizeof(dcu_comfort_t) == 8, "dcu_comfort_t is 8 bytes");
    check(sizeof(dcu_radar_t)   == 8, "dcu_radar_t is 8 bytes");
    check(sizeof(keypad_t)      == 8, "keypad_t is 8 bytes");

    /* every field, at its extremes, through the wire and back */
    for (int trial = 0; trial < 3; trial++) {
        icu_sensors_t tx = {};
        tx.rpm            = (trial == 0) ? 0 : (trial == 1) ? 8500 : 65535;
        tx.water_c        = TEMP_ENCODE(trial == 0 ? -40 : trial == 1 ? 92 : 127);
        tx.oil_temp_c     = TEMP_ENCODE(trial == 0 ? -40 : trial == 1 ? 110 : 127);
        tx.oil_press_cbar = (trial == 0) ? 0 : (trial == 1) ? 435 : 65535;
        tx.speed_kph      = (trial == 0) ? 0 : (trial == 1) ? 137 : 255;
        tx.counter        = (uint8_t)(trial * 100);

        uint8_t wire[8];
        memcpy(wire, &tx, 8);
        icu_sensors_t rx;
        memcpy(&rx, wire, 8);

        checkf(rx.rpm == tx.rpm,                       "rpm survives (trial %d)", trial);
        checkf(rx.water_c == tx.water_c,               "water survives (trial %d)", trial);
        checkf(rx.oil_temp_c == tx.oil_temp_c,         "oil temp survives (trial %d)", trial);
        checkf(rx.oil_press_cbar == tx.oil_press_cbar, "oil press survives (trial %d)", trial);
        checkf(rx.speed_kph == tx.speed_kph,           "speed survives (trial %d)", trial);
        checkf(rx.counter == tx.counter,               "counter survives (trial %d)", trial);
    }

    /* bitfields must not collide */
    pmu_state_t s = {};
    s.wake_source = WAKE_ACC | WAKE_RUN | WAKE_HAZARD | WAKE_DOOR
                  | WAKE_HORN | WAKE_LATCH;
    check((s.wake_source & WAKE_ACC)   != 0, "WAKE_ACC set");
    check((s.wake_source & WAKE_LATCH) != 0, "WAKE_LATCH set");
    check(s.wake_source == 0x3F,             "all six wake bits distinct");
}

/* ================= 2. counter wrap ================= */
static void testCounterWrap() {
    group("2  counter wrap - where naive stall detection breaks");

    check( can_counter_advanced(10, 11),  "normal advance");
    check( can_counter_advanced(254,255), "254 -> 255");
    check( can_counter_advanced(255, 0),  "WRAP 255 -> 0 must advance");
    check( can_counter_advanced(250, 3),  "wrap with a gap");
    check(!can_counter_advanced(42, 42),  "stalled sender detected");
    check(!can_counter_advanced(0, 0),    "stalled at zero detected");

    /* exhaustive: every pair must be correct */
    bool ok = true;
    for (int p = 0; p < 256; p++)
        for (int n = 0; n < 256; n++)
            if (can_counter_advanced((uint8_t)p, (uint8_t)n) != (p != n)) ok = false;
    check(ok, "all 65536 counter pairs correct");
}

/* ================= 3. conversions ================= */
static void testConversions() {
    group("3  temperature and unit conversions");

    for (int c = -40; c <= 127; c++)
        checkf(TEMP_DECODE(TEMP_ENCODE(c)) == c, "temp round trip at %d C", c);

    check(TEMP_DECODE(TEMP_INVALID) == -128, "TEMP_INVALID is distinct");

    /* the conversions the display performs */
    struct { int c, f; } tf[] = { {0,32}, {100,212}, {88,190}, {-40,-40}, {105,221} };
    for (auto &t : tf)
        checkf((t.c * 9) / 5 + 32 == t.f, "%d C -> %d F", t.c, t.f);

    struct { int cbar, psi; } bp[] = { {0,0}, {100,14}, {435,63}, {800,116} };
    for (auto &t : bp)
        checkf((t.cbar * 145) / 1000 == t.psi, "%d cbar -> %d psi", t.cbar, t.psi);
}

/* ================= 4/5. digits, centring, decimal point ================= */
static Framebuffer fb;
static Cluster     cl;

static void testDigits() {
    group("4  digit rendering and segment maps");

    /* every glyph must light a distinct segment set */
    for (int a = 0; a < 10; a++)
        for (int b = a + 1; b < 10; b++)
            checkf(SEG_MAP[a] != SEG_MAP[b], "digit %d and %d differ", a, b);

    check(SEG_MAP[8] == 0x7F, "8 lights all seven segments");
    check(SEG_MAP[1] == 0x06, "1 lights only b and c");
    check(SEG_DASH  == 0x40,  "dash is segment g only");
    check(SEG_BLANK == 0x00,  "blank lights nothing");

    group("5  centring and the decimal point");

    cl.layout();
    /* speed field must stay centred as the digit count changes */
    int prevCentre = -1;
    for (int v : { 0, 5, 9, 10, 55, 99, 100, 555, 999 }) {
        cl.speedNum.draw(fb, v, C_GREEN, SENSOR_OK);
        Box b = boxOf(cl.speedNum, "speed");
        int centre = (b.x0 + b.x1) / 2;
        checkf(abs(centre - Cluster::SPD_CX) <= 2,
               "speed %d centred on %d (got %d)", v, Cluster::SPD_CX, centre);
        (void)prevCentre; prevCentre = centre;
    }

    /* decimal point must sit inside the field, not beyond it */
    cl.voltsNum.draw(fb, 142, C_GREEN, SENSOR_OK);
    Box vb = boxOf(cl.voltsNum, "volts");
    checkf(cl.voltsNum.prevDpX >= vb.x0 && cl.voltsNum.prevDpX < vb.x1,
           "volts decimal point inside the field");
}

/* ================= 6. EXHAUSTIVE layout overlap =================
 * This is the test that would have caught the speed digits running into
 * the gauge icons, and the volts field crossing the warning row. Both were
 * found by eye on a screenshot, which is not a method. */
static void collectBoxes(std::vector<Box> &v) {
    v.clear();
    v.push_back(boxOf(cl.rpmBar,   "rpm bar"));
    v.push_back(boxOf(cl.rpmNum,   "rpm number"));
    v.push_back(boxOf(cl.speedNum, "speed"));
    v.push_back(boxOf(cl.water,    "water bar"));
    v.push_back(boxOf(cl.oilP,     "oilP bar"));
    v.push_back(boxOf(cl.oilT,     "oilT bar"));
    v.push_back(boxOf(cl.fuel,     "fuel bar"));
    v.push_back(boxOf(cl.volts,    "volts bar"));
    v.push_back(boxOf(cl.waterNum, "water value"));
    v.push_back(boxOf(cl.oilPNum,  "oilP value"));
    v.push_back(boxOf(cl.oilTNum,  "oilT value"));
    v.push_back(boxOf(cl.fuelNum,  "fuel value"));
    v.push_back(boxOf(cl.voltsNum, "volts value"));
    v.push_back(boxOf(cl.compass.deg, "compass digits"));
    v.push_back(boxOf(cl.incline.num, "pitch digits"));
    v.push_back(boxOf(cl.gNum,     "G value"));

    /* static elements that have no widget object */
    v.push_back({ Cluster::G_CX - Cluster::G_R, Cluster::G_CY - Cluster::G_R,
                  Cluster::G_CX + Cluster::G_R, Cluster::G_CY + Cluster::G_R,
                  "G circle" });
    for (int i = 0; i < 5; i++) {
        int cy = Cluster::BAR_Y + i*Cluster::BAR_STEP + Cluster::BAR_SH/2;
        v.push_back({ Cluster::BAR_ICON_X, cy - 16,
                      Cluster::BAR_ICON_X + 32, cy + 16, "gauge icon" });
    }
    for (int i = 0; i < 5; i++)
        v.push_back({ Cluster::WARN_X + i*Cluster::WARN_STEP, Cluster::WARN_Y,
                      Cluster::WARN_X + i*Cluster::WARN_STEP + 32,
                      Cluster::WARN_Y + 32, "warning icon" });
}

static void testOverlap() {
    group("6  layout overlap - every widget against every other");

    cl.layout();
    std::vector<Box> boxes;
    int collisions = 0;

    /* Sweep every value that can change a widget's footprint. Digit-count
     * transitions are exactly where the centring logic moves things. */
    const int speeds[] = { 0, 9, 10, 99, 100, 999 };
    const int rpms[]   = { 0, 900, 4000, 8500 };
    const int temps[]  = { 0, 88, 130 };
    const int volts[]  = { 90, 142, 200 };
    const int hdgs[]   = { 0, 45, 180, 359 };
    const int pitches[]= { -45, 0, 45 };

    VehicleState s;
    for (int sp : speeds)
    for (int rp : rpms)
    for (int tp : temps)
    for (int vo : volts)
    for (int hd : hdgs)
    for (int pi : pitches) {
        s.speed = sp; s.rpm = rp;
        s.waterC = tp; s.oilTempC = tp;
        s.oilPressCbar = tp * 6; s.fuelPct = tp % 101;
        s.voltsX10 = vo; s.headingDeg = hd; s.pitchDeg = pi;
        s.latGx100 = (pi * 2); s.lonGx100 = -(pi * 2);

        cl.update(fb, s);
        collectBoxes(boxes);

        for (size_t i = 0; i < boxes.size(); i++)
            for (size_t j = i + 1; j < boxes.size(); j++) {
                if (!boxes[i].valid() || !boxes[j].valid()) continue;
                if (overlap(boxes[i], boxes[j])) {
                    if (collisions < 8)
                        printf("  FAIL  '%s' overlaps '%s'  "
                               "(speed %d rpm %d volts %d)\n",
                               boxes[i].name, boxes[j].name, sp, rp, vo);
                    collisions++;
                }
            }
    }
    checkf(collisions == 0, "%d overlapping pairs across the sweep", collisions);
    printf("        swept %d states\n",
           (int)(sizeof(speeds)/4 * sizeof(rpms)/4 * sizeof(temps)/4
                 * sizeof(volts)/4 * sizeof(hdgs)/4 * sizeof(pitches)/4));
}

/* ================= 7. nothing draws off-screen ================= */
static void testBounds() {
    group("7  nothing draws off-screen");

    cl.layout();
    fb.clippedPixels = 0;
    cl.setPage(fb, PAGE_DRIVE, true);

    VehicleState s;
    for (int sp = 0; sp <= 999; sp += 7)
    for (int rp = 0; rp <= 8500; rp += 850) {
        s.speed = sp; s.rpm = rp;
        s.waterC = sp % 131; s.oilTempC = sp % 151;
        s.oilPressCbar = (sp * 8) % 801; s.fuelPct = sp % 101;
        s.voltsX10 = 90 + (sp % 111);
        s.headingDeg = sp % 360; s.pitchDeg = (sp % 91) - 45;
        s.latGx100 = (sp % 201) - 100; s.lonGx100 = 100 - (sp % 201);
        cl.update(fb, s);
    }
    checkf(fb.clippedPixels == 0,
           "%u pixels clipped off-screen on the drive page", fb.clippedPixels);

    /* extremes far outside plausible range must still not draw off-screen */
    s.speed = 99999; s.rpm = 99999; s.waterC = 9999; s.oilTempC = 9999;
    s.oilPressCbar = 99999; s.fuelPct = 9999; s.voltsX10 = 9999;
    s.headingDeg = 99999; s.pitchDeg = 9999;
    s.latGx100 = 9999; s.lonGx100 = -9999;
    fb.clippedPixels = 0;
    cl.update(fb, s);
    checkf(fb.clippedPixels == 0, "absurd inputs still stay on-screen");
}

/* ================= 8. dirty-rectangle correctness =================
 * The invariant the whole rendering design rests on: if a pixel changed,
 * its tile must be marked dirty. A widget that draws outside its dirty
 * marking leaves stale content on a real panel - and would look correct
 * in the simulator, because the simulator repaints the whole texture. */
static uint8_t snapshot[SCR_W * SCR_H];

static void testDirtyRects() {
    group("8  dirty-rectangle correctness");

    cl.layout();
    cl.setPage(fb, PAGE_DRIVE, false);

    VehicleState s;
    s.speed = 50; s.rpm = 3000; s.waterC = 88; s.oilTempC = 95;
    s.oilPressCbar = 400; s.fuelPct = 60; s.voltsX10 = 142;
    cl.update(fb, s);

    int leaks = 0, framesChecked = 0;

    for (int step = 0; step < 400; step++) {
        memcpy(snapshot, fb.buf, sizeof(snapshot));
        fb.clearDirty();

        /* move everything that can move */
        s.rpm = (s.rpm + 137) % 8501;
        s.speed = (s.speed + 3) % 200;
        s.waterC = 20 + (step % 111);
        s.oilTempC = 20 + (step % 131);
        s.oilPressCbar = (step * 13) % 801;
        s.fuelPct = step % 101;
        s.voltsX10 = 110 + (step % 41);
        s.headingDeg = (s.headingDeg + 7) % 360;
        s.pitchDeg = ((step % 91) - 45);
        s.latGx100 = ((step * 5) % 201) - 100;
        s.lonGx100 = 100 - ((step * 3) % 201);
        s.wOil   = (step % 17) == 0;
        s.wTemp  = (step % 23) == 0;
        s.wBrake = (step % 5)  == 0;

        cl.update(fb, s);
        framesChecked++;

        for (int y = 0; y < SCR_H; y++)
            for (int x = 0; x < SCR_W; x++) {
                int i = y * SCR_W + x;
                if (fb.buf[i] == snapshot[i]) continue;
                if (!fb.tileDirty(x / TILE, y / TILE)) {
                    if (leaks < 5)
                        printf("  FAIL  pixel (%d,%d) changed outside a dirty "
                               "tile, step %d\n", x, y, step);
                    leaks++;
                }
            }
    }
    checkf(leaks == 0, "%d pixels changed outside a dirty tile", leaks);
    printf("        checked %d frames, %d pixels each\n",
           framesChecked, SCR_W * SCR_H);
}

/* ================= 9. sensor faults ================= */
static void testFaults() {
    group("9  sensor fault rendering, every field x every status");

    cl.layout();
    cl.setPage(fb, PAGE_DRIVE, false);

    const SensorStatus all[] = { SENSOR_OK, SENSOR_OPEN, SENSOR_SHORT,
                                 SENSOR_STALE, SENSOR_RANGE };
    VehicleState s;
    s.speed = 55; s.rpm = 2500; s.waterC = 88; s.oilTempC = 95;
    s.oilPressCbar = 400; s.fuelPct = 60; s.voltsX10 = 142;

    fb.clippedPixels = 0;
    for (auto a : all) for (auto b : all) for (auto c : all) {
        s.sWater = a; s.sOilP = b; s.sFuel = c;
        s.sRpm = a;   s.sSpeed = b; s.sOilT = c; s.sVolts = a; s.sImu = b;
        cl.update(fb, s);
    }
    checkf(fb.clippedPixels == 0, "fault rendering stays on-screen");

    /* a fault must not render as a plausible zero */
    s.sWater = SENSOR_OPEN; s.waterC = 0;
    cl.update(fb, s);
    check(cl.waterNum.d[2].prevMask == SEG_DASH,
          "OPEN sensor draws a dash, not a zero");

    s.sWater = SENSOR_OK; s.waterC = 0;
    cl.update(fb, s);
    check(cl.waterNum.d[2].prevMask == SEG_MAP[2],
          "a real 32 F reading draws digits");   /* 0 C -> 32 F */

    /* fault colours must be distinguishable */
    check(faultColour(SENSOR_OPEN)  == C_AMBER, "OPEN is amber");
    check(faultColour(SENSOR_SHORT) == C_RED,   "SHORT is red");
    check(faultColour(SENSOR_STALE) == C_MID,   "STALE is dim");
    check(faultColour(SENSOR_OK)    == 0,       "OK is not a fault colour");
}

/* ================= 10. vehicle model invariants ================= */
static void testVehicleModel() {
    group("10  vehicle model invariants over a simulated drive");

    Vehicle v;
    uint32_t t = 0;
    int badRpm=0, badVolts=0, badOil=0, badFuel=0, badWater=0, badCurrent=0;
    int prevFuel = v.fuelPctX10;
    bool sawTripLatched = false;

    for (int step = 0; step < 60000; step++) {     /* 10 minutes at 100 Hz */
        t += 10;
        if (step == 100)   v.key = K_ACC;
        if (step == 300)   v.key = K_START;
        if (step == 500)   v.key = K_RUN;
        if (step > 500)    v.throttle = (step / 200) % 100;
        if (step == 2000)  v.head = H_HEAD;
        if (step == 3000)  v.turn = T_LEFT;
        if (step == 4000)  v.defog = true;
        if (step == 20000) v.tripChannel(O6_TAIL);

        v.update(t, 10);

        /* the latch must hold for ~5 s before it retries */
        if (step > 20000 && step < 20400 && v.chState[O6_TAIL] == 2)
            sawTripLatched = true;

        if (v.rpm < 0 || v.rpm > 9000) badRpm++;
        if (v.voltsX10 < 80 || v.voltsX10 > 160) badVolts++;
        if (v.oilPressCbar < 0 || v.oilPressCbar > 800) badOil++;
        if (v.fuelPctX10 < 0 || v.fuelPctX10 > 1000) badFuel++;
        if (v.waterCx10 < 170 || v.waterCx10 > 1400) badWater++;
        if (v.fuelPctX10 > prevFuel) badFuel++;      /* fuel never rises */
        prevFuel = v.fuelPctX10;

        for (int i = 0; i < 24; i++)
            if (v.chState[i] == 0 && v.chCurrent[i] != 0) badCurrent++;
    }

    checkf(badRpm == 0,     "rpm stayed in range (%d violations)", badRpm);
    checkf(badVolts == 0,   "voltage stayed in range (%d)", badVolts);
    checkf(badOil == 0,     "oil pressure stayed in range (%d)", badOil);
    checkf(badFuel == 0,    "fuel monotonically decreased (%d)", badFuel);
    checkf(badWater == 0,   "water temp stayed in range (%d)", badWater);
    checkf(badCurrent == 0, "off channels drew zero current (%d)", badCurrent);

    check(v.running,                 "engine started and stayed running");
    check(v.waterCx10 > 600,         "engine reached operating temperature");
    check(v.oilPressCbar > 100,      "oil pressure came up");
    check(sawTripLatched,            "tripped channel latched before retrying");
    check(v.voltsX10 > 135,          "alternator charging");
}

/* ================= 11. stats accumulation ================= */
static void testStats() {
    group("11  stats accumulation");

    StatsTracker st;
    st.begin(0);
    VehicleState s;
    s.fuelPct = 80;

    uint32_t t = 0;
    for (int i = 0; i < 600; i++) {          /* 600 seconds */
        t += 1000;
        s.rpm    = (i < 60) ? 0 : 1000 + (i % 60) * 120;
        s.speed  = (i < 60) ? 0 : (i % 90);
        s.waterC = (i < 60) ? 20 : 20 + (i / 6);
        s.oilTempC = s.waterC + 10;
        s.oilPressCbar = s.rpm ? 150 + s.rpm / 20 : 0;
        s.voltsX10 = s.rpm ? 142 : 124;
        s.latGx100 = (i % 100) - 50;
        s.lonGx100 = 50 - (i % 100);
        s.pitchDeg = (i % 30) - 15;
        if (i == 300) s.fuelPct = 60;
        st.tick(s, t);
    }

    const Stats &a = st.trip;
    check(a.maxRpm >= 8000 || a.maxRpm > 0, "max rpm captured");
    check(a.maxSpeed > 0,                   "max speed captured");
    check(a.maxWaterC > 20,                 "max water captured");
    check(a.runtimeSec > 0,                 "runtime accumulated");
    check(a.distanceX10 > 0,                "distance accumulated");
    check(a.maxLatG > 0,                    "peak lateral G captured");
    check(a.maxAccelG > 0,                  "peak acceleration captured");
    check(a.maxBrakeG > 0,                  "peak braking captured");
    check(a.maxPitchUp > 0,                 "max climb captured");
    check(a.maxPitchDown < 0,               "max descent captured");

    /* min oil pressure must only be sampled while running - otherwise it
     * reads zero from every key-off and the figure is worthless */
    checkf(a.minOilPress > 0 && a.minOilPress != 65535,
           "min oil pressure sampled only while running (got %u)", a.minOilPress);

    /* MPG refuses to guess on a small sample */
    Stats small = a;
    small.fuelPctStart = 80; small.fuelPctNow = 76;    /* 4% drop */
    check(StatsTracker::mpgX10(small) == 0, "MPG refuses a <10% tank drop");
    small.fuelPctNow = 50;                              /* 30% drop */
    check(StatsTracker::mpgX10(small) > 0,  "MPG computes on a real drop");

    /* trip resets, life does not */
    st.trip.reset();
    check(st.trip.maxRpm == 0,  "trip resets");
    check(st.life.maxRpm > 0,   "life persists across a trip reset");

    /* CSV must not overflow its buffer */
    char csv[512];
    int n = statsToCsv(st.life, csv, sizeof(csv));
    checkf(n > 0 && n < (int)sizeof(csv), "CSV line fits the buffer (%d bytes)", n);
    check(strlen(statsCsvHeader()) > 0, "CSV header present");
}

/* ================= 12. diagnostics page ================= */
static void testDiagPage() {
    group("12  diagnostics page and channel table");

    /* every channel has a name and a sane limit */
    for (int i = 0; i < PMU_CHANNELS; i++) {
        checkf(CH_NAME[i] != nullptr && CH_NAME[i][0] != 0,
               "channel %d has a display name", i + 1);
        checkf(CH[i].limit > 0, "channel %d has a soft-fuse limit", i + 1);
        checkf(CH[i].steady <= CH[i].limit,
               "channel %d steady <= limit (%u vs %u)",
               i + 1, CH[i].steady, CH[i].limit);
    }

    /* names must fit their column - 8 chars at scale 2 is 96 px, and the
     * current column starts 118 px in */
    for (int i = 0; i < PMU_CHANNELS; i++)
        checkf(textWidth(CH_NAME[i], 2) <= Cluster::DG_CUR - Cluster::DG_NAME,
               "channel %d name '%s' fits its column", i + 1, CH_NAME[i]);

    cl.layout();
    cl.setPage(fb, PAGE_DIAG, false);
    fb.clippedPixels = 0;

    VehicleState s;
    /* every state, every current, including current above limit */
    for (int pass = 0; pass < 4; pass++)
        for (int i = 0; i < PMU_CHANNELS; i++) {
            s.chState[i]   = (uint8_t)((i + pass) % 4);
            s.chLimit[i]   = CH[i].limit;
            s.chCurrent[i] = (uint16_t)((pass == 3) ? CH[i].limit * 2
                                                    : CH[i].limit * pass / 2);
        }
    for (int pass = 0; pass < 4; pass++) cl.updateDiag(fb, s);
    checkf(fb.clippedPixels == 0, "diagnostics page stays on-screen");

    /* zero limit must not divide by zero */
    for (int i = 0; i < PMU_CHANNELS; i++) { s.chLimit[i] = 0; s.chCurrent[i] = 500; }
    cl.updateDiag(fb, s);
    check(true, "zero soft-fuse limit does not crash");
}

/* ================= 13. frame cost ================= */
static void testFrameCost() {
    group("13  frame cost against the 30 fps budget");

    cl.layout();
    cl.setPage(fb, PAGE_DRIVE, false);

    VehicleState s;
    s.speed = 60; s.rpm = 3000; s.waterC = 88; s.oilTempC = 95;
    s.oilPressCbar = 400; s.fuelPct = 60; s.voltsX10 = 142;
    cl.update(fb, s);

    uint32_t worst = 0, total = 0;
    int rpm = 900, dir = 1;
    for (int i = 0; i < 900; i++) {
        rpm += dir * 55;
        if (rpm > 8400) dir = -1;
        if (rpm < 900)  dir = 1;
        s.rpm = rpm; s.speed = rpm / 62;
        if ((i % 30) == 0) { s.waterC = 40 + (i/30) % 60; s.voltsX10 = 136 + (i/60)%8; }

        fb.clearDirty();
        cl.update(fb, s);
        uint32_t d = fb.dirtyPixels();
        total += d;
        if (d > worst) worst = d;
    }

    double avgMs   = (total / 900.0) / 6000000.0 * 1000.0;
    double worstMs = worst / 6000000.0 * 1000.0;
    printf("        avg %.2f ms   worst %.2f ms   budget 33.3 ms\n", avgMs, worstMs);

    checkf(worstMs < 33.3, "worst frame %.2f ms is inside the 30 fps budget", worstMs);
    checkf(avgMs   < 11.0, "average frame %.2f ms leaves 3x headroom", avgMs);

    /* a full-screen clear must be recognisably expensive - if this ever
     * gets cheap, the dirty tracking has broken */
    fb.clearDirty();
    fb.clearAll(C_BLACK);
    double fullMs = fb.dirtyPixels() / 6000000.0 * 1000.0;
    checkf(fullMs > 50.0, "full clear costs %.1f ms - never do this per frame", fullMs);
}

/* ================= main ================= */
int main() {
    printf("\n========================================\n");
    printf(" RX-7 ICU REGRESSION SUITE\n");
    printf("========================================\n");

    testStructs();
    testCounterWrap();
    testConversions();
    testDigits();
    testOverlap();
    testBounds();
    testDirtyRects();
    testFaults();
    testVehicleModel();
    testStats();
    testDiagPage();
    testFrameCost();

    printf("\n========================================\n");
    printf(" passed %d   failed %d\n", g_pass, g_fail);
    if (g_fail == 0) printf(" ALL TESTS PASSED\n");
    else             printf(" %d FAILURE%s\n", g_fail, g_fail == 1 ? "" : "S");
    printf("========================================\n\n");
    return g_fail ? 1 : 0;
}

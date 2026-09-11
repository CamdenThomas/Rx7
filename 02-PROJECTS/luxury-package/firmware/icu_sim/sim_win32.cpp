/*
 * sim_win32.cpp — desktop preview, ZERO external libraries
 *
 * Renders cluster_core.h in a Windows window using only gdi32/user32,
 * which ship with Windows. No SDL, no downloads beyond a compiler.
 *
 * This runs THE ACTUAL FIRMWARE RENDERER. What you see is what the car draws.
 *
 * ===============================================================
 * BUILD — you need a C++ compiler. Easiest is w64devkit:
 *
 *   1. Download w64devkit from
 *      https://github.com/skeeto/w64devkit/releases
 *      Take the .zip (about 80 MB). NO INSTALLER — just unzip it.
 *   2. Unzip anywhere, e.g. C:\w64devkit
 *   3. Run C:\w64devkit\w64devkit.exe  (opens a shell with g++ ready)
 *   4. cd to this folder:
 *        cd "C:/Users/Camden Thomas/Documents/Storage/Rx7/02-PROJECTS/electrical-pmu/03-MODULES/firmware/icu_sim"
 *   5. Build:
 *        g++ sim_win32.cpp -o sim.exe -std=c++17 -O2 -lgdi32 -luser32
 *   6. Run:
 *        ./sim.exe
 *
 * Or just double-click build.bat once w64devkit is on your PATH.
 * ===============================================================
 *
 * CONTROLS
 *   Q / A    rpm            W / S    speed
 *   E / D    water temp     R / F    oil pressure
 *   T / G    oil temp       Y / H    fuel
 *   U / J    volts
 *   1..5     warnings: oil, temp, batt, brake, fuel
 *   Z        cycle WATER sensor state      X   cycle OIL PRESSURE state
 *   C        cycle FUEL sensor state       V   cycle RPM state
 *   SPACE    auto sweep
 *   L        toggle background grid
 *   ESC      quit
 */

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>

/* ONE SOURCE OF TRUTH. The Arduino sketch and this simulator include the
 * SAME header. Edit the layout once; both change. There is no second copy
 * to drift out of sync. */
#include "../icu/cluster_core.h"
#include "../icu/stats.h"

static StatsTracker stats;

/* 1 = native 800x480. Press + / - at runtime to change. */
static int SCALE = 1;

static Framebuffer  fb;
static Cluster      cluster;
static VehicleState st;

static uint32_t pal[256];
static uint32_t rgb[SCR_W * SCR_H];
static bool     grid  = false;      /* press L to turn it on */
static bool     sweep = false;
static bool     running = true;

static void paletteInit() {
    for (int i = 0; i < 256; i++) {
        uint8_t r = (uint8_t)(((i >> 5) & 7) * 255 / 7);
        uint8_t g = (uint8_t)(((i >> 2) & 7) * 255 / 7);
        uint8_t b = (uint8_t)(( i       & 3) * 255 / 3);
        rgb[0] = 0;                       /* silence unused warnings */
        pal[i] = (uint32_t)((r << 16) | (g << 8) | b);
    }
}

static const char *statusName(SensorStatus s) {
    switch (s) {
        case SENSOR_OK: return "OK";      case SENSOR_OPEN:  return "OPEN";
        case SENSOR_SHORT: return "SHORT"; case SENSOR_STALE: return "STALE";
        default: return "RANGE";
    }
}
static SensorStatus cycleStatus(SensorStatus s) {
    return (SensorStatus)((s + 1) % 5);
}

/* invalidateWidgets now lives on Cluster itself - it was drifting out of
 * date every time a widget was added. */

static HWND g_hwnd = nullptr;

/* Resize the window to match the current SCALE */
static void applyScale() {
    if (!g_hwnd) return;
    RECT r = { 0, 0, SCR_W * SCALE, SCR_H * SCALE };
    AdjustWindowRect(&r, WS_OVERLAPPEDWINDOW, FALSE);
    SetWindowPos(g_hwnd, nullptr, 0, 0, r.right - r.left, r.bottom - r.top,
                 SWP_NOMOVE | SWP_NOZORDER);
    printf("scale %dx  ->  window %d x %d\n", SCALE, SCR_W * SCALE, SCR_H * SCALE);
}

static LRESULT CALLBACK WndProc(HWND h, UINT m, WPARAM w, LPARAM l) {
    switch (m) {
        case WM_DESTROY: running = false; PostQuitMessage(0); return 0;
        case WM_KEYDOWN:
            switch (w) {
                case VK_ESCAPE: running = false; break;
                case VK_SPACE:  sweep = !sweep;  break;
                case VK_OEM_PLUS: case VK_ADD:
                    if (SCALE < 3) { SCALE++; applyScale(); } break;
                case VK_OEM_MINUS: case VK_SUBTRACT:
                    if (SCALE > 1) { SCALE--; applyScale(); } break;
                case 'L': grid = !grid;
                          cluster.setPage(fb, cluster.page, grid); break;
                case 'P': cluster.nextPage(fb);
                          printf("page %d\n", (int)cluster.page); break;
                case '1': st.wOil   = !st.wOil;   break;
                case '2': st.wTemp  = !st.wTemp;  break;
                case '3': st.wBatt  = !st.wBatt;  break;
                case '4': st.wBrake = !st.wBrake; break;
                case '5': st.wFuel  = !st.wFuel;  break;
                case 'Z': st.sWater = cycleStatus(st.sWater);
                          printf("water     -> %s\n", statusName(st.sWater)); break;
                case 'X': st.sOilP  = cycleStatus(st.sOilP);
                          printf("oil press -> %s\n", statusName(st.sOilP)); break;
                case 'C': st.sFuel  = cycleStatus(st.sFuel);
                          printf("fuel      -> %s\n", statusName(st.sFuel)); break;
                case 'V': st.sRpm   = cycleStatus(st.sRpm);
                          printf("rpm       -> %s\n", statusName(st.sRpm)); break;
            }
            return 0;
    }
    return DefWindowProc(h, m, w, l);
}

static bool down(int vk) { return (GetAsyncKeyState(vk) & 0x8000) != 0; }

int main() {
    paletteInit();

    WNDCLASSA wc = {};
    wc.lpfnWndProc   = WndProc;
    wc.hInstance     = GetModuleHandle(nullptr);
    wc.lpszClassName = "RX7ICU";
    wc.hCursor       = LoadCursor(nullptr, IDC_ARROW);
    RegisterClassA(&wc);

    RECT r = { 0, 0, SCR_W * SCALE, SCR_H * SCALE };
    AdjustWindowRect(&r, WS_OVERLAPPEDWINDOW, FALSE);
    HWND hwnd = CreateWindowA("RX7ICU", "RX-7 ICU cluster - live firmware render",
        WS_OVERLAPPEDWINDOW | WS_VISIBLE, CW_USEDEFAULT, CW_USEDEFAULT,
        r.right - r.left, r.bottom - r.top, nullptr, nullptr, wc.hInstance, nullptr);
    g_hwnd = hwnd;

    BITMAPINFO bmi = {};
    bmi.bmiHeader.biSize        = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth       = SCR_W;
    bmi.bmiHeader.biHeight      = -SCR_H;      /* negative = top-down */
    bmi.bmiHeader.biPlanes      = 1;
    bmi.bmiHeader.biBitCount    = 32;
    bmi.bmiHeader.biCompression = BI_RGB;

    st.rpm = 900;  st.speed = 100;  st.waterC = 88;
    st.oilPressCbar = 450;         st.oilTempC = 95;
    st.fuelPct = 72;               st.voltsX10 = 142;

    cluster.layout();

    /* Plausible PMU channel telemetry so the diagnostics page has something
     * real-shaped to show. Replaced by CAN 0x130 in the car. */
    static const uint16_t demoLimit[PMU_CHANNELS] = {
      2500,1500,1500,1600, 500,800,800,1500, 1500,1200,1000,800,
      1800,2500,2000,2000,  600,600,600,500,  100,100,700,700 };
    static const uint8_t demoState[PMU_CHANNELS] = {
      1,1,0,0, 1,1,0,0, 0,1,0,1, 0,0,1,1, 0,0,0,1, 0,1,0,0 };
    for (int i = 0; i < PMU_CHANNELS; i++) {
        st.chLimit[i]  = demoLimit[i];
        st.chState[i]  = demoState[i];
        st.chCurrent[i] = demoState[i] ? (uint16_t)(demoLimit[i] * (30 + (i*7)%55) / 100) : 0;
    }
    st.chState[6]   = 2;                       /* one tripped channel */
    st.chCurrent[6] = st.chLimit[6];
    st.chState[13]  = 3;                       /* one retrying */

    cluster.setPage(fb, PAGE_DRIVE, grid);

    printf("RX-7 ICU simulator running. Keys are listed in the source header.\n");

    int sweepRpm = 900, dir = 1;
    DWORD lastReport = GetTickCount();
    uint32_t frames = 0, sumDirty = 0, worstDirty = 0;

    while (running) {
        MSG msg;
        while (PeekMessage(&msg, nullptr, 0, 0, PM_REMOVE)) {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
        if (!running) break;

        if (GetForegroundWindow() == hwnd) {
            if (!sweep) { if (down('Q')) st.rpm += 60; if (down('A')) st.rpm -= 60; }
            if (down('W')) st.speed += 1;         if (down('S')) st.speed -= 1;
            if (down('E')) st.waterC += 1;        if (down('D')) st.waterC -= 1;
            if (down('R')) st.oilPressCbar += 8;  if (down('F')) st.oilPressCbar -= 8;
            if (down('T')) st.oilTempC += 1;      if (down('G')) st.oilTempC -= 1;
            if (down('Y')) st.fuelPct += 1;       if (down('H')) st.fuelPct -= 1;
            if (down('U')) st.voltsX10 += 1;      if (down('J')) st.voltsX10 -= 1;

            /* G meter - arrow keys, spring back to centre when released */
            bool gk = false;
            if (down(VK_LEFT))  { st.latGx100 -= 4; gk = true; }
            if (down(VK_RIGHT)) { st.latGx100 += 4; gk = true; }
            if (down(VK_UP))    { st.lonGx100 += 4; gk = true; }
            if (down(VK_DOWN))  { st.lonGx100 -= 4; gk = true; }
            if (!gk) {
                st.latGx100 -= st.latGx100 / 8;
                st.lonGx100 -= st.lonGx100 / 8;
            }
            if (st.latGx100 >  100) st.latGx100 =  100;
            if (st.latGx100 < -100) st.latGx100 = -100;
            if (st.lonGx100 >  100) st.lonGx100 =  100;
            if (st.lonGx100 < -100) st.lonGx100 = -100;

            /* compass N/M, pitch K/I */
            if (down('N')) st.headingDeg += 2;
            if (down('M')) st.headingDeg -= 2;
            if (down('I')) st.pitchDeg   += 1;
            if (down('K')) st.pitchDeg   -= 1;
            st.headingDeg = ((st.headingDeg % 360) + 360) % 360;
            if (st.pitchDeg >  45) st.pitchDeg =  45;
            if (st.pitchDeg < -45) st.pitchDeg = -45;
        }

        if (sweep) {
            sweepRpm += dir * 130;
            if (sweepRpm > 8400) dir = -1;
            if (sweepRpm < 800)  dir = 1;
            st.rpm = sweepRpm;
            st.speed = sweepRpm / 62;
        }

        if (st.rpm < 0) st.rpm = 0;                if (st.rpm > 8500) st.rpm = 8500;
        if (st.speed < 0) st.speed = 0;            if (st.speed > 999) st.speed = 999;
        if (st.waterC < 0) st.waterC = 0;          if (st.waterC > 130) st.waterC = 130;
        if (st.oilPressCbar < 0) st.oilPressCbar = 0;
        if (st.oilPressCbar > 800) st.oilPressCbar = 800;
        if (st.oilTempC < 0) st.oilTempC = 0;      if (st.oilTempC > 150) st.oilTempC = 150;
        if (st.fuelPct < 0) st.fuelPct = 0;        if (st.fuelPct > 100) st.fuelPct = 100;
        if (st.voltsX10 < 0) st.voltsX10 = 0;      if (st.voltsX10 > 200) st.voltsX10 = 200;

        /* ---- one frame of the real renderer ---- */
        fb.clearDirty();
        cluster.update(fb, st);
        if (cluster.page == PAGE_TRIP)
            drawTripPage(fb, stats.trip, StatsTracker::mpgX10(stats.trip));

        uint32_t d = fb.dirtyPixels();
        sumDirty += d; frames++;
        if (d > worstDirty) worstDirty = d;

        for (int i = 0; i < SCR_W * SCR_H; i++) rgb[i] = pal[fb.buf[i]];

        HDC dc = GetDC(hwnd);
        StretchDIBits(dc, 0, 0, SCR_W * SCALE, SCR_H * SCALE,
                          0, 0, SCR_W, SCR_H,
                      rgb, &bmi, DIB_RGB_COLORS, SRCCOPY);
        ReleaseDC(hwnd, dc);

        DWORD now = GetTickCount();
        stats.tick(st, now);

        if (now - lastReport > 1000 && frames) {
            double avgMs   = (sumDirty / (double)frames) / 6000000.0 * 1000.0;
            double worstMs = worstDirty / 6000000.0 * 1000.0;
            printf("avg %6u px (%.2f ms)   worst %6u px (%.2f ms)   max %.0f fps\n",
                   (unsigned)(sumDirty / frames), avgMs,
                   (unsigned)worstDirty, worstMs,
                   worstMs > 0.01 ? 1000.0 / worstMs : 9999.0);

            const Stats &t = stats.trip;
            printf("  TRIP  maxRPM %u  maxMPH %u  water %d  oilT %d  "
                   "minOilP %.2f  G lat %.2f acc %.2f brk %.2f  dist %.1f mi\n",
                   t.maxRpm, t.maxSpeed, t.maxWaterC, t.maxOilTempC,
                   (t.minOilPress == 65535 ? 0 : t.minOilPress) / 100.0,
                   t.maxLatG/100.0, t.maxAccelG/100.0, t.maxBrakeG/100.0,
                   t.distanceX10/10.0);

            lastReport = now; sumDirty = 0; frames = 0; worstDirty = 0;
        }

        Sleep(16);
    }
    return 0;
}

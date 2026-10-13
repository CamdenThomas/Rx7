/*
 * sim_sdl.cpp — desktop preview on Linux, in an SDL2 window
 *
 * This runs THE ACTUAL FIRMWARE RENDERER. What you see is what the car draws.
 * It is the Win32 host (sim_win32.cpp, retired 2026-09-22 with the move to one
 * Fedora machine) ported to SDL2 key for key: pages, trip stats, the G meter,
 * compass, pitch and the demo PMU telemetry for the diagnostics page.
 *
 * ===============================================================
 * BUILD — once:   sudo dnf install gcc-c++ SDL2-devel
 *         then:   ./build.sh          (from this folder)
 *         run:    ./sim
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
 *   arrows   G meter (springs back)        N / M  compass    I / K  pitch
 *   P        next page                     + / -  window scale 1x-3x
 *   SPACE    auto sweep
 *   L        toggle background grid
 *   ESC      quit
 */

#include <SDL2/SDL.h>
#include <stdio.h>

/* ONE SOURCE OF TRUTH. The Arduino sketch and this simulator include the
 * SAME header. Edit the layout once; both change. There is no second copy
 * to drift out of sync. */
#include "../icu/cluster_core.h"
#include "../icu/stats.h"

static StatsTracker stats;

/* 1 = native size. Press + / - at runtime to change. */
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

static SDL_Window *g_win = nullptr;

/* Resize the window to match the current SCALE */
static void applyScale() {
    if (!g_win) return;
    SDL_SetWindowSize(g_win, SCR_W * SCALE, SCR_H * SCALE);
    printf("scale %dx  ->  window %d x %d\n", SCALE, SCR_W * SCALE, SCR_H * SCALE);
}

static void onKey(SDL_Keycode k) {
    switch (k) {
        case SDLK_ESCAPE: running = false; break;
        case SDLK_SPACE:  sweep = !sweep;  break;
        case SDLK_PLUS: case SDLK_EQUALS: case SDLK_KP_PLUS:
            if (SCALE < 3) { SCALE++; applyScale(); } break;
        case SDLK_MINUS: case SDLK_KP_MINUS:
            if (SCALE > 1) { SCALE--; applyScale(); } break;
        case SDLK_l: grid = !grid;
                     cluster.setPage(fb, cluster.page, grid); break;
        case SDLK_p: cluster.nextPage(fb);
                     printf("page %d\n", (int)cluster.page); break;
        case SDLK_1: st.wOil   = !st.wOil;   break;
        case SDLK_2: st.wTemp  = !st.wTemp;  break;
        case SDLK_3: st.wBatt  = !st.wBatt;  break;
        case SDLK_4: st.wBrake = !st.wBrake; break;
        case SDLK_5: st.wFuel  = !st.wFuel;  break;
        case SDLK_z: st.sWater = cycleStatus(st.sWater);
                     printf("water     -> %s\n", statusName(st.sWater)); break;
        case SDLK_x: st.sOilP  = cycleStatus(st.sOilP);
                     printf("oil press -> %s\n", statusName(st.sOilP)); break;
        case SDLK_c: st.sFuel  = cycleStatus(st.sFuel);
                     printf("fuel      -> %s\n", statusName(st.sFuel)); break;
        case SDLK_v: st.sRpm   = cycleStatus(st.sRpm);
                     printf("rpm       -> %s\n", statusName(st.sRpm)); break;
        default: break;
    }
}

int main(int, char **) {
    paletteInit();

    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        printf("SDL_Init failed: %s\n", SDL_GetError());
        return 1;
    }
    g_win = SDL_CreateWindow("RX-7 ICU cluster - live firmware render",
                             SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                             SCR_W * SCALE, SCR_H * SCALE, 0);
    SDL_Renderer *ren = SDL_CreateRenderer(g_win, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (!ren) ren = SDL_CreateRenderer(g_win, -1, 0);
    SDL_RenderSetLogicalSize(ren, SCR_W, SCR_H);
    SDL_Texture *tex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888,
                                         SDL_TEXTUREACCESS_STREAMING, SCR_W, SCR_H);
    if (!g_win || !ren || !tex) {
        printf("SDL window setup failed: %s\n", SDL_GetError());
        return 1;
    }

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
    uint32_t lastReport = SDL_GetTicks();
    uint32_t frames = 0, sumDirty = 0, worstDirty = 0;

    while (running) {
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) running = false;
            if (e.type == SDL_KEYDOWN && !e.key.repeat) onKey(e.key.keysym.sym);
        }
        if (!running) break;

        if (SDL_GetKeyboardFocus() == g_win) {
            const Uint8 *k = SDL_GetKeyboardState(nullptr);
            if (!sweep) { if (k[SDL_SCANCODE_Q]) st.rpm += 60; if (k[SDL_SCANCODE_A]) st.rpm -= 60; }
            if (k[SDL_SCANCODE_W]) st.speed += 1;         if (k[SDL_SCANCODE_S]) st.speed -= 1;
            if (k[SDL_SCANCODE_E]) st.waterC += 1;        if (k[SDL_SCANCODE_D]) st.waterC -= 1;
            if (k[SDL_SCANCODE_R]) st.oilPressCbar += 8;  if (k[SDL_SCANCODE_F]) st.oilPressCbar -= 8;
            if (k[SDL_SCANCODE_T]) st.oilTempC += 1;      if (k[SDL_SCANCODE_G]) st.oilTempC -= 1;
            if (k[SDL_SCANCODE_Y]) st.fuelPct += 1;       if (k[SDL_SCANCODE_H]) st.fuelPct -= 1;
            if (k[SDL_SCANCODE_U]) st.voltsX10 += 1;      if (k[SDL_SCANCODE_J]) st.voltsX10 -= 1;

            /* G meter - arrow keys, spring back to centre when released */
            bool gk = false;
            if (k[SDL_SCANCODE_LEFT])  { st.latGx100 -= 4; gk = true; }
            if (k[SDL_SCANCODE_RIGHT]) { st.latGx100 += 4; gk = true; }
            if (k[SDL_SCANCODE_UP])    { st.lonGx100 += 4; gk = true; }
            if (k[SDL_SCANCODE_DOWN])  { st.lonGx100 -= 4; gk = true; }
            if (!gk) {
                st.latGx100 -= st.latGx100 / 8;
                st.lonGx100 -= st.lonGx100 / 8;
            }
            if (st.latGx100 >  100) st.latGx100 =  100;
            if (st.latGx100 < -100) st.latGx100 = -100;
            if (st.lonGx100 >  100) st.lonGx100 =  100;
            if (st.lonGx100 < -100) st.lonGx100 = -100;

            /* compass N/M, pitch K/I */
            if (k[SDL_SCANCODE_N]) st.headingDeg += 2;
            if (k[SDL_SCANCODE_M]) st.headingDeg -= 2;
            if (k[SDL_SCANCODE_I]) st.pitchDeg   += 1;
            if (k[SDL_SCANCODE_K]) st.pitchDeg   -= 1;
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

        for (int i = 0; i < SCR_W * SCR_H; i++) rgb[i] = 0xFF000000u | pal[fb.buf[i]];
        SDL_UpdateTexture(tex, nullptr, rgb, SCR_W * 4);
        SDL_RenderClear(ren);
        SDL_RenderCopy(ren, tex, nullptr, nullptr);
        SDL_RenderPresent(ren);

        uint32_t now = SDL_GetTicks();
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
            fflush(stdout);

            lastReport = now; sumDirty = 0; frames = 0; worstDirty = 0;
        }

        SDL_Delay(16);
    }

    SDL_DestroyTexture(tex);
    SDL_DestroyRenderer(ren);
    SDL_DestroyWindow(g_win);
    SDL_Quit();
    return 0;
}

/*
 * sim_main.cpp — desktop preview host
 *
 * Renders cluster_core.h in an SDL2 window at 2x scale.
 * This runs THE ACTUAL FIRMWARE RENDERER, not a mockup.
 *
 * ---------------------------------------------------------------
 * BUILD - Windows, MSYS2 / MinGW (easiest route)
 *   1. Install MSYS2 from msys2.org
 *   2. In the MSYS2 MINGW64 shell:
 *        pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-SDL2
 *   3. cd to this folder, then:
 *        g++ sim_main.cpp -o sim.exe -std=c++17 -O2 `sdl2-config --cflags --libs`
 *   4. ./sim.exe
 *
 * BUILD - Linux / macOS
 *   g++ sim_main.cpp -o sim -std=c++17 -O2 $(sdl2-config --cflags --libs)
 * ---------------------------------------------------------------
 *
 * CONTROLS
 *   Q / A      rpm up / down          W / S   speed
 *   E / D      water temp             R / F   oil pressure
 *   T / G      oil temp               Y / H   fuel
 *   U / J      volts
 *   1..5       toggle warnings
 *   Z          cycle water sensor status   X  oil pressure
 *   C          cycle fuel sensor status    V  rpm sensor
 *   SPACE      auto sweep on/off
 *   L          toggle background grid  (forces a full static redraw)
 *   ESC        quit
 */

#include <SDL2/SDL.h>
#include <stdio.h>
#include "cluster_core.h"

static const int SCALE = 2;

/* RGB332 -> RGB888 */
static void paletteInit(uint32_t *pal) {
    for (int i = 0; i < 256; i++) {
        uint8_t r = (uint8_t)(((i >> 5) & 7) * 255 / 7);
        uint8_t g = (uint8_t)(((i >> 2) & 7) * 255 / 7);
        uint8_t b = (uint8_t)(( i       & 3) * 255 / 3);
        pal[i] = (0xFFu << 24) | (r << 16) | (g << 8) | b;
    }
}

static const char *statusName(SensorStatus s) {
    switch (s) {
        case SENSOR_OK:    return "OK";
        case SENSOR_OPEN:  return "OPEN";
        case SENSOR_SHORT: return "SHORT";
        case SENSOR_STALE: return "STALE";
        default:           return "RANGE";
    }
}
static SensorStatus cycle(SensorStatus s) {
    return (SensorStatus)((s + 1) % 5);
}

static Framebuffer fb;
static Cluster     cluster;
static VehicleState st;

int main(int, char **) {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        printf("SDL init failed: %s\n", SDL_GetError());
        return 1;
    }
    SDL_Window *win = SDL_CreateWindow("RX-7 ICU cluster - live firmware render",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        SCR_W * SCALE, SCR_H * SCALE, 0);
    SDL_Renderer *ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
    SDL_Texture *tex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888,
        SDL_TEXTUREACCESS_STREAMING, SCR_W, SCR_H);

    uint32_t pal[256];
    paletteInit(pal);
    static uint32_t rgb[SCR_W * SCR_H];

    /* starting state */
    st.rpm = 900;  st.speed = 0;    st.waterC = 88;
    st.oilPressCbar = 450;          st.oilTempC = 95;
    st.fuelPct = 72;                st.voltsX10 = 142;

    bool grid = true;
    cluster.layout();
    cluster.drawStatic(fb, grid);

    bool run = true, sweep = false;
    int  sweepRpm = 900, dir = 1;
    uint32_t lastReport = SDL_GetTicks();
    uint32_t frames = 0, sumDirty = 0, worstDirty = 0;

    while (run) {
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) run = false;
            if (e.type == SDL_KEYDOWN) {
                switch (e.key.keysym.sym) {
                    case SDLK_ESCAPE: run = false; break;
                    case SDLK_SPACE:  sweep = !sweep; break;
                    case SDLK_l:      grid = !grid;
                                      cluster.drawStatic(fb, grid);
                                      /* widgets must repaint after a static redraw */
                                      cluster.rpmBar.prevLit = -1;
                                      cluster.water.prevLit = -1;
                                      cluster.oilP.prevLit = -1;
                                      cluster.oilT.prevLit = -1;
                                      cluster.fuel.prevLit = -1;
                                      break;
                    case SDLK_1: st.wOil   = !st.wOil;   break;
                    case SDLK_2: st.wTemp  = !st.wTemp;  break;
                    case SDLK_3: st.wBatt  = !st.wBatt;  break;
                    case SDLK_4: st.wBrake = !st.wBrake; break;
                    case SDLK_5: st.wFuel  = !st.wFuel;  break;
                    case SDLK_z: st.sWater = cycle(st.sWater);
                                 printf("water  -> %s\n", statusName(st.sWater)); break;
                    case SDLK_x: st.sOilP  = cycle(st.sOilP);
                                 printf("oil P  -> %s\n", statusName(st.sOilP)); break;
                    case SDLK_c: st.sFuel  = cycle(st.sFuel);
                                 printf("fuel   -> %s\n", statusName(st.sFuel)); break;
                    case SDLK_v: st.sRpm   = cycle(st.sRpm);
                                 printf("rpm    -> %s\n", statusName(st.sRpm)); break;
                    default: break;
                }
            }
        }

        const Uint8 *k = SDL_GetKeyboardState(nullptr);
        if (!sweep) {
            if (k[SDL_SCANCODE_Q]) st.rpm += 60;
            if (k[SDL_SCANCODE_A]) st.rpm -= 60;
        }
        if (k[SDL_SCANCODE_W]) st.speed += 1;
        if (k[SDL_SCANCODE_S]) st.speed -= 1;
        if (k[SDL_SCANCODE_E]) st.waterC += 1;
        if (k[SDL_SCANCODE_D]) st.waterC -= 1;
        if (k[SDL_SCANCODE_R]) st.oilPressCbar += 8;
        if (k[SDL_SCANCODE_F]) st.oilPressCbar -= 8;
        if (k[SDL_SCANCODE_T]) st.oilTempC += 1;
        if (k[SDL_SCANCODE_G]) st.oilTempC -= 1;
        if (k[SDL_SCANCODE_Y]) st.fuelPct += 1;
        if (k[SDL_SCANCODE_H]) st.fuelPct -= 1;
        if (k[SDL_SCANCODE_U]) st.voltsX10 += 1;
        if (k[SDL_SCANCODE_J]) st.voltsX10 -= 1;

        if (sweep) {
            sweepRpm += dir * 130;
            if (sweepRpm > 8400) dir = -1;
            if (sweepRpm < 800)  dir = 1;
            st.rpm = sweepRpm;
            st.speed = sweepRpm / 62;
        }

        /* clamp */
        if (st.rpm < 0) st.rpm = 0;             if (st.rpm > 8500) st.rpm = 8500;
        if (st.speed < 0) st.speed = 0;         if (st.speed > 999) st.speed = 999;
        if (st.waterC < 0) st.waterC = 0;       if (st.waterC > 130) st.waterC = 130;
        if (st.oilPressCbar < 0) st.oilPressCbar = 0;
        if (st.oilPressCbar > 800) st.oilPressCbar = 800;
        if (st.oilTempC < 0) st.oilTempC = 0;   if (st.oilTempC > 150) st.oilTempC = 150;
        if (st.fuelPct < 0) st.fuelPct = 0;     if (st.fuelPct > 100) st.fuelPct = 100;
        if (st.voltsX10 < 0) st.voltsX10 = 0;   if (st.voltsX10 > 200) st.voltsX10 = 200;

        /* ---- the frame ---- */
        fb.clearDirty();
        fb.pixelsWritten = 0;
        cluster.update(fb, st);

        uint32_t d = fb.dirtyPixels();
        sumDirty += d; frames++;
        if (d > worstDirty) worstDirty = d;

        /* palette expand and present */
        for (int i = 0; i < SCR_W * SCR_H; i++) rgb[i] = pal[fb.buf[i]];
        SDL_UpdateTexture(tex, nullptr, rgb, SCR_W * 4);
        SDL_RenderCopy(ren, tex, nullptr, nullptr);
        SDL_RenderPresent(ren);

        uint32_t now = SDL_GetTicks();
        if (now - lastReport > 1000) {
            double avgMs   = (sumDirty / (double)frames) / 6000000.0 * 1000.0;
            double worstMs = worstDirty / 6000000.0 * 1000.0;
            printf("avg dirty %6u px (%.2f ms)   worst %6u px (%.2f ms)   "
                   "max %.0f fps\n",
                   (unsigned)(sumDirty / frames), avgMs,
                   (unsigned)worstDirty, worstMs,
                   worstMs > 0.01 ? 1000.0 / worstMs : 9999.0);
            lastReport = now; sumDirty = 0; frames = 0; worstDirty = 0;
        }

        SDL_Delay(16);        /* ~60 Hz host loop */
    }

    SDL_DestroyTexture(tex);
    SDL_DestroyRenderer(ren);
    SDL_DestroyWindow(win);
    SDL_Quit();
    return 0;
}

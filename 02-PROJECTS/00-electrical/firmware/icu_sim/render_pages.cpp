/*
 * render_pages.cpp — draw every cluster page once, headless, to PPM files
 *
 * The same renderer as the car and the simulator (cluster_core.h), the same
 * demo state as sim_sdl.cpp, no window: for a render you can look at, archive
 * or compare (work X-007). Build and run with ./render.sh.
 *
 * Output: page0_drive.ppm, page1_diag.ppm, page2_trip.ppm (1280 x 480, RGB),
 * in the current directory. render.sh turns them into PNGs.
 */
#include <stdio.h>
#include "../icu/cluster_core.h"
#include "../icu/stats.h"

static Framebuffer  fb;
static Cluster      cluster;
static VehicleState st;
static StatsTracker stats;

static void write_ppm(const char *name)
{
    FILE *f = fopen(name, "wb");
    if (!f) { printf("cannot write %s\n", name); return; }
    fprintf(f, "P6\n%d %d\n255\n", SCR_W, SCR_H);
    for (int i = 0; i < SCR_W * SCR_H; i++) {
        uint8_t c = fb.buf[i];
        uint8_t rgb[3] = { (uint8_t)(((c >> 5) & 7) * 255 / 7),
                           (uint8_t)(((c >> 2) & 7) * 255 / 7),
                           (uint8_t)(( c       & 3) * 255 / 3) };
        fwrite(rgb, 1, 3, f);
    }
    fclose(f);
    printf("wrote %s\n", name);
}

int main()
{
    /* the simulator's opening state: warm idle */
    st.rpm = 900;  st.speed = 100;  st.waterC = 88;
    st.oilPressCbar = 450;         st.oilTempC = 95;
    st.fuelPct = 72;               st.voltsX10 = 142;

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
    st.chState[6]   = 2;  st.chCurrent[6] = st.chLimit[6];   /* one tripped channel */
    st.chState[13]  = 3;                                      /* one retrying */

    cluster.layout();
    static const char *names[PAGE_COUNT] = { "page0_drive.ppm", "page1_diag.ppm", "page2_trip.ppm" };
    for (int p = 0; p < PAGE_COUNT; p++) {
        cluster.setPage(fb, (Page)p, false);
        for (int n = 0; n < 3; n++) {           /* settle every widget */
            fb.clearDirty();
            cluster.update(fb, st);
            if (cluster.page == PAGE_TRIP)
                drawTripPage(fb, stats.trip, StatsTracker::mpgX10(stats.trip));
        }
        write_ppm(names[p]);
    }
    return 0;
}

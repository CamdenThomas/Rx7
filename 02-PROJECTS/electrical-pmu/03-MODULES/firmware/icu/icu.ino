/*
 * icu.ino — Teensy 4.1 host for the ICU cluster
 *
 * Includes the SAME cluster_core.h that the desktop simulator uses.
 * Nothing in the renderer changes between the two. Only this file differs.
 *
 * SETUP
 *   Put cluster_core.h in this folder, beside this .ino.
 *
 * DISPLAY
 *   pushDirtyTiles() below is the only display-specific code. Fill in the
 *   three calls marked TODO once a panel is chosen (Q-060). The interface is
 *   decided: SPI with dirty-rectangle tiles from the RAM framebuffer (D-168);
 *   the arithmetic is in DCU-CLUSTER.md Appendix A.
 *
 *   Until then this compiles and runs with the display calls stubbed out,
 *   and reports real timing over serial.
 */

/* Bump on every change that alters behaviour; log it in 05-BUILD/LOGS.md
 * and tag the commit. Printed over serial at boot. */
#define ICU_FW_VERSION "0.3.0-dev"

#include "cluster_core.h"

Framebuffer  fb;
Cluster      cluster;
VehicleState state;

/* ---------------------------------------------------------------
 * The ONLY display-dependent function in the whole project.
 *
 * Walks the dirty tile map and pushes just those tiles. A tile is
 * 16x16 = 256 bytes at 8bpp.
 * --------------------------------------------------------------- */
uint32_t pushDirtyTiles() {
    uint32_t sent = 0;
    static uint8_t tileBuf[TILE * TILE];

    for (int ty = 0; ty < TILES_Y; ty++) {
        for (int tx = 0; tx < TILES_X; tx++) {
            if (!fb.tileDirty(tx, ty)) continue;

            int x0 = tx * TILE, y0 = ty * TILE;
            for (int r = 0; r < TILE; r++)
                memcpy(&tileBuf[r * TILE], &fb.buf[(y0 + r) * SCR_W + x0], TILE);

            /* TODO when the panel is chosen:
             *   tft.setAddrWindow(x0, y0, TILE, TILE);
             *   tft.writePixels8bpp(tileBuf, TILE * TILE);
             */
            sent += TILE * TILE;
        }
    }
    return sent;
}

/* Merge adjacent dirty tiles into rows before pushing — fewer address-window
 * commands, same pixels. Worth doing once real timing is measurable. */

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {}

    Serial.print("ICU cluster — Teensy host, firmware ");
    Serial.println(ICU_FW_VERSION);
    Serial.print("framebuffer bytes: ");
    Serial.println((uint32_t)sizeof(fb.buf));

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
    /* --- until CAN and sensors are wired, sweep for timing --- */
    static int rpm = 900, dir = 1;
    rpm += dir * 130;
    if (rpm > 8400) dir = -1;
    if (rpm < 800)  dir = 1;
    state.rpm = rpm;
    state.speed = rpm / 62;

    /* --- the frame --- */
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
        n = 0; sumC = 0; sumP = 0; worst = 0;
    }

    delay(33);        /* 30 Hz */
}

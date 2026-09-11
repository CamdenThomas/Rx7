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
 */

/* Bump on every change that alters behaviour; log it in 05-BUILD/LOGS.md
 * and tag the commit. Printed over serial at boot. */
#define ICU_FW_VERSION "0.4.0-dev"

#include "cluster_core.h"
#include "bt817.h"

EXTMEM Framebuffer fb;          /* 614 KB — PSRAM only */
Cluster      cluster;
VehicleState state;
Bt817        display;

extern "C" uint8_t external_psram_size;   /* MB detected at startup, 0 = none */

uint32_t pushDirtyTiles() {
    return display.pushDirty(fb, TILE, TILES_X, TILES_Y, SCR_W);
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

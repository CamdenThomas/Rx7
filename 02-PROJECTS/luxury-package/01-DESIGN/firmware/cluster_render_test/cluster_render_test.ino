/*
 * cluster_render_test.ino
 *
 * Runs the full RX-7 cluster renderer against a COUNTING MOCK CANVAS.
 * No display needed. Verifies the dirty-rectangle 01-DESIGN and reports the
 * real pixel cost per frame, so you know the performance before you buy a panel.
 *
 * Upload, Serial Monitor at 115200.
 *
 * Swap MockCanvas for a real display driver later and the renderer is unchanged.
 */

#include "cluster.h"

/* ---------------- mock canvas: counts instead of drawing ---------------- */
class MockCanvas : public Canvas {
public:
  uint32_t pixels = 0;
  uint32_t rects  = 0;

  void fillRect(int x, int y, int w, int h, uint8_t c) override {
    (void)x; (void)y; (void)c;
    if (w <= 0 || h <= 0) return;
    pixels += (uint32_t)w * h;
    rects++;
  }
  void reset() { pixels = 0; rects = 0; }
};

MockCanvas g;

/* ================= LAYOUT =================
 *
 *  ┌──────────────────────────────────────────────────────────────┐
 *  │  RPM  ▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮      │
 *  │       1    2    3    4    5    6    7  |8|                   │
 *  │                                                               │
 *  │      ┌─────────────┐            WATER  ▮▮▮▮▮▮▮▮░░░░          │
 *  │      │   1 2 8     │            OIL P  ▮▮▮▮▮▮▮▮▮▮░          │
 *  │      │      MPH    │            OIL T  ▮▮▮▮▮░░░░░░          │
 *  │      └─────────────┘            FUEL   ▮▮▮▮▮▮▮▮▮░░          │
 *  │                                 VOLTS   1 4 . 2              │
 *  │  ■ OIL   ■ TEMP   ■ BATT   ■ BRK   ■ FUEL                   │
 *  └──────────────────────────────────────────────────────────────┘
 */

SegBar        rpmBar;
DigitField<3> speed;
DigitField<3> volts;      /* 14.2 shown as 3 digits, decimal painted static */
SegBar        water, oilP, oilT, fuel;
Warn          wOil, wTemp, wBatt, wBrake, wFuel;

const int RPM_SEGS = 50;
const int REDLINE_SEG = 42;      /* ~7000 of 8000 rpm */

void buildLayout() {
  /* RPM bar across the top */
  rpmBar.place(60, 40, RPM_SEGS, 12, 46, 3);
  rpmBar.redlineFrom = REDLINE_SEG;

  /* Big speed, left of centre */
  speed.place(150, 180, 70, 130, 18, 14);
  speed.setColour(C_BRIGHT);

  /* Right column bars */
  int bx = 560, by = 180, bstep = 52;
  water.place(bx, by + 0*bstep, 12, 22, 30, 4);
  oilP .place(bx, by + 1*bstep, 12, 22, 30, 4);
  oilT .place(bx, by + 2*bstep, 12, 22, 30, 4);
  fuel .place(bx, by + 3*bstep, 12, 22, 30, 4);

  /* Volts, small digits */
  volts.place(bx, by + 4*bstep, 26, 46, 8, 6);
  volts.leadingBlank = false;

  /* Warning row along the bottom */
  int wy = 420, ww = 90, wh = 26;
  wOil  .place(60,  wy, ww, wh);
  wTemp .place(190, wy, ww, wh);
  wBatt .place(320, wy, ww, wh);
  wBrake.place(450, wy, ww, wh);
  wFuel .place(580, wy, ww, wh);
}

/* Static background: drawn ONCE. Never touched again. */
uint32_t drawBackground() {
  g.reset();
  g.fillRect(0, 0, SCREEN_W, SCREEN_H, C_BLACK);

  /* rpm scale ticks */
  for (int k = 0; k <= 8; k++) {
    int x = 60 + (k * (RPM_SEGS * 15)) / 8;
    g.fillRect(x, 92, 3, 12, (k >= 7) ? C_RED : C_MID);
  }
  /* bar troughs */
  rpmBar.drawAll(g);
  water.drawAll(g); oilP.drawAll(g); oilT.drawAll(g); fuel.drawAll(g);

  /* label blocks - real firmware draws text here */
  g.fillRect(60, 20, 46, 14, C_MID);            /* "RPM"   */
  g.fillRect(150, 330, 90, 18, C_MID);          /* "MPH"   */
  for (int i = 0; i < 5; i++)
    g.fillRect(480, 180 + i*52 + 4, 70, 14, C_MID);   /* row labels */

  return g.pixels;
}

/* ---------------- simulated vehicle state ---------------- */
struct State {
  int rpm, mph, waterPct, oilPPct, oilTPct, fuelPct, voltsX10;
  bool oil, temp, batt, brake, lowFuel;
};

void renderFrame(State &s) {
  rpmBar.draw(g, (s.rpm * RPM_SEGS) / 8000);
  speed .draw(g, s.mph);
  water .draw(g, (s.waterPct * 12) / 100);
  oilP  .draw(g, (s.oilPPct  * 12) / 100);
  oilT  .draw(g, (s.oilTPct  * 12) / 100);
  fuel  .draw(g, (s.fuelPct  * 12) / 100);
  volts .draw(g, s.voltsX10);
  wOil.draw(g, s.oil);   wTemp.draw(g, s.temp);  wBatt.draw(g, s.batt);
  wBrake.draw(g, s.brake); wFuel.draw(g, s.lowFuel);
}

/* ---------------- performance model ----------------
 * 8bpp over SPI at 60 MHz, ~6 MB/s sustained = 6,000,000 px/s
 */
const float PX_PER_SEC = 6000000.0f;
float msFor(uint32_t px) { return (px / PX_PER_SEC) * 1000.0f; }

void report(const char *label, uint32_t px, uint32_t rects) {
  float ms = msFor(px);
  Serial.print(label);
  Serial.print("  px="); Serial.print(px);
  Serial.print("  rects="); Serial.print(rects);
  Serial.print("  "); Serial.print(ms, 2); Serial.print(" ms");
  if (ms > 0.01f) { Serial.print("   max "); Serial.print(1000.0f/ms, 0); Serial.print(" fps"); }
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 4000) {}

  Serial.println("=========================================");
  Serial.println(" RX-7 cluster render model  800x480 8bpp");
  Serial.println("=========================================");

  buildLayout();

  uint32_t bg = drawBackground();
  report("BACKGROUND (once, at boot) ", bg, g.rects);
  Serial.print("  ^ ");
  Serial.print((bg * 100.0f) / (SCREEN_W * SCREEN_H), 0);
  Serial.println("% of screen. Drawn ONCE, never again.\n");

  /* first render paints every element from scratch */
  State s = { 800, 0, 45, 70, 30, 80, 138, false,false,false,false,false };
  g.reset();
  renderFrame(s);
  report("FIRST FRAME (cold, all elements)", g.pixels, g.rects);
  Serial.println();

  /* --- steady idle: nothing changes --- */
  g.reset();
  renderFrame(s);
  report("IDLE, no change            ", g.pixels, g.rects);

  /* --- rpm creeping, 1 segment --- */
  s.rpm = 960;
  g.reset(); renderFrame(s);
  report("RPM +1 segment             ", g.pixels, g.rects);

  /* --- speed digit rolls 99 -> 100 --- */
  s.mph = 99;  g.reset(); renderFrame(s);
  s.mph = 100; g.reset(); renderFrame(s);
  report("SPEED 99 -> 100 (3 digits) ", g.pixels, g.rects);

  /* --- single digit change --- */
  s.mph = 101; g.reset(); renderFrame(s);
  report("SPEED 100 -> 101 (1 digit) ", g.pixels, g.rects);

  /* --- hard acceleration: rpm sweeping fast --- */
  s.rpm = 2400; g.reset(); renderFrame(s);
  report("RPM 960 -> 2400 (9 segs)   ", g.pixels, g.rects);

  /* --- worst realistic case: redline sweep + speed + a warning --- */
  s.rpm = 7600; s.mph = 138; s.oil = true;
  g.reset(); renderFrame(s);
  report("WORST CASE sweep to redline", g.pixels, g.rects);

  Serial.println("\n-- sustained: 30 s of driving at 30 fps --");
  uint32_t worst = 0, total = 0; int frames = 0;
  float rpmF = 900; int dir = 1;
  for (int f = 0; f < 900; f++) {
    rpmF += dir * 55; if (rpmF > 7800) dir = -1; if (rpmF < 900) dir = 1;
    s.rpm = (int)rpmF;
    s.mph = 30 + (int)(rpmF / 90);
    if ((f % 30) == 0) { s.waterPct = 40 + (f/30) % 20; s.voltsX10 = 136 + (f/60)%6; }
    g.reset();
    renderFrame(s);
    if (g.pixels > worst) worst = g.pixels;
    total += g.pixels; frames++;
  }
  report("  worst frame              ", worst, 0);
  Serial.print("  average frame               px=");
  Serial.print(total / frames);
  Serial.print("  "); Serial.print(msFor(total / frames), 2); Serial.println(" ms");

  Serial.println("\n=========================================");
  float avgMs = msFor(total / frames);
  Serial.print(" Headroom at 30 fps target: ");
  Serial.print(33.3f / avgMs, 0);
  Serial.println("x");
  Serial.println(" Full-screen clear would cost 64 ms.");
  Serial.println(" NEVER call fillScreen in a redraw path.");
  Serial.println("=========================================");
}

void loop() {}

/*
 * cluster.h — RX-7 ICU cluster renderer
 *
 * 800 x 480, 8bpp, flat green. Dirty-rectangle rendering throughout.
 *
 * DESIGN RULES, enforced by construction:
 *   1. The static background is drawn ONCE. Never cleared again.
 *   2. Every element tracks its own previous state and redraws only the
 *      pixels that actually changed.
 *   3. Digits are drawn as 7 rectangles, not font bitmaps. Changing 3->4
 *      redraws only the segments that differ - typically 2 or 3 small rects.
 *   4. Bars are segmented. Moving one segment redraws one segment.
 *   5. No gradients, no antialiasing, no alpha. Flat fills only.
 *
 * The Canvas abstraction lets the same renderer drive a real display or a
 * counting mock. See cluster_render_test.ino.
 */

#ifndef CLUSTER_H
#define CLUSTER_H

#include <Arduino.h>

/* ---------------- palette ----------------
 * RGB332: RRRGGGBB. Green-dominant by design. */
#define C_BLACK     0x00
#define C_DIM       0x08   /* barely-lit green, for unlit bar segments   */
#define C_MID       0x14   /* labels, scale marks                        */
#define C_GREEN     0x1C   /* primary readout green                      */
#define C_BRIGHT    0x1E   /* emphasis                                   */
#define C_RED       0xE0   /* redline and active warnings ONLY           */

#define SCREEN_W 800
#define SCREEN_H 480

/* ---------------- canvas ---------------- */
class Canvas {
public:
  virtual void fillRect(int x, int y, int w, int h, uint8_t c) = 0;
  virtual void flush() {}
};

/* ---------------- seven-segment digits ----------------
 * Bit order: a=0 b=1 c=2 d=3 e=4 f=5 g=6
 *
 *   aaa
 *  f   b
 *   ggg
 *  e   c
 *   ddd
 */
static const uint8_t SEG[10] = {
  0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F
};
#define SEG_BLANK 0x00

class Digit {
public:
  int x, y, w, h, t;          /* position, size, stroke thickness */
  uint8_t prev = 0xFF;        /* 0xFF = never drawn */
  uint8_t colour = C_GREEN;

  void place(int px, int py, int pw, int ph, int pt) {
    x = px; y = py; w = pw; h = ph; t = pt; prev = 0xFF;
  }

  /* Draw one segment in a given colour. Segments are plain rectangles —
   * no font bitmap, no antialiasing, nothing to blend. */
  void segColoured(Canvas &g, int i, uint8_t c) {
    int hh = h / 2;
    switch (i) {
      case 0: g.fillRect(x + t,     y,            w - 2*t, t,      c); break;
      case 1: g.fillRect(x + w - t, y + t,        t,       hh - t, c); break;
      case 2: g.fillRect(x + w - t, y + hh,       t,       hh - t, c); break;
      case 3: g.fillRect(x + t,     y + h - t,    w - 2*t, t,      c); break;
      case 4: g.fillRect(x,         y + hh,       t,       hh - t, c); break;
      case 5: g.fillRect(x,         y + t,        t,       hh - t, c); break;
      case 6: g.fillRect(x + t,     y + hh - t/2, w - 2*t, t,      c); break;
    }
  }

  /* THE KEY OPTIMISATION: only redraw segments whose state changed. */
  void draw(Canvas &g, int value, bool blank = false) {
    uint8_t want = blank ? SEG_BLANK : SEG[value % 10];
    if (want == prev) return;                 /* nothing to do at all */

    uint8_t diff = (prev == 0xFF) ? 0x7F : (uint8_t)(want ^ prev);
    for (int i = 0; i < 7; i++) {
      if (diff & (1 << i)) {
        segColoured(g, i, (want & (1 << i)) ? colour : C_BLACK);
      }
    }
    prev = want;
  }
};

/* ---------------- multi-digit field ---------------- */
template <int N>
class DigitField {
public:
  Digit d[N];
  bool leadingBlank = true;

  void place(int x, int y, int dw, int dh, int gap, int t) {
    for (int i = 0; i < N; i++) d[i].place(x + i * (dw + gap), y, dw, dh, t);
  }
  void setColour(uint8_t c) { for (int i = 0; i < N; i++) d[i].colour = c; }

  void draw(Canvas &g, int value) {
    if (value < 0) value = 0;
    int div = 1;
    for (int i = 1; i < N; i++) div *= 10;
    bool seenDigit = false;
    for (int i = 0; i < N; i++) {
      int dig = (value / div) % 10;
      bool blank = leadingBlank && !seenDigit && dig == 0 && i < N - 1;
      if (!blank) seenDigit = true;
      d[i].draw(g, dig, blank);
      div /= 10;
    }
  }
};

/* ---------------- segmented bar ----------------
 * Only the segments that change state get redrawn. Sweeping the tach from
 * 3000 to 3100 rpm touches one or two segments, not the whole bar.
 */
class SegBar {
public:
  int x, y, segW, segH, gap, count;
  int redlineFrom = -1;          /* segment index where red starts, -1 = none */
  int prevLit = -1;
  bool vertical = false;

  void place(int px, int py, int n, int sw, int sh, int g_) {
    x = px; y = py; count = n; segW = sw; segH = sh; gap = g_; prevLit = -1;
  }

  void segRect(Canvas &g, int i, uint8_t c) {
    if (vertical) g.fillRect(x, y + (count - 1 - i) * (segH + gap), segW, segH, c);
    else          g.fillRect(x + i * (segW + gap), y, segW, segH, c);
  }

  void drawAll(Canvas &g) {                 /* background pass, once */
    for (int i = 0; i < count; i++) segRect(g, i, C_DIM);
    prevLit = 0;
  }

  void draw(Canvas &g, int lit) {
    if (lit < 0) lit = 0;
    if (lit > count) lit = count;
    if (lit == prevLit) return;

    if (lit > prevLit) {                    /* light up new segments */
      for (int i = prevLit; i < lit; i++) {
        uint8_t c = (redlineFrom >= 0 && i >= redlineFrom) ? C_RED : C_GREEN;
        segRect(g, i, c);
      }
    } else {                                /* dim the ones that dropped */
      for (int i = lit; i < prevLit; i++) segRect(g, i, C_DIM);
    }
    prevLit = lit;
  }
};

/* ---------------- warning lamp ---------------- */
class Warn {
public:
  int x, y, w, h;
  bool prev = false;
  bool init = false;

  void place(int px, int py, int pw, int ph) { x=px; y=py; w=pw; h=ph; init=false; }

  void draw(Canvas &g, bool on) {
    if (init && on == prev) return;
    g.fillRect(x, y, w, h, on ? C_RED : C_BLACK);
    prev = on; init = true;
  }
};

#endif /* CLUSTER_H */

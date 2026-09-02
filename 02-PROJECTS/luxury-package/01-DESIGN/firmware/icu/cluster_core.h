/*
 * cluster_core.h — RX-7 ICU cluster renderer
 *
 * PORTABLE C++. No Arduino headers, no platform calls, no dynamic allocation.
 * The identical file compiles for:
 *   - Teensy 4.1   (icu.ino provides the display push)
 *   - Desktop      (sim_main.cpp provides an SDL2 window)
 *
 * That is the point: the preview on your PC runs THIS code, not a lookalike.
 * What you see is what the car will draw.
 *
 * ARCHITECTURE
 *   Framebuffer   8bpp buffer in RAM + tile-based dirty tracking
 *   Widgets       Digit, DigitField, SegBar, Warn, text - all rect fills
 *   Cluster       layout, static background, per-frame update
 *
 * RULE: composition into RAM is free. Only CHANGED tiles are transmitted.
 */

#ifndef CLUSTER_CORE_H
#define CLUSTER_CORE_H

#include <stdint.h>
#include <string.h>
#include <math.h>

/* ================= geometry =================
 * 12.3-inch bar panel (D-193): 1280 x 480. At 8bpp the framebuffer is
 * 614,400 bytes - PSRAM territory on the Teensy (D-170, EXTMEM in
 * icu.ino); the desktop does not care. */
static const int SCR_W = 1280;
static const int SCR_H = 480;

static const int TILE   = 16;                       /* dirty granularity */
static const int TILES_X = SCR_W / TILE;            /* 80 */
static const int TILES_Y = SCR_H / TILE;            /* 30 */

/* ================= palette, RGB332 =================
 * Format is RRRGGGBB: 8 red levels, 8 green, only 4 blue.
 *
 * EMERALD. What separates emerald from plain green is a touch of blue.
 * With 2 blue bits the only usable step is b=1 (85), so the lit tones carry
 * it and the dark tones drop to b=0 - at low luminance a fixed 85 blue
 * dominates and the hue turns teal.
 *
 * ONE LIT SHADE. Labels, bar segments, digits and the G dot are all the
 * same emerald. Nothing is emphasised by being lighter.
 *
 *   0x11  ->  RGB(  0, 145,  85)  #009155   EVERYTHING LIT
 *   0x04  ->  RGB(  0,  36,   0)  #002400   unlit / trough
 *
 * Green levels available: 0, 36, 72, 109, 145, 182, 218, 255.
 * Lit sits at 145, unlit at 36 - a 4:1 ratio, so an unlit segment reads as
 * off rather than as a dim reading. */
static const uint8_t C_BLACK  = 0x00;
static const uint8_t C_GRID   = 0x04;
static const uint8_t C_DIM    = 0x04;   /* unlit segments, off icons */
static const uint8_t C_MID    = 0x11;   /* labels                    */
static const uint8_t C_GREEN  = 0x11;   /* == C_MID                  */
static const uint8_t C_BRIGHT = 0x11;   /* == C_MID                  */
static const uint8_t C_RED    = 0xE0;   /* redline, warning          */
static const uint8_t C_AMBER  = 0xF4;   /* sensor fault              */

/* ================= sensor status =================
 * A missing sensor must NEVER render as a real zero. */
enum SensorStatus : uint8_t {
    SENSOR_OK = 0,
    SENSOR_OPEN,     /* reading pinned at full scale - disconnected  */
    SENSOR_SHORT,    /* reading pinned at zero - chafed to ground    */
    SENSOR_STALE,    /* CAN message stopped arriving                 */
    SENSOR_RANGE     /* plausible-looking but physically impossible  */
};

inline uint8_t faultColour(SensorStatus s) {
    switch (s) {
        case SENSOR_OPEN:  return C_AMBER;
        case SENSOR_SHORT: return C_RED;
        case SENSOR_STALE: return C_MID;
        case SENSOR_RANGE: return C_RED;
        default:           return 0;      /* 0 = no fault */
    }
}

/* ================= vehicle state ================= */

/* PMU channel telemetry, from CAN 0x130 (multiplexed). Drives the
 * diagnostics page - the thing no factory cluster can show you. */
static const int PMU_CHANNELS = 24;

struct VehicleState {
    int rpm = 0;
    int speed = 0;            /* mph                       */
    int waterC = 0;
    int oilPressCbar = 0;     /* 0.01 bar                  */
    int oilTempC = 0;
    int fuelPct = 0;
    int voltsX10 = 0;
    int latGx100 = 0;         /* +right, hundredths of g, +-100 full scale */
    int lonGx100 = 0;         /* +accel, -brake                            */
    int headingDeg = 0;       /* 0-359, 0 = north                          */
    int pitchDeg = 0;         /* +climbing, -descending, +-45              */

    SensorStatus sRpm   = SENSOR_OK;
    SensorStatus sSpeed = SENSOR_OK;
    SensorStatus sWater = SENSOR_OK;
    SensorStatus sOilP  = SENSOR_OK;
    SensorStatus sOilT  = SENSOR_OK;
    SensorStatus sFuel  = SENSOR_OK;
    SensorStatus sVolts = SENSOR_OK;
    SensorStatus sImu   = SENSOR_OK;

    bool wOil = false, wTemp = false, wBatt = false;
    bool wBrake = false, wFuel = false;

    /* PMU channel telemetry */
    uint16_t chCurrent[PMU_CHANNELS] = {0};   /* 0.01 A */
    uint16_t chLimit  [PMU_CHANNELS] = {0};   /* 0.01 A */
    uint8_t  chState  [PMU_CHANNELS] = {0};   /* ch_status: 0 off 1 on 2 trip 3 retry */
};

/* ================= framebuffer ================= */
class Framebuffer {
public:
    uint8_t  buf[SCR_W * SCR_H];
    uint8_t  dirty[(TILES_X * TILES_Y + 7) / 8];
    uint32_t pixelsWritten = 0;     /* instrumentation */
    uint32_t clippedPixels = 0;     /* anything drawn off-screen. Tests assert
                                     * this stays zero - silent clipping hides
                                     * layout bugs until they reach a panel. */

    void clearAll(uint8_t c) {
        memset(buf, c, sizeof(buf));
        memset(dirty, 0xFF, sizeof(dirty));
        pixelsWritten += SCR_W * SCR_H;
    }
    void clearDirty() { memset(dirty, 0, sizeof(dirty)); }

    bool tileDirty(int tx, int ty) const {
        int i = ty * TILES_X + tx;
        return (dirty[i >> 3] >> (i & 7)) & 1;
    }
    void markTile(int tx, int ty) {
        int i = ty * TILES_X + tx;
        dirty[i >> 3] |= (uint8_t)(1u << (i & 7));
    }

    void fillRect(int x, int y, int w, int h, uint8_t c) {
        if (w <= 0 || h <= 0) return;
        const uint32_t asked = (uint32_t)w * h;
        if (x < 0) { w += x; x = 0; }
        if (y < 0) { h += y; y = 0; }
        if (x + w > SCR_W) w = SCR_W - x;
        if (y + h > SCR_H) h = SCR_H - y;
        if (w <= 0 || h <= 0) { clippedPixels += asked; return; }
        clippedPixels += asked - (uint32_t)w * h;

        for (int r = y; r < y + h; r++)
            memset(&buf[r * SCR_W + x], c, (size_t)w);

        pixelsWritten += (uint32_t)w * h;

        int tx0 = x / TILE, tx1 = (x + w - 1) / TILE;
        int ty0 = y / TILE, ty1 = (y + h - 1) / TILE;
        for (int ty = ty0; ty <= ty1; ty++)
            for (int tx = tx0; tx <= tx1; tx++)
                markTile(tx, ty);
    }

    /* How many pixels would actually go over the wire this frame */
    uint32_t dirtyPixels() const {
        uint32_t n = 0;
        for (int ty = 0; ty < TILES_Y; ty++)
            for (int tx = 0; tx < TILES_X; tx++)
                if (tileDirty(tx, ty)) n += TILE * TILE;
        return n;
    }
};

/* ================= 5x7 pixel font, drawn as rects ================= */
struct Glyph { char c; uint8_t col[5]; };
static const Glyph FONT[] = {
    {'A',{0x7E,0x11,0x11,0x11,0x7E}}, {'B',{0x7F,0x49,0x49,0x49,0x36}},
    {'C',{0x3E,0x41,0x41,0x41,0x22}}, {'D',{0x7F,0x41,0x41,0x41,0x3E}},
    {'E',{0x7F,0x49,0x49,0x49,0x41}}, {'F',{0x7F,0x09,0x09,0x09,0x01}},
    {'G',{0x3E,0x41,0x49,0x49,0x7A}}, {'H',{0x7F,0x08,0x08,0x08,0x7F}},
    {'I',{0x00,0x41,0x7F,0x41,0x00}}, {'K',{0x7F,0x08,0x14,0x22,0x41}},
    {'L',{0x7F,0x40,0x40,0x40,0x40}}, {'M',{0x7F,0x02,0x0C,0x02,0x7F}},
    {'N',{0x7F,0x04,0x08,0x10,0x7F}}, {'O',{0x3E,0x41,0x41,0x41,0x3E}},
    {'P',{0x7F,0x09,0x09,0x09,0x06}}, {'R',{0x7F,0x09,0x19,0x29,0x46}},
    {'S',{0x46,0x49,0x49,0x49,0x31}}, {'T',{0x01,0x01,0x7F,0x01,0x01}},
    {'U',{0x3F,0x40,0x40,0x40,0x3F}}, {'V',{0x1F,0x20,0x40,0x20,0x1F}},
    {'W',{0x7F,0x20,0x18,0x20,0x7F}}, {'X',{0x63,0x14,0x08,0x14,0x63}},
    {'Y',{0x03,0x04,0x78,0x04,0x03}}, {'Z',{0x61,0x51,0x49,0x45,0x43}},
    {'0',{0x3E,0x51,0x49,0x45,0x3E}}, {'1',{0x00,0x42,0x7F,0x40,0x00}},
    {'2',{0x42,0x61,0x51,0x49,0x46}}, {'3',{0x21,0x41,0x45,0x4B,0x31}},
    {'4',{0x18,0x14,0x12,0x7F,0x10}}, {'5',{0x27,0x45,0x45,0x45,0x39}},
    {'6',{0x3C,0x4A,0x49,0x49,0x30}}, {'7',{0x01,0x71,0x09,0x05,0x03}},
    {'8',{0x36,0x49,0x49,0x49,0x36}}, {'9',{0x06,0x49,0x49,0x29,0x1E}},
    {'-',{0x08,0x08,0x08,0x08,0x08}}, {'.',{0x00,0x40,0x00,0x00,0x00}},
    {'%',{0x62,0x64,0x08,0x13,0x23}}, {'*',{0x06,0x09,0x09,0x06,0x00}},
    {'/',{0x20,0x10,0x08,0x04,0x02}}, {' ',{0,0,0,0,0}}
};
static const int FONT_N = sizeof(FONT) / sizeof(FONT[0]);

inline void drawText(Framebuffer &fb, const char *s, int x, int y,
                     int scale, uint8_t c) {
    int px = x;
    for (const char *p = s; *p; p++) {
        char ch = *p;
        if (ch >= 'a' && ch <= 'z') ch = (char)(ch - 32);
        const Glyph *g = nullptr;
        for (int i = 0; i < FONT_N; i++) if (FONT[i].c == ch) { g = &FONT[i]; break; }
        if (g) {
            for (int col = 0; col < 5; col++)
                for (int row = 0; row < 7; row++)
                    if (g->col[col] & (1u << row))
                        fb.fillRect(px + col * scale, y + row * scale, scale, scale, c);
        }
        px += 6 * scale;
    }
}

inline int textWidth(const char *s, int scale) {
    int n = 0;
    for (const char *p = s; *p; p++) n++;
    return n ? (n * 6 * scale - scale) : 0;
}

/* Centre a string on cx, so units of different length - F, PSI, % - share
 * one vertical axis instead of being left-aligned. */
inline void drawTextCentred(Framebuffer &fb, const char *s, int cx, int y,
                            int scale, uint8_t c) {
    drawText(fb, s, cx - textWidth(s, scale) / 2, y, scale, c);
}

/* Render an integer as text. For low-refresh pages where a full redraw is
 * cheap - the driving page uses DigitField and diffs instead.
 * decimals > 0 inserts a point that many places from the right. */
inline void drawNum(Framebuffer &fb, int v, int x, int y, int scale,
                    uint8_t c, int decimals = 0, int minDigits = 1) {
    char buf[12];
    int n = 0;
    bool neg = v < 0;
    if (neg) v = -v;
    do { buf[n++] = (char)('0' + v % 10); v /= 10; } while (v && n < 10);
    while (n < minDigits || n <= decimals) buf[n++] = '0';
    if (neg) buf[n++] = '-';

    int px = x;
    for (int i = n - 1; i >= 0; i--) {
        char s[2] = { buf[i], 0 };
        drawText(fb, s, px, y, scale, c);
        px += 6 * scale;
        if (decimals > 0 && i == decimals) {
            drawText(fb, ".", px - scale, y, scale, c);
            px += 4 * scale;
        }
    }
}

inline int numWidth(int v, int scale, int decimals = 0, int minDigits = 1) {
    int n = 0; if (v < 0) { v = -v; n++; }
    int d = 0; int t = v;
    do { d++; t /= 10; } while (t);
    if (d < minDigits) d = minDigits;
    if (d <= decimals) d = decimals + 1;
    return (n + d) * 6 * scale + (decimals > 0 ? 4 * scale : 0);
}

/* ================= seven-segment digit ================= */
static const uint8_t SEG_MAP[10] =
    { 0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x6F };
static const uint8_t SEG_DASH  = 0x40;   /* middle bar only */
static const uint8_t SEG_BLANK = 0x00;

class Digit {
public:
    int x=0,y=0,w=0,h=0,t=0;
    uint8_t prevMask = 0xFF;      /* 0xFF = never drawn */
    uint8_t prevCol  = 0;
    uint8_t colour   = C_GREEN;

    void place(int px,int py,int pw,int ph,int pt) {
        x=px; y=py; w=pw; h=ph; t=pt; prevMask=0xFF;
    }

    void segment(Framebuffer &fb, int i, uint8_t c) const {
        int hh = h / 2;
        switch (i) {
            case 0: fb.fillRect(x+t,     y,           w-2*t, t     , c); break;
            case 1: fb.fillRect(x+w-t,   y+t,         t,     hh-t  , c); break;
            case 2: fb.fillRect(x+w-t,   y+hh,        t,     hh-t  , c); break;
            case 3: fb.fillRect(x+t,     y+h-t,       w-2*t, t     , c); break;
            case 4: fb.fillRect(x,       y+hh,        t,     hh-t  , c); break;
            case 5: fb.fillRect(x,       y+t,         t,     hh-t  , c); break;
            case 6: fb.fillRect(x+t,     y+hh-t/2,    w-2*t, t     , c); break;
        }
    }

    /* Redraw ONLY the segments whose state changed. 3->4 touches 3 rects. */
    void draw(Framebuffer &fb, uint8_t mask, uint8_t col) {
        if (mask == prevMask && col == prevCol) return;
        uint8_t diff = (prevMask == 0xFF || col != prevCol) ? 0x7F
                                                            : (uint8_t)(mask ^ prevMask);
        for (int i = 0; i < 7; i++)
            if (diff & (1u << i))
                segment(fb, i, (mask & (1u << i)) ? col : C_BLACK);
        prevMask = mask; prevCol = col;
    }
};

/* ================= multi-digit field ================= */
template <int N>
class DigitField {
public:
    Digit d[N];
    bool blankLeading = true;

    /* Optional centring: digits are laid out about centreX and shift as the
     * number gains or loses a digit, so the readout stays visually centred
     * under its label instead of drifting right. -1 disables. */
    int  centreX = -1;
    int  dw=0, dh=0, dgap=0, dt=0, dy=0;
    int  prevShown = -1, prevStartX = 0;

    /* Decimal point: index of the digit it follows. -1 = none. */
    int  dpAfter = -1;
    int  prevDpX = -1, prevDpY = -1;

    void place(int x,int y,int w,int h,int gap,int t) {
        dw=w; dh=h; dgap=gap; dt=t; dy=y;
        for (int i = 0; i < N; i++) d[i].place(x + i*(w+gap), y, w, h, t);
        prevDpX = -1;
    }
    void setCentre(int cx) { centreX = cx; prevShown = -1; }
    void setDecimal(int afterIndex) { dpAfter = afterIndex; prevDpX = -1; }

    void drawPoint(Framebuffer &fb, uint8_t col) {
        if (dpAfter < 0 || dpAfter >= N) return;
        int sz = dt + 1;
        int px = d[dpAfter].x + dw + (dgap - sz) / 2;
        int py = dy + dh - sz;
        if (px != prevDpX || py != prevDpY) {
            if (prevDpX >= 0) fb.fillRect(prevDpX, prevDpY, sz, sz, C_BLACK);
            prevDpX = px; prevDpY = py;
        }
        fb.fillRect(px, py, sz, sz, col);
    }

    void draw(Framebuffer &fb, int value, uint8_t col, SensorStatus st) {
        uint8_t f = faultColour(st);
        if (f) {
            for (int i = 0; i < N; i++) d[i].draw(fb, SEG_DASH, f);
            drawPoint(fb, f);
            return;
        }
        if (value < 0) value = 0;

        if (centreX >= 0) {
            /* Fields that show every digit always occupy all N slots.
             * Only blank-leading fields shrink as the value shrinks. */
            int shown = N;
            if (blankLeading) {
                shown = 1;
                int v = value;
                while (v >= 10) { v /= 10; shown++; }
                if (shown > N) shown = N;
            }
            if (shown != prevShown) {
                int span   = shown*dw + (shown-1)*dgap;
                int startX = centreX - span/2;
                if (prevShown > 0) {                    /* wipe old footprint */
                    int oldSpan = prevShown*dw + (prevShown-1)*dgap;
                    fb.fillRect(prevStartX, dy, oldSpan, dh, C_BLACK);
                }
                for (int i = 0; i < N; i++) {
                    int slot = i - (N - shown);         /* right-aligned slots */
                    d[i].place(startX + slot*(dw+dgap), dy, dw, dh, dt);
                }
                prevShown = shown; prevStartX = startX;
            }
        }

        int div = 1;
        for (int i = 1; i < N; i++) div *= 10;
        bool seen = false;
        for (int i = 0; i < N; i++, div /= 10) {
            int dig = (value / div) % 10;
            bool blank = blankLeading && !seen && dig == 0 && i < N-1;
            if (!blank) seen = true;

            /* When centring, a blanked slot sits OUTSIDE the field to the
             * left. Drawing it - even as black - would erase whatever is
             * next to the field. The footprint wipe already cleared it, so
             * skip it entirely. Found by the overlap test, not by eye. */
            if (blank && centreX >= 0) { d[i].prevMask = SEG_BLANK; continue; }

            d[i].draw(fb, blank ? SEG_BLANK : SEG_MAP[dig], col);
        }
        drawPoint(fb, col);
    }
};

/* ================= segmented bar ================= */
class SegBar {
public:
    int x=0,y=0,segW=0,segH=0,gap=0,count=0;
    int redFrom = -1;
    int prevLit = -1;
    SensorStatus prevStatus = SENSOR_OK;
    bool prevWasFault = false;

    void place(int px,int py,int n,int sw,int sh,int g) {
        x=px; y=py; count=n; segW=sw; segH=sh; gap=g; prevLit=-1;
    }
    void segRect(Framebuffer &fb, int i, uint8_t c) const {
        fb.fillRect(x + i*(segW+gap), y, segW, segH, c);
    }
    /* Hollow outline - unmistakably not a reading */
    void segOutline(Framebuffer &fb, int i, uint8_t c) const {
        int bx = x + i*(segW+gap);
        fb.fillRect(bx, y,          segW, 1, c);
        fb.fillRect(bx, y+segH-1,   segW, 1, c);
    }

    void drawTrough(Framebuffer &fb) {
        for (int i = 0; i < count; i++) segRect(fb, i, C_DIM);
        prevLit = 0; prevWasFault = false;
    }

    void draw(Framebuffer &fb, int lit, SensorStatus st) {
        uint8_t f = faultColour(st);
        if (f) {
            if (!prevWasFault || st != prevStatus) {
                for (int i = 0; i < count; i++) { segRect(fb,i,C_BLACK); segOutline(fb,i,f); }
                prevWasFault = true; prevStatus = st; prevLit = -1;
            }
            return;
        }
        if (prevWasFault) {                       /* recovering from fault */
            for (int i = 0; i < count; i++) segRect(fb, i, C_DIM);
            prevWasFault = false; prevLit = 0;
        }
        if (lit < 0) lit = 0;
        if (lit > count) lit = count;
        if (lit == prevLit) return;

        if (lit > prevLit)
            for (int i = prevLit; i < lit; i++)
                segRect(fb, i, (redFrom >= 0 && i >= redFrom) ? C_RED : C_GREEN);
        else
            for (int i = lit; i < prevLit; i++) segRect(fb, i, C_DIM);
        prevLit = lit;
    }
};

/* ================= warning icons =================
 * 16x16 bitmaps, LSB = leftmost pixel. Drawn as rects, scaled.
 * Symbols, not labels - readable at a glance, no reading required. */
struct Icon { uint16_t row[16]; };

/* Oil can, side view. Handle left, body centre, spout rising right.
 * No drip - the can alone reads cleanly at this size.
 * Vertically centred in the 16x16 box so it aligns with everything else.
 *
 *                ##    <- spout tip
 *              ###
 *            ###
 *          ###
 *        ###
 *     ## ########      <- handle meets body
 *     #  ########
 *     #  ########
 *     #  ########
 *     ## ########
 *        ########
 */
static const Icon ICON_OIL = {{
  0x0000, 0x0000,
  0xC000, 0xE000, 0x7000, 0x3800, 0x1C00, 0x0F00,
  0x0FF6, 0x0FF1, 0x0FF1, 0x0FF1, 0x0FF6, 0x0FF0,
  0x0000, 0x0000 }};

static const Icon ICON_TEMP = {{
  0x0180,0x03C0,0x03C0,0x0BC0,0x03C0,0x0BC0,0x03C0,0x0BC0,
  0x07E0,0x0FF0,0x0FF0,0x0FF0,0x0FF0,0x07E0,0x0000,0x0000 }};

static const Icon ICON_BATT = {{
  0x0000,0x0630,0x3FFC,0x2004,0x2004,0x2184,0x2184,0x27E4,
  0x2184,0x2184,0x2004,0x27E4,0x2004,0x3FFC,0x0000,0x0000 }};

static const Icon ICON_BRAKE = {{
  0x03C0,0x0C30,0x1008,0x2184,0x4182,0x4182,0x8181,0x8001,
  0x8181,0x4182,0x4002,0x2004,0x1008,0x0C30,0x03C0,0x0000 }};

static const Icon ICON_FUEL = {{
  0x0000,0x03F8,0x0208,0x03F8,0x02F8,0x02F8,0x0208,0x0238,
  0x0228,0x0238,0x0208,0x0208,0x07FC,0x0000,0x0000,0x0000 }};

/* ramp — pitch indicator symbol */
static const Icon ICON_SLOPE = {{
  0x0000,0x0000,0x8000,0xC000,0xE000,0xF000,0xF800,0xFC00,
  0xFE00,0xFF00,0xFF80,0xFFC0,0xFFE0,0xFFF0,0xFFF8,0xFFFC }};

inline void drawIcon(Framebuffer &fb, const Icon &ic, int x, int y,
                     int scale, uint8_t c, uint8_t bg) {
    for (int r = 0; r < 16; r++)
        for (int b = 0; b < 16; b++) {
            uint8_t col = (ic.row[r] & (1u << b)) ? c : bg;
            fb.fillRect(x + b*scale, y + r*scale, scale, scale, col);
        }
}

/* ================= warning lamp, symbol ================= */
class WarnIcon {
public:
    const Icon *ic = nullptr;
    int x=0, y=0, scale=2;
    bool prev = false, init = false;

    void place(const Icon *i, int px, int py, int s) {
        ic=i; x=px; y=py; scale=s; init=false;
    }
    void draw(Framebuffer &fb, bool on) {
        if (init && on == prev) return;
        drawIcon(fb, *ic, x, y, scale, on ? C_RED : C_DIM, C_BLACK);
        prev = on; init = true;
    }
};

/* ================= G meter ================= */
class GMeter {
public:
    int cx=0, cy=0, r=0;
    int dotR = 4;
    int prevX = -9999, prevY = -9999;
    int peakX = -9999, peakY = -9999;

    void place(int x, int y, int radius) { cx=x; cy=y; r=radius; prevX=-9999; }

    /* integer midpoint circle, 1px outline */
    static void ring(Framebuffer &fb, int cx, int cy, int r, uint8_t c) {
        int x = r, y = 0, err = 0;
        while (x >= y) {
            fb.fillRect(cx+x, cy+y, 1,1, c);  fb.fillRect(cx+y, cy+x, 1,1, c);
            fb.fillRect(cx-y, cy+x, 1,1, c);  fb.fillRect(cx-x, cy+y, 1,1, c);
            fb.fillRect(cx-x, cy-y, 1,1, c);  fb.fillRect(cx-y, cy-x, 1,1, c);
            fb.fillRect(cx+y, cy-x, 1,1, c);  fb.fillRect(cx+x, cy-y, 1,1, c);
            if (err <= 0) { y++; err += 2*y + 1; }
            if (err  > 0) { x--; err -= 2*x + 1; }
        }
    }

    void drawStatic(Framebuffer &fb) {
        ring(fb, cx, cy, r,       C_MID);
        ring(fb, cx, cy, (r*2)/3, C_DIM);
        ring(fb, cx, cy, r/3,     C_DIM);
        fb.fillRect(cx - r, cy, 2*r+1, 1, C_DIM);
        fb.fillRect(cx, cy - r, 1, 2*r+1, C_DIM);
        prevX = -9999; peakX = -9999;
    }

    /* lat/lon in hundredths of g, +-100 = +-1.0 g full scale */
    void draw(Framebuffer &fb, int latX100, int lonX100, SensorStatus st) {
        uint8_t f = faultColour(st);
        int nx = cx + (latX100 * r) / 100;
        int ny = cy - (lonX100 * r) / 100;
        if (nx < cx-r) nx = cx-r;   if (nx > cx+r) nx = cx+r;
        if (ny < cy-r) ny = cy-r;   if (ny > cy+r) ny = cy+r;

        if (nx == prevX && ny == prevY && !f) return;

        /* erase old dot, then repair the graticule it sat on */
        if (prevX != -9999) {
            fb.fillRect(prevX-dotR, prevY-dotR, dotR*2, dotR*2, C_BLACK);
            fb.fillRect(cx - r, cy, 2*r+1, 1, C_DIM);
            fb.fillRect(cx, cy - r, 1, 2*r+1, C_DIM);
            ring(fb, cx, cy, (r*2)/3, C_DIM);
            ring(fb, cx, cy, r/3,     C_DIM);
            ring(fb, cx, cy, r,       C_MID);
        }
        /* peak-hold ghost, nearly free */
        int mag = latX100*latX100 + lonX100*lonX100;
        int pmag = (peakX==-9999) ? -1
                 : (peakX-cx)*(peakX-cx)*10000/(r*r) + (peakY-cy)*(peakY-cy)*10000/(r*r);
        if (peakX != -9999) fb.fillRect(peakX-2, peakY-2, 4,4, C_MID);
        if (mag > pmag) { peakX = nx; peakY = ny; }

        fb.fillRect(nx-dotR, ny-dotR, dotR*2, dotR*2, f ? f : C_BRIGHT);
        prevX = nx; prevY = ny;
    }
};

/* ================= compass ================= */
class Compass {
public:
    DigitField<3> deg;
    int sufX=0, sufY=0, sufScale=3, sufW=0;
    int prevIdx = -1;

    void place(int degX, int degY, int dw, int dh, int gap, int t,
               int suffixX, int suffixY, int scale, int suffixW) {
        deg.place(degX, degY, dw, dh, gap, t);
        deg.blankLeading = false;
        sufX=suffixX; sufY=suffixY; sufScale=scale; sufW=suffixW;
        prevIdx = -1;
    }
    static const char *cardinal(int hdg) {
        static const char *C[8] = {"N","NE","E","SE","S","SW","W","NW"};
        return C[(((hdg % 360) + 360 + 22) / 45) % 8];
    }
    void draw(Framebuffer &fb, int hdg, SensorStatus st) {
        uint8_t f = faultColour(st);
        hdg = ((hdg % 360) + 360) % 360;
        deg.draw(fb, hdg, C_GREEN, st);

        int idx = f ? -2 : (((hdg + 22) / 45) % 8);
        if (idx != prevIdx) {
            /* sufX is a CENTRE, so N and NE share an axis */
            fb.fillRect(sufX - sufW/2, sufY, sufW, sufScale * 7, C_BLACK);
            drawTextCentred(fb, f ? "--" : cardinal(hdg), sufX, sufY, sufScale,
                            f ? f : C_BRIGHT);
            prevIdx = idx;
        }
    }
};

/* ================= pitch — symbol + signed angle ================= */
class Incline {
public:
    DigitField<2> num;
    int signX=0, signY=0, signW=0, signH=0;
    int prevDeg = -999;

    void place(int numX, int numY, int dw, int dh, int gap, int t,
               int sx, int sy, int sw, int sh) {
        num.place(numX, numY, dw, dh, gap, t);
        num.blankLeading = false;
        signX=sx; signY=sy; signW=sw; signH=sh;
        prevDeg = -999;
    }

    void draw(Framebuffer &fb, int deg, SensorStatus st) {
        uint8_t f = faultColour(st);
        if (deg >  45) deg =  45;
        if (deg < -45) deg = -45;

        int a = deg < 0 ? -deg : deg;
        num.draw(fb, a, f ? f : (deg == 0 ? C_GREEN : C_BRIGHT), st);

        if (deg != prevDeg) {
            uint8_t c = f ? f : C_BRIGHT;
            fb.fillRect(signX, signY, signW, signH, C_BLACK);
            if (deg > 0) {                       /* plus */
                fb.fillRect(signX, signY + signH/2 - 2, signW, 4, c);
                fb.fillRect(signX + signW/2 - 2, signY, 4, signH, c);
            } else if (deg < 0) {                /* minus */
                fb.fillRect(signX, signY + signH/2 - 2, signW, 4, c);
            }
            prevDeg = deg;
        }
    }
};

/* ================= pages ================= */
enum Page : uint8_t { PAGE_DRIVE = 0, PAGE_DIAG, PAGE_TRIP, PAGE_COUNT };

/* PMU channel names, indexed 0..23 = O1..O24. Matches SPEC.md. */
static const char *CH_NAME[PMU_CHANNELS] = {
    "MOTOR BUS", "HEAD LOW",  "HEAD HIGH", "DEFOG",
    "FUEL PUMP", "TAIL PARK", "BRAKE",     "WIPE LOW",
    "WIPE HIGH", "ACCESSORY", "HORN",      "IGNITION",
    "LS ECU",    "LS FAN",    "COMFORT",   "BLOWER",
    "TURN L",    "TURN R",    "REVERSE",   "INTERIOR",
    "START RLY", "KEEPALIVE", "SPARE 23",  "SPARE 24"
};

/* ================= the cluster ================= */
class Cluster {
public:
    SegBar        rpmBar, water, oilP, oilT, fuel, volts;
    DigitField<4> rpmNum;
    DigitField<3> speedNum;
    DigitField<3> waterNum, oilPNum, oilTNum, fuelNum, voltsNum;
    WarnIcon      wOil, wTemp, wBatt, wBrake, wFuel;
    GMeter        gmeter;
    Compass       compass;
    Incline       incline;
    DigitField<2> gNum;

    /* Contiguous segments - gap 0. 80 x 14 = 1120, from 80 -> 1200. */
    static const int RPM_N   = 80;
    static const int RPM_RED = 66;                  /* 7000 of 8500 */
    static const int RPM_X   = 80,  RPM_Y = 38;
    static const int RPM_SW  = 14,  RPM_SH = 28, RPM_GAP = 0;
    static const int RPM_PITCH = RPM_SW + RPM_GAP;
    static const int RPM_SPAN  = RPM_N * RPM_PITCH;

    /* Right column, one axis per element. Everything centres on these.
     *
     *   [icon]      VALUE      UNIT      [============------]
     *    858         932        984        1012 .......... 1222
     */
    static const int BAR_ICON_X = 858;                 /* icon left edge   */
    static const int BAR_VAL_CX = 932;                 /* value centre     */
    static const int BAR_UNIT_CX = 984;                /* unit centre      */
    static const int BAR_X = 1012, BAR_Y = 120, BAR_STEP = 56;
    static const int BAR_N = 14,  BAR_SW = 15, BAR_SH = 26, BAR_GAP = 0;

    static const int VAL_W = 14, VAL_H = 22, VAL_GAP = 4, VAL_T = 4;
    static const int VAL_SPAN = 3*VAL_W + 2*VAL_GAP;   /* 50 */

    /* Centre - speed. 3 digits span 212, centred on 640 -> 534..746. */
    static const int SPD_CX = 640, SPD_Y = 168;
    static const int SPD_W = 62,  SPD_H = 132, SPD_GAP = 13, SPD_T = 13;

    /* Left column: THREE items. The G value is the circle's LABEL, not a
     * fourth item - it stays tucked under the graph and the group spaces
     * as one.
     *
     * Margins and gaps are proportional: roughly 45 above, 42 between,
     * 54 below. Previously the gaps were 74 with only 15 above, which made
     * the column look crammed against the tach and floating at the bottom.
     *
     *   margin    45   (tach numerals end at 97)
     *   compass   30   142..172
     *      gap    42
     *   pitch     32   214..246
     *      gap    42
     *   G group  138   288..426
     *       circle    288..388   (centre 338)
     *       label gap   8
     *       value      396..426
     *   margin    54
     */
    static const int LCOL_CX  = 120;
    static const int LCOL_TOP = 142;
    static const int LCOL_GAP = 42;
    static const int G_LBL_GAP = 8;

    static const int CMP_H   = 30;
    static const int CMP_TOP = LCOL_TOP;
    static const int CMP_CY  = CMP_TOP + CMP_H/2;                    /* 127 */

    static const int PIT_H   = 32;
    static const int PIT_TOP = CMP_TOP + CMP_H + LCOL_GAP;           /* 216 */
    static const int PIT_CY  = PIT_TOP + PIT_H/2;                    /* 232 */

    static const int G_R     = 50;
    static const int G_TOP   = PIT_TOP + PIT_H + LCOL_GAP;           /* 322 */
    static const int G_CX    = LCOL_CX;
    static const int G_CY    = G_TOP + G_R;                          /* 372 */

    static const int GNUM_H   = 30;
    static const int GNUM_TOP = G_TOP + 2*G_R + G_LBL_GAP;           /* 430 */
    static const int GNUM_CY  = GNUM_TOP + GNUM_H/2;                 /* 445 */

    static const int WARN_Y = 410, WARN_X = 440;
    static const int WARN_STEP = 92, WARN_SCALE = 2;

    /* One row. Every element shares the row's vertical centre line. */
    void row(SegBar &b, DigitField<3> &n, int i, int dpAfter) {
        int y = BAR_Y + i*BAR_STEP;
        int cy = y + BAR_SH/2;                       /* the row's axis */

        b.place(BAR_X, y, BAR_N, BAR_SW, BAR_SH, BAR_GAP);
        n.place(BAR_VAL_CX - VAL_SPAN/2, cy - VAL_H/2,
                VAL_W, VAL_H, VAL_GAP, VAL_T);
        n.blankLeading = (dpAfter < 0);
        if (dpAfter >= 0) n.setDecimal(dpAfter);
        n.setCentre(BAR_VAL_CX);
    }

    void layout() {
        rpmBar.place(RPM_X, RPM_Y, RPM_N, RPM_SW, RPM_SH, RPM_GAP);
        rpmBar.redFrom = RPM_RED;
        rpmNum.place(RPM_X + RPM_SPAN - 160, 8, 16, 24, 5, 4);

        speedNum.place(SPD_CX - 110, SPD_Y, SPD_W, SPD_H, SPD_GAP, SPD_T);
        speedNum.setCentre(SPD_CX);

        row(water, waterNum, 0, -1);      /* 190  F   */
        row(oilP,  oilPNum,  1, -1);      /*  63  PSI */
        row(oilT,  oilTNum,  2, -1);      /* 203  F   */
        row(fuel,  fuelNum,  3, -1);      /*  72  %   */
        row(volts, voltsNum, 4,  1);      /* 14.2 V   */

        /* HDG:  042  NE  */
        compass.place(LCOL_CX - 59, CMP_TOP, 20, CMP_H, 5, 5,
                      LCOL_CX + 40, CMP_CY - 10, 3, 44);
        compass.deg.setCentre(LCOL_CX - 26);

        /* PITCH:  [ramp] -12 */
        incline.place(LCOL_CX + 4, PIT_TOP - 1, 20, CMP_H, 5, 5,
                      LCOL_CX - 16, PIT_CY - 5, 14, 8);
        incline.num.setCentre(LCOL_CX + 29);

        gmeter.place(G_CX, G_CY, G_R);
        gNum.place(LCOL_CX - 40, GNUM_TOP, 22, GNUM_H, 6, 5);
        gNum.blankLeading = false;
        gNum.setDecimal(0);
        gNum.setCentre(LCOL_CX - 12);

        const Icon *ic[5] = { &ICON_OIL, &ICON_TEMP, &ICON_BATT,
                              &ICON_BRAKE, &ICON_FUEL };
        WarnIcon *w[5] = { &wOil, &wTemp, &wBatt, &wBrake, &wFuel };
        for (int i = 0; i < 5; i++)
            w[i]->place(ic[i], WARN_X + i*WARN_STEP, WARN_Y, WARN_SCALE);
    }

    /* Drawn ONCE at boot. Free forever after. Be as intricate as you like. */
    void drawStatic(Framebuffer &fb, bool grid = true) {
        fb.clearAll(C_BLACK);

        if (grid) {
            for (int x = 0; x < SCR_W; x += 40) fb.fillRect(x, 0, 1, SCR_H, C_GRID);
            for (int y = 0; y < SCR_H; y += 40) fb.fillRect(0, y, SCR_W, 1, C_GRID);
        }

        /* drafting corner brackets */
        const int B = 18, T = 2;
        fb.fillRect(10, 10, B, T, C_MID);            fb.fillRect(10, 10, T, B, C_MID);
        fb.fillRect(SCR_W-10-B, 10, B, T, C_MID);    fb.fillRect(SCR_W-10-T, 10, T, B, C_MID);
        fb.fillRect(10, SCR_H-10-T, B, T, C_MID);    fb.fillRect(10, SCR_H-10-B, T, B, C_MID);
        fb.fillRect(SCR_W-10-B, SCR_H-10-T, B, T, C_MID);
        fb.fillRect(SCR_W-10-T, SCR_H-10-B, T, B, C_MID);

        /* rpm scale */
        for (int k = 0; k <= 8; k++) {
            int x = RPM_X + (k * RPM_SPAN) / 8;
            uint8_t c = (k >= 7) ? C_RED : C_MID;
            fb.fillRect(x, RPM_Y + RPM_SH + 4, 2, 9, c);
            char s[2] = { (char)('0' + k), 0 };
            drawText(fb, s, x - 4, RPM_Y + RPM_SH + 17, 2, c);
        }
        drawText(fb, "RPM X1000", RPM_X, 14, 2, C_MID);

        /* MPH centred under the speed digits */
        drawTextCentred(fb, "MPH", SPD_CX, SPD_Y + SPD_H + 14, 5, C_MID);

        /* Gauge column. Icon left edge, unit centred - both on the row axis. */
        const Icon *gi[5] = { &ICON_TEMP, &ICON_OIL, &ICON_OIL,
                              &ICON_FUEL, &ICON_BATT };
        const char *unit[5] = { "F", "PSI", "F", "%", "V" };
        for (int i = 0; i < 5; i++) {
            int cy = BAR_Y + i*BAR_STEP + BAR_SH/2;
            drawIcon(fb, *gi[i], BAR_ICON_X, cy - 16, 2, C_MID, C_BLACK);
            drawTextCentred(fb, unit[i], BAR_UNIT_CX, cy - 7, 2, C_MID);
        }

        /* Left column - ramp icon and the G suffix, both on the axis */
        drawIcon(fb, ICON_SLOPE, LCOL_CX - 62, PIT_TOP, 2, C_MID, C_BLACK);
        gmeter.drawStatic(fb);
        drawTextCentred(fb, "G", LCOL_CX + 34, GNUM_CY - 10, 3, C_MID);

        drawText(fb, "SA22C", SCR_W - 100, 14, 2, C_DIM);

        rpmBar.drawTrough(fb);
        water.drawTrough(fb); oilP.drawTrough(fb);
        oilT.drawTrough(fb);  fuel.drawTrough(fb);
        volts.drawTrough(fb);
    }

    /* Called every frame. Only changed pixels are touched. */
    void update(Framebuffer &fb, const VehicleState &s) {
        if (page != PAGE_DRIVE) { if (page == PAGE_DIAG) updateDiag(fb, s); return; }
        rpmBar.draw(fb, (s.rpm * RPM_N) / 8500, s.sRpm);
        rpmNum.draw(fb, s.rpm, C_GREEN, s.sRpm);
        speedNum.draw(fb, s.speed, C_BRIGHT, s.sSpeed);

        water.draw(fb, (s.waterC        * BAR_N) / 130, s.sWater);
        oilP .draw(fb, (s.oilPressCbar  * BAR_N) / 800, s.sOilP);
        oilT .draw(fb, (s.oilTempC      * BAR_N) / 150, s.sOilT);
        fuel .draw(fb, (s.fuelPct       * BAR_N) / 100, s.sFuel);

        /* volts bar spans 10.0 - 16.0 V, where the useful detail lives */
        int vLit = ((s.voltsX10 - 100) * BAR_N) / 60;
        if (vLit < 0) vLit = 0;
        volts.draw(fb, vLit, s.sVolts);

        /* Sensors are read in metric; the display converts. Keeping the raw
         * units in VehicleState means the CAN map and the logs stay metric
         * and only the readout is imperial. */
        int waterF = (s.waterC   * 9) / 5 + 32;
        int oilTF  = (s.oilTempC * 9) / 5 + 32;
        int oilPsi = (s.oilPressCbar * 145) / 1000;   /* 1 bar = 14.5 psi */

        waterNum.draw(fb, waterF,      C_GREEN, s.sWater);
        oilPNum .draw(fb, oilPsi,      C_GREEN, s.sOilP);
        oilTNum .draw(fb, oilTF,       C_GREEN, s.sOilT);
        fuelNum .draw(fb, s.fuelPct,   C_GREEN, s.sFuel);
        voltsNum.draw(fb, s.voltsX10,  C_GREEN, s.sVolts);

        gmeter.draw(fb, s.latGx100, s.lonGx100, s.sImu);
        compass.draw(fb, s.headingDeg, s.sImu);
        incline.draw(fb, s.pitchDeg, s.sImu);

        /* resultant G magnitude, integer sqrt - no float needed.
         * mag is hundredths; /10 gives tenths for the 0.0 readout. */
        int sq = s.latGx100*s.latGx100 + s.lonGx100*s.lonGx100;
        int mag = 0; while ((mag+1)*(mag+1) <= sq) mag++;
        int tenths = mag / 10;
        if (tenths > 99) tenths = 99;
        gNum.draw(fb, tenths, C_BRIGHT, s.sImu);

        wOil.draw(fb, s.wOil);     wTemp.draw(fb, s.wTemp);
        wBatt.draw(fb, s.wBatt);   wBrake.draw(fb, s.wBrake);
        wFuel.draw(fb, s.wFuel);
    }

    /* ================= page control ================= */
    Page page = PAGE_DRIVE;

    /* Widgets cache their previous state. After any full repaint they must be
     * told to start again. Lives here, not in the host - it was drifting out
     * of date every time a widget was added. */
    void invalidate() {
        SegBar *bars[6] = { &rpmBar, &water, &oilP, &oilT, &fuel, &volts };
        for (int i = 0; i < 6; i++) bars[i]->prevLit = -1;

        DigitField<3> *f3[6] = { &speedNum, &waterNum, &oilPNum,
                                 &oilTNum, &fuelNum, &voltsNum };
        for (int k = 0; k < 6; k++) {
            for (int i = 0; i < 3; i++) f3[k]->d[i].prevMask = 0xFF;
            f3[k]->prevDpX = -1; f3[k]->prevShown = -1;
        }
        for (int i = 0; i < 4; i++) rpmNum.d[i].prevMask = 0xFF;
        for (int i = 0; i < 3; i++) compass.deg.d[i].prevMask = 0xFF;
        for (int i = 0; i < 2; i++) incline.num.d[i].prevMask = 0xFF;
        for (int i = 0; i < 2; i++) gNum.d[i].prevMask = 0xFF;
        gNum.prevDpX = -1;

        wOil.init = wTemp.init = wBatt.init = wBrake.init = wFuel.init = false;
        gmeter.prevX = -9999;
        compass.prevIdx = -1;
        incline.prevDeg = -999;
    }

    void setPage(Framebuffer &fb, Page p, bool grid = false) {
        page = p;
        invalidate();
        switch (p) {
            case PAGE_DIAG:  drawStaticDiag(fb);  break;
            case PAGE_TRIP:  drawStaticTrip(fb);  break;
            default:         drawStatic(fb, grid); break;
        }
    }
    void nextPage(Framebuffer &fb) {
        setPage(fb, (Page)((page + 1) % PAGE_COUNT));
    }

    /* ================= diagnostics page =================
     * 24 channels, live current, soft-fuse setpoint, state.
     * Read while parked, so a 2 Hz full redraw of the dynamic area is fine -
     * that is what makes this page affordable at all. */
    static const int DG_ROWS = 12;
    static const int DG_TOP  = 56, DG_STEP = 34;
    static const int DG_COL0 = 18, DG_COL1 = 658;
    static const int DG_TAG = 0, DG_NAME = 34, DG_CUR = 152,
                     DG_LIM = 222, DG_BAR = 286, DG_BAR_W = 200;

    void drawStaticDiag(Framebuffer &fb) {
        fb.clearAll(C_BLACK);
        drawText(fb, "PMU CHANNELS", 18, 16, 3, C_MID);
        drawText(fb, "A     LIMIT", DG_COL0 + DG_CUR, 34, 1, C_DIM);
        drawText(fb, "A     LIMIT", DG_COL1 + DG_CUR, 34, 1, C_DIM);
        fb.fillRect(18, 48, SCR_W - 36, 1, C_MID);

        for (int i = 0; i < PMU_CHANNELS; i++) {
            int col = (i < DG_ROWS) ? DG_COL0 : DG_COL1;
            int y   = DG_TOP + (i % DG_ROWS) * DG_STEP;
            drawText(fb, "O", col + DG_TAG, y, 2, C_DIM);
            drawNum(fb, i + 1, col + DG_TAG + 12, y, 2, C_DIM);
            drawText(fb, CH_NAME[i], col + DG_NAME, y, 2, C_MID);
        }
    }

    void updateDiag(Framebuffer &fb, const VehicleState &s) {
        for (int i = 0; i < PMU_CHANNELS; i++) {
            int col = (i < DG_ROWS) ? DG_COL0 : DG_COL1;
            int y   = DG_TOP + (i % DG_ROWS) * DG_STEP;

            uint8_t st = s.chState[i];
            uint8_t c  = (st == 2) ? C_RED : (st == 3) ? C_AMBER
                       : (st == 1) ? C_GREEN : C_DIM;

            /* clear only the dynamic span of the row */
            fb.fillRect(col + DG_CUR, y, DG_BAR + DG_BAR_W - DG_CUR, 16, C_BLACK);

            drawNum(fb, s.chCurrent[i], col + DG_CUR, y, 2, c, 2);
            drawNum(fb, s.chLimit[i],   col + DG_LIM, y, 2, C_DIM, 2);

            /* proportion of limit, so a channel near its trip point is obvious */
            int lit = s.chLimit[i] ? (s.chCurrent[i] * DG_BAR_W) / s.chLimit[i] : 0;
            if (lit > DG_BAR_W) lit = DG_BAR_W;
            fb.fillRect(col + DG_BAR, y + 3, DG_BAR_W, 10, C_DIM);
            if (lit > 0) fb.fillRect(col + DG_BAR, y + 3, lit, 10, c);
        }
    }

    /* Trip page static frame. Values are drawn by drawTripPage() in stats.h,
     * which is where the Stats struct lives. */
    void drawStaticTrip(Framebuffer &fb) {
        fb.clearAll(C_BLACK);
        drawText(fb, "TRIP", 18, 16, 3, C_MID);
        fb.fillRect(18, 48, SCR_W - 36, 1, C_MID);
    }
};

#endif /* CLUSTER_CORE_H */

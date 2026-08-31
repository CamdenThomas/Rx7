/*
 * bt817.h — BT817 EVE display driver for the ICU  (F-008, D-193)
 *
 * The panel is driven as ONE static bitmap: the display list is written
 * once at init and never touched again. Every frame we DMA only the dirty
 * tiles of the RGB332 framebuffer into RAM_G (the BT817's 1 MB graphics
 * RAM — 1280x480 @ 8bpp = 614,400 B fits with room to spare). The BT817
 * scans RAM_G out to the panel continuously, so a tile lands on glass the
 * next scanout after it is written. No display-list rebuild, no OS, no
 * boot — REG_PCLK starts the panel a few ms after power.
 *
 * PORTABLE: everything except the HAL at the bottom compiles on the
 * desktop. tests/test_bt817.cpp mocks the five bt817_hal_* calls and
 * verifies init traffic, display-list encoding, blit addressing and the
 * dirty-run merge against expected byte streams.
 *
 * !! V-084: every timing constant in BT817_TIMINGS below is a PLACEHOLDER
 * !! for a generic 1280x480 panel. Set them from the chosen glass's
 * !! datasheet before first light. Marked [V-084] individually.
 */

#pragma once
#include <stdint.h>
#include <string.h>

/* ---------------- HAL — the only platform-specific surface -------------
 * Teensy implementations live at the bottom of this file (#ifdef ARDUINO).
 * Desktop tests provide their own and record the traffic.               */
void    bt817_hal_init();                              /* pins + SPI.begin */
void    bt817_hal_select(bool sel);                    /* CS, active low   */
void    bt817_hal_powerdown(bool pd);                  /* PDN, active low  */
void    bt817_hal_delay(uint32_t ms);
uint8_t bt817_hal_xfer(uint8_t b);                     /* one byte, duplex */
void    bt817_hal_write(const uint8_t* p, uint32_t n); /* bulk write       */

/* ---------------- memory map (FT81x/BT81x standard) -------------------- */
enum : uint32_t {
    BT_RAM_G        = 0x000000,
    BT_RAM_DL       = 0x300000,
    REG_ID          = 0x302000,
    REG_CPURESET    = 0x302020,
    REG_HCYCLE      = 0x30202C,
    REG_HOFFSET     = 0x302030,
    REG_HSIZE       = 0x302034,
    REG_HSYNC0      = 0x302038,
    REG_HSYNC1      = 0x30203C,
    REG_VCYCLE      = 0x302040,
    REG_VOFFSET     = 0x302044,
    REG_VSIZE       = 0x302048,
    REG_VSYNC0      = 0x30204C,
    REG_VSYNC1      = 0x302050,
    REG_DLSWAP      = 0x302054,
    REG_OUTBITS     = 0x30205C,
    REG_DITHER      = 0x302060,
    REG_SWIZZLE     = 0x302064,
    REG_CSPREAD     = 0x302068,
    REG_PCLK_POL    = 0x30206C,
    REG_PCLK        = 0x302070,
    REG_GPIO_DIR    = 0x302090,
    REG_GPIO        = 0x302094,
    REG_PWM_DUTY    = 0x3020D4,
};

/* ---------------- panel timing [V-084 — ALL PLACEHOLDERS] -------------- */
struct Bt817Timings {
    uint16_t hcycle, hoffset, hsync0, hsync1;
    uint16_t vcycle, voffset, vsync0, vsync1;
    uint8_t  pclk, pclk_pol, swizzle, cspread;
};
static const Bt817Timings BT817_TIMINGS = {
    /* hcycle  */ 1440,  /* [V-084] total px per line            */
    /* hoffset */ 158,   /* [V-084]                              */
    /* hsync0  */ 0,     /* [V-084]                              */
    /* hsync1  */ 30,    /* [V-084]                              */
    /* vcycle  */ 500,   /* [V-084] total lines per frame        */
    /* voffset */ 18,    /* [V-084]                              */
    /* vsync0  */ 0,     /* [V-084]                              */
    /* vsync1  */ 3,     /* [V-084]                              */
    /* pclk    */ 1,     /* [V-084] sysclk divider — check freq! */
    /* pol     */ 0,     /* [V-084]                              */
    /* swizzle */ 0,     /* [V-084] RGB pin order                */
    /* cspread */ 0,     /* [V-084]                              */
};

/* ---------------- display-list word encoders --------------------------- */
namespace btdl {
    enum { FMT_RGB332 = 4, PRIM_BITMAPS = 1, FILTER_NEAREST = 0 };
    inline uint32_t clearColor(uint32_t rgb) { return (2u  << 24) | (rgb & 0xFFFFFF); }
    inline uint32_t clearAll()               { return (0x26u << 24) | 7; }
    inline uint32_t bitmapHandle(uint8_t h)  { return (5u  << 24) | h; }
    inline uint32_t bitmapSource(uint32_t a) { return (1u  << 24) | (a & 0xFFFFFF); }
    inline uint32_t bitmapLayout(uint8_t fmt, uint32_t stride, uint32_t h) {
        return (7u << 24) | ((uint32_t)fmt << 19) | ((stride & 0x3FF) << 9) | (h & 0x1FF);
    }
    inline uint32_t bitmapLayoutH(uint32_t stride, uint32_t h) {
        return (0x28u << 24) | (((stride >> 10) & 3) << 2) | ((h >> 9) & 3);
    }
    inline uint32_t bitmapSize(uint8_t filt, uint32_t w, uint32_t h) {
        return (8u << 24) | ((uint32_t)filt << 20) | ((w & 0x1FF) << 9) | (h & 0x1FF);
    }
    inline uint32_t bitmapSizeH(uint32_t w, uint32_t h) {
        return (0x29u << 24) | (((w >> 9) & 3) << 2) | ((h >> 9) & 3);
    }
    inline uint32_t begin(uint8_t prim)      { return (0x1Fu << 24) | prim; }
    inline uint32_t vertexFormat(uint8_t f)  { return (0x27u << 24) | f; }
    inline uint32_t vertex2f(int32_t x, int32_t y) {
        return (1u << 30) | (((uint32_t)x & 0x7FFF) << 15) | ((uint32_t)y & 0x7FFF);
    }
    inline uint32_t end()                    { return 0x21u << 24; }
    inline uint32_t display()                { return 0; }
}

/* ---------------- the driver ------------------------------------------- */
struct Bt817 {
    bool     ok = false;      /* init succeeded — safe to blit            */
    uint16_t w  = 0, h = 0;

    /* ---- low-level transactions ---- */
    void hostCmd(uint8_t cmd) {
        bt817_hal_select(true);
        bt817_hal_xfer(cmd); bt817_hal_xfer(0); bt817_hal_xfer(0);
        bt817_hal_select(false);
    }
    void memWrite(uint32_t addr, const uint8_t* p, uint32_t n) {
        bt817_hal_select(true);
        bt817_hal_xfer(0x80 | ((addr >> 16) & 0x3F));
        bt817_hal_xfer((addr >> 8) & 0xFF);
        bt817_hal_xfer(addr & 0xFF);
        bt817_hal_write(p, n);
        bt817_hal_select(false);
    }
    void memRead(uint32_t addr, uint8_t* p, uint32_t n) {
        bt817_hal_select(true);
        bt817_hal_xfer((addr >> 16) & 0x3F);
        bt817_hal_xfer((addr >> 8) & 0xFF);
        bt817_hal_xfer(addr & 0xFF);
        bt817_hal_xfer(0);                      /* dummy */
        for (uint32_t i = 0; i < n; i++) p[i] = bt817_hal_xfer(0xFF);
        bt817_hal_select(false);
    }
    void wr8 (uint32_t a, uint8_t v)  { memWrite(a, &v, 1); }
    void wr16(uint32_t a, uint16_t v) { uint8_t b[2] = { (uint8_t)v, (uint8_t)(v >> 8) }; memWrite(a, b, 2); }
    void wr32(uint32_t a, uint32_t v) {
        uint8_t b[4] = { (uint8_t)v, (uint8_t)(v >> 8), (uint8_t)(v >> 16), (uint8_t)(v >> 24) };
        memWrite(a, b, 4);
    }
    uint8_t rd8(uint32_t a) { uint8_t v = 0; memRead(a, &v, 1); return v; }

    /* ---- bring-up. Returns false (ok=false) if the chip never answers,
     * so the host can keep running headless and report over serial. ---- */
    bool init(uint16_t width, uint16_t height, const Bt817Timings& t = BT817_TIMINGS) {
        w = width; h = height;
        bt817_hal_init();
        bt817_hal_powerdown(true);  bt817_hal_delay(6);
        bt817_hal_powerdown(false); bt817_hal_delay(21);
        /* [V-084] if the carrier fits an external crystal, send CLKEXT
         * (0x44) here before ACTIVE. Internal oscillator assumed for now. */
        hostCmd(0x00);                       /* ACTIVE */
        bt817_hal_delay(40);

        int tries = 50;                      /* ~250 ms */
        while (rd8(REG_ID) != 0x7C && --tries) bt817_hal_delay(5);
        if (!tries) return ok = false;
        tries = 50;
        while (rd8(REG_CPURESET) != 0 && --tries) bt817_hal_delay(5);
        if (!tries) return ok = false;

        wr16(REG_HCYCLE,  t.hcycle);   wr16(REG_HOFFSET, t.hoffset);
        wr16(REG_HSYNC0,  t.hsync0);   wr16(REG_HSYNC1,  t.hsync1);
        wr16(REG_VCYCLE,  t.vcycle);   wr16(REG_VOFFSET, t.voffset);
        wr16(REG_VSYNC0,  t.vsync0);   wr16(REG_VSYNC1,  t.vsync1);
        wr16(REG_HSIZE,   w);          wr16(REG_VSIZE,   h);
        wr8 (REG_SWIZZLE, t.swizzle);  wr8 (REG_PCLK_POL, t.pclk_pol);
        wr8 (REG_CSPREAD, t.cspread);  wr8 (REG_DITHER,  0);

        writeDisplayList();
        wr8(REG_DLSWAP, 2);                  /* DLSWAP_FRAME */

        wr8(REG_GPIO_DIR, rd8(REG_GPIO_DIR) | 0x80);   /* DISP pin out  */
        wr8(REG_GPIO,     rd8(REG_GPIO)     | 0x80);   /* DISP high     */
        wr8(REG_PCLK,     t.pclk);                     /* scanout START */
        wr8(REG_PWM_DUTY, 128);                        /* backlight     */
        return ok = true;
    }

    /* One static bitmap covering the panel, sourced at RAM_G offset 0. */
    void writeDisplayList() {
        using namespace btdl;
        const uint32_t dl[] = {
            clearColor(0x000000),
            clearAll(),
            bitmapHandle(0),
            bitmapSource(BT_RAM_G),
            bitmapLayout(FMT_RGB332, w, h),
            bitmapLayoutH(w, h),
            bitmapSize(FILTER_NEAREST, w, h),
            bitmapSizeH(w, h),
            begin(PRIM_BITMAPS),
            vertexFormat(0),                 /* whole-pixel units */
            vertex2f(0, 0),
            end(),
            display(),
        };
        uint8_t bytes[sizeof(dl)];
        for (uint32_t i = 0; i < sizeof(dl) / 4; i++) {
            bytes[i * 4 + 0] = (uint8_t)(dl[i]);
            bytes[i * 4 + 1] = (uint8_t)(dl[i] >> 8);
            bytes[i * 4 + 2] = (uint8_t)(dl[i] >> 16);
            bytes[i * 4 + 3] = (uint8_t)(dl[i] >> 24);
        }
        memWrite(BT_RAM_DL, bytes, sizeof(bytes));
    }

    /* Copy a rectangle of the framebuffer into RAM_G, one scanline-run
     * per transaction (rows are contiguous in both memories). */
    uint32_t blitRect(const uint8_t* fbuf, uint32_t fbW,
                      uint32_t x0, uint32_t y0, uint32_t rw, uint32_t rh) {
        for (uint32_t r = 0; r < rh; r++) {
            uint32_t off = (y0 + r) * fbW + x0;
            memWrite(BT_RAM_G + off, fbuf + off, rw);
        }
        return rw * rh;
    }

    /* Walk the dirty tile map, merge horizontal runs of dirty tiles, and
     * push each run as one blitRect. FB is the cluster Framebuffer type
     * (templated so the desktop test can use the real one). */
    template <class FB>
    uint32_t pushDirty(const FB& fb, int tile, int tilesX, int tilesY, int scrW) {
        if (!ok) return 0;
        uint32_t sent = 0;
        for (int ty = 0; ty < tilesY; ty++) {
            int tx = 0;
            while (tx < tilesX) {
                if (!fb.tileDirty(tx, ty)) { tx++; continue; }
                int run = tx;
                while (run < tilesX && fb.tileDirty(run, ty)) run++;
                sent += blitRect(fb.buf, scrW,
                                 (uint32_t)tx * tile, (uint32_t)ty * tile,
                                 (uint32_t)(run - tx) * tile, tile);
                tx = run;
            }
        }
        return sent;
    }
};

/* ---------------- Teensy HAL ------------------------------------------- */
#ifdef ARDUINO
#include <Arduino.h>
#include <SPI.h>

/* Provisional carrier pins (H-001 — firm up with the PCB): */
#define BT817_PIN_CS   10
#define BT817_PIN_PDN  9
/* SPI0: MOSI 11, MISO 12, SCK 13.
 * [V-084] 20 MHz single SPI for bring-up. BT817 tops out at 30 MHz single
 * SPI; QSPI is a later optimisation if push time ever matters. */
static SPISettings bt817_spi(20000000, MSBFIRST, SPI_MODE0);

inline void bt817_hal_init() {
    pinMode(BT817_PIN_CS, OUTPUT);  digitalWrite(BT817_PIN_CS, HIGH);
    pinMode(BT817_PIN_PDN, OUTPUT); digitalWrite(BT817_PIN_PDN, HIGH);
    SPI.begin();
}
inline void bt817_hal_select(bool sel) {
    if (sel) { SPI.beginTransaction(bt817_spi); digitalWrite(BT817_PIN_CS, LOW); }
    else     { digitalWrite(BT817_PIN_CS, HIGH); SPI.endTransaction(); }
}
inline void bt817_hal_powerdown(bool pd) { digitalWrite(BT817_PIN_PDN, pd ? LOW : HIGH); }
inline void bt817_hal_delay(uint32_t ms) { delay(ms); }
inline uint8_t bt817_hal_xfer(uint8_t b)  { return SPI.transfer(b); }
inline void bt817_hal_write(const uint8_t* p, uint32_t n) {
    SPI.transfer((void*)p, nullptr, n);      /* non-destructive bulk write */
}
#endif /* ARDUINO */

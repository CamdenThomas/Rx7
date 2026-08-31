/*
 * test_bt817.cpp — desktop verification of the BT817 driver (F-008)
 *
 * Mocks the five bt817_hal_* calls, records every SPI transaction, and
 * checks: init handshake and register writes, display-list encoding
 * against independently hand-computed words, blit addressing byte-for-
 * byte, and the dirty-run merge over the REAL cluster Framebuffer.
 *
 * Build (w64devkit on PATH):
 *   g++ test_bt817.cpp -o test_bt817.exe -std=c++17 -O2 -I../icu && test_bt817
 */
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <vector>

#include "cluster_core.h"

/* ---------- recording mock HAL ---------- */
struct Txn { std::vector<uint8_t> bytes; };
static std::vector<Txn> g_txns;
static Txn g_cur;
static bool g_sel = false;

void bt817_hal_init() {}
void bt817_hal_powerdown(bool) {}
void bt817_hal_delay(uint32_t) {}
void bt817_hal_select(bool sel) {
    if (sel) { g_cur.bytes.clear(); g_sel = true; }
    else     { g_txns.push_back(g_cur); g_sel = false; }
}
uint8_t bt817_hal_xfer(uint8_t b) {
    g_cur.bytes.push_back(b);
    /* answer reads: header top bits 00, dummy byte, then data */
    if (g_cur.bytes.size() >= 5 && (g_cur.bytes[0] & 0xC0) == 0x00) {
        uint32_t addr = ((uint32_t)(g_cur.bytes[0] & 0x3F) << 16)
                      | ((uint32_t)g_cur.bytes[1] << 8) | g_cur.bytes[2];
        if (addr == 0x302000) return 0x7C;   /* REG_ID       */
        if (addr == 0x302020) return 0x00;   /* REG_CPURESET */
        return 0x00;                         /* GPIO etc.    */
    }
    return 0;
}
void bt817_hal_write(const uint8_t* p, uint32_t n) {
    g_cur.bytes.insert(g_cur.bytes.end(), p, p + n);
}

#include "bt817.h"

/* ---------- tiny assert harness (same style as test_suite) ---------- */
static int g_pass = 0, g_fail = 0;
#define CHECK(cond, msg) do { \
    if (cond) g_pass++; \
    else { g_fail++; printf("  FAIL %s:%d  %s\n", __FILE__, __LINE__, msg); } \
} while (0)

/* find the last write transaction addressed to `addr` and return payload */
static const uint8_t* findWrite(uint32_t addr, size_t* len = nullptr) {
    for (int i = (int)g_txns.size() - 1; i >= 0; i--) {
        const auto& b = g_txns[i].bytes;
        if (b.size() < 4 || !(b[0] & 0x80)) continue;
        uint32_t a = ((uint32_t)(b[0] & 0x3F) << 16) | ((uint32_t)b[1] << 8) | b[2];
        if (a == addr) { if (len) *len = b.size() - 3; return b.data() + 3; }
    }
    return nullptr;
}
static uint32_t le32(const uint8_t* p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

int main() {
    printf("-- BT817 driver verification --\n");

    /* ================= 1. init handshake + registers ================= */
    Bt817 d;
    bool up = d.init(SCR_W, SCR_H);
    CHECK(up && d.ok, "init reports success against answering mock");

    /* first transaction after power sequencing must be host cmd ACTIVE */
    CHECK(!g_txns.empty() && g_txns[0].bytes.size() == 3 &&
          g_txns[0].bytes[0] == 0x00 && g_txns[0].bytes[1] == 0 && g_txns[0].bytes[2] == 0,
          "first SPI transaction is host command ACTIVE (00 00 00)");

    size_t n;
    const uint8_t* p = findWrite(REG_HSIZE, &n);
    CHECK(p && n == 2 && p[0] == (1280 & 0xFF) && p[1] == (1280 >> 8),
          "REG_HSIZE = 1280 little-endian");
    p = findWrite(REG_VSIZE, &n);
    CHECK(p && n == 2 && p[0] == (480 & 0xFF) && p[1] == (480 >> 8),
          "REG_VSIZE = 480 little-endian");
    p = findWrite(REG_HCYCLE, &n);
    CHECK(p && n == 2 && (p[0] | (p[1] << 8)) == BT817_TIMINGS.hcycle, "REG_HCYCLE from timing table");
    p = findWrite(REG_PCLK, &n);
    CHECK(p && n == 1 && p[0] == BT817_TIMINGS.pclk, "REG_PCLK written (scanout started)");
    p = findWrite(REG_PWM_DUTY, &n);
    CHECK(p && n == 1 && p[0] == 128, "backlight PWM set");
    p = findWrite(REG_DLSWAP, &n);
    CHECK(p && n == 1 && p[0] == 2, "DLSWAP_FRAME issued");
    p = findWrite(REG_GPIO, &n);
    CHECK(p && n == 1 && (p[0] & 0x80), "DISP GPIO driven high");

    /* ============ 2. display list — independently computed =========== */
    p = findWrite(BT_RAM_DL, &n);
    CHECK(p != nullptr, "display list written to RAM_DL");
    CHECK(n == 13 * 4, "display list is 13 words");
    if (p && n == 52) {
        /* hand-computed for 1280x480 RGB332 (fmt 4):
         *   LAYOUT   = 7<<24 | 4<<19 | (1280&0x3FF)<<9 | 480 = 0x072201E0
         *   LAYOUT_H = 0x28<<24 | (1280>>10)<<2 | 480>>9     = 0x28000004
         *   SIZE     = 8<<24 | (1280&0x1FF)<<9 | 480         = 0x080201E0
         *   SIZE_H   = 0x29<<24 | (1280>>9)<<2 | 480>>9      = 0x29000008 */
        CHECK(le32(p +  0) == 0x02000000u, "CLEAR_COLOR_RGB black");
        CHECK(le32(p +  4) == 0x26000007u, "CLEAR(1,1,1)");
        CHECK(le32(p +  8) == 0x05000000u, "BITMAP_HANDLE 0");
        CHECK(le32(p + 12) == 0x01000000u, "BITMAP_SOURCE RAM_G+0");
        CHECK(le32(p + 16) == 0x072201E0u, "BITMAP_LAYOUT RGB332 stride 1280 h 480");
        CHECK(le32(p + 20) == 0x28000004u, "BITMAP_LAYOUT_H carries stride bit 10");
        CHECK(le32(p + 24) == 0x080201E0u, "BITMAP_SIZE 1280x480 nearest");
        CHECK(le32(p + 28) == 0x29000008u, "BITMAP_SIZE_H carries width bit 9-10");
        CHECK(le32(p + 32) == 0x1F000001u, "BEGIN(BITMAPS)");
        CHECK(le32(p + 36) == 0x27000000u, "VERTEX_FORMAT(0) whole pixels");
        CHECK(le32(p + 40) == 0x40000000u, "VERTEX2F(0,0)");
        CHECK(le32(p + 44) == 0x21000000u, "END");
        CHECK(le32(p + 48) == 0x00000000u, "DISPLAY");
    }

    /* =================== 3. blit addressing, exact =================== */
    g_txns.clear();
    static uint8_t fake[SCR_H * SCR_W];
    for (uint32_t i = 0; i < sizeof(fake); i++) fake[i] = (uint8_t)(i * 7 + 3);
    uint32_t sent = d.blitRect(fake, SCR_W, 48, 32, 32, 16);
    CHECK(sent == 32 * 16, "blitRect reports w*h pixels");
    CHECK(g_txns.size() == 16, "one transaction per scanline row");
    bool addrOk = true, dataOk = true;
    for (uint32_t r = 0; r < g_txns.size() && r < 16; r++) {
        const auto& b = g_txns[r].bytes;
        uint32_t want = (32 + r) * SCR_W + 48;      /* RAM_G base is 0 */
        if (b.size() != 3 + 32) { addrOk = false; break; }
        uint32_t a = ((uint32_t)(b[0] & 0x3F) << 16) | ((uint32_t)b[1] << 8) | b[2];
        if (!(b[0] & 0x80) || a != want) addrOk = false;
        if (memcmp(b.data() + 3, fake + want, 32) != 0) dataOk = false;
    }
    CHECK(addrOk, "every row lands at RAM_G + (y*1280 + x)");
    CHECK(dataOk, "payload bytes match the framebuffer rows exactly");

    /* ============ 4. dirty-run merge over the real Framebuffer ======= */
    static Framebuffer fb;                    /* 614 KB — static, not stack */
    memset(&fb, 0, sizeof(fb));
    for (uint32_t i = 0; i < sizeof(fb.buf); i++) fb.buf[i] = (uint8_t)(i ^ (i >> 8));
    fb.clearDirty();
    fb.markTile(2, 3); fb.markTile(3, 3); fb.markTile(4, 3);   /* run of 3 */
    fb.markTile(10, 3);                                        /* lone     */
    fb.markTile(5, 7);                                         /* lone     */

    g_txns.clear();
    sent = d.pushDirty(fb, TILE, TILES_X, TILES_Y, SCR_W);
    CHECK(sent == (3 + 1 + 1) * TILE * TILE, "pushDirty pixel count = 5 tiles");
    /* run of 3 = 16 rows, lone x2 = 32 rows -> 48 transactions total */
    CHECK(g_txns.size() == 48, "adjacent tiles merged: 3 runs -> 48 row writes");
    /* first transaction: row 0 of the merged run: addr (3*16)*1280 + 2*16,
     * length 3 + 3*16 bytes */
    if (!g_txns.empty()) {
        const auto& b = g_txns[0].bytes;
        uint32_t a = ((uint32_t)(b[0] & 0x3F) << 16) | ((uint32_t)b[1] << 8) | b[2];
        CHECK(a == (uint32_t)(3 * TILE) * SCR_W + 2 * TILE, "merged run starts at tile (2,3)");
        CHECK(b.size() == 3u + 3 * TILE, "merged run row is 48 px wide");
        CHECK(memcmp(b.data() + 3, fb.buf + a, 3 * TILE) == 0, "merged payload matches fb");
    }

    /* clean fb pushes nothing */
    fb.clearDirty();
    g_txns.clear();
    sent = d.pushDirty(fb, TILE, TILES_X, TILES_Y, SCR_W);
    CHECK(sent == 0 && g_txns.empty(), "clean framebuffer pushes zero bytes");

    /* not-ok driver pushes nothing (headless mode) */
    Bt817 dead;
    fb.markTile(0, 0);
    g_txns.clear();
    CHECK(dead.pushDirty(fb, TILE, TILES_X, TILES_Y, SCR_W) == 0 && g_txns.empty(),
          "uninitialised driver stays silent (headless fallback)");

    printf("\n passed %d   failed %d\n", g_pass, g_fail);
    printf(g_fail ? " BT817 TESTS FAILED\n" : " ALL BT817 TESTS PASSED\n");
    return g_fail ? 1 : 0;
}

/*
 * test_radio.cpp — desktop verification of the battery path (F-015):
 * the Ionic BMS decoder (icu_radio/ionic_decode.h) and the C3 -> Teensy line
 * protocol with the 0x220 / 0x221 frames built from it (icu/radio_link.h).
 *
 * Build (g++ on PATH):
 *   g++ test_radio.cpp -o test_radio -std=c++17 -O2 && ./test_radio
 */
#include <cstdio>
#include <cstring>
#include <cstddef>
#include "../icu_radio/ionic_decode.h"
#include "../icu/radio_link.h"

static int passed = 0, failed = 0;
#define CHECK(c, msg) do { if (c) passed++; else { failed++; printf("  FAIL  %s\n", msg); } } while (0)

static size_t mkline(char *out, const char *body)
{
    uint8_t cs = radio_xor(body, strlen(body));
    return (size_t)sprintf(out, "$%s*%02X", body, cs);
}

int main()
{
    printf("-- battery path verification (F-015) --\n");

    /* ---------- 1. the frames are 8 bytes and where the map says ---------- */
    CHECK(sizeof(icu_batt_t) == 8 && sizeof(icu_cells_t) == 8, "0x220 and 0x221 are 8 bytes");
    CHECK(offsetof(icu_batt_t, flags) == 6 && offsetof(icu_cells_t, spread_mv) == 4, "flags at byte 6, spread at bytes 4-5");

    /* ---------- 2. the advertisement ---------- */
    {
        const uint8_t adv[] = { 0xC8, 0x32, 0x11, 0x22 };          /* 0x32C8 = 13000 mV */
        CHECK(ionic_adv_pack_mv(adv, sizeof adv) == 13000, "pack mV from the advertisement's first two bytes");
        const uint8_t junk[] = { 0x10, 0x00 };                      /* 16 mV: not a pack */
        CHECK(ionic_adv_pack_mv(junk, 2) == 0, "an implausible pack voltage reads as no reading, not 16 mV");
        CHECK(ionic_adv_pack_mv(adv, 1) == 0, "one byte is too short");
    }

    /* ---------- 3. the type-01 cell frame ---------- */
    {
        /* 3.25 V per cell at ~1.43 mV/count = 2273 counts = 0x08E1 (the 2026-09-08 reading) */
        uint8_t f[13] = { 0x7E, 0x01, 0x08, 0xE1, 0x08, 0xE1, 0x08, 0xE2, 0x08, 0xE1, 0x08, 0x00, 0x0D };
        uint8_t sum = 0; for (int i = 1; i <= 10; i++) sum = (uint8_t)(sum + f[i]);
        f[11] = sum;
        ionic_cells_t c;
        CHECK(ionic_decode_type01(f, 13, &c) == 1, "a well-framed type-01 frame decodes");
        CHECK(c.cell_mv[0] == 3250 && c.cell_mv[2] == 3252, "2273 counts -> 3250 mV, 2274 -> 3252 mV");
        CHECK(c.csum_kind == CSUM_SUM8, "an 8-bit sum checksum is recognised");
        uint8_t x = 0; for (int i = 1; i <= 10; i++) x ^= f[i];
        f[11] = x;
        ionic_decode_type01(f, 13, &c);
        CHECK(c.csum_kind == CSUM_XOR8, "an 8-bit XOR checksum is recognised");
        f[11] = (uint8_t)(x + 1 == sum ? x + 2 : x + 1);
        ionic_decode_type01(f, 13, &c);
        CHECK(c.csum_kind == CSUM_NONE, "a checksum matching neither is reported as failed");
        CHECK(ionic_cells_agree(&c, 13000) == 1, "four cells summed agree with a 13.0 V pack");
        CHECK(ionic_cells_agree(&c, 12000) == 0, "and disagree with 12.0 V");
        f[12] = 0x0A;
        CHECK(ionic_decode_type01(f, 13, &c) == 0, "a bad end byte is not a frame");
        f[12] = 0x0D; f[1] = 0x02;
        CHECK(ionic_decode_type01(f, 13, &c) == 0, "another frame type is not decoded");
        CHECK(ionic_decode_type01(f, 12, &c) == 0, "a short frame is not decoded");
    }

    /* ---------- 4. the line protocol ---------- */
    {
        char l[80]; radio_bat_t b;
        size_t n = mkline(l, "BAT,13012,3251,3252,3254,3250,07");
        CHECK(radio_parse_bat(l, n, &b) == 1, "a good $BAT line parses");
        CHECK(b.pack_mv == 13012 && b.cell_mv[3] == 3250 && b.flags == 0x07, "every field lands where it belongs");
        l[6] = '9';
        CHECK(radio_parse_bat(l, n, &b) == 0, "one changed digit fails the checksum and the whole line is dropped");
        n = mkline(l, "BAT,13012,,,,,01");
        CHECK(radio_parse_bat(l, n, &b) == 1 && b.cell_mv[0] == 0 && b.flags == 0x01, "empty cell fields are no reading, flags say so");
        n = mkline(l, "BAT,13012,3251,3252,3254,3250,17");
        CHECK(radio_parse_bat(l, n, &b) == 1 && b.flags == 0x07, "the C3 cannot set RADIO_LOST - only the Teensy decides that");
        n = mkline(l, "BAT,99999,1,2,3,4,00");
        CHECK(radio_parse_bat(l, n, &b) == 0, "a value over 16 bits is refused");
        n = mkline(l, "BAT,1,2,3,4,00");
        CHECK(radio_parse_bat(l, n, &b) == 0, "a missing field is refused");
        n = mkline(l, "XYZ,1,2,3,4,5,00");
        CHECK(radio_parse_bat(l, n, &b) == 0, "only $BAT lines are read");
        CHECK(radio_parse_bat("garbage", 7, &b) == 0, "noise is refused");
        char req[16]; size_t rn = radio_cells_request(req, 1);
        CHECK(rn == 13 && memcmp(req, "$CELLS,1*", 9) == 0 && req[rn - 1] == '\n', "the cells request is framed and terminated");
        uint8_t cs = radio_xor("CELLS,1", 7);
        CHECK(radio_hex(req[9]) * 16 + radio_hex(req[10]) == cs, "and carries its checksum");
    }

    /* ---------- 5. the frames the ICU sends ---------- */
    {
        radio_bat_t b = { 13012, { 3251, 3252, 3259, 3250 }, BATT_ADV_FRESH | BATT_GATT_CONN | BATT_CELLS_FRESH };
        icu_batt_t a; icu_cells_t c;
        radio_build_frames(&b, 400, &a, &c);
        CHECK(a.pack_mv == 13012 && a.cell2_mv == 3252 && c.cell3_mv == 3259, "fresh data goes straight into 0x220 / 0x221");
        CHECK(c.spread_mv == 9, "the spread is highest minus lowest (3259 - 3250)");
        radio_build_frames(&b, 3500, &a, &c);
        CHECK(a.pack_mv == 0 && c.spread_mv == 0 && a.flags == BATT_RADIO_LOST && c.flags == BATT_RADIO_LOST,
              "3 s without a line: every value blank, RADIO_LOST set - never a held reading");
        radio_build_frames(nullptr, 0, &a, &c);
        CHECK(a.flags == BATT_RADIO_LOST && a.pack_mv == 0, "no line ever received is the same as lost");
        b.flags = BATT_ADV_FRESH | BATT_CELLS_FRESH | BATT_CSUM_FAILED;
        radio_build_frames(&b, 100, &a, &c);
        CHECK(a.pack_mv == 13012 && a.cell1_mv == 0 && c.spread_mv == 0 && (a.flags & BATT_CSUM_FAILED),
              "a failed cell checksum blanks the cells but keeps the advertised pack");
        b.flags = BATT_CELLS_FRESH;
        radio_build_frames(&b, 100, &a, &c);
        CHECK(a.pack_mv == 0 && a.cell1_mv == 3251, "a stale advertisement blanks the pack, not the cells");
    }

    printf("\n passed %d   failed %d\n", passed, failed);
    if (failed) { printf(" *** RADIO TESTS FAILED ***\n"); return 1; }
    printf(" ALL RADIO TESTS PASSED\n");
    return 0;
}

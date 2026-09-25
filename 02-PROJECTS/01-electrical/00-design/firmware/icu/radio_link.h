/*
 * radio_link.h — the line protocol from the ESP32-C3 radio to the Teensy, and
 * the two battery frames the ICU builds from it (0x220, 0x221, D-345)
 *
 * Portable C++, no Arduino headers: icu.ino, the C3 sketch and the desk tests
 * (tests/test_radio.cpp) include the same file.
 *
 * THE PROTOCOL (F-015). Serial2 on the Teensy (RX 7, TX 8, D-377), 115200 8N1.
 * One line from the C3 every 500 ms (2 Hz), NMEA-style so it can be read by eye
 * on a terminal during bring-up:
 *
 *     $BAT,<pack_mv>,<c1_mv>,<c2_mv>,<c3_mv>,<c4_mv>,<flags>*<CS>\r\n
 *
 *   - every value is a decimal integer in millivolts; an EMPTY field means
 *     "no reading" and is carried as 0 plus a cleared freshness bit - it is
 *     never invented
 *   - <flags> is two hex digits: BATT_ADV_FRESH, BATT_GATT_CONN,
 *     BATT_CELLS_FRESH, BATT_CSUM_FAILED (can_map.h). The Teensy adds
 *     BATT_RADIO_LOST itself when no good line has arrived for 3 s
 *   - <CS> is two hex digits: the XOR of every byte between '$' and '*'
 *
 * One line from the Teensy to the C3, only when it wants cell detail (D-345:
 * connect to FFE1 only when wanted - e.g. while the battery page is shown):
 *
 *     $CELLS,1*<CS>\r\n     start reading the cell frame
 *     $CELLS,0*<CS>\r\n     stop, and drop the GATT connection
 */
#ifndef RADIO_LINK_H
#define RADIO_LINK_H

#include <stdint.h>
#include <stddef.h>
#include "can_map.h"

#define RADIO_LOST_MS  3000u
#define RADIO_LINE_MAX 64

typedef struct {
    uint16_t pack_mv;
    uint16_t cell_mv[4];
    uint8_t  flags;         /* BATT_* as sent by the C3 */
} radio_bat_t;

static inline uint8_t radio_xor(const char *s, size_t n)
{
    uint8_t x = 0;
    for (size_t i = 0; i < n; i++) x ^= (uint8_t)s[i];
    return x;
}

static inline int radio_hex(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

/* Parse one line (without the \r\n). Returns 1 and fills `out` for a good
 * $BAT line with a correct checksum, 0 for anything else - a bad line is
 * dropped whole, never half-used. */
static inline int radio_parse_bat(const char *line, size_t len, radio_bat_t *out)
{
    if (!line || !out || len < 12 || len > RADIO_LINE_MAX || line[0] != '$') return 0;
    size_t star = 0;
    for (size_t i = 1; i < len; i++) if (line[i] == '*') { star = i; break; }
    if (star == 0 || star + 3 != len) return 0;
    int h1 = radio_hex(line[star + 1]), h2 = radio_hex(line[star + 2]);
    if (h1 < 0 || h2 < 0) return 0;
    if (radio_xor(line + 1, star - 1) != (uint8_t)(h1 * 16 + h2)) return 0;
    if (star < 5 || line[1] != 'B' || line[2] != 'A' || line[3] != 'T' || line[4] != ',') return 0;

    uint32_t v[6] = {0, 0, 0, 0, 0, 0};
    int field = 0, digits = 0;
    for (size_t i = 5; i < star; i++) {
        char c = line[i];
        if (c == ',') {
            if (++field > 5) return 0;
            digits = 0;
            continue;
        }
        if (field < 5) {
            if (c < '0' || c > '9' || ++digits > 5) return 0;
            v[field] = v[field] * 10u + (uint32_t)(c - '0');
            if (v[field] > 65535u) return 0;
        } else {
            int h = radio_hex(c);
            if (h < 0 || ++digits > 2) return 0;
            v[5] = v[5] * 16u + (uint32_t)h;
        }
    }
    if (field != 5) return 0;
    out->pack_mv = (uint16_t)v[0];
    for (int c = 0; c < 4; c++) out->cell_mv[c] = (uint16_t)v[1 + c];
    out->flags = (uint8_t)(v[5] & (BATT_ADV_FRESH | BATT_GATT_CONN | BATT_CELLS_FRESH | BATT_CSUM_FAILED));
    return 1;
}

/* Build the "$CELLS,n*CS" request into buf (>= 12 bytes). Returns its length. */
static inline size_t radio_cells_request(char *buf, int on)
{
    const char *body = on ? "CELLS,1" : "CELLS,0";
    size_t n = 0;
    buf[n++] = '$';
    for (const char *p = body; *p; p++) buf[n++] = *p;
    uint8_t cs = radio_xor(buf + 1, n - 1);
    const char *hx = "0123456789ABCDEF";
    buf[n++] = '*'; buf[n++] = hx[cs >> 4]; buf[n++] = hx[cs & 15];
    buf[n++] = '\r'; buf[n++] = '\n';
    return n;
}

/* The two frames, from the last good line and how old it is. With the link
 * lost every value goes to 0 and every freshness bit is cleared - receivers
 * blank on the flags, they never show a held value (D-153). The spread is only
 * computed when the cells are fresh. Counters are the caller's. */
static inline void radio_build_frames(const radio_bat_t *b, uint32_t age_ms,
                                      icu_batt_t *f220, icu_cells_t *f221)
{
    uint8_t flags = b ? b->flags : 0;
    int lost = (b == NULL) || age_ms > RADIO_LOST_MS;
    if (lost) flags = BATT_RADIO_LOST;
    int cells_ok = !lost && (flags & BATT_CELLS_FRESH) && !(flags & BATT_CSUM_FAILED);

    f220->pack_mv  = (!lost && (flags & BATT_ADV_FRESH)) ? b->pack_mv : 0;
    f220->cell1_mv = cells_ok ? b->cell_mv[0] : 0;
    f220->cell2_mv = cells_ok ? b->cell_mv[1] : 0;
    f220->flags    = flags;
    f221->cell3_mv = cells_ok ? b->cell_mv[2] : 0;
    f221->cell4_mv = cells_ok ? b->cell_mv[3] : 0;
    f221->flags    = flags;
    f221->spread_mv = 0;
    if (cells_ok) {
        uint16_t lo = b->cell_mv[0], hi = b->cell_mv[0];
        for (int c = 1; c < 4; c++) {
            if (b->cell_mv[c] < lo) lo = b->cell_mv[c];
            if (b->cell_mv[c] > hi) hi = b->cell_mv[c];
        }
        f221->spread_mv = (uint16_t)(hi - lo);
    }
}

#endif /* RADIO_LINK_H */

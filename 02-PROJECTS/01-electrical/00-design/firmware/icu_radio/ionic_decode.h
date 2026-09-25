/*
 * ionic_decode.h — decode what the Ionic BMS broadcasts, and nothing more
 *
 * Portable C++, no Arduino headers: the ESP32-C3 sketch (icu_radio.ino) and the
 * desk tests (tests/test_radio.cpp) include the same file.
 *
 * Source of truth: 02-PROJECTS/01-electrical data, icu_channels IC24, D-330, D-345.
 *   - The advertisement's manufacturer data BEGINS with pack millivolts. Read here
 *     as a little-endian uint16 in its first two bytes (the slot a BLE scanner
 *     shows as the "company ID"). confirm at bring-up on the dev board (P116): the
 *     four cells summed must agree with it, which is how the 1.43 mV scale was
 *     confirmed in the first place.
 *   - The type-01 cell frame on GATT FFE1 (service FFE0):
 *       7E 01 08  c1 c1  c2 c2  c3 c3  c4 c4  CS  0D      (13 bytes)
 *     four little-endian uint16 cell counts at ~1.43 mV per count.
 *     The checksum algorithm is NOT documented. Two candidates are accepted -
 *     an 8-bit sum and an 8-bit XOR over type, length and data - and the one that
 *     matched is reported, so bring-up can say which it is (confirm).
 *
 * THIS FILE ONLY READS. The sketch never writes to the BMS, and FFE7 or anything
 * labelled DFU is never touched: that is the firmware-update door on the BMS
 * that runs the car's power (D-330).
 */
#ifndef IONIC_DECODE_H
#define IONIC_DECODE_H

#include <stdint.h>
#include <stddef.h>

/* ~1.43 mV per raw count (D-330), kept as an exact ratio so there is no float */
#define IONIC_MV_NUM   143u
#define IONIC_MV_DEN   100u

enum ionic_csum_t { CSUM_NONE = 0, CSUM_SUM8 = 1, CSUM_XOR8 = 2 };

typedef struct {
    uint16_t cell_mv[4];
    uint8_t  csum_kind;     /* ionic_csum_t that matched, CSUM_NONE if neither */
} ionic_cells_t;

/* Pack millivolts from the advertisement's manufacturer data. Returns 0 if the
 * data is too short or the value is implausible for a 4S LiFePO4 pack
 * (outside 8.0-16.0 V) - 0 means "no reading", never "0 V". */
static inline uint16_t ionic_adv_pack_mv(const uint8_t *mfr, size_t len)
{
    if (!mfr || len < 2) return 0;
    uint16_t mv = (uint16_t)(mfr[0] | ((uint16_t)mfr[1] << 8));
    return (mv >= 8000u && mv <= 16000u) ? mv : 0;
}

/* Decode one type-01 frame. Returns 1 and fills `out` if the framing is right
 * (7E 01 08 ... 0D, 13 bytes); out->csum_kind says whether either checksum
 * candidate matched. Returns 0 for anything else. */
static inline int ionic_decode_type01(const uint8_t *f, size_t len, ionic_cells_t *out)
{
    if (!f || !out || len != 13) return 0;
    if (f[0] != 0x7E || f[1] != 0x01 || f[2] != 0x08 || f[12] != 0x0D) return 0;
    uint8_t sum = 0, x = 0;
    for (int i = 1; i <= 10; i++) { sum = (uint8_t)(sum + f[i]); x ^= f[i]; }
    out->csum_kind = (f[11] == sum) ? CSUM_SUM8 : (f[11] == x) ? CSUM_XOR8 : CSUM_NONE;
    for (int c = 0; c < 4; c++) {
        uint32_t counts = (uint32_t)f[3 + 2 * c] | ((uint32_t)f[4 + 2 * c] << 8);
        out->cell_mv[c] = (uint16_t)((counts * IONIC_MV_NUM + IONIC_MV_DEN / 2) / IONIC_MV_DEN);
    }
    return 1;
}

/* The bring-up cross-check: the four cells summed against the advertised pack,
 * within 3 %. 1 = they agree. */
static inline int ionic_cells_agree(const ionic_cells_t *c, uint16_t pack_mv)
{
    if (!c || pack_mv == 0) return 0;
    uint32_t s = (uint32_t)c->cell_mv[0] + c->cell_mv[1] + c->cell_mv[2] + c->cell_mv[3];
    uint32_t d = (s > pack_mv) ? s - pack_mv : pack_mv - s;
    return d * 100u <= (uint32_t)pack_mv * 3u;
}

#endif /* IONIC_DECODE_H */

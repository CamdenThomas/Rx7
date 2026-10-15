/*
 * log_link.h — the framed binary channel between the ICU's Teensy and its ESP32-C3
 * radio, which carries the log link (D-478, D-493, D-494, work BT3)
 *
 * IMPLEMENTS (R6): the record's table `log_link` - rows LL03-LL14 byte for byte here
 * (the frame types, payloads, error and state codes, the framing, the time rule);
 * LL01-LL02 (advertising, pairing) live in du_radio/du_radio.ino. `log_channels` is
 * log_store.h's. rx7.py sql 01-electrical "select * from log_link order by id".
 * 00-design/tests/gen_log_vectors.py reads the same rows and 00-design/tests/test_loglink.cpp holds every
 * opcode and UUID here to them.
 *
 * Portable C++, no Arduino headers: du.ino, du_radio.ino and 00-design/tests/test_loglink.cpp
 * include the same file. Every multi-byte field is little-endian (both CPUs are).
 *
 * FRAMING (LL11). Serial2 on the Teensy (RX 7, TX 8, D-377) to Serial1 on the C3,
 * 921600 8N1 (D-493):
 *
 *     AA 55 | len u16 | type u8 | payload | crc16 u16
 *
 *   - len counts type + payload, 1..LL_LEN_MAX
 *   - crc16 is CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF, no reflection, no final
 *     xor; "123456789" -> 0x29B1) over type + payload
 *   - the 2 Hz $BAT lines and the $CELLS requests of radio_link.h keep running between
 *     frames on the same wire. A frame never starts with '$', a line never with 0xAA,
 *     so one byte-at-a-time decoder (ll_rx_feed) hands back either. A frame whose CRC
 *     fails is dropped whole; the C3 re-asks (re-OPENs at its last offset).
 *
 * WHO SENDS WHAT
 *   C3 -> Teensy (LL12): LIST 0x01 · OPEN 0x02 · ACK 0x03 · ABORT 0x04 · SET_TIME 0x10 ·
 *                        PING 0x7F · CREDIT 0x20 · PAIRING 0x21
 *   Teensy -> C3 (LL13): ITEM 0x81 · DATA 0x82 · END 0x83 · INFO 0x84 · START 0x85 ·
 *                        PAIR 0x86 · UNBOND 0x87 · ERR 0x8F
 *
 *   Not in the record, added here (BT3, reported):
 *   - ABORT 0x04 is forwarded over the UART: LL12's list leaves it out, but LL08 makes it
 *     a phone opcode and LL12 says "the BLE opcodes forwarded with the same fields"
 *   - START 0x85 (seq, tier, offset, total): the Teensy says a transfer has begun, so the
 *     C3 knows `total` for status (LL10) and drops DATA still in flight from an aborted
 *     transfer (it forwards nothing between an OPEN and its START)
 *   - PAIR 0x86 (window_s): the cluster's long press of the page button opens pairing
 *     on the radio for that long (LL02); 0 closes it
 *   - UNBOND 0x87: the cluster menu's "forget phones" (LL02: never over the link)
 *   - PAIRING 0x21 (state, passkey, seconds left): the radio hands the Teensy the
 *     six-digit key so the cluster can show it, and says how pairing ended
 *   - err 7 LL_E_CRC: an ACK whose CRC does not match the tier - pulled stays clear
 *   - the Teensy answers ACK with ERR 0 (marked pulled) or an error, PING and SET_TIME
 *     with INFO, ABORT with ERR 5, an unknown type with ERR 1
 *
 * CREDIT (LL12): the C3 says how many more payload bytes of ITEM and DATA frames it
 * can buffer (DATA counts its 4-byte offset); grants add up; LIST and OPEN zero the
 * Teensy's credit, and the C3 follows each with a fresh grant. The Teensy never sends
 * an ITEM or DATA past its credit. Control frames (INFO, START, END, ERR) are not counted.
 *
 * NOTHING HERE CAN SWITCH AN OUTPUT, CHANGE A SETTING OF THE CAR OR LOAD CODE (D-478).
 * SET_TIME is the one state write (D-493), and ll_time_should_set is its whole rule.
 */
#ifndef LOG_LINK_H
#define LOG_LINK_H

#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define LL_PROTOCOL        1         /* info.protocol (LL03)                         */
#define LL_BAUD            921600u   /* params radio_uart_baud (D-493)               */
#define LL_SYNC0           0xAA
#define LL_SYNC1           0x55
#define LL_DATA_MAX        240u      /* LL13: DATA carries up to 240 bytes           */
#define LL_LEN_MAX         (1u + 4u + LL_DATA_MAX)      /* type + the largest payload */
#define LL_FRAME_MAX       (2u + 2u + LL_LEN_MAX + 2u)  /* 251 bytes on the wire      */
#define LL_LINE_MAX        64        /* == RADIO_LINE_MAX (radio_link.h); tested      */
#define LL_TIMEOUT_MS      5000u     /* LL14: no CREDIT 5 s aborts; no DATA 5 s err 6 */
#define LL_STATUS_MS       1000u     /* LL10: status once a second during a transfer  */
#define LL_PAIR_WINDOW_S   60u       /* LL02: pairing mode for 60 s                  */
#define LL_TIME_SLACK_S    2u        /* LL08: SET_TIME only if unset or off by > 2 s */

/* the service and its characteristics (LL01, LL03-LL05, LL09, LL10) */
#define LL_UUID_SERVICE    "7a1e0001-5b2c-4d3e-9f10-8a7b6c5d4e3f"
#define LL_UUID_INFO       "7a1e0002-5b2c-4d3e-9f10-8a7b6c5d4e3f"
#define LL_UUID_DRIVES     "7a1e0003-5b2c-4d3e-9f10-8a7b6c5d4e3f"
#define LL_UUID_CONTROL    "7a1e0004-5b2c-4d3e-9f10-8a7b6c5d4e3f"
#define LL_UUID_DATA       "7a1e0005-5b2c-4d3e-9f10-8a7b6c5d4e3f"
#define LL_UUID_STATUS     "7a1e0006-5b2c-4d3e-9f10-8a7b6c5d4e3f"
#define LL_DEVICE_NAME     "RX7-ICU"

/* ---------------- frame types / opcodes ---------------- */
/* phone -> ICU on control (LL06-LL08), forwarded C3 -> Teensy with the same fields (LL12) */
#define LL_LIST            0x01
#define LL_OPEN            0x02
#define LL_ACK             0x03
#define LL_ABORT           0x04
#define LL_SET_TIME        0x10
#define LL_PING            0x7F
/* C3 -> Teensy only - never accepted from the phone */
#define LL_CREDIT          0x20
#define LL_PAIRING         0x21      /* added (BT3) */
/* Teensy -> C3 (LL13) */
#define LL_ITEM            0x81
#define LL_DATA            0x82
#define LL_END             0x83
#define LL_INFO            0x84
#define LL_START           0x85      /* added (BT3) */
#define LL_PAIR            0x86      /* added (BT3) */
#define LL_UNBOND          0x87      /* added (BT3) */
#define LL_ERR             0x8F

/* tiers (LL07) */
#define LL_TIER_SUMMARY    0
#define LL_TIER_THIN       1
#define LL_TIER_FULL       2
#define LL_TIERS           3

/* status.state (LL10) */
#define LL_S_IDLE          0
#define LL_S_LISTING       1
#define LL_S_SENDING       2
#define LL_S_DONE          3
#define LL_S_ERROR         4

/* status.err / ERR.err (LL10) */
#define LL_E_NONE          0
#define LL_E_OPCODE        1
#define LL_E_NO_DRIVE      2
#define LL_E_NO_CARD       3
#define LL_E_BUSY          4
#define LL_E_ABORTED       5
#define LL_E_SILENT        6
#define LL_E_CRC           7         /* added (BT3): ACK's CRC does not match the tier */

/* PAIRING.state (added, BT3) */
#define LL_PAIR_CLOSED     0
#define LL_PAIR_OPEN       1         /* waiting for a phone; passkey valid             */
#define LL_PAIR_BONDED     2
#define LL_PAIR_FAILED     3

/* ---------------- payloads ---------------- */

typedef struct __attribute__((packed)) { uint32_t from_seq; } ll_list_t;                     /* LL06 */
typedef struct __attribute__((packed)) { uint32_t seq; uint8_t tier; uint32_t offset; } ll_open_t;  /* LL07 */
typedef struct __attribute__((packed)) { uint32_t seq; uint8_t tier; uint32_t crc32; } ll_ack_t;    /* LL08 */
typedef struct __attribute__((packed)) { uint32_t unix_time; } ll_set_time_t;                /* LL08 */
typedef struct __attribute__((packed)) { uint16_t bytes; } ll_credit_t;                      /* LL12 */
typedef struct __attribute__((packed)) { uint8_t state; uint32_t passkey; uint8_t secs_left; } ll_pairing_t;

/* LL04 drives entry; seq 0 ends a list. pulled: b0 summary, b1 thin, b2 full */
typedef struct __attribute__((packed)) {
    uint32_t seq;
    uint32_t start_odo;     /* 0.1 mi                                   */
    uint32_t duration_s;
    uint32_t start_unix;    /* 0 = the RTC was unset at the start       */
    uint8_t  pulled;
    uint16_t summary_len;
    uint32_t thin_len;
    uint32_t full_len;
} ll_item_t;

typedef struct __attribute__((packed)) { uint32_t offset; } ll_data_hdr_t;   /* LL09 / LL13, then the bytes */
typedef struct __attribute__((packed)) { uint32_t crc32; } ll_end_t;         /* LL13 */
typedef struct __attribute__((packed)) { uint32_t seq; uint8_t tier; uint32_t offset; uint32_t total; } ll_start_t;
typedef struct __attribute__((packed)) { uint8_t window_s; } ll_pair_t;
typedef struct __attribute__((packed)) { uint8_t err; } ll_err_t;

/* LL03 info */
typedef struct __attribute__((packed)) {
    uint8_t  protocol;      /* LL_PROTOCOL                              */
    uint16_t fw;            /* ICU firmware, major*10000 + minor*100 + patch */
    uint32_t odometer;      /* 0.1 mi (F-007)                           */
    uint32_t drive_count;
    uint16_t not_pulled;    /* drives whose summary or thin is not pulled */
    uint8_t  card_free;     /* %                                        */
    uint8_t  rtc_set;
    uint32_t unix_time;
    uint32_t uptime_ms;
} ll_info_t;

/* LL10 status, built by the C3 */
typedef struct __attribute__((packed)) {
    uint8_t  state;
    uint32_t seq;
    uint8_t  tier;
    uint32_t sent;
    uint32_t total;
    uint32_t crc32;         /* valid when done */
    uint8_t  err;
} ll_status_t;

static_assert(sizeof(ll_list_t) == 4 && sizeof(ll_open_t) == 9 && sizeof(ll_ack_t) == 9, "LL06-LL08 sizes");
static_assert(sizeof(ll_set_time_t) == 4 && sizeof(ll_credit_t) == 2, "LL08 / LL12 sizes");
static_assert(sizeof(ll_item_t) == 27 && sizeof(ll_info_t) == 23 && sizeof(ll_status_t) == 19, "LL04 / LL03 / LL10 sizes");
static_assert(sizeof(ll_end_t) == 4 && sizeof(ll_start_t) == 13 && sizeof(ll_pairing_t) == 6, "LL13 and added sizes");

/* ---------------- checksums ---------------- */

/* CRC-16/CCITT-FALSE over type + payload (LL11) */
static inline uint16_t ll_crc16(uint16_t crc, const uint8_t *p, size_t n)
{
    while (n--) {
        crc ^= (uint16_t)(*p++) << 8;
        for (int b = 0; b < 8; b++) crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u) : (uint16_t)(crc << 1);
    }
    return crc;
}

/* CRC-32 (IEEE 802.3 / zlib: reflected 0xEDB88320, init and final xor 0xFFFFFFFF;
 * "123456789" -> 0xCBF43926) over a whole tier file (LL08, LL13). Nibble table: 64 bytes
 * of flash, two steps a byte - an 11 MB full log in well under a second on the Teensy. */
static inline uint32_t ll_crc32_update(uint32_t crc, const void *data, size_t n)
{
    static const uint32_t T[16] = {
        0x00000000u, 0x1DB71064u, 0x3B6E20C8u, 0x26D930ACu, 0x76DC4190u, 0x6B6B51F4u, 0x4DB26158u, 0x5005713Cu,
        0xEDB88320u, 0xF00F9344u, 0xD6D6A3E8u, 0xCB61B38Cu, 0x9B64C2B0u, 0x86D3D2D4u, 0xA00AE278u, 0xBDBDF21Cu };
    const uint8_t *p = (const uint8_t *)data;
    while (n--) {
        crc ^= *p++;
        crc = (crc >> 4) ^ T[crc & 15];
        crc = (crc >> 4) ^ T[crc & 15];
    }
    return crc;
}
#define LL_CRC32_INIT  0xFFFFFFFFu
static inline uint32_t ll_crc32_final(uint32_t crc) { return crc ^ 0xFFFFFFFFu; }
static inline uint32_t ll_crc32(const void *data, size_t n) { return ll_crc32_final(ll_crc32_update(LL_CRC32_INIT, data, n)); }

/* ---------------- encoder ---------------- */

/* One frame into out. Returns its length, or 0 if it does not fit or is too long. */
static inline size_t ll_encode(uint8_t *out, size_t cap, uint8_t type, const void *payload, size_t n)
{
    size_t len = 1 + n;
    if (len > LL_LEN_MAX || cap < len + 6) return 0;
    out[0] = LL_SYNC0; out[1] = LL_SYNC1;
    out[2] = (uint8_t)(len & 0xFF); out[3] = (uint8_t)(len >> 8);
    out[4] = type;
    if (n) memcpy(out + 5, payload, n);
    uint16_t c = ll_crc16(0xFFFF, out + 4, len);
    out[4 + len] = (uint8_t)(c & 0xFF); out[5 + len] = (uint8_t)(c >> 8);
    return len + 6;
}

/* DATA: the offset, then the bytes (LL13) */
static inline size_t ll_encode_data(uint8_t *out, size_t cap, uint32_t offset, const uint8_t *bytes, size_t n)
{
    uint8_t p[4 + LL_DATA_MAX];
    if (n > LL_DATA_MAX) return 0;
    memcpy(p, &offset, 4);
    if (n) memcpy(p + 4, bytes, n);
    return ll_encode(out, cap, LL_DATA, p, 4 + n);
}

/* ---------------- decoder: frames and lines from one wire ---------------- */

enum { LL_RX_NONE = 0, LL_RX_FRAME, LL_RX_LINE };

typedef struct {
    uint8_t  st;                    /* 0 hunt, 1 sync1, 2 len lo, 3 len hi, 4 body, 5 crc lo, 6 crc hi, 7 line */
    uint16_t len, n, crc;
    uint8_t  body[LL_LEN_MAX];      /* type, then payload                         */
    char     line[LL_LINE_MAX + 1]; /* a $ line, without its \r\n, NUL-terminated */
    uint16_t line_n;
    uint32_t frames, bad_crc, bad_len, lines, dropped;   /* counters, for the diag page */
} ll_rx_t;

static inline void ll_rx_init(ll_rx_t *r) { memset(r, 0, sizeof *r); }
static inline uint8_t        ll_rx_type(const ll_rx_t *r)    { return r->body[0]; }
static inline const uint8_t *ll_rx_payload(const ll_rx_t *r) { return r->body + 1; }
static inline uint16_t       ll_rx_plen(const ll_rx_t *r)    { return (uint16_t)(r->len - 1); }

static inline void ll_rx_begin_line(ll_rx_t *r)
{
    r->st = 7; r->line[0] = '$'; r->line_n = 1;
}

/* Feed one byte. Returns LL_RX_FRAME when a whole frame with a good CRC is in r
 * (ll_rx_type / ll_rx_payload / ll_rx_plen), LL_RX_LINE when a $ line is in r->line,
 * LL_RX_NONE otherwise. Anything else - noise, a bad CRC, a length out of range, a
 * line too long - is dropped and the hunt starts again. */
static inline int ll_rx_feed(ll_rx_t *r, uint8_t b)
{
    switch (r->st) {
    case 0:
        if (b == LL_SYNC0) r->st = 1;
        else if (b == '$') ll_rx_begin_line(r);
        else r->dropped++;
        return LL_RX_NONE;
    case 1:
        if (b == LL_SYNC1) r->st = 2;
        else if (b == LL_SYNC0) r->st = 1;
        else if (b == '$') ll_rx_begin_line(r);
        else { r->st = 0; r->dropped++; }
        return LL_RX_NONE;
    case 2: r->len = b; r->st = 3; return LL_RX_NONE;
    case 3:
        r->len |= (uint16_t)b << 8;
        if (r->len == 0 || r->len > LL_LEN_MAX) { r->bad_len++; r->st = 0; }
        else { r->n = 0; r->st = 4; }
        return LL_RX_NONE;
    case 4:
        r->body[r->n++] = b;
        if (r->n == r->len) r->st = 5;
        return LL_RX_NONE;
    case 5: r->crc = b; r->st = 6; return LL_RX_NONE;
    case 6:
        r->crc |= (uint16_t)b << 8;
        r->st = 0;
        if (r->crc != ll_crc16(0xFFFF, r->body, r->len)) { r->bad_crc++; return LL_RX_NONE; }
        r->frames++;
        return LL_RX_FRAME;
    default: /* 7: a line */
        if (b == '\r' || b == '\n') {
            r->st = 0;
            r->line[r->line_n] = 0;
            r->lines++;
            return LL_RX_LINE;
        }
        if (b == LL_SYNC0) { r->st = 1; r->dropped++; return LL_RX_NONE; }   /* a line cut short: a frame starts */
        if (r->line_n >= LL_LINE_MAX) { r->st = 0; r->dropped++; return LL_RX_NONE; }
        r->line[r->line_n++] = (char)b;
        return LL_RX_NONE;
    }
}

/* ---------------- the phone's control write (LL05) ---------------- */

/* The payload length each phone opcode carries, or -1: the six opcodes and nothing
 * else (LL05: "anything else is rejected with ERR 0x01"). CREDIT, PAIRING and every
 * Teensy -> C3 type are -1 here - the phone cannot send them. */
static inline int ll_control_plen(uint8_t op)
{
    switch (op) {
    case LL_LIST:     return (int)sizeof(ll_list_t);
    case LL_OPEN:     return (int)sizeof(ll_open_t);
    case LL_ACK:      return (int)sizeof(ll_ack_t);
    case LL_ABORT:    return 0;
    case LL_SET_TIME: return (int)sizeof(ll_set_time_t);
    case LL_PING:     return 0;
    default:          return -1;
    }
}

/* A control write as the phone sent it: opcode then fields. Returns the opcode if it
 * is one of the six with exactly its fields, -1 otherwise (answer ERR LL_E_OPCODE). */
static inline int ll_control_check(const uint8_t *v, size_t n)
{
    if (!v || n == 0) return -1;
    int want = ll_control_plen(v[0]);
    if (want < 0 || (size_t)want != n - 1) return -1;
    if (v[0] == LL_OPEN || v[0] == LL_ACK) {
        uint8_t tier = v[5];
        if (tier >= LL_TIERS) return -1;
    }
    return v[0];
}

/* ---------------- the one state write (LL08, D-493) ---------------- */

/* Apply a SET_TIME? Only if the RTC is unset (now_unix == 0) or differs by more than
 * LL_TIME_SLACK_S seconds. A zero time is never applied. */
static inline int ll_time_should_set(uint32_t now_unix, int rtc_set, uint32_t new_unix)
{
    if (new_unix == 0) return 0;
    if (!rtc_set || now_unix == 0) return 1;
    uint32_t d = now_unix > new_unix ? now_unix - new_unix : new_unix - now_unix;
    return d > LL_TIME_SLACK_S;
}

#endif /* LOG_LINK_H */

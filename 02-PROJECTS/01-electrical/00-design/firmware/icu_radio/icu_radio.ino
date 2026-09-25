/*
 * icu_radio.ino — the ICU's radio co-processor (ESP32-C3, Seeed XIAO class, P116)
 *
 * ONE JOB: read the Ionic BMS over BLE and send the Teensy one line every
 * 500 ms (radio_link.h). Nothing else runs here (D-267, D-330, D-345).
 *
 *   - a PASSIVE scan, always: pack millivolts from the advertisement - no
 *     connection, no pairing, nothing that can hang, and a phone can still
 *     connect to the BMS at the same time
 *   - a GATT client on FFE1 (service FFE0), ONLY while the Teensy asks for cell
 *     detail ($CELLS,1): subscribe and decode the type-01 cell frame
 *
 * NEVER A WRITE. FFE7 and anything labelled DFU are never touched by any code
 * path: that is the firmware-update door on the BMS that runs the car's power,
 * and the downside is a bricked pack in the cargo bin. There is no write call
 * anywhere in this file, and there must never be one.
 *
 * STATUS: written 2026-09-22 for F-015; NOT COMPILED - there is no ESP32 toolchain
 * on the project machine yet. Bring-up is on the spare XIAO dev board (P116) on
 * the desk, never first on the car's pack. The two assumptions to confirm there
 * are in ionic_decode.h: where the pack millivolts sit in the advertisement, and
 * which checksum the cell frame uses.
 *
 * Library: NimBLE-Arduino (h2zero), ESP32 Arduino core. Board: XIAO_ESP32C3.
 * The BMS is found by its advertised name, set in BMS_NAME below - read it off
 * the pack with a phone scanner at bring-up (confirm).
 */
#include <NimBLEDevice.h>
#include "ionic_decode.h"
#include "../icu/radio_link.h"

static const char *BMS_NAME   = "IONIC";      /* confirm at bring-up          */
static const uint32_t LINE_MS = 500;           /* 2 Hz to the Teensy (D-345)   */
static const uint32_t ADV_FRESH_MS = 10000;    /* advertisement fresh < 10 s   */
static const uint32_t CELL_FRESH_MS = 10000;

static NimBLEUUID SVC_FFE0("FFE0");
static NimBLEUUID CHR_FFE1("FFE1");

static volatile uint16_t g_pack_mv = 0;
static volatile uint32_t g_adv_ms = 0;
static ionic_cells_t     g_cells = {};
static volatile uint32_t g_cells_ms = 0;
static volatile bool     g_csum_bad = false;
static bool              g_want_cells = false;
static NimBLEAddress     g_bms_addr;
static bool              g_have_addr = false;
static NimBLEClient     *g_client = nullptr;

/* ---- the scan: read-only, passive ---- */
class ScanCb : public NimBLEScanCallbacks {
    void onResult(const NimBLEAdvertisedDevice *d) override {
        if (!d->haveName() || d->getName().find(BMS_NAME) == std::string::npos) return;
        g_bms_addr = d->getAddress();
        g_have_addr = true;
        if (d->haveManufacturerData()) {
            std::string m = d->getManufacturerData();
            uint16_t mv = ionic_adv_pack_mv((const uint8_t *)m.data(), m.size());
            if (mv) { g_pack_mv = mv; g_adv_ms = millis(); }
        }
    }
};

/* ---- the cell frame: a notification on FFE1, read-only ---- */
static void onNotify(NimBLERemoteCharacteristic *, uint8_t *data, size_t len, bool) {
    ionic_cells_t c;
    if (ionic_decode_type01(data, len, &c)) {
        g_csum_bad = (c.csum_kind == CSUM_NONE);
        g_cells = c;
        g_cells_ms = millis();
    }
}

static void cells_connect() {
    if (!g_have_addr || (g_client && g_client->isConnected())) return;
    if (!g_client) g_client = NimBLEDevice::createClient();
    if (!g_client->connect(g_bms_addr)) return;
    NimBLERemoteService *s = g_client->getService(SVC_FFE0);
    NimBLERemoteCharacteristic *c = s ? s->getCharacteristic(CHR_FFE1) : nullptr;
    /* subscribe only - never writeValue() on any characteristic */
    if (!c || !c->canNotify() || !c->subscribe(true, onNotify)) g_client->disconnect();
}

static void cells_disconnect() {
    if (g_client && g_client->isConnected()) g_client->disconnect();
}

/* ---- the Teensy side ---- */
static void read_requests() {
    static char buf[RADIO_LINE_MAX + 1];
    static size_t n = 0;
    while (Serial1.available()) {
        char ch = (char)Serial1.read();
        if (ch == '\n' || ch == '\r') {
            if (n >= 11 && buf[0] == '$') {
                buf[n] = 0;
                /* "$CELLS,1*CS" / "$CELLS,0*CS" - checksum as radio_link.h */
                size_t star = 0;
                for (size_t i = 1; i < n; i++) if (buf[i] == '*') { star = i; break; }
                if (star && star + 3 == n) {
                    int h1 = radio_hex(buf[star + 1]), h2 = radio_hex(buf[star + 2]);
                    if (h1 >= 0 && h2 >= 0 && radio_xor(buf + 1, star - 1) == (uint8_t)(h1 * 16 + h2)) {
                        if (star == 8 && memcmp(buf + 1, "CELLS,", 6) == 0)
                            g_want_cells = (buf[7] == '1');
                    }
                }
            }
            n = 0;
        } else if (n < RADIO_LINE_MAX) {
            buf[n++] = ch;
        } else {
            n = 0;
        }
    }
}

static void send_line() {
    uint32_t now = millis();
    uint8_t flags = 0;
    bool adv = g_adv_ms && (now - g_adv_ms) < ADV_FRESH_MS;
    bool cells = g_cells_ms && (now - g_cells_ms) < CELL_FRESH_MS;
    if (adv) flags |= BATT_ADV_FRESH;
    if (g_client && g_client->isConnected()) flags |= BATT_GATT_CONN;
    if (cells) flags |= BATT_CELLS_FRESH;
    if (cells && g_csum_bad) flags |= BATT_CSUM_FAILED;

    char body[RADIO_LINE_MAX];
    char f[5][8];
    /* an empty field is "no reading" - never a made-up 0 */
    if (adv) snprintf(f[0], 8, "%u", (unsigned)g_pack_mv); else f[0][0] = 0;
    for (int c = 0; c < 4; c++) {
        if (cells) snprintf(f[1 + c], 8, "%u", (unsigned)g_cells.cell_mv[c]); else f[1 + c][0] = 0;
    }
    int n = snprintf(body, sizeof body, "BAT,%s,%s,%s,%s,%s,%02X", f[0], f[1], f[2], f[3], f[4], flags);
    uint8_t cs = radio_xor(body, (size_t)n);
    Serial1.printf("$%s*%02X\r\n", body, cs);
}

void setup() {
    Serial1.begin(115200);                     /* to the Teensy's Serial2 */
    NimBLEDevice::init("");
    NimBLEScan *scan = NimBLEDevice::getScan();
    scan->setScanCallbacks(new ScanCb(), true);
    scan->setActiveScan(false);                /* passive: we only listen   */
    scan->setInterval(160);
    scan->setWindow(80);
    scan->start(0, false, true);               /* forever, keep results off */
}

void loop() {
    static uint32_t last = 0;
    read_requests();
    if (g_want_cells) cells_connect(); else cells_disconnect();
    if (millis() - last >= LINE_MS) { last = millis(); send_line(); }
    delay(5);
}

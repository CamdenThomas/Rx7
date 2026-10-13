/*
 * icu_radio.ino — the ICU's radio co-processor (ESP32-C3, Seeed XIAO class, P116)
 *
 * TWO JOBS (D-267, D-330, D-345; D-478, D-494):
 *
 * 1. THE BATTERY. Read the Ionic BMS over BLE and send the Teensy one line every
 *    500 ms (radio_link.h).
 *   - a PASSIVE scan, always: pack millivolts from the advertisement - no
 *     connection, no pairing, nothing that can hang, and a phone can still
 *     connect to the BMS at the same time
 *   - a GATT client on FFE1 (service FFE0), ONLY while the Teensy asks for cell
 *     detail ($CELLS,1): subscribe and decode the type-01 cell frame. Dropped for
 *     the length of a log transfer (LL14); the scan goes on
 *
 *   NEVER A WRITE TO THE BMS. FFE7 and anything labelled DFU are never touched by
 *   any code path: that is the firmware-update door on the BMS that runs the car's
 *   power, and the downside is a bricked pack in the cargo bin. There is no write
 *   call on any remote characteristic in this file, and there must never be one.
 *
 * 2. THE LOG LINK (log_link LL01-LL14, implemented with ../icu/log_link.h - R6). A
 *    NimBLE peripheral, "RX7-ICU", one service, five characteristics:
 *   - info (read), drives (notify), control (write), data (notify), status (notify);
 *     every one needs an encrypted, authenticated, bonded link (LL02)
 *   - pairing only while the cluster has opened it (PAIR from the Teensy, 60 s):
 *     LE Secure Connections, passkey shown on the cluster (PAIRING to the Teensy),
 *     typed on the phone; the bond kept on both sides. Outside that window an
 *     unknown phone is refused, and with the whitelist filter on it cannot connect
 *   - the phone's control write is checked (ll_control_check) and forwarded to the
 *     Teensy as a frame; the Teensy's ITEM / DATA come back through a queue and go
 *     out as notifications, paced by CREDIT so neither side ever overruns
 *   NOTHING ARRIVING OVER BLUETOOTH REACHES AN OUTPUT, A SETTING OF THE CAR OR THE
 *   FLASH (D-478): the control write has one switch, six opcodes, and its default is
 *   ERR 1. SET_TIME is forwarded; the Teensy alone decides whether to apply it.
 *
 * STATUS: written 2026-09-22 for F-015, the log link added 2026-10-12 for BT3. It
 * compiles for the XIAO ESP32C3 (00-design/firmware/tests/run.sh); it has never run. Bring-up is on the
 * spare XIAO dev board (P116) on the desk, never first on the car's pack. BT4 proves
 * the scan, the BMS client and the peripheral together, the rate, and the whitelist
 * with a phone's private address. The two battery assumptions to confirm are in
 * ionic_decode.h: where the pack millivolts sit in the advertisement, and which
 * checksum the cell frame uses.
 *
 * Library: NimBLE-Arduino 2.x (h2zero), ESP32 Arduino core 3.x. Board: XIAO_ESP32C3.
 * The BMS is found by its advertised name, set in BMS_NAME below - read it off
 * the pack with a phone scanner at bring-up (confirm).
 */
#include <NimBLEDevice.h>
#include "ionic_decode.h"
#include "../icu/radio_link.h"
#include "../icu/log_link.h"

/* a control write, copied out of NimBLE's task for loop() (here, above every function,
 * so the Arduino builder's prototypes can name it) */
struct Req { uint8_t n; uint8_t v[16]; };

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

/* ---- the Teensy side: $BAT out, $CELLS in (radio_link.h) ---- */
static void on_line(const char *buf, size_t n) {
    /* "$CELLS,1*CS" / "$CELLS,0*CS" - checksum as radio_link.h */
    if (n < 11 || buf[0] != '$') return;
    size_t star = 0;
    for (size_t i = 1; i < n; i++) if (buf[i] == '*') { star = i; break; }
    if (!star || star + 3 != n) return;
    int h1 = radio_hex(buf[star + 1]), h2 = radio_hex(buf[star + 2]);
    if (h1 < 0 || h2 < 0 || radio_xor(buf + 1, star - 1) != (uint8_t)(h1 * 16 + h2)) return;
    if (star == 8 && memcmp(buf + 1, "CELLS,", 6) == 0) g_want_cells = (buf[7] == '1');
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

/* =====================================================================
 * THE LOG LINK
 * ===================================================================== */

/* BT4: a phone with a private (resolvable) address must reconnect through the
 * whitelist. If it cannot, set this false - the AUTHEN permissions and the bonded
 * check in on_auth still keep every unbonded phone out, only less early. */
static const bool     WHITELIST_FILTER = true;
static const uint16_t CREDIT_WINDOW = 8192;    /* payload bytes of ITEM / DATA in flight */
static const uint16_t CREDIT_STEP   = 1024;    /* hand back credit in steps this big     */
static const size_t   Q_BYTES = 16384;         /* the window plus 3 bytes an entry, and control frames */
static const uint32_t PING_MS = 1000;

static NimBLEServer         *g_srv = nullptr;
static NimBLECharacteristic *c_info, *c_drives, *c_control, *c_data, *c_status;

/* set in NimBLE's task, acted on in loop() */
static volatile bool     ev_connect = false, ev_disconnect = false, ev_auth = false;
static volatile uint16_t ev_conn_handle = BLE_HS_CONN_HANDLE_NONE, ev_disc_handle = BLE_HS_CONN_HANDLE_NONE;
static volatile bool     ev_auth_ok = false;
static NimBLEAddress     ev_auth_addr;
static volatile uint16_t g_mtu = 23;
static QueueHandle_t     g_req_q;               /* control writes, in order (Req, at the top) */

static uint16_t g_conn = BLE_HS_CONN_HANDLE_NONE;   /* the one phone (LL14) */
static uint32_t g_conn_ms = 0;
static bool     g_secure = false;                   /* encrypted, authenticated, bonded */
static bool     g_pairing = false;
static uint32_t g_pair_until = 0, g_passkey = 0;

enum { M_IDLE, M_LIST, M_SEND, M_ACK };
static uint8_t     g_mode = M_IDLE;
static bool        g_await_start = false;           /* after OPEN: drop DATA until START */
static ll_status_t g_st = {}, g_st_sent = {};
static bool        g_st_force = false;   /* notify status once even if unchanged: a taken ACK (LL18) */
static uint32_t    g_st_ms = 0;
static ll_info_t   g_info = {};
static uint32_t    g_teensy_ms = 0;                 /* the last frame from the Teensy */
static uint32_t    g_data_ms = 0;                   /* the last ITEM / START / DATA / END / ERR */
static int32_t     g_outstanding = 0;               /* credit granted, not yet used by the Teensy */
static uint32_t    g_regrant = 0;
static uint16_t    g_split = 0;                     /* bytes of the head DATA already notified */
static ll_rx_t     g_rx;

/* ---- the queue: Teensy frames on their way to the phone, in order ---- */
static uint8_t q_buf[Q_BYTES];
static size_t  q_head = 0, q_used = 0;

static void q_clear() { q_head = 0; q_used = 0; g_split = 0; }
static bool q_push(uint8_t type, const uint8_t *p, uint16_t n) {
    if (q_used + 3 + n > Q_BYTES) return false;
    size_t at = (q_head + q_used) % Q_BYTES;
    uint8_t h[3] = { type, (uint8_t)(n & 0xFF), (uint8_t)(n >> 8) };
    for (int i = 0; i < 3; i++) { q_buf[at] = h[i]; at = (at + 1) % Q_BYTES; }
    for (uint16_t i = 0; i < n; i++) { q_buf[at] = p[i]; at = (at + 1) % Q_BYTES; }
    q_used += 3 + n;
    return true;
}
static bool q_peek(uint8_t *type, uint8_t *p, uint16_t *n) {
    if (q_used < 3) return false;
    size_t at = q_head;
    *type = q_buf[at]; at = (at + 1) % Q_BYTES;
    uint16_t len = q_buf[at]; at = (at + 1) % Q_BYTES;
    len |= (uint16_t)q_buf[at] << 8; at = (at + 1) % Q_BYTES;
    for (uint16_t i = 0; i < len; i++) { p[i] = q_buf[at]; at = (at + 1) % Q_BYTES; }
    *n = len;
    return true;
}
static void q_pop(uint16_t n) { q_head = (q_head + 3 + n) % Q_BYTES; q_used -= 3 + n; g_split = 0; }

/* ---- frames to the Teensy ---- */
static void to_teensy(uint8_t type, const void *p, size_t n) {
    uint8_t f[LL_FRAME_MAX];
    size_t fn = ll_encode(f, sizeof f, type, p, n);
    if (fn) Serial1.write(f, fn);
}
static void grant(uint16_t bytes) {
    ll_credit_t c = { bytes };
    to_teensy(LL_CREDIT, &c, sizeof c);
    g_outstanding += bytes;
}
static void pairing_to_teensy(uint8_t state) {
    uint32_t left = g_pairing && g_pair_until > millis() ? (g_pair_until - millis() + 999) / 1000 : 0;
    ll_pairing_t p = { state, state == LL_PAIR_OPEN ? g_passkey : 0, (uint8_t)left };
    to_teensy(LL_PAIRING, &p, sizeof p);
}

static void set_status(uint8_t state, uint8_t err) { g_st.state = state; g_st.err = err; }

/* ---- advertising: 1 s, connectable, whitelist-only outside pairing (LL01) ---- */
static void advertise() {
    NimBLEAdvertising *adv = NimBLEDevice::getAdvertising();
    adv->stop();
    adv->setScanFilter(false, WHITELIST_FILTER && !g_pairing);
    if (g_conn == BLE_HS_CONN_HANDLE_NONE) adv->start();
}

static bool known_phone(const NimBLEAddress &a) {
    for (size_t i = 0; i < NimBLEDevice::getWhiteListCount(); i++)
        if (NimBLEDevice::getWhiteListAddress(i) == a) return true;
    return false;
}

static void pair_open(uint8_t window_s) {
    if (window_s == 0) { g_pairing = false; pairing_to_teensy(LL_PAIR_CLOSED); advertise(); return; }
    g_pairing = true;
    g_pair_until = millis() + (uint32_t)window_s * 1000u;
    g_passkey = esp_random() % 1000000u;
    NimBLEDevice::setSecurityPasskey(g_passkey);
    pairing_to_teensy(LL_PAIR_OPEN);
    advertise();
}

static void forget_phones() {                    /* the cluster menu (LL02), never the link */
    NimBLEDevice::deleteAllBonds();
    while (NimBLEDevice::getWhiteListCount()) NimBLEDevice::whiteListRemove(NimBLEDevice::getWhiteListAddress(0));
    if (g_conn != BLE_HS_CONN_HANDLE_NONE) g_srv->disconnect(g_conn);
    advertise();
}

class SrvCb : public NimBLEServerCallbacks {
    void onConnect(NimBLEServer *, NimBLEConnInfo &ci) override { ev_conn_handle = ci.getConnHandle(); ev_connect = true; }
    void onDisconnect(NimBLEServer *, NimBLEConnInfo &ci, int) override { ev_disc_handle = ci.getConnHandle(); ev_disconnect = true; }
    void onMTUChange(uint16_t mtu, NimBLEConnInfo &) override { g_mtu = mtu; }
    uint32_t onPassKeyDisplay() override { return g_passkey; }
    void onAuthenticationComplete(NimBLEConnInfo &ci) override {
        ev_auth_ok = ci.isEncrypted() && ci.isAuthenticated() && ci.isBonded();
        ev_auth_addr = ci.getIdAddress();
        ev_auth = true;
    }
};

class ControlCb : public NimBLECharacteristicCallbacks {
    void onWrite(NimBLECharacteristic *c, NimBLEConnInfo &ci) override {
        if (!ci.isEncrypted() || !ci.isAuthenticated()) return;     /* the permissions already refuse it */
        NimBLEAttValue v = c->getValue();
        Req r;
        r.n = (uint8_t)(v.size() > sizeof r.v ? sizeof r.v + 1 : v.size());   /* too long: rejected below */
        memcpy(r.v, v.data(), r.n > sizeof r.v ? sizeof r.v : r.n);
        xQueueSend(g_req_q, &r, 0);
    }
};

/* The phone's request (LL05-LL08): ONE switch, six opcodes, default = ERR 1.
 * Each is forwarded to the Teensy with the same fields (LL12). */
static void on_control(const Req &r) {
    int op = r.n <= sizeof r.v ? ll_control_check(r.v, r.n) : -1;
    const uint8_t *f = r.v + 1;
    uint8_t n = (uint8_t)(r.n - 1);
    switch (op) {
    case LL_LIST:
        q_clear(); g_mode = M_LIST; g_outstanding = 0; g_regrant = 0; g_data_ms = millis();
        set_status(LL_S_LISTING, LL_E_NONE);
        to_teensy(LL_LIST, f, n);
        grant(CREDIT_WINDOW);
        break;
    case LL_OPEN: {
        ll_open_t o; memcpy(&o, f, sizeof o);
        q_clear(); g_mode = M_SEND; g_await_start = true; g_outstanding = 0; g_regrant = 0; g_data_ms = millis();
        g_st.seq = o.seq; g_st.tier = o.tier; g_st.sent = o.offset; g_st.total = 0; g_st.crc32 = 0;
        set_status(LL_S_SENDING, LL_E_NONE);
        cells_disconnect();                        /* the cell connection waits (LL14) */
        to_teensy(LL_OPEN, f, n);
        grant(CREDIT_WINDOW);
        break; }
    case LL_ACK: {
        ll_ack_t a; memcpy(&a, f, sizeof a);
        g_mode = M_ACK; g_st.seq = a.seq; g_st.tier = a.tier;
        to_teensy(LL_ACK, f, n);
        break; }
    case LL_ABORT:
        q_clear(); g_mode = M_IDLE;
        to_teensy(LL_ABORT, nullptr, 0);
        break;
    case LL_SET_TIME:
        to_teensy(LL_SET_TIME, f, n);              /* the Teensy applies LL08's rule */
        break;
    case LL_PING:
        to_teensy(LL_PING, nullptr, 0);
        break;
    default:
        set_status(LL_S_ERROR, LL_E_OPCODE);
        break;
    }
}

/* A frame from the Teensy. Nothing here writes anything but the queue, the status and
 * the info value. */
static void on_frame(uint8_t type, const uint8_t *p, uint16_t n, uint32_t now) {
    g_teensy_ms = now;
    if (type == LL_ITEM || type == LL_DATA) g_outstanding -= n;   /* credit the Teensy has used */
    if (type == LL_ITEM || type == LL_START || type == LL_DATA || type == LL_END || type == LL_ERR) g_data_ms = now;
    switch (type) {
    case LL_INFO:
        if (n == sizeof g_info) { memcpy(&g_info, p, n); c_info->setValue((const uint8_t *)&g_info, sizeof g_info); }
        break;
    case LL_ITEM:
        if (g_mode == M_LIST) q_push(type, p, n);
        break;
    case LL_START:
    case LL_DATA:
    case LL_END:
        if (g_mode != M_SEND) break;
        if (type == LL_START) g_await_start = false;
        if (!g_await_start) q_push(type, p, n);    /* DATA of an aborted transfer is dropped */
        break;
    case LL_ERR:
        if (g_mode == M_ACK) g_st_force = true;   /* ERR 0 after an ACK leaves status DONE / 0 unchanged - the phone must still hear it (LL18) */
        q_push(type, p, n);
        break;
    case LL_PAIR:
        if (n == sizeof(ll_pair_t)) pair_open(p[0]);
        break;
    case LL_UNBOND:
        forget_phones();
        break;
    default:
        break;
    }
}

/* The queue to the phone, as fast as NimBLE takes notifications. */
static void pump() {
    uint8_t type, p[LL_LEN_MAX];
    uint16_t n;
    for (int k = 0; k < 16 && q_peek(&type, p, &n); k++) {
        bool ok = true;
        switch (type) {
        case LL_ITEM:
            ok = c_drives->notify(p, n, g_conn);
            if (ok) {
                uint32_t seq; memcpy(&seq, p, 4);
                if (seq == 0) { g_mode = M_IDLE; set_status(LL_S_IDLE, LL_E_NONE); }
                g_regrant += n;
            }
            break;
        case LL_START: {
            ll_start_t s; memcpy(&s, p, sizeof s);
            g_st.sent = s.offset; g_st.total = s.total;
            break; }
        case LL_DATA: {
            uint32_t off; memcpy(&off, p, 4);
            uint16_t len = (uint16_t)(n - 4);
            uint16_t chunk = g_mtu > 7 + 1 ? (uint16_t)(g_mtu - 7) : 1;   /* LL09: up to MTU - 7 */
            while (g_split < len) {
                uint16_t k2 = len - g_split < chunk ? len - g_split : chunk;
                uint8_t nb[4 + LL_DATA_MAX];
                uint32_t o = off + g_split;
                memcpy(nb, &o, 4); memcpy(nb + 4, p + 4 + g_split, k2);
                if (!c_data->notify(nb, 4 + k2, g_conn)) { ok = false; break; }
                g_split += k2;
                g_st.sent = o + k2;
            }
            if (ok) g_regrant += n;
            break; }
        case LL_END: {
            ll_end_t e; memcpy(&e, p, sizeof e);
            g_st.crc32 = e.crc32;
            g_mode = M_IDLE;
            set_status(LL_S_DONE, LL_E_NONE);
            break; }
        case LL_ERR:
            if (p[0] == LL_E_NONE) set_status(LL_S_DONE, LL_E_NONE);   /* an ACK taken */
            else set_status(LL_S_ERROR, p[0]);
            g_mode = M_IDLE;
            break;
        }
        if (!ok) return;                       /* NimBLE is full: the same entry next pass */
        q_pop(n);
    }
}

static void link_setup() {
    g_req_q = xQueueCreate(8, sizeof(Req));
    NimBLEDevice::setMTU(247);                            /* LL09 */
    NimBLEDevice::setSecurityAuth(true, true, true);      /* bond, MITM, Secure Connections (LL02) */
    NimBLEDevice::setSecurityIOCap(BLE_HS_IO_DISPLAY_ONLY);/* the key is shown, the phone types it */
    for (int i = 0; i < NimBLEDevice::getNumBonds(); i++) NimBLEDevice::whiteListAdd(NimBLEDevice::getBondedAddress(i));

    g_srv = NimBLEDevice::createServer();
    g_srv->setCallbacks(new SrvCb());
    g_srv->advertiseOnDisconnect(false);                  /* advertise() decides */
    NimBLEService *svc = g_srv->createService(LL_UUID_SERVICE);
    const uint32_t SECURE_R = NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::READ_ENC | NIMBLE_PROPERTY::READ_AUTHEN;
    c_info    = svc->createCharacteristic(LL_UUID_INFO,    SECURE_R);
    c_drives  = svc->createCharacteristic(LL_UUID_DRIVES,  SECURE_R | NIMBLE_PROPERTY::NOTIFY);
    c_control = svc->createCharacteristic(LL_UUID_CONTROL, NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_ENC | NIMBLE_PROPERTY::WRITE_AUTHEN);
    c_data    = svc->createCharacteristic(LL_UUID_DATA,    SECURE_R | NIMBLE_PROPERTY::NOTIFY);
    c_status  = svc->createCharacteristic(LL_UUID_STATUS,  SECURE_R | NIMBLE_PROPERTY::NOTIFY);
    c_control->setCallbacks(new ControlCb());
    c_info->setValue((const uint8_t *)&g_info, sizeof g_info);
    c_status->setValue((const uint8_t *)&g_st, sizeof g_st);
    g_srv->start();                                       /* the GATT table, before advertising */

    NimBLEAdvertising *adv = NimBLEDevice::getAdvertising();
    adv->setName(LL_DEVICE_NAME);
    adv->addServiceUUID(NimBLEUUID(LL_UUID_SERVICE));
    adv->enableScanResponse(false);
    adv->setMinInterval(1600);                            /* 1 s, in 0.625 ms units (LL01) */
    adv->setMaxInterval(1600);
    advertise();
}

static void link_events(uint32_t now) {
    if (ev_disconnect) {
        ev_disconnect = false;
        if (ev_disc_handle == g_conn) {                    /* not a second phone we turned away */
            if (g_mode == M_SEND || g_mode == M_LIST) to_teensy(LL_ABORT, nullptr, 0);
            q_clear(); g_mode = M_IDLE; g_secure = false;
            g_conn = BLE_HS_CONN_HANDLE_NONE;
            set_status(LL_S_IDLE, LL_E_NONE);
            advertise();
        }
    }
    if (ev_connect) {
        ev_connect = false;
        uint16_t h = ev_conn_handle;
        if (g_conn != BLE_HS_CONN_HANDLE_NONE) { g_srv->disconnect(h); }      /* one phone at a time */
        else {
            g_conn = h; g_conn_ms = now; g_secure = false; g_mtu = 23;
            NimBLEDevice::startSecurity(h);               /* bonded: encrypt; pairing: the passkey */
            g_srv->updatePhy(h, BLE_GAP_LE_PHY_2M_MASK, BLE_GAP_LE_PHY_2M_MASK, 0);   /* LL09: 2M asked for */
            g_srv->setDataLen(h, 251);
        }
    }
    if (ev_auth) {
        ev_auth = false;
        bool known = known_phone(ev_auth_addr);
        if (ev_auth_ok && (known || g_pairing)) {
            g_secure = true;
            if (!known) {                                  /* a new bond, inside the window */
                NimBLEDevice::whiteListAdd(ev_auth_addr);
                g_pairing = false;
                pairing_to_teensy(LL_PAIR_BONDED);
            }
            to_teensy(LL_PING, nullptr, 0);
        } else {
            if (ev_auth_ok && !known) NimBLEDevice::deleteBond(ev_auth_addr);   /* bonded outside the window */
            if (g_pairing) pairing_to_teensy(LL_PAIR_FAILED);
            if (g_conn != BLE_HS_CONN_HANDLE_NONE) g_srv->disconnect(g_conn);
        }
    }
    /* a phone that has not secured the link in time is let go */
    if (g_conn != BLE_HS_CONN_HANDLE_NONE && !g_secure && now - g_conn_ms > (g_pairing ? 60000u : 10000u))
        g_srv->disconnect(g_conn);
    if (g_pairing && (int32_t)(now - g_pair_until) >= 0) {
        g_pairing = false;
        pairing_to_teensy(LL_PAIR_CLOSED);
        advertise();
    }
}

static void link_loop(uint32_t now) {
    /* the wire from the Teensy: frames and $CELLS lines */
    for (int b = 0; b < 2048 && Serial1.available(); b++) {
        int r = ll_rx_feed(&g_rx, (uint8_t)Serial1.read());
        if (r == LL_RX_FRAME) on_frame(ll_rx_type(&g_rx), ll_rx_payload(&g_rx), ll_rx_plen(&g_rx), now);
        else if (r == LL_RX_LINE) on_line(g_rx.line, strlen(g_rx.line));
    }
    link_events(now);
    Req r;
    while (xQueueReceive(g_req_q, &r, 0) == pdTRUE) if (g_secure) on_control(r);

    if (g_secure) pump(); else if (q_used) q_clear();
    if (g_regrant >= CREDIT_STEP || (g_regrant && q_used == 0)) {
        grant((uint16_t)g_regrant);            /* what went out to the phone is given back */
        g_regrant = 0;
    }

    /* LL14: no DATA for 5 s while the Teensy holds credit, or no frame at all for 5 s,
     * is err 6 - mid-transfer the Teensy is told to stop */
    static uint32_t last_ping = 0;
    if (now - last_ping >= PING_MS) { last_ping = now; to_teensy(LL_PING, nullptr, 0); }
    bool busy = g_mode == M_SEND || g_mode == M_LIST;
    bool stalled = busy && g_outstanding >= 5 && now - g_data_ms > LL_TIMEOUT_MS;
    if ((stalled || now - g_teensy_ms > LL_TIMEOUT_MS) && g_st.err != LL_E_SILENT) {
        if (busy) to_teensy(LL_ABORT, nullptr, 0);
        q_clear(); g_mode = M_IDLE;
        set_status(LL_S_ERROR, LL_E_SILENT);
    }

    /* status: on every change, and once a second during a transfer (LL10) */
    bool changed = memcmp(&g_st, &g_st_sent, sizeof g_st) != 0;
    if (g_secure && (changed || g_st_force || (g_st.state == LL_S_SENDING && now - g_st_ms >= LL_STATUS_MS))) {
        c_status->setValue((const uint8_t *)&g_st, sizeof g_st);
        if (c_status->notify((const uint8_t *)&g_st, sizeof g_st, g_conn)) { g_st_sent = g_st; g_st_ms = now; g_st_force = false; }
    }
}

void setup() {
    Serial1.setRxBufferSize(8192);
    Serial1.begin(LL_BAUD);                    /* to the Teensy's Serial2, 921600 (D-493) */
    ll_rx_init(&g_rx);
    NimBLEDevice::init(LL_DEVICE_NAME);
    NimBLEScan *scan = NimBLEDevice::getScan();
    scan->setScanCallbacks(new ScanCb(), true);
    scan->setActiveScan(false);                /* passive: we only listen   */
    scan->setInterval(160);
    scan->setWindow(80);
    scan->start(0, false, true);               /* forever, keep results off */
    link_setup();
}

void loop() {
    static uint32_t last = 0;
    uint32_t now = millis();
    link_loop(now);
    bool transferring = g_mode == M_SEND;
    if (g_want_cells && !transferring) cells_connect(); else cells_disconnect();
    if (now - last >= LINE_MS) { last = now; send_line(); }
    delay(1);
}

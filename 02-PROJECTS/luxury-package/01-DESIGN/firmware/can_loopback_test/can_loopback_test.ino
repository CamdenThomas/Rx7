/*
 * can_loopback_test.ino — Stage 3
 *
 * Brings up CAN1 in INTERNAL LOOPBACK at 500 kbps and runs every message in
 * can_map.h through the controller and back.
 *
 * NO TRANSCEIVER NEEDED. Nothing leaves the chip. No wires, no resistors.
 *
 * SETUP:
 *   1. Arduino IDE -> Tools -> Manage Libraries -> search "ACAN_T4" -> install
 *      (Pierre Molinaro's library. NOT FlexCAN_T4 - it doesn't expose loopback)
 *   2. Copy can_map.h into this folder, beside this .ino
 *   3. Upload. Serial Monitor at 115200.
 *
 * WHY LOOPBACK MATTERS: a real CAN node needs another node to ACK every frame.
 * One Teensy alone on a bus transmits, gets no ACK, and retries forever.
 * Loopback mode disables the ACK requirement so a single chip can test itself.
 */

#include <ACAN_T4.h>
#include "can_map.h"

int failures = 0;
int received  = 0;

void check(const char *name, bool ok) {
  Serial.print(ok ? "PASS  " : "FAIL  ");
  Serial.println(name);
  if (!ok) failures++;
}

/* ---------- build one of each message ---------- */

CANMessage makeIcuSensors() {
  CANMessage f;
  f.id  = ID_ICU_SENSORS;
  f.len = 8;

  icu_sensors_t s = {};
  s.rpm            = 6500;
  s.water_c        = TEMP_ENCODE(92);
  s.oil_temp_c     = TEMP_ENCODE(110);
  s.oil_press_cbar = 435;
  s.speed_kph      = 137;
  s.counter        = 7;

  memcpy(f.data, &s, 8);
  return f;
}

CANMessage makePmuState() {
  CANMessage f;
  f.id  = ID_PMU_STATE;
  f.len = 8;

  pmu_state_t s = {};
  s.key_pos     = KEY_RUN;
  s.wake_source = WAKE_RUN | WAKE_HORN;
  s.fault       = 0;
  s.headlight   = HL_HEAD;
  s.turn        = TURN_LEFT;
  s.popup       = POP_UP;
  s.counter     = 11;

  memcpy(f.data, &s, 8);
  return f;
}

CANMessage makeDcuClimate() {
  CANMessage f;
  f.id  = ID_DCU_CLIMATE;
  f.len = 8;

  dcu_climate_t c = {};
  c.mode       = CLIM_HEAT;
  c.blower     = 2;
  c.target_c   = 21;
  c.cabin_c    = TEMP_ENCODE(8);
  c.ac_request = 0;
  c.counter    = 3;

  memcpy(f.data, &c, 8);
  return f;
}

/* ---------- send one frame, wait for it to come back ---------- */

bool sendAndReceive(const CANMessage &tx, CANMessage &rx) {
  if (!ACAN_T4::can1.tryToSend(tx)) {
    Serial.println("   tryToSend() refused - TX buffer full?");
    return false;
  }

  /* Loopback is fast, but give it a sane window rather than spinning forever */
  const uint32_t deadline = millis() + 50;
  while (millis() < deadline) {
    if (ACAN_T4::can1.receive(rx)) {
      received++;
      return true;
    }
  }
  return false;
}

/* ---------- the dispatch switch, exactly as real firmware will do it ---------- */

const char *dispatch(const CANMessage &f) {
  switch (f.id) {
    case ID_PMU_STATE:    return "PMU state";
    case ID_PMU_POWER:    return "PMU power";
    case ID_PMU_OUTPUTS:  return "PMU outputs";
    case ID_PMU_CHANNEL:  return "PMU channel";
    case ID_ICU_SENSORS:  return "ICU sensors";
    case ID_ICU_HEALTH:   return "ICU health";
    case ID_DCU_CLIMATE:  return "DCU climate";
    case ID_DCU_COMFORT:  return "DCU comfort";
    case ID_DCU_RADAR:    return "DCU radar";
    case ID_KEYPAD:       return "Keypad";
    default:              return "UNKNOWN";
  }
}

void testOneMessage(const char *label, const CANMessage &tx) {
  Serial.print("\n-- "); Serial.print(label); Serial.println(" --");

  CANMessage rx;
  if (!sendAndReceive(tx, rx)) {
    check("frame came back", false);
    return;
  }

  check("frame came back", true);
  check("ID preserved",    rx.id  == tx.id);
  check("length is 8",     rx.len == 8);

  bool payloadOk = true;
  for (int i = 0; i < 8; i++) {
    if (rx.data[i] != tx.data[i]) payloadOk = false;
  }
  check("payload byte-identical", payloadOk);

  Serial.print("   dispatched as: ");
  Serial.println(dispatch(rx));
}

/* ---------- decode a received sensor frame, as the ICU consumer will ---------- */

void testDecode() {
  Serial.println("\n-- decode as a consumer would --");

  CANMessage tx = makeIcuSensors();
  CANMessage rx;
  if (!sendAndReceive(tx, rx)) {
    check("sensors frame returned", false);
    return;
  }

  icu_sensors_t s;
  memcpy(&s, rx.data, 8);

  check("rpm decodes to 6500",  s.rpm == 6500);
  check("water decodes to 92C", TEMP_DECODE(s.water_c) == 92);
  check("oil temp 110C",        TEMP_DECODE(s.oil_temp_c) == 110);
  check("oil press 4.35 bar",   s.oil_press_cbar == 435);
  check("speed 137 kph",        s.speed_kph == 137);
}

/* ---------- timeout: the receiver must BLANK, not hold ---------- */

void testTimeout() {
  Serial.println("\n-- timeout behaviour --");

  uint32_t lastRx = millis();

  /* Send one, then deliberately go quiet */
  CANMessage tx = makeIcuSensors();
  CANMessage rx;
  if (sendAndReceive(tx, rx)) lastRx = millis();

  Serial.print("   staying silent for ");
  Serial.print(TMO_ICU_SENSORS + 100);
  Serial.println(" ms...");
  delay(TMO_ICU_SENSORS + 100);

  bool timedOut = (millis() - lastRx) > TMO_ICU_SENSORS;
  check("timeout correctly detected", timedOut);
  Serial.println("   -> real firmware BLANKS the gauge here, never holds the");
  Serial.println("      last value. A frozen gauge lies; a blank one doesn't.");
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 4000) { }

  Serial.println("=====================================");
  Serial.println(" CAN loopback test - no transceiver");
  Serial.println("=====================================");

  ACAN_T4_Settings settings(500 * 1000);   /* 500 kbps, matches D-086 */
  settings.mLoopBackMode      = true;      /* controller talks to itself */
  settings.mSelfReceptionMode = true;      /* and hears what it sent     */

  const uint32_t errorCode = ACAN_T4::can1.begin(settings);

  if (errorCode == 0) {
    Serial.println("CAN1 up at 500 kbps, loopback + self-reception.");
  } else {
    Serial.print("CAN1 FAILED to start, error 0x");
    Serial.println(errorCode, HEX);
    Serial.println("Is ACAN_T4 installed? Library Manager -> ACAN_T4");
    return;
  }

  testOneMessage("ICU sensors 0x200", makeIcuSensors());
  testOneMessage("PMU state   0x100", makePmuState());
  testOneMessage("DCU climate 0x300", makeDcuClimate());
  testDecode();
  testTimeout();

  Serial.println("\n=====================================");
  Serial.print(" frames round-tripped: ");
  Serial.println(received);
  if (failures == 0) {
    Serial.println(" ALL CHECKS PASSED");
    Serial.println(" CAN stack works. Transceivers just replace");
    Serial.println(" loopback with a wire.");
  } else {
    Serial.print(" FAILURES: ");
    Serial.println(failures);
  }
  Serial.println("=====================================");
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH); delay(400);
  digitalWrite(LED_BUILTIN, LOW);  delay(400);
}

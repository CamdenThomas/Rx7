/*
 * can_map_test.ino — Stage 2 validation
 *
 * Proves can_map.h is correct before anything depends on it.
 * Needs NO transceiver, NO PMU, NO car. Just a Teensy and a USB cable.
 *
 * SETUP:
 *   1. Put this file and can_map.h in the same folder, both named
 *      can_map_test  (Arduino requires folder name == .ino name)
 *   2. Upload. Open Serial Monitor at 115200.
 *
 * Every check must print PASS. A single FAIL means a packing or encoding bug
 * that would otherwise show up as garbage on the bus at 2am.
 */

#include "can_map.h"

/* ---- compile-time checks ----
 * These fail the BUILD, not the run. If the sketch compiles, they passed.
 * Struct packing is silent when wrong, which is what makes it dangerous. */
static_assert(sizeof(pmu_state_t)    == 8, "pmu_state_t must be 8 bytes");
static_assert(sizeof(pmu_power_t)    == 8, "pmu_power_t must be 8 bytes");
static_assert(sizeof(pmu_outputs_t)  == 8, "pmu_outputs_t must be 8 bytes");
static_assert(sizeof(pmu_channel_t)  == 8, "pmu_channel_t must be 8 bytes");
static_assert(sizeof(icu_sensors_t)  == 8, "icu_sensors_t must be 8 bytes");
static_assert(sizeof(icu_health_t)   == 8, "icu_health_t must be 8 bytes");
static_assert(sizeof(dcu_climate_t)  == 8, "dcu_climate_t must be 8 bytes");
static_assert(sizeof(dcu_comfort_t)  == 8, "dcu_comfort_t must be 8 bytes");
static_assert(sizeof(dcu_radar_t)    == 8, "dcu_radar_t must be 8 bytes");
static_assert(sizeof(keypad_t)       == 8, "keypad_t must be 8 bytes");

int failures = 0;

void check(const char *name, bool ok) {
  Serial.print(ok ? "PASS  " : "FAIL  ");
  Serial.println(name);
  if (!ok) failures++;
}

/* ---- round trip: struct -> 8 bytes -> struct ----
 * This is exactly what happens on the bus. If it doesn't survive here,
 * it won't survive there. */
void test_roundtrip() {
  Serial.println("\n-- round trip --");

  icu_sensors_t tx = {};
  tx.rpm             = 6500;
  tx.water_c         = TEMP_ENCODE(92);
  tx.oil_temp_c      = TEMP_ENCODE(110);
  tx.oil_press_cbar  = 435;      /* 4.35 bar */
  tx.speed_kph       = 137;
  tx.counter         = 200;

  uint8_t buf[8];
  memcpy(buf, &tx, 8);

  icu_sensors_t rx;
  memcpy(&rx, buf, 8);

  check("rpm survives",        rx.rpm == 6500);
  check("water temp survives", TEMP_DECODE(rx.water_c) == 92);
  check("oil temp survives",   TEMP_DECODE(rx.oil_temp_c) == 110);
  check("oil press survives",  rx.oil_press_cbar == 435);
  check("speed survives",      rx.speed_kph == 137);
  check("counter survives",    rx.counter == 200);
}

/* ---- temperature encode/decode across the real range ---- */
void test_temperature() {
  Serial.println("\n-- temperature --");

  int cases[] = { -40, -20, 0, 20, 92, 110, 127 };
  bool ok = true;
  for (unsigned i = 0; i < sizeof(cases)/sizeof(cases[0]); i++) {
    int8_t enc = TEMP_ENCODE(cases[i]);
    int dec = TEMP_DECODE(enc);
    if (dec != cases[i]) {
      ok = false;
      Serial.print("   mismatch at "); Serial.println(cases[i]);
    }
  }
  check("temp round trips -40..127 C", ok);
  check("TEMP_INVALID is distinct",    TEMP_DECODE(TEMP_INVALID) == -128);
}

/* ---- counter wrap ----
 * THIS is the one that matters. 255 -> 0 is where naive stall detection
 * breaks and reports a dead sender that is perfectly healthy. */
void test_counter_wrap() {
  Serial.println("\n-- counter wrap --");

  check("normal advance 10->11",  can_counter_advanced(10, 11));
  check("advance 254->255",       can_counter_advanced(254, 255));
  check("WRAP 255->0 advances",   can_counter_advanced(255, 0));
  check("wrap 250->3 advances",   can_counter_advanced(250, 3));
  check("stalled 42->42 detected", !can_counter_advanced(42, 42));
  check("stalled 0->0 detected",   !can_counter_advanced(0, 0));
}

/* ---- bitfields ---- */
void test_bitfields() {
  Serial.println("\n-- bitfields --");

  pmu_state_t s = {};
  s.wake_source = WAKE_HAZARD | WAKE_HORN;

  check("hazard wake set",     (s.wake_source & WAKE_HAZARD) != 0);
  check("horn wake set",       (s.wake_source & WAKE_HORN)   != 0);
  check("door wake NOT set",   (s.wake_source & WAKE_DOOR)   == 0);

  icu_health_t h = {};
  h.sensor_valid = SENS_RPM | SENS_WATER | SENS_OILPRESS;
  check("oil press valid",     (h.sensor_valid & SENS_OILPRESS) != 0);
  check("VSS not valid",       (h.sensor_valid & SENS_VSS)      == 0);
}

/* ---- channel index mapping ---- */
void test_channel_index() {
  Serial.println("\n-- channel index --");
  check("index 0 is O1",   CH_INDEX_TO_OUTPUT(0)  == 1);
  check("index 23 is O24", CH_INDEX_TO_OUTPUT(23) == 24);
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 4000) { }   /* wait for the monitor, but not forever */

  Serial.println("=====================================");
  Serial.println(" can_map.h validation");
  Serial.println("=====================================");
  Serial.println("All struct sizes passed at compile time.");

  test_roundtrip();
  test_temperature();
  test_counter_wrap();
  test_bitfields();
  test_channel_index();

  Serial.println("\n=====================================");
  if (failures == 0) {
    Serial.println(" ALL CHECKS PASSED");
    Serial.println(" can_map.h is safe to build on.");
  } else {
    Serial.print(" FAILURES: ");
    Serial.println(failures);
    Serial.println(" DO NOT build firmware on this header yet.");
  }
  Serial.println("=====================================");
}

void loop() {
  /* Heartbeat. Slow blink means the sketch is running and didn't hang. */
  digitalWrite(LED_BUILTIN, HIGH); delay(900);
  digitalWrite(LED_BUILTIN, LOW);  delay(900);
}

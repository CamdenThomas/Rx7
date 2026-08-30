/*
 * tach_simulator.ino — Stage 5
 *
 * Validates the RPM measurement path with ONE board and ONE jumper wire.
 *
 * The same Teensy generates a simulated tach signal on pin 3 and measures it
 * on pin 4. Sweeps 500 -> 8000 rpm and back, checking measured against
 * generated the whole way.
 *
 * HARDWARE:
 *   ONE jumper wire: pin 3 -> pin 4. That's it.
 *   No transceiver, no second board, no car.
 *
 * WHY THIS MATTERS:
 *   RPM is the one gauge you look at constantly and the one signal that is
 *   hardest to get right - the real tach input is a coil primary pulse with
 *   spikes well above 12V (V-041). This proves the *measurement* half works
 *   before you ever build the *conditioning* half.
 *
 * Serial Monitor at 115200.
 */

#include <Arduino.h>

const int OUT_PIN = 3;    /* generates the simulated tach pulse */
const int IN_PIN  = 4;    /* measures it. Jumper 3 -> 4 */

/* ---------------------------------------------------------------
 * PULSES PER REVOLUTION
 *
 * On a 12A rotary the tach is driven off the leading coil. Each rotor
 * fires once per eccentric shaft revolution, so a 2-rotor gives 2 pulses
 * per rev - but this MUST be confirmed against the real car.
 *
 * Logged as [V-067]. Getting it wrong scales every RPM reading.
 * --------------------------------------------------------------- */
const float PULSES_PER_REV = 2.0f;

/* ---------------------------------------------------------------
 * Measurement, interrupt driven.
 * Period between rising edges, averaged over a short window.
 * --------------------------------------------------------------- */
volatile uint32_t lastEdgeUs   = 0;
volatile uint32_t periodSumUs  = 0;
volatile uint16_t periodCount  = 0;
volatile uint32_t lastSeenMs   = 0;

void tachISR() {
  uint32_t now = micros();
  uint32_t dt  = now - lastEdgeUs;
  lastEdgeUs   = now;

  /* Reject implausibly short gaps - that is noise, not a cylinder.
   * 40us == 25kHz == far above any real engine speed. */
  if (dt > 40) {
    periodSumUs += dt;
    periodCount++;
    lastSeenMs = millis();
  }
}

float readRPM() {
  noInterrupts();
  uint32_t sum = periodSumUs;
  uint16_t cnt = periodCount;
  uint32_t seen = lastSeenMs;
  periodSumUs = 0;
  periodCount = 0;
  interrupts();

  /* No pulse recently -> genuinely zero, not stale. */
  if (millis() - seen > 500) return 0.0f;
  if (cnt == 0) return -1.0f;             /* no new data this window */

  float avgPeriodUs = (float)sum / (float)cnt;
  float freqHz      = 1000000.0f / avgPeriodUs;
  return (freqHz * 60.0f) / PULSES_PER_REV;
}

/* ---------------------------------------------------------------
 * Signal generation.
 * analogWriteFrequency sets the PWM rate; analogWrite at half scale
 * gives a 50% duty square wave.
 * --------------------------------------------------------------- */
void setSimulatedRPM(float rpm) {
  if (rpm <= 0) { analogWrite(OUT_PIN, 0); return; }
  float freqHz = (rpm * PULSES_PER_REV) / 60.0f;
  analogWriteFrequency(OUT_PIN, freqHz);
  analogWrite(OUT_PIN, 128);              /* 50% of 8-bit default */
}

int failures = 0;

void testPoint(float targetRPM) {
  setSimulatedRPM(targetRPM);
  delay(300);                             /* let it settle and gather edges */
  readRPM();                              /* discard the first window */
  delay(200);
  float measured = readRPM();

  float err = (targetRPM > 0)
            ? fabs(measured - targetRPM) / targetRPM * 100.0f
            : fabs(measured);

  bool ok = (targetRPM > 0) ? (err < 3.0f) : (measured < 1.0f);
  if (!ok) failures++;

  Serial.print(ok ? "PASS  " : "FAIL  ");
  Serial.print("target ");
  Serial.print(targetRPM, 0);
  Serial.print(" rpm   measured ");
  Serial.print(measured, 0);
  Serial.print("   error ");
  Serial.print(err, 1);
  Serial.println("%");
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 4000) { }

  pinMode(OUT_PIN, OUTPUT);
  pinMode(IN_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(IN_PIN), tachISR, RISING);

  Serial.println("=====================================");
  Serial.println(" Tach measurement validation");
  Serial.println("=====================================");
  Serial.print("Jumper pin "); Serial.print(OUT_PIN);
  Serial.print(" -> pin "); Serial.println(IN_PIN);
  Serial.print("Pulses per rev: "); Serial.println(PULSES_PER_REV, 1);
  Serial.println("  ^ [V-067] CONFIRM against the real car\n");

  Serial.println("-- sweep up --");
  testPoint(500);
  testPoint(1000);
  testPoint(2000);
  testPoint(3000);
  testPoint(4500);
  testPoint(6000);
  testPoint(7000);
  testPoint(8000);

  Serial.println("\n-- step changes, no ramp --");
  testPoint(800);
  testPoint(6500);
  testPoint(1200);

  Serial.println("\n-- zero rpm --");
  Serial.println("   stopped engine must read 0, not the last value");
  testPoint(0);

  Serial.println("\n=====================================");
  if (failures == 0) {
    Serial.println(" ALL RPM CHECKS PASSED");
    Serial.println(" Measurement path is good. What remains is");
    Serial.println(" signal conditioning - see V-041.");
  } else {
    Serial.print(" FAILURES: ");
    Serial.println(failures);
    Serial.println(" Check the jumper between pins 3 and 4.");
  }
  Serial.println("=====================================");
  Serial.println("\nLive sweep. Watch it track continuously.\n");
}

/* Continuous sweep so you can watch it track, and leave it running
 * as a signal source when the display work starts. */
void loop() {
  static float rpm = 800;
  static float dir = 25;

  rpm += dir;
  if (rpm > 8000) dir = -25;
  if (rpm < 800)  dir =  25;

  setSimulatedRPM(rpm);
  delay(40);

  static uint32_t lastPrint = 0;
  if (millis() - lastPrint > 250) {
    lastPrint = millis();
    float m = readRPM();
    if (m >= 0) {
      Serial.print("gen ");  Serial.print(rpm, 0);
      Serial.print("   measured "); Serial.println(m, 0);
    }
  }
}

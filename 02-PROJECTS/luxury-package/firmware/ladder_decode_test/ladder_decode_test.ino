/*
 * ladder_decode_test.ino — Stage 4
 *
 * Validates the resistor-ladder decode logic from 01-DESIGN/LADDERS.md
 * before a single resistor is soldered.
 *
 * HARDWARE — pick one:
 *   A) A potentiometer: outer legs to 3.3V and GND, wiper to pin A0.
 *      Sweep it and watch every state appear in order.
 *   B) Just a jumper wire on A0: touch it to 3.3V (reads ~1023) and to
 *      GND (reads ~0). Proves the fault bands. Less thorough but valid.
 *   C) Nothing at all: set SIMULATE to true below and it self-tests
 *      against synthetic ADC values.
 *
 * !!! 3.3V ONLY. The Teensy 4.1 is NOT 5V tolerant. !!!
 * Never touch A0 to a 5V rail. It will kill the pin.
 *
 * Serial Monitor at 115200.
 */

#include <Arduino.h>

const int LADDER_PIN = A0;
const bool SIMULATE  = false;   /* true = run self-test with no hardware */

/* ---------------------------------------------------------------
 * A ladder state: a name and the ADC window that means it.
 * WINDOWS, not thresholds. A reading between windows is a FAULT,
 * not "the nearest state" - that is the whole point of the 01-DESIGN.
 * --------------------------------------------------------------- */
struct LadderState {
  const char *name;
  int lo;
  int hi;
};

/* Values from 01-DESIGN/LADDERS.md. 10-bit, 0-1023. */

const LadderState TURN_STALK[] = {
  { "LEFT",   100, 210 },
  { "RIGHT",  450, 570 },
  { "OFF",    790, 900 },
};

const LadderState WIPER_STALK[] = {
  { "WASH",   110, 200 },
  { "HIGH",   280, 375 },
  { "LOW",    465, 560 },
  { "INT",    610, 705 },
  { "OFF",    800, 890 },
};

const LadderState BRAKE_PEDAL[] = {
  { "PRESSED",  280, 375 },
  { "RELEASED", 980, 1023 },
};

const LadderState POPUP_POS[] = {
  { "DOWN limit", 210, 300 },
  { "UP limit",   465, 560 },
  { "mid-travel", 800, 890 },
};

const LadderState DOOR_PINS[] = {
  { "both open",      380, 432 },
  { "passenger only", 435, 490 },
  { "driver only",    740, 830 },
  { "both closed",    980, 1023 },
};

/* ---------------------------------------------------------------
 * The decode function. This exact logic goes into ICU firmware.
 * Returns the state name, or a fault string.
 * --------------------------------------------------------------- */
const char *decode(int adc, const LadderState *table, int count) {
  if (adc < 40)   return "FAULT - shorted to ground";
  if (adc > 1000 && strcmp(table[count-1].name, "RELEASED") != 0
                 && strcmp(table[count-1].name, "both closed") != 0) {
    return "FAULT - open circuit";
  }
  for (int i = 0; i < count; i++) {
    if (adc >= table[i].lo && adc <= table[i].hi) return table[i].name;
  }
  return "FAULT - between states";
}

/* ---------------------------------------------------------------
 * Self-test: feed known values, confirm the right state comes out.
 * --------------------------------------------------------------- */
int failures = 0;

void expect(const char *label, int adc, const LadderState *t, int n,
            const char *want) {
  const char *got = decode(adc, t, n);
  bool ok = (strcmp(got, want) == 0);
  Serial.print(ok ? "PASS  " : "FAIL  ");
  Serial.print(label);
  Serial.print("  adc="); Serial.print(adc);
  Serial.print("  -> "); Serial.println(got);
  if (!ok) { failures++; Serial.print("      expected: "); Serial.println(want); }
}

void selfTest() {
  Serial.println("\n-- turn stalk --");
  expect("centre of LEFT ",  156, TURN_STALK, 3, "LEFT");
  expect("centre of RIGHT",  512, TURN_STALK, 3, "RIGHT");
  expect("centre of OFF  ",  843, TURN_STALK, 3, "OFF");
  expect("between states ",  300, TURN_STALK, 3, "FAULT - between states");
  expect("shorted        ",    5, TURN_STALK, 3, "FAULT - shorted to ground");
  expect("open circuit   ", 1023, TURN_STALK, 3, "FAULT - open circuit");

  Serial.println("\n-- wiper stalk, all five --");
  expect("WASH", 156, WIPER_STALK, 5, "WASH");
  expect("HIGH", 327, WIPER_STALK, 5, "HIGH");
  expect("LOW ", 512, WIPER_STALK, 5, "LOW");
  expect("INT ", 658, WIPER_STALK, 5, "INT");
  expect("OFF ", 843, WIPER_STALK, 5, "OFF");

  Serial.println("\n-- door pins, the tight one --");
  Serial.println("   55 counts between 'both open' and 'passenger only'.");
  Serial.println("   Tightest ladder in the car. Watch this one on the bench.");
  expect("both open     ", 406, DOOR_PINS, 4, "both open");
  expect("passenger only", 461, DOOR_PINS, 4, "passenger only");
  expect("driver only   ", 785, DOOR_PINS, 4, "driver only");
  expect("both closed   ", 1023, DOOR_PINS, 4, "both closed");
  expect("in the 3-count gap", 433, DOOR_PINS, 4, "FAULT - between states");

  Serial.println("\n-- brake pedal --");
  expect("pressed ",  327, BRAKE_PEDAL, 2, "PRESSED");
  expect("released", 1023, BRAKE_PEDAL, 2, "RELEASED");
  expect("chafed to gnd", 5, BRAKE_PEDAL, 2, "FAULT - shorted to ground");
  Serial.println("   ^ this is why no state uses a dead short (D-053).");
  Serial.println("     A chafed wire is distinguishable from a pressed pedal.");

  Serial.println("\n-- pop-up position --");
  expect("DOWN", 254, POPUP_POS, 3, "DOWN limit");
  expect("UP  ", 512, POPUP_POS, 3, "UP limit");
  expect("mid ", 843, POPUP_POS, 3, "mid-travel");
  Serial.println("   ^ PROVISIONAL. Real values come from T-011 continuity test.");
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 4000) { }

  analogReadResolution(10);          /* 0-1023, matches A1-A8 on the PMU */

  Serial.println("=====================================");
  Serial.println(" Ladder decode validation");
  Serial.println("=====================================");
  Serial.println("Windows, not thresholds. Between states = FAULT.");

  selfTest();

  Serial.println("\n=====================================");
  if (failures == 0) Serial.println(" ALL DECODE CHECKS PASSED");
  else { Serial.print(" FAILURES: "); Serial.println(failures); }
  Serial.println("=====================================");

  if (!SIMULATE) {
    Serial.println("\nLive mode. Sweep a pot on A0, or touch a jumper");
    Serial.println("to 3.3V and GND. 3.3V ONLY - never 5V.\n");
  }
}

void loop() {
  if (SIMULATE) { delay(1000); return; }

  static int last = -99;
  int adc = analogRead(LADDER_PIN);

  if (abs(adc - last) > 4) {          /* only print on real change */
    last = adc;
    Serial.print("adc="); Serial.print(adc);
    Serial.print("   turn="); Serial.print(decode(adc, TURN_STALK, 3));
    Serial.print("   wiper="); Serial.println(decode(adc, WIPER_STALK, 5));
  }
  delay(60);
}

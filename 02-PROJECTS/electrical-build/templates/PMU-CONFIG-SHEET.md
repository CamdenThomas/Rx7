<!-- out: 03-INSTALL/PMU-CONFIG-SHEET.md -->
# PMU CONFIGURATION SHEET

Everything typed into the ECUMaster PMU client, in the order it is entered. Channel names are exact. Nothing here needs a current figure until §5.


## Entry order

1. Name all 39 channels (§0)  2. Enter the input decode tables (§1)  3. Enter the output expressions (§2)  4. Enter the rules and interlocks (§3)  5. Wake and shutdown (§4)  6. Save as `RevA-01`  7. After the L3 input check in the car: correct the windows from the live readings, save `RevA-02`  8. Enter the enable-at limits (§5) and, per circuit as it migrates, enable the output.


## 0 · Channel names

{{channel_names}}

## 1 · Input decode tables

Enter as lookup tables with windows. A reading between windows must report FAULT, not the nearest state. **Pull configuration:** A1–A8 = 10 kΩ pull-UP except A7 = 1 MΩ pull-DOWN · A15, A16 = 10 kΩ pull-DOWN.


{{decode:A1}}

{{decode:A2}}

{{decode:A3}}

{{decode:A4}}

{{decode:A5}}

{{decode:A6}}

{{decode:A8}}

HAZARD is a band 265–370 (hazard alone 327; hazard + either wink 278 / 298 read as HAZARD).


**A7 `FUEL_LEVEL`** — three-point lookup with interpolation, read in the car: FULL ____ · MID ____ · EMPTY ____ (the factory gauge drives the sender; this input only observes it). FAULT below 10 and above 1000. If the reading is unstable, leave the channel unused — the cluster's gauge is the instrument.


{{decode:A15}}

{{decode:A16}}

A15 PASS: any reading ≥ 1750. A16 START: either 1720 or ~1650 depending on whether ACC drops during crank — set the window from the live reading.


## 2 · Output expressions

{{logic:config}}

## 3 · Rules and interlocks

{{rules}}

## 4 · Wake, shutdown, CAN

Wake sources on pin 7: ACC · RUN · door stage · horn/hazard/wink stage · O22 latch. Shutdown: `KEEP_ALIVE` releases 30 s after the last input change with the key OFF and the doors closed; the module sleeps and K11 opens. CAN1: 1 Mbps (fixed). CAN2: 500 kbps, termination ON. Enable data logging: every channel current at 10 Hz, every input at 10 Hz.


## 5 · Enable-at limits

The software limit typed in before each output is first enabled. `meas` = measured, keep; `cap` = channel cap, to be tightened from telemetry in shakedown (§7.5 of the install).

{{enable_at}}

## 6 · Save discipline

Version after every working step — `RevA-01`, `-02`, … Never overwrite. Log each version with the date and what changed:

| Version | Date | What changed | Backed up |
|---|---|---|---|
| RevA-01 |  | Names, tables, expressions, rules, wake | ☐ |
| RevA-02 |  | Windows corrected from live readings | ☐ |
|  |  |  | ☐ |
|  |  |  | ☐ |
|  |  |  | ☐ |

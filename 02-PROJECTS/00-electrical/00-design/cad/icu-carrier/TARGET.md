# What has to be on the sheet

*Rev 2026-09-12 (b) · owns: the drawing checklist for the ICU carrier.*

> **All five blocks are drawn** as of sheet rev 0.02, and ERC is clean at 0 errors and 0 warnings.
> This file stays as the checklist, because it is what a re-draw would be checked against.

> **This is a snapshot taken 2026-09-12, not a link.** The live record is
> `../../../data/icu_channels.csv` —
> `python tools/rx7.py sql 00-electrical "select * from icu_channels"`. If the CSV and this
> file disagree, the CSV is right and this file is stale: re-read it rather than trusting what
> is below. Nothing in the record depends on this file, and nothing in `../../../data/` cites it.

Draw in this order. Each block is finished when it passes ERC on its own.

## 1 · Power — the block where a mistake is expensive

- `DP-ICU-A 1` **logic 12 V** — accessory bus tap off O10. SS34 → SMBJ33A → LMR36015-Q1-class buck (60 V
  input) → `+5V` → Teensy VIN. ~0.8 A peak: Teensy, transceiver, IMU, three sender excitations, radio.
  The 36 V LMR33630 was rejected — it sits under the SMBJ33A's ~53 V clamp.
- `DP-ICU-A 6` **backlight 12 V** — F16 ignition aux, 5 A. SS34 → SMBJ33A → 4 A fuse → ≥ 60 V high-side
  switch (SQD50P06-class P-FET or VN5E-class driver ≥ 6 A) → the panel's backlight driver. ~2.5 A at 12 V.
- **These two rails never meet on this board.** Two inputs, two diodes (D-273).
- `+3V3` — **there is no regulator on this board.** It is the Teensy's own 3.3 V output, arriving at the
  socket behind a `PWR_FLAG`. This line used to read "`+3V3` LDO for the ESP32-C3, off `+5V`" and that
  disagreed with the CSV: D-273 put the radio on the XIAO module's own LDO because a BLE scan peaks near
  300 mA and the Teensy's regulator is a 250 mA part. The CSV wins, as the header says.
- `DP-ICU-A 3` **ground** — single pour, star-tied at this pin.
- `DP-ICU-A 2` **IC14 illumination** — divider to ADC; the dimming reference the display follows off the
  PWM-dimmed O20 bus.

## 2 · CAN

- `DP-ICU-A 4 / 5` → **TCAN1042HVDRQ1**, 3.3 V IO, to the Teensy's FlexCAN (CAN1). 500 kbps.
- **No termination on this board** (D-079). Common-mode choke footprint present, DNP, with the reason in
  its field.

## 3 · Analog in — one stage, drawn eight times

Every one ends: series/divider resistor → 100 nF → BAT54S to `+3V3` and GND. Draw all of them.

| Ch | Drop | Front end | Jumper |
|---|---|---|---|
| IC01 water temp | `DP-ICU-B 1` | 100 Ω 1 W pull-up from `+5V` → 15 k / 10 k (×0.4) | **J1, fitted** |
| IC02 oil pressure | `DP-ICU-B 2` | **no pull-up** — PMU-excited node, read only; 15 k / 10 k | — |
| IC03 fuel level | `DP-ICU-B 3` | 100 Ω 1 W pull-up from `+5V` → 15 k / 10 k | **J3, fitted** |
| IC05 charge lamp | `DP-ICU-B 5` | 47 k / 10 k → RC | — |
| IC06 brake warning | `DP-ICU-B 6` | 47 k / 10 k → RC (digital read) | — |
| IC07 oil temp | `DP-ICU-B 7` | footprint only — pull-up 1 k–2.2 k 1 % sized later, ×0.4 divider | **J7, not fitted** |
| IC09 turn LEFT | `DP-ICU-B 10` | 47 k / 10 k | — |
| IC10 turn RIGHT | `DP-ICU-B 11` | 47 k / 10 k | — |
| IC11 high beam | `DP-ICU-B 12` | 47 k / 10 k | — |

The jumpers are the reason this board outlives the 12A (D-262): open the jumper and the same ×0.4 divider
reads a 0–5 V transducer. Draw them as real jumpers, not as fitted links.

## 4 · Pulse in — the two that are not copies of anything

- **IC04 tachometer**, `DP-ICU-B 4`, shielded. Trailing coil negative primary — *hundreds of volts of
  inductive kick.* 2 × 100 kΩ ½ W series → 5.1 V zener + BAT54S to `+3V3` → **LM393 on the `+5V` rail**
  with ~0.5 V hysteresis and a 10 kΩ pull-up to `+3V3` → input-capture pin. 2 pulses/rev.
  The comparator is on 5 V deliberately (`CONVENTIONS.md §2.4`). H11L1 opto is the fallback if it picks
  up noise.
- **IC08 road speed**, `DP-ICU-B 8`, 12 V square wave from the transmission-boss Hall sensor (D-272).
  Jumper-selected: 4.7 kΩ pull-up to `+3V3` for open-collector, or 10 k / 4.7 k divider for push-pull;
  BAT54S; Schmitt → input capture.

## 5 · Display and local

- **IC21** — QSPI header to the BT817 EVE bridge board; backlight 12 V comes from IC13, not from here.
  The bridge → TFP410-class encoder → the 1920 × 720 panel's scaler is off-board (chain ii, D-269).
- **IC22 page button** — momentary to ground, 10 kΩ pull-up, 100 nF debounce.
- Teensy 4.1 on 0.1-inch female headers, 8 MB PSRAM on its pads, the IMU, the ESP32-C3 on its own `+3V3`.
  **Drawn as the socket, `J5`**, with the real Teensy 4.1 pad numbers from `icu_channels.teensy_pin`
  (D-377) and its VIN / 3V3 / GND pins (`CONVENTIONS.md §2.9`). The PSRAM is not on the sheet at all: it solders to the Teensy's underside
  pads, not to the carrier.

## 6 · Known open — do not draw a conclusion here

These are unresolved in the record. Drawing something plausible does not resolve them, and a schematic
that quietly picks an answer is worse than one with a question mark on it (R13):

- **`V-084`** — BT817 pixel clock and sync polarity against the actual panel. Not measured.
- **`Q-308`** — the oil-temperature sender, hence IC07's pull-up value. No part chosen.
- **IC01 / IC03 curves** — three-point reads on the senders *in the car*, still to be taken (D-261).
- **The tach front end** — LM393 vs H11L1 is a bench result, not a preference. The reference and
  hysteresis values now on the sheet (39 k / 12 k giving 1.18 V, and 1.2 M giving ~0.47 V against the
  200 k source) were **derived on the sheet** to meet the record's "~0.5 V", and are a proposal. They
  are not in `icu_channels.csv` and should not be copied into it until a bench says so.

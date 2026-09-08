<!-- out: 01-DESIGN/ICU-CARRIER.md -->
# ICU CARRIER — board H-001

*Rev 2026-09-07 · owns: the ICU carrier — every block between `DP-ICU-A` / `DP-ICU-B` and the Teensy 4.1. Front-end values are `data/sensors.csv`'s (D-310); part numbers are `V-082` until verified; the display connector waits on `V-085`.*

One board behind the cluster bezel. Teensy 4.1 socketed on standard 0.1-inch female headers (D-084), 8 MB PSRAM on its pads before install (D-170). The display ribbons straight to this board and never crosses the harness (D-159).

## 1 · Power entry — two inputs

```
DP-ICU-A 1 (O10, accessory) ── SS34 ── SMBJ33A ── LMR33630-class buck 5 V / 3 A ── Teensy VIN ── 3V3 (Teensy's own)
AUX 12 V (O15 block, this project) ── SS34 ── SMBJ33A ──┘   fitted only if Q-302 says the O10 tap is short — the display's backlight
```

The headless ICU of stage S1 draws Teensy + transceiver + IMU, ~0.5 A, on O10 alone. The panel arrives at S3 and its draw is measured then; the second input exists so that answer never forces a board spin. Bulk 100 µF + 10 µF at the buck, 470 µF on VIN. No keep-alive: stats persist to SD on key-off (F-007).

## 2 · CAN2

```
Teensy CTX / CRX ── TCAN1042-class transceiver (suffix V-057), 3.3 V IO, 5 V bus ── DP-ICU-A 4 / 5
```

**No termination on this board** — software termination at the PMU, 120 Ω at the engine-bay drop (electrical D-079). Common-mode choke footprint, DNP.

## 3 · Inputs — `DP-ICU-B`

Every observer input follows one pattern: 1 MΩ series → 330 kΩ to ground → 100 nF at the ADC → BAT54S clamp to 3V3 / GND, plus the DNP 100 Ω 1 W local-excitation pull-up behind a jumper (D-310). The two pulse inputs (tach, road speed) go to input-capture pins through a comparator or Schmitt stage. Values and calibration per channel:

{{sensors:module=ICU}}

**Grounding:** a single pour, star-tied at `DP-ICU-A 3`. Analog inputs enter on one board edge, CAN and power on the other; every RC lives at the connector edge, not at the Teensy pin. The tach shield lands at the dash node end only (electrical N48).

## 4 · Display, button, IMU, SD

- **Display chain (D-193):** Teensy QSPI → BT817 EVE → bridge → glass. Chain (i) SN75LVDS83B RGB→LVDS into 1280 × 480 cluster glass, backlight boost on this carrier, PWM-dimmed against the illumination reference on `DP-ICU-A 2`; chain (ii) TFP410-class RGB→HDMI into a 1920 × 720 panel's scaler board, which carries its own backlight driver. `V-085` picks; `V-084` sets the pixel clock and sync polarity; `T-051` proves it on the eval board first.
- **Page button (D-169):** panel-mount momentary to a digital pin, 10 kΩ pull-up, 100 nF.
- **IMU:** I²C + INT. **Mounting orientation must match the D-161 axes — `V-073` rules before layout.**
- **SD:** the Teensy 4.1's own socket; nothing on the carrier.

## 5 · Bring-up order

1. Power only — both 5 V paths, no Teensy fitted
2. Teensy in; CAN2 loopback against the bench SN65HVD230 node (D-085)
3. One observer input against a pot, then the tach front end against `tach_simulator/`
4. Display header last, after `V-085`

## 6 · What changed on 2026-09-07 and why

The old draft read every sender through a **pull-up divider** (1 kΩ to 3V3 on water temp, 330 Ω on oil pressure). That would have loaded the node the factory gauge drives and moved the needle — the inputs are taps, not senders (Q-301). The pinout also predated the harness data and the housing split: it is now `DP-ICU-B` 1 water · 2 oil · 3 fuel · 4 tach · 5 charge · 6 brake · 7 oil temp · 8 road speed · 9 spare, with power and bus on `DP-ICU-A` (electrical D-252). Fuel is a new input (electrical D-249 / D-251); the tach is the **trailing** coil's negative primary (D-304), an inductive-kick signal that needs the clamp ahead of the comparator.

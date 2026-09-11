<!-- out: 01-DESIGN/DCU-CARRIER.md -->
# DCU CARRIER — board H-002

*Rev 2026-09-07 · owns: the DCU carrier — power, CAN, servo drive, the blower's PWM command, comfort switching and the two temperature inputs between `DP-DCU`, the O15 block and the Teensy 4.1. Channel values are `data/sensors.csv`'s; part numbers are `V-083` until verified.*

Same power-entry and CAN sections as the electrical build's [`ICU-CARRIER.md`](../../electrical-build/01-DESIGN/ICU-CARRIER.md) §1 — one proven front end, two boards (D-085). Differences only below.

## 1 · Power — three rails

```
DP-DCU 1 (O10, accessory) ── SS34 ── SMBJ33A ── buck 5 V ── Teensy + logic
O15 block (this project, from L3-P 2) ─┬─ buck 5 V / 3 A ── SERVO RAIL (own regulator: a stalled cable never browns out the MCU; 470 µF at the header)
                                        └─ comfort loads → the seven low-side FETs
```

Logic on O10 like the ICU; climate memory restores from SD on wake, so there is no constant keep-alive (D-191). **`DP-DCU 2` is not a power tap** — it is the outside-air thermistor from `L2-S 5` (electrical D-256); the old draft had the O15 tap there and was wrong.

## 2 · Outputs and inputs

{{sensors:module=DCU}}

**Servos (SN15):** standard hobby pinout (GND / +5 servo rail / signal) on 3-pin locking headers, signal through 330 Ω. **Blower (SN14):** one logic-level PWM output at ≥ 20 kHz to the final stage plugged into `L3-BLW`, with a pull-down so the blower is off through a reset — there is no blower power stage on this board (D-308). **Comfort FETs (SN16):** AOD4184-class low-side, gate through 100 Ω with a 10 kΩ pull-down; SS34 flyback footprints, DNP; a 5 mΩ shunt + INA180 on the common return feeds `bus_current_ca`. **Mirror bridges (SN17):** three half-bridges per side, fitted only if `Q-305` puts adjustment on the DCU rather than a switch.

## 3 · Bring-up order

1. Power, all three rails, nothing fitted
2. CAN2 against the bench node; `0x300` / `0x310` visible
3. One servo on the bench — calibrate the endpoint store/restore loop
4. The blower PWM into a scope, then into the final stage with a headlamp bulb as the load
5. One FET channel into a bulb; verify off-at-reset
6. Panel `0x400` → mode / temperature / recirculate round trip

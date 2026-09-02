# DCU CARRIER — PCB schematic (H-002)

*Rev 2026-08-31 · owns: the DCU carrier board — power, CAN, servo drive and comfort switching between DP-DCU / the O15 tap and the Teensy 4.1. Candidate part numbers are collectively `V-083` until verified.*

Same power and CAN sections as [`ICU-CARRIER.md`](ICU-CARRIER.md) §1–§2 — one proven front
end, two boards (D-085: TCAN1042-class on both carriers, suffix `V-057`).
Differences only below.

## 1 · Power

Two feeds, kept apart:

```
DP-DCU 1 (ACCESSORY, O10) ── SS34 ── SMBJ33A ── BUCK 5 V/3 A ── Teensy + logic
DP-DCU 2 (COMFORT tap, O15) ─────────────────── comfort loads via the MOSFETs
```

- Logic lives on O10 like the ICU — no keep-alive; climate memory restores
  from SD on wake (F-001, settles `V-056` → D-191 — D-191).
- **Servo rail:** servos are the noisy load — their own 5 V buck (second
  LMR33630-class, `V-083`) so a stalled door cable never browns out the MCU.
  470 µF bulk at the servo header.

## 2 · Servo outputs — 3 channels (SRV_MODE, SRV_BLEND, SRV_RECIRC)

Standard hobby pinout (GND / +5 servo rail / signal), signal from Teensy PWM
through 330 Ω, 3-pin locking headers. Door cables per the hobby-servo concept —
mode, blend, recirc; travel calibrated at commissioning, endpoints stored
with the climate memory (`dcu/climate.h`).

## 3 · Comfort switching — 7 low-side channels

Low-side N-FETs (AOD4184-class, `V-083`) switching the F10/F11-protected
branches of the O15 bus: seat heat ×2, seat cool ×2, mirror heat, nozzles,
de-icer.

```
O15 branch (F10/F11) ── load ── FET drain
                                FET source ── GND
   gate ← Teensy pin via 100 Ω, 10 kΩ pull-DOWN (off at reset — matters)
```

- **Gate pull-downs are the safety feature:** every comfort load is off while
  the Teensy resets. The D-073 heat/cool interlock is enforced again in
  firmware — two layers.
- Flyback: comfort loads are resistive; fit SS34 footprints anyway, DNP.
- Current sense: one 5 mΩ shunt + INA180 (`V-083`) on the common return,
  feeding `bus_current_ca` on 0x310.

## 4 · Cabin temperature

10 kΩ NTC on a flying lead to a shaded dash location, divider to an ADC pin,
RC at the connector edge. `TEMP_INVALID` until it reads plausibly.

## 5 · Bring-up order

1. Power, both rails, nothing fitted
2. CAN2 against the bench node; 0x300/0x310 visible
3. One servo on the bench — calibrate the endpoint store/restore loop
4. One FET channel into a headlamp bulb as a dummy load; verify off-at-reset
5. Keypad 0x400 → mode/temp/recirc round trip

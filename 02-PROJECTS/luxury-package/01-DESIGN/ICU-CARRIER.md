# ICU CARRIER — PCB schematic (H-001)

*Rev 2026-08-30 · owns: the ICU carrier board — every net, block and part choice between DP-ICU and the Teensy 4.1. Candidate part numbers are collectively `V-082` until verified; the display connector waits on `Q-060` → D-193.*

One board behind the cluster bezel. Teensy 4.1 socketed (D-084), PSRAM
fitted before install (D-170). The display never crosses the harness — it
ribbons straight to this board (D-159).

## 1 · Power entry

```
DP-ICU 1 (ACCESSORY, O10) ──┬── F?? none (O10 soft fuse upstream)
                            │
                     D1  SS34 reverse block
                            │
                     TVS SMBJ33A ─── GND      (load dump clamp)
                            │
                  BUCK  LMR33630 class, 5 V / 3 A     ← V-082
                            │
                     Teensy VIN (5 V)  ──  3V3 from the Teensy's regulator
```

- Input is the accessory bus: the ICU lives and dies with O10 (D-078 — no
  keep-alive; stats persist to SD on shutdown, `V-075` shutdown delay).
- Buck, not LDO: 12 V → 5 V at the Teensy's ~0.5 A plus display backlight
  budget if the panel takes 5 V — revisit at `Q-060` → D-193.
- Bulk: 100 µF electrolytic + 10 µF ceramic at the buck; 470 µF on VIN.

## 2 · CAN (CAN2 vehicle bus)

```
Teensy CTX/CRX ── TCAN1042-class transceiver (exact suffix V-057) ── DP-ICU 3/4
```

- 3.3 V-IO variant, 5 V supply. **No termination on this board** — the bus is
  terminated at the PMU (software) and the L1 drop (D-079).
- Common-mode choke footprint, DNP by default.

## 3 · Conditioned inputs — six channels (F-003)

All follow one pattern: series R → divider → RC low-pass → BAT54S clamp to
3V3/GND → Teensy ADC (or digital pin where noted). Values provisional until
each sender is confirmed; the sender list is SPEC §10 / D-083.

| # | Signal | From | Topology | Values (provisional) |
|---|---|---|---|---|
| 1 | Tach (coil −, D-082) | DP-ICU 6 | **F-004 circuit**: 10 kΩ series → optocoupler (H11L1) or LM393 comparator with 100 V zener front end → digital pin | pulses/rev `V-067` |
| 2 | Water temp | DP-ICU 7 | 1 kΩ pull-up to 3V3 against the factory NTC, RC 1 kΩ/100 nF | curve at commissioning |
| 3 | Oil temp | DP-ICU 8 | same as water | sender TBD |
| 4 | Oil pressure | DP-ICU 9 | sender resistive → 330 Ω pull-up divider, RC | range at commissioning |
| 5 | VSS | DP-ICU 10 | comparator squarer like tach, digital pin | pulses/km at commissioning |
| 6 | Alternator sense | DP-ICU 11 | 47 kΩ / 10 kΩ divider (20 V → 3.5 V), RC | direct ADC |

Brake fluid level (DP-ICU 12, A-010): switch to ground — 10 kΩ pull-up to
3V3, RC, digital read. Seventh input, no conditioning beyond the clamp.

## 4 · Display, button, IMU, SD

- **Display chain (Q-060 → D-193):** Teensy **QSPI** → BT817 EVE board →
  bridge → 12.3″ bar glass. Bridge per `V-085`: SN75LVDS83B RGB→LVDS
  serializer (chain i — 330-nit cluster glass under the brow) or
  TFP410-class RGB→HDMI encoder into the panel's stock scaler board
  (chain ii — 900–1000-nit 1920 × 720 glass, canvas scaled 1.5×).
  Backlight: bar panels need their own LED boost driver — chain (ii)'s
  scaler board carries one; chain (i) puts it on this carrier, PWM-dimmed
  and O20-tracked. Timing check is `V-084`.
- **Page button** (D-169): panel-mount momentary beside the display, to a
  digital pin with 10 kΩ pull-up and 100 nF debounce.
- **IMU:** I²C (SDA/SCL + INT). **Mounting orientation must match the D-161
  axis convention — `V-073` rules before layout.**
- **SD:** the Teensy 4.1's own socket; nothing on the carrier.

## 5 · Grounding and EMC

Single ground pour, star-tied at DP-ICU 2. Analog inputs enter on one board
edge, CAN and power on the other. Every conditioned input's RC lives at the
connector edge, not at the Teensy pin.

## 6 · Bring-up order

1. Power only — 5 V rail, no Teensy fitted
2. Teensy in, CAN2 loopback against the bench SN65HVD230 node (D-085)
3. One conditioned input against a pot; then the tach front end against
   `tach_simulator/`
4. Display header last, after `Q-060` → D-193

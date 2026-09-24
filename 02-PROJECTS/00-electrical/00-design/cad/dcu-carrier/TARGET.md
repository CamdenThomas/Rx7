# What has to be on the sheet

*Rev 2026-09-22 (b, after the parts check D-379) · owns: the drawing checklist for the DCU carrier.*

> **This is a snapshot taken 2026-09-22, not a link.** The live record is
> `../../../data/dcu_channels.csv` —
> `python tools/rx7.py sql 02-PROJECTS/00-electrical "select * from dcu_channels"`. If the CSV and
> this file disagree, the CSV is right and this file is stale. Nothing in the record cites it.

Draw in this order. Each block is finished when it passes ERC on its own.

## 1 · Power: the block where a mistake is expensive

- `DP-DCU 1` **logic 12 V, constant** (SN24): F22, 3 A inline at the dash node. SS34 → SMBJ33A →
  LMR36015-Q1-class 60 V buck → `+5V` → Teensy VIN. Constant, not accessory: the DCU has to see a
  panel press with the key out (D-355).
- **Servo rail and comfort supply** (SN27): in on the comfort receptacle (`P153`) from the luxury
  package's O15 block. A **TPS54560B-Q1** 5 A buck (with a 60 V 5 A Schottky) for the servo rail,
  470 µF at each servo header; the firmware moves one servo at a time (D-379). The mirror-heat
  high-side switch is fed from here too. The connector's pinout and its own ground pins are block
  `00.28`.
- **These two supplies never meet on this board**, as the ICU's two don't (D-273).
- `+3V3`: the Teensy's own output. No regulator on this board.
- `DP-DCU 3` **ground** (SN25): single pour, star-tied at this pin. The comfort returns come back
  through the 5 mΩ shunt (SN13) on their own receptacle, never through the logic ground.

## 2 · CAN

- `DP-DCU 4 / 5` (SN26) → TCAN1042-class transceiver (`P145`), **unterminated**: the bus ends at
  the PMU and the dash node (D-346). Sends `0x300`, `0x310`, `0x320`, `0x400`.

## 3 · Inputs

- **SN11** cabin NTC: 10 kΩ pull-up to 3V3, RC 10 kΩ / 100 nF at the connector edge → ADC.
- **SN12** outside-air NTC on `DP-DCU 2`: the same, plus a BAT54S (cathode to +3V3, anode to
  ground — the ICU sheet's first pass had these backwards).
- **SN13** comfort-bus current: **INA180A1** (gain 20) across two 10 mΩ 2512 ≥ 2 W in parallel → ADC.
- **Panel ribbon** (count at `H-007`): **SN19** key-matrix rows and columns on GPIO · **SN20**
  encoder A / B on GPIO · **SN18** thumbstick, two ADC axes and one digital press.

## 4 · Outputs

- **SN14** blower PWM to the final stage: ≥ 20 kHz, 100 Ω series, 10 kΩ pull-down (off through a
  reset). The pin's timer must hold 20 kHz independently of the servos' 50 Hz.
- **SN15** servo PWM ×3 (mode, blend, recirculate): 330 Ω series, on the servo rail.
- **SN16** comfort switching: **BTS3011TE** protected low-side switches ×4 (seat heat ×2, seat
  cool ×2), driven straight from 3.3 V: the AOD4184 could not be (D-379) · **BTT6050-1ERA**
  high-side for mirror heat, out on `DP-DCU-B 9` (D-369).
- **SN17** mirror drive: one **DRV8962-Q1** — three half-bridges (motor common, left, right) on
  `DP-DCU-B 5–7`, the fourth channel's low FET sinking both clutch coils on `DP-DCU-B 8` (D-360,
  D-379). Stall current from luxury `W-332`.
- **SN22** window commands: one **BTT6200-4ESA** quad high-side sourcing 12 V into K5–K8's coils, on
  `DP-DCU-B 1–4` (D-363). Up and down on one side are interlocked in firmware.
- **SN23** release selects: two **PMV37ENEA** sinking K3 / K4's coils, on `DP-DCU-B 10 / 11`
  (D-370).
- **SN21** wake request on `DP-DCU 6` into the PMU's wake strip. The drive level is `confirm`
  against the strip's input.

## 5 · Connectors and mechanics

- `DP-DCU`: DT13-06PA and `DP-DCU-B`: DT13-12PA (`P150`), flanged through one enclosure wall
  (luxury D-362). `DP-DCU-B 12` is a sealing plug.
- The comfort receptacle (`P153`): a DT13 if every circuit fits a size-16 contact, a DTP-class part
  if not. Waits on `V-101`.
- Grommets, not connectors: the panel ribbon, the cabin sensor, the blower final stage's lead,
  the three servo leads.
- Teensy 4.1 socketed on standard female headers (`P148`), never machined-pin.

## 6 · What this sheet will not know

Every load current (`V-101`, luxury `W-332`), the panel's ribbon (`H-007`), every part number
(`V-083`), the Teensy pinout (layout), and the space it fits in (`V-102`). None of these is a
drawing problem: each is a row that lands first.

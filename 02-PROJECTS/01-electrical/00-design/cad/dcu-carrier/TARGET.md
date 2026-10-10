# What has to be on the sheet

*Rev 2026-10-09 (d, Y11 provisions - D-455) · owns: the drawing checklist for the DCU carrier.*

> **Drawn 2026-09-28.** Every item below is on `dcu-carrier.kicad_sch`, ERC clean. Where D-452 went
> further than this list: a TCA9539-Q1 expander for the slow lines (§4 SN17, SN22 DEN/DSEL, CAN STB),
> the windows and mirrors fed from logic 12 V, a B560C + SMBJ33A on the comfort input, and two 0 Ω
> links in place of the DNP choke (§2).

> **Y11, 2026-10-09: the open blocks' worst case is drawn in (§7).** A second expander U13, the A/C
> clutch stage and pressure input of engine 02.15 (b), the radar alert input of luxury 03.12, and
> DP-DCU-C 8 on PGND for 01.26 (a) - all DNP but U13, on the sheet and the board.

> **This is a snapshot taken 2026-09-22, not a link.** The live record is
> `../../../data/dcu_channels.csv` —
> `python tools/rx7.py sql 02-PROJECTS/01-electrical "select * from dcu_channels"`. If the CSV and
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
- The comfort receptacle (`P153`): **DT13-08PA** (D-382): every circuit fits a size-16 contact, its own two ground pins on 6 / 7
  and pin 8 a sealing plug; the current figures stay `confirm` (V-101).
- Grommets, not connectors: the panel ribbon, the cabin sensor, the blower final stage's lead,
  the three servo leads.
- Teensy 4.1 socketed on standard female headers (`P148`), never machined-pin.

## 6 · What this sheet will not know

Every load current (`V-101`, luxury `W-332`), the panel's ribbon (`H-007`), every part number
(`V-083`), the Teensy pinout (layout), and the space it fits in (`V-102`). None of these is a
drawing problem: each is a row that lands first.

## 7 · Provisions for the open blocks (Y11, D-455: assume the worst case, fit on the answer)

- **U13**, a second **TCA9539-Q1** at **0x75** (A0 high, A1 low), fitted, on U12's I²C bus, INT wired-OR
  on EXP_INT (R53) and RESET shared (R54): P00 the four BTS3011TE STATUS lines (`SEAT_STATUS`, R58,
  moved from U12 P17), P01 the radar alert; P02-P17 spare.
- **A/C clutch** (02.15 (b), DNP): U12 **P17** → R59 4.7 k (R60 10 k off at reset) → **U14 BTT6050-1ERA**
  high side, VS on `V12C_RAW` (the comfort input ahead of D3), out on **DP-DCU-B 12** (`AC_CLUTCH`, the
  one cavity free on the three DCU receptacles). The coil returns at the compressor and carries its own
  diode. DEN held low (R61) and IS on R62 1.2 k, unread - as U9 / U10. F29 (7.5 A) is too small with the
  clutch added - confirm, V-101.
- **A/C pressure** (02.15 (b), DNP): **J11** a 3-way PLACEHOLDER lead (no drop cavity is free), 0.5-4.5 V
  ratiometric `confirm`, 10 k / 20 k + 100 nF + BAT54S → **U15 ADS1115-Q1** (0x48, VSSOP-10) AIN0; the
  supply the same way on AIN2 (AIN1 / AIN3 grounded, spare); **U16 TPS7B4250-Q1** makes `SENS_5V` from
  logic 12 V, tracking `+5V`.
- **Radar alert** (03.12 / Z-002, DNP): **J12** a 2-way PLACEHOLDER lead, 47 k / 22 k + 100 nF + BAT54S →
  U13 P01; R68 10 k to logic 12 V only for an open-collector output (`confirm`).
- **DP-DCU-C 8** on `PGND`: 01.26 (a)'s third comfort ground; the record keeps it a plug until it answers.

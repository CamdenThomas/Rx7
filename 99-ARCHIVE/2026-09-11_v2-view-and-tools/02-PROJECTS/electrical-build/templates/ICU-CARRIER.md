<!-- out: 01-DESIGN/ICU-CARRIER.md -->
# ICU CARRIER — board H-001

*Rev 2026-09-08 · owns: the ICU and its display — the instruments of this build. Every channel between `DP-ICU-A` / `DP-ICU-B`, the Teensy 4.1, the display and the radio is a row in `data/icu_channels.csv`; the part numbers are checked against their datasheets (D-273). The pages the display draws are the luxury package's firmware; the bezel around it is the luxury package's dash plastics.*

## What it is

One board behind the binnacle and a 12.3-inch bar in front of it. A Teensy 4.1 socketed on standard 0.1-inch female headers, 8 MB PSRAM on its pads, a TCAN1042 on CAN2, two 12 V inputs, an analog front end for eight sensor lines, three tell-tale senses, a BT817 display bridge on a ribbon, an ESP32-C3 radio for the battery data, and nothing else. The car's instruments are the ICU's from the first drive on the new harness (D-268): it excites the fuel and water-temp senders, reads the PMU-excited oil node, the tach, the charge and brake lines and the three tell-tales, and draws all of it. The factory cluster stays on the factory harness until the meters cutover (MG22) and leaves with it — nothing in the new harness was ever built for it.

## Contents

1. Power and bus · 2. Inputs · 3. The display · 4. On the board — IMU and radio · 5. Grounding and EMC · 6. Bring-up · 7. What changed and why

## 1 · Power and bus

{{table:icu_channels|kind=power|-kind}}

{{table:icu_channels|kind=bus|-kind}}

Two 12 V inputs, never joined on the board: logic on the accessory tap (`DP-ICU-A 1`), the display's backlight on the F16 ignition aux (`DP-ICU-A 6`) through a fuse and a high-side switch the Teensy controls. Each through its own SS34 and SMBJ33A (D-088). The logic buck is an LMR36015-Q1-class 5 V / 3 A; the three sender excitations (100 Ω from 5 V, ≤ 50 mA each at a shorted sender) and the radio co-processor (≤ 120 mA in a scan) hang off it. No CAN termination on this board (D-079).

## 2 · Inputs

{{table:icu_channels|kind=input|-kind}}

Every analog input ends in the same three parts at the connector edge — series or divider resistor, 100 nF, BAT54S to 3V3 and ground — because the Teensy is 3.3 V only and not 5 V tolerant. The two pulse inputs go to input-capture pins through a comparator or Schmitt stage. **Built to outlive the 12A (D-262):** each sender's pull-up sits behind a jumper (J1, J3, J7 — fitted for the car's own resistive senders, D-261), the ×0.4 divider reads a 0–5 V transducer just as well with the jumper open, and every curve is a config file — at the engine swap the channels change by file and jumper, never by board, and most of them go quiet in favour of the ECU's CAN frames (luxury F-014).

## 3 · The display

{{table:icu_channels|kind=display|-kind}}

The 12.3-inch bar is this build's instrument from the meters cutover (D-268). The chain is proved on the desk in order — the BT817 evaluation board first (`T-051`, the one order that should not wait), then the glass (chain ii — the 900–1000-nit 1920 × 720 panel through its scaler, D-269), then the timings (`V-084`, agent work at install §1.22) — and the DRIVE page runs on the bench before the car is touched. It mounts on a plain plate in the binnacle aperture, sized at M-6, which stays as the sub-frame the luxury package's moulded bezel later surrounds (D-269). The odometer starts from the factory cluster's reading at cutover and persists in the Teensy's EEPROM with the microSD as the log (D-269, luxury F-007 — a cutover gate). Road speed comes from the transmission-boss pulse generator (D-272) from the same day, because the mechanical speedometer leaves with the cluster.

## 4 · On the board — IMU and radio

{{table:icu_channels|kind=sensor|-kind}}

{{table:icu_channels|kind=radio|-kind}}

The radio is the one addition the battery data asked for (D-267): an ESP32-C3 module on the 3V3 rail talking to the Teensy over a UART, decoding the Ionic's BMS and / or a shunt at the battery (`Q-128` picks the source) — the Teensy has no radio, and keeping the Bluetooth stack on its own chip keeps its timing and its power off the instrument core. The IMU serves the luxury package's performance page; it goes on now so the board never comes out for it (`V-073` → D-265).

## 5 · Grounding and EMC

Single pour, star-tied at `DP-ICU-A 3`. Analog inputs enter on one edge; CAN, power, the display header and the radio leave on the other (D-265); every RC lives at the connector edge. The tach shield lands at the dash node end only (node conductor N48). The display header's QSPI lines stay short and away from the tach input. The ESP32-C3's antenna end overhangs the board edge with a 5 mm keep-out and faces an RF-transparent enclosure wall — the printed ASA / PETG enclosure of D-270, no external antenna needed; the module sits at the CAN / display edge, as far from the tach comparator as the board allows.

## 6 · Bring-up

The bench sequence is the install plan's, not this document's: [`../03-INSTALL/INSTALL.md`](../03-INSTALL/INSTALL.md) §1.21–1.23 — power with nothing fitted, then the Teensy and CAN, then each input against a resistor or the tach simulator, then the display chain (eval board, glass, timings) with the DRIVE page live and the odometer persisting across a power cycle. Only then the car.

## 7 · What changed and why

Until 2026-09-07 this board was the luxury package's, read the senders as a high-impedance observer of nodes the factory gauges drove, and shared those nodes with a cluster drop (`DP-CLU`). Camden ruled the ICU a wiring-project device (Q-122 → D-259) and the cluster temporary and traceless (Q-121 → D-258): the senders came to the ICU and the drop went. The same evening he asked whether the display should simply come now, with only the dash plastics left to the luxury package (Q-129 → D-268) — and it should, because the parallel-system migration already keeps the factory cluster alive on the factory harness until its own cutover, so the temporary cluster, its twelve-line tail and the three gauge-drive stages that D-258 had put on this board were never needed. The oil node stays PMU-excited so the fuel-pump gate never depends on this board (D-260).

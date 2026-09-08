<!-- out: 03-INSTALL/INSTALL.md -->
# INSTALL — the stages, in order

*Rev 2026-09-07 · owns: the order the luxury package goes into the car and what each stage needs, consumes and delivers. Rendered from `data/stages.csv`, `data/features.csv`, `data/provisions.csv` and `data/parts.csv`. The firmware record is [`BRING-UP.md`](BRING-UP.md)'s.*

**Three rules govern the order.** Modules join a finished car — the electrical build's shakedown comes first (D-081). Each dash-plastics event is done once: the centre stack opens for the panel and DCU, the binnacle for the display, the door cards for mirrors and windows together, the carpet for seats and sound deadening. And the car must drive home at the end of every session — every stage below plugs into a capped receptacle and can be unplugged again.

## 0 · The stages

{{stages}}

The recommended order is the table's order: climate (`S2`) before the display's bezel (`S3`), because the car has no heater airflow until the blower returns (electrical D-253) and the display is already in the car on its plate (electrical D-268). `Q-306` is the owner's call on that order.

## 1 · S0 — bench and boards

{{stage_detail:S0}}

{{provisions:stage=S0}}

Everything here happens on a desk with the PMU simulator standing in for the car ([`BRING-UP.md`](BRING-UP.md)). Lay out the DCU carrier to [`../01-DESIGN/DCU-CARRIER.md`](../01-DESIGN/DCU-CARRIER.md) once `V-083` and `Q-305` are closed (the ICU carrier is the electrical build's — its `ICU-CARRIER.md` and install §1.20–1.24, D-259); order the BT817 eval board (`T-051`) first of anything; land `F-012` on a machine with g++ so the header matches the map before a board is flashed.

## 2 · S1 — the ICU, already in the car

{{stage_detail:S1}}

Nothing to do here. The ICU and its display were designed, built, commissioned on the bench and installed with the harness by the electrical build (its install §1.20–1.24, §5 and the meters cutover MG22 — electrical D-259, D-268); the ICU excites and reads every sender, draws them on the 12.3-inch display on its binnacle plate, and publishes `0x200` / `0x210` / `0x218` on CAN2. The oil-temperature sender and the road-speed sensor are that project's too (electrical `Q-308`, `Q-309`). This project meets a running node — the stage stays in the table so the numbering and the dependency read right.

## 3 · S2 — climate: panel, DCU, blower

{{stage_detail:S2}}

{{provisions:stage=S2}}

1. Centre stack apart — the one time. The factory heater control head and its cables' levers come out; the servos take the cables.
2. Build the O15 block behind the centre stack and plug it into `L3-CMF` (`L3-P 2`, electrical D-274); the DCU's servo rail and comfort branches hang off it.
3. Plug the DCU into `DP-DCU`, the panel into `DP-KEY`, the new blower into `L3-BLW` **through the final stage**; the DCU's PWM pigtail to the module.
4. In the PMU client: enable O16 (steady feed, limit from the motor's sheet per D-126) and O4 with the CAN trigger from the panel key.
5. Calibrate servo endpoints; check the blower is silent at part speed (that is what the ≥ 20 kHz stage is for); confirm every comfort FET is off through a DCU reset.
6. Fit K3 / K4 and their fuses for the existing hatch and fuel-door solenoids (`T-032`, `T-033`; the conductors already reach them — electrical D-274) and map the panel keys to the PMU's O10 branches (D-180).

## 4 · S3 — the display bezel

{{stage_detail:S3}}

1. The display has been the car's instrument since the electrical build's meters cutover (D-268), on its plain plate.
2. Binnacle apart — the one time: measure the plate and the aperture; electrical `Q-130` says whether the plate stays as the sub-frame.
3. Foam plug shaped in place over the plate, fibreglass skin, filler, primer, finish (H-006); the page button's place kept.
4. Refit. Nothing electrical changes — the ribbon and the button are as they were (D-159).
5. Noon-sun and night legibility with the brow in its final shape; instant-on check with a stopwatch.

## 5 · S4 — comfort loads

{{stage_detail:S4}}

{{provisions:stage=S4}}

Carpet up for sound deadening; run the seat elements and fans to the O15 block under the console; nozzles only if `Q-303` found one that fits, onto `L2-S 6` at the cowl.

## 6 · S5 and S6 — mirrors and windows, door cards off once

{{stage_detail:S5}}

{{provisions:stage=S5}}

{{stage_detail:S6}}

{{provisions:stage=S6}}

Mirrors: uncap `D1 / D2 4–7` in the doors, land the motors and heater, splice `L4-S2 1–5` onto `D1 / D2 4–6` at the sill node, fit F14 and its holder on `L4-P 4`. Windows: regulators and motors to `D1 / D2 1–2`, populate K5–K8 and F8 / F9 at the sill, uncap `L3-S2 3–6` at the console switches, enable the window logic in the PMU.

## 7 · S7 — lighting, the second pass

{{stage_detail:S7}}

Only after the electrical shakedown on stock bulbs (L-004). Tail lights, headlamp units, LED bulbs — and then **every lamp channel's soft fuse is re-set from measurement** (D-122); a limit set for a filament does not protect an LED.

## 8 · S8 — radar

{{stage_detail:S8}}

{{provisions:stage=S8}}

Design first (`V-061`, Z-002). The pass-through and the module drop exist; nothing is uncapped until the subsystem does.

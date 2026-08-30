# STATUS — where the project is

*Rev 2026-08-30 · owns: current state, one dashboard — refreshed at the end of every session. If you read one file after a long gap, read this one. Money figures are [`06-PROCUREMENT/BOM.md`](06-PROCUREMENT/BOM.md)'s; the phase estimates are [`05-BUILD/CHECKLIST.md`](05-BUILD/CHECKLIST.md)'s.*

## Contents

1. In one paragraph · 2. Scope boundary · 3. In hand · 4. Phase state ·
5. Firmware · 6. Blockers and what to do now · 7. Money · 8. Open decisions ·
9. Recently settled · 10. Effort and the critical path · 11. If you have been
away a year

---

## 1 · In one paragraph

The 1982 RX-7's electrical system is being replaced with an ECUMaster PMU-24
DL, a rear-mounted Ionic S9 lithium battery, four modular harness legs plus a
sill node, and two Teensy 4.1 CAN modules — a climate DCU and an instrument
cluster ICU. **The car runs on its stock incandescent bulbs throughout**; LED
conversion and custom lamps are [`../lighting-body/`](../lighting-body/README.md).
The PMU, battery, three Teensys, five bench transceivers and the clamp meter
are in hand; two spare housings are inbound. **Firmware Stages 1–5 are
complete**, the renderer and a 415-assertion test suite exist, and the first
three meter readings are recorded. Nothing has been cut, crimped or installed
on the car. Five design packets (`Q-061`–`Q-065`) are waiting on Camden
before the connector order can be placed.

## 2 · Scope boundary

| This project | `lighting-body/` |
|---|---|
| Channels, gauge, connectors, soft fuses, flash logic | LED bulbs, custom tail lights, headlamp units |
| Working lamps on **stock bulbs** (D-119) | Any change to what's *in* the socket |
| Inrush config for filament (D-120) | Second-pass fuse reset after the bulb change (D-122) |

## 3 · In hand

PMU-24 DL with connector, 39 terminals and the USB-to-CAN adapter · Ionic S9 ·
3 × Teensy 4.1 with pins · 5 × SN65HVD230 (bench only) · UT210E clamp meter ·
1 micro-USB cable · **2 spare Sicma housings inbound** (`T-045` on arrival).

**Connector confirmed:** 16 large / 27 small terminals supplied, **zero small
spares** (D-135 → `T-044`). Pin 1 top-left, opposite the purple lock (D-139).
Not bought yet: resistors, breadboards, jumpers — [`05-BUILD/BENCH-KIT.md`](05-BUILD/BENCH-KIT.md).

## 4 · Phase state

| Phase | Hrs | State |
|---|---|---|
| 0 · Documentation & measurement | 55–85 | **Started.** Paperwork done; **3 of 22 outputs measured**; tape-measure session not started; 0.23 ruling pending |
| 1 · Order & practice | 10–16 | Wire order held on `T-008` and 0.23 |
| 2A · PMU configuration | 12–20 | **Unblocked, fully specified** in [`PMU-CONFIG.md`](01-DESIGN/PMU-CONFIG.md). Needs 120 Ω × 4 and a 5 A fuse |
| **2B · Firmware** | 155–325 | **Stages 1–5 complete**, ~90–125 hrs done. Display driver waits on `Q-060`; DCU not started |
| 3 · Power backbone | 18–28 | Parts not ordered. Winter break |
| 4 · Panel build | 49–74 | Blocked on `Q-014` / `T-007` |
| 5 · Harness legs | 98–162 | Blocked on `T-008` |
| 6–8 · Install, migrate, shakedown | 118–199 | Summer 2027 |
| 9 · Modules | — | Late 2027 → 2028 |

## 5 · Firmware

| Stage | State |
|---|---|
| 1 · Toolchain, blink | ✅ Board 1. Boards 2 and 3 still to flash and label (`T-048`) |
| 2 · `can_map.h` validation | ✅ Found and fixed a real bug in the temperature macros |
| 3 · CAN loopback, 500 kbps | ✅ 5 frames, byte-identical payloads, dispatch and timeout |
| 4 · Ladder decode | ✅ Absorbed into `icu.ino` |
| 5 · Tach measurement | ✅ Absorbed; `tach_simulator/` kept as the RPM source |
| 6 · SD config | Needs a microSD card — `F-010` |
| 7 · Datalogging | After 6 |

Version `ICU_FW_VERSION 0.3.0-dev`. Library **ACAN_T4**, not FlexCAN_T4.
The desktop simulator runs the real renderer; `tests/run.bat` must be green
before any flash.

## 6 · Blockers and what to do now

| # | Blocker | Unblocks | Needs |
|---|---|---|---|
| 1 | **T-014** finish the meter session | Every soft fuse. **Irreversible window** | The meter, in hand — ~8 hrs left |
| 2 | **T-007** dash envelope | Panel drawing, panel parts, Phase 4 | A tape measure |
| 3 | **T-008** harness routes | Cut list lengths, the wire order, Phase 5 | String |
| 4 | **Checklist 0.23** — rule on `Q-061`–`Q-065` | Four functions with no pin; the connector order | Reading [`OPEN.md`](07-PROCESS/OPEN.md) §1 and answering five packets |

**Needs nothing in the post:** the three above · `T-028` sill space · `T-018`
photographs · `T-019` find the PO splices · `T-029` look at the battery posts
· `T-049` write down the VIN · install the PMU client and read the `V-065`
CAN export · `T-048` flash boards 2 and 3.

**Agent work available now** ([`07-PROCESS/FORWARD-WORK.md`](07-PROCESS/FORWARD-WORK.md)):
`F-001` DCU skeleton · `H-001`/`H-002` carrier PCB schematics · `F-003`/`F-004`
conditioning · `X-002` panel schematic sheet.

## 7 · Money

From [`06-PROCUREMENT/BOM.md`](06-PROCUREMENT/BOM.md) §1:

| | |
|---|---|
| Committed | ~$2,950–3,350 |
| Remaining | ~$3,450–6,200 |
| Project total | ~$6,400–9,550 |
| **Buy next** | Bench kit remainder ~$100–150, spare 1.5 mm terminals |
| Then | Battery mount, Class-T, 2 AWG — ~$540–880, before Phase 3 |
| **Hold** | Wire and connector order until `T-008` and 0.23 |

## 8 · Open decisions

| ID | Question | State |
|---|---|---|
| **Q-061** | F13 and where the solenoids get an output | packet ready |
| **Q-062** | Conductors from the dash to the sill | packet ready |
| **Q-063** | Inhibitor, wiper park, horn input, washer output — no PMU pin | packet ready |
| **Q-064** | RPM-dependent PMU logic before the ICU exists | packet ready |
| **Q-065** | Dimmer and passing on A15 | packet ready |
| **Q-060** | Display panel — the next hardware decision | needs a panel search |
| **Q-014** | Dash envelope — a measurement, not a decision | `T-007` |
| Q-028 | CAN wake latency | not live |
| Q-001 | VIN | `T-049` |

Flagged verifies: `V-065` PMU CAN export (Checklist 2.5) · `V-067` tach pulses
per rev · `V-069` crimper die size · `V-074` O8 braking vs park input ·
`V-075` native shutdown delay. The full list is
[`07-PROCESS/OPEN.md`](07-PROCESS/OPEN.md).

## 9 · Recently settled

D-168 **SPI dirty-rectangle rendering** is the display interface (supersedes
D-150's controller recommendation) · D-169 page button by the display ·
D-170 fit PSRAM · D-171/D-172 L1-S and L3-S allocations as generated · D-148
start relay on the inner fender · D-144/145 no bench PSU, a 5 A fuse instead ·
D-141 bench mule dropped · D-140 what was actually bought · D-135 terminal
count · D-131 the windows are manual.

**Housekeeping this session:** Audit 4 — 95 findings, 85 closed
([`07-PROCESS/AUDITS.md`](07-PROCESS/AUDITS.md)). The pin data now lives in
three CSVs and everything downstream is generated; `check.py` is clean.

## 10 · Effort and the critical path

**Roughly 90–125 hours of 531–932 complete — about 12–18 %.** Almost all of
it is Phase 2B firmware, which was scheduled to run through late 2027 and is
now well ahead.

| | Hours | Done |
|---|---|---|
| Laptop work — 2A, 2B, paperwork | 180–365 | ~90–125 |
| Physical work — measure, order, build, migrate | 333–544 | 0 |

The rate is about to drop: remaining laptop work is the DCU, carrier PCBs,
conditioning schematics, the panel sheet — 60–120 hours. After that everything
needs measurements, parts, or the car. **The critical path was never
firmware:**

```
measure  →  rule on 0.23  →  order wire  →  build panel  →  build legs  →  migrate  →  shake down
```

Two tape-measure tasks and one ruling gate 147–236 hours of downstream work
and take perhaps two hours in daylight plus an evening's reading. July 2027 is
still real, limited by weekends with the car, not by code.

**Rule that governs the build:** the car drives home at the end of every
session. Never start a cutover you can't finish or reverse before dark.

## 11 · If you have been away a year

[`STATUS.md`](STATUS.md) → [`README.md`](README.md) →
[`01-DESIGN/GLOSSARY.md`](01-DESIGN/GLOSSARY.md) →
[`01-DESIGN/SPEC.md`](01-DESIGN/SPEC.md) →
[`02-HARNESS/CAVITY-STATE.md`](02-HARNESS/CAVITY-STATE.md) →
[`05-BUILD/CHECKLIST.md`](05-BUILD/CHECKLIST.md) →
[`07-PROCESS/OPEN.md`](07-PROCESS/OPEN.md). About an hour. Then
[`02-HARNESS/diagrams/architecture.svg`](02-HARNESS/diagrams/architecture.svg)
for the picture.

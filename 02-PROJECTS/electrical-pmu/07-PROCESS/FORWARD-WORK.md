# FORWARD WORK — what becomes possible next

*Rev 2026-08-30 · owns: the agent-side backlog — firmware (F), hardware design (H), documentation (X) and further-ahead thinking (Z). Camden's physical tasks are [`TASKS-CAMDEN.md`](TASKS-CAMDEN.md)'s; the build sequence is [`../05-BUILD/CHECKLIST.md`](../05-BUILD/CHECKLIST.md)'s.*

Ordered by what unblocks the most. **AGENT** items can be done now on a
laptop; **BLOCKED** items name their gate. Tick and date here when done; the
result goes in [`CHANGELOG.md`](CHANGELOG.md).

## Contents

1. Firmware · 2. Hardware design · 3. Documentation · 4. Further ahead ·
5. Where progress genuinely stops

---

## 1 · Firmware — the largest available block

- [ ] **F-001 AGENT · DCU firmware skeleton.** `dcu.ino` + `climate.h` mirroring
      the ICU structure: CAN node, state struct, servo outputs, comfort
      switching, heat/cool interlock (D-073). Nothing blocks this — the CAN map
      is final and the pattern is proven. Settles `V-056` as a side effect
- [x] **F-002 AGENT · PMU simulator on the spare Teensy.** `firmware/pmu_sim/`
      transmits 0x100–0x130 with a vehicle model; `channels.h` is generated
      from the CSV. *Done 2026-08*
- [ ] **F-003 AGENT · Sensor conditioning schematic.** Dividers, RC filters and
      clamp diodes for all six ICU inputs, values computed from the sender
      ranges. Blocked only on `V-037` for one of the six
- [ ] **F-004 AGENT · Tach conditioning circuit.** Opto or comparator, with part
      numbers. Coil primary spikes well above 12 V (D-082); pulses per rev is
      `V-067`
- [ ] **F-005 AGENT · Cluster page framework.** Page enum, the D-169 button
      handling, per-page draw and invalidate. Makes the diagnostics and trip
      pages additive rather than a rewrite (`../03-MODULES/CLUSTER-DESIGN.md`)
- [ ] **F-006 AGENT · Diagnostics page.** 24 channels, live current, soft-fuse
      setpoint, state — the thing nothing else can do. Needs F-005
- [ ] **F-007 AGENT · SD persistence for `stats.h`.** Write on key-off via the
      shutdown delay (`V-075`). Needs a decision on write frequency (D-162)
- [ ] **F-008 BLOCKED on Q-060** · Display driver — `pushDirtyTiles()` in
      `icu.ino` is three TODO calls away from complete
- [ ] **F-009 BLOCKED on V-065** · Reconcile `can_map.h` 0x100–0x130 against the
      PMU's actual export (Checklist 2.5)
- [ ] **F-010 AGENT · Config-as-data.** Thresholds, colours and units on the SD
      card with a safe-mode render path if the file is missing or corrupt
      (BENCH-BRINGUP Stage 6)

## 2 · Hardware design

- [ ] **H-001 AGENT · ICU carrier PCB schematic.** Teensy socket, TCAN1042, IMU
      (orientation `V-073`), buck + load-dump TVS, six conditioned inputs,
      display header, page button, PSRAM fitted (D-170). Every part is decided
- [ ] **H-002 AGENT · DCU carrier PCB schematic.** Same power section, servo
      drivers, comfort MOSFETs
- [ ] **H-003 BLOCKED on T-007** · Panel 1:1 drawing ([`../01-DESIGN/PANEL-LAYOUT.md`](../01-DESIGN/PANEL-LAYOUT.md)
      is the template)
- [ ] **H-004 BLOCKED on T-028** · Sill plate drawing
- [ ] **H-005 AGENT · Dash post bracket layout** — 15 leg receptacles plus four
      drops, using the `1027-003-1200` clips confirmed in the TE catalogue
- [ ] **H-006 BLOCKED on Q-061–Q-065** · Re-run the A4/A5/A6/A15 ladder maths
      for whichever extra states the packets add (`../01-DESIGN/LADDERS.md`)

## 3 · Documentation

- [x] **X-001 AGENT · Wiring diagram set.** One SVG per leg, generated from the
      cavity CSV — `../02-HARNESS/diagrams/`. *Done 2026-08-30*
- [ ] **X-002 AGENT · Panel schematic sheet.** Relay bank, fuse block, busbars,
      wake network as one drawing, in the same SVG style
- [ ] **X-003 AGENT · Troubleshooting guide.** Symptom → likely cause → which
      document. Written while the design is fresh, used when it isn't
- [ ] **X-004 AGENT · Commissioning test card.** Per-circuit pass/fail for
      Phase 6, tighter than the migration log
- [x] **X-005 AGENT · Strip duplicated current figures from the leg files.**
      *Done 2026-08-30 — leg files describe why; figures come from the CSV*
- [ ] **X-006 AGENT · Failure-mode table** (was Z-005). For each of the ~20
      things that can fail, what the driver sees and what still works. The ICU
      already guarantees gauges survive a CAN loss; nothing else is written
- [ ] **X-007 CAMDEN · Archived render of the agreed cluster.** Run
      `icu_sim/sim.exe`, `+` for 2×, screenshot, save as
      `03-MODULES/cluster-2026-08.png` (Audit 3, I-69)

## 4 · Further ahead

- [ ] **Z-001 · LS swap electrical plan.** O13, O14, the CAN drop and the L1-S2
      sensor spares are reserved. Nobody has written what actually connects
- [ ] **Z-002 · Radar subsystem design** (`V-061`) — concealed sensors front and
      rear, DCU-managed. Cavities are DEFERRED in L3-S2/S3 and L4-S
- [ ] **Z-003 · Mirror control protocol** (`V-060`, `Q-062`) — the door
      connector has zero spare cavities, so the mirror choice is load-bearing
- [ ] **Z-004 · Cold-weather behaviour.** Battery heater draw (`V-052`), winter
      parasitic budget, whether the PMU should shed loads below a temperature

## 5 · Where progress genuinely stops

Four measurements gate the physical build, and no amount of design replaces
them:

| Gate | Blocks |
|---|---|
| **T-007** dash envelope | Panel drawing, panel parts, all of Phase 4 |
| **T-008** harness routes | Cut list lengths, the wire order, Phase 5 |
| **T-014** clamp every load | Every soft fuse — **irreversible window** |
| **T-011** pop-up limit pinout | A4/A5 ladder values |

Plus one ruling: **Checklist 0.23** — the five packets in [`OPEN.md`](OPEN.md) §1. Four
functions have no pin until it is done, and the connector order waits on it.

Everything on the AGENT list above can be done without any of them. That is
roughly two hundred hours of design and firmware work still available on a
laptop.

# FORWARD WORK — what becomes possible next

*Rev 2026-08-30 · owns: the agent-side backlog — firmware (F), hardware design (H), documentation (X) and further-ahead thinking (Z). Camden's physical tasks are [`TASKS-CAMDEN.md`](TASKS-CAMDEN.md)'s; the build sequence is [`../04-BUILD/CHECKLIST.md`](../04-BUILD/CHECKLIST.md)'s.*

Ordered by what unblocks the most. **AGENT** items can be done now on a
laptop; **BLOCKED** items name their gate. Tick and date here when done; the
result goes in [`CHANGELOG.md`](CHANGELOG.md). Completed items leave this
file — the D-register and CHANGELOG are the record; no backlog lives here.

## Contents

1. Firmware · 2. Hardware design · 3. Documentation · 4. Further ahead ·
5. Where progress genuinely stops

---

## 1 · Firmware — the largest available block

- [ ] **F-003 AGENT · Sensor conditioning schematic.** Dividers, RC filters and
      clamp diodes for all six ICU inputs, values computed from the sender
      ranges. Drafted in [`../03-MODULES/ICU-CARRIER.md`](../03-MODULES/ICU-CARRIER.md) §3; nothing blocks it — A7 closed (D-197)
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
- [ ] **F-009 BLOCKED on V-065** · Reconcile `can_map.h` 0x100–0x130 against the
      PMU's actual export (Checklist 2.5)
- [ ] **F-010 AGENT · Config-as-data.** Thresholds, colours and units on the SD
      card with a safe-mode render path if the file is missing or corrupt
      (BENCH-BRINGUP Stage 6)

## 2 · Hardware design

- [ ] **H-003 BLOCKED on T-007** · Panel 1:1 drawing ([`../01-DESIGN/PANEL-LAYOUT.md`](../01-DESIGN/PANEL-LAYOUT.md)
      is the template)
- [ ] **H-004 BLOCKED on T-028** · Sill plate drawing
- [ ] **H-005 AGENT · Dash post bracket layout** — 15 leg receptacles plus four
      drops, using the `1027-003-1200` clips confirmed in the TE catalogue

## 3 · Documentation

- [ ] **X-003 AGENT · Troubleshooting guide.** Symptom → likely cause → which
      document. Written while the design is fresh, used when it isn't
- [ ] **X-004 AGENT · Commissioning test card.** Per-circuit pass/fail for
      Phase 6, tighter than the migration log
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
- [ ] **Z-003 · Mirror control protocol** (`V-060`, `Q-062` → D-181) — the door
      connector has zero spare cavities, so the mirror choice is load-bearing
- [ ] **Z-004 · Cold-weather behaviour.** Battery heater draw (`V-052`), winter
      parasitic budget, whether the PMU should shed loads below a temperature

## 5 · Where progress genuinely stops

What still gates the physical build:

| Gate | Blocks |
|---|---|
| **T-007** dash envelope | Panel drawing, panel parts, all of Phase 4 |
| **T-008** harness routes | Cut list lengths, the wire order, Phase 5 |
| **V-081** pop-up motor ohm check (D-199 procedure) | Confirming K1/K2 single-direction drive before it's wired |
| **V-084** panel timing constants (with `T-051` eval board) | First light on the BT817 — `bt817.h` ships placeholders |

T-014 → D-197 and T-011 closed 2026-08 (D-175–D-178): every fuse is measured or at
its channel cap, and the pinouts came off the factory sheets.

Everything on the AGENT list above can be done without any of them. That is
roughly two hundred hours of design and firmware work still available on a
laptop.

# Camden's Tasks — Electrical / PMU

*Rev 2026-08-30 · owns: physical work, measurements, purchases and sign-offs that only Camden can clear. Each task cites the Checklist step it satisfies; the Checklist owns the sequence, this file owns the list. Lighting tasks are `../../lighting-body/TASKS.md`'s.*

**Blocking** means downstream work stops. IDs are permanent; done tasks stay
listed, struck through.

## Contents

1. Do next · 2. Phase 0 — the meter session · 3. Phase 0 — the tape measure
session · 4. Before Phase 4 · 5. Decisions and sourcing · 6. Firmware ·
7. Done

---

## 1 · Do next

| ID | Task | Why | Checklist |
|---|---|---|---|
| **T-014** | **Finish the meter session** — 3 of 22 outputs done | **Irreversible window.** These numbers cannot be recovered once the harness is out | 0.1 |
| **T-007** | **Dash cavity envelope** — W × H × D + 39-pin lever clearance | `Q-014`. Gates the panel drawing, the panel parts order and Phase 4 | 0.8 |
| **T-008** | **Every harness route with string, +15 %** | Gates the cut list lengths and the wire-and-connector order | 0.11 |
| T-022 | Check the Ionic's state of charge; keep it above BMS cutoff until fitted | A lithium left to self-discharge into cutoff is hard to recover | G0.4 |
| T-045 | Verify the two inbound housings arrive **with** terminals, not housing-only | If they ship bare, the small-terminal shortfall is worse than it looks | G0.2 |
| **T-049** | Record the VIN in `00-CAR/vehicle.md` | `Q-001`. Two minutes | — |

**T-007 and T-008 are two of the three biggest blockers in the project.**
Neither needs anything in the post.

## 2 · Phase 0 — the meter session

[`../05-BUILD/METER-SESSION.md`](../05-BUILD/METER-SESSION.md) is the step-by-step, with access points for
every circuit and workarounds for the four broken ones. ~10–12 hrs across
sittings.

| ID | Task | Closes | Checklist |
|---|---|---|---|
| **T-014** | **Clamp every load, steady and stall** — headlights lo/hi, wiper lo/hi/stall, defog cold, fuel pump, horn, tail on `RG`, hazard on `WG`, reverse, interior, coils at 3000. **Done:** brake, turn L, turn R | every soft fuse; `V-054` | 0.1 |
| **T-011 + T-015** | **Do these together** (D-127). Continuity-test the pop-up motor pinout with the battery disconnected, then drive it on the identified pins for running and stall current | `V-030`, A-007 → D-112; sizes the motor bus | 0.2, 0.6 |
| T-004 | Alternator output rating off the case | `V-002`, `V-019` | 0.4 |
| T-012 | Fuel sender ohm range, empty → full | `V-037`, sets the A7 divider | 0.5 |
| T-023 | Continuity-test which ignition outputs stay live in RUN and START | `V-050`. The A16 key ladder is wrong if this is | 0.7 |
| T-009 | Confirm the coil / ignitor configuration matches twin coils + twin igniters | `V-001` | with 0.1 |
| T-040 | Diagnose the washer pump (K-022) — pump, wiring, or switch? | Decides whether T-039 exists | Part 3.3 |
| T-041 | Confirm the blower is the motor, not the feed — 12 V at the connector with the switch on? (K-023) | | Part 3.4 |

**The three readings that matter most:** wiper stall (sets O8/O9 and the wire
gauge), pop-up stall (sets the motor bus and the relay bank), defog cold. The
blower cannot be measured — O16 stays 25 A with the flyback diode and gets its
soft fuse at migration from whatever is fitted (D-126).

## 3 · Phase 0 — the tape measure session

| ID | Task | Closes | Checklist |
|---|---|---|---|
| **T-007** | **Dash cavity envelope** | `Q-014` | 0.8 |
| T-024 | Cargo bin vs the Group 25 case. Mock in cardboard before cutting | `V-051` | 0.9 |
| T-028 | Sill space behind the kick panel — 4 relays, 3 fuse positions, ground stud | `V-055` | 0.10 |
| **T-008** | Every harness route with string, +15 % | the cut list | 0.11 |
| T-018 | Photograph the entire harness — connectors, branches, grounds → `01-REFERENCE/photos/` | reference once the loom is gone | 0.12 |
| T-019 | Find and log the wideband tap and every PO splice | K-001, K-002 | 0.13 |
| T-029 | Battery terminal type — SAE or 3/8 threaded. **The battery is here; look at it** | `V-053`, decides the lugs | 0.14 |

## 4 · Before Phase 4

| ID | Task | Why | Checklist |
|---|---|---|---|
| **T-043** | **Mark the housing** — paint pen dot beside cavity 1 | Costs nothing. The question is never re-asked at the bench with the panel half-built (D-139) | G0.5 |
| **T-044** | **Order spare 1.5 mm terminals, 211CC2S2160P**, ~15 minimum | Zero spares on the size that is 69 % of the connector, hardest to crimp, while learning to crimp (D-135) | 1.8 |

## 5 · Decisions and sourcing

| ID | Task | Blocks | Checklist |
|---|---|---|---|
| **T-030** | **Rule on the five design packets** `Q-061`–`Q-065` in [`OPEN.md`](OPEN.md), and `Q-014` | Four functions have no pin; the connector order | 0.23 |
| T-031 | **Source the new mirrors** — larger, heated, digital control. Confirm the conductor count (`V-060`) | D-093. D1/D2 has zero spare cavities; `Q-062` | 1.5 |
| T-032 | **Source a fuel-door solenoid** — never existed, this is new (D-098) | `Q-061` gives it an output | 1.6 |
| T-033 | **Source a hatch latch switch** — the original is broken (D-098) | | 1.7 |
| T-038 | **Source a blower motor.** Confirmed dead (K-023) | Before Phase 6 | 1.15 |
| T-039 | Source a washer pump — **only if T-040 says the pump is dead** | | 1.15 |
| T-017 | Verify connector pin labels in `01-REFERENCE/factory-circuits/` against the scans | Pin letters are the weak link in every rebuild table | before 0.13 |

## 6 · Firmware

| ID | Task | Hardware |
|---|---|---|
| T-048 | Flash and label boards 2 and 3 | Nothing — `firmware/pmu_sim/` on one, `tach_simulator/` on the other |

Stages 1–5 are done ([`../03-MODULES/BENCH-BRINGUP.md`](../03-MODULES/BENCH-BRINGUP.md)). What the bench still
needs to finish Stage 6 onward is [`../05-BUILD/BENCH-KIT.md`](../05-BUILD/BENCH-KIT.md) items 1–4.

## 7 · Done

| ID | Task | Result |
|---|---|---|
| ~~T-001~~ | Clamp DMM with DC current | **Bought** — UT210E |
| ~~T-002~~ | Ionic S9 (heated) | **Bought** — `V-017` closed |
| ~~T-003~~ | PMU-24 DL | **Bought** — `V-016`, `V-018` closed |
| ~~T-010~~ | Inspection sweep | Closed V-023, V-024, V-025, V-027, V-029, V-031, V-032, V-034, V-036, V-049 → D-097–D-100 |
| ~~T-013~~ | Sicma cavity geometry | Resolved from CAD, then confirmed in the hand (D-134). [`SPEC.md`](../01-DESIGN/SPEC.md) §11 |
| ~~T-016~~ | ~~Diagnose K-008~~ | **Cancelled** — D-105. Traced from the diagram; dies with the harness |
| ~~T-020~~ | Compare housing #1 to [`SPEC.md`](../01-DESIGN/SPEC.md) §11 | **Confirmed** — 12 large, 27 small, widest farthest out (D-134) |
| ~~T-021~~ | Inventory the PMU box | Connector kit **and** USB-to-CAN adapter both included |
| ~~T-025~~ | Count terminal stock | **16 large (4 spare), 27 small (zero spare)** — D-135 |
| ~~T-026~~ | Bench kit | **Bought:** 3 × Teensy 4.1 with pins, SN65HVD230 ×5, one micro-B cable, the meter. **Not bought** (D-140): resistors, breadboards, jumpers, board materials, rotary switch — [`BENCH-KIT.md`](../05-BUILD/BENCH-KIT.md) |
| ~~T-027~~ | Spare Sicma housings | **2 ordered**, each with a full pin set — **inbound**; T-045 checks them on arrival |
| ~~T-042~~ | Establish which cavity is pin 1 | Verified against the ECUmaster manual and the part. Top-left, opposite the purple lock (D-139) |
| ~~T-046~~ | Stage 4 — ladder decode | **Passed** (`ladder_decode_test/`) |
| ~~T-047~~ | Stage 5 — tach measurement | **Passed** (`tach_simulator/`, one jumper) |
| → lighting | T-034, T-035, T-036, T-037 | Moved to `../../lighting-body/TASKS.md` (D-123) |

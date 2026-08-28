# Camden's Tasks — Electrical / PMU

Physical work, measurements, purchases, sign-offs. Only Camden can clear these.
**Blocking** means downstream work stops.

---

## DONE

| ID        | Task                                                                                                                                              | Result                                                                                              |
|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| ~~T-001~~ | Clamp DMM with DC current                                                                                                                         | **PURCHASED** — UT210E. Unblocks T-014, T-015, T-016                                                |
| ~~T-002~~ | Ionic S9 (heated)                                                                                                                                 | **PURCHASED** — closes V-017                                                                        |
| ~~T-003~~ | PMU-24 DL                                                                                                                                         | **PURCHASED** — closes V-016, V-018                                                                 |
| ~~T-013~~ | Sicma cavity geometry                                                                                                                             | **RESOLVED from CAD.** 3×13, L→R T→B, 2 large / 9 small / 2 large per row. SPEC §11                 |
| ~~T-021~~ | Inventory the PMU box                                                                                                                             | Connector kit **and** USB-to-CAN adapter both included                                              |
| ~~T-026~~ | Bench kit — 3× Teensy 4.1 w/ pins, SN65HVD230 5-pack, micro-B cables, 120 Ω, E24 assortment, breadboards, jumpers, board materials, rotary switch | **PURCHASED.** Phase 2A and 2B fully unblocked                                                      |
| ~~T-027~~ | Spare Sicma housings                                                                                                                              | **2 PURCHASED**, each with a full pin set. Three housings total — bench, car, spare                 |
| ~~T-010~~ | Inspection sweep                                                                                                                                  | **DONE.** Closed V-023, V-024, V-025, V-027, V-029, V-031, V-032, V-034, V-036, V-049 → D-097–D-100 |

## Connector and terminal stock

| Housing | Source          | Terminals                | Allocated to                                        |
|---------|-----------------|--------------------------|-----------------------------------------------------|
| #1      | PMU box         | full set, spares unknown | **The car** — the real one, terminated once (D-004) |
| #2      | Purchased spare | full set, spares unknown | **Bench mule** — test pigtail, Checklist 2.3        |
| #3      | Purchased spare | full set, spares unknown | **Spare** — untouched until something goes wrong    |

**Terminals deliberately not ordered yet** — pending the stock count below.

---

## OPEN — do these next

| ID        | Task                                                                                                                                         | Why                                                             | Blocks           | Status |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|------------------|--------|
| **T-025** | **Count all three terminal sets by size** — 2.8 mm large / 2.8 mm / 1.5 mm. Need **12 large + 27 small** per housing, plus 20% working spare | Decides whether terminals go on the wire order at all           | Phase 1 ordering | Open   |
| **T-020** | Compare housing #1 to SPEC §11 — confirm 2 large / 9 small / 2 large per row in the hand                                                     | Ten seconds. Makes the CAD result certain before any crimp      | Before Phase 4   | Open   |
| T-022     | Check the Ionic's state of charge, keep it above BMS cutoff until fitted                                                                     | A lithium left to self-discharge into cutoff is hard to recover | Now              | Open   |

## OPEN — Phase 0, the meter session

| ID        | Task                                                                                                                                                     | Blocks                                                                           |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| **T-014** | **Clamp every load — inrush and steady.** Headlights lo/hi, blower each speed, wiper lo/hi, defog, fuel pump, horn, tail, brake, turn, reverse, interior | **BLOCKING.** Sets every gauge and soft fuse. Impossible once the harness is out |
| ~~T-016~~ | ~~Diagnose K-008~~                                                                                                                                       | **CANCELLED — D-105.** The fault dies with the harness. Not being fixed          |
| T-015     | Pop-up motor stall current, both sides                                                                                                                   | Sizes the motor bus and relay bank                                               |
| T-004     | Alternator output rating off the case                                                                                                                    | V-002, V-019                                                                     |
| T-012     | Fuel sender ohm range, empty → full                                                                                                                      | V-037, sets the A7 divider                                                       |
| T-011     | Continuity-test pop-up motor internal limit pinout                                                                                                       | V-030, A-007. Adjusts the A4/A5 ladders                                          |
| T-023     | Continuity-test which ignition outputs stay live in RUN and START                                                                                        | V-050. The A16 key ladder is wrong if this is                                    |
| T-009     | Confirm the coil / ignitor configuration matches twin coils + twin igniters                                                                              | V-001                                                                            |

## OPEN — Phase 0, the tape measure session

| ID        | Task                                                              | Blocks                                         |
|-----------|-------------------------------------------------------------------|------------------------------------------------|
| **T-007** | **Dash cavity envelope** — W × H × D + 39-pin lever clearance     | Q-014. Panel drawing, panel parts order        |
| T-024     | Cargo bin vs the Group 25 case. Mock in cardboard before cutting  | V-051. Battery tray order                      |
| T-028     | Sill space behind the kick panel — 4 relays, 3 fuses, ground stud | V-055. Sill plate fabrication                  |
| **T-008** | Every harness route with string, +15%                             | **The wire cut list**, and the connector order |
| T-018     | Photograph the entire harness — connectors, branches, grounds     | Reference once the loom is gone                |
| T-019     | Find and log the wideband tap and every PO splice                 | K-001, K-002                                   |
| T-029     | Battery terminal type — SAE or 3/8 threaded                       | V-053. Decides which lugs to buy               |

## OPEN — decisions and sourcing

| ID    | Task                                                                                            | Blocks                                        |
|-------|-------------------------------------------------------------------------------------------------|-----------------------------------------------|
| T-030 | Answer Q-014, Q-037, Q-042, A-005, A-007 in `OPEN.md`                                           | Panel drawing, display order, PCB layout      |
| T-031 | **Source the new mirrors** — larger, heated, digital control. Confirm conductor count `[V-060]` | D-093. D1/D2 has zero spare cavities          |
| T-032 | **Source a fuel-door solenoid** — never existed, this is new                                    | D-098                                         |
| T-033 | **Source a hatch latch switch** — original is broken                                            | D-098                                         |
| T-017 | Verify connector pin labels in `01-REFERENCE/factory-circuits/`                                 | Read off scans. Pin letters are the weak link |

---

## What's unblocked right now

**Phase 2A — PMU configuration.** 35–55 hrs. You have the PMU, the USB-to-CAN
adapter, a bench housing, 120 Ω resistors and the board materials. Nothing is
missing.

**Phase 2B — firmware.** 155–325 hrs. Three Teensys, five transceivers, cables,
breadboards. Nothing is missing.

Together that's the largest block of work in the project and none of it needs
the car, the shop, or good weather.

---

## NEW TASKS — 2026-08 round four

| ID        | Task                                                                                                                                  | Why                                                                                                                                       | Blocks              | Status |
|-----------|---------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|---------------------|--------|
| **T-011** | **Continuity-test the pop-up motor internal limit pinout** — which of WR/YG/R/RY are limits vs drive, at both extremes and mid-travel | `[A-007]` was converted from an assumption to this task (D-112). The A4/A5 ladder values in `LADDERS.md` stay provisional until it's done | Ladder finalisation | Open   |
| **T-034** | **Measure the tail light aperture** — width, height, depth, mounting `[V-063]`                                                        | Drives the entire tail light design. Target is 5 cm reverse section, 2.2 cm strip height, but that assumes a 30 cm aperture               | Tail light design   | Open   |
| **T-035** | **Confirm 7-inch round or rectangular sealed beams** on this car `[V-066]`                                                            | Decides whether the headlamp needs an adapter plate                                                                                       | `[Q-048]`           | Open   |
| **T-036** | Answer `[Q-048]` — which headlamp unit                                                                                                | 4×6 + adapter, 5×7, or 7-inch round with a rectangular element                                                                            | Headlamp order      | Open   |
| **T-037** | Source **DOT/SAE LED modules** with published candela, red and white `[V-064]`                                                        | Photometry is the hard part of the tail lights, not area                                                                                  | Tail light build    | Open   |

## Reminder — the four measurements that need nothing in the post

| ID        | Task                             | Tool         |
|-----------|----------------------------------|--------------|
| **T-007** | Dash cavity envelope             | Tape measure |
| **T-008** | Harness routes, +15%             | String       |
| **T-034** | Tail light aperture              | Tape measure |
| **T-028** | Sill space behind the kick panel | Tape measure |

**T-007 and T-008 are two of the three biggest blockers in the project.** Neither
needs the meter, the Teensys, or anything else in transit.

---

## METER DAY — 2026-08

The clamp meter arrives today. `05-BUILD/METER-SESSION.md` is the step-by-step,
with access points for every circuit and workarounds for the four broken ones.

| ID                | Task                                                                                                                                                                     | Note                                                                               |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| **T-014**         | **The meter session.** Half a day. Parts 1–5 of METER-SESSION.md                                                                                                         | **Irreversible window.** These numbers cannot be recovered once the harness is out |
| **T-011 + T-015** | **Do these together** (D-127). Continuity-test the pop-up motor pinout with the battery disconnected, then drive it on the identified pins for running and stall current | Guessing the pinout risks the limit switches                                       |
| **T-040**         | Diagnose the washer pump `[K-022]` — pump, wiring, or switch?                                                                                                            | Decides whether it goes on the parts list                                          |
| **T-041**         | Confirm the blower is the motor, not the feed — 12 V present at the connector with the switch on? `[K-023]`                                                              |                                                                                    |
| **T-038**         | **Source a blower motor.** Confirmed dead, on the migration list                                                                                                         | Before Phase 6                                                                     |
| **T-039**         | Source a washer pump — **only if T-040 says the pump is dead**                                                                                                           |                                                                                    |

### The three readings that matter most

Everything else has headroom. These three size real hardware:

1. **Wiper stall** — sets O8/O9 and the wire gauge
2. **Pop-up stall** — sets the motor bus and the relay bank
3. **Defog cold** — grids draw more cold, and the cold figure is the design one

### What can't be measured at all

**The blower.** The motor is dead. O16 stays a 25 A channel with the flyback
diode and gets its soft fuse set at migration from whatever is fitted (D-126).

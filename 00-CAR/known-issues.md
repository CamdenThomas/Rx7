# Known Issues & Quirks

Anything about this specific car that will bite you later. PO hacks, worn parts,
undocumented wiring. Add to this the moment you find something.

## Electrical

| #     | Issue                                                                                                                                                                                                                                                                                                                                     | Status                                                                                                                                                                                                                                     |
|-------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| K-001 | Wideband O2 wiring tapped into factory harness, location unknown                                                                                                                                                                                                                                                                          | Find and log during Phase 0 step 005                                                                                                                                                                                                       |
| K-002 | Previous-owner splices and hacks — extent unknown                                                                                                                                                                                                                                                                                         | Full harness photo survey pending (Phase 0 steps 003–005)                                                                                                                                                                                  |
| K-003 | Interval wiper control unit present, to be deleted                                                                                                                                                                                                                                                                                        | Planned deletion, logic moves to PMU                                                                                                                                                                                                       |
| K-008 | **Turn signal operation intermittently affects other circuits — fuel pump and tachometer both react to blinker pulses.** Traced from the factory diagram to two shared ground studs: X-13 carries the flasher, instrument cluster and emission unit; X-15 carries the rear lamps and the fuel pump. Blinker current modulates both references | **NOT BEING FIXED — D-105.** The fault lives in the factory harness's shared grounds and has no path into the new one, which gives every zone a local star node. It dies with the harness. Observed severity is low: the pump changes note, the engine does not, so delivery stays above the regulator setpoint. See `01-REFERENCE/factory-circuits/FAULT-K008-analysis.md` for the trace |

## Chassis / mechanical

| #     | Issue                                                                     | Status                                        |
|-------|---------------------------------------------------------------------------|-----------------------------------------------|
| K-004 | Pre-1983 steering box: non-hardened sector shaft, known wear point        | Replacement being researched                  |
| K-005 | Age-related rubber degradation throughout suspension                      | Full bushing overhaul planned                 |
| K-006 | Rear compliance link bushings — improper replacement risks chassis damage | Procedure must be confirmed before attempting |
| K-007 | Rust — extent not surveyed                                                | Not assessed                                  |
| K-019 | **Coolant has never been fully drained or flushed.** About half was lost and replaced during the Sep 2025 intake removal. What came out looked OK and the passageways weren't bad, so this is a note rather than an alarm — but the remaining half is of unknown age on a 44-year-old car | Not urgent. Worth a proper drain and refill at some point, and the thermostat and hoses are worth eyeballing while it's open. **Not electrical, does not block the PMU project** |

## Notes

Nothing in this file is verified unless marked. Fill in as the car is
disassembled and inspected.

---

## UPDATE 2026-08 — inspection results

`[D-097]` Confirmed gone from the car, removed from all specs:

| # | Was | Status |
|---|---|---|
| K-009 | Cruise control unit | **Gone.** Explicitly not wanted |
| K-010 | Rear wiper and washer | **Gone** |
| K-011 | Power antenna | **Gone** |
| K-012 | Headlight cleaner | **Gone** |
| K-013 | All cold-start hardware — hot start relay/motor, sub-zero motor/sensor, choke, carb heater | **Zero remain post-Weber** |
| K-014 | Power mirror control | **Dead.** Replaced by new heated mirrors with digital control |

## Still broken or missing

| # | Issue | Status |
|---|---|---|
| K-015 | **A/C barely cool** — probably low on charge | Not an electrical fault. Out of scope for the PMU project, but do not chase it as a wiring problem |
| K-016 | **Hatch latch switch broken** | Needs sourcing, Checklist 1.7 |
| K-017 | **Fuel-door solenoid never existed** | New addition, not a migration. Needs sourcing, Checklist 1.6 |

## Confirmed working

| # | Item | Status |
|---|---|---|
| K-018 | Both retractor manual raise knobs | **Functional** — D-040 holds, no software gesture needed to park the lamps up |

---

## FAULTS FOUND 2026-08

| # | Issue | Rebuild impact | Measurement impact |
|---|---|---|---|
| **K-020** | **Rear defrost switch (G-24) broken** | **None** — the switch is deleted anyway. Defog moves to the CAN keypad (Checklist 2.21) | **Blocks measuring O4** through the switch. Jumper the switch connector or feed the grid directly |
| **K-021** | **Headlamp retractor switch (E-02) broken** — the dash switch, not the column combo switch | **None** — deleted by D-038. Pop-ups raise from the A15 ladder, wink switches are the only manual control | **Blocks operating the pop-ups** to measure stall (T-015). Must drive the motors directly |
| **K-022** | **Washer fluid pump (D-01) not working** | **Unknown until diagnosed.** Pump, wiring, or switch? The pump is currently assumed to carry forward | If the pump is dead it needs sourcing. **Diagnose before ordering** |
| **K-023** | **Blower motor (G-14) not working** | Was already flagged as a death-date item — now **confirmed dead, not dying.** Needs replacing | **O16 cannot be measured.** Size the channel from the replacement's spec sheet instead |

### The pattern worth noticing

**Three of these four are switches or devices the rebuild was already deleting or
replacing.** They cost nothing in redesign. What they cost is **measurement
access** — you cannot measure a circuit by operating a switch that doesn't work.

Every one has a workaround. See `02-PROJECTS/electrical-pmu/05-BUILD/METER-SESSION.md`.

### Still to look for

The list above is what's known. Assume there is more. Things to check while the
meter is out:

- Every interior lamp, glovebox, luggage compartment
- Both horns individually
- Wiper on all speeds including intermittent
- Every turn signal position and the hazard
- Reverse lamps with the car in R
- Both pop-ups through a full cycle
- Both windows through full travel
- All four door pin switches

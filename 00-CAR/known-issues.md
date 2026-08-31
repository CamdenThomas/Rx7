# Known Issues & Quirks

*Rev 2026-08-31 · owns: every fault, quirk and PO hack of this specific car — K-###. One table per area; add a row the moment something is found. Nothing here is verified unless the row says so.*

## Electrical

| # | Issue | Status | Rebuild / measurement impact |
|---|---|---|---|
| K-001 | Wideband O2 wiring tapped into the factory harness, location unknown | Find and log — Checklist 0.13 (`T-019`) | Carried to the dash on L1-S1 12 and capped (`A-011`) |
| K-002 | Previous-owner splices and hacks — extent unknown | Full harness photo survey — Checklist 0.12–0.13 (`T-018`, `T-019`) | |
| K-003 | Interval wiper control unit present | Planned deletion; the timer moves into PMU logic (Checklist 2.12) | |
| K-008 | **Turn signals modulate other circuits — fuel pump and tach react to blinker pulses.** Traced from the factory diagram to two shared ground studs: X-13 (flasher, cluster, emission unit) and X-15 (rear lamps, fuel pump) | **Not being fixed — D-105.** It lives in the factory harness's shared grounds and has no path into the new one, which gives every zone a local star node. Observed live during the first meter sitting (turn current dips 3.4 → 2.3 A with the pump note) | Trace: [`../01-REFERENCE/factory-circuits/FAULT-K008-analysis.md`](../01-REFERENCE/factory-circuits/FAULT-K008-analysis.md) |
| K-009 | Cruise control unit | **Gone** (D-097). Explicitly not wanted | Removed from all specs |
| K-010 | Rear wiper and washer | **Gone** (D-097) | |
| K-011 | Power antenna | **Gone** (D-097) | |
| K-012 | Headlight cleaner | **Gone** (D-097) | |
| K-013 | Cold-start hardware — hot-start relay/motor, sub-zero motor/sensor, choke, carb heater | **Zero remain post-Weber** (D-097) | |
| K-014 | Power mirror control | **Dead.** New heated mirrors with digital control replace it (D-093, `T-031`) | Conductor count `V-060`; dash → sill path `Q-062` → D-181 |
| K-016 | **Hatch latch switch broken** | Needs sourcing — Checklist 1.7 (`T-033`) | Output for the solenoid is `Q-061` → D-180 |
| K-017 | **Fuel-door solenoid never existed** | New addition, not a migration — Checklist 1.6 (`T-032`, D-098) | Output is `Q-061` → D-180 |
| K-018 | Both retractor manual raise knobs | **Functional** — D-040 holds, no software gesture needed to park the lamps up | |
| K-020 | **Rear defrost switch (G-24) broken** | **No rebuild impact** — the switch is deleted; defog moves to the CAN keypad (Checklist 2.18) | Blocks measuring O4 through the switch — jumper the connector or feed the grid directly — the cold read now comes from PMU telemetry at migration (D-174, `T-014` → D-197) |
| K-021 | **Headlamp retractor switch (E-02) broken** — the dash switch, not the column combo switch | **No rebuild impact** — deleted by D-038; pop-ups raise from the A15 ladder, wink switches are the only manual control | Blocks operating the pop-ups to measure stall (`T-015`) — drive the motors directly (Part 3.2) |
| K-022 | **Washer fluid pump (D-01) not working** | **Unknown until diagnosed** — pump, wiring, or switch? (`T-040`) | Diagnose before ordering (`T-039`). The pump also has no PMU output yet — `Q-063` → D-182 |
| K-023 | **Blower motor (G-14) not working** | **Confirmed dead**, not dying — needs replacing (`T-038`, Checklist 1.15) | O16 cannot be measured; size it from the replacement's spec sheet (D-126) |

Three of the four 2026-08 faults are switches or devices the rebuild was
already deleting or replacing. They cost nothing in redesign; what they cost
was **measurement access** — and the campaign closed around them anyway
(`T-014` → D-197): measured where clean, channel caps elsewhere, PMU
telemetry finishing the job at migration (D-174, D-175).

## Mechanical

| # | Issue | Status |
|---|---|---|
| K-004 | Pre-1983 steering box: non-hardened sector shaft, known wear point | Replacement being researched |
| K-005 | Age-related rubber degradation throughout the suspension | Full bushing overhaul planned |
| K-006 | Rear compliance link bushings — improper replacement risks chassis damage | Procedure must be confirmed before attempting |
| K-007 | Rust — extent not surveyed | Not assessed; the deferred lighting & body pass surveys it (`TAIL-LIGHTS.md` §10, D-201) |
| K-015 | **A/C barely cool** — probably low on charge (D-099) | Not an electrical fault. Out of scope for the PMU project; do not chase it as a wiring problem |
| K-019 | **Coolant has never been fully drained or flushed.** About half was lost and replaced during the Sep 2025 intake removal; what came out looked OK | Not urgent. A proper drain and refill at some point, and eyeball the thermostat and hoses while it's open. Does not block the PMU project |

## Still to look for

The list above is what's known. Assume there is more. While the meter is out:
every interior lamp, glovebox and luggage lamp · both horns individually ·
wipers on every speed including intermittent · every turn position and the
hazard · reverse lamps in R · both pop-ups through a full cycle · all four door
pin switches. (The windows are manual — nothing to test.)

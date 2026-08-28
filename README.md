# RX-7 — Master File System

Root for every RX-7 project. Car-level facts live at the top and are reused by
every project underneath. Project folders are self-contained; `00-CAR` is
permanent.

## Structure

```
Rx7\
├── README.md              <- you are here. Conventions.
├── ASSISTANT.md           <- Claude's operating instructions. Read every session.
├── 00-CAR\                <- permanent. Survives every project.
│   ├── vehicle.md
│   ├── modifications.md
│   └── known-issues.md
├── 01-REFERENCE\
│   ├── factory-circuits\  <- the 1982 harness, decoded circuit by circuit
│   └── PMU_info\          <- pinout, manual, CAD
├── 02-PROJECTS\
│   ├── electrical-pmu\    <- the active project
│   └── lighting-body\     <- deferred. LED lights, custom lamps, body
└── 99-ARCHIVE\            <- superseded. Never deleted.
```

## Projects

| Project | State |
|---|---|
| **`electrical-pmu/`** | **Active.** PMU, battery, harness, DCU/ICU. Runs on **stock incandescent bulbs** |
| `lighting-body/` | **Deferred.** LED conversion, custom tail lights, headlamp units, rust and paint. Starts after the electrical rebuild is shaken down |

Lighting was split out 2026-08 (D-123) because none of it is needed to finish the
car — every lamp channel has 40–74% headroom on filament bulbs.

## The electrical project — what's in it

**Start here:** `STATUS.md` for where things stand · `GLOSSARY.md` if the
notation is unfamiliar.

| File | Holds |
|---|---|
| **STATUS.md** | **Where the project is. Refreshed every session. Read this first** |
| **GLOSSARY.md** | Every ID prefix, channel, connector code and colour scheme decoded |
| **SPEC.md** | Canonical. All 39 pins, connector geometry, wire colours, module split. **Rev C** |
| **DECISIONS.md** | Append-only, D-001…D-105, with a topic index at the top |
| **OPEN.md** | Questions with answer blocks, assumptions, verify checklist |
| **TASKS-CAMDEN.md** | Physical work only Camden can do |
| **CHECKLIST.md** | The build, phase by phase, with checkboxes |
| **SAFETY.md** | Lithium, 2 AWG, under the car, fuel, the meter session |
| **LOADS.md** | Estimated draw and signal type, every circuit. **The only source for current figures** |
| **LADDERS.md** | Resistor values for all six switch ladders |
| **SCHEMATICS.md** | Wake network, H-bridges, constant bus, ground architecture |
| **PARTS-CHANGES.md** | Every part being replaced, and with what |
| **METER-SESSION.md** | Field procedure for the measurement session |
| **BATTERY-INSTALL.md** | Ionic S9, cargo bin, power backbone |
| **DCU-CLUSTER.md** | DCU and ICU scope, MCU selection, display capability |
| **CAN-MESSAGES.md** | The message map. Finalise before firmware |
| **MIGRATION-LOG.md** | Phase 6 working sheet — the authoritative migration order |
| **CUT-LIST.md** | Wire cut list and label schedule. Blocked on T-008 |
| **LOGS.md** | Config versions, firmware versions, photo index, session log |
| **BOM.md** / **BUY-LIST.md** | Money, and what's already bought |
| **legs/** | Four harness legs, connectors, pin map, sill node |

## Reference — the factory car

`01-REFERENCE/factory-circuits/` holds the 1982 harness decoded from the factory
diagram: ten circuit files, a frozen `OEM-RECORD.md`, a fuse and ground map, and
`FAULT-K008-analysis.md` — the blinker/fuel-pump/tach fault traced to two shared
ground studs.

## Conventions

**SPEC.md holds only what is true right now.** No history, no rationale.

**DECISIONS.md is append-only.** To reverse something, add a new entry marking
the old one superseded. Never edit a past entry.

**OPEN.md** — questions have `**ANSWER:**` blocks. Type into them; answered items
migrate to DECISIONS on the next pass.

**IDs are permanent and never reused.** `D` decision · `Q` question ·
`A` assumption · `V` verify · `T` Camden task · `K` known issue · `M` modification.
Gaps mean something closed.

## Session protocol

Name the mode: **DECIDE** (Claude presents packets with defaults, Camden answers),
**GENERATE** (Claude produces an artifact, Camden reviews), **AUDIT** (Claude
attacks SPEC for contradictions), **BUILD** (files updated from measured data).

Close with "give me the diff."

## Current state

| Area | State |
|---|---|
| **Gate 0** | **CLOSED** — bench kit and 3 connector housings in hand |
| **Phase 2A · PMU config** | **Unblocked, ready to start** |
| **Phase 2B · firmware** | **Unblocked, ready to start** |
| Pin allocation | Done — all 39, geometry confirmed from CAD |
| Leg + connector design | Done — 14 leg connectors + 2 door, all Deutsch |
| Resistor ladders | Done — bench verification pending |
| Panel schematics | Done — wake network, H-bridges, constant bus, grounds |
| Battery + backbone | Designed, parts listed, 2 AWG feed |
| DCU / ICU | Scoped, Teensy 4.1 × 2 selected, firmware not started |
| Load figures | Estimated — **T-014 measurement is the blocking item** |
| Wire cut list | Blocked on route measurements (T-008) |
| Panel 1:1 layout | Blocked on the dash envelope (T-007) |

## Next actions

1. **Start Phase 2A or 2B** — both are apartment work and need nothing more.
2. **Two half-days with the car** — the meter session and the tape measure
   session clear almost every remaining blocker. See `TASKS-CAMDEN.md`.
3. **Hold the wire order** until T-008.

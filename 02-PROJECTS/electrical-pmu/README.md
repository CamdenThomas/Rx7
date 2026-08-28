# ELECTRICAL / PMU PROJECT

*Rev 2026-08*

Full replacement of the 1982 RX-7's electrical system: ECUMaster PMU-24 DL,
rear-mounted Ionic S9 lithium, four modular harness legs, and two Teensy CAN
modules — a climate DCU and an instrument cluster ICU.

**Read `STATUS.md` first.** If the notation is unfamiliar, read
`01-DESIGN/GLOSSARY.md` second.

---

## Folder map

| Folder | Holds | When you need it |
|---|---|---|
| **`01-DESIGN/`** | The engineering | Working out *what* to build |
| **`02-HARNESS/`** | Legs, connectors, pin map, sill node | Working out *where wires go* |
| **`03-MODULES/`** | DCU, ICU, CAN | Firmware and module hardware |
| **`04-SUBSYSTEMS/`** | Battery, tail lights, parts changes | One self-contained thing at a time |
| **`05-BUILD/`** | Checklist, procedures, working sheets | In the shop, doing it |
| **`06-PROCUREMENT/`** | BOM, buy list | Spending money |
| **`07-PROCESS/`** | Decisions, open questions, tasks | Deciding, or recalling why |

Root holds only `STATUS.md` and this file.

## Files

### `01-DESIGN/`
| File | Holds |
|---|---|
| `SPEC.md` | **Canonical.** All 39 pins, connector geometry, wire colours, module split. Rev C |
| `GLOSSARY.md` | Every ID prefix, channel, connector code and colour scheme |
| `LOADS.md` | **The only source for current figures.** Draw and signal type, every circuit |
| `LADDERS.md` | Resistor values for all six switch ladders |
| `SCHEMATICS.md` | Wake network, H-bridges, constant bus, ground architecture |

### `02-HARNESS/`
| File | Holds |
|---|---|
| `PIN-MAP.md` | **Authoritative cavity assignments** |
| `CONNECTORS.md` | Housing part numbers, series selection, the dash post |
| `sill-node.md` | Window relays K5–K8, branch fuses, door connectors |
| `engine.md` `front-chassis.md` `dash.md` `rear-cabin.md` | The four legs |

### `03-MODULES/`
| File | Holds |
|---|---|
| `DCU-CLUSTER.md` | DCU and ICU scope, Teensy selection, display capability |
| `CAN-MESSAGES.md` | The message map. Finalise before firmware |

### `04-SUBSYSTEMS/`
| File | Holds |
|---|---|
| `BATTERY-INSTALL.md` | Ionic S9, cargo bin, power backbone |
| `TAIL-LIGHTS.md` | Custom LED strip design, FMVSS area math |
| `PARTS-CHANGES.md` | Every part being replaced, and with what |

### `05-BUILD/`
| File | Holds |
|---|---|
| `CHECKLIST.md` | The build, phase by phase, with checkboxes |
| `SAFETY.md` | Lithium, 2 AWG, under the car, fuel, the meter session |
| `METER-SESSION.md` | Field procedure for the measurement session |
| `MIGRATION-LOG.md` | Phase 6 working sheet. **The authoritative migration order** |
| `CUT-LIST.md` | Wire cut list and label schedule |
| `LOGS.md` | Config versions, firmware versions, photo index, session log |

### `06-PROCUREMENT/`
| File | Holds |
|---|---|
| `BOM.md` | Money — spent, remaining, buy order |
| `BUY-LIST.md` | What's already bought, with links |

### `07-PROCESS/`
| File | Holds |
|---|---|
| `DECISIONS.md` | Append-only, D-001…D-105, topic index at the top |
| `OPEN.md` | Questions with answer blocks, assumptions, verify checklist |
| `TASKS-CAMDEN.md` | Physical work only Camden can do |

---

## Conventions

**One owner per fact.** `LOADS.md` owns current figures. `PIN-MAP.md` owns cavity
assignments. `MIGRATION-LOG.md` owns the migration order. `CHECKLIST.md` owns
build sequence. If two files disagree, the owner wins.

**`DECISIONS.md` is append-only.** Reverse by adding a new entry marking the old
superseded. Never edit a past entry.

**IDs are permanent.** Gaps mean something closed.

---

## Cross-reference note

Files were reorganised into folders 2026-08. **Inline relative links inside
documents have not all been updated** — a link saying `LOADS.md` now means
`01-DESIGN/LOADS.md`. Filenames are unchanged and unique, so nothing is
ambiguous. Logged as `I-29`, fixed on next touch of each file.

# ELECTRICAL / PMU PROJECT

*Rev 2026-08-31 · owns: the map of this project — every file, what it holds, and who owns which fact.*

Full replacement of the 1982 RX-7's electrical system: ECUMaster PMU-24 DL,
rear-mounted Ionic S9 lithium, four modular harness legs plus a sill node, and
two Teensy 4.1 CAN modules — a climate DCU and an instrument cluster ICU.
Lighting and body work is deferred scope inside this project (D-201, D-204):
its open items live in OPEN §8, its tasks in TASKS-CAMDEN §6, its money as
BOM Wave 5; the design reference is archived at
[`TAIL-LIGHTS.md`](../../99-ARCHIVE/2026-08-31_lighting-body/TAIL-LIGHTS.md)
until the second pass starts after shakedown (L-004).

**Read [`STATUS.md`](STATUS.md) first.** If the notation is unfamiliar, read
[`01-DESIGN/GLOSSARY.md`](01-DESIGN/GLOSSARY.md) second. The agent's rules are
in the root [`ASSISTANT.md`](../../ASSISTANT.md).

## Contents

1. Folder map · 2. Files · 3. Who owns which fact · 4. Generated files ·
5. Conventions

---

## 1 · Folder map

Five folders, numbered in work order. 04-SUBSYSTEMS and 06-PROCUREMENT were
retired in the 2026-08-31 consolidation (D-200): battery went to the build
folder, money went to the process folder, the rest went to `99-ARCHIVE/`.

| Folder | Holds | When you need it |
|---|---|---|
| **[`01-DESIGN/`](01-DESIGN/)** | The engineering | Working out *what* to build |
| **[`02-HARNESS/`](02-HARNESS/)** | Legs, connectors, pin map, cavity state, sill node, the data tables, the diagrams | Working out *where wires go* |
| **[`03-MODULES/`](03-MODULES/)** | DCU, ICU, CAN, the firmware | Firmware and module hardware |
| **[`04-BUILD/`](04-BUILD/)** | Checklist, procedures, working sheets, battery install, safety | In the shop, doing it |
| **[`05-PROCESS/`](05-PROCESS/)** | Decisions, open items, tasks, the BOM, audits, forward work, changelog, the tools | Deciding, recalling why, spending, or checking the tree |

Root holds only [`STATUS.md`](STATUS.md) and this file.

## 2 · Files

### `01-DESIGN/`

| File | Holds |
|---|---|
| [`SPEC.md`](01-DESIGN/SPEC.md) | **Canonical.** Device, terminals, relays and fuses, the generated pin tables, connectors, modules, geometry, status vocabulary. Rev D |
| [`GLOSSARY.md`](01-DESIGN/GLOSSARY.md) | Every ID prefix, channel, connector code, colour scheme and status word |
| [`LOADS.md`](01-DESIGN/LOADS.md) | Estimation method and the incandescent design figures; LED figures as an appendix |
| [`CHANNEL-SCHEDULE.md`](01-DESIGN/CHANNEL-SCHEDULE.md) | The measured-to-configured pipeline — measured current and soft fuse per channel (generated block) |
| [`LADDERS.md`](01-DESIGN/LADDERS.md) | Resistor values and ADC windows for the switch ladders |
| [`SCHEMATICS.md`](01-DESIGN/SCHEMATICS.md) | Wake network, pop-up relays, constant bus, sill branches, ground architecture |
| [`PMU-CONFIG.md`](01-DESIGN/PMU-CONFIG.md) | Everything to type into the PMU client — decode tables, output logic, interlocks, wake, inrush |
| [`PANEL-LAYOUT.md`](01-DESIGN/PANEL-LAYOUT.md) | The backer plate — what mounts where. Template until `T-007` |
| *(lighting design — archived, D-204)* [`TAIL-LIGHTS.md`](../../99-ARCHIVE/2026-08-31_lighting-body/TAIL-LIGHTS.md) | **Deferred** (L-004) — tail lights (TL-1 … TL-19), headlamp sourcing; kept in `99-ARCHIVE/` until the second pass starts |

### `02-HARNESS/`

| File | Holds |
|---|---|
| [`README.md`](02-HARNESS/README.md) | The leg system explained; leg summary table |
| [`data/pmu_pins.csv`](02-HARNESS/data/pmu_pins.csv) | **Source of truth** — all 39 pins: channel, circuit, gauge, colour, destination, estimated and measured current, soft fuse, status |
| [`data/connectors.csv`](02-HARNESS/data/connectors.csv) | **Source of truth** — every cavity of every housing |
| [`data/housings.csv`](02-HARNESS/data/housings.csv) | **Source of truth** — housing part numbers, wedgelocks, locations |
| [`PIN-MAP.md`](02-HARNESS/PIN-MAP.md) | *Generated.* Pin-ordered and housing-ordered views of the CSVs |
| [`CAVITY-STATE.md`](02-HARNESS/CAVITY-STATE.md) | *Generated.* Every cavity with its status word — what is LIVE, PROVISIONED, RESERVED, DEFERRED, SPARE |
| [`CONNECTORS.md`](02-HARNESS/CONNECTORS.md) | Series selection, the dash post, accessories; housing table generated |
| [`engine.md`](02-HARNESS/engine.md) [`front-chassis.md`](02-HARNESS/front-chassis.md) [`dash.md`](02-HARNESS/dash.md) [`rear-cabin.md`](02-HARNESS/rear-cabin.md) | The four legs — *why* each is shaped as it is; cavities come from the CSV |
| [`sill-node.md`](02-HARNESS/sill-node.md) | The secondary node: K5–K8 sockets, F8/F9/F14, D1/D2 |
| [`diagrams/`](02-HARNESS/diagrams/) | *Generated* SVG per leg, the sill, the drops; plus [`architecture.svg`](02-HARNESS/diagrams/architecture.svg) |

### `03-MODULES/`

| File | Holds |
|---|---|
| [`DCU-CLUSTER.md`](03-MODULES/DCU-CLUSTER.md) | Module scope, node split, hardware, power, sensors, display decision |
| [`CAN-MESSAGES.md`](03-MODULES/CAN-MESSAGES.md) | The message map — IDs, byte layouts, rates, timeouts, bus load |
| [`CLUSTER-DESIGN.md`](03-MODULES/CLUSTER-DESIGN.md) | **Forward scope** — pages beyond the driving page, and what is settled |
| [`BENCH-BRINGUP.md`](03-MODULES/BENCH-BRINGUP.md) | Firmware bring-up stages 1–7; 1–5 done |
| [`ICU-CARRIER.md`](03-MODULES/ICU-CARRIER.md) [`DCU-CARRIER.md`](03-MODULES/DCU-CARRIER.md) | The two carrier PCB schematics (H-001, H-002); parts are `V-082`/`V-083` |
| [`firmware/README.md`](03-MODULES/firmware/README.md) | Folder map, build instructions, tests, simulator controls |
| **[`firmware/icu/cluster_core.h`](03-MODULES/firmware/icu/cluster_core.h)** | **Owns** cluster layout, palette, icons, rendering |
| [`firmware/icu/stats.h`](03-MODULES/firmware/icu/stats.h) | **Owns** the automated trip and lifetime figures |
| [`firmware/icu/can_map.h`](03-MODULES/firmware/icu/can_map.h) | **Master** CAN structs; the two test-sketch copies must match |
| [`firmware/icu/icu.ino`](03-MODULES/firmware/icu/icu.ino) | Teensy host; `ICU_FW_VERSION` |
| [`firmware/pmu_sim/channels.h`](03-MODULES/firmware/pmu_sim/channels.h) | *Generated* from `pmu_pins.csv` |
| `firmware/icu_sim/` · `firmware/tests/` · `firmware/pmu_sim/` · `firmware/dcu/` | Desktop simulator · regression suites (`run.bat`) · PMU simulator · DCU firmware |

### `04-BUILD/`

| File | Holds |
|---|---|
| [`CHECKLIST.md`](04-BUILD/CHECKLIST.md) | The build, phase by phase, with checkboxes |
| [`SAFETY.md`](04-BUILD/SAFETY.md) | Lithium, 2 AWG, under the car, fuel, working with the meter |
| [`BATTERY-INSTALL.md`](04-BUILD/BATTERY-INSTALL.md) | Ionic S9, cargo bin, power backbone, the Phase 3 sequence |
| [`MIGRATION-LOG.md`](04-BUILD/MIGRATION-LOG.md) | Phase 6 working sheet — **the migration order** |
| [`CUT-LIST.md`](04-BUILD/CUT-LIST.md) | Wire cut list and label schedule (structure generated; lengths wait on `T-008`) |
| [`BENCH-KIT.md`](04-BUILD/BENCH-KIT.md) | In-hand inventory and the in-car commissioning procedure (D-194) |
| [`LOGS.md`](04-BUILD/LOGS.md) | Config versions, firmware versions, photo index, session log |

### `05-PROCESS/`

| File | Holds |
|---|---|
| [`DECISIONS.md`](05-PROCESS/DECISIONS.md) | Append-only decision log, D-001 → and the merged lighting L-series; topic index at the top |
| [`OPEN.md`](05-PROCESS/OPEN.md) | Questions, verify items, assumptions in force — including the deferred lighting items |
| [`TASKS-CAMDEN.md`](05-PROCESS/TASKS-CAMDEN.md) | Physical work only Camden can do |
| [`BOM.md`](05-PROCESS/BOM.md) | **Owns the money** — every purchasable line by wave, plus the re-order part-number reference |
| [`FORWARD-WORK.md`](05-PROCESS/FORWARD-WORK.md) | The agent backlog — F/H/X/Z items |
| [`AUDITS.md`](05-PROCESS/AUDITS.md) | Every documentation audit and its results; where R1–R8 came from |
| [`CHANGELOG.md`](05-PROCESS/CHANGELOG.md) | One entry per session |
| [`ID-REGISTRY.md`](05-PROCESS/ID-REGISTRY.md) | *Generated.* Every ID ever issued, where it lives, open or closed |
| [`tools/gen.py`](05-PROCESS/tools/gen.py) | Regenerates every generated file and block from the CSVs (`--check` to verify) |
| [`tools/registry.py`](05-PROCESS/tools/registry.py) | Rebuilds [`ID-REGISTRY.md`](05-PROCESS/ID-REGISTRY.md) and `ids.json` |
| [`tools/check.py`](05-PROCESS/tools/check.py) | Drift checker — headers, links, closed IDs, old step numbers, copies, generator drift |

## 3 · Who owns which fact

If two files disagree, the owner wins (R3).

| Fact | Owner |
|---|---|
| Pin allocation, gauge, colour, destination, status | `02-HARNESS/data/pmu_pins.csv` |
| Cavity assignments | `02-HARNESS/data/connectors.csv` |
| Housing part numbers | `02-HARNESS/data/housings.csv` |
| Measured current and soft-fuse value | `pmu_pins.csv` (`meas_a`, `soft_fuse`) → [`CHANNEL-SCHEDULE.md`](01-DESIGN/CHANNEL-SCHEDULE.md) |
| Estimation method and design figures | [`01-DESIGN/LOADS.md`](01-DESIGN/LOADS.md) |
| Relays, fuses, terminals, geometry, status vocabulary | [`01-DESIGN/SPEC.md`](01-DESIGN/SPEC.md) |
| Ladder values | [`01-DESIGN/LADDERS.md`](01-DESIGN/LADDERS.md) |
| What goes into the PMU client | [`01-DESIGN/PMU-CONFIG.md`](01-DESIGN/PMU-CONFIG.md) |
| Lighting & body second pass (deferred) | DECISIONS §Lighting + OPEN §8 + BOM Wave 5; design archived — [`TAIL-LIGHTS.md`](../../99-ARCHIVE/2026-08-31_lighting-body/TAIL-LIGHTS.md) (D-204) |
| CAN message layouts | [`03-MODULES/CAN-MESSAGES.md`](03-MODULES/CAN-MESSAGES.md) ↔ `firmware/icu/can_map.h` |
| Cluster layout, palette, rendering | `firmware/icu/cluster_core.h` |
| Automated trip figures | `firmware/icu/stats.h` |
| Migration order | [`04-BUILD/MIGRATION-LOG.md`](04-BUILD/MIGRATION-LOG.md) |
| Build sequence | [`04-BUILD/CHECKLIST.md`](04-BUILD/CHECKLIST.md) |
| Money | [`05-PROCESS/BOM.md`](05-PROCESS/BOM.md) |
| What is pre-wired and waiting | the CSVs → [`CAVITY-STATE.md`](02-HARNESS/CAVITY-STATE.md) (add-later detail archived in `99-ARCHIVE/DEFERRED-FEATURES.md`) |
| Decisions | [`05-PROCESS/DECISIONS.md`](05-PROCESS/DECISIONS.md) |
| Hand-written logs | [`04-BUILD/LOGS.md`](04-BUILD/LOGS.md) |
| Car-level facts, faults, modifications | `00-CAR/` |
| The factory harness | `01-REFERENCE/factory-circuits/` |

## 4 · Generated files — never edit by hand

`python 05-PROCESS/tools/gen.py` rewrites these from the three CSVs:
[`PIN-MAP.md`](02-HARNESS/PIN-MAP.md), [`CAVITY-STATE.md`](02-HARNESS/CAVITY-STATE.md), `firmware/pmu_sim/channels.h`, the six SVGs
in `diagrams/`, and the `<!-- gen:… -->` blocks in `SPEC.md`,
`CHANNEL-SCHEDULE.md`, `CUT-LIST.md` and `CONNECTORS.md`. `gen.py --check`
reports drift without writing. `registry.py` rebuilds `ID-REGISTRY.md`.
`check.py` runs both checks and the document rules; it should be clean at
every session close.

## 5 · Conventions

**`SPEC.md` holds only what is true right now.** No history, no rationale.

**`DECISIONS.md` is append-only.** Reverse by adding a new entry and marking
the old one `> SUPERSEDED BY D-xxx`.

**`OPEN.md`** — packets have `ANSWER:` quotes. Type into them; the answer
becomes a decision and the packet leaves the file.

**IDs are permanent and never reused.** Prefixes in `GLOSSARY.md`; a closed ID
is cited as `Q-038 → D-095`.

**Status words** — LIVE · PROVISIONED · RESERVED · DEFERRED · OPEN · SPARE —
are defined once, `SPEC.md` §12, and used everywhere.

**Every file** carries `*Rev YYYY-MM-DD · owns: …*`, one H1, and a Contents
line past 200 lines.

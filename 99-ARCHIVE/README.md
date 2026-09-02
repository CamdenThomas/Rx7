# ARCHIVE

*Rev 2026-08-31 · owns: the index of superseded work. Nothing here is current. Kept because the reasoning is useful.*

| File | What | Superseded by |
|---|---|---|
| [`2026-08_superseded-C1-C7-connector-scheme.md`](Electrical/2026-08_superseded-C1-C7-connector-scheme.md) | Seven regional bulkhead connectors cut by geography | Four-leg design, D-029 |
| [`2026-08_rx7-pmu24-pin-plan-revA.html`](Electrical/2026-08_rx7-pmu24-pin-plan-revA.html) | Rev A pin plan, generated view | [`SPEC.md`](../02-PROJECTS/electrical-pmu/01-DESIGN/SPEC.md) Rev D and the generated [`PIN-MAP.md`](../02-PROJECTS/electrical-pmu/02-HARNESS/PIN-MAP.md) |
| [`2026-08_rx7-pmu-build-checklist-revA.html`](Electrical/2026-08_rx7-pmu-build-checklist-revA.html) | Rev A build checklist, generated view, three-digit step numbers | [`CHECKLIST.md`](../02-PROJECTS/electrical-pmu/04-BUILD/CHECKLIST.md) — phase.step numbering |
| [`2026-08_ROADMAP-superseded-by-STATUS.md`](Electrical/2026-08_ROADMAP-superseded-by-STATUS.md) | A snapshot of "what next" from early August | [`STATUS.md`](../02-PROJECTS/electrical-pmu/STATUS.md) — Audit 1, I-04 |
| [`2026-08_infotainment-options-considered.md`](Electrical/2026-08_infotainment-options-considered.md) | Hidden Bluetooth module, ANCS turn-by-turn, three Raspberry Pi architectures, offline OSM minimap | [`HEAD-UNIT.md`](Electrical/HEAD-UNIT.md) — a double-DIN head unit (D-051). The Pi minimap is buildable later if offline ever matters |
| [`2026-08_cluster-mockup-superseded-by-sim.html`](Electrical/2026-08_cluster-mockup-superseded-by-sim.html) | Hand-drawn HTML mockup of the cluster | The simulator runs the real firmware: [`firmware/icu_sim/`](../02-PROJECTS/electrical-pmu/03-MODULES/firmware/icu_sim/) — Audit 3, I-58 |
| [`2026-08-30_audit-4-findings.md`](Electrical/2026-08-30_audit-4-findings.md) | The 95-item Audit 4 list as written, before anything was fixed | [`AUDITS.md`](../02-PROJECTS/electrical-pmu/05-PROCESS/AUDITS.md) §4 — the same items with results |
| [`HEAD-UNIT.md`](Electrical/HEAD-UNIT.md) | Audio, maps, the double-DIN install — moved out of the project in the 2026-08-31 consolidation (D-200) | Still the reference when the head unit is chosen (D-149); wiring is already in the pin plan (O10, busbar F1/F5) |
| [`PARTS-CHANGES.md`](Electrical/PARTS-CHANGES.md) | What physically changes in the project — moved out 2026-08-31 (D-200) | The live facts it held are owned by `00-CAR/`, [`LOADS.md`](../02-PROJECTS/electrical-pmu/01-DESIGN/LOADS.md), [`TASKS-CAMDEN.md`](../02-PROJECTS/electrical-pmu/05-PROCESS/TASKS-CAMDEN.md) and [`BOM.md`](../02-PROJECTS/electrical-pmu/05-PROCESS/BOM.md) |
| [`DEFERRED-FEATURES.md`](Electrical/DEFERRED-FEATURES.md) | What is pre-wired and waiting, with add-later cost tables — moved out 2026-08-31 (D-200) | Live cavity status is the CSVs → [`CAVITY-STATE.md`](../02-PROJECTS/electrical-pmu/02-HARNESS/CAVITY-STATE.md); the cost tables remain useful here |
| [`2026-08-31_lighting-body/`](Electrical/2026-08-31_lighting-body/) | The lighting-body project's five process files (README, DECISIONS, OPEN, TASKS, BOM), as they stood when the project was dissolved back into electrical-pmu (D-201) | [`TAIL-LIGHTS.md`](Electrical/2026-08-31_lighting-body/TAIL-LIGHTS.md) + DECISIONS §Lighting + OPEN §8 + TASKS-CAMDEN §6 + BOM Wave 5 |

## Why the Rev A HTML files are wrong

Both were generated before the structural changes below. Do not read them for
anything except history — and never load them into the Claude Project as
knowledge (Audit 4, I-71).

| They say | Truth now |
|---|---|
| C1–C7 regional connectors | Four legs, 15 leg housings, 24 mated pairs (D-029, D-171) |
| 18 AWG signal wire | **16 AWG** — the 1.5 mm terminal is 14–17 AWG (D-027) |
| 16 relay sockets, 10 populated | **10 sockets, 5 populated** — K5–K8 moved to the sill and are provisioned empty (D-067, D-131) |
| Ionic S9H | Ionic S9, heated car-post version (D-002) |
| Cavity map "logical, unverified" | **Confirmed** from CAD and in the hand — 3 × 13, 2 large / 9 small / 2 large per row (D-045, D-134, D-139) |
| Load resistors for LED bulb-out | **None anywhere** — bulb-out dropped (D-047) |
| DCU deferred | **In full scope**, two nodes (D-075, D-083) |
| 4 AWG main feed | **2 AWG** (D-091) |
| Power windows wired live | **Manual windows**; the bridge is provisioned empty (D-131) |
| Three-digit checklist steps (001–129) | Phase.step numbering — mapping below |

## Rev A step numbers → current `CHECKLIST.md` steps

For anyone following an old citation. Rev A numbers ran 001–129 in one
sequence; the current checklist is phase.step.

| Rev A | Now | Rev A | Now |
|---|---|---|---|
| 001–002 binder, diagram | dropped — `01-REFERENCE/` holds the diagram | 063–076 battery backbone | 3.1–3.18 |
| 003–006 photograph, log hacks and grounds | 0.12, 0.13 | 077–082 plate, PMU, sockets, fuse block, busbars | 4.1–4.6 |
| 007 clamp every load | 0.1 (`T-014`) | 083 C1–C7 brackets | 4.7 — 15 leg receptacles + 4 drops |
| 008 pop-up stall | 0.2 | 084–088 stud feed, ground, relays, wake strip, constant bus | 4.8–4.13 |
| 009 cavity geometry | closed — D-134, D-139 | 089–096 terminate the 39-pin, route, cap, test, label | 4.14–4.20 |
| 010–012 spreadsheet, cross-checks | `pmu_pins.csv` + `tools/check.py`, Phase 0 gate | 097–099 bench-power the panel | dropped — D-146; powered check is 6.3 |
| 013–014 ladder values | `LADDERS.md`; in-car verification 6.4 (D-142) | 100 photograph the panel | 4.24 |
| 015–017 routes, cut list, connector BOM | 0.11, 0.15, 0.16 | 101–110 build a leg | 5.1–5.10 |
| 018–019 panel 1:1, mock-up | 0.20, 0.21 | 111–113 mount, feed, power up disabled | 6.1–6.3 |
| 020–023 schematics | `SCHEMATICS.md` | 114 install L3, verify inputs | 6.4 |
| 024 freeze | 0.22 | 115 install remaining legs | 6.5; sill node 6.6 |
| 025–030 orders, inventory | Gate 0 and 1.1–1.9 | 116 migration order | `MIGRATION-LOG.md` |
| 031–035 coupons, practice, labels | 1.10–1.14 | 117–123 per-circuit loop | `MIGRATION-LOG.md` loop steps 1–7 |
| 036–039 plywood board, pigtail | dropped — D-141, D-147 | 124 car drives every day | 6.7 |
| 040–046 CAN1 termination, client, project file, bulb, short, PWM | 2.2–2.9 | 125–127 function check, sheet, week's driving | 6.8 and the Phase 7 gate |
| 047–050 physical ladders on the bench | dropped — verified in the car, 6.4 (D-142) | 128–129 harness out, boarded | Phase 7 |
| 051–062 logic, thresholds, logging, save, dry run | 2.10–2.21 | | |

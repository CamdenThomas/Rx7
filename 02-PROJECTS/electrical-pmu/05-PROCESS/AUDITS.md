# AUDITS — the record

*Rev 2026-08-31 · owns: every documentation audit of this project — findings (I-###), what was done about each, and the standing rules that came out of them. [`ASSISTANT.md`](../../../ASSISTANT.md) holds the rules themselves; this file holds why they exist.*

Four audits so far. Each was triggered by the same two conditions — a major
scope change, or a file past ~250 lines with more than one UPDATE section —
and each found the same root problem in a new form: **appending is cheap and
safe, and it produces documents that are wrong at the top and right at the
bottom.** Trigger the next one on the same conditions, or when
`tools/check.py` stops being clean.

## Contents

1. Audit 1 — the first tree read (I-01 … I-31) · 2. Audit 2 — accretion and
scope (I-32 … I-51) · 3. Audit 3 — after the ICU firmware (I-52 … I-70) ·
4. Audit 4 — representation and organisation, 2026-08-30 (I-71 … I-165) ·
5. Standing rules

---

## 1 · Audit 1 — the first tree read, 2026-08

From a two-pass read of the whole tree. **All 28 items closed**, plus three
that surfaced during the folder reorganisation.

| Group | Items | Result |
|---|---|---|
| **Contradictions** | I-01, I-03, I-07 | [`vehicle.md`](../../../00-CAR/vehicle.md) fuel pump → Carter P4070; `01-REFERENCE/README.md` rebuilt; the TASKS reorder rule corrected to match practice |
| **Stale files** | I-02, I-04, I-05, I-06 | [`dash.md`](../02-HARNESS/dash.md) rewritten; `ROADMAP.md` archived and replaced by [`STATUS.md`](../STATUS.md); stale `[V-0xx] pending` cleared from leg files; `legs/README` rebuilt |
| **Duplication** | I-08 – I-11 | Owners assigned: LOADS owns current, PIN-MAP owns cavities, MIGRATION-LOG owns the migration order, CHECKLIST owns sequence |
| **Missing files** | I-12 – I-22 | STATUS · GLOSSARY · SAFETY · CAN-MESSAGES · MIGRATION-LOG · CUT-LIST · LOGS created; DECISIONS index; wire colour table in SPEC §2 |
| **Polish** | I-23 – I-28 | `*Rev YYYY-MM*` stamps; factory-file banner; [`vehicle.md`](../../../00-CAR/vehicle.md) purchases; service history; routing rule **decisions → OPEN, actions → TASKS**; handover path in STATUS |
| **Reorganisation** | I-29 – I-31 | Numbered folders `01-DESIGN` … `05-PROCESS`; session-opening paths corrected in [`ASSISTANT.md`](../../../ASSISTANT.md) §0; `04-SUBSYSTEMS/` established as the home for self-contained designs |

I-29 (relative links after the reorganisation) was carried "fix on next touch"
through two more audits and finally closed by Audit 4's link sweep.

## 2 · Audit 2 — accretion and scope, 2026-08

From reading [`PARTS-CHANGES.md`](../../../99-ARCHIVE/PARTS-CHANGES.md) and `INFOTAINMENT.md` end to end; the findings
generalised to most of the project. **I-32 … I-51 closed.**

**The root problem — append-only accretion.** [`PARTS-CHANGES.md`](../../../99-ARCHIVE/PARTS-CHANGES.md) opened with a
full LED conversion table that four UPDATE sections later turned out to belong
to another project. `INFOTAINMENT.md` spent 202 lines on Bluetooth modules and
three Pi architectures before §9 said the answer was a head unit. A reader
building a model top-down built the wrong one.

| Group | Items | Result |
|---|---|---|
| **Accretion** | I-32 – I-34 | [`PARTS-CHANGES.md`](../../../99-ARCHIVE/PARTS-CHANGES.md) and `INFOTAINMENT.md` rewritten clean; every file audited for UPDATE-contradicts-above |
| **Scope leakage** | I-35 – I-38 | Lighting out of PARTS-CHANGES · INFOTAINMENT → `04-SUBSYSTEMS/HEAD-UNIT.md` · dead paths archived as `99-ARCHIVE/2026-08_infotainment-options-considered.md` · PARTS-CHANGES owns *what changes*, DEFERRED-FEATURES owns *what is pre-wired and waiting* |
| **Factual errors** | I-39 – I-42 | Window motors removed (D-131), blower marked dead (K-023), broken TAIL-LIGHTS link fixed, headlamp claim flagged `V-066` |
| **Representation** | I-43 – I-47 | Standard header, supersession banners, contents blocks, closed-question sweep |
| **Structure** | I-48 – I-51 | `04-BUILD/` stays one folder; [`PMU-CONFIG.md`](../01-DESIGN/PMU-CONFIG.md) and [`PANEL-LAYOUT.md`](../01-DESIGN/PANEL-LAYOUT.md) stay in `01-DESIGN/` (they *describe the thing*); `can_map.h` stays with the firmware; `lighting-body/DECISIONS.md` created with inherited D-107/110/111 keeping their IDs and local decisions as `L-###` |

The rule it produced: **read a file before appending to it** (R1).

## 3 · Audit 3 — after the ICU firmware, 2026-08

The project gained working C++ firmware and a desktop simulator, and the
documentation had not caught up. **I-52 … I-70 closed**, two deferred.

**The root problem — code became a source of truth, silently.** `cluster_core.h`
defined the palette, every layout constant, the icon set, unit conversions and
fault rendering, and none of it was in [`DECISIONS.md`](DECISIONS.md).

| Item | Result |
|---|---|
| I-52 | **D-151 … D-158** record every cluster design decision that existed only in code |
| I-53 | README conventions table names `cluster_core.h` and `stats.h` as owners |
| I-54 – I-57 | README documents `firmware/`; `can_map.h` path corrected; decision range corrected; **`firmware/README.md` created** with the w64devkit build steps and simulator controls |
| I-58 | `cluster-mockup.html` archived |
| I-59 – I-61 | [`CLUSTER-DESIGN.md`](../03-MODULES/CLUSTER-DESIGN.md) retitled forward scope; [`DCU-CLUSTER.md`](../03-MODULES/DCU-CLUSTER.md) display analysis marked settled; BENCH-BRINGUP Stages 4–5 marked done and absorbed |
| I-62 – I-63 | Q-035, Q-041, Q-056, Q-057 closed; `V-058` elevated into **Q-060 panel selection** |
| I-64 | **D-159** — the display does not cross the harness; DP-ICU is correctly sized |
| I-65 – I-68 | **D-160** `stats.h` thresholds recorded (three flagged `V-070`–`V-072`) · **D-162** volatile-only · **D-163** `stats.h` owns automated figures, [`LOGS.md`](../04-BUILD/LOGS.md) manual ones · **D-161** IMU class and axis convention |
| I-69 | Deferred — an archived render of the agreed cluster needs a screenshot only Camden can take (`icu_sim/sim.exe`, `+` for 2×, save to `03-MODULES/`) |
| I-70 | Closed by Audit 4's leg-file rewrites |

The rule it produced: **when code becomes the source of truth for something,
say so in the index and record the decisions that shaped it** (R6). Forward
work identified at its closeout (F/H/X/Z items) lives in [`FORWARD-WORK.md`](FORWARD-WORK.md).

## 4 · Audit 4 — representation and organisation, 2026-08-30

A full read of `02-PROJECTS/electrical-pmu/` and [`ASSISTANT.md`](../../../ASSISTANT.md) — 95 findings
in eleven sections, the original list archived as
`../../../99-ARCHIVE/2026-08-30_audit-4-findings.md`. **The root problems:** the
same fact owned by three files that had already drifted; append-only accretion
back in eleven files despite R1/R2; 60 closed IDs cited as live; no
machine-readable source for the pin data; no checks. **Structural results:**
single-source CSV tables with a generator (`tools/gen.py`), an ID registry
(`tools/registry.py`), a drift checker (`tools/check.py`), a CHANGELOG, this
file, [`FORWARD-WORK.md`](FORWARD-WORK.md), and [`ASSISTANT.md`](../../../ASSISTANT.md) reduced to rules.

**85 of 95 closed in the same pass.** Two are Camden's (I-72 project
instructions, I-153 git commit), one is half his (I-156 binaries in git
history), three are partial, four were ruled no-change.

### A · The Claude Project and ASSISTANT.md

- [x] **I-71 · P1** · The Claude Project's knowledge base is the superseded Rev A — Claude Project refreshed with the current STATUS, README, GLOSSARY, SPEC, OPEN, ASSISTANT; the two Rev A HTML pages removed
- [ ] **I-72 · P1** · The project instructions don't say to read [`ASSISTANT.md`](../../../ASSISTANT.md) — **Camden** — Project instructions must say: read [`ASSISTANT.md`](../../../ASSISTANT.md) first, then [`STATUS.md`](../STATUS.md). Only Camden can edit them
- [x] **I-73 · P3** · No [`CLAUDE.md`](../../../CLAUDE.md) — Root [`CLAUDE.md`](../../../CLAUDE.md) created — points at [`ASSISTANT.md`](../../../ASSISTANT.md)
- [x] **I-74 · P2** · [`ASSISTANT.md`](../../../ASSISTANT.md) says "never produce artifacts — no HTML" but the project's only artifacts are HTML — Rule reworded: file edits are the default; artifacts only when asked by name, and never as a source of truth
- [x] **I-75 · P1** · Sections 8–12 are audit logs appended to an operating manual — §8–§12 moved here; [`ASSISTANT.md`](../../../ASSISTANT.md) is rules only
- [x] **I-76 · P1** · §0 was corrected in place but I-30 still sits at line 371 saying §0 is wrong — I-30 retired with the move; §0 is correct
- [x] **I-77 · P2** · R1–R6 are defined in three places — R1–R6 defined once, in [`ASSISTANT.md`](../../../ASSISTANT.md); this file and the README point at them
- [x] **I-78 · P2** · The mode table (§0) and the session protocol in the root `README.md` §"Session protocol" are the same content in two places — Root README keeps structure and conventions only; the session protocol lives in [`ASSISTANT.md`](../../../ASSISTANT.md)
- [x] **I-79 · P2** · I-29 (relative links) is marked "fix on next touch" in three files — Every relative link swept and made clickable (I-108); the note is gone from all three files
- [x] **I-80 · P4** · [`ASSISTANT.md`](../../../ASSISTANT.md) has no header of its own — Header added
- [x] **I-81 · P4** · §2 says [`TASKS-CAMDEN.md`](TASKS-CAMDEN.md) — "reorder and regroup freely" — Wording fixed
- [x] **I-82 · P4** · The GLOSSARY says I-## lives in "[`ASSISTANT.md`](../../../ASSISTANT.md) §8" — GLOSSARY points at `AUDITS.md`

### B · Where the truth lives now

- [x] **I-83 · P1** · `02-HARNESS/PIN-MAP.md` is "authoritative cavity assignments" and describes a design that no longer exists — [`PIN-MAP.md`](../02-HARNESS/PIN-MAP.md) regenerated from `pmu_pins.csv` + `connectors.csv` — one current table
- [x] **I-84 · P1** · SPEC and PIN-MAP disagree about which terminal the 15 A / 7 A outputs use — One terminal table in [`SPEC.md`](../01-DESIGN/SPEC.md) §2; PIN-MAP carries the same sizes from the CSV
- [x] **I-85 · P1** · `01-DESIGN/LOADS.md` is "the only source for current figures" and is wrong top-to-bottom — [`LOADS.md`](../01-DESIGN/LOADS.md) rewritten: method, incandescent design figures, LED appendix

### C · Duplication that has drifted

- [x] **I-86 · P2** · Current figures now have three owners, not one — One source — the CSV; LOADS holds method, CHANNEL-SCHEDULE and `channels.h` are generated
- [x] **I-87 · P2** · The measured readings themselves live in three places — Readings recorded once in `pmu_pins.csv`; METER-SESSION shows them only as done-markers
- [x] **I-88 · P2** · Migration order is restated in [`CHECKLIST.md`](../04-BUILD/CHECKLIST.md) Phase 6 (18 items) although [`MIGRATION-LOG.md`](../04-BUILD/MIGRATION-LOG.md) "owns" it (26 rows) — CHECKLIST Phase 6 defers to [`MIGRATION-LOG.md`](../04-BUILD/MIGRATION-LOG.md)
- [x] **I-89 · P2** · [`CONNECTORS.md`](../02-HARNESS/CONNECTORS.md) contains three master connector lists — [`CONNECTORS.md`](../02-HARNESS/CONNECTORS.md) carries one generated housing table
- [x] **I-90 · P2** · Total mated-pair count: [`CONNECTORS.md`](../02-HARNESS/CONNECTORS.md) says 20, [`PIN-MAP.md`](../02-HARNESS/PIN-MAP.md) and `02-HARNESS/README.md` say 23 — Defined once in PIN-MAP: 15 leg housings, 24 mated pairs; every file updated
- [x] **I-91 · P2** · The CAN message map exists four times — One finalised map in [`CAN-MESSAGES.md`](../03-MODULES/CAN-MESSAGES.md); draft removed from DCU-CLUSTER; three `can_map.h` copies identical and checked
- [x] **I-92 · P2** · [`PMU-CONFIG.md`](../01-DESIGN/PMU-CONFIG.md) is two complete documents concatenated — [`PMU-CONFIG.md`](../01-DESIGN/PMU-CONFIG.md) is one document
- [x] **I-93 · P2** · [`SCHEMATICS.md`](../01-DESIGN/SCHEMATICS.md) shows every sub-circuit twice — [`SCHEMATICS.md`](../01-DESIGN/SCHEMATICS.md) rewritten current-state
- [x] **I-94 · P2** · `02-HARNESS/README.md` "Elsewhere" links `../LOADS.md` and `../SCHEMATICS.md` — Links fixed; leg counts from the CSV

### D · Accretion

- [x] **I-95 · P1** · [`STATUS.md`](../STATUS.md) contradicts itself — [`STATUS.md`](../STATUS.md) rewritten as one dashboard
- [x] **I-96 · P1** · [`STATUS.md`](../STATUS.md) "Open decisions" omits three of the five open questions — Open decisions list complete (Q-014, Q-028, Q-060–Q-065)
- [x] **I-97 · P1** · Stage 4 and 5 status is stated four ways — Stages 1–5 done, stated once in BENCH-BRINGUP and echoed
- [x] **I-98 · P1** · Whether the spare housings have arrived is stated four ways — Housings: ordered, inbound, `T-045` on arrival — stated the same way everywhere
- [x] **I-99 · P1** · `BUY-LIST.md` (since absorbed into [`BOM.md`](BOM.md) §9, D-200) "STATUS — bench kit PURCHASED" (line 263) marks 120 Ω resistors, E24 assortment, breadboards, jumpers, board materials and the rotary switch as Bought — BUY-LIST rewritten as a record per D-140
- [x] **I-100 · P1** · [`CLUSTER-DESIGN.md`](../03-MODULES/CLUSTER-DESIGN.md) banner says the multi-page architecture, diagnostics page and trip page "do not exist yet" — CLUSTER-DESIGN banner corrected
- [x] **I-101 · P1** · [`CHECKLIST.md`](../04-BUILD/CHECKLIST.md) still builds the power windows — Windows provisioned only (D-131) throughout CHECKLIST; 0.3 dropped
- [x] **I-102 · P1** · [`PARTS-CHANGES.md`](../../../99-ARCHIVE/PARTS-CHANGES.md) §3 "Cluster display — Format undecided `[Q-037]`" — PARTS-CHANGES cluster row → D-150/D-168
- [ ] **I-103 · P2** · [`DEFERRED-FEATURES.md`](../../../99-ARCHIVE/DEFERRED-FEATURES.md) is the model for the tree — *no change* — DEFERRED-FEATURES kept as the pattern; headers everywhere follow it

### E · Cross-references and IDs

- [x] **I-104 · P1** · 35 Q-IDs and 25 V-IDs are cited as live in file bodies that [`OPEN.md`](OPEN.md) does not hold — Sweep done; closed IDs cited as `Q-038 → D-095`; `check.py` C5 catches bare closed IDs
- [x] **I-105 · P1** · Task IDs were renumbered (D-043) and the old numbers survive in reference files — horn.md T-002 → T-001; OEM-RECORD pointer note for T-017
- [x] **I-106 · P1** · The old three-digit Checklist step numbers are cited in 11 files — All three-digit step numbers mapped to phase.step
- [x] **I-107 · P2** · Path references that point at the pre-reorganisation layout — Paths corrected
- [x] **I-108 · P2** · There is not one clickable link in the tree — Every file mention linkified; `check.py` C4 checks link targets exist
- [x] **I-109 · P2** · [`DECISIONS.md`](DECISIONS.md) index covers D-001…D-105; the file runs to D-167 — Index extended to D-172
- [x] **I-110 · P2** · [`GLOSSARY.md`](../01-DESIGN/GLOSSARY.md) is missing five ID schemes now in use — GLOSSARY covers D/Q/A/V/T/K/M/P/I/L/R/TL/F/H/X/Z and the status words
- [x] **I-111 · P4** · [`SPEC.md`](../01-DESIGN/SPEC.md) §1 "All 16 analog inputs are allocated. There is no spare" — SPEC §1 wording matches §7

### F · Facts that disagree

- [x] **I-112 · P1** · Power windows — Windows: manual, bridge PROVISIONED — one status everywhere
- [x] **I-113 · P1** · Main feed gauge — 2 AWG everywhere; D-061/D-064 marked amended
- [x] **I-114 · P1** · Start relay location — K9 inner fender everywhere (D-148)
- [x] **I-115 · P1** · CAN transceivers — TCAN in the car, SN65HVD230 on the bench — stated as such everywhere
- [x] **I-116 · P1** · LED figures in the canonical files — Incandescent baseline in the canonical files; LED in the LOADS appendix
- [x] **I-117 · P1** · Display interface decision is recorded backwards — D-168 records SPI dirty-rectangle; D-150 marked superseded in part
- [x] **I-118 · P1** · The PMU logic needs an RPM it cannot see — Q-063, Q-064, Q-065 packets; PMU-CONFIG cites them instead of presenting the gaps as settled
- [x] **I-119 · P2** · Phase 2A effort is 35–55 hrs ([`TASKS-CAMDEN.md`](TASKS-CAMDEN.md)), 25–40 ([`CHECKLIST.md`](../04-BUILD/CHECKLIST.md), [`STATUS.md`](../STATUS.md) phase table), 12–20 ([`STATUS.md`](../STATUS.md) assessment) — Phase 2A = 12–20 hrs everywhere (D-166)
- [x] **I-120 · P2** · Money — One money table in [`BOM.md`](BOM.md) §1; STATUS and CHECKLIST point at it
- [x] **I-121 · P2** · [`TASKS-CAMDEN.md`](TASKS-CAMDEN.md) carries lighting-body tasks — T-034–T-037 moved to `lighting-body/TASKS.md`
- [x] **I-122 · P2** · [`OPEN.md`](OPEN.md) holds two answered questions — Q-058 → D-169, Q-059 → D-170, V-041 → D-083 removed; V-053 reworded
- [x] **I-123 · P2** · Terminal wire range for 1.5 mm is 13–17 AWG in [`SPEC.md`](../01-DESIGN/SPEC.md) §2 and D-027/D-046, and 14–17 AWG in `BUY-LIST.md` (now [`BOM.md`](BOM.md) §9), [`BENCH-KIT.md`](../04-BUILD/BENCH-KIT.md) — 14–17 AWG with the pinout revision in SPEC §2
- [x] **I-124 · P4** · Teensy count — Two nodes, three boards — stated once in DCU-CLUSTER

### G · DECISIONS.md

- [x] **I-125 · P1** · Superseded decisions are not marked at the old entry — 19 supersede/amend marks added under the old entries
- [x] **I-126 · P2** · The topic index stops at D-105 — Index rows added through D-172
- [ ] **I-127 · P2** · Entries are not dated — *partial* — New entries from D-168 carry a date; earlier entries keep their round headings (all 2026-08)
- [ ] **I-128 · P2** · One ID, several decisions — *no change* — Stands — splitting past multi-decision entries would break citations; new entries are one decision each
- [ ] **I-129 · P2** · Decisions belonging to other projects — *no change* — Inherited lighting decisions keep their D-IDs per the closeout ruling (I-51); lighting-body has its own log
- [x] **I-130 · P4** · The stated format is not used — Format line replaced with the format actually used
- [ ] **I-131 · P4** · D-136 through D-139 are four entries for one fact — *no change* — Left as history; D-139 is the entry to cite

### H · Representation

- [x] **I-132 · P2** · 48 of 66 files have no rev/owner header — Every file has a `*Rev … · owns: …*` header; `check.py` H1 enforces it
- [x] **I-133 · P2** · Chat-export citation markup embedded in five files — All chat-export citation tags removed; `check.py` C1
- [x] **I-134 · P2** · A user reply is embedded inline in a spec — Camden's Q-058 answer became D-169; packets carry answers only until recorded
- [x] **I-135 · P2** · Heading hierarchy is inconsistent within files — One H1 per file, H2 sections; `check.py` H2
- [x] **I-136 · P3** · No table of contents in any file over 200 lines — `## Contents` in every file over 200 lines; `check.py` H3
- [x] **I-137 · P3** · No supersession banners inside files — No stacked UPDATE sections remain — files are current-state with marked appendices
- [x] **I-138 · P4** · [`CHECKLIST.md`](../04-BUILD/CHECKLIST.md) numbering has gaps — Gaps annotated (0.3, 4.21–4.23, 5.12) with the decision that dropped them
- [ ] **I-139 · P4** · Wide tables — *partial* — Widest tables split (PIN-MAP per housing, SPEC per size); some remain wide by nature
- [x] **I-140 · P4** · `00-CAR/known-issues.md` K-numbering — One K table in [`known-issues.md`](../../../00-CAR/known-issues.md)
- [x] **I-141 · P4** · [`TAIL-LIGHTS.md`](../01-DESIGN/TAIL-LIGHTS.md) §6 lists Q-046 and Q-047 as open — TAIL-LIGHTS cites Q-046/Q-047 as closed

### I · Missing structure

- [x] **I-142 · P1** · The two READMEs are stale indexes — Both READMEs rebuilt with the correct tree
- [x] **I-143 · P1** · `99-ARCHIVE/README.md` indexes 3 of 6 archived files — All six archived files indexed
- [x] **I-144 · P3** · The pin/channel/cavity data has no single machine-readable source — `02-HARNESS/data/*.csv` + `tools/gen.py` generate PIN-MAP, CAVITY-STATE, CHANNEL-SCHEDULE, CUT-LIST, CONNECTORS, `channels.h`, the leg SVGs
- [x] **I-145 · P3** · No ID registry — `tools/registry.py` → [`ID-REGISTRY.md`](ID-REGISTRY.md) + `ids.json`
- [x] **I-146 · P3** · No checks — `tools/check.py` — headers, TOCs, cite markup, old step numbers, paths, links, bare closed IDs, `can_map.h` copies, generator drift
- [x] **I-147 · P3** · `01-REFERENCE/README.md` breaks its own rule — 01-REFERENCE README indexes the Part Dates PDF; V-062 cited closed
- [x] **I-148 · P3** · `factory-circuits/README.md` has two Status tables — One status table, correct paths, V-023 closed
- [x] **I-149 · P3** · `lighting-body/` has decisions and no tasks, questions or status — `lighting-body/OPEN.md`, [`TASKS.md`](../../../99-ARCHIVE/2026-08-31_lighting-body/TASKS.md), [`BOM.md`](BOM.md) created
- [x] **I-150 · P3** · `00-CAR/` has no README — `00-CAR/README.md` created
- [x] **I-151 · P4** · Scope leakage in [`BOM.md`](BOM.md) — Lighting money in `lighting-body/BOM.md`
- [ ] **I-152 · P4** · [`PANEL-LAYOUT.md`](../01-DESIGN/PANEL-LAYOUT.md) and [`CUT-LIST.md`](../04-BUILD/CUT-LIST.md) are templates waiting on T-007 / T-008 — *no change* — Templates stay — their shape is the deliverable until T-007/T-008 fill them

### J · Firmware and git

- [ ] **I-153 · P1** · Nothing since 2026-08-28 is committed — **Camden** — `git add -A && git commit` on Camden's machine; consider LFS for the two large PDFs
- [x] **I-154 · P1** · Three identical copies of `can_map.h` — `icu/can_map.h` declared master; `check.py` F1 fails if the copies differ
- [x] **I-155 · P2** · `firmware/README.md` layout omits `tests/` and `cluster_ render_test/` — firmware README lists every folder
- [ ] **I-156 · P2** · Built binaries are in the tree and in git — *partial* — `.gitignore` added (`*.exe`, `.idea/`); removing the committed binaries from history is Camden's
- [x] **I-157 · P2** · `channels.h` is the third copy of the amp table — `channels.h` generated from the CSV
- [x] **I-158 · P3** · No build script for the test suite — `tests/run.bat`
- [x] **I-159 · P4** · `firmware/README.md` hardcodes `C:\Users\Camden Thomas\ Downloads\w64devkit\` — README uses `C:\w64devkit`, matching `build.bat`
- [x] **I-160 · P4** · Firmware has no version — `ICU_FW_VERSION` 0.3.0-dev, printed at boot, logged in LOGS

### K · Generated artefacts

- [x] **I-161 · P3** · A wiring diagram set — Six leg SVGs in `02-HARNESS/diagrams/`, generated
- [x] **I-162 · P3** · One architecture picture — `02-HARNESS/diagrams/architecture.svg`
- [x] **I-163 · P3** · A "state of every cavity" export — `02-HARNESS/CAVITY-STATE.md`, generated
- [x] **I-164 · P3** · A CHANGELOG — `05-PROCESS/CHANGELOG.md`; [`ASSISTANT.md`](../../../ASSISTANT.md) §7 appends to it at every close
- [x] **I-165 · P4** · [`STATUS.md`](../STATUS.md) "If you have been away a year" names five files — Handover path in STATUS lists the files that exist

## 5 · Standing rules

Defined in [`ASSISTANT.md`](../../../ASSISTANT.md) §R; listed here only by origin.

| Rule | Came from |
|---|---|
| R1 · Read a file before appending to it | Audit 2, I-32 – I-42 |
| R2 · A document must be correct top to bottom | Audit 2 |
| R3 · One owner per fact, declared in the header | Audit 1, I-08 – I-11 |
| R4 · Scope belongs to the project that owns the work | Audit 2, I-35 – I-38 |
| R5 · Every file gets a header | Audit 2, I-43; enforced by Audit 4's `check.py` |
| R6 · When code owns a fact, say so and record the decisions | Audit 3 |
| R7 · Cite a closed ID as `Q-038 → D-095`, never bare | Audit 4, I-104 |
| R8 · Generated blocks are never edited by hand — edit the CSV and run `gen.py` | Audit 4, I-144 |

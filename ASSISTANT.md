# ASSISTANT.md — operating instructions for Claude

Read this first, every session. It replaces remembered context. If anything here
conflicts with a habit, this file wins.

---

## 0 · Session opening

At session start, read **only**:
1. This file.
2. `02-PROJECTS/electrical-pmu/STATUS.md` — where the project is.
3. The specific file the task touches.
4. `07-PROCESS/OPEN.md` if the task touches an unresolved item.

Project files live in numbered folders: `01-DESIGN` `02-HARNESS` `03-MODULES`
`04-SUBSYSTEMS` `05-BUILD` `06-PROCUREMENT` `07-PROCESS`. The project
`README.md` is the map.

Do **not** read the whole tree. Do **not** search past conversations for
anything already written to a file. If it's in a file, it's true; cite the file
and move on.

Camden names the mode. If he doesn't, ask once, in one line:
`DECIDE / GENERATE / AUDIT / BUILD?`

| Mode     | Claude does                                          | Camden does                       |
|----------|------------------------------------------------------|-----------------------------------|
| DECIDE   | Presents 10–20 decision packets, defaults pre-chosen | Replies with a yes/no/change list |
| GENERATE | Produces one tedious artifact for a named section    | Reviews the output afterward      |
| AUDIT    | Attacks SPEC.md for contradictions, orphans, gaps    | Reads findings, rules on fixes    |
| BUILD    | Updates files from measured shop data                | Supplies the numbers              |

---

## 1 · Credit rules — non-negotiable

**Never re-derive.** Anything in a file is settled. Re-researching a price, a
pinout, or a past decision is a wasted credit and a correctness risk.

**Never re-read chats.** The files are the memory. Conversation search is only
for something explicitly not in a file.

**Never rewrite a file to change part of it.** Use `edit_block` with the minimum
unique context. Full `write_file` is only for: a brand-new file, or a rewrite
Camden explicitly asks for.

**Never regenerate a document to add one row.** Append or edit in place.

**Never produce artifacts.** No HTML, no canvas documents, unless Camden asks
for a printable view by name. Default output is a file edit plus a short chat
summary.

**Never restate file contents in chat.** After an edit, report the diff, not the
document. Ten lines maximum.

**Batch tool calls.** Reading four files takes one `read_multiple_files` call,
not four. Ten small edits to one file is still ten `edit_block` calls — that's
correct and cheaper than one rewrite.

**One search maximum per unknown fact.** If a search doesn't resolve it, log it
as `[VERIFY]` and move on. Do not chain searches hunting for certainty.

---

## 2 · Markdown edit process

Every file change follows this order:

1. **Read the target section only.** Use `read_file` with `offset`/`length`, or
   read the whole file only if it's under ~60 lines.
2. **Edit with `edit_block`.** Include 1–3 lines of context, exact whitespace.
3. **Log it.** If the edit reflects a decision, append to `DECISIONS.md` with a
   new ID. If it creates an unknown, append to `OPEN.md`.
4. **Report the diff.** Ten lines. What changed, what ID it got, what it opened.

Rules for the files themselves:

- `SPEC.md` — current state only. No history, no rationale, no alternatives.
- `DECISIONS.md` — append-only. Never edit or delete a past entry. Reverse by
  adding a new one and marking the old `SUPERSEDED BY D-0xx`.
- `OPEN.md` — items are removed only when resolved. Resolution means a new
  `DECISIONS.md` entry or a verified fact written into `SPEC.md`.
- `TASKS-CAMDEN.md` — physical work only Camden can do. **Reorder and regroup
  freely** to keep it usable; never renumber a `T-###`.
- IDs are permanent and never reused: `D-###` decision, `Q-###` question,
  `A-###` assumption, `V-###` verify, `T-###` Camden task, `K-###` known issue,
  `M-###` modification.

---

## 3 · Delegation — who does what

**Claude's work.** Anything that is reading, writing, calculating, cross-checking
or enumerating. Never hand these back to Camden:

- Pin schedules, cut lists, connector BOMs, label lists
- Resistor ladder math, ADC value tables, fuse sizing arithmetic
- Cross-checks: every cavity has a destination, every relay has a coil source
  and a load path, no circuit appears twice, no load lacks a fuse
- Schematic layouts and drawings
- Restating Camden's own decisions back in auditable form
- Arguing against a decision to test whether it holds
- Finding contradictions between documents written weeks apart

**Camden's work.** Only these. If a task is on this list, do not attempt it —
write it to `TASKS-CAMDEN.md` with a `T-###` and continue:

- Anything requiring hands on the car or a measurement from it
- Anything requiring eyes on a physical part (cavity geometry, clearances, fit)
- Ordering, spending money, committing to lead times
- Final sign-off on any decision that changes wiring, BOM, or cost
- Judgment about his own priorities, budget, and schedule

**The test:** if Claude could be wrong in a way Camden couldn't catch from the
document alone, it's Camden's task.

---

## 4 · Small decisions — decide, log, keep going

A decision is **small** if reversing it costs nothing but a file edit.

Claude makes small decisions unilaterally. Do not ask. The process is:

1. Pick the sensible default.
2. Append to `DECISIONS.md` with the next `D-###` and a one-line reason.
3. Keep working.
4. Mention it in the closing diff, one line.

If Claude had to guess rather than reason, it's an **assumption**, not a
decision: append to `OPEN.md` under `[ASSUMED]` with an `A-###`, keep going, and
surface the whole batch at the end. Never stop mid-task to ask about one.

---

## 5 · Big decisions — stop, package, hand over

A decision is **big** if it changes wiring, the BOM, cost, schedule, or forecloses
a future option.

Claude does **not** make these. The process is:

1. Stop that thread. Continue with everything else.
2. Write a decision packet to `OPEN.md` under `[DECIDE]` with a `Q-###`.
3. Add a matching line to `TASKS-CAMDEN.md` if it needs anything physical first.
4. Present the packet in chat in exactly this shape:

```
Q-0xx · <one-line title>
Recommend:  <the call Claude would make>
Because:    <one line>
Flip it if: <the single condition that changes the answer>
Costs:      <dollars / pins / hours, if any>
```

Four lines. Camden replies `yes` / `no, do X`. Nothing more should be required
of him to rule on it.

Never present a big decision as an open-ended question. Never present more than
20 packets in one batch.

---

## 6 · Verification discipline

The moment Claude writes a **part number, price, dimension, cavity position,
current rating, or claim that two connectors mate**, it gets a `[V-###]` tag in
`OPEN.md` in the same edit. No exceptions.

Treat every unverified part number as a placeholder, not a fact. Never let one
reach the BOM's ordered column.

Known-unreliable territory — flag automatically:
- Part numbers and connector mating
- Prices, stock, lead times
- Physical geometry and clearances
- Anything about this specific car Camden hasn't stated

---

## 7 · Session close

Camden says "give me the diff." Claude outputs, in ten lines or fewer:

```
CHANGED   files touched, sections
LOGGED    D-### decisions added
OPENED    new Q-### / A-### / V-### / T-###
CLOSED    items removed from OPEN.md
NEXT      recommended mode + target for next session
```

Then write nothing else.

---

# 8 · CLAUDE'S TASK LIST — improvements to this directory

From a two-pass read of the whole tree, 2026-08. **Work top-down.** Tick and
date each line as it's done. Add to it whenever drift is spotted.

## P1 · Contradictions — a reader would be actively misled

- [ ] **I-01 · `00-CAR/vehicle.md` says the fuel pump is a Holley Gold Flow.**
  `modifications.md` M-002 says Carter P4070. Two files in the same folder
  disagree about a current part. Fix vehicle.md.
- [ ] **I-02 · `legs/dash.md` is the most stale file in the project.** It still
  specifies AMPSEAL 35 (superseded by D-070), lists the cigarette lighter
  (deleted, D-095), shows Q-018/Q-020 as unresolved, treats the DCU as deferred
  (superseded by D-075), and carries a whole "Future direction" section written
  against D-006. Rewrite against PIN-MAP and CONNECTORS.
- [ ] **I-03 · `01-REFERENCE/README.md` references `1983RX7WiringDiagram.pdf`.**
  The file is `1982…` and it moved into `factory-circuits/`. Four "wanted" items
  are already obtained. `TS-ICT-T-C-CAT-2018.pdf` is unindexed.
- [ ] **I-04 · `ROADMAP.md` is a snapshot of a moment that has passed.** T-016 is
  cancelled, the $290 order is spent, transceivers are SN65HVD230 not TCAN,
  Q-033 is answered. Either refresh it or fold it into CHECKLIST.
- [ ] **I-05 · Leg files still list deleted subsystems as `[V-0xx] pending`** —
  cruise, power antenna, rear wiper, headlight cleaner. All confirmed gone
  (D-097).
- [ ] **I-06 · `legs/README.md` device counts are wrong** and it doesn't mention
  `sill-node.md` or `PIN-MAP.md` in its file table.
- [ ] **I-07 · `ASSISTANT.md` §2 says "TASKS-CAMDEN.md — append, never reorder."**
  It has been fully rewritten twice, for good reasons. Fix the rule to match
  practice: reorder freely, but never renumber.

## P2 · Duplication that will drift

- [ ] **I-08 · Current estimates live in three places** — `LOADS.md`, the "Est. A"
  columns in `SPEC.md`, and the leg files. Three copies of the same number.
  **Fix:** LOADS.md is the only source. SPEC and legs link to it, no numbers.
- [ ] **I-09 · Connector assignments live in three places** — `CONNECTORS.md`,
  `PIN-MAP.md`, and each leg file. Already drifted (I-02). **Fix:** PIN-MAP owns
  cavity assignments; leg files describe *why* and link.
- [ ] **I-10 · `ROADMAP.md` and `CHECKLIST.md` both describe sequence.** Decide
  which owns it. CHECKLIST is the better format; ROADMAP could become a one-page
  "where am I" instead.
- [ ] **I-11 · The migration order appears in three files** with slightly
  different wording. One source.

## P3 · Missing — things a builder will want and can't find

- [ ] **I-12 · No STATUS page.** "Where am I, what's next, what's blocked"
  currently needs four files. One short dashboard, updated each session.
- [ ] **I-13 · No index in `DECISIONS.md`.** 105 entries, no table of contents.
  Add a topic index at the top — architecture, channels, connectors, modules,
  build sequence.
- [ ] **I-14 · No glossary.** O15, L4-M, DP-ICU, K-008, A15, K11 are all
  undefined to a cold reader — including Camden in six months.
- [ ] **I-15 · The new wire colour scheme exists only inside D-016.** RED = 25 A,
  ORN = 15 A, VIO = 7 A, GRY = input. That belongs in SPEC as a table, next to
  the factory colour codes it will be confused with.
- [ ] **I-16 · The CAN message map is buried in `DCU-CLUSTER.md` §13.** It will be
  referenced from firmware constantly. Own file.
- [ ] **I-17 · No migration log template.** Phase 6 needs a per-circuit sheet —
  circuit, date, measured A, soft fuse set, V-drop, initials. Build it before
  Phase 6, not during.
- [ ] **I-18 · No label schedule.** Checklist 4.20 and 5.8 both say "label every
  wire" with no list of what the labels say.
- [ ] **I-19 · No wire cut list**, even as an empty template keyed to the legs.
  It's blocked on T-008, but the shape can exist now.
- [ ] **I-20 · No safety page.** Lithium handling, 2 AWG shorting energy, fuel
  system work, working under a car. One page, written once.
- [ ] **I-21 · No PMU config version log.** Checklist 2.24 says "start a version
  log" and there's nowhere to put it.
- [ ] **I-22 · No photo index.** T-018 generates dozens of harness photos with no
  described home.

## P4 · Polish

- [ ] **I-23 · Most files have no date or revision stamp.** Can't tell fresh from
  stale at a glance. Add a one-line header to each.
- [ ] **I-24 · Factory circuit files' "what this means for the rebuild" tables
  still reference C1–C7.** Archived scheme. Update or strip those columns —
  the factory decode is still valid, the mapping is not.
- [ ] **I-25 · `vehicle.md` doesn't record that the Ionic is purchased**, or the
  PMU. Its "Electrical — current" section is now behind reality.
- [ ] **I-26 · `00-CAR` has no service history section** — dates, mileage, what
  was done. It's meant to be the permanent record across every project.
- [ ] **I-27 · OPEN.md and TASKS-CAMDEN.md overlap.** Several `Q-###` are really
  tasks (Q-014 is a tape measure, not a decision). Route by *action type*, not by
  who's blocked.
- [ ] **I-28 · No handover summary.** If this project sat for a year, the fastest
  path back in is currently "read 20 files."

## Standing rule

When any of these is fixed, tick it here and note the date. When new drift is
found mid-task, **add a line here rather than fixing it inline** — unless it's a
contradiction that would mislead, in which case fix it immediately and log it.

---

## §8 STATUS — 2026-08 pass

**All 28 items addressed.** Log below. Re-audit after the next major scope change.

### P1 · Contradictions — all fixed

- [x] **I-01** vehicle.md fuel pump → Carter P4070
- [x] **I-02** `legs/dash.md` rewritten — AMPSEAL, lighter, stale Q-refs, D-006 section all gone
- [x] **I-03** `01-REFERENCE/README.md` rebuilt — right filenames, obtained items moved, TS-ICT catalogue indexed as `[V-062]`
- [x] **I-04** `ROADMAP.md` archived, replaced by `STATUS.md`
- [x] **I-05** Stale `[V-0xx] pending` cleared from engine.md and front-chassis.md
- [x] **I-06** `legs/README.md` rebuilt with correct counts and the full file table
- [x] **I-07** This file's own reorder rule corrected to match practice

### P2 · Duplication — single owners assigned

- [x] **I-08** `LOADS.md` is the only source for current figures. Leg files link, don't restate
- [x] **I-09** `PIN-MAP.md` owns cavity assignments. Leg files describe *why*. Stated explicitly in `legs/README.md`
- [x] **I-10** ROADMAP retired; CHECKLIST owns sequence, STATUS owns "where am I"
- [x] **I-11** `MIGRATION-LOG.md` owns the migration order. Others reference it

### P3 · Missing — created

- [x] **I-12** `STATUS.md`
- [x] **I-13** Topic index at the top of `DECISIONS.md`
- [x] **I-14** `GLOSSARY.md`
- [x] **I-15** Wire colour scheme now a table in `SPEC.md` §2, next to the terminals
- [x] **I-16** `CAN-MESSAGES.md`
- [x] **I-17** `MIGRATION-LOG.md`
- [x] **I-18** Label schedule in `CUT-LIST.md`
- [x] **I-19** `CUT-LIST.md` template, keyed by leg
- [x] **I-20** `SAFETY.md`
- [x] **I-21** Config and firmware version logs in `LOGS.md`
- [x] **I-22** Photo index and naming convention in `LOGS.md`

### P4 · Polish

- [x] **I-23** Date stamps added to rewritten files. **Convention:** `*Rev YYYY-MM*` under the title
- [x] **I-24** Banner on `factory-circuits/README.md` — the decode is valid, the C1–C7 rebuild mapping is not
- [x] **I-25** `vehicle.md` records the PMU and battery purchases
- [x] **I-26** Service history, fluids and torque tables added to `modifications.md`
- [x] **I-27** Routing rule set: **decisions → OPEN, actions → TASKS.** Q-014 is a measurement and now appears in both, correctly
- [x] **I-28** Handover path at the foot of `STATUS.md` — five files, forty minutes

### New files this pass

`STATUS.md` · `GLOSSARY.md` · `SAFETY.md` · `CAN-MESSAGES.md` ·
`MIGRATION-LOG.md` · `CUT-LIST.md` · `LOGS.md`

### Carried forward

- `[V-062]` — identify what `TS-ICT-T-C-CAT-2018.pdf` actually covers
- The remaining leg files (`front-chassis.md`, `rear-cabin.md`, `engine.md`)
  still restate current figures that belong only in `LOADS.md`. Corrected on
  next touch rather than rewritten wholesale

---

## I-29 · Cross-reference sweep after the 2026-08 folder reorganisation

Project files moved into `01-DESIGN` … `07-PROCESS`. Inline relative links inside
documents were **not** all updated.

**Not urgent** — filenames are unchanged and unique across the project, so
`LOADS.md` is unambiguous even without the folder prefix. Fix each file's links
on next touch rather than sweeping all 30 at once.

- [ ] `01-DESIGN/*` — internal links
- [ ] `02-HARNESS/*` — `../LOADS.md` → `../01-DESIGN/LOADS.md`
- [ ] `03-MODULES/*`
- [ ] `04-SUBSYSTEMS/*`
- [ ] `05-BUILD/*`
- [ ] `06-PROCUREMENT/*`
- [ ] `07-PROCESS/*`
- [ ] `01-REFERENCE/factory-circuits/README.md` — points into the project

## I-30 · ASSISTANT.md §0 is now wrong

Section 0 says to read "SPEC.md" and "OPEN.md" at session start. Those are now
`01-DESIGN/SPEC.md` and `07-PROCESS/OPEN.md`, and `STATUS.md` should be first.

**Corrected reading order for session start:**
1. This file
2. `02-PROJECTS/electrical-pmu/STATUS.md`
3. The specific file the task touches
4. `07-PROCESS/OPEN.md` if the task touches an unresolved item

- [x] Noted here. Fold into §0 on next edit of that section.

## I-31 · New subsystem pattern established

`04-SUBSYSTEMS/` now holds self-contained designs — battery, tail lights, parts
changes. **Future one-off designs go here**, not in the root: radar subsystem,
switch panel, cluster bezel, sill node fabrication.

---

# 9 · SECOND AUDIT — 2026-08

From reading `PARTS-CHANGES.md` and `INFOTAINMENT.md` end to end. The findings
generalise to most of the project.

## THE ROOT PROBLEM — append-only accretion

**I have been appending rather than revising, because appending is cheap and
safe. It has produced documents where the wrong answer is at the top and the
right answer is at the bottom.**

Two proven examples:

**`PARTS-CHANGES.md`** — 300+ lines. Opens with "§1 · Lighting — all of it
changes" and a full LED conversion table. A reader must scroll through **four
UPDATE sections** to discover lighting moved to another project entirely. §1 is
now actively false. It also still says "Until `[Q-044]` is answered, the design
assumes option A" — Q-044 was answered.

**`INFOTAINMENT.md`** — 202 lines before the answer. §1 recommends a hidden
Bluetooth module. §2 recommends turn-by-turn text. §3 and §8 evaluate three Pi
paths. §9 says all of it is dead and the answer is a head unit. **Someone reading
top-down builds an entirely wrong model before reaching the conclusion.**

**The fix, and it is a standing rule from now on:**

> When a decision supersedes content, **revise the section in place** and move
> the superseded reasoning to a clearly-marked appendix at the bottom, or to
> `99-ARCHIVE`. Do not append a correction and leave the error above it.
>
> A document should be readable top-to-bottom and be correct the whole way down.

- [ ] **I-32 · Rewrite `PARTS-CHANGES.md` from scratch.** Current state only.
      Lighting gone, blower dead not failing, windows manual, Q-044 answered.
      Move the superseded reasoning to an appendix
- [ ] **I-33 · Rewrite `INFOTAINMENT.md` from scratch.** Head unit decision at
      the top. §1–§8 become "Appendix: options considered", or archive them
- [ ] **I-34 · Audit every file for the same pattern.** Any file with an "UPDATE"
      heading that contradicts content above it. Likely: `LOADS.md`,
      `CONNECTORS.md`, `sill-node.md`, `BOM.md`, `BUY-LIST.md`, `DCU-CLUSTER.md`

## SCOPE LEAKAGE — wiring project holding non-wiring content

- [ ] **I-35 · `PARTS-CHANGES.md` §1 is entirely lighting.** LED conversion
      table, headlight strip options, Q-044 discussion. **Belongs in
      `lighting-body/`.** The electrical project's lighting scope is one line:
      "stock incandescent bulbs, unchanged"
- [ ] **I-36 · `INFOTAINMENT.md` is not a module.** It sits in `03-MODULES/`
      alongside the DCU and ICU, but a head unit is an accessory, not a CAN node.
      **Move to `04-SUBSYSTEMS/`.** `03-MODULES/` should hold only DCU, ICU, CAN
- [ ] **I-37 · Dead-path content is 90% of `INFOTAINMENT.md`.** Bluetooth
      modules, ANCS turn-by-turn, three Pi architectures, offline OSM data, GPS
      modules, graceful shutdown circuits. **None of it is in the project.**
      Archive it — it's good reasoning, but it isn't this project's content
- [ ] **I-38 · `DEFERRED-FEATURES.md` and `PARTS-CHANGES.md` overlap.** Heated
      seats, cooled seats, radar and the LS reservation appear in both. Pick one
      owner. **Suggest: PARTS-CHANGES owns *what changes*, DEFERRED-FEATURES owns
      *what's pre-wired and waiting*.** They are different questions

## FACTUAL ERRORS FOUND

- [ ] **I-39 · `PARTS-CHANGES.md` §6 lists "Window motors ×2 — Sill H-bridges"
      under "Carrying forward unchanged."** The windows are manual (D-131).
      There are no window motors on this car
- [ ] **I-40 · `PARTS-CHANGES.md` §2 says the blower is "Original, failing."**
      It is confirmed dead (K-023). Corrected only in an UPDATE 200 lines below
- [ ] **I-41 · `PARTS-CHANGES.md` links `TAIL-LIGHTS.md` as a sibling.** That
      file moved to `lighting-body/`. Broken reference
- [ ] **I-42 · `PARTS-CHANGES.md` §1 says headlights are "LED enclosed housing."**
      Cross-check against `V-066` — the car may have 7-inch round sealed beams.
      Two files disagree about what is currently fitted

## REPRESENTATION

- [ ] **I-43 · No consistent file header.** Some files have `*Rev 2026-08*`, most
      don't. **Standard header for every file:** title, one-line purpose,
      `*Rev date · owner-of-this-fact*`
- [ ] **I-44 · Superseded content is not marked inline.** A reader in the middle
      of a document cannot tell whether what they're reading is current. **Mark
      superseded sections with a banner at the section head**, not only at the
      file foot
- [ ] **I-45 · `INFOTAINMENT.md` §1–§8 have no supersession markers at all.**
      Only §9 reveals it. Highest-risk instance of I-44
- [ ] **I-46 · Long files have no table of contents.** `PARTS-CHANGES.md`,
      `INFOTAINMENT.md`, `DCU-CLUSTER.md`, `CHECKLIST.md`, `METER-SESSION.md` all
      exceed 200 lines
- [ ] **I-47 · Question IDs referenced in prose are often already closed.**
      Q-044, Q-046, Q-047, Q-050, Q-051 all appear as open in file bodies. Sweep
      for `[Q-` and `[V-` and check each against `OPEN.md`

## STRUCTURAL

- [ ] **I-48 · `05-BUILD/` mixes procedures with working sheets.** `SAFETY.md`
      and `METER-SESSION.md` are read-once procedures; `MIGRATION-LOG.md`,
      `CUT-LIST.md` and `LOGS.md` are filled-in-during-work sheets. Consider
      `05-BUILD/` and `06-SHEETS/`
- [ ] **I-49 · `01-DESIGN/` now holds seven files** including `PMU-CONFIG.md`
      and `PANEL-LAYOUT.md`, which are arguably build documents. Re-check the
      boundary
- [ ] **I-50 · `can_map.h` is source code in a documentation tree.** Fine for
      now, but when firmware starts it wants a repo. Note where it will live
- [ ] **I-51 · No `lighting-body/` decision log.** It inherited D-107, D-110,
      D-111 from the electrical project with no local record

## THE ONE RULE THAT PREVENTS MOST OF THIS

**Before appending to any file, read it first.** If the append contradicts
anything above it, revise instead of appending. Every finding in I-32 through
I-42 exists because that step was skipped.

---

# 10 · AUDIT CLOSEOUT — 2026-08

**I-01 through I-51 are complete.** Sections 8 and 9 above are the working
records; this is the result. Future audits append a new numbered section rather
than editing these.

## Standing rules that came out of it

These are permanent. They exist because each was violated at least once.

**R1 · Read a file before appending to it.** If the append contradicts anything
above it, **revise instead of appending.** Nearly every finding in the second
audit existed because this step was skipped.

**R2 · A document must be correct top to bottom.** When a decision supersedes
content, revise the section in place and move superseded reasoning to a marked
appendix or `99-ARCHIVE`. Never leave an error above a correction.

**R3 · One owner per fact.** Declared in each file's header line. If two files
disagree, the owner wins.

**R4 · Scope belongs to the project that owns the work.** Not the project where
it was first discussed.

**R5 · Every file gets a header:** title, one-line purpose, `*Rev date · owns:
what*`.

## What was fixed

| Group | Items | Result |
|---|---|---|
| **Contradictions** | I-01, I-03, I-07 | Fuel pump conflict, reference index, reorder rule |
| **Stale files** | I-02, I-04, I-05, I-06 | `dash.md` rewritten, ROADMAP archived, leg files cleaned, `legs/README` rebuilt |
| **Duplication** | I-08 – I-11 | Owners assigned: LOADS owns current, PIN-MAP owns cavities, MIGRATION-LOG owns migration order, CHECKLIST owns sequence |
| **Missing files** | I-12 – I-22 | STATUS · GLOSSARY · SAFETY · CAN-MESSAGES · MIGRATION-LOG · CUT-LIST · LOGS created |
| **Polish** | I-23 – I-28 | Date stamps, factory-file banner, vehicle.md, service history, routing rule, handover path |
| **Reorganisation** | I-29 – I-31 | Numbered folders, session-opening paths, subsystem pattern |
| **Accretion** | **I-32 – I-34** | `PARTS-CHANGES.md` and `INFOTAINMENT.md` rewritten clean |
| **Scope leakage** | **I-35 – I-38** | Lighting out of PARTS-CHANGES · INFOTAINMENT → `04-SUBSYSTEMS/HEAD-UNIT.md` · dead paths archived · DEFERRED-FEATURES vs PARTS-CHANGES ownership declared |
| **Factual errors** | **I-39 – I-42** | Window motors removed, blower marked DEAD, broken link fixed, headlamp claim flagged to `V-066` |
| **Representation** | **I-43 – I-47** | Headers, supersession banners, contents blocks, closed-question sweep |
| **Structure** | **I-48 – I-51** | Boundaries reviewed, `can_map.h` noted, `lighting-body/DECISIONS.md` created |

## Structural decisions made during closeout

**I-48 · `05-BUILD/` stays one folder.** Splitting procedures from working sheets
would add a folder to save a scroll. Both are shop documents used on the same
days.

**I-49 · `PMU-CONFIG.md` and `PANEL-LAYOUT.md` stay in `01-DESIGN/`.** Both are
*specifications* of what to build, not procedures for building. The line is
"describes the thing" versus "tells you what to do next."

**I-50 · `can_map.h` stays in `03-MODULES/` until firmware starts.** When there
is a repo it moves there and this copy becomes a pointer. Noted so it isn't
duplicated into two places that drift.

**I-51 · `lighting-body/DECISIONS.md` created.** Inherited D-107, D-110 and D-111
keep their electrical-project IDs so cross-references stay valid. Local decisions
use `L-###`.

## Files created this audit

`04-SUBSYSTEMS/HEAD-UNIT.md` · `04-SUBSYSTEMS/DEFERRED-FEATURES.md` ·
`../lighting-body/DECISIONS.md`

## Files archived

`2026-08_infotainment-options-considered.md` — the Bluetooth, ANCS and three Pi
paths. Kept because the Pi minimap is genuinely buildable later if the offline
aspect ever matters.

## Carried forward — not closed

| Item | Why |
|---|---|
| `V-066` | Round or rectangular sealed beams. **Two files disagreed about what's fitted** — now flagged rather than guessed |
| `I-29` links | Relative paths inside documents still assume the pre-folder layout. Filenames are unique so nothing is ambiguous. Fixed on next touch of each file |
| Remaining leg files | `front-chassis.md`, `rear-cabin.md`, `engine.md` still restate current figures owned by `LOADS.md`. Corrected on next touch |

## Next audit

Trigger it after the next major scope change, or when any file exceeds ~250 lines
with more than one UPDATE section. **Those two conditions are what produced this
one.**

---

# 11 · THIRD AUDIT — 2026-08, after the ICU firmware

The project gained working C++ firmware and a desktop simulator since the last
audit. **The documentation has not caught up with the code**, and that is now
the dominant problem.

## THE ROOT PROBLEM — code became a source of truth, silently

`cluster_core.h` now defines the palette, every layout constant, the icon set,
the unit conversions and the sensor-fault rendering. **None of that is recorded
in `DECISIONS.md`.** The docs still describe a design that was superseded while
it was being built.

Worse: the docs claim canonical status they no longer hold. `README.md` says
"one owner per fact", but for cluster layout the owner is now a header file that
the index does not mention.

**The fix is not to duplicate the code into prose.** It is to say plainly which
facts the source owns, and record the *decisions* that produced it.

- [ ] **I-52 · Record the cluster design decisions.** Emerald `#009155` as the
      single lit shade · unlit at 4:1 · one-shade rule with `C_BRIGHT == C_MID` ·
      imperial at the display layer with metric in state and logs · segment bars
      with zero gap · sensor faults as dashes + hollow outline · symbols not
      words · the four-axis column layout
- [ ] **I-53 · Declare `cluster_core.h` the owner of cluster layout** in
      `README.md` conventions, the way `LOADS.md` owns current figures

## THE INDEX IS WRONG

- [ ] **I-54 · `README.md` does not mention `03-MODULES/firmware/` at all.**
      Six sketch folders and the real ICU firmware are invisible to anyone
      reading the index
- [ ] **I-55 · `README.md` lists `can_map.h` in `03-MODULES/`.** It moved to
      `firmware/icu/`. Broken path in the file index itself
- [ ] **I-56 · `README.md` says "D-001…D-105".** Decisions now run past D-150
- [ ] **I-57 · No `firmware/README.md`.** Nothing explains what each sketch is,
      which are superseded, or how to build the simulator. **The w64devkit build
      workflow exists only in a source comment and a chat log**

## DEAD AND SUPERSEDED

- [ ] **I-58 · `cluster-mockup.html` is dead.** Superseded by the real simulator
      running actual firmware. Archive it — leaving a lookalike beside the real
      thing invites editing the wrong one
- [ ] **I-59 · `CLUSTER-DESIGN.md` describes a design that was overtaken.** The
      multi-page architecture, the "make the static layer elaborate" ideas, the
      page-refresh table — none of it is what got built. Either mark it as
      forward-looking scope or fold the live parts into the firmware README
- [ ] **I-60 · `DCU-CLUSTER.md` §5a/§5b analyse three display approaches.** We
      committed to SPI + dirty rectangles and built it. That analysis is now
      background, not a live decision
- [ ] **I-61 · `BENCH-BRINGUP.md` stages 4 and 5 point at standalone sketches**
      that the full ICU firmware has absorbed. Mark them done or superseded

## OPEN ITEMS THE CODE ALREADY ANSWERED

- [ ] **I-62 · Sweep `Q-056`, `Q-057`, `Q-058`, `Q-059`.** Q-056 visual style and
      Q-057 rotating-horizon-vs-bars were both settled by building the thing.
      Q-059 PSRAM is still genuinely open. Close what's closed
- [ ] **I-63 · `V-058` display nit rating is now urgent, not "easy".** Panel
      selection is the next hardware decision and 800–1000 nits is the spec most
      often omitted from listings

## GAPS THE FIRMWARE EXPOSED

- [ ] **I-64 · How does the display physically connect?** `DP-ICU` is a DT06-12S
      with 11 conductors used. A panel needs SPI or parallel plus backlight
      power — far more. **The display almost certainly connects directly to the
      Teensy inside the dash and never crosses the harness**, but that is
      nowhere stated, and someone sizing `DP-ICU` later will assume otherwise
- [ ] **I-65 · `stats.h` thresholds are undocumented magic numbers.**
      `REDLINE_RPM 7000`, `HOT_WATER_C 105`, `LOW_OIL_CBAR 100`,
      `TANK_GAL_X10 159`. None verified against a 12A, none recorded as
      decisions. The redline one in particular drives the tach's red zone
- [ ] **I-66 · `stats.h` has no persistence.** It says `life[]` reloads at boot;
      no SD read or write exists. Either write it or mark the struct as
      volatile-only for now
- [ ] **I-67 · `LOGS.md` has manual tables `stats.h` now automates** — max
      speed, max RPM, runtime. Decide which is authoritative and say so
- [ ] **I-68 · The IMU is decided (D-109) but unspecified.** No part number, no
      I2C address, no orientation convention. Which axis is lateral matters and
      is not written down
- [ ] **I-69 · No archived render of the agreed design.** After a dozen layout
      iterations there is no image showing what was settled on. A screenshot in
      `03-MODULES/` costs nothing and is the fastest way back into context

## STILL CARRIED FROM EARLIER AUDITS

- [ ] **I-29 · Relative links** still assume the pre-folder layout. The note is
      still in `README.md`, which means it still reads as unfixed
- [ ] **I-70 · Three leg files** — `engine.md`, `front-chassis.md`,
      `rear-cabin.md` — still restate current figures owned by `LOADS.md`

## STANDING RULE ADDED

**R6 · When code becomes the source of truth for something, say so in the
index and record the decisions that shaped it.** Code and prose drift silently
because nothing forces them to agree; the only defence is naming the owner.

---

# 12 · AUDIT 3 CLOSEOUT + FORWARD WORK — 2026-08

## I-52 … I-70 complete

| Item | Result |
|---|---|
| I-52 | **D-151…D-158** record every cluster design decision that existed only in code |
| I-53 | `README.md` conventions table now names `cluster_core.h` and `stats.h` as owners |
| I-54 | `README.md` documents `firmware/` and every file in it |
| I-55 | `can_map.h` path corrected to `firmware/icu/` |
| I-56 | Decision range corrected to D-001…D-163 |
| I-57 | **`firmware/README.md` created** — folder map, w64devkit build steps, simulator controls |
| I-58 | `cluster-mockup.html` archived |
| I-59 | `CLUSTER-DESIGN.md` retitled **forward scope**, banner explains what's built |
| I-60 | `DCU-CLUSTER.md` §5a marked **settled**, kept as background |
| I-61 | `BENCH-BRINGUP.md` stages 4 and 5 marked done and absorbed |
| I-62 | Q-035, Q-056, Q-057, Q-041 closed. Q-058 and Q-059 remain, correctly |
| I-63 | `V-058` elevated into **Q-060 panel selection**, the next hardware decision |
| I-64 | **D-159 — the display does not cross the harness.** `DP-ICU` is correctly sized |
| I-65 | **D-160** — every `stats.h` threshold recorded, three flagged for verification |
| I-66 | **D-162** — `stats.h` marked volatile-only, persistence scoped |
| I-67 | **D-163** — `stats.h` owns automated figures, `LOGS.md` owns manual ones |
| I-68 | **D-161** — IMU class and axis convention fixed |
| I-69 | Deferred — needs a screenshot only Camden can take |
| I-70 | Deferred to next touch of each leg file |

**New rule R6:** when code becomes the source of truth, name it in the index and
record the decisions that shaped it.

---

# FORWARD WORK — what becomes possible next

Ordered by what unblocks the most. **AGENT** items Claude can do now;
**BLOCKED** items name their gate.

## Firmware — the largest available block

- [ ] **F-01 AGENT · DCU firmware skeleton.** `dcu.ino` + `climate.h` mirroring
      the ICU structure: CAN node, state struct, servo outputs, comfort
      switching, heat/cool interlock (D-073). **Nothing blocks this** — the CAN
      map is final and the pattern is proven
- [ ] **F-02 AGENT · PMU simulator on the spare Teensy.** Transmit 0x100–0x130
      so ICU and DCU can be developed against a live bus before the PMU is
      configured. Turns the third board into a permanent test rig
- [ ] **F-03 AGENT · Sensor conditioning schematic.** Dividers, RC filters and
      clamp diodes for all six ICU inputs, with values computed from the sender
      ranges. Blocked only on `V-037` fuel sender ohms for one of the six
- [ ] **F-04 AGENT · Tach conditioning circuit.** Opto or comparator, with part
      numbers. Coil primary spikes well above 12 V (D-082)
- [ ] **F-05 AGENT · Cluster page framework.** Page enum, switch handling,
      per-page draw and invalidate. Makes the diagnostics and trip pages
      additive rather than a rewrite
- [ ] **F-06 AGENT · Diagnostics page.** 24 channels, live current, soft-fuse
      setpoint, state. **The thing nothing else can do.** Needs F-05
- [ ] **F-07 AGENT · SD persistence for `stats.h`.** Write on key-off via the
      PMU shutdown delay (D-054). Needs a decision on write frequency
- [ ] **F-08 BLOCKED on Q-060** · Display driver — `pushDirtyTiles()` is three
      TODO calls away from complete
- [ ] **F-09 BLOCKED on V-065** · Reconcile `can_map.h` 0x100–0x130 against the
      PMU's actual export

## Hardware design

- [ ] **H-01 AGENT · ICU carrier PCB schematic.** Teensy socket, TCAN1042, IMU,
      buck + load-dump TVS, six conditioned inputs, display header. Every part
      is now decided
- [ ] **H-02 AGENT · DCU carrier PCB schematic.** Same power section, servo
      drivers, comfort MOSFETs
- [ ] **H-03 BLOCKED on T-007** · Panel 1:1 drawing
- [ ] **H-04 BLOCKED on T-028** · Sill plate drawing
- [ ] **H-05 AGENT · Dash post bracket layout** — 14 leg receptacles plus four
      drops, using the mounting clips confirmed in the TE catalogue

## Documentation gaps that will bite later

- [ ] **X-01 AGENT · Wiring diagram set.** One page per leg, generated from
      `PIN-MAP.md`. The project has no visual wiring reference at all
- [ ] **X-02 AGENT · Panel schematic sheet.** Relay bank, fuse block, busbars,
      wake network as one drawing
- [ ] **X-03 AGENT · Troubleshooting guide.** Symptom → likely cause → which
      document. Written while the design is fresh, used when it isn't
- [ ] **X-04 AGENT · Commissioning test card.** Per-circuit pass/fail for
      Phase 6, tighter than the migration log
- [ ] **X-05 AGENT · Fix I-70** — strip duplicated current figures from the
      three remaining leg files

## Thinking further ahead

- [ ] **Z-01 · LS swap electrical plan.** O13, O14, the CAN drop and six sensor
      spares are reserved. Nobody has written what actually connects to them
- [ ] **Z-02 · Radar subsystem design** `[V-061]` — concealed sensors front and
      rear, DCU-managed. Still a placeholder
- [ ] **Z-03 · Mirror control protocol** `[V-060]` — the door connector has zero
      spare cavities, so the mirror choice is load-bearing
- [ ] **Z-04 · Cold-weather behaviour.** Battery heater draw, winter parasitic
      budget, whether the PMU should shed loads below a temperature
- [ ] **Z-05 · Failure-mode table.** For each of the ~20 things that can fail,
      what the driver sees and what still works. The ICU already guarantees
      gauges survive a CAN loss — nothing else is written down

## Where progress genuinely stops

**Four measurements gate the physical build**, and no amount of design replaces
them:

| Gate | Blocks |
|---|---|
| **T-007** dash envelope | Panel drawing, panel parts, all of Phase 4 |
| **T-008** harness routes | Cut list, the $1,000–1,700 wire order, Phase 5 |
| **T-014** clamp every load | Every soft fuse. **Irreversible window** |
| **T-011** pop-up limit pinout | A4/A5 ladder values |

**Everything on the AGENT list above can be done without them.** That is roughly
two hundred hours of design and firmware work still available on a laptop.

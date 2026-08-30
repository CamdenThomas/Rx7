# AUDIT 4 — representation and organisation of `electrical-pmu`

*2026-08-30 · full read of the tree: 66 Markdown files, the two Rev A HTML
files, the firmware sources, `.git` history and the Claude Project attached to
this folder. Written as a list of improvements, not as fixes — nothing in the
tree was edited. Numbering continues from I-70.*

**How to read this.** Items are grouped by the kind of problem, and within each
group ordered by how much a reader would be misled. Every item names the file
and, where it matters, the line. `P1` = a reader is actively misled · `P2` =
duplication that has already drifted or will · `P3` = something missing ·
`P4` = polish.

---

## The five root problems

Everything below is an instance of one of these.

**1 · The declared owners are the stale files.** `README.md` names `PIN-MAP.md`
the owner of cavity assignments and `LOADS.md` the only source for current
figures. Both are the two most out-of-date design files in the project.
Ownership was declared but the owner was never brought current, so the
"if two disagree the owner wins" rule now points readers at the wrong answer.

**2 · Rules R1–R2 (read before appending, correct top to bottom) are still
being broken, including by the file that made them.** `ASSISTANT.md` is an
operating manual with four audit logs appended to it; `STATUS.md` has a
progress assessment appended that contradicts its own phase table; `BOM.md`
carries thirteen stacked revisions and five different project totals.

**3 · Facts live in three copies with no generator.** Current figures
(`LOADS.md` / `CHANNEL-SCHEDULE.md` / `channels.h`), cavity assignments
(`SPEC.md` / `PIN-MAP.md` / leg files), migration order (`CHECKLIST.md` /
`MIGRATION-LOG.md`), the CAN map (`DCU-CLUSTER.md` §13 / `CAN-MESSAGES.md` ×2
/ `can_map.h` ×3). Every one has drifted.

**4 · IDs are permanent but their status isn't tracked anywhere.** 35 Q-IDs
and 25 V-IDs are cited as live in file bodies that `OPEN.md` does not hold —
most closed by a decision, a few open but tracked nowhere. The old
three-digit Checklist numbering is cited in 11 files. There is no single table
that says what every ID is and whether it is open.

**5 · The Claude Project knowledge base is the archived Rev A.** The only two
documents the attached Claude Project holds are the HTML files that
`99-ARCHIVE/README.md` says "do not read for anything except history".

---

# A · The Claude Project layer

- [ ] **I-71 · P1 · The Claude Project's knowledge base is the superseded Rev A.**
      The project holds exactly two docs: `rx7-pmu24-pin-plan-revA.html` and
      `rx7-pmu-build-checklist-revA.html`. These are byte-for-byte the files
      archived as `99-ARCHIVE/2026-08_*.html`, and the archive README lists
      seven things they get wrong (C1–C7, 18 AWG, 16 sockets, S9H, unverified
      cavity map, load resistors, DCU deferred). Any session that answers from
      project search gets Rev A. **Fix:** remove both; add `STATUS.md`,
      `README.md` (project), `GLOSSARY.md`, `SPEC.md` and `OPEN.md` — the five
      files the handover path names — and refresh them when they change.
- [ ] **I-72 · P1 · The project instructions don't say to read `ASSISTANT.md`.**
      The instruction is one line ("database and responses all live within this
      directory"). `ASSISTANT.md` §0 says "read this first, every session", but
      nothing in the project makes that happen. **Fix:** put the §0 reading order
      and the mode question directly in the project instructions, or upload
      `ASSISTANT.md` as a project doc.
- [ ] **I-73 · P3 · No `CLAUDE.md`.** Claude Code reads a root `CLAUDE.md`
      automatically; nothing reads `ASSISTANT.md` unless told to. A three-line
      `CLAUDE.md` that says "read ASSISTANT.md first, then STATUS.md" closes the
      gap for every tool that honours the convention.
- [ ] **I-74 · P2 · `ASSISTANT.md` says "never produce artifacts — no HTML"
      but the project's only artifacts are HTML.** Either the rule or the project
      contents is wrong. Decide which and make them agree (see I-71).

---

# B · `ASSISTANT.md` — the operating manual has become a logbook

- [ ] **I-75 · P1 · Sections 8–12 are audit logs appended to an operating
      manual.** 809 lines, of which the actual rules (§0–§7) are 195. A new
      session must read 600 lines of closed audit history to find the rules.
      §10 already says "future audits append a new numbered section" — that
      guarantees the file keeps growing. **Fix:** `ASSISTANT.md` holds rules only
      (§0–§7 plus R1–R6). Move §8–§12 to `07-PROCESS/AUDITS.md`, and the I-###
      registry to its own table there. Move `FORWARD WORK` (F/H/X/Z items) to
      `07-PROCESS/FORWARD-WORK.md` or into `STATUS.md`.
- [ ] **I-76 · P1 · §0 was corrected in place but I-30 still sits at line 371
      saying §0 is wrong.** A reader can't tell which is current. Delete I-30
      once the fix is confirmed folded (it is).
- [ ] **I-77 · P2 · R1–R6 are defined in three places** — §10 "Standing rules",
      §11 "STANDING RULE ADDED", §12 "New rule R6". Collect them once, in the
      rules half of the file, numbered.
- [ ] **I-78 · P2 · The mode table (§0) and the session protocol in the root
      `README.md` §"Session protocol" are the same content in two places.**
      README should point at ASSISTANT, not restate it.
- [ ] **I-79 · P2 · I-29 (relative links) is marked "fix on next touch" in three
      files** — `ASSISTANT.md`, `README.md` (project) §"Cross-reference note",
      and the closeout table. Twenty files have been touched since; none of the
      links were fixed. Either do the sweep once (30 minutes with a script — see
      I-146) or stop claiming it is in progress.
- [ ] **I-80 · P4 · `ASSISTANT.md` has no header of its own** (title, purpose,
      rev), while R5 requires one on every file.
- [ ] **I-81 · P4 · §2 says `TASKS-CAMDEN.md` — "reorder and regroup freely".**
      In practice it was appended to three times (section D table). The rule is
      right; the file doesn't follow it.
- [ ] **I-82 · P4 · The GLOSSARY says I-## lives in "`ASSISTANT.md` §8".** They
      now span §8–§12 and will move (I-75). Update the pointer when they do.

---

# C · Declared owners that are not current

- [ ] **I-83 · P1 · `02-HARNESS/PIN-MAP.md` is "authoritative cavity
      assignments" and describes a design that no longer exists.** Title says
      "four leg connectors … one connector per leg" (line 1–3); tables give L1
      cav 1–20, L2 cav 1–21, L3 cav 1–30, L4 cav 1–25 as single housings — the
      pre-D-070 scheme. The current scheme (L1-P/S, L2-P1/P2/M/S, L3-P/M/S1/S2/S3,
      L4-P/M/S) exists only in the leg files and CONNECTORS' *third* table. Only
      L4 was revised, in an UPDATE at the bottom. Also: "11 relays" (D-067 says
      5 in the box), K9 "mounts at the starter" (D-148: inner fender), senders
      "cluster now" ×5 (D-083: ICU), cigarette lighter on O10 (D-095), window
      commands live (D-131), Q-016/018/019/022/026 and V-027/033 cited as open
      (all closed), and the terminal table contradicts SPEC (I-84). **Fix:**
      rewrite PIN-MAP as one table per housing in the current scheme, generated
      from the same source as SPEC §4–§8 (see I-144).
- [ ] **I-84 · P1 · SPEC and PIN-MAP disagree about which terminal the 15 A /
      7 A outputs use.** `SPEC.md` §2: 1.5 mm `211CC2S2160P` for 15 A / 7 A /
      inputs; 2.8 mm `211CC3S2120` for pin 15 only. `PIN-MAP.md` lines 12–16:
      2.8 mm `211CC3S2120` for "15 A and 7 A outputs". SPEC §11 (confirmed from
      CAD, D-045/046) is right. PIN-MAP is wrong in the file that a builder will
      have open while crimping.
- [ ] **I-85 · P1 · `01-DESIGN/LOADS.md` is "the only source for current
      figures" and is wrong top-to-bottom.** Lines 34–67 present LED conversion
      as the design intent; the incandescent baseline (D-124) is at line 343.
      In between: `Facet` fuel pump (line 115, corrected at 287), cigarette
      lighter (126), window motors (81), rear wiper and power antenna (83, 85 —
      gone, D-097), `C1 spare` / `C2 spare` / `C4 spare` (archived scheme),
      "Checklist 121 / 044–045 / 013/014 / 051" (retired numbering), "bench mule"
      (dropped, D-141), `[Q-032] still needs your yes` (answered, D-073), seven
      `(cite index=…)` chat-export artifacts, and senders "reserved on C1 spare"
      (ICU reads them). **Fix:** rewrite to current state only — one design table
      (incandescent), one measured column pointing at CHANNEL-SCHEDULE, LED
      figures as a clearly-labelled appendix for `lighting-body/`.
- [ ] **I-86 · P2 · Current figures now have three owners, not one.** `LOADS.md`
      (estimates), `CHANNEL-SCHEDULE.md` (measured, "owns the measured-to-
      configured pipeline"), `firmware/pmu_sim/channels.h` ("the machine-
      readable copy"). The README ownership table names only LOADS. They already
      disagree: brake is 3.9 A in LOADS, 7.0 A measured in CHANNEL-SCHEDULE and
      `channels.h`; CHANNEL-SCHEDULE says "3 of 24 measured", `firmware/README`
      says "22 of 24 are estimates". **Fix:** one machine-readable table
      (I-144); LOADS becomes method + rationale and links to it.
- [ ] **I-87 · P2 · The measured readings themselves live in three places.**
      `METER-SESSION.md` Part 6 "First session readings", `CHANNEL-SCHEDULE.md`
      MEASURED column, `channels.h`. METER-SESSION is a procedure; readings
      should be recorded once, in the schedule.
- [ ] **I-88 · P2 · Migration order is restated in `CHECKLIST.md` Phase 6
      (18 items) although `MIGRATION-LOG.md` "owns" it (26 rows).** They differ:
      CHECKLIST has "Windows" as a live item and merges wipers + washer;
      MIGRATION-LOG strikes windows through and separates them. I-11 declared
      this fixed; it wasn't.
- [ ] **I-89 · P2 · `CONNECTORS.md` contains three master connector lists.**
      Lines 54–70 (13 connectors, AMPSEAL), 123–133 (15), 143–161 (14, final).
      The first is what a reader sees. The file also disagrees with itself on D1/D2
      (DTP06-2S + DT06-6S at line 167; DT06-08S at line 269 and in D-092).
- [ ] **I-90 · P2 · Total mated-pair count: `CONNECTORS.md` says 20, `PIN-MAP.md`
      and `02-HARNESS/README.md` say 23.** Different things are being counted
      (door sub-connectors 2 vs 4, dash-post drops 2 vs 4). Define what a "mated
      pair" is once and count once.
- [ ] **I-91 · P2 · The CAN message map exists four times.** `DCU-CLUSTER.md`
      §13 "Draft message map", `CAN-MESSAGES.md` "Messages" (draft), `CAN-
      MESSAGES.md` "FINALISED MAP", and `can_map.h` — of which there are three
      identical copies (`icu/`, `can_map_test/`, `can_loopback_test/`). I-16 made
      CAN-MESSAGES the owner; the draft in DCU-CLUSTER and the draft half of
      CAN-MESSAGES were never removed. `CAN-MESSAGES.md` line 3 still says
      "*Draft. Finalise before firmware starts*" above a section titled
      FINALISED, and its "Before firmware starts" checklist is unticked although
      firmware has started and the header exists.
- [ ] **I-92 · P2 · `PMU-CONFIG.md` is two complete documents concatenated.**
      "PMU CONFIGURATION PLAN" §1–§6 (lines 1–205) and "LOGIC DEFINITIONS" §1–§6
      (lines 209–346) both carry the decode tables, output logic, interlocks and
      wake network. Two §1s, two §2s. Keep the second (it has expressions and
      windows), fold the bench order and save discipline into it.
- [ ] **I-93 · P2 · `SCHEMATICS.md` shows every sub-circuit twice.** Wake network
      with 5 inputs (§1) and 6 (UPDATE); window bridge in the box (§3) and at the
      sill (UPDATE); parts summary of 11 relays / 16 sockets (line 157) and 5 / 10
      (UPDATE). `[Q-025]` and `[Q-026]` cited as open in §1/§3 — both answered by
      the UPDATE 100 lines below.
- [ ] **I-94 · P2 · `02-HARNESS/README.md` "Elsewhere" links `../LOADS.md` and
      `../SCHEMATICS.md`** — both moved to `../01-DESIGN/`. Its leg-summary
      table says L2 Front has 7 heavy conductors; `front-chassis.md` counts 6
      (2 headlight + 4 pop-up). Small, but it is the file that claims to be the
      map of the leg files.

---

# D · Accretion — wrong at the top, right at the bottom

Files where a top-down reader builds the wrong model before reaching the
correction. Counts are of stacked UPDATE/REVISED/STATUS sections.

| File | Stacked sections | Lines | What the top says that is no longer true |
|---|---|---|---|
| `06-PROCUREMENT/BOM.md` | **13** | 446 | "Nothing here is ordered" (line 4) above four PURCHASED sections; AMPSEAL, 16 sockets, 4 AWG, TCAN, "Not in this BOM: DCU"; **five different project totals** ($5,230–7,045 → 6,067–9,172 → 6,100–9,100 → 6,700–10,300 → 6,470–9,560) |
| `01-DESIGN/LOADS.md` | 5 | 393 | See I-85 |
| `01-DESIGN/SCHEMATICS.md` | 4 | 235 | See I-93 |
| `02-HARNESS/CONNECTORS.md` | 4 | 287 | See I-89 |
| `02-HARNESS/PIN-MAP.md` | 3 | 287 | See I-83 |
| `02-HARNESS/sill-node.md` | 3 | 216 | Populated window relays (line 13), D1/D2 as two housings (65), then D-092 single housing (117), then D-131 empty sockets (165) |
| `07-PROCESS/TASKS-CAMDEN.md` | 3 | 170 | T-025 and T-020 "OPEN — do these next" (lines 37–38) and struck through as done (149–150) |
| `05-BUILD/METER-SESSION.md` | 2 | 379 | Part 1.1 names the wrong wire (`R`); the CORRECTION is at line 321 and the recording sheet (line 229) still says `R` |
| `06-PROCUREMENT/BUY-LIST.md` | 2 | 323 | A shopping list with links, then "everything is bought" at line 263 |
| `03-MODULES/CAN-MESSAGES.md` | 1 | 283 | "Draft" header over a finalised map (I-91) |
| `00-CAR/known-issues.md` | 1 | 91 | K-009…K-023 appended in blocks below the main tables instead of in them |
| `STATUS.md` | 1 | 223 | See I-95 |
| `03-MODULES/DCU-CLUSTER.md` | — | 691 | §3 says "**DCU** publishes engine sensors" (line 76) directly under the §2 correction saying the ICU does; §8 O10 budget with the deleted lighter; §13 recommends against the SN65HVD230 that was bought; `[Q-035]`–`[Q-043]`, `[V-056]`–`[V-058]` all cited as open |
| `07-PROCESS/DECISIONS.md` | 3 H1 blocks | 1290 | See I-125 |

- [ ] **I-95 · P1 · `STATUS.md` contradicts itself.** Phase table: "0 ·
      Documentation & measurement — **Started.** First meter readings taken"
      (line 38); progress assessment: "measurement not started" (line 132).
      Firmware table: stages 4–5 "Sketch written. Unblocked" (55–56) and "Do now:
      Firmware Stages 4 and 5" (74); progress assessment: "Bring-up stages 1–5 —
      All passed" (152). The opening paragraph says "Stages 1–3 are complete".
      The appended "PROGRESS ASSESSMENT" is a second STATUS. **Fix:** one
      dashboard, revised in place, with the assessment folded into the phase
      table.
- [ ] **I-96 · P1 · `STATUS.md` "Open decisions" omits three of the five open
      questions.** It lists Q-014 and Q-028; `OPEN.md` also holds Q-058, Q-059
      and **Q-060 — flagged there as "the next hardware decision"**. A reader of
      STATUS would not know a hardware decision is pending.
- [ ] **I-97 · P1 · Stage 4 and 5 status is stated four ways.** `BENCH-
      BRINGUP.md` headings: "✅ DONE — absorbed into the ICU firmware" (lines 119,
      140) with every checkbox under them unticked and a "Next sessions" table
      saying "**Next** — Stages 4 and 5"; `CHECKLIST.md` 2.27d/e unticked
      "sketch written, unblocked"; `TASKS-CAMDEN.md` T-046/T-047 open; `STATUS.md`
      both ways (I-95). Pick one state and write it once.
- [ ] **I-98 · P1 · Whether the spare housings have arrived is stated four
      ways.** `STATUS.md` line 29 "2 spare housings inbound"; `CHECKLIST.md` G0.2
      "Done — three housings total"; `BUY-LIST.md` line 280 "Bought"; D-140 "2
      spare housings inbound"; `TASKS-CAMDEN.md` T-027 "2 PURCHASED … three
      housings total"; T-045 "verify the two inbound housings".
- [ ] **I-99 · P1 · `BUY-LIST.md` "STATUS — bench kit PURCHASED" (line 263)
      marks 120 Ω resistors, E24 assortment, breadboards, jumpers, board
      materials and the rotary switch as Bought.** D-140 says they are **not in
      hand** and D-141/D-147 dropped most of them from the kit. `TASKS-CAMDEN.md`
      T-026 repeats the "PURCHASED" list. `BENCH-KIT.md` has them under "To buy".
- [ ] **I-100 · P1 · `CLUSTER-DESIGN.md` banner says the multi-page
      architecture, diagnostics page and trip page "do not exist yet"** (lines
      9–10); `STATUS.md` line 157 lists "Page framework — Drive, diagnostics,
      trip" as delivered and `stats.h` as having a trip page. Its "Open" table
      lists Q-057 (closed in audit 3, I-62) and Q-056 as "decided".
- [ ] **I-101 · P1 · `CHECKLIST.md` still builds the power windows.** 5.12 "Wire
      the K5–K8 window H-bridges at the sill" and Phase 6 "Windows" as a
      migration item. D-131: sockets fitted empty, relays not populated, nothing
      to migrate. `CUT-LIST.md` still carries the window-command and motor-leg
      rows without a "capped" mark.
- [ ] **I-102 · P1 · `PARTS-CHANGES.md` §3 "Cluster display — Format undecided
      `[Q-037]`"** — decided, D-150. §3 "Head unit `[Q-055]` PENDING" — criteria
      set, D-149. Both also in its "Open items on this page" table.
- [ ] **I-103 · P2 · `DEFERRED-FEATURES.md` is the model for the tree** — one
      rev stamp, current state only, forward pointers. Note it as the pattern
      when rewriting the files in this section.

---

# E · Cross-references and IDs that are stale

- [ ] **I-104 · P1 · 35 Q-IDs and 25 V-IDs are cited as live in file bodies
      that `OPEN.md` does not hold.** Most were closed by a decision and the
      citing file was never touched; a few (Q-001 VIN, V-001 coil config,
      V-056 DCU standby, V-059 Teensy supply) are genuinely open and tracked
      nowhere — the same defect from the other side. Sweep list, file → bare
      IDs it presents as live:
      `PIN-MAP.md` Q-016 Q-018 Q-019 Q-022 Q-026 V-027 · `SCHEMATICS.md` Q-025
      Q-026 · `LOADS.md` Q-032 Q-038 V-042 V-056 · `SPEC.md` Q-038 ·
      `DCU-CLUSTER.md` Q-035 Q-036 Q-037 Q-038 Q-039 Q-040 Q-041 Q-042 Q-043
      Q-056 V-056 · `CLUSTER-DESIGN.md` Q-057 · `CAN-MESSAGES.md` Q-041 ·
      `BENCH-BRINGUP.md` Q-037 · `CONNECTORS.md` Q-030 Q-031 · `sill-node.md`
      Q-033 V-036 · `front-chassis.md` Q-016 Q-024 Q-044 · `rear-cabin.md` Q-022
      Q-023 Q-025 V-027 V-031 V-035 V-048 · `engine.md` Q-019 · `BOM.md` Q-010
      Q-012 Q-030 Q-031 Q-033 Q-037 Q-048 V-018 V-064 · `BUY-LIST.md` V-059 ·
      `PARTS-CHANGES.md` Q-037 Q-055 · `DEFERRED-FEATURES.md` Q-013 ·
      `TASKS-CAMDEN.md` Q-037 Q-042 (T-030 lists "Q-014, Q-037, Q-042, A-005,
      A-007" — four of five answered) · `00-CAR/modifications.md` Q-045 ·
      `00-CAR/vehicle.md` Q-001 V-001 · `01-REFERENCE/README.md` V-062 (closed
      D-114) · every `factory-circuits/*.md` "Unknowns" table (Q-016 Q-018 Q-019
      Q-020 Q-021 Q-022, V-021…V-039) · `lighting-body/TAIL-LIGHTS.md` Q-044
      Q-046 Q-047. **Fix:** an ID registry (I-145) and a rule that a closed ID is
      cited as `Q-038 → D-095`, never bare.
- [ ] **I-105 · P1 · Task IDs were renumbered (D-043) and the old numbers
      survive in reference files.** `factory-circuits/horn.md` line 63 "Clamp
      meter, T-002" (T-002 is now the Ionic battery); `OEM-RECORD.md` line 8
      "see task T-016" (T-016 is now the cancelled K-008 diagnosis; the pin-label
      task is T-017). OEM-RECORD is marked FROZEN, so this needs a deliberate
      exception.
- [ ] **I-106 · P1 · The old three-digit Checklist step numbers are cited in
      11 files** and no longer exist (CHECKLIST uses phase.step): `LOADS.md` (5),
      `SCHEMATICS.md` (5: "steps 020–023"), `LADDERS.md` (3: "013 and 014",
      "047–050"), `BOM.md` (3: "036–062", "031–033"), `BATTERY-INSTALL.md` ("063–
      076", "058"), `sill-node.md` ("080", "086", "101–110", "115"), `known-
      issues.md` ("step 005", "003–005"), `BUY-LIST.md` ("047"), `blower-ac-
      defroster-audio.md`, `charging-starting.md`, `meters-ignition-fuelpump.md`,
      `wipers-washers.md`. Also `LOGS.md` and `ASSISTANT.md` cite "Checklist 2.24"
      — the version-log step is 2.21; `known-issues.md` K-020 cites "Checklist
      2.21" for the keypad — that is 2.18. **Fix:** either give checklist steps
      stable IDs (`C-###`, like everything else) or stop citing step numbers.
- [ ] **I-107 · P2 · Path references that point at the pre-reorganisation
      layout** (bare-name mentions are fine per I-29; these are *paths*):
      `SPEC.md` §9 and §12 `legs/CONNECTORS.md`, `legs/PIN-MAP.md`, `legs/engine.md`,
      `legs/sill-node.md`; `00-CAR/vehicle.md` `02-PROJECTS/electrical-pmu/SPEC.md`;
      `factory-circuits/README.md` `02-PROJECTS/electrical-pmu/legs/PIN-MAP.md`,
      `02-PROJECTS/electrical-pmu/LOADS.md`, `01-REFERENCE/1982RX7WiringDiagram.pdf`
      (file is in `factory-circuits/`); `PIN-MAP.md` `01-REFERENCE/PMU-24_Pinout_
      v1.0.pdf` (is in `PMU_info/`); `02-HARNESS/README.md` and `dash.md`
      `../LOADS.md`; `CHANNEL-SCHEDULE.md` `MIGRATION-LOG.md` (is `../05-BUILD/`);
      `DECISIONS.md` D-110 `04-SUBSYSTEMS/TAIL-LIGHTS.md` (moved to `lighting-
      body/`), D-129 `INFOTAINMENT.md` (archived); `99-ARCHIVE/2026-08_superseded-
      C1-C7…` `02-PROJECTS/electrical-pmu/legs/`; `factory-circuits/turn-hazard.md`
      `backup-lights.md` (never existed); `firmware/icu/icu.ino` comment
      "see CLUSTER-DESIGN.md 5a" (§5a is in DCU-CLUSTER).
- [ ] **I-108 · P2 · There is not one clickable link in the tree.** Every
      cross-reference is a bare name in backticks. The repo is on GitHub
      (`CamdenThomas/Rx7`) and in an IDE — both render `[LOADS.md](../01-DESIGN/
      LOADS.md)`. Bare names are why I-29 could be deferred; real links would
      have failed visibly and been fixed.
- [ ] **I-109 · P2 · `DECISIONS.md` index covers D-001…D-105; the file runs to
      D-167.** `README.md` (project) says "D-001…D-163"; root `README.md` says
      "D-001…D-105". Three different ranges for one file.
- [ ] **I-110 · P2 · `GLOSSARY.md` is missing five ID schemes now in use:**
      `L-###` (lighting-body decisions), `TL-##` (tail-light process steps),
      `P-###` (planned modifications, `00-CAR`), `R#` (standing rules), `F/H/X/Z-
      ##` (forward work in ASSISTANT). It also doesn't say where `[VERIFY]`
      (no number) fits against `V-###`.
- [ ] **I-111 · P4 · `SPEC.md` §1 "All 16 analog inputs are allocated. There is
      no spare"** — but §7 shows six of the eight shared channels used as
      *outputs* (O17–O22); only A15/A16 are inputs. True in effect, misleading as
      written. And `CHANNEL-SCHEDULE.md` / `channels.h` call O23/O24 "Spare —
      disabled" when those pins are consumed as A15/A16. Neither "spare" nor
      "all allocated" is the right word; say "O23/O24 configured as inputs A15/
      A16".

---

# F · Contradictions between files that no owner rule resolves

- [ ] **I-112 · P1 · Power windows.** D-131 (windows are manual, hardware
      provisioned empty) is reflected in `sill-node.md` (bottom), `DEFERRED-
      FEATURES.md`, `MIGRATION-LOG.md`, `METER-SESSION.md`, `PARTS-CHANGES.md`.
      It is **not** reflected in `SPEC.md` §3 (K5–K8 "Sill node", no
      provisioned/empty state), `GLOSSARY.md`, `PMU-CONFIG.md` (live window
      interlocks and `MOTOR_BUS = popup || window`), `SCHEMATICS.md`,
      `PIN-MAP.md`, `CONNECTORS.md`, `dash.md` ("Window switch DRV/PASS"),
      `rear-cabin.md`, `02-HARNESS/README.md`, `CHECKLIST.md`, `CUT-LIST.md`
      (label example `K5-87 / D1-1`), `known-issues.md` ("both windows through
      full travel"). The canonical SPEC has no notation for *provisioned but not
      fitted*. **Fix:** add a status column to SPEC (LIVE / PROVISIONED /
      RESERVED / DELETED) and use it everywhere.
- [ ] **I-113 · P1 · Main feed gauge.** D-091 and `CHECKLIST.md` 3.9, `CUT-
      LIST.md`, `STATUS.md`, `SAFETY.md`: **2 AWG**. `BATTERY-INSTALL.md` (§3
      parts, §4 diagram "Class-T 150 A sized to the 4 AWG feed", §6), `SPEC.md`
      §4 (STUD row "AWG 4"), `CONNECTORS.md` DP-BAT "4 AWG", `SCHEMATICS.md` §4
      "DP-BAT (4 AWG)", `BOM.md` §2: **4 AWG**. D-061 and D-064 still say 4 AWG
      and are not marked superseded.
- [ ] **I-114 · P1 · Start relay location.** D-148: inner fender. `PIN-MAP.md`
      line 47 "mounts at the starter, not in the box"; `engine.md` line 16
      "relay mounts at the starter" and L1-S cav 1 "K9 at starter"; `factory-
      circuits/charging-starting.md`.
- [ ] **I-115 · P1 · CAN transceivers.** D-085 chose TCAN1042/1051 and
      "rejected SN65HVD230"; the car has 5 × SN65HVD230 in hand (STATUS, BENCH-
      KIT, D-140). `BUY-LIST.md` explains the bench/car split; `DCU-CLUSTER.md`
      §13 and `BOM.md` (6 × TCAN) do not. A reader of DCU-CLUSTER concludes the
      wrong part was bought. State the split once, in SPEC §10 or DCU-CLUSTER.
- [ ] **I-116 · P1 · LED figures in the canonical files.** `SPEC.md` §5–§7 Est.
      A column: "LED", "3.0 LED", "0.6 LED"; `front-chassis.md` and `rear-
      cabin.md` device tables: "0.3 LED", "0.6 LED", "Signal (18 AWG)";
      `CHANNEL-SCHEDULE.md` O2/O3 type "LED". The baseline is stock incandescent
      (D-124). Headlights may or may not be LED (`V-066` open — `TAIL-LIGHTS.md`
      states "7-inch round sealed beams" as fact, `LOADS.md` says "already LED
      housings").
- [ ] **I-117 · P1 · Display interface decision is recorded backwards.** D-150
      "**Recommended: a controller-based panel** (RA8875/RA8876)". `DCU-
      CLUSTER.md` §5a: "SETTLED — Option 3 was chosen and built: SPI with dirty
      rectangles". `OPEN.md` Q-060 asks for an SPI panel. The code went the other
      way from the last recorded decision and no D-### says so. R6 case.
- [ ] **I-118 · P1 · The PMU logic needs an RPM it cannot see.** `PMU-CONFIG.md`
      `FUEL_PUMP` = "RUN && rpm > 300", `START_RLY` = "rpm < 300"; the PMU has
      no tach input (D-076/083 — tach goes to the ICU) and D-081 says the car
      must run on the PMU **before** the ICU exists. Whether rpm arrives over
      CAN later, or a different cut-off is used until then, is written nowhere.
      Likewise `HEAD_HIGH` needs "dimmer HIGH / PASS" (D-051 says software off
      A15 — with what input?), `REVERSE` needs "inhibitor == R" — SPEC §8 says
      the inhibitor is "laddered onto one of the shared-pin inputs on L1-S", but
      every shared pin is allocated (§7) — and the wiper park logic needs a park
      sense that `front-chassis.md` L2-S cav 3 and `PIN-MAP.md` assign to an
      "A9–A16 spare" that does not exist and that SPEC does not list. These are
      design gaps; they are listed here because the *documents present them as
      settled*. Each needs a Q-### or a D-###.
- [ ] **I-119 · P2 · Phase 2A effort is 35–55 hrs (`TASKS-CAMDEN.md`), 25–40
      (`CHECKLIST.md`, `STATUS.md` phase table), 12–20 (`STATUS.md` assessment).**
- [ ] **I-120 · P2 · Money.** Project total: `STATUS.md` ~6,500–9,500 ·
      `CHECKLIST.md` ~6,100–9,200 · `BOM.md` five values, last 6,470–9,560.
      Remaining: STATUS 3,400–6,100 · CHECKLIST 3,300–6,000 · BOM 3,465–6,155 ·
      BOM "SPENT / REMAINING" 3,090–5,700. Bench kit: STATUS 110–165, `BENCH-
      KIT.md` 98–153, CHECKLIST G0.1 "~$270 Done". One money table, one owner.
- [ ] **I-121 · P2 · `TASKS-CAMDEN.md` carries lighting-body tasks** T-034,
      T-035, T-036, T-037 (tail-light aperture, sealed-beam type, headlamp unit,
      DOT modules) after D-123 moved that scope out. `lighting-body/` has no task
      file. Also T-030 (mostly answered), T-046/T-047 (see I-97), and "Checklist
      2.3 test pigtail" for housing #2 (pigtail dropped, D-141).
- [ ] **I-122 · P2 · `OPEN.md` holds two answered questions.** Q-058 has an
      answer typed in ("unique toggle button … small button that will cycle
      through"); Q-059 has "follow recommendations". The convention says answered
      items migrate to DECISIONS on the next pass; they haven't. V-041 ("will the
      tach ever feed the PMU") was answered by D-083 and is still listed. V-053
      (battery post type, "look at it") has been answerable since the battery
      arrived (D-101) and is still listed as blocking the lug order.
- [ ] **I-123 · P2 · Terminal wire range for 1.5 mm is 13–17 AWG in `SPEC.md`
      §2 and D-027/D-046, and 14–17 AWG in `BUY-LIST.md`, `BENCH-KIT.md`** (the
      pinout doc v1.2/1.3 revision, noted only in BUY-LIST). SPEC should carry
      the current figure and the revision it came from.
- [ ] **I-124 · P4 · Teensy count.** Root `README.md` "Teensy 4.1 × 2 selected,
      firmware not started"; D-089 says buy three, STATUS says three in hand and
      Stages 1–3 done. Two nodes, three boards — say both numbers once.

---

# G · `DECISIONS.md` — the append-only log needs structure to stay usable

- [ ] **I-125 · P1 · Superseded decisions are not marked at the old entry.**
      The rule (line 3) says mark the old one `SUPERSEDED BY D-0xx`. Only D-006
      is marked, and only in D-075's text. Unmarked: D-008 (16 sockets → D-067),
      D-021 (window switches → D-131), D-030 (11 relays incl. windows), D-034
      (AMPSEAL → D-052/070), D-035 and D-036 (13 connectors → D-070), D-061 and
      D-064 (4 AWG → D-091), D-076 and D-077 (→ D-083), D-080 (DP-DCU/DP-ICU
      housings swapped by D-083), D-101 and D-103 (→ D-140), D-104 (→ D-105),
      D-138 (→ D-139), D-143 (→ D-144), D-150 (→ whatever settled SPI, I-117).
      A reader who lands on D-034 has no signal it is dead. **Fix:** one-line
      `> SUPERSEDED BY D-070` under each, and a "Superseded" column in the index.
- [ ] **I-126 · P2 · The topic index stops at D-105** (I-109) and has no entry
      for D-106…D-167: CAN layouts, lighting split, incandescent baseline, faults
      found, head unit, windows, PMU receipt, orientation, bench-kit reductions,
      cluster implementation, channel schedule.
- [ ] **I-127 · P2 · Entries are not dated.** Every one is "2026-08"; section
      headers give the only chronology ("UPDATE 2026-08 — answers applied",
      "round three", "round four"). Since the whole project is 2026-08-26 to
      -30, month stamps distinguish nothing. Date to the day.
- [ ] **I-128 · P2 · One ID, several decisions.** D-051 bundles Q-011, Q-016,
      Q-020, Q-023; D-094 bundles Q-035, Q-036, Q-039; D-100 bundles V-013 and
      V-049; D-097 closes seven V-items. Cross-references then point at a bundle
      rather than a decision.
- [ ] **I-129 · P2 · Decisions belonging to other projects.** D-107, D-110,
      D-111 (lighting — mirrored into `lighting-body/DECISIONS.md`, fine), and
      **D-113 (rear disc conversion)** which is not electrical at all and has no
      other home. `00-CAR/modifications.md` P-005 still says "Reconsider `[Q-045]`"
      although D-113 answered it.
- [ ] **I-130 · P4 · The stated format is not used.** Line 24: "Format: `ID |
      decision | one-line reason`". Entries run to 40 lines with tables and H2
      sub-sections ("## What changes now", "## What this preserves"), and three H1
      blocks ("# UPDATE …", "# ROUND FOUR ANSWERS", "# CLUSTER IMPLEMENTATION")
      sit between entries. Either drop the format line or hold to a two-tier
      format: one-line decision, optional "Because" paragraph, optional table.
- [ ] **I-131 · P4 · D-136 through D-139 are four entries for one fact**
      (connector orientation), three of them provisional. Fine as history, but
      the index should point at D-139 only.

---

# H · File-level representation

- [ ] **I-132 · P2 · 48 of 66 files have no rev/owner header**, against R5.
      Stamped: CHANNEL-SCHEDULE, SPEC, 02-HARNESS/README, dash, BENCH-BRINGUP,
      CLUSTER-DESIGN, firmware/README, DEFERRED-FEATURES, HEAD-UNIT, PARTS-CHANGES,
      BENCH-KIT, LOGS, METER-SESSION, OPEN, project README, STATUS, lighting-body
      README and DECISIONS. Not stamped: everything in `00-CAR`, `01-REFERENCE`,
      `99-ARCHIVE`, plus LOADS, LADDERS, PANEL-LAYOUT, PMU-CONFIG, SCHEMATICS,
      GLOSSARY, CONNECTORS, PIN-MAP, engine, front-chassis, rear-cabin, sill-node,
      CAN-MESSAGES, DCU-CLUSTER, BATTERY-INSTALL, CHECKLIST, CUT-LIST, MIGRATION-
      LOG, SAFETY, BOM, BUY-LIST, DECISIONS, TASKS-CAMDEN, TAIL-LIGHTS, ASSISTANT,
      root README. And "Rev 2026-08" is the same on all of them — use the day.
- [ ] **I-133 · P2 · Chat-export citation markup is embedded in five files:**
      `LOADS.md` (7 × `(cite index="…">…</cite>`), `BATTERY-INSTALL.md` (6),
      `TAIL-LIGHTS.md` (3), `DCU-CLUSTER.md` (2), `BUY-LIST.md` (2). They render
      as literal angle-bracket noise and the sources they cite are not
      recoverable. Replace with plain text and, where the source matters, a URL.
- [ ] **I-134 · P2 · A user reply is embedded inline in a spec.** `DCU-CLUSTER.md`
      line 67: `> two boards for sure` sits under the Q-035 paragraph as a
      block-quote. That answer is D-094; the quote should go.
- [ ] **I-135 · P2 · Heading hierarchy is inconsistent within files.**
      `DCU-CLUSTER.md` §1–§11 are H2, §12–§15 are H1. `METER-SESSION.md` has nine
      H1s. `parts-history.md` six. `DECISIONS.md` five. `CAN-MESSAGES.md`, `PMU-
      CONFIG.md`, `LOADS.md`, `BOM.md`, `BUY-LIST.md`, `STATUS.md` each have a
      second H1 marking where the appended document starts — which is the
      accretion seam made visible. One H1 per file.
- [ ] **I-136 · P3 · No table of contents in any file over 200 lines.** I-46
      claimed this fixed; only `PARTS-CHANGES.md` has one. Over 200 lines:
      DECISIONS (1290), ASSISTANT (809), DCU-CLUSTER (691), BOM (446), LOADS
      (393), METER-SESSION (379), CHECKLIST (353), PMU-CONFIG (346), BUY-LIST
      (323), SPEC (297), CONNECTORS (287), PIN-MAP (287), CAN-MESSAGES (283),
      TAIL-LIGHTS (280), BENCH-BRINGUP (244), SCHEMATICS (235), STATUS (223),
      sill-node (216), CLUSTER-DESIGN (210).
- [ ] **I-137 · P3 · No supersession banners inside files** (I-44 claimed
      done). The pattern exists in exactly two places — `FAULT-K008-analysis.md`
      top banner and `DCU-CLUSTER.md` §5a — and both work. Every stale section in
      D above needs one, or removal.
- [ ] **I-138 · P4 · `CHECKLIST.md` numbering has gaps** (0.3; 2.22–2.25) with
      no note that something was deleted, unlike the D/Q/V rule where "gaps mean
      something closed".
- [ ] **I-139 · P4 · Wide tables.** `LOADS.md` signal-type table and `TASKS-
      CAMDEN.md` rows exceed 250 columns; they wrap badly in any renderer and are
      unreadable in a diff. Split the long "Note" cells into a sentence under the
      table.
- [ ] **I-140 · P4 · `00-CAR/known-issues.md` K-numbering.** K-009…K-014 live
      in an "UPDATE" block, K-015…K-018 in "Still broken / Confirmed working",
      K-020…K-023 in "FAULTS FOUND". One table, one status column.
- [ ] **I-141 · P4 · `TAIL-LIGHTS.md` §6 lists Q-046 and Q-047 as open** with
      §8 (appended) answering both; L-001 and D-111 exist. Same top/bottom
      pattern in the one lighting-body design file.

---

# I · Folder and index level

- [ ] **I-142 · P1 · The two READMEs are stale indexes.** Root `README.md`:
      structure tree omits `parts-history.md`, lists a `legs/` row, gives
      "D-001…D-105", and its "Current state" / "Next actions" sections (lines
      94–117) are a third STATUS — "DCU / ICU … firmware not started" against
      Stages 1–3 complete. Project `README.md`: `01-DESIGN` table omits `PANEL-
      LAYOUT.md`, `PMU-CONFIG.md`, `CHANNEL-SCHEDULE.md`; `05-BUILD` table omits
      `BENCH-KIT.md`; firmware table omits `tests/` and `cluster_render_test/`;
      the ownership table omits CHANNEL-SCHEDULE and `channels.h` (I-86). **Fix:**
      the root README holds structure and conventions only, no state; the project
      README's file tables are regenerated from the directory (I-146).
- [ ] **I-143 · P1 · `99-ARCHIVE/README.md` indexes 3 of 6 archived files.**
      Missing: `2026-08_cluster-mockup-superseded-by-sim.html`, `2026-08_
      infotainment-options-considered.md`, `2026-08_ROADMAP-superseded-by-
      STATUS.md`. Its own rule is that every archived file gets a row.
- [ ] **I-144 · P3 · The pin/channel/cavity data has no single machine-readable
      source.** `SPEC.md` §4–§8 (six tables), `PIN-MAP.md`, four leg files,
      `CHANNEL-SCHEDULE.md`, `CUT-LIST.md`, `PMU-CONFIG.md` channel names,
      `channels.h`, `cluster_core.h` labels and the future PMU client config all
      restate one 39-row × ~12-column table by hand. **Fix:** one `channels.csv`
      (or `.json`) — pin, channel, name, class, AWG, colour, leg connector, cavity,
      device end, est A, measured A, soft fuse, status — and a 40-line script that
      renders the SPEC tables, PIN-MAP, CHANNEL-SCHEDULE, CUT-LIST skeleton and
      `channels.h` from it. Drift becomes impossible rather than forbidden.
- [ ] **I-145 · P3 · No ID registry.** One table, one row per D/Q/V/A/T/K/M/I/L
      ID: what it is, status (open / closed by … / superseded by …), where it
      lives. It is the only thing that makes I-104 fixable once and checkable
      afterwards. Generate it from the files (the IDs are already regular).
- [ ] **I-146 · P3 · No checks.** A 60-line script in `07-PROCESS/tools/` that
      fails on: an ID cited bare that the registry says is closed; a relative
      path that doesn't resolve; a three-digit "Checklist NNN"; a `(cite index`;
      a file without the R5 header; a `legs/` path; more than one H1. Run it
      before "give me the diff". Every finding in sections E and H would have
      been caught at write time.
- [ ] **I-147 · P3 · `01-REFERENCE/README.md` breaks its own rule.** "Index
      everything you drop in" — `Part Dates - Sheet1.pdf` (the source of
      `00-CAR/parts-history.md`) is not in the table. `LOGS.md` says photos go in
      `01-REFERENCE/photos/<zone>/` — the folder doesn't exist; create it with a
      README so the convention survives until the first photo. The TE catalogue
      row still says `[V-062] confirm which series it covers` (closed, D-114).
      "Still wanted" lists a DT contact datasheet "vs window stall".
- [ ] **I-148 · P3 · `factory-circuits/README.md` has two Status tables** (lines
      66–73 marked superseded but kept; 119–135 current), a source path that is
      wrong (I-107), and "Cruise control detail — pending V-023" (closed, D-097).
      The circuit files' "what this means for the rebuild" tables still carry
      `C2-B2`-style cavities (27 refs across 7 files) — the README banner warns,
      but the columns could simply be replaced with the L-codes now that they
      are final.
- [ ] **I-149 · P3 · `lighting-body/` has decisions and no tasks, questions or
      status.** Its open items sit in `electrical-pmu/07-PROCESS/TASKS-CAMDEN.md`
      (I-121) and its `DECISIONS.md` "Open" table lists **V-058 (display nit
      rating)** — an ICU item. Give it `OPEN.md` and `TASKS.md`, or state that the
      electrical project's process files serve both and tag rows by project.
- [ ] **I-150 · P3 · `00-CAR/` has no README** and no note that `modifications.md`
      + `parts-history.md` + `vehicle.md` overlap on the same facts (mileage,
      fuel pump, battery, PMU). `vehicle.md` "Electrical — planned: see
      `02-PROJECTS/electrical-pmu/SPEC.md`" is a dead path. `modifications.md`
      "Torque and spec quick reference" is four `[to fill]` rows waiting on an
      FSM the reference index lists as "still wanted" — say so in the table.
- [ ] **I-151 · P4 · Scope leakage in `BOM.md`.** The "Lighting & body project
      — separate budget" table (lines 415–427) lives in the electrical BOM.
      `lighting-body/` has no BOM. Move it.
- [ ] **I-152 · P4 · `PANEL-LAYOUT.md` and `CUT-LIST.md` are templates waiting on
      T-007 / T-008** and say so — good. But `CUT-LIST.md` defers L1-S and L3-S
      rows to "*see PIN-MAP*", which is the stale file (I-83). When PIN-MAP is
      regenerated (I-144) the cut list can be too.

---

# J · Firmware and repository

- [ ] **I-153 · P1 · Nothing since 2026-08-28 is committed.** Three commits total,
      all on 08-28. `STATUS.md`, `SPEC.md`, `DECISIONS.md`, `OPEN.md`, `TASKS-
      CAMDEN.md`, `CHECKLIST.md`, `PMU-CONFIG.md`, `CHANNEL-SCHEDULE.md`,
      `ASSISTANT.md` and the whole `firmware/` tree have changed since. `LOGS.md`
      has a "Tagged in git?" column that nothing will ever tick at this rate.
      Commit at "give me the diff" — make it the last line of the §7 close.
- [ ] **I-154 · P1 · Three identical copies of `can_map.h`** (`icu/`,
      `can_map_test/`, `can_loopback_test/`, same MD5). The README says "one
      source of truth — there is no second copy to drift"; there are two. Arduino
      needs the header beside the sketch, so either symlink, or make the test
      sketches `#include "../icu/can_map.h"` the way `sim_win32.cpp` does, or
      accept the copies and say which is master.
- [ ] **I-155 · P2 · `firmware/README.md` layout omits `tests/` and `cluster_
      render_test/`.** The 415-assertion regression suite that `STATUS.md` calls
      out is invisible to the folder map, and `cluster_render_test/` uses an older
      `cluster.h` renderer that predates `cluster_core.h` — it is superseded and
      not in the superseded list.
- [ ] **I-156 · P2 · Built binaries are in the tree and in git** (`icu_sim/
      sim.exe` 161 KB, `tests/test.exe` 584 KB). There is no root `.gitignore`
      (only `.idea/.gitignore`), so `.idea/`, both `.exe`s and every large PDF are
      versioned. `.git/objects` already holds a 29 MB, a 24 MB, a 13.7 MB and a
      3.7 MB blob. Add `.gitignore` (`*.exe`, `.idea/`) and move the four large
      PDFs/STEP (85 MB) to Git LFS or a release asset.
- [ ] **I-157 · P2 · `channels.h` is the third copy of the amp table** (I-86)
      and its comment "THE ONE FILE TO EDIT AFTER THE METER SESSION" contradicts
      `CHANNEL-SCHEDULE.md` "type the measured column into **one** place". Both
      say they are the one place. Generate one from the other (I-144).
- [ ] **I-158 · P3 · No build script for the test suite** — the command lives in
      a comment in `test_suite.cpp`; `icu_sim/build.bat` exists but nothing runs
      the tests. A `tests/run.bat` and a line in the README ("run after any change
      to cluster_core.h") makes the regression suite a habit instead of a memory.
- [ ] **I-159 · P4 · `firmware/README.md` hardcodes `C:\Users\Camden Thomas\
      Downloads\w64devkit\`** while `build.bat` says `C:\w64devkit`. One location.
- [ ] **I-160 · P4 · Firmware has no version.** `LOGS.md` firmware version log is
      empty; `STATUS.md` says ~1000 lines and 415 assertions exist. A `#define
      ICU_FW_VERSION` in `icu.ino` printed at boot, plus a git tag, is the whole
      mechanism.

---

# K · Things that would change how the project is read

- [ ] **I-161 · P3 · A wiring diagram set.** Forward-work item X-01 says it:
      the project has no visual wiring reference at all — 61 documents and not
      one drawing of a leg. Generate one page per leg from the channel table
      (I-144); even a boxes-and-lines SVG per connector would be the most-used
      document in the shop.
- [ ] **I-162 · P3 · One architecture picture.** PMU → dash post → 14 leg
      receptacles → 4 legs → devices, with the sill node, DP-ICU/DP-DCU, the
      battery backbone and the two CAN buses. The Rev A HTML had one (C1–C7); the
      current design has none.
- [ ] **I-163 · P3 · A "state of every cavity" export.** 39 PMU cavities + 14
      leg connectors + D1/D2 + 4 drops: what is LIVE, PROVISIONED, RESERVED,
      SPARE. It is the question every later session asks and today it takes five
      files to answer. Falls out of I-144.
- [ ] **I-164 · P3 · A CHANGELOG.** DECISIONS records *why*; nothing records
      *what changed in which file when*. `LOGS.md` "Session log" is empty. The
      "give me the diff" output (§7) is exactly a changelog entry — append it to
      `07-PROCESS/CHANGELOG.md` each session and the session log fills itself.
- [ ] **I-165 · P4 · `STATUS.md` "If you have been away a year" names five
      files.** After this audit the honest list is: STATUS → GLOSSARY → the
      channel table (I-144) → the ID registry (I-145) → CHECKLIST. Update the
      handover path when those exist.

---

## Suggested order

1. **I-71, I-72, I-73** — the Claude Project and `CLAUDE.md`. Ten minutes;
   every future session benefits.
2. **I-75** — split `ASSISTANT.md` into rules and logs.
3. **I-144, I-145, I-146** — the channel table, the ID registry, the checker.
   Everything in C, E and F becomes a generate-and-diff instead of a hand sweep.
4. **I-83, I-85, I-95** — regenerate PIN-MAP, rewrite LOADS, revise STATUS in
   place. The three files people will actually open next.
5. **I-112, I-113, I-125** — the windows status column, 2 AWG everywhere, and
   the SUPERSEDED marks.
6. Section D, one file per session, using `DEFERRED-FEATURES.md` as the
   pattern.
7. **I-153, I-156** — commit, `.gitignore`, LFS.

## What is fine and should be left alone

`DEFERRED-FEATURES.md`, `HEAD-UNIT.md`, `PARTS-CHANGES.md` (bar I-102),
`SAFETY.md`, `GLOSSARY.md` (bar I-110), `LADDERS.md` (bar step numbers),
`FAULT-K008-analysis.md`, `MIGRATION-LOG.md`, `CHANNEL-SCHEDULE.md` (bar
I-111), `BENCH-KIT.md`, `CUT-LIST.md`, `firmware/README.md` (bar I-155/159),
`lighting-body/README.md`, `OEM-RECORD.md` (bar I-105), the ten factory circuit
decodes above their rebuild tables, and the numbered-folder structure itself.
The folder design is right; the files inside it need to be brought up to the
standard the folder design implies.

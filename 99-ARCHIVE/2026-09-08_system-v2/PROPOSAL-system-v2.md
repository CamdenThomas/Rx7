# RX-7 SYSTEM v2 — the proposal

*2026-09-08 · rev b (2026-09-08, after Camden's rulings on §6 — §2.4, the completion workflow and §6 rewritten; step 0 done) · owns: the plan to take the Rx7 tree from the 2026-09-03 "data, rendered" system to a phase-driven set of CLI workflows and a 00-CAR that is the car's owner's + service manual. Nothing in the tree is changed by this document. Read §0 (what I found), then §2 (the target), then §5 (the order of work). §6 is what I need from you.*

## Contents

0 · What I read and what I found · 1 · The seven faults in the current system · 2 · The target — one record, one tool, one lifecycle · 3 · The workflows · 4 · Where I differ from your outline · 5 · Migration, step by step · 6 · Your calls before we start · A · The collision repair list

---

## 0 · What I read and what I found

Read in full: `CLAUDE.md` (which now carries the whole of `ASSISTANT.md` §0–§10 and R1–R11), `README.md`, `tools/rx7.py`, `tools/answers.py`, `apply-rx7-changes.py`, every `README` / `QUESTIONS` / `DECISIONS` / `views.py` / `view.json` of the three projects, every template of `00-CAR`, `01-REFERENCE` and `electrical-build`, the luxury and engine-swap templates and data, the 00-CAR data (7 tables, 337 rows), `sources.csv`, the factory-circuits and photos READMEs, the archive index, the `rx7-answer-cycle` skill, and the Claude Project's `SOURCE-OF-TRUTH.md` and both `PENDING-*` docs. Skimmed by heading: `DESIGN.md`, `INSTALL.md`, `SHOPPING-LIST.md`, the harness renderer. Ran `rx7.py tables` and `check` on a copy of every project (all clean except luxury, where I had not staged four of its CSVs — not a real failure).

**Where the build stands.** Nothing bought, cut or crimped. Four carts wait; §0 of the electrical `QUESTIONS.md` is the finishing list (A1–A7 desk, B strip A/C, C the measurement day, D arrivals, E the install plan, F the ICU on the bench, G fourteen improvement items from the production-car comparison). Electrical decisions run to D-277, luxury to D-315; the swap has none of its own yet. The tree is genuinely good: one tool, facts in rows, six harness sheets rendered from the same rows, cross-project joins (luxury reads electrical live), eight electrical checks and seven luxury checks that refuse a bad build.

**What is broken today** (evidence in Appendix A): `apply-rx7-changes.py` was written in chat from the Claude-Project PENDING docs, numbered from **D-249 / Q-112**, and ran this afternoon against a tree that had already spent **D-249–D-253 and Q-112, Q-116–Q-121** on other rulings. Its `patch()` skips when the marker text is already present, so the new decisions were silently *not* written while the data edits and question packets *were*. Result: seven question IDs each carry two unrelated questions; `D-247` was deleted but never replaced; three data rows and a §0 line cite a "D-249" that means the plunger switch while `DECISIONS.md` D-249 means oil pressure; one template still cites the deleted D-247. `build` reports clean because nothing checks IDs or prose.

That single incident is every fault below at once: two records (Project vs tree), IDs as prose, prose as the only home of status, a patch script guessing at anchors, and no workflow whose only job is to look for exactly this.

---

## 1 · The seven faults in the current system

**F1 · Two records.** The Claude Project holds ten stale docs plus a `SOURCE-OF-TRUTH.md` whose "next IDs" line is 24 decisions behind the tree, plus two PENDING docs that were "the record" for three days. Work that cannot reach the tree gets numbered in chat and lands later, out of order. Every session has to be told which of the two to believe.

**F2 · IDs and status live in prose.** `D-###` and `Q-###` exist only as bold headings in two Markdown files. The "next ID" is typed in `CLAUDE.md`, both README templates and `SOURCE-OF-TRUTH.md`. A question's state (open / closed / moved) is the section it sits in plus a row in §3 plus a banner line at the top. No check can see a duplicate, a dangling cite, a closed question that is still open, or a decision that no row or template ever mentions.

**F3 · Prose states facts that have rows.** `{{table}}` and named views cover tables; there is no scalar view, so every count, total, next-ID, "ten questions are left", "Latest:" line and every `(D-###)` in a sentence is typed. The one you named — *data changes, the description doesn't* — is structural: the template has no way to *point at* a cell, so it copies the value.

**F4 · Logs inside state files.** The electrical `QUESTIONS.md` opens with thirteen `> **date.**` banner paragraphs — a changelog at the top of a file whose own rule is "nothing here is a log". `DECISIONS.md`'s **Latest** line is 1,100 words. Both grow every session and both are hand-typed.

**F5 · The workflow is mode-driven, not phase-driven.** `DECIDE / GENERATE / AUDIT / BUILD` describe what Claude does in a session, not where a project is. There is no proposal step (the engine swap has a hand-over table and nothing else to start from), no critique step that is forbidden from changing things, no completion step beyond four bullets in §8, and the planning loop needs you to prompt each turn. The answer cycle (§10) is the one routine that is written down end to end — and it is the one that works.

**F6 · 00-CAR is a good spec sheet, not a manual.** It has identity, 230 cited specs, a mod log, a 5-row service table, fluids, issues and a purchase history. It has no maintenance schedule, no procedures (jump-start, disconnect, fuse map, PMU restore, limp-home), no as-fitted system descriptions, no diagrams, no way for a finished project to *become* a chapter. Some cells carry Markdown bold and narrative ("**Never fully drained.** ~half lost…") — a fact and its commentary in one field, which no view can use.

**F7 · The chat is the CLI.** Sessions run through the device bridge from Cowork; when the bound machine is off, the fallback is a patch script that guesses anchors (F1 again). You already run Claude Code in the repo; the workflows should live *in* the repo as skills and run there, where `rx7.py` runs and `git` is local.

---

## 2 · The target — one record, one tool, one lifecycle

### 2.1 · The tree

```
Rx7\
├── CLAUDE.md                  <- 40 lines: the lifecycle, the workflows, "run /rx7-status first"
├── README.md                  <- structure and conventions (as now, shorter)
├── .claude\skills\            <- THE WORKFLOWS, versioned with the repo, appear as /rx7-* in Claude Code
│   ├── rx7-status\  rx7-propose\  rx7-plan\  rx7-answers\  rx7-criticize\
│   ├── rx7-clean\   rx7-build\    rx7-complete\  rx7-log\  rx7-overview\
├── tools\
│   ├── rx7.py                 <- the data tool, + registry, lint, scalar views, cross-project reads
│   ├── scaffold.py            <- /rx7-propose: builds a project skeleton from the standard
│   ├── complete.py            <- /rx7-complete: folds a project into 00-CAR, archives its process
│   └── answers.py             <- as now
├── 00-CAR\                    <- THE MANUAL (see 2.4)
│   ├── data\  templates\  views.py  view.json
│   ├── systems\<system>\      <- one folder per finished project: ONLY the as-built facts (tables, diagrams) and the service pages
│   ├── *.md                   <- rendered chapters
│   └── MANUAL.html            <- the whole manual, one file, tabs, search, every ID a link
├── 01-REFERENCE\              <- unchanged
├── 02-PROJECTS\<project>\     <- the v2 skeleton (2.2)
└── 99-ARCHIVE\                <- unchanged; /rx7-complete writes here
```

The Claude Project keeps **one** doc — a pointer to the repo — and the other twelve are deleted. Nothing is ever queued there again: if the machine is off, the work waits, or it is done in the CLI on the machine that is on.

### 2.2 · The project skeleton, v2

```
<project>\
├── project.csv        <- one row: name, goal, phase, opened, owner-of-record, next-gate
├── work.csv           <- the plan as data: every task, agent- or Camden-owned, with state and gate
├── data\              <- facts, as now
│   ├── questions\Q-###.md   <- one file per packet (Ask · Options · Recommend · Blocks · ANSWER:)
│   └── decisions\D-###.md   <- one file per ruling (decision · his words · reasoning · supersedes · consequences)
├── questions.csv      <- id, title, section, status, opened, closer, blocks, owner   (the index)
├── decisions.csv      <- id, system, title, date, supersedes, closes, status         (the index)
├── log.csv            <- date, workflow, ids touched, one line    (append-only; renders LOG.md and the banners)
├── templates\         <- prose, as now, with cell references (2.3)
├── views.py           <- derivations and checks, as now
├── reviews\           <- /rx7-criticize output: CRITIQUE-<date>.md, findings as C-###; never edited after
├── QUESTIONS.md  DECISIONS.md  LOG.md  README.md      <- RENDERED
└── 01-DESIGN\ 02-SHOPPING\ 03-INSTALL\ VIEW.html      <- rendered, as now
```

**Questions and decisions become data.** This is the backend change that makes today's collision impossible and makes F2–F4 checkable:

- `rx7.py add questions id=Q-134 …` refuses if `Q-134` exists anywhere in the tree — the registry scans every project's index, every `data/*/`, and the archive. Next IDs are *computed* (`{{next_id:D}}`), never typed.
- A packet's body is one Markdown file; you still answer in place under `**ANSWER:**`, exactly as now. `answers.py` reads the folder instead of a regex over a 54 KB file.
- The rendered `QUESTIONS.md` is built from the index: §0 from `work.csv` (owner = Camden, state open), §1/§2 by `section`, §3 from `status = closed` with the closer, §4 from `status = moved`. It cannot disagree with itself because it has one source.
- A decision that is superseded gets `status = superseded` and leaves the rendered file automatically; its Markdown stays in `data/decisions/` as the chronological history — no more copying superseded entries to the archive by hand.
- The **Latest** line and the `> **date.**` banners are rendered from `log.csv` (last N entries), not typed.

**New checks, generic to every project** (they run inside `check`, so `build` refuses on them):

| Check | Refuses when |
|---|---|
| `c_registry` | a D/Q/K/M/P/S/SP/C id is defined twice anywhere in the tree; an id is cited in any CSV cell, packet, decision, template or `CLAUDE.md` and defined nowhere; a question is `closed` with no closer, or `open` while a decision names it as closed |
| `c_prose_ids` | a template cites an id that is superseded or moved without the `→ closer` form (R7) |
| `c_retired` | any word in `retired.csv` (a term of art a ruling retired, with the D that retired it) appears in the live tree outside `data/decisions/` and `99-ARCHIVE/` — the "grep for the corpse" step, made permanent |
| `c_headers` | a template lacks the `*Rev · owns:*` line, has more than one H1, or is past 200 lines with no Contents (R5) |
| `c_rev` | a template's `Rev` date is older than the newest row of any table it renders (the prose is older than its facts — the exact smell behind F3) |
| `c_links` | a relative link in a template resolves to nothing |
| `c_work` | `work.csv` has a done item whose gate is still open, or an open Camden item with no packet behind it |
| `c_phase` | the project is in a phase whose entry gate `views.py` reports unmet (2.5) |

### 2.3 · Templates that cannot drift — scalar views and cell references

Three new placeholders in `rx7.py`, usable inline in a sentence:

- `{{cell:cavities|L3-S1 7|lands_on}}` — the value of one cell. The sentence *points at* the fact instead of copying it. If the row is deleted the build refuses; if it changes the sentence changes.
- `{{param:battery_case_mm}}` — a project parameter (the `params` table already exists; this makes it usable in prose).
- `{{next_id:Q}}`, `{{count:questions|status=open}}`, `{{latest:5}}` — the numbers that are typed today in `CLAUDE.md`, the README templates and the banner lines.

With these, the rule R3 gets a mechanical form: **a template may not contain a number or an id that has a row without going through a placeholder.** `/rx7-clean` enforces it (a lint that lists every bare number and bare id in a template beside the row it could point at; the agent converts them), and after one pass the class of error you named stops recurring for anything that has a home.

For facts that have *no* row — a rule explained, a reason — the prose stays prose, and `c_rev` plus the critique workflow are the net.

### 2.4 · 00-CAR as the owner's + service manual

The manual is chapters; every chapter is rendered from tables; `MANUAL.html` is the whole thing in one file with tabs and search, the way `VIEW.html` is for a project. Nothing here is written by a project directly — a project *folds in* through `/rx7-complete`, which is the only way content arrives.

| Chapter (rendered) | Tables behind it | What it holds |
|---|---|---|
| `README.md` | — | the index, how to read the manual, what the car is in three lines |
| `1-VEHICLE.md` | `vehicle` (key/value), `as_fitted` | identity, VIN, mileage; every system *as fitted today* — engine, fuel, ignition, electrical, brakes, suspension — one row per system with its `systems/` chapter link. Replaces `vehicle.md`'s current/planned tables; "planned" moves to projects |
| `2-SPECS.md` | `specs` | as now — 230 cited factory numbers, by category |
| `3-MAINTENANCE.md` | `intervals`, `service`, `fluids` | **the schedule**: item · interval (miles / months) · spec · last done · next due (computed) — and the service log beneath it, one row per visit (date, mileage, work, parts used, fluids, torques, who, notes). `fluids` becomes spec-only; "last changed" is a view of `service` |
| `4-SYSTEMS\<system>.md` | `systems/<s>/data/…` | one chapter per finished project: what it is, how it is wired/plumbed/mounted (the design tables and diagrams as built), configuration (the PMU sheet, the ICU config), commissioning values recorded at shakedown |
| `5-PROCEDURES.md` | `procedures` + `procedures/*.md` | how-to pages: jump-start, master disconnect, fuse-lid card (G10 — rendered), PMU config restore, limp-home (Q-121), battery storage, what to check before a mountain drive. Each procedure is a data row (id, system, title, when, tools) with a body file, so a system chapter can list its own |
| `6-PARTS.md` | `parts_fitted`, `parts_history` | the parts catalogue of the car as it is: every fitted part with maker, number, source, price, date fitted, replaces-what — and the purchase history beneath it (the current `parts_history` becomes purchase records; "fitted" is a state, not a group name) |
| `7-ISSUES.md` | `issues` | as now, K-###, with `status` a controlled value (open / designed-out / fixed / deleted) instead of narrative |
| `8-HISTORY.md` | `mods`, `log` | M-### by date; the completed projects with their dates and the link to their archived process |
| `9-DIAGRAMS.md` | — | every rendered sheet in `systems/*/diagrams/`, one page, thumbnails linked |

Rules for the manual's data: cells are values, not sentences (`last_changed = 2026-07` and `note = …`, not `**Jul 2026**` in the value); dates are ISO; statuses are controlled vocabularies checked by `views.py`; every number cites `S-###` or a service-log row.

**`systems/` holds what an OEM manual would hold, and nothing else.** When a project completes, it is split three ways, and only the first two reach the manual (Camden's ruling on §6 item 2):

| Goes to | What | Examples from the electrical build |
|---|---|---|
| `00-CAR/systems/electrical/` — **information and diagrams** | the facts of the car as it physically is: the as-built tables (every pin, cavity, fuse, relay, conductor, ladder value, device terminal, ground), the rendered sheets (HARNESS, the four legs, the dash node), the configuration as loaded (the PMU sheet, the ICU config), the values recorded at commissioning | `data/` (cavities, housings, pins, fuses, relays, node_conductors, ladders, devices, grounds, logic, icu_channels) · `diagrams/` · the config sheet · the shakedown numbers |
| `00-CAR/systems/electrical/` — **service** | how to work on it: procedures, tests, torque / crimp / label specs, the fuse-lid card, fault-finding by symptom, what to check at what interval, the recovery paths | the install plan's test appendix, label format, migration-log loop, limp-home and restore procedures, the shakedown card — rewritten as service pages, not build steps |
| `99-ARCHIVE/<date>_<project>/` — **process** | how it got there: the decisions and their reasoning, every question and answer, the work list, the log, the critiques, the shopping lists and carts, the templates of the build documents | `DECISIONS.md` and `data/decisions/`, `QUESTIONS.md` and `data/questions/`, `work.csv`, `log.csv`, `reviews/`, `02-SHOPPING/`, the build-phase templates |

The test for every row and paragraph at completion: *is this a fact about the car as it sits in the driveway, or a service instruction for it?* If yes, it stays; if it is about how or why the design was reached, it is archived. A decision's *outcome* is a fact (the brake wakes the module through a plunger switch on the pedal — that is in the cavity row); the decision itself, with its reasoning and what it superseded, is process. The manual never cites `D-` or `Q-` ids; it cites `S-` sources, `SP-` specs and its own procedure and part ids. The archive keeps every id forever, so anyone who wants the *why* can still find it.

The manual's chapters read `systems/<s>/data/` live, the same join luxury uses on electrical today — so the tables are still one home per fact; they have simply moved from a project to the car.

### 2.5 · The lifecycle — phases and gates

A project is always in exactly one phase; `project.csv` says which; each workflow is allowed in some phases and not others; each phase has an entry gate that `views.py` can evaluate and `c_phase` enforces.

| Phase | Enter when | What is allowed | Leave when |
|---|---|---|---|
| **0 PROPOSED** | `/rx7-propose` ran | `/rx7-overview`, `/rx7-plan` | the goal statement is ruled (D-x01) and the first work list exists |
| **1 PLANNING** | goal ruled | `/rx7-plan` (cycles), `/rx7-answers`, `/rx7-criticize`, `/rx7-clean`, `/rx7-overview` | every `work.csv` design item done · every §1 question closed · a critique with no open Major finding · build clean → **design freeze** (a D entry) |
| **2 SOURCING** | design frozen | `/rx7-answers` (§2 only), `/rx7-clean`; design edits refused unless a D unfreezes | carts paid, parts counted against the list (the arrival check is a work item) |
| **3 BUILDING** | parts in hand | `/rx7-build` (shop), `/rx7-answers`, `/rx7-clean`, `/rx7-criticize` (on the install plan) | every install step done, every measurement box filled, shakedown recorded |
| **4 COMPLETE** | shakedown recorded | `/rx7-complete` only | the fold-in has run: chapters rendered, archive written, `02-PROJECTS/<p>` gone |

The **electrical build is in phase 1** by this table (§1 still has packets; G-list items are open work). The **luxury package is phase 1**, the **engine swap is phase 0**. Design freeze is what "the carts are paid" was standing in for — it becomes an explicit ruling with a gate, and shopping gets its own phase so that a design edit during sourcing is a *decision*, not a drift.

---

## 3 · The workflows

Every workflow is a skill in `.claude/skills/rx7-<name>/SKILL.md`, invoked as `/rx7-<name> [project]` in Claude Code, in the repo, on whichever machine you are on. Each has the same shape: **entry gate → read → do → build → log → report**, and each ends by appending one `log.csv` row and printing the ten-line diff you already use. Every step that can be a script is a script; the agent's judgement is spent only where the SKILL says so. `git commit` stays yours (the report ends with the suggested commit line).

### /rx7-status `[project]`  *(new — the session opener)*
Prints: phase per project, next IDs (computed), open Camden items, answered-but-unapplied packets, the last five log lines, and `check` for every project. Replaces "read ASSISTANT.md, QUESTIONS §0, tables" and the mode question. Every other workflow calls it first.

### /rx7-propose `<name> "<goal>"`  *(your "project proposal")*
Gate: name not taken. Does: `scaffold.py` builds the v2 skeleton with the standard tables for the project's *kind* (electrical / mechanical / software / body — the kind sets which CSVs are seeded, e.g. an electrical project starts with `cavities housings pins …`, a mechanical one with `components fasteners torques procedures`); writes `project.csv` (phase 0); writes `D-x01` as a *draft* goal statement in your words; then the agent reads `00-CAR` and every sibling project's boundary tables and writes the **opening question set** — every decision the goal implies that only you can make, each as a packet with options and a recommendation, easiest first — and the first `work.csv` (agent items: research, boundary tables, seams with other projects). Output: the folder, `QUESTIONS.md` rendered, a README that says what this project is and is not. You answer the packets; the next `/rx7-plan` starts phase 1.

### /rx7-plan `<project> [--cycles N] [--until <condition>]`  *(your "project planning" — the self-driving loop)*
Gate: phase 0 or 1. One cycle is:

1. **Harvest** — `answers.py`; if any packet is answered, run the answer cycle in full (it is the same routine as today's §10, now `/rx7-answers`, and `/rx7-plan` calls it rather than duplicating it).
2. **Pick** — the next agent-owned item in `work.csv` in order (state open, gate met). If none: stop, report.
3. **Do** — the item, through data / templates / views only. If it needs your call, it *becomes* a packet (Ask · Options · Recommend · Blocks · one-word ask) and a Camden-owned work item, and the loop moves on. If it exposes a fact that has no row, the row is added (this is where the design grows).
4. **Build** — `rx7.py -p <project> build`; a refusal is fixed in the data or becomes a packet; never worked around.
5. **Log** — one `log.csv` row; the cycle count.

Stop conditions: no agent-owned item left · N cycles · a check that cannot be satisfied without you · the credit budget you set in the call. Report: what got done (by work id), what now waits on you (by Q id, with the one-word ask), what changed in the carts, what is next. **You are prompted once** — at the start — and the loop grinds the list; your only input between calls is answering packets in place.

### /rx7-answers `[project|all]`  *(as today's §10 / the existing skill, kept)*
Same eight steps, with three changes: it reads packets from `data/questions/`, it writes decisions as `data/decisions/D-###.md` + an index row (so the ID is reserved before a word is written), and steps 4–7 (seams, corpse, record) are the `c_registry` / `c_retired` / `c_rev` checks plus a `log.csv` row — they run inside `build`, so they cannot be skipped.

### /rx7-criticize `<project> [--scope design|shopping|install|all]`  *(your "project criticize")*
Gate: any phase ≥ 1. **Changes nothing.** Spawns three isolated reviewers — this is your three-workers test made into a process: a *design reviewer* who sees only `01-DESIGN/` and the data; a *buyer* who sees only `02-SHOPPING/`; a *builder* who sees only `03-INSTALL/` — plus a fourth, the *auditor*, who sees everything and looks for contradictions between the three and against `DECISIONS.md`. Each hunts one class of error: logic holes, magic numbers, a step that assumes something the design never fixed, a part that fits nothing, a cavity that two conductors claim, a ruling the prose forgot. Output: `reviews/CRITIQUE-<date>.md` — findings `C-###` (permanent ids, registry-checked), each with severity (Blocker / Major / Minor / Nit), where, what, why it matters, and *what would settle it* — and a `log.csv` row. Nothing else is touched. Findings enter the plan only through the next `/rx7-plan`, which turns each one into a work item (agent) or a packet (you), citing `C-###`. The phase-1 exit gate reads "no open Major" from this file.

### /rx7-clean `[project|all]`  *(your "project clean")*
Gate: none. Two halves. **The script half** is `rx7.py lint`: every check in 2.2 plus the bare-number / bare-id lint of 2.3, link resolution, header/Rev/Contents rules, banner presence, `view.json` tabs that exist, `retired.csv` sweep. **The agent half**: for each template, read it *against its rows* (one `sql` per section) and fix prose that says something the data does not — smallest edits, no design changes; anything that would be a design change becomes a packet. Then `build -a`, then the diff. It is what you run before a commit and what `/rx7-complete` requires clean.

### /rx7-build `<project>`  *(the shop assistant — your "project build assistant")*
Gate: phase 3. The install plan's steps are `steps.csv` (rendered into `INSTALL.md` as today's numbered boxes): id, phase, text, gate, measurement fields, state, done-date. You say what you did — "did 2.4 through 2.7, alternator at 2000 warm reads 14.1, stall on the left pop-up 12.8 A" — and the agent: sets the step rows, writes every number to its home (`loads.measured_a`, `specs`, `service`), opens a `K-` for anything found wrong, opens a packet if a measurement contradicts the design, rebuilds, and prints **the next step with its gate and its tools** — one step, not the plan. `MIGRATION-LOG` and the shakedown card are views of `steps.csv`. Photos you name land in `01-REFERENCE/photos/` and get indexed the same call.

### /rx7-complete `<project>`  *(your "project completion")*
Gate: phase 3 with every step done and shakedown recorded; `/rx7-clean` clean; `QUESTIONS.md` empty or every remaining packet moved to a named project. `complete.py` then, in one script with a dry run first, does the three-way split of §2.4: (1) every fitted part → `parts_fitted`, purchase rows reconciled, every `P-` → `M-`; (2) every learned number → `specs` / `service` / the system's own tables, cited to the step that measured it; (3) the as-built tables, `views.py`, `diagrams/` and the config sheets → `00-CAR/systems/<system>/` as the **information** section — stripped of every `D-`/`Q-` cite and every "why" note (the strip is a lint; anything it cannot classify is listed for you); (4) the install plan's tests, specs, label rules, recovery procedures and the shakedown card → the **service** section as procedure pages, and `intervals` rows for anything with a check interval; (5) `as_fitted` updated; the old 00-CAR text that described the previous state is *replaced*, not appended to; (6) decisions, questions, work, log, reviews, shopping and the build-phase templates → `99-ARCHIVE/<date>_<project>/` with a README that indexes them; (7) `02-PROJECTS/<project>` removed; every sibling project's boundary reads re-pointed (`db.other("electrical")` now resolves to `systems/electrical`); (8) `build -a`, `MANUAL.html` rendered; (9) the log row and the diff. The manual is clean the moment the script ends, and it reads like a manual: numbers, drawings, procedures — no history.

### /rx7-log `"<what you did>" [--mileage N] [--date …]`  *(new — the service log, car-level)*
No project needed. "Oil change, Mobil 1 HM 10W-30, 153,400, filter Duralast X" → one `service` row, `intervals.next_due` recomputed, a `parts_history` row if a part is named, `build -p 00-CAR`. This is how the manual stays a *service log* between projects.

### /rx7-overview `<project|topic>`  *(the one chat workflow — your "project overview discussion")*
Run in the Cowork / desktop chat, not the CLI. Reads `/rx7-status` and the project's README + DESIGN headings only; answers in short paragraphs; **writes nothing to the tree** — if the conversation reaches a decision, it ends with "say the word and I'll log it: `D-###` — <one line>", and the logging happens in the next `/rx7-answers` or `/rx7-plan` in the CLI. The register: broad, few words, options over detail, drawings when a picture is shorter than a paragraph.

### /rx7-diff  *(session close, as §9 today)*
Unchanged: `build -a`, the ten lines, nothing else.

**What Camden does, in this system:** answers packets in place · runs the workflows · does the physical work and tells `/rx7-build` what happened · commits. Nothing else. If a workflow ever asks you a question mid-run, that is a bug in the skill.

---

## 4 · Where I differ from your outline, and why

**Questions and decisions as data, not prose.** Your outline keeps the process in Markdown and adds a clean-scan to catch drift. I would rather make the drift impossible where it can be: the index + one-file-per-packet form keeps your answering habit exactly as it is, and buys the registry, computed next-IDs, automatic supersession and a rendered `QUESTIONS.md` that has one source. Today's collision could not have happened.

**Cell references over a clean-scan.** The scan stays (it is `/rx7-clean`), but the primary fix for "data changes, text doesn't" is that the text stops containing the data. A clean-scan finds a stale sentence after the fact; `{{cell}}` means the sentence was never stale.

**Criticize produces findings with ids, and only the planner acts on them.** You asked that it change nothing — agreed, and I would go one further: its output is an immutable file with permanent `C-###` ids, so a finding is cited like a decision, and the phase gate can read it.

**A status command and a log command that you did not list.** `/rx7-status` replaces the "read these three things first" session opener with one call, and `/rx7-log` is what makes 00-CAR a service log on a random Tuesday when no project is running.

**Phases with gates, not just workflows.** Your six workflows are the right six; what makes them *linear* is that each is allowed only in some phases, and a phase ends by a gate the tool can evaluate. That is what turns "an endless sea of details" into "the next thing".

**Finished projects are split at completion — information + service into `00-CAR/systems/`, process into the archive** (Camden's ruling, §6 item 2, replacing my first draft's move-it-whole). The as-built tables keep one home per fact and the diagrams stay renderable; the reasoning is archived under the project's own folder so the manual reads like an OEM manual, not an engineering log.

**The Claude Project is emptied.** One pointer doc. The stale snapshot has cost more sessions than it saved, and the PENDING mechanism is how today's collision was manufactured.

**Kept as-is, deliberately:** `rx7.py` and its CSV + SQLite core (it is right), `views.py` per project, `VIEW.html`, the harness renderer, the answer cycle's eight steps, the R-rules (R1–R11 survive; several become checks), permanent ids and their ranges (electrical 1–299, luxury 300–399, swap 400–499, car-level `K/M/P/SP/S` as now; `C` for critique findings, per project, from 001).

---

## 5 · Migration, step by step

Eleven steps, in order; each is one CLI session (or one `/rx7-*` call once the skill exists), each ends with `build -a` clean and a commit, and each leaves the tree usable — you can stop after any step. Nothing moves to a new place until the tool can read the new place.

**Step 0 · Freeze and repair (today's tree, no new machinery).**
Commit the tree as it is and tag it `pre-v2`. Then fix Appendix A by hand in one script — with asserts, dry-run first, reviewed by you before it writes: renumber the seven duplicated open packets to `Q-134…Q-140`, re-key the plunger ruling as `D-278` and restore what D-247 said inside it as the superseding entry, fix the four cites, remove the duplicate Q-112 packet, correct the three "next id" lines, and delete both PENDING docs from the Claude Project *after* confirming every edit they carried is either in the tree or re-queued as a packet under a fresh number. *Gate:* `build -a` clean and a hand count that every `Q-` and `D-` in the electrical tree is defined exactly once.

**Step 1 · Tool v2, additive.**
`rx7.py` gains: the registry (`ids` command: list / next / where-defined / where-cited); the eight generic checks of 2.2, initially as *warnings* so the current tree still builds; the three scalar placeholders of 2.3; `db.other(project)`; `lint`; `project.csv` and `phase` awareness; `-a` covering `00-CAR/systems/*`. No file moves. *Gate:* every existing project builds unchanged; `lint` prints its list.

**Step 2 · Questions and decisions to data — electrical build first.**
A migration script splits `QUESTIONS.md` and `DECISIONS.md` into `data/questions/`, `data/decisions/`, the two index CSVs and `log.csv` (from the thirteen banners and the §3 tables). Templates for the rendered `QUESTIONS.md` / `DECISIONS.md` / `LOG.md`. The registry checks become *errors*. `answers.py` reads the folder. *Gate:* the rendered files read the same as before, section by section, with the collision gone; `build` refuses on any dangling cite.

**Step 3 · Same for luxury and engine-swap.** Smaller; the same script. *Gate:* `build -a` clean, the registry sees three projects.

**Step 4 · `work.csv` everywhere; `CLAUDE.md` rewritten.**
Electrical §0 (A–G, 35 items) becomes rows; luxury already has `work.csv` (36 rows) and gains the columns; the swap gets its first list. §0 is rendered from it. `CLAUDE.md` shrinks to the lifecycle table, the workflow list and the four rules that are not yet checks; the rest of `ASSISTANT.md` is either a check or a SKILL. *Gate:* `QUESTIONS.md` §0 renders from data; `CLAUDE.md` under 60 lines.

**Step 5 · Templates de-drifted.**
`lint` lists every bare number and bare id in every template; the agent converts each to `{{cell}}` / `{{param}}` / `{{count}}` / `{{next_id}}` or cites it to a row in a note. `retired.csv` seeded from the last twenty rulings (the terms they retired). `c_rev` on. *Gate:* `lint` clean; a `set` on any cited row visibly changes the rendered sentence.

**Step 6 · The skills.**
Write the eleven `SKILL.md` files and `scaffold.py`, `complete.py`. Each skill is a numbered list with its gate, its script calls, its report shape; each cites the `rx7.py` commands it uses. Register the existing `rx7-answer-cycle` account skill as superseded by `/rx7-answers` in the repo. *Gate:* `/rx7-status` runs on both machines and prints the same thing.

**Step 7 · 00-CAR v2.**
The chapter set of 2.4: new tables (`intervals`, `as_fitted`, `parts_fitted`, `procedures`), cells normalised (values not sentences, ISO dates, controlled statuses — a script, reviewed), the current `vehicle / modifications / known-issues / parts-history / SPECS` re-templated as chapters 1–8, `MANUAL.html` from `view.json`. The first intervals come from `specs` (the 1985 §0 schedule is already in `01-REFERENCE`). `/rx7-log` works. *Gate:* the manual renders; a `/rx7-log` entry appears in chapter 3 with a computed next-due.

**Step 8 · Dry runs, on the live projects.**
`/rx7-criticize electrical-build` (read-only — its first output is also the acceptance test for the G-list); `/rx7-clean all`; `/rx7-plan luxury-package --cycles 3`; `/rx7-propose` on a throw-away name in a branch, then delete it; `/rx7-complete` on a *copy* of the electrical build in a branch, to prove the fold-in end to end before it is ever needed for real. *Gate:* each workflow ran start to finish without asking you a question; findings from the criticize run are in `reviews/`.

**Step 9 · Phases on.**
`project.csv` rows written; `c_phase` from warning to error; the design-freeze gate defined in each `views.py`. *Gate:* `/rx7-status` shows electrical: PLANNING, luxury: PLANNING, engine-swap: PROPOSED, with each one's next gate.

**Step 10 · Claude Project and memory.**
Delete the twelve docs; write the one pointer. Update the account skill and the memory file so any surface points at the repo's skills. *Gate:* a fresh Cowork session, asked "where does the build stand", answers from `/rx7-status`'s output and nothing else.

**Step 11 · Archive the transition.**
`99-ARCHIVE/2026-09_system-v2/`: this proposal, the migration scripts, the pre-v2 tag name, and the before/after of `CLAUDE.md`. *Gate:* the archive README indexes it.

Effort, roughly: steps 0–3 are the heavy ones (one long session each); 4–7 are medium; 8–11 are short. Nothing physical waits on any of it — the carts, the A/C strip and the measurement day proceed on the current tree, and step 0 is the only step that must happen before the next answer cycle.

---

## 6 · Your calls — ruled 2026-09-08

1. **Questions and decisions become data** — *yes.* His condition: every packet must be clear enough that he understands the whole question from the packet alone. That becomes a rule of the packet format (Ask · Why it matters · Options with their consequences · Recommend · Blocks · one-word ask) and a `/rx7-criticize` check on packets.
2. **Finished projects into `00-CAR/systems/` whole** — *no.* Split three ways: information + diagrams and service pages into the manual; every trace of process into `99-ARCHIVE/<project>/`. §2.4 and `/rx7-complete` rewritten above to match.
3. **The Claude Project reduced to one pointer** — *yes.*
4. **Five phases with gates and a design-freeze ruling** — *yes.*
5. **Step 0 repair as listed in Appendix A** — *yes.* Done 2026-09-08f; see the electrical `QUESTIONS.md` banner.
6. **Skill names and `.claude/skills/`** — *yes.*

---

## A · The collision repair list (evidence, and the fix for each)

All paths under `02-PROJECTS/electrical-build/`.

| # | What is wrong | Where | Fix (step 0) |
|---|---|---|---|
| A1 | `Q-112` (blower NLA, 2026-09-05 sweep) is an open packet **and** closed → D-253 in §3. The tree's D-253 (blower as a PWM load) already answers it | `QUESTIONS.md` lines 109 and 370 | delete the open packet; the closed row stands |
| A2 | `Q-116`…`Q-121` each exist twice: open packets from the 09-08 benchmark (CAN2 to the rear · disconnect polarity · kick-down · load dump / AFD · MRBF 250 A · limp-home) **and** closed rows → D-251, D-252, D-254, D-255, D-256, D-258 with unrelated outcomes | `QUESTIONS.md` §1 lines 136–192 vs §3 lines 350–373 | renumber the six open packets `Q-134`…`Q-139` in the order they appear; update the cross-refs inside them ("Pair with Q-119" → the new number) |
| A3 | `Q-113`, `Q-114`, `Q-115` were inserted by the script into numbers that §0 A7 and the 2026-09-07 banner say are *reserved* — no closed twin, but they sit outside the reserved-by-audit story and Q-115 was placed in §2a | lines 118, 128, 237 | keep the numbers (they are the audit's own), delete the "reserved" language from §0 A7 and the banner, since the audit is now applied |
| A4 | The plunger ruling — supersedes D-247, "any 2-terminal stop-lamp switch, wake from a spare P084 plunger" — was never written; `patch()` skipped on `**D-249` | `DECISIONS.md` §3 has no such entry; D-249 there = A7 oil pressure | write it as **D-278** in §5 (switches), naming D-247 as superseded and stating what D-247 said |
| A5 | D-247 was cut from `DECISIONS.md` but is still cited | `templates/PMU-CONFIG-SHEET.md` line 58 "brake (D-247)" | cite `D-247 → D-278` |
| A6 | Three rows and one §0 line cite "(D-249)" meaning the plunger | `cavities L3-S1 7 lands_on` · `devices DV25 terminals` · `parts P085 used_for` · `QUESTIONS.md` §0 A2 | `D-249` → `D-278` in each |
| A7 | The benchmark's other rulings the script intended (D-250 protection split · D-251 sleeping-current test · D-252 ignition condenser · D-253 F20 load-bearing / recovery path) were **not** written either; but their *data* edits landed (`rules retry`, `loads LD17`, `parts P099`) and cite those numbers | `data/rules.csv`, `data/loads.csv`, `data/parts.csv` P099 | write them as **D-279 … D-282** (in that order) and re-point the three cells; or, if you would rather rule on them first, park them as packets `Q-140`… and revert the three cells — your call, it is the one judgement item in this list |
| A8 | "Next IDs" typed in three places disagree with the tree and with each other | `CLAUDE.md` (D-278 / Q-134) · README template (same) · Project `SOURCE-OF-TRUTH.md` (D-254 / Q-122) | after A1–A7: D-283 / Q-141 (or Q-14x if A7 parks packets); in step 2 these lines become `{{next_id}}` |
| A9 | Both PENDING docs still say "apply, then delete this file" | Claude Project | delete both once A1–A8 are in; everything else they carried (V-081 expected values, Q-115 rewrite, the G-list) is already in the tree |
| A10 | `apply-rx7-changes.py` sits at the repo root and would re-run its SKIP/MISS logic | root | move to `99-ARCHIVE/2026-09-08_apply-script/` with a README that says what it did and did not do |

The fix is one script, dry-run first, with an assert on every anchor. I will write it for your review as the first act of step 0 once you have ruled on §6.

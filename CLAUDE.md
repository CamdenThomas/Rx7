# CLAUDE.md

*Rev 2026-09-03 · owns: nothing — this file exists so Claude Code and any agent that reads a root `CLAUDE.md` finds the real instructions.*

Read [`ASSISTANT.md`](ASSISTANT.md) first, every session. It is the operating
manual: the data tool, credit rules, edit process, delegation, decision
handling, verification, project close, session close, and the standing rules
R1–R11.

## The record is data, rendered (D-233, 2026-09-03)

Every project is `data/*.csv` (facts, one home each) + `templates/*.md`
(prose) → `python tools/rx7.py -p <project> build` → the documents and
`VIEW.html`. Rendered files carry a banner and are never edited by hand.
`DECISIONS.md` and `QUESTIONS.md` stay prose.

| Project | Owns | State |
|---|---|---|
| [`02-PROJECTS/electrical-build/`](02-PROJECTS/electrical-build/) | The harness — design, shopping, install | **Active.** Data-driven since 2026-09-03 |
| [`02-PROJECTS/luxury-package/`](02-PROJECTS/luxury-package/) | Every future feature — the cluster display, DCU, comfort, mirrors, windows, lighting (the ICU itself is the electrical build's, D-259) | **Data-driven since 2026-09-07** (luxury D-309) — its boundary table is derived live from the electrical data |
| [`02-PROJECTS/engine-swap/`](02-PROJECTS/engine-swap/) | Everything that changes with the engine | **Data-driven since 2026-09-07** — `data/handover.csv` is the interface the swap inherits from the harness (electrical D-262) |
| [`00-CAR/`](00-CAR/) | The car itself — identity, specs, modifications, faults, parts | Permanent; every project folds into it |
| [`01-REFERENCE/`](01-REFERENCE/) | Source documents, indexed in `data/sources.csv` | Permanent |

## Where to start

1. [`02-PROJECTS/electrical-build/QUESTIONS.md`](02-PROJECTS/electrical-build/QUESTIONS.md) — §0 is the finishing task list; §1 is what must be answered before the carts are paid.
2. `python tools/rx7.py -p electrical-build tables` — then `get` / `find` / `sql` for the rows the task touches.
3. [`DECISIONS.md`](02-PROJECTS/electrical-build/DECISIONS.md) `**Latest:**` line only, unless the task is a ruling.

## Quick facts an agent needs before touching anything

- **Never read a rendered document to learn a fact.** `DESIGN.md`, `WIRE-TABLES.md`, `PMU-CONFIG-SHEET.md`, `SHOPPING-LIST.md`, `INSTALL.md`, `GLOSSARY.md` and the project `README.md` are outputs of `build`. The rows are in `data/`; the prose is in `templates/`; the derivations are in `views.py`.
- **`build` refuses on a contradiction.** Fix the data, never the check — unless the check is wrong, in which case fix the check and log why.
- **Numbering:** electrical decisions continue from **D-278**, luxury from **D-316**. Electrical questions from **Q-134** (Q-113–Q-115 are reserved by the unapplied 2026-09-05 future-proofing audit, queued in the Claude Project as `rx7/PENDING-2026-09-05-futureproofing.md`), luxury from **Q-311**. IDs are permanent; a closed question is cited with its closer.
- **Nothing has been bought, cut or crimped.** Four carts wait for payment; `QUESTIONS.md` §1a lists what blocks paying them.
- The user is Camden. Physical work, spending, sign-off and `git commit` are his; everything that is reading, writing, calculating or cross-checking is the agent's.
- Line endings: `.gitattributes` normalises to LF in the repository. The tool writes LF; Windows editors are fine with it.

## Known stale artefacts

- The attached Claude Project (`rx7/…`) holds a flattened snapshot of the dissolved `electrical-pmu` tree from 2026-08-31 / 09-01. Its `SOURCE-OF-TRUTH.md` says so. **Do not answer from it — read this tree.**
- `99-ARCHIVE/` is history. Nothing in it is current; it stays for the reasoning.

# ASSISTANT.md — operating instructions for Claude

*Rev 2026-09-08 · owns: how the agent works in this tree — session protocol, the data tool, credit rules, edit process, delegation, decision handling, verification, session close, the standing rules R1–R11. Rewritten for the data + views workflow (D-233); the 2026-08-31 revision is in `99-ARCHIVE/`.*

Read this first, every session. It replaces remembered context. If anything here
conflicts with a habit, this file wins. Rules only — nothing in this file is a
log.

## Contents

0. Session opening · 1. The tool · 2. Credit rules · 3. Edit process ·
4. Delegation · 5. Small decisions · 6. Big decisions · 7. Verification ·
8. Project close — fold into the car · 9. Session close · 10. The answer cycle · R. Standing rules

---

## 0 · Session opening

Read **only**:

1. This file.
2. The active project's `QUESTIONS.md` §0 — where the work stands and what is
   open. Today the active project is `02-PROJECTS/electrical-build/`.
3. `python tools/rx7.py -p <project> tables` — the shape of the data, one call.
4. The specific rows the task touches (`get`, `find`, `sql`) — never the
   rendered document.

Do **not** read the whole tree. Do **not** read a generated file to learn a
fact — the row is the fact, the document is a print of it. Do **not** search
past conversations for anything already written down. If it's in a row or a
template, it's true; cite it and move on.

Camden names the mode. If he doesn't, ask once, in one line:
`DECIDE / GENERATE / AUDIT / BUILD?`

| Mode | Claude does | Camden does |
|---|---|---|
| DECIDE | Presents up to 20 decision packets, defaults pre-chosen | Replies with a yes/no/change list |
| GENERATE | Produces one artifact — a view, a template section, a table | Reviews the output afterward |
| AUDIT | `rx7.py check`, then attacks the prose for contradictions the checks can't see | Reads findings, rules on fixes |
| BUILD | Enters measured shop data as `set` calls, rebuilds | Supplies the numbers |

---

## 1 · The tool — `tools/rx7.py`

Every project is a folder holding `data/*.csv` (the facts — one row per thing,
one home per fact) and `templates/*.md` (the prose, with `{{view}}` lines where
tables go). `build` renders the documents and `VIEW.html` from both. An optional
`views.py` beside them supplies the project's named views and checks;
`{{table:name}}` works everywhere without one.

```
python tools/rx7.py -p electrical-build tables              tables and columns
python tools/rx7.py -p electrical-build get cavities "L3-S1 4"
python tools/rx7.py -p electrical-build get pins ch=O10
python tools/rx7.py -p electrical-build find "wink"
python tools/rx7.py -p electrical-build sql "select id, src from cavities where state='CAPPED'"
python tools/rx7.py -p electrical-build set pins 4 enable_a=13.0
python tools/rx7.py -p electrical-build add fuses id=F20 rating="5 A" ... --after F19
python tools/rx7.py -p electrical-build del fuses F5
python tools/rx7.py -p electrical-build check                integrity — no output written
python tools/rx7.py -p electrical-build build                check, then render everything
python tools/rx7.py -a build                                 every project
```

**Derived facts are never typed.** A pin's destinations, a housing's used
count, a wire label, the Deutsch kit counts, ADC centres, fuse-drawer values,
cart totals, the counts table — all computed in `views.py`. If a number can be
computed from other rows, computing it is the only correct way to state it.

**`build` refuses on any contradiction.** A cavity with no source, a LIVE fuse
with no load, a ladder window that overlaps, a cart line below the design's
count, a deleted part still named in a note, a gauge too light for its limit.
Fix the data; never work around a check. Add a check the moment a class of
error is found twice (R11).

**Rendered files carry a banner** and are committed to git so GitHub and
sponsors read them — but they are outputs. Editing one is the same mistake as
editing a compiled binary.

---

## 2 · Credit rules — non-negotiable

**One row, one call.** `get` and `sql` replace file reads. Reading DESIGN.md to
find a cavity is the old failure mode.

**Never re-derive.** Anything in a row or a decision is settled. Re-researching
a price, a pinout, or a past decision is a wasted credit and a correctness risk.

**Never rewrite a file to change part of it.** Data changes are `set` calls.
Prose changes are the smallest edit to the template with 1–3 lines of context.
A whole-file write is only for a brand-new file or a rewrite Camden names.

**Never restate a document in chat.** After a change, report the diff: rows
changed, IDs logged, what the build wrote. Ten lines maximum.

**Batch.** Several `set` calls in one shell command. One `build` at the end,
not after every edit.

**One search maximum per unknown fact.** If a search doesn't resolve it, log a
`Q-###` and move on. Do not chain searches hunting for certainty.

**Artifacts only by name.** `VIEW.html` is the visual view and is regenerated
by `build`; no other rendered artifact is produced unless Camden asks for one,
and it is dated and never a source of truth.

---

## 3 · Edit process

A change is one of three kinds, and each has one home:

| Kind | Home | How |
|---|---|---|
| A fact — a pin, a cavity, a part, a limit, a resistor | `data/*.csv` | `set` / `add` / `del` |
| Prose — a rule explained, a section rewritten | `templates/*.md` | smallest edit |
| Why — a ruling and its reasoning | `DECISIONS.md` | append a `D-###` in its system's section |

Then `build`, then commit both the data and the rendered output.

Rules for the prose files:

- `DECISIONS.md` — grouped by system, append-only within a section. A decision
  is never edited; it is superseded by a newer one that names it, and the
  superseded entry leaves the file. Update the `**Latest:**` line.
- `QUESTIONS.md` — one kind of item, easiest first, split BEFORE / AFTER the
  deadline that matters. Answered items leave and become `D-` entries. §0 is
  the finishing task list and must read true after every session.
- Templates keep the header `*Rev YYYY-MM-DD · owns: …*`, one H1, a Contents
  line past 200 lines (R5). Links are relative Markdown links.
- IDs are permanent and never reused; a closed ID is cited with its closer
  (`Q-100 → D-227`). Next IDs are in the project's `README.md`.
- Every CSV's first column is its key. Keys are stable — a cavity is
  `L3-S1 4` forever; a part is `P042` even after its item changes.

---

## 4 · Delegation — who does what

**Claude's work.** Anything that is reading, writing, calculating,
cross-checking or enumerating. Never hand these back to Camden:

- Pin schedules, cut lists, connector counts, label lists — via the data
- Resistor ladder math, ADC tables, fuse sizing arithmetic — via views
- Cross-checks — via `check`; a new class of error becomes a new check
- Schematic layouts and drawings
- Restating Camden's own decisions back in auditable form
- Arguing against a decision to test whether it holds
- Finding contradictions between prose written weeks apart

**Camden's work.** Only these. If a task is on this list, do not attempt it —
write it into `QUESTIONS.md` §0 and continue:

- Anything requiring hands on the car or a measurement from it
- Anything requiring eyes on a physical part (cavity geometry, clearances, fit)
- Ordering, spending money, committing to lead times
- Final sign-off on any decision that changes wiring, BOM, or cost
- Judgment about his own priorities, budget, and schedule
- `git commit`, and anything in the Claude Project's settings

**The test:** if Claude could be wrong in a way Camden couldn't catch from the
document alone, it's Camden's task.

---

## 5 · Small decisions — decide, log, keep going

A decision is **small** if reversing it costs nothing but a file edit.

1. Pick the sensible default.
2. Append to `DECISIONS.md` with the next `D-###` and a one-line reason.
3. Keep working.
4. Mention it in the closing diff, one line.

If Claude had to guess rather than reason, it's a **question**, not a decision:
add a `Q-###` to `QUESTIONS.md`, cite it where it bites, keep going, surface the
batch at the end. Never stop mid-task to ask about one.

---

## 6 · Big decisions — stop, package, hand over

A decision is **big** if it changes wiring, the BOM, cost, schedule, or
forecloses a future option. Claude does not make these.

1. Stop that thread. Continue with everything else.
2. Write a packet to `QUESTIONS.md` with a `Q-###`: Ask · Options ·
   Recommendation · Blocks, and an `ANSWER:` quote.
3. Present it in chat in exactly this shape:

```
Q-0xx · <one-line title>
Recommend:  <the call Claude would make>
Because:    <one line>
Flip it if: <the single condition that changes the answer>
Costs:      <dollars / pins / hours, if any>
```

Camden replies `yes` / `no, do X`. When he answers, the answer becomes a
`D-###` in the same session, the data is changed, the build is run, and the
packet leaves `QUESTIONS.md`. Never more than 20 packets in one batch.

---

## 7 · Verification discipline

The moment Claude writes a **part number, price, dimension, cavity position,
current rating, or claim that two connectors mate**, it is flagged in the same
edit — a `Q-###` (verify) in `QUESTIONS.md`, or the word *confirm* in the row's
note. Treat every unverified part number as a placeholder.

Known-unreliable territory — flag automatically: part numbers and connector
mating · prices, stock, lead times · physical geometry and clearances ·
anything about this specific car Camden hasn't stated. A fact from a document
in `01-REFERENCE/` is cited by that document's ID in `sources.csv`.

---

## 8 · Project close — fold into the car

A project that ends has changed the car. Before its `README.md` says *done*:

1. Every part fitted → a row in `00-CAR/data/` (modification, part history).
2. Every fact learned about the car itself — a rating, a capacity, a torque,
   a connector, a quirk — → `00-CAR/data/specs.csv` or `known-issues`, cited.
3. Every document obtained → `01-REFERENCE/data/sources.csv`, indexed the same
   session it lands (an unindexed file is one nobody finds twice).
4. The project's `data/` stays as the record of what was built; the next
   project starts from `00-CAR`, never from the old project.

---

## 9 · Session close

Camden says "give me the diff." Claude:

1. Runs `python tools/rx7.py -a build` and fixes anything it reports.
2. Confirms `QUESTIONS.md` §0 reads true.
3. Outputs, in ten lines or fewer:

```
CHANGED   rows set/added/deleted (table:key), templates touched
LOGGED    D-### decisions added
OPENED    new Q-###
CLOSED    Q-### → D-###
BUILT     files written by build
NEXT      recommended mode + target for next session
```

Then writes nothing else. The commit is Camden's.

---

## 10 · The answer cycle — when Camden says "I answered questions"

Camden answers in place: under the `**ANSWER:**` line of a packet in a project's `QUESTIONS.md`. One sentence from him — "I answered questions" — starts this routine, and the routine is the whole job. Run it in one pass, one script, one build.

1. **Find every answer.** `python tools/answers.py` prints each answered packet across all projects. Read them all before touching anything; an answer late in the list can change how an early one is applied.
2. **Classify each answer.** *A ruling* (yes / no / a choice / "follow recommendations") becomes a `D-` entry. *A brief* ("help me choose", guidelines, a re-framing) sharpens the packet — new options, one recommendation, a one-word ask — and stays open. *A question back* is answered inside the packet. *A fact he learned* ("I unplugged it and the temp gauge stopped") goes to `00-CAR` and the rows it corrects. Never leave an answer half-applied: a ruling that touches three projects is applied to all three in the same script.
3. **For each ruling, in this order:** (a) the `D-` entry in the owning project's `DECISIONS.md` — the decision in bold, then Camden's words, the reasoning, what it supersedes by ID, and the consequences in the data, filed under the system it touches, plus the **Latest** line; (b) every data row the ruling changes — sweep the electrical tables (`cavities`, `housings`, `pins`, `node_conductors`, `fuses`, `devices`, `migration`, `parts`, `icu_channels`, `logic`, `grounds`), the luxury tables (`features`, `stages`, `provisions`, `sensors`, `can_messages`, `can_fields`, `parts`, `work`, `modules`), the engine-swap `handover`, and `00-CAR` `issues` / `parts_history`; (c) every template and prose file that stated the old fact — grep the *old term of art* across `templates/`, `QUESTIONS.md`, `CLAUDE.md`, `README.md`, the other projects and `01-REFERENCE` (which must stay free of the new design); (d) the packet moves to `QUESTIONS.md` §3 with its closer; anything it moved between projects keeps its number and lands in §4 of the project it left; (e) new questions the ruling raises are written as packets with a recommendation and a one-word ask, in the project that owns them.
4. **Cross-project seams, every time.** The luxury `provisions` expectations against the electrical states; the engine-swap hand-over rows; `00-CAR` known issues; the numbering lines in `CLAUDE.md`, both README templates and the Claude Project's `SOURCE-OF-TRUTH.md`.
5. **Grep for the corpse.** Before building, search the live tree for the words the ruling retired (the old housing, the old part, the old phrase) — excluding `99-ARCHIVE/`, `DECISIONS.md` (history stays) and `VIEW.html` (rendered). Every hit is either fixed or is history.
6. **Build all, fix, build again.** `python tools/rx7.py -a build`. A refusal names the row; fix the data, never the check — unless the check is wrong, in which case fix the check and say why in the decision.
7. **Record the state.** `SOURCE-OF-TRUTH.md` in the Claude Project (next IDs, what stands, what is open) and the banner line at the top of the project's `QUESTIONS.md` (`> **date.**` — rulings, sharpened packets, new packets, next question number).
8. **Report, briefly:** what was ruled (by D-number, one line each), what was sharpened and now wants one word, what is new, what left or joined the carts, and what stays open — in that order. Never re-ask anything he has answered; never restate a packet he can read.

Credit rules apply: read the answers once, batch every edit into one script in `%TEMP%` (asserts on every anchor so a miss is loud), one build at the end and one more if it refused. A cycle that touches only prose is still a cycle — steps 5–7 are not optional.

## R · Standing rules

Permanent. Each exists because it was violated at least once.

**R1 · Read a row before changing it.** `get` first; if the change contradicts
the row's neighbors, revise the neighbors too.

**R2 · A document must be correct top to bottom.** Superseded reasoning goes to
the archive, never above a correction. Templates are prose; keep them current.

**R3 · One home per fact.** A fact lives in one row. Every other place it
appears is a view of that row. If a fact had to be typed twice, one of
the two is a view that hasn't been written yet.

**R4 · Scope belongs to the project that owns the work**, not the project where
it was first discussed. Car-level facts belong to `00-CAR`.

**R5 · Every template gets a header** — title, one-line purpose,
`*Rev YYYY-MM-DD · owns: what*` — one H1, and a Contents line past 200 lines.

**R6 · When code owns a fact, say so.** A view's docstring names what it
derives and from which tables.

**R7 · Cite a closed ID with its closer** — `Q-038 → D-095`, never bare.

**R8 · Generated files are never edited by hand.** The banner is the tell.
Edit the data or the template, run `build`, commit both.

**R9 · The build must be clean before the session closes.** A red check is a
finding, not an inconvenience.

**R10 · Every project has the same skeleton.** `README.md` · `DECISIONS.md` ·
`QUESTIONS.md` · `data/` · `templates/` · `views.py` (optional) ·
`view.json` (optional) · numbered step folders for the rendered output.

**R11 · Twice is a pattern.** The second time a class of error is found by
hand, it becomes a check in `views.py` the same session.

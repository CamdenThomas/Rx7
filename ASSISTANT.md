# ASSISTANT.md — operating instructions for Claude

*Rev 2026-09-03 · owns: how the agent works in this tree — session protocol, the data tool, credit rules, edit process, delegation, decision handling, verification, session close, the standing rules R1–R11. Rewritten for the data + views workflow (D-233); the 2026-08-31 revision is in `99-ARCHIVE/`.*

Read this first, every session. It replaces remembered context. If anything here
conflicts with a habit, this file wins. Rules only — nothing in this file is a
log.

## Contents

0. Session opening · 1. The tool · 2. Credit rules · 3. Edit process ·
4. Delegation · 5. Small decisions · 6. Big decisions · 7. Verification ·
8. Project close — fold into the car · 9. Session close · R. Standing rules

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

## R · Standing rules

Permanent. Each exists because it was violated at least once.

**R1 · Read a row before changing it.** `get` first; if the change contradicts
the row's neighbours, revise the neighbours too.

**R2 · A document must be correct top to bottom.** Superseded reasoning goes to
the archive, never above a correction. Templates are prose; keep them current.

**R3 · One home per fact.** A fact lives in one row. Every other place it
appears is a view of that row. If a fact would have to be typed twice, one of
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

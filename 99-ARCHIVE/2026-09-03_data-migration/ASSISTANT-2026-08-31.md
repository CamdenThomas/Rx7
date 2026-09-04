# ASSISTANT.md — operating instructions for Claude

*Rev 2026-08-31 · owns: how the agent works in this tree — session protocol, credit rules, edit process, delegation, decision handling, verification, the standing rules R1–R8. Audit history is [`02-PROJECTS/electrical-pmu/05-PROCESS/AUDITS.md`](02-PROJECTS/electrical-pmu/05-PROCESS/AUDITS.md)'s; the agent backlog is [`FORWARD-WORK.md`](02-PROJECTS/electrical-pmu/05-PROCESS/FORWARD-WORK.md)'s.*

Read this first, every session. It replaces remembered context. If anything here
conflicts with a habit, this file wins. Rules only — nothing in this file is a
log.

## Contents

0. Session opening · 1. Credit rules · 2. Markdown edit process · 3. Delegation
· 4. Small decisions · 5. Big decisions · 6. Verification · 7. Session close ·
R. Standing rules

---

## 0 · Session opening

At session start, read **only**:
1. This file.
2. [`02-PROJECTS/electrical-pmu/STATUS.md`](02-PROJECTS/electrical-pmu/STATUS.md) — where the project is.
3. The specific file the task touches.
4. [`05-PROCESS/OPEN.md`](02-PROJECTS/electrical-pmu/05-PROCESS/OPEN.md) if the task touches an unresolved item.

Project files live in numbered folders: `01-DESIGN` `02-HARNESS` `03-MODULES`
`04-BUILD` `05-PROCESS` (renumbered 2026-08-31, D-200). The project
[`README.md`](02-PROJECTS/electrical-pmu/README.md) is the map and names the
owner of every fact.

Do **not** read the whole tree. Do **not** search past conversations for
anything already written to a file. If it's in a file, it's true; cite the file
and move on. If it's in a **generated block** (`<!-- gen:… -->`) or a generated
file, the CSV under `02-HARNESS/data/` is the truth — edit that and run
`05-PROCESS/tools/gen.py`.

Camden names the mode. If he doesn't, ask once, in one line:
`DECIDE / GENERATE / AUDIT / BUILD?`

| Mode | Claude does | Camden does |
|---|---|---|
| DECIDE | Presents up to 20 decision packets, defaults pre-chosen | Replies with a yes/no/change list |
| GENERATE | Produces one tedious artifact for a named section | Reviews the output afterward |
| AUDIT | Attacks the tree for contradictions, orphans, gaps; runs `tools/check.py` | Reads findings, rules on fixes |
| BUILD | Updates files from measured shop data — CSV first, then regenerate | Supplies the numbers |

---

## 1 · Credit rules — non-negotiable

**Never re-derive.** Anything in a file is settled. Re-researching a price, a
pinout, or a past decision is a wasted credit and a correctness risk.

**Never re-read chats.** The files are the memory. Conversation search is only
for something explicitly not in a file.

**Never rewrite a file to change part of it.** Use the smallest edit with the
minimum unique context. A full rewrite is only for a brand-new file, a rewrite
Camden explicitly asks for, or an audit fix where the file is wrong top to
bottom (R2).

**Never regenerate a document to add one row.** Append or edit in place — and
never hand-edit a generated block (R8).

**File edits are the default output.** An HTML or rendered artifact is produced
only when Camden asks for a printable or visual view by name, is dated, and is
never a source of truth — the Rev A HTML pages in `99-ARCHIVE/` are what
happens otherwise.

**Never restate file contents in chat.** After an edit, report the diff, not the
document. Ten lines maximum.

**Batch tool calls.** Reading four files takes one call, not four. Ten small
edits to one file is still ten edits — that's correct and cheaper than one
rewrite.

**One search maximum per unknown fact.** If a search doesn't resolve it, log it
as a `V-###` and move on. Do not chain searches hunting for certainty.

---

## 2 · Markdown edit process

Every file change follows this order:

1. **Read the target section only**, or the whole file if it's under ~60 lines.
   **Read before appending** (R1).
2. **Edit** with 1–3 lines of context, exact whitespace.
3. **Log it.** If the edit reflects a decision, append to `DECISIONS.md` with a
   new ID. If it creates an unknown, append to `OPEN.md`.
4. **Report the diff.** Ten lines. What changed, what ID it got, what it opened.

Rules for the files themselves:

- `SPEC.md` — current state only. No history, no rationale, no alternatives.
- `DECISIONS.md` — append-only. Never edit or delete a past entry. Reverse by
  adding a new one and putting `> SUPERSEDED BY D-xxx` under the old one.
- `OPEN.md` — items are removed only when resolved. Resolution means a new
  `DECISIONS.md` entry or a verified fact written into `SPEC.md`.
- `TASKS-CAMDEN.md` — physical work only Camden can do. **Reorder and regroup
  freely** to keep it usable; never renumber a `T-###`.
- Generated files and blocks (`PIN-MAP.md`, `CAVITY-STATE.md`, `channels.h`,
  the diagrams, the `gen:` blocks in SPEC / CHANNEL-SCHEDULE / CUT-LIST /
  CONNECTORS) — edit the CSV, run `gen.py`, commit both.
- IDs are permanent and never reused. The prefixes are in
  [`GLOSSARY.md`](02-PROJECTS/electrical-pmu/01-DESIGN/GLOSSARY.md); the
  registry of every ID issued is `ID-REGISTRY.md` (run `tools/registry.py`).
- Every file carries the header `*Rev YYYY-MM-DD · owns: …*` in its first six
  lines, one H1, and a `## Contents` line once it passes 200 lines (R5).
- Links are relative Markdown links, checked by `tools/check.py`.

---

## 3 · Delegation — who does what

**Claude's work.** Anything that is reading, writing, calculating, cross-checking
or enumerating. Never hand these back to Camden:

- Pin schedules, cut lists, connector BOMs, label lists — via the CSVs
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
- `git commit`, and anything in the Claude Project's settings

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
decision: add it to `OPEN.md` §Assumptions with an `A-###`, cite the ID where
the assumption bites, keep going, and surface the whole batch at the end. Never
stop mid-task to ask about one.

---

## 5 · Big decisions — stop, package, hand over

A decision is **big** if it changes wiring, the BOM, cost, schedule, or forecloses
a future option.

Claude does **not** make these. The process is:

1. Stop that thread. Continue with everything else.
2. Write a decision packet to `OPEN.md` with a `Q-###`: Ask · Options ·
   Recommendation · Blocks, and an `ANSWER:` quote.
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
of him to rule on it. When he answers, the answer becomes a `D-###` in the
same session and the packet leaves `OPEN.md` — an answer typed into a spec is
not a decision until it is logged.

Never present a big decision as an open-ended question. Never present more than
20 packets in one batch.

---

## 6 · Verification discipline

The moment Claude writes a **part number, price, dimension, cavity position,
current rating, or claim that two connectors mate**, it gets a `V-###` in
`OPEN.md` in the same edit. No exceptions.

Treat every unverified part number as a placeholder, not a fact. Never let one
reach the BOM's committed section.

Known-unreliable territory — flag automatically:
- Part numbers and connector mating
- Prices, stock, lead times
- Physical geometry and clearances
- Anything about this specific car Camden hasn't stated

---

## 7 · Session close

Camden says "give me the diff." Claude:

1. Runs `python 05-PROCESS/tools/registry.py` and `python 05-PROCESS/tools/check.py`
   and fixes anything they report.
2. Appends the same five lines to `05-PROCESS/CHANGELOG.md` under today's date.
3. Outputs, in ten lines or fewer:

```
CHANGED   files touched, sections
LOGGED    D-### decisions added
OPENED    new Q-### / A-### / V-### / T-###
CLOSED    items removed from OPEN.md
NEXT      recommended mode + target for next session
```

Then writes nothing else.

---

## R · Standing rules

Permanent. Each exists because it was violated at least once; the audit that
produced each is in `AUDITS.md` §5.

**R1 · Read a file before appending to it.** If the append contradicts anything
above it, **revise instead of appending.**

**R2 · A document must be correct top to bottom.** When a decision supersedes
content, revise the section in place and move superseded reasoning to a marked
appendix or `99-ARCHIVE/`. Never leave an error above a correction.

**R3 · One owner per fact**, declared in each file's header line. If two files
disagree, the owner wins. The project README's ownership table is the list.

**R4 · Scope belongs to the project that owns the work**, not the project where
it was first discussed.

**R5 · Every file gets a header** — title, one-line purpose,
`*Rev YYYY-MM-DD · owns: what*` — one H1, and a Contents line past 200 lines.

**R6 · When code owns a fact, say so in the index** and record the decisions
that shaped it. Code and prose drift silently; the only defence is naming the
owner.

**R7 · Cite a closed ID with its closer** — `Q-038 → D-095`, never bare — so a
reader never mistakes it for live. `check.py` C5 catches the bare ones.

**R8 · Generated blocks are never edited by hand.** Edit the CSV under
`02-HARNESS/data/`, run `gen.py`, commit both. `check.py` F2 catches drift.

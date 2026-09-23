# CLAUDE.md — the Rx7 tree

_Rev 2026-09-21 (v3). This file is the whole instruction set. There are no skills, no
slash commands, no second document. If a rule is not here it is not a rule; if you need
one that is missing, that is a block._

> **THERE IS ONE TREE: `~/docs/storage/Rx7`, on one machine.** The v3 conversion finished on
> 2026-09-12: v3 became this directory and the old v2 working tree was deleted. Any
> instruction you find anywhere telling you that `Rx7-v3` is the project, or that `Rx7`
> is frozen reference, is stale — that folder no longer exists. §9 has what is left of
> the history.

---

## 0 · Start

```
python tools/rx7.py status
```

Read nothing else until it tells you where things stand. `status` prints: whether the
record is valid, each area's phase, open work by owner, and the blocks.

Then take **exactly one** of two paths. There is no third.

|       | Path                                                                           | When                             |
| ----- | ------------------------------------------------------------------------------ | -------------------------------- |
| **A** | **Do the work.** Read this file for the rule, apply it, move on.               | Every doubt that §3 calls small. |
| **B** | **Write a block.** Append it to `BLOCKS.md` and keep going on everything else. | Every doubt that §3 calls big.   |

You never ask Camden a question in chat. You never stop mid-run. You speak to him once,
per §8, and only when blocks have stopped all remaining progress.

---

## 1 · The record

The record is CSV, and it describes itself.

```
<area>/data/_project.csv    key,value        — name, kind, phase, goal
<area>/data/_tables.csv     table,purpose    — every table that exists
<area>/data/_schema.csv     table,column,type,required,ref,note
<area>/data/*.csv           the facts — one row per thing, first column the key
<area>/data/decisions.csv   every ruling; the body is data/decisions/<id>.md
BLOCKS.md                   the one page Camden writes in
```

A car-level ruling that belongs to no project (a fluid, a service call) is a decision in
`00-CAR/data/decisions.csv`, closing a `CAR.` block; `00-CAR`'s other tables still never
cite it (§6.6).

An **area** is any directory holding `data/_tables.csv`: `00-CAR` (the car itself, phase
PERMANENT), `01-REFERENCE` (manuals, factory circuits, photos, sources — PERMANENT), and
each project under `02-PROJECTS`.

**There is one data format.** Everything is a CSV table, including the schema, so the
description of the record is checked by the same code that checks the record. A table
that is not declared, a declared table with no file, an undeclared column, a missing
column, a value that is not its declared type, a duplicate or empty key, a reference to
a row that is not there — each is a refusal naming the exact row.

**No counter is ever stored.** The next `D-` is derived from the highest that exists
anywhere in the tree or the archive; a project's next block from the highest number that
project has used, on the page or in any decision's `closes`. A stored counter
can disagree with reality. Never type an id — `rx7.py new` and `rx7.py block` issue them.

**There are exactly two kinds of generated document: `DECISIONS.md`, and each project's `TODO.md` (D-373).** Nothing else. No templates,
no rendered design or shopping or install documents, no HTML, no diagrams. The v2 view
layer is in `99-ARCHIVE/2026-09-11_v2-view-and-tools/`, and that archive is the only
place the old tree survives (§9). The visual layer is a separate, later concern; until it exists,
do not build one, and do not write a document "so it can be read." The record is the
deliverable.

`DECISIONS.md` is the exception because it is Camden's record of every call made without
him, and it has to stay readable and searchable. It is safe to generate where v2's
documents were not, for four reasons that must all stay true:

- it is a **pure projection** of `decisions.csv` plus the decision bodies — it adds no
  fact of its own, so it cannot disagree with the record
- it is **read-only**: he reads it, he never edits it, and nothing in it invites typing
- `rx7.py decisions` regenerates it whole; run it at the end of **every** run that wrote
  a decision
- **nothing gates a commit on whether it is current.** `check` does not look at it. A
  stale index is fixed by running the command, never by refusing a commit — that trap is
  what v2's pre-commit hook did, and it is why he could not push.

It is one file for the whole tree, grouped by area and then by the category in each
decision's `system` column — never by number — so he can read one system's rulings
together or search the file for an id. Superseded and withdrawn decisions are listed at
the end with the decision that replaced each, so every id ever issued is still findable.

**`<project>/TODO.md`** (D-373) is the same kind of exception, under the same four rules: a
pure projection of that project's `work` table, read-only, rebuilt whole by `rx7.py todo`,
and never looked at by `check`. It is Camden's working list: what he can start today, then
every row in working order (stages in the order their work can start, each row after what
it waits on), with its note. It has **no boxes to tick** (R3): he says what he did, the row
is set through the record, and the file is regenerated. Run `rx7.py todo` at the end of
**every** run that changed a `work` row.

**Exit codes are the only signal anything may branch on.**

| Code | Means                                         | Effect                                                                 |
| ---- | --------------------------------------------- | ---------------------------------------------------------------------- |
| `0`  | valid / done                                  | —                                                                      |
| `1`  | **invalid** — the record contradicts itself   | the only code that blocks a commit                                     |
| `2`  | nothing to do, or something waits on a person | **blocks nothing, ever**                                               |
| `3`  | a usage error or a crash in `rx7.py` itself   | **blocks nothing** — a broken checker is never a verdict on the record |

Never branch on the text of any command's output. Never grep it, never test it for a
word. If you need a machine-readable fact you do not have, add a command or a column.
_This is the rule v2 broke in four places and it is why a clean build could stop a push._

### The tool

```
rx7.py status                            where everything stands
rx7.py check [-p AREA]                   validate (rc 1 if the record contradicts itself)
rx7.py tables AREA                       every declared table, row counts, purpose
rx7.py get AREA TABLE KEY                one row
rx7.py set AREA TABLE KEY col=val ...    change an existing row
rx7.py add AREA TABLE col=val ...        add a row
rx7.py del AREA TABLE KEY                delete a row
rx7.py sql AREA "select ..."             query one area (read-only)
rx7.py find TEXT [-p AREA]               search every cell, decision body and BLOCKS.md
rx7.py new AREA "title" [col=val ...]    reserve the next D- and stub its body
rx7.py block "ask" -p AREA               append a block to BLOCKS.md
rx7.py blocks [--answered|--solved]      list blocks
rx7.py decisions                         regenerate DECISIONS.md (grouped by category)
rx7.py todo [-p AREA]                    regenerate each project's TODO.md from its work table
rx7.py cites                             advisory: prose cites that no longer resolve
rx7.py selftest                          the gate resolver's own tests (in memory)
rx7.py log AREA KIND "what" [refs]       one log row (KIND = the area's log.workflow enum)
```

### Gates and READY

`work.gate` holds **references, and nothing else** — prose belongs in `note`. All of them
must be met before the row can start; an empty gate is met. They resolve across the whole
tree, so one area can wait on another:

| Reference         | Met when                                                                                                 |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| `D-274`           | that decision is standing or inherited                                                                   |
| `01.07`           | that block is gone from `BLOCKS.md` and a decision names it in `closes`                                  |
| `A5` · `F-012`    | that work row is done or dropped, in this area                                                           |
| `01-luxury:F-012` | the same, in another area — **always qualify across areas**, because work ids are only unique within one |
| `phase:SOURCING`  | this area is at that phase or past it                                                                    |

**READY** is every open row whose gate is met. `status` prints it per owner and prints
**BLOCKED** with what holds each row, so answering one block visibly moves several rows
across on the next run. §6.1 takes its work from READY and nowhere else.

`check` refuses a reference that resolves to nothing, an unqualified work id two areas
could answer, a dependency ring, and an area that has gated every one of its own rows on
its own rows or its own phase — that last one cannot be true, and it is the failure that
hides: a walled-off queue and a finished project look identical, because the planner says
"nothing to do" in both cases. An area whose work all waits on a **block** or on **another
area** is a real state, not a contradiction: that is exit code 2, and it refuses nothing.

`selftest` checks the resolver itself. A resolver that wrongly calls a gate met sends the
planner at work that is not ready; one that wrongly calls it unmet stops the project with
no error printed anywhere. Both are silent, so both get tests (R7).

`set`, `add` and `del` refuse a column that `_schema.csv` does not declare. To add a
fact that has no column, add the column to `_schema.csv` first — that is a small
decision (§3) and it is how the design grows.

---

## 2 · Who does what

**Camden**: answers blocks in `BLOCKS.md` · spends money · does the physical work and
says what happened · takes measurements · `git commit`.

**You**: everything that is reading, writing, calculating, cross-checking, enumerating,
sourcing, or deciding within §3's small list. If a step needs a call only he can make,
write a block and carry on with the rest of the run.

`BLOCKS.md` is the only file Camden ever writes in. Nothing regenerates it: you append
new blocks and delete solved ones once their decision stands (§4), and that is all that
ever touches it. No tool rewrites it, and no output of yours ever invites him to type anywhere else.

---

## 3 · Big or small — the test

Apply this to every doubt. It has two directions, and the second is as binding as the
first: over-blocking is a failure, not caution. v2 accumulated 129 questions on one
project because asking was the only defined move.

**SMALL — decide it yourself, silently, and write it into the record. All must hold:**

- undoing it means editing rows, not rebuying, recutting or rewiring
- it costs no money and no bench time to reverse
- it does not change what is bought, what is cut, or where a wire goes
- a row already in the record, a factory document, or arithmetic settles it
- a competent builder would call the answer obvious in hindsight

**BIG — write a block. Any one of these is enough:**

- **money** — changes what is bought, from whom, or the total
- **irreversible** — undoing it means re-cutting, re-crimping, re-ordering, re-drilling
- **the car** — needs a measurement, a look, or a test only he can perform
- **forecloses** — closes off something he has said he wants (the LS/CD009 swap, the
  luxury package, the sponsor showcase, future serviceability)
- **taste** — appearance, feel, ergonomics, how the finished car reads
- **safety** — fusing, grounding, fuel, anything that can burn, strand or shock
- **contradiction** — two standing decisions disagree, or a new fact breaks one
- **scope** — adds or removes work, or moves work between projects

**If you cannot tell,** the tiebreak is the cost of being wrong. Wrong costs only your
time → decide it. Wrong costs his money, his weekend, or a part that must be bought
again → block it.

**Never block the same thing twice.** A solved block governs every case like it. Before
writing a block, `rx7.py find` the subject: if a decision already rules it, the decision
governs — apply it, do not re-ask.

### Standing answers — the small path, pre-decided

These exist so a small doubt never becomes a conversation.

| Doubt                                         | Standing answer                                                                                                                                           |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A check refuses                               | Fix the data. Never the check — unless the check itself is wrong, in which case fix it and say so in the decision.                                        |
| A type or enum refuses a legitimate new value | Widen it in `_schema.csv` deliberately, in the same pass, and note why. Never work around it in the data.                                                 |
| A fact has no column                          | Add the column to `_schema.csv`, then the value.                                                                                                          |
| A fact has no table                           | Add the table to `_tables.csv` and `_schema.csv`, then the rows.                                                                                          |
| Two areas both want a fact                    | It belongs to whoever owns the work. A fact about the car as it stands belongs to `00-CAR`; a fact about what a project will do belongs to the project.   |
| A number could be derived or typed            | Derive it. A typed derived number is drift waiting to happen.                                                                                             |
| A part number cannot be verified              | Put the row in with the note `confirm`, keep going, and block it only if buying it wrong costs money.                                                     |
| A quantity is uncertain                       | Round up to the next sane pack size, note the margin. Wire: 1.5× measured route length.                                                                   |
| Units                                         | Millimetres, amps, volts, AWG, ISO dates. Numbers in cells, no units, no formatting, no bold — units belong in the column name or `note`.                 |
| A row needs changing                          | `get` it first, always.                                                                                                                                   |
| Something is ambiguous in what Camden wrote   | Take the reading that keeps the most options open, write it into the record, and note the reading in the decision. If both readings cost money, block it. |
| A superseded decision must be cited           | Cite it with its closer: `D-247 → D-278`.                                                                                                                 |
| An old cite no longer resolves                | `rx7.py cites` lists these. Advisory. Fix them when you are already in the file; never let one stop a run.                                                |
| The record and your memory disagree           | The record wins. Always.                                                                                                                                  |
| You are about to write a document             | Don't. `DECISIONS.md` and each project's `TODO.md` are the only ones, and `rx7.py decisions` / `rx7.py todo` write them. See §1.                          |
| You wrote a decision this run                 | Run `rx7.py decisions` before you report.                                                                                                                 |
| You changed a `work` row this run             | Run `rx7.py todo` before you report.                                                                                                                      |

---

## 4 · Blocks

`BLOCKS.md` holds **only what is still open**, grouped under one header per project —
`## 00 · Electrical`, `## 01 · Luxury`, … — and every block sits under its own project's
header (`check` refuses one that does not). A block looks like this:

```
### 00.07 · A short title
**Opened** 2026-09-21
**Ask** One sentence, answerable on its own.
**Why** What changes depending on the answer.
**Options**
- (a) … — what it costs, what it forecloses
- (b) … — what it costs, what it forecloses
**Recommend** (a), unless <the thing that would flip it>.
**Stops** What cannot proceed until this is answered.
**SOLVE:**
```

He types after `**SOLVE:**` — on that line or the lines below it, plain sentences, any
length, no markers to preserve. Blank means unanswered.

**Block ids are `<project>.<number>`** (D-356): `00.01` is the first block ever raised for
`02-PROJECTS/00-electrical`, `01.07` the seventh for `01-luxury`. The prefix is the project
directory's two-digit number; `00-CAR` and `01-REFERENCE` use `CAR` and `REF`, because
`00` and `01` are taken. `rx7.py block "ask" -p AREA` issues the id and files the block
under its header — `-p` is required. Never `B-`: this car's factory diagrams already use
`B-12` and `D-01` as component codes, and an id family must never share a namespace with
the subject matter. And because a bare `13.80` in prose is a voltage, a block id is only
recognised as structure — a heading, `closes`, a gate. In prose write it as `block 00.07`
or in backticks. Blocks were `BLK-###` until 2026-09-21; each old id is a `retired` row in
its project naming the new one.

**The clarity bar.** A block must be answerable from the page alone, with no design in
front of him — the same three-isolated-workers standard as everything else. `check`
refuses a block missing any of Ask / Why / Options / Recommend / Stops. If he answers
"unclear — <what is missing>", that is a defect in the block: sharpen it, do not rule it.

**Lifecycle.** You append it → he types a solution → `rx7.py blocks --answered` finds it
→ you apply it through the record (§6.2) → the ruling becomes a decision whose `closes`
names the block → **you delete the block from this page.** An answered-but-unapplied
block is exit code **2**. It never refuses a commit. _That single sentence is the whole
fix for why he could not push._

**Nothing is archived on this page, because nothing needs to be.** A settled question
lives in `DECISIONS.md`, with his words, the reasoning and the consequences in the data —
that is what the decision is for, and keeping a second copy here would be two homes for
one fact (R2). Before deleting a block, confirm three things: the decision exists and is
`standing`, its `closes` names the block, and its body carries **his answer in his own
words**. If any of those is missing, finish the job instead of deleting the block. Ids
are never reused — `rx7.py block` derives the next number from the decisions as well as
the page, so a deleted 01.05 can never come back as something else.

**A block that came back unclear is replaced, not ruled.** Write the new, plainer block
first, carry his words into its **Why** so nothing he typed is lost, then delete the old
one. If his answer contained a question for you, answer it in the new block's **Why**,
then ask only the part that actually needs him.

---

## 5 · Standing rules

**R1** `get` a row before changing it.
**R2** One home per fact. If it can be computed, compute it.
**R3** Nothing you generate may contain a place to type. `BLOCKS.md` is the one entry
point for his writing, and no parser of his writing may be picky. Losing his writing is
the worst failure this system has; a wrong ruling is recoverable, a lost session is not.
**R4** A decision, once written, is never edited. It is superseded by a new one that
names it.
**R5** Never type an id. Never store a counter.
**R6** When code owns a fact, its docstring says which tables.
**R7** Twice is a pattern — the second time a class of error is found by hand, it becomes
a check in `rx7.py`.
**R8** `check` is clean before the session closes. If it is not, that is the report.
**R9** Never branch on the words of any output — only its exit code (§1).
**R10** Scope belongs to the project that owns the work; car-level facts belong to
`00-CAR`; anything that is a manual, a diagram or a datasheet belongs to `01-REFERENCE`.
**R11 You cannot see the car.** Every wire table, cavity map, clearance and pin letter in
this tree was written by something that has never looked at the vehicle, held the
connector, or put a meter on anything. A measured number always beats your reasoning:
where the two disagree, the measurement wins and the row is wrong. Never conclude anything
about a physical part from a verbal description, a photograph, or a datasheet for a part
nobody has confirmed is the part in the box — there your job is to say _what to measure_,
and it is a block, not a guess. A dimension, resistance, pin letter or wire length that
has not been measured carries `confirm` in its note until it has. This is not modesty: the
design is tens of thousands of rows describing an object you cannot perceive, and the
failure mode is a harness that is internally perfect and does not fit.
**R12 A gate holds references, never prose.** Work is taken from READY, never from file
order. If READY is empty, that is the report.

---

## 6 · Playbooks

Each of these is one run. Every run ends the same way: `check` clean, `rx7.py decisions`
if a decision was written, `rx7.py todo` if a work row changed, a `log` row, and — only if blocks have stopped everything —
the report in §8.

### 6.1 · Plan (phase PROPOSED or PLANNING)

1. `status`. If any block is answered, do 6.2 first — an answer can change how an
   earlier work item should be done.
2. Take the first agent row in **READY** — `status` prints it. Never the next row in file
   order, and never a BLOCKED one. **READY empty is a report, not permission to take
   something else**: say what is holding the queue and stop.
3. Do it through the record only: facts become rows (R1); a derivation becomes a query,
   never a typed number; a fact with no column gets a column (§3). Anything §3 calls big
   becomes a block plus a Camden-owned work row gated on it, and the item stays open with
   `note=waits on block 00.…`.
4. `check`. A refusal is fixed in the data, or becomes a block if the fix is his.
5. `set work <id> state=done`; `log`.
6. Repeat until no agent item has a met gate.
7. **Phase gate.** Every agent design item done, no open block that stops design, no open
   Major review finding → write the design-freeze block. The freeze is his ruling; it
   moves the phase to SOURCING.

### 6.2 · Apply answered blocks

1. `rx7.py blocks --answered`. Read every one before touching anything.
2. **If it prints none and he says he answered, find the text before doing anything
   else.** Look in `BLOCKS.md` (was the `**SOLVE:**` line edited away?), then
   `git diff`, then `git stash list`. Never tell him nothing was answered until you have
   looked. Never run anything that writes until you have.
3. Classify each: a **ruling** (yes / no / a choice / "follow recommendations") → a
   decision. A **brief** (guidelines, a re-framing, "help me choose") → sharpen the block
   and leave it open. A **question back** → answer it in the block body above `**SOLVE:**`
   and leave it open. A **fact about the car** → `00-CAR` rows plus every project row it
   corrects.
4. For each ruling, in this order:
   a. `rx7.py new AREA "<title>" closes=… supersedes=…` then write the body: the decision
   in bold, his words, the reasoning, what it supersedes by id, the consequences in the
   data.
   b. Every row the ruling changes — `get`, then `set` / `add` / `del`. A ruling that
   touches three projects is applied to all three in the same pass.
   c. Every retired term into `retired.csv` so it can never come back.
   d. New questions the ruling raises → new blocks.
   e. Work rows gated on it: gate met → leave open for 6.1; the ruling did the work →
   `state=done`.
5. Delete each solved block from `BLOCKS.md`, but only after its decision exists, is
   `standing`, names it in `closes`, and carries his answer in his own words (§4).
6. `check` everything; `rx7.py decisions`; `log`.

**An answer you do not fully understand is not a ruling.** "I don't understand the
question", "it sounds like…", or an answer to a question you did not ask means the block
was unclear: rewrite it plainer, leave it open, and rule nothing. Guessing his intent
here is the one way this system can put a wrong fact in the permanent record.

### 6.3 · Source (phase SOURCING)

Carts and parts only. Every line traces to a row that needs it and a quantity the record
derives. A line with no consumer is deleted; a consumer with no line is a block if it
costs money, a row if it does not. Never let a cart and the design disagree — the design
wins, and the cart is brought to it.

### 6.4 · Build (phase BUILDING)

He says what he did. Parse it into: steps done · measurements (number, unit, the step it
belongs to) · things found · things bought. File each where it lives, `get` first. A
measurement that contradicts the design is a finding: report it, block it if it costs
money, and never soften a check to make it fit. Hand back exactly one thing — the next
open step whose gate is met, its gate, its tools, and the measurement it wants.

### 6.5 · Review (any phase ≥ PLANNING)

Changes nothing. Four isolated readers, each given only its own section — the designer,
the buyer who never sees the design, the builder who only follows instructions, and an
auditor who reads all three plus the decisions. This is his standing quality bar and it
is the reason the sections must each stand alone. Findings get severity (Blocker / Major
/ Minor / Nit) and land as work rows or blocks; nothing else is written.

### 6.6 · Complete (phase BUILDING, everything done)

As-built facts and service instructions fold into `00-CAR`; all process — decisions,
blocks, work, logs, carts — moves to `99-ARCHIVE/<date>_<project>/`; the project's area
is removed. `00-CAR` states what _is_, never how it was decided: it never cites a `D-` or
a block id.

### 6.7 · Log a service act

One row in `00-CAR`: the work, the mileage, the parts fitted, anything found wrong. No
project needed.

### 6.8 · New project

An area is a directory with `data/_project.csv`, `_tables.csv`, `_schema.csv`,
`decisions.csv`, `work.csv`, `log.csv`, `retired.csv`. Phase PROPOSED. Read the boundary
first — `00-CAR` and any sibling table that looks like a hand-over — then write the
opening blocks (every call only he can make, easiest first) and the first work list.

---

## 7 · Credit rules

One row, one call: `get` / `sql` / `find` to learn a fact, never a whole file. Never
re-derive what a row or a decision settles. Never rewrite a file to change part of it.
Never restate the record back to him — report the diff. Batch edits; one `check` at the
end. One search per unknown fact, then a block. A whole-file write only for a new file or
a rewrite he named.

---

## 8 · Reporting — the only time you speak

You report **once per run**, and only when blocks have stopped all remaining progress or
the run is finished. Ten lines or fewer, no explanations, no restating anything he can
read:

```
DID        what got done, by work id
DECIDED    D-### one line each
BLOCKED    00.## (project.number) and the one-word ask
CHANGED    tables and rows touched
RECORD     valid / N problems
NEXT       what runs when the blocks are answered
```

Then stop. He clears the blocks and says continue.

---

## 9 · One tree, and what is left of the old one

**One machine: `/home/crash/docs/storage/Rx7` on Fedora.** Since 2026-09-22 this is the only
computer the project lives on — there is no laptop and no `crashs-pc` any more, and nothing
is synced between machines. It is a git clone of `github.com/CamdenThomas/Rx7`; the remote
is the backup, not a second place to work. Any instruction, script or path that assumes
Windows (`C:\…`, `.bat`, `.ps1`, `.exe`, w64devkit) is stale.

The tools on this machine, and nothing else:

- `python` / `python3` (3.14) runs `tools/rx7.py`; the pre-commit hook is enabled
  (`git config core.hooksPath .githooks`, set once per clone).
- KiCad 10.0.6 system-wide: `kicad`, `kicad-cli` in `/usr/bin`.
- Firmware: `firmware/tests/run.sh` and `firmware/icu_sim/build.sh` need
  `sudo dnf install gcc-c++ SDL2-devel` once; flashing a Teensy needs PJRC's udev rule
  (`firmware/README.md` §4). The car's diagnostic port `DP-DIAG` takes Camden's Windows laptop,
  which runs ECUMaster's PMU client and nothing else for this project (D-376). It holds no
  clone, and it is not a second home for the tree.

**The v2 working tree is gone.** On 2026-09-12 the v3 record replaced it, after a
file-by-file check that nothing needed had been left behind: every open question carried
into a block, a work row or a decision; the firmware byte-identical; the v2 tools, the
eleven skills and `WORKFLOWS.md` preserved under `99-ARCHIVE/2026-09-11_v2-view-and-tools/`.
The only rows that vanished were `L2-NZL` and its two cavities, which is D-329 doing its
job. If you need to know how something used to read, the archive is where it lives now —
there is no second directory to open, and any instruction that says otherwise is stale.

**The visual layer is still a later concern.** `DECISIONS.md` remains the one generated
file. Do not build a view, a template or a rendered document, and do not write a document
"so it can be read" (§1). The one exception is
`02-PROJECTS/00-electrical/cad/`: the KiCad projects for the ICU and DCU carriers —
schematic, board layout and 3D model, with `PCB-AND-3D-GUIDE.md` as the method — ruled in
by Camden on 2026-09-12 (the schematic) and widened on 2026-09-21 (layout, both boards,
D-361). It is not an area — no `data/`, so `rx7.py` cannot see
it — nothing in the record cites it, and if the record and a drawing ever disagree the
record is right. Its own README is the fence.

The Claude Project holds one pointer document and nothing else; nothing is ever queued
there.

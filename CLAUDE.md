# CLAUDE.md — the Rx7 tree

*Rev 2026-09-11 (v3). This file is the whole instruction set. There are no skills, no
slash commands, no second document. If a rule is not here it is not a rule; if you need
one that is missing, that is a block.*

> **THE PROJECT IS `Rx7-v3`. `Rx7` IS REFERENCE ONLY.**
> Every read, every write, every command runs in `Rx7-v3`. `Rx7` is the previous system,
> frozen: open it to look something up, never to change it, and never to run a tool in
> it. If you are about to touch a path with no `-v3` in it, stop — that is the mistake.
> §9 has the full rule and the conversion plan.

---

## 0 · Start

```
python tools/rx7.py status
```

Read nothing else until it tells you where things stand. `status` prints: whether the
record is valid, each area's phase, open work by owner, and the blocks. On Windows the
tool sets its own encoding; you do not need `PYTHONIOENCODING`.

Then take **exactly one** of two paths. There is no third.

| | Path | When |
|---|---|---|
| **A** | **Do the work.** Read this file for the rule, apply it, move on. | Every doubt that §3 calls small. |
| **B** | **Write a block.** Append it to `BLOCKS.md` and keep going on everything else. | Every doubt that §3 calls big. |

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

An **area** is any directory holding `data/_tables.csv`: `00-CAR` (the car itself, phase
PERMANENT), `01-REFERENCE` (manuals, factory circuits, photos, sources — PERMANENT), and
each project under `02-PROJECTS`.

**There is one data format.** Everything is a CSV table, including the schema, so the
description of the record is checked by the same code that checks the record. A table
that is not declared, a declared table with no file, an undeclared column, a missing
column, a value that is not its declared type, a duplicate or empty key, a reference to
a row that is not there — each is a refusal naming the exact row.

**No counter is ever stored.** The next `D-` is derived from the highest that exists
anywhere in the tree or the archive; the next `BLK-` from `BLOCKS.md`. A stored counter
can disagree with reality. Never type an id — `rx7.py new` and `rx7.py block` issue them.

**There is exactly one generated document: `DECISIONS.md`.** Nothing else. No templates,
no rendered design or shopping or install documents, no HTML, no diagrams. The v2 view
layer is in `99-ARCHIVE/2026-09-11_v2-view-and-tools/` and the old tree is still at
`..\Rx7` for reference. The visual layer is a separate, later concern; until it exists,
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

**Exit codes are the only signal anything may branch on.**

| Code | Means | Effect |
|---|---|---|
| `0` | valid / done | — |
| `1` | **invalid** — the record contradicts itself | the only code that blocks a commit |
| `2` | nothing to do, or something waits on a person | **blocks nothing, ever** |

Never branch on the text of any command's output. Never grep it, never test it for a
word. If you need a machine-readable fact you do not have, add a command or a column.
*This is the rule v2 broke in four places and it is why a clean build could stop a push.*

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
rx7.py block "ask" [-p AREA]             append a block to BLOCKS.md
rx7.py blocks [--answered|--solved]      list blocks
rx7.py decisions                         regenerate DECISIONS.md (grouped by category)
rx7.py cites                             advisory: prose cites that no longer resolve
rx7.py log AREA KIND "what" [refs]       one log row
```

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
new blocks and move solved ones to the SOLVED section, and that is all that ever touches
it. No tool rewrites it, and no output of yours ever invites him to type anywhere else.

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

| Doubt | Standing answer |
|---|---|
| A check refuses | Fix the data. Never the check — unless the check itself is wrong, in which case fix it and say so in the decision. |
| A type or enum refuses a legitimate new value | Widen it in `_schema.csv` deliberately, in the same pass, and note why. Never work around it in the data. |
| A fact has no column | Add the column to `_schema.csv`, then the value. |
| A fact has no table | Add the table to `_tables.csv` and `_schema.csv`, then the rows. |
| Two areas both want a fact | It belongs to whoever owns the work. A fact about the car as it stands belongs to `00-CAR`; a fact about what a project will do belongs to the project. |
| A number could be derived or typed | Derive it. A typed derived number is drift waiting to happen. |
| A part number cannot be verified | Put the row in with the note `confirm`, keep going, and block it only if buying it wrong costs money. |
| A quantity is uncertain | Round up to the next sane pack size, note the margin. Wire: 1.5× measured route length. |
| Units | Millimetres, amps, volts, AWG, ISO dates. Numbers in cells, no units, no formatting, no bold — units belong in the column name or `note`. |
| A row needs changing | `get` it first, always. |
| Something is ambiguous in what Camden wrote | Take the reading that keeps the most options open, write it into the record, and note the reading in the decision. If both readings cost money, block it. |
| A superseded decision must be cited | Cite it with its closer: `D-247 → D-278`. |
| An old cite no longer resolves | `rx7.py cites` lists these. Advisory. Fix them when you are already in the file; never let one stop a run. |
| The record and your memory disagree | The record wins. Always. |
| You are about to write a document | Don't. `DECISIONS.md` is the only one, and `rx7.py decisions` writes it. See §1. |
| You wrote a decision this run | Run `rx7.py decisions` before you report. |

---

## 4 · Blocks

`BLOCKS.md` has two sections, `## OPEN` and `## SOLVED`. A block looks like this:

```
### BLK-007 · electrical-build
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
length, no markers to preserve. Blank means unanswered. Ids are `BLK-`, never `B-`: this
car's factory diagrams already use `B-12` and `D-01` as component codes, and an id family
must never share a namespace with the subject matter.

**The clarity bar.** A block must be answerable from the page alone, with no design in
front of him — the same three-isolated-workers standard as everything else. `check`
refuses a block missing any of Ask / Why / Options / Recommend / Stops. If he answers
"unclear — <what is missing>", that is a defect in the block: sharpen it, do not rule it.

**Lifecycle.** You append it → he types a solution → `rx7.py blocks --answered` finds it
→ you apply it (§6.2) → you move the block under `## SOLVED` with `→ D-###` naming the
decision it produced (several, comma-separated, if it produced several). An
answered-but-unapplied block is exit code **2**. It never refuses a commit. *That single
sentence is the whole fix for why he could not push.*

**A block that came back unclear is replaced, not ruled.** Move it to `## SOLVED` with
`→ BLK-###` pointing at a new, plainer block — his words stay where he wrote them, the
page stops claiming an answer is waiting to be applied, and nothing was guessed. If his
answer contained a question for you, answer it in the new block's **Why**, then ask only
the part that actually needs him.

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

---

## 6 · Playbooks

Each of these is one run. Every run ends the same way: `check` clean, `rx7.py decisions`
if a decision was written, a `log` row, and — only if blocks have stopped everything —
the report in §8.

### 6.1 · Plan (phase PROPOSED or PLANNING)

1. `status`. If any block is answered, do 6.2 first — an answer can change how an
   earlier work item should be done.
2. `sql AREA "select id, item, gate, owner, state from work where owner='agent' and state='open'"`.
   Take the first whose gate is met.
3. Do it through the record only: facts become rows (R1); a derivation becomes a query,
   never a typed number; a fact with no column gets a column (§3). Anything §3 calls big
   becomes a block plus a Camden-owned work row gated on it, and the item stays open with
   `note=waits on BLK-…`.
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
5. Move each solved block under `## SOLVED` with `→ D-###`.
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
is removed. `00-CAR` states what *is*, never how it was decided: it never cites a `D-` or
a `BLK-`.

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
BLOCKED    BLK-### and the one-word ask
CHANGED    tables and rows touched
RECORD     valid / N problems
NEXT       what runs when the blocks are answered
```

Then stop. He clears the blocks and says continue.

---

## 9 · The two directories, and the plan

There are two trees side by side. Confusing them is the easiest serious mistake
available, so the rule is absolute.

| | Path (laptop) | What it is | What you may do |
|---|---|---|---|
| **`Rx7-v3`** | `C:\Users\Camden Thomas\Documents\Storage\Rx7-v3` | **The project.** The live record. | everything |
| `Rx7` | `C:\Users\Camden Thomas\Documents\Storage\Rx7` | The previous system, **frozen for reference** | read only |

On the desktop `crashs-pc` both sit under `C:\Users\USER\Documents\Storage\` with the
same two names. Both `Rx7-v3` clones are git; pull before you start.

**`Rx7` is frozen.** It holds the v2 rendered documents, the eleven skills, the old
1,307-line tool and Camden's own uncommitted work as he left it. Open it to look
something up — a design paragraph, an old diagram, how something used to read. Never
write a file in it, never run a tool in it, never run git in it, and never let a path
without `-v3` appear in a command you are about to execute. A fact worth keeping from it
is copied into the v3 record, not edited where it lies.

**The plan, in order.** Finish the **data** side in v3 first: every ruling applied, every
agent work row done, every table declared and clean, the design frozen. Only then the
visual layer — and that is a separate, later, read-only concern that reads the v3 record
and writes nothing back to it. Do not start it, sketch it, or write a document "so it can
be read" before the data side is finished (§1). `DECISIONS.md` is the one generated file
and it is not the beginning of a view layer.

**When v3 is complete**, `Rx7` is archived wholesale and stops existing as a working
tree. Until then it is a library, not a workspace.

The Claude Project holds one pointer document and nothing else; nothing is ever queued
there.

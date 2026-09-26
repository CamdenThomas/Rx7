# CLAUDE.md — the Rx7 tree

_Rev 2026-09-24 (v3, pages retired — D-405). This file is the whole instruction set. There
are no skills, no slash commands, no second document. If a rule is not here it is not a
rule; if you need one that is missing, that is a block._

> **THERE IS ONE TREE: `~/docs/storage/Rx7`, on one machine.** The v3 conversion finished on
> 2026-09-12: v3 became this directory and the old v2 working tree was deleted. Any
> instruction you find anywhere telling you that `Rx7-v3` is the project, or that `Rx7`
> is frozen reference, is stale — that folder no longer exists. §9 has what is left of
> the history.

---

## 0 · Start

```
git pull --rebase
python tools/rx7.py status
```

Pull first, every run: Camden answers from his phone, and the phone commits straight to
GitHub (D-403). Then read nothing else until `status` tells you where things stand. It
prints whether the record is valid, each area's phase, open work by owner, the open blocks
and the answers waiting in the inbox.

Then take **exactly one** of two paths. There is no third.

|       | Path                                                                             | When                             |
| ----- | -------------------------------------------------------------------------------- | -------------------------------- |
| **A** | **Do the work.** Read this file for the rule, apply it, move on.                 | Every doubt that §3 calls small. |
| **B** | **Raise a block.** `rx7.py block` it into the record and keep going on the rest. | Every doubt that §3 calls big.   |

You never ask Camden a question in chat. You never stop mid-run. You speak to him once,
per §8, and only when blocks have stopped all remaining progress.

---

## 1 · The record

The record is CSV, and it describes itself.

```
<area>/data/_project.csv    key,value        — name, kind, phase, goal, icon
<area>/data/_tables.csv     table,purpose    — every table that exists
<area>/data/_schema.csv     table,column,type,required,ref,note
<area>/data/*.csv           the facts — one row per thing, first column the key
<area>/data/decisions.csv   every ruling, its full text in `body`
<area>/data/blocks.csv      the questions only Camden can answer (§4)
<area>/data/inbox/*.csv     his answers waiting to be applied, one file per answer (§4)
```

A car-level ruling that belongs to no project (a fluid, a service call) is a decision in
`00-CAR/data/decisions.csv`, closing a `CAR.` block; `00-CAR`'s other tables still never
cite it (§6.6).

An **area** is any directory holding `data/_tables.csv`: `00-CAR` (the car itself, phase
PERMANENT), `01-REFERENCE` (manuals, factory circuits, photos, sources — PERMANENT), `02-APP`
(the Rx7 app and its own work, D-428), and each project under `02-PROJECTS`.

**There is one data format.** Everything is a CSV table, including the schema, so the
description of the record is checked by the same code that checks the record. A table
that is not declared, a declared table with no file, an undeclared column, a missing
column, a value that is not its declared type, a duplicate or empty key, a reference to
a row that is not there — each is a refusal naming the exact row. `inbox` is the one
folder table: each row is its own file, `data/inbox/<key>.csv`, so the phone and the
desktop can never write the same file (D-405). `rx7.py` reads and writes it like any other.

**No counter is ever stored.** The next `D-` is derived from the highest that exists
anywhere in the tree or the archive; a project's next block from the highest number that
project has used, in `blocks` or in any decision's `closes`. A stored counter can disagree
with reality. Never type an id — `rx7.py new` and `rx7.py block` issue them.

**There are no pages (D-405).** Blocks, his answers, parts picks, the TODO lists and every
decision live in the record, and **the Rx7 app** (`02-APP/app`, a desktop app
and an Android app) is how he reads and answers them. Do not write a Markdown page for him
to read or to type in: not a TODO, not an index, not a summary, not a spec sheet. What was
`BLOCKS.md`, `PICKS.md`, `DECISIONS.md` and each `TODO.md` is now a screen in the app,
computed from the record every time it is shown. The app keeps no fact of its own, reads
the record only through `rx7.py export` (JSON), and writes only his answers, only through
`rx7.py answer` (or, on the phone, the same function). Nothing in it gates a commit.

**The Manual (D-417)** is the app's view of `00-CAR` as the car is now. `rx7.py export`
computes it (`manual`). It shows only backed facts: a row still saying `confirm` in a shown
cell, an `unverified` spec, or a spec or interval whose `applies` is `other-car` is held back
and listed with the reason. `replaced` and `not-fitted` rows are not facts about the car now,
and are neither shown nor listed. So an unchecked value keeps its `confirm` (R11), and a
factory figure for a part that has gone is marked `applies=replaced`, never deleted. A part's
fitted date is read from the `service` visit whose `fitted` names it, and the odometer is read
from the newest `drives` or `service` reading. Neither is ever typed.

**Files that stay files.** This one. `02-APP/README.md`, where the app's design
is pitched, at his request. Code and drawings with the READMEs that belong to them: the
firmware, the KiCad boards, the tools, the app. The reference write-ups in `01-REFERENCE`
and `00-CAR/data/procedures/` wait for the Manual's plan (D-407). And `99-ARCHIVE`.

**The one generated file type left is the harness-leg drawings** (D-385): for each leg,
`A-pin-ladder.svg` and `B-route-map.svg` in `02-PROJECTS/01-electrical/00-design/diagrams/`,
a pure projection of `housings`, `cavities`, `devices` and `routes`, read-only, rebuilt whole
by `rx7.py diagrams`, and never looked at by `check`. The command refuses to write any sheet
where a label touches a label or sits on a wire (rc 2). Fix that in the layout code, never
by loosening the check. `00-design/diagrams/README.md` holds the method and the options
kept in reserve.

**The work list is the `work` table, and the app's TODO page shows it:** what can start
today, then every row in working order (stages in the order their work can start, each row
after what it waits on), each with its note. It has **no boxes to tick** for anyone but
him, and his ticks are answers (§4): `work.reply` says how he answers his row — `check`
(done), `value` (a measurement in `work.unit`) or `choice` (one of `work.choices`, split on
`|`). His answer arrives in `inbox` and you set the row (§6.4).

**A project whose `work` has a `track` column has two lists** (D-386 → D-405; today
`01-electrical`). Each row's `track` says which:

- **design**: his checklist in working order and every agent row, ready or blocked and by
  what, then the open blocks. Its last two rows are the design review (§6.5) and his freeze
  ruling.
- **build**: everything physical and everything bought. **Every build row gates on
  `phase:SOURCING`**, which only the freeze moves, so nothing in build starts before the
  design is verified. The freeze does not close design (D-398, §6.1): a design row opened
  after it gates the build rows it changes, by id.

A new row goes on the track where its work happens: desk, measurement, bench proof or the
agent's work is design; the cart, the car, and the modules' fabrication are build.

**The car comes apart once** (D-387). `_project` names the row that strips the interior
(`car_apart`, S1) and the one that puts it back (`car_back`, E35). Each list is split at those
rows: design Part 1 is everything with the car whole, and S1 waits on all of it; Part 2 is S1,
the measurements that need the car apart, the review and the freeze. Build Part 3 is the car
apart, and Part 4 starts at E35. A row's part is derived from its gate, never typed: a row
that needs the car apart gates on S1.

**Exit codes are the only signal anything may branch on.**

| Code | Means                                         | Effect                                                                 |
| ---- | --------------------------------------------- | ---------------------------------------------------------------------- |
| `0`  | valid / done                                  | —                                                                      |
| `1`  | **invalid** — the record contradicts itself   | the only code that blocks a commit                                     |
| `2`  | nothing to do, or something waits on a person | **blocks nothing, ever**                                               |
| `3`  | a usage error or a crash in `rx7.py` itself   | **blocks nothing** — a broken checker is never a verdict on the record |

Never branch on the text of any command's output. Never grep it, never test it for a
word. If you need a machine-readable fact you do not have, add a command or a column —
`rx7.py export` is the machine-readable view of everything.
_This is the rule v2 broke in four places and it is why a clean build could stop a push._

### The tool

```
rx7.py status                            where everything stands
rx7.py check [-p AREA]                   validate (rc 1 if the record contradicts itself)
rx7.py tables AREA                       every declared table, row counts, purpose
rx7.py get AREA TABLE KEY                one row
rx7.py set AREA TABLE KEY col=val ...    change an existing row   (col=@file reads a file)
rx7.py add AREA TABLE col=val ...        add a row                (col=@file reads a file)
rx7.py del AREA TABLE KEY                delete a row
rx7.py sql AREA "select ..."             query one area (read-only)
rx7.py find TEXT [-p AREA]               search every cell, decision bodies included
rx7.py new AREA "title" [col=val ...]    reserve the next D- (body=@file writes its text)
rx7.py block -p AREA ask= why= options= recommend= stops= [title=]   raise a block (§4)
rx7.py blocks [--answered]               open blocks; --answered: those with an answer waiting
rx7.py inbox [-p AREA]                   his answers waiting to be applied, his words in full
rx7.py answer AREA TARGET --device D ... save one of his answers (the app calls this)
rx7.py export [--out F] [--pretty]       everything the app shows, as JSON
rx7.py diagrams                          regenerate each harness leg's pin ladder (A) and route map (B)
rx7.py picks [-p AREA]                   where every parts pick stands
rx7.py cites                             advisory: prose cites that no longer resolve
rx7.py selftest                          the tool's own tests (in memory and a scratch folder)
rx7.py log AREA KIND "what" [refs]       one log row (KIND = the area's log.workflow enum)
```

### Gates and READY

`work.gate` holds **references, and nothing else** — prose belongs in `note`. All of them
must be met before the row can start; an empty gate is met. They resolve across the whole
tree, so one area can wait on another:

| Reference         | Met when                                                                                                 |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| `D-274`           | that decision is standing or inherited                                                                   |
| `01.07`           | that block is gone from `blocks` and a decision names it in `closes`                                     |
| `A5` · `F-012`    | that work row is done or dropped, in this area                                                           |
| `03-luxury:F-012` | the same, in another area — **always qualify across areas**, because work ids are only unique within one |
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

`selftest` checks the resolver itself, and the writer of his answers. A resolver that
wrongly calls a gate met sends the planner at work that is not ready; one that wrongly calls
it unmet stops the project with no error printed anywhere. A writer that drops a character
loses his words. All three are silent, so all three get tests (R7).

`set`, `add` and `del` refuse a column that `_schema.csv` does not declare. To add a
fact that has no column, add the column to `_schema.csv` first — that is a small
decision (§3) and it is how the design grows.

---

## 2 · Who does what

**Camden**: answers in the Rx7 app — blocks, parts picks and his own work rows · spends
money · does the physical work and says what happened · takes measurements.

**You**: everything that is reading, writing, calculating, cross-checking, enumerating,
sourcing, or deciding within §3's small list, and keeping the repository current:
you commit and push (§6.10, D-401). If a step needs a call only he can make,
raise a block and carry on with the rest of the run.

**He writes in no file.** Everything he types goes through the app into `inbox`, one file
per answer, and from there into the record through you (§4, §6.2, §6.9). He may also tell
you things in chat; that is a ruling or a fact like any other, recorded the same way. Nothing
you write ever invites him to type anywhere else.

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

**BIG — raise a block. Any one of these is enough:**

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
raising a block, `rx7.py find` the subject: if a decision already rules it, the decision
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
| You are about to write a document             | Don't. There are no pages (§1); the app shows the record. The leg drawings are the only generated files, and `rx7.py diagrams` writes them.             |
| A decision's body is long                     | Write it to a scratch file and `rx7.py new AREA "title" … body=@file` (or `set … body=@file`). Never hand-edit `decisions.csv`.                         |
| A row of his in `work` takes a number or a choice | Set `reply=value` with `unit`, or `reply=choice` with `choices` (`a\|b\|c`), so the app offers the right control (D-406). A plain step needs nothing: `check` is the default. |
| You changed `housings`, `cavities`, `devices` or `routes` | Run `rx7.py diagrams` before you report.                                                                                                      |

---

## 4 · Blocks

A block is **one row in its project's `blocks` table**, and only what is still open is
there. The app shows each one on its own screen, with every option as a button. A block has
exactly these fields, and `check` refuses one missing any:

```
id         00.07                        issued by rx7.py block, never typed
title      A short title
opened     2026-09-21
ask        One sentence, answerable on its own.
why        What changes depending on the answer.
options    (a) … — what it costs, what it forecloses
           (b) … — what it costs, what it forecloses      one per line, lettered in order
recommend  (a), unless <the thing that would flip it>.  name the option first: the app's
                                                          "follow the recommendation" reads it
stops      What cannot proceed until this is answered.
```

Raise it in one go, every field at once (`rx7.py block -p AREA ask=… why=@why.txt
options=@opts.txt recommend=… stops=…`). Long fields go through `@file`.

**Block ids are `<project>.<number>`** (D-356): `01.12` is the twelfth block raised for
`02-PROJECTS/01-electrical`, `03.07` the seventh for `03-luxury`. The prefix is the project
directory's two-digit number; `00-CAR`, `01-REFERENCE` and `02-APP` use `CAR`, `REF` and
`APP`, because they are not numbered projects. Never `B-`: this car's factory diagrams already use `B-12` and
`D-01` as component codes, and an id family must never share a namespace with the subject
matter. And because a bare `13.80` in prose is a voltage, a block id is only recognised as
structure — a `blocks` key, `closes`, a gate. In prose write it as `block 00.07` or in
backticks. Blocks were `BLK-###` until 2026-09-21; each old id is a `retired` row in its
project naming the new one.

**The projects moved up one number on 2026-09-25** (D-427) to make room for `00-verify`:
electrical 00 → 01, luxury 01 → 02, engine 02 → 03, beauty 03 → 04; 10-gui kept 10. The same
day Camden swapped engine and luxury and took the app out of the projects (D-428): the tree
is now `00-verify`, `01-electrical`, `02-engine`, `03-luxury`, `04-beauty`, and `02-APP`
(was `02-PROJECTS/10-gui`, block prefix `APP`; engine's open `03.02` became `02.12` and
luxury's `02.11` became `03.12`). Open
blocks were renumbered and their old ids retired. Decisions and logs are never edited, so a
block id in one written before that date keeps its old project: `00.NN` there is electrical,
`01.NN` luxury, `02.NN` engine, `03.NN` beauty. Numbering is derived from every `closes` and
retired id, so no new id repeats an old one.

**The clarity bar.** A block must be answerable from its screen alone, with no design in
front of him — the same three-isolated-workers standard as everything else. If he answers
"unclear — <what is missing>", that is a defect in the block: sharpen it, do not rule it.

**His answers.** He answers in the app: an option (its letter), "follow the
recommendation", words, or both — and a Discuss chat's key points ride along in `context`.
Each answer is a row in the project's `inbox`, saved as its own file
`data/inbox/<target>~<device>.csv`, and it waits there until he presses Apply, the desktop
app's auto-apply starts the run (90 seconds after his last answer, D-413), or you next run. The same table carries his answers to parts picks (`kind=pick`: yes, no or question),
to his own work rows (`kind=work`: done, a value, a choice), and requests for a run from the
phone (`kind=run`, `kind=project`), and, in `00-CAR`, the Manual's Log drive and Set odo
(`kind=drive`: the choice is the odometer, target `drive-<when>` or `odo-<when>`). An answer in the inbox is exit code **2**. It never
refuses a commit.

**His notes are not answers (D-426).** A `kind=note` row in `00-CAR`'s inbox (target
`note-<when>`) is a note he made on words he selected in the Manual. Its `context` holds
`where:`, `page:` and `selected:`. It is a log he keeps while the Manual is being dialled in:
no run applies it or deletes it, `inbox` and `status` do not count it as waiting, and only he
removes one, from the Notes page. Read notes as leads when you work on the Manual, and act on
one only when he asks.

**Lifecycle.** You raise it → he answers in the app → `rx7.py inbox` shows his words → you
apply it through the record (§6.2) → the ruling becomes a decision whose `closes` names the
block → **you delete the block row and its inbox rows.** Before deleting, confirm three
things: the decision exists and is `standing`, its `closes` names the block, and its body
carries **his answer in his own words**. If any of those is missing, finish the job instead
of deleting. `check` refuses a block that a standing decision already closes. Ids are never
reused — `rx7.py block` derives the next number from the decisions as well as the table,
so a deleted 01.05 can never come back as something else.

**A block that came back unclear is replaced, not ruled.** Raise the new, plainer block
first, carry his words into its **why** so nothing he typed is lost, then delete the old
block and his inbox row. If his answer contained a question for you, answer it in the new
block's why, then ask only the part that actually needs him.

---

## 5 · Standing rules

**R1** `get` a row before changing it.
**R2** One home per fact. If it can be computed, compute it.
**R3** Nothing you generate may contain a place to type. His writing enters only through
the app, into `inbox` — one file per answer, written whole or not at all — and no reader of
his writing may be picky. Losing his writing is the worst failure this system has; a wrong
ruling is recoverable, a lost answer is not. An inbox row is deleted only by you, and only
once his words are saved where they ruled.
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

Each of these is one run. Every run starts with `git pull --rebase` and ends the same way:
`check` clean, `rx7.py diagrams` if a harness table changed, a `log` row, a commit and a
push (§6.10), and — only if blocks have stopped everything — the report in §8.

### 6.1 · Plan (any project, any phase)

**Planning is open in every project at every phase** (D-398). The phase says how far the
build has got, never whether design may be touched: a project in PROPOSED, SOURCING or
BUILDING takes design work, blocks and parts rounds exactly as one in PLANNING does, and
one project's phase never holds another's planning. Past the freeze, new design work never
moves the phase back. The new row goes on the design track, and every build row it changes
gets the new row's id in its gate, so only that work waits and the rest of the build carries
on. Undoing work already done (re-cutting, re-ordering, re-wiring) is §3's irreversible,
so it is a block.

1. `status`. If any answer is in the inbox, do 6.2 first — an answer can change how an
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
   Major review finding → raise the design-freeze block. The freeze is his ruling; it
   moves the phase to SOURCING. It starts the build; it does not end planning.

### 6.2 · Apply his answers

1. `git pull --rebase`, then `rx7.py inbox`. Read every answer before touching anything.
2. **If it shows none and he says he answered, find the text before doing anything
   else.** Pull again, then look at `git log -5 --stat` and `git status` for `data/inbox/`
   files, then `git stash list`. His phone commits straight to GitHub, so a missed pull is
   the usual cause. Never tell him nothing was answered until you have looked. Never run
   anything that writes until you have.
3. Classify each (`rx7.py inbox` already leaves out his notes, `kind=note`, which are never
   applied — §4): a **ruling** (a letter, "follow recommendation", yes / no / a choice) → a
   decision. A **brief** (guidelines, a re-framing, "help me choose") → sharpen the block
   and leave it open. A **question back** → answer it in the block's why and leave it open
   (delete only his inbox row, once his question is carried into the why). A **fact about
   the car** → `00-CAR` rows plus every project row it corrects. A letter with words means
   the option as he qualified it — the words win where they narrow it.
4. For each ruling, in this order:
   a. Write the body to a scratch file — the decision in bold, his words (the option he
   picked, quoted in full, then anything he typed, verbatim, then the Discuss points in
   `context` if any), the reasoning, what it supersedes by id, the consequences in the
   data — then `rx7.py new AREA "<title>" closes=… supersedes=… body=@file`.
   b. Every row the ruling changes — `get`, then `set` / `add` / `del`. A ruling that
   touches three projects is applied to all three in the same pass.
   c. Every retired term into `retired.csv` so it can never come back.
   d. New questions the ruling raises → new blocks.
   e. Work rows gated on it: gate met → leave open for 6.1; the ruling did the work →
   `state=done`.
5. Delete each solved block's row and its inbox rows, but only after its decision exists,
   is `standing`, names it in `closes`, and carries his answer in his own words (§4).
6. `check` everything; `log`.

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

He says what he did — in chat, or as answers to his work rows in the app (`kind=work` in
the inbox: `done`, a value in the row's `unit`, or one of its `choices`). Parse it into:
steps done · measurements (number, unit, the step it belongs to) · things found · things
bought. File each where it lives, `get` first; a measurement goes into the row it measures,
not only into the work row. A measurement that contradicts the design is a finding: report
it, block it if it costs money, and never soften a check to make it fit. Delete each inbox
row once it is filed. Hand back exactly one thing — the next open step whose gate is met,
its gate, its tools, and the measurement it wants.

### 6.5 · Review (any phase)

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

A `kind=drive` answer is one `drives` row: its id is the answer's target, `date` from its
`at`, `odometer` its choice, and `kind` is `set` for an `odo-` target and `drive` otherwise.
His words go into `from`, `to` and `note` as he wrote them. A reading lower than the one
before it is a finding: raise it, and never write it over. Delete the inbox row once the
drives row exists.

### 6.8 · New project

An area is a directory with `data/_project.csv` (with an `icon` from the app's icon set),
`_tables.csv`, `_schema.csv`, `decisions.csv`, `blocks.csv`, `work.csv`, `log.csv`,
`retired.csv`, and `inbox` declared. Phase PROPOSED. Read the boundary first — `00-CAR` and
any sibling table that looks like a hand-over — then raise the opening blocks (every call
only he can make, easiest first) and the first work list. From the app, "New project"
arrives as a run whose prompt carries his name and goal, or from the phone as an inbox row
`kind=project` in `00-CAR` (target = the name, text = the goal); delete that row once the
area exists.

---

### 6.9 · A parts round (D-388, D-390 → D-405)

Choosing a product is money, so it is always his ruling. A round is how the ruling is asked
for.

1. Pick the parts to search: rows whose spec is settled (nothing in their gate is open), plus
   any part whose last pick was vetoed. Read every veto for that part first. His reason
   rules out a class of product, not just the one item.
2. For each part, find one **primary** and one **runner-up**. Each gets real listings with
   prices, the numbers that meet the parts row's spec, why, honest drawbacks, a confidence,
   and what must still be confirmed (R11: a fit nobody has measured is `confirm`). Add them to
   `picks`, with the primary `proposed` and the runner-up `reserve`. The app shows every
   `proposed` pick as a question at once; there is nothing else to write.
3. He answers any, some or all, whenever he likes: `yes`, `no` with a reason, or a question.
4. When answers are in the inbox (`kind=pick`), read every one before touching anything.
   Classify each the way §6.2 does:
   - A **yes** makes the pick `accepted`. The yeses in one pass become one decision naming
     each product, and each parts row is updated (`spec` names the product, the prices,
     `status` `chosen`).
   - A **no** makes it `vetoed`. The runner-up is proposed next unless his reason rules it
     out too; otherwise the search starts again.
   - A **question or an unclear answer** leaves it `proposed`. Answer the question in the
     next suggestion for that part (its `why` or `confirm`), or sharpen the pick.

   His words go in `picks.said`, verbatim, every time. Then delete exactly the inbox rows
   whose verdict and words are saved.

### 6.10 · Commit and push (the end of every run, D-401)

You commit and push; Camden no longer does. The repository is kept current and its history
useful:

- **Small commits, one change each**: a decision and the rows it moved, one work item, a
  tool fix. Never one commit for a whole session of unrelated changes. Order them so each
  one leaves `check` clean.
- **The message says what changed and why.** Subject: what changed, ending with the
  decision ids, e.g. `Luxury: every lamp to LED (D-397)`. Body: the why in a sentence
  or two, and the work ids and blocks it touches. No "update files", no "wip".
- **Straight to `master`, then `git push`.** No pull requests and no branches unless
  Camden asks. Never force-push, never rewrite pushed history, never skip the hook
  (`--no-verify`). If the push is refused because the phone committed meanwhile,
  `git pull --rebase` and push again — inbox files never conflict.
- **The hook refusing is rc 1**, the only thing that stops a commit: fix the data and
  commit again (R8). A failed push (network, auth) is not a refusal: say so in the report
  and push next run.
- **The app commits too.** Each answer he saves on the desktop is committed and pushed by
  the app on its own (`Camden answered 00.29 (desktop)`); the phone commits through
  GitHub. Never amend, squash or revert those commits.

### 6.11 · Runs started from the app

The app starts you headless, in this tree, with a prompt that names one playbook and one
project: **Apply** (§6.2 for that project, or §6.9 step 4 from the Picks page, or §6.4 from
the TODO page), **Plan** (§6.1), **Review** (§6.5), **Parts round** (§6.9), **New project**
(§6.8). It is the same run as from the terminal, under every rule here, and it ends with the
§8 report — the app shows that report to him as the run's result. A run requested from the
phone arrives as an inbox row `kind=run` (target `apply`, `plan`, `review` or `parts`) in
the project it is for: do that run, then delete the row. An Apply run the app started on its
own says so in its prompt (auto-apply, D-413); it is the same §6.2 run. While any run is
going, the app does not pull or push, so your own `git pull --rebase` and push are the only
ones in the tree.

Explain, Discuss and the app's chat start you read-only: answer from the record, never
write, never commit.

## 7 · Credit rules

One row, one call: `get` / `sql` / `find` to learn a fact, never a whole file. Never
re-derive what a row or a decision settles. Never restate the record back to him — report
the diff. Batch edits; one `check` at the end. One search per unknown fact, then a block.
A whole-file write only for a new file or a rewrite he named.

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
PUSHED     the commits, short hash and subject each, or why the push failed
NEXT       what runs when the blocks are answered
```

Then stop. He answers in the app and says continue, or presses Apply.

---

## 9 · One tree, and what is left of the old one

**One machine: `/home/crash/docs/storage/Rx7` on Fedora.** Since 2026-09-22 this is the only
computer the project lives on — there is no laptop and no `crashs-pc` any more, and nothing
is synced between machines except through GitHub. It is a git clone of
`github.com/CamdenThomas/Rx7`; the remote is the backup and the phone app's way in (D-403),
not a second place to work. Any instruction, script or path that assumes Windows (`C:\…`,
`.bat`, `.ps1`, `.exe`, w64devkit) is stale.

The tools on this machine, and nothing else:

- `python` / `python3` (3.14) runs `tools/rx7.py`; the pre-commit hook is enabled
  (`git config core.hooksPath .githooks`, set once per clone).
- KiCad 10.0.6 system-wide: `kicad`, `kicad-cli` in `/usr/bin`.
- Firmware (`02-PROJECTS/01-electrical/00-design/firmware/`): `tests/run.sh` and `icu_sim/build.sh` need
  `sudo dnf install gcc-c++ SDL2-devel` once; flashing a Teensy needs PJRC's udev rule
  (its `README.md` §4). The car's diagnostic port `DP-DIAG` takes Camden's Windows laptop,
  which runs ECUMaster's PMU client and nothing else for this project (D-376). It holds no
  clone, and it is not a second home for the tree.
- The Rx7 app (`02-APP/app/`): Node 22 and npm (dnf), Rust through rustup in
  `~/.cargo`, the Tauri build libraries (dnf, listed in the app's README), JDK 21 in
  `~/.local/jdk`, and the Android SDK and NDK in `~/Android/Sdk`. The app's README says how
  to build, test and install both apps.

**The v2 working tree is gone.** On 2026-09-12 the v3 record replaced it, after a
file-by-file check that nothing needed had been left behind: every open question carried
into a block, a work row or a decision; the firmware byte-identical; the v2 tools, the
eleven skills and `WORKFLOWS.md` preserved under `99-ARCHIVE/2026-09-11_v2-view-and-tools/`.
The only rows that vanished were `L2-NZL` and its two cavities, which is D-329 doing its
job. If you need to know how something used to read, the archive is where it lives now —
there is no second directory to open, and any instruction that says otherwise is stale.

**The visual layer is the Rx7 app, `02-APP`** (D-399 → D-405; not a project since D-428). It is a
view and an input over the record that keeps no fact of its own. Nothing else grows a view.
The generated files are only the harness-leg drawings in
`02-PROJECTS/01-electrical/00-design/diagrams/` (D-385, §1). The one hand-drawn exception
is `02-PROJECTS/01-electrical/00-design/cad/`: the KiCad projects for the ICU and DCU
carriers — schematic, board layout and 3D model, with `PCB-AND-3D-GUIDE.md` as the method —
ruled in by Camden on 2026-09-12 (the schematic) and widened on 2026-09-21 (layout, both
boards, D-361). It is not an area — no `data/`, so `rx7.py` cannot see it — nothing in the
record cites it, and if the record and a drawing ever disagree the record is right. Its own
README is the fence.

The Claude Project holds one pointer document and nothing else; nothing is ever queued
there.

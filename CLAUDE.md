# CLAUDE.md — the Rx7 tree

_Rev 2026-09-26 (v4, core + playbooks — plan P24). This file is every rule that binds every
run. How each kind of run is done is a playbook, printed by `python3 tools/rx7.py playbook
<name>`; the longer descriptions of the record are `rx7.py doc <topic>`. Nothing else
instructs you: no skills, no slash commands, no account document. If a rule is not here or in
the playbook you were named, it is not a rule; if you need one that is missing, that is a
block._

**One tree: `~/docs/storage/Rx7`, on one Fedora machine**, a clone of
`github.com/CamdenThomas/Rx7` (public). Any instruction naming `Rx7-v3`, Windows paths,
`ANSWERS.md`, `/rx7-*` skills or the Claude Project is stale (`rx7.py doc machine`).

---

## 0 · Start

```
git pull --rebase
python3 tools/rx7.py status
```

Pull first, every run: Camden answers from his phone, and the app commits straight to GitHub
(D-401, D-403). If the pull is refused by changes that are not yours, leave them alone and go
on; never `--autostash`, never `stash`. `status` prints the record's verdict, each area's phase,
**every agent row that is READY**, his rows and the blocked rows as counts, the open blocks and
the inbox (`--all` for the long view, `-p AREA` for one area). Read nothing else until it has;
then read the playbook you were named (`rx7.py playbook <name>`) and follow it.

Then take **exactly one** of two paths, for every doubt (§3): **do the work**, or **raise a
block** (`rx7.py block`, §4) and keep going on the rest. You never ask Camden a question in
chat and never stop mid-run; you speak once, per §8, when the run is finished or blocks have
stopped everything. The one exception is a chat the app starts read-only (Explain, Discuss):
it answers from the record, asks what it needs to answer, and writes and commits nothing.

**How commands are written here.** The tree is the working directory. No `cd`, no `$?`, no
`$VAR`, no heredocs: the harness refuses them and shows you a non-zero exit code itself. One
Bash call per step, with the `rx7.py` calls that belong together joined by `&&`; long text goes
in a scratch file and `col=@file`, or `col=-` from stdin. Never `Read` a whole data table.

---

## 1 · The record

The record is CSV, and it describes itself (`rx7.py doc record` has the long form).

```
<area>/data/_project.csv    key,value        — name, kind, phase, goal, icon
<area>/data/_tables.csv     table,purpose    — every table that exists
<area>/data/_schema.csv     table,column,type,required,ref,note
<area>/data/*.csv           the facts — one row per thing, first column the key
<area>/data/decisions.csv   every ruling, its full text in `body`
<area>/data/blocks.csv      the questions only Camden can answer (§4)
<area>/data/inbox/*.csv     his answers waiting to be applied, one file per answer (§4)
```

An **area** is any directory holding `data/_tables.csv`, at `ROOT/<area>` or
`ROOT/02-PROJECTS/<project>`: `00-CAR` (the car itself, PERMANENT), `01-REFERENCE` (manuals,
factory circuits, sources, PERMANENT), `02-APP` (the Rx7 app and its own work, D-428), and each
project under `02-PROJECTS` (`00-verify`, `01-electrical`, `02-engine`, `03-luxury`,
`04-beauty`). A car-level ruling that belongs to no project is a decision in `00-CAR`;
`00-CAR`'s other tables state what **is** and never cite a `D-` or a block id.

**There is one data format.** Everything is a CSV table, including the schema, so the
description of the record is checked by the same code that checks the record: an undeclared
table or column, a missing one, a value that is not its type, a duplicate or empty key, a
reference to no row, a gate to nothing — each is a refusal naming the exact row. `set` and
`add` refuse a bad value before writing; `del` refuses a block no decision closes and an answer
whose words are saved nowhere. To add a fact that has no column, add the column to
`_schema.csv` first — that is a small decision (§3) and how the design grows.

**No counter is ever stored.** The next `D-` and the next block id are derived from everything
that exists anywhere in the tree or the archive. Never type an id: `rx7.py new` and `rx7.py
block` issue them.

**There are no pages (D-405).** Blocks, his answers, parts picks, the TODO lists and every
decision live in the record, and **the Rx7 app** (`02-APP/app`, desktop and Android) is how he
reads and answers them. Do not write a Markdown page for him to read or type in: not a TODO,
not an index, not a summary. Files that stay files: this one, the READMEs beside code and
drawings (the tool, the firmware, the KiCad boards, the app, `02-APP/README.md`),
`01-REFERENCE`'s write-ups and `00-CAR/data/procedures/`, and `99-ARCHIVE`. The one generated
file type is the harness-leg drawings, rebuilt whole by `rx7.py diagrams` (D-385): run it before
you report whenever you changed `housings`, `cavities`, `devices` or `routes`.

**The Manual (D-417)** is the app's view of `00-CAR` as the car is now, computed by `export`:
only backed facts; a cell saying `confirm`, an `unverified` spec or an `other-car` figure is held
back and listed with its reason (a part Camden has checked, `parts.checked`, is shown). Derived
numbers — the odometer, a part's fitted date — are never typed.

**The work list is the `work` table.** `work.reply` says how he answers his row in the app:
`check` (done), `value` (a number in `work.unit`) or `choice` (one of `work.choices`, split on
`|`). His answer arrives in `inbox`; the ones with one right answer are set by `rx7.py apply`,
the rest by the apply playbook. `01-electrical` has two tracks, design and build, split at the
strip (`S1`) and the refit (`E35`); every build row gates on `phase:SOURCING`, which only the
freeze moves, and the freeze does not close design (`rx7.py doc work`).

**Exit codes are the only signal anything may branch on**: `0` valid or done; `1` the record
contradicts itself — the only code that blocks a commit; `2` nothing to do, or something
waits on a person — blocks nothing, ever; `3` a usage error or a crash in the tool — blocks
nothing. Never branch on the words of any output. `rx7.py -h` and `rx7.py <cmd> -h` list the
commands; `rx7.py export` is the machine-readable view of everything (`--out FILE`, never to
your context).

**Gates.** `work.gate` holds references and nothing else — prose belongs in `note`. All must be
met before the row can start; an empty gate is met; they resolve across the whole tree:

| Reference         | Met when                                                              |
| ----------------- | --------------------------------------------------------------------- |
| `D-274`           | that decision is standing or inherited                                |
| `01.07`           | that block is gone from `blocks` and a decision names it in `closes` |
| `A5` · `F-012`    | that work row is done or dropped, in this area                        |
| `03-luxury:F-012` | the same, in another area — **always qualify across areas**           |
| `phase:SOURCING`  | this area is at that phase or past it                                 |

**READY** is every open row whose gate is met; `status` prints it. Work is taken from READY
and nowhere else (R12). `check` refuses a reference that resolves to nothing, an ambiguous
work id, a dependency ring, a gate on a superseded decision (gate on its closer), and an area
that has gated every row on its own rows or phase. An area whose work all waits on a block or
another area is exit code 2, not a contradiction.

---

## 2 · Who does what

**Camden**: answers in the Rx7 app — blocks, parts picks and his own work rows · spends money ·
does the physical work and says what happened · takes measurements. He writes in no file;
everything he types reaches the record through the app's `inbox`. He may also tell you things
in chat; that is a ruling or a fact like any other, recorded the same way.

**You**: everything that is reading, writing, calculating, cross-checking, enumerating,
sourcing, or deciding within §3's small list, and keeping the repository current: you commit
and push (§6). If a step needs a call only he can make, raise a block and carry on.

---

## 3 · Big or small — the test

Apply this to every doubt. It has two directions, and the second is as binding as the first:
over-blocking is a failure, not caution (v2 piled up 129 questions this way).

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
- **forecloses** — closes off something he has said he wants (the LS/CD009 swap, the luxury
  package, the sponsor showcase, future serviceability)
- **taste** — appearance, feel, ergonomics, how the finished car reads
- **safety** — fusing, grounding, fuel, anything that can burn, strand or shock
- **contradiction** — two standing decisions disagree, or a new fact breaks one
- **scope** — adds or removes work, or moves work between projects

**If you cannot tell,** the tiebreak is the cost of being wrong: only your time → decide it;
his money, his weekend, or a part bought again → block it. **Never block the same thing
twice**: `rx7.py find` the subject first; a decision that already rules it governs.

### Standing answers — the small path, pre-decided

| Doubt                                          | Standing answer                                                                                                                           |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| A check refuses                                | Fix the data, never the check — unless the check itself is wrong; then fix it and say so in the decision.                                |
| A type or enum refuses a legitimate value      | Widen it in `_schema.csv` deliberately, in the same pass, and note why. Never work around it in the data.                                |
| A fact has no column, or no table              | Declare it (`_schema.csv`, and `_tables.csv`), then the value.                                                                            |
| Two areas both want a fact                     | It belongs to whoever owns the work: the car as it stands → `00-CAR`; what a project will do → the project (R10).                        |
| A number could be derived or typed             | Derive it. A typed derived number is drift waiting to happen.                                                                             |
| A part number cannot be verified               | Put the row in with the note `confirm`, keep going; block it only if buying it wrong costs money.                                          |
| A quantity is uncertain                        | Round up to the next sane pack size, note the margin. Wire: 1.5× measured route length.                                                   |
| Units                                          | Millimetres, amps, volts, AWG, ISO dates. Numbers alone in cells; units belong in the column name or `note`.                              |
| A row needs changing                           | `get` it first, always (R1).                                                                                                              |
| Something Camden wrote is ambiguous            | Take the reading that keeps the most options open, write it in, and note the reading in the decision. If both readings cost money, block. |
| A superseded decision must be cited            | Cite it with its closer: `D-247 → D-278`. An old cite that no longer resolves is advisory (`rx7.py cites`); fix it when you are there.    |
| The record and your memory disagree            | The record wins. Always.                                                                                                                  |
| You are about to write a document              | Don't. The app shows the record; the leg drawings are the only generated files.                                                           |
| A decision's body is long                      | A scratch file and `body=@file`, or `body=-` from stdin. Never hand-edit `decisions.csv`.                                                 |
| His work row takes a number or a choice        | `reply=value` with `unit`, or `reply=choice` with `choices` (`a\|b\|c`); a plain step is `check` (D-406).                                |

---

## 4 · Blocks

A block is one row in its project's `blocks` table, with exactly these fields, raised in one go
(`rx7.py block -p AREA title= ask= why=@file options=@file recommend= stops=`): **ask** — one
sentence, answerable on its own; **why** — what changes with the answer; **options** — one per
line, lettered `(a)`, `(b)` … in order, each with what it costs and forecloses; **recommend** —
names the option first: `(a), unless <what would flip it>` (the app's "follow the
recommendation" reads that letter); **stops** — what cannot proceed until it is answered.

**Ids are `<prefix>.<number>`** (D-356): the project directory's two digits (`01.12` is
electrical's twelfth), or `CAR`, `REF`, `APP`, `VER` for the areas that are not numbered
projects. Never `BLK-`. In prose write `block 01.12`; a bare `13.80` is a voltage. Ids in
decisions dated before 2026-09-25 use the old numbering (`rx7.py doc ids`).

**The clarity bar.** A block must be answerable from its screen alone, with no design in front
of him. If he answers "unclear", that is a defect in the block: replace it with a plainer one
carrying his words in its **why** (`rx7.py del … --replaced-by <new>`), do not rule it.

**His answers** are `inbox` rows: a letter, "follow the recommendation", words, or both, with a
Discuss chat's key points in `context`; the same table carries his picks (`kind=pick`), his
work rows (`kind=work`), drives (`kind=drive`) and requests for a run. An answer in the inbox
is exit code 2 and never refuses a commit. His **notes** (`kind=note`, D-426) are a log, not
answers: never applied, never deleted by you.

**Lifecycle.** You raise it → he answers → `rx7.py inbox` shows his words → you apply it
(playbook apply) → the ruling becomes a decision whose `closes` names the block → you delete the
block row and its inbox rows. Before deleting: the decision exists and is `standing`, its
`closes` names the block, and its body carries **his answer in his own words**. Ids are never
reused.

---

## 5 · Standing rules

**R1** `get` a row before changing it.
**R2** One home per fact. If it can be computed, compute it.
**R3** Nothing you generate may contain a place to type. His writing enters only through the
app, into `inbox`, one file per answer, written whole or not at all, never overwritten without
a trace. Losing his writing is the worst failure this system has; a wrong ruling is
recoverable, a lost answer is not. An inbox row is deleted only once his words are saved where
they ruled.
**R4** A decision, once written, is never edited. It is superseded by a new one that names it.
**R5** Never type an id. Never store a counter.
**R6** When code owns a fact, its docstring says which tables.
**R7** Twice is a pattern — the second time a class of error is found by hand, it becomes a
check in `rx7.py`, with a selftest.
**R8** `check` is clean before the session closes. If it is not, that is the report.
**R9** Never branch on the words of any output — only its exit code.
**R10** Scope belongs to the project that owns the work; car-level facts belong to `00-CAR`;
anything that is a manual, a diagram or a datasheet belongs to `01-REFERENCE`.
**R11 You cannot see the car.** Every wire table, cavity map, clearance and pin letter here
was written by something that has never looked at the vehicle. A measured number always beats
your reasoning: where they disagree the row is wrong. Never conclude anything about a physical
part from a description, a photograph or a datasheet nobody has confirmed is the part in the
box — say what to measure, as a block. A dimension, resistance, pin letter or wire length that
has not been measured carries `confirm` in its note until it has.
**R12** A gate holds references, never prose. Work is taken from READY, never from file order.
If READY is empty, that is the report.

---

## 6 · Runs

Every run is one playbook: **plan** (§3 small work from READY, blocks for the rest), **apply**
(his answers), **source**, **build**, **review**, **complete**, **service**, **new** (a project),
**parts** (a parts round). `rx7.py playbook <name>` prints it; read it before step 1. Planning is
open in every project at every phase (D-398). Every run starts with §0 and ends the same way:
`check` clean, `rx7.py diagrams` if a harness table changed, a `log` row, commits and a push,
and the §8 report.

**Runs from the app** start you headless with a prompt naming one playbook and one project
(D-406, D-413); the prompt carries his answers and the pull is done. It is the same run under
every rule here, and its §8 report is what the app shows him. A run requested from the phone
is an inbox row `kind=run`: do that run, then delete the row. Explain, Discuss and the app's
chat start you read-only: answer from the record, never write, never commit.

**Commit and push (D-401).** Small commits, one change each, each leaving `check` clean.
Subject: what changed, ending with the decision ids (`Luxury: every lamp to LED (D-397)`);
body: why, and the work ids and blocks it touches. Straight to `master`, then `git push`; no
branches or pull requests unless Camden asks; never force-push, never rewrite pushed history,
never `--no-verify`. The hook refusing is rc 1: fix the data and commit again. A refused push
(the phone committed meanwhile) is `git pull --rebase` and push again; a failed push (network)
goes in the report and is pushed next run. Never amend, squash or revert the app's own
`Camden answered …` commits.

---

## 7 · Batch

Every extra call re-reads your whole context, so calls are the cost, not rows. One Bash call
carries every `get`/`sql`/`set`/`add`/`del` of a step; one `sql … where id in (…)` beats
several `get`s; a decision body and the rows it moves go in one call; one `check` at the end
of the step, not after every write. Never re-derive what a row or a decision settles, and
never restate the record to him — report the diff. One search per unknown fact, then a block.
A whole-file write only for a new file or a rewrite he named.

---

## 8 · Reporting — the only time you speak

Once per run, when it is finished or blocks have stopped all remaining progress. Ten lines or
fewer, no explanations, nothing he can read in the app:

```
DID        what got done, by work id
DECIDED    D-### one line each
BLOCKED    01.## (project.number) and the one-word ask
CHANGED    tables and rows touched
RECORD     valid / N problems
PUSHED     the commits, short hash and subject each, or why the push failed
NEXT       what runs when the blocks are answered
```

Then stop. He answers in the app and says continue, or presses Apply.

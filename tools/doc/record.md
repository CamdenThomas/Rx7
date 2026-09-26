# The record, in full (was CLAUDE.md §1)

**There are no pages (D-405).** Blocks, his answers, parts picks, the TODO lists and every
decision live in the record, and **the Rx7 app** (`02-APP/app`, a desktop app and an Android
app) is how he reads and answers them. Do not write a Markdown page for him to read or to type
in: not a TODO, not an index, not a summary, not a spec sheet. What was `BLOCKS.md`,
`PICKS.md`, `DECISIONS.md` and each `TODO.md` is now a screen in the app, computed from the
record every time it is shown. The app keeps no fact of its own, reads the record only through
`rx7.py export` (JSON), and writes only his answers, only through `rx7.py answer` (or, on the
phone, the same function). Nothing in it gates a commit.

**The Manual (D-417)** is the app's view of `00-CAR` as the car is now. `rx7.py export`
computes it (`manual`). It shows only backed facts: a row still saying `confirm` in a shown
cell, an `unverified` spec, or a spec or interval whose `applies` is `other-car` is held back
and listed with the reason; a part Camden has confirmed on the car (`parts.checked`, dated by
`rx7.py apply` from his 'yes, as described') is shown whatever its note says. `replaced` and
`not-fitted` rows are not facts about the car now, and are neither shown nor listed. So an
unchecked value keeps its `confirm` (R11), and a factory figure for a part that has gone is
marked `applies=replaced`, never deleted. A part's fitted date is read from the `service`
visit whose `fitted` names it, and the odometer is read from the newest `drives` or `service`
reading. Neither is ever typed.

**Files that stay files.** `CLAUDE.md`. `02-APP/README.md`, where the app's design is
pitched, at his request. Code and drawings with the READMEs that belong to them: the
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
`|`). His answer arrives in `inbox`; `rx7.py apply` sets the wordless ones (`work.result`
holds what he said; `work.settles` names the rows a choice flips, or the PT ids in the item
do), and the build playbook files the rest. The two tracks and the car coming apart once are
`rx7.py doc work`.

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

## The tool

```
rx7.py status [-p AREA] [--all]          where everything stands (brief by default)
rx7.py check [-p AREA]                   validate (rc 1 if the record contradicts itself)
rx7.py tables AREA                       every declared table, row counts, purpose
rx7.py get AREA TABLE KEY [COL ...]      one row; AREA may be - for a D- or block id
rx7.py set AREA TABLE KEY col=val ...    change an existing row   (col=@file, col=- stdin)
rx7.py add AREA TABLE col=val ...        add a row
rx7.py del AREA TABLE KEY                delete a row (blocks: --replaced-by; inbox: words saved)
rx7.py sql AREA "select ..."             query one area, or every area with AREA -
rx7.py find TEXT [-p AREA] [--word] [--limit N]   search every cell, with snippets
rx7.py new AREA "title" [col=val ...]    reserve the next D- (body=@file writes its text)
rx7.py block -p AREA title= ask= why= options= recommend= stops=   raise a block (§4)
rx7.py blocks [--answered]               open blocks; --answered: those with an answer waiting
rx7.py inbox [-p AREA]                   his answers waiting to be applied, his words in full
rx7.py apply [-p AREA]                   set the answers with one right answer; name the rest
rx7.py answer AREA TARGET --device D ... save one of his answers (the app calls this)
rx7.py export --out F | --stdout         everything the app shows, as JSON
rx7.py diagrams                          regenerate each harness leg's pin ladder (A) and route map (B)
rx7.py picks [-p AREA]                   where every parts pick stands
rx7.py cites [--table T]                 advisory: prose cites that no longer resolve, grouped
rx7.py selftest [-v]                     the tool's own tests (in memory and a scratch folder)
rx7.py log AREA KIND "what" [ref ...]    one log row (KIND = the area's log.workflow enum)
rx7.py playbook NAME · rx7.py doc TOPIC  print one playbook, one description
```

## Gates and READY

`work.gate` holds **references, and nothing else** — prose belongs in `note`. All of them
must be met before the row can start; an empty gate is met. They resolve across the whole
tree, so one area can wait on another:

| Reference         | Met when                                                                                                 |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| `D-274`           | that decision is standing or inherited                                                                   |
| `01.07`           | that block is gone from `blocks` and a decision names it in `closes` (its own area's, for ids after 2026-09-25) |
| `A5` · `F-012`    | that work row is done or dropped, in this area                                                           |
| `03-luxury:F-012` | the same, in another area — **always qualify across areas**, because work ids are only unique within one |
| `phase:SOURCING`  | this area is at that phase or past it                                                                    |

**READY** is every open row whose gate is met. `status` prints every READY agent row and,
with `--all`, **BLOCKED** with what holds each row, so answering one block visibly moves
several rows across on the next run. The plan playbook takes its work from READY and nowhere
else.

`check` refuses a reference that resolves to nothing, an unqualified work id two areas
could answer, a dependency ring, a gate on a superseded decision, and an area that has gated
every one of its own rows on its own rows or its own phase — that last one cannot be true,
and it is the failure that hides: a walled-off queue and a finished project look identical,
because the planner says "nothing to do" in both cases. An area whose work all waits on a
**block** or on **another area** is a real state, not a contradiction: that is exit code 2,
and it refuses nothing.

`selftest` checks the resolver, the checker, the id deriver and the writer of his answers on
a scratch fixture. A resolver that wrongly calls a gate met sends the planner at work that is
not ready; one that wrongly calls it unmet stops the project with no error printed anywhere.
A writer that drops a character loses his words. All are silent, so all get tests (R7).

`set`, `add` and `del` refuse a column that `_schema.csv` does not declare, and a value that
is not its type, not in its enum, empty when required, or a reference to no row. To add a
fact that has no column, add the column to `_schema.csv` first — that is a small decision
(§3) and it is how the design grows.

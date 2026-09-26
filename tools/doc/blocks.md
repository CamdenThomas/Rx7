# Blocks, in full (was CLAUDE.md §4)

A block is **one row in its project's `blocks` table**, and only what is still open is
there. The app shows each one on its own screen, with every option as a button. A block has
exactly these fields, and `check` refuses one missing any:

```
id         01.07                        issued by rx7.py block, never typed
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
options=@opts.txt recommend=… stops=…`). Long fields go through `@file`. Never raise a block
that asks him to weigh a list the agent has not produced yet: do the research row first.

**Block ids are `<project>.<number>`** (D-356): `01.12` is the twelfth block raised for
`02-PROJECTS/01-electrical`, `03.07` the seventh for `03-luxury`. The prefix is the project
directory's two-digit number; `00-CAR`, `01-REFERENCE`, `02-APP` and `00-verify` use `CAR`,
`REF`, `APP` and `VER`, because they are not numbered projects. Never `BLK-`: this car's
factory diagrams already use `B-12` and `D-01` as component codes, and an id family must never
share a namespace with the subject matter. And because a bare `13.80` in prose is a voltage, a
block id is only recognised as structure — a `blocks` key, `closes`, a gate. In prose write it
as `block 01.07` or in backticks. The renumberings are `rx7.py doc ids`.

**The clarity bar.** A block must be answerable from its screen alone, with no design in
front of him — the same three-isolated-workers standard as everything else. If he answers
"unclear — <what is missing>", that is a defect in the block: sharpen it, do not rule it.

**His answers.** He answers in the app: an option (its letter), "follow the
recommendation", words, or both — and a Discuss chat's key points ride along in `context`.
Each answer is a row in the project's `inbox`, saved as its own file
`data/inbox/<target>~<device>.csv`, and it waits there until he presses Apply, the desktop
app's auto-apply starts the run (90 seconds after his last answer, D-413), or you next run.
An answer to a target he already answered carries the earlier choice and words in `context`
(R3). The same table carries his answers to parts picks (`kind=pick`: yes, no or question),
to his own work rows (`kind=work`: done, a value, a choice), and requests for a run from the
phone (`kind=run`, `kind=project`), and, in `00-CAR`, the Manual's Log drive and Set odo
(`kind=drive`: the choice is the odometer, target `drive-<when>` or `odo-<when>`). An answer
in the inbox is exit code **2**. It never refuses a commit.

**His notes are not answers (D-426).** A `kind=note` row in `00-CAR`'s inbox (target
`note-<when>`) is a note he made on words he selected in the Manual. Its `context` holds
`where:`, `page:` and `selected:`. It is a log he keeps while the Manual is being dialled in:
no run applies it or deletes it, `inbox` and `status` do not count it as waiting, and only he
removes one, from the Notes page. Read notes as leads when you work on the Manual, and act on
one only when he asks.

**Lifecycle.** You raise it → he answers in the app → `rx7.py inbox` shows his words → you
apply it through the record (the apply playbook) → the ruling becomes a decision whose
`closes` names the block → **you delete the block row and its inbox rows.** Before deleting,
confirm three things: the decision exists and is `standing`, its `closes` names the block,
and its body carries **his answer in his own words**. If any of those is missing, finish the
job instead of deleting; `rx7.py del` refuses a block no standing decision closes and an inbox
row whose words are saved nowhere. `check` refuses a block that a standing decision already
closes. Ids are never reused — `rx7.py block` derives the next number from the decisions and
the retired terms as well as the table, so a deleted 01.05 can never come back as something
else.

**A block that came back unclear is replaced, not ruled.** Raise the new, plainer block
first, carry his words into its **why** so nothing he typed is lost, then delete the old
block and his inbox row (`rx7.py del AREA blocks OLD --replaced-by NEW` retires the old id).
If his answer contained a question for you, answer it in the new block's why, then ask only
the part that actually needs him.

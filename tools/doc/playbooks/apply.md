# Playbook: apply his answers

1. `git pull --rebase`, then `rx7.py apply -p AREA` (the answers with one right answer — a
   tick, a value, a choice with no words, a drive — are set by the tool and their inbox
   rows deleted; rc 2 means some wait for you), then `rx7.py inbox`. Read every remaining
   answer before touching anything.
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
   e. Work rows gated on it: gate met → leave open for the plan playbook; the ruling did
   the work → `state=done`.
5. Delete each solved block's row and its inbox rows, but only after its decision exists,
   is `standing`, names it in `closes`, and carries his answer in his own words (§4). The
   tool refuses otherwise.
6. `check` everything; `log`.

**His picks** (`kind=pick`) are applied by the parts playbook, step 4; **his work rows with
words** by the build playbook; **his drives** by the service playbook.

**His saved places** (`kind=place`, D-520): `target` is the Design page's part (scene.json's
`id`), `choice` its place, six numbers (x y z mm, rx ry rz degrees, the car's frame). Find the
row that part names - `UNITS[...]["row"]` or `PMU["row"]` in `00-design/tools/export_glb.py`,
a `parts` or `modules` row of 01-electrical - `get` it, `set … place=<choice>`, then rebuild
the scene (`export_glb.py --only scene`) and delete the inbox row; a later save of the same
part replaces the earlier one (his newest wins, the old one is in git). A part whose row has no
`place` column yet (a device, a connector) gets the column (§3: a fact with no column) and the
export reads it the same way, in the same pass; a child board's place is in its parent's
frame, so it goes to the parent's row only if he moved the parent. A measured place (R11) always replaces a
saved one.

**An answer you do not fully understand is not a ruling.** "I don't understand the
question", "it sounds like…", or an answer to a question you did not ask means the block
was unclear: rewrite it plainer, leave it open, and rule nothing. Guessing his intent
here is the one way this system can put a wrong fact in the permanent record.

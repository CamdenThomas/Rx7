# CLAUDE.md — Rx7

*Rev 2026-09-08 (system v2) · owns: how any agent works in this tree. Rules only; the workflows are the skills in `.claude/skills/rx7-*/`; the tool is `tools/rx7.py`.*

**Start every session with `python tools/rx7.py status`.** It prints every project's phase, next ids, what waits on whom, the last log lines, the checks, and which workflow the triggers say should run. Read nothing else until a workflow tells you to.

## The record

Every project and the manual (`00-CAR`) is `data/*.csv` (facts — one row per thing, one home per fact, first column the key) + `templates/*.md` (prose, with `{{view}}` placeholders) → `python tools/rx7.py -p <project> build` → the documents, `VIEW.html` / `MANUAL.html` and the harness sheets. Rendered files carry a banner and are never edited by hand.

Questions, decisions, the work list and the log are data too: `data/questions.csv` + `data/questions/<id>.md` (Camden answers in the body under `**ANSWER:**`), `data/decisions.csv` + `data/decisions/<id>.md`, `data/work.csv`, `data/log.csv`, `data/project.csv` (the phase). `QUESTIONS.md`, `DECISIONS.md` and `LOG.md` are rendered from them. **Never type an id** — `rx7.py new Q|D` takes the next one from the registry and refuses a collision; `{{next_id:D}}` prints it in prose.

`build` refuses on any contradiction: duplicate or dangling `D-`/`Q-`/`C-` ids, a closed question with no closer, a retired term still in use, a phase whose gate is not met, and every project's own checks in `views.py`. Fix the data, never the check — unless the check is wrong, in which case fix the check and say so in the decision. `lint` warns about drift (duplicate paragraphs, typed numbers, bare superseded cites, Markdown in cells) and never refuses.

## The lifecycle

| Phase | Allowed workflows | Leaves when |
|---|---|---|
| PROPOSED | overview · plan | the goal is ruled and the first work list exists |
| PLANNING | plan · answers · criticize · clean · overview | every agent design item done · no open §1 question · no open Major finding · build clean → **design freeze** (a `D-`) |
| SOURCING | answers (§2 only) · clean | carts paid, parts counted |
| BUILDING | build · answers · clean · criticize | every step done, every measurement recorded, shakedown logged |
| COMPLETE | complete | folded into `00-CAR/systems/` and the archive; the project folder is gone |

`00-CAR` and `01-REFERENCE` are PERMANENT. The manual never cites a `D-` or `Q-`.

## Who does what

Camden: answers packets in place · runs the workflows · does the physical work and tells `/rx7-build` what happened · spends money · `git commit`. The agent: everything that is reading, writing, calculating, cross-checking or enumerating. If a workflow needs a call only Camden can make, it writes a packet (Ask · Why it matters · Options with consequences · Recommend · Blocks · one-word ask) and moves on — it never stops mid-run to ask in chat.

## Standing rules

**R1** `get` a row before changing it. **R2** A rendered document is correct top to bottom because its rows and prose are. **R3** One home per fact — if it can be computed, compute it (`{{cell}}`, `{{count}}`, a view). **R4** Scope belongs to the project that owns the work; car-level facts belong to `00-CAR`. **R5** Every template: one H1, a `*Rev · owns:*` line, a Contents line past 200 lines. **R6** When code owns a fact, its docstring says which tables. **R7** Cite a closed or superseded id with its closer: `Q-108 → D-278`. **R8** Generated files are never edited by hand. **R9** The build is clean before the session closes. **R10** Every project has the same skeleton (`tools/scaffold.py` makes it). **R11** Twice is a pattern — the second time a class of error is found by hand it becomes a check.

## Credit rules

One row, one call — `get` / `sql` / `find`, never a rendered document, to learn a fact. Never re-derive what a row or a decision settles. Never rewrite a file to change part of it. Never restate a document in chat — report the diff. Batch edits; one `build` at the end. One search per unknown fact; then a packet. A whole-file write only for a new file or a rewrite Camden names.

## Machines and paths

Desktop `crashs-pc`: `C:\Users\USER\Documents\Storage\Rx7`. Laptop: `C:\Users\Camden Thomas\Documents\Storage\Rx7`. Both are git clones; the CLI runs in whichever is in front of him. Set `PYTHONIOENCODING=utf-8` before any Python on Windows. Nothing is ever queued in the Claude Project — it holds one pointer doc and nothing else; work waits for the CLI.

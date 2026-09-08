# RX-7 — the master file system

*Rev 2026-09-08 (system v2) · owns: the structure of this tree and the conventions every folder follows. The agent's rules are [`CLAUDE.md`](CLAUDE.md); the workflows are `.claude/skills/rx7-*/`; how to run them from PyCharm is [`WORKFLOWS.md`](WORKFLOWS.md).*

Root for every RX-7 project. `00-CAR/` is the car's owner's and service manual — the permanent record every finished project folds into. `02-PROJECTS/` is what is being changed, one folder per project, each in one phase of one lifecycle. `01-REFERENCE/` is every source document. `99-ARCHIVE/` is how things came to be.

## Structure

```
Rx7\
├── CLAUDE.md                  <- the agent's rules: the record, the lifecycle, who does what, R1–R11
├── README.md                  <- you are here
├── WORKFLOWS.md               <- how Camden runs the workflows from PyCharm, and the triggers
├── .claude\skills\rx7-*\      <- THE WORKFLOWS: status · propose · plan · answers · criticize · clean · build · complete · log · overview · diff
├── .claude\settings.json      <- Claude Code hooks: check after every edit, triggers at session end
├── .githooks\pre-commit       <- the build must be clean and current before a commit (git config core.hooksPath .githooks)
├── .run\                      <- PyCharm run configurations: status, check, build, lint, triggers
├── tools\
│   ├── rx7.py                 <- THE tool: data + templates -> documents, registry, checks, lint, status, new, log
│   ├── rx7.cmd                <- the terminal launcher:  rx7 plan electrical-build
│   ├── scaffold.py            <- /rx7-propose builds a project from the standard skeleton
│   ├── complete.py            <- /rx7-complete folds a finished project into the manual and the archive
│   ├── answers.py             <- every packet Camden has answered
│   ├── triggers.py/.csv       <- which workflow the metrics say should run
│   └── hook_*.py              <- the Claude Code hooks
├── 00-CAR\                    <- THE MANUAL. data\ · templates\ · views.py · the chapters · MANUAL.html · systems\<system>\
├── 01-REFERENCE\              <- source documents, every one indexed in data/sources.csv
├── 02-PROJECTS\<project>\     <- the v2 skeleton (below)
└── 99-ARCHIVE\                <- superseded and completed work; never deleted; README indexes it
```

## A project's skeleton (R10)

```
<project>\
├── data\
│   ├── project.csv            <- name · kind · goal · phase · id ranges
│   ├── questions.csv + questions\<id>.md     <- the packets; Camden answers in the body under **ANSWER:**
│   ├── decisions.csv + decisions\<id>.md     <- the rulings, by system; superseded ones stay as history
│   ├── work.csv               <- the plan: every task, agent- or Camden-owned, state, gate
│   ├── log.csv                <- append-only; the banners and LOG.md render from it
│   ├── retired.csv            <- terms a ruling retired; the build refuses them
│   ├── findings.csv           <- /rx7-criticize's C- ids (once one has run)
│   └── *.csv                  <- THE RECORD of the design: one row per thing, one home per fact, first column = key
├── templates\*.md             <- the prose, with {{view}} placeholders where facts go
├── views.py                   <- derivations and checks (optional); GATES = {phase: fn} for phase gates
├── view.json                  <- which documents VIEW.html shows as tabs
├── reviews\CRITIQUE-*.md      <- immutable critique output
├── README.md · QUESTIONS.md · DECISIONS.md · LOG.md · VIEW.html      <- RENDERED
└── 01-DESIGN\ 02-SHOPPING\ 03-INSTALL\                                <- RENDERED
```

`python tools/rx7.py -p <project> build` checks the data and writes every rendered file; a refusal names the row. `python tools/rx7.py status` is the one-screen view of everything.

## Conventions

**One home per fact (R3).** A fact lives in one row; everywhere else it appears is a view — `{{table}}`, `{{cell:table|key|column}}`, `{{count}}`, `{{param}}`, `{{next_id}}` or a named view in `views.py`. If a number can be computed, computing it is the only correct way to state it.

**Permanent ids, never typed.** `D` decision · `Q` question · `C` critique finding · `K` known issue · `M` modification · `P` planned · `S` source · `SP` spec · `PR` procedure · `SV` service visit. `rx7.py new Q|D` takes the next number from the registry and refuses a collision; a closed or superseded id is cited with its closer (`Q-108 → D-278`). Each project has its own hundred: electrical 001–299, luxury 300–399, engine swap 400–499, the next project 500–599.

**Phases with gates.** PROPOSED → PLANNING → (design freeze, a ruling) → SOURCING → BUILDING → COMPLETE. `project.csv` says which; the build refuses a phase whose gate is not met.

**The manual holds what is, never why.** At completion a project splits three ways: as-built facts and drawings, and service pages, into `00-CAR/systems/<system>/`; every trace of process into `99-ARCHIVE/<date>_<project>/`. The manual never cites a `D-` or `Q-`.

**Generated files are never edited by hand (R8).** The banner is the tell.

## Git

The commit is Camden's. `.gitattributes` normalises line endings; `.gitignore` excludes built binaries and IDE state (`.run/` is shared on purpose). Install the hook once per clone: `git config core.hooksPath .githooks` — or `tools\rx7 setup`, which also checks that Claude Code and WireViz are installed.

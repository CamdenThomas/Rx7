# RX-7 — Master File System

*Rev 2026-08-31 · owns: the structure of this tree and the conventions every project under it follows. Project state is [`STATUS.md`](02-PROJECTS/electrical-pmu/STATUS.md); the agent's rules are [`ASSISTANT.md`](ASSISTANT.md).*

Root for every RX-7 project. Car-level facts live at the top and are reused by
every project underneath. Project folders are self-contained; `00-CAR` is
permanent.

## Structure

```
Rx7\
├── README.md                <- you are here. Structure and conventions
├── ASSISTANT.md             <- Claude's operating rules. Read every session
├── CLAUDE.md                <- pointer to ASSISTANT.md for Claude Code
├── 00-CAR\                  <- permanent. Survives every project
│   ├── README.md
│   ├── vehicle.md           <- identity, drivetrain, what is fitted today
│   ├── modifications.md     <- M-### done, P-### planned, service history
│   ├── known-issues.md      <- K-### faults and quirks
│   └── parts-history.md     <- what was replaced when
├── 01-REFERENCE\
│   ├── README.md
│   ├── factory-circuits\    <- the 1982 harness, decoded circuit by circuit
│   ├── PMU_info\            <- ECUMaster pinout
│   ├── photos\              <- T-018 harness photographs, by zone
│   └── Part Dates - Sheet1.pdf
├── 02-PROJECTS\
│   └── electrical-pmu\      <- ACTIVE. PMU, battery, harness, DCU/ICU —
│                               folders 01-DESIGN … 05-PROCESS (D-200);
│                               lighting & body is its deferred second pass (D-201)
└── 99-ARCHIVE\              <- superseded. Never deleted; README indexes it
```

## Projects

| Project | State | Start at |
|---|---|---|
| **[`electrical-pmu/`](02-PROJECTS/electrical-pmu/README.md)** | **Active.** PMU, battery, harness, sill node, DCU/ICU. Runs on **stock incandescent bulbs** | [`STATUS.md`](02-PROJECTS/electrical-pmu/STATUS.md) |

Lighting & body — LED conversion, custom tail lights, headlamp units, rust and
paint — was split out 2026-08 (D-123) and folded back in as **deferred scope**
of the electrical project 2026-08-31 (D-201): none of it is needed to finish
the car, and it starts only after the electrical rebuild is shaken down
(L-004). Its design lives in
[`01-DESIGN/TAIL-LIGHTS.md`](02-PROJECTS/electrical-pmu/01-DESIGN/TAIL-LIGHTS.md);
its money is BOM Wave 5; its tasks and open items sit in the project's
process files, marked deferred.

## The car

[`00-CAR/`](00-CAR/README.md) is the permanent record: what the car is, what has
been done to it, what is wrong with it. Every project cites it and none of them
own it. [`01-REFERENCE/`](01-REFERENCE/README.md) is the factory harness decoded
from the 1982 wiring diagram, frozen as [`OEM-RECORD.md`](01-REFERENCE/factory-circuits/OEM-RECORD.md), plus the PMU pinout
and the photo archive.

## Conventions — every project

**One owner per fact**, declared in each file's header line
(`*Rev YYYY-MM-DD · owns: …*`). If two files disagree, the owner wins.

**Current-state documents.** A file is correct top to bottom. Superseded
reasoning goes to a marked appendix or `99-ARCHIVE/`, never left above a
correction.

**Append-only decision logs.** `DECISIONS.md` in each project; reverse by a new
entry marking the old one `> SUPERSEDED BY …`.

**Permanent IDs, never reused.** `D` decision · `Q` question · `A` assumption ·
`V` verify · `T` Camden task · `K` known issue · `M` modification · `P` planned
modification · `I` improvement · `L` lighting decision · `F/H/X/Z` forward
work · `R` standing rule. Three digits; a closed one is cited as
`Q-038 → D-095`. The full key is
[`electrical-pmu/01-DESIGN/GLOSSARY.md`](02-PROJECTS/electrical-pmu/01-DESIGN/GLOSSARY.md).

**Generated files are never edited by hand.** Where a project keeps data in
CSVs (`electrical-pmu/02-HARNESS/data/`), the tables, diagrams and headers
downstream are regenerated from them.

**Links are relative Markdown links**, checked by
`electrical-pmu/05-PROCESS/tools/check.py`.

## Git

The tree is a git repository. Commit at the end of every session — the agent
cannot commit from the cloud, so this is Camden's step. `.gitignore` excludes
built binaries and IDE state; the two large PDFs under `01-REFERENCE/` are
candidates for Git LFS if the repository ever moves to a remote.

# RX-7 — Master File System

*Rev 2026-09-03 · owns: the structure of this tree and the conventions every project under it follows. The agent's rules are [`ASSISTANT.md`](ASSISTANT.md); the active project's state is its `QUESTIONS.md` §0.*

Root for every RX-7 project. Car-level facts live at the top and are reused by
every project underneath. Project folders are self-contained; `00-CAR` is
permanent and every finished project folds into it.

## Structure

```
Rx7\
├── README.md                <- you are here. Structure and conventions
├── ASSISTANT.md             <- Claude's operating rules. Read every session
├── CLAUDE.md                <- pointer + quick facts for any agent
├── tools\
│   └── rx7.py               <- THE tool: data/*.csv + templates/*.md -> documents + VIEW.html
├── 00-CAR\                  <- permanent. The car itself
│   ├── data\                <- specs, modifications, known issues, parts history (CSV)
│   ├── templates\           <- the prose around them
│   └── *.md                 <- rendered by the tool
├── 01-REFERENCE\            <- source documents, every one indexed in data/sources.csv
│   ├── factory-circuits\    <- the 1982 harness, decoded circuit by circuit
│   ├── PMU_info\            <- ECUMaster pinout, manual, CAD
│   ├── manuals\             <- workshop manual sections and other documents obtained
│   └── photos\
├── 02-PROJECTS\
│   ├── electrical-build\    <- ACTIVE. The harness: 01-DESIGN / 02-SHOPPING / 03-INSTALL
│   ├── luxury-package\      <- every future feature
│   └── engine-swap\         <- everything that changes with the engine
└── 99-ARCHIVE\              <- superseded. Never deleted; README indexes it
```

## A project's skeleton (R10)

```
<project>\
├── README.md          <- rendered: the map, the three steps, next IDs
├── DECISIONS.md       <- prose, by system, append-only: why it is the way it is
├── QUESTIONS.md       <- prose, easiest first: everything still open; §0 = finishing tasks
├── data\*.csv         <- THE RECORD. One row per thing, one home per fact, first column = key
├── templates\*.md     <- the prose of every rendered document, {{view}} lines where tables go
├── views.py           <- how facts derive from other facts, and the checks (optional)
├── view.json          <- which documents VIEW.html shows as tabs (optional)
├── VIEW.html          <- rendered: the three sub-plans side by side, searchable, every ID a link
└── 01-… 02-… 03-…     <- rendered documents, each with the banner
```

`python tools/rx7.py -p <project> build` checks the data and writes every
rendered file. A red check refuses the build. See `ASSISTANT.md` §1.

## Conventions — every project

**One home per fact (R3).** A fact lives in one row. Everywhere else it
appears is a view of that row — a pin's destinations, a housing's used count,
a cut-list label, a kit quantity, a total. If it can be computed, it is.

**Current-state documents (R2).** A rendered file is correct top to bottom
because its rows and prose are. Superseded reasoning goes to `99-ARCHIVE/`.

**Append-only decision logs.** `DECISIONS.md` in each project, grouped by
system; a decision is superseded by a newer one that names it.

**Permanent IDs, never reused.** `D` decision · `Q` question · `K` known
issue · `M` modification · `P` planned. Three digits; a closed one is cited as
`Q-100 → D-227`. Older prefixes (`V A T I L F/H/X/Z R`) belong to the archive.
Row keys inside `data/` (`L3-S1 4`, `F19`, `P042`, `S017`) are permanent too.

**Generated files are never edited by hand (R8).** The banner is the tell.

**Every source document is indexed** in `01-REFERENCE/data/sources.csv` the
session it lands, and every fact taken from one cites its `S-###`.

## Git

The tree is a git repository; the commit is Camden's step. `.gitattributes`
normalises line endings (the tree is edited from Windows and from a Linux
sandbox). `.gitignore` excludes built binaries and IDE state. The large PDFs
under `01-REFERENCE/` are candidates for Git LFS.

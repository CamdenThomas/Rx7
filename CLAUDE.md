# CLAUDE.md

*Rev 2026-09-03 · owns: nothing — this file exists so Claude Code and any agent that reads a root `CLAUDE.md` finds the real instructions.*

Read [`ASSISTANT.md`](ASSISTANT.md) first, every session. It is the operating
manual: the data tool, credit rules, edit process, delegation, decision
handling, verification, project close, session close, and the standing rules
R1–R11.

## The record is data, rendered (D-233, 2026-09-03)

Every project is `data/*.csv` (facts, one home each) + `templates/*.md`
(prose) → `python tools/rx7.py -p <project> build` → the documents and
`VIEW.html`. Rendered files carry a banner and are never edited by hand.
`DECISIONS.md` and `QUESTIONS.md` stay prose.

| Project | Owns | State |
|---|---|---|
| [`02-PROJECTS/electrical-build/`](02-PROJECTS/electrical-build/) | The harness — design, shopping, install | **Active.** Data-driven since 2026-09-03 |
| [`02-PROJECTS/luxury-package/`](02-PROJECTS/luxury-package/) | Every future feature — ICU, DCU, cluster, comfort, mirrors, windows, lighting | Prose only; gets `data/` when it starts |
| [`02-PROJECTS/engine-swap/`](02-PROJECTS/engine-swap/) | Everything that changes with the engine | Prose only |
| [`00-CAR/`](00-CAR/) | The car itself — identity, specs, modifications, faults, parts | Permanent; every project folds into it |
| [`01-REFERENCE/`](01-REFERENCE/) | Source documents, indexed in `data/sources.csv` | Permanent |

## Where to start

1. [`02-PROJECTS/electrical-build/QUESTIONS.md`](02-PROJECTS/electrical-build/QUESTIONS.md) — §0 is the finishing task list; §1 is what must be answered before the carts are paid.
2. `python tools/rx7.py -p electrical-build tables` — then `get` / `find` / `sql` for the rows the task touches.
3. [`DECISIONS.md`](02-PROJECTS/electrical-build/DECISIONS.md) `**Latest:**` line only, unless the task is a ruling.

## Quick facts an agent needs before touching anything

- **Never read a rendered document to learn a fact.** `DESIGN.md`, `WIRE-TABLES.md`, `PMU-CONFIG-SHEET.md`, `SHOPPING-LIST.md`, `INSTALL.md`, `GLOSSARY.md` and the project `README.md` are outputs of `build`. The rows are in `data/`; the prose is in `templates/`; the derivations are in `views.py`.
- **`build` refuses on a contradiction.** Fix the data, never the check — unless the check is wrong, in which case fix the check and log why.
- **Numbering:** electrical decisions continue from **D-234**, luxury from D-306. Electrical questions from **Q-105**, luxury from Q-301. IDs are permanent; a closed question is cited with its closer.
- **Nothing has been bought, cut or crimped.** Four carts wait for payment; `QUESTIONS.md` §1a lists what blocks paying them.
- The user is Camden. Physical work, spending, sign-off and `git commit` are his; everything that is reading, writing, calculating or cross-checking is the agent's.
- Line endings: `.gitattributes` normalises to LF in the repository. The tool writes LF; Windows editors are fine with it.

## Known stale artefacts

- The attached Claude Project (`rx7/…`) holds a flattened snapshot of the dissolved `electrical-pmu` tree from 2026-08-31 / 09-01. Its `SOURCE-OF-TRUTH.md` says so. **Do not answer from it — read this tree.**
- `99-ARCHIVE/` is history. Nothing in it is current; it stays for the reasoning.

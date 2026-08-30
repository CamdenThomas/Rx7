# CLAUDE.md

*Rev 2026-08-30 · owns: nothing — this file exists so Claude Code and any agent that reads a root `CLAUDE.md` finds the real instructions.*

Read [`ASSISTANT.md`](ASSISTANT.md) first, every session. It is the operating
manual: session opening, credit rules, edit process, delegation, decision
handling, verification, session close, and the standing rules R1–R8.

Then read [`02-PROJECTS/electrical-pmu/STATUS.md`](02-PROJECTS/electrical-pmu/STATUS.md)
for where the project is, and only the file the task touches.

Quick facts an agent needs before touching anything:

- Pin, cavity and housing data live in `02-PROJECTS/electrical-pmu/02-HARNESS/data/*.csv`.
  Everything generated from them ([`PIN-MAP.md`](02-PROJECTS/electrical-pmu/02-HARNESS/PIN-MAP.md), [`CAVITY-STATE.md`](02-PROJECTS/electrical-pmu/02-HARNESS/CAVITY-STATE.md),
  `channels.h`, the SVGs, the `<!-- gen:… -->` blocks) is rewritten by
  `python 02-PROJECTS/electrical-pmu/07-PROCESS/tools/gen.py`. Never edit those by hand.
- `python 02-PROJECTS/electrical-pmu/07-PROCESS/tools/check.py` must be clean at session close.
- `DECISIONS.md` is append-only. IDs are permanent. A closed ID is cited as `Q-038 → D-095`.
- The user is Camden. Physical work, spending and sign-off are his; everything
  that is reading, writing, calculating or cross-checking is the agent's.

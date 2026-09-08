---
name: rx7-complete
description: Fold a finished Rx7 project into the owner's manual three ways — as-built facts and drawings, service pages, and the process into the archive — then remove the project. /rx7-complete <project> --system <name>.
---

# /rx7-complete `<project> --system <name>`

**Gate** (the script enforces it): phase BUILDING, every `steps.csv` row done, no open question (close or move each), build clean. Run `/rx7-clean <project>` first.

1. `python tools/complete.py <project> --system <name> --dry`. Read the plan and the **STRIP** list — every line in the as-built templates and tables that carries a `D-`/`Q-`/`C-` cite or a "why" sentence. The manual keeps *what is*, never *how it was decided*.
2. **Rewrite before folding.** For each STRIP line, in the project (not the manual): a cite of a decision becomes the fact the decision produced, stated plainly; a "why" sentence is deleted from the template (it lives in the archive) or, if it is a service fact ("keep the tunnel pair away from the coil leads"), rewritten as an instruction. Re-run `--dry` until STRIP is empty or every remaining line is one you have judged a service instruction.
3. Run without `--dry`. It copies the as-built tables, `views.py`, drawings and config templates to `00-CAR/systems/<name>/`, writes a `SERVICE.md` skeleton and a `README.md`, moves every process file to `99-ARCHIVE/<date>_<project>/` with a README, and removes the project folder.
4. **Write the service pages** in `00-CAR/systems/<name>/templates/SERVICE.md` from the archived install plan's tests, adjustments and recovery sections — as instructions, present tense, with pass values; add `intervals` rows for anything with a check interval; each recovery path becomes a `procedures` row + body in `00-CAR`.
5. **The 00-CAR rows** the script lists: `as_fitted` (state, since, chapter), `planned` → `mods` (`P-` becomes a new `M-`; delete the `P-` row), `parts_history` statuses, `specs` for every commissioning number (cited to the step that measured it), `vehicle` rows that changed.
6. Sibling projects that read this project live: `db.other("<name>")` now resolves to `00-CAR/systems/<name>` — run `python tools/rx7.py -a build` and fix any boundary check that moved.
7. `python tools/rx7.py -p 00-CAR log complete "<project> folded as <name>"`; `/rx7-diff`. The manual is clean the moment the build is.

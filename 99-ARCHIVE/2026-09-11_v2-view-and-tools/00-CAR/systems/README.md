# systems/ — one chapter per completed project

*Rev 2026-09-08 · owns: the rule for this folder. Empty until the first project completes.*

`/rx7-complete <project>` splits a finished project three ways: the **as-built facts** (its tables, its rendered sheets, its configuration as loaded) and its **service pages** (tests, adjustments, recovery, intervals) land here as `systems/<system>/` — a folder with the same skeleton as a project (`data/`, `templates/`, `views.py`, rendered chapters) but frozen to what is physically in the car. Everything about *how it got there* — decisions, questions, work lists, logs, critiques, shopping — goes to `../../99-ARCHIVE/<date>_<project>/`.

A system chapter never cites a `D-` or `Q-` id. Its tables keep their permanent row keys (a cavity is `L3-S1 7` here too), so the manual's other chapters and any later project can read them live with `db.other("<system>")`.

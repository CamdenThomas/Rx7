---
name: rx7-clean
description: Make an Rx7 project's prose tell exactly what its data says — run lint, convert typed facts to placeholders, fix stale sentences, cite closed ids with their closers, values-not-sentences in cells. No design changes. /rx7-clean [project|all].
---

# /rx7-clean `[project|all]`

**Gate:** none. **No design change** — if a fix would change what is built, bought or wired, it becomes a packet instead.

1. **The script half.** `python tools/rx7.py -p <project> check` then `lint`. Every warning is a work item for this run: duplicate paragraphs · typed next-ids · superseded ids cited bare · dangling ids · Markdown in data cells · stale `Rev` lines · dead links · missing Contents lines · answered-but-unapplied packets (those are `/rx7-answers`'s — report, do not apply).
2. **The agent half — template by template.** For each `templates/*.md`, read it against its rows: one `sql` per section, never the rendered file. Fix prose that says something the data does not, with the smallest edit. Where a sentence states a number or an id that has a row, replace the literal with `{{cell:table|key|column}}`, `{{count:…}}`, `{{param:…}}` or `{{next_id:…}}` so it cannot drift again. Cite closed and superseded ids as `Q-108 → D-278` (R7). Update the template's `*Rev*` date only if its prose actually changed.
3. **Cells.** In the manual (`00-CAR`) and any table the manual will inherit, a cell is a value: ISO dates, numbers without formatting, statuses from the vocabulary, no bold, commentary in `note`. Fix cells; leave long narrative statuses in `issues` if the narrative is the fact, but move dates and numbers out of them.
4. **Duplicates.** A paragraph that appears in two files is either a view that has not been written (write it in `views.py`, call it from both) or history that belongs in the archive (move it). Never leave both.
5. `python tools/rx7.py -a build` — must be clean; `lint` again — report what remains and why.
6. `python tools/rx7.py -p <project> log clean "<what changed, one line>"`; then `/rx7-diff`.

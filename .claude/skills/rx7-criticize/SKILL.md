---
name: rx7-criticize
description: Tear an Rx7 project's design, shopping list and install plan apart from three isolated seats and one auditor — logic holes, magic numbers, parts that fit nothing, steps that assume what the design never fixed. Changes nothing; writes findings with permanent C- ids. /rx7-criticize <project> [--scope design|shopping|install|all].
---

# /rx7-criticize `<project> [--scope …]`

**Gate:** phase ≥ PLANNING. **This workflow changes nothing** — no row, no template, no packet. Its only output is `reviews/CRITIQUE-<date>.md` and a log row. Findings enter the plan through the next `/rx7-plan`, which turns each into a work item or a packet citing the `C-` id.

1. `python tools/rx7.py -p <project> build` first — a critique of a tree that does not build is noise. Record the head commit.
2. **Four reviewers, each in its own subagent, each given only its section** (this is the three-isolated-workers test made into a process):
   - **the design reviewer** — reads `01-DESIGN/*` and may query the data. Hunts: a rule with no owner, two rows that claim the same thing, a limit with no basis, a derived number typed by hand, a decision the prose forgot, a boundary a sibling project reads that this design silently changed.
   - **the buyer** — reads `02-SHOPPING/*` only. Hunts: a line with no quantity or a quantity below the design's count (the gap view), a part number never verified, a store line that mates with nothing, an "any" that should be a spec, a tool missing for a step the plan names.
   - **the builder** — reads `03-INSTALL/*` only. Hunts: a step that assumes a fact the design never fixed, a measurement with no box, a test with no pass value, an order that traps a later step, a safety step missing where power or fuel is touched, a step nobody could follow without the designer in the room.
   - **the auditor** — reads all three plus `DECISIONS.md` and `QUESTIONS.md`. Hunts contradictions *between* the sections and against the rulings; checks that every open packet passes the clarity test (readable alone: ask, why, options with consequences, recommend, blocks, one-word ask).
   Each reviewer returns findings as: **what** (one sentence) · **where** (file / row) · **why it matters** · **severity** Blocker (stops the build or endangers the car) / Major (wrong part, wrong wire, wrong order) / Minor (drift, unclear) / Nit · **what would settle it** (a row, a packet, a measurement).
3. **Merge and number.** Deduplicate; for each finding `python tools/rx7.py -p <project> ids next C` and write `reviews/CRITIQUE-<date>.md`: a header with the scope, the commit and the four seats; a table (id · severity · where · what · settles-by); then the findings in full, Blockers first. Add each `C-` id to `data/findings.csv` (`id,date,severity,where,what,settles_by,state`) so the registry owns the ids and the phase gate can read "no open Major".
4. `python tools/rx7.py -p <project> log criticize "<n findings: b/m/m/n>" <C-ids>`. Nothing else is written.
5. **Report:** the counts by severity and the three worst findings, one line each. Then stop — Camden decides whether `/rx7-plan` acts on them now.

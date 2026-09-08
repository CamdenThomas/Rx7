---
name: rx7-plan
description: The self-driving planning loop for an Rx7 project — harvest answers, take the next agent-owned work item, do it through data and templates, turn every needed call into a packet, build, log, repeat until nothing agent-side is left. /rx7-plan <project> [--cycles N].
---

# /rx7-plan `<project> [--cycles N]`

**Gate:** phase PROPOSED or PLANNING. Read `CLAUDE.md`; run `/rx7-status`. Camden is prompted **once** — at the start. Never stop mid-run to ask; a needed call becomes a packet.

## One cycle

1. **Harvest.** `python tools/answers.py`. If any packet of this project is answered, run `/rx7-answers <project>` in full before anything else (an answer late in the list can change how an early work item is done).
2. **Pick.** `python tools/rx7.py -p <project> sql "select id, block, item, gate, note from work where owner='agent' and state='open'"` — take the first whose gate is met (a gate names a work id, a question id, or a phase). None → stop and report.
3. **Do it, through the record only.** Facts → `set` / `add` rows (R1: `get` first). Prose → the smallest template edit, pointing at rows with `{{cell}}` / `{{count}}` rather than copying values. Derivations and checks → `views.py` (R6, R11). A fact that has no row yet gets its row — this is how the design grows. Anything that needs Camden — a choice that changes wiring, cost, schedule or forecloses an option; a measurement; a purchase — becomes a packet (`new Q`, body per `/rx7-propose` step 3) plus a Camden-owned work row gated on it; the item stays open with `note=waits on Q-…`. A fact that must be verified (part number, price, mating, geometry) is flagged in the row's note as *confirm* and gets a packet in section 2.
4. **Build.** `python tools/rx7.py -p <project> build`. A refusal is fixed in the data (or becomes a packet if the fix is Camden's) — never worked around; a check that is wrong is fixed and the reason logged.
5. **Log and mark.** `set work <id> state=done`; `python tools/rx7.py -p <project> log plan "<one line>" <ids>`.

## Stop conditions

No open agent item whose gate is met · `--cycles N` reached (default 6) · a refusal that only Camden can clear · the credit budget he named. Then the **phase gate**: if every agent design item is done, no §1 question is open and the latest `reviews/CRITIQUE-*.md` has no open Major, write the design-freeze packet (`new Q "Freeze the design?" section=1 ask=yes/no`) — the freeze itself is his ruling, and `/rx7-answers` moves the phase to SOURCING.

## Report — ten lines

`DONE` work ids · `OPENED` packets that now want one word (id + the ask) · `CHANGED` rows/templates · `CARTS` what left or joined · `BLOCKED` items and what clears them · `NEXT` the workflow to run. Never restate a packet he can read.

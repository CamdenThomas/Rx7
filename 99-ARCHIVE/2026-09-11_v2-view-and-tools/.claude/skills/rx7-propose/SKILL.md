---
name: rx7-propose
description: Start a new Rx7 project from a one-sentence goal — scaffold the folder, write the opening question set and the first work list. /rx7-propose <name> --kind <kind> "<goal>".
---

# /rx7-propose `<name> --kind electrical|electronics|mechanical|body|software "<goal>"`

**Gate:** the name is not taken. Read `CLAUDE.md`; run `/rx7-status`.

1. **Scaffold.** `python tools/scaffold.py <name> --kind <kind> "<goal>"` — the v2 skeleton, a fresh id range, `project.csv` at phase PROPOSED, the goal as the first draft decision, work items A1 (agent) and A2 (Camden). Then `python tools/rx7.py -p <name> build` must be clean before anything else.
2. **Read the boundary, not the tree.** `python tools/rx7.py -p 00-CAR tables`, then the `vehicle`, `as_fitted`, `issues` and `planned` rows that touch this goal (`find`, `sql`). For every sibling project: its `project.csv` goal and any table whose name suggests a hand-over (`handover`, `provisions`, `cavities` with RESERVED state). Do not read rendered documents.
3. **Write the opening question set** — every decision the goal implies that only Camden can make, easiest first, each with `python tools/rx7.py -p <name> new Q "<title>" section=1 why="…" blocks="…"` and then the body filled in `data/questions/<id>.md`: **Ask** (one sentence) · **Why it matters** (what changes with the answer) · **Options** with the consequence of each (cost, time, what it forecloses) · **Recommend** one, with *flip it if* · **Blocks** (what cannot proceed until answered) · a one-word ask. The test: Camden understands the whole question from the packet alone, without the design in front of him.
4. **Write the first work list** in `data/work.csv` — agent items for research, the boundary tables this project must read live from siblings (`db.other()` in a `views.py`), the seams it creates; Camden items only for physical looks and money.
5. **Seed the data.** Any fact already known about the car for this scope is a row (cited to `SP-`/`S-`/`K-`/`M-` ids), never prose.
6. `build`; `python tools/rx7.py -p <name> log propose "<one line>" <ids>`; then the diff (`/rx7-diff`).

The project stays PROPOSED until Camden answers the opening packets and `/rx7-plan` rules the goal.

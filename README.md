# Rx7 — v3

The car's record. One data format, one instruction file, one page to answer on.

```
python tools/rx7.py status
```

- **`CLAUDE.md`** — the entire instruction set for any agent working here. No skills,
  no slash commands, no second document.
- **`BLOCKS.md`** — the only file Camden writes in. Every decision that needs him is a
  block; he types the answer after `**SOLVE:**`.
- **`tools/rx7.py`** — the only tool. Stdlib Python. `check` is the gate: exit 1 means
  the record contradicts itself, and it is the only thing that can stop a commit.

Areas: `00-CAR` (the car as it stands), `01-REFERENCE` (manuals, factory circuits,
photos), `02-PROJECTS/*` (work in flight), `99-ARCHIVE` (finished process, and the v2
view layer this version replaced).

There are **no generated documents** in this tree — no templates, no rendered Markdown,
no HTML. The visual layer is a separate, later concern. The previous system, with all of
its rendered documents intact, is still at `..\Rx7`; read it for history, never write
to it.

One-time per clone: `git config core.hooksPath .githooks`

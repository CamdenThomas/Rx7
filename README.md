# Rx7

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
  `status` prints READY and BLOCKED per area — what can be started now, and what each
  waiting row waits on. `selftest` tests the gate resolver itself.
- **`.github/workflows/rx7.yml`** — CI backstop, `selftest` + `check`, for the clone
  where the hook was never installed. It deliberately does not care whether
  `DECISIONS.md` is current.

Areas: `00-CAR` (the car as it stands), `01-REFERENCE` (manuals, factory circuits,
photos), `02-PROJECTS/*` (work in flight), `99-ARCHIVE` (finished process, and the v2
view layer this version replaced).

There are **two kinds of generated document**: `DECISIONS.md` (`rx7.py decisions`) and each project's `TODO.md`, its working list (`rx7.py todo`, D-373) — no templates,
no other rendered Markdown, no HTML. The visual layer is a separate, later concern. The
previous system (v2) is gone from disk except for `99-ARCHIVE/2026-09-11_v2-view-and-tools/`;
read that for history, never write to it.

One-time per clone: `git config core.hooksPath .githooks`

# Rx7

The record of one 1982 Mazda RX-7: every fact about the car and every project on it, as
self-describing CSV, checked by one tool, read and answered through one app.

```
python tools/rx7.py status
```

- **`CLAUDE.md`** — the entire instruction set for any agent working here. No skills,
  no slash commands, no second document.
- **`tools/rx7.py`** — the only tool. Stdlib Python. `check` is the gate: exit 1 means
  the record contradicts itself, and it is the only thing that can stop a commit.
  `status` prints READY and BLOCKED per area — what can be started now, and what each
  waiting row waits on. `export` is the whole record as JSON for the app; `answer` is the
  one writer of Camden's answers. `selftest` tests the gate resolver and that writer.
- **The Rx7 app** (`02-PROJECTS/10-gui/app/`) — a desktop app for the Fedora PC and an
  Android app for the phone, one design. It shows the car, the projects, the open blocks,
  parts picks, work lists and every decision, and it is where Camden answers. It keeps no
  fact of its own. Its README says how to build and install it.
- **`.github/workflows/rx7.yml`** — CI backstop, `selftest` + `check`, for the clone
  where the hook was never installed.

Areas: `00-CAR` (the car as it stands), `01-REFERENCE` (manuals, factory circuits,
photos), `02-PROJECTS/*` (work in flight), `99-ARCHIVE` (finished process, and the v2
view layer this version replaced).

There are no Markdown pages to read or to write in (D-405): blocks, answers, picks, the
TODO lists and every decision's text live in the record, and the app shows them. The only
generated files are the harness-leg drawings (`rx7.py diagrams`, D-385).

One-time per clone: `git config core.hooksPath .githooks`

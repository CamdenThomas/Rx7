# WORKFLOWS — how to run the Rx7 system from PyCharm

*Rev 2026-09-08 · owns: the operator's guide — what each workflow is for, how to start it in one keystroke from PyCharm, what runs automatically, and what still needs a word from you. The rules the agent follows are [`CLAUDE.md`](CLAUDE.md); the workflows themselves are `.claude/skills/rx7-*/SKILL.md`.*

## Contents

0 · One-time setup · 1 · The day-to-day loop · 2 · The workflows, one line each · 3 · Starting a workflow from PyCharm · 4 · What runs by itself — the triggers · 5 · Answering questions · 6 · Two machines · 7 · If something is wrong

---

## 0 · One-time setup (each clone, five minutes)

1. **Claude Code in the terminal.** `npm install -g @anthropic-ai/claude-code`, then `claude` once in the repo folder to sign in. The eleven `/rx7-*` commands appear automatically — they are the `.claude/skills/` folders in the repo, so every clone has the same set.
2. **The JetBrains plugin** (Settings → Plugins → *Claude Code [Beta]*). It opens Claude Code in a PyCharm tool window; typing `/rx7-plan electrical-build` there is the same as in the terminal, with the file you are editing in context. This is the "inside PyCharm" path.
3. **The hook and the tools:** in the PyCharm terminal, `tools\rx7 setup`. It installs the pre-commit hook (`git config core.hooksPath .githooks`) and tells you if Claude Code, WireViz or Graphviz are missing.
4. **Run configurations** are already in `.run/` — PyCharm shows them in the Run dropdown under the *rx7* folder: `rx7 status`, `rx7 check (all)`, `rx7 build (all)`, `rx7 lint …`, `rx7 triggers`, `rx7 answered packets`. Pin `rx7 status` to the toolbar.
5. **Optional, recommended — File Watchers** (Settings → Tools → File Watchers, *bundled plugin*): one watcher on `data/*.csv` and `templates/*.md`, program `python`, arguments `tools/rx7.py -p $FileParentDir$/.. build` (or simply `-a build`), working directory `$ProjectFileDir$`, *auto-save edited files* on. With it, the rendered documents and `MANUAL.html` regenerate every time you save a CSV or template — you never run `build` by hand. Uncheck *immediate file synchronization* so it runs once per save, not per keystroke.

## 1 · The day-to-day loop

Everything runs in this order; the tool tells you where you are.

```
rx7 status                      ← where everything stands; what the triggers say to run next
(answer packets in PyCharm)     ← data/questions/Q-xxx.md, under **ANSWER:**
rx7 answers                     ← every answer becomes a ruling, applied everywhere, built
rx7 plan electrical-build       ← the agent grinds the work list until it needs you
rx7 criticize electrical-build  ← when a design settles: three isolated reviewers, findings only
rx7 clean                       ← before a commit, or when a trigger says so
rx7 diff                        ← the ten lines; then git commit
```

You touch the record in exactly three places: the **ANSWER:** block of a packet, a `set` of a measured number, and `git commit`. Everything else is a workflow.

## 2 · The workflows, one line each

| Command | When | What you get back |
|---|---|---|
| `rx7 status` | first thing, every time | one screen: phase per project, what waits on whom, the checks, the trigger's recommendation |
| `rx7 propose <name> --kind <kind> "<goal>"` | a new project | the folder, the opening question set, the first work list — phase PROPOSED |
| `rx7 plan <project> [--cycles N]` | PROPOSED / PLANNING | cycles of harvest → next agent item → do → build → log, until only your calls are left |
| `rx7 answers` | after you answer packets | rulings by `D-`, what was sharpened, what is new, what left or joined the carts |
| `rx7 criticize <project>` | a design feels settled; every two weeks | `reviews/CRITIQUE-<date>.md` with `C-` findings by severity — nothing changed |
| `rx7 clean [project]` | a trigger says so; before a commit | prose brought to the data, typed facts turned into placeholders, cells to values |
| `rx7 shop <project> "did 2.4–2.7, alternator 14.1 V warm"` | BUILDING, in the garage | steps ticked, numbers filed, the **next step** and its gate |
| `rx7 complete <project> --system <name>` | shakedown logged | the manual gains the system chapter; the archive gains the process; the project folder is gone |
| `rx7 log "oil change, 153400, Mobil 1 HM"` | any day, no project | one service row; the schedule recomputes next-due |
| `/rx7-overview <project>` | **in the chat app**, not the terminal | a short design conversation; nothing written — it ends with "say the word and I'll log it" |
| `rx7 diff` | end of every session | the ten-line diff and the commit line |

`rx7 check`, `rx7 build`, `rx7 lint`, `rx7 triggers`, `rx7 tables <p>`, `rx7 find <p> <text>` run the tool directly — no Claude, no credits.

## 3 · Starting a workflow from PyCharm

Three ways, from fastest to most integrated:

**A · The terminal tool window** (Alt+F12). `rx7 <workflow> <args>` — the launcher `tools\rx7.cmd` opens Claude Code with the slash command already typed (`claude "/rx7-plan electrical-build"`), so the workflow starts the moment the window opens. Add `tools\` to PATH once (or type `tools\rx7`). This is the recommended path for `plan`, `answers`, `criticize`, `clean`, `shop`, `complete`, `log`, `diff`.

**B · The Run dropdown** (Shift+F10 on the selected configuration). The deterministic commands — status, check, build, lint, triggers, answered packets — run as Python configurations in the Run window with clickable file paths. Assign keymaps in Settings → Keymap → *Run Configurations* (e.g. `rx7 status` → Ctrl+Alt+S).

**C · The Claude Code tool window** (the JetBrains plugin). Type `/rx7-<workflow> <args>` — same skills, plus the open file as context. Best for `overview`-style thinking while editing, and for `plan` when you want to watch it work.

Two things to know: a workflow *never* asks you a question mid-run — if it needs your call it writes a packet and keeps going; and every workflow ends with a `log.csv` row, so `rx7 status` always shows what last happened.

## 4 · What runs by itself — the triggers

Nothing spends credits without you saying so; everything deterministic runs on its own.

| Layer | Fires when | Does |
|---|---|---|
| **Claude Code hooks** (`.claude/settings.json`) | the agent edits any `data/` or `templates/` file | runs that project's `check`; a refusal is fed straight back to the agent, so it cannot leave a contradiction behind. At the end of every agent turn: `check` on every project + the triggers, printed into the transcript |
| **Pre-commit hook** (`.githooks/pre-commit`) | `git commit` | refuses a commit unless every project's build is clean; rebuilds and stages any rendered file that was stale; prints the triggers |
| **File Watcher** (PyCharm, §0.5) | you save a CSV or template | rebuilds that project — documents and `MANUAL.html` are always current |
| **`tools/triggers.csv`** | `rx7 status`, the Stop hook, the pre-commit hook | evaluates the lint metrics against thresholds and **names the workflow to run** |

The trigger rules, editable in `tools/triggers.csv` — your "duplicated text" example is T02:

| ID | Metric | Threshold | Names |
|---|---|---|---|
| T01 | `check_problems` | > 0 | `/rx7-clean` — the build is refused |
| T02 | `duplicate_paragraphs` | ≥ 2 | `/rx7-clean` — the same text in two files; one is a view not yet written |
| T03 | `superseded_cited_bare` | ≥ 5 | `/rx7-clean` — superseded decisions cited without `→` |
| T04 | `typed_next_ids` | > 0 | `/rx7-clean` |
| T05 | `answered_waiting` | > 0 | `/rx7-answers` — you answered; it is not applied |
| T06 | `open_agent_work` | ≥ 1 | `/rx7-plan` — the agent has work |
| T07 | `markdown_in_cells` | ≥ 20 | `/rx7-clean` — values, not sentences |
| T08 | `dangling_other_ids` | ≥ 10 | `/rx7-clean` |
| T09 | `days_since_critique` | ≥ 14 | `/rx7-criticize` |

**Making a trigger act on its own.** Set `auto=yes` on a row and run `rx7 triggers --auto` — it runs `claude -p "/rx7-<workflow> <project>"` headless for every fired row. To schedule it: Windows Task Scheduler → a nightly task running `tools\rx7 triggers --auto` in the repo. I have left every row at `auto=no` on purpose: a headless `/rx7-clean` on a tree you are mid-edit in is a bad surprise, and it spends credits while you sleep. The safe pattern is `auto=yes` on T02/T03/T04/T07 only (clean is idempotent and changes no design), nightly, with the commit still yours in the morning — turn it on when the first few manual runs have shown it behaves.

## 5 · Answering questions — the one habit that drives everything

Open `02-PROJECTS/<project>/data/questions/Q-xxx.md` in PyCharm. Every packet reads on its own: **Ask · Why it matters · Options with consequences · Recommend · Blocks · a one-word ask**. Write under `**ANSWER:**` — `yes`, `no, do (b)`, `follow recommendations`, or a paragraph if it is a brief. Then `rx7 answers`. Never edit `QUESTIONS.md` — it is rendered; the body file is the record. `rx7 answers-list` shows what you have answered and not yet applied.

If a packet is not clear enough to answer from the file alone, that is a defect: answer "unclear — <what is missing>" and `rx7 answers` sharpens it instead of ruling.

## 6 · Two machines

Both clones are equal; the workflows run in whichever PyCharm is in front of you. The only rule: **pull before you start, commit and push when `rx7 diff` says so.** The Claude Project on claude.ai holds one pointer document and nothing else; nothing is ever queued there — if the machine you want is off, the work waits.

## 7 · If something is wrong

`rx7 check` names the row. The fix is always in the data or the template, never in the check — unless the check is wrong, in which case fix the check and log why in the decision. A workflow that asks you a question mid-run, edits a rendered file, or types an id by hand has a bug: say so, and the skill file gets fixed the same session (R11 — twice is a pattern).

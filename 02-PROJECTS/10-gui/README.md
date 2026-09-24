# 10 · GUI

A graphical tool for running this tree: see where every project stands, read and answer
blocks and picks one at a time in a clean layout, and hand work to Claude Code with a
button instead of a terminal. Opened 2026-09-24 (D-399). Phase: PROPOSED. The plan is
under Camden's review, and nothing is built yet.

---

## The rules it lives under

The GUI is a **window onto the record**, not a new place for facts. Every rule in
`CLAUDE.md` applies to it, and five of them shape its design:

1. **The record is the only truth (R2).** The GUI keeps no copy of any fact: no database of
   its own, no cache that can go stale. It reads the CSVs, `BLOCKS.md` and `PICKS.md`
   through `rx7.py` every time it shows them.
2. **His writing goes where it always goes (R3).** An answer typed in the GUI is written under
   the block's `**SOLVE:**` line in `BLOCKS.md` (or a pick's `**ANSWER:**` in `PICKS.md`) by
   a script, exactly as if he had typed it there. The GUI is a nicer way to type into the
   same page. Nothing typed is ever lost: drafts save as he types, and a write that finds
   the file changed underneath it stops and says so.
3. **Exit codes and data, never scraped text (R9).** The GUI never reads `rx7.py`'s printed
   words. `rx7.py` gains a machine-readable output (JSON) for what the GUI shows.
4. **Scripts first, Claude second.** Anything with one right answer (listing blocks, saving
   an answer, running `check`, regenerating a TODO) is a script. Claude is called only for
   judgement: explaining a block, discussing an answer, applying answered blocks.
5. **It runs here.** On the Fedora PC, from the tree at `~/docs/storage/Rx7`, and never on
   the Windows machine.

---

## How a GUI application is made

The same ten steps apply to any GUI (web, desktop or phone). This project follows them in
order, and each step is work rows in `data/work.csv`.

1. **Jobs.** Write down what the tool must let you *do*, as verbs: "answer a block",
   "see what I can start today", "ask Claude to explain this". Features come from jobs,
   never the other way round.
2. **Screens and flows.** One screen per job (or a few jobs that belong together), and the
   paths between them: where you land, how you get from a block to its decision, how you
   get back.
3. **Wireframes.** Rough grey boxes for each screen: what goes where and what is biggest.
   No colour, no fonts. Wireframes are cheap to change and code is not.
4. **Architecture.** Every GUI has three layers, and deciding them early saves rewrites:
   - **Data**: where facts live. Here, the record, reached only through `rx7.py`.
   - **Logic (the backend)**: code that does things: runs `rx7.py`, writes an answer,
     calls Claude. It answers requests like "give me block 01.11" or "save this answer".
   - **Interface (the frontend)**: what you see and click. It asks the backend for data
     and shows it. It never touches files itself.
5. **Platform and toolkit.** Web page, desktop window or phone app; and the language and
   framework to build it in. Chosen *after* the architecture, because the backend usually
   stays the same whichever face it wears.
6. **Visual design.** A small design system: one or two typefaces, a colour palette that
   works in light and dark, spacing rules, and reusable pieces (a card, a button, a
   status badge). Decided once and reused, so every screen looks like one tool.
7. **A vertical slice.** One screen built all the way through, from data to logic to
   interface: the Blocks screen first. It proves the whole stack before anything is
   copied.
8. **Testing.** With the real record, including the failures: `check` refusing, Claude not
   answering, two edits at once, the network down.
9. **Iterate.** Add screens one at a time, each a copy of the pattern the slice proved.
10. **Package and launch.** How it starts: a Super+P entry, a menu item, a service that
    starts at boot, and how it is reached from a phone if at all.

---

## Screens

The site map lives in `data/screens.csv`, and every idea raised about the app in
`data/ideas.csv`, raw and unsorted until the clean-up (D-400). The layout starts from
Camden's home page with two options:

- **Manual**: the owner's manual (car state, diagrams, work and repair history, parts and
  spec sheets)
- **Projects**: the hub for starting a new project and working on current ones

`SPEC.md` is the sheet Camden fills in with every detail the build needs.

---

## Where Claude fits

| Task | Done by |
| --- | --- |
| List blocks, picks, work, status | `rx7.py` (JSON output) |
| Save an answer into `BLOCKS.md` / `PICKS.md` | a script |
| Explain a block in plain words · discuss before answering | Claude (quick, read-only) |
| Apply answered blocks · plan · review · parts rounds | Claude Code, running the `CLAUDE.md` playbooks in the tree |

---

## Platform options

| Option | What it is | Pros | Cons |
| --- | --- | --- | --- |
| **Local web app** | A Python backend on this PC; the interface is a page in the browser | Same language as `rx7.py`; works on the desktop and on a phone's browser; nothing to install on the phone | Needs the PC on; phone access needs a private network link |
| **Desktop app** | A native window (for example Python with Qt, or Tauri) | Feels like an app; no browser | Desktop only; a phone version would be a second build |
| **Phone app (iOS)** | A native app | Best on the phone | Needs a Mac and Apple's developer account to build; the PC still does the work |

The plan under review recommends the **local web app**. The choice is Camden's: SPEC.md 1.1.

# 10 · GUI — Rx7, the app

The pitch, 2026-09-25. On 2026-09-24 you answered every question in the spec sheet and asked
me to design, build, test, review and dial in the apps on my own, then pitch the design here.
Both apps are built and tested, and nothing is installed yet. Read this, then tell me what to
change (work row C3). Once you're happy, I install the desktop app and build the phone app for
your Galaxy (F1, F2).

---

## In three sentences

**Rx7 is one app in two places: a desktop app on the Fedora PC and an Android app on your
Galaxy. Both show the whole record (every project, block, pick, work row, decision and part)
and are where you answer what only you can answer.** The Markdown pages are gone (D-405).
The app computes every screen from the CSVs each time it opens, so it can never disagree with
the record. It keeps no fact of its own. The phone works with no signal: it reads everything
offline, keeps what you type, and sends it the next time it can reach GitHub.

---

## What you asked for, and where it is

| You said | What the app does |
| --- | --- |
| "desktop fedora app + andriod app" (1.1) | One codebase, two real installed apps: Tauri on the desktop, Tauri's Android build on the phone. |
| "4 states over mid roadtrip at the gas station… as accessable as the book in the glovebox" (1.4) | The phone reads the record from GitHub, keeps a copy, and reads it offline. The PC can be off. |
| "you can queue responses but not send them" offline (4.7) | An answer typed offline says *Saved on this phone, sent at the next connection*. It survives the app being closed, and it goes out as one commit when GitHub is back. |
| Dark only, your five colours, "clean, technical and calm" (2.1–2.4) | Your palette is the whole design system. Every lighter and darker tone is mixed from those five, with no new hue. |
| Home "roomy and style oriented, only two options" (2.5, 3.1) | Home is the car drawn in your colours, the car's line, and two tiles: **Manual** and **Projects**. |
| Data pages "tight and condenced" (2.5) | Project pages are dense: one line per work row, one line per part, no pictures. |
| Menu bar and breadcrumbs (3.3) | Always there on the desktop. On the phone they become a tab bar at the bottom and a back arrow. |
| "search will be a very key part of this tool" (3.4) | One box finds anything anywhere: decisions (their full text), blocks, work rows, parts, any row of any table. **Ctrl K** from every screen. |
| Project cards with "id + default + icon" (6.1) | Each card shows the id, name, icon, phase, a progress bar, what waits for you, and the last thing that happened. |
| "c + skip to next question button" (7.3) | A block has a button per option, **Follow the recommendation** in one tap, a box for your own words, and **Next unanswered**. |
| Every answering page: a list, step forwards and back, next unanswered, back to the list, Apply at the top (8.4) | Blocks, Picks and TODO all work this way. The keys **←/→**, **N** and **Esc** do the same. |
| TODO answered "case by case… a check… a value… a dropdown" (8.2) | Each of your rows gets the control it needs: **Done**, a number with its unit, or a list of choices (`work.reply`, D-406). |
| "remove the poor expensive md system" (11.2) | No page is written anywhere. The record is CSV, and the app shows it. |

---

## A walk through it

**Home.** The car in line-art, *1982 Mazda RX-7, FB chassis · GS · Sunbeam Silver · 12A
rotary · 153,000 mi*, then the two tiles. The Projects tile tells you how many things wait
for you. When you add a photo to `01-REFERENCE/photos/`, it replaces the drawing with no code
change.

**Projects.** One card per project. **New project** asks for a name and a paragraph of what
it's for; Claude opens the area and you land on it.

**A project.** A header with the goal and progress, then tabs: **Overview · Blocks · Picks ·
TODO · Decisions · Parts · Run**. An orange count on a tab is what waits for *you* there.
Overview puts it on one screen: your blocks, the steps you can start today (with **Done**
right there), and the latest log entries.

**Answering a block.** One block at a time. The question sits large at the top, then the
options as buttons with the recommended one marked, then the recommendation, then your box.
*Why it matters* and *What it stops* sit beside it on the desktop and below it on the phone.
**Explain** has Claude restate the block in plain words. **Discuss** opens a chat about it
first, and the chat's key points ride along with your answer so they reach the decision. Your
answer is saved at once and waits for **Apply** (7.6).

**Apply.** Every answering page has **Apply** at the top. It hands your saved answers to
Claude Code, which runs the playbook in `CLAUDE.md` (§6.2 for blocks, §6.9 for picks, §6.4
for TODO). You watch it work live, and its report is the result.

**TODO.** Two lists, **Design** and **Build**, each in working order and split into the
parts of the build (car whole → car apart → car back together). You can filter to *yours*,
*Claude's*, or *only what can start now*.

**Decisions.** Searchable, grouped by system, each one linked to what it replaced and what
cites it. Your own words are always quoted as you typed them.

**Parts.** The whole parts table, one part per line: item, spec, quantity and price first,
the part number pinned at the left while the row scrolls. Click a line for everything about
that part.

**Run.** The runs that belong to no single page: **Plan**, **Review** and a **parts round**,
plus the live feed, earlier runs and recent commits. The app says when a run is likely to
take a while. There is no hard cap (D-406).

**On the phone.** The same screens, laid out for one hand: a tab bar at the bottom, lists as
cards, tabs that scroll sideways and fade where more wait. Claude runs only on the desktop
(4.7: "no claude access" offline). From the phone, **Request** saves a run request in the
record, and the desktop runs it the next time it opens.

---

## How it works

Three layers, and the rule that keeps them honest:

- **Data: the record, reached only through `tools/rx7.py`.** The app never opens a CSV
  itself. The desktop runs `rx7.py export` for everything it shows and `rx7.py answer` for the
  one thing it writes: your answer, as its own file in the project's `inbox`, written whole or
  not at all.
- **Logic, on the desktop: a small Rust shell** that runs `rx7.py`, commits and pushes each
  answer (*Camden answered 00.29 (desktop)*), syncs with GitHub, and runs Claude Code headless
  for Explain, Discuss, Apply and the Run page.
- **Logic, on the phone: the same `rx7.py`, compiled to WebAssembly.** The phone downloads
  the record's CSVs from GitHub and runs the *real* `rx7.py` on them inside the app (Python
  in the browser engine, via Pyodide). The phone and the desktop can't drift apart, because
  there is one tool, not two copies of the rules. Your answers go to GitHub as commits through
  its API.
- **Interface: Svelte, one codebase for both.** Only one small module per device differs
  (`app/src/lib/platform/`).

Why these choices: Tauri makes small, fast native apps from a web interface, so one design
serves the desktop and the phone (your 1.1). Running `rx7.py` itself on the phone was the
only way to keep "one source of truth" true offline (your 11.2). The code is kept plain and
commented so we can go through it piece by piece later (12.1). `app/README.md` has the map of
the code and every build, test and install step.

---

## How it was tested

- **29 unit tests**: the safe renderer for decision text, search, the phone's queue of
  unsent answers.
- **16 browser tests** at desktop and phone size: every screen, answering a block, a pick and
  a TODO row, search, and a Claude run with a stand-in Claude.
- **The desktop app itself, 9 checks**: loads the real record through `rx7.py export`, saves
  an answer, checks your words arrive byte for byte, commits it alone with its message,
  pushes, syncs a phone answer in, withdraws it. All on a sandbox copy, never the real tree.
- **The Android app on an emulator**: add a GitHub key, open block 00.31, cut the network,
  answer with curly quotes, µ, ✓ and a line break in the text, kill the app, reopen it offline
  (the answer is still there), reconnect. It arrived as one commit, *Camden answered 00.31
  (phone)*, every character exact, and `rx7.py check` passed with it in the record. The GitHub
  in these tests is a local stand-in, so nothing touched the real repository.
- **A visual review** of every screen at 412 to 1920 px wide. It found and fixed: phone tabs
  hiding Parts and Run, the project header crowding every phone page, a desktop page scrolling
  sideways, an unreadable parts table, a stage letter that read as an 8, and a test-only
  network permission that would have shipped in the real app.

---

## Calls I made that you may want changed

1. **The phone needs a GitHub key to send answers** (a fine-grained token for this one
   repository, set once in Settings). It reads without one. This is the price of the phone
   working with the PC off.
2. **Claude never runs on the phone.** A run you ask for from the phone waits for the desktop.
3. **Manual is a placeholder.** It says what it will be and waits for the plan we make
   together from your brief (D-407, work row M1).
4. **No photos yet**, because there are none in the tree. The home page uses the line drawing
   until you add one.
5. **The phone build is a debug build** (signed with a development key, installed over USB).
   That's fine for one phone. A proper signing key is idea I-016.
6. **The app has no Content-Security-Policy yet** (idea I-015). It only ever loads its own
   files, GitHub and your record, but turning one on is the right finish before you show it
   to anyone.

---

## What happens next

| Row | Who | What |
| --- | --- | --- |
| C3 | you | Read this and say what to change. "Done" means go ahead. |
| F1 | me | Install the desktop app with a menu entry; build the phone app for your Galaxy. |
| F2 | you | Plug in the phone, install Rx7, paste the GitHub key. `app/README.md` has the steps. |
| D3 | you | Answer one real block through the app and tell me what worked. |
| M1 | you, with me | Plan the Manual from your brief in D-407. |

The site map is `data/screens.csv`, every idea raised about the app is in `data/ideas.csv`,
and the rulings behind all of it are D-403 to D-407.

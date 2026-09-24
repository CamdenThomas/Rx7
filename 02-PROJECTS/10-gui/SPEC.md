# 10 · GUI — the spec sheet

_Written 2026-09-24 (D-400). This is your page to write in, like `BLOCKS.md`. Nothing
regenerates or rewrites it. When you're done, your answers are copied into the record
(decisions and rows) and only then removed from here._

**How to fill it in**

- Type after any `**ANSWER:**` line, on that line or below it. Plain sentences, any
  length, no special format.
- **Blank means "use the default."** Every question has one, so you only need to answer
  what you care about. "Default is fine" or "you pick" also works.
- Answer in any order, over as many sittings as you like. Say "I filled in some of the spec"
  and it gets picked up.
- Unsure? Write your question after `**ANSWER:**` and it'll be answered here.
- Ideas that don't fit any question go in section 13.

---

## 1 · The big picture

### 1.1 · Platform
In chat you called it "the gui web app." Is that the call: a web app running on the Fedora
PC, opened in a browser?
- (a) Web app on the Fedora PC, opened in a browser
- (b) Desktop window app on Fedora
- (c) iOS app (needs a Mac to build)

**Default** (a).
**ANSWER:**

### 1.2 · Who uses it
Only you? Or will anyone else ever look at it, like a mechanic, a friend helping, a
sponsor, or a buyer if the car is sold?

**Default** Only you. Nobody else sees it.
**ANSWER:**

### 1.3 · Which devices
Where will you open it? Desktop monitor, laptop, phone, tablet, a screen in the garage?
Which one matters most?

**Default** The desktop first, and it also works on a phone's browser.
**ANSWER:**

### 1.4 · Reaching it away from home
Should your phone reach it when you're not at home (in a parts store, at a junkyard), or
only on home Wi-Fi?
- (a) Home only
- (b) Anywhere, over a private encrypted link (Tailscale, free)
- (c) Later, not now

**Default** (c).
**ANSWER:**

### 1.5 · In the garage
Is there Wi-Fi where the car is? Will the laptop or phone be used next to the car with
dirty hands? (That decides big buttons, a high-contrast mode and offline copies.)

**Default** Assume weak Wi-Fi and dirty hands: big touch targets and a readable
high-contrast mode.
**ANSWER:**

### 1.6 · Always on, or started when needed
- (a) Starts automatically when the PC boots and is always there
- (b) Starts from Super+P or a menu item when you want it

**Default** (a), so a phone can always reach it.
**ANSWER:**

### 1.7 · Name
What's the app called? Shown in the browser tab and at the top of the page.

**Default** "Rx7".
**ANSWER:**

---

## 2 · Look and feel

### 2.1 · Three mood words
Pick three words for how it should feel. Examples: clean, technical, warm, luxurious,
retro-80s, Japanese, workshop, minimal, dark, glossy, paper-manual.

**Default** Clean, technical, calm.
**ANSWER:**

### 2.2 · Things you like the look of
Name any apps, websites, car dashboards or manuals whose look you like: the RX-7's own
1980s factory manual, a modern car's infotainment, Apple, Notion, a race-data app.

**Default** None. The style is built from 2.1.
**ANSWER:**

### 2.3 · Light, dark or both
- (a) Dark only
- (b) Light only
- (c) Follow the device setting
- (d) A switch in the app

**Default** (c) and (d).
**ANSWER:**

### 2.4 · Colours
Any colours it should use or avoid? A body colour of the car, a brand colour, Mazda red?

**Default** Neutral greys, with one accent colour chosen from the car.
**ANSWER:**

### 2.5 · Density
- (a) Roomy: big text, one thing at a time
- (b) Dense: lots on screen at once, like a spreadsheet
- (c) Roomy on the phone, dense on the desktop

**Default** (c).
**ANSWER:**

### 2.6 · Photos and models
How much should it lean on pictures: photos of the car, 3D models of the boards, rendered
diagrams? Everywhere, or only where they explain something?

**Default** Only where they explain something.
**ANSWER:**

### 2.7 · Animation
Smooth transitions and small motion, or instant and still?

**Default** Subtle and quick, and off if the device asks for reduced motion.
**ANSWER:**

---

## 3 · The home page

### 3.1 · Exactly two options
You said the home page has only two options, Manual and Projects. Should anything else
show there at all? For example: the car's photo, a one-line status ("2 blocks waiting for
you"), a search box, the date of the last service.

**Default** The two options, with a small status line under Projects.
**ANSWER:**

### 3.2 · What the two options look like
Two big tiles with a picture each, two plain buttons, or something else?

**Default** Two large tiles, each with a photo and a one-line summary.
**ANSWER:**

### 3.3 · Getting around
Once inside, how do you move around?
- (a) A menu bar always on screen
- (b) Back buttons and breadcrumbs (Home › Manual › Diagrams)
- (c) Both

**Default** (c).
**ANSWER:**

### 3.4 · Search everywhere
Should one search box find anything anywhere: a part number, a wire colour, a decision, a
torque spec, a date?

**Default** Yes, from every screen, with a keyboard shortcut.
**ANSWER:**

---

## 4 · The Manual: overall

### 4.1 · The tool you wish you had
In your own words: when you started on this car, what did you waste time on? What did you
wish you could just look up? This is the most important answer on the sheet.

**Default** None. Only your answer can fill this one.
**ANSWER:**

### 4.2 · How it's organised
What's the top-level order of the Manual?
- (a) By **system**: engine, fuel, electrical, brakes, suspension, body, interior
- (b) By **where on the car**: engine bay, dash, doors, rear
- (c) Like the factory manual's chapters
- (d) By the four areas you named: state, diagrams, history, parts, each one searchable by
  system

**Default** (d), with system as the filter everywhere.
**ANSWER:**

### 4.3 · Read-only or editable
Can you change facts from the Manual (fix a spec, add a note, log a repair)? Or does it only
show them, with changes going through Claude or a form?

**Default** Read-only, plus an "add to history" form and a "this is wrong" button that
opens a block.
**ANSWER:**

### 4.4 · Where each fact came from
Every fact in the record has a source: a factory manual page, a measurement, a datasheet.
Should the Manual show it?
- (a) Always, next to the fact
- (b) On hover or tap
- (c) Never

**Default** (b).
**ANSWER:**

### 4.5 · Measured or unconfirmed
Many values carry `confirm`, meaning nobody has measured them yet. Should the Manual mark
those visibly?

**Default** Yes, with a small badge.
**ANSWER:**

### 4.6 · Printing
Do you want printed or PDF copies, like the pins-and-cavities printout the electrical build
keeps in the car? Which parts?

**Default** Any Manual page prints cleanly, and there's a "print the in-car kit" button.
**ANSWER:**

### 4.7 · Offline
Should the Manual work with no connection, for example in the garage with the PC off?

**Default** No for now; it needs the PC reachable. Offline is revisited later.
**ANSWER:**

---

## 5 · The Manual: its four sections

### 5.1 · Car state: the first thing you see
When you open Car state, what should be at the top? For example: VIN, mileage, engine, the
photo, what's broken right now, what's changed from factory, what's planned.

**Default** Identity and mileage, then open issues, then each system as fitted.
**ANSWER:**

### 5.2 · Car state: mileage
Should you be able to enter the current mileage whenever you drive it, so intervals and
history stay dated?

**Default** Yes, a one-field "update mileage" on Car state.
**ANSWER:**

### 5.3 · Car state: due and overdue
Show service intervals as due, overdue or fine (oil, coolant, belts)?

**Default** Yes, a small "due soon" list on Car state.
**ANSWER:**

### 5.4 · Diagrams: which ones
Which diagrams belong here? Check any: the factory wiring circuits, the new harness legs,
the connector pinouts, the ICU/DCU boards and their 3D models, photos of the car, exploded
parts views, vacuum diagrams, anything else.

**Default** All of the ones that exist, grouped by system.
**ANSWER:**

### 5.5 · Diagrams: how you use them
What should you be able to do with a diagram? Zoom and pan; tap a wire to see its colour,
gauge, both ends and fuse; tap a connector for its pinout; search for a wire and have it
light up; compare the factory circuit with the new harness side by side.

**Default** Zoom, pan and search first. Tap-a-wire comes in a later phase (it needs the
drawings made clickable).
**ANSWER:**

### 5.6 · Diagrams: factory scans
The factory circuits are scanned pages. Are plain scans (zoom only) fine, or should they be
redrawn over time so they can be searched and clicked?

**Default** Scans for now, redrawn only where you ask.
**ANSWER:**

### 5.7 · History: how it reads
- (a) One timeline, newest first
- (b) Grouped by system
- (c) A timeline with a system filter

**Default** (c).
**ANSWER:**

### 5.8 · History: what each entry holds
Tick what matters: date, mileage, what was done, why, parts used, cost, time it took,
photos, who did it, what was found wrong, links to the project and decisions behind it.

**Default** All of them, with cost and time optional.
**ANSWER:**

### 5.9 · History: adding entries
How do you add a repair? A form in the app, telling Claude in plain words ("changed the oil
at 101,200"), or both?

**Default** Both. The form for quick entries, Claude for anything with detail.
**ANSWER:**

### 5.10 · History: photos
Should you be able to add photos from your phone to a history entry or a part? Where should
they be stored?

**Default** Yes. Stored in the tree under `01-REFERENCE/photos/`, named by date and system.
**ANSWER:**

### 5.11 · Parts: what a spec sheet shows
For one part, tick what you'd want: part number, maker, the specs, where it's fitted, where
it was bought and the price, the datasheet PDF, photos, torque, fluid, the service interval,
substitutes, and the project that chose it.

**Default** All of the ones the record holds.
**ANSWER:**

### 5.12 · Parts: factory specs
The record holds 218 factory specifications (torques, clearances, capacities). Should they
sit with the parts, in their own "Specs" list, or both?

**Default** Both: a searchable Specs list, plus each part showing its own.
**ANSWER:**

### 5.13 · Parts: buying
Should the parts section show things still to buy, with prices and links, and totals per
project?

**Default** No. Buying lives in each project; the Manual shows only what's on the car.
**ANSWER:**

---

## 6 · Projects

### 6.1 · The hub: what each project card shows
On the Projects page, what should each project show? Phase, a progress bar, blocks waiting
for you, what you can start today, money spent or left, the last activity, a photo.

**Default** Name, phase, a progress bar, "N waiting for you", and the last activity.
**ANSWER:**

### 6.2 · A new project
When you press "New project," what do you give it? Name, goal, which systems it touches, a
rough budget? And then what happens: Claude opens the area and writes its first questions,
or an empty project waits for you?

**Default** You give a name and one paragraph of goal. Claude opens the area, writes the
opening blocks and a first work list, and you land on the project's page.
**ANSWER:**

### 6.3 · Inside a project: its pages
These pages are proposed for each project: Blocks, Picks, TODO, Decisions, Run. Keep all,
drop any, add any (Parts, Carts, Diagrams, Log, Budget, Photos)?

**Default** Keep all five, plus Parts.
**ANSWER:**

### 6.4 · Finished projects
When a project is complete, it folds into the car record and its process is archived.
Should finished projects still show on the hub?

**Default** Yes, in a collapsed "Finished" group that opens the archive.
**ANSWER:**

---

## 7 · The Blocks page and Claude

### 7.1 · How Claude is reached
- (a) Claude Code in headless mode: your subscription, running in the tree, following
  `CLAUDE.md`
- (b) The Claude API with a key: faster for quick chat, billed per use
- (c) (a) for work, (b) only for quick chat

**Default** (a). (b) is added only if (a) is too slow for chat.
**ANSWER:**

### 7.2 · One block at a time: what's on screen
The block's Ask, Why, Options, Recommend and Stops, laid out for reading. What else? Which
project, how long it's been open, what it unblocks, the decisions it touches, a picture if
one helps?

**Default** All of the above; pictures only where one exists.
**ANSWER:**

### 7.3 · Answering
- (a) A text box only
- (b) A button per option, plus a text box for anything else
- (c) (b), plus "follow recommendation" as one tap

**Default** (c).
**ANSWER:**

### 7.4 · Explain
What should "Explain" do? Restate the block in plain words; show what each option would
mean for the car; draw a picture; say what happens if you don't answer?

**Default** Plain words, then what each option means for the car.
**ANSWER:**

### 7.5 · Discuss
Should "Discuss" open a chat beside the block, so you can ask questions and then answer? Is
the chat saved? If so, where (inside the block's `Why`, in a history, or thrown away)?

**Default** A chat beside the block. When you answer, its key points are saved into the
block's Why above your answer; the rest is thrown away.
**ANSWER:**

### 7.6 · After you answer
- (a) The answer is saved and waits until you press "Apply answers"
- (b) Claude applies it right away and shows what changed

**Default** (a). Applying writes decisions, so you choose when.
**ANSWER:**

### 7.7 · Chat anywhere else
Should there be a general "ask Claude about the car" chat anywhere else: on every page, in
the Manual, per project?

**Default** One chat on every page that knows which page you're on.
**ANSWER:**

### 7.8 · What Claude may do without asking
From the GUI, can Claude write to the record freely (as the playbooks allow), or should
every write show you a summary to approve first?

**Default** It follows `CLAUDE.md` as the terminal does, and each run ends with a report of
what changed.
**ANSWER:**

### 7.9 · Cost and limits
Any usage cap or warning you want: a daily limit on Claude runs, a warning before a long
one?

**Default** A warning before a run expected to be long. No hard cap.
**ANSWER:**

---

## 8 · Other project pages

### 8.1 · Picks
One product at a time with its photo, price, why, drawbacks and runner-up; Yes / No with a
reason / Question. Anything to add, like a "compare with runner-up" view or a buy link that
opens the store?

**Default** As described, plus a buy link.
**ANSWER:**

### 8.2 · TODO
Can you mark things done or enter measurements from the TODO page ("measured 55.2 mm"), or
only read it?

**Default** A "Tell Claude what I did" box per row; Claude records it.
**ANSWER:**

### 8.3 · Decisions
Just searchable and grouped, or also a "why is it like this?" view that walks back through
the decisions behind something?

**Default** Searchable and grouped; each decision links to what it superseded and what
cites it.
**ANSWER:**

### 8.4 · Run
Which workflows need buttons: apply answers, plan, review, parts round, check, commit? Should
you watch Claude work live, or just get the report?

**Default** Apply answers, plan, review and parts round, with a live feed you can collapse.
**ANSWER:**

---

## 9 · Notifications

### 9.1 · Being told
Should the app tell you things, like a Claude run finishing, new blocks waiting, or an
interval due? How: a phone push, an email, a badge in the app?

**Default** A badge in the app only, for now.
**ANSWER:**

---

## 10 · Git and safety

### 10.1 · Commits
Claude now commits and pushes at the end of every run (D-401). Should the app show that
history (what changed, when, and why), have a "commit now" button, or stay out of git?

**Default** A read-only list of recent commits on each project's page. Committing stays
Claude's job.
**ANSWER:**

### 10.2 · Things that must never happen
List anything the app must never do. Some are already rules: never lose your typing, never
keep facts outside the record, never touch the Windows drive. Add your own.

**Default** Those three.
**ANSWER:**

### 10.3 · Password
If it's ever reachable from the phone (1.4), should it ask for a password or PIN?

**Default** No. The private link (Tailscale) only lets your own devices in.
**ANSWER:**

---

## 11 · Order and priorities

### 11.1 · What first
After the groundwork, which screen should be built first?
- (a) Blocks (answering is the daily job)
- (b) Manual
- (c) Projects hub

**Default** (a), then the hub, then the Manual.
**ANSWER:**

### 11.2 · Must-haves
Which ideas on this sheet would make the app worthless without them? Which are nice-to-have?

**Default** The Blocks page and search are must-haves; everything else is nice-to-have.
**ANSWER:**

### 11.3 · Time
Any date you'd like the first usable version by?

**Default** No date.
**ANSWER:**

---

## 12 · Learning

### 12.1 · Do you want to build parts yourself?
Should the code be written so you can learn from it and change it yourself (comments, a
walkthrough, simple tools), or just work?

**Default** Plain and commented, with a short "how it works" in the README.
**ANSWER:**

---

## 13 · Anything else

Ideas, wishes, screens not covered, or things you've seen elsewhere that you want.

**ANSWER:**

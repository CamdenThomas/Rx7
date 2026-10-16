# tools/steps - the writers of Camden's TODO briefs and steps (D-533)

Four folders, one per phase of the list. Each `build.py` regenerates that phase's `briefs.csv`
and `steps.csv` beside itself from the record's tables and the prose in its row files; they
reproduce the loaded rows exactly (checked 2026-10-13). To change a row: edit its text in the
phase's row file (or the table it quotes), then from the tree root

    python3 02-PROJECTS/02-electrical/tools/steps/<phase>/build.py      # phase 1 takes the parts table's path
    python3 02-PROJECTS/02-electrical/tools/steps/load.py 02-PROJECTS/02-electrical/tools/steps/<phase>

`plugs.py`, beside the four folders, words the plug of every part from `devices` (`plug`, `plug_from`,
`leg_end`, `plug_seen`; D-543): the LOOK steps of S1, V-115 and V-116, the End steps of the legs
(E20-E23), E26's switch move, every migration row of E28 and the ends of E36-E41 quote it, so rebuild
all four phases after a device row's plug changes. A row a ruling drops comes out of its phase's row
file and list, and its briefs and steps rows are deleted with `rx7.py del` (the loader only replaces
the ids a phase still names).

`load.py` replaces the briefs and steps of that phase's work ids and runs `check`. A one-line
fix to a single step is `rx7.py set 02-electrical steps <id> how=…` - then make the same
change in the row file, or the next rebuild undoes it. What follows is the brief the writers
were given: it is the standard a new row's brief and steps are written to.

---

# Writing the briefs and steps for Camden's electrical TODO rows (D-533, work row Y31)

Tree: /Users/crash/dev/Rx7 (a 1982 Mazda RX-7 FB being rewired: ECUMaster PMU-24, a rear lithium
battery, four harness legs L1-L4 with Deutsch connectors, two custom modules ICU and DCU). The
record is CSV driven by `tools/rx7.py`. Every python3 call on this Mac is
`env DEVELOPER_DIR=/Library/Developer/CommandLineTools python3 tools/rx7.py …`.

Read first: /Users/crash/dev/Rx7/CLAUDE.md (the rules; R11 "you cannot see the car" binds every
line you write), then `rx7.py get 02-electrical decisions D-533` (the ruling and his words),
`rx7.py doc work`, `rx7.py doc record`, and 02-PROJECTS/02-electrical/data/_tables.csv (what
every table is: backbone, cables, cavities, housings, fuses, relays, grounds, routes, devices,
loads, inputs, ladders, wake_stages, migration, checks, node_conductors, modules, pins, parts,
carts, bringup_log, recovery, rules, params …) and _schema.csv for their columns.

## Who reads it
Camden is doing this himself, mostly alone, in a home garage, for the first time: he has not
crimped a Deutsch terminal before the practice row. He reads each row in the app on his phone
or laptop while doing it. He wants every detail he needs in front of him at that moment: about
the car, the situation and the task - and nothing he has to go and look up. Plain words, short
sentences, no jargon left unexplained the first time (say "DT06-12S, the 12-way grey plug" once).

## What to produce
For EACH work row in your list: one `briefs` row and its `steps` rows, as two draft CSV files in
your scratch folder (never write under any data/ folder, never run git; the overseer loads the
drafts). Use Python's csv module, UTF-8, LF line endings, exactly these headers:

briefs.csv: id,goal,where,time,tools,parts,before,know,done_when,if_not,record
- id: the work row's id.
- goal: one sentence, what is true when the row is done.
- where: "desk", "bench", or the place on the car ("driver footwell and under the dash").
- time: an honest estimate ("20 min", "2 h", "a weekend"); say "confirm" if it is a guess.
- tools: one per line. Name the real tool and size where the record gives it (a crimper that is
  a parts row: "Deutsch size-16 crimper (P037)"; "10 mm socket"; "multimeter on DC volts").
- parts: space-separated ids from 02-electrical's `parts` table that the row uses (they must
  exist: check with `rx7.py sql 02-electrical "select id from parts where id in (…)"`). Only
  that table's ids go here; a 00-CAR part (PT…) or a luxury part (LP…) is named in `know` or
  in a step instead.
- before: one per line: what must be done or true first (the rows it follows, by id and plain
  name; the battery disconnected; the key out), and the safety that applies (the Class-T fuse
  out, eye protection for crimping, jack stands).
- know: one fact per line, each ending with its source in square brackets: a row
  ("[cavities L3-S1 9]", "[fuses F12]", "[00-CAR PT025]", "[D-280]") or a document
  ("[S-002 p.15-12]"). These are the facts about the car and the situation he needs while
  doing it: where the thing is, what colour the factory wire is, what the fuse is, what the
  reading should be, what was decided and why in one clause. A figure nobody has measured ends
  "- confirm". Aim for 4 to 12 lines.
- done_when: the acceptance, measurable or visible.
- if_not: what to do when a result is not as expected (stop and what to check, the recovery
  row, "raise it in the app as a note").
- record: what he enters in the app when done (the row's reply: a tick, a value and its unit,
  a choice), and any other of his rows that take a reading from this work.

steps.csv: id,work,n,do,how,expect,caution
- id: "<work id>.<two digits>" ("E8.01", "E8.02" …); work: the work row id; n: 1, 2, 3 …
- do: one short imperative line ("Disconnect the battery negative").
- how: exactly how. The place on the car; the housing code and what it looks like; the cavity
  number, the wire's colour and gauge, the terminal and the crimper position; the fastener and
  its torque; the order. Write the actual values from the rows (do not say "see the cavities
  table" - he cannot; give the table's content for that step, as a compact list inside the
  cell when there are many: "1 red 18 AWG O3 headlight L · 2 …").
- expect: what he sees, hears or measures when it went right ("12.6 to 13.4 V", "the relay
  clicks", "continuity, under 1 ohm").
- caution: only where a real hazard or an expensive mistake sits at that step.
- 5 to 25 steps per row, as many as the work really has. A row that is one reading may have 3.
  A harness leg has many: cut list, each housing's pin-out, each test.

## The rule that matters most
Nothing in a brief or step is new truth. Every number, colour, cavity, fuse, torque, part
number and location comes from a row or a source document, and `know` says which. Start from
the work row itself (`rx7.py get 02-electrical work <id>` - its item, note, gate) and the rows
it names; follow every id it cites; then the tables. For how the factory car comes apart
(trim, console, dash, seats, connectors' places) read the factory manual scans in
00-CAR/library/docs/fsm-1985-sections/ (1985 workshop manual sections; the Read tool shows PDF pages, 20 per call)
and 00-CAR circuit_paths rows (the 1982 circuits written up), cite source id and page
(00-CAR `sources`: S-002 is the 1985 manual, S-001 the 1982 wiring diagram), and where the
1985 book may differ from his 1982 car say "1985 manual - confirm on the car". Background
only, never authority: 99-ARCHIVE/Electrical (the old v2 install text). The record wins.
Where the record does not hold a detail he needs (a torque, a clip count, a wire colour),
write the step so he is not stuck - "not in the record: note what you find" - and list it in
your report as a gap. Never invent a value to fill a hole. Never state as fact anything
about the physical car that no row or document states.

Do not put a path containing "cad/" in any cell (the record's check refuses it); name a
drawing or script by what it is.

## Before you finish
Validate with a small script: every briefs id is in your list and every list id has a brief;
every step's work is in your list; n runs 1..k without gaps and ids match; goal, done_when and
do are never empty; every id in `parts` exists in 02-electrical parts; no cell contains "cad/".
Report in under 20 lines: rows written, steps per row (min / median / max), the gaps you
found in the record (what a row needed that no table holds), and any row whose note
contradicts a table (say which you followed and why).

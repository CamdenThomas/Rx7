# The two tracks, and the car coming apart once (was CLAUDE.md §1)

**A project whose `work` has a `track` column has two lists** (D-386 → D-405; today
`01-electrical`). Each row's `track` says which:

- **design**: his checklist in working order and every agent row, ready or blocked and by
  what, then the open blocks. Its last two rows are the design review (the review playbook)
  and his freeze ruling.
- **build**: everything physical and everything bought. **Every build row gates on
  `phase:SOURCING`**, which only the freeze moves, so nothing in build starts before the
  design is verified. The freeze does not close design (D-398): a design row opened after
  it gates the build rows it changes, by id.

A new row goes on the track where its work happens: desk, measurement, bench proof or the
agent's work is design; the cart, the car, and the modules' fabrication are build.

**The car comes apart once** (D-387). `_project` names the row that strips the interior
(`car_apart`, S1) and the one that puts it back (`car_back`, E35). Each list is split at those
rows: design Part 1 is everything with the car whole, and S1 waits on all of it; Part 2 is S1,
the measurements that need the car apart, the review and the freeze. Build Part 3 is the car
apart, and Part 4 starts at E35. A row's part is derived from its gate, never typed: a row
that needs the car apart gates on S1. What S1 itself waits on is block `01.12` (2026-09-26).

**His rows are a manual, not a list** (D-533). A project that declares `briefs` and `steps`
(today `01-electrical`) holds, for every open row of his:

- one `briefs` row keyed by the work id: `goal` (what is true when it is done), `where`,
  `time`, `tools` (one per line), `parts` (ids of the project's `parts`), `before` (one per
  line, safety included), `know` (one fact per line, each ending with its source in square
  brackets - `[cavities L3-S1 9]`, `[00-CAR PT025]`, `[S-002 p.15-12]`, `[D-280]` - and an
  unmeasured one says confirm), `done_when`, `if_not`, `record`;
- its `steps` rows, `<work id>.<nn>`: `do` (one imperative line), `how` (the actual housing,
  cavity, colour, gauge, torque, order - never "see the table"; a compact list uses ` · `
  between items or one numbered item per line), `expect`, `caution`.

`check` refuses an open row of his without both. The app's TODO page shows the brief and the
steps, ticks each step on the device only, and takes his answer as before. The writers that
produced the first set are in the project's `tools/steps/` (one folder per phase, each with a
`build.py` that regenerates its drafts from the tables, and `load.py` that replaces the rows
for those work ids and runs `check`): rerun the phase's builder when `cavities`, `pins`,
`fuses`, `relays`, `migration`, `checks` or `parts` change under a step that quotes them.


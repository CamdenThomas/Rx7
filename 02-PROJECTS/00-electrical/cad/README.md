# cad — drawn by hand, outside the record

*Rev 2026-09-21 · owns: the boundary between this folder and the record. It lives inside
`00-electrical`, which owns the ICU; the DCU carrier is drawn here too (D-361).*

**This is not the visual layer.** CLAUDE.md §1 and §9 say the tree has exactly one
generated document and that the visual layer of the record is a separate, later concern
that must not be started yet. Nothing in here is generated, nothing in here renders the
record, and nothing in here reads a CSV at build time. It is a CAD tool being used to draw
a circuit board, in the same category as `02-PROJECTS/01-luxury/firmware/` — an
engineering artefact for one component, not a view of the design.

The fence, in full:

- **This folder is not an area.** No `data/`, no `_tables.csv`, so `rx7.py` does not see it
  at all: `areas()` cannot find it, `check` never reads it, and nothing here can make the
  record invalid or be made invalid by it. It sits beside `data/`, not inside it.
- **The record wins, always.** If a schematic and a row disagree, the row is right and the
  drawing is stale. Nothing in `../data/` cites a file in here as evidence.
- **A fact worth keeping is promoted, not linked** — it becomes a row, and the drawing
  becomes an illustration of the row.
- **Camden ruled this in conversation on 2026-09-12**, as a way to learn KiCad on something
  real before a future project needs it. If it starts to look like the beginning of a view
  layer, it should be deleted, not grown.

| Project | What | Status |
|---|---|---|
| `icu-carrier/` | The ICU carrier board as a KiCad 10 schematic | **drawn, rev 0.02, ERC clean** — see its README |
| `dcu-carrier/` | The DCU carrier (luxury `H-002`) | **not started** — Part B of the guide; connectors ruled (luxury D-362); waits on `V-083`, `V-101`, `W-332`, `H-007` (window drive settled, D-363) |
| `PCB-AND-3D-GUIDE.md` | Step by step, schematic → layout → 3D model → fit test, for each carrier separately | Camden asked for it 2026-09-21 (D-361) |

**Layout is in, as of 2026-09-21 (D-361).** Camden asked for the full PCB and 3D guide for both
boards, which lifts `icu-carrier/README.md`'s old "schematic yes, PCB not yet" (ICU layout was
already his step `F2`). Board layout and the 3D model are part of this folder's job now.
**Ordering boards is still his, and still money** (`F2`, luxury `LP07`), and nothing in here
orders anything. The DCU is the luxury package's board. It is drawn here because the tools, the
conventions and the guide are here, and its spec stays in `01-luxury/data/`.

## Why a schematic at all

The analog front end is currently only describable in prose. `icu_channels.csv` row IC01
carries, in its stage column, *"100 Ω 1 W pull-up from the carrier's 5 V behind jumper J1
(fitted) → node → 15 kΩ / 10 kΩ divider (×0.4, 5 V → 2.0 V) → 100 nF → BAT54S to 3V3 /
GND"*. That is precise, complete, and unreviewable — nobody can read that sentence and see
that a clamp is on the wrong side of a resistor. Drawn, it is one glance.

That is the whole argument, and it is narrow. It does not extend to the harness: wire
gauge, colour, bundles, cavities and cut lengths are the record's job and KiCad has no
model for any of them.

And it earned that on the first attempt, which belongs here where the argument is made: drawing
IC01 turned up that **every BAT54S clamp on the board was the wrong way round** - anode to +3V3 and
cathode to ground. The sentence above is silent on direction and reads perfectly either way round.
The picture is not.

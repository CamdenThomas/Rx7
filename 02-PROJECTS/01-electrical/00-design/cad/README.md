# cad — drawn by hand, outside the record

*Rev 2026-09-22 · owns: the boundary between this folder and the record. It lives inside
`01-electrical`, which owns both carriers - the ICU and, since D-374, the DCU.*

**This is not the visual layer.** CLAUDE.md §1 and §9 say the tree has exactly one
generated document and that the visual layer of the record is a separate, later concern
that must not be started yet. Nothing in here is generated, nothing in here renders the
record, and nothing in here reads a CSV at build time. It is a CAD tool being used to draw
a circuit board, in the same category as `../firmware/` — an
engineering artefact for one component, not a view of the design.

The fence, in full:

- **This folder is not an area.** No `data/`, no `_tables.csv`, so `rx7.py` does not see it
  at all: `areas()` cannot find it, `check` never reads it, and nothing here can make the
  record invalid or be made invalid by it. It sits in `00-design/`, beside `firmware/` and `diagrams/`, and never inside `data/` (moved 2026-09-23, D-386).
- **The record wins, always.** If a schematic and a row disagree, the row is right and the
  drawing is stale. Nothing in `../../data/` cites a file in here as evidence.
- **A fact worth keeping is promoted, not linked** — it becomes a row, and the drawing
  becomes an illustration of the row.
- **Camden ruled this in conversation on 2026-09-12**, as a way to learn KiCad on something
  real before a future project needs it. If it starts to look like the beginning of a view
  layer, it should be deleted, not grown.

| Project | What | Status |
|---|---|---|
| `icu-carrier/` | The ICU carrier board as a KiCad 10 schematic, plus its Teensy socket footprint | **drawn, ERC clean, real Teensy pads (D-377)** — next is `PCB-AND-3D-GUIDE.md` step 1 |
| `dcu-carrier/` | The DCU carrier (`H-002`) | **checklist only, no sheet yet** — `TARGET.md` lists every block from `dcu_channels`; the schematic starts when `V-083`, `V-101`, `H-007` and luxury `W-332` are in (connectors ruled, luxury D-362; window drive settled, D-363) |
| `PCB-AND-3D-GUIDE.md` | A first-timer's step-by-step guide: schematic → footprints → layout → 3D → measure → fit, ICU first | rewritten for a first-time KiCad user 2026-09-22 (D-361) |

**Layout is in, as of 2026-09-21 (D-361).** Camden asked for the full PCB and 3D guide for both
boards, which lifts `icu-carrier/README.md`'s old "schematic yes, PCB not yet" (ICU layout was
already his step `F2`). Board layout and the 3D model are part of this folder's job now.
**Ordering boards is still his, and still money** (`F2` for the ICU, `F5` for the DCU), and
nothing in here orders anything. Both boards are this build's (D-374): their specs are
`../../data/icu_channels.csv` and `../../data/dcu_channels.csv`. Only the loads the DCU drives are the
luxury package's.

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

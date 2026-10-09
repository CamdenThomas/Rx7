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
- **Who draws (D-453).** Camden ruled on 2026-09-12 that he would draw these himself to learn
  KiCad; D-453 lifts that, and the agent draws, lays out and checks the boards too. They are
  still not a view layer: if one starts to look like it, delete it, don't grow it.

| Project | What | Status |
|---|---|---|
| `icu-carrier/` | The ICU carrier board as a KiCad 10 schematic, plus its Teensy socket footprint | **drawn, ERC clean, real Teensy pads (D-377)** — next is `PCB-AND-3D-GUIDE.md` step 1 |
| `dcu-carrier/` | The DCU carrier (`H-002`) | **drawn, ERC clean, real Teensy pads (D-452)** — every pin in `dcu_channels.teensy_pin`, the slow lines on a TCA9539-Q1; next is the layout, after `V-102` and luxury `W-332` for the outline and the mirror stage |
| `panel/` | The control panel's electronics (`H-008`): the 3 × 3 matrix, four encoders, the thumbstick, the ribbon header | **provisional board drawn, DRC clean (Y6, 2026-10-09)** — no processor (D-355); both key styles as alternates, the backlight DNP; the outline is `confirm` until `V-113`, and blocks 01.14, 01.15 and 03.14 pick what is fitted |
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

## Checking the sheets against the record (`check.py`, Y3)

`python3 check.py` (from this folder; `-v` for every pass and the walk it took, `--board icu|dcu|panel`, `--netlists DIR` to reuse exports) runs `kicad-cli sch export netlist` on each sheet, one at a time, and holds the drawing to the record: every pin in `icu_channels.teensy_pin` and `dcu_channels.teensy_pin` on its socket pad and named net, reaching the part the record says (the XIAO's TX, the transceiver's STB, the expander's ports); every `at_the_drop` cavity wired on the board-edge connector and walked through the board to that channel's processor pin; the ribbon against `panel_ribbon` on both boards, with the keys, encoders and thumbstick pins that hang off each conductor and the matrix diodes' direction; `CONVENTIONS.md` §5 (the rails never meet, every BAT54S the right way round); and each functional-block symbol's pin numbers against the vendor pin tables in `pin_tables.csv` (part, package, pin, name, source URL and page). It prints one `board:ref:pin expected X got Y` line per disagreement and a summary line per board; exit 0 clean, 1 any mismatch, 3 kicad-cli missing or a sheet unreadable. `../firmware/tests/run.sh` runs it after the can_map check, so a schematic that disagrees with the record fails the firmware suite (skipped with a notice when kicad-cli is absent). The record wins: a mismatch is fixed on the sheet, or in `pin_tables.csv` from the datasheet, never by editing the check to pass.

First run, 2026-10-09: every record pin on every sheet matched. The 106 mismatches it reports are all pin-table ones on the DCU - U5-U8 BTS3011TE, U9 BTT6050, U10 BTT6200 and U11 DRV8962 still carry functional-block pin numbers (Y5 redraws them on their real packages) - and the ICU's U8 XIAO, whose symbol has EN and BOOT pins the module does not expose as castellations (IC24).

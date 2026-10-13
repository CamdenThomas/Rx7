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
| `climate-unit/` | The climate control unit (D-479, D-480): a parametric FreeCAD mock-up of its insides and its case - face, panel board, DCU carrier, upper connector board, four DT13s in two rows | **mock-up built, fit check clear, self-test 31 of 31 (Y14, 2026-10-11)** - one table of numbers (`unit_params.py`), nothing measured (R11); not the print-ready model (F1) |
| `icu-unit/` | The ICU as one unit (D-491): a parametric FreeCAD mock-up - the 12.3-inch display behind its bezel, the display plate with the BT817 board and the chain-ii driver boards, the ICU carrier behind (or under) them with the radio's RF window, the page button, DP-ICU-A / -B in the rear plate | **mock-up built, fit check clear, self-test 28 of 28 (Y19, 2026-10-12)** - one table of numbers (`unit_params.py`); 335 x 136.5 face, 206.6 deep with plugs (182.5 carrier below); nothing measured (R11), `C4` / `M-1` the envelope; not the print-ready model (F1) |
| `icu-carrier/` | The ICU carrier board as a KiCad 10 schematic, plus its Teensy socket footprint | **provisional board placed, routed, poured and 3D-modelled, DRC clean (F9 / F10, 2026-10-09)** — 110 × 80 mm is `confirm` until `C4` / `F11`; guide step 8 reached, the fit test is `F11` |
| `dcu-carrier/` | The DCU carrier (`H-002`) | **provisional board placed, routed, poured and 3D-modelled, DRC clean (Y5, 2026-10-09)** — every pin in `dcu_channels.teensy_pin`, the slow lines on a TCA9539-Q1; 180 × 80 mm is `confirm` until `V-102` and luxury `W-332`; `Y11` (2026-10-09) drew the open blocks' worst case DNP: a second expander, the A/C clutch stage and pressure ADC, the radar alert input, the third comfort ground; sheet and board rev 0.04 carry the 26-way ribbon header (D-458): `Y12` (2026-10-11) re-laid the top-left block for it, H1 now at (4, 15) |
| `panel/` | The control panel's electronics (`H-008`), the climate unit's face (D-492): the centre encoder with push, the screen's header, four keys and two window switches on a 4 × 3 matrix, two seat encoders, the IS31FL3236A with 24 LEDs, the 26-way ribbon `J1` and the left plate's 2 × 6 header `J3` | **rev 0.04 provisional board drawn, routed and poured to D-492 (Y20, 2026-10-13)** — ERC 0, DRC 0 / 0 / 0 parity, `check.py --board panel` 0 mismatches; 180 × 84.76 from the mock-up, `confirm` until `V-113`; the window switches drawn DPDT (the record's DRV up / down share no row or column) and the screen's supply left to `JP1`, both in its README; no processor (D-355), ordered with the DCU's (D-459) |
| `upper-board/` | The climate unit's upper connector board (`P195`, D-480, D-492): `DP-DCU-D` to leads for the carrier's J6-J8, J5 and J3, `DP-DCU-E` straight through to a 2 × 6 header for the panel board's plate header; no active parts | **provisional board drawn, routed and 3D-modelled, ERC and DRC clean, `check.py --board upper` 0 mismatches (Y15, 2026-10-12)** — 130 × 36 mm and the two M3 holes from the mock-up (Y14), `UPPER_D` 30 → 36 so the headers fit (its README says why); `confirm` until `V-102` / `F11` |
| `PCB-AND-3D-GUIDE.md` | A first-timer's step-by-step guide: schematic → footprints → layout → 3D → measure → fit, ICU first | rewritten for a first-time KiCad user 2026-09-22 (D-361) |
| `enclosure_lib.py`, `enclosure_extract.py`, `<board>/enclosure/` | The three enclosures as parametric FreeCAD scripts: `enclosure_extract.py` writes `board.json` from the board, `make_enclosure.py` builds base, DT13 plate and lid (ASA, TE 114-151046 cut-outs, lid gasket groove) and fit-checks them against the board STEP; `freecadcmd make_enclosure.py`, rc 0 = clear | **built on the provisional outlines, fit check clean (Y7, 2026-10-09)** — envelopes `C4` / `V-102` / `V-113` are parameters, `confirm`; STEP / STL outputs are generated and ignored; rebuilt at `F11`, printed at `F1` (CK27) |

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

`python3 check.py` (from this folder; `-v` for every pass and the walk it took, `--board icu|dcu|panel|upper`, `--netlists DIR` to reuse exports) runs `kicad-cli sch export netlist` on each sheet, one at a time, and holds the drawing to the record: every pin in `icu_channels.teensy_pin` and `dcu_channels.teensy_pin` on its socket pad and named net, reaching the part the record says (the XIAO's TX, the transceiver's STB, the expander's ports); every `at_the_drop` cavity wired on the board-edge connector and walked through the board to that channel's processor pin; the ribbon against `panel_ribbon` on both boards, with the keys, encoders and thumbstick pins that hang off each conductor and the matrix diodes' direction; `CONVENTIONS.md` §5 (the rails never meet, every BAT54S the right way round); and each functional-block symbol's pin numbers against the vendor pin tables in `pin_tables.csv` (part, package, pin, name, source URL and page). On the upper connector board, which has no processor, every cavity of `DP-DCU-D` and `DP-DCU-E` is held to its `state` (wired, or bare behind a plug), to a net of its own, and to what its `src_note` names: the header for the carrier's J6-J8 / J5 / J3 lead pin for pin, or the `panel_ribbon` line, named as that line. It prints one `board:ref:pin expected X got Y` line per disagreement and a summary line per board; exit 0 clean, 1 any mismatch, 3 kicad-cli missing or a sheet unreadable. `../firmware/tests/run.sh` runs it after the can_map check, so a schematic that disagrees with the record fails the firmware suite (skipped with a notice when kicad-cli is absent). The record wins: a mismatch is fixed on the sheet, or in `pin_tables.csv` from the datasheet, never by editing the check to pass.

First run, 2026-10-09: every record pin on every sheet matched. The 106 mismatches it reports are all pin-table ones on the DCU - U5-U8 BTS3011TE, U9 BTT6050, U10 BTT6200 and U11 DRV8962 still carry functional-block pin numbers (Y5 redraws them on their real packages) - and the ICU's U8 XIAO, whose symbol has EN and BOOT pins the module does not expose as castellations (IC24).

# cur-assembly - the Control Unit Remote (CUR), mocked up

*Rev 2026-10-13 (Y25, first pass) · owns: what this folder is, what it may claim, and how to rebuild
it. Read `../../../README.md` first: it is the fence. The design is the record's (D-514, D-492, D-499,
D-504, parts P198 / P199 / P204 / P156 / P200, block 01.41); this is a drawing of it.*

> **D-582 (2026-10-14).** The CUR's link to the Control Unit is DP-DCU 36-47 in the unit's one rear connector, not DP-DCU-E; nothing at the CUR's end changes.

## What it is

D-514 made the left plate a unit of its own: the **Control Unit Remote**, a small sealed box like the
Control Unit (D-479) for the dash face left of the wheel. The plate's board (`../cur-board`, rev 0.02,
Y22) stands on four standoffs behind a faceplate; the face carries the two wink caps, the hatch and
fuel-door key caps, the mirror stick's well and knob; the board's two leads - J1's twelve lines to the
Control Unit's DP-DCU-E (D-492) and J2's four wink lines to the dash post (D-504) - leave at the back
by receptacles or a sealed grommet. Which is block 01.41, which waits on his answer; **the default is
its recommendation: two receptacles**, DP-CUR (a DT13-12PA for J1) and DP-CUR-B (a DT13-06PA for J2),
both provisional codes. Sixteen lines do not fit one 12-way.

This folder is the **mock-up**: insides and case as one parametric FreeCAD build, driven by one table of
numbers, that rebuilds when a number changes and says in words what no longer fits - the climate
unit's method (`../cu-assembly`), and where that code is generic, its code (below). It is **not the
print-ready model**.

**R11 applies to all of it: nothing here has been measured, and nothing is in hand.** The opening left
of the wheel, what the CUR fastens to, the switches (P204), the stick (P156), the caps, the cable
(P200), the grommet and the receptacle are all unknown; every dimension in `control-unit/control-unit-remote/data/cur_assembly_params.py` carries a
`confirm`.

## Change a number, rebuild

Every number is in **`control-unit/control-unit-remote/data/cur_assembly_params.py`**, one commented row each. Edit a value, then:

```
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 00-design/tools/mockup.py --pass cur-assembly
```

Exit 0 built and clear · 1 a fit rule failed (nothing is built; one sentence per problem naming the
parameter and which way to move it), an interference, or a failed check · 3 a crash.

| To get | Set |
|---|---|
| two receptacles, DP-CUR for J1 and DP-CUR-B for J2 (the default, 01.41's recommendation) | `RECEPTACLES` as it stands |
| one receptacle for J1, the wink lead through a grommet beside it | `RECEPTACLES = [("DP-CUR", "DT13-12PA", ("J1",))]` |
| no receptacle, both leads captive through a grommet | `REAR = "grommet"` |
| the board or the rear row elsewhere in the box | `BOARD_DX` / `BOARD_DZ`, `REAR_DX` / `REAR_DZ` (the box grows round them) |
| a larger face | `FACE_W` / `FACE_H` (None = the body + `BEZEL_OVERLAP`) |
| longer caps, the board further back | `BOARD_GAP` (None = the least the switches allow) |
| no ears: a box that slides in from the front | `EARS = []` |
| the opening checked | `ENVELOPE`, once it is measured |

**The self-test** rebuilds under the parameter sets in `the parameter table's SELFTEST`, writes no file, and holds
each to its stored outcome (built clear, built with a failing check, refused). About 5 s.

```
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 00-design/tools/mockup_selftest.py --pass cur-assembly
```

## What it reads, nothing typed

- **`../cur-board/cur-board.kicad_pcb`**, parsed as text at every build (no KiCad needed): the outline,
  corner radius and thickness; the four M3 holes (the front frame's standoffs); and every footprint's
  place. The **wink caps** are the 17 x 15 dashed F.Fab outline of the P204 placeholder (SW3 / SW4 at
  their 19 mm pitch), the switch body its 12 x 12 F.Fab square. The **key caps** take that same outline
  (`KEY_CAP_FROM`: the sketch draws all four keys 17 x 15), centred on the 6 x 6 tactiles' bodies
  (SW1 / SW2). The **stick's well** is JS1's 28 mm F.Fab circle, its body the 26 x 26 square. Each **LED**
  is lit through the cap or the well it sits in or beside (within `LED_LIT_REACH`); one that no opening
  lights gets a window and a light pipe. The **headers** J1 / J2 are their courtyards, and the conductors
  each carries are their pads. Move a part on the board and the face follows.
- **`control-unit/data/cu-carrier-probe.json`** and `board.json`: the DT13's flange, housing section, flange
  seal and nose, as the DCU enclosure build read them from TE's models; **`00-design/tools/enclosure_lib.py`**:
  TE's panel cut-out (114-151046) and its 6.25 mm panel limit.
- **`tools/cu_assembly.py`**, imported as `CU`: the 2D opening arithmetic, the stand-in DT13
  (`_standin_dt13`), the case builder (`build_case`: body with the beam the lid lands on and the lid's
  lugs, the rear plate in its channel with TE's cut-outs, the lid's cord-gasket groove, the front frame
  with its standoffs and webs), the interference test and the drawing helpers. A change there changes
  the CUR; this self-test catches it.

It writes nothing outside this folder.

## What it writes

| File | What | In git |
|---|---|---|
| `cur-assembly.FCStd` | everything as named objects: group `Insides` (faceplate, caps, switches, stick, board, headers, receptacle or grommet and leads, and `Keepouts`), group `Case` (body, rear plate, lid, front frame) | no |
| `cur-assembly.step`, `cur-assembly-body.step`, `-rear_plate`, `-lid`, `-front_frame` | the assembly (parts only) and one STEP per case part | no |
| `control-unit/control-unit-remote/data/cur-assembly-report.json` | every derived dimension, every check, the parameters, the `confirm` list, and `connectors`: each receptacle's code and its place on the rear face (the export reads the same from `unit_lib.connectors`) | no |
| `view-front.svg`, `-back`, `-side`, `-top` | line drawings by hidden-line projection; blue = room kept clear; on the front view, orange = the board's outline | yes |

`export_glb.py --only cur` (§13 of the design README) writes `cur.glb` from the same calls: `case:` and
`inside:` nodes, the board and what the board's glb draws (J1, J2, the tactile keys) left to the
`cur-board` child, which it places from `tools/cur_assembly.py's export_boards`.

## How it is laid out

Frame (the Control Unit's): X across the face (0 = its left edge from the driver's seat), Y back from
the face's front, Z up from its bottom edge.

- **Across and up.** The body is the inner room plus `WALL` a side, `FLOOR` and `LID`; the inner room is
  whichever is larger of the board with `GAP` round it and the rear row with its margins. The face is
  the body plus `BEZEL_OVERLAP` a side. One height front to back.
- **Going back.** Faceplate · front frame ring (`FRAME_D`) and four standoffs to the board's holes ·
  the board at `BOARD_GAP`, derived from the tallest switch under a cap standing `CAP_PROUD` · the room
  behind the board for J1 / J2 and their mated plugs (`BOARD_BACK_H`) · the beam the lid lands on ·
  the room for the wires to turn (`REC_WIRE_L`) · the receptacle's housing (`REC_BODY_L`) and flange ·
  the rear plate in its channel · the lip. In grommet mode the room behind the board ends in
  `LEAD_BEND_IN` and the grommet's inner lip.
- **The receptacle** mounts through TE's cut-out from inside, the Control Unit's way; its flange seal
  (probed 0.51 mm proud of the flange) is drawn pressing into the plate, and the check measures that
  squeeze. **The grommet** fills a round hole, a lip each side, a bore per lead; the captive leads are
  drawn 40 mm out.
- **The ears** are flat tabs on the side walls at the body's front, a screw along Y each, into a bracket
  behind the dash skin. Provisional: with them the box cannot slide in from the front, and the report
  says so.

Not drawn: the leads inside from the headers to the receptacle, the joint between the front frame and
the body, the caps' retention, any fillet, draft or print orientation.

## What the default build says (2026-10-13)

- **Size.** Body 108.5 x 63 (across, the two receptacles' flanges side by side with `GAP`; up, the board's
  56 with `GAP` and 2.5 mm walls), face 112.5 x 67, 128.5 across the ears. Box 86.7 deep from the face's front to the rear lip, 96.3 to the receptacles' tips, 164.7
  with a mated plug and its cable bend. One receptacle and a grommet: 107 wide, as deep. Grommet
  mode: 66.7 deep, 104.7 with the leads drawn.
- **Face.** The four caps 19 mm apart across and 18 mm up and down, as the board has them; 1.4 mm of
  face between neighbouring cap openings. The well at X 80. LED1-LED4 are lit through their caps, LED5
  (the mirror symbol, 1.5 mm outside the well's edge on the board) through the well: a 3 mm window
  there would touch the well, and `LED_LIT_REACH 0` is refused for that.
- **The rear: two receptacles.** DP-CUR (DT13-12PA) carries J1's 12 conductors on 12 ways, DP-CUR-B
  (DT13-06PA) J2's 4 on 6, side by side at X 34.3 and 86.1, Z 33.5, on the rear face (`control-unit/control-unit-remote/data/cur-assembly-report.json`
  `connectors`). One DT13-12PA for both - the first brief - builds with its conductor check failing
  (16 on 12); the self-test keeps that set.
- **Front install: no** while the ears stand 10 mm out; `EARS = []` builds clear and slides in.

## The `confirm` list

The report prints the live list with each value: every dimension in the table except the numerical
slack - the opening (`ENVELOPE`, `FACE_*`, `BEZEL_OVERLAP`), the caps and switches (`CAP_*`,
`WINK_SW_H`, `KEY_SW_H`), the stick (`STICK_*`), the LEDs (`LED_*`), the board's depth and room
(`BOARD_GAP`, `BOARD_BACK_H`, `BACK_PARTS`, `HEADER_PLUG_H`), the rear (`REAR`, `RECEPTACLES`, `LEADS`,
`REC_*`, `GROMMET_*`, `PLUG_*`, `CABLE_BEND`), the case (walls, plate, inserts, gasket), the ears.

## Files

| File | What |
|---|---|
| `control-unit/control-unit-remote/data/cur_assembly_params.py` | the parameter table, the leads, the receptacles, the back parts, the self-test's sets and their expected outcomes |
| `tools/cur_assembly.py` | `read_board` (the KiCad parser), `load_source`, `derive`, `validate`, the builders, `check`, `connectors` / `export_boards` (what the export reads), the writers |
| `tools/mockup.py` | the one command |
| `tools/mockup_selftest.py` | the self-test's command |

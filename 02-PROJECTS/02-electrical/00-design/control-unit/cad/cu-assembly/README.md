# cu-assembly - the Control Unit, mocked up

> **OUTDATED by the overhaul (D-612).** This is the last drawn state from before the boxes: the CU's connector is the DRC 64 with a DTP comfort inlet (D-594, D-612), the seats' heat and cool are its + side switches and the radar receiver is inside it (D-597), the face is the eighth pass (D-602), the CUR is on four I2C wires (D-604). It is kept as it is until row Y70 redraws it; the brief is `00-design/diagrams/overhaul-plan.html`, and the record (`../data/`) is what it must match.

*Rev 2026-10-14 (Y53: single-DIN tall with one rear header, D-582; before it Y40, the case made like
the head unit, D-542; Y14, the one-height unit) · owns: what this folder is, what it may claim, and
how to rebuild it. Read `../../../README.md` first: it is the fence. The design is the record's
(D-479, D-582, `housings` DP-DCU, parts P152 / P220; the head unit is luxury's LP55); this is a
drawing of it.*

## What it is

D-479 made the climate control one sealed unit built like a stereo head unit: the faceplate and its
dials on the front, the control panel's board right behind it, the DCU carrier lying flat behind
that, and nothing outside but sealed connector halves in the rear wall. D-582 (Camden, 2026-10-14)
made it **single-DIN tall with one connector**: every conductor the unit has - 48 of them - leaves
through one Molex CMC 48-way hybrid header on the carrier's rear edge, so the second row of D-480
and its upper board are gone, and the empty bands above and below the controls go with them.

This folder is the **mock-up**: the insides and the case as one parametric FreeCAD build, driven by
one table of numbers, that rebuilds when a number changes and says in words what no longer fits.
It is **not the print-ready model** (that is F1).

**The default unit (D-582).** One row: the carrier, and on its connector edge `REAR_HEADER`, a
stand-in block for the CMC 48 header (no model of it is in the tree; every number in that row is
confirm until Molex's drawing is read at Y54). The row needs a body only 40 tall; the face is as
tall as the sketch's controls need with `SKETCH_CROP` on - their empty bands cut away, each control
still `CONTROL_EDGE` from the edge and clear of the frame behind - which is 181 x 59.3, over a body
188 x 56.3 (it was 192 / 181 x 97 over 100). The face stands 1.5 proud of the body top and bottom,
as a single-DIN nose does of its chassis, and is set in 3.5 a side as the head unit's is; the width
and the side mounting are still the head unit's (D-542 → D-582), the height no longer. The panel
board is cut to the face (`PANEL_H` None, 180 x 47.3): the drawn one (84.76 tall) is redrawn at Y55.
The report always says which unit was built: `front install: yes` or `no - …`.

The two-row unit of D-480 / D-542 is still a parameter set away (`_TWO_ROWS` in `control-unit/data/cu_assembly_params.py`:
`REAR_HEADER` None, `UPPER_CONNECTORS` both, the head unit's height), and the self-test keeps every
rule written for it.

**R11 applies to all of it: nothing here has been measured.** No opening is measured and none is a
gate (D-542). The head unit's sizes are Pioneer's published ones, not the unit in hand. The face is
a sketch he is still changing (I-001 to I-006), and no knob, key, display, plug or insert is in
hand. The CMC header is a stand-in from a listing's outline. Everything else is a parameter, and
most are marked `confirm`.

## Change a number, rebuild

Every number is in **`control-unit/data/cu_assembly_params.py`**, one commented row each: name, value, unit, what it is,
and why it is a guess. No other file holds a dimension. Edit a value, then:

```
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 00-design/tools/mockup.py --pass cu-assembly
```

Exit 0 built and clear · 1 a fit rule failed, an interference, or the measured envelope refused ·
3 a crash. The fit rules run before anything is drawn. When one fails nothing is built, the last
good build's outputs are removed so they cannot be mistaken for this one, and the report gives one
sentence per problem naming the parameter and which way to move it, for example:

> ROW_PITCH 32 is too small: raise it to at least 40.3. What sets that, largest first: a DT13
> stands 37.76 above its board's underside and the upper board needs UPPER_BOT_H 2.5 under it …

After a build, every inside solid is checked against every case solid, and the inside parts
against each other; an interference names the feature (`lid lug 4`, `side screw boss, right wall`)
and the parameters that move it.

The numbers most likely to be turned:

| To get | Set |
|---|---|
| the single-DIN unit with one rear header (the default, D-582) | as it stands: `REAR_HEADER` set, `FACE_H` None, `SKETCH_CROP` True |
| the two-row unit at the head unit's height (D-480 / D-542) | the `_TWO_ROWS` set in `control-unit/data/cu_assembly_params.py` |
| the CMC header's real outline, once Molex's drawing is read | the `REAR_HEADER` row |
| the head unit measured, once it is bought | the `HEAD_UNIT_*` block: the six sizes, and the two Pioneer does not publish - `HEAD_UNIT_SIDE_HOLES` (then the side bosses stand on its pattern) and `HEAD_UNIT_NOSE_R` (then the face's corners are its) |
| the sketch kept whole (no crop) | `SKETCH_CROP` False: a face of 60 |
| a face that stands proud and covers the opening itself (the case before D-542) | `BEZEL_OVERLAP_X` and `BEZEL_OVERLAP_Z` positive, e.g. `2.0` |
| the stepped unit: a low face, the rear rising behind the dash | `FACE_H` lower than the body needs AND `PANEL_H` None - the drawn panel board is 84.76 tall and needs a face of 89.76 or more, so a low face is a panel board drawn again, lower; `FRONT_L` is then the length of the low front section |
| the control block higher or lower on the face | `CONTROLS_ANCHOR` = `"centre"`, `"top"` or `"bottom"` (the drawn panel board has it centred) |
| a lower unit | `FACE_H`, then `ROW_PITCH` (least 40.3), `BOSS_H`, `TOP_GAP` |
| a narrower unit | `CARRIER_W` (its connector edge needs about 163) and `PANEL_W`: two boards drawn again |
| the left plate's connector not fitted | `fitted` False on its row of `UPPER_CONNECTORS` |
| an opening checked | `ENVELOPE` - no opening is a gate (D-542), so this is for the dash's builder |

**The self-test** rebuilds under the parameter sets in `the parameter table's SELFTEST` and writes no file.
Each set is stored with the outcome it must have - built clear, built with a failing check, or
refused in words - and the self-test fails (exit 1) when any outcome differs, so an edit that
changes what the model does is caught. If the change is meant, change the stored word.

```
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 00-design/tools/mockup_selftest.py --pass cu-assembly
```

## What it reads

`control-unit/data/cu-carrier-board.json` (outline, holes, connector positions) and `probe.json`
(each DT13's flange, housing and height), and `../cu-carrier/cu-carrier.step` when it is there:
then the real board, with every part on it, goes in the box. Without the STEP, with
`CARRIER_STEP` False, or when `CARRIER_W` / `CARRIER_D` are not the drawn board's, plain blocks
of the same sizes stand in and the report says so. `probe.json` is read as it is: if the board
moves, rebuild the DCU enclosure first so the probe is fresh. `../panel/cu-face-board.kicad_pcb` is read
as text for its outline only: `PANEL_W` / `PANEL_H` are typed, and the report notes it when they
are not the drawn board's. It writes nothing outside this folder.

`tools/cu_assembly.py` is also the CUR mock-up's (`../cur-assembly` imports `build_case` and the helpers): after
a change to it, run that folder's self-test too.

## What it writes

| File | What | In git |
|---|---|---|
| `cu-assembly.FCStd` | everything as named objects: group `Insides` (faceplate, each control, panel board, carrier, upper board, connectors, standoffs, and a sub-group `Keepouts` for the rooms kept clear and the mated plugs), group `Case` (body, rear plate, lid, front frame). Opens in the FreeCAD GUI | no |
| `cu-assembly.step` | the assembly: parts only, no keep-outs | no |
| `cu-assembly-body.step`, `-rear_plate`, `-lid`, `-front_frame` | one per case part | no |
| `control-unit/data/cu-assembly-report.json` | every derived dimension, every check, the parameters, the `confirm` list | no |
| `view-front.svg`, `-back`, `-side`, `-top` | line drawings by hidden-line projection; blue = room kept clear; on the front view, orange = the sketch's 180 x 60 control block, so the spare face round it shows. The carrier is drawn as blocks here (TE's models break the projection) | yes |

## How it is laid out

Frame: X across the face (0 = the left edge from the cabin), Y back from the faceplate's front,
Z up from the faceplate's bottom edge.

With the face set in from the body, the body's left side is at X -3.5 and its underside at Z -1.5.

- **Height.** The least body is what the two rows need - floor, bosses, `ROW_PITCH`, the upper
  DT13, `TOP_GAP`, the lid - and that is never typed. The body is `FACE_H` less 2 x
  `BEZEL_OVERLAP_Z`: 100 under the head unit's 97 face, which is 3.64 more than the rows need on
  `BOSS_H` 8.6; the spare is under the lid. With `FACE_H` None the face is the least body plus
  2 x `BEZEL_OVERLAP_Z` (or the least the control block needs, if that is more). Either way
  there is no step.
- **Behind the face**: the front frame (a ring behind the faceplate, four standoffs to the panel
  board), the panel board `PANEL_GAP` behind the faceplate, and the room kept behind it. The
  faceplate reaches `BEZEL_OVERLAP_X` past the body at the sides and `BEZEL_OVERLAP_Z` at the top
  and bottom; both are negative, so it is set in and the front frame shows round it as a head
  unit's chassis shows round its nose. Where it is set in further than the wall is thick (the
  sides) the frame's opening is `FRAME_LAND` inside the face's edge, so the faceplate's rim always
  rests on plastic. Its corners are rounded `FACE_R`.
- **The panel board** is the drawn one, `PANEL_W` x `PANEL_H` = 180 x 84.76, centred on the face.
  It was drawn for a 192 x 96.76 face with the control block centred on both; centred on the 181 x
  97 face the block is centred on both again, so every switch still meets its hole. It has 1 mm
  to each side wall, as the carrier has, and its four screws come 4.5 from the face's side edges.
- **Behind that**: the carrier on four bosses, its connector edge to the rear; the upper board
  `ROW_PITCH` above it on two standoffs, its connector edge flush.
- **Rear plate**: slides into a channel in the walls and floor; every fitted DT13 mounts through
  TE's cut-out from inside. A reserved position gets no cut-out: its flange zone is kept clear
  inside and its outline is scribed outside.
- **Lid**: flat, flush with the roof, with the cord-gasket groove (1.6 x 1.2) on the walls'
  centre lines in one plane. Its front edge lands on a beam under the roof, `RIM_H` tall, placed
  straight behind the room kept for the panel board; the carrier drops in from above behind that
  beam, which puts it 3 mm further back than `CARRIER_FRONT_GAP` alone would (`RIM_H` 0 takes the
  beam and the 3 mm away). Its four screw lugs stand inside the walls.
- **Fixing**: two insert bosses inside each side wall, head-unit style, for the head unit's own
  screw (`SIDE_SCREW_D`, M5) so one pair of brackets can carry both. Where they stand is
  `SIDE_SCREWS` - placeholders - until the head unit's pattern is measured into
  `HEAD_UNIT_SIDE_HOLES`; then they stand on that, a hole with no wall behind it is refused in
  words, and one that lands on a part fails the interference check. Both lists are (back from the
  body's front face, up from its underside).
- No grommet and no ribbon notch: the ribbon runs inside from the panel board's header to the
  carrier's J4.
- **The stepped unit** (a typed `FACE_H` lower than the body): the first `FRONT_L` behind the
  face is the face's height, a step wall rises behind it, and the lid covers the tall rear. The
  carrier is then where `CARRIER_FRONT_GAP` puts it, and a `FRONT_L` that would put the step wall
  over it is refused.

Not drawn, on purpose: the ribbon and the inside leads from the upper board to J3 / J5-J8, the
joint between the front frame and the body, the faceplate's own fixing detail, draft and print
orientation, any fillet.

## Against the head unit (D-542, Y40)

The head unit is luxury's LP55, the Pioneer DMH-W4660NEX. Its sizes are from Pioneer's Operation
Manual for the DMH-WT8600NEX / WT7600NEX / WC6600NEX / W4660NEX / W4600NEX
(`<OPM_DMHWC6600NEXUC_EN_B>`), p.137, Specifications: "Chassis (D): 178 mm x 100 mm x 87 mm",
"Nose: 171 mm x 97 mm x 3 mm" (the copy PK037 cites, read 2026-10-13). Pioneer's Installation
Manual for it was not found, so the mounting rows are weaker: M5 is a retailer's box list ("Pan-head
ISO screws (M5 x 9mm)", seen only in a search result) and what Pioneer's other receivers use; "no
sleeve" is another retailer's box list; the side-hole pattern and the nose's corner radius are
published nowhere found. **Every figure is `confirm` until the unit is in hand.** The report
prints this table from the model at every build (`control-unit/data/cu-assembly-report.json`, `against_head_unit`).

| | Head unit | This unit | Differs by | What would close it |
|---|---|---|---|---|
| face height | 97 | 97 | 0 | - |
| face in front of the body | 3 | 3 | 0 | - |
| face set in from the body, each side | 3.5 | 3.5 | 0 | - |
| face set in from the body, top and bottom | 1.5 | 1.5 | 0 | - |
| body height | 100 | 100 | 0 | - (the two rows need 92.76 on bosses of 5; the 7.24 over is shared, half under the carrier, half under the lid) |
| body width, which is also bracket to bracket | 178 | 188 | +10 | The body is the carrier, 180, plus `GAP` 1 and `WALL` 3 a side, and the panel board is 180 too. A 178 body needs both at 170 or less: the DCU carrier laid out again narrower (its connector edge needs 162.3) and the panel board with it - two boards drawn again and a second order (D-542 says not now). Thinner walls alone reach 185. Until then one pair of brackets carries both with a 5 mm joggle each side, or a 5 mm spacer each side of the head unit |
| face width | 171 | 181 | +10 | follows the body. On a 171 face the sketch's control block, 180 wide, reaches within 1.5 of the face's edge (6.5 now): the window switches come in a little or the block is drawn again - his sketch, his call |
| body depth, its front to the rear plate's outer face | 87 | 119.56 | +32.56 | The stack behind the face: 8 to the panel board, 1.6 board, 16 kept behind it, 7 for the lid's beam and the gaps, the carrier 80, 3.96 flange, 3 plate. `RIM_H` 0 and `CARRIER_FRONT_GAP` 0 take 7 off and no more; the rest is a carrier 47 deep or less, or one stood on edge - a different board. Depth is not a gate (D-542) |
| depth with plugs and cable bend, behind the body's front | not published | 199.56 | ? | measure the head unit with its harness plugged; `PLUG_L` and `CABLE_BEND` are guesses here too |
| face corner radius | not published | 2 (a guess, `FACE_R`) | ? | measure it on the unit into `HEAD_UNIT_NOSE_R` |
| side screw | M5 (weak source) | M5 | 0 | try the screw in the unit |
| side holes, each side | not published | (47, 42) and (97, 42), placeholders | ? | measure each hole on the unit - back from the chassis's front face, up from its underside - into `HEAD_UNIT_SIDE_HOLES`, rebuild; a hole this unit has no wall for gets a hole of its own in the bracket |
| DIN sleeve | none | none | 0 | - |

What to measure, on the head unit, when it is bought: the six sizes above, each side hole's place
and thread, the nose's corner radius, and the depth with its plugs in.

## What the default build says (2026-10-13)

- **Front install: yes.** One height, 188 x 100, behind a 181 x 97 face set in 3.5 a side and 1.5
  top and bottom.
- **Width.** The carrier is 180 wide, so the body is 188 and the face 181 - 1 mm wider than the
  sketch's 180. `FACE_W 180` is refused with the two ways out: a wider face, or a narrower
  carrier.
- **Height.** A DT13 stands 37.8 mm above the underside of its board, so the upper board must sit
  at least 40.3 mm up (the first brief's 32 cannot be built). At `ROW_PITCH` 42 the rows need a
  body 92.76 mm tall on bosses of 5 - not the 75 D-480 estimated - and the head unit's 100 is
  7.24 more: `BOSS_H` 8.6 puts half under the carrier, so the carrier, the rows and the ribbon
  keep their places against the panel board. The face is 37 mm more than the sketch's 60; centred,
  the control block has 18.5 mm of bare face above and below it.
- **Depth.** 124.6 mm from the face's front to the rear lip, 134.3 to the receptacles' tips,
  202.6 with a 50 mm plug and 30 mm of cable bend. Unchanged: the boards set it.
- **Ribbon.** 20 mm in a straight line between the two header faces: a short jumper, with two IDC
  plugs to fit in that room.
- **Upper board standoffs.** The carrier rev 0.04 has no holes for them. The default spots are
  clear of its parts, not of its tracks (Y15).
- **The stepped unit** is no longer one number away: the drawn panel board is 84.76 tall, so
  `FACE_H 64` is refused until `PANEL_H` is None (a panel board drawn again, lower). Then: face
  181 x 64, front section 67 tall, rear 96.36; `front install: no - the rear is 29.36 mm taller
  than the face covers`. The self-test also still builds it on the case as it was before D-542.

## The `confirm` list

The report prints the live list with each value. As of this revision: the ten `HEAD_UNIT_*` rows
(published figures, or not published at all) and what follows them - `FACE_W`, `FACE_H`, `FACE_T`,
`BEZEL_OVERLAP_X`, `BEZEL_OVERLAP_Z`, `FACE_R`, `SIDE_SCREW_D`, `SIDE_SCREWS` · `ENVELOPE`,
`FRONT_L` (no opening is measured, and none is a gate, D-542) · `CONTROLS`,
`CONTROLS_ANCHOR`, `KNOB_PROUD`, `KNOB_FLOAT`, `KNOB_HOLE_D`, `KNOB_SHAFT_D`, `KEY_PROUD`,
`KEY_CLEAR`, `PADDLE_PROUD`, `PADDLE_CLEAR`, `SCREEN_T`, `SCREEN_BORDER` (the face is a concept;
no control is chosen) · `PANEL_GAP`, `PANEL_MARGIN`, `PANEL_BACK_H`, `PANEL_RIBBON_X`,
`PANEL_RIBBON_Z` (the panel board's parts and header, not measured) · `CARRIER_W`, `CARRIER_D`,
`CARRIER_TOP_H` (as drawn, no part in hand; the Teensy on its socket unmeasured) · `ROW_PITCH`,
`UPPER_BOT_H`, `UPPER_W`, `UPPER_D`, `UPPER_STANDOFFS` (the upper board is not drawn, Y15) ·
`PLUG_L`, `CABLE_BEND`, `PLUG_GROW`, `PLUG_ROW_CLEAR`, `PLUG_SIDE_CLEAR` (no plug measured) ·
`INSERT_BORE`, `INSERT_DEPTH`, `SIDE_INSERT_BORE`, `SIDE_INSERT_DEPTH` (against the inserts and
the screw bought).

## Files

| File | What |
|---|---|
| `control-unit/data/cu_assembly_params.py` | the head unit's block, the parameter table, the control table, the upper row, the self-test's sets and their expected outcomes |
| `tools/cu_assembly.py` | `derive` (every position), `validate` (the fit rules), the builders, `check`, `against_head_unit`, the writers. Also imported by `../cur-assembly` |
| `tools/mockup.py` | the one command |
| `tools/mockup_selftest.py` | the self-test's command (`freecadcmd` passes a script its own arguments only after `--pass`) |

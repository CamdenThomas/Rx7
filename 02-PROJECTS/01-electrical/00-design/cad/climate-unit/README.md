# climate-unit - the climate control unit, mocked up

*Rev 2026-10-11 (Y14, second pass: the one-height unit is the default) · owns: what this folder
is, what it may claim, and how to rebuild it. Read `../README.md` first: it is the fence. The
design is the record's (D-479, D-480, `housings` DP-DCU to DP-DCU-D, parts P152 / P194 / P195);
this is a drawing of it.*

## What it is

D-479 made the climate control one sealed unit built like a stereo head unit: the faceplate and its
dials on the front, the control panel's board right behind it, the DCU carrier lying flat behind
that, and nothing outside but sealed Deutsch connector halves. D-480 put every one of those halves
in the rear wall, in two rows: the carrier's three DT13s below, DP-DCU-D on a small board of its
own above, and a second upper position kept for the left plate (idea I-002).

This folder is the **mock-up** D-480 asked for before any detailed model: the insides and the case
as one parametric FreeCAD build, driven by one table of numbers, that rebuilds when a number
changes and says in words what no longer fits. It is **not the print-ready model** (that is F1,
after the measurements) and it replaces neither `../dcu-carrier/enclosure` nor `../panel/enclosure`
yet.

**The default is the front-install unit.** D-480: "height is the dimension with the most wiggle
room … you would install this exactly like a head unit". So the unit is ONE height front to back,
whatever the two connector rows need, and the face grows to cover it: `FACE_H` is None and
derived, as `FACE_W` is. The sketch's 180 x 60 control layout is kept whole, as a block, on the
larger face. The other unit - a face lower than the body, with the rear stepping up behind the
dash - is still one number away (below), and the report always says which one was built:
`front install: yes` or `front install: no - the rear is N mm taller than the face covers`.

**R11 applies to all of it: nothing here has been measured.** The dash opening (V-113) and the room
behind it (V-102) are unknown, the face is a sketch he is still changing (I-001 to I-006), the
carrier's outline is provisional (D-455), and no knob, key, display, plug or insert is in hand. The
DT13 cut-outs are TE's drawing (114-151046, through `../enclosure_lib.py`) and the DT13 bodies are
TE's models as the DCU enclosure build probed them. Everything else is a parameter, and most are
marked `confirm`.

## Change a number, rebuild

Every number is in **`unit_params.py`**, one commented row each: name, value, unit, what it is,
and why it is a guess. No other file holds a dimension. Edit a value, then:

```
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd make_unit.py
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
| the front-install unit, one height (the default) | `FACE_H = None` |
| the stepped unit: a low face, the rear rising behind the dash | `FACE_H` to a number lower than the body needs, e.g. `64.0` (the least the sketch's layout fits); `FRONT_L` is then the length of the low front section |
| the control block higher or lower on the face | `CONTROLS_ANCHOR` = `"centre"`, `"top"` or `"bottom"` |
| a lower unit | `ROW_PITCH` (least 40.3), `BOSS_H`, `TOP_GAP` |
| a narrower unit | `CARRIER_W` (its connector edge needs about 163) |
| the left plate's connector fitted | `fitted` True on its row of `UPPER_CONNECTORS` |
| the car's opening checked | `ENVELOPE`, once V-113 and V-102 are measured |

**The self-test** rebuilds under the parameter sets in `unit_params.SELFTEST` and writes no file.
Each set is stored with the outcome it must have - built clear, built with a failing check, or
refused in words - and the self-test fails (exit 1) when any outcome differs, so an edit that
changes what the model does is caught. If the change is meant, change the stored word.

```
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd selftest.py
```

## What it reads

`../dcu-carrier/enclosure/board.json` (outline, holes, connector positions) and `probe.json`
(each DT13's flange, housing and height), and `../dcu-carrier/dcu-carrier.step` when it is there:
then the real board, with every part on it, goes in the box. Without the STEP, with
`CARRIER_STEP` False, or when `CARRIER_W` / `CARRIER_D` are not the drawn board's, plain blocks
of the same sizes stand in and the report says so. `probe.json` is read as it is: if the board
moves, rebuild the DCU enclosure first so the probe is fresh. It writes nothing outside this
folder.

## What it writes

| File | What | In git |
|---|---|---|
| `climate-unit.FCStd` | everything as named objects: group `Insides` (faceplate, each control, panel board, carrier, upper board, connectors, standoffs, and a sub-group `Keepouts` for the rooms kept clear and the mated plugs), group `Case` (body, rear plate, lid, front frame). Opens in the FreeCAD GUI | no |
| `climate-unit.step` | the assembly: parts only, no keep-outs | no |
| `climate-unit-body.step`, `-rear_plate`, `-lid`, `-front_frame` | one per case part | no |
| `report.json` | every derived dimension, every check, the parameters, the `confirm` list | no |
| `view-front.svg`, `-back`, `-side`, `-top` | line drawings by hidden-line projection; blue = room kept clear; on the front view, orange = the sketch's 180 x 60 control block, so the spare face round it shows. The carrier is drawn as blocks here (TE's models break the projection) | yes |

## How it is laid out

Frame: X across the face (0 = the left edge from the cabin), Y back from the faceplate's front,
Z up from the faceplate's bottom edge.

- **Height.** The body is as tall as the two rows need - floor, bosses, `ROW_PITCH`, the upper
  DT13, `TOP_GAP`, the lid - and that is never typed. With `FACE_H` None the face is that plus
  `BEZEL_OVERLAP` top and bottom (or the least the control block needs, if that is more), so
  there is no step.
- **Behind the face**: the front frame (a ring behind the faceplate, four standoffs to the panel
  board), the panel board `PANEL_GAP` behind the faceplate, and the room kept behind it. The
  faceplate stands `BEZEL_OVERLAP` proud of the body all round.
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
- **Fixing**: two insert bosses inside each side wall (`SIDE_SCREWS`), head-unit style -
  placeholders.
- No grommet and no ribbon notch: the ribbon runs inside from the panel board's header to the
  carrier's J4.
- **The stepped unit** (a typed `FACE_H` lower than the body): the first `FRONT_L` behind the
  face is the face's height, a step wall rises behind it, and the lid covers the tall rear. The
  carrier is then where `CARRIER_FRONT_GAP` puts it, and a `FRONT_L` that would put the step wall
  over it is refused.

Not drawn, on purpose: the ribbon and the inside leads from the upper board to J3 / J5-J8, the
joint between the front frame and the body, the faceplate's own fixing detail, draft and print
orientation, any fillet.

## What the default build says (2026-10-11)

- **Front install: yes.** One height, 188 x 92.76, behind a 192 x 96.76 face.
- **Width.** The carrier is 180 wide, so the body is 188 and the face 192 - 12 mm wider than the
  sketch's 180. `FACE_W 180` is refused with the two ways out: a wider face, or a narrower
  carrier.
- **Height.** A DT13 stands 37.8 mm above the underside of its board, so the upper board must sit
  at least 40.3 mm up (the first brief's 32 cannot be built). At `ROW_PITCH` 42 the body is
  92.76 mm tall - not the 75 D-480 estimated - and the face 96.76, which is 36.76 mm more than
  the sketch's 60. Centred, the control block has 18.4 mm of bare face above and below it.
- **Depth.** 124.6 mm from the face's front to the rear lip, 134.3 to the receptacles' tips,
  202.6 with a 50 mm plug and 30 mm of cable bend.
- **Ribbon.** 20 mm in a straight line between the two header faces: a short jumper, with two IDC
  plugs to fit in that room.
- **Upper board standoffs.** The carrier rev 0.04 has no holes for them. The default spots are
  clear of its parts, not of its tracks (Y15).
- **The stepped unit** (`FACE_H 64`): face 192 x 64, front section 60 tall, rear 92.76, depth
  121.6 / 199.6; `front install: no - the rear is 32.76 mm taller than the face covers`. At the
  sketch's own 60 the screen window's top 1.8 mm is behind the box's roof, so 60 is refused.

## The `confirm` list

The report prints the live list with each value. As of this revision: `ENVELOPE`, `FACE_W`,
`FACE_H`, `FACE_T`, `BEZEL_OVERLAP`, `FRONT_L` (the opening, V-113 / V-102) · `CONTROLS`,
`CONTROLS_ANCHOR`, `KNOB_PROUD`, `KNOB_FLOAT`, `KNOB_HOLE_D`, `KNOB_SHAFT_D`, `KEY_PROUD`,
`KEY_CLEAR`, `PADDLE_PROUD`, `PADDLE_CLEAR`, `SCREEN_T`, `SCREEN_BORDER` (the face is a concept;
no control is chosen) · `PANEL_GAP`, `PANEL_MARGIN`, `PANEL_BACK_H`, `PANEL_RIBBON_X`,
`PANEL_RIBBON_Z` (no panel board is placed for this face) · `CARRIER_W`, `CARRIER_D`,
`CARRIER_TOP_H` (provisional outline; the Teensy on its socket unmeasured) · `ROW_PITCH`,
`UPPER_BOT_H`, `UPPER_W`, `UPPER_D`, `UPPER_STANDOFFS` (the upper board is not drawn, Y15) ·
`PLUG_L`, `CABLE_BEND`, `PLUG_GROW`, `PLUG_ROW_CLEAR`, `PLUG_SIDE_CLEAR` (no plug measured) ·
`INSERT_BORE`, `INSERT_DEPTH` (against the insert bought) · `SIDE_SCREWS` (what the unit fastens
to is unmeasured).

## Files

| File | What |
|---|---|
| `unit_params.py` | the parameter table, the control table, the upper row, the self-test's sets and their expected outcomes |
| `unit_lib.py` | `derive` (every position), `validate` (the fit rules), the builders, `check`, the writers |
| `make_unit.py` | the one command |
| `selftest.py` | the self-test's command (`freecadcmd` passes a script its own arguments only after `--pass`) |

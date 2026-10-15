# du-assembly - the ICU as one unit, mocked up

*Rev 2026-10-12 (Y19, first pass) · owns: what this folder is, what it may claim, and how to rebuild
it. Read `../../../README.md` first: it is the fence. The design is the record's (D-491, D-270, D-268,
`housings` DP-ICU-A / DP-ICU-B, parts P111 and P117 to P122, `icu_channels` IC21 / IC22 / IC24);
this is a drawing of it.*

## What it is

D-491 made the ICU one assembly, like the Control Unit: the 12.3-inch bar display as the face, the
BT817 eval board and the ICU carrier behind it in one housing, the radio behind an RF-transparent
wall, the page button on the face, and the two sealed Deutsch DT13 halves in the housing's rear
wall. It goes into the binnacle aperture from the front and is plugged from behind; nothing leaves
it but the two DT13s (no grommet, no notch: the ribbon and the display's flex stay inside).

This folder is the **mock-up** D-491 asked for: insides and housing as one parametric FreeCAD
build, driven by one table of numbers, that rebuilds when a number changes and says in words what
no longer fits. It copies the method of `../../../control-unit/cad/cu-assembly` (Y14). It is **not the print-ready model**
(that is F1, after C4 and M-1 are measured) and it replaces Y7's `../du-carrier/enclosure` as the
ICU's box (P111); D-270's separate box behind the binnacle stays the fallback if C4 shows the
binnacle shallow.

**R11 applies to all of it: nothing here has been measured.** The aperture and the depth behind it
(C4, M-1 / C1) are unknown, no display is chosen (P118), the eval board is not in hand (P117), the
page button is not chosen (P120), and the carrier's outline is provisional (D-455). The DT13
cut-outs are TE's drawing (114-151046, through `00-design/tools/enclosure_lib.py`) and the carrier and its
DT13s are the board's own files. Everything else is a parameter, most marked `confirm`.

## Change a number, rebuild

Every number is in **`display-unit/data/du_assembly_params.py`**, one commented row each: name, value, unit, what it is,
and why it is a guess. No other file holds a dimension. Edit a value, then:

```
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 00-design/tools/mockup.py --pass du-assembly
```

Exit 0 built and clear · 1 a fit rule failed, an interference, the RF window, or the measured
envelope refused · 3 a crash. The fit rules run before anything is drawn; when one fails nothing is
built, the last good build's outputs are removed, and the report gives one sentence per problem
naming the parameter and which way to move it, for example:

> The page button's body (X 313-329, Z 61.5-77.5, back to Y 33) runs into the BT817 board on the
> display plate (X 229-329, Z 6-82), GAP 1 included: move the button (BUTTON_X / BUTTON_Z, from the
> display's centre) or the BT817 board (BT_X / BT_Z).

After a build every inside solid is checked against every case solid and the inside parts against
each other, an interference naming the feature and the parameters that move it.

| To get | Set |
|---|---|
| a shorter unit (the carrier slides under the BT817 board) | `CARRIER_LAYOUT = "below"` |
| another display | `DISP_W`, `DISP_H`, `DISP_T`, `ACTIVE_*`, `FLEX_*` |
| the page button elsewhere | `BUTTON_X`, `BUTTON_Z` (from the display's centre) |
| a symmetric face | `DISPLAY_CENTRED = True` |
| the radio's window on another wall | `RF_WINDOW_ON` = `"left"`, `"right"`, `"lid"`, `"floor"`, `"rear"` |
| the brief's chain (no scaler, no HDMI bridge) | `DRIVER_BOARDS = []`, `FLEX_TO = "BT817"` |
| the binnacle checked | `ENVELOPE`, once C4 and M-1 are measured |

**The self-test** rebuilds under the parameter sets in `the parameter table's SELFTEST` and writes no file.
Each set is stored with the outcome it must have - built clear, built with a failing check, or
refused in words - and the self-test fails (exit 1) when any outcome differs. If a change is meant,
change the stored word. About 50 s on the Mac.

```
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 00-design/tools/mockup_selftest.py --pass du-assembly
```

## What it reads, what it writes

Reads `display-unit/data/du-carrier-board.json` (outline, holes, footprints) and `probe.json` (each
DT13's flange, housing and tip, and every part's 3D extent: the XIAO, J4, SW1), and
`../du-carrier/du-carrier.step` when it is there - then the real board, every part on it, goes
in the box; without it (or `CARRIER_STEP` False) stand-in blocks of the probed sizes do. `probe.json`
is read as it is: if the board moves, rebuild Y7's enclosure first so the probe is fresh. It writes
nothing outside this folder.

| File | What | In git |
|---|---|---|
| `du-assembly.FCStd` | everything as named objects: group `Insides` (bezel, display, page button, BT817 board and parts, the driver boards, the carrier, and a sub-group `Keepouts`: the flex, the CN8 plug, above / below the carrier, the mated plugs), group `Case` (body, rear plate, lid, front frame) | no |
| `du-assembly.step` | the assembly: parts only, no keep-outs | no |
| `du-assembly-body.step`, `-rear_plate`, `-lid`, `-front_frame` | one per case part | no |
| `display-unit/data/du-assembly-report.json` | every derived dimension, every check, the parameters, the `confirm` list | no |
| `view-front.svg`, `-back`, `-side`, `-top` | hidden-line drawings; blue = room kept clear; orange on the front = the display's active area. The carrier is drawn as blocks (TE's models break the projection) | yes |

## How it is laid out

Frame: X across the face (0 = its left edge seen from the driver's seat), Y back from the bezel's
front, Z up from the bezel's bottom edge.

- **The face** is the bezel plate (P121, 3 mm), with the window (the active area + `WINDOW_MARGIN`,
  `BEZEL_LEDGE` inside the glass's outline), the page button's hole and six M2 screws into the front
  frame's top and bottom bands. Each border is derived: the display + `BEZEL_BORDER`, the body +
  `BEZEL_OVERLAP`, or what the page button needs, whichever is more on that side.
- **The front frame** is a ring as big as the body round the display's pocket, closed behind the
  display by the **display plate** (`BULKHEAD`), which has a slot for the flex (it leaves the glass's
  bottom edge and turns back through `FLEX_ROOM`) and a hole for the button's body, and carries the
  BT817 board on four standoffs. The driver boards stand on it beside the BT817 board.
- **The carrier** lies flat on four bosses, connector edge to the rear, hard against the left wall
  (`CARRIER_X`), so the XIAO's u.FL end faces the RF window: the left wall thinned to `RF_WALL` over
  the XIAO's span plus `RF_KEEPOUT`, as Y7 had it. `behind`: it starts `CARRIER_FRONT_GAP` behind
  what stands on the plate over its width. `below`: it slides under the BT817 board, which then
  stands `GAP` over the room kept above the carrier.
- **Height is never typed**: the body is what the display, the button and the stack on the plate
  need, ONE height front to back, the face covering it.
- **Rear plate**: slides into a channel in the walls and floor; both DT13s mount through TE's
  cut-out from inside. **Lid**: flat, over the whole body behind the front frame, its front edge on
  a beam (`RIM_H`) straight behind the display plate, the cord-gasket groove on the walls' centre
  lines, four lugs inside the walls. **Fixing**: two insert bosses inside each side wall
  (`SIDE_SCREWS`), head-unit style - placeholders.
- **The display chain** (IC21, D-269 chain ii): BT817 RGB to a TFP410-class HDMI encoder (P119), HDMI
  into the display's scaler board (P118), the flex to the glass. The two boards are placeholder
  blocks (`DRIVER_BOARDS`); the brief's simpler chain is `DRIVER_BOARDS = []`, `FLEX_TO = "BT817"`.

Not drawn, on purpose: the ribbon, the flex beyond the plate and the button's lead (straight-line
lengths only), the driver boards' mounts, the joints frame-to-body and bezel-to-frame beyond the
screw holes, draft, print orientation, any fillet.

## What the default build says (2026-10-12)

- **Front install: yes.** One height, body 331 x 132.5, behind a 335 x 136.5 face. The width is the
  display (305) plus the page button beside it on the left (24 mm border; 6 on the right); the
  height is the display (122) plus the flex's room and the floor below.
- **Depth**: 15.5 to the display plate's back; 128.6 to the rear lip, 138.3 to the receptacles'
  tips, **206.6 with a 50 mm plug and 30 mm of bend** (203.6 behind the face). `CARRIER_LAYOUT
  "below"`: 104.5 / 182.5. Y7's estimate for the carrier box alone was 51 mm deep.
- **Lines inside**: the ribbon CN8 to J4 17.8 mm (21.7 below); the flex at least 10.3 to the scaler;
  the page button's lead 67 mm to SW1.
- **RF window**: the left wall, Y 58.2 to 86, Z 6.5 to 31.9, 1 mm from the XIAO; the nearest metal
  is carrier insert H1, 7.8 mm off. The rear plate would put DP-ICU-B in the way, the floor the
  carrier's own copper; the lid works, about 100 mm above the radio.

## The `confirm` list

The report prints the live list with each value (53 today): the aperture (`ENVELOPE`, `FACE_*`,
`BEZEL_*`), the display (`DISP_*`, `ACTIVE_*`, `FLEX_*`, `DISP_TAPE`, `DISP_BACK_CLEAR`,
`WINDOW_MARGIN`), the eval board (`BT_W`, `BT_H`, `BT_PARTS_H`, `BT_UNDER_H`, `BT_HOLE_INSET`,
`BT_CN8`, `CN8_T`), the ribbon (`IDC_*`), the driver boards (`DRIVER_BOARDS`), the page button
(`BUTTON_*`), taste (`DISPLAY_CENTRED`, `BEZEL_SCREWS_AT`), the carrier's room (`CARRIER_TOP_H`,
`CARRIER_LAYOUT`), the plugs (`PLUG_*`, `CABLE_BEND`), the inserts and the side screws.

## Files

| File | What |
|---|---|
| `display-unit/data/du_assembly_params.py` | the parameter table, the driver boards, the self-test's sets and their outcomes |
| `tools/du_assembly.py` | `derive`, `validate` (the fit rules), the builders, `check`, the writers |
| `tools/mockup.py` | the one command |
| `tools/mockup_selftest.py` | the self-test's command (`freecadcmd` passes a script its arguments only after `--pass`) |

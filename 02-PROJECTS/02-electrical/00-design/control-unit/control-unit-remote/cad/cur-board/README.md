# CUR board — the KiCad project

*Rev 2026-10-15 (sheet and board rev 1.00 - Y71: D-597, D-602, D-604, D-615) · owns: what this KiCad project
is for and what it may claim. The CUR's design is the record: the cavities of `DP-CUR` 1-9
(`../../../../../data/cavities.csv`), devices `DV21`, `DV24` and `DV62`, parts P156, P198, P199, P200, P204,
P219, P226, P249 and P250, and the box `CUR` (`boxes.csv`). Read `00-design/README.md` first: it is the fence.*

## What it is

The Control Unit Remote's board (D-586, D-597): the controls right of the steering wheel, behind the face
D-602 rules - 43.11 x 32.0 mm, the screen knob over the mirror control on the wheel side, the hazard across
the top row, the two winks, then the fuel-door and hatch keys, one 1.6 mm gap everywhere. The board is that
face's control area, **38.11 x 27.0 mm**, its top-left corner at the face's (2.5, 2.5), so every switch sits
on its cap's centre. It is drawn whole by `00-design/tools/cur_board_sch.py` (the sheet, the footprints) and
`cur_board_pcb.py` (placement, freerouting, the pour): edit those, never the files here.

Front (toward the driver, F.Cu):

| Ref | What | Under |
|---|---|---|
| `SW5` | the hazard, a 5.8 mm self-locking push switch (P226) | the top row's 23.8 x 7.9 red-triangle cap |
| `SW3` / `SW4` | the winks, subminiature SPDT momentaries, Omron D2FS class (P204, D-499) | 11.1 x 7.9 caps |
| `SW2` / `SW1` | the fuel-door and hatch keys, TL3342-class 4.2 x 3.2 tactiles | 11.1 x 7.9 caps |
| `SW6` | the mirror control, an ALPS SKRH-class 4-direction switch with push (P156, D-615) | a 7.1 mm knob in the face's 12.7 mm well |
| `ENC1` | the screen knob, a 9 mm encoder with push, M7 bushing (P219, D-615) | the 12.7 mm knob; its bushing through the face, a nut in front |
| `LED1`-`LED6` | 0603: wink L / R faces, hatch, fuel door, the mirror symbol (in the well), the hazard's triangle | their caps |

Back (B.Cu): `U1` IS31FL3218 (the lights, 0x54) with `C1`, `C2`, `R1`, `R2`; `U2` PCA9555PW (the keys, 0x20)
with `C3`; `U3` AP2112K-3.3 (the expander's 3.3 V) with `C4`, `C5`; the winks' `R3` 18 k / `R4` 33 k, the
hazard's `R5` 4.7 k / `R6` 47 k; `J1`, the pigtail's nine solder pads.

## What it may claim

That the sheet carries exactly what the record says, cavity by cavity (`check.py`), that the board is the
sheet (DRC with schematic parity), and that every switch is on its cap's centre on the ruled face. It may
not claim any part: every switch, the encoder and the 4-way are **classes with placeholder footprints**
(`cur-board.pretty`), drawn from a typical part of the class and marked `confirm` - each is redrawn from
the drawing of the part bought (R11). Nothing right of the wheel is measured.

## The pins: J1, the pigtail (D-615)

Nine 20 AWG conductors soldered into J1's plated holes from the back, out through the rear cover's grommet,
about 150 mm to an inline DRC 24 receptacle that mates the harness's `DP-CUR` plug. Pad n = DP-CUR n.

| J1 | DP-CUR | Net | Far end |
|---|---|---|---|
| 1 | 1 | `PNL_SDA` | the CU, DP-DCU 44 |
| 2 | 2 | `PNL_SCL` | the CU, DP-DCU 45 |
| 3 | 3 | `GND` | the CU, DP-DCU 46 - the board's own return |
| 4 | 4 | `+5V_PNL` | the CU, DP-DCU 47 - the LEDs, and U3 for the 3.3 V |
| 5 | 5 | `WINK_L_NC` | K2's switch input in the PMU box |
| 6 | 6 | `WINK_R_NC` | K1's switch input |
| 7 | 7 | `WINK_REQ` | A8 - wink L NO through 18 k, wink R NO through 33 k |
| 8 | 8 | `WINK_COM` | the PMU box's ground star - never the board's `GND` |
| 9 | 9 | `HAZ_LADDER` | A8 - the hazard through 4.7 k, 47 k baseline across (D-368) |

The winks and the hazard keep their own lines to the PMU box because they wake the car while the CU sleeps;
everything else rides the I²C bus (D-604).

## The keys: U2, the PCA9555 (D-604)

Every input closes to `GND`; the PCA9555's own 100 k pull-ups hold it high. Address 0x20 (A0-A2 low), VDD 3.3 V
from `U3` so its inputs read the CU's 3.3 V bus (the pull-ups are on the CU carrier). There is no INT wire -
the link is four wires - so the CU polls it (row Y80).

| IO | Net | | IO | Net |
|---|---|---|---|---|
| 0_0 | `KEY_HATCH` | | 0_6 | `MIR_PUSH` |
| 0_1 | `KEY_FUEL` | | 0_7 | `KNOB_PUSH` |
| 0_2 | `MIR_UP` | | 1_0 | `KNOB_A` |
| 0_3 | `MIR_RIGHT` | | 1_1 | `KNOB_B` |
| 0_4 | `MIR_DOWN` | | 1_2 - 1_7 | spare |
| 0_5 | `MIR_LEFT` | | | |

## The lights: U1 and the channel map

The CU firmware's map (`control-unit/firmware/cu/lights.h`), unchanged: OUT1 wink L, OUT2 wink R, OUT3 hatch,
OUT4 fuel door, OUT6 hazard, OUT13 mirror; R_EXT 10 k = 7.6 mA a channel; SDB held high by `R2`. The knob's
bulb symbol, lit while it turns, needs a hollow-shaft encoder or a light pipe: not drawn - confirm with the part.

## Confirm

- Every part is a class (P156, P199, P204, P219, P226): footprints and heights from the part bought.
- The pigtail's length and conductor, the grommet, the inline DRC 24's part number (P200, P249).
- U1's QFN footprint against Lumissil's package drawing; U2, U3 against NXP's and Diodes' (no vendor pin
  table for them in `data/pin_tables.csv` yet - check.py notes it).

## Checking it

    <kicad python> 00-design/tools/cur_board_sch.py sch     the sheet, the footprints, the project
    <kicad python> 00-design/tools/cur_board_sch.py pcb     placement, routing (freerouting), the pour
    kicad-cli sch erc cur-board.kicad_sch                    0 violations
    kicad-cli pcb drc --schematic-parity cur-board.kicad_pcb 0 violations, 0 unconnected, 0 parity
    python3 00-design/tools/check.py --board cur-board      the sheet against DP-CUR (0 mismatches)

`<kicad python>` is `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`.

## Opening it

KiCad 10: **File → Open Project** → `cur-board.kicad_pro`; the schematic and the board open from the project
window. The 3D view is **View → 3D Viewer** in the board editor (the placeholders have no 3D model). The
whole box - board, caps, knobs, shell and cover - is the mock-up in `../cur-assembly/` (FreeCAD).

## Files

`cur-board.kicad_pro` / `.kicad_sch` / `.kicad_pcb` the project; `cur-board.kicad_sym`, `sym-lib-table`,
`cur-board.pretty`, `fp-lib-table` its own symbols and footprints; `cur-board.step` the board in 3D;
`cur-board-erc.rpt`, `cur-board-drc.rpt` the last checks; `fab/` the fab package (gerbers, drill, zip).
The schematic as SVG and the assembly drawings are in `../../diagrams/`.

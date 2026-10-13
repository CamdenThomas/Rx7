# Left plate — the KiCad project

*Rev 2026-10-13 (sheet and board rev 0.01, provisional - Y21, D-492) · owns: what this KiCad project is
for and what it may claim. The plate's design is the record: the cavities of `DP-DCU-E`
(`../../../../data/cavities.csv`), the `panel_ribbon` lines they name, devices `DV24` and `DV62`, parts
P083, P156, P198, P199 and P200. Read `../../../README.md` first: it is the fence.*

## What it is

The panel's second face (D-492): a small board left of the steering wheel, behind its own faceplate,
carrying the two wink switches, the hatch and fuel-door keys, the mirror stick and five lit symbols.
It is joined to the climate unit by a twelve-conductor cable (P200) to `DP-DCU-E`, which the upper
connector board runs straight through to the panel board's plate header `J3`.

- **The keys** are matrix keys on `ROW1`, as they were on the centre panel: hatch on `COL2`, fuel door
  on `COL3`, each through its own 1N4148W, cathode to the row, anode toward the column - the panel
  board's convention (`../panel/README.md`).
- **The stick** (P156) is the ribbon's lines 17-20: two pots across `+3V3` / `AGND` (D-380: its own
  return), wipers on `JOY_X` / `JOY_Y`, the push from `JOY_PRESS` to `GND` (panel_ribbon 19 "push switch
  to GND", cavity 6). `AGND` is kept apart from `GND` here; they meet on the carrier.
- **The lights** are the plate's own I²C driver on the panel's bus (P199).
- **The winks are not on the sheet** (below): the board only has holes for them.

## What it may claim

ERC-clean, DRC-clean with schematic parity, and `check.py --board left-plate` holding `J1` against
`DP-DCU-E` pin for pin, the two keys against the cavities that name them, the stick against
panel_ribbon 1 and 17-20. That makes it **internally consistent and consistent with the record, not
correct** (R11): no part, cable or dimension here has been in anyone's hand, and nothing left of the
steering wheel has been measured. The record wins; a fact found here is promoted to a row, never cited
from this folder.

## The pins: J1, DP-DCU-E pin for pin

`J1` is a 2 × 6 shrouded header (`Connector_IDC:IDC-Header_2x06_P2.54mm_Vertical`) on the back, pin n =
cavity n, the net named as the cavity's `src_note` panel_ribbon line names it:

| Pin | Net | panel_ribbon | On this board |
|---|---|---|---|
| 1 | `ROW1` | 3 | `D1` and `D2` cathodes |
| 2 | `COL2` | 7 | `SW1` the hatch key |
| 3 | `COL3` | 8 | `SW2` the fuel-door key |
| 4 / 5 | `JOY_X` / `JOY_Y` | 17 / 18 | `JS1` X / Y wipers |
| 6 | `JOY_PRESS` | 19 | `JS1` push (SW_A); its other side SW_B on `GND` |
| 7 | `+3V3` | 1 | `JS1` pot supplies only (cavity 7: "nothing else on the plate is powered from it") |
| 8 | `AGND` | 20 | `JS1` pot grounds only |
| 9 / 10 | `PNL_SDA` / `PNL_SCL` | 22 / 24 | `U1` SDA / SCL; the pull-ups are the carrier's (R51 / R52), none here |
| 11 | `GND` | 21 | `U1`, `C1`, `C2`, `R1`, the stick's push, the pour |
| 12 | `+5V_PNL` | 26 | `U1` VCC, `C1` / `C2`, `R2`, the five LED anodes |

## The lights: U1 and the channel map

**`U1`, IS31FL3218-QFLS2-TR** (QFN-24 4 × 4, Lumissil Rev G 2024): 18 constant-current sinks, I²C
address fixed at **0x54** ("1010 100x", p.1). It suits the rails as they are: VCC 2.7-5.5 V, so it runs
from `+5V_PNL`; VIH 1.4 V min on SDA / SCL / SDB (p.4), so the 3.3 V bus reads, and the bus is pulled to
3.3 V on the carrier, never to 5 V. No other part was needed. `C1` 1 µF and `C2` 100 nF at VCC (P199);
`R1` 10 k on R_EXT, IMAX = 58.5 × 1.3 V / 10 k = **7.6 mA** a channel (p.10), the panel's D-458 current;
`R2` 100 k holds SDB high, so the driver is on and blank until written, as the panel's `U2`. Five
channels at full current draw 38 mA from `+5V_PNL`.

The map is **the DCU firmware's** (`../../firmware/dcu/lights.h`, the plate's `LQ_` channels), followed
as written:

| OUT | LED | What it lights | Board (x, y), front |
|---|---|---|---|
| 1 | `LED1` | wink left face | (20, 8) |
| 2 | `LED2` | wink right face | (39, 8) |
| 3 | `LED3` | hatch release symbol | (44.75, 37) |
| 4 | `LED4` | fuel-door release symbol | (25.75, 37) |
| 5 | `LED5` | mirror stick symbol | (74.5, 12.5) |

OUT6-OUT18 are open (no-connect on the sheet). Anodes on `+5V_PNL`, cathodes to the channel, 0603.

## The wink switches: mechanical only

P083 (two DMWD 1NO+1NC metal panel-mount pushbuttons) mount in the plate's faceplate; their bodies and
lugs pass through the board in two **16.5 mm clearance holes**, `H5` and `H6`, board-only footprints
with no pads and no nets (`left-plate:WinkSwitch_P083_Clearance_D16.5`). Their lines are the
harness's and stay exactly as `DV24` has them (D-189, D-482, D-492): NC poles to L3-S1 9 / 10, NO poles
through 18 kΩ / 33 kΩ to the L3-S1 11 node, commons to dash ground, on their own lead to the dash post.

The 18 k / 33 k ladder resistors could sensibly live on this board (a 5-way header for the wink lead,
the switches' lugs wired to pads, the resistors beside them), which would take them out of the
harness; that moves a fact in `DV24` and adds a header, so it is not drawn - a question for the record.

## The board

2 layers, 1.6 mm, **100 × 56 mm**, 3 mm corner radius, from the sketch's `plate()`
(`../../../panel-concept.html`, 10 units per mm). Millimetres from the plate's top-left corner **as seen
from the front** (the faceplate side, F.Cu), x toward the steering wheel, y down. The sketch's default
is drawn: the stick on the steering-wheel side. `gen_left_plate.py` carries the sketch's `flip` as
`FLIP`, but the board half refuses it (only the default has been placed and routed).

| What | Part | Board (x, y) | Side |
|---|---|---|---|
| wink left | `H5` Ø16.5 hole | (20, 19) | through |
| wink right | `H6` Ø16.5 hole | (39, 19) | through |
| fuel-door key (cap centre) | `SW2` 6 × 6 tactile, pad 1 at (16.75, 34.75) | (20, 37) | front |
| hatch key (cap centre) | `SW1`, pad 1 at (35.75, 34.75) | (39, 37) | front |
| mirror stick (axis) | `JS1` placeholder | (74.5, 28), well radius 14 | front |
| cable header | `J1`, pin 1 at (94.5, 21.65); odd pins x 94.5, even x 91.96, down to y 34.35 | centre (93.2, 28) | back, at the right (wheel-side) edge |
| LED driver | `U1`, turned so OUT1-5 face the keys and pins 1-6 face down | (58, 36) | back |
| `C2` 100 nF / `C1` 1 µF | under `U1`'s VCC | (58.25, 41) / (58.25, 43) | back |
| `R1` R_EXT / `R2` SDB | right of `U1` | (62.5, 39.5) / (62.5, 35.5) | back |
| `D1` hatch / `D2` fuel-door diode | under their keys | (39, 43.75) / (20, 43.75) | back |
| M3 holes `H1`-`H4` | 3.2 mm | (4, 4), (96, 4), (4, 52), (96, 52) | through |

The key LEDs sit inside their 17 × 15 caps, 5.75 mm toward the wheel from the switch's centre (the
switch fills the middle; the panel does the same at 5.6), lit through the cap (D-488). The wink LEDs
sit 8 mm from the top edge, above their buttons' holes: a metal pushbutton cannot be lit through, so
the faceplate needs a window above each, or the wink part changes (I-006's note: a lit-symbol switch
is money, a block when he rules). The mirror LED sits just outside the top of the stick's 14 mm well.

**Routing**, by a grid router in `board_left_plate.py` (0.25 mm grid, Manhattan, no freerouting on this
machine): 0.25 mm tracks throughout (0.2 mm clearance, 0.6 / 0.3 mm vias), 118 segments and 19 signal
vias, every net routed including `GND`; a solid GND pour on both layers stitched on a 6 mm lattice
(about 100 vias, any left dangling after the fill are dropped). Correct, not pretty: the final board is
laid out when the parts are in hand.

## Confirm

- **The outline, the holes and the plate's place** - the sketch's, nothing measured left of the wheel
  (Y21's note, R11).
- **The stick footprint** - `left-plate:Thumbstick_P156_Placeholder_2x04_P2.54mm`, the panel's Y6
  placeholder: eight 1.0 mm holes on a 2 × 4 grid for a stick on a breakout or leads, a 26 × 26
  courtyard for an ALPS RKJXV-class body. **No part is chosen (P156)**; its pins, body and well come from
  the part's drawing. The mirror symbol "in the centre of the joystick" (I-006) is a part question; the
  LED is beside the well for now.
- **The driver** - IS31FL3218 is P199's own part and fits the rails (above); KiCad's QFN-24 4 × 4
  footprint (EP 2.7) against Lumissil's package drawing. Its pin table is not in `../../../tools/pin_tables.csv`
  (that file is outside this folder's fence): `check.py` prints a note for `U1`, not a mismatch. The
  table is on Lumissil Rev G p.2: 1 OUT18, 2 R_EXT, 3 VCC, 4 GND, 5 SDA, 6 SCL, 7-23 OUT1-OUT17, 24 SDB,
  thermal pad GND - the KiCad symbol carries it unchanged.
- **The wink switch holes** - 16.5 mm for a 16 mm-thread metal button (the reference model is Adafruit
  916, 22 × 19 × 37; the record's own note says confirm size). At the sketch's 19 mm pitch two 19 mm
  bezels touch and the board keeps a 2.5 mm web between the holes: **the sketch's key spacing does not
  leave room for a 16 mm button's bezel** - if P083 is 16 mm, the keys move apart or a 12 mm button is
  bought (money, his). The nut sits between faceplate and board, so the standoff must clear it.
- **The cable side** - `J1` at the right edge, the wheel side, toward the climate unit; its shroud's key
  faces that edge. Where the cable actually runs behind the dash is not measured (P200, about 1 m).
- **The keys** - the 13 mm actuator against the cap and faceplate (LP20); `SW_PUSH_6mm`.
- **The LEDs** - colours (I-006: the wink faces green; the rest LP20's), brightness on the bench, parts.
- **The 100 kHz bus over about 1 m of P200** with the stick's wipers in the same cable (the housing
  row's own note).

## Checking it

```
<kicad python> gen_left_plate.py sch      # symbols, sheet, footprints, lib tables, project
<kicad python> gen_left_plate.py pcb      # place, route, pour (reads the sheet's netlist)
kicad-cli sch erc left-plate.kicad_sch --severity-all --exit-code-violations -o left-plate-erc.rpt
python3 ../../../tools/check.py --board left-plate
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o left-plate-drc.rpt left-plate.kicad_pcb
kicad-cli sch export svg --no-background-color -o . left-plate.kicad_sch
kicad-cli sch export bom --fields 'Reference,${QUANTITY},Value,Footprint,${DNP},Confirm' --labels 'Ref,Qty,Value,Footprint,DNP,Confirm' --group-by 'Value,Footprint,${DNP}' --sort-field Reference -o left-plate-bom.csv left-plate.kicad_sch
kicad-cli pcb render --side top --zoom 1.6 --quality high -w 2000 -h 1200 -o left-plate-top.png left-plate.kicad_pcb
kicad-cli pcb render --side bottom --zoom 1.6 --quality high -w 2000 -h 1200 -o left-plate-bottom.png left-plate.kicad_pcb
kicad-cli pcb export step --subst-models -f -o left-plate.step left-plate.kicad_pcb
```

`<kicad python>` is KiCad's own (`/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`
on the Mac): the board half needs `pcbnew`. The project file is written by the generator from the
panel's rules (one net class), so a KiCad save that resets it is undone by the next run.

Rev 0.01, 2026-10-13: ERC 0 / 0; `check.py --board left-plate` 23 checks, 0 mismatches, one note (U1's
pin table); DRC 0 violations, 0 unconnected, 0 parity issues. The SVG and the BOM are committed; the
renders, the STEP and the reports are rebuilt and not (`.gitignore`). The stick and the wink holes have
no 3D model.

## Files

| File | What |
|---|---|
| `left-plate.kicad_pro` · `.kicad_sch` · `.kicad_pcb` | the project, the schematic and the provisional board |
| `left-plate.kicad_sym` · `sym-lib-table` | every symbol used, kept with the project (the panel's, KiCad's IS31FL3218-QF, the stick's functional block) |
| `left-plate.pretty` · `fp-lib-table` | the stick placeholder and the wink switches' clearance hole, drawn here |
| `gen_left_plate.py` · `board_left_plate.py` | the generator: the sheet from the record's nets, the board from the sketch's positions, the router |
| `left-plate.svg` · `left-plate-bom.csv` | the committed picture and the parts list, `confirm` included |

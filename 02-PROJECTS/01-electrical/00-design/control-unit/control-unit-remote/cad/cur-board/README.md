# Left plate — the KiCad project

*Rev 2026-10-14 (sheet and board rev 0.03, provisional - Y62, Y50: D-586, D-589, D-580, D-581; rev 0.02 Y21, Y22, D-492, D-499, D-504) · owns: what this
KiCad project is for and what it may claim. The plate's design is the record: the cavities of `DP-DCU-E`
and `L3-S1` 9-11 (`../../../../data/cavities.csv`), the `panel_ribbon` lines they name, devices `DV24` and
`DV62`, parts P156, P198, P199, P200 and P204. Read `../../../README.md` first: it is the fence.*

> **D-582 (2026-10-14).** The plate's twelve lines reach the Control Unit as DP-DCU 36-47, the CUR breakout of its branch, not a separate DP-DCU-E; the CUR end (DP-CUR) is unchanged.

> **Rev 0.03 (2026-10-14, Y62 and Y50).** The plate is the CUR, right of the wheel since D-586, and it grows to
> **118 x 56** for a third column (the face's layout is block 01.60's, drawn here as recommended):
> - **The hazard** (D-586, D-589): `SW5`, a latching push button under a lit red-triangle cap (P226, placeholder
>   footprint `HazardSwitch_P226_Latching_Placeholder` - no part chosen), top of the third column beside the
>   winks; `R5` 4.7 k from `J2` pin 5 (`HAZ_LADDER`, L3-S1 6) to the button, the button's other side on the
>   winks' commons (`WINK_COM`, J2 pin 4), `R6` 47 k across the whole (D-368). `J2` is a JST XH **5-way** now.
>   Its cap is `LED6` on the driver's **OUT6**; the mirror symbol `LED5` moved to **OUT13**, the driver's pin on
>   the stick's side (the DCU's `lights.h` follows: `LQ_HAZARD` 5, `LQ_MIRROR` 12).
> - **The screen knob** (D-580, D-581): `J4`, a JST-SH 4-way (STEMMA QT order: 1 GND, 2 +3V3, 3 PNL_SDA,
>   4 PNL_SCL) for the knob's I2C encoder board (P219, seesaw 0x36), which stands off the plate's front below
>   the hazard, its room kept by the board-only `KN1` (25.4 mm square - confirm against the board bought).
> - The stick, `U1` and the two headers moved right with the column. `check.py --board cur-board` now also
>   holds the hazard: the resistor and baseline at the values `L3-S1 6`'s `lands_on` gives, the button between.
> - The board script finishes any connection its grid router leaves with freerouting (not needed this time).

## What it is

The panel's second face (D-492): a small board left of the steering wheel, behind its own faceplate,
carrying the two wink switches, the hatch and fuel-door keys, the mirror stick and five lit symbols.
It is joined to the Control Unit by a twelve-conductor cable (P200) to `DP-DCU-E`, which the upper
connector board runs straight through to the panel board's plate header `J3`.

- **The keys** are matrix keys on `ROW1`, as they were on the centre panel: hatch on `COL2`, fuel door
  on `COL3`, each through its own 1N4148W, cathode to the row, anode toward the column - the panel
  board's convention (`../panel/README.md`).
- **The stick** (P156) is the ribbon's lines 17-20: two pots across `+3V3` / `AGND` (D-380: its own
  return), wipers on `JOY_X` / `JOY_Y`, the push from `JOY_PRESS` to `GND` (panel_ribbon 19 "push switch
  to GND", cavity 6). `AGND` is kept apart from `GND` here; they meet on the carrier.
- **The lights** are the plate's own I²C driver on the panel's bus (P199).
- **The winks** (D-499) are two SPDT momentary pushbuttons under lit caps (P204), `SW3` / `SW4`, with their
  18 k / 33 k ladder resistors `R3` / `R4` beside them; their lines leave on their own 4-way header `J2`
  to the dash post (D-504), never on `J1`.

## What it may claim

ERC-clean, DRC-clean with schematic parity, and `check.py --board cur-board` holding `J1` against
`DP-DCU-E` pin for pin, the two keys against the cavities that name them, the stick against
panel_ribbon 1 and 17-20, and `J2` against the `L3-S1` cavities whose `lands_on` names it (each wink's NC
and common on its pin, the commons apart from the plate's `GND`, and the wink resistors at the values
cavity 11 gives - read from the row, not typed in the check). That makes it **internally consistent and consistent with the record, not
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

The map is **the DCU firmware's** (`../../firmware/cu/lights.h`, the plate's `LQ_` channels), followed
as written:

| OUT | LED | What it lights | Board (x, y), front |
|---|---|---|---|
| 1 | `LED1` | wink left face | (27, 19) |
| 2 | `LED2` | wink right face | (46, 19) |
| 3 | `LED3` | hatch release symbol | (44.75, 37) |
| 4 | `LED4` | fuel-door release symbol | (25.75, 37) |
| 5 | `LED5` | mirror stick symbol | (74.5, 12.5) |

OUT6-OUT18 are open (no-connect on the sheet). Anodes on `+5V_PNL`, cathodes to the channel, 0603.

## The winks: SW3 / SW4 and J2, the wink lead (D-499, D-504)

`SW3` (left) and `SW4` (right) are KiCad's `SW_Push_SPDT`: pin 1 A is the contact the pole rests on (NC),
2 B the common, 3 C the NO. Their lines are the harness's, unchanged (DV24, D-189, D-482); only the two
resistors moved onto the board, and the lead ends on `J2`, a JST XH 4-way
(`Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical`) on the back:

| `J2` pin | Net | Cavity at the dash post | On this board |
|---|---|---|---|
| 1 | `WINK_L_NC` | L3-S1 9 | `SW3` A |
| 2 | `WINK_R_NC` | L3-S1 10 | `SW4` A |
| 3 | `WINK_REQ` | L3-S1 11 | `R3` 18 k from `SW3` C, `R4` 33 k from `SW4` C, joined here |
| 4 | `WINK_COM` | dash ground (G20) | `SW3` B, `SW4` B |

`WINK_COM` is its own net, not this board's `GND`: the winks return to the dash post as today, the plate's
electronics on DP-DCU-E 8 and 11 (DV62). `R3` / `R4` are 0603, 1 %.

## The board

2 layers, 1.6 mm, **100 × 56 mm**, 3 mm corner radius, from the sketch's `plate()`
(`../../../cu-face-concept.html`, 10 units per mm). Millimetres from the plate's top-left corner **as seen
from the front** (the faceplate side, F.Cu), x toward the steering wheel, y down. The sketch's default
is drawn: the stick on the steering-wheel side. `tools/cur_board_sch.py` carries the sketch's `flip` as
`FLIP`, but the board half refuses it (only the default has been placed and routed).

| What | Part | Board (x, y) | Side |
|---|---|---|---|
| wink left (cap centre) | `SW3` P204 placeholder, pins 1-3 at x 17.46 / 20 / 22.54 | (20, 19) | front |
| wink right (cap centre) | `SW4`, 19 mm on - the sketch's pitch | (39, 19) | front |
| wink resistors | `R3` 18 k / `R4` 33 k, behind their switches | (20, 12) / (39, 12) | back |
| fuel-door key (cap centre) | `SW2` 6 × 6 tactile, pad 1 at (16.75, 34.75) | (20, 37) | front |
| hatch key (cap centre) | `SW1`, pad 1 at (35.75, 34.75) | (39, 37) | front |
| mirror stick (axis) | `JS1` placeholder | (74.5, 28), well radius 14 | front |
| cable header | `J1`, pin 1 at (94.5, 21.65); odd pins x 94.5, even x 91.96, down to y 34.35 | centre (93.2, 28) | back, at the right (wheel-side) edge |
| wink lead header | `J2`, pin 1 at (95, 44), pins 2-4 at x 92.5 / 90 / 87.5 | below `J1`, clear of its shroud and `H4` | back |
| LED driver | `U1`, turned so OUT1-5 face the keys and pins 1-6 face down | (58, 36) | back |
| `C2` 100 nF / `C1` 1 µF | under `U1`'s VCC | (58.25, 41) / (58.25, 43) | back |
| `R1` R_EXT / `R2` SDB | right of `U1` | (62.5, 39.5) / (62.5, 35.5) | back |
| `D1` hatch / `D2` fuel-door diode | under their keys | (39, 43.75) / (20, 43.75) | back |
| M3 holes `H1`-`H4` | 3.2 mm | (4, 4), (96, 4), (4, 52), (96, 52) | through |

The key LEDs sit inside their 17 × 15 caps, 5.75 mm toward the wheel from the switch's centre (the
switch fills the middle; the panel does the same at 5.6), lit through the cap (D-488). The wink LEDs
sit the same way inside the wink caps, 7 mm toward the wheel from the cap's centre, beside the
placeholder's 12 mm body, lit through the cap (D-499: no window). The mirror LED sits just outside the
top of the stick's 14 mm well.

**Routing**, by a grid router in `tools/cur_board_pcb.py` (0.25 mm grid, Manhattan, no freerouting on this
machine): 0.25 mm tracks throughout (0.2 mm clearance, 0.6 / 0.3 mm vias), 147 segments and 16 signal
vias, every net routed including `GND`; a solid GND pour on both layers stitched on a 6 mm lattice
(109 vias, any left dangling after the fill are dropped). The router takes an oval pad (`J2`'s) as the
stadium it is, not its bounding rectangle. Correct, not pretty: the final board is
laid out when the parts are in hand.

## Confirm

- **The outline, the holes and the plate's place** - the sketch's, nothing measured left of the wheel
  (Y21's note, R11).
- **The stick footprint** - `cur-board:Thumbstick_P156_Placeholder_2x04_P2.54mm`, the panel's Y6
  placeholder: eight 1.0 mm holes on a 2 × 4 grid for a stick on a breakout or leads, a 26 × 26
  courtyard for an ALPS RKJXV-class body. **No part is chosen (P156)**; its pins, body and well come from
  the part's drawing. The mirror symbol "in the centre of the joystick" (I-006) is a part question; the
  LED is beside the well for now.
- **The driver** - IS31FL3218 is P199's own part and fits the rails (above); KiCad's QFN-24 4 × 4
  footprint (EP 2.7) against Lumissil's package drawing. Its pin table is not in `00-design/tools/pin_tables.csv`
  (that file is outside this folder's fence): `check.py` prints a note for `U1`, not a mismatch. The
  table is on Lumissil Rev G p.2: 1 OUT18, 2 R_EXT, 3 VCC, 4 GND, 5 SDA, 6 SCL, 7-23 OUT1-OUT17, 24 SDB,
  thermal pad GND - the KiCad symbol carries it unchanged.
- **The wink switches** - `cur-board:WinkSwitch_P204_SPDT_Placeholder`, drawn here and **not a part's
  footprint: no P204 part is chosen** (C&K 8125 class, part number and cap confirm). Three 1.0 mm holes
  (1.7 mm pads) on a 2.54 mm row for pins 1 NC / 2 common / 3 NO, a 12 × 12 mm body square (silk at
  12.22, courtyard 12.5), the sketch's 17 × 15 cap dashed on F.Fab, origin the cap's centre. Every one of
  those numbers is a placeholder; the pins, body, actuator height and whether the part carries its own
  LED (then the face LED moves onto its pins) come from the chosen part's drawing. The 19 mm pitch
  leaves 2 mm between the two 17 mm caps and 6.5 mm between the 12.5 mm courtyards.
- **The wink lead** - `J2` JST XH 4-way, locking: housing and crimps confirm; where it sits (below `J1`
  on the wheel-side edge) and the lead's run to the dash post are not measured.
- **The wink resistors** - 18 k / 33 k 0603 1 %, the values `L3-S1 11` names; part numbers confirm.
- **The cable side** - `J1` at the right edge, the wheel side, toward the Control Unit; its shroud's key
  faces that edge. Where the cable actually runs behind the dash is not measured (P200, about 1 m).
- **The keys** - the 13 mm actuator against the cap and faceplate (LP20); `SW_PUSH_6mm`.
- **The LEDs** - colours (I-006: the wink faces green; the rest LP20's), brightness on the bench, parts.
- **The 100 kHz bus over about 1 m of P200** with the stick's wipers in the same cable (the housing
  row's own note).

## Checking it

```
<kicad python> tools/cur_board_sch.py sch      # symbols, sheet, footprints, lib tables, project
<kicad python> tools/cur_board_sch.py pcb      # place, route, pour (reads the sheet's netlist)
kicad-cli sch erc cur-board.kicad_sch --severity-all --exit-code-violations -o cur-board-erc.rpt
python3 00-design/tools/check.py --board cur-board
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o cur-board-drc.rpt cur-board.kicad_pcb
kicad-cli sch export svg --no-background-color -o . cur-board.kicad_sch
kicad-cli sch export bom --fields 'Reference,${QUANTITY},Value,Footprint,${DNP},Confirm' --labels 'Ref,Qty,Value,Footprint,DNP,Confirm' --group-by 'Value,Footprint,${DNP}' --sort-field Reference -o cur-board-bom.csv cur-board.kicad_sch
kicad-cli pcb render --side top --zoom 1.6 --quality high -w 2000 -h 1200 -o cur-board-top.png cur-board.kicad_pcb
kicad-cli pcb render --side bottom --zoom 1.6 --quality high -w 2000 -h 1200 -o cur-board-bottom.png cur-board.kicad_pcb
kicad-cli pcb export step --subst-models -f -o cur-board.step cur-board.kicad_pcb
```

`<kicad python>` is KiCad's own (`/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`
on the Mac): the board half needs `pcbnew`. The project file is written by the generator from the
panel's rules (one net class), so a KiCad save that resets it is undone by the next run.

Rev 0.02, 2026-10-13 (Y22, D-499, D-504): the P083 clearance holes `H5` / `H6` and their footprint are
gone; `SW3` / `SW4` on the P204 placeholder at (20, 19) and (39, 19), `R3` / `R4` behind them, `J2` below
`J1`, `LED1` / `LED2` inside the wink caps. ERC 0 / 0; `check.py --board cur-board` 29 checks, 0
mismatches, one note (U1's pin table); DRC 0 violations, 0 unconnected, 0 parity issues. The SVG and the
BOM are committed; the renders, the STEP and the reports are rebuilt and not (`.gitignore`). The STEP
carries the board, `J1`, `J2`, the two 6 mm keys, `U1` and the 0603 / SOD-123 parts; the stick and the
two winks are placeholders with no 3D model, so they are absent from it.

Rev 0.01, 2026-10-13 (Y21): the winks were P083 metal buttons in two 16.5 mm holes, off the sheet.

## Files

| File | What |
|---|---|
| `cur-board.kicad_pro` · `.kicad_sch` · `.kicad_pcb` | the project, the schematic and the provisional board |
| `cur-board.kicad_sym` · `sym-lib-table` | every symbol used, kept with the project (the panel's, KiCad's IS31FL3218-QF, the stick's functional block) |
| `cur-board.pretty` · `fp-lib-table` | the stick and the wink switch (P204) placeholders, drawn here by the generator |
| `tools/cur_board_sch.py` · `tools/cur_board_pcb.py` | the generator: the sheet from the record's nets, the board from the sketch's positions, the router |
| `control-unit/control-unit-remote/diagrams/cur-board.svg` · `control-unit/control-unit-remote/data/cur-board-bom.csv` | the committed picture and the parts list, `confirm` included |

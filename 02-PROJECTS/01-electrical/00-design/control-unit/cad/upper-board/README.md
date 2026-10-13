# Upper connector board — the KiCad project

*Rev 2026-10-12 (sheet and board rev 0.01, provisional - Y15, D-480, D-492) · owns: what this KiCad
project is for and what it may claim. Its design is the record's cavities `DP-DCU-D` and `DP-DCU-E`
(`../../../../data/cavities.csv`) and what their `src_note` names: the carrier's headers and the
`panel_ribbon` lines. Read `../../../cad/README.md` first: it is the fence.*

## What it is

The climate unit's second connector row (D-480): a small board standing above the DCU carrier,
its two DT13-12PA receptacles in the unit's rear wall above `DP-DCU-B`, the part `P195`.

- **`DP-DCU-D`** (`J1`, D-480) takes the leads that left the DCU's box through grommets until D-479:
  the three door servos, the blower duty and the cabin sensor. Short leads (`P196`) join it to the
  carrier's own headers, so the carrier (rev 0.04) does not change.
- **`DP-DCU-E`** (`J2`, D-492) is the left plate's link: the position D-480 kept is fitted. Its twelve
  conductors go straight through to `J8`, a 2 × 6 header whose lead goes to the panel board's plate
  header (drawn in `Y20`), not to the carrier.

It has no active parts and no capacitor: two receptacles, six headers and copper. A 100 nF across
`+5V_PNL` / `GND` at `J2` was considered and left off: the panel board's `C1` (10 µF) sits at that
rail's own entry and the plate's LED driver carries its own decoupling, so a part here would buy
nothing and add a BOM line no row asks for.

## What it may claim

ERC-clean, DRC-clean with schematic parity, and `check.py --board upper` holding every cavity of
both housings. That makes it **internally consistent and consistent with the record, not correct**
(R11): no part, lead or dimension here has been in anyone's hand. The record wins; a fact found
here is promoted to a row, never cited from this folder.

## The pins

`J1`, `DP-DCU-D` (net names are this sheet's; the record's are the circuits):

| Cav | Net | Record | Header on this board | Lead to the carrier |
|---|---|---|---|---|
| 1 | `SRV_MODE` | SN15 mode door servo signal | `J3` pin 1 | `J6` pin 1 |
| 2 | `SRV_BLEND` | SN15 blend door servo signal | `J4` pin 1 | `J7` pin 1 |
| 3 | `SRV_RECIRC` | SN15 recirculate door servo signal | `J5` pin 1 | `J8` pin 1 |
| 4 | `+5V_SERVO` | SN15 servo +5 V, shared | `J3`, `J4`, `J5` pin 2, joined here | `J6`-`J8` pin 2 |
| 5 | `SERVO_GND` | SN15 servo ground, shared | `J3`, `J4`, `J5` pin 3, joined here | `J6`-`J8` pin 3 |
| 6 | `BLOWER_PWM` | SN14 blower duty | `J6` pin 1 | `J5` pin 1 |
| 7 | `BLOWER_GND` | SN14 blower duty ground | `J6` pin 2 | `J5` pin 2 |
| 8 | `NTC_CABIN` | SN11 cabin sensor | `J7` pin 1 | `J3` pin 1 |
| 9 | `NTC_RET` | SN11 cabin sensor return | `J7` pin 2 | `J3` pin 2 |
| 10-12 | - | sealing plugs (`PLUG`): spares for the radar alert `J12` if luxury 03.12 fits it | no copper | - |

The three servo headers keep the carrier's order (pin 1 signal, 2 +5 V, 3 GND), so each lead is a
plain 3-way jumper, pin for pin. **The returns stay apart on this board** - `SERVO_GND`,
`BLOWER_GND` and `NTC_RET` are three nets, each on its own lead, and become `GND` only on the
carrier. Joined here they would make a loop through two leads and put servo current on the sensor's
return, which cavity 9 exists to prevent. `+5V_SERVO` and `SERVO_GND` are 1.2 mm copper (one servo
moves at a time, F-017: 1-2.5 A), with two 1.2 / 0.6 mm vias where the rail changes layer.

`J2`, `DP-DCU-E`, to `J8` pin for pin (net names are `panel_ribbon`'s signals):

| Cav = `J8` pin | Net | panel_ribbon line | What it is |
|---|---|---|---|
| 1 | `ROW1` | 3 | key matrix row 1 (the plate's hatch and fuel-door keys) |
| 2 | `COL2` | 7 | column 2 - the hatch key |
| 3 | `COL3` | 8 | column 3 - the fuel-door key |
| 4 | `JOY_X` | 17 | mirror stick X wiper |
| 5 | `JOY_Y` | 18 | mirror stick Y wiper |
| 6 | `JOY_PRESS` | 19 | mirror stick push |
| 7 | `+3V3` | 1 | the stick's pot supply |
| 8 | `AGND` | 20 | the stick's pot ground |
| 9 | `PNL_SDA` | 22 | I2C to the plate's LED driver |
| 10 | `PNL_SCL` | 24 | I2C clock |
| 11 | `GND` | 21 | the plate's lights and logic return |
| 12 | `+5V_PNL` | 26 | the plate's LED supply |

`GND` and `AGND` are separate nets here, as they are on the ribbon; the panel board decides where
they meet. `J8` is `Connector_IDC:IDC-Header_2x06_P2.54mm_Vertical`, odd pins on the row nearer
the board's front edge, pin 1 at its right end seen from above (the triangle on the silkscreen).

## The board

2 layers, 1.6 mm, **130 × 36 mm**, square corners. Frame: KiCad's, origin at the board's front-left
corner seen from above, x to the right (the carrier's x), y toward the connector edge (y = 36). The
board's x is the carrier's x − 4.245 and its connector edge lies over the carrier's (carrier y =
board y + 44), so the board can be read straight into `../dcu-carrier/` coordinates.

| What | Board (x, y) | Carrier frame | Unit frame (X, from `report.json`) |
|---|---|---|---|
| `J1` DP-DCU-D, footprint origin | (33.855, 19.17) | (38.1, 63.17): straight above `J9` | X 147.9 |
| `J2` DP-DCU-E, footprint origin | (96.145, 19.17) | (100.39, 63.17) | X 85.61 |
| `H1` M3, 3.2 mm | (4.3, 8.5) | (8.545, 52.5) | X 177.455, Y 88.1 |
| `H2` M3, 3.2 mm | (115.8, 8.5) | (120.045, 52.5) | X 65.955, Y 88.1 |
| `J6` blower (JST-XH), pin 1 / pin 2 | (15.0, 6.5) / (12.5, 6.5) | | |
| `J7` cabin NTC (JST-XH), pin 1 / pin 2 | (21.5, 6.5) / (24.0, 6.5) | | |
| `J5` recirculate, pins 1-3 | (30.0 / 32.54 / 35.08, 6.5) | | |
| `J4` blend, pins 1-3 | (39.0 / 41.54 / 44.08, 6.5) | | |
| `J3` mode, pins 1-3 | (48.0 / 50.54 / 53.08, 6.5) | | |
| `J8` plate header, pin 1 (odd row y 5.0, even row y 7.54) | (102.5, 5.0); pin 11 at (89.8, 5.0) | | |

The DT13 footprint is the carrier's (`../dcu-carrier/dcu-carrier.pretty`): its board edge is 16.83 mm
behind the footprint origin and the flange stands 4 mm past the edge, so each receptacle's centre
is at the X the mock-up gives its rear-plate cut-out.

**Routing**, by hand: the `DP-DCU-D` side on both layers with 0.4 mm signals and the 1.2 mm servo
rail and ground (`+5V_SERVO` on F.Cu along the front edge, `SERVO_GND` under it on B.Cu); the
`DP-DCU-E` side as a two-layer grid, B.Cu risers from `J2`, one F.Cu run per line between them,
B.Cu drops to `J8` (0.25 mm, 0.6 / 0.3 mm vias). 87 segments, 22 vias, no pour. Net classes are in
`upper-board.kicad_pro`: `Default` 0.25 mm, `SERVO` 1.2 mm (1.2 / 0.6 mm vias) for `/+5V_SERVO` and
`/SERVO_GND`.

## Where it differs from the mock-up (Y14)

`../climate-unit/unit_params.py` was written before this board was drawn. Two numbers change, and
the mock-up should take them so it can carry the real board:

- **`UPPER_D` 30 → 36.** At 30 the strip in front of the DT13s is 6.6 mm: the DT13's courtyard runs
  23.4 mm in from the connector edge. The three servo headers fit in that, the JST-XH (6.8 mm) and
  the 2 × 6 shrouded header (10 mm) do not. At 36 they stand in a 12.6 mm strip along the front edge.
- **`UPPER_STANDOFFS` [(4.3, 3.3), (115.8, 3.3)] → [(4.3, 8.5), (115.8, 8.5)]** (along from the
  DP-DCU-D end, back from the front edge). With the board 6 mm deeper the mock-up's carrier spots
  would be at 9.3; they move a further 0.8 mm toward the face so an M3 hole's 3.5 mm keep-out clears
  the DT13's courtyard. On the carrier that is (8.545, 52.5) and (120.045, 52.5), 0.8 mm forward of
  the spots the mock-up checked against the carrier's parts - the mock-up's fit check says whether
  they are still clear.
- `UPPER_W` 130 and both DT13 positions are the mock-up's, unchanged. Its second upper position is
  still `("left plate, idea I-002", 12, False)`: since D-492 it is `DP-DCU-E`, fitted.

## Confirm

- **The outline and the holes**: from the mock-up (Y14), nothing measured; provisional until `V-102`
  / `V-113` and the fit test (`F11`). The carrier rev 0.04 has no holes under the standoffs (the
  mock-up's own confirm).
- **The DT13-12PA footprint**: the carrier's, with its own confirms - pin numbering from TE's
  customer drawing, and the board edge 4 mm behind the flange face.
- **The inside leads** (`P196`): a 3-way 2.54 mm jumper per servo and a JST-XH 2-way lead each for
  the blower and the sensor, about 80 mm - lengths from the mock-up, confirm.
- **`J8` and its lead**: the panel board's plate header is `Y20`'s; pin n here is `DP-DCU-E` n.
- **The plate cable** (`P200`, about 1 m): the stick's wipers and the 100 kHz I2C pair on one cable,
  confirm on the bench (the housing row's own note).
- **Current**: 2.5 A servo stall on 1.2 mm 1 oz copper is under a 10 °C rise by IPC-2221 - the
  servos bought set the real number.

## Checking it

```
kicad-cli sch erc upper-board.kicad_sch --severity-all --exit-code-violations -o upper-board-erc.rpt
python3 ../../../cad/check.py --board upper
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o upper-board-drc.rpt upper-board.kicad_pcb
kicad-cli sch export svg --no-background-color -o . upper-board.kicad_sch
kicad-cli sch export bom --fields 'Reference,${QUANTITY},Value,Footprint,${DNP},Confirm' --labels 'Ref,Qty,Value,Footprint,DNP,Confirm' --group-by 'Value,Footprint,${DNP}' --sort-field Reference -o upper-board-bom.csv upper-board.kicad_sch
kicad-cli pcb render --side top --zoom 1.6 --quality high -w 2000 -h 700 -o upper-board-top.png upper-board.kicad_pcb
kicad-cli pcb render --side bottom --zoom 1.6 --quality high -w 2000 -h 700 -o upper-board-bottom.png upper-board.kicad_pcb
kicad-cli pcb export step --subst-models -f -o upper-board.step upper-board.kicad_pcb
```

Rev 0.01, 2026-10-12: ERC 0 errors 0 warnings; DRC 0 violations, 0 unconnected, 0 parity issues;
`check.py --board upper` 28 checks, 0 mismatches. The DT13 model comes from `${RX7_MODELS}`
(`<tree>/01-REFERENCE/model/library/electrical`): set it before rendering or exporting, as for the
carrier. The SVG and the BOM are committed; the renders, the STEP and the reports are rebuilt from
the board and are not (`.gitignore`).

## Files

| File | What |
|---|---|
| `upper-board.kicad_pro` · `.kicad_sch` · `.kicad_pcb` | the project, the schematic and the provisional board |
| `upper-board.kicad_sym` · `sym-lib-table` | every symbol used, kept with the project (the carrier's connector symbols and KiCad's `Conn_02x06_Odd_Even`) |
| `fp-lib-table` | the carrier's footprint library, for the DT13-12PA; the rest are KiCad's own |
| `upper-board.svg` · `upper-board-bom.csv` | the committed picture and the parts list, `confirm` included |

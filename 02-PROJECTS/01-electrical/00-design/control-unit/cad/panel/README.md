# Control panel — the KiCad project

*Rev 2026-10-13 (sheet and board rev 0.04, provisional - Y20, D-492) · owns: what this KiCad project
is for and what it may claim. The panel's design is `../../../../data/panel_ribbon.csv`, the cavities of
`DP-DCU-E`, `dcu_channels` SN17-SN20 and parts P155, P192, P201 (D-492, D-458, D-459). Read
`../../../README.md` first: it is the fence.*

## Where it stands

**Rev 0.04 is the sketch's control set (D-492)**, drawn in place of Y6's board (D-380's nine keys,
four encoders and the thumbstick, superseded). It is the face of the climate unit (D-479, D-481):
the board stands 8 mm behind the faceplate, inside the unit's enclosure, the DCU carrier behind it.

- **Schematic: ERC 0 errors, 0 warnings.** `../../../tools/check.py --board panel`: 79 checks, 0 mismatches
  against `panel_ribbon` (every conductor, the keys on each row and column through their diodes,
  the encoders, the spares), against `DP-DCU-E` (the plate header pin for pin) and against the
  IS31FL3236A pin table.
- **Board: DRC 0 violations, 0 unconnected, 0 schematic-parity issues** with `--severity-all`.
  180 × 84.76 mm, 2 layers, 56 footprints (52 parts and four M3 holes), 0.25 mm tracks throughout
  (0.2 mm clearance, 0.6 / 0.3 mm vias), about 1660 segments and 110 vias, a GND pour on both layers
  with solid pad connections. Routed by a script (a grid router written for this board, no
  freerouting on this machine), so it is correct, not pretty: `H-008` lays out the final board.
- No processor, no CAN node, no 12 V (D-355): the ribbon's +5 V and I²C feed the lights and the screen.
- The thumbstick, the hatch and fuel-door keys are not on this board any more: they are on the
  left plate (Y21) and reach the ribbon through `J3` (below).

## The board, as seen from the faceplate

Millimetres from the board's top-left corner, x to the right, y down. **The outline is the mock-up's,
`confirm`**: the face is 192 × 96.76 (D-481), the board the face less `PANEL_MARGIN` 6 a side
(`../climate-unit/unit_params.py`). The sketch's 180 × 60 control block is centred on the face, so
**board x = sketch x and board y = sketch y + 12.378**. Four M3 holes 4 mm in from the corners:
(4, 4), (176, 4), (4, 80.76), (176, 80.76).

| Control | Part | Board (x, y) | On the face (the sketch) |
|---|---|---|---|
| screen window | `J2` header for the module, pin 1 at (86.19, 12.0), pins along +x | window centre (90, 27.38) | 44 × 23.6 window |
| centre knob | `SW7` encoder with push | (90, 54.38) | Ø20 knob |
| fan-mode key (upper left) | `SW2` | (67.7, 48.88) | 13 × 8 cap |
| recirculate key (upper right) | `SW3` | (112.3, 48.88) | 13 × 8 cap |
| rear-defog key (lower left) | `SW1` | (67.7, 59.88) | 13 × 8 cap |
| mirror-defog key (lower right) | `SW4` | (112.3, 59.88) | 13 × 8 cap |
| driver seat knob | `SW8` | (40, 42.38) | Ø22 knob |
| passenger seat knob | `SW9` | (140, 42.38) | Ø22 knob |
| driver window switch | `SW5` | (12, 42.38) | 12 × 24 slot |
| passenger window switch | `SW6` | (168, 42.38) | 12 × 24 slot |

Key positions are the cap's centre (the `SW_PUSH_6mm` footprint's origin is pad 1, 3.25 / 2.25 mm
up-left of it). The faceplate's cut-outs are drawn on `Cmts.User`. "Upper / lower, left / right"
follow I-001: driver side is the left.

**The back** carries the rest: the ribbon header **`J1`** (2 × 13, centre (157, 68.26), pin 1 at
the right end (172.24, 69.53), toward the carrier's J4 pin 1 - `PANEL_RIBBON_Z` 16.5 above the bottom
edge, 0.5 more than the mock-up's 16 so `J3` fits under it; the carrier's J4 is straight behind at
x ≈ 158.4, this one 1.4 mm left of that so its shroud clears the board's edge, `confirm`), the plate header **`J3`** (2 × 6, centre (150, 78.6), pin 1 at the
right (156.35, 79.87)), the light driver **`U2`** at (90.05, 30.05) behind the screen with **`C2`,
`C3`, `R1`, `R2`** under it, **`C1`** by `J1` pin 26, the eight matrix diodes beside their switches,
the screen-supply jumper **`JP1`** at (101, 12) and **`TP1`** (the ribbon's spare) at (128, 80.5).

## The ribbon, J1 (`panel_ribbon`, pin for pin)

| Pin | Net | On this board |
|---|---|---|
| 1 | `+3V3` | `J3` 7 only (the stick's pots, on the plate); `JP1` 3 if the screen is set to 3.3 V |
| 2, 21, 23 | `GND` | encoder commons, the centre push, `U2`, `C1`-`C3`, `R1`, the screen; 21 / 23 guard the I²C pair |
| 3 | `ROW1` | rear defog (`D1`); `J3` 1 for the plate's hatch and fuel-door keys |
| 4 | `ROW2` | HVAC mode (`D2`), recirculate (`D3`), window DRV up (`D4`) |
| 5 | `ROW3` | window DRV down (`D5`), PASS up (`D6`), PASS down (`D7`) |
| 6 | `COL1` | rear defog, HVAC mode, window DRV down, mirror defog |
| 7 | `COL2` | recirculate, window PASS up; `J3` 2 (hatch) |
| 8 | `COL3` | window DRV up, window PASS down; `J3` 3 (fuel door) |
| 9 / 10 | `ENC_CENTRE_A` / `_B` | `SW7` A / B |
| 11 | `ENC_CENTRE_PUSH` | `SW7` S1 (S2 to GND) |
| 12 | `ROW4` | mirror defog (`D8`); columns 2 and 3 spare |
| 13 / 14 | `ENC_SEAT_DRV_A` / `_B` | `SW8` A / B |
| 15 / 16 | `ENC_SEAT_PASS_A` / `_B` | `SW9` A / B |
| 17 / 18 / 19 | `JOY_X` / `JOY_Y` / `JOY_PRESS` | `J3` 4 / 5 / 6 only |
| 20 | `AGND` | `J3` 8 only - kept apart from `GND` on this board; they meet on the carrier |
| 22 / 24 | `PNL_SDA` / `PNL_SCL` | `U2`, the screen `J2`, `J3` 9 / 10 |
| 25 | `SPARE` | `TP1` |
| 26 | `+5V_PNL` | `U2` VCC, the 24 LED anodes, `C1`-`C3`, `R2`, `JP1` 1, `J3` 12 |

**The matrix:** one 1N4148W per key, cathode to the row, anode toward the column (a row driven low
pulls its column low; with every row held low any press wakes the DCU). Eight diodes on this board,
the plate's two keys carry their own (D-492).

**The window switches** are drawn as a centre-sprung **DPDT** (ON)-OFF-(ON) toggle, one pole per
direction. The record puts DRV up at `ROW2` / `COL3` and DRV down at `ROW3` / `COL1`: two different
rows *and* two different columns, which an SPDT's single common cannot serve without a phantom key
(its common would join two rows or two columns). With two poles each contact is an ordinary key
behind its own diode. PASS (both on `ROW3`) could use an SPDT, but both switches are the same part.
If the record re-pins DRV up / down onto one row or one column, an SPDT fits and P155 can stay as worded.

## The plate header, J3 - what the left plate (Y21) carries

`J3` is `DP-DCU-E` 1-12 pin for pin; a lead joins it to the upper connector board's `J8`, which runs
straight through to the DT13 `DP-DCU-E` in the unit's back wall and on to the plate's cable (P200).

| Pin | Net | panel_ribbon | On the plate |
|---|---|---|---|
| 1 | `ROW1` | 3 | the row for its two keys |
| 2 | `COL2` | 7 | the hatch key, through its own 1N4148W |
| 3 | `COL3` | 8 | the fuel-door key, through its own 1N4148W |
| 4 / 5 | `JOY_X` / `JOY_Y` | 17 / 18 | the mirror stick's wipers (P156) |
| 6 | `JOY_PRESS` | 19 | the stick's push, to GND |
| 7 | `+3V3` | 1 | the stick's pot supply |
| 8 | `AGND` | 20 | the stick's pot ground |
| 9 / 10 | `PNL_SDA` / `PNL_SCL` | 22 / 24 | the plate's own I²C LED driver (its symbols) |
| 11 | `GND` | 21 | the plate's lights and logic return |
| 12 | `+5V_PNL` | 26 | the plate's LED supply |

The two wink switches on the plate are not here: they stay hardwired to the PMU (DV24, D-492).

## The lights (D-458, D-492)

**`U2`, IS31FL3236A-TQLS4** (eTQFP-48, I²C **0x3C**, AD to GND), as on Y6: `C1` 10 µF at `J1` 26,
`C2` 1 µF and `C3` 100 nF at VCC, `R1` 10 k on R_EXT (IMAX = 58.5 × 1.3 V / 10 k = 7.6 mA a channel,
p.11), `R2` 100 k holding SDB high (on and blank until written). 24 LEDs, 0603, anode on `+5V_PNL`,
cathode to the channel - 24 × 7.6 mA = 0.18 A at full current. The fan and temperature arcs of D-458
are gone; the screen shows those. Which lights follow the headlights (the ring, the window and seat
symbols) and which show state (the key symbols, the seat arcs) is firmware's (I-004), not wiring.

The channel map was chosen from the geometry (channels taken round `U2` in the same order as the
LEDs around it, so the runs do not cross); the record names no order. **F-018 reads it from here.**

| OUT | LED | What it lights | x | y |
|---|---|---|---|---|
| 3 | `LED8` | knob ring, lower left | 80.454 | 63.924 |
| 5 | `LED1` | rear-defog key symbol | 73.3 | 59.878 |
| 6 | `LED5` | knob ring, upper left | 80.454 | 44.832 |
| 7 | `LED2` | fan-mode key symbol | 73.3 | 48.878 |
| 9 | `LED18` | driver seat heat 3 | 54.943 | 43.685 |
| 10 | `LED13` | driver seat cool 3 | 25.057 | 43.685 |
| 11 | `LED17` | driver seat heat 2 | 54.095 | 37.248 |
| 13 | `LED14` | driver seat cool 2 | 25.905 | 37.248 |
| 14 | `LED16` | driver seat heat 1 | 50.607 | 31.771 |
| 15 | `LED9` | driver window symbol | 12.0 | 32.978 |
| 17 | `LED15` | driver seat cool 1 | 29.393 | 31.771 |
| 18 | `LED11` | driver seat symbol | 40.0 | 27.978 |
| 19 | `LED12` | passenger seat symbol | 140.0 | 27.978 |
| 21 | `LED22` | passenger seat heat 1 | 150.607 | 31.771 |
| 22 | `LED10` | passenger window symbol | 168.0 | 32.978 |
| 23 | `LED21` | passenger seat cool 1 | 129.393 | 31.771 |
| 25 | `LED23` | passenger seat heat 2 | 154.095 | 37.248 |
| 26 | `LED20` | passenger seat cool 2 | 125.905 | 37.248 |
| 27 | `LED24` | passenger seat heat 3 | 154.943 | 43.685 |
| 29 | `LED19` | passenger seat cool 3 | 125.057 | 43.685 |
| 30 | `LED3` | recirculate key symbol | 106.7 | 48.878 |
| 31 | `LED6` | knob ring, upper right | 99.546 | 44.832 |
| 33 | `LED4` | mirror-defog key symbol | 106.7 | 59.878 |
| 34 | `LED7` | knob ring, lower right | 99.546 | 63.924 |

OUT 1, 2, 4, 8, 12, 16, 20, 24, 28, 32, 35 and 36 are open. The (x, y) are the faceplate's windows
for LP20, from the board's top-left as seen from the face.

- **Key symbols** sit inside the 13 × 8 cap, beside the tactile switch on the knob's side (5.6 mm from
  the cap's centre; the switch fills the middle), lit through the cap (D-488).
- **The knob's ring:** four LEDs on the diagonals, 13.5 mm from the shaft, toward the four keys (I-001).
- **Seat arcs:** 15 mm from the shaft, OFF at the top (D-073); cool 3-2-1 anticlockwise at −95°, −70°,
  −45° (blue), heat 1-2-3 clockwise at +45°, +70°, +95° (red), the same on both knobs.
- **Window symbols** 9.4 mm above the switch, inside its 12 × 24 slot; **seat symbols** 14.4 mm above
  the knob's shaft. I-005 asks for the window symbol on the switch's cap and the seat symbol in the
  knob's centre: both are part questions (below), so the LED sits beside the control for now.

## The screen (P201)

`J2` is a placeholder for a 128 × 64-class I²C module's own 4-pin header, in the common order
**GND, VCC, SCL, SDA**, centred over the window's top edge (a 1.3-inch module's header sits there).
**`JP1` picks its supply and is left open**: bridge 1-2 for `+5V_PNL` (what the record allows - its
`+3V3` line says "nothing else on the panel is powered from it"), or 2-3 for `+3V3`. Many modules pull
SDA / SCL up to their VCC pin: such a module at 5 V would pull the DCU's 3.3 V bus to 5 V, which the
Teensy's pins do not tolerate. The parts round picks a module whose pull-ups are on its own 3.3 V
regulator (or removes them), or bridges 2-3 and changes the record's `+3V3` note. The module's
address must differ from the driver's 0x3C (0x3D on most).

## Confirm

- **The outline and holes** (mock-up, `V-113` / `F11`); `J1`'s X near the carrier's J4 and its height
  (16.5, not the mock-up's 16) for the ribbon's few centimetres (P157).
- **The window switch:** `panel:Toggle_DPDT_SubMini_2x3_P2.54mm`, drawn here - a generic 2 × 3 grid
  (2.54 mm along the lever, poles 5.08 apart), 8 × 12 body - **not from a part's drawing**; which
  throw closes on "up" is the usual toggle's (the far terminal), confirm on the part. **A DPDT where P155
  says SPDT** (above). A lit cap or light pipe on the paddle (I-005) is a part question.
- **The seat symbol:** a fixed lit symbol in the knob's centre needs a hollow-shaft encoder or a
  ring encoder with a light pipe; none is chosen, so the symbol LED is beside the knob.
- **The screen:** `J2`'s pin order, the standoff that puts the glass at the window, the module's size,
  its supply (`JP1`) and pull-ups, its address (P201).
- **The encoders:** `panel:RotaryEncoder_Bourns_Vertical_PEC11R-4xxxF-Sxxxx` (Y6's, read from a model,
  not the Bourns drawing); S1 / S2 empty on the two N-type seat knobs.
- **The keys:** the 13 mm actuator against the faceplate and caps (LP20).
- **The LEDs:** colours (blue cool, red heat, the rest LP20's), brightness on the bench, part numbers.
- **`U2`'s footprint** (KiCad's TQFP-48 7 × 7, EP 4.11, as Lumissil p.17) and the passives' part numbers.

## 3D and `RX7_MODELS`

KiCad's own parts bring their models from `${KICAD10_3DMODEL_DIR}`. The PEC11R model is not copied
here: the footprint points at `${RX7_MODELS}/rotary-encoder-bourns-pec11r-github-daxxn/PEC11R-4230F-S0024 v7.step`,
`RX7_MODELS` = `<tree>/01-REFERENCE/model/library/electrical`; set it before rendering or exporting.
The window switch and the screen module have no model.

## Checking it

```
kicad-cli sch erc panel.kicad_sch --severity-all --exit-code-violations -o panel-erc.rpt
python3 ../../../tools/check.py --board panel
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o panel-drc.rpt panel.kicad_pcb
kicad-cli sch export svg --no-background-color -o . panel.kicad_sch
kicad-cli sch export bom --fields 'Reference,${QUANTITY},Value,Footprint,${DNP},Confirm' --labels 'Ref,Qty,Value,Footprint,DNP,Confirm' --group-by 'Value,Footprint,${DNP}' --sort-field Reference -o panel-bom.csv panel.kicad_sch
kicad-cli pcb render --side top --zoom 1.6 --quality high -w 2000 -h 1000 -o panel-top.png panel.kicad_pcb
kicad-cli pcb render --side bottom --zoom 1.6 --quality high -w 2000 -h 1000 -o panel-bottom.png panel.kicad_pcb
kicad-cli pcb export step --subst-models -f -o panel.step panel.kicad_pcb
```

Rev 0.04, 2026-10-13: ERC 0 / 0; `check.py --board panel` 79 checks, 0 mismatches; DRC 0 violations,
0 unconnected, 0 parity issues. The SVG and the BOM are committed (`JP1` and `TP1` are out of the
BOM); the renders, the STEP and the reports are rebuilt and not committed (`.gitignore`).

## Files

| File | What |
|---|---|
| `panel.kicad_pro` · `.kicad_sch` · `.kicad_pcb` | the project, the schematic and the provisional board |
| `panel.kicad_sym` · `sym-lib-table` | every symbol used, kept with the project |
| `panel.pretty` · `fp-lib-table` | the PEC11R encoder and the window switch, drawn here; the Y6 thumbstick placeholder, unused, kept for the plate's board (Y21) |
| `panel.svg` · `panel-bom.csv` | the committed picture and the parts list, `confirm` included |
| `enclosure/` | Y7's tray behind the dash, built on Y6's 200 × 70 board - stale since the panel became the climate unit's face (D-479); the unit's enclosure is `../climate-unit/` |

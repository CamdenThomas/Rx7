# Control panel — the KiCad project

*Rev 2026-10-09 (sheet rev 0.02, provisional board, Y6) · owns: what this KiCad project is for
and what it may claim. The panel's design is `../../../data/panel_ribbon.csv` and
`dcu_channels` SN18–SN20 (D-380). Read `../README.md` first: it is the fence.*

## Where it stands

**The schematic is drawn and ERC is clean** (D-452, rev 0.02 on 2026-10-09). It has nine keys on
a 3 × 3 matrix, with one 1N4148W per key, anode toward the column. A row driven low pulls its
column low through the diode, so any combination reads true and a press with every row held low
wakes the DCU. It also has four detented encoders common to GND, the thumbstick (two pots across
+3V3 and its own AGND, a push to GND), and the 20-way IDC header, pinned as `panel_ribbon`. The
panel has no processor, no CAN node and no 12 V on the ribbon (D-355, D-380). `check.py --board
panel` holds it to the record: 49 checks, 0 mismatches.

**A provisional board is laid out, routed and DRC-clean** (Y6, D-455): `panel.kicad_pcb`, 46
parts, 2 layers, 0 errors, 0 warnings, 0 unconnected, 0 parity issues. It is drawn the way
D-455 says: on a provisional outline, to the recommendation where a block is open, so an answer
changes rows and positions, not the design.

- **The outline is a guess, `confirm`.** 200 × 70 mm, R3 corners, four M3 holes 4 mm in from the
  corners. `V-113` measures the dash opening and sets the real numbers (D-455); the board's back
  silkscreen and the `Cmts.User` layer say so.
- **The faceplate side (front) carries what the hand touches**, left to right as a driver reads
  it: the mirror thumbstick and the driver-seat knob at the driver's end, the driver window keys
  (up over down), the five function keys across the top in the `0x400` bit order (defog, hatch,
  fuel door, HVAC mode, recirculate) with fan and temperature below them, the passenger window
  keys, and the passenger-seat knob at the far end. Key labels sit on `Cmts.User`.
- **The back carries everything else:** the ribbon header `J1` on the lower edge, the nine
  matrix diodes, the illumination input `J2`, the backlight resistors and the style-(b) leads.
- **Routing:** freerouting 2.5.0 through Specctra DSN/SES, 27 vias, then a GND pour on B.Cu.
  Net classes are in `panel.kicad_pro`: `Default` 0.25 mm, `ILLUM` 0.5 mm for `/ILLUM_*` and the
  backlight strings `/BL*`. Tracks the router necked below their class were set back to it.

## Both key styles are on the board (luxury 03.14 open)

Each key has two footprints wired in parallel on the same column and diode. Fit one set, never
both:

| Style | Parts | Footprint | Fitted now |
|---|---|---|---|
| (a) low-travel board switch under a faceplate cap (the recommendation) | `SW1`–`SW9` | `Button_Switch_THT:SW_PUSH_6mm_H13mm`, KiCad's own, with its 3D model | yes |
| (b) a 12–16 mm round button with a light ring, wired to the board | `SWB1`–`SWB9` | `Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical` on the back: 1-2 the switch, 3-4 the ring LED | DNP |

The alternates carry the prefix `SWB` so `check.py`'s matrix walk (one `SW` per diode) still
reads the record's nine keys. If 03.14 lands on (b), flip the DNP flags and the board is done;
if it lands on (c), a donor module, the (b) leads are where its switches wire in.

## The illumination input (01.14 open)

`J2` (JST-XH 2-way, back) takes the dash illumination lead from `L3-S1 8` (DV53, PV94): pin 1
`ILLUM_12V`, the dimmed +12 V bus, pin 2 `ILLUM_GND`, its own return to the dash ground. It never
touches the ribbon's `GND`, so no logic return runs through the lamps. It feeds only DNP parts:

- **the style-(a) backlight:** three strings of three 1206 LEDs, one string per matrix row,
  each on its own 0805 series resistor `R1`–`R3`. `LEDn` sits beside key `SWn` under its cap.
  At 13.8 V with white LEDs (3 × 2.9 V), 1 kΩ gives about 5 mA per string. Values, colour and
  whether the keys are lit at all are `confirm`;
- **the style-(b) light rings**, pins 3-4 of each `SWB` lead, assuming a 12 V ring with its own
  resistor (`confirm`).

01.14's indicator lamps (option a or c) need a 26-way ribbon and an LED driver on I2C, which
changes `panel_ribbon`. Nothing for them is drawn: the record has no conductor for them yet.

## The parts that are not chosen

- **The encoders** `SW10`–`SW13`: `panel:RotaryEncoder_Bourns_Vertical_PEC11R-4xxxF-Sxxxx`, drawn
  here because KiCad 10.0.6 has no PEC11R footprint. The origin is the shaft. A-C-B sit on 2.5 mm
  at +7.5 mm, the push pins S1/S2 on 5.0 mm at −7.0 mm, and the lugs in 1.0 × 3.0 mm slots at
  ±6.45 mm. The positions are read from the daxxn `PEC11R-4230F-S0024` model (terminals at
  −2.54/0/+2.54 mm, lugs at −6.6/+6.35 mm) and rounded to Bourns' grid: **`confirm` against the
  Bourns drawing and on the part (F11)**. A on the left is `confirm` too, though a swap only
  reverses the count in firmware. S1/S2 are left unconnected: the footprint takes the S (push)
  and N (no push) parts alike.
- **The thumbstick** `U1` (P156): `panel:Thumbstick_P156_Placeholder_2x04_P2.54mm` is a
  **PLACEHOLDER**. Its eight 2.54 mm holes carry U1's functional pins, and the 26 mm courtyard
  reserves the stick. The real footprint comes from the chosen stick's drawing (`H-008`). It has
  no 3D model.
- **The key switch height:** the 13 mm actuator is `confirm` against the faceplate (luxury LP20).

## 3D and `RX7_MODELS`

KiCad's own parts bring their models from `${KICAD10_3DMODEL_DIR}`. The PEC11R model is not
copied into this project: the footprint points at
`${RX7_MODELS}/rotary-encoder-bourns-pec11r-github-daxxn/PEC11R-4230F-S0024 v7.step`, where
`RX7_MODELS` = `<tree>/01-REFERENCE/model/library/electrical`. Set it in the environment (or
KiCad's Preferences → Configure Paths) before rendering or exporting. That model has a 30 mm
shaft; P155's 4220F has 20 mm (`confirm`). DNP parts are left out of the renders and the STEP.

## What `V-113`, 01.14, 01.15 and 03.14 change

- **`V-113`** (the dash opening): the outline, the hole positions and the spacing of the
  controls. The layout is moved and re-routed, not redrawn.
- **01.14** (lights): (b) changes nothing. (a) or (c) grows the ribbon to 26-way and adds the
  driver, which is a `panel_ribbon` change first, then the sheet.
- **01.15** (board or hand-wired): the board is drawn either way, and it costs nothing. If the
  answer is hand-wired, the sheet still holds and this layout becomes the drilling template.
- **03.14** (key style): which set is fitted, the cap or bezel drawing (LP20), and the backlight.

`H-008` lays out the final board once those are in.

## Checking it

```
kicad-cli sch erc panel.kicad_sch --severity-all --exit-code-violations -o panel-erc.rpt
python3 ../check.py --board panel
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o panel-drc.rpt panel.kicad_pcb
kicad-cli sch export svg --no-background-color -o . panel.kicad_sch
kicad-cli sch export bom --fields 'Reference,${QUANTITY},Value,Footprint,${DNP},Confirm' --labels 'Ref,Qty,Value,Footprint,DNP,Confirm' --group-by 'Value,Footprint,${DNP}' --sort-field Reference -o panel-bom.csv panel.kicad_sch
kicad-cli pcb render --side top --zoom 2.3 --quality high -w 2000 -h 800 -o panel-top.png panel.kicad_pcb
kicad-cli pcb render --side bottom --zoom 2.3 --quality high -w 2000 -h 800 -o panel-bottom.png panel.kicad_pcb
kicad-cli pcb export step --subst-models -f -o panel.step panel.kicad_pcb
```

The SVG and the BOM are committed. The renders, the STEP, the reports and the router's DSN/SES
are rebuilt from the board and are not committed (`.gitignore`).

## Files

| File | What |
|---|---|
| `panel.kicad_pro` · `.kicad_sch` · `.kicad_pcb` | the project, the schematic and the provisional board |
| `panel.kicad_sym` · `sym-lib-table` | every symbol used, kept with the project |
| `panel.pretty` · `fp-lib-table` | the PEC11R encoder and the thumbstick placeholder, drawn here |
| `panel.svg` · `panel-bom.csv` | the committed picture and the parts list, DNP and `confirm` included |
| `enclosure/` | the mount behind the faceplate (Y7): `make_enclosure.py` (parameters at the top, `V-113` the envelope; `freecadcmd make_enclosure.py`) builds the rear tray and the front frame as STEP / STL from `board.json` (`../enclosure_extract.py panel`) and `panel.step`, and fit-checks them; `confirm` until `V-113` and LP20 |

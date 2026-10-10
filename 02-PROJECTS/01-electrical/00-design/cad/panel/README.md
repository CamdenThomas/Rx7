# Control panel — the KiCad project

*Rev 2026-10-09 (sheet rev 0.03, provisional board - Y6, D-458, D-459) · owns: what this KiCad
project is for and what it may claim. The panel's design is `../../../data/panel_ribbon.csv` and
`dcu_channels` SN18–SN20 (D-380), its lights D-458. Read `../README.md` first: it is the fence.*

## Where it stands

**The schematic is drawn and ERC is clean** (rev 0.03, 2026-10-09). It has nine keys on a 3 × 3
matrix, with one 1N4148W per key, anode toward the column. A row driven low pulls its column low
through the diode, so any combination reads true and a press with every row held low wakes the
DCU. It also has four detented encoders common to GND, the thumbstick (two pots across +3V3 and
its own AGND, a push to GND), **the lights** (D-458: an IS31FL3236A driver and 35 LEDs, below)
and the **26-way** IDC header, pinned as `panel_ribbon`. The panel has no processor, no CAN node
and no 12 V on the ribbon (D-355, D-380); the ribbon's +5 V and I²C serve the lights only.
`check.py --board panel` holds it to the record: 56 checks, 0 mismatches once `panel_ribbon`
carries pins 21–26.

**It is a circuit board, ordered with the DCU's** (D-459, `P175`). The provisional board is laid
out, routed and DRC-clean: `panel.kicad_pcb`, 80 footprints, 2 layers, 0 errors, 0 warnings, 0
unconnected, 0 parity issues. It is drawn the way D-455 says: on a provisional outline, to the
recommendation where a block is open, so an answer changes rows and positions, not the design.

- **The outline is a guess, `confirm`.** 200 × 70 mm, R3 corners, four M3 holes 4 mm in from the
  corners. `V-113` measures the dash opening and sets the real numbers (D-455); the board's back
  silkscreen and the `Cmts.User` layer say so.
- **The faceplate side (front) carries what the hand touches and what lights**, left to right as
  a driver reads it: the mirror thumbstick and the driver-seat knob at the driver's end, the driver
  window keys (up over down), the five function keys across the top in the `0x400` bit order
  (defog, hatch, fuel door, HVAC mode, recirculate) with fan and temperature below them, the
  passenger window keys, and the passenger-seat knob at the far end. An LED sits above each key and
  an arc of LEDs over each knob. Key labels sit on `Cmts.User`.
- **The back carries everything else:** the ribbon header `J1` (2 × 13) on the lower edge, the
  light driver `U2` with `C1`–`C3`, `R1`, `R2` between the fan and temperature knobs, the nine
  matrix diodes, the illumination input `J2` and the style-(b) leads (both DNP), and the ribbon's
  spare on the test pad `TP1`.
- **Routing:** freerouting 2.5.0 through Specctra DSN/SES, 124 vias, then a GND pour on B.Cu.
  Net classes are in `panel.kicad_pro`: `Default` 0.25 mm, `LED5V` 0.3 mm (0.6 / 0.3 mm vias) for
  `/+5V_PNL`, `ILLUM` 0.5 mm for `/ILLUM_*`. Tracks the router necked below their class were set back
  to it, except where that came within 0.2 mm of a neighbour (those stay at 0.2 mm or more), and one
  via by U2 is 0.55 mm. U2's ground pins and the knobs' commons join the pour solid, not by spokes.

## The lights (D-458, D-462)

**`U2`, an IS31FL3236A-TQLS4**: 36 constant-current sinks, I²C, 2.7–5.5 V, eTQFP-48, −40 to
+125 °C (Lumissil, Rev. I: pinout p.2–3, address p.7, current p.11, land pattern p.17; the
pin table is in `../pin_tables.csv`). One part, chosen over two TLC59116: its logic threshold is
1.4 V at any supply (p.5), so a 5 V part reads the DCU's 3.3 V bus, and one package holds every
light.

- **Address 0x3C** (AD to GND). The DCU's bus already has 0x74 and 0x75 (the expanders, SN17) and
  0x48 (the ADC, SN29): no collision. It is write-only.
- **Supply:** `+5V_PNL`, ribbon pin 26, through a PTC on the carrier. `C1` 10 µF sits at the
  header for the LEDs' PWM current, `C2` 1 µF and `C3` 100 nF at VCC. `R2` 100 k holds SDB high, so
  the chip is on whenever the ribbon is powered and starts blank (every register 0) until the DCU
  writes it.
- **Current:** `R1` 10 k sets IMAX = 58.5 × 1.3 V / 10 k = 7.6 mA per channel (p.11). Every LED at
  full current is about 0.28 A. The brightness that reads well through a window is the bench's,
  `confirm`.
- **Dimming (D-462):** the panel follows the dash dimmer. The DCU scales every channel's PWM byte
  (256 steps) to the dimmer level and writes the update register 25h. It sets 22 kHz PWM (4Bh)
  so the ceramic capacitors do not sing (p.12). The bus runs at 100 kHz over about 1 m of ribbon
  (`confirm` on the bench).
- **Channels:** each LED has its own, anode on `+5V_PNL`, cathode to the channel. OUT1–OUT9 are the
  keys in the `0x400` bit order. OUT10–OUT16 are the fan arc and OUT17–OUT23 the temperature arc,
  both anticlockwise to clockwise. OUT24–OUT29 and OUT30–OUT35 are the driver and passenger seats:
  cool 3, 2, 1, then heat 1, 2, 3. OUT36 is open.
- **The knob arcs:** 15 mm from the shaft, so a knob up to about 25 mm across leaves them clear.
  Fan and temperature have seven steps at −60° to +60°. Each seat has three at −75° to −35° (cool)
  and three at +35° to +75° (heat). The gap at the top is OFF (D-073): the knob has no end stops,
  so the light is the only thing that shows the level.

**The faceplate's windows** (luxury LP20 draws them from this table). Each is the LED's centre in
mm from the board's top-left corner, seen from the faceplate side, x to the right and y down. The
key LEDs are 1206 and the knob LEDs 0603; the window size and any light pipe are LP20's.

| LED | What it lights | x | y |
|---|---|---|---|
| `LED1` | key light defog | 64.0 | 9.8 |
| `LED2` | key light hatch release | 82.0 | 9.8 |
| `LED3` | key light fuel-door release | 100.0 | 9.8 |
| `LED4` | key light HVAC mode | 118.0 | 9.8 |
| `LED5` | key light recirculate | 136.0 | 9.8 |
| `LED6` | key light window DRV up | 42.0 | 27.8 |
| `LED7` | key light window DRV down | 42.0 | 45.8 |
| `LED8` | key light window PASS up | 158.0 | 27.8 |
| `LED9` | key light window PASS down | 158.0 | 45.8 |
| `LED10` | fan level 1 | 63.0 | 40.5 |
| `LED11` | fan level 2 | 66.4 | 36.5 |
| `LED12` | fan level 3 | 70.9 | 33.9 |
| `LED13` | fan level 4 | 76.0 | 33.0 |
| `LED14` | fan level 5 | 81.1 | 33.9 |
| `LED15` | fan level 6 | 85.6 | 36.5 |
| `LED16` | fan level 7 | 89.0 | 40.5 |
| `LED17` | temperature level 1 | 111.0 | 40.5 |
| `LED18` | temperature level 2 | 114.4 | 36.5 |
| `LED19` | temperature level 3 | 118.9 | 33.9 |
| `LED20` | temperature level 4 | 124.0 | 33.0 |
| `LED21` | temperature level 5 | 129.1 | 33.9 |
| `LED22` | temperature level 6 | 133.6 | 36.5 |
| `LED23` | temperature level 7 | 137.0 | 40.5 |
| `LED24` | driver seat cool 3 | 3.5 | 46.1 |
| `LED25` | driver seat cool 2 | 5.7 | 41.4 |
| `LED26` | driver seat cool 1 | 9.4 | 37.7 |
| `LED27` | driver seat heat 1 | 26.6 | 37.7 |
| `LED28` | driver seat heat 2 | 30.3 | 41.4 |
| `LED29` | driver seat heat 3 | 32.5 | 46.1 |
| `LED30` | passenger seat cool 3 | 167.5 | 46.1 |
| `LED31` | passenger seat cool 2 | 169.7 | 41.4 |
| `LED32` | passenger seat cool 1 | 173.4 | 37.7 |
| `LED33` | passenger seat heat 1 | 190.6 | 37.7 |
| `LED34` | passenger seat heat 2 | 194.3 | 41.4 |
| `LED35` | passenger seat heat 3 | 196.5 | 46.1 |

These move with the keys and knobs when `V-113` sets the outline.

## Both key styles are on the board (luxury 03.14 open)

Each key has two footprints wired in parallel on the same column and diode. Fit one set, never
both:

| Style | Parts | Footprint | Fitted now |
|---|---|---|---|
| (a) low-travel board switch under a faceplate cap (the recommendation) | `SW1`–`SW9`, lit by `LED1`–`LED9` | `Button_Switch_THT:SW_PUSH_6mm_H13mm`, KiCad's own, with its 3D model | yes |
| (b) a 12–16 mm round button with a light ring, wired to the board | `SWB1`–`SWB9`, rings on `J2` | `Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical` on the back: 1-2 the switch, 3-4 the ring LED | DNP |

The alternates carry the prefix `SWB` so `check.py`'s matrix walk (one `SW` per diode) still
reads the record's nine keys. If 03.14 lands on (b), flip the DNP flags: `SWB1`–`SWB9` and `J2` in,
`SW1`–`SW9` and `LED1`–`LED9` out. The knob arcs stay either way. If it lands on (c), a donor module,
the (b) leads are where its switches wire in.

## The illumination input (style (b) only)

`J2` (JST-XH 2-way, back, **DNP**) takes the dash illumination lead from `L3-S1 8` (DV53, PV94):
pin 1 `ILLUM_12V`, the dimmed +12 V bus, pin 2 `ILLUM_GND`, its own return to the dash ground. It
never touches the ribbon's `GND`. It now feeds only the style-(b) light rings, pins 3-4 of each
`SWB` lead, assuming a 12 V ring with its own resistor (`confirm`). Y6's backlight strings (`R1`–`R3`
off this input) are gone: the key LEDs are the driver's channels. `R1` and `R2` are now the
driver's parts.

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
- **The LEDs:** colour (blue for cool, red for heat, the rest LP20's), brightness and part number
  are `confirm`; the footprints are KiCad's `LED_1206_3216Metric` and `LED_0603_1608Metric`.
- **`U2`'s footprint** is KiCad's `TQFP-48-1EP_7x7mm_P0.5mm_EP4.11x4.11mm`, which matches
  Lumissil's eTQFP-48 land pattern (4.11 mm pad, p.17). KiCad ships no model for it, so it renders
  as bare pads. `confirm` against the part bought.

## 3D and `RX7_MODELS`

KiCad's own parts bring their models from `${KICAD10_3DMODEL_DIR}`. The PEC11R model is not
copied into this project: the footprint points at
`${RX7_MODELS}/rotary-encoder-bourns-pec11r-github-daxxn/PEC11R-4230F-S0024 v7.step`, where
`RX7_MODELS` = `<tree>/01-REFERENCE/model/library/electrical`. Set it in the environment (or
KiCad's Preferences → Configure Paths) before rendering or exporting. That model has a 30 mm
shaft; P155's 4220F has 20 mm (`confirm`). DNP parts are left out of the renders and the STEP.

## What `V-113` and 03.14 change

- **`V-113`** (the dash opening): the outline, the hole positions and the spacing of the
  controls, and with them the window table. The layout is moved and re-routed, not redrawn.
- **03.14** (key style): which set is fitted, the cap or bezel drawing (LP20), and whether
  `LED1`–`LED9` or the rings light the keys.

01.14 (the lights, D-458) and 01.15 (a board, D-459) are answered and drawn. `H-008` lays out the
final board once `V-113` and 03.14 are in.

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

# DCU carrier — the KiCad project

*Rev 2026-10-09 (sheet rev 0.02, board rev 0.02 provisional - Y5) · owns: what this KiCad project
is for, what it may claim, and how to start. The board's design is `../../../data/dcu_channels.csv`.
That is the record, and this is a drawing of it. Read `../README.md` first: it is the fence.*

## Where it stands

**The board is laid out, routed and 3D-modelled on a PROVISIONAL outline (Y5).** `kicad-cli pcb drc
--severity-all --exit-code-violations --schematic-parity` reads 0 violations (errors and warnings),
0 unconnected, 0 parity issues; ERC is 0 / 0. `../check.py --board dcu` holds every record pin; its
one remaining line is the check's own pin parser against the record's wording (SN17 / SN24), not the
sheet. `H-002` stays the final board: it gates on `V-102`, luxury `W-332` and this row. Nothing here is
ordered (F5).

- **The sheet** (rev 0.02): every functional block is on its real package, its pin numbers held to
  `../pin_tables.csv` by `check.py` (S-480 to S-489):
  - U5-U8 **BTS3011TE**, TO-252-5: 1 IN, 2 VDD, 3 OUT, 4 STATUS, 5 GND (the source - the seat
    current leaves here), tab 6 = OUT. **STATUS** is open-drain and latching on an over-temperature
    shutdown (datasheet section 7.1, p.20): the four are wired-OR on `SEAT_STATUS`, pulled up by R58
    10 k to `+3V3` (the R_STATUS of the application table, p.40) and read on expander **P17**. The
    latch clears with IN low and STATUS high, so firmware drops all four inputs to clear it; which
    switch tripped is not told apart. `confirm`.
  - U9 **BTT6050-1ERA**, PG-TSDSO-14: 3 GND (47 Ω PROFET ground), 4 IN, 5 DEN, 6 IS, 10-12 OUT, tab VS
    on `+12V_CMF`.
  - U10 **BTT6200-4ESA**, PG-TSDSO-24: 2 IN0, 4 GND, 5 IN1, 6 DEN, 7 IS, 8 DSEL0, 9 IN2, 10 IN3,
    11 DSEL1, 13 OUT3, 17 OUT2, 20 OUT1, 24 OUT0, tab VS on `+12V_LOGIC`; DEN / DSEL0 / DSEL1 on
    expander P11-P13 (SN22).
  - U11 **DRV8962-Q1**, HTSSOP-44 (SLVSHN2A): every pin. The three pins of each OUT paralleled, VM on
    2 / 11 / 12 / 21, PGND1-4 and GND to the exposed pad, IPROPI1-4 each to its own 1.5 k (`confirm`
    against the stall current, W-332), **VCC tied to DVDD** (p.4: "when separate logic supply voltage
    is not available, tie the VCC pin to the DVDD pin"), VREF on `+3V3`. **MODE to GND**: on this part MODE is not a control
    mode but the output slew rate, low = 140 ns rise / fall, the quieter one (p.4, p.7, section 6.4
    p.12); the part always runs as four independent half-bridges, EN/IN per channel, as SN17 wants.
    **OCPM to GND = latch-off** (section 6.10.4, p.19): a stalled mirror motor latches the driver off
    until an nSLEEP reset pulse, which the firmware gives through the expander (P07). `confirm`.
  - U2 TPS54560B-Q1 (DDA), U4 INA180A1 and U12 TCA9539-Q1 were already on their real pins.
- **CONVENTIONS §5 holds**: `+12V_LOGIC` and `+12V_CMF` share no part, and only U4 touches both `GND`
  and `PGND`. On the board the two grounds share no copper either.

**R11 applies to all of it:** nothing on this board has been measured. The outline is a guess, the DT13
hole pattern is TE's drawing, the Teensy socket is PJRC's card, and the mirror stage's values wait on
luxury `W-332`.

## The board

**Outline: 180 x 80 mm, PROVISIONAL - `confirm` until `V-102` (D-455).** The brief's 120 x 80 does
not hold the three flanged DT13s side by side on one edge: their courtyards (flange ears included) are
60.3 + 56.1 + 44.1 mm, so the connector edge needs about 165 mm. Four M3 holes (3.2 mm, NPTH) 4 mm in
from each corner. 2 layers, 1.6 mm, 1 oz.

- **The connector edge** is the bottom long edge: J9 `DP-DCU-B` DT13-12PA (left, x 38.1), J2
  `DP-DCU-C` DT13-08PA (centre, x 97.2), J1 `DP-DCU` DT13-06PA (right, x 148.2). The board edge sits on
  each flange's rear face (4 mm behind its front face), flush for panel mounting through one enclosure
  wall (D-362).
- **The opposite edge** (grommets, D-362): J4 the panel ribbon (2 x 10 IDC, top left), the Teensy
  (J10, socketed, along the top), the three servo headers J6-J8 each with its 470 µF beside it, J3 the
  cabin NTC lead and J5 the blower pigtail (top right).
- **Blocks**: the window quad U10 and the mirror bridge U11 over J9 (their outputs face the pins), the
  releases Q1 / Q2 beside them, the mirror heat U9 between J9 and J2; the four seat switches U5-U8 over
  J2, tabs down onto their pins; the shunt R15 / R16 and U4 to their right; the logic buck U1 and the
  servo buck U2 top right, under the servo headers they feed; CAN U3, the wake stage and the
  outside-air input over J1; the expander U12 top left beside the ribbon.

**Copper.** The comfort paths are pours on F.Cu, `COMFORT` and `PGND`, 0.5 mm from everything else,
connected solid:

- each seat return from its switch's tab (drain) down to its `DP-DCU-C` pin 1-4;
- `CMF_RTN`, the four sources (pin 5) along one bus to R15 / R16;
- `PGND`, from the shunt down the right of J2 and under its body to pins 6 / 7, with D4's anode;
- `V12C_RAW`, pin 5 under the body and up the left of J2 to D3.

The INA180's two inputs are Kelvin lines from R15's own pads. `GND` is poured on both layers, stitched
top to bottom (about 100 vias), and the DRV8962's exposed pad carries 27 vias into it. The fine-pitch
power pins (DRV8962, BTT6050, BTT6200, LMR36015) are necked out at their pad width and widen to their
class past the toes; both buck switch nodes are short drawn tracks. The rest was routed with
freerouting 2.5.0 (Specctra DSN / SES, the project's clearances + 0.05 mm) and finished with a small
grid router; necks the router narrowed below 0.2 mm were widened to 0.2. No isolated copper is left.

| Net class | Track | Clearance | Nets |
|---|---|---|---|
| `Default` | 0.25 | 0.2 | signals, `+3V3` (the Teensy's own output, light loads), `GND` (poured) |
| `COMFORT` | 4.0 or a pour | **0.5** | `V12C_RAW`, `SH_DRV_RTN`, `SH_PASS_RTN`, `SC_DRV_RTN`, `SC_PASS_RTN`, `CMF_RTN` - up to 18 A |
| `PGND` | 4.0 or a pour | **0.5** | `PGND` |
| `PWR_LOGIC` | 0.6 | 0.2 | `+12V_LOGIC`, `V12L_RAW`, `+5V`, `BUCK_SW` |
| `SERVO` | 1.0 | 0.2 | `+5V_SERVO`, `SRV_SW`, `+12V_CMF` |
| `DRIVE` | 0.8 | 0.2 | `MIR_COM`, `MIR_L`, `MIR_R`, `MIR_CLUTCH`, `MIRROR_HEAT` |
| `WIN` | 0.5 | 0.2 | `WIN_DRV_UP/DN`, `WIN_PASS_UP/DN`, `REL_HATCH`, `REL_FUEL`, `WAKE_OUT` |

One rule relaxes a clearance, with its reason in `dcu-carrier.kicad_dru`: pad-to-pad inside U4-U8
only, because the TO-252-5 legs (1.14 mm pitch) and the SOT-23-5 pins (0.95 mm) cannot hold 0.5 mm
between their own comfort and logic pins. Their tracks and pours still keep 0.5 mm.

## The footprints

| Ref | Footprint | Source |
|---|---|---|
| J1 / J2 / J9 | `dcu-carrier:DT13-06PA` / `DT13-08PA` / `DT13-12PA` | TE application spec 114-151046 Rev A p.5-6: pins Ø1.88 on 4.45 mm in two rows 6.35 apart (pads 2.9), three Ø3.43 flange posts (two at the sides, level with the far row, at ±10.87 / ±13.59 / ±17.55 for 6 / 8 / 12 ways, one on the centre line 11.43 toward the flange); the same pattern as the ICU's two, turned 180°. The 3D models sit as on the ICU's (TE's model frame turned onto the footprint, not checked against a part) |
| J3, J5 | `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical` | KiCad |
| J4 | `Connector_IDC:IDC-Header_2x10_P2.54mm_Vertical` | KiCad |
| J6-J8 | `PinHeader_1x03_P2.54mm_Vertical`, pin 1 signal, 2 V+, 3 GND | KiCad; the FS5115M lead order `confirm` |
| J10 | `dcu-carrier:Teensy41_Socket` | the ICU's, its outline now the ICU's corrected one (body -1.27 to 59.69 mm along the rows) |
| L2 | `Inductor_SMD:L_Coilcraft_XAL7030-682` | KiCad; 6.8 µH, Isat ≥ 7 A `confirm` |
| U1 | `Package_DFN_QFN:Texas_RNX0012C_VQFN-14-11-1EP_2x3mm_P0.5mm_EP0.25x1.825mm` | KiCad (as the ICU) |
| U2 | `Package_SO:HSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm` | KiCad (TI DDA), 6 vias in the pad |
| U9 | `dcu-carrier:Infineon_PG-TSDSO-14-22` | KiCad's geometry, exposed pad numbered TAB and drawn 6.4 x 2.65 (BTT6050-1ERA Fig. 53; KiCad's is 4.0) `confirm` |
| U10 | `dcu-carrier:Infineon_PG-TSDSO-24-21` | drawn from BTT6200-4ESA Fig. 30: 24 leads at 0.65, pads 1.31 x 0.40 at ±2.85, body 8.65 x 3.9, exposed pad 6.4 x 2.77 = TAB `confirm` |
| U11 | `Package_SO:HTSSOP-44-1EP_6.1x14mm_P0.635mm_EP5.2x14mm_Mask4.31x8.26mm` | KiCad; the 27 thermal vias are placed on the board rather than taken from the `_ThermalVias` variant |

## 3D models: `RX7_MODELS`

The vendor models (the TE DT13s, the XenGi Teensy 4.1, Infineon's PG-TSDSO packages) are not ours to
publish, so they are not in this folder: the footprints point at `${RX7_MODELS}/<cad row>/<file>`,
and `RX7_MODELS` is the local CAD library `01-REFERENCE/model/library/electrical` (gitignored,
catalogued in the `01-REFERENCE` `cad` table). Set it once — KiCad: **Preferences → Configure Paths →
+**, name `RX7_MODELS`; terminal: `export RX7_MODELS=$HOME/dev/Rx7/01-REFERENCE/model/library/electrical`
(Mac) or the Fedora path. Without it those parts show bare pads. Three still do:

- **J2**: TE's DT13-08PA model is still zipped in its library folder
  (`deutsch-dt13-08pa-te/dt13-08pa_te-cvm-3d_stp.zip`); the footprint names the file inside it,
  `c-dt13-08pa-99-3d.stp`, and picks it up once it is extracted there. Its placement copies the 12-way's,
  `confirm`.
- **U1** and **U11**: TI publishes no free model (RNX0012C, DDW0044) and KiCad 10 ships none; they are
  left named.

```
kicad-cli pcb render --side top -o dcu-carrier-top.png dcu-carrier.kicad_pcb
kicad-cli pcb render --side bottom -o dcu-carrier-bottom.png dcu-carrier.kicad_pcb
kicad-cli pcb export step --subst-models -o dcu-carrier.step dcu-carrier.kicad_pcb
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o dcu-carrier-drc.rpt dcu-carrier.kicad_pcb
```

The renders and the STEP (about 23 MB) are built, never committed (`.gitignore`).

## What V-102 and W-332 change

- **`V-102`** (the space behind the centre stack) sets the outline and the hole positions. If the
  three connectors cannot share one 165 mm edge, the comfort receptacle J2 is the one to move to a short
  edge, and its pours go with it. The enclosure (`P152`) is drawn around the result.
- **Luxury `W-332`** (the mirror stage) sets the stall current: the IPROPI resistors R37 / R55-R57, the
  `DRIVE` track width and U11's copper. It does not move the layout.

## What the measurement pass fixes

| Measure | On | Fixes |
|---|---|---|
| Depth, width, height behind the centre stack | the car (`V-102`) | the outline, the holes, the enclosure |
| Pin pitch, hole Ø, the three flange posts, flange-to-pin-field, the flange's rear face against the board edge, cavity 1's corner | the DT13-06PA / -08PA / -12PA in hand (`P122`, `P153`) | `DT13-*` |
| Row spacing, socket height, underside clearance | a Teensy 4.1 on its headers | `Teensy41_Socket` |
| Exposed pad size, lead span | a BTT6050-1ERA and a BTT6200-4ESA | `Infineon_PG-TSDSO-14-22` / `-24-21` |
| Lead order of the FS5115M servo plug | a servo | J6-J8 |
| Stall current of a mirror motor | luxury `W-332` | R37 / R55-R57, `DRIVE` |

**Every other `confirm` on the board**: the XAL7030's saturation current; STATUS's wired-OR and its
clearing; OCPM latch-off and its reset by nSLEEP; the comfort currents (`V-101`) the 0.5 mm / pour
sizing assumes (18 A through the shunt on 1 oz F.Cu); the I²C address 0x74; the sheet's own "what this
sheet does not know" box.

## What it may and may not claim

The same as `../icu-carrier/README.md`, and for the same reasons.

**May:** how the parts on the carrier connect to each other and where they sit on a guessed outline.

**May not:** anything about the car, the harness or the drops. `DP-DCU 1` and `DP-DCU-B 10` appear here
only as pins on the board edge; what is on the other side belongs to `cavities.csv`. **If this project
and the record disagree, the record is right.**

## Checking it

```
kicad-cli sch erc dcu-carrier.kicad_sch --severity-all -o dcu-carrier-erc.rpt
kicad-cli sch export svg --no-background-color -o . dcu-carrier.kicad_sch
kicad-cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},${DNP}' --labels 'Ref,Value,Footprint,Qty,DNP' --group-by 'Value,Footprint' -o dcu-carrier-bom.csv dcu-carrier.kicad_sch
python3 ../check.py --board dcu
```

## Files

| File | What |
|---|---|
| `dcu-carrier.kicad_pro` · `.kicad_sch` | the project (net classes included) and the schematic |
| `dcu-carrier.kicad_pcb` · `.kicad_dru` | the provisional board and its one relaxed rule |
| `dcu-carrier.kicad_sym` · `sym-lib-table` | every symbol used, kept with the project |
| `dcu-carrier.pretty` · `fp-lib-table` | the footprints drawn here: the three DT13s, the two PG-TSDSO packages, the Teensy socket |
| `dcu-carrier.svg` · `dcu-carrier-bom.csv` | the committed picture and the BOM export: the reviewable forms of a change |
| `CONVENTIONS.md` | how to draw it, and what differs from the ICU |
| `TARGET.md` | the drawing checklist from `dcu_channels`, a snapshot and not a link |

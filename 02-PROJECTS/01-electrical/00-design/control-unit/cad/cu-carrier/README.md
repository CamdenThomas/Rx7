# DCU carrier — the KiCad project

*Rev 2026-10-13 (sheet rev 0.07 - Y44's fix pass, D-549, values only; rev 0.06 was Y44's one value, 0.05 Y42, 0.04 D-458, D-465, Y12) · owns: what this KiCad project
is for, what it may claim, and how to start. The board's design is `../../../../data/dcu_channels.csv`.
That is the record, and this is a drawing of it. Read `../../../README.md` first: it is the fence.*

> **Y49 / D-593 (2026-10-14): the dash-light stage is on the sheet, not yet on the board.** U17, a fifth BTS3011TE
> (IN from Teensy 11 through R73 100 R, R74 10 k to +3V3; STATUS on U13 P03 with R75 10 k; GND to PGND after the
> comfort shunt; OUT on `DASH_OUT`, class DRIVE, to TP2 until the header), and the wake request moved from Teensy 11
> to U13 P02. ERC 0; `check.py --board cu-carrier` 172 / 0. The board is rev 0.06 until Y54 places the stage beside the new
> header: its `--schematic-parity` DRC names exactly U17, R73-R75 and TP2 missing and J10 pad 13 / U13 pads 6-7 on
> their old nets. **Edit a copy of this whole folder** - a board saved by KiCad's Python without its .kicad_pro beside
> it gets default rules and writes them over this project's.

> **D-582 (2026-10-14): the connector edge changes.** The three DT13s (J1, J2, J9) give way to one CMC 48 header carrying every conductor the unit has, DP-DCU 1-48 - and the nets that went out on the upper board (J3, J5-J8, the dash-light stage) and the CUR's lines (the ribbon's plate nets) come to it too. Y54 draws that, once block 01.57 has picked the connector family; until then this board is as drawn, `check.py --board cu-carrier` still holds it to the old housings, and the scene hides J1 / J2 / J9.

## Where it stands

**2026-10-13 (Y44, D-549): sheet rev 0.07 - what the independent read found (D-548), values only.** No copper,
mask, silkscreen or drill changed: `fab/` was plotted again and every file is the same but its date, so the zip
is the one Y42 issued. ERC 0 / 0; DRC 0 violations, 0 unconnected, 0 parity; `check.py --board cu-carrier` 171 checks,
0 mismatches.

- **Q1 / Q2, the release selects, are Vishay SQ2364EES** (75975: 60 V, 0.245 ohm at 1.5 V on the gate, threshold
  0.46-1.0 V, gate +-8 V, SOT-23 G1 S2 D3). They are switched from Teensy pins at 3.3 V through 100 R with a 10 k
  pull-down, and the SQ2362CES named before has no on-resistance given under 4.5 V. D7 / D8 clamp the drains
  under 50 V.
- **Q4, the wake switch's driver, is MMBT5551** (160 V): its collector stands at the rail through R43, and the
  rail is clamped at 53 V. **D1, the logic input diode, is SL310A** (100 V 3 A, SMA), for the same reason.
- **C27, the DRV8962's charge-pump capacitor (CPH - CPL), is 100 nF 100 V**, the part on C25 / C30: TI's pin
  table (SLVSHN2A) asks 0.1 uF, VM-rated; 22 nF was drawn.
- **Not changed, to know at the bench:** a +3V3 track on the back passes 2.88 mm from H1's centre: **a nylon
  washer, or a nylon standoff, at H1**. The ribbon plug on J4 stands 4.9 mm in front of the Teensy's USB port:
  plug the USB lead in before the ribbon. GND and PGND meet only in the harness (D-382): with DP-DCU unplugged
  and DP-DCU-C live, the servo buck's input has no return but through the driver ICs' pins, so plug DP-DCU
  first and unplug it last. The DT13 pad numbering waits on the part in hand (D-548, V-117).

`fab/` also holds two hand-assembly drawings, `cu-carrier-revA-assembly-top.svg` and `-bottom.svg` (the back mirrored, to read
as you look at it): the outline, every part's outline and pads, and its reference in the middle of the part; the
values are in `control-unit/data/cu-carrier-revA-bom.csv` by reference. `00-design/tools/assembly.py` rebuilds them (KiCad's Python);
`00-design/tools/fabpack.py` re-plots the gerbers and drill files and writes the zip.

**2026-10-13 (Y42): rev 0.05 - what pricing the order found, made right before the boards are ordered (D-541).**
`fab/` is bench revision A re-issued from this board: the zip keeps its name, and the rev 0.04 package must not be
ordered. ERC 0 / 0; DRC 0 violations, 0 unconnected, 0 parity; `check.py --board cu-carrier` 171 checks, 0 mismatches.

- **Q3, the wake switch, was drawn gate / drain / source on a SOT-23.** Every SOT-23 P-FET is gate 1, source 2,
  drain 3 (Vishay 66894, top view), so the part would have sat drain to `+12V_LOGIC` and source to `WAKE_OUT`:
  its body diode holds the wake line at 12 V and the car never sleeps. The symbol is `Q_PMOS_GSD` now, pad 2 is
  `+12V_LOGIC` and pad 3 `WAKE_OUT`; the two short runs at its pads were re-laid and the `WAKE_OUT` via moved
  1.9 mm, to (152.15, 44.75). The part is **SQ2361ES** (60 V): its source sits on a rail the SMBJ33A clamps at
  53.3 V, so D-273's rule asks 60 V, and the SQ2351ES the sheet named is a 20 V part.
- **D2, D4 (SMBJ33A) and D7, D8 (SMAJ40A) are one-way parts and were drawn with two anodes**, pad 1 - the end
  the silkscreen marks as the cathode - on ground. Fitted to the mark they conduct forward: D2 / D4 short their
  inputs, D7 / D8 hold the hatch and fuel-door relays on. The symbol is `D_TVS_Uni` (pin 1 the cathode) and each
  footprint is turned half a turn in place: the same copper, the mark at the rail or drain end.
- **C1, C8, C29 are 68 µF 63 V** (Panasonic EEE-FK1J680UP), not 100 µF. Each sits across an SMBJ33A, so the same
  rule asks more than 53.3 V and a 50 V part is out; in the FK series 100 µF 63 V is a 10 × 10.2 can (size G, lands
  4.1 × 2.0 with 4.6 between) and the footprint drawn is the 8 × 10.2 one (size F), whose largest 63 V value is
  68 µF. The record names no value for this capacitor (`dcu_channels` gives the buck's ceramics), so the value
  moved and the board did not; 100 µF needs the 10 mm footprint and room it does not have here without a re-lay.
- **Values that follow the cart**: C31-C33 470 µF 16 V (the same can as 10 V); Q1 / Q2 were SQ2362CES or PMV37ENEA
  here (Nexperia lists PMV37ENEA in production, but four distributors had none) and are SQ2364EES since rev 0.07,
  above.
- **Q3's gate divider (Y44, sheet rev 0.06, a value only): R43 is 18 k, was 1 k** (R42, gate to source, stays
  10 k). With 1 k the gate saw ten elevenths of the rail while the wake is asserted, past the part's ±20 V once
  the rail passed 22 V. Now it sees 10 / 28: 3.2 V at 9 V, 4.3 at 12, 5.1 at 14.4, 8.6 at 24 and 19.0 V at the
  SMBJ33A's 53.3 V clamp. Q3 carries milliamps (a diode into the wake strip's bleed resistor), and Vishay 66894
  gives a threshold of 2.5 V at most and about 0.6 A at 3 V, so 3.2 V is on for that load. No copper, mask,
  silkscreen or drill changed: `fab/` was re-plotted and compared, every file the same but its date.

These four boards have no generator (only the left plate does): the change was made by two scripts on the sheet and
the board themselves - nodes replaced in the `.kicad_sch` / `.kicad_sym`, the board through KiCad's `pcbnew`.

**2026-10-12 (Y17): bench revision A (board rev 0.04) is packaged under `fab/`** - gerbers, Excellon drill
(PTH / NPTH, maps), `cu-carrier-revA-gerbers.zip` and `cu-carrier-revA-bom.csv` (MPNs `confirm` where the sheet
does not name them; the D-489 / D-455 parts listed as not fitted), from this board on its provisional outline, for
the bench order of D-490; the final board follows F11.

**2026-10-12 (Y20, D-492): J4's pins 9-12 carry the new names** - `ENC_FAN_A` / `ENC_FAN_B` → `ENC_CENTRE_A` / `ENC_CENTRE_B`, `ENC_TEMP_A` → `ENC_CENTRE_PUSH`, `ENC_TEMP_B` → `ROW4` - on the sheet's labels and the Teensy symbol's pin names, and the board's nets renamed to match (no footprint or copper moved; the same Teensy pins 40 / 41 / 34 / 35). ERC 0, DRC 0 / 0 with 0 parity issues, `00-design/tools/check.py --board cu-carrier` 0 mismatches. The `fab/` package still carries the old names in its netlist attributes; the copper is the same.

**Sheet and board are both rev 0.04 (Y12, 2026-10-11).** The sheet carries D-458 and D-465; ERC is 0 / 0 and
`00-design/tools/check.py --board cu-carrier` reads 0 mismatches:

- **J4 is a 2 x 13 keyed IDC header** (26-way, D-458). Pins 1-20 keep their nets. 21 and 23 are
  `GND`. 22 `PNL_SDA` and 24 `PNL_SCL` are the I²C bus (Teensy 18 / 19, the bus of U12, U13 and U15)
  through **R71 / R72, 100 Ω** series resistors. 25 `SPARE` ends on the test pad **TP1**. 26
  `+5V_PNL` is the logic `+5V` through **F1, a 0.5 A-hold PTC** (1206L050 class, `confirm`), so a
  short on the panel trips F1 and never browns out the Teensy. No BAT54S clamp: there is no room for
  one by J4. The panel's driver has 8 kV HBM on its pins, the Teensy has its own clamps, and the
  100 Ω limits the current into both (`confirm`). The panel bus runs at 100 kHz (`confirm`).
- **R39 / R41, the K3 / K4 select gate pull-downs, are 10 kΩ** (were 100 kΩ, D-465). Each sits gate
  to source behind its 100 Ω series resistor, so a floating Teensy pin cannot fire a release: an empty
  socket, reset, boot or an unprogrammed part. The 10 kΩ also holds the gate against drain-gate
  coupling when the relay coil switches. A driven pin pays 0.33 mA for it.

**The top-left block was re-laid for the 2 x 13 header (Y12).** Its courtyard (41.8 mm) is 1.9 mm longer
than the gap the 2 x 10 had between H1's screw head and the Teensy's USB end, so:

- **J4 sits three pitches (7.62 mm) further left**, pin 1 at (6.38, 7.6): pins 7-26 stand on the 2 x 10's
  pads 1-20, and the header's right end, with the 13 mm the bus needs to reach the Teensy, is where it
  was. The Teensy socket J10 did not move.
- **H1 moved to (4, 15)**, under the header's left end (the other three holes stay 4 mm from their
  corners). `confirm` with `V-102` / `CK26`.
- **F1, R72, R71 stand in the gap between the header and the Teensy**, by pins 21-26: F1 with pad 1 on the
  +5V track and pad 2 straight to pin 26; R72 beside the I²C clock's via; R71 astride the +3V3 trunk with
  pad 1 on the SDA trunk. **TP1** is on the bottom side beside pin 25.
- The six 0805s H1 landed on moved: R52 / R54 between H1 and U12, R53 / R3 / C24 below H1, R51 onto
  the SDA trunk above U12.

An earlier placement (pin 1 3.0 mm left, the new parts in the old H1 corner) left four nets open: its
three extra columns stood in the bus's way to the Teensy, and +5V lost its way round the header.

**D-479 (2026-10-11): this board now lives inside the Control Unit**, one enclosure with the
control panel's board on its face, like a stereo head unit, with only sealed connector halves outside.
The panel ribbon (J4) stays inside the box, and nothing leaves through a grommet: the servo leads
(J6-J8), the blower duty (J5) and the cabin sensor (J3) go out on a sealed half of their own. The
connector edge is full (160.5 of 165 mm), so that half, `DP-DCU-D`, is a fourth DT13-12PA in a second
row above J9, on a small upper connector board joined to J6-J8, J5 and J3 by short plug-in leads
(D-480, parts P194-P196). **This board does not change for it.** The unit's mock-up is `../cu-assembly/`
(`Y14`), the upper board's drawing is `Y15`. The Y7 box in `enclosure/` is the old DCU-only box, kept
until the unit's enclosure replaces it.

**The board is laid out, routed and 3D-modelled on a PROVISIONAL outline (Y5), with the open blocks'
worst case drawn in (Y11, D-455) and the 26-way header (Y12).** `kicad-cli pcb drc --severity-all
--exit-code-violations --schematic-parity` reads 0 violations (errors and warnings), 0 unconnected,
0 parity issues; ERC is 0 / 0. `00-design/tools/check.py --board cu-carrier` holds every record pin; its one remaining line
is a note on DP-DCU-B 12, wired here to the clutch stage for block 02.15 behind a sealing plug. `H-002`
stays the final board: it gates on `V-102`, luxury `W-332` and this row. Nothing here is ordered (F5).

- **The sheet** (since rev 0.03): every functional block is on its real package, its pin numbers held to
  `00-design/tools/pin_tables.csv` by `check.py` (S-480 to S-489):
  - U5-U8 **BTS3011TE**, TO-252-5: 1 IN, 2 VDD, 3 OUT, 4 STATUS, 5 GND (the source - the seat
    current leaves here), tab 6 = OUT. **STATUS** is open-drain and latching on an over-temperature
    shutdown (datasheet section 7.1, p.20): the four are wired-OR on `SEAT_STATUS`, pulled up by R58
    10 k to `+3V3` (the R_STATUS of the application table, p.40) and read on the second expander
    **U13 P00** (Y11; U12 P17 went back to the A/C clutch). The
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
- **The provisions** (Y11, the `PROVISIONS` box; D-455: the worst case of each open block, so an answer
  is a fitting change, not a redesign). Every part is **DNP** with its block and reason in its `Note`
  field, except U13 and C38:
  - **U13** TCA9539-Q1 at **0x75** (A0 high, A1 low), fitted: P00 `SEAT_STATUS`, P01 the radar alert,
    P02-P17 spare. Same I²C bus as U12 (R51 / R52), INT wired-OR on `EXP_INT` (R53, Teensy 12), RESET
    shared on `EXP_RESET` (R54): a reset holds both expanders' ports as inputs.
  - **A/C clutch** (engine 02.15 (b)): U12 **P17** `AC_CLUTCH_CMD` → R59 4.7 k (R60 10 k off at reset) →
    **U14 BTT6050-1ERA** high side, VS on `V12C_RAW` (the comfort input ahead of D3, so a ~4 A coil never
    passes the B560C), OUT `AC_CLUTCH` on **DP-DCU-B 12** (the one free cavity of the three receptacles).
    DEN low (R61), IS on R62 1.2 k unread, 47 Ω ground (R63) - as U9. The coil returns at the compressor
    and must carry its own diode (EAS 60 mJ); F29 (7.5 A) needs 10 A with it - `confirm` (V-101).
  - **A/C pressure** (02.15 (b)): **J11** a 3-way PLACEHOLDER lead (no drop cavity is free for its three
    wires), 0.5-4.5 V ratiometric `confirm`, 10 k / 20 k + 100 nF + BAT54S → **U15 ADS1115-Q1** (0x48,
    VSSOP-10) AIN0; the sensor supply the same way on AIN2; AIN1 / AIN3 grounded, spare. **U16
    TPS7B4250-Q1** makes `SENS_5V` from logic 12 V, tracking `+5V` and proof against a short to battery.
  - **Radar alert** (luxury 03.12 / Z-002): **J12** a 2-way PLACEHOLDER lead → 47 k / 22 k + 100 nF +
    BAT54S → U13 P01; R68 10 k to logic 12 V only for an open-collector output (`confirm`).
  - **DP-DCU-C 8** (J2 pin 8) on `PGND`: 01.26 (a)'s third comfort ground. The record keeps the cavity a
    sealing plug until 01.26 answers; the copper is there either way.
- **CONVENTIONS §5 holds**: `+12V_LOGIC` and `+12V_CMF` share no part, and only U4 touches both `GND`
  and `PGND`. On the board the two grounds share no copper either.

**R11 applies to all of it:** nothing on this board has been measured. The outline is a guess, the DT13
hole pattern is TE's drawing, the Teensy socket is PJRC's card, and the mirror stage's values wait on
luxury `W-332`.

## The board

**Outline: 180 x 80 mm, PROVISIONAL - `confirm` until `V-102` (D-455).** The brief's 120 x 80 does
not hold the three flanged DT13s side by side on one edge: their courtyards (flange ears included) are
60.3 + 56.1 + 44.1 mm, so the connector edge needs about 165 mm. Four M3 holes (3.2 mm, NPTH): H2-H4
4 mm in from their corners, H1 at (4, 15) below the ribbon header (Y12). 2 layers, 1.6 mm, 1 oz.

- **The connector edge** is the bottom long edge: J9 `DP-DCU-B` DT13-12PA (left, x 38.1), J2
  `DP-DCU-C` DT13-08PA (centre, x 97.2), J1 `DP-DCU` DT13-06PA (right, x 148.2). The board edge sits on
  each flange's rear face (4 mm behind its front face), flush for panel mounting through one enclosure
  wall (D-362).
- **The opposite edge** (grommets, D-362): J4 the panel ribbon (2 x 13 IDC, D-458; in the top left
  corner, pin 1 at (6.38, 7.6), its courtyard from 0.7 to 42.5 mm along the edge), the Teensy (J10,
  socketed, along the top, pad 1 at (50, 18), its courtyard from 47.4 mm), the three servo headers J6-J8
  each with its 470 µF beside it, J3 the cabin NTC lead and J5 the blower pigtail (top right).
- **Blocks**: the window quad U10 and the mirror bridge U11 over J9 (their outputs face the pins), the
  releases Q1 / Q2 beside them, the mirror heat U9 between J9 and J2; the four seat switches U5-U8 over
  J2, tabs down onto their pins; the shunt R15 / R16 and U4 to their right; the logic buck U1 and the
  servo buck U2 top right, under the servo headers they feed; CAN U3, the wake stage and the
  outside-air input over J1; the expander U12 top left below the ribbon, with the panel lines' F1 / R72 /
  R71 at the header's right end and TP1 under it (Y12).
- **The provisions (Y11)**: the clutch stage U14 with R61-R63 on the **bottom side**, under DP-DCU-B's
  body right of its pins: OUT runs a 1.5 mm B.Cu track straight to pin 12, the tab is fed from the
  `V12C_RAW` pour by four vias and a 2 mm track; R59 / R60 also on the bottom, under the end of U12 P17's
  route. U13 with C38 at the right over J1, U16 and C40-C42 beside it, J11 on the right edge; U15 and the
  two analog front ends along the top right under J3 / J5; J12 and the radar front end top right
  beside J5. `confirm` the bottom-side parts against the enclosure's underside clearance (Y7).

**Copper.** The comfort paths are pours on F.Cu, `COMFORT` and `PGND`, 0.5 mm from everything else,
connected solid:

- each seat return from its switch's tab (drain) down to its `DP-DCU-C` pin 1-4;
- `CMF_RTN`, the four sources (pin 5) along one bus to R15 / R16;
- `PGND`, from the shunt down the right of J2 and under its body to pins 6 / 7, with D4's anode;
- `V12C_RAW`, pin 5 under the body and up the left of J2 to D3, and through four vias to the clutch
  stage's tab on the bottom (Y11).

The INA180's two inputs are Kelvin lines from R15's own pads. `GND` is poured on both layers, stitched
top to bottom (about 100 vias), and the DRV8962's exposed pad carries 27 vias into it. The fine-pitch
power pins (DRV8962, BTT6050, BTT6200, LMR36015) are necked out at their pad width and widen to their
class past the toes; both buck switch nodes are short drawn tracks. The rest was routed with
freerouting 2.5.0 (Specctra DSN / SES, the project's clearances + 0.05 mm) and finished with a small
grid router; necks the router narrowed below 0.2 mm were widened to 0.2. No isolated copper is left.
Y11 kept that routing and added to it: what the new parts displaced or crossed was taken up and routed
again net by net with a raster A* router on both layers (0.2-0.25 mm tracks at the fine-pitch pins of
U13 and U15), the clutch stage's power paths and fan-outs drawn by hand and locked.

Y12 took up the header's seventeen signals between J4 and the Teensy's USB end (x < 48.2, y < 13), the
+5V and +3V3 runs to the header and the links to the six 0805s that moved, and laid them again; the rest
of Y5 / Y11's copper is as it was. Drawn by hand and locked: the four lines whose old runs leave south-west of the header (ENC_FAN_B,
ENC_TEMP_A, ENC_SEAT_PASS_A, I2C_SCL) go back along the top of the header on B.Cu, nested, round pins
2 / 1 and under the bottom row, so no column gap is spent on them; **+5V** drops between columns 1 and 2
(0.4 mm between the pads, 0.22 mm clear; it carries the Teensy and the panel's 0.5 A, `confirm`) instead
of wrapping the header; ROW1-3 / COL1-3 leave on F.Cu (COL2 / COL3 on B.Cu) and step down to their B.Cu
lanes through a staircase of vias beside the +5V diagonal; the header's own ground pins (2, 20, 21, 23),
ringed in by the fan-out on both layers, get a **GND rail** along the top edge between +5V and the signal
lanes, under the +5V neck on B.Cu. The eight lines east of column 4 were routed with freerouting 2.5.0
on a DSN in which every other net's copper is a keepout (it does not follow KiCad's T-junctions or
pours); its 0.15 mm necks were widened to 0.25. The GND pours were restitched (two vias) and refilled:
one fragment group, no isolated copper.

| Net class | Track | Clearance | Nets |
|---|---|---|---|
| `Default` | 0.25 | 0.2 | signals, `+3V3` (the Teensy's own output, light loads), `GND` (poured) |
| `COMFORT` | 4.0 or a pour | **0.5** | `V12C_RAW`, `SH_DRV_RTN`, `SH_PASS_RTN`, `SC_DRV_RTN`, `SC_PASS_RTN`, `CMF_RTN` - up to 18 A |
| `PGND` | 4.0 or a pour | **0.5** | `PGND` |
| `PWR_LOGIC` | 0.6 | 0.2 | `+12V_LOGIC`, `V12L_RAW`, `+5V`, `BUCK_SW` |
| `SERVO` | 1.0 | 0.2 | `+5V_SERVO`, `SRV_SW`, `+12V_CMF` |
| `DRIVE` | 0.8 | 0.2 | `MIR_COM`, `MIR_L`, `MIR_R`, `MIR_CLUTCH`, `MIRROR_HEAT` |
| `WIN` | 0.5 | 0.2 | `WIN_DRV_UP/DN`, `WIN_PASS_UP/DN`, `REL_HATCH`, `REL_FUEL`, `WAKE_OUT` |
| `CLUTCH` | 1.5 | 0.2 | `AC_CLUTCH` (Y11, ~4 A `confirm`) |

Two rules relax a clearance, with their reasons in `cu-carrier.kicad_dru`: pad-to-pad inside U4-U8
only, because the TO-252-5 legs (1.14 mm pitch) and the SOT-23-5 pins (0.95 mm) cannot hold 0.5 mm
between their own comfort and logic pins (their tracks and pours still keep 0.5 mm); and pad-to-pad
inside U15 only (Y11), whose 0.5 mm-pitch VSSOP-10 lands leave 0.15 mm between its own pins.

## The footprints

| Ref | Footprint | Source |
|---|---|---|
| J1 / J2 / J9 | `cu-carrier:DT13-06PA` / `DT13-08PA` / `DT13-12PA` | TE application spec 114-151046 Rev A p.5-6: pins Ø1.88 on 4.45 mm in two rows 6.35 apart (pads 2.9), three Ø3.43 flange posts (two at the sides, level with the far row, at ±10.87 / ±13.59 / ±17.55 for 6 / 8 / 12 ways, one on the centre line 11.43 toward the flange); the same pattern as the ICU's two, turned 180°. The 3D models sit as on the ICU's (TE's model frame turned onto the footprint, not checked against a part) |
| J3, J5 | `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical` | KiCad |
| J4 | `Connector_IDC:IDC-Header_2x13_P2.54mm_Vertical` | KiCad; keyed, shrouded - the part bought `confirm` (Y12) |
| F1 | `Fuse:Fuse_1206_3216Metric` | KiCad; 1206L050-class PTC `confirm` (Y12) |
| TP1 | `TestPoint:TestPoint_Pad_D1.0mm` | KiCad; a bare 1.0 mm pad on the bottom side (Y12) |
| J6-J8 | `PinHeader_1x03_P2.54mm_Vertical`, pin 1 signal, 2 V+, 3 GND | KiCad; the FS5115M lead order `confirm` |
| J10 | `cu-carrier:Teensy41_Socket` | the ICU's, its outline now the ICU's corrected one (body -1.27 to 59.69 mm along the rows) |
| L2 | `Inductor_SMD:L_Coilcraft_XAL7030-682` | KiCad; 6.8 µH, Isat ≥ 7 A `confirm` |
| U1 | `Package_DFN_QFN:Texas_RNX0012C_VQFN-14-11-1EP_2x3mm_P0.5mm_EP0.25x1.825mm` | KiCad (as the ICU) |
| U2 | `Package_SO:HSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm` | KiCad (TI DDA), 6 vias in the pad |
| U9 | `cu-carrier:Infineon_PG-TSDSO-14-22` | KiCad's geometry, exposed pad numbered TAB and drawn 6.4 x 2.65 (BTT6050-1ERA Fig. 53; KiCad's is 4.0) `confirm` |
| U10 | `cu-carrier:Infineon_PG-TSDSO-24-21` | drawn from BTT6200-4ESA Fig. 30: 24 leads at 0.65, pads 1.31 x 0.40 at ±2.85, body 8.65 x 3.9, exposed pad 6.4 x 2.77 = TAB `confirm` |
| U11 | `Package_SO:HTSSOP-44-1EP_6.1x14mm_P0.635mm_EP5.2x14mm_Mask4.31x8.26mm` | KiCad; the 27 thermal vias are placed on the board rather than taken from the `_ThermalVias` variant |
| U13 | `Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm` | KiCad, as U12 (Y11) |
| U14 | `cu-carrier:Infineon_PG-TSDSO-14-22` | U9's, on the bottom side (Y11) |
| U15 | `Package_SO:MSOP-10_3x3mm_P0.5mm` | KiCad; TI's DGS (VSSOP-10, SBAS563E) is the same 3 x 3 mm 0.5 mm-pitch body - `confirm` (Y11) |
| U16 | `Package_TO_SOT_SMD:SOT-23-5` | KiCad; TI's DBV (SLVSCA0C) (Y11) |
| J11 / J12 | `Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical` / `..._B2B-XH-A_1x02_...` | KiCad; PLACEHOLDER leads (Y11) |

## 3D models: `RX7_MODELS`

The vendor models (the TE DT13s, the XenGi Teensy 4.1, Infineon's PG-TSDSO packages) are not ours to
publish, so they are not in this folder: the footprints point at `${RX7_MODELS}/<cad row>/<file>`,
and `RX7_MODELS` is the local CAD library `02-PROJECTS/02-cad/model/library/electrical` (gitignored,
catalogued in the `00-CAR` `cad` table). Set it once — KiCad: **Preferences → Configure Paths →
+**, name `RX7_MODELS`; terminal: `export RX7_MODELS=$HOME/dev/Rx7/02-PROJECTS/02-cad/model/library/electrical`
(Mac) or the Fedora path. Without it those parts show bare pads. Three still do:

- **J2**: TE's DT13-08PA model is still zipped in its library folder
  (`deutsch-dt13-08pa-te/dt13-08pa_te-cvm-3d_stp.zip`); the footprint names the file inside it,
  `c-dt13-08pa-99-3d.stp`, and picks it up once it is extracted there. Its placement copies the 12-way's,
  `confirm`.
- **U1** and **U11**: TI publishes no free model (RNX0012C, DDW0044) and KiCad 10 ships none; they are
  left named.

```
kicad-cli pcb render --side top -o cu-carrier-top.png cu-carrier.kicad_pcb
kicad-cli pcb render --side bottom -o cu-carrier-bottom.png cu-carrier.kicad_pcb
kicad-cli pcb export step --subst-models -o cu-carrier.step cu-carrier.kicad_pcb
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o cu-carrier-drc.rpt cu-carrier.kicad_pcb
```

The renders and the STEP (about 25 MB) are built, never committed (`.gitignore`).

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
| A/C clutch coil current and its diode; the transducer's range and output; the radar receiver's alert output | engine 02.15 (b), luxury 03.12 / Z-002 | U14 (or a lower-RON PROFET), F29; R64-R67; R68 fitted or not |
| Stall current of a mirror motor | luxury `W-332` | R37 / R55-R57, `DRIVE` |

**Every other `confirm` on the board**: the XAL7030's saturation current; STATUS's wired-OR and its
clearing; OCPM latch-off and its reset by nSLEEP; the comfort currents (`V-101`) the 0.5 mm / pour
sizing assumes (18 A through the shunt on 1 oz F.Cu); the I²C addresses 0x74 / 0x75 (U12 / U13), 0x3C (the panel's IS31FL3236A, D-458) and
0x48 (U15); the PLACEHOLDER leads J11 / J12 and how their wires reach the DCU; the bottom-side parts
(U14, R59-R63, TP1) against the enclosure; H1 at (4, 15) and the one +3V3 via 3.4 mm from its centre
(inside the 7 mm courtyard, outside a 6 mm screw head); whether a USB plug reaches the Teensy with the
ribbon plugged in (the header's shroud ends 6.7 mm from the Teensy's edge, as on rev 0.03); the sheet's own
"what this sheet does not know" box.

## What it may and may not claim

The same as `../../../display-unit/cad/du-carrier/README.md`, and for the same reasons.

**May:** how the parts on the carrier connect to each other and where they sit on a guessed outline.

**May not:** anything about the car, the harness or the drops. `DP-DCU 1` and `DP-DCU-B 10` appear here
only as pins on the board edge; what is on the other side belongs to `cavities.csv`. **If this project
and the record disagree, the record is right.**

## Checking it

```
kicad-cli sch erc cu-carrier.kicad_sch --severity-all -o cu-carrier-erc.rpt
kicad-cli sch export svg --no-background-color -o . cu-carrier.kicad_sch
kicad-cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},${DNP}' --labels 'Ref,Value,Footprint,Qty,DNP' --group-by 'Value,Footprint,${DNP}' -o cu-carrier-bom.csv cu-carrier.kicad_sch
python3 00-design/tools/check.py --board cu-carrier
```

## Files

| File | What |
|---|---|
| `cu-carrier.kicad_pro` · `.kicad_sch` | the project (net classes included) and the schematic |
| `cu-carrier.kicad_pcb` · `.kicad_dru` | the provisional board and its two relaxed rules |
| `cu-carrier.kicad_sym` · `sym-lib-table` | every symbol used, kept with the project |
| `cu-carrier.pretty` · `fp-lib-table` | the footprints drawn here: the three DT13s, the two PG-TSDSO packages, the Teensy socket |
| `control-unit/diagrams/cu-carrier.svg` · `control-unit/data/cu-carrier-bom.csv` | the committed picture and the BOM export (grouped by DNP too, so a fitted and a DNP part never share a line): the reviewable forms of a change |
| `CONVENTIONS.md` | how to draw it, and what differs from the ICU |
| `TARGET.md` | the drawing checklist from `dcu_channels`, a snapshot and not a link |
| `enclosure/` | the enclosure (`P152`, Y7): `tools/enclosure.py --pass cu-carrier` (parameters at the top, `V-102` the envelope; `freecadcmd tools/enclosure.py --pass cu-carrier`) builds base, DT13 plate and lid as STEP / STL from `board.json` (`00-design/tools/enclosure_extract.py cu-carrier`) and the board STEP, and fit-checks them; provisional, `confirm` until `V-102` / F11 |

`control-unit/data/cu-carrier-board.json` is extracted from the rev 0.04 board (Y12; rerun `00-design/tools/enclosure_extract.py cu-carrier`
whenever the board moves): `RIBBON_WAYS` is 26, the ribbon notch runs from x 4.1 to 39.1 mm, the H1 boss
stands at (4, 15), and base, plate and lid fit with 0 interferences. J11 on the right edge still needs its
side-wall hole; U14, R59-R63 and TP1 sit on the underside.

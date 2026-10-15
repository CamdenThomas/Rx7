# ICU carrier — the KiCad project

*Rev 2026-10-14 (sheet and board rev 0.07 - Y63, the one DRC connector, D-587 / D-590; rev 0.06 was Y44's fix pass, D-549; 0.05 Y44's one value, 0.04 Y42, 0.03 2026-10-09) · owns: what this KiCad project is for, what it
may claim, and how to start. The board's design is `../../../../data/icu_channels.csv` — that is the
record; this is a drawing of it. Read `../../../README.md` first: it is the fence.*

## Where it stands

**2026-10-14 (Y63, D-587 / D-590): rev 0.07 - one Deutsch DRC13-24PA in place of the two DT13s.**
`fab/` is bench revision A re-issued from this board: no earlier zip may be ordered.
ERC 0 / 0; DRC 0 violations, 0 unconnected, 0 parity; `check.py --board du-carrier` 105 checks, 0 mismatches.

- **J1 is the DRC13-24PA** (24 size-16 pins, key A), mated by a DRC16-24SA plug; J3 is gone. Pin n is DP-ICU
  cavity n, mapped so the tach keeps its 2.5 mm (D-592): 1 logic +12 V, 2 illumination, 3 the backlight's
  +12 V (over D25), 4 / 5 CAN2, **6 the tach, straight over R29 with no live pin in its column**, 7-11 and 14-17
  the senders and tell-tales, 21 ground, 22 the high-beam tell-tale; 12, 13, 18-20, 23, 24 sealing plugs in the
  plug. The sheet draws it as one part in three units where J1 and J3 stood, so no wire moved; unit 3 carries
  no-connect flags. Footprint `du-carrier.pretty/DRC13-24PA` from TE's drawing DRC13-24P* rev D (pins
  5.49 x 3.81 mm in two groups of three columns, pegs dia 2.54 at +-17.58 mm); TE's own model
  (`${RX7_MODELS}/deutsch-drc13-24pa-te`, 00-CAR cad) lands its 24 tails and two pegs on it exactly.
- **The board grew 4 mm at the connector edge: 110 x 84 mm** (D-591). The DRC reaches about 2 mm further back
  than the DT13s did, into the row of protection parts behind them; moving the edge out moved nothing else. The
  connector is centred on that edge (x 155); the GND pours follow the edge.
- **Re-routed with freerouting under this project's rules** (the connector's nets and every track the new part
  landed on; the pours kept in the DSN, the router's micron gaps snapped after import). The tach's 7 mm run
  from pin 6 to R29 is drawn by hand, pad edge to pad edge: R29's own pads sit inside the tach's 2.5 mm, which
  this rule file excuses and the router cannot know. U4A- and BL_EN keep their rev 0.06 routes; the three
  nets those crossed were re-routed round them. The backlight feed's two layer changes are four vias on a
  0.9 mm square each, as D-549 made them. Some GND pour pieces the new tracks fenced off are stitched back.
- **Trap, for the next script:** a board saved by KiCad's Python without its `.kicad_pro` beside it gets a
  default project - net classes, TACH_HV's 2.5 mm and the 0.3 mm edge rule gone - and saving it into this
  folder writes that over `du-carrier.kicad_pro`. Work on a copy of the whole project folder.
- **What it means at the bench:** the connector stands 52.6 mm above the board (the DT13s 37.7). Its four
  #10-32 screws go through the rear wall into the flange's threaded inserts; the wall's cut-out is TE's,
  56.13 x 32.13 mm with four dia 5.61 holes (sheet 2). The DU mock-up (`../du-assembly`) carries it; the bench
  enclosure under `enclosure/` reads the same files but is not the part being built.

**2026-10-13 (Y44, D-549): rev 0.06 - what the independent read found (D-548), fixed before the boards are ordered.**
`fab/` is bench revision A re-issued again from this board under the same names: no earlier zip may be ordered.
ERC 0 / 0; DRC 0 violations, 0 unconnected, 0 parity; `check.py --board du-carrier` 99 checks, 0 mismatches.

- **Road speed, IC08.** Cavity 8 went straight to U5 and D22, R36 sat in a loop on that one net and R37 was
  always in circuit. Now `ICU_B8` - R36 (10 k) - the node `IC08_IN` with D22, U5 and R37 on it; R35 / J8A pull the
  cavity side to +3V3 (open-collector sensor); J8B is in R37's ground leg and makes the 10 k / 4.7 k divider (12 V
  push-pull: 3.84 V, the BAT54S takes 0.07 mA). **One jumper, never both; a 5 V push-pull sensor takes neither.**
- **Q1's gate.** D27, a 15 V zener (onsemi MM3Z15VT1G, SOD-323), gate to source with its cathode on the source,
  on the back under R1 / R2; R2 is 4.7 k. The gate has 6.1 V at 9 V on the rail, 8.2 at 12, 9.8 at 14.4, and is
  held at 15 V (15.8 at most) from 22 V to the SMBJ33A's 53.3 V clamp, where the zener carries 6.6 mA (0.1 W of
  0.3 W). The two nets are named on the sheet, `BL_FUSED` (F1 to the source; the project's PWR_BL net class
  names it) and `BL_GATE`, so the diode does not rename them.
- **The backlight path** (J1.6 - D25 - F1 - Q1 - J2, 2.5 A behind a 4 A fuse) changed layer through one
  0.6 / 0.3 mm via at each of four places; each is now four, on a 0.9 mm square inside the 2.2 mm track.
- **Brake warning, IC06 - found while these changes were read back.** The switches pull cavity 6 to ground and
  low means warn, but the stage was a divider to ground and nothing pulled the line up: it read low always.
  R17 (10 k) now goes from the node to +3V3 and R16 is 1 k: 3.3 V with both switches open, 0.30 V with either
  closed (the i.MX RT1062 reads low under 0.99 V); a short to 14.4 V puts 10.8 mA through D5. R17 moved to
  (135.96, 87.35) on the back, pad 1 on the node's track and pad 2 on the +3V3 via there: a via beside its old
  place would stand 1.85 mm from the tach's series resistors, whose net class keeps 2.5 mm.
- **The three tell-tale dividers** R21, R23, R25 (IC09-IC11) are 22 k over 10 k, were 47 k: 2.81 V at 9 V on
  the lamp against the 2.31 V the processor guarantees as high (NXP IMXRT1060CEC rev 4: 0.7 x NVCC); at 16 V
  the BAT54S takes 0.2 mA. R14 and R27, the analogue dividers, stay 47 k.
- **On the rails the TVS clamps at 53 V** (D-273): Q2 is MMBT5551 (160 V, the same SOT-23 pins as the MMBT3904
  it was; Q4, on +5V, stays MMBT3904); D23 and D25 are SL310A (MCC, 100 V 3 A, SMA, 0.60 V at 3 A - about 0.25 W
  more in D25 at 2.5 A than the 40 V part).
- **Not changed, to know at the bench:** the screw at H1 sits over `ICU_B1` and `ICU_B3` (tracks 2.15 and 2.69 mm
  from the hole's centre, and 1.8 mm from the board's edge on the other side, so they do not move): **a nylon
  washer under that screw's head**. A USB plug in the Teensy stands over C1 (the can is 10.2 mm tall): use a
  lead with a slim plug, or the Teensy's own pins raise it enough - confirm at F3. The DT13 pad numbering is as
  it was and waits on the part in hand (D-548, V-117).

`fab/` also holds two hand-assembly drawings, `du-carrier-revA-assembly-top.svg` and `-bottom.svg` (the back mirrored, to read
as you look at it): the outline, every part's outline and pads, and its reference in the middle of the part; the
values are in `display-unit/data/du-carrier-revA-bom.csv` by reference. `00-design/tools/assembly.py` rebuilds them (KiCad's Python);
`00-design/tools/fabpack.py` re-plots the gerbers and drill files and writes the zip.

**2026-10-13 (Y42): rev 0.04 - what pricing the order found, made right before the boards are ordered (D-541).**
`fab/` is bench revision A re-issued from this board: the zip keeps its name, and the rev 0.03 package must not be
ordered. ERC 0 / 0; DRC 0 violations, 0 unconnected, 0 parity; `check.py --board du-carrier` 98 checks, 0 mismatches.
Y44 changed one value after it and no fab file: re-plotted and compared, every file the same but its date.

- **D24 and D26 (SMBJ33A) are one-way parts and were drawn with two anodes**, pad 1 - the end the silkscreen
  marks as the cathode - on ground: fitted to the mark they short both 12 V inputs. The symbol is `D_TVS_Uni`
  (pin 1 the cathode) and each footprint is turned half a turn in place: the same copper, the mark at the rail end.
- **D20, the tach node's 5.1 V zener, was a two-pin symbol on a SOT-23**: its anode pad on ground, the node on the
  package's unused pin 2, and the cathode, pin 3, on nothing (onsemi BZX84C2V4LT1/D: 1 anode, 2 no connection,
  3 cathode). The symbol is `D_Zener_SOT23`; pad 3 is joined to the node by one 2 mm track beside pad 2. D21
  clamps the node first either way, so nothing the bench saw changes.
- **C1 is 68 µF 63 V** (Panasonic EEE-FK1J680UP), not 100 µF: it sits across D24, whose clamp is 53.3 V, so D-273's
  rule asks more than a 50 V part; 100 µF 63 V is a 10 × 10.2 can and the footprint is the 8 × 10.2 one, whose
  largest 63 V value is 68 µF. C1's courtyard is 0.2 mm from the board's edge with C3, C4 and R5 0.2 to 0.6 mm
  from it: the 10 mm can (2.7 mm longer, 1.9 wider) needs the buck's corner laid again, which is F11's.
- **Q1's gate divider (Y44, sheet rev 0.05, a value only): R2 is 10 k, was 1 k** (R1, gate to source, stays
  10 k). The gate now sees half the backlight rail: 4.5 V at 9 V, 6.0 at 12, 7.2 at 14.4, 12.0 at 24 - inside the
  part's ±20 V up to 40 V on the rail, where 1 k passed it at 22 V. **It is not the whole answer**: at the
  SMBJ33A's 53.3 V clamp it is 26.7 V. No pair of values does both ends: Q1 carries the backlight's 2.5 A (about
  3.3 A at 9 V), Vishay 69098 gives its on-resistance no lower than 4.5 V on the gate (20 mΩ), and 4.5 V at 9 V is
  half the rail, where 20 V at 53.3 V is three eighths. The rest is a 12 V zener from gate to source, cathode to
  the source: on R1's own pads at (179.0, 79.3) a SOD-323 part fits beside or on the resistor, and through R2's
  10 k it carries 4 mA at the clamp. That part is drawn since rev 0.06 (above): D27, 15 V, with R2 at 4.7 k.
- Q3's part, DMG3415U, is marked not for new designs by its maker, who names DMP2045U (the same pins); the cart
  carries both.

This board has no generator: the change was made by two scripts on the sheet and the board themselves - nodes
replaced in the `.kicad_sch` / `.kicad_sym`, the board through KiCad's `pcbnew`.

**2026-10-12 (Y17): bench revision A is packaged under `fab/`** - gerbers, Excellon drill (PTH / NPTH, maps),
`du-carrier-revA-gerbers.zip` and `du-carrier-revA-bom.csv` (MPNs `confirm` where the sheet does not name them),
from this board on its provisional outline, for the bench order of D-490; the final board follows F11.

**The board is laid out, routed and 3D-modelled on a PROVISIONAL outline: guide step 8 is done
(F9, F10); step 9, the measurement pass, is F11.** `kicad-cli pcb drc --severity-all
--exit-code-violations --schematic-parity` reads 0 violations, 0 unconnected, 0 parity issues;
ERC is 0 / 0; `00-design/tools/check.py --board du-carrier` is 0 mismatches. Nothing here is ordered (F12).

- **The sheet** (rev 0.03): U8, the XIAO ESP32C3, has Seeed's real castellation pins 1-14 and sits
  in a 2 x 7 socket. EN 34 cannot reach the module's CHIP_EN (a back pad, TP6), so it power-cycles
  the module instead: Q4 (MMBT3904, R47 10 k from EN to its base) pulls down the gate of Q3, a
  SOT-23 P-FET (DMG3415U class, `confirm`) that R46 (10 k to `+5V`) holds off while the Teensy is
  in reset; Q3 switches `+5V` onto the module's VBUS (`RADIO_5V`), with C19 10 µ at the pin. BOOT 35 lands on D9 / GPIO9. J4 is the
  ME817EV's CN8 2 x 8 host header, U7 the Adafruit 4517 on its 1 x 6 + 1 x 5 headers. U2, the VN5E
  alternative, is DNP and off the board (no footprint until it is picked). The back pads 15-22 of
  the XIAO are not drawn: no socket reaches them (`00-design/tools/pin_tables.csv`, "XIAO ESP32C3 2x7 socket").
- **The outline is a working guess**, 110 x 80 mm, because the two DT13 housings side by side need
  107 mm of edge: the connector face is the top long edge (J3 DT13-12PA left, J1 DT13-06PA right,
  flange rear faces on the edge, housings overhanging it as TE's panel mount intends); the grommet
  face is the bottom edge (J4 BT817 CN8, SW1 page button, J2 backlight out); the radio edge is the
  left short edge, where the XIAO's u.FL end overhangs by about 1.5 mm with a no-pour, no-via
  keep-out 4 mm in from it. Four M3 holes: the bottom two 4 mm from the corners, the top two 29.8
  mm down because the DT13 housings cover the top corners. **C4 (the space behind the binnacle)
  sets the real outline at F11, and the board will shrink or grow** (D-455).
- **Placement** follows `TARGET.md`'s blocks: power entry at J1 (SL310A + SMBJ33A on each 12 V pin,
  the 4 A fuse and Q1 on the backlight path, the two inputs never sharing copper); the 5 V buck at
  the right edge in a HotRod layout (an input cap across each VIN / PGND pair, L2 straight up from
  the centre SW pad, the feedback parts under FB); CAN (U3, the R44 / R45 links, L1 DNP) under J1;
  the nine sensor front ends on the back, one column under each DT13 pin, ADC node down the left of
  each column and ground down the right; the tach stage (R29, R30 in a column under J3 pin 4,
  2.5 mm from everything) and the LM393 and road-speed stage between J3 and the Teensy, with the
  J8A / J8B jumpers beside it; the Teensy socket in the middle, USB end toward the buck; the IMU
  bottom left, away from the buck and the connectors.
- **Routing**: freerouting 2.5.0 (Specctra DSN / SES round trip) for the bulk, the buck's 0.5 mm
  pitch VQFN, the tach's high-voltage column and a handful of leftovers by script. Power is sized
  to its fuse: `PWR_BL` 2.2 mm (including the fuse-to-Q1 source path), `PWR_LOGIC` 0.6 mm except
  0.25 mm necks at U1's pins. Ground is a pour on both layers (B.Cu the plane, F.Cu filling between
  parts) with stitching vias on a 5 mm grid; SMD pads solid, through-hole pads on spokes.
- **Two board rules relax a clearance, each with its reason in `du-carrier.kicad_dru`**: the DT13's
  own 4.45 mm pin pitch on the tach net, and the pad-to-pad gap inside each of R29 and R30 (the
  part's own rating); a third lets J5's GND pins take one thermal spoke on top where the socket row
  leaves a 2 mm strip of pour.

**R11, in full:** none of this has been measured. The DT13 hole pattern is TE's drawing, the Teensy
socket is PJRC's dimensions, the XIAO and IMU positions are the vendors' files: every one carries
`confirm` until F11 puts calipers on the part in hand.

## 3D models: `RX7_MODELS`

The vendor models (the TE DT13s, the XenGi Teensy 4.1, the Seeed XIAO, the Adafruit 4517) are not
ours to publish, so they are not in this folder: the footprints point at
`${RX7_MODELS}/<cad row>/<file>`, and `RX7_MODELS` is the local CAD library,
`02-PROJECTS/02-cad/model/library/electrical` (gitignored, catalogued in the `00-CAR` `cad` table).
Set it once — KiCad: **Preferences → Configure Paths → +**, name `RX7_MODELS`; terminal:
`export RX7_MODELS=$HOME/dev/Rx7/02-PROJECTS/02-cad/model/library/electrical` (Mac) or the Fedora path —
and the renders and the STEP pick them up. Without it those parts show bare pads. U1's model
(`Texas_RNX0012C...step`) does not ship with KiCad 10: it is left named and shows as bare pads.

```
kicad-cli pcb render --side top -o du-carrier-top.png du-carrier.kicad_pcb
kicad-cli pcb render --side bottom -o du-carrier-bottom.png du-carrier.kicad_pcb
kicad-cli pcb export step --subst-models -o du-carrier.step du-carrier.kicad_pcb
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o du-carrier-drc.rpt du-carrier.kicad_pcb
```

The renders and the STEP (about 23 MB) are built, never committed (`.gitignore`).

## What F11 measures

| Measure | On | Fixes |
|---|---|---|
| Length, width, depth behind the binnacle | the car (C4) | the outline and the hole positions |
| Pin pitch (4.45 / 6.35), hole Ø, the three flange holes, flange-to-pin-field 18.675 mm, cavity 1's corner | the DT13-06PA and DT13-12PA in hand (P122) | `DT13-06PA` / `DT13-12PA`; TE's 12-way model shows no peg in the single flange hole: confirm the hole is there |
| Row spacing, socket height, underside clearance | a Teensy 4.1 on its headers | `Teensy41_Socket` |
| Header pitch, keying, CN8's position on the eval board | the ME817EV (P117) | J4 |
| Outline, castellation row spacing, u.FL position | the XIAO in hand | `XIAO_ESP32C3_Socket_2x07`, the RF edge |
| Header rows, outline | the IMU breakout bought (P109) | `IMU_Adafruit_4517_Socket` |
| Package on the reel | Q3 (DMG3415U class), U5, the fuse, C1 | footprints |
| The 2.5 A backlight through J2 (0.1 in header, 3 A pins) | the panel's backlight driver | J2 |

## Why it exists

1. **To learn KiCad on something real.** A tutorial board teaches the keystrokes and
   nothing else. This one is already specified down to the resistor values, so the design
   work is done and the only thing left to learn is the tool. Whatever comes next that
   needs a PCB, the practice is already paid for.
2. **Because the analog front end cannot be reviewed as prose.** See `../../../README.md`.

## What it may and may not claim

**May:** how the parts on the carrier connect to each other — divider ratios, clamp
placement, the pull-up jumpers, the comparator's hysteresis network, decoupling, what
shares a rail, and what the ERC thinks of all of it.

**May not:** anything about the car, the harness, or the drops. `DP-ICU-A 1` and
`DP-ICU-B 4` appear here only as pins on the board edge; what is on the other side of them
belongs to `cavities.csv`. **If this schematic and the record disagree, the record is
right.**

**Two things this revision deliberately does not assert, and says so on the sheet:**

- **The Teensy pinout — asserted since 2026-09-22.** D-377 put every channel's Teensy pin in
  `icu_channels.teensy_pin`, so `J5` now carries the real Teensy 4.1 pad numbers (pad n = edge
  pin n, pad 1 = GND at the USB end) and the six power pins it had been missing — VIN on `+5V`,
  3V3 ×2 on `+3V3`, GND ×3 — along its bottom edge. Its footprint is
  `du-carrier.pretty/Teensy41_Socket` (`confirm - not measured`). The SPI nets are named
  `SPI_*` now, not `QSPI_*` (D-377).
- **Module pin numbers — asserted since 2026-10-09 (F9).** The transceiver, the buck, the XIAO
  (castellations 1-14 in its socket), the IMU breakout's headers and the ME817EV's CN8 carry the
  vendors' numbers, held to `00-design/tools/pin_tables.csv` by `00-design/tools/check.py`. What is still a guess is the
  geometry of the sockets and connectors, not the numbering: that is F11.

**And R11 applies with full force:** none of this has been measured. A schematic that
passes ERC is internally consistent, not correct. The panel timings, the tach comparator's
real noise margin, and every sender curve are still unmeasured — drawing them neatly does
not close them. The sheet carries its own "what this sheet does not know" panel, and
`TARGET.md §6` is the same list.

## Scope: schematic yes, PCB not yet — superseded 2026-09-21

> **Layout is now in scope** (D-361): Camden asked for the full layout and 3D guide, and ICU
> layout was already his step `F2`. The step-by-step guide that walked it is gone (Camden deleted it on 2026-10-13 once the boards were drawn). The paragraph below
> is kept for why it used to say no. Its last point still stands: **fabricating** (ordering
> boards) is money with a lead time, and it stays Camden's.

Capture the schematic. Do not lay out a board until there is a reason to, and "I have a
schematic" is not one. The carrier can be protoboard for bring-up, and fabricating one is
a decision with a lead time, a cost and a revision cycle attached — which makes it **big**
by §3, so it is a block before any time goes into `.kicad_pcb`, not an assumption because
the file exists. (There was no `.kicad_pcb` here then; D-453 and F9 put one here, and ordering is
still F12.)

## Opening it

KiCad 10.0.6 on each machine (D-454; on the Mac `kicad-cli` is in
`/Applications/KiCad/KiCad.app/Contents/MacOS/`). Open `du-carrier.kicad_pro`: the sheet is A0
with five blocked-out areas, the board is `du-carrier.kicad_pcb`. Set `RX7_MODELS` first (above)
or the vendor parts show bare pads in the 3D viewer. ERC, DRC and `check.py` were re-run on the
Mac on 2026-10-09: all zero.

**Every symbol it uses is in `du-carrier.kicad_sym`, beside the project**, with a
`sym-lib-table` pointing at it. Nothing depends on which KiCad libraries happen to be
installed, so the sheet opens identically after a reinstall or a KiCad upgrade, and ERC has no
missing-library complaints to make.

## Checking it

```
kicad-cli sch erc du-carrier.kicad_sch --severity-all -o du-carrier-erc.rpt
kicad-cli sch export svg --no-background-color -o . du-carrier.kicad_sch
kicad-cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},${DNP}' --labels 'Refs,Value,Footprint,Qty,DNP' --group-by 'Value,Footprint,${DNP}' --ref-range-delimiter '' -o du-carrier-bom.csv du-carrier.kicad_sch
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o du-carrier-drc.rpt du-carrier.kicad_pcb
python3 00-design/tools/check.py --board du-carrier
```

ERC violations are errors, not suggestions — the same standing as a `check` refusal. The
report is gitignored; the **SVG is committed**, because an S-expression diff of coordinate
tuples cannot be reviewed by anyone, including you in three weeks. A PDF
(`kicad-cli sch export pdf`) is easier to read at a desk and is gitignored for the same
reason a second copy of any fact is: one picture in the repo, not two.

## Files

| File | What |
|---|---|
| `du-carrier.kicad_pro` · `.kicad_sch` | the project and the schematic |
| `du-carrier.kicad_sym` · `sym-lib-table` | every symbol used, kept with the project |
| `display-unit/diagrams/du-carrier.svg` | the committed picture — the reviewable form of a change |
| `du-carrier.kicad_pcb` | the board: provisional outline, placed, routed, both pours filled |
| `du-carrier.kicad_dru` | the three relaxed board rules, each with its reason |
| `du-carrier.pretty/` · `fp-lib-table` | the footprints drawn here: DT13-06PA, DT13-12PA (TE 114-151046), the Teensy, XIAO and IMU sockets; their vendor models through `${RX7_MODELS}` |
| `display-unit/data/du-carrier-bom.csv` | the bill of materials, grouped — the reviewable form of a part change |
| `report.txt` | a stale log of the first Update-PCB run on the placeholder footprints (2026-09); nothing reads it |
| `CONVENTIONS.md` | how to draw it so it stays reviewable |
| `TARGET.md` | what has to be on the sheet, from `icu_channels.csv` — a snapshot, not a link |
| `enclosure/` | the enclosure (P111, Y7): `tools/enclosure.py --pass du-carrier` (parameters at the top, C4 the envelope; `freecadcmd tools/enclosure.py --pass du-carrier`) builds base, DT13 plate and lid as STEP / STL from `board.json` (`00-design/tools/enclosure_extract.py du-carrier`, KiCad's Python) and the board STEP, and fit-checks them; provisional, every dimension `confirm` until C4 / F11 |

`.kicad_prl`, `*-backups/`, `*.kicad_sch-bak`, autosaves, the ERC and DRC reports, the netlist,
the PDF, the renders, the STEP and the router's DSN / SES files are gitignored (the root
`.gitignore` and this folder's).

## What to draw next

Nothing, until something in the record changes or a bench result arrives. The open ends
are all measurements, not drawings:

- `Q-308` picks an oil-temperature sender and IC07's pull-up stops being a question mark.
- `V-084` settles the BT817's pixel clock and sync polarity against the real panel.
- `D-261`'s three-point sender reads make IC01 and IC03 curves rather than dividers.
- The tach front end is a bench result: LM393 or H11L1, and the hysteresis values on this
  sheet are a proposal derived here, not a fact from the record.
- `F11` measures the space and the parts in hand, and the outline, the sockets and the DT13
  footprints move to the numbers; then DRC to zero again and a new STEP for the enclosure (F1).

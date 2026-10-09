# ICU carrier — the KiCad project

*Rev 2026-10-09 (sheet rev 0.03, board rev 0.03) · owns: what this KiCad project is for, what it
may claim, and how to start. The board's design is `../../../data/icu_channels.csv` — that is the
record; this is a drawing of it. Read `../README.md` first: it is the fence.*

## Where it stands

**The board is laid out, routed and 3D-modelled on a PROVISIONAL outline: guide step 8 is done
(F9, F10); step 9, the measurement pass, is F11.** `kicad-cli pcb drc --severity-all
--exit-code-violations --schematic-parity` reads 0 violations, 0 unconnected, 0 parity issues;
ERC is 0 / 0; `../check.py --board icu` is 0 mismatches. Nothing here is ordered (F12).

- **The sheet** (rev 0.03): U8, the XIAO ESP32C3, has Seeed's real castellation pins 1-14 and sits
  in a 2 x 7 socket. EN 34 cannot reach the module's CHIP_EN (a back pad, TP6), so it power-cycles
  the module instead: Q4 (MMBT3904, R47 10 k from EN to its base) pulls down the gate of Q3, a
  SOT-23 P-FET (DMG3415U class, `confirm`) that R46 (10 k to `+5V`) holds off while the Teensy is
  in reset; Q3 switches `+5V` onto the module's VBUS (`RADIO_5V`), with C19 10 µ at the pin. BOOT 35 lands on D9 / GPIO9. J4 is the
  ME817EV's CN8 2 x 8 host header, U7 the Adafruit 4517 on its 1 x 6 + 1 x 5 headers. U2, the VN5E
  alternative, is DNP and off the board (no footprint until it is picked). The back pads 15-22 of
  the XIAO are not drawn: no socket reaches them (`../pin_tables.csv`, "XIAO ESP32C3 2x7 socket").
- **The outline is a working guess**, 110 x 80 mm, because the two DT13 housings side by side need
  107 mm of edge: the connector face is the top long edge (J3 DT13-12PA left, J1 DT13-06PA right,
  flange rear faces on the edge, housings overhanging it as TE's panel mount intends); the grommet
  face is the bottom edge (J4 BT817 CN8, SW1 page button, J2 backlight out); the radio edge is the
  left short edge, where the XIAO's u.FL end overhangs by about 1.5 mm with a no-pour, no-via
  keep-out 4 mm in from it. Four M3 holes: the bottom two 4 mm from the corners, the top two 29.8
  mm down because the DT13 housings cover the top corners. **C4 (the space behind the binnacle)
  sets the real outline at F11, and the board will shrink or grow** (D-455).
- **Placement** follows `TARGET.md`'s blocks: power entry at J1 (SS34 + SMBJ33A on each 12 V pin,
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
- **Two board rules relax a clearance, each with its reason in `icu-carrier.kicad_dru`**: the DT13's
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
`01-REFERENCE/model/library/electrical` (gitignored, catalogued in the `01-REFERENCE` `cad` table).
Set it once — KiCad: **Preferences → Configure Paths → +**, name `RX7_MODELS`; terminal:
`export RX7_MODELS=$HOME/dev/Rx7/01-REFERENCE/model/library/electrical` (Mac) or the Fedora path —
and the renders and the STEP pick them up. Without it those parts show bare pads. U1's model
(`Texas_RNX0012C...step`) does not ship with KiCad 10: it is left named and shows as bare pads.

```
kicad-cli pcb render --side top -o icu-carrier-top.png icu-carrier.kicad_pcb
kicad-cli pcb render --side bottom -o icu-carrier-bottom.png icu-carrier.kicad_pcb
kicad-cli pcb export step --subst-models -o icu-carrier.step icu-carrier.kicad_pcb
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o icu-carrier-drc.rpt icu-carrier.kicad_pcb
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
2. **Because the analog front end cannot be reviewed as prose.** See `../README.md`.

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
  `icu-carrier.pretty/Teensy41_Socket` (`confirm - not measured`). The SPI nets are named
  `SPI_*` now, not `QSPI_*` (D-377).
- **Module pin numbers — asserted since 2026-10-09 (F9).** The transceiver, the buck, the XIAO
  (castellations 1-14 in its socket), the IMU breakout's headers and the ME817EV's CN8 carry the
  vendors' numbers, held to `../pin_tables.csv` by `../check.py`. What is still a guess is the
  geometry of the sockets and connectors, not the numbering: that is F11.

**And R11 applies with full force:** none of this has been measured. A schematic that
passes ERC is internally consistent, not correct. The panel timings, the tach comparator's
real noise margin, and every sender curve are still unmeasured — drawing them neatly does
not close them. The sheet carries its own "what this sheet does not know" panel, and
`TARGET.md §6` is the same list.

## Scope: schematic yes, PCB not yet — superseded 2026-09-21

> **Layout is now in scope** (D-361): Camden asked for the full layout and 3D guide, and ICU
> layout was already his step `F2`. Follow `../PCB-AND-3D-GUIDE.md` Part A. The paragraph below
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
`/Applications/KiCad/KiCad.app/Contents/MacOS/`). Open `icu-carrier.kicad_pro`: the sheet is A0
with five blocked-out areas, the board is `icu-carrier.kicad_pcb`. Set `RX7_MODELS` first (above)
or the vendor parts show bare pads in the 3D viewer. ERC, DRC and `check.py` were re-run on the
Mac on 2026-10-09: all zero.

**Every symbol it uses is in `icu-carrier.kicad_sym`, beside the project**, with a
`sym-lib-table` pointing at it. Nothing depends on which KiCad libraries happen to be
installed, so the sheet opens identically after a reinstall or a KiCad upgrade, and ERC has no
missing-library complaints to make.

## Checking it

```
kicad-cli sch erc icu-carrier.kicad_sch --severity-all -o icu-carrier-erc.rpt
kicad-cli sch export svg --no-background-color -o . icu-carrier.kicad_sch
kicad-cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},${DNP}' --labels 'Refs,Value,Footprint,Qty,DNP' --group-by 'Value,Footprint,${DNP}' --ref-range-delimiter '' -o icu-carrier-bom.csv icu-carrier.kicad_sch
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o icu-carrier-drc.rpt icu-carrier.kicad_pcb
python3 ../check.py --board icu
```

ERC violations are errors, not suggestions — the same standing as a `check` refusal. The
report is gitignored; the **SVG is committed**, because an S-expression diff of coordinate
tuples cannot be reviewed by anyone, including you in three weeks. A PDF
(`kicad-cli sch export pdf`) is easier to read at a desk and is gitignored for the same
reason a second copy of any fact is: one picture in the repo, not two.

## Files

| File | What |
|---|---|
| `icu-carrier.kicad_pro` · `.kicad_sch` | the project and the schematic |
| `icu-carrier.kicad_sym` · `sym-lib-table` | every symbol used, kept with the project |
| `icu-carrier.svg` | the committed picture — the reviewable form of a change |
| `icu-carrier.kicad_pcb` | the board: provisional outline, placed, routed, both pours filled |
| `icu-carrier.kicad_dru` | the three relaxed board rules, each with its reason |
| `icu-carrier.pretty/` · `fp-lib-table` | the footprints drawn here: DT13-06PA, DT13-12PA (TE 114-151046), the Teensy, XIAO and IMU sockets; their vendor models through `${RX7_MODELS}` |
| `icu-carrier-bom.csv` | the bill of materials, grouped — the reviewable form of a part change |
| `report.txt` | a stale log of the first Update-PCB run on the placeholder footprints (2026-09); nothing reads it |
| `CONVENTIONS.md` | how to draw it so it stays reviewable |
| `TARGET.md` | what has to be on the sheet, from `icu_channels.csv` — a snapshot, not a link |
| `enclosure/` | the enclosure (P111, Y7): `make_enclosure.py` (parameters at the top, C4 the envelope; `freecadcmd make_enclosure.py`) builds base, DT13 plate and lid as STEP / STL from `board.json` (`../enclosure_extract.py icu-carrier`, KiCad's Python) and the board STEP, and fit-checks them; provisional, every dimension `confirm` until C4 / F11 |

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

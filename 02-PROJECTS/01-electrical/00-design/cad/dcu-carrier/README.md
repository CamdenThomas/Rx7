# DCU carrier — the KiCad project

*Rev 2026-09-28 (sheet rev 0.01) · owns: what this KiCad project is for, what it may claim, and how
to start. The board's design is `../../../data/dcu_channels.csv`. That is the record, and this is a
drawing of it. Read `../README.md` first: it is the fence.*

## Where it stands

**The schematic is drawn, all five blocks, and ERC is clean: zero errors and zero warnings**
(2026-09-28, D-452). The five blocks are power, bus, inputs, outputs and processor. The sheet has
125 parts and 130 nets. It carries every channel in `dcu_channels` and every conductor in
`panel_ribbon`, and every cavity on DP-DCU, DP-DCU-B and DP-DCU-C lands on a pin at the board
edge.

What it settled on the way:

- **The pin budget (D-442's open item).** The map needs 44 I/O against the Teensy 4.1's 40 edge
  pins besides CAN2. A **TCA9539-Q1** I²C expander takes the slow lines: the mirror bridge,
  nSLEEP / nFAULT, the PROFETs' DEN / DSEL, CAN STB and the logic buck's power-good. The bottom
  pads stay unused. All 42 edge pins are used, and every one is in `dcu_channels.teensy_pin`.
- **Two supplies, two grounds.** Logic 12 V (DP-DCU 1) and the comfort feed (DP-DCU-C 5) share
  no part. `GND` and `PGND` meet only at the dash ground bus: the seat returns go through the
  shunt and out on DP-DCU-C 6/7, never through DP-DCU 3 (D-382).
- **The windows and mirrors run on logic 12 V**, so they work in ACC. That puts about 2.2 A worst
  case on F22's 3 A, `confirm`.

## What it may and may not claim

The same as `../icu-carrier/README.md`, and for the same reasons.

**May:** how the parts on the carrier connect to each other. That covers the protection on each
input, the two rails and where they never meet, the switch inputs and their pull-downs, the
half-bridges, the shunt, decoupling, and what the ERC thinks of all of it.

**May not:** anything about the car, the harness or the drops. `DP-DCU 1` and `DP-DCU-B 10`
appear here only as pins on the board edge; what is on the other side belongs to `cavities.csv`.
**If this schematic and the record disagree, the record is right.**

**The Teensy pads are real, and nothing else's pin numbers are.** The pads come from
`dcu_channels.teensy_pin`. Change a pin there first, then here. Every other module (the bucks
except the copied LMR36015, the PROFETs, the DRV8962, the expander, the INA180) is a functional
block: its pin *names* are real, and its pin *numbers* are fixed against the datasheet at layout
(`H-002`).

**R11 applies:** none of the DCU's parts, loads or spaces has been measured. The sheet's own
"what this sheet does not know" box lists what is `confirm`. The main items are the TPS54560B's
compensation, the DRV8962's support parts, and the mirror stage (luxury `W-332`). `V-102`
measures the space behind the centre stack, and the outline and the enclosure (`P152`) wait on it.

## Opening it

Open `dcu-carrier.kicad_pro` in KiCad 10. Every symbol is in `dcu-carrier.kicad_sym` beside it.
The one footprint drawn for this project, the Teensy socket, is in `dcu-carrier.pretty`, copied
from the ICU's. Everything else uses KiCad's stock footprint names.

The sheet was generated as a netlist-with-labels. Every pin ends in a short stub and a net label,
with no long wires, so it reads by net name rather than by tracing. Rearranging it by hand in
KiCad is fine and expected. Keep ERC at zero while you do.

## Checking it

```
kicad-cli sch erc dcu-carrier.kicad_sch --severity-all -o dcu-carrier-erc.rpt
kicad-cli sch export svg --no-background-color -o . dcu-carrier.kicad_sch
```

`CONVENTIONS.md §5` has the two netlist checks: the supplies never meet, and every BAT54S is the
right way round. The report is gitignored; the SVG is committed.

## Files

| File | What |
|---|---|
| `dcu-carrier.kicad_pro` · `.kicad_sch` | the project and the schematic |
| `dcu-carrier.kicad_sym` · `sym-lib-table` | every symbol used, kept with the project |
| `dcu-carrier.pretty` · `fp-lib-table` | the Teensy socket footprint (the ICU's, `confirm - not measured`) |
| `dcu-carrier.svg` | the committed picture: the reviewable form of a change |
| `CONVENTIONS.md` | how to draw it, and what differs from the ICU |
| `TARGET.md` | the drawing checklist from `dcu_channels`, a snapshot and not a link |

## What to draw next

The layout, `H-002`: footprints, a provisional outline, placement and routing. Follow
`../PCB-AND-3D-GUIDE.md` Part B. The outline is final only after `V-102`, and the mirror stage's
values only after `W-332`.

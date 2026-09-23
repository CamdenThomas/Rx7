# DCU carrier — the KiCad project

*Rev 2026-09-22 · owns: what this KiCad project is for, what it may claim, and when it starts.
The board's design is `../../data/dcu_channels.csv` — that is the record; this will be a drawing
of it. Read `../README.md` first: it is the fence.*

## Where it stands

**No sheet yet — the checklist is here, the schematic is not.** The DCU became this build's on
2026-09-22 (D-374), alongside the ICU. `TARGET.md` lists every block the sheet must carry, taken
from `dcu_channels`. The schematic starts when the four things it waits on are in the record (three are done; what is left is luxury `W-332` and block `00.28`):

| Waits on | What it settles on the sheet |
|---|---|
| ~~`V-083`~~ done (D-379) | the parts are chosen and datasheet-checked |
| ~~`V-101`~~ done, and block `00.28` | the currents are in; the fuses and the comfort connector's ground pins are yours to rule |
| ~~`H-007`~~ done (D-380) | the panel ribbon is `panel_ribbon`: 20-way IDC, 3 × 3 matrix, four encoders, the thumbstick |
| luxury `W-332` | the mirror heads' stall and clutch currents: SN17's four drivers |

Drawing before these would put parts on the sheet that the record hasn't chosen yet. Guide Part B
(`../PCB-AND-3D-GUIDE.md`) is the method once they land; `H-002` is the layout row.

## What it may and may not claim

The same as `../icu-carrier/README.md`, and for the same reasons:

**May:** how the parts on the carrier connect to each other: the protection on each input, the
two rails and where they never meet, the FET gates and their pull-downs, the half-bridges, the
shunt, decoupling, and what the ERC thinks of all of it.

**May not:** anything about the car, the harness or the drops. `DP-DCU 1` and `DP-DCU-B 10`
appear here only as pins on the board edge; what is on the other side belongs to `cavities.csv`.
**If this schematic and the record disagree, the record is right.**

**No Teensy pinout until layout.** The record gives pin classes only (`ADC`, `PWM out`,
`digital out`). When layout fixes a pin, it is promoted into `dcu_channels.teensy_pin`, not kept
only here.

**R11 applies:** none of the DCU's parts, loads or spaces has been measured. `V-102` measures the
space behind the centre stack, and the enclosure (`P152`) is drawn around the laid-out board and
that measurement, never an estimate.

## Files (when it starts)

Set up exactly like `../icu-carrier/`: `dcu-carrier.kicad_pro` · `.kicad_sch`, a project-local
`dcu-carrier.kicad_sym` and `sym-lib-table`, the committed `dcu-carrier.svg`, and `CONVENTIONS.md`
copied from the ICU's with what differs changed.

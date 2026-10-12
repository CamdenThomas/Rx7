# Y12 checkpoint - the DCU board's 2 x 13 header

_Checkpoint 3, 2026-10-11: the board passes the gate and is installed as `../../dcu-carrier.kicad_pcb`
(not committed - the overseer commits). `v12-drc-clean.kicad_pcb` here is a byte copy of it. Steps (5) and
(6) of the work row are done too (STEP, renders, BOM, README, enclosure). This folder can go with the rest of
`relay-attempt/`._

## Result

`kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity` on the installed board:
0 violations, 0 unconnected, 0 parity; exit 0. GND pours: one connected group (`gnd.py`), no isolated copper.
ERC 0 / 0. `check.py --board dcu`: 163 checks, 0 mismatches, 1 note (as before). Enclosure: 0 interferences.

## Placement

| Part | Was | Now |
|---|---|---|
| J4 (2 x 13) pin 1 | (14.0, 7.6) rot 90 | **(6.38, 7.6)** rot 90 - three pitches left; pins 7-26 on the old pads 1-20, right end where the 2 x 10's was |
| H1 | (4, 4) | **(4, 15)** |
| J10 Teensy | (50, 18) | not moved |
| F1 | new | (43.75, 3.6) rot 270 |
| R72 | new | (44.9, 7.3) rot 180 |
| R71 | new | (44.9, 11.76) rot 90 - astride the +3V3 trunk, pad 1 on the SDA trunk |
| TP1 | new | (39.0, 7.6) bottom side |
| R52 | (7.995, 14.225) | (8.55, 14.225) |
| R54 | (5.245, 18.475) | (8.55, 18.7) |
| R53 | (2.495, 18.475) | (2.495, 20.45) |
| R3 | (7.995, 18.475) | (5.245, 20.45) |
| C24 | (2.525, 14.245) rot 90 | (2.525, 24.5) rot 270 |
| R51 | (5.245, 14.225) | (19.4, 13.65) |

## Why the earlier attempt's four nets had no channel

- Every header signal funnels through the 13 mm between J4's last column and the Teensy's first. Pin 1 at 11.0
  put three new THT columns in that funnel; COL1, ENC_SEAT_PASS_B and JOY_Y lost their lanes.
- +5V reaches the Teensy's VIN only round the header's LEFT end; that corner had been filled with F1 / R71 / R72.

## What made this one close (in the order the problems appeared)

1. Shift the header a whole 7.62 mm: the funnel stays intact, the new parts fit in the gap beside pins 21-26.
2. But then columns 1-3 stand over the old "outside" runs (+5V's via, ENC_TEMP_A / ENC_SEAT_PASS_A / I2C_SCL going
   south-west). Sending those through column gaps boxed pins in; the router never got below 4 open nets.
   Fix: they wrap the header's west end on B.Cu, nested (ENC_FAN_B joins them and gets a tail to its trunk).
3. +5V: a 0.4 mm neck between columns 1 and 2, then F.Cu to its old via.
4. The west signals' order at the Teensy is the reverse of their pin order: COL2 / COL3 go on B.Cu under
   ROW1-3 / COL1 on F.Cu, which drop to B.Cu through a staircase of vias (all drawn by hand, `place11.py`).
5. The header's GND pins are ringed in on both layers: a GND rail along the top edge, under the +5V neck.
6. Only then freerouting, for the eight nets east of column 4 (any pass count closes them).

## Traps

- **pcbnew `Save()` rewrites the `.kicad_pro`.** A board loaded under another name has no project: every net is
  class Default, pours fill 0.3 mm from COMFORT / PGND copper, and the next save under the project's name wipes
  the net classes from the project file. Scratch DRC then lies. `refill.py` guards it; DRC in the tree is the gate.
- `GetTracks()` breaks after the first `Remove` in a process (`place11.py`, `cleanup.py` work round it).
- freerouting does not follow KiCad's T-junctions or pours: export with `dsn_prep.py` (every other net's copper
  becomes keepouts). Its last pass is not its best; `tryruns.py` tries several pass limits.
- zsh eats an unquoted `=0.2` argument.

## Commands (Mac, KiCad 10.0.6; no heredocs, no cd; scratch layout: s/ scripts, w/ a copy of the project, fr/ the jar)

```
KP=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
kicad-cli sch export netlist --format kicadsexpr -o net.txt dcu-carrier.kicad_sch
$KP place11.py <rev 0.03 board from git>.kicad_pcb net.txt w/p11.kicad_pcb     # placement, rip-up, drawn routes
python3 tryruns.py w/p11.kicad_pcb t /ENC_FAN_A,/ENC_TEMP_B,/ENC_SEAT_DRV_A,/ENC_SEAT_DRV_B,/ENC_SEAT_PASS_B,/JOY_PRESS,/JOY_X,/JOY_Y 8,100
        # = per run: dsn_prep.py -> freerouting -> ses_merge.py -> widen.py -> drc.py (frrun.py)
cp w/t-100.kicad_pcb w/dcu-carrier.kicad_pcb
python3 cleanup.py w/dcu-carrier.kicad_pcb                 # dangling stubs, by DRC uuid
$KP gnd.py w/dcu-carrier.kicad_pcb w/g.kicad_pcb 5         # stitch GND fragments; cp g over dcu-carrier
$KP refill.py w/dcu-carrier.kicad_pcb                      # with w/dcu-carrier.kicad_pro restored from git first
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o x.rpt w/dcu-carrier.kicad_pcb
```

freerouting: `curl -sL -o freerouting-2.5.0.jar https://github.com/freerouting/freerouting/releases/download/v2.5.0/freerouting-2.5.0.jar`
(65 MB, sha256 f6f51bb0...de3c7); run as `/opt/homebrew/opt/openjdk/bin/java -Djava.awt.headless=true -jar <jar>
--user_data_path=<dir with freerouting-userdata.json as freerouting.json> --gui.enabled=false -de in.dsn -do out.ses
-mp 100 --router.fanout.enabled=false --router.optimizer.enabled=false`.

# relay-attempt — the DCU board's 2 × 13 ribbon header (work `Y12`)

_Kept 2026-10-10 so a fresh agent can finish `Y12` from any clone. Nothing here is the board:
the board is `../dcu-carrier.kicad_pcb` (rev 0.03, 2 × 10 J4, DRC clean but 17 parity issues
against sheet rev 0.04, which already carries J4 2 × 13, R71 / R72, F1, TP1 and the 10 k
pull-downs R39 / R41). `python3 tools/rx7.py get 02-PROJECTS/01-electrical work Y12` is the
task; its note is the hand-off._

- `apply-boards/v6-h1-moved-4-nets-open.kicad_pcb` — the one attempt so far: H1 moved to
  (4, 15), J4 pin 1 at x 11.0, the new parts in the old H1 corner; left COL1, ENC_SEAT_PASS_B,
  JOY_Y and +5V open and a few isolated GND fragments. Start here or from the committed board.
- `apply-boards/*.py`, `snap.sh` — that attempt's pcbnew scripts: `board6.py` is the latest
  placement, `astar.py` / `astar_gnd.py` a raster router for single nets, `rip*.py` rip-up
  helpers, `stitch.py` / `gndvia.py` / `islands.py` pour stitching, `drcsum.py` a DRC summary,
  `dsn_post*.py` DSN fixes for freerouting, `widen.py` neck widening.
- `y11/` — the Y11 agent's scripts that re-routed locally without disturbing Y5's copper
  (`astar.py`, `build.py`, `dsn_export.py` / `dsn_post.py`, `fixviol.py`, `fin.py`,
  `gndcc_lib.py`, `dangle.py`) and `dcu10.ses`, the route it imported.

Run them with KiCad's Python (`/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`),
one process at a time. Delete this folder when `Y12` is done.

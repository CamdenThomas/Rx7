"""The Control Unit face board's mount behind the face (H-008), parametric (Y7, D-455). Built by tools/enclosure.py from the parameters below.

Reads `control-unit/data/cu-face-board-board.json` (from the board's .kicad_pcb, by `tools/enclosure_extract.py` with KiCad's Python -
re-run it whenever the board moves) and `cad/cu-face-board/cu-face-board.step` when it is there (cached in `cu-face-board-probe.json`
when it is not); writes the rear tray (`base`) and the front frame (`lid`) as STEP and STL into
cad/cu-face-board/enclosure/, in the board's own frame, and fit-checks them against the board STEP. Exit 0 built and
clear, 1 an interference or the measured envelope refused, 3 a crash.

How it hangs (V-113 decides which): the board's keys and knobs face the faceplate (luxury LP20).
Four M3 countersunk bolts from the faceplate's front pass the front frame's standoffs and the
board's corner holes into heat-set inserts in the rear tray's bosses, so the panel hangs on the
faceplate's bolts and the frame sets the gap from the board to the faceplate's back. The frame's
four slotted lip tabs are the other way: they screw to the back of the opening's lip if the
faceplate cannot carry it. The tray covers the back: the ribbon's IDC plug passes its floor under
J1, and the illumination lead (J2) leaves through a grommet.

This file is data: the parameters only. Build with (FreeCAD):
    freecadcmd 00-design/tools/enclosure.py --pass cu-face-board
"""

KIND = 'panel'             # build_carrier or build_panel in enclosure_lib
TITLE = 'Control Unit face board mount (H-008) - provisional, V-113 not measured'
ENVELOPE_ROW = 'V-113'          # the measurement that would set ENVELOPE
SEAL_DT13 = False          # the fit check squeezes each DT13's flange seal


# ---------------------------------------------------------------------------- parameters ----
# The placing envelope: V-113, the opening in the centre stack - width, height, and depth to the
# first thing behind it, mm. None until measured: the mount is then the provisional board outline
# (200 x 70, R3, confirm) plus walls, and nothing is checked.
ENVELOPE = None                      # V-113 - confirm

P = {
    # ASA, as the carriers: the centre stack's face is in the sun (D-270's 70 C); PETG's ~75-80 C
    # Tg leaves no margin and it creeps under the faceplate bolts. Never PLA.
    "MATERIAL": "ASA",
    "WALL": 2.5,
    "FLOOR": 2.5,
    "GAP": 0.5,              # board outline to the tray / frame walls
    "BACK_GAP": 3.0,         # under the deepest back-side part (the IDC header, J1)
    "BACK_MIN": 15.0,        # and room for J2's mated JST-XH plug and its lead's bend - confirm
    "BOSS_D": 8.0,
    # M3 brass heat-set insert, Ruthex RX-M3x5.7 class: bore 4.0 x 6.5 deep - confirm.
    "INSERT_BORE": 4.0, "INSERT_DEPTH": 6.5,
    "SCREW_CLEAR": 3.4,
    # The frame: board top face to the faceplate's back. 7 mm puts a PEC11R's bushing through a
    # ~3 mm plate for its nut and the 13 mm key actuators 6 mm past the plate's back into their
    # caps - confirm against the PEC11R drawing (F11) and the faceplate and caps (luxury LP20).
    "STANDOFF_FRONT": 7.0,
    "STANDOFF_D": 8.0,
    "WEB": 4.0,
    # Lip tabs: (side, fraction along it) - positions and the lip's holes confirm at V-113.
    "LIP_TABS": [("left", 0.5), ("right", 0.5), ("top", 0.5), ("bottom", 0.25)],
    "LIP_TAB_L": 10.0, "LIP_TAB_W": 12.0, "LIP_TAB_T": 2.5, "LIP_SLOT": 8.0,
    "RIBBON_REF": "J1",
    "RIBBON_SLOT_MARGIN": 1.5,   # the 2 x 13 IDC plug (D-458) passes the floor around J1's courtyard
    "GROMMETS": ["J2"],
    "GROMMET_HOLE": 8.0,          # a grommet for an 8 mm hole, 5 mm bore - confirm
}

"""The ICU carrier's enclosure (P111), parametric (Y7, D-455). One command, from anywhere:

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd make_enclosure.py

Reads `board.json` (from `../icu-carrier.kicad_pcb`, by `../../enclosure_extract.py` with KiCad's
Python - re-run it whenever the board moves) and `../icu-carrier.step` when it is there (cached in
`probe.json` when it is not); writes the base, the connector plate and the lid as STEP and STL beside
this file, in the board's own frame, and fit-checks them against the board STEP. Exit 0 built and
clear, 1 an interference or the measured envelope refused, 3 a crash.

Three parts, because TE mounts a DT13 by pushing it through the panel from inside and screwing the
flange to it (114-151046 3.11): the DT13s are screwed to the plate first, then board and plate drop
into the base together (the plate runs down slots in the side walls), the board screws to its four
bosses, and the lid closes over everything with a cord gasket.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import enclosure_lib as L  # noqa: E402

# ---------------------------------------------------------------------------- parameters ----
# The placing envelope: C4, the space behind the binnacle, length x width x depth in mm. None until
# Camden measures it: the box is then the provisional board outline (110 x 80, confirm) plus walls,
# and nothing is checked. Set it to the three numbers and the build refuses a box that does not fit.
ENVELOPE = None                      # C4 - confirm

P = {
    # ASA, not PETG: a dash reaches 70 C in the sun (D-270). ASA's heat deflection is ~95 C and it
    # does not yellow or embrittle in UV; PETG softens from ~75-80 C (Tg), which is no margin at
    # all behind the binnacle glass, and it creeps under the inserts' screw load. Both print; ASA
    # needs an enclosed printer. Never PLA (D-270).
    "MATERIAL": "ASA",
    "WALL": 3.0,          # side walls; 3 mm so the lid gasket groove sits on the wall's centre line
    "FLOOR": 3.0,
    "LID": 3.0,
    "PLATE": 3.0,         # the connector plate - TE's panel is 6.25 max (114-151046 3.11)
    "PLATE_LIP": 2.0,     # how far the side walls run past the plate's outer face (traps it)
    "SLOT_DEPTH": 1.5,    # the plate's channel into each side wall
    "SLOT_CLEAR": 0.3,    # total play of the plate in its channel
    "SLOT_BLOCK": 2.5,    # wall thickening outside each channel
    "FLOOR_GROOVE": 1.0,  # the plate's channel into the floor
    "GAP": 1.0,           # air between the parts' outline (board + every 3D body) and the walls
    "TOP_GAP": 2.0,       # air between the tallest part (the DT13 flange) and the lid
    "BOSS_H": 5.0,        # board bottom face above the floor; the back-side parts stand 1.8 mm
    "BOSS_D": 8.0,        # insert boss: bore + 2 x 2.0 mm wall (CNC Kitchen's minimum is 1.6)
    # M3 brass heat-set insert, Ruthex RX-M3x5.7 class (= CNC Kitchen M3 standard, M3 x 5.7 mm,
    # OD 4.6 knurl): bore 4.0 mm, 6.5 deep (the insert + 0.8 mm for displaced plastic) - confirm
    # against the insert bought.
    "INSERT_BORE": 4.0,
    "INSERT_DEPTH": 6.5,
    "SCREW_CLEAR": 3.4,   # M3 clearance through the lid
    "LUG_D": 9.0,         # the four lid-screw lugs outside the side walls
    # Mounting tabs to the car: (side, fraction along the side wall from the grommet face to the
    # plate). Positions confirm at C4. The left wall carries the RF window, so its tab sits at the
    # connector end, clear of the antenna's 5 mm.
    "TABS": [("left", 0.85), ("right", 0.85), ("right", 0.15)],
    "TAB_L": 14.0, "TAB_W": 14.0, "TAB_HOLE": 4.5,     # M4 or #8 self-tapper to the dash - confirm
    # DT13 cut-outs: TE 114-151046 option 2, placed on the housing as TE's 3D model has it
    # ("model") or on the footprint's pin field ("footprint"); printed holes come out small, so
    # each opening is opened by CUTOUT_CLEAR a side (TE's tolerance is +-0.12).
    "CUTOUT_ON": "model",
    "CUTOUT_CLEAR": 0.15,
    "SEAL_SQUEEZE_OFFSET": 0.0,   # 0 = the plate's inner face on the flange's front face (TE)
    # The grommet face (opposite the DT13s, D-270): the page button lead and the backlight lead
    # leave through rubber grommets; the display ribbon through a notch the lid's tongue closes.
    "GROMMETS": ["SW1", "J2"],
    "GROMMET_HOLE": 8.0,          # a grommet for an 8 mm hole, 5 mm bore, 3 mm panel - confirm
    "GROMMET_Z": 12.0,            # above the board's bottom face: over a mated JST-XH plug
    "RIBBON_REF": "J4",
    "RIBBON_WAYS": 16,            # the ME817EV CN8 2 x 8 on a 1.27 mm ribbon
    "RIBBON_SIDE_CLEAR": 1.0,
    "NOTCH_DEPTH": 3.0,
    "RIBBON_GAP": 1.5,            # ribbon 1.0 + 0.5 closed-cell foam tape under the tongue
    "TONGUE_CLEAR": 0.25,
    # The RF window: the left wall thinned to RF_WALL over the XIAO's span plus RF_KEEPOUT on every
    # side - a thin solid wall, not an opening (dust and the odd spill stay out), printed 100 %
    # solid (three 0.4 mm perimeters, no infill), and no metal within the keep-out.
    "RF_REF": "U8",
    "RF_SIDE": "left",
    "RF_KEEPOUT": 5.0,
    "RF_WALL": 1.2,
    # The lid gasket (D-270 "a gasket groove in the lid"): a 1.5 mm silicone cord in a groove on
    # the wall's centre line, 1.6 wide x 1.2 deep (20 % squeeze), across the plate's top edge.
    "GASKET_GROOVE_W": 1.6,
    "GASKET_GROOVE_D": 1.2,
    "GASKET_R": 3.0,
    "LID_VENTS": 0,
}


def main():
    board = L.load(os.path.join(HERE, "board.json"))
    step = os.path.join(os.path.dirname(HERE), "icu-carrier.step")
    pr = L.probe(board, step, os.path.join(HERE, "probe.json"))
    parts, info = L.build_carrier(P, board, pr)
    files = L.export(parts, HERE, "icu")
    fit = L.fit_check(parts, step, board, seal_refs=tuple(pr["dt13"].keys()))
    env = L.envelope_check(info, ENVELOPE)
    L.report("ICU carrier enclosure (P111) - provisional, C4 not measured", P, info, fit, files,
             env, "C4")
    bad = env is False or (fit and any(r["interferences"] for r in fit.values()))
    return 1 if bad else 0


try:
    rc = main()
except SystemExit:
    raise
except Exception:
    import traceback
    traceback.print_exc()
    rc = 3
sys.stdout.flush()
os._exit(rc)

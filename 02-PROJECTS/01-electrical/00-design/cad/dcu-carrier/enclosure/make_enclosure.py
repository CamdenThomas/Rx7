"""The DCU carrier's enclosure (P152), parametric (Y7, D-455). One command, from anywhere:

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd make_enclosure.py

Reads `board.json` (from `../dcu-carrier.kicad_pcb`, by `../../enclosure_extract.py` with KiCad's
Python - re-run it whenever the board moves) and `../dcu-carrier.step` when it is there (cached in
`probe.json` when it is not); writes the base, the connector plate and the lid as STEP and STL beside
this file, in the board's own frame, and fit-checks them against the board STEP. Exit 0 built and
clear, 1 an interference or the measured envelope refused, 3 a crash.

Three parts, as the ICU's: the three DT13s (J9 12-way, J2 8-way, J1 6-way) screw to the plate
first (TE 114-151046 3.11), board and plate drop into the base together, the board screws to its
four bosses, the lid closes over a cord gasket. The DCU's DT13s face -y; the box is built with them
toward +y and turned 180 degrees about the board's centre.

Heat (assumed, `confirm` against V-101's currents): the power stages' copper faces UP, toward the
lid - U5-U8 BTS3011TE tabs down onto the F.Cu comfort pours, U9 / U10 / U11 exposed pads into F.Cu
and the B.Cu plane. At the record's comfort loads the box dissipates about 3 W (four seat switches
at ~0.25 W, the mirror heat and window stages, both bucks); over this box's ~0.07 m2 of skin in
still air that is ~10 K over the cabin, so ~80 C at the 70 C dash-in-sun case. That is inside ASA
(~95 C HDT) and every part's rating, so the lid is plain: no vents (they let dust onto the 0.5 mm
comfort clearances) and no pad to the lid (a 3 mm ASA lid spreads almost nothing). LID_VENTS
puts slots in if the bench says otherwise.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import enclosure_lib as L  # noqa: E402

# ---------------------------------------------------------------------------- parameters ----
# The placing envelope: V-102, the space behind the centre stack, depth x width x height in mm.
# None until Camden measures it: the box is then the provisional board outline (180 x 80, confirm)
# plus walls, and nothing is checked. Set it and the build refuses a box that does not fit.
ENVELOPE = None                      # V-102 - confirm

P = {
    # ASA, not PETG: the dash reaches 70 C in the sun (D-270) and this box adds ~10 K of its own;
    # PETG softens from ~75-80 C (Tg), ASA's heat deflection is ~95 C and it is UV-stable. Never PLA.
    "MATERIAL": "ASA",
    "WALL": 3.0, "FLOOR": 3.0, "LID": 3.0,
    "PLATE": 3.0,         # TE's panel 6.25 max (114-151046 3.11)
    "PLATE_LIP": 2.0, "SLOT_DEPTH": 1.5, "SLOT_CLEAR": 0.3, "SLOT_BLOCK": 2.5, "FLOOR_GROOVE": 1.0,
    "GAP": 1.0, "TOP_GAP": 2.0,
    "BOSS_H": 5.0, "BOSS_D": 8.0,
    # M3 brass heat-set insert, Ruthex RX-M3x5.7 class (CNC Kitchen M3 standard): bore 4.0 x 6.5 deep
    # - confirm against the insert bought.
    "INSERT_BORE": 4.0, "INSERT_DEPTH": 6.5,
    "SCREW_CLEAR": 3.4, "LUG_D": 9.0,
    # Mounting tabs to the car: (side, fraction from the grommet face to the plate) - confirm at V-102.
    "TABS": [("left", 0.5), ("right", 0.5)],
    "TAB_L": 14.0, "TAB_W": 14.0, "TAB_HOLE": 4.5,
    "CUTOUT_ON": "model", "CUTOUT_CLEAR": 0.15, "SEAL_SQUEEZE_OFFSET": 0.0,
    # The grommet face (opposite the DT13s, D-362): the three servo leads (J6-J8), the cabin NTC (J3)
    # and the blower pigtail (J5) through rubber grommets, staggered in height because the headers
    # are 10-11 mm apart; the panel ribbon (J4) through the notch the lid's tongue closes.
    "GROMMETS": [("J6", 12.0), ("J7", 23.0), ("J8", 12.0), ("J3", 23.0), ("J5", 12.0), ("J12", 23.0)],  # J12: the radar alert lead (Y11, PLACEHOLDER); J11 (the A/C transducer, right edge) gets its side-wall hole when its route is known - confirm
    "GROMMET_HOLE": 8.0,          # a grommet for an 8 mm hole, 5 mm bore, 3 mm panel - confirm
    "GROMMET_Z": 12.0,
    "RIBBON_REF": "J4",
    "RIBBON_WAYS": 20,            # panel_ribbon, 2 x 10 IDC on a 1.27 mm ribbon
    "RIBBON_SIDE_CLEAR": 1.0, "NOTCH_DEPTH": 3.0, "RIBBON_GAP": 1.5, "TONGUE_CLEAR": 0.25,
    "RF_REF": None,
    "GASKET_GROOVE_W": 1.6, "GASKET_GROOVE_D": 1.2, "GASKET_R": 3.0,
    "LID_VENTS": 0,
}


def main():
    board = L.load(os.path.join(HERE, "board.json"))
    step = os.path.join(os.path.dirname(HERE), "dcu-carrier.step")
    pr = L.probe(board, step, os.path.join(HERE, "probe.json"))
    parts, info = L.build_carrier(P, board, pr)
    files = L.export(parts, HERE, "dcu")
    fit = L.fit_check(parts, step, board, seal_refs=tuple(pr["dt13"].keys()))
    env = L.envelope_check(info, ENVELOPE)
    L.report("DCU carrier enclosure (P152) - provisional, V-102 not measured", P, info, fit, files,
             env, "V-102")
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

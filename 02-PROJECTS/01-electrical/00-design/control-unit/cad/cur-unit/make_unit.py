"""The Control Unit Remote (CUR), a parametric MOCK-UP of its insides and its case (D-514; work row
Y25). One command, from anywhere:

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd make_unit.py

The left plate made a unit like the climate unit, but small: the plate's board (../left-plate, Y22)
on standoffs behind a faceplate whose openings - the two wink caps at their 19 mm pitch, the hatch
and fuel-door key caps, the mirror stick's well, a window for any symbol LED no opening lights - are
placed from the board's own footprints; the board's two leads leave at the back by a DT13
receptacle or a sealed grommet (REAR, block 01.41); two mounting ears. Not the print-ready model:
nothing left of the wheel is measured (R11), so every size is a parameter and every one a guess.

Every number is in `unit_params.py`; this file and `unit_lib.py` hold none. The board is read from
`../left-plate/left-plate.kicad_pcb`, the DT13 from `../dcu-carrier/enclosure/` (probe.json,
board.json), and the climate unit's `unit_lib.py` lends its generic code. Writes, beside this
file: `cur-unit.FCStd` (groups Insides and Case), the assembly `cur-unit.step`, one STEP per case
part, four line drawings `view-*.svg`, and `report.json`; prints the report.

Exit 0 built and clear; 1 a fit rule failed (nothing is built, the report says which parameter to
move and which way), an interference, or a check failed (the report says which); 3 a crash.

The self-test rebuilds under the parameter sets of `unit_params.SELFTEST`, writes nothing, and
holds each set to the outcome stored with it (exit 1 when one differs, 3 on a crash):

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd selftest.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(CAD)), "tools"))  # 00-design/tools: enclosure_lib
sys.path.insert(0, HERE)
import unit_params as U  # noqa: E402
import unit_lib as K  # noqa: E402


def main():
    src = K.load_source(CAD, U.P)
    if "--selftest" in sys.argv or os.environ.get("RX7_UNIT_SELFTEST"):
        if src["problems"]:
            for p in src["problems"]:
                print("  - " + p)
            return 1
        return K.selftest(U, src)
    res = K.run(U.P, src, U)
    files, views, gone = [], "", []
    if res["case"] is None:
        gone = K.clear_outputs(HERE)
    else:
        files = K.write_model(HERE, res["insides"], res["case"])
        try:
            files += K.write_views(U.P, HERE, res["insides"], res["case"], res["D"])
            views = "front / back / side / top"
        except Exception as e:                      # the drawings are a convenience, never a gate
            views = "skipped - the hidden-line projection failed (%s)" % e
    K.report_json(os.path.join(HERE, "report.json"), U.P, U, res, files, views)
    K.print_report(U.P, U, res, files, views, gone)
    return res["rc"]


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

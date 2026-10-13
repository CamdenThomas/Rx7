"""The climate control unit, a parametric MOCK-UP of its insides and its case (D-479, D-480; work
row Y14). One command, from anywhere:

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd make_unit.py

One sealed unit built like a stereo head unit: the faceplate and its dials, the panel board behind
it, the DCU carrier lying flat behind that, and every Deutsch DT13 in the rear wall in two rows -
the carrier's three below, DP-DCU-D on its own small board above, a second position reserved
beside it. By default it is ONE height front to back and the face grows to cover it (FACE_H None),
so it goes into its opening from the front; a typed FACE_H lower than the body builds the stepped
unit instead, and the report says which in its first line (`front install: yes` / `no`). Not the
print-ready model: nothing in the car is measured (R11), so every size is a parameter and most are
guesses.

Every number is in `unit_params.py`; this file and `unit_lib.py` hold none. The carrier is read
from `../dcu-carrier/enclosure/board.json` and `probe.json`, and from `../dcu-carrier.step` when it
is there. Writes, beside this file: `climate-unit.FCStd` (groups Insides and Case), the assembly
`climate-unit.step`, one STEP per case part, four line drawings `view-*.svg`, and `report.json`;
prints the report.

Exit 0 built and clear; 1 a fit rule failed (nothing is built, the report says which parameter to
move and which way), an interference, or the measured envelope refused; 3 a crash.

The self-test rebuilds under the parameter sets of `unit_params.SELFTEST`, writes nothing, and
holds each set to the outcome stored with it (exit 1 when one differs, 3 on a crash):

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd selftest.py
    (the same thing: freecadcmd make_unit.py --pass --selftest)
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
        return K.selftest(U, src)
    res = K.run(U.P, src, U)
    files, views, gone = [], "", []
    if res["case"] is None:
        gone = K.clear_outputs(HERE)
    else:
        files = K.write_model(HERE, res["insides"], res["case"])
        try:
            drawn = K.build_insides(U.P, res["D"], src, standin=True)
            files += K.write_views(U.P, HERE, drawn, res["case"], res["D"])
            views = "front / back / side / top, the carrier as stand-in blocks"
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

"""The ICU unit, a parametric MOCK-UP of its insides and its housing (D-491, D-270, D-268; work
row Y19). One command, from anywhere:

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd make_unit.py

One assembly that goes into the binnacle aperture from the front and is plugged from behind: the
12.3-inch bar display behind a bezel plate as the face, the display plate behind it carrying the
BT817 eval board and the display chain's driver boards, the ICU carrier lying flat behind or below
them with its radio's RF window, the page button in the bezel, and the two sealed DT13 halves
(DP-ICU-A, DP-ICU-B) in the rear plate. ONE height front to back, the face covering it. Not the
print-ready model (F1): nothing in the car is measured (R11), so every size is a parameter and most
are guesses.

Every number is in `unit_params.py`; this file and `unit_lib.py` hold none. The carrier is read
from `../icu-carrier/enclosure/board.json` and `probe.json`, and from `../icu-carrier/icu-carrier.step`
when it is there. Writes, beside this file: `icu-unit.FCStd` (groups Insides and Case), the
assembly `icu-unit.step`, one STEP per case part, four line drawings `view-*.svg`, and
`report.json`; prints the report.

Exit 0 built and clear; 1 a fit rule failed (nothing is built, the report says which parameter to
move and which way), an interference, the RF window, or the measured envelope refused; 3 a crash.

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

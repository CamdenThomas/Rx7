"""mockup.py - build one unit's parametric MOCK-UP: its insides and its case, from the part's
parameter table and its boards' files. One driver for every assembly (it replaced the three
make_unit.py copies, 2026-10-15). With FreeCAD's command-line binary, from anywhere:

    freecadcmd 00-design/tools/mockup.py --pass du-assembly          (or cu-assembly, cur-assembly)
    RX7_ASSEMBLY=cu-assembly freecadcmd 00-design/tools/mockup.py    (the same, by environment)
    add --selftest after the name (or RX7_UNIT_SELFTEST=1) for the self-test

On the Mac freecadcmd is /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd.

Reads (through parts.py): the part's parameter table <part>/data/<name>_params.py (every number of
the unit, each with what it is and why it is a guess), the library tools/<name>.py (the geometry),
and the boards' extracts and STEPs it names. Writes: the model and one STEP per case part into
<part>/cad/<name>/, four line drawings <name>-view-*.svg into <part>/diagrams/, and the report
<part>/data/<name>-report.json; prints the report.

Exit 0 built and clear; 1 a fit rule failed (nothing is built, the report says which parameter to
move and which way), an interference, or the measured envelope refused; 3 a crash or no assembly
named. The self-test rebuilds under the parameter sets of the table's SELFTEST in memory, writes
nothing, and holds each set to the outcome stored with it (exit 1 when one differs).
"""
import importlib.util
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import parts  # noqa: E402


def _load(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


def _assembly():
    for a in sys.argv[1:]:
        if a in parts.ASSEMBLIES:
            return a
    name = os.environ.get("RX7_ASSEMBLY", "")
    if name in parts.ASSEMBLIES:
        return name
    print("name the assembly: %s (after --pass, or in RX7_ASSEMBLY)" % ", ".join(sorted(parts.ASSEMBLIES)))
    return None


def main():
    name = _assembly()
    if not name:
        return 3
    part = parts.part_of(name)
    module = name.replace("-", "_")
    U = _load(module + "_params", os.path.join(parts.data_dir(part), module + "_params.py"))
    K = _load(module, os.path.join(TOOLS, module + ".py"))
    cad, views_dir = parts.cad_dir(name), parts.diagrams_dir(part)
    for d in (cad, views_dir, parts.data_dir(part)):
        os.makedirs(d, exist_ok=True)
    src = K.load_source(cad, U.P)
    if "--selftest" in sys.argv or os.environ.get("RX7_UNIT_SELFTEST"):
        return K.selftest(U, src)
    res = K.run(U.P, src, U)
    files, views, gone = [], "", []
    if res["case"] is None:
        gone = K.clear_outputs(cad) + K.clear_outputs(views_dir)
    else:
        files = K.write_model(cad, res["insides"], res["case"])
        try:
            drawn = K.build_insides(U.P, res["D"], src, standin=True)
            files += K.write_views(U.P, views_dir, drawn, res["case"], res["D"])
            views = "front / back / side / top, the boards as stand-in blocks"
        except Exception as e:                      # the drawings are a convenience, never a gate
            views = "skipped - the hidden-line projection failed (%s)" % e
    K.report_json(parts.data_file(name, "-report.json"), U.P, U, res, files, views)
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

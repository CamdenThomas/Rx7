"""enclosure.py - build one board's parametric enclosure (Y7, D-455) from its parameters. One driver
for the three boards that have one (it replaced three make_enclosure.py copies, 2026-10-15). With
FreeCAD's command-line binary, from anywhere:

    freecadcmd 00-design/tools/enclosure.py --pass cu-carrier      (or cu-face-board, du-carrier)
    RX7_BOARD=du-carrier freecadcmd 00-design/tools/enclosure.py   (the same, by environment)

Reads, through parts.py: the board's parameters <part>/data/<board>_enclosure_params.py (P,
ENVELOPE, KIND, TITLE, ENVELOPE_ROW, SEAL_DT13), its extract <part>/data/<board>-board.json (written
by enclosure_extract.py with KiCad's Python) and its STEP cad/<board>/<board>.step when it is there.
Writes: the probe cache <part>/data/<board>-probe.json (what only the 3D model knows: each DT13's
flange, housing and seal, every part's height), and the case parts as STEP and STL into
cad/<board>/enclosure/<board>-enclosure-<part>.step. Exit 0 built and clear, 1 an interference or
the measured envelope refused, 3 a crash or no board named.
"""
import importlib.util
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import enclosure_lib as L  # noqa: E402
import parts as layout  # noqa: E402

BOARDS = ("cu-carrier", "cu-face-board", "du-carrier")


def _board():
    for a in sys.argv[1:]:
        if a in BOARDS:
            return a
    b = os.environ.get("RX7_BOARD", "")
    if b in BOARDS:
        return b
    print("name the board: %s (after --pass, or in RX7_BOARD)" % ", ".join(BOARDS))
    return None


def main():
    board_name = _board()
    if not board_name:
        return 3
    part = layout.part_of(board_name)
    path = os.path.join(layout.data_dir(part), board_name.replace("-", "_") + "_enclosure_params.py")
    spec = importlib.util.spec_from_file_location("enclosure_params", path)
    E = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(E)
    board = L.load(layout.data_file(board_name, "-board.json"))
    step = layout.board_file(board_name, "step")
    pr = L.probe(board, step, layout.data_file(board_name, "-probe.json"))
    build = L.build_carrier if E.KIND == "carrier" else L.build_panel
    case, info = build(E.P, board, pr)
    outdir = os.path.join(layout.cad_dir(board_name), "enclosure")
    os.makedirs(outdir, exist_ok=True)
    files = L.export(case, outdir, board_name)
    if E.SEAL_DT13:
        fit = L.fit_check(case, step, board, seal_refs=tuple(pr["dt13"].keys()))
    else:
        fit = L.fit_check(case, step, board)
    env = L.envelope_check(info, E.ENVELOPE)
    L.report(E.TITLE, E.P, info, fit, files, env, E.ENVELOPE_ROW)
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

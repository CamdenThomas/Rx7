"""fc_run.py - FreeCAD's half of build.py: run by freecadcmd, never by hand (03-cad A04).

The job is a JSON file named by RX7_CAD_JOB: {"assembly", "rows" (the datums rows build.py read
through rx7.py), "glb_dir", "glb_prefix", "step", "meta", "linear"}. It imports the assembly's
params.py (numbers and parts) and geometry.py (solids), writes one glb per part (mm, z up, the
part's own frame, one node per solid) and one STEP of the whole assembly in the car's frame, and a
meta JSON (each part's file, bytes, box and nodes). Exit 0 written; 1 the assembly refuses its
parameters; 3 a crash.
"""
import json
import os
import sys
import traceback

JOB = json.load(open(os.environ["RX7_CAD_JOB"]))
HERE = JOB["model_dir"]
sys.path.insert(0, HERE)

import importlib  # noqa: E402

import partlib as L  # noqa: E402
from frame import Datum  # noqa: E402
import placing  # noqa: E402


def run():
    asm = JOB["assembly"]
    dt = {r["id"]: Datum(r) for r in JOB["rows"]}
    pm = importlib.import_module(asm + ".params")
    gm = importlib.import_module(asm + ".geometry")
    P = pm.params(dt)
    problems = pm.check(P) if hasattr(pm, "check") else []
    if problems:
        return {"problems": problems}, 1
    parts = pm.parts(P)
    shapes = gm.build(P)
    car_frame = getattr(gm, "CAR_FRAME", False)
    world = placing.world(parts)
    os.makedirs(JOB["glb_dir"], exist_ok=True)
    meta = {"assembly": asm, "parts": {}, "problems": [], "step": os.path.basename(JOB["step"])}
    step_items = []
    for p in parts:
        pid = p["id"]
        if p["kind"] == "node":
            continue
        nodes = shapes.get(pid)
        if not nodes:
            meta["problems"].append("%s: no solid built" % pid)
            continue
        own = []
        for nm, sh, col in nodes:
            s = sh.copy()
            if car_frame:                       # built in the car's frame: move to the part's own
                o = world[pid]["origin"]
                s.translate(L.V(-o[0], -o[1], -o[2]))
            own.append((nm, s, col))
            step_items.append((nm.split(":", 1)[1], placing.to_car(s, world[pid])))
        fname = placing.file_name(pid)
        path = os.path.join(JOB["glb_dir"], fname)
        info = L.write_part_glb(path, pid, own, JOB["linear"])
        vol = sum(s.Volume for _, s, _ in own)
        meta["parts"][pid] = {"glb": JOB["glb_prefix"] + fname, "bytes": info["bytes"],
                              "bbox": info["bbox"], "vertices": info["vertices"],
                              "triangles": info["triangles"], "nodes": [n for n, _, _ in own],
                              "volume_mm3": round(vol, 1), "valid": all(s.isValid() for _, s, _ in own)}
    L.write_step(JOB["step"], step_items)
    meta["step_bytes"] = os.path.getsize(JOB["step"])
    return meta, (1 if meta["problems"] else 0)


try:
    meta, rc = run()
    with open(JOB["meta"], "w") as fh:
        json.dump(meta, fh, indent=1)
except Exception:
    traceback.print_exc()
    rc = 3
sys.stdout.flush()
sys.stderr.flush()
os._exit(rc)

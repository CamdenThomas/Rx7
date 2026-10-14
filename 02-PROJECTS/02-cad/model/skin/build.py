"""skin/build.py - B01's second pass: cut the found FB model (01-INTAKE/model/rx7-fb.glb, the app's
home-page car) into the parts skin/params.py declares, move each into the car's frame and write one
glb per part to 02-APP/app/public/design/00-CAR/skin/ and the assembly's meta to out/skin.meta.json,
the files export_scene.py reads. Pure python (no FreeCAD, no Blender): the found model is a mesh.

    python3 02-PROJECTS/02-cad/model/skin/build.py        then  build.py --only scene

Which mesh is which part, by the found model's own names and materials:
  carpaint                     -> PT704-skin          glass         -> PT729
  tail_lamp_left / _right      -> PT601-L / PT601-R
  tire, rim, chrome, black, brakedisk at a corner  -> PT530-<corner> (tyre) / PT525-<corner> (the rest)
  every other surface          -> PT704-trim
The FL corner's meshes are left out: that corner is the corner assembly's, from factory figures.
"""
import json
import os
import sys
from array import array

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.dirname(HERE)
sys.path.insert(0, MODEL)
sys.path.insert(0, HERE)
import frame  # noqa: E402
import glbread  # noqa: E402
import placing  # noqa: E402
import params as SP  # noqa: E402
from partlib import G, COLOURS  # noqa: E402

ROOT = os.path.abspath(os.path.join(MODEL, "..", "..", ".."))
SRC = os.path.join(ROOT, "01-INTAKE", "model", "rx7-fb.glb")
APP = os.path.join(ROOT, "02-APP", "app", "public", "design", "00-CAR", "skin")
OUT = os.path.join(MODEL, "out", "skin.meta.json")
WHEEL_MATS = {"rim", "chrome", "black", "brakedisk"}

# the found model's materials, as the home page shows them (blend.py's), for the parts' glb
LOOK = {"carpaint": ((0.74, 0.75, 0.77, 1.0), 0.6, 0.35), "glass": ((0.55, 0.65, 0.72, 0.35), 0.0, 0.05),
        "tail_red": ((0.65, 0.05, 0.04, 1.0), 0.1, 0.3), "tire": ((0.06, 0.06, 0.07, 1.0), 0.0, 0.9),
        "rim": ((0.72, 0.73, 0.75, 1.0), 0.8, 0.3), "chrome": ((0.85, 0.86, 0.88, 1.0), 1.0, 0.15),
        "black": ((0.05, 0.05, 0.05, 1.0), 0.0, 0.6), "brakedisk": ((0.42, 0.41, 0.40, 1.0), 0.7, 0.45)}
TRIM = ((0.16, 0.16, 0.17, 1.0), 0.1, 0.7)


def to_car(p, P):
    s = P.v("scale")
    return (s * p[0], -s * p[2] + P.v("y_shift"), s * p[1])


def corner_of(lo, hi):
    """FL / FR / RL / RR of a mesh by its box centre in the car frame (x right, y forward)."""
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    return ("F" if cy > -1210 else "R") + ("L" if cx < 0 else "R")


def main():
    if not os.path.exists(SRC):
        print("no found model at %s (it stays on the machines, out of git)" % SRC)
        sys.exit(2)
    P = SP.params({r["id"]: frame.Datum(r) for r in frame.sql("02-cad", "select * from datums")})
    declared = {p["id"]: p for p in SP.parts(P)}
    meshes = glbread.read(SRC)
    groups = {}                                   # part id -> [(material, [car-frame points], tris)]
    for m in meshes:
        pts = [to_car(p, P) for p in m["positions"]]
        lo, hi = glbread.bbox(pts)
        mat, node = m["material"], m["node"]
        if node.startswith("tail_lamp_"):
            pid = "PT601-" + ("L" if "left" in node else "R")
        elif mat == "glass":
            pid = "PT729"
        elif mat == "carpaint":
            pid = "PT704-skin"
        elif mat == "tire" or mat in WHEEL_MATS:
            c = corner_of(lo, hi)
            if c == "FL":
                continue
            pid = ("PT530-" if mat == "tire" else "PT525-") + c
        else:
            pid = "PT704-trim"
            mat = "trim:" + mat
        groups.setdefault(pid, []).append((mat, pts, m["triangles"]))
    world = placing.world(list(declared.values()))
    os.makedirs(APP, exist_ok=True)
    meta = {"assembly": "skin", "parts": {}, "problems": [], "step": None, "step_bytes": 0}
    for pid, chunks in sorted(groups.items()):
        assert pid in declared, pid
        ox, oy, oz = world[pid]["origin"]          # the part's origin in the car's frame
        mats, matidx, prims = [], {}, []
        for mat, pts, tris in chunks:
            if mat not in matidx:
                rgba, met, rough = LOOK.get(mat, TRIM)
                matidx[mat] = len(mats)
                mats.append(G.material(mat.replace("trim:", ""), rgba, met, rough))
            pos = array("f")
            for x, y, z in pts:
                pos.extend((x - ox, y - oy, z - oz))
            idx = array("I")
            for t in tris:
                idx.extend(t)
            prims.append((matidx[mat], pos, array("f", G.face_normals(pos, idx)), idx))
        name = placing.file_name(pid)
        res = G.write_glb(os.path.join(APP, name), [{"name": "part:" + pid, "prims": prims}], mats, "part:" + pid)
        meta["parts"][pid] = {"glb": "skin/" + name, "bytes": res["bytes"], "bbox": res["bbox"],
                              "vertices": res["vertices"], "triangles": res["triangles"],
                              "nodes": ["part:" + pid], "volume_mm3": None, "valid": True}
        print("%-14s %7d triangles  %8d bytes" % (pid, res["triangles"], res["bytes"]))
    missing = sorted(set(declared) - set(groups))
    if missing:
        meta["problems"].append("declared but not in the found model: %s" % missing)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    print("skin: %d parts -> %s; %s" % (len(meta["parts"]), os.path.relpath(OUT, ROOT), meta["problems"] or "no problems"))


if __name__ == "__main__":
    main()

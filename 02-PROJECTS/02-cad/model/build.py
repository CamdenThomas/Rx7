#!/usr/bin/env python3
"""build.py - build the car's model headless and hand it to the app (02-cad A04, B01; D-516, D-518).

    python3 02-PROJECTS/02-cad/model/build.py                  every assembly, then scene.json
    python3 02-PROJECTS/02-cad/model/build.py --only corner    one assembly (corner | unibody | skin), then scene.json
    python3 02-PROJECTS/02-cad/model/build.py --only scene     scene.json alone, from the last build
    python3 02-PROJECTS/02-cad/model/build.py --selftest       hold scene.json to the contract
    python3 02-PROJECTS/02-cad/model/build.py --drafts DIR     also write the record drafts (model_parts,
                                                               model_dims, model_mates, 00-CAR parts) to DIR

From the tree's root; on the Mac every python3 call is `env DEVELOPER_DIR=/Library/Developer/CommandLineTools python3`.
Reads 02-cad `datums` and 00-CAR `parts` / `systems` through rx7.py; writes nothing to the record.
Writes the glb files and scene.json into 02-APP/app/public/design/00-CAR/ (the glb files are
git-ignored, scene.json is committed) and each assembly's STEP and meta into model/out/ (ignored).
It needs freecadcmd (FreeCAD 1.1; FREECADCMD overrides where it looks) for corner and unibody; skin
is plain python over the found model (skin/build.py, D-563) and is skipped where that file is absent.
Exit 0 built; 1 an assembly refuses its parameters or the scene breaks the contract; 3 a usage
error or a tool crash.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frame  # noqa: E402

ROOT = frame.ROOT
ASSEMBLIES = ["corner", "unibody", "skin"]
OUT = os.path.join(HERE, "out")
APP_DIR = os.path.join(ROOT, "02-APP", "app", "public", "design", "00-CAR")
FREECADCMD = os.environ.get("FREECADCMD",
                            "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd")
LINEAR = {"corner": 0.6, "unibody": 2.0}     # tessellation, mm


def build_assembly(asm, rows):
    if asm == "skin":                             # a mesh cut from the found model: no FreeCAD
        r = subprocess.run([sys.executable, os.path.join(HERE, "skin", "build.py")], capture_output=True, text=True)
        print((r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else "skin: rc %d" % r.returncode)
        return 0 if r.returncode in (0, 2) else r.returncode
    if not os.path.exists(FREECADCMD):
        print("freecadcmd is not at %s (set FREECADCMD)" % FREECADCMD, file=sys.stderr)
        return 3
    os.makedirs(OUT, exist_ok=True)
    meta_path = os.path.join(OUT, asm + ".meta.json")
    with tempfile.TemporaryDirectory() as tmp:
        job = {"assembly": asm, "rows": rows, "model_dir": HERE,
               "glb_dir": os.path.join(APP_DIR, asm), "glb_prefix": asm + "/",
               "step": os.path.join(OUT, asm + ".step"), "meta": meta_path,
               "linear": LINEAR[asm]}
        jp = os.path.join(tmp, "job.json")
        with open(jp, "w") as fh:
            json.dump(job, fh)
        r = subprocess.run([FREECADCMD, os.path.join(HERE, "fc_run.py")], cwd=tmp,
                           env=dict(os.environ, RX7_CAD_JOB=jp), capture_output=True, text=True)
    if r.returncode != 0:
        print("%s: freecadcmd rc %s\n%s" % (asm, r.returncode, (r.stderr or r.stdout)[-1500:]),
              file=sys.stderr)
        if os.path.exists(meta_path):
            print(json.load(open(meta_path)).get("problems"), file=sys.stderr)
        return 1 if r.returncode == 1 else 3
    m = json.load(open(meta_path))
    print("%s: %d parts, STEP %.2f MB, glb %.2f MB" % (
        asm, len(m["parts"]), m["step_bytes"] / 1e6,
        sum(p["bytes"] for p in m["parts"].values()) / 1e6))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=ASSEMBLIES + ["scene"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--drafts", metavar="DIR")
    a = ap.parse_args()
    import export_scene
    if a.selftest:
        return export_scene.selftest(os.path.join(APP_DIR, "scene.json"))
    try:
        dts = frame.sql("02-cad", "select * from datums")
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 3
    todo = [] if a.only == "scene" else ([a.only] if a.only else ASSEMBLIES)
    for asm in todo:
        rc = build_assembly(asm, dts)
        if rc:
            return rc
    rc = export_scene.write_scene(APP_DIR, OUT, dts, drafts=a.drafts)
    if rc:
        return rc
    return export_scene.selftest(os.path.join(APP_DIR, "scene.json"))


if __name__ == "__main__":
    sys.exit(main())

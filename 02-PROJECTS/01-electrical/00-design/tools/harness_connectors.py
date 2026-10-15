"""The harness's connectors in 3D for the app (D-514, D-515, work row Y24). One command, from the
tree's root:

    python3 02-PROJECTS/01-electrical/00-design/tools/harness_connectors.py [--out DIR] [--only VARIANT]
    python3 .../harness_connectors.py --check
    python3 .../harness_connectors.py --selftest

It writes, into DIR (default 02-APP/app/public/design/01-electrical/connectors):

  <variant>.glb   one per DEUTSCH variant the housings use (DT06-12S, DT04-12P, DT13-12PA ...)
  manifest.json   {variant: {glb, family, half, ways, size_mm, origin, confirm, source, standin,
                  cad, bytes, nodes, stamp}}

Owns no fact. The dimensions are 00-CAR `connector_dims` (read through `rx7.py sql`, never
copied here); the vendor models are 00-CAR `cad` rows (their `local_path`, out of git). A
variant whose `cad` row points at a model on this machine, in a frame this file knows (FRAMES:
TE's DT13 headers, measured on the Mac 2026-10-13), is converted from that model ("standin":
false); every other variant is drawn as a stand-in from its row ("standin": true): the body with
its wire-seal end, the latch (plugs) or the shroud (receptacles), the DT13's flange with its two
mounting holes, the cavities on the face in their rows, and the wedgelock.

The frame (the scene's, 00-design/README.md §13): millimetres, z up, the part's own frame. The
mating face is centred on the origin - for a plug its front face, for a receptacle the floor of
its shroud, where the plug's front face lands - the mate is along +Y and the wires leave along
-Y, so a mated pair is the receptacle and the plug turned half a turn about Z. Z up is the
housing as it is read: the plug's latch, the receptacle's latch ramp, the DT13's flange top.
Width (x) runs along the cavity rows. Nodes: body, latch (plug) or shroud (receptacle), flange
(DT13), cavities, wedgelock; a converted model has body, flange and shroud only.

Runs itself under FreeCAD (`freecadcmd`) for the geometry, with the job in RX7_CONNECTOR_JOB, and
writes each glb through 00-design/tools/export_glb.py's writer, so the files are packed exactly as
the rest of the scene (KHR_mesh_quantization, one primitive per material).

Exit 0 built / current / selftest passed - 1 a source is inconsistent (a housings variant with no
row, a glb whose box disagrees with its row, a stale file under --check) - 2 under --check, not
built on this machine - 3 a usage error or a tool crash.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile

SELF = os.environ.get("RX7_CONNECTOR_SELF") or os.path.abspath(__file__)   # freecadcmd may not set __file__
HERE = os.path.dirname(SELF)                                      # 00-design/tools
DESIGN = os.path.dirname(HERE)                                    # 00-design
TOOLS = HERE
ROOT = os.path.abspath(os.path.join(DESIGN, "..", "..", ".."))    # the tree
RX7 = os.path.join(ROOT, "tools", "rx7.py")
OUT_DEFAULT = os.path.join(ROOT, "02-APP", "app", "public", "design", "01-electrical", "connectors")
FREECADCMD = os.environ.get("FREECADCMD",
                            "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd")
ORIGIN = "mating face centre; mate +Y; wires -Y"
TOLERANCE = 1.0          # mm: a glb's box against its row
COLUMNS = ["id", "family", "half", "ways", "rows", "length_mm", "width_mm", "height_mm",
           "flange_w_mm", "flange_h_mm", "hole_pitch_mm", "hole_mm", "shroud_mm", "shroud_w_mm",
           "shroud_h_mm", "pitch_mm", "row_mm", "gap_mm", "cavity_mm", "wedgelock", "cad",
           "source"]
NUMS = {"length_mm", "width_mm", "height_mm", "flange_w_mm", "flange_h_mm", "hole_pitch_mm",
        "hole_mm", "shroud_mm", "shroud_w_mm", "shroud_h_mm", "pitch_mm", "row_mm", "gap_mm",
        "cavity_mm"}

# A vendor model's frame, by family: the matrix that takes the file's axes to the scene's (rows of
# a 3x3, x' = row 0 . (x, y, z)). TE's DT13 customer-view models put the mate along +z and the
# flange top (away from the PCB tails) along +y, so x' = -x, y' = z, z' = y. Only a frame measured
# against the file goes here; a DT or DTP model (obtained on the PC, never opened on the Mac) is
# drawn as a stand-in until its frame is read (Y27).
# TE's DRC models share the frame (DRC13-24PA read 2026-10-14, Y63: its tails land on the footprint so).
FRAMES = {"DT13": [[-1, 0, 0], [0, 0, 1], [0, 1, 0]], "DRC": [[-1, 0, 0], [0, 0, 1], [0, 1, 0]]}

COLOURS = {   # name: rgba, metallic, roughness - display colours, not TE's
    "DT": ((0.62, 0.63, 0.64, 1.0), 0.0, 0.65),
    "DTP": ((0.07, 0.07, 0.08, 1.0), 0.0, 0.55),
    "DT13": ((0.62, 0.63, 0.64, 1.0), 0.0, 0.65),
    "CMC": ((0.08, 0.08, 0.09, 1.0), 0.0, 0.55),
    "DRC": ((0.06, 0.06, 0.07, 1.0), 0.0, 0.5),
    "flange": ((0.36, 0.37, 0.38, 1.0), 0.0, 0.6),
    "wedgelock": ((0.85, 0.45, 0.12, 1.0), 0.0, 0.6),
    "cavities": ((0.03, 0.03, 0.03, 1.0), 0.0, 0.9),
}
LINEAR, ANGULAR = 0.1, 0.4           # mm, rad: the stand-ins
MODEL_LINEAR, MODEL_ANGULAR = 0.08, 0.35


class Fail(Exception):
    """rc 1: a source is inconsistent."""


class Crash(Exception):
    """rc 3: a tool is missing or crashed."""


# ======================================================================== pure (both pythons) ==
def cavity_layout(row):
    """[(x, z)] of each cavity on the face, centred on it: `rows` rows along x, `pitch_mm` apart
    in a row (`gap_mm` in the middle where TE's layout widens it), the rows `row_mm` apart in z."""
    ways, rows = int(row["ways"]), int(row["rows"])
    if rows < 1 or ways % rows:
        raise Fail("%s: %d ways do not split into %d rows" % (row["id"], ways, rows))
    n, p = ways // rows, float(row["pitch_mm"])
    gap = float(row["gap_mm"]) if row.get("gap_mm") not in (None, "") else p
    half = n // 2
    if n % 2:
        xs = [(i - half) * p for i in range(n)]
    else:
        right = [gap / 2.0 + i * p for i in range(half)]
        xs = [-x for x in reversed(right)] + right
    dz = float(row["row_mm"]) if rows > 1 else 0.0
    zs = [((rows - 1) / 2.0 - k) * dz for k in range(rows)]
    return [(round(x, 4), round(z, 4)) for z in zs for x in xs]


def rx7_sql(area, query):
    """Rows of `rx7.py sql` as dicts. Refuses a line that does not split into the header's
    columns (a cell holding ' | ' would) rather than guess."""
    r = subprocess.run([sys.executable, RX7, "sql", area, query], capture_output=True, text=True,
                       cwd=ROOT)
    if r.returncode == 2:
        return []
    if r.returncode != 0:
        raise Crash("rx7.py sql %s failed (rc %d): %s" % (area, r.returncode, r.stderr[-400:]))
    lines = r.stdout.split("\n")
    names = lines[0].split(" | ")
    out = []
    for ln in lines[1:]:
        if ln.startswith("(") and ln.endswith(" row(s))"):
            break
        cells = ln.split(" | ")
        if len(cells) != len(names):
            raise Fail("rx7.py sql %s: a row does not split into %d columns: %r"
                       % (area, len(names), ln[:120]))
        out.append(dict(zip(names, cells)))
    return out


def read_rows(only=None):
    rows = rx7_sql("00-CAR", "select %s from connector_dims order by id" % ", ".join(COLUMNS))
    for r in rows:
        for k in NUMS:
            r[k] = float(r[k]) if r[k] != "" else None
        r["ways"], r["rows"] = int(r["ways"]), int(r["rows"])
    if only:
        rows = [r for r in rows if r["id"] == only]
        if not rows:
            raise Fail("%s has no connector_dims row (00-CAR)" % only)
    return rows


def housing_variants():
    """Every variant the 01-electrical housings name, either half."""
    out = set()
    for h in rx7_sql("01-electrical", "select leg_side, box_side from housings"):
        out |= {h["leg_side"], h["box_side"]}
    return sorted(v for v in out if v)


def model_paths(rows, tmp):
    """{variant: STEP path on this machine} for each row whose cad row has a model here (a .stp or
    .step in local_path, else the one inside its zip, extracted to tmp) and whose family has a
    measured frame. {variant: reason} for the ones found but not used."""
    ids = sorted({r["cad"] for r in rows if r["cad"]})
    if not ids:
        return {}, {}
    cad = {c["id"]: c for c in rx7_sql(
        "00-CAR", "select id, local_path from cad where id in (%s)"
        % ", ".join("'%s'" % i for i in ids))}
    use, unused = {}, {}
    for r in rows:
        c = cad.get(r["cad"])
        if not c or not c["local_path"]:
            continue
        d = os.path.join(ROOT, c["local_path"])
        if not os.path.isdir(d):
            continue
        names = sorted(os.listdir(d))
        steps = [n for n in names if n.lower().endswith((".stp", ".step"))]
        path = os.path.join(d, steps[0]) if steps else None
        if path is None:
            zips = [n for n in names if n.lower().endswith(".zip")]
            for z in zips:
                with zipfile.ZipFile(os.path.join(d, z)) as zf:
                    inner = [m for m in zf.namelist() if m.lower().endswith((".stp", ".step"))
                             and "/" not in m and not m.startswith(".")]
                    if inner:
                        dst = os.path.join(tmp, r["id"] + ".stp")
                        with zf.open(inner[0]) as src, open(dst, "wb") as fh:
                            fh.write(src.read())
                        path = dst
                        break
        if path is None:
            continue
        if r["family"] not in FRAMES:
            unused[r["id"]] = ("%s's model is on this machine but its frame has not been read "
                               "(FRAMES): drawn as a stand-in" % r["cad"])
            continue
        use[r["id"]] = path
    return use, unused


def stamp(row, model):
    h = hashlib.sha256()
    h.update(json.dumps(row, sort_keys=True).encode())
    with open(SELF, "rb") as fh:
        h.update(fh.read())
    if model:
        h.update(str(os.path.getsize(model)).encode())
    return h.hexdigest()[:16]


# ================================================================================ host side ==
def run_fc(job):
    if not os.path.exists(FREECADCMD):
        raise Crash("freecadcmd is not at %s (set FREECADCMD)" % FREECADCMD)
    with tempfile.TemporaryDirectory() as tmp:
        jpath = os.path.join(tmp, "job.json")
        job = dict(job, meta=os.path.join(tmp, "meta.json"))
        with open(jpath, "w") as fh:
            json.dump(job, fh)
        env = dict(os.environ, RX7_CONNECTOR_JOB=jpath, RX7_CONNECTOR_SELF=SELF)
        r = subprocess.run([FREECADCMD, SELF], env=env, capture_output=True,
                           text=True, cwd=tmp)
        meta = json.load(open(job["meta"])) if os.path.exists(job["meta"]) else None
        if r.returncode != 0 or meta is None:
            raise Crash("freecadcmd failed (rc %s): %s" % (r.returncode,
                                                           (r.stderr or r.stdout)[-800:]))
        return meta


def build_all(out_dir=OUT_DEFAULT, only=None):
    """Build every variant's glb (or only one) into out_dir and write manifest.json beside them.
    Returns the manifest (every variant built so far, the others kept from the file)."""
    rows = read_rows(only)
    os.makedirs(out_dir, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        models, unused = model_paths(rows, tmp)
        job = {"tools_dir": TOOLS, "out": out_dir, "rows": rows, "models": models,
               "frames": FRAMES, "colours": COLOURS,
               "tess": [LINEAR, ANGULAR, MODEL_LINEAR, MODEL_ANGULAR]}
        meta = run_fc(job)
        stamps = {r["id"]: stamp(r, models.get(r["id"])) for r in rows}
    mpath = os.path.join(out_dir, "manifest.json")
    manifest = {}
    if only and os.path.exists(mpath):
        manifest = json.load(open(mpath))
    for r in rows:
        m = meta[r["id"]]
        lo, hi = m["bbox"]
        standin = r["id"] not in models
        entry = {
            "glb": "connectors/%s.glb" % r["id"], "family": r["family"], "half": r["half"],
            "ways": r["ways"],
            "size_mm": {"x": round(hi[0] - lo[0], 2), "y": round(hi[1] - lo[1], 2),
                        "z": round(hi[2] - lo[2], 2)},
            "bbox_mm": [lo, hi], "origin": ORIGIN, "confirm": True,
            "source": r["source"] if standin else r["cad"], "standin": standin,
            "cad": r["cad"] or None, "bytes": m["bytes"], "nodes": m["nodes"],
            "stamp": stamps[r["id"]]}
        if r["id"] in unused:
            entry["note"] = unused[r["id"]]
        manifest[r["id"]] = entry
    manifest = {k: manifest[k] for k in sorted(manifest)}
    with open(mpath + ".part", "w") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    os.replace(mpath + ".part", mpath)
    return manifest


def _glb_tools():
    sys.path.insert(0, TOOLS)
    import export_glb as G
    return G


def selftest(out_dir=OUT_DEFAULT):
    """[problem sentences]: every housings variant has a row, a glb and a manifest entry; each glb
    is the manifest's bytes, carries its nodes and fits its row's box within TOLERANCE."""
    probs = []
    # the layout, pure
    for ways, rows, gap, want in ((2, 1, None, [(-2.73, 0.0), (2.73, 0.0)]),
                                  (8, 2, 5.46, [(-7.18, 4.56), (-2.73, 4.56), (2.73, 4.56),
                                                (7.18, 4.56)])):
        r = {"id": "t", "ways": ways, "rows": rows, "pitch_mm": 5.46 if ways == 2 else 4.45,
             "row_mm": 9.12, "gap_mm": gap}
        got = cavity_layout(r)
        if len(got) != ways or any(abs(a[0] - b[0]) > 1e-3 or abs(a[1] - b[1]) > 1e-3
                                   for a, b in zip(got, want)):
            probs.append("cavity_layout(%d ways) gives %s, not %s" % (ways, got[:4], want))
    rows = {r["id"]: r for r in read_rows()}
    for r in rows.values():
        try:
            cavity_layout(r)
        except Fail as e:
            probs.append(str(e))
    mpath = os.path.join(out_dir, "manifest.json")
    if not os.path.exists(mpath):
        return probs + ["%s is not there: build first" % os.path.relpath(mpath, ROOT)]
    man = json.load(open(mpath))
    G = _glb_tools()
    for v in housing_variants():
        if v not in rows:
            probs.append("housings name %s, which has no connector_dims row (00-CAR)" % v)
        if v not in man:
            probs.append("housings name %s, which the manifest does not list" % v)
    for v, e in man.items():
        path = os.path.join(out_dir, os.path.basename(e["glb"]))
        if not os.path.exists(path):
            probs.append("%s: %s is not there" % (v, e["glb"]))
            continue
        if os.path.getsize(path) != e["bytes"]:
            probs.append("%s: the glb is %d bytes, the manifest says %d"
                         % (v, os.path.getsize(path), e["bytes"]))
        js, _ = G.read_glb(path)
        names = {n.get("name") for n in js["nodes"]}
        need = {"body"} | ({"flange"} if e["family"] in ("DT13", "DRC") and e["half"] == "receptacle" else set()) | \
            ({"shroud"} if e["half"] == "receptacle" else {"latch"})
        if e["standin"]:
            need |= {"cavities"} | (set() if e["family"] in ("DT13", "CMC", "DRC") and e["half"] == "receptacle"
                                    else {"wedgelock"})
        if need - names:
            probs.append("%s: the glb has no node %s" % (v, ", ".join(sorted(need - names))))
        r = rows.get(v)
        if r is None:
            probs.append("%s: in the manifest, but no connector_dims row" % v)
            continue
        lo, hi = G.glb_bbox(path)
        for ax, col in ((0, "width_mm"), (1, "length_mm"), (2, "height_mm")):
            size = hi[ax] - lo[ax]
            if abs(size - r[col]) > TOLERANCE:
                probs.append("%s: the glb is %.2f mm along %s, the row's %s is %s"
                             % (v, size, "xyz"[ax], col, r[col]))
        if lo[1] > 0.5 or (e["half"] == "plug" and abs(hi[1]) > 0.5):
            probs.append("%s: the mating face is not at the origin (y %.2f .. %.2f)"
                         % (v, lo[1], hi[1]))
    return probs


def check(out_dir=OUT_DEFAULT):
    """rc 0 current, 1 stale, 2 not built here."""
    mpath = os.path.join(out_dir, "manifest.json")
    rows = read_rows()
    if not os.path.exists(mpath):
        print("not built on this machine: %s" % os.path.relpath(mpath, ROOT))
        return 2
    man = json.load(open(mpath))
    missing, stale = [], []
    with tempfile.TemporaryDirectory() as tmp:
        models, _ = model_paths(rows, tmp)
        for r in rows:
            e = man.get(r["id"])
            path = os.path.join(out_dir, "%s.glb" % r["id"])
            if e is None or e.get("stamp") != stamp(r, models.get(r["id"])):
                stale.append(r["id"])
            elif not os.path.exists(path):
                missing.append(r["id"])
            elif os.path.getsize(path) != e["bytes"]:
                stale.append(r["id"])
    for v in stale:
        print("stale: %s (its row, this builder or its model changed)" % v)
    for v in missing:
        print("not built on this machine: %s.glb" % v)
    if stale:
        return 1
    return 2 if missing else 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--only", metavar="VARIANT")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.check:
            return check(a.out)
        if a.selftest:
            probs = selftest(a.out)
            for p in probs:
                print(p)
            print("selftest: %s" % ("%d problem(s)" % len(probs) if probs else "passed"))
            return 1 if probs else 0
        man = build_all(a.out, a.only)
        total = 0
        for v, e in man.items():
            if a.only and v != a.only:
                continue
            total += e["bytes"]
            s = e["size_mm"]
            print("%-10s %7.1f kB  %5.1f x %5.1f x %5.1f mm  %s"
                  % (v, e["bytes"] / 1024.0, s["x"], s["y"], s["z"],
                     "stand-in" if e["standin"] else "model " + e["cad"]))
        print("%d connector(s), %.2f MB -> %s" % (len(man) if not a.only else 1, total / 1048576.0,
                                                  os.path.relpath(a.out, ROOT)))
        return 0
    except Fail as e:
        print("problem: %s" % e)
        return 1
    except Crash as e:
        print("crash: %s" % e)
        return 3


# ============================================================================= FreeCAD side ==
def _fc_main(job):
    import array
    import FreeCAD
    import MeshPart
    import Part
    sys.path.insert(0, job["tools_dir"])
    import export_glb as G
    V = FreeCAD.Vector
    lin, ang, mlin, mang = job["tess"]
    col = job["colours"]

    def mesh(shape, mat, linear, angular, assign=None):
        """[(node, (material, positions, normals, indices))] one patch per face."""
        MeshPart.meshFromShape(Shape=shape, LinearDeflection=linear, AngularDeflection=angular,
                               Relative=False)
        out = []
        for f in shape.Faces:
            pts, tris = f.tessellate(linear)
            if not tris:
                continue
            pos = array.array("f", [c for p in pts for c in (p.x, p.y, p.z)])
            idx = [i for t in tris for i in t]
            out.append((assign(f) if assign else None,
                        (mat, pos, G.face_normals(pos, idx), idx)))
        return out

    def rrect(w, h, r, y0, y1, x=0.0, z=0.0):
        """A rounded rectangle w (x) by h (z), extruded from y0 to y1."""
        r = max(0.0, min(r, w / 2.0 - 0.01, h / 2.0 - 0.01))
        s = Part.makeBox(w, y1 - y0, h, V(x - w / 2.0, y0, z - h / 2.0))
        if r > 0.05:
            edges = [e for e in s.Edges if abs(e.BoundBox.YLength - (y1 - y0)) < 1e-6
                     and e.BoundBox.XLength < 1e-6 and e.BoundBox.ZLength < 1e-6]
            s = s.makeFillet(r, edges)
        return s

    def cyl(r, x, z, y0, y1):
        return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))

    def box(x0, x1, y0, y1, z0, z1):
        return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

    def standin(r):
        """{node: [solids]} for one variant, from its row."""
        W, L, H = r["width_mm"], r["length_mm"], r["height_mm"]
        rad = r["cavity_mm"] / 2.0
        cav = cavity_layout(r)
        nodes = {}
        if r["family"] in ("DT13", "CMC", "DRC") and r["half"] == "receptacle":
            S, sw, sh = r["shroud_mm"], r["shroud_w_mm"], r["shroud_h_mm"]
            fw, fh, hp, hd = r["flange_w_mm"], r["flange_h_mm"], r["hole_pitch_mm"], r["hole_mm"]
            ft = 3.0                                   # the flange's thickness, drawn
            wall = 1.6
            shroud = rrect(sw, sh, 3.0, 0.0, S).cut(rrect(sw - 2 * wall, sh - 2 * wall, 2.0,
                                                          0.0, S + 0.1))
            nodes["shroud"] = [shroud]
            boss = (W - hp) / 2.0                      # the ears reach the model's width
            flange = rrect(fw, fh, 2.0, -ft, 0.0)
            for sx in (-1, 1):
                flange = flange.fuse(cyl(boss, sx * hp / 2.0, 0.0, -ft, 0.0))
            for sx in (-1, 1):
                flange = flange.cut(cyl(hd / 2.0, sx * hp / 2.0, 0.0, -ft - 0.1, 0.1))
            nodes["flange"] = [flange.removeSplitter()]
            back = L - S - ft                          # behind the flange, to the PCB tails
            body = rrect(sw + 4.0, sh + 4.0, 2.0, -ft - back, -ft)
            tails = box(-sw / 2.0, sw / 2.0, -ft - back, -ft - back + 6.0, fh / 2.0 - H,
                        -sh / 2.0)
            nodes["body"] = [body, tails]
            nodes["cavities"] = [cyl(rad, x, z, 0.0, 0.6 * S) for (x, z) in cav]
            return nodes
        if r["half"] == "plug":
            lh = min(3.0, 0.18 * H)                    # the latch, drawn
            hb = H - lh
            front = 0.72 * L
            pocket = rrect(W - 3.0, hb - 3.0, 1.5, -0.8, 0.01)
            holes = [cyl(rad, x, z, -4.0, 0.1) for (x, z) in cav]
            body = rrect(W, hb, min(2.5, hb / 4.0), -front, 0.0).cut(pocket)
            for h in holes:
                body = body.cut(h)
            seal = rrect(W - 2.0, hb - 2.0, min(2.0, hb / 4.0), -L, -front)
            nodes["body"] = [body, seal]
            lw = min(8.0, 0.4 * W)
            nodes["latch"] = [box(-lw / 2.0, lw / 2.0, -0.6 * L, -0.08 * L, hb / 2.0 - 0.5,
                                  hb / 2.0 + lh)]
            wl = rrect(W - 3.0, hb - 3.0, 1.5, -0.8, 0.0)
            for h in holes:
                wl = wl.cut(h)
            nodes["wedgelock"] = [wl]
            nodes["cavities"] = [cyl(rad, x, z, -4.0, -0.4) for (x, z) in cav]
            return nodes
        # a receptacle: the shroud in front of the origin, the body behind
        S = r["shroud_mm"]
        rh = min(2.0, 0.1 * H)                         # the latch ramp, drawn
        hs = H - rh
        wall = 1.6
        shroud = rrect(W, hs, min(2.5, hs / 4.0), 0.0, S).cut(
            rrect(W - 2 * wall, hs - 2 * wall, min(1.5, hs / 5.0), 0.0, S + 0.1))
        ramp = box(-0.2 * W, 0.2 * W, 0.45 * S, 0.85 * S, hs / 2.0 - 0.5, hs / 2.0 + rh)
        nodes["shroud"] = [shroud, ramp]
        back = L - S
        nodes["body"] = [rrect(W - 1.0, hs - 1.0, min(2.0, hs / 4.0), -0.75 * back, 0.0),
                         rrect(W - 2.5, hs - 2.5, min(2.0, hs / 4.0), -back, -0.75 * back)]
        wl = rrect(W - 2 * wall - 1.0, hs - 2 * wall - 1.0, 1.0, 0.0, 1.2)
        for (x, z) in cav:
            wl = wl.cut(cyl(rad + 0.3, x, z, -0.1, 1.3))
        nodes["wedgelock"] = [wl]
        nodes["cavities"] = [cyl(rad, x, z, 0.0, 0.55 * S) for (x, z) in cav]
        return nodes

    def model(r, path):
        """The vendor model in the scene's frame, its faces split into body, flange and shroud by
        where they sit along the mate."""
        s = Part.read(path)
        m = job["frames"][r["family"]]
        M = FreeCAD.Matrix(m[0][0], m[0][1], m[0][2], 0, m[1][0], m[1][1], m[1][2], 0,
                           m[2][0], m[2][1], m[2][2], 0, 0, 0, 0, 1)
        s = s.copy()
        s.transformShape(M, True)
        tip = s.optimalBoundingBox().YMax        # BoundBox is loose on curved faces
        sec = s.slice(V(0, 1, 0), tip - 3.0)
        nb = None
        for w in sec:
            nb = FreeCAD.BoundBox(w.BoundBox) if nb is None else (nb.add(w.BoundBox) or nb)
        if nb is None:
            raise RuntimeError("%s: no section 3 mm in from the tip" % r["id"])
        s.translate(V(-nb.Center.x, -(tip - r["shroud_mm"]), -nb.Center.z))
        b = s.BoundBox
        # the flange: the slab whose section is (nearly) the widest
        ys, widths = [], []
        y = b.YMin + 0.1
        while y < b.YMax:
            ws = s.slice(V(0, 1, 0), y)
            if ws:
                xb = None
                for w in ws:
                    xb = FreeCAD.BoundBox(w.BoundBox) if xb is None else (xb.add(w.BoundBox) or xb)
                ys.append(y)
                widths.append(xb.XLength * xb.ZLength)
            y += 0.25
        top = max(widths)
        slab = [yy for yy, a in zip(ys, widths) if a >= 0.95 * top]
        f0, f1 = min(slab) - 0.25, max(slab) + 0.25

        def assign(face):
            c = face.BoundBox.Center.y
            return "shroud" if c > f1 else "flange" if c >= f0 else "body"
        return s, assign

    mats = [G.material("body", *col[fam]) for fam in ("DT", "DTP", "DT13", "CMC", "DRC")] + \
        [G.material(n, *col[n]) for n in ("flange", "wedgelock", "cavities")]
    mix = {m["name"]: i for i, m in enumerate(mats)}
    fam_mat = {"DT": 0, "DTP": 1, "DT13": 2, "CMC": 3, "DRC": 4}
    order = ["body", "latch", "shroud", "flange", "cavities", "wedgelock"]
    meta = {}
    for r in job["rows"]:
        path = job["models"].get(r["id"])
        groups = {}
        if path:
            s, assign = model(r, path)
            for node, prim in mesh(s, fam_mat[r["family"]], mlin, mang, assign):
                if node == "flange":
                    prim = (mix["flange"],) + prim[1:]
                groups.setdefault(node, []).append(prim)
        else:
            for node, solids in standin(r).items():
                mat = fam_mat[r["family"]] if node == "body" else mix.get(node, fam_mat[r["family"]])
                for so in solids:
                    groups.setdefault(node, []).extend(p for _, p in mesh(so, mat, lin, ang))
        nodes = [{"name": n, "prims": groups[n]} for n in order if groups.get(n)]
        dst = os.path.join(job["out"], "%s.glb" % r["id"])
        info = G.write_glb(dst, nodes, mats, r["id"], extras={
            "source": "00-CAR connector_dims %s" % r["id"] + (
                "; model %s" % os.path.basename(path) if path else "; stand-in"),
            "origin": ORIGIN, "confirm": True})
        meta[r["id"]] = {"bytes": info["bytes"], "bbox": info["bbox"],
                         "nodes": [n["name"] for n in nodes]}
    return meta


if os.environ.get("RX7_CONNECTOR_JOB"):
    _job = json.load(open(os.environ["RX7_CONNECTOR_JOB"]))
    _rc = 0
    try:
        _meta = _fc_main(_job)
        with open(_job["meta"], "w") as _fh:
            json.dump(_meta, _fh)
    except Exception:
        import traceback
        traceback.print_exc()
        _rc = 3
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(_rc)
elif __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

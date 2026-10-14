#!/usr/bin/env python3
"""export_scene.py - the car's scene.json for the app's Manual model page (02-cad C01's contract;
02-APP MG1), and the record drafts. Called by build.py; run alone for --selftest.

    python3 02-PROJECTS/02-cad/model/export_scene.py --selftest [SCENE]

Reads: each assembly's params.py (parts, places, mates, dims), its build meta (model/out/*.meta.json:
the glb files, bytes, boxes), 02-cad `datums`, 00-CAR `parts` and `systems` through rx7.py.
Writes 02-APP/app/public/design/00-CAR/scene.json and, with drafts=DIR, DIR/model_parts.csv,
model_dims.csv, model_mates.csv and 00-CAR_parts_new.csv (exact columns; ids blank where the
record issues them, NEW:<slug> where a 00-CAR row does not exist yet). Never writes the record.
Exit 0 written / the scene holds; 1 it breaks the contract; 3 a crash.

scene.json, version 2 (the electrical Design page's contract plus the car's fields; only add):
  version, built, project "00-CAR", car true, frame {units, x, y, z, ruling, glb, rotation},
  systems [{id, name}], parts [{id, name, kind body|part|node, system, zone, glb, bytes, parent,
  place {x y z rx ry rz} (in the parent's frame), place_from, confirm, size_mm {x y z}, origin,
  made_from, state, mate {to, kind, fasteners, apart {x y z}} | null, children, source}],
  links [], legs [], missing [], notes []. Added fields: record (the 00-CAR parts id a part stands
  for; a pair's row carries -L / -R in the part's id), record_name, side, world (the place in the
  car's frame), nodes (the glb's node names), dims [{dim, value_mm, how, source}], assembly.
"""
import csv
import datetime
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frame  # noqa: E402
import placing  # noqa: E402

ROOT = frame.ROOT
ASSEMBLIES = ["corner", "unibody", "skin"]     # skin: built by skin/build.py from the found model, not FreeCAD
KINDS = ("body", "part", "node")
MATE_KINDS = ("welded", "bolted", "clipped", "pressed", "pivot", "sits-on", "fits-in", "slides")
TODAY = "2026-10-13"

MISSING = [
    {"what": "the FR, RL and RR corners from factory figures", "why": "the found model's wheels and tyres stand in (skin assembly); A04's FL corner is the factory-figure one"},
    {"what": "the closures as parts of their own: hood, front fenders, doors, the hatch panel, bumpers",
     "why": "the found model's skin stands in as one piece (PT704-skin, skin assembly); cutting it per panel is B01's next pass; the hatch panel and glass have no 00-CAR row yet"},
    {"what": "the knuckle, strut and suspension the hub turns on", "why": "not modelled yet: the hub is placed on DT02 directly"},
    {"what": "the hatch aperture as one ring", "why": "drawn as its pieces: PT773-rear (header), PT772-L/-R (gutters), PT775 (the rear end panel's top)"},
    {"what": "the rear upper link brackets as their own part", "why": "no 00-CAR row: drawn with PT780-L/-R, the rear side frames"},
]
NOTES = [
    "Nothing in this model is measured on the car (R11): every part is confirm, every number in model_dims says how it is known.",
    "place is in the parent's frame (the electrical contract); world is the same place in the car's frame. PT704, the shell, sits at the car's origin unturned, so a panel's place is its world.",
    "mate.apart is the move, in the car's frame (mm), of a part away from its mate.to when the car is taken apart; a chain adds them (a nut moves with its wheel, then off it).",
    "A 00-CAR row that covers a left-right pair is drawn as two parts, its id with -L / -R; record names the row.",
    "The overall length (DT04) and width (DT05) include bumpers and mouldings that are not in this pass: the nodes hp-front-end and hp-rear-end mark the length's ends.",
    "glb files are mm, z up, in the part's own frame; three.js strips ':' from node names - the written name is in userData.name.",
]


def _datums(rows):
    return {r["id"]: frame.Datum(r) for r in rows}


def _record(ids):
    ids = sorted({i for i in ids if i and not i.startswith("NEW:")})
    if not ids:
        return {}
    q = "select id, name, system, zone, parent from parts where id in (%s)" % ",".join("'%s'" % i for i in ids)
    return {r["id"]: r for r in frame.sql("00-CAR", q)}


def collect(rows):
    """[(assembly, params P, parts, meta)] for every assembly built."""
    dt = _datums(rows)
    out = []
    for asm in ASSEMBLIES:
        pm = importlib.import_module(asm + ".params")
        P = pm.params(dt)
        mp = os.path.join(HERE, "out", asm + ".meta.json")
        meta = json.load(open(mp)) if os.path.exists(mp) else None
        out.append((asm, P, pm.parts(P), meta))
    return out


def _xyz(v):
    return {"x": round(v[0], 2), "y": round(v[1], 2), "z": round(v[2], 2)}


def assemble(rows):
    got = collect(rows)
    allparts = [p for _, _, ps, _ in got for p in ps]
    rec = _record([p["record"] for p in allparts if p["record"]])
    systems = [{"id": r["id"], "name": r["name"]} for r in frame.sql("00-CAR", "select id, name from systems")]
    world = placing.world(allparts)
    parts, missing = [], list(MISSING)
    for asm, P, ps, meta in got:
        for p in ps:
            r = rec.get(p["record"] or "", {})
            m = (meta or {}).get("parts", {}).get(p["id"])
            if p["kind"] != "node" and not m:
                missing.append({"what": p["id"], "why": "the %s assembly is not built on this machine" % asm})
            w = world[p["id"]]
            rot = p["rot"]
            # the world turn: a top-level part's own; a child's is its parent's (filled below) -
            # the assemblies use only half turns about z, so the two compose by inheritance
            wr = list(rot) if not p.get("parent") else [0.0, 0.0, 0.0]
            mate = None
            if p["mate"]:
                mate = {"to": p["mate"]["to"], "kind": p["mate"]["kind"],
                        "fasteners": list(p["mate"]["fasteners"]), "apart": _xyz(p["mate"]["apart"])}
            size = None
            if m:
                lo, hi = m["bbox"]
                size = {"x": round(hi[0] - lo[0], 1), "y": round(hi[1] - lo[1], 1), "z": round(hi[2] - lo[2], 1)}
            parts.append({
                "id": p["id"], "name": p["name"], "kind": p["kind"],
                "system": p.get("system") or r.get("system") or "body",
                "zone": p.get("zone") or r.get("zone") or ("cabin" if p["kind"] == "body" else None),
                "glb": m["glb"] if m else None, "bytes": m["bytes"] if m else 0,
                "parent": p.get("parent"),
                "place": dict(_xyz(p["origin"]), rx=rot[0], ry=rot[1], rz=rot[2]),
                "world": dict(_xyz(w["origin"]), rx=wr[0], ry=wr[1], rz=wr[2]),
                "place_from": p["place_from"], "confirm": True, "size_mm": size,
                "origin": p["origin_note"], "made_from": p["made_from"], "state": "rough",
                "mate": mate, "children": [], "source": "02-PROJECTS/02-cad/model/%s (%s)" % (asm, p["source"]),
                "record": p["record"], "record_name": r.get("name") if r else None, "side": p.get("side"),
                "nodes": m["nodes"] if m else [], "assembly": asm,
                "dims": [{"dim": P[k].label or k, "value_mm": P[k].value, "how": P[k].how, "source": P[k].source}
                         for k in p["dims"]],
                "note": p.get("note") or "",
            })
    by = {p["id"]: p for p in parts}
    for p in parts:
        if p["parent"] in by:
            by[p["parent"]]["children"].append(p["id"])
    # the corner's world rotation: a child of a turned parent inherits its turn
    for p in parts:
        if p["parent"] in by and by[p["parent"]]["world"]["rz"]:
            p["world"]["rz"] = by[p["parent"]]["world"]["rz"]
    return {
        "version": 2, "built": datetime.datetime.now().replace(microsecond=0).isoformat(),
        "project": "00-CAR", "car": True,
        "frame": {"units": "mm", "x": "right", "y": "forward", "z": "up", "ruling": "D-418",
                  "glb": "mm, z up, the part's own frame", "rotation": "degrees, three.js Euler order XYZ"},
        "systems": systems, "parts": parts, "links": [], "legs": [], "missing": missing, "notes": NOTES,
    }, got, world


# ------------------------------------------------------------------------------- the drafts --
def write_drafts(d, got, world):
    os.makedirs(d, exist_ok=True)
    counts = {}
    allparts = {p["id"]: p for _, _, ps, _ in got for p in ps}
    by_record = {}
    for p in allparts.values():
        if p["kind"] != "node" and p["record"]:
            by_record.setdefault(p["record"], []).append(p["id"])

    def w(name, cols, rows):
        with open(os.path.join(d, name), "w", newline="", encoding="utf-8") as fh:
            wr = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
            wr.writeheader()
            for r in rows:
                wr.writerow({c: r.get(c, "") for c in cols})
        counts[name] = len(rows)

    head = open(os.path.join(ROOT, "00-CAR", "data", "parts.csv"), encoding="utf-8").readline().strip().split(",")
    new = [{"id": "PT976", "name": "Centre pillars (B-pillar and sail), R and L", "system": "body",
            "zone": "doors", "parent": "PT704", "qty": "2",
            "note": "unibody panel, modelled rough 2026-10-13 (D-518); confirm. No catalogue number found yet (S-005 body figures) - confirm"}]
    w("00-CAR_parts_new.csv", head, new)

    mp, md, mm = [], [], []
    for asm, P, ps, meta in got:
        for p in ps:
            if p["kind"] == "node":
                continue
            m = (meta or {}).get("parts", {}).get(p["id"], {})
            mp.append({"id": p["id"], "file": ("02-APP/app/public/design/00-CAR/" + m["glb"]) if m else "",
                       "made_from": p["made_from"], "source": p["source"], "state": "rough",
                       "parent": p["mate"]["to"] if p["mate"] else "",
                       "confirm": p["confirm_text"] or "every dimension",
                       "note": ("%s; STEP in model/out/%s.step. " % (p["name"], asm) if (meta or {}).get("step")
                                else "%s; mesh only, no STEP. " % p["name"]) + (p.get("note") or "")})
            if p["mate"]:
                a, b = world[p["id"]], world[p["mate"]["to"]]
                rel = [x - y for x, y in zip(a["origin"], b["origin"])]
                Rt = [[b["R"][j][i] for j in range(3)] for i in range(3)]
                off = placing.apply(Rt, rel)
                mm.append({"id": "", "part": p["id"], "to": p["mate"]["to"], "kind": p["mate"]["kind"],
                           "fasteners": " ".join(p["mate"]["fasteners"]),
                           "offset_mm": "%.1f %.1f %.1f" % tuple(round(c, 1) + 0.0 for c in off) + "; confirm",
                           "note": (p["mate"].get("offset") or "") + (" apart %g %g %g (car frame)" % tuple(p["mate"]["apart"]))})
        for k, dim in P.items():
            targets = []
            for rid in dim.parts:
                if rid == "PT704":
                    targets.append("PT778" if asm == "unibody" else None)
                else:
                    targets += by_record.get(rid, [])
            seen = set()
            for t in targets:
                if not t or t in seen:
                    continue
                seen.add(t)
                md.append({"id": "", "part": t, "dim": dim.label or k, "value_mm": dim.value, "how": dim.how,
                           "source": dim.source, "date": "",
                           "note": ("params %s/%s. " % (asm, k)) + (dim.note or "") +
                                   (" Governs the whole shell." if "PT704" in dim.parts and t == "PT778" else "")})
    w("model_parts.csv", ["id", "file", "made_from", "source", "state", "parent", "confirm", "note"], mp)
    w("model_dims.csv", ["id", "part", "dim", "value_mm", "how", "source", "date", "note"], md)
    w("model_mates.csv", ["id", "part", "to", "kind", "fasteners", "offset_mm", "note"], mm)
    return counts


def write_scene(app_dir, out_dir, rows, drafts=None):
    try:
        scene, got, world = assemble(rows)
    except Exception as e:                                   # a crash in a params module
        import traceback
        traceback.print_exc()
        print("scene: %s" % e, file=sys.stderr)
        return 3
    os.makedirs(app_dir, exist_ok=True)
    path = os.path.join(app_dir, "scene.json")
    tmp = path + ".part"
    with open(tmp, "w") as fh:
        json.dump(scene, fh, indent=1)
    os.replace(tmp, path)
    print("scene.json: %d parts (%d body, %d part, %d node), %.0f KB" % (
        len(scene["parts"]), sum(p["kind"] == "body" for p in scene["parts"]),
        sum(p["kind"] == "part" for p in scene["parts"]), sum(p["kind"] == "node" for p in scene["parts"]),
        os.path.getsize(path) / 1e3))
    if drafts:
        for k, v in write_drafts(drafts, got, world).items():
            print("draft %s: %d rows" % (k, v))
    return 0


# ------------------------------------------------------------------------------- the selftest --
def selftest(path):
    from partlib import G
    problems = []
    if not os.path.exists(path):
        print("no scene at %s" % path, file=sys.stderr)
        return 1
    s = json.load(open(path))
    for k in ("version", "built", "project", "car", "frame", "systems", "parts", "links", "legs", "missing", "notes"):
        if k not in s:
            problems.append("scene has no %s" % k)
    if s.get("version") != 2 or s.get("project") != "00-CAR" or s.get("car") is not True:
        problems.append("version / project / car")
    sysids = {x["id"] for x in s.get("systems", [])}
    ids = [p["id"] for p in s["parts"]]
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids: %s" % sorted({i for i in ids if ids.count(i) > 1}))
    by = {p["id"]: p for p in s["parts"]}
    base = os.path.dirname(path)
    for p in s["parts"]:
        pid = p["id"]
        if p["kind"] not in KINDS:
            problems.append("%s: kind %s" % (pid, p["kind"]))
        if p.get("parent") and p["parent"] not in by:
            problems.append("%s: parent %s resolves to nothing" % (pid, p["parent"]))
        for c in p.get("children", []):
            if c not in by or by[c].get("parent") != pid:
                problems.append("%s: child %s does not name it" % (pid, c))
        pl = p.get("place") or {}
        if not all(isinstance(pl.get(k), (int, float)) for k in ("x", "y", "z", "rx", "ry", "rz")):
            problems.append("%s: place incomplete" % pid)
        m = p.get("mate")
        if m:
            if m.get("to") not in by:
                problems.append("%s: mate to %s resolves to nothing" % (pid, m.get("to")))
            if m.get("kind") not in MATE_KINDS:
                problems.append("%s: mate kind %s" % (pid, m.get("kind")))
            if not all(isinstance(m.get("apart", {}).get(k), (int, float)) for k in "xyz"):
                problems.append("%s: mate.apart incomplete" % pid)
        if p["kind"] == "node":
            if p.get("glb"):
                problems.append("%s: a node with a glb" % pid)
            continue
        if not p.get("system") or p["system"] not in sysids:
            problems.append("%s: system %s is not a 00-CAR system" % (pid, p.get("system")))
        if not p.get("zone"):
            problems.append("%s: no zone" % pid)
        g = p.get("glb")
        f = os.path.join(base, g) if g else None
        if not f or not os.path.exists(f):
            problems.append("%s: glb %s missing" % (pid, g))
        elif os.path.getsize(f) != p.get("bytes"):
            problems.append("%s: glb is %d bytes, the scene says %s" % (pid, os.path.getsize(f), p.get("bytes")))
    # the envelope: the shell on the datums
    wb = {}
    for p in s["parts"]:
        if p["kind"] == "node" or not p.get("glb") or not os.path.exists(os.path.join(base, p["glb"])):
            continue
        lo, hi = G.glb_bbox(os.path.join(base, p["glb"]))
        w = p["world"]
        if w["rz"] in (180, -180):
            lo, hi = [-hi[0], -hi[1], lo[2]], [-lo[0], -lo[1], hi[2]]
        wb[p["id"]] = ([lo[k] + w[a] for k, a in enumerate("xyz")], [hi[k] + w[a] for k, a in enumerate("xyz")])
    body = [v for k, v in wb.items() if by[k]["kind"] == "body"]
    env = None
    if body:
        env = ([min(b[0][k] for b in body) for k in range(3)], [max(b[1][k] for b in body) for k in range(3)])
        if abs(env[1][2] - 1259.8) > 1.0:
            problems.append("roof top %.1f is not DT06 1259.8" % env[1][2])
        if abs(env[1][0] - 834.4) > 1.0 or abs(env[0][0] + 834.4) > 1.0:
            problems.append("shell half-width %.1f / %.1f is not DT05 834.4" % (env[0][0], env[1][0]))
        if env[0][2] < 144.8:
            problems.append("the shell's lowest point %.1f is below DT07 144.8" % env[0][2])
        fe, re_ = by.get("hp-front-end"), by.get("hp-rear-end")
        if fe and re_ and abs(fe["world"]["y"] - re_["world"]["y"] - 4320.5) > 0.6:
            problems.append("hp-front-end to hp-rear-end is not DT04 4320.5")
    w = by.get("PT525-FL")
    if w and (abs(w["world"]["x"] + 710) > 0.01 or abs(w["world"]["y"]) > 0.01 or abs(w["world"]["z"] - 294.5) > 0.01):
        problems.append("the front-left wheel is not on DT02")
    r3 = [by.get("hp-DT03-L"), by.get("hp-DT03-R")]
    if all(r3) and any(abs(p["world"]["y"] + 2420) > 0.01 for p in r3):
        problems.append("the rear wheel centres are not on DT03")
    for p in problems:
        print("selftest: " + p, file=sys.stderr)
    if env:
        print("envelope of the shell: x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f" % (
            env[0][0], env[1][0], env[0][1], env[1][1], env[0][2], env[1][2]))
    print("selftest: %d parts, %d problems" % (len(s["parts"]), len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--selftest"]
    if "--selftest" in sys.argv:
        sys.exit(selftest(args[0] if args else os.path.join(ROOT, "02-APP", "app", "public", "design", "00-CAR", "scene.json")))
    print(__doc__)
    sys.exit(3)

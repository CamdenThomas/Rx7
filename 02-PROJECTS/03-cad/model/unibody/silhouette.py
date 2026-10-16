#!/usr/bin/env python3
"""unibody/silhouette.py - re-derive the found shell's stations that params.py cites (03-cad B01).

    python3 02-PROJECTS/03-cad/model/unibody/silhouette.py [--length]

Reads 00-CAR cad fb-rx7-gsl-se-85-3dwarehouse-blastronaut's glb from the model library
(read only), finds its four wheel centres, scales it to the factory wheelbase (DT03; --length: to
DT04 instead), puts its front axle at y 0 and lifts its body to put the roof on DT06, then prints
per 100 mm station: the body's half-width, its top near the centreline, its lowest point and the
glass's half-width and lowest point. params.py's `found` figures are read off this table; nothing
is written. Exit 0; 2 the library file is not on this machine.
"""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from partlib import G  # noqa: E402  (02-electrical's export_glb: read_glb, _walk, _accessor)

sys.path.insert(0, os.path.join(os.path.dirname(HERE), "found"))
from paths import LIBRARY  # noqa: E402  (the library's folder, named once: found/paths.py)

GLB = os.path.join(LIBRARY, "body",
                   "fb-rx7-gsl-se-85-3dwarehouse-blastronaut", "Mazda RX-7 fb Tuner (Copper).glb")
WHEEL = (15, 17, 21)                     # the tuner wheels' materials
BODY = (0, 1, 2, 3, 4, 5, 7, 11, 13)     # paint, trim, glass
GLASS = (13,)


def main():
    if not os.path.exists(GLB):
        print("not on this machine: %s" % GLB, file=sys.stderr)
        return 2
    js, bin_ = G.read_glb(GLB)
    by = collections.defaultdict(list)

    def visit(i, m, top):
        n = js["nodes"][i]
        if "mesh" not in n:
            return
        for p in js["meshes"][n["mesh"]]["primitives"]:
            a = G._accessor(js, bin_, p["attributes"]["POSITION"])
            for k in range(0, len(a), 3):
                x, y, z = a[k], a[k + 1], a[k + 2]
                by[p.get("material")].append([m[r][0] * x + m[r][1] * y + m[r][2] * z + m[r][3] for r in range(3)])
    G._walk(js, visit)
    wheel = [q for k in WHEEL for q in by[k]]
    xm = sum(q[0] for q in wheel) / len(wheel)
    zm = sum(q[2] for q in wheel) / len(wheel)
    cl = collections.defaultdict(list)
    for q in wheel:
        cl[(q[0] > xm, q[2] > zm)].append(q)
    cen = {k: [(min(q[i] for q in v) + max(q[i] for q in v)) / 2 for i in range(3)] for k, v in cl.items()}
    zf = (cen[(False, True)][2] + cen[(True, True)][2]) / 2
    zr = (cen[(False, False)][2] + cen[(True, False)][2]) / 2
    xc = sum(c[0] for c in cen.values()) / 4
    body = [q for k in BODY for q in by[k]]
    if "--length" in sys.argv:
        s = 4320.5 / ((max(q[2] for q in body) - min(q[2] for q in body)) * 1000)
    else:
        s = 2420.0 / ((zf - zr) * 1000)
    top = max(q[1] for q in body) * 1000 * s
    lift = 1259.8 - top

    def car(q):
        return (-(q[0] - xc) * 1000 * s, (q[2] - zf) * 1000 * s, q[1] * 1000 * s + lift)
    B = [car(q) for q in body]
    Gl = [car(q) for k in GLASS for q in by[k]]
    print("scale %.4f, wheelbase %.1f, lift %.1f mm, body y %.0f..%.0f" % (
        s, (zf - zr) * 1000 * s, lift, min(p[1] for p in B), max(p[1] for p in B)))
    print("    y  half-w  top(|x|<250)  lowest  glass half-w  glass lowest")
    for y in range(1000, -3500, -100):
        b = [p for p in B if abs(p[1] - y) <= 50]
        g = [p for p in Gl if abs(p[1] - y) <= 50]
        if not b:
            continue
        c = [p[2] for p in b if abs(p[0]) < 250]
        print("%5d %7.0f %13s %7.0f %13s %13s" % (
            y, max(abs(p[0]) for p in b), "%.0f" % max(c) if c else "-", min(p[2] for p in b),
            "%.0f" % max(abs(p[0]) for p in g) if g else "-", "%.0f" % min(p[2] for p in g) if g else "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

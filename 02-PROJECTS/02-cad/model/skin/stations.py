"""skin/stations.py - the found FB model's stations (the app's home-page car, 02-PROJECTS/02-cad/model/sa/rx7-fb.glb),
in the car's frame, for unibody/params.py's `found` figures (B01, 2026-10-13).

    python3 02-PROJECTS/02-cad/model/skin/stations.py

The model is already at factory size (skin/params.py says why), so it is only turned into the car's
frame - no scaling, no lift. Per 50 mm station: the body's half-width, its top near the centreline
(|x| < 250), its top at the roof's edge (|x| 600-700), its lowest point, the glass's half-width, its
lowest and highest point near the centreline. Then the points params.py names. Read only.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import glbread  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(ROOT, "02-PROJECTS", "02-cad", "model", "sa", "rx7-fb.glb")


def slice_y(tris, y0):
    """Points where the triangles cross the plane y = y0: the section's outline."""
    out = []
    for a, b, c in tris:
        for p, q in ((a, b), (b, c), (c, a)):
            if (p[1] - y0) * (q[1] - y0) < 0:
                t = (y0 - p[1]) / (q[1] - p[1])
                out.append((p[0] + t * (q[0] - p[0]), y0, p[2] + t * (q[2] - p[2])))
    return out


def tris_of(meshes, want):
    T = []
    for m in meshes:
        if not want(m):
            continue
        P = [(10 * p[0], -10 * p[2] - 1210.0, 10 * p[1]) for p in m["positions"]]
        T += [(P[i], P[j], P[k]) for i, j, k in m["triangles"]]
    return T


def main():
    meshes = glbread.read(SRC)
    body = tris_of(meshes, lambda m: m["material"] == "carpaint")
    glass = tris_of(meshes, lambda m: m["material"] == "glass")
    f = lambda v: "%.0f" % v if v is not None else "-"
    print("     y  half-w  top|x|<200  top@x600-700  lowest  glass-hw  glass-low(c)  glass-top(c)")
    for y in range(950, -3450, -50):
        b, g = slice_y(body, y), slice_y(glass, y)
        if not b:
            continue
        c = [p[2] for p in b if abs(p[0]) < 200]
        e = [p[2] for p in b if 600 <= abs(p[0]) <= 700]
        gc = [p[2] for p in g if abs(p[0]) < 200]
        print("%6d %7.0f %11s %13s %7.0f %9s %13s %13s" % (
            y, max(abs(p[0]) for p in b), f(max(c) if c else None), f(max(e) if e else None), min(p[2] for p in b),
            f(max(abs(p[0]) for p in g) if g else None), f(min(gc) if gc else None), f(max(gc) if gc else None)))


if __name__ == "__main__":
    main()

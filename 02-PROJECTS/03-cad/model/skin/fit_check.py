"""skin/fit_check.py - which unibody panels stand outside the found FB skin, and by how much (B01).

For every part of the unibody assembly, its box in the car's frame (scene.json's world place and
size) is held to the skin: the skin's highest point over the box's footprint and its widest point
over the box's length and height. A panel whose box rises above the roof line over it, or reaches
past the skin's side, is printed with the overshoot in mm. Read only; it prints, it writes nothing.
Owns no fact about the car (R11): both sides of the comparison are models.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import glbread  # noqa: E402
import params as SP  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCENE = os.path.join(ROOT, "02-APP", "app", "public", "design", "00-CAR", "scene.json")
SRC = os.path.join(ROOT, "02-PROJECTS", "03-cad", "model", "sa", "rx7-fb.glb")
STEP = 25.0


def main():
    s = json.load(open(SCENE))
    P = SP.params({"DT02": _D(710, 0, 294.5), "DT03": _D(699.8, -2420, 294.5)})
    top, side = {}, {}
    for m in glbread.read(SRC):
        if m["material"] not in ("carpaint", "glass") and not m["material"].startswith("surface_11"):
            continue
        for p in m["positions"]:
            x, y, z = 10 * p[0], -10 * p[2] + P.v("y_shift"), 10 * p[1]
            k = (int(x // STEP), int(y // STEP))
            top[k] = max(top.get(k, -1e9), z)
            k2 = (int(y // STEP), int(z // STEP))
            side[k2] = max(side.get(k2, 0.0), abs(x))
    meta = json.load(open(os.path.join(HERE, "..", "out", "unibody.meta.json")))["parts"]
    rows = []
    for p in s["parts"]:
        if p.get("assembly") != "unibody" or p["kind"] == "node" or p["id"] not in meta:
            continue
        w = p["world"]
        assert not (w["rx"] or w["ry"]) and w["rz"] in (0, 0.0, 180, 180.0), p["id"]
        (lx, ly, lz), (hx, hy, hz) = meta[p["id"]]["bbox"]
        if w["rz"] in (180, 180.0):
            lx, hx, ly, hy = -hx, -lx, -hy, -ly
        x0, x1, y0, y1, z0, z1 = w["x"] + lx, w["x"] + hx, w["y"] + ly, w["y"] + hy, w["z"] + lz, w["z"] + hz
        xs = range(int(x0 // STEP), int(x1 // STEP) + 1)
        ys = range(int(y0 // STEP), int(y1 // STEP) + 1)
        zs = range(int(z0 // STEP), int(z1 // STEP) + 1)
        roof = max((top.get((i, j), -1e9) for i in xs for j in ys), default=-1e9)
        wide = max((side.get((j, k), 0.0) for j in ys for k in zs), default=0.0)
        up = z1 - roof if roof > -1e8 else 0
        out = max(abs(x0), abs(x1)) - wide if wide else 0
        if up > 15 or out > 15:
            rows.append((max(up, out), p["id"], p["name"][:46], round(up), round(out)))
    for r in sorted(rows, reverse=True):
        print("%-12s %-46s above the skin %5s mm, outside it %5s mm" % r[1:])
    print("%d panels stand out by more than 15 mm" % len(rows))


class _D:
    def __init__(self, x, y, z):
        self.v = {"x_mm": x, "y_mm": y, "z_mm": z}

    def num(self, k):
        return self.v[k]


if __name__ == "__main__":
    main()

"""placing.py - where each part sits: its place in its parent's frame composed to the car's (pure).

world(parts) -> {id: {"origin": [x y z] car frame, "R": 3x3}} for every part, its parent's place
applied first (a child's `origin` and `rot` are in its parent's frame, as the scene contract says).
rot is degrees, three.js Euler order XYZ (R = Rx . Ry . Rz). to_car(shape, w) moves a FreeCAD shape
from the part's own frame into the car's (for the STEP). file_name(id) is the glb's name.
"""
import math
import re


def _rx(a):
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def _ry(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def _rz(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def apply(R, v):
    return [sum(R[i][k] * v[k] for k in range(3)) for i in range(3)]


def euler(rot):
    rx, ry, rz = (math.radians(a) for a in rot)
    return mul(mul(_rx(rx), _ry(ry)), _rz(rz))


def world(parts):
    by = {p["id"]: p for p in parts}
    out = {}

    def get(pid):
        if pid in out:
            return out[pid]
        p = by[pid]
        R = euler(p["rot"])
        o = list(p["origin"])
        par = p.get("parent")
        if par and par in by:
            w = get(par)
            o = [a + b for a, b in zip(w["origin"], apply(w["R"], o))]
            R = mul(w["R"], R)
        out[pid] = {"origin": [round(c, 4) for c in o], "R": R}
        return out[pid]

    for p in parts:
        get(p["id"])
    return out


def to_car(shape, w):
    import FreeCAD
    R, o = w["R"], w["origin"]
    m = FreeCAD.Matrix(R[0][0], R[0][1], R[0][2], o[0],
                       R[1][0], R[1][1], R[1][2], o[1],
                       R[2][0], R[2][1], R[2][2], o[2],
                       0, 0, 0, 1)
    s = shape.copy()
    s.transformShape(m)
    return s


def file_name(pid):
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", pid).strip("-") + ".glb"

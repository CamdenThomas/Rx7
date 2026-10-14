"""glbread.py - a small pure-python reader for the found models' glb files (05-cad B01): every mesh's
triangles with its node's name and its material's name, in the file's own frame. Reads only what
Blender's exporter writes (float positions and normals, unsigned indices, node TRS); refuses
anything else. Owns no fact about the car."""
import json
import math
import struct
from array import array

CT = {5121: "B", 5123: "H", 5125: "I", 5126: "f"}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def _mat4(node):
    if "matrix" in node:
        m = node["matrix"]
        return [m[0:4], m[4:8], m[8:12], m[12:16]]          # column-major columns
    t = node.get("translation", [0, 0, 0])
    r = node.get("rotation", [0, 0, 0, 1])
    s = node.get("scale", [1, 1, 1])
    x, y, z, w = r
    R = [[1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w)],
         [2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w)],
         [2 * (x * z + y * w), 2 * (y * z - x * w), 1 - 2 * (x * x + y * y)]]
    return [[R[0][0] * s[0], R[0][1] * s[0], R[0][2] * s[0], 0],
            [R[1][0] * s[1], R[1][1] * s[1], R[1][2] * s[1], 0],
            [R[2][0] * s[2], R[2][1] * s[2], R[2][2] * s[2], 0],
            [t[0], t[1], t[2], 1]]


def _mul(a, b):            # column-major: (a * b)
    return [[sum(a[k][r] * b[c][k] for k in range(4)) for r in range(4)] for c in range(4)]


def _apply(m, p):
    x, y, z = p
    return (m[0][0] * x + m[1][0] * y + m[2][0] * z + m[3][0],
            m[0][1] * x + m[1][1] * y + m[2][1] * z + m[3][1],
            m[0][2] * x + m[1][2] * y + m[2][2] * z + m[3][2])


def read(path):
    """[{"node", "material", "positions" [(x, y, z)], "triangles" [(i, j, k)]}] in the file's frame
    (node transforms applied)."""
    data = open(path, "rb").read()
    assert data[:4] == b"glTF", path
    jlen = struct.unpack("<I", data[12:16])[0]
    j = json.loads(data[20:20 + jlen])
    assert not j.get("extensionsRequired"), j.get("extensionsRequired")
    boff = 20 + jlen
    blen, btype = struct.unpack("<II", data[boff:boff + 8])
    assert btype == 0x004E4942
    bin_ = data[boff + 8:boff + 8 + blen]

    def acc(i):
        a = j["accessors"][i]
        v = j["bufferViews"][a["bufferView"]]
        code = CT[a["componentType"]]
        n = NC[a["type"]]
        size = struct.calcsize(code)
        stride = v.get("byteStride", size * n)
        start = v.get("byteOffset", 0) + a.get("byteOffset", 0)
        out = []
        for k in range(a["count"]):
            o = start + k * stride
            out.append(struct.unpack_from("<%d%s" % (n, code), bin_, o))
        return out

    mats = [m.get("name", "") for m in j.get("materials", [])]
    result = []

    def walk(ni, parent):
        node = j["nodes"][ni]
        m = _mul(parent, _mat4(node))
        if "mesh" in node:
            for prim in j["meshes"][node["mesh"]]["primitives"]:
                assert prim.get("mode", 4) == 4
                pos = [_apply(m, p) for p in acc(prim["attributes"]["POSITION"])]
                idx = [i[0] for i in acc(prim["indices"])] if "indices" in prim else list(range(len(pos)))
                tris = [tuple(idx[k:k + 3]) for k in range(0, len(idx), 3)]
                result.append({"node": node.get("name", "node%d" % ni),
                               "material": mats[prim["material"]] if "material" in prim else "",
                               "positions": pos, "triangles": tris})
        for c in node.get("children", []):
            walk(c, m)

    ident = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    for scene in j["scenes"]:
        for ni in scene["nodes"]:
            walk(ni, ident)
    return result


def bbox(pos):
    xs, ys, zs = [p[0] for p in pos], [p[1] for p in pos], [p[2] for p in pos]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


if __name__ == "__main__":
    import sys
    for m in read(sys.argv[1]):
        lo, hi = bbox(m["positions"])
        print("%-18s %-11s %6d tris  x %8.1f..%8.1f  y %8.1f..%8.1f  z %8.1f..%8.1f" % (
            m["node"], m["material"], len(m["triangles"]), lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))

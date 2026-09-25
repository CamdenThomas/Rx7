"""Rough harness route lengths from the 3D body (D-416). Owns `routes.model_ft` in
02-PROJECTS/00-electrical; never touches `routes.ft`, which is measured on the car.

    python3 01-REFERENCE/model/estimate.py            print the estimates
    python3 01-REFERENCE/model/estimate.py --write    also set routes.model_ft through rx7.py

Reads 01-REFERENCE/model/landmarks.json (build.py writes it; out of git). Millimetres; x to
the car's right, y toward the front, z up, ground z = 0. The car's centreline is x = 47.

Every length is taxicab (along x, then y, then z) between points, because a harness follows
panels, not straight lines, and is then multiplied by SLACK for bends and the tie-down path.
The body is a 1978 artist's model and the node positions below are ASSUMED: nothing in the
record places a node yet. So each estimate is a planning figure, never a cut length.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
AREA = "02-PROJECTS/00-electrical"
SLACK = 1.15
CL = 47.0

L = json.load(open(os.path.join(HERE, "landmarks.json")))


def at(name):
    return tuple(L[name]["centre"])


# Nodes: assumed positions. Change one here and every route through it follows.
NODE = {
    "dash post": (CL, 450, 650),          # behind the dash, on the centreline, at the firewall
    "cowl grommet": (CL + 600, 600, 880),  # passenger end of the cowl, at the windscreen base
    "nose splice": (CL, 1650, 500),       # radiator support, centre
    "rear node": (CL, -900, 550),         # cargo bin behind the seats, floor level
    "sill node": (-650, 450, 350),        # driver kick panel (left-hand drive: x negative)
    "hinge loop": (CL, -1052, 1180),      # hatch hinges (pCube15/pCube75), under the roof edge
}

# Endpoints from the model's own parts (see landmarks.json), each named for what it is.
END = {
    "headlamp bucket, far side": at("polysurface09"),
    "front combo lamp, far side": at("polysurface17"),
    "front side marker, far side": at("polysurface15"),
    "tail lamp, far side": at("polysurface01"),
    "licence lamp, far side": at("pcube13"),
    "hatch lower edge": (CL, -1964, 800),
    "passenger door jamb": (CL + 800, 450, 650),
    "driver door jamb": (-750, 450, 650),
}


def taxi(*pts):
    return sum(sum(abs(a - b) for a, b in zip(p, q)) for p, q in zip(pts, pts[1:]))


# route id -> (path through points, what the longest branch is)
ROUTES = {
    "RT06": (["dash post", "cowl grommet", (CL + 600, 1650, 600), "nose splice"], "dash post, cowl, inner wing, nose"),
    "RT07": (["nose splice", "headlamp bucket, far side"], "the far headlamp bucket"),
    "RT08": (["nose splice", "front combo lamp, far side", "front side marker, far side"], "the far combo lamp, on to its side marker"),
    "RT15": (["dash post", (CL, 450, 250), (CL, -900, 250), "rear node"], "down the tunnel to the cargo bin"),
    "RT16": (["rear node", (CL + 700, -900, 550), "tail lamp, far side", "licence lamp, far side"], "along the quarter to the far tail lamp and the licence lamp"),
    "RT18": (["rear node", (CL, -1052, 900), "hinge loop", "hatch lower edge"], "up to the hinge loop and down the hatch"),
    "RT19": (["dash post", "sill node"], "the driver kick panel"),
    "RT20": (["sill node", (CL, 450, 250), "passenger door jamb"], "the far door, across the floor"),
}


def point(p):
    return NODE.get(p) or END.get(p) or p


def main():
    out = {}
    for rid, (path, what) in ROUTES.items():
        mm = taxi(*[point(p) for p in path]) * SLACK
        out[rid] = round(mm / 304.8, 1)
        print(f"{rid}  {out[rid]:5.1f} ft  {what}")
    if "--write" in sys.argv:
        for rid, ft in out.items():
            subprocess.run([sys.executable, "tools/rx7.py", "set", AREA, "routes", rid, f"model_ft={ft}"], cwd=ROOT, check=True)


main()

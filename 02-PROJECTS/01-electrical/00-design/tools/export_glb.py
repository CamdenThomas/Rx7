"""The electrical design in 3D for the app (02-APP D-505, work row Y23). One command, from the
tree's root:

    python3 02-PROJECTS/01-electrical/00-design/tools/export_glb.py [--out DIR] [--only NAME]
    python3 02-PROJECTS/01-electrical/00-design/tools/export_glb.py --check
    python3 02-PROJECTS/01-electrical/00-design/tools/export_glb.py --selftest [SCENE]

It writes, into DIR (default 02-APP/app/public/design/01-electrical):

  <board>.glb       each KiCad board with its parts' 3D models, tracks, pads, zones, silkscreen
                    and soldermask (kicad-cli pcb export glb), re-packed (see below)
  control-unit.glb  the Control Unit's case and the insides no board stands for, from the
  display-unit.glb  FreeCAD mock-ups (export_glb_fc.py imports their own tools/<assembly>.py, so nothing
                    is drawn twice), one named node per solid: case:<name>, inside:<name>
  pmu.glb           ECUMaster's PMU-24 STEP from pmu/vendor, with its own face colours
  connectors/       one glb per Deutsch variant and manifest.json, by tools/harness_connectors.py
                    (Y24), run here as a step
  devices/          the far ends' devices and common parts and manifest.json, by
                    tools/harness_devices.py (Y28), run here as a step
  scene.json        every part, its place, its connectors, one labelled link per housing; at
                    version 2 (D-514, Y26) both halves of every housing, the devices at their
                    nodes and the legs as paths (the contract is in 00-design/README.md §13)

--only takes an asset, `connectors`, `devices`, or `legs` / `scene` (the scene alone, from the
record and what is built).

Every glb is in the part's own frame, in millimetres, z up - NOT glTF's metres and y up - so a
viewer working in the car's frame (D-418) puts the file under a node at `place` and nothing else.
The geometry is re-packed: one node per named group, one primitive per material (chunks of at
most 65535 vertices, 16-bit indices), float positions and 8-bit normals (KHR_mesh_quantization,
which three.js reads natively).

Reads the record only through `rx7.py export` (00-CAR zones and parts, 01-electrical housings,
cavities, routes, devices, modules and parts) and writes nothing to it. The harness is drawn as
it will be built (D-583): TRUNKS, SPOTS and the breakouts are judgement, every point confirm. Owns no fact: a top-level part whose row
(UNITS, PMU) has a `place` - his Save place on the Design page, 01-electrical parts.place or
modules.place (D-520, Y29) - is put there, `place_from: 01-electrical <table> <id>`; every place
it cannot find in a row is `place_from: provisional`; all stay `confirm: true` until measured.
The far ends' and the units' provisional spots are judgement, one line each in WHERE and TOP.

Exit 0 built (or, with --check, current) - 1 a source is inconsistent (a board the scene names
has no glb, a mock-up refuses its parameters, a scene that breaks the contract, a stale asset
under --check) - 2 with --check, assets missing (not built on this machine) - 3 a usage error or
a tool crash.
"""
import argparse
import array
import datetime
import hashlib
import json
import math
import os
import re
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(HERE)                                   # 00-design
ROOT = os.path.abspath(os.path.join(DESIGN, "..", "..", ".."))  # the tree
sys.path.insert(0, HERE)
import parts as layout  # noqa: E402  (where every board, assembly and extract lives)
OUT_DEFAULT = os.path.join(ROOT, "02-APP", "app", "public", "design", "01-electrical")
KICAD_CLI = os.environ.get("KICAD_CLI", "/opt/homebrew/bin/kicad-cli")
FREECADCMD = os.environ.get("FREECADCMD",
                            "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd")
KICAD_MODELS = os.environ.get("KICAD10_3DMODEL_DIR",
                              "/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels")
RX7_MODELS = os.path.join(ROOT, "02-PROJECTS", "02-cad", "model", "library", "electrical")
PMU_STEP = os.path.join(DESIGN, "pmu", "vendor", "PMU CAD info", "PMU-24.STEP")

# The PMU sets the standard (D-505): fine enough that every radius reads round.
PMU_LINEAR, PMU_ANGULAR = 0.03, 0.15          # mm, radians
UNIT_LINEAR, UNIT_ANGULAR = 0.05, 0.2

KICAD_FLAGS = ["--subst-models", "--include-tracks", "--include-pads", "--include-zones",
               "--include-silkscreen", "--include-soldermask"]

# ---------------------------------------------------------------------------------- the design --
# Each board: its KiCad project and the record row that names it (01-electrical parts / modules).
BOARDS = {
    "cu-carrier": ("control-unit/cad/cu-carrier/cu-carrier.kicad_pcb", "parts", "P144"),
    "cu-face-board": ("control-unit/cad/cu-face-board/cu-face-board.kicad_pcb", "modules", "PANEL"),
    "cur-board": ("control-unit/control-unit-remote/cad/cur-board/cur-board.kicad_pcb", "parts", "P198"),
    "du-carrier": ("display-unit/cad/du-carrier/du-carrier.kicad_pcb", "parts", "P103"),
}
# What a board's glb leaves out, and why: the record has moved past the board as drawn.
BOARD_HIDE = {
    "cu-carrier": {"refs": ("J1", "J2", "J9"),
                    "why": "D-582: the three DT13s give way to the Control Unit's one CMC 48 "
                           "header, which the unit's mock-up draws; the board is redrawn at Y54"},
}
# Each unit: its mock-up, the record row that names it, and which of the mock-up's inside solids
# a child board's glb stands for (those are left out of the unit's glb, so nothing is drawn twice).
UNITS = {
    "control-unit": {"assembly": "cu-assembly", "row": ("modules", "DCU"),
                     "housing": "P152",
                     "children": {"cu-carrier": {"kinds": ["carrier"]},
                                  "cu-face-board": {"names": ["panel board", "panel ribbon header"]}}},
    "display-unit": {"assembly": "du-assembly", "row": ("modules", "ICU"),
                     "housing": "P111",
                     "children": {"du-carrier": {"kinds": ["carrier"]}}},
    # the left plate made a unit (D-514, Y25): the plate board is its child, placed from the
    # mock-up's export_boards(); no record row names the CUR yet, so its name is given here
    "cur": {"assembly": "cur-assembly", "row": ("parts", "P198"),
            "name": "Control Unit Remote (CUR)",
            "children": {"cur-board": {"kinds": ["plate"]}},
            "sources": ["tools/cu_assembly.py",
                        "control-unit/control-unit-remote/cad/cur-board/cur-board.kicad_pcb",
                        "control-unit/data/cu-carrier-board.json",
                        "control-unit/data/cu-carrier-probe.json"]},
}
PMU = {"id": "pmu", "row": ("modules", "PMU")}
ASSETS = list(BOARDS) + list(UNITS) + ["pmu"]

# Where a housing's far end is when the record names a place, not a modelled part. Judgement,
# one line each: (node id, the 00-CAR zone, fx fy fz as fractions across that zone's first box).
# The zone box is the record's (zones.model_box_mm); the fractions are not, so every node made
# from this table is provisional and confirm.
WHERE = {
    "L1 Engine": ("leg-l1", "engine_bay", (0.5, 0.5, 0.5), "L1 Engine - the leg's far end"),
    "L2 Front": ("leg-l2", "front", (0.5, 0.5, 0.5), "L2 Front - the leg's far end"),
    "L3 Dash": ("leg-l3", "dash", (0.35, 0.45, 0.45), "L3 Dash - the leg's devices"),
    "L4 Rear": ("leg-l4", "cargo", (0.5, 0.5, 0.3), "L4 Rear - the leg's far end"),
    "HVAC case": ("hvac-case", "dash", (0.62, 0.75, 0.4), "HVAC case"),
    "Sill node": ("sill-node", "cabin", (0.05, 0.95, 0.15), "Sill node (driver kick panel)"),
    "Glovebox": ("glovebox", "dash", (0.75, 0.2, 0.35), "Glovebox"),
    "Nose": ("nose", "front", (0.5, 0.8, 0.45), "Nose"),
    "Nose, behind the front bumper": ("nose-bumper", "front", (0.5, 0.95, 0.35),
                                      "Nose, behind the front bumper"),
    "Centre stack": ("centre-stack", "dash", (0.5, 0.3, 0.2), "Centre stack, behind it"),
    "Behind the dash": ("behind-dash", "dash", (0.45, 0.6, 0.55), "Behind the dash"),
    "Rear node": ("rear-node", "cargo", (0.5, 0.6, 0.2), "Rear node"),
    "Under the driver's seat": ("seat-driver", "cabin", (0.3, 0.5, 0.08),
                                "Under the driver's seat"),
    "Under the passenger seat": ("seat-passenger", "cabin", (0.7, 0.5, 0.08),
                                 "Under the passenger seat"),
    "Hatch, behind the trim": ("hatch", "cargo", (0.5, 0.15, 0.9), "Hatch, behind the trim"),
    "Driver kick panel": ("kick-driver", "cabin", (0.05, 0.97, 0.12), "Driver kick panel"),
    "Passenger kick panel": ("kick-passenger", "cabin", (0.95, 0.97, 0.12),
                             "Passenger kick panel"),
    "Driver A-pillar base / sail panel": ("pillar-driver", "dash", (0.03, 0.15, 0.95),
                                          "Driver A-pillar base"),
    "Passenger A-pillar base / sail panel": ("pillar-passenger", "dash", (0.97, 0.15, 0.95),
                                             "Passenger A-pillar base"),
    "Console, between the seats": ("console", "cabin", (0.5, 0.75, 0.3),
                                   "Console, between the seats"),
    "Driver rear quarter trim": ("quarter-driver", "cargo", (0.04, 0.8, 0.4),
                                 "Driver rear quarter trim"),
    "Passenger rear quarter trim": ("quarter-passenger", "cargo", (0.96, 0.8, 0.4),
                                    "Passenger rear quarter trim"),
    "Driver-side cargo bin": ("cargo-bin", "cargo", (0.15, 0.5, 0.15), "Driver-side cargo bin"),
    "Passenger-side cargo bin": ("cargo-bin-passenger", "cargo", (0.85, 0.5, 0.15),
                                 "Passenger-side cargo bin"),
    # the overhaul's places (D-610, D-609): the doors' plugs at the A-pillar boot, the amplifier's dock
    "Door, at the A-pillar boot": ("pillar-driver", "dash", (0.03, 0.15, 0.95), "Driver A-pillar base"),
    "Amplifier dock, passenger-side cargo bin": ("cargo-bin-passenger", "cargo", (0.85, 0.5, 0.15),
                                                 "Passenger-side cargo bin"),
}
# The top-level parts: no row places any of them yet (00-CAR parts has no model_at_mm for the
# cluster, the radio or the PMU, and D-416 says nothing places the dash node), so each is a
# judgement inside 00-CAR zones dash: (fx fy fz across the box, what the spot stands for). The
# point is the face's centre for a unit, the board's centre for the plate, the box's centre for
# the PMU. Driver on the left: a US car (x right, D-418).
TOP = {
    "control-unit": ((0.5, 0.12, 0.33), "the centre stack's opening (modules DCU)"),
    "display-unit": ((0.28, 0.1, 0.72), "the binnacle aperture ahead of the driver (modules ICU)"),
    "pmu": ((0.5, 0.8, 0.3), "the dash node, behind the stack at the firewall (modules PMU)"),
    "cur-board": ((0.43, 0.07, 0.67), "the dash face right of the wheel, high beside the DU (P198, D-586)"),
    "cur": ((0.43, 0.07, 0.67), "the dash face right of the wheel, high beside the DU (D-514, D-586)"),
}
# Drops whose far end is not the dash post: the record's rulings, one line each.
FAR_END = {
    "DP-CUR": ("control-unit", "D-521 / D-582: the CUR's link, a breakout of the Control Unit's "
                               "branch (DP-DCU 36-47)", "DP-DCU"),
}


# ------------------------------------------------------------- version 2: the harness (D-514) --
# The two builders whose glb files and manifests the scene places (Y24, Y28). The export runs them
# as steps; their own READMEs say how each model is made.
CONNECTORS_BUILDER = os.path.join(HERE, "harness_connectors.py")
DEVICES_BUILDER = os.path.join(HERE, "harness_devices.py")
STEPS = ["connectors", "devices"]
UNIT_OF = {"ICU unit": "display-unit", "Control Unit": "control-unit",   # housings.where -> unit
           "CUR": "cur", "On the CUR's pigtail": "cur"}                  # D-615: the CUR's DRC 24 on its pigtail

# Nodes no housings.where names, judgement: (zone, box, fx fy fz, name, why).
NODES_EXTRA = {
    "cargo-bin-passenger": ("cargo", 0, (0.85, 0.5, 0.15), "Passenger-side cargo bin",
                            "D-449: the battery, disconnect, Class-T, MRBF and amplifier"),
    "door-driver": ("doors", 0, (0.5, 0.7, 0.4), "Driver door",
                    "RT20: the door's drop through the jamb boot (D1)"),
    "door-passenger": ("doors", 1, (0.5, 0.7, 0.4), "Passenger door",
                       "RT20: the door's drop through the jamb boot (D2)"),
}
# Devices the devices builder sits at leg-l4 because the passenger cargo bin had no node (D-449).
MOVE_DEVICES = {k: "cargo-bin-passenger" for k in ("P049", "P047", "P051", "00-CAR:P-002", "DV60")}

# ------------------------------------------------- the harness as it will be built (D-583, Y57) --
# Every number below is a judgement in the car's frame (D-418: mm, x right, y forward from the
# front axle, z up), made against the 00-CAR zone boxes (zones.model_box_mm) and the unibody's
# panels: the firewall's cabin face at y -660 (the windscreen foot is -642), the dash rail behind
# the dash at y -800 z 690, the cabin floor at z about 215, the tunnel's sides at x +-145, the
# inner sills at x +-690, the cargo floor at z about 480, the hatch hinge line at y -2230 z 1160.
# Nothing is measured (R11, D-416): every point is confirm.
#
# TRUNKS: each leg's trunk - "main" from its row at the dash post (or "start"), and "subs", each
# leaving a point already on the trunk ("main" or an earlier sub, named by its index there as
# (trunk, index)) - the runs the bundle is taped along. Each housing and device the leg feeds then
# gets its own breakout from the nearest point of its leg's trunk (BREAKOUT_*).
TRUNKS = {
    "L1": {"main": [(250, -700, 690), (300, -650, 700), (300, -600, 700), (0, -600, 720),
                    (-400, -600, 720)],
           "subs": [(("main", 3), [(470, -560, 700), (470, 150, 700)]),
                    (("main", 4), [(0, -450, 660), (0, 150, 600)])]},
    "L2": {"main": [(500, -700, 780), (550, -650, 800), (520, -580, 760), (520, 450, 720),
                    (520, 590, 600), (0, 590, 600), (-520, 590, 600)],
           "subs": [(("main", 2), [(-330, -650, 820)]),
                    (("main", 6), [(0, 860, 360)])]},
    "L3": {"main": [(0, -800, 690), (-370, -800, 690), (-640, -800, 690)],
           "subs": [(("main", 1), [(330, -800, 690), (640, -800, 690)]),
                    (("main", 1), [(0, -880, 430), (0, -1120, 430), (-145, -1150, 235),
                                   (-145, -1750, 235)]),
                    ((1, 2), [(145, -1150, 235), (145, -1750, 235)])]},
    "L4": {"main": [(-60, -760, 420), (-190, -1100, 240), (-190, -2050, 240), (-190, -2220, 470),
                    (0, -2540, 520), (0, -3030, 560)],
           "subs": [(("main", 6), [(-560, -3030, 600)]),
                    (("main", 6), [(560, -3030, 600)]),
                    (("main", 5), [(-650, -2540, 600), (-680, -2300, 1000), (-350, -2240, 1140),
                                   (0, -2600, 1060), (0, -2900, 1020)]),
                    (("main", 0), [(-300, -760, 400), (-640, -800, 300), (-700, -1100, 300)]),
                    ((3, 3), [(-760, -800, 430), (-770, -1080, 516)]),
                    ((3, 3), [(-600, -1150, 220), (600, -1150, 220), (760, -800, 430),
                              (770, -1080, 516)])]},
    "Audio": {"start": (0, -1000, 640),
              "main": [(150, -1000, 430), (150, -1150, 230), (660, -1150, 230),
                       (660, -2050, 230), (600, -2250, 470), (500, -2450, 480)],
              "subs": [(("main", 6), [(-500, -2450, 480), (-660, -2250, 470), (-660, -2050, 230),
                                      (-660, -1150, 230)])]},
}
LEG_NAMES = {"L1": "L1 Engine", "L2": "L2 Front", "L3": "L3 Dash", "L4": "L4 Rear",
             "Audio": "Audio"}
# routes.leg -> the trunk a run of that route hangs on
ROUTE_LEG = {"L1 Engine": "L1", "L2 Front": "L2", "L3 Dash": "L3", "L4 Rear": "L4", "Sill": "L4",
             "Audio": "Audio"}
# housings.leg -> the trunk, when no cavity of the housing names a route
HOUSING_LEG = {"L1 Engine": "L1", "L2 Front": "L2", "L3 Dash": "L3", "L4 Rear": "L4",
               "L4 Rear (sill)": "L4"}
UNIT_LEG = {"control-unit": "L3", "display-unit": "L3", "cur": "L3"}
# the doors: no device is modelled inside them (DV67 / DV68 have no model), so the breakout
# carrying D1's and D2's conductors ends at the door's node
DOOR_ITEMS = [("door-driver", "D1"), ("door-passenger", "D2")]

# Where a device sits, when its node's shelf is not where it would be fitted: its model's origin
# (the builders' "z=0 the base, centred") at (x, y, z), one row per instance in its manifest's
# order. Judgement from the 1982 diagram's locations (devices.zone, routes) and the zone boxes.
SPOTS = {
    "DV01": [(180, -330, 620)], "DV02": [(-260, -380, 300)], "DV03": [(470, -420, 640)],
    "DV04": [(-230, 230, 450)], "DV05": [(70, -790, 250)], "DV06": [(40, -300, 560)],
    "DV07": [(-90, -280, 380)], "DV08": [(-430, -540, 760)],
    "P004": [(470, -330, 640)], "P005": [(470, -330, 600)],
    "P053": [(-330, -430, 420), (-330, -380, 420)],
    "DV10": [(-560, 640, 600), (560, 640, 600)], "DV11": [(-560, 560, 470), (560, 560, 470)],
    "DV12": [(-600, 880, 330), (600, 880, 330)], "DV13": [(-800, 800, 380), (800, 800, 380)],
    "DV14": [(-380, 830, 280), (380, 830, 280)], "DV15": [(-330, -600, 790)],
    "DV16": [(480, 420, 450)],
    "DV18": [(-330, -930, 640)], "DV19": [(-365, -960, 700)], "DV25": [(-300, -770, 520)],
    "DV26": [(60, -1450, 330)], "DV27": [(430, -820, 520)], "DV28": [(0, -995, 640)],
    "DV29": [(0, -1150, 470)], "DV44": [(-200, -900, 560)], "DV50": [(-200, -760, 470)],
    "DV55": [(430, -770, 470)], "DV56": [(150, -900, 470)],
    "DV59": [(180, -800, 600), (260, -800, 620), (340, -800, 600)], "DV63": [(260, -900, 780)],
    "DV34": [(-120, -2750, 300)], "DV36": [(120, -2750, 400)],
    "DV37": [(-560, -3080, 640), (560, -3080, 640)],
    "DV38": [(-90, -3150, 560), (90, -3150, 560), (-820, -2950, 600), (820, -2950, 600)],
    "DV39": [(0, -1950, 1170)], "DV40": [(-620, -2750, 760)],
    "DV41": [(-760, -790, 420), (760, -790, 420)], "DV47": [(60, -1150, 240)],
    "DV48": [(0, -3060, 700)], "DV49": [(-760, -2650, 720)], "DV51": [(-60, -1050, 240)],
    "DV64": [(0, 900, 340)], "DV65": [(0, -2950, 960)],
    "DV60": [(560, -2420, 480)], "DV66": [(560, -2600, 480)], "DV61": [(-520, -2600, 480)],
    "00-CAR:P-002": [(580, -2800, 480)], "P049": [(380, -2800, 520)],
    "P047": [(380, -2700, 480)], "P051": [(380, -2640, 480), (380, -2600, 480)],
}
BREAKOUT_BEND = 25.0       # mm: the radius a bundle is bent round at a corner (drawn)
WALL_X = 680.0             # mm: the cabin's and cargo's side wall, inside the trim
WALL_RISE = 300.0          # mm: a breakout that climbs more than this behind the dash goes by the wall
TAPE = "a taped bundle (a dark wrap); the trunk's thickness from the conductors still in it"
AWG_OD = {"10": 3.5, "12": 2.9, "14": 2.4, "16": 2.0, "18": 1.7, "20": 1.5, "22": 1.3}
BUNDLE_K, BUNDLE_MIN_R = 1.2, 3.0
WIRED = ("LIVE", "CAPPED")      # a conductor in the leg; RESERVED is pinned at the post only
CLUSTER_GAP, NODE_GAP, DEVICE_GAP, ROW_WRAP = 20.0, 5.0, 10.0, 600.0


def rel(p):
    return os.path.relpath(p, ROOT)


class Fail(Exception):
    """rc 1: a source is inconsistent."""


class Crash(Exception):
    """rc 3: a tool is missing or crashed."""


# =================================================================================== glb, pure ==
# Read, write and measure binary glTF without numpy: the system python and FreeCAD's both import
# this module.
F32, U8, I8, U16, U32 = 5126, 5121, 5120, 5123, 5125
_CT = {F32: ("f", 4), U8: ("B", 1), I8: ("b", 1), U16: ("H", 2), U32: ("I", 4)}
_NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_glb(path):
    with open(path, "rb") as fh:
        data = fh.read()
    magic, ver, length = struct.unpack("<4sII", data[:12])
    if magic != b"glTF" or ver != 2:
        raise Fail("%s is not a glTF 2 binary" % path)
    off, js, bin_ = 12, None, b""
    while off < length:
        clen, ctype = struct.unpack("<I4s", data[off:off + 8])
        chunk = data[off + 8:off + 8 + clen]
        if ctype == b"JSON":
            js = json.loads(chunk.decode("utf-8"))
        elif ctype == b"BIN\x00":
            bin_ = chunk
        off += 8 + clen
    return js, bin_


def _accessor(js, bin_, i):
    a = js["accessors"][i]
    bv = js["bufferViews"][a["bufferView"]]
    code, size = _CT[a["componentType"]]
    nc = _NC[a["type"]]
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", 0) or size * nc
    count = a["count"]
    out = array.array(code)
    if stride == size * nc:
        out.frombytes(bin_[base:base + count * stride])
    else:
        for k in range(count):
            o = base + k * stride
            out.frombytes(bin_[o:o + size * nc])
    if sys.byteorder != "little":
        out.byteswap()
    if a.get("normalized") and code in "bB":
        scale = 127.0 if code == "b" else 255.0
        out = array.array("f", [max(v / scale, -1.0) for v in out])
    return out


def _mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _node_matrix(n):
    if "matrix" in n:
        m = n["matrix"]
        return [[m[c * 4 + r] for c in range(4)] for r in range(4)]
    t = n.get("translation", [0, 0, 0])
    x, y, z, w = n.get("rotation", [0, 0, 0, 1])
    s = n.get("scale", [1, 1, 1])
    r = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
         [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
         [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    return [[r[0][0] * s[0], r[0][1] * s[1], r[0][2] * s[2], t[0]],
            [r[1][0] * s[0], r[1][1] * s[1], r[1][2] * s[2], t[1]],
            [r[2][0] * s[0], r[2][1] * s[1], r[2][2] * s[2], t[2]],
            [0, 0, 0, 1]]


def _walk(js, visit):
    """visit(node_index, world_matrix, top_level_index) for every node under the scene."""
    eye = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
    scene = js["scenes"][js.get("scene", 0)]
    stack = [(i, eye, None) for i in scene["nodes"]]
    while stack:
        i, parent, top = stack.pop()
        m = _mat_mul(parent, _node_matrix(js["nodes"][i]))
        visit(i, m, top)
        for c in js["nodes"][i].get("children", []):
            stack.append((c, m, c if top is None else top))


def glb_bbox(path):
    """The file's bounding box in its own frame: accessor min / max through each node's matrix."""
    js, _ = read_glb(path)
    lo, hi = [math.inf] * 3, [-math.inf] * 3

    def visit(i, m, top):
        n = js["nodes"][i]
        if "mesh" not in n:
            return
        for p in js["meshes"][n["mesh"]]["primitives"]:
            a = js["accessors"][p["attributes"]["POSITION"]]
            amin, amax = a["min"], a["max"]
            for cx in (amin[0], amax[0]):
                for cy in (amin[1], amax[1]):
                    for cz in (amin[2], amax[2]):
                        for k in range(3):
                            v = m[k][0] * cx + m[k][1] * cy + m[k][2] * cz + m[k][3]
                            lo[k], hi[k] = min(lo[k], v), max(hi[k], v)
    _walk(js, visit)
    return lo, hi


def material(name, rgba, metallic=0.0, roughness=0.6):
    return {"name": name, "rgba": [round(float(c), 4) for c in rgba],
            "metallic": metallic, "roughness": roughness}


def write_glb(path, nodes, materials, root_name, extras=None):
    """nodes: [{"name", "prims": [(material index, positions array('f'), normals array('f'),
    indices array('I'))]}] in the part's own frame, mm, z up. One glTF node per entry under one
    root, one primitive per material per chunk of at most 65535 vertices. Returns
    {"bytes", "bbox": [lo, hi], "vertices", "triangles"}."""
    blob = bytearray()
    views, accs, meshes, gnodes = [], [], [], []
    lo, hi = [math.inf] * 3, [-math.inf] * 3
    nverts = ntris = 0

    def put(data, target, stride=None):
        while len(blob) % 4:
            blob.append(0)
        v = {"buffer": 0, "byteOffset": len(blob), "byteLength": len(data), "target": target}
        if stride:
            v["byteStride"] = stride
        blob.extend(data)
        views.append(v)
        return len(views) - 1

    def flush(mat, pos, nrm, idx, prims):
        nonlocal nverts, ntris
        n = len(pos) // 3
        if n == 0 or not idx:
            return
        xs, ys, zs = pos[0::3], pos[1::3], pos[2::3]
        mn, mx = [min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]
        for k in range(3):
            lo[k], hi[k] = min(lo[k], mn[k]), max(hi[k], mx[k])
        p = array.array("f", pos)
        qb = array.array("b", [127 if c >= 1.0 else -127 if c <= -1.0 else int(round(c * 127.0))
                               for c in nrm]).tobytes()
        q = bytearray(4 * n)                       # int8 x3, padded to 4 bytes a vertex
        q[0::4], q[1::4], q[2::4] = qb[0::3], qb[1::3], qb[2::3]
        wide = n > 65535
        ix = array.array("I" if wide else "H", idx)
        if sys.byteorder != "little":
            p.byteswap()
            ix.byteswap()
        accs.append({"bufferView": put(p.tobytes(), 34962), "componentType": F32, "count": n,
                     "type": "VEC3", "min": mn, "max": mx})
        pa = len(accs) - 1
        accs.append({"bufferView": put(bytes(q), 34962, 4), "componentType": I8,
                     "normalized": True, "count": n, "type": "VEC3"})
        na = len(accs) - 1
        accs.append({"bufferView": put(ix.tobytes(), 34963),
                     "componentType": U32 if wide else U16, "count": len(ix), "type": "SCALAR"})
        prims.append({"attributes": {"POSITION": pa, "NORMAL": na}, "indices": len(accs) - 1,
                      "material": mat, "mode": 4})
        nverts += n
        ntris += len(ix) // 3

    for node in nodes:
        by_mat = {}
        for (mat, pos, nrm, idx) in node["prims"]:
            by_mat.setdefault(mat, []).append((pos, nrm, idx))
        prims = []
        for mat in sorted(by_mat):
            pos, nrm, idx = array.array("f"), array.array("f"), []
            for (p, nm, ix) in by_mat[mat]:
                n = len(p) // 3
                if len(pos) // 3 + n > 65535 and len(pos):
                    flush(mat, pos, nrm, idx, prims)
                    pos, nrm, idx = array.array("f"), array.array("f"), []
                base = len(pos) // 3
                pos.extend(p)
                nrm.extend(nm)
                idx.extend([i + base for i in ix])
            flush(mat, pos, nrm, idx, prims)
        if not prims:
            continue
        meshes.append({"name": node["name"], "primitives": prims})
        gnodes.append({"name": node["name"], "mesh": len(meshes) - 1})
    js = {
        "asset": {"version": "2.0", "generator": "Rx7 00-design/tools/export_glb.py",
                  "extras": dict(extras or {}, units="mm", up="z")},
        "extensionsUsed": ["KHR_mesh_quantization"],
        "extensionsRequired": ["KHR_mesh_quantization"],
        "scene": 0,
        "scenes": [{"name": root_name, "nodes": [0]}],
        "nodes": [{"name": root_name, "children": list(range(1, len(gnodes) + 1))}] + gnodes,
        "meshes": meshes,
        "materials": [{"name": m["name"], "doubleSided": True,
                       "pbrMetallicRoughness": {"baseColorFactor": m["rgba"],
                                                "metallicFactor": m["metallic"],
                                                "roughnessFactor": m["roughness"]}}
                      for m in materials],
        "accessors": accs,
        "bufferViews": views,
        "buffers": [{"byteLength": len(blob)}],
    }
    if any(m["rgba"][3] < 1 for m in materials):
        for g, m in zip(js["materials"], materials):
            if m["rgba"][3] < 1:
                g["alphaMode"] = "BLEND"
    jb = json.dumps(js, separators=(",", ":")).encode("utf-8")
    jb += b" " * ((4 - len(jb) % 4) % 4)
    while len(blob) % 4:
        blob.append(0)
    total = 12 + 8 + len(jb) + 8 + len(blob)
    tmp = path + ".part"
    with open(tmp, "wb") as fh:
        fh.write(struct.pack("<4sII", b"glTF", 2, total))
        fh.write(struct.pack("<I4s", len(jb), b"JSON"))
        fh.write(jb)
        fh.write(struct.pack("<I4s", len(blob), b"BIN\x00"))
        fh.write(blob)
    os.replace(tmp, path)
    box = [[round(v, 3) + 0.0 for v in lo], [round(v, 3) + 0.0 for v in hi]]
    return {"bytes": total, "bbox": box, "vertices": nverts, "triangles": ntris}


def repack_kicad(src, dst, root_name, hide=()):
    """kicad-cli's glb (metres, y up, one node per part and per layer, 40 000-odd primitives)
    -> ours: mm, z up, the board frame (x = KiCad x, y = -KiCad y, z up from the board's
    underside - the frame of the board's STEP and of enclosure_extract's board.json), two nodes:
    `pcb:board` (the laminate, copper, mask, silkscreen) and `pcb:parts` (the parts' models)."""
    js, bin_ = read_glb(src)
    mats, mat_of = [], {}
    for i, m in enumerate(js.get("materials", [])):
        pbr = m.get("pbrMetallicRoughness", {})
        rgba = pbr.get("baseColorFactor", [0.7, 0.7, 0.7, 1.0])
        key = tuple(round(c, 4) for c in rgba)
        if key not in mat_of:
            mat_of[key] = len(mats)
            mats.append(material("m%d" % len(mats), rgba, pbr.get("metallicFactor", 0.0),
                                 pbr.get("roughnessFactor", 0.6)))
        mat_of[i] = mat_of[key]
    if not mats:
        mats.append(material("default", [0.7, 0.7, 0.7, 1.0]))
    groups = {"pcb:board": [], "pcb:parts": []}
    names = js["nodes"]

    def visit(i, m, top):
        n = names[i]
        if "mesh" not in n:
            return
        # the frame: glTF (X, Y, Z) metres -> (1000 X, -1000 Z, 1000 Y) mm
        c = [[1000 * m[0][j] for j in range(4)],
             [-1000 * m[2][j] for j in range(4)],
             [1000 * m[1][j] for j in range(4)]]
        tname = names[top].get("name", "") if top is not None else ""
        if tname in hide:
            return
        group = "pcb:board" if (top is None or tname.startswith("=>")) else "pcb:parts"
        for p in js["meshes"][n["mesh"]]["primitives"]:
            if p.get("mode", 4) != 4:
                continue
            pos = _accessor(js, bin_, p["attributes"]["POSITION"])
            xs, ys, zs = pos[0::3], pos[1::3], pos[2::3]
            out = array.array("f", bytes(4 * len(pos)))
            for k in range(3):
                a, b, cc, d = c[k]
                out[k::3] = array.array("f", [a * x + b * y + cc * z + d
                                              for x, y, z in zip(xs, ys, zs)])
            if "indices" in p:
                idx = list(_accessor(js, bin_, p["indices"]))
            else:
                idx = list(range(len(pos) // 3))
            if "NORMAL" in p["attributes"]:
                nr = _accessor(js, bin_, p["attributes"]["NORMAL"])
                nx, ny, nz = nr[0::3], nr[1::3], nr[2::3]
                outn = array.array("f", bytes(4 * len(nr)))
                for k in range(3):
                    a, b, cc, _ = c[k]
                    outn[k::3] = array.array("f", [a * x + b * y + cc * z
                                                   for x, y, z in zip(nx, ny, nz)])
                for k in range(0, len(outn), 3):
                    ln = math.sqrt(outn[k] ** 2 + outn[k + 1] ** 2 + outn[k + 2] ** 2) or 1.0
                    outn[k], outn[k + 1], outn[k + 2] = (outn[k] / ln, outn[k + 1] / ln,
                                                         outn[k + 2] / ln)
            else:
                outn = face_normals(out, idx)
            if group == "pcb:board":
                out, outn, idx = _drop_low_walls(out, outn, idx)
            if idx:
                groups[group].append((mat_of.get(p.get("material"), 0), out, outn, idx))
    _walk(js, visit)
    nodes = [{"name": g, "prims": groups[g]} for g in ("pcb:board", "pcb:parts")]
    return write_glb(dst, nodes, mats, root_name)


LOW_WALL = 0.1    # mm: a vertical wall shorter than this is a copper or mask edge


def _drop_low_walls(pos, nrm, idx):
    """Drop the board's vertical walls under LOW_WALL tall - the 35 um edges of every track,
    pad and pour, invisible at any zoom and half the copper's vertices. The laminate's edge and
    the via barrels (1.6 mm) stay."""
    zs = pos[2::3]
    nz = nrm[2::3]
    keep = []
    for t in range(0, len(idx) - 2, 3):
        a, b, c = idx[t], idx[t + 1], idx[t + 2]
        if abs(nz[a]) < 0.1 and abs(nz[b]) < 0.1 and abs(nz[c]) < 0.1 and \
                max(zs[a], zs[b], zs[c]) - min(zs[a], zs[b], zs[c]) < LOW_WALL:
            continue
        keep += (a, b, c)
    if len(keep) == len(idx):
        return pos, nrm, idx
    remap, p2, n2 = {}, array.array("f"), array.array("f")
    out = []
    for v in keep:
        w = remap.get(v)
        if w is None:
            w = remap[v] = len(p2) // 3
            p2.extend(pos[3 * v:3 * v + 3])
            n2.extend(nrm[3 * v:3 * v + 3])
        out.append(w)
    return p2, n2, out


def face_normals(pos, idx):
    """Smooth normals over one patch: each vertex the area-weighted mean of its triangles'."""
    n = len(pos) // 3
    acc = [0.0] * (3 * n)
    for t in range(0, len(idx) - 2, 3):
        a, b, c = idx[t], idx[t + 1], idx[t + 2]
        ax, ay, az = pos[3 * a], pos[3 * a + 1], pos[3 * a + 2]
        ux, uy, uz = pos[3 * b] - ax, pos[3 * b + 1] - ay, pos[3 * b + 2] - az
        vx, vy, vz = pos[3 * c] - ax, pos[3 * c + 1] - ay, pos[3 * c + 2] - az
        cx, cy, cz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        for v in (a, b, c):
            acc[3 * v] += cx
            acc[3 * v + 1] += cy
            acc[3 * v + 2] += cz
    out = array.array("f", acc)
    for k in range(0, len(out), 3):
        ln = math.sqrt(out[k] ** 2 + out[k + 1] ** 2 + out[k + 2] ** 2)
        if ln > 0:
            out[k], out[k + 1], out[k + 2] = out[k] / ln, out[k + 1] / ln, out[k + 2] / ln
        else:
            out[k], out[k + 1], out[k + 2] = 0.0, 0.0, 1.0
    return out


# ============================================================================== the KiCad side ==
def pcb_outline(pcb):
    """The board's Edge.Cuts bounding box in the board frame (x, -y KiCad): [x0, x1, y0, y1]."""
    txt = open(pcb, encoding="utf-8").read()
    xs, ys = [], []
    for m in re.finditer(r"\((gr_line|gr_rect|gr_arc|gr_poly|gr_circle)\b", txt):
        depth, k = 0, m.start()
        while True:
            ch = txt[k]
            depth += (ch == "(") - (ch == ")")
            k += 1
            if depth == 0:
                break
        block = txt[m.start():k]
        if '"Edge.Cuts"' not in block:
            continue
        for x, y in re.findall(r"\((?:start|end|mid|center|xy)\s+([-\d.]+)\s+([-\d.]+)\)", block):
            xs.append(float(x))
            ys.append(-float(y))
    if not xs:
        raise Fail("%s has no Edge.Cuts outline" % rel(pcb))
    return [min(xs), max(xs), min(ys), max(ys)]


def _sexp_end(txt, k):
    """The index just past the s-expression that opens at txt[k] == "(" (quoted strings skipped)."""
    depth, quoted = 0, False
    while k < len(txt):
        ch = txt[k]
        if quoted:
            if ch == "\\":
                k += 1
            elif ch == '"':
                quoted = False
        elif ch == '"':
            quoted = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return k + 1
        k += 1
    return len(txt)


def pcb_footprint_at(pcb, ref):
    """A footprint's origin in the board frame, or None. Each footprint is read only within its
    own s-expression (a fixed window once ran into the next footprint and gave R1's place for J1)."""
    txt = open(pcb, encoding="utf-8").read()
    for m in re.finditer(r"\(footprint\s+\"[^\"]*\"", txt):
        block = txt[m.start():_sexp_end(txt, m.start())]
        if re.search(r'\(property\s+"Reference"\s+"%s"' % re.escape(ref), block):
            at = re.search(r"\(at\s+([-\d.]+)\s+([-\d.]+)", block)
            if at:
                return [float(at.group(1)), -float(at.group(2))]
    return None


def _selftest_footprint_at():
    """pcb_footprint_at on a two-footprint board: each ref gets its own place, a missing one None.
    Returns the list of what came out wrong."""
    snippet = ('(kicad_pcb\n'
               ' (footprint "Resistor_SMD:R_0603" (layer "B.Cu") (at 62.5 39.5 90)\n'
               '  (property "Reference" "R1" (at 0 -1 0))\n'
               '  (property "Value" "10k (a quoted paren: ) here")\n'
               '  (pad "1" smd rect (at -0.8 0 90)))\n'
               ' (footprint "Connector_IDC:IDC-Header_2x06" (layer "B.Cu") (at 94.5 21.65 180)\n'
               '  (property "Reference" "J1" (at 0 -2 0))\n'
               '  (pad "1" thru_hole rect (at 0 0 180))))\n')
    bad = []
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "two.kicad_pcb")
        with open(path, "w") as fh:
            fh.write(snippet)
        for ref, want in (("J1", [94.5, -21.65]), ("R1", [62.5, -39.5]), ("J9", None)):
            got = pcb_footprint_at(path, ref)
            if got != want:
                bad.append("pcb_footprint_at(%s) gave %s, not %s" % (ref, got, want))
    return bad


def _selftest_saved_place():
    """_saved_place on a three-row parts table: a saved place is taken as the part's place, a blank
    cell gives None (the provisional spot stands), a bad place is refused. What came out wrong."""
    rec = {("01-electrical", "parts"): [{"id": "P1", "place": "-310.5 1200 640 90 0 -5"},
                                        {"id": "P2", "place": ""},
                                        {"id": "P3", "place": "-310 1200 640"}]}
    bad = []
    got = _saved_place(rec, "parts", "P1")
    if not got or got[0] != _place(-310.5, 1200, 640, 90, 0, -5) or \
            got[1] != "01-electrical parts P1":
        bad.append("a saved place gave %s" % (got,))
    if _saved_place(rec, "parts", "P2") is not None:
        bad.append("a blank place was not None")
    try:
        _saved_place(rec, "parts", "P3")
        bad.append("a place of three numbers was taken")
    except Fail:
        pass
    return bad


def build_board(bid, out):
    pcb = os.path.join(DESIGN, BOARDS[bid][0])
    if not os.path.exists(pcb):
        raise Fail("%s: %s is not there" % (bid, rel(pcb)))
    if not os.path.exists(KICAD_CLI):
        raise Crash("kicad-cli is not at %s (set KICAD_CLI)" % KICAD_CLI)
    env = dict(os.environ, RX7_MODELS=RX7_MODELS, KICAD10_3DMODEL_DIR=KICAD_MODELS)
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, bid + ".glb")
        r = subprocess.run([KICAD_CLI, "pcb", "export", "glb"] + KICAD_FLAGS +
                           ["-f", "-o", raw, pcb], env=env, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(raw):
            raise Crash("kicad-cli failed on %s: %s" % (rel(pcb), (r.stderr or r.stdout)[-400:]))
        missing = sorted(set(re.findall(r"Could not add 3D model for (\S+?)\.",
                                        r.stdout + r.stderr)))
        files = sorted(set(os.path.basename(f) for f in re.findall(
            r"File not found: (\S+)", r.stdout + r.stderr)))
        info = repack_kicad(raw, os.path.join(out, bid + ".glb"), bid,
                            hide=BOARD_HIDE.get(bid, {}).get("refs", ()))
    meta = {"id": bid, "kind": "pcb", "glb": bid + ".glb", "bytes": info["bytes"],
            "bbox": info["bbox"], "vertices": info["vertices"], "triangles": info["triangles"],
            "nodes": {"board": ["pcb:board"], "parts": ["pcb:parts"]},
            "outline": pcb_outline(pcb), "source": rel(pcb),
            "missing_models": missing, "missing_files": files,
            "origin": "KiCad's origin, the board frame of its STEP: x = KiCad x, y = -KiCad y, "
                      "z = 0 on the board's underside"}
    if bid in BOARD_HIDE:
        meta["hidden"] = dict(BOARD_HIDE[bid])
    if bid == "cur-board":
        meta["j1"] = pcb_footprint_at(pcb, "J1")
    return meta


# =========================================================================== the FreeCAD side ==
def run_fc(job):
    if not os.path.exists(FREECADCMD):
        raise Crash("freecadcmd is not at %s (set FREECADCMD)" % FREECADCMD)
    with tempfile.TemporaryDirectory() as tmp:
        jpath = os.path.join(tmp, "job.json")
        job = dict(job, meta=os.path.join(tmp, "meta.json"))
        with open(jpath, "w") as fh:
            json.dump(job, fh)
        env = dict(os.environ, RX7_EXPORT_JOB=jpath)
        r = subprocess.run([FREECADCMD, os.path.join(HERE, "export_glb_fc.py")], env=env,
                           capture_output=True, text=True, cwd=tmp)
        meta = None
        if os.path.exists(job["meta"]):
            meta = json.load(open(job["meta"]))
        if r.returncode == 1 and meta and meta.get("problems"):
            raise Fail("%s: %s" % (job["id"], " | ".join(meta["problems"])))
        if r.returncode != 0 or meta is None:
            raise Crash("freecadcmd failed on %s (rc %s): %s"
                        % (job["id"], r.returncode, (r.stderr or r.stdout)[-600:]))
        return meta


def build_unit(uid, out):
    u = UNITS[uid]
    name = u["assembly"]
    params = os.path.join(layout.data_dir(layout.part_of(name)), name.replace("-", "_") + "_params.py")
    meta = run_fc({"id": uid, "kind": "unit", "assembly": name, "params": params,
                   "lib": os.path.join(HERE, name.replace("-", "_") + ".py"), "cad_dir": layout.cad_dir(name),
                   "tools_dir": HERE, "glb": os.path.join(out, uid + ".glb"),
                   "children": u["children"], "linear": UNIT_LINEAR, "angular": UNIT_ANGULAR})
    meta.update({"id": uid, "kind": "unit", "glb": uid + ".glb",
                 "source": "%s (%s, %s)" % (rel(layout.cad_dir(name)), rel(params),
                                            rel(os.path.join(HERE, name.replace("-", "_") + ".py")))})
    return meta


def build_pmu(out):
    if not os.path.exists(PMU_STEP):
        raise Fail("the PMU's STEP is not at %s" % rel(PMU_STEP))
    meta = run_fc({"id": "pmu", "kind": "pmu", "step": PMU_STEP, "tools_dir": HERE,
                   "glb": os.path.join(out, "pmu.glb"),
                   "linear": PMU_LINEAR, "angular": PMU_ANGULAR})
    meta.update({"id": "pmu", "kind": "module", "glb": "pmu.glb", "source": rel(PMU_STEP)})
    return meta


# =============================================================================== the stamps ==
def _hash_files(paths):
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(rel(p).encode())
        with open(p, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:16]


def source_files(aid):
    """Every file an asset is made from (and this script), for the staleness stamp."""
    mine = [os.path.join(HERE, "export_glb.py"), os.path.join(HERE, "export_glb_fc.py")]
    if aid in BOARDS:
        pcb = os.path.join(DESIGN, BOARDS[aid][0])
        d = os.path.dirname(pcb)
        files = [pcb] + [os.path.join(dp, f) for dp, _, fs in os.walk(d) for f in fs
                         if dp.endswith(".pretty") and f.endswith(".kicad_mod")]
        return mine + files
    if aid in UNITS:
        name = UNITS[aid]["assembly"]
        files = [os.path.join(layout.data_dir(layout.part_of(name)), name.replace("-", "_") + "_params.py"),
                 os.path.join(HERE, name.replace("-", "_") + ".py")]
        if "sources" in UNITS[aid]:
            files += [os.path.join(DESIGN, f) for f in UNITS[aid]["sources"]]
        else:
            car = [c for c in UNITS[aid]["children"] if "carrier" in c][0]
            files += [layout.data_file(car, s) for s in ("-board.json", "-probe.json")]
        files.append(os.path.join(HERE, "enclosure_lib.py"))
        return mine + [f for f in files if os.path.exists(f)]
    if aid == "pmu":
        return mine + [PMU_STEP]
    raise KeyError(aid)


# =============================================================================== the record ==
def read_record():
    """The tables the scene reads, through rx7.py export (the machine-readable view)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "record.json")
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "rx7.py"), "export",
                            "--out", path], cwd=ROOT, capture_output=True, text=True)
        if r.returncode not in (0, 2) or not os.path.exists(path):
            raise Crash("rx7.py export failed (rc %s): %s" % (r.returncode, r.stderr[-300:]))
        data = json.load(open(path))
    want = {("00-CAR", "zones"), ("00-CAR", "parts"), ("01-electrical", "housings"),
            ("01-electrical", "routes"), ("01-electrical", "devices"),
            ("01-electrical", "cavities"), ("01-electrical", "modules"),
            ("01-electrical", "parts")}
    out = {}
    for t in data["tables"]:
        key = (t["area"], t["table"])
        if key in want:
            cols = t["columns"]
            out[key] = [dict(zip(cols, row)) for row in t["rows"]]
    for key in want:
        if key not in out:
            raise Fail("the record has no %s %s" % key)
    return out


def _short(text):
    """The record's words, up to the first ' - ' or em dash: its name, not its note."""
    text = (text or "").strip()
    for sep in (" - ", " — ", " – "):
        if sep in text:
            text = text.split(sep)[0]
    return text.strip()


def _zone_box(rec, zid, box=0):
    for z in rec[("00-CAR", "zones")]:
        if z["id"] == zid and z.get("model_box_mm"):
            boxes = z["model_box_mm"].split(";")
            if box >= len(boxes):
                raise Fail("00-CAR zones %s has no box %d" % (zid, box + 1))
            return [float(v) for v in boxes[box].split()]
    raise Fail("00-CAR zones has no model_box_mm for %r" % zid)


def _in_zone(rec, zid, f, box=0):
    b = _zone_box(rec, zid, box)
    return [round(b[0] + f[0] * (b[1] - b[0]), 1), round(b[2] + f[1] * (b[3] - b[2]), 1),
            round(b[4] + f[2] * (b[5] - b[4]), 1)]


# ================================================================================ the scene ==
def _place(x=0.0, y=0.0, z=0.0, rx=0.0, ry=0.0, rz=0.0):
    return {"x": round(x, 3), "y": round(y, 3), "z": round(z, 3),
            "rx": rx, "ry": ry, "rz": rz}


def _saved_place(rec, table, key):
    """(place, place_from, place_note) from 01-electrical <table> <key>.place - his Save place
    on the Design page (D-520), the car's frame - or None while the cell is blank."""
    for r in rec[("01-electrical", table)]:
        if r.get("id") == key and (r.get("place") or "").strip():
            v = r["place"].split()
            try:
                n = [float(x) for x in v]
            except ValueError:
                n = []
            if len(n) != 6:
                raise Fail("01-electrical %s %s: place %r is not six numbers" % (table, key,
                                                                                 r["place"]))
            return (_place(*n), "01-electrical %s %s" % (table, key),
                    "saved on the Design page (D-520): 01-electrical %s %s.place, confirm until "
                    "the car is measured (R11)" % (table, key))
    return None


def _rot(p, place):
    """A point in a child's frame -> its parent's, by `place` (three.js Euler XYZ, degrees)."""
    x, y, z = p
    for axis, deg in (("z", place["rz"]), ("y", place["ry"]), ("x", place["rx"])):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        if axis == "x":
            y, z = c * y - s * z, s * y + c * z
        elif axis == "y":
            x, z = c * x + s * z, -s * x + c * z
        else:
            x, y = c * x - s * y, s * x + c * y
    return [x, y, z]


def _size(meta):
    lo, hi = meta["bbox"]
    return {"x": round(hi[0] - lo[0], 2), "y": round(hi[1] - lo[1], 2),
            "z": round(hi[2] - lo[2], 2)}


def _row(rec, table, key):
    area_table = ("01-electrical", table)
    k = "id"
    for r in rec[area_table]:
        if r.get(k) == key:
            return r
    raise Fail("01-electrical %s has no row %s" % (table, key))


def _name(rec, table, key):
    r = _row(rec, table, key)
    return _short(r.get("module") or r.get("item") or key)


def assemble(rec, metas, built, out=None):
    """scene.json from the record and the assets' metas. Raises Fail on an inconsistency."""
    notes, missing, parts = [], [], {}
    for aid in ASSETS:
        if aid not in metas:
            raise Fail("%s has no glb: build it (export_glb.py --only %s)" % (aid, aid))

    # ---- the units, with their boards inside
    for uid, u in UNITS.items():
        m = metas[uid]
        name = u.get("name") or _name(rec, *u["row"])
        anchor = _in_zone(rec, "dash", TOP[uid][0])
        fw, fh = m["face"]
        pl = _place(anchor[0] - fw / 2.0, anchor[1], anchor[2] - fh / 2.0)
        pfrom, pnote = "provisional", ("inside 00-CAR zones dash: %s, the face's centre there"
                                       % TOP[uid][1])
        saved = _saved_place(rec, *u["row"])
        if saved:
            pl, pfrom, pnote = saved
        conns = [{"code": c["code"], "at": {"x": round(c["at"][0], 2), "y": round(c["at"][1], 2),
                                            "z": round(c["at"][2], 2)},
                  "face": "rear", "note": c.get("note", "")} for c in m["connectors"]]
        parts[uid] = {
            "id": uid, "name": name, "kind": "unit", "glb": m["glb"], "bytes": m["bytes"],
            "parent": None, "place": pl, "place_from": pfrom, "confirm": True,
            "place_note": pnote, "size_mm": _size(m),
            "origin": "the mock-up's frame: the face's front, bottom-left corner seen from the "
                      "cabin; x across the face, y back into the dash (= the car's forward), z up",
            "connectors": conns, "children": list(u["children"]), "source": m["source"],
            "nodes": m["nodes"]}
        for kid in u["children"]:
            km = metas[kid]
            cp = child_place(kid, m, km, notes)
            parts[kid] = board_part(rec, kid, km, uid, cp, "mock-up report", False)
        for kid, why in u.get("standing_in", {}).items():
            missing.append({"part": uid, "what": "%s board model" % kid, "why": why})
        if m.get("placeholders"):
            missing.append({"part": uid, "what": ", ".join(m["placeholders"]),
                            "why": "placeholder blocks in the mock-up: no model of these parts "
                                   "is in the tree"})
        notes += ["%s: %s" % (uid, n) for n in m.get("notes", [])]

    # ---- the left plate: a board with no housing yet, standing for the plate
    lm = metas["cur-board"]
    if "cur-board" not in parts:                 # not a unit's child (the CUR's, D-514)
        anchor = _in_zone(rec, "dash", TOP["cur-board"][0])
        o = lm["outline"]
        c = _rot([(o[0] + o[1]) / 2.0, (o[2] + o[3]) / 2.0, 0.0], _place(rx=90))
        lp = _place(anchor[0] - c[0], anchor[1] - c[1], anchor[2] - c[2], rx=90)
        parts["cur-board"] = board_part(rec, "cur-board", lm, None, lp, "provisional", True)
        parts["cur-board"]["place_note"] = ("inside 00-CAR zones dash: %s, the board facing "
                                             "the driver" % TOP["cur-board"][1])
    if parts["cur-board"]["parent"] is None:     # the CUR is its housing now (D-514)
        missing.append({"part": "cur-board", "what": "housing model",
                        "why": "no plate housing is drawn yet; the board stands for the plate"})
    if lm.get("j1"):
        parts["cur-board"]["connectors"] = [{"code": "DP-DCU-E", "at": {
            "x": lm["j1"][0], "y": lm["j1"][1], "z": 0.0}, "face": "rear",
            "note": "J1, the cable to DP-DCU-E (D-492), at its footprint's origin"}]

    # ---- the PMU
    pm = metas["pmu"]
    anchor = _in_zone(rec, "dash", TOP["pmu"][0])
    lo, hi = pm["bbox"]
    ctr = [(lo[k] + hi[k]) / 2.0 for k in range(3)]
    parts["pmu"] = {
        "id": "pmu", "name": _name(rec, *PMU["row"]), "kind": "module", "glb": "pmu.glb",
        "bytes": pm["bytes"], "parent": None,
        "place": _place(anchor[0] - ctr[0], anchor[1] - ctr[1], anchor[2] - ctr[2]),
        "place_from": "provisional", "confirm": True,
        "place_note": "inside 00-CAR zones dash: %s, the box's centre there, as the vendor "
                      "model lies" % TOP["pmu"][1],
        "size_mm": _size(pm), "origin": "the vendor STEP's own origin (ECUMaster's frame)",
        "connectors": [], "children": [], "source": pm["source"], "nodes": pm["nodes"]}
    saved = _saved_place(rec, *PMU["row"])
    if saved:
        parts["pmu"]["place"], parts["pmu"]["place_from"], parts["pmu"]["place_note"] = saved

    # ---- links: one per housing, and the nodes their far ends need
    nodes = {}

    def node(key):
        nid, zone, f, label = WHERE[key]
        if nid not in nodes:
            at = _in_zone(rec, zone, f)
            nodes[nid] = {"id": nid, "name": label, "kind": "node", "glb": None, "bytes": 0,
                          "parent": None, "place": _place(*at), "place_from": "provisional",
                          "confirm": True, "place_note": "inside 00-CAR zones %s" % zone,
                          "size_mm": {"x": 0, "y": 0, "z": 0}, "origin": "the place itself",
                          "connectors": [], "children": [],
                          "source": "01-electrical housings.where / leg"}
        return nid

    cav_by = {}
    for cv in rec[("01-electrical", "cavities")]:
        cav_by.setdefault(cv["housing"], []).append(cv)
    unit_of = UNIT_OF
    links, post = [], []
    for h in rec[("01-electrical", "housings")]:
        code, where = h["code"], (h.get("where") or "").strip()
        cavs = sorted(cav_by.get(code, []), key=lambda r: int(r.get("cav") or 0))
        carries = [re.sub(r"\s*\([^)]*\)", "", cv["circuit"]).strip() for cv in cavs
                   if (cv.get("circuit") or "").strip()]
        ways = int(h.get("cavs") or len(cavs) or 0)
        side = h.get("box_side") or h.get("leg_side") or ""
        family = side.split("-")[0] if side else "?"
        label = "%s · %s %d-way" % (code, family, ways)
        on_unit = next((p for k, p in unit_of.items() if where.startswith(k)), None)
        if on_unit:
            frm = {"part": on_unit, "connector": code}
            if code in FAR_END:
                far = FAR_END[code][0]
                if far not in parts:
                    far = node(next(k for k, v in WHERE.items() if v[0] == far))
                to = {"part": far, "connector": FAR_END[code][2] if len(FAR_END[code]) > 2
                      else code}
            else:
                to = {"part": "pmu", "connector": code}
                post.append(code)
        elif where in ("Dash post", "PMU box"):        # the PMU box's plugs and bundles run where the post's did (D-600)
            frm = {"part": "pmu", "connector": code}
            post.append(code)
            leg = (h.get("leg") or "").strip()
            if leg not in WHERE:
                raise Fail("housing %s: leg %r has no far end in WHERE" % (code, leg))
            to = {"part": node(leg), "connector": code}
        else:
            if where not in WHERE:
                raise Fail("housing %s: where %r has no node in WHERE" % (code, where))
            frm = {"part": "pmu", "connector": code}
            post.append(code)
            to = {"part": node(where), "connector": code}
        links.append({"id": code, "code": code, "from": frm, "to": to, "label": label,
                      "ways": ways, "carries": carries, "confirm": False})
    for nid, n in nodes.items():
        n["connectors"] = [{"code": l["code"], "at": {"x": 0, "y": 0, "z": 0}, "face": "",
                            "note": ""} for l in links if l["to"]["part"] == nid]
    # the dash post's receptacles are not modelled: spread along the PMU's connector face
    lo, hi = pm["connector_box"]
    blo, bhi = pm["bbox"]
    span = [hi[k] - lo[k] for k in range(3)]
    ax = max(range(3), key=lambda k: span[k])
    face = [(lo[i] + hi[i]) / 2.0 for i in range(3)]
    for i in range(3):                  # the sockets' outer face: where their box meets the PMU's
        if i != ax and abs(lo[i] - blo[i]) < 1.0:
            face[i] = lo[i]
            break
        if i != ax and abs(hi[i] - bhi[i]) < 1.0:
            face[i] = hi[i]
            break
    for k, code in enumerate(post):
        at = list(face)
        at[ax] = lo[ax] + span[ax] * (k + 0.5) / len(post)
        parts["pmu"]["connectors"].append({
            "code": code, "at": {"x": round(at[0], 2), "y": round(at[1], 2),
                                 "z": round(at[2], 2)}, "face": "connectors",
            "note": "the dash post's receptacle - not modelled; spread along the PMU's "
                    "connector face (provisional)"})
    missing.append({"part": "pmu", "what": "the dash post's receptacles",
                    "why": "no model of the post; its links start on the PMU's connector face"})
    for bid in BOARDS:
        bm = metas[bid]
        if bm.get("hidden"):
            missing.append({"part": bid, "what": "its %s" % ", ".join(bm["hidden"]["refs"]),
                            "why": bm["hidden"]["why"]})
        if bm.get("missing_models"):
            missing.append({"part": bid, "what": "3D models of %s" % ", ".join(
                bm["missing_models"]), "why": "kicad-cli found no file for them on this "
                "machine (%s); the boards show their pads" % ", ".join(bm["missing_files"])})
    notes += [
        "Every glb is in mm with z up, in the part's own frame; place it at `place` (three.js "
        "Euler XYZ, degrees) under its parent, the car's frame for a top-level part (D-418).",
        "No place here is measured: every unit, the PMU, the left plate and every far end is a "
        "judgement inside its 00-CAR zone box, confirm until the dash is measured (C4, V-102, "
        "V-113).",
        "The PMU stands for the dash node: every leg and drop meets it at the dash post (modules "
        "PMU: Dash node).",
        "A link is a straight line from connector to connector, not the wire's run: the harness "
        "drawings (D-385) stay the wire's truth.",
        "The boards show every part they draw, DNP ones too - the worst case the mock-ups' fit "
        "checks use.",
    ]
    seen = set()
    for l in links:
        if l["id"] in seen:
            raise Fail("two links share the id %s" % l["id"])
        seen.add(l["id"])
    order = list(dict.fromkeys(list(UNITS) + [k for u in UNITS.values() for k in u["children"]] +
                               ["cur-board", "pmu"]))
    out_parts = [parts[k] for k in order] + [nodes[k] for k in sorted(nodes)]
    scene = {
        "version": 1,
        "built": built,
        "project": "01-electrical",
        "frame": {"units": "mm", "x": "right", "y": "forward", "z": "up", "ruling": "D-418",
                  "glb": "mm, z up, the part's own frame (not glTF's metres, y up)",
                  "rotation": "degrees, three.js Euler order XYZ"},
        "parts": out_parts,
        "links": links,
        "missing": missing,
        "notes": notes,
        "assets": {k: metas[k] for k in ASSETS},
    }
    if out is not None:
        harness_v2(rec, scene, metas, out)
    return scene


# ======================================================================= version 2: the harness ==
def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _box_rot(box, place):
    """A part's own-frame box [lo, hi] turned by `place`'s rotation (not moved)."""
    lo, hi = box
    pts = [_rot([x, y, z], place) for x in (lo[0], hi[0]) for y in (lo[1], hi[1])
           for z in (lo[2], hi[2])]
    return [[min(p[k] for p in pts) for k in range(3)], [max(p[k] for p in pts) for k in range(3)]]


def _box_union(a, b):
    return [[min(a[0][k], b[0][k]) for k in range(3)], [max(a[1][k], b[1][k]) for k in range(3)]]


def _xyz(p):
    return {"x": round(p[0], 2), "y": round(p[1], 2), "z": round(p[2], 2)}


def _manifest(out, sub):
    path = os.path.join(out, sub, "manifest.json")
    if not os.path.exists(path):
        raise Fail("%s is not built: run export_glb.py --only %s" % (rel(path), sub))
    return json.load(open(path))


def _cavity_rows(cavs):
    return [{"cav": int(c.get("cav") or 0), "circuit": (c.get("circuit") or "").strip(),
             "awg": (c.get("awg") or "").strip(), "colour": (c.get("colour") or "").strip(),
             "state": (c.get("state") or "").strip()} for c in cavs]


def _plug_of(variant):
    """The plug that mates a DT13 PCB receptacle: a DT06 of the same ways (DT13-12PA -> DT06-12S)."""
    m = re.fullmatch(r"DT13-0?(\d+)PA", variant or "")
    return "DT06-%sS" % m.group(1) if m else None


def _pack(items, anchor, align="centre", within=None):
    """Lay boxes on a shelf: rows along +x wrapping at ROW_WRAP, rows stepping along +y, every
    box's underside on the anchor's z. items: [(key, [lo, hi] in the car's orientation, gap)].
    Returns {key: [tx, ty, tz]}, the translation for each item's origin; the block is centred on
    the anchor (align centre) or starts at its x (align left), centred on its y either way."""
    rows, row, w = [], [], 0.0
    for it in items:
        iw = it[1][1][0] - it[1][0][0]
        if row and w + iw > ROW_WRAP:
            rows.append(row)
            row, w = [], 0.0
        row.append(it)
        w += iw + it[2]
    if row:
        rows.append(row)
    rel_, y, width = {}, 0.0, 0.0
    for row in rows:
        x, depth = 0.0, 0.0
        for key, (lo, hi), gap in row:
            rel_[key] = [x - lo[0], y - lo[1], -lo[2]]
            x += hi[0] - lo[0] + gap
            depth = max(depth, hi[1] - lo[1])
        width = max(width, x - row[-1][2])
        y += depth + max(it[2] for it in row)
    depth_all = y - (max(it[2] for it in rows[-1]) if rows else 0.0)
    dx = anchor[0] - (width / 2.0 if align == "centre" else 0.0)
    if within:                                    # keep the shelf inside the car's width
        dx = max(within[0], min(dx, within[1] - width))
    dy = anchor[1] - depth_all / 2.0
    return {k: [v[0] + dx, v[1] + dy, v[2] + anchor[2]] for k, v in rel_.items()}


def _conn_part(code, half, variant, man, place, parent, place_from, leg, cavs, note):
    e = man.get(variant)
    if e is None:
        raise Fail("housing %s: no connector model for %s in connectors/manifest.json" % (code,
                                                                                     variant))
    other = "receptacle" if half == "plug" else "plug"
    return {"id": "%s:%s" % (code, half), "kind": "connector",
            "name": "%s %s · %s" % (code, half, variant), "family": variant, "half": half,
            "housing": code, "leg": leg, "glb": e["glb"], "bytes": e["bytes"], "parent": parent,
            "place": place, "place_from": place_from, "confirm": True,
            "place_note": note, "size_mm": e["size_mm"],
            "origin": "mating face centre; mate along +Y; wires along -Y",
            "mate": "%s:%s" % (code, other), "cavities": cavs, "connectors": [], "children": [],
            "source": "01-electrical housings %s; connectors/manifest.json %s (%s)"
                      % (code, variant, "stand-in" if e.get("standin") else "vendor model")}


def _mated(place):
    """The plug's place for a receptacle at `place`: the same, turned half a turn about its z."""
    p = dict(place)
    p["rz"] = ((p["rz"] + 180.0 + 180.0) % 360.0) - 180.0
    return p


def harness_v2(rec, scene, metas, out):
    """Grow a version-1 scene to version 2 (D-514, Y26): every housing's two halves, the devices
    at their nodes, the legs as paths. Adds parts and fields; changes none it finds."""
    cman = _manifest(out, "connectors")
    dman = _manifest(out, "devices")
    parts = {p["id"]: p for p in scene["parts"]}
    notes, new = scene["notes"], []
    cav_by = {}
    for cv in rec[("01-electrical", "cavities")]:
        cav_by.setdefault(cv["housing"], []).append(cv)
    for k in cav_by:
        cav_by[k].sort(key=lambda r: int(r.get("cav") or 0))
    housings = rec[("01-electrical", "housings")]

    # ---- the extra nodes
    for nid, (zone, box, f, name, why) in NODES_EXTRA.items():
        if nid in parts:
            continue
        at = _in_zone(rec, zone, f, box)
        n = {"id": nid, "name": name, "kind": "node", "glb": None, "bytes": 0, "parent": None,
             "place": _place(*at), "place_from": "provisional", "confirm": True,
             "place_note": "inside 00-CAR zones %s (box %d): %s" % (zone, box + 1, why),
             "size_mm": {"x": 0, "y": 0, "z": 0}, "origin": "the place itself",
             "connectors": [], "children": [], "source": "export_glb.py NODES_EXTRA"}
        parts[nid] = n
        new.append(n)

    # ---- a unit's receptacles at its rear face, each plug mated
    by_code = {h["code"]: h for h in housings}
    for uid in UNITS:
        for c in metas[uid].get("connectors", []):
            code = c["code"]
            h = by_code.get(code)
            rv = (h or {}).get("box_side") or c.get("part") or \
                (re.match(r"(DT13-\d+PA)", c.get("note", "")) or [None, None])[1]
            pv = (h or {}).get("leg_side") or _plug_of(rv)
            y = c.get("tip_y") if c.get("tip_y") is not None else c["at"][1]
            pl = _place(c["at"][0], y, c["at"][2])
            cavs = _cavity_rows(cav_by.get(code, []))
            note = ("the mock-up's cut-out at the receptacle's tip (%s's rear face)" % uid +
                    ("" if h else "; no housings row yet - no cavities (block 01.41)"))
            leg = (h or {}).get("leg", "")
            new.append(_conn_part(code, "receptacle", rv, cman, pl, uid, "mock-up report", leg,
                                  cavs, note))
            new.append(_conn_part(code, "plug", pv, cman, _mated(pl), uid, "mock-up report", leg,
                                  cavs, note))

    # ---- the dash post: a cluster of receptacles beside the PMU, a row per leg
    pmu = parts["pmu"]
    pb = metas["pmu"]["bbox"]
    pp = pmu["place"]
    plo = [pp["x"] + pb[0][0], pp["y"] + pb[0][1], pp["z"] + pb[0][2]]
    phi = [pp["x"] + pb[1][0], pp["y"] + pb[1][1], pp["z"] + pb[1][2]]
    pc = [(plo[k] + phi[k]) / 2.0 for k in range(3)]
    rec_rot, plug_rot = _place(rz=180), _place()
    rows = []
    for lid in ("L1", "L2", "L3", "L4"):
        row = [h for h in housings if (h.get("where") or "").strip() == "Dash post" and
               (h.get("leg") or "").startswith(LEG_NAMES[lid])]
        if row:
            rows.append((lid, row))
    post_codes = {h["code"] for _, r in rows for h in r}
    stray = [h["code"] for h in housings if (h.get("where") or "").strip() == "Dash post" and
             h["code"] not in post_codes]
    if stray:
        raise Fail("dash-post housings on no leg row: %s" % ", ".join(stray))

    def pair_box(h, rrot, prot):
        rb = _box_rot(cman[h["box_side"]]["bbox_mm"], rrot)
        qb = _box_rot(cman[h["leg_side"]]["bbox_mm"], prot)
        return _box_union(rb, qb)

    for h in housings:
        for v in (h.get("box_side"), h.get("leg_side")):
            if v not in cman:
                raise Fail("housing %s: no connector model for %s in connectors/manifest.json"
                           % (h["code"], v))
    heights = [max(pair_box(h, rec_rot, plug_rot)[1][2] - pair_box(h, rec_rot, plug_rot)[0][2]
                   for h in r) for _, r in rows]
    total_h = sum(heights) + CLUSTER_GAP * (len(rows) - 1)
    z_top = pc[2] + total_h / 2.0
    right = plo[0] - 40.0
    starts = {}
    for (lid, row), rh in zip(rows, heights):
        boxes = [pair_box(h, rec_rot, plug_rot) for h in row]
        width = sum(b[1][0] - b[0][0] for b in boxes) + CLUSTER_GAP * (len(row) - 1)
        x = right - width
        zc = z_top - rh / 2.0
        for h, b in zip(row, boxes):
            tx = x - b[0][0]
            pl = _place(tx, pc[1], zc - (b[0][2] + b[1][2]) / 2.0, rz=180)
            cavs = _cavity_rows(cav_by.get(h["code"], []))
            note = "the dash post's cluster beside the PMU, row %s (provisional)" % lid
            new.append(_conn_part(h["code"], "receptacle", h["box_side"], cman, pl, None,
                                  "provisional", h.get("leg", ""), cavs, note))
            new.append(_conn_part(h["code"], "plug", h["leg_side"], cman, _mated(pl), None,
                                  "provisional", h.get("leg", ""), cavs, note))
            x += b[1][0] - b[0][0] + CLUSTER_GAP
        y_out = pc[1] + min(pair_box(h, rec_rot, plug_rot)[0][1] for h in row)
        starts[lid] = [right - width / 2.0, y_out, zc]
        z_top -= rh + CLUSTER_GAP
    notes.append("The dash post is a cluster of receptacles beside the PMU, a row per leg "
                 "(L1 at the top), %d mm apart, each plug mated, facing the cabin - a judgement "
                 "until the post is designed and measured." % CLUSTER_GAP)

    # ---- far ends (D-583): each device at its SPOT, else on its node's shelf; each housing beside
    #      the device that names it in devices.plug when that device has a SPOT, else on the shelf
    node_items, where_node = {}, {}
    for key, v in WHERE.items():
        where_node[key] = v[0]
    far = []
    for h in housings:
        where = (h.get("where") or "").strip()
        if where == "Dash post" or any(where.startswith(k) for k in UNIT_OF):
            continue
        nid = where_node.get(where)
        if nid is None or nid not in parts:
            raise Fail("housing %s: where %r has no node in the scene" % (h["code"], where))
        far.append((h, nid))

    models = dman.get("_meta", {}).get("models", {})
    unplaced, dev_at = [], []
    for key in sorted(k for k in dman if not k.startswith("_")):
        e = dman[key]
        spots = [(MOVE_DEVICES.get(key, e.get("node")), e.get("count", 1))]
        spots += [(a.get("node"), a.get("count", 1)) for a in e.get("also", [])]
        total = sum(c for _, c in spots if c)
        if not total:
            unplaced.append({"device": key, "why": "count 0: %s" % (e.get("node_note") or
                                                                     "drawn by another entry")})
            continue
        box = (models.get(e.get("model"), {}) or {}).get("bbox")
        if box is None:
            unplaced.append({"device": key, "why": "its model has no box in the manifest"})
            continue
        i = 0
        for nid, count in spots:
            for _ in range(count or 0):
                i += 1
                pid = "dev-%s%s" % (_slug(key), "-%d" % i if total > 1 else "")
                if nid not in parts:
                    unplaced.append({"device": key, "why": "its node %r is not in the scene"
                                     % nid})
                    continue
                kind = parts[nid]["kind"]
                if kind in ("pcb", "unit"):
                    unplaced.append({"device": key, "why": "inside %s: that part's glb draws it"
                                     % nid})
                    continue
                at = SPOTS.get(key, [])
                spot = list(at[i - 1]) if i <= len(at) else None
                dev_at.append((pid, key, e, nid, i, total, spot, box))
                if spot is None:
                    node_items.setdefault(nid, []).append(("dev:" + pid, box, DEVICE_GAP))
    if any(k in dman and MOVE_DEVICES[k] != dman[k].get("node") for k in MOVE_DEVICES):
        notes.append("The battery, disconnect, Class-T, MRBF holders and amplifier are moved to "
                     "the passenger-side cargo bin (D-449); the devices builder had no node for it.")

    # a housing named in a placed device's devices.plug sits beside that device
    devrows = {d["id"]: d for d in rec[("01-electrical", "devices")]}
    codes = sorted((h["code"] for h in housings), key=len, reverse=True)
    code_re = re.compile(r"(?<![\w-])(%s)(?![\w-])" % "|".join(re.escape(c) for c in codes))
    beside, paired = {}, set()
    for pid, key, e, nid, i, total, spot, box in dev_at:
        if key not in devrows:
            continue
        named = [c for c in code_re.findall(devrows[key].get("plug") or "")
                 if any(h["code"] == c for h, _ in far)]
        if named:
            paired.add(key)                       # its conductors arrive on that housing
        if spot is None:
            continue
        for k, c in enumerate(dict.fromkeys(named)):
            if c in beside:
                continue
            w = (box[1][0] - box[0][0]) / 2.0 + 45.0
            side = -1.0 if spot[0] > 0 else 1.0           # toward the car's centre line
            beside[c] = [spot[0] + side * w, spot[1] - 55.0 * k, spot[2] + 15.0]
    for h, nid in far:
        if h["code"] in beside:
            continue
        box = _box_union(_box_rot(cman[h["box_side"]]["bbox_mm"], _place()),
                         _box_rot(cman[h["leg_side"]]["bbox_mm"], _place(rz=180)))
        node_items.setdefault(nid, []).append(("conn:" + h["code"], box, NODE_GAP))

    cb = _zone_box(rec, "cabin")
    cabin_x = (cb[0], cb[1])
    shelf = {}
    for nid, items in node_items.items():
        if nid == "pmu":                            # the dash node's parts: a shelf right of the PMU
            shelf.update(_pack(items, [phi[0] + 40.0, pc[1], plo[2]], align="left"))
        else:
            n = parts[nid]["place"]
            shelf.update(_pack(items, [n["x"], n["y"], n["z"]], within=cabin_x))
    for h, nid in far:
        if h["code"] in beside:
            pl = _place(*beside[h["code"]])
            note = ("beside the device that takes it (devices.plug), at its spot (D-583, "
                    "provisional)")
        else:
            pl = _place(*shelf["conn:" + h["code"]])
            note = "at its far end, node %s, beside the others there (provisional)" % nid
        cavs = _cavity_rows(cav_by.get(h["code"], []))
        new.append(_conn_part(h["code"], "receptacle", h["box_side"], cman, pl, None,
                              "provisional", h.get("leg", ""), cavs, note))
        new.append(_conn_part(h["code"], "plug", h["leg_side"], cman, _mated(pl), None,
                              "provisional", h.get("leg", ""), cavs, note))
    for pid, key, e, nid, i, total, spot, box in dev_at:
        t = spot if spot is not None else shelf["dev:" + pid]
        new.append({
            "id": pid, "name": e["name"] + ("" if total == 1 else " (%d of %d)" % (i, total)),
            "kind": "module", "device": key, "node": nid, "glb": e["glb"], "bytes": e["bytes"],
            "parent": None, "place": _place(*t), "place_from": "provisional", "confirm": True,
            "place_note": ("where it is fitted, a judgement (SPOTS, D-583; provisional)"
                           if spot is not None else
                           "at node %s, on a shelf with the others there (provisional)" % nid),
            "size_mm": e["size_mm"], "origin": e.get("origin", ""), "connectors": [],
            "children": [], "standin": e.get("standin"), "cad": e.get("cad"),
            "source": "devices/manifest.json %s (%s)" % (key, e.get("source", ""))})
    notes.append("Devices stand where they are fitted (SPOTS in export_glb.py, judgement) and a "
                 "housing named in such a device's devices.plug beside it; the rest stand on a "
                 "shelf centred on their node, %d mm apart (the devices %d), rows wrapping at %d mm "
                 "- the dash node's relays and fuses, the sill node's, the seats', the speakers'."
                 % (NODE_GAP, DEVICE_GAP, ROW_WRAP))
    for p in new:
        parts[p["id"]] = p

    # ---- the legs (D-583): each a taped trunk along the body (TRUNKS), thinning at every
    #      breakout, and a breakout per housing and device it feeds, ending on that part
    def world(p, local=(0.0, 0.0, 0.0)):
        q = [p["place"]["x"], p["place"]["y"], p["place"]["z"]]
        v = _rot(list(local), p["place"])
        v = [q[k] + v[k] for k in range(3)]
        if p.get("parent"):
            return world(parts[p["parent"]], v)
        return v

    def wire_end(p):
        """Where a plug's wires leave it: its rear face, on its axis (wires along its -Y)."""
        lo = cman[p["family"]]["bbox_mm"][0]
        return world(p, (0.0, lo[1] - 8.0, 0.0))

    def ok_awg(a):
        a = (a or "").split()[0] if (a or "").split() else "16"
        return AWG_OD.get(a, AWG_OD["16"])

    def bundle_r(awgs):
        if not awgs:
            return BUNDLE_MIN_R
        return round(max(BUNDLE_MIN_R, BUNDLE_K * math.sqrt(sum(ok_awg(a) ** 2 for a in awgs))
                         / 2.0), 1)

    def wired(code, all_=False):
        return [c.get("awg") for c in cav_by.get(code, [])
                if (c.get("circuit") or "").strip() and
                ((c.get("state") or "") in WIRED or (all_ and c.get("state") == "RESERVED"))]

    route_leg = {r["id"]: ROUTE_LEG.get((r.get("leg") or "").strip())
                 for r in rec[("01-electrical", "routes")]}

    def leg_of_housing(h):
        for c in cav_by.get(h["code"], []):
            lg = route_leg.get((c.get("route") or "").strip())
            if lg:
                return lg
        for d in devrows.values():
            if h["code"] in code_re.findall(d.get("plug") or "") and route_leg.get(d.get("route")):
                return route_leg[d["route"]]
        return HOUSING_LEG.get((h.get("leg") or "").strip())

    items = {lid: [] for lid in TRUNKS}             # (part id, target, awgs, housing code)
    by_code = {h["code"]: h for h in housings}
    for h, nid in far:
        lg = leg_of_housing(h)
        if lg is None:
            continue
        items[lg].append(("%s:plug" % h["code"], wire_end(parts["%s:plug" % h["code"]]),
                          wired(h["code"], h.get("class") == "Door"), h["code"]))
    for p in new:
        if p.get("half") == "plug" and p.get("parent") in UNIT_LEG and p["housing"] in by_code:
            items[UNIT_LEG[p["parent"]]].append((p["id"], wire_end(p), wired(p["housing"]),
                                                 p["housing"]))
    for pid, key, e, nid, i, total, spot, box in dev_at:
        d = devrows.get(key)
        if d is None or key in paired or not route_leg.get(d.get("route")):
            continue
        n = max(2, len([t for t in re.split(r"<br>|\n", d.get("terminals") or "") if t.strip()]))
        p = parts[pid]
        h = min(30.0, (box[1][2] - box[0][2]) / 2.0)
        items[route_leg[d["route"]]].append((pid, [p["place"]["x"], p["place"]["y"],
                                                   p["place"]["z"] + h], ["16"] * n, None))
    for nid, code in DOOR_ITEMS:
        if nid in parts and code in by_code:
            n = parts[nid]["place"]
            items["L4"].append((nid, [n["x"], n["y"], n["z"]], wired(code, True), code))

    def manhattan(a, b):
        return sum(abs(a[k] - b[k]) for k in range(3))

    def nearest(seg_a, seg_b, t):
        d = [seg_b[k] - seg_a[k] for k in range(3)]
        dd = sum(x * x for x in d)
        u = 0.0 if dd == 0 else max(0.0, min(1.0, sum((t[k] - seg_a[k]) * d[k]
                                                    for k in range(3)) / dd))
        return u, [seg_a[k] + u * d[k] for k in range(3)]

    def ortho(a, b, trunk=False):
        """a -> b in straight runs along the car's axes (D-583: never across open air): down
        first and then along, or along first and up last, so a bundle lies on the lower
        surface; a breakout that climbs far behind the dash goes by the side wall."""
        a, b = list(a), list(b)
        behind = a[1] < -1092 or b[1] < -1092
        if not trunk and behind and abs(b[2] - a[2]) > WALL_RISE:
            side = 1.0 if (b[0] if abs(b[0]) > 50 else a[0]) >= 0 else -1.0
            wx = side * WALL_X
            pts = [a, [wx, a[1], a[2]], [wx, b[1], a[2]], [wx, b[1], b[2]], b]
        elif b[2] < a[2]:
            pts = [a, [a[0], a[1], b[2]], [a[0], b[1], b[2]], b]
        else:
            pts = [a, [a[0], b[1], a[2]], [b[0], b[1], a[2]], b]
        out = [pts[0]]
        for q in pts[1:]:
            if manhattan(q, out[-1]) > 1.0:
                out.append(q)
        if len(out) == 1:
            out.append(list(b))
        return out

    def fillet(pts, fixed, r=BREAKOUT_BEND):
        """Round each corner that is not a fixed point; returns the points and, for each input
        index, its index in the output (fixed points keep theirs exactly)."""
        out, where = [list(pts[0])], {0: 0}
        for k in range(1, len(pts) - 1):
            a, v, b = pts[k - 1], pts[k], pts[k + 1]
            da = [a[j] - v[j] for j in range(3)]
            db = [b[j] - v[j] for j in range(3)]
            la, lb = math.sqrt(sum(x * x for x in da)), math.sqrt(sum(x * x for x in db))
            cos = (sum(da[j] * db[j] for j in range(3)) / (la * lb)) if la and lb else -1.0
            if k in fixed or cos < -0.999 or not la or not lb:
                where[k] = len(out)
                out.append(list(v))
                continue
            rr = min(r, 0.45 * la, 0.45 * lb)
            p1 = [v[j] + da[j] * rr / la for j in range(3)]
            p2 = [v[j] + db[j] * rr / lb for j in range(3)]
            for s in (0.0, 0.25, 0.5, 0.75, 1.0):
                out.append([(1 - s) ** 2 * p1[j] + 2 * (1 - s) * s * v[j] + s * s * p2[j]
                            for j in range(3)])
            where[k] = len(out) - 3
        where[len(pts) - 1] = len(out)
        out.append(list(pts[-1]))
        return out, where

    legs, taken = [], set()
    routes = rec[("01-electrical", "routes")]
    for lid, tr in TRUNKS.items():
        start = list(tr["start"]) if "start" in tr else starts.get(lid)
        if start is None:
            raise Fail("leg %s has no row at the dash post" % lid)
        polys = [[list(start)] + [list(q) for q in tr["main"]]]
        parent = [None]
        for (frm, at), pts in tr["subs"]:
            k = 0 if frm == "main" else int(frm) + 1
            if k >= len(polys) or at >= len(polys[k]):
                raise Fail("leg %s: a sub-trunk leaves (%s, %s), not on its trunk" % (lid, frm, at))
            polys.append([list(polys[k][at])] + [list(q) for q in pts])
            parent.append((k, at))
        # every trunk run along the car's axes too: each pair of its points squared off
        sq, smap = [], []
        for poly in polys:
            out, m = [list(poly[0])], {0: 0}
            for j in range(1, len(poly)):
                out += ortho(poly[j - 1], poly[j], trunk=True)[1:]
                m[j] = len(out) - 1
            sq.append(out)
            smap.append(m)
        parent = [None] + [(pk, smap[pk][pat]) for (pk, pat) in parent[1:]]
        polys = sq
        # each item's attach point: the trunk point nearest it, by the run its breakout must make
        taps = [[] for _ in polys]                  # (poly vertex index after insertion, awgs)
        att = []
        for it in items[lid]:
            best = None
            for k, poly in enumerate(polys):
                for j in range(len(poly) - 1):
                    u, q = nearest(poly[j], poly[j + 1], it[1])
                    c = manhattan(q, it[1])
                    if best is None or c < best[0] - 1e-6:
                        best = (c, k, j, u, q)
            att.append((it, best))
        # insert the attach points into their trunks, in order along each segment
        ins = {}
        for n_, (it, (c, k, j, u, q)) in enumerate(att):
            ins.setdefault((k, j), []).append((u, n_, q))
        new_polys, vmap = [], []
        for k, poly in enumerate(polys):
            out, m = [], {}
            for j, v in enumerate(poly):
                m[j] = len(out)
                out.append(v)
                for u, n_, q in sorted(ins.get((k, j), [])):
                    if u <= 1e-6:
                        att[n_] = (att[n_][0], (None, k, len(out) - 1))
                    elif u >= 1 - 1e-6 and j + 1 < len(poly):
                        att[n_] = (att[n_][0], (None, k, ("next", j + 1)))
                    else:
                        att[n_] = (att[n_][0], (None, k, len(out)))
                        out.append(q)
            new_polys.append(out)
            vmap.append(m)
        for n_, (it, a) in enumerate(att):
            k, ix = a[1], a[2]
            if isinstance(ix, tuple):
                ix = vmap[k][ix[1]]
            att[n_] = (it, (k, ix))
        sub_at = [None] + [(pk, vmap[pk][pat]) for (pk, pat) in parent[1:]]
        for n_, (it, (k, ix)) in enumerate(att):
            taps[k].append((ix, list(it[2])))
        # what each sub-trunk carries, the last first (a sub only leaves an earlier trunk)
        carried = [None] * len(new_polys)
        for k in range(len(new_polys) - 1, -1, -1):
            awgs = [a for (_, aw) in taps[k] for a in aw]
            for s in range(k + 1, len(new_polys)):
                if sub_at[s] and sub_at[s][0] == k:
                    awgs += carried[s]
            carried[k] = awgs
        for s in range(1, len(new_polys)):
            taps[sub_at[s][0]].append((sub_at[s][1], list(carried[s])))
        # fillet each trunk (taps and sub starts stay exact), then cut it into runs of one
        # thickness: a segment carries every tap beyond its start
        runs, trunk_paths = [], []
        for k, poly in enumerate(new_polys):
            fixed = {ix for ix, _ in taps[k]} | {0, len(poly) - 1}
            fp, where = fillet(poly, fixed)
            trunk_paths.append(fp)
            cuts = sorted({where[ix] for ix, _ in taps[k]} | {0, len(fp) - 1})
            for a, b in zip(cuts, cuts[1:]):
                if b <= a:
                    continue
                aw = [x for ix, awl in taps[k] if where[ix] > a for x in awl]
                runs.append({"path": [_xyz(q) for q in fp[a:b + 1]], "radius_mm": bundle_r(aw),
                             "conductors": len(aw)})
            # re-key this trunk's taps to the filleted points for the breakouts below
            taps[k] = [(where[ix], aw) for ix, aw in taps[k]]
            for n_, (it, a) in enumerate(att):
                if len(a) == 2 and a[0] == k:
                    att[n_] = (it, (k, where[a[1]], True))
        branches = []
        for s in range(1, len(trunk_paths)):
            branches.append({"to": "", "kind": "trunk",
                             "path": [_xyz(q) for q in trunk_paths[s]],
                             "radius_mm": bundle_r(carried[s]), "conductors": len(carried[s])})
        for it, (k, ix, _) in att:
            a = trunk_paths[k][ix]
            bp, _ = fillet(ortho(a, it[1]), set())
            branches.append({"to": it[0], "kind": "breakout", "housing": it[3] or "",
                             "path": [_xyz(q) for q in bp], "radius_mm": bundle_r(it[2]),
                             "conductors": len(it[2])})
            if it[3]:
                taken.add(it[3])
        hs = [h for h in housings if (h.get("where") or "").strip() == "Dash post" and
              (h.get("leg") or "").startswith(LEG_NAMES[lid])]
        for h in hs:
            taken.add(h["code"])
        live = [c.get("awg") for h in hs for c in cav_by.get(h["code"], [])
                if (c.get("state") or "") in WIRED and (c.get("circuit") or "").strip()]
        root = carried[0] if len(carried[0]) >= len(live) else live
        legs.append({
            "id": lid, "name": LEG_NAMES[lid], "path": [_xyz(q) for q in trunk_paths[0]],
            "branches": branches, "runs": runs, "radius_mm": bundle_r(root),
            "conductors": len(root), "housings": [h["code"] for h in hs] +
            [it[3] for it, _ in att if it[3]],
            "routes": [r["id"] for r in routes if ROUTE_LEG.get((r.get("leg") or "").strip()) == lid],
            "wrap": TAPE, "place_from": "provisional", "confirm": True,
            "note": "the trunk is a judgement along the body (TRUNKS); each breakout a run along "
                    "the car's axes from the trunk point nearest its part; thickness from the "
                    "conductors still in the bundle (AWG_OD, confirm)"})
    left = [h["code"] for h in housings if h["code"] not in taken]
    if left:
        notes.append("Housings no leg reaches (drawn at their node, on no leg's list): %s."
                     % ", ".join(left))
    notes.append("Each leg is drawn as it will be built (D-583): a taped trunk from the dash post "
                 "along the body - the firewall, the dash rail, the tunnel's sides, the sills, the "
                 "inner wing, the hinge loop (TRUNKS in export_glb.py, judgement) - and from it a "
                 "breakout to each housing and device, in straight runs along the car's axes and "
                 "up the side wall where it climbs behind the dash, bent round %d mm. A run's "
                 "thickness is 1.2 x the root of the sum of its conductors' squared diameters "
                 "(TXL-class, confirm), so the trunk thins as each breakout leaves it. The Audio "
                 "runs (RT30-RT32) are a leg of their own from the head unit; a link is data "
                 "(what mates what), not drawn." % BREAKOUT_BEND)

    order = [p["id"] for p in scene["parts"]]
    scene["parts"] = [parts[k] for k in order] + new
    scene["version"] = 2
    scene["legs"] = legs
    scene["unplaced"] = unplaced
    scene["manifests"] = {"connectors": "connectors/manifest.json",
                          "devices": "devices/manifest.json"}


def board_part(rec, bid, m, parent, place, place_from, confirm):
    table, key = BOARDS[bid][1], BOARDS[bid][2]
    return {"id": bid, "name": _name(rec, table, key), "kind": "pcb", "glb": m["glb"],
            "bytes": m["bytes"], "parent": parent, "place": place, "place_from": place_from,
            "confirm": confirm, "size_mm": _size(m), "origin": m["origin"], "connectors": [],
            "children": [], "source": m["source"], "nodes": m["nodes"]}


def child_place(kid, um, km, notes):
    """A board's place in its unit, from the mock-up's own numbers (um, written by
    export_glb_fc.py from the mock-up's derive()) and the board's outline."""
    o = km["outline"]
    bc = [(o[0] + o[1]) / 2.0, (o[2] + o[3]) / 2.0]
    b = um["boards"]
    if kid in ("cu-carrier", "du-carrier"):
        mv, turn = b["carrier"]["move"], b["carrier"]["turn"]
        return _place(mv[0], mv[1], mv[2], rz=turn)
    if kid in ("cu-face-board", "cur-board"):    # a board standing behind its unit's face
        x0, x1, y0, y1, z0, z1 = b["panel" if kid == "cu-face-board" else "plate"]
        return _place((x0 + x1) / 2.0 - bc[0], y1, (z0 + z1) / 2.0 - bc[1], rx=90)
    raise Fail("no rule places %s in its unit" % kid)


# ============================================================================== the selftest ==
def validate_scene(path):
    """The contract, version 1 and 2. Returns a list of problems (empty when it holds)."""
    bad = []
    try:
        s = json.load(open(path))
    except Exception as e:
        return ["%s does not read as JSON: %s" % (path, e)]
    base = os.path.dirname(path)
    for k in ("version", "built", "project", "frame", "parts", "links", "missing", "notes"):
        if k not in s:
            bad.append("no %r" % k)
    if bad:
        return bad
    if s["version"] not in (1, 2):
        bad.append("version is %r, not 1 or 2" % s["version"])
    try:
        datetime.datetime.fromisoformat(s["built"])
    except Exception:
        bad.append("built %r is not ISO 8601" % s["built"])
    f = s["frame"]
    if (f.get("units"), f.get("x"), f.get("y"), f.get("z")) != ("mm", "right", "forward", "up"):
        bad.append("frame is not mm / right / forward / up")
    ids, conns = {}, {}
    for p in s["parts"]:
        pid = p.get("id")
        if not pid or not (re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", pid) or (
                p.get("kind") == "connector" and
                re.fullmatch(r"[A-Za-z0-9]+(-[A-Za-z0-9]+)*:(plug|receptacle)", pid))):
            bad.append("part id %r is not kebab-case (or <housing>:<half>)" % pid)
        if pid in ids:
            bad.append("part id %s twice" % pid)
        ids[pid] = p
        conns[pid] = {c.get("code") for c in p.get("connectors", [])}
        if p.get("kind") not in ("unit", "pcb", "module", "node", "connector"):
            bad.append("%s: kind %r" % (pid, p.get("kind")))
        pl = p.get("place", {})
        if sorted(pl) != sorted("x y z rx ry rz".split()) or not all(
                isinstance(pl[k], (int, float)) and not isinstance(pl[k], bool) for k in pl):
            bad.append("%s: place is not six numbers" % pid)
        if not isinstance(p.get("confirm"), bool):
            bad.append("%s: confirm is not true / false" % pid)
        if p.get("place_from") is None:
            bad.append("%s: no place_from" % pid)
        if p.get("kind") == "node":
            if p.get("glb") is not None:
                bad.append("%s: a node with a glb" % pid)
        else:
            g = p.get("glb")
            if not g:
                bad.append("%s: no glb" % pid)
            else:
                gp = os.path.join(base, g)
                if not os.path.exists(gp):
                    bad.append("%s: %s is not there" % (pid, g))
                elif os.path.getsize(gp) != p.get("bytes"):
                    bad.append("%s: %s is %d bytes, the scene says %s"
                               % (pid, g, os.path.getsize(gp), p.get("bytes")))
        sz = p.get("size_mm", {})
        if sorted(sz) != ["x", "y", "z"]:
            bad.append("%s: size_mm is not x y z" % pid)
        for c in p.get("connectors", []):
            at = c.get("at", {})
            if sorted(at) != ["x", "y", "z"] or not c.get("code"):
                bad.append("%s: a connector without a code or an x y z" % pid)
    for p in s["parts"]:
        par = p.get("parent")
        if par is not None and par not in ids:
            bad.append("%s: parent %s is no part" % (p["id"], par))
        for ch in p.get("children", []):
            if ch not in ids:
                bad.append("%s: child %s is no part" % (p["id"], ch))
            elif ids[ch].get("parent") != p["id"]:
                bad.append("%s: child %s names another parent" % (p["id"], ch))
    lids = set()
    for l in s["links"]:
        if l.get("id") in lids:
            bad.append("link id %s twice" % l.get("id"))
        lids.add(l.get("id"))
        for end in ("from", "to"):
            e = l.get(end, {})
            if e.get("part") not in ids:
                bad.append("link %s: %s part %s is no part" % (l.get("id"), end, e.get("part")))
            elif e.get("connector") not in conns[e["part"]]:
                bad.append("link %s: %s has no connector %s" % (l.get("id"), e["part"],
                                                                e.get("connector")))
        if not isinstance(l.get("ways"), int) or not isinstance(l.get("carries"), list):
            bad.append("link %s: ways or carries malformed" % l.get("id"))
    for m in s["missing"]:
        if m.get("part") not in ids:
            bad.append("missing names %s, no part" % m.get("part"))
    if s["version"] == 2:
        bad += _validate_v2(s, base, ids)
    return bad


def _validate_v2(s, base, ids):
    """Version 2 on top of version 1: connectors, mates, places, legs, the devices placed."""
    bad = []
    for k in ("legs", "unplaced", "manifests"):
        if k not in s:
            bad.append("version 2 without %r" % k)
    if bad:
        return bad
    try:
        cman = json.load(open(os.path.join(base, s["manifests"]["connectors"])))
        dman = json.load(open(os.path.join(base, s["manifests"]["devices"])))
    except Exception as e:
        return ["a manifest does not read: %s" % e]
    for p in s["parts"]:
        if p.get("kind") != "connector":
            continue
        e = cman.get(p.get("family"))
        if e is None or e.get("glb") != p.get("glb"):
            bad.append("%s: %s is not its family's glb in connectors/manifest.json"
                       % (p["id"], p.get("glb")))
        if p.get("half") not in ("plug", "receptacle"):
            bad.append("%s: half %r" % (p["id"], p.get("half")))
        m = ids.get(p.get("mate"))
        if m is None or m.get("mate") != p["id"] or m.get("half") == p.get("half"):
            bad.append("%s: its mate %s does not name it back" % (p["id"], p.get("mate")))
        if not isinstance(p.get("cavities"), list):
            bad.append("%s: cavities is not a list" % p["id"])
    seen = {}
    for p in s["parts"]:
        if p.get("kind") == "node":
            continue
        pl = p.get("place", {})
        key = (p.get("parent"), round(pl.get("x", 0)), round(pl.get("y", 0)),
               round(pl.get("z", 0)))
        other = seen.get(key)
        if other is not None and other.get("mate") != p["id"]:
            bad.append("%s and %s share a place" % (other["id"], p["id"]))
        seen.setdefault(key, p)
    for lg in s["legs"]:
        path = lg.get("path", [])
        if len(path) < 2:
            bad.append("leg %s: fewer than two points" % lg.get("id"))
        pts = {(q["x"], q["y"], q["z"]) for q in path}
        for b in lg.get("branches", []):        # a branch leaves the path or an earlier branch
            bp = b.get("path", [])
            if len(bp) < 2:
                bad.append("leg %s: a branch to %s has fewer than two points" % (lg.get("id"),
                                                                              b.get("to")))
            elif (bp[0]["x"], bp[0]["y"], bp[0]["z"]) not in pts:
                bad.append("leg %s: the branch to %s does not start on the path"
                           % (lg.get("id"), b.get("to")))
            if b.get("kind") != "trunk" and b.get("to") not in ids:
                bad.append("leg %s: a branch to %s, no part" % (lg.get("id"), b.get("to")))
            if "radius_mm" in b and not (isinstance(b["radius_mm"], (int, float)) and
                                         b["radius_mm"] > 0):
                bad.append("leg %s: a branch to %s with no radius" % (lg.get("id"), b.get("to")))
            pts |= {(q["x"], q["y"], q["z"]) for q in bp}
        for r in lg.get("runs", []):
            if len(r.get("path", [])) < 2 or not r.get("radius_mm", 0) > 0:
                bad.append("leg %s: a run with fewer than two points or no radius" % lg.get("id"))
        if not (isinstance(lg.get("radius_mm"), (int, float)) and lg["radius_mm"] > 0):
            bad.append("leg %s: no radius" % lg.get("id"))
    placed = {p.get("device") for p in s["parts"] if p.get("device")}
    reasons = {u.get("device") for u in s["unplaced"]}
    for k in dman:
        if not k.startswith("_") and k not in placed and k not in reasons:
            bad.append("device %s is neither placed nor given a reason" % k)
    return bad


def selftest(path):
    """The contract check, run on the output and on broken copies of it (each must refuse); and
    the board reader's footprint lookup on a two-footprint snippet."""
    fp_bad = _selftest_footprint_at()
    for b in fp_bad:
        print("  footprint: " + b)
    print("  %-34s %s" % ("footprint places, two footprints", "FAIL" if fp_bad else "ok"))
    if fp_bad:
        return 1
    pl_bad = _selftest_saved_place()
    for b in pl_bad:
        print("  place: " + b)
    print("  %-34s %s" % ("saved places (D-520)", "FAIL" if pl_bad else "ok"))
    if pl_bad:
        return 1
    probs = validate_scene(path)
    if probs:
        for p in probs:
            print("  scene: " + p)
        return 1
    s = json.load(open(path))
    cases = []
    t = json.loads(json.dumps(s))
    t["parts"].append(dict(t["parts"][0]))
    cases.append(("a duplicate id", t))
    t = json.loads(json.dumps(s))
    t["parts"][1]["parent"] = "no-such-part"
    cases.append(("a parent that does not exist", t))
    t = json.loads(json.dumps(s))
    t["links"][0]["to"]["part"] = "no-such-part"
    cases.append(("a link end that does not exist", t))
    t = json.loads(json.dumps(s))
    t["parts"][0]["bytes"] += 1
    cases.append(("a glb of other bytes", t))
    t = json.loads(json.dumps(s))
    del t["parts"][0]["place"]["rz"]
    cases.append(("a place of five numbers", t))
    if s.get("version") == 2:
        conn = [i for i, p in enumerate(s["parts"]) if p.get("kind") == "connector"]
        dev = [i for i, p in enumerate(s["parts"]) if p.get("device")]
        t = json.loads(json.dumps(s))
        t["parts"][conn[0]]["mate"] = t["parts"][conn[2]]["id"]
        cases.append(("a mate that does not name it back", t))
        t = json.loads(json.dumps(s))
        t["parts"][conn[0]]["glb"] = "connectors/NO-SUCH.glb"
        cases.append(("a connector glb not in the manifest", t))
        t = json.loads(json.dumps(s))
        a, b = t["parts"][dev[0]], t["parts"][dev[1]]
        b["parent"], b["place"] = a["parent"], dict(a["place"])
        cases.append(("two parts at one place", t))
        t = json.loads(json.dumps(s))
        t["legs"][0]["path"] = t["legs"][0]["path"][:1]
        cases.append(("a leg of one point", t))
        t = json.loads(json.dumps(s))
        lg = next(x for x in t["legs"] if x["branches"])
        lg["branches"][0]["path"][0]["x"] += 50
        cases.append(("a branch that starts off the path", t))
        t = json.loads(json.dumps(s))
        key = t["parts"][dev[0]]["device"]
        t["parts"] = [p for p in t["parts"] if p.get("device") != key]
        t["unplaced"] = [u for u in t["unplaced"] if u.get("device") != key]
        cases.append(("a device neither placed nor excused", t))
    rc = 0
    base = os.path.dirname(os.path.abspath(path))
    for what, t in cases:
        tmp = os.path.join(base, ".selftest-scene.json")
        try:
            with open(tmp, "w") as fh:
                json.dump(t, fh)
            got = validate_scene(tmp)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        print("  %-34s %s" % (what, "refused" if got else "NOT REFUSED"))
        rc |= 0 if got else 1
    print("selftest: %s (the scene holds; %d broken copies, %d refused)"
          % ("pass" if rc == 0 else "FAIL", len(cases), len(cases) - rc))
    return rc


# ==================================================================================== the run ==
class _Args(argparse.ArgumentParser):
    def error(self, message):                     # a usage error is rc 3 here, not argparse's 2
        self.print_usage(sys.stderr)
        print("export_glb: %s" % message, file=sys.stderr)
        sys.exit(3)


def main(argv):
    ap = _Args(description=__doc__.split("\n\n")[0],
               formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--only", choices=ASSETS + STEPS + ["legs", "scene"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", nargs="?", const="", metavar="SCENE")
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out)
    scene_path = os.path.join(out, "scene.json")
    if a.selftest is not None:
        return selftest(a.selftest or scene_path)
    old = json.load(open(scene_path)) if os.path.exists(scene_path) else None
    stamps = {aid: _hash_files(source_files(aid)) for aid in ASSETS}

    if a.check:
        if old is None:
            print("scene.json is not there: build with export_glb.py")
            return 2
        rc, absent = 0, False
        for aid in ASSETS:
            m = old.get("assets", {}).get(aid)
            g = os.path.join(out, aid + ".glb")
            if not os.path.exists(g):
                print("%-14s not built here" % aid)
                absent = True
            elif m is None or os.path.getsize(g) != m["bytes"]:
                print("%-14s does not match scene.json" % aid)
                rc = 1
            elif m.get("stamp") != stamps[aid]:
                print("%-14s stale: its sources changed since it was built" % aid)
                rc = 1
            else:
                print("%-14s current" % aid)
        rec_stamp = _record_stamp(read_record())
        if old.get("record_stamp") != rec_stamp:
            print("scene.json     stale: the record's housings, cavities or places changed")
            rc = 1
        for step in STEPS:
            r = run_step(step, out, check=True)
            print("%-14s %s" % (step, {0: "current", 1: "stale", 2: "not built here"}.get(
                r, "rc %d" % r)))
            if r == 1:
                rc = 1
            elif r == 2:
                absent = True
            elif r != 0:
                raise Crash("the %s builder's check crashed (rc %d)" % (step, r))
        probs = validate_scene(scene_path) if not absent else []
        for p in probs:
            print("scene: " + p)
        if probs:
            rc = 1
        return rc if rc else (2 if absent else 0)

    os.makedirs(out, exist_ok=True)
    metas = dict(old.get("assets", {})) if old else {}
    todo = ASSETS + STEPS if a.only is None else (
        [] if a.only in ("scene", "legs") else [a.only])
    for aid in todo:
        if aid in STEPS:
            print("%-14s building ..." % aid, flush=True)
            r = run_step(aid, out)
            if r == 1:
                raise Fail("the %s builder found its sources inconsistent" % aid)
            if r != 0:
                raise Crash("the %s builder failed (rc %d)" % (aid, r))
            continue
        print("%-14s building ..." % aid, flush=True)
        if aid in BOARDS:
            m = build_board(aid, out)
        elif aid in UNITS:
            m = build_unit(aid, out)
        else:
            m = build_pmu(out)
        m["stamp"] = stamps[aid]
        metas[aid] = m
        print("%-14s %8.2f MB  %s x %s x %s mm" % (aid, m["bytes"] / 1e6, *[
            round(m["bbox"][1][k] - m["bbox"][0][k], 1) for k in range(3)]), flush=True)
    rec = read_record()
    built = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    scene = assemble(rec, metas, built, out)
    scene["record_stamp"] = _record_stamp(rec)
    with open(scene_path + ".part", "w") as fh:
        json.dump(scene, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    os.replace(scene_path + ".part", scene_path)
    probs = validate_scene(scene_path)
    for p in probs:
        print("scene: " + p)
    total = sum(m["bytes"] for m in metas.values()) + os.path.getsize(scene_path)
    for step in STEPS:
        d = os.path.join(out, step)
        b = sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d)) if \
            os.path.isdir(d) else 0
        total += b
        print("%-14s %8.2f MB  %d files" % (step, b / 1e6, len(os.listdir(d)) if b else 0))
    kinds = {}
    for p in scene["parts"]:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    print("%-14s %8.2f MB  %d parts (%s), %d links, %d legs, %d branches" % (
        "scene.json", os.path.getsize(scene_path) / 1e6, len(scene["parts"]),
        ", ".join("%d %s" % (v, k) for k, v in sorted(kinds.items())), len(scene["links"]),
        len(scene.get("legs", [])), sum(len(l["branches"]) for l in scene.get("legs", []))))
    print("%-14s %8.2f MB" % ("total", total / 1e6))
    return 1 if probs else 0


def run_step(step, out, check=False):
    """One harness builder (connectors, devices) as its own command; returns its exit code."""
    script = CONNECTORS_BUILDER if step == "connectors" else DEVICES_BUILDER
    if not os.path.exists(script):
        raise Fail("the %s builder is not at %s" % (step, rel(script)))
    dest = os.path.join(out, "connectors") if step == "connectors" else out
    args = [sys.executable, script, "--out", dest] + (["--check"] if check else [])
    r = subprocess.run(args, cwd=ROOT, capture_output=check, text=True)
    return r.returncode


def _record_stamp(rec):
    h = hashlib.sha256()
    for key in sorted(rec):
        h.update(json.dumps([key, rec[key]], sort_keys=True).encode())
    return h.hexdigest()[:16]


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Fail as e:
        print("export_glb: %s" % e, file=sys.stderr)
        sys.exit(1)
    except Crash as e:
        print("export_glb: %s" % e, file=sys.stderr)
        sys.exit(3)
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(3)

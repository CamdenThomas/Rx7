"""corner/geometry.py - the front-left wheel assembly's solids, each in its own frame (FreeCAD only).

build(P) -> {part id: [(node name, shape, colour)]}; P is corner/params.py's. Frame: the axis is x,
+x outboard; the wheel's origin is the rim's centre plane, the hub's its mounting face, the nuts'
their seat plane. Rough shapes from the dimensions; see params.py for every number's source.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import partlib as L  # noqa: E402
from corner.params import CORNER  # noqa: E402


def _hex_x(af, x0, x1, cy, cz):
    r = af / math.sqrt(3)                      # circumradius of a hexagon across flats af
    pts = [(x0, cy + r * math.cos(math.radians(30 + 60 * k)), cz + r * math.sin(math.radians(30 + 60 * k)))
           for k in range(6)]
    return L.plate(pts, x1 - x0, (1, 0, 0))


def build(P):
    c = CORNER
    rb = P.v("rim_dia") / 2
    half = P.v("rim_width") / 2
    fl = rb + P.v("flange_h")
    drop = rb - P.v("drop_depth")
    et, dt = P.v("offset"), P.v("disc_t")
    pcr = P.v("pcd") / 2
    n = int(P.v("studs"))
    angles = [math.radians(45 + 360.0 / n * k) for k in range(n)]

    # the tyre: a rounded section revolved
    ro = P.v("tyre_od") / 2
    tw = P.v("tyre_w") / 2
    tyre = L.revolve_xr([(-half - 4, rb), (half + 4, rb), (tw, rb + 40), (tw, ro - 45),
                         (tw - 10, ro - 12), (tw - 30, ro), (-tw + 30, ro), (-tw + 10, ro - 12),
                         (-tw, ro - 45), (-tw, rb + 40)])

    # the wheel: the rim's contour thickened inward, and the dished disc with its stud holes
    rim_line = [(-half - 7, fl), (-half, rb + 5), (-half, rb), (-half + 22, rb), (-half + 38, drop),
                (half - 52, drop), (half - 36, rb), (half, rb), (half, rb + 5), (half + 7, fl)]
    rim = L.revolve_xr(L._offset2(rim_line, -P.v("rim_t")))
    rbore = P.v("bore") / 2
    disc = L.revolve_xr([(et - dt, rbore), (et, rbore), (et, rbore + 52), (et - 12, rbore + 82),
                         (et - 12, drop - 1), (et - 12 - dt, drop - 1), (et - 12 - dt, rbore + 80),
                         (et - dt, rbore + 50)])
    for a in angles:
        disc = disc.cut(L.cylinder_x(6.75, et - 30, et + 10, (0, pcr * math.cos(a), pcr * math.sin(a))))
    wheel = rim.fuse(disc)

    # the hub: flange, barrel, the disc on its hat, four studs (no stud row: they are the hub's)
    hub = L.cylinder_x(P.v("hub_flange") / 2, -10, 0)
    hub = hub.fuse(L.cylinder_x(P.v("hub_barrel") / 2, -P.v("hub_len"), 22))
    dod = P.v("disc_od") / 2
    disc_r = L.revolve_xr([(-12 - P.v("disc_th"), 62), (-12, 62), (-12, dod), (-12 - P.v("disc_th"), dod)])
    hat = L.revolve_xr([(-12, 58), (-10, 58), (-10, 72), (-12, 72)])
    hub = hub.fuse(disc_r).fuse(hat)
    for a in angles:
        hub = hub.fuse(L.cylinder_x(P.v("nut_thread") / 2, -10, et + dt + 18,
                                    (0, pcr * math.cos(a), pcr * math.sin(a))))

    nuts = []
    for k, a in enumerate(angles):
        cy, cz = pcr * math.cos(a), pcr * math.sin(a)
        nut = _hex_x(P.v("nut_af"), 0, P.v("nut_h"), cy, cz)
        nut = nut.cut(L.cylinder_x(P.v("nut_thread") / 2, -1, P.v("nut_h") + 1, (0, cy, cz)))
        nuts.append(("part:PT526-%s#%d" % (c, k + 1), nut, "nut"))

    return {
        "PT042-" + c: [("part:PT042-" + c, hub, "hub")],
        "PT525-" + c: [("part:PT525-" + c, wheel, "wheel")],
        "PT530-" + c: [("part:PT530-" + c, tyre, "tyre")],
        "PT526-" + c: nuts,
    }

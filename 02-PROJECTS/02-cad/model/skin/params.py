"""skin/params.py - B01's second pass (2026-10-13): the skin, the glass, the trim, the tail lamps and
three road wheels from the found FB model the app's home page shows (02-PROJECTS/02-cad/model/sa/rx7-fb.glb,
built by found/blend.py from the free library's FB body, the bought SA model's wheels and the
tail-lamp scans), cut into parts and laid on the hard points.

How it sits: that model is already at factory size. Its wheel centres land on DT02 / DT03 within a
millimetre (front x +-710, rear +-700, wheelbase 2420, centre height 294.5), its roof on DT06 (1260)
and its length on DT04 (4320), so the only move is the frame: the glb is y-up in centimetres with the
front at -z; the car's frame is D-418's (mm, x right, y forward, z up, front axle y = 0):
    X = 10 x,   Y = -10 z - 1210,   Z = 10 y
Nothing is measured from it (R11): it is an artist's model scaled to the factory figures, every
part's shape is the model's and every one carries confirm. Reads: 02-cad datums DT02, DT03.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from partlib import Dim, Params, part  # noqa: E402

FOUND = "found model 02-PROJECTS/02-cad/model/sa/rx7-fb.glb (found/blend.py)"
FIT = "found model on DT02 / DT03 (wheel centres within 1 mm), DT04, DT06"
# the found wheels: FL is the corner assembly's (factory figures); these are the other three
CORNERS = [("FR", 1, 0), ("RL", -1, 1), ("RR", 1, 1)]


def params(dt):
    P = Params()
    P["scale"] = Dim(10.0, "found", FOUND, "centimetres to millimetres; at that scale the model's wheel "
                     "centres, roof and length match the factory figures", [], "found model, cm to mm")
    P["y_shift"] = Dim(-1210.0, "derived", "02-cad DT02 (front axle y = 0)",
                       "the model's front axle is at z = -121.0 cm", [], "found model, front axle to y 0")
    P["wheel_x_f"] = Dim(dt["DT02"].num("x_mm"), "factory", "02-cad DT02 (SP-132)", "", ["PT525"],
                         "front wheel centre, across")
    P["wheel_x_r"] = Dim(dt["DT03"].num("x_mm"), "factory", "02-cad DT03 (SP-132)", "", ["PT525"],
                         "rear wheel centre, across")
    P["wheelbase"] = Dim(-dt["DT03"].num("y_mm"), "factory", "02-cad DT03 (SP-131)", "", ["PT525"], "wheelbase")
    P["wheel_z"] = Dim(dt["DT02"].num("z_mm"), "derived", "02-cad DT02", "unloaded", ["PT525"], "wheel centre height")
    return P


def _mate(to, apart, kind="welded", fasteners=()):
    return {"to": to, "kind": kind, "fasteners": list(fasteners), "apart": tuple(apart), "offset": ""}


def wheel_centre(P, corner):
    side, rear = {c: (s, r) for c, s, r in CORNERS}[corner]
    x = side * (P.v("wheel_x_r") if rear else P.v("wheel_x_f"))
    return (x, -P.v("wheelbase") if rear else 0.0, P.v("wheel_z"))


def parts(P):
    conf = "the found model's shape, scaled to the factory figures: nothing measured (R11)"
    out = [
        part("PT704-skin", "PT704", name="Body skin - fenders, doors, hood, roof, quarters, bumpers (found FB model, one piece)",
             kind="part", origin=(0.0, 0.0, 0.0), made_from="found", source=FOUND, place_from=FIT,
             dims=["scale", "y_shift"], mate=_mate("PT704", (0.0, 0.0, 420.0)), colour="skin", zone="doors", system="body",
             origin_note="the car's origin (D-418); the glb is in the car's frame",
             confirm_text=conf, note="one piece as the found model has it: the hood, fenders, doors and hatch are not yet parts of their own (PT744 and the rest)"),
        part("PT729", "PT729", name="Glass - windshield, doors, quarters and hatch (found FB model, one piece)",
             kind="part", origin=(0.0, 0.0, 0.0), made_from="found", source=FOUND, place_from=FIT,
             dims=["scale", "y_shift"], mate=_mate("PT704-skin", (0.0, 0.0, 300.0), kind="clipped"),
             colour="skin", zone="cabin", system="body", origin_note="the car's origin; the glb is in the car's frame",
             confirm_text=conf, note="all the glass in one piece under the windshield's row; the hatch glass has no 00-CAR row yet"),
        part("PT704-trim", "PT704", name="Trim, seals, mirrors and the cabin shell (found FB model)",
             kind="part", origin=(0.0, 0.0, 0.0), made_from="found", source=FOUND, place_from=FIT,
             dims=["scale", "y_shift"], mate=_mate("PT704-skin", (0.0, 0.0, 180.0), kind="clipped"),
             colour="skin", zone="cabin", system="body", origin_note="the car's origin; the glb is in the car's frame",
             confirm_text=conf, note="the model's other surfaces: bumper rubbers, garnishes, mirrors, seals and a rough cabin"),
    ]
    for side, k in (("L", -1), ("R", 1)):
        out.append(part("PT601-" + side, "PT601", name="Rear combination lamp, %s (scan in the found model)" % ("left" if k < 0 else "right"),
                        kind="part", origin=(0.0, 0.0, 0.0), made_from="found", source=FOUND, place_from=FIT,
                        dims=["scale", "y_shift"], mate=_mate("PT704-skin", (0.0, -220.0, 0.0), kind="bolted"),
                        colour="skin", zone="rear", side=side, system="lighting",
                        origin_note="the car's origin; the glb is in the car's frame", confirm_text=conf))
    for corner, s, rear in CORNERS:
        out.append(part("PT525-" + corner, "PT525", name="Road wheel, %s (found model's, with its brake and nuts)" % corner,
                        kind="part", origin=wheel_centre(P, corner), made_from="found", source=FOUND, place_from="datum %s" % ("DT03" if rear else "DT02"),
                        dims=["wheel_x_r" if rear else "wheel_x_f", "wheel_z", "wheelbase"],
                        mate=_mate("PT704", (s * 260.0, 0.0, 0.0), kind="bolted", fasteners=["PT526"]),
                        colour="wheel", zone="corners", side=corner, system="wheels",
                        origin_note="the wheel centre on DT02 / DT03", confirm_text=conf,
                        note="the SA model's wheel; the FL corner is built from factory figures. The found brakes are discs all round; the car's rears are drums (PT047)"))
        out.append(part("PT530-" + corner, "PT530", name="Tyre, %s (found model's)" % corner, kind="part",
                        parent="PT525-" + corner, origin=(0.0, 0.0, 0.0), made_from="found", source=FOUND,
                        place_from="datum %s" % ("DT03" if rear else "DT02"), dims=["wheel_z"],
                        mate=_mate("PT525-" + corner, (s * 140.0, 0.0, 0.0), kind="fits-in"),
                        colour="tyre", zone="corners", side=corner, system="wheels",
                        origin_note="the wheel centre", confirm_text="the fitted tyre's make and size (PT530: not recorded)"))
    return out

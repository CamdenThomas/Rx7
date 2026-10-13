"""corner/params.py - the front-left wheel assembly's governing dimensions and its parts (05-cad A04).

Pure python: read by the build (FreeCAD) and by export_scene (the drafts). Every number has how it
is known and its source; nothing here is measured on the car, so every dimension is confirm (R11).
Record: 00-CAR parts PT525 (road wheels), PT530 (tyres), PT526 (wheel nuts), PT042 (front rotor
hubs); specs SP-1513 / SP-126 (5-J x 13), SP-128 (185/70HR13), SP-1520 / SP-127 (ET 20),
SP-1519 / SP-123 (4 x 110), SP-124 (M12 x 1.5), SP-113 (front disc); 05-cad datums DT02.

The part frame: the origin on the wheel's axis, x along the axis and outboard. A left wheel is
turned half a turn about z (rz 180) so its +x points to the car's left.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from partlib import Dim, Params, part  # noqa: E402

CORNER = "FL"            # the one corner A04 builds; DT02's left wheel


def params(dt):
    P = Params()
    x02, z02 = dt["DT02"].num("x_mm"), dt["DT02"].num("z_mm")
    P["wheel_x"] = Dim(x02, "factory", "05-cad DT02 (SP-132, S-004 p.14)",
                       "front track 1419.9 / 2; the tyre's centre plane", ["PT525"], "wheel centre, across")
    P["wheel_z"] = Dim(z02, "derived", "05-cad DT02 (tyre size, unloaded)",
                       "the unloaded tyre radius; loaded it is less - confirm at the ride height",
                       ["PT525"], "wheel centre height")
    P["rim_dia"] = Dim(330.2, "factory", "SP-1513 (S-038 T:6), SP-126", "13 in bead seat",
                       ["PT525"], "rim bead seat diameter")
    P["rim_width"] = Dim(127.0, "factory", "SP-1513 (5-J x 13)", "5 in between the flanges",
                         ["PT525"], "rim width between flanges")
    P["flange_h"] = Dim(17.5, "catalogue", "ETRTO J flange (catalogue figure)",
                        "the J contour's flange height; not measured", ["PT525"], "rim flange height")
    P["offset"] = Dim(20.0, "catalogue", "SP-1520 (S-020, secondary)",
                      "mounting face outboard of the rim centre line", ["PT525", "PT042"], "wheel offset ET")
    P["pcd"] = Dim(110.0, "catalogue", "SP-1519 (S-021, secondary)", "4 studs",
                   ["PT525", "PT526", "PT042"], "bolt circle (PCD)")
    P["studs"] = Dim(4, "catalogue", "SP-1519 (4 x 110)", "", ["PT526"], "stud count")
    P["bore"] = Dim(60.0, "guess", "", "centre bore; not in the record", ["PT525"], "centre bore")
    P["disc_t"] = Dim(4.0, "guess", "", "pressed steel disc thickness", ["PT525"], "disc thickness")
    P["rim_t"] = Dim(3.0, "guess", "", "rim sheet thickness", ["PT525"], "rim thickness")
    P["drop_depth"] = Dim(24.0, "guess", "", "well depth below the bead seat", ["PT525"], "drop centre depth")
    P["tyre_w"] = Dim(185.0, "factory", "SP-128 (S-004 p.14-15)", "section width", ["PT530"], "tyre section width")
    P["tyre_aspect"] = Dim(70.0, "factory", "SP-128", "per cent", ["PT530"], "tyre aspect ratio")
    P["tyre_od"] = Dim(330.2 + 2 * 185.0 * 0.70, "derived", "SP-128, SP-1513",
                       "13 in + 2 x 70 % of 185; DT02's 589", ["PT530"], "tyre outside diameter")
    P["nut_af"] = Dim(19.0, "catalogue", "00-CAR PT526 note (Mazdatrix M12x1.5 19 mm)", "",
                      ["PT526"], "nut across flats")
    P["nut_h"] = Dim(22.0, "guess", "", "open-top nut height", ["PT526"], "nut height")
    P["nut_thread"] = Dim(12.0, "factory", "SP-124 (M12 x 1.5)", "", ["PT526"], "stud thread")
    P["disc_eff"] = Dim(202.0, "factory", "SP-113 (S-002 p.11-2)", "effective diameter",
                        ["PT042"], "brake disc effective diameter")
    P["disc_od"] = Dim(228.0, "guess", "", "outside diameter, from the effective 202 + pad height",
                       ["PT042"], "brake disc outside diameter")
    P["disc_th"] = Dim(18.0, "factory", "SP-113", "new; limit 17", ["PT042"], "brake disc thickness")
    P["hub_flange"] = Dim(140.0, "guess", "", "", ["PT042"], "hub flange diameter")
    P["hub_barrel"] = Dim(76.0, "guess", "", "bearing barrel", ["PT042"], "hub barrel diameter")
    P["hub_len"] = Dim(95.0, "guess", "", "flange face to the inner bearing end", ["PT042"], "hub length")
    return P


def parts(P):
    x, z, et = P.v("wheel_x"), P.v("wheel_z"), P.v("offset")
    c = CORNER
    conf = "every dimension (rim, tyre, hub and nut sizes are catalogue or guess)"
    return [
        part("PT042-" + c, "PT042", name="Front rotor hub, front left", kind="part",
             origin=(-(x + et), 0.0, z), rot=(0, 0, 180), made_from="factory",
             source="SP-113, SP-1519; corner/params.py", place_from="datum DT02",
             dims=["disc_eff", "disc_od", "disc_th", "hub_flange", "hub_barrel", "hub_len", "pcd", "offset"],
             mate=None, colour="hub", zone="corners", side=c, system="brakes",
             origin_note="the hub's wheel-mounting face on the axis; +x outboard",
             confirm_text=conf, note="hub and disc as one unit (S-002 p.9-5); the knuckle it turns on is not modelled yet"),
        part("PT525-" + c, "PT525", name="Road wheel, front left", kind="part",
             origin=(-x, 0.0, z), rot=(0, 0, 180), made_from="factory",
             source="SP-1513, SP-1520, SP-1519; corner/params.py", place_from="datum DT02",
             dims=["wheel_x", "wheel_z", "rim_dia", "rim_width", "flange_h", "offset", "pcd", "bore",
                   "disc_t", "rim_t", "drop_depth"],
             mate={"to": "PT042-" + c, "kind": "bolted", "fasteners": ["PT526"],
                   "apart": (-160.0, 0.0, 0.0), "offset": "%g 0 0 in the hub's frame (ET %g)" % (-et, et)},
             colour="wheel", zone="corners", side=c, system="wheels",
             origin_note="the rim's centre plane on the axis (DT02); +x outboard",
             confirm_text=conf, note="5-J x 13 steel (GS) assumed; the GSL alloy is 5.5-JJ - which is on the car is a check (PT525 note)"),
        part("PT530-" + c, "PT530", name="Tyre, front left", kind="part", parent="PT525-" + c,
             origin=(0.0, 0.0, 0.0), made_from="factory", source="SP-128; corner/params.py",
             place_from="datum DT02", dims=["tyre_w", "tyre_aspect", "tyre_od"],
             mate={"to": "PT525-" + c, "kind": "fits-in", "fasteners": [],
                   "apart": (-140.0, 0.0, 0.0), "offset": "0 0 0 in the wheel's frame"},
             colour="tyre", zone="corners", side=c, system="wheels",
             origin_note="the tyre's centre plane on the axis",
             confirm_text="the fitted tyre's make and size (PT530 note: not recorded)"),
        part("PT526-" + c, "PT526", name="Wheel nuts, front left (4)", kind="part", parent="PT525-" + c,
             origin=(et + P.v("disc_t"), 0.0, 0.0), made_from="catalogue",
             source="SP-124, SP-1519, PT526 note; corner/params.py", place_from="datum DT02",
             dims=["nut_af", "nut_h", "nut_thread", "pcd", "studs"],
             mate={"to": "PT525-" + c, "kind": "bolted", "fasteners": [],
                   "apart": (-70.0, 0.0, 0.0), "offset": "%g 0 0 in the wheel's frame (the disc's outer face)" % (et + P.v("disc_t"))},
             colour="nut", zone="corners", side=c, system="wheels",
             origin_note="the nuts' seat plane on the axis; the four on the bolt circle",
             confirm_text="nut height; the seat type (taper / flat)"),
    ]

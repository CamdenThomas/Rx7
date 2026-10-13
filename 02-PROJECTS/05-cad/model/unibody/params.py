"""unibody/params.py - the FB unibody's governing dimensions, ONE table, and its panels (05-cad B01, D-518).

Pure python: read by the build (FreeCAD) and by export_scene (the scene and the record drafts).
Every number says how it is known (model_dims.how) and where from. NOTHING here is measured on the
car (R11): every dimension is confirm until a measurement replaces it.

Sources, by the short names used below:
  DTnn       05-cad datums, read through rx7.py each build (frame.py) - the factory hard points
  FSM        S-002, 1985 FSM section 14 p.14-24 (PDF p.24), Body checking dimensions: plan and side
             views of the underbody. The drawing is not to scale (2250 spans 755 px of the 300 dpi
             scan, 580 spans 145 px), so a point it does not dimension is read by interpolating
             between the two dimensioned points either side of it, and says so.
  blueprint  the-blueprints.com 83684 "Mazda RX-7 FB" (00-CAR cad
             fb-rx7-blueprint-the-blueprints-83684), 2483 x 2546 px: the library's copy,
             01-REFERENCE/model/library/body/fb-rx7-blueprint-the-blueprints-83684/mazda-rx-7fb.png
             (sha1 94410117..., byte-identical to the copy re-fetched from the site 2026-10-13). A JDM
             Savanna drawing (fender mirrors), the same shell. Its views are not drawn at one
             scale, so each axis is scaled to a factory figure:
               lengthwise between the axles  2420 / 1332.5 px = 1.816 mm/px (DT03 wheelbase;
                                             wheel centres at px 592 and 1924.5)
               lengthwise, the overhangs     1900.5 / 1094 px = 1.737 mm/px (DT04 less DT03)
               height                        1259.8 / 720 px  = 1.750 mm/px (DT06; ground row 737,
                                             roof row 17)
               width (plan view)             1668.8 / 947 px  = 1.762 mm/px (DT05; centre row 1266)
             so y = -(px - 592) x 1.816 between the axles, z = (737 - row) x 1.750.
  found      00-CAR cad fb-rx7-gsl-se-85-3dwarehouse-blastronaut (quality 3): the 1985 GSL-SE
             shell, 01-REFERENCE/model/library/body/fb-rx7-gsl-se-85-3dwarehouse-blastronaut/
             "Mazda RX-7 fb Tuner (Copper).glb" (sha1 504ebf62..., byte-identical to 3D Warehouse's
             public glb, no login; 3D Warehouse General Model License). Scaled to the factory
             length (4320.5 / 4467.8 = 0.9670) it puts its axles 2430.4 apart, 10.4 over DT03; so
             it is scaled to the wheelbase instead (0.9628), its front axle at y 0 - the two scales
             differ by at most 17 mm at the ends, under every guess here. It is a lowered "tuner",
             so its body is lifted 59 mm to put its roof on DT06. Its mesh is coarse (10 720 paint
             vertices), so it checks the blueprint's greenhouse and sill; where they differ, each
             dimension's note says which won.
  record     00-CAR rows named in the source text.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from partlib import Dim, Params, part  # noqa: E402

FSM = "S-002 p.14-24 (FSM body checking dimensions)"
BP = "blueprint the-blueprints 83684"
FOUND = "found model fb-rx7-gsl-se-85-3dwarehouse-blastronaut"
SHELL = "PT704"
SIDES = (("R", 1.0), ("L", -1.0))


def params(dt):
    P = Params()

    def d(key, value, how, source, note, parts, label):
        P[key] = Dim(round(value, 2), how, source, note, parts, label)

    # -------- the factory frame (datums) ----------------------------------------------------
    d("wheelbase", -dt["DT03"].num("y_mm"), "factory", "DT03 (SP-131, S-004 p.14)", "", ["PT768", "PT777"], "wheelbase")
    d("wheel_z", dt["DT02"].num("z_mm"), "derived", "DT02 (tyre size, unloaded)", "confirm at the ride height", ["PT777"], "wheel centre height")
    d("length", dt["DT04"].num("y_mm"), "factory", "DT04 (SP-133, S-004 p.15)", "bumpers included; the shell is shorter", [SHELL], "overall length")
    d("half_w", dt["DT05"].num("x_mm"), "factory", "DT05 (SP-134, S-004 p.15)",
      "reading: the widest point is the rear-arch lip of the quarter panel; with side protector mouldings - confirm where", ["PT768"], "overall half-width")
    d("height", dt["DT06"].num("z_mm"), "factory", "DT06 (SP-135, S-004 p.15)", "unladen; the roof's top", ["PT774"], "overall height")
    d("ground_clear", dt["DT07"].num("z_mm"), "factory", "DT07 (SP-136, S-004 p.15)",
      "the lowest point of the car - a mechanical part, not the shell; the shell stays above it", [SHELL], "ground clearance")
    d("a_half", dt["DT10"].num("x_mm"), "factory", "DT10 (SP-234, FSM)", "front frame basic holes A, 800 apart", ["PT755"], "hole A, across")
    d("a_z_rel", dt["DT10"].above_datum() or 220, "factory", "DT10 (SP-239, FSM)", "above the underbody datum line", ["PT755"], "hole A above the datum")
    d("b_half", dt["DT11"].num("x_mm"), "factory", "DT11 (SP-235, FSM)", "rear frame basic holes B, 795 apart", ["PT780"], "hole B, across")
    d("a_to_b", dt["DT11"].num("y_mm") or 2250, "factory", "DT11 (SP-236, FSM)", "lengthwise", ["PT755", "PT780"], "hole A to hole B, lengthwise")
    d("c_half", dt["DT12"].num("x_mm"), "factory", "DT12 (SP-237, FSM)", "rear frame holes C, 890 apart", ["PT780"], "hole C, across")
    d("f_half", dt["DT13"].num("x_mm"), "factory", "DT13 (SP-238, FSM)", "rear upper arm fixing holes F, 1048 apart", ["PT780"], "hole F, across")
    d("nut_half", dt["DT14"].num("x_mm"), "factory", "DT14 (SP-239, FSM)", "front fender fixing nuts, 1324 apart", ["PT754"], "fender fixing nuts, across")
    d("fender_line_f", 364.0, "factory", "SP-1280 (S-038 T:7)", "wheel centre to the front fender line (arch top)", ["PT754"], "front wheel centre to fender line")
    d("fender_line_r", 358.0, "factory", "DT08 (SP-106, S-003 T:7)",
      "read as SP-1280 reads the front figure: wheel centre to the rear fender line (the 1980 spec)", ["PT768", "PT777"], "rear wheel centre to fender line")

    # -------- the underbody, from the FSM drawing ---------------------------------------------
    d("z_datum", 60.0, "guess", FSM + "; DT09",
      "the datum line's height above the ground is not in the record; 60 puts the floor's underside at the blueprint's sill bottom", [SHELL], "underbody datum line above the ground")
    d("y_a", 580.0, "guess", FSM + " plan view",
      "hole A's lengthwise place is not in the record (DT10). The plan view puts the strut-tower circle at the hole 580 behind A; read as the tower over the front axle (caster ignored)", ["PT755"], "hole A forward of the front axle")
    d("a_to_c", 3445.0, "derived", FSM + " diagonals 2990.4, 3095.6, 1466.2, 1190.9 (plan, A+460 hole to C; B to C)",
      "the four give 3438-3450; the mean", ["PT780"], "hole A to hole C, lengthwise")
    d("e_half", 530.0, "guess", FSM + " plan view", "E sits a hair outboard of F on the drawing", ["PT780"], "hole E, across")
    d("a_to_e", 2519.0, "derived", FSM + " diagonal E to the opposite C 1343.6, with e_half and a_to_c", "", ["PT780"], "hole A to hole E, lengthwise")
    d("a_to_f", 2784.0, "derived", FSM + " plan view, F's line interpolated between B (2250) and C (3445) at 2.543 mm/px",
      "not dimensioned on the page", ["PT780"], "hole A to hole F, lengthwise")
    d("c_z_rel", 345.0, "factory", FSM + " side view", "reading: the 345 (13.58) on the side view is C's height above the datum", ["PT780"], "hole C above the datum")
    d("e_z_rel", 110.0, "factory", FSM + " side view", "reading: the 110 (4.33) is E's height above the datum", ["PT780"], "hole E above the datum")
    d("f_z_rel", 339.4, "factory", FSM + " side view",
      "reading: the 339.4 (13.36) is F's height above the datum (it may instead be E to F) - confirm on the page", ["PT780"], "hole F above the datum")
    d("nut_z_rel_a", 435.0, "factory", "SP-1281 (FSM section G-G)", "reading: the fender nut's height above hole A", ["PT754"], "fender fixing nut above hole A")
    d("rail_tip", 150.0, "derived", FSM + " plan view (50 px x 2.98 mm/px)", "the front rail's end ahead of hole A", ["PT755", "PT753"], "front rail tip ahead of hole A")
    d("strut_half", 510.0, "derived", FSM + " plan view (the tower circle, 40 px outboard of the rail at 2.7 mm/px)", "", ["PT754"], "strut tower centre, across")

    # -------- the shell's outline, from the blueprint and the found model -----------------------
    d("front_oh", 981.5, "derived", BP + " (front tip px 27 of overhang px 565 + 529)", "DT04 less DT03, split as the blueprint splits it", [SHELL], "front overhang")
    d("rear_oh", 919.0, "derived", BP + " (rear tip px 2453)", "", [SHELL], "rear overhang")
    d("ws_base_y", -720.0, "found", BP + " px 1000 -> -741; " + FOUND + " -> -700", "the mean", ["PT764", "PT770"], "windshield base, lengthwise")
    d("ws_base_z", 880.0, "found", BP + " row 207 -> 927; " + FOUND + " -> 871", "the mean, nearer the found model (the blueprint's cowl line is the hood's)", ["PT764"], "windshield base height")
    d("ws_corner_y", -980.0, "guess", BP + " plan view px 1093 -> -910; side view puts the pillar's top further back",
      "the two views disagree; between them", ["PT770"], "A-pillar top, lengthwise")
    d("ws_corner_z", 1150.0, "guess", BP + " side view", "", ["PT770"], "A-pillar top height")
    d("roof_front_y", -1150.0, "found", BP + " windshield top px 1253 -> -1200 (centre); " + FOUND + " -1200", "the roof panel's front edge, ahead of the glass's top line", ["PT774", "PT773"], "roof front edge, lengthwise")
    d("roof_peak_y", -1540.0, "found", BP + " roof top px 1440", FOUND + " tops out -1500 to -1700", ["PT774"], "roof's highest point, lengthwise")
    d("roof_rear_y", -2220.0, "found", BP + " px 1813 -> -2217; " + FOUND + " -2200", "", ["PT774", "PT773", "PT767"], "roof rear edge (hatch hinge line), lengthwise")
    d("roof_rear_z", 1200.0, "found", BP + " row 47 -> 1207; " + FOUND + " -> 1194", "", ["PT774", "PT773"], "roof rear edge height")
    d("roof_half", 690.0, "found", BP + " plan 693; " + FOUND + " glass 699", "the drip line", ["PT774", "PT767", "PT773"], "roof half-width")
    d("roof_camber", 45.0, "guess", BP + " front view", "crown above the side edge", ["PT774"], "roof camber")
    d("tail_y", -2990.0, "found", BP + " px 2253 -> -2991; " + FOUND + " -3000", "the hatch glass's lower edge", ["PT772", "PT768"], "hatch aperture bottom, lengthwise")
    d("tail_z", 850.0, "found", BP + " row 247 -> 857; " + FOUND + " -> 846", "", ["PT772", "PT768"], "hatch aperture bottom height")
    d("belt_z", 870.0, "found", BP + " row 240", "the door and quarter window sill", ["PT768", "PT769"], "belt line height")
    d("sill_bottom", 205.0, "found", BP + " row 617 -> 210; " + FOUND + " -> 205", "", ["PT771", "PT783", "PT768"], "sill bottom height")
    d("door_front_y", -728.0, "found", BP + " px 993", "", ["PT769"], "door opening front, lengthwise")
    d("door_rear_y", -1927.0, "found", BP + " px 1653", "", ["PT976", "PT768"], "door opening rear, lengthwise")
    d("bpillar_top_y", -2010.0, "found", BP + " px 1700", "the door glass's rear top corner", ["PT976"], "centre pillar top, lengthwise")
    d("sail_rear_y", -2266.0, "found", BP + " px 1840", "the sail panel's rear edge, at the quarter glass", ["PT976"], "sail rear edge, lengthwise")
    d("arch_r", 351.0, "found", BP + " front arch 193 px", "the arch opening's radius; the rear taken the same", ["PT768", "PT754"], "wheel arch radius")
    d("hood_z0", 847.0, "found", BP + " row 253 at the front axle", "", ["PT754"], "hood line at the front axle")
    d("rad_y", 720.0, "guess", FSM + " (rail tip at A + 150) and " + BP + " nose", "the core support sits on the rail tips", ["PT753", "PT752", "PT761"], "radiator support, lengthwise")
    d("firewall_y", -640.0, "found", "00-CAR zones engine_bay / dash boundary -642 (the combined model, D-421)", "", ["PT756", "PT757", "PT762", "PT766"], "firewall, lengthwise")
    d("firewall_foot_y", -850.0, "guess", "", "the toe board's foot", ["PT756", "PT778"], "toe board foot, lengthwise")
    d("rear_panel_y", -3260.0, "guess", "DT04 rear end (-3339) less the bumper", "", ["PT775", "PT776", "PT779", "PT780"], "rear end panel, lengthwise")

    # -------- the sections: guesses until the strip ---------------------------------------------
    d("floor_rel", 150.0, "guess", FSM + " side view (the floor runs 120-150 above the datum)", "floor underside above the datum", ["PT778"], "front floor above the datum")
    d("rear_floor_z", 520.0, "guess", "", "the cargo floor, clear of the axle (DT03) and the tank", ["PT779"], "rear (cargo) floor height")
    d("kick_y", -1950.0, "guess", "", "where the front floor steps up to the rear floor, behind the seats", ["PT778", "PT779", "PT781"], "floor kick-up, lengthwise")
    d("sill_in", 690.0, "guess", "", "the inner sill's face", ["PT771", "PT783", "PT778"], "sill inner face, across")
    d("sill_out", 800.0, "guess", BP + " plan (the rocker sits inside the door skin)", "", ["PT771"], "sill outer face, across")
    d("sill_top", 330.0, "guess", "", "", ["PT771", "PT783", "PT769"], "sill top height")
    d("tunnel_base", 380.0, "guess", "", "", ["PT778"], "tunnel width at the floor")
    d("tunnel_top", 240.0, "guess", "", "", ["PT778"], "tunnel width at the top")
    d("tunnel_h", 250.0, "guess", "", "", ["PT778"], "tunnel height")
    d("frail_w", 75.0, "guess", "", "", ["PT755"], "front rail width")
    d("frail_h", 107.0, "factory", FSM + " detail K, b = 107", "reading: b is the rail's depth at hole A - confirm", ["PT755"], "front rail depth")
    d("rrail_w", 70.0, "guess", "", "", ["PT780"], "rear rail width")
    d("rrail_h", 100.0, "guess", "", "", ["PT780"], "rear rail depth")
    d("under_h", 50.0, "guess", "", "the rails' depth under the floor", ["PT755", "PT780"], "rail depth under the floor")
    d("strut_r", 90.0, "guess", "", "", ["PT754"], "strut tower radius")
    d("strut_top", 785.0, "guess", BP + " hood line less 62", "", ["PT754"], "strut tower top height")
    d("wh_in", 560.0, "guess", "", "", ["PT777", "PT779", "PT784"], "rear wheelhouse inner face, across")
    d("wh_r", 375.0, "guess", "", "clears the 589 tyre with travel", ["PT777"], "rear wheelhouse radius")
    d("t_sheet", 1.0, "guess", "", "panel steel", [SHELL], "sheet thickness")
    d("t_rail", 1.6, "guess", "", "rail and sill steel", ["PT755", "PT780", "PT771"], "rail sheet thickness")
    for k, why in WON.items():
        P[k].note = ("won: %s. " % why) + P[k].note
    return P


# which source won, for every outline dimension the blueprint and the found shell both speak to
WON = {
    "ws_base_y": "the mean of the two (41 mm apart)",
    "ws_base_z": "the found shell, nearly (the blueprint's line there is the hood's rear edge)",
    "ws_corner_y": "neither: the blueprint's plan and side views disagree; between them",
    "roof_front_y": "both agree (-1200 at the centre)",
    "roof_peak_y": "the blueprint (the found shell is flat from -1500 to -1700)",
    "roof_rear_y": "the blueprint (the found shell agrees within 17)",
    "roof_rear_z": "the blueprint (the found shell agrees within 13)",
    "roof_half": "the blueprint (the found shell's glass agrees within 9)",
    "tail_y": "the blueprint (the found shell agrees within 10)",
    "tail_z": "the blueprint (the found shell agrees within 11)",
    "belt_z": "the blueprint alone (the found shell's belt is not a crease in its mesh)",
    "sill_bottom": "the found shell (205; the blueprint's 210 is the rocker moulding)",
    "door_front_y": "the blueprint alone (the found shell's door cut is not modelled)",
    "door_rear_y": "the blueprint alone",
    "bpillar_top_y": "the blueprint alone",
    "sail_rear_y": "the blueprint alone",
    "arch_r": "the blueprint alone (the found shell carries flares)",
    "hood_z0": "the blueprint alone (the found shell is lowered)",
}


def check(P):
    """The shell must land on the datums: refusals, not warnings."""
    out = []
    if abs(P.v("front_oh") + P.v("wheelbase") + P.v("rear_oh") - P.v("length")) > 0.6:
        out.append("front_oh + wheelbase + rear_oh != DT04 length")
    if P.v("sill_bottom") < P.v("ground_clear"):
        out.append("the sill is below DT07")
    if P.v("z_datum") + P.v("floor_rel") - P.v("under_h") < P.v("ground_clear"):
        out.append("the rails under the floor are below DT07")
    return out


def derived(P):
    """The points every panel shares, in the car's frame."""
    D = {}
    D["y_a"] = P.v("y_a")
    D["y_b"] = D["y_a"] - P.v("a_to_b")
    D["y_c"] = D["y_a"] - P.v("a_to_c")
    D["y_e"] = D["y_a"] - P.v("a_to_e")
    D["y_f"] = D["y_a"] - P.v("a_to_f")
    D["z_a"] = P.v("z_datum") + P.v("a_z_rel")
    D["z_c"] = P.v("z_datum") + P.v("c_z_rel")
    D["z_e"] = P.v("z_datum") + P.v("e_z_rel")
    D["z_f"] = P.v("z_datum") + P.v("f_z_rel")
    D["floor_z"] = P.v("z_datum") + P.v("floor_rel")
    D["nut_z"] = D["z_a"] + P.v("nut_z_rel_a")
    D["y_rear_axle"] = -P.v("wheelbase")
    D["front_end"] = P.v("front_oh")
    D["rear_end"] = -P.v("wheelbase") - P.v("rear_oh")
    D["arch_top_f"] = P.v("wheel_z") + P.v("fender_line_f")
    D["arch_top_r"] = P.v("wheel_z") + P.v("fender_line_r")
    D["roof_top"] = P.v("height")
    return D


def _mate(to, apart, offset="", kind="welded", fasteners=()):
    return {"to": to, "kind": kind, "fasteners": list(fasteners), "apart": tuple(apart), "offset": offset}


def parts(P):
    """Every panel as the scene and the drafts need it; origins in the car's frame (the shell
    node PT704 sits at the car's origin, unturned, so its frame is the car's)."""
    D = derived(P)
    fz = D["floor_z"]
    conf = "every dimension: none is measured (R11)"
    out = [part(SHELL, SHELL, name="Body shell (welded unit body)", kind="node", origin=(0, 0, 0),
                made_from="factory", source="unibody/params.py", place_from="datum DT01", dims=["length", "ground_clear"],
                colour="steel", zone=None, origin_note="the car's origin (DT01): front axle, centreline, ground",
                confirm_text=conf, note="the welded shell: every panel below is its child")]

    def body(pid, record, name, origin, dims, mate, colour="steel", made="factory", src="", zone=None,
             side=None, note="", place_from=None):
        out.append(part(pid, record, name=name, kind="body", origin=origin, parent=SHELL,
                        made_from=made, source=src or "unibody/params.py", dims=dims,
                        place_from=place_from or "FSM S-002 p.14-24", mate=mate, colour=colour,
                        zone=zone, side=side, confirm_text=conf, note=note,
                        origin_note="a point on the panel; the glb is drawn about it"))

    body("PT778", "PT778", "Front floor pan, with the transmission tunnel", (0, (P.v("firewall_foot_y") + P.v("kick_y")) / 2, fz),
         ["floor_rel", "z_datum", "sill_in", "tunnel_base", "tunnel_top", "tunnel_h", "firewall_foot_y", "kick_y"],
         None, colour="floor", made="guess", note="the shell's root: everything welds to it, directly or through a neighbour")
    body("PT779", "PT779", "Rear floor pan", (0, (P.v("kick_y") + P.v("rear_panel_y")) / 2, P.v("rear_floor_z")),
         ["rear_floor_z", "kick_y", "rear_panel_y", "wh_in"], _mate("PT778", (0, -180, 60)), colour="floor", made="guess")
    body("PT781", "PT781", "Floor cross members (three)", (0, -1300.0, fz - 20),
         ["kick_y", "sill_in", "c_half"], _mate("PT778", (0, 0, -120)), colour="rail", made="guess",
         note="three of the catalogue's four: under the seats, at the kick-up, at the rear panel")
    for s, k in SIDES:
        body("PT755-" + s, "PT755", "Front side frame (rail), " + ("right" if k > 0 else "left"),
             (k * P.v("a_half"), D["y_a"], D["z_a"]), ["a_half", "a_z_rel", "y_a", "a_to_b", "frail_w", "frail_h", "rail_tip", "under_h", "t_rail"],
             _mate("PT778", (k * 40, 220, -90)), colour="rail", side=s, place_from="datum DT10",
             note="origin at hole A (DT10)")
        body("PT780-" + s, "PT780", "Rear side frame (rail), with the upper link bracket, " + ("right" if k > 0 else "left"),
             (k * P.v("b_half"), D["y_b"], fz - P.v("under_h")),
             ["b_half", "a_to_b", "c_half", "a_to_c", "c_z_rel", "f_half", "a_to_f", "f_z_rel", "rrail_w", "rrail_h", "under_h", "t_rail"],
             _mate("PT779", (k * 40, -220, -90)), colour="rail", side=s, place_from="datum DT11",
             note="origin at hole B (DT11). The rear upper link bracket (holes F, DT13) is drawn with it: the record has no row of its own for the bracket")
        body("PT782-" + s, "PT782", "Torque box, " + ("right" if k > 0 else "left"), (k * 560, -910.0, fz - 10),
             ["firewall_foot_y", "sill_in", "a_half"], _mate("PT778", (k * 60, 60, -100)), colour="rail", made="guess", side=s)
        body("PT771-" + s, "PT771", "Side sill panel (outer), " + ("right" if k > 0 else "left"),
             (k * P.v("sill_out"), -1200.0, P.v("sill_bottom")), ["sill_in", "sill_out", "sill_top", "sill_bottom", "t_rail"],
             _mate("PT778", (k * 200, 0, 0)), colour="skin", made="found", src=BP, side=s, zone="doors", place_from="blueprint")
        body("PT783-" + s, "PT783", "Inner side sill panel, " + ("right" if k > 0 else "left"),
             (k * P.v("sill_in"), -1200.0, P.v("sill_bottom")), ["sill_in", "sill_top", "sill_bottom"],
             _mate("PT778", (k * 120, 0, 0)), colour="rail", made="guess", side=s)
        body("PT769-" + s, "PT769", "Hinge pillar (A-pillar, lower), " + ("right" if k > 0 else "left"),
             (k * 770, P.v("door_front_y") - 37, P.v("sill_top")), ["door_front_y", "sill_top", "belt_z"],
             _mate("PT771-" + s, (k * 120, 80, 0)), made="found", src=BP, side=s, place_from="blueprint")
        body("PT770-" + s, "PT770", "Front pillar (A-pillar, windshield), " + ("right" if k > 0 else "left"),
             (k * 750, P.v("door_front_y") - 37, P.v("belt_z")), ["ws_corner_y", "ws_corner_z", "roof_front_y", "roof_half", "belt_z"],
             _mate("PT769-" + s, (k * 100, 0, 120)), made="found", src=BP, side=s, place_from="blueprint")
        body("PT976-" + s, "PT976", "Centre pillar (B-pillar and sail), " + ("right" if k > 0 else "left"),
             (k * 780, P.v("door_rear_y") - 33, P.v("sill_top")), ["door_rear_y", "bpillar_top_y", "sail_rear_y", "sill_top", "roof_half"],
             _mate("PT771-" + s, (k * 140, 0, 60)), made="found", src=BP, side=s, place_from="blueprint")
        body("PT767-" + s, "PT767", "Roof rail, " + ("right" if k > 0 else "left"),
             (k * (P.v("roof_half") - 10), P.v("roof_front_y"), 1190.0), ["roof_half", "roof_front_y", "roof_rear_y", "roof_peak_y"],
             _mate("PT770-" + s, (k * 120, 0, 140)), made="found", src=BP, side=s, place_from="blueprint")
        body("PT768-" + s, "PT768", "Quarter panel, with the rear arch, " + ("right" if k > 0 else "left"),
             (k * P.v("half_w"), D["y_rear_axle"], P.v("wheel_z")),
             ["half_w", "arch_r", "fender_line_r", "wheelbase", "belt_z", "tail_y", "tail_z", "door_rear_y", "rear_panel_y", "sill_bottom"],
             _mate("PT771-" + s, (k * 260, -60, 0)), colour="skin", made="found", src=BP + "; " + FOUND, side=s, place_from="datum DT03",
             note="origin at the rear wheel centre's line on the panel's outer face")
        body("PT777-" + s, "PT777", "Rear fender panel (inner wheelhouse), " + ("right" if k > 0 else "left"),
             (k * P.v("wh_in"), D["y_rear_axle"], P.v("wheel_z")), ["wh_in", "wh_r", "wheelbase", "wheel_z"],
             _mate("PT779", (k * 140, 0, 80)), made="guess", side=s, place_from="datum DT03",
             note="reading: FA01-70-400 'rear fender panel' is the inner wheelhouse - confirm against the catalogue figure")
        body("PT784-" + s, "PT784", "Floor deck (cargo side), " + ("right" if k > 0 else "left"),
             (k * 670, -2975.0, 670.0), ["wh_in", "wh_r", "rear_panel_y"], _mate("PT779", (k * 60, 0, 120)), made="guess", side=s)
        body("PT754-" + s, "PT754", "Front wheel apron and strut tower, " + ("right" if k > 0 else "left"),
             (k * P.v("strut_half"), 0.0, P.v("strut_top")),
             ["strut_half", "strut_r", "strut_top", "nut_half", "nut_z_rel_a", "a_half", "frail_h", "rad_y", "firewall_y", "arch_r", "fender_line_f"],
             _mate("PT755-" + s, (k * 200, 60, 90)), side=s, place_from="FSM S-002 p.14-24",
             note="origin at the strut tower's top centre")
        body("PT766-" + s, "PT766", "Cowl side panel, " + ("right" if k > 0 else "left"),
             (k * P.v("sill_in"), P.v("firewall_y"), D["floor_z"]), ["firewall_y", "sill_in", "belt_z"],
             _mate("PT756", (k * 120, 0, 0)), made="guess", side=s, zone="cabin")
        body("PT761-" + s, "PT761", "Engine bay side panel, " + ("right" if k > 0 else "left"),
             (k * 640, 400.0, 450.0), ["rad_y"], _mate("PT754-" + s, (k * 100, 80, 0)), made="guess", side=s,
             note="8871-56-370: read as the panel between the apron and the core support - confirm what it is")
        body("PT772-" + s, "PT772", "Rain rail (hatch opening side gutter), " + ("right" if k > 0 else "left"),
             (k * (P.v("roof_half") - 30), P.v("roof_rear_y"), P.v("roof_rear_z") - 30), ["roof_half", "roof_rear_y", "roof_rear_z", "tail_y", "tail_z"],
             _mate("PT768-" + s, (k * 80, -40, 100)), made="found", src=BP, side=s, zone="cargo", place_from="blueprint",
             note="reading: the rain rails are the hatch opening's side gutters; with the rear roof header and the rear end panel's top they make the hatch aperture")
    body("PT756", "PT756", "Dash panel, lower (firewall and toe board)", (0, P.v("firewall_y"), 520.0),
         ["firewall_y", "firewall_foot_y", "sill_in", "floor_rel"], _mate("PT778", (0, 200, 0)), made="guess", place_from="00-CAR zones (D-421)")
    body("PT757", "PT757", "Dash panel, upper", (0, P.v("firewall_y"), 700.0), ["firewall_y", "ws_base_z"],
         _mate("PT756", (0, 120, 80)), made="guess", place_from="00-CAR zones (D-421)")
    body("PT762", "PT762", "Upper cowling panel (plenum front)", (0, -560.0, 770.0), ["firewall_y", "hood_z0"],
         _mate("PT757", (0, 120, 100)), made="guess")
    body("PT764", "PT764", "Cowl panel (under the windshield)", (0, P.v("ws_base_y"), P.v("ws_base_z")), ["ws_base_y", "ws_base_z", "firewall_y"],
         _mate("PT757", (0, 40, 200)), made="found", src=BP + "; " + FOUND, place_from="blueprint")
    body("PT773-front", "PT773", "Roof header, front", (0, P.v("roof_front_y"), 1190.0), ["roof_front_y", "roof_half"],
         _mate("PT767-L", (0, 100, 160)), made="found", src=BP, zone="cabin", place_from="blueprint")
    body("PT773-rear", "PT773", "Roof header, rear (hatch hinge line)", (0, P.v("roof_rear_y"), P.v("roof_rear_z") - 30),
         ["roof_rear_y", "roof_rear_z", "roof_half"], _mate("PT767-L", (0, -100, 160)), made="found", src=BP, zone="cabin", place_from="blueprint")
    body("PT774", "PT774", "Roof panel", (0, P.v("roof_peak_y"), D["roof_top"]),
         ["height", "roof_peak_y", "roof_front_y", "roof_rear_y", "roof_rear_z", "roof_half", "roof_camber"],
         _mate("PT773-front", (0, 0, 300)), colour="skin", made="found", src=BP + "; " + FOUND, zone="cabin", place_from="datum DT06",
         note="origin at the roof's highest point, on DT06")
    body("PT753", "PT753", "Radiator support (core support)", (0, P.v("rad_y"), D["z_a"] + 200),
         ["rad_y", "rail_tip", "a_half"], _mate("PT755-L", (0, 260, 0)), made="guess")
    body("PT752", "PT752", "Nose panel", (0, P.v("rad_y") + 90, 410.0), ["rad_y", "front_oh"],
         _mate("PT753", (0, 160, 0)), made="guess")
    body("PT775", "PT775", "Rear end panel", (0, P.v("rear_panel_y"), 590.0), ["rear_panel_y", "rear_oh", "tail_z"],
         _mate("PT779", (0, -260, 0)), made="guess")
    body("PT776", "PT776", "Rear skirt panel", (0, P.v("rear_panel_y") - 10, 315.0), ["rear_panel_y"],
         _mate("PT775", (0, -120, -60)), made="guess")

    # the hard points as nodes: no solid, a place to measure against
    def node(nid, name, at, on, src, dims):
        out.append(part(nid, None, name=name, kind="node", origin=at, parent=SHELL, made_from="factory",
                        source=src, place_from=src, dims=dims, colour="steel", zone="underbody",
                        confirm_text="its place: from the drawing, not measured", note="on " + on))
    for s, k in SIDES:
        node("hp-A-" + s, "Front frame basic hole A, " + s, (k * P.v("a_half"), D["y_a"], D["z_a"]), "PT755-" + s, "datum DT10", ["a_half", "y_a"])
        node("hp-B-" + s, "Rear frame basic hole B, " + s, (k * P.v("b_half"), D["y_b"], D["floor_z"] - P.v("under_h")), "PT780-" + s, "datum DT11", ["b_half", "a_to_b"])
        node("hp-C-" + s, "Rear frame hole C, " + s, (k * P.v("c_half"), D["y_c"], D["z_c"]), "PT780-" + s, "datum DT12", ["c_half", "a_to_c"])
        node("hp-E-" + s, "Lower arm fixing hole E, " + s, (k * P.v("e_half"), D["y_e"], D["z_e"]), "PT780-" + s, "FSM S-002 p.14-24", ["e_half", "a_to_e"])
        node("hp-F-" + s, "Upper arm fixing hole F, " + s, (k * P.v("f_half"), D["y_f"], D["z_f"]), "PT780-" + s, "datum DT13", ["f_half", "a_to_f"])
        node("hp-DT14-" + s, "Front fender fixing nut, " + s, (k * P.v("nut_half"), 0.0, D["nut_z"]), "PT754-" + s, "datum DT14", ["nut_half", "nut_z_rel_a"])
        node("hp-DT03-" + s, "Rear wheel centre, " + s, (k * 699.75, D["y_rear_axle"], P.v("wheel_z")), SHELL, "datum DT03", ["wheelbase"])
    node("hp-DT02-R", "Front wheel centre, R", (710.0, 0.0, P.v("wheel_z")), SHELL, "datum DT02", ["wheel_z"])
    node("hp-front-end", "Overall length, front end (bumper)", (0.0, D["front_end"], 420.0), SHELL, "datum DT04", ["front_oh"])
    node("hp-rear-end", "Overall length, rear end (bumper)", (0.0, D["rear_end"], 420.0), SHELL, "datum DT04", ["rear_oh"])
    return out

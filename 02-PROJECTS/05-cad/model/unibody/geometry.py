"""unibody/geometry.py - the FB unibody's panels as rough sheet solids (FreeCAD only; 05-cad B01).

build(P) -> {part id: [(node name, shape, colour)]}, every shape drawn in the CAR's frame
(CAR_FRAME: fc_run moves each to its part's own frame by the part's origin). Each panel is a
polyline thickened to a sheet and extruded or lofted, a plate, or a box section - a mock-up to be
touched up with measurements, not a surface model. Every number is from unibody/params.py; the
few shaping constants written here (a flange's width, a pillar's section) are marked SHAPE and
govern nothing that mates.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import partlib as L  # noqa: E402
from unibody.params import SIDES, derived  # noqa: E402

CAR_FRAME = True


def _arc(cy, cz, r, a0, a1, n=24):
    """Points (y, z) on a circle about (cy, cz), angle a0 -> a1 in degrees (0 = +y, 90 = up)."""
    return [(cy + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def build(P):
    D = derived(P)
    t, tr = P.v("t_sheet"), P.v("t_rail")
    fz = D["floor_z"]
    si, so, st, sb = P.v("sill_in"), P.v("sill_out"), P.v("sill_top"), P.v("sill_bottom")
    out = {}

    def put(pid, shape, colour="steel"):
        out[pid] = [("body:" + pid, shape, colour)]

    # ---- floors ------------------------------------------------------------------------------
    tb, tt, th = P.v("tunnel_base") / 2, P.v("tunnel_top") / 2, P.v("tunnel_h")
    prof = [(-si, fz), (-tb, fz), (-tt, fz + th), (tt, fz + th), (tb, fz), (si, fz)]
    put("PT778", L.strip_xz(prof, P.v("kick_y"), P.v("firewall_foot_y"), t), "floor")
    rz, ky, wh = P.v("rear_floor_z"), P.v("kick_y"), P.v("wh_in")
    put("PT779", L.strip_yz([(ky, fz), (ky - 70, rz), (P.v("rear_panel_y"), rz)], -wh, wh, t), "floor")
    xm = L.beam((-si, -1300, fz - 20), (si, -1300, fz - 20), 60, 40)          # SHAPE 60 x 40
    xm = xm.fuse(L.beam((-si, ky - 30, (fz + rz) / 2), (si, ky - 30, (fz + rz) / 2), 50, 60))
    xm = xm.fuse(L.beam((-P.v("c_half"), P.v("rear_panel_y") + 60, rz - 25),
                        (P.v("c_half"), P.v("rear_panel_y") + 60, rz - 25), 60, 40))
    put("PT781", xm, "rail")

    # ---- per side ----------------------------------------------------------------------------
    fw, fh, uh = P.v("frail_w"), P.v("frail_h"), P.v("under_h")
    rw, rh = P.v("rrail_w"), P.v("rrail_h")
    ya, yb, yc, yf = D["y_a"], D["y_b"], D["y_c"], D["y_f"]
    for s, k in SIDES:
        # front rail: level from its tip to the firewall, down under the floor to B's rail
        ax = P.v("a_half")
        zc = D["z_a"] + fh / 2
        front = L.box_tube([(ax, ya + P.v("rail_tip"), zc), (ax, -250, zc),
                            (ax, P.v("firewall_foot_y") - 50, fz - uh + fh / 2)], fw, fh, tr)   # bottom meets the under-floor run
        under = L.box_tube([(ax, P.v("firewall_foot_y") - 20, fz - uh / 2),
                            (P.v("b_half"), yb + 70, fz - uh / 2)], fw, uh, tr)
        rail = front.fuse(under)
        if k < 0:
            rail = L.mirror_x(rail)
        put("PT755-" + s, rail, "rail")

        # rear rail: under the floor from B, up over the axle to C, on to the rear panel; the
        # upper link bracket (F) hangs from the rear floor beside it
        bx, cx = P.v("b_half"), P.v("c_half")
        zr = D["z_c"] + rh / 2
        r_under = L.box_tube([(bx, yb + 70, fz - uh / 2), (bx + 10, -2000, fz - uh / 2)], rw, uh, tr)
        r_up = L.box_tube([(bx + 10, -2000, fz - uh / 2 + 10), (cx - 10, -2560, zr), (cx, yc, zr),
                           (cx, P.v("rear_panel_y") + 20, zr)], rw, rh, tr)
        fx, zf = P.v("f_half"), D["z_f"]
        br = None
        for dx in (-22, 22):                                                    # SHAPE: 44 mm jaw
            web = L.plate([(fx + dx, yf - 45, zf - 45), (fx + dx, yf + 45, zf - 45),
                           (fx + dx, yf + 45, rz), (fx + dx, yf - 45, rz)], 3.0, (1, 0, 0))
            web = web.cut(L.cylinder_x(6.0, fx + dx - 2, fx + dx + 5, (0, yf, zf)))
            br = web if br is None else br.fuse(web)
        br = br.fuse(L.plate([(cx, yf - 45, rz - 3), (fx + 25, yf - 45, rz - 3),
                              (fx + 25, yf + 45, rz - 3), (cx, yf + 45, rz - 3)], 3.0, (0, 0, 1)))
        rr = r_under.fuse(r_up).fuse(br)
        if k < 0:
            rr = L.mirror_x(rr)
        put("PT780-" + s, rr, "rail")

        # torque box: the front rail's kick to the sill's front
        tq = L.beam((ax + fw / 2 - 5, P.v("firewall_foot_y") - 60, fz - 20),
                    (si + 5, P.v("firewall_foot_y") - 60, (sb + st) / 2), 90, 60)   # SHAPE 90 x 60
        put("PT782-" + s, L.mirror_x(tq) if k < 0 else tq, "rail")

        # sills: the outer C opening inward, the inner C closing it
        y0, y1 = -2050.0, -380.0
        outer = L.strip_xz([(si + 15, st), (so, st), (so, sb), (si + 15, sb)], y0, y1, -tr)
        inner = L.strip_xz([(si + 25, st + 1), (si, st + 1), (si, sb - 1), (si + 25, sb - 1)], y0 + 20, y1 - 340, tr)
        put("PT771-" + s, L.mirror_x(outer) if k < 0 else outer, "skin")
        put("PT783-" + s, L.mirror_x(inner) if k < 0 else inner, "rail")

        # hinge pillar (lower A) and the windshield pillar
        yd = P.v("door_front_y")
        hp = L.box_tube([(770, yd - 37, st - 5), (770, yd - 37, P.v("belt_z") - 20)], 70, 60, tr, up=(0, 1, 0))   # B01 2nd pass: top inside the skin
        ap = L.box_tube([(740, yd - 37, P.v("belt_z") - 20), (P.v("roof_half") + 35, P.v("ws_corner_y"), P.v("ws_corner_z") - 70),
                         (P.v("roof_half") + 20, P.v("roof_front_y") - 20, 1100)], 55, 70, tr)   # B01 2nd pass: along the glass edge
        put("PT769-" + s, L.mirror_x(hp) if k < 0 else hp)
        put("PT770-" + s, L.mirror_x(ap) if k < 0 else ap)

        # centre pillar: B-pillar foot on the sill, widening into the sail at the roof rail
        yr = P.v("door_rear_y")
        bot = [(750, yr - 70, st), (810, yr - 70, st), (810, yr, st), (750, yr, st)]
        top = [(P.v("roof_half") - 40, P.v("sail_rear_y"), 1110), (P.v("roof_half") + 15, P.v("sail_rear_y"), 1110),
               (P.v("roof_half") + 15, P.v("bpillar_top_y"), 1130), (P.v("roof_half") - 40, P.v("bpillar_top_y"), 1130)]   # B01 2nd pass
        bp = L.loft([bot, top], ruled=True)
        put("PT976-" + s, L.mirror_x(bp) if k < 0 else bp)

        # roof rail along the drip line
        rh_ = P.v("roof_half")
        rr2 = L.box_tube([(rh_ - 25, P.v("roof_front_y") - 20, 1150), (rh_ - 20, P.v("roof_peak_y"), 1175),
                          (rh_ - 25, P.v("roof_rear_y") - 10, P.v("roof_rear_z") - 65)], 45, 35, tr)   # B01 2nd pass: under the skin
        put("PT767-" + s, L.mirror_x(rr2) if k < 0 else rr2)

        # quarter panel: the side plate with the arch cut (centre the wheel, top at the fender
        # line), and its rear corner turned in to the rear end panel
        yax, wz, qx = D["y_rear_axle"], P.v("wheel_z"), P.v("half_w")
        ra = P.v("fender_line_r")
        dz = wz - sb
        a_lo = math.degrees(math.asin(-dz / ra))
        arch = _arc(yax, wz, ra, a_lo, 180 - a_lo, 36)                         # front foot -> over -> rear foot
        yb2, ycorner = -2800.0, P.v("rear_panel_y")   # B01 2nd pass: the tail tapers from -2700
        outline = [(yr - 30, sb)] + arch + [(yb2, sb + 40), (yb2, 800.0),
                                            (P.v("sail_rear_y"), P.v("belt_z")), (yr - 30, P.v("belt_z"))]
        q = L.plate([(qx - t, y, z) for y, z in outline], t, (1, 0, 0))
        cdx, cdy = 760 - (qx - t), ycorner - yb2
        cn = math.hypot(cdx, cdy)
        corner = L.plate([(qx - t, yb2 - 2, sb + 40), (760, ycorner, 330), (760, ycorner, 800),
                          (qx - t, yb2 - 2, 800.0)], t, (-cdy / cn, cdx / cn, 0))
        q = q.fuse(corner)
        put("PT768-" + s, L.mirror_x(q) if k < 0 else q, "skin")

        # rear wheelhouse: a half drum over the wheel and its inner wall
        whr = P.v("wh_r")
        drum = L.cylinder_x(whr + t, wh, qx - 5, (0, yax, wz)).cut(L.cylinder_x(whr, wh - 1, qx, (0, yax, wz)))
        wall = L.cylinder_x(whr + t, wh, wh + t, (0, yax, wz))
        import Part
        keep = Part.makeBox(qx, 2 * whr + 20, whr + 20, L.V(wh - 5, yax - whr - 10, rz - 60))
        whs = drum.fuse(wall).common(keep)
        put("PT777-" + s, L.mirror_x(whs) if k < 0 else whs)

        # cargo side deck behind the wheelhouse
        dk = L.plate([(wh, -2800, 670), (790, -2800, 670), (790, P.v("rear_panel_y") + 110, 670),
                      (wh, P.v("rear_panel_y") + 110, 670)], t, (0, 0, 1))
        put("PT784-" + s, L.mirror_x(dk) if k < 0 else dk)

        # front apron with the strut tower
        nz, nx = D["nut_z"], P.v("nut_half")
        ap_prof = [(ax + fw / 2, D["z_a"] + fh), (ax + 80, 560), (nx, nz), (nx + 35, nz)]
        apron = L.strip_xz(ap_prof, P.v("firewall_y"), P.v("rad_y") - 40, t)
        sx, sr, stz = P.v("strut_half"), P.v("strut_r"), P.v("strut_top")
        import Part
        tower = Part.makeCylinder(sr + t, stz - 480, L.V(sx, 0, 480), L.V(0, 0, 1)).cut(
            Part.makeCylinder(sr, stz - 480 - t, L.V(sx, 0, 479), L.V(0, 0, 1)))
        tower = tower.cut(Part.makeCylinder(25, 10, L.V(sx, 0, stz - 5), L.V(0, 0, 1)))  # SHAPE: the strut's hole
        apron = apron.fuse(tower)
        put("PT754-" + s, L.mirror_x(apron) if k < 0 else apron)

        # cowl side (the footwell's side wall) and the engine bay side panel
        fy = P.v("firewall_y")
        cs = L.plate([(si, fy, fz), (si, yd - 30, fz), (si, yd - 30, P.v("belt_z")), (si, fy, 790)], t, (1, 0, 0))
        put("PT766-" + s, L.mirror_x(cs) if k < 0 else cs)
        es = L.plate([(640, 160, 470), (640, P.v("rad_y") - 50, 470), (640, P.v("rad_y") - 50, 680), (640, 160, 700)], t, (1, 0, 0))
        put("PT761-" + s, L.mirror_x(es) if k < 0 else es)

        # rain rail: the hatch opening's side gutter, header to tail
        gt = L.beam((rh_ - 60, P.v("roof_rear_y") - 20, P.v("roof_rear_z") - 70),
                    (600, P.v("tail_y") + 20, P.v("tail_z") - 40), 40, 25)   # B01 2nd pass: inside the hatch opening       # SHAPE 40 x 25
        put("PT772-" + s, L.mirror_x(gt) if k < 0 else gt)

    # ---- across the car ----------------------------------------------------------------------
    fy, ffy = P.v("firewall_y"), P.v("firewall_foot_y")
    put("PT756", L.strip_yz([(ffy - 40, fz), (ffy, fz + 40), (fy, 520), (fy, 620)], -si, si, t))
    put("PT757", L.strip_yz([(fy, 620), (fy, 780), (fy - 20, 795)], -si, si, t))
    put("PT762", L.strip_yz([(-545, 830), (-565, 770), (fy, 762)], -si, si, t))
    put("PT764", L.strip_yz([(fy - 20, 795), (P.v("ws_base_y"), P.v("ws_base_z"))], -si, si, t))

    rhf = P.v("roof_half")
    put("PT773-front", L.box_tube([(-rhf + 15, P.v("roof_front_y") - 10, 1150), (rhf - 15, P.v("roof_front_y") - 10, 1150)], 60, 35, tr))
    put("PT773-rear", L.box_tube([(-rhf + 15, P.v("roof_rear_y") - 10, P.v("roof_rear_z") - 35),
                                  (rhf - 15, P.v("roof_rear_y") - 10, P.v("roof_rear_z") - 35)], 60, 35, tr))

    cam = P.v("roof_camber")

    def roof_sec(y, crown):
        prof = [(x, crown - t - cam * (x / rhf) ** 2) for x in [rhf * (i / 10.0 - 1) for i in range(21)]]
        return L.section_xz(y, prof, t)

    top = D["roof_top"]
    put("PT774", L.loft([roof_sec(P.v("roof_front_y"), 1215.0), roof_sec(-1350, 1248.0), roof_sec(P.v("roof_peak_y"), top),
                         roof_sec(-1900, 1240.0), roof_sec(P.v("roof_rear_y"), P.v("roof_rear_z"))]), "skin")

    ry, za = P.v("rad_y"), D["z_a"]
    put("PT753", L.tube([(-660, ry, za + 30), (660, ry, za + 30), (660, ry, 630), (-660, ry, 630), (-660, ry, za + 30)],
                        50, 50, up=(0, 1, 0)))                                  # SHAPE 50 x 50 box frame
    put("PT752", L.plate([(-700, ry + 90, 300), (700, ry + 90, 300), (640, ry + 90, 520), (-640, ry + 90, 520)], t, (0, 1, 0)))
    rpy = P.v("rear_panel_y")
    put("PT775", L.plate([(-740, rpy, 380), (740, rpy, 380), (740, rpy, 790), (-740, rpy, 790)], t, (0, 1, 0)))
    put("PT776", L.plate([(-740, rpy - 20, 250), (740, rpy - 20, 250), (740, rpy, 380), (-740, rpy, 380)], t, (0, 0.986, -0.164)))
    return out

"""Build the one combined model of the FB from the free CAD library (D-418).

Run headless, from the tree root:

    blender -b --factory-startup -P 01-REFERENCE/model/blend.py

Reads   01-REFERENCE/model/library/...        the downloaded models (out of git, see README.md)
        01-REFERENCE/model/rx7.glb         the bought SA body (S-037), as model/build.py left it
Writes  01-REFERENCE/model/out/rx7-fb.blend  the combined scene, one collection per piece
        01-REFERENCE/model/out/rx7-fb.glb    the same, shown pieces only, for any viewer
        01-REFERENCE/model/out/checks.json   every figure the pieces were checked against
        01-REFERENCE/model/out/*.png         side, top, front, rear and three-quarter renders

Owns no table. The pieces and their fits are the `blend` table in 01-REFERENCE; the
factory figures used here are 00-CAR `specs` rows, named beside each constant. Every
number below that is not from those rows is an assumption and says so (CLAUDE.md R11):
nothing about the real car is measured from any of these models.

Frame: millimetres, x to the car's right, y forward, z up, ground at z = 0, the front
axle at y = 0 and the centreline at x = 0.
"""

import bpy
import bmesh
import json
import math
import mathutils
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = os.path.join(ROOT, "01-REFERENCE", "model", "library")
OUT = os.path.join(ROOT, "01-REFERENCE", "model", "out")

# ---- factory figures (00-CAR specs) --------------------------------------------------
WHEELBASE = 2420.0            # SP-131
TRACK_F, TRACK_R = 55.9 * 25.4, 55.1 * 25.4   # SP-132
LENGTH = 170.1 * 25.4         # SP-133, US 1981-85 with the 5 mph bumpers
WIDTH = 65.7 * 25.4           # SP-134
HEIGHT = 49.6 * 25.4          # SP-135
CLEARANCE = 5.7 * 25.4        # SP-136
TYRE_W, TYRE_AR, RIM_IN = 185.0, 0.70, 13.0   # SP-128: 185/70HR13
RIM_W = 5.0 * 25.4            # SP-126: 5J x 13
TYRE_D = RIM_IN * 25.4 + 2 * TYRE_W * TYRE_AR
# 12A: 573 cc per rotor (SP-010) on the shared R = 105, e = 15 mm trochoid.
# Chamber displacement = 3*sqrt(3)*e*R*B, so the housing width is derived, never typed.
TROCHOID_R, TROCHOID_E = 105.0, 15.0
WIDTH_12A = 573000.0 / (3 * math.sqrt(3) * TROCHOID_E * TROCHOID_R)
WIDTH_13B = 80.0              # the 13B-REW model's housing, full size (checked below)

# ---- assumptions, one line each (R11: place them when the car is apart) ---------------
ENGINE_FRONT_Y = -120.0       # front face of the 12A's front plate, behind the front axle
ENGINE_SHAFT_Z = 360.0        # eccentric shaft height above the ground
EXPORT_SCALE_13B = 0.35       # ericthepoolboy's parts are 35 % of full size

CHECKS = {}
SILVER = (0.46, 0.48, 0.50, 1.0)  # Sunbeam Silver as a linear base colour, as model/build.py has it
# the FB shell's painted groups: body, bonnet, doors, roof, bumpers, pop-up covers
PAINTED = ("CARROCERIA", "CAPOT", "PUERTAS", "TECHO", "PARAG_DEL", "PARAG_TRAS", "TAPAFAROS")
APP_ART = os.path.join(ROOT, "02-APP", "app", "public", "car")
GLASS = None  # set by fb_body()
VIEWS = {}  # each app render's camera, filled by app_art()
GROUPS = {}  # the FB shell's named groups (Spanish), kept by fb_body() for locations()
APP_GLB = os.path.join(ROOT, "01-REFERENCE", "model", "rx7-fb.glb")
LAMP_TARGET = []  # the FB body's own tail lamp meshes, filled by fb_body()


def check(name, model, factory, unit="mm"):
    err = model - factory
    CHECKS[name] = {"model": round(model, 1), "factory": round(factory, 1), "error": round(err, 1),
                    "error_pct": round(100 * err / factory, 2) if factory else None, "unit": unit}


def f(*parts):
    return os.path.join(FILES, *parts)


def collection(name, shown=True):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    c.hide_render = not shown
    c.hide_viewport = not shown
    return c


def move_to(objs, coll):
    for o in objs:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)


def imported(fn):
    before = set(bpy.data.objects)
    fn()
    return [o for o in bpy.data.objects if o not in before]


def bounds(objs):
    for o in objs:
        if o.type == "MESH":
            o.data.update()
    bpy.context.view_layer.update()  # bound_box is only refreshed by an update
    pts = [o.matrix_world @ mathutils.Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    mn = mathutils.Vector([min(p[i] for p in pts) for i in range(3)])
    mx = mathutils.Vector([max(p[i] for p in pts) for i in range(3)])
    return mn, mx


def parent_all(objs, name):
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    for o in objs:
        if o.parent is None:
            o.parent = root
    return root


def bake(objs):
    """Apply every transform so bounds and exports read world millimetres."""
    bpy.context.view_layer.update()
    world = {o.name: o.matrix_world.copy() for o in objs}  # read them all before any changes
    for o in objs:
        if o.type == "MESH":
            o.data = o.data.copy()
            o.data.transform(world[o.name])
    for o in objs:
        if o.type == "MESH":
            o.parent = None
            o.matrix_world = mathutils.Matrix.Identity(4)
    for o in objs:
        if o.type != "MESH":
            bpy.data.objects.remove(o)


def material(name, rgba, metal=0.0, rough=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    m.diffuse_color = rgba
    return m


def paint(objs, mat):
    for o in objs:
        if o.type == "MESH":
            o.data.materials.clear()
            o.data.materials.append(mat)


# ---- the FB body ---------------------------------------------------------------------
def fb_body():
    """3D Warehouse '1983 Mazda RX7' (zxt): the only free FB shell with the right proportions.

    Its parts are named in Spanish (CARROCERIA body, PARAG bumpers, TAPAFAROS the pop-up
    covers...). Its aftermarket wheels ('Rueda ...') and its wing ('a28') are dropped. It
    is scaled uniformly to the factory length, and its width and height are then checks.
    """
    src = f("body", "fb-rx7-1983-modified-3dwarehouse-zxt", "1983 Mazda RX7.glb")
    objs = imported(lambda: bpy.ops.import_scene.gltf(filepath=src))
    bpy.context.view_layer.update()

    def under(o, word):
        while o:
            if o.name.startswith(word):
                return True
            o = o.parent
        return False

    meshes = [o for o in objs if o.type == "MESH"]
    wheels = [o for o in meshes if under(o, "Rueda")]
    wing = [o for o in meshes if under(o, "a28")]
    mirror_ids = {id(o) for o in meshes if under(o, "ESPEJOS")}
    panel_ids = {id(o) for o in meshes if any(under(o, w) for w in PAINTED)}
    glass_ids = {id(o) for o in meshes if under(o, "VIDRIOS")}
    for g in ("RADIADOR", "TAPAFAROS", "LUCES_DEL", "ESPEJOS", "VIDRIOS", "PUERTAS", "CAPOT"):
        GROUPS[g] = [o for o in meshes if under(o, g)]
    LAMP_TARGET[:] = [o for o in meshes if under(o, "LUCES_TRAS") or under(o, "LUZ_TRAS")]
    bake(objs)
    meshes = [o for o in bpy.data.objects if o in meshes]
    # glTF +z came in as Blender -y with the rear at +y: turn it so the front is +y.
    turn = mathutils.Matrix.Rotation(math.pi, 4, "Z")
    for o in meshes:
        o.data.transform(turn)
    wmn, wmx = bounds(wheels)
    front_wheels = [o for o in wheels if (o.matrix_world @ mathutils.Vector(o.bound_box[0])).y > (wmn.y + wmx.y) / 2]
    rear_wheels = [o for o in wheels if o not in front_wheels]
    fmn, fmx = bounds(front_wheels)
    rmn, rmx = bounds(rear_wheels)
    wheel_centre_f, wheel_centre_r = (fmn + fmx) / 2, (rmn + rmx) / 2
    body = [o for o in meshes if o not in wheels and o not in wing]
    for o in wheels + wing:
        bpy.data.objects.remove(o)
    mn, mx = bounds(body)
    s = LENGTH / (mx.y - mn.y)
    model_wb = (wheel_centre_f.y - wheel_centre_r.y) * s
    arch_mid_y = (wheel_centre_f.y + wheel_centre_r.y) / 2
    # centre it: x on the centreline, the arches' midpoint on the axles' midpoint,
    # the roof at the factory height.
    t = mathutils.Matrix.Translation((-(mn.x + mx.x) / 2, -arch_mid_y, -mx.z))
    m = mathutils.Matrix.Translation((0, -WHEELBASE / 2, HEIGHT)) @ mathutils.Matrix.Scale(s, 4) @ t
    for o in body:
        o.data.transform(m)
    mn, mx = bounds(body)
    check("fb_body.length", mx.y - mn.y, LENGTH)
    check("fb_body.width_with_mirrors", mx.x - mn.x, WIDTH)
    bare = [o for o in body if id(o) not in mirror_ids]
    bmn, bmx = bounds(bare)
    check("fb_body.width", bmx.x - bmn.x, WIDTH)
    check("fb_body.wheelbase_of_its_arches", model_wb, WHEELBASE)
    check("fb_body.lowest_point", mn.z, CLEARANCE)
    CHECKS["fb_body.scale"] = round(s, 4)
    CHECKS["fb_body.overhang_front"] = round(mx.y, 1)
    CHECKS["fb_body.overhang_rear"] = round(-WHEELBASE - mn.y, 1)
    global GLASS
    GLASS = material("glass", (0.02, 0.025, 0.03, 1), 0.0, 0.04)
    GLASS.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.6
    carpaint = material("carpaint", SILVER, 0.85, 0.32)
    carpaint.node_tree.nodes["Principled BSDF"].inputs["Coat Weight"].default_value = 1.0
    for o in body:
        o.data.shade_smooth()
        o.data.set_sharp_from_angle(angle=math.radians(40))
        for i, m in enumerate(o.data.materials):
            if id(o) in glass_ids or (m and "glass" in m.name.lower()):
                o.data.materials[i] = GLASS
        if id(o) not in panel_ids:
            continue
        for i, m in enumerate(o.data.materials):
            # every material on a painted panel is its paint, except a lamp's strong colour
            bsdf = m.node_tree.nodes.get("Principled BSDF") if m and m.use_nodes else None
            c = bsdf.inputs["Base Color"].default_value if bsdf else (0.8, 0.8, 0.8, 1)
            if m is None or (m.name != "glass" and max(c[:3]) - min(c[:3]) < 0.5):
                o.data.materials[i] = carpaint
    move_to(body, collection("fb_body"))
    return body


# ---- the SA body, hidden, for its detail ----------------------------------------------
def sa_overlay():
    src = os.path.join(ROOT, "01-REFERENCE", "model", "rx7.glb")
    if not os.path.exists(src):
        CHECKS["sa_overlay"] = "missing - build 01-REFERENCE/model first"
        return []
    objs = imported(lambda: bpy.ops.import_scene.gltf(filepath=src))
    bake(objs)
    meshes = [o for o in bpy.data.objects if o in objs and o.type == "MESH"]
    tyres = [o for o in meshes if o.name.lower().startswith("tire")]
    if len(tyres) != 4:
        CHECKS["sa_overlay"] = f"expected 4 tyres, found {len(tyres)}"
    cs = [sum(bounds([o]), mathutils.Vector()) / 2 for o in tyres]
    ys = sorted(c.y for c in cs)
    xs = sorted(c.x for c in cs)
    long_axis_y = (ys[-1] - ys[0]) > (xs[-1] - xs[0])
    if not long_axis_y:  # the model's length lies along x: turn it
        r = mathutils.Matrix.Rotation(math.pi / 2, 4, "Z")
        for o in meshes:
            o.data.transform(r)
        cs = [r @ c for c in cs]
    front = max(c.y for c in cs)
    rear = min(c.y for c in cs)
    # the front is the end nearer the bonnet badge: keep the build.py convention (y forward)
    wb = front - rear
    s = WHEELBASE / wb
    cx = sum(c.x for c in cs) / 4
    cz = sum(c.z for c in cs) / 4
    m = mathutils.Matrix.Translation((0, 0, TYRE_D / 2)) @ mathutils.Matrix.Scale(s, 4) @ \
        mathutils.Matrix.Translation((-cx, -front, -cz))
    for o in meshes:
        o.data.transform(m)
    mn, mx = bounds(meshes)
    CHECKS["sa_overlay.scale_to_fb_wheelbase"] = round(s, 4)
    CHECKS["sa_overlay.length_at_that_scale"] = round(mx.y - mn.y, 1)
    track = (max(c.x for c in cs) - min(c.x for c in cs)) * s
    check("sa_overlay.track_at_tyre_centres", track, (TRACK_F + TRACK_R) / 2)
    move_to(meshes, collection("sa_overlay", shown=False))
    sa_wheels(meshes, tyres)
    return meshes


def sa_wheels(meshes, tyres):
    """The SA's tyre, rim, brake disc and wheel nuts - everything within 320 mm of each tyre
    centre that is not paint - copied and moved onto the FB's factory track (SP-132). Its
    tyre is 599 mm across against the FB's derived 589; kept as modelled."""
    out = []
    for t in tyres:
        c = sum(bounds([t]), mathutils.Vector()) / 2
        parts = []
        for o in meshes:
            a, b = bounds([o])
            oc, size = (a + b) / 2, max(b - a)
            mat = o.active_material.name if o.active_material else ""
            if (oc - c).length < 320 and size < 650 and not mat.startswith("carpaint"):
                parts.append(o)
        side = 1 if c.x > 0 else -1
        track = TRACK_F if c.y > -WHEELBASE / 2 else TRACK_R
        dx = side * track / 2 - c.x
        for o in parts:
            n = o.copy()
            n.data = o.data.copy()
            n.data.transform(mathutils.Matrix.Translation((dx, 0, 0)))
            bpy.context.scene.collection.objects.link(n)
            out.append(n)
    CHECKS["wheels_sa.parts"] = len(out)
    move_to(out, collection("wheels_sa"))
    return out


# ---- wheels and tyres, from the specs alone -------------------------------------------
def wheels():
    rubber = material("tyre", (0.03, 0.03, 0.03, 1), 0, 0.9)
    steel = material("wheel", (0.55, 0.56, 0.58, 1), 0.9, 0.3)
    objs = []
    for name, x, y in (("wheel_fl", -TRACK_F / 2, 0), ("wheel_fr", TRACK_F / 2, 0),
                       ("wheel_rl", -TRACK_R / 2, -WHEELBASE), ("wheel_rr", TRACK_R / 2, -WHEELBASE)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=TYRE_D / 2, depth=TYRE_W,
                                            location=(x, y, TYRE_D / 2), rotation=(0, math.pi / 2, 0))
        t = bpy.context.object
        t.name = name + "_tyre"
        bev = t.modifiers.new("round", "BEVEL")
        bev.width, bev.segments = 35, 6
        paint([t], rubber)
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=RIM_IN * 25.4 / 2, depth=RIM_W + 4,
                                            location=(x, y, TYRE_D / 2), rotation=(0, math.pi / 2, 0))
        r = bpy.context.object
        r.name = name + "_rim"
        paint([r], steel)
        objs += [t, r]
    move_to(objs, collection("wheels", shown=False))
    CHECKS["wheels.tyre_diameter"] = round(TYRE_D, 1)
    return objs


# ---- the 12A, built from the 13B-REW working model ------------------------------------
STACK = [  # (file, flipped when printed, is a rotor housing) front to rear
    ("timing-cover", False, False),
    ("front-plate", False, False),
    ("front-rotor-housing", False, True),
    ("center-plate", False, False),
    ("rear-rotor-housing", True, True),
    ("rear-plate-plain-rotor", True, False),
    ("flywheel-13b", False, False),
]
SHAFT_XY = (157.0, 158.0)  # the bore every plate shares, full size mm (55 mm in the 35 % files)


def engine_12a():
    """ericthepoolboy's parts share one assembly frame: the shaft bore is at (157, 158) mm
    (35 % scale) in every plate. The ones printed face-down are turned back over, each part
    is stacked along the shaft, and the rotor housings are thinned from 80 to the 12A's
    derived width. The FB's 12A has no turbo, so the turbo, its manifold and the REW intake
    are left out; the carburettor and intake are not modelled."""
    folder = f("rotary", "13b-rew-working-model-mmf-ericthepoolboy")
    paths = {}
    for dp, _, fs in os.walk(folder):
        for n in fs:
            paths[n] = os.path.join(dp, n)
    k = 1.0 / EXPORT_SCALE_13B
    z = 0.0
    objs = []
    widths = {}
    for name, flipped, housing in STACK:
        o = imported(lambda: bpy.ops.wm.stl_import(filepath=paths[name + "-scaled.stl"]))[0]
        me = o.data
        mn, mx = bounds([o])
        m = mathutils.Matrix.Identity(4)
        if flipped:  # a turn about y through the part's own centre
            c = (mn + mx) / 2
            m = mathutils.Matrix.Translation(c) @ mathutils.Matrix.Rotation(math.pi, 4, "Y") @ \
                mathutils.Matrix.Translation(-c)
        me.transform(m)
        mn, mx = bounds([o])
        # shaft on (0, 0), the part's front face at z = 0, to full size
        if name.startswith("flywheel"):
            cx, cy = (mn.x + mx.x) / 2, (mn.y + mx.y) / 2
        else:
            cx, cy = SHAFT_XY[0] / k, SHAFT_XY[1] / k
        me.transform(mathutils.Matrix.Translation((-cx, -cy, -mn.z)))
        me.transform(mathutils.Matrix.Scale(k, 4))
        thick = (mx.z - mn.z) * k
        if housing:
            widths[name] = thick
            me.transform(mathutils.Matrix.Diagonal((1, 1, WIDTH_12A / thick, 1)))
            thick = WIDTH_12A
        me.transform(mathutils.Matrix.Translation((0, 0, z)))
        z += thick
        o.name = "engine_12a_" + name
        objs.append(o)
    for name, w in widths.items():
        check(f"engine_13b_model.{name}_width", w, WIDTH_13B)
    CHECKS["engine_12a.housing_width_derived"] = round(WIDTH_12A, 2)
    CHECKS["engine_12a.stack_length"] = round(z, 1)
    # into the car: the shaft along y, the front plate's face at ENGINE_FRONT_Y
    front_plate_z = [o for o in objs if o.name.endswith("front-plate")][0]
    fz = bounds([front_plate_z])[0].z
    m = mathutils.Matrix.Translation((0, ENGINE_FRONT_Y, ENGINE_SHAFT_Z)) @ \
        mathutils.Matrix.Rotation(math.pi / 2, 4, "X") @ mathutils.Matrix.Translation((0, 0, -fz))
    for o in objs:
        o.data.transform(m)
    for o in objs:
        a, b = bounds([o])
        CHECKS["engine_12a.part." + o.name[11:]] = [round(a.z), round(b.z), round(a.y), round(b.y)]
    mn, mx = bounds(objs)
    CHECKS["engine_12a.lowest_point"] = round(mn.z, 1)
    paint(objs, material("aluminium", (0.62, 0.63, 0.64, 1), 0.9, 0.45))
    move_to(objs, collection("engine_12a"))
    return objs


# ---- the LS3, hidden, for the swap's envelope -----------------------------------------
def engine_ls3():
    src = f("swap", "ls3-engine-assembly-3dwarehouse-tom", "LS3 Engine Assembly.glb")
    objs = imported(lambda: bpy.ops.import_scene.gltf(filepath=src))
    bake(objs)
    meshes = [o for o in bpy.data.objects if o in objs and o.type == "MESH"]
    mn, mx = bounds(meshes)
    ext = mx - mn
    # the long axis is the crank; lay it along y, front forward (assumed: the end with
    # the larger cross-section is the bellhousing, at the rear)
    axis = max(range(3), key=lambda i: ext[i])
    if axis == 0:
        r = mathutils.Matrix.Rotation(math.pi / 2, 4, "Z")
    elif axis == 2:
        r = mathutils.Matrix.Rotation(math.pi / 2, 4, "X")
    else:
        r = mathutils.Matrix.Identity(4)
    s = 1000.0 if ext[axis] < 20 else 1.0   # glTF metres to mm
    for o in meshes:
        o.data.transform(mathutils.Matrix.Scale(s, 4) @ r)
    mn, mx = bounds(meshes)
    CHECKS["engine_ls3.envelope_lwh"] = [round(mx.y - mn.y), round(mx.x - mn.x), round(mx.z - mn.z)]
    m = mathutils.Matrix.Translation((-(mn.x + mx.x) / 2, ENGINE_FRONT_Y - mx.y, ENGINE_SHAFT_Z - 0.35 * (mx.z - mn.z) - mn.z))
    for o in meshes:
        o.data.transform(m)
    paint(meshes, material("ls_orange", (0.8, 0.25, 0.05, 1), 0.2, 0.5))
    move_to(meshes, collection("engine_ls3", shown=False))
    return meshes


# ---- the FB tail lamp scan ------------------------------------------------------------
def _rotations():
    """The 24 proper rotations that map the axes onto each other."""
    import itertools
    out = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            m = mathutils.Matrix.Identity(3)
            for i in range(3):
                for j in range(3):
                    m[i][j] = signs[i] if perm[i] == j else 0
            if abs(m.determinant() - 1) < 1e-6:
                out.append(m)
    return out


def _icp(src, dst, rot, iters=40):
    """Rigid ICP of point list src onto dst (numpy), starting from rotation rot about the
    centroids. Returns (4x4 matrix, rms distance)."""
    import numpy as np
    from mathutils.kdtree import KDTree
    tree = KDTree(len(dst))
    for i, p in enumerate(dst):
        tree.insert(p, i)
    tree.balance()
    S = np.array(src)
    D = np.array(dst)
    R = np.array(rot)
    t = D.mean(0) - S.mean(0) @ R.T
    for _ in range(iters):
        P = S @ R.T + t
        Q = np.array([tree.find(mathutils.Vector(p))[0] for p in P])
        pc, qc = P.mean(0), Q.mean(0)
        H = (P - pc).T @ (Q - qc)
        U, _, Vt = np.linalg.svd(H)
        dR = Vt.T @ U.T
        if np.linalg.det(dR) < 0:
            Vt[-1] *= -1
            dR = Vt.T @ U.T
        R = dR @ R
        t = dR @ (t - pc) + qc
    P = S @ R.T + t
    rms = float(np.sqrt(np.mean([(tree.find(mathutils.Vector(p))[2]) ** 2 for p in P])))
    m = mathutils.Matrix.Identity(4)
    for i in range(3):
        for j in range(3):
            m[i][j] = R[i][j]
        m[i][3] = t[i]
    return m, rms


def tail_lamps(body):
    """Printables 993677: a scan of the passenger (right) wraparound housing, in mm, 1:1.

    It is registered onto the FB body's own right tail lamp by ICP (no scaling), trying all
    24 axis orientations and keeping the best; the rms distance is the check. The left is
    its mirror. Kept hidden unless the fit is within 25 mm rms."""
    import random
    src = f("body", "fb-rx7-taillight-housing-scan-printables-giooig13", "rx7-tail-light.stl")
    if not os.path.exists(src) or not LAMP_TARGET:
        CHECKS["tail_lamp"] = "missing scan or body lamp"
        return []
    o = imported(lambda: bpy.ops.wm.stl_import(filepath=src))[0]
    o.name = "tail_lamp_right"
    mn, mx = bounds([o])
    CHECKS["tail_lamp.scan_extents"] = sorted([round(e, 1) for e in (mx - mn)], reverse=True)
    right = [p for t in LAMP_TARGET for p in (t.matrix_world @ v.co for v in t.data.vertices) if p.x > 0]
    tmn = mathutils.Vector([min(p[i] for p in right) for i in range(3)])
    tmx = mathutils.Vector([max(p[i] for p in right) for i in range(3)])
    CHECKS["tail_lamp.body_lamp_extents"] = sorted([round(e, 1) for e in (tmx - tmn)], reverse=True)
    # The body's lamp is only a lens face; the scan is the whole housing. So the body's
    # points are fitted onto the scan (every lens point should lie on it) and inverted.
    random.seed(7)
    verts = [v.co.copy() for v in o.data.vertices]
    dst = random.sample(verts, min(20000, len(verts)))
    src = random.sample(right, min(1500, len(right)))
    best = None
    for rot in _rotations():
        m, rms = _icp(src, dst, rot, iters=15)
        if best is None or rms < best[1]:
            best = (m, rms)
    m, rms = _icp(src, dst, best[0].to_3x3(), iters=80)
    # _icp started from centroids; rebuild the full map body->scan and invert it
    o.data.transform(m.inverted())
    CHECKS["tail_lamp.icp_rms"] = round(rms, 1)
    left = o.copy()
    left.data = o.data.copy()
    left.data.transform(mathutils.Matrix.Diagonal((-1, 1, 1, 1)))
    left.data.flip_normals()
    left.name = "tail_lamp_left"
    bpy.context.scene.collection.objects.link(left)
    paint([o, left], material("tail_red", (0.55, 0.02, 0.02, 1), 0, 0.2))
    move_to([o, left], collection("tail_lamps", shown=rms <= 25))
    return [o, left]



# ---- locations for the Manual's "The car" view (D-421) ------------------------------------
def _pts(objs):
    return [o.matrix_world @ v.co for o in objs for v in o.data.vertices]


def _box(a, b):
    return [round(a.x), round(b.x), round(a.y), round(b.y), round(a.z), round(b.z)]


def locations(body, engine):
    """Where the models put each zone (a box) and some parts (points), in this file's frame,
    mm. Every value says what it comes from; none is measured (R11). Written to
    out/locations.json, and into 00-CAR zones.model_box_mm / parts.model_at_mm by
    locate.py."""
    bare = [o for o in body if o not in GROUPS.get("ESPEJOS", [])]
    mn, mx = bounds(bare)
    ws = [p for p in _pts(GROUPS["VIDRIOS"])]
    ws_front = max(ws, key=lambda p: p.y)           # the windscreen's foot: the firewall line
    glass_rear = min(ws, key=lambda p: p.y)         # the hatch glass's tail
    rad_mn, rad_mx = bounds(GROUPS["RADIADOR"])
    door_mn, door_mx = bounds(GROUPS["PUERTAS"])
    hood_mn, hood_mx = bounds(GROUPS["CAPOT"])
    hatch = [p for p in ws if p.y < door_mn.y - 100]  # the hatch glass: the glass behind the doors
    belt = door_mx.z + 50                           # assumed: the dash top, 50 mm above the doors' top (frameless glass: the beltline)
    rw = TYRE_D / 2
    zones = {
        "front": ([mn.x, rad_mn.y, 0], [mx.x, mx.y, hood_mx.z],
                  "FB shell: from the radiator's back face (RADIADOR) to the nose"),
        "engine_bay": ([-TRACK_F / 2 + 150, ws_front.y, 150], [TRACK_F / 2 - 150, rad_mn.y, hood_mx.z],
                       "FB shell: windscreen foot (VIDRIOS) to the radiator (RADIADOR); inside the tyres (SP-132), 150 mm up"),
        "dash": ([door_mn.x, ws_front.y - 450, 450], [door_mx.x, ws_front.y, belt],
                 "assumed: 450 mm behind the windscreen foot, 450 mm up to 50 mm above the beltline (PUERTAS top)"),
        "cabin": ([door_mn.x, door_mn.y - 250, 150], [door_mx.x, ws_front.y - 450, mx.z],
                  "FB shell: behind the dash to 250 mm past the doors' rear edge (PUERTAS)"),
        "cargo": ([door_mn.x, glass_rear.y, 400], [door_mx.x, door_mn.y - 250, glass_rear.z + 250],
                  "FB shell: behind the cabin to the hatch glass's tail (VIDRIOS)"),
        "rear": ([mn.x, mn.y, 0], [mx.x, glass_rear.y, glass_rear.z],
                 "FB shell: the hatch glass's tail to the rear bumper"),
        "underbody": ([mn.x, mn.y, 0], [mx.x, mx.y, 250],
                      "assumed: the footprint, ground to 250 mm"),
    }
    out_z = {}
    for k, (a, b, why) in zones.items():
        out_z[k] = {"boxes": [[round(a[0]), round(b[0]), round(a[1]), round(b[1]), round(a[2]), round(b[2])]], "from": why}
    doors = []
    for side in (-1, 1):
        ps = [p for p in _pts(GROUPS["PUERTAS"]) if p.x * side > 0]
        a = mathutils.Vector([min(p[i] for p in ps) for i in range(3)])
        b = mathutils.Vector([max(p[i] for p in ps) for i in range(3)])
        doors.append(_box(a, b))
    out_z["doors"] = {"boxes": doors, "from": "FB shell: each door (PUERTAS), left and right"}
    corners = []
    for x, y in ((-TRACK_F / 2, 0), (TRACK_F / 2, 0), (-TRACK_R / 2, -WHEELBASE), (TRACK_R / 2, -WHEELBASE)):
        corners.append([round(x - 150), round(x + 150), round(y - rw - 20), round(y + rw + 20), 0, round(TYRE_D + 40)])
    out_z["corners"] = {"boxes": corners, "from": "specs: wheel centres from SP-131 and SP-132, tyre from SP-128, 150 mm either side"}

    def c(objs):
        a, b = bounds(objs)
        return [round(v) for v in (a + b) / 2]

    def sides(objs):
        out = []
        for side in (-1, 1):
            ps = [p for p in _pts(objs) if p.x * side > 0]
            out.append([round(sum(p[i] for p in ps) / len(ps)) for i in range(3)])
        return out

    wf = [[round(-TRACK_F / 2), 0, round(rw)], [round(TRACK_F / 2), 0, round(rw)]]
    wr = [[round(-TRACK_R / 2), round(-WHEELBASE), round(rw)], [round(TRACK_R / 2), round(-WHEELBASE), round(rw)]]
    spec = "specs: wheel centres from SP-131, SP-132, SP-128"
    parts = {
        "PT001": ([c(engine)], "blend: engine_12a, its assumed place (blend.py ENGINE_*)"),
        "PT020": ([c(GROUPS["RADIADOR"])], "FB shell: RADIADOR"),
        "PT032": (sides(GROUPS["ESPEJOS"]), "FB shell: ESPEJOS, left and right"),
        "PT033": (sides([o for o in GROUPS["TAPAFAROS"] if bounds([o])[0].y > 0]), "FB shell: the front pop-up covers (TAPAFAROS); the motor is under each"),
        "PT035": (sides([o for o in GROUPS["TAPAFAROS"] if bounds([o])[0].y > 0]), "FB shell: the front pop-up covers (TAPAFAROS)"),
        "PT037": ([[0] + [round(sum(p[i] for p in hatch) / len(hatch)) for i in (1, 2)]], "FB shell: the middle of the hatch glass (VIDRIOS behind the doors)"),
        "PT055": ([[0, round(-WHEELBASE), round(rw)]], "specs: the rear axle line, SP-131"),
    }
    for pid in ("PT042", "PT043", "PT044", "PT045", "PT050", "PT056"):
        parts[pid] = (wf, spec + ", front")
    for pid in ("PT046", "PT047", "PT048", "PT049", "PT057"):
        parts[pid] = (wr, spec + ", rear")
    out_p = {k: {"points": v[0], "from": v[1]} for k, v in parts.items()}
    with open(os.path.join(OUT, "locations.json"), "w") as fh:
        json.dump({"frame": "mm; x right, y forward, z up; ground z = 0; front axle y = 0 (model/README.md)",
                   "zones": out_z, "parts": out_p}, fh, indent=1, sort_keys=True)
    CHECKS["locations.firewall_y"] = round(ws_front.y)


# ---- the app: its renders and its 3D view (D-420) ---------------------------------------
def app_frame():
    """The app's 3D view frames the car in centimetres, centred on the ground (CarModel.svelte)."""
    return mathutils.Matrix.Scale(0.1, 4) @ mathutils.Matrix.Translation((0, WHEELBASE / 2, 0))


def app_art(objs):
    """The Home and Manual renders, lit and framed as model/build.py lit the SA (D-415)."""
    sc = bpy.context.scene
    keep = (sc.render.engine, sc.render.resolution_x, sc.render.resolution_y, sc.camera, sc.world)
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = 1800, 900
    sc.view_settings.view_transform = "AgX"
    world = bpy.data.worlds.new("studio")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.20, 0.24, 0.30, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    sc.world = world
    lights = []
    for name, loc, energy, size in (("key", (-400, -300, 500), 1.6e7, 400), ("rim", (500, 400, 300), 9e6, 300),
                                    ("fill", (500, -400, 120), 4e6, 500)):
        light = bpy.data.objects.new(name, bpy.data.lights.new(name, "AREA"))
        light.data.energy, light.data.size = energy, size
        light.location = loc
        light.rotation_euler = (mathutils.Vector((0, 0, 50)) - mathutils.Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(light)
        lights.append(light)
    lo, hi = bounds(objs)
    centre = (lo + hi) / 2
    cam = bpy.data.objects.new("appcam", bpy.data.cameras.new("appcam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = 70
    cam.data.clip_end = 10000
    os.makedirs(APP_ART, exist_ok=True)
    for name, direction, dist in (("side", (-1, 0.0, 0.08), 1150), ("threequarter", (-0.72, 0.66, 0.2), 1150)):
        d = mathutils.Vector(direction).normalized()
        cam.location = centre + d * dist
        cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
        png = os.path.join(OUT, f"app-{name}.png")
        sc.render.filepath = png
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(png)
        sc.render.image_settings.file_format = "WEBP"
        sc.render.image_settings.quality = 88
        img.save_render(os.path.join(APP_ART, f"{name}.webp"))
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        proj = cam.calc_matrix_camera(dg, x=sc.render.resolution_x, y=sc.render.resolution_y)
        m = proj @ cam.matrix_world.inverted() @ app_frame()
        VIEWS[name] = {"width": sc.render.resolution_x, "height": sc.render.resolution_y,
                       "matrix": [[round(v, 9) for v in row] for row in m]}
        sc.render.image_settings.file_format = "PNG"
    for o in lights + [cam]:
        bpy.data.objects.remove(o)
    sc.render.engine, sc.render.resolution_x, sc.render.resolution_y, sc.camera, sc.world = keep
    sc.render.film_transparent = False


def app_model(objs):
    for o in bpy.data.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=APP_GLB, export_format="GLB", use_selection=True, export_apply=True,
                              export_yup=True, export_texcoords=False, export_cameras=False, export_lights=False)


def in_frame(objs, m, fn):
    """Run fn with objs moved into another frame, then move them back."""
    for o in objs:
        o.data.transform(m)
    try:
        fn(objs)
    finally:
        inv = m.inverted()
        for o in objs:
            o.data.transform(inv)


# ---- output ---------------------------------------------------------------------------
def render(name, view):
    scn = bpy.context.scene
    cam = bpy.data.objects.get("cam") or bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    if cam.name not in scn.collection.objects:
        scn.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.clip_end = 50000
    d, ortho = {"side": ((1, 0, 0), 5000), "top": ((0, 0, 1), 5000), "front": ((0, 1, 0), 2200),
                "rear": ((0, -1, 0), 2200), "three": ((1, 1.2, 0.6), 5200)}[view]
    d = mathutils.Vector(d).normalized()
    c = mathutils.Vector((0, -WHEELBASE / 2, 600))
    cam.location = c + d * 12000
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    if view == "top":
        cam.rotation_euler = (0, 0, math.pi / 2)
    cam.data.ortho_scale = ortho
    scn.camera = cam
    scn.render.engine = "BLENDER_WORKBENCH"
    scn.display.shading.light = "STUDIO"
    scn.display.shading.color_type = "MATERIAL"
    scn.display.shading.show_cavity = True
    scn.render.resolution_x, scn.render.resolution_y = 1600, 900
    scn.render.filepath = os.path.join(OUT, f"{name}-{view}.png")
    bpy.ops.render.render(write_still=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.unit_settings.system = "METRIC"
    scn.unit_settings.scale_length = 0.001
    w = bpy.data.worlds.new("w")
    w.color = (0.85, 0.85, 0.85)
    scn.world = w
    body = fb_body()
    sa_overlay()
    wheels()
    engine = engine_12a()
    engine_ls3()
    tail_lamps(body)
    locations(body, engine)
    for v in ("side", "top", "front", "rear", "three"):
        render("rx7-fb", v)
    cols = bpy.data.collections

    def only(*names, xray=False):
        for c in cols:
            c.hide_render = c.name not in names
        bpy.context.scene.display.shading.show_xray = xray
        bpy.context.scene.display.shading.xray_alpha = 0.25

    only("fb_body", "wheels_sa", "engine_12a", xray=True)
    render("xray-12a", "side")
    render("xray-12a", "top")
    only("fb_body", "wheels_sa", "engine_ls3", xray=True)
    render("xray-ls3", "side")
    render("xray-ls3", "top")
    only("fb_body", "wheels_sa", "tail_lamps")
    render("tail-lamps", "rear")
    render("tail-lamps", "three")
    only("sa_overlay")
    render("sa-overlay", "side")
    shown_set = ["fb_body", "wheels_sa", "engine_12a"]
    if "tail_lamps" in cols and CHECKS.get("tail_lamp.icp_rms", 99) <= 25:
        shown_set.append("tail_lamps")
    only(*shown_set)  # the shown set, as exported
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "rx7-fb.blend"))
    shown = [o for o in bpy.data.objects if o.type == "MESH"
             and not any(c.hide_render for c in o.users_collection)]
    # the app's set: what shows from outside - the engine is inside a closed body
    app = [o for o in shown if not any(c.name == "engine_12a" for c in o.users_collection)]
    if "--no-app" not in sys.argv:
        hidden = [c for c in cols if not c.hide_render and c.name not in ("fb_body", "wheels_sa", "tail_lamps")]
        for c in hidden:
            c.hide_render = True
        in_frame(app, app_frame(), app_art)
        with open(os.path.join(APP_ART, "views.json"), "w") as fh:
            json.dump({"about": "clip = matrix @ [x, y, z, 1] for a point in mm (01-REFERENCE/model/README.md frame); "
                       "pixel x = (clip.x / clip.w + 1) / 2 * width, y = (1 - clip.y / clip.w) / 2 * height (D-421)",
                       "views": VIEWS}, fh, indent=1, sort_keys=True)
        thin = []
        for o in app:
            if len(o.data.polygons) > 50000:  # the lamp scans: a million triangles each
                d = o.modifiers.new("thin", "DECIMATE")
                d.ratio = 30000 / len(o.data.polygons)
                thin.append((o, d))
        in_frame(app, app_frame(), app_model)
        for o, d in thin:
            o.modifiers.remove(d)
        for c in hidden:
            c.hide_render = False
    in_frame(shown, mathutils.Matrix.Scale(0.001, 4), lambda objs: (
        [o.select_set(o in objs) for o in bpy.data.objects],
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "rx7-fb.glb"), export_format="GLB",
                                  use_selection=True, export_apply=True, export_yup=True)))
    with open(os.path.join(OUT, "checks.json"), "w") as fh:
        json.dump(CHECKS, fh, indent=1, sort_keys=True)
    print("CHECKS", json.dumps(CHECKS, sort_keys=True))


main()

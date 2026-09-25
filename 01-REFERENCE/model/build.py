"""Build what the Rx7 app and the record use from the purchased 3D model (S-037).

Run headless, from the tree root:

    blender -b --factory-startup -P 01-REFERENCE/model/build.py

Reads   01-REFERENCE/model/1978-mazda-rx-7-mk1-sa.zip   (kept out of git - README.md)
Writes  01-REFERENCE/model/rx7.glb                        the app's 3D view (desktop only, out of git)
        01-REFERENCE/model/landmarks.json                 part centres, mm, for route estimates (out of git)
        02-PROJECTS/10-gui/app/public/car/*.webp          only with --renders: the app's renders come from
                                                          blend.py, the FB body, since D-420

Owns no table. Paint is Sunbeam Silver, read from 00-CAR/data/vehicle.csv (row `colour`)
only to name it here; the colour itself is set below.
"""

import bpy
import json
import math
import mathutils
import os
import sys
import tempfile
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.join(ROOT, "01-REFERENCE", "model")
ZIP = os.path.join(HERE, "1978-mazda-rx-7-mk1-sa.zip")
APP_ART = os.path.join(ROOT, "02-PROJECTS", "10-gui", "app", "public", "car")

# Sunbeam Silver, as a linear base colour - a metallic mid silver.
SILVER = (0.46, 0.48, 0.50, 1.0)
DECIMATE = 0.18  # about 140k faces from 790k: light enough to spin in the app


def unzip_obj() -> str:
    """The OBJ sits three zips deep; open each layer until it appears."""
    work = tempfile.mkdtemp(prefix="rx7-model-")
    layer = ZIP
    for _ in range(5):
        with zipfile.ZipFile(layer) as z:
            z.extractall(work)
            names = z.namelist()
        objs = [n for n in names if n.lower().endswith(".obj")]
        if objs:
            return os.path.join(work, objs[0])
        layer = os.path.join(work, next(n for n in names if n.lower().endswith(".zip")))
    raise SystemExit("no .obj inside the zip")


def load(path: str):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=path, forward_axis="NEGATIVE_Y", up_axis="Z", use_split_groups=True)
    meshes = []
    for o in list(bpy.context.scene.objects):
        # The seller's number plates carry its name; the car's own plate is not modelled.
        if o.type == "MESH" and any(s.material and s.material.name.startswith("LicPlate") for s in o.material_slots):
            bpy.data.objects.remove(o)
        elif o.type == "MESH":
            meshes.append(o)
    for m in bpy.data.materials:
        bsdf = m.node_tree.nodes.get("Principled BSDF") if m.use_nodes else None
        if not bsdf:
            continue
        if m.name.startswith("carpaint"):
            bsdf.inputs["Base Color"].default_value = SILVER
            bsdf.inputs["Metallic"].default_value = 0.85
            bsdf.inputs["Roughness"].default_value = 0.32
            bsdf.inputs["Coat Weight"].default_value = 1.0
        elif m.name.startswith("chrome") or m.name.startswith("mirror"):
            bsdf.inputs["Metallic"].default_value = 1.0
            bsdf.inputs["Roughness"].default_value = 0.08
        elif "glass" in m.name:
            bsdf.inputs["Roughness"].default_value = 0.05
            bsdf.inputs["Transmission Weight"].default_value = 0.6
    return meshes


def bounds(meshes):
    lo = mathutils.Vector((1e9,) * 3)
    hi = -lo
    for o in meshes:
        for c in o.bound_box:
            v = o.matrix_world @ mathutils.Vector(c)
            lo = mathutils.Vector(map(min, lo, v))
            hi = mathutils.Vector(map(max, hi, v))
    return lo, hi


def landmarks(meshes):
    """Each part's bounding-box centre and size, in millimetres (the OBJ is in centimetres).
    Axes: x to the car's right, y toward the front, z up; the ground is z = 0."""
    out = {}
    for o in meshes:
        lo, hi = bounds([o])
        out[o.name] = {
            "material": o.active_material.name if o.active_material else "",
            "centre": [round((a + b) / 2 * 10, 1) for a, b in zip(lo, hi)],
            "size": [round((b - a) * 10, 1) for a, b in zip(lo, hi)],
        }
    with open(os.path.join(HERE, "landmarks.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)


def render(meshes):
    sc = bpy.context.scene
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
    for name, loc, energy, size in (("key", (-400, -300, 500), 1.6e7, 400), ("rim", (500, 400, 300), 9e6, 300), ("fill", (500, -400, 120), 4e6, 500)):
        light = bpy.data.objects.new(name, bpy.data.lights.new(name, "AREA"))
        light.data.energy, light.data.size = energy, size
        light.location = loc
        light.rotation_euler = (mathutils.Vector((0, 0, 50)) - mathutils.Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(light)
    lo, hi = bounds(meshes)
    centre = (lo + hi) / 2
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = 70
    cam.data.clip_end = 10000
    os.makedirs(APP_ART, exist_ok=True)
    # The side is where this 1978 body matches the FB best; the three-quarter shows the rest.
    for name, direction, dist in (("side", (-1, 0.0, 0.08), 1150), ("threequarter", (-0.72, 0.66, 0.2), 1150)):
        d = mathutils.Vector(direction).normalized()
        cam.location = centre + d * dist
        cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
        png = os.path.join(tempfile.gettempdir(), f"rx7-{name}.png")
        sc.render.filepath = png
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(png)
        img.file_format = "WEBP"
        sc.render.image_settings.file_format = "WEBP"
        sc.render.image_settings.quality = 88
        img.save_render(os.path.join(APP_ART, f"{name}.webp"))
        sc.render.image_settings.file_format = "PNG"


def export_glb(meshes):
    for o in meshes:
        mod = o.modifiers.new("lighter", "DECIMATE")
        mod.ratio = DECIMATE
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(HERE, "rx7.glb"),
        export_format="GLB",
        export_apply=True,
        export_yup=True,
        export_texcoords=False,
        export_cameras=False,
        export_lights=False,
    )


def main():
    meshes = load(unzip_obj())
    landmarks(meshes)
    if "--renders" in sys.argv:  # the app shows the FB since D-420: blend.py writes them
        render(meshes)
    export_glb(meshes)
    print("RX7-MODEL built", len(meshes), "parts")


main()

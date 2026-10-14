"""The devices at the legs' far ends and the harness's common parts, in 3D for the app (D-515,
work row Y28). One command, from the tree's root:

    python3 02-PROJECTS/01-electrical/00-design/harness/cad/devices/build_devices.py
    python3 .../build_devices.py --only relay-micro-iso      one model, then the manifest
    python3 .../build_devices.py --check                     are the glb files current?
    python3 .../build_devices.py --selftest                  hold the manifest to its contract

It writes, into 02-APP/app/public/design/01-electrical/ (--out DIR for elsewhere):

  devices/<model>.glb    one per model: a vendor's or a community model found online (D-515),
                         converted by FreeCAD, or - where none was found - a dimensioned stand-in
                         drawn here from the PARAMS of its recipe, every number with its source
  devices/manifest.json  every device (01-electrical devices, DVxx) and common part (parts Pxxx,
                         another area's qualified, 04-luxury:LP58) with its glb, the scene node it
                         sits at, its size and origin, whether it is a stand-in, its cad row

Every glb is in millimetres, z up, in the part's own frame, as export_glb.py's are (00-design
README §13); each model's `origin` says where its zero is. Nothing here is measured (R11): every
entry is `confirm: true`, and a stand-in's numbers are a drawing's or an estimate, said so in
PARAMS.

Owns no fact. Reads, through `rx7.py export`: 01-electrical devices (which rows exist), relays
and fuses (how many relays and holders sit at each node), parts (quantities); 00-CAR cad
(that a found model's row exists). Reads scene.json (export_glb.py's) for the node names. Writes
nothing to the record. The found models' files are under 01-INTAKE/model/library/electrical/
<cad id>/ (git-ignored: their licences vary and the repository is public).

Exit 0 built (or current, or the selftest passes) - 1 the manifest breaks its contract or an
asset is stale - 2 under --check, assets not built on this machine - 3 a usage error or a tool
crash (freecadcmd missing, a found model's file missing).
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))           # 00-design
ROOT = os.path.abspath(os.path.join(DESIGN, "..", "..", ".."))            # the tree
TOOLS = os.path.join(DESIGN, "tools")
OUT_DEFAULT = os.path.join(ROOT, "02-APP", "app", "public", "design", "01-electrical")
SUB = "devices"                                       # the glb folder under OUT, and the manifest's
LIB = os.path.join(ROOT, "01-INTAKE", "model", "library", "electrical")
FREECADCMD = os.environ.get("FREECADCMD",
                            "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd")


class Fail(Exception):
    """rc 1."""


class Crash(Exception):
    """rc 3."""


# ================================================================================ materials ==
# name: (rgba, metallic, roughness)
MATS = {
    "black": ((0.07, 0.07, 0.08, 1.0), 0.0, 0.6),        # moulded plastic
    "dark": ((0.22, 0.22, 0.24, 1.0), 0.1, 0.5),
    "grey": ((0.55, 0.56, 0.58, 1.0), 0.0, 0.6),
    "metal": ((0.70, 0.70, 0.72, 1.0), 0.7, 0.35),       # steel, zinc
    "tin": ((0.78, 0.74, 0.60, 1.0), 0.7, 0.35),         # relay tabs, brass terminals
    "copper": ((0.72, 0.45, 0.22, 1.0), 0.7, 0.35),
    "pcb": ((0.08, 0.35, 0.18, 1.0), 0.0, 0.6),
    "pcb-blue": ((0.10, 0.20, 0.45, 1.0), 0.0, 0.6),
    "glass": ((0.03, 0.04, 0.06, 1.0), 0.1, 0.15),
    "clear": ((0.80, 0.86, 0.92, 0.35), 0.0, 0.1),       # a clear cover or lens
    "red": ((0.70, 0.10, 0.10, 1.0), 0.0, 0.5),
    "amber": ((0.90, 0.55, 0.10, 0.85), 0.0, 0.3),
    "white": ((0.85, 0.85, 0.85, 1.0), 0.0, 0.6),
    "blue": ((0.12, 0.25, 0.65, 1.0), 0.0, 0.5),
    "paper": ((0.12, 0.12, 0.12, 1.0), 0.0, 0.85),       # a speaker cone
}

# ============================================================================ found models ==
# Kept only where the licence allows this private use (D-515); the cad row says so. `file` is
# relative to LIB; `member` a file inside a zip. `rot` turns the file's frame into this one
# (degrees about x, then y, then z), then the box's base centre goes to the origin.
FOUND = {
    "teensy41": {
        "what": "PJRC Teensy 4.1 (the ICU and DCU carriers' socketed board, P142)",
        "file": "teensy41-step-github-xengi/Teensy_4.1_Assembly.STEP",
        "cad": "teensy41-step-github-xengi", "fits": "exact", "licence": "MIT",
        "rot": [0, 0, 0], "linear": 0.05, "angular": 0.3, "mat": "pcb",
        "origin": "base centre: x along the board (USB end at +x), y across, z=0 the lowest "
                  "point under the board, parts side up"},
    "xiao-esp32c3": {
        "what": "Seeed XIAO-format module (the ICU's radio co-processor, P116 - XIAO ESP32C3 "
                "class); the generic XIAO outline, the C3's antenna socket not drawn",
        "file": "seeeduino-xiao-step-github-frogpad/Seeeduino_Xiao.step",
        "cad": "seeeduino-xiao-step-github-frogpad", "fits": "close", "licence": "MIT",
        "rot": [90, 0, 0], "linear": 0.05, "angular": 0.3, "mat": "pcb",
        "origin": "base centre: z=0 the board's underside, the shield can and USB-C up"},
    "display-12p3": {
        "what": "Waveshare 12.3inch HDMI LCD (1920 x 720) - the candidate bar display (P118)",
        "file": "display-12p3in-hdmi-lcd-waveshare/12.3inch_HDMI_LCD_3D_file.zip",
        "member": "12_3inch-HMDI-LCD_V1.stp",
        "cad": "display-12p3in-hdmi-lcd-waveshare", "fits": "close",
        "licence": "Waveshare free download (no licence stated)",
        "rot": [90, 0, 0], "linear": 0.2, "angular": 0.4, "mat": "dark",
        "origin": "base centre: z=0 the rearmost point (the driver board behind the panel), "
                  "the glass facing +z, x along the bar"},
    "pololu-g2-24v21": {
        "what": "Pololu G2 High-Power Motor Driver 24v21 (#2995) - the blower final stage "
                "(luxury LP18, DV55); the md31b board the 18v25 and 24v21 share",
        "file": "pololu-g2-md31b-step-pololu/g2-high-power-motor-driver-md31b.step",
        "cad": "pololu-g2-md31b-step-pololu", "fits": "exact",
        "licence": "Pololu free download (no licence stated)",
        "rot": [0, 0, 0], "linear": 0.05, "angular": 0.3, "mat": "pcb-blue",
        "origin": "base centre: z=0 the lowest point (the through-hole pins under the board), "
                  "parts side up"},
    "atc-block-4": {
        "what": "OptiFuse BLR-504 ATC fuse block, 4-position, bussed input (P001, blocks A "
                "and B at the dash node)",
        "file": "optifuse-blr-504-datasheet-optifuse/BLR-504.stp.zip", "member": "BLR-504.stp",
        "cad": "optifuse-blr-504-datasheet-optifuse", "fits": "exact",
        "licence": "OptiFuse free manufacturer download (no licence stated)",
        "rot": [90, 0, 0], "linear": 0.05, "angular": 0.3, "mat": "black",
        "origin": "base centre: z=0 the mounting face, the fuses and the input stud up"},
}


# ================================================================== stand-ins: the recipes ==
# Each recipe: PARAMS {name: (mm, source)} and a function of them returning primitives
#   ("box", node, mat, [x0, y0, z0, dx, dy, dz])
#   ("cyl", node, mat, [x, y, z, r, h, axis])          base centre, axis "x" | "y" | "z"
#   ("cone", node, mat, [x, y, z, r1, r2, h, axis])
#   ("hex", node, mat, [x, y, z, across_flats, h])       along z
# The sources: a drawing read here (file and page), a published figure, or "estimate" with its
# basis. Every one is confirm (R11): no device has been measured.
DS_871 = "Song Chuan 871 datasheet p.238 outline (relay-datasheets-picker-songchuan)"
EST = "estimate"


def bc(node, mat, w, d, h, z0=0.0, x=0.0, y=0.0):
    """A box centred on (x, y), its base at z0."""
    return ("box", node, mat, [x - w / 2.0, y - d / 2.0, z0, w, d, h])


def r_relay(p, mini=False):
    out = [bc("body", "black", p["w"], p["d"], p["h"])]
    # bottom view (ISO 7588 micro / mini): 86, 87a, 85 in the upper row, 87 then 30 below
    s, t, L = p["coil_pitch"], p["tab_t"], p["tab_len"]
    for name, x, y, wide, along in (("86", -s, p["row1"], p["coil_tab_w"], "y"),
                                    ("87a", 0.0, p["row1"], p["power_tab_w"], "y"),
                                    ("85", s, p["row1"], p["coil_tab_w"], "y"),
                                    ("87", 0.0, p["row2"], p["power_tab_w"], "x"),
                                    ("30", 0.0, p["row3"], p["power_tab_w"], "x")):
        w, d = (t, wide) if along == "y" else (wide, t)
        out.append(bc("tab " + name, "tin", w, d, L, z0=-L, x=x, y=y))
    return out


def r_socket(p):
    w, d, h, wall = p["w"], p["d"], p["h"], p["wall"]
    return [bc("shell", "black", w, d, h - wall, z0=0.0),
            bc("rim", "black", w, d, wall, z0=h - wall),
            bc("relay seat", "dark", w - 2 * wall, d - 2 * wall, 0.6, z0=h),
            bc("flange", "black", w + 2 * p["flange"], d + 2 * p["flange"], 2.0,
               z0=h - p["flange_below_top"])]


def r_inline(p):
    out = [bc("body", "black", p["w"], p["d"], p["h"]),
           bc("cap", p.get("cap_mat", "red"), p["w"] * 0.9, p["d"] * 0.9, p["cap_h"], z0=p["h"])]
    for side in (-1, 1):
        out.append(("cyl", "lead %s" % ("A" if side < 0 else "B"), "red",
                    [side * p["w"] / 2.0, 0.0, p["h"] / 2.0, p["lead_d"] / 2.0, p["lead_len"],
                     "x" if side > 0 else "-x"]))
    return out


def r_stud_block(p):
    out = [bc("base", "black", p["w"], p["d"], p["h"]),
           bc("cover", p.get("cover_mat", "clear"), p["w"] * 0.92, p["d"] * 0.8, p["cover_h"],
              z0=p["h"])]
    n = int(p["studs"])
    for k in range(n):
        x = (k - (n - 1) / 2.0) * p["stud_pitch"]
        out.append(("cyl", "stud %d" % (k + 1), "metal",
                    [x, -p["d"] / 2.0 + p["stud_r"] * 3, p["h"], p["stud_r"], p["stud_h"], "z"]))
    return out


def r_busbar(p):
    out = [bc("base", "black", p["w"], p["d"], p["h"]),
           bc("cover", "clear", p["w"] * 0.96, p["d"] * 0.9, p["cover_h"], z0=p["h"])]
    n = int(p["gangs"])
    for k in range(n):
        x = (k - (n - 1) / 2.0) * (p["w"] - 30.0) / max(n - 1, 1)
        out.append(("cyl", "screw %d" % (k + 1), "metal", [x, 0.0, p["h"], 2.4, 6.0, "z"]))
    for side in (-1, 1):
        out.append(("cyl", "stud %s" % ("L" if side < 0 else "R"), "metal",
                    [side * (p["w"] / 2.0 - 8.0), 0.0, p["h"], 4.0, 14.0, "z"]))
    return out


def r_fuse_block_st(p):
    out = [bc("base", "black", p["w"], p["d"], p["h"]),
           bc("cover", "clear", p["w"] - 4.0, p["d"] - 4.0, p["cover_h"], z0=p["h"])]
    for i in range(3):
        for j in range(2):
            out.append(bc("fuse %d" % (i * 2 + j + 1), "red", 19.0, 5.0, 18.0, z0=p["h"],
                          x=(i - 1) * 26.0, y=(j - 0.5) * 30.0))
    out.append(("cyl", "input stud #10-32", "metal",
                [p["w"] / 2.0 - 8.0, 0.0, p["h"], 2.4, 14.0, "z"]))
    return out


def r_board(p):
    out = [bc("board", "pcb-blue", p["w"], p["d"], p["t"])]
    for name, x, y, w, d, h in p["features"]:
        out.append(bc(name, "dark" if "FFC" in name else "metal" if "USB" in name else "black",
                      w, d, h, z0=p["t"], x=x, y=y))
    return out


def r_servo(p):
    w, d, h = p["w"], p["d"], p["h"]
    return [bc("case", "black", w, d, h),
            bc("ears", "black", p["ears_w"], d, p["ears_t"], z0=p["ears_z"]),
            ("cyl", "output boss", "black", [w / 2.0 - p["spline_off"], 0.0, h, 6.5, 2.0, "z"]),
            ("cyl", "output spline 25T", "metal",
             [w / 2.0 - p["spline_off"], 0.0, h + 2.0, p["spline_d"] / 2.0, 4.0, "z"])]


def r_can(p):
    """A motor or sender: a can along z on a flange, optional shaft and a side box."""
    out = [("cyl", "can", p.get("mat", "metal"), [0, 0, 0, p["d"] / 2.0, p["h"], "z"])]
    if p.get("flange_d"):
        out.append(("cyl", "flange", "metal", [0, 0, 0, p["flange_d"] / 2.0, p["flange_t"], "z"]))
    if p.get("shaft_d"):
        out.append(("cyl", "shaft", "metal",
                    [0, 0, -p["shaft_len"], p["shaft_d"] / 2.0, p["shaft_len"], "z"]))
    if p.get("box_w"):
        out.append(bc("gearbox" if p.get("gear") else "housing", "grey", p["box_w"], p["box_d"],
                      p["box_h"], z0=-p["box_h"], x=p.get("box_x", 0.0)))
    if p.get("hex"):
        out.append(("hex", "hex", "metal", [0, 0, -p["hex_h"], p["hex"], p["hex_h"]]))
    if p.get("wheel_d"):
        out.append(("cyl", "blower wheel", "black",
                    [0, 0, -p["shaft_len"] - p["wheel_h"], p["wheel_d"] / 2.0, p["wheel_h"], "z"]))
    return out


def r_lamp(p):
    out = [bc("housing", "black", p["w"], p["d"], p["h"])]
    out.append(bc("lens", p.get("lens", "clear"), p["w"] - 4.0, 3.0, p["h"] - 4.0,
                  z0=2.0, y=p["d"] / 2.0 + 1.5))
    return out


def r_round_lamp(p):
    return [("cyl", "bucket", "black", [0, 0, 0, p["d"] / 2.0 - 4.0, p["depth"], "z"]),
            ("cyl", "lens", "clear", [0, 0, p["depth"], p["d"] / 2.0, 6.0, "z"])]


def r_speaker(p):
    return [("cyl", "basket and magnet", "dark",
             [0, 0, -p["depth"], p["magnet_d"] / 2.0, p["depth"], "z"]),
            ("cyl", "flange", "black", [0, 0, 0, p["d"] / 2.0, 4.0, "z"]),
            ("cone", "cone", "paper", [0, 0, -p["cone_depth"], p["d"] * 0.18,
                                       p["d"] / 2.0 - 8.0, p["cone_depth"], "z"])]


def r_gauge(p):
    return [("cyl", "body", "black", [0, 0, -p["depth"], p["d"] / 2.0, p["depth"], "z"]),
            ("cyl", "bezel", "dark", [0, 0, 0, p["bezel_d"] / 2.0, p["bezel_t"], "z"]),
            ("cyl", "face", "glass", [0, 0, p["bezel_t"], p["d"] / 2.0 - 3.0, 0.5, "z"])]


def r_battery(p):
    out = [bc("case", "dark", p["w"], p["d"], p["h"])]
    for name, x in (("post +", -p["post_x"]), ("post -", p["post_x"])):
        out.append(("cone", name, "tin", [x, p["post_y"], p["h"], p["post_d_base"] / 2.0,
                                          p["post_d_top"] / 2.0, p["post_h"], "z"]))
    return out


def r_box(p):
    out = [bc("body", p.get("mat", "black"), p["w"], p["d"], p["h"])]
    if p.get("knob_d"):
        out.append(("cyl", "knob", "red", [0, 0, p["h"], p["knob_d"] / 2.0, p["knob_h"], "z"]))
    if p.get("heatsink"):
        for k in range(int(p["heatsink"])):
            x = (k - (p["heatsink"] - 1) / 2.0) * (p["w"] - 20.0) / max(p["heatsink"] - 1, 1)
            out.append(bc("fin %d" % (k + 1), "dark", 3.0, p["d"] - 10.0, 8.0, z0=p["h"], x=x))
    if p.get("cone_d"):
        out += [("cyl", "driver surround", "black",
                 [0, 0, p["h"], p["cone_d"] / 2.0, 3.0, "z"]),
                ("cone", "driver cone", "paper",
                 [0, 0, p["h"] - p["cone_d"] * 0.2, p["cone_d"] * 0.15, p["cone_d"] / 2.0 - 10.0,
                  p["cone_d"] * 0.2, "z"])]
    return out


MICRO_RELAY = {
    "w": (15.5, DS_871), "d": (23.0, DS_871), "h": (25.4, DS_871),
    "tab_len": (11.2, DS_871), "tab_t": (0.8, DS_871),
    "power_tab_w": (6.3, DS_871), "coil_tab_w": (4.8, DS_871),
    "coil_pitch": (4.5, DS_871 + " (9 between 86 and 85)"),
    "row1": (7.0, DS_871 + " (the upper row; its offset from centre read off the view)"),
    "row2": (1.0, DS_871 + " (6 below the upper row)"),
    "row3": (-7.0, DS_871 + " (8 below 87)"),
}
MINI_RELAY = {
    "w": (28.0, EST + ": the mini ISO (ISO 7588-1) body, 28 x 28; the Picker PC792E drawing "
                  "not read"),
    "d": (28.0, EST + ": as w"), "h": (31.0, EST + ": a sealed mini relay with its tab skirt"),
    "tab_len": (9.5, EST + ": ISO 7588 mini tab length"), "tab_t": (0.8, EST),
    "power_tab_w": (9.5, EST + ": ISO 7588 mini power tab"), "coil_tab_w": (6.3, EST),
    "coil_pitch": (8.0, EST), "row1": (8.0, EST), "row2": (0.0, EST), "row3": (-8.0, EST),
}

STANDINS = {
    # ------------------------------------------------------------------- the common parts --
    "relay-micro-iso": {"what": "ISO micro relay, Song Chuan 871-1C-C-D1 (P003)",
                        "params": MICRO_RELAY, "make": r_relay,
                        "origin": "z=0 the tab face (the socket's face), body +z, tabs -z; "
                                  "x across the 86-85 row"},
    "relay-mini-iso-sealed": {"what": "Sealed mini ISO relay, Picker PC792E (P004, K9)",
                              "params": MINI_RELAY, "make": r_relay,
                              "origin": "z=0 the tab face, body +z, tabs -z"},
    "socket-micro-iso-panel": {
        "what": "Panel-mount micro relay socket (P006, Waytek 75290)",
        "params": {"w": (21.0, EST + ": the 871's 15.5 plus 2.75 mm walls - no drawing found"),
                   "d": (28.5, EST + ": the 871's 23 plus 2.75 mm walls"),
                   "h": (24.0, EST + ": a socket deep enough for 11.2 mm tabs and the crimps"),
                   "wall": (2.75, EST), "flange": (3.0, EST), "flange_below_top": (6.0, EST)},
        "make": r_socket, "origin": "z=0 the wire end, the relay seat at the top (+z)"},
    "socket-mini-weatherproof": {
        "what": "Chief weatherproof 5-pin mini relay connector (P005, K9's socket)",
        "params": {"w": (36.0, EST + ": round the 28 mm mini body with 4 mm walls"),
                   "d": (36.0, EST), "h": (40.0, EST + ": with its seal skirt"),
                   "wall": (4.0, EST), "flange": (4.0, EST + ": the mounting ear"),
                   "flange_below_top": (12.0, EST)},
        "make": r_socket, "origin": "z=0 the wire end, the relay seat at the top"},
    "inline-atc-sealed": {
        "what": "Sealed inline ATC fuse holder, 14 AWG leads (P002, Waytek 46047)",
        "params": {"w": (48.0, EST + ": body length - the Waytek drawing not read"),
                   "d": (22.0, EST), "h": (14.0, EST), "cap_h": (12.0, EST + ": the snap cap"),
                   "lead_d": (3.4, "14 AWG insulated, about 3.4 mm"),
                   "lead_len": (60.0, EST + ": a stub of each lead, not its length")},
        "make": r_inline, "origin": "base centre of the body; the leads run along x"},
    "inline-maxi-sealed": {
        "what": "Sealed inline MAXI fuse holder, 10 AWG leads (P189)",
        "params": {"w": (70.0, EST + ": a weatherproof MAXI holder body"), "d": (36.0, EST),
                   "h": (24.0, EST), "cap_h": (16.0, EST),
                   "lead_d": (5.0, "10 AWG insulated, about 5 mm"), "lead_len": (60.0, EST)},
        "make": r_inline, "origin": "base centre of the body; the leads run along x"},
    "midi-block": {
        "what": "MIDI / AMI fuse block, sealed cover, bolt-down (P053; F17, F18 at the starter)",
        "params": {"w": (60.0, EST + ": a single MIDI holder"), "d": (28.0, EST),
                   "h": (18.0, EST), "cover_h": (14.0, EST), "studs": (2, "a MIDI fuse's two "
                   "bolts"), "stud_pitch": (36.0, EST), "stud_r": (3.0, "M6"),
                   "stud_h": (16.0, EST)},
        "make": r_stud_block, "origin": "z=0 the mounting face, centred"},
    "mrbf-holder": {
        "what": "MRBF terminal fuse holder (P051; Blue Sea 5191 class, on the disconnect's stud)",
        "params": {"w": (52.0, EST + ": a 5191 class terminal fuse block - no drawing read"),
                   "d": (38.0, EST), "h": (12.0, EST), "cover_h": (16.0, EST),
                   "studs": (2, "the terminal stud and the output stud"),
                   "stud_pitch": (30.0, EST), "stud_r": (4.0, "3/8 in class"),
                   "stud_h": (20.0, EST)},
        "make": r_stud_block, "origin": "z=0 the face that sits on the stud, centred"},
    "class-t-block": {
        "what": "Class-T fuse block with cover, 110-200 A (P047)",
        "params": {"w": (125.0, EST + ": a Class-T 110-200 A holder with cover"),
                   "d": (42.0, EST), "h": (16.0, EST), "cover_h": (30.0, EST),
                   "studs": (2, "line and load studs"), "stud_pitch": (95.0, EST),
                   "stud_r": (4.8, "3/8 in"), "stud_h": (22.0, EST),
                   "cover_mat": ("red", "the usual red cover")},
        "make": r_stud_block, "origin": "z=0 the mounting face, centred"},
    "busbar-10": {
        "what": "Blue Sea 2300 busbar, 10-gang 150 A, with cover (P007)",
        "params": {"w": (190.0, EST + ": 10 screws and two studs; Blue Sea's drawing not read "
                                       "(its page refused the fetch)"),
                   "d": (44.0, EST), "h": (14.0, EST), "cover_h": (24.0, EST),
                   "gangs": (10, "P007: 10-gang")},
        "make": r_busbar, "origin": "z=0 the mounting face, centred"},
    "disconnect": {
        "what": "Master battery disconnect switch (P049, not chosen)",
        "params": {"w": (90.0, EST + ": a rotary 300 A class switch"), "d": (90.0, EST),
                   "h": (45.0, EST), "knob_d": (55.0, EST), "knob_h": (25.0, EST)},
        "make": r_box, "origin": "z=0 the mounting face, centred, the knob +z"},
    "comfort-block-st6": {
        "what": "Blue Sea 5028 ST blade fuse block, 6 circuits with cover (P164, O15 comfort "
                "block C)",
        "params": {"w": (123.8, "retailer listing: 4 7/8 in long (Blue Sea's page refused the "
                                "fetch)"),
                   "d": (84.1, "retailer listing: 3 5/16 in wide"),
                   "h": (18.0, EST + ": the base; 38.1 overall with the cover (1 1/2 in, "
                                     "retailer listing)"),
                   "cover_h": (20.1, "38.1 overall less the base")},
        "make": r_fuse_block_st, "origin": "z=0 the mounting face, centred, the cover +z"},
    "battery-ionic-s9": {
        "what": "Ionic IC-12V40-S9H heated LiFePO4 battery, rear mount (00-CAR planned P-002)",
        "params": {"w": (230.0, "D-239: 230 L"), "d": (170.0, "D-239: 170 W"),
                   "h": (190.0, "D-239: 190 H"),
                   "post_x": (80.0, EST + ": the posts' spacing from centre"),
                   "post_y": (-55.0, EST),
                   "post_d_base": (17.5, "SAE tapered post (D-234), positive, base"),
                   "post_d_top": (15.9, "SAE tapered post, top"), "post_h": (16.0, EST)},
        "make": r_battery, "origin": "z=0 the base, centred, the posts +z"},
    "bt817-me817ev": {
        "what": "Bridgetek ME817EV BT817 EVE evaluation board (P117)",
        "params": {"w": (165.0, "DS_ME817EV v1.1 Fig 6-1 (bt817-me817ev-datasheet-bridgetek)"),
                   "d": (100.0, "DS_ME817EV Fig 6-1"), "t": (1.6, EST + ": board thickness"),
                   "features": ([("FFC LCD_LVDS_40P", -50.0, 44.0, 32.0, 6.0, 2.5),
                                 ("FFC LCD_RGB_50P", 0.0, 4.0, 40.0, 6.0, 2.5),
                                 ("CN8 2x8 header", 21.0, -4.0, 6.0, 21.0, 8.5),
                                 ("USB-C USBC1", 0.0, -46.0, 9.0, 8.0, 3.2),
                                 ("USB-C USBC2", 41.0, -46.0, 9.0, 8.0, 3.2),
                                 ("BT817", -10.0, 26.0, 9.0, 9.0, 1.0)],
                                "Fig 6-1, the features' places read off the figure, rounded"),
                   },
        "make": r_board, "origin": "z=0 the board's underside, centred, parts up"},
    # ------------------------------------------------------------------------ the devices --
    "servo-fs5115m": {
        "what": "FEETECH FS5115M servo (luxury LP19; the three HVAC door servos, DV59)",
        "params": {"w": (40.1, "FS5115M spec sheet 6-1 (feetech-fs5115m-datasheet-pololu)"),
                   "d": (20.1, "FS5115M spec sheet 6-1"),
                   "h": (38.9, "FS5115M spec sheet 6-1"),
                   "ears_w": (54.0, EST + ": a standard servo's mounting ears"),
                   "ears_t": (2.5, EST), "ears_z": (27.0, EST),
                   "spline_off": (10.0, EST + ": the output's distance from the case end"),
                   "spline_d": (5.9, "FS5115M spec sheet 6-9: 25T / 5.9 mm")},
        "make": r_servo, "origin": "z=0 the case bottom, centred, the output spline +z at +x"},
    "aem-gauge-52": {
        "what": "AEM 30-0300 X-Series wideband gauge, 52 mm (DV44)",
        "params": {"d": (52.4, "52 mm gauge class (AEM 30-0300)"),
                   "depth": (40.0, EST + ": the install drawing not on this machine"),
                   "bezel_d": (60.0, EST), "bezel_t": (6.0, EST)},
        "make": r_gauge, "origin": "z=0 the bezel's back (the panel face), the face +z"},
    "blower-motor": {
        "what": "Blower motor, Four Seasons 35483 class, 2-wire (DV27, luxury LP17)",
        "params": {"d": (100.0, EST + ": the motor can"), "h": (85.0, EST),
                   "flange_d": (135.0, EST + ": the mounting flange on the HVAC case"),
                   "flange_t": (4.0, EST), "shaft_d": (8.0, EST), "shaft_len": (30.0, EST),
                   "wheel_d": (140.0, EST + ": the factory blower wheel, in the case's scroll"),
                   "wheel_h": (70.0, EST)},
        "make": r_can, "origin": "z=0 the flange face; the motor +z, the shaft and wheel -z"},
    "seat-module": {
        "what": "Seat heat / cool / power module (DV57, DV58; luxury LP52, not chosen)",
        "params": {"w": (120.0, EST + ": a seat heater and fan controller, worst case"),
                   "d": (80.0, EST), "h": (30.0, EST)},
        "make": r_box, "origin": "z=0 the base, centred"},
    "amplifier": {
        "what": "Amplifier / DSP (DV60, luxury LP57, not chosen - the largest class)",
        "params": {"w": (300.0, EST + ": a 6-8 channel DSP amplifier"), "d": (200.0, EST),
                   "h": (55.0, EST), "heatsink": (8, EST + ": fins for the look")},
        "make": r_box, "origin": "z=0 the base, centred"},
    "subwoofer-box": {
        "what": "Subwoofer enclosure in the driver-side cargo bin (DV61, luxury LP62, made)",
        "params": {"w": (400.0, EST + ": volume from V-107 / V-108, not measured"),
                   "d": (330.0, EST), "h": (300.0, EST),
                   "cone_d": (254.0, EST + ": a 10 in driver"), "mat": ("dark", "")},
        "make": r_box, "origin": "z=0 the base, centred, the driver on top (+z)"},
    "head-unit-1din": {
        "what": "Head unit, aftermarket single DIN (DV28)",
        "params": {"w": (178.0, "ISO 7736 single DIN, 180 x 50 aperture"),
                   "d": (155.0, EST + ": the chassis depth"), "h": (50.0, "ISO 7736")},
        "make": r_box, "origin": "z=0 the chassis bottom, centred; the face at -y"},
    "usb-c-module": {
        "what": "USB-C charging module, aftermarket (DV29)",
        "params": {"d": (29.0, EST + ": the common 1 1/8 in round socket"), "h": (40.0, EST),
                   "mat": ("black", "")},
        "make": r_can, "origin": "z=0 the panel face, the body +z"},
    "coil-igniter-set": {
        "what": "Ignition coils and igniters (DV01: B-18 to B-21, factory, on their bracket)",
        "params": {"w": (160.0, EST + ": two coils and two igniters on the factory bracket"),
                   "d": (90.0, EST), "h": (80.0, EST)},
        "make": r_box, "origin": "z=0 the bracket's base, centred"},
    "starter": {
        "what": "Starting motor A-01 (DV02, factory)",
        "params": {"d": (80.0, EST), "h": (150.0, EST), "box_w": (45.0, EST + ": the solenoid"),
                   "box_d": (45.0, EST), "box_h": (90.0, EST), "box_x": (65.0, EST)},
        "make": r_can, "origin": "z=0 the mounting flange, the motor +z"},
    "alternator": {
        "what": "Alternator (DV04, factory)",
        "params": {"d": (125.0, EST), "h": (110.0, EST), "shaft_d": (17.0, EST),
                   "shaft_len": (20.0, EST), "flange_d": (60.0, EST + ": the pulley"),
                   "flange_t": (20.0, EST)},
        "make": r_can, "origin": "z=0 the pulley face, the body +z"},
    "switch-small": {
        "what": "A small switch or sender body (the inhibitor, park-brake, kick-down, glove-box "
                "and luggage switches; factory)",
        "params": {"w": (40.0, EST), "d": (25.0, EST), "h": (20.0, EST)},
        "make": r_box, "origin": "z=0 the mounting face, centred"},
    "sender-threaded": {
        "what": "A threaded sender or switch (water temp C-02, oil pressure C-09, brake "
                "switch F-11, door jamb switches, the speed pulse generator; factory or new)",
        "params": {"d": (22.0, EST), "h": (30.0, EST), "hex": (19.0, EST), "hex_h": (8.0, EST)},
        "make": r_can, "origin": "z=0 the hex's top (the seat), the body +z, the thread -z"},
    "solenoid": {
        "what": "A solenoid (hatch and fuel-door releases, the kick-down solenoid; factory)",
        "params": {"d": (28.0, EST), "h": (55.0, EST), "shaft_d": (6.0, EST),
                   "shaft_len": (15.0, EST)},
        "make": r_can, "origin": "z=0 the mounting face, the body +z, the plunger -z"},
    "motor-gear": {
        "what": "A geared motor (the pop-up motors E-03 / E-04, the wiper motor D-02; factory)",
        "params": {"d": (60.0, EST), "h": (100.0, EST), "box_w": (100.0, EST + ": the gearbox"),
                   "box_d": (75.0, EST), "box_h": (40.0, EST), "box_x": (15.0, EST),
                   "gear": (1, "")},
        "make": r_can, "origin": "z=0 the gearbox's face, the motor +z, the gearbox -z"},
    "washer-pump": {
        "what": "Washer pump D-01 (DV16, factory)",
        "params": {"d": (35.0, EST), "h": (70.0, EST), "mat": ("black", "")},
        "make": r_can, "origin": "z=0 the pump's base, the motor +z"},
    "fuel-pump": {
        "what": "Fuel pump, Carter P4070 (DV34)",
        "params": {"d": (70.0, EST + ": the Carter drawing not read"), "h": (130.0, EST),
                   "shaft_d": (10.0, EST + ": the outlet"), "shaft_len": (20.0, EST)},
        "make": r_can, "origin": "z=0 the inlet end, the pump along +z"},
    "fuel-sender": {
        "what": "Fuel level sender C-01 (DV36, factory)",
        "params": {"d": (75.0, EST + ": the sender's flange"), "h": (12.0, EST),
                   "box_w": (20.0, EST + ": the float arm's housing"), "box_d": (20.0, EST),
                   "box_h": (180.0, EST)},
        "make": r_can, "origin": "z=0 the flange face, the arm -z into the tank"},
    "horn": {
        "what": "Horn (DV14, F-09 / F-10, factory)",
        "params": {"d": (90.0, EST), "h": (35.0, EST), "box_w": (20.0, EST + ": the bracket"),
                   "box_d": (8.0, EST), "box_h": (30.0, EST)},
        "make": r_can, "origin": "z=0 the bracket's foot, the horn +z"},
    "headlight-7in": {
        "what": "Headlight, 7 in round sealed beam class (DV10, E-08 / E-09)",
        "params": {"d": (178.0, "7 in round"), "depth": (100.0, EST)},
        "make": r_round_lamp, "origin": "z=0 the bucket's back, the lens +z"},
    "lamp-front-combo": {
        "what": "Front combination lamp (DV12, F-05 / F-06, factory)",
        "params": {"w": (200.0, EST), "d": (60.0, EST), "h": (70.0, EST),
                   "lens": ("amber", "")},
        "make": r_lamp, "origin": "z=0 the housing's base, centred, the lens at +y"},
    "lamp-rear-combo": {
        "what": "Rear combination lamp (DV37, F-07 / F-08, factory)",
        "params": {"w": (470.0, EST + ": from the FB tail-light scan's 479 x 217 box (cad "
                                       "fb-rx7-taillight-housing-scan-printables-giooig13)"),
                   "d": (100.0, EST), "h": (150.0, EST), "lens": ("red", "")},
        "make": r_lamp, "origin": "z=0 the housing's base, centred, the lens at +y"},
    "lamp-small": {
        "what": "A small lamp (side markers, licence lamps, glove-box, luggage and the "
                "interior lamp; factory)",
        "params": {"w": (100.0, EST), "d": (35.0, EST), "h": (30.0, EST),
                   "lens": ("amber", "")},
        "make": r_lamp, "origin": "z=0 the housing's base, centred, the lens at +y"},
    "ignition-switch": {
        "what": "Ignition switch, electrical portion (DV18, new, 1981-83 FB)",
        "params": {"d": (32.0, EST), "h": (40.0, EST), "mat": ("black", "")},
        "make": r_can, "origin": "z=0 the face on the lock, the body +z"},
    "combination-switch": {
        "what": "Column combination switch (DV19-DV22: light, turn, hazard, wiper; factory)",
        "params": {"w": (160.0, EST + ": both stalks' housing round the column"),
                   "d": (90.0, EST), "h": (60.0, EST)},
        "make": r_box, "origin": "z=0 the base, centred on the column"},
    "speaker-165": {
        "what": "Speaker, 6.5 in class (luxury LP58 fronts, LP59 surrounds - not chosen)",
        "params": {"d": (165.0, "6.5 in"), "depth": (60.0, EST + ": V-103 to V-106 will say"),
                   "magnet_d": (100.0, EST), "cone_depth": (45.0, EST)},
        "make": r_speaker, "origin": "z=0 the flange's back (the baffle), the cone +z"},
    "speaker-100": {
        "what": "Speaker, 4 in class (luxury LP60 centre - not chosen)",
        "params": {"d": (100.0, "4 in"), "depth": (45.0, EST + ": V-109 / V-110 will say"),
                   "magnet_d": (65.0, EST), "cone_depth": (30.0, EST)},
        "make": r_speaker, "origin": "z=0 the baffle, the cone +z"},
    "radar-receiver": {
        "what": "Radar receiver, concealed (luxury LP44, Escort MAX Ci 360c class, D-502)",
        "params": {"w": (110.0, EST + ": a concealed radar receiver"), "d": (80.0, EST),
                   "h": (40.0, EST)},
        "make": r_box, "origin": "z=0 the base, centred; the horn faces +y"},
}


# ================================================================ what goes where: entries ==
# key: the device (DVxx), the part (Pxxx), or another area's part qualified like a gate
# ("04-luxury:LP58"). node: the scene's part id it sits at (scene.json). count: how many at that
# node (`also` adds other nodes); a function of the record where the record says (relays,
# fuses, parts.qty), else the record's own words.
def _count_relays(rec, where):
    return sum(1 for r in rec["relays"] if (r.get("location") or "").startswith(where))


def _count_fuses(rec, where, holder):
    return sum(1 for f in rec["fuses"] if (f.get("location") or "").startswith(where)
               and holder in (f.get("location") or ""))


def _qty(rec, pid):
    for p in rec["parts"]:
        if p["id"] == pid:
            return int(float(p.get("qty") or 1))
    raise Fail("01-electrical parts has no %s" % pid)


ENTRIES = {
    # the common parts
    "P003": {"model": "relay-micro-iso", "kind": "module", "node": "pmu",
             "count": lambda r: _count_relays(r, "Dash node"),
             "node_note": "the dash node (the PMU stands for it in the scene)",
             "also": [("sill-node", lambda r: _count_relays(r, "Sill node"), "K5-K8")]},
    "P006": {"model": "socket-micro-iso-panel", "kind": "module", "node": "pmu",
             "count": lambda r: _count_relays(r, "Dash node"),
             "node_note": "the dash node", "also": [("sill-node",
                                                     lambda r: _count_relays(r, "Sill node"),
                                                     "under K5-K8")]},
    "P004": {"model": "relay-mini-iso-sealed", "kind": "module", "node": "leg-l1",
             "count": lambda r: _count_relays(r, "Inner fender"),
             "node_note": "K9, on the inner fender (L1)"},
    "P005": {"model": "socket-mini-weatherproof", "kind": "module", "node": "leg-l1",
             "count": lambda r: _qty(r, "P005"), "node_note": "K9's socket"},
    "P001": {"model": "atc-block-4", "kind": "module", "node": "pmu",
             "count": lambda r: _qty(r, "P001"), "node_note": "blocks A and B at the dash node"},
    "P002": {"model": "inline-atc-sealed", "kind": "module", "node": "pmu",
             "count": lambda r: _count_fuses(r, "Dash node", "inline"),
             "node_note": "the dash node's sealed inline holders",
             "also": [("sill-node", lambda r: _count_fuses(r, "Sill node", "inline"),
                       "the sill's inline holders"),
                      ("leg-l3", lambda r: _count_fuses(r, "Behind the lower dash", "inline"),
                       "F24 in the L3 leg")]},
    "P189": {"model": "inline-maxi-sealed", "kind": "module", "node": "pmu",
             "count": lambda r: _count_fuses(r, "Dash node", "MAXI"),
             "node_note": "at the busbar stud and K11"},
    "P053": {"model": "midi-block", "kind": "module", "node": "leg-l1",
             "count": lambda r: _qty(r, "P053"), "node_note": "beside the starter B+ stud"},
    "P051": {"model": "mrbf-holder", "kind": "module", "node": "leg-l4",
             "count": lambda r: _qty(r, "P051"),
             "node_note": "the passenger-side cargo bin, on the disconnect's output stud (the "
                          "scene has no node there yet; leg-l4 stands for it)"},
    "P047": {"model": "class-t-block", "kind": "module", "node": "leg-l4",
             "count": lambda r: _qty(r, "P047"),
             "node_note": "the cargo bin, beside the master disconnect"},
    "P049": {"model": "disconnect", "kind": "module", "node": "leg-l4",
             "count": lambda r: _qty(r, "P049"), "node_note": "the cargo bin, on the battery +"},
    "P007": {"model": "busbar-10", "kind": "module", "node": "pmu",
             "count": lambda r: _qty(r, "P007"), "node_note": "the dash node's always-hot bar"},
    "00-CAR:P-002": {"model": "battery-ionic-s9", "kind": "module", "node": "leg-l4",
                     "count": 1, "node_note": "the passenger-side cargo bin (D-002, D-449)"},
    "P142": {"model": "teensy41", "kind": "module", "node": "icu-carrier", "count": 1,
             "node_note": "one on each carrier, socketed: icu-carrier and dcu-carrier (D-259)",
             "also": [("dcu-carrier", 1, "the DCU's")]},
    "P116": {"model": "xiao-esp32c3", "kind": "module", "node": "icu-carrier", "count": 1,
             "node_note": "the ICU's radio co-processor on its header (D-267)"},
    "P117": {"model": "bt817-me817ev", "kind": "module", "node": "display-unit", "count": 1,
             "node_note": "inside the display unit, where its placeholder block is"},
    "04-luxury:LP58": {"model": "speaker-165", "kind": "device", "node": "kick-driver",
                       "count": 1, "node_note": "the fronts (L3-SPF-L / -R)",
                       "also": [("kick-passenger", 1, "the right front")]},
    "04-luxury:LP59": {"model": "speaker-165", "kind": "device", "node": "quarter-driver",
                       "count": 1, "node_note": "the surrounds (L4-SPR-L / -R)",
                       "also": [("quarter-passenger", 1, "the right surround")]},
    "04-luxury:LP60": {"model": "speaker-100", "kind": "device", "node": "console", "count": 1,
                       "node_note": "the centre, between the seats (L3-CTR)"},
    "04-luxury:LP44": {"model": "radar-receiver", "kind": "device", "node": "nose-bumper",
                       "count": 1, "node_note": "front on L2-RDR",
                       "also": [("rear-node", 1, "rear on L4-RDR")]},
    # the devices
    "DV01": {"model": "coil-igniter-set", "node": "leg-l1"},
    "DV02": {"model": "starter", "node": "leg-l1"},
    "DV03": {"model": "relay-mini-iso-sealed", "node": "leg-l1",
             "node_note": "K9 in P005's socket"},
    "DV04": {"model": "alternator", "node": "leg-l1"},
    "DV05": {"model": "switch-small", "node": "leg-l1"},
    "DV06": {"model": "sender-threaded", "node": "leg-l1"},
    "DV07": {"model": "sender-threaded", "node": "leg-l1"},
    "DV08": {"model": "sender-threaded", "node": "leg-l1"},
    "DV10": {"model": "headlight-7in", "node": "leg-l2", "count": 2},
    "DV11": {"model": "motor-gear", "node": "leg-l2", "count": 2},
    "DV12": {"model": "lamp-front-combo", "node": "leg-l2", "count": 2},
    "DV13": {"model": "lamp-small", "node": "leg-l2", "count": 2},
    "DV14": {"model": "horn", "node": "leg-l2", "count": 2},
    "DV15": {"model": "motor-gear", "node": "leg-l2"},
    "DV16": {"model": "washer-pump", "node": "leg-l2"},
    "DV18": {"model": "ignition-switch", "node": "leg-l3"},
    "DV19": {"model": "combination-switch", "node": "leg-l3",
             "node_note": "DV19-DV22 are one column assembly; one model stands for all four"},
    "DV20": {"model": "combination-switch", "node": "leg-l3", "count": 0,
             "node_note": "drawn by DV19's"},
    "DV21": {"model": "combination-switch", "node": "leg-l3", "count": 0,
             "node_note": "drawn by DV19's"},
    "DV22": {"model": "combination-switch", "node": "leg-l3", "count": 0,
             "node_note": "drawn by DV19's"},
    "DV25": {"model": "sender-threaded", "node": "leg-l3"},
    "DV26": {"model": "switch-small", "node": "leg-l3"},
    "DV27": {"model": "blower-motor", "node": "hvac-case"},
    "DV28": {"model": "head-unit-1din", "node": "leg-l3"},
    "DV29": {"model": "usb-c-module", "node": "leg-l3"},
    "DV31": {"model": "lamp-small", "node": "glovebox"},
    "DV34": {"model": "fuel-pump", "node": "leg-l4"},
    "DV36": {"model": "fuel-sender", "node": "leg-l4"},
    "DV37": {"model": "lamp-rear-combo", "node": "leg-l4", "count": 2},
    "DV38": {"model": "lamp-small", "node": "leg-l4", "count": 4},
    "DV39": {"model": "lamp-small", "node": "leg-l4"},
    "DV40": {"model": "lamp-small", "node": "leg-l4"},
    "DV41": {"model": "sender-threaded", "node": "leg-l4", "count": 2},
    "DV44": {"model": "aem-gauge-52", "node": "leg-l3",
             "node_note": "hidden behind the dash (modules WBO)"},
    "DV46": {"model": "display-12p3", "node": "display-unit",
             "node_note": "in the display unit, where its placeholder block is (D-268)"},
    "DV47": {"model": "sender-threaded", "node": "leg-l4"},
    "DV48": {"model": "solenoid", "node": "hatch"},
    "DV49": {"model": "solenoid", "node": "leg-l4"},
    "DV50": {"model": "switch-small", "node": "leg-l3"},
    "DV51": {"model": "solenoid", "node": "leg-l4",
             "node_note": "on the transmission; its lead is in L4"},
    "DV55": {"model": "pololu-g2-24v21", "node": "hvac-case",
             "node_note": "in the old resistor pack's hole (D-308)"},
    "DV56": {"model": "comfort-block-st6", "node": "centre-stack"},
    "DV57": {"model": "seat-module", "node": "seat-driver"},
    "DV58": {"model": "seat-module", "node": "seat-passenger"},
    "DV59": {"model": "servo-fs5115m", "node": "hvac-case", "count": 3,
             "node_note": "mode, blend, recirculate, each on its door cable (D-073)"},
    "DV60": {"model": "amplifier", "node": "leg-l4",
             "node_note": "the passenger-side cargo bin beside the battery (D-449); leg-l4 "
                          "stands for it"},
    "DV61": {"model": "subwoofer-box", "node": "cargo-bin"},
}

# Devices with no model of their own, and why. Every devices row is in ENTRIES or here.
NO_MODEL = {
    "DV09": "a ground strap: a cable, the harness's (routes), not a device",
    "DV17": "the front star node: a stud on the radiator support - the scene's node",
    "DV42": "the rear star node: a stud in the cargo bin - the scene's rear-node",
    "DV43": "the sill node: the scene's sill-node; its panel is the harness's, drawn with the "
            "connectors (Y24)",
    "DV23": "the horn pad is the steering wheel's (factory, kept)",
    "DV24": "on the left plate's own board (left-plate.glb, the CUR, D-514)",
    "DV30": "bulbs inside the factory heater, select-lever and switch panels",
    "DV33": "the defog grid is printed on the hatch glass",
    "DV45": "the ICU is the display unit and its carrier (display-unit.glb, icu-carrier.glb); "
            "its Teensy is P142's entry",
    "DV53": "the control panel is panel.glb, inside the control unit",
    "DV54": "the DCU is the control unit and its carrier (control-unit.glb, dcu-carrier.glb); "
            "its Teensy is P142's entry",
    "DV62": "the left plate is left-plate.glb, being made the CUR (D-514)",
}


# ============================================================================== the record ==
def read_record():
    """devices, relays, fuses, parts (01-electrical) and cad (00-CAR), via rx7.py
    export."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "record.json")
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "rx7.py"), "export",
                            "--out", path], cwd=ROOT, capture_output=True, text=True)
        if r.returncode not in (0, 2) or not os.path.exists(path):
            raise Crash("rx7.py export failed (rc %s): %s" % (r.returncode, r.stderr[-300:]))
        data = json.load(open(path))
    want = {("01-electrical", "devices"): "devices", ("01-electrical", "relays"): "relays",
            ("01-electrical", "fuses"): "fuses", ("01-electrical", "parts"): "parts",
            ("00-CAR", "cad"): "cad"}
    out = {}
    for t in data["tables"]:
        k = want.get((t["area"], t["table"]))
        if k:
            out[k] = [dict(zip(t["columns"], row)) for row in t["rows"]]
    for k in want.values():
        if k not in out:
            raise Fail("the record has no %s table" % k)
    return out


# ============================================================================= the building ==
def _params(name):
    return {k: v[0] for k, v in STANDINS[name]["params"].items()}


def prims_of(name):
    s = STANDINS[name]
    return s["make"](_params(name))


def source_of(name):
    if name in FOUND:
        return os.path.join(LIB, FOUND[name]["file"])
    return None


def stamp(name):
    h = hashlib.sha256()
    for p in (os.path.join(HERE, "build_devices.py"), os.path.join(HERE, "devices_fc.py")):
        h.update(open(p, "rb").read())
    h.update(name.encode())
    if name in FOUND:
        h.update(json.dumps(FOUND[name], sort_keys=True).encode())
        src = source_of(name)
        h.update(str(os.path.getsize(src) if os.path.exists(src) else -1).encode())
    else:
        h.update(json.dumps(prims_of(name)).encode())
    return h.hexdigest()[:16]


def run_fc(models, glb_dir):
    if not os.path.exists(FREECADCMD):
        raise Crash("freecadcmd is not at %s (set FREECADCMD)" % FREECADCMD)
    jobs = []
    for name in models:
        glb = os.path.join(glb_dir, name + ".glb")
        if name in FOUND:
            f = FOUND[name]
            src = source_of(name)
            if not os.path.exists(src):
                raise Crash("%s: the found model is not on this machine: %s (cad row %s; fetch "
                            "it to that path)" % (name, os.path.relpath(src, ROOT), f["cad"]))
            jobs.append({"name": name, "kind": "step", "path": src, "member": f.get("member"),
                         "rot": f["rot"], "linear": f["linear"], "angular": f["angular"],
                         "mat": f["mat"], "glb": glb})
        else:
            jobs.append({"name": name, "kind": "prims", "prims": prims_of(name), "glb": glb})
    with tempfile.TemporaryDirectory() as tmp:
        job = {"tools_dir": TOOLS, "mats": MATS, "jobs": jobs,
               "meta": os.path.join(tmp, "meta.json"), "tmp": tmp}
        jpath = os.path.join(tmp, "job.json")
        with open(jpath, "w") as fh:
            json.dump(job, fh)
        r = subprocess.run([FREECADCMD, os.path.join(HERE, "devices_fc.py")],
                           env=dict(os.environ, RX7_DEVICES_JOB=jpath),
                           capture_output=True, text=True, cwd=tmp)
        meta = json.load(open(job["meta"])) if os.path.exists(job["meta"]) else None
        if r.returncode != 0 or meta is None:
            raise Crash("freecadcmd failed (rc %s): %s" % (r.returncode,
                                                           (r.stderr or r.stdout)[-800:]))
        return meta


def _size(bbox):
    lo, hi = bbox
    return {"x": round(hi[0] - lo[0], 2), "y": round(hi[1] - lo[1], 2),
            "z": round(hi[2] - lo[2], 2)}


def _count(v, rec):
    return v(rec) if callable(v) else v


def manifest_of(rec, models, built):
    devs = {d["id"]: d for d in rec["devices"]}
    out = {}
    for key, e in ENTRIES.items():
        name = e["model"]
        m = models[name]
        found = name in FOUND
        info = FOUND[name] if found else STANDINS[name]
        if key in devs:
            d = devs[key]
            label = "%s - %s" % (d["device"], d["ident"]) if d.get("ident") else d["device"]
        else:
            label = info["what"]
        ent = {"glb": "%s/%s.glb" % (SUB, name), "name": label,
               "kind": e.get("kind", "device"), "node": e["node"],
               "count": _count(e.get("count", 1), rec),
               "size_mm": _size(m["bbox"]), "bytes": m["bytes"],
               "origin": info["origin"], "standin": not found,
               "cad": info["cad"] if found else None, "confirm": True,
               "model": name, "source": (
                   "%s, %s (%s), converted by FreeCAD" % (info["what"], info["cad"],
                                                         info["licence"]) if found else
                   "drawn here (build_devices.py STANDINS[%r]): %s" % (name, info["what"]))}
        if e.get("node_note"):
            ent["node_note"] = e["node_note"]
        if e.get("also"):
            ent["also"] = [{"node": n, "count": _count(c, rec), "what": w}
                           for (n, c, w) in e["also"]]
        if not found:
            ent["params"] = {k: {"mm": v[0], "source": v[1]}
                             for k, v in info["params"].items() if v[1]}
        out[key] = ent
    out["_meta"] = {
        "version": 1, "built": built, "work": "Y28", "ruling": "D-515",
        "frame": "every glb in mm, z up, in the part's own frame (00-design README §13); "
                 "each entry's origin says where its zero is",
        "keys": "an entry per device (01-electrical devices DVxx) or part (01-electrical "
                "parts Pxxx; another area's qualified, 04-luxury:LP58); keys starting _ are "
                "not entries",
        "node": "the scene.json part the entry sits at; `also` lists further places",
        "none": {k: NO_MODEL[k] for k in sorted(NO_MODEL)},
        "models": {n: {"bytes": models[n]["bytes"], "bbox": models[n]["bbox"],
                       "triangles": models[n].get("triangles"),
                       "standin": n not in FOUND, "stamp": models[n]["stamp"]}
                   for n in sorted(models)},
    }
    return out


def all_models():
    seen = []
    for e in ENTRIES.values():
        if e["model"] not in seen:
            seen.append(e["model"])
    return seen


def build_all(out_dir=OUT_DEFAULT, only=None):
    """Build every model (or `only`), write devices/manifest.json, return the manifest."""
    glb_dir = os.path.join(out_dir, SUB)
    os.makedirs(glb_dir, exist_ok=True)
    mpath = os.path.join(glb_dir, "manifest.json")
    old = {}
    if os.path.exists(mpath):
        old = json.load(open(mpath)).get("_meta", {}).get("models", {})
    names = all_models()
    todo = names if only is None else [only]
    meta = run_fc(todo, glb_dir)
    models = {n: dict(old[n]) for n in names if n in old}
    for n in todo:
        m = meta[n]
        m["stamp"] = stamp(n)
        models[n] = m
        print("%-26s %8.3f MB  %s x %s x %s mm%s" % (
            n, m["bytes"] / 1e6, *[_size(m["bbox"])[k] for k in "xyz"],
            "" if n in FOUND else "  (stand-in)"), flush=True)
    missing = [n for n in names if n not in models]
    if missing:
        raise Fail("not built yet: %s (run without --only)" % ", ".join(missing))
    rec = read_record()
    built = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    man = manifest_of(rec, models, built)
    with open(mpath + ".part", "w") as fh:
        json.dump(man, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    os.replace(mpath + ".part", mpath)
    total = sum(m["bytes"] for m in models.values())
    print("%-26s %8.3f MB  %d models (%d found, %d stand-ins), %d entries" % (
        "total", total / 1e6, len(models), sum(1 for n in models if n in FOUND),
        sum(1 for n in models if n not in FOUND), len(man) - 1))
    return man


# ============================================================================ the contract ==
def validate(man, out_dir, rec, scene_nodes):
    probs = []
    devs = {d["id"] for d in rec["devices"]}
    cads = {c["id"] for c in rec["cad"]}
    meta = man.get("_meta", {})
    for key, e in man.items():
        if key.startswith("_"):
            continue
        for f in ("glb", "name", "kind", "node", "size_mm", "origin", "standin", "cad",
                  "confirm", "source"):
            if f not in e:
                probs.append("%s: no %s" % (key, f))
        if e.get("kind") not in ("device", "module"):
            probs.append("%s: kind %r" % (key, e.get("kind")))
        if e.get("confirm") is not True:
            probs.append("%s: confirm must be true - nothing here is measured (R11)" % key)
        g = os.path.join(out_dir, e.get("glb", ""))
        if not os.path.exists(g):
            probs.append("%s: %s is not built" % (key, e.get("glb")))
        elif os.path.getsize(g) != e.get("bytes"):
            probs.append("%s: %s is %d bytes, the manifest says %s"
                         % (key, e.get("glb"), os.path.getsize(g), e.get("bytes")))
        nodes = [e.get("node")] + [a.get("node") for a in e.get("also", [])]
        for n in nodes:
            if scene_nodes is not None and n not in scene_nodes:
                probs.append("%s: node %r is not a part in scene.json" % (key, n))
        if e.get("standin") is False and e.get("cad") not in cads:
            probs.append("%s: cad row %r is not in 00-CAR cad" % (key, e.get("cad")))
        if e.get("standin") is True and e.get("cad") is not None:
            probs.append("%s: a stand-in names a cad row" % key)
    for d in sorted(devs):
        if d not in man and d not in meta.get("none", {}):
            probs.append("%s: a device with no entry and no stated reason" % d)
    for d in meta.get("none", {}):
        if d not in devs:
            probs.append("%s: a reason for a device the record does not have" % d)
    return probs


def scene_nodes_of(out_dir):
    p = os.path.join(out_dir, "scene.json")
    if not os.path.exists(p):
        return None
    return {x["id"] for x in json.load(open(p))["parts"]}


def selftest(out_dir):
    mpath = os.path.join(out_dir, SUB, "manifest.json")
    if not os.path.exists(mpath):
        print("manifest.json is not there: build first")
        return 2
    man = json.load(open(mpath))
    rec = read_record()
    nodes = scene_nodes_of(out_dir)
    probs = validate(man, out_dir, rec, nodes)
    for p in probs:
        print("  manifest: " + p)
    if probs:
        return 1
    if nodes is None:
        print("  (scene.json not built here: nodes not checked)")
    cases = []
    t = json.loads(json.dumps(man))
    t[next(k for k in t if k.startswith("DV"))]["bytes"] += 1
    cases.append(("a glb of other bytes", t))
    t = json.loads(json.dumps(man))
    del t[next(k for k in t if k.startswith("DV"))]
    cases.append(("a device with no entry", t))
    t = json.loads(json.dumps(man))
    t["P003"]["node"] = "no-such-node"
    cases.append(("a node the scene lacks", t))
    t = json.loads(json.dumps(man))
    t["P003"]["confirm"] = False
    cases.append(("an entry not confirm", t))
    t = json.loads(json.dumps(man))
    t["DV46"]["cad"] = "no-such-cad-row"
    cases.append(("a found model with no cad row", t))
    rc = 0
    for what, t in cases:
        got = validate(t, out_dir, rec, nodes if nodes is not None else {"pmu", "leg-l1"})
        if what == "a node the scene lacks" and nodes is None:
            got = got or ["skipped"]
        print("  %-34s %s" % (what, "refused" if got else "NOT REFUSED"))
        rc |= 0 if got else 1
    nent = sum(1 for k in man if not k.startswith("_"))
    print("selftest: %s (%d entries, %d devices with a stated reason; %d broken copies, %d "
          "refused)" % ("pass" if rc == 0 else "FAIL", nent, len(man["_meta"]["none"]),
                        len(cases), len(cases) - rc))
    return rc


def check(out_dir):
    mpath = os.path.join(out_dir, SUB, "manifest.json")
    if not os.path.exists(mpath):
        print("devices/manifest.json is not there: build with build_devices.py")
        return 2
    models = json.load(open(mpath))["_meta"]["models"]
    rc, absent = 0, False
    for n in all_models():
        g = os.path.join(out_dir, SUB, n + ".glb")
        m = models.get(n)
        if not os.path.exists(g):
            print("%-26s not built here" % n)
            absent = True
        elif m is None or os.path.getsize(g) != m["bytes"]:
            print("%-26s does not match the manifest" % n)
            rc = 1
        elif m.get("stamp") != stamp(n):
            print("%-26s stale: its recipe or source changed since it was built" % n)
            rc = 1
        else:
            print("%-26s current" % n)
    return rc if rc else (2 if absent else 0)


class _Args(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print("build_devices: %s" % message, file=sys.stderr)
        sys.exit(3)


def main(argv):
    ap = _Args(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--only", choices=all_models())
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out)
    try:
        if a.selftest:
            return selftest(out)
        if a.check:
            return check(out)
        build_all(out, a.only)
        rec = read_record()
        probs = validate(json.load(open(os.path.join(out, SUB, "manifest.json"))), out, rec,
                         scene_nodes_of(out))
        for p in probs:
            print("manifest: " + p)
        return 1 if probs else 0
    except Fail as e:
        print("build_devices: %s" % e, file=sys.stderr)
        return 1
    except Crash as e:
        print("build_devices: %s" % e, file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

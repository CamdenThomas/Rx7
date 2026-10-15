"""parts.py - where every file of a part lives in 00-design (the layout of 2026-10-15). Every tool in
this folder finds a board, an assembly or a part's data through these functions and types no path
of its own, so the layout is written once, here.

    00-design/
      <part>/cad/<name>/      a KiCad project or a FreeCAD assembly, and its generated outputs
      <part>/data/            the part's design data: BOMs, the board extracts (board.json, probe.json),
                              the assembly parameter tables, the mock-up reports
      <part>/diagrams/        what is read by eye: schematic SVGs, renders, assembly views and
                              drawings, the face concept pages
      <part>/firmware/        the part's sketches
      data/                   what several parts share: the vendor pin tables, the bench order's carts
      diagrams/               what spans the parts: the overhaul plan
      tools/                  every script (this file)

The parts are the Display Unit (du), the Control Unit (cu), the Control Unit Remote (cur, a part of
the CU), the PMU box (pmu), the bin box (bin), the bay junction (bay), the amplifier dock (amp) and
the harness - one per row of the record's `boxes` table, plus the harness (D-612). Nothing here
reads the record: the record is ../data/*.csv, and these files only draw it (00-design/README.md,
the fence).
"""
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(TOOLS)
AREA = os.path.dirname(DESIGN)                      # 02-PROJECTS/01-electrical
RECORD = os.path.join(AREA, "data")
SHARED_DATA = os.path.join(DESIGN, "data")
SHARED_DIAGRAMS = os.path.join(DESIGN, "diagrams")

PARTS = {
    "du": "display-unit",
    "cu": "control-unit",
    "cur": os.path.join("control-unit", "control-unit-remote"),
    "pmu": "pmu",                   # the PMU box, not only the PMU (D-596)
    "bin": "bin-box",               # the battery bin's box (D-608)
    "bay": "bay-junction",          # the engine bay's jump post and power junction (D-609)
    "amp": "amp-dock",              # the amplifier and upmix dock (D-609)
    "harness": "harness",
}

# KiCad projects: the board's name is its folder's, its files' and its fab package's name
BOARDS = {
    "du-carrier": "du",          # the Display Unit's carrier (the Teensy, its inputs, the radio)
    "du-hdmi-bridge": "du",      # the BT817 board's RGB to the panel's HDMI (P119)
    "cu-carrier": "cu",          # the Control Unit's carrier (the Teensy, comfort and window stages)
    "cu-face-board": "cu",       # the board behind the CU's face: keys, knobs, screen, lights
    "cur-board": "cur",          # the CUR's board: winks, hazard, releases, mirror stick, screen knob
}
# FreeCAD mock-ups of a whole unit: its insides and its case
ASSEMBLIES = {"du-assembly": "du", "cu-assembly": "cu", "cur-assembly": "cur"}


def part_dir(part):
    return os.path.join(DESIGN, PARTS[part])


def data_dir(part):
    return os.path.join(part_dir(part), "data")


def diagrams_dir(part):
    return os.path.join(part_dir(part), "diagrams")


def firmware_dir(part):
    return os.path.join(part_dir(part), "firmware")


def part_of(name):
    """The part a board or an assembly belongs to."""
    if name in BOARDS:
        return BOARDS[name]
    if name in ASSEMBLIES:
        return ASSEMBLIES[name]
    raise KeyError("%s is neither a board nor an assembly in parts.py" % name)


def cad_dir(name):
    """A board's or an assembly's own folder under its part's cad/."""
    return os.path.join(part_dir(part_of(name)), "cad", name)


def board_file(board, ext):
    """cad/<board>/<board>.<ext>: kicad_pcb, kicad_sch, kicad_pro, step ..."""
    return os.path.join(cad_dir(board), "%s.%s" % (board, ext))


def fab_dir(board):
    """What goes to the board house: the gerbers, the drill files and their zip."""
    return os.path.join(cad_dir(board), "fab")


def data_file(name, suffix):
    """<part>/data/<name><suffix>: -bom.csv, -revA-bom.csv, -board.json, -probe.json, -report.json"""
    return os.path.join(data_dir(part_of(name)), name + suffix)


def diagram_file(name, suffix):
    """<part>/diagrams/<name><suffix>: .svg, -top.png, -revA-assembly-top.svg, -view-front.svg"""
    return os.path.join(diagrams_dir(part_of(name)), name + suffix)


def board_from_path(path):
    """The board a .kicad_pcb or .kicad_sch path belongs to (for tools given a file)."""
    stem = os.path.splitext(os.path.basename(path))[0]
    if stem not in BOARDS:
        raise KeyError("%s is not a board of parts.py: %s" % (stem, ", ".join(sorted(BOARDS))))
    return stem

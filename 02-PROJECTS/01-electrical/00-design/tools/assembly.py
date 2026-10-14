"""assembly.py BOARD.kicad_pcb [BOARD.kicad_pcb ...]  - the hand-assembly drawings of a board, into
the fab/ folder beside it (Y44, D-548's list: no reference designators print on the Control Unit
carrier or the panel, and the Display Unit's sit on the fabrication layer only):

    fab/<board>-revA-assembly-top.svg       the front, as you look at it
    fab/<board>-revA-assembly-bottom.svg    the back, mirrored so it reads as you look at it

Each drawing is the board's outline, every part's fabrication outline with its pads sketched, and
its reference designator in the middle of the part, sized to fit it. The values are in the BOM
beside it (fab/<board>-revA-bom.csv), row by reference.

The board file is never written: the references are moved onto the fabrication layers in a copy
held in a temporary folder, and that copy is plotted. Run it with KiCad's own Python (it needs
`pcbnew`): on the Mac
    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 assembly.py ...
on Fedora the system python3. `kicad-cli` is found on PATH, or named in KICAD_CLI.
Reads: the .kicad_pcb named. Owns: the two SVGs. No table of the record.
"""
import os
import shutil
import subprocess
import sys
import tempfile

import pcbnew

mm = pcbnew.ToMM
MM = pcbnew.FromMM
CLI = os.environ.get("KICAD_CLI") or shutil.which("kicad-cli") or "/opt/homebrew/bin/kicad-cli"
GLYPH = 0.9          # a stroke-font character's advance, in text heights


def box(fp):
    """The part's courtyard box, or its pads' box where it has no courtyard: x0, y0, x1, y1 in mm."""
    cy = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd)
    if cy.OutlineCount():
        b = cy.BBox()
        return mm(b.GetLeft()), mm(b.GetTop()), mm(b.GetRight()), mm(b.GetBottom())
    xs, ys = [], []
    for p in fp.Pads():
        c, s = p.GetPosition(), p.GetSize(pcbnew.F_Cu)
        r = max(mm(s.x), mm(s.y)) / 2
        xs += [mm(c.x) - r, mm(c.x) + r]
        ys += [mm(c.y) - r, mm(c.y) + r]
    if not xs:
        c = fp.GetPosition()
        return mm(c.x) - 1, mm(c.y) - 1, mm(c.x) + 1, mm(c.y) + 1
    return min(xs), min(ys), max(xs), max(ys)


def prepare(board):
    """Put every reference on its side's fabrication layer, in the middle of its part; hide the
    values and the footprints' own fabrication-layer texts so nothing prints twice."""
    count = {"top": 0, "bottom": 0}
    for fp in board.GetFootprints():
        back = fp.IsFlipped()
        fab = pcbnew.B_Fab if back else pcbnew.F_Fab
        x0, y0, x1, y1 = box(fp)
        w, h = x1 - x0, y1 - y0
        ref = fp.Reference()
        text = fp.GetReference()
        upright = h > w * 1.3
        along, across = (h, w) if upright else (w, h)
        size = min(across * 0.55, along * 0.9 / (max(len(text), 1) * GLYPH), 2.0)
        size = max(size, 0.4)
        ref.SetLayer(fab)
        ref.SetVisible(True)
        ref.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
        ref.SetTextThickness(MM(max(size * 0.14, 0.06)))
        ref.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        ref.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        ref.SetTextAngle(pcbnew.EDA_ANGLE(90 if upright else 0, pcbnew.DEGREES_T))
        ref.SetKeepUpright(True)
        ref.SetMirrored(back)
        ref.SetPosition(pcbnew.VECTOR2I(MM((x0 + x1) / 2), MM((y0 + y1) / 2)))
        fp.Value().SetVisible(False)
        for item in fp.GraphicalItems():       # hidden, not removed: pcbnew's Remove() frees the item
            if item.GetClass() == "PCB_TEXT" and item.GetLayer() in (pcbnew.F_Fab, pcbnew.B_Fab):
                item.SetVisible(False)
        count["bottom" if back else "top"] += 1
    return count


def plot(copy, out, layers, mirror):
    cmd = [CLI, "pcb", "export", "svg", "--layers", layers, "--mode-single", "--page-size-mode", "2",
           "--exclude-drawing-sheet", "--black-and-white", "--sketch-pads-on-fab-layers",
           "--drill-shape-opt", "0", "-o", out, copy]
    if mirror:
        cmd.insert(4, "--mirror")
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode == 0 and os.path.getsize(out) > 0, (cmd, r.stderr[-400:])


def main():
    for pcb in sys.argv[1:]:
        pcb = os.path.abspath(pcb)
        name = os.path.basename(pcb)[: -len(".kicad_pcb")]
        fab = os.path.join(os.path.dirname(pcb), "fab")
        assert os.path.isdir(fab), fab
        board = pcbnew.LoadBoard(pcb)
        count = prepare(board)
        with tempfile.TemporaryDirectory() as tmp:
            copy = os.path.join(tmp, name + ".kicad_pcb")
            pcbnew.SaveBoard(copy, board)
            plot(copy, os.path.join(fab, name + "-revA-assembly-top.svg"), "F.Fab,Edge.Cuts", False)
            plot(copy, os.path.join(fab, name + "-revA-assembly-bottom.svg"), "B.Fab,Edge.Cuts", True)
        print("%s: %d parts on the front, %d on the back -> fab/%s-revA-assembly-{top,bottom}.svg"
              % (name, count["top"], count["bottom"], name))


main()

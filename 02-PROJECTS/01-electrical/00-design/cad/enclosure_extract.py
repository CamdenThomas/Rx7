"""Read a board's geometry from its .kicad_pcb into <board>/enclosure/board.json (Y7).

Run with KiCad's own Python (it needs `pcbnew`), from anywhere:

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 \
        enclosure_extract.py icu-carrier        # or dcu-carrier, panel

Writes the outline (bounding box, corner radius), the board thickness, every hole of 3 mm or more
(the M3 mounting holes), and every footprint: reference, value, footprint name, position, rotation,
side and courtyard box. Coordinates are the STEP export's: x as KiCad, y = -y(KiCad), mm, so the
enclosure script and the board STEP share one frame. Owns no fact in the record: the board is the
drawing of `dcu_channels` / `icu_channels` / `panel_ribbon`, this is a copy of its geometry.
"""
import json, os, sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))


def mm(v):
    return round(pcbnew.ToMM(v), 4)


def main(board_name):
    path = os.path.join(HERE, board_name, board_name + ".kicad_pcb")
    b = pcbnew.LoadBoard(path)
    xs, ys, radii = [], [], []
    for d in b.GetDrawings():
        if d.GetLayer() != pcbnew.Edge_Cuts:
            continue
        bb = d.GetBoundingBox()
        xs += [mm(bb.GetLeft()), mm(bb.GetRight())]
        ys += [mm(bb.GetTop()), mm(bb.GetBottom())]
        if d.GetShape() == pcbnew.SHAPE_T_ARC:
            radii.append(mm(d.GetRadius()))
    out = {
        "board": board_name,
        "source": board_name + ".kicad_pcb",
        "frame": "STEP export frame: x = KiCad x, y = -KiCad y, z up, board bottom face z = 0",
        "outline": {"xmin": min(xs), "xmax": max(xs), "ymin": -max(ys), "ymax": -min(ys),
                    "corner_r": max(radii) if radii else 0.0},
        "thickness": mm(b.GetDesignSettings().GetBoardThickness()),
        "holes": [],
        "footprints": [],
    }
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        pos = fp.GetPosition()
        side = "bottom" if fp.IsFlipped() else "top"
        cy = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd)
        if cy.OutlineCount():
            bb = cy.BBox()
            box = [mm(bb.GetLeft()), mm(bb.GetRight()), -mm(bb.GetBottom()), -mm(bb.GetTop())]
        else:
            bb = fp.GetBoundingBox(False)
            box = [mm(bb.GetLeft()), mm(bb.GetRight()), -mm(bb.GetBottom()), -mm(bb.GetTop())]
        out["footprints"].append({
            "ref": ref, "value": fp.GetValue(), "footprint": str(fp.GetFPID().GetLibItemName()),
            "x": mm(pos.x), "y": -mm(pos.y), "rot": round(fp.GetOrientationDegrees(), 3),
            "side": side, "dnp": bool(fp.IsDNP()), "courtyard": box})
        for p in fp.Pads():
            d = mm(p.GetDrillSize().x)
            if d >= 3.0:
                pp = p.GetPosition()
                out["holes"].append({"ref": ref, "x": mm(pp.x), "y": -mm(pp.y), "d": d,
                                     "plated": p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH})
    out["footprints"].sort(key=lambda f: f["ref"])
    out["holes"].sort(key=lambda h: (h["x"], h["y"]))
    dst = os.path.join(HERE, board_name, "enclosure", "board.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print("wrote", dst, len(out["footprints"]), "footprints", len(out["holes"]), "holes")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(3)
    main(sys.argv[1])

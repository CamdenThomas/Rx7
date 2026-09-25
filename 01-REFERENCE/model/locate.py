"""Write where the combined 3D model puts each zone and part into 00-CAR (D-421).

Run from the tree root, after blend.py:

    python3 01-REFERENCE/model/locate.py            # show what would change
    python3 01-REFERENCE/model/locate.py --write    # write it

Reads   01-REFERENCE/model/out/locations.json   written by blend.py (out of git)
Writes  00-CAR zones.model_box_mm, zones.model_from, parts.model_at_mm, parts.model_from

Owns those four columns and nothing else. They are model estimates, never measurements
(R11): the Manual's "The car" view uses them to pin a zone or a part on the 3D view and on
the app's renders (app/public/car/views.json). A part the models cannot place stays empty
and is found by its zone.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import rx7  # noqa: E402

CAR = ROOT / "00-CAR"
LOC = ROOT / "01-REFERENCE" / "model" / "out" / "locations.json"


def cell(groups):
    return "; ".join(" ".join(str(v) for v in g) for g in groups)


def update(table, key, got, col_val, col_from, field):
    hdr, rows = rx7.read_table(CAR, table)
    changed = 0
    for r in rows:
        e = got.get(r[key])
        val, frm = (cell(e[field]), e["from"]) if e else ("", "")
        if (r.get(col_val, ""), r.get(col_from, "")) != (val, frm):
            print(f"{table}:{r[key]} {col_val} {r.get(col_val, '')!r} -> {val!r}")
            r[col_val], r[col_from] = val, frm
            changed += 1
    for c in (col_val, col_from):
        if c not in hdr:
            hdr.append(c)
    return hdr, rows, changed


def main() -> int:
    if not LOC.exists():
        print("no locations.json - run blend.py first")
        return rx7.RC_WAITING
    loc = json.loads(LOC.read_text(encoding="utf-8"))
    zh, zr, zc = update("zones", "id", loc["zones"], "model_box_mm", "model_from", "boxes")
    ph, pr, pc = update("parts", "id", loc["parts"], "model_at_mm", "model_from", "points")
    if not (zc or pc):
        return rx7.RC_WAITING
    if "--write" in sys.argv:
        rx7.write_table(CAR, "zones", zh, zr)
        rx7.write_table(CAR, "parts", ph, pr)
    return rx7.RC_OK


if __name__ == "__main__":
    sys.exit(main())

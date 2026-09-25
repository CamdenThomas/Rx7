"""Import the CAD finders' manifests into the record (01-REFERENCE `cad` table, D-418).

Run from the tree root:

    python3 01-REFERENCE/model/catalog.py            # show what would be added
    python3 01-REFERENCE/model/catalog.py --write    # add the new rows

Reads   01-REFERENCE/model/library/<category>/manifest.jsonl   one JSON line per find (out of git)
Writes  01-REFERENCE/data/cad.csv                          through rx7.py's own table writer

Owns the `cad` table's rows it adds, and nothing else. A row already in `cad` is never
overwritten: once imported, the record is the fact's home (R2) and the manifest is scratch.
The manifests' free-text units are turned into a size in mm here, and only where the unit
is plain; anything else keeps its size empty and its words in `note`.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import rx7  # noqa: E402

AREA = ROOT / "01-REFERENCE"
FILES = AREA / "model" / "library"
UNIT = [("mm", 1.0), ("cm", 10.0), ("inch", 25.4), ("m", 1000.0)]  # order matters: mm before m
MATCH = {"exact": "exact", "close": "close", "different": "different"}


def mm_factor(units: str):
    u = (units or "").strip().lower()
    if "?" in u or u.startswith(("unknown", "unclear", "px", "0.1")):
        return None
    for name, f in UNIT:
        if u.startswith(name):
            return f
    return None


def size_mm(d: dict) -> str:
    ext, f = d.get("extents"), mm_factor(d.get("units_guess", ""))
    if not f or not isinstance(ext, list) or len(ext) != 3:
        return ""
    try:
        return " x ".join(f"{float(x) * f:.0f}" for x in ext)
    except (TypeError, ValueError):
        return ""


def flat(v) -> str:
    if v is None:
        return ""
    if isinstance(v, (list, tuple)):
        return "; ".join(flat(x) for x in v)
    # the finders wrote while the library sat in 01-REFERENCE/cad/files (moved, D-418)
    return " ".join(str(v).split()).replace("01-REFERENCE/cad/files", "01-REFERENCE/model/library")


def row(cat: str, d: dict) -> dict:
    tri = d.get("triangles")
    q = d.get("quality")
    note = flat(d.get("notes"))
    if not size_mm(d) and d.get("extents"):
        note = f"extents as found: {flat(d.get('extents'))} {flat(d.get('units_guess'))}. " + note
    return {
        "id": d["slug"].strip(),
        "category": cat,
        "title": flat(d.get("title")) or d["slug"],
        "subject": flat(d.get("subject")) or flat(d.get("title")),
        "fits": MATCH.get(str(d.get("generation_match", "")).split()[0].lower() if d.get("generation_match") else "", "different"),
        "site": flat(d.get("site")),
        "url": flat(d.get("url")),
        "author": flat(d.get("author")),
        "licence": flat(d.get("license")),
        "format": flat(d.get("format")),
        "obtained": "yes" if d.get("obtained") is True else "no",
        "login": "yes" if d.get("needs_login") is True else "no",
        "local_path": flat(d.get("local_path")) if d.get("obtained") is True else "",
        "size_mm": size_mm(d),
        "scale": flat(d.get("scale_guess")),
        "triangles": str(int(tri)) if isinstance(tri, (int, float)) and tri else "",
        "quality": str(int(q)) if isinstance(q, (int, float)) and q else "",
        "detail": flat(d.get("detail")),
        "note": note,
    }


def main() -> int:
    write = "--write" in sys.argv
    hdr, rows = rx7.read_table(AREA, "cad")
    have = {r["id"] for r in rows}
    new = []
    for man in sorted(FILES.glob("*/manifest.jsonl")):
        for line in man.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = row(man.parent.name, json.loads(line))
            if r["id"] in have:
                continue
            have.add(r["id"])
            new.append(r)
    print(f"{len(new)} new of {len(rows) + len(new)}")
    if not new:
        return rx7.RC_WAITING
    if write:
        rx7.write_table(AREA, "cad", hdr, rows + new)
    return 0


if __name__ == "__main__":
    sys.exit(main())

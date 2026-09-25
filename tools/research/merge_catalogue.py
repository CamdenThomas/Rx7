"""Merge the catalogue chunk CSVs into 01-REFERENCE/data/catalogue.csv, one row per printed
table row, keyed <book>-<page>-<row on page>. Prints counts and every doubtful cell."""
import csv, glob, re, sys, collections
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
BOOK = {"Engine-Chassis": "EC", "Body-Index": "BI"}
COLS = ["id", "book", "page", "figure", "figure_title", "dcode", "description", "part_no", "qty",
        "model", "remarks", "fits", "fits_why"]
PN = re.compile(r"^[0-9A-Z]{4}-[0-9A-Z]{2}-[0-9A-Z]{3,5}$")

rows, bad = [], []
for f in sorted(glob.glob(str(SRC / "*.csv"))):
    with open(f, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            r = {k: (v or "").strip() for k, v in r.items() if k}
            book = next((v for k, v in BOOK.items() if k in r.get("file", "")), None)
            if not book:
                bad.append(f"{Path(f).name}: no book in file={r.get('file')!r}")
                continue
            try:
                page = int(r.get("pdf_page", ""))
            except ValueError:
                bad.append(f"{Path(f).name}: page {r.get('pdf_page')!r}")
                continue
            fits = r.get("fits", "").lower()
            if fits not in ("yes", "no", "unclear"):
                bad.append(f"{book}-{page}: fits {fits!r} -> unclear")
                fits = "unclear"
            rows.append({"book": book, "page": page, **{c: r.get(c, "") for c in COLS[3:]}, "fits": fits})

rows.sort(key=lambda r: (r["book"] != "EC", r["page"]))
n = collections.Counter()
seen = set()
out = []
for r in rows:
    n[(r["book"], r["page"])] += 1
    r["id"] = f"{r['book']}-{r['page']:03d}-{n[(r['book'], r['page'])]:02d}"
    key = (r["book"], r["page"], r["dcode"], r["part_no"], r["description"])
    if key in seen and r["part_no"]:
        bad.append(f"{r['id']}: duplicate of an earlier row on the same page ({r['part_no']})")
    seen.add(key)
    if r["part_no"] and not PN.match(r["part_no"].replace("?", "0")):
        bad.append(f"{r['id']}: part_no {r['part_no']!r} is not Mazda-shaped")
    if "?" in r["part_no"]:
        bad.append(f"{r['id']}: unreadable characters in {r['part_no']!r}")
    r["page"] = str(r["page"])
    out.append(r)

with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(out)

c = collections.Counter(r["fits"] for r in out)
pages = {(r["book"], r["page"]) for r in out}
print(f"{len(out)} rows from {len(pages)} pages; fits {dict(c)}; "
      f"{len({r['part_no'] for r in out if r['part_no']})} distinct part numbers")
print(f"{len(bad)} doubtful cell(s)")
for b in bad[:400]:
    print("  " + b)

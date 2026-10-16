"""page.py - what a parsing agent reads: one page or a few, as text or as an image (D-574).

    python3 02-PROJECTS/00-library/tools/page.py text  DOC-062 12-14
    python3 02-PROJECTS/00-library/tools/page.py image DOC-048 27 [--dpi 120] [--crop x,y,w,h]

`text` prints each page's text layer (or its OCR text when the PDF has none), headed
`=== DOC-062.012 (printed 1-12) ===`; a page with no text says so - then look at its image.
`image` renders one page to a PNG under /tmp/rx7-pages and prints the path; --crop takes
fractions of the page (0.1,0.5,0.4,0.3 = from 10 % across and 50 % down, 40 % wide, 30 % tall)
for a figure the whole page shows too small. Read the PNG with the Read tool.

Owns nothing; reads 00-CAR docs and pages. Needs poppler (pdftotext, pdftoppm).
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import rx7  # noqa: E402

OUT = Path("/tmp/rx7-pages")


def pages_of(spec):
    out = []
    for part in spec.replace(",", " ").split():
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def doc_row(did):
    for d in rx7.read_table(ROOT / "00-CAR", "docs")[1]:
        if d["id"] == did:
            return d
    sys.exit(f"no doc {did}")


def main(argv):
    if len(argv) < 3 or argv[0] not in ("text", "image"):
        print(__doc__)
        return 3
    mode, did, spec = argv[0], argv[1], argv[2]
    d = doc_row(did)
    if not d.get("path") or not (ROOT / d["path"]).exists():
        sys.exit(f"{did}: its file is not on this disk ({d.get('file')}) - see docs.offline")
    pdf = ROOT / d["path"]
    printed = {p["id"]: p.get("printed", "") for p in rx7.read_table(ROOT / "00-CAR", "pages")[1] if p["doc"] == did}
    if mode == "text":
        ocr = (ROOT / d["ocr"]).read_text(errors="replace").split("\f") if d.get("text") == "ocr" and d.get("ocr") else None
        for n in pages_of(spec):
            pid = f"{did}.{n:03d}"
            if ocr is not None:
                t = ocr[n - 1] if n - 1 < len(ocr) else ""
            else:
                t = subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), str(pdf), "-"],
                                   capture_output=True, text=True, errors="replace").stdout
            print(f"=== {pid} (printed {printed.get(pid) or '?'}) ===")
            print(t.strip() or "(no text on this page - read its image)")
        return 0
    dpi, crop = 110, None
    rest = argv[3:]
    if "--dpi" in rest:
        dpi = int(rest[rest.index("--dpi") + 1])
    if "--crop" in rest:
        crop = [float(x) for x in rest[rest.index("--crop") + 1].split(",")]
    OUT.mkdir(exist_ok=True)
    n = pages_of(spec)[0]
    stem = OUT / f"{did}.{n:03d}-{dpi}" if not crop else OUT / f"{did}.{n:03d}-{dpi}-{'-'.join(str(int(c * 100)) for c in crop)}"
    cmd = ["pdftoppm", "-r", str(dpi), "-f", str(n), "-l", str(n), "-singlefile", "-png"]
    if crop:
        info = subprocess.run(["pdfinfo", "-f", str(n), "-l", str(n), str(pdf)], capture_output=True, text=True).stdout
        w_pt, h_pt = 612.0, 792.0
        for line in info.splitlines():
            if line.startswith(f"Page    {n} size:") or line.startswith("Page size:"):
                parts = line.split(":")[1].split()
                w_pt, h_pt = float(parts[0]), float(parts[2])
        W, H = w_pt * dpi / 72, h_pt * dpi / 72
        x, y, w, h = crop
        cmd += ["-x", str(int(x * W)), "-y", str(int(y * H)), "-W", str(int(w * W)), "-H", str(int(h * H))]
    subprocess.run(cmd + [str(pdf), str(stem)], check=True)
    print(f"{stem}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""inventory.py - phase 1 of the library plan (D-574, tools/doc/library.md): every PDF in the tree
as a 00-CAR `docs` row, every page as a `pages` row, and a `sources` row for every file that had
none; then the pages that existing rows already cite are marked `cited`, with those rows.

Owns: 00-CAR docs and pages (adds and refreshes; never lowers a page's status or drops its rows)
and the sources rows it creates (S- ids after the highest, only for a file no row names).
Reads: 00-CAR sources, cad, specs, terminals, procedures, procedure_steps, circuit_paths,
catalogue, intervals.

Run from the tree:  python3 02-PROJECTS/05-library/tools/inventory.py  [--dry]
Needs poppler (pdfinfo, pdftotext). Idempotent: a second run changes nothing it has written,
only adds what is new. Takes rx7.py's write lock, so it can run while agents work.
"""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import rx7  # noqa: E402

CAR = ROOT / "00-CAR"
OCR = CAR / "library" / "docs" / "ocr"
DRY = "--dry" in sys.argv

# ------------------------------------------------------------------ what each folder is worth
# (prefix of the path, owner, tier, scope). The first prefix that matches wins. Tier 1 is read
# first; 5 is index only. Scope is whom the document describes (1982 12A automatic GS = this car).
RULES = [
    ("00-CAR/library/docs/wiring-1982/", "00-CAR", 1, "this-car"),
    ("00-CAR/library/docs/fsm-technical-data-81-83/", "00-CAR", 1, "mixed"),
    ("00-CAR/library/docs/parts-catalogue-81-83/", "00-CAR", 1, "mixed"),
    ("00-CAR/library/docs/manual-1983-full/", "00-CAR", 1, "other-year"),
    ("00-CAR/library/docs/fsm-1985-sections/1985_RX-7_Workshop_Manual_Index", "00-CAR", 4, "other-year"),
    ("00-CAR/library/docs/fsm-1985-sections/", "00-CAR", 1, "other-year"),
    ("00-CAR/library/datasheets/PT525/", "00-CAR", 1, "other-year"),
    ("02-PROJECTS/02-cad/model/library/body/sa-rx7-1980-fsm-body-section/", "00-CAR", 1, "other-year"),
    ("00-CAR/library/docs/fsm-1980-sections/", "00-CAR", 2, "other-year"),
    ("00-CAR/library/docs/fsm-technical-data-80/", "00-CAR", 2, "other-year"),
    ("00-CAR/library/docs/service-bulletins-", "00-CAR", 2, "mixed"),
    ("00-CAR/library/docs/body-shop-manual-1985/", "00-CAR", 2, "mixed"),
    ("00-CAR/library/docs/training-1981/", "00-CAR", 2, "mixed"),
    ("00-CAR/library/docs/emissions-check-1981/", "00-CAR", 2, "mixed"),
    ("00-CAR/library/docs/ac-dealer-install/", "00-CAR", 2, "mixed"),
    ("00-CAR/library/docs/brochure-1982/", "00-CAR", 2, "this-car"),
    ("00-CAR/library/datasheets/PT054/", "00-CAR", 3, "other-model"),
    ("00-CAR/library/datasheets/", "00-CAR", 2, "this-car"),
    ("00-CAR/library/docs/wiring-1983/", "00-CAR", 3, "other-year"),
    ("00-CAR/library/docs/carburetor-manuals/", "00-CAR", 3, "mixed"),
    ("00-CAR/library/docs/rotary-overhaul-criteria-1979/", "00-CAR", 3, "mixed"),
    ("00-CAR/library/docs/book-yamamoto-rotary-1981/", "00-CAR", 3, "mixed"),
    ("00-CAR/library/docs/setup-tuning-early-rx7/", "00-CAR", 3, "mixed"),
    ("00-CAR/library/docs/brochure-1981-fog-light/", "00-CAR", 3, "other-year"),
    ("00-CAR/library/docs/te-catalogue-2018/", "01-electrical", 3, "other-model"),
    ("02-PROJECTS/01-electrical/", "01-electrical", 2, "this-car"),
    ("02-PROJECTS/02-cad/model/library/electrical/", "01-electrical", 3, "this-car"),
    ("02-PROJECTS/02-cad/model/library/swap/nissan-", "03-engine", 4, "other-model"),
    ("02-PROJECTS/02-cad/model/library/swap/chevy-", "02-cad", 5, "other-model"),
    ("02-PROJECTS/02-cad/model/library/swap/ls3-v8-engine-moving-model", "02-cad", 5, "other-model"),
    ("02-PROJECTS/02-cad/model/library/swap/", "03-engine", 4, "other-model"),
    ("02-PROJECTS/02-cad/model/library/rotary/", "02-cad", 5, "other-model"),
    ("02-PROJECTS/02-cad/model/library/", "02-cad", 4, "other-model"),
]


def rule(path):
    for pre, owner, tier, scope in RULES:
        if path.startswith(pre):
            return owner, tier, scope
    return "00-CAR", 3, "mixed"


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace").stdout


def all_pdfs():
    out = []
    for base in (CAR / "library", ROOT / "02-PROJECTS"):
        for p in base.rglob("*"):
            if p.suffix.lower() == ".pdf" and "node_modules" not in p.parts and p.is_file():
                out.append(p.relative_to(ROOT).as_posix())
    return sorted(out)


def page_texts(path, npages, ocr):
    """One string per page: the text layer if there is one, else the OCR file split on form feeds."""
    t = run("pdftotext", "-layout", str(ROOT / path), "-")
    pages = t.split("\f")
    have = sum(len(x.strip()) for x in pages[:npages])
    if have > 40 * npages:
        return pages[:npages] + [""] * (npages - len(pages)), "yes"
    if ocr and (ROOT / ocr).exists():
        pages = (ROOT / ocr).read_text(errors="replace").split("\f")
        return pages[:npages] + [""] * (npages - len(pages)), "ocr"
    return [""] * npages, "no"


PRINTED_RES = [
    re.compile(r"(?<![\w.])(\d{1,2}[A-Z]?)\s?[-–]\s?(\d{1,3})(?![\w.])"),   # 4A-16, 14-24
    re.compile(r"(?<![\w.])(\d{1,2}[A-Z]?|[A-Z])\s?:\s?(\d{1,3})(?![\w.])"),  # 7A:20, T:6
]


def printed_of(text):
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    for l in lines[-3:][::-1] + lines[:3]:
        if len(l) > 40 and not re.search(r"\s{3,}\S{1,6}$", l):
            m = None
        for rx in PRINTED_RES:
            ms = list(rx.finditer(l))
            if ms and (len(l) < 30 or ms[-1].end() >= len(l) - 2 or ms[0].start() <= 1):
                m = ms[-1] if ms[-1].end() >= len(l) - 2 else ms[0]
                sep = "-" if rx is PRINTED_RES[0] else ":"
                return f"{m.group(1)}{sep}{m.group(2)}"
    return ""


def kind_of(text, layer):
    s = text.strip()
    if layer == "no":
        return "unknown"
    if len(s) < 25:
        return "unknown"  # a scan's empty text layer: a drawing as often as a blank page
    lines = [l for l in s.splitlines() if l.strip()]
    cols = sum(1 for l in lines if len(re.findall(r"\S\s{3,}\S", l)) >= 2)
    digits = sum(c.isdigit() for c in s) / max(len(s), 1)
    if len(s) < 300:
        return "figure"
    if cols > 0.4 * len(lines) or digits > 0.18:
        return "table"
    return "text"


def topic_of(text):
    for l in text.strip().splitlines()[:12]:
        l = re.sub(r"\s{2,}", " ", l.strip())
        if 4 <= len(l) <= 70 and sum(c.isalpha() for c in l) > 0.6 * len(l) and l.upper() == l:
            return l.title()[:70]
    for l in text.strip().splitlines()[:6]:
        l = re.sub(r"\s{2,}", " ", l.strip())
        if 6 <= len(l) <= 70 and sum(c.isalpha() for c in l) > 0.6 * len(l):
            return l[:70]
    return ""


def title_from(path, first_page):
    stem = Path(path).stem.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", stem).strip()


# ------------------------------------------------------------------ the cites already in the record

PDF_P = re.compile(r"PDF\s*p\.?\s*(\d+)", re.I)
PRINT_P = re.compile(r"(?<![\w.])(\d{1,2}[A-Z]?|[A-Z])\s?([-:])\s?(\d{1,3})(?![\w.])")
PLAIN_P = re.compile(r"(?<![\w.:-])p\.?\s*(\d{1,3})(?![\w.:-])")


def cites():
    """(source id, page text, row token) for every row that cites a page."""
    out = []
    def tab(t):
        return rx7.read_table(CAR, t)[1] if (CAR / "data" / f"{t}.csv").exists() else []
    for t, key in (("specs", "id"), ("terminals", "id"), ("intervals", "id"), ("diagnosis", "id")):
        for r in tab(t):
            for part in re.split(r";", r.get("page") or ""):
                srcs = re.findall(r"S-\d{3}", part) or re.findall(r"S-\d{3}", r.get("source") or "")
                for s in srcs[:1] or []:
                    out.append((s, part, f"{t}:{r[key]}"))
    procs = {r["id"]: (r.get("source") or "") for r in tab("procedures")}
    for r in tab("procedure_steps"):
        for s in re.findall(r"S-\d{3}", procs.get(r.get("procedure"), ""))[:1]:
            out.append((s, r.get("page") or "", f"procedure_steps:{r['id']}"))
    csrc = {r["file"]: (re.findall(r"S-\d{3}", r.get("source") or "") or ["S-001"])[0] for r in tab("circuits")}
    for r in tab("circuit_paths"):
        pg = (r.get("page") or "").strip()
        if pg:
            s = csrc.get(r.get("circuit"), "S-001")
            out.append((s, ("PDF p." + pg) if pg.isdigit() else pg, f"circuit_paths:{r['id']}"))
    for r in tab("catalogue"):
        book = (r.get("book") or "").strip()
        out.append(("S-005", f"{book}|PDF p.{(r.get('page') or '').strip()}", f"catalogue:{r['id']}"))
    return out


def resolve(src, text, docs_of, pages_by_doc):
    """The page ids a cite names: PDF p.N exactly; a printed number through pages.printed (or, for
    S-002's sections, the section's own file); a plain p.N on a one-file source."""
    files = docs_of.get(src, [])
    if not files:
        return []
    if src == "S-005" and "|" in text:
        book, text = text.split("|", 1)
        files = [d for d in files if ("Engine-Chassis" in d["path"]) == (book == "EC")] or files
    hits = []
    raw = text
    if len(files) == 1:
        ns = []
        for a, b in re.findall(r"PDF\s*p\.?\s*(\d+)(?:\s*[-–]\s*(\d+)(?![-\d]))?", text, re.I):
            ns += list(range(int(a), int(b) + 1)) if b and int(b) > int(a) and int(b) - int(a) < 40 else [int(a)]
        ns += [int(x) for x in re.findall(r"\band\s+p\.?\s*(\d+)", text) if PDF_P.search(text)]
        if ns:
            return [f"{files[0]['id']}.{n:03d}" for n in ns if n <= int(files[0]["pages"] or 0)]
    text = re.sub(r"S-\d{3}", " ", text)
    text = re.sub(r"\b(?:pp?|PDF p)\.\s*", " ", text)
    for sec, sep, n in PRINT_P.findall(text):
        tok = f"{sec}{sep}{n}"
        for d in files:
            if src == "S-002" and sep == "-":
                code = re.search(r"Section_(\w+?)_", Path(d["path"]).name)
                if code and code.group(1) == sec and int(n) <= int(d["pages"] or 0):
                    hits.append(f"{d['id']}.{int(n):03d}")
                    continue
            for pid, pr in pages_by_doc.get(d["id"], {}).items():
                if pr == tok.replace(":", sep):
                    hits.append(pid)
    if hits:
        return hits
    if len(files) == 1:
        for n in PLAIN_P.findall(raw):
            if int(n) <= int(files[0]["pages"] or 0):
                hits.append(f"{files[0]['id']}.{int(n):03d}")
    return hits


def main():
    rx7.take_write_lock()
    shdr, sources = rx7.read_table(CAR, "sources")
    dhdr, docs = rx7.read_table(CAR, "docs")
    phdr, pages = rx7.read_table(CAR, "pages")
    _, cad = rx7.read_table(CAR, "cad")
    by_path = {d["path"]: d for d in docs}
    pages_by_id = {p["id"]: p for p in pages}
    new_sources = []

    def source_for(path):
        for s in sources + new_sources:
            lp = (s.get("local_path") or "").strip()
            if lp == path:
                return s["id"]
        for s in sources + new_sources:
            lp = (s.get("local_path") or "").strip()
            if lp and (lp.endswith("/") and path.startswith(lp) or ("*" in lp and path.startswith(lp.split("*")[0]))):
                return s["id"]
        # a model-library file: its cad row gives the title, url and licence
        for c in cad:
            lp = (c.get("local_path") or "").strip().rstrip("/")
            if lp and path.startswith(lp + "/"):
                sid = rx7.next_keys({s["id"] for s in sources + new_sources}, 1)[0]
                new_sources.append({"id": sid, "title": f"{c.get('title', '')} - {Path(path).name}", "kind": "datasheet",
                                    "covers": c.get("subject", ""), "url": c.get("url", ""), "format": "pdf",
                                    "credibility": "primary" if "datasheet" in c["id"] or "-te" in c["id"] else "secondary",
                                    "obtained": "yes", "local_path": path,
                                    "note": f"Bundled with the 02-cad library row {c['id']} (licence: {c.get('licence', '') or 'as the site states'}). Added by the library inventory, 2026-10-14."})
                return sid
        sid = rx7.next_keys({s["id"] for s in sources + new_sources}, 1)[0]
        new_sources.append({"id": sid, "title": title_from(path, ""), "kind": "datasheet", "covers": "", "url": "",
                            "format": "pdf", "credibility": "secondary", "obtained": "yes", "local_path": path,
                            "note": "Found on disk with no sources row; added by the library inventory, 2026-10-14. Title from the file name - the first agent to read it corrects title, covers and url."})
        return sid

    md5s = {}
    for path in all_pdfs():
        info = run("pdfinfo", str(ROOT / path))
        m = re.search(r"Pages:\s+(\d+)", info)
        n = int(m.group(1)) if m else 0
        md5 = hashlib.md5((ROOT / path).read_bytes()).hexdigest()
        ocr = OCR / (Path(path).name + ".txt")
        if not ocr.exists():
            ocr = OCR / (Path(path).stem + ".txt")
        ocr_rel = ocr.relative_to(ROOT).as_posix() if ocr.exists() else ""
        texts, layer = page_texts(path, n, ocr_rel)
        owner, tier, scope = rule(path)
        d = by_path.get(path)
        if d is None:
            d = {"id": rx7.next_keys({x["id"] for x in docs} | {"DOC-000"}, 1)[0], "path": path, "file": "on-disk"}
            docs.append(d)
            by_path[path] = d
        d.update({"source": d.get("source") or source_for(path), "pages": str(n), "md5": md5, "text": layer,
                  "ocr": ocr_rel if layer == "ocr" else "", "owner": d.get("owner") or owner,
                  "tier": d.get("tier") or str(tier), "scope": d.get("scope") or scope,
                  "title": d.get("title") or title_from(path, texts[0] if texts else "")})
        if md5 in md5s and not d.get("duplicate_of"):
            d["duplicate_of"] = md5s[md5]
        md5s.setdefault(md5, d["id"])
        for i in range(1, n + 1):
            pid = f"{d['id']}.{i:03d}"
            t = texts[i - 1] if i - 1 < len(texts) else ""
            p = pages_by_id.get(pid)
            if p is None:
                p = {"id": pid, "doc": d["id"], "n": str(i), "status": "open", "rows": ""}
                pages.append(p)
                pages_by_id[pid] = p
            p["printed"] = p.get("printed") or printed_of(t)
            p["kind"] = p.get("kind") if p.get("kind") not in ("", None, "unknown", "blank") else kind_of(t, layer)
            p["topic"] = p.get("topic") or topic_of(t)
            p["scope"] = p.get("scope") or (d["scope"] if d["scope"] != "mixed" else "unknown")
            if d.get("duplicate_of") and p["status"] == "open":
                p["status"] = "duplicate"
    # S-004 and S-042 share one file: the inventory keeps the first sources row for it.
    sources_all = sources + new_sources
    docs_of = {}
    for d in docs:
        docs_of.setdefault(d["source"], []).append(d)
    pages_by_doc = {}
    for p in pages:
        pages_by_doc.setdefault(p["doc"], {})[p["id"]] = p.get("printed", "")
    marked = 0
    for src, text, tok in cites():
        for pid in resolve(src, text, docs_of, pages_by_doc):
            p = pages_by_id.get(pid)
            if not p:
                continue
            toks = set((p.get("rows") or "").split())
            if tok not in toks:
                toks.add(tok)
                p["rows"] = " ".join(sorted(toks))
                marked += 1
            if p["status"] == "open":
                p["status"] = "cited"
    docs.sort(key=lambda d: d["id"])
    pages.sort(key=lambda p: p["id"])
    print(f"{len(docs)} docs, {sum(int(d['pages'] or 0) for d in docs)} pages, {len(new_sources)} new sources rows, "
          f"{sum(1 for p in pages if p['status'] == 'cited')} pages cited ({marked} row links), "
          f"{sum(1 for d in docs if d.get('duplicate_of'))} duplicate files")
    if DRY:
        return 0
    if new_sources:
        rx7.write_table(CAR, "sources", shdr, sources_all)
    rx7.write_table(CAR, "docs", dhdr, docs)
    rx7.write_table(CAR, "pages", phdr, pages)
    return 0


if __name__ == "__main__":
    sys.exit(main())

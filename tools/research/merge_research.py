"""Merge research/<batch>.json files (Stage 2) into the record: 01-REFERENCE sources and cad,
00-CAR specs, terminals and parts. Source keys become new S- ids (a URL already in sources
reuses its id); specs get the next SP- ids; terminals are <part>-<terminal>. Dry run unless
--write. Usage: merge_research.py SCRATCH BATCH_ID_PREFIX... [--write]"""
import csv, glob, json, re, sys
from pathlib import Path

S = Path(sys.argv[1])
prefixes = [a for a in sys.argv[2:] if not a.startswith("--") and not a.startswith("keep=")]
KEEP_CONFIRM = {x for a in sys.argv[2:] if a.startswith("keep=") for x in a[5:].split(",") if x}
WRITE = "--write" in sys.argv
T = Path("/home/crash/docs/storage/Rx7")


def load(p):
    with open(p, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        return rd.fieldnames, list(rd)


def save(p, hdr, rows):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=hdr, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


P = {n: T / f"00-CAR/data/{n}.csv" for n in ("parts", "specs", "terminals")}
R = {n: T / f"01-REFERENCE/data/{n}.csv" for n in ("sources", "cad")}
ph, parts = load(P["parts"]); sh, specs = load(P["specs"]); th, terms = load(P["terminals"])
oh, srcs = load(R["sources"]); ch, cads = load(R["cad"])
part_by = {r["id"]: r for r in parts}
url_to = {r["url"].strip(): r["id"] for r in srcs if r.get("url", "").strip()}
nS = max(int(r["id"][2:]) for r in srcs) + 1
nSP = max(int(r["id"][3:]) for r in specs) + 1
cad_ids = {r["id"] for r in cads}
term_ids = {r["id"] for r in terms}
spec_seen = {(r.get("part", ""), r.get("item", "").strip().lower(), r.get("value", "").strip()) for r in specs}

EN = {"confidence": {"primary", "secondary", "unverified"}, "applies": {"", "other-car", "not-fitted", "replaced"},
      "format": {"html", "pdf", "pdf+step", "pdf-scan", "web-viewer", "obj", "json", "jpg"},
      "credibility": {"primary", "secondary", "tertiary"}, "cadcat": {"body", "parts", "rotary", "swap", "electrical"},
      "fits": {"exact", "close", "different"}}
yn = lambda v: "yes" if str(v).strip().lower() in ("yes", "true", "1") else "no"

files = sorted(f for f in glob.glob(str(S / "research" / "*.json")) if any(Path(f).stem.startswith(p) for p in prefixes))
problems, n = [], {"sources": 0, "specs": 0, "terminals": 0, "cad": 0, "parts": 0, "confirm_added": 0}
for f in files:
    b = Path(f).stem
    try:
        d = json.load(open(f))
    except Exception as e:
        problems.append(f"{b}: unreadable JSON ({e})")
        continue
    keymap = {}
    for s in d.get("sources", []):
        url = (s.get("url") or "").strip()
        if url and url in url_to:
            keymap[s.get("key", "")] = url_to[url]
            continue
        sid = f"S-{nS:03d}"; nS += 1
        keymap[s.get("key", "")] = sid
        fmt = s.get("format", "") if s.get("format", "") in EN["format"] else ""
        cred = s.get("credibility", "") if s.get("credibility", "") in EN["credibility"] else ""
        srcs.append({"id": sid, "title": s.get("title", ""), "kind": s.get("kind", ""), "covers": s.get("covers", ""), "url": url,
                     "format": fmt, "credibility": cred, "obtained": yn(s.get("obtained")), "local_path": s.get("local_path", ""),
                     "note": s.get("note", "")})
        if url:
            url_to[url] = sid
        n["sources"] += 1

    def src(cell):
        toks = re.split(r"[\s,;]+", cell or "")
        out = []
        for t in toks:
            if not t:
                continue
            if t in keymap:
                out.append(keymap[t])
            elif re.fullmatch(r"S-\d{3}", t):
                out.append(t)
            else:
                problems.append(f"{b}: unknown source token {t!r}")
        return ",".join(dict.fromkeys(out))

    for s in d.get("specs", []):
        pid = s.get("part", "")
        if pid not in part_by:
            problems.append(f"{b}: spec for unknown part {pid}"); continue
        key = (pid, s.get("item", "").strip().lower(), s.get("value", "").strip())
        if key in spec_seen or not s.get("item") or not s.get("value"):
            continue
        spec_seen.add(key)
        conf = s.get("confidence", "") if s.get("confidence", "") in EN["confidence"] else "secondary"
        app = s.get("applies", "") if s.get("applies", "") in EN["applies"] else ""
        specs.append({"id": f"SP-{nSP:03d}", "category": s.get("category", ""), "item": s["item"].strip(), "value": s["value"].strip(),
                      "unit": s.get("unit", ""), "source": src(s.get("source", "")), "page": s.get("page", ""), "confidence": conf,
                      "note": s.get("note", ""), "system": part_by[pid]["system"], "part": pid, "applies": app})
        nSP += 1; n["specs"] += 1

    for t in d.get("terminals", []):
        pid = t.get("part", "")
        if pid not in part_by or not t.get("terminal"):
            problems.append(f"{b}: terminal for unknown part {pid}"); continue
        lab = re.sub(r"[^A-Za-z0-9._-]+", "_", t["terminal"].strip()).strip("_") or "T"
        tid = f"{pid}-{lab}"; k = 2
        while tid in term_ids:
            tid = f"{pid}-{lab}-{k}"; k += 1
        term_ids.add(tid)
        note = t.get("note", "")
        if "confirm" not in note.lower():
            note = (note + " Confirm on the car.").strip()
        terms.append({"id": tid, "part": pid, "terminal": t["terminal"].strip(), "function": t.get("function", ""), "inside": t.get("inside", ""),
                      "wire": t.get("wire", ""), "to": t.get("to", ""), "source": src(t.get("source", "")), "page": t.get("page", ""), "note": note})
        n["terminals"] += 1

    for c in d.get("cad", []):
        cid = re.sub(r"[^a-z0-9-]+", "-", (c.get("id") or "").lower()).strip("-")
        if not cid or cid in cad_ids:
            continue
        cat = c.get("category", "") if c.get("category", "") in EN["cadcat"] else "parts"
        fits = c.get("fits", "") if c.get("fits", "") in EN["fits"] else "different"
        row = {h: "" for h in ch}
        row.update({"id": cid, "category": cat, "title": c.get("title", "") or cid, "subject": c.get("subject", "") or c.get("title", ""),
                    "fits": fits, "site": c.get("site", ""), "url": c.get("url", ""), "author": c.get("author", ""), "licence": c.get("licence", ""),
                    "format": c.get("format", ""), "obtained": yn(c.get("obtained")), "login": yn(c.get("login")), "local_path": c.get("local_path", ""),
                    "detail": c.get("detail", ""), "note": (c.get("note", "") + (f" For {c['part']}." if c.get("part") else "")).strip()})
        cads.append(row); cad_ids.add(cid); n["cad"] += 1
        if c.get("part") in part_by and not part_by[c["part"]].get("cad"):
            part_by[c["part"]]["cad"] = cid

    for u in d.get("parts", []):
        r = part_by.get(u.get("id", ""))
        if not r:
            problems.append(f"{b}: update for unknown part {u.get('id')}"); continue
        touched = False
        for col in ("link", "support", "cad"):
            v = (u.get(col) or "").strip()
            if v and not r.get(col):
                r[col] = v; touched = True
        add = (u.get("note_add") or "").strip()
        # A doubt about one detail in the note (a bulb's trade number, a wire colour) is a
        # "check", so the part stays in the Manual; only a doubt about the part itself holds it.
        if u.get("id") not in KEEP_CONFIRM:
            add = re.sub(r"\b(c|C)onfirm\b", lambda m: "check" if m.group(1) == "c" else "Check", add)
        if add and add not in r.get("note", ""):
            if "confirm" in add.lower() and "confirm" not in r.get("note", "").lower():
                n["confirm_added"] += 1
            r["note"] = (r.get("note", "") + " " + add).strip(); touched = True
        n["parts"] += touched

print(f"{len(files)} batch file(s): {n}")
print(f"{len(problems)} problem(s)")
for p in problems[:60]:
    print("  " + p)
if WRITE:
    save(P["parts"], ph, parts); save(P["specs"], sh, specs); save(P["terminals"], th, terms)
    save(R["sources"], oh, srcs); save(R["cad"], ch, cads)
    print("written")

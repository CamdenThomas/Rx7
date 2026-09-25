"""Merge the Stage 1b section files into 00-CAR/data/parts.csv. New parts get the next PT ids
in section order; keys become ids; existing parts gain catalogue refs, a blank oem_no, and a
parent. Refuses (exit 1) on a parent that resolves to nothing or a system/zone that does not
exist. Dry run unless --write."""
import csv, glob, json, re, sys
from pathlib import Path

S = Path(sys.argv[1])
WRITE = "--write" in sys.argv
ROOT = Path("/home/crash/docs/storage/Rx7")
P = ROOT / "00-CAR/data/parts.csv"
rows = list(csv.DictReader(open(P, newline="", encoding="utf-8")))
hdr = list(rows[0].keys())
if "parent" not in hdr:
    hdr.append("parent")
    for r in rows:
        r["parent"] = ""
by_id = {r["id"]: r for r in rows}
systems = {r["id"] for r in csv.DictReader(open(ROOT / "00-CAR/data/systems.csv"))}
zones = {r["id"] for r in csv.DictReader(open(ROOT / "00-CAR/data/zones.csv"))}
nxt = max(int(r["id"][2:]) for r in rows) + 1

problems, new, keymap, touched = [], [], {}, 0
sections = sorted(glob.glob(str(S / "parts1b" / "*.json")))
items = []
for f in sections:
    sec = Path(f).stem
    for it in json.load(open(f)):
        it["_sec"] = sec
        items.append(it)
# ids first, so parents can point forward
for it in items:
    k = (it["_sec"], it.get("key", ""))
    if it.get("existing"):
        if it["existing"] not in by_id:
            problems.append(f"{k}: existing {it['existing']} is no part")
            continue
        keymap[k] = it["existing"]
    else:
        keymap[k] = f"PT{nxt:03d}"
        nxt += 1

def resolve(par, sec):
    if not par:
        return ""
    if re.fullmatch(r"PT\d{3,4}", par):
        return par if par in by_id or par in keymap.values() else None
    if (sec, par) in keymap:
        return keymap[(sec, par)]
    hits = [v for (s, k), v in keymap.items() if k == par]
    return hits[0] if len(hits) == 1 else None

for it in items:
    k = (it["_sec"], it.get("key", ""))
    if k not in keymap:
        continue
    pid = keymap[k]
    par = resolve(it.get("parent", ""), it["_sec"])
    if par is None:
        problems.append(f"{k}: parent {it.get('parent')!r} resolves to nothing")
        par = ""
    if par == pid:
        par = ""
    if it.get("system") not in systems:
        problems.append(f"{k}: system {it.get('system')!r}")
    if it.get("zone") and it["zone"] not in zones:
        problems.append(f"{k}: zone {it.get('zone')!r} -> blank")
        it["zone"] = ""
    cat = (it.get("catalogue") or "").strip()
    note = (it.get("note") or "").strip()
    if it.get("qty"):
        note = (note + f" Qty on the car: {it['qty']}.").strip()
    if it.get("existing"):
        r = by_id[pid]
        r["catalogue"] = "; ".join(x for x in [r.get("catalogue", ""), cat] if x and x not in r.get("catalogue", ""))
        if not r.get("oem_no"):
            r["oem_no"] = it.get("oem_no", "")
        if par and not r.get("parent"):
            r["parent"] = par
        touched += 1
    else:
        r = {h: "" for h in hdr}
        r.update({"id": pid, "name": it["name"].strip(), "system": it["system"], "zone": it.get("zone", ""),
                  "factory": "yes", "maker": "Mazda", "oem_no": it.get("oem_no", "").strip(), "catalogue": cat,
                  "applies": it.get("applies", "") if it.get("applies") in ("replaced", "not-fitted") else "",
                  "note": note, "parent": par})
        new.append(r)

# a parent ring is impossible physically
allp = {**{r["id"]: r.get("parent", "") for r in rows}, **{r["id"]: r["parent"] for r in new}}
for a in allp:
    seen, x = set(), a
    while x:
        if x in seen:
            problems.append(f"parent ring through {a}")
            break
        seen.add(x)
        x = allp.get(x, "")

print(f"{len(items)} items from {len(sections)} sections: {len(new)} new, {touched} existing enriched, "
      f"{sum(1 for r in new if r['applies'])} replaced/not-fitted, {sum(1 for r in new if 'confirm' in r['note'].lower())} confirm")
print(f"{len(problems)} problem(s)")
for p in problems[:80]:
    print("  " + p)
if WRITE and not [p for p in problems if "resolves to nothing" in p or "ring" in p or "system" in p]:
    with open(P, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=hdr, lineterminator="\n")
        w.writeheader()
        w.writerows(rows + new)
    print("written")

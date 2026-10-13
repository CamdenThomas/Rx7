#!/usr/bin/env python3
"""coverage.py - what exists for every part of the car, derived (05-cad A01, R2 of CLAUDE.md).

Reads 00-CAR parts and specs, 00-CAR cad and 05-cad blend, and sorts the 975 parts into tiers:
  file     parts.cad names a model file in the tree
  placed   parts.model_at_mm puts it in the combined model (05-cad blend, D-418 / D-421)
  dim      a specs row for the part in mm or in - a factory dimension to build or check it from
  found    a 00-CAR cad row (fits exact or close) whose subject or title carries the part's
           name words - a HINT only: the match is by words, nobody has opened the file against the part
  figure   parts.catalogue names a figure in the 1981-83 parts catalogue (S-005): shape, not size
  nothing  none of file, placed, dim or figure
A part is counted in every tier it reaches. Nothing is typed back into any table: run it again and
the numbers follow the record. Exit 0.

    env DEVELOPER_DIR=/Library/Developer/CommandLineTools python3 02-PROJECTS/05-cad/model/coverage.py [--list TIER] [--system SYSTEM]
"""
import argparse
import collections
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DIM_UNITS = {"mm", "in", "inch", "cm", "m", "mm (in)", "in (mm)", "deg", "°"}
STOP = {"assembly", "bracket", "switch", "front", "rear", "left", "right", "upper", "lower", "inner",
        "outer", "cover", "plate", "with", "unit", "pipe", "hose", "bolt", "nuts", "screw"}


def rows(rel):
    with open(ROOT / rel, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def coverage():
    parts = rows("00-CAR/data/parts.csv")
    specs = rows("00-CAR/data/specs.csv")
    cad = rows("00-CAR/data/cad.csv")
    dim_parts = {s["part"] for s in specs if s.get("part") and (s.get("unit") or "").strip().lower() in DIM_UNITS}
    subjects = [((c.get("subject") or "") + " " + (c.get("title") or "")).lower()
                for c in cad if c.get("fits") in ("exact", "close")]
    out = []
    for p in parts:
        words = [w for w in re.findall(r"[a-z]{4,}", (p.get("name") or "").lower()) if w not in STOP][:2]
        tiers = set()
        if (p.get("cad") or "").strip():
            tiers.add("file")
        if (p.get("model_at_mm") or "").strip():
            tiers.add("placed")
        if p["id"] in dim_parts:
            tiers.add("dim")
        if words and any(all(w in s for w in words) for s in subjects):
            tiers.add("found")
        if (p.get("catalogue") or "").strip():
            tiers.add("figure")
        if not tiers & {"file", "placed", "dim", "figure"}:
            tiers.add("nothing")
        out.append((p, tiers))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", metavar="TIER", help="list the parts in one tier")
    ap.add_argument("--system", help="only this 00-CAR system")
    a = ap.parse_args()
    cov = [(p, t) for p, t in coverage() if not a.system or p.get("system") == a.system]
    if a.list:
        for p, t in cov:
            if a.list in t:
                print(f"{p['id']}\t{p.get('system','')}\t{p['name']}")
        return 0
    n = collections.Counter()
    by_sys = collections.defaultdict(collections.Counter)
    for p, t in cov:
        n["parts"] += 1
        by_sys[p.get("system", "")]["parts"] += 1
        for tier in t:
            n[tier] += 1
            by_sys[p.get("system", "")][tier] += 1
    print(f"parts {n['parts']}: file {n['file']} · placed {n['placed']} · dim {n['dim']} · found (hint) {n['found']} · figure {n['figure']} · nothing {n['nothing']}")
    print("system                 parts  file placed  dim found figure nothing")
    for s, c in sorted(by_sys.items(), key=lambda kv: -kv[1]["parts"]):
        print(f"{s:22s} {c['parts']:5d} {c['file']:5d} {c['placed']:6d} {c['dim']:4d} {c['found']:5d} {c['figure']:6d} {c['nothing']:7d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

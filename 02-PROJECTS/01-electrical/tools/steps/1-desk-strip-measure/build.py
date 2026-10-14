# -*- coding: utf-8 -*-
"""Write briefs.csv and steps.csv for group 1 from the rows_*.py drafts, then validate them."""
import csv
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rows_a, rows_b, rows_c, rows_d, rows_e, rows_f  # noqa: E402

WANT = ("A5 V-002 W-330b W-330c R6 T-048 T-049 X-007 F-009 BT4 Y16 Y18 Y48 Y27 V-114 V-115 S1 C1 V-116 "
        "Q-014 Q-115 V-081 V-055 V-088 V-112 Z2").split()
PARTS_CSV = sys.argv[1] if len(sys.argv) > 1 else None

rows = {}
for mod in (rows_a, rows_b, rows_c, rows_d, rows_e, rows_f):
    for r in mod.ROWS:
        assert r["id"] not in rows, "duplicate " + r["id"]
        rows[r["id"]] = r

BH = ["id", "goal", "where", "time", "tools", "parts", "before", "know", "done_when", "if_not", "record"]
SH = ["id", "work", "n", "do", "how", "expect", "caution"]


def lines(v):
    return "\n".join(v) if isinstance(v, (list, tuple)) else v


briefs, steps = [], []
for wid in WANT:
    r = rows[wid]
    briefs.append({
        "id": wid, "goal": r["goal"], "where": r["where"], "time": r["time"],
        "tools": lines(r["tools"]), "parts": r["parts"], "before": lines(r["before"]),
        "know": lines(r["know"]), "done_when": r["done_when"], "if_not": r["if_not"],
        "record": r["record"],
    })
    for n, st in enumerate(r["steps"], 1):
        do, how, expect, caution = st
        steps.append({"id": "%s.%02d" % (wid, n), "work": wid, "n": n, "do": do, "how": how,
                      "expect": expect, "caution": caution})

for name, head, data in (("briefs.csv", BH, briefs), ("steps.csv", SH, steps)):
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=head, lineterminator="\n")
        w.writeheader()
        w.writerows(data)

# ---- validate, reading the files back ----
problems = []
B = list(csv.DictReader(open(os.path.join(HERE, "briefs.csv"), encoding="utf-8", newline="")))
S = list(csv.DictReader(open(os.path.join(HERE, "steps.csv"), encoding="utf-8", newline="")))
ids = [b["id"] for b in B]
if sorted(ids) != sorted(WANT):
    problems.append("brief ids differ from the list: %s" % (set(ids) ^ set(WANT)))
if len(ids) != len(set(ids)):
    problems.append("duplicate brief id")
parts_ok = None
if PARTS_CSV:
    parts_ok = {r["id"] for r in csv.DictReader(open(PARTS_CSV, encoding="utf-8", newline=""))}
for b in B:
    for col in ("goal", "done_when"):
        if not b[col].strip():
            problems.append("%s: empty %s" % (b["id"], col))
    for k, v in b.items():
        if "cad/" in v:
            problems.append("%s.%s contains cad/" % (b["id"], k))
    if parts_ok is not None:
        for p in b["parts"].split():
            if p not in parts_ok:
                problems.append("%s: part %s not in parts" % (b["id"], p))
    for ln in b["know"].split("\n"):
        if not ln.rstrip().endswith("]"):
            problems.append("%s: know line without a source: %s" % (b["id"], ln[:60]))
per = {}
for s in S:
    if s["work"] not in WANT:
        problems.append("step %s: work not in list" % s["id"])
    if not s["do"].strip():
        problems.append("step %s: empty do" % s["id"])
    for k, v in s.items():
        if "cad/" in v:
            problems.append("step %s.%s contains cad/" % (s["id"], k))
    per.setdefault(s["work"], []).append(s)
for wid in WANT:
    ss = per.get(wid, [])
    if not ss:
        problems.append("%s: no steps" % wid)
        continue
    ns = [int(s["n"]) for s in ss]
    if ns != list(range(1, len(ss) + 1)):
        problems.append("%s: n does not run 1..k" % wid)
    for s in ss:
        if s["id"] != "%s.%02d" % (wid, int(s["n"])):
            problems.append("step id mismatch %s" % s["id"])
    if not (3 <= len(ss) <= 25):
        problems.append("%s: %d steps" % (wid, len(ss)))
for name in ("briefs.csv", "steps.csv"):
    raw = open(os.path.join(HERE, name), "rb").read()
    if b"\r" in raw:
        problems.append(name + " has CR")
    raw.decode("utf-8")

counts = [len(per[w]) for w in WANT]
print("briefs", len(B), "steps", len(S))
print("steps per row: min %d median %s max %d" % (min(counts), statistics.median(counts), max(counts)))
print(" ".join("%s:%d" % (w, len(per[w])) for w in WANT))
print("know lines per row:", " ".join("%s:%d" % (b["id"], len(b["know"].split("\n"))) for b in B))
print("problems:", len(problems))
for p in problems:
    print("  -", p)
sys.exit(1 if problems else 0)

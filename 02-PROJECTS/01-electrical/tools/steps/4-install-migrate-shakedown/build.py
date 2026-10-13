"""Build and validate g4's briefs.csv and steps.csv."""
import csv, io, os, re, statistics, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402
import p1, p2, p3, p4, p5  # noqa: E402,F401

WANT = ["E24", "E25", "E26", "E27", "E28", "E29", "E30", "E2", "Q-110", "Q-028", "E36", "E37",
        "E38", "E39", "E40", "E41", "E35", "E31", "E32", "E33", "E34", "E48"]
BH = ["id", "goal", "where", "time", "tools", "parts", "before", "know", "done_when", "if_not", "record"]
SH = ["id", "work", "n", "do", "how", "expect", "caution"]

order = {w: i for i, w in enumerate(WANT)}
B = sorted(common.B, key=lambda r: order[r["id"]])
S = sorted(common.S, key=lambda r: (order[r["work"]], r["n"]))

for name, head, rows in (("briefs.csv", BH, B), ("steps.csv", SH, S)):
    with io.open(os.path.join(HERE, name), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(head)
        for r in rows:
            w.writerow([r[h] for h in head])

# ---- validate from the files as written
errs = []
with io.open(os.path.join(HERE, "briefs.csv"), encoding="utf-8", newline="") as f:
    br = list(csv.DictReader(f))
with io.open(os.path.join(HERE, "steps.csv"), encoding="utf-8", newline="") as f:
    st = list(csv.DictReader(f))
ids = [r["id"] for r in br]
if sorted(ids) != sorted(WANT):
    errs.append("brief ids differ: missing %s extra %s" % (set(WANT) - set(ids), set(ids) - set(WANT)))
if len(ids) != len(set(ids)):
    errs.append("duplicate brief id")
for r in br:
    for k in ("goal", "done_when"):
        if not r[k].strip():
            errs.append("%s empty %s" % (r["id"], k))
    for line in r["know"].split("\n"):
        if not re.search(r"\[[^\]]+\]$", line.strip()):
            errs.append("%s know line without a source: %s" % (r["id"], line[:60]))
    n = len(r["know"].split("\n"))
    if not 4 <= n <= 14:
        errs.append("%s know has %d lines" % (r["id"], n))
by = {}
for r in st:
    if r["work"] not in WANT:
        errs.append("step for unknown work %s" % r["work"])
    if not r["do"].strip():
        errs.append("%s empty do" % r["id"])
    by.setdefault(r["work"], []).append(r)
for w_ in WANT:
    rows = by.get(w_, [])
    if not rows:
        errs.append("%s has no steps" % w_)
    ns = [int(r["n"]) for r in rows]
    if ns != list(range(1, len(ns) + 1)):
        errs.append("%s n not 1..k: %s" % (w_, ns))
    for r in rows:
        if r["id"] != "%s.%02d" % (w_, int(r["n"])):
            errs.append("bad step id %s" % r["id"])
sid = [r["id"] for r in st]
if len(sid) != len(set(sid)):
    errs.append("duplicate step id")
for rows, name in ((br, "briefs"), (st, "steps")):
    for r in rows:
        for k, v in r.items():
            if "cad/" in v:
                errs.append("%s %s.%s contains cad/" % (name, r["id"], k))
            if "\r" in v:
                errs.append("%s %s.%s has CR" % (name, r["id"], k))
used = sorted({p for r in br for p in r["parts"].split()})
if used:
    q = "select id from parts where id in (%s)" % ",".join("'%s'" % p for p in used)
    out = subprocess.run(["python3", "tools/rx7.py", "sql", "01-electrical", q], capture_output=True,
                         text=True, cwd=os.path.dirname(os.path.abspath(__file__)).split('/02-PROJECTS/')[0],
                         env=dict(os.environ, DEVELOPER_DIR="/Library/Developer/CommandLineTools"))
    have = set(re.findall(r"^(P\d+)\s*$", out.stdout, re.M))
    miss = [p for p in used if p not in have]
    if miss:
        errs.append("parts not in 01-electrical parts: %s (rc %s)" % (miss, out.returncode))
counts = [len(by[w_]) for w_ in WANT]
print("briefs", len(br), "steps", len(st))
print("steps per row:", dict(zip(WANT, counts)))
print("min / median / max:", min(counts), statistics.median(counts), max(counts))
print("parts used:", len(used))
print("ERRORS:" if errs else "VALID")
for e in errs:
    print(" -", e)
sys.exit(1 if errs else 0)

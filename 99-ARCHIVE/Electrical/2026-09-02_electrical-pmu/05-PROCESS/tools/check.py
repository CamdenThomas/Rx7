#!/usr/bin/env python3
"""
check.py — the drift checker. Run it before "give me the diff".

    python check.py            report every finding, exit 1 if any
    python check.py --fix      (nothing is auto-fixed; the flag is reserved)

What it checks, and the audit item each rule exists because of:

    H1  every .md has a `*Rev YYYY-MM-DD …*` header in its first 6 lines     (I-132 / R5)
    H2  exactly one H1 heading per file                                       (I-135)
    H3  files over 200 lines carry a `## Contents` section                    (I-136)
    C1  no chat-export citation markup (outside 99-ARCHIVE)                    (I-133)
    C2  no three-digit "Checklist NNN" / "step NNN" citations                 (I-106)
    C3  no `legs/` paths                                                      (I-107)
    C4  every relative Markdown link resolves                                 (I-108)
    C5  a closed Q/V/A/T/I ID is never cited bare — write `Q-038 → D-095`     (I-104)
    F1  the three can_map.h copies are byte-identical; icu/ is the master     (I-154)
    F2  gen.py --check and registry.py --check are clean                      (I-144 / I-145)

Exempt from C2/C3/C5: DECISIONS.md (append-only history), OEM-RECORD.md
(frozen), 99-ARCHIVE, AUDITS.md, CHANGELOG.md and the registry itself.
"""
import os, re, sys, json, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(PROJ, "..", ".."))
findings = []

def rel(p): return os.path.relpath(p, ROOT).replace(os.sep, "/")
def note(rule, path, msg, line=None):
    findings.append(f"{rule:3} {rel(path)}{':' + str(line) if line else ''} — {msg}")

md = []
for dp, dn, fn in os.walk(ROOT):
    if any(s in dp for s in (".git", ".idea", "node_modules")): continue
    for f in fn:
        if f.endswith(".md"): md.append(os.path.join(dp, f))
md.sort()

ARCHIVE = lambda p: "99-ARCHIVE" in p
HISTORY = lambda p: (p.endswith("DECISIONS.md") or p.endswith("OEM-RECORD.md") or p.endswith("AUDITS.md")
                     or p.endswith("CHANGELOG.md") or p.endswith("ID-REGISTRY.md") or ARCHIVE(p))

ids_path = os.path.join(HERE, "ids.json")
ids = json.load(open(ids_path, encoding="utf-8")) if os.path.exists(ids_path) else {}
CLOSED_WORDS = re.compile(r"(→|->|closes|closed|CLOSED|answered|resolved|RESOLVED|decided|confirmed|CONFIRMED|moot|superseded|cancelled|CANCELLED|done|DONE|absorbed|dropped|withdrawn|by D-|by L-|see D-|see T-)")

for p in md:
    txt = open(p, encoding="utf-8", errors="replace").read()
    lines = txt.split("\n")
    head = "\n".join(lines[:6])
    if not ARCHIVE(p):
        if not re.search(r"\*Rev \d{4}-\d{2}-\d{2}", head):
            note("H1", p, "no `*Rev YYYY-MM-DD …*` header in the first 6 lines")
        h1 = [i + 1 for i, l in enumerate(lines) if l.startswith("# ")]
        if len(h1) != 1:
            note("H2", p, f"{len(h1)} H1 headings (lines {h1})")
        if len(lines) > 200 and "## Contents" not in txt and not p.endswith("PIN-MAP.md") and not p.endswith("ID-REGISTRY.md") and not p.endswith("CAVITY-STATE.md"):
            note("H3", p, f"{len(lines)} lines and no `## Contents` section")
    if not ARCHIVE(p):
        for i, l in enumerate(lines, 1):
            if "(cite index=" in l or "<cite index=" in l:
                note("C1", p, "chat-export citation markup", i)
    if not HISTORY(p):
        for i, l in enumerate(lines, 1):
            if re.search(r"(?i)\b(?:checklist|step)s?\s+\d{3}\b", l):
                note("C2", p, "old three-digit checklist numbering", i)
            if re.search(r"(?<![\w/])legs/", l):
                note("C3", p, "`legs/` path — the folder is 02-HARNESS", i)
    # C4 links
    d = os.path.dirname(p)
    for i, l in enumerate(lines, 1):
        for m in re.finditer(r"\]\(([^)]+)\)", l):
            target = m.group(1).split("#")[0].strip()
            if not target or target.startswith(("http", "mailto:", "computer://")): continue
            if target.lower().endswith((".pdf", ".step", ".stp")): continue   # large binaries may be LFS pointers or unsynced
            if not os.path.exists(os.path.normpath(os.path.join(d, target.replace("%20", " ")))):
                note("C4", p, f"link target does not exist: {target}", i)
    # C5 bare closed IDs
    if not HISTORY(p) and not p.endswith("OPEN.md") and not p.endswith("TASKS-CAMDEN.md") and not p.endswith("TASKS.md"):
        for i, l in enumerate(lines, 1):
            for m in re.finditer(r"\b([QVAT]-\d{3}|I-\d{2,3})\b", l):
                idd = m.group(1)
                st = ids.get(idd)
                if not st or st in ("open",): continue
                after = l[m.end(): m.end() + 45]
                before = l[max(0, m.start() - 25): m.start()]
                if CLOSED_WORDS.search(after) or CLOSED_WORDS.search(before): continue
                note("C5", p, f"{idd} is {st} but cited as if live — write `{idd} → …`", i)

# F1 can_map copies
fw = os.path.join(PROJ, "03-MODULES", "firmware")
copies = [os.path.join(fw, x, "can_map.h") for x in ("icu", "can_map_test", "can_loopback_test")]
sums = {c: hashlib.md5(open(c, "rb").read()).hexdigest() for c in copies if os.path.exists(c)}
if len(set(sums.values())) > 1:
    note("F1", copies[0], "can_map.h copies differ — copy icu/can_map.h over the test sketches")

# F2 generated outputs current
for tool in ("gen.py", "registry.py"):
    r = subprocess.run([sys.executable, os.path.join(HERE, tool), "--check"], capture_output=True, text=True)
    if r.returncode != 0:
        note("F2", os.path.join(HERE, tool), r.stdout.strip() or r.stderr.strip())

if findings:
    print(f"{len(findings)} finding(s):")
    for f in findings: print("  " + f)
    sys.exit(1)
print("check.py: clean")

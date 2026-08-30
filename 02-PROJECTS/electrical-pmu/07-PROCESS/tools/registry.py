#!/usr/bin/env python3
"""
registry.py — build 07-PROCESS/ID-REGISTRY.md and tools/ids.json from the files.

One row per permanent ID, with its status and where it lives:

    D-###  DECISIONS.md            active / SUPERSEDED BY D-###
    L-###  lighting-body/DECISIONS active
    Q-###  A-###  V-###            open (OPEN.md) / closed by D-### / closed (no decision cited)
    T-###  TASKS-CAMDEN.md, lighting-body/TASKS.md   open / done / cancelled / moved
    K-###  M-###  P-###            00-CAR
    I-###  AUDITS.md               open / done
    R#     ASSISTANT.md            standing rule

IDs are permanent and never reused (D-043). Nothing here is typed by hand:
run this after any edit to the files above.  check.py uses ids.json to flag a
closed ID cited as if it were open.
"""
import os, re, json, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(PROJ, "..", ".."))
CHECK = "--check" in sys.argv

def rd(rel):
    p = os.path.join(ROOT, rel)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""

DEC = rd("02-PROJECTS/electrical-pmu/07-PROCESS/DECISIONS.md")
LDEC = rd("02-PROJECTS/lighting-body/DECISIONS.md")
OPEN = rd("02-PROJECTS/electrical-pmu/07-PROCESS/OPEN.md")
LOPEN = rd("02-PROJECTS/lighting-body/OPEN.md")
TASKS = rd("02-PROJECTS/electrical-pmu/07-PROCESS/TASKS-CAMDEN.md")
LTASKS = rd("02-PROJECTS/lighting-body/TASKS.md")
KNOWN = rd("00-CAR/known-issues.md")
MODS = rd("00-CAR/modifications.md")
AUDITS = rd("02-PROJECTS/electrical-pmu/07-PROCESS/AUDITS.md")
ASSIST = rd("ASSISTANT.md")

reg = collections.OrderedDict()   # id -> dict(status, title, where, ref)

def first_line(text, n=110):
    t = re.sub(r"\s+", " ", text).strip(" —-*")
    return (t[:n] + "…") if len(t) > n else t

# ---- decisions
def parse_decisions(text, where, prefix):
    entries = list(re.finditer(rf"^\*\*({prefix}-\d{{3}})\*\*\s*—\s*(.*)$", text, re.M))
    for i, m in enumerate(entries):
        start = m.end()
        end = entries[i + 1].start() if i + 1 < len(entries) else len(text)
        body = text[start:end]
        sup = re.search(r"^>\s*SUPERSEDED BY ([DL]-\d{3})", body, re.M)
        status = f"superseded by {sup.group(1)}" if sup else "active"
        reg[m.group(1)] = dict(status=status, title=first_line(m.group(2)), where=where)
parse_decisions(DEC, "07-PROCESS/DECISIONS.md", "D")
parse_decisions(LDEC, "lighting-body/DECISIONS.md", "L")

# which decision closes which Q/V/A — the decision entry that cites the ID in its first line or in a [ID ...] tag
closer = {}
for m in re.finditer(r"^\*\*(D-\d{3})\*\*\s*—\s*(.*)$", DEC, re.M):
    for q in re.findall(r"\b([QVA]-\d{3})\b", m.group(2)):
        closer.setdefault(q, m.group(1))
for m in re.finditer(r"^\*\*(L-\d{3})\*\*\s*—\s*(.*)$", LDEC, re.M):
    for q in re.findall(r"\b([QVA]-\d{3})\b", m.group(2)):
        closer.setdefault(q, m.group(1))
# also: a decision body that says "[Q-0xx closed]" / "closes V-0xx" / "V-0xx CONFIRMED"
for m in re.finditer(r"\b([QVA]-\d{3})\b[^.\n]{0,30}\b(closed|CLOSED|confirmed|CONFIRMED|answered|resolved|RESOLVED|moot)\b", DEC):
    q = m.group(1)
    if q not in closer:
        # find the enclosing decision
        pos = m.start()
        ds = [d for d in re.finditer(r"^\*\*(D-\d{3})\*\*", DEC, re.M) if d.start() < pos]
        if ds: closer[q] = ds[-1].group(1)
for m in re.finditer(r"\b(closes?|closing)\s+\[?([QVA]-\d{3})", DEC):
    q = m.group(2)
    if q not in closer:
        pos = m.start()
        ds = [d for d in re.finditer(r"^\*\*(D-\d{3})\*\*", DEC, re.M) if d.start() < pos]
        if ds: closer[q] = ds[-1].group(1)

# ---- open items
def open_ids(text):
    ids = set(re.findall(r"^##+\s+\*?\*?([QAV]-\d{3})", text, re.M))
    ids |= set(re.findall(r"^\|\s*\*?\*?([QAV]-\d{3})\*?\*?\s*\|", text, re.M))
    return ids
def open_title(text, idd):
    m = re.search(rf"^##+\s+\*?\*?{idd}\*?\*?\s*·\s*(.*)$", text, re.M)
    if m: return first_line(m.group(1))
    m = re.search(rf"^\|\s*\*?\*?{idd}\*?\*?\s*\|\s*(.*?)\s*\|", text, re.M)
    return first_line(m.group(1)) if m else ""
open_e, open_l = open_ids(OPEN), open_ids(LOPEN)
# every Q/V/A ever mentioned anywhere in the tree
all_ids = set()
for dp, dn, fn in os.walk(ROOT):
    if any(s in dp for s in (".git", ".idea", "99-ARCHIVE")): continue
    for f in fn:
        if f.endswith(".md"):
            all_ids |= set(re.findall(r"\b([QAV]-\d{3})\b", open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()))
for idd in sorted(all_ids):
    if idd in open_e:
        reg[idd] = dict(status="open", title=open_title(OPEN, idd), where="07-PROCESS/OPEN.md")
    elif idd in open_l:
        reg[idd] = dict(status="open", title=open_title(LOPEN, idd), where="lighting-body/OPEN.md")
    elif idd in closer:
        reg[idd] = dict(status=f"closed by {closer[idd]}", title=reg.get(closer[idd], {}).get("title", ""), where="07-PROCESS/DECISIONS.md")
    else:
        reg[idd] = dict(status="closed (no decision cites it)", title="", where="—")

# ---- tasks
def parse_tasks(text, where):
    for m in re.finditer(r"^\|\s*(~~)?\*?\*?(T-\d{3})\*?\*?(~~)?\s*\|\s*(.*?)\s*\|", text, re.M):
        idd, struck, title = m.group(2), bool(m.group(1) or m.group(3)), m.group(4)
        title = re.sub(r"~~|\*\*", "", title)
        line = text[text.rfind("\n", 0, m.start()) + 1: text.find("\n", m.end())]
        status = "done"
        if not struck: status = "open"
        if re.search(r"CANCELLED", line): status = "cancelled"
        if re.search(r"moved to", line, re.I): status = "moved to lighting-body"
        if idd in reg and reg[idd]["status"] in ("done", "cancelled") and status == "open":
            continue  # a done row elsewhere wins over a later open mention
        reg[idd] = dict(status=status, title=first_line(title, 90), where=where)
parse_tasks(TASKS, "07-PROCESS/TASKS-CAMDEN.md")
parse_tasks(LTASKS, "lighting-body/TASKS.md")

# ---- car-level
for m in re.finditer(r"^\|\s*\*?\*?(K-\d{3})\*?\*?\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", KNOWN, re.M):
    reg[m.group(1)] = dict(status=first_line(re.sub(r"\*\*", "", m.group(3)), 60), title=first_line(re.sub(r"\*\*", "", m.group(2)), 90), where="00-CAR/known-issues.md")
for m in re.finditer(r"^\|\s*([MP]-\d{3})\s*\|(.*)$", MODS, re.M):
    cells = [c.strip() for c in m.group(2).split("|")]
    reg[m.group(1)] = dict(status="done" if m.group(1).startswith("M") else "planned", title=first_line(" · ".join(c for c in cells[:3] if c), 90), where="00-CAR/modifications.md")

# ---- audit items
for m in re.finditer(r"^- \[( |x)\]\s+\*\*(I-\d{2,3})\s*·\s*(?:P\d\s*·\s*)?(.*?)\*\*", AUDITS, re.M):
    reg[m.group(2)] = dict(status="done" if m.group(1) == "x" else "open", title=first_line(m.group(3), 90), where="07-PROCESS/AUDITS.md")

# ---- rules
for m in re.finditer(r"^\*\*(R\d)\s*·\s*(.*?)\*\*", ASSIST, re.M):
    reg[m.group(1)] = dict(status="standing", title=first_line(m.group(2), 90), where="ASSISTANT.md")

# ---- write
def keyf(k):
    m = re.match(r"([A-Z]+)-?(\d+)", k)
    return (m.group(1), int(m.group(2)))
ordered = sorted(reg.items(), key=lambda kv: keyf(kv[0]))
groups = collections.OrderedDict()
for k, v in ordered:
    groups.setdefault(keyf(k)[0], []).append((k, v))
names = {"D": "Decisions", "L": "Lighting-body decisions", "Q": "Questions", "A": "Assumptions", "V": "Verify items",
         "T": "Camden's tasks", "K": "Known issues", "M": "Modifications", "P": "Planned modifications", "I": "Improvement items (audits)", "R": "Standing rules"}
L = ["# ID REGISTRY — every permanent ID and its status", "",
     "*Rev 2026-08-30 · owns: nothing — a generated view. Run `tools/registry.py` after editing DECISIONS, OPEN, TASKS, known-issues, modifications or AUDITS.*", "",
     "IDs are permanent and never reused (D-043); a gap means something closed. **Cite a closed ID with its closer** — `Q-038 → D-095`, never bare `Q-038` — and `check.py` will stay quiet.", "",
     "| Prefix | Total | Open / active |", "|---|---|---|"]
for g, rows in groups.items():
    openish = sum(1 for k, v in rows if v["status"] in ("open", "active", "standing", "planned"))
    L.append(f"| {g} — {names.get(g, g)} | {len(rows)} | {openish} |")
for g, rows in groups.items():
    L += ["", f"## {g} — {names.get(g, g)}", "", "| ID | Status | What | Lives in |", "|---|---|---|---|"]
    for k, v in rows:
        L.append(f"| {k} | {v['status']} | {v['title']} | {v['where']} |")
out = "\n".join(L) + "\n"
target = os.path.join(PROJ, "07-PROCESS", "ID-REGISTRY.md")
jtarget = os.path.join(HERE, "ids.json")
old = open(target, encoding="utf-8").read() if os.path.exists(target) else None
jnew = json.dumps({k: v["status"] for k, v in ordered}, indent=0, ensure_ascii=False)
jold = open(jtarget, encoding="utf-8").read() if os.path.exists(jtarget) else None
if CHECK:
    if old != out or jold != jnew:
        print("registry.py --check: ID-REGISTRY.md is out of date — run registry.py")
        sys.exit(1)
    print("registry.py --check: registry is current")
else:
    open(target, "w", encoding="utf-8", newline="\n").write(out)
    open(jtarget, "w", encoding="utf-8", newline="\n").write(jnew)
    print(f"registry.py: {len(reg)} IDs → 07-PROCESS/ID-REGISTRY.md")

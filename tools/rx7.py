#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rx7.py - the only tool in this tree. Standard library only.

THE RECORD IS CSV, AND IT DESCRIBES ITSELF.
Every area (00-CAR, 01-REFERENCE, each project under 02-PROJECTS) keeps its
facts in <area>/data/*.csv. Two of those tables declare all the others:

    data/_tables.csv   table,purpose
    data/_schema.csv   table,column,type,required,ref,note

Both are ordinary tables, so the description of the record is checked by the
same code that checks the record. A table that exists but is not declared, a
declared table with no file, an undeclared column, a missing column, a bad
type, a duplicate key, a reference to a row that is not there - each is a
refusal naming the exact row.

NO COUNTERS ARE EVER STORED. The next D- is max(decisions.id)+1; the next
block in a project is the highest <prefix>.<n> that project has ever used, +1.
A stored counter can disagree with reality; a derived one cannot.

EXIT CODES ARE THE ONLY SIGNAL A CALLER MAY BRANCH ON:
    0  valid / done
    1  invalid - the record contradicts itself. The ONLY code that blocks a commit.
    2  nothing to do, or something is waiting on a person. Advisory. Blocks nothing.
Never branch on this tool's words, and never grep its output. If a caller needs
a machine-readable fact it does not have, add a command or a column.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import os
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOCKS_MD = ROOT / "BLOCKS.md"

# 3 is a usage error or a crash in this tool: never "the record contradicts itself" (§1),
# so a hook that blocks only on 1 cannot be tripped by a typo or a missing interpreter.
RC_OK, RC_INVALID, RC_WAITING, RC_USAGE = 0, 1, 2, 3

PHASES = ("PERMANENT", "PROPOSED", "PLANNING", "SOURCING", "BUILDING", "COMPLETE")
# `inherited` is a decision this project reads but another project owns.
DEC_STATUS = ("standing", "superseded", "withdrawn", "inherited")
WORK_STATE = ("open", "done", "blocked", "dropped")
WORK_OWNER = ("agent", "camden")

# Columns whose vocabulary THIS TOOL owns, not the project. Every area's _schema.csv must
# declare exactly these, so the same column cannot mean different things in two projects.
# (Inferring them per project from the values that happened to exist produced four false
# refusals on 2026-09-11 - `blocked` work, a `standing` 02-engine decision. R7.)
VOCAB = {
    ("decisions", "status"): "enum(" + "|".join(sorted(DEC_STATUS)) + ")",
    ("work", "state"): "enum(" + "|".join(sorted(WORK_STATE)) + ")",
    ("work", "owner"): "enum(" + "|".join(sorted(WORK_OWNER)) + ")",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
ID_RE = re.compile(r"^[A-Z]{1,4}-\d{1,4}$")
# Blocks are numbered per project, <prefix>.<n>: `00.01` is the first block ever raised
# for 02-PROJECTS/00-electrical, `01.07` the seventh for 01-luxury (D-356). The prefix is
# the project directory's two-digit number; 00-CAR and 01-REFERENCE would collide with
# 00 and 01, so theirs are CAR and REF. The number has at least two digits, so no id is
# shorter than `00.01` — but a bare `13.80` in prose is a voltage, so a block id is only
# recognised where it is structure: a BLOCKS.md heading, `closes`, a gate. Never in prose.
# Blocks were BLK-### until 2026-09-21; each old id is a `retired` row in its project.
BLOCK_ID_RE = re.compile(r"^(\d{2}|CAR|REF)\.(\d{2,3})$")
BLOCK_PREFIX_FIXED = {"00-CAR": "CAR", "01-REFERENCE": "REF"}
# Prose cites are checked by `rx7.py cites` (advisory), never by `check`. D- only, three
# digits only, because this car's factory diagrams use D-01 and B-12 as component codes.
CITE_RE = re.compile(r"\b(D-\d{3})\b")
_BID = r"(?:\d{2}|CAR|REF)\.\d{2,3}"
_CLOSER = rf"(?:D-\d{{3}}|{_BID})"
# The title may contain → (the house cite style); only a trailing `→ D-###` list is a closer.
BLOCK_HEAD_RE = re.compile(
    rf"^###\s+({_BID})(?![\w.])\s*(?:[·:\-–—]\s*(.*?))?"
    rf"\s*(?:→\s*({_CLOSER}(?:\s*,\s*{_CLOSER})*))?\s*$"
)
SOLVE_RE = re.compile(r"^\*{0,2}\s*solve\s*\*{0,2}\s*:\s*\*{0,2}\s*(.*)$|^\*\*solve\*\*\s*(.*)$", re.I)
# `## 00 · Electrical` — one header per project; every block sits under its own.
GROUP_HEAD_RE = re.compile(r"^##\s+(\d{2}|CAR|REF)\b")
FIELD_RE = re.compile(r"^\*\*([A-Za-z]+):?\*\*\s*(.*)$")

BLOCK_FIELDS = ("Ask", "Why", "Options", "Recommend", "Stops")


def today() -> str:
    return datetime.date.today().isoformat()


def rel(p: Path) -> str:
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


# --------------------------------------------------------------------------- IO

def read_csv_rows(p: Path):
    if not p.exists():
        return [], []
    with p.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    if not rows:
        return [], []
    hdr = [c.strip() for c in rows[0]]
    body = []
    for r in rows[1:]:
        if not any((c or "").strip() for c in r):
            continue
        body.append(list(r) + [""] * (len(hdr) - len(r)))
    return hdr, body


def read_table(area: Path, table: str):
    hdr, body = read_csv_rows(area / "data" / f"{table}.csv")
    return hdr, [dict(zip(hdr, r)) for r in body]


def write_table(area: Path, table: str, hdr, dicts) -> None:
    p = area / "data" / f"{table}.csv"
    # A key the header does not have would be dropped without a word — which is exactly how
    # `log` wrote nothing but ids and dates from v3's first run to 2026-09-21. Refuse it.
    stray = sorted({k for d in dicts for k in d if k not in hdr})
    if stray:
        die(f"{rel(p)}: refusing to write columns the header does not have: {', '.join(stray)} "
            "(nothing was written)")
    tmp = p.with_name(p.name + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(hdr)
        for d in dicts:
            w.writerow([(d.get(c, "") or "") for c in hdr])
    tmp.replace(p)


def areas():
    out = []
    for p in sorted(ROOT.rglob("data/_tables.csv")):
        if "99-ARCHIVE" in p.parts or ".git" in p.parts:
            continue
        out.append(p.parent.parent)
    return out


def resolve_area(name: str | None):
    if not name:
        return None
    cand = ROOT / name
    if (cand / "data" / "_tables.csv").exists():
        return cand
    for a in areas():
        if a.name == name or rel(a) == name.replace("\\", "/"):
            return a
    die(f"no area named {name!r} - areas are: " + ", ".join(rel(a) for a in areas()))


def die(msg: str, code: int = RC_USAGE):
    print(msg)
    sys.exit(code)


# ----------------------------------------------------------------------- schema

def schema(area: Path):
    _, trows = read_table(area, "_tables")
    _, srows = read_table(area, "_schema")
    tables = {r["table"]: r for r in trows if r.get("table")}
    cols: dict[str, list[dict]] = {}
    for r in srows:
        if r.get("table"):
            cols.setdefault(r["table"], []).append(r)
    return tables, cols


def key_column(spec) -> str | None:
    keys = [c["column"] for c in spec if c.get("type") == "key"]
    return keys[0] if len(keys) == 1 else None


def bad_value(typ: str, v: str):
    if typ in ("key", "str", "text", "list"):
        return None
    if typ == "int":
        try:
            int(v)
        except ValueError:
            return "is not an integer"
    elif typ == "num":
        try:
            float(v)
        except ValueError:
            return "is not a number"
    elif typ == "bool":
        if v not in ("yes", "no"):
            return "is not yes/no"
    elif typ == "date":
        if not DATE_RE.match(v):
            return "is not a date (YYYY-MM-DD or YYYY-MM)"
    elif typ == "id":
        if not ID_RE.match(v):
            return "is not an id (like D-123)"
    elif typ.startswith("enum(") and typ.endswith(")"):
        allowed = typ[5:-1].split("|")
        if v not in allowed:
            return "is not one of " + "/".join(allowed)
    else:
        return f"has an unknown declared type {typ!r}"
    return None


# ------------------------------------------------------------------------ blocks

def block_prefix(area: Path):
    """The block-id prefix an area owns: CAR, REF, or a project's two-digit number."""
    if area.name in BLOCK_PREFIX_FIXED:
        return BLOCK_PREFIX_FIXED[area.name]
    m = re.match(r"^(\d{2})-", area.name)
    return m.group(1) if m and area.parent.name == "02-PROJECTS" else None


def prefix_areas():
    """{prefix: area} — the only map from a block id to the project it belongs to."""
    return {p: a for a in areas() if (p := block_prefix(a))}


def group_title(area: Path) -> str:
    """`## 00 · Electrical` — the header a project's blocks sit under on the page."""
    name = re.sub(r"^\d{2}-", "", area.name).replace("-", " ")
    return f"## {block_prefix(area)} · {name[:1].upper() + name[1:].lower()}"


def read_blocks_text():
    """(text, is_utf8). A page saved by Notepad as ANSI or UTF-16 must still be READ — his
    answers are in it — but nothing may be WRITTEN back through a guessed decoding, or a
    character he typed is silently changed (R3). append_block refuses when is_utf8 is False."""
    raw = BLOCKS_MD.read_bytes()
    for enc in ("utf-8-sig",):
        try:
            return raw.decode(enc), True
        except UnicodeDecodeError:
            pass
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16"), False
    return raw.decode("cp1252", errors="replace"), False


# Problems that only mean "a block Claude is still writing" - they refuse a commit, but they
# must not stop `rx7.py block` from adding the next one in the same pass (§6.2 4d).
UNFINISHED = set()


def parse_blocks():
    """Return (blocks, problems). Never rewrites the file; refuses rather than guess.

    The page is one `## <prefix> · <Project>` header per project, each block under its
    own. There is no OPEN section heading: everything on the page is open."""
    if not BLOCKS_MD.exists():
        return [], []
    text, _ = read_blocks_text()
    lines = [l.rstrip("\r") for l in text.split("\n")]
    blocks, problems = [], []
    owners = prefix_areas()
    section, group, cur = "OPEN", None, None
    for ln, raw in enumerate(lines, start=1):
        s = raw.strip()
        # Inside an answer, only page structure ends it — a `## ` or a `### ` of his own is
        # part of what he wrote and must not be cut off (R3).
        structural = (GROUP_HEAD_RE.match(s) or s.upper() in ("## OPEN", "## SOLVED")
                      or BLOCK_HEAD_RE.match(s))
        # ...except a line that is plainly an attempt at a block heading (`### 00.7`, `### BLK-…`)
        # but does not parse: that is a block Claude wrote wrong, and swallowing it would hide it.
        idlike = re.match(r"^###\s+(BLK-|\d|CAR\b|REF\b)", s)
        if cur is not None and cur["in_solve"] and not structural and not idlike:
            cur["solve"].append(raw)
            continue
        if s.startswith("## "):
            head = s[3:].strip().upper()
            if head in ("OPEN", "SOLVED"):
                section = head
            g = GROUP_HEAD_RE.match(s)
            group = g.group(1) if g else None
            cur = None
            continue
        m = BLOCK_HEAD_RE.match(s)
        if not m and s.startswith("### "):
            # A heading that is not a block would otherwise be swallowed into the previous
            # block's text — or, worse, hide a new block entirely. Refuse it by name.
            problems.append(f"BLOCKS.md: line {ln} is a `###` heading that is not a block "
                            f"(`### <id> · <title>`, e.g. `### 00.19 · …`): {s[:70]!r}")
            cur = None
            continue
        if m:
            bid = m.group(1)
            prefix, num = BLOCK_ID_RE.match(bid).groups()
            area = owners.get(prefix)
            if area is None:
                problems.append(f"BLOCKS.md: {bid} (line {ln}) — no area owns the prefix {prefix!r}")
            elif group != prefix:
                problems.append(f"BLOCKS.md: {bid} (line {ln}) is not under its project's "
                                f"header `{group_title(area)}`")
            cur = {
                "id": bid,
                "prefix": prefix,
                "num": int(num),
                "area": area.name if area else "",
                "title": (m.group(2) or "").strip(),
                "closer": m.group(3) or "",
                "section": section,
                "line": ln,
                "fields": {},
                "solve": [],
                "in_solve": False,
            }
            blocks.append(cur)
            continue
        if cur is None:
            continue
        sv = SOLVE_RE.match(s)
        if sv:
            # `**SOLVE:**`, `SOLVE:`, `solve:` and `**Solve**:` all count: the marker is his
            # to type near, and a parser that is picky about it loses his answer (R3).
            cur["in_solve"] = True
            rest = sv.group(1) if sv.group(1) is not None else (sv.group(2) or "")
            if rest.strip():
                cur["solve"].append(rest)
            continue
        f = FIELD_RE.match(s)
        if f:
            cur["fields"][f.group(1)] = f.group(2)
            continue
        # continuation of the previous field (options lists, wrapped prose)
        if cur["fields"]:
            last = list(cur["fields"])[-1]
            cur["fields"][last] = (cur["fields"][last] + "\n" + raw).strip()

    for b in blocks:
        b["solution"] = "\n".join(b["solve"]).strip()
    seen = {}
    for b in blocks:
        if b["id"] in seen:
            problems.append(
                f"BLOCKS.md: {b['id']} appears twice (lines {seen[b['id']]} and {b['line']})"
            )
        else:
            seen[b["id"]] = b["line"]
        if b["section"] == "OPEN":
            # The five fields are the answerable-from-the-page bar, and they only matter
            # while the block is still waiting: once Camden has answered it, enumerating
            # the options he did not pick is busywork.
            if not b["solution"]:
                n0 = len(problems)
                for need in BLOCK_FIELDS:
                    if need not in b["fields"] or not b["fields"][need].strip():
                        problems.append(
                            f"BLOCKS.md: {b['id']} (line {b['line']}) is waiting with no **{need}** - "
                            "it cannot be answered from the page alone"
                        )
                    elif "TO WRITE" in b["fields"][need]:
                        problems.append(
                            f"BLOCKS.md: {b['id']} (line {b['line']}) has a placeholder in "
                            f"**{need}** - write it or delete the block"
                        )
                UNFINISHED.update(problems[n0:])
            if not b["in_solve"]:
                problems.append(
                    f"BLOCKS.md: {b['id']} (line {b['line']}) has no **SOLVE:** line - "
                    "Camden has nowhere to answer"
                )
        else:
            # There is no SOLVED section any more: an answered block is applied through the
            # record, becomes a decision whose `closes` names it, and is then deleted from
            # this page. DECISIONS.md is where a settled question lives. A block still
            # sitting under a SOLVED heading is therefore work that was never finished.
            problems.append(
                f"BLOCKS.md: {b['id']} (line {b['line']}) is under a SOLVED heading. That "
                "section no longer exists — apply the answer, write the decision with "
                "closes={id}, then delete the block from this page.".format(id=b["id"])
            )
    return blocks, problems


def _closes_tokens(path: Path):
    """Every token in the `closes` column of one decisions.csv."""
    hdr, body = read_csv_rows(path)
    if "closes" not in hdr:
        return []
    i = hdr.index("closes")
    return [t for row in body if len(row) > i for t in re.split(r"[\s,;·]+", row[i]) if t]


def next_block_id(blocks, prefix: str) -> str:
    """The highest number this project has ever used, plus one — derived, never stored (R5).

    A block is DELETED from BLOCKS.md once its answer is a decision, so the page alone no
    longer knows how high a project's numbering went: the decisions do, in `closes` —
    including the decisions of a project that has since been archived. Counting only the
    page would hand out 00.05 twice, and an id that means two things is the one mistake
    this record cannot recover from."""
    highest = max([b["num"] for b in blocks if b["prefix"] == prefix], default=0)
    files = [a / "data" / "decisions.csv" for a in areas()]
    files += list((ROOT / "99-ARCHIVE").rglob("decisions.csv"))
    toks = [t for f in files for t in _closes_tokens(f)]
    # A block withdrawn WITHOUT a decision (moot, merged) leaves no `closes`; its id goes
    # into `retired` as a term so the number is still never handed out again.
    for f in [a / "data" / "retired.csv" for a in areas()] + list((ROOT / "99-ARCHIVE").rglob("retired.csv")):
        hdr, body = read_csv_rows(f)
        if "term" in hdr:
            toks += [row[hdr.index("term")].strip() for row in body]
    for tok in toks:
        m = BLOCK_ID_RE.match(tok)
        if m and m.group(1) == prefix:
            highest = max(highest, int(m.group(2)))
    return f"{prefix}.{highest + 1:02d}"


def append_block(bid: str, area: Path, ask: str) -> None:
    """Insert a new block at the end of its project's group, adding the group header if
    the project has none yet. Every other byte of the page is left exactly as it was."""
    if BLOCKS_MD.exists():
        text, is_utf8 = read_blocks_text()
        if not is_utf8:
            die("BLOCKS.md is not saved as UTF-8 (Notepad 'ANSI' or 'Unicode'?). Nothing was "
                "written - re-save it as UTF-8 first, so no character Camden typed is changed.")
        lines = [l.rstrip("\r") for l in text.split("\n")]
    else:
        lines = ["# BLOCKS"]
    # The generated title must itself parse: no → (it would read as a closer) and no line break.
    title = re.sub(r"\s+", " ", ask.replace("→", "->")).strip()
    title = title if len(title) <= 60 else title[:60].rsplit(" ", 1)[0].rstrip(" -,;") + " …"
    entry = [
        f"### {bid} · {title}",
        f"**Ask** {ask}",
        f"**Opened** {today()}",
        "**Why** TO WRITE",
        "**Options** TO WRITE",
        "**Recommend** TO WRITE",
        "**Stops** TO WRITE",
        "**SOLVE:**",
    ]
    prefix = block_prefix(area)
    order = sorted(prefix_areas(), key=lambda p: (p.isdigit(), p))  # CAR, REF, 00, 01 …
    heads = [(i, GROUP_HEAD_RE.match(l.strip()).group(1)) for i, l in enumerate(lines)
             if GROUP_HEAD_RE.match(l.strip())]
    mine = [i for i, p in heads if p == prefix]
    if mine:
        # the group ends at the next `## ` of ANY kind, not only the next project header
        later = [i for i, l in enumerate(lines) if i > mine[0] and l.strip().startswith("## ")]
        at = later[0] if later else len(lines)
        new = entry
        # an empty project reads `*Nothing open.*` under its header — no longer true
        gone = [i for i in range(mine[0], at) if lines[i].strip() == "*Nothing open.*"]
        for i in reversed(gone):
            del lines[i]
        at -= len(gone)
    else:
        after = [i for i, p in heads if p in order and order.index(p) > order.index(prefix)]
        at = after[0] if after else len(lines)
        new = [group_title(area), ""] + entry
    while at > 0 and not lines[at - 1].strip():
        at -= 1
    # only BLANK lines at the insertion point are touched - never a line of text
    while at < len(lines) and not lines[at].strip():
        del lines[at]
    lines[at:at] = [""] + new + ([""] if at < len(lines) else [])
    out = "\n".join(lines).rstrip("\n") + "\n"
    tmp = BLOCKS_MD.with_name(BLOCKS_MD.name + ".tmp")
    tmp.write_text(out, encoding="utf-8", newline="\n")
    tmp.replace(BLOCKS_MD)
    # Prove it: the new block must parse back as itself, or the page is restored untouched.
    if not any(b["id"] == bid for b in parse_blocks()[0]):
        BLOCKS_MD.write_text(text if 'text' in locals() else "", encoding="utf-8", newline="\n")
        die(f"{bid} did not parse back after writing - BLOCKS.md restored, nothing added")


# ------------------------------------------------------------------------- gates
#
# `work.gate` holds REFERENCES, all of which must be met before the row can be started.
# Nothing else: prose belongs in `note`. The references, resolved across the whole tree:
#
#   D-274                 met when that decision is standing or inherited
#   01.07                 met when that block is gone from BLOCKS.md and a decision
#                         names it in `closes` — i.e. it has been answered and applied
#   A5                    met when that work row is done or dropped, in this area
#   01-luxury:F-012  the same, in another area (work ids are only unique per area)
#   phase:SOURCING        met when the owning area is at that phase or past it
#
# An empty gate is met. READY is every open row whose gate is met; that list is the only
# answer to "what can be started now", and §6.1 takes its work from it.
#
# Why this is code and not a convention: a gate that quietly never opens looks exactly
# like a finished project — the planner reports "nothing to do" and stops. Nothing else
# in the tree can tell those two apart, so the check has to (R7).

GATE_SPLIT = re.compile(r"[\s,;]+")
WORK_REF_RE = re.compile(r"^(?:(?P<area>[A-Za-z0-9_.-]+):)?(?P<id>[A-Za-z]{1,4}-?\d{1,4}[a-z]?)$")
PHASE_REF_RE = re.compile(r"^phase:(?P<phase>[A-Za-z]+)$")
GATE_DONE = ("done", "dropped")
GATE_LIVE_DEC = ("standing", "inherited")

_TREE = None


def tree_index(fresh: bool = False):
    """Every gate-addressable fact in the tree, read straight from the CSVs and BLOCKS.md.

    {"decisions": {id: status}, "blocks": {id: section}, "phase": {area: phase},
     "work": {(area, id): state}, "work_ids": {id: [area…]}, "row": {(area, id): row}}
    """
    global _TREE
    if _TREE is not None and not fresh:
        return _TREE
    idx = {"decisions": {}, "blocks": {}, "phase": {}, "work": {}, "work_ids": {}, "row": {}}
    for a in areas():
        name = a.name
        _, prow = read_table(a, "_project")
        kv = {(r.get("key") or "").strip(): (r.get("value") or "").strip() for r in prow}
        idx["phase"][name] = kv.get("phase", "")
        _, drows = read_table(a, "decisions")
        for r in drows:
            i = (r.get("id") or "").strip()
            st = (r.get("status") or "").strip()
            # The owner's row decides. An `inherited` copy in another area only fills in when
            # no owner row exists - it must never re-open a decision its owner superseded
            # (D-208 read `inherited` in luxury after electrical had superseded it).
            if i and (i not in idx["decisions"] or idx["decisions"][i] == "inherited"):
                idx["decisions"][i] = st
        _, wrows = read_table(a, "work")
        for r in wrows:
            i = (r.get("id") or "").strip()
            if not i:
                continue
            idx["work"][(name, i)] = (r.get("state") or "").strip()
            idx["work_ids"].setdefault(i, []).append(name)
            idx["row"][(name, i)] = r
    for b in parse_blocks()[0]:
        idx["blocks"][b["id"]] = b["section"]
    # A block leaves BLOCKS.md the moment its answer is a decision, so "was it answered?"
    # is not a section any more — it is whether a decision says it closed it. That is the
    # one home for the fact (R2), and it is why a gate on a removed block still resolves.
    # Only a STANDING (or inherited) decision closes a block (§4), and a project that has been
    # archived still closed what it closed.
    closed = set()
    for f in [a / "data" / "decisions.csv" for a in areas()] + list((ROOT / "99-ARCHIVE").rglob("decisions.csv")):
        hdr, _b = read_csv_rows(f)
        if "closes" not in hdr or "status" not in hdr:
            continue
        ci, si = hdr.index("closes"), hdr.index("status")
        for row in _b:
            if row[si].strip() in GATE_LIVE_DEC:
                closed |= {t for t in re.split(r"[\s,;·]+", row[ci]) if BLOCK_ID_RE.match(t)}
    idx["blocks_closed"] = closed
    _TREE = idx
    return idx


def parse_gate(cell: str):
    return [x for x in GATE_SPLIT.split((cell or "").strip()) if x]


def _resolve_work(ref_area, wid, area, idx):
    """Which area owns the work id this reference names — [] none, >1 ambiguous."""
    if ref_area:
        return sorted({x for x in idx["work_ids"].get(wid, []) if x == ref_area})
    if (area, wid) in idx["work"]:
        return [area]
    return sorted(set(idx["work_ids"].get(wid, [])))


def gate_ref_state(ref: str, area: str, idx=None):
    """(met, why). `why` starts with '?' when the reference resolves to nothing at all."""
    idx = idx or tree_index()
    m = PHASE_REF_RE.match(ref)
    if m:
        want = m.group("phase").upper()
        if want not in PHASES:
            return False, f"? unknown phase {want!r}"
        have = idx["phase"].get(area, "")
        if have not in PHASES:
            return False, f"? {area} has no phase to compare"
        return PHASES.index(have) >= PHASES.index(want), f"phase {want} (now {have or '-'})"
    if ref in idx["decisions"]:
        st = idx["decisions"][ref]
        if st in ("superseded", "withdrawn"):
            # It can never open, and silently waiting forever is the failure gates exist to
            # prevent: name its closer instead.
            return False, f"? {ref} is {st} - gate on the decision that replaced it"
        return st in GATE_LIVE_DEC, f"{ref} {st}"
    if ref in idx["blocks"]:
        return False, f"{ref} open"
    if ref in idx.get("blocks_closed", ()):
        return True, f"{ref} closed"
    if BLOCK_ID_RE.match(ref):
        return False, f"? {ref} is no block on BLOCKS.md and no decision closes it"
    m = WORK_REF_RE.match(ref)
    if m:
        wid = m.group("id")
        hits = _resolve_work(m.group("area"), wid, area, idx)
        if len(hits) > 1:
            return False, f"? {ref} is ambiguous ({', '.join(hits)}) — qualify it as <area>:{wid}"
        if hits and not m.group("area") and hits[0] != area:
            short = hits[0]
            return False, (f"? {ref} is a work row in {short}, not here - qualify it as "
                           f"{short}:{wid} (§1: always qualify across areas)")
        if hits:
            st = idx["work"].get((hits[0], wid), "")
            label = wid if hits[0] == area else f"{hits[0]}:{wid}"
            return st in GATE_DONE, f"{label} {st or 'unknown'}"
        if ref.startswith("D-"):
            return False, f"? {ref} is no decision in the tree"
        return False, f"? {ref} is no decision, block or work item in the tree"
    return False, (f"? {ref!r} is not a reference — a gate holds D-/BLK-/work ids and "
                   f"phase:<PHASE>, nothing else; prose belongs in `note`")


def gate_state(cell: str, area: str, idx=None):
    """(met, unmet_reasons, bad_refs) for a whole gate cell."""
    idx = idx or tree_index()
    unmet, bad = [], []
    for ref in parse_gate(cell):
        ok, why = gate_ref_state(ref, area, idx)
        if why.startswith("?"):
            bad.append(why[2:])
        elif not ok:
            unmet.append(why)
    return (not unmet and not bad), unmet, bad


def gate_cycles(idx=None):
    """Every dependency ring among work items, tree-wide, as readable chains."""
    idx = idx or tree_index()
    edges = {}
    for (ar, wid) in idx["work"]:
        outs = []
        for ref in parse_gate(idx["row"][(ar, wid)].get("gate", "")):
            if PHASE_REF_RE.match(ref) or ref in idx["decisions"] or ref in idx["blocks"]:
                continue
            m = WORK_REF_RE.match(ref)
            if not m:
                continue
            hits = _resolve_work(m.group("area"), m.group("id"), ar, idx)
            if len(hits) == 1:
                outs.append((hits[0], m.group("id")))
        edges[(ar, wid)] = outs
    colour, cycles = {}, []

    def walk(n, stack):
        colour[n] = 1
        for nxt in edges.get(n, ()):
            if colour.get(nxt) == 1:
                i = stack.index(nxt) if nxt in stack else 0
                cycles.append(" -> ".join(f"{x}:{y}" for x, y in stack[i:] + [nxt]))
            elif colour.get(nxt, 0) == 0:
                walk(nxt, stack + [nxt])
        colour[n] = 2

    for n in edges:
        if colour.get(n, 0) == 0:
            walk(n, [n])
    return sorted(set(cycles))


def ready_report(area: str, idx=None):
    """(ready, blocked) for one area's open work. Each entry is (id, row, [reasons])."""
    idx = idx or tree_index()
    ready, blocked = [], []
    for (ar, wid), st in idx["work"].items():
        if ar != area or st != "open":
            continue
        row = idx["row"][(ar, wid)]
        met, unmet, bad = gate_state(row.get("gate", ""), ar, idx)
        (ready if met else blocked).append((wid, row, unmet + bad))
    order = lambda t: (t[1].get("stage", ""), t[0])
    return sorted(ready, key=order), sorted(blocked, key=order)


def walled_off(area: str, idx=None):
    """'' unless this area has open work, none startable, and every blocker is its own.

    All-blocked on a BLOCK or on another area is a real state — it means something waits
    on Camden, which is exit code 2 and refuses nothing. All-blocked on your own rows or
    your own phase cannot be true, so it is a contradiction and refuses (exit 1).
    """
    idx = idx or tree_index()
    ready, blocked = ready_report(area, idx)
    if ready or not blocked:
        return ""
    for _, row, _ in blocked:
        for ref in parse_gate(row.get("gate", "")):
            if ref in idx["blocks"]:
                return ""
            m = WORK_REF_RE.match(ref)
            if m and ref not in idx["decisions"]:
                hits = _resolve_work(m.group("area"), m.group("id"), area, idx)
                if hits and hits[0] != area:
                    return ""
    return (f"{area}: all {len(blocked)} open work row(s) are gated on this area's own rows "
            f"or its own phase, so nothing here can ever start — a gate is wrong")


def check_gates(area: Path, idx=None) -> list[str]:
    """Gates are structure, so they are checked like structure (R7)."""
    if not (area / "data" / "work.csv").exists():
        return []
    idx = idx or tree_index()
    name = area.name
    p = []
    _, rows = read_table(area, "work")
    for r in rows:
        wid = (r.get("id") or "").strip()
        for bad in gate_state(r.get("gate", ""), name, idx)[2]:
            p.append(f"{rel(area)}:work:{wid}: gate — {bad}")
    for chain in gate_cycles(idx):
        if any(n.split(":", 1)[0] == name for n in chain.split(" -> ")):
            p.append(f"{rel(area)}:work: dependency ring {chain}")
    wall = walled_off(name, idx)
    if wall:
        p.append(f"{rel(area)}:work: {wall.split(': ', 1)[1]}")
    return p


# ------------------------------------------------------------------------ checks

def load_keys():
    """Global index: (area_name, table) -> set of key values."""
    idx = {}
    for a in areas():
        tables, cols = schema(a)
        for t in tables:
            spec = cols.get(t) or []
            kc = key_column(spec)
            if not kc:
                continue
            _, rows = read_table(a, t)
            idx[(a.name, t)] = {(r.get(kc) or "").strip() for r in rows}
    return idx


def check_area(area: Path, keyidx) -> list[str]:
    p: list[str] = []
    tables, cols = schema(area)
    if not tables:
        return [f"{rel(area)}: data/_tables.csv is missing or empty"]

    files = {f.stem for f in (area / "data").glob("*.csv") if not f.name.startswith("_")}
    for t in sorted(files - set(tables)):
        p.append(f"{rel(area)}: data/{t}.csv exists but {t!r} is not declared in _tables.csv")
    for t in sorted(set(tables) - files):
        p.append(f"{rel(area)}: _tables.csv declares {t!r} but data/{t}.csv does not exist")

    for t in sorted(files & set(tables)):
        spec = cols.get(t) or []
        if not spec:
            p.append(f"{rel(area)}:{t} has no columns declared in _schema.csv")
            continue
        kc = key_column(spec)
        if not kc:
            n = len([c for c in spec if c.get("type") == "key"])
            p.append(f"{rel(area)}:{t} declares {n} key columns in _schema.csv (want exactly 1)")
            continue
        for c in spec:
            canon = VOCAB.get((t, c["column"]))
            if canon and (c.get("type") or "") != canon:
                p.append(
                    f"{rel(area)}:_schema: {t}.{c['column']} is declared {c.get('type')!r} "
                    f"but this column's vocabulary belongs to the tool: it must be {canon}"
                )
        hdr, rows = read_table(area, t)
        want = {c["column"] for c in spec}
        have = set(hdr)
        for c in sorted(want - have):
            p.append(f"{rel(area)}:{t} is missing declared column {c!r}")
        for c in sorted(have - want):
            p.append(f"{rel(area)}:{t} has column {c!r}, which _schema.csv does not declare")

        seen = {}
        for i, r in enumerate(rows, start=2):
            k = (r.get(kc) or "").strip()
            if not k:
                p.append(f"{rel(area)}:{t} line {i}: the key column {kc!r} is empty")
                continue
            if k in seen:
                p.append(f"{rel(area)}:{t}: duplicate key {k!r} (lines {seen[k]} and {i})")
            else:
                seen[k] = i
            for c in spec:
                col, typ = c["column"], (c.get("type") or "str")
                if col not in r:
                    continue
                v = (r[col] or "").strip()
                if not v:
                    if (c.get("required") or "").lower() == "yes" and typ != "key":
                        p.append(f"{rel(area)}:{t}:{k}: {col} is required but empty")
                    continue
                why = bad_value(typ, v)
                if why:
                    p.append(f"{rel(area)}:{t}:{k}: {col}={v!r} {why}")
                target = (c.get("ref") or "").strip()
                if target:
                    toks = re.split(r"[\s,;|]+", v) if typ == "list" else [v]
                    for tok in [x for x in toks if x]:
                        if not ref_ok(area, target, tok, keyidx):
                            p.append(
                                f"{rel(area)}:{t}:{k}: {col}={tok!r} is not a key in {target}"
                            )
        # A row with more cells than its header loses them on the next write (read_table zips
        # to the header), so it is refused while the cells are still there to rescue.
        _raw_hdr, raw_body = read_csv_rows(area / "data" / f"{t}.csv")
        for i, raw in enumerate(raw_body, start=2):
            if len(raw) > len(_raw_hdr) and any(x.strip() for x in raw[len(_raw_hdr):]):
                p.append(f"{rel(area)}:{t} line {i}: {len(raw)} cells under a {len(_raw_hdr)}-column "
                         "header - the extra cells would be lost on the next write")
        if t in ("decisions", "log", "retired"):
            continue
        for r in rows:
            k = (r.get(kc) or "").strip()
            for col, v in r.items():
                v = v or ""
                # §6.6: 00-CAR states what IS, never how it was decided.
                if block_prefix(area) == "CAR":
                    for hit in re.findall(r"\b(?:D-\d{3}|BLK-\d{1,4})\b", v):
                        p.append(f"{rel(area)}:{t}:{k}: {col} cites {hit} - 00-CAR never cites a "
                                 "decision or a block (§6.6); say what the car is")
                # The cad/ fence: nothing in the record cites a drawing as evidence.
                if re.search(r"(?<![\w-])cad/", v):
                    p.append(f"{rel(area)}:{t}:{k}: {col} cites a file in cad/ - the record never "
                             "cites a drawing (cad/README.md); promote the fact into a row instead")
    p += check_decisions(area)
    p += check_phase(area)
    p += check_gates(area)
    return p


def ref_ok(area: Path, target: str, value: str, keyidx) -> bool:
    if ":" in target:
        aname, rest = target.split(":", 1)
    else:
        aname, rest = area.name, target
    tname = rest.split(".", 1)[0]
    keys = keyidx.get((aname, tname))
    if keys is None:
        return False
    return value in keys


def check_decisions(area: Path) -> list[str]:
    p = []
    ddir = area / "data" / "decisions"
    if not (area / "data" / "decisions.csv").exists():
        return p
    _, rows = read_table(area, "decisions")
    ids = set()
    for r in rows:
        i = (r.get("id") or "").strip()
        if not i:
            continue
        ids.add(i)
        st = (r.get("status") or "").strip()
        if st and st not in DEC_STATUS:
            p.append(f"{rel(area)}:decisions:{i}: status {st!r} is not " + "/".join(DEC_STATUS))
        # Only a standing decision must have a body. A superseded, withdrawn or inherited
        # row is allowed to be a tombstone: the id is reserved, the reasoning lives in the
        # decision that replaced it.
        if st == "standing" and not (ddir / f"{i}.md").exists():
            p.append(f"{rel(area)}:decisions:{i}: standing, but data/decisions/{i}.md does not exist")
        if st == "superseded" and not (r.get("superseded_by") or "").strip():
            p.append(f"{rel(area)}:decisions:{i}: superseded with no superseded_by")
        if st == "standing" and (ddir / f"{i}.md").exists():
            body = (ddir / f"{i}.md").read_text(encoding="utf-8", errors="replace")
            if re.search(r"\*\*Decision\.\*\*\s*\*\*Why\.\*\*", body):
                p.append(f"{rel(area)}:decisions:{i}: standing, but its body is still the empty "
                         "stub `rx7.py new` wrote - write it or withdraw it")
    if ddir.is_dir():
        for f in sorted(ddir.glob("D-*.md")):
            if f.stem not in ids:
                p.append(f"{rel(area)}: data/decisions/{f.name} has no row in decisions.csv")
    return p


def check_phase(area: Path) -> list[str]:
    _, rows = read_table(area, "_project")
    kv = {(r.get("key") or "").strip(): (r.get("value") or "").strip() for r in rows}
    ph = kv.get("phase", "")
    if ph and ph not in PHASES:
        return [f"{rel(area)}:_project: phase {ph!r} is not one of " + "/".join(PHASES)]
    return []


def run_check(sel=None):
    keyidx = load_keys()
    tree_index(fresh=True)
    problems = []
    for a in sel or areas():
        problems += check_area(a, keyidx)
    _, bp = parse_blocks()
    problems += bp
    problems += check_supersedes()
    seen_prefix = {}
    for a in areas():
        px = block_prefix(a)
        if px and px in seen_prefix:
            problems.append(f"{rel(a)} and {rel(seen_prefix[px])} both own block prefix {px!r} - "
                            "their block ids would collide; renumber one directory")
        elif px:
            seen_prefix[px] = a
    return problems


def check_supersedes():
    """R4 both ways round: a standing decision that supersedes D-x means D-x is superseded,
    everywhere it has a row, and says by what. §3 calls two standing rulings that disagree a
    contradiction - which is exactly what an un-marked supersede is (D-355 / D-210 sat that
    way until 2026-09-21, and a gate on D-210 would have opened)."""
    rows = {}
    for a in areas():
        _, rs = read_table(a, "decisions")
        for r in rs:
            i = (r.get("id") or "").strip()
            if i:
                rows.setdefault(i, []).append((a, r))
    p = []
    for i, lst in rows.items():
        for a, r in lst:
            if (r.get("status") or "").strip() != "standing":
                continue
            for old in re.findall(r"\bD-\d{3}\b", r.get("supersedes") or ""):
                for oa, orow in rows.get(old, []):
                    ost = (orow.get("status") or "").strip()
                    if ost not in ("superseded", "withdrawn"):
                        p.append(f"{rel(oa)}:decisions:{old}: {ost or 'no status'}, but {rel(a)} {i} "
                                 f"supersedes it - set status=superseded, superseded_by={i}")
    return p


def unresolved_cites():
    """ADVISORY ONLY. Ids written inside prose cells are documentation, not structure:
    a cite that no longer resolves is worth knowing about and must never refuse a commit.
    Structural references are the `ref` column in _schema.csv, which `check` does enforce
    exactly. This scan is deliberately narrow - D- with three digits only - because this
    car's own diagrams use two-digit codes like D-01 and B-12 for components, and a block
    id like `00.18` cannot be told from a number in prose, so it is not scanned at all."""
    known = set()
    for a in areas():
        _, rows = read_table(a, "decisions")
        known |= {(r.get("id") or "").strip() for r in rows}
    for d in (ROOT / "99-ARCHIVE").rglob("D-*.md"):
        known.add(d.stem)
    out = []
    # retired.csv exists "so it can never come back" - so say where it has.
    terms = set()
    for a in areas():
        _, rr = read_table(a, "retired")
        terms |= {(r.get("term") or "").strip() for r in rr}
    terms = {t for t in terms if len(t) >= 5 and not t.startswith("BLK-")}
    for a in areas():
        for f in sorted((a / "data").glob("*.csv")):
            if f.stem.startswith("_") or f.stem in ("decisions", "retired", "log"):
                continue
            _, body = read_csv_rows(f)
            for i, row in enumerate(body, start=2):
                for cell in row:
                    low = (cell or "").lower()
                    for t in terms:
                        if t.lower() in low:
                            out.append(f"{rel(a)}:{f.stem} line {i} uses the retired term {t!r}")
    for a in areas():
        for f in sorted((a / "data").glob("*.csv")):
            _, body = read_csv_rows(f)
            for i, row in enumerate(body, start=2):
                for cell in row:
                    for ident in CITE_RE.findall(cell or ""):
                        if ident not in known:
                            out.append(f"{rel(a)}:{f.stem} line {i} cites {ident}, which resolves to nothing")
    return sorted(set(out))


# --------------------------------------------------------------------- commands

def cmd_check(args):
    sel = [resolve_area(args.area)] if args.area else None
    problems = run_check(sel)
    if problems:
        for x in problems:
            print(x)
        print(f"\n{len(problems)} problem(s) - the record contradicts itself. Fix the rows named above.")
        return RC_INVALID
    print("record valid")
    return RC_OK


def cmd_status(args):
    keyidx = load_keys()
    problems = run_check()
    blocks, _ = parse_blocks()
    open_b = [b for b in blocks if b["section"] == "OPEN"]
    waiting = [b for b in open_b if b["solution"]]
    stuck = [b for b in open_b if not b["solution"]]

    idx = tree_index()
    print(f"RECORD   {'valid' if not problems else str(len(problems)) + ' problem(s)'}")
    for a in areas():
        _, prow = read_table(a, "_project")
        kv = {(r.get("key") or "").strip(): (r.get("value") or "").strip() for r in prow}
        line = f"{rel(a):<34} {kv.get('phase','-'):<10}"
        if (a / "data" / "work.csv").exists():
            _, w = read_table(a, "work")
            ag = sum(1 for r in w if r.get("state") == "open" and r.get("owner") == "agent")
            cm = sum(1 for r in w if r.get("state") == "open" and r.get("owner") == "camden")
            line += f" work: {ag} agent / {cm} camden"
        alone, standing = decisions_made_alone(a)
        if standing:
            line += f"   decisions {len(standing)} ({len(alone)} nobody was asked)"
        print(line)
        print_queue(a.name, idx)
    print(f"BLOCKS   {len(stuck)} unanswered, {len(waiting)} answered and not yet applied")
    for b in stuck:
        print(f"  {b['id']} {b['area']}: {b['fields'].get('Ask','')[:80]}{block_age(b)}")
    for b in waiting:
        print(f"  {b['id']} {b['area']}: ANSWERED - apply it{block_age(b)}")
    if problems:
        return RC_INVALID
    if waiting or stuck:
        return RC_WAITING
    return RC_OK


def days_since(iso: str):
    """Whole days from an ISO date to today; None if the text is not a date."""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", (iso or "").strip())
    if not m:
        return None
    return (datetime.date.today() - datetime.date(*(int(x) for x in m.groups()))).days


def block_age(b) -> str:
    d = days_since(b["fields"].get("Opened", ""))
    return f"  ({d}d)" if d is not None else ""


def decisions_made_alone(area: Path):
    """(alone, standing) — standing decisions that closed nothing at all.

    Not a stored flag: §3 already partitions every ruling into one he answered and one
    made alone, and `closes` says which — a block id (or, from v2, a Q-/V- question) means he
    ruled it; empty means nobody was asked. One home per fact (R2).

    It is a number to watch, not a refusal: some of these are the small calls §3 exists to
    authorise. It earns its place in `status` because nothing else in the tree counts how
    much of the design was settled without him."""
    _, rows = read_table(area, "decisions")
    standing = [r for r in rows if (r.get("status") or "").strip() == "standing"]
    alone = [(r.get("id") or "").strip() for r in standing if not (r.get("closes") or "").strip()]
    return alone, standing


def print_queue(area: str, idx, limit=6):
    """READY and BLOCKED — the only two lists that answer 'what can start now'."""
    ready, blocked = ready_report(area, idx)
    if not ready and not blocked:
        return
    if ready:
        by_owner = {}
        for wid, row, _ in ready:
            by_owner.setdefault(row.get("owner", "?"), []).append((wid, row))
        print("   ready: " + " · ".join(f"{o} {len(v)}" for o, v in sorted(by_owner.items()))
              + (f"   blocked {len(blocked)}" if blocked else ""))
        for owner, items in sorted(by_owner.items()):
            for wid, row in items[:limit]:
                print(f"     {owner:<7} {wid:<7} {(row.get('item') or '')[:70]}")
            if len(items) > limit:
                print(f"     {'':<7} {'':<7} … {len(items) - limit} more")
    else:
        print(f"   ready: nothing — all {len(blocked)} open row(s) are gated")
    for wid, row, why in blocked[:limit]:
        print(f"     blocked {wid:<7} {(row.get('item') or '')[:46]:<46} waits on {', '.join(why) or '?'}")
    if len(blocked) > limit:
        print(f"     blocked … {len(blocked) - limit} more")


def cmd_tables(args):
    a = resolve_area(args.area)
    tables, cols = schema(a)
    for t in sorted(tables):
        _, rows = read_table(a, t)
        spec = cols.get(t) or []
        print(f"{t:<20} {len(rows):>5} rows  key={key_column(spec) or '?':<12} {tables[t].get('purpose','')}")
    return RC_OK


def cmd_get(args):
    a = resolve_area(args.area)
    _, cols = schema(a)
    spec = cols.get(args.table)
    if not spec:
        die(f"{args.table!r} is not a declared table in {rel(a)}")
    kc = key_column(spec)
    _, rows = read_table(a, args.table)
    for r in rows:
        if (r.get(kc) or "").strip() == args.key:
            for c in spec:
                print(f"{c['column']:<18} {r.get(c['column'],'')}")
            return RC_OK
    print(f"{args.table}:{args.key} has no row")
    return RC_WAITING


def _pairs(items):
    out = {}
    for it in items:
        if "=" not in it:
            die(f"{it!r} is not col=value")
        k, v = it.split("=", 1)
        out[k.strip()] = v
    return out


def cmd_set(args):
    a = resolve_area(args.area)
    _, cols = schema(a)
    spec = cols.get(args.table)
    if not spec:
        die(f"{args.table!r} is not a declared table in {rel(a)}")
    declared = {c["column"] for c in spec}
    kc = key_column(spec)
    vals = _pairs(args.pairs)
    for k in vals:
        if k not in declared:
            die(f"{args.table} has no declared column {k!r} - add it to _schema.csv first")
    hdr, rows = read_table(a, args.table)
    hit = None
    for r in rows:
        if (r.get(kc) or "").strip() == args.key:
            hit = r
            break
    if hit is None:
        die(f"{args.table}:{args.key} has no row - use `add`")
    before = {k: hit.get(k, "") for k in vals}
    hit.update(vals)
    write_table(a, args.table, hdr, rows)
    for k, v in vals.items():
        print(f"{args.table}:{args.key} {k}: {before[k]!r} -> {v!r}")
    return RC_OK


def cmd_add(args):
    a = resolve_area(args.area)
    _, cols = schema(a)
    spec = cols.get(args.table)
    if not spec:
        die(f"{args.table!r} is not a declared table in {rel(a)}")
    declared = [c["column"] for c in spec]
    kc = key_column(spec)
    vals = _pairs(args.pairs)
    for k in vals:
        if k not in declared:
            die(f"{args.table} has no declared column {k!r} - add it to _schema.csv first")
    if not (vals.get(kc) or "").strip():
        die(f"{args.table} needs {kc}=<key>")
    hdr, rows = read_table(a, args.table)
    hdr = hdr or declared
    if any((r.get(kc) or "").strip() == vals[kc] for r in rows):
        die(f"{args.table}:{vals[kc]} already exists - use `set`")
    rows.append({c: vals.get(c, "") for c in hdr})
    write_table(a, args.table, hdr, rows)
    print(f"{args.table}:{vals[kc]} added")
    return RC_OK


def cmd_del(args):
    a = resolve_area(args.area)
    _, cols = schema(a)
    spec = cols.get(args.table)
    if not spec:
        die(f"{args.table!r} is not a declared table in {rel(a)}")
    kc = key_column(spec)
    hdr, rows = read_table(a, args.table)
    keep = [r for r in rows if (r.get(kc) or "").strip() != args.key]
    if len(keep) == len(rows):
        die(f"{args.table}:{args.key} has no row")
    write_table(a, args.table, hdr, keep)
    print(f"{args.table}:{args.key} deleted")
    return RC_OK


def cmd_sql(args):
    a = resolve_area(args.area)
    tables, _ = schema(a)
    con = sqlite3.connect(":memory:")
    for t in tables:
        hdr, rows = read_table(a, t)
        if not hdr:
            continue
        cq = ",".join('"%s"' % c for c in hdr)
        con.execute(f'create table "{t}" ({cq})')
        con.executemany(
            f'insert into "{t}" values ({",".join("?" * len(hdr))})',
            [[r.get(c, "") for c in hdr] for r in rows],
        )
    try:
        cur = con.execute(args.query)
    except sqlite3.Error as e:
        die(f"sql: {e}")
    names = [d[0] for d in cur.description or []]
    out = cur.fetchall()
    if names:
        print(" | ".join(names))
    for row in out:
        print(" | ".join("" if v is None else str(v) for v in row))
    print(f"({len(out)} row(s))")
    return RC_OK if out else RC_WAITING


def cmd_find(args):
    sel = [resolve_area(args.area)] if args.area else areas()
    needle = args.text.lower()
    n = 0
    for a in sel:
        for f in sorted((a / "data").glob("*.csv")):
            hdr, body = read_csv_rows(f)
            for i, row in enumerate(body, start=2):
                if any(needle in (c or "").lower() for c in row):
                    print(f"{rel(a)}:{f.stem} line {i}: " + " | ".join(row)[:200])
                    n += 1
        for f in sorted((a / "data" / "decisions").glob("*.md")) if (a / "data" / "decisions").is_dir() else []:
            if needle in f.read_text(encoding="utf-8", errors="replace").lower():
                print(f"{rel(a)}:{f.stem} (decision body)")
                n += 1
    if BLOCKS_MD.exists() and needle in BLOCKS_MD.read_text(encoding="utf-8").lower():
        print("BLOCKS.md contains it")
        n += 1
    print(f"({n} hit(s))")
    return RC_OK if n else RC_WAITING


def next_decision_id() -> str:
    """The highest D- anywhere in the tree or the archive, plus one (R5). One derivation, used
    by `new` and by DECISIONS.md's "Next id" line, so the two can never disagree."""
    nums = []
    for d in (ROOT / "99-ARCHIVE").rglob("D-*.md"):
        m = re.match(r"D-(\d+)$", d.stem)
        if m:
            nums.append(int(m.group(1)))
    for f in [a / "data" / "decisions.csv" for a in areas()] + list((ROOT / "99-ARCHIVE").rglob("decisions.csv")):
        hdr, body = read_csv_rows(f)
        if "id" in hdr:
            for row in body:
                m = re.match(r"D-(\d+)$", row[hdr.index("id")].strip())
                if m:
                    nums.append(int(m.group(1)))
    return f"D-{max(nums, default=0) + 1:03d}"


def cmd_new(args):
    a = resolve_area(args.area)
    hdr, rows = read_table(a, "decisions")
    nid = next_decision_id()
    vals = _pairs(args.pairs)
    stray = [k for k in vals if hdr and k not in hdr]
    if stray:
        die(f"decisions has no column {', '.join(stray)} - nothing reserved (a typo here would "
            "silently lose a `closes`)")
    row = {c: vals.get(c, "") for c in (hdr or ["id", "date", "title", "status", "superseded_by", "closes", "who"])}
    row["id"] = nid
    row["date"] = vals.get("date", today())
    row["title"] = args.title
    row["status"] = vals.get("status", "standing")
    write_table(a, "decisions", hdr or list(row), rows + [row])
    body = a / "data" / "decisions" / f"{nid}.md"
    body.parent.mkdir(parents=True, exist_ok=True)
    body.write_text(
        f"# {nid} - {args.title}\n\n*{row['date']} - {row.get('who') or 'Camden'}*\n\n"
        "**Decision.** \n\n**Why.** \n\n**In the data.** \n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"{nid} reserved - write the body in {rel(body)}")
    return RC_OK


DEC_HEADER = """# DECISIONS — every ruling on this car

*Generated by `tools/rx7.py decisions` from every area's `decisions.csv` and
`data/decisions/<id>.md`. Never edited by hand: it is a projection of those files and
adds no fact of its own. Regenerated at the end of every run. Nothing ever gates a
commit on whether it is current — if it is stale, run the command.*

This is the record of what was decided and why, including every small call made without
you. Standing decisions are grouped by the system they touch, in id order inside each
group. Superseded and withdrawn ones are listed at the end with the decision that
replaced each, so any id ever issued can still be found by searching this file for it.

"""


def cmd_decisions(args):
    """Regenerate DECISIONS.md — one file, every area, grouped by category.
    Reads decisions.csv and data/decisions/*.md in every area. Writes nothing else."""
    per = {}          # area -> category -> [(num, id, body, row)]
    dead = []         # superseded / withdrawn / inherited
    latest = []
    for a in areas():
        _, rows = read_table(a, "decisions")
        for r in rows:
            i = (r.get("id") or "").strip()
            if not i:
                continue
            m = re.match(r"D-(\d+)$", i)
            num = int(m.group(1)) if m else 0
            st = (r.get("status") or "standing").strip()
            bp = a / "data" / "decisions" / f"{i}.md"
            body = bp.read_text(encoding="utf-8", errors="replace").strip() if bp.exists() else ""
            # Only superseded and withdrawn are dead. `inherited` is a LIVE decision that
            # another project owns and this one reads — burying it here would hide every
            # 02-engine ruling, all seven of which are inherited.
            if st in ("superseded", "withdrawn"):
                dead.append((num, i, a.name, st, r, body))
                continue
            cat = (r.get("system") or "Uncategorised").strip() or "Uncategorised"
            per.setdefault(a.name, {}).setdefault(cat, []).append((num, i, body, r, st))
            if st == "standing":
                latest.append((num, i, a.name, (r.get("title") or "").strip()))

    latest.sort()
    out = [DEC_HEADER]
    if latest:
        tail = latest[-5:]
        out.append("**Most recent:** " + " · ".join(f"`{i}` {t or ''}".strip() for _, i, _, t in tail))
        out.append(f"\nNext id: `{next_decision_id()}`.\n")

    out.append("## Contents\n")
    for aname in sorted(per):
        cats = per[aname]
        line = " · ".join(f"{c} ({len(cats[c])})" for c in sorted(cats))
        out.append(f"**{aname}** — {line}\n")
    if dead:
        out.append(f"**Superseded and withdrawn** — {len(dead)}\n")

    for aname in sorted(per):
        out.append(f"\n---\n\n# {aname}\n")
        for cat in sorted(per[aname]):
            items = sorted(per[aname][cat])
            ids = " ".join(i for _, i, _, _, _ in items)
            out.append(f"\n## {cat}\n")
            out.append(f"*{len(items)} live — {ids}*\n")
            for _, i, body, r, st in items:
                date = (r.get("date") or "").strip()
                sup = (r.get("supersedes") or "").strip()
                clo = (r.get("closes") or "").strip()
                tags = " · ".join(x for x in [date, f"supersedes {sup}" if sup else "",
                                              f"closes {clo}" if clo else "",
                                              "inherited - owned by another project"
                                              if st == "inherited" else ""] if x)
                if body:
                    out.append(body)
                else:
                    out.append(f"**{i} — {(r.get('title') or '').strip()}**")
                if tags:
                    out.append(f"*{tags}*\n")
                else:
                    out.append("")

    if dead:
        out.append("\n---\n\n# Superseded and withdrawn\n")
        out.append("*Kept so every id ever issued can be found by searching for it.*\n")
        for num, i, aname, st, r, body in sorted(dead):
            by = (r.get("superseded_by") or "").strip()
            title = (r.get("title") or "").strip()
            arrow = f" → `{by}`" if by else ""
            out.append(f"- `{i}` ({aname}, {st}){arrow} — {title or '(no title)'}")

    text = "\n".join(out).rstrip() + "\n"
    (ROOT / "DECISIONS.md").write_text(text, encoding="utf-8", newline="\n")
    n = sum(len(v) for c in per.values() for v in c.values())
    print(f"DECISIONS.md written: {n} standing in "
          f"{sum(len(c) for c in per.values())} categories, {len(dead)} superseded/withdrawn")
    return RC_OK


TODO_HEADER = """# TODO — {area}

*Generated by `tools/rx7.py todo` from this project's `data/work.csv` (D-373). Never edited by
hand: it is a projection of that table and adds no fact of its own, so it cannot disagree with
the record. Nothing gates a commit on whether it is current — if it looks stale, run the
command. There are no boxes to tick here on purpose: to mark a step done, say what you did
("E9 done, cables crimped") and the row is set and this file regenerated.*

**▶** ready now · **⏳** waiting on what is named · **✔** done · **✖** dropped.
*you* = Camden · *agent* = Claude. Full detail of any row:
`python tools/rx7.py get {rel} work <id>`.

"""


def cmd_todo(args):
    """Regenerate <project>/TODO.md for every project with a `work` table (or one, with -p).
    Reads: work.csv, plus the tree index for gates (decisions, BLOCKS.md, other areas' work).
    Writes: <area>/TODO.md and nothing else. Read-only projection, like DECISIONS.md (D-373)."""
    idx = tree_index(fresh=True)
    status_rc = RC_OK
    sel = [resolve_area(args.area)] if args.area else [
        a for a in areas() if (a / "data" / "work.csv").exists() and (block_prefix(a) or "").isdigit()]
    for a in sel:
        _, rows = read_table(a, "work")
        rows = [r for r in rows if (r.get("id") or "").strip()]
        by_id = {r["id"].strip(): r for r in rows}

        def status(r):
            st = (r.get("state") or "").strip()
            if st in ("done", "dropped"):
                return st, []
            met, unmet, bad = gate_state(r.get("gate", ""), a.name, idx)
            if st == "open" and met:
                return "ready", []
            why = unmet + bad
            if st == "blocked" and not why:
                why = ["marked blocked - see its note"]
            return "waiting", why

        memo = {}

        def depth(wid, seen=()):
            # Working order: a row comes after everything its gate names. Phase gates sit after
            # the whole design; a gate on another area or a block counts as one step.
            if wid in memo:
                return memo[wid]
            r = by_id[wid]
            st, _ = status(r)
            if st in ("ready", "done", "dropped"):
                memo[wid] = 0
                return 0
            d = 1
            for ref in parse_gate(r.get("gate", "")):
                if ref.startswith("phase:"):
                    d = max(d, 50)
                elif ref in by_id and ref not in seen:
                    d = max(d, 1 + depth(ref, seen + (wid,)))
            memo[wid] = d
            return d

        info = {wid: (status(r), depth(wid)) for wid, r in by_id.items()}
        num = lambda w: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", w)]
        owner = lambda r: "you" if (r.get("owner") or "").strip() == "camden" else "agent"
        mark = {"ready": "▶", "waiting": "⏳", "done": "✔", "dropped": "✖"}

        _, prow = read_table(a, "_project")
        kv = {(r.get("key") or "").strip(): (r.get("value") or "").strip() for r in prow}
        out = [TODO_HEADER.format(area=rel(a), rel=rel(a))]
        out.append(f"**Phase:** {kv.get('phase', '-')}. " + (f"**Goal:** {kv['goal']}\n" if kv.get("goal") else "\n"))

        ready = sorted((w for w in by_id if info[w][0][0] == "ready"),
                       key=lambda w: (owner(by_id[w]) != "you", num(w)))
        n_open = sum(1 for w in by_id if info[w][0][0] in ("ready", "waiting"))
        n_done = sum(1 for w in by_id if info[w][0][0] == "done")
        out.append(f"{n_open} open · {len(ready)} ready now · {n_done} done.\n")
        out.append("## Now — what can be started today\n")
        for who in ("you", "agent"):
            items = [w for w in ready if owner(by_id[w]) == who]
            if items:
                out.append(f"**{'Yours' if who == 'you' else 'Agent'}:**\n")
                out += [f"- **{w}** — {(by_id[w].get('item') or '').strip()}" for w in items]
                out.append("")
        if not ready:
            out.append("*Nothing is startable: every open row waits on something below.*\n")

        # stages in the order their open work becomes startable
        stages = {}
        for w, r in by_id.items():
            stages.setdefault((r.get("stage") or "-").strip(), []).append(w)
        def stage_key(s):
            open_d = [info[w][1] for w in stages[s] if info[w][0][0] in ("ready", "waiting")]
            # the stage's typical row, not its earliest - one early row (E2) must not pull the
            # whole install stage ahead of the parts arriving
            return (0 if open_d else 1, sorted(open_d)[len(open_d) // 2] if open_d else 0, s)
        out.append("## Everything, in working order\n")
        out.append("*Stages in the order their work can start; inside a stage, each row after "
                   "what it waits on.*\n")
        for s in sorted(stages, key=stage_key):
            ws = stages[s]
            title = next(((by_id[w].get("stage_title") or "").strip() for w in ws
                          if (by_id[w].get("stage_title") or "").strip()), "")
            out.append(f"### {s}" + (f" · {title}" if title else "") + "\n")
            live = sorted((w for w in ws if info[w][0][0] in ("ready", "waiting")),
                          key=lambda w: (info[w][1], num(w)))
            for w in live:
                r = by_id[w]
                (st, why), _ = info[w]
                line = f"- {mark[st]} **{w}** — {(r.get('item') or '').strip()}  \n  *{owner(r)}*"
                if why:
                    line += " · waits on: " + "; ".join(why)
                note = re.sub(r"\s+", " ", (r.get("note") or "").strip())
                if note:
                    line += f"  \n  {note}"
                out.append(line)
            closed = sorted((w for w in ws if info[w][0][0] in ("done", "dropped")), key=num)
            if closed:
                out.append(("\n" if live else "") + "*Closed:* " + " · ".join(
                    f"{mark[info[w][0][0]]} {w}" for w in closed))
            out.append("")
        body = "\n".join(out).rstrip() + "\n"
        path = a / "TODO.md"
        # R3: Camden may write in this file even though it says not to - and losing his
        # writing is the worst failure this system has. The file carries a fingerprint of
        # what the tool wrote; if the text no longer matches it, he has written in it, and
        # nothing is overwritten until what he wrote has been carried into the record.
        if path.exists() and not getattr(args, "force", False):
            old = path.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"\n<!-- rx7 todo sha256:([0-9a-f]{64}) -->\s*$", old)
            mine = old[:m.start() + 1] if m else None
            if not m or hashlib.sha256(mine.encode("utf-8")).hexdigest() != m.group(1):
                new_lines = set(body.splitlines())
                added = [l for l in old.splitlines() if l not in new_lines and not l.startswith("<!-- rx7 todo")]
                print(f"{rel(a)}/TODO.md has been written in by hand - NOT overwritten. Lines that "
                      "are not the tool's own (carry them into the record, then run with --force):")
                for l in added[:40]:
                    print("   " + l)
                status_rc = RC_WAITING
                continue
        path.write_text(body + f"<!-- rx7 todo sha256:{hashlib.sha256(body.encode('utf-8')).hexdigest()} -->\n",
                        encoding="utf-8", newline="\n")
        print(f"{rel(a)}/TODO.md written: {n_open} open, {len(ready)} ready")
    return status_rc


def cmd_cites(args):
    out = unresolved_cites()
    for x in out:
        print(x)
    print(f"({len(out)} unresolved cite(s) in prose - advisory, nothing is refused)")
    return RC_WAITING if out else RC_OK


def cmd_block(args):
    blocks, problems = parse_blocks()
    structural = [x for x in problems if x not in UNFINISHED]
    if structural:
        for x in structural:
            print(x)
        die("BLOCKS.md does not parse - fix it before adding a block (nothing was written)", RC_INVALID)
    if not args.area:
        die("a block belongs to a project: pass -p AREA - its number comes from that project")
    area = resolve_area(args.area)
    prefix = block_prefix(area)
    if not prefix:
        die(f"{rel(area)} owns no block prefix - only 00-CAR, 01-REFERENCE and "
            "02-PROJECTS/NN-* do")
    bid = next_block_id(blocks, prefix)
    append_block(bid, area, args.ask)
    print(f"{bid} appended to BLOCKS.md under {group_title(area)[3:]} - "
          "fill in Why / Options / Recommend / Stops")
    return RC_OK


def cmd_blocks(args):
    blocks, problems = parse_blocks()
    for x in problems:
        print(x)
    if problems:
        return RC_INVALID
    sel = [b for b in blocks if b["section"] == "OPEN"]
    if args.answered:
        sel = [b for b in sel if b["solution"]]
    if args.solved:
        print("solved blocks are not kept here — they are decisions. "
              "`rx7.py find 00.05` or read DECISIONS.md.")
        return RC_WAITING
    for b in sel:
        print(f"{b['id']} · {b['area'] or '-'} · {'answered' if b['solution'] else 'waiting'}")
        print(f"   ask:   {b['fields'].get('Ask','')}")
        if b["solution"]:
            print(f"   solve: {b['solution']}")
    print(f"({len(sel)} block(s))")
    return RC_OK if sel else RC_WAITING


def cmd_selftest(args):
    """The gate resolver's own tests. In memory: reads nothing, writes nothing.

    `check` asks whether THIS tree's gates are sound. This asks whether the thing that
    decides that is itself right — because a resolver that wrongly calls a gate 'met'
    puts the planner to work on something that is not ready, and one that wrongly calls
    it 'unmet' stops the project with no error anywhere. Both fail silently (R7)."""
    A, B = "00-electrical", "01-luxury"
    fails = []

    def mk(rows, phase="PLANNING", blocks=None):
        # 00.90 is still on the page (open). 00.91 is gone from the page and named in
        # some decision's `closes` — that is what "answered and applied" means now.
        idx = {"decisions": {"D-900": "standing", "D-901": "superseded"},
               "blocks": dict(blocks or {"00.90": "OPEN"}),
               "blocks_closed": {"00.91"},
               "phase": {A: phase, B: "PLANNING"},
               "work": {}, "work_ids": {}, "row": {}}
        for wid, gate, state in rows:
            idx["work"][(A, wid)] = state
            idx["work_ids"].setdefault(wid, []).append(A)
            idx["row"][(A, wid)] = {"id": wid, "gate": gate, "state": state,
                                    "owner": "agent", "item": wid, "stage": "A"}
        return idx

    def expect(label, got, want=True):
        if bool(got) != want:
            fails.append(label)
            print(f"FAIL {label}   got={got!r}")
        else:
            print(f"PASS {label}")

    idx = mk([("A1", "D-404", "open")])
    expect("a reference to nothing is refused", gate_state("D-404", A, idx)[2])
    expect("prose in a gate is refused", gate_state("install M-1", A, idx)[2])
    expect("a block that does not exist is refused", gate_state("00.94", A, idx)[2])

    amb = mk([("A1", "", "open")])
    amb["work_ids"]["A1"].append(B)
    amb["work"][(B, "A1")] = "open"
    expect("an ambiguous unqualified work id is refused", gate_state("A1", "02-engine", amb)[2])

    expect("a dependency ring is found",
           gate_cycles(mk([("A1", "A2", "open"), ("A2", "A3", "open"), ("A3", "A1", "open")])))
    expect("an area gated only on itself is refused",
           walled_off(A, mk([("A1", "A2", "open"), ("A2", "A1", "open")])))
    expect("an area waiting on a block is NOT refused",
           walled_off(A, mk([("A1", "00.90", "open")])), want=False)

    ext = mk([("A1", f"{B}:F1", "open")])
    ext["work"][(B, "F1")] = "open"
    ext["work_ids"].setdefault("F1", []).append(B)
    ext["row"][(B, "F1")] = {"id": "F1", "gate": "", "state": "open"}
    expect("an area waiting on another area is NOT refused", walled_off(A, ext), want=False)

    suf = mk([("A1", "W-330b", "open"), ("W-330b", "", "done")])
    expect("a work id with a letter suffix is a reference, not prose",
           gate_state("W-330b", A, suf)[2], want=False)
    expect("a done work id with a letter suffix opens its gate", gate_state("W-330b", A, suf)[0])

    ok = mk([("A1", "A2", "open"), ("A2", "", "done")])
    expect("an empty gate is met", gate_state("", A, ok)[0])
    expect("a done work row opens its gate", gate_state("A2", A, ok)[0])
    expect("an open work row holds its gate shut", gate_state("A1", A, ok)[0], want=False)
    expect("a standing decision opens its gate", gate_state("D-900", A, ok)[0])
    expect("a superseded decision does not", gate_state("D-901", A, ok)[0], want=False)
    expect("a block that became a decision opens its gate", gate_state("00.91", A, ok)[0])
    expect("a block still on the page does not", gate_state("00.90", A, ok)[0], want=False)
    expect("a block that never existed is refused", gate_state("00.94", A, ok)[2])
    expect("the phase reached opens its gate", gate_state("phase:PLANNING", A, ok)[0])
    expect("a later phase does not", gate_state("phase:BUILDING", A, ok)[0], want=False)
    expect("several references, one unmet, stays shut", gate_state("D-900 A1", A, ok)[0], want=False)
    expect("several references, all met, opens", gate_state("D-900 A2 00.91", A, ok)[0])

    expect("a project block id is a block id", BLOCK_ID_RE.match("00.18"))
    expect("a car block id is a block id", BLOCK_ID_RE.match("CAR.01"))
    expect("a one-digit number is not a block id", BLOCK_ID_RE.match("13.8"), want=False)
    expect("an old BLK- id is not a block id", BLOCK_ID_RE.match("BLK-020"), want=False)
    expect("an old BLK- id in a gate is refused", gate_state("BLK-020", A, ok)[2])
    expect("a project's prefix is its directory number",
           block_prefix(ROOT / "02-PROJECTS" / "07-paint") == "07")
    expect("00-CAR does not share 00 with a project", block_prefix(ROOT / "00-CAR") == "CAR")
    expect("a numbered folder outside 02-PROJECTS owns no prefix",
           block_prefix(ROOT / "99-ARCHIVE" / "03-old"), want=False)

    # --- the page parser and writer, on a scratch copy of BLOCKS.md (never the real one) ---
    import tempfile
    global BLOCKS_MD
    real = BLOCKS_MD
    elec = next((a for a in areas() if block_prefix(a) == "00"), None)
    with tempfile.TemporaryDirectory() as td:
        try:
            BLOCKS_MD = Path(td) / "BLOCKS.md"
            head = "# BLOCKS\n\n## 00 · Electrical\n\n"
            full = ("**Ask** a\n**Why** b\n**Options**\n- (a) x\n**Recommend** a\n**Stops** s\n")
            BLOCKS_MD.write_text(head + "### 00.90 · one\n" + full + "SOLVE: yes please\n", encoding="utf-8")
            bl, pr = parse_blocks()
            expect("an answer after a bare `SOLVE:` is read", bl and bl[0]["solution"] == "yes please")
            BLOCKS_MD.write_text(head + "### 00.90 · one\n" + full +
                                 "**SOLVE:** first\n## my notes\nsecond\n", encoding="utf-8")
            bl, pr = parse_blocks()
            expect("a `## ` line inside his answer does not cut it off",
                   bl and "second" in bl[0]["solution"])
            BLOCKS_MD.write_text(head + "### 00.90 · one\n" + full + "**SOLVE:**\n### 00.7 · short id\n",
                                 encoding="utf-8")
            expect("a malformed block heading after an empty answer is refused, not swallowed",
                   parse_blocks()[1])
            BLOCKS_MD.write_text(head + "### 00.90 · one\n" + full + "**SOLVE:** yes\n### my own heading\nmore\n",
                                 encoding="utf-8")
            bl, pr = parse_blocks()
            expect("a `###` of his own inside an answer stays his text",
                   bl and "more" in bl[0]["solution"] and not pr)
            if elec is not None:
                BLOCKS_MD.write_text(head + "### 00.90 · one\n" + full + "**SOLVE:**\n", encoding="utf-8")
                append_block("00.91", elec, "Swap 12 → 14 AWG on L3?")
                bl, _ = parse_blocks()
                ids = [b["id"] for b in bl]
                expect("a block whose ask contains → is added and parses", "00.91" in ids)
                expect("adding it leaves the previous block unanswered",
                       bl and bl[0]["id"] == "00.90" and not bl[0]["solution"])
        finally:
            BLOCKS_MD = real

    expect("an ISO date parses", days_since("2026-09-01") is not None)
    expect("a non-date does not", days_since("soon") is None)

    print(f"\n{len(fails)} failure(s)" if fails else "\nselftest: all pass")
    return RC_INVALID if fails else RC_OK


def cmd_log(args):
    a = resolve_area(args.area)
    hdr, rows = read_table(a, "log")
    hdr = hdr or ["id", "date", "workflow", "ids", "summary"]
    # KIND is the log's `workflow` column, and its vocabulary is the area's declared enum.
    shdr, srows = read_table(a, "_schema")
    typ = next(((r.get("type") or "") for r in srows
                if r.get("table") == "log" and r.get("column") == "workflow"), "")
    if typ.startswith("enum(") and args.kind not in typ[5:-1].split("|"):
        die(f"log KIND must be one of {typ[5:-1].replace('|', '/')} - got {args.kind!r} (nothing was written)")
    nums = [int(m.group(1)) for m in (re.match(r"L-?(\d+)$", (r.get("id") or "")) for r in rows) if m]
    nid = f"L-{max(nums, default=0) + 1:04d}"
    rows.append({"id": nid, "date": today(), "workflow": args.kind, "ids": args.refs or "",
                 "summary": args.what})
    write_table(a, "log", hdr, rows)
    print(f"{nid} logged")
    return RC_OK


# ------------------------------------------------------------------------- main

def main(argv=None):
    class _Parser(argparse.ArgumentParser):
        def error(self, message):  # argparse's own exit 2 would read as "nothing to do"
            self.print_usage(sys.stderr)
            print(f"rx7: {message}", file=sys.stderr)
            sys.exit(RC_USAGE)

    ap = _Parser(prog="rx7", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("check", help="validate the whole record (rc 1 if it contradicts itself)")
    p.add_argument("-p", "--area")
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("status", help="one screen: record validity, phases, work, blocks")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("tables", help="every declared table in an area, with row counts")
    p.add_argument("area")
    p.set_defaults(fn=cmd_tables)

    p = sub.add_parser("get", help="one row")
    p.add_argument("area"); p.add_argument("table"); p.add_argument("key")
    p.set_defaults(fn=cmd_get)

    p = sub.add_parser("set", help="change columns on an existing row")
    p.add_argument("area"); p.add_argument("table"); p.add_argument("key")
    p.add_argument("pairs", nargs="+")
    p.set_defaults(fn=cmd_set)

    p = sub.add_parser("add", help="add a row")
    p.add_argument("area"); p.add_argument("table"); p.add_argument("pairs", nargs="+")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("del", help="delete a row")
    p.add_argument("area"); p.add_argument("table"); p.add_argument("key")
    p.set_defaults(fn=cmd_del)

    p = sub.add_parser("sql", help="read-only query across one area's tables")
    p.add_argument("area"); p.add_argument("query")
    p.set_defaults(fn=cmd_sql)

    p = sub.add_parser("find", help="search every cell, decision body and BLOCKS.md")
    p.add_argument("text"); p.add_argument("-p", "--area")
    p.set_defaults(fn=cmd_find)

    p = sub.add_parser("new", help="reserve the next D- and write its body stub")
    p.add_argument("area"); p.add_argument("title"); p.add_argument("pairs", nargs="*")
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("decisions", help="regenerate DECISIONS.md, grouped by category")
    p.set_defaults(fn=cmd_decisions)

    p = sub.add_parser("todo", help="regenerate each project's TODO.md from its work table")
    p.add_argument("-p", "--area")
    p.add_argument("--force", action="store_true",
                   help="overwrite a TODO.md written in by hand - only after carrying what he wrote")
    p.set_defaults(fn=cmd_todo)

    p = sub.add_parser("cites", help="advisory: prose cites that no longer resolve (never refuses)")
    p.set_defaults(fn=cmd_cites)

    p = sub.add_parser("block", help="append a new block to BLOCKS.md")
    p.add_argument("ask"); p.add_argument("-p", "--area", required=True)
    p.set_defaults(fn=cmd_block)

    p = sub.add_parser("blocks", help="list blocks")
    p.add_argument("--solved", action="store_true")
    p.add_argument("--answered", action="store_true", help="open blocks Camden has answered")
    p.set_defaults(fn=cmd_blocks)

    p = sub.add_parser("selftest", help="the gate resolver's own tests (in memory; touches nothing)")
    p.set_defaults(fn=cmd_selftest)

    p = sub.add_parser("log", help="append a log row")
    p.add_argument("area"); p.add_argument("kind"); p.add_argument("what"); p.add_argument("refs", nargs="?")
    p.set_defaults(fn=cmd_log)

    args = ap.parse_args(argv)
    return args.fn(args) or RC_OK


if __name__ == "__main__":
    if os.name == "nt":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        print("rx7: crashed - that is a bug in the tool, not a verdict on the record (rc 3)")
        sys.exit(RC_USAGE)

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

NO COUNTERS ARE EVER STORED. The next D- is max(decisions.id)+1; the next B-
is max of the ids in BLOCKS.md +1. A stored counter can disagree with reality;
a derived one cannot.

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
import os
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOCKS_MD = ROOT / "BLOCKS.md"

RC_OK, RC_INVALID, RC_WAITING = 0, 1, 2

PHASES = ("PERMANENT", "PROPOSED", "PLANNING", "SOURCING", "BUILDING", "COMPLETE")
# `inherited` is a decision this project reads but another project owns.
DEC_STATUS = ("standing", "superseded", "withdrawn", "inherited")

DATE_RE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
ID_RE = re.compile(r"^[A-Z]{1,4}-\d{1,4}$")
# Blocks are BLK-, never B-: this car's factory diagrams already use B-12, D-01 and
# friends as component codes, and an id family must never share a namespace with the
# subject matter. Prose cites are checked by `rx7.py cites` (advisory), never by `check`.
CITE_RE = re.compile(r"\b(D-\d{3}|BLK-\d{1,4})\b")
BLOCK_HEAD_RE = re.compile(
    r"^###\s+BLK-(\d{1,4})\s*(?:·\s*([^→\n]+?))?\s*(?:→\s*(D-\d{3}))?\s*$"
)
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


def die(msg: str, code: int = RC_INVALID):
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

def parse_blocks():
    """Return (blocks, problems). Never rewrites the file; refuses rather than guess."""
    if not BLOCKS_MD.exists():
        return [], []
    lines = BLOCKS_MD.read_text(encoding="utf-8").splitlines()
    blocks, problems = [], []
    section, cur = "OPEN", None
    for ln, raw in enumerate(lines, start=1):
        s = raw.strip()
        if s.upper().startswith("## "):
            head = s[3:].strip().upper()
            if head in ("OPEN", "SOLVED"):
                section = head
            cur = None
            continue
        m = BLOCK_HEAD_RE.match(s)
        if m:
            cur = {
                "id": f"BLK-{int(m.group(1)):03d}",
                "num": int(m.group(1)),
                "area": (m.group(2) or "").strip(),
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
        if cur["in_solve"]:
            cur["solve"].append(raw)
            continue
        f = FIELD_RE.match(s)
        if f:
            name, rest = f.group(1), f.group(2)
            if name.upper() == "SOLVE":
                cur["in_solve"] = True
                if rest.strip():
                    cur["solve"].append(rest)
            else:
                cur["fields"][name] = rest
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
            if not b["in_solve"]:
                problems.append(
                    f"BLOCKS.md: {b['id']} (line {b['line']}) has no **SOLVE:** line - "
                    "Camden has nowhere to answer"
                )
        else:
            if not b["closer"]:
                problems.append(
                    f"BLOCKS.md: {b['id']} (line {b['line']}) is under SOLVED with no "
                    "→ D-### naming the decision it produced"
                )
            if not b["solution"]:
                problems.append(
                    f"BLOCKS.md: {b['id']} (line {b['line']}) is under SOLVED with an empty SOLVE"
                )
    return blocks, problems


def next_block_num(blocks):
    return (max([b["num"] for b in blocks], default=0)) + 1


def append_block(num: int, area: str, ask: str) -> None:
    text = BLOCKS_MD.read_text(encoding="utf-8") if BLOCKS_MD.exists() else (
        "# BLOCKS\n\n## OPEN\n\n## SOLVED\n"
    )
    entry = (
        f"### BLK-{num:03d} · {area}\n"
        f"**Ask** {ask}\n"
        f"**Why** \n"
        f"**Options**\n- (a) \n- (b) \n"
        f"**Recommend** \n"
        f"**Stops** \n"
        f"**SOLVE:**\n\n"
    )
    marker = "\n## SOLVED"
    if marker in text:
        i = text.index(marker)
        text = text[:i].rstrip("\n") + "\n\n" + entry + text[i:]
    else:
        text = text.rstrip("\n") + "\n\n" + entry
    BLOCKS_MD.write_text(text, encoding="utf-8", newline="\n")


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
    p += check_decisions(area)
    p += check_phase(area)
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
    problems = []
    for a in sel or areas():
        problems += check_area(a, keyidx)
    _, bp = parse_blocks()
    problems += bp
    return problems


def unresolved_cites():
    """ADVISORY ONLY. Ids written inside prose cells are documentation, not structure:
    a cite that no longer resolves is worth knowing about and must never refuse a commit.
    Structural references are the `ref` column in _schema.csv, which `check` does enforce
    exactly. This scan is deliberately narrow - D- with three digits and BLK- - because
    this car's own diagrams use two-digit codes like D-01 and B-12 for components."""
    known = set()
    for a in areas():
        _, rows = read_table(a, "decisions")
        known |= {(r.get("id") or "").strip() for r in rows}
    for d in (ROOT / "99-ARCHIVE").rglob("D-*.md"):
        known.add(d.stem)
    known |= {b["id"] for b in parse_blocks()[0]}
    out = []
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
        print(line)
    print(f"BLOCKS   {len(stuck)} unanswered, {len(waiting)} answered and not yet applied")
    for b in stuck:
        print(f"  {b['id']} {b['area']}: {b['fields'].get('Ask','')[:88]}")
    for b in waiting:
        print(f"  {b['id']} {b['area']}: ANSWERED - apply it")
    if problems:
        return RC_INVALID
    if waiting or stuck:
        return RC_WAITING
    return RC_OK


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


def cmd_new(args):
    a = resolve_area(args.area)
    hdr, rows = read_table(a, "decisions")
    nums = [int(m.group(1)) for m in (re.match(r"D-(\d+)$", (r.get("id") or "")) for r in rows) if m]
    for d in (ROOT / "99-ARCHIVE").rglob("D-*.md"):
        m = re.match(r"D-(\d+)$", d.stem)
        if m:
            nums.append(int(m.group(1)))
    for other in areas():
        if other == a:
            continue
        _, orows = read_table(other, "decisions")
        for r in orows:
            m = re.match(r"D-(\d+)$", (r.get("id") or ""))
            if m:
                nums.append(int(m.group(1)))
    nid = f"D-{max(nums, default=0) + 1:03d}"
    vals = _pairs(args.pairs)
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


def cmd_cites(args):
    out = unresolved_cites()
    for x in out:
        print(x)
    print(f"({len(out)} unresolved cite(s) in prose - advisory, nothing is refused)")
    return RC_WAITING if out else RC_OK


def cmd_block(args):
    blocks, problems = parse_blocks()
    if problems:
        for x in problems:
            print(x)
        die("BLOCKS.md does not parse - fix it before adding a block (nothing was written)")
    n = next_block_num(blocks)
    append_block(n, args.area or "-", args.ask)
    print(f"BLK-{n:03d} appended to BLOCKS.md - fill in Why / Options / Recommend / Stops")
    return RC_OK


def cmd_blocks(args):
    blocks, problems = parse_blocks()
    for x in problems:
        print(x)
    if problems:
        return RC_INVALID
    sel = [b for b in blocks if b["section"] == ("SOLVED" if args.solved else "OPEN")]
    if args.answered:
        sel = [b for b in blocks if b["section"] == "OPEN" and b["solution"]]
    for b in sel:
        print(f"{b['id']} · {b['area'] or '-'} · {'answered' if b['solution'] else 'waiting'}")
        print(f"   ask:   {b['fields'].get('Ask','')}")
        if b["solution"]:
            print(f"   solve: {b['solution']}")
    print(f"({len(sel)} block(s))")
    return RC_OK if sel else RC_WAITING


def cmd_log(args):
    a = resolve_area(args.area)
    hdr, rows = read_table(a, "log")
    hdr = hdr or ["id", "date", "kind", "what", "refs"]
    nums = [int(m.group(1)) for m in (re.match(r"L-(\d+)$", (r.get("id") or "")) for r in rows) if m]
    nid = f"L-{max(nums, default=0) + 1:04d}"
    rows.append({"id": nid, "date": today(), "kind": args.kind, "what": args.what, "refs": args.refs or ""})
    write_table(a, "log", hdr, rows)
    print(f"{nid} logged")
    return RC_OK


# ------------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(prog="rx7", description=__doc__.splitlines()[0])
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

    p = sub.add_parser("cites", help="advisory: prose cites that no longer resolve (never refuses)")
    p.set_defaults(fn=cmd_cites)

    p = sub.add_parser("block", help="append a new block to BLOCKS.md")
    p.add_argument("ask"); p.add_argument("-p", "--area")
    p.set_defaults(fn=cmd_block)

    p = sub.add_parser("blocks", help="list blocks")
    p.add_argument("--solved", action="store_true")
    p.add_argument("--answered", action="store_true", help="open blocks Camden has answered")
    p.set_defaults(fn=cmd_blocks)

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
    sys.exit(main())

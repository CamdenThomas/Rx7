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

THERE ARE NO PAGES (D-405). Blocks are rows in `blocks`, Camden's answers are
rows in `inbox`, decisions carry their text in `decisions.body`. The Rx7 app
reads all of it through `export` and writes his answers through `answer`.

NO COUNTERS ARE EVER STORED. The next D- is max(decisions.id)+1; the next
block in a project is the highest <prefix>.<n> that project has ever used, +1.
A stored counter can disagree with reality; a derived one cannot.

EXIT CODES ARE THE ONLY SIGNAL A CALLER MAY BRANCH ON:
    0  valid / done
    1  invalid - the record contradicts itself. The ONLY code that blocks a commit.
    2  nothing to do, or something is waiting on a person. Advisory. Blocks nothing.
    3  a usage error or a crash in this tool - never a verdict on the record.
Never branch on this tool's words, and never grep its output. If a caller needs
a machine-readable fact it does not have, add a command or a column: `export`
is the machine-readable view of everything.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import io
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 3 is a usage error or a crash in this tool: never "the record contradicts itself" (§1),
# so a hook that blocks only on 1 cannot be tripped by a typo or a missing interpreter.
RC_OK, RC_INVALID, RC_WAITING, RC_USAGE = 0, 1, 2, 3

PHASES = ("PERMANENT", "PROPOSED", "PLANNING", "SOURCING", "BUILDING", "COMPLETE")
# `inherited` is a decision this project reads but another project owns.
DEC_STATUS = ("standing", "superseded", "withdrawn", "inherited")
WORK_STATE = ("open", "done", "blocked", "dropped")
WORK_OWNER = ("agent", "camden")
# How Camden answers a work row in the app (D-406): a check, a measured value, or a choice.
WORK_REPLY = ("check", "value", "choice")
INBOX_KIND = ("block", "pick", "work", "run", "project", "drive", "note")
INBOX_DEVICE = ("desktop", "phone")
RUN_WORKFLOWS = ("apply", "plan", "review", "parts")
# Log drive and Set odo in the Manual (D-417): the target names the moment, the choice is the
# odometer reading. drive- is a drive he logged; odo- is a reading with nothing else known.
DRIVE_TARGET_RE = re.compile(r"^(drive|odo)-\d{8}T\d{6}$")
# A note he makes on words he selected in the Manual (D-426): a log, never applied. The
# target names the moment; `context` says where he was and what he selected.
NOTE_TARGET_RE = re.compile(r"^note-\d{8}T\d{6}$")
# Kinds the agent applies; a note stays in the inbox as his log until he deletes it (D-426).
APPLIED_KINDS = tuple(k for k in INBOX_KIND if k != "note")


def waiting(rows):
    """The inbox rows that wait to be applied: every one but his notes (D-426)."""
    return [r for r in rows if (r.get("kind") or "").strip() in APPLIED_KINDS]

# Columns whose vocabulary THIS TOOL owns, not the project. Every area's _schema.csv must
# declare exactly these, so the same column cannot mean different things in two projects.
# (Inferring them per project from the values that happened to exist produced four false
# refusals on 2026-09-11 - `blocked` work, a `standing` 02-engine decision. R7.)
VOCAB = {
    ("decisions", "status"): "enum(" + "|".join(sorted(DEC_STATUS)) + ")",
    ("work", "state"): "enum(" + "|".join(sorted(WORK_STATE)) + ")",
    ("work", "owner"): "enum(" + "|".join(sorted(WORK_OWNER)) + ")",
    ("work", "reply"): "enum(" + "|".join(sorted(WORK_REPLY)) + ")",
    ("inbox", "kind"): "enum(" + "|".join(sorted(INBOX_KIND)) + ")",
    ("inbox", "device"): "enum(" + "|".join(sorted(INBOX_DEVICE)) + ")",
}

# Tables whose columns the tool and the app depend on. An area that declares one must declare
# every one of these columns (it may add its own).
TOOL_COLUMNS = {
    "blocks": ("id", "title", "opened", "ask", "why", "options", "recommend", "stops"),
    "inbox": ("id", "target", "kind", "choice", "text", "context", "device", "at"),
    "decisions": ("id", "system", "title", "date", "status", "supersedes", "superseded_by",
                  "closes", "also", "body"),
}
INBOX_COLUMNS = TOOL_COLUMNS["inbox"]

# A folder table keeps one row per file, data/<table>/<key>.csv, so two writers - the phone
# committing through GitHub and the desktop committing through git - never touch the same
# file and can never conflict (D-405). Only the tool may declare one.
FOLDER_TABLES = ("inbox",)
FILE_KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._~-]*$")

DATE_RE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})?$")
ID_RE = re.compile(r"^[A-Z]{1,4}-\d{1,4}$")
# Blocks are numbered per project, <prefix>.<n>: `01.12` is the twelfth block raised for
# 02-PROJECTS/01-electrical, `02.07` the seventh for 03-luxury (D-356). The prefix is
# the project directory's two-digit number; 00-CAR and 01-REFERENCE would collide with
# 00 and 01, so theirs are CAR and REF. The number has at least two digits, so no id is
# shorter than `00.01` — but a bare `13.80` in prose is a voltage, so a block id is only
# recognised where it is structure: a `blocks` key, `closes`, a gate. Never in prose.
# Blocks were BLK-### until 2026-09-21; each old id is a `retired` row in its project.
# The projects moved up one number on 2026-09-25 (D-427): a block id in a decision written
# before then keeps its old project, and next_block_id never repeats it. Engine and luxury
# then swapped to 02 and 03, and the app left the projects for 02-APP, prefix APP (D-428).
BLOCK_ID_RE = re.compile(r"^(\d{2}|CAR|REF|APP)\.(\d{2,3})$")
BLOCK_PREFIX_FIXED = {"00-CAR": "CAR", "01-REFERENCE": "REF", "02-APP": "APP"}
# Prose cites are checked by `rx7.py cites` (advisory), never by `check`. D- only, three
# digits only, because this car's factory diagrams use D-01 and B-12 as component codes.
CITE_RE = re.compile(r"\b(D-\d{3})\b")
# One option per line in blocks.options, each `(a) …` - the app shows each as a button.
OPTION_RE = re.compile(r"^\(([a-z])\)\s+(\S.*)$")
DECISION_STUB = "**Decision.** \n\n**Why.** \n\n**In the data.** "
STUB_RE = re.compile(r"\*\*Decision\.\*\*\s*\*\*Why\.\*\*")


def today() -> str:
    return datetime.date.today().isoformat()


def now_iso() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def rel(p: Path) -> str:
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def natural(s: str):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", s or "")]


# --------------------------------------------------------------------------- IO

def read_csv_text(text: str):
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return [], []
    hdr = [c.strip() for c in rows[0]]
    body = []
    for r in rows[1:]:
        if not any((c or "").strip() for c in r):
            continue
        body.append(list(r) + [""] * (len(hdr) - len(r)))
    return hdr, body


def read_csv_rows(p: Path):
    if not p.exists():
        return [], []
    return read_csv_text(p.read_text(encoding="utf-8-sig"))


def folder_files(area: Path, table: str):
    d = area / "data" / table
    return sorted(d.glob("*.csv")) if d.is_dir() else []


def read_table(area: Path, table: str):
    if table in FOLDER_TABLES:
        hdr, rows = [], []
        for f in folder_files(area, table):
            h, body = read_csv_rows(f)
            hdr = hdr or h
            rows += [dict(zip(h, r)) for r in body]
        return hdr or list(TOOL_COLUMNS.get(table, ())), rows
    hdr, body = read_csv_rows(area / "data" / f"{table}.csv")
    return hdr, [dict(zip(hdr, r)) for r in body]


def csv_text(hdr, dicts) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(hdr)
    for d in dicts:
        w.writerow([(d.get(c, "") or "") for c in hdr])
    return buf.getvalue()


def write_atomic(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(p)


def write_table(area: Path, table: str, hdr, dicts) -> None:
    # A key the header does not have would be dropped without a word — which is exactly how
    # `log` wrote nothing but ids and dates from v3's first run to 2026-09-21. Refuse it.
    stray = sorted({k for d in dicts for k in d if k not in hdr})
    if stray:
        die(f"{rel(area)}/data/{table}: refusing to write columns the header does not have: "
            f"{', '.join(stray)} (nothing was written)")
    if table in FOLDER_TABLES:
        # One file per row, named by its key (the first column). Only rows that changed are
        # written, and only files whose row is gone are removed.
        d, key = area / "data" / table, hdr[0]
        keep = set()
        for row in dicts:
            k = (row.get(key) or "").strip()
            if not FILE_KEY_RE.match(k):
                die(f"{rel(d)}: {k!r} cannot be a file name (nothing was written)")
            keep.add(k)
            p, text = d / f"{k}.csv", csv_text(hdr, [row])
            if not p.exists() or p.read_text(encoding="utf-8") != text:
                write_atomic(p, text)
        for f in folder_files(area, table):
            if f.stem not in keep:
                f.unlink()
        return
    write_atomic(area / "data" / f"{table}.csv", csv_text(hdr, dicts))


def areas():
    out = []
    for p in sorted(ROOT.rglob("data/_tables.csv")):
        if "99-ARCHIVE" in p.parts or ".git" in p.parts or "node_modules" in p.parts:
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


def project_kv(area: Path) -> dict:
    _, rows = read_table(area, "_project")
    return {(r.get("key") or "").strip(): (r.get("value") or "").strip() for r in rows}


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
    elif typ == "datetime":
        if not DATETIME_RE.match(v):
            return "is not a date and time (YYYY-MM-DDTHH:MM:SS+hh:mm)"
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
#
# A block is a row in its project's `blocks` table: id, title, opened, ask, why, options,
# recommend, stops. It stays until a decision closes it, and is then deleted (§4) — the
# decision is where a settled question lives. His answer is never in this table: it is an
# `inbox` row until the agent has applied it.

def block_prefix(area: Path):
    """The block-id prefix an area owns: CAR, REF, or a project's two-digit number."""
    if area.name in BLOCK_PREFIX_FIXED:
        return BLOCK_PREFIX_FIXED[area.name]
    m = re.match(r"^(\d{2})-", area.name)
    return m.group(1) if m and area.parent.name == "02-PROJECTS" else None


def prefix_areas():
    """{prefix: area} — the only map from a block id to the project it belongs to."""
    return {p: a for a in areas() if (p := block_prefix(a))}


def parse_options(cell: str):
    """[(letter, text)] from blocks.options, or None if any line is not `(x) text`."""
    out = []
    for line in (cell or "").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("- "):
            s = s[2:].strip()
        m = OPTION_RE.match(s)
        if not m:
            return None
        out.append((m.group(1), m.group(2).strip()))
    return out


def recommended_letter(recommend: str, letters) -> str:
    """The option the Recommend line names first, if it names one: `(a), unless …` → a."""
    for m in re.finditer(r"\(([a-z])\)", recommend or ""):
        if m.group(1) in letters:
            return m.group(1)
    return ""


def open_blocks():
    """Every block row in the tree, each with its area."""
    out = []
    for a in areas():
        for r in read_table(a, "blocks")[1]:
            if (r.get("id") or "").strip():
                out.append(dict(r, _area=a))
    return out


def _closes_tokens(path: Path):
    """Every token in the `closes` column of one decisions.csv."""
    hdr, body = read_csv_rows(path)
    if "closes" not in hdr:
        return []
    i = hdr.index("closes")
    return [t for row in body if len(row) > i for t in re.split(r"[\s,;·]+", row[i]) if t]


def next_block_id(prefix: str) -> str:
    """The highest number this project has ever used, plus one — derived, never stored (R5).

    A block is DELETED once its answer is a decision, so the table alone no longer knows how
    high a project's numbering went: the decisions do, in `closes` — including the decisions
    of a project that has since been archived. Counting only the table would hand out 00.05
    twice, and an id that means two things is the one mistake this record cannot recover from."""
    toks = [(r.get("id") or "").strip() for r in open_blocks()]
    files = [a / "data" / "decisions.csv" for a in areas()]
    files += list((ROOT / "99-ARCHIVE").rglob("decisions.csv"))
    toks += [t for f in files for t in _closes_tokens(f)]
    # A block withdrawn WITHOUT a decision (moot, merged) leaves no `closes`; its id goes
    # into `retired` as a term so the number is still never handed out again.
    for f in [a / "data" / "retired.csv" for a in areas()] + list((ROOT / "99-ARCHIVE").rglob("retired.csv")):
        hdr, body = read_csv_rows(f)
        if "term" in hdr:
            toks += [row[hdr.index("term")].strip() for row in body]
    highest = 0
    for tok in toks:
        m = BLOCK_ID_RE.match(tok)
        if m and m.group(1) == prefix:
            highest = max(highest, int(m.group(2)))
    return f"{prefix}.{highest + 1:02d}"


# ------------------------------------------------------------------------- inbox
#
# Camden's answers, one row per answer per device, each in its own file (D-405). Written by
# `answer` on the desktop and by the same function on the phone, which runs this file in the
# app. Deleted only by the agent, once his words are saved in the decision or row they rule.

def inbox_entry(target: str, device: str, kind: str, choice: str = "", text: str = "",
                context: str = "", at: str = ""):
    """(id, file text) for one answer. Pure: validates the shape, touches no file."""
    if kind not in INBOX_KIND:
        raise ValueError(f"kind must be one of {'/'.join(INBOX_KIND)}")
    if device not in INBOX_DEVICE:
        raise ValueError(f"device must be one of {'/'.join(INBOX_DEVICE)}")
    iid = f"{target}~{device}"
    if not FILE_KEY_RE.match(iid):
        raise ValueError(f"{target!r} cannot be answered - not a plain id")
    if not (choice or "").strip() and not (text or "").strip():
        raise ValueError("an answer needs a choice or some words")
    at = at or now_iso()
    if not DATETIME_RE.match(at):
        raise ValueError(f"{at!r} is not a date and time")
    row = {"id": iid, "target": target, "kind": kind, "choice": choice.strip(), "text": text,
           "context": context, "device": device, "at": at}
    return iid, csv_text(list(INBOX_COLUMNS), [row])


def resolve_target(area: Path, target: str, kind: str = ""):
    """(kind, row) for what an answer targets in this area, or raise ValueError saying why."""
    if kind in ("run", "project"):
        if kind == "run" and target not in RUN_WORKFLOWS:
            raise ValueError(f"a run is one of {'/'.join(RUN_WORKFLOWS)}")
        if kind == "project" and not re.match(r"^[a-z0-9][a-z0-9-]*$", target):
            raise ValueError("a new project's name is lowercase words joined by -")
        return kind, {}
    if kind == "drive" or (not kind and DRIVE_TARGET_RE.match(target)):
        if not DRIVE_TARGET_RE.match(target):
            raise ValueError("a drive is drive-<YYYYMMDDTHHMMSS> or odo-<YYYYMMDDTHHMMSS>")
        if not (area / "data" / "drives.csv").exists():
            raise ValueError(f"{rel(area)} keeps no drives - they belong to 00-CAR")
        return "drive", {}
    if kind == "note" or (not kind and NOTE_TARGET_RE.match(target)):
        if not NOTE_TARGET_RE.match(target):
            raise ValueError("a note is note-<YYYYMMDDTHHMMSS>")
        if not (area / "data" / "parts.csv").exists():
            raise ValueError(f"{rel(area)} holds no Manual - notes belong to 00-CAR")
        return "note", {}
    if BLOCK_ID_RE.match(target):
        for r in read_table(area, "blocks")[1]:
            if (r.get("id") or "").strip() == target:
                return "block", r
        raise ValueError(f"{target} is not an open block in {rel(area)}")
    for t, k in (("picks", "pick"), ("work", "work")):
        if (area / "data" / f"{t}.csv").exists():
            for r in read_table(area, t)[1]:
                if (r.get("id") or "").strip() == target:
                    return k, r
    raise ValueError(f"{target} is no block, pick or work row in {rel(area)}")


def check_choice(kind: str, row: dict, choice: str):
    """Why this choice cannot answer that row, or None."""
    c = (choice or "").strip()
    if kind == "drive" and not c:
        return "a drive needs the odometer reading"
    if not c:
        return None
    if kind == "block":
        letters = [x for x, _ in parse_options(row.get("options", "")) or []]
        return None if c in letters else f"{c!r} is not one of the options {', '.join(letters)}"
    if kind == "pick":
        return None if c in ("yes", "no", "question") else "a pick is answered yes, no or question"
    if kind == "drive":
        return None if re.fullmatch(r"[1-9]\d{0,6}", c) else "an odometer reading is whole miles"
    if kind == "work":
        reply = (row.get("reply") or "check").strip() or "check"
        if reply == "check" and c not in ("done", "not done"):
            return "a check is answered done or not done"
        if reply == "choice":
            opts = split_choices(row.get("choices", ""))
            if c not in opts:
                return f"{c!r} is not one of {', '.join(opts)}"
    return None


def split_choices(cell: str):
    return [x.strip() for x in (cell or "").split("|") if x.strip()]


# ------------------------------------------------------------------------- gates
#
# `work.gate` holds REFERENCES, all of which must be met before the row can be started.
# Nothing else: prose belongs in `note`. The references, resolved across the whole tree:
#
#   D-274                 met when that decision is standing or inherited
#   01.07                 met when that block is gone from `blocks` and a decision names it
#                         in `closes` — i.e. it has been answered and applied
#   A5                    met when that work row is done or dropped, in this area
#   03-luxury:F-012  the same, in another area (work ids are only unique per area)
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
    """Every gate-addressable fact in the tree, read straight from the CSVs.

    {"decisions": {id: status}, "blocks": {id: "OPEN"}, "phase": {area: phase},
     "work": {(area, id): state}, "work_ids": {id: [area…]}, "row": {(area, id): row}}
    """
    global _TREE
    if _TREE is not None and not fresh:
        return _TREE
    idx = {"decisions": {}, "blocks": {}, "phase": {}, "work": {}, "work_ids": {}, "row": {}}
    for a in areas():
        name = a.name
        idx["phase"][name] = project_kv(a).get("phase", "")
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
        for r in read_table(a, "blocks")[1]:
            if (r.get("id") or "").strip():
                idx["blocks"][r["id"].strip()] = "OPEN"
    # A block leaves `blocks` the moment its answer is a decision, so "was it answered?" is
    # whether a decision says it closed it. That is the one home for the fact (R2), and it is
    # why a gate on a removed block still resolves. Only a STANDING (or inherited) decision
    # closes a block (§4), and a project that has been archived still closed what it closed.
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
        return False, f"? {ref} is no open block and no decision closes it"
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
    return False, (f"? {ref!r} is not a reference — a gate holds D-/block/work ids and "
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
    folders = {t for t in FOLDER_TABLES if (area / "data" / t).is_dir()}
    for t in sorted(files - set(tables)):
        p.append(f"{rel(area)}: data/{t}.csv exists but {t!r} is not declared in _tables.csv")
    for t in sorted(folders - set(tables)):
        p.append(f"{rel(area)}: data/{t}/ exists but {t!r} is not declared in _tables.csv")
    for t in sorted(set(tables) - files - set(FOLDER_TABLES)):
        p.append(f"{rel(area)}: _tables.csv declares {t!r} but data/{t}.csv does not exist")
    for t in sorted(files & set(FOLDER_TABLES)):
        p.append(f"{rel(area)}: {t} keeps one row per file in data/{t}/, not in data/{t}.csv")

    for t in sorted(set(tables) & (files | set(FOLDER_TABLES))):
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
        declared = [c["column"] for c in spec]
        for c in TOOL_COLUMNS.get(t, ()):
            if c not in declared:
                p.append(f"{rel(area)}:_schema: {t} must declare {c!r} - the tool and the app read it")
        if t in FOLDER_TABLES:
            if declared[0] != kc:
                p.append(f"{rel(area)}:_schema: {t}'s key must be its first column (it names the file)")
            p += check_folder(area, t, declared, kc)
        hdr, rows = read_table(area, t)
        want = set(declared)
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
        if t not in FOLDER_TABLES:
            # A row with more cells than its header loses them on the next write (read_table
            # zips to the header), so it is refused while the cells are still there to rescue.
            _raw_hdr, raw_body = read_csv_rows(area / "data" / f"{t}.csv")
            for i, raw in enumerate(raw_body, start=2):
                if len(raw) > len(_raw_hdr) and any(x.strip() for x in raw[len(_raw_hdr):]):
                    p.append(f"{rel(area)}:{t} line {i}: {len(raw)} cells under a {len(_raw_hdr)}-column "
                             "header - the extra cells would be lost on the next write")
        if t == "blocks":
            p += check_blocks(area, rows)
        if t == "inbox":
            p += check_inbox(area, rows)
        if t in ("decisions", "log", "retired", "inbox"):
            continue
        for r in rows:
            k = (r.get(kc) or "").strip()
            for col, v in r.items():
                v = v or ""
                # §6.6: 00-CAR states what IS, never how it was decided.
                if block_prefix(area) == "CAR" and t != "blocks":
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


def check_folder(area: Path, t: str, declared, kc) -> list[str]:
    """Each file of a folder table is one row, under the declared header, named by its key."""
    p = []
    for f in folder_files(area, t):
        hdr, body = read_csv_rows(f)
        where = rel(f)
        if set(hdr) != set(declared):
            p.append(f"{where}: its header is not {t}'s declared columns")
            continue
        if len(body) != 1:
            p.append(f"{where}: holds {len(body)} rows - a {t} file holds exactly one")
            continue
        key = body[0][hdr.index(kc)].strip()
        if key != f.stem:
            p.append(f"{where}: its {kc} is {key!r} - the file must be named {key}.csv")
    return p


def check_blocks(area: Path, rows) -> list[str]:
    """The clarity bar (§4): every block answerable from its row alone."""
    p, px = [], block_prefix(area)
    closed = tree_index().get("blocks_closed", set())
    for r in rows:
        bid = (r.get("id") or "").strip()
        m = BLOCK_ID_RE.match(bid)
        if not m:
            p.append(f"{rel(area)}:blocks:{bid}: not a block id (<prefix>.<nn>, D-356)")
            continue
        if m.group(1) != px:
            p.append(f"{rel(area)}:blocks:{bid}: this area's blocks are {px}.<nn>")
        opts = parse_options(r.get("options", ""))
        if opts is None:
            p.append(f"{rel(area)}:blocks:{bid}: options must be one per line, each starting "
                     "(a) , (b) … - the app shows each as a button")
        elif len(opts) < 2:
            p.append(f"{rel(area)}:blocks:{bid}: a block offers at least two options")
        elif [x for x, _ in opts] != [chr(ord("a") + i) for i in range(len(opts))]:
            p.append(f"{rel(area)}:blocks:{bid}: options are lettered (a), (b), (c) … in order")
        for col in ("ask", "why", "options", "recommend", "stops", "title"):
            if "TO WRITE" in (r.get(col) or ""):
                p.append(f"{rel(area)}:blocks:{bid}: {col} still says TO WRITE")
        if bid in closed:
            p.append(f"{rel(area)}:blocks:{bid}: a standing decision closes it - delete the block (§4)")
    return p


def check_inbox(area: Path, rows) -> list[str]:
    p = []
    for r in rows:
        iid = (r.get("id") or "").strip()
        want = f"{(r.get('target') or '').strip()}~{(r.get('device') or '').strip()}"
        if iid != want:
            p.append(f"{rel(area)}:inbox:{iid}: its id must be <target>~<device> ({want})")
        if not (r.get("choice") or "").strip() and not (r.get("text") or "").strip():
            p.append(f"{rel(area)}:inbox:{iid}: holds neither a choice nor any words")
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
    if not (area / "data" / "decisions.csv").exists():
        return p
    _, rows = read_table(area, "decisions")
    for r in rows:
        i = (r.get("id") or "").strip()
        if not i:
            continue
        st = (r.get("status") or "").strip()
        body = (r.get("body") or "").strip()
        # Only a standing decision must have a body. A superseded, withdrawn or inherited
        # row is allowed to be a tombstone: the id is reserved, the reasoning lives in the
        # decision that replaced it.
        if st == "standing" and not body:
            p.append(f"{rel(area)}:decisions:{i}: standing, but its body is empty")
        if st == "standing" and STUB_RE.search(body):
            p.append(f"{rel(area)}:decisions:{i}: standing, but its body is still the empty "
                     "stub `rx7.py new` wrote - write it or withdraw it")
        if st == "superseded" and not (r.get("superseded_by") or "").strip():
            p.append(f"{rel(area)}:decisions:{i}: superseded with no superseded_by")
    if (area / "data" / "decisions").is_dir():
        p.append(f"{rel(area)}: data/decisions/ exists - decision text lives in decisions.body (D-405)")
    return p


def check_phase(area: Path) -> list[str]:
    ph = project_kv(area).get("phase", "")
    if ph and ph not in PHASES:
        return [f"{rel(area)}:_project: phase {ph!r} is not one of " + "/".join(PHASES)]
    return []


def run_check(sel=None):
    keyidx = load_keys()
    tree_index(fresh=True)
    problems = []
    for a in sel or areas():
        problems += check_area(a, keyidx)
    problems += check_supersedes()
    seen_prefix = {}
    for a in areas():
        px = block_prefix(a)
        if px and px in seen_prefix:
            problems.append(f"{rel(a)} and {rel(seen_prefix[px])} both own block prefix {px!r} - "
                            "their block ids would collide; renumber one directory")
        elif px:
            seen_prefix[px] = a
    for stray in ("BLOCKS.md", "DECISIONS.md"):
        if (ROOT / stray).exists():
            problems.append(f"{stray} exists - blocks and decisions live in the record now (D-405)")
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


def archived_decision_ids():
    ids = set()
    for d in (ROOT / "99-ARCHIVE").rglob("D-*.md"):
        ids.add(d.stem)
    for f in (ROOT / "99-ARCHIVE").rglob("decisions.csv"):
        hdr, body = read_csv_rows(f)
        if "id" in hdr:
            ids |= {row[hdr.index("id")].strip() for row in body}
    return ids


def unresolved_cites():
    """ADVISORY ONLY. Ids written inside prose cells are documentation, not structure:
    a cite that no longer resolves is worth knowing about and must never refuse a commit.
    Structural references are the `ref` column in _schema.csv, which `check` does enforce
    exactly. This scan is deliberately narrow - D- with three digits only - because this
    car's own diagrams use two-digit codes like D-01 and B-12 for components, and a block
    id like `00.18` cannot be told from a number in prose, so it is not scanned at all."""
    known = archived_decision_ids()
    for a in areas():
        _, rows = read_table(a, "decisions")
        known |= {(r.get("id") or "").strip() for r in rows}
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


# ------------------------------------------------------------------------- views
#
# What the app shows, computed from the record each time and never stored: the working order
# of each project's work, what holds each row, and the links between decisions. Reads every
# area's work, blocks, inbox, picks, parts, decisions and log; writes nothing.

def work_view(a: Path, idx) -> list[dict]:
    """Every work row of one area with its status, what holds it, and its place in the
    working order. Reads work and _project, plus the tree index for gates.

    Working order: a row comes after everything its gate names. A project whose work has a
    `track` column has two tracks, design and build (D-386 → D-405); each is split where the
    car comes apart and goes back together (D-387): design part 1 is the car whole, part 2
    starts at `car_apart`; build part 3 is the car apart, part 4 starts at `car_back`."""
    hdr, rows = read_table(a, "work")
    rows = [r for r in rows if (r.get("id") or "").strip()]
    by_id = {r["id"].strip(): r for r in rows}
    kv = project_kv(a)
    titles = {(r.get("id") or "").strip(): (r.get("title") or "").strip()
              for r in read_table(a, "blocks")[1]}
    answered = {(r.get("target") or "").strip() for ar in areas() for r in read_table(ar, "inbox")[1]}

    def status(r):
        st = (r.get("state") or "").strip()
        if st in ("done", "dropped"):
            return st
        met, _, _ = gate_state(r.get("gate", ""), a.name, idx)
        return "ready" if st == "open" and met else "waiting"

    stat = {w: status(r) for w, r in by_id.items()}
    memo = {}

    def depth(wid, seen=()):
        # Phase gates sit after the whole design; a gate on another area or a block is one step.
        if wid in memo:
            return memo[wid]
        if stat[wid] in ("ready", "done", "dropped"):
            memo[wid] = 0
            return 0
        d = 1
        for ref in parse_gate(by_id[wid].get("gate", "")):
            if ref.startswith("phase:"):
                d = max(d, 50)
            elif ref in by_id and ref not in seen:
                d = max(d, 1 + depth(ref, seen + (wid,)))
        memo[wid] = d
        return d

    def blockers(w):
        r, out = by_id[w], []
        for ref in parse_gate(r.get("gate", "")):
            ok, why = gate_ref_state(ref, a.name, idx)
            if ok:
                continue
            if why.startswith("?"):
                out.append({"ref": ref, "kind": "bad", "label": why[2:]})
            elif ref.startswith("phase:"):
                out.append({"ref": ref, "kind": "phase", "label": why,
                            "freeze": ref[6:].upper() == "SOURCING"})
            elif ref in by_id:
                out.append({"ref": ref, "kind": "work", "label": (by_id[ref].get("item") or "").strip(),
                            "owner": (by_id[ref].get("owner") or "").strip(), "state": stat[ref]})
            elif ref in idx["blocks"]:
                out.append({"ref": ref, "kind": "block", "label": titles.get(ref, ""),
                            "answered": ref in answered})
            elif ":" in ref:
                other, wid = ref.split(":", 1)
                orow = idx["row"].get((other, wid), {})
                out.append({"ref": ref, "kind": "area-work", "area": other,
                            "label": (orow.get("item") or "").strip(),
                            "state": idx["work"].get((other, wid), "")})
            else:
                out.append({"ref": ref, "kind": "decision", "label": why})
        if not out and (r.get("state") or "").strip() == "blocked":
            out.append({"ref": "", "kind": "marked", "label": "marked blocked - see its note"})
        return out

    split = "track" in (hdr or [])

    def after(w, root, seen=()):
        if not root or w not in by_id:
            return False
        if w == root:
            return True
        return any(g in by_id and g not in seen and after(g, root, seen + (w,))
                   for g in parse_gate(by_id[w].get("gate", "")))

    apart_row, back_row = kv.get("car_apart", ""), kv.get("car_back", "")
    track = lambda w: ((by_id[w].get("track") or "design").strip() or "design") if split else ""

    def part(w):
        if not split:
            return 0
        if track(w) == "design":
            freeze = (by_id[w].get("stage") or "").strip() == "Z"
            return 2 if (apart_row and (after(w, apart_row) or freeze)) else 1
        return 4 if (back_row and after(w, back_row)) else 3

    info = {w: {"depth": depth(w), "track": track(w), "part": part(w)} for w in by_id}
    # Stages in the order their work can start: the stage's typical open row, not its earliest -
    # one early row must not pull the whole install stage ahead of the parts arriving.
    groups = {}
    for w in by_id:
        groups.setdefault((info[w]["track"], info[w]["part"], (by_id[w].get("stage") or "-").strip()), []).append(w)

    def stage_key(g):
        live = sorted(info[w]["depth"] for w in groups[g] if stat[w] in ("ready", "waiting"))
        return (g[0] != "design", g[1], 0 if live else 1, live[len(live) // 2] if live else 0, natural(g[2]))

    rank = {g: i for i, g in enumerate(sorted(groups, key=stage_key))}
    order = sorted(by_id, key=lambda w: (rank[(info[w]["track"], info[w]["part"],
                                                (by_id[w].get("stage") or "-").strip())],
                                          info[w]["depth"], natural(w)))
    # The design track reads in pure working order (his checklist, D-386); the build track and
    # an unsplit project read stage by stage. `order` is the second, `seq` the first.
    seq = {w: n for n, w in enumerate(sorted(by_id, key=lambda w: (
        info[w]["track"] != "design", info[w]["part"], info[w]["depth"], natural(w))))}
    out = []
    for n, w in enumerate(order):
        r = by_id[w]
        out.append({
            "area": a.name, "id": w, "order": n, "seq": seq[w],
            "stage": (r.get("stage") or "").strip(), "stage_title": (r.get("stage_title") or "").strip(),
            "item": (r.get("item") or "").strip(), "owner": (r.get("owner") or "").strip(),
            "state": (r.get("state") or "").strip(), "status": stat[w],
            "gate": parse_gate(r.get("gate", "")), "blockers": blockers(w) if stat[w] == "waiting" else [],
            "note": (r.get("note") or "").strip(), "track": info[w]["track"], "part": info[w]["part"],
            "depth": info[w]["depth"],
            "reply": (r.get("reply") or "").strip() or "check",
            "choices": split_choices(r.get("choices", "")), "unit": (r.get("unit") or "").strip(),
        })
    # Stage titles belong to the stage, and only one row of a stage may carry it.
    stage_titles = {}
    for x in out:
        if x["stage_title"]:
            stage_titles.setdefault(x["stage"], x["stage_title"])
    for x in out:
        x["stage_title"] = stage_titles.get(x["stage"], "")
    return out


def export_data() -> dict:
    """Everything the Rx7 app shows, as one JSON-ready dict (R9: the app never reads words).
    Reads every table of every area, the archive's decision ids and 01-REFERENCE/photos;
    `manual` is manual_view() (D-417)."""
    problems = run_check()
    idx = tree_index()
    out = {"version": 1, "generated": now_iso(),
           "record": {"valid": not problems, "problems": problems[:100]},
           "areas": [], "blocks": [], "picks": [], "work": [], "decisions": [], "inbox": [],
           "log": [], "tables": [], "photos": [], "next": {}}
    structured = {"blocks", "inbox", "work", "decisions", "log", "retired", "picks"}
    cites_in = {}
    for a in areas():
        tables, cols = schema(a)
        kv = project_kv(a)
        kind = {"00-CAR": "car", "01-REFERENCE": "reference", "02-APP": "app"}.get(a.name, "project")
        meta = []
        for t in sorted(tables):
            spec = cols.get(t) or []
            hdr, rows = read_table(a, t)
            meta.append({"name": t, "purpose": (tables[t].get("purpose") or "").strip(),
                         "key": key_column(spec), "rows": len(rows),
                         "columns": [{k: (c.get(k) or "").strip() for k in
                                      ("column", "type", "required", "ref", "note")} for c in spec]})
            if t not in structured:
                out["tables"].append({"area": a.name, "table": t, "columns": hdr,
                                      "rows": [[r.get(c, "") for c in hdr] for r in rows]})
            for r in rows:
                for col, v in r.items():
                    for d in set(CITE_RE.findall(v or "")):
                        cites_in.setdefault(d, []).append({"area": a.name, "table": t,
                                                           "key": (r.get(key_column(spec) or "") or "").strip()})
        out["areas"].append({"path": rel(a), "name": a.name, "prefix": block_prefix(a) or "",
                             "kind": kind, "project": kv, "tables": meta})
        if block_prefix(a):
            out["next"][a.name] = next_block_id(block_prefix(a))
        for r in read_table(a, "inbox")[1]:
            out["inbox"].append(dict(r, area=a.name))
        for r in read_table(a, "log")[1][-40:]:
            out["log"].append(dict(r, area=a.name))
        if (a / "data" / "work.csv").exists():
            out["work"] += work_view(a, idx)
        for r in read_table(a, "decisions")[1]:
            i = (r.get("id") or "").strip()
            out["decisions"].append({
                "area": a.name, "id": i, "system": (r.get("system") or "").strip(),
                "title": (r.get("title") or "").strip(), "date": (r.get("date") or "").strip(),
                "status": (r.get("status") or "").strip(),
                "supersedes": CITE_RE.findall(r.get("supersedes") or ""),
                "superseded_by": (r.get("superseded_by") or "").strip(),
                "closes": [t for t in re.split(r"[\s,;·]+", r.get("closes") or "") if t],
                "also": (r.get("also") or "").strip(), "body": (r.get("body") or "").strip()})
        if (a / "data" / "picks.csv").exists():
            _, parts = read_table(a, "parts")
            part = {(p.get("id") or "").strip(): p for p in parts}
            for r in read_table(a, "picks")[1]:
                pr = part.get((r.get("part") or "").strip(), {})
                out["picks"].append(dict({k: (v or "").strip() for k, v in r.items()}, area=a.name,
                                         part_item=(pr.get("item") or "").strip(),
                                         part_spec=(pr.get("spec") or "").strip()))
    answered = {(e["area"], e["target"]) for e in out["inbox"]}
    for r in open_blocks():
        a = r["_area"]
        opts = parse_options(r.get("options", "")) or []
        bid = r["id"].strip()
        text = " ".join(r.get(c, "") or "" for c in ("ask", "why", "options", "recommend", "stops"))
        out["blocks"].append({
            "area": a.name, "id": bid, "title": (r.get("title") or "").strip(),
            "opened": (r.get("opened") or "").strip(), "age": days_since(r.get("opened", "")),
            "ask": (r.get("ask") or "").strip(), "why": (r.get("why") or "").strip(),
            "options": [{"letter": x, "text": t} for x, t in opts],
            "recommend": (r.get("recommend") or "").strip(),
            "recommended": recommended_letter(r.get("recommend", ""), [x for x, _ in opts]),
            "stops": (r.get("stops") or "").strip(),
            "touches": sorted(set(CITE_RE.findall(text)), key=natural),
            "unblocks": [{"area": ar, "id": w, "item": (row.get("item") or "").strip(),
                          "owner": (row.get("owner") or "").strip()}
                         for (ar, w), row in sorted(idx["row"].items())
                         if bid in parse_gate(row.get("gate", ""))],
            "answered": (a.name, bid) in answered})
    by_dec = {}
    for d in out["decisions"]:
        by_dec.setdefault(d["id"], []).append(d)
    for d in out["decisions"]:
        refs = cites_in.get(d["id"], [])
        d["cited_by"] = sorted({x["key"] for x in refs if x["table"] == "decisions" and x["key"] != d["id"]},
                               key=natural)
        d["cited_in"] = [x for x in refs if x["table"] != "decisions"][:60]
    photos = ROOT / "01-REFERENCE" / "photos"
    if photos.is_dir():
        out["photos"] = sorted(rel(p) for p in photos.rglob("*")
                               if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
    out["manual"] = manual_view()
    return out


# ------------------------------------------------------------------------ manual
#
# The Manual (D-417): one spine of verified facts about the car as it is now, and every screen
# a query over it. This is that query. The app shows only what comes out of here and computes
# nothing of its own; the phone runs this same function.
#
# A row reaches the Manual only when it is a backed fact about this car now (his 4.5):
#   - no shown cell still says `confirm` (R11's marker for a value nobody has checked),
#   - a spec is not `unverified`, and it is this car's figure (`applies` blank).
# `other-car` rows and the two above are HELD: they are listed with the reason, because they
# are what the verify work is made of. `replaced` and `not-fitted` rows are not facts about
# the car at all (his 5.6, 5.13) and are neither shown nor listed.

CONFIRM_RE = re.compile(r"\bconfirm\b", re.I)
MANUAL_SHOWN = {
    "vehicle": ("field", "value", "note"),
    "systems": ("name", "state", "since", "note"),
    "zones": ("name", "note"),
    "parts": ("name", "maker", "part_no", "factory_code", "link", "support", "note"),
    "specs": ("item", "value", "unit", "source", "page", "note"),
    "service": ("date", "mileage", "work", "notes"),
    "intervals": ("item", "every_miles", "every_months", "spec", "note"),
    "issues": ("issue", "status"),
    "drives": ("date", "odometer", "from", "to", "note"),
    "procedures": ("system", "title", "when", "tools"),
}
HELD_WHY = {"confirm": "marked confirm - not yet measured or checked on the car",
            "unverified": "its only source is not a factory document",
            "other-car": "another year's, trim's or gearbox's figure, and this car's differs or is in doubt"}
DUE_SOON_MILES, DUE_SOON_DAYS = 1000, 30


def manual_hold(table: str, row: dict):
    """'shown', 'gone' (not a fact about the car now) or a HELD_WHY key."""
    applies = (row.get("applies") or "").strip()
    if applies in ("replaced", "not-fitted"):
        return "gone"
    if applies == "other-car":
        return "other-car"
    if table == "specs" and (row.get("confidence") or "").strip() == "unverified":
        return "unverified"
    if any(CONFIRM_RE.search(row.get(c) or "") for c in MANUAL_SHOWN.get(table, ())):
        return "confirm"
    return "shown"


def _as_date(v: str):
    """A record date (YYYY-MM or YYYY-MM-DD) as a date; a month is its first day."""
    v = (v or "").strip()
    if not DATE_RE.match(v):
        return None
    y, m, *d = (int(x) for x in v.split("-"))
    return datetime.date(y, m, d[0] if d else 1)


def _int(v):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def odometer_now(drives, service, vehicle):
    """The newest odometer reading: a drive, a Set odo or a service visit, whichever is latest
    (on the same day, the higher reading). Only when none has one, vehicle.mileage."""
    seen = []
    for r in drives:
        if _int(r.get("odometer")) is not None and _as_date(r.get("date")):
            seen.append((_as_date(r["date"]), _int(r["odometer"]), (r.get("kind") or "drive").strip(), r["id"]))
    for r in service:
        if _int(r.get("mileage")) is not None and _as_date(r.get("date")):
            seen.append((_as_date(r["date"]), _int(r["mileage"]), "service", r["id"]))
    if seen:
        d, miles, source, ref = max(seen)
        return {"miles": miles, "date": d.isoformat(), "source": source, "ref": ref}
    v = next((r for r in vehicle if r.get("key") == "mileage"), {})
    miles = _int(v.get("value"))
    return {"miles": miles, "date": "", "source": "vehicle" if miles is not None else "", "ref": "mileage"}


def interval_due(iv: dict, service, odo: dict, today_d):
    """When an interval is next due, from the newest service visit whose `items` names it.
    status: overdue · soon · ok · never (no visit has done it) · each (no interval, e.g. every fill)."""
    every_mi = _int(iv.get("every_miles"))
    try:
        every_mo = float(iv.get("every_months") or "")
    except ValueError:
        every_mo = None
    last = None
    for r in service:
        if iv["id"] in (r.get("items") or "").split() and _as_date(r.get("date")):
            if last is None or _as_date(r["date"]) > _as_date(last["date"]):
                last = r
    out = {"last": None, "next_miles": None, "next_date": "", "status": "each"}
    if not every_mi and not every_mo:
        return out
    if not last:
        out["status"] = "never"
        return out
    out["last"] = {"service": last["id"], "date": last["date"], "miles": _int(last.get("mileage"))}
    if every_mi and out["last"]["miles"] is not None:
        out["next_miles"] = out["last"]["miles"] + every_mi
    if every_mo:
        out["next_date"] = (_as_date(last["date"]) + datetime.timedelta(days=round(every_mo * 30.44))).isoformat()
    miles_left = out["next_miles"] - odo["miles"] if out["next_miles"] is not None and odo.get("miles") is not None else None
    days_left = (datetime.date.fromisoformat(out["next_date"]) - today_d).days if out["next_date"] else None
    if (miles_left is not None and miles_left <= 0) or (days_left is not None and days_left <= 0):
        out["status"] = "overdue"
    elif (miles_left is not None and miles_left <= DUE_SOON_MILES) or (days_left is not None and days_left <= DUE_SOON_DAYS):
        out["status"] = "soon"
    else:
        out["status"] = "ok"
    out["miles_left"], out["days_left"] = miles_left, days_left
    return out


def manual_view(today_iso: str = "") -> dict:
    """The Manual, computed. Reads 00-CAR vehicle, systems, zones, parts, specs, service,
    intervals, issues, drives, procedures (and data/procedures/<id>.md), parts_history, and
    01-REFERENCE sources, circuits (and the factory-circuits files they name) and photos.
    Writes nothing (D-417)."""
    car = ROOT / "00-CAR"
    if not (car / "data" / "parts.csv").exists():
        return {}
    today_d = datetime.date.fromisoformat(today_iso) if today_iso else datetime.date.today()
    t = {n: read_table(car, n)[1] for n in ("vehicle", "systems", "zones", "parts", "specs", "service",
                                            "intervals", "issues", "drives", "procedures", "parts_history")}
    clean = lambda r: {k: (v or "").strip() for k, v in r.items()}
    held, shown = [], {}
    for name in MANUAL_SHOWN:
        shown[name] = []
        for r in map(clean, t[name]):
            why = manual_hold(name, r)
            if why == "shown":
                shown[name].append(r)
            elif why != "gone":
                label = r.get("item") or r.get("name") or r.get("field") or r.get("issue") or r.get("title") or ""
                held.append({"table": name, "key": next(iter(r.values()), ""), "label": label,
                             "reason": why, "why": HELD_WHY[why]})
    part_ids = {p["id"] for p in shown["parts"]}
    history = {r["id"]: clean(r) for r in t["parts_history"]}

    # each part's fitting is read from the service visit that fitted it (never typed)
    fitted = {}
    for s in sorted(shown["service"], key=lambda r: _as_date(r["date"]) or datetime.date.min):
        for pid in (s.get("fitted") or "").split():
            fitted[pid] = {"service": s["id"], "date": s["date"], "miles": _int(s.get("mileage"))}
    for p in shown["parts"]:
        p["fitted"] = fitted.get(p["id"])
        p["specs"] = [s["id"] for s in shown["specs"] if s.get("part") == p["id"]]
        p["service"] = [s["id"] for s in shown["service"] if p["id"] in (s.get("fitted") or "").split()]
        p["bought"] = [{"id": b, "part": history.get(b, {}).get("part", ""), "source": history.get(b, {}).get("source", "")}
                       for b in (p.get("bought") or "").split() if b in history]
    # layers (D-429): a part's parent is the part it sits in; its children are computed here
    for p in shown["parts"]:
        if p.get("parent") not in part_ids:
            p["parent"] = ""
    for p in shown["parts"]:
        p["children"] = [c["id"] for c in shown["parts"] if c.get("parent") == p["id"]]
    for s in shown["specs"]:
        if s.get("part") not in part_ids:
            s["part"] = ""
    for s in shown["service"]:
        s["fitted"] = [x for x in (s.get("fitted") or "").split() if x in part_ids]

    systems = sorted(shown["systems"], key=lambda r: (_int(r.get("order")) or 999, r["name"]))
    for s in systems:
        s["children"] = [c["id"] for c in systems if c.get("parent") == s["id"]]
        s["parts"] = [p["id"] for p in shown["parts"] if p["system"] == s["id"]]
        s["specs"] = len([x for x in shown["specs"] if x.get("system") == s["id"]])
    zones = sorted(shown["zones"], key=lambda r: (_int(r.get("order")) or 999, r["name"]))
    for z in zones:
        z["parts"] = [p["id"] for p in shown["parts"] if p.get("zone") == z["id"]]

    drives = sorted(shown["drives"], key=lambda r: (_as_date(r["date"]) or datetime.date.min, _int(r["odometer"]) or 0))
    prev = None
    for d in drives:
        d["miles"] = (_int(d["odometer"]) - prev) if prev is not None and _int(d["odometer"]) is not None else None
        prev = _int(d["odometer"]) if _int(d["odometer"]) is not None else prev
    odo = odometer_now(drives, shown["service"], t["vehicle"])

    intervals = []
    for iv in shown["intervals"]:
        intervals.append(dict(iv, due=interval_due(iv, shown["service"], odo, today_d)))
    rank = {"overdue": 0, "soon": 1, "never": 2, "ok": 3, "each": 4}
    intervals.sort(key=lambda iv: (rank[iv["due"]["status"]], iv["due"].get("next_date") or "9999"))

    for pr in shown["procedures"]:
        f = car / "data" / "procedures" / f"{pr['id']}.md"
        pr["body"] = f.read_text(encoding="utf-8") if f.exists() else ""

    ref = ROOT / "01-REFERENCE"
    sources = {r["id"]: {"title": (r.get("title") or "").strip(), "url": (r.get("url") or "").strip(),
                         "local_path": (r.get("local_path") or "").strip()}
               for r in read_table(ref, "sources")[1]} if (ref / "data" / "sources.csv").exists() else {}
    # each circuit write-up with the systems 01-REFERENCE files it under; a Markdown one
    # carries its text, since the app reads the tree only through this export
    circuits = []
    if (ref / "data" / "circuits.csv").exists():
        for r in map(clean, read_table(ref, "circuits")[1]):
            f = ref / "factory-circuits" / r["file"]
            if not f.exists():
                continue
            circuits.append({"file": r["file"], "path": rel(f), "title": r["title"], "systems": r["systems"].split(),
                             "source": r.get("source", ""), "note": r.get("note", ""),
                             "body": f.read_text(encoding="utf-8") if f.suffix.lower() == ".md" else ""})

    return {"today": today_d.isoformat(), "odometer": odo,
            "vehicle": [r for r in shown["vehicle"] if r.get("key") != "mileage"],
            "systems": systems, "zones": zones, "parts": shown["parts"], "specs": shown["specs"],
            "service": sorted(shown["service"], key=lambda r: _as_date(r["date"]) or datetime.date.min, reverse=True),
            "intervals": intervals, "issues": shown["issues"], "drives": list(reversed(drives)),
            "procedures": shown["procedures"], "sources": sources, "circuits": circuits, "held": held}


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
    problems = run_check()
    blocks = open_blocks()
    everything = [(a, r) for a in areas() for r in read_table(a, "inbox")[1]]
    inbox = [(a, r) for a, r in everything if r in waiting([r])]
    notes = len(everything) - len(inbox)
    answered = {(a.name, (r.get("target") or "").strip()) for a, r in inbox}
    idx = tree_index()
    print(f"RECORD   {'valid' if not problems else str(len(problems)) + ' problem(s)'}")
    for a in areas():
        kv = project_kv(a)
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
    stuck = [b for b in blocks if (b["_area"].name, b["id"].strip()) not in answered]
    print(f"BLOCKS   {len(stuck)} unanswered")
    for b in stuck:
        d = days_since(b.get("opened", ""))
        print(f"  {b['id']} {b['_area'].name}: {(b.get('ask') or '')[:80]}" + (f"  ({d}d)" if d is not None else ""))
    print(f"INBOX    {len(inbox)} answer(s) waiting to be applied")
    for a, r in inbox:
        print(f"  {r.get('target')} {a.name}: {r.get('kind')} from the {r.get('device')} {r.get('at', '')[:16]}")
    if notes:
        print(f"NOTES    {notes} of his notes in the Manual's log - kept, never applied (D-426)")
    if problems:
        return RC_INVALID
    if inbox or stuck:
        return RC_WAITING
    return RC_OK


def days_since(iso: str):
    """Whole days from an ISO date to today; None if the text is not a date."""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", (iso or "").strip())
    if not m:
        return None
    return (datetime.date.today() - datetime.date(*(int(x) for x in m.groups()))).days


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
    """col=value pairs. `col=@path` reads the value from a file (a decision body, a block's
    why); `col=@@text` is a value that really starts with @."""
    out = {}
    for it in items:
        if "=" not in it:
            die(f"{it!r} is not col=value")
        k, v = it.split("=", 1)
        if v.startswith("@@"):
            v = v[1:]
        elif v.startswith("@"):
            p = Path(v[1:]).expanduser()
            if not p.is_file():
                die(f"{k}=@{v[1:]}: no such file (nothing was written)")
            v = p.read_text(encoding="utf-8").strip("\n")
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
        show = lambda s: repr(s if len(s) <= 120 else s[:117] + "...")
        print(f"{args.table}:{args.key} {k}: {show(before[k])} -> {show(v)}")
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
    import sqlite3  # here, not at the top: the phone runs this file without sqlite3
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
        tables, cols = schema(a)
        for t in sorted(tables):
            kc = key_column(cols.get(t) or []) or ""
            for r in read_table(a, t)[1]:
                hits = [c for c, v in r.items() if needle in (v or "").lower()]
                if hits:
                    print(f"{rel(a)}:{t}:{(r.get(kc) or '').strip()} ({', '.join(hits)})")
                    n += 1
    print(f"({n} hit(s))")
    return RC_OK if n else RC_WAITING


def next_decision_id() -> str:
    """The highest D- anywhere in the tree or the archive, plus one (R5)."""
    nums = [int(m.group(1)) for i in archived_decision_ids() if (m := re.match(r"D-(\d+)$", i))]
    for a in areas():
        for r in read_table(a, "decisions")[1]:
            m = re.match(r"D-(\d+)$", (r.get("id") or "").strip())
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
    row = {c: vals.get(c, "") for c in (hdr or list(TOOL_COLUMNS["decisions"]))}
    row["id"] = nid
    row["date"] = vals.get("date", today())
    row["title"] = args.title
    row["status"] = vals.get("status", "standing")
    row["body"] = vals.get("body") or DECISION_STUB
    write_table(a, "decisions", hdr or list(row), rows + [row])
    if "body" in vals:
        print(f"{nid} written")
    else:
        print(f"{nid} reserved - write its body: rx7.py set {rel(a)} decisions {nid} body=@<file>")
    return RC_OK


def cmd_export(args):
    data = export_data()
    text = json.dumps(data, ensure_ascii=False, indent=1 if args.pretty else None,
                      separators=None if args.pretty else (",", ":"))
    if args.out:
        write_atomic(Path(args.out), text)
    else:
        sys.stdout.write(text)
    return RC_OK if data["record"]["valid"] else RC_INVALID


def cmd_answer(args):
    """Save one of Camden's answers into the area's inbox: data/inbox/<target>~<device>.csv.
    The desktop app calls this; the phone calls inbox_entry() itself. Reads blocks, picks and
    work to check the target; writes that one file and nothing else."""
    a = resolve_area(args.area)
    text = args.text or ""
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    context = Path(args.context_file).read_text(encoding="utf-8") if args.context_file else ""
    try:
        kind, row = resolve_target(a, args.target, args.kind or "")
        why = check_choice(kind, row, args.choice or "")
        if why:
            raise ValueError(why)
        iid, body = inbox_entry(args.target, args.device, kind, args.choice or "", text, context, args.at or "")
    except ValueError as e:
        die(f"not saved: {e}")
    write_atomic(a / "data" / "inbox" / f"{iid}.csv", body)
    print(f"saved {rel(a)}/data/inbox/{iid}.csv")
    return RC_OK


def cmd_inbox(args):
    """Every answer waiting to be applied, with his words. rc 2 when there are any. His notes
    (kind note, D-426) are a log, not answers, and are not listed."""
    sel = [resolve_area(args.area)] if args.area else areas()
    n = 0
    for a in sel:
        for r in sorted(waiting(read_table(a, "inbox")[1]), key=lambda r: r.get("at", "")):
            n += 1
            print(f"{rel(a)} · {r.get('kind')} {r.get('target')} · {r.get('device')} {r.get('at')}")
            if (r.get("choice") or "").strip():
                print(f"   choice:  {r['choice']}")
            if (r.get("text") or "").strip():
                print("   his words: " + r["text"].strip().replace("\n", "\n              "))
            if (r.get("context") or "").strip():
                print("   from the discussion: " + r["context"].strip().replace("\n", "\n              "))
    print(f"({n} answer(s) waiting)")
    return RC_WAITING if n else RC_OK


def cmd_picks(args):
    """Where every parts pick stands (D-388). Reads picks, parts and inbox; writes nothing.
    His answers to proposed picks arrive in `inbox` (kind pick) - `rx7.py inbox` lists them."""
    sel = [resolve_area(args.area)] if args.area else [a for a in areas() if (a / "data" / "picks.csv").exists()]
    for a in sel:
        _, picks = read_table(a, "picks")
        _, parts = read_table(a, "parts")
        cell = lambda r, k: re.sub(r"\s+", " ", (r.get(k) or "").strip())
        waiting = {(r.get("target") or "").strip() for r in read_table(a, "inbox")[1] if r.get("kind") == "pick"}
        proposed = [r for r in picks if cell(r, "verdict") == "proposed"]
        chosen = [r for r in picks if cell(r, "verdict") == "accepted"]
        vetoed = [r for r in picks if cell(r, "verdict") == "vetoed"]
        touched = {cell(r, "part") for r in picks}
        todo = [r for r in parts if cell(r, "id") not in touched and cell(r, "status") not in ("in hand", "chosen")]
        print(f"{rel(a)}: {len(proposed)} proposed ({len(waiting)} answered, not applied) · {len(chosen)} chosen · "
              f"{len(vetoed)} vetoed · {len(todo)} parts not yet searched")
        for r in proposed:
            print(f"   {'answered' if cell(r, 'id') in waiting else 'proposed'}  {cell(r, 'id')}  {cell(r, 'part')}  {cell(r, 'product')}")
        for r in chosen:
            print(f"   chosen  {cell(r, 'part')}  {cell(r, 'product')}  {cell(r, 'decision')}")
        for r in vetoed:
            print(f"   vetoed  {cell(r, 'part')}  {cell(r, 'product')} - \"{cell(r, 'said')}\"")
        for r in todo:
            print(f"   search  {cell(r, 'id')}  {cell(r, 'item')}" + (f" (waits on {cell(r, 'gate')})" if cell(r, "gate") else ""))
    return RC_OK


def cmd_diagrams(args):
    """Regenerate the two drawings of every harness leg (D-385): 01-electrical/00-design/diagrams/<leg>/
    A-pin-ladder.svg and B-route-map.svg. Reads 01-electrical housings, cavities, devices and routes;
    writes those SVGs and nothing else. A read-only projection: `check` never looks at it and it
    never refuses a commit. rc 2 when a sheet fails the overlap rule and is not written.
    The drawing code is tools/diagrams.py (it needs Pillow, which this file does not)."""
    sys.path.insert(0, str(ROOT / "tools"))
    import diagrams
    return diagrams.main()


def cmd_cites(args):
    out = unresolved_cites()
    for x in out:
        print(x)
    print(f"({len(out)} unresolved cite(s) in prose - advisory, nothing is refused)")
    return RC_WAITING if out else RC_OK


def cmd_block(args):
    """Raise a block: one row in the project's `blocks`, every field written at once. Reads the
    tree's blocks, decisions and retired terms for the next number; writes that one row."""
    area = resolve_area(args.area)
    prefix = block_prefix(area)
    if not prefix:
        die(f"{rel(area)} owns no block prefix - only 00-CAR, 01-REFERENCE and 02-PROJECTS/NN-* do")
    vals = _pairs(args.pairs)
    need = [c for c in ("ask", "why", "options", "recommend", "stops") if not (vals.get(c) or "").strip()]
    if need:
        die(f"a block is answerable from its row alone (§4) - missing {', '.join(need)} (nothing was written)")
    opts = parse_options(vals["options"])
    if not opts or len(opts) < 2:
        die("options: one per line, each starting (a) , (b) … and at least two (nothing was written)")
    vals["options"] = "\n".join(f"({x}) {t}" for x, t in opts)
    title = re.sub(r"\s+", " ", vals.get("title") or vals["ask"]).strip()
    vals["title"] = title if len(title) <= 70 else title[:70].rsplit(" ", 1)[0].rstrip(" -,;") + " …"
    vals["opened"] = vals.get("opened") or today()
    vals["id"] = next_block_id(prefix)
    hdr, rows = read_table(area, "blocks")
    hdr = hdr or list(TOOL_COLUMNS["blocks"])
    stray = [k for k in vals if k not in hdr]
    if stray:
        die(f"blocks has no column {', '.join(stray)} (nothing was written)")
    write_table(area, "blocks", hdr, rows + [vals])
    print(f"{vals['id']} raised in {rel(area)}")
    return RC_OK


def cmd_blocks(args):
    """Open blocks; with --answered, only those with an answer in the inbox (rc 2 if any)."""
    answers = {}
    for a in areas():
        for r in read_table(a, "inbox")[1]:
            answers.setdefault((a.name, (r.get("target") or "").strip()), []).append(r)
    sel = [b for b in open_blocks() if not args.answered or (b["_area"].name, b["id"].strip()) in answers]
    for b in sel:
        mine = answers.get((b["_area"].name, b["id"].strip()), [])
        print(f"{b['id']} · {b['_area'].name} · {'answered' if mine else 'waiting'} · {b.get('title', '')}")
        print(f"   ask:   {b.get('ask', '')}")
        for r in mine:
            print(f"   {r.get('device')}: {(r.get('choice') or '').strip()} {(r.get('text') or '').strip()}".rstrip())
    print(f"({len(sel)} block(s))")
    if args.answered:
        return RC_WAITING if sel else RC_OK
    return RC_OK if sel else RC_WAITING


def cmd_selftest(args):
    """The tool's own tests, in memory and in a scratch folder: never the real record.

    `check` asks whether THIS tree's gates are sound. This asks whether the thing that
    decides that is itself right — because a resolver that wrongly calls a gate 'met'
    puts the planner to work on something that is not ready, and one that wrongly calls
    it 'unmet' stops the project with no error anywhere. Both fail silently (R7). The same
    goes for the writer of his answers: one that loses a character loses his words (R3)."""
    A, B = "01-electrical", "03-luxury"
    fails = []

    def mk(rows, phase="PLANNING", blocks=None):
        # 00.90 is still open (a row in `blocks`). 00.91 is gone from `blocks` and named in
        # some decision's `closes` — that is what "answered and applied" means.
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
    expect("a reference to nothing is refused", gate_state("D-999", A, idx)[2])
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
    expect("an open block does not", gate_state("00.90", A, ok)[0], want=False)
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

    # --- blocks: the options every answer button comes from ---
    expect("options one per line parse", parse_options("(a) one\n(b) two") == [("a", "one"), ("b", "two")])
    expect("options written as a list still parse", parse_options("- (a) one\n- (b) two") == [("a", "one"), ("b", "two")])
    expect("an option without its letter is refused", parse_options("(a) one\ntwo") is None)
    expect("the recommended option is found", recommended_letter("(b), unless it rains; (a) otherwise", "ab") == "b")
    expect("a recommendation naming no option names none", recommended_letter("Yes, if it fits", "ab") == "")

    # --- his answers: written exactly, one file each, never merged ---
    words = 'Line one, with "quotes", commas; and a → arrow\n\nLine three — ñ 12 µF\n'
    iid, body = inbox_entry("00.29", "phone", "block", "a", words, "points", "2026-09-24T21:05:00-06:00")
    hdr, rows = read_csv_text(body)
    expect("an answer's id is its target and device", iid == "00.29~phone")
    expect("an answer's words survive the file byte for byte", rows and dict(zip(hdr, rows[0]))["text"] == words)
    expect("an answer file holds exactly one row under the inbox header",
           len(rows) == 1 and tuple(hdr) == INBOX_COLUMNS)
    for bad, label in ((("", "phone", "block", "a"), "an empty target is refused"),
                       (("00.29", "laptop", "block", "a"), "an unknown device is refused"),
                       (("00.29", "phone", "block", "", "  "), "an answer with no choice and no words is refused"),
                       (("../x", "phone", "block", "a"), "a target that is a path is refused")):
        try:
            inbox_entry(*bad)
            expect(label, False)
        except ValueError:
            expect(label, True)
    expect("a pick is answered yes, no or question", check_choice("pick", {}, "maybe"))
    expect("a choice row takes one of its choices", check_choice("work", {"reply": "choice", "choices": "a|b"}, "c"))
    expect("a value row takes any value", check_choice("work", {"reply": "value"}, "55.2") is None)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        area = Path(td) / "02-PROJECTS" / "07-test"
        (area / "data").mkdir(parents=True)
        hdr = list(INBOX_COLUMNS)
        r1 = dict(zip(hdr, read_csv_text(body)[1][0]))
        r2 = dict(r1, id="00.30~desktop", target="00.30", device="desktop")
        write_table(area, "inbox", hdr, [r1, r2])
        back = {r["id"]: r for r in read_table(area, "inbox")[1]}
        expect("a folder table writes one file per row", len(folder_files(area, "inbox")) == 2)
        expect("a folder table reads back exactly", back.get("00.29~phone", {}).get("text") == words)
        write_table(area, "inbox", hdr, [r2])
        expect("deleting a row removes only its file",
               [f.name for f in folder_files(area, "inbox")] == ["00.30~desktop.csv"])

    # --- the Manual (D-417): what is held back, what is due, where the odometer stands ---
    expect("a spec for this car is shown", manual_hold("specs", {"item": "Gap", "confidence": "primary"}) == "shown")
    expect("a value marked confirm is held", manual_hold("parts", {"name": "Pump", "note": "draw 5 A - confirm"}) == "confirm")
    expect("'confirmed' is not the confirm marker", manual_hold("issues", {"issue": "Blower", "status": "Confirmed dead"}) == "shown")
    expect("confirm in a column the Manual never shows holds nothing",
           manual_hold("issues", {"issue": "Blower", "status": "dead", "impact": "confirm later"}) == "shown")
    expect("an unverified spec is held", manual_hold("specs", {"item": "Offset", "confidence": "unverified"}) == "unverified")
    expect("another year's figure is held", manual_hold("specs", {"item": "x", "applies": "other-car"}) == "other-car")
    expect("a replaced part's spec is gone, not held", manual_hold("specs", {"item": "Choke", "applies": "replaced"}) == "gone")
    svc = [{"id": "SV1", "date": "2026-07", "mileage": "150000", "items": "oil brake_fluid"},
           {"id": "SV0", "date": "2025-09", "mileage": "", "items": "oil"}]
    odo = odometer_now([{"id": "odo-1", "date": "2026-09-20", "odometer": "157200", "kind": "set"}], svc, [])
    expect("the odometer is the newest reading", odo["miles"] == 157200 and odo["source"] == "set")
    expect("with no drives the odometer is the newest service reading",
           odometer_now([], svc, [{"key": "mileage", "value": "1"}])["miles"] == 150000)
    expect("with no reading at all it falls back to vehicle.mileage",
           odometer_now([], [], [{"key": "mileage", "value": "153000"}])["source"] == "vehicle")
    today_d = datetime.date(2026, 9, 24)
    oil = {"id": "oil", "every_miles": "7500", "every_months": "7.5"}
    expect("an interval is due from the newest visit that did it",
           interval_due(oil, svc, {"miles": 150100}, today_d)["last"]["service"] == "SV1")
    expect("under 1000 miles left is soon", interval_due(oil, svc, {"miles": 156800}, today_d)["status"] == "soon")
    expect("past the miles is overdue", interval_due(oil, svc, {"miles": 157600}, today_d)["status"] == "overdue")
    expect("past the months is overdue, whatever the miles",
           interval_due(oil, svc, {"miles": 150100}, datetime.date(2027, 3, 1))["status"] == "overdue")
    expect("an interval no visit has done is never",
           interval_due({"id": "atf", "every_miles": "30000"}, svc, {"miles": 1}, today_d)["status"] == "never")
    expect("an interval with no period is each", interval_due({"id": "premix"}, svc, {"miles": 1}, today_d)["status"] == "each")
    expect("a drive target is recognised", DRIVE_TARGET_RE.match("odo-20260924T221500"))
    expect("a drive with no reading is refused", check_choice("drive", {}, ""))
    expect("a reading that is not whole miles is refused", check_choice("drive", {}, "157,200"))
    expect("a whole-mile reading is taken", check_choice("drive", {}, "157200") is None)
    words = 'He said "this torque looks wrong", then µ ✓\nsecond line'
    nid, body = inbox_entry("note-20260925T120000", "desktop", "note", "", words,
                            "where: #/manual/specs\nselected: Wheel nut torque")
    back = list(csv.DictReader(io.StringIO(body)))[0]
    expect("a note keeps his words byte for byte", back["text"] == words and back["kind"] == "note")
    expect("a note's target is recognised", NOTE_TARGET_RE.match(nid.split("~")[0]))
    expect("a note is never waiting to be applied",
           waiting([{"kind": "note"}, {"kind": "block"}]) == [{"kind": "block"}])
    try:
        inbox_entry("note-20260925T120000", "phone", "note", "", "   ")
        expect("an empty note is refused", False)
    except ValueError:
        expect("an empty note is refused", True)

    expect("an ISO date parses", days_since("2026-09-01") is not None)
    expect("a non-date does not", days_since("soon") is None)
    expect("a date and time is a datetime", not bad_value("datetime", "2026-09-24T21:05:00-06:00"))

    print(f"\n{len(fails)} failure(s)" if fails else "\nselftest: all pass")
    return RC_INVALID if fails else RC_OK


def cmd_log(args):
    a = resolve_area(args.area)
    if "log" not in schema(a)[1]:
        die(f"'log' is not a declared table in {rel(a)} (nothing was written)")
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

    p = sub.add_parser("status", help="one screen: record validity, phases, work, blocks, inbox")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("tables", help="every declared table in an area, with row counts")
    p.add_argument("area")
    p.set_defaults(fn=cmd_tables)

    p = sub.add_parser("get", help="one row")
    p.add_argument("area"); p.add_argument("table"); p.add_argument("key")
    p.set_defaults(fn=cmd_get)

    p = sub.add_parser("set", help="change columns on an existing row (col=@file reads a file)")
    p.add_argument("area"); p.add_argument("table"); p.add_argument("key")
    p.add_argument("pairs", nargs="+")
    p.set_defaults(fn=cmd_set)

    p = sub.add_parser("add", help="add a row (col=@file reads a file)")
    p.add_argument("area"); p.add_argument("table"); p.add_argument("pairs", nargs="+")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("del", help="delete a row")
    p.add_argument("area"); p.add_argument("table"); p.add_argument("key")
    p.set_defaults(fn=cmd_del)

    p = sub.add_parser("sql", help="read-only query across one area's tables")
    p.add_argument("area"); p.add_argument("query")
    p.set_defaults(fn=cmd_sql)

    p = sub.add_parser("find", help="search every cell of every table, decision bodies included")
    p.add_argument("text"); p.add_argument("-p", "--area")
    p.set_defaults(fn=cmd_find)

    p = sub.add_parser("new", help="reserve the next D- (body=@file writes its text at once)")
    p.add_argument("area"); p.add_argument("title"); p.add_argument("pairs", nargs="*")
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("export", help="everything the app shows, as JSON (rc 1 if the record is invalid)")
    p.add_argument("--out"); p.add_argument("--pretty", action="store_true")
    p.set_defaults(fn=cmd_export)

    p = sub.add_parser("answer", help="save one of his answers into an area's inbox")
    p.add_argument("area"); p.add_argument("target")
    p.add_argument("--device", required=True, choices=INBOX_DEVICE)
    p.add_argument("--kind", choices=INBOX_KIND)
    p.add_argument("--choice"); p.add_argument("--text"); p.add_argument("--text-file")
    p.add_argument("--context-file"); p.add_argument("--at")
    p.set_defaults(fn=cmd_answer)

    p = sub.add_parser("inbox", help="his answers waiting to be applied, with his words (rc 2 if any)")
    p.add_argument("-p", "--area")
    p.set_defaults(fn=cmd_inbox)

    p = sub.add_parser("picks", help="where every parts pick stands")
    p.add_argument("-p", "--area")
    p.set_defaults(fn=cmd_picks)

    p = sub.add_parser("diagrams", help="regenerate each harness leg's pin ladder (A) and route map (B)")
    p.set_defaults(fn=cmd_diagrams)

    p = sub.add_parser("cites", help="advisory: prose cites that no longer resolve (never refuses)")
    p.set_defaults(fn=cmd_cites)

    p = sub.add_parser("block", help="raise a block: ask= why= options= recommend= stops= [title=]")
    p.add_argument("-p", "--area", required=True); p.add_argument("pairs", nargs="+")
    p.set_defaults(fn=cmd_block)

    p = sub.add_parser("blocks", help="list open blocks (--answered: those with an answer waiting)")
    p.add_argument("--answered", action="store_true")
    p.set_defaults(fn=cmd_blocks)

    p = sub.add_parser("selftest", help="the tool's own tests (never touches the record)")
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

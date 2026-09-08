#!/usr/bin/env python3
"""rx7 — the project data tool.  Python 3.10+, standard library only.   (v2, 2026-09-08)

A project keeps its facts in  data/*.csv  (one row per thing, one home per fact)
and its prose in  templates/*.md.  `build` renders the documents and VIEW.html
from both; nothing generated is ever edited by hand.

Questions, decisions, work and the log are data too (system v2):
  data/questions.csv + data/questions/<id>.md     the packets (answer in the body, under **ANSWER:**)
  data/decisions.csv + data/decisions/<id>.md     the rulings, by system
  data/work.csv                                   the plan — every task, agent- or Camden-owned
  data/log.csv                                    append-only; the banners and LOG.md render from it
  data/project.csv                                key/value: name, kind, goal, phase, opened
  data/retired.csv                                terms a ruling retired; the build refuses if one is used

    python tools/rx7.py status                      every project: phase, next ids, what waits on whom
    python tools/rx7.py tables                      list tables and columns
    python tools/rx7.py get   <table> <key>         one row  (key = first column, or col=value)
    python tools/rx7.py find  <text>                every row in every table containing text
    python tools/rx7.py sql   "<select …>"          query the in-memory database
    python tools/rx7.py set   <table> <key> col=value …     change fields on one row
    python tools/rx7.py add   <table> col=value …           new row (key column required)
    python tools/rx7.py del   <table> <key>
    python tools/rx7.py new   Q|D "<title>" [col=value …]   next id, index row and body file, in one call
    python tools/rx7.py ids   next D|Q|C  ·  where <id>     the registry
    python tools/rx7.py log   <workflow> "<summary>" [ids…] append a log row
    python tools/rx7.py check                       integrity checks, no output written
    python tools/rx7.py lint  [--json]              warnings and drift metrics (never refuses)
    python tools/rx7.py build                       check, then render documents + VIEW.html

Project selection: -p <name> (a folder under 02-PROJECTS, 00-CAR/systems, or 00-CAR / 01-REFERENCE),
-a for every project, or run from inside the project folder. A project is any folder holding data/
and templates/; an optional views.py beside them supplies named views and checks.

Generic placeholders every template may use, with or without a views.py:
  {{table:name|col=value|-hide,cols}}   {{count:name|col=value}}   {{cell:table|key|column}}
  {{param:key}}   {{next_id:D}}   {{phase}}   {{packets:section}}   {{work}}   {{closed}}   {{moved}}
  {{banners:N}}   {{decisions:system}}   {{latest:N}}   {{log}}   {{open_for_camden}}
"""
import csv, html, io, json, re, sqlite3, sys
from datetime import date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
PHASES = ["PROPOSED", "PLANNING", "SOURCING", "BUILDING", "COMPLETE", "PERMANENT"]
ID_TOKEN = re.compile(r"\b([A-Z]{1,2})-(\d{3})\b")          # D-278, Q-134, SP-010, C-001 …
LIVE_ID_FAMILIES = ("D", "Q", "C")                            # dup / dangling checks refuse the build for these


# ------------------------------------------------------------------ database

class DB:
    """All CSVs of one project, loaded into an in-memory SQLite database."""
    _others: dict = {}

    def __init__(self, project: Path):
        self.project = project
        self.data = project / "data"
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.tables: dict[str, list[str]] = {}
        for p in sorted(self.data.glob("*.csv")):
            with open(p, encoding="utf-8", newline="") as f:
                rd = csv.reader(f)
                header = next(rd)
                rows = [r + [""] * (len(header) - len(r)) for r in rd]
            self.tables[p.stem] = header
            cols = ", ".join(f'"{c}" TEXT' for c in header)
            self.con.execute(f'CREATE TABLE "{p.stem}" (_n INTEGER, {cols})')
            self.con.executemany(
                f'INSERT INTO "{p.stem}" VALUES ({",".join("?" * (len(header) + 1))})',
                [[i] + r for i, r in enumerate(rows)])
        self.con.commit()

    # reading -----------------------------------------------------------
    def q(self, sql, *args):
        return self.con.execute(sql, args).fetchall()

    def rows(self, table, where="", *args):
        if table not in self.tables:
            return []
        w = f" WHERE {where}" if where else ""
        return [dict(r) for r in self.q(f'SELECT * FROM "{table}"{w} ORDER BY _n', *args)]

    def get(self, table, key):
        if table not in self.tables:
            return None
        keycol = self.tables[table][0]
        if "=" in key:
            col, val = key.split("=", 1)
        else:
            col, val = keycol, key
        r = self.q(f'SELECT * FROM "{table}" WHERE "{col}" = ?', val)
        return dict(r[0]) if r else None

    def key(self, table):
        return self.tables[table][0]

    def param(self, key, default=""):
        """A scalar from data/params.csv or data/project.csv (key,value)."""
        for t in ("params", "project"):
            r = self.get(t, key) if t in self.tables else None
            if r:
                return r.get("value", default)
        return default

    def other(self, name):
        """Another project's database, by name — cached. Follows a completed project into 00-CAR/systems/."""
        p = find_project(name)
        if p not in DB._others:
            DB._others[p] = DB(p)
        return DB._others[p]

    def body(self, kind, id_):
        """The Markdown body of a question or decision: data/<kind>/<id>.md, '' if none."""
        p = self.data / kind / f"{id_}.md"
        return p.read_text(encoding="utf-8") if p.exists() else ""

    # writing (CSV is the record; the database is rebuilt on next load) ---
    def _load_csv(self, table):
        p = self.data / f"{table}.csv"
        with open(p, encoding="utf-8", newline="") as f:
            rd = csv.reader(f)
            header = next(rd)
            rows = [r + [""] * (len(header) - len(r)) for r in rd]
        return p, header, rows

    def _save_csv(self, p, header, rows):
        with open(p, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(header)
            w.writerows(rows)

    def set(self, table, key, changes: dict):
        p, header, rows = self._load_csv(table)
        bad = [c for c in changes if c not in header]
        if bad:
            raise SystemExit(f"{table}: no such column(s) {bad}; columns are {header}")
        kc = header.index(self.key(table))
        hit = [r for r in rows if r[kc] == key]
        if len(hit) != 1:
            raise SystemExit(f"{table}: key {key!r} matched {len(hit)} rows")
        before = dict(zip(header, hit[0]))
        for c, v in changes.items():
            hit[0][header.index(c)] = v
        self._save_csv(p, header, rows)
        return before, dict(zip(header, hit[0]))

    def add(self, table, values: dict, after: str | None = None):
        p, header, rows = self._load_csv(table)
        bad = [c for c in values if c not in header]
        if bad:
            raise SystemExit(f"{table}: no such column(s) {bad}; columns are {header}")
        k = self.key(table)
        if not values.get(k):
            raise SystemExit(f"{table}: the key column {k!r} is required")
        if any(r[0] == values[k] for r in rows):
            raise SystemExit(f"{table}: key {values[k]!r} already exists")
        if table in ("questions", "decisions"):
            hit = registry().defined.get(values[k])
            if hit:
                raise SystemExit(f"{values[k]} is already defined in {hit} — ids are permanent, take the next one (`ids next {values[k][0]}`)")
        row = [values.get(c, "") for c in header]
        if after is not None:
            idx = [i for i, r in enumerate(rows) if r[0] == after]
            if not idx:
                raise SystemExit(f"{table}: --after key {after!r} not found")
            rows.insert(idx[0] + 1, row)
        else:
            rows.append(row)
        self._save_csv(p, header, rows)
        return dict(zip(header, row))

    def delete(self, table, key):
        p, header, rows = self._load_csv(table)
        keep = [r for r in rows if r[0] != key]
        if len(keep) == len(rows):
            raise SystemExit(f"{table}: key {key!r} not found")
        self._save_csv(p, header, keep)
        return len(rows) - len(keep)

    def append_log(self, workflow, summary, ids=""):
        p = self.data / "log.csv"
        header = ["id", "date", "workflow", "ids", "summary"]
        if not p.exists():
            self._save_csv(p, header, [])
        _, hdr, rows = self._load_csv("log")
        n = max([int(r[0][1:]) for r in rows if r and r[0][1:].isdigit()] + [0]) + 1
        row = [f"L{n:03d}", date.today().isoformat(), workflow, ids, summary]
        rows.append(row)
        self._save_csv(p, hdr, rows)
        return dict(zip(hdr, row))


# ------------------------------------------------------------------ the registry

class Registry:
    """Every id defined anywhere in the live tree (and, for cites, the archive), and where."""

    def __init__(self):
        self.defined: dict[str, str] = {}     # id -> "project/table" of its definition (live tree)
        self.dups: list[str] = []
        self.archived: set[str] = set()       # ids that exist only as history
        for d in all_projects():
            name = d.relative_to(ROOT).as_posix()
            for p in sorted((d / "data").glob("*.csv")):
                with open(p, encoding="utf-8", newline="") as f:
                    rd = csv.reader(f)
                    hdr = next(rd, None)
                    if not hdr:
                        continue
                    also = hdr.index("also") if "also" in hdr else None
                    status = hdr.index("status") if "status" in hdr else None
                    for r in rd:
                        if not r or not ID_TOKEN.fullmatch(r[0]):
                            continue
                        ids = [r[0]] + (re.split(r"[\s,]+", r[also].strip()) if also is not None and len(r) > also and r[also].strip() else [])
                        inherited = status is not None and len(r) > status and r[status] in ("inherited", "moved")
                        for i in ids:
                            if inherited:
                                continue
                            if i in self.defined and self.defined[i] != f"{name}/{p.stem}":
                                self.dups.append(f"{i} defined in both {self.defined[i]} and {name}/{p.stem}")
                            self.defined.setdefault(i, f"{name}/{p.stem}")
        arch = ROOT / "99-ARCHIVE"
        if arch.exists():
            for p in arch.rglob("*.md"):
                try:
                    for m in re.finditer(r"(?:\*\*|^\|\s*`?|^- `?|^#+\s+)([A-Z]{1,2}-\d{3})", p.read_text(encoding="utf-8", errors="ignore"), re.M):
                        self.archived.add(m.group(1))
                except OSError:
                    pass

    def next(self, family, project: Path | None = None):
        lo, hi = 1, 999
        if project is not None:
            db = DB(project)
            rng = db.param(f"range_{family}")
            if rng and "-" in rng:
                lo, hi = (int(x) for x in rng.split("-", 1))
        used = [int(i.split("-")[1]) for i in self.defined if i.startswith(family + "-")]
        used += [int(i.split("-")[1]) for i in self.archived if i.startswith(family + "-")]
        used = [u for u in used if lo <= u <= hi] or [lo - 1]
        n = max(used) + 1
        if n > hi:
            raise SystemExit(f"{family} range {lo}-{hi} is exhausted")
        return f"{family}-{n:03d}"

    def where(self, id_):
        return self.defined.get(id_) or ("archive" if id_ in self.archived else None)


_REG = None


def registry(fresh=False):
    global _REG
    if _REG is None or fresh:
        _REG = Registry()
    return _REG


# ------------------------------------------------------------------ rendering helpers

def md_table(headers, rows):
    """Markdown table. Cells are strings; a '|' inside a cell is escaped."""
    esc = lambda c: str(c).replace("|", "\\|") if "\\|" not in str(c) else str(c)
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        out.append("| " + " | ".join(esc(c) for c in r) + " |")
    return "\n".join(out)


def md_to_html(md: str, anchors: bool = False) -> str:
    """A small Markdown → HTML converter covering what these documents use:
    headings, paragraphs, bold/italic/code, links, images (SVG inlined), lists,
    task boxes, tables, rules, block quotes, fenced code."""
    lines = md.splitlines()
    out, i, para = [], 0, []
    ctx = {"housing": ""}

    def inline(s):
        s = html.escape(s, quote=False)
        s = re.sub(r"\\\|", "|", s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"(?<![\w*])\*([^*]+?)\*(?![\w*])", r"<i>\1</i>", s)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
        s = s.replace("&lt;br&gt;", "<br>")
        return s

    def flush():
        nonlocal para
        if para:
            text = " ".join(para).strip()
            attr = ""
            if anchors:
                m = re.match(r"\*\*([DQC]-\d{3})", text)
                if m:
                    attr = f' id="{m.group(1)}"'
                m = re.match(r"\*\*((?:L\d-(?:[PMS]\d?|BLW)|D[12]|DP-[A-Z]+(?:-[A-Z])?))\*\*", text)
                if m:
                    ctx["housing"] = m.group(1)
            out.append(f"<p{attr}>{inline(text)}</p>")
            para = []

    while i < len(lines):
        l = lines[i]
        if l.startswith("```"):
            flush(); j = i + 1; buf = []
            while j < len(lines) and not lines[j].startswith("```"):
                buf.append(lines[j]); j += 1
            out.append("<pre>" + html.escape("\n".join(buf)) + "</pre>"); i = j + 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)$", l)
        if m:
            flush(); n = len(m.group(1)); t = m.group(2)
            hid = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()
            m2 = re.search(r"\b(DP-[A-Z]+(?:-[A-Z])?|L\d-BLW)\b", t)
            if anchors and m2:
                ctx["housing"] = m2.group(1)
            out.append(f'<h{n} id="{hid}">{inline(t)}</h{n}>'); i += 1; continue
        if re.match(r"^\s*(---|\*\*\*)\s*$", l):
            flush(); out.append("<hr>"); i += 1; continue
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", l)
        if m:
            flush(); alt, src = m.groups()
            p = Path(src)
            svg = None
            for base in (CURRENT_DOC_DIR, ROOT):
                if base and (base / p).exists():
                    svg = (base / p).read_text(encoding="utf-8"); break
            if svg:
                svg = re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>", "", svg)
                out.append(f'<figure class="diagram" title="{html.escape(alt)}">{svg}</figure>')
            else:
                out.append(f'<p><i>[diagram: {html.escape(src)}]</i></p>')
            i += 1; continue
        if l.startswith("|"):
            flush(); j = i; rows = []
            while j < len(lines) and lines[j].startswith("|"):
                rows.append(lines[j]); j += 1
            if len(rows) >= 2 and re.match(r"^\|[\s:|-]+\|$", rows[1].strip()):
                hdr = split_cells(rows[0]); body = [split_cells(r) for r in rows[2:]]
                t = ["<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in hdr) + "</tr></thead><tbody>"]
                for r in body:
                    attr = ""
                    if anchors and r:
                        key = ""
                        c0 = r[0].strip("`* ")
                        if hdr[0] == "Cav" and ctx["housing"] and c0.isdigit():
                            key = f"{ctx['housing']} {c0}"
                        elif hdr[0] == "Pin" and len(r) > 2 and ID_RE.fullmatch(r[2].strip("`* ")) and not r[2].strip().isdigit():
                            key = r[2].strip("`* ")
                        elif ID_RE.fullmatch(c0) and not c0.isdigit():
                            key = c0
                        if key:
                            attr = f' id="row-{slug(key)}"'
                    t.append(f"<tr{attr}>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
                t.append("</tbody></table>")
                out.append("".join(t))
            else:
                out.extend(f"<p>{inline(r)}</p>" for r in rows)
            i = j; continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", l)
        if m:
            flush(); j = i; items = []; ordered = m.group(2)[0].isdigit()
            while j < len(lines):
                m2 = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[j])
                if m2:
                    items.append(m2.group(3)); j += 1
                elif lines[j].startswith("  ") and items:
                    items[-1] += " " + lines[j].strip(); j += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            lis = []
            for it in items:
                it = re.sub(r"^\[ \]\s*", '<span class="box">&#9744;</span> ', it)
                it = re.sub(r"^\[x\]\s*", '<span class="box">&#9745;</span> ', it, flags=re.I)
                lis.append(f"<li>{inline(it)}</li>")
            out.append(f"<{tag}>" + "".join(lis) + f"</{tag}>"); i = j; continue
        if l.startswith(">"):
            flush(); j = i; buf = []
            while j < len(lines) and lines[j].startswith(">"):
                buf.append(lines[j][1:].strip()); j += 1
            out.append("<blockquote>" + inline(" ".join(buf)) + "</blockquote>"); i = j; continue
        if l.strip() == "":
            flush(); i += 1; continue
        para.append(l); i += 1
    flush()
    return "\n".join(out)


CURRENT_DOC_DIR: Path | None = None
ID_RE = re.compile(r"(?:L\d-(?:[PMS]\d?|BLW) \d+|D[12] \d+|DP-[A-Z]+(?:-[A-Z])? \d+|O\d{1,2}|A\d{1,2}|F\d{1,2}|K\d{1,2}|[DQC]-\d{3}|CAN[12][HL]|STUD|\d{1,2})")


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")


def split_cells(line):
    line = line.strip()
    if line.startswith("|"): line = line[1:]
    if line.endswith("|"): line = line[:-1]
    cells, cur, i = [], "", 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            cur += "\\|"; i += 2; continue
        if c == "|":
            cells.append(cur.strip()); cur = ""; i += 1; continue
        cur += c; i += 1
    cells.append(cur.strip())
    return cells


# ------------------------------------------------------------------ project plumbing

def find_project(name: str | None) -> Path:
    if name:
        for p in (Path(name), ROOT / name, ROOT / "02-PROJECTS" / name, ROOT / "00-CAR" / "systems" / name):
            if (p / "data").is_dir():
                return p.resolve()
        raise SystemExit(f"no data/ under {name}")
    cwd = Path.cwd()
    for c in [cwd, *cwd.parents]:
        if (c / "data").is_dir() and (c / "templates").is_dir():
            return c.resolve()
    cands = all_projects()
    if len(cands) == 1:
        return cands[0].resolve()
    raise SystemExit("which project? use -p <name> or -a for all: " + ", ".join(str(c.relative_to(ROOT)) for c in cands))


def all_projects():
    """Every folder in the tree holding data/ and templates/: 00-CAR, 01-REFERENCE, 00-CAR/systems/*, 02-PROJECTS/*."""
    out = []
    for d in sorted(ROOT.glob("*/")) + sorted((ROOT / "00-CAR" / "systems").glob("*/")) + sorted((ROOT / "02-PROJECTS").glob("*/")):
        if (d / "data").is_dir() and (d / "templates").is_dir() and "99-ARCHIVE" not in str(d):
            out.append(d)
    return out


def load_views(project: Path):
    vp = project / "views.py"
    if not vp.exists():
        return dict(GENERIC_VIEWS), [], None, {}
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"views_{project.name}", vp)
    mod = importlib.util.module_from_spec(spec)
    mod.rx7 = sys.modules[__name__]
    spec.loader.exec_module(mod)
    return ({**GENERIC_VIEWS, **getattr(mod, "VIEWS", {})}, getattr(mod, "CHECKS", []),
            getattr(mod, "PRE_BUILD", None), getattr(mod, "GATES", {}))


# ------------------------------------------------------------------ generic checks

def generic_checks(db: DB, gates=None):
    problems = []
    for t, cols in db.tables.items():
        k = cols[0]
        seen = {}
        for r in db.rows(t):
            v = r[k]
            if not v:
                problems.append(f"{t}: a row has an empty key ({k})")
            elif v in seen:
                problems.append(f"{t}: duplicate key {v!r}")
            seen[v] = 1
    problems += c_registry(db)
    problems += c_questions(db)
    problems += c_decisions(db)
    problems += c_work(db)
    problems += c_retired(db)
    problems += c_headers(db)
    problems += c_phase(db, gates or {})
    return problems


def _live_text_sources(db: DB):
    """(label, text) for every place a cite can live in this project: cells, bodies, templates."""
    out = []
    for t in db.tables:
        for r in db.rows(t):
            for c, v in r.items():
                if c != "_n" and v:
                    out.append((f"{t}:{r[db.key(t)]}.{c}", v))
    for kind in ("questions", "decisions"):
        for p in sorted((db.data / kind).glob("*.md")) if (db.data / kind).is_dir() else []:
            out.append((f"{kind}/{p.name}", p.read_text(encoding="utf-8")))
    for p in sorted((db.project / "templates").glob("*.md")):
        out.append((f"templates/{p.name}", p.read_text(encoding="utf-8")))
    return out


def c_registry(db: DB):
    """D-/Q-/C- ids: never defined twice in the live tree; never cited without a definition (live or archive)."""
    reg = registry()
    problems = list(dict.fromkeys(reg.dups))
    seen = set()
    for label, text in _live_text_sources(db):
        if label.startswith("log:"):
            continue
        for m in ID_TOKEN.finditer(text):
            i = m.group(0)
            if m.group(1) not in LIVE_ID_FAMILIES or i in seen:
                continue
            if reg.where(i) is None:
                problems.append(f"{label}: cites {i}, which is defined nowhere in the tree or the archive")
                seen.add(i)
    return problems


def c_questions(db: DB):
    problems = []
    if "questions" not in db.tables:
        return problems
    for q in db.rows("questions"):
        st = q.get("status", "")
        if st not in ("open", "closed", "moved"):
            problems.append(f"questions:{q['id']} status {st!r} is not open / closed / moved")
        if st == "closed" and not q.get("closer"):
            problems.append(f"questions:{q['id']} is closed with no closer")
        if st == "moved" and not q.get("closer"):
            problems.append(f"questions:{q['id']} is moved with no destination in `closer`")
        if st == "open" and not db.body("questions", q["id"]):
            problems.append(f"questions:{q['id']} is open but data/questions/{q['id']}.md does not exist")
        if st == "open" and "**ANSWER:**" not in db.body("questions", q["id"]):
            problems.append(f"questions/{q['id']}.md has no **ANSWER:** block — Camden has nowhere to answer")
    return problems


def c_decisions(db: DB):
    problems = []
    if "decisions" not in db.tables:
        return problems
    for d in db.rows("decisions"):
        st = d.get("status", "")
        if st not in ("standing", "superseded", "withdrawn", "inherited"):
            problems.append(f"decisions:{d['id']} status {st!r} is not standing / superseded / withdrawn / inherited")
        if st in ("standing", "inherited") and not db.body("decisions", d["id"]):
            problems.append(f"decisions:{d['id']} is {st} but data/decisions/{d['id']}.md does not exist")
        if st == "superseded" and not d.get("superseded_by"):
            problems.append(f"decisions:{d['id']} is superseded with no `superseded_by`")
    return problems


def c_work(db: DB):
    problems = []
    if "work" not in db.tables:
        return problems
    for w in db.rows("work"):
        if w.get("state") not in ("open", "done", "blocked", "dropped"):
            problems.append(f"work:{w['id']} state {w.get('state')!r} is not open / done / blocked / dropped")
        if w.get("owner") not in ("agent", "camden"):
            problems.append(f"work:{w['id']} owner {w.get('owner')!r} is not agent / camden")
    return problems


def c_retired(db: DB):
    """A term a ruling retired must not appear in live prose (templates, bodies of standing decisions and open questions)."""
    problems = []
    if "retired" not in db.tables:
        return problems
    for t in db.rows("retired"):
        term = t["term"]
        if not term:
            continue
        pat = re.compile(re.escape(term), re.I)
        for label, text in _live_text_sources(db):
            if label.startswith("retired:") or label.startswith("decisions/") or label.startswith("log:"):
                continue
            if pat.search(text):
                problems.append(f"{label}: uses the retired term {term!r} (retired by {t.get('retired_by', '?')})")
    return problems


def c_headers(db: DB):
    problems = []
    for p in sorted((db.project / "templates").glob("*.md")):
        s = p.read_text(encoding="utf-8")
        if not re.match(r"<!--\s*out:", s.split("\n", 1)[0]):
            problems.append(f"templates/{p.name}: first line must be <!-- out: path -->")
        body = s.split("\n", 1)[1] if "\n" in s else ""
        h1 = [l for l in body.splitlines() if l.startswith("# ")]
        if len(h1) != 1 and not p.name.startswith("channels"):
            problems.append(f"templates/{p.name}: {len(h1)} H1 headings (R5 wants one)")
    return problems


def c_links(db: DB):
    problems = []
    for p in sorted((db.project / "templates").glob("*.md")):
        s = p.read_text(encoding="utf-8")
        m = re.match(r"<!--\s*out:\s*(.+?)\s*-->", s.split("\n", 1)[0])
        outdir = (db.project / m.group(1)).parent if m else db.project
        for lm in re.finditer(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", s):
            href = lm.group(1)
            if re.match(r"^[a-z]+:", href) or href.startswith("{{"):
                continue
            if not (outdir / href).exists() and not (db.project / href).exists():
                problems.append(f"templates/{p.name}: link to {href} resolves to nothing")
    return problems


def c_phase(db: DB, gates: dict):
    problems = []
    if "project" not in db.tables:
        return problems
    phase = db.param("phase")
    if phase not in PHASES:
        problems.append(f"project: phase {phase!r} is not one of {PHASES}")
        return problems
    if phase in ("SOURCING", "BUILDING", "COMPLETE") and "questions" in db.tables:
        for q in db.rows("questions", "status = 'open' AND section = '1'"):
            problems.append(f"phase {phase} with a design question still open: {q['id']} — a change after the freeze is a decision, not a habit")
    fn = gates.get(phase)
    if fn:
        problems += [f"gate {phase}: {x}" for x in (fn(db) or [])]
    return problems


def run_checks(db, checks, gates=None):
    problems = generic_checks(db, gates)
    for fn in checks:
        try:
            problems += list(fn(db) or [])
        except Exception as e:  # a broken check is itself a finding
            problems.append(f"check {fn.__name__} crashed: {e!r}")
    return problems


# ------------------------------------------------------------------ lint — warnings and metrics, never refuses

def lint(db: DB):
    warn, metrics = [], {}
    tpl = {p.name: p.read_text(encoding="utf-8") for p in sorted((db.project / "templates").glob("*.md"))}
    reg = registry()
    # 1 · duplicate paragraphs across templates and bodies (the "same text in two places" smell)
    paras = {}
    sources = list(tpl.items()) + [(f"{k}/{p.name}", p.read_text(encoding="utf-8"))
                                   for k in ("questions", "decisions") if (db.data / k).is_dir()
                                   for p in sorted((db.data / k).glob("*.md"))]
    for name, s in sources:
        for para in re.split(r"\n\s*\n", s):
            key = re.sub(r"\s+", " ", para.strip().lower())
            if len(key) >= 120 and not key.startswith("|") and not key.startswith("{{"):
                paras.setdefault(key, []).append(name)
    dup = {k: v for k, v in paras.items() if len(set(v)) > 1}
    metrics["duplicate_paragraphs"] = len(dup)
    for k, v in list(dup.items())[:20]:
        warn.append(f"duplicate paragraph in {sorted(set(v))}: “{k[:70]}…”")
    # 2 · typed facts that have a placeholder
    typed = 0
    for name, s in tpl.items():
        for m in re.finditer(r"(?i)(next ids?|next question|next decision)[^\n]{0,60}?\b([DQC]-\d{3})", s):
            typed += 1; warn.append(f"templates/{name}: typed next id {m.group(2)} — use {{{{next_id:{m.group(2)[0]}}}}}")
        for m in re.finditer(r"\*Rev (\d{4}-\d{2}-\d{2})", s):
            newest = max([p.stat().st_mtime for p in db.data.glob("*.csv")] + [0])
            if newest and date.fromtimestamp(newest).isoformat() > m.group(1):
                warn.append(f"templates/{name}: Rev {m.group(1)} is older than its data ({date.fromtimestamp(newest).isoformat()}) — re-read it")
    metrics["typed_next_ids"] = typed
    # 3 · cites of superseded decisions without their successor
    sup = {}
    if "decisions" in db.tables:
        sup = {d["id"]: d.get("superseded_by", "") for d in db.rows("decisions") if d.get("status") == "superseded"}
    bad_sup = 0
    for label, text in _live_text_sources(db):
        if label.startswith("decisions/") or label.startswith("log:") or label.startswith("decisions:"):
            continue
        for old, new in sup.items():
            for m in re.finditer(r"(?<!upersedes )(?<!upersedes\*\* )" + re.escape(old) + r"(?!\s*→)(?!\s*\(superseded)", text):
                bad_sup += 1
                if bad_sup <= 20:
                    warn.append(f"{label}: cites superseded {old} without → {new or '?'} (R7)")
    metrics["superseded_cited_bare"] = bad_sup
    # 4 · every other id family cited but defined nowhere (warning only — K/M/P/S/SP/V/T/A)
    dang = 0
    seen = set()
    for label, text in _live_text_sources(db):
        for m in ID_TOKEN.finditer(text):
            i = m.group(0)
            if m.group(1) in LIVE_ID_FAMILIES or i in seen:
                continue
            if reg.where(i) is None:
                dang += 1; seen.add(i)
                if dang <= 15:
                    warn.append(f"{label}: cites {i} — not defined in any table or the archive")
    metrics["dangling_other_ids"] = dang
    # 5 · markdown inside data cells (a fact and its commentary in one field)
    md_cells = 0
    for t in db.tables:
        if t in ("questions", "decisions", "log", "work"):
            continue
        for r in db.rows(t):
            for c, v in r.items():
                if c != "_n" and v and ("**" in v or v.strip().startswith("[")):
                    md_cells += 1
    metrics["markdown_in_cells"] = md_cells
    if md_cells:
        warn.append(f"{md_cells} data cells carry Markdown bold or links — values, not sentences (manual rule)")
    # 5b · links and Contents lines (R5)
    warn += c_links(db)
    for name, s in tpl.items():
        if len(s.splitlines()) > 200 and "Contents" not in s[:4000]:
            warn.append(f"templates/{name}: over 200 lines with no Contents line (R5)")
    # 6 · answered packets waiting for a cycle; Camden items open
    if "questions" in db.tables:
        ans = [q["id"] for q in db.rows("questions", "status = 'open'") if answered(db.body("questions", q["id"]))]
        metrics["answered_waiting"] = len(ans)
        if ans:
            warn.append(f"answered, not yet applied: {' '.join(ans)} — run /rx7-answers")
    if "work" in db.tables:
        metrics["open_agent_work"] = len(db.rows("work", "state = 'open' AND owner = 'agent'"))
        metrics["open_camden_work"] = len(db.rows("work", "state = 'open' AND owner = 'camden'"))
    return warn, metrics


def answered(body: str) -> str:
    """The text Camden wrote under **ANSWER:**, '' if none."""
    m = re.search(r"\*\*ANSWER:\*\*\n((?:>[^\n]*\n?)+)", body)
    if not m:
        return ""
    return " ".join(l.lstrip("> ").strip() for l in m.group(1).splitlines() if l.strip("> ").strip())


# ------------------------------------------------------------------ generic views

def _filters(arg):
    parts = [a.strip() for a in arg.split("|")]
    name, filters, hide = parts[0], {}, set()
    for a in parts[1:]:
        if a.startswith("-"):
            hide |= {c.strip() for c in a[1:].split(",")}
        elif "=" in a:
            k, v = a.split("=", 1); filters[k] = v
    return name, filters, hide


def v_table(db, arg):
    """{{table:name}} renders a whole CSV; {{table:name|col=value}} filters; a leading
    '-col,col' hides columns:  {{table:specs|category=Engine|-id,category}}"""
    name, filters, hide = _filters(arg)
    if name not in db.tables:
        raise SystemExit(f"table view: no table {name!r}")
    cols = [c for c in db.tables[name] if c not in hide]
    rows = [r for r in db.rows(name) if all(r.get(k) == v for k, v in filters.items())]
    pretty = lambda c: c.replace("_", " ").capitalize() if c != "id" else "ID"
    return md_table([pretty(c) for c in cols], [[r[c] for c in cols] for r in rows])


def v_count(db, arg):
    name, filters, _ = _filters(arg)
    rows = [r for r in db.rows(name) if all(r.get(k) == v for k, v in filters.items())]
    return str(len(rows))


def v_cell(db, arg):
    """{{cell:table|key|column}} — one value, so the sentence points at the fact instead of copying it."""
    t, k, c = [x.strip() for x in arg.split("|")]
    r = db.get(t, k)
    if r is None:
        raise SystemExit(f"cell view: {t}:{k} does not exist")
    if c not in r:
        raise SystemExit(f"cell view: {t} has no column {c!r}")
    return r[c]


def v_param(db, arg):
    v = db.param(arg.strip())
    if v == "":
        raise SystemExit(f"param view: no param or project key {arg.strip()!r}")
    return v


def v_next_id(db, arg):
    return registry().next(arg.strip() or "D", db.project)


def v_phase(db, arg):
    return db.param("phase") or "PERMANENT"


def v_packets(db, arg):
    """{{packets:section}} — every open question in that section, its body, in table order."""
    sec = arg.strip()
    out = []
    for q in db.rows("questions", "status = 'open' AND section = ?", sec):
        head = f"**{q['id']} · {q['title']}**"
        if q.get("also"):
            head = f"**{q['id']} / {q['also']} · {q['title']}**"
        opened = f" *({q['opened']})*" if q.get("opened") else ""
        body = db.body("questions", q["id"]).rstrip()
        out.append(head + opened + "\n" + body + "\n")
    return "\n".join(out) if out else "*Nothing open in this section.*"


def v_work(db, arg):
    """{{work}} — the finishing list by block, from data/work.csv (and {{work:agent}} / {{work:camden}} filter by owner)."""
    if "work" not in db.tables:
        return "*No work list yet.*"
    owner = arg.strip()
    rows = db.rows("work")
    blocks, titles = {}, {}
    for w in rows:
        if owner and w["owner"] != owner:
            continue
        blocks.setdefault(w["block"], []).append(w)
        titles.setdefault(w["block"], w.get("block_title", ""))
    out = []
    for b, ws in blocks.items():
        out.append(f"**{b} · {titles[b]}**\n" if titles[b] else f"**{b}**\n")
        for w in ws:
            box = "[x]" if w["state"] == "done" else "[ ]"
            tag = "" if w["owner"] == "camden" else " *(agent)*"
            gate = f" — gate: {w['gate']}" if w.get("gate") and w["state"] != "done" else ""
            out.append(f"- {box} **{w['id']} · {w['item']}**{tag}{gate}{(' ' + w['note']) if w.get('note') else ''}")
        out.append("")
    return "\n".join(out)


def v_open_for_camden(db, arg):
    """{{open_for_camden}} — the one list Camden reads: open packets that want his word, then his work items."""
    out = []
    qs = [q for q in db.rows("questions", "status = 'open'") if not answered(db.body("questions", q["id"]))]
    if qs:
        out.append(md_table(["ID", "Question", "Section", "Ask"], [[q["id"], q["title"], q["section"], q.get("ask", "")] for q in qs]))
    ws = db.rows("work", "state = 'open' AND owner = 'camden'") if "work" in db.tables else []
    if ws:
        out.append(md_table(["ID", "Do", "Gate"], [[w["id"], w["item"], w.get("gate", "")] for w in ws]))
    return "\n\n".join(out) if out else "*Nothing waits on Camden.*"


def v_closed(db, arg):
    rows = db.rows("questions", "status = 'closed'")
    if not rows:
        return "*Nothing closed yet.*"
    groups = {}
    for q in rows:
        groups.setdefault(q.get("closed_on", "") or "—", []).append(q)
    out = []
    for when in sorted(groups, reverse=True):
        out.append(f"**{when}**\n")
        out.append(md_table(["ID", "Closed by", "Outcome"], [[f"`{q['id']}`", q["closer"], q.get("outcome", "")] for q in groups[when]]))
        out.append("")
    return "\n".join(out)


def v_moved(db, arg):
    rows = db.rows("questions", "status = 'moved'")
    if not rows:
        return "*Nothing moved out.*"
    return md_table(["ID", "Went to", "Because"], [[f"`{q['id']}`", q["closer"], q.get("outcome", "")] for q in rows])


def v_banners(db, arg):
    n = int(arg or 6)
    rows = db.rows("log")[-n:] if "log" in db.tables else []
    return "\n\n".join(f"> **{r['date']} · {r['workflow']}.** {r['summary']}" + (f" *({r['ids']})*" if r.get("ids") else "") for r in reversed(rows)) or "*No log yet.*"


def v_log(db, arg):
    rows = db.rows("log") if "log" in db.tables else []
    return md_table(["Date", "Workflow", "IDs", "What"], [[r["date"], r["workflow"], r["ids"], r["summary"]] for r in reversed(rows)]) if rows else "*No log yet.*"


def v_decisions(db, arg):
    """{{decisions:system}} — every standing (or inherited) decision filed under that system, body after body."""
    system = arg.strip()
    out = []
    for d in db.rows("decisions", "system = ? AND status IN ('standing','inherited')", system):
        out.append(db.body("decisions", d["id"]).rstrip() + "\n")
    return "\n".join(out) if out else "*No standing decision under this system.*"


def v_latest(db, arg):
    """{{latest:N}} — the N newest standing decisions by date then id, grouped by date, as the Latest line."""
    n = int(arg or 12)
    rows = [d for d in db.rows("decisions") if d.get("status") == "standing"]
    rows.sort(key=lambda d: (d.get("date", ""), d["id"]))
    rows = rows[-n:]
    by = {}
    for d in rows:
        by.setdefault(d.get("date", "") or "undated", []).append(d)
    parts = ["**" + " · ".join(f"{d['id']} {d['title']}" for d in ds) + f"** ({when})" for when, ds in by.items()]
    return ("**Latest:** " + " · ".join(parts) + f". Next: {registry().next('D', db.project)}.") if parts else "*No decisions yet.*"


GENERIC_VIEWS = {"table": v_table, "count": v_count, "cell": v_cell, "param": v_param, "next_id": v_next_id,
                 "phase": v_phase, "packets": v_packets, "work": v_work, "open_for_camden": v_open_for_camden,
                 "closed": v_closed, "moved": v_moved, "banners": v_banners, "log": v_log,
                 "decisions": v_decisions, "latest": v_latest}

PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_][\w]*)\s*(?::\s*([^}]*?))?\s*\}\}")


def render_template(text: str, views: dict, db: DB) -> str:
    def sub(m):
        name, arg = m.group(1), (m.group(2) or "").strip()
        if name not in views:
            raise SystemExit(f"template placeholder {{{{{name}}}}} has no view")
        return views[name](db, arg)
    out = []
    for line in text.splitlines():
        m = PLACEHOLDER.fullmatch(line.strip())
        if m:
            out.append(sub(m))
        else:
            out.append(PLACEHOLDER.sub(sub, line))
    return "\n".join(out) + "\n"


BANNER = "*Generated by `tools/rx7.py build` from `data/` and `templates/` — edit those, never this file.*"


def build(project: Path, views: dict, db: DB, write=True):
    """Render every template to its declared output. Returns {out_path: text}."""
    outputs = {}
    for tp in sorted((project / "templates").glob("*.md")):
        text = tp.read_text(encoding="utf-8")
        first, _, rest = text.partition("\n")
        m = re.match(r"<!--\s*out:\s*(.+?)\s*-->", first)
        if not m:
            raise SystemExit(f"{tp.name}: first line must be <!-- out: path -->")
        outp = project / m.group(1)
        body = render_template(rest, views, db)
        lines = body.splitlines()
        for k, l in enumerate(lines):
            if l.startswith("# "):
                lines.insert(k + 1, ""); lines.insert(k + 2, BANNER); break
        body = "\n".join(lines) + "\n"
        outputs[outp] = body
    if write:
        for p, body in outputs.items():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, encoding="utf-8", newline="\n")
    return outputs


def build_viewer(project: Path, docs: dict[Path, str], extra: list[Path], title: str):
    """VIEW.html (or view.json's "out") — one self-contained page. Tabs come from view.json:
    {"tabs": [{"title": "Design", "file": "01-DESIGN/DESIGN.md"}, …], "out": "VIEW.html"}"""
    global CURRENT_DOC_DIR
    cfg = json.loads((project / "view.json").read_text(encoding="utf-8"))
    title = cfg.get("title", title)
    panes = []
    for t in cfg["tabs"]:
        p = project / t["file"]
        text = docs.get(p.resolve()) or docs.get(p) or (p.read_text(encoding="utf-8") if p.exists() else "")
        CURRENT_DOC_DIR = p.parent
        body = md_to_html(text, anchors=t.get("anchors", False))
        panes.append((t["title"], slug(t["title"]).lower(), body))
    CURRENT_DOC_DIR = None
    css = VIEW_CSS
    js = VIEW_JS
    nav = "".join(f'<button data-tab="{k}">{html.escape(n)}</button>' for n, k, _ in panes)
    sections = "".join(f'<section id="tab-{k}" class="pane"><div class="doc">{b}</div></section>' for _, k, b in panes)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{css}</style></head>
<body>
<header><span class="brand">{html.escape(title)}</span><nav>{nav}</nav>
<input id="q" type="search" placeholder="filter rows — or type an ID and press Enter" autocomplete="off">
<button id="split" title="show the panes side by side">split</button></header>
<main class="tabs">{sections}</main>
<script>{js}</script></body></html>"""
    outp = project / cfg.get("out", "VIEW.html")
    outp.write_text(page, encoding="utf-8", newline="\n")
    return outp


VIEW_CSS = r"""
:root{--bg:#fbfbf9;--fg:#1c1c1a;--mut:#6b6b66;--line:#dcdcd6;--acc:#2f6f4e;--hi:#fff2a8;--row:#f3f3ee;color-scheme:light dark}
@media(prefers-color-scheme:dark){:root{--bg:#161715;--fg:#e6e6e1;--mut:#9a9a94;--line:#33342f;--acc:#7fc39f;--hi:#5a4d00;--row:#1f201d}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,Segoe UI,Roboto,sans-serif}
header{position:sticky;top:0;z-index:5;display:flex;gap:.5rem;align-items:center;padding:.5rem .8rem;background:var(--bg);border-bottom:1px solid var(--line)}
.brand{font-weight:700;margin-right:.6rem}nav{display:flex;gap:.2rem;flex-wrap:wrap}
nav button,#split{border:1px solid var(--line);background:transparent;color:var(--fg);padding:.3rem .7rem;border-radius:6px;cursor:pointer}
nav button.on{background:var(--acc);color:#fff;border-color:var(--acc)}
#q{margin-left:auto;min-width:18rem;padding:.35rem .6rem;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
main.tabs .pane{display:none}main.tabs .pane.on{display:block}
main.split{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);gap:0;height:calc(100vh - 3rem)}
main.split .pane{display:none;overflow:auto;border-right:1px solid var(--line)}main.split .pane.main{display:block}
.doc{max-width:1100px;margin:0 auto;padding:1rem 1.2rem 4rem}main.split .doc{max-width:none}
h1{font-size:1.5rem;margin:.6rem 0}h2{font-size:1.2rem;margin:1.6rem 0 .5rem;border-bottom:1px solid var(--line);padding-bottom:.2rem}
h3{font-size:1.05rem;margin:1.2rem 0 .4rem}h4{margin:1rem 0 .3rem}
table{border-collapse:collapse;margin:.5rem 0 1rem;font-size:13px;width:100%}th,td{border:1px solid var(--line);padding:.25rem .5rem;text-align:left;vertical-align:top}
th{background:var(--row);position:sticky;top:2.9rem}tr:nth-child(even) td{background:var(--row)}tr.hit td{background:var(--hi)!important}tr.hide{display:none}
code{font:12px ui-monospace,Consolas,monospace;background:var(--row);padding:0 .25rem;border-radius:3px}pre{background:var(--row);padding:.6rem;overflow:auto}
a{color:var(--acc)}a.id{text-decoration:none;border-bottom:1px dotted var(--acc)}
figure.diagram{margin:.5rem 0;overflow:auto;max-height:85vh;border:1px solid var(--line);border-radius:6px;background:#fff}figure.diagram svg{max-width:none;display:block}
blockquote{border-left:3px solid var(--line);margin:.4rem 0;padding:.1rem .8rem;color:var(--mut)}
.box{font-size:1.1em}.flash{animation:fl 1.6s}@keyframes fl{from{background:var(--hi)}to{background:transparent}}
"""

VIEW_JS = r"""
const ID=/\b(L\d-(?:[PMS]\d?|BLW) \d+|D[12] \d+|DP-[A-Z]+(?:-[A-Z])? \d+|[DQC]-\d{3}|O\d{1,2}|A\d{1,2}|F\d{1,2}|K\d{1,2})\b/g;
const slug=s=>s.replace(/[^A-Za-z0-9]+/g,'-').replace(/^-|-$/g,'');
const defs=new Set([...document.querySelectorAll('[id^="row-"],[id^="D-"],[id^="Q-"],[id^="C-"]')].map(e=>e.id));
function linkify(node){for(const el of node.querySelectorAll('td,li,p')){if(el.querySelector('table'))continue;
 const h=('>'+el.innerHTML+'<').replace(/>([^<]+)</g,(m,t)=>'>'+t.replace(ID,x=>{const s=/^[DQC]-/.test(x)?x:'row-'+slug(x);return defs.has(s)?'<a class="id" href="#'+s+'">'+x+'</a>':x;})+'<');el.innerHTML=h.slice(1,-1);}}
document.querySelectorAll('.pane').forEach(linkify);
const panes=[...document.querySelectorAll('.pane')],btns=[...document.querySelectorAll('nav button')],main=document.querySelector('main');
function show(k,push=true){if(main.classList.contains('split')){const p=document.getElementById('tab-'+k);p.classList.toggle('main');
  if(!main.querySelector('.pane.main'))p.classList.add('main');btns.forEach(b=>b.classList.toggle('on',document.getElementById('tab-'+b.dataset.tab).classList.contains('main')));return;}
 panes.forEach(p=>p.classList.toggle('on',p.id==='tab-'+k));btns.forEach(b=>b.classList.toggle('on',b.dataset.tab===k));if(push)history.replaceState(null,'','#'+k);}
btns.forEach(b=>b.onclick=()=>show(b.dataset.tab));
document.getElementById('split').onclick=()=>{main.classList.toggle('split');main.classList.toggle('tabs');const sp=main.classList.contains('split');
 if(sp){panes.slice(0,3).forEach(p=>p.classList.add('main'));btns.forEach((b,i)=>b.classList.toggle('on',i<3));}
 else{panes.forEach(p=>p.classList.remove('main'));const on=panes.find(p=>p.classList.contains('on'))||panes[0];show(on.id.slice(4));}
 document.getElementById('split').textContent=sp?'tabs':'split';};
function jump(id){const el=document.getElementById(id);if(!el)return false;const pane=el.closest('.pane');
 if(main.classList.contains('split')){if(!pane.classList.contains('main'))show(pane.id.slice(4));}else if(!pane.classList.contains('on'))show(pane.id.slice(4));
 el.scrollIntoView({block:'center'});el.classList.remove('flash');void el.offsetWidth;el.classList.add('flash');return true;}
document.addEventListener('click',e=>{const a=e.target.closest('a.id');if(a){e.preventDefault();jump(a.getAttribute('href').slice(1));}});
const q=document.getElementById('q');let t;
q.addEventListener('input',()=>{clearTimeout(t);t=setTimeout(()=>{const v=q.value.trim().toLowerCase();
 document.querySelectorAll('.pane.on tbody tr, .pane.main tbody tr').forEach(r=>{const hit=v&&r.textContent.toLowerCase().includes(v);r.classList.toggle('hit',!!hit);r.classList.toggle('hide',!!v&&!hit);});},120);});
q.addEventListener('keydown',e=>{if(e.key==='Enter'){const v=q.value.trim();if(jump(/^[DQC]-/.test(v)?v:'row-'+slug(v))){q.value='';q.dispatchEvent(new Event('input'));}}
 if(e.key==='Escape'){q.value='';q.dispatchEvent(new Event('input'));}});
const h=location.hash.slice(1);if(h&&document.getElementById('tab-'+h))show(h,false);else if(h&&document.getElementById(h)){show(panes[0].id.slice(4),false);setTimeout(()=>jump(h),50);}else show(panes[0].id.slice(4),false);
"""


# ------------------------------------------------------------------ status

def status(projects):
    """One screen: every project's phase, next ids, what waits on whom, the last log lines, the check."""
    reg = registry(fresh=True)
    print(f"next ids (tree-wide): D {reg.next('D')} · Q {reg.next('Q')} · C {reg.next('C')}")
    if reg.dups:
        print("  !! duplicate ids:", "; ".join(reg.dups))
    for d in projects:
        db = DB(d)
        views, checks, _, gates = load_views(d)
        name = d.relative_to(ROOT).as_posix()
        phase = db.param("phase") or "PERMANENT"
        line = f"== {name}  [{phase}]"
        if "questions" in db.tables:
            opens = db.rows("questions", "status = 'open'")
            ans = [q["id"] for q in opens if answered(db.body("questions", q["id"]))]
            line += f"  open Q {len(opens)}" + (f" (answered, unapplied: {' '.join(ans)})" if ans else "")
            try:
                line += f"  next D {reg.next('D', d)} · Q {reg.next('Q', d)}"
            except SystemExit as e:
                line += f"  !! {e}"
        if "work" in db.tables:
            ag = len(db.rows("work", "state = 'open' AND owner = 'agent'"))
            cm = len(db.rows("work", "state = 'open' AND owner = 'camden'"))
            line += f"  work agent {ag} · camden {cm}"
        print(line)
        for r in (db.rows("log")[-3:] if "log" in db.tables else []):
            print(f"   {r['date']} {r['workflow']:<10} {r['summary'][:110]}")
        problems = run_checks(db, checks, gates)
        warn, metrics = lint(db)
        print(f"   check: {'clean' if not problems else str(len(problems)) + ' problem(s)'} · lint: {len(warn)} warning(s) · " +
              " · ".join(f"{k} {v}" for k, v in metrics.items() if v))
        for p in problems[:5]:
            print("     ✗", p)
    trig = ROOT / "tools" / "triggers.py"
    if trig.exists():
        import subprocess
        subprocess.run([sys.executable, str(trig)], check=False)


# ------------------------------------------------------------------ CLI

def parse_kv(args):
    out = {}
    for a in args:
        if "=" not in a:
            raise SystemExit(f"expected col=value, got {a!r}")
        k, v = a.split("=", 1)
        out[k] = v
    return out


def show_row(r):
    w = max(len(k) for k in r) if r else 0
    return "\n".join(f"{k:<{w}}  {v}" for k, v in r.items() if k != "_n")


QUESTION_BODY = """{ask}

**Why it matters:** {why}

**Options:** (a) … · (b) …

**Recommend:** … **Flip it if:** … **Costs:** …

**Blocks:** {blocks}

**ANSWER:**
>
>
"""

DECISION_BODY = """**{id} — {title}.** {who}, {date}{closes}. Reasoning: …{supersedes}

"""


def cmd_new(db: DB, project: Path, args):
    """new Q "title" section=1 ask=yes/no blocks=… why=…   |   new D "title" system=… closes=Q-… supersedes=D-… who=Camden"""
    fam, title = args[0].upper(), args[1]
    kv = parse_kv(args[2:])
    reg = registry(fresh=True)
    nid = reg.next(fam, project)
    today = date.today().isoformat()
    if fam == "Q":
        row = {"id": nid, "section": kv.get("section", "1"), "title": title, "opened": today, "status": "open",
               "owner": kv.get("owner", "camden"), "ask": kv.get("ask", "one word"), "blocks": kv.get("blocks", ""),
               "closer": "", "closed_on": "", "outcome": "", "also": kv.get("also", "")}
        db.add("questions", {k: v for k, v in row.items() if k in db.tables["questions"]})
        p = db.data / "questions" / f"{nid}.md"; p.parent.mkdir(exist_ok=True)
        p.write_text(QUESTION_BODY.format(ask=kv.get("text", "…"), why=kv.get("why", "…"), blocks=kv.get("blocks", "nothing")), encoding="utf-8", newline="\n")
    elif fam == "D":
        row = {"id": nid, "system": kv.get("system", ""), "title": title, "date": today, "status": "standing",
               "supersedes": kv.get("supersedes", ""), "superseded_by": "", "closes": kv.get("closes", ""), "also": ""}
        db.add("decisions", {k: v for k, v in row.items() if k in db.tables["decisions"]})
        p = db.data / "decisions" / f"{nid}.md"; p.parent.mkdir(exist_ok=True)
        closes = f", answering `{kv['closes']}`" if kv.get("closes") else ""
        sup = f" Supersedes {kv['supersedes']}." if kv.get("supersedes") else ""
        p.write_text(DECISION_BODY.format(id=nid, title=title, who=kv.get("who", "Camden's call"), date=today, closes=closes, supersedes=sup), encoding="utf-8", newline="\n")
        for old in [x.strip() for x in kv.get("supersedes", "").split(",") if x.strip()]:
            if db.get("decisions", old):
                db.set("decisions", old, {"status": "superseded", "superseded_by": nid})
        for q in [x.strip() for x in kv.get("closes", "").split(",") if x.strip()]:
            if db.get("questions", q):
                db.set("questions", q, {"status": "closed", "closer": nid, "closed_on": today})
    else:
        raise SystemExit("new: Q or D")
    print(f"{nid}  {p.relative_to(project)}")
    return nid


def main(argv):
    proj = None
    if argv[:1] == ["-p"]:
        proj = argv[1]; argv = argv[2:]
    if argv[:1] == ["status"]:
        status(all_projects()); return 0
    if argv[:1] == ["-a"]:
        rc = 0
        for d in all_projects():
            print(f"== {d.relative_to(ROOT)}")
            rc |= main(["-p", str(d)] + argv[1:])
        return rc
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    cmd, args = argv[0], argv[1:]
    project = find_project(proj)
    db = DB(project)
    views, checks, pre_build, gates = load_views(project)

    if cmd == "tables":
        for t, cols in db.tables.items():
            n = db.q(f'SELECT COUNT(*) AS n FROM "{t}"')[0]["n"]
            print(f"{t:<18} {n:>4} rows   {', '.join(cols)}")
    elif cmd == "get":
        t, key = args[0], args[1]
        r = db.get(t, key)
        if not r:
            raise SystemExit(f"{t}: {key!r} not found")
        print(show_row(r))
        if t in ("questions", "decisions"):
            print("---\n" + db.body(t, r[db.key(t)]))
    elif cmd == "find":
        needle = " ".join(args).lower()
        for t, cols in db.tables.items():
            for r in db.rows(t):
                if any(needle in str(v).lower() for v in r.values()):
                    print(f"{t}:{r[cols[0]]}  " + " | ".join(str(r[c]) for c in cols[1:] if r[c])[:160])
        for kind in ("questions", "decisions"):
            for p in sorted((db.data / kind).glob("*.md")) if (db.data / kind).is_dir() else []:
                if needle in p.read_text(encoding="utf-8").lower():
                    print(f"{kind}/{p.name}")
    elif cmd == "sql":
        for r in db.q(" ".join(args)):
            print(" | ".join(str(v) for k, v in dict(r).items() if k != "_n"))
    elif cmd == "set":
        t, key = args[0], args[1]
        before, after = db.set(t, key, parse_kv(args[2:]))
        for k in after:
            if before[k] != after[k]:
                print(f"{t}:{key}  {k}: {before[k]!r} → {after[k]!r}")
    elif cmd == "add":
        t = args[0]; after = None; rest = args[1:]
        if "--after" in rest:
            i = rest.index("--after"); after = rest[i + 1]; rest = rest[:i] + rest[i + 2:]
        r = db.add(t, parse_kv(rest), after)
        print(f"{t}: added\n" + show_row(r))
    elif cmd == "del":
        n = db.delete(args[0], args[1]); print(f"{args[0]}: deleted {n}")
    elif cmd == "new":
        cmd_new(db, project, args)
    elif cmd == "ids":
        reg = registry(fresh=True)
        if args[:1] == ["next"]:
            print(reg.next(args[1].upper(), project))
        elif args[:1] == ["where"]:
            for i in args[1:]:
                print(f"{i}: {reg.where(i) or 'NOT DEFINED'}")
        elif args[:1] == ["dups"]:
            print("\n".join(reg.dups) or "no duplicates")
        else:
            raise SystemExit("ids next D|Q|C  ·  ids where <id>…  ·  ids dups")
    elif cmd == "log":
        r = db.append_log(args[0], args[1], " ".join(args[2:]))
        print(f"log: {r['id']} {r['date']} {r['workflow']} — {r['summary']}")
    elif cmd == "lint":
        warn, metrics = lint(db)
        if "--json" in args:
            print(json.dumps({"project": project.relative_to(ROOT).as_posix(), "warnings": warn, "metrics": metrics}, ensure_ascii=False))
        else:
            for w in warn:
                print("  ~", w)
            print(f"lint: {len(warn)} warning(s) · " + " · ".join(f"{k} {v}" for k, v in metrics.items()))
    elif cmd in ("check", "build"):
        problems = run_checks(db, checks, gates)
        for p in problems:
            print("  ✗", p)
        if problems:
            print(f"{len(problems)} problem(s)")
            if cmd == "build":
                print("build refused — fix the data first"); return 1
        else:
            print("check: clean")
        if cmd == "build":
            if pre_build:
                for line in pre_build(project, db):
                    print("  " + line)
            docs = build(project, views, db)
            for p in docs:
                print("  wrote", p.relative_to(project))
            if (project / "view.json").exists():
                vp = build_viewer(project, {p.resolve(): t for p, t in docs.items()}, [], project.name)
                print("  wrote", vp.relative_to(project))
    else:
        raise SystemExit(f"unknown command {cmd!r}; try --help")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

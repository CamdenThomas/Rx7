#!/usr/bin/env python3
"""rx7 — the project data tool.  Python 3.10+, standard library only.

A project keeps its facts in  data/*.csv  (one row per thing, one home per fact)
and its prose in  templates/*.md.  `build` renders the documents and VIEW.html
from both; nothing generated is ever edited by hand.

    python tools/rx7.py tables                      list tables and columns
    python tools/rx7.py get   <table> <key>         one row  (key = first column, or col=value)
    python tools/rx7.py find  <text>                every row in every table containing text
    python tools/rx7.py sql   "<select …>"          query the in-memory database
    python tools/rx7.py set   <table> <key> col=value …     change fields on one row
    python tools/rx7.py add   <table> col=value …           new row (key column required)
    python tools/rx7.py del   <table> <key>
    python tools/rx7.py check                       integrity checks, no output written
    python tools/rx7.py build                       check, then render documents + VIEW.html

Project selection: -p <name> (a folder under 02-PROJECTS, or 00-CAR / 01-REFERENCE),
-a for every project, or run from inside the project folder. A project is any
folder holding data/ and templates/; an optional views.py beside them supplies
named views and checks. Every project can use {{table:name}} with no views.py.
"""
import csv, html, io, json, re, sqlite3, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------ database

class DB:
    """All CSVs of one project, loaded into an in-memory SQLite database."""

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
        w = f" WHERE {where}" if where else ""
        return [dict(r) for r in self.q(f'SELECT * FROM "{table}"{w} ORDER BY _n', *args)]

    def get(self, table, key):
        keycol = self.tables[table][0]
        if "=" in key:
            col, val = key.split("=", 1)
        else:
            col, val = keycol, key
        r = self.q(f'SELECT * FROM "{table}" WHERE "{col}" = ?', val)
        return dict(r[0]) if r else None

    def key(self, table):
        return self.tables[table][0]

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
                m = re.match(r"\*\*([DQ]-\d{3})", text)
                if m:
                    attr = f' id="{m.group(1)}"'
                m = re.match(r"\*\*((?:L\d-[PMS]\d?|D[12]|DP-[A-Z]+))\*\*", text)
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
            m2 = re.search(r"\b(DP-[A-Z]+)\b", t)
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
                svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
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
ID_RE = re.compile(r"(?:L\d-[PMS]\d? \d+|D[12] \d+|DP-[A-Z]+ \d+|O\d{1,2}|A\d{1,2}|F\d{1,2}|K\d{1,2}|[DQ]-\d{3}|CAN[12][HL]|STUD|\d{1,2})")


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
        for p in (Path(name), ROOT / name, ROOT / "02-PROJECTS" / name):
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
    """Every folder in the tree holding data/ and templates/ (00-CAR, 01-REFERENCE, each 02-PROJECTS/*)."""
    out = []
    for d in sorted(ROOT.glob("*/")) + sorted((ROOT / "02-PROJECTS").glob("*/")):
        if (d / "data").is_dir() and (d / "templates").is_dir() and "99-ARCHIVE" not in str(d):
            out.append(d)
    return out


def load_views(project: Path):
    vp = project / "views.py"
    if not vp.exists():
        return dict(GENERIC_VIEWS), []
    import importlib.util
    spec = importlib.util.spec_from_file_location("views", vp)
    mod = importlib.util.module_from_spec(spec)
    mod.rx7 = sys.modules[__name__]
    spec.loader.exec_module(mod)
    return {**GENERIC_VIEWS, **getattr(mod, "VIEWS", {})}, getattr(mod, "CHECKS", [])


def generic_checks(db: DB):
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
    return problems


def run_checks(db, checks):
    problems = generic_checks(db)
    for fn in checks:
        try:
            problems += list(fn(db) or [])
        except Exception as e:  # a broken check is itself a finding
            problems.append(f"check {fn.__name__} crashed: {e!r}")
    return problems


def v_table(db, arg):
    """{{table:name}} renders a whole CSV; {{table:name|col=value}} filters; a leading
    '-col,col' hides columns:  {{table:specs|category=Engine|-id,category}}"""
    parts = [a.strip() for a in arg.split("|")]
    name, filters, hide = parts[0], {}, set()
    for a in parts[1:]:
        if a.startswith("-"):
            hide |= {c.strip() for c in a[1:].split(",")}
        elif "=" in a:
            k, v = a.split("=", 1); filters[k] = v
    if name not in db.tables:
        raise SystemExit(f"table view: no table {name!r}")
    cols = [c for c in db.tables[name] if c not in hide]
    rows = [r for r in db.rows(name) if all(r.get(k) == v for k, v in filters.items())]
    pretty = lambda c: c.replace("_", " ").capitalize() if c != "id" else "ID"
    return md_table([pretty(c) for c in cols], [[r[c] for c in cols] for r in rows])


def v_count(db, arg):
    name, _, cond = arg.partition("|")
    rows = db.rows(name)
    if cond and "=" in cond:
        k, v = cond.split("=", 1); rows = [r for r in rows if r.get(k) == v]
    return str(len(rows))


GENERIC_VIEWS = {"table": v_table, "count": v_count}

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
        # banner goes right after the H1
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
    """VIEW.html — one self-contained page. Tabs come from view.json:
    {"tabs": [{"title": "Design", "file": "01-DESIGN/DESIGN.md"}, …]}"""
    global CURRENT_DOC_DIR
    cfg = json.loads((project / "view.json").read_text(encoding="utf-8"))
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
    (project / "VIEW.html").write_text(page, encoding="utf-8", newline="\n")
    return project / "VIEW.html"


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
figure.diagram{margin:.5rem 0;overflow:auto;border:1px solid var(--line);border-radius:6px;background:#fff}figure.diagram svg{max-width:100%;height:auto;display:block}
blockquote{border-left:3px solid var(--line);margin:.4rem 0;padding:.1rem .8rem;color:var(--mut)}
.box{font-size:1.1em}.flash{animation:fl 1.6s}@keyframes fl{from{background:var(--hi)}to{background:transparent}}
"""

VIEW_JS = r"""
const ID=/\b(L\d-[PMS]\d? \d+|D[12] \d+|DP-[A-Z]+ \d+|[DQ]-\d{3}|O\d{1,2}|A\d{1,2}|F\d{1,2}|K\d{1,2})\b/g;
const slug=s=>s.replace(/[^A-Za-z0-9]+/g,'-').replace(/^-|-$/g,'');
const defs=new Set([...document.querySelectorAll('[id^="row-"],[id^="D-"],[id^="Q-"]')].map(e=>e.id));
// auto-link IDs that have a definition row
function linkify(node){for(const el of node.querySelectorAll('td,li,p')){if(el.querySelector('table'))continue;
 const h=('>'+el.innerHTML+'<').replace(/>([^<]+)</g,(m,t)=>'>'+t.replace(ID,x=>{const s=/^[DQ]-/.test(x)?x:'row-'+slug(x);return defs.has(s)?'<a class="id" href="#'+s+'">'+x+'</a>':x;})+'<');el.innerHTML=h.slice(1,-1);}}
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
q.addEventListener('keydown',e=>{if(e.key==='Enter'){const v=q.value.trim();if(jump(/^[DQ]-/.test(v)?v:'row-'+slug(v))){q.value='';q.dispatchEvent(new Event('input'));}}
 if(e.key==='Escape'){q.value='';q.dispatchEvent(new Event('input'));}});
const h=location.hash.slice(1);if(h&&document.getElementById('tab-'+h))show(h,false);else if(h&&document.getElementById(h)){show(panes[0].id.slice(4),false);setTimeout(()=>jump(h),50);}else show(panes[0].id.slice(4),false);
"""


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


def main(argv):
    proj = None
    if argv[:1] == ["-p"]:
        proj = argv[1]; argv = argv[2:]
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
    views, checks = load_views(project)

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
    elif cmd == "find":
        needle = " ".join(args).lower()
        for t, cols in db.tables.items():
            for r in db.rows(t):
                if any(needle in str(v).lower() for v in r.values()):
                    print(f"{t}:{r[cols[0]]}  " + " | ".join(str(r[c]) for c in cols[1:] if r[c])[:160])
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
    elif cmd in ("check", "build"):
        problems = run_checks(db, checks)
        for p in problems:
            print("  ✗", p)
        if problems:
            print(f"{len(problems)} problem(s)")
            if cmd == "build":
                print("build refused — fix the data first"); return 1
        else:
            print("check: clean")
        if cmd == "build":
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

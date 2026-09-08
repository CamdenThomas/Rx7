# -*- coding: utf-8 -*-
"""scaffold.py — /rx7-propose: build a new project's skeleton from the standard.

    python tools/scaffold.py <name> --kind electrical|electronics|mechanical|body|software "<goal in one sentence>"

Creates 02-PROJECTS/<name>/ with data/ (project, questions, decisions, work, log, retired + the kind's
seed tables), templates/ (README, DESIGN, SHOPPING-LIST, INSTALL, QUESTIONS, DECISIONS, LOG), view.json,
and writes the goal as the project's first draft decision (status standing, Camden's words) so the
agent's opening question set has something to cite. Refuses if the folder exists.
"""
import csv, io, sys, re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import rx7  # noqa: E402

argv = sys.argv[1:]
kind = "mechanical"
if "--kind" in argv:
    i = argv.index("--kind"); kind = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
args = [a for a in argv if not a.startswith("--")]
if len(args) < 2:
    raise SystemExit(__doc__)
name, goal = args[0], args[1]
P = ROOT / "02-PROJECTS" / name
if P.exists():
    raise SystemExit(f"{P} exists — pick another name or /rx7-plan the one that is there")
D = P / "data"; T = P / "templates"
for d in (D, D / "questions", D / "decisions", T, P / "reviews", P / "01-DESIGN", P / "02-SHOPPING", P / "03-INSTALL"):
    d.mkdir(parents=True)

SEED = {
    "electrical": {"devices": "id,zone,device,ident,terminals,ground", "cavities": "id,housing,cav,circuit,src,src_note,awg,colour,state,lands_on",
                   "housings": "code,leg,class,leg_side,box_side,cavs,wedgelocks,where,note", "loads": "id,circuit,ch,rated,design_a,measured_a,basis"},
    "electronics": {"modules": "id,module,board,location,logic_power,heavy_power,drops,state,owns", "sensors": "id,signal,at_the_drop,on_the_wire,calibration,can,note",
                    "can_messages": "id,name,sender,rate_hz,dlc,status,note"},
    "mechanical": {"components": "id,system,component,part_no,spec,source,state,note", "fasteners": "id,joint,size,grade,torque,source,note",
                   "measurements": "id,what,value,unit,taken_on,tool,note"},
    "body": {"components": "id,area,component,part_no,spec,source,state,note", "measurements": "id,what,value,unit,taken_on,tool,note"},
    "software": {"modules": "id,module,language,target,state,note", "interfaces": "id,from,to,protocol,spec,note"},
}
common = {
    "parts": "id,store,section,sku,item,spec,qty,unit,unit_usd,basis,used_for,status,need_rule,target",
    "steps": "id,phase,step,gate,measure,value,state,done_on,note",
    "params": "key,value,note",
}
for t, hdr in {**common, **SEED.get(kind, SEED["mechanical"])}.items():
    (D / f"{t}.csv").write_text(hdr + "\n", encoding="utf-8", newline="\n")


def w(t, header, rows):
    o = io.StringIO(); wr = csv.writer(o, lineterminator="\n"); wr.writerow(header); wr.writerows(rows)
    (D / f"{t}.csv").write_text(o.getvalue(), encoding="utf-8", newline="\n")


reg = rx7.registry(fresh=True)
# a fresh number range: the next free hundred above every range in use
used = set()
for d in rx7.all_projects():
    db = rx7.DB(d)
    r = db.param("range_D")
    if r and "-" in r:
        used.add(int(r.split("-")[0]) // 100)
block = max(used or {4}) + 1
lo, hi = block * 100, block * 100 + 99
today = date.today().isoformat()
w("project", ["key", "value", "note"], [["name", name, ""], ["kind", kind, "electrical · electronics · mechanical · body · software"],
   ["goal", goal, ""], ["phase", "PROPOSED", " · ".join(rx7.PHASES)], ["opened", today, ""],
   ["range_D", f"{lo}-{hi}", "this project's decision numbers"], ["range_Q", f"{lo}-{hi}", "this project's question numbers"], ["range_C", f"{lo}-{hi}", "critique findings"]])
w("questions", ["id", "section", "title", "opened", "status", "owner", "ask", "closer", "closed_on", "outcome", "blocks", "also"], [])
did = f"D-{lo:03d}"
w("decisions", ["id", "system", "title", "date", "status", "supersedes", "superseded_by", "closes", "also"],
  [[did, "Scope", "The goal, in Camden's words (draft — ruled when planning starts)", today, "standing", "", "", "", ""]])
(D / "decisions" / f"{did}.md").write_text(f"**{did} — The goal.** Camden, {today}: *{goal}*\n\nThis is the project's charter. `/rx7-plan` turns it into the opening question set and the first work list; the first ruling that changes it supersedes this entry.\n", encoding="utf-8", newline="\n")
w("work", ["id", "block", "block_title", "item", "owner", "state", "gate", "note"],
  [["A1", "A", "Propose", "Read 00-CAR and every sibling project's boundary tables; write the opening question set (every call only Camden can make) and the first work list", "agent", "open", "", ""],
   ["A2", "A", "Propose", "Answer the opening packets", "camden", "open", "A1", ""]])
w("log", ["id", "date", "workflow", "ids", "summary"], [["L001", today, "propose", did, f"Project proposed: {goal[:120]}"]])
w("retired", ["term", "retired_by", "note"], [])

TITLE = name.replace("-", " ").upper()
(T / "README.md").write_text(f"""<!-- out: README.md -->
# {TITLE} — 1982 Mazda RX-7 (FB)

*Rev {today} · owns: the map of this project. Facts are `data/`'s, prose is `templates/`', rendered by `tools/rx7.py -p {name} build`. Phase **{{{{phase}}}}**.*

**Goal.** {{{{param:goal}}}}

| Step | Folder | What it is |
|---|---|---|
| **1 · Understand** | [`01-DESIGN/`](01-DESIGN/DESIGN.md) | The design — every fact a reviewer needs, no prices, no build steps |
| **2 · Buy** | [`02-SHOPPING/`](02-SHOPPING/SHOPPING-LIST.md) | Every part and tool by store, with quantities |
| **3 · Build** | [`03-INSTALL/`](03-INSTALL/INSTALL.md) | The job in order, with every measurement box |

**Next IDs:** decisions from {{{{next_id:D}}}} · questions from {{{{next_id:Q}}}}.

[`QUESTIONS.md`](QUESTIONS.md) is what waits on Camden and the finishing list; [`DECISIONS.md`](DECISIONS.md) is why it is the way it is; [`LOG.md`](LOG.md) is what happened when.
""", encoding="utf-8", newline="\n")
(T / "DESIGN.md").write_text(f"""<!-- out: 01-DESIGN/DESIGN.md -->
# {TITLE} — THE DESIGN

*Rev {today} · owns: the complete design. A design-only reviewer must be able to judge it from this file alone.*

## What it is

{{{{param:goal}}}}

## 1 · Scope and boundary

What this project owns, what it hands to or inherits from other projects (read their tables live with `db.other()` in `views.py`, never retype them).

## 2 · The design

{{{{table:components}}}}
""" if kind in ("mechanical", "body") else f"""<!-- out: 01-DESIGN/DESIGN.md -->
# {TITLE} — THE DESIGN

*Rev {today} · owns: the complete design. A design-only reviewer must be able to judge it from this file alone.*

## What it is

{{{{param:goal}}}}

## 1 · Scope and boundary

What this project owns, what it hands to or inherits from other projects (read their tables live with `db.other()` in `views.py`, never retype them).

## 2 · The design

*(tables go here as `{{{{table:…}}}}` lines)*
""", encoding="utf-8", newline="\n")
(T / "SHOPPING-LIST.md").write_text(f"""<!-- out: 02-SHOPPING/SHOPPING-LIST.md -->
# {TITLE} — THE SHOPPING LIST

*Rev {today} · owns: every part and tool, by store. A buyer who never sees the design must be able to buy from this file alone.*

{{{{table:parts|-need_rule,target}}}}
""", encoding="utf-8", newline="\n")
(T / "INSTALL.md").write_text(f"""<!-- out: 03-INSTALL/INSTALL.md -->
# {TITLE} — INSTALLATION

*Rev {today} · owns: the job in order. A builder who only follows instructions must succeed from this file alone. Steps are `data/steps.csv`; `/rx7-build` ticks them and records every measurement.*

{{{{table:steps|-done_on}}}}
""", encoding="utf-8", newline="\n")
(T / "QUESTIONS.md").write_text(f"""<!-- out: QUESTIONS.md -->
# QUESTIONS — {name}

*Rev {today} · owns: what waits on Camden, and the finishing list. Packets are `data/questions/<id>.md` — answer under **ANSWER:** and say "I answered questions". Every packet must be readable on its own: the ask, why it matters, the options with their consequences, one recommendation, what it blocks, and a one-word ask.*

{{{{banners:6}}}}

---

## 0 · The finishing task list

{{{{work}}}}

---

## 1 · Before the design freezes

{{{{packets:1}}}}

## 2 · After — validation and tuning

{{{{packets:2}}}}

---

## 3 · Closed

{{{{closed}}}}

## 4 · Moved out of this project

{{{{moved}}}}
""", encoding="utf-8", newline="\n")
(T / "DECISIONS.md").write_text(f"""<!-- out: DECISIONS.md -->
# DECISIONS — {name}

Every decision that governs this project, by system. A decision is never edited; it is superseded by a newer one that names it (status `superseded` in `data/decisions.csv`), and the superseded one leaves this file while its body stays in `data/decisions/` as history.

{{{{latest:10}}}}

## Contents

Scope

---

## Scope

{{{{decisions:Scope}}}}
""", encoding="utf-8", newline="\n")
(T / "LOG.md").write_text(f"""<!-- out: LOG.md -->
# LOG — {name}

*Rendered from `data/log.csv` — one row per workflow run, newest first.*

{{{{log}}}}
""", encoding="utf-8", newline="\n")
(P / "view.json").write_text('{"tabs": [\n  {"title": "Design", "file": "01-DESIGN/DESIGN.md", "anchors": true},\n  {"title": "Shopping", "file": "02-SHOPPING/SHOPPING-LIST.md"},\n  {"title": "Install", "file": "03-INSTALL/INSTALL.md"},\n  {"title": "Questions", "file": "QUESTIONS.md"},\n  {"title": "Decisions", "file": "DECISIONS.md", "anchors": true},\n  {"title": "Log", "file": "LOG.md"}\n]}\n', encoding="utf-8", newline="\n")
print(f"scaffolded 02-PROJECTS/{name}  kind={kind}  ids {lo}-{hi}  first decision {did}\nnext: python tools/rx7.py -p {name} build")

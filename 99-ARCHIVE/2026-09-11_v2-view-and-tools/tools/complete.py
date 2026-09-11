# -*- coding: utf-8 -*-
"""complete.py — /rx7-complete: fold a finished project into the manual, three ways.

    python tools/complete.py <project> --system <name> [--dry]

Gate (refuses otherwise): phase BUILDING with every steps.csv row done, no open question, build clean.
Then, dry-run first:
  1. INFORMATION  data/*.csv (minus the process tables), views.py, diagrams/, view.json, the DESIGN /
     config templates  →  00-CAR/systems/<system>/  — with a strip report: every D-/Q- cite and every
     "why" sentence the manual must not carry is listed for the agent to rewrite (the script never guesses).
  2. SERVICE      the INSTALL template's tests, label rules, recovery pages → systems/<system>/templates/SERVICE.md
     (a skeleton the agent completes); steps.csv rows marked `interval` → 00-CAR/data/intervals.csv rows.
  3. PROCESS      questions, decisions, work, log, reviews, SHOPPING, the build-phase templates
                  → 99-ARCHIVE/<date>_<project>/ with a README.
  4. 00-CAR: as_fitted row, planned P- → mods M- (listed for the agent to confirm), then `build -a`.
The project folder is removed last, only when everything above wrote clean.
"""
import csv, io, re, shutil, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import rx7  # noqa: E402

DRY = "--dry" in sys.argv
argv = [a for a in sys.argv[1:] if a != "--dry"]
if "--system" not in argv or len(argv) < 3:
    raise SystemExit(__doc__)
system = argv[argv.index("--system") + 1]
name = [a for a in argv if a != "--system" and a != system][0]
P = rx7.find_project(name)
db = rx7.DB(P)
PROCESS_TABLES = {"questions", "decisions", "work", "log", "retired", "carts", "migration"}
today = date.today().isoformat()

# ---- gate
problems = []
if db.param("phase") != "BUILDING":
    problems.append(f"phase is {db.param('phase')!r}, not BUILDING")
if "steps" in db.tables:
    left = [s["id"] for s in db.rows("steps") if s.get("state") != "done"]
    if left:
        problems.append(f"{len(left)} install step(s) not done: {' '.join(left[:8])}")
else:
    problems.append("no steps.csv — the install plan is not data yet, so completion cannot be gated")
opn = [q["id"] for q in db.rows("questions", "status = 'open'")]
if opn:
    problems.append(f"open questions: {' '.join(opn)} — close or move each before completing")
views, checks, _, gates = rx7.load_views(P)
problems += rx7.run_checks(db, checks, gates)
if problems:
    print("complete: GATE NOT MET")
    for p in problems:
        print("  ✗", p)
    sys.exit(1)

SYS = ROOT / "00-CAR" / "systems" / system
ARCH = ROOT / "99-ARCHIVE" / f"{today}_{P.name}"
plan = []          # (action, src, dst)
strip = []         # (file, line) — D-/Q- cites or why-sentences the manual must not keep

def cp(src, dst):
    plan.append(("copy", src, dst))

# 1 information
for p in sorted((P / "data").glob("*.csv")):
    if p.stem not in PROCESS_TABLES:
        cp(p, SYS / "data" / p.name)
for sub in ("diagrams",):
    for p in (P / "01-DESIGN" / sub).glob("*") if (P / "01-DESIGN" / sub).is_dir() else []:
        cp(p, SYS / "diagrams" / p.name)
for f in ("views.py", "harness.py", "view.json"):
    if (P / f).exists():
        cp(P / f, SYS / f)
for t in sorted((P / "templates").glob("*.md")):
    if t.stem in ("QUESTIONS", "DECISIONS", "LOG", "SHOPPING-LIST", "README"):
        continue
    cp(t, SYS / "templates" / t.name)
    for n, line in enumerate(t.read_text(encoding="utf-8").splitlines(), 1):
        if re.search(r"\b[DQC]-\d{3}\b", line) or re.search(r"\b(Camden's call|answering `|supersedes|the audit|the sweep|we chose|was chosen because)\b", line, re.I):
            strip.append((t.name, n, line.strip()[:110]))
for p in sorted((P / "data").glob("*.csv")):
    if p.stem in PROCESS_TABLES:
        continue
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if re.search(r"\b[DQC]-\d{3}\b", line):
            strip.append((f"data/{p.name}", n, line[:110]))

# 2 service skeleton
service = f"""<!-- out: SERVICE.md -->
# {system.upper()} — SERVICE

*Rev {today} · owns: how to work on this system as fitted: tests, adjustments, recovery, what to check at what interval. Written at completion from the install plan's test and shakedown sections; the agent fills the sections below from `../../../99-ARCHIVE/{today}_{P.name}/` and the steps that measured the values.*

## Tests
## Adjustments and configuration
## Recovery
## Intervals (rows in ../../data/intervals.csv)
"""
plan.append(("write", service, SYS / "templates" / "SERVICE.md"))
plan.append(("write", f"<!-- out: README.md -->\n# {system.upper()} — AS BUILT\n\n*Rev {today} · owns: the {system} system as it is fitted, from the {P.name} project as completed. Facts are the tables in `data/`; the service pages are [`SERVICE.md`](SERVICE.md); the process record is `../../../99-ARCHIVE/{today}_{P.name}/`.*\n\n## Tables\n\n" + "".join(f"### {t}\n\n{{{{table:{t}}}}}\n\n" for t in sorted(p.stem for p in (P / "data").glob("*.csv") if p.stem not in PROCESS_TABLES and p.stem != "project")), SYS / "templates" / "README.md"))
# the system's project.csv says PERMANENT
_pj = (P / "data" / "project.csv").read_text(encoding="utf-8").replace(",BUILDING,", ",PERMANENT,")
plan.append(("write", _pj, SYS / "data" / "project.csv"))
plan.append(("write", '{"tabs": [{"title": "As built", "file": "README.md"}, {"title": "Service", "file": "SERVICE.md"}]}\n', SYS / "view.json"))

# 3 process → archive
for p in sorted((P / "data").glob("*.csv")):
    if p.stem in PROCESS_TABLES:
        cp(p, ARCH / "data" / p.name)
for sub in ("questions", "decisions"):
    for p in sorted((P / "data" / sub).glob("*.md")):
        cp(p, ARCH / "data" / sub / p.name)
for t in ("QUESTIONS.md", "DECISIONS.md", "LOG.md", "README.md"):
    if (P / t).exists():
        cp(P / t, ARCH / t)
for t in sorted((P / "templates").glob("*.md")):
    cp(t, ARCH / "templates" / t.name)
for sub in ("reviews", "02-SHOPPING"):
    for p in sorted((P / sub).rglob("*")) if (P / sub).is_dir() else []:
        if p.is_file():
            cp(p, ARCH / sub / p.relative_to(P / sub))
plan.append(("write", f"# {P.name} — completed {today}\n\n*owns: the process record of the {P.name} project: every question, decision, work item, log line, review and shopping list, as they stood at completion. The as-built facts and service pages are the manual's: `00-CAR/systems/{system}/`.*\n", ARCH / "README.md"))

# 4 00-CAR rows to confirm
car = rx7.DB(ROOT / "00-CAR")
todo = [f"as_fitted: add or update the row for {system!r} (state, since {today[:7]}, chapter {system})"]
for pl in car.rows("planned"):
    if P.name in (pl.get("project") or ""):
        todo.append(f"planned:{pl['id']} → a new M- row in mods.csv, and delete the P- row")
todo.append("parts_history: every part this project fitted → status installed, with its date")
todo.append("specs: every number learned at commissioning → a row, cited to the step that measured it")

print(f"complete {P.name} → 00-CAR/systems/{system}  ({'DRY RUN' if DRY else 'WRITING'})")
for a, s, d in plan:
    if a == "copy":
        print(f"  copy  {s.relative_to(ROOT)}  →  {d.relative_to(ROOT)}")
    else:
        print(f"  write {d.relative_to(ROOT)}")
print(f"\nSTRIP — {len(strip)} line(s) the manual must not keep as written (agent rewrites each, or moves it to the archive README):")
for f, n, l in strip[:60]:
    print(f"  {f}:{n}  {l}")
if len(strip) > 60:
    print(f"  … {len(strip) - 60} more")
print("\n00-CAR rows for the agent to confirm:")
for t in todo:
    print("  -", t)
if DRY:
    print("\ndry run — nothing written. Re-run without --dry to fold; the project folder is removed last.")
    sys.exit(0)
for a, s, d in plan:
    d.parent.mkdir(parents=True, exist_ok=True)
    if a == "copy":
        shutil.copy2(s, d)
    else:
        d.write_text(s, encoding="utf-8", newline="\n")
shutil.rmtree(P)
print(f"\nfolded. Now: rewrite the STRIP lines in 00-CAR/systems/{system}/, confirm the 00-CAR rows, then `python tools/rx7.py -a build`.")

# -*- coding: utf-8 -*-
"""triggers.py — evaluate tools/triggers.csv against every project's lint metrics and checks.

    python tools/triggers.py            print what each project needs, and the command to run
    python tools/triggers.py --json     machine-readable
    python tools/triggers.py --auto     ALSO run, headless, every fired trigger whose row says auto=yes
                                        (claude -p "/rx7-<workflow> <project>") — costs credits; off by default

Called by `rx7.py status`, the pre-commit hook and the Claude Code Stop hook. A trigger never edits
anything itself; it names the workflow that should run. Deterministic parts (check, build, lint)
are free; agent workflows only run when a person (or auto=yes) says so.
"""
import csv, json, subprocess, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import rx7  # noqa: E402

OPS = {">": lambda a, b: a > b, ">=": lambda a, b: a >= b, "<": lambda a, b: a < b, "==": lambda a, b: a == b}
rules = list(csv.DictReader(open(ROOT / "tools" / "triggers.csv", encoding="utf-8")))
fired = []
for d in rx7.all_projects():
    db = rx7.DB(d)
    views, checks, _, gates = rx7.load_views(d)
    problems = rx7.run_checks(db, checks, gates)
    warn, metrics = rx7.lint(db)
    metrics["check_problems"] = len(problems)
    reviews = sorted((d / "reviews").glob("CRITIQUE-*.md")) if (d / "reviews").is_dir() else []
    if reviews and "questions" in db.tables:
        last = reviews[-1].stem.split("-", 1)[1][:10]
        try:
            metrics["days_since_critique"] = (date.today() - date.fromisoformat(last)).days
        except ValueError:
            pass
    for r in rules:
        m = metrics.get(r["metric"])
        if m is None:
            continue
        if OPS[r["op"]](float(m), float(r["threshold"])):
            fired.append({"project": d.relative_to(ROOT).as_posix(), "name": d.name, "trigger": r["id"], "metric": r["metric"], "value": m,
                          "workflow": r["workflow"], "auto": r["auto"] == "yes", "why": r["why"]})
if "--json" in sys.argv:
    print(json.dumps(fired, ensure_ascii=False, indent=1)); sys.exit(0)
if not fired:
    print("triggers: nothing fired"); sys.exit(0)
print("triggers:")
seen = set()
for f in fired:
    key = (f["name"], f["workflow"])
    tag = "" if key not in seen else "        "
    seen.add(key)
    print(f"  {f['trigger']}  {f['project']:<34} {f['metric']}={f['value']:<4} → /{f['workflow']} {f['name']}   ({f['why']})")
if "--auto" in sys.argv:
    for key in {(f["name"], f["workflow"]) for f in fired if f["auto"]}:
        cmd = ["claude", "-p", f"/{key[1]} {key[0]}"]
        print("running", " ".join(cmd))
        subprocess.run(cmd, cwd=ROOT, check=False)

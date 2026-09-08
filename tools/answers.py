# -*- coding: utf-8 -*-
"""answers.py — every question packet Camden has answered, across every project.
   python tools/answers.py [--json]          (stdlib only; step 1 of /rx7-answers)
Reads data/questions/<id>.md of every open question and prints the ones whose **ANSWER:** block has text."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import rx7  # noqa: E402

found = []
for d in rx7.all_projects():
    db = rx7.DB(d)
    if "questions" not in db.tables:
        continue
    for q in db.rows("questions", "status = 'open'"):
        ans = rx7.answered(db.body("questions", q["id"]))
        if ans:
            found.append({"project": d.name, "id": q["id"], "title": q["title"], "section": q["section"], "answer": ans})
if "--json" in sys.argv:
    print(json.dumps(found, ensure_ascii=False, indent=1))
else:
    for f in found:
        print(f"## {f['project']} | {f['id']} · {f['title']}\n    {f['answer']}")
    print(f"{len(found)} answered packet(s)")

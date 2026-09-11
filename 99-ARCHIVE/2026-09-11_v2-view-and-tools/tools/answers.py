# -*- coding: utf-8 -*-
"""answers.py - every question packet Camden has answered, across every project.
   python tools/answers.py [--json]          (stdlib only; step 1 of /rx7-answers)

Ingests ANSWERS.md first (tools/inbox.py), so it does not matter whether he typed in
the inbox or straight into a packet - both arrive here. Then prints every open
question whose **ANSWER:** block has text.

If this prints 0 while Camden says he answered, do not proceed: find where he typed.
Check ANSWERS.md, any *.typed-in.bak next to a generated document, and 99-ARCHIVE/answers/."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import rx7    # noqa: E402
import inbox  # noqa: E402

quiet = "--json" in sys.argv
moved = inbox.take(quiet=quiet)

found = []
for d in rx7.all_projects():
    db = rx7.DB(d)
    if "questions" not in db.tables:
        continue
    for q in db.rows("questions", "status = 'open'"):
        ans = rx7.answered(db.body("questions", q["id"]))
        if ans:
            found.append({"project": d.name, "id": q["id"], "title": q["title"],
                          "section": q["section"], "answer": ans,
                          "via": "ANSWERS.md" if q["id"] in moved else "packet"})
if quiet:
    print(json.dumps(found, ensure_ascii=False, indent=1))
else:
    for f in found:
        print(f"## {f['project']} | {f['id']} · {f['title']}  [{f['via']}]\n    {f['answer']}")
    print(f"{len(found)} answered packet(s)")
    if not found:
        strays = sorted(p.name for p in ROOT.rglob("*.typed-in.bak"))
        if strays:
            print("  !! but text was typed into a generated file: " + ", ".join(strays))
        elif inbox.INBOX.exists():
            print("  ANSWERS.md exists but every answer space is empty.")
        else:
            print("  No ANSWERS.md. Run: python tools/rx7.py ask")

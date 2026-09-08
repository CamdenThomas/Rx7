# -*- coding: utf-8 -*-
"""answers.py — list every question packet whose ANSWER block has content, across the projects.
   python tools/answers.py            (run from the repo root; stdlib only)
Step 1 of the answer cycle (ASSISTANT.md §10)."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
FILES = sorted(ROOT.glob("02-PROJECTS/*/QUESTIONS.md"))
PACKET = re.compile(r"\*\*((?:[A-Z]-\d{3}|[A-Z]\d)[^\n]*?)\*\*.*?\*\*ANSWER:\*\*\n((?:>[^\n]*\n?)+)", re.S)
n = 0
for f in FILES:
    s = f.read_text(encoding="utf-8")
    for m in PACKET.finditer(s):
        ans = " ".join(l.lstrip("> ").strip() for l in m.group(2).splitlines() if l.strip("> ").strip())
        if ans:
            n += 1
            print(f"## {f.parent.name} | {m.group(1)[:100]}")
            print("   ", ans)
print(f"{n} answered packet(s)")

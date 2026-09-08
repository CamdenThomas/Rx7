# -*- coding: utf-8 -*-
"""hook_stop.py — Claude Code Stop hook: before the agent ends its turn, check every project and print
the triggers. Never blocks (exit 0); the summary lands in the transcript so a dirty build is visible."""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
out = []
for cmd in (["-a", "check"],):
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "rx7.py"), *cmd], capture_output=True, text=True, encoding="utf-8", errors="replace")
    out.append(r.stdout)
r = subprocess.run([sys.executable, str(ROOT / "tools" / "triggers.py")], capture_output=True, text=True, encoding="utf-8", errors="replace")
out.append(r.stdout)
text = "".join(out)
if "problem" in text or "triggers:" in text:
    print("rx7 session close —\n" + text)
sys.exit(0)

# -*- coding: utf-8 -*-
"""hook_check.py - Claude Code PostToolUse hook. After an edit inside any area's data/,
run `check` and, if the record now contradicts itself, put the refusal on stderr and
exit 2 so the agent sees it immediately.

It branches on the RETURN CODE and nothing else. It never tests the output for a word:
that is exactly how v2 turned clean reports into refusals. Exit code 2 from `check`
(something waits on a person) is not a refusal here and never will be.
Stdlib only.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

fp = (payload.get("tool_input") or {}).get("file_path") or ""
if not fp:
    sys.exit(0)

try:
    rel = Path(fp).resolve().relative_to(ROOT)
except ValueError:
    sys.exit(0)

parts = rel.parts
if "data" not in parts:
    sys.exit(0)
if "99-ARCHIVE" in parts:
    sys.exit(0)

r = subprocess.run(
    [sys.executable, str(ROOT / "tools" / "rx7.py"), "check"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)

# 1 = the record contradicts itself. Nothing else is a refusal.
if r.returncode == 1:
    sys.stderr.write(f"rx7 check refused after editing {rel.as_posix()}:\n{r.stdout}{r.stderr}")
    sys.exit(2)
sys.exit(0)

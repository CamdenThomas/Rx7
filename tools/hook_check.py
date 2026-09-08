# -*- coding: utf-8 -*-
"""hook_check.py — Claude Code hook. After an Edit/Write inside a project's data/ or templates/, run that
project's `check`; print problems to stderr and exit 2 so the agent sees the refusal immediately.
Reads the hook's JSON on stdin (tool_input.file_path). Stdlib only."""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)
fp = (payload.get("tool_input") or {}).get("file_path") or ""
if not fp:
    sys.exit(0)
p = Path(fp)
try:
    rel = p.resolve().relative_to(ROOT)
except ValueError:
    sys.exit(0)
parts = rel.parts
if "data" not in parts and "templates" not in parts and rel.name != "views.py":
    sys.exit(0)
i = parts.index("data") if "data" in parts else parts.index("templates") if "templates" in parts else len(parts) - 1
proj = ROOT.joinpath(*parts[:i])
if not (proj / "data").is_dir():
    sys.exit(0)
r = subprocess.run([sys.executable, str(ROOT / "tools" / "rx7.py"), "-p", str(proj), "check"], capture_output=True, text=True, encoding="utf-8", errors="replace")
if r.returncode != 0 or "problem" in r.stdout:
    sys.stderr.write(f"rx7 check ({proj.name}) after editing {rel.as_posix()}:\n{r.stdout}{r.stderr}")
    sys.exit(2)
sys.exit(0)

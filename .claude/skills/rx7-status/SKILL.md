---
name: rx7-status
description: Where every Rx7 project stands — phase, next ids, what waits on Camden, answered packets, checks, and which workflow the triggers say to run. Run first in every session; /rx7-status.
---

# /rx7-status

The session opener. Nothing is read before it; nothing is decided by it.

1. Run `python tools/rx7.py status` from the repo root (set `PYTHONIOENCODING=utf-8` on Windows). It prints, per project: phase · open questions (and which are answered but unapplied) · next `D` / `Q` · open work by owner · the last three log lines · check and lint summary · then the fired triggers with the workflow each names.
2. Report it in **at most twelve lines**: one line per project (phase, what waits on whom), then the triggers' recommendation as one line: "next: `/rx7-answers electrical-build`" or "nothing waits on the agent".
3. Stop. Do not read any document, do not start any workflow — Camden names the next one. If he already named it in the same message, run it now.

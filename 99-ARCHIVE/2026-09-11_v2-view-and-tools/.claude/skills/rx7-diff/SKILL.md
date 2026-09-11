---
name: rx7-diff
description: Close an Rx7 session — build everything, confirm the work list reads true, print the ten-line diff for the commit. /rx7-diff.
---

# /rx7-diff

1. `python tools/rx7.py -a build` — fix anything it reports; `python tools/triggers.py` — note what it names.
2. Confirm the active project's `QUESTIONS.md` §0 reads true (every done item is `done`, every open item's gate is right).
3. Print, ten lines or fewer, then nothing else — the commit is Camden's:

```
CHANGED   rows set/added/deleted (table:key), templates touched
LOGGED    D-### decisions added
OPENED    new Q-### / C-###
CLOSED    Q-### → D-###
BUILT     files written by build
NEXT      the workflow the triggers name, and its target
COMMIT    git commit -am "<one line>"
```

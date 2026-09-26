# Playbook: plan (any project, any phase)

**Planning is open in every project at every phase** (D-398). The phase says how far the
build has got, never whether design may be touched: a project in PROPOSED, SOURCING or
BUILDING takes design work, blocks and parts rounds exactly as one in PLANNING does, and
one project's phase never holds another's planning. Past the freeze, new design work never
moves the phase back. The new row goes on the design track, and every build row it changes
gets the new row's id in its gate, so only that work waits and the rest of the build carries
on. Undoing work already done (re-cutting, re-ordering, re-wiring) is §3's irreversible,
so it is a block.

1. `status`. If any answer is in the inbox, run the apply playbook first — an answer can
   change how an earlier work item should be done.
2. Take the first agent row in **READY** — `status` prints it. Never the next row in file
   order, and never a BLOCKED one. **READY empty is a report, not permission to take
   something else**: say what is holding the queue and stop.
3. Do it through the record only: facts become rows (R1); a derivation becomes a query,
   never a typed number; a fact with no column gets a column (§3). Anything §3 calls big
   becomes a block plus a Camden-owned work row gated on it, and the item stays open with
   `note=waits on block 01.…`.
4. `check`. A refusal is fixed in the data, or becomes a block if the fix is his.
5. `set work <id> state=done`; `log`.
6. Repeat until no agent item has a met gate.
7. **Phase gate.** Every agent design item done, no open block that stops design, no open
   Major review finding → raise the design-freeze block. The freeze is his ruling; it
   moves the phase to SOURCING. It starts the build; it does not end planning.

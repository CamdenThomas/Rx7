# Playbook: merge - one merge item of 00-library (D-574, phase 3)

You move a batch of staged facts (00-library `facts`, state new) into their home tables, one
fact once. This needs judgement: run it on a stronger model than the parse workers.

**Not for you:** CLAUDE.md §0, §6, §8 - no pull, commit, push or report; never run git; never
edit a CSV by hand. Everything else in CLAUDE.md binds you - §3 (big or small), §4 (blocks),
R1, R2, R5, R11.

## 1. Claim

```
python3 tools/rx7.py claim 02-PROJECTS/00-library --kind merge --agent <name>
```

It prints `section` (the home area, system and kind), `brief` and `rows` (the facts, a range).
Read them:

```
python3 tools/rx7.py sql 02-PROJECTS/00-library "select * from facts where id between 'F-000101' and 'F-000134'"
```

## 2. Each fact, in order

1. **Find its home.** The table `kind` names in the area the section names (spec -> specs,
   step/procedure -> procedures + procedure_steps, terminal -> terminals, circuit ->
   circuit_paths, diagnosis -> diagnosis, interval -> intervals, part -> parts or the
   catalogue, dimension -> specs or the project's dims table, issue -> issues, figure -> the
   row the drawing explains, note -> the nearest row's note). Search it narrowly:
   `rx7.py sql 00-CAR "select id,item,value,unit,source,page,applies from specs where system='engine' and item like '%tension bolt%'"`.
2. **Decide**, and record it on the fact with one `set`:
   - **the same fact is there** (same thing, same value, same applies) -> add this source and
     page to that row's `source`/`page` if they are not there; fact `state=duplicate target=specs:SP-0123`.
   - **not there** -> add the home row (`id=next`; `source` the doc's S- id, `page` as the
     document prints it; `applies`: this-car -> blank, other-year -> other-car, other-model ->
     other-car only if a project uses that part, else reject); fact `state=merged target=...`.
   - **there with another value**: if one is this-car and the other another year, both stand
     (the other year's is held back, `applies=other-car`). If two this-car sources disagree,
     or a page contradicts a measured or checked row: change nothing - fact `state=conflict`
     with the two rows in `note`. The orchestrator raises conflicts as blocks.
   - **nothing worth keeping** (an advert, another model's part nobody uses) -> `state=rejected` and why in `note`.
3. **Link the page**: `python3 02-PROJECTS/00-library/tools/link.py DOC-048.027 specs:SP-0123` -
   adds the row to the page's `rows`.

One fact once (R2): when two facts in your batch are the same, merge the first and mark the
second `duplicate` of the same target. Never type a D- or block id; never cite a decision in
00-CAR.

## 3. Finish

```
python3 tools/rx7.py finish 02-PROJECTS/00-library Q-01300 "result=34 facts: 12 merged, 19 duplicate, 2 rejected, 1 conflict (F-000120)" "rows=specs:SP-1830..SP-1841"
```

Then stop, with one line.

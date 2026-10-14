# Playbook: parse - one queue item of 05-library (D-574)

You are one of many small workers reading the car's documents. You do **one** queue item - a
few pages of one PDF - and stop. The whole plan is `rx7.py doc library`; you do not need it.

**Not for you:** CLAUDE.md §0 (no pull, no status), §6 (no commit, no push), §8 (no report).
Never run git. Never edit a CSV by hand. Never read a whole table. Never message Camden. The
only commands you run are the six below.

## 1. Claim

```
python3 tools/rx7.py claim 02-PROJECTS/05-library --agent <a short name>
```

rc 2 means the queue is empty or waiting: stop. Otherwise it prints `id` (Q-.....), `kind`,
`doc` (DOC-...), `pages` (PDF page numbers, e.g. `12-14`), `brief`, `doc.path`, `doc.text`.

## 2. Read

```
python3 02-PROJECTS/05-library/tools/page.py text DOC-062 12-14
```

Use the text when it reads cleanly. When a page has no text, or its table or drawing comes out
scrambled, look at it:

```
python3 02-PROJECTS/05-library/tools/page.py image DOC-062 13                     # whole page
python3 02-PROJECTS/05-library/tools/page.py image DOC-062 13 --dpi 250 --crop 0.1,0.5,0.4,0.3
```

and Read the PNG it prints. One image at a time; crop to zoom on a figure, table or small print.

## 3. Write the facts

Everything the pages state that a mechanic could use: every figure, setting, torque, clearance,
limit, capacity, part number, step, wire, terminal, symptom and cause, and what each drawing
fixes. Take it all - even what the record may already hold. The merge drops the duplicates, so
never search 00-CAR yourself.

Write a file `/tmp/rx7-facts-<Q-id>.txt`: the header line exactly as below, then one line per
fact, fields split by `|` (never put a `|` inside a field; write `/`).

```
id|page|kind|system|subject|item|value|unit|context|applies|quote|note
next|DOC-048.027|spec|engine|Tension bolt|Tightening torque|31-34|N·m|final pass, in sequence|other-year|3.2-3.5 m-kg (23-25 ft-lb)|
next|DOC-048.027|step|engine|Remove the rear housing|Loosen the tension bolts in two or three passes|||step 4, order on the figure|other-year||
```

- `id` is always `next`. `page` is the page the fact is on: `DOC-xxx.nnn`, three digits.
- `kind`: spec, step, procedure (a procedure's title, when, tools), terminal, circuit, diagnosis
  (item = symptom, value = cause, context = the check and the remedy), interval, part (a part
  name with its number), catalogue (a parts-catalogue callout), dimension, figure (what a
  drawing fixes, in words), issue (a known fault or bulletin), note (anything else useful).
- `system`, when you can tell: engine fuel ignition cooling electrical lighting transmission
  driveline brakes suspension steering wheels climate body. Otherwise empty.
- `subject` is the thing (a part, a system, the procedure's title); `item` what is stated about it.
- `value` as printed - both units if both are printed; `unit` the first value's unit.
- `context`: the condition - model, year, gearbox, engine, step number, figure id, test state.
- `applies` - read the page's own heading and context: **this-car** if it is the 1982 RX-7 12A
  (or the 1981-83 car generally); **other-year** for another 1979-85 RX-7 (a 1980 or 1985 figure);
  **other-model** for anything else (13B, 626, GLC, FC, a Nissan); **unknown** if the page does
  not say.
- `quote`: the printed line, short, only when the wording matters (a caution, a misprint).
- A digit you cannot read: put your best reading and `unclear` in `note`. Never invent.

Then add them, in one call:

```
python3 tools/rx7.py add 02-PROJECTS/05-library facts --rows /tmp/rx7-facts-Q-00042.txt state=new queue=Q-00042
```

It prints the ids it gave (`F-000101 to F-000134`). If it refuses a row it writes nothing and
says which line - fix that line and run it again.

## 4. Mark the pages

One `set` per page, joined with `&&` in one call:

```
python3 tools/rx7.py set 00-CAR pages DOC-048.027 kind=mixed "topic=Rear housing removal" scope=other-year status=parsed && \
python3 tools/rx7.py set 00-CAR pages DOC-048.028 kind=figure "topic=Tension bolt order" scope=other-year status=parsed
```

- `kind`: text, table, figure, photo, mixed, cover, blank, index.
- `status`: **parsed** (its facts are in, or it had none worth taking), **indexed** (another
  model's page: topic only, no facts), **empty** (blank, cover, advert), **duplicate** (the same
  page as another).
- `scope`: this-car, other-year, other-model, none.

## 5. Finish

```
python3 tools/rx7.py finish 02-PROJECTS/05-library Q-00042 "result=34 facts F-000101..F-000134; p.13 figure decoded" "rows=F-000101..F-000134"
```

Could not do it (illegible, a drawing too dense, the wrong pages)? Do not guess:

```
python3 tools/rx7.py finish 02-PROJECTS/05-library Q-00042 state=failed "result=why, in one line"
```

A stronger agent takes failed items. Leave the facts you did add; say so in `result`.

## 6. Stop

Reply with one line: the item, done or failed, how many facts. Then stop - do not claim another
unless your instructions said to loop.

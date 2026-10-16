# Playbook: parse - one queue item of 00-library (D-574)

`run_session.py` hands this text, the item's brief, the pages' text and the names of the page
images to a small worker (`claude -p`, Haiku or Sonnet), started in an empty folder: the worker
never touches the record. Everything below the line is the worker's whole instruction. Run by
hand, the same output pasted into `run_session.py --ingest Q-id FILE` does the writing.

---

You read a few pages of a car manual or datasheet and write down every fact they state, as
rows. You do not edit files and run no commands. The only tool you may use is **Read**, and only
on the image files named below - read each one; a page's image shows what its text scrambles
(tables, drawings, small print).

The car is a 1982 Mazda RX-7 (FB body), 12A rotary, 3-speed automatic, GS trim, US.

**Take everything a mechanic could use:** every figure, setting, torque, clearance, limit,
capacity, part number, step of a procedure, wire, terminal, symptom and cause, and what each
drawing fixes (positions, orders, directions, dimensions, connector faces). Take it even if it
seems obvious. Do not judge whether the record already has it. Never invent: a digit you cannot
read gets your best reading and `unclear` in note.

**Answer with exactly two fenced blocks and nothing else.**

```facts
page|kind|system|subject|item|value|unit|context|applies|quote|note
DOC-048.027|spec|engine|Tension bolt|Tightening torque|31-34|N·m|final pass, in sequence|other-year|3.2-3.5 m-kg (23-25 ft-lb)|
DOC-048.027|step|engine|Remove the rear housing|Loosen the tension bolts in two or three passes|||step 4; order on fig. 1-27|other-year||
```

One fact per line, **always exactly 11 fields - 10 `|` per line, empty fields included** (an empty
unit is `||`). Never a `|` inside a field: write `/`. The header line is optional.

- **page**: the page id the fact is on, exactly as given (`DOC-xxx.nnn`).
- **kind**: spec, step, procedure (a procedure's title, when to do it, its tools), terminal,
  circuit, diagnosis (item = the symptom, value = the cause, context = the check and the remedy),
  interval, part (a part's name and number), catalogue (a parts-catalogue callout: subject = the
  figure, item = the callout, value = the part number), dimension, figure (what a drawing shows,
  in words), issue (a known fault or a bulletin), note (anything else useful).
- **system**: engine, fuel, ignition, cooling, electrical, lighting, transmission, driveline, brakes,
  suspension, steering, wheels, climate or body - or empty.
- **subject**: the thing (a part, a system, a procedure's title). **item**: what is stated about it.
- **value** as printed (both units if both are printed); **unit**: the first value's unit.
- **context**: what the value depends on - model, year, gearbox, engine, step number, figure id, test condition.
- **applies**: `this-car` if the page is about the 1982 RX-7 12A (or 1981-83 generally) - `other-year` for
  another 1979-85 RX-7 - `other-model` for anything else (13B, 626, GLC, a later RX-7, another make) - `unknown`.
- **quote**: the printed words, short, only when the wording matters (a caution, a misprint).

```pages
page|kind|topic|scope|status
DOC-048.027|mixed|Rear housing removal|other-year|parsed
```

One line per page you were given: **kind** text, table, figure, photo, mixed, cover, blank or index;
**topic** a few words; **scope** this-car, other-year, other-model or none; **status** `parsed` (its facts
are above, or it had none worth taking), `indexed` (another model's page - topic only, no facts),
`empty` (blank, cover, advert).

If you cannot read the pages (illegible, a drawing too dense for you, the wrong pages), answer
only: `FAILED: <why, one line>`.

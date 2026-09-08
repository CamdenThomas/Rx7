---
name: rx7-log
description: Record a service visit, a fluid change, a part fitted, a mileage reading or a fault found on the RX-7 in the owner's manual — no project needed. /rx7-log "<what you did>" [--mileage N] [--date YYYY-MM-DD].
---

# /rx7-log `"<what you did>" [--mileage N] [--date …]`

The manual is a service log between projects. One call, one visit.

1. Parse the sentence into: the work (one line) · the schedule items it satisfies (match `00-CAR/data/intervals.csv` ids: oil, plugs, coolant, brake_fluid, atf, diff, air_filter, fuel_filter, belts, wheel_nuts, battery — add a row if a new kind of item appears) · parts used (match or add `parts_history` rows, status `installed`, with the date) · the mileage · anything found wrong (a `K-` row in `issues`).
2. `python tools/rx7.py -p 00-CAR add service id=SV<next> date=<YYYY-MM> mileage=<n> work="…" items="oil belts" parts="PH0xx" notes="…"`; `set vehicle mileage value=<n>` if it moved; the `K-` row if any.
3. `python tools/rx7.py -p 00-CAR build` — the schedule recomputes last-done and next-due from the log.
4. Report in three lines: the row, what is now next due, anything opened.

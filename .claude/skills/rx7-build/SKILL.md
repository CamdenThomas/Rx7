---
name: rx7-build
description: The shop assistant for an Rx7 project in BUILDING — Camden says what he did and measured, the agent ticks the steps, files every number where it lives, opens issues, rebuilds and hands back the next step. /rx7-build <project> "<what happened>".
---

# /rx7-build `<project> "<what happened>"`

**Gate:** phase BUILDING; `data/steps.csv` exists (`id,phase,step,gate,measure,value,state,done_on,note`) — if the install plan is still prose, the first run converts its numbered boxes to rows (one row per box, the measurement boxes with `measure` filled) and re-templates `INSTALL.md` on `{{table:steps}}`; that conversion is logged as a decision.

1. **Parse what he said** into: steps done (ids or the words that match a step) · measurements (a number, a unit, the step or box it belongs to) · things found (a fault, a part that does not fit, a surprise) · things bought.
2. **File each where it lives**, `get` first: steps → `set steps <id> state=done done_on=<date> value=<n>`; a measurement → its home row (`loads.measured_a`, `pins.enable_a` only with its basis, `00-CAR/specs` if it is a fact about the car, `00-CAR/service` if it was a service act); a fault → `00-CAR` `issues` `K-` row (`new`-style id from the registry: `ids next K` is not a registry family — take max+1 from the table); a part fitted → `00-CAR/parts_history` status `installed` and its date; a measurement that contradicts the design → a packet (section 2), the step stays open with `note=waits on Q-…`.
3. **Photos** he names → `01-REFERENCE/photos/<zone>/YYYY-MM-DD_<zone>_<subject>.jpg` and a `sources` row the same call.
4. `python tools/rx7.py -p <project> build` (and `-p 00-CAR` if it changed). A refusal means a measurement broke a check — that is a finding: report it, do not soften the check.
5. `log build "<steps done, numbers taken>" <ids>`.
6. **Hand back exactly one thing:** the next open step whose gate is met — its text, its gate, the tools it names, and the measurement it wants — not the plan. If the next step is Camden-only and blocked (parts, weather, a packet), say what clears it.

When the last step is done and the shakedown values are in their rows: say so, and that `/rx7-complete` is next.

<!-- out: QUESTIONS.md -->
# QUESTIONS — everything still open, in the order it has to be answered

*Rev 2026-09-08 · owns: what is still undecided, unconfirmed or unmeasured in the electrical build, plus the finishing task list. Rulings are [`DECISIONS.md`](DECISIONS.md)'s; facts are `data/`'s.*

One kind of item only: a question is anything not yet settled — a call only the owner can make, a fact to confirm, or a measurement to take. Answer one by writing under it or saying it in a session; it then becomes a `D-` entry in `DECISIONS.md` and leaves this file. IDs are permanent; the ones that came from the old verify/assumption lists keep their old numbers, new ones run from Q-100.

**The file is split by the one deadline that matters: paying for the carts.**

| | §1 · BEFORE SHOPPING | §2 · AFTER SHOPPING |
|---|---|---|
| **What it is** | Design questions — what gets bought, and whether the drawing is right | Install validation and fine tuning — is what was built correct, and is it set up well |
| **Cost of a wrong answer** | A re-order, or a part that does not fit | An afternoon, on a car that still drives home |
| **Answer them** | Now, at the desk, before `T-053` | When the car is apart, when the parts land, or at commissioning |

Nothing in §2 blocks a purchase. Nothing in §1 should wait.

§0 is the finishing task list — the order of work from here to a car driving on the PMU; its block G is the agent's improvement list from the production-car comparison. §3 records what closed. §4 records what left this project and where it went.

---

{{banners:6}}

---

## 0 · The finishing task list

Rendered from `data/work.csv` — every task, who owns it (Camden unless marked *agent*), its state and its gate. `/rx7-plan` works the agent items; the rest are yours.

{{work}}

---

## 1 · BEFORE SHOPPING — design questions

One desk check and nine items. `T-017` has to be done before the design freezes. `Q-113`, `Q-114` and `Q-134`–`Q-139` come from the 2026-09-05 and 2026-09-08 sweeps; each carries a recommendation and wants one word — only `Q-137` (a switch part number, P049) and `Q-138` (a fuse rating, P052) touch a cart. `Q-128` wants a source and the nRF Connect look. `Q-133` is answered and waits for its answer cycle.

{{packets:1}}

## 2 · AFTER SHOPPING — install validation and fine tuning

Nothing here changes what is bought or how the harness is drawn. Each one is answered at the moment the plan reaches it, on a car that drives home at the end of the day.

{{packets:2}}

## 2a · The measurement day — interior apart, before anything is cut

These gate **cutting**, never buying (D-202). All four are one session with a tape measure and a meter.

{{packets:2a}}

## 2b · When the parts arrive

No open questions — the arrival checks are §0's D1–D4 boxes.

{{packets:2b}}

## 2c · At configuration — PMU powered in the car, every output disabled (install §5.3–5.6)


{{packets:2c}}

## 2d · At shakedown — numbers for judging a running car

Neither of these sizes anything. Both are wanted so the first week's telemetry can be read against something.

{{packets:2d}}

---

## 3 · Closed

Answered items leave the sections above and land here with their closer (`data/questions.csv`, status `closed`). IDs are permanent and are cited with their closer.

{{closed}}

---

## 4 · Moved out of this project

{{moved}}

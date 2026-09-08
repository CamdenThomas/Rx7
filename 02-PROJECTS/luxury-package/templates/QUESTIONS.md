<!-- out: QUESTIONS.md -->
# QUESTIONS — luxury package

*Rev 2026-09-08 · owns: what is still open in this project, and the finishing checklist. Rulings are [`DECISIONS.md`](DECISIONS.md)'s; facts are `data/`'s. IDs inherited from the electrical project keep their numbers; new ones run from Q-300.*

**None of this blocks the electrical build's carts.** The harness side of every feature here is run and capped; the boundary table in [`01-DESIGN/DESIGN.md`](01-DESIGN/DESIGN.md) §2 is read live from that project's data. The file is split by this project's own shopping event — the carrier boards and the glass.

| | §1 · BEFORE the boards and the glass | §2 · AFTER |
|---|---|---|
| **What it is** | Calls the owner makes, facts to confirm, measurements to take before a PCB is laid out or a panel is bought | Bring-up, validation and tuning |
| **Cost of a wrong answer** | A re-spun board, or glass that cannot be driven | A firmware revision |

The ICU's own questions — its layout, its senders, the wideband's frame — are the electrical build's now (D-313); they sit in its `QUESTIONS.md` §1 under their old numbers.

Three items ride along with the electrical build's measurement day — marked **[M-DAY]**. Miss that day and they wait for the next teardown.

---

{{banners:6}}

---

## 0 · The finishing task list

Rendered from `data/work.csv` — every task, who owns it (Camden unless marked *agent*), its state and its gate. `/rx7-plan` works the agent items; the rest are yours.

{{work}}

---

## 1 · BEFORE the boards and the glass


{{packets:1}}

## 2 · AFTER — bring-up, validation and tuning


{{packets:2}}

---

## 3 · Closed

Answered items leave the sections above and land here with their closer (`data/questions.csv`, status `closed`). IDs are permanent and are cited with their closer.

{{closed}}

---

## 4 · Moved out of this project

{{moved}}

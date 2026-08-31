# Circuit — Front & Rear Wiper and Washer

*Rev 2026-08-30 · owns: the factory decode of this circuit — devices, wires, logic. The rebuild table at the foot points into the new design and is not its owner; cavities are `02-HARNESS/data/connectors.csv`'s.*

**Source:** Section D, page 18.

---

## 1 · Devices

| Ref | Device | Pins |
|---|---|---|
| D-01 | Front washer motor | LY, LB |
| D-02 | Front wiper motor | L, LB, B / LW, LR |
| D-03 | Combination switch — wiper + washer + one-touch | B, LO, LY / LR, LG, LW |
| D-04 | Rear washer motor | LB, L |
| D-05 | Rear wiper motor | L, BG |
| D-06 | Rear wiper & washer switch | B, BG, LW |
| D-07 | Connector to rear wiper | B, LB, BG, L |
| — | Control Processing Unit (intermittent timer) | X-16 |

## 2 · Front wiper

| Item | Value |
|---|---|
| Feed | Ignition **IG** → X-04 **10 A** → **LB** bus |
| Speeds | **Separate LOW and HIGH brushes** — motor has LO and HI terminals |
| Motor wires | L, LB (park/common), LW (low), LR (high) |
| Park | Internal park switch in the motor, on LB |
| Intermittent | Control Processing Unit (X-16), the same module family as the flasher |
| Switch positions | OFF / INT / LO / HI, plus WASHER and a one-touch position |
| Ground | B → X-13 |

**Confirms A-001** (A-001 → confirmed here) — the motor genuinely needs two outputs. O8 (with braking)
for LOW, O9 for HIGH, per SPEC.

## 3 · Rear wiper & washer

| Item | Value |
|---|---|
| Feed | Separate **10 A** fuse off the L bus |
| Switch | D-06, in the cabin. BG and LW |
| Motor | D-05 rear wiper, D-04 rear washer |
| Ground | B → X-13, via X-11 / X-02 |

V-027 → D-097: the rear wiper is gone from the car and is not in the SPEC. It has no channel
allocated. Decide whether it stays.

## 4 · What this means for the rebuild

| Factory | PMU-24 plan |
|---|---|
| Control Processing Unit for intermittent | Deleted (D-014) — software timer on O8 (Checklist 2.12) |
| Motor internal park switch | Retained as a wire (**L2-S 3**) — **no PMU pin is free**; whether O8 braking needs it is `V-074`, the pin is `Q-063` → D-182 |
| LO / HI brushes | O8 (braking) → **L2-M 1**; O9 → **L2-M 2** |
| Combination switch carrying motor current | A2 five-step resistor ladder, switch-to-ground, **L3-S1 4** |
| Washer motor on the switch directly | PMU-driven (Q-016 → D-051) on **L2-M 4** — **no output is free**, `Q-063` → D-182. Pump not working, K-022 |
| Rear wiper + washer | Gone (V-027 → D-097) |
| Ground at X-13 | Front star node |

## 5 · Unknowns

| ID | Unknown | Resolve by |
|---|---|---|
| V-027 → D-097 | Rear wiper | Gone, not returning |
| V-028 | One-touch wipe in software? | Decide during Checklist 2.12 — tracked in `OPEN.md` |

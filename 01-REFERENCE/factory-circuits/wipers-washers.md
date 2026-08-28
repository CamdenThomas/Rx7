# Circuit — Front & Rear Wiper and Washer

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

**Confirms A-001** — the motor genuinely needs two outputs. O8 (with braking)
for LOW, O9 for HIGH, per SPEC.

## 3 · Rear wiper & washer

| Item | Value |
|---|---|
| Feed | Separate **10 A** fuse off the L bus |
| Switch | D-06, in the cabin. BG and LW |
| Motor | D-05 rear wiper, D-04 rear washer |
| Ground | B → X-13, via X-11 / X-02 |

`[V-027]` The rear wiper is not in the PMU SPEC at all. It has no channel
allocated. Decide whether it stays.

## 4 · What this means for the rebuild

| Factory | PMU-24 plan |
|---|---|
| Control Processing Unit for intermittent | Deleted (D-014) — software timer on O8 |
| Motor internal park switch | Retained; PMU reads park state for correct stop position |
| LO / HI brushes | O8 (braking) / O9 |
| Combination switch carrying motor current | A2 five-step resistor ladder, switch-to-ground |
| Washer motor on switch directly | `[Q-016]` — assumed PMU-driven on a C2 spare |
| Rear wiper + washer | **Unallocated** — see V-027 |
| Ground at X-13 | Cowl-area local star node |

## 5 · Unknowns

| ID | Unknown | Resolve by |
|---|---|---|
| V-027 | Is the rear wiper staying? No PMU channel exists for it | Decide; if yes it needs a C4 channel and a switch input |
| V-028 | Is the one-touch wipe function wanted in software? | Decide during Checklist 052 |

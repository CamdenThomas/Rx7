# Circuit — Front & Rear Wiper and Washer

*Rev 2026-09-07 · owns: the factory decode of this circuit — devices, wires, logic. Nothing of the new design lives here; the last section says where it does.*

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

The rebuild's side of every device and wire above is the electrical build's record, not this file's: find a factory code in its data — `python tools/rx7.py -p electrical-build find "C-02"` — or read the rendered [`DESIGN.md`](../../02-PROJECTS/electrical-build/01-DESIGN/DESIGN.md) §12 (device ends) and [`WIRE-TABLES.md`](../../02-PROJECTS/electrical-build/03-INSTALL/WIRE-TABLES.md). A hand-copied mapping table stood here until 2026-09-07; it had drifted three decisions behind and was removed — one fact, one home. Decisions that shaped this circuit's rebuild: D-014 · D-051 · D-097 · D-182.

## 5 · Unknowns

Every unknown this decode raised has an ID. The open ones live in the projects' `QUESTIONS.md` files (electrical, luxury, engine swap); the closed ones are cited with their closer in the projects' `DECISIONS.md`. This circuit's: V-027 · V-028.

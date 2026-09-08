# Circuit — Power Windows & Remote Mirrors

*Rev 2026-09-07 · owns: the factory decode of this circuit — devices, wires, logic. Nothing of the new design lives here; the last section says where it does.*

**Source:** Section I, page 28.

---

## 1 · Power windows

| Ref | Device | Pins |
|---|---|---|
| I-06 | Power window switch LH | RL, B / GL, BL |
| I-07 | Power window switch RH | R, B / G, BL |
| I-09 | Power window motor LH | R, G |
| I-11 | Power window motor RH | R, G |
| I-08 | Front↔door harness connector LH | RL/GL → R/G |
| I-10 | Inpane↔door harness connector RH | R/G |

| Item | Value |
|---|---|
| Feed | Ignition **IG** → BW → X-04 **30 A** → **BL** |
| Motors | **2 wires each** (R, G) — polarity reversal drives up/down |
| Switch topology | Each switch is a **DPDT reverser** — both motor legs land on the switch |
| Ground | BL common, B → X-13 |

**Confirms A-004** (A-004 → confirmed here, though the car has no window motors — D-131) — two conductors per motor, four total into the doors. The
factory switches do the reversing directly; the rebuild moves that to relays on
the panel (D-021) and the switches become PMU-side commands.

Note the factory feed is a single **30 A** fuse for both windows. That is the
number to size the motor bus against, not two separate loads.

## 2 · Remote control mirrors

| Ref | Device | Pins |
|---|---|---|
| I-01 | Remote control mirror switch | B, WG, LgR / Lg, LgB, LgY |
| I-03 | Remote control mirror LH | LgY, Lg, B, LgB |
| I-05 | Remote control mirror RH | LgY, Lg, B, LgB |

| Item | Value |
|---|---|
| Feed | WR constant → X-04 **10 A** → WG |
| Motors | Two motors per mirror (horizontal + vertical), 4 wires per side |
| Select | The switch does LH/RH selection **and** direction |
| Ground | B → X-13 |

These are **motor-driven mirrors, not heated mirrors.** SPEC allocates C5-B3 and
C5-B4 to *heated* mirrors off the comfort bus, and C5-B5…B8 as spares for mirror
motors. Four wires per side means the spares are exactly consumed — there is no
margin left in C5 if both functions are wanted.

## 3 · What this means for the rebuild

The rebuild's side of every device and wire above is the electrical build's record, not this file's: find a factory code in its data — `python tools/rx7.py -p electrical-build find "C-02"` — or read the rendered [`DESIGN.md`](../../02-PROJECTS/electrical-build/01-DESIGN/DESIGN.md) §12 (device ends) and [`WIRE-TABLES.md`](../../02-PROJECTS/electrical-build/03-INSTALL/WIRE-TABLES.md). A hand-copied mapping table stood here until 2026-09-07; it had drifted three decisions behind and was removed — one fact, one home. Decisions that shaped this circuit's rebuild: D-065 · D-093 · D-131 · D-181.

## 4 · Unknowns

Every unknown this decode raised has an ID. The open ones live in the projects' `QUESTIONS.md` files (electrical, luxury, engine swap); the closed ones are cited with their closer in the projects' `DECISIONS.md`. This circuit's: Q-022 · V-035 · V-036.

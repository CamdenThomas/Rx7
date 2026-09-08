# Circuit — Stop, Tail, Parking, Side Marker, License, Back-up

*Rev 2026-09-07 · owns: the factory decode of this circuit — devices, wires, logic. Nothing of the new design lives here; the last section says where it does.*

**Source:** Section F, page 22. All five share this sheet.

---

## 1 · Stop lights

| Item | Value |
|---|---|
| Feed | WR constant → X-04 **15 A** → GW |
| Fuse shared with | **Horn** |
| Switch | F-11 stop light switch, at the pedal. GW in, W out |
| Also feeds | Cruise control unit (Section B) via W |
| Checker | F-03 stop light checker — monitors filament, reports to meter (Section C) via G |
| Lamps | Rear combination, 27/8 W dual filament ×2 (27 W is the stop element) |
| Ground | B → X-15 |

Stop lights are **constant-hot** — they work with the key off, as they must.

## 2 · Tail / parking / side marker / license

One switched circuit, all on **RG**.

| Item | Value |
|---|---|
| Feed | WR constant → X-04 **10 A** → R |
| Switch | E-01 combination switch, LIGHT section (OFF / PARK / HEAD) |
| Output | RG — a single bus feeding every marker lamp on the car |
| Ground | B → X-13 (front), X-14 / X-15 (rear) |

| Lamp | Ref | W | Qty |
|---|---|---|---|
| Front parking | F-05 / F-06 | 8 | 2 |
| Front side marker | F-12 / F-13 | 3.8 | 2 |
| Rear side marker | F-14 / F-15 | 3.8 | 2 |
| License | F-04 | 6 | 2 |
| Tail | F-07 / F-08 | 8 | 2 |

Total roughly 55 W, ~4.6 A. RG stays on in both PARK and HEAD positions — which
is why D-015 keeps this as one circuit on O6.

## 3 · Back-up lights

| Item | Value |
|---|---|
| Feed | Ignition IG → BY → X-04 **10 A** → **GY** bus (shared with turn signals) |
| Switch, A/T | Inhibitor switch via A-06. GY in, RY out |
| Switch, M/T | Back-up light switch F-01. GY in, RW out |
| Output | RW → rear combination lights, via X-10 / X-03 |
| Lamps | 27 W ×2 |
| Ground | B → X-15 |

**This car is automatic** — the inhibitor switch is the active path (A-06),
not the M/T switch.

## 4 · What this means for the rebuild

The rebuild's side of every device and wire above is the electrical build's record, not this file's: find a factory code in its data — `python tools/rx7.py -p electrical-build find "C-02"` — or read the rendered [`DESIGN.md`](../../02-PROJECTS/electrical-build/01-DESIGN/DESIGN.md) §12 (device ends) and [`WIRE-TABLES.md`](../../02-PROJECTS/electrical-build/03-INSTALL/WIRE-TABLES.md). A hand-copied mapping table stood here until 2026-09-07; it had drifted three decisions behind and was removed — one fact, one home. Decisions that shaped this circuit's rebuild: D-071 · D-097 · D-119 · D-167 · D-182 · D-201.

## 5 · Unknowns

Every unknown this decode raised has an ID. The open ones live in the projects' `QUESTIONS.md` files (electrical, luxury, engine swap); the closed ones are cited with their closer in the projects' `DECISIONS.md`. This circuit's: Q-019 · Q-063 · V-023 · V-024.

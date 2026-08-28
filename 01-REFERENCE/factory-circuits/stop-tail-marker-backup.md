# Circuit — Stop, Tail, Parking, Side Marker, License, Back-up

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

| Factory | PMU-24 plan |
|---|---|
| Stop + horn sharing one 15 A fuse | O7 brake and O11 horn, separate channels and separate soft fuses |
| Stop light switch carrying lamp current | A3 input, switch-to-ground; O7 carries the load |
| Stop light checker | Deleted — PMU current sensing does the same job better |
| RG single marker bus | O6, split at panel to C2-B1 and C4-B1 |
| Light switch carrying RG current | A15 ladder input, 0–20 V, reads switched 12 V directly |
| Back-up on shared GY turn bus | O19, its own channel |
| Inhibitor switch | Feeds O19 logic — becomes a PMU input `[Q-019]` no pin allocated yet |
| Incandescent 8 W / 3.8 W / 6 W / 27 W | LED throughout |

## 5 · Unknowns

| ID | Unknown | Resolve by |
|---|---|---|
| Q-019 | Reverse trigger — inhibitor switch needs a PMU input, none allocated | Decide with Q-018; both are homeless inputs |
| V-023 | Whether the cruise control unit is still fitted and wanted | Inspect car |
| V-024 | Stop light checker present? Some cars had it deleted | Inspect car |

# PARTS CHANGES

*Rev 2026-08-30 · owns: what physically changes on the car in THIS project.*

Every load that will not be the same part at the end of the electrical rebuild.
Keeps the measured value and the design value from being confused.

**Not here:** anything pre-wired but deferred → [`DEFERRED-FEATURES.md`](DEFERRED-FEATURES.md).
Anything about bulbs or lamps → `../../lighting-body/`.

**Status key:** `CHOSEN` decided · `PENDING` known change, part not picked ·
`DEAD` confirmed not working · `DIAGNOSE` cause unknown

---

## Contents

1. Lighting — one line
2. Dead or dying
3. New — did not exist on the car
4. Replacing broken or missing
5. Deleted
6. Carrying forward unchanged
7. Designing against an unchosen part

---

## 1 · Lighting

**Stock incandescent bulbs, in stock housings, unchanged through this entire
project.** They work, they're consumable, and replacing them is the next
project's job.

Every lamp channel has 40–74% headroom on filament. See [`../01-DESIGN/LOADS.md`](../02-PROJECTS/electrical-pmu/01-DESIGN/LOADS.md).

**LED conversion, custom tail lights and headlamp units are `lighting-body/`.**
Hard prerequisite: this project finished and shaken down.

---

## 2 · Dead or dying

| Item | State | Replacement | Design implication |
|---|---|---|---|
| **Blower motor** | **`DEAD`** — confirmed not working (K-023) | Not chosen — `T-038` | **Cannot be measured.** O16 stays 25 A with the flyback diode and gets sized from the replacement's spec (D-126) |
| **Washer pump** | **`DIAGNOSE`** — not working (K-022) | Only if the pump itself is dead — `T-040`, then `T-039` | Diagnose before ordering — pump, wiring or switch. Its PMU output is `Q-063` → D-182 |
| **Fuel pump** | Carter P4070, working | Aeromotive Phantom 340 eventually | O5 sized for **8–12 A**, not the Carter's 1–3 A. `L4-P` carries a spare heavy cavity |
| Ionic battery heater | New, unquantified | — | Winter draw `V-052` |

**The rule for death-date items:** size the channel, wire and connector for the
worst plausible replacement. Set the soft fuse at migration from whatever is
actually fitted that day.

---

## 3 · New — did not exist on the car

| Item | Note | Status |
|---|---|---|
| **Fuel-door solenoid** | Never existed (D-098) — `T-032`. Output `Q-061` → D-180 | `PENDING` |
| **USB-C ports** | Replacing the deleted lighter | `PENDING` |
| **Oil temperature sender** | New ICU input | `PENDING` |
| **VSS sensor** | New ICU input | `PENDING` |
| **CAN keypad** | Ecumaster 8-key | `CHOSEN` |
| **DCU + ICU** | Teensy 4.1 ×2 | `CHOSEN` |
| **Cluster display** | One wide 800 × 480 panel (Q-037 → D-150). Panel choice `Q-060` → D-193 | `PENDING` |
| **Head unit** | Double-DIN, wireless CarPlay, full passthrough — criteria set (Q-055 → D-149) | `PENDING` |

Heated seats, cooled seats, heated nozzles, wiper de-icer and the radar
subsystem are **pre-wired but deferred** → [`DEFERRED-FEATURES.md`](DEFERRED-FEATURES.md).

---

## 4 · Replacing broken or missing

| Item | Why | Status |
|---|---|---|
| **Hatch latch switch** | Original broken (K-016) — `T-033` | `PENDING` |
| **Side mirrors** | Larger, heated, digital control (D-093). Factory control dead. Conductor count unconfirmed `V-060`; dash → sill conductors `Q-062` → D-181 | `PENDING` |

---

## 5 · Deleted — not carried into the new harness

| Item | Reason |
|---|---|
| Cigarette lighter | D-095 — freed 8–10 A on O10 |
| Cruise control unit and switches | D-097 — confirmed gone |
| Rear wiper and washer | D-097 — confirmed gone |
| Power antenna | D-097 — confirmed gone |
| Headlight cleaner | D-097 — confirmed gone |
| All cold-start hardware | D-097 — zero remain post-Weber |
| Stop light checker | D-097 — PMU current sensing replaces it |
| Control Processing Unit | D-013/014 — flasher, wiper INT, chime, belt, key reminder all become software |
| Instrument panel dimmer rheostat | O20 PWM replaces it |
| Retractable headlight switch | D-038 — pop-ups raise from the A15 ladder. Also broken (K-021) |
| Rear defrost switch | Moves to the CAN keypad. Also broken (K-020) |
| Horn relay | PMU switches the horns directly |
| Interval wiper control unit | Software timer on O8 |
| All 15 factory fuses and the fuse block | Soft fuses + 13 panel fuse positions + 3 at the sill |

---

## 6 · Carrying forward unchanged

**This is what the meter session exists for.** No spec sheet, no second chance.

| Item | Note |
|---|---|
| Wiper motor | Two-speed + park switch. O8/O9. **Measure stall** |
| Pop-up motors ×2 | Retained — pop-ups stay (D-110). **Measure stall** |
| Defog grid | **Measure cold** — grids draw more cold |
| Horns ×2 | Ground moves to the front star node |
| Starter + solenoid | K9 trigger only; K9 on the inner fender (D-148) |
| Alternator | Rating unread `V-002` |
| Ignition coils ×2, igniters ×2 | O12. Refreshed Aug 2025 |
| Fuel level sender | A7, ohm range unknown `V-037` → D-197 |
| Door pin switches | Already switch-to-ground |
| Brake pedal switch | Becomes a signal input |
| Turn / wiper / headlight stalks | Become resistor ladders |
| Ignition switch | A16 ladder — continuity test `T-023` → D-178 |
| Inhibitor switch | Crank interlock + reverse (D-071) — its PMU pin is `Q-063` → D-182 |
| A/C system entire | Factory circuit, untouched. Low on charge (K-015) |

**Not on this list:** window motors. **The windows are manual** (D-131).

---

## 7 · Designing against an unchosen part

Four rules, applied throughout:

1. **Size the channel for the worst plausible part**, not today's part. O5 is
   sized for the Aeromotive, not the Carter
2. **Wire gauge comes from voltage drop and mechanical robustness**, not current
   (D-016)
3. **Terminate every cavity now** (D-004). A capped spare costs a wire; a re-pin
   costs a housing and a teardown
4. **Set soft fuses at migration**, from the part actually fitted that day

**An unchosen part blocks almost nothing.** It only blocks its own soft-fuse
value, which is the last thing set anyway.

---

## Open items on this page

| ID | Item |
|---|---|
| `Q-060` → D-193 | Cluster panel selection |
| `Q-061` → D-180 | Where the hatch and fuel-door solenoids get an output |
| `Q-063` → D-182 | Where the washer pump gets an output |
| `V-060` | Mirror conductor count |
| `V-052` | Battery heater draw |
| `T-038` | Source a blower motor |
| `T-040` → `T-039` | Diagnose the washer pump; source one only if it is dead |

# MIGRATION LOG

*Rev 2026-08-31 · owns: the Phase 6 migration order and the per-circuit loop. [`CHECKLIST.md`](CHECKLIST.md) Phase 6 points here rather than restating it. Fill it in the car, at the time — not afterwards.*

## The per-circuit loop

1. Unplug the load at the factory connector
2. Tape the factory end back, label `MIGRATED` + date
3. Connect to the new harness
4. Enable that one output at its **Enable at** value below — the CSV's
   measured-or-channel-cap figure (D-175)
5. Operate it. Read live current on the PMU — **this is the real measurement**
   (D-174). Tighten the soft fuse per D-164's class multiplier and type both
   figures into `pmu_pins.csv`
6. Voltage-drop at the device under load — must be under 0.5 V
7. Fill in the row below

---

## Migration order — the single source

Least to most consequential, so a bad day never strands you.

| # | Circuit | Ch | Enable at (A) | Date | Measured A | Fuse set | V-drop | Factory end labelled | ✔ |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Interior + hatch lamps | O20 | 7.0 cap | | | | | ☐ | ☐ |
| 2 | USB-C ports | O10 | 15.0 cap | | | | | ☐ | ☐ |
| 3 | Horn | O11 | 15.0 cap | | | | | ☐ | ☐ |
| 4 | Wipers LOW | O8 | 15.0 cap | | | | | ☐ | ☐ |
| 5 | Wipers HIGH | O9 | 15.0 cap | | | | | ☐ | ☐ |
| 6 | Washer pump | K12 pulse (`Q-063` → D-182) | feed detail — H-008 | | | | | ☐ | ☐ |
| 7 | Tail / park / marker / plate | O6 | **7.5 meas** | | | | | ☐ | ☐ |
| 8 | Brake lamps | O7 | **9.5 meas** | | | | | ☐ | ☐ |
| 9 | Turn LEFT | O17 | **4.5 meas** | | | | | ☐ | ☐ |
| 10 | Turn RIGHT | O18 | **4.5 meas** | | | | | ☐ | ☐ |
| 11 | Reverse | O19 | 7.0 cap | | | | | ☐ | ☐ |
| 12 | Rear defog | O4 | 25.0 cap — cold read from telemetry | | | | | ☐ | ☐ |
| 13 | Headlight LOW | O2 | 25.0 cap | | | | | ☐ | ☐ |
| 14 | Headlight HIGH | O3 | 25.0 cap | | | | | ☐ | ☐ |
| 15 | Pop-up LEFT | O1 / K1 (D-186) | 25.0 cap | | | | | ☐ | ☐ |
| 16 | Pop-up RIGHT | O1 / K2 (D-186) | 25.0 cap | | | | | ☐ | ☐ |
| 17 | ~~Window DRIVER~~ | — | manual, bridge provisioned empty (D-131) | | | | | ☐ | n/a |
| 18 | ~~Window PASSENGER~~ | — | manual (D-131) | | | | | ☐ | n/a |
| 19 | Mirror heat (F14) | O15 | — deferred loads | | | | | ☐ | ☐ |
| — | ~~Mirror motors~~ | — | deferred until the new mirrors arrive (`Q-062` → D-181, `V-060`) | | | | | ☐ | n/a |
| 20 | Blower motor | O16 | from replacement spec (D-126) | | | | | ☐ | ☐ |
| 21 | Comfort bus | O15 | — deferred loads | | | | | ☐ | ☐ |
| 22 | Hatch release solenoid | O10 branch (`Q-061` → D-180) | branch fuse | | | | | ☐ | ☐ |
| 23 | Fuel-door solenoid | O10 branch (`Q-061` → D-180) | branch fuse | | | | | ☐ | ☐ |
| 24 | Fuel pump | O5 | **4.0 meas** (D-173) | | | | | ☐ | ☐ |
| 25 | Ignition / coils | O12 | 25.0 cap | | | | | ☐ | ☐ |
| 26 | **Start** | O21 / K9 | 7.0 cap | | | | | ☐ | ☐ |

Rows 6, 22 and 23 gained homes in the 0.23 ruling — washer on K12 (D-182), solenoids on fused O10 branches (D-180); they migrate once K12 and the branch fuses are fitted.

---

## Daily sign-off

**Before you stop, every single day:** confirm the car starts and drives
(Checklist 6.7).

| Date | Circuits done today | Car drives? | Notes |
|---|---|---|---|
| | | ☐ | |
| | | ☐ | |
| | | ☐ | |
| | | ☐ | |
| | | ☐ | |

---

## Gate before Phase 7

- [ ] Every row above ticked
- [ ] Full function check of every circuit in one pass (Checklist 6.8)
- [ ] **The car completes every function on dumb switches with no CAN module
      attached except the keypad.** If it can't, the DCU has crept onto the
      critical path and D-081 is violated
- [ ] Driven for a week with the factory harness disconnected but still fitted

---

## Second pass — after any bulb change

**Soft fuses set against incandescent are far too generous for LED.** A tail
circuit set at 6 A does not protect a 3 A LED load (D-122).

Re-run the measure-and-set loop on every lamp circuit after the bulbs change,
and record it here as a second pass. The LED figures to expect are
[`../01-DESIGN/LOADS.md`](../01-DESIGN/LOADS.md) Appendix A.

| Circuit | Ch | Date | Bulb type | Measured A | Soft fuse | ✔ |
|---|---|---|---|---|---|---|
| Tail / park / marker / plate | O6 | | | | | ☐ |
| Brake | O7 | | | | | ☐ |
| Turn LEFT | O17 | | | | | ☐ |
| Turn RIGHT | O18 | | | | | ☐ |
| Reverse | O19 | | | | | ☐ |
| Interior + details | O20 | | | | | ☐ |
| Headlight LOW | O2 | | | | | ☐ |
| Headlight HIGH | O3 | | | | | ☐ |

## Note on the first pass

**Migration happens on stock incandescent bulbs** (D-119). Every lamp channel has
40–74% headroom on filament, so nothing is marginal.

**Configure the inrush window before enabling any lamp channel** (D-120). A cold
filament pulls 8–12× steady for a few milliseconds and a flat soft-fuse limit
will trip on the first flash. Turn signals are the case to get right.

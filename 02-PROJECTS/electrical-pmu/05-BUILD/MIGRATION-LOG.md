# MIGRATION LOG

*Phase 6. One row per circuit. Fill it in the car, at the time — not afterwards.*

**The per-circuit loop:**
1. Unplug the load at the factory connector
2. Tape the factory end back, label `MIGRATED` + date
3. Connect to the new harness
4. Enable that one output, limit set just above the T-014 measurement
5. Operate it. Read live current. **Set the soft fuse from measured, not estimated**
6. Voltage-drop at the device under load — must be under 0.5 V
7. Fill in the row below

---

## Migration order — the single source

Least to most consequential, so a bad day never strands you. **This order is
authoritative; other files reference it rather than restating it.**

| # | Circuit | Ch | Date | Measured A | Soft fuse | V-drop | Factory end labelled | ✔ |
|---|---|---|---|---|---|---|---|---|
| 1 | Interior + hatch lamps | O20 | | | | | ☐ | ☐ |
| 2 | USB-C ports | O10 | | | | | ☐ | ☐ |
| 3 | Horn | O11 | | | | | ☐ | ☐ |
| 4 | Wipers LOW | O8 | | | | | ☐ | ☐ |
| 5 | Wipers HIGH | O9 | | | | | ☐ | ☐ |
| 6 | Washer pump | O10 | | | | | ☐ | ☐ |
| 7 | Tail / park / marker / plate | O6 | | | | | ☐ | ☐ |
| 8 | Brake lamps | O7 | | | | | ☐ | ☐ |
| 9 | Turn LEFT | O17 | | | | | ☐ | ☐ |
| 10 | Turn RIGHT | O18 | | | | | ☐ | ☐ |
| 11 | Reverse | O19 | | | | | ☐ | ☐ |
| 12 | Rear defog | O4 | | | | | ☐ | ☐ |
| 13 | Headlight LOW | O2 | | | | | ☐ | ☐ |
| 14 | Headlight HIGH | O3 | | | | | ☐ | ☐ |
| 15 | Pop-up LEFT | O1 / K1-K2 | | | | | ☐ | ☐ |
| 16 | Pop-up RIGHT | O1 / K3-K4 | | | | | ☐ | ☐ |
| 17 | ~~Window DRIVER~~ | — | **MANUAL — not fitted** `[D-131]` | | | | ☐ | n/a |
| 18 | ~~Window PASSENGER~~ | — | **MANUAL — not fitted.** Wire capped in the door | | | | ☐ | n/a |
| 19 | Mirrors — heat + motors | O15 | | | | | ☐ | ☐ |
| 20 | Blower motor | O16 | | | | | ☐ | ☐ |
| 21 | Comfort bus | O15 | | | | | ☐ | ☐ |
| 22 | Hatch release solenoid | spare | | | | | ☐ | ☐ |
| 23 | Fuel-door solenoid | spare | | | | | ☐ | ☐ |
| 24 | Fuel pump | O5 | | | | | ☐ | ☐ |
| 25 | Ignition / coils | O12 | | | | | ☐ | ☐ |
| 26 | **Start** | O21 / K9 | | | | | ☐ | ☐ |

---

## Daily sign-off

**Before you stop, every single day:** confirm the car starts and drives.

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
- [ ] Full function check of every circuit in one pass
- [ ] **The car completes every function on dumb switches with no CAN module
      attached except the keypad.** If it can't, the DCU has crept onto the
      critical path and D-081 is violated
- [ ] Driven for a week with the factory harness disconnected but still fitted

---

## Second pass — after any bulb change

**Soft fuses set against incandescent are far too generous for LED.** A tail
circuit set at 6 A does not protect a 3 A LED load (D-122).

Re-run the measure-and-set loop on every lamp circuit after the bulbs change,
and record it here as a second pass.

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

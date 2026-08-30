# CHANNEL SCHEDULE

*Rev 2026-08 · owns: the measured-to-configured pipeline*

**This is the sheet the meter session fills in.** Everything downstream — the
soft fuse values, the PMU config, the simulator, the diagnostics page — derives
from these numbers.

Fill the **MEASURED** column, apply the formula, and the project is done
guessing.

---

## How a soft fuse is set

**Never from an estimate.** The rule, in order of precedence:

| Load type | Soft fuse | Why |
|---|---|---|
| **Motors** | measured **stall** × 1.10 | Stall is the real worst case and it is a steady reading you create on purpose |
| **Filament lamps** | measured steady × 1.35, **plus an inrush window** | Cold inrush is 8–12× for a few ms — handled by time characteristic, not by raising the limit |
| **Resistive** (defog) | measured **cold** × 1.20 | Grids draw most when cold; that is the design case |
| **Electronics** | measured steady × 1.50 | Small absolute numbers, so a wider margin costs nothing |
| **Anything unmeasured** | leave **DISABLED** | An output with a guessed limit is worse than an output that is off |

Round **up** to the nearest 0.5 A. A limit set too tight nuisance-trips at the
worst moment; one set too loose is still far better protection than the 15 A
blade fuse it replaces.

> **The limit protects the WIRE, not the load.** A 14 AWG circuit is good for
> far more than any of these figures — the soft fuse exists to catch a short or
> a seizing motor, not to police normal operation.

---

## The schedule

`EST` = estimate, replace me. `MEAS` = measured, trust me.
`STALL` where the motor figure is what matters.

| Ch | Circuit | Class | Goes to | AWG | EST A | **MEASURED A** | Type | **SOFT FUSE** |
|---|---|---|---|---|---|---|---|---|
| **O1** | Motor bus | 25 A | relay bank | 12 | 9.5 | ______ *stall* | motor | ______ |
| **O2** | Headlight LOW | 25 A | L2-P1 1 | 12 | 3.0 | ______ | LED | ______ |
| **O3** | Headlight HIGH | 25 A | L2-P1 2 | 12 | 3.5 | ______ | LED | ______ |
| **O4** | Rear defog | 25 A | L4-P 1 | 12 | 11.5 | ______ *cold* | resistive | ______ |
| **O5** | Fuel pump | 25 A | L4-P 2 | 12 | 2.0 | ______ | motor | ______ |
| **O6** | Tail / park / plate | 15 A | L2-M 7, L4-M 1 | 14 | 4.4 | ______ | filament | ______ |
| **O7** | Brake | 15 A | L4-M 2 | 14 | **7.0** | **7.0 MEAS** | filament | **9.5** |
| **O8** | Wiper LOW ⚙ | 15 A | L2-M 1 | 14 | 4.0 | ______ *stall* | motor | ______ |
| **O9** | Wiper HIGH | 15 A | L2-M 2 | 14 | 5.5 | ______ *stall* | motor | ______ |
| **O10** | Accessory bus | 15 A | L3-M 1 | 14 | 2.5 | ______ | electronics | ______ |
| **O11** | Horn | 15 A | L2-M 3 | 14 | 6.0 | ______ | electro-mech | ______ |
| **O12** | Ignition / coils | 25 A | L1-P 1 | 12 | 5.0 | ______ *at 3000* | electronics | ______ |
| **O13** | LS ECU | 25 A | L1-P 2 capped | 12 | — | *reserved* | — | **disabled** |
| **O14** | LS cooling fan | 25 A | L1-P 3 capped | 12 | — | *reserved* | — | **disabled** |
| **O15** | Comfort bus | 25 A | L3-P 2 | 12 | 14.0 | ______ | mixed | ______ |
| **O16** | Blower ⚡ | 25 A | L3-P 1 | 12 | — | **motor is DEAD** | motor | from replacement spec |
| **O17** | Turn LEFT | 7 A | L2-M 5, L4-M 5 | 16 | **3.4** | **3.4 MEAS** | filament | **4.5** |
| **O18** | Turn RIGHT | 7 A | L2-M 6, L4-M 6 | 16 | **3.4** | **3.4 MEAS** | filament | **4.5** |
| **O19** | Reverse | 7 A | L4-M 7 | 16 | 3.9 | ______ | filament | ______ |
| **O20** | Interior + details | 7 A | L4-M 8, L3-S | 16 | 2.5 | ______ | filament | ______ |
| **O21** | Start relay coil | 7 A | L1-S 1 | 16 | 0.9 | ______ | relay coil | ______ |
| **O22** | Keep-alive latch | 7 A | panel | 16 | 0.15 | ______ | logic | ______ |
| **O23** | Spare | 7 A | — | 16 | — | — | — | **disabled** |
| **O24** | Spare | 7 A | — | 16 | — | — | — | **disabled** |

**3 of 24 measured.** The rest are estimates carried since Rev A.

---

## Where the numbers go afterwards

Type the measured column into **one** place and everything follows:

```
firmware/pmu_sim/channels.h      <- the machine-readable copy
```

Each row there has `steady`, `limit`, `inrushX10`, `inrushMs` and a `src` tag.
Change `EST` to `MEASURED` as you go — **the simulator prints how many are still
guesses at boot**, so the count only ever goes down.

Then:

| Consumer | Gets what |
|---|---|
| PMU client config | The soft-fuse column, entered by hand at Checklist 2.x |
| `pmu_sim` | Realistic currents on CAN 0x130 |
| Diagnostics page | Real bars showing draw against limit |
| `01-DESIGN/LOADS.md` | Updated design figures |
| `MIGRATION-LOG.md` | The per-circuit target to compare against |

---

## Inrush windows

Separate from the limit, and the thing that stops lamps tripping on the first
flash (D-120).

| Type | Multiplier | Window |
|---|---|---|
| Filament lamps | 10× | 100 ms |
| Motors, running start | 7× | 300–400 ms |
| Blower | 8× | 600 ms |
| Resistive grid | 1.3× | 2 s |
| Electronics | 1.5–2× | 100 ms |

**Turn signals are the case to get right.** They cycle constantly, so the window
fires 1.5 times a second forever. After the first flash the filament stays warm
and the real inrush is much smaller — but the first one is full size.

---

## What "not measured" costs

An unmeasured channel can still be wired, terminated and migrated. It just
cannot be **protected properly**, so it stays disabled until the number exists.

That is the whole reason `T-014` is the one irreversible-window task: every
figure above is recoverable from the car **only while the factory harness is
still in it.**

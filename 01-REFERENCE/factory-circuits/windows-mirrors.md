# Circuit — Power Windows & Remote Mirrors

*Rev 2026-08-30 · owns: the factory decode of this circuit — devices, wires, logic. The rebuild table at the foot points into the new design and is not its owner; cavities are `02-HARNESS/data/connectors.csv`'s.*

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

**This car has manual windows and dead power mirrors** (D-131, K-014). The
factory section I circuit exists on the diagram, not on the car.

| Factory | PMU-24 plan |
|---|---|
| 30 A window fuse | O1 motor bus with F8/F9 at the sill — **PROVISIONED**: the bus feed (**L4-P 3**), the command wires (**L3-S2 3–6 → L4-M 9–12**), the K5–K8 sockets and the door legs (**D1/D2 1–2**) are terminated and capped, nothing populated |
| DPDT window switches in the doors | Would be dash-side commands to the sill relays (D-065) — not fitted |
| 2-wire motors | **D1/D2 1–2**, 14 AWG — capped in the door |
| Mirror switch on 10 A constant | New heated, digitally controlled mirrors (Q-022 → D-093, `T-031`). Conductor count `V-060`; dash → sill path `Q-062` |
| Mirror motors, 4 wires per side | **D1/D2 4–6** DEFERRED; mirror heat **D1/D2 7** off sill fuse F14, DEFERRED |

## 4 · Unknowns

| ID | Unknown | Resolve by |
|---|---|---|
| V-035 → D-092 / D-093 | Door connector spare count | One DT06-08S per door, zero spares — the mirror choice is load-bearing |
| V-036 → D-131 / K-014 | Windows and mirrors working? | Windows are manual; mirror control is dead |
| Q-022 → D-093 | Keep remote mirror motors? | New mirrors, independent wiring per side |

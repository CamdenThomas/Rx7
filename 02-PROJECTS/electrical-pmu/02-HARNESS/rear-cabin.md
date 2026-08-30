# LEG 4 — REAR CABIN

*Rev 2026-08-30 · owns: what is in the rear leg and why. Cavities are [`PIN-MAP.md`](PIN-MAP.md)'s; draw figures are [`../01-DESIGN/LOADS.md`](../01-DESIGN/LOADS.md)'s.*

**Boundary:** tunnel entry at the console, running back to the hatch, plus the
sill runs into both doors.
**Ground:** rear star node. Doors ground at the sill node, not in the door.
**Housings:** L4-P (DTP-4) · L4-M (DT-12) · L4-S (DT-8), plus D1/D2 at the
sill ([`sill-node.md`](sill-node.md)). Diagram: `diagrams/L4-rear-cabin.svg`.

---

## Rear body devices

| Device | OEM ref | Direction | Goes to | Note |
|---|---|---|---|---|
| Rear defog grid | G-25 | Out | O4 via L4-P 1 | Measure **cold** |
| Fuel pump — Carter P4070 | B-24 | Out | O5 via L4-P 2 | Own return at the rear node — the K-008 fix. Sized for the Aeromotive later |
| Fuel level sender | C-01 | In | A7 via L4-S 1 | Resistive — `V-037` |
| Tail / plate / rear markers | F-04/07/08/14/15 | Out | O6 via L4-M 1 | Filament |
| Brake lamps | F-07/F-08 | Out | O7 via L4-M 2 | **7.0 A measured** |
| Turn LEFT / RIGHT rear | F-07 / F-08 | Out | O17 / O18 via L4-M 5, 6 | 3.4 A measured per side |
| Reverse lamps | F-07/F-08 | Out | O19 via L4-M 7 | `Q-063` may move these to the inhibitor's R contact |
| Luggage compartment light + switch | H-11, H-12 | Out / In | O20 bus; switch → A6 node via L4-S 3 | `A-012` |
| Hatch release solenoid | H-14 | Out | L4-M 3 — **no output yet** | `Q-061`. Latch switch broken (K-016) |
| Fuel-door release solenoid | new | Out | L4-M 4 — **no output yet** | `Q-061`. Never existed (D-098) |
| Rear speakers | G-09/G-10 | — | — | Audio, independent of the PMU |

## Cabin devices

| Device | OEM ref | Direction | Goes to | Note |
|---|---|---|---|---|
| Interior & spot light, footwell / sill / console lighting | H-06, new | Out | O20 via L4-M 8, F12 branch | PWM theatre fade |
| Heated / cooled seats | new | Out | O15 via the DCU, F10 | DEFERRED |

## Door devices — via the sill

| Device | OEM ref | Direction | Goes to | Note |
|---|---|---|---|---|
| Door switches LH / RH | H-08, H-07 | In | A6 ladder via D1 3 / D2 3 → L4-S 2 | Already switch-to-ground |
| Window motors | I-09, I-11 | Out | D1/D2 1–2, **capped in the door** | **Not fitted — windows are manual** (D-131). PROVISIONED |
| New mirrors — motors | replaces I-03/I-05 | Out | D1/D2 4–6 | DEFERRED. Control protocol `V-060`; dash → sill conductors `Q-062` |
| New mirrors — heat | new | Out | D1/D2 7 via sill fuse F14 | DEFERRED. O15 → sill conductor `Q-062` |

## Devices deleted

| Device | OEM ref | Status |
|---|---|---|
| Stop light checker | F-03 | **Deleted** — PMU current sensing replaces it (D-097) |
| Rear wiper and washer | D-04, D-05 | **Confirmed gone** (D-097) |
| Power antenna | G-02 | **Confirmed gone** (D-097) |
| Seat belt switch | H-04 | **Dropped** with the chime (D-050) |
| Factory mirror switch and motors | I-01, I-03, I-05 | **Dead**; replaced by new mirrors (D-093) |

## Leg totals

| | Value |
|---|---|
| Heavy conductors (12 AWG) | Defog, fuel pump = 2 used · 1 provisioned window bus · 1 spare |
| Medium (14 AWG) | Tail bus, brake, hatch solenoid, fuel-door solenoid = 4 |
| Light (16 AWG) | Turn L, turn R, reverse, interior PWM, 4 provisioned window commands = 8 |
| Signal (16 AWG) | Fuel sender, door pins, luggage switch, +5 V ref, 3 deferred radar, 1 spare = 8 |
| Est. peak draw | ~15 A — defog + fuel pump (windows would add ~10 A each when fitted) |
| Ground | Rear star node + sill node for doors |

## Why this leg is shaped the way it is

**Fixing K-008 lives here.** Factory put the fuel pump ground and the rear turn
lamp grounds on the same X-15 stud. Separating those is the direct structural
fix. The fuel pump gets its own return to the rear node — not a shared one.

**L4-P2 is gone** (D-066). When the window relays moved to the sill (D-065)
the four 12 AWG motor legs stopped crossing the tunnel; one provisioned 12 AWG
feed and four 16 AWG commands replaced them.

**The tunnel run is the longest in the car.** Voltage drop, not current, sets
the gauge on the defog and fuel pump legs.

**Separate the sender from the pump.** The fuel level sender in L4-S runs the
full length of the tunnel alongside the fuel pump feed in L4-P. Separate
housings mean they can be separated physically — do it. A resistive sender
sharing a bundle with a pump feed is the same class of mistake that produced
K-008.

**Doors are inside this leg by choice** (D-051, D-068). The sill run comes out
with the interior; the door boot is a service point, not a removal boundary.

**Two things still need a conductor across the tunnel** — the O15 feed for
the mirror heat and whatever the new mirrors need for control (`Q-062`) — and
two loads need an output that does not exist (`Q-061`). L4-P 4 and L4-S 8 are
the spares available.

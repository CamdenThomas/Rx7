# Legs — modular removal design

*Rev 2026-08-30 · owns: the leg boundaries and the map of this folder. Cavities are [`PIN-MAP.md`](PIN-MAP.md)'s; housings are [`CONNECTORS.md`](CONNECTORS.md)'s.*

Four physical legs, cut by **what comes out of the car as one piece**, not by
connector count (D-029).

| Leg | Removal boundary | Comes out with |
|---|---|---|
| **ENGINE** | Firewall grommet | Engine, or engine-bay service |
| **FRONT CHASSIS** | Firewall / radiator support | Nose, bumper, pop-up assemblies |
| **DASH** | Dash structure | The dash as a unit |
| **REAR CABIN** | Tunnel entry at the console | Interior + rear body, incl. the sill and doors |

## The rule that defines a leg

A leg is a bundle that can be **fully removed without disturbing any other leg.**
Every device in a leg is fed and returned entirely within it. Nothing shares a
ground across a boundary. If a device would straddle two legs, the boundary is
wrong or the device needs a local node.

## Boundary decisions

- **Doors are inside REAR CABIN**, entering through the sill. The door boot is a
  service point, not a removal boundary (D-051, D-068).
- **The cowl is inside FRONT CHASSIS.** The wiper motor and washer come off with
  nose work, not with the engine.
- **The fuel pump and tank sender are REAR CABIN**, reached through the hatch.
- **The sill is a sub-node of REAR CABIN**, not a fifth leg — it has no
  independent removal boundary (D-065, D-132).
- **The panel belongs to no leg.** It is the hub the legs plug into. The four
  drops (DP-ICU, DP-DCU, DP-DIAG, DP-KEY) are box-adjacent and belong to no leg
  either.

## Files

| File | Holds |
|---|---|
| `data/pmu_pins.csv` · `data/connectors.csv` · `data/housings.csv` | **The source of truth for every pin, cavity and housing.** Edit these |
| [`PIN-MAP.md`](PIN-MAP.md) | **Authoritative cavity assignments** — generated from the CSVs |
| [`CAVITY-STATE.md`](CAVITY-STATE.md) | What is live, provisioned, reserved, deferred, open or spare — generated |
| `diagrams/*.svg` | One wiring diagram per leg, plus the sill and the drops — generated |
| [`CONNECTORS.md`](CONNECTORS.md) | Housing part numbers, series selection, wedgelocks, the dash post |
| [`sill-node.md`](sill-node.md) | Door connectors D1/D2, the sill ground, the provisioned window relays |
| [`engine.md`](engine.md) · [`front-chassis.md`](front-chassis.md) · [`dash.md`](dash.md) · [`rear-cabin.md`](rear-cabin.md) | The four legs — devices, boundaries and *why* |

**Leg files describe *why*. PIN-MAP owns *what*.** A cavity number in a leg
file is a courtesy copy of the generated map; if they ever disagree, the map
wins and the leg file gets fixed.

## Leg summary

| Leg | Housings | Heavy 12 AWG conductors | Est. peak A |
|---|---|---|---|
| L1 Engine | L1-P, L1-S1, L1-S2 | 3 used + 1 spare | ~8 now, ~30 post-LS |
| L2 Front | L2-P1, L2-P2, L2-M, L2-S | 6 used + 2 spare | ~35 — both pop-ups moving + wipers + headlights |
| L3 Dash | L3-P, L3-M, L3-S1, L3-S2, L3-S3 | 2 | ~30 — blower + comfort bus |
| L4 Rear | L4-P, L4-M, L4-S | 2 used + 1 provisioned + 1 spare | ~15 — defog + fuel pump |
| — sill sub | D1, D2 | 4 × 14 AWG, provisioned | — |

**15 leg housings + 2 door + 4 drops + 2 lugs + the PMU = 24 mated pairs**
([`PIN-MAP.md`](PIN-MAP.md) §Counts).

## Elsewhere

- As-built factory car: `../../../01-REFERENCE/factory-circuits/OEM-RECORD.md`
- Estimated draw and signal types: [`../01-DESIGN/LOADS.md`](../01-DESIGN/LOADS.md)
- Measured draw and soft fuses: [`../01-DESIGN/CHANNEL-SCHEDULE.md`](../01-DESIGN/CHANNEL-SCHEDULE.md)
- Panel sub-circuits: [`../01-DESIGN/SCHEMATICS.md`](../01-DESIGN/SCHEMATICS.md)

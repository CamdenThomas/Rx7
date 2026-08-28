# Legs — modular removal design

*Rev 2026-08*

Four physical legs, cut by **what comes out of the car as one piece**, not by
connector count.

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
  service point, not a removal boundary *(D-068)*.
- **The cowl is inside FRONT CHASSIS.** The wiper motor and washer come off with
  nose work, not with the engine.
- **The fuel pump and tank sender are REAR CABIN**, reached through the hatch.
- **The sill is a sub-node of REAR CABIN**, not a fifth leg — it has no
  independent removal boundary *(D-065)*.
- **The panel belongs to no leg.** It is the hub the legs plug into.

## Files

| File | Holds |
|---|---|
| `PIN-MAP.md` | **Authoritative cavity assignments.** Every conductor → PMU pin, relay or fuse |
| `CONNECTORS.md` | Housing part numbers, series selection, the dash post |
| `sill-node.md` | Window relays K5–K8, branch fuses, door connectors D1/D2 |
| `engine.md` | Leg 1 contents and rationale |
| `front-chassis.md` | Leg 2 |
| `dash.md` | Leg 3 |
| `rear-cabin.md` | Leg 4 |

**Leg files describe *why*. PIN-MAP owns *what*.** If a cavity number appears in
both and they disagree, PIN-MAP wins.

## Leg summary

| Leg | Connectors | Heavy 12 AWG | Est. peak A |
|---|---|---|---|
| L1 Engine | L1-P, L1-S ×2 | 4 | ~8 now, ~30 post-LS |
| L2 Front | L2-P1, L2-P2, L2-M, L2-S | 7 | ~35 |
| L3 Dash | L3-P, L3-M, L3-S1/S2/S3 | 2 | ~35 |
| L4 Rear | L4-P, L4-M, L4-S | 3 | ~30 |
| — sill sub | D1, D2 | 4 sill→door | — |

**14 leg connectors + 2 door + 4 dash-post drops + 2 lugs + the PMU = 23 mated
pairs.**

## Elsewhere

- As-built factory car: `../../../01-REFERENCE/factory-circuits/OEM-RECORD.md`
- Current draw and signal types: `../LOADS.md`
- Panel sub-circuits: `../SCHEMATICS.md`

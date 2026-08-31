# PANEL LAYOUT — planning

*Rev 2026-08-31 · owns: what has to fit on the plate and the layout principles. Blocked on `Q-014` / `T-007` for final dimensions.*

Everything that can be decided without the measurement is decided here.

---

## What has to fit

| Component | Size | Notes |
|---|---|---|
| **PMU-24 DL** | 131 × 112.1 × 32.5 mm | 3 × Ø6.5 mounting. Connector on the short edge, stud opposite |
| Relay sockets ×10 | ~26 × 26 mm each | 4 populated: K1, K2, K11, K12 (D-182, D-186) |
| Fuse block, 12 way | ~120 × 60 mm | ATO/mini. Full — F15 is the exciter (D-198); F13 radar, deferred (D-191) |
| Busbar, always-hot | ~100 × 25 mm | |
| Ground bus | ~100 × 25 mm | |
| Diode-OR terminal strip | 8 position, ~80 mm | 8 used — strip full (D-189, D-190) |
| **Leg receptacles ×15** | see below | The real space consumer — L1-S is two DT-12s |
| DP-DIAG, DP-KEY, DP-ICU, DP-DCU | 4 more | |
| Battery lugs ×2 | M8 studs | |

### Receptacle footprints

| Housing | Approx face | Qty |
|---|---|---|
| DTP04-2P | 25 × 20 mm | 1 |
| DTP04-4P | 35 × 22 mm | 4 |
| DT04-2P | 22 × 18 mm | 1 |
| DT04-6P | 32 × 22 mm | 2 |
| DT04-08P | 38 × 26 mm | 3 |
| DT04-12P | 45 × 28 mm | 6 |
| DTM04-4P | 20 × 16 mm | 2 |

**Rough edge length needed: ~450 mm of receptacle frontage.** That is the number
to check against the dash cavity, and it likely means receptacles on **two edges**
rather than one.

## Layout principles

**1 · The 39-pin lever needs clearance.** It is the one thing that must be
operable with the panel mounted, at least once. Leave a clear arc.

**2 · Pin 25 ground is the shortest, heaviest wire on the plate.** Put the ground
bus immediately adjacent to the PMU connector, not across the plate. It carries
flyback return for every inductive load.

**3 · Stud feed short and direct.** Busbar next to the stud.

**4 · Separate the relay bank from the signal receptacles.** K1–K4 switch
inductively. Signal legs — L1-S1/S2, L2-S, L3-S1/S2/S3, L4-S, DP-ICU — should
not run past them.

**5 · Group receptacles by leg.** All of L2's four housings adjacent, all of L3's
five adjacent. A leg comes out as a unit; it should unplug as one.

**6 · Fuses reachable without removing the panel.** F1–F5 especially — those are
the constant-bus fuses that will be checked when something odd happens.

**7 · PMU standoff for airflow.** It dissipates real heat at 150 A capability.

## Suggested zoning

```
   ┌─────────────────────────────────────────────┐
   │  [BATT LUGS]        [BUSBAR]   [GND BUS]    │
   │                                              │
   │      ┌──────────────────┐                    │
   │      │   PMU-24 DL      │   [DIODE STRIP]    │
   │      │  131 x 112 mm    │                    │
   │      └────[39-PIN]──────┘   [FUSE BLOCK]     │
   │            ↑ lever arc                       │
   │  [K1 K2 K11 K12] [6 spare sockets]           │
   │                                              │
   ├──── L1 ───┬── L2 ────┬── L3 ──────┬── L4 ─────┤
   │  P S1 S2  │ P1 P2 M S│ P M S1 S2 S3│ P  M  S  │
   └─────────────────────────────────────────────┘
         DP-DIAG  DP-KEY  DP-ICU  DP-DCU
```

Receptacles along the bottom edge grouped by leg; modules and drops on a second
edge if frontage runs short.

## Dash space — the expedited estimate (D-202)

Ordered against an estimate; `T-007` confirms on teardown day 1 **before any
plate is cut**. What is actually known without the tape measure:

| Fact | Value | Source |
|---|---|---|
| PMU envelope | 131 × 112.1 × 32.5 mm | CAD, confirmed (SPEC §11) |
| Receptacle frontage needed | ~450 mm, two edges likely | This file |
| Cluster aperture (Camden, preliminary) | ~100 mm tall × 260–300 mm wide | Q-014 note |
| Centre-stack face freed by deleting radio/cassette + ashtray + lighter | ≈ 180 mm wide × ~160–180 mm tall below the HVAC head (shaft-style radio era — the 79–83 opening is ~178 mm wide) | Estimate — `V-087` |
| Behind-stack depth | **unknown** — the one number that matters | `V-087` / `T-007` |
| Factory/old amp position | relocates to the rear cargo bin with battery + Class-T + disconnect (space confirmed by eye, `V-088`) | Camden |

**Reading:** the PMU alone fits the freed centre-stack face nearly twice over
— Camden's hunch holds on face area. The full panel does not fit the stack
alone: the fuse blocks, relay bank, busbars and ~450 mm of receptacle
frontage want the region behind/below the glovebox as well, which matches
the two-edge zoning above. Nothing in the expedited order depends on the
answer — plate stock is generic sheet, cut after `T-007`.

## The measurement that decides everything

`T-007` — dash cavity: **width × height × depth**, plus:

- Clear arc for the 39-pin lever
- Depth for the deepest connector plus its backshell and wire bend radius —
  budget **60 mm behind any receptacle face**
- Access to F1–F5 with the panel in place
- Somewhere the panel can be unbolted and withdrawn as a unit

**The panel got smaller than originally planned** — the relay bank dropped from
16 sockets to 10 when K5–K8 moved to the sill (D-067), and those four sockets
sit empty until power windows are fitted (D-131). If space was going to be the
problem, it is less of one now.

## Fabrication

| Item | Spec |
|---|---|
| Material | 3 mm aluminium sheet |
| Finish | Anodised or powder-coated. **Not bare** — it is a ground plane risk otherwise |
| Mounting | 4 points minimum, rubber-isolated |
| Labels | Every relay position and fuse **on the plate itself**, not on the component |

## Next step

Measure `T-007`, then Claude produces the 1:1 drawing with real dimensions.
Everything above survives the measurement — only the arrangement changes.

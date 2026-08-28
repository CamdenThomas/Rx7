# Reference

Source documents. Binary files welcome here. **Index everything you drop in.**

| File | What it is | Notes |
|---|---|---|
| `factory-circuits/1982RX7WiringDiagram.pdf` | Factory wiring diagram, **1982** FB | 31 pages, scanned, no text layer. Decoded circuit by circuit in `factory-circuits/` |
| `PMU_info/PMU-24_Pinout_v1.0.pdf` | ECUMaster pinout | Pin numbers, terminal part numbers, device view. **Source for SPEC §11** |
| `PMU_info/PMU_Manual.pdf` | ECUMaster PMU manual | Software, logic functions, configuration |
| `PMU_info/PMU CAD info/PMU-24.pdf` | 2D dimensional drawing | 131 × 112.1 × 32.5 mm, 3 × Ø6.5 mounting. **Source for the cavity layout** |
| `PMU_info/PMU CAD info/PMU-24.STEP` | 3D model | For panel layout and clearance checking |
| `PMU_info/PMU CAD info/PMU-24_3D.pdf` | 3D views | |
| `TS-ICT-T-C-CAT-2018.pdf` | Terminal / connector catalogue | `[V-062]` confirm which series it covers and whether it lists the 211CC… terminals |
| `factory-circuits/` | The 1982 harness decoded — 10 circuit files, `OEM-RECORD.md`, fuse and ground maps | The frozen record of the car as built |

## Obtained since this list was first written

| Was wanted | Status |
|---|---|
| Sicma 39-pos housing geometry | **RESOLVED** from the CAD + pinout device view. SPEC §11, D-045 |
| ECUMaster PMU-24 pinout PDF | **Obtained**, local copy above |
| AMPSEAL catalogue page | **Moot** — AMPSEAL dropped from the design (D-052) |
| 1983 vs 1982 diagram question | **Moot** — the 1982 diagram was obtained |

## Still wanted

| Need | For | Priority |
|---|---|---|
| 1982 FSM electrical section | Cross-checking connector pin letters `[T-017]` | Medium |
| Ionic S9 manual / heater spec | `[V-052]` heater trigger and winter draw | Medium |
| TE Deutsch DT contact datasheet | `[V-014]` size-16 rating vs window stall | Low |
| Aeromotive Phantom 340 spec | `[V-040]` — future part | Low |

## Rule

Anything dropped in this folder gets a row in the table above **in the same
session**. An unindexed reference file is one nobody will find twice.

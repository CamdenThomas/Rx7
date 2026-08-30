# Reference

*Rev 2026-08-30 · owns: the index of every source document in this folder. Binary files welcome; **index everything you drop in, in the same session.** An unindexed reference file is one nobody will find twice.*

| File | What it is | Notes |
|---|---|---|
| [`factory-circuits/1982RX7WiringDiagram.pdf`](factory-circuits/1982RX7WiringDiagram.pdf) | Factory wiring diagram, **1982** FB | 31 pages, scanned, no text layer, 29 MB. Decoded circuit by circuit in [`factory-circuits/`](factory-circuits/README.md) |
| [`factory-circuits/`](factory-circuits/README.md) | The 1982 harness decoded — 10 circuit files, the frozen [`OEM-RECORD.md`](factory-circuits/OEM-RECORD.md), fuse and ground maps, the K-008 trace | The record of the car as built |
| [`PMU_info/PMU-24_Pinout_v1.0.pdf`](PMU_info/PMU-24_Pinout_v1.0.pdf) | ECUMaster pinout | Pin numbers, terminal part numbers, device view. **Source for [`SPEC.md`](../02-PROJECTS/electrical-pmu/01-DESIGN/SPEC.md) §2 and §11.** The v1.2/1.3 revision moved the 1.5 mm terminal range to 14–17 AWG |
| [`PMU_info/PMU_Manual.pdf`](PMU_info/PMU_Manual.pdf) | ECUMaster PMU manual | Software, logic functions, configuration. 28 MB. Answers `V-074` and `V-075` |
| [`PMU_info/PMU CAD info/PMU-24.pdf`](PMU_info/PMU%20CAD%20info/PMU-24.pdf) | 2D dimensional drawing | 131 × 112.1 × 32.5 mm, 3 × Ø6.5 mounting. **Source for the cavity layout** (D-045) |
| [`PMU_info/PMU CAD info/PMU-24.STEP`](PMU_info/PMU%20CAD%20info/PMU-24.STEP) | 3D model | For panel layout and clearance checking |
| [`PMU_info/PMU CAD info/PMU-24_3D.pdf`](PMU_info/PMU%20CAD%20info/PMU-24_3D.pdf) | 3D views | |
| [`TS-ICT-T-C-CAT-2018.pdf`](TS-ICT-T-C-CAT-2018.pdf) | **TE Connectivity Industrial & Commercial Transportation** terminals and connectors catalogue, 2018, 256 pages (V-062 → D-114) | DT family pp. 109–132, contacts 169–180, tooling 181–190, CAN 195–207. 15 MB. Does **not** cover the FCI/Sicma 211CC… terminals — those are Ballenger, [`BUY-LIST.md`](../02-PROJECTS/electrical-pmu/06-PROCUREMENT/BUY-LIST.md) §3 |
| [`Part Dates - Sheet1.pdf`](Part%20Dates%20-%20Sheet1.pdf) | Camden's parts sheet — what was bought, when, from where | Imported into [`../00-CAR/parts-history.md`](../00-CAR/parts-history.md); incomplete, more to come |
| [`photos/`](photos/README.md) | Harness photographs from `T-018`, by zone | Empty until Checklist 0.12. Naming convention in its README |

## Obtained since this list was first written

| Was wanted | Status |
|---|---|
| Sicma 39-pos housing geometry | **Resolved** from the CAD and pinout, then confirmed in the hand — [`SPEC.md`](../02-PROJECTS/electrical-pmu/01-DESIGN/SPEC.md) §11, D-045, D-134, D-139 |
| ECUMaster PMU-24 pinout PDF | **Obtained**, local copy above |
| AMPSEAL catalogue page | **Moot** — AMPSEAL dropped from the design (D-052) |
| 1983 vs 1982 diagram question | **Moot** — the 1982 diagram was obtained |
| What the TE catalogue covers | **Answered** — D-114 |

## Still wanted

| Need | For | Priority |
|---|---|---|
| 1982 FSM electrical section | Cross-checking connector pin letters (`T-017`); redline, oil pressure, tank capacity (`V-070`–`V-072`) | Medium |
| Ionic S9 manual / heater spec | `V-052` heater trigger and winter draw | Medium |
| TE Deutsch DT contact datasheet | `V-014` size-16 contact rating | Low |
| Aeromotive Phantom 340 spec | `V-040` — future part | Low |

## Size note

The wiring diagram, the PMU manual, the STEP model and the TE catalogue are
together ~85 MB. They are tracked in git today; if the repository ever gets a
remote, move them to Git LFS (`.gitignore` has the command).

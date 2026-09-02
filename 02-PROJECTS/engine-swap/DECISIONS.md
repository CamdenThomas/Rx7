# DECISIONS — engine swap

Decisions that already shape this project, inherited from the electrical build on 2026-09-02 (D-213). Full reasoning: `../../99-ARCHIVE/Electrical/2026-09-02_electrical-pmu/05-PROCESS/DECISIONS-chronological.md`. New decisions for this project continue from D-400.

## What the electrical build reserves for the swap

**D-007 — O13 and O14 (25 A) are reserved for the swap engine's ECU/injectors and cooling fan**, wired to the engine leg and capped at the bulkhead (L1-P 2, L1-P 3). Three 16 AWG sensor spares (L1-S2 4–6) and the CAN2 drop (L1-S1 9/10, with the bus's far-end 120 Ω terminator across it) are capped in the same place.

**D-211(d) — The engine leg (L1) is built to be cut off at the firewall grommet and rebuilt from scratch at the swap.** It carries only what the 12A on the mounts needs today — no stubs to nothing, no connectors marking where something used to be. The reservations above are the only exceptions. Everything else about the new engine's wiring — ECU, sensors, fans, a PMU-driven A/C clutch and pressure transducer — is designed here, around whatever the engine is.

**D-211 — The 12A's A/C system comes out and cooling returns with the new engine.** The compressor, bracket, condenser and hoses are boxed and kept (FB A/C hardware is scarce). The new system is a new compressor on the new engine, a PMU-driven clutch and a pressure transducer — not the 1982 relay chain.

**D-091 — The main feed is 2 AWG, sized for the swap engine, not the 12A**, so the tunnel is never pulled a second time.

**D-183 — The PMU's fuel-pump and start-relay rules gain their rpm terms once an ECU puts rpm on CAN2** (0x200). The interim rules (key RUN / key START + inhibitor) run until then.

**D-187 — The automatic's inhibitor switch is read on A4 (P/N, crank interlock) and A5 (R, reverse lamps) through the engine leg (L1-S1 11, L1-S2 7).** Both disappear with the automatic; the transmission that replaces it needs its own P/N and reverse signals into the same two ladder states.

**D-173 — The fuel-pump soft fuse (4.0 A, set for the Carter P4070) is re-set from the in-tank pump's spec at the swap.**

**D-113 — The rear disc conversion and the rear axle are still planned.** The July 2026 drum overhaul was an interim so the car could be driven; the intent is a thoroughly sorted rear axle and engine that then last.

## Earlier research that still stands

The swap planning that preceded the harness work — LS (LM7 / 5.3 junkyard path with a CD009) against 13B-REW and Ecotec LE5, junkyard sourcing near Fort Collins, the Aeromotive Phantom 340 in-tank pump as the permanent fuel solution — is recorded in the car-level files under `00-CAR/` and the chat history; nothing in it was decided as a `D-` entry. This project starts with those as the working assumptions.

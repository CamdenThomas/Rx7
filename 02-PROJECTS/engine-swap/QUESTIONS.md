# QUESTIONS — engine swap

Everything open in this project, easiest first. Inherited IDs keep their numbers; new ones start at Q-400.

**V-040 · Aeromotive Phantom 340 draw at target pressure.** Sets the fuel-pump soft fuse when the in-tank pump replaces the Carter P4070 (D-173). From the Aeromotive spec; nothing to do until the pump is chosen.

**ANSWER:**
>

**Q-400 · What switches the A/C clutch — the DCU, or a PMU output that does not exist?** *(new, 2026-09-07)*
D-211 said "a PMU-driven clutch and a pressure transducer", but every one of the PMU's 22 outputs is allocated (O13 / O14 are the swap's ECU and fan). **Recommend:** the clutch is a comfort load — a relay whose coil the DCU switches (one of its seven comfort FETs, luxury `V-083`), contact fed from the luxury package's O15 block, the pressure transducer into a DCU input, the A/C toggle already drawn on the panel (luxury D-210). No PMU output, no harness change; the clutch feed runs from the O15 block to the engine leg at the swap. Flip it only if you want the clutch independent of the DCU — then it needs a relay socket at the dash node (K3 / K4 are empty) and a panel switch on a spare ladder state.

**ANSWER:**
>

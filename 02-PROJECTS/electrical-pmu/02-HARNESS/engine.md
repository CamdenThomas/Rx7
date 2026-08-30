# LEG 1 — ENGINE

*Rev 2026-08-30 · owns: what is in the engine leg and why. Cavities are [`PIN-MAP.md`](PIN-MAP.md)'s; draw figures are [`../01-DESIGN/LOADS.md`](../01-DESIGN/LOADS.md)'s.*

**Boundary:** firewall grommet. Comes out for engine service or an engine swap.
**Ground:** local star node on the block. Nothing returns through the firewall.
**Housings:** L1-P (DTP-4) · L1-S1, L1-S2 (DT-12 ×2). Diagram: `diagrams/L1-engine.svg`.

---

## Devices kept

| Device | OEM ref | Direction | Goes to | Note |
|---|---|---|---|---|
| Ignition coils (T, L) + igniters | B-18 … B-21 | Out | O12 via L1-P 1 | Twin-coil rotary. Refreshed Aug 2025 (M-005) |
| Start relay K9 coil | — | Out | O21 via L1-S1 1 | Relay on the **inner fender / firewall** (D-148), not at the starter |
| Alternator sense | A-08 | In | ICU via L1-S1 2 | Lamp-driven excitation — a divider at the ICU, not a clean digital signal |
| Water temp sender | C-02 | In | ICU via L1-S1 3 | D-083. New sender sourced, not fitted |
| Oil pressure sender | C-09 | In | ICU via L1-S1 4 | Not yet sourced |
| Oil temperature sender | new | In | ICU via L1-S1 5 | Not yet sourced |
| **Tach pickup** | B-19 YG | In | ICU via L1-S1 6, **shielded** | Coil primary pulse, >12 V spikes — opto or comparator at the ICU (D-082) |
| VSS | new | In | ICU via L1-S1 7 | Not yet sourced |
| Brake fluid level | C-05 | In | ICU via L1-S2 1 | Keep — safety (`A-010`) |
| Inhibitor switch (A/T) | A-06 | In | L1-S1 11 — **no PMU pin yet** | Crank interlock + reverse. `Q-063` |
| Coolant level, oil level sensors | C-08, C-06 | In | L1-S2 2–3, capped | Optional; no ICU cavity (`A-010`) |
| Wideband O2 | K-001 | In | L1-S1 12, capped | Tap location unknown |

## Devices deleted

Emission control unit (B-01) and its entire solenoid tree — relief valve (B-02),
throttle sensor (B-03), shutter valve (B-04), check connector (B-05), air-con
solenoid (B-07), switching solenoid (B-08), vacuum control (B-10), water temp
switches (B-11, B-12), heat hazard sensor (B-13). All served the factory
carburetor, replaced by the Weber (M-001).

Choke switch & magnet (B-14), choke and check relay (B-15), carburetor heater
(B-16), air vent valve (B-17), hot start relay/motor (A-03, A-04), sub-zero
motor/sensor (A-05, A-07). All carb-era. **Confirmed: zero remain post-Weber
(D-097).**

Back-up light switch (F-01) — M/T only, car is A/T.

## A/C — kept, untouched (D-012)

No.1 A/C relay (G-18), magnet clutch (G-19), refrigerant pressure switch (G-21),
frost warning temp switch (G-22), diode (G-23). The whole safety interlock chain
stays on the factory switch, fed from busbar F4. It does not enter the PMU and
does not enter this leg's connector count — it is a self-contained factory
sub-harness. K10 is the factory clutch relay.

## Reserved — LS swap (D-007)

| Reservation | Where | Note |
|---|---|---|
| LS ECU + injectors, ~18 A | O13 → L1-P 2, capped | |
| LS cooling fan(s), ~25 A | O14 → L1-P 3, capped | |
| CAN2 drop for the LS ECU | L1-S1 9/10 | Twisted pair, run now. **120 Ω terminator fitted at this end, capped** (D-079) |
| Sensor spares ×3 | L1-S2 4–6, capped | Knock, cam/crank, +1 |

## Leg totals

| | Value |
|---|---|
| Heavy conductors (12 AWG) | 3 used + 1 spare |
| Signal conductors | L1-S1 11 used of 12 · L1-S2 4 used of 12 |
| CAN | 1 twisted pair, terminated at the engine-bay end |
| Est. peak draw, current engine | ~8 A |
| Est. peak draw, post-LS | ~30 A |
| Ground | Local block star node |

## Why this leg is shaped the way it is

**This leg shrinks dramatically.** Eighteen carb-era devices delete. What
remains is ignition, the ICU's six sensors, two interlocks and reserved
capacity — a fraction of the factory bundle.

**The tach signal is the one hazard in here.** It shares L1-S1 with the CAN
pair and the +5 V reference — all low-level, which is correct — and is
deliberately *not* in L1-P alongside the coil feed and the LS fan reservation.
Run it shielded with the shield grounded at the box end only.

**The sensor wires pass straight through the dash post to DP-ICU.** The PMU
never sees them — it has no spare analog input (D-076). The box that draws the
gauge reads the sender (D-083).

**Nothing returns through the firewall.** The block star node handles every
ground in this leg, which is the structural fix for K-008's class of fault.

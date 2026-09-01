# LEG 1 — ENGINE

*Rev 2026-09-01 · owns: what is in the engine leg and why. Cavities are [`PIN-MAP.md`](PIN-MAP.md)'s; draw figures are [`../01-DESIGN/LOADS.md`](../01-DESIGN/LOADS.md)'s.*

**Boundary:** firewall grommet. Comes out for engine service or an engine swap.
**Ground:** local star node on the block. Nothing returns through the firewall.
**Housings:** L1-P (DTP-4) · L1-S1, L1-S2 (DT-12 ×2). Diagram: `diagrams/L1-engine.svg`.

---

## Devices kept

| Device | OEM ref | Direction | Goes to | Note |
|---|---|---|---|---|
| Ignition coils (T, L) + igniters | B-18 … B-21 | Out | O12 via L1-P 1 | Twin-coil rotary. Refreshed Aug 2025 (M-005) |
| Start relay K9 coil | — | Out | O21 via L1-S1 1 | Relay on the **inner fender / firewall** (D-148), not at the starter |
| Alternator BW excitation | A-08 | Out | O12 → F15 → L1-S1 2 | Factory-spec field feed (D-198) — without it the alternator never charges |
| Alternator WB charge-sense | A-08 | In | L1-S2 8 → DP-ICU 11, capped until Phase 9 | DEFERRED (D-198); PMU voltage telemetry is the interim charge indicator |
| Water temp sender | C-02 | In | ICU via L1-S1 3 | D-083. New sender sourced, not fitted |
| Oil pressure sender | C-09 | In | ICU via L1-S1 4 | Not yet sourced |
| Oil temperature sender | new | In | ICU via L1-S1 5 | Not yet sourced |
| **Tach pickup** | B-19 YG | In | ICU via L1-S1 6, **shielded** | Coil primary pulse, >12 V spikes — opto or comparator at the ICU (D-082) |
| VSS | new | In | ICU via L1-S1 7 | Not yet sourced |
| Brake fluid level | C-05 | In | ICU via L1-S2 1 | Keep — safety (`A-010`) |
| Inhibitor switch (A/T) | A-06 | In | P/N → A4 node via L1-S1 11 · R → A5 node via L1-S2 7 | Crank interlock + reverse lamps (`Q-063` → D-182, D-187) |
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

**The entire A/C interlock chain** — No.1 A/C relay (G-18), magnet clutch
(G-19), refrigerant pressure switch (G-21), frost warning temp switch (G-22),
diode (G-23) — deleted with the compressor (D-211). See the section below.

## A/C — removed entirely (D-211, supersedes D-012)

**The whole cooling system leaves the car and nothing is left behind for it.**
Compressor, bracket, belt, condenser, receiver/drier and lines come out; the
factory interlock chain goes with them — No.1 A/C relay (G-18), magnet clutch
(G-19), refrigerant pressure switch (G-21), frost warning temp switch (G-22),
diode (G-23) and the dash A/C switch. Panel side: **F4 and K10 are deleted**
([`../01-DESIGN/SPEC.md`](../01-DESIGN/SPEC.md) §3).

**Heat and ventilation are untouched.** Blower motor, heater core, HVAC case,
ducts and blend doors all stay — O16 → L3-P 1 and the comfort bus are exactly
as they were. The car loses cooling and nothing else.

**No stub is left in this leg.** That is deliberate and it is the rule that
makes L1 different from every other leg: hidden interior conductors are run and
capped for deferred features (D-208(f)), and the engine bay is the one place
that is not worth it. L1 carries only what the engine currently on the mounts
needs — no connector to nothing, no cap marking where something used to be.
When a compressor returns with the swap engine, **this leg is rebuilt from
scratch** around whatever that system actually is: a PMU-driven clutch output
and a pressure transducer into the DCU, not a 1982 relay chain. The boundary at
the firewall grommet is what makes that cheap.

Physical removal is `T-054` — **the refrigerant is recovered by a shop first**
(K-015 says the system still cools, so it still holds charge; venting it is
illegal). Hardware is boxed and kept, not scrapped.

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
| Signal conductors | L1-S1 11 used of 12 · L1-S2 6 allocated of 12 |
| CAN | 1 twisted pair, terminated at the engine-bay end |
| Est. peak draw, current engine | ~8 A |
| Est. peak draw, post-LS | ~30 A |
| Ground | Local block star node |

## Why this leg is shaped the way it is

**This leg shrinks dramatically.** Eighteen carb-era devices delete, plus the
five-device A/C interlock chain (D-211). What remains is ignition, the ICU's six
sensors, two interlocks and reserved capacity — a fraction of the factory bundle.

**This leg is the one place capped spares are not free.** Everywhere else in
the car a run-and-cap conductor is hidden, out of the way, and cheaper now than
a re-pin later. In the engine bay it is visible clutter on a bay that is meant
to read clean, and it is guaranteed to be wrong: the swap engine's sensors,
coils, injectors and accessories will not match the stubs left for them. So the
only capped cavities in L1 are the LS reservations below, which exist
because L1-P and L1-S2 are terminated once (D-004) and the LS is a known
quantity — everything else in this leg is live or absent (D-211).

**The tach signal is the one hazard in here.** It shares L1-S1 with the CAN
pair and the +5 V reference — all low-level, which is correct — and is
deliberately *not* in L1-P alongside the coil feed and the LS fan reservation.
Run it shielded with the shield grounded at the box end only.

**The sensor wires pass straight through the dash post to DP-ICU.** The PMU
never sees them — it has no spare analog input (D-076). The box that draws the
gauge reads the sender (D-083).

**Nothing returns through the firewall.** The block star node handles every
ground in this leg, which is the structural fix for K-008's class of fault.

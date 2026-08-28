# LEG 1 — ENGINE

**Boundary:** firewall grommet. Comes out for engine service or an engine swap.
**Ground:** local star node on the block. Nothing returns through the firewall.

---

## Devices kept

| Device                   | OEM ref | Direction | Est. A       | Signal type                          | Notes                             |
|--------------------------|---------|-----------|--------------|--------------------------------------|-----------------------------------|
| Ignition coil (T)        | B-18    | Out       | 2–3          | Power                                | Twin-coil rotary                  |
| Ignition coil (L)        | B-19    | Out       | 2–3          | Power                                |                                   |
| Igniter (T)              | B-20    | Out       | incl. above  | Power                                |                                   |
| Igniter (L)              | B-21    | Out       | incl. above  | Power                                |                                   |
| Start relay coil         | —       | Out       | 0.15–0.2     | Low-current out                      | Relay mounts **at the starter**   |
| Alternator sense         | A-08    | In        | <0.5         | Lamp-driven excitation               | Not a clean digital signal        |
| Water temp sender        | C-02    | In        | —            | Resistive                            | To cluster now, PMU later         |
| Oil pressure sender      | C-09    | In        | —            | Resistive                            | To cluster now, PMU later         |
| Coolant level sensor     | C-08    | In        | —            | Closure                              | Optional                          |
| Oil level sensor         | C-06    | In        | —            | Closure                              | Optional                          |
| Brake fluid level sensor | C-05    | In        | —            | Closure                              | Keep — safety                     |
| Inhibitor switch (A/T)   | A-06    | In        | —            | Closure                              | Crank interlock + reverse trigger |
| Wideband O2              | K-001   | In        | 1–2 (heater) | 0–5 V analog                         | Location unknown                  |
| **Tach pickup**          | B-18 YG | In        | —            | **Coil primary pulse, >12 V spikes** | Needs conditioning — V-041        |

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
stays on the factory switch. It does not enter the PMU and does not enter this
leg's connector count — it is a self-contained factory sub-harness.

## Reserved — LS swap

| Reservation          | Est. A | Notes                               |
|----------------------|--------|-------------------------------------|
| LS ECU + injectors   | ~18    | Capped at the bulkhead              |
| LS cooling fan(s)    | ~25    | Capped                              |
| CAN2 drop for LS ECU | —      | Twisted pair, run now               |
| Sensor spares ×6     | —      | VSS, knock, cam/crank, wideband, +2 |

## Leg totals

|                                | Value                 |
|--------------------------------|-----------------------|
| Heavy conductors (12 AWG)      | 3 kept + 1 spare      |
| Signal conductors              | 10 kept + 6 spare     |
| CAN                            | 1 twisted pair        |
| Est. peak draw, current engine | ~8 A                  |
| Est. peak draw, post-LS        | ~30 A                 |
| Ground                         | Local block star node |

## Optimization notes

**This leg shrinks dramatically.** Eighteen carb-era devices delete. What remains
is ignition, three senders, two interlocks, and reserved capacity — a fraction of
the factory bundle.

**The tach signal is the one hazard in here.** Route it away from the coil feeds
and the LS fan reservation. It is a low-level signal sharing a bundle with the
noisiest wires in the car.

**Nothing returns through the firewall.** The block star node handles every
ground in this leg, which is the structural fix for K-008's class of fault.

---

## Connectors — ENGINE leg

Two housings. Mates at the dash post via `DP-L1-P` and `DP-L1-S`.

### L1-P · DTP06-4S → DP-L1-P (DTP04-4P) · 12 AWG, size 12

| Cav | Circuit                       | Terminates at | PMU pin |
|-----|-------------------------------|---------------|---------|
| 1   | Ignition / coil feed          | O12           | 2       |
| 2   | RESERVED — LS ECU + injectors | O13           | 1       |
| 3   | RESERVED — LS cooling fan     | O14           | 14      |
| 4   | SPARE heavy                   | capped        | —       |

### L1-S · AMPSEAL 23 → DP-L1-S · 16 AWG

| Cav   | Circuit                            | Terminates at         | PMU pin |
|-------|------------------------------------|-----------------------|---------|
| 1     | Start relay coil → K9 at starter   | O21                   | 21      |
| 2     | Alternator lamp / sense            | spare                 | —       |
| 3     | Water temp sender                  | cluster now           | —       |
| 4     | Oil pressure sender                | cluster now           | —       |
| 5     | Brake fluid level                  | cluster now           | —       |
| 6     | Oil level sensor                   | cluster now           | —       |
| 7     | Coolant level sensor               | cluster now           | —       |
| 8     | Inhibitor switch — crank interlock | A9–A16 bank `[Q-019]` | —       |
| 9     | Wideband O2 signal                 | capped                | —       |
| 10    | **Tach pickup (YG)** — shielded    | capped                | —       |
| 11    | +5 V reference                     | +5V out               | 15      |
| 12    | CAN2 H                             | CAN2H                 | 24      |
| 13    | CAN2 L                             | CAN2L                 | 37      |
| 14–16 | LS sensor spares ×3                | capped                | —       |
| 17–23 | SPARE ×7                           | capped                | —       |

**Routing note:** the tach pickup (L1-S cav 10) shares a housing with the CAN
pair and the +5 V reference — all low-level, which is correct. It is deliberately
*not* in L1-P alongside the coil feed and the LS fan reservation. Run it shielded
with the shield grounded at the box end only.

**Ground:** block star node, local. No ground conductor crosses the firewall in
either housing.

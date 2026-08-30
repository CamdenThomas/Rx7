# Circuit — Blower, A/C, Defroster, Audio, Power Antenna

*Rev 2026-08-30 · owns: the factory decode of this circuit — devices, wires, logic. The rebuild table at the foot points into the new design and is not its owner; cavities are `02-HARNESS/data/connectors.csv`'s.*

**Source:** Section G, page 24.

---

## 1 · Blower & heater

| Ref  | Device                  | Pins                |
|------|-------------------------|---------------------|
| G-14 | Blower motor & resistor | LO, LR / LY, LW     |
| G-15 | Blower motor switch     | LW, LY / LG, LR, LB |

| Item          | Value                                                             |
|---------------|-------------------------------------------------------------------|
| Feed          | Ignition **IG** → L bus → X-04 **20 A** → LO                      |
| Speed control | **Resistor pack** with MI / HI / LO / OFF positions on the switch |
| Ground        | X-15                                                              |

**Confirms A-002** (A-002 → confirmed here) — factory resistor pack sets speed. The PMU supplies the feed
on O16 and the existing switch/resistor stack does the rest.

## 2 · Air conditioning

| Ref  | Device                      | Pins            |
|------|-----------------------------|-----------------|
| G-18 | No.1 A/C relay              | LB, LR / YL, BW |
| G-19 | Magnet clutch               | BW              |
| G-21 | Refrigerant pressure switch | YL, YR          |
| G-22 | Frost warning temp switch   | LG, YR          |
| G-23 | Diode (in the A/C harness)  | LB, YL          |

Chain: A/C switch → frost switch → pressure switch → No.1 A/C relay → magnet
clutch. There is also a No.2 A/C relay in Section B that talks to the emission
control unit for idle-up.

**D-012 keeps all of this on the factory switch**, off the PMU. The safety
interlock chain (pressure + frost) stays exactly as built.

## 3 · Rear window defroster

| Ref  | Device           | Pins  |
|------|------------------|-------|
| G-24 | Defroster switch | Y, LG |
| G-25 | Defroster grid   | LG, B |

| Item      | Value                               |
|-----------|-------------------------------------|
| Feed      | Ignition **IG** → X-04 **15 A** → Y |
| Indicator | 3.4 W in the switch                 |
| Ground    | X-13 / X-15                         |

No timer in the factory circuit — it's on until switched off. The PMU should add
a shutoff timer (Checklist 2.18 puts the switch on the keypad).

## 4 · Audio & power antenna

| Ref     | Device              | Pins                     |
|---------|---------------------|--------------------------|
| G-03    | Stereo              | LR, LgW, RG              |
| G-04    | Radio               | LW, LR, LgW / LG, LY, RG |
| G-08    | Main amp            | LO, LB, LR, LW, L        |
| G-01    | Power antenna relay | LR, R, LY, B / LG, L     |
| G-02    | Power antenna motor | L, LY, R                 |
| G-05/06 | Front speakers      | LG/LW, LY/LR             |
| G-09/10 | Rear speakers       | LR/LO, LW/LB             |

| Item         | Value                  |
|--------------|------------------------|
| Feed         | X-04 **20 A** → LR     |
| Illumination | RG from the dimmer bus |

## 5 · What this means for the rebuild

| Factory | PMU-24 plan |
|---|---|
| 20 A blower feed + resistor pack | O16 (25 A, flyback diode) → **L3-P 1**; the DCU drives the servos, the resistor pack stays. Motor is **dead** (K-023) — O16 sized from the replacement (D-126) |
| A/C relay chain and magnet clutch | Untouched, factory switch, K10 (D-012). Barely cool — K-015 |
| 15 A defroster, no timer | O4 → **L4-P 1**, plus a software shutoff timer |
| Defroster switch | Broken (K-020); moves to the CAN keypad (Checklist 2.18) |
| 20 A audio feed | O10 accessory bus (**L3-M 1**) + a **separate constant** off the busbar via K11/F1 (**L3-M 2**, D-020) |
| Power antenna relay + motor | Gone (V-031 → D-097) |
| Speaker wiring | Not a PMU concern; [`HEAD-UNIT.md`](../../02-PROJECTS/electrical-pmu/04-SUBSYSTEMS/HEAD-UNIT.md) |

## 6 · Unknowns

| ID | Unknown | Resolve by |
|---|---|---|
| V-031 → D-097 | Power antenna | Gone |
| V-032 → D-099 | A/C system | Barely cool, probably low on charge — not electrical |
| V-023 → D-097 | Cruise control unit | Gone |

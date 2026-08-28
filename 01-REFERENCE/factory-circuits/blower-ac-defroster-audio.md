# Circuit — Blower, A/C, Defroster, Audio, Power Antenna

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

**Confirms A-002** — factory resistor pack sets speed. The PMU supplies the feed
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
a shutoff timer (Checklist 057).

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

| Factory                           | PMU-24 plan                                                        |
|-----------------------------------|--------------------------------------------------------------------|
| 20 A blower feed + resistor pack  | O16 (25 A, flyback diode), factory switch retained                 |
| A/C relay chain and magnet clutch | Untouched, factory switch (D-012)                                  |
| 15 A defroster, no timer          | O4, plus a software shutoff timer                                  |
| Defroster switch                  | CAN keypad (Checklist 057)                                         |
| 20 A audio feed                   | O10 accessory bus + a **separate constant** off the busbar (D-020) |
| Power antenna relay + motor       | **Not in SPEC** — `[V-031]`                                        |
| Speaker wiring                    | Not a PMU concern; runs independently                              |

## 6 · Unknowns

| ID    | Unknown                                                   | Resolve by          |
|-------|-----------------------------------------------------------|---------------------|
| V-031 | Power antenna still fitted / wanted? No channel allocated | Inspect car, decide |
| V-032 | Is the A/C system still charged and functional?           | Inspect car         |
| V-023 | Cruise control unit still present?                        | Inspect car         |

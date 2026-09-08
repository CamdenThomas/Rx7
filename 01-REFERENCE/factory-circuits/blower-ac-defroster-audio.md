# Circuit — Blower, A/C, Defroster, Audio, Power Antenna

*Rev 2026-09-07 · owns: the factory decode of this circuit — devices, wires, logic. Nothing of the new design lives here; the last section says where it does.*

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
a shutoff timer (the trigger is the luxury package's panel key — electrical D-210(b), luxury FT16).

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

The rebuild's side of every device and wire above is the electrical build's record, not this file's: find a factory code in its data — `python tools/rx7.py -p electrical-build find "C-02"` — or read the rendered [`DESIGN.md`](../../02-PROJECTS/electrical-build/01-DESIGN/DESIGN.md) §12 (device ends) and [`WIRE-TABLES.md`](../../02-PROJECTS/electrical-build/03-INSTALL/WIRE-TABLES.md). A hand-copied mapping table stood here until 2026-09-07; it had drifted three decisions behind and was removed — one fact, one home. Decisions that shaped this circuit's rebuild: D-012 · D-020 · D-097 · D-126.

## 6 · Unknowns

Every unknown this decode raised has an ID. The open ones live in the projects' `QUESTIONS.md` files (electrical, luxury, engine swap); the closed ones are cited with their closer in the projects' `DECISIONS.md`. This circuit's: V-023 · V-031 · V-032.

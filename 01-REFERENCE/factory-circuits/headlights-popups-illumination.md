# Circuit — Headlights, Pop-ups, Illumination

**Source:** Section E, page 20. The most complex sheet in the book.

---

## 1 · Devices

| Ref  | Device                                      | Pins                       |
|------|---------------------------------------------|----------------------------|
| E-01 | Combination switch — LIGHT, DIMMER, PASSING | R, WG / RL, RY, RG, RW, GL |
| E-02 | Retractable headlight switch                | RW, WG, LY / RY, R, B      |
| E-03 | Retractable headlight motor LH              | WR, YG, R, RY              |
| E-04 | Retractable headlight motor RH              | WR, YG, R, RY              |
| E-05 | Instrument panel light control (dimmer)     | RL, RG, B                  |
| E-08 | Headlight LH                                | RY, RL, B                  |
| E-09 | Headlight RH                                | RY, RL, B                  |
| E-11 | Headlight cleaner motor                     | R, LY                      |

## 2 · Headlight feed

| Item                | Value                                                                       |
|---------------------|-----------------------------------------------------------------------------|
| Fusible links       | **0.3 sq ×2** plus the 1.25 sq main — headlights get their own links        |
| Bulbs               | Sealed beam **50 W / 40 W** (halogen option 60/50 W)                        |
| Low beam            | **RL**                                                                      |
| High beam           | **RY**                                                                      |
| Switch              | E-01 LIGHT section (OFF/PARK/HEAD) feeds DIMMER section                     |
| Passing             | Separate DIMMER contact — flash-to-pass works independent of LIGHT position |
| High beam indicator | 3.4 W on RY                                                                 |
| Ground              | B → X-13 (LH) / X-14 (RH)                                                   |

Headlights are fed from fusible links, **not** from the 10 A fuse that runs the
parking/tail circuit. Two independent protection paths.

## 3 · Pop-up motors

| Item      | Value                                                                    |
|-----------|--------------------------------------------------------------------------|
| Motors    | E-03 (LH), E-04 (RH) — each has **4 wires**: WR, YG, R, RY               |
| Drive     | Reversible. UP and DOWN limit contacts are **inside the motor assembly** |
| Control   | E-02 retractable headlight switch, separate from the light switch        |
| Indicator | 3.4 W retractor indicator light on YG                                    |
| Feed      | WR constant + R from the light switch                                    |

**Confirms A-003** — each side needs two motor legs forward, so four heavy
conductors to the nose. The limit switches are internal to the motor, which
means the position ladder on A4/A5 has to pick up those internal contacts.

## 4 · Illumination bus

E-05 instrument panel light control is a **rheostat dimmer**. It takes RG in and
outputs **RL** to every illuminated item:

| Item               | W   |
|--------------------|-----|
| Meter              | 3.4 |
| Heater panel       | 1.4 |
| Select lever (A/T) | 3.4 |
| Switch panel       | 3.4 |
| Cigarette lighter  | 3.4 |
| Radio              | 3.4 |
| Stereo             | 1.4 |

Ground B → X-13.

## 5 · What this means for the rebuild

| Factory                        | PMU-24 plan                                                           |
|--------------------------------|-----------------------------------------------------------------------|
| Sealed beam 50/40 W on RL / RY | O2 low / O3 high, 12 AWG to C2-A1 / C2-A2                             |
| Dimmer rheostat E-05           | Deleted — O20 PWM drives illumination (SPEC C3-14)                    |
| E-01 LIGHT + DIMMER + PASSING  | A15 ladder. **Passing/flash-to-pass needs software logic, not a pin** |
| E-02 pop-up switch             | C3-12 / C3-13 raise/lower commands to the relay bank                  |
| Motor internal limit contacts  | A4 / A5 position ladders via C2-B5 / C2-B6                            |
| 4-wire motors                  | C2-A3…A6, H-bridge relays on the panel                                |
| Headlight cleaner E-11         | **Not in SPEC** — `[V-029]` almost certainly already gone             |
| Separate 0.3 sq fusible links  | Soft fuses on O2 / O3                                                 |

## 6 · Unknowns

| ID    | Unknown                                                                              | Resolve by                          |
|-------|--------------------------------------------------------------------------------------|-------------------------------------|
| V-029 | Is the headlight cleaner system still fitted?                                        | Inspect car — rare, usually deleted |
| V-030 | Pop-up motor internal limit contact pinout — which of WR/YG/R/RY are limits vs drive | Continuity test the motor, T-003    |
| Q-020 | Flash-to-pass: software function off the A15 ladder, or its own input?               | Decide with Q-018/Q-019             |

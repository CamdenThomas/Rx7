# Circuit — Headlights, Pop-ups, Illumination

*Rev 2026-08-30 · owns: the factory decode of this circuit — devices, wires, logic. The rebuild table at the foot points into the new design and is not its owner; cavities are `02-HARNESS/data/connectors.csv`'s.*

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
| Drive     | Sheet reads as reversible (R and RY commands), but **Camden observed the motor spinning one direction only** (D-186) — the D-199 ohm check at E-03 settles it |
| Control   | E-02 retractable headlight switch, separate from the light switch        |
| Indicator | 3.4 W retractor indicator light on YG                                    |
| Feed      | WR constant + R from the light switch                                    |

**Confirms A-003** (A-003 → confirmed here) — each side needs two motor legs forward, so four heavy
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

| Factory | PMU-24 plan |
|---|---|
| Sealed beam 50/40 W on RL / RY | O2 low → **L2-P1 1**, O3 high → **L2-P1 2**, 12 AWG. What is fitted today is `V-066` |
| Dimmer rheostat E-05 | Deleted — O20 PWM drives illumination (**L3-S1 8**); the ICU backlight tracks it on DP-ICU 5 |
| E-01 LIGHT + DIMMER + PASSING | A15 ladder (**L3-S1 2**). Dimmer HIGH/LOW and PASS were put "in software" (Q-020 → D-051) — how they reach A15 is `Q-065` → D-184 |
| E-02 pop-up switch | **Deleted** (D-038) — broken anyway (K-021). Pop-ups raise on HEAD from the A15 ladder; wink switches **L3-S1 9/10** are the only manual control |
| Motor internal limit contacts | A4 / A5 transit + inhibitor ladders via **L2-S 1 / 2** (D-187) |
| 4-wire motors | Run feed **L2-P1 3** (LH) / **L2-P2 1** (RH) from K1/K2 (D-186); conductor ID per the D-199 check (R + RY bridged if single-direction confirms); F6/F7 branches |
| Headlight cleaner E-11 | Gone (V-029 → D-097) |
| Separate 0.3 sq fusible links | Soft fuses on O2 / O3 |

## 6 · Unknowns

| ID | Unknown | Resolve by |
|---|---|---|
| V-029 → D-097 | Headlight cleaner | Gone |
| V-030 → D-177 | Pop-up motor pinout — read off sheet E: YG top · WR left · RY right · R bottom; YG = indicator / position line; assembly grounds locally, not through the connector | Closed off the diagram; limit contacts confirmed at commissioning |
| Q-020 → D-051 / `Q-065` → D-184 | Flash-to-pass | Software off A15; the ladder states are the `Q-065` → D-184 packet |
| V-066 | Round or rectangular sealed beams, and whether LED housings are fitted today | Look — `05-PROCESS/OPEN.md` §8, `T-035` |

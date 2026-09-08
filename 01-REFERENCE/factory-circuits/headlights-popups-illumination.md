# Circuit — Headlights, Pop-ups, Illumination

*Rev 2026-09-07 · owns: the factory decode of this circuit — devices, wires, logic. Nothing of the new design lives here; the last section says where it does.*

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

The rebuild's side of every device and wire above is the electrical build's record, not this file's: find a factory code in its data — `python tools/rx7.py -p electrical-build find "C-02"` — or read the rendered [`DESIGN.md`](../../02-PROJECTS/electrical-build/01-DESIGN/DESIGN.md) §12 (device ends) and [`WIRE-TABLES.md`](../../02-PROJECTS/electrical-build/03-INSTALL/WIRE-TABLES.md). A hand-copied mapping table stood here until 2026-09-07; it had drifted three decisions behind and was removed — one fact, one home. Decisions that shaped this circuit's rebuild: D-038 · D-051 · D-097 · D-184 · D-186 · D-187 · D-199.

## 6 · Unknowns

Every unknown this decode raised has an ID. The open ones live in the projects' `QUESTIONS.md` files (electrical, luxury, engine swap); the closed ones are cited with their closer in the projects' `DECISIONS.md`. This circuit's: Q-020 · Q-065 · T-035 · V-029 · V-030 · V-066.

# LOADS — estimated current draw and signal types

*Rev 2026-08-31 · owns: the estimation method, the design (worst-case) draw per circuit, and the signal type of every input. Measured figures live in [`CHANNEL-SCHEDULE.md`](CHANNEL-SCHEDULE.md), not here.*

**Every number here is an estimate.** Nothing in this file may be used to set
a soft fuse — that comes from measurement ([`CHANNEL-SCHEDULE.md`](CHANNEL-SCHEDULE.md), D-164).
These exist so wire gauge, connector class and relay sizing can be decided
before the meter session.

**Baseline is stock incandescent bulbs** (D-124). The LED figures are kept in
the appendix for the deferred lighting second pass (D-122, D-201); they are
not this build's design values.

## Contents

1. Method · 2. Lighting — design figures · 3. Motors · 4. Heating and the
comfort bus · 5. Engine and fuel · 6. Accessory bus · 7. Modules ·
8. Sleeping draw · 9. Input signal types · 10. Signals that are not simple
switches · Appendix A — LED figures for the lighting project

---

## 1 · Method — best evidence first

**1 · Factory wattage (highest confidence).** The Section E/F sheets print bulb
wattages directly. A = W ÷ 13.8 V (running voltage, not 12 V).

**2 · Factory fuse size (high confidence).** A designed circuit is fused roughly
40–60 % above its steady load. A 15 A fuse implies ~7–10 A steady. This is the
single most useful inference available without a meter.

**3 · Published figures for the part class (medium).**

**4 · Motor multipliers (design rule).** Motors are the trap: a lugging motor
draws roughly seven times its running current and a stalled motor as much as
ten — a 2 A motor may pull 16 A lugging and 30 A stalled. Wire and connectors
are sized for stall, not running.

**Confidence key:** `A` factory-printed · `B` fuse-inferred · `C` published
class figure · `D` engineering estimate · `M` measured (see the schedule).

## 2 · Lighting — design figures, filament bulbs

| Circuit | Ch | Bulbs | Design A | Rating | Headroom | Conf |
|---|---|---|---|---|---|---|
| Headlight LOW | O2 | LED housings as stated — `V-066` confirms | 3.0 | 25 A | — | D |
| Headlight HIGH | O3 | same | 3.5 | 25 A | — | D |
| Tail / park / marker / plate | O6 | 8 W ×2 + 8 W ×2 + 3.8 W ×4 + 6 W ×2 | **4.4** | 15 A | 71 % | A |
| Brake | O7 | 27 W ×2 | 3.9 est · **7.0 M** | 15 A | 53 % | M |
| Turn, per side | O17 / O18 | 27 W ×2 + 3.4 W indicator | 4.2 est · **3.4 M** | 7 A | 51 % | M |
| Reverse | O19 | 27 W ×2 | **3.9** | 7 A | 44 % | A |
| Interior + glovebox + luggage + illumination | O20 | 5 + 3.4 + 5 W + 3.4/1.4 W ×7 | **2.5** | 7 A | 64 % | A |

The brake circuit measured nearly double its estimate — worth confirming the
bulbs are 27/8 W and not something larger, but the 15 A channel has headroom
either way.

**Inrush is the number that matters on filament.** A cold filament draws
8–12× steady for a few milliseconds; every lamp channel needs an inrush window
configured (D-120), and turn signals are the case to get right because they
cycle constantly. Windows are in [`CHANNEL-SCHEDULE.md`](CHANNEL-SCHEDULE.md).

Wire gauge is unchanged by any of this — D-016 sets it by voltage drop over
the run and by crimp robustness, not by ampacity.

## 3 · Motors — sized for stall, not for running

| Load | Ch | Factory fuse | Running A | Stall A | Conf |
|---|---|---|---|---|---|
| Front wiper LOW | O8 | 10 A | 3–5 | 12–20 | C |
| Front wiper HIGH | O9 | 10 A (shared) | 5–6 | 12–20 | C |
| Blower | O16 | 20 A | motor is **DEAD** (K-023) — size from the replacement's spec (D-126) | | — |
| Pop-up motor, each | O1 via K1–K4 | — | 4–6 | 15–25 | D |
| Pop-up, both together | O1 | — | 8–12 | 25–50 | D |
| Washer pump | `Q-063` → D-182 | — | 3–5 | 8 | D |
| Window motors | K5–K8, **provisioned** | 30 A | 4–6 each | 10–15 each | C — measure when fitted |

**O1 motor bus worst case (D-133):** two pop-ups moving = 8–12 A steady,
25–50 A transient. The 25 A channel handles the steady load; the integrated
flyback diode and the PMU's inrush tolerance handle the transient. When
windows arrive, never run both pop-ups and both windows simultaneously
(interlock in [`PMU-CONFIG.md`](PMU-CONFIG.md)) and raise O1's limit from measurement.

## 4 · Heating and the comfort bus

| Load | Ch | Factory fuse | Est. A | Conf |
|---|---|---|---|---|
| Rear defog grid | O4 | 15 A | 10–13 **cold** | B |
| Heated seat element, each | O15 via DCU | — | 4–5 | D |
| Cooled seat fan module, each | O15 via DCU | — | 1.5–2.5 | D |
| Heated mirror, each | O15 → sill F14 | — | 1–2 | C |
| Heated washer nozzles | O15 via DCU | — | 1–2 | D |
| Wiper park de-icer | O15 via DCU | — | 2–3 | D |
| **O15 worst case, everything on** | O15 | — | **17–26 A** | D |

Published defog grid figures run 8–20 A across a commercial range; the
factory 15 A fuse caps the FB's small hatch glass at the low end. Grids draw
**more when cold** — the soft fuse needs headroom for the first 30 seconds.

O15 exceeds its 25 A channel only if everything runs at once. **The DCU
enforces the interlock downstream** (D-073) — heated and cooled seats are
mutually exclusive by definition, and the de-icer only runs when the wipers
are parked and cold. Realistic simultaneous worst case is heat + mirrors +
nozzles ≈ 14 A. F10/F11 branch fuses protect each leg. Every comfort load is
deferred ([`../02-HARNESS/CAVITY-STATE.md`](../02-HARNESS/CAVITY-STATE.md) lists them); the bus itself is built.

## 5 · Engine and fuel

| Load | Ch | Factory fuse | Est. A | Conf |
|---|---|---|---|---|
| Ignition coils + igniters (twin, 12A) | O12 | — | 4–6, rising with rpm | D |
| Fuel pump — **Carter P4070** (current) | O5 | 10 A | 1–3 (`V-054` → measured 2.38 A) | C |
| Aeromotive Phantom 340 (planned) | O5 | — | 8–12 at pressure `V-040` | D |
| Start relay coil (K9) | O21 | — | 0.15–0.2 | C |
| Horn, pair | O11 | 15 A (shared with stop) | 4–8 | B |
| Hatch / fuel-door solenoid | `Q-061` → D-180 | 20 A | 3–5 momentary | D |
| A/C magnet clutch | factory switch, K10 | — | 3–5 | C |

O5 is sized for the Aeromotive, not the Carter — size the channel for the
worst plausible replacement (the rule preserved in `99-ARCHIVE/PARTS-CHANGES.md` §7).

## 6 · Accessory bus — O10

| Load | Est. A | Conf |
|---|---|---|
| USB-C charging | 3 per port | D |
| Head unit, switched | 2–5 | B |
| DCU logic — MCU, transceiver, regulator | 0.3–0.5 | D |
| ICU logic + display backlight | 0.5–1.5 | D |
| CAN keypad | 0.1–0.3 | D |
| **Worst case, both ports loaded** | **~10 A on a 15 A channel** | |

The cigarette lighter (8–10 A while heating) is deleted (D-095) — it was the
only load that could trip the channel that powers the instruments. Head unit
clock keep-alive (10–20 mA) is on busbar F1, not O10 (D-020).

## 7 · Modules

| Load | On | Est. A |
|---|---|---|
| DCU logic | O10 | 0.3–0.5 |
| ICU logic + backlight | O10 | 0.5–1.5 |
| HVAC servos, while moving | O15 via DCU | ~1 each, 3–4 channels |
| Comfort loads | O15 via DCU | see §4 |

**HVAC servos and comfort loads are on O15, not O10.** Only module logic and
the display backlight sit on the accessory bus.

## 8 · Sleeping draw

| Source | mA |
|---|---|
| PMU standby | 150 |
| Head unit clock, when K11 is closed | 10–20 |
| DCU standby, if a keep-alive is fitted | `V-056` → D-191 |
| ICU standby | 0 — fully switched |
| **Battery heater, winter** | `V-052` |

On the Ionic's 40 Ah that is weeks, not days — but the BMS low-voltage cutoff
is usually the binding constraint, not capacity. K11 (constant-bus master)
drops the head unit keep-alive on a long park. The battery heater is the
unknown that matters in a Fort Collins winter.

## 9 · Input signal types — what each PMU input sees

| Pin | Input | Signal type | Range | Conditioning |
|---|---|---|---|---|
| A1 | Turn stalk | Resistor ladder → 0–5 V | 3 states | Ladder + internal 10 kΩ pull-up |
| A2 | Wiper stalk | Resistor ladder → 0–5 V | 5 states | Ladder + pull-up |
| A3 | Brake pedal switch | Closure via 4.7 kΩ | on/off | Switch to ground, pull-up |
| A4 | Pop-up LEFT position | Ladder from **motor-internal** limit contacts | 3 states | Ladder. Pinout by continuity test, `T-011` |
| A5 | Pop-up RIGHT position | Same | 3 states | Same |
| A6 | Door pins (+ luggage switch, `A-012`) | Ladder, 2–3 switches | 3–4 states | Factory already switches to ground |
| A7 | Fuel level sender | **Resistive**, variable | `V-037` → D-197 | Divider against +5 V ref. Needs the sender's ohm range |
| A8 | Hazard switch | Closure via 4.7 kΩ | on/off | Switch to ground; the wake source is a second pole |
| A15 | Headlight switch | Ladder, **12 V side** | 3 states (5 with dimmer/pass — `Q-065` → D-184) | 0–20 V range, plus a 100 kΩ bias from +5 V (D-167) |
| A16 | Key position | Summed ladder, **12 V side** | 4 states | Same. Values are for the *combinations* (D-055) |

Four functions have no input or output yet — inhibitor P/N/R, wiper park
sense, the washer pump and the horn switch's PMU input. See `Q-063` → D-182.

## 10 · Signals that are not simple switches

| Signal | Type | Handling |
|---|---|---|
| **Tachometer** | Coil primary pulse, **YG** from the leading coil — inductive spike well above 12 V | **ICU input**, opto or comparator conditioning (D-082). Never raw to an ADC |
| Water temp sender | Resistive, ground-referenced | ICU input, divider (D-083) |
| Oil pressure sender | Resistive, ground-referenced | ICU input |
| Oil temperature sender (new) | Resistive | ICU input |
| VSS (new) | Pulse | ICU input, Schmitt buffer |
| Alternator sense (BW/WB) | Lamp-driven excitation — a current path through the warning lamp, not a clean digital signal | ICU input, divider |
| Brake fluid level | Closure | ICU input (`A-010`) |
| Wideband O2 | 0–5 V analog out | Capped spare in L1-S1; tap location unknown (K-001) |
| Refrigerant pressure switch, frost switch | Closure | Stay in the factory A/C chain (D-012) |

**The PMU reads none of these** — it has no spare analog input (D-076). The
box that draws the gauge reads the sender (D-083).

---

## Appendix A — LED figures for the lighting project

Kept for the deferred lighting second pass (D-122; [`TAIL-LIGHTS.md`](TAIL-LIGHTS.md)).
**Not this build's design values.** Working figure 0.3 A per LED bulb,
deliberately conservative.

| Circuit | Ch | Filament A | LED A |
|---|---|---|---|
| Tail / park / marker / plate | O6 | 4.4 | 1.5–3.0 |
| Brake | O7 | 3.9 (7.0 measured) | 0.3–0.6 |
| Turn, per side | O17 / O18 | 4.2 (3.4 measured) | 0.3–0.7 |
| Reverse | O19 | 3.9 | 0.3–0.6 |
| Interior + details | O20 | 2.5 | 1.0–2.0 |

Expect draw to drop 5–7× on the lamp circuits. Soft fuses set against
filament are far too generous for LED, so every lamp circuit is re-measured
and re-set as a second pass ([`../04-BUILD/MIGRATION-LOG.md`](../04-BUILD/MIGRATION-LOG.md)). Bulb selection
is unconstrained — bulb-out detection was dropped (D-047), so draw no longer
matters for function.

# LOADS — estimated current draw & signal types

Baseline for leg design. **Every number here is an estimate.** Nothing in this
file may be used to set a soft fuse — that comes from measurement (Checklist
121). These exist so wire gauge, connector class, and relay sizing can be
decided now.

> Kept as one master table rather than scattered across the ten circuit files,
> because leg design needs every load side by side. Each circuit file points here.

---

## Method — how these were derived, best evidence first

**1 · Factory wattage (highest confidence).** The Section E/F sheets print bulb
wattages directly. A = W ÷ 13.8 V (running voltage, not 12 V).

**2 · Factory fuse size (high confidence).** A designed circuit is fused roughly
40–60% above its steady load. A 15 A fuse implies ~7–10 A steady. This is the
single most useful inference available without a meter, and it comes free from
the decode already done.

**3 · Published figures for the part class (medium).** Cited below.

**4 · Motor multipliers (design rule).** Motors are the trap:
<cite index="29-1">a lugging motor draws roughly seven times normal, and a stalled motor as much as ten times — a 2 A motor may pull 16 A lugging and 30 A stalled</cite>.
Wire and connectors get sized for stall, not for running.

**Confidence key:** `A` factory-printed · `B` fuse-inferred · `C` published class
figure · `D` engineering estimate

---

## Lighting — factory incandescent vs planned LED

<cite index="13-1">An incandescent 1157 typically pulls about 2 A, where an LED equivalent pulls about 0.2 A</cite>.
<cite index="17-1">Quality LED 1156/1157 bulbs draw 5–10 W</cite>, so 0.4–0.8 A for
a bright one. Estimates below use **0.3 A per LED bulb** as a working figure —
deliberately conservative, since cheap LEDs draw less and undershooting the
estimate is the safer error for wire sizing.

| Circuit                  | Ch      | Factory                       | Factory A | LED A                     | Conf |
|--------------------------|---------|-------------------------------|-----------|---------------------------|------|
| Headlight LOW            | O2      | 40 W ×2 sealed beam           | 5.8       | already LED               | A    |
| Headlight HIGH           | O3      | 50 W ×2 (60 W halogen opt.)   | 7.2–8.7   | already LED               | A    |
| Front turn               | O17/O18 | 27 W ×2                       | 3.9       | 0.6                       | A    |
| Rear turn                | O17/O18 | 27 W ×2                       | 3.9       | 0.6                       | A    |
| Turn indicators          | O17/O18 | 3.4 W ×2                      | 0.5       | 0.1                       | A    |
| **Turn, per side total** | —       | ~55 W                         | **~4.0**  | **~0.65**                 | A    |
| Brake                    | O7      | 27 W ×2                       | 3.9       | 0.6                       | A    |
| Tail                     | O6      | 8 W ×2                        | 1.2       | 0.6                       | A    |
| Front parking            | O6      | 8 W ×2                        | 1.2       | 0.6                       | A    |
| Side markers             | O6      | 3.8 W ×4                      | 1.1       | 1.2                       | A    |
| License                  | O6      | 6 W ×2                        | 0.9       | 0.6                       | A    |
| **O6 bus total**         | O6      | ~52 W                         | **~4.4**  | **~3.0**                  | A    |
| Reverse                  | O19     | 27 W ×2                       | 3.9       | 0.6                       | A    |
| Interior + spot          | O20     | 5 W                           | 0.4       | 0.15                      | A    |
| Glove box                | O20     | 3.4 W                         | 0.25      | 0.1                       | A    |
| Luggage compartment      | O20     | ~5 W                          | 0.4       | 0.15                      | A    |
| Illumination bus         | O20     | 3.4+1.4+3.4+3.4+3.4+3.4+1.4 W | 1.4       | 0.5                       | A    |
| Warning lamps            | cluster | 1.4 W ×6                      | 0.6       | —                         | A    |
| **O20 bus total**        | O20     | —                             | **~2.5**  | **~1.0 + added lighting** | A    |

**Consequence for leg design:** the LED conversion drops every lamp circuit to
well under 1 A except O6. The 14 and 16 AWG gauges in SPEC are now hugely
oversized on current grounds — but D-016 keeps them anyway, because voltage drop
over a 15-foot run and mechanical robustness, not ampacity, set the floor.

---

## Motors — sized for stall, not for running

| Load                  | Ch            | Factory fuse  | Est. running A | Est. stall A | Conf |
|-----------------------|---------------|---------------|----------------|--------------|------|
| Front wiper LOW       | O8            | 10 A          | 3–5            | 12–20        | C    |
| Front wiper HIGH      | O9            | 10 A (shared) | 5–6            | 12–20        | C    |
| Blower, HI            | O16           | 20 A          | 12–15          | 25+ inrush   | B    |
| Blower, MI / LO       | O16           | —             | 6–10           | —            | B    |
| Pop-up motor, each    | O1 via relays | —             | 4–6            | 15–25        | D    |
| Pop-up, both together | O1            | —             | 8–12           | 30–50        | D    |
| Window motor, each    | O1 via relays | 30 A (both)   | 4–6            | 10–15        | C    |
| Window, both together | O1            | 30 A          | 8–12           | 20–30        | C    |
| Rear wiper            | unallocated   | 10 A          | 2–3            | 8–12         | C    |
| Washer pump           | C2 spare      | —             | 3–5            | 8            | D    |
| Power antenna         | unallocated   | —             | 3–5            | 10           | D    |

(cite index="25-1">An average wiper motor draws about 5 A, rising to 10–12 A under heavy or stall load</cite>.
(cite index="26-1">Window motors measured around 10–15 A at stall</cite>.

**O1 motor bus worst case:** both pop-ups moving while a window runs =
~15 A steady, 40 A+ transient. The 25 A channel handles the steady load; the
integrated flyback diode and the PMU's inrush tolerance handle the transient.
Never operate both pop-ups and both windows simultaneously in software.

## Heating loads

| Load                           | Ch  | Factory fuse | Est. A    | Conf |
|--------------------------------|-----|--------------|-----------|------|
| Rear defog grid                | O4  | 15 A         | 10–13     | B    |
| Heated mirror, each            | O15 | —            | 1–2       | C    |
| Heated seat, each              | O15 | —            | 4–5       | D    |
| Heated washer nozzles          | O15 | —            | 1–2       | D    |
| **O15 comfort bus worst case** | O15 | —            | **12–16** | D    |

Published grid figures run <cite index="8-1">roughly 10–20 A</cite> and
<cite index="11-1">8–17 A across a commercial range</cite>. The factory 15 A fuse
caps the FB's small hatch glass at the low end of that. Grids draw **more when
cold** than hot — the soft fuse needs headroom for the first 30 seconds.

## Engine & fuel

| Load                                  | Ch             | Factory fuse            | Est. A           | Conf        |
|---------------------------------------|----------------|-------------------------|------------------|-------------|
| Ignition coils + igniters (twin, 12A) | O12            | —                       | 4–6              | D           |
| Facet fuel pump (current)             | O5             | 10 A                    | 1–2              | C           |
| Aeromotive Phantom 340 (planned)      | O5             | —                       | 8–12 at pressure | D `[V-040]` |
| Start relay coil                      | O21            | —                       | 0.15–0.2         | C           |
| Horn, pair                            | O11            | 15 A (shared with stop) | 4–8              | B           |
| Hatch / fuel-door solenoid            | C4 spare       | 20 A                    | 3–5 momentary    | D           |
| A/C magnet clutch                     | factory switch | —                       | 3–5              | C           |

## Accessory

| Load                        | Ch          | Factory fuse | Est. A             | Conf |
|-----------------------------|-------------|--------------|--------------------|------|
| Cigarette lighter           | O10         | 15 A         | 8–10 while heating | B    |
| USB-C charging              | O10         | —            | 3 per port         | D    |
| Head unit, switched         | O10         | 20 A         | 2–5                | B    |
| Head unit, clock keep-alive | busbar fuse | —            | 0.01–0.02          | C    |
| Amp remote turn-on          | O10         | —            | 0.1                | D    |
| CAN keypad                  | CAN2        | —            | 0.1–0.3            | D    |
| PMU itself, awake           | —           | —            | 0.15               | C    |

**Total sleeping draw:** head unit clock + PMU standby ≈ 20–40 mA. On the Ionic
S9's 40 Ah that is weeks, not days — but confirm against the BMS's own
low-voltage cutoff, which is usually the binding constraint, not capacity.
**In winter, add the heater's draw** — it runs off the BMS to keep the cells
warm enough to accept charge `[V-052]`.

---

## Input signal types — what each PMU input actually sees

This is the half that decides whether an input needs a ladder, a pull-up, a
divider, or nothing.

| Pin | Input                 | Signal type                                   | Range     | Conditioning needed                                    |
|-----|-----------------------|-----------------------------------------------|-----------|--------------------------------------------------------|
| A1  | Turn stalk            | Resistor ladder → 0–5 V                       | 3 states  | Ladder + internal 10 kΩ pull-up                        |
| A2  | Wiper stalk           | Resistor ladder → 0–5 V                       | 5 states  | Ladder + pull-up                                       |
| A3  | Brake pedal switch    | Simple closure                                | on/off    | Switch to ground, pull-up                              |
| A4  | Pop-up LEFT position  | Ladder from **motor-internal** limit contacts | 3 states  | Ladder. `[V-030]` pinout unknown                       |
| A5  | Pop-up RIGHT position | Same                                          | 3 states  | Same                                                   |
| A6  | Door pins             | Ladder, 2 switches                            | 3 states  | Factory already switches to ground — no change         |
| A7  | Fuel level sender     | **Resistive**, variable                       | `[V-037]` | Divider against +5 V ref. Needs the sender's ohm range |
| A8  | Hazard switch         | Simple closure                                | on/off    | Switch to ground + diode to pin 7                      |
| A15 | Headlight switch      | Ladder, **12 V side**                         | 3 states  | Uses 0–20 V range, reads switched 12 V directly        |
| A16 | Key position          | Ladder, **12 V side**                         | 4 states  | Same                                                   |

### Signals that are not simple switches

| Signal                      | Type                                              | Note                                                                                                                                                                |
|-----------------------------|---------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Tachometer**              | Coil primary pulse, **YG** from ignition coil (T) | Inductive spike well above 12 V. Do NOT land raw on an analog input. Needs clamping/conditioning if ever fed to the PMU. Currently goes to the factory cluster only |
| Water temp sender           | Resistive, ground-referenced                      | Reserved on C1 spare                                                                                                                                                |
| Oil pressure sender         | Resistive, ground-referenced                      | Reserved on C1 spare                                                                                                                                                |
| Alternator sense (BW/WB)    | Lamp-driven excitation                            | Not a clean digital signal — it is a current path through the warning lamp                                                                                          |
| Wideband O2                 | 0–5 V analog out                                  | K-001, tap location unknown                                                                                                                                         |
| Refrigerant pressure switch | Closure                                           | Stays in the factory A/C chain (D-012)                                                                                                                              |
| Frost warning temp switch   | Closure                                           | Stays in the factory A/C chain                                                                                                                                      |

**The tach signal is the one real trap here.** It is not a 0–5 V logic signal.
Landing it directly on an analog input would damage the pin.

---

## Provisional soft-fuse starting points

**Do not program these.** They exist so the bench mule (Checklist 044–045) has a
sane starting value before real measurement replaces them.

| Ch      | Circuit          | Provisional limit               | Basis                       |
|---------|------------------|---------------------------------|-----------------------------|
| O1      | Motor bus        | 25 A, slow trip                 | Stall-tolerant              |
| O2      | Headlight LOW    | 12 A                            | Already LED, will drop hard |
| O3      | Headlight HIGH   | 15 A                            | Already LED                 |
| O4      | Defog            | 16 A                            | Cold-start headroom         |
| O5      | Fuel pump        | 4 A now / 15 A after Aeromotive |
| O6      | Tail/park/marker | 6 A                             | LED, generous               |
| O7      | Brake            | 4 A                             | LED                         |
| O8      | Wiper LOW        | 15 A, slow                      | Stall                       |
| O9      | Wiper HIGH       | 15 A, slow                      | Stall                       |
| O10     | Accessory        | 12 A                            | Lighter dominates           |
| O11     | Horn             | 10 A                            |                             |
| O12     | Ignition         | 8 A                             |                             |
| O15     | Comfort bus      | 20 A                            |                             |
| O16     | Blower           | 20 A, inrush delay              |                             |
| O17/O18 | Turn             | 3 A                             | LED — see below             |
| O19     | Reverse          | 3 A                             | LED                         |
| O20     | Interior PWM     | 5 A                             |                             |
| O21     | Start relay coil | 1 A                             |                             |

### The LED problem, quantified

Turn signal current falls from **~4.0 A to ~0.65 A per side.** That is a 6× drop.
Any bulb-out detection threshold set against the factory number will never
trigger, and any flash-rate logic tuned to incandescent behaviour will hyper-flash.
This is the open decision already logged in the pin plan and checklist — the
numbers above are what makes it concrete.

## Unknowns created by this pass

| ID    | Unknown                                                                      | Blocks              |
|-------|------------------------------------------------------------------------------|---------------------|
| V-037 | Fuel sender ohm range, empty→full                                            | A7 divider design   |
| V-040 | Aeromotive Phantom 340 published draw at target pressure                     | O5 sizing, future   |
| V-041 | Whether the tach will ever feed the PMU (needs a conditioning circuit if so) | C1 spare allocation |
| V-042 | Actual LED bulbs chosen — draw varies 3× between cheap and bright            | Bulb-out thresholds |

---

## UPDATE 2026-08 — cooled seats in, bulb-out out

### D-048 · Comfort bus recalculated with cooled seats

| Load | Qty | A each | Total |
|---|---|---|---|
| Heated seat element | 2 | 4–5 | 8–10 |
| Cooled seat fan module | 2 | 1.5–2.5 | 3–5 |
| Heated mirror | 2 | 1–2 | 2–4 |
| Heated washer nozzle | 2 | 1–2 | 2–4 |
| Wiper park de-icer | 1 | 2–3 | 2–3 |
| **O15 worst case, everything on** | | | **17–26 A** |

**This exceeds the 25 A channel at the top of the range.** Three ways out:

| Option | Effect |
|---|---|
| **A** — Software interlock: never allow heat + cool + de-icer together | Free. They are never wanted simultaneously anyway |
| **B** — Move the de-icer and nozzles to a second channel | Costs a 25 A channel; only O13/O14 are free and they are LS-reserved |
| **C** — Downstream fuse limiting per branch (F10, F11) plus a soft-fuse ceiling | Protects the wire, does not solve the channel ceiling |

**Recommendation: A, with C as backing.** Heated and cooled seats are mutually
exclusive by definition, and the de-icer only runs when the wipers are parked and
cold. A realistic simultaneous worst case is heat + mirrors + nozzles ≈ 14 A.
`[Q-032]` still needs your yes.

### D-047 · What dropping bulb-out changes

| Was | Now |
|---|---|
| Buy higher-draw LED bulbs for detectability | **Buy any LED bulbs** — draw is irrelevant |
| Inline load resistors, 6–25 W, per circuit | **None anywhere** |
| Threshold math in Checklist 013/014 | Gone — ladders only |
| Checklist 051 bulb-out configuration | Reduced to flash rate + hazard override |
| Open decision carried since Rev A | **Closed** |

Current measurement is still used for **soft fuses** (Checklist 121). That is
unchanged and unrelated.

### Revised LED lighting totals

With no resistors and no detection floor, use realistic low-draw LEDs:

| Circuit | Ch | LED A |
|---|---|---|
| Turn, per side | O17 / O18 | 0.3–0.7 |
| Brake | O7 | 0.3–0.6 |
| Tail / park / marker / plate | O6 | 1.5–3.0 |
| Reverse | O19 | 0.3–0.6 |
| Interior + details | O20 | 1.0–2.0 |

Every lamp channel now runs at under 15% of its rating. The gauges in SPEC stay
as they are — set by voltage drop over the run length and by crimp robustness,
not by ampacity (D-016).

### Q-021 · Chime and seat belt warning dropped

Removes the last reason to read the seat belt switch (H-04) and the key reminder
switch (H-03). Both come out of the L4-S and L3-S spare lists — two cavities
recovered.

---

## UPDATE 2026-08 — corrections and module loads

### Fuel pump — corrected part

`[V-054]` The pump is a **Carter P4070**, not the Holley figure used earlier.
Re-estimate O5 against the Carter spec before the soft fuse is set.

| Was | Now |
|---|---|
| Facet / Holley, 1–2 A | **Carter P4070** — draw `[V-054]` unconfirmed |

Typical low-pressure carb pumps of this class sit in the 1–3 A range, so the O5
sizing is unlikely to change. Confirm rather than assume.

### DCU and ICU loads

| Load | On | Est. A |
|---|---|---|
| DCU logic — MCU, transceiver, regulator | O10 | 0.3–0.5 |
| ICU logic + display backlight | O10 | 0.5–1.5 |
| HVAC servos, while moving | O15 via DCU | 1 each, 3–4 channels |
| Comfort loads — seats, mirrors, nozzles, de-icer | O15 via DCU | 12–16 |

**HVAC servos and comfort loads are on O15, not O10.** Only module logic and the
display backlight sit on the accessory bus.

### O10 accessory bus — the open problem

`[Q-038]`

| Load | A |
|---|---|
| Cigarette lighter | 8–10 while heating |
| USB-C | 3 per port |
| Head unit, switched | 2–5 |
| DCU logic | 0.3–0.5 |
| ICU + backlight | 0.5–1.5 |
| **Worst case** | **~20 A on a 15 A channel** |

Recommendation is to delete the lighter — it is the only load here that does not
earn its place with USB-C fitted, and the alternative is a cigarette lighter
tripping the channel that powers the instrument cluster.

### Sleeping draw — revised

| Source | mA |
|---|---|
| PMU standby | 150 |
| Head unit clock | 10–20 |
| DCU standby (if not fully switched) | `[V-056]` |
| ICU standby | 0 — fully switched |
| **Battery heater, winter** | `[V-052]` |

K11 (constant-bus master) can drop the head unit keep-alive on a long park.
The battery heater is the unknown that matters in a Fort Collins winter.

---

# BASELINE IS INCANDESCENT — 2026-08 (D-124)

**Lighting moved to `02-PROJECTS/lighting-body/` (D-123).** This project's design
figures are **stock filament bulbs**. The LED columns above are kept as a future
reference for the lighting project's second-pass fuse reset (D-122) — they are
not this project's design values.

## Design figures — use these

| Circuit | Ch | Rating | **Design draw** | Headroom |
|---|---|---|---|---|
| Tail / park / marker / plate | O6 | 15 A | **4.4 A** | 71% |
| Brake | O7 | 15 A | **3.9 A** | 74% |
| Turn, per side | O17 / O18 | 7 A | **4.2 A** | 40% |
| Reverse | O19 | 7 A | **3.9 A** | 44% |
| Interior + glovebox + luggage + illumination | O20 | 7 A | **2.5 A** | 64% |
| Headlight LOW | O2 | 25 A | already LED housings | — |
| Headlight HIGH | O3 | 25 A | already LED housings | — |

Wire gauge is unchanged — D-016 sets it by voltage drop and crimp robustness,
not current.

## Inrush — the number that actually matters now

A cold filament draws **8–12× steady for a few milliseconds.**

| Circuit | Steady | Cold inrush |
|---|---|---|
| Turn, per side | 4.2 A | ~40 A momentary |
| Tail bus | 4.4 A | ~45 A momentary |
| Brake | 3.9 A | ~40 A momentary |

**Every lamp channel needs an inrush window configured** (D-120). A flat 5 A soft
fuse trips on the first flash. The PMU supports a current limit with a time
characteristic — use it.

**Turn signals are the case to get right**, because they cycle constantly. After
the first flash the filament stays warm and inrush drops sharply, but the first
one is real.

> This is the one respect in which incandescent is **harder** than LED. Everything
> else about filament bulbs is easier — more headroom, no bulb-out threshold
> problem, and the dual-filament rear bulb maps directly onto the two-channel
> tail/brake design with no driver board (D-121).

## What the lighting project will change

When it runs, every lamp channel gets re-measured and every soft fuse re-set
(D-122). Expect draw to drop by roughly 5–7× on the lamp circuits. The second-pass
table is in `../05-BUILD/MIGRATION-LOG.md`.

# LADDERS — resistor ladder design

*Rev 2026-08-30 · owns: resistor values and expected ADC readings for every switch ladder.*

All six multi-position switches, calculated. The decode tables the PMU gets
are in [`PMU-CONFIG.md`](PMU-CONFIG.md) §1.

## Contents

Design principle · A1–A8 ladders (A1 turn · A2 wiper · A4/A5 pop-up · A6
doors · A3/A8 switches) · A9–A16 12 V ladders (A15 · A16) · Physical build ·
Verification

**Values are E24 1 %.** Every ADC figure below is theoretical — verification
against real resistors happens **in the car during Phase 6** (D-142), when the
switches are genuinely wired; write the measured value into the config lookup.

---

## Design principle: no state uses a dead short

Every valid switch position goes to ground through a **finite** resistor. That
buys fault detection for free:

| ADC reading | Meaning |
|---|---|
| **~0 counts** | Wire shorted to ground — a fault, not a position |
| **~1023 / 4095** | Wire open or connector unplugged — a fault |
| anything between | A real switch position |

If any state used a direct ground, a chafed wire would look identical to a
pressed switch. This costs one resistor per ladder and is worth it.

---

## A1–A8 ladders — 0–5 V, 10-bit, internal 10 kΩ pull-up

Switch closes to ground through R. The formula:

```
count = 1023 × R / (R + 10000)
R     = 10000 × count / (1023 − count)
```

### A1 · Turn stalk — 3 states

| Position | R (E24) | Volts | ADC | Gap |
|---|---|---|---|---|
| LEFT | 1.8 kΩ | 0.76 | **156** | — |
| RIGHT | 10 kΩ | 2.50 | **512** | 356 |
| OFF (centre) | 47 kΩ | 4.12 | **843** | 331 |

Open = 1023 (fault), short = 0 (fault). Margins are enormous.

### A2 · Wiper stalk — 5 states

| Position | R (E24) | Volts | ADC | Gap |
|---|---|---|---|---|
| WASH | 1.8 kΩ | 0.76 | **156** | — |
| HIGH | 4.7 kΩ | 1.60 | **327** | 171 |
| LOW | 10 kΩ | 2.50 | **512** | 185 |
| INT | 18 kΩ | 3.21 | **658** | 146 |
| OFF | 47 kΩ | 4.12 | **843** | 185 |

Smallest gap 146 counts, against a 40-count target. Comfortable.

WASH sits at the low end deliberately — it is the position most likely to be
held briefly, and the widest margin from the fault floor.

### A4 / A5 · Pop-up transit + inhibitor — 4 states each (D-187)

The motor exposes **one** position contact — the YG line, **closed in transit
or when blocked, open at rest at either limit** (D-177; Camden's confirmation
of the factory indicator's behaviour). Up vs down is tracked in software from
commanded state; YG says *moving / stuck*, and D-186's 4 s timeout turns
"still closed" into an obstruction fault.

Each node also carries one inhibitor contact — resistors at the switch,
spliced onto the node at the dash post: **P/N on A4** (crank interlock),
**R on A5** (reverse lamps). A **47 kΩ baseline** to ground at the connector
keeps "nothing closed" distinct from a broken wire.

| Source | R (E24) |
|---|---|
| Baseline, always fitted | 47 kΩ |
| YG transit contact | 3.3 kΩ |
| Inhibitor contact (P/N on A4 · R on A5) | 12 kΩ |

| State | Combination | ADC | Gap |
|---|---|---|---|
| Transit + inhibitor | 3.3 ∥ 12 ∥ 47 kΩ | **201** | — |
| Transit | 3.3 ∥ 47 kΩ | **245** | 44 |
| Inhibitor closed | 12 ∥ 47 kΩ | **500** | 255 |
| Idle | 47 kΩ | **843** | 343 |
| Open / unplugged | — | **1023** | fault |

44 counts on the tight pair — window ±20, A6's class. The inhibitor's R
contact takes its own conductor: L1-S1 11 carries P/N and **R takes the
plain spare L1-S2 7** (D-187, amended). One aged-contact caution: the
YG cam spent its life switching a 3.4 W lamp; confirm it reads cleanly at the
ladder's 0.5 mA in Phase 6.

### A6 · Door pins — 4 states

Two independent switches on one node. A fifth state — the luggage-compartment
switch (`A-012`) — is proposed for this node; re-run the maths before adding it. **This is the tightest ladder in the car**
because "both doors open" is the parallel combination and lands close to
"passenger only."

| State | R | ADC | Gap |
|---|---|---|---|
| Both open | 33k ∥ 8.2k = 6.57 kΩ | **406** | — |
| Passenger only | 8.2 kΩ | **461** | **55** |
| Driver only | 33 kΩ | **785** | 324 |
| Both closed | open | **1023** | 238 |

**55 counts on the tight pair.** Above the 40-count target but the least margin
anywhere in this design.

*Measured 2026-08:* open-door closures are clean — L 0.1 Ω, R 0.2 Ω to
ground — and the shut readings were **MΩ** (1.13 / 20.9): clean opens. The
switches are healthy and this table stands as designed (D-187). Verify on the bench before trusting it, and if it drifts,
accept losing the "both open" state — nothing in the config actually needs to
distinguish it from "passenger open."

### A7 · Fuel sender — measured curve (V-037 → D-197)

Measured on the car, float swept: **FULL 6 Ω · MID 31.5 Ω · EMPTY 80 Ω.**
Against the internal 10 kΩ pull-up alone that is ~8 counts of span inside
the fault floor — unusable — so A7 carries an **external 100 Ω 1 % pull-up
to the +5 V reference, at the sender connector** (1 W part, or 2 × 200 Ω
½ W in parallel; it dissipates ~0.25 W at full).

| Tank | Sender Ω | ADC | Gap |
|---|---|---|---|
| FULL | 6 | **58** | — |
| MID | 31.5 | **247** | 189 |
| EMPTY | 80 | **457** | 210 |
| Short / chafe | <2 | **<25** | fault |
| Open / unplugged | — | **>900** | fault |

The sender is nonlinear (mid sits at 31.5 Ω, not the linear 43) — the config
uses the three-point lookup with interpolation, trued by the in-car read
(D-142). Harness resistance (~0.3 Ω) is ~5 % at full; calibration absorbs it.

### A3 · Brake pedal — 2 states

Not a ladder. Single switch to ground through **4.7 kΩ**: pressed **327**,
released **1023**. The 4.7 kΩ instead of a dead short is what makes a chafe
distinguishable from a press — on the brake pedal that matters.

### A8 · Hazard + horn — 4 states (Q-071 → D-190)

Two momentaries summed: hazard **4.7 kΩ**, horn **12 kΩ**, resistors at the
switch, the horn conductor (L3-S1 11) splicing onto the node at the post.

| State | Combination | ADC | Gap |
|---|---|---|---|
| Hazard + horn | 4.7 ∥ 12 kΩ | **259** | — |
| Hazard | 4.7 kΩ | **327** | 68 |
| Horn | 12 kΩ | **558** | 231 |
| Released | — | **1023** | 465 |

Window ±30. The horn switch closes to ground, so its asleep wake is a plate
PNP sensing this node (D-190, the D-188 pattern) into the horn's wake diode.

---

## A9–A16 ladders — 0–20 V, 12-bit, 12 V side

These read switched 12 V directly. Use a **10 kΩ pull-down** at the PMU and feed
each source through a series resistor.

```
V    = 12 × 10000 / (Rseries + 10000)
count = V / 20 × 4095
```

### A15 · Headlight / dimmer / pass — 5 states, summed (Q-065 → D-184)

A summed node like A16. Sources, each feeding the node through its own
resistor, with the **100 kΩ bias from +5 V** (D-167) retained so OFF reads 93
and a true open reads 0:

| Source | R (E24) | Fed from | Live when |
|---|---|---|---|
| PARK contact | 33 kΩ | +12 V | PARK and HEAD |
| HEAD contact | 15 kΩ | +12 V | HEAD |
| Dimmer HIGH contact | 8.2 kΩ | **the HEAD side** | HEAD + dimmer HIGH |
| PASS momentary | 3.3 kΩ | +12 V direct | flash, any switch position |

| State | ADC | Gap |
|---|---|---|
| OFF (bias only) | **93** | — |
| PARK | **604** | 511 |
| HEAD + LO | **1201** | 597 |
| HEAD + HI | **1666** | 465 |
| PASS active | **1828–2045** | 162 to the band |

Smallest inter-state gap 162 counts — clears the 60-count bar, so the
five-state option stands. **PASS is a superstate:** any reading ≥1750 means
"flash requested" — the logic holds the previously decoded lighting states
and forces high beam, so the sub-60-count differences inside the PASS band
(which underlying position PASS was pressed from) never need decoding.

### A16 · Key position — 4 states

**This one has a real complication.** On the factory switch, ACC stays live in
RUN, and both ACC and IG stay live in START. The node sees the sum, not one
source. Values are chosen so the *combinations* are distinct:

| Position | Live sources | Effective R | Volts | ADC | Gap |
|---|---|---|---|---|---|
| OFF | none | — | 0.00 | **0** | — |
| ACC | ACC via 33 kΩ | 33 kΩ | 2.79 | **571** | 571 |
| RUN | + IG via 15 kΩ | 10.3 kΩ | 5.91 | **1210** | 639 |
| START | + ST via 6.8 kΩ | 4.10 kΩ | 8.51 | **1743** | 533 |

Feed each ignition switch output through its own resistor into the shared node.
Do **not** design this as a single-source ladder — it will read wrong the moment
two contacts are live together.

`V-050` → D-178 — closed off FSM sheet F. Either crank behaviour decodes:
if ACC drops during START the node reads ~1673 instead of 1743 — still >400
counts from RUN — so the resistors can be soldered now, and the Phase 6
in-car ADC read (D-142) writes the true value into the config lookup.

---

## Physical build

Put the resistors **at the switch**, not at the PMU. One wire returns to the box
per ladder instead of one per position — which is the entire point.

Use 1% metal film, 1/4 W. Dissipation is negligible everywhere (worst case is
about 2.5 mW). Heat-shrink each resistor individually and pot the cluster if it
lives anywhere damp.

## Verification — in the car, Phase 6 (D-142)

1. With the switch wired, read the ADC at every position in the PMU client;
   compare to the table above.
2. Adjust values if any gap falls under 40 counts.
3. Write the **measured** values into the config lookup ([`PMU-CONFIG.md`](PMU-CONFIG.md) §1),
   not the calculated ones.
4. Repeat for all six.

Expect real readings to sit a few counts off — the internal pull-up has
tolerance and so does the reference. The bench ladder rig was dropped with the
plywood mule (D-141); the firmware decode logic is proven separately by
`ladder_decode_test`.

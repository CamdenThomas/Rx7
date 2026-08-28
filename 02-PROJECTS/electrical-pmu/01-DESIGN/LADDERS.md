# LADDERS — resistor ladder design

All six multi-position switches, calculated. Closes Checklist steps 013 and 014.

**Values are E24 1%.** Every ADC figure below is theoretical — verify on the
bench (Checklist 047–050) and write the measured value into the config lookup.

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

### A4 / A5 · Pop-up position — 3 states each

Two limit switches per side feeding one node. `[V-030]` the internal motor
pinout is still unknown, so these values are provisional on which contacts exist.

| State | R (E24) | ADC | Gap |
|---|---|---|---|
| DOWN limit closed | 3.3 kΩ | **254** | — |
| UP limit closed | 10 kΩ | **512** | 258 |
| Mid-travel (neither) | 47 kΩ | **843** | 331 |

If both limits somehow close, the parallel combination reads ~193 — below the
DOWN state and distinguishable as a fault.

### A6 · Door pins — 4 states

Two independent switches on one node. **This is the tightest ladder in the car**
because "both doors open" is the parallel combination and lands close to
"passenger only."

| State | R | ADC | Gap |
|---|---|---|---|
| Both open | 33k ∥ 8.2k = 6.57 kΩ | **406** | — |
| Passenger only | 8.2 kΩ | **461** | **55** |
| Driver only | 33 kΩ | **785** | 324 |
| Both closed | open | **1023** | 238 |

**55 counts on the tight pair.** Above the 40-count target but the least margin
anywhere in this design. Verify on the bench before trusting it, and if it drifts,
accept losing the "both open" state — nothing in the config actually needs to
distinguish it from "passenger open."

### A3 · Brake pedal, A8 · Hazard — 2 states

Not ladders. Single switch to ground through **4.7 kΩ**.

| State | ADC |
|---|---|
| Pressed | **327** |
| Released | **1023** |

The 4.7 kΩ instead of a dead short is what makes a chafe distinguishable from a
press. On the brake pedal that matters.

---

## A9–A16 ladders — 0–20 V, 12-bit, 12 V side

These read switched 12 V directly. Use a **10 kΩ pull-down** at the PMU and feed
each source through a series resistor.

```
V    = 12 × 10000 / (Rseries + 10000)
count = V / 20 × 4095
```

### A15 · Headlight switch — 3 states

| Position | Rseries | Volts | ADC | Gap |
|---|---|---|---|---|
| OFF | — (pull-down only) | 0.00 | **0** | — |
| PARK | 10 kΩ | 6.00 | **1229** | 1229 |
| HEAD | 0 Ω (direct) | 12.00 | **2457** | 1228 |

**Note the ambiguity:** OFF and "connector unplugged" both read 0. Unavoidable on
the 12 V side without a bias resistor. If you want the distinction, add a 100 kΩ
bias from +5 V to the node — OFF then sits near 100 counts and true open sits at
0. Cheap; recommended.

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

`[V-050]` Confirm on the car which ignition switch outputs stay live in RUN and
START. The FSM shows ACC and IG both live in START on many Mazdas of this era,
but it should be continuity-checked before the resistors are soldered.

---

## Physical build

Put the resistors **at the switch**, not at the PMU. One wire returns to the box
per ladder instead of one per position — which is the entire point.

Use 1% metal film, 1/4 W. Dissipation is negligible everywhere (worst case is
about 2.5 mW). Heat-shrink each resistor individually and pot the cluster if it
lives anywhere damp.

## Bench procedure (Checklist 047–050)

1. Build one ladder on a scrap switch.
2. Read the ADC at every position; compare to the table above.
3. Adjust values if any gap falls under 40 counts.
4. Write the **measured** values into the config lookup, not the calculated ones.
5. Repeat for all six.

Expect real readings to sit a few counts off — the internal pull-up has tolerance
and so does the reference.

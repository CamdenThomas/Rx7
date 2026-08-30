# CUSTOM TAIL LIGHTS

*Rev 2026-08-30 · owns: the custom tail-light design — the legal position, the area maths, the driver board, the process (TL-1 … TL-19), and the headlamp sourcing rule. Deferred until the electrical rebuild is shaken down (L-004).*

Thin LED strip per side, in the stock aperture, at stock width. White reverse
section inboard, red for tail / brake / turn across the rest (D-107). Reverse
section 5 cm × 2.2 cm strip (Q-047 → L-001); driver PCB per side (Q-046 →
D-111); headlamps sourced, not built (L-002).

## Contents

1. The legal position · 2. The intensity problem · 3. Photometry · 4. Process
· 5. Wiring · 6. Open items · 7. One-line summary · 8. Reverse section sizing
and the headlamp question

---

## 1 · The legal position

### Does FMVSS bind you?

**Not directly.** FMVSS 108 binds manufacturers, dealers, distributors and repair
businesses through the "make inoperative" provision. **An owner modifying their
own vehicle is not covered by it federally.**

What does apply is **Colorado state equipment law**, which requires functioning
tail, stop and turn lamps. State statutes generally defer to SAE/DOT standards
for what "functioning" means, and an officer's judgement matters on the roadside.

**And separately from legality: liability.** If you're rear-ended and your lamps
are demonstrably below the federal standard, that becomes a fact in the case.

**Conclusion: build it to the standard even though you aren't bound by it.**
The standard is also just the engineering baseline for being seen.

### The number that constrains the design

FMVSS 108 S6.4.1: “the effective projected luminous lens area of a single compartment stop lamp, and a single compartment rear turn signal lamp, shall be not less than 50 square centimetres (7¾ square inches).”

And for split designs: “if a multiple compartment lamp or multiple lamps are used, the effective projected luminous lens area of each compartment shall be at least 22 square centimetres, provided the combined area is at least 50 square centimetres.”

**Backup lamps have no minimum area** — an NHTSA interpretation states plainly
that “there is no minimum EPLLA for these lamps”, though they must still
meet the visibility requirements.

### What that does to a 1 cm strip

`V-063` — measure the actual stock aperture width (`T-034`). Working from a nominal 30 cm:

| Strip height | Red area (30 cm wide) | Compliant? |
|---|---|---|
| **1.0 cm** | 30 cm² | **No** — 40% short |
| 1.5 cm | 45 cm² | No |
| **1.7 cm** | 51 cm² | **Yes, marginal** |
| **2.0 cm** | 60 cm² | **Yes, comfortable** |

**Minimum height = 50 cm² ÷ red width.**

And the white reverse section eats into it. If reverse takes 6 cm of a 30 cm
aperture, the red is only 24 cm wide, so the red strip needs **2.1 cm** to clear
50 cm².

### The answer

**Go to 2 cm instead of 1 cm.** It is still unmistakably a thin strip, it clears
the standard with margin, and it removes the entire argument. A centimetre of
height is a much cheaper concession than a non-compliant lamp.

### Other rules this design must respect

| Rule | Effect here |
|---|---|
| Rear turn signals may be **red or amber** in the US | Red is fine. Combination stop/turn on shared LEDs is standard practice |
| Stop must be **brighter than tail** | Requires two intensity levels from the same red array |
| Turn must **override** stop on that side | When braking and indicating, the turning side flashes |
| Reverse lamps must be **white** | Inboard section, as planned |
| Photometric minimums (candela at test points) | **Generic LED strip will not meet these.** See §3 |

---

## 2 · The intensity problem, and why each side needs a driver board

The stock lamp used a **dual-filament bulb** — one filament for tail, both for
stop. Your PMU has tail on **O6** and brake on **O7** as separate channels.

**You cannot feed one LED array from two channels directly.** O6 and O7 would
backfeed into each other, and the PMU would see current on a channel it isn't
driving.

Three ways out:

| Option | Verdict |
|---|---|
| **A** — Separate LED zones: tail LEDs, brake LEDs, turn LEDs | Simplest, no electronics. But it breaks the single-strip look and wastes area |
| **B** — Diode-isolate O6 and O7 into a shared array with a resistor on the tail leg | Cheap, works, crude. Intensity ratio is set by a resistor and drifts with temperature |
| **C** — **A small driver PCB in each housing** | Takes tail, brake and turn as logic inputs, drives the array with proper constant-current, handles the intensity ratio and turn override locally |

**Recommendation: C.** You are already laying out PCBs for the DCU and ICU, and
this is a far simpler board. It gives you a correct intensity ratio, proper
constant-current drive, no backfeed, and turn-override logic that doesn't depend
on the PMU getting the sequencing right.

Q-046 → D-111: option C is decided. Confirm the board is designed before any strip is bought (TL-5).

---

## 3 · Photometry — the part that actually bites

Area is easy to satisfy. **Candela output at the specified test angles is not.**

A generic adhesive LED strip will fail SAE photometric requirements in every
direction that matters. What it needs:

- **Automotive-grade LEDs** with a known candela figure, not a lumens-per-metre
  rating from a hobby strip
- **An optic** — lens or reflector — spreading light to the required horizontal
  and vertical angles, not just straight back
- Correct **red wavelength**, not white LEDs behind red plastic

`V-064` (`T-037`) — the realistic path is buying **DOT/SAE-compliant LED modules** designed
for trailer or truck use and building the housing around them, rather than
building a light engine from bare emitters. That gets you photometry that
someone else has already tested.

---

## 4 · Process

### Design
- [ ] **TL-1** Measure the stock aperture — width, height, depth, mounting (`V-063`, `T-034`)
- [ ] **TL-2** Set strip height from the area math. **Expect ~2 cm**
- [ ] **TL-3** Decide the reverse/red split, recompute the red area
- [ ] **TL-4** Choose LED modules — DOT/SAE compliant, red and white (`V-064`, `T-037`)
- [ ] **TL-5** Design the driver PCB — tail, brake, turn inputs; constant-current out (Q-046 → D-111)
- [ ] **TL-6** Design the housing and lens. Sealed, serviceable, stock mounting
- [ ] **TL-7** Confirm the PMU config: O6 tail, O7 brake, O17/O18 turn, O19 reverse

### Prototype
- [ ] **TL-8** Breadboard one driver, one strip. Verify the intensity ratio and turn override
- [ ] **TL-9** Bench-test with the PMU driving all four inputs
- [ ] **TL-10** Measure current draw — into `pmu_pins.csv` for the second-pass soft fuses (D-122)
- [ ] **TL-11** Night comparison against the stock lamp, from 30 m and from 3 m
- [ ] **TL-12** Wide-angle check — visible from 45° either side

### Build
- [ ] **TL-13** Fabricate both housings
- [ ] **TL-14** Assemble, pot or seal, pressure-check
- [ ] **TL-15** Fit and aim
- [ ] **TL-16** Wet test — condensation is what kills custom lights

### Integrate
- [ ] **TL-17** Migrate on the normal per-circuit loop, [`../electrical-pmu/05-BUILD/MIGRATION-LOG.md`](../electrical-pmu/05-BUILD/MIGRATION-LOG.md) second pass
- [ ] **TL-18** Set soft fuses from measured draw
- [ ] **TL-19** Keep the stock lamps intact as a fallback until the strips are proven

---

## 5 · Wiring — no change to the harness

The strips land on exactly the channels already allocated. **This does not touch
the pin plan.**

| Function | Channel | Connector |
|---|---|---|
| Tail / park | O6 | L4-M 1 |
| Brake | O7 | L4-M 2 |
| Turn L / R | O17 / O18 | L4-M 5, 6 |
| Reverse | O19 | L4-M 7 |
| Ground | — | Rear star node |

Each housing needs **five conductors**: tail, brake, turn, reverse, ground. That
is what the existing rear lamp branch already carries.

**Current drops.** LED replaces incandescent — see [`LOADS.md`](../electrical-pmu/01-DESIGN/LOADS.md). Update the
estimates after TL-10.

---

## 6 · Open items

The live list is [`OPEN.md`](OPEN.md); the tasks are [`TASKS.md`](TASKS.md).

| ID | Item | State |
|---|---|---|
| `V-063` | Stock aperture dimensions — **drives the whole design** | open — `T-034` |
| `V-064` | DOT/SAE-compliant LED module source, red and white | open — `T-037` |
| Q-046 → D-111 | Driver PCB per side | decided |
| Q-047 → L-001 | Reverse section 5 cm wide, 2.2 cm strip | decided, §8 |
| `Q-048` | Which headlamp unit | open — `T-036` |
| `V-066` | Round or rectangular sealed beams on this car | open — `T-035` |

## 7 · The one-line summary

**Legal, yes — as an owner you aren't bound by FMVSS, and Colorado only requires
working lamps. But build it to the 50 cm² standard anyway, which means about
2 cm tall rather than 1 cm.** The rest is photometry, and the shortcut there is
buying compliant modules instead of bare emitters.

---

## 8 · Reverse section sizing, and the headlamp question

*The reasoning behind L-001 (Q-047) and the headlamp half of Q-044 → D-110.*

### Q-047 → L-001 · How small can the white reverse section be?

You asked how the size-versus-brightness balance works. It doesn't work the way
it does for the red section, and that's the useful part.

**Backup lamps have no minimum lens area.** An NHTSA interpretation states
plainly that there is no minimum EPLLA for these lamps — they only have to meet
the visibility and photometric requirements. So unlike the stop and turn
functions, you are not fighting a 50 cm² floor.

**But brightness does not substitute for area, because a reverse lamp has a
different job.** Stop and turn lamps exist to be *seen*. A reverse lamp exists to
*light the ground behind the car* and to be seen. Shrinking the aperture and
raising the intensity to compensate gives you:

- A **hotspot instead of a wash.** Same total lumens concentrated into a smaller
  emitting area lights a smaller patch of ground
- **Glare** for anyone behind you, because intensity per unit area went up
- **Worse off-axis visibility** — the whole point of the area requirement on
  other lamps

**Recommendation: 5–6 cm wide.**

That is enough emitting area to throw a usable wash rather than a spot, it is
unmistakably a deliberate design element rather than an afterthought, and it
leaves the red section room.

### What that does to the red section

Working from a nominal 30 cm aperture (`V-063` — measure it):

| Reverse width | Red width | Red height for 50 cm² |
|---|---|---|
| 4 cm | 26 cm | 1.93 cm |
| **5 cm** | **25 cm** | **2.00 cm** |
| **6 cm** | **24 cm** | **2.09 cm** |
| 8 cm | 22 cm | 2.28 cm |

**Design target: 5 cm reverse, 2.2 cm strip height.** That gives 55 cm² of red —
10% margin over the federal minimum — and a reverse section that actually works.

The 0.2 cm of margin costs nothing visually and means a measurement error in
`V-063` doesn't put you under the line.

---

### Q-044 → D-110 · Headlamps — the part that is genuinely different

**Pop-ups stay** (D-110). The bucket keeps its mechanism, its four heavy
conductors, its relays and its position ladders. Only the lamp inside changes.

### Do not build this one custom

Tail lights are a reasonable custom project. **Headlamps are not**, and the
reason is beam pattern.

| Tail lights | Headlamps |
|---|---|
| Requirement is *be seen* | Requirement is *illuminate the road without blinding oncoming traffic* |
| Spec is area + candela at test points | Spec is a **beam pattern with a defined cutoff**, measured across a grid of angles |
| A well-made LED array with an optic can meet it | Needs a designed reflector or projector. **A strip of LEDs cannot produce a cutoff** |

A thin LED strip pointed forward produces a wide glare source with no cutoff.
It is the single most dangerous common lighting modification, and unlike the tail
lights, no amount of care in fabrication fixes it — the physics of the optic is
the problem.

### Source it, don't build it

The 1982 FB uses **7-inch round sealed beams**, one per side, in the pop-up
buckets — `V-066`, confirm round vs rectangular on this car (`T-035`); [`LOADS.md`](../electrical-pmu/01-DESIGN/LOADS.md) records LED housings as currently fitted, so one of the two files is wrong.

For a shorter rectangular look inside a round bucket:

| Option | Note |
|---|---|
| **DOT-compliant 4×6 rectangular LED sealed beam** | Off-the-shelf, road legal, real beam pattern. Needs an adapter plate in the round bucket |
| **5×7 rectangular LED sealed beam** | Same, larger. Less "short" |
| **7-inch round LED with a rectangular-appearing DRL/element** | Fits the bucket directly. Gets the look without the fabrication |
| Custom strip | **Not recommended.** No cutoff, not legal, genuinely unsafe |

`Q-048` (`T-036`) — which of these three? All are sourceable. The adapter plate for a
4×6 in a round bucket is the only fabrication involved, and it's a flat plate.

### What this changes electrically

**Nothing.** O2 low, O3 high, `L2-P1` cavities 1 and 2, 12 AWG. Draw drops from
the sealed-beam figures to whatever the LED unit specifies — a second-pass measurement into
`pmu_pins.csv` (D-122).

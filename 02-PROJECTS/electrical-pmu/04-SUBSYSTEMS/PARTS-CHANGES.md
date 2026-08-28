# PARTS CHANGES — what's being replaced, and with what

Every load that will not be the same part at the end of the build. Keeps the
"measured value" and the "design value" from being confused.

**Status key:** `CHOSEN` decided · `PENDING` known change, part not picked ·
`DEATH DATE` works now, will fail or be replaced · `DELETED` gone entirely

---

## 1 · Lighting — all of it changes

**No bulb currently on the car is the final part.** Every lamp except the
headlights is still incandescent; the headlights are LED but not the final choice.

| Circuit                      | Now                             | Becoming                         | Status    |
|------------------------------|---------------------------------|----------------------------------|-----------|
| Tail / park / marker / plate | 8 W, 3.8 W, 6 W incandescent ×8 | LED                              | `PENDING` |
| Brake                        | 27/8 W dual filament ×2         | LED                              | `PENDING` |
| Turn front                   | 27 W ×2                         | LED                              | `PENDING` |
| Turn rear                    | 27 W ×2                         | LED                              | `PENDING` |
| Turn indicators              | 3.4 W ×2                        | LED                              | `PENDING` |
| Reverse                      | 27 W ×2                         | LED                              | `PENDING` |
| Interior + spot              | 5 W                             | LED                              | `PENDING` |
| Glove box                    | 3.4 W                           | LED                              | `PENDING` |
| Luggage compartment          | ~5 W                            | LED                              | `PENDING` |
| Illumination bus             | 3.4 / 1.4 W ×7                  | LED                              | `PENDING` |
| **Headlight LOW**            | LED enclosed housing            | **Thin LED strip, one per side** | `PENDING` |
| **Headlight HIGH**           | LED enclosed housing            | **Thin LED strip, one per side** | `PENDING` |

**Bulb selection is genuinely unconstrained** — bulb-out detection was dropped
(D-047), so draw no longer matters for function. Buy on light output and colour,
not on current.

### The headlight change raises a real question

`[Q-044]` **A thin strip per side changes the pop-up situation.**

| Option | Consequence |
|---|---|
| **A** — Strips mount inside the existing pop-up buckets | Pop-ups stay. K1–K4, four 12 AWG legs, A4/A5 ladders all survive. Draw drops from ~12 A to maybe 2–3 A |
| **B** — Strips mount fixed in the nose, pop-ups deleted | **Removes 4 heavy conductors, 4 relays, 2 ladder inputs and the entire L2-P2 connector.** Also removes the wink feature and a defining piece of the car's character |

This is the largest single simplification still available in the project, and
it's also an aesthetic decision about what an FB *is*. **Not Claude's call.**

Until it's answered, the design assumes option A — pop-ups retained, everything
allocated.

---

## 2 · Death dates — works now, won't later

| Item | State | Replacement | Design implication |
|---|---|---|---|
| **Fuel pump** | Carter P4070, working | Aeromotive Phantom 340 in-tank, eventually | O5 sized for **8–12 A**, not the Carter's 1–3 A. `L4-P` already carries a spare heavy cavity for the upgrade |
| **Blower motor** | Original, failing | Not chosen | O16 sized for **worst-case 20 A** with the flyback diode. Any replacement fits under that |
| Ionic battery heater | New | — | Winter draw still unquantified `[V-052]` |

**The rule for death-date items:** size the channel, wire and connector for the
worst plausible replacement. Set the soft fuse at migration from whatever is
actually fitted that day.

---

## 3 · New — did not exist on the car

| Item | Note | Status |
|---|---|---|
| **Fuel-door solenoid** | Never existed. Genuinely new, needs sourcing *(T-032)* | `PENDING` |
| **Heated seats** | 2 × ~4 A elements | `PENDING` |
| **Cooled seats** | 2 × fan modules, ~1.5–2.5 A | `PENDING` |
| **Heated washer nozzles** | 2 × ~1–2 A | `PENDING` |
| **Wiper park de-icer** | ~2–3 A | `PENDING` |
| **USB-C ports** | Replacing the lighter's function | `PENDING` |
| **Radar sensors** | Concealed, front and rear, DCU-driven. Custom subsystem `[V-061]` | `PENDING` |
| **CAN keypad** | Ecumaster, 8-key | `CHOSEN` |
| **DCU + ICU** | Teensy 4.1 ×2 | `CHOSEN` |
| **Cluster display** | Format undecided `[Q-037]` | `PENDING` |
| **Oil temperature sender** | New gauge input | `PENDING` |
| **VSS sensor** | New speed input | `PENDING` |

---

## 4 · Replacing a broken or missing part

| Item | Why | Status |
|---|---|---|
| **Hatch latch switch** | Original is broken *(T-033)* | `PENDING` |
| **Side mirrors** | Larger, heated, digital control. Factory control is dead. Conductor count unconfirmed `[V-060]` | `PENDING` |
| **Head unit** | Double-DIN | `PENDING` |

---

## 5 · Deleted — not carried into the new harness

| Item | Reason |
|---|---|
| Cigarette lighter | D-095 — freed 8–10 A on O10 |
| Cruise control unit and switches | D-097 — gone, unwanted |
| Rear wiper and washer | D-097 — gone |
| Power antenna | D-097 — gone |
| Headlight cleaner | D-097 — gone |
| All cold-start hardware | D-097 — zero remain post-Weber |
| Stop light checker | D-097 — PMU current sensing replaces it |
| Control Processing Unit | D-013/014 — flasher, wiper INT, chime, belt, key reminder all become software |
| Instrument panel dimmer rheostat | O20 PWM replaces it |
| Retractable headlight switch | D-038 — pop-ups raise from the A15 ladder |
| Horn relay | PMU switches the horns directly |
| Interval wiper control unit | Software timer on O8 |
| All 15 factory fuses and the fuse block | Replaced by soft fuses + 13 panel fuses |

---

## 6 · Carrying forward unchanged

**These are what the meter session actually exists for.** No spec sheet, no
second chance.

| Item | Note |
|---|---|
| Wiper motor | Two-speed + park switch. O8/O9 |
| Pop-up motors ×2 | Pending Q-044 |
| Window motors ×2 | Sill H-bridges |
| Defog grid | Measure cold |
| Horns ×2 | Ground moves to the front star node |
| Starter + solenoid | K9 trigger only |
| Alternator | Rating unread `[V-002]` |
| Ignition coils ×2, igniters ×2 | O12 |
| Fuel level sender | A7, ohm range unknown `[V-037]` |
| Door pin switches | Already switch-to-ground |
| Brake pedal switch | Becomes a signal input |
| Turn / wiper / headlight stalks | Become resistor ladders |
| Ignition switch | A16 ladder `[T-023]` |
| Inhibitor switch | Crank interlock + reverse `[D-071]` |
| A/C system entire | Factory circuit, untouched |

---

## 7 · How to design against a part you haven't chosen

Four rules, applied throughout this project:

1. **Size the channel for the worst plausible part**, not today's part. O5 is
   sized for the Aeromotive, not the Carter.
2. **Wire gauge comes from voltage drop and mechanical robustness**, not from
   current (D-016). This is why the LED switch shrinks nothing.
3. **Terminate every cavity now** (D-004). A capped spare costs a wire; a
   re-pin costs a housing and a teardown.
4. **Set soft fuses at migration**, from the part actually fitted that day —
   never from an estimate, never from Phase 0.

The consequence: **an unchosen part blocks almost nothing.** It only blocks its
own soft-fuse value, which is the last thing set anyway.

---

## Open questions from this page

| ID | Question |
|---|---|
| **Q-044** | **Headlight strips: inside the pop-up buckets, or fixed with the pop-ups deleted?** The largest simplification still on the table |
| Q-037 | Cluster display format |
| V-060 | New mirror conductor count and control protocol |
| V-061 | Radar sensor interface |
| V-052 | Battery heater draw |

---

## UPDATE 2026-08 — custom tail lights (see `TAIL-LIGHTS.md`)

The rear lamp change is no longer "LED bulbs in stock housings." It is a
**custom-built lamp** and it supersedes the tail/brake/turn/reverse rows above.

| Circuit | Now | Becoming | Status |
|---|---|---|---|
| Tail / brake / turn, rear | Incandescent in stock housings | **Custom LED strip**, ~2 cm tall, stock width and position | `PENDING` |
| Reverse | 27 W incandescent | **White LED section**, inboard end of the same strip | `PENDING` |

**Design constraint that sets the shape:** FMVSS 108 requires 50 cm² minimum
effective projected luminous lens area for a stop lamp or rear turn signal. A
1 cm strip across a 30 cm aperture is only 30 cm² — 40% short. **~2 cm clears it.**

**New hardware this introduces:**

| Item | Note |
|---|---|
| DOT/SAE-compliant LED modules, red and white | `[V-064]` photometry is the hard part, not area |
| Driver PCB ×2 | `[Q-046]` — takes tail/brake/turn/reverse as inputs, handles intensity ratio and turn override locally |
| Custom housings ×2 | Sealed, stock mounting |

**Wiring unchanged.** Five conductors per side — tail, brake, turn, reverse,
ground — which the existing L4-M branch already carries. **This does not touch
the pin plan.**

**Keep the stock lamps intact** until the strips are proven on the road.

### Front headlights — related, still undecided

`[Q-044]` remains the larger question: thin LED strips inside the pop-up buckets,
or fixed in the nose with the pop-ups deleted. The tail light work is a good
rehearsal for it — same fabrication problem, lower stakes, no mechanism involved.

---

# Running on stock bulbs — yes, and it's the easy case

*Added 2026-08. Answers: can the car be migrated and driven on the original
incandescent bulbs before any lighting change?*

**Yes.** Nothing in the pin plan, gauge selection or channel allocation assumes
LED. The original estimates were **worst-case incandescent**, and the LED
conversion only ever made those numbers smaller.

## Headroom on every lamp channel, incandescent

| Circuit | Ch | Rating | Incandescent draw | Headroom |
|---|---|---|---|---|
| Tail / park / marker / plate | O6 | 15 A | ~4.4 A | 71% |
| Brake | O7 | 15 A | ~3.9 A | 74% |
| Turn, per side | O17 / O18 | 7 A | ~4.2 A | **40%** — tightest |
| Reverse | O19 | 7 A | ~3.9 A | 44% |
| Interior + glovebox + luggage + illumination | O20 | 7 A | ~2.5 A | 64% |
| Headlight LOW | O2 | 25 A | already LED | — |
| Headlight HIGH | O3 | 25 A | already LED | — |

**Wire gauge is unaffected.** D-016 sets gauge by voltage drop and crimp
robustness, not current. Every one of these is comfortably inside its wire.

## The one thing that actually needs configuring: inrush

A cold filament draws **8–12× its steady current for a few milliseconds.**

| Circuit | Steady | Cold inrush |
|---|---|---|
| Turn, per side | 4.2 A | ~40 A momentary |
| Tail bus | 4.4 A | ~45 A momentary |
| Brake | 3.9 A | ~40 A momentary |

A soft fuse set to a flat 5 A will trip on the first flash. **Configure the
inrush window** — the PMU supports a current limit with a time characteristic,
and for lamp channels the limit must tolerate a short spike well above steady.

This is a config task, not a hardware problem, and it belongs in Checklist 2.14
alongside the flash logic.

**Turn signals are the case to get right**, because they cycle constantly. After
the first flash the filament stays warm and subsequent inrush is much smaller —
but the first one is real.

## The dual-filament bulb is exactly what this design wants

Worth noticing: **the stock 27/8 W rear bulb has two separate filaments.** O6
feeds the tail filament, O7 feeds the brake filament, and they share a ground.

**No backfeed. No diodes. No driver board.**

The backfeed problem that drove `[Q-046]` and D-111 only exists for the *custom
LED strip*, where one array has to serve both functions. On stock bulbs the
two-channel design maps perfectly onto the two filaments.

## What this means for sequencing

**You can migrate the entire car on stock bulbs and drive it.** The custom tail
lights and the headlamp change become a separate later project rather than a
dependency of the rewire.

That fits the same reasoning as D-081 — the car should be finished and driving
before optional subsystems join.

| Phase | Lighting state |
|---|---|
| 6 · Migrate | **Stock bulbs.** Set soft fuses from measured incandescent draw |
| 7 · Factory harness out | Stock bulbs |
| 8 · Shakedown | Stock bulbs. Car is finished |
| **Later** | Custom tail lights, headlamp units. **Re-measure and re-set soft fuses** |

## The one thing to remember at changeover

**Soft fuses set against incandescent will be far too generous for LED.** A tail
circuit set at 6 A won't protect a 3 A LED load. Re-run the measure-and-set step
(Checklist 6, per-circuit step 5) on every lamp circuit after any bulb change,
and log it in `MIGRATION-LOG.md` as a second pass.

## What does NOT work on stock bulbs

Nothing. There is no part of the design that requires LED.

The only feature that ever depended on it was bulb-out detection, and that was
dropped entirely (D-047) — which, incidentally, makes incandescent *easier*,
since detection thresholds were the one thing filament draw would have
complicated.

---

# SCOPE CHANGE 2026-08 — lighting is a separate project (D-123)

**Everything above about LED conversion, custom tail lights and headlamp changes
has moved to `02-PROJECTS/lighting-body/`.**

## What this project's lighting scope actually is

**Stock incandescent bulbs, in stock housings, on new wiring.** That's it.

| Item | This project | Lighting project |
|---|---|---|
| Channel allocation O2/O3/O6/O7/O17–O20 | ✅ | |
| Wire gauge, connectors, cavity assignments | ✅ | |
| Turn signal flash logic | ✅ | |
| Inrush configuration (D-120) | ✅ **needed for filament** | |
| Soft fuses from measured incandescent draw | ✅ | |
| Working lamps on stock bulbs | ✅ | |
| LED bulb conversion | | ✅ |
| Custom tail light strips | | ✅ |
| Headlamp unit change | | ✅ |
| Driver PCBs | | ✅ |
| Second-pass fuse reset after bulb change | | ✅ |

## Parts still changing in THIS project

With lighting removed, the electrical project's parts changes are:

### Death dates — works now, won't later

| Item | State | Replacement | Design implication |
|---|---|---|---|
| **Fuel pump** | Carter P4070, working | Aeromotive Phantom 340 eventually | O5 sized for **8–12 A**, not the Carter's 1–3 A. `L4-P` carries a spare heavy cavity |
| **Blower motor** | Original, failing | Not chosen | O16 sized for **worst-case 20 A** with the flyback diode |

### New — did not exist on the car

| Item | Note |
|---|---|
| **Fuel-door solenoid** | Never existed. Needs sourcing `[T-032]` |
| **Heated seats** | 2 × ~4 A elements |
| **Cooled seats** | 2 × fan modules |
| **Heated washer nozzles**, **wiper park de-icer** | Comfort bus |
| **USB-C ports** | Replacing the deleted lighter |
| **Radar sensors** | Concealed front and rear, DCU-driven `[V-061]` |
| **CAN keypad** | Ecumaster 8-key — chosen |
| **DCU + ICU** | Teensy 4.1 ×2 — chosen |
| **Oil temperature sender**, **VSS** | New ICU inputs |

### Replacing broken or missing

| Item | Why |
|---|---|
| **Hatch latch switch** | Original broken `[T-033]` |
| **Side mirrors** | Larger, heated, digital control. Factory control dead `[V-060]` |
| **Head unit** | Double-DIN |

### Deleted

Cigarette lighter · cruise control · rear wiper · power antenna · headlight
cleaner · all cold-start hardware · stop light checker · Control Processing Unit ·
dimmer rheostat · retract switch · horn relay · interval wiper unit · all 15
factory fuses.

## Bulbs carried forward unchanged

Every lamp keeps its **stock incandescent bulb** through this entire project.
They are consumable, they work, and replacing them is the next project's job.

---

## UPDATE 2026-08 — faults change three part statuses

| Item | Was | Now |
|---|---|---|
| **Blower motor** | `DEATH DATE` — original, failing | **`DEAD` — confirmed not working (K-023).** Replacement required, not optional. O16 sized from the replacement's spec (D-126) |
| **Washer pump** | Assumed carrying forward | **`DIAGNOSE` (K-022).** Not working. Pump, wiring or switch unknown. If the pump is dead it joins the parts list |
| **Defrost switch** | Moving to the CAN keypad | **Broken (K-020).** Doesn't change the plan — the switch was already being deleted. Note it so nobody tries to reuse it |
| **Retractor switch** | Deleted by D-038 | **Broken (K-021).** Confirms the deletion costs nothing. Nobody was going to reuse it |

### New sourcing tasks

| Item | Task | Note |
|---|---|---|
| **Blower motor** | `[T-038]` | Confirmed dead. Source before Phase 6 — it's on the migration list |
| **Washer pump** | `[T-039]` | Only if diagnosis shows the pump itself is dead |

### What this does NOT change

**Nothing in the pin plan, wiring or connector design.** All four faults are in
devices or switches, not in the architecture. Three of them were already being
deleted or replaced.

The blower is the only one that adds a purchase, and it was already flagged as a
death-date item — this just moves it from "eventually" to "before Phase 6."

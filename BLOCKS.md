# BLOCKS

*The one page Camden writes in.*

Type your answer after `**SOLVE:**` - on that line or the lines under it. Plain
sentences, any length, no markers to keep. Blank means unanswered. Skipping one costs
nothing: it stays open and comes back.

Nothing here is ever regenerated, and nothing but you writes in it.

**This page holds only what is still open.** Once you answer a block, it is applied
through the record, becomes a decision whose `closes` names it, and is then deleted from
here — `DECISIONS.md` is where a settled question lives, with the reasoning and the
consequences. So a short page means a short queue, not a lost history: search
`DECISIONS.md` for a `BLK-` id and you will find the ruling it became.

An answered block that is not yet applied is advisory - it never refuses a commit.

## OPEN

### BLK-015 · 01-luxury

**Ask** Which DOT-compliant headlamp unit goes in the retained pop-up buckets?
**Why** The bucket shape decides the part, and the part decides whether an adapter plate is bought. Nothing electrical changes either way - the feed and the wink relays are the same for all three.
**Options**
- (a) 4x6 rectangular LED on an adapter plate - needs the plate made or bought
- (b) 5x7 rectangular LED on an adapter plate - same, larger aperture
- (c) 7-inch round LED with a rectangular-looking element, no plate - simplest, no fabrication
**Recommend** (c), unless the bucket turns out to be already rectangular - see the work row for V-066, which looks at what is fitted today.
**Stops** The headlamp line in the luxury cart. Nothing in the electrical build waits on it.
**Carried from** Q-048
**SOLVE:**

### BLK-020 · 01-luxury

**Ask** Which mirror pair - the factory FB power mirror, or a universal 3-wire set?
**Why** You said search, so here is the search. **Nothing on the market meets the original spec as sold.** Heat is the reason: the compact and universal aftermarket does not make a heated power mirror at all, and the FB's own factory power mirror - a real option on 1981-85 cars - was never offered heated in any year. That is now settled separately: D-332 puts heat on a bonded resistive pad (~$8-20 the pair) on the F14 feed, which is what Mazda itself did on the RX-8, motors on three pins and the heater on two of its own. So this question is only about the **motors**, and three candidates survive that filter.
**Options**
- (a) **Factory FB power mirror pair, used OEM** - ~$75/side at autopartone, ~$125/side on eBay, plus the console switch ($40-60) and the chassis pigtail ($48). Direct fit, correct shell, correct connector, and your five conductors at the sill *are* this harness. Zero drilling, zero adapter plate, zero aesthetic risk. **The catch is real:** I could not open the FB wiring diagram, so whether it is two motors or one motor plus an electromagnetic clutch is **unverified** - the pre-1986 Porsche 911 and the VW Vanagon both use a clutch on a similar conductor count, and a clutch cannot be driven by a plain joystick. Used only, 40-year-old motors, glass often hazed. No reproduction exists; Mazda heritage covers FC and FD only
- (b) **AutoStyle K3 universal set, part AC KT13E** - EUR 116 the pair from voorwindenparts, roughly $150-190 landed. This is the one product where the manufacturer sells the 3-wire scheme as its own part number (the 4-wire BMW variant is AC KT13E4), and AUTODOC's spec table lists it as 3 wires. Set is L+R and deliberately excludes the adjuster knob, which suits your panel. **Catches:** needs drilling and almost certainly a wedge plate for the door curvature; head dimensions are unpublished by everyone, so size is a real unknown; EU import
- (c) **Smart Fortwo 451 mirror, 2008-2015** - $65-110 each. Among the smallest heated power heads sold, no memory, no fold, no turn signal, 5 pins that read as 3 motor + 2 heat. **Catches:** the pinout is inferred, not verified; needs an adapter plate and a Mercedes connector; sold per side; do not cross-shop the 2016+ 453, which added sensors
**Recommend** (a), gated on one test you can do in an afternoon: `W-332` is on your list - get one used FB head and ohm it out or bench it, and see whether it has two independent motors or a motor plus a clutch coil. If two motors, (a) wins on fit and connector alone and nothing else comes close. If it is a clutch, go straight to (b), because it is the only candidate where the wiring scheme is a part number rather than a hope - and then confirm the K3 head size before ordering from the EU.
**Stops** The mirror line in the luxury cart, stage S5, and the door-leg conductor count if a candidate ever needed more than three per side.
**Carried from** Q-300 → BLK-016, where you answered "(b) — do the search". This is that search; BLK-016 is closed and gone from this page.
**SOLVE:** 1982 Mazda RX-7 side mirrors utilize a single motor plus a clutch coil (magnetic solenoid)

### BLK-026 · 00-electrical
**Ask** The windows now share O1 with the pop-up bus, whose retry class is GUARDED — do they get their own output, a conditional retry class, or neither?
**Opened** 2026-09-13
**Why** This is the item your BLK-021 answer said "needs its own ruling", written up so it does not get lost. `O1` is the pop-up motor bus: `L4-P 3` feeds the window motor bus at the sill through K5–K8, and the same output feeds K1/K2 for the pop-ups. D-335 put `MOTOR_BUS` in retry class **guarded** — one retry, then off and flag — for a specific reason: an overcurrent on a pop-up means something is physically in the way, and a hand is the something, so retrying is the wrong answer and the D-186 obstruction timeout is the real handler.

A window is a different animal on the same wire. **A window reaching its stop is a legitimate current spike every single time it closes**, and it reads exactly like a pop-up obstruction. Under `guarded`, the third or fourth normal window close of the day latches the channel off and flags a fault — and takes the pop-ups with it, because they are the same output. Making the windows work parked (D-350, D-354) means this now happens with the car asleep in a car park, not just while you are sitting in it.

There is no headroom to hide in: D-279 already records `O1` at the 25 A channel ceiling against a measured 26 A both-sides pop-up stall (LD08), which is why it leans on the timeout rather than the current trip.

And the supply side is settled and unhelpful: D-354's scan found **no free PMU output**. O13 and O14 are the only unused ones and both are the LS swap's reserves, so spending one forecloses something you have said you want — which is why that is your call and not mine.
**Options**
- (a) **A conditional retry class.** The PMU knows which consumer it just commanded, so `MOTOR_BUS` behaves as `guarded` during a pop-up cycle and as `motor` (5 retries at 15 s, no latch) during a window command. Costs nothing physical — it is an expression and a class change. The cost is honesty: one output now has two protection personalities, and the config is harder to read and easier to get wrong. It also does nothing about the two loads sharing a 25 A ceiling.
- (b) **Give the windows O13 or O14**, the LS swap's reserves. A real output, 25 A, its own retry class, its own soft fuse, and the pop-ups keep `guarded` untouched. Costs a swap reserve — and the pins are wired to `L1-P 2 / L1-P 3` at the post for the engine bay, so the window feed would have to be re-terminated from L1-P to `L4-P 3`. **Forecloses** a channel the LS/CD009 swap is holding.
- (c) **A second PMU.** The module supports up to five in tandem. Solves this and the next three channel arguments at once. Several hundred dollars and a second unit to mount, wire and configure — far past what this question is worth on its own, but it is the honest answer to "we are out of outputs" if that keeps happening.
- (d) **Neither — keep the windows key-on only.** They stay on O1 under `guarded`, and the PMU refuses a window command unless `A16 >= ACC`, so a stop-spike only ever happens while you are in the car and can see the flag. Costs the parked window, which D-350 deliberately did not build a timer for anyway.
**Recommend** (a), with (d) as the fallback if the config gets ugly. The conditional class is free, it is reversible, and the PMU genuinely does know which consumer it commanded — this is the kind of thing a programmable module is for. Not (b): spending an LS reserve on power windows is the wrong trade against a problem that config can solve, and the re-termination is real work. Not (c) yet: one crowded output is not worth a second module, but if BLK-026, a future window output and the swap all want channels, that is the moment to price one.
**Stops** `logic` MOTOR_BUS's retry class and expression, `rules` retry-class (whether a class may be conditional at all), and the S6 window stage in the luxury package. Nothing physical — the harness is the same either way, which is why this can wait until the config is written.
**SOLVE:** follow recommendations

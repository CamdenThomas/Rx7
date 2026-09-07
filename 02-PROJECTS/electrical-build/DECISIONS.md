# DECISIONS — why the design is the way it is

Every decision that still governs this project, grouped by the system it touches. Each entry is the decision in bold, then the reasoning. IDs are permanent: a decision is never edited, it is superseded by a newer one that names it, and the superseded one leaves this file. The full chronological log, superseded entries included, is `../../99-ARCHIVE/Electrical/2026-09-02_electrical-pmu/05-PROCESS/DECISIONS-chronological.md`. Decisions that belong to the luxury package or the engine swap live in those projects' own `DECISIONS.md`.

**Latest:** D-212 wire scheme · D-213 one wiring project · D-214 no plate · D-215 the presentation defaults adopted · D-216 two fuse blocks · D-217 one L2 power housing · D-218 spares plugged · D-219 DT for the ports · D-220 the 2026-09-02 order changes · D-221 tables are the record · D-222 the shopping list is the carts · **D-223 13 A output caps · D-224 both busbars covered · D-225 one-touch wipe · D-226 ignition layout confirmed · D-227 the wideband stays, the gauge goes · D-228 A/C is on its own belt · D-229 no battery box · D-230 the amp comes off the PMU · D-231 no interim AFR** (2026-09-03) · **D-234 tapered posts · D-235 boots only · D-236 the whole amplifier goes · D-237 200 A MRBF confirmed · D-238 cable acceptance at the cart · D-239 the battery measured · D-240 transit never gates crank · D-241 C10 is 2 AWG · D-242 F1 to 10 A · D-243 O2/O3 at 13 A** (2026-09-04) · **D-244 the wideband gauge is the controller, AFR on CAN2 (supersedes D-227, D-231) · D-245 the disconnect moves to the negative · D-246 1/0 starter feed and a dedicated cranking return · D-247 two-circuit brake switch · D-248 the parasitic-drain rules** (2026-09-04).

## Contents

1 · Architecture and scope · 2 · Power backbone and battery · 3 · The dash node · 4 · Outputs, soft fuses and logic · 5 · Switches, ladders and inputs · 6 · Legs, connectors and grounds · 7 · Wire, labels and materials · 8 · Build sequence · 9 · The record itself

---

## 1 · Architecture and scope

**D-001 — ECUMaster PMU-24 DL over a conventional relay/fuse box.** Accepted about $2,500 of premium for per-channel current logging, soft fuses set from measured draw, and logic without physical relays.

**D-002 — Ionic S9 heated lithium battery, rear-mounted.** Sold as "Ionic Lithium 12V S9 — Car Post Starter Heater Battery"; some listings say *S9H*. Same product. This project says "S9". The heater is why this model is right for a cold, high-altitude car: lithium must not be charged below freezing, and the heater warms the cells so it can (D-060).

**D-007 — Baseline pinned for the current 12A / Weber configuration; O13 and O14 (25 A) reserved for an engine swap's ECU and cooling fan, wired to the engine leg and capped.** The engine leg carries the reservation; its design lives in `../engine-swap/`.

**D-081 — The car drives fully on the PMU with plain switches, the factory harness comes out, and the build completes — then any module joins.** Modules add capability to a finished car; they are never a dependency for it starting, running or being legal. This is the whole reason the luxury package is a separate project.

**D-131 — The windows are manual.** This car has no power-window motors, switches or wiring; the factory diagram's I-06/I-07/I-09/I-11 describe an option it does not have. Power windows are a luxury-package item. Nothing is deleted for it — every window conductor is run and capped (D-004), K5–K8 sockets and F8/F9 positions are provided at the sill, and adding motors later is plug in, populate, enable.

**D-004 — All 39 PMU cavities are terminated at build time; reserved channels get real wire to the right housing and are capped there.** The 39-way connector is assembled once and never reopened.

**D-119 / D-124 — The car migrates and drives on stock incandescent bulbs.** Every lamp channel has 40–74 % headroom on filament bulbs, so nothing in the pin plan assumes LED. The custom tail lights, the headlamp change and the LED conversion are luxury-package scope; D-122 (soft fuses re-set after any bulb change) travels with them.

**D-209 — The column combination switch stays; every other switch in the car is replaced.** They are all broken or near it, and the dash opens once. Stays: E-01 LIGHT + DIMMER, F-02 TURN + HAZARD, D-03 wiper stalk — all laddered. The horn stays on the steering pad. Bought new: wink switches ×2, brake pedal switch, door-pin plungers, the ignition switch (electrical portion), the blower motor, resistor and speed switch.

**D-210 — No ECUMaster keypad; DP-KEY is a generic control-panel drop.** CAN2 H/L, switched +12 V off O10, ground — the universal set, so whatever panel the luxury package builds plugs in. Consequences accepted: the rear defogger has no trigger this build (O4 wired, configured, disabled); the hatch keeps opening on its key. A hardwired defog switch on a spare L3-S2 cavity is the fallback if a winter without one is worse in practice than on paper.

**D-211 — The A/C system comes out; no cooling until the swap engine.** Compressor, bracket, belt, condenser, receiver/drier and lines are removed (a shop recovers the refrigerant first — venting it is illegal). The blower, heater core, HVAC case, ducts and blend doors stay, so heat, defrost and ventilation are unaffected. Electrically all subtractions: F4 and K10 deleted, the factory interlock chain leaves with the hardware, no cavity moves. **Nothing is capped for it in the engine bay** — the engine leg carries only what the engine on the mounts needs and is rebuilt from scratch at a swap. Its return is `../engine-swap/`.

**D-228 — The A/C compressor runs on its own belt; the D-211 strip is purely subtractive.** Confirmed at the crank pulley, 2026-09-03. Nothing else is driven off that belt, so removing the compressor and bracket needs no shorter belt and does not touch the alternator or water-pump drive. Answers V-097.

**D-202 — One teardown: everything is bought now; measurements confirm before cutting, not before buying.** The interior comes apart once. Wire is bought with a 1.5× margin because the routes are unmeasured at order time; the dash envelope, the routes and the pop-up ohm check gate *cutting*, never purchasing. The drive-home rule survives throughout.

**D-194 — Configure in the car; there is no bench phase.** The PMU is mounted, powered from the new backbone through a 5 A fuse (D-145), and configured over CAN1 with every output disabled before any circuit migrates. Four bench-era rules survive as hard requirements: the 5 A first-power-up fuse; 120 Ω at both CAN1 ends or the client never connects; three practice crimps pull-tested before any real crimp; one circuit at a time, the car drives home every day.

**D-213 — One wiring project.** `electrical-build/` owns the harness — design, shopping, install — as a three-step guide with `DECISIONS.md` and `QUESTIONS.md` at its root. `luxury-package/` owns every future feature (heated/cooled seats, the digital cluster ICU, the climate module DCU, the control panel, defog trigger, mirrors, windows, sound deadening, LED lighting); `engine-swap/` owns everything that changes with the engine (ECU, CAN drop, in-tank pump, A/C's return, transmission, axle). The old `electrical-pmu/` tree is dissolved: its history and process files are archived under `../../99-ARCHIVE/Electrical/2026-09-02_electrical-pmu/` and stay linkable; its firmware and module designs moved to the luxury package. Answers Q-072.

---

## 2 · Power backbone and battery

**D-061 / D-091 — The starter feed and the PMU feed are separate runs from the battery post; the PMU feed is 2 AWG.** Cranking pulls 300–500 A briefly and cannot pass through a Class-T sized for the module feed. The master disconnect sits in the PMU leg, so opening it isolates the electrical system while the starter cable stays passive. 2 AWG (not 4) because it is sized for the swap engine, not the 12A — about $40 more now against pulling the tunnel a second time.

**D-062 — Main protection is Class-T (Blue Sea 5007100 block, 5114 150 A fuse), mounted as close to the positive post as physically possible.** LiFePO4 delivers enormous short-circuit current and Class-T is the only common fuse with the interrupt rating to break it. The cable between post and fuse is the one length that can never be protected — keep it inches long. Not economised, ever.

**D-203 — The starter run is protected by an MRBF (Blue Sea 5191 holder, 5187 200 A) on the post; the alternator charges through the starter cable via F18 (100 A MIDI) at the starter stud, as the factory did through its fusible link; K9's contact feed is F17 (30 A MIDI) at the same stud.**

**D-198 — The alternator gets its factory-spec excitation circuit: O12 → F15 (7.5 A) → L1-S1 2 → alternator BW; the charge-lamp sense WB gets its own conductor, L1-S2 8 → DP-CLU 8.** Reading factory sheet A exposed that an earlier plan had repurposed the BW feed as a sense input — the new harness would never have excited the alternator at all. This is also the prime suspect for the observed no-charge (D-179: 11.4 V at idle): the factory BW path ran through the emissions-era connectors the delete disturbed. The unit is kept and judged at commissioning on correct wiring; replaced only if it still refuses to charge.

**D-063 — The battery mounts on a backing plate under the floor, not through sheet metal alone.** A 15 lb mass with live terminals becomes a projectile in a crash; the plate turns a tearing load into a shear load. NOCO BG27 box (D-207), hold-down, M8 grade-8 hardware.

**D-229 — No battery box.** Camden's call, 2026-09-03: the NOCO BG27 leaves the design and the Amazon cart. The backing plate, hold-down and M8 grade-8 hardware of D-063 still carry the crash case — the box was never the structure. What the box *did* provide and now has no owner is terminal insulation and debris protection for a live post in an open cargo bin, so a replacement means of covering the terminals is required before the battery is installed (`Q-103`). Supersedes the box in D-063 and D-207, and the "in a NOCO BG27 box" wording in `01-DESIGN/DESIGN.md` §2. Answers V-093.

**D-064 — A pull string goes into the tunnel beside the 2 AWG feed.** The rear leg follows the same route later, and adding it without the string means dropping the console again.

**D-145 — First power-up of the dash node is through a 5 A fuse in the main feed, not a bench supply.** Enough for the PMU to boot and talk over CAN; anything shorted blows a $2 fuse instead of melting 2 AWG. Verify, then fit the Class-T.

**D-203(g) / D-207 — Fine-strand copper welding cable for the 2 AWG runs (loomed and grommeted), closed-barrel tinned lugs hydraulically crimped; bought as fixed lengths 45 ft red / 25 ft black.** Marine-tinned cable costs about twice as much for no benefit inside loom.

**D-234 — The Ionic has SAE tapered posts, so every battery connection is a brass post clamp with a 3/8 in stud take-off, not a ring lug on a stud.** Camden looked, 2026-09-04, answering `V-053`. The consequence is that the positive clamp's stud becomes the one mechanical junction carrying the MRBF holder (starter feed), the 2 AWG feed to the master disconnect, and — after D-236 — the new audio system's own fused line. That rules out a stamped parts-store terminal: it needs a real stud with real thread. Confirm at the cart review that the Blue Sea 5191's mounting foot lands on it. P095 joins the Amazon cart.

**D-235 — The terminals are covered by boots and nothing else.** Camden's call, 2026-09-04, answering `Q-103`. The cargo bin is an isolated compartment with its own lid, so the debris case D-229 opened is already covered; boots handle the tool-across-the-post case for cents. **No fabricated cover panel** — deliberately, because every layer over the battery is a layer to strip off at the roadside for a jump start, and boots pull off by hand. The battery-cover stock leaves the C2 hardware-store trip. D-063's backing plate, hold-down and M8 grade-8 hardware are untouched — they were always the structure. P094 joins the Amazon cart.

**D-237 — The 200 A MRBF is right for the starter feed; no upsize.** Answers `V-094`. A 12A's starter pulls 300–500 A for the moment of engagement and settles to roughly 150–250 A while it spins; MRBF curves run seconds at 3× rating and minutes at 1.5×, so even a long flooded-rotary crank sits inside the curve while a genuine dead short still clears in milliseconds. The 250 A (5188) would buy nothing and would sit further above the cable's own rating — this fuse protects the cable, not the starter.

**D-238 — The 2 AWG cable is accepted at the cart on two criteria, and CCA is refused at any price.** Answers `V-095`: the listing must state **≥ 90 °C insulation** and **100 % copper**. Camden asked for this to ride on the cart review rather than become an errand, so it is a line in the review; if the carted TEMCo listing does not state both, the line is swapped before payment, not after.

**D-239 — The Ionic S9 case measures 170 W × 230 L × 190 H mm.** Measured 2026-09-04, answering `V-051`; the row is `params.battery_case_mm`. Terminals and boots stand proud of the 190 mm, so the M-4 cargo-bin mock-up is cut to the case *plus* the boot height, not to the case.

**D-241 — C10, the busbar → PMU stud link, is 2 AWG.** Found in the 2026-09-04 audit: it was drawn as 4 AWG, no 4 AWG cable or lug appears in any cart, and 4 AWG sits at its own rating under a 150 A Class-T. 2 AWG is already carted, already lugged (P064) and already in the hydraulic crimper's dies. Eight inches of heavier cable costs nothing and deletes a missing part that would not have been noticed until the backbone weekend.

**D-245 — The master disconnect moves to the battery negative.** Camden's call, 2026-09-04, answering `Q-105`. In the PMU leg it isolated the module and nothing else: the MRBF branch kept the starter B+ stud live, and with it F17's feed to K9 and F18's to the alternator B+ — three energised studs in an engine bay somebody had just "isolated", and eighteen feet of live cable under the car. Between the negative post and the rear ground stud, opening it takes the return away from every positive fault in the car, starter cable included. The Class-T stays on the positive at the post where it belongs. `backbone` B1/B5, `cables` C01/C02/C05 and `grounds` G24 are re-drawn. The switch (Blue Sea 9003e — **e-Series**, not m-Series as the part row said: 350 A continuous, 1500 A cranking) now carries the starter return, which that cranking rating covers with room. Nothing is bought.

**D-246 — 1/0 for the starter feed, and a dedicated 1/0 cranking return from the rear stud to the engine block.** Camden's call, 2026-09-04, answering `Q-106` — *go bigger and safer for both*. The feed settles an ambiguity the data carried in two rows ("1/0 (or 2 AWG)") against a cart that bought neither consistently: 18 ft of 2 AWG costs about 2 V at 400 A, and 1/0 hands half of that back on the engine that is hardest to start when it is flooded. The return is the more important half. `B5` + `B6` as drawn sent 400 A of cranking current across the whole unibody, through 44-year-old spot welds and seam sealer, on a shell whose rust extent is unsurveyed (`K-007`) and which has already produced one shared-ground fault (`K-008`); the factory never asked the shell to do this, because the battery was in the engine bay. `B7` / `C11` is now a dedicated 1/0 from the rear stud forward to the block, and `B6` stays as the block-to-chassis bond rather than the main return. Both cables are pulled on the same backbone weekend, through the same tunnel, once. Cart: P096 (25 ft 1/0 red) and P097 (30 ft 1/0 black) join, P098 carries the 1/0 lugs, P065 drops to the 6 AWG lugs alone, and the 2 AWG lines fall to 25 ft red / 10 ft black — a net of roughly **+$180**.

---

## 3 · The dash node

**D-214 — No backer plate and no sealed box. The dash node mounts on one or more small carrier panels, low in the dash, laid out with the parts in hand.** Camden's call, 2026-09-02: a sealed box would be too bulky for the footwell shape; the components will be spread around the dash floor and centre stack once their real sizes can be tried in the space. The electrical design is unchanged by the split — every conductor is the same whether pieces share a panel or not. The 12 × 24 in aluminium sheet left the order; panel stock comes from a hardware store after the measurement day. Supersedes D-005 (single removable plate) and the plate-layout drawing (archived).

**D-003 — Two-tier connector architecture.** The 39-way SICMA is a *device* connector at the dash node; short wires run from it to a receptacle for every leg and drop. Legs plug into the node; the 39-way is never touched again.

**D-020 / D-030 — A true-constant bus lives off the PMU, fed from the always-hot busbar through K11 (the audio master, driven by O22 keep-alive) and block B, plus block A straight off the busbar for the laptop port, the switch supply and the courtesy lamps.** The PMU sleeps; the head unit keeps its memory on its own non-volatile store; nothing draws through the module while it is asleep except the module itself.

**D-224 — Both busbars are covered — the always-hot bar and the ground bus.** Camden's call, 2026-09-03, against the design's original "cover the hot one, leave the ground bare". A bare ground bus in a footwell is not a shock risk but it is a short risk: a dropped tool, a coin or a seat rail bridging the ground bus to the hot bar beside it is exactly the fault the Class-T has to clear. Covers cost a few dollars against a 150 A event. Buy two covered 10-gang bars, or fit Blue Sea 2718 covers to both. Answers Q-101; changes `02-SHOPPING/SHOPPING-LIST.md` §8 (the Waytek cart carries one 78250 today).

**D-230 — The amplifier comes off the PMU entirely; the head unit stays on it.** Camden, 2026-09-03. The audio system is deliberately isolated from every other powered system in the car — its only interface to anything is the pre-amp signal from the head unit to the amp — and the amp already has its own power. The head unit is different: it is woven into the body harness, it needs switched power, illumination, ground and a memory constant, and it stays a PMU load.

*Deleted:* **F5** (30 A, block B) and **L4-P 4** (12 AWG RED, amplifier constant). L4-P 4 becomes a plugged spare under D-218 — a heavy cavity with no named future feature, so it gets sealing plugs in both halves, not a capped wire. Block B goes from F1 + F5 + two spare to **F1 + three spare**.

*Narrowed, not deleted:* K11. D-020/D-030 called it "the audio master"; with F5 gone its only load is F1, the head-unit memory constant, so K11 is now the **head-unit constant master** and the O22 keep-alive latch that drives it is unchanged. The reasoning survives — the head unit must hold memory while the PMU sleeps — the name does not.

*Supersedes* D-215's "L4-P 4 is the amplifier constant". *Opens* `Q-104`: the amp is believed to draw from a rear-cabin junction, and the factory harness is removed at install §6 — if that junction leaves with it, the amp loses its feed on a day nobody is thinking about audio.

**D-216 — Two fuse blocks, not four. Block A (busbar: F2, F3, F19, F13 empty) and block B (K11: F1, F5, two spare). F6/F7 (O1 → K1/K2 contacts) and F10/F11 (O15) are deleted; F8/F9/F14 at the sill are labelled positions with no holder this build.** O1's two branches are identical 12 AWG runs carrying one function, and the output's 25 A soft fuse protects either; O15 has no load until the luxury package, which adds its own block on that output when it lands; the sill holders belong to windows and mirrors that do not exist yet. F12 stays because a shorted interior lamp must not take the illumination bus and cluster feed down with it at night. This is what was carted on 2026-09-02 (two OptiFuse BLR-504, three sealed inlines). Supersedes D-206 and D-208(f).

**D-056 — The wake network uses 1N5819 Schottky diodes (not 1N4007) with a 10 kΩ bleed from the rail to ground.** The lower forward drop matters at cold-crank voltage; without the bleed, diode leakage can hold pin 7 above threshold and the PMU never sleeps.

**D-167 — A 100 kΩ bias resistor from +5 V on A15 and A16.** These are the 12 V-side ladders, where OFF would read 0 counts — identical to a disconnected wire. The bias lifts OFF to ~90 counts so the two are distinguishable. Same principle as D-053: no valid state may sit at an extreme.

**D-186 — Pop-up drive is one run relay per side, K1 (LH) and K2 (RH); no H-bridge.** Camden confirmed the motors spin one direction only (the crank flips the lamp each half-revolution; the internal cam stops it at each end), and that the factory indicator stays lit when a motor never reaches its limit. So raise and lower are the same electrical act: energise the relay until that side's YG transit contact opens again; 4 s still-closed is an obstruction fault. 87a to ground keeps dynamic braking for free (D-057). Whether K1/K2 drive R and RY bridged or R alone is the ohm check on the measurement day (install M-3).

**D-189 — K1 and K2 coils are fed from O1, each in series with the *opposite* side's wink-switch NC pole.** Holding a wink opens the other side's coil return, so when the PMU runs the half-cycle only the winked lamp moves; O1 stays both supply and command, keeping pop-up telemetry. The wink NO poles feed the A8 ladder (D-215), so a wink also wakes the PMU with the key out.

**D-182 — The washer pump runs on its own relay K12: coil from O10, coil return through the wiper stalk's WASH contact, contact fed from O8.** The pump runs only while the driver holds WASH; O8 stays on for two more sweeps after release.

**D-148 / D-208(e) — Start relay K9 is a sealed mini ISO relay (Picker PC792E-1C-C-12S-DN-X in a Chief 75340 weatherproof socket) on the inner fender, not at the starter.** The relay keeps solenoid current off the PMU and does not need to be adjacent; pull-in is 15–25 A and 10 AWG over a few feet loses almost nothing. Mini, not micro, because micro has no weatherproof housing in the catalogue.

**D-215 — The presentation design's defaults are adopted as the design, pin by pin, wherever they differ from earlier decisions.** When the three-step guide was written (2026-09-01) it resolved every open electrical item with a sensible default, and those defaults are what the carts were built to. Where they differ from older entries, the guide wins: A3 reads brake pedal *and* wiper park as a 4-state ladder (D-182 had left park sense capped) · A8 reads hazard, horn, wink L and wink R summed — hazard 4.7 kΩ, horn 8.2 kΩ, wink L 18 kΩ, wink R 33 kΩ (D-190 had horn 12 kΩ and winks pin-7-only) · A4/A5 inhibitor contacts through 8.2 kΩ with 47 kΩ baselines at the L2-S plug (D-187 had 12 kΩ) · the +5 V reference stays at the dash node, used only for the two bias resistors — nothing in any leg uses +5 V (D-197's 100 Ω pull-up at the sender is not fitted; A7 observes the factory fuel-gauge node through a 1 MΩ pull-down, read in the car as a three-point lookup) · the door and A8 wake stages are two NPN sense stages at the dash node (D-188 had a PNP at the sill) · L4-P 4 is the amplifier constant (D-181's O15 → sill feed is not run; mirror heat waits on F14) · L4-M 3/4 are the hatch and fuel-door solenoids, capped (D-180's O10 branches wait for the panel) · DP-ICU is the 12-way sensor drop and DP-DCU the 6-way (D-083) · DP-CLU feeds the factory cluster from day one · the private DCU↔ICU pair (D-087) is not run — the luxury package can add it behind the same bezel · O2/O3 are filament headlamps.

**D-236 — The factory amplifier and every wire that serves it come out; the replacement audio system is standalone off the battery posts.** Camden, 2026-09-04, answering `Q-104` — and confirming D-230 by a different route than expected. The stock amp's feed cannot be traced because a previous owner spliced the dash badly, so it is *not* traced: the amp, its power lead and all the factory speaker wire leave with the factory harness at install §6, and nothing in this project waits on finding where it fed from. What replaces it is a new amplifier beside the battery on its own fused line straight off the positive and negative posts, new speaker cable, new speakers, taking pre-amp signal from the head unit. The head unit stays the only audio load the PMU sees, exactly as D-230 left it, and L4-P 4 stays plugged.

*Two consequences that are this project's business:* the new amp's feed and return lugs land on the same posts as D-234, so the terminal stack and the D-235 boots must clear them — mock it at M-4 with the amp in place; and the head unit's own speaker outputs go unused, so nothing in the dash needs speaker-level wire.

**D-242 — F1, the head-unit constant, drops from 15 A to 10 A.** Found in the 2026-09-04 audit. F1's conductor is 14 AWG into L3-M 2, a Deutsch DT size-16 contact rated 13 A: a 15 A fuse sits outside a component's rating in the path it protects. That is precisely the finding D-223 acted on for the software caps, and this physical fuse was missed by it. With the amplifier gone (D-230, D-236) the constant carries memory and the head unit's own internal output stage, not an amp, so 10 A is generous and inside every part in the path. A drawer value; no cart change.

**D-247 — The brake pedal switch is a two-circuit switch, and the brake joins the wake strip.** Camden's call, 2026-09-04, answering `Q-108`. As drawn the brake was read only by the `A3` ladder — a ground-side input — and the brake was not a wake source, so a sleeping car with the brake pressed lit nothing: no brake lamps while it is pushed, rolled or towed. Pole 1 does the ladder exactly as before. Pole 2 is fed from the F3 switch supply, branched off `L3-S2 2` in the leg, and returns on **`L3-S1 7`** — a cavity that was a sealing plug — to **wake strip input 6** through a sixth 1N5819. The strip is 8-position and the diodes are carted twenty at a time, so the only cart change is the switch's own line, which had not been bought yet. This is also the cheapest of the audit's findings to have missed: after the pedal box is back together, adding a pole means pulling it apart again.

---

## 4 · Outputs, soft fuses and logic

**D-009 — O1 (pop-up motor bus) and O16 (blower) carry the inductive loads, because they are the only two channels with integrated high-power flyback diodes.**

**D-010 — Wipers live on O8 and nothing else does; O8 is the only channel with wiper-motor braking.** O9 is the high-speed brush. Park is software: hold O8 until A3 reads PARKED, then brake.

**D-225 — One-touch single wipe is in the wiper logic.** A tap of the stalk to LOW and back runs one full sweep and parks: `LOW held < 400 ms → one sweep to PARKED`. Software only — no wire, no part, no cost, and the A3 park state it needs is already read (D-215). Answers V-028; enters `03-INSTALL/PMU-CONFIG-SHEET.md` §3 at install §5.4.

**D-013 / D-014 — Turn signals are flashed natively by the PMU (1.5 Hz); the interval wiper unit is deleted — intermittent is a software timer on O8.** No flasher and no interval unit anywhere in the car.

**D-015 — Tail, park, side markers and licence lamps are one circuit on O6, lit in both PARK and HEAD.** Front on L2-M 7, rear on L4-M 1, spliced at the nose and the hatch.

**D-011 — O15 is a 25 A comfort bus for the luxury package (seats, mirror heat, and the like), fanned out downstream by that project.** This build runs it to L3-P 2 and caps it. Chosen over holding it as a third swap reservation.

**D-095 — The cigarette lighter is deleted.** It was the only load that could trip the channel powering the accessories; USB-C covers the function.

**D-047 / D-050 — No bulb-out detection, no load resistors anywhere, no seat-belt or key chimes.** A manual lamp check is easy; flash rate is set in software; the chimes are not wanted.

**D-038 / D-040 / D-110 — The retractable-headlight switch is deleted; pop-ups raise when the A15 ladder reaches HEAD and lower when it leaves; the only cabin controls are the two momentary wink switches; each motor's manual raise knob covers maintenance access.** The pop-ups themselves stay — K1/K2, the L2-P run feeds, the A4/A5 ladders and the winks are all as specified.

**D-164 / D-165 / D-175 — Soft-fuse rule: motors measured stall × 1.10 · filament lamps steady × 1.35 plus an inrush window · resistive cold × 1.20 · electronics steady × 1.50, rounded up to 0.5 A. Until a channel has been measured it runs at its channel cap, and the PMU's own telemetry on the new harness is the measurement.** The limit protects the wire, not the load; a guessed limit either nuisance-trips or fails to protect while looking configured. Consequence accepted: during shakedown the soft fuses discriminate nothing — a seizing motor shows only in telemetry — so the protection burden sits on continuity testing every conductor before first power and watching telemetry through the first week. Measured today: O5 fuel pump 4.0 A (D-173: steady 2.38 A × 1.5, because dead-heading the pump for a stall reading risks more than it teaches), O6 7.5, O7 9.5, O17/O18 4.5.

**D-120 / D-122 — Every lamp channel gets an inrush window before it is enabled (a cold filament pulls 8–12× for a few milliseconds; turn signals are the case that bites), and every soft fuse is re-set after any bulb change.** A tail circuit set for filament does not protect an LED.

**D-166 — The entire PMU logic is enterable before any current figure exists.** Names, decode tables, expressions, interlocks, wake, flasher, wiper timing and pop-up logic have no dependency on measurement; limits and enabling happen per channel as each migrates.

**D-183 — Interim rules until an engine ECU or cluster module puts rpm on CAN: fuel pump = key RUN; start relay = key START and the inhibitor's P/N state — no rpm term in either.** The rpm-qualified versions are luxury-package / engine-swap scope.

**D-126 — O16's blower limit comes from the replacement motor's spec, then telemetry.** The original motor is dead (K-023); the channel stays 25 A with the flyback diode, which covers any plausible replacement.

**D-210(b) — DEFOG (O4) is configured and disabled; INTERIOR is `A6 != CLOSED` with the theatre fade; there is no keypad term in any expression.**

**D-223 — The enable-at cap on O8, O9, O10 and O11 is 13.0 A, not 15 A.** The 15 A outputs reach their loads through Deutsch DT size-16 contacts rated 13 A continuous, so a 15 A software limit sits outside a component's rating for no gain: the real loads are 4–10 A and the cap only ever acts in a fault, which trips in milliseconds either way. Lowering it costs nothing and keeps every software limit inside every part's rating. O6 and O7 already sit at their measured values (7.5 A, 9.5 A) and are unaffected. Answers V-014; changes `03-INSTALL/PMU-CONFIG-SHEET.md` §5 and `01-DESIGN/DESIGN.md` §4.1.

**D-226 — The ignition layout is factory and untouched: two coils and two igniters, leading and trailing.** Confirmed by eye 2026-09-03. The four BW feeds are not individually traceable without pulling the loom, but nothing about the installation looks disturbed, so the design's assumption stands — L1-P 1 splices to BW on all four (`01-DESIGN/DESIGN.md` §12). Answers V-001. If commissioning shows a coil unfed, the splice count is the first thing to re-open.

**D-243 — O2 and O3 are enabled at 13.0 A, not the 25 A channel cap.** Found in the 2026-09-04 audit. D-164/D-175 park an *unmeasured* channel at its cap, but LD01 is not unmeasured — it is published, two 55 W lamps, 3.0 A low and 3.5 A high — and both channels reach their lamps through 14 AWG branches spliced at L2-P. A 25 A limit over a 14 AWG branch protects nothing that branch needs protecting from, and it is the same mismatch D-223 and D-232 closed everywhere else. 13.0 A is the gauge rule's own number for 14 AWG and still leaves 3.7× headroom over the published draw; the inrush window is untouched, so cold filaments are unaffected. Re-set from telemetry at migration like every other channel (D-025).

**D-248 — Three rules so a door left ajar cannot flatten the Ionic.** Camden's call, 2026-09-04, answering `Q-109`. `INTERIOR` was `A6 != CLOSED` with no timeout; the door stage is a wake source, so the same open door also held `KEEP_ALIVE` latched; and the only shed rule shed `COMFORT`, a channel with no load in this build. Together that is about 2.7 A until the BMS cuts off — the one battery state a LiFePO4 is hard to come back from, and the reason `A4` on the finishing list exists at all. Now: the interior lamp **drops after 10 minutes** with a door still open and re-arms when every door closes; below **11.5 V** the shed takes `INTERIOR` and `ACCESSORY` as well as `COMFORT`; and `KEEP_ALIVE` **releases after 30 minutes** with `A16 == OFF` whatever `A6` reads, so a failed door plunger cannot hold the module awake for a week. Config only — no wire, no part. The always-hot courtesy lamps (F19, glove box and luggage) sit outside all three by design: a stuck lid switch is still a slow drain nothing watches, which is worth knowing rather than fixing.

---

## 5 · Switches, ladders and inputs

**D-018 — Every switch input on A1–A8 is wired to ground with the internal 10 kΩ pull-up, never to 12 V. Only A9–A16 read 12 V directly, which is why the key and the headlight switch live there.**

**D-019 / D-054 — Every multi-position switch is a resistor ladder from day one, with the resistors mounted at the switch.** One return wire per ladder instead of one per position is the whole point; retrofitting a ladder onto point-to-point wiring is a re-pin.

**D-053 — No valid switch position uses a dead short.** Every state reaches ground through a finite resistor, so 0 counts means "shorted wire" and full scale means "open wire" — fault detection for the cost of one resistor per ladder.

**D-055 / D-178 — The A16 key ladder is a *summed* ladder: ACC stays live in RUN and both ACC and IG stay live in START, so each ignition-switch output feeds the node through its own resistor (ACC 33 kΩ · IG 15 kΩ · ST 6.8 kΩ) and the decode targets the combinations.** Factory sheet F confirms the closure pattern. Whether ACC holds through START only moves the START reading between ~1650 and ~1720 counts — both far from RUN — so the in-car read (D-142) writes the true window.

**D-184 — A15 is a five-state summed ladder: PARK 33 kΩ · HEAD 15 kΩ · dimmer-HIGH 8.2 kΩ fed from the HEAD side · PASS 3.3 kΩ fed direct, with the D-167 bias.** Centres 93 / 604 / 1201 / 1666 / ≥1750; smallest gap 162 counts. PASS is a superstate: while the reading is ≥ 1750 the logic holds the previous lighting state and forces high beam, so nothing inside the PASS band needs decoding.

**D-187 / D-071 — A4 and A5 are 4-state transit-plus-inhibitor ladders: the pop-up YG transit contact through 3.3 kΩ, one inhibitor contact through 8.2 kΩ (P/N on A4 for the crank interlock, R on A5 for the reverse lamps), a 47 kΩ baseline to ground at the L2-S plug so a broken wire still reads as a fault.** The inhibitor's R contact takes L1-S2 7. Caution for commissioning: the YG cam contact spent its life switching a 3.4 W lamp — confirm it reads cleanly at the ladder's 0.5 mA.

**D-197 — Fuel sender measured 6 Ω full · 31.5 Ω mid · 80 Ω empty; the sender is nonlinear, so A7 is a three-point lookup with interpolation, trued by the in-car read.** The reading method is D-215's (a tap on the factory gauge node); if it proves unstable, the channel is left unused and the cluster's gauge is the instrument.

**D-142 — Ladder windows are verified in the car, from live readings, not on a bench.** The switches must be genuinely wired for real resistances and real ADC readings to exist; the decode windows are corrected from what the client shows and saved as a new config revision.

**D-027 / D-028 — Signal wire is 16 AWG throughout (the PMU's 1.5 mm terminal is specified 13–17 AWG; 18 AWG crimps unreliably), and precision signals prefer the 12-bit A9–A16 bank.**

**D-105 — The factory blinker fault (K-008: shared-ground modulation across body studs X-13 and X-15) is not being fixed.** Every ground in the new harness is a local star node and every conductor is new — there is no mechanism for it to transfer. The old harness comes out intact and is not repaired.

**D-244 — The wideband gauge is kept, hidden, as the controller, and AFR reaches both modules over CAN2.** Camden's ruling, 2026-09-04, answering the restated `Q-102`. **Supersedes D-227 and D-231**, which both stood on a premise that turned out to be false: there is no separate controller box. The AEM 30-0300 is an X-Series *controller gauge* — the electronics that drive the pump cell, the Nernst cell and the heater live inside the gauge, so deleting the gauge deletes the instrument. What survives of D-227 is everything that mattered: the wideband stays, because a lean condition on a carburettored total-loss-oil rotary is expensive; and it runs on the **ignition** feed, so the heater is powered while cranking.

*What is built:* the gauge moves out of sight — behind the dash or in the glovebox, its face unused — and becomes a dash-node device. `F20` (7.5 A, sealed inline off O12) feeds it, the GND bus grounds it, and its **AEMnet pair joins the CAN2 splice**. AEMnet is CAN 2.0 at 500 kbps, which is CAN2's own speed, so the gauge is simply another node on the bus: it publishes, the **PMU logs AFR as a received CAN channel from first start**, and the ICU displays it when it arrives. Neither device is "first" — that was the shape of the question, and a bus does not have one. The 0–5 V output is left unused. The sensor keeps the gauge's own lead through the firewall grommet and is **never cut or extended**: the calibration resistor is in the sensor connector and the pump-cell currents are microamps against milliohms of lead.

*What this deletes:* the engine-leg pair D-231 reserved. **L1-S2 9 and 10 stay plugged**, no engine-leg conductor is added, nothing is bought, and "capped at the engine end, commissioned with the ICU" is void — AFR works the day the PMU is configured. What survives of D-231 is that there is no *dash display* until the ICU, and that is now a choice rather than a gap. It also leaves `DP-ICU 8` free, which `Q-107` wants.

*Two confirms:* the part number on the back of the gauge must show AEMnet — if it does not, the fallback is the 0–5 V output into `DP-ICU 8`, read by the ICU and republished on CAN2, with no AFR until the ICU exists; and F20's value against the kit's stated heater draw. The sensor lead is a fixed length, so where the gauge hides is settled at M-1 by whether the lead reaches the bung.

**D-240 — A4 and A5 are decoded as two independent bits, and the transit bit never gates crank or reverse.** Found in the 2026-09-04 audit. Both are summed ladders carrying a pop-up transit contact *and* an inhibitor contact (D-187/D-215), so the sum of transit + inhibitor is its own state — and `A4 == CRANK_OK` is therefore false for the second or two either pop-up spends in transit. Turn the headlights on and reach for the key inside the same movement and the start relay is refused; worse, a transit contact left closed by a stuck motor or a dirty cam refuses the start relay **permanently**, on a car that is otherwise perfectly able to run. `A5 == REVERSE` has the same shape and drops the reverse lamps while the right pop-up moves. Both expressions become the inhibitor bit alone: crank on `CRANK_OK` **or** `CRANK_OK+TRANSIT`, reverse on `REVERSE` **or** `REVERSE+TRANSIT`. Software only — no wire, no part — and it enters `03-INSTALL/PMU-CONFIG-SHEET.md` §3 with the rest of the decode. The obstruction fault (D-186) is unaffected: it reads the transit bit directly, which is what it is for.

---

## 6 · Legs, connectors and grounds

**D-029 — Four legs, cut by removal boundary, not connector convenience: L1 engine (the firewall grommet), L2 front (nose, bumper, pop-ups), L3 dash, L4 rear (tunnel to hatch, plus the sill).**

**D-032 / D-033 — Power and signal get separate housings on every leg (terminal size, noise, and service — diagnosing a switch must not break a 25 A circuit), coded `L<leg>-<class><index>`: P = 12 AWG power, M = 14–16 AWG medium, S = signal. Leg side is always the socket housing (`06-…S`), dash-node side always the pin housing (`04-…P`), so a leg cannot be plugged into the wrong half.**

**D-034 / D-052 / D-070 / D-219 — Every housing is genuine Deutsch: DTP (size 12) for `-P`, DT (size 16) for everything else, DP-DIAG and DP-KEY included.** No AMPSEAL, and no DTM: the two 4-way ports were carted as DT 4-way on 2026-09-02 so every contact in the car is size 12 or size 16 and there is no size-20 tooling. L3-S is 2 × DT06-12S + 1 × DT06-8S — cheaper and easier to source than one large housing, and a failure takes out part of the dash rather than all of it.

**D-115 / D-116 / D-117 / D-118 — DTP is manufactured in 2-way and 4-way only; size 16 seals 14–20 AWG and size 12 seals 10–14 AWG (14 AWG in a DT is at the top of the seal range — fine, no margin above); the C015 reduced-diameter seal exists if 16 AWG GXL seals loosely; secondary wedgelocks are separate parts and are in the kits.**

**D-217 — L2 has one power housing, L2-P (DTP 4-way): headlight LOW, headlight HIGH, pop-up LH run, pop-up RH run. L2-P2 is deleted.** The second DTP shell existed for reversible pop-up motors; D-186 made them single-direction, so the front needs four size-12 conductors and one shell holds them. The 2026-09-02 cart carries three DTP-4 pairs (L1-P, L2-P, L4-P). Closes the D-208(d) finding.

**D-218 — A spare cavity gets sealing plugs in both halves, not a capped wire. CAPPED is reserved for a named future feature.** A capped spare costs wire, two contacts, two labels and crimping time for a cavity nothing is planned for; a plug costs cents and the housing stays sealed. Named features (windows, mirrors, solenoids, the module drops, the swap reservations) keep their capped conductors so no later project touches the harness. 64 size-16 plugs carted. Supersedes D-022.

**D-045 / D-046 / D-134 / D-139 — The 39-way connector is 3 rows × 13, numbered left → right, top → bottom viewed at the device, with pin 1 top-left at the end furthest from the purple lock. Each row is 2 large · 9 small · 2 large: the twelve 2.8 mm cavities are pins 1, 2, 12, 13, 14, 15, 25, 26, 27, 28, 38, 39.** Confirmed on the physical part against the ECUmaster manual. Consequence: every 15 A and 7 A output sits in a 1.5 mm cavity limited to 13–17 AWG, so 14 AWG on O6–O11 is the maximum, and pin 15 (+5 V) needs the 2.8 mm 16 AWG terminal despite its small current.

**D-065 / D-067 / D-068 / D-132 — The sill node: window relays K5–K8 and fuses F8/F9 belong at the sill (dry, accessible, short motor legs), the doors get their own connector pair there (D1/D2), and the node is built now — sockets fitted empty, fuse positions labelled — even though nothing on it is live.** Building it behind a trim panel on a finished car costs an afternoon; building it now costs a few dollars.

**D-092 / D-093 — One DT06-08S per door: two 14 AWG window-motor legs, a spare, three mirror-motor conductors, mirror heat, and the door ground to the sill stud.** Independent wiring per side; the factory multiplexed mirror switch is dead and the mirrors will be new.

**D-069 — Pop-up relays stay at the dash node, not in the nose.** The nose is the wettest, hottest, most vibration-exposed part of the car.

**D-171 / D-172 — L1-S is two DT06-12S (L1-S1, L1-S2) and L3-S is three housings, allocated as the design's cavity tables show; every cavity carries a status word so a capped wire is never mistaken for a spare.**

**D-017 / D-037 — Grounds never cross a leg connector; every zone has one star node straight to bare chassis (engine block, front stud, dash-node ground bus, rear stud, sill stud); pin 25 is the only PMU ground and carries every flyback return.** The five dash-post drops are the one exception: their grounds cross a connector because they are devices inches from the node with no zone of their own.

**D-079 — CAN2's far-end 120 Ω terminator is fitted now, capped in the engine bay across L1-S1 9/10, with the PMU's software termination at the other end.** The bus is electrically correct before any second node exists; node count never sets termination.

**D-159 — The future cluster display does not cross the harness.** DP-ICU carries power, ground, CAN2, the illumination reference and the sensor taps; a display needs a high-speed bus and belongs inches from its controller behind the same bezel.

---

**D-232 — The gauge rule is set by the enable-at limit, not the channel's rating.** 2026-09-03, a clarification the automated check forced: `DESIGN.md` §13 said "12 AWG on 25 A, 14 AWG on 15 A", and four rows already broke it on purpose — the 16 AWG high-beam-indicator tap on O3 and the three 16 AWG capped module drops on O10. A wire has to survive what its protection lets through, and the protection is the software limit: 12 AWG above 15 A, 14 AWG above 13 A, 16 AWG at 13 A and below. A 16 AWG tap off a heavier feed is allowed only where the cavity notes it as a tap, and the check flags any other case. No wire changes.

---

## 7 · Wire, labels and materials

**D-212 — Family-colour solid wire, identified by printed labels; no tracers.** Camden's call, 2026-09-02, after the striped-tracer scheme proved unpurchasable as cut lengths. The colour names the family (RED power · ORN 15 A outputs at 14 AWG · BLK ground · GRY analog inputs · BLU commands · PNK switch supply and +5 V · YEL/GRN CAN); the label at each end names the wire; the cavity number and the design tables are the record. Wire comes as four 16 AWG Prysmian GXL spools from Waytek (black, red, grey, blue) plus 14/12/10 AWG cuts from WireBarn and three short 16 AWG colours (pink, yellow, green). Labels are printed on a Brother PT-D220 onto TZe-FX231 flexible-ID tape, wrapped on the wire, with clear heat-shrink over them where they live under loom or in the engine bay — chosen over heat-shrink-sleeve printers as a quarter of the cost with the same permanence. Supersedes D-016 (base colour = class, tracer = circuit), D-203(c) (PT-E300 + HSe sleeves) and D-203(h) (striped GXL by the foot).

**D-203(d) / D-207 — Crimpers: one IWISS solid-contact Deutsch crimper (sizes 12/16) and an open-barrel ratchet crimper for the SICMA terminals, each accepted only after three practice crimps pass the pull test (16 AWG 20 lbf · 14 AWG 34 lbf · 12 AWG 45 lbf); a hydraulic crimper for every lug.** The genuine HDT-48-00 is the gold standard; the pull test is what makes a cheaper tool acceptable.

**D-135 / D-220 — SICMA terminal spares come from the two spare 39-way housings in hand (54 small, 32 large), so there is no Ballenger order.** Zero spares in the car's own set is why the practice crimps use the spare sets first.

**D-220 — The 2026-09-02 order changes, Camden's own edits to the carts:** the wink switches are the DMWD 1NO+1NC momentary 2-pack (replacing a 5-pack); the ATC fuse assortment is out — the drawer is checked and any missing value bought locally; the 12 × 24 aluminium sheet is out (D-214); a stainless star-washer kit and three clear heat-shrink packs are in; relays are bought without spares; no spare housing pairs.

**D-141 / D-144 / D-147 — No bench kit: no bench PSU, no plywood mule, no test pigtail.** Every risk the bench was justified by is already covered by the parallel-system architecture (D-023) and the in-car config sequence (D-194).

**D-205 — Ground studs are 3/8 stainless with star washers (four: rear, front, dash, sill); the PMU stands off its panel on three M6 spacers; F2 (2 A), F19 (3 A) and F15 (7.5 A) are values cheap assortments skip — buy them by value.**

---

## 8 · Build sequence

**D-023 / D-024 — Parallel-system migration, least to most consequential, ending with ignition and start.** The factory harness stays intact and powered until each circuit's own cutover; never both systems on one load; the car drives home at the end of every session.

**D-025 / D-174 — Soft fuses are set from current measured live in the client during migration, never from an estimate; the PMU's telemetry on the new harness is the measurement, and its gap against healthy-expected draw is also the list of tired parts to replace afterwards.**

**D-176 — Part replacement (a slow wiper motor, a weak pump) is a separate job after the PMU is in, identified from telemetry — not clutter inside the wiring project.**

**D-177 / D-199 — The pop-up motor pinout comes from factory sheet E (E-03 / E-04: YG top · WR left · RY right · R bottom; YG is the cam-driven transit contact the ladders read; WR is the constant feed and is capped). Which of R / RY carries the run winding through the cam — bridged or single — is decided by the ohm check at the motor (install M-3), the one measurement the pin plan waits on.**

**D-143 / D-145 — The deliberate soft-fuse trip is a required step, done in the car on the first migrated circuit (the interior lamp): set the limit to 2 A, short the output, watch it trip and retry.** It is the single behaviour that distinguishes this device from a fuse box and it must be met on purpose, not at speed.

**D-146 — Powered verification of the dash node is replaced by continuity testing, which needs no power and catches a wrong cavity, a missed crimp, a swapped pair and a short to the panel.** Powered checks happen in the car with every output disabled.

**D-127 / D-137 / D-103 — Housekeeping that stands: verify the two spare housings' terminal counts on arrival; mark cavity 1 on the housing with the paint pen before the first terminal goes in (D-139); measure the pop-up motors and check the transit contacts in one sitting.**

---

## 9 · The record itself

**D-026 / D-043 — Working files are Markdown; IDs are permanent and never reused; a closed question is cited with its closer.**

**D-233 — The record is `data/*.csv`; every document with a table in it is rendered.** Camden's call, 2026-09-03, after the eleven "downstream edits still to make" showed what hand-mirrored tables cost: one fact in one row, referenced by ID everywhere else. `tools/rx7.py` loads the tables, refuses to build on any contradiction (a cavity without a source, a fuse without a load, a ladder window that overlaps, a cart line below the design's count, an unknown ID) and renders `DESIGN.md`, `GLOSSARY.md`, `SHOPPING-LIST.md`, `INSTALL.md`, `WIRE-TABLES.md`, `PMU-CONFIG-SHEET.md`, `README.md` and `VIEW.html` from `templates/` (the prose) and `data/` (the facts). Derived facts — a pin's destinations, a housing's used count, a wire label, the Deutsch kit counts, ADC centres, totals — are computed, never typed. Generated files carry a banner and are never edited by hand; `DECISIONS.md` and `QUESTIONS.md` stay prose. Supersedes D-221 (the tables were the record and the generator was retired — that put the same row in four files) and revives the intent of the 2026-08-30 CSV convention in a shape that keeps the documents readable.

**D-222 — The shopping list is the four live carts of 2026-09-02 — Waytek $455.04 · WireBarn $382.68 · DeutschConnector.com $944.08 · Amazon $1,096.22 — plus the short list of gaps in `02-SHOPPING/SHOPPING-LIST.md` §8.** Nothing has been purchased; every cart waits for Camden's review and payment. Supersedes D-207's cart figures and the old five-store manifest.

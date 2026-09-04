# QUESTIONS — everything still open, in the order it has to be answered

One kind of item only: a question is anything not yet settled — a call only the owner can make, a fact to confirm, or a measurement to take. Answer one by writing under it or saying it in a session; it then becomes a `D-` entry in `DECISIONS.md` and leaves this file. IDs are permanent; the ones that came from the old verify/assumption lists keep their old numbers, new ones start at Q-100.

**The file is split by the one deadline that matters: paying for the carts.**

| | §1 · BEFORE SHOPPING | §2 · AFTER SHOPPING |
|---|---|---|
| **What it is** | Design questions — what gets bought, and whether the drawing is right | Install validation and fine tuning — is what was built correct, and is it set up well |
| **Cost of a wrong answer** | A re-order, or a part that does not fit | An afternoon, on a car that still drives home |
| **Answer them** | Now, at the desk, before `T-053` | When the car is apart, when the parts land, or at commissioning |

Nothing in §2 blocks a purchase. Nothing in §1 should wait.

§0 is the finishing task list — the order of work from here to a car driving on the PMU. §3 records what closed. §4 records what left this project and where it went.

---

## 0 · The finishing task list

**A · At the desk, now — no car, no parts**

- [ ] **A1 · Close the cart gaps** (`02-SHOPPING/SHOPPING-LIST.md` §8): at DeutschConnector add DT4P-DC ×1, 0413-204-2005 ×4 (L1-P 4 and L4-P 4, both halves — D-230), 0411-310-1205 ×1, and raise 0462-209-16141 and 0460-215-16141 to 18 each · at WireBarn sign in, confirm the 8 lines, add 16 AWG PNK 25 ft, YEL 50 ft, GRN 50 ft · **swap the Waytek 78250 (uncovered 2301) for two covered Blue Sea 2300 bars (D-224)** · **delete the NOCO BG27 (D-229)** · then pay the four carts. The shopping list §8 is the same list, generated.
- [ ] **A2 · Order the vehicle parts** — shopping list §6 (brake pedal switch, ignition switch electrical portion, blower motor, resistor pack, speed switch).
- [ ] **A3 · Check the fuse drawer** against shopping list §9 and buy any missing value locally.
- [ ] **A4 · Keep the Ionic above its BMS cutoff** while it waits — a lithium left to self-discharge into cutoff is hard to recover. Check it monthly on the app.
- [ ] **A5 · Answer §1.** Cart-blocking first — `Q-103`, `Q-104`, `V-094`, `V-095`, `V-053`, `V-051` — then the design pair, `Q-102` and `T-017`.

**B · One afternoon with the car — nothing cut, no parts needed**

- [ ] **B1 · Strip the A/C system** (D-211, D-228) — a prerequisite of the install plan. Order: a shop recovers the refrigerant first (it still holds charge; venting is illegal) · pull the compressor, bracket, belt, condenser, receiver/drier and lines · pull the factory interlock chain (G-18, G-19, G-21, G-22, G-23 and the dash A/C switch) · leave the blower, heater core, HVAC case, ducts and doors alone · box the hardware, don't scrap it. The compressor is on its own belt (D-228), so nothing else on the crank is disturbed.
- [ ] **B2 · Photograph the wideband's current install** — the piggyback fuse tap in the factory box, the controller, the gauge head and the sensor lead (M-7 `hacks` set). D-227 moves all of it into the engine leg; the photographs are what make the removal clean.
- [ ] **B3 · Look at the battery** for `V-053` (post type) and measure it for `V-051`.
- [ ] **B4 · Trace the amplifier's power lead** for `Q-104` — does it land on something that stays, or on the factory harness that leaves at install §6?

**C · The measurement day — interior apart once, before anything is cut** (`03-INSTALL/INSTALL.md` §0, boxes M-1 … M-7)

- [ ] **C1** M-1 dash envelope (closes `Q-014`) · M-2 routes · M-3 pop-up ohm check (closes `V-081`) · M-4 cargo bin (`V-088`, plus the battery cover from `Q-103`) · M-5 posts and sill space (`V-055`) · M-6 cluster plug · M-7 photographs.
- [ ] **C2** Buy the carrier-panel and backing-plate stock from the hardware store afterwards (shopping list §7) — and the battery-cover stock with it if `Q-103` lands on a fabricated cover.
- [ ] **C3** The luxury package has three ten-minute looks that ride along: the tail-light aperture, what headlamps are actually fitted, and how deep the binnacle brow shades the cluster. See `../luxury-package/QUESTIONS.md`.

**D · When the parts arrive**

- [ ] **D1** Count everything against shopping list §10.
- [ ] **D2** Fit-check the battery retention and whatever `Q-103` chose to cover the terminals.
- [ ] **D3** Confirm the two spare 39-way housings carry full terminal sets (16 large, 27 small each) — they are the spares.
- [ ] **D4** Install §1: crimp coupons and pull tests on every crimper before any real crimp.

**E · Then the install plan, in its own order** — §2 backbone (one weekend, car drives home) · §3 dash node (bench) · §4 legs (bench) · §5 install and migrate (one circuit per sitting) · §6 factory harness out · §7 shakedown.

---

# 1 · BEFORE SHOPPING — design questions

Eight questions. Six change what is in a cart; two change the drawing. All of them are answerable at the desk, with a look at parts already in hand, or with a look in the cargo bin — none needs the car apart.

## 1a · Cart-blocking — answer before `T-053` is paid

**Q-103 · What covers the battery terminals now that the box is gone?**
D-229 deleted the NOCO BG27. Retention is unaffected — D-063's backing plate, hold-down and M8 grade-8 hardware were always the structure, and the box was never load-bearing. What the box also did, and now nothing does, is keep a live 12 V post from meeting a tool, a spare wheel, or a bag of groceries in an open cargo bin. Options: **(a)** terminal boots on both posts plus a fabricated cover panel over the whole install, cut from the same hardware-store stock as the carrier panels after the measurement day; **(b)** a different, lower box that clears the Ionic's case and terminals; **(c)** boots alone, with the installation living behind the cargo trim. **Recommend (a)** — boots cost cents, the panel costs nothing extra because it rides on the C2 hardware-store trip, and unlike (c) it survives the trim being out for other work. Whatever is chosen, the boots are a cart line.
**Blocks:** the Amazon cart (the BG27 line comes out either way), and the M-4 cargo-bin mock-up.

**ANSWER:**
>
>

**Q-104 · Where does the amplifier actually get its power — and does that survive the factory harness coming out?** *(new, from D-230)*
D-230 took the amp off the PMU: F5 and L4-P 4 are deleted and the audio system stands alone. The belief is that the amp draws from a rear-cabin junction, possibly straight onto a terminal block with posts built in. **That belief has to be checked, because the factory harness is removed at install §6.** If the amp's feed originates on the factory harness — a junction, a splice, a fused tap — then the day the old loom comes out is the day the amp goes dead, and it will not be a day anyone is thinking about audio.

Look at the amp's power lead in the cargo bin and answer one thing: does it terminate on **the battery / a distribution post that stays**, or on **something the factory harness owns**? If the former, nothing more is needed and this closes. If the latter, the amp needs its own fused feed from the rear distribution before §6 — which is audio-side work, not PMU work, but it has to be on the list or it becomes a surprise.
**Cart impact:** L4-P drops from 4 conductors to 3, so one DTP size-12 contact pair leaves and one sealing-plug pair joins (D-218). ~14 ft of 12 AWG RED is no longer needed — inside the 1.5× margin, no line change.

**ANSWER:**
>
>

**V-094 · Does a 200 A MRBF survive cranking?**
The starter run is fused at the post with a Blue Sea 5187 (200 A). A 12A starter pulls 300–500 A for a fraction of a second; MRBF time-current curves tolerate that, but confirm on the 5187 curve against the Ionic's cranking data before the first start, or a cold morning ends with a blown $17 fuse and no spare. If marginal, the 250 A (5188) is the same holder — a cart swap, not a redesign.

**ANSWER:**
>
>

**V-095 · Is the carted 2 AWG welding cable rated for the runs?**
Check the Amazon listing's insulation temperature rating (≥ 90 °C) and that it is copper, not CCA. Fine-strand welding cable is accepted (D-203g) when loomed and grommeted — CCA is not accepted at any price.

**ANSWER:**
>
>

**V-053 · Battery terminal type — SAE tapered posts or 3/8 threaded studs.**
Look at the Ionic; it is in hand. It chooses the lug type for both battery cables, and the wrong lug is a re-order that stops the backbone weekend.

**ANSWER:**
>
>

**V-051 · Ionic case dimensions, with boots on.**
Tape-measure it. Two things now depend on it: whatever `Q-103` chooses to cover the terminals, and the cargo-bin cut at M-4. It no longer has to fit a box.

**ANSWER:**
>
>

## 1b · Design correctness — no cart impact, but the design cannot freeze without them

**Q-102 · The wideband: which cavities, and what fuses it?**
D-227 ruled that the O2 sensor and its controller stay, the AEM gauge head is deleted, and the signal becomes an ordinary engine-leg sensor conductor on the **ignition** feed. D-231 then closed part (c) — no interim reading, no temporary feed. Two mechanics remain, both cart-neutral.

**(a) Which cavities.** The controller needs its signal carried up to the dash and its power carried down; its ground is local to the engine-block star node and never crosses the leg (D-017/D-037). So the leg carries **two** conductors. L1-S1 has 4 free cavities, L1-S2 has 6. **Recommend L1-S2 9 (signal, GRY) and L1-S2 10 (ignition feed, RED)** — it keeps the pair together in the emptier housing and away from the shielded tach in L1-S1. The signal is low-level analog: route it with the sender wires, not the coil feed. Whether it wants its own shield like the tach does is a judgement — the AEM output is a buffered 0–5 V, which is far more robust than a coil pickup, so plain GRY is probably right.

**(b) What fuses it.** It must be live in RUN *and* START. O12 (`IGNITION`) already feeds F15 (alternator excitation, 7.5 A) and F16 (cluster IG, 5 A), and it is a 25 A channel estimated at 5.0 A — there is ample headroom for a heater that pulls a few amps at warm-up. **Recommend a new 5 A position off O12 at the dash node — F20 — feeding L1-S2 10.** Block B has two spare positions and the value is a drawer item, so the cart does not move. Confirm the controller's actual heater draw from the kit's instructions before setting the value.

**(c) What reads it — CLOSED by D-231.** **Every PMU analog input is already allocated**: A1–A8 are the dedicated bank, A15/A16 take the two shared pins that are not outputs, and the other six shared pins are outputs. The PMU cannot read AFR without giving up one of the ten inputs it already uses. The ICU can — it is a Teensy with spare analog inputs, and DP-ICU cavities 8 and 10 are sealing-plugged today. So: **signal → L1-S2 9 → dash post → DP-ICU 8, read by the ICU, published on CAN2, logged by the PMU as a received channel.** Camden ruled that the resulting gap costs nothing — the engine does not need tuning until the ICU and digital dash are in the car — so **no temporary gauge feed is built** (D-231). The two conductors are run now and capped at the engine end; the controller and sensor are commissioned with the ICU.

**ANSWER:**
>
>

**T-017 · Verify the connector pin letters in `01-REFERENCE/factory-circuits/` against the diagram scans.**
The two-letter factory colours in design §12 are what a new wire lands on; a wrong letter there sends a conductor to the wrong terminal, and nothing downstream catches it — continuity testing proves the harness is built as drawn, not that the drawing is right. A desk check with the scans open, before the measurement day. This is the one remaining item where the *design* could still be wrong rather than merely unconfirmed.

**ANSWER:**
>
>

---

# 2 · AFTER SHOPPING — install validation and fine tuning

Nothing here changes what is bought or how the harness is drawn. Each one is answered at the moment the plan reaches it, on a car that drives home at the end of the day.

## 2a · The measurement day — interior apart, before anything is cut

These gate **cutting**, never buying (D-202). All four are one session with a tape measure and a meter.

**Q-014 · Dash envelope** — install M-1. The clear width, height and depth of the centre-stack cavity, the glovebox region and the floor under the dash on both sides; lever clearance; 60 mm behind the receptacles. The carrier panels are sized from it, and the panel stock is bought afterwards (C2), so a wrong guess costs nothing but a second trip.

**ANSWER:**
>
>

**V-081 · Pop-up drive conductors** — install M-3. Ohms R → case and RY → case at parked, half-raised and raised on each motor. One winding reached through different cam segments = bridge R and RY on the run feed; a winding on each at every position = R only, RY capped. This is the one measurement the pin plan waits on (D-186, D-199) — five minutes, before the L2 leg is pinned.

**ANSWER:**
>
>

**V-055 · Sill space** — install M-5. Does a 150 × 100 mm panel with the two door receptacles, the ground stud and four relay sockets fit behind the driver kick panel?

**ANSWER:**
>
>

**V-088 · Do the amplifier, battery, Class-T block and disconnect all fit the rear cargo bins?** — install M-4. Mock it in cardboard with the amp in its intended position. With the box gone (D-229) there is more room than the design assumed, and the mock-up now also has to prove whatever `Q-103` chose to cover the terminals.

**ANSWER:**
>
>

## 2b · When the parts arrive

No open questions — the arrival checks are §0's D1–D4 boxes, and the one question that lived here (`V-093`, the box fit) closed with D-229.

## 2c · At configuration — PMU powered in the car, every output disabled (install §5.3–5.6)

**V-075 · Does the PMU have a native shutdown delay that makes the O22 self-hold latch unnecessary?**
If the client offers a configurable power-down delay on pin 7, the `KEEP_ALIVE` output (pin 8, O22) and its wake-strip diode are redundant and K11 can be driven from that delay instead. Nothing in the harness changes either way — O22's wire is already at the dash node — only the config. Check in the client at §5.4; if yes, log it and simplify `03-INSTALL/PMU-CONFIG-SHEET.md` §4.

**ANSWER:**
>
>

## 2d · At shakedown — numbers for judging a running car

Neither of these sizes anything. Both are wanted so the first week's telemetry can be read against something.

**V-002 · Alternator output rating.**
The case reads only "B" / Mitsubishi. The 1980 and 1985 workshop manuals both give a 55 A Mitsubishi unit (`00-CAR/SPECS.md` SP-078, SP-079 — the 1985 part is A5T30574; the 1981–83 fiche lists N221-18-300R, SP-006); an enthusiast chart says 50 A for base cars (SP-080, unverified). Read the rating stamped on the case to settle which the 1982 GS automatic carries. Nothing in the harness depends on it — F18 is 100 A and the 6 AWG B+ cable carries 100 A — but the charging figures at install 2.14 cannot be called good or bad without it. It also feeds the D-179 no-charge diagnosis: D-198 rebuilt the excitation circuit, and this is the number that says whether a healthy unit is behaving.

**ANSWER:**
>
>

**V-052 · The Ionic's heater trigger and winter draw.**
From the Ionic docs or app: at what temperature the heater runs, and what it draws. It sets the sleeping budget on a cold night — the PMU sleeps at ~150 mA; a heater that runs for hours does not. Nothing changes in the harness; this is a number for the owner.

**ANSWER:**
>
>

---

# 3 · Closed

Answered items leave the body of the file and land in `DECISIONS.md`. The IDs stay permanent and are cited with their closer.

**2026-09-03 — Camden's answers parsed in:**

| ID | Closed by | Outcome |
|---|---|---|
| `V-014` | D-223 | Follow the recommendation — O8/O9/O10/O11 cap at **13.0 A**, inside the DT size-16 contact rating |
| `Q-101` | D-224 | **Both** busbars covered, not just the always-hot one. Second covered bar joins the Waytek cart |
| `V-028` | D-225 | One-touch single wipe **is** wanted — `LOW < 400 ms → one sweep to PARKED`, software only |
| `V-001` | D-226 | Two coils, two igniters, leading and trailing; looks factory and untampered. Splices not individually traced |
| `Q-100` | D-227 | Wideband **stays**, AEM gauge head **goes**. Signal becomes an engine-leg sensor conductor on the **ignition** feed, read by the ICU, logged by the PMU. Mechanics → `Q-102` |
| `V-097` | D-228 | A/C compressor is on its **own belt** — the D-211 strip is purely subtractive |
| `V-093` | D-229 | **No battery box.** NOCO BG27 leaves the design and the cart; terminal covering → `Q-103` |
| `Q-102`(c) | D-231 | **No interim AFR and no temporary gauge feed** — the engine is not tuned until the ICU and digital dash are in. The wideband's conductors are run now and capped at the engine end; controller and sensor commission with the ICU |
| — | D-230 | **The amplifier comes off the PMU.** It has its own power and the audio system is deliberately isolated — its only interface anywhere is the head-unit pre-amp signal. **F5 and L4-P 4 deleted.** The head unit stays a PMU load (body-harness integrated); K11 narrows from "audio master" to head-unit constant master |

**Opened by those answers:** `Q-102` (a, b — wideband cavities and fuse) · `Q-103` (battery terminal covering) · `Q-104` (where the amp actually gets power, and whether it survives §6).

## Downstream edits still to make

D-223, D-224, D-225, D-229 and D-230 were applied to the data on 2026-09-03 (D-233 — one edit per fact, the documents regenerated). One item still waits on a ruling:

| Decision | File | Edit |
|---|---|---|
| **D-227/231** | `data/cavities.csv` L1-S2 · `data/fuses.csv` | Add the wideband pair (signal + ignition-fed heater) and its fuse once `Q-102`(a)(b) is answered |

---|---|---|
| **D-230** | `01-DESIGN/DESIGN.md` §3 | Delete the **F5** row from the protection schedule |
| **D-230** | `01-DESIGN/DESIGN.md` §5.3 | Delete the `Fuse block B, F5 out → Receptacle L4-P 4` row |
| **D-230** | `01-DESIGN/DESIGN.md` §6 | L4-P: **used 4 → 3**; note becomes "Defog, fuel pump, capped window bus"; cavity 4 becomes PLUG |
| **D-230** | `01-DESIGN/DESIGN.md` §1 | Fuse count: 8 fitted at the dash node → **7** |
| **D-230** | `02-SHOPPING/SHOPPING-LIST.md` | One DTP size-12 contact pair out, one sealing-plug pair in; 30 A fuse no longer needed for F5 |
| **D-229** | `01-DESIGN/DESIGN.md` §2 | Remove "in a NOCO BG27 box" from the Ionic paragraph |
| **D-229** | `02-SHOPPING/SHOPPING-LIST.md` | Delete the NOCO BG27 line from the Amazon cart |
| **D-224** | `02-SHOPPING/SHOPPING-LIST.md` §8 | Second covered 10-gang busbar |
| **D-223** | `03-INSTALL/PMU-CONFIG-SHEET.md` §5 · `DESIGN.md` §4.1 | O8/O9/O10/O11 enable-at **15 A → 13.0 A** |
| **D-225** | `03-INSTALL/PMU-CONFIG-SHEET.md` §3 | Add `LOW held < 400 ms → one sweep to PARKED` to the wiper rule |
| **D-227/231** | `01-DESIGN/DESIGN.md` §6 L1 · `WIRE-TABLES.md` | Add the wideband pair once `Q-102`(a)(b) is answered |

---

# 4 · Moved out of this project

Answered elsewhere, or belonging to another project. The IDs stay closed here.

| ID | Went to | Because |
|---|---|---|
| Q-072 | D-213 | One wiring project — answered |
| V-070 V-071 V-072 V-073 V-057 V-059 V-065 V-067 V-082 V-083 V-084 V-085 | `../luxury-package/QUESTIONS.md` | Cluster module (ICU) firmware and hardware |
| Q-028 V-060 V-061 T-031 T-032 T-033 T-048 T-051 | `../luxury-package/QUESTIONS.md` | Control panel, mirrors, solenoids, radar, module boards |
| Q-048 V-063 V-064 V-066 T-034 T-035 T-036 T-037 | `../luxury-package/QUESTIONS.md` | Lighting second pass (tail lights, headlamp unit) |
| V-040 | `../engine-swap/QUESTIONS.md` | Aeromotive in-tank pump draw |
| Q-001 T-049 | `00-CAR/vehicle.md` | The VIN is a car-level record, not an electrical question |
| V-074 V-047 V-069 V-087 V-089 V-090 V-091 V-092 V-096 V-038 V-021 V-019 A-010 A-012 A-013 | closed | Answered by the design as built (D-215, D-216, D-218, D-219, D-221) or turned into an install step |
| A-011 | D-227 | Superseded — the wideband is a live sensor input now, not a capped conductor |
| T-007 T-008 T-024 T-028 T-029 T-018 T-019 T-052 T-054 T-043 T-044 T-045 T-022 T-004 T-009 T-041 T-038 T-039 T-040 T-053 | §0 above or the install plan | Tasks are the finishing list and the plan's own boxes now, not a separate list |

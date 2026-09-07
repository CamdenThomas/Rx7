# QUESTIONS — everything still open, in the order it has to be answered

*Rev 2026-09-04b · owns: what is still undecided, unconfirmed or unmeasured in the electrical build, plus the finishing task list. Rulings are [`DECISIONS.md`](DECISIONS.md)'s; facts are `data/`'s.*

One kind of item only: a question is anything not yet settled — a call only the owner can make, a fact to confirm, or a measurement to take. Answer one by writing under it or saying it in a session; it then becomes a `D-` entry in `DECISIONS.md` and leaves this file. IDs are permanent; the ones that came from the old verify/assumption lists keep their old numbers, new ones run from Q-100.

**The file is split by the one deadline that matters: paying for the carts.**

| | §1 · BEFORE SHOPPING | §2 · AFTER SHOPPING |
|---|---|---|
| **What it is** | Design questions — what gets bought, and whether the drawing is right | Install validation and fine tuning — is what was built correct, and is it set up well |
| **Cost of a wrong answer** | A re-order, or a part that does not fit | An afternoon, on a car that still drives home |
| **Answer them** | Now, at the desk, before `T-053` | When the car is apart, when the parts land, or at commissioning |

Nothing in §2 blocks a purchase. Nothing in §1 should wait.

§0 is the finishing task list — the order of work from here to a car driving on the PMU. §3 records what closed. §4 records what left this project and where it went.

> **2026-09-04b.** Five of the six audit packets are ruled — **D-244** (the wideband gauge is the controller; AFR rides CAN2; supersedes D-227 and D-231) · **D-245** (the disconnect moves to the negative) · **D-246** (1/0 starter feed and a dedicated cranking return) · **D-247** (two-circuit brake switch, brake joins the wake strip) · **D-248** (the parasitic-drain rules). **Two questions are left before shopping — `Q-107` and `Q-111`** — and one desk check, `T-017`.

---

## 0 · The finishing task list

**A · At the desk, now — no car, no parts**

- [ ] **A1 · Close the cart gaps.** The generated list is `02-SHOPPING/SHOPPING-LIST.md` §8 — work from it, it is derived from the design and cannot drift. The three things that are *not* line items and have to be done by hand: **sign in at WireBarn** before checkout or the cart is lost · **swap the Waytek 78250** (uncovered 2301) for two covered Blue Sea 2300 bars (D-224) · **delete the NOCO BG27** (D-229). Then pay the four carts.
- [ ] **A2 · Order the vehicle parts** — shopping list §6. The brake pedal switch must be a **two-circuit** switch (D-247); a single-circuit one cannot be fixed later without pulling the pedal box apart again.
- [ ] **A3 · Check the fuse drawer** against shopping list §9. Two changed: F1 is **10 A** (D-242), and **F20 7.5 A** is new (D-244).
- [ ] **A4 · Keep the Ionic above its BMS cutoff** while it waits — a lithium left to self-discharge into cutoff is hard to recover. Check it monthly on the app.
- [ ] **A5 · Answer `Q-107`** (the fuel-pump oil-pressure gate) and **`Q-111`** (fresh senders, and whether the engine leg carries a sensor supply for Phase 2), then **do `T-017`** (the factory pin letters). Nothing else in §1 is open.
- [ ] **A6 · At the cart review, apply D-238** to every heavy cable line, 2 AWG and 1/0 alike: the listing must state ≥ 90 °C insulation and 100 % copper. Swap the line before payment if it does not.

**B · One afternoon with the car — nothing cut, no parts needed**

- [ ] **B1 · Strip the A/C system** (D-211, D-228) — a prerequisite of the install plan. Order: a shop recovers the refrigerant first (it still holds charge; venting is illegal) · pull the compressor, bracket, belt, condenser, receiver/drier and lines · pull the factory interlock chain (G-18, G-19, G-21, G-22, G-23 and the dash A/C switch) · leave the blower, heater core, HVAC case, ducts and doors alone · box the hardware, don't scrap it. The compressor is on its own belt (D-228), so nothing else on the crank is disturbed.
- [ ] **B2 · Read the part number off the back of the wideband gauge** and photograph the whole install — the fuse-box piggyback tap, the gauge, the sensor lead. D-244 assumes the gauge carries an **AEMnet** pair; if it does not, the fallback (0–5 V into `DP-ICU 8`) is a different wire and a different commissioning date.

**C · The measurement day — interior apart once, before anything is cut** (`03-INSTALL/INSTALL.md` §0, boxes M-1 … M-7)

- [ ] **C1** M-1 dash envelope, **plus where the wideband gauge hides and whether its fixed sensor lead reaches the bung from there** (closes `Q-014`) · M-2 routes — the tunnel now carries **three** heavy cables, the 2 AWG PMU feed and two 1/0 runs, so measure it for the bundle, not one wire · M-3 pop-up ohm check (closes `V-081`) · M-4 cargo bin (`V-088`) · M-5 sill space (`V-055`) · M-6 cluster plug · M-7 photographs.
- [ ] **C2** Buy the carrier-panel and backing-plate stock from the hardware store afterwards (shopping list §7). No battery-cover stock — D-235 chose boots alone.
- [ ] **C3** The luxury package has three ten-minute looks that ride along: the tail-light aperture, what headlamps are actually fitted, and how deep the binnacle brow shades the cluster. See `../luxury-package/QUESTIONS.md`.

**D · When the parts arrive**

- [ ] **D1** Count everything against shopping list §10.
- [ ] **D2** Fit-check the battery retention, the post terminals and the boots — including whether a boot lifts by hand with the terminal stack loaded (D-235's whole point).
- [ ] **D3** Confirm the two spare 39-way housings carry full terminal sets (16 large, 27 small each) — they are the spares.
- [ ] **D4** Install §1: crimp coupons and pull tests on every crimper before any real crimp — including the 1/0 dies on the hydraulic crimper (D-246 added two 1/0 runs).

**E · Then the install plan, in its own order** — §2 backbone (one weekend, car drives home) · §3 dash node (bench) · §4 legs (bench) · §5 install and migrate (one circuit per sitting) · §6 factory harness out · §7 shakedown.

---

# 1 · BEFORE SHOPPING — design questions

Two questions and one desk check. Neither question changes a cart line; all three have to be settled before the design freezes.

**Q-107 · Can the PMU gate the fuel pump on oil pressure?** *(your question, 2026-09-04)*

**The logic is easy; the input is the problem.** The PMU's expression language does exactly what you described — a prime window, an unconditional crank, and a run condition:

```
FUEL_PUMP = (A16 == START)
         || (A16 >= RUN && prime_timer < 3 s)
         || (A16 >= RUN && oil_press > threshold, latched)
```

What the PMU does not have is a spare analog input to read oil pressure with. A1–A8 are the dedicated bank and all eight are used; A15 and A16 are the two shared pins that are not outputs, and they are the key and headlight ladders. Ten inputs, ten allocated. So the real question is what to give up.

**(a) Recommended — A7 stops being `FUEL_LEVEL` and becomes `OIL_PRESS`.** The oil-pressure sender's conductor already lands at the dash node (`N47`: L1-S1 4 → DP-CLU 6). A7's tap moves from the fuel-gauge node onto that one. **No cavity changes, no cart line, one wire moved at the node.** What you give up is the PMU's fuel-level reading — the shakiest input in the car by the design's own admission (D-197: *if the reading is unstable, leave the channel unused; the cluster's gauge is the instrument*), and one the factory gauge shows anyway. And it comes back: `DP-ICU 8` is free again now that the wideband went to CAN (D-244), so the ICU can read the fuel node there and publish it on CAN2, where the PMU logs it as a received channel — but that is **a conductor added while the harness is on the bench**, not later (`../luxury-package/QUESTIONS.md` `Q-301`). Oil pressure is the input that protects the engine; fuel level is the one that tells you to stop for petrol.

**(b) The hardware answer, no input needed — the $20 inertia switch** from the original packet, in series with the pump feed at the rear. It covers a crash. It does not cover a stall, a rollover with the key left on, or a burst fuel line, and it trips on potholes.

**(c) Both.** They are cheap and they fail differently — (a) needs a working sender, (b) needs nothing.

**Recommend (a).** Three conditions have to go into the config with it, and they are not optional: a **3 s prime window** from key-on so the float bowl fills; **unconditional during START**; and a **latch with a long de-bounce** — once oil pressure has been seen the pump stays on until the key leaves RUN, and a cut only ever follows several seconds of continuous zero. A sender tap is a less trustworthy signal than a pressure switch, and the one thing this must never become is a pump that cuts on a glitch at 60 mph.

**A fourth condition, for the version of this that arrives later.** Once the ICU exists it will publish oil pressure, temperature and rpm on CAN2, and D-183 already reserves the rpm-qualified rules for that day. **Do not move the interlock onto the bus when it comes.** A safety cut that depends on a message from another module fails in a new way: an ICU reboot, a hung task or a dropped bus is indistinguishable from zero oil pressure, and cutting the pump at speed is far more dangerous than a pump that runs five seconds after a stall. If a CAN-sourced value is ever admitted to this rule it **fails open** — a stale channel reads as *pressure OK*, the pump stays on, and the PMU logs the fault. The interlock lives on the shortest path, the hard-wired A7 node; CAN carries the same number for display and logging.

**Confirm before it is entered:** what this engine's sender actually reads at the node, in ADC counts, at idle and at speed — the same in-car read D-142 does for every ladder. Until that number exists the threshold is a guess, so the gate is entered at commissioning, not on the bench.
**Costs:** nothing in any cart. It changes the A7 row, `N45`, the A7 decode table, the `FUEL_PUMP` expression, and the fuel-level clause in D-183 / D-197 / D-215.

**ANSWER:**
>
>

**Q-111 · Fresh senders now, and does the engine leg get a sensor supply and spare sensor cavities for the ICU's sensors later?** *(new, 2026-09-04, from the sensor review)*

Two calls that have to be made together, because the engine leg is built once and the firewall grommet is not opening twice.

**(a) New senders — yes, and in Phase 1 they must be factory-spec resistive.** The water temp (C-02), oil pressure (C-09) and fuel (C-01) senders are original and their condition is unknown; replacing them is cheap and obviously right. The constraint is that **while the factory cluster is the instrument, a new sender has to drive a 1982 bimetal gauge** — a modern 0–5 V transducer will not. So Phase 1 gets factory-spec replacements, and they are fitted **before** the in-car calibration reads (D-142, D-197), or every lookup table is read twice. Fitting a new tank sender also voids D-197's measured fuel curve (6 Ω full · 31.5 Ω mid · 80 Ω empty) — re-measure it after the swap, not before.

**(b) The Phase 2 question — what will a better sensor need that this leg does not have?** When the ICU takes over the instruments, better sensors become possible: a 3-wire pressure transducer, a thermistor with a published curve, a real temperature sensor. Every one of them wants **a regulated supply, a signal and a ground — three conductors where this design runs one** — and there is deliberately **no +5 V in any leg** (D-215). L1-S1 has 4 free cavities and L1-S2 has 6, so the *cavities* exist; the supply does not, and adding one later means the grommet, the leg and the dash.

**Options: (a)** run nothing extra, and accept that Phase 2 sensors must be single-wire resistive types forever. **(b)** Run **one switched sensor-supply conductor** to the engine bay now, capped, plus **two signal spares** — `L1-S2 9`, `10`, `11`, which D-244 has just freed — so a future sensor's regulator can live at the dash node or at the sender. **(c)** Run a +5 V reference out from the dash node: rejected. A 5 V rail down twelve feet of unshielded leg into an engine bay is a noise and fault problem this design has avoided on purpose (D-215).

**Recommend (b).** Three conductors, six contacts, about forty feet of 16 AWG inside the existing margin — a few dollars and an hour on the bench, against a firewall grommet and a whole leg later. It is the same trade D-004 and D-218 already made everywhere else, and "a named future feature" is exactly what CAPPED is for. It also covers the LS swap's sensor reservations, which are named but unspecified (L1-S2 4/5/6, D-007).
**Costs:** 3 × size-16 contacts per half, three cavities that were sealing plugs, no cart line beyond contacts already carried as spares.
**Blocks:** `L1-S2`'s final cavity state, and the design freeze.

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

**Q-014 · Dash envelope** — install M-1. The clear width, height and depth of the centre-stack cavity, the glovebox region and the floor under the dash on both sides; lever clearance; 60 mm behind the receptacles. Two riders now: where the wideband gauge hides, and whether its fixed sensor lead reaches the bung from there (D-244).

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

**V-088 · Does everything fit the rear cargo bins?** — install M-4. Mock it in cardboard: the battery at 170 × 230 × 190 mm plus boot height (D-239), the new standalone amplifier beside it (D-236), the Class-T block on the positive and the master disconnect now on the negative (D-245). Prove a hand can reach a post to jump-start the car with the boots on (D-235).

**ANSWER:**
>
>

## 2b · When the parts arrive

No open questions — the arrival checks are §0's D1–D4 boxes.

## 2c · At configuration — PMU powered in the car, every output disabled (install §5.3–5.6)

**V-075 · Does the PMU have a native shutdown delay that makes the O22 self-hold latch unnecessary?**
If the client offers a configurable power-down delay on pin 7, the `KEEP_ALIVE` output (pin 8, O22) and its wake-strip diode are redundant and K11 can be driven from that delay instead. Nothing in the harness changes either way — O22's wire is already at the dash node — only the config. Check in the client at §5.4; if yes, log it and simplify `03-INSTALL/PMU-CONFIG-SHEET.md` §4.

**ANSWER:**
>
>

**Q-110 · How long does the horn take from asleep?**
Horn, hazard, wink — and now the brake (D-247) — all work with the key out, and all of them work by *waking the module first*: the stage lifts pin 7, the PMU boots, decodes and drives the output. Nothing in the design says how long that takes, and the horn is the one control whose whole value is in its first 200 milliseconds. Measure it at §5.4 with a stopwatch and a helper: press the pad on a sleeping car, time until it sounds. Under ~200 ms, say nothing more about it. Over ~500 ms, decide whether the horn should hang off the always-hot busbar through its own relay instead — a change this build can still absorb and a finished car cannot. The brake is the same measurement and matters more.

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

**2026-09-04b — the audit packets, ruled:**

| ID | Closed by | Outcome |
|---|---|---|
| `Q-102` | D-244 | **The gauge is the controller and stays**, hidden behind the dash on F20, publishing AFR on **CAN2** — the PMU logs it from first start, the ICU displays it later, neither is "first". No engine-leg pair; L1-S2 9/10 stay plugged. **Supersedes D-227 and D-231** |
| `Q-105` | D-245 | **The master disconnect moves to the battery negative.** Opening it now kills the whole car, starter cable included. Nothing bought |
| `Q-106` | D-246 | **1/0 starter feed and a dedicated 1/0 cranking return** rear stud → engine block. 400 A stops crossing the unibody. ≈ +$180 net |
| `Q-108` | D-247 | **Two-circuit brake switch**; pole 2 → `L3-S1 7` → wake strip input 6. A pushed or towed car lights its brake lamps |
| `Q-109` | D-248 | **Interior lamp times out at 10 min · the 11.5 V shed takes INTERIOR and ACCESSORY · KEEP_ALIVE releases at 30 min with the key off** whatever the doors read |

**2026-09-04a — Camden's first six answers, and the four small audit rulings:**

| ID | Closed by | Outcome |
|---|---|---|
| `V-053` | D-234 | **Tapered SAE posts** → brass post clamps with a 3/8 in stud take-off; P095 |
| `Q-103` | D-235 | **Boots only, no cover panel** — the bin has a lid, and layers are what you strip off for a jump start; P094 |
| `Q-104` | D-236 | **The whole amplifier goes** with its untraceable feed and all the factory speaker wire; the replacement is standalone off the posts |
| `V-094` | D-237 | **200 A MRBF confirmed** — cranking sits inside the curve |
| `V-095` | D-238 | **Cable acceptance is a cart-review line**: ≥ 90 °C, 100 % copper, CCA refused at any price |
| `V-051` | D-239 | **170 × 230 × 190 mm**, recorded as `params.battery_case_mm` |
| — | D-240 | A4/A5 transit must never gate crank or reverse — a stuck transit contact would have refused the start relay permanently |
| — | D-241 | C10 was drawn 4 AWG, carted nowhere, marginal under a 150 A Class-T → 2 AWG |
| — | D-242 | F1 15 A sat outside the 13 A rating of the DT contact it feeds through → 10 A |
| — | D-243 | O2/O3 sat at the 25 A cap over 14 AWG branches with a published 3.0/3.5 A load → 13.0 A |

**2026-09-03 — the batch before that:** `V-014` → D-223 · `Q-101` → D-224 · `V-028` → D-225 · `V-001` → D-226 · `Q-100` → D-227 *(superseded by D-244)* · `V-097` → D-228 · `V-093` → D-229 · plus D-230 (the amplifier comes off the PMU), D-232 (the gauge rule) and D-233 (the record is data, rendered).

Every downstream edit from all three batches is applied. The data is the record (D-233), so a ruling reaches every document the moment `build` runs.

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
| A-011 | D-227 → D-244 | Superseded twice — the wideband is a CAN node now, not a capped conductor |
| T-007 T-008 T-024 T-028 T-029 T-018 T-019 T-052 T-054 T-043 T-044 T-045 T-022 T-004 T-009 T-041 T-038 T-039 T-040 T-053 | §0 above or the install plan | Tasks are the finishing list and the plan's own boxes now, not a separate list |

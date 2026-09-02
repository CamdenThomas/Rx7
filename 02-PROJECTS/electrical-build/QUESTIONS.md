# QUESTIONS — everything still open, easiest first

One kind of item only: a question is anything not yet settled — a call only the owner can make, a fact to confirm, or a measurement to take. Answer one by writing under it or saying it in a session; it then becomes a `D-` entry in `DECISIONS.md` and leaves this file. IDs are permanent; the ones that came from the old verify/assumption lists keep their old numbers, new ones start at Q-100.

§0 is the finishing task list — the order of work from here to a car driving on the PMU. §1 is the questions themselves, in the order they can be answered. §2 records what left this project and where it went.

---

## 0 · The finishing task list

**A · At the desk, now — no car, no parts**

- [ ] **A1 · Close the cart gaps** (`02-SHOPPING/SHOPPING-LIST.md` §8): at DeutschConnector add DT4P-DC ×1, 0413-204-2005 ×2, 0411-310-1205 ×1, and raise 0462-209-16141 and 0460-215-16141 to 18 each · at WireBarn sign in, confirm the 8 lines, add 16 AWG PNK 25 ft, YEL 50 ft, GRN 50 ft · add a covered 10-gang busbar (Q-101 decides which part) · then pay the four carts.
- [ ] **A2 · Order the vehicle parts** — shopping list §6 (brake pedal switch, ignition switch electrical portion, blower motor, resistor pack, speed switch).
- [ ] **A3 · Check the fuse drawer** against shopping list §9 and buy any missing value locally.
- [ ] **A4 · Keep the Ionic above its BMS cutoff** while it waits — a lithium left to self-discharge into cutoff is hard to recover. Check it monthly on the app.
- [ ] **A5 · Answer the desk questions** below: V-014, Q-101, V-028, V-094, V-095, V-002, V-052, T-017.

**B · One afternoon with the car — nothing cut, no parts needed**

- [ ] **B1 · Strip the A/C system** (D-211) — a prerequisite of the install plan. Order: a shop recovers the refrigerant first (it still holds charge; venting is illegal) · pull the compressor, bracket, belt, condenser, receiver/drier and lines · pull the factory interlock chain (G-18, G-19, G-21, G-22, G-23 and the dash A/C switch) · leave the blower, heater core, HVAC case, ducts and doors alone · box the hardware, don't scrap it. Confirm V-097 at the pulley.
- [ ] **B2 · Look under the hood** for V-001 (coils and igniters) and Q-100 (how the wideband is wired today).
- [ ] **B3 · Look at the battery** for V-053 (post type) and measure it for V-051.

**C · The measurement day — interior apart once, before anything is cut** (`03-INSTALL/INSTALL.md` §0, boxes M-1 … M-7)

- [ ] **C1** M-1 dash envelope (closes Q-014) · M-2 routes · M-3 pop-up ohm check (closes V-081) · M-4 cargo bin (V-088) · M-5 posts and sill space (V-055) · M-6 cluster plug · M-7 photographs.
- [ ] **C2** Buy the carrier-panel and backing-plate stock from the hardware store afterwards (shopping list §7).

**D · When the parts arrive**

- [ ] **D1** Count everything against shopping list §10.
- [ ] **D2** V-093 — the Ionic fits the NOCO BG27 with boots on.
- [ ] **D3** Confirm the two spare 39-way housings carry full terminal sets (16 large, 27 small each) — they are the spares.
- [ ] **D4** Install §1: crimp coupons and pull tests on every crimper before any real crimp.

**E · Then the install plan, in its own order** — §2 backbone (one weekend, car drives home) · §3 dash node (bench) · §4 legs (bench) · §5 install and migrate (one circuit per sitting) · §6 factory harness out · §7 shakedown. The remaining questions below are answered where the plan reaches them (V-075 and V-028 at configuration, §5.4).

---

## 1 · Questions

### Desk — a search, a datasheet, or a decision

**V-014 · Lower the O6–O11 enable-at caps from 15 A to 13 A?**
The 15 A outputs run through Deutsch DT size-16 contacts rated 13 A continuous (design §6). The loads on them are 4–10 A, so the cap only matters in a fault, and a fault trips in milliseconds — but a 13 A cap costs nothing and keeps the software limit inside every component's rating. **Recommend:** 13.0 A on O8, O9, O10, O11 (O6 and O7 already sit at measured 7.5 / 9.5 A). Changes `PMU-CONFIG-SHEET.md` §5 and design §4.1.

**ANSWER:**
>

**Q-101 · Which busbar has the cover?**
The design wants the always-hot bar covered (a live 150 A bar in a footwell) and the ground bus bare. The Waytek cart holds one 78250 (Blue Sea 2301). Confirm on the Blue Sea page whether 2301 or 2300 is the 10-gang 150 A bar *with* cover, buy one of the covered kind for the always-hot bar, and use the other as the ground bus. If neither is covered, a Blue Sea 2718 cover fits the 10-gang bars.

**ANSWER:**
>

**V-028 · Is a one-touch (single wipe) function wanted?**
A tap of the stalk to LOW and back would run one full sweep and park. It is a software rule only (add "LOW for < 400 ms → one sweep to PARKED" to the wiper rule in `PMU-CONFIG-SHEET.md` §3). Decide before §5.4 config entry.

**ANSWER:**
>

**V-094 · Does a 200 A MRBF survive cranking?**
The starter run is fused at the post with a Blue Sea 5187 (200 A). A 12A starter pulls 300–500 A for a fraction of a second; MRBF time-current curves tolerate that, but confirm on the 5187 curve against the Ionic's cranking data before the first start, or a cold morning ends with a blown $17 fuse and no spare. If marginal, the 250 A (5188) is the same holder.

**ANSWER:**
>

**V-095 · Is the carted 2 AWG welding cable rated for the runs?**
Check the Amazon listing's insulation temperature rating (≥ 90 °C) and that it is copper, not CCA. Fine-strand welding cable is accepted (D-203g) when loomed and grommeted.

**ANSWER:**
>

**V-002 · Alternator output rating.**
The case reads only "B" / Mitsubishi. Find the rating in the FSM or a parts lookup for a 1982 RX-7 GS automatic. It sizes nothing in the harness (F18 is 100 A, the 6 AWG B+ cable carries 100 A) — it is wanted so the shakedown charging figures can be judged (install 2.14).

**ANSWER:**
>

**V-052 · The Ionic's heater trigger and winter draw.**
From the Ionic docs or app: at what temperature the heater runs, and what it draws. It sets the sleeping budget on a cold night — the PMU sleeps at ~150 mA; a heater that runs for hours does not. Nothing changes in the harness; this is a number for the owner.

**ANSWER:**
>

**T-017 · Verify the connector pin letters in `01-REFERENCE/factory-circuits/` against the diagram scans.**
The two-letter factory colours in design §12 are what a wire lands on; a wrong letter there sends a new wire to the wrong terminal. A desk check with the scans open, before the measurement day.

**ANSWER:**
>

### With the car — a look, no tools

**V-001 · Confirm the ignition layout: two coils and two igniters, leading and trailing, as the factory diagram shows.**
L1-P 1 splices to BW on all four (design §12). If the car has been changed under a previous owner, the splice count changes.

**ANSWER:**
>

**Q-100 · How is the AEM X-Series wideband gauge wired today, and where does it live in the new harness?**
The car carries an AEM 30-0300 wideband (K-001, previous-owner install). The design does not power it. Find its power, ground and the sensor lead, then decide: (a) keep it on a switched feed — the accessory branch L3-M 1 (O10) with its own inline fuse and a dash ground, or (b) remove it with the carburettor tuning finished. **Recommend (a)** — it is a tuning tool worth keeping until the swap. Log the previous-owner splices you find (they are the `hacks` photo set, M-7).

**ANSWER:**
>

**V-053 · Battery terminal type — SAE tapered posts or 3/8 threaded studs.**
Look at the Ionic. It chooses the lug type for the two battery cables (install M-5).

**ANSWER:**
>

**V-051 · Ionic case dimensions.**
Tape-measure the case with its boots on before the cargo bin is cut (install M-4) and against the BG27 box (V-093).

**ANSWER:**
>

**V-097 · Is the A/C compressor on its own belt?**
Assumed yes for the FB 12A (an A/C belt was fitted separately in 2026-07). Confirm at the crank pulley during B1 — if it shares a belt with the alternator or water pump, a shorter belt is needed when it comes off.

**ANSWER:**
>

### The measurement day — interior apart

**Q-014 · Dash envelope** — install M-1. The clear width, height and depth of the centre-stack cavity, the glovebox region and the floor under the dash on both sides; lever clearance; 60 mm behind the receptacles. The carrier panels are sized from it.

**ANSWER:**
>

**V-081 · Pop-up drive conductors** — install M-3. Ohms R → case and RY → case at parked, half-raised and raised on each motor. One winding reached through different cam segments = bridge R and RY on the run feed; a winding on each at every position = R only, RY capped.

**ANSWER:**
>

**V-055 · Sill space** — install M-5. Does a 150 × 100 mm panel with the two door receptacles, the ground stud and four relay sockets fit behind the driver kick panel?

**ANSWER:**
>

**V-088 · Do the amplifier, battery box, Class-T block and disconnect all fit the rear cargo bins?** — install M-4. Mock it in cardboard with the amp in its intended position.

**ANSWER:**
>

### When the parts arrive

**V-093 · The Ionic S9 fits inside the NOCO BG27 box with terminals and boots on.** Dimensions from V-051 against the box; if not, a Group 27 box with a taller lid.

**ANSWER:**
>

### At configuration — with the PMU powered in the car (install §5.3–5.6)

**V-075 · Does the PMU have a native shutdown delay that makes the O22 self-hold latch unnecessary?**
If the client offers a configurable power-down delay on pin 7, the KEEP_ALIVE output (pin 8, O22) and its wake-strip diode are redundant and K11 can be driven from that delay instead. Nothing in the harness changes either way — O22's wire is at the dash node — only the config. Check in the client at §5.4; if yes, log it and simplify `PMU-CONFIG-SHEET.md` §4.

**ANSWER:**
>

---

## 2 · Moved out of this project

Answered elsewhere, or belonging to another project. The IDs stay closed here.

| ID | Went to | Because |
|---|---|---|
| Q-072 | D-213 | One wiring project — answered |
| V-070 V-071 V-072 V-073 V-057 V-059 V-065 V-067 V-082 V-083 V-084 V-085 | `../luxury-package/QUESTIONS.md` | Cluster module (ICU) firmware and hardware |
| Q-028 V-060 V-061 T-031 T-032 T-033 T-048 T-051 | `../luxury-package/QUESTIONS.md` | Control panel, mirrors, solenoids, radar, module boards |
| Q-048 V-063 V-064 V-066 T-034 T-035 T-036 T-037 | `../luxury-package/QUESTIONS.md` | Lighting second pass (tail lights, headlamp unit) |
| V-040 | `../engine-swap/QUESTIONS.md` | Aeromotive in-tank pump draw |
| Q-001 T-049 | `00-CAR/vehicle.md` | The VIN is a car-level record, not an electrical question |
| V-074 V-047 V-069 V-087 V-089 V-090 V-091 V-092 V-096 V-038 V-021 V-019 A-010 A-011 A-012 A-013 | closed | Answered by the design as built (D-215, D-216, D-218, D-219, D-221) or turned into an install step |
| T-007 T-008 T-024 T-028 T-029 T-018 T-019 T-052 T-054 T-043 T-044 T-045 T-022 T-004 T-009 T-041 T-038 T-039 T-040 T-053 | §0 above or the install plan | Tasks are the finishing list and the plan's own boxes now, not a separate list |

# QUESTIONS — everything still open, in the order it has to be answered

*Rev 2026-09-08 · owns: what is still undecided, unconfirmed or unmeasured in the electrical build, plus the finishing task list. Rulings are [`DECISIONS.md`](DECISIONS.md)'s; facts are `data/`'s.*

One kind of item only: a question is anything not yet settled — a call only the owner can make, a fact to confirm, or a measurement to take. Answer one by writing under it or saying it in a session; it then becomes a `D-` entry in `DECISIONS.md` and leaves this file. IDs are permanent; the ones that came from the old verify/assumption lists keep their old numbers, new ones run from Q-100.

**The file is split by the one deadline that matters: paying for the carts.**

| | §1 · BEFORE SHOPPING | §2 · AFTER SHOPPING |
|---|---|---|
| **What it is** | Design questions — what gets bought, and whether the drawing is right | Install validation and fine tuning — is what was built correct, and is it set up well |
| **Cost of a wrong answer** | A re-order, or a part that does not fit | An afternoon, on a car that still drives home |
| **Answer them** | Now, at the desk, before `T-053` | When the car is apart, when the parts land, or at commissioning |

Nothing in §2 blocks a purchase. Nothing in §1 should wait.

§0 is the finishing task list — the order of work from here to a car driving on the PMU; its block G is the agent's improvement list from the production-car comparison. §3 records what closed. §4 records what left this project and where it went.

> **2026-09-04b.** Five of the six audit packets are ruled — **D-244** (the wideband gauge is the controller; AFR rides CAN2; supersedes D-227 and D-231) · **D-245** (the disconnect moves to the negative) · **D-246** (1/0 starter feed and a dedicated cranking return) · **D-247** (two-circuit brake switch, brake joins the wake strip) · **D-248** (the parasitic-drain rules). **Two questions are left before shopping — `Q-107` and `Q-111`** — and one desk check, `T-017`.

> **2026-09-07.** The ICU / modularity session's four packets are ruled: **D-249** (A7 → oil pressure; the fuel pump is gated on it) · **D-250** (sensor supply + two spares in `L1-S2 9/10/11`) · **D-251** (wire is control, CAN is telemetry; fuel level is the ICU's) · **D-252** (the ICU drop is `DP-ICU-A` + `DP-ICU-B`; road-speed conductors `L4-S 3/4`), with luxury **D-306** (the ICU joins early, headless, behind the factory cluster). **§1 is down to the desk check `T-017`.** `Q-112`–`Q-115` are reserved by the unapplied 2026-09-05 future-proofing audit (queued in the Claude Project as `rx7/PENDING-2026-09-05-futureproofing.md`); the next question is Q-118.

> **2026-09-07b.** The DCU wiring audit, ruled: **D-253** (the blower is a PWM load on `L3-BLW`; no resistor pack or switch; no motor until the luxury package — `Q-112`, the audit's reserved number) · **D-254** (`L4-P 4` is the O15 → sill feed again) · **D-255** (`L4-S2`, mirror-adjust commands) · **D-256** (`L2-S 5` outside-air sensor → `DP-DCU 2`; `L2-S 6` nozzle heat), with luxury **D-307**; then **D-257** — the PMU's PWM tops out at 400 Hz, so the ≥ 20 kHz final stage at `L3-BLW` is the plan, not the fallback (luxury **D-308**). Next question Q-121.

> **2026-09-07c.** The ICU becomes the cluster: **D-258** (the old cluster is a peripheral of the ICU — no cluster drop; `Q-121`) · **D-259** (the ICU is a device of this build; `Q-122`) · **D-260** (the oil node is PMU-excited), with luxury **D-313** (the hand-over). **§1 gains the ICU's layout questions**, moved from the luxury package with their numbers — `V-073`, `V-082`, `V-057`, `Q-304`, `Q-308`, `Q-309` — and one new one, `Q-123`. None of them touches a cart. Next question Q-124.

> **2026-09-07e.** Sensors: **D-261** (the working senders stay — new wire to each, no replacements; the three factory-spec senders leave A2) · **D-262** (every sensor input is jumper-configured and curve-as-data so the swap changes a file, not a board; the hand-over to the swap is `../engine-swap/README.md`). The cut device at the thermostat housing is identified as the emission system's B-12 switch (`Q-124`, K-024); the oil level float switch is `Q-125`. The 01-REFERENCE circuit files lost their hand-copied "what this means for the rebuild" tables — they had drifted three decisions behind; the rebuild's side of every factory device is the electrical data's, found by its factory code. Next question Q-126.

> **2026-09-07f.** Camden's answers in this file, ruled: **D-263** (the gauges are bimetal — `Q-123`) · **D-264** (the 12A's sensors are the three senders and nothing else: B-12 stays as a plug, no oil-level lamp, no oil-temp conductor — `Q-124`, `Q-125`, `Q-308`) · **D-265** (the ICU carrier's layout brief; TCAN1042HVDRQ1 confirmed — `V-073`, `V-057`; `V-082` is agent work at F2) · **D-266** (the AEMnet frame, read from the AEM sheet he filed — `Q-304`). `Q-309` carries a sharpened recommendation and waits for a yes; two new ones from his notes: `Q-126` (the ICU enclosure with embedded connector halves) and `Q-127` (drop the engine leg's pre-run reserves); then `Q-128` (battery data into the ICU — the Ionic's Bluetooth, a shunt, or both). Next question Q-129.

> **2026-09-07h.** **D-267** — the ICU carries an ESP32-C3 radio co-processor on its carrier (channel `IC24`, dev board `P116` bought now to try the decode); nothing at the harness changes; the enclosure must be RF-transparent in front of the antenna (a constraint on `Q-126`). `Q-128` narrows to *which source*; the battery frame `0x220` joins the luxury CAN map, its firmware is luxury `F-015`. Then `Q-129` — the display now, the dash plastics later, no temporary cluster at all (recommend yes). Next question Q-130.

> **2026-09-07i.** **D-268** — `Q-129` yes: the display is this build's, installed with the ICU; no temporary cluster, no CLU pigtail, no gauge drives (IC17–IC20 and `DV32` gone, D-263 withdrawn as moot); the factory cluster stays on the *factory* harness until MG22, now gated on the display proven on the bench. The display chain `T-051` / `V-085` / `V-084` and parts P117–P121 move in from the luxury package, which keeps the moulded bezel (luxury D-314, FT34). Two new questions from it: `Q-130` (the plate as the bezel's sub-frame) and `Q-131` (the odometer as a cutover gate). Next question Q-132.

> **2026-09-08.** Answer cycle 2 — **D-269** (chain (ii) glass; the plate stays as the bezel's sub-frame; the odometer non-volatile in EEPROM + SD, a cutover gate — `V-085`, `Q-130`, `Q-131`) · **D-270** (the ICU enclosure: printed ASA / PETG, two DT13 receptacles in the wall, the harness plugs in — `Q-126`; his one-or-two-connector question answered: two) · **D-271** (reserves live at the post — the new RESERVED cavity state; the engine leg carries only the 12A — `Q-127`). `Q-309` re-suggested without the cluster (transmission-boss pulse generator, the cable deleted); `Q-128` noted open; `Q-132` opened (the three chassis stubs). The answer cycle itself is now written down — `ASSISTANT.md` §10 and `tools/answers.py`. Next question Q-133.

> **2026-09-08b.** Answer cycle 3 — **D-272** (road speed: a Hall pulse generator on the transmission's speedo-drive boss, the cable deleted, LIVE at the cutover; the supply is an O10 tap — `Q-309`) · **D-273** (the ICU carrier parts check done — `V-082`: a 60 V buck, a ≥ 60 V backlight switch behind a 4 A fuse, a current IMU, the radio on its own LDO, the LM393 on 5 V) · **D-274** (the chassis principle — every future branch ends in a dust-capped receptacle where it leaves its leg: seven new housings; both release solenoids exist and are wired to; `D1` / `D2` RESERVED at the sill — `Q-132`), with luxury **D-315**. `Q-128`: the ESP32 is confirmed (D-267); the packet now asks only for the source and the nRF Connect look. Next question Q-133.

> **2026-09-08c.** **D-275** — the drawing is a view: `build` now renders one master harness sheet (`01-DESIGN/diagrams/HARNESS.svg`, WireViz) from the tables — battery to part to ground, every conductor — and the twelve hand-drawn SVGs are archived; **A8 is done**. `DESIGN.md` §1 shows whether the sheet is current. Next question Q-133.

---

## 0 · The finishing task list

**A · At the desk, now — no car, no parts**

- [ ] **A1 · Close the cart gaps.** The generated list is `02-SHOPPING/SHOPPING-LIST.md` §8 — work from it, it is derived from the design and cannot drift. The three things that are *not* line items and have to be done by hand: **sign in at WireBarn** before checkout or the cart is lost · **swap the Waytek 78250** (uncovered 2301) for two covered Blue Sea 2300 bars (D-224) · **delete the NOCO BG27** (D-229). Then pay the four carts. D-252 adds one DT06-6S / DT04-6P assembly-kit pair and a 6-way dust cap to the DeutschConnector cart; D-253 / D-255 add a DTP-2 pair with a cap (`L3-BLW`) and a DT-8 pair (`L4-S2`); D-256 tips the 16 AWG RED family over its 500 ft spool, so a 50 ft cut joins WireBarn. §8 shows all of it once `build` runs. D-258 takes the `DP-CLU` DT-12 pair *out*; D-270 takes the two ICU receptacle kits and two clips out (the ICU's halves are DT13 headers on its board); D-271 takes about 110 ft of engine-leg wire out and adds sealing plugs. Two 100 Ω 1 W resistors (`P114`) and two ESP32-C3 boards (`P116`) join Amazon. D-274 adds the branch-end receptacles to DeutschConnector: three DT-2 pairs (`P123`), a DT-4 pair (`P124`), a DTP-2 pair and a DT-6 pair, seven dust caps, seven clips and about two dozen sealing plugs (the door receptacles are RESERVED). §8 is the list.
- [ ] **A2 · Order the vehicle parts** — shopping list §6. The senders are *not* on it: the car's own work and stay (D-261). The brake pedal switch must be a **two-circuit** switch (D-247); a single-circuit one cannot be fixed later without pulling the pedal box apart again.
- [ ] **A3 · Check the fuse drawer** against shopping list §9. Two changed: F1 is **10 A** (D-242), and **F20 7.5 A** is new (D-244).
- [ ] **A4 · Keep the Ionic above its BMS cutoff** while it waits — a lithium left to self-discharge into cutoff is hard to recover. Check it monthly on the app.
- [ ] **A5 · Do `T-017`** (the factory pin letters) — the sender and switch letters still matter; the cluster plug's no longer do (D-268). Nothing in §1 gates a cart.
- [ ] **A6 · At the cart review, apply D-238** to every heavy cable line, 2 AWG and 1/0 alike: the listing must state ≥ 90 °C insulation and 100 % copper. Swap the line before payment if it does not.
- [ ] **A7 · Apply the 2026-09-05 future-proofing audit** — queued in the Claude Project as `rx7/PENDING-2026-09-05-futureproofing.md` while the device bridge was down. It supersedes D-247 (the brake switch mechanism), opens `Q-113`–`Q-115` (alternator S/P conductors, wiper park, road speed — `Q-112` blower is ruled → D-253, and road speed is ruled → D-272), ; its sender-availability findings are moot (D-261) and its decision numbers start at D-263 when applied.

**B · One afternoon with the car — nothing cut, no parts needed**

- [ ] **B1 · Strip the A/C system** (D-211, D-228) — a prerequisite of the install plan. Order: a shop recovers the refrigerant first (it still holds charge; venting is illegal) · pull the compressor, bracket, belt, condenser, receiver/drier and lines · pull the factory interlock chain (G-18, G-19, G-21, G-22, G-23 and the dash A/C switch) · leave the blower, heater core, HVAC case, ducts and doors alone · box the hardware, don't scrap it. The compressor is on its own belt (D-228), so nothing else on the crank is disturbed.
- [ ] **B2 · Read the part number off the back of the wideband gauge** and photograph the whole install — the fuse-box piggyback tap, the gauge, the sensor lead. D-244 assumes the gauge carries an **AEMnet** pair; if it does not, the fallback (0–5 V into `DP-ICU-B 9`, the pre-wired spare) is a different wire and a different commissioning date.

**C · The measurement day — interior apart once, before anything is cut** (`03-INSTALL/INSTALL.md` §0, boxes M-1 … M-7)

- [ ] **C1** M-1 dash envelope, **plus where the wideband gauge hides and whether its fixed sensor lead reaches the bung from there** (closes `Q-014`) · M-2 routes — the tunnel now carries **three** heavy cables, the 2 AWG PMU feed and two 1/0 runs, so measure it for the bundle, not one wire · M-3 pop-up ohm check (closes `V-081`) · M-4 cargo bin (`V-088`) · M-5 sill space (`V-055`) · M-6 cluster plug — and the gauge type, `Q-123` · M-7 photographs.
- [ ] **C2** Buy the carrier-panel and backing-plate stock from the hardware store afterwards (shopping list §7). No battery-cover stock — D-235 chose boots alone.
- [ ] **C3** The luxury package has three ten-minute looks that ride along: the tail-light aperture, what headlamps are actually fitted, and how deep the binnacle brow shades the cluster. See `../luxury-package/QUESTIONS.md`.

**D · When the parts arrive**

- [ ] **D1** Count everything against shopping list §10.
- [ ] **D2** Fit-check the battery retention, the post terminals and the boots — including whether a boot lifts by hand with the terminal stack loaded (D-235's whole point).
- [ ] **D3** Confirm the two spare 39-way housings carry full terminal sets (16 large, 27 small each) — they are the spares.
- [ ] **D4** Install §1: crimp coupons and pull tests on every crimper before any real crimp — including the 1/0 dies on the hydraulic crimper (D-246 added two 1/0 runs).

**E · Then the install plan, in its own order** — §2 backbone (one weekend, car drives home) · §3 dash node (bench) · §4 legs (bench) · §5 install and migrate (one circuit per sitting) · §6 factory harness out · §7 shakedown.

**F · The ICU — built and commissioned on the bench before the harness goes in (D-259)**

- [ ] **F1 · Draw the enclosure** — D-270: the board outline with the two DT13 flanges on one face, grommets on the other, the antenna window; printed in ASA / PETG (CSU's makerspace or a print service). Agent draws, Camden prints.
- [ ] **F2 · Order the BT817 eval board (P117) now — before the layout — then lay out carrier H-001 around the DT13 headers and order it** with the §6b parts (P122 the DT13s); the display header, the PSRAM, the IMU and the radio go on together.
- [ ] **F3 · Build it and bring up the display chain on the bench** — install §1.21–1.23: eval board and DRIVE page first, the chain-(ii) panel after M-1 sizes the aperture, `V-084` timings, the odometer persisting in EEPROM and on the card (D-269). MG22 waits for this box; nothing else does.
- [ ] **F4 · Land `F-012`** (the `can_map.h` bump, luxury `BRING-UP.md` §1) on a machine with g++ before anything is flashed for the car.

**G · What production cars that wire this way do better — the agent's improvement list** *(2026-09-07, from a comparison against the closest production analogues: Tesla Model 3 / Y body controllers with solid-state eFuses and no relays; Rivian's 2025 zonal R1T / R1S; Mercedes W220 / W211 SAM front / rear zone modules; BMW's IBS power management and FRM solid-state lighting; Toyota / Lexus junction-block multiplex; and the motorsport PDM practice this PMU comes from. Each line is a lesson, the change it implies here, and who does it. Nothing below touches a cart unless it says so.)*

- [ ] **G1 · Every output's current is a diagnostic (Tesla, BMW FRM).** Production eFuse controllers read bulb-out, a tired motor and a seizing pump from the current trace — this PMU logs the same trace and the design only uses it once, to set the soft fuses (D-025). *Change:* a `healthy_a` band per output in `pins.csv`, recorded at shakedown, and PMU logic rows that flag a lamp channel reading under half its baseline or a motor over 1.5× it — a warning bit on `0x1xx` the ICU shows. Agent: the columns, the rows, the shakedown box. No hardware.
- [ ] **G2 · Retry policy by load class (Tesla eFuses, MoTeC / AiM practice).** One retry rule for everything ("3 retries, 5 s") is a fuse-box habit. Lamps and motors can retry; a fuel pump or ignition that trips should retry once and then stay off until the key cycles; a wiper that stalls in snow should retry more, slower. *Change:* a `retry` column per output in `logic.csv` / the config sheet, three classes. Agent.
- [ ] **G3 · A shorted MOSFET is an output stuck ON — decide what that means for each safety load (motorsport PDM practice).** A relay fails open; a high-side FET fails short, and the load runs with the key out. The negative disconnect (D-245) is the hard kill and the answer for the driveway; the question is what the *car* does for FUEL_PUMP, IGNITION, START and HEAD. *Change:* read the PMU manual (`01-REFERENCE/PMU_info/PMU_Manual.pdf`) for whether a stuck output is detected and reported; add a shakedown card line — "disconnect open before any work" — and, if the manual is silent, decide whether O5 (fuel pump) gets a series relay off the key's RUN ladder as the one hardware back-stop. Agent reads; Camden rules on the relay.
- [ ] **G4 · The 12 V budget needs a meter on the battery, not just on the outputs (BMW IBS).** BMW's power management measures total current at the negative post, computes state of charge and sheds loads on quiescent draw it did not expect. This design measures PMU channels only — nothing sees the standalone amplifier, the Ionic's own heater or a leak elsewhere — and its 150 mA sleeping figure (V-052) is quoted, not measured. *Change:* (a) read the PMU's real sleep current from the manual and compute days-to-BMS-cutoff against the Ionic's capacity — agent, now; (b) a clamp-meter box at shakedown on the negative cable, engine off, 1 h after key-off — install plan; (c) *Camden's call, now `Q-128`:* a Bluetooth shunt (Victron SmartShunt class, ~$130) on the negative between the disconnect and the post — the one instrument that turns D-248's rules into numbers the ICU can read and the PMU can log; the space for it is decided at M-4.
- [ ] **G5 · Charging voltage against a lithium battery (Porsche / BMW lithium starter options).** Lithium starter batteries want the regulator's set-point checked against the cell chemistry's ceiling, and low-temperature charging inhibited (the Ionic's heater is that). *Change:* install 2.14 records the alternator's regulated voltage at 2000 rpm, warm; the Ionic's maximum charge voltage goes into `00-CAR/specs` from its sheet; if the alternator sits above it, the fix is the regulator, not the battery. Agent adds the box and the spec row; the reading is the car's.
- [ ] **G6 · Wake sources are enumerated and every module that must work with the key out has one (Mercedes / BMW wake-on-CAN).** The wake strip has six inputs and six are used (ACC, RUN, door stage, horn / hazard / wink stage, brake, the O22 latch). The luxury panel on `DP-KEY` is fed from O10 — accessory-switched — so a hatch-release or fuel-door key on it cannot work with the key out, and nothing can wake the PMU from the panel. *Change:* decide now, while `DP-KEY` is a DT-4 in a cart: either (i) those two keys stay hardwired to the wake strip like the winks (a seventh diode; two conductors from the panel position), or (ii) `DP-KEY` becomes a DT-6 with a constant feed and a wake line. Cheap today, a dash-out job later. **Camden's call** — it is the same class of question as Q-108 was for the brake.
- [ ] **G7 · Module placement vs water (the Mercedes rear-SAM failure).** The classic SAM failure is water down a tail-lamp seal or a blocked drain into the module. FBs leak at the cowl seam and the windscreen; the dash node sits in the footwell under both. *Change:* M-1 gains a look — where does water go when the cowl drains block? — and install §3 gains a rule: every conductor enters the PMU and the panels from below or with a drip loop, nothing sits in the lowest 50 mm of the footwell, the 39-way faces down or sideways. Agent adds; the look is M-1's.
- [ ] **G8 · Bundled derating (OEM terminal practice).** OEMs run sealed 1.5 mm contacts at ~10 A continuous in a loom, not their 13 A rating. D-232 lets 16 AWG sit at exactly 13.0 A. *Change:* list every 16 AWG conductor whose channel is enabled above 10 A and check each is a tap (fault current only) or a short run; anything continuous at 13 A moves to 14 AWG. Agent — a query, then perhaps two rows.
- [ ] **G9 · Sensor returns and ground offset (OEM single-wire senders, same weakness).** The water-temp and oil senders return through the engine block; the ICU and the PMU read them against the dash ground. Under cranking or full alternator load the block-to-dash offset is tens of millivolts — a few degrees on the temperature curve. *Change:* a shakedown box — measure block ground to GND bus at idle and at full load; if over 50 mV the swap's rebuilt leg gets a dedicated sensor return, which costs nothing to decide now. Agent adds the box and the hand-over row.
- [ ] **G10 · The fuse-lid map (Toyota / Lexus junction blocks).** Every OEM box carries its map on the lid; here the map is a config sheet in a binder. *Change:* a rendered one-page card — output → circuit → soft-fuse limit → what trips it — printed and laminated, one at the dash node, one in the glovebox with the laptop port. Agent: a template and a view; it is derived, so it can never be wrong.
- [ ] **G11 · CAN and ignition routing (OEM EMC practice).** The engine leg carries the CAN2 drop and the tach line past the coils and igniters. *Change:* a routing rule in install §4 for L1 — the twisted pair and the shielded tach cross the coil leads at 90° and never run alongside them within 50 mm; the same for the CAN pair past the blower and wiper motors at the dash. Agent.
- [ ] **G12 · Spare capacity (motorsport PDM practice: 10–15 % spare channels).** All 22 outputs are allocated (two to the swap) and all ten inputs; the expansion path is K3 / K4 empty sockets, the spare block-B fuse positions and the luxury package's O15 block. *Change:* write that path down in the design (§4) so the next feature does not start by asking for a channel that does not exist, and list the two channels that could be freed by merging (glovebox + luggage lamps; the two courtesy circuits) if it ever comes to it. Agent.
- [ ] **G13 · Wire footage is the one derived fact still typed (Rivian's lesson is that the wire count is the design).** Rivian cut 1.6 miles of wire by *measuring* what a zonal layout needed. This design's footage is a hand estimate at 1.5× (D-202); the tool could compute it from the cavity table and a route-length table once M-2 measures the routes. *Change:* a `routes.csv` (leg → grommet → node, feet) and a footage view feeding the WireBarn / Waytek lines — agent, after M-2.
- [ ] **G14 · Connector-side conventions written once (OEM harness drawings).** Every OEM harness print states the view convention (wire side / mating side) at the top; this design's cavity numbers are the housing's moulded numbers, but nothing says so in the wire tables. *Change:* one sentence at the head of `WIRE-TABLES.md` §C and the M-6 / T-017 sheets — "cavity numbers are the numbers moulded into the housing, read from the wire side". Agent, five minutes, prevents the classic mirror-image error.

---

# 1 · BEFORE SHOPPING — design questions

One desk check and three items. `Q-309` wants a yes to (a); `Q-132` a yes or a keep; `Q-128` waits on the BMS protocol. `V-082` is the agent's, at layout. The carrier layout is no longer gated on anything but the enclosure file (D-270). `T-017` has to be done before the design freezes; `Q-309`, `Q-126` and `Q-127` each carry a recommendation and want one word — `Q-126` gates the carrier layout (install §1.20), `Q-127` takes wire *out* of the carts, `Q-309` changes nothing until M-2. `V-082` is the agent's, at layout.

**T-017 · Verify the connector pin letters in `01-REFERENCE/factory-circuits/` against the diagram scans.**
The two-letter factory colours in design §12 are what a new wire lands on; a wrong letter there sends a conductor to the wrong terminal, and nothing downstream catches it — continuity testing proves the harness is built as drawn, not that the drawing is right. A desk check with the scans open, before the measurement day. This is the one remaining item where the *design* could still be wrong rather than merely unconfirmed.

**ANSWER:**
>
>

**Q-128 · Battery data — the source: the Ionic's BMS, a shunt, or both?** *(the ESP32-C3 is in — D-267, confirmed 2026-09-08 ("include the esp32 for sure"); this packet is only the source)*
The dev board (`P116`) tries the Ionic decode. **The twenty-minute test, yours:** nRF Connect on the phone beside the battery → paste the BMS's advertised name and service UUIDs here (a `0xFF00` service with `FF01` / `FF02` characteristics is JBD — an evening's firmware; Daly and JK have their own; nothing recognisable → the Android HCI snoop log and Wireshark, a weekend; authenticated or encrypted → the shunt is the answer, not a project). The reliable route to the same numbers either way is a **Victron SmartShunt** (~$130, on the negative at the G4 placement): voltage, current, its own state of charge, consumed Ah, temperature, over published Bluetooth advertisements or a VE.Direct serial line, and it sees the amplifier and every leak the BMS cannot. **Recommend both** — the shunt for what the car logs, the BMS decoded as a bonus. **Say: shunt now / shunt later / BMS only — and paste the UUIDs.**

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

**2026-09-08b — answer cycle 3:**

| ID | Closed by | Outcome |
|---|---|---|
| `Q-309` | D-272 | **A Hall pulse generator on the transmission's speedo-drive boss**, the cable deleted, fitted at the meters cutover; the same kind of sensor on whatever transmission follows, or the ECU's VSS frame if the next box has no drive |
| `V-082` | D-273 | **Parts check done** — LMR36015-Q1-class buck (60 V), ≥ 60 V backlight switch behind a 4 A fuse, LSM6DSO / ICM-42688-P IMU, the radio on its own LDO, the LM393 on 5 V; everything else confirmed as drawn |
| `Q-132` | D-274 | **Both solenoids exist and are wired to**; the nozzle feed and every other future branch ends in a dust-capped receptacle where it leaves its leg — seven new housings (`L2-NZL` `L2-OAT` `L3-CMF` `L3-WIN` `L3-MOD` `L3-RDR` `L4-RDR`); `D1` / `D2` are RESERVED at the sill |

**2026-09-08 — answer cycle 2:**

| ID | Closed by | Outcome |
|---|---|---|
| `V-085` | D-269 | **Chain (ii)** — 900–1000-nit 1920 × 720 bar through its scaler, TFP410-class bridge; M-1 sizes the aperture, no longer decides the glass |
| `V-084` · `T-051` | D-269 | Agent work at install §1.22 (timings) and an order now (the eval board, P117) |
| `Q-130` | D-269 | **The plate stays** as the bezel's sub-frame — 10 mm flange, its holes the bezel's |
| `Q-131` | D-269 | **Odometer non-volatile no matter what** — Teensy EEPROM emulation authoritative, microSD the log; persistence is a cutover gate |
| `Q-126` | D-270 | **A printed ASA / PETG enclosure with two DT13 receptacles in the wall**; the harness plugs in; two connectors, not one — the 6-way is the module pattern, the 12-way keeps sensors apart, only the display leaves the box |
| `Q-127` | D-271 | **Reserves live at the post** — RESERVED state: `L1-P 2/3`, `L1-S2 9`, `L1-S2 11` pinned at the receptacle, sealed in the leg; `L1-S2 4–6` plugs; the engine leg carries only the 12A |

**2026-09-07i — the display comes now:**

| ID | Closed by | Outcome |
|---|---|---|
| `Q-129` | D-268 | **The display is this build's, installed with the ICU** — no temporary cluster, no CLU pigtail, no gauge drives; the factory cluster lives on the factory harness until MG22, gated on the display proven on the bench; the display chain and P117–P121 move in; the bezel stays luxury. D-263 (bimetal gauges) withdrawn as moot |

**2026-09-07f — Camden's answers in this file:**

| ID | Closed by | Outcome |
|---|---|---|
| `Q-123` | D-263 | **All three gauges are bimetal** — the ICU's gauge drives are 1–2 kHz PWM sinks; IC17–IC19 final |
| `Q-124` | D-264 | **B-12 confirmed unneeded** — stays in the thermostat housing as the port's plug, unconnected (K-024) |
| `Q-125` | D-264 | **No oil-level lamp** — C-06 is not wired; the CLU pigtail stays at twelve lines |
| `Q-308` | D-264 | **No oil-temp sender and no conductor for one on the 12A** — `L1-S2 10` and `DP-ICU-B 7` are sealing plugs, `N65` and `P112` gone; IC07 stays a footprint for the swap |
| `V-073` | D-265 | **Layout brief** — inputs one edge, drives / display / CAN the other; IMU per the recommendation; the enclosure note became `Q-126` |
| `V-057` | D-265 | **TCAN1042HVDRQ1 verified available** |
| `Q-304` | D-266 | **AEMnet frame confirmed from the 30-0300 sheet** — 29-bit 0x180, 100 Hz, big-endian, no termination; flags in bytes 6–7; the luxury map row is *confirmed* |

**2026-09-07c — the ICU becomes the cluster:**

| ID | Closed by | Outcome |
|---|---|---|
| `Q-121` | D-258 (+ D-260) | **The old cluster is a peripheral of the ICU** — no `DP-CLU`; the senders terminate at `DP-ICU-B`, the ICU excites fuel and water temp, reads the PMU-excited oil node, drives the three gauges and passes the rest through a twelve-line CLU pigtail; `DP-ICU-A 6` = F16 aux, `DP-ICU-B 10–12` = tell-tale senses. Unplug the pigtail and the cluster is gone without a trace |
| `Q-122` | D-259 (+ luxury D-313) | **The ICU is this build's device** — built, bench-commissioned against the old cluster and installed with the harness; the luxury package brings only the display, onto a board that is already there. D-081 reads "PMU + ICU" |

`Q-121` and `Q-122` were raised and ruled in the same session and never sat in this file.

**2026-09-07 — the ICU / modularity session:**

| ID | Closed by | Outcome |
|---|---|---|
| `Q-107` | D-249 | **A7 reads the oil-pressure node; the fuel pump is gated on it** — START unconditional, 3 s prime, latched with a 5 s de-bounce, threshold read in the car, FAULT fails open. Fuel level leaves the PMU |
| `Q-111` | D-250 | **Sensor supply + two signal spares in `L1-S2 9/10/11`**, capped past the grommet; fresh factory-spec senders fitted before calibration |
| `Q-116` | D-251 + luxury D-306 | **Wire is control, CAN is telemetry.** The ICU joins early as a headless CAN node behind the factory cluster; fuel level is its signal (`DP-ICU-B 3`, frame `0x218`); the display is a bezel-only event later |
| `Q-117` | D-252 | **Two ICU housings** — `DP-ICU-A` DT-6 (the DP-DCU pattern) and `DP-ICU-B` DT-12 (sensors only, with oil temp, road speed and a spare pre-wired). Road-speed conductors `L4-S 3/4` run now. +1 DT-6 kit pair |

`Q-116` and `Q-117` were raised and ruled in the same session and never sat in this file.

**2026-09-07b — the DCU wiring audit:**

| ID | Closed by | Outcome |
|---|---|---|
| `Q-112` | D-253 | **Blower wired as a PWM load** — O16 → `L3-P 1` → `L3-BLW` (DTP-2 at the HVAC case), 12 AWG return to the dash ground; no resistor pack, no speed switch, no motor until the luxury package; speed = a ≥ 20 kHz final stage at `L3-BLW` on the DCU's PWM (D-257 — the PMU's PWM caps at 400 Hz), O16 a steady feed. P087–P089 leave the parts |
| `Q-118` | D-254 | **`L4-P 4` is the O15 → sill feed** (D-181 restored) — F14 mirror heat has a source again |
| `Q-119` | D-255 | **`L4-S2` (DT-8)** — mirror-adjust commands dash → sill, spliced onto D1/D2 4–6 at the sill node |
| `Q-120` | D-256 | **`L2-S 5` outside-air sensor → `DP-DCU 2` · `L2-S 6` heated-nozzle / de-icer feed** (conditional on luxury `Q-303`); no auto-climate, display only |

`Q-118`–`Q-120` were raised and ruled in the same session and never sat in this file. `Q-112` is the first item of the 2026-09-05 audit applied.

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
| V-070 V-071 V-072 V-059 V-065 V-067 V-083 | `../luxury-package/QUESTIONS.md` | DCU carrier, firmware, the PMU's CAN export |
| V-084 V-085 T-051 | back in §1 above (D-268) | The display is this build's instrument |
| V-073 V-057 V-082 | back in §1 above (D-259) — with `Q-304`, `Q-308`, `Q-309`, which were raised there | The ICU carrier is this build's hardware |
| Q-028 V-060 V-061 T-031 T-032 T-033 T-048 T-051 | `../luxury-package/QUESTIONS.md` | Control panel, mirrors, solenoids, radar, module boards |
| Q-048 V-063 V-064 V-066 T-034 T-035 T-036 T-037 | `../luxury-package/QUESTIONS.md` | Lighting second pass (tail lights, headlamp unit) |
| V-040 | `../engine-swap/QUESTIONS.md` | Aeromotive in-tank pump draw |
| Q-001 T-049 | `00-CAR/vehicle.md` | The VIN is a car-level record, not an electrical question |
| V-074 V-047 V-069 V-087 V-089 V-090 V-091 V-092 V-096 V-038 V-021 V-019 A-010 A-012 A-013 | closed | Answered by the design as built (D-215, D-216, D-218, D-219, D-221) or turned into an install step |
| A-011 | D-227 → D-244 | Superseded twice — the wideband is a CAN node now, not a capped conductor |
| T-007 T-008 T-024 T-028 T-029 T-018 T-019 T-052 T-054 T-043 T-044 T-045 T-022 T-004 T-009 T-041 T-038 T-039 T-040 T-053 | §0 above or the install plan | Tasks are the finishing list and the plan's own boxes now, not a separate list |

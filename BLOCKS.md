# BLOCKS

*The one page Camden writes in.*

Type your answer after `**SOLVE:**` - on that line or the lines under it. Plain
sentences, any length, no markers to keep. Blank means unanswered. Skipping one costs
nothing: it stays open and comes back.

Nothing here is ever regenerated. New blocks are appended; solved ones move down to
SOLVED with the decision they produced. An answered block that is not yet applied is
advisory - it never refuses a commit.

## OPEN

### BLK-015 · luxury-package
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

### BLK-016 · luxury-package
**Ask** Which mirror?
**Why** D-305 fixed the feature set - adjustment and heat only. The doors then fix the part: a conventional 3-wire motor pair (common + X + Y) with a resistive heater on its own feed. A 5-wire, LIN-bus or module-driven mirror needs conductors the doors do not have and never will, so the wiring diagram is the filter, not the photograph.
**Options**
- (a) name a specific mirror pair you want and I check its diagram against the 3-wire + resistive-heat constraint
- (b) I search for candidates that meet the constraint and come back with two or three, with prices
**Recommend** (b) - the constraint is narrow enough that the search is mechanical, and it costs you nothing to read the shortlist.
**Stops** The mirror line in the luxury cart, and the door-leg conductor count if a candidate ever needed more than three.
**Carried from** Q-300
**SOLVE:**

### BLK-017 · luxury-package
**Ask** A heated washer nozzle (and park de-icer) that fits the FB cowl - is there one, and do you want the de-icer on the same feed?
**Why** The feed is already run: L2-S 6 ending in the L2-NZL receptacle at the cowl (electrical D-274), a comfort-bus load the DCU switches. Your standing condition is that it goes in only if one can be made to work - if none can, the receptacle stays capped and nothing is lost. The open part is whether a wiper-park de-icer strip shares the feed, because that changes the load and the DCU channel.
**Options**
- (a) integral-PTC nozzle in the factory hole pattern and hose size, nozzle only - cleanest if one exists
- (b) universal heated nozzle on an adapter plate, nozzle only - always available, needs a plate
- (c) either of the above plus a wiper-park de-icer strip on the same feed - more load on one channel, more winter value
**Recommend** (a) for the nozzle, and yes to the de-icer as (c) if the strip's draw fits the channel - I will size it before anything is bought. Nozzles ground at the front star, not through the hood hinge.
**Stops** The nozzle and de-icer lines in the luxury cart, and the DCU channel budget for the comfort bus.
**Carried from** Q-303
**SOLVE:**

### BLK-018 · electrical-build
**Ask** Battery data: shunt now, shunt later, or BMS only?
**Why** Your decode answered the part you asked me about, so here it is settled. The Ionic (IC-12V40-S9H, 4S) runs a Telink/HM-10-class transparent-serial module: FFE0/FFE1, one characteristic both directions. Two ways to read it, and the ESP32-C3 can do either in about a hundred lines of NimBLE-Arduino. **(1) Passive scan, no connection at all** - the advertisement's manufacturer data starts with pack millivolts, broadcast continuously, so a scan callback gets pack voltage with no pairing, no connection state, nothing that can hang, and it keeps working while your phone is also connected. **(2) GATT client** - connect, subscribe to FFE1 notifications, parse the 13-byte frame you already cracked (`7E` type `len` | four LE uint16 | checksum `0D`), type 01 being the four cell voltages at ~1.43 mV/count. One connection at a time, so the ESP32 and your phone cannot both be attached. Do both: scan for voltage always, connect only when cell detail is wanted. FEE7 and anything labelled DFU stay untouched, exactly as you said.
**What is still missing is the reason this is a question.** Type 01 is voltages. **Current and state of charge are not in it**, and getting them means writing commands to FFE1 and guessing message types with no documentation and no guarantee - the pack could also answer nothing useful. A **Victron SmartShunt** (~$130, on the negative at the G4 placement) gives voltage, current, its own state of charge, consumed Ah and temperature over published BLE advertisements or a VE.Direct line, and it sees the amplifier, the ICU and every parasitic leak the BMS cannot see because they are outside it.
**Options**
- (a) shunt now - buy it in the same pass as everything else; the BMS decode stays a free bonus for cell detail. Adds a cart line and a rear-node ground stud detail
- (b) shunt later - build the BLE read now, live on pack voltage and cell balance, add the shunt if you find you want current. Costs nothing now; adds a cargo-bin job later with the bin already closed
- (c) BMS only - no shunt ever. Free, and the car never logs current or true state of charge
**Recommend** (a). Current is the number that makes the sleeping-current budget (D-280) an acceptance test instead of an estimate, and the bin is open exactly once. Flip to (b) if you would rather see what the BMS alone tells you for a season first - nothing in the harness changes either way, and under D-323 nothing is bought yet.
**Stops** The battery-data cart line, the G4 shunt placement, and whether SN-class current lands on CAN at all.
**Carried from** BLK-003, which asked the same thing before your decode; your working notes stay there.
**SOLVE:**

### BLK-019 · electrical-build
**Ask** Which e-Series master switch, and does the PMU get a switch-position input?
**Why** This is the load-dump question from BLK-003's neighbour, now that two things you have since ruled make it much smaller. You asked what was involved and said it sounds like you should prepare for both - so here is what is actually left. An unsuppressed load dump on a 12 V system is ISO 7637-2 pulse 5a, **65-87 V for 40-400 ms**, and reports on lithium BMS disconnects run **120 V+**. There are two triggers. Opening the master with the engine running is the one you control. **The BMS opening while driving** - over-current, cell fault, over-temperature - needs no mistake from you and never goes away; lead-acid degrades gracefully and stays in circuit, a BMS opens in milliseconds at full charge current.
**What your rulings already settled.** D-316 fixed the engine leg to the FB/FC alternator, which is **internally regulated**, so the Blue Sea 9004e's Alternator Field Disconnect pole has no external field to open and cannot help directly. But the PMU already owns excitation on O12 -> F15, so the 9004e's auxiliary pole - which opens slightly *before* the main contacts - can instead be read as a **switch-position input**, letting the PMU kill excitation before the main path breaks. D-319 put the switch on the positive side at the battery, which is in the cargo bin, so that input costs one conductor up the L4 leg. A **high-joule TVS across the PMU main feed at the module** goes in either way: it is the only thing that covers the BMS case, and it is a couple of dollars.
**Options**
- (a) 9003e + TVS. No extra conductor, no cavity. Covers the BMS trigger; opening the master with the engine running stays a written "do not do that"
- (b) 9004e + TVS + one conductor from its aux pole up L4 to a PMU input. Covers both triggers in hardware. Costs the switch price difference, one L4 cavity and ~16 ft of 16 AWG
- (c) 9003e + TVS now, and leave an L4 cavity plugged for (b) later. Cheapest now, but the aux pole needs the other switch, so "later" means buying the switch twice
**Recommend** (b). It is the only option that covers the trigger that needs no mistake *and* the one that does, the tunnel is open exactly once, and under D-323 nothing has been bought yet so there is no re-buy to eat. Flip to (a) if you would rather not spend an L4 cavity and a PMU input on a failure mode you can also avoid by habit.
**Stops** P049's SKU, one L4 cavity, and one PMU input allocation. Also queued as agent work: ask ECUMaster whether the PMU's "immunity per ISO 7637" covers pulse 5a unclamped or only 5b - the TVS goes in regardless of their answer.
**Carried from** BLK-007; your words stay there.
**SOLVE:**

## SOLVED

### BLK-001 · electrical-build → D-316
**Ask** Alternator sense and phase conductors, run now and capped
**Why** Carried from Q-113
**Carried from** Q-113
**Detail**
The FB is an **LR** system: `BW` is the R terminal (ignition-switched regulator wake, under 0.5 A) and `WB` is L (lamp sink). The lamp is decorative - R does the exciting, and O12 -> F15 -> L1-S1 2 is correct for it. The **'86-88 FC 70 A alternator is a bolt-in with the identical two-terminal interface**, ~$120, and the single narrow V-belt caps realistic output around 70-90 A anyway - so that is the sensible ceiling and it needs no wiring change.
What cannot be fitted today is anything **LS-type** - FD 100 A, GM CS-series, Denso 3-wire - because they need a **sense** wire and use the **lamp as the excitation path**. Two 16 AWG conductors into free `L1-S1` cavities (5, 7, 8, 12 are all sealing plugs) cover it: **S**, whose dash end lands on the **busbar** through a 3-5 A fuse rather than at the alternator stud, and **P** (phase/FR, milliamps, free insurance).
*Note against D-198:* once the ICU replaces the cluster there is no bulb, so an LS-type unit needs a **100 Ohm 5 W resistor in parallel** on the L line or it may never start charging.
**Blocks:** L1-S1's final cavity state.
**SOLVE:** prepare only for a FB/FC alternator in the engine leg with no warning light (I don't know if that means I need a resistor for these alternators or not) however the pmu/relay/fuse section should be pinned and wired to work for an alternator id find on most engines id consider swapping in. just like every cuircut in the engine leg, the fuse/relay/pmu are fully dune and future prrof the engine leg is bare bones what i have now no uneeded wires just unpinned spaces on the connector to the relay/fuse/omu fully pinned connector

### BLK-002 · electrical-build → D-317
**Ask** The wiper park sense is the one place a replacement motor will not fit
**Why** Carried from Q-114
**Carried from** Q-114
**Detail**
Replacement two-speed motors sort into five families. The fitted one (Japanese OE pattern) brings the cam out as a **dry SPDT** - what the A3 ladder assumes, and correct. But the most common universal on the shelf today is the **Bosch/SWF/Valeo DIN 72552 family**, which is self-parking: the cam's common is the **low-brush node**, `53a` wants a permanent +12, `53e` is the brake throw, and reading either would put battery volts and brush spikes onto A3.
**Recommend:** promote **`L2-S 4`** (sealing plug) to a capped `WIPER_PARK_RET` conductor, hold **`L2-M 8`** as a fused park feed, and specify the A3 wiper-park leg as **clamped and 12 V tolerant** at the resistor sub-assembly. Two cavities, and the whole replacement population fits.
**SOLVE:** follow recommendations, prepare for both wires through the front leg, however when the wiper branches off solo only the one needed wire continues after the branch to the part, then if I use other wipers I just pull that tiny branch and pin the second wire (all casis/body/intitor shoud follow this patter for future circuts)

### BLK-003 · electrical-build → BLK-018
**Ask** Battery data — the source: the Ionic's BMS, a shunt, or both?
**Why** Carried from Q-128
**Carried from** Q-128
**Detail**
*(the ESP32-C3 is in — D-267, confirmed 2026-09-08 ("include the esp32 for sure"); this packet is only the source)*
The dev board (`P116`) tries the Ionic decode. **The twenty-minute test, yours:** nRF Connect on the phone beside the battery → paste the BMS's advertised name and service UUIDs here (a `0xFF00` service with `FF01` / `FF02` characteristics is JBD — an evening's firmware; Daly and JK have their own; nothing recognisable → the Android HCI snoop log and Wireshark, a weekend; authenticated or encrypted → the shunt is the answer, not a project). The reliable route to the same numbers either way is a **Victron SmartShunt** (~$130, on the negative at the G4 placement): voltage, current, its own state of charge, consumed Ah, temperature, over published Bluetooth advertisements or a VE.Direct serial line, and it sees the amplifier and every leak the BMS cannot. **Recommend both** — the shunt for what the car logs, the BMS decoded as a bonus. **Say: shunt now / shunt later / BMS only — and paste the UUIDs.**
**SOLVE:** we already started the decode:
That's the battery — IC-12V40-S9H, Ionic 12 V 40 Ah S9H. And you got further than a service list: that Last Read on FFE1 is live cell data.
What the device is
FFE0/FFE1 is the classic transparent-serial profile (Telink/HM-10 class module) — one characteristic used both directions: you write a command to FFE1, responses come back as notifications on FFE1. FEE7 is advertised but doesn't appear in the connected GATT, which almost always means an OTA/DFU service that only materialises in bootloader mode.
Leave FEE7 and anything labelled DFU completely alone. That's the firmware update path on the BMS that runs your car's power. There is no upside and the downside is a bricked pack.
The good news is that FFE1 answered a plain Read with real data, so you may not need the command protocol at all for basic telemetry.
The frame decodes cleanly
7E 01 08 | E4 08 E4 08 E3 08 E3 08 | FC 0D
Read that as a textbook framed packet: 7E start of frame, 01 message type, 08 payload length — and 8 bytes of payload is exactly what follows, as four little-endian uint16s, then FC checksum and 0D (carriage return) as the terminator. Thirteen bytes, everything accounted for.
The four values: 2276, 2276, 2275, 2275.
Four near-identical numbers is the signature of a 4S pack with well-balanced cells — a one-count spread across the pack, which is a healthy battery. What's left is the scale.
And here's the cross-check that makes me fairly confident: the four counts sum to 9102. Your advertisement's manufacturer data starts CC 32, which as a little-endian uint16 is 13004 — i.e. 13.004 V, a completely plausible resting pack voltage. 13004 ÷ 9102 works out to ~1.43 mV per count. Two independent readings, four minutes apart, agreeing on the same pack voltage. That's not a coincidence I'd bet against.
So the working model:
FFE1, type 01 = four cell voltages, ~1.43 mV/count → 3.25 V per cell, pack 13.0 V
Advertising manufacturer data, first two bytes = pack millivolts, broadcast without a connection
i do not understand what is needed to best get the needed data over bluetoth to the esp32

### BLK-004 · electrical-build → D-318, D-325
**Ask** Does CAN2 go to the rear?
**Why** Carried from Q-134
**Carried from** Q-134
**Detail**
CAN2 reaches the engine bay (`L1-S1 9/10`) and the dash drops. **There is no CAN in L4.** A rear node is not hypothetical - the Ionic's BLE telemetry gateway, a reversing camera, tyre pressure, a hatch module - and `L4-S 3` and `4` sit as sealing plugs, exactly a twisted pair, with the YEL/GRN already carted.
**Recommend:** run the pair now and make the bus a proper line - **engine bay <- dash node -> rear**, 120 Ohm at both physical ends, the PMU's software termination **OFF** so it becomes a short stub rather than an end. A 16 ft unterminated stub off a 500 kbps bus cannot be bolted on later.
**Flip it if:** the gateway will live behind the dash and BLE reaches the cargo bin reliably - test with a phone before deciding.
**Costs:** two contacts, carted wire, one 120 Ohm resistor (P070 carries ten), one config change.
**SOLVE:** tested with my phone, and it will reliably view the battery telemetry from much farther than the dash. I have no wish to ever put any cameras of any sort on this vehicle ever. I do want TPMS and suspect the generalized 10-30 feet tpms sensor radio range will be plenty for the receiver to live in the dash ang gather both tpms and battery information leaving the CAN only at the front
I also do not want the ecu in the engine bay like you say (I want as stripped clean of an engine bay as possible and do not want to put anything there unless there is no way to avoid it). the ECU will also be a dash node localized with all the other computers and more intircate wiring, then only the small branches travel everywhere. so that being said CAN should only ever stay inside the dashboard out of sight

### BLK-005 · electrical-build → D-319
**Ask** Should the master disconnect go back to the positive side?
**Why** Carried from Q-135
**Carried from** Q-135
**Detail**
D-245 put the switch in the battery negative, and its reasoning held as far as it went: with the negative open, a positive-to-chassis fault has no return path. The benchmark found three arguments the other way that were not considered.
**(1) Convention.** ABYC E-9.10.c puts the switch in the cranking-motor supply. NHRA requires the positive side verbatim. NEC 404.2(B) states the general principle - do not switch the grounded conductor. Anyone who works on this car, a first responder included, will expect a positive-side kill.
**(2) The negative leg is unfused by definition.** Any parallel negative bond - a shunt, a battery monitor sense lead, the pack's BMS or heater return, a trickle charger left connected - silently becomes the return path for the whole system.
**(3)** With the switch open and the engine running, the battery negative post floats at (Vsys - Vbat) above chassis and sits near spike potential during a load dump.
**Recommend:** **one positive-side switch at the battery carrying both branches** - the Class-T/PMU leg and the MRBF/starter leg - so opening it genuinely kills the car, on the side everyone expects. Keep post-to-switch-to-fuses in inches, as D-062 already demands. Pair with `Q-137`.
**Costs:** none - the switch is carted; cable lengths shift by a foot.
**SOLVE:** follow recommendations and switch positive side

### BLK-006 · electrical-build → D-320
**Ask** Kick-down: reproduce, delete deliberately, or defer?
**Why** Carried from Q-136
**Carried from** Q-136
**Detail**
The 1982 component list carries a **kick-down switch (B-32)** at the throttle pedal and a **kick-down solenoid (B-33)** on the transmission - two wires, automatic-only. It appears in no cavity, no device row and no decision, and it is **not** on D-097's deliberate-deletion list. Without it the transmission will not force a downshift at wide-open throttle.
**Options: (a)** reproduce it - one dash-local conductor to the pedal box, one down the tunnel; **(b)** delete it deliberately and log it beside D-097; **(c)** run and cap the tunnel conductor now, decide later.
**Recommend (c) at minimum** - the tunnel is open once. **Blocks:** the L4 cut list.
**SOLVE:** option A, as i think the switch and solenoid are functioning as expected now in the car (kickdown seams to work) we should incorporate the kick down into the wiring and keep it operational

### BLK-007 · electrical-build → BLK-019
**Ask** The alternator has no disconnect path, and lithium makes a load dump worse
**Why** Carried from Q-137
**Carried from** Q-137
**Detail**
ISO 7637-2 pulse **5a** - an unsuppressed load dump on a 12 V system - is **65-87 V for 40-400 ms**. Reports on lithium BMS disconnects run **120 V+**. Two triggers, and the second needs no mistake and never goes away: **opening the master with the engine running** (Blue Sea: *"the voltage will increase due to the sudden elimination of the load. This will burn the diodes out in the rectifier quickly"*), and **the BMS opening while driving** on over-current, cell fault or over-temperature. Lead-acid degrades gracefully and stays in circuit; a BMS opens in milliseconds at full charge current.
**Two fixes, both cheap. (a)** Swap **P049 from the Blue Sea 9003e to the 9004e** - same single-circuit e-Series switch, same 350 A continuous / 1200 A cranking, but carrying an **Alternator Field Disconnect** pole whose contacts open *slightly before* the main contacts, so the field is dead before the main path breaks. **(b)** Fit a **high-joule TVS across the PMU main feed at the module** - the only thing covering the BMS case.
**Depends on `V-002`:** AFD only works on an **externally regulated** alternator, and the 1982 diagram draws the regulator inside the alternator envelope. If internal, the aux pole must instead kill the `BW` excitation - which O12 -> F15 already controls, so the PMU can do it in logic given a switch-position input. **Resolve V-002 before ordering.**
Also ask ECUMaster directly whether the PMU's *"immunity to transients according to ISO 7637"* covers pulse **5a** (unclamped) or only **5b**. Fit the TVS either way.
**SOLVE:** i do not understand what is involved in this question the shut off switch just moved and i dont know what lternators i should prepare for
sounds like i should prepare for both

### BLK-008 · electrical-build → D-321
**Ask** The MRBF rating was ruled against a cable that has since changed
**Why** Carried from Q-138
**Carried from** Q-138
**Detail**
D-237 fixed the starter fuse at 200 A, correct **when the cable was 2 AWG** (~210 A). D-246 then took it to **1/0 (285 A)** and nobody re-opened the fuse. A fuse protects the cable, not the load, so at 1/0 the 200 A is sized to the load - conservative in the wrong direction - and the Bussmann MRBF curve is unforgiving of a long crank: **200 % (400 A) opens in max 60 s**, 135 % (270 A) in max 900 s. A hot rotary that cranks long walks up that curve.
**Recommend 250 A** (same 5191 holder, ~$17), then close `V-094` with a clamp meter on the starter cable during a hot start rather than from published curves.
**SOLVE:** follow recommendations

### BLK-009 · electrical-build → D-322
**Ask** Pick a limp-home strategy and write it into the install plan
**Why** Carried from Q-139
**Carried from** Q-139
**Detail**
No PDM vendor documents a bypass, backup module or manual override, and the corpus treats it as accepted risk - *"in the unlikely event that a PDM fails, you are pretty much done, whereas a fuse is always changeable."* The professional mitigation is carrying a spare configured unit. But that is a **racing** answer, and this is a street-registered car where brake lamps, ignition and fuel pump are all software-defined on one module that is not automotive-qualified and lives in a 44-year-old dash.
**Options, ascending: (a)** keep the config file and a USB-to-CAN cable in the car; **(b)** a one-page written emergency procedure for feeding fuel pump, ignition and brake lamps directly from the busbar; **(c)** carry a pre-configured spare PMU.
**Recommend (a) + (b)** - together they cost a cable and an afternoon. The design currently has none of the three. Field recovery from a *single* dead output is separate and already possible (D-282).
**SOLVE:** follow recommendation (i cant afford a spare pmu so definitely give my a way to fix small pmu issues on the go or enable limp mode under worse cases)

### BLK-010 · electrical-build → D-323
**Ask** The four carts are ready to pay, but four open §1 packets would change what is in them
**Why** Carried from Q-140
**Carried from** Q-140
**Detail**
Work item `A1` says to pay the four carts, and `A5` says nothing in §1 gates a cart. That was true when it was written; the 2026-09-08 sweep has since made it false. Three open §1 packets change a line that is already in a cart or add one that is not:

- `Q-137` recommends swapping **P049** (Amazon, master battery disconnect, in cart) from the Blue Sea 9003e to the 9004e, so an alternator load dump has a path.
- `Q-135` asks whether that same switch moves to the **positive** side, which changes what P049 has to carry and how it is cabled.
- `Q-138` recommends **P052** (Amazon, MRBF fuse) goes 200 A → 250 A, because D-246 took the cable to 1/0 after D-237 set the rating.
- `Q-128` recommends a shunt that has **no cart line at all** yet.

**Why it matters:** P049 and P052 are Amazon lines, the cart that is easiest to amend and the one most likely to arrive before the ruling. Buying the 9003e and the 200 A fuse and then ruling the packets means two parts bought twice.

**Options.** **(a) Rule first** — answer `Q-135`, `Q-137`, `Q-138` and `Q-128`, then pay everything once. Costs a session, no wasted parts. **(b) Pay now** — Waytek, WireBarn and DeutschConnector are untouched by these four packets, so those three carts are safe to pay today; the Amazon cart waits. **(c) Pay all now** — fastest to parts on the bench, and P049 and P052 are cheap enough to buy twice.

**Recommend (b):** pay Waytek, WireBarn and DeutschConnector today, hold the Amazon cart until the four packets are ruled. Nothing in the other three carts depends on any open §1 packet, and the long-lead Deutsch order starts moving.

**Blocks:** `A1` (pay the four carts), and the design freeze reads on §1 being empty either way.

**Say: rule first / pay now / split.**
**SOLVE:** Rule everything first i do not want to buy anything until the plan is detail for detail flawless and i undersatand like its already physcaly in the car and working perfectly

### BLK-011 · engine-swap → D-324
**Ask** What switches the A/C clutch — the DCU, or a PMU output that does not exist?
**Why** Carried from Q-400
**Carried from** Q-400
**Detail**
D-211 said "a PMU-driven clutch and a pressure transducer", but every one of the PMU's 22 outputs is allocated (O13 / O14 are the swap's ECU and fan). **Recommend:** the clutch is a comfort load — a relay whose coil the DCU switches (one of its seven comfort FETs, luxury `V-083`), contact fed from the luxury package's O15 block, the pressure transducer into a DCU input, the A/C toggle already drawn on the panel (luxury D-210). No PMU output, no harness change; the clutch feed runs from the O15 block to the engine leg at the swap. Flip it only if you want the clutch independent of the DCU — then it needs a relay socket at the dash node (K3 / K4 are empty) and a panel switch on a spare ladder state.
**SOLVE:** I want all A/C comfort controls together manged by the dcu no pmu tear down and change up

### BLK-012 · luxury-package → D-326
**Ask** Who moves the mirrors — a switch in the panel, or the DCU?
**Why** Carried from Q-305
**Carried from** Q-305
**Detail**
`L4-S2` carries the five command conductors to the sill either way. **(a)** A mechanical mirror switch (joystick + L/R selector) on the panel wired straight to `L4-S2` at the post: zero electronics, works with the DCU off, the DCU still does mirror heat. **(b)** The DCU drives them through six half-bridges and the panel sends the joystick over CAN: a knob-free panel, but bridges on H-002, firmware, and a mirror that cannot move if the DCU is down. **Recommend (a).** Flip it if the panel design has no room for a mechanical mirror control. Decides `SN17` before H-002 is laid out.
**SOLVE:** follow recommendations

### BLK-013 · luxury-package → D-327
**Ask** Stage order — climate before the display's bezel?
**Why** Carried from Q-306
**Carried from** Q-306
**Detail**
The plan puts `S2` (panel, DCU, blower — the centre-stack plastics) ahead of `S3` (the display's bezel — the binnacle plastics), because the car has no heater airflow until the blower returns (electrical D-253) and the display is already in the car on its plate (electrical D-268). **Recommend yes.** Flip it if the bare plate bothers you more than a winter without heat. Costs nothing either way — the two plastics events are independent.
**SOLVE:** follow recommendations

### BLK-014 · luxury-package → D-328
**Ask** Tank capacity for the range calculation — 15.9 or 16.6 gal?
**Why** Carried from Q-307
**Carried from** Q-307
**Detail**
`stats.h` carries 15.9 gal (D-300 confirmed it "as assumed"). The 1982 brochure (S-004, primary) says **16.6 gal**; S-015 says 16.4; S-016 says the 1981-on tank is 16.5. **Recommend 16.6** from the primary document — one constant in `stats.h`. Flip it if the tank was ever replaced or you have measured a fill.
**SOLVE:** 16.6

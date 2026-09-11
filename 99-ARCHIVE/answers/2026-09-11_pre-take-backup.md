# ANSWERS - 24 questions waiting on you

**Type your answer in the space between the `>>> ANSWER` and `<<< END` lines.**
Plain sentences are fine - no formatting, no `>` marks, no particular length.
A question you leave blank stays open and is asked again next time; there is no
cost to skipping one. Nothing else in this file is read, so scribble freely.

When you are done: save the file, then say **"I answered questions"** in a session
(or run `python tools/rx7.py take` yourself).

*Generated 2026-09-09 09:28 by `tools/rx7.py ask`. Do not rename or delete the marker lines -
they are how each answer finds its question. This file is not the record: `take`
moves your text into `data/questions/<id>.md` and archives this copy.*

Waiting on you: electrical-build 11 · luxury-package 11 · engine-swap 2

*13 more question(s) are open but belong to a later phase - install checks and measurements, asked when the plan reaches them. `python tools/rx7.py ask --all` if you want them anyway.*


---

## Q-113 · Alternator sense and phase conductors, run now and capped

*electrical-build · §1 · wants: **one word** · opened 2026-09-05 · packet `electrical-build/data/questions/Q-113.md`*

The FB is an **LR** system: `BW` is the R terminal (ignition-switched regulator wake, under 0.5 A) and `WB` is L (lamp sink). The lamp is decorative - R does the exciting, and O12 -> F15 -> L1-S1 2 is correct for it. The **'86-88 FC 70 A alternator is a bolt-in with the identical two-terminal interface**, ~$120, and the single narrow V-belt caps realistic output around 70-90 A anyway - so that is the sensible ceiling and it needs no wiring change.
What cannot be fitted today is anything **LS-type** - FD 100 A, GM CS-series, Denso 3-wire - because they need a **sense** wire and use the **lamp as the excitation path**. Two 16 AWG conductors into free `L1-S1` cavities (5, 7, 8, 12 are all sealing plugs) cover it: **S**, whose dash end lands on the **busbar** through a 3-5 A fuse rather than at the alternator stud, and **P** (phase/FR, milliamps, free insurance).
*Note against D-198:* once the ICU replaces the cluster there is no bulb, so an LS-type unit needs a **100 Ohm 5 W resistor in parallel** on the L line or it may never start charging.
**Blocks:** L1-S1's final cavity state.

>>> ANSWER Q-113 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
prepare only for a FB/FC alternator in the engine leg with no warning light (I don't know if that means I need a resistor for these alternators or not) however the pmu/relay/fuse section should be pinned and wired to work for an alternator id find on most engines id consider swapping in. just like every cuircut in the engine leg, the fuse/relay/pmu are fully dune and future prrof the engine leg is bare bones what i have now no uneeded wires just unpinned spaces on the connector to the relay/fuse/omu fully pinned connector

<<< END Q-113 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-114 · The wiper park sense is the one place a replacement motor will not fit

*electrical-build · §1 · wants: **one word** · opened 2026-09-05 · packet `electrical-build/data/questions/Q-114.md`*

Replacement two-speed motors sort into five families. The fitted one (Japanese OE pattern) brings the cam out as a **dry SPDT** - what the A3 ladder assumes, and correct. But the most common universal on the shelf today is the **Bosch/SWF/Valeo DIN 72552 family**, which is self-parking: the cam's common is the **low-brush node**, `53a` wants a permanent +12, `53e` is the brake throw, and reading either would put battery volts and brush spikes onto A3.
**Recommend:** promote **`L2-S 4`** (sealing plug) to a capped `WIPER_PARK_RET` conductor, hold **`L2-M 8`** as a fused park feed, and specify the A3 wiper-park leg as **clamped and 12 V tolerant** at the resistor sub-assembly. Two cavities, and the whole replacement population fits.

>>> ANSWER Q-114 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
follow recommendations, prepare for both wires through the front leg, however when the wiper branches off solo only the one needed wire continues after the branch to the part, then if I use other wipers I just pull that tiny branch and pin the second wire (all casis/body/intitor shoud follow this patter for future circuts)

<<< END Q-114 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-134 · Does CAN2 go to the rear?

*electrical-build · §1 · wants: **one word** · opened 2026-09-08 · packet `electrical-build/data/questions/Q-134.md`*

CAN2 reaches the engine bay (`L1-S1 9/10`) and the dash drops. **There is no CAN in L4.** A rear node is not hypothetical - the Ionic's BLE telemetry gateway, a reversing camera, tyre pressure, a hatch module - and `L4-S 3` and `4` sit as sealing plugs, exactly a twisted pair, with the YEL/GRN already carted.
**Recommend:** run the pair now and make the bus a proper line - **engine bay <- dash node -> rear**, 120 Ohm at both physical ends, the PMU's software termination **OFF** so it becomes a short stub rather than an end. A 16 ft unterminated stub off a 500 kbps bus cannot be bolted on later.
**Flip it if:** the gateway will live behind the dash and BLE reaches the cargo bin reliably - test with a phone before deciding.
**Costs:** two contacts, carted wire, one 120 Ohm resistor (P070 carries ten), one config change.

>>> ANSWER Q-134 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
tested with my phone, and it will reliably view the battery telemetry from much farther than the dash. I have no wish to ever put any cameras of any sort on this vehicle ever. I do want TPMS and suspect the generalized 10-30 feet tpms sensor radio range will be plenty for the receiver to live in the dash ang gather both tpms and battery information leaving the CAN only at the front
I also do not want the ecu in the engine bay like you say (I want as stripped clean of an engine bay as possible and do not want to put anything there unless there is no way to avoid it). the ECU will also be a dash node localized with all the other computers and more intircate wiring, then only the small branches travel everywhere. so that being said CAN should only ever stay inside the dashboard out of sight
<<< END Q-134 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-135 · Should the master disconnect go back to the positive side?

*electrical-build · §1 · wants: **one word** · opened 2026-09-08 · packet `electrical-build/data/questions/Q-135.md`*

D-245 put the switch in the battery negative, and its reasoning held as far as it went: with the negative open, a positive-to-chassis fault has no return path. The benchmark found three arguments the other way that were not considered.
**(1) Convention.** ABYC E-9.10.c puts the switch in the cranking-motor supply. NHRA requires the positive side verbatim. NEC 404.2(B) states the general principle - do not switch the grounded conductor. Anyone who works on this car, a first responder included, will expect a positive-side kill.
**(2) The negative leg is unfused by definition.** Any parallel negative bond - a shunt, a battery monitor sense lead, the pack's BMS or heater return, a trickle charger left connected - silently becomes the return path for the whole system.
**(3)** With the switch open and the engine running, the battery negative post floats at (Vsys - Vbat) above chassis and sits near spike potential during a load dump.
**Recommend:** **one positive-side switch at the battery carrying both branches** - the Class-T/PMU leg and the MRBF/starter leg - so opening it genuinely kills the car, on the side everyone expects. Keep post-to-switch-to-fuses in inches, as D-062 already demands. Pair with `Q-137`.
**Costs:** none - the switch is carted; cable lengths shift by a foot.

>>> ANSWER Q-135 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
follow recommendations and switch positive side

<<< END Q-135 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-136 · Kick-down: reproduce, delete deliberately, or defer?

*electrical-build · §1 · wants: **one word** · opened 2026-09-08 · packet `electrical-build/data/questions/Q-136.md`*

The 1982 component list carries a **kick-down switch (B-32)** at the throttle pedal and a **kick-down solenoid (B-33)** on the transmission - two wires, automatic-only. It appears in no cavity, no device row and no decision, and it is **not** on D-097's deliberate-deletion list. Without it the transmission will not force a downshift at wide-open throttle.
**Options: (a)** reproduce it - one dash-local conductor to the pedal box, one down the tunnel; **(b)** delete it deliberately and log it beside D-097; **(c)** run and cap the tunnel conductor now, decide later.
**Recommend (c) at minimum** - the tunnel is open once. **Blocks:** the L4 cut list.

>>> ANSWER Q-136 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
option A, as i think the switch and solenoid are functioning as expected now in the car (kickdown seams to work) we should incorporate the kick down into the wiring and keep it operational

<<< END Q-136 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-137 · The alternator has no disconnect path, and lithium makes a load dump worse

*electrical-build · §1 · wants: **one word** · opened 2026-09-08 · packet `electrical-build/data/questions/Q-137.md`*

ISO 7637-2 pulse **5a** - an unsuppressed load dump on a 12 V system - is **65-87 V for 40-400 ms**. Reports on lithium BMS disconnects run **120 V+**. Two triggers, and the second needs no mistake and never goes away: **opening the master with the engine running** (Blue Sea: *"the voltage will increase due to the sudden elimination of the load. This will burn the diodes out in the rectifier quickly"*), and **the BMS opening while driving** on over-current, cell fault or over-temperature. Lead-acid degrades gracefully and stays in circuit; a BMS opens in milliseconds at full charge current.
**Two fixes, both cheap. (a)** Swap **P049 from the Blue Sea 9003e to the 9004e** - same single-circuit e-Series switch, same 350 A continuous / 1200 A cranking, but carrying an **Alternator Field Disconnect** pole whose contacts open *slightly before* the main contacts, so the field is dead before the main path breaks. **(b)** Fit a **high-joule TVS across the PMU main feed at the module** - the only thing covering the BMS case.
**Depends on `V-002`:** AFD only works on an **externally regulated** alternator, and the 1982 diagram draws the regulator inside the alternator envelope. If internal, the aux pole must instead kill the `BW` excitation - which O12 -> F15 already controls, so the PMU can do it in logic given a switch-position input. **Resolve V-002 before ordering.**
Also ask ECUMaster directly whether the PMU's *"immunity to transients according to ISO 7637"* covers pulse **5a** (unclamped) or only **5b**. Fit the TVS either way.

>>> ANSWER Q-137 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
i do not understand what is involved in this question the shut off switch just moved and i dont know what lternators i should prepare for
sounds like i should prepare for both
<<< END Q-137 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-138 · The MRBF rating was ruled against a cable that has since changed

*electrical-build · §1 · wants: **one word** · opened 2026-09-08 · packet `electrical-build/data/questions/Q-138.md`*

D-237 fixed the starter fuse at 200 A, correct **when the cable was 2 AWG** (~210 A). D-246 then took it to **1/0 (285 A)** and nobody re-opened the fuse. A fuse protects the cable, not the load, so at 1/0 the 200 A is sized to the load - conservative in the wrong direction - and the Bussmann MRBF curve is unforgiving of a long crank: **200 % (400 A) opens in max 60 s**, 135 % (270 A) in max 900 s. A hot rotary that cranks long walks up that curve.
**Recommend 250 A** (same 5191 holder, ~$17), then close `V-094` with a clamp meter on the starter cable during a hot start rather than from published curves.

>>> ANSWER Q-138 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
follow recommendations

<<< END Q-138 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-139 · Pick a limp-home strategy and write it into the install plan

*electrical-build · §1 · wants: **one word** · opened 2026-09-08 · packet `electrical-build/data/questions/Q-139.md`*

No PDM vendor documents a bypass, backup module or manual override, and the corpus treats it as accepted risk - *"in the unlikely event that a PDM fails, you are pretty much done, whereas a fuse is always changeable."* The professional mitigation is carrying a spare configured unit. But that is a **racing** answer, and this is a street-registered car where brake lamps, ignition and fuel pump are all software-defined on one module that is not automotive-qualified and lives in a 44-year-old dash.
**Options, ascending: (a)** keep the config file and a USB-to-CAN cable in the car; **(b)** a one-page written emergency procedure for feeding fuel pump, ignition and brake lamps directly from the busbar; **(c)** carry a pre-configured spare PMU.
**Recommend (a) + (b)** - together they cost a cable and an afternoon. The design currently has none of the three. Field recovery from a *single* dead output is separate and already possible (D-282).

>>> ANSWER Q-139 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
follow recommendation (i cant afford a spare pmu so definitely give my a way to fix small pmu issues on the go or enable limp mode under worse cases)

<<< END Q-139 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## T-017 · Verify the connector pin letters in `01-REFERENCE/factory-circuits/` against the diagram scans

*electrical-build · §1 · wants: **one word** · packet `electrical-build/data/questions/T-017.md`*

The two-letter factory colours in design §12 are what a new wire lands on; a wrong letter there sends a conductor to the wrong terminal, and nothing downstream catches it — continuity testing proves the harness is built as drawn, not that the drawing is right. A desk check with the scans open, before the measurement day. This is the one remaining item where the *design* could still be wrong rather than merely unconfirmed.

>>> ANSWER T-017 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


<<< END T-017 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-128 · Battery data — the source: the Ionic's BMS, a shunt, or both?

*electrical-build · §1 · wants: **Say: shunt now / shunt later / BMS only — and paste the UUIDs.** · opened 2026-09-08 · packet `electrical-build/data/questions/Q-128.md`*

*(the ESP32-C3 is in — D-267, confirmed 2026-09-08 ("include the esp32 for sure"); this packet is only the source)*
The dev board (`P116`) tries the Ionic decode. **The twenty-minute test, yours:** nRF Connect on the phone beside the battery → paste the BMS's advertised name and service UUIDs here (a `0xFF00` service with `FF01` / `FF02` characteristics is JBD — an evening's firmware; Daly and JK have their own; nothing recognisable → the Android HCI snoop log and Wireshark, a weekend; authenticated or encrypted → the shunt is the answer, not a project). The reliable route to the same numbers either way is a **Victron SmartShunt** (~$130, on the negative at the G4 placement): voltage, current, its own state of charge, consumed Ah, temperature, over published Bluetooth advertisements or a VE.Direct serial line, and it sees the amplifier and every leak the BMS cannot. **Recommend both** — the shunt for what the car logs, the BMS decoded as a bonus. **Say: shunt now / shunt later / BMS only — and paste the UUIDs.**

>>> ANSWER Q-128 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
we already started the decode:
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
<<< END Q-128 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-140 · The four carts are ready to pay, but four open §1 packets would change what is in them

*electrical-build · §1 · wants: **Say: rule first / pay now / split.** · opened 2026-09-08 · packet `electrical-build/data/questions/Q-140.md`*

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

>>> ANSWER Q-140 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Rule everything first i do not want to buy anything until the plan is detail for detail flawless and i undersatand like its already physcaly in the car and working perfectly 

<<< END Q-140 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## V-040 · Aeromotive Phantom 340 draw at target pressure

*engine-swap · §1 · wants: **one word** · packet `engine-swap/data/questions/V-040.md`*

Sets the fuel-pump soft fuse when the in-tank pump replaces the Carter P4070 (D-173). From the Aeromotive spec; nothing to do until the pump is chosen.

>>> ANSWER V-040 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


<<< END V-040 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-400 · What switches the A/C clutch — the DCU, or a PMU output that does not exist?

*engine-swap · §1 · wants: **one word** · opened 2026-09-07 · packet `engine-swap/data/questions/Q-400.md`*

D-211 said "a PMU-driven clutch and a pressure transducer", but every one of the PMU's 22 outputs is allocated (O13 / O14 are the swap's ECU and fan). **Recommend:** the clutch is a comfort load — a relay whose coil the DCU switches (one of its seven comfort FETs, luxury `V-083`), contact fed from the luxury package's O15 block, the pressure transducer into a DCU input, the A/C toggle already drawn on the panel (luxury D-210). No PMU output, no harness change; the clutch feed runs from the O15 block to the engine leg at the swap. Flip it only if you want the clutch independent of the DCU — then it needs a relay socket at the dash node (K3 / K4 are empty) and a panel switch on a spare ladder state.

>>> ANSWER Q-400 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
I want all A/C comfort controls together manged by the dcu no pmu tear down and change up

<<< END Q-400 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-306 · Stage order — climate before the display's bezel?

*luxury-package · §1 · wants: **one word** · opened 2026-09-07 · packet `luxury-package/data/questions/Q-306.md`*

The plan puts `S2` (panel, DCU, blower — the centre-stack plastics) ahead of `S3` (the display's bezel — the binnacle plastics), because the car has no heater airflow until the blower returns (electrical D-253) and the display is already in the car on its plate (electrical D-268). **Recommend yes.** Flip it if the bare plate bothers you more than a winter without heat. Costs nothing either way — the two plastics events are independent.

>>> ANSWER Q-306 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
follow recommendations

<<< END Q-306 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-305 · Who moves the mirrors — a switch in the panel, or the DCU?

*luxury-package · §1 · wants: **one word** · opened 2026-09-07 · packet `luxury-package/data/questions/Q-305.md`*

`L4-S2` carries the five command conductors to the sill either way. **(a)** A mechanical mirror switch (joystick + L/R selector) on the panel wired straight to `L4-S2` at the post: zero electronics, works with the DCU off, the DCU still does mirror heat. **(b)** The DCU drives them through six half-bridges and the panel sends the joystick over CAN: a knob-free panel, but bridges on H-002, firmware, and a mirror that cannot move if the DCU is down. **Recommend (a).** Flip it if the panel design has no room for a mechanical mirror control. Decides `SN17` before H-002 is laid out.

>>> ANSWER Q-305 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
follow recommendations

<<< END Q-305 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-307 · Tank capacity for the range calculation — 15.9 or 16.6 gal?

*luxury-package · §1 · wants: **one word** · opened 2026-09-07 · packet `luxury-package/data/questions/Q-307.md`*

`stats.h` carries 15.9 gal (D-300 confirmed it "as assumed"). The 1982 brochure (S-004, primary) says **16.6 gal**; S-015 says 16.4; S-016 says the 1981-on tank is 16.5. **Recommend 16.6** from the primary document — one constant in `stats.h`. Flip it if the tank was ever replaced or you have measured a fill.

>>> ANSWER Q-307 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
16.6

<<< END Q-307 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## V-083 · DCU carrier parts

*luxury-package · §1 · wants: **one word** · packet `luxury-package/data/questions/V-083.md`*

— second LMR33630 for the servo rail, AOD4184-class FETs ×7, INA180 + 5 mΩ, and — if `Q-305` says (b) — six half-bridges. Datasheet-verify before layout.

>>> ANSWER V-083 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


<<< END V-083 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-303 · A heated washer nozzle (and park de-icer) that fits the FB cowl

*luxury-package · §1 · wants: **one word** · opened 2026-09-07 · packet `luxury-package/data/questions/Q-303.md`*

The feed is run — `L2-S 6`, ending in the `L2-NZL` receptacle at the cowl (electrical D-274), a comfort-bus load the DCU switches. A nozzle with an integral PTC heater in the factory hole pattern and hose size, or a universal heated nozzle on an adapter plate, plus whether a wiper-park de-icer strip is wanted on the same feed; nozzles ground at the front star, not through the hood hinge. Your condition stands: it goes in only if one can be made to work; if none can, the receptacle stays capped and nothing is lost.

>>> ANSWER Q-303 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


<<< END Q-303 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-300 · Which mirror?

*luxury-package · §1 · wants: **one word** · packet `luxury-package/data/questions/Q-300.md`*

D-305 settled the feature set — adjustment and heat only. The doors impose the part: a **conventional 3-wire motor pair** (common + X + Y) with a **resistive** heater on its own feed. A 5-wire, LIN-bus or module-driven mirror needs conductors the doors do not have and never will. Filter every candidate on its wiring diagram, not its photograph.

>>> ANSWER Q-300 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


<<< END Q-300 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## Q-048 · Which DOT-compliant headlamp unit goes in the retained pop-up buckets?

*luxury-package · §1 · wants: **one word** · packet `luxury-package/data/questions/Q-048.md`*

(a) 4×6 rectangular LED on an adapter plate · (b) 5×7 · (c) 7-inch round LED with a rectangular-looking element, no plate. **Recommend (c)** unless `V-066` finds the bucket already rectangular. Nothing electrical changes either way.

>>> ANSWER Q-048 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


<<< END Q-048 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## V-064 · A DOT/SAE LED module source, red and white, with published candela

*luxury-package · §1 · wants: **one word** · packet `luxury-package/data/questions/V-064.md`*

for the tail-light strips. A module without published candela cannot be shown to meet FMVSS 108 and is not a candidate.

>>> ANSWER V-064 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


<<< END V-064 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## T-032 · The release triggers, and the hatch latch switch (broken, K-016)

*luxury-package · §1 · wants: **one word** · packet `luxury-package/data/questions/T-032.md`*

Both solenoids exist and are wired to — `L4-M 3 / 4` run all the way to them, their post ends capped (electrical D-274). What is left: the trigger per D-180 (the K3 / K4 sockets at the dash node are the slot) and the latch switch (LP24). Nothing to source for the solenoids themselves.

>>> ANSWER T-032 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


<<< END T-032 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## V-063 · Tail-light aperture [M-DAY]

*luxury-package · §1 · wants: **one word** · packet `luxury-package/data/questions/V-063.md`*

— width, height, depth, mounting. D-107's 55 cm² of red against FMVSS 108's 50 has no margin for a wrong assumption.

>>> ANSWER V-063 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


<<< END V-063 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

---

## V-066 · What headlamps are actually fitted today [M-DAY]

*luxury-package · §1 · wants: **one word** · packet `luxury-package/data/questions/V-066.md`*

— round or rectangular, and whether LED housings are already in. Decides `Q-048`.

>>> ANSWER V-066 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


<<< END V-066 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

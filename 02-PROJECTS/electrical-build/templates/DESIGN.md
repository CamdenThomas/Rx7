<!-- out: 01-DESIGN/DESIGN.md -->
# ELECTRICAL BUILD — THE DESIGN

**1982 Mazda RX-7 (FB) · 12A / Weber · automatic · full replacement of the factory electrical system.**

This document is the complete design. Everything a reviewer needs to validate it is in this folder: this file, `GLOSSARY.md` for the notation, and the drawings in `diagrams/`. It contains no purchasing information and no build sequence — those live in their own sections and are derived from this one.

## What the system is

An ECUMaster PMU-24 DL solid-state power module replaces the factory fuse box, relays, flasher and control unit. Every load in the car is switched by one of its 22 outputs and protected by a software current limit on that output. Every switch in the car is read as a resistor ladder on one wire into one of its analog inputs, so no switch carries load current. A rear-mounted lithium battery feeds the module through a Class-T fuse over a single 2 AWG cable; the starter has its own cable off the battery post. Four harness legs leave the dash node through Deutsch connectors, cut by what comes out of the car as one piece. The factory instrument cluster stays and is fed from day one. Everything the car may gain later — power windows, mirrors, heated seats, a climate module, a digital cluster, a control panel — has its wire run now, terminated and capped, so no future project reopens the interior.

## Scope

| In this design | Not in this design |
|---|---|
| Battery relocation and the power backbone | Any luxury-package hardware — window motors, mirrors, seat heaters, climate module, digital cluster, control panel, LED lamps, A/C |
| The dash node — PMU, busbars, fuse blocks, relays, wake circuit | The design of those future subsystems — only their conductors appear here, as capped wires |
| Four harness legs, the sill node, five dash-post drops | The audio system — the amplifier has its own power and is isolated from every other system (D-230); only the head unit is a load here |
| Every switch, ladder, sender and lamp the car needs to drive, day and night, in rain | The LS engine swap — its outputs, CAN drop and sensor cavities are reserved and capped |
| The ICU and its 12.3-inch display — the instruments from the meters cutover (D-259, D-268) | The bezel and dash plastics around the display |

**Status words used throughout:** **LIVE** — wired, connected, enabled. **CAPPED** — wire run, terminated in its cavity, far end sealed and labelled. **PLUG** — a cavity with no circuit assigned: fitted with a sealing plug in both halves, no wire, no contact. **RESERVED** — the receptacle half is pinned from the PMU or a fuse position at the post, the plug half carries a sealing plug, and no conductor runs down the leg (D-271): the harness is ready for a future engine at the connector, never in the bay. **EMPTY** — relay socket or fuse holder fitted and labelled with nothing in it.


---

## 1 · The system in one picture

![architecture](diagrams/00-architecture.svg)

{{counts}}

---

## 2 · Power backbone

![backbone](diagrams/01-power-backbone.svg)

The Ionic S9 (LiFePO4, 40 Ah, 1,100 CCA, built-in heater, Group 25 case) sits in the cargo bin clamped against g-load in every axis over a backing plate, both posts booted (no box — D-229; boots are the whole of the terminal covering, deliberately, so a post stays reachable for a jump start — D-235). Its case measures 170 W × 230 L × 190 H mm (`params.battery_case_mm`, D-239), and its posts are SAE tapered, so every cable end is a brass post clamp with a 3/8 in stud take-off rather than a ring lug (D-234). Two runs leave the positive post and they never share a fuse:

{{backbone}}

At the dash post the 2 AWG lands directly on the always-hot busbar. The busbar feeds the PMU stud over a 2 AWG jumper of a few inches (D-241) and, through fuse block A and relay K11, the handful of loads that must live outside the PMU (§5).


---

## 3 · Protection schedule

**Two layers.** Every PMU output is a software current limit that protects the wire from that pin to the device. Where one output feeds several branches through a bus, each branch gets a blade fuse so a fault on one branch cannot take the others down. The heavy cables are fused at their source.

{{fuses}}

### Fuse blocks on the dash node — one source per block

{{fuse_blocks}}

F12, F15, F16 and F20 are sealed inline holders at the dash node; F8, F9 and F14 are labelled positions at the sill node with no holder until the windows and mirrors arrive; F17 and F18 are bolt-down MIDI holders beside the starter stud. There is no fuse on the O1 → K1 / K2 branches (two identical 12 AWG runs carrying one function; the 25 A soft fuse protects either) and none on O15 (no load this build). F12 stays because a shorted interior lamp must not take the illumination bus and the cluster feed down with it at night.


### Software limits — the rule

A limit is set from a measured figure, never from an estimate. Motors: measured stall × 1.10. Filament lamps: measured steady × 1.35 plus an inrush window (a cold filament pulls 8–12× for a few milliseconds). Resistive: measured cold × 1.20. Electronics: measured steady × 1.50. Round up to 0.5 A. Until a channel has been measured it runs at its channel cap — the limit still protects the wire, because every wire is sized above its limit — and the PMU's own current telemetry provides the measurement in the first week of driving, after which each limit is tightened. The values in §4 are the enable-at values. The four 15 A outputs that reach their loads through DT size-16 contacts (O8–O11) cap at **13.0 A**, the contact's continuous rating (D-223).


---

## 4 · The PMU — every pin

**Device:** ECUMaster PMU-24 DL. 39-way SICMA connector, 150 A stud. Outputs: O1–O5 and O12–O16 25 A · O6–O11 15 A · O17–O24 7 A. O1 and O16 carry integrated flyback diodes; O8 has wiper-motor braking. A1–A8 are dedicated 0–5 V 10-bit inputs; A9–A16 share the O17–O24 pins, 0–20 V 12-bit. CAN1 is fixed at 1 Mbps with no internal termination; CAN2 has software termination.

**Terminals:** 2.8 mm large `211CC3S3120` for the ten 25 A outputs and ground (10–12 AWG) · 2.8 mm `211CC3S2120` for pin 15 (14–16 AWG) · 1.5 mm `211CC2S2160P` for everything else (14–17 AWG). **Signal wire is 16 AWG. 14 AWG is the heaviest a 15 A output can take.**


### 4.1 · Pin allocation

{{pins}}

**Cav:** L = large 2.8 mm cavity · M = 2.8 mm (pin 15 only) · S = 1.5 mm. **Enable at:** the software limit typed in before the channel is first enabled — *meas* is a measured figure, *cap* is the channel cap pending telemetry.


### 4.2 · Connector geometry, looking at the device

```
   1:O13    2:O12    3:O11    4:O10    5:O9     6:O17    7:+12V   8:O22    9:O8    10:O7    11:O6    12:O5    13:O4      ← row 1
  14:O14   15:+5V   16:A2    17:A4    18:A6    19:A8    20:O19   21:O21   22:A16   23:CAN1H 24:CAN2H 25:GND   26:O3      ← row 2
  27:O15   28:O16   29:A1    30:A3    31:A5    32:A7    33:O18   34:O20   35:A15   36:CAN1L 37:CAN2L 38:O1    39:O2      ← row 3
```

Pin 1 is top-left with the purple lock on the right and the connector face toward you. Each row is 2 large · 9 small · 2 large; the large cavities are 1, 2, 12, 13, 14, 15, 25, 26, 27, 28, 38, 39. Enclosure 131 × 112.1 × 32.5 mm, three Ø6.5 mm mounts, connector on the short edge, stud opposite. Leave a clear arc for the lever.


### 4.3 · Wire colour code

A wire's colour says which family it belongs to; the printed label at each end says which wire it is (install plan, Appendix A). The colour is never the identity — the label and the cavity number are. Wire is bought as solid colours only.

{{colours}}

Two wires of the same colour and gauge are told apart only by their labels, so a label goes on the moment a wire is cut, before it goes anywhere. Where several wires of one family meet at a device or a splice, the label pairs in the install plan's cut list are the record, not the colour.

This is **not** the factory scheme. Factory colours are two-letter codes (first letter base, second tracer; `GY` is green/yellow, not grey) and appear in this document only to identify the terminal a new wire lands on.


---

## 5 · The dash node

The dash node is everything between the 2 AWG feed and the harness legs: the PMU, the always-hot busbar, the ground bus, two single-source fuse blocks, four sealed inline fuses, six relay sockets (four populated), the wake strip with its two sense stages, the two bias resistors, the wideband gauge hidden behind the dash (D-244), and the receptacle for every leg and drop. It is not one plate. It mounts on one or more small carrier panels low in the dash, laid out with the parts in hand once the envelope is measured (§5.4), and the electrical design does not depend on how it is split — every conductor in §5.3 is the same whether the pieces share a panel or not. Nothing on the dash node is spliced anywhere else; every splice in the car is either at the dash node or at a device.

![dash node](diagrams/02-dash-node-schematic.svg)


### 5.1 · Relays

{{relays}}

### 5.2 · Wake circuit

Pin 7 (+12V SW) turns the PMU on. Six sources feed it through one 1N5819 Schottky each on an 8-position barrier strip, with a 10 kΩ bleed from the rail to ground so leakage can never hold the module awake: **ACC** and **RUN** from the ignition switch (raw 12 V, one conductor each), **the door node** and **the horn/hazard/wink node** through the two sense stages, **the brake pedal switch's second pole** (D-247, so a pushed or towed car still lights its brake lamps), and **O22**, the PMU's own keep-alive latch. The strip has two spare positions.


Two identical NPN sense stages on the dash node (2N3904 / 2N2222 class), one on the A6 node and one on the A8 node. Base ← node through 100 kΩ · 1 MΩ from the node to the F3 rail · emitter → GND bus · collector → 100 kΩ to the F3 rail and → its wake-strip diode. Node idle (open switch): the node sits at ~4–12 V, the transistor is ON, the collector is LOW — no wake. Any switch on that node closes to ground: base falls, transistor OFF, collector rises to 12 V through the pull-up — wake. The 1 MΩ injects ~7 µA into the ladder while awake (about 1.5 ADC counts); the decode windows absorb it.


O22 (`KEEP_ALIVE`) lets the PMU finish its own shutdown — the interior-lamp fade, saving state — then release pin 7 and sleep. It also drives K11, so the head-unit constant drops when the car sleeps and the sleeping draw is the PMU's own 150 mA plus nothing.


### 5.3 · Every conductor on the dash node

{{node_conductors}}

### 5.4 · Mounting

There is no layout drawing: the layout is decided with the parts on the bench and the dash envelope measured (install plan M-1 and §3.1). The rules it must satisfy:

- **Low and close to the floor**, in the centre-stack cavity freed by the radio, cassette, ashtray and lighter, and the space behind and below the glovebox. Not a sealed box — one would not fit the footwell shape.
- **Several small carrier panels are fine.** The natural split is (a) the PMU with the ground bus and the always-hot busbar — the three heaviest, shortest wires — and (b) the relays, fuse blocks, wake strip and sense-stage board. The receptacles can sit on their own strip or bracket if that fits the space better.
- **The 39-way lever needs a clear arc** and must be operable at least once with the panels fitted · **60 mm clear behind every receptacle** · **blocks A and B reachable** with the dash together.
- **Pin 25 to the ground bus** is the shortest, heaviest wire on the node (10 AWG, ≤ 6 in) · **the busbar sits beside the PMU stud** (2 AWG, ≤ 8 in — D-241).
- **The always-hot busbar is covered** — it is a live 150 A bar in a footwell.
- **Relays away from the signal receptacles** · receptacles grouped by leg so a leg unplugs as a unit · the PMU stood off its panel for airflow · no bare aluminium against a live stud.
- About 500 mm of edge in total for the receptacles.


---

## 6 · The legs

A leg is a bundle that can be removed without disturbing any other leg. Every device in a leg is fed and returned entirely within it; no ground crosses a leg connector. Power and signal ride in separate housings so a 25 A motor feed never shares a bundle with a ladder wire. Leg side is always the socket housing (`06-…S`), box side always the pin housing (`04-…P`), so a leg cannot be plugged into the wrong half.

{{series}}

**Housing schedule**

{{housings}}

### L1 · ENGINE

**Boundary** the firewall grommet — comes out for engine service or a swap. **Ground** the engine block; nothing returns through the firewall. **Rule** this leg carries only what the engine on the mounts needs today: no capped stubs for future parts — unused cavities get sealing plugs. The three LS reservations are the one exception, because the swap is a known quantity. The tach wire is shielded, grounded at the dash node end only, and rides in the signal housing away from the coil feed.

![L1 · ENGINE](diagrams/10-L1-engine.svg)


{{cavities:L1-P}}

{{cavities:L1-S1}}

{{cavities:L1-S2}}

### L2 · FRONT

**Boundary** firewall to radiator support, cowl included — comes out with the nose, bumper and pop-up assemblies. **Ground** the front star stud on the radiator support. One DTP-4 shell carries both headlight feeds and both pop-up run feeds (the motors are single-direction, so each needs one run conductor). Keep L2-S out of the L2-P bundle: pop-up motor feeds are the noisiest conductors in the nose and the ladders the most sensitive. Horns get a deliberate ground wire — the factory grounded them through their brackets.

![L2 · FRONT](diagrams/11-L2-front.svg)


{{cavities:L2-P}}

{{cavities:L2-M}}

{{cavities:L2-S}}

### L2-NZL · L2-OAT — the front leg's branch ends
Two DT-2 receptacles on the L2 loom, not at the post, where the future circuits leave the leg (D-274): **L2-NZL** at the cowl carries the heated-nozzle feed (`L2-S 6`) and **L2-OAT** ahead of the radiator the outside-air thermistor (`L2-S 5`). Both are dust-capped; the nozzle harness and the thermistor arrive with their plugs, and nothing is run past the receptacle until they do. Both loads ground at the front star.

{{cavities:L2-NZL}}

{{cavities:L2-OAT}}

### L3 · DASH

**Boundary** the dash structure. **Ground** the dash node's ground bus. Almost entirely signal: two heavy conductors, two medium and everything else 16 AWG, because every multi-position switch is a ladder on one wire. The dash node and the five drops live here but belong to no leg.

![L3 · DASH](diagrams/12-L3-dash.svg)


{{cavities:L3-P}}

{{cavities:L3-M}}

{{cavities:L3-S1}}

{{cavities:L3-S2}}

{{cavities:L3-S3}}

### L3-BLW
The blower receptacle at the HVAC case — a DTP-2 on the L3 loom, not at the post. The motor is dead (K-023) and is not replaced until the luxury package, so the receptacle is dust-capped; O16 feeds cavity 1 and cavity 2 is the 12 AWG return to the dash ground. Speed is set by a low-side final stage — ≥ 20 kHz, its own freewheel diode across the motor, mounted in the resistor pack's hole for airflow — that plugs in here as an adapter between receptacle and motor, on the DCU's own PWM output; the PMU's PWM tops out at 400 Hz, which a brushed blower would sing at, so O16 is a steady feed (D-257).

{{cavities:L3-BLW}}

### L3-CMF · L3-WIN · L3-MOD · L3-RDR — the dash leg's branch ends
The same pattern for every other future circuit on the leg (D-274): the conductor stops in a dust-capped receptacle at the point it branches off, and the part that arrives brings the plug. **L3-CMF** (DTP-2, behind the centre stack) is the O15 comfort bus — the luxury package's fuse block plugs in. **L3-WIN** (DT-6, console) carries the four window commands and, on cavity 5, the switch pack's common feed, tapped off the F3 switch supply where `L3-S2 2` passes; the commands land on the K5–K8 sockets at the sill, which is that branch's end. **L3-MOD** (DT-2, behind the dash) is the future module's switched feed and ground. **L3-RDR** (DT-4, behind the dash) is the dash end of the radar pass-through, linked at the post to `L4-S 5–7`.

{{cavities:L3-CMF}}

{{cavities:L3-WIN}}

{{cavities:L3-MOD}}

{{cavities:L3-RDR}}

### L4 · REAR

**Boundary** the tunnel entry at the console, back to the hatch, plus the sill node, where the door receptacles wait — `D1` / `D2` are RESERVED (D-274): pinned on the node side, sealing plugs in the door plugs, nothing run into a door until its harness comes with the mirror and the window. **Ground** the rear star stud in the cargo bin; the doors ground at the sill stud, never inside a door. The tunnel run is the longest in the car — voltage drop, not current, sets the 12 AWG on the defog and pump feeds. The fuel sender wire is routed apart from the fuel pump feed.

![L4 · REAR](diagrams/13-L4-rear.svg)


{{cavities:L4-P}}

{{cavities:L4-M}}

{{cavities:L4-S}}

### L4-S2
Mirror-adjust commands, dash → sill: one shared common and X/Y per side, capped at the post, spliced at the sill node onto the door receptacles (D-255). A mechanical mirror switch or the climate module's bridges land here later.

{{cavities:L4-S2}}

### L4-RDR — the rear leg's branch end
The rear end of the radar pass-through: a DT-4 receptacle at the rear node, dust-capped (D-274). The run up the hatch — across the hinge, the one place a dead wire is worst — goes in with the sensor, not now.

{{cavities:L4-RDR}}

### Sill node and the door connectors

A small panel behind the driver's kick panel: the D1 / D2 receptacles (pinned on the node side and RESERVED — the door plugs carry sealing plugs until the door harness is built, D-274), a ground stud to the chassis, four empty relay sockets and three labelled fuse positions (F8, F9, F14 — the holders come with the windows and mirrors). It is a sub-assembly of the rear leg, not a fifth leg. **No conductor on it is live in this build** — and nothing runs through a door boot: the door receptacles are pinned on the node side and their plugs sealed (RESERVED, D-274), so the door harness is built with the mirror and the window and never touches the leg. The door jamb switches are body-mounted plungers wired at the sill, not through the door connectors.

![sill](diagrams/14-sill-doors.svg)


{{cavities:D1}}

{{cavities:D2}}

---

## 7 · Dash-post drops

Five connectors on the dash node edge for devices that sit inches from it and belong to no leg. Their grounds are the only grounds in the car that cross a connector.

![drops](diagrams/15-dash-post-drops.svg)


### 7.1 · The instruments — the ICU and its display, not a cluster drop

There is no cluster drop and no temporary cluster. Every conductor the factory cluster used to receive — the three senders, the tach pulse, the charge and brake lines, the three tell-tale outputs — terminates at `DP-ICU-A` / `DP-ICU-B`, where the ICU excites the fuel and water-temp senders, reads everything and draws it on a 12.3-inch display ribboned to its own board (D-258, D-268). The oil-pressure node is the one exception to "the ICU excites": the PMU excites it (D-260) so the fuel-pump gate never depends on the ICU. The factory cluster stays alive on the *factory* harness until the meters cutover (MG22, gated on the display proven on the bench) and leaves with that harness at install §6 — nothing in the new harness was ever built for it. The display's backlight is the F16 ignition aux on `DP-ICU-A 6`; the display sits on a plain plate in the binnacle aperture until the luxury package's moulded bezel surrounds it.

### DP-DIAG
The laptop port, in the glovebox. CAN1 (with its 120 Ω inside the plug), a 2 A constant and ground. The PMU is configured through this port with the module in the car.

{{cavities:DP-DIAG}}

### DP-ICU-A
The ICU's power and bus drop — live from install (D-259). Cavities 1 · 3 · 4 · 5 are the same as DP-DCU's, so every module in the car plugs into one six-way pattern (D-252); 6 is the F16 ignition aux — the display's backlight, through the ICU (D-268).

{{cavities:DP-ICU-A}}

### DP-ICU-B
The ICU's sensor drop — live from install. The three senders, the tach, the charge and brake lines and the three tell-tale senses **terminate** here: the ICU excites the senders, reads everything, and the display draws it (D-258, D-268) — the harness has no cluster drop. Cavity 7 is a sealing plug (no oil-temperature sender on the 12A, D-264); 8 (road speed, `L4-S 3`) and 9 (the engine-leg spare) are capped and belong to `Q-309` and `Q-127`. Fuel level is here and not on the PMU; A7 reads the oil-pressure node, which the PMU itself excites (D-249, D-260).

{{cavities:DP-ICU-B}}

### DP-DCU
Future climate module. Power, ground, CAN2 — capped at the post.

{{cavities:DP-DCU}}

### DP-KEY
Future control panel. CAN2, switched 12 V, ground — a dust-capped receptacle at the post; the panel's tail plugs in.

{{cavities:DP-KEY}}

---

## 8 · Switches and how they are read

![ladders](diagrams/04-switch-ladders.svg)

**The column combination switch stays** (light / dimmer / passing, turn / hazard, wiper / washer) — it is mechanically sound. **Every other switch is new:** ignition switch (electrical portion), brake pedal switch, two wink pushbuttons, four plunger switches (door jambs, glove box, luggage lid). The horn stays on the steering pad.

**No state uses a dead short.** Every switch position reaches ground through a resistor, so an open wire reads full scale and a chafed wire reads zero — both are faults, never a position. Resistors are 1 % metal film, 1/4 W, fitted at the switch and heat-shrunk individually; one wire returns to the dash node per ladder. Decode as windows: a reading between windows is a fault, not the nearest state.


### 8.1 · Ground ladders — A1 to A8 (10-bit, internal 10 kΩ pull-up to 5 V)

`count = 1023 × R / (R + 10 000)` — with a diode in the leg, `V = 0.3 + 4.7 × R / (R + 10 000)`.


{{ladder:A1}}

{{ladder:A2}}

{{ladder:A3}}

{{ladder:A4}}

{{ladder:A5}}

{{ladder:A6}}

{{ladder:A8}}

A7 (oil pressure, D-249) is not a ladder: the node is excited by a 100 Ω 1 W pull-up from pin 15 at the dash node (D-260) and read through the same 1 MΩ pull-down as before — negligible against 100 Ω; the ICU reads the same node (D-258). Its threshold — the count below which the fuel-pump gate reads "no oil pressure" — is read in the car at commissioning from the live node at idle and at speed, never entered from a datasheet; the gate itself (START unconditional · 3 s prime · latched with a 5 s de-bounce · fails open on a FAULT reading) is in the logic table. Fuel level is no longer a PMU input: the ICU taps that node on DP-ICU-B 3 and publishes it on CAN2 (D-251). A8's HAZARD state is decoded as a band, 265–370, so a wink pressed while the hazards are on reads as HAZARD and does nothing.


### 8.2 · 12 V summed ladders — A15 and A16 (12-bit, 10 kΩ pull-down, 100 kΩ bias from +5 V)

Several contacts can be live at once (ACC stays live in RUN; HEAD keeps PARK live). Each contact feeds the node through its own resistor from the F3 switch supply; the table lists the combinations. The bias makes OFF read ~93 and a disconnected wire read 0.


{{ladder:A15}}

{{ladder:A16}}

A15 PASS is a superstate: any reading above 1750 means flash-to-pass, whatever the switch position underneath.


---

## 9 · Control logic

Written the way it is typed into the PMU client. Channel names match §4.1.

{{logic}}

### Rules

{{rules}}

![popups](diagrams/05-popups-and-wink.svg)


### CAN

**CAN1** — laptop only, 1 Mbps fixed, no internal termination: 120 Ω at the PMU pins and 120 Ω in the DP-DIAG plug, or the client will never see the device. **CAN2** — vehicle bus, 500 kbps, software termination ON at the PMU; the far-end 120 Ω sits capped at the engine-bay drop (L1-S1 9/10). Nothing else is on CAN2 in this build; the three dash drops are capped.


---

## 10 · Grounds

![grounds](diagrams/07-ground-tree.svg)

One star node per zone, each straight to bare chassis: the engine block (with its own 2 AWG strap to the body), a stud on the radiator support, the dash node's ground bus, a stud in the cargo bin (where the battery negative lands), and a stud at the sill. Every device returns to its zone's node on its own wire, sized to its feed. The fuel pump has a dedicated return — it must never share a ground with a lamp. Pin 25 carries the flyback return for every inductive load on the PMU and is the shortest, heaviest wire on the dash node.

{{grounds}}

---

## 11 · Loads and wire sizing

Wire gauge is set by voltage drop over the run and by crimp robustness, not by ampacity — every conductor is good for far more than its channel. Motors are sized for stall (roughly seven times running), lamps for cold inrush (handled by the inrush window, not the limit), the defog grid for cold (it draws most in the first thirty seconds).

{{loads}}

---

## 12 · Device terminations

The far end of every conductor. Factory two-letter colours name the terminal on the device or its plug; the factory plug is kept as a pigtail wherever one exists.

{{devices}}

---

## 13 · What to validate

The reviewer's checklist. Every line should be checkable from this folder alone.

- Every one of the 39 PMU cavities in §4.1 is allocated exactly once, and its `Goes to` appears as a `From` in a cavity table or the dash node list.
- Every LIVE cavity in §6 and §7 has a box-side source, a wire gauge and colour, and a device terminal it lands on.
- Every CAPPED cavity has a defined far-end location; every PLUG cavity has a sealing plug in both halves.
- Every relay has a coil source, a coil return, a contact source and a contact load (§5.1). K9's contact feed is fused (F17).
- Every fuse in §3 has a source and a load, and every fused branch in the cavity tables names its fuse.
- Every device in §12 has a ground path to its zone's node (§10), and the fuel pump's return is dedicated.
- Ladder windows in §8 do not overlap; the tightest gaps are A4 / A5 (44 counts) and A6 (55 counts).
- Every ladder resistor named in §12 appears in the §8 tables with the same value.
- The wake circuit (§5.2) can wake the PMU from every source that must work with the key out: hazard, horn, wink, door, brake.
- Nothing in the engine leg is a stub for a future part.
- Every conductor's gauge is at or above what its output's enable-at limit requires: 12 AWG above 15 A, 14 AWG above 13 A, 16 AWG at 13 A and below and on every signal. A 16 AWG tap off a heavier feed (an indicator, a capped module drop) is allowed only where the cavity notes it as a tap (D-232).
- The three measurements the design still waits on are only dimensions: the dash envelope for the dash node's panels, the harness routes for wire lengths, and the pop-up motor ohm check that decides whether R and RY are bridged.


*The tables in this file are the record. The install plan's tables are printed from the same rows and must never disagree with them.*

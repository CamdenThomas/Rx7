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
| The factory cluster, fed from the new harness |  |

**Status words used throughout:** **LIVE** — wired, connected, enabled. **CAPPED** — wire run, terminated in its cavity, far end sealed and labelled. **PLUG** — a cavity with no circuit assigned: fitted with a sealing plug in both halves, no wire, no contact. **EMPTY** — relay socket or fuse holder fitted and labelled with nothing in it.


---

## 1 · The system in one picture

![architecture](diagrams/00-architecture.svg)

{{counts}}

---

## 2 · Power backbone

![backbone](diagrams/01-power-backbone.svg)

The Ionic S9 (LiFePO4, 40 Ah, 1,100 CCA, built-in heater, Group 25 case) sits in the cargo bin clamped against g-load in every axis over a backing plate, both posts booted (no box — D-229; what covers the terminals beyond the boots is `Q-103`). Two runs leave the positive post and they never share a fuse:

{{backbone}}

At the dash post the 2 AWG lands directly on the always-hot busbar. The busbar feeds the PMU stud over a 4 AWG jumper of a few inches and, through fuse block A and relay K11, the handful of loads that must live outside the PMU (§5).


---

## 3 · Protection schedule

**Two layers.** Every PMU output is a software current limit that protects the wire from that pin to the device. Where one output feeds several branches through a bus, each branch gets a blade fuse so a fault on one branch cannot take the others down. The heavy cables are fused at their source.

{{fuses}}

### Fuse blocks on the dash node — one source per block

{{fuse_blocks}}

F12, F15 and F16 are sealed inline holders at the dash node; F8, F9 and F14 are labelled positions at the sill node with no holder until the windows and mirrors arrive; F17 and F18 are bolt-down MIDI holders beside the starter stud. There is no fuse on the O1 → K1 / K2 branches (two identical 12 AWG runs carrying one function; the 25 A soft fuse protects either) and none on O15 (no load this build). F12 stays because a shorted interior lamp must not take the illumination bus and the cluster feed down with it at night.


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

The dash node is everything between the 2 AWG feed and the harness legs: the PMU, the always-hot busbar, the ground bus, two single-source fuse blocks, three sealed inline fuses, six relay sockets (four populated), the wake strip with its two sense stages, the two bias resistors, and the receptacle for every leg and drop. It is not one plate. It mounts on one or more small carrier panels low in the dash, laid out with the parts in hand once the envelope is measured (§5.4), and the electrical design does not depend on how it is split — every conductor in §5.3 is the same whether the pieces share a panel or not. Nothing on the dash node is spliced anywhere else; every splice in the car is either at the dash node or at a device.

![dash node](diagrams/02-dash-node-schematic.svg)


### 5.1 · Relays

{{relays}}

### 5.2 · Wake circuit

Pin 7 (+12V SW) turns the PMU on. Five sources feed it through one 1N5819 Schottky each on an 8-position barrier strip, with a 10 kΩ bleed from the rail to ground so leakage can never hold the module awake: **ACC** and **RUN** from the ignition switch (raw 12 V, one conductor each), **the door node** and **the horn/hazard/wink node** through the two sense stages, and **O22**, the PMU's own keep-alive latch. The strip has three spare positions.


Two identical NPN sense stages on the dash node (2N3904 / 2N2222 class), one on the A6 node and one on the A8 node. Base ← node through 100 kΩ · 1 MΩ from the node to the F3 rail · emitter → GND bus · collector → 100 kΩ to the F3 rail and → its wake-strip diode. Node idle (open switch): the node sits at ~4–12 V, the transistor is ON, the collector is LOW — no wake. Any switch on that node closes to ground: base falls, transistor OFF, collector rises to 12 V through the pull-up — wake. The 1 MΩ injects ~7 µA into the ladder while awake (about 1.5 ADC counts); the decode windows absorb it.


O22 (`KEEP_ALIVE`) lets the PMU finish its own shutdown — the interior-lamp fade, saving state — then release pin 7 and sleep. It also drives K11, so the head-unit constant drops when the car sleeps and the sleeping draw is the PMU's own 150 mA plus nothing.


### 5.3 · Every conductor on the dash node

{{node_conductors}}

### 5.4 · Mounting

There is no layout drawing: the layout is decided with the parts on the bench and the dash envelope measured (install plan M-1 and §3.1). The rules it must satisfy:

- **Low and close to the floor**, in the centre-stack cavity freed by the radio, cassette, ashtray and lighter, and the space behind and below the glovebox. Not a sealed box — one would not fit the footwell shape.
- **Several small carrier panels are fine.** The natural split is (a) the PMU with the ground bus and the always-hot busbar — the three heaviest, shortest wires — and (b) the relays, fuse blocks, wake strip and sense-stage board. The receptacles can sit on their own strip or bracket if that fits the space better.
- **The 39-way lever needs a clear arc** and must be operable at least once with the panels fitted · **60 mm clear behind every receptacle** · **blocks A and B reachable** with the dash together.
- **Pin 25 to the ground bus** is the shortest, heaviest wire on the node (10 AWG, ≤ 6 in) · **the busbar sits beside the PMU stud** (4 AWG, ≤ 8 in).
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

### L3 · DASH

**Boundary** the dash structure. **Ground** the dash node's ground bus. Almost entirely signal: two heavy conductors, two medium and everything else 16 AWG, because every multi-position switch is a ladder on one wire. The dash node and the five drops live here but belong to no leg.

![L3 · DASH](diagrams/12-L3-dash.svg)


{{cavities:L3-P}}

{{cavities:L3-M}}

{{cavities:L3-S1}}

{{cavities:L3-S2}}

{{cavities:L3-S3}}

### L4 · REAR

**Boundary** the tunnel entry at the console, back to the hatch, plus the sill runs into both doors. **Ground** the rear star stud in the cargo bin; the doors ground at the sill stud, never inside a door. The tunnel run is the longest in the car — voltage drop, not current, sets the 12 AWG on the defog and pump feeds. The fuel sender wire is routed apart from the fuel pump feed.

![L4 · REAR](diagrams/13-L4-rear.svg)


{{cavities:L4-P}}

{{cavities:L4-M}}

{{cavities:L4-S}}

### Sill node and the door connectors

A small panel behind the driver's kick panel: the D1 / D2 receptacles, a ground stud to the chassis, four empty relay sockets and three labelled fuse positions (F8, F9, F14 — the holders come with the windows and mirrors). It is a sub-assembly of the rear leg, not a fifth leg. **No conductor on it is live in this build** — every door wire is run through the door boot and capped inside the door so a future door project never touches the harness. The door jamb switches are body-mounted plungers wired at the sill, not through the door connectors.

![sill](diagrams/14-sill-doors.svg)


{{cavities:D1}}

{{cavities:D2}}

---

## 7 · Dash-post drops

Five connectors on the dash node edge for devices that sit inches from it and belong to no leg. Their grounds are the only grounds in the car that cross a connector.

![drops](diagrams/15-dash-post-drops.svg)


### 7.1 · DP-CLU — the factory cluster

![cluster](diagrams/06-cluster-drop.svg)

The car keeps its instruments. One DT-12 drop feeds the cluster's ignition supply (F16), ground, illumination (the O20 PWM bus, so the cluster dims with the rest of the dash), the tachometer pulse from the trailing coil, the water-temperature and oil-pressure senders, the fuel sender, the alternator's lamp terminal, the brake-warning switches and the three indicators. The factory cluster plug is kept as a pigtail and re-terminated, so no cluster pin has to be sourced. The retractor indicator lamp is not used (its YG line is now a ladder input).

{{cavities:DP-CLU}}

### DP-DIAG
The laptop port, in the glovebox. CAN1 (with its 120 Ω inside the plug), a 2 A constant and ground. The PMU is configured through this port with the module in the car.

{{cavities:DP-DIAG}}

### DP-ICU
Future digital-cluster module. Power, ground, CAN2, illumination reference, and taps on the sensor conductors — all capped at the post.

{{cavities:DP-ICU}}

### DP-DCU
Future climate module. Power, ground, CAN2 — capped at the post.

{{cavities:DP-DCU}}

### DP-KEY
Future control panel. CAN2, switched 12 V, ground — capped behind the dash.

{{cavities:DP-KEY}}

---

## 8 · Switches and how they are read

![ladders](diagrams/04-switch-ladders.svg)

**The column combination switch stays** (light / dimmer / passing, turn / hazard, wiper / washer) — it is mechanically sound. **Every other switch is new:** ignition switch (electrical portion), brake pedal switch, blower speed switch, two wink pushbuttons, four plunger switches (door jambs, glove box, luggage lid). The horn stays on the steering pad.

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

A7 (fuel) is not a ladder: the factory gauge drives the sender and the PMU taps the node with a 1 MΩ pull-down and no pull-up. Its three-point lookup (FULL / MID / EMPTY) is read in the car at commissioning. A8's HAZARD state is decoded as a band, 265–370, so a wink pressed while the hazards are on reads as HAZARD and does nothing.


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
- The wake circuit (§5.2) can wake the PMU from every source that must work with the key out: hazard, horn, wink, door.
- Nothing in the engine leg is a stub for a future part.
- Every conductor's gauge is at or above what its output's enable-at limit requires: 12 AWG above 15 A, 14 AWG above 13 A, 16 AWG at 13 A and below and on every signal. A 16 AWG tap off a heavier feed (an indicator, a capped module drop) is allowed only where the cavity notes it as a tap (D-232).
- The three measurements the design still waits on are only dimensions: the dash envelope for the dash node's panels, the harness routes for wire lengths, and the pop-up motor ohm check that decides whether R and RY are bridged.


*The tables in this file are the record. The install plan's tables are printed from the same rows and must never disagree with them.*

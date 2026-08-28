# BUILD CHECKLIST

Tick as you go. Every step is either **[YOU]** hands-on or **[AGENT]** paperwork
Claude can do on request.

**Scope:** PMU panel · power backbone · four harness legs · sill node · DCU · ICU
**Effort:** 531–932 hrs · **Money:** ~$6,100–9,200 total, ~$3,300–6,000 remaining

**The rule that governs everything:** the car drives home at the end of every
session. Never start a cutover you can't finish or reverse before dark.

---

## GATE 0 — CLOSED ✅

- [x] **G0.1** [YOU] Buy the bench kit — ~$270. **Done**
- [x] **G0.2** [YOU] Buy 2 spare Sicma housings, each with a full pin set. **Done** — three housings total
- [ ] **G0.3** [YOU] Count all three terminal sets by size *(T-025)* — held deliberately until stock is known
- [ ] **G0.4** [YOU] Check the Ionic's state of charge, keep it above BMS cutoff *(T-022)*
- [ ] **G0.5** [YOU] Compare housing #1 to SPEC §11 — 2 large / 9 small / 2 large per row *(T-020)*

> **Phase 2A and 2B are unblocked.** Nothing is missing for either. G0.3–G0.5 are
> ten-minute jobs that don't gate anything you can start today.

---

## PHASE 0 · DOCUMENTATION & MEASUREMENT
`55–85 hrs · laptop + two half-days with the car`

### 0A — The meter session *(needs the clamp meter)*
- [ ] **0.1** [YOU] **Clamp every load, inrush and steady** — headlights lo/hi, blower each speed, wiper lo/hi, defog, fuel pump, horn, tail, brake, turn, reverse, interior *(T-014)*
- [ ] **0.2** [YOU] Pop-up motor stall current, both sides *(T-015)*
- [ ] **0.4** [YOU] Alternator output rating off the case *(T-004)*
- [ ] **0.5** [YOU] Fuel sender ohm range, empty → full *(T-012)*
- [ ] **0.6** [YOU] Continuity-test pop-up motor internal limit pinout *(T-011)*
- [ ] **0.7** [YOU] Continuity-test which ignition outputs stay live in RUN and START *(T-023)*

> **0.1 is irreversible-window work.** Once the harness is out those numbers are
> gone forever. Do not skip it.

### 0B — The tape measure session
- [ ] **0.8** [YOU] **Dash cavity envelope** — W × H × D, plus 39-pin lever clearance *(T-007, Q-014)*
- [ ] **0.9** [YOU] Cargo bin measurements against the Group 25 case *(T-024)*
- [ ] **0.10** [YOU] Sill space behind the kick panel — 4 relays, 2 fuses, ground stud *(V-055)*
- [ ] **0.11** [YOU] Every harness route with string, +15% *(T-008)*
- [ ] **0.12** [YOU] Photograph the entire harness — every connector, branch, ground *(T-018)*
- [ ] **0.13** [YOU] Find and log the wideband tap and every PO splice *(T-019)*
- [ ] **0.14** [YOU] Battery terminal type — SAE or threaded *(V-053)*

### 0C — Paper work
- [ ] **0.15** [AGENT] Wire cut list — gauge, colour, length, quantity
- [ ] **0.16** [AGENT] Connector BOM — housings, wedges, contacts +20%, seals
- [ ] **0.17** [AGENT] Update LADDERS.md with measured pop-up and ignition values
- [ ] **0.18** [AGENT] Update LOADS.md soft-fuse table from measured current
- [ ] **0.19** [AGENT] Label list for every wire and connector
- [ ] **0.20** [YOU] Panel layout 1:1 on paper, verified against 0.8
- [ ] **0.21** [YOU] Mock the panel in cardboard, check it fits with service access
- [ ] **0.22** [YOU] **Freeze the design.** Print it. Date it.

> **GATE:** every one of the 39 cavities has a destination, every relay has a coil
> source and a load path, and no circuit appears twice. If any fail, Phase 0 is
> not done.

---

## PHASE 1 · ORDER & PRACTICE
`10–16 hrs · apartment`

- [ ] **1.1** [YOU] Consolidated wire and connector order *(hold until 0.11 and 0.16)*
- [ ] **1.2** [YOU] Order Deutsch crimper, hydraulic lug crimper, label printer
- [ ] **1.3** [YOU] Order battery mount, Class-T, disconnect, **2 AWG** cable, lugs
- [ ] **1.4** [YOU] Order the CAN keypad, 8-key
- [ ] **1.5** [YOU] **Source the new mirrors** — larger, heated, digital control *(D-093)*
- [ ] **1.6** [YOU] **Source a fuel-door solenoid** — it never existed, this is new *(D-098)*
- [ ] **1.7** [YOU] **Source a hatch latch switch** — the original is broken *(D-098)*
- [ ] **1.8** [YOU] Inventory everything against the BOM on arrival
- [ ] **1.9** [YOU] Build crimp coupons — three of every terminal and gauge combination
- [ ] **1.10** [YOU] Pull-test every coupon, record the force, adjust until it repeats
- [ ] **1.11** [YOU] Practice Deutsch contact insertion and extraction ×10
- [ ] **1.12** [YOU] Practice adhesive heat shrink until you get weep at both ends
- [ ] **1.13** [YOU] Set up the label printer, lock a format

---

## PHASE 2A · PMU CONFIGURATION
`35–55 hrs · apartment · unblocked today`

- [ ] **2.1** [YOU] Build the plywood bench board, ground bus, fused feed
- [ ] **2.2** [YOU] Mount the PMU using a **spare** housing — never the real one
- [ ] **2.3** [YOU] Terminate a test pigtail: stud, pin 25, pin 7, pin 15, CAN1 pair, six outputs, four inputs
- [ ] **2.4** [YOU] **Fit 120 Ω at both ends of CAN1.** No termination = no connection
- [ ] **2.5** [YOU] Install the PMU client on Windows, connect the USB-to-CAN adapter
- [ ] **2.6** [YOU] Power up, confirm the PMU appears
- [ ] **2.7** [YOU] Create the project file, name every channel to match SPEC exactly
- [ ] **2.8** [YOU] Wire a bulb to one output, verify switching and live current
- [ ] **2.9** [YOU] Short that output deliberately — verify the soft fuse trips, test retry
- [ ] **2.10** [YOU] Configure PWM on an LED strip, tune the theatre fade
- [ ] **2.11** [YOU] Build one ladder on a scrap switch, read ADC at each position
- [ ] **2.12** [YOU] Compare to `LADDERS.md`, adjust resistors, write the decode table
- [ ] **2.13** [YOU] Repeat 2.11–2.12 for all six ladders
- [ ] **2.14** [YOU] Turn signal logic — flash rate, hazard override. **No bulb-out** *(D-047)*
- [ ] **2.15** [YOU] Wiper logic — LOW, HIGH, intermittent timer, park sensing, O8 braking
- [ ] **2.16** [YOU] Headlight logic — PARK feeds O6, HEAD adds O2, **pop-ups raise on HEAD** *(D-038)*
- [ ] **2.17** [YOU] Wink override logic — momentary, returns to ladder state
- [ ] **2.18** [YOU] Keep-alive latch — pin 7 diode-OR sources, O22 self-hold, shutdown delay
- [ ] **2.19** [YOU] Crank logic and interlocks on O21
- [ ] **2.20** [YOU] Fuel pump prime, run-with-RPM, inertia cutoff
- [ ] **2.21** [YOU] CAN keypad — defog, interior override, spare keys
- [ ] **2.22** [YOU] Undervoltage / overvoltage warnings for the lithium's BMS window
- [ ] **2.23** [YOU] Enable data logging
- [ ] **2.24** [YOU] Save, back up, start a version log — RevA-01, -02…
- [ ] **2.25** [YOU] Full dry-run: every configured function, real switches, real loads

---

## PHASE 2B · FIRMWARE
`155–325 hrs · laptop · runs in parallel with everything below`

- [ ] **2.26** [AGENT] Finalise the CAN message map *(Q-041)*
- [ ] **2.27** [YOU] Two Teensys + two SN65HVD230 + 120 Ω each end, CAN talking
- [ ] **2.28** [YOU] Shared CAN library — send, receive, fault handling
- [ ] **2.29** [YOU] ICU: analog acquisition + scaling for six sensor inputs
- [ ] **2.30** [YOU] ICU: tach conditioning circuit, breadboard, verify against a signal generator
- [ ] **2.31** [YOU] ICU: VSS pulse capture on a hardware timer
- [ ] **2.32** [YOU] ICU: display driver, first gauge rendering
- [ ] **2.33** [YOU] ICU: **safe-mode render path** — works with no config file
- [ ] **2.34** [YOU] ICU: config-from-SD — layout, thresholds, colours as data
- [ ] **2.35** [YOU] DCU: climate logic, servo drive, comfort switching
- [ ] **2.36** [YOU] DCU: heat/cool interlock *(D-073)*
- [ ] **2.37** [YOU] **Radar subsystem** — sensor interface, DCU integration, display *(D-096)*
- [ ] **2.38** [YOU] Three-node integration — PMU + DCU + ICU on one bench bus
- [ ] **2.39** [YOU] Design and order the carrier PCBs, socketed Teensy
- [ ] **2.40** [YOU] Power supply boards — reverse protection, **load-dump TVS**, buck *(D-088)*

---

## PHASE 3 · POWER BACKBONE
`18–28 hrs · shop · factory harness untouched`

- [ ] **3.1** [YOU] Disconnect the factory battery
- [ ] **3.2** [YOU] Mock the battery box in cardboard before cutting
- [ ] **3.3** [YOU] Fabricate and mount the tray with a **backing plate** *(D-063)*
- [ ] **3.4** [YOU] Mount the Ionic. Secure against g-loading in **every** axis
- [ ] **3.5** [YOU] Mount the master disconnect within reach
- [ ] **3.6** [YOU] Mount the Class-T **as close to battery positive as physically possible**
- [ ] **3.7** [YOU] Cut and hydraulically crimp cables. Adhesive shrink and a boot on every lug
- [ ] **3.8** [YOU] Rear ground stud — bare metal, star washer, torque, cavity wax
- [ ] **3.9** [YOU] Run **2 AWG** forward through the tunnel *(D-091)*
- [ ] **3.10** [YOU] **Put a pull string in beside it** *(D-064)*
- [ ] **3.11** [YOU] Grommet every pass-through, loom the full length
- [ ] **3.12** [YOU] Terminate forward on a temporary insulated junction post
- [ ] **3.13** [YOU] Install the front star ground node
- [ ] **3.14** [YOU] Reconnect the factory harness to the new feed and ground
- [ ] **3.15** [YOU] Pair the Ionic app, baseline voltage / SoC / temperature
- [ ] **3.16** [YOU] Start it. Verify charging voltage
- [ ] **3.17** [YOU] Voltage-drop test while cranking, post to starter and ground return
- [ ] **3.18** [YOU] **Drive it.** Identical to before, on a new backbone

---

## PHASE 4 · PANEL BUILD
`49–74 hrs · bench`

- [ ] **4.1** [YOU] Cut and fold the backer plate per the 1:1 drawing
- [ ] **4.2** [YOU] Deburr, drill, finish
- [ ] **4.3** [YOU] Mount the PMU, standing it off for airflow
- [ ] **4.4** [YOU] Mount **10 relay sockets, populate 5** — K1–K4 and K11 *(D-067)*
- [ ] **4.5** [YOU] Mount the fuse block, 13 positions
- [ ] **4.6** [YOU] Mount the always-hot busbar and ground bus
- [ ] **4.7** [YOU] Mount bracket positions for all 14 leg receptacles + DP-DIAG, DP-KEY, DP-ICU, DP-DCU
- [ ] **4.8** [YOU] Stud feed from busbar to PMU stud, torque to spec
- [ ] **4.9** [YOU] **Pin 25 ground to the ground bus — shortest, heaviest path on the plate**
- [ ] **4.10** [YOU] Wire the K1–K4 pop-up H-bridges, label every relay position
- [ ] **4.11** [YOU] Build the diode-OR wake network — **six inputs incl. horn** *(D-072)*
- [ ] **4.12** [YOU] Fit the 10 kΩ bleed resistor *(D-056)*
- [ ] **4.13** [YOU] Build the constant bus, F1–F5, each individually fused
- [ ] **4.14** [YOU] **Terminate the real 39-pin. All 39 cavities.** Work in cavity order, tick each on the printed schedule
- [ ] **4.15** [YOU] Insert the wedge lock, verify no contact backs out
- [ ] **4.16** [YOU] Route each wire to its bulkhead receptacle and terminate
- [ ] **4.17** [YOU] Terminate reserved wires to their bulkheads and cap the far ends
- [ ] **4.18** [YOU] Continuity-test every path, 39-pin cavity to bulkhead cavity
- [ ] **4.19** [YOU] High-resistance check between adjacent power cavities
- [ ] **4.20** [YOU] Label every wire at both ends and every receptacle
- [ ] **4.21** [YOU] Bench-power from a current-limited supply
- [ ] **4.22** [YOU] Verify each output at the correct bulkhead pin with a test lamp
- [ ] **4.23** [YOU] Verify each input by shorting its bulkhead pin to ground
- [ ] **4.24** [YOU] Photograph from every angle

> **GATE:** the 39-pin is never opened after 4.15. If 4.18 finds a fault, fix it
> now — this is the last cheap opportunity.

---

## PHASE 5 · HARNESS LEGS
`98–162 hrs · bench · order: L3 → L2 → L4 + sill → L1`

Repeat for each leg:

- [ ] **5.1** [YOU] Lay the route out full-scale using measured lengths
- [ ] **5.2** [YOU] Cut every wire per the cut list, plus service loop
- [ ] **5.3** [YOU] Strip, crimp, seat contacts in the mating housing
- [ ] **5.4** [YOU] Fit the wedge lock, pull-test every contact
- [ ] **5.5** [YOU] Terminate device ends — LED sockets, motors, switches, senders
- [ ] **5.6** [YOU] Continuity-test every wire end to end
- [ ] **5.7** [YOU] Tug-test every crimp
- [ ] **5.8** [YOU] Label both ends of every wire and the segment
- [ ] **5.9** [YOU] Bundle with Tesa or loom. **Do not final-wrap**
- [ ] **5.10** [YOU] Bag and tag

Plus, once:

- [ ] **5.11** [YOU] Fabricate the sill plate — 4 relay sockets, F8/F9, ground stud
- [ ] **5.12** [YOU] Wire the K5–K8 window H-bridges at the sill
- [ ] **5.13** [YOU] Build D1 and D2 door connectors, DT06-08S each
- [ ] **5.14** [YOU] **Fit the 120 Ω CAN terminator at the engine-bay drop**, capped *(D-079)*
- [ ] **5.15** [YOU] Run the capped DCU↔ICU private CAN pair *(D-087)*

---

## PHASE 6 · INSTALL & MIGRATE
`75–125 hrs · shop`

- [ ] **6.1** [YOU] Mount the panel. Verify the 39-pin lever and all receptacles are reachable **in place**
- [ ] **6.2** [YOU] Connect main feed and panel ground. **No bulkhead yet**
- [ ] **6.3** [YOU] Power up with **all outputs disabled**. Confirm CAN from the diag port
- [ ] **6.4** [YOU] Install L3. Flip every switch, verify the whole input layer — still zero outputs
- [ ] **6.5** [YOU] Install remaining legs physically — routed, secured, grommeted — loads still on the factory harness
- [ ] **6.6** [YOU] Install the sill node

**Then migrate, in this order.** Tick each circuit as it completes the full
per-circuit loop below.

- [ ] Interior + hatch lamps
- [ ] USB-C ports *(no lighter — D-095)*
- [ ] Horn
- [ ] Wipers + washer
- [ ] Tail / park / marker / plate
- [ ] Brake
- [ ] Turn L and R
- [ ] Reverse
- [ ] Defog
- [ ] Headlights
- [ ] Pop-ups
- [ ] Windows
- [ ] Mirrors *(new units)*
- [ ] Blower
- [ ] Comfort bus
- [ ] Fuel pump
- [ ] Ignition
- [ ] **Start — last**

**Per-circuit loop:**
1. Unplug the load at the factory connector
2. Tape the factory end back, label `MIGRATED` + date
3. Connect to the new harness
4. Enable that one output, limit set just above the 0.1 measurement
5. Operate it. Read live current. **Set the soft fuse from measured, not estimated**
6. Voltage-drop at the device under load — under 0.5 V
7. Log: migrated / verified / measured A / soft fuse / V-drop

- [ ] **6.7** [YOU] Confirm the car starts and drives **before you stop, every day**
- [ ] **6.8** [YOU] Full function check of every circuit in one pass

> **GATE:** the car must complete every function on dumb switches with no CAN
> module attached except the keypad. If it can't, the DCU has crept onto the
> critical path and D-081 is violated.

---

## PHASE 7 · FACTORY HARNESS OUT
`8–14 hrs · shop`

- [ ] **7.1** [YOU] Confirm every circuit on the migration sheet is ticked
- [ ] **7.2** [YOU] Drive a week with the factory harness disconnected but still fitted
- [ ] **7.3** [YOU] Pull it out **intact**. Do not cut it
- [ ] **7.4** [YOU] Board it as a reference, keep until after shakedown

---

## PHASE 8 · SHAKEDOWN
`35–60 hrs · road`

- [ ] **8.1** [YOU] Cold start. Watch the Ionic heater, log voltage through crank
- [ ] **8.2** [YOU] Night drive — headlights, high beams, pop-ups, wink, all lighting
- [ ] **8.3** [YOU] Wet drive — wipers all modes, washer, defog
- [ ] **8.4** [YOU] Long drive with logging on
- [ ] **8.5** [YOU] Review the log for spikes, sag, any soft fuse near a trip
- [ ] **8.6** [YOU] Adjust soft fuses that sit too close to real draw
- [ ] **8.7** [YOU] Re-torque every stud and lug after heat cycling
- [ ] **8.8** [YOU] Re-check voltage drop on the main feed and ground
- [ ] **8.9** [YOU] **Now** final loom wrap, tie-down, grommet sealing
- [ ] **8.10** [YOU] Back up the final config, print it, file it
- [ ] **8.11** [YOU] Put spare Deutsch contacts, a wedge tool, and a printed pinout in the car

---

## PHASE 9 · MODULES
`after the car is finished · D-081`

- [ ] **9.1** [YOU] Install DP-ICU and DP-DCU harnesses
- [ ] **9.2** [YOU] Fit the ICU, **factory cluster stays** *(D-094)*
- [ ] **9.3** [YOU] Calibrate every sender against known references
- [ ] **9.4** [YOU] Verify the ICU works with CAN2 unplugged — critical gauges must survive
- [ ] **9.5** [YOU] Fit the DCU, migrate climate off the factory switch
- [ ] **9.6** [YOU] Install radar sensors front and rear, integrate with the DCU
- [ ] **9.7** [YOU] Night legibility check, sunlight legibility check
- [ ] **9.8** [YOU] Remove the factory cluster once the ICU is trusted
- [ ] **9.9** [YOU] Final config backup, both modules

---

## Calendar

| When | What |
|---|---|
| Now | Gate 0, ~$270 |
| Fall 2026 | Phase 0 sessions · Phase 2A · Phase 2B starts |
| Winter break 2026 | Phase 3 · Phase 4 |
| Spring 2027 | Phase 5 · Phase 2B continues |
| Summer 2027 | Phase 6 · 7 · 8 — **car finished** |
| Late 2027 – 2028 | Phase 9 |

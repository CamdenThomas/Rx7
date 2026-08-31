# BUILD CHECKLIST

*Rev 2026-08-31 · owns: the build sequence, phase by phase. The migration order inside Phase 6 is [`MIGRATION-LOG.md`](MIGRATION-LOG.md)'s; money is [`../05-PROCESS/BOM.md`](../05-PROCESS/BOM.md)'s.*

Tick as you go. Every step is either **[YOU]** hands-on or **[AGENT]** paperwork
Claude can do on request. Step IDs are permanent — a gap means a step was
dropped and the reason is in [`DECISIONS.md`](../05-PROCESS/DECISIONS.md).

**Scope:** PMU panel · power backbone · four harness legs · sill node · DCU · ICU
**Effort:** 531–932 hrs, ~90–125 done ([`STATUS.md`](../STATUS.md)) · **Money:** [`BOM.md`](../05-PROCESS/BOM.md)

**The rule that governs everything:** the car drives home at the end of every
session. Never start a cutover you can't finish or reverse before dark.

## Contents

Gate 0 · Phase 0 documentation & measurement · 1 order & practice · 2A PMU
configuration · 2B firmware · 3 power backbone · 4 panel build · 5 harness
legs · 6 install & migrate · 7 factory harness out · 8 shakedown · 9 modules
· Calendar

---

## GATE 0 — CLOSED ✅ (D-101, D-102)

- [x] **G0.1** [YOU] Buy the bench kit — meter, 3 × Teensy, transceivers, cable. **Done** (D-140 for what actually arrived; the remainder is [`BENCH-KIT.md`](BENCH-KIT.md))
- [x] **G0.2** [YOU] Buy 2 spare Sicma housings, each with a full pin set. **Ordered** — inbound, verify on arrival (`T-045`)
- [x] **G0.3** [YOU] Count the terminal set by size. **Done** — 16 large, 27 small, zero small spares (D-135). Order spares before Phase 4 (`T-044`)
- [ ] **G0.4** [YOU] Check the Ionic's state of charge, keep it above BMS cutoff (`T-022`)
- [x] **G0.5** [YOU] Compare housing #1 to SPEC §11. **Confirmed** (D-134, D-139) — mark cavity 1 with a paint pen (`T-043`)

> **Phase 2A and 2B are unblocked.** Nothing is missing for either.

---

## PHASE 0 · DOCUMENTATION & MEASUREMENT
`55–85 hrs · laptop + two half-days with the car · started`

### 0A — The meter session *(meter in hand; ~10–12 hrs total)*
- [x] **0.1** [YOU] Clamp session — **CLOSED 2026-08** (`T-014` → D-197): measured where clean, channel caps everywhere else (D-175); telemetry finishes the job after migration (D-174)
- [x] **0.2** [YOU] Pop-up motor stall current — DONE 2026-08: L 12.8 / R 13.1 A (`T-015` → D-177)
- ~~**0.3** Window motor stall~~ — dropped, the windows are manual (D-131)
- [ ] **0.4** [YOU] Alternator: factory-spec exciter wired instead (`V-086` → D-198); rating from the FSM or parts counter (`T-004`, `V-002`)
- [x] **0.5** [YOU] Fuel sender — **DONE 2026-08**: 6 / 31.5 / 80 Ω (`T-012` → D-197); LADDERS §A7
- [x] **0.6** [YOU] Pop-up pinout — closed off FSM sheet E instead (`T-011` → D-177)
- [x] **0.7** [YOU] Ignition closure — closed off FSM sheet F (`T-023` → D-178)

> **0A is complete** (D-197). Every figure lives in
> `../02-HARNESS/data/pmu_pins.csv` → [`CHANNEL-SCHEDULE.md`](../01-DESIGN/CHANNEL-SCHEDULE.md) and [`../01-DESIGN/LADDERS.md`](../01-DESIGN/LADDERS.md).

### 0B — The tape measure session
- [ ] **0.8** [YOU] **Dash cavity envelope** — W × H × D, plus 39-pin lever clearance (`T-007`, `Q-014`)
- [ ] **0.9** [YOU] Cargo bin measurements against the Group 25 case (`T-024`)
- [ ] **0.10** [YOU] Sill space behind the kick panel — 4 relays, 3 fuses, ground stud (`T-028`, `V-055`)
- [ ] **0.11** [YOU] Every harness route with string, +15 % (`T-008`)
- [ ] **0.12** [YOU] Photograph the entire harness — every connector, branch, ground (`T-018`) → `01-REFERENCE/photos/`
- [ ] **0.13** [YOU] Find and log the wideband tap and every PO splice (`T-019`)
- [ ] **0.14** [YOU] Battery terminal type — SAE or threaded (`T-029`, `V-053`)

### 0C — Paper work
- [x] **0.15** [AGENT] Wire cut list — structure generated from the cavity table; lengths wait on 0.11
- [x] **0.16** [AGENT] Connector BOM — housings, wedgelocks, clips, contacts +20 %, seals ([`CONNECTORS.md`](../02-HARNESS/CONNECTORS.md), [`BOM.md`](../05-PROCESS/BOM.md))
- [x] **0.17** [AGENT] LADDERS final — pop-up transit (D-187), ignition (D-178), A15 five-state (D-184), A8 horn (D-190), A7 sender (D-197)
- [x] **0.18** [AGENT] Measured figures in `pmu_pins.csv`, regenerated — campaign closed (D-197); telemetry continues at 6.x
- [x] **0.19** [AGENT] Label list for every wire and connector ([`CUT-LIST.md`](CUT-LIST.md))
- [ ] **0.20** [YOU] Panel layout 1:1 on paper, verified against 0.8
- [ ] **0.21** [YOU] Mock the panel in cardboard, check it fits with service access
- [ ] **0.22** [YOU] **Freeze the design.** Print it. Date it
- [x] **0.23** [YOU] Ruled 2026-08, all five per recommendation: Q-061 → D-180 · Q-062 → D-181 · Q-063 → D-182 · Q-064 → D-183 · Q-065 → D-184

> **GATE:** every one of the 39 cavities has a destination, every relay has a
> coil source and a load path, no circuit appears twice, and
> `05-PROCESS/tools/check.py` is clean. If any fail, Phase 0 is not done.

---

## PHASE 1 · ORDER & PRACTICE
`10–16 hrs · apartment`

- [ ] **1.1** [YOU] Consolidated wire and connector order *(hold until 0.11 — 0.23 is ruled (D-180–D-184))*
- [ ] **1.2** [YOU] Order Deutsch crimper, hydraulic lug crimper, label printer, open-barrel FCI crimper (`V-069`)
- [ ] **1.3** [YOU] Order battery mount, Class-T, disconnect, **2 AWG** cable, lugs (D-091)
- [ ] **1.4** [YOU] Order the CAN keypad, 8-key
- [ ] **1.5** [YOU] **Source the new mirrors** — larger, heated, digital control (D-093, `T-031`)
- [ ] **1.6** [YOU] **Source a fuel-door solenoid** — it never existed, this is new (D-098, `T-032`)
- [ ] **1.7** [YOU] **Source a hatch latch switch** — the original is broken (D-098, `T-033`)
- [ ] **1.8** [YOU] Order spare 1.5 mm terminals, ~15 minimum (`T-044`)
- [ ] **1.9** [YOU] Inventory everything against the BOM on arrival
- [ ] **1.10** [YOU] Build crimp coupons — three of every terminal and gauge combination
- [ ] **1.11** [YOU] Pull-test every coupon, record the force, adjust until it repeats
- [ ] **1.12** [YOU] Practice Deutsch contact insertion and extraction ×10
- [ ] **1.13** [YOU] Practice adhesive heat shrink until you get weep at both ends
- [ ] **1.14** [YOU] Set up the label printer, lock a format
- [ ] **1.15** [YOU] Source a replacement blower motor (K-023, `T-038`); the washer diagnosis is post-PMU (D-176)

---

## PHASE 2A · PMU CONFIGURATION — IN THE CAR (D-194)
`12–20 hrs · laptop in the car, after 6.2 powers the panel · fully specified in PMU-CONFIG.md (D-166)`

**The car is the bench (D-194).** The whole vehicle logic is entered with the
PMU mounted and powered from the new backbone, every output disabled, before
any circuit migrates. Each Phase 6 cutover then just enables one configured
output and verifies it against telemetry.

- [ ] **2.1** [YOU] PMU powered in the panel (after 6.2), **all outputs disabled**; laptop on DP-DIAG — wired early for exactly this
- [ ] **2.2** [YOU] **120 Ω at both ends of CAN1.** No termination = no connection
- [ ] **2.3** [YOU] Install the PMU client on Windows, connect the USB-to-CAN adapter
- [ ] **2.4** [YOU] **5 A fuse in the feed for first power-up** (D-145); step up only after CAN is clean
- [ ] **2.5** [YOU] **`V-065`** — export the PMU's CAN message structure from the client. Reconcile against `can_map.h` 0x100–0x130
- [ ] **2.6** [YOU] Create the project file. Name every channel to match [`SPEC.md`](../01-DESIGN/SPEC.md) exactly
- [ ] **2.7** [YOU] First migrated circuit (interior lamps — lowest stakes) doubles as the output test: switching + live current on telemetry
- [ ] **2.8** [YOU] On that same circuit: **limit 2 A, short it deliberately.** Watch the trip, retry count, reset (D-143)
- [ ] **2.9** [YOU] Configure PWM, tune the theatre fade
- [ ] **2.10** [YOU] Turn signal logic — flash rate, hazard override. **No bulb-out** (D-047)
- [ ] **2.11** [YOU] **Inrush windows on every lamp channel** (D-120) — filament pulls 8–12× for a few ms
- [ ] **2.12** [YOU] Wiper logic — LOW, HIGH, intermittent timer, mechanical park (`Q-063` → D-182; `V-074` may reopen), O8 braking
- [ ] **2.13** [YOU] Headlight logic — PARK feeds O6, HEAD adds O2, **pop-ups raise on HEAD** (D-038)
- [ ] **2.14** [YOU] Wink — NC-cross side selection off O1 (D-189); request is pin-7, key-out/ACC only (D-190)
- [ ] **2.15** [YOU] Keep-alive latch — diode-OR sources, O22 self-hold, shutdown delay (`V-075`)
- [ ] **2.16** [YOU] Crank logic and interlocks on O21 — interim rule per `Q-064` → D-183
- [ ] **2.17** [YOU] Fuel pump prime, run-with-RPM (`Q-064` → D-183), inertia cutoff
- [ ] **2.18** [YOU] CAN keypad — defog, interior override, spare keys
- [ ] **2.19** [YOU] Undervoltage / overvoltage for the lithium's BMS window
- [ ] **2.20** [YOU] Enable data logging
- [ ] **2.21** [YOU] Save, back up, start the version log in [`LOGS.md`](LOGS.md)
- [ ] **2.22** [YOU] Enter every soft-fuse value from [`CHANNEL-SCHEDULE.md`](../01-DESIGN/CHANNEL-SCHEDULE.md) — all present (D-175); telemetry tightens each channel per D-164 after its cutover

> **Ladder ADC verification happens in the car** during Phase 6, when the
> switches are wired and real resistances exist (D-142). Firmware Stage 4
> proved the *decode logic*; the car proves the *values*.

---

## PHASE 2B · FIRMWARE
`155–325 hrs · laptop · ~90–125 done · runs in parallel with everything below`

- [x] **2.26** [AGENT] Finalise the CAN message map — **done**, byte layouts in [`CAN-MESSAGES.md`](../03-MODULES/CAN-MESSAGES.md) (D-106)
- [x] **2.27a** [YOU] Toolchain, blink, board 1 — **Stage 1**. Boards 2 and 3: `T-048`
- [x] **2.27b** [YOU] `can_map.h` validation — **Stage 2, all passed**
- [x] **2.27c** [YOU] CAN loopback, no transceiver — **Stage 3, all passed**
- [x] **2.27d** [YOU] Ladder decode — **Stage 4, done, absorbed into the ICU firmware**
- [x] **2.27e** [YOU] Tach measurement, one jumper — **Stage 5, done, absorbed**
- [ ] **2.27f** [YOU] Two Teensys on real CAN — module era (headers, cable; deferred with T-048 per D-194)
- [x] **2.28** [AGENT] Shared CAN structs, dispatch, timeout handling — `can_map.h`, proven Stages 2–3
- [ ] **2.29** [YOU] ICU: analog acquisition + scaling for the six sensor inputs (conditioning schematic F-003)
- [ ] **2.30** [YOU] ICU: tach conditioning circuit, breadboard, verify against the tach simulator (F-004)
- [ ] **2.31** [YOU] ICU: VSS pulse capture on a hardware timer — same code as the tach path
- [x] **2.32** [AGENT] ICU: renderer, drive / diagnostics / trip pages, desktop simulator, 415-assertion regression suite — **built** (`cluster_core.h`, D-151…D-158)
- [ ] **2.32a** [YOU] ICU: display driver — the three `pushDirtyTiles()` calls, after `Q-060` → D-193
- [ ] **2.33** [YOU] ICU: **safe-mode render path** — works with no config file
- [ ] **2.34** [YOU] ICU: config-from-SD — layout, thresholds, colours as data; `stats.h` persistence (Stage 6, D-162)
- [ ] **2.35** [YOU] DCU: climate logic, servo drive, comfort switching (skeleton F-001)
- [ ] **2.36** [YOU] DCU: heat/cool interlock (D-073)
- [ ] **2.37** [YOU] **Radar subsystem** — sensor interface, DCU integration, display (D-096, `V-061`)
- [ ] **2.38** [YOU] Three-node integration — PMU + DCU + ICU on one bench bus
- [ ] **2.39** [YOU] Design and order the carrier PCBs, socketed Teensy, IMU orientation fixed (`V-073`) (H-001, H-002)
- [ ] **2.40** [YOU] Power supply boards — reverse protection, **load-dump TVS**, buck (D-088)

---

## PHASE 3 · POWER BACKBONE
`18–28 hrs · shop · factory harness untouched · procedure in BATTERY-INSTALL.md §5`

- [ ] **3.1** [YOU] Disconnect the factory battery
- [ ] **3.2** [YOU] Mock the battery box in cardboard before cutting (`T-024`)
- [ ] **3.3** [YOU] Fabricate and mount the tray with a **backing plate** (D-063)
- [ ] **3.4** [YOU] Mount the Ionic. Secure against g-loading in **every** axis
- [ ] **3.5** [YOU] Mount the master disconnect within reach
- [ ] **3.6** [YOU] Mount the Class-T **as close to battery positive as physically possible**
- [ ] **3.7** [YOU] Cut and hydraulically crimp cables. Adhesive shrink and a boot on every lug
- [ ] **3.8** [YOU] Rear ground stud — bare metal, star washer, torque, cavity wax
- [ ] **3.9** [YOU] Run **2 AWG** forward through the tunnel (D-091)
- [ ] **3.10** [YOU] **Put a pull string in beside it** (D-064)
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
`49–74 hrs · bench · blocked on T-007`

- [ ] **4.1** [YOU] Cut and fold the backer plate per the 1:1 drawing
- [ ] **4.2** [YOU] Deburr, drill, finish
- [ ] **4.3** [YOU] Mount the PMU, standing it off for airflow
- [ ] **4.4** [YOU] Mount **10 relay sockets, populate 4** — K1, K2, K11, K12 (D-182, D-186). Sockets for K5–K8 are on the sill plate (5.11)
- [ ] **4.5** [YOU] Mount the fuse block — 12 positions on the plate (F1–F7, F10–F13, F15 exciter D-198); F13 labelled radar, deferred (D-191)
- [ ] **4.6** [YOU] Mount the always-hot busbar and ground bus
- [ ] **4.7** [YOU] Mount bracket positions for all 15 leg receptacles + DP-DIAG, DP-KEY, DP-ICU, DP-DCU (`1027-003-1200` clips)
- [ ] **4.8** [YOU] Stud feed from busbar to PMU stud, torque to spec
- [ ] **4.9** [YOU] **Pin 25 ground to the ground bus — shortest, heaviest path on the plate**
- [ ] **4.10** [YOU] Wire K1/K2 pop-up run relays with the wink NC-cross + steering diodes (D-186, D-189) and K12 washer relay (D-182); label every position
- [ ] **4.11** [YOU] Build the diode-OR wake network — **eight inputs, strip full** (D-189): ACC, RUN, hazard, door (sill PNP, D-188), horn (plate PNP on A8, D-190), wink L/R, O22; fit both PNPs
- [ ] **4.12** [YOU] Fit the 10 kΩ bleed resistor (D-056) and the two 100 kΩ A15/A16 bias resistors (D-167)
- [ ] **4.13** [YOU] Build the constant bus, F1–F5, each individually fused, K11 ahead of F1/F5
- [ ] **4.14** [YOU] **Terminate the real 39-pin. All 39 cavities.** Work in cavity order, tick each on the printed [`PIN-MAP.md`](../02-HARNESS/PIN-MAP.md)
- [ ] **4.15** [YOU] Insert the wedge lock, verify no contact backs out
- [ ] **4.16** [YOU] Route each wire to its receptacle and terminate
- [ ] **4.17** [YOU] Terminate reserved and provisioned wires to their receptacles and cap the far ends
- [ ] **4.18** [YOU] Continuity-test every path, 39-pin cavity to receptacle cavity, and every relay leg (D-146 — this replaces powered bench verification)
- [ ] **4.19** [YOU] High-resistance check between adjacent power cavities
- [ ] **4.20** [YOU] Label every wire at both ends and every receptacle ([`CUT-LIST.md`](CUT-LIST.md) format)
- [ ] **4.24** [YOU] Photograph from every angle → `01-REFERENCE/photos/dash/`

> **GATE:** the 39-pin is never opened after 4.15. If 4.18 finds a fault, fix it
> now — this is the last cheap opportunity. Steps 4.21–4.23 (powered bench
> verification) were dropped by D-146; powered verification happens in the car
> at 6.3.

---

## PHASE 5 · HARNESS LEGS
`98–162 hrs · bench · blocked on T-008 · order: L3 → L2 → L4 + sill → L1`

Repeat for each leg:

- [ ] **5.1** [YOU] Lay the route out full-scale using measured lengths
- [ ] **5.2** [YOU] Cut every wire per the cut list, plus service loop
- [ ] **5.3** [YOU] Strip, crimp, seat contacts in the mating housing
- [ ] **5.4** [YOU] Fit the wedge lock, pull-test every contact
- [ ] **5.5** [YOU] Terminate device ends — bulb sockets, motors, switches, senders
- [ ] **5.6** [YOU] Continuity-test every wire end to end
- [ ] **5.7** [YOU] Tug-test every crimp
- [ ] **5.8** [YOU] Label both ends of every wire and the segment; `CAPPED` on every provisioned end
- [ ] **5.9** [YOU] Bundle with Tesa or loom. **Do not final-wrap**
- [ ] **5.10** [YOU] Bag and tag

Plus, once:

- [ ] **5.11** [YOU] Fabricate the sill plate — 4 relay sockets (empty), F8/F9 positions (empty), F14, ground stud (D-131, D-132)
- [ ] **5.13** [YOU] Build D1 and D2 door connectors, DT06-08S each, window legs capped in the door
- [ ] **5.14** [YOU] **Fit the 120 Ω CAN terminator at the engine-bay drop**, capped (D-079)
- [ ] **5.15** [YOU] Run the capped DCU↔ICU private CAN pair (D-087)

> 5.12 (wire the window H-bridges) was dropped — the windows are manual (D-131).
> Sockets are fitted empty; wiring them is part of fitting windows later.

---

## PHASE 6 · INSTALL & MIGRATE
`75–125 hrs · shop`

- [ ] **6.1** [YOU] Mount the panel. Verify the 39-pin lever and all receptacles are reachable **in place**
- [ ] **6.2** [YOU] Connect main feed and panel ground. **No receptacle yet**
- [ ] **6.3** [YOU] Power up with **all outputs disabled**. Confirm CAN from the diag port. This is the powered verification (D-146)
- [ ] **6.4** [YOU] Install L3. Flip every switch, verify the whole input layer, **write the measured ladder values into the config** (D-142) — still zero outputs
- [ ] **6.5** [YOU] Install remaining legs physically — routed, secured, grommeted — loads still on the factory harness
- [ ] **6.6** [YOU] Install the sill node

**Then migrate, in the order in [`MIGRATION-LOG.md`](MIGRATION-LOG.md)** — it owns the order and
the per-circuit loop; tick each circuit there as it completes.

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
- [ ] **8.11** [YOU] Put spare Deutsch contacts, a wedge tool, and a printed [`PIN-MAP.md`](../02-HARNESS/PIN-MAP.md) in the car

---

## PHASE 9 · MODULES
`after the car is finished · D-081`

- [ ] **9.1** [YOU] Install DP-ICU and DP-DCU harnesses
- [ ] **9.2** [YOU] Fit the ICU, **factory cluster stays** (D-094)
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
| Now | Phase 0 sessions · Phase 2A · Phase 2B continues (well ahead) |
| Winter break 2026 | Phase 3 · Phase 4 |
| Spring 2027 | Phase 5 · Phase 2B continues |
| Summer 2027 | Phase 6 · 7 · 8 — **car finished** |
| Late 2027 – 2028 | Phase 9 |

The schedule is limited by weekends with the car, not by firmware. Two
tape-measure tasks (`T-007`, `T-008`) gate 147–236 hours of downstream work
and take perhaps two hours in daylight ([`STATUS.md`](../STATUS.md)).

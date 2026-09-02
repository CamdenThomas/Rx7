# DECISIONS — luxury package

Decisions that govern this project. The ones below were made inside the electrical project before the split (D-213, 2026-09-02) and moved here because they concern features the wiring build only *provisions for*. Full text with reasoning: `../../99-ARCHIVE/Electrical/2026-09-02_electrical-pmu/05-PROCESS/DECISIONS-chronological.md`. New decisions for this project continue from D-300.

## The boundary — what the electrical build hands over

**D-208(f) / D-215 — This project is fabrication, modules and software; it does no harness work.** Every conductor a luxury feature needs is already run and capped in the electrical build, and its relay sockets and fuse positions are fitted empty. What is waiting (all detail in `../electrical-build/01-DESIGN/DESIGN.md`):

| Provision | Where | For |
|---|---|---|
| O15 comfort bus, 25 A, capped | L3-P 2 | Seats, mirror heat, whatever the DCU switches — this project adds its own fuse block on O15 |
| O4 defog output, wired to the grid, configured, disabled | L4-P 1 | The defogger — needs only a trigger (a panel key or a hardwired switch on a spare L3-S2 cavity) |
| Window commands ×4, capped both ends | L3-S2 3–6 → L4-M 9–12 | Power windows: switches at the console, K5–K8 sockets and F8/F9 positions at the sill, motor legs in D1/D2 1–2 |
| O1 window motor bus feed, capped | L4-P 3 | The K5–K8 contact feed |
| Mirror motor ×3 + mirror heat, capped in each door | D1/D2 4–7, F14 position at the sill | Heated, powered mirrors |
| Future module +12 V switched and ground, capped | L3-S2 7, L3-S2 8 | Any dash module |
| Pass-through ×3 dash ↔ rear, capped | L3-S3 1–3 ↔ L4-S 5–7 | Radar rear sensor, or anything else needing a dash-to-hatch link |
| Hatch and fuel-door solenoid outputs, capped | L4-M 3, L4-M 4 | Solenoids on an O10 branch with their own fuses (D-180) |
| DP-ICU — 12-way: switched 12 V, ground, CAN2, illumination reference, taps on water temp, oil pressure, tach, charge sense, brake warning | dash post | The digital cluster module |
| DP-DCU — 6-way: switched 12 V, ground, CAN2 | dash post | The climate / comfort module |
| DP-KEY — 4-way: CAN2, switched 12 V off O10, ground | dash | The custom control panel (D-210) |
| K3 / K4 empty sockets, F13 position, two spare block-B fuse positions | dash node | Anything else |
| CAN2 at 500 kbps, far-end 120 Ω already fitted in the engine bay | — | New nodes plug into the drops; termination never changes |

**D-081 — Modules join a finished car.** The PMU harness drives, shakes down and has its factory harness removed first; nothing here is a dependency for the car starting, running or being legal.

**D-210 — No ECUMaster keypad; the control panel is a custom design that lands on DP-KEY.** Its keys: defog, hatch release, fuel-door release, then the climate and comfort controls (A/C mode, fan, temperature, seat heat). Frame `0x400` is reserved for its buttons. The wink switches are hardwired in the electrical build and can never be panel keys (they must work with the panel asleep and their NC poles interrupt the pop-up relay coils).

**D-209(b)(e) — Still to design here:** the parking-brake sense (no input in the PMU build — a switch into a spare ladder state, or a CAN node), and the hatch latch switch (K-016, broken, unsourced).

## Modules — DCU and ICU

**D-075 / D-077 / D-083 — Two nodes: the DCU (climate, HVAC servos, comfort switching) and the ICU (instrument display *and* engine-sensor acquisition).** A gauge's sender wires into the box that draws the gauge — sender → ADC → pixel, no bus hop — so if CAN2 fails the ICU still shows tach, water temp, oil pressure and speed from its own inputs. The DP-ICU taps exist for this.

**D-078 — Single source of truth per signal.** If the PMU measures it (fuel level, battery voltage, key state, output currents) the ICU reads it from CAN; only signals the PMU cannot see get an ICU input.

**D-084 / D-085 / D-086 / D-088 / D-089 — Teensy 4.1 in both boxes (three bought — one spare), TI TCAN1042/1051 transceivers, CAN 2.0B at 500 kbps with 11-bit IDs (the PMU is not CAN-FD), load-dump TVS on both module supplies (reverse polarity → TVS → filter → automotive buck → the Teensy's 3.3 V), Teensy socketed on its carrier so a heat casualty is a $32 swap.**

**D-087 — A private DCU ↔ ICU CAN-FD pair was planned; the electrical build did not run it (D-215).** Both modules sit behind the same bezel — run it there if it is ever wanted.

**D-106 — CAN byte layouts: 8-byte messages, little-endian, byte 7 a rolling counter, explicit timeout per message, a receiver blanks a field rather than holding the last value.** Bus load ~1.5 %. The PMU's own export format (`V-065`) still has to be reconciled.

**D-082 — The tach input gets opto-isolation or a comparator at the ICU.** Coil-primary spikes run well above 12 V.

**D-090 — No hardwired oil-pressure lamp; oil pressure is shown by the ICU only.** The factory cluster stays live through ICU development (D-094), which covers the window when the ICU is least trustworthy. Reopen if the car's use changes.

**D-191 — The DCU restores climate memory from SD on wake — no constant keep-alive.** F13 at the dash node therefore goes to the radar feed when that subsystem exists.

**D-183 — Once the ICU (or an engine ECU) puts rpm on CAN, the fuel-pump and start-relay rules gain their rpm terms.** Until then the PMU runs the interim rules.

## The cluster

**D-150 / D-192 / D-193 — One wide display, instant-on (no OS, no boot sequence — key on, display on): a 12.3″ bar panel on a 1280 × 480 canvas driven by a BT817 EVE over QSPI from the Teensy.** Two bridge chains, decided by `V-085`: RGB → LVDS into 1280 × 480 cluster glass (only if the binnacle brow shades a 330-nit panel), or RGB → HDMI into a 900–1000-nit 1920 × 720 bar panel's scaler board (the default if the brow does not convince).

**D-168 / D-170 — Dirty-rectangle rendering from a RAM framebuffer (built and proven, 415-assertion suite); 8 MB PSRAM fitted to the Teensy pads before the board is installed.**

**D-151 – D-158 — Rendering rules:** emerald `#009155` is the single lit colour, unlit is a 4:1 dimmer green · imperial at the display layer only, everything stored metric · a missing sensor never renders as a real zero (open = amber dashes, short = red dashes, stale = dim dashes, out of range = red) · contiguous bar segments · symbols not words in the gauge column · four named axes · three items in the left column · digit fields re-centre.

**D-159 / D-169 — The display does not cross the harness; the page-cycle button is a small momentary wired directly to the Teensy.**

**D-109 / D-161 — An IMU on the ICU carrier (MPU-6050 / ICM-20948 class, I²C); axis convention: lateral positive right, longitudinal positive under acceleration, pitch positive nose-up.** Mounting orientation must match (`V-073`).

**D-160 / D-162 / D-163 — `stats.h` thresholds (redline 7000 rpm, hot water 105 °C, low oil 1.0 bar, tank 15.9 gal — all to confirm, `V-070`–`V-072`) · volatile-only until SD persistence exists (probably write on key-off) · the firmware owns automated figures, hand logs own config and firmware versions.**

## Comfort, mirrors, windows, seats

**D-048 / D-074 / D-058 / D-073 — Cooled seats are in scope (fans and ducting on the comfort bus); seat products stay estimates (2 × 4 A heat, 2 × 1.5–2.5 A fans); the heat/cool interlock and comfort-bus switching are the DCU's job, downstream of the dumb O15 feed.**

**D-049 / D-093 — Remote mirror motors kept, plus heated mirrors, with independent wiring per side — slightly larger mirrors with integrated heat and digital controls, new switch.** The door connector budget is exactly 8 conductors per door.

**D-131 — Power windows are a luxury item; the electrical build provisioned everything (see the table above).** Adding them: fit the regulators and motors, plug in D1/D2, populate K5–K8, fit F8/F9, uncap the commands, enable the logic.

**D-180 / D-181 — Hatch and fuel-door solenoids on O10 branches with their own fuses, pulsed by the panel → PMU; mirror heat through F14 at the sill.** Part choice is `T-032` / `T-033`.

**D-096 — Radar is a custom subsystem, not a commercial unit:** DCU-managed, displayed on the cluster, concealed sensors front and rear. The rear link is the L3-S3 ↔ L4-S pass-through; the front sensor is wired locally to the module (`V-061` designs it).

## Head unit and audio

**D-128 / D-129 / D-130 / D-149 — A CarPlay head unit does maps and audio; the ICU keeps gauges only.** Head-unit criteria: double-DIN, physical buttons, button colour set to green, wireless CarPlay, and **full-range unprocessed pre-outs** feeding the external amp (the hard requirement — many units band-limit or EQ their pre-outs). The harness side (L3-M 1/2, illumination, ground, amplifier feed) is already in the electrical build.

## Lighting — the second pass

**D-201 / L-004 — Lighting starts only after the electrical rebuild is shaken down: factory harness out, car driving on the PMU with stock bulbs and soft fuses set from measurement.**

**D-107 / L-001 / D-111 — Custom tail lights: a thin LED strip per side in the stock aperture, red for tail/brake/turn with a 5 cm white reverse section inboard; 2.2 cm strip height gives 55 cm² of red (FMVSS 108 wants 50 cm² for stop and rear turn); a driver PCB per housing takes tail, brake, turn and reverse as logic inputs and handles intensity, constant-current drive and turn override locally.** Design notes: `../../99-ARCHIVE/Electrical/2026-08-31_lighting-body/TAIL-LIGHTS.md`.

**D-110 / L-002 — The pop-ups stay; the headlamp becomes a DOT-compliant sealed unit inside the existing bucket (a strip of LEDs cannot make a beam cutoff).** Which unit is `Q-048`.

**D-122 / L-003 — Every soft fuse is re-set after any bulb change.** A limit set for a filament does not protect an LED.

## Money — from the archived BOM

The archived `BOM.md` (`../../99-ARCHIVE/Electrical/2026-09-02_electrical-pmu/05-PROCESS/BOM.md`) holds the module-era and lighting purchase waves (Waves 3–5: carrier boards, BT817 eval board, display glass, LED modules, the custom panel) and the parts already in hand for this project: three Teensy 4.1, five SN65HVD230 transceivers (superseded by TCAN — D-085), one micro-USB cable.

<!-- out: 01-DESIGN/DESIGN.md -->
# DESIGN — the luxury package

*Rev 2026-09-07 · owns: the design of everything the car gets after it drives on the new harness — the modules, what the electrical build hands over (read live from its data), every sensor front end, the cluster, climate, comfort, body, lighting and the failure modes. Rendered from `data/` + `templates/` (D-309). The CAN map is [`CAN-MESSAGES.md`](CAN-MESSAGES.md)'s; the DCU carrier is [`DCU-CARRIER.md`](DCU-CARRIER.md)'s; the ICU carrier is the electrical build's ([`ICU-CARRIER.md`](../../electrical-build/01-DESIGN/ICU-CARRIER.md), D-259 / D-313); the cluster's layout, palette and rendering are `firmware/icu/cluster_core.h`'s (R6).*

## Contents

1. Two modules and a panel · 2. What the electrical build hands over · 3. Power · 4. Sensors and front ends · 5. The cluster · 6. Climate · 7. Comfort · 8. Body — mirrors and windows · 9. What fails how · 10. Lighting, audio, radar · 11. The feature list · 12. Numbers

---

## 1 · Two modules and a panel

{{modules}}

**Why two boards (D-094):** a blend-door firmware bug must never blank the tachometer. The split is *engine instrumentation from the comfort system* (D-083), not display from climate. **Why the ICU exists at all (D-076):** the PMU has no spare analog input — every one of its sixteen is allocated — so water temp, oil pressure, oil temperature, road speed and the tach were always going to need a reader. **Why the ICU is not this project's to build (electrical D-259, superseding D-306's timing):** it is the car's instrument from the first drive — it excites and reads the senders and draws them on its own display (electrical D-258, D-268) — so the electrical build designs, builds, bench-commissions and installs both with the harness; this project meets a running instrument and moulds the bezel around it (D-313, D-314). **Why the DCU does not (D-307):** it is an output module; its inputs are the panel knobs and its actuators displace the manual levers — both are dash plastics. A headless DCU would sit on the bus with nothing to say.

**Where they live.** Both behind the dash face, never against the windscreen (D-084): the ICU behind the cluster bezel with the display ribboned straight to it (D-159), the DCU behind the centre stack within reach of the HVAC case, the panel on the centre stack. The wideband gauge is already there (electrical D-244) — this project only *displays* it.

## 2 · What the electrical build hands over

Read from `../electrical-build/data/` at every build. A cavity that changes state there fails this project's check the same day.

{{provision_counts}}

{{provisions}}

Three things are **not** provisions: the display (it went in with the ICU — electrical D-268; this project makes the bezel around it), the HVAC servos (local to the case) and the seats' runs to the O15 block under the console. Nothing of the ICU or the display is this project's wiring any more.

## 3 · Power

The DCU's and the panel's **logic** is on the accessory bus through their drops — `DP-DCU 1`, `DP-KEY 3` — 16 AWG taps off O10, beside the ICU's (`DP-ICU-A 1`, the electrical build's), the head unit and the USB-C ports. **The display and its backlight** are the electrical build's (F16 through the ICU board — electrical D-268); O10's headroom is never asked to carry them (D-313 closed `Q-302`). The DCU's **heavy loads** come from **O15, the comfort bus**: 25 A, ON in RUN, delivered to `L3-P 2` behind the centre stack and capped there; **this project builds the fuse block on it** (FT31) — servo rail, seats, nozzles, mirror heat (through `L4-P 4` to F14 at the sill). Neither Teensy goes near raw 12 V (D-088): reverse diode → SMBJ33A load-dump TVS → filter → automotive buck → the Teensy's 3.3 V. The DCU's servo rail is its own buck so a stalled door cable never browns out the MCU.

## 4 · Sensors and front ends

**The engine senders are the ICU's, and the ICU is the electrical build's** (D-259): it excites the fuel and water-temp senders, reads the PMU-excited oil node, the tach, the charge and brake lines and the three tell-tale senses, and drives the old cluster's gauges from what it reads — every channel is a row in that project's `data/icu_channels.csv`, rendered as its `ICU-CARRIER.md`. The observer front end this project drew (D-310) went with the cluster drop it observed (electrical D-258): nothing here shares a node with a factory gauge any more, and there is no excitation hand-over at S3. What this project reads itself is the DCU's — cabin and outside-air temperature, the comfort-bus current — and what it drives: the blower's final stage, the servos, the comfort FETs. **The Teensy 4.1 is 3.3 V only and not 5 V tolerant** — every input below is clamped.

{{sensors}}

## 5 · The cluster

**One wide display, instant-on** — key on, display on, no OS, no boot sequence (D-192): a 12.3-inch bar panel on a **1280 × 480 canvas** driven by a **BT817 EVE over QSPI** from the Teensy, dirty-rectangle tiles out of a 614 KB framebuffer in the 8 MB PSRAM (D-150 / D-168 / D-170 / D-193). The chain is decided — electrical D-269, chain (ii): RGB → a TFP410-class HDMI encoder → the scaler board of a 900–1000-nit 1920 × 720 bar panel, the canvas scaled 1.5×; Camden would not depend on the brow's shade when the sun glints at a funny angle. The display went in with the ICU (electrical D-268); this project's part of the cluster is the pages and the bezel (FT34). Sunlight is the real-world killer: 800–1000 nits, bonded or AR glass, and the hood. The eval board (`T-051`), the glass and the timings are the electrical build's bench items now.

**Rendering rules (D-151 – D-158, owned by `cluster_core.h`):** emerald `#009155` is the single lit colour and unlit is a 4:1 dimmer green · imperial at the display layer only, everything stored metric · **a missing sensor never renders as a real zero** — open = amber dashes, short = red dashes, stale = dim dashes, out of range = red · contiguous bar segments · symbols not words in the gauge column · four named axes · three items in the left column · digit fields re-centre. **The one discipline:** never clear the whole screen in a redraw path — compose freely, transmit only the tiles that changed; a full push is ~100 ms, invisible as a page transition and fatal inside the 30 fps loop.

**Pages.** DRIVE (30 fps, built) · PERFORMANCE (G-meter dot inside a static ring with peak-hold ghosts, pitch as a numeric readout under the compass — D-157 / D-161; IMU on the ICU carrier — electrical `V-073`) · DIAGNOSTICS (built — the 24 channels of `0x130` with live current, soft-fuse setpoint and state: a tripped channel names itself, a motor's rising draw is bearings, a migration verifies on the spot) · TRIP / LOG (built, volatile until SD persistence F-007; min oil pressure and max water temp record the worst moment of a drive). A small momentary button by the display cycles them (D-169). Config-as-data on SD with a safe-mode path — a cluster that fails to boot because of a typo is worse than no cluster (F-010).

**What it shows that the factory cluster could not:** AFR from the wideband (electrical `Q-304`), oil temperature, outside and cabin temperature from the DCU, the charge tell-tale from the alternator's L line, one **BRAKE** tell-tale for fluid level and parking brake together — the two switches share one node, exactly as the factory lamp had it (D-310) — and there is deliberately **no hardwired oil-pressure lamp** (D-090): the ICU shows oil pressure, and the PMU gates the pump on its own A7, on a node the PMU itself excites (electrical D-249 / D-260) — the old cluster is downstream of the ICU now (electrical D-258), so it no longer covers a dead ICU; the pump gate does. Thresholds — redline 7000 rpm, hot water 105 °C, low oil 1.0 bar, tank 15.9 gal — are `stats.h`'s (D-300; the tank figure is `Q-307`).

## 6 · Climate

There is **no automatic climate control** and none is planned. The panel has a temperature knob and a fan knob with green pointers against a red-to-blue arc, a detented mode switch, and two small green-LED toggles for recirculate and (one day) A/C; the DCU turns knob positions into servo angles and a blower duty.

**Blower (D-307 / D-308).** The original motor is dead (K-023) and comes back here: a 2-wire brushed replacement (Four Seasons 35483 class, the squirrel cage transferred) plugging into `L3-BLW`, the DTP-2 the electrical build left dust-capped at the HVAC case — cavity 1 is O16 (a steady 25 A feed with the flyback diode, ON in RUN), cavity 2 the 12 AWG return to the dash ground. **Speed is a low-side final stage** that inserts at `L3-BLW` as a plug-in adapter — module into the receptacle, motor into the module — switching at **≥ 20 kHz** on a logic-level PWM from the DCU, with **its own freewheel diode across the motor** (the PMU's diode clamps the high side only) and a ≥ 25 A rating, mounted in the resistor pack's hole so the airstream cools it. The PMU's own PWM tops out at 400 Hz, which a brushed blower would sing at (electrical D-257). A lost `0x300` changes nothing: the final stage is on a local wire.

**Servos (D-073).** Three hobby-class servos pull the existing mode, blend and recirculate cables; the factory control head leaves with the plastics. Own 5 V buck, endpoints calibrated at commissioning and stored with the climate memory, which restores from SD on wake (D-191) — no constant keep-alive.

**Temperature.** Cabin from a shaded NTC on a flying lead; outside air from the NTC at the nose on `L2-S 5` → `DP-DCU 2` (electrical D-256). Both to the bus, both to the cluster.

**Defog.** O4 is wired to the grid, configured and disabled (electrical D-210); the panel key enables it over CAN with the 15-minute auto-off already written — a comfort command, fails to off (D-251). Until the panel exists there is no rear defogger, by decision.

## 7 · Comfort

**The O15 block (FT31)** is this project's: a bussed block behind the centre stack that plugs into the `L3-CMF` receptacle (`L3-P 2`'s far end, electrical D-274), feeding the servo rail and every comfort load through the DCU's seven low-side FETs — seat heat ×2, seat cool ×2, mirror heat, nozzles, park de-icer — each gate pulled down so **every comfort load is off through a reset**, and the heat/cool interlock enforced in firmware as a second layer (D-073). Seats: elements and fans on the O15 block (D-048 / D-074), knobs on the panel, the runs laid under the console when the carpet is up for sound deadening. **Heated nozzles / de-icer:** the feed is `L2-S 6`, ending in the `L2-NZL` receptacle at the cowl (electrical D-274) (electrical D-256); it goes live only if a nozzle can be made to fit (`Q-303`).

## 8 · Body — mirrors and windows

**Mirrors do adjustment and heat, and nothing else (D-305).** The doors have exactly eight conductors each, so the part must be a conventional **3-wire motor pair with a resistive heater** — a 5-wire, LIN or module mirror does not fit and never will (`Q-300`). Heat: F14 at the sill, fed by `L4-P 4` from O15 (electrical D-254), switched by the DCU. Adjustment: the commands run dash → sill on **`L4-S2`** — shared common, LEFT X/Y, RIGHT X/Y (electrical D-255) — and either a mechanical mirror switch in the panel or the DCU's half-bridges drive them (`Q-305`, decided before the DCU carrier is laid out).

**Power windows** are entirely provisioned (D-131): plug the regulators and motors into `D1 / D2 1–2`, populate K5–K8 and F8 / F9 at the sill, uncap the four commands, enable the logic. The console switches are already in the electrical build's carts.

**Hatch and fuel-door release** — both factory solenoids exist and are wired to: `L4-M 3 / 4` run all the way to them, capped at the post (electrical D-274). What this project adds is the trigger — the panel → PMU pulse of D-180 through the K3 / K4 sockets at the dash node — and the hatch latch switch (`T-033`; `T-032` is the trigger).

## 9 · What fails how

| Failure | The driver sees | Still works | Why |
|---|---|---|---|
| ICU dies or reboots | the display dark — every gauge with it (electrical D-268) | the car — engine, lights, heat; the PMU still gates the fuel pump on its own A7, on a node the PMU excites (electrical D-260) | the ICU is never a control source (D-251) |
| DCU dies | climate frozen at the last servo positions; comfort loads off | every gauge; the blower at its last duty | gate pull-downs; blower command is a local wire (D-308) |
| CAN2 drops entirely | fuel, volts, AFR, climate and outside temp go to dim dashes | rpm, water, oil pressure, oil temp, speed — all ICU-local (D-083) | sender → ADC → pixel, no bus hop |
| One frame stalls (counter stops) | that frame's fields blank after its timeout | everything else | rolling counters, explicit timeouts (D-106) |
| PMU sleeps or faults | everything downstream is off anyway | — | nothing to protect |
| Oil-pressure sender fails | ICU shows a fault, PMU A7 reads FAULT | the pump keeps running — a FAULT reading counts as pressure present | fail-open (electrical D-249 / D-251) |
| Panel unplugged | no climate or comfort input | last climate state holds; defog off | the panel is a CAN node, not a switch |
| Wideband gauge off the bus | AFR dashes | everything else | vendor node, no dependency |
| Final stage fails | no blower | everything else; the motor is unharmed (O16 soft fuse) | plug-in adapter — swap it |

## 10 · Lighting, audio, radar

**Lighting is the second pass (D-201 / L-004)** — only after the electrical rebuild is shaken down on stock incandescent bulbs: custom tail lights (a thin LED strip per side in the stock aperture, 55 cm² of red against FMVSS 108's 50, a driver PCB per housing taking tail / brake / turn / reverse as logic inputs — D-107 / D-111), DOT sealed headlamp units inside the retained pop-up buckets (`Q-048`), LED bulbs everywhere else, then **every lamp soft fuse re-set from measurement** (D-122). The archived design is `99-ARCHIVE/Electrical/2026-08-31_lighting-body/TAIL-LIGHTS.md`.

**Audio** is the owner's own system (car P-007): a new amplifier beside the battery on its own fused line, new speakers. The head unit is the one audio device on the harness, and this project's only say is its criteria (D-128 – D-149): double-DIN, physical buttons, green button colour, wireless CarPlay, and **full-range unprocessed pre-outs**. Maps and media live there; the cluster keeps gauges (D-128).

**Radar** is a custom subsystem (D-096) — concealed sensors front and rear, DCU-managed, shown on the cluster. The rear link is the `L3-S3 ↔ L4-S` pass-through, the front sensor wires locally. Nothing commits until `V-061` designs it.

## 11 · The feature list

{{features}}

## 12 · Numbers

{{params}}

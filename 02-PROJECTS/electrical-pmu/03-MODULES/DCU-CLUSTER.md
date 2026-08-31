# DCU & ICU — the two CAN modules

*Rev 2026-08-31 · owns: module scope, the node split, hardware selection, power supply, the sensor set and the display decision. The message map is [`CAN-MESSAGES.md`](CAN-MESSAGES.md)'s; the cluster layout is `firmware/icu/cluster_core.h`'s.*

Two Teensy 4.1 nodes on CAN2 (D-084, D-094): a climate **DCU** and an
instrument cluster **ICU**. In full scope since D-075, joining a finished car
per the sequencing rule (D-081).

## Contents

1. Why two nodes · 2. What each node owns · 3. CAN2 bus · 4. DCU hardware ·
5. ICU hardware and the display · 6. Signals the ICU acquires · 7. Dash-post
drops · 8. Power supply · 9. What the build and the BOM gain · 10. Sequencing ·
Appendix A — display bandwidth arithmetic (background)

---

## 1 · Why two nodes, and why they exist at all

**The PMU has no spare analog input** (D-076). All eight A1–A8 and all eight
A9–A16 are allocated. Water temp, oil pressure, oil temperature, VSS and tach
therefore cannot be read by the PMU — there is no pin left for them. They were
always going to need a reader, and that reader is the ICU.

Two boards, not one (D-094): a blend-door firmware bug must never blank the
tachometer. The isolation is **engine instrumentation from the comfort
system** (D-083), not display from climate.

## 2 · What each node owns (D-083)

| Node | Owns | Fails how |
|---|---|---|
| **ICU** | Instrument display **and the engine sensors that feed it** — tach, water temp, oil pressure, oil temp, VSS, alternator sense, brake fluid level | Cluster goes dark. Nothing else is affected |
| **DCU** | Climate, HVAC servos, comfort bus switching, the heat/cool interlock (D-073) | Climate stops. **Gauges keep working** |

**The principle:** a gauge's sender wires into the box that draws the gauge.
Sender → ADC → pixel, no bus hop, no second processor, no shared failure.

| Failure | Consequence |
|---|---|
| DCU dies | No climate control. Tach, temp, oil pressure all normal |
| ICU dies | Cluster dark. Car runs, climate works, PMU unaffected |
| CAN2 drops entirely | **ICU still shows tach, water temp, oil pressure, oil temp, speed** from its own inputs. Only fuel level and voltage blank |
| PMU sleeps or faults | Everything downstream is off anyway — nothing to protect |

The gauges you actually need while driving have **zero bus dependency**. CAN
carries only the values the PMU already measures better than a second sensor
would (D-078).

## 3 · CAN2 bus — five nodes (D-079)

| Node | Role | Termination |
|---|---|---|
| PMU-24 DL | Publishes key state, voltage, fuel level, output states, channel currents | Software, at the dash end |
| CAN keypad | Buttons in | — |
| **ICU** | Publishes engine sensors and sensor health; consumes everything | — |
| **DCU** | Publishes climate and comfort state; consumes keypad and ICU | — |
| LS ECU | Future | **120 Ω at this end** — fitted now, capped, at the L1-S1 drop |

**Bus rules:** 500 kbps, CAN 2.0B, 11-bit IDs (D-086) — the PMU is CAN 2.0
only, so the shared bus cannot be FD. 120 Ω at exactly two points. Keep every
drop short: stubs off a linear backbone, not a star. The dash is electrically
one node point — four devices within a few inches is a cluster, not four stubs.
Twisted pair, 16 AWG, roughly 33–40 twists per metre, routed away from the
pop-up motor legs and the coil feed.

**The private link (D-087):** a second twisted pair runs DCU ↔ ICU, capped at
both ends. Both Teensys have spare CAN controllers and one supports CAN-FD.
Cheap now, impossible later.

## 4 · DCU hardware

| Item | Spec | Note |
|---|---|---|
| MCU | **Teensy 4.1**, socketed (D-084) | Same board as the ICU: one toolchain, shared code, a spare that fits either node |
| CAN transceiver | **TCAN1042 / TCAN1051** on the carrier PCB (D-085) | SN65HVD230 modules are the bench parts only |
| Servo drivers | 3–4 channels | HVAC blend, mode, recirc doors |
| Comfort switching | 5–6 MOSFET or relay channels | Seats, mirrors, nozzles, de-icer off O15 (D-073) |
| Power | §8 | |
| Climate memory | `V-056` → D-191 — whether a constant keep-alive is needed at all | Fuse position `Q-061` → D-180 |

**Firmware:** not started. `dcu.ino` + `climate.h` mirroring the ICU
structure is forward-work item F-001 — nothing blocks it.

## 5 · ICU hardware and the display

| Item | Spec | Note |
|---|---|---|
| MCU | **Teensy 4.1**, socketed | 8 MB PSRAM to be fitted on the pads (D-170) |
| **Display** | **One 12.3″ bar panel, 1280 × 480 canvas** (`Q-060` → D-193; supersedes D-150's 800 × 480) | Instant-on is a hard requirement (D-192). One bezel aperture |
| **Interface** | **BT817 EVE over QSPI** — dirty-rectangle tiles from a 614 KB PSRAM framebuffer (D-168 as amended by D-193) | Driver written (`firmware/icu/bt817.h`, F-008); timing constants await `V-084` |
| Glass + bridge | `V-085` decides the chain | (i) SN75LVDS83B → 330-nit 1280 × 480 cluster glass, only if the brow shades it (`T-007`); (ii) TFP410-class HDMI → 900–1000-nit 1920 × 720 panel via its scaler board — the default |
| Backlight dimming | PWM, referenced to O20 via DP-ICU 5 | Matches panel dimming automatically |
| **IMU** | MPU-6050 / ICM-20948 class, I²C, on the carrier (D-109, D-161) | G-meter, pitch. Axis convention in D-161; PCB orientation `V-073` |
| CAN transceiver | TCAN1042 / TCAN1051 (D-085) | |
| Page switching | A small dedicated momentary button by the display (D-169) | |

**The display connects directly to the Teensy behind the bezel** on a short
ribbon or flying leads and **never crosses the harness** (D-159). DP-ICU's
eleven-plus-one conductors are correct as they are.

**Sunlight readability is the real-world killer.** A cheap TFT that looks
superb on a desk is unreadable at noon with the sun behind you — 800–1000 nits
minimum, optically bonded or AR treated, and the factory binnacle's hood.

**Config as data** ([`BENCH-BRINGUP.md`](BENCH-BRINGUP.md) Stage 6): layout thresholds, colours and
units on the SD card, with a safe-mode render path that works if the config is
missing or corrupt. A cluster that fails to boot because of a typo is worse
than no cluster. Oil pressure has **no hardwired lamp** — the ICU shows it,
and the factory cluster stays in place through ICU development (D-090, D-094).

## 6 · Signals the ICU acquires

These are the wires that had no reader. They route from `L1-S1`/`L1-S2`
through the dash post to **DP-ICU** — the box that draws the gauge.

| Signal | Type | Conditioning at the ICU | DP-ICU |
|---|---|---|---|
| Water temp | Resistive sender | Divider vs a known pull-up | 6 |
| Oil pressure | Resistive sender | Divider | 7 |
| Oil temperature | Resistive sender (new) | Divider | 8 |
| Tachometer | Coil primary pulse, >12 V spikes | **Opto or comparator. Never raw to an ADC** (D-082) | 9 |
| VSS | Pulse (new sensor) | Schmitt input | 10 |
| Alternator sense | Lamp-driven | Divider | 11 |
| Brake fluid level | Closure | Direct, pull-up | 12 (`A-010`) |
| Fuel level | — | **Read by the PMU on A7**, published on 0x120 | — |
| Battery voltage, key state, channel currents | — | **PMU publishes them.** Never duplicated (D-078) | — |

Coolant level and oil level have no ICU cavity and are capped in L1-S2
(`A-010`). The conditioning schematic — dividers, RC filters, clamp diodes for
every input, opto for the tach — is forward-work item F-003/F-004. **The Teensy
4.1 is 3.3 V only and not 5 V tolerant.**

## 7 · Dash-post drops (D-080, D-083)

| Code | What | Housing | Used |
|---|---|---|---|
| **DP-ICU** | Power, ground, CAN2, dimming reference, six engine sensors, brake fluid | DT06-12S | 12 |
| **DP-DCU** | Power, constant (if `V-056` → D-191), ground, CAN2 | DT06-6S | 5 |

Every cavity is in [`../02-HARNESS/PIN-MAP.md`](../02-HARNESS/PIN-MAP.md). The DCU also takes a short
heavy lead off O15 at the plate for the comfort bus it switches, and drives the
HVAC servos locally — the heater box is inches away. Neither crosses a leg.
Both modules mount behind the dash face, not against the windscreen (D-084).

## 8 · Power supply for both modules (D-088)

Neither Teensy goes anywhere near raw 12 V.

| Stage | Part | Why |
|---|---|---|
| Reverse polarity | Schottky or ideal-diode controller | Survives a backwards jump |
| Transient | TVS, SMBJ33A | **Load dump.** An alternator disconnect can put 60 V+ on the rail |
| Filter | Series inductor + bulk cap | EMI, and rides out cranking dips |
| Regulation | 12 V → 5 V automotive buck (TPS54331 class) | Not a bench LM7805 — it will cook |
| Local | Teensy's onboard 3.3 V | Fine for the MCU |

**The load-dump TVS is not optional.** Both modules are switched from O10, so
neither has a standby draw to budget — except `V-056` → D-191.

## 9 · What the modules add

| Phase | Addition | Hrs |
|---|---|---|
| 2B | Firmware — CAN, sensor acquisition, display, climate logic | 155–325 (~90–125 done) |
| 2B | Carrier PCBs, power boards, conditioning | in the above |
| 4 | DP-DCU and DP-ICU on the plate | 4 |
| 5 | Dash module harness | 8–12 |
| 9 | Install, calibrate senders, tune the display | 20–35 |
| 9 | Shakedown — sensor accuracy, legibility at night and in sun | 10–15 |

Money: [`../05-PROCESS/BOM.md`](../05-PROCESS/BOM.md) §Wave 3 — the module era, ~$510–1,170.

## 10 · The sequencing rule that must not break (D-081)

**The car drives fully on the PMU with dumb switches before either module is
connected.** Phase 6 completes, the factory harness comes out, and the car is
finished. Only then do the DCU and ICU join. They add capability to a working
car and are never a dependency for it starting, running, or being legal.

Two PMU functions were written against an RPM the PMU cannot see until the ICU
publishes 0x200 — the fuel-pump cut and the crank interlock. The interim rule
is `Q-064` → D-183.

---

## Appendix A — driving a wide panel: the arithmetic (background)

*Settled by D-168. Kept because the numbers still govern what the cluster can
afford.*

800 × 480 at 16 bpp is 768 KB per full frame; at 8 bpp (RGB332) it is 384 KB —
which **fits in the Teensy's 1 MB RAM**, so the framebuffer lives there and
only changed 16 × 16 tiles go over SPI.

| Interface | Throughput | Full frames/s |
|---|---|---|
| SPI at 60 MHz | ~6 MB/s real | ~8 — unusable for full redraws |
| FlexIO 8-bit parallel | ~20 MB/s | ~26 |
| FlexIO 16-bit parallel | ~40 MB/s | ~52 |
| RA8875/RA8876 controller | commands only | the controller renders |

A cluster does not redraw the whole screen. The static layer is drawn once at
boot; digits, bars and tell-tales are the only things that move — roughly 21 %
of the screen can change at all, and a realistic frame touches 10,000–30,000
pixels, 2–5 ms at 8 bpp. **Never clear the whole screen in a redraw path** — one
careless `fillScreen()` costs 64 ms and turns a smooth cluster into a stuttering
one. That single discipline is the whole technique, and `cluster_core.h`
enforces it by diffing every widget's own state.

Option 1 (a controller panel) remains the fallback if a large analogue sweep
is ever wanted; Option 2 (FlexIO) was never needed.

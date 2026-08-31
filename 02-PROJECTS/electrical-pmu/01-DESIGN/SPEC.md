# SPEC — Electrical / PMU-24 DL

*Rev 2026-08-31 (Rev D) · owns: pin allocation, connector geometry, wire colours, relay and fuse schedule, module split, and the status of every cavity.*

Canonical. Current state only — no history, no rationale, no alternatives.
Those live in [`../05-PROCESS/DECISIONS.md`](../05-PROCESS/DECISIONS.md). If it is here, it is the plan.
The pin and cavity tables in §4–§8 are **generated** from
`../02-HARNESS/data/pmu_pins.csv`; edit the CSV and run
`../05-PROCESS/tools/gen.py`, never the table.

**Baseline:** 12A / Weber · stock incandescent bulbs (D-124) · manual windows,
power windows provisioned (D-131) · LS + CD009 reserved (D-007) · DCU + ICU in
scope but joining a finished car (D-075, D-081).

> **Rev D changes (from Rev C):** status column on every cavity · 2 AWG main
> feed (D-091) · K9 on the inner fender (D-148) · windows PROVISIONED (D-131) ·
> terminal ranges from pinout v1.2/1.3 · display interface recorded (D-168) ·
> §13's physical confirmation folded into §11 · all paths current.

## Contents

1. Device · 2. Terminals and wire colour · 3. The black box · 4–8. Pin
schedule (generated) · 9. Connectors · 10. Modules · 11. Connector geometry ·
12. Cavity status · 13. Cross-reference

---

## 1 · Device

| Field | Value |
|---|---|
| Device | ECUMaster PMU-24 DL |
| Housing | Sicma / FCI 39-position — geometry confirmed in the hand, §11 |
| Main feed | Central stud, 150 A max constant |
| Outputs | 10 × 25 A (O1–O5, O12–O16) · 6 × 15 A (O6–O11) · 8 × 7 A (O17–O24) |
| Inputs A1–A8 | Dedicated. 0–5 V, 10-bit. 20 V max |
| Inputs A9–A16 | Shared with O17–O24. 0–20 V, **12-bit**. 30 V max |
| Pull options | 1 MΩ down · 10 kΩ down · 10 kΩ up |
| CAN | CAN1 fixed 1 Mbps, **no internal termination** · CAN2 software termination |

**Special channels:** O1 and O16 have integrated high-power flyback diodes.
O8 has wiper motor braking.

**Current measurement floor:** 25 A ch 0.5 A · 15 A ch 0.2 A · 7 A ch 0.1 A.

**Every one of the 24 shared-and-dedicated channels is spoken for.** Six of the
eight shared pins are outputs (O17–O22) and two are inputs (A15, A16). Engine
sensors are read by the ICU, not the PMU (D-076/083). The four pin-less functions were ruled in `Q-063` → D-182: horn on the wake pin, washer on K12, mechanical wiper park, inhibitor onto A4/A5 (H-007).

## 2 · Terminals and wire colour

| Terminal | Part | Wire range | Used for |
|---|---|---|---|
| 2.8 mm large | 211CC3S3120 | 10–12 AWG | The ten 25 A outputs and GND (pin 25) |
| 2.8 mm | 211CC3S2120 | 14–16 AWG | Pin 15 (+5 V) only |
| 1.5 mm | 211CC2S2160P | **14–17 AWG** | Every 15 A and 7 A output, every input, CAN |

The 1.5 mm range is 14–17 AWG per pinout doc v1.2/1.3 (v1.0 said 13–17).
Either way **signal wire is 16 AWG, not 18** (D-027), and 14 AWG is the
heaviest wire any 15 A output can take, with no headroom above it (D-046).

**Base colour encodes channel class. Tracer encodes circuit** (D-016). You can
identify a wire's origin without a diagram.

| Base | Class | AWG |
|---|---|---|
| **RED** | 25 A output; heavy feeds | 12 (2 for the main feed) |
| **ORN** | 15 A output | 14 |
| **VIO** | 7 A output | 16 |
| **GRY** | Analog input, sender and sensor wires | 16 |
| **PNK** | +5 V reference | 16 |
| **BLU** | Wake sources and switched-12 V relay commands | 16 |
| **YEL / GRN** | CAN H / CAN L (BLK tracer = CAN2) | 16 twisted |
| **BLK** | Ground | 10 at the panel, 16 elsewhere |

> This is **not** the factory colour scheme. The factory diagram uses two-letter
> codes where `GY` means green/yellow, not gray. See [`GLOSSARY.md`](GLOSSARY.md).

## 3 · The black box

Removable aluminium backer plate in the dash. Carries the PMU, **4 relays (D-182, D-186) in
10 sockets**, 12 of the 15 fuse positions (F8, F9 and F14 are at the sill; F15 is D-198's exciter branch), always-hot busbar, ground bus, the diode-OR
wake strip and the constant bus. Sub-circuits are drawn in [`SCHEMATICS.md`](SCHEMATICS.md).

### Relays — 10 in the design, 4 populated on the plate (D-182, D-186)

| Relay | Function | Location | State |
|---|---|---|---|
| K1–K2 | Pop-up run relays, LH and RH — single-direction motors (D-186) | Plate | LIVE |
| K3–K4 | Freed by D-186 | Plate sockets | SPARE |
| K5–K8 | Window H-bridges, driver and passenger | Sill node | **PROVISIONED** — sockets fitted, relays not populated (D-131) |
| K9 | Start relay | Inner fender / firewall, engine bay (D-148) | LIVE |
| K10 | A/C compressor clutch | Engine bay, factory circuit (D-012) | Factory — untouched |
| K11 | Constant-bus master, driven by O22 | Plate | LIVE |
| K12 | Washer pump pulse relay (Q-063 → D-182) | Plate — takes a spare socket | DESIGN — circuit detail lands in [`SCHEMATICS.md`](SCHEMATICS.md) with H-008 |

### Fuses

| Fuse | Rating | Feeds | Off | State |
|---|---|---|---|---|
| F1 | 15 A | Head unit constant keep-alive | Busbar via K11 | LIVE |
| F2 | 2 A | Diagnostic port +12 V (DP-DIAG 3) | Busbar | LIVE |
| F3 | 5 A | Wake diode network supply | Busbar | LIVE |
| F4 | 10 A | A/C factory circuit | Busbar | LIVE |
| F5 | 30 A | Amp / audio constant | Busbar via K11 | LIVE |
| F6 | 10 A | Pop-up motor bus — LH branch | O1 downstream | LIVE |
| F7 | 10 A | Pop-up motor bus — RH branch | O1 downstream | LIVE |
| F8 | 15 A | Window motor bus — DRV branch | O1 downstream, **at the sill** | PROVISIONED — position only |
| F9 | 15 A | Window motor bus — PASS branch | O1 downstream, **at the sill** | PROVISIONED — position only |
| F10 | 10 A | Comfort bus — heated seats | O15 downstream | LIVE position, loads deferred |
| F11 | 5 A | Comfort bus — nozzles, de-icer | O15 downstream | LIVE position, loads deferred |
| F12 | 5 A | Interior lighting branch | O20 downstream | LIVE |
| F13 | — | Radar module feed (D-039; freed by `V-056` → D-191) | Busbar | DEFERRED until `V-061` designs the subsystem |
| F14 | 5 A | Mirror heat branch | O15 → sill via L4-P 4 (Q-062 → D-181), **at the sill** | DEFERRED |
| F15 | 7.5 A | Alternator BW excitation — factory-spec field feed (D-198) | O12 downstream, the block's twelfth position | LIVE |

F6–F12 and F15 are downstream branch protection — the PMU soft fuse protects the
channel, these protect each leg off a shared bus.

**Interfaces at the dash post:** 2 lugs (DP-BAT, DP-GND) · 15 leg receptacles (L1-S is two housings)
· DP-DIAG · DP-KEY · DP-ICU · DP-DCU.

<!-- gen:pins -->
*Generated by `05-PROCESS/tools/gen.py` from `02-HARNESS/data/*.csv` — edit the CSV, not this table.*

### 4 · Power, ground and comms

| Pin | Name | Circuit | AWG | Colour | To |
|---|---|---|---|---|---|
| STUD | +12V BATT | Main supply, 150 A max constant | 2 | RED | DP-BAT ← Class-T 150 A |
| 25 | GND | Device ground + flyback return for every inductive load | 10 | BLK | DP-GND, ≤6 in |
| 7 | +12V SW | Wake. Diode-OR: ACC, RUN, hazard, door pin, horn, O22 latch | 16 | BLU | Panel diode strip |
| 15 | +5V OUT | Ladder + sender reference, 500 mA ceiling | 16 | PNK | L1-S1 8 + L2-S 4 + L3-S1 7 + L4-S 4 |
| 23 | CAN1H | Laptop / config. 1 Mbps fixed, no internal termination | 16 tw | YEL | DP-DIAG 1 |
| 36 | CAN1L | Laptop / config | 16 tw | GRN | DP-DIAG 2 |
| 24 | CAN2H | Vehicle bus 500 kbps — keypad, ICU, DCU, future LS ECU | 16 tw | YEL/BLK | L1-S1 9 + DP-KEY 1 + DP-ICU 3 + DP-DCU 4 |
| 37 | CAN2L | Vehicle bus | 16 tw | GRN/BLK | L1-S1 10 + DP-KEY 2 + DP-ICU 4 + DP-DCU 5 |

### 5 · 25 A outputs — 12 AWG, large cavities

Estimates only. Never set a soft fuse from these — the measured column lives in `CHANNEL-SCHEDULE.md`.

| Pin | Ch | Name | Circuit | Est. A | Colour | To | Status |
|---|---|---|---|---|---|---|---|
| 38 | O1 | `MOTOR_BUS` | Motor bus — K1–K2 pop-up run relays on the plate (D-186); K5–K8 at the sill provisioned empty | 9.5 | RED/WHT | Relay bank + L4-P 3 (capped) | LIVE |
| 39 | O2 | `HEAD_LOW` | Headlight LOW | 3.0 | RED/BLK | L2-P1 1 | LIVE |
| 26 | O3 | `HEAD_HIGH` | Headlight HIGH | 3.5 | RED/BRN | L2-P1 2 | LIVE |
| 13 | O4 | `DEFOG` | Rear defog grid | 11.5 | RED/GRN | L4-P 1 | LIVE |
| 12 | O5 | `FUEL_PUMP` | Fuel pump — Carter P4070 now; sized for the Aeromotive 340 later | 2.0 | RED/YEL | L4-P 2 | LIVE |
| 2 | O12 | `IGNITION` | Ignition / coil feed | 5.0 | RED/BLU | L1-P 1 | LIVE |
| 1 | O13 | `LS_ECU` | RESERVED — LS ECU + injectors | — | RED/ORN | L1-P 2 (capped) | RESERVED |
| 14 | O14 | `LS_FAN` | RESERVED — LS cooling fan(s) | — | RED/GRY | L1-P 3 (capped) | RESERVED |
| 27 | O15 | `COMFORT` | Comfort bus — dumb 25 A feed; the DCU switches loads downstream | 14.0 | RED/VIO | L3-P 2 + DCU tap | LIVE |
| 28 | O16 | `BLOWER` | Blower motor feed | — | RED/PNK | L3-P 1 | LIVE |

### 6 · 15 A outputs — 14 AWG

| Pin | Ch | Name | Circuit | Est. A | Colour | To | Status |
|---|---|---|---|---|---|---|---|
| 11 | O6 | `TAIL_PARK` | Tail / park / marker / plate — PARK and HEAD | 4.4 | ORN/BRN | L2-M 7 + L4-M 1 | LIVE |
| 10 | O7 | `BRAKE` | Brake lamps | 3.9 | ORN/GRN | L4-M 2 | LIVE |
| 9 | O8 | `WIPE_LOW` | Wiper LOW — braking channel | 4.0 | ORN/BLU | L2-M 1 | LIVE |
| 5 | O9 | `WIPE_HIGH` | Wiper HIGH | 5.5 | ORN/WHT | L2-M 2 | LIVE |
| 4 | O10 | `ACCESSORY` | Accessory bus — USB-C, head unit switched, ICU + DCU logic | 2.5 | ORN/YEL | L3-M 1 + DP-ICU 1 + DP-DCU 1 + DP-KEY 3 | LIVE |
| 3 | O11 | `HORN` | Horn pair | 6.0 | ORN/BLK | L2-M 3 | LIVE |

### 7 · 7 A shared pins — 16 AWG

Each of O17–O24 can be an output or an analog input (A9–A16). Six are outputs; O23 and O24 are configured as inputs A15 and A16 — there is no spare on this bank.

| Pin | Ch | Mode | Name | Circuit | Colour | To | Status |
|---|---|---|---|---|---|---|---|
| 6 | O17 | OUT | `TURN_L` | Turn LEFT — flashed natively | VIO/GRN | L2-M 5 + L4-M 5 | LIVE |
| 33 | O18 | OUT | `TURN_R` | Turn RIGHT | VIO/YEL | L2-M 6 + L4-M 6 | LIVE |
| 20 | O19 | OUT | `REVERSE` | Reverse lamps | VIO/BLK | L4-M 7 | LIVE |
| 34 | O20 | PWM | `INTERIOR` | Interior + details bus and the ICU dimming reference | VIO/WHT | L4-M 8 + L3-S1 8 + DP-ICU 5 | LIVE |
| 21 | O21 | OUT | `START_RLY` | Start relay coil → K9 on the inner fender | VIO/RED | L1-S1 1 | LIVE |
| 8 | O22 | OUT | `KEEP_ALIVE` | Keep-alive latch → diode → pin 7; drives K11 | VIO/BLU | Panel diode strip | LIVE |
| 35 | A15 | IN | `HEADLIGHT_SW` | Headlight ladder — OFF / PARK / HEAD. Also commands pop-up raise | GRY/WHT | L3-S1 2 | LIVE |
| 22 | A16 | IN | `KEY_POS` | Key ladder — OFF / ACC / RUN / START | GRY/RED | L3-S1 1 | LIVE |

### 8 · Dedicated inputs A1–A8 — 16 AWG

0–5 V, 10-bit. Every switch goes to ground through a finite resistor (D-053), read against the internal 10 kΩ pull-up. Values in `LADDERS.md`.

| Pin | In | Name | Signal | Colour | To | Status |
|---|---|---|---|---|---|---|
| 29 | A1 | `TURN_STALK` | Turn stalk — L / off / R | GRY/GRN | L3-S1 3 | LIVE |
| 16 | A2 | `WIPER_STALK` | Wiper stalk — off / INT / LO / HI / WASH | GRY/BLU | L3-S1 4 | LIVE |
| 30 | A3 | `BRAKE_PEDAL` | Brake pedal switch | GRY/ORN | L3-S1 5 | LIVE |
| 17 | A4 | `POPUP_L` | Pop-up LEFT position | GRY/BLK | L2-S 1 | LIVE |
| 31 | A5 | `POPUP_R` | Pop-up RIGHT position | GRY/BRN | L2-S 2 | LIVE |
| 18 | A6 | `DOOR_PINS` | Door pins — driver / passenger | GRY/VIO | L4-S 2 | LIVE |
| 32 | A7 | `FUEL_LEVEL` | Fuel level sender | GRY/YEL | L4-S 1 | LIVE |
| 19 | A8 | `HAZARD` | Hazard switch — closure; wake source is a separate conductor | GRY/PNK | L3-S1 6 | LIVE |

**39 cavities, all allocated:** 7 power/comms + 10 × 25 A + 6 × 15 A + 8 shared + 8 dedicated. Status key: **LIVE** wired and enabled at migration · **PROVISIONED** wire run and capped, hardware fitted empty (D-131) · **RESERVED** capped for the LS swap (D-007) · **DEFERRED** conductor allocated, subsystem not designed · **OPEN** a home is still needed.
<!-- /gen:pins -->

## 9 · Connectors — summary

**Everything is Deutsch DT (size 16), DTP (size 12) or DTM (size 20). No
AMPSEAL anywhere** (D-070) — two crimp dies, one supplier.

| Leg | Connectors |
|---|---|
| L1 Engine | L1-P (DTP-4) · L1-S1, L1-S2 (DT-12 ×2) |
| L2 Front | L2-P1, L2-P2 (DTP-4 ×2) · L2-M (DT-8) · L2-S (DT-6) |
| L3 Dash | L3-P (DTP-2) · L3-M (DT-2) · L3-S1, L3-S2 (DT-12 ×2) · L3-S3 (DT-8) |
| L4 Rear | L4-P (DTP-4) · L4-M (DT-12) · L4-S (DT-8) |
| Sill (inside L4) | D1, D2 (DT-8 each, D-092) |
| Dash post drops | DP-ICU (DT-12) · DP-DCU (DT-6) · DP-DIAG, DP-KEY (DTM-4) |

**15 leg housings (14 codes — L1-S is two housings) + 2 door + 4 drops + 2
lugs + the device connector = 24 mated pairs.** Housing part numbers and wedgelocks: [`../02-HARNESS/CONNECTORS.md`](../02-HARNESS/CONNECTORS.md).
Every cavity: [`../02-HARNESS/PIN-MAP.md`](../02-HARNESS/PIN-MAP.md). One diagram per leg:
`../02-HARNESS/diagrams/`.

## 10 · Modules — DCU and ICU

Full detail in [`../03-MODULES/DCU-CLUSTER.md`](../03-MODULES/DCU-CLUSTER.md).

| Node | Owns | Board |
|---|---|---|
| **ICU** | Cluster display **and** tach, water temp, oil pressure, oil temp, VSS, alternator sense, brake fluid level | Teensy 4.1 (D-084) |
| **DCU** | Climate, HVAC servos, comfort bus switching | Teensy 4.1 |

**Display:** a 12.3″ bar panel on a **1280 × 480 canvas**, driven by a BT817
EVE over QSPI — dirty-rectangle tiles from a 614 KB PSRAM framebuffer
(D-168 as amended by D-193; supersedes D-150). Instant-on is a hard
requirement (D-192). Behind the bezel, never crossing the harness (D-159).
Glass variant and bridge chain: `V-084` / `V-085`.

**Rule:** a gauge's sender wires into the box that draws the gauge (D-083). If
CAN2 fails, the ICU still shows every critical gauge from its own inputs.

**Rule:** if the PMU measures it, the ICU reads it from CAN — fuel level,
battery voltage, key state, channel currents. Never duplicated (D-078).

**Sequencing rule (D-081):** the car drives fully on the PMU with dumb switches,
the factory harness comes out, and the build completes — *then* the modules
join. `Q-064` → D-183 covers the two PMU functions written against an RPM the PMU
cannot see until then.

**CAN transceivers:** SN65HVD230 modules on the bench (in hand); TCAN1042/1051
on the carrier PCBs in the car (D-085). Both are correct — for different
places.

## 11 · Connector geometry — CONFIRMED in the hand

From the CAD (D-045) and confirmed on the physical part on receipt (D-134,
D-139). `[V-068 CLOSED]`.

```
   connector face toward you, PMU flat and upright

    pin 1                                    pin 13
      ↓                                        ↓
   ┌─────────────────────────────────────────────┐
   │  ■ ■ □ □ □ □ □ □ □ □ □ ■ ■                 │  row 1   1–13
   │  ■ ■ □ □ □ □ □ □ □ □ □ ■ ■                 │  row 2  14–26   [PURPLE
   │  ■ ■ □ □ □ □ □ □ □ □ □ ■ ■                 │  row 3  27–39     LOCK]
   └─────────────────────────────────────────────┘
      ↑                                        ↑
   pin 27                                   pin 39

   ■ = large 2.8 mm    □ = small 1.5 mm
```

Numbered left→right, top→bottom, looking at the device. **Pin 1 is top-left,
at the end furthest from the purple lock.** Each row is **2 large · 9 small ·
2 large**; the twelve large cavities are pins 1, 2, 12, 13, 14, 15, 25, 26,
27, 28, 38, 39 — exactly the ten 25 A outputs, GND and +5 V.

| Property | Confirmed |
|---|---|
| Large cavities | 12 — marking `FCI` |
| Small cavities | 27 — marking `FCI 125` |
| Terminal stock, housing #1 | 16 large (4 spare) · **27 small (0 spare)** — D-135 |

**Order spare 1.5 mm terminals before Phase 4** (T-044) and **mark the housing
beside cavity 1** with a paint pen (T-043).

**Enclosure:** 131 × 112.1 × 32.5 mm. Mounting 3 × Ø6.5 mm. Connector face on
the short edge, +12 V stud opposite. Allow clearance for the connector lever.

## 12 · Cavity status — the vocabulary

| Status | Means | Examples |
|---|---|---|
| **LIVE** | Wired, enabled at migration | Almost everything |
| **PROVISIONED** | Wire run, terminated and capped; sockets and fuse positions fitted empty | Power windows — K5–K8, F8/F9, L4-P 3, L4-M 9–12, L3-S2 3–6, D1/D2 1–2 (D-131) |
| **RESERVED** | Capped for the LS swap | O13, O14, L1-S2 4–6, the CAN2 drop (D-007) |
| **DEFERRED** | Conductor allocated, subsystem not yet designed | Radar link, mirror motors and heat, comfort loads — [`CAVITY-STATE.md`](../02-HARNESS/CAVITY-STATE.md) lists them |
| **OPEN** | Needs a pin or fuse position that does not exist | *None — the 0.23 ruling emptied this category (`Q-061` → D-180 · `Q-062` → D-181 · `Q-063` → D-182)* |
| **SPARE** | Capped, no purpose assigned | See [`../02-HARNESS/CAVITY-STATE.md`](../02-HARNESS/CAVITY-STATE.md) |

Nothing gets deleted from a housing. A change of status is a config change
and an uncapping, never a re-pin (D-004).

## 13 · Cross-reference

| Need | File |
|---|---|
| Why a decision was made | [`../05-PROCESS/DECISIONS.md`](../05-PROCESS/DECISIONS.md) |
| What is undecided | [`../05-PROCESS/OPEN.md`](../05-PROCESS/OPEN.md) |
| What only Camden can do | [`../05-PROCESS/TASKS-CAMDEN.md`](../05-PROCESS/TASKS-CAMDEN.md) |
| Estimated draw, method, signal types | [`LOADS.md`](LOADS.md) |
| Measured draw and soft-fuse values | [`CHANNEL-SCHEDULE.md`](CHANNEL-SCHEDULE.md) |
| Resistor values | [`LADDERS.md`](LADDERS.md) |
| Wake network, pop-up relays, constant bus, grounds | [`SCHEMATICS.md`](SCHEMATICS.md) + [`panel-sheet.svg`](panel-sheet.svg) |
| PMU configuration and logic | [`PMU-CONFIG.md`](PMU-CONFIG.md) |
| Every cavity | [`../02-HARNESS/PIN-MAP.md`](../02-HARNESS/PIN-MAP.md) |
| What is live / provisioned / open | [`../02-HARNESS/CAVITY-STATE.md`](../02-HARNESS/CAVITY-STATE.md) |
| Housing part numbers, wedgelocks | [`../02-HARNESS/CONNECTORS.md`](../02-HARNESS/CONNECTORS.md) |
| Leg contents and boundaries | [`../02-HARNESS/engine.md`](../02-HARNESS/engine.md), [`front-chassis.md`](../02-HARNESS/front-chassis.md), [`dash.md`](../02-HARNESS/dash.md), [`rear-cabin.md`](../02-HARNESS/rear-cabin.md) |
| Sill relays and door connectors | [`../02-HARNESS/sill-node.md`](../02-HARNESS/sill-node.md) |
| DCU / ICU | [`../03-MODULES/DCU-CLUSTER.md`](../03-MODULES/DCU-CLUSTER.md) |
| Battery and backbone | [`../04-BUILD/BATTERY-INSTALL.md`](../04-BUILD/BATTERY-INSTALL.md) |
| Parts and money | [`../05-PROCESS/BOM.md`](../05-PROCESS/BOM.md) |
| Build sequence | [`../04-BUILD/CHECKLIST.md`](../04-BUILD/CHECKLIST.md) |
| Factory wiring | `../../../01-REFERENCE/factory-circuits/` |

# SPEC — Electrical / PMU-24 DL

Canonical. Only current state. No history, no rationale — those live in
`DECISIONS.md`. If it's here, it's the plan.

**Rev C** · 12A / Weber baseline · LS + CD009 reserved · DCU + ICU in scope

> **Rev C changes:** DCU and digital cluster in full scope (D-075) · sensor
> acquisition assigned to the ICU, not the DCU (D-083) · window relays moved to
> the sill, L4-P2 deleted (D-065/066) · relay bank split, 5 in the box (D-067) ·
> connector schedule final, all Deutsch (D-070) · retract switch deleted (D-038) ·
> radar detector added (D-039).

---

## 1 · Device

| Field | Value |
|---|---|
| Device | ECUMaster PMU-24 DL |
| Housing | Sicma / FCI 39-position — **geometry confirmed, §11** |
| Main feed | Central stud, 150 A max constant |
| Outputs | 10 × 25 A (O1–O5, O12–O16) · 6 × 15 A (O6–O11) · 8 × 7 A (O17–O24) |
| Inputs A1–A8 | Dedicated. 0–5 V, 10-bit. 20 V max |
| Inputs A9–A16 | Shared with O17–O24. 0–20 V, **12-bit**. 30 V max |
| Pull options | 1 MΩ down · 10 kΩ down · 10 kΩ up |
| CAN | CAN1 fixed 1 Mbps, **no internal termination** · CAN2 software termination |

**Special channels:** O1 and O16 have integrated high-power flyback diodes.
O8 has wiper motor braking.

**Current measurement floor:** 25 A ch 0.5 A · 15 A ch 0.2 A · 7 A ch 0.1 A.

**All 16 analog inputs are allocated.** There is no spare. Engine sensors are
read by the ICU, not the PMU (D-076/083).

## 2 · Terminals and wire colour

| Terminal | Part | Wire range | Used for |
|---|---|---|---|
| 2.8 mm large | 211CC3S3120 | 10–12 AWG | 25 A outputs, GND |
| 2.8 mm | 211CC3S2120 | 14–16 AWG | Pin 15 (+5 V) |
| 1.5 mm | 211CC2S2160P | **13–17 AWG** | 15 A / 7 A outputs, inputs, CAN |

Signal wire is **16 AWG**, not 18.

**Base colour encodes channel class. Tracer encodes circuit** (D-016). You can
identify a wire's origin without a diagram.

| Base | Class | AWG |
|---|---|---|
| **RED** | 25 A output | 12 |
| **ORN** | 15 A output | 14 |
| **VIO** | 7 A output | 16 |
| **GRY** | Analog input | 16 |
| **PNK** | +5 V reference | 16 |
| **BLU** | Wake / +12 V SW | 16 |
| **YEL / GRN** | CAN H / CAN L | 16 tw |
| **BLK** | Ground | 10 at the panel |

> This is **not** the factory colour scheme. The factory diagram uses two-letter
> codes where `GY` means green/yellow, not gray. See `GLOSSARY.md`.

## 3 · The black box

Removable aluminium backer plate in the dash. Carries the PMU, **5 relays in 10
sockets**, 13 fuses, always-hot busbar, ground bus, diode-OR wake network,
constant bus.

**Relays — 11 total, only 5 on the plate:**

| Relay | Function | Location |
|---|---|---|
| K1–K4 | Pop-up H-bridges | **Plate** |
| K11 | Constant-bus master | **Plate** |
| K5–K8 | Window H-bridges | Sill node |
| K9 | Start relay | Inner fender |
| K10 | A/C clutch | Engine bay, factory circuit |

**Interfaces:** 2 lugs · 14 leg receptacles · DP-DIAG · DP-KEY · DP-ICU · DP-DCU.

## 4 · Pin schedule — power, ground, comms

| Pin | Name | Circuit | AWG | Color | To |
|---|---|---|---|---|---|
| STUD | +12V BATT | Main supply, 150 A max | 4 | RED | DP-BAT ← Class-T |
| 25 | GND | Device ground + flyback return, every inductive load | 10 | BLK | DP-GND, ≤6 in |
| 7 | +12V SW | Wake. Diode-OR: ACC, RUN, hazard, door pin, **horn**, O22 | 16 | BLU | Panel diode network |
| 15 | +5V OUT | Ladder + sender reference, 500 mA | 16 | PNK | Split → L1-S, L2-S, L3-S, L4-S |
| 23 | CAN1H | Laptop / config | 16 tw | YEL | DP-DIAG |
| 36 | CAN1L | Laptop / config | 16 tw | GRN | DP-DIAG |
| 24 | CAN2H | Keypad, DCU, ICU, future LS ECU | 16 tw | YEL/BLK | L3-S · L1-S · DP-KEY · DP-ICU · DP-DCU |
| 37 | CAN2L | Peripheral bus | 16 tw | GRN/BLK | same |

## 5 · Pin schedule — 25 A outputs (12 AWG)

Estimates only. Never set a soft fuse from these — see `LOADS.md`.

| Pin | Ch | Circuit | Est. A | Color | To |
|---|---|---|---|---|---|
| 38 | O1 ⚡ | Motor bus — K1–K4 on the plate, K5–K8 at the sill | 8–12 run, 40+ transient | RED/WHT | Relay bank + L4-P 3 |
| 39 | O2 | Headlight LOW | LED | RED/BLK | L2-P1 1 |
| 26 | O3 | Headlight HIGH | LED | RED/BRN | L2-P1 2 |
| 13 | O4 | Rear defog grid | 10–13 | RED/GRN | L4-P 1 |
| 12 | O5 | Fuel pump | 1–2 now / 8–12 Aeromotive | RED/YEL | L4-P 2 |
| 2 | O12 | Ignition / coil feed | 4–6 | RED/BLU | L1-P 1 |
| 1 | O13 | RESERVED — LS ECU + injectors | ~18 | RED/ORN | L1-P 2, capped |
| 14 | O14 | RESERVED — LS cooling fan(s) | ~25 | RED/GRY | L1-P 3, capped |
| 27 | O15 | Comfort bus — **DCU switches downstream** | 12–16 | RED/VIO | L3-P 2 + DCU tap |
| 28 | O16 ⚡ | Blower motor feed | 12–15, 25 inrush | RED/PNK | L3-P 1 |

## 6 · Pin schedule — 15 A outputs (14 AWG)

| Pin | Ch | Circuit | Est. A | Color | To |
|---|---|---|---|---|---|
| 11 | O6 | Tail / park / marker / plate — PARK and HEAD | 3.0 LED | ORN/BRN | Split L2-M 7, L4-M 1 |
| 10 | O7 | Brake lamps | 0.6 LED | ORN/GRN | L4-M 2 |
| 9 | O8 ⚙ | Wiper LOW — braking channel | 3–5 run, 12–20 stall | ORN/BLU | L2-M 1 |
| 5 | O9 | Wiper HIGH | 5–6 run, 12–20 stall | ORN/WHT | L2-M 2 |
| 4 | O10 | Accessory bus — USB, head unit, **DCU + ICU logic** | `[Q-038]` | ORN/YEL | L3-M 1 |
| 3 | O11 | Horn | 4–8 | ORN/BLK | L2-M 3 |

## 7 · Pin schedule — 7 A shared pins

| Pin | Ch | Mode | Circuit | AWG | Color | To |
|---|---|---|---|---|---|---|
| 6 | O17 | OUT | Turn LEFT — flashed natively | 16 | VIO/GRN | Split L2-M 5, L4-M 5 |
| 33 | O18 | OUT | Turn RIGHT | 16 | VIO/YEL | Split L2-M 6, L4-M 6 |
| 20 | O19 | OUT | Reverse lamps | 16 | VIO/BLK | L4-M 7 |
| 34 | O20 | PWM | Interior + details bus, and the ICU dimming reference | 16 | VIO/WHT | L4-M 8, L3-S, DP-ICU 5 |
| 21 | O21 | OUT | Start relay coil → K9 at the fender | 16 | VIO/RED | L1-S 1 |
| 8 | O22 | OUT | Keep-alive latch → diode → pin 7; drives K11 | 16 | VIO/BLU | Panel diode network |
| 35 | A15 | IN | Headlight ladder — OFF/PARK/HEAD. **Also commands pop-up raise** | 16 | GRY/WHT | L3-S 2 |
| 22 | A16 | IN | Key ladder — OFF/ACC/RUN/START | 16 | GRY/RED | L3-S 1 |

## 8 · Pin schedule — dedicated inputs A1–A8 (16 AWG)

0–5 V, 10-bit. All switches to ground with the internal 10 kΩ pull-up.
Ladder values in `LADDERS.md`.

| Pin | In | Signal | Type | Color | To |
|---|---|---|---|---|---|
| 29 | A1 | Turn stalk — L / off / R | 3-step ladder | GRY/GRN | L3-S 3 |
| 16 | A2 | Wiper stalk — off/INT/LO/HI/WASH | 5-step ladder | GRY/BLU | L3-S 4 |
| 30 | A3 | Brake pedal switch | switch-to-gnd | GRY/ORN | L3-S 5 |
| 17 | A4 | Pop-up LEFT position | 3-step ladder | GRY/BLK | L2-S 1 |
| 31 | A5 | Pop-up RIGHT position | 3-step ladder | GRY/BRN | L2-S 2 |
| 18 | A6 | Door pins — driver / passenger | 3-step ladder | GRY/VIO | L4-S 2 |
| 32 | A7 | Fuel level sender | resistive | GRY/YEL | L4-S 1 |
| 19 | A8 | Hazard switch — also diodes to pin 7 | switch-to-gnd | GRY/PNK | L3-S 6 |

**All 39 cavities allocated.** 8 power/comms + 10 × 25 A + 6 × 15 A + 8 shared
+ 7 dedicated = 39.

**Inhibitor switch** (crank interlock + reverse) is laddered onto one of the
shared-pin inputs on L1-S per D-071.

## 9 · Connectors — summary

Full detail in `legs/CONNECTORS.md` and `legs/PIN-MAP.md`.

**Everything is Deutsch DT (size 16) or DTP (size 12). No AMPSEAL anywhere** —
two contact sizes, two crimp dies, one supplier.

| Leg | Connectors |
|---|---|
| L1 Engine | L1-P (DTP-4), L1-S (DT-12 ×2) |
| L2 Front | L2-P1, L2-P2 (DTP-4 ×2), L2-M (DT-8), L2-S (DT-6) |
| L3 Dash | L3-P (DTP-2), L3-M (DT-2), L3-S1/S2 (DT-12 ×2), L3-S3 (DT-8) |
| L4 Rear | L4-P (DTP-4), L4-M (DT-12), L4-S (DT-8) |

**14 leg connectors.** Plus at the dash post: DP-BAT, DP-GND, DP-PMU, DP-DIAG,
DP-KEY, **DP-ICU**, **DP-DCU**. Plus D1/D2 at the sill.

## 10 · Modules — DCU and ICU

Full detail in `DCU-CLUSTER.md`.

| Node | Owns |
|---|---|
| **ICU** | Cluster display **and** tach, water temp, oil pressure, oil temp, VSS, alternator sense |
| **DCU** | Climate, HVAC servos, comfort bus switching |

**Rule:** a gauge's sender wires into the box that draws the gauge. If CAN2 fails,
the ICU still shows every critical gauge from its own inputs.

**Rule:** if the PMU measures it, the ICU reads it from CAN — fuel level, battery
voltage, key state. Never duplicated.

**Sequencing rule (D-081):** the car drives fully on the PMU with dumb switches,
the factory harness comes out, and the build completes — *then* the modules join.

## 11 · Connector geometry — CONFIRMED

From the CAD and the pinout device view.

```
  1  2  3  4  5  6  7  8  9 10 11 12 13     ← row 1
 14 15 16 17 18 19 20 21 22 23 24 25 26     ← row 2
 27 28 29 30 31 32 33 34 35 36 37 38 39     ← row 3
```

Numbered left→right, top→bottom, **looking at the device**.

**Cavity sizes are not uniform.** Each row is **2 large · 9 small · 2 large**.

| Size | Pins |
|---|---|
| **Large (2.8 mm)** | 1, 2, 12, 13, 14, 15, 25, 26, 27, 28, 38, 39 |
| **Small (1.5 mm)** | all other 27 |

The twelve large cavities land exactly on the ten 25 A outputs, GND, and +5 V.
**Every 15 A and 7 A output sits in a 1.5 mm cavity** capped at 13–17 AWG — 14 AWG
is the heaviest wire that can go on O6–O11, with no headroom above it.

**Enclosure:** 131 × 112.1 × 32.5 mm. Mounting 3 × Ø6.5 mm. Connector face on the
short edge, +12 V stud opposite. Allow clearance for the connector lever.

## 12 · Cross-reference

| Need | File |
|---|---|
| Why a decision was made | `DECISIONS.md` |
| What's undecided | `OPEN.md` |
| What only Camden can do | `TASKS-CAMDEN.md` |
| Current draw, signal types | `LOADS.md` |
| Resistor values | `LADDERS.md` |
| Wake network, H-bridges, grounds | `SCHEMATICS.md` |
| Connector cavity assignments | `legs/PIN-MAP.md` |
| Connector part numbers | `legs/CONNECTORS.md` |
| Leg contents and boundaries | `legs/engine.md`, `front-chassis.md`, `dash.md`, `rear-cabin.md` |
| Sill relays and door connectors | `legs/sill-node.md` |
| DCU / ICU | `DCU-CLUSTER.md` |
| Battery and backbone | `BATTERY-INSTALL.md` |
| Parts and money | `BOM.md` |
| Build sequence | `CHECKLIST.md` |
| Factory wiring | `../../01-REFERENCE/factory-circuits/` |

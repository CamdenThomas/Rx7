# PMU CONFIGURATION — logic definitions

*Rev 2026-08-31 · owns: every channel's name, decode table, trigger expression, interlock, timer and wake source. Soft-fuse values are [`CHANNEL-SCHEDULE.md`](CHANNEL-SCHEDULE.md)'s.*

Phase 2A. Enter this rather than working it out at the bench. **Everything
here is enterable without a single amp figure** (D-166) — every soft-fuse value
exists — measured, or at its channel cap until telemetry re-measures it
(D-165 → amended by D-175).

Channel names match [`SPEC.md`](SPEC.md) exactly. The diagnostics page, the simulator and
the migration log all use the same strings, so a mismatch here shows up as a
wrong label on the cluster.

## Contents

1. Analog inputs — decode tables · 2. Output logic · 3. Interlocks ·
4. Wake and shutdown · 5. CAN · 6. Entry order · 7. Commissioning order ·
8. Save discipline

---

## 1 · Analog inputs — decode tables

Ladder resistor values are in [`LADDERS.md`](LADDERS.md). Enter as **lookup tables with
windows**, not thresholds. A reading between windows must report FAULT, not
snap to the nearest state (D-053).

| Input | Pin | States → ADC centre | Window ± | Fault |
|---|---|---|---|---|
| `A1_TURN` | 29 | LEFT 156 · RIGHT 512 · OFF 843 | 55 | <50 or >990 |
| `A2_WIPER` | 16 | WASH 156 · HIGH 327 · LOW 512 · INT 658 · OFF 843 | 45 | <50 or >990 |
| `A3_BRAKE` | 30 | PRESSED 327 · RELEASED 1023 | 47 | <50 |
| `A4_POPUP_L` | 17 | TRANSIT+PN 201 · TRANSIT 245 · CRANK_OK 500 · IDLE 843 | 20 | <50 short, >990 open |
| `A5_POPUP_R` | 31 | TRANSIT+R 201 · TRANSIT 245 · REVERSE 500 · IDLE 843 | 20 | same |
| `A6_DOOR` | 18 | BOTH 406 · PASS 461 · DRV 785 · CLOSED 1023 | **27** | <50 |
| `A7_FUEL` | 32 | FULL 58 · MID 247 · EMPTY 457 — 3-point lookup, interpolated (D-197) | — | <25 short, >900 open |
| `A8_HAZ_HORN` | 19 | HAZ+HORN 259 · HAZARD 327 · HORN 558 · RELEASED 1023 | 30 | <50 |
| `A15_HEADLIGHT` | 35 | OFF 93 · PARK 604 · HEAD+LO 1201 · HEAD+HI 1666 · PASS ≥1750 (superstate) | 75 | 0 = disconnected |
| `A16_KEY` | 22 | OFF ~100 · ACC 571 · RUN 1210 · START 1743 | 200 | 0 = disconnected |

**A6 is the tightest ladder in the car** — 55 counts between BOTH and PASS, so
the window is ±27. If it proves marginal in the car, drop the "both open"
state; nothing in the config distinguishes it from "passenger open". The
luggage-compartment switch is planned as a fourth state on this node
(`A-012`) — re-run the ladder math before adding it.

**A15/A16 are 12 V side, 12-bit,** with a **100 kΩ bias from +5 V** (D-167)
so OFF reads ~100 counts and a disconnected wire reads 0.

**A16 is not a simple ladder.** ACC stays live in RUN, and both stay live in
START, so the node sums (D-055). Closed off FSM sheet F (`T-023` → D-178):
either crank behaviour decodes (START centre 1673–1743 — set the window from
the Phase 6 in-car read). **A4/A5 are D-187's**: the YG transit
contact (closed in transit or blocked) plus one inhibitor contact — P/N on
A4, R on A5 — over a 47 kΩ baseline so a true open still reads as a fault. **A15 five-state values are
D-184's**, from [`LADDERS.md`](LADDERS.md).

Ladder verification against real resistors happens in the car during Phase 6
(D-142), when the switches are genuinely wired.

---

## 2 · Output logic

Written as boolean expressions; `&&` and `||` as you would expect.

### Lighting

| Channel | Expression | Inrush | Retry |
|---|---|---|---|
| `HEAD_LOW` | `A15 == HEAD_LO` | 3× for 200 ms | 3, 5 s |
| `HEAD_HIGH` | `A15 == HEAD_HI \|\| A15 == PASS` (Q-065 → D-184) | 3× for 200 ms | 3, 5 s |
| `TAIL_PARK` | `A15 >= PARK`; during PASS hold the prior state (D-184) | **10× for 100 ms** | 3, 5 s |
| `BRAKE` | `A3 == PRESSED` | 10× for 100 ms | 3, 5 s |
| `TURN_L` | `(A1 == LEFT \|\| hazard) && flasher_phase` | 10× for 100 ms | 3, 5 s |
| `TURN_R` | `(A1 == RIGHT \|\| hazard) && flasher_phase` | 10× for 100 ms | 3, 5 s |
| `REVERSE` | `A5 == REVERSE && A16 >= RUN` — the inhibitor R contact (D-187) | 10× for 100 ms | 3, 5 s |
| `INTERIOR` | `(A6 != CLOSED \|\| keypad_override)` — PWM, theatre fade | 10× for 100 ms | 3, 5 s |

> **The inrush windows are the whole reason this section exists.** Cold filament
> pulls 8–12× steady for a few milliseconds. Without a time characteristic,
> every one of these trips on the first flash (D-120).

**Flasher:** 1.5 Hz, 50 % duty, generated in the PMU. `hazard` in the turn
expressions means `A8 == HAZARD || A8 == HAZ_HORN` (D-190). **No flasher unit exists
in the car** (D-013). Hazard drives both channels and overrides the stalk.

### Motors

| Channel | Expression | Notes |
|---|---|---|
| `MOTOR_BUS` | `popup_moving` (add `\|\| window_moving` when windows are fitted) | ⚡ flyback. Feeds K1–K2 |
| `WIPE_LOW` | `A2 == LOW \|\| (A2 == INT && int_timer) \|\| A2 == WASH` | ⚙ **braking enabled** |
| `WIPE_HIGH` | `A2 == HIGH` | |
| `BLOWER` | `A16 >= RUN` — the factory switch and resistor pack are in the motor path | ⚡ flyback, **inrush delay 500 ms** |

**Wiper intermittent:** 3 s fixed, timed full cycles. **Wiper park:** handled
mechanically at the motor — the factory park contact self-feeds to the parked
position (`Q-063` → D-182) — unless `V-074` shows O8 braking demands a
park-sense input, which reopens the question. **Never cut power mid-sweep.**

**Pop-ups (D-186):** single-direction cam-crank motors — every half-cycle
flips that side's state, so raise and lower are the same electrical act.
`A15` reaching HEAD runs both sides a half-cycle; leaving HEAD runs both
again; a wink runs one side. Energise K1/K2 until that side's YG transit
contact opens; **4 s still-closed = obstruction** — stop and fault. Track
commanded position in the keep-alive state; on a cold boot with unknown
position the first command self-corrects.

### Everything else

| Channel | Expression | Notes |
|---|---|---|
| `DEFOG` | `keypad_defog && A16 >= RUN` — **15 min auto-off** | Grid draws more cold |
| `FUEL_PUMP` | **Interim (D-183):** `A16 >= RUN`, 3 s prime, inertia-switch cut, no rpm term. **Final:** `(A16 == START) \|\| (A16 == RUN && rpm > 300)` once 0x200 is on the bus | `rpm` arrives on CAN 0x200 from the ICU (`Q-064` → D-183) |
| `IGNITION` | `A16 >= RUN` | |
| `ACCESSORY` | `A16 >= ACC` | USB-C, head unit, ICU + DCU logic, keypad |
| `HORN` | `A8 == HORN \|\| A8 == HAZ_HORN` (`Q-071` → D-190) — asleep, the plate inverter wakes the PMU and the same read fires | |
| `COMFORT` | `A16 >= RUN` | DCU switches downstream |
| `START_RLY` | **Interim (D-183):** `A16 == START && inhibitor_PN`. **Final:** adds `&& rpm < 300` at the ICU | `inhibitor_PN` = `A4 == CRANK_OK` (D-187) |
| `KEEP_ALIVE` | self-hold, releases 30 s after the last input change | Drives K11. `V-075` |
| `LS_ECU`, `LS_FAN` | **disabled** | Capped, reserved |

---

## 3 · Interlocks — enter these before any output is enabled

| Interlock | Rule |
|---|---|
| **Crank** | `START_RLY` only if inhibitor P or N; the `rpm < 300` term joins at the ICU (D-183) |
| **Fuel pump** | Cut if rpm = 0 for > 2 s after prime. Cut on inertia switch |
| **Pop-up** | One half-cycle at a time per side; stop on the 4 s YG timeout — obstruction (D-186) |
| **Window** (when fitted) | Never up and down on the same window. Never both windows plus both pop-ups |
| **Motor bus** | Refuse new motor commands above 20 A total on O1 |
| **Undervoltage** | Warn below 12.0 V. Shed `COMFORT` below 11.5 V |
| **Overvoltage** | Warn above 15.0 V |

---

## 4 · Wake and shutdown

Six diode-OR inputs to pin 7 (D-056, D-072): `ACC` · `RUN` · `hazard switch`
· `door pin` · `horn switch` · `O22 latch`, plus a **10 kΩ bleed to ground**
so the node cannot float. Drawn in [`SCHEMATICS.md`](SCHEMATICS.md) §1.

**Shutdown:** 30 s after the last input change with the key off, `O22`
releases and the PMU sleeps. `K11` drops the constant bus on a long park.

---

## 5 · CAN

**CAN1** — laptop, 1 Mbps fixed, **no internal termination.** Fit 120 Ω at
both ends or the client will not see the device.

**CAN2** — 500 kbps (D-086), software termination enabled at the PMU end,
physical 120 Ω at the engine-bay drop (D-079).

**Export the PMU's own message structure before writing any firmware against
it** — `V-065`. `can_map.h` messages 0x100–0x130 are intent until reconciled.

---

## 6 · Entry order

Everything above is enterable **without a single amp figure** (D-166):

1. Name all 39 channels to match [`SPEC.md`](SPEC.md)
2. Enter the ten decode tables
3. Enter the output expressions
4. Enter the interlocks
5. Enter the wake sources and shutdown timer
6. Configure the flasher, wiper timer, pop-up logic
7. Enable data logging
8. Save as `RevA-01`, log it in [`../04-BUILD/LOGS.md`](../04-BUILD/LOGS.md)

**Then, and only then:** enter the soft-fuse values from [`CHANNEL-SCHEDULE.md`](CHANNEL-SCHEDULE.md) —
all present since D-175 — and enable the LIVE outputs ([`CHECKLIST.md`](../04-BUILD/CHECKLIST.md) 2.22).

Fuse values are measured or channel caps (D-175); telemetry tightens each
channel per D-164 in the first week after migration.

---

## 7 · Commissioning order — in the car (D-194), in this sequence

There is no bench phase — the PMU is configured mounted in the car, powered
from the new backbone with every output disabled, laptop over CAN1 through
DP-DIAG. A 5 A fuse guards the first power-up (D-145). Steps 4–14 each run
against the first migrated circuits as they cut over, one per sitting.

1. CAN1 up, PMU visible in the client, **120 Ω both ends**
2. `V-065` — export the CAN stream definition, reconcile `can_map.h`
3. Name every channel to match this document
4. One output + bulb: switching and live current
5. Deliberate short with the limit at 2 A: soft fuse trips, retry behaviour
6. **Inrush window tuning** — this is the step people skip
7. Enter the decode tables; prove one ladder against a pot
8. Turn flash, hazard override
9. Wiper: LOW, HIGH, INT timer, park, braking
10. Headlight ladder → O2/O6, pop-up raise logic
11. Keep-alive latch and shutdown timer
12. Crank interlock, fuel pump prime and cut
13. All interlocks from §3
14. Full dry run, every function, real switches

---

## 8 · Save discipline

Version after every working step — `RevA-01`, `-02`. Never overwrite. Log
each in [`../04-BUILD/LOGS.md`](../04-BUILD/LOGS.md).

**The one time you need to roll back is the one time you won't have kept it.**

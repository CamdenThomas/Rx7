# PMU CONFIGURATION — logic definitions

*Rev 2026-08-30 · owns: every channel's name, decode table, trigger expression, interlock, timer and wake source. Soft-fuse values are [`CHANNEL-SCHEDULE.md`](CHANNEL-SCHEDULE.md)'s.*

Phase 2A. Enter this rather than working it out at the bench. **Everything
here is enterable without a single amp figure** (D-166) — soft-fuse limits are
added per channel as each measurement arrives, and an output with no measured
figure stays **disabled** (D-165).

Channel names match [`SPEC.md`](SPEC.md) exactly. The diagnostics page, the simulator and
the migration log all use the same strings, so a mismatch here shows up as a
wrong label on the cluster.

## Contents

1. Analog inputs — decode tables · 2. Output logic · 3. Interlocks ·
4. Wake and shutdown · 5. CAN · 6. Entry order · 7. Bench order ·
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
| `A4_POPUP_L` | 17 | DOWN 254 · UP 512 · MID 843 | 45 | <50, or ~193 = both limits closed |
| `A5_POPUP_R` | 31 | same as A4 | 45 | same |
| `A6_DOOR` | 18 | BOTH 406 · PASS 461 · DRV 785 · CLOSED 1023 | **27** | <50 |
| `A7_FUEL` | 32 | resistive — divider table after `V-037` | — | open / short |
| `A8_HAZARD` | 19 | PRESSED 327 · RELEASED 1023 | 47 | <50 |
| `A15_HEADLIGHT` | 35 | OFF ~100 · PARK 1229 · HEAD 2457 | 200 | 0 = disconnected |
| `A16_KEY` | 22 | OFF ~100 · ACC 571 · RUN 1210 · START 1743 | 200 | 0 = disconnected |

**A6 is the tightest ladder in the car** — 55 counts between BOTH and PASS, so
the window is ±27. If it proves marginal in the car, drop the "both open"
state; nothing in the config distinguishes it from "passenger open". The
luggage-compartment switch is planned as a fourth state on this node
(`A-012`) — re-run the ladder math before adding it.

**A15/A16 are 12 V side, 12-bit,** with a **100 kΩ bias from +5 V** (D-167)
so OFF reads ~100 counts and a disconnected wire reads 0.

**A16 is not a simple ladder.** ACC stays live in RUN, and both stay live in
START, so the node sums (D-055). Verify against `T-023` before trusting the
centres. **A4/A5 are provisional** until `T-011` identifies the motor's limit
contacts. **A15 gains states** if dimmer and passing move onto it (`Q-065`).

Ladder verification against real resistors happens in the car during Phase 6
(D-142), when the switches are genuinely wired.

---

## 2 · Output logic

Written as boolean expressions; `&&` and `||` as you would expect.

### Lighting

| Channel | Expression | Inrush | Retry |
|---|---|---|---|
| `HEAD_LOW` | `A15 == HEAD` | 3× for 200 ms | 3, 5 s |
| `HEAD_HIGH` | `(A15 == HEAD && dimmer == HIGH) \|\| passing` — dimmer/pass input is `Q-065` | 3× for 200 ms | 3, 5 s |
| `TAIL_PARK` | `A15 >= PARK` | **10× for 100 ms** | 3, 5 s |
| `BRAKE` | `A3 == PRESSED` | 10× for 100 ms | 3, 5 s |
| `TURN_L` | `(A1 == LEFT \|\| hazard) && flasher_phase` | 10× for 100 ms | 3, 5 s |
| `TURN_R` | `(A1 == RIGHT \|\| hazard) && flasher_phase` | 10× for 100 ms | 3, 5 s |
| `REVERSE` | `inhibitor == R && A16 >= RUN` — inhibitor input is `Q-063` | 10× for 100 ms | 3, 5 s |
| `INTERIOR` | `(A6 != CLOSED \|\| keypad_override)` — PWM, theatre fade | 10× for 100 ms | 3, 5 s |

> **The inrush windows are the whole reason this section exists.** Cold filament
> pulls 8–12× steady for a few milliseconds. Without a time characteristic,
> every one of these trips on the first flash (D-120).

**Flasher:** 1.5 Hz, 50 % duty, generated in the PMU. **No flasher unit exists
in the car** (D-013). Hazard drives both channels and overrides the stalk.

### Motors

| Channel | Expression | Notes |
|---|---|---|
| `MOTOR_BUS` | `popup_moving` (add `\|\| window_moving` when windows are fitted) | ⚡ flyback. Feeds K1–K4 |
| `WIPE_LOW` | `A2 == LOW \|\| (A2 == INT && int_timer) \|\| A2 == WASH` | ⚙ **braking enabled** |
| `WIPE_HIGH` | `A2 == HIGH` | |
| `BLOWER` | `A16 >= RUN` — the factory switch and resistor pack are in the motor path | ⚡ flyback, **inrush delay 500 ms** |

**Wiper intermittent:** 3 s fixed. Pulse `WIPE_LOW` for one cycle, wait for
park sense, repeat. **Wiper park:** on release, hold `WIPE_LOW` until the park
switch closes, then apply O8 braking. **Never cut power mid-sweep.** The park
sense input is `Q-063`.

**Pop-ups:** `A15` reaching HEAD raises both; leaving HEAD lowers both. Wink
switches momentarily override one side and return it to the ladder state.
**Never energise raise and lower on the same side.**

### Everything else

| Channel | Expression | Notes |
|---|---|---|
| `DEFOG` | `keypad_defog && A16 >= RUN` — **15 min auto-off** | Grid draws more cold |
| `FUEL_PUMP` | `(A16 == START) \|\| (A16 == RUN && rpm > 300)` — prime 3 s on RUN | `rpm` arrives on CAN 0x200 from the ICU; the interim rule before the ICU exists is `Q-064`. Inertia switch cuts it |
| `IGNITION` | `A16 >= RUN` | |
| `ACCESSORY` | `A16 >= ACC` | USB-C, head unit, ICU + DCU logic, keypad |
| `HORN` | `horn_switch` — the switch's PMU input is `Q-063` | |
| `COMFORT` | `A16 >= RUN` | DCU switches downstream |
| `START_RLY` | `A16 == START && inhibitor_PN && rpm < 300` | Inhibitor input `Q-063`; rpm term `Q-064` |
| `KEEP_ALIVE` | self-hold, releases 30 s after the last input change | Drives K11. `V-075` |
| `LS_ECU`, `LS_FAN` | **disabled** | Capped, reserved |

---

## 3 · Interlocks — enter these before any output is enabled

| Interlock | Rule |
|---|---|
| **Crank** | `START_RLY` only if inhibitor P or N **and** rpm < 300 |
| **Fuel pump** | Cut if rpm = 0 for > 2 s after prime. Cut on inertia switch |
| **Pop-up** | Never raise and lower the same side |
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
8. Save as `RevA-01`, log it in [`../05-BUILD/LOGS.md`](../05-BUILD/LOGS.md)

**Then, and only then:** enter soft-fuse limits from [`CHANNEL-SCHEDULE.md`](CHANNEL-SCHEDULE.md) as
each measurement arrives, and enable that output ([`CHECKLIST.md`](../05-BUILD/CHECKLIST.md) 2.22).

An output with no measured figure stays **disabled**. That is not a
limitation — it is the design working.

---

## 7 · Bench order — do it in this sequence

PMU on a desk, laptop over CAN1, flying leads into a **spare** housing
(never the real one), a 5 A fuse in the feed for the first power-up (D-145),
one bulb, a few switches. No bench PSU, no plywood mule (D-141, D-144).

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
each in [`../05-BUILD/LOGS.md`](../05-BUILD/LOGS.md).

**The one time you need to roll back is the one time you won't have kept it.**

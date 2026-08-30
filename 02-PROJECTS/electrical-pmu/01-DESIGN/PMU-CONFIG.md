# PMU CONFIGURATION PLAN

*Phase 2A. Enter this rather than working it out at the bench.*

Every channel's name, trigger logic, current limit and behaviour. Names match
`SPEC.md` exactly so the config, the schedule and the labels all agree.

**Nothing here is a final soft-fuse value.** Limits below are *starting points*
for the bench; real values come from measurement at migration (Checklist 6,
step 5).

---

## 1 · Inputs — analog, with decode tables

Ladder resistor values are in `LADDERS.md`. Enter these as **lookup tables**, not
thresholds, so a reading between states reads as a fault rather than snapping to
the nearest valid position.

### A1 · Turn stalk

| ADC | State | Window |
|---|---|---|
| 156 | LEFT | 100–210 |
| 512 | RIGHT | 450–570 |
| 843 | OFF | 790–900 |
| <50 or >990 | **FAULT** | short / open |

### A2 · Wiper stalk

| ADC | State | Window |
|---|---|---|
| 156 | WASH | 110–200 |
| 327 | HIGH | 280–375 |
| 512 | LOW | 465–560 |
| 658 | INT | 610–705 |
| 843 | OFF | 800–890 |
| <50 or >990 | **FAULT** | |

### A3 · Brake pedal · A8 · Hazard

| ADC | State |
|---|---|
| 327 | PRESSED |
| 1023 | RELEASED |
| <50 | **FAULT — shorted** |

The 4.7 kΩ instead of a dead short is what makes a chafe distinguishable from a
press. On the brake pedal that matters.

### A4 / A5 · Pop-up position

**Provisional** — values firm up after T-011 continuity testing.

| ADC | State |
|---|---|
| 254 | DOWN limit |
| 512 | UP limit |
| 843 | mid-travel |
| ~193 | both closed — **FAULT** |

### A6 · Door pins

| ADC | State | Note |
|---|---|---|
| 406 | both open | **55-count gap to the next state — the tightest ladder in the car** |
| 461 | passenger only | |
| 785 | driver only | |
| 1023 | both closed | |

If this drifts on the bench, drop the "both open" state. Nothing in the config
needs to distinguish it from "passenger open."

### A15 · Headlight switch · 12 V side, 12-bit

| ADC | State |
|---|---|
| 0 | OFF *(also reads as open circuit — see note)* |
| 1229 | PARK |
| 2457 | HEAD |

**Add a 100 kΩ bias from +5 V** to separate OFF (~100 counts) from a
disconnected wire (0). Cheap, recommended.

### A16 · Key position · 12 V side, 12-bit

**Not a simple ladder.** ACC stays live in RUN, and both stay live in START, so
the node sees the sum. Verify against T-023 before trusting these.

| ADC | State |
|---|---|
| 0 | OFF |
| 571 | ACC |
| 1210 | RUN |
| 1743 | START |

---

## 2 · Outputs — trigger logic and limits

### Lighting

| Ch | Name | Trigger | Limit | Inrush | Retry |
|---|---|---|---|---|---|
| O2 | `HEAD_LOW` | A15 = HEAD | 15 A | **3× for 200 ms** | 3, 5 s |
| O3 | `HEAD_HIGH` | A15 = HEAD **and** dimmer HIGH, **or** PASS | 15 A | 3× for 200 ms | 3, 5 s |
| O6 | `TAIL_PARK` | A15 = PARK **or** HEAD | 8 A | **10× for 100 ms** | 3, 5 s |
| O7 | `BRAKE` | A3 = PRESSED | 8 A | 10× for 100 ms | 3, 5 s |
| O17 | `TURN_L` | A1 = LEFT **or** hazard | 6 A | **10× for 100 ms** | 3, 5 s |
| O18 | `TURN_R` | A1 = RIGHT **or** hazard | 6 A | 10× for 100 ms | 3, 5 s |
| O19 | `REVERSE` | inhibitor = R | 6 A | 10× for 100 ms | 3, 5 s |
| O20 | `INTERIOR` | door pin **or** override, PWM | 5 A | 10× for 100 ms | 3, 5 s |

> **The inrush windows are the whole reason this section exists.** Cold filament
> pulls 8–12× steady for a few milliseconds. Without a time characteristic, every
> one of these trips on the first flash (D-120).

**Turn flash:** 1.5 Hz, 50% duty, generated in the PMU. No flasher unit anywhere.
Hazard drives both channels simultaneously and **overrides** the stalk.

### Motors

| Ch | Name | Trigger | Limit | Notes |
|---|---|---|---|---|
| O1 | `MOTOR_BUS` | pop-up or window command active | 25 A | ⚡ flyback. Feeds K1–K8 |
| O8 | `WIPE_LOW` | A2 = LOW, INT timer, or WASH | 15 A slow | ⚙ **braking enabled** |
| O9 | `WIPE_HIGH` | A2 = HIGH | 15 A slow | |
| O16 | `BLOWER` | blower switch ≠ OFF | 20 A | ⚡ flyback, **inrush delay 500 ms** |

**Wiper intermittent:** 3 s fixed delay. On INT, pulse O8 for one wipe cycle,
wait for park sense, repeat.

**Wiper park:** on release, hold O8 until the park switch closes, then apply
braking. Never cut power mid-sweep.

**Pop-up logic:** A15 reaching HEAD raises both. Leaving HEAD lowers both. Wink
switches momentarily override one side and return it to the ladder state.
**Never energise raise and lower on the same side.** Never run both pop-ups and
both windows simultaneously.

### Everything else

| Ch | Name | Trigger | Limit | Notes |
|---|---|---|---|---|
| O4 | `DEFOG` | keypad, **15-minute auto-off** | 16 A | Grid draws more cold |
| O5 | `FUEL_PUMP` | key RUN, prime 3 s, then RPM > 300 | 5 A | Inertia switch cuts it |
| O10 | `ACCESSORY` | key ACC or RUN | 12 A | USB, head unit, DCU/ICU |
| O11 | `HORN` | horn switch | 10 A | |
| O12 | `IGNITION` | key RUN or START | 8 A | |
| O15 | `COMFORT` | key RUN | 20 A | DCU switches downstream |
| O21 | `START_RLY` | key START **and** inhibitor P/N **and** RPM < 300 | 1 A | |
| O22 | `KEEP_ALIVE` | self-hold, 30 s after last activity | 1 A | Drives K11 |
| O13/O14 | `LS_ECU` / `LS_FAN` | **disabled** | — | Capped, reserved |

---

## 3 · Interlocks — enter these before touching anything else

| Interlock | Rule |
|---|---|
| **Crank** | O21 only if inhibitor = P or N **and** RPM < 300 |
| **Fuel pump** | Cut if RPM = 0 for >2 s after prime. Cut on inertia switch |
| **Pop-up** | Never raise and lower the same side. Never both sides plus both windows |
| **Window** | Never up and down on the same window |
| **Motor bus** | Total O1 draw ceiling — stop new motor commands above 20 A |
| **Undervoltage** | Warn below 12.0 V, shed comfort below 11.5 V |
| **Overvoltage** | Warn above 15.0 V |

## 4 · Wake and shutdown

| Wake source | Via |
|---|---|
| Key ACC / RUN | Diode to pin 7 |
| Hazard switch | Diode to pin 7 |
| Door pin | Diode to pin 7 |
| **Horn switch** | Diode to pin 7 (D-072) |
| O22 self-hold | Diode to pin 7 |

**Shutdown:** 30 s after the last input change with the key off, O22 releases and
the PMU sleeps. K11 drops the constant bus on a long park.

## 5 · Bench order — do it in this sequence

1. CAN1 up, PMU visible in the client, **120 Ω both ends**
2. Name every channel to match this document
3. One output + bulb: switching and live current
4. Deliberate short: soft fuse trips, retry behaviour
5. **Inrush window tuning** — this is the step people skip
6. One ladder, verify against `LADDERS.md`, write the decode table
7. Remaining five ladders
8. Turn flash, hazard override
9. Wiper: LOW, HIGH, INT timer, park, braking
10. Headlight ladder → O2/O6, pop-up raise logic
11. Keep-alive latch and shutdown timer
12. Crank interlock
13. Fuel pump prime and RPM cut
14. All interlocks from §3
15. Full dry run, every function, real switches

## 6 · Save discipline

Version after every working step — `RevA-01`, `-02`. Never overwrite. Log each in
`../05-BUILD/LOGS.md`.

**The one time you need to roll back is the one time you won't have kept it.**

---

# LOGIC DEFINITIONS — enter these as written

*Rev 2026-08. Soft-fuse values come from `CHANNEL-SCHEDULE.md`; everything
below is independent of the amp numbers and can be entered tonight.*

Naming convention: **channel names match `SPEC.md` exactly.** The diagnostics
page, the simulator and the migration log all use the same strings, so a
mismatch here shows up as a wrong label on the cluster.

---

## 1 · Analog inputs — decode tables

Enter as **lookup tables with windows**, not thresholds. A reading between
windows must report FAULT, not snap to the nearest state (D-053).

| Input | Pin | States → ADC centre | Window ± | Fault |
|---|---|---|---|---|
| `A1_TURN` | 29 | LEFT 156 · RIGHT 512 · OFF 843 | 55 | <50 or >990 |
| `A2_WIPER` | 16 | WASH 156 · HIGH 327 · LOW 512 · INT 658 · OFF 843 | 45 | <50 or >990 |
| `A3_BRAKE` | 30 | PRESSED 327 · RELEASED 1023 | 47 | <50 |
| `A4_POPUP_L` | 17 | DOWN 254 · UP 512 · MID 843 | 45 | <50, or ~193 = both closed |
| `A5_POPUP_R` | 31 | same as A4 | 45 | same |
| `A6_DOOR` | 18 | BOTH 406 · PASS 461 · DRV 785 · CLOSED 1023 | **27** | <50 |
| `A15_HEADLIGHT` | 35 | OFF 0 · PARK 1229 · HEAD 2457 | 200 | see note |
| `A16_KEY` | 22 | OFF 0 · ACC 571 · RUN 1210 · START 1743 | 200 | see note |

**A6 is the tightest ladder in the car** — 55 counts between BOTH and PASS, so
the window is ±27. If it proves marginal on the bench, drop the "both open"
state; nothing in the config distinguishes it from "passenger open".

**A15/A16 are 12 V side, 12-bit.** Add a **100 kΩ bias from +5 V** so OFF reads
~100 counts instead of 0 — otherwise OFF and a disconnected wire are identical.

**A16 is not a simple ladder.** ACC stays live in RUN, and both stay live in
START, so the node sums. Verify against `T-023` before trusting the centres.

---

## 2 · Output logic

Written as boolean expressions. `&&` and `||` as you would expect.

| Channel | Expression |
|---|---|
| `HEAD_LOW` | `A15 == HEAD` |
| `HEAD_HIGH` | `(A15 == HEAD && dimmer == HIGH) \|\| passing` |
| `TAIL_PARK` | `A15 >= PARK` |
| `BRAKE` | `A3 == PRESSED` |
| `TURN_L` | `(A1 == LEFT \|\| hazard) && flasher_phase` |
| `TURN_R` | `(A1 == RIGHT \|\| hazard) && flasher_phase` |
| `REVERSE` | `inhibitor == R && A16 >= RUN` |
| `INTERIOR` | `(A6 != CLOSED \|\| override) — PWM, theatre fade` |
| `WIPE_LOW` | `A2 == LOW \|\| (A2 == INT && int_timer) \|\| A2 == WASH` |
| `WIPE_HIGH` | `A2 == HIGH` |
| `DEFOG` | `keypad_defog && A16 >= RUN` — **15 min auto-off** |
| `FUEL_PUMP` | `(A16 == START) \|\| (A16 == RUN && rpm > 300)` — prime 3 s |
| `IGNITION` | `A16 >= RUN` |
| `ACCESSORY` | `A16 >= ACC` |
| `HORN` | `horn_switch` |
| `COMFORT` | `A16 >= RUN` |
| `START_RLY` | `A16 == START && inhibitor_PN && rpm < 300` |
| `KEEPALIVE` | self-hold, releases 30 s after last input change |
| `MOTOR_BUS` | `popup_moving \|\| window_moving` |

**Flasher:** 1.5 Hz, 50% duty, generated in the PMU. **No flasher unit exists
in the car.** Hazard drives both channels and overrides the stalk.

**Wiper intermittent:** 3 s fixed. Pulse `WIPE_LOW` for one cycle, wait for park
sense, repeat.

**Wiper park:** on release, hold `WIPE_LOW` until the park switch closes, then
apply O8 braking. **Never cut power mid-sweep.**

**Pop-ups:** `A15` reaching HEAD raises both. Leaving HEAD lowers both. Wink
switches momentarily override one side and return it to the ladder state.

---

## 3 · Interlocks — enter these before any output is enabled

| Interlock | Rule |
|---|---|
| **Crank** | `START_RLY` only if inhibitor P or N **and** rpm < 300 |
| **Fuel pump** | Cut if rpm = 0 for > 2 s after prime. Cut on inertia switch |
| **Pop-up** | Never raise and lower the same side. Never both sides plus both windows |
| **Window** | Never up and down on the same window |
| **Motor bus** | Refuse new motor commands above 20 A total on O1 |
| **Undervoltage** | Warn below 12.0 V. Shed `COMFORT` below 11.5 V |
| **Overvoltage** | Warn above 15.0 V |

---

## 4 · Wake network

Six diode-OR inputs to pin 7 (D-072):

`ACC` · `RUN` · `hazard switch` · `door pin` · **`horn switch`** · `O22 latch`

Plus a **10 kΩ bleed to ground** so the node cannot float (D-056).

**Shutdown:** 30 s after the last input change with the key off, `O22` releases
and the PMU sleeps. `K11` drops the constant bus on a long park.

---

## 5 · CAN

**CAN1** — laptop, 1 Mbps fixed, **no internal termination.** Fit 120 Ω at both
ends or the client will not see the device.

**CAN2** — 500 kbps (D-086), software termination enabled at the PMU end,
physical 120 Ω at the engine-bay drop (D-079).

**Export the PMU's own message structure before writing any firmware against
it** — `V-065`. `can_map.h` messages 0x100–0x130 are intent until reconciled.

---

## 6 · Entry order

Everything above is enterable **without a single amp figure**:

1. Name all 39 channels to match `SPEC.md`
2. Enter the eight decode tables
3. Enter the output expressions
4. Enter the interlocks
5. Enter the wake sources and shutdown timer
6. Configure the flasher, wiper timer, pop-up logic
7. Enable data logging
8. Save as `RevA-01`, log it in `LOGS.md`

**Then, and only then:** enter soft-fuse limits from `CHANNEL-SCHEDULE.md` as
each measurement arrives, and enable that output.

An output with no measured figure stays **disabled**. That is not a
limitation — it is the design working.

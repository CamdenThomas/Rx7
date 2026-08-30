# Open Queue — Electrical / PMU

*Rev 2026-08-30 · owns: what is undecided (Q), unconfirmed (V) or assumed (A). Answered items move to [`DECISIONS.md`](DECISIONS.md) and leave this file; the ID stays permanent and is cited as `Q-038 → D-095` from then on. [`ID-REGISTRY.md`](ID-REGISTRY.md) lists every ID ever issued.*

**How to answer:** type under the `ANSWER:` quote, or say it in a session. The
agent records the D-entry and removes the packet here.

## Contents

1. Design packets — the five that gate Checklist 0.23 · 2. Other questions ·
3. Verify — flagged · 4. Verify — easy · 5. Verify — needs the car ·
6. Verify — blocked · 7. Assumptions in force

---

## 1 · Design packets — rule on these at Checklist 0.23

Each is a gap the documents used to present as settled. Four functions have no
pin or output until these are answered, and the wire-and-connector order
([`BOM.md`](../06-PROCUREMENT/BOM.md) §11 item 8) waits on them.

### Q-061 · Spare fuse F13 and the two solenoids
**Ask:** F13 has three claims — DCU climate memory (`V-056`), the radar module
feed (D-039) and the hatch / fuel-door solenoids (`V-033`). Which gets it, and
where do the solenoids get an *output*? They are momentary loads that the
keypad commands (D-031) but no O-channel drives them.
*Update 2026-08:* the factory fuel-door release **exists and its switch is
broken** — it cannot be exercised or measured on the old harness; whether the
hatch release still works is unknown. The keypad replaces the switch either
way (D-031); solenoid draw comes from PMU telemetry or the replacement part's
spec, not the meter session.
**Options:** (a) solenoids on O10 branches with their own fuse, keypad → PMU
logic pulses them; (b) a spare 7 A output — none is free, so this means a
channel swap; (c) solenoids on the DCU's comfort switching, which puts a
convenience function behind the module (D-081 says that is acceptable for
non-driving functions). F13 then goes to whichever of the other two claims
survives `V-056` and `V-061`.
**Recommendation:** (a) — O10 already wakes with ACC and the pulses are short.
**Blocks:** L4-M 3/4 destination, [`MIGRATION-LOG.md`](../05-BUILD/MIGRATION-LOG.md) rows 22–23, `T-032`/`T-033`
part choice.

**ANSWER:**
>
>

### Q-062 · Conductors from the dash to the sill
**Ask:** Three things are wanted at the sill with no conductor allocated: the
O15 comfort feed for mirror heat (F14), mirror motor control from the dash
(count unknown — `V-060`), and a door-pin wake source. L4-P 4 is the only heavy
spare on L4.
**Options:** (a) L4-P 4 becomes the O15 → sill feed and mirror control waits on
the mirrors, using L4-M spares when known; (b) a small dedicated dash → sill
housing added to the sill node; (c) mirror heat off the comfort bus is dropped
and F14 with it.
**Recommendation:** (a) now, revisit when `T-031` picks the mirrors.
**Blocks:** L4 cut list lengths, sill plate layout (Checklist 5.11), F14.

**ANSWER:**
>
>

### Q-063 · Four signals with no PMU pin
**Ask:** All sixteen analog inputs are allocated (D-076). Four signals the
logic in [`PMU-CONFIG.md`](../01-DESIGN/PMU-CONFIG.md) depends on have nowhere to land: the inhibitor
switch (crank interlock + reverse, D-071 — L1-S1 11), wiper park sense
(L2-S 3), the horn switch as an *input* rather than only a wake source
(L3-S1 11), and the washer pump has no *output* (L2-M 4).
**Options:** (a) ladder more states onto existing nodes — inhibitor P/N/R onto
A16's key ladder is not possible (different switch), but horn can share the
wake diode and be read on the +12V SW pin's logic state; park sense can share
the wiper ladder node A4 as an extra state; washer on a K-relay off O9 with a
timed pulse; (b) accept that the PMU is short and put inhibitor and park on
the ICU's spare inputs, published on CAN — which violates D-081 for the crank
interlock; (c) drop O8 braking and park sensing entirely and let the wipers
park mechanically as the factory motor does.
**Recommendation:** (a) for horn and washer; (c) for park unless `V-074` says
braking needs it; inhibitor stays a hard requirement — find it a state on A4 or
A5 by re-running the ladder maths.
**Blocks:** Checklist 2.12, 2.16, L1-S1 11, L2-S 3, L2-M 4, [`MIGRATION-LOG.md`](../05-BUILD/MIGRATION-LOG.md)
row 6.

**ANSWER:**
>
>

### Q-064 · RPM-dependent PMU logic before the ICU exists
**Ask:** `FUEL_PUMP` runs on `rpm > 300` and `START_RLY` cuts on `rpm < 300`,
but the PMU has no tach input; rpm arrives on CAN 0x200 from the ICU, and the
ICU joins a finished car (D-081).
**Options:** (a) interim: fuel pump = RUN with a 3 s prime and an inertia
switch cut, no rpm term; start relay = key START only; rpm terms added when
0x200 is on the bus; (b) feed a conditioned tach pulse to a PMU digital input
now — but none is free (Q-063); (c) keep the rpm terms and accept the pump
does not run until the ICU exists — not acceptable.
**Recommendation:** (a), written into [`PMU-CONFIG.md`](../01-DESIGN/PMU-CONFIG.md) as the interim rule with
the CAN version beside it.
**Blocks:** Checklist 2.16, 2.17.

**ANSWER:**
>
>

### Q-065 · Dimmer and passing on A15
**Ask:** D-051 put dimmer HIGH/LOW and PASS "in software off A15" but A15's
ladder is OFF / PARK / HEAD. The dimmer is a separate column switch. Do its
states join the A15 ladder (five states on a 12 V-side ladder with the D-167
bias) or does it need its own node?
**Options:** (a) five-state ladder on A15 — re-run [`LADDERS.md`](../01-DESIGN/LADDERS.md) maths for the
12 V side; (b) dimmer/pass share a ladder with the wink switches; (c) PASS
becomes a momentary on the keypad — poor ergonomics.
**Recommendation:** (a) if the maths gives ≥ 60 counts between states, else (b).
**Blocks:** Checklist 2.13, `HEAD_HIGH` expression, L3-S1 2.

**ANSWER:**
>
>

---

## 2 · Other questions

### Q-014 · Dash panel envelope
**Ask:** W × H × D behind the dash, plus clearance for the 39-pin lever.
**Blocks:** panel 1:1 drawing, panel parts order, Checklist 0.8, 0.20–0.21, all
of Phase 4. A tape measure — the panel is smaller than originally planned
(five relays on the plate, D-067).

**ANSWER:**
>
>

### Q-028 · CAN wake latency
**Ask:** If horn and wink ever move to CAN wake once the MCU exists, what
wake-to-horn latency is acceptable on a cold boot? Not live yet; recorded so it
isn't rediscovered.

**ANSWER:**
>
>

### Q-060 · Display panel selection **← next hardware decision**
**Ask:** Which 800 × 480 panel? The interface is settled (D-168 — SPI,
dirty-rectangle, RGB332).

| Must have | Why |
|---|---|
| **800–1000 nits minimum** (`V-058`) | A wide panel has more area to wash out. The spec most often omitted from listings — its absence usually means it's low |
| **8-bit colour mode (RGB332)** | Halves SPI traffic. Confirm the controller supports it |
| SPI interface, ILI9488 / ST7796 class | Matches the renderer |
| Optically bonded or AR treated | Not an air gap |
| Backlight PWM input | For O20 illumination tracking |

**ANSWER:**
>
>

### Q-001 · VIN
**Ask:** Record the VIN in `00-CAR/vehicle.md` (`T-049`). Nothing blocks on it;
it is the one field a stranger would look for first.

**ANSWER:**
>
>

---

## 3 · Verify — flagged

| ID | Claim | Source |
|---|---|---|
| **V-070** | **12A redline.** `stats.h` assumes 7000 rpm, which also sets the tach red zone | FSM |
| V-071 | Minimum acceptable oil pressure for a 12A at idle. Assumed 1.0 bar | FSM / rotary reference |
| V-072 | FB fuel tank capacity. Assumed 15.9 gal | FSM |
| **V-073** | **IMU mounting orientation on the ICU PCB** must match the axis convention in D-161, or every axis needs a sign flip | Decide before PCB layout |
| **V-074** | **Does O8 wiper braking need a park input?** If the PMU's braking feature only works against a park-sense signal, `Q-063` option (c) is off the table | PMU manual |
| **V-075** | **Does the PMU have a native shutdown delay** that makes the O22 self-hold latch unnecessary — freeing pin 8 and K11's coil logic | PMU client — Checklist 2.15 |

## 4 · Verify — easy: one search, catalogue page, or a look

| ID | Claim | Source |
|---|---|---|
| V-053 | Battery terminal type — SAE or 3/8 threaded. The battery is in hand; **look at it** before the lug order (`T-029`) | The battery |
| V-051 | Ionic case dimensions before cutting the cargo bin | Tape measure |
| V-052 | Battery heater trigger and winter draw | Ionic docs / app |
| V-014 | DT size-16 contact current rating. Catalogue confirms size 20 = 7.5 A | TE catalogue pp. 169–180 |
| V-057 | TCAN1042/1051 exact part suffix | TI datasheet |
| V-047 | Shielded 16 AWG availability; single-end shield grounding | Wire supplier |
| V-058 | **Display nit rating — 800–1000 minimum.** | Vendor spec |
| V-069 | **Open-barrel crimper die size.** Confirm against a real terminal before buying | Measure the terminal |
| V-040 | Aeromotive Phantom 340 draw at target pressure | Aeromotive spec — future part |
| V-059 | Teensy 4.1 availability after the Adafruit → SparkFun distribution change | PJRC / SparkFun, before the carrier PCB commits |
| V-001 | Stock 12A coil / ignitor configuration — one coil per rotor, leading and trailing, as the factory diagram shows | Under the hood |

## 5 · Verify — needs the car

| ID | Claim | Via |
|---|---|---|
| V-002 | Alternator output rating — the case says only 'B' / Mitsubishi (2026-08), no rating readable | FSM / Mitsubishi part lookup |
| V-055 | Sill space behind the kick panel — 4 relays, 3 fuse positions, ground stud | Tape measure — Checklist 0.10 |
| V-038 | Coolant level unit and oscillator still fitted | Inspect |
| V-037 | Fuel sender ohm range, empty → full | Measure at the tank — Checklist 0.5 |
| V-050 | Which ignition outputs stay live in RUN and START | `T-023` continuity test — Checklist 0.7 |
| V-030 | Pop-up motor internal limit pinout — drive vs limit pins | `T-011` continuity test — Checklist 0.6 |
| V-067 | **Tach pulses per revolution.** Assumed 2 for a 2-rotor off the leading coil. Wrong scales every RPM reading by a constant | Meter session or FSM |
| V-021 | Horn current draw — estimate 4–8 A the pair; interim fuse 10.0 A set | PMU telemetry after migration (D-174) |
| **V-077** | **Alternator health.** Redo 2026-08: 0.8 A idle → 2.5 A with wipers HIGH + hazards — direction now correct, but the 100 A range is ±~3.5 A down there, so the magnitude is mush. The decisive check is battery volts at idle: 13.5–14.5 V = charging; below ~12.8 V = failing, and likely the day-by-day decay | Volt check at the battery · feeds `V-002` `V-019` |

## 6 · Verify — blocked on something else

| ID | Claim | Blocked by |
|---|---|---|
| V-065 | **PMU's own CAN export format.** ECUMaster fixes it, we don't. Gates the PMU half of the message map | The client — Checklist 2.5 |
| V-019 | Can the 12A alternator carry the migrated load | Measured draw, `T-014` |
| V-060 | New mirror conductor count and control protocol | Pick the mirrors, `T-031` |
| V-033 | Fuel-door and hatch solenoid channel allocation | `Q-061` |
| V-028 | Is a one-touch (single wipe) function wanted in the wiper logic | Decide during Checklist 2.12 |
| V-056 | Does the DCU need a constant keep-alive for climate memory at all — or does it restore from SD on wake | DCU firmware design (F-001) |
| V-061 | Radar sensor interface | Design the subsystem ([`DEFERRED-FEATURES.md`](../04-SUBSYSTEMS/DEFERRED-FEATURES.md)) |

## 7 · Assumptions in force

Assumptions carry an `A-` ID so a wrong one can be found and unwound. Closed
ones are in [`DECISIONS.md`](DECISIONS.md) (A-005 → D-148, A-007 → D-112, A-009 → D-091).

| ID | Assumption | Where it bites |
|---|---|---|
| A-010 | Brake fluid level goes to the ICU on DP-ICU 12 via L1-S2 1. Coolant and oil level are optional, have no ICU cavity, and are capped in L1-S2 2–3 | `connectors.csv`, [`CAVITY-STATE.md`](../02-HARNESS/CAVITY-STATE.md) |
| A-011 | The wideband O2 signal (K-001) is carried to the dash on L1-S1 12 and capped. It is not an ICU input and has no display until the LS | `connectors.csv`, [`engine.md`](../02-HARNESS/engine.md) |
| A-012 | The luggage compartment switch joins the A6 door-pin ladder as a fourth state — re-run the ladder maths before it is added | [`LADDERS.md`](../01-DESIGN/LADDERS.md), L4-S 3 |
| A-013 | The CAN keypad is powered from the accessory bus O10 (DP-KEY 3), so it is dead when the car sleeps and cannot itself be a wake source | [`PIN-MAP.md`](../02-HARNESS/PIN-MAP.md) DP-KEY, [`SCHEMATICS.md`](../01-DESIGN/SCHEMATICS.md) wake network |

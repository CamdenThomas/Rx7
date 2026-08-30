# METER SESSION — what remains

*Rev 2026-08-30 · owns: the remaining old-harness measurement procedure — everything still needed from the car before the PMU goes in. Completed figures live in `../02-HARNESS/data/pmu_pins.csv` → [`../01-DESIGN/CHANNEL-SCHEDULE.md`](../01-DESIGN/CHANNEL-SCHEDULE.md); prior sittings' procedure text is in git history. Scope set by D-174 / D-175 / D-176: all remaining current figures come from PMU telemetry after migration; part replacement is a separate post-PMU project.*

**Tool:** UNI-T UT210E. **One sitting — roughly 2–3 hours.** Items 1–2 need
the battery connected (2 needs the engine); everything after runs with the
battery disconnected. Do them in this order and you disconnect once.

**The two clamp rules still apply to item 1:** zero the jaw (closed, empty,
ZERO) before the reading, and clamp ONE conductor.

**Continuity mode:** test leads in (black **COM**, red **V/Ω**), dial to **Ω**,
press **SELECT** until the beeper symbol shows. Beep = connected.

---

## 1 · Parasitic draw — first, before opening anything

Car asleep **20+ minutes**: key out, doors and hatch shut, glovebox shut.
Don't open a door to check on things — that wakes it. Take the reading first.

1. Clamp on the **2 A range**, zero the jaw
2. Clamp the **battery negative cable**, one conductor
3. Record in **mA**

**Expect tens of mA.** Over ~100 mA, something is awake — worth one note of
what, but do not chase it; the whole circuit dies with the harness. This
number is the baseline the finished car gets compared against.

## 2 · Battery volts at idle — the alternator verdict (`V-077`)

Leads in (black **COM**, red **V/Ω**), dial **V**, **SELECT** until `DC` / ⎓
shows. Engine running, at idle:

1. Red probe on the battery **+** post, black on **−**. Record
2. Turn on wipers HIGH + hazards, record again

| Reading | Verdict |
|---|---|
| 13.5–14.5 V, holds above ~13.2 loaded | Charging — alternator fine |
| Below ~12.8 V at idle | **Failing** — likely the cause of the day-by-day decay. Feeds `V-002` / `V-019`; replacement is post-PMU (D-176) |

Engine off. **Disconnect the battery negative** for everything below.

## 3 · Pop-up motor limit pinout (`T-011` / `V-030`)

Gates the K1–K4 H-bridge wiring and the A4/A5 ladders. Battery disconnected.

Unplug **E-03** (left motor). The motor-side connector has four wires:
**WR / YG / R / RY**. Which pair is the motor winding and which pins are the
internal limit switches is the question — **do not guess**.

1. Headlights DOWN (parked): measure **resistance between every pair** of the
   four motor-side pins — six pairs. Record the six numbers
2. Hand-crank the motor to **mid-travel** (manual knob on the motor). Repeat
   all six pairs
3. Crank to full **UP**. Repeat all six pairs

**Reading it:** the pair showing low ohms (~0.5–5 Ω) at *every* position is
the **drive pair** (motor winding). Pins whose continuity *changes with
position* are the **limit switches** — record at which extreme each opens.

Repeat everything at **E-04** (right motor). Eighteen numbers per side.

## 4 · Ignition switch continuity (`V-050` / `T-023`)

Gates the wake network and the A16 key ladder. Battery still disconnected.

Unplug the ignition switch connector under the column. Identify the **feed
terminal** (the heaviest wire) on the switch side.

For the key at each of **OFF · ACC · RUN · START** (hold START against the
spring): beep-test the feed terminal against **every other switch terminal**
and record which connect. Note terminals by wire colour.

**The design question this answers:** which outputs are live *together* —
especially what stays live in START and what drops.

## 5 · Fuel sender ohms (`V-037` / `T-012`)

Gates the A7 input scaling. At the tank, rear of the car.

1. Unplug the sender connector
2. Dial **Ω**. Measure sender-side: **signal pin to ground pin** (or signal
   pin to the sender's metal body if there's no ground pin)
3. Record the ohms **and the dash gauge reading right now** — the pair is the
   calibration point
4. **Again after the next fill-up** for the second point — leave this page
   open until then

## 6 · Door pin switches — A6 ladder

Gates the A6 ladder and the door-pin wake source. Battery still disconnected.

Per side: unplug the door pin switch (front of the door opening), beep-test
the switch terminal to the switch body / mounting screw:

- Plunger **out** (door open) — record beep or no beep
- Plunger **pressed** (door shut) — record

Both doors. Expect closed-to-ground with the door open (that's what lit the
dome lamp); confirm rather than assume.

---

## Recording sheet

| # | Item | Reading(s) | Notes |
|---|---|---|---|
| 1 | Parasitic, mA |  |  |
| 2 | Volts idle / loaded |  /  |  |
| 3 | E-03 pairs at DOWN / MID / UP | 6 × 3: |  |
| 3 | E-04 pairs at DOWN / MID / UP | 6 × 3: |  |
| 4 | Ignition: feed → live terminals at OFF / ACC / RUN / START |  |  |
| 5 | Sender Ω + gauge reading now |  | after fill: |
| 6 | Door pins L/R, open / shut |  |  |

## When you're done

Send the sheet. The agent files the figures (ladder maths into
[`../01-DESIGN/LADDERS.md`](../01-DESIGN/LADDERS.md), limits into the K1–K4 wiring, sender into A7,
ignition states into the wake network), closes the V/T items, and the
old-harness measurement campaign is **complete**. Reconnect the battery —
the car drives home.

**Deliberately not here (D-176):** washer diagnosis, volt-drop tests, any
replace-or-keep investigation. Underperforming parts are identified by PMU
telemetry against healthy-expected draw after migration, and replaced as
their own project when it's as easy as installing a new part.

# METER SESSION — step by step

*Rev 2026-08. The clamp meter arrives today. This is the procedure.*

**Tool:** UNI-T UT210E. **DC current.** It defaults to AC on power-up — change it.

**Budget half a day.** You will not finish in an hour and rushing it costs you
data you can never recover.

---

## Before you start

- [ ] Meter on **DC A**, not AC
- [ ] Print the recording sheet at the bottom of this file
- [ ] Car outside or garage door open — **rotary at idle in a closed garage is
      carbon monoxide**
- [ ] Sleeves rolled, nothing loose, hair tied. Belt and pulleys are spinning
- [ ] Fire extinguisher within reach, not across the garage

## The two rules that make or break every reading

**1 · Zero the jaw before EVERY reading.** Jaw closed, nothing inside, press
ZERO. DC clamps drift constantly and an un-zeroed jaw reads a full amp off.

**2 · Clamp ONE conductor.** Both wires in the jaw reads zero. This is the single
most common clamp meter mistake and it looks exactly like a dead circuit.

---

## Where to clamp — the general rule

**At the device's own connector, on one wire, without unplugging anything.**
You do not need to break any circuit. That is the whole reason this tool was
chosen.

If a circuit feeds several devices — the tail bus feeds eight lamps — clamp
**upstream of the splits**, at the fuse block or the switch output, to get the
whole circuit at once.

---

# PART 1 · Engine off, key on

Ignition to **RUN**, engine not running. Safer, and most lighting works here.

### 1.1 · Tail / park / marker / plate — O6

- **Access:** the R wire at the headlight switch output (E-01), under the dash
  behind the column shroud. That's upstream of all eight lamps
- Switch to **PARK**. Record. Switch to **HEAD**. Record — should be identical
- Expect **~4.4 A**

### 1.2 · Brake lamps — O7

- **Access:** the W wire at the stop light switch (F-11), at the brake pedal
- Have someone press the pedal, or wedge it
- Expect **~3.9 A**

### 1.3 · Turn signals — O17 / O18

- **Access:** the GR wire (left) or GO wire (right) at the combination switch
  connector (F-02), under the column
- Stalk to LEFT. **Read the peak during an ON phase** — it flashes, so watch for
  the high reading, not the average
- Repeat RIGHT. Then **HAZARD** — both sides together
- Expect **~4.2 A per side**, ~8.4 A on hazard

### 1.4 · Reverse — O19

- **Access:** the RW wire at the inhibitor switch (A-06) on the transmission, or
  at a rear combination lamp connector
- **Engine off, key RUN, foot on brake**, shifter to R
- Expect **~3.9 A**

### 1.5 · Interior, glovebox, luggage — O20

- **Access:** the LY wire at the interior lamp, or upstream at the fuse block
- Open a door, then the glovebox, then the hatch. Record each and all together
- Expect **~1 A total**

### 1.6 · Illumination bus

- **Access:** the RL wire at the dimmer (E-05)
- Headlight switch to PARK, dimmer to **full bright**
- Expect **~1.4 A**

### 1.7 · Horns — O11

- **Access:** the GY wire at either horn (F-09 / F-10)
- Press the horn. **Both together, then unplug one and read the other**
- Expect **4–8 A the pair**

### 1.8 · Wipers — O8 / O9 · **the important one**

- **Access:** the LW wire (low) and LR wire (high) at the wiper motor connector
  (D-02), under the cowl panel
- **Wet the glass first.** A dry sweep reads low and lies to you
- LOW running. Record. HIGH running. Record
- **Then stall:** hold a blade with a gloved hand for **2 seconds maximum**,
  read, release. This is the number that sizes the channel
- Expect 3–5 A running, **12–20 A stalled**

> Two seconds. Longer and you cook the motor.

### 1.9 · Windows — **SKIP. The windows are manual** `[D-131]`

No motors, no wiring, nothing to measure. Power windows are a deferred luxury
item — see `../04-SUBSYSTEMS/DEFERRED-FEATURES.md`.

**When motors are eventually fitted**, measure then: run fully up and hold the
switch for 2 s at the top stop, which is a natural stall. Expect 4–6 A running,
10–15 A stalled. Set the soft fuse from that reading, and raise O1's limit to
cover pop-ups plus windows together.

---

# PART 2 · Engine running

Idle, charging. **Measure at running voltage** — figures at 12.6 V rest are ~10%
wrong.

### 2.1 · Headlights — O2 / O3

- **Access:** the RL wire (low) and RY wire (high) at the headlight connector
  (E-08 / E-09), in the bucket
- Currently LED housings. Record both anyway — it's the baseline for whatever
  replaces them
- Low, then high, then **PASS** from the column

### 2.2 · Fuel pump — O5

- **Access:** the BLg wire at the pump (B-24), rear of the car
- Running, at idle
- Expect **1–3 A** for the Carter P4070. Also closes `[V-054]`

### 2.3 · Ignition coils — O12

- **Access:** the BW wire feeding the coils (B-18 / B-19)
- At idle, then at **~3000 rpm** — it rises with rpm
- Expect 4–6 A

### 2.4 · Alternator output

- **Access:** the WR cable at the alternator B+ (A-09). This is a big cable —
  use the 100 A range
- At idle with everything off, then everything on
- Also **read the rating stamped on the case** — closes `[V-002]`

---

# PART 3 · The four broken circuits

**These cannot be measured normally.** Workarounds below.

### 3.1 · Rear defog — O4 · switch broken `[K-020]`

- **Workaround:** unplug the defrost switch (G-24) and **jumper Y to LG** in the
  connector with a fused lead. That energises the grid without the switch
- **Access:** clamp the LG wire at the grid terminal on the glass
- **Read cold, then again at 2 minutes.** Grids draw more cold and the cold
  figure is the design one
- Expect **10–13 A cold**

### 3.2 · Pop-up motors — O1 stall · switch broken `[K-021]`

- **Workaround:** drive the motor directly. Disconnect the retractor motor
  connector (E-03 / E-04) and apply fused 12 V to the drive pair
- **Before you do:** `[T-011]` continuity-test the motor first to identify which
  of WR/YG/R/RY are drive and which are the internal limits. **Do not guess** —
  backfeeding a limit switch can damage it
- Run a full raise cycle, record. Then hold at the limit for 2 s for stall
- Expect 4–6 A running, **15–25 A stalled**

> This one is two jobs in one: it closes `[V-030]` and `[T-015]` together.
> Do the continuity test first, with the battery disconnected.

### 3.3 · Washer pump — not working `[K-022]`

- **Diagnose before measuring.** Three possibilities:
  1. **Pump dead** — apply fused 12 V directly at the pump (D-01). If it doesn't
     run, it needs replacing
  2. **Wiring open** — check for 12 V at the pump connector with the stalk in
     WASH
  3. **Switch fault** — continuity across the WASH position of D-03
- If the pump runs on direct 12 V, measure it. Expect 3–5 A
- **Record which it was.** If the pump is dead it goes on the parts list

### 3.4 · Blower motor — dead `[K-023]`

- **Cannot be measured.** The motor doesn't run
- Confirm it's the motor: 12 V present at the connector with the switch on?
- **O16 gets sized from the replacement's spec sheet**, not from measurement.
  The channel is 25 A with a flyback diode, which covers any plausible unit
- **Still measure the resistor pack** if you can — continuity across each tap
  tells you whether it survived whatever killed the motor

---

# PART 4 · Parasitic draw — do this last

Engine off, key out, doors shut, everything closed. **Wait 20 minutes** for
anything with a timer to sleep.

- **Access:** clamp the battery **negative** cable
- Use the **2 A range** — the UT210E resolves 1 mA there, which is the whole
  reason this meter was chosen
- Expect tens of milliamps

Record it. It becomes the baseline you compare the finished car against.

---

# PART 5 · Not current — while you're there

| Item                        | Method                                                                              | Closes              |
|-----------------------------|-------------------------------------------------------------------------------------|---------------------|
| **Ignition switch outputs** | Continuity on every output at OFF / ACC / RUN / START. **Which stay live together** | `[V-050]` `[T-023]` |
| **Fuel sender**             | Resistance, at the current fuel level. Again after a fill                           | `[V-037]` `[T-012]` |
| **Pop-up limits**           | Continuity, both sides, both extremes, mid-travel                                   | `[V-030]` `[T-011]` |
| **Door pin switches**       | Continuity, each door open and closed                                               | A6 ladder           |

---

# Recording sheet

| #   | Circuit            | Access point              | Steady A | Stall / peak A | Volts | Notes |
|-----|--------------------|---------------------------|----------|----------------|-------|-------|
| 1.1 | Tail / park PARK   | E-01 R wire               |          |                |       |       |
| 1.1 | Tail / park HEAD   | E-01 R wire               |          |                |       |       |
| 1.2 | Brake              | F-11 W wire               |          |                |       |       |
| 1.3 | Turn LEFT          | F-02 GR wire              |          |                |       |       |
| 1.3 | Turn RIGHT         | F-02 GO wire              |          |                |       |       |
| 1.3 | Hazard both        | F-02                      |          |                |       |       |
| 1.4 | Reverse            | A-06 RW wire              |          |                |       |       |
| 1.5 | Interior all       | LY at lamp                |          |                |       |       |
| 1.6 | Illumination       | E-05 RL wire              |          |                |       |       |
| 1.7 | Horns pair         | F-09 GY wire              |          |                |       |       |
| 1.7 | Horn single        | F-09 GY wire              |          |                |       |       |
| 1.8 | **Wiper LOW**      | D-02 LW wire              |          |                |       |       |
| 1.8 | **Wiper HIGH**     | D-02 LR wire              |          |                |       |       |
| 1.8 | **Wiper STALL**    | D-02                      |          |                |       |       |
| 1.9 | Windows            | **MANUAL — skip**         |          |                |       |       |
| 2.1 | Headlight LOW      | E-08 RL wire              |          |                |       |       |
| 2.1 | Headlight HIGH     | E-08 RY wire              |          |                |       |       |
| 2.2 | Fuel pump          | B-24 BLg wire             |          |                |       |       |
| 2.3 | Coils idle         | B-18 BW wire              |          |                |       |       |
| 2.3 | Coils 3000 rpm     | B-18 BW wire              |          |                |       |       |
| 2.4 | Alternator idle    | A-09 WR cable             |          |                |       |       |
| 2.4 | Alternator loaded  | A-09 WR cable             |          |                |       |       |
| 3.1 | **Defog cold**     | grid LG, jumpered         |          |                |       |       |
| 3.1 | Defog 2 min        | grid LG                   |          |                |       |       |
| 3.2 | **Pop-up L run**   | E-03, direct 12 V         |          |                |       |       |
| 3.2 | **Pop-up L stall** | E-03                      |          |                |       |       |
| 3.2 | **Pop-up R run**   | E-04                      |          |                |       |       |
| 3.2 | **Pop-up R stall** | E-04                      |          |                |       |       |
| 3.3 | Washer pump        | D-01, if it runs          |          |                |       |       |
| 3.4 | Blower             | **DEAD — cannot measure** | —        | —              | —     |       |
| 4   | **Parasitic**      | battery negative          |          |                |       | mA    |

---

# When you're done

Send Claude the sheet. It updates `LOADS.md`, recalculates the provisional
soft-fuse table, and firms up the A4/A5 ladder values in `LADDERS.md`.

**The wiper stall, pop-up stall and defog cold readings are the three that matter
most.** Everything else has headroom; those three size real hardware.

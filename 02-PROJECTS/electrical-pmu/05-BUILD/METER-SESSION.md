# METER SESSION — step by step

*Rev 2026-08-30 · owns: the clamp-meter procedure — access points, expected figures and the recording sheet. Readings themselves are recorded once, in `../02-HARNESS/data/pmu_pins.csv` → [`../01-DESIGN/CHANNEL-SCHEDULE.md`](../01-DESIGN/CHANNEL-SCHEDULE.md).*

**Tool:** UNI-T UT210E, in hand (`T-001` done). **DC current.** It defaults to
AC on power-up — change it. **Checklist:** [`CHECKLIST.md`](CHECKLIST.md) 0.1–0.7.

**Budget ~10–12 hours across two or three sittings**, not an afternoon. The
first sitting (brake, turn, one wrong-wire attempt at the tail circuit) took
most of an evening and produced three usable numbers. Rushing costs data that
cannot be recovered once the harness is out.

## Contents

1. Before you start · 2. The two rules · 3. Where to clamp · Part 1 engine
off · Part 2 engine running · Part 3 the four broken circuits · Part 4
parasitic draw · Part 5 not current · Recording sheet · When you're done ·
Part 6 using the meter — clarifications from the first sitting

---

## 1 · Before you start

- [ ] Meter on **DC A**, not AC (SELECT toggles it — §Part 6)
- [ ] Print the recording sheet at the bottom of this file
- [ ] Car outside or garage door open — **rotary at idle in a closed garage is
      carbon monoxide**
- [ ] Sleeves rolled, nothing loose, hair tied. Belt and pulleys are spinning
- [ ] Fire extinguisher within reach, not across the garage

## 2 · The two rules that make or break every reading

**1 · Zero the jaw before EVERY reading.** Jaw closed, nothing inside, press
ZERO. DC clamps drift constantly and an un-zeroed jaw reads a full amp off.

**2 · Clamp ONE conductor.** Both wires in the jaw reads zero. This is the single
most common clamp meter mistake and it looks exactly like a dead circuit.

## 3 · Where to clamp — the general rule

**At the device's own connector, on one wire, without unplugging anything.**
You do not need to break any circuit. That is the whole reason this tool was
chosen.

If a circuit feeds several devices — the tail bus feeds eight lamps — clamp
**upstream of the splits**, at the fuse block or the switch output, to get the
whole circuit at once. Factory connector codes (E-01, F-11 …) are the
`01-REFERENCE/factory-circuits/OEM-RECORD.md` codes; wire colours are the
factory abbreviations from the same file.

---

## Part 1 · Engine off, key on

Ignition to **RUN**, engine not running. Safer, and most lighting works here.

### 1.1 · Tail / park / marker / plate — O6 · **done — 5.4 A, PARK = HEAD**

- **Access:** the **`RG` wire at the headlight switch output (E-01)**, under
  the dash behind the column shroud. That is upstream of all eight lamps.
- Switch to **PARK**. Record. Switch to **HEAD**. Record — should be identical
- Expect **~4.4 A**
- Recorded 2026-08: **5.4 A**, identical in both positions. E-01 carries two
  `RG` conductors (the bus splits at the switch) — both together in the jaw
  sums them, which is the correct total here since both flow the same way.
  5.4 A ≈ eight filaments at ~8 W — accepted. Soft fuse 7.5 A (× 1.35)

### 1.2 · Brake lamps — O7 · **done — 7.0 A steady, 9.5 A warm-up**

- **Access:** the W wire at the stop light switch (F-11), at the brake pedal
- Have someone press the pedal, or wedge it
- Recorded 2026-08 against an estimate of 3.9 A — nearly double. Worth
  confirming the bulbs are the correct 27/8 W and not something larger, but the
  channel is 15 A and the soft fuse is set at 9.5 A either way

### 1.3 · Turn signals — O17 / O18 · **done per side — 3.4 A**

- **Access:** the GR wire (left) or GO wire (right) at the combination switch
  connector (F-02), under the column
- Stalk to LEFT. **Read the peak during an ON phase** — it flashes, so watch for
  the high reading, not the average. Repeat RIGHT
- **Hazard: clamp the `WG` feed upstream of the hazard switch**, which carries
  both sides. Clamping `GR` during hazard gives half the circuit and a reading
  that wanders with the flash cycle (2–3.4 A on the first sitting). Or record
  left and right and add them
- Recorded 3.4 A per side against an estimate of 4.2 A — slightly under, normal
  for aged filaments and a plausible sign one bulb is dim or out. The
  occasional 3.4 → 2.3 A drop that follows the fuel-pump note is fault K-008
  happening in front of you; it dies with the harness (D-105)

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

---

## Part 2 · Engine running

Idle, charging. **Measure at running voltage** — figures at 12.6 V rest are ~10%
wrong.

### 2.1 · Headlights — O2 / O3

- **Access:** the RL wire (low) and RY wire (high) at the headlight connector
  (E-08 / E-09), in the bucket
- Currently LED housings. Record both anyway — it's the baseline for whatever
  replaces them
- Low, then high, then **PASS** from the column

### 2.2 · Fuel pump — O5 · **done — 2.38 A**

- **Access:** the BLg wire at the pump (B-24), rear of the car
- Running, at idle
- Expect **1–3 A** for the Carter P4070. Also closes `V-054`
- Recorded 2026-08: **2.38 A** at idle — in range, `V-054` closed. Soft fuse
  4.0 A (D-173 — no practical stall on an in-line pump)

### 2.3 · Ignition coils — O12

- **Access:** the BW wire feeding the coils (B-18 / B-19)
- At idle, then at **~3000 rpm** — it rises with rpm
- Expect 4–6 A

### 2.4 · Alternator output

- **Access:** the WR cable at the alternator B+ (A-09). This is a big cable —
  use the 100 A range
- At idle with everything off, then everything on
- Also **read the rating stamped on the case** — closes `V-002` / `T-004`

---

## Part 3 · The four broken circuits

**These cannot be measured normally.** Workarounds below.

### 3.1 · Rear defog — O4 · switch broken (K-020)

- **Workaround:** unplug the defrost switch (G-24) and **jumper Y to LG** in the
  connector with a fused lead. That energises the grid without the switch
- **Access:** clamp the LG wire at the grid terminal on the glass
- **Read cold, then again at 2 minutes.** Grids draw more cold and the cold
  figure is the design one
- Expect **10–13 A cold**

### 3.2 · Pop-up motors — O1 stall · switch broken (K-021)

- **Workaround:** drive the motor directly. Disconnect the retractor motor
  connector (E-03 / E-04) and apply fused 12 V to the drive pair
- **Before you do:** `T-011` continuity-test the motor first to identify which
  of WR/YG/R/RY are drive and which are the internal limits. **Do not guess** —
  backfeeding a limit switch can damage it
- Run a full raise cycle, record. Then hold at the limit for 2 s for stall
- Expect 4–6 A running, **15–25 A stalled**

> This one is two jobs in one: it closes `V-030` and `T-015` together
> ([`CHECKLIST.md`](CHECKLIST.md) 0.2 and 0.6). Do the continuity test first, with the battery
> disconnected.

### 3.3 · Washer pump — not working (K-022)

- **Diagnose before measuring.** Three possibilities:
  1. **Pump dead** — apply fused 12 V directly at the pump (D-01). If it doesn't
     run, it needs replacing
  2. **Wiring open** — check for 12 V at the pump connector with the stalk in
     WASH
  3. **Switch fault** — continuity across the WASH position of D-03
- If the pump runs on direct 12 V, measure it. Expect 3–5 A
- **Record which it was.** If the pump is dead it goes on the parts list. The
  pump also has no PMU output yet — `Q-063`

### 3.4 · Blower motor — dead (K-023)

- **Cannot be measured.** The motor doesn't run
- Confirm it's the motor: 12 V present at the connector with the switch on?
- **O16 gets sized from the replacement's spec sheet**, not from measurement.
  The channel is 25 A with a flyback diode, which covers any plausible unit
- **Still measure the resistor pack** if you can — continuity across each tap
  tells you whether it survived whatever killed the motor

---

## Part 4 · Parasitic draw — do this last

Engine off, key out, doors shut, everything closed. **Wait 20 minutes** for
anything with a timer to sleep.

- **Access:** clamp the battery **negative** cable
- Use the **2 A range** — the UT210E resolves 1 mA there, which is the whole
  reason this meter was chosen
- Expect tens of milliamps

Record it. It becomes the baseline you compare the finished car against.

---

## Part 5 · Not current — while you're there

| Item | Method | Closes |
|---|---|---|
| **Ignition switch outputs** | Continuity on every output at OFF / ACC / RUN / START. **Which stay live together** | `V-050` `T-023` — Checklist 0.7 |
| **Fuel sender** | Resistance, at the current fuel level. Again after a fill | `V-037` `T-012` — Checklist 0.5 |
| **Pop-up limits** | Continuity, both sides, both extremes, mid-travel | `V-030` `T-011` — Checklist 0.6 |
| **Door pin switches** | Continuity, each door open and closed | A6 ladder, [`../01-DESIGN/LADDERS.md`](../01-DESIGN/LADDERS.md) |

---

## Recording sheet

Print this. Then transcribe it into `pmu_pins.csv` (`meas_a`, and `soft_fuse`
per the multipliers in [`CHANNEL-SCHEDULE.md`](../01-DESIGN/CHANNEL-SCHEDULE.md)) and run `gen.py`; the schedule,
[`PIN-MAP.md`](../02-HARNESS/PIN-MAP.md) and `channels.h` update together. Rows marked **done** already
have their figure in the CSV.

| #   | Circuit            | Access point              | Steady A | Stall / peak A | Volts | Notes            |
|-----|--------------------|---------------------------|----------|----------------|-------|------------------|
| 1.1 | Tail / park PARK   | E-01 **RG** wire          | 5.4      |                |       | **done** 2026-08 |
| 1.1 | Tail / park HEAD   | E-01 **RG** wire          | 5.4      |                |       | **done** 2026-08 |
| 1.2 | Brake              | F-11 W wire               | 7.0      | 9.5            |       | **done** 2026-08 |
| 1.3 | Turn LEFT          | F-02 GR wire              | 3.4      | —              |       | **done** 2026-08 |
| 1.3 | Turn RIGHT         | F-02 GO wire              | 3.4      | —              |       | **done** 2026-08 |
| 1.3 | Hazard both        | **WG** feed               | ~6.8 max |                |       | wanders 2–7 with flash cycle; max ≈ L+R ✓ — nothing to file, hazard = O17+O18 |
| 1.4 | Reverse            | A-06 RW wire              |          |                |       |                  |
| 1.5 | Interior all       | LY at lamp                |          |                |       |                  |
| 1.6 | Illumination       | E-05 RL wire              |          |                |       |                  |
| 1.7 | Horns pair         | F-09 GY wire              |          |                |       |                  |
| 1.7 | Horn single        | F-09 GY wire              |          |                |       |                  |
| 1.8 | **Wiper LOW**      | D-02 LW wire              |          |                |       |                  |
| 1.8 | **Wiper HIGH**     | D-02 LR wire              |          |                |       |                  |
| 1.8 | **Wiper STALL**    | D-02                      |          |                |       | 2 s max          |
| 2.1 | Headlight LOW      | E-08 RL wire              |          |                |       | LED baseline     |
| 2.1 | Headlight HIGH     | E-08 RY wire              |          |                |       |                  |
| 2.2 | Fuel pump          | B-24 BLg wire             | 2.38     |                |       | **done** 2026-08 |
| 2.3 | Coils idle         | B-18 BW wire              |          |                |       |                  |
| 2.3 | Coils 3000 rpm     | B-18 BW wire              |          |                |       |                  |
| 2.4 | Alternator idle    | A-09 WR cable             |          |                |       | 100 A range      |
| 2.4 | Alternator loaded  | A-09 WR cable             |          |                |       | + case rating    |
| 3.1 | **Defog cold**     | grid LG, jumpered         |          |                |       |                  |
| 3.1 | Defog 2 min        | grid LG                   |          |                |       |                  |
| 3.2 | **Pop-up L run**   | E-03, direct 12 V         |          |                |       |                  |
| 3.2 | **Pop-up L stall** | E-03                      |          |                |       | 2 s max          |
| 3.2 | **Pop-up R run**   | E-04                      |          |                |       |                  |
| 3.2 | **Pop-up R stall** | E-04                      |          |                |       | 2 s max          |
| 3.3 | Washer pump        | D-01, if it runs          |          |                |       | which fault?     |
| 3.4 | Blower             | **dead — cannot measure** | —        | —              | —     |                  |
| 4   | **Parasitic**      | battery negative          |          |                |       | mA, 2 A range    |

**The wiper stall, pop-up stall and defog cold readings are the three that
matter most.** Everything else has headroom; those three size real hardware.

## When you're done

Send the sheet. The agent enters the figures into the CSV, regenerates, and
firms up the A4/A5 ladder values in [`../01-DESIGN/LADDERS.md`](../01-DESIGN/LADDERS.md) (Checklist 0.17,
0.18). Each measured channel then gets its soft fuse entered in the client at
[`CHECKLIST.md`](CHECKLIST.md) 2.22 and is enabled; unmeasured outputs stay disabled (D-165).

---

## Part 6 · Using the meter — clarifications from the first sitting

*The things that weren't obvious with the meter in hand.*

### Voltage — you need the probes, not the clamp

**The clamp only measures current.** For voltage you must plug the **test leads**
into the meter: black into `COM`, red into the `V/Ω` jack.

Then:
1. Dial to **V**
2. It defaults to **AC** — press the **SELECT** button to toggle to **DC**.
   The display should show a small `DC` or a `⎓` symbol
3. Black probe on a ground, red probe on the point you're measuring

**If the display reads nothing on V with leads connected, you're still in AC
mode.** SELECT is the fix, not the dial. The same button toggles AC/DC on the
current ranges too.

### Peak and inrush — mostly you will NOT catch it, and that's fine

**A handheld clamp cannot see a 30 ms spike.** Do not chase it.

| What you saw | What it means |
|---|---|
| Brake: peaked 9.5 A, settled 7 A | **Real.** A 27 W filament warms over a few hundred ms — slow enough to catch |
| Most circuits: one steady number, no peak | **Normal and expected.** Leave the peak column blank |
| Nothing to see at all | Fine. Record steady, move on |

**Only motors get a deliberate peak measurement**, and it isn't inrush — it's
**stall**, which is a steady reading you create on purpose by holding the motor.
Wipers and pop-ups. Nothing else.

> **Rule: if a peak doesn't present itself within a second or two, there isn't
> one worth recording. Write the steady value and move on.**

**Do not try to catch inrush.** The design already applies a 10× multiplier for
filament and 7–10× for motors — that is what the inrush window in the PMU config
is sized against (D-120, [`CHANNEL-SCHEDULE.md`](../01-DESIGN/CHANNEL-SCHEDULE.md)).

### Reading 0 on a live circuit — the four causes

In order of likelihood:

1. **Both conductors in the jaw.** Feed and return cancel to zero. Clamp **one
   wire**
2. **Jaw not zeroed.** Close it empty, press ZERO, then clamp
3. **Wrong wire** — the tail circuit on the first sitting read 0 on `R` because
   `R` is the switch's *input*; the lamp output is `RG` (Part 1.1)
4. Circuit genuinely off

### Why hazard read 2 to 9 A erratically

Hazard flashes **both sides at once**, but `GR` is the **left side only**.
Clamping one wire gives you half the circuit, and the spread comes from catching
different points in the flash cycle. Clamp the `WG` feed for the total, or add
left and right.

### What to expect per circuit

- **Most lamp circuits: one number.** Steady only
- **Wipers and pop-ups: two numbers.** Running, then a deliberate 2-second stall
- **Defog: two numbers.** Cold at switch-on, then again at 2 minutes
- **Everything else: one number**

### Second sitting — the four readings that failed sanity (2026-08)

Wiper LOW/HIGH running, tail, hazard and fuel pump all passed sanity and are
recorded. These four did not — D-174 later ruled the redos moot
(interim fuses from healthy-expected values); kept for technique:

- **A minus sign is fine; falling with rpm is not.** Negative only means the
  jaw's arrow faces against current flow — flip the clamp or ignore the sign.
  But the coil feed must RISE with rpm, and ~2 A looks like one coil's branch,
  not the pair. Find the BW upstream of the split to both coils (V-076 → D-174)
- **The alternator cannot make LESS current when you add load.** 0.44 → 0.09 A
  is an un-zeroed jaw or the wrong conductor — or the alternator really is
  weak, which would also explain electrics worsening by the day. Zero on the
  100 A range, clamp the WR alone, then read battery volts at idle:
  13.5–14.5 V means charging (`V-077`)
- **A stall reading below running current means the motor never stalled.**
  Holding the blade lets the linkage slip. Hold the wiper arm at its base
  (V-079 → D-174)
- **All four wires in the jaw only sums correctly when the return is chassis
  ground.** The pop-up read (3 A up / 1 A down) may be real for a case-grounded
  motor — `T-011` identifies the drive pair; then clamp one wire (V-080 → D-174)

**On the decaying factory harness:** readings taken through corroded wiring
read LOW, because the loads see less voltage than the new harness will deliver.
The measured figures are a floor, not a ceiling — the ×1.35 / ×1.10 / ×1.20
soft-fuse multipliers absorb exactly this. The right response to failing wiring
is to measure sooner, not to distrust the numbers.

### Voltage-drop testing — wiring or a dying part? (D-174)

The clamp cannot separate a weak motor from weak wiring — this can, and it is
now the primary old-harness diagnostic. Leads in: black in **COM**, red in
**V/Ω**. Dial to **V**, press SELECT until the small `DC` / ⎓ symbol shows.

1. **Reference first.** Red probe on the battery **+** post, black on the
   **−** post, with the circuit under test running. Write it down — say 13.8 V.
2. **At the load's feed.** Black probe on bare chassis metal — a clean
   unpainted bolt or bracket (scratch to shiny if needed). Red probe
   **backprobes** the feed terminal: slide the tip in along the wire from the
   back of the connector until it touches the terminal metal, connector still
   mated, circuit still running. Wiper example: engine running, wipers HIGH,
   wet glass, red probe backprobing the **LR terminal at D-02**.
3. **Ground side.** Red probe on the load's ground terminal (or the motor
   case), black on the battery **−** post. That reading IS the ground-path
   drop — no arithmetic.

**Reading it:** feed drop = step 1 − step 2.

- Feed + ground drop under **~0.8 V** → the wiring is fine; a slow motor is a
  dying motor → replacement list
- **1.5 V or more** → the wiring is eating it; the part may well be healthy
  and wakes up on the new harness
- Works on any doubtful circuit. Write the load-side voltage in the Volts
  column of the sheet

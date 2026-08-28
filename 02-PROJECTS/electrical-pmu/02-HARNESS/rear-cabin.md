# LEG 4 — REAR CABIN

**Boundary:** tunnel entry at the console, running back to the hatch, plus the
sill runs into both doors.
**Ground:** rear star node. Doors ground locally at the sill, not in the door.

---

## Rear body devices

| Device                     | OEM ref          | Direction | Est. A                    | Signal type                      |
|----------------------------|------------------|-----------|---------------------------|----------------------------------|
| Rear defog grid            | G-25             | Out       | 10–13                     | Resistive heater                 |
| Fuel pump                  | B-24             | Out       | 1–2 now / 8–12 Aeromotive | Power                            |
| Fuel level sender          | C-01             | In        | —                         | **Resistive** — V-037            |
| Tail / plate / marker      | F-04/07/08/14/15 | Out       | 3.0 LED                   | Power                            |
| Brake lamps                | F-07/F-08        | Out       | 0.6 LED                   | Power                            |
| Turn LEFT rear             | F-07             | Out       | 0.3 LED                   | Power                            |
| Turn RIGHT rear            | F-08             | Out       | 0.3 LED                   | Power                            |
| Reverse lamps              | F-07/F-08        | Out       | 0.6 LED                   | Power                            |
| Luggage compartment light  | H-11             | Out       | 0.15 LED                  | Power                            |
| Luggage light switch       | H-12             | In        | —                         | Closure                          |
| Hatch release solenoid     | H-14             | Out       | 3–5 momentary             | Solenoid                         |
| Fuel-door release solenoid | H-16             | Out       | 3–5 momentary             | Solenoid — **no channel, V-033** |
| Rear speakers              | G-09/G-10        | —         | —                         | Audio, independent               |

## Cabin devices

| Device                             | OEM ref | Direction | Est. A   | Signal type     |
|------------------------------------|---------|-----------|----------|-----------------|
| Interior & spot light              | H-06    | Out       | 0.15 LED | PWM bus         |
| Footwell / sill / console lighting | new     | Out       | ~0.5     | PWM bus         |
| Seat belt switch                   | H-04    | In        | —        | Closure         |
| Heated seats                       | new     | Out       | 4–5 each | Off comfort bus |

## Door devices — via sill

| Device                  | OEM ref | Direction | Est. A                | Signal type                          |
|-------------------------|---------|-----------|-----------------------|--------------------------------------|
| Window motor DRV        | I-09    | Out       | 4–6 run / 10–15 stall | Reversible, 2 legs                   |
| Window motor PASS       | I-11    | Out       | 4–6 run / 10–15 stall | Reversible, 2 legs                   |
| Door switch LH          | H-08    | In        | —                     | Closure to ground                    |
| Door switch RH          | H-07    | In        | —                     | Closure to ground                    |
| Heated mirror LH/RH     | new     | Out       | 1–2 each              | Off comfort bus                      |
| Remote mirror motors LH | I-03    | Out       | 1–2                   | 4 wires — **V-035 capacity problem** |
| Remote mirror motors RH | I-05    | Out       | 1–2                   | 4 wires                              |

## Devices deleted or pending

| Device              | OEM ref | Status                                        |
|---------------------|---------|-----------------------------------------------|
| Stop light checker  | F-03    | **Deleted** — PMU current sensing replaces it |
| Rear wiper motor    | D-05    | `[V-027]` no channel allocated                |
| Rear washer motor   | D-04    | `[V-027]`                                     |
| Power antenna motor | G-02    | `[V-031]`                                     |

## Leg totals

|                           | Value                                                     |
|---------------------------|-----------------------------------------------------------|
| Heavy conductors (12 AWG) | Defog, fuel pump, 4 window motor legs = 6                 |
| Medium (14 AWG)           | Tail bus, brake, hatch solenoid = 3                       |
| Light (16 AWG)            | Turn L, turn R, reverse, interior PWM, mirror heat ×2 = 6 |
| Signal (18 AWG)           | Fuel sender, door pins, luggage switch, +5 V ref = 4      |
| Est. peak draw            | ~30 A (defog + fuel pump + both windows)                  |
| Ground                    | Rear star node + sill node for doors                      |

## Optimization notes

**Fixing K-008 lives here.** Factory put the fuel pump ground and the rear turn
lamp grounds on the same X-15 stud. Separating those is the direct structural
fix. The fuel pump gets its own return to the rear node — not a shared one.

**Window motors are the wire-count driver**, same as the pop-ups up front, and
the same question applies: relays at the sill instead of the panel would trade
four 12 AWG runs for two plus control wires, in a much drier location than the
nose. `[Q-025]` — this one is more attractive than the nose version.

**The mirror capacity problem is real.** Remote mirror motors need 8 conductors
total. Add heated mirrors on top and this leg's door branch is oversubscribed.
Either the mirrors get a dedicated sub-branch at the sill, or manual mirrors free
the capacity for heat only. `[Q-022]`

**Doors are inside this leg by choice.** The sill run comes out with the interior;
the door boot is a service point, not a removal boundary. `[Q-023]` to override.

**Four devices have no channel:** rear wiper, rear washer, power antenna,
fuel-door solenoid. Most are probably already off the car — T-018 clears them all
in one inspection.

**The tunnel run is the longest in the car.** Voltage drop, not current, sets the
gauge on the defog and fuel pump legs.

---

## Connectors — REAR CABIN leg

Four housings. Longest run in the car, so voltage drop rather than ampacity sets
the gauge on the defog and fuel pump legs.

### L4-P1 · DTP06-4S → DP-L4-P1 · 12 AWG, size 12

| Cav | Circuit                            | Terminates at | PMU pin |
|-----|------------------------------------|---------------|---------|
| 1   | Rear defog grid                    | O4            | 13      |
| 2   | Fuel pump                          | O5            | 12      |
| 3   | SPARE heavy — in-tank pump upgrade | capped        | —       |
| 4   | SPARE heavy                        | capped        | —       |

### L4-P2 · DTP06-4S → DP-L4-P2 · 12 AWG, size 12

| Cav | Circuit             | Terminates at | PMU pin     |
|-----|---------------------|---------------|-------------|
| 1   | Window DRV — leg A  | K5/K6         | via O1 (38) |
| 2   | Window DRV — leg B  | K5/K6         | via O1 (38) |
| 3   | Window PASS — leg A | K7/K8         | via O1 (38) |
| 4   | Window PASS — leg B | K7/K8         | via O1 (38) |

### L4-M · DT06-12S → DP-L4-M · 14–16 AWG, size 16

| Cav | Circuit                      | Terminates at      | PMU pin |
|-----|------------------------------|--------------------|---------|
| 1   | Tail / plate / rear marker   | O6                 | 11      |
| 2   | Brake lamps                  | O7                 | 10      |
| 3   | Hatch release solenoid       | spare ch `[V-033]` | —       |
| 4   | Fuel-door release solenoid   | spare ch `[V-033]` | —       |
| 5   | Turn LEFT rear               | O17                | 6       |
| 6   | Turn RIGHT rear              | O18                | 33      |
| 7   | Reverse lamps                | O19                | 20      |
| 8   | Interior + details bus (PWM) | O20                | 34      |
| 9   | Heated mirror LH             | O15 via F11        | —       |
| 10  | Heated mirror RH             | O15 via F11        | —       |
| 11  | SPARE — third brake lamp     | capped             | —       |
| 12  | SPARE — rear wiper `[V-027]` | capped             | —       |

### L4-S · DT06-8S → DP-L4-S · 16 AWG, size 16

Upsized from 6-way to 8-way to carry the radar rear sensor link.

| Cav | Circuit                    | Terminates at       | PMU pin |
|-----|----------------------------|---------------------|---------|
| 1   | Fuel level sender          | A7                  | 32      |
| 2   | Door pin ladder            | A6                  | 18      |
| 3   | Luggage compartment switch | keypad or A6 ladder | —       |
| 4   | +5 V reference             | +5V out             | 15      |
| 5   | Radar — rear sensor link A | L3-S cav 11         | —       |
| 6   | Radar — rear sensor link B | L3-S cav 12         | —       |
| 7   | Radar — rear sensor link C | L3-S cav 27         | —       |
| 8   | SPARE — seat belt switch   | capped              | —       |

**Radar rear sensor** mounts at the hatch. Its link runs the full tunnel to the
dash module, passing straight through the box — the PMU does not touch it. Keep
it out of the L4-P1 bundle; it is a low-level signal and the defog and fuel pump
feeds are the two worst neighbours in this leg. `[V-048]` conductor count and
shielding are vendor-specific and unconfirmed.

**Routing note:** the fuel level sender in L4-S runs the full length of the tunnel
alongside the fuel pump feed in L4-P1. Separate housings means they can be
separated physically — do it. A resistive sender sharing a bundle with a pump
feed is the same class of mistake that produced K-008.

**Ground:** rear star node. **The fuel pump gets its own dedicated return** — not
shared with the rear lamps. That is the direct structural fix for K-008.

**Doors** branch off this leg at the sill with a local sill ground node.
The door boot is a service break, not a leg boundary `[Q-023]`.

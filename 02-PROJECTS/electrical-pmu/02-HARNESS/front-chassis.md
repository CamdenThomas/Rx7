# LEG 2 — FRONT CHASSIS

**Boundary:** firewall to radiator support, including the cowl.
Comes out with nose, bumper, and pop-up assemblies.
**Ground:** front star node. Includes the cowl-area returns.

---

## Devices

| Device                | OEM ref       | Direction | Est. A                | Signal type                    | Notes                                |
|-----------------------|---------------|-----------|-----------------------|--------------------------------|--------------------------------------|
| Headlight LOW         | E-08/E-09     | Out       | already LED           | Power                          | Was 40 W ×2                          |
| Headlight HIGH        | E-08/E-09     | Out       | already LED           | Power                          | Was 50 W ×2                          |
| Pop-up motor LH       | E-03          | Out       | 4–6 run / 15–25 stall | Reversible power ×2 legs       |                                      |
| Pop-up motor RH       | E-04          | Out       | 4–6 run / 15–25 stall | Reversible power ×2 legs       |                                      |
| Pop-up limit LH       | E-03 internal | In        | —                     | Ladder, 3 states               | **Inside the motor** — V-030         |
| Pop-up limit RH       | E-04 internal | In        | —                     | Ladder, 3 states               | Same                                 |
| Front turn LH         | F-05          | Out       | 0.3 LED               | Power                          | Was 27 W                             |
| Front turn RH         | F-06          | Out       | 0.3 LED               | Power                          | Was 27 W                             |
| Front parking LH/RH   | F-05/F-06     | Out       | 0.6 LED               | Power                          | Was 8 W ×2                           |
| Front side marker LH  | F-12          | Out       | 0.3 LED               | Power                          | Was 3.8 W                            |
| Front side marker RH  | F-13          | Out       | 0.3 LED               | Power                          | Was 3.8 W                            |
| Horn LH               | F-09          | Out       | 2–4                   | Power                          | Single-wire, needs a real ground now |
| Horn RH               | F-10          | Out       | 2–4                   | Power                          | Single-wire                          |
| **Front wiper motor** | D-02          | Out       | 3–6 run / 12–20 stall | 2-speed + internal park switch | Cowl                                 |
| Front washer pump     | D-01          | Out       | 3–5                   | Power                          | Cowl                                 |
| Wiper park sense      | D-02 internal | In        | —                     | Closure                        | For correct stop position            |

## Devices deleted or pending

| Device                  | OEM ref | Status                                    |
|-------------------------|---------|-------------------------------------------|
| Horn relay              | F-16    | **Deleted** — PMU switches horns directly |
| Headlight cleaner motor | E-11    | **Confirmed gone** *(D-097)*              |
| Headlights LOW / HIGH | E-08/09 | **Not the final part.** Moving to a thin LED strip per side `[Q-044]` — may delete the pop-ups entirely |

## Leg totals

|                           | Value                                             |
|---------------------------|---------------------------------------------------|
| Heavy conductors (12 AWG) | 2 headlight + 4 pop-up motor legs = 6             |
| Medium (14 AWG)           | Wiper LO, wiper HI, horn, washer = 4              |
| Light (16 AWG)            | Turn L, turn R, park/marker = 3                   |
| Signal (18 AWG)           | Pop-up limits ×2, wiper park, +5 V ref = 4        |
| Est. peak draw            | ~35 A (both pop-ups moving + wipers + headlights) |
| Ground                    | Front star node                                   |

## Optimization notes

**Pop-up motors dominate this leg.** Four heavy conductors for two motors, and
the reversing happens back at the panel relay bank. That is the single biggest
wire-count driver in the whole car and it is unavoidable with H-bridge reversing.

**Worth questioning:** relays at the *nose* instead of the panel would cut four
12 AWG runs down to two plus two control wires. The cost is relays living in the
wettest, hottest part of the car. Logged `[Q-024]` — this is a real trade, not
an obvious call.

**The cowl belongs here, not with the engine.** Wiper motor and washer pump come
off with nose work. Grouping them with the engine leg would mean two legs
disturbing each other for a wiper job.

**Lighting current collapsed.** Every lamp in this leg except the headlights is
now under 0.5 A. The 14 and 16 AWG sizes are set by voltage drop over a ~12 ft
run and by crimp robustness, not by ampacity.

**Horns need a deliberate ground.** Factory grounded them through the mounting
bracket. Both go to the front star node now.

---

## Connectors — FRONT CHASSIS leg

Four housings. The pop-up motors force two DTP shells; DTP is only made in 2- and
4-way.

### L2-P1 · DTP06-4S → DP-L2-P1 · 12 AWG, size 12

| Cav | Circuit           | Terminates at | PMU pin     |
|-----|-------------------|---------------|-------------|
| 1   | Headlight LOW     | O2            | 39          |
| 2   | Headlight HIGH    | O3            | 26          |
| 3   | Pop-up LH — leg A | K1/K2         | via O1 (38) |
| 4   | Pop-up LH — leg B | K1/K2         | via O1 (38) |

### L2-P2 · DTP06-4S → DP-L2-P2 · 12 AWG, size 12

| Cav | Circuit           | Terminates at | PMU pin     |
|-----|-------------------|---------------|-------------|
| 1   | Pop-up RH — leg A | K3/K4         | via O1 (38) |
| 2   | Pop-up RH — leg B | K3/K4         | via O1 (38) |
| 3   | SPARE heavy       | capped        | —           |
| 4   | SPARE heavy       | capped        | —           |

### L2-M · DT06-8S → DP-L2-M · 14–16 AWG, size 16

| Cav | Circuit                          | Terminates at         | PMU pin |
|-----|----------------------------------|-----------------------|---------|
| 1   | Wiper LOW                        | O8 (braking)          | 9       |
| 2   | Wiper HIGH                       | O9                    | 5       |
| 3   | Horn — both, spliced at the nose | O11                   | 3       |
| 4   | Washer pump                      | O10 / spare `[Q-016]` | 4       |
| 5   | Turn LEFT front                  | O17                   | 6       |
| 6   | Turn RIGHT front                 | O18                   | 33      |
| 7   | Front park / side marker         | O6                    | 11      |
| 8   | SPARE — cornering lamp           | capped                | —       |

### L2-S · DT06-6S → DP-L2-S · 16 AWG, size 16

| Cav | Circuit                     | Terminates at | PMU pin |
|-----|-----------------------------|---------------|---------|
| 1   | Pop-up LH position ladder   | A4            | 17      |
| 2   | Pop-up RH position ladder   | A5            | 31      |
| 3   | Wiper park sense            | A9–A16 spare  | —       |
| 4   | +5 V reference              | +5V out       | 15      |
| 5   | SPARE — ambient temp sensor | capped        | —       |
| 6   | SPARE                       | capped        | —       |

**Routing note:** L2-S carries the two ladder references and the +5 V supply.
Keep it out of the L2-P1/P2 bundle — pop-up motor legs are the noisiest
conductors in the nose and the ladders are the most noise-sensitive.

**Ground:** front star node. Both horns ground there rather than through their
brackets.

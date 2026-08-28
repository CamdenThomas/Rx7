# PIN MAP — four leg connectors into the black box

One connector per leg. Everything inside the box — PMU, 11 relays, 13 fuses,
busbars, diode network — is the hub; the legs plug into it.

Verified against `01-REFERENCE/PMU-24_Pinout_v1.0.pdf`.

---

## Terminal selection (from the pinout doc)

| Terminal     | Part         | Wire range    | Used for             |
|--------------|--------------|---------------|----------------------|
| 2.8 mm large | 211CC3S3120  | **10–12 AWG** | 25 A outputs         |
| 2.8 mm       | 211CC3S2120  | **14–16 AWG** | 15 A and 7 A outputs |
| 1.5 mm       | 211CC2S2160P | **13–17 AWG** | Inputs, CAN, +5 V    |

`[V-012 resolved]` The 1.5 mm terminal is 13–17 AWG, so **signal wire is 16 AWG,
not 18**. SPEC currently says 18 AWG on every input — that is below the terminal's
range and will crimp badly. Logged as `D-027`.

## Input capability — the two banks are not the same

| Bank   | Resolution | Range      | Max input | Pull options                    |
|--------|------------|------------|-----------|---------------------------------|
| A1–A8  | 10-bit     | 0–5 V      | 20 V      | 1 MΩ down, 10 kΩ down, 10 kΩ up |
| A9–A16 | **12-bit** | **0–20 V** | 30 V      | same                            |

A9–A16 are better inputs in every respect. That reinforces putting the two
12 V-side ladders (key, headlight switch) there — and means any *precision*
analog signal wants A9–A16 too, not A1–A8.

---

## The black box — 11 relays

| #   | Relay                   | Coil driven by       | Switches                   | Notes                                         |
|-----|-------------------------|----------------------|----------------------------|-----------------------------------------------|
| K1  | Pop-up LH — direction A | Wink/raise logic     | O1 motor bus               | H-bridge half                                 |
| K2  | Pop-up LH — direction B | Wink/lower logic     | O1 motor bus               | H-bridge half                                 |
| K3  | Pop-up RH — direction A | Wink/raise logic     | O1 motor bus               | H-bridge half                                 |
| K4  | Pop-up RH — direction B | Wink/lower logic     | O1 motor bus               | H-bridge half                                 |
| K5  | Window DRV — up         | Dash switch          | O1 motor bus               | H-bridge half                                 |
| K6  | Window DRV — down       | Dash switch          | O1 motor bus               | H-bridge half                                 |
| K7  | Window PASS — up        | Dash switch          | O1 motor bus               | H-bridge half                                 |
| K8  | Window PASS — down      | Dash switch          | O1 motor bus               | H-bridge half                                 |
| K9  | Start relay             | **O21**              | Battery → starter solenoid | **Mounts at the starter, not in the box**     |
| K10 | A/C compressor clutch   | Factory switch chain | Battery → magnet clutch    | Factory circuit, untouched (D-012)            |
| K11 | Constant-bus master     | O22 keep-alive latch | Busbar → constant loads    | Lets the box drop true-constants on long park |

Eight of eleven are the four H-bridges. That is the cost of reversing two pop-ups
and two windows at the panel.

## The black box — 13 fuses

| #   | Fuse | Feeds                           | Off              |
|-----|------|---------------------------------|------------------|
| F1  | 15 A | Head unit constant keep-alive   | Busbar (not PMU) |
| F2  | 2 A  | Diagnostic port +12 V           | Busbar           |
| F3  | 5 A  | PMU wake / diode-OR network     | Busbar           |
| F4  | 10 A | A/C factory circuit             | Busbar           |
| F5  | 30 A | Amp / audio constant            | Busbar           |
| F6  | 10 A | Pop-up motor bus — LH branch    | O1 downstream    |
| F7  | 10 A | Pop-up motor bus — RH branch    | O1 downstream    |
| F8  | 15 A | Window motor bus — DRV branch   | O1 downstream    |
| F9  | 15 A | Window motor bus — PASS branch  | O1 downstream    |
| F10 | 10 A | Comfort bus — heated seats      | O15 downstream   |
| F11 | 5 A  | Comfort bus — mirrors + nozzles | O15 downstream   |
| F12 | 5 A  | Interior lighting branch        | O20 downstream   |
| F13 | —    | Spare                           | —                |

Fuses F6–F12 are **downstream branch protection** — the PMU soft fuse protects
the channel, these protect each individual leg off a shared bus.

---

## L1 — ENGINE connector

| Cav   | Circuit                            | Terminates at             | PMU pin | AWG         |
|-------|------------------------------------|---------------------------|---------|-------------|
| 1     | Ignition / coil feed               | **O12**                   | 2       | 12          |
| 2     | RESERVED — LS ECU + injectors      | **O13**                   | 1       | 12          |
| 3     | RESERVED — LS cooling fan          | **O14**                   | 14      | 12          |
| 4     | SPARE heavy                        | — capped                  | —       | 12          |
| 5     | Start relay coil → K9 at starter   | **O21**                   | 21      | 16          |
| 6     | Alternator lamp / sense            | C1 spare                  | —       | 16          |
| 7     | Water temp sender                  | cluster now               | —       | 16          |
| 8     | Oil pressure sender                | cluster now               | —       | 16          |
| 9     | Brake fluid level                  | cluster now               | —       | 16          |
| 10    | Oil level sensor                   | cluster now               | —       | 16          |
| 11    | Coolant level sensor               | cluster now               | —       | 16          |
| 12    | Inhibitor switch — crank interlock | **A9/O17 bank** `[Q-019]` | —       | 16          |
| 13    | Wideband O2 signal                 | spare, capped             | —       | 16          |
| 14    | **Tach pickup (YG)**               | spare, capped             | —       | 16 shielded |
| 15    | +5 V reference                     | **+5V out**               | 15      | 16          |
| 16    | CAN2 H                             | **CAN2H**                 | 24      | 16 tw       |
| 17    | CAN2 L                             | **CAN2L**                 | 37      | 16 tw       |
| 18–20 | SPARE ×3                           | capped                    | —       | 16          |

Ground: block star node, local. Does not cross the firewall.

## L2 — FRONT CHASSIS connector

| Cav   | Circuit                      | Terminates at              | PMU pin     | AWG |
|-------|------------------------------|----------------------------|-------------|-----|
| 1     | Headlight LOW                | **O2**                     | 39          | 12  |
| 2     | Headlight HIGH               | **O3**                     | 26          | 12  |
| 3     | Pop-up LH — leg A            | **K1/K2**                  | via O1 (38) | 12  |
| 4     | Pop-up LH — leg B            | **K1/K2**                  | via O1 (38) | 12  |
| 5     | Pop-up RH — leg A            | **K3/K4**                  | via O1 (38) | 12  |
| 6     | Pop-up RH — leg B            | **K3/K4**                  | via O1 (38) | 12  |
| 7     | SPARE heavy                  | capped                     | —           | 12  |
| 8     | Wiper LOW                    | **O8** (braking)           | 9           | 14  |
| 9     | Wiper HIGH                   | **O9**                     | 5           | 14  |
| 10    | Horn (both, spliced at nose) | **O11**                    | 3           | 14  |
| 11    | Washer pump                  | **O10** or spare `[Q-016]` | 4           | 14  |
| 12    | Turn LEFT front              | **O17**                    | 6           | 16  |
| 13    | Turn RIGHT front             | **O18**                    | 33          | 16  |
| 14    | Front park / side marker     | **O6**                     | 11          | 16  |
| 15    | Pop-up LH position ladder    | **A4**                     | 17          | 16  |
| 16    | Pop-up RH position ladder    | **A5**                     | 31          | 16  |
| 17    | Wiper park sense             | **A9/O17 bank** spare      | —           | 16  |
| 18    | +5 V reference               | **+5V out**                | 15          | 16  |
| 19–21 | SPARE ×3                     | capped                     | —           | 16  |

Ground: front star node.

## L3 — DASH connector

| Cav   | Circuit                                    | Terminates at            | PMU pin | AWG   |
|-------|--------------------------------------------|--------------------------|---------|-------|
| 1     | Blower motor feed                          | **O16** ⚡                | 28      | 12    |
| 2     | Comfort bus                                | **O15**                  | 27      | 12    |
| 3     | Accessory bus — lighter, USB, head unit sw | **O10**                  | 4       | 14    |
| 4     | Head unit CONSTANT                         | **F1 busbar**            | —       | 14    |
| 5     | Key position ladder                        | **A16** (12-bit, 0–20 V) | 22      | 16    |
| 6     | Headlight switch ladder                    | **A15** (12-bit, 0–20 V) | 35      | 16    |
| 7     | Turn stalk ladder                          | **A1**                   | 29      | 16    |
| 8     | Wiper stalk ladder                         | **A2**                   | 16      | 16    |
| 9     | Brake pedal switch                         | **A3**                   | 30      | 16    |
| 10    | Hazard switch                              | **A8** + diode → pin 7   | 19      | 16    |
| 11    | +5 V reference                             | **+5V out**              | 15      | 16    |
| 12    | Illumination / dimmer feed                 | **O20** branch           | 34      | 16    |
| 13    | Wink switch LEFT                           | **K1/K2 coils**          | —       | 16    |
| 14    | Wink switch RIGHT                          | **K3/K4 coils**          | —       | 16    |
| 15    | Radar — rear sensor link (3 cond.)         | pass-through → L4-S      | —       | 16    |
| 16    | Radar detector +12 V sw / ground           | **O10 via F13** / DP-GND | 4       | 16    |
| 17    | Window DRV up                              | **K5 coil**              | —       | 16    |
| 18    | Window DRV down                            | **K6 coil**              | —       | 16    |
| 19    | Window PASS up                             | **K7 coil**              | —       | 16    |
| 20    | Window PASS down                           | **K8 coil**              | —       | 16    |
| 21    | CAN2 H — keypad, future DCU                | **CAN2H**                | 24      | 16 tw |
| 22    | CAN2 L — keypad, future DCU                | **CAN2L**                | 37      | 16 tw |
| 23    | CAN1 H — diagnostic port                   | **CAN1H**                | 23      | 16 tw |
| 24    | CAN1 L — diagnostic port                   | **CAN1L**                | 36      | 16 tw |
| 25    | Diag port +12 V                            | **F2 busbar**            | —       | 16    |
| 26–30 | SPARE ×5 — DCU, cluster, A/C controller    | capped                   | —       | 16    |

Ground: dash star node. Horn switch, parking brake, glove box switch, hatch and
fuel-door buttons all move to the **CAN keypad** — see optimization note below.

## L4 — REAR CABIN connector

| Cav   | Circuit                                                  | Terminates at                | PMU pin     | AWG |
|-------|----------------------------------------------------------|------------------------------|-------------|-----|
| 1     | Rear defog grid                                          | **O4**                       | 13          | 12  |
| 2     | Fuel pump                                                | **O5**                       | 12          | 12  |
| 3     | Window DRV — leg A                                       | **K5/K6**                    | via O1 (38) | 12  |
| 4     | Window DRV — leg B                                       | **K5/K6**                    | via O1 (38) | 12  |
| 5     | Window PASS — leg A                                      | **K7/K8**                    | via O1 (38) | 12  |
| 6     | Window PASS — leg B                                      | **K7/K8**                    | via O1 (38) | 12  |
| 7     | SPARE heavy — in-tank pump upgrade                       | capped                       | —           | 12  |
| 8     | Tail / plate / rear marker                               | **O6**                       | 11          | 14  |
| 9     | Brake lamps                                              | **O7**                       | 10          | 14  |
| 10    | Hatch release solenoid                                   | **F13 / spare ch** `[V-033]` | —           | 14  |
| 11    | Fuel-door release solenoid                               | **no channel** `[V-033]`     | —           | 14  |
| 12    | Turn LEFT rear                                           | **O17**                      | 6           | 16  |
| 13    | Turn RIGHT rear                                          | **O18**                      | 33          | 16  |
| 14    | Reverse lamps                                            | **O19**                      | 20          | 16  |
| 15    | Interior + details bus (PWM)                             | **O20**                      | 34          | 16  |
| 16    | Heated mirror LH                                         | **O15** via F11              | —           | 16  |
| 17    | Heated mirror RH                                         | **O15** via F11              | —           | 16  |
| 18    | Fuel level sender                                        | **A7**                       | 32          | 16  |
| 19    | Door pin ladder                                          | **A6**                       | 18          | 16  |
| 20    | Luggage compartment switch                               | keypad or A6 ladder          | —           | 16  |
| 21    | +5 V reference                                           | **+5V out**                  | 15          | 16  |
| 22–25 | SPARE ×4 — mirror motors `[Q-022]`, rear wiper `[V-027]` | capped                       | —           | 16  |

Ground: rear star node + sill node for doors.

---

## Pins that feed two legs

One PMU pin, two connector cavities, split at the busbar inside the box:

| Pin | Ch                  | L2 cavity     | L4 cavity      |
|-----|---------------------|---------------|----------------|
| 11  | O6 tail/park/marker | 14            | 8              |
| 6   | O17 turn LEFT       | 12            | 12             |
| 33  | O18 turn RIGHT      | 13            | 13             |
| 38  | O1 motor bus        | 3–6 via K1–K4 | 3–6 via K5–K8  |
| 15  | +5 V ref            | 18            | 21             |
| 34  | O20                 | —             | 15 + L3 cav 12 |

## Connector sizing

| Leg       | Cavities used | Heavy (12 AWG) | Buy at                      |
|-----------|---------------|----------------|-----------------------------|
| L1 Engine | 20            | 4              | 4-way heavy + 16-way signal |
| L2 Front  | 21            | 7              | 8-way heavy + 14-way signal |
| L3 Dash   | 30            | 2              | 2-way heavy + 28-way signal |
| L4 Rear   | 25            | 7              | 8-way heavy + 18-way signal |

## Optimization notes

**The dash leg is 28 signals and 2 power.** No standard sealed heavy connector
suits it. This is where a high-cavity signal connector earns its place, with a
small separate heavy plug alongside.

**Five dash buttons moved to the CAN keypad** — horn, parking brake sense, glove
box, hatch, fuel door. That is how L3 fits at all, and it resolves `Q-018`
without consuming a PMU pin. The horn switch on a keypad is a real behavior
change though: no horn if the PMU is asleep. Flagged `Q-026`.

**O1 never leaves the box directly.** It feeds the relay bank; only switched
motor legs go out. All eight H-bridge outputs are downstream of one pin.

**16 AWG everywhere on signals**, not 18 — forced by the 1.5 mm terminal's
13–17 AWG range. This is a real change to SPEC and to the wire order.

---

## UPDATE 2026-08 — L4 revised, modules added

`[D-065/066]` **L4-P2 is deleted.** Window motor legs no longer cross the tunnel.

### L4-P · DTP06-4S — revised

| Cav | Circuit | Terminates at | PMU pin |
|---|---|---|---|
| 1 | Rear defog grid | O4 | 13 |
| 2 | Fuel pump | O5 | 12 |
| 3 | **Window motor bus feed → sill** | O1 via K5–K8 at the sill | 38 |
| 4 | SPARE heavy — in-tank pump upgrade | capped | — |

### L4-M · DT06-12S — revised

| Cav | Circuit | Terminates at | PMU pin |
|---|---|---|---|
| 1 | Tail / plate / rear marker | O6 | 11 |
| 2 | Brake lamps | O7 | 10 |
| 3 | Hatch release solenoid | spare ch `[V-033]` | — |
| 4 | Fuel-door release solenoid | spare ch `[V-033]` | — |
| 5 | Turn LEFT rear | O17 | 6 |
| 6 | Turn RIGHT rear | O18 | 33 |
| 7 | Reverse lamps | O19 | 20 |
| 8 | Interior + details bus (PWM) | O20 | 34 |
| 9 | **Window DRV up command** | K5 coil at the sill | — |
| 10 | **Window DRV down command** | K6 coil at the sill | — |
| 11 | **Window PASS up command** | K7 coil at the sill | — |
| 12 | **Window PASS down command** | K8 coil at the sill | — |

Heated mirror feeds move to the **sill node**, off the O15 comfort branch —
see `sill-node.md`.

### Module connectors at the dash post

| Code | Housing | Cav | Carries |
|---|---|---|---|
| **DP-ICU** | DT06-12S | 12 (11 used) | Power, GND, CAN2, illumination ref, **6 engine sensor inputs** |
| **DP-DCU** | DT06-6S | 6 (5 used) | Power, GND, CAN2 |

Sensor wires route **L1-S → dash post → DP-ICU**. The PMU never sees them —
it has no spare analog inputs (D-076).

### Running total

| Group | Count |
|---|---|
| Leg connectors | 14 |
| Sill door sub-connectors | 2 |
| Dash post drops (DIAG, KEY, ICU, DCU) | 4 |
| Lugs | 2 |
| PMU device connector | 1 |
| **Total mated pairs** | **23** |

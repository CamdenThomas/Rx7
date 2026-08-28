# DCU & DIGITAL CLUSTER — full scope

**Supersedes D-006.** The DCU and digital gauge cluster are no longer deferred.
They are in scope, in the pin plan, and in the wiring.

---

## 1 · Why this changes the architecture

Four decisions already lean on the DCU existing:

| Decision | Depends on the DCU |
|---|---|
| D-073 | Comfort bus switching and the heat/cool interlock |
| D-012 | A/C controls eventually moving off the factory switch |
| D-031 / Q-028 | Horn and wink over CAN wake |
| D-006 | Cluster replacement |

It had become load-bearing while nominally deferred. Making it explicit removes
that risk.

### The finding that forces the design

**The PMU has no spare analog inputs.** All eight A1–A8 and all eight A9–A16 are
allocated. Water temp, oil pressure, oil temperature, VSS and tach therefore
**cannot be read by the PMU** — there is no pin left for them.

The C1/L1-S "sensor spares" are capped wires with no destination. They were
always going to need a reader.

**That reader is the ICU** — the same box that draws the gauges. See §2.

---

## 2 · Two nodes — corrected split

> **Correction, 2026-08.** The first draft of this file gave sensor acquisition
> to the DCU while claiming the ICU was failure-isolated from it. That was
> contradictory: a DCU fault would have left a working display with no data.
> **Sensor acquisition belongs to the ICU**, in the same failure domain as the
> gauges it feeds.

| Node | Owns | Fails how |
|---|---|---|
| **ICU** | Instrument display **and the engine sensors that feed it** — tach, water temp, oil pressure, oil temp, VSS | Cluster goes dark. Nothing else is affected |
| **DCU** | Climate, HVAC servos, comfort bus switching | Climate stops. **Gauges keep working** |

**The principle:** a gauge's sender wires into the box that draws the gauge.
Sender → ADC → pixel, no bus hop, no second processor, no shared failure.

### What this buys

| Failure | Consequence |
|---|---|
| DCU dies | No climate control. Tach, temp, oil pressure all normal |
| ICU dies | Cluster dark. Car runs, climate works, PMU unaffected |
| CAN2 drops entirely | **ICU still shows tach, water temp, oil pressure, oil temp, speed** from its own inputs. Only fuel level and voltage degrade |
| PMU sleeps or faults | Everything downstream is off anyway — nothing to protect |

That third row is the important one. The gauges you actually need while driving
have **zero bus dependency**. CAN carries only the two values the PMU already
measures better than a second sensor would.

`[Q-035]` — one board or two? Two remains the recommendation, but the argument is
now cleaner: it is not "isolate the display from climate," it is **"isolate the
engine instrumentation from the comfort system."**
> two boards for sure
---

## 3 · CAN2 bus — now five nodes

| Node | Role | Termination |
|---|---|---|
| PMU-24 DL | Publishes outputs, currents, fuel level, voltage, key state | Software-controlled |
| CAN keypad | Buttons in | — |
| **DCU** | Publishes engine sensors, consumes comfort commands | — |
| **ICU** | Consumes everything, displays | — |
| LS ECU | Future | **120 Ω at this end** |

**Bus design rules:**
- 120 Ω at exactly two points — the PMU (software) and the physical far end.
- The far end is the engine-bay drop at L1-S, reserved for the LS ECU. Fit the
  resistor there now, capped, so the bus is correct before the ECU exists.
- Keep every drop short. Stubs off a linear backbone, not a star.
- `[Q-036]` — CAN2 speed. 500 kbps is the sane default and leaves headroom.

---

## 4 · DCU hardware

| Item              | Spec                                            | Note                                                                    |
|-------------------|-------------------------------------------------|-------------------------------------------------------------------------|
| MCU               | Teensy 4.1, or STM32G4                          | Teensy has 3 CAN controllers on-chip, plenty of ADC, and good libraries |
| CAN transceiver   | TJA1051 or MCP2562                              | One per CAN interface                                                   |
| Analog front end  | Dividers + RC filters + clamp diodes per sensor | **Every input needs transient protection**                              |
| Tach conditioning | Opto-isolator or comparator                     | Coil primary spikes well above 12 V — see V-041                         |
| Servo drivers     | 3–4 channels                                    | HVAC blend, mode, recirc doors                                          |
| Comfort switching | 5–6 MOSFET or relay channels                    | Seats, mirrors, nozzles, de-icer off O15                                |
| Power             | 12 V → 5 V buck, with load-dump protection      | Automotive-grade, not a bench regulator                                 |

## 5 · ICU hardware

| Item | Spec | Note |
|---|---|---|
| MCU | Teensy 4.1 or RP2040 | Display bandwidth is the driver |
| Display | `[Q-037]` — round TFTs for a retro pair, or one wide TFT | Decides bezel fabrication |
| Backlight dimming | PWM, referenced to the PMU's O20 illumination level over CAN | Matches panel dimming automatically |
| CAN transceiver | 1 | |
| Power | 12 V → 5 V buck | |

---

## 6 · Signals the ICU acquires

These are the wires that had no reader. They route from `L1-S` through the dash
post to the **ICU** — the box that draws the gauge, not the climate module.

| Signal | Type | Conditioning |
|---|---|---|
| Water temp | Resistive sender | Divider vs a known pull-up |
| Oil pressure | Resistive sender | Divider |
| Oil temperature | Resistive sender `[new]` | Divider |
| Tachometer | Coil primary pulse, >12 V spikes | **Opto or comparator. Never raw to an ADC** |
| VSS | Pulse | Schmitt input |
| Alternator sense | Lamp-driven | Divider |
| Fuel level | — | **Read by the PMU on A7**, published over CAN |
| Battery voltage | — | **PMU publishes it.** Do not duplicate |
| Coolant level | Closure | Direct to ICU |
| Brake fluid level | Closure | Direct to ICU |

**The rule:** if the PMU already measures it, the ICU reads it from CAN. Only
signals the PMU cannot see get a dedicated ICU input.

**The corollary that matters:** the ICU's critical gauges — tach, water temp,
oil pressure, oil temp, speed — are all on its own inputs. **If CAN2 fails
completely, those still work.** Only fuel level and voltage go blank, and neither
will strand you.

---

## 7 · New connectors at the dash post

| Code | What | Housing | Cav | Used |
|---|---|---|---|---|
| **DP-ICU** | Cluster power, CAN, **all engine sensor inputs**, dimming | DT06-12S | 12 | 11 |
| **DP-DCU** | DCU power, CAN | DT06-6S | 6 | 5 |

### DP-ICU — the instrumentation connector

| Cav | Circuit | Source |
|---|---|---|
| 1 | +12 V switched | O10 accessory bus |
| 2 | Ground | DP-GND |
| 3 | CAN2 H | Pin 24 |
| 4 | CAN2 L | Pin 37 |
| 5 | Illumination level reference | O20 branch |
| 6 | Water temp sender | L1-S |
| 7 | Oil pressure sender | L1-S |
| 8 | Oil temperature sender | L1-S |
| 9 | Tach, conditioned — **shielded** | L1-S |
| 10 | VSS | L1-S |
| 11 | Alternator sense | L1-S |
| 12 | SPARE | — |

### DP-DCU — climate only

| Cav | Circuit | Source |
|---|---|---|
| 1 | +12 V switched | O10 accessory bus |
| 2 | +12 V constant, fused | Busbar F13 |
| 3 | Ground | DP-GND |
| 4 | CAN2 H | Pin 24 |
| 5 | CAN2 L | Pin 37 |
| 6 | SPARE | — |

The DCU also takes a **short heavy lead off O15** at the plate for the comfort
bus it switches, and drives the HVAC servos locally — the heater box is inches
away. Neither crosses a leg.

**Both modules mount in the dash, inches from the post.** Short runs, no leg
involvement.

---

## 8 · Power budget problem

`[Q-038]` **O10 is now oversubscribed.**

| Load | A |
|---|---|
| Cigarette lighter | 8–10 while heating |
| USB-C ports | 3 per port |
| Head unit, switched | 2–5 |
| DCU logic | 0.3–0.5 |
| ICU + backlight | 0.5–1.5 |
| **Worst case** | **~20 A on a 15 A channel** |

Three ways out:

| Option | Effect |
|---|---|
| **A** — Delete the cigarette lighter | Frees 8–10 A instantly. With USB-C fitted, what is it for? |
| **B** — Move DCU/ICU to the O15 comfort bus | O15 has headroom, but ties module power to the comfort circuit |
| **C** — Accept it and let the soft fuse manage | The lighter is intermittent, but a trip blanks your cluster |

**Recommendation: A.** The lighter is the only load here that does not earn its
place, and option C means a cigarette lighter can turn off your instruments.

HVAC servos and comfort loads stay on **O15**, switched by the DCU — they are not
part of this budget.

---

## 9 · What this adds to the build

| Phase | Addition | Hrs |
|---|---|---|
| 0 | DCU/ICU schematic, CAN message map, sensor scaling | 25–40 |
| 1 | Order MCUs, transceivers, displays, servos, passives | 3 |
| 2 | Bench-bring-up both nodes on the mule alongside the PMU | 40–70 |
| 2 | Firmware — CAN, sensor acquisition, display, climate logic | 80–200 |
| 4 | DP-DCU and DP-ICU on the plate | 4 |
| 5 | Dash module harness | 8–12 |
| 6 | Install, calibrate senders, tune the display | 20–35 |
| 8 | Shakedown — sensor accuracy, display legibility at night | 10–15 |

**Total: 190–380 hrs.** Roughly doubles the project.

## 10 · What this adds to the BOM

| Item | ~$ |
|---|---|
| 2 × Teensy 4.1 or STM32 dev boards | 60–100 |
| CAN transceivers, passives, protection | 40–70 |
| Display(s) | 60–200 |
| HVAC servos ×4 | 60–120 |
| Oil temp sender + VSS | 60–120 |
| Custom PCBs, 2 revisions | 100–250 |
| Enclosures, bezel fabrication | 80–200 |
| Connectors DP-DCU + DP-ICU | 40–60 |
| **Total** | **500–1,120** |

---

## 11 · The sequencing rule that must not break

**The car drives fully on the PMU with dumb switches before either module is
connected.** Checklist Phase 6 completes, the factory harness comes out, and the
car is finished. Only then do the DCU and ICU join.

The DCU and ICU add capability to a working car. They are never a dependency for
it starting, running, or being legal. Every decision in this file preserves that.

`[Q-039]` — does the factory cluster stay in place as a fallback during ICU
development, or come out at Phase 6? Keeping it means a working tach while the
firmware is half-written.

---

# 12 · MCU selection

## The recommendation: Teensy 4.1 for both nodes

Same board in both boxes. For a solo builder that is worth more than optimising
each node separately:

- **One toolchain, one library set, one set of gotchas learned once.**
- **A spare board is a spare for either node.** Buy three, always have a swap.
- **Shared code** — CAN stack, sensor scaling, fault handling, logging all
  written once and used twice.
- If one node's firmware outgrows the other, nothing has to be re-selected.

At roughly $32 each it is overkill for the DCU. Buy the overkill.

## Why the 4.1 specifically

| Feature | Why it matters here |
|---|---|
| **3 CAN controllers on-chip** | (cite index="72-1">CAN1, CAN2 and CAN3, with CAN-FD on CAN3</cite>. No external controller needed |
| 600 MHz Cortex-M7 | Drives a TFT at a real frame rate without tricks |
| 18 analog inputs | ICU needs 6 sensors plus headroom |
| Hardware timers with input capture | Tach and VSS pulse measurement done properly, not by polling |
| **microSD slot** | Config storage, and a datalogger you get for free |
| PSRAM pads | Display framebuffer if you go large |
| Arduino ecosystem | Display and CAN libraries already exist and are mature |

**Libraries:** (cite index="72-1">ACAN-T4 supports CAN1, CAN2, CAN2.0 and CAN-FD on CAN3</cite>,
and FlexCAN_T4 is the other mature option. Both are actively used and documented.

## The honest objection

**Teensy is not automotive-qualified.** The i.MX RT1062 is a commercial-temp
part, and a dash cavity in a Colorado summer gets hot. Two mitigations:

1. Mount both modules **behind the dash face, not against the windscreen** —
   ambient, not solar-loaded.
2. Design the carrier PCB with a **socketed Teensy**. If a board dies from heat,
   you swap a $32 module instead of rebuilding an assembly.

The alternative — an STM32G4 or H7 on a custom automotive-grade board — is the
right answer for a production part and the wrong answer for a first build you
need to finish. `[Q-040]` if you want to revisit this.

---

# 13 · CAN transceivers and bus design

## Transceiver

**TI TCAN1042 or TCAN1051** (automotive-qualified variants). `[V-057]` confirm
the exact part suffix before ordering.

| Why not | |
|---|---|
| SN65HVD230 | 3.3 V only, weak bus fault protection. Fine on a bench, marginal in a car |
| MCP2551 | 5 V logic — needs level shifting to Teensy's 3.3 V |
| MCP2515 | It's a *controller* plus transceiver. Redundant, the Teensy already has three controllers |

The TCAN family has a **VIO pin** so the logic side runs at 3.3 V natively while
the bus side runs at 5 V, plus bus fault protection well beyond ±12 V. That is
the difference between a bench project and something that survives a short to
battery.

## Bus topology

```
   ENGINE BAY                    DASH  (all four nodes within inches)
        │                              │
   [LS ECU drop]                  [PMU] [KEYPAD] [DCU] [ICU]
        │                              │
       120 Ω  ────── twisted pair ─────┴── PMU software termination
    (fit now, capped)
```

**Termination: exactly two points.**
- PMU software termination at the dash end (CAN2 supports it).
- A physical **120 Ω at the engine-bay drop** — fit it now, capped, so the bus
  is electrically correct before the LS ECU exists.

**The dash is electrically one node point.** Four devices within a few inches is
not four stubs — it is a cluster. Keep each drop under ~30 cm and it behaves as
a single point on the backbone.

**Wire:** twisted pair, 16 AWG to match the rest of the harness, roughly 33–40
twists per metre. Route away from the pop-up motor legs and the coil feed.

## Speed and protocol

**500 kbps, CAN 2.0B, 11-bit identifiers.**

The PMU is CAN 2.0 only, so the shared bus cannot be FD regardless of what the
Teensys can do. 500 kbps is standard, tolerant of the run length, and leaves
enormous headroom for five nodes exchanging gauge data at 10–50 Hz.

## The spare link worth wiring now

Both Teensys have three CAN controllers and the vehicle bus only uses one.

**Wire a second twisted pair between the DCU and ICU, capped at both ends.**
It costs two conductors inside the dash and gives you a private CAN-FD channel
later — climate state, diagnostics, display handoff — without touching the
vehicle bus or redesigning either board.

Same philosophy as the capped LS reservations: the wire is cheap now and
impossible later.

## Draft message map

11-bit IDs, lower number = higher priority.

| ID | From | Contents | Rate |
|---|---|---|---|
| 0x100 | PMU | Key state, wake state, global fault | 20 Hz |
| 0x110 | PMU | Battery voltage, total current | 10 Hz |
| 0x120 | PMU | Fuel level, output states | 5 Hz |
| 0x130 | PMU | Per-channel currents (multiplexed) | 5 Hz |
| 0x200 | ICU | Engine sensors — RPM, water temp, oil press, oil temp, speed | 20 Hz |
| 0x210 | ICU | Sensor fault flags | 2 Hz |
| 0x300 | DCU | Climate state, blower request, A/C request | 5 Hz |
| 0x310 | DCU | Comfort bus states | 2 Hz |
| 0x400 | Keypad | Button states | on change |
| 0x500+ | LS ECU | Reserved | — |

`[Q-041]` — finalise the map before firmware starts. It is much cheaper to
change on paper than across three codebases.

---

# 14 · Power supply for both modules

Neither Teensy goes anywhere near raw 12 V.

| Stage | Part | Why |
|---|---|---|
| Reverse polarity | Schottky or ideal-diode controller | Survives a backwards jump |
| Transient | TVS, e.g. SMBJ33A | **Load dump.** An alternator disconnect can put 60 V+ on the rail |
| Filter | Series inductor + bulk cap | EMI, and rides out cranking dips |
| Regulation | 12 V → 5 V buck, automotive-grade | Not a bench LM7805 — it will cook |
| Local | Teensy's onboard 3.3 V | Fine for the MCU |

**The load-dump TVS is not optional.** It is the single most common way a
hobbyist microcontroller dies in a car.

Both modules are switched from O10, so neither has a standby draw to budget —
except `[V-056]`, if the DCU needs a keep-alive for climate memory.

---

# 15 · Display capability — what "fully customizable" actually means

## What you genuinely control

Everything drawn. Layout, gauge style, fonts, colours, pages, animations,
warning behaviour, units, thresholds, startup sequence. It is your code and your
framebuffer.

**Things this build can do that no factory cluster can:**

| Capability | Source |
|---|---|
| Per-channel live current for any circuit | PMU publishes it on CAN |
| Soft-fuse trip reporting with the channel named | PMU fault messages |
| Multiple pages — street, night, diagnostic, LS-ready | Firmware |
| Warning thresholds you set and change | Config file |
| Backlight tracking the panel dimmer automatically | O20 illumination reference |
| Datalogging to SD alongside the display | Teensy 4.1 slot |

## Limit 1 · You can only draw what something measures

The display is unlimited. The **sensor set** is not.

| Available now | Source |
|---|---|
| RPM | Tach pickup → ICU |
| Water temp, oil pressure, oil temp | Senders → ICU |
| Road speed | VSS → ICU |
| Fuel level | PMU A7 → CAN |
| Battery voltage, charge state | PMU → CAN |
| Key position, output states, channel currents | PMU → CAN |

**Not available without adding hardware:**

| Wanted | Needs |
|---|---|
| Air/fuel ratio | The existing wideband wired to an ICU input — K-001, currently an unknown tap |
| Gear position | Inferable from VSS + RPM on an automatic, or a shifter position sensor |
| Trans temp | A sender in the pan |
| Intake air temp | A sender |
| G-force, lean angle | An IMU on the ICU board — cheap to add now, impossible later |

`[Q-042]` — fit an IMU on the ICU carrier PCB? A $5 part while the board is being
laid out, and it enables g-meter, lap timing and level display. Adding it after
the PCB exists means a new board.

## Limit 2 · Interface bandwidth sets your frame rate

The Teensy 4.1 is fast. The **display interface** is usually what limits you.

| Interface | Practical |
|---|---|
| SPI, 320×240 | Full redraw comfortable. Fine for a round gauge pair |
| SPI, 800×480 | Full redraw is slow. Needs dirty-rectangle drawing |
| 8080 parallel or RA8875/RA8876 controller | Large panels at real frame rates |

**This is the actual decision hiding inside `[Q-037]`.** Two round TFTs on SPI is
the easy path and looks period-correct. One wide panel is more flexible and needs
a parallel interface or a display controller to feel smooth.

## Limit 3 · Sunlight readability is the real-world killer

A cheap TFT that looks superb on your desk is unreadable at noon with the sun
behind you. This is the single most common failure of custom clusters.

| Need | Spec |
|---|---|
| Brightness | **800–1000 nits minimum.** Typical hobby TFTs are 200–400 |
| Treatment | Optically bonded or anti-reflective, not an air gap |
| Physical | A hood or deep bezel — the factory binnacle already gives you one |

`[V-058]` Check the nit rating before buying any panel. It is the spec most
often omitted from hobby listings, and its absence usually means it's low.

## Design rule: config as data, not code

Put layout, thresholds, colours and units in a **JSON or INI file on the SD
card**. Change the redline warning or swap a page without recompiling, in the
car, with a laptop.

Then write a **safe-mode render path** that works if the config is missing or
corrupt — a plain, hardcoded layout showing RPM, water temp, oil pressure and
speed. A cluster that fails to boot because a config file has a typo is worse
than no cluster.

## The warning that should not depend on the display

`[Q-043]` — **should oil pressure have a hardwired lamp independent of the ICU?**

Right now, if the ICU crashes or its config is bad, you lose your only oil
pressure indication. On a rotary that is the warning that actually matters.

Two cheap options:
- A single discrete LED driven by the pressure switch directly, ignoring both
  MCUs entirely.
- A PMU-driven warning on a spare output — but no spare outputs exist.

**Recommendation: the discrete lamp.** One LED, one wire, one switch, no
processor. It is the same reasoning that put sensor acquisition in the ICU
(D-083) — the thing that matters most should have the fewest dependencies.

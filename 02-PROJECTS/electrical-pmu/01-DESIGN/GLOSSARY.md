# GLOSSARY

Everything in this project written in shorthand. Read this before anything else
if the notation is unfamiliar.

---

## ID prefixes

| Prefix | Means | Lives in |
|---|---|---|
| `D-###` | **Decision** — settled, with reasoning. Append-only, never edited | `DECISIONS.md` |
| `Q-###` | **Question** — needs Camden's judgement | `OPEN.md` |
| `A-###` | **Assumption** — Claude guessed a default, needs a yes/no | `OPEN.md` |
| `V-###` | **Verify** — a fact to confirm before money is spent | `OPEN.md` |
| `T-###` | **Task** — physical work only Camden can do | `TASKS-CAMDEN.md` |
| `K-###` | **Known issue** — a fault or quirk of this car | `00-CAR/known-issues.md` |
| `M-###` | **Modification** — something already changed on the car | `00-CAR/modifications.md` |
| `I-##` | **Improvement** — housekeeping on the documents themselves | `ASSISTANT.md` §8 |

**IDs are permanent and never reused.** A gap in the numbering means something
closed.

## PMU channels

| Notation | Means |
|---|---|
| **O1–O24** | PMU outputs. O1–O5 and O12–O16 are 25 A; O6–O11 are 15 A; O17–O24 are 7 A |
| **A1–A8** | Dedicated analog inputs. 0–5 V, 10-bit, internal 10 kΩ pull-up |
| **A9–A16** | Analog inputs **shared** with O17–O24. 0–20 V, 12-bit. Better inputs |
| **⚡** | Channel has an integrated high-power flyback diode — O1 and O16 only |
| **⚙** | Channel has wiper motor braking — O8 only |
| **Pin 7** | +12 V SW. The wake input. Diode-OR fed |
| **Pin 15** | +5 V reference out, 500 mA ceiling |
| **Pin 25** | Ground. The only one. Carries flyback return for every inductive load |
| **Soft fuse** | A current limit set in software, per channel. Replaces a physical fuse |

## Harness notation

| Notation | Means |
|---|---|
| **L1–L4** | The four legs — Engine, Front Chassis, Dash, Rear Cabin |
| **-P** | Power connector, 12 AWG, Deutsch DTP, size 12 contacts |
| **-M** | Medium connector, 14–16 AWG, Deutsch DT, size 16 |
| **-S** | Signal connector, 16 AWG, Deutsch DT |
| `L3-S2 cav 7` | Leg 3, second signal connector, cavity 7 |
| **DP-** | Dash post — the box side of any connector. `DP-L3-S2` mates with `L3-S2` |
| **D1 / D2** | Door connectors at the sill, driver and passenger |
| **K1–K11** | Relays. K1–K4 pop-ups (panel), K5–K8 windows (sill), K9 start (fender), K10 A/C, K11 constant-bus master |
| **F1–F13** | Panel fuses |

## Wire colour scheme — the NEW harness

Base colour encodes channel class. Tracer encodes circuit. You can identify a
wire's origin without a diagram.

| Base | Class |
|---|---|
| **RED** | 25 A output, 12 AWG |
| **ORN** | 15 A output, 14 AWG |
| **VIO** | 7 A output, 16 AWG |
| **GRY** | Analog input, 16 AWG |
| **PNK** | +5 V reference |
| **BLU** | Wake / +12 V SW |
| **YEL / GRN** | CAN H / CAN L |
| **BLK** | Ground |

## Wire colour codes — the FACTORY harness

**Different scheme. Don't confuse them.** First letter base, second tracer.

| Code | Colour | Code | Colour |
|---|---|---|---|
| B | Black | Lg | Light green |
| W | White | Gy | Gray |
| R | Red | Br | Brown |
| G | Green | O | Orange |
| Y | Yellow | P | Pink |
| L | Blue | V | Violet |

**`GY` on the factory diagram is green/yellow, not gray.** A real trap.

## Factory component refs

Letters match the wiring diagram's section index — `A-06` is section A
(charging/starting), component 6. Sections: **A** charging/starting · **B**
emission/ignition/cruise/fuel pump · **C** meters · **D** wipers · **E**
headlights/illumination · **F** turn/stop/tail/horn · **G** audio/HVAC/defrost ·
**H** interior/accessories · **I** mirrors/windows · **X** common connectors.

**X-##** are shared connectors and ground studs — X-13, X-14, X-15 are the three
factory ground nodes.

## Modules

| Term | Means |
|---|---|
| **PMU** | ECUMaster PMU-24 DL. The power controller. Owns all switching |
| **DCU** | Dash Control Unit. Teensy 4.1. Climate, HVAC servos, comfort switching |
| **ICU** | Instrument Cluster Unit. Teensy 4.1. Display **and** engine sensor acquisition |
| **CAN1** | PMU ↔ laptop, 1 Mbps fixed, **no internal termination** |
| **CAN2** | Vehicle bus, 500 kbps — PMU, keypad, DCU, ICU, future LS ECU |
| **Dash post** | The panel edge where every leg plugs in. Not a physical product, a location |

## Build vocabulary

| Term | Means |
|---|---|
| **Migration** | Moving one circuit from the factory harness to the new one. Per circuit, never in bulk |
| **Dual system** | Two independent power systems in the car at once. **Never both on one load** |
| **Star node** | A single grounding point per zone. Grounds never cross a leg connector |
| **Ladder** | A resistor network turning a multi-position switch into one analog input |
| **Capped spare** | A terminated wire with no load yet, sealed at the bulkhead. Expansion without re-pinning |
| **Irreversible window** | Work that becomes impossible once the harness is out. Only T-014 qualifies |

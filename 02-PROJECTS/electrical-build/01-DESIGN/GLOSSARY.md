# GLOSSARY

Every ID prefix, channel code, connector code, colour and term used in shorthand across this project. Read it once if the notation is unfamiliar.

---

## Project IDs

| Prefix | Means | Lives in |
|---|---|---|
| `D-###` | **Decision** — settled, with its reasoning. A decision is never edited; it is reversed by a newer one that names it | [`../DECISIONS.md`](../DECISIONS.md), grouped by system |
| `Q-###` | **Question** — anything still open: a call only the owner can make, a fact to confirm, or a measurement to take | [`../QUESTIONS.md`](../QUESTIONS.md), easiest first |
| `K-###` | **Known issue** — a fault or quirk of this car | `../../../00-CAR/known-issues.md` |
| `M-###` | **Modification** — something already changed on the car (in the install plan, `M-1` … `M-7` are the *measurement-day* boxes — different thing) | `../../../00-CAR/modifications.md` |
| `A-06`, `F-11`, `X-13` … | **Factory connector and ground codes** — a letter and *two* digits from the 1982 wiring diagram. Not project IDs | `../../../01-REFERENCE/factory-circuits/OEM-RECORD.md` |

**IDs are permanent and never reused.** A gap in the numbering means something closed or moved to another project. A closed question is cited with its closer — `Q-014 → D-215` — never bare. Older IDs (`V-`, `A-`, `T-`, `I-`, `L-`, `F/H/X/Z-`) belong to the archived process files under `99-ARCHIVE/Electrical/` and are not issued any more; the questions that survived from them keep their old numbers.

## PMU channels

| Notation | Means |
|---|---|
| **O1–O24** | PMU outputs. O1–O5 and O12–O16 are 25 A; O6–O11 are 15 A; O17–O24 are 7 A |
| **A1–A8** | Dedicated analog inputs. 0–5 V, 10-bit, internal 10 kΩ pull-up (A7 uses a 1 MΩ pull-down) |
| **A9–A16** | Analog inputs **shared** with O17–O24. 0–20 V, 12-bit. A15 and A16 occupy O23 and O24 |
| **⚡** | Channel with an integrated high-power flyback diode — O1 and O16 only |
| **⚙** | Channel with wiper-motor braking — O8 only |
| **Pin 7** | +12 V SW — the wake input, diode-OR fed |
| **Pin 15** | +5 V reference out, 500 mA ceiling. Used only for the two bias resistors at the dash node |
| **Pin 25** | Ground. The only one. Carries the flyback return for every inductive load |
| **Soft fuse** | A current limit set in software, per channel. Replaces a physical fuse |
| **Inrush window** | A time characteristic on a soft fuse that tolerates a cold filament's 8–12× surge |
| **Channel cap** | The limit a channel runs at until its real draw has been measured by the PMU's own telemetry |

## Harness notation

| Notation | Means |
|---|---|
| **L1–L4** | The four legs — Engine, Front, Dash, Rear (the sill node rides with L4) |
| **-P** | Power housing, 12 AWG, Deutsch DTP, size 12 contacts |
| **-M** | Medium housing, 14–16 AWG, Deutsch DT, size 16 |
| **-S** | Signal housing, 16 AWG, Deutsch DT, size 16 |
| `L3-S2 7` | Leg 3, second signal housing, cavity 7. On a label: `L3-S2-7` |
| **06-…S / 04-…P** | Leg side is always the socket housing (`DT06-…S`), dash-node side always the pin housing (`DT04-…P`) — a leg cannot be plugged into the wrong half |
| **Dash post · DP-** | The row of receptacles at the dash node where every leg plugs in — a location, not a product. **DP-CLU, DP-DIAG, DP-ICU, DP-DCU, DP-KEY** are the five *drops*: devices inches from the node that belong to no leg |
| **Dash node** | The PMU, busbars, fuse blocks, relays, wake strip and receptacles — mounted on one or more small carrier panels low in the dash. Formerly "the plate" |
| **Sill node** | A small panel behind the driver kick panel: the two door receptacles, a ground stud, four empty relay sockets and three labelled fuse positions. Part of L4, not a fifth leg |
| **D1 / D2** | Door connectors at the sill, driver and passenger — every conductor capped this build |
| **K1–K12** | Relays. K1 / K2 pop-up run LH / RH · K3 / K4 empty sockets · K5–K8 window sockets at the sill, empty · K9 start (inner fender) · K11 audio master · K12 washer. K10 was deleted with the A/C; the number is not reused |
| **F1–F19** | Fuses. F1–F3, F5, F12, F13, F15, F16, F19 at the dash node · F8, F9, F14 labelled positions at the sill · F17, F18 in the engine bay. F4, F6, F7, F10, F11 were deleted; the numbers are not reused |
| **LIVE · CAPPED · PLUG · EMPTY** | The status words, defined at the top of `DESIGN.md` |
| **Capped** | A wire run and terminated in its cavity with its far end sealed and labelled, waiting for a future feature. Adding the feature is uncap, connect, enable — no harness work |
| **Star node** | One grounding point per zone, straight to bare chassis. Grounds never cross a leg connector |
| **Ladder** | A resistor network that turns a multi-position switch into one analog input on one wire |

## Wire colours — the NEW harness

Solid colours only. The colour names the family; the printed label names the wire (`DESIGN.md` §4.3).

| Colour | Family |
|---|---|
| **RED** | Power — PMU outputs at 12 and 16 AWG, every fused feed, the backbone |
| **ORN** | 15 A PMU outputs, 14 AWG |
| **BLK** | Ground |
| **GRY** | Analog inputs — ladders, senders, sensor pass-throughs |
| **BLU** | Commands — wake sources, relay-coil returns, window commands |
| **PNK** | F3 switch supply and the +5 V reference |
| **YEL / GRN** | CAN high / low, both buses |

## Wire colour codes — the FACTORY harness

**Different scheme — don't confuse them.** First letter base, second tracer.

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

Letters match the wiring diagram's section index — `A-06` is section A (charging/starting), component 6. Sections: **A** charging/starting · **B** emission/ignition/fuel pump · **C** meters · **D** wipers · **E** headlights/illumination · **F** turn/stop/tail/horn · **G** audio/HVAC/defrost · **H** interior/accessories · **I** mirrors/windows · **X** common connectors. **X-13, X-14, X-15** are the three factory ground nodes.

## Modules and buses

| Term | Means |
|---|---|
| **PMU** | ECUMaster PMU-24 DL. The power controller; owns all switching and the logic |
| **CAN1** | PMU ↔ laptop, 1 Mbps fixed, **no internal termination** — 120 Ω at both ends or the client never connects |
| **CAN2** | Vehicle bus, 500 kbps. This build: the PMU only, with the far-end terminator fitted. Future nodes (luxury package): the ICU cluster module, the DCU climate module, the DP-KEY control panel; engine swap: the engine ECU |
| **ICU / DCU** | The future instrument-cluster and dash-control modules of the luxury package. Only their drops (DP-ICU, DP-DCU) exist here |

## Build vocabulary

| Term | Means |
|---|---|
| **Migration** | Moving one circuit from the factory harness to the new one. Per circuit, never in bulk |
| **Dual system** | Two independent power systems in the car at once. **Never both on one load** |
| **Enable-at** | The soft-fuse value typed in before an output is first switched on — a measured figure or the channel cap |
| **Drive-home rule** | The car starts and drives at the end of every session. Never start a cutover you cannot finish or reverse before dark |

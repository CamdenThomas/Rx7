# GLOSSARY

*Rev 2026-09-01 · owns: every ID prefix, channel code, connector code, colour scheme and term used in shorthand across the project.*

Read this before anything else if the notation is unfamiliar.

---

## ID prefixes

| Prefix | Means | Lives in |
|---|---|---|
| `D-###` | **Decision** — settled, with reasoning. Append-only; reversed by a new entry that marks the old one superseded | [`../05-PROCESS/DECISIONS.md`](../05-PROCESS/DECISIONS.md) |
| `Q-###` | **Question** — needs Camden's judgement. Presented as a four-line packet | [`../05-PROCESS/OPEN.md`](../05-PROCESS/OPEN.md) |
| `A-###` | **Assumption** — Claude picked a default, needs a yes/no | [`../05-PROCESS/OPEN.md`](../05-PROCESS/OPEN.md) |
| `V-###` | **Verify** — a fact to confirm before money is spent | [`../05-PROCESS/OPEN.md`](../05-PROCESS/OPEN.md) |
| `T-###` | **Task** — physical work only Camden can do | [`../05-PROCESS/TASKS-CAMDEN.md`](../05-PROCESS/TASKS-CAMDEN.md) |
| `K-###` | **Known issue** — a fault or quirk of this car | `../../../00-CAR/known-issues.md` |
| `M-###` | **Modification** — something already changed on the car | `../../../00-CAR/modifications.md` |
| `P-###` | **Planned modification** — car-level, not yet done | `../../../00-CAR/modifications.md` |
| `I-###` | **Improvement** — housekeeping on the documents themselves | [`../05-PROCESS/AUDITS.md`](../05-PROCESS/AUDITS.md) |
| `R#` | **Standing rule** for how the documents are kept | `../../../ASSISTANT.md` |
| `L-###` | **Lighting decision** — the deferred lighting scope's own series, merged into the main log (D-201) | [`../05-PROCESS/DECISIONS.md`](../05-PROCESS/DECISIONS.md) §Lighting |
| `TL-##` | Tail-light process step | [`TAIL-LIGHTS.md`](../../../99-ARCHIVE/2026-08-31_lighting-body/TAIL-LIGHTS.md) |
| `F/H/X/Z-###` | Forward-work items — firmware, hardware, documentation, thinking ahead. Three digits, so `F-003` (a firmware item) is never confused with factory connector `F-03` | [`../05-PROCESS/FORWARD-WORK.md`](../05-PROCESS/FORWARD-WORK.md) |
| `[VERIFY]` | An unnumbered price or part-number placeholder that has not been checked | inline, mostly [`BOM.md`](../05-PROCESS/BOM.md) |
| `A-06`, `F-11`, `X-13` … | **Factory connector and ground codes** — a letter and *two* digits, from the 1982 wiring diagram. Not project IDs | `../../../01-REFERENCE/factory-circuits/OEM-RECORD.md` |

**IDs are permanent and never reused** (D-043). A gap in the numbering means
something closed. **Cite a closed ID with its closer** — `Q-038 → D-095`,
never bare — so a reader never mistakes it for live. The status of every ID
is in [`../05-PROCESS/ID-REGISTRY.md`](../05-PROCESS/ID-REGISTRY.md).

## PMU channels

| Notation | Means |
|---|---|
| **O1–O24** | PMU outputs. O1–O5 and O12–O16 are 25 A; O6–O11 are 15 A; O17–O24 are 7 A |
| **A1–A8** | Dedicated analog inputs. 0–5 V, 10-bit, internal 10 kΩ pull-up |
| **A9–A16** | Analog inputs **shared** with O17–O24. 0–20 V, 12-bit. A15 and A16 occupy O23 and O24 |
| **⚡** | Channel has an integrated high-power flyback diode — O1 and O16 only |
| **⚙** | Channel has wiper motor braking — O8 only |
| **Pin 7** | +12 V SW. The wake input. Diode-OR fed |
| **Pin 15** | +5 V reference out, 500 mA ceiling |
| **Pin 25** | Ground. The only one. Carries flyback return for every inductive load |
| **Soft fuse** | A current limit set in software, per channel. Replaces a physical fuse |
| **Inrush window** | A time characteristic on a soft fuse that tolerates a cold filament's 8–12× surge (D-120) |

## Harness notation

| Notation | Means |
|---|---|
| **L1–L4** | The four legs — Engine, Front Chassis, Dash, Rear Cabin |
| **-P** | Power connector, 12 AWG, Deutsch DTP, size 12 contacts |
| **-M** | Medium connector, 14–16 AWG, Deutsch DT, size 16 |
| **-S** | Signal connector, 16 AWG, Deutsch DT |
| `L3-S2 cav 7` | Leg 3, second signal connector, cavity 7 |
| **DP-** | Dash post — the box side of any connector. `DP-L3-S2` mates with `L3-S2` |
| **DP-ICU, DP-DCU, DP-DIAG, DP-KEY** | The four dash-post *drops* — box-adjacent devices, not part of any leg. **DP-KEY** is the generic control-panel drop since D-210 (CAN2 + switched 12 V + ground); no keypad is bought |
| **D1 / D2** | Door connectors at the sill, driver and passenger |
| **K1–K12** | Relays. K1/K2 pop-up run LH/RH (plate, D-186; K3/K4 sockets spare), K5–K8 windows (sill, provisioned empty), K9 start (inner fender), **K10 deleted with the A/C (D-211)**, K11 constant-bus master, K12 washer pulse (plate, D-182) |
| **F1–F15** | Fuses. 11 on the plate — F1–F3, F5–F7, F10–F13 (F13 radar, deferred D-191), F15 exciter (D-198); F8/F9/F14 at the sill. **F4 deleted with the A/C (D-211)** — IDs are never reused (D-043), so the numbering skips it |
| **Status words** | LIVE · PROVISIONED · RESERVED · DEFERRED · OPEN · SPARE — defined in [`SPEC.md`](SPEC.md) §12 |

## Wire colour scheme — the NEW harness

Base colour encodes channel class. Tracer encodes circuit. You can identify a
wire's origin without a diagram.

| Base | Class |
|---|---|
| **RED** | 25 A output, 12 AWG; heavy feeds |
| **ORN** | 15 A output, 14 AWG |
| **VIO** | 7 A output, 16 AWG |
| **GRY** | Analog input, sender and sensor wires, 16 AWG |
| **PNK** | +5 V reference |
| **BLU** | Wake sources and switched-12 V relay commands |
| **YEL / GRN** | CAN H / CAN L — BLK tracer marks CAN2 |
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
| **CAN2** | Vehicle bus, 500 kbps — PMU, DCU, ICU, the deferred DP-PANEL control panel (D-210), future LS ECU |
| **Dash post** | The panel edge where every leg plugs in. Not a physical product, a location |
| **Sill node** | The one distribution point outside the dash post: door connectors, ground stud, provisioned window relays |

## Build vocabulary

| Term | Means |
|---|---|
| **Migration** | Moving one circuit from the factory harness to the new one. Per circuit, never in bulk |
| **Dual system** | Two independent power systems in the car at once. **Never both on one load** |
| **Star node** | A single grounding point per zone. Grounds never cross a leg connector |
| **Ladder** | A resistor network turning a multi-position switch into one analog input |
| **Capped spare** | A terminated wire with no load yet, sealed at the bulkhead. Expansion without re-pinning |
| **Provisioned** | Capped spare *plus* the socket or fuse position fitted empty — adding the feature is populate, uncap, enable |
| **Irreversible window** | Work that becomes impossible once the harness is out. Only T-014 → D-197 qualifies |
| **Give me the diff** | The session-close command. Claude reports CHANGED / LOGGED / OPENED / CLOSED / NEXT and appends it to [`CHANGELOG.md`](../05-PROCESS/CHANGELOG.md) |

# LEG 3 — DASH

*Rev 2026-08 · authoritative cavity assignments live in `PIN-MAP.md`*

**Boundary:** the dash structure. Comes out when the dash comes out.
**Ground:** dash star node, adjacent to the panel.
**Special:** the panel lives here but is not part of this leg — it is the hub.

---

## What's in this leg

### Inputs — switches and controls

| Device | OEM ref | Signal type | States |
|---|---|---|---|
| Key / ignition switch | — | Ladder, 12 V side | OFF/ACC/RUN/START |
| Headlight switch | E-01 LIGHT | Ladder, 12 V side | OFF/PARK/HEAD |
| Dimmer / passing | E-01 DIMMER | Software off A15 *(D-051)* | LO/HI/PASS |
| Turn stalk | F-02 TURN | Ladder to ground | L/off/R |
| Hazard switch | F-02 HAZARD | Closure + **wake diode** | on/off |
| Wiper stalk | D-03 | Ladder to ground | 5 states |
| Brake pedal switch | F-11 | Closure to ground | on/off |
| Wink switch L/R | — | Closure ×2 → K1–K4 coils | momentary |
| Window switch DRV/PASS | I-06/07 | Closure ×4 → K5–K8 at the **sill** | momentary |
| Blower switch | G-15 | Factory switch + resistor pack | OFF/LO/MI/HI |
| Horn switch | steering pad | Closure + **wake diode** *(D-072)* | momentary |
| Parking brake switch | C-04 | Closure | on/off |
| Glove box light switch | H-02 | Closure | on/off |
| Hatch release button | H-13 | Momentary | — |
| Fuel-door release button | H-15 | Momentary | — |
| Defroster | G-24 | **CAN keypad** | on/off |

**No retract switch.** Deleted (D-038) — pop-ups raise from the A15 ladder
reaching HEAD. Wink switches are momentary overrides.

### Outputs — loads in the dash

| Device | On | Note |
|---|---|---|
| Blower motor | O16 ⚡ | Flyback channel. Factory resistor pack sets speed |
| Comfort bus | O15 | **DCU switches downstream** *(D-073)* |
| Illumination bus | O20 branch | PWM. Rheostat deleted |
| Glove box light | O20 | LED |
| USB-C ports | O10 | |
| Head unit, switched | O10 | Double-DIN *(D-051)* |
| Head unit, constant | F1 busbar | Off the PMU — it sleeps |
| **DCU + ICU logic** | O10 | *(D-075)* |

**No cigarette lighter.** Deleted (D-095) — it was 8–10 A and could trip the
channel powering the instruments.

Current figures: see `../LOADS.md`. Not duplicated here.

### Deleted from this leg

| Device | Why |
|---|---|
| Control Processing Unit | Flasher, wiper INT, chime, belt, key reminder → all software |
| Instrument panel dimmer rheostat | O20 PWM replaces it |
| Retractable headlight switch | D-038 |
| Cigarette lighter | D-095 |
| Cruise control unit and switches | **Confirmed gone** *(D-097)* |
| Power antenna relay + switch | **Confirmed gone** *(D-097)* |
| Rear wiper switch | **Confirmed gone** *(D-097)* |
| Oscillator (chime), brake warning checker | Software — then dropped entirely *(D-050)* |
| Stop light switch as a load-carrier | Becomes a signal input only |

---

## Connectors

**Five housings.** Cavity assignments are in `PIN-MAP.md` — this section names
the housings and explains the shape.

| Code | Housing | Cav | Used | Carries |
|---|---|---|---|---|
| **L3-P** | DTP06-2S | 2 | 2 | Blower, comfort bus — 12 AWG |
| **L3-M** | DT06-2S | 2 | 2 | Accessory bus, head unit constant — 14 AWG |
| **L3-S1** | DT06-12S | 12 | 12 | Signal |
| **L3-S2** | DT06-12S | 12 | 12 | Signal |
| **L3-S3** | DT06-8S | 8 | 5 | Signal |

**AMPSEAL is gone** (D-052/070). Three DT housings instead of one 35-way: cheaper,
easier to source contacts for, and a connector failure takes out part of the dash
rather than all of it.

**Plus two module drops at the post**, not part of this leg: `DP-ICU` (DT06-12S,
carries all six engine sensor inputs) and `DP-DCU` (DT06-6S, power and CAN only).

---

## Why this leg is shaped the way it is

**Almost entirely signal.** Two heavy conductors against 29 signals. That inverts
the usual harness assumption — the connectors here are chosen for cavity count,
not current.

**Ladders are what make it fit.** Without them the switch inputs alone would need
15+ pins. With them it is six. Every multi-position switch is laddered from day
one, because retrofitting one is a re-pin (D-019).

**The Control Processing Unit deletion is the biggest single simplification in
the project.** One module was doing flasher, wiper intermittent, chime, seat belt
warning and key reminder. All of it is now config.

**Routing:** keep the CAN pairs away from the relay coil commands. Coils switch
inductively and put spikes back down the bundle.

**Two grounds legitimately cross this leg** — the diagnostic port and keypad
returns. Both are box-adjacent devices with no zone of their own (D-037).

---

## Later additions land here

The DCU and ICU mount inches from the post and join at `DP-DCU` / `DP-ICU`.
L3-S3 has three spare cavities; the module connectors are separate, so the DCU
arriving does not consume this leg's spares.

`[Q-014]` — the dash envelope is still unmeasured, and it gates the panel
drawing. The relay bank dropped from 16 sockets to 10 (D-067), so the panel is
smaller than when that question was first written.

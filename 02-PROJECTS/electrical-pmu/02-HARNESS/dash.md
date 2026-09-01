# LEG 3 — DASH

*Rev 2026-09-01 · owns: what is in the dash leg and why. Cavities are [`PIN-MAP.md`](PIN-MAP.md)'s; draw figures are [`../01-DESIGN/LOADS.md`](../01-DESIGN/LOADS.md)'s.*

**Boundary:** the dash structure. Comes out when the dash comes out.
**Ground:** dash star node, adjacent to the panel.
**Special:** the panel lives here but is not part of this leg — it is the hub.
The four drops (DP-ICU, DP-DCU, DP-DIAG, DP-KEY) are box-adjacent and not part
of this leg either.
**Housings:** L3-P (DTP-2) · L3-M (DT-2) · L3-S1, L3-S2 (DT-12 ×2) · L3-S3
(DT-8). Diagram: `diagrams/L3-dash.svg`.

---

## Inputs — switches and controls

| Device | OEM ref | Signal | Goes to | Note |
|---|---|---|---|---|
| Key / ignition switch | — | Summed ladder, 12 V side | A16 via L3-S1 1 | ACC and IG contacts also feed the wake strip (L3-S1 12, L3-S2 1) |
| Headlight switch | E-01 LIGHT | Ladder, 12 V side | A15 via L3-S1 2 | OFF/PARK/HEAD. Also commands the pop-ups (D-038) |
| Dimmer / passing | E-01 DIMMER | Software off A15 (D-051) — states not yet defined | `Q-065` → D-184 | |
| Turn stalk | F-02 TURN | Ladder to ground | A1 via L3-S1 3 | L/off/R |
| Hazard switch | F-02 HAZARD | Closure + second pole as a wake source | A8 via L3-S1 6; wake L3-S2 2 | |
| Wiper stalk | D-03 | Ladder to ground | A2 via L3-S1 4 | 5 states |
| Brake pedal switch | F-11 | Closure to ground | A3 via L3-S1 5 | |
| Wink switches L / R | new | SPDT ×2 — NC poles cross into K1/K2 coil paths, NO poles feed the wake strip | L3-S1 9, 10 | Momentary override (D-038, D-189) |
| Horn switch | steering pad | Closure + wake diode (D-072) | Wake L3-S1 11; **PMU input `Q-063` → D-182** | |
| Window switches DRV/PASS | new, not fitted | Closure ×4 → K5–K8 at the sill | L3-S2 3–6, **capped** | PROVISIONED (D-131) |
| Blower switch + resistor pack | G-15, G-14 | In the motor path, fed by O16 | via L3-P 1 | Factory switch sets speed; the PMU only enables O16 |
| Defog, hatch release, fuel-door release | G-24 | **Deferred to the custom A/C panel** (D-210) | DP-KEY — drop wired and capped | Factory defrost switch broken (K-020) and deleted. `DEFOG` stays configured and **disabled**; hatch and fuel-door solenoid branches (D-180) are unbuilt |
| Custom A/C / control panel | — | CAN2 + switched 12 V + ground, 4 conductors | DP-KEY | D-210 — **no keypad is bought.** The drop is the universal set, so whatever panel is designed plugs in |
| Glove box lamp switch | H-02 | Local closure — lamp only, **no PMU input** | O20 branch | D-209 — manual latch; light on door open |

**No panel buttons in this build (D-210):** the horn stays on the steering pad (A8 via 12 kΩ, D-190) · interior-light override deleted outright · glove box is a lamp switch, not a button · defog, hatch and fuel-door controls wait for the custom panel. **Every switch in the car except the column combination switch is replaced** — schedule and parts: [`../01-DESIGN/SWITCHES.md`](../01-DESIGN/SWITCHES.md).

**No retract switch.** Deleted (D-038) — pop-ups raise from the A15 ladder
reaching HEAD. Wink switches are momentary overrides.

## Outputs — loads in the dash

| Device | On | Goes to | Note |
|---|---|---|---|
| Blower motor | O16 ⚡ | L3-P 1 | Motor is DEAD (K-023) — replacement sized from its spec (D-126) |
| Comfort bus | O15 | L3-P 2 | **DCU switches downstream** (D-073); loads deferred |
| Accessory bus — USB-C, head unit switched | O10 | L3-M 1 | No lighter (D-095) |
| Head unit constant | Busbar F1 via K11 | L3-M 2 | Off the PMU — it sleeps (D-020) |
| Illumination bus | O20 branch | L3-S1 8 | PWM. Rheostat deleted |
| ICU + DCU logic | O10 | DP-ICU 1, DP-DCU 1 | Drops, not this leg |
| Radar module | Busbar F13 (`V-056` → D-191) | L3-S2 7, 8 | DEFERRED (`V-061`) |

## Deleted from this leg

| Device | Why |
|---|---|
| Control Processing Unit | Flasher, wiper INT, chime, belt, key reminder → all software (D-013, D-014, D-050) |
| Instrument panel dimmer rheostat | O20 PWM replaces it |
| Retractable headlight switch | D-038 |
| Cigarette lighter | D-095 |
| Cruise control unit and switches | **Confirmed gone** (D-097) |
| Power antenna relay + switch | **Confirmed gone** (D-097) |
| Rear wiper switch | **Confirmed gone** (D-097) |
| Oscillator (chime), brake warning checker | Software — then dropped entirely (D-050) |
| Stop light switch as a load-carrier | Becomes a signal input only |
| Rear defrost switch | Broken (K-020); control moves to the custom A/C panel (D-210) — **no defogger until then** |
| **A/C switch and its interlock chain** | The compressor is removed (D-211). Nothing to switch — heat, defrost and ventilation are unaffected; F4 and K10 go with it |

## Why this leg is shaped the way it is

**Almost entirely signal.** Two heavy conductors, two medium, and 23 signal
conductors in use across three DT housings. That inverts the usual harness
assumption — the connectors here are chosen for cavity count, not current.

**Ladders are what make it fit.** Without them the switch inputs alone would
need 15+ pins. With them it is seven. Every multi-position switch is laddered
from day one, because retrofitting one is a re-pin (D-019).

**Three DT housings instead of one 35-way AMPSEAL** (D-052, D-070): cheaper,
easier to source contacts for, and a connector failure takes out part of the
dash rather than all of it. Nine cavities are spare.

**The Control Processing Unit deletion is the biggest single simplification in
the project.** One module was doing flasher, wiper intermittent, chime, seat
belt warning and key reminder. All of it is now config.

**Routing:** keep the CAN pairs away from the relay coil commands. Coils switch
inductively and put spikes back down the bundle.

**Grounds that cross here** — the diagnostic port, control-panel drop, ICU and DCU returns
— are box-adjacent devices with no zone of their own (D-037). They are drops,
not part of the leg.

## Later additions land at the drops, not in this leg

The DCU and ICU mount inches from the post and join at `DP-DCU` / `DP-ICU`;
the module connectors are separate, so the DCU arriving does not consume this
leg's spares. `Q-014` / `T-007` — the dash envelope is still unmeasured, and
it gates the panel drawing.

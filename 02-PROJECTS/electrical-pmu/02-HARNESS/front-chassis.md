# LEG 2 — FRONT CHASSIS

*Rev 2026-08-30 · owns: what is in the front leg and why. Cavities are [`PIN-MAP.md`](PIN-MAP.md)'s; draw figures are [`../01-DESIGN/LOADS.md`](../01-DESIGN/LOADS.md)'s.*

**Boundary:** firewall to radiator support, including the cowl. Comes out with
nose, bumper, and pop-up assemblies.
**Ground:** front star node. Includes the cowl-area returns.
**Housings:** L2-P1, L2-P2 (DTP-4 ×2) · L2-M (DT-8) · L2-S (DT-6). Diagram:
`diagrams/L2-front-chassis.svg`.

---

## Devices

| Device | OEM ref | Direction | Goes to | Note |
|---|---|---|---|---|
| Headlight LOW / HIGH | E-08/E-09 | Out | O2 / O3 via L2-P1 1, 2 | Stated as LED housings — `V-066` confirms what is fitted. The lamp unit itself is `lighting-body/` scope (D-110, D-123) |
| Pop-up motor LH | E-03 | Out | K1/K2 via L2-P1 3, 4 | Reversible, 2 legs. Stays (D-110) |
| Pop-up motor RH | E-04 | Out | K3/K4 via L2-P2 1, 2 | |
| Pop-up limit LH / RH | E-03 / E-04 internal | In | A4 / A5 via L2-S 1, 2 | Ladder, 3 states. **Inside the motor** — pinout by continuity test, `T-011` |
| Front turn LH / RH | F-05 / F-06 | Out | O17 / O18 via L2-M 5, 6 | 27 W filament |
| Front parking, side markers | F-05/F-06, F-12/F-13 | Out | O6 via L2-M 7 | |
| Horns LH / RH | F-09 / F-10 | Out | O11 via L2-M 3, spliced at the nose | Single-wire factory units — **deliberate ground to the star node now** |
| **Front wiper motor** | D-02 | Out | O8 / O9 via L2-M 1, 2 | 2-speed. **Measure stall** |
| Wiper park sense | D-02 internal | In | L2-S 3 — **no PMU pin yet** | `Q-063` |
| Front washer pump | D-01 | Out | L2-M 4 — **no PMU output yet** | Not working (K-022): diagnose first, `T-040`. Output is `Q-063` |

## Devices deleted

| Device | OEM ref | Status |
|---|---|---|
| Horn relay | F-16 | **Deleted** — the PMU switches the horns directly |
| Headlight cleaner motor | E-11 | **Confirmed gone** (D-097) |
| Retractable headlight switch | E-02 | **Deleted** (D-038) — pop-ups raise from the A15 ladder; also broken (K-021) |

## Leg totals

| | Value |
|---|---|
| Heavy conductors (12 AWG) | 2 headlight + 4 pop-up motor legs = 6, plus 2 spare |
| Medium (14 AWG) | Wiper LO, wiper HI, horn, washer = 4 |
| Light (16 AWG) | Turn L, turn R, park/marker, spare = 4 |
| Signal (16 AWG) | Pop-up limits ×2, wiper park, +5 V ref, 2 spare = 6 |
| Est. peak draw | ~35 A — both pop-ups moving + wipers + headlights |
| Ground | Front star node |

## Why this leg is shaped the way it is

**Pop-up motors dominate this leg.** Four heavy conductors for two motors, and
the reversing happens back at the panel relay bank. That is the single biggest
wire-count driver in the whole car and it is unavoidable with H-bridge
reversing. Relays at the nose were considered and rejected (D-069) — the nose
is the wettest, hottest, most vibration-exposed part of the car.

**The cowl belongs here, not with the engine.** Wiper motor and washer pump come
off with nose work. Grouping them with the engine leg would mean two legs
disturbing each other for a wiper job.

**Two DTP shells because DTP is only made in 2- and 4-way** (D-115). L2-P2
carries the RH pop-up and two heavy spares.

**Keep L2-S out of the L2-P1/P2 bundle.** Pop-up motor legs are the noisiest
conductors in the nose and the ladders are the most noise-sensitive.

**Horns need a deliberate ground.** Factory grounded them through the mounting
bracket. Both go to the front star node now.

**Lighting current is filament, not LED** (D-124). The 14 and 16 AWG sizes are
set by voltage drop over a ~12 ft run and by crimp robustness, not by ampacity
(D-016) — they would not change with LED either way.

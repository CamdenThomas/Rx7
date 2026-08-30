# Circuit — Meters, Warning Lights, Ignition, Fuel Pump

*Rev 2026-08-30 · owns: the factory decode of this circuit — devices, wires, logic. The rebuild table at the foot points into the new design and is not its owner; cavities are `02-HARNESS/data/connectors.csv`'s.*

**Source:** Section C page 16, Section B pages 12–13.

---

## 1 · Instrument panel

| Ref  | Device                      | Pins              |
|------|-----------------------------|-------------------|
| C-01 | Fuel gauge tank unit        | B, Y              |
| C-02 | Water temp gauge unit       | YW                |
| C-03 | Brake warning light checker | BR, B             |
| C-04 | Parking brake switch        | BR                |
| C-05 | Brake fluid level sensor    | BR, B             |
| C-06 | Oil level sensor            | BG                |
| C-07 | Coolant level unit          | YB, YL, GY, Br, B |
| C-08 | Coolant level sensor        | Br                |
| C-09 | Oil pressure gauge unit     | BrY               |
| C-10 | Oscillator (warning chime)  | G, YB, LR, YR, B  |

| Item     | Value                                                            |
|----------|------------------------------------------------------------------|
| Feed     | Ignition **IG** → BY → X-04 **10 A** → **GY** bus                |
| Internal | A voltage regulator inside the cluster steadies the gauge supply |
| Ground   | **X-13** throughout                                              |

## 2 · Senders and signals

| Signal             | Wire         | From                                        |
|--------------------|--------------|---------------------------------------------|
| Fuel level         | Y            | C-01 tank unit, resistive                   |
| Water temp         | YW           | C-02 sender, resistive                      |
| Oil pressure       | BrY          | C-09 sender, resistive                      |
| **Tachometer**     | **YG**       | Ignition coil (T), B-18 — Section B         |
| Alternator warning | BW           | Emission control unit / choke & check relay |
| Stop light warning | GL           | F-03 stop light checker                     |
| Coolant level      | YB / YL / Br | C-07 unit                                   |

Warning lamps are 1.4 W. The tach reads the **coil primary** on YG — a
low-level signal referenced to X-13, which is why K-008 shows up there.

## 3 · Ignition

| Ref  | Device                       | Pins           |
|------|------------------------------|----------------|
| B-18 | Ignition coil (T) — trailing | YG, BW         |
| B-19 | Ignition coil (L) — leading  | YL, BW         |
| B-20 | Igniter (T)                  | YG, BW         |
| B-21 | Igniter (L)                  | YL, BW         |
| B-22 | Condenser                    | BW             |
| —    | Pick-up coil                 | in distributor |

Twin coils, twin igniters — leading and trailing, standard 12A rotary. Feed is
**BW** from ignition IG.

## 4 · Fuel pump

| Item   | Value                                          |
|--------|------------------------------------------------|
| Feed   | Ignition **IG** → BW → X-04 **10 A** → **BLg** |
| Pump   | B-24                                           |
| Ground | **X-15**                                       |

Simple key-on circuit. No prime logic, no oil-pressure interlock, no inertia
cutoff. K-008 — the pump grounds at X-15 alongside the rear turn lamps.

## 5 · What this means for the rebuild

| Factory | PMU-24 plan |
|---|---|
| Cluster on 10 A GY bus, internal regulator | The **ICU** replaces the cluster (D-006 → D-075, D-083). The factory cluster stays in place through ICU development (D-090) |
| Fuel level sender Y | A7 input, **L4-S 1** — the one sender the PMU reads; published on CAN 0x120 |
| Water temp YW, oil pressure BrY | ICU inputs — **L1-S1 3 → DP-ICU 6**, **L1-S1 4 → DP-ICU 7**. Oil temp (new) L1-S1 5 → DP-ICU 8 |
| Tach signal YG from coil | **L1-S1 6 → DP-ICU 9**, shielded, opto/comparator at the ICU (D-082). Routed away from every high-current wire |
| Twin coils + igniters on BW | O12 ignition feed, **L1-P 1** |
| Fuel pump, key-on only | O5 → **L4-P 2**, with a software prime, the PMU's inertia switch, and run-with-RPM once the ICU publishes rpm — interim rule `Q-064` (Checklist 2.17) |
| Warning lamp logic, checkers, oscillator | All software, in the ICU |
| Everything grounded at X-13 / X-15 | Zone star nodes (D-017) |

The fuel pump gains real safety it never had: prime on key-on, cut if the engine
stops, cut on impact.

## 6 · Unknowns

| ID | Unknown | Resolve by |
|---|---|---|
| V-037 | Fuel sender resistance range, empty → full, for A7 scaling | Measure at the tank, `T-012`, Checklist 0.5 |
| V-038 | Whether the coolant level unit and oscillator are still fitted | Inspect (A-010 caps the level senders either way) |
| V-039 → D-082 / `V-067` | Tach signal type and level | Conditioning decided; pulses per rev still to confirm |

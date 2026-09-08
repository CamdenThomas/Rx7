# Circuit — Meters, Warning Lights, Ignition, Fuel Pump

*Rev 2026-09-07 · owns: the factory decode of this circuit — devices, wires, logic. Nothing of the new design lives here; the last section says where it does.*

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

The rebuild's side of every device and wire above is the electrical build's record, not this file's: find a factory code in its data — `python tools/rx7.py -p electrical-build find "C-02"` — or read the rendered [`DESIGN.md`](../../02-PROJECTS/electrical-build/01-DESIGN/DESIGN.md) §12 (device ends) and [`WIRE-TABLES.md`](../../02-PROJECTS/electrical-build/03-INSTALL/WIRE-TABLES.md). A hand-copied mapping table stood here until 2026-09-07; it had drifted three decisions behind and was removed — one fact, one home. Decisions that shaped this circuit's rebuild: D-006 · D-017 · D-075 · D-082 · D-083 · D-090 · D-183.

## 6 · Unknowns

Every unknown this decode raised has an ID. The open ones live in the projects' `QUESTIONS.md` files (electrical, luxury, engine swap); the closed ones are cited with their closer in the projects' `DECISIONS.md`. This circuit's: A-010 · T-012 · V-037 · V-038 · V-039 · V-067.

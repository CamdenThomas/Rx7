# Circuit — Charging & Starting

*Rev 2026-09-07 · owns: the factory decode of this circuit — devices, wires, logic. Nothing of the new design lives here; the last section says where it does.*

**Source:** Section A, page 10.

---

## 1 · Charging

| Ref  | Device                             | Connector   | Pins   |
|------|------------------------------------|-------------|--------|
| A-08 | Alternator with integral regulator | 2-pin       | BW, WB |
| A-09 | Alternator B+ output               | ring/eyelet | WR     |

| # | Wire | From                                | To                                          | Notes                   |
|---|------|-------------------------------------|---------------------------------------------|-------------------------|
| 1 | WR   | Alternator B+ (A-09)                | WR constant bus                             | Main charge path        |
| 2 | BW   | Ignition IG → X-04 **7.5 A** → X-01 | Alternator (A-08)                           | Field excitation / lamp |
| 3 | WB   | Alternator (A-08)                   | Choke and check relay (Section B), via X-01 | Charge indicator sense  |

Fusible link **0.5 sq** at X-09 protects the ignition-side feed.

## 2 · Starting

| Ref  | Device                 | Connector | Pins                     |
|------|------------------------|-----------|--------------------------|
| A-01 | Starting motor         | 1-pin     | BY (M/T) or **BW (A/T)** |
| A-06 | Inhibitor switch (A/T) | 4-pin     | BY, GY, BW, RW           |
| A-02 | Fusible link 0.5 sq    | —         | LW                       |

| # | Wire | From                            | To                                                                |
|---|------|---------------------------------|-------------------------------------------------------------------|
| 1 | WR   | Battery via fusible link        | Ignition switch (X-08)                                            |
| 2 | BY   | Ignition switch **ST** terminal | Inhibitor switch A-06                                             |
| 3 | BW   | Inhibitor switch A-06           | Starting motor solenoid (A-01)                                    |
| 4 | BY   | Ignition switch ST              | Also to emission control unit and cruise control unit (Section B) |

**This car is A/T** — cranking passes through the inhibitor switch (A-06,
BY in / BW out). That switch is the park/neutral interlock and also carries the
back-up light circuit on its GY/RW pins.

## 3 · Cold-start hardware (present on this diagram)

| Ref  | Device          | Notes                      |
|------|-----------------|----------------------------|
| A-03 | Hot start relay | LW, GR, LW, B              |
| A-04 | Hot start motor | GR                         |
| A-05 | Sub-zero motor  | Except California. BW, Blg |
| A-07 | Sub-zero sensor | Except California. Blg     |

V-025 → D-097: none of these remain. With the Weber conversion
(M-001) the sub-zero and hot-start assist hardware is very likely gone — it
served the factory carburetor.

## 4 · What this means for the rebuild

The rebuild's side of every device and wire above is the electrical build's record, not this file's: find a factory code in its data — `python tools/rx7.py -p electrical-build find "C-02"` — or read the rendered [`DESIGN.md`](../../02-PROJECTS/electrical-build/01-DESIGN/DESIGN.md) §12 (device ends) and [`WIRE-TABLES.md`](../../02-PROJECTS/electrical-build/03-INSTALL/WIRE-TABLES.md). A hand-copied mapping table stood here until 2026-09-07; it had drifted three decisions behind and was removed — one fact, one home. Decisions that shaped this circuit's rebuild: D-097 · D-148 · D-182 · D-198.

## 5 · Unknowns

Every unknown this decode raised has an ID. The open ones live in the projects' `QUESTIONS.md` files (electrical, luxury, engine swap); the closed ones are cited with their closer in the projects' `DECISIONS.md`. This circuit's: Q-063 · T-004 · T-023 · V-002 · V-025 · V-026 · V-050.

# Circuit — Charging & Starting

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

`[V-025]` Confirm which of these are still fitted. With the Weber conversion
(M-001) the sub-zero and hot-start assist hardware is very likely gone — it
served the factory carburetor.

## 4 · What this means for the rebuild

| Factory                                      | PMU-24 plan                                                                |
|----------------------------------------------|----------------------------------------------------------------------------|
| Ignition switch ST carrying solenoid current | A16 key ladder input; O21 drives a start relay coil at the starter (A-005) |
| Inhibitor switch in series with crank        | Becomes a PMU **input**; crank interlock done in software (Checklist 055)  |
| Alternator BW excitation via 7.5 A fuse      | C1-B6 alternator lamp/sense, 18 AWG                                        |
| Alternator WR to battery bus                 | Unchanged — heavy cable, does not pass through the PMU                     |
| Hot start / sub-zero hardware                | Almost certainly deleted, pending V-025                                    |

The alternator's B+ cable and the starter cable never touch the PMU. Only the
sense wire and the relay coil do.

## 5 · Unknowns

| ID    | Unknown                                                          | Resolve by                |
|-------|------------------------------------------------------------------|---------------------------|
| V-025 | Which cold-start components remain after the Weber conversion    | Inspect car               |
| V-002 | Alternator output rating                                         | Read the case, T-010      |
| V-026 | Inhibitor switch condition and pin function on this specific car | Inspect / continuity test |

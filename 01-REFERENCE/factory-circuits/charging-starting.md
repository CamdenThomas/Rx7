# Circuit — Charging & Starting

*Rev 2026-08-30 · owns: the factory decode of this circuit — devices, wires, logic. The rebuild table at the foot points into the new design and is not its owner; cavities are `02-HARNESS/data/connectors.csv`'s.*

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

| Factory | PMU-24 plan |
|---|---|
| Ignition switch ST carrying solenoid current | A16 key ladder input (**L3-S1 1**); O21 drives the start relay K9 coil via **L1-S1 1** — K9 on the inner fender, not at the starter (A-005 → D-148) |
| Inhibitor switch in series with crank | Becomes a PMU **input**; crank interlock in software (Checklist 2.16). Pin is `Q-063` → D-182 |
| Alternator BW excitation via 7.5 A fuse | **Reproduced to factory spec (D-198): O12 branch → F15 (7.5 A) → L1-S1 2 → BW.** BW is the field FEED, not a lamp — the earlier sense-only plan would never have excited the alternator. The WB charge-sense gets **L1-S2 8 → DP-ICU 11** at Phase 9 |
| Alternator WR to battery bus | Unchanged — heavy cable to the distribution post, does not pass through the PMU ([`BATTERY-INSTALL.md`](../../02-PROJECTS/electrical-pmu/04-BUILD/BATTERY-INSTALL.md) §4) |
| Hot start / sub-zero hardware | Gone — zero remain post-Weber (V-025 → D-097) |

The alternator's B+ cable and the starter cable never touch the PMU. Only the
sense wire and the relay coil do.

## 5 · Unknowns

| ID | Unknown | Resolve by |
|---|---|---|
| V-025 → D-097 | Cold-start components after the Weber conversion | None remain |
| V-002 | Alternator output rating | Read the case, `T-004`, Checklist 0.4 |
| V-026 → V-050 → D-178 / `Q-063` → D-182 | Inhibitor switch condition and pin function | Continuity test with `T-023` → D-178; pin allocation in `Q-063` → D-182 |

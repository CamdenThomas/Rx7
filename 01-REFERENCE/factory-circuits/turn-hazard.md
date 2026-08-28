# Circuit — Turn Signals & Hazard

**Source:** Section F, page 22.
**Type:** Turn = ignition-switched. Hazard = constant-hot (works key-off).
**Relevant to fault K-008.**

---

## 1 · Devices

| Ref | Device | Connector | Pins |
|---|---|---|---|
| F-02 | Combination switch (hazard + turn sections) | 6-pin | WG, GW, GY, GR, GO, GB |
| — | Control Processing Unit (flasher/hazard module) | X-16 | GW, GB, B |
| F-05 | Front turn & parking light LH (dual filament) | 3-pin | RG, GR, B |
| F-06 | Front turn & parking light RH | 3-pin | RG, GO, B |
| F-07 | Rear combination light LH | multi | GR, RW, G, RG, B |
| F-08 | Rear combination light RH | multi | GO, RW, G, RG, B |
| X-04 | Fuse block — 10 A turn, 10 A hazard | — | — |

## 2 · Feed topology

| Path | Wire | Notes |
|---|---|---|
| Battery → fusible link 1.25 sq → **WR** constant bus | WR | |
| WR → X-04 **10 A** → WG → F-02 hazard section | WG | Constant — hazards work with key out |
| Ignition switch **IG** → BY → X-04 **10 A** → **GY** bus → F-02 turn section | GY | Ignition-switched |
| GY bus also feeds the back-up light circuit | GY | Shared bus — see `backup-lights.md` |

## 3 · Signal path

| # | Wire | From | To |
|---|---|---|---|
| 1 | GW | F-02 combination switch | Control Processing Unit |
| 2 | GB | F-02 combination switch | Control Processing Unit |
| 3 | B | Control Processing Unit | Ground via X-13 |
| 4 | GR | F-02 turn LEFT out | Front LH (F-05), rear LH (F-07), LH indicator |
| 5 | GO | F-02 turn RIGHT out | Front RH (F-06), rear RH (F-08), RH indicator |
| 6 | B | All lamps | Ground via X-13 / X-14 / X-15 |

## 4 · Lamp loads (factory incandescent)

| Lamp | W each | Qty |
|---|---|---|
| Front turn | 27 | 2 |
| Rear turn | 27 | 2 |
| Dash indicator | 3.4 | 2 |

Roughly 55 W per side flashing, ~4.5 A. This is the number the flasher and any
bulb-out logic was designed around.

## 5 · Fault K-008 — why this circuit is the suspect

Turn signal current is pulsing and returns to ground through X-13. If that
ground point is corroded or shared with the tach and fuel pump returns, every
blinker pulse lifts the local ground reference and both circuits see it. The
Control Processing Unit's own ground (B → X-13) is the first thing to test.

**This is exactly what the new architecture eliminates** — D-017 puts a local
star node in each zone and forbids grounds from crossing a bulkhead.

## 6 · What this means for the rebuild

| Factory | PMU-24 plan | Change |
|---|---|---|
| Control Processing Unit flasher | Deleted | PMU flashes O17/O18 natively (D-013) |
| Combination switch turn contacts | A1 resistor ladder, switch-to-ground | Three states: L / off / R |
| Hazard on its own constant feed | A8 input + diode to pin 7 | PMU wakes for hazards key-off (A-011) |
| Separate L and R output wiring | O17 (VIO/GRN), O18 (VIO/YEL) | Split at panel to C2 and C4 |
| Shared ground at X-13 | Front and rear star nodes | Direct fix for K-008 |
| 27 W incandescent | LED | Flash rate and bulb-out thresholds must be set from measured LED current, not these wattages |

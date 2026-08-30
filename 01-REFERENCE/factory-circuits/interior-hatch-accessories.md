# Circuit — Interior, Doors, Hatch, Fuel Door, Accessories

*Rev 2026-08-30 · owns: the factory decode of this circuit — devices, wires, logic. The rebuild table at the foot points into the new design and is not its owner; cavities are `02-HARNESS/data/connectors.csv`'s.*

**Source:** Section H, page 26.

---

## 1 · Devices

| Ref  | Device                           | Pins          |
|------|----------------------------------|---------------|
| H-01 | Glove box light (3.4 W)          | LO, BL        |
| H-02 | Glove box light switch           | BL, B         |
| H-03 | Ignition key reminder switch     | G, LY         |
| H-04 | Seat belt switch                 | Br, BrW       |
| H-05 | Ignition switch light (3.4 W)    | LY, GL        |
| H-06 | Interior & spot light (5 W)      | LY, RY        |
| H-07 | Door switch, RH                  | RY            |
| H-08 | Door switch, LH                  | RY            |
| H-09 | Cigarette lighter                | LY, RL, B     |
| H-10 | Auto clock                       | B, RG, LY, GY |
| H-11 | Luggage compartment light        | LY, RB        |
| H-12 | Luggage compartment light switch | RB            |
| H-13 | Glass hatch release switch       | LR, GR        |
| H-14 | Glass hatch release solenoid     | GR, B         |
| H-15 | Fuel-door release switch         | LR, GB        |
| H-16 | Fuel-door release solenoid       | GB, B         |

## 2 · Feeds

| Bus    | Source                  | Fuse | Feeds                                                                            |
|--------|-------------------------|------|----------------------------------------------------------------------------------|
| **LY** | WR constant → X-04 15 A | 15 A | Interior light, spot light, lighter, clock, luggage light, ignition switch light |
| **LO** | WR constant → X-04 20 A | 20 A | Glove box light, seat belt warning                                               |
| **LR** | WR constant → X-04 20 A | 20 A | Hatch release, fuel-door release                                                 |
| **GY** | IG → X-04 10 A          | 10 A | Seat belt warning, key reminder, clock                                           |
| **RG** | Dimmer bus (Section E)  | —    | Lighter and clock illumination                                                   |

The interior lighting bus is **constant-hot** — it must work with the key out.
Door switches (H-07 / H-08) are **switch-to-ground on RY**, exactly the topology
the PMU wants.

## 3 · Control Processing Unit

The same X-16 module family that runs the flasher and wiper intermittent also
handles: seat belt warning, key reminder buzzer, lights-off reminder chime. It
takes GY, GB, G, GL, RY, Br, BrW and drives the chime and warning lamps.

**All of this collapses into PMU software.** The module disappears.

## 4 · Hatch and fuel door

Both are solenoid pulls on a 20 A constant feed, switched by a dash button:

| Path                                                       | Wire |
|------------------------------------------------------------|------|
| LR → H-13 hatch switch → GR → H-14 solenoid → B → X-15     | GR   |
| LR → H-15 fuel-door switch → GB → H-16 solenoid → B → X-15 | GB   |

## 5 · What this means for the rebuild

| Factory | PMU-24 plan |
|---|---|
| LY constant interior bus | O20 PWM interior bus → **L4-M 8** (F12 branch); a true constant lives on the busbar (D-020) |
| Door switches to ground on RY | A6 door pin ladder — **D1 3 / D2 3 → L4-S 2**; same topology |
| Control Processing Unit (chime, belt, key reminder) | Deleted; chimes dropped (Q-021 → D-050) |
| Cigarette lighter on LY | **Deleted** (D-095) |
| Auto clock on LY constant | Constant bus off the PMU (D-020) — the PMU sleeps |
| Luggage compartment light + switch | O20 bus; the switch joins the A6 ladder as a fourth state via **L4-S 3** (A-012) |
| Hatch release solenoid | **L4-M 3** — **no output yet**, `Q-061`. Latch switch broken, K-016 |
| Fuel-door release solenoid | **L4-M 4** — never existed (V-034 → D-098), new part `T-032`; output `Q-061` |
| Glove box light | O20 bus |
| Seat belt warning | Dropped (D-050) |

## 6 · Unknowns

| ID | Unknown | Resolve by |
|---|---|---|
| V-033 | Hatch and fuel-door solenoids have no output | The `Q-061` packet, Checklist 0.23 |
| V-034 → D-098 | Solenoid state | Hatch switch broken; fuel-door solenoid never existed |
| Q-021 → D-050 | Chimes | Dropped |

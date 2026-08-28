# Circuit — Interior, Doors, Hatch, Fuel Door, Accessories

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

| Factory                                             | PMU-24 plan                                                         |
|-----------------------------------------------------|---------------------------------------------------------------------|
| LY constant interior bus                            | O20 PWM interior bus, C5-B1 (D-020 keeps a true constant elsewhere) |
| Door switches to ground on RY                       | A6 door pin ladder, C5-B2 — same topology, no change needed         |
| Control Processing Unit (chime, belt, key reminder) | Deleted, all software                                               |
| Cigarette lighter on LY                             | O10 accessory bus, C6-1                                             |
| Auto clock on LY constant                           | **Constant bus off the PMU** (D-020) — the PMU sleeps               |
| Luggage compartment light + switch                  | O20 bus, C4-B9 spare                                                |
| Hatch release solenoid                              | C4-B8 spare, already reserved in SPEC                               |
| Fuel-door release solenoid                          | **No channel allocated** — `[V-033]`                                |
| Glove box light                                     | O20 bus                                                             |
| Seat belt warning                                   | Software, or dropped                                                |

## 6 · Unknowns

| ID    | Unknown                                                                      | Resolve by                     |
|-------|------------------------------------------------------------------------------|--------------------------------|
| V-033 | Fuel-door release solenoid has no channel. Needs a C4 spare                  | Allocate during next SPEC pass |
| V-034 | Are the hatch and fuel-door solenoids still working?                         | Inspect car                    |
| Q-021 | Keep the seat belt warning and key reminder chime in software, or drop them? | Decide                         |

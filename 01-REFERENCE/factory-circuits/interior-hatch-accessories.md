# Circuit — Interior, Doors, Hatch, Fuel Door, Accessories

*Rev 2026-09-07 · owns: the factory decode of this circuit — devices, wires, logic. Nothing of the new design lives here; the last section says where it does.*

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

The rebuild's side of every device and wire above is the electrical build's record, not this file's: find a factory code in its data — `python tools/rx7.py -p electrical-build find "C-02"` — or read the rendered [`DESIGN.md`](../../02-PROJECTS/electrical-build/01-DESIGN/DESIGN.md) §12 (device ends) and [`WIRE-TABLES.md`](../../02-PROJECTS/electrical-build/03-INSTALL/WIRE-TABLES.md). A hand-copied mapping table stood here until 2026-09-07; it had drifted three decisions behind and was removed — one fact, one home. Decisions that shaped this circuit's rebuild: D-020 · D-050 · D-095 · D-098 · D-180.

## 6 · Unknowns

Every unknown this decode raised has an ID. The open ones live in the projects' `QUESTIONS.md` files (electrical, luxury, engine swap); the closed ones are cited with their closer in the projects' `DECISIONS.md`. This circuit's: Q-021 · Q-061 · V-033 · V-034.

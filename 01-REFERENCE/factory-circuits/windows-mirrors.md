# Circuit — Power Windows & Remote Mirrors

**Source:** Section I, page 28.

---

## 1 · Power windows

| Ref | Device | Pins |
|---|---|---|
| I-06 | Power window switch LH | RL, B / GL, BL |
| I-07 | Power window switch RH | R, B / G, BL |
| I-09 | Power window motor LH | R, G |
| I-11 | Power window motor RH | R, G |
| I-08 | Front↔door harness connector LH | RL/GL → R/G |
| I-10 | Inpane↔door harness connector RH | R/G |

| Item | Value |
|---|---|
| Feed | Ignition **IG** → BW → X-04 **30 A** → **BL** |
| Motors | **2 wires each** (R, G) — polarity reversal drives up/down |
| Switch topology | Each switch is a **DPDT reverser** — both motor legs land on the switch |
| Ground | BL common, B → X-13 |

**Confirms A-004** — two conductors per motor, four total into the doors. The
factory switches do the reversing directly; the rebuild moves that to relays on
the panel (D-021) and the switches become PMU-side commands.

Note the factory feed is a single **30 A** fuse for both windows. That is the
number to size the motor bus against, not two separate loads.

## 2 · Remote control mirrors

| Ref | Device | Pins |
|---|---|---|
| I-01 | Remote control mirror switch | B, WG, LgR / Lg, LgB, LgY |
| I-03 | Remote control mirror LH | LgY, Lg, B, LgB |
| I-05 | Remote control mirror RH | LgY, Lg, B, LgB |

| Item | Value |
|---|---|
| Feed | WR constant → X-04 **10 A** → WG |
| Motors | Two motors per mirror (horizontal + vertical), 4 wires per side |
| Select | The switch does LH/RH selection **and** direction |
| Ground | B → X-13 |

These are **motor-driven mirrors, not heated mirrors.** SPEC allocates C5-B3 and
C5-B4 to *heated* mirrors off the comfort bus, and C5-B5…B8 as spares for mirror
motors. Four wires per side means the spares are exactly consumed — there is no
margin left in C5 if both functions are wanted.

## 3 · What this means for the rebuild

| Factory | PMU-24 plan |
|---|---|
| 30 A window fuse | O1 motor bus (25 A, flyback), relay bank does reversing |
| DPDT window switches in the doors | C3-15…18 switch inputs, relays on the panel (D-021) |
| 2-wire motors | C5-A1…A4, four heavy legs |
| Mirror switch on 10 A constant | C5-B5…B8 spares — **tight, see below** |
| Mirror motors, 4 wires per side | Consumes all four C5 signal spares |

## 4 · Unknowns

| ID | Unknown | Resolve by |
|---|---|---|
| V-035 | **C5 spare count.** Remote mirror motors need 8 conductors total; C5-B5…B8 is only 4 spares. Either C5 grows or the mirrors go on their own sub-connector at the door | Recount during the next SPEC audit |
| V-036 | Are the power mirrors and windows currently working? | Inspect car |
| Q-022 | Keep remote mirror motors, or go manual and use the spares for heated mirrors only? | Decide |

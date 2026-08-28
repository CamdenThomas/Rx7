# CUT LIST & LABEL SCHEDULE

*Template. Lengths are **blocked on T-008** — measure every route with string,
add 15%, then Claude fills this in.*

---

## Label format

Every wire gets a label at **both ends**. Every connector gets one on the housing.

```
   <ORIGIN>-<CAVITY> / <DESTINATION>
```

Examples:

| Label | Reads as |
|---|---|
| `O8 / L2-M1` | PMU channel O8 → leg 2 medium connector, cavity 1 |
| `L2-M1 / WIPER-LO` | Leg 2 medium cavity 1 → the wiper motor low brush |
| `A7 / L4-S1` | PMU input A7 → leg 4 signal connector, cavity 1 |
| `K5-87 / D1-1` | Relay K5 terminal 87 → driver door connector, cavity 1 |

**Both ends carry the same pair, read in opposite order.** Pick up any wire
anywhere and you know both where it came from and where it goes.

Heat-shrink sleeve labels, printed. Not tape, not marker — both fail in a
loom within a year.

## Connector labels

Each housing gets its code on the shell: `L1-P`, `L3-S2`, `D1`, `DP-ICU`.
Both halves. A leg cannot then be plugged into the wrong receptacle even if
the keying somehow allows it.

## Relay and fuse labels

Label the **plate itself**, not the component — components get swapped.

| Position | Label |
|---|---|
| K1–K4 | `POPUP-L-A`, `POPUP-L-B`, `POPUP-R-A`, `POPUP-R-B` |
| K11 | `CONST-MASTER` |
| F1–F13 | Function + rating, e.g. `HEAD-UNIT-CONST 15A` |

---

## Cut list — to be filled after T-008

One row per conductor. Grouped by leg so it can be cut leg by leg.

### L1 · ENGINE

| Cavity | Circuit | AWG | Colour | Length | Qty |
|---|---|---|---|---|---|
| L1-P 1 | Ignition / coil feed | 12 | RED/BLU | | 1 |
| L1-P 2 | LS ECU reserve | 12 | RED/ORN | | 1 |
| L1-P 3 | LS fan reserve | 12 | RED/GRY | | 1 |
| L1-P 4 | Spare heavy | 12 | RED | | 1 |
| L1-S… | *see PIN-MAP* | 16 | GRY/* | | 17 |

### L2 · FRONT CHASSIS

| Cavity | Circuit | AWG | Colour | Length | Qty |
|---|---|---|---|---|---|
| L2-P1 1–2 | Headlight LOW / HIGH | 12 | RED/BLK, RED/BRN | | 2 |
| L2-P1 3–4 | Pop-up LH legs A/B | 12 | RED/WHT | | 2 |
| L2-P2 1–2 | Pop-up RH legs A/B | 12 | RED/WHT | | 2 |
| L2-M… | Wipers, horn, washer, turn, park | 14–16 | ORN/*, VIO/* | | 7 |
| L2-S… | Pop-up ladders, park sense, +5 V | 16 | GRY/*, PNK | | 4 |

### L3 · DASH

| Cavity | Circuit | AWG | Colour | Length | Qty |
|---|---|---|---|---|---|
| L3-P 1–2 | Blower, comfort bus | 12 | RED/PNK, RED/VIO | inches | 2 |
| L3-M 1–2 | Accessory, head unit constant | 14 | ORN/YEL, RED | inches | 2 |
| L3-S1/S2/S3 | *see PIN-MAP* | 16 | various | inches | 29 |

### L4 · REAR CABIN

| Cavity | Circuit | AWG | Colour | Length | Qty |
|---|---|---|---|---|---|
| L4-P 1–2 | Defog, fuel pump | 12 | RED/GRN, RED/YEL | | 2 |
| L4-P 3 | Window motor bus → sill | 12 | RED/WHT | | 1 |
| L4-M… | Lamps, solenoids, window commands | 14–16 | ORN/*, VIO/* | | 10 |
| L4-S… | Sender, door pins, radar, +5 V | 16 | GRY/*, PNK | | 8 |
| D1 / D2 | Door branches, sill → door | 14–16 | various | | 16 |

### Power backbone

| Run | AWG | Length | Qty |
|---|---|---|---|
| Battery + → Class-T | 2 | inches | 1 |
| Class-T → disconnect → dash post | 2 | | 1 |
| Battery − → rear ground stud | 2 | | 1 |
| Starter feed | 1/0 or 2 | | 1 |
| PMU pin 25 → ground bus | 10 | ≤6 in | 1 |

---

## Ordering rule

**Add 20% to every wire quantity and every terminal count.** You will miscut,
you will ruin crimps, and a second order costs shipping and two weeks.

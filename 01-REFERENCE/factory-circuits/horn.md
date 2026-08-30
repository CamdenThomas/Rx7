# Circuit — Horn

*Rev 2026-08-30 · owns: the factory decode of this circuit — devices, wires, logic. The rebuild table at the foot points into the new design and is not its owner; cavities are `02-HARNESS/data/connectors.csv`'s.*

**Source:** Section F, page 22 (schematic), page 23 (harness routing).
**Type:** Constant-hot, relay-switched, ground-side triggered.
**Shares its fuse with:** stop lights (both on the same 15 A).

---

## 1 · Devices

| Ref  | Device                                | Location                | Connector | Pins       |
|------|---------------------------------------|-------------------------|-----------|------------|
| F-16 | Horn relay                            | Engine bay / cowl       | 3-pin     | GW, GY, GL |
| F-09 | Horn, LH                              | Behind front bumper, LH | 1-pin     | GY         |
| F-10 | Horn, RH                              | Behind front bumper, RH | 1-pin     | GY         |
| —    | Horn switch                           | Steering wheel pad      | via E-01  | GL         |
| X-07 | Fusible link, 1.25 sq                 | At battery              | —         | —          |
| X-04 | Fuse block, 15 A position             | Under dash              | —         | —          |
| E-01 | Combination switch / column connector | Steering column         | —         | —          |

Both horns are **single-wire** — they ground through their mounting bracket to
the body. The horn switch also grounds through the column.

## 2 · Wire runs

| # | Color | Meaning                        | From        | To                       | Notes                                     |
|---|-------|--------------------------------|-------------|--------------------------|-------------------------------------------|
| 1 | —     | Battery +                      | Battery     | X-07 fusible link        | 1.25 sq                                   |
| 2 | WR    | White/red — constant hot       | X-07        | X-04 fuse block          | Main constant bus, feeds many circuits    |
| 3 | GW    | Green/white — fused constant   | X-04 (15 A) | F-16 relay               | Feeds relay coil **and** contact together |
| 4 | GL    | Green/blue — coil ground path  | F-16 relay  | Horn switch via E-01     | Switch closes to ground → relay pulls in  |
| 5 | GY    | Green/yellow — switched output | F-16 relay  | F-09 and F-10 (parallel) | Splices to both horns                     |
| 6 | —     | Ground                         | F-09, F-10  | Body via bracket         | Not a wire                                |
| 7 | —     | Ground                         | Horn switch | Column / body            | Not a wire                                |

## 3 · Logic

Relay coil and contact share one feed (GW). The coil's other end (GL) runs up
the column to the horn switch, which is a simple momentary switch to ground.
Press it → coil energises → contacts close → GY goes hot → both horns sound.

This is a **ground-side switched** circuit. The horn switch never carries horn
current, only coil current, which is why a thin wire and a slip ring survive it.

## 4 · What this means for the rebuild

| Factory | PMU-24 plan | Change |
|---|---|---|
| 15 A fuse shared with stop lights | O11, own 15 A soft fuse | Horn gets its own protected channel |
| F-16 horn relay | Deleted | PMU output switches the horns directly |
| GL coil ground → horn switch | Horn switch closure → wake diode to pin 7 (D-072, L3-S1 11). Its PMU *input* is still `Q-063` | Same electrical behaviour, no relay |
| GY output splice to two horns | **L2-M 3**, 14 AWG, splices to both horns at the nose | Same topology |
| Horns ground via bracket | Front star ground node (D-017) | Deliberate ground, not a bracket |

## 5 · Unknowns

| ID | Unknown | Resolve by |
|---|---|---|
| V-021 | Horn current draw — not stated on the diagram | Clamp meter, `T-014` ([`METER-SESSION.md`](../../02-PROJECTS/electrical-pmu/05-BUILD/METER-SESSION.md) 1.7) |
| V-022 → D-097 | Both horns present and original | Confirmed on inspection, `T-010` done |
| Q-018 → D-072 / `Q-063` | The horn switch as a PMU input | Wake source settled; the input pin is in the `Q-063` packet |

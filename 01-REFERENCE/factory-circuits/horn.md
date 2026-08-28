# Circuit — Horn

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

| Factory                           | PMU-24 plan                                       | Change                                 |
|-----------------------------------|---------------------------------------------------|----------------------------------------|
| 15 A fuse shared with stop lights | O11, own 15 A soft fuse                           | Horn gets its own protected channel    |
| F-16 horn relay                   | Deleted                                           | PMU output switches the horns directly |
| GL coil ground → horn switch      | Horn switch becomes a PMU input, switch-to-ground | Same electrical behavior, no relay     |
| GY output splice to two horns     | C2-B2, 14 AWG, splices to both horns at the nose  | Same topology                          |
| Horns ground via bracket          | Front star ground node                            | Deliberate ground, not a bracket       |

**Open:** the horn switch is not currently allocated a PMU input. A1–A8 are all
assigned and the shared pins are all claimed. Options are the CAN keypad, or
folding it onto an existing ladder. Logged as `Q-018`.

## 5 · Unknowns

| ID    | Unknown                                           | Resolve by         |
|-------|---------------------------------------------------|--------------------|
| V-021 | Horn current draw — not stated on the diagram     | Clamp meter, T-002 |
| V-022 | Whether both horns are still present and original | Inspect car        |

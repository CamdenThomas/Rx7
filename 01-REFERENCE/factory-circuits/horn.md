# Circuit — Horn

*Rev 2026-09-07 · owns: the factory decode of this circuit — devices, wires, logic. Nothing of the new design lives here; the last section says where it does.*

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

The rebuild's side of every device and wire above is the electrical build's record, not this file's: find a factory code in its data — `python tools/rx7.py -p electrical-build find "C-02"` — or read the rendered [`DESIGN.md`](../../02-PROJECTS/electrical-build/01-DESIGN/DESIGN.md) §12 (device ends) and [`WIRE-TABLES.md`](../../02-PROJECTS/electrical-build/03-INSTALL/WIRE-TABLES.md). A hand-copied mapping table stood here until 2026-09-07; it had drifted three decisions behind and was removed — one fact, one home. Decisions that shaped this circuit's rebuild: D-017 · D-072 · D-182.

## 5 · Unknowns

Every unknown this decode raised has an ID. The open ones live in the projects' `QUESTIONS.md` files (electrical, luxury, engine swap); the closed ones are cited with their closer in the projects' `DECISIONS.md`. This circuit's: Q-018 · Q-063 · T-010 · V-021 · V-022.

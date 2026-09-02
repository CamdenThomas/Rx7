# ROADMAP — from here to a car on the PMU

Written 2026-08. The sequence that gets from planning to prepping, with the
buy order attached to what it unblocks.

---

## First, one correction about "dual system"

You cannot run both systems on the **same load** — they'd back-feed each other.
What you run in parallel is **two independent power systems**, with each load
belonging to exactly one of them at any moment.

| What runs in parallel | What doesn't |
|---|---|
| Two battery feeds, two fuse paths, two harnesses physically in the car | One lamp fed by both |
| Old harness serving 40 circuits while the new one serves 3 | Any circuit half-migrated |

The migration is **per circuit**: unplug the load from the factory connector,
tape and label the factory end `MIGRATED` with the date, land it on the new
harness, enable one PMU output, measure, set the soft fuse, log it. That's
D-023/024, and it's already the plan — this is just naming it precisely.

**The hard rule:** the car drives home at the end of every session. Never start a
cutover you can't finish or reverse before dark.

---

## STEP 1 · Buy the unblockers — ~$290, this week

Nothing here waits on an open question. All of it unblocks work you can do now.

| Item | ~$ | Unblocks |
|---|---|---|
| DMM with DC current clamp | 40–60 | **Every measurement task.** T-014, T-015, T-016 |
| 3 × Teensy 4.1, 6 × TCAN transceivers, sockets, protection passives | 130 | **All firmware.** CAN bring-up, sensor scaling, display work |
| Spare Sicma housing + terminals | 60–120 | Bench mule. **Never practise on the real housing** |
| Plywood, ground bus, fused feed for the bench board | 40 | Phase 2a |

**This is the whole gate.** Under $300 and it opens three parallel tracks.

---

## STEP 2 · Two measurement sessions with the car

Do these before anything is ordered that depends on them.

### Session A — the meter session, half a day
| Task | Gets you |
|---|---|
| T-014 | Clamp every load, inrush and steady. **Sets every wire gauge and soft fuse** |
| T-015 | Pop-up stall current, both sides |
| T-016 | **Diagnose K-008** — voltage-drop X-13 and X-15 with the blinker running |
| T-004 | Alternator rating off the case |

T-014 is irreversible-window work. Once the harness is out it can never be done.

### Session B — the tape measure and eyeballs session, half a day
| Task | Gets you |
|---|---|
| T-007 | **Dash envelope** → unblocks the panel drawing and the panel parts order |
| T-024 | Cargo bin → unblocks the battery mount order |
| T-008 | Harness routes with string, +15% → **unblocks the wire cut list** |
| T-010 | Inspection sweep — clears 12 verify items in one pass |
| T-011, T-012, T-023 | Pop-up limit pinout, fuel sender ohms, ignition switch outputs |
| T-018, T-019 | Harness photos, find the wideband tap and PO splices |

**Two half-days clears almost every blocked item in the project.**

---

## STEP 3 · Three tracks run in parallel

### Track A — PMU config (apartment, semester)
Bench mule, learn the client, build and verify all six ladders, configure wipers,
lighting, crank logic, keep-alive. **35–55 hrs, needs only the PMU.**

### Track B — Firmware (laptop, semester)
CAN bring-up between two Teensys, message map, sensor scaling, display
prototyping on a breadboard. **80–200 hrs, needs no car at all.**

### Track C — Dash design
Blocked until T-007. Then: panel 1:1 drawing → display format `[Q-037]` →
bezel and switch panel fabrication. Runs alongside everything else.

---

## STEP 4 · Buy in dependency order

| # | What | ~$ | Wait for |
|---|---|---|---|
| 1 | **The $290 unblockers** | 290 | nothing |
| 2 | Battery mount, tray, backing plate | 90–180 | T-024 |
| 3 | Class-T, disconnect, PowerPost, heavy cable, lugs | 430–650 | nothing |
| 4 | Deutsch crimper + coupon stock | 80–250 | nothing |
| 5 | CAN keypad, 8-key | 300–450 | Track A underway |
| 6 | Relays, sockets, fuse block, busbars, backer plate | 360–640 | **T-007** |
| 7 | **Connector and wire order** | 1,000–1,700 | **Q-033, T-008** |
| 8 | Display, servos, senders, PCBs | 230–500 | Track B proves what's needed |

**Item 7 is the one to hold.** It's the biggest single spend, and it depends on
both a decision and a measurement.

---

## STEP 5 · Build order

| Phase | When | Ends with |
|---|---|---|
| 3 · Power backbone | Winter break | Car drives on a new battery, new feed, new grounds. **Factory harness untouched** |
| 4 · Panel build | Winter break | Panel bench-tested, all 39 cavities terminated and continuity-checked |
| 5 · Harness legs | Spring semester | Four legs + sill node, built and tested on the bench |
| 6 · Install & migrate | Summer | **Dual system live.** Circuit-by-circuit cutover |
| 7 · Factory harness out | Summer | Pulled intact, boarded as reference |
| 8 · Shakedown | Summer | Soft fuses set from measurement, final loom wrap |

**Migration order** — least to most consequential, so a bad day never strands you:
interior/hatch → lighter and USB → horn → wipers/washer → tail/park/marker →
brake → turn → reverse → defog → headlights → pop-ups → windows → blower →
fuel pump → ignition → **start last**.

---

## STEP 6 · Modules join a finished car

D-081. The car completes on dumb switches and the factory harness comes out
*before* the DCU and ICU are connected. Factory cluster stays in during ICU
development (Q-039), so you keep working gauges the whole time.

DCU and ICU land through late 2027 into 2028.

---

## The short version

1. Spend **$290** this week.
2. Give the car **two half-days** with a meter and a tape measure.
3. Start **PMU config and firmware** in parallel — both are apartment work.
4. Answer **Q-033** and you can place the wire order.
5. Backbone and panel over **winter break**.
6. Legs in **spring**, migration in **summer**.
7. Car finished **~July 2027**. Modules through 2028.

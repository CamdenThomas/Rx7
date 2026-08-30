# STATUS — where the project is

*Rev 2026-08 · owns: current state. Refresh at the end of every session.*
*If you read one file after a long gap, read this one.*

---

## In one paragraph

The 1982 RX-7's electrical system is being replaced with an ECUMaster PMU-24 DL,
a rear-mounted Ionic S9 lithium battery, four modular harness legs, and two
Teensy CAN modules — a climate DCU and an instrument cluster ICU. **The car runs
on its stock incandescent bulbs throughout**; LED conversion and custom lamps are
a separate deferred project. The PMU, battery, Teensys and transceivers are in
hand. **Firmware Stages 1–3 are complete and the CAN software stack is proven.**
Nothing has been cut, crimped or installed on the car.

## Scope boundary

| This project | `lighting-body/` |
|---|---|
| Channels, gauge, connectors, soft fuses, flash logic | LED bulbs, custom tail lights, headlamp units |
| Working lamps on **stock bulbs** | Any change to what's *in* the socket |
| Inrush config for filament (D-120) | Second-pass fuse reset after the bulb change (D-122) |

## Hardware in hand

PMU-24 DL + connector + 39 terminals · Ionic S9 · 3 × Teensy 4.1 ·
5 × SN65HVD230 · UT210E clamp meter · 1 micro-USB cable · 2 spare housings inbound

**Connector confirmed:** 12 large `FCI`, 27 small `FCI 125`, **zero small
spares**. Pin 1 top-left, opposite the purple lock — orientation closed (D-139).

## Phase state

| Phase | State |
|---|---|
| 0 · Documentation & measurement | **Started.** First meter readings taken. Session is ~10–12 hrs total, not half a day |
| 1 · Order & practice | Wire order held on T-008 |
| 2A · PMU configuration | **Unblocked.** PMU in hand. Needs 120 Ω ×4 and a 5 A fuse |
| **2B · Firmware** | **Stages 1–3 COMPLETE.** 4 and 5 written and unblocked |
| 3 · Power backbone | Parts not ordered. Winter break |
| 4 · Panel build | Blocked on Q-014 / T-007 |
| 5 · Harness legs | Blocked on T-008 |
| 6–8 · Install, migrate, shakedown | Summer 2027 |
| 9 · Modules | Late 2027 → 2028 |

## Firmware progress

| Stage | State |
|---|---|
| 1 · Toolchain, blink | ✅ Board 1. **Flash + label boards 2 and 3** |
| 2 · `can_map.h` validation | ✅ All passed. Found and fixed a real bug in the temperature macros |
| 3 · CAN loopback, 500 kbps | ✅ All passed. 5 frames, byte-identical payloads, dispatch and timeout working |
| 4 · Ladder decode | Sketch written. **Unblocked** — self-tests with no hardware |
| 5 · Tach measurement | Sketch written. **Unblocked** — one jumper, pin 3 → 4 |
| 6 · SD config | Needs a microSD card |
| 7 · Datalogging | After 6 |

**Library: ACAN_T4, not FlexCAN_T4.** Only ACAN_T4 exposes loopback cleanly.

## The three biggest blockers

| # | Blocker | Unblocks | Needs |
|---|---|---|---|
| 1 | **T-014** clamp every load | Every soft fuse. **Irreversible window** | Meter in hand — session part-done |
| 2 | **T-007** dash envelope | Panel drawing, panel parts order, Phase 4 | **A tape measure** |
| 3 | **T-008** harness routes | Cut list, the $1,000–1,700 wire order, Phase 5 | **String** |

## Do now — needs nothing in the post

| Task | Needs |
|---|---|
| **Firmware Stages 4 and 5** | A jumper wire |
| **T-007** dash cavity envelope | Tape measure |
| **T-008** harness routes, +15% | String |
| **T-028** sill space | Tape measure |
| Finish the meter session — parts 1–5 | Meter, in hand |
| Flash and label boards 2 and 3 | Nothing |
| Install the PMU client, read `V-065` CAN export | A download |
| T-018 harness photographs · T-019 find PO splices | A phone, eyes |

## Money

| | |
|---|---|
| Committed | ~$3,005–3,405 |
| Remaining | ~$3,400–6,100 |
| Project total | ~$6,500–9,500 |
| **Buy next** | Bench kit remainder, **~$110–165** — see `05-BUILD/BENCH-KIT.md` |
| Then | Battery mount, Class-T, 2 AWG — ~$540–880, before Phase 3 |
| **Hold** | Wire and connector order until T-008 |

## Open decisions

| ID | Question |
|---|---|
| **Q-014** | Dash envelope — a measurement, not a decision. **Blocks Phase 4** |
| Q-028 | CAN wake latency — not live until the MCU exists |
| V-069 | Open-barrel crimper die size — confirm against a real terminal |
| V-065 | PMU's own CAN export format — **gates all firmware** |
| V-067 | Tach pulses per revolution — confirm against the car |

**Only two questions remain open**, and one of them isn't live yet.

## Recently settled

D-134 PMU received, cavity layout confirmed · D-139 connector orientation closed ·
D-141 bench mule dropped · D-144 no bench PSU · D-148 start relay on the inner
fender · D-149 head unit criteria — physical buttons, green LEDs, wireless
CarPlay, **full passthrough critical** · D-150 **cluster is one wide display**,
which forces a framebuffer controller rather than plain SPI

## Rule that governs the build

The car drives home at the end of every session. Never start a cutover you can't
finish or reverse before dark.

## If you have been away a year

`STATUS.md` → project `README.md` → `01-DESIGN/GLOSSARY.md` →
`01-DESIGN/SPEC.md` → `05-BUILD/CHECKLIST.md`. About forty minutes.

---

# PROGRESS ASSESSMENT — 2026-08

## Effort by phase, and what is actually done

| Phase | Est. hrs | Done | State |
|---|---|---|---|
| 0 · Documentation & measurement | 55–85 | ~10% | **Paperwork advanced, measurement not started** |
| 1 · Order & practice | 10–16 | 0 | Held on T-008 |
| 2A · PMU configuration | 25–40 | ~0 hrs entered, **but fully specified** | See below |
| **2B · Firmware** | **155–325** | **~80–110 hrs** | **The bulk of what has been achieved** |
| 3 · Power backbone | 18–28 | 0 | |
| 4 · Panel build | 49–74 | 0 | Blocked on T-007 |
| 5 · Harness legs | 98–162 | 0 | Blocked on T-008 |
| 6 · Install & migrate | 75–125 | 0 | |
| 7 · Factory harness out | 8–14 | 0 | |
| 8 · Shakedown | 35–60 | 0 | |

**Roughly 90–125 hours of 531–932 complete — about 12–18%.**

## Where the time actually went

Phase 2B is far further along than the schedule assumed:

| Delivered | |
|---|---|
| Bring-up stages 1–5 | All passed |
| `can_map.h` | Finalised and validated |
| `cluster_core.h` | ~1000 lines. Framebuffer, dirty tiles, every widget, full layout |
| `stats.h` | Trip and lifetime accumulators, CSV export, trip page |
| `icu.ino` | Teensy host, tile push |
| Desktop simulator | Runs the real firmware, not a mock |
| Page framework | Drive, diagnostics, trip |
| PMU simulator | Vehicle model, channel table, scripted drive cycle |
| **Regression suite** | **415 assertions, 13 groups. Found 4 real bugs** |

**The ICU display side is roughly 60–70% complete.** What remains in 2B: the
display driver (3 calls, blocked on panel choice), the entire DCU, analog
conditioning, carrier PCBs, and `V-065` reconciliation.

## Phase 2A is specified but not entered

`PMU-CONFIG.md` now holds every decode table, output expression, interlock and
timer. **The thinking is done; only typing remains.** Realistically **12–20 hrs**
rather than 25–40, and it needs nothing but the PMU on a desk.

---

## The honest headline

**We are not ahead of schedule. We are consuming the available work faster than
expected.**

Split the estimate by what it needs:

| | Hours | Done |
|---|---|---|
| Laptop work — 2A, 2B, paperwork | 180–365 | **~90–125** |
| Physical work — measure, order, build, migrate | 333–544 | **0** |

**Roughly 35% of this project can be done at a desk. About a third of that is
finished. The other 65% has not started, and none of it can.**

## The rate is about to drop

Remaining laptop work: DCU firmware, carrier PCBs, wiring diagrams,
troubleshooting guide, conditioning schematics. Call it **60–120 hours.**

**After that, everything left needs measurements, parts, or the car.**

## The critical path

It is not firmware. Firmware was never on it. The path is:

```
measure  →  order wire  →  build panel  →  build legs  →  migrate  →  shake down
```

**Two tape-measure tasks gate all of it:**

| | Blocks | Needs |
|---|---|---|
| **T-007** dash envelope | Panel drawing, panel order, Phase 4 (49–74 hrs) | Tape measure |
| **T-008** harness routes | Cut list, the $1,000–1,700 wire order, Phase 5 (98–162 hrs) | String |

**Those two tasks gate 147–236 hours of downstream work** — more than a quarter
of the project — and between them take perhaps two hours in daylight.

**T-014**, the clamp session, is the third and the only irreversible one.

## Is July 2027 still real

**Yes, and the firmware lead helps** — Phase 2B was scheduled to run through late
2027 and is now well ahead, which removes it as a late-stage risk.

But the schedule was never limited by firmware. It is limited by **weekends with
the car**, and that count has not changed. The next genuine milestone is not code:
it is a tape measure and a ball of string.

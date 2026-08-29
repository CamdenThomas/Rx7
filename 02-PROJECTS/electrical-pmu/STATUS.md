# STATUS — where the project is

*Updated 2026-08. Refresh at the end of every session. If you read one file after
a long gap, read this one.*

---

## In one paragraph

The 1982 RX-7's entire electrical system is being replaced with an ECUMaster
PMU-24 DL, a rear-mounted Ionic S9 lithium battery, four modular harness legs,
and two Teensy CAN modules — a climate DCU and an instrument cluster ICU.
**The car will run on its stock incandescent bulbs throughout** — LED conversion
and custom lamps are now a separate deferred project (D-123). The PMU, battery
and full bench kit are bought and in transit. The design is complete on paper.
Nothing has been cut, crimped or installed.

## Scope boundary

| In this project | In `lighting-body/` |
|---|---|
| Channels, gauge, connectors, soft fuses, flash logic | LED bulbs, custom tail lights, headlamp units |
| Working lamps on **stock bulbs** | Any change to what's *in* the socket |
| Inrush config for filament (D-120) | Second-pass fuse reset after the bulb change (D-122) |

## Waiting on delivery — what that does and doesn't block

**Blocked until the boxes arrive:** Phase 2A bench mule, Phase 2B firmware
bring-up, and every current measurement.

**Not blocked — do these now:**

| Task | Needs |
|---|---|
| **T-007** dash cavity envelope | A tape measure |
| **T-008** harness routes, +15% | String and a tape measure |
| **V-063** tail light aperture | A tape measure |
| **T-028** sill space behind the kick panel | A tape measure |
| T-018 harness photographs | A phone |
| T-019 find the wideband tap and PO splices | Eyes |
| Install the PMU client on Windows | A download |
| Install Teensyduino + toolchain | A download |
| Read the PMU manual | It's in `01-REFERENCE/PMU_info/` |
| **V-065** export the PMU CAN format from the client | The client, once installed |
| Answer the open questions | A chair |

**T-007 and T-008 are two of the three biggest blockers in the whole project and
neither needs a single thing that's in the post.**

## Phase state

| Phase | State |
|---|---|
| Gate 0 · bench kit | **Bought.** Teensys in hand, transceivers + PMU imminent |
| 0 · Documentation & measurement | **Tape-measure half ready now.** Meter session ~10–12 hrs, not half a day |
| 1 · Order & practice | Wire order held on T-008 |
| 2A · PMU configuration | Ready the day the PMU lands |
| **2B · Firmware** | **STARTED. Stages 1–3 complete** — see below |
| 3 · Power backbone | Parts not ordered. Winter break |
| 4 · Panel build | Blocked on Q-014 / T-007 |
| 5 · Harness legs | Blocked on T-008 |
| 6–8 · Install, migrate, shakedown | Summer 2027 |
| 9 · Modules | Late 2027 → 2028 |

## Firmware progress — `03-MODULES/BENCH-BRINGUP.md`

| Stage | State |
|---|---|
| 1 · Toolchain, blink | ✅ Board 1 verified. **Flash + label boards 2 and 3** |
| 2 · `can_map.h` validation | ✅ **All checks passed.** Found and fixed a real bug in the temperature macros |
| 3 · CAN loopback, 500 kbps | ✅ **All checks passed.** 5 frames, byte-identical payloads, dispatch and timeout working |
| 4 · Ladder decode | Sketch written. Needs a pot or a jumper wire |
| 5 · Tach simulator | Sketch written. Needs one jumper wire |
| 6 · SD config | Needs a microSD card |
| 7 · Datalogging | After 6 |

**The entire CAN software stack is proven.** Transceivers replace loopback with a
wire — none of the existing code gets rewritten.

**Library decision: ACAN_T4, not FlexCAN_T4.** Only ACAN_T4 exposes loopback and
self-reception cleanly.

## The three biggest blockers

| # | Blocker | Unblocks | Needs |
|---|---|---|---|
| 1 | **T-014** clamp every load | Every soft fuse. **Irreversible window** | The meter, in transit |
| 2 | **T-007** dash envelope | Panel drawing, panel parts order, Phase 4 | **A tape measure. Do it today** |
| 3 | **T-008** harness routes | Cut list, the $1,000–1,700 wire order, Phase 5 | **String. Do it today** |

## Money

| | |
|---|---|
| Committed | ~$3,005–3,405 |
| Remaining | ~$3,300–6,000 |
| Project total | ~$6,400–9,400 |
| Next spend | Battery mount, Class-T, 2 AWG cable — ~$540–880, before Phase 3 |
| **Hold** | The wire and connector order until T-008 |

## Open decisions, by weight

| ID | Question |
|---|---|
| **Q-044** | Headlight strips inside the pop-up buckets, or fixed with pop-ups deleted? **Largest simplification left** |
| Q-014 | Dash envelope — a measurement, not a decision |
| Q-037 | Cluster display format |
| Q-046 | Tail light driver PCB or diode isolation? |
| Q-047 | Reverse section width |
| Q-042 | IMU on the ICU board? ~$5 now, a new PCB later |
| A-005 | Start relay location — recommend inner fender |
| A-007 | Pop-up limit ladder — resolved by T-011, not by deciding |

## Recently settled

D-091 2 AWG feed · D-092 one housing per door · D-093 new heated mirrors ·
D-095 lighter deleted · D-097 six subsystems confirmed gone · D-101 bench kit
bought · D-105 blinker fault not being fixed · CAN byte layouts finalised

## What to do next, in order

1. **Take a tape measure to the car this week.** T-007, T-008, V-063, T-028.
   Four measurements, no special tools, and they unblock two whole phases.
2. **Install the PMU client and Teensyduino** while you wait. Free, and it makes
   day one with the hardware productive instead of spent on setup.
3. **Answer Q-044.** It changes the front of the car more than anything else left.
4. When the boxes land: bench mule, then firmware.

## Rule that governs the build

The car drives home at the end of every session. Never start a cutover you can't
finish or reverse before dark.

## If you have been away a year

`STATUS.md` → project `README.md` → `01-DESIGN/GLOSSARY.md` →
`01-DESIGN/SPEC.md` → `05-BUILD/CHECKLIST.md`. About forty minutes.

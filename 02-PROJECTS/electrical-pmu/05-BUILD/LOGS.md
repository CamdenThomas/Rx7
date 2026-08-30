# LOGS — hand-written records

*Rev 2026-08-30 · owns: the PMU config version log, the firmware version log, the photo index and the session log — things nothing can generate automatically.*

> **`../03-MODULES/firmware/icu/stats.h` owns the automated figures** — max
> speed, max RPM, peak G, runtime, distance, min oil pressure, seconds above
> redline. Do not duplicate those here (D-163). This file is for what only a
> person can record.

---

## PMU config version log

[`CHECKLIST.md`](CHECKLIST.md) 2.21. Save, back up, and add a row **every time the config
changes**.

| Version | Date | What changed | File backed up? |
|---|---|---|---|
| RevA-01 | | Initial project, channels named to [`SPEC.md`](../01-DESIGN/SPEC.md) §4 | ☐ |
| | | | ☐ |
| | | | ☐ |
| | | | ☐ |

**Rule:** never overwrite a saved config. New version, new row. The one time you
need to roll back is the one time you won't have kept it. Send the exported
file to the agent and it gets archived under `99-ARCHIVE/`.

---

## Firmware version log

ICU and DCU. Same discipline. The ICU prints `ICU_FW_VERSION` (defined in
`firmware/icu/icu.ino`) on the serial console at boot; the DCU will do the
same once `dcu.ino` exists (F-001). When `can_map.h` changes, **both versions
bump together** ([`../03-MODULES/CAN-MESSAGES.md`](../03-MODULES/CAN-MESSAGES.md)).

| Node | Version | Date | What changed | Tagged in git? |
|---|---|---|---|---|
| ICU | 0.3.0-dev | 2026-08 | Stages 1–5 absorbed: CAN dispatch and timeout, ladder decode, tach capture, dirty-rectangle renderer, `stats.h` | ☐ |
| ICU | | | | ☐ |
| DCU | — | | not started | ☐ |

---

## Photo index

`T-018` (Checklist 0.12) generates dozens of harness photos. They are worthless
if you can't find the one you need in 2027.

**Naming:** `YYYY-MM-DD_<zone>_<subject>.jpg`
Example: `2026-09-14_dash_ignition-switch-connector.jpg`

**Store in:** `01-REFERENCE/photos/<zone>/` (the folder's own README repeats
this table).

| Zone | What to capture |
|---|---|
| `engine` | Every connector, the coil/igniter pair, the inhibitor switch, grounds |
| `front` | Pop-up motors and their connectors, headlight buckets, horns, cowl |
| `dash` | Behind the dash before anything is touched. Switch backs, cluster connector, fuse block |
| `rear` | Tank sender, rear lamp connectors, ground studs, hatch area |
| `doors` | Window regulator (manual), mirror wiring, door boot |
| `grounds` | **X-13, X-14, X-15 specifically**, before and after cleaning |
| `hacks` | Every PO splice and the wideband tap — K-001, K-002 (`T-019`) |

**Take more than you think you need.** The harness is coming out and it isn't
coming back. Photos are the only record of how it was.

---

## Session log

One line per working session. Keeps the calendar honest.

| Date | Phase | Hours | What got done | Car drives? |
|---|---|---|---|---|
| 2026-08 | 0A | ~3 | First meter sitting — brake, turn L/R recorded; tail read on the wrong wire | ☑ |
| 2026-08 | 2B | — | Bench Stages 1–5 passed, `cluster_core.h` + test suite (415 assertions) | ☑ |
| | | | | ☐ |
| | | | | ☐ |
| | | | | ☐ |

**The estimate is 531–932 hours** ([`CHECKLIST.md`](CHECKLIST.md)). Logging actual hours
against phases is the only way to know whether that number was any good — and
whether July 2027 is still real.

---

## Automated stats — where they live

`stats.h` accumulates two sets. **Neither is persisted yet** (D-162):

| Set | Resets |
|---|---|
| `trip` | Every wake |
| `life` | Never — **once SD persistence exists** (Stage 6) |

Peaks, totals and faults are listed in `firmware/icu/stats.h`. When persistence
lands, `statsToCsv()` writes one line per trip and this file gets a pointer to
the CSV rather than a copy of the numbers.

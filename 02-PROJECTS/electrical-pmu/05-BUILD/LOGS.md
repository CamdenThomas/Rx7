# LOGS — config versions, photos, session record

Three small logs that have nowhere else to live.

---

## PMU config version log

Checklist 2.24. Save, back up, and add a row **every time the config changes**.

| Version | Date | What changed | File backed up? |
|---|---|---|---|
| RevA-01 | | Initial project, channels named to SPEC | ☐ |
| | | | ☐ |
| | | | ☐ |
| | | | ☐ |

**Rule:** never overwrite a saved config. New version, new row. The one time you
need to roll back is the one time you won't have kept it.

Send the exported file to Claude and it gets archived alongside these documents.

---

## Firmware version log

DCU and ICU. Same discipline.

| Node | Version | Date | What changed | Tagged in git? |
|---|---|---|---|---|
| ICU | | | | ☐ |
| DCU | | | | ☐ |

**Both nodes should share a CAN header file.** When the message map changes,
both versions bump together — see `CAN-MESSAGES.md`.

---

## Photo index

T-018 generates dozens of harness photos. They are worthless if you can't find
the one you need in 2027.

**Naming:** `YYYY-MM-DD_<zone>_<subject>.jpg`
Example: `2026-09-14_dash_ignition-switch-connector.jpg`

**Store in:** `01-REFERENCE/photos/<zone>/`

| Zone | What to capture |
|---|---|
| `engine` | Every connector, the coil/igniter pair, the inhibitor switch, grounds |
| `front` | Pop-up motors and their connectors, headlight buckets, horns, cowl |
| `dash` | Behind the dash before anything is touched. Switch backs, cluster connector, fuse block |
| `rear` | Tank sender, rear lamp connectors, ground studs, hatch area |
| `doors` | Window motor, mirror wiring, door boot |
| `grounds` | **X-13, X-14, X-15 specifically**, before and after cleaning |
| `hacks` | Every PO splice and the wideband tap — K-001, K-002 |

**Take more than you think you need.** The harness is coming out and it isn't
coming back. Photos are the only record of how it was.

---

## Session log

One line per working session. Keeps the calendar honest.

| Date | Phase | Hours | What got done | Car drives? |
|---|---|---|---|---|
| | | | | ☐ |
| | | | | ☐ |
| | | | | ☐ |
| | | | | ☐ |
| | | | | ☐ |

**The estimate is 531–932 hours.** Logging actual hours against phases is the
only way to know whether that number was any good — and whether July 2027 is
still real.

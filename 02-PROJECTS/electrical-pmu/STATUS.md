# STATUS — where the project is

*Rev 2026-08-31 · owns: current state and next steps, one dashboard — refreshed at the end of every session. Money is [`05-PROCESS/BOM.md`](05-PROCESS/BOM.md)'s; the build sequence is [`04-BUILD/CHECKLIST.md`](04-BUILD/CHECKLIST.md)'s; history is [`05-PROCESS/DECISIONS.md`](05-PROCESS/DECISIONS.md)'s — this page carries no backlog (D-196).*

## Contents

1. In one paragraph · 2. Scope boundary · 3. In hand · 4. Phase state ·
5. Do next · 6. Money · 7. Open items · 8. Critical path · 9. If you have
been away a year

---

## 1 · In one paragraph

The 1982 RX-7's electrical system is being replaced with an ECUMaster PMU-24
DL, a rear-mounted Ionic S9 lithium battery, four modular harness legs plus a
sill node, and two Teensy 4.1 CAN modules — a climate DCU and an instrument
cluster ICU with a 12.3″ instant-on bar display (D-192/D-193). The car stays
on stock incandescent bulbs; lighting & body is deferred second-pass scope —
[`01-DESIGN/TAIL-LIGHTS.md`](01-DESIGN/TAIL-LIGHTS.md) (D-201, after shakedown).
**The design is complete and the measurement campaign is closed** (D-197):
every output has a fuse value, every input a final decode table, every cavity
a destination; the pop-up drive, wake network, horn/wink sensing and fuel
sender are all resolved against the real car. There is no bench phase — the
car is the bench (D-194) and the BOM is the single purchase ledger, by wave
(D-196). Nothing has been cut, crimped or installed yet. **Known fault: the
alternator is not charging (D-179). The new harness reproduces the factory
excitation circuit the old one likely lost — O12 → F15 → BW (D-198) — and
the unit is replaced only if it still refuses on correct wiring.**

## 2 · Scope boundary

| First pass — this build | Second pass — lighting & body (deferred, L-004) |
|---|---|
| Channels, gauge, connectors, soft fuses, flash logic | LED bulbs, custom tail lights, headlamp units |
| Working lamps on **stock bulbs** (D-119) | Any change to what's *in* the socket |
| Inrush config for filament (D-120) | Second-pass fuse reset after the bulb change (D-122) |

## 3 · In hand

PMU-24 DL with connector, 39 terminals and the USB-to-CAN adapter · Ionic S9
· 3 × Teensy 4.1 · 5 × SN65HVD230 (desk only) · UT210E clamp meter · 2 spare
Sicma housings inbound (`T-045` on arrival). Zero small terminal spares
(D-135) — Wave 1 fixes that before anything is crimped.

## 4 · Phase state

| Phase | Hrs | State |
|---|---|---|
| 0 · Documentation & measurement | 55–85 | **Meter work DONE (D-197).** Left: the 0B tape-measure session and the design freeze (0.20–0.22) |
| 1 · Order & practice | 10–16 | Waves 0–1 buyable now; Wave 2 waits on 0B ([`BOM.md`](05-PROCESS/BOM.md)) |
| 2A · PMU configuration | 12–20 | **In the car** (D-194) — slots after 6.2, fully written in [`PMU-CONFIG.md`](01-DESIGN/PMU-CONFIG.md) |
| 2B · Firmware | 155–325 | ~100–140 hrs done, ahead of schedule. ICU renders the full 1280×480 panel (F-011) with the BT817 driver written (F-008, timings await `V-084`); DCU logic split out and tested (F-001). All three desktop suites green: 415 + 35 + 33 |
| 3 · Power backbone | 18–28 | Parts are Wave 2a. Winter break |
| 4 · Panel build | 49–74 | Blocked on `T-007` only |
| 5 · Harness legs | 98–162 | Blocked on `T-008` only |
| 6–8 · Install, migrate, shakedown | 118–199 | Summer 2027 |
| 9 · Modules | — | Late 2027 → 2028 |

## 5 · Do next

**Camden — car and stores:**

1. **`V-081` ohm check at E-03** — R and RY to case at parked / mid /
   raised (D-199); settles the pop-up drive conductors in five minutes
2. **Wave 0 + Wave 1 buys** (~$55 total — [`BOM.md`](05-PROCESS/BOM.md) §3–§4)
3. **The 0B tape-measure session** — dash envelope **+ how deep the cluster
   brow shades** (`T-007`, decides the display glass via `V-085`), routes
   with string (`T-008`), cargo bin (`T-024`), sill (`T-028`), battery posts
   (`T-029`), photos, VIN
4. Freeze the design, print it, date it (0.20–0.22) → place the Wave 2 orders

**Agent — queued, nothing blocking** ([`05-PROCESS/FORWARD-WORK.md`](05-PROCESS/FORWARD-WORK.md)):
F-004 tach front end · F-005/F-006 cluster pages + diagnostics screen ·
F-003 sensor conditioning · X-003/X-004/X-006 docs. (F-011 + F-008 landed
2026-08-31 — run `icu_sim/sim.exe` to see the full-width cluster.)

## 6 · Money

[`BOM.md`](05-PROCESS/BOM.md) §1 — the only ledger: bought ~$2,950–3,350 · Wave 0 ~$30 ·
Wave 1 ~$20–45 · Wave 2 ~$2,800–4,750 (after 0B) · Wave 3 ~$510–1,170 ·
Wave 4 conditional. Electrical total ~$6,550–9,900; Wave 5 (lighting,
after shakedown — D-201) ~$400–980 on top.

## 7 · Open items

Everything undecided or unverified is [`05-PROCESS/OPEN.md`](05-PROCESS/OPEN.md)'s — currently:
three dormant questions (Q-014's depth figures, Q-028, Q-001 VIN) and the
working verifies, led by `V-081` (pop-up drive conductors, D-199), `V-084`/`V-085` (display chain), `V-069` (crimper die), `V-065` (PMU
CAN export). Decisions D-173–D-201 landed 2026-08-30/31 — the complete
ruling set; [`05-PROCESS/DECISIONS.md`](05-PROCESS/DECISIONS.md) is the only history.

## 8 · Critical path

```
V-081 + 0B measure  →  freeze + Wave 2 orders  →  winter: backbone + panel
→  spring: legs  →  summer 2027: install, configure in car, migrate, shake down
→  then: modules, replacements, someday the LS
```

One evening of tests and one daylight tape-measure session gate ~150–240
hours of build. The car drives home at the end of every session — never start
a cutover you can't finish or reverse before dark. Until telemetry re-sets
the fuses, harness verification carries the whole protection burden (D-175):
continuity-test every conductor, verify every cavity against PIN-MAP before
first power.

## 9 · If you have been away a year

[`STATUS.md`](STATUS.md) → [`README.md`](README.md) →
[`01-DESIGN/GLOSSARY.md`](01-DESIGN/GLOSSARY.md) →
[`01-DESIGN/SPEC.md`](01-DESIGN/SPEC.md) →
[`02-HARNESS/CAVITY-STATE.md`](02-HARNESS/CAVITY-STATE.md) →
[`04-BUILD/CHECKLIST.md`](04-BUILD/CHECKLIST.md) →
[`05-PROCESS/OPEN.md`](05-PROCESS/OPEN.md). About an hour. Then
[`02-HARNESS/diagrams/architecture.svg`](02-HARNESS/diagrams/architecture.svg)
and [`01-DESIGN/panel-sheet.svg`](01-DESIGN/panel-sheet.svg) for the picture.

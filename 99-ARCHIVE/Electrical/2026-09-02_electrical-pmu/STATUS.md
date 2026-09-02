# STATUS — where the project is

*Rev 2026-09-01 · owns: current state and next steps, one dashboard — refreshed at the end of every session. Money is [`05-PROCESS/BOM.md`](05-PROCESS/BOM.md)'s; the build sequence is [`04-BUILD/CHECKLIST.md`](04-BUILD/CHECKLIST.md)'s; history is [`05-PROCESS/DECISIONS.md`](05-PROCESS/DECISIONS.md)'s — this page carries no backlog (D-196).*

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
[`TAIL-LIGHTS.md` (archived)](../../99-ARCHIVE/Electrical/2026-08-31_lighting-body/TAIL-LIGHTS.md) (D-201, after shakedown).
**The design is complete and the measurement campaign is closed** (D-197):
every output has a fuse value, every input a final decode table, every cavity
a destination; the pop-up drive, wake network, horn/wink sensing and fuel
sender are all resolved against the real car. There is no bench phase — the
car is the bench (D-194) and the BOM is the single purchase ledger, by wave
(D-196). Nothing has been cut, crimped or installed yet. **Known fault: the
alternator is not charging (D-179). The new harness reproduces the factory
excitation circuit the old one likely lost — O12 → F15 → BW (D-198) — and
the unit is replaced only if it still refuses on correct wiring.**
**Scope subtraction 2026-09-01: the A/C system is deleted (D-211)** — compressor,
condenser, lines and the whole factory interlock chain come out, taking F4 and
K10 with them. Heat, defrost, blower and ventilation are untouched. Cooling
returns with the swap engine, and the engine leg carries **nothing** capped for
it in the meantime.

## 2 · Scope boundary

| First pass — this build | Second pass — lighting & body (deferred, L-004) |
|---|---|
| Channels, gauge, connectors, soft fuses, flash logic | LED bulbs, custom tail lights, headlamp units |
| Working lamps on **stock bulbs** (D-119) | Any change to what's *in* the socket |
| Inrush config for filament (D-120) | Second-pass fuse reset after the bulb change (D-122) |

**Deferred conductors are run and capped everywhere except the engine bay.**
Heated seats, mirrors, windows and radar all get their wire now, hidden and out
of the way (D-208(f)). **L1 is the exception** — it carries only what the
current engine needs, no stubs to nothing, and is rebuilt from scratch at the
swap (D-211, [`engine.md`](02-HARNESS/engine.md)).

## 3 · In hand

PMU-24 DL with connector, 39 terminals and the USB-to-CAN adapter · Ionic S9
· 3 × Teensy 4.1 · 5 × SN65HVD230 (desk only) · UT210E clamp meter · 2 spare
Sicma housings inbound (`T-045` on arrival). Zero small terminal spares
(D-135) — Wave 1 fixes that before anything is crimped.

## 4 · Phase state

| Phase | Hrs | State |
|---|---|---|
| 0 · Documentation & measurement | 55–85 | **Meter work DONE (D-197).** Left: the 0B tape-measure session and the design freeze (0.20–0.22) |
| 1 · Order & practice | 10–16 | **Waves 0–2 merged into one expedited buy** — the five-store manifest is [`BOM.md`](05-PROCESS/BOM.md) §11 (D-202); nothing gates ordering |
| 2A · PMU configuration | 12–20 | **In the car** (D-194) — slots after 6.2, fully written in [`PMU-CONFIG.md`](01-DESIGN/PMU-CONFIG.md) |
| 2B · Firmware | 155–325 | ~100–140 hrs done, ahead of schedule. ICU renders the full 1280×480 panel (F-011) with the BT817 driver written (F-008, timings await `V-084`); DCU logic split out and tested (F-001). All three desktop suites green: 415 + 35 + 33 |
| 3 · Power backbone | 18–28 | Parts are Wave 2a. Winter break |
| 4 · Panel build | 49–74 | Parts ordered (D-202); plate cutting waits on `T-007`, teardown day 1 |
| 5 · Harness legs | 98–162 | Parts ordered with 1.5× wire margin (D-202); cutting waits on `T-008` |
| 6–8 · Install, migrate, shakedown | 118–199 | Summer 2027 |
| 9 · Modules | — | Late 2027 → 2028 |

## 5 · Do next

**Camden — stores first, then the car:**

1. **`T-053` — pay the four loaded carts, then order wire by hand**
   ([`BOM.md`](05-PROCESS/BOM.md) §11, D-202). Loaded and waiting on review:
   DeutschConnector $1,281 · Amazon $1,561 · Waytek $170 · Ballenger $11 =
   **$3,024**. Camden places WireBarn himself from the §11c colour table
   (Cloudflare blocks the agent browser) plus 2 microSD. **No ECUMaster
   line** — the keypad is deleted (D-210). ~$3,570–3,920 all-in
2. **`V-081` ohm check at E-03** — R and RY to case at parked / mid /
   raised (D-199); settles the pop-up drive conductors in five minutes
3. **Teardown day 1** (while parts ship): the full 0B session — dash
   envelope + centre-stack depth (`T-007`/`V-087`), **how deep the cluster
   brow shades** (`V-085` glass call), routes with string (`T-008`), cargo
   bin (`T-024`), sill (`T-028`), battery posts (`T-029`), photos, VIN
4. Freeze the design, print it, date it (0.20–0.22) → **then cut** plate
   and wire — measurements gate cutting, not buying (D-202)

**Agent — queued, nothing blocking** ([`05-PROCESS/FORWARD-WORK.md`](05-PROCESS/FORWARD-WORK.md)):
F-004 tach front end · F-005/F-006 cluster pages + diagnostics screen ·
F-003 sensor conditioning · X-003/X-004/X-006 docs. (F-011 + F-008 landed
2026-08-31 — run `icu_sim/sim.exe` to see the full-width cluster.)

## 6 · Money

[`BOM.md`](05-PROCESS/BOM.md) §1 — the only ledger: bought ~$2,950–3,350 ·
**the expedited Waves 0–2 buy ~$3,570–3,920 across four stores + wire (§11, D-202/D-207)** ·
Wave 3 ~$510–1,170 · Wave 4 conditional. Electrical total ~$6,250–9,450;
Wave 5 (lighting **+ the custom A/C panel**, after shakedown — D-201, D-210)
~$770–1,580 on top. **A/C deletion (D-211) costs $50–120 for refrigerant
recovery and avoids a $470–1,150 recharge or retrofit; it changes no cart** —
F4's fuse position simply becomes the seventh spare on the busbar block.

## 7 · Open items

Everything undecided or unverified is [`05-PROCESS/OPEN.md`](05-PROCESS/OPEN.md)'s — currently:
three dormant questions (Q-014's depth figures, Q-028, Q-001 VIN) and the
working verifies, led by `V-081` (pop-up drive conductors, D-199), `V-084`/`V-085` (display chain), `V-069` (crimper die), `V-065` (PMU
CAN export) and `V-097` (A/C compressor's dedicated belt, D-211). Decisions D-173–D-211 landed 2026-08-30 → 09-01 — the complete
ruling set; [`05-PROCESS/DECISIONS.md`](05-PROCESS/DECISIONS.md) is the only history.
**Four calls are waiting on Camden** in [`01-DESIGN/SWITCHES.md`](01-DESIGN/SWITCHES.md) §7:
the ignition switch, parking-brake sense, the blower speed switch and the
hatch latch.

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

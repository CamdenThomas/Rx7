# CHANGELOG

*Rev 2026-09-01 · owns: one entry per session, newest first — what changed, what was decided, what opened and closed. The `ASSISTANT.md` §7 close step appends here. Individual decisions are `DECISIONS.md`'s; this is the timeline.*

Format: date · mode · one line of scope, then `CHANGED / LOGGED / OPENED /
CLOSED / NEXT` — the same five lines as the session-close diff.

---

## Contents

Newest first: 2026-09-01 A/C deleted · 2026-09-01 verify · 2026-08-31 expedited buy · 2026-08-31
consolidation · 2026-08-31 firmware night · 2026-08-30 audit 4 · 2026-08
audit 3 · ICU firmware · audit 2 · first meter sitting · PMU received ·
audit 1 · rounds one to four.

---

## 2026-09-01 · DECIDE · A/C system deleted; the engine leg carries nothing for it

Camden costed the three A/C paths and killed the system. Also set the rule
that separates L1 from every other leg: hidden interior conductors get run
and capped, the engine bay gets nothing but what the current engine needs.

```
CHANGED   SPEC §3 — K10 and F4 removed, relays 10→9, plate fuses 12→11,
          F15 is now the eleventh position · SCHEMATICS constant-bus tree
          and the "F2/F3/F4 stay live" line · GLOSSARY K/F rows ·
          LOADS §5 clutch row and the sensor-type table · engine.md §A/C
          rewritten as removal + a new "capped spares are not free here"
          paragraph · dash.md deletions table · CAN-MESSAGES 0x300 bytes
          0 and 4 marked RESERVED (frame unchanged) · BOM §5b fuse-block
          note and §10 deletions · CHECKLIST 0.24 and 4.5 · STATUS §1/§2/
          §6/§7 · known-issues K-015 closed by deletion
LOGGED    D-211 — A/C system removed, cooling gone until the swap engine;
          heat, defrost, blower and ventilation untouched. Supersedes
          D-012 and D-099, amends D-067's relay count
OPENED    V-097 (compressor on its own dedicated belt — five-minute look) ·
          T-054 / Checklist 0.24 (strip the system; shop recovers the
          refrigerant first — K-015 says it still holds charge)
CLOSED    K-015 (barely cool) by deletion rather than repair
NEXT      BUILD — nothing here gates T-053 or teardown day 1. No CSV
          changed and no cavity moved, so no gen.py run was needed
```

---

## 2026-09-01 · DECIDE · Keypad deleted; controls fold into the A/C panel

Camden: no ECUMaster button controls at all. Swept the whole tree for what
that touches — including two PMU config expressions that would have failed
at Phase 2A entry.

```
CHANGED   BOM — ECUKB8 out of Wave 2 and §11f, panel added to Wave 5,
          Order 5 is Ballenger-only, totals redone · SWITCHES §3 rewritten
          as the DP-KEY drop · PMU-CONFIG: INTERIOR loses its override
          term, DEFOG loses its trigger · CSVs + gen.py re-run so SPEC and
          PIN-MAP stop saying "keypad" · CONNECTORS, dash, GLOSSARY, LOADS,
          SCHEMATICS, CHECKLIST 1.4/2.18, MIGRATION-LOG, STATUS, T-053
LOGGED    D-210 — no keypad bought; DP-KEY still built and capped (CAN2 +
          switched 12 V + ground, the universal set) so the panel is a
          plug-in; D-031 marked superseded, D-079 amended to four nodes
OPENED    —
CLOSED    —
NEXT      −$369. Four carts $3,024 · wire + microSD by hand · no rear
          defogger until the panel — say so if that needs a stopgap switch
```

---

## 2026-09-01 · DECIDE · Switch schedule — the whole operator interface

Camden: the luxury package is fab and install only, no wiring. Everything
but the column combination switch gets replaced. Wink controls were missing
from the order entirely.

`
CHANGED   NEW 01-DESIGN/SWITCHES.md — every control surface, what stays,
          what is bought, what it feeds · dash.md input table rewritten ·
          SPEC §10 points at it · BOM Order 3 gains the switch block
LOGGED    D-209 — column combo switch stays, horn stays on the wheel ·
          keypad = defog + hatch + fuel door, keys 4–8 RESERVED for
          luxury-package A/C and comfort (no new wiring, DCU already
          reads 0x400) · wink CANNOT be a keypad key (dead asleep, NC
          pole interrupts the opposite coil, NO pole is a wake input) ·
          L3-S3 radar leg NO LONGER a drop candidate — luxury = install
          only means every conductor runs now
OPENED    Four calls in SWITCHES.md §7 — ignition switch, parking-brake
          sense, blower speed switch, hatch latch
CLOSED    —
NEXT      Answer the four §7 calls · Camden reviews and pays · WireBarn
          and microSD by hand
`

---

## 2026-09-01 · DECIDE · Luxury package splits off; carts audited

Camden: digital A/C, LED lighting and heated seats become their own
project. Audited every cart against that line and against the schedule.

`
CHANGED   BOM §3 Wave 0 folded into Order 3 (never bought locally) · new
          §11i draws the luxury-package line · Waytek block rewritten —
          K9 sealed mini + weatherproof connector, micro count 7 → 6,
          4 × 4-pos fuse blocks with 6 spare live-source positions
LOGGED    D-208 — no servos in any cart (never were) · keypad is not A/C
          (4 wires, keys assigned in software) · DP-DCU stays, it is a
          drop not a leg · legs stay full-cavity, D-202 buys one teardown
          · K9 is sealed MINI not micro (corrects D-205e) · D2 14 AWG
          kit gap found and fixed
OPENED    —
CLOSED    — (V-081 now also decides whether L2-P2 collapses)
NEXT      Camden reviews and pays · WireBarn by hand · microSD by hand ·
          two open calls: drop L3-S3 radar leg? trim Deutsch to stamped?
`

---

## 2026-09-01 · BUY · Four carts loaded live in the browser

Same session, second half: the manifest became real carts, store by store.
Nothing purchased — every cart waits on Camden's review and payment.

`
CHANGED   BOM §11 store table now carries live cart subtotals, not
          estimates · new §11h records every substitution with its reason
          and the four trims available on the Deutsch overrun
LOGGED    D-207 carts loaded — Deutsch ,241.36 · Amazon ,488.01 ·
          Waytek .86 · Ballenger .37 + ECUMaster .00 =
          ,270.60, wire still to add
OPENED    —
CLOSED    — (V-093 re-aimed at NOCO BG27; V-096 at the IWISS crimper)
NEXT      Camden reviews five tabs and pays · WireBarn is his to place by
          hand — Cloudflare blocks the agent browser · then T-053 closes
`

---

## 2026-09-01 · VERIFY · Manifest fact-checked, two design corrections

Line-by-line audit of BOM §11 against the design docs, then live checks in
the browser pane. Two catches that would have been order-day surprises.

```
CHANGED   BOM §11 — A7 100 Ω 1 % 1 W pull-up added (kits are ¼ W) · 2 AWG
          40 → 55 ft + lugs ×10 → ×18 (the starter feed was unbought) ·
          explicit 2 A / 7.5 A ATO fuses · ground studs, PMU standoffs,
          pull string, pull-test scale, DT removal tools, optional LiFePO4
          charger · relay line: ISO micro (not mini), K9 added + sealed
          engine-bay socket · §11g savings levers (Camden's call, none
          taken) · totals ~2,550–3,750
LOGGED    D-205 fact-check corrections · D-206 fuse blocks source-grouped —
          V-091 failed live: OptiFuse "BLR-I" = indicating LED, common bus;
          plate carries 1×4-pos + 3×2-pos bussed + 2 inlines (SCHEMATICS §7)
OPENED    —
CLOSED    V-091 → D-206 · ECUKB8 $369 confirmed live at ECUMaster USA
NEXT      Cart co-pilot session — build the five carts in the browser pane
          (WireBarn blocks the pane's Cloudflare check; Camden drives that
          one, or the Crimpzone/CE Auto fallbacks), then T-053
```

---

## 2026-08-31 · DECIDE → GENERATE · Expedited one-teardown buy sourced

Camden's call: order everything now, tear the interior down once, measure
before cutting instead of before buying.

```
CHANGED   BOM §11 order manifest — five consolidated carts (WireBarn wire ·
          DeutschConnector kits · Amazon backbone/tools · Waytek
          distribution · Ballenger terminals + ECUKB8 direct), ~$2,500–3,550
          for Waves 0–2 · §11c per-colour wire table computed from
          connectors.csv (2,525 ft ordered at 1.5× margin, 25 ft floors) ·
          PANEL-LAYOUT gains the dash-space estimate (PMU fits the freed
          centre stack on face area; depth is V-087; diagram.pdf identified
          as factory sheet F, no dimensions in the repo's manuals) ·
          BATTERY-INSTALL part numbers corrected (Class-T 5007100 + 5114;
          HM318BKS) · STATUS/CHECKLIST/TASKS re-gated: T-007/T-008 gate
          cutting, not ordering
LOGGED    D-202 one-teardown expedite + wire margins · D-203 sourcing calls
          (independent-feed ATC blocks ×3 — a bussed 12-way can't serve six
          sources; PT-E300 + HSe shrink labels; iCrimp pair gated on pull
          tests; welding-cable 2 AWG; ECUKB8 $369 direct)
OPENED    T-053 place the orders · V-087 centre-stack depth · V-088 amp/bin
          space · V-089–V-096 sourcing verifies (every price a placeholder
          until carted)
CLOSED    nothing — V-069 deliberately stays open (die check before the FCI
          crimper ships)
NEXT      Camden: T-053, V-081, then teardown day 1 (full 0B + freeze).
          Agent: F-004/F-005/F-006 while parts ship
```

---

## 2026-08-31 · AUDIT → BUILD · Consolidation — five folders, lighting folded in

Camden's reorganisation (04-SUBSYSTEMS and 06-PROCUREMENT emptied, lighting-body
dragged under 07-PROCESS, BUY-LIST and METER-SESSION deleted) completed and made
consistent across the whole tree.

```
CHANGED   Folders renumbered 05-BUILD → 04-BUILD, 07-PROCESS → 05-PROCESS
          (D-200); every link, tool path and doc updated (37 files bulk +
          ~30 hand edits) · lighting-body dissolved (D-201): TAIL-LIGHTS →
          01-DESIGN (now owns the full deferred lighting & body scope),
          L-decisions into DECISIONS, open items → OPEN §8, tasks →
          TASKS-CAMDEN §6, money → BOM Wave 5; originals archived
          99-ARCHIVE/2026-08-31_lighting-body/ · BOM rebuilt: lost Wave 1 /
          Wave 4 / deletions sections restored from git, §9 re-order
          reference absorbs BUY-LIST, malformed rows fixed · project README,
          root README, ASSISTANT, STATUS updated to the five-folder map ·
          stale K1–K4/five-relay/13-fuse/800×480 references corrected to
          D-186/D-198/D-193 across PANEL-LAYOUT, SCHEMATICS, GLOSSARY,
          CHECKLIST, MIGRATION-LOG, dash/engine/front-chassis, DCU-CLUSTER,
          CLUSTER-DESIGN, PMU-CONFIG §7 (bench → in-car per D-194) ·
          connectors.csv: the five stale OPEN cavities re-statused per
          D-180/D-182/D-191 (L2-M 4 LIVE · L2-S 3 DEFERRED · L4-M 3/4
          PROVISIONED · DP-DCU 2 SPARE), everything regenerated ·
          registry.py reads the merged locations
LOGGED    D-200 consolidation + renumber · D-201 lighting fold-in (amends
          D-123); L-001…L-004 merged into the main log
CLOSED    T-050 (superseded by D-198) · the last OPEN cavity statuses
NEXT      Camden: T-052 (V-081 ohm check), Wave 0/1 buys, the 0B tape
          session, git commit · Agent: F-004, F-005/F-006, F-003, X-003/4/6
```

---

## 2026-08-31 · BUILD · Firmware night — both Teensys code-complete on the desktop

The all-nighter push: exciter fixed to factory spec, pop-up verify sharpened,
then the whole firmware queue.

```
CHANGED   cluster_core.h + stats.h resized 800×480 → 1280×480 (F-011), suite
          415/415 green first run · NEW firmware/icu/bt817.h — full BT817
          driver: init, static display list, dirty-run merge into RAM_G
          (F-008; every timing constant flagged V-084) · NEW
          tests/test_bt817.cpp (35 asserts, mocked SPI, hand-computed DL
          words) · NEW tests/test_dcu.cpp (33 asserts) · climate.h gains
          mem_crc/mem_defaults (moved from dcu.ino, now testable) and a
          hardened mode cycle · icu.ino 0.4.0-dev: EXTMEM framebuffer,
          PSRAM boot check, headless fallback · tests/run.bat runs all
          three suites · sim.exe rebuilt full-width · connectors.csv, SPEC,
          SCHEMATICS, reference pages, BOM (D-198 propagation) · STATUS,
          FORWARD-WORK, LOGS
LOGGED    D-198 factory-spec exciter O12 → F15 → BW (V-086 skipped, wire it
          right and replace only if it still refuses) · D-199 V-081 becomes
          a five-minute ohm check at E-03 (R / RY to case, three positions)
CLOSED    V-086 → D-198 · F-011 · F-008 (code side; first light waits on
          V-084 + T-051)
NEXT      Camden: V-081, Wave 0/1 buys, the 0B tape session · Agent: F-004,
          F-005/F-006, F-003, docs X-003/X-004/X-006
```

---

## 2026-08-30 · AUDIT → BUILD · Audit 4 implemented, whole tree

Every one of the 95 Audit 4 findings addressed in one pass (`AUDITS.md` §4);
85 closed, 2 are Camden's, 3 partial, 4 ruled no-change.

```
CHANGED   Every file in electrical-pmu/ except OEM-RECORD.md; root ASSISTANT.md,
          README.md; 00-CAR, 01-REFERENCE, lighting-body, 99-ARCHIVE READMEs.
          NEW: 02-HARNESS/data/{pmu_pins,connectors,housings}.csv ·
          05-PROCESS/tools/{gen,registry,check}.py · CAVITY-STATE.md ·
          ID-REGISTRY.md · AUDITS.md · FORWARD-WORK.md · CHANGELOG.md ·
          02-HARNESS/diagrams/*.svg (6 legs + architecture) · firmware/tests/run.bat ·
          00-CAR/README.md · 01-REFERENCE/photos/README.md · lighting-body/{OPEN,TASKS,BOM}.md ·
          root CLAUDE.md, .gitignore · 99-ARCHIVE/2026-08-30_audit-4-findings.md
          GENERATED: PIN-MAP.md, CAVITY-STATE.md, channels.h, and the marker blocks in
          SPEC/CHANNEL-SCHEDULE/CUT-LIST/CONNECTORS — from the CSVs, never by hand
LOGGED    D-168 SPI dirty-rectangle display (supersedes D-150 in part) · D-169 page
          button (Q-058) · D-170 PSRAM (Q-059) · D-171 L1-S as generated · D-172 L3-S
          as generated · 19 SUPERSEDED / AMENDED marks under old entries · R7, R8
OPENED    Q-061 F13 + solenoid outputs · Q-062 dash→sill conductors · Q-063 four
          signals with no PMU pin · Q-064 rpm logic before the ICU · Q-065 dimmer/pass
          on A15 · V-074 O8 braking needs park? · V-075 native shutdown delay ·
          A-010…A-013 · T-049 record the VIN · Checklist 0.23, 1.15
CLOSED    Q-058, Q-059 (→ D-169/170) · V-041 (→ D-083) · I-71…I-165 bar I-72, I-153
          (Camden), I-156 (half) · T-046, T-047 (Stages 4–5) · X-001, X-005, F-002
NEXT      Camden: rule on Q-061…Q-065 (0.23) · T-014 finish the meter session ·
          T-007/T-008 tape measure · git commit · project instructions (I-72).
          Agent: F-001 DCU skeleton, or H-001 ICU carrier schematic — either runs
          without the car.
```

## 2026-08 · AUDIT · Audit 3 closeout, after the ICU firmware

I-52 … I-70. D-151 … D-163 recorded the cluster decisions that lived only in
`cluster_core.h`; `firmware/README.md` created; `CLUSTER-DESIGN.md` retitled
forward scope; R6 added. Details in `AUDITS.md` §3.

## 2026-08 · BUILD · ICU firmware Stages 1–5, `cluster_core.h`, simulator, test suite

`can_map_test`, `can_loopback_test`, `ladder_decode_test`, `tach_simulator`
all passed and were absorbed into `icu/icu.ino`. Desktop simulator
(`icu_sim/`) runs the real renderer. 415-assertion regression suite found
four real bugs. `pmu_sim/` written for the third Teensy.

## 2026-08 · AUDIT · Audit 2 closeout — accretion and scope

I-32 … I-51. `PARTS-CHANGES.md` and `INFOTAINMENT.md` rewritten;
`HEAD-UNIT.md` and `DEFERRED-FEATURES.md` created; lighting split into
`lighting-body/` (D-123); R1–R5 recorded. Details in `AUDITS.md` §2.

## 2026-08 · BUILD · First meter sitting

Brake 7.0 A steady / 9.5 A warm-up; turn 3.4 A per side. Tail read on the
wrong wire (`R`, should be `RG`); hazard read one side only. Procedure
corrected in `METER-SESSION.md`. K-008 observed live.

## 2026-08 · DECIDE · PMU received; bench mule cut down

D-134 … D-148: cavity layout confirmed in the hand, terminal stock counted
(zero small spares), pin 1 confirmed, bench mule reduced to the PMU on a desk
with a 5 A fuse, powered panel verification moved to the car, K9 to the inner
fender.

## 2026-08 · AUDIT · Audit 1 closeout — the first tree read

I-01 … I-31. Numbered folders; STATUS, GLOSSARY, SAFETY, CAN-MESSAGES,
MIGRATION-LOG, CUT-LIST, LOGS created; owners assigned. Details in
`AUDITS.md` §1.

## 2026-08 · DECIDE · Rounds one to four

D-001 … D-133 over four decision rounds: the PMU and the Ionic (D-001/002),
four legs (D-029), Deutsch throughout (D-052/070), the sill node (D-065–069),
the two CAN modules (D-075–094), 2 AWG feed (D-091), lighting split (D-123),
manual windows (D-131). Purchases: PMU, Ionic, meter, three Teensys.

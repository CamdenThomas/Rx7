# CHANGELOG

*Rev 2026-08-31 · owns: one entry per session, newest first — what changed, what was decided, what opened and closed. The `ASSISTANT.md` §7 close step appends here. Individual decisions are `DECISIONS.md`'s; this is the timeline.*

Format: date · mode · one line of scope, then `CHANGED / LOGGED / OPENED /
CLOSED / NEXT` — the same five lines as the session-close diff.

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

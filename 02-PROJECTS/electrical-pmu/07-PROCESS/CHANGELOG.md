# CHANGELOG

*Rev 2026-08-30 · owns: one entry per session, newest first — what changed, what was decided, what opened and closed. The `ASSISTANT.md` §7 close step appends here. Individual decisions are `DECISIONS.md`'s; this is the timeline.*

Format: date · mode · one line of scope, then `CHANGED / LOGGED / OPENED /
CLOSED / NEXT` — the same five lines as the session-close diff.

---

## 2026-08-30 · AUDIT → BUILD · Audit 4 implemented, whole tree

Every one of the 95 Audit 4 findings addressed in one pass (`AUDITS.md` §4);
85 closed, 2 are Camden's, 3 partial, 4 ruled no-change.

```
CHANGED   Every file in electrical-pmu/ except OEM-RECORD.md; root ASSISTANT.md,
          README.md; 00-CAR, 01-REFERENCE, lighting-body, 99-ARCHIVE READMEs.
          NEW: 02-HARNESS/data/{pmu_pins,connectors,housings}.csv ·
          07-PROCESS/tools/{gen,registry,check}.py · CAVITY-STATE.md ·
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

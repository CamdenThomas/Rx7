# ID REGISTRY — every permanent ID and its status

*Rev 2026-08-30 · owns: nothing — a generated view. Run `tools/registry.py` after editing DECISIONS, OPEN, TASKS, known-issues, modifications or AUDITS.*

IDs are permanent and never reused (D-043); a gap means something closed. **Cite a closed ID with its closer** — `Q-038 → D-095`, never bare `Q-038` — and `check.py` will stay quiet.

| Prefix | Total | Open / active |
|---|---|---|
| A — Assumptions | 11 | 4 |
| D — Decisions | 175 | 162 |
| I — Improvement items (audits) | 95 | 10 |
| K — Known issues | 23 | 0 |
| L — Lighting-body decisions | 4 | 4 |
| M — Modifications | 11 | 0 |
| P — Planned modifications | 6 | 6 |
| Q — Questions | 56 | 10 |
| R — Standing rules | 8 | 8 |
| T — Camden's tasks | 45 | 31 |
| V — Verify items | 65 | 36 |

## A — Assumptions

| ID | Status | What | Lives in |
|---|---|---|---|
| A-001 | closed (no decision cites it) |  | — |
| A-002 | closed (no decision cites it) |  | — |
| A-003 | closed (no decision cites it) |  | — |
| A-004 | closed (no decision cites it) |  | — |
| A-005 | closed by D-148 | `[A-005]` **Start relay K9 mounts high on the inner fender or | 07-PROCESS/DECISIONS.md |
| A-007 | closed by D-112 | `[A-007]` **Converted from an assumption to a task.** The pop-up | 07-PROCESS/DECISIONS.md |
| A-009 | closed by D-091 | `[A-009]` **Main feed upgraded to 2 AWG.** Sized for the LS, not the | 07-PROCESS/DECISIONS.md |
| A-010 | open | Brake fluid level goes to the ICU on DP-ICU 12 via L1-S2 1. Coolant and oil level are optional, have no ICU ca… | 07-PROCESS/OPEN.md |
| A-011 | open | The wideband O2 signal (K-001) is carried to the dash on L1-S1 12 and capped. It is not an ICU input and has n… | 07-PROCESS/OPEN.md |
| A-012 | open | The luggage compartment switch joins the A6 door-pin ladder as a fourth state — re-run the ladder maths before… | 07-PROCESS/OPEN.md |
| A-013 | open | The CAN keypad is powered from the accessory bus O10 (DP-KEY 3), so it is dead when the car sleeps and cannot … | 07-PROCESS/OPEN.md |

## D — Decisions

| ID | Status | What | Lives in |
|---|---|---|---|
| D-001 | active | ECUMaster PMU-24 DL over a conventional relay/fuse box. | 07-PROCESS/DECISIONS.md |
| D-002 | active | Ionic S9 heated lithium battery, rear-mounted. Sold as "Ionic Lithium | 07-PROCESS/DECISIONS.md |
| D-003 | active | Two-tier connector architecture. The 39-pin Sicma is a *device | 07-PROCESS/DECISIONS.md |
| D-004 | active | All 39 cavities terminated at build time. Reserved channels get real | 07-PROCESS/DECISIONS.md |
| D-005 | active | Panel is a single removable aluminum backer plate in the dash, | 07-PROCESS/DECISIONS.md |
| D-006 | superseded by D-075 | DCU/MCU, digital gauge cluster, and electronic A/C controls are | 07-PROCESS/DECISIONS.md |
| D-007 | active | Baseline pinned for the current 12A / Weber configuration. Two 25 A | 07-PROCESS/DECISIONS.md |
| D-008 | superseded by D-030 | Relay bank uses 16 sockets, 10 populated. Six empty sockets are | 07-PROCESS/DECISIONS.md |
| D-009 | active | O1 (motor bus) and O16 (blower) carry the worst inductive loads, | 07-PROCESS/DECISIONS.md |
| D-010 | active | Wipers live on O8 and nothing else does. O8 is the only channel with | 07-PROCESS/DECISIONS.md |
| D-011 | active | O15 assigned as a 25 A comfort bus (heated/cooled seats, heated | 07-PROCESS/DECISIONS.md |
| D-012 | active | A/C compressor clutch stays on the factory switch, off the PMU. | 07-PROCESS/DECISIONS.md |
| D-013 | active | Turn signals flashed natively by the PMU. No flasher unit anywhere | 07-PROCESS/DECISIONS.md |
| D-014 | active | Interval wiper control unit deleted. Intermittent is a software | 07-PROCESS/DECISIONS.md |
| D-015 | active | Tail / park / side marker / plate is one circuit on O6, covering both | 07-PROCESS/DECISIONS.md |
| D-016 | active | Wire base color encodes channel class: RED = 25 A, ORN = 15 A, | 07-PROCESS/DECISIONS.md |
| D-017 | active | Grounds never cross a bulkhead connector. Local star node per zone. | 07-PROCESS/DECISIONS.md |
| D-018 | active | All switch inputs on A1–A8 wired to ground with the internal 10 kΩ | 07-PROCESS/DECISIONS.md |
| D-019 | active | Every multi-position switch gets a resistor ladder from day one | 07-PROCESS/DECISIONS.md |
| D-020 | active | A true-constant bus lives off the PMU entirely, fed from the busbar | 07-PROCESS/DECISIONS.md |
| D-021 | superseded by D-065 | Wink switches and window switches are hardwired to the relay bank, | 07-PROCESS/DECISIONS.md |
| D-022 | active | Housings bought at full cavity count; unused positions filled with a | 07-PROCESS/DECISIONS.md |
| D-023 | active | Parallel-system migration. Factory harness stays intact and powered | 07-PROCESS/DECISIONS.md |
| D-024 | active | Migration order runs least to most consequential, ending with | 07-PROCESS/DECISIONS.md |
| D-025 | active | Soft fuses are set from current measured live in the client during | 07-PROCESS/DECISIONS.md |
| D-026 | active | Working files are Markdown. HTML is generated on demand as a | 07-PROCESS/DECISIONS.md |
| D-027 | active | Signal wire changes from 18 AWG to **16 AWG** throughout. The PMU's | 07-PROCESS/DECISIONS.md |
| D-028 | active | Precision analog signals prefer the **A9–A16** bank over A1–A8. | 07-PROCESS/DECISIONS.md |
| D-029 | active | Four leg connectors replace the seven regional connectors. Legs are | 07-PROCESS/DECISIONS.md |
| D-030 | active | Relay bank defined at 11: eight H-bridge halves (two pop-ups, two | 07-PROCESS/DECISIONS.md |
| D-031 | active | Five dash buttons move to the CAN keypad — horn, parking brake sense, | 07-PROCESS/DECISIONS.md |
| D-032 | active | Power and signal get **separate housings** on every leg. Three | 07-PROCESS/DECISIONS.md |
| D-033 | active | Connector code scheme: `L<leg><class><index>` leg-side, | 07-PROCESS/DECISIONS.md |
| D-034 | superseded by D-052 | Series selection: **Deutsch DTP** (size 12) for all P, **Deutsch DT | 07-PROCESS/DECISIONS.md |
| D-035 | superseded by D-066 | 13 leg connectors total: L1 ×2, L2 ×4, L3 ×3, L4 ×4. L2 and L4 need | 07-PROCESS/DECISIONS.md |
| D-036 | superseded by D-070 | The dash post carries 2 lugs (DP-BAT, DP-GND), the sealed PMU device | 07-PROCESS/DECISIONS.md |
| D-037 | active | The diagnostic port and keypad grounds are the **only** grounds | 07-PROCESS/DECISIONS.md |
| D-038 | active | Retractable headlight switch (E-02) deleted.** Pop-ups raise | 07-PROCESS/DECISIONS.md |
| D-039 | active | Radar detector added.** Control module and minimalist LED display in | 07-PROCESS/DECISIONS.md |
| D-040 | active | No software gesture needed to park the lamps up.** Each retractor | 07-PROCESS/DECISIONS.md |
| D-041 | active | SPEC bumped to **Rev B**. Rev A's connector section, gauges, relay | 07-PROCESS/DECISIONS.md |
| D-042 | active | C1–C7 moved to `99-ARCHIVE/2026-08_superseded-C1-C7-connector-scheme.md` | 07-PROCESS/DECISIONS.md |
| D-043 | active | Task IDs in `TASKS-CAMDEN.md` renumbered T-001…T-019 and reordered | 07-PROCESS/DECISIONS.md |
| D-044 | active | Bulb-out detection confirmed viable on 7 A and 15 A channels | 07-PROCESS/DECISIONS.md |
| D-045 | active | `[V-010 RESOLVED]` Connector geometry confirmed from the CAD and the | 07-PROCESS/DECISIONS.md |
| D-046 | active | Consequence of D-045: every 15 A and 7 A output sits in a 1.5 mm | 07-PROCESS/DECISIONS.md |
| D-047 | active | `[Q-029]` **Bulb-out detection dropped entirely.** Manual check is | 07-PROCESS/DECISIONS.md |
| D-048 | active | `[Q-013]` **Cooled seats are in scope.** Adds fans and ducting to the | 07-PROCESS/DECISIONS.md |
| D-049 | active | `[Q-022]` **Remote mirror motors kept, plus heated mirrors.** This | 07-PROCESS/DECISIONS.md |
| D-050 | active | `[Q-021]` Seat belt warning and key reminder chime **dropped**. | 07-PROCESS/DECISIONS.md |
| D-051 | active | `[Q-011]` Head unit is **double-DIN**. `[Q-016]` washer pump is | 07-PROCESS/DECISIONS.md |
| D-052 | active | `[Q-027]` L3-S becomes **Deutsch DT-12s instead of AMPSEAL 35 | 07-PROCESS/DECISIONS.md |
| D-053 | active | Ladder design principle: **no valid switch position uses a dead | 07-PROCESS/DECISIONS.md |
| D-054 | active | Resistors mount **at the switch**, not at the PMU. One return wire | 07-PROCESS/DECISIONS.md |
| D-055 | active | The A16 key ladder is **not** a single-source ladder. ACC stays live | 07-PROCESS/DECISIONS.md |
| D-056 | active | Wake network uses **1N5819 Schottky** diodes, not 1N4007. The lower | 07-PROCESS/DECISIONS.md |
| D-057 | active | H-bridge relay pairs idle with **both motor legs grounded**, so a | 07-PROCESS/DECISIONS.md |
| D-058 | active | `[Q-032 provisional]` O15 comfort bus worst case is 17–26 A with | 07-PROCESS/DECISIONS.md |
| D-059 | active | PMU shipped **with the mating connector kit and the USB-to-CAN | 07-PROCESS/DECISIONS.md |
| D-060 | active | Battery is a **Group 25 case, ~9.1 × 6.9 × 8.9 in, 14.6 lb, SAE | 07-PROCESS/DECISIONS.md |
| D-061 | active | Starter feed and PMU feed are separate runs from the battery**, | 07-PROCESS/DECISIONS.md |
| D-062 | active | Main protection is **Class-T, not ANL or MIDI**. LiFePO4 delivers | 07-PROCESS/DECISIONS.md |
| D-063 | active | Battery mounts on a **backing plate**, not through sheet metal alone. | 07-PROCESS/DECISIONS.md |
| D-064 | active | A **pull string goes into the tunnel alongside the 4 AWG main feed | 07-PROCESS/DECISIONS.md |
| D-065 | active | `[Q-025]` **Window H-bridge relays K5–K8 move to the sill.** Dry, | 07-PROCESS/DECISIONS.md |
| D-066 | active | Cascade of D-065: **L4-P2 is deleted entirely.** The four 12 AWG | 07-PROCESS/DECISIONS.md |
| D-067 | active | Cascade of D-065: **the in-box relay count drops from 11 to 5. | 07-PROCESS/DECISIONS.md |
| D-068 | active | `[Q-031]` **The doors get their own connector pair at the sill. | 07-PROCESS/DECISIONS.md |
| D-069 | active | `[Q-024]` **Pop-up relays stay in the box.** Confirmed no. The nose | 07-PROCESS/DECISIONS.md |
| D-070 | active | `[Q-030]` L3-S is **2 × DT06-12S + 1 × DT06-8S** — 32 cavities, | 07-PROCESS/DECISIONS.md |
| D-071 | active | `[Q-019]` **Inhibitor switch laddered onto one input** on the L1-S | 07-PROCESS/DECISIONS.md |
| D-072 | active | `[Q-026]` **Horn gets a dedicated wake diode to pin 7.** Sixth input | 07-PROCESS/DECISIONS.md |
| D-073 | active | `[Q-032]` **Comfort bus management defers to the DCU/MCU**, alongside | 07-PROCESS/DECISIONS.md |
| D-074 | active | `[Q-012]` Seat products stay as **estimates** — 2 × 4 A heat elements, | 07-PROCESS/DECISIONS.md |
| D-075 | active | D-006 is SUPERSEDED.** The DCU and digital gauge cluster are in | 07-PROCESS/DECISIONS.md |
| D-076 | superseded by D-083 | The PMU has no spare analog inputs.** All 16 are allocated. Water | 07-PROCESS/DECISIONS.md |
| D-077 | superseded by D-083 | Two nodes, not one: DCU and ICU.** The DCU owns climate, comfort | 07-PROCESS/DECISIONS.md |
| D-078 | active | Single source of truth per signal.** If the PMU measures it, the ICU | 07-PROCESS/DECISIONS.md |
| D-079 | active | CAN2 becomes a **five-node bus**: PMU, keypad, DCU, ICU, future LS | 07-PROCESS/DECISIONS.md |
| D-080 | superseded by D-083 | Two new dash-post connectors: **DP-DCU** (DT06-12S, 11 used) and | 07-PROCESS/DECISIONS.md |
| D-081 | active | The sequencing rule.** The car drives fully on the PMU with dumb | 07-PROCESS/DECISIONS.md |
| D-082 | active | Tach signal gets **opto-isolation or a comparator** at the DCU. Coil | 07-PROCESS/DECISIONS.md |
| D-083 | active | CORRECTS D-076 and D-077.** Sensor acquisition moves from the DCU | 07-PROCESS/DECISIONS.md |
| D-084 | active | Teensy 4.1 for both DCU and ICU.** Same board in both boxes: one | 07-PROCESS/DECISIONS.md |
| D-085 | active | CAN transceivers are **TI TCAN1042 / TCAN1051**, automotive | 07-PROCESS/DECISIONS.md |
| D-086 | active | Vehicle bus is **500 kbps, CAN 2.0B, 11-bit IDs**. The PMU is CAN 2.0 | 07-PROCESS/DECISIONS.md |
| D-087 | active | A second twisted pair runs between DCU and ICU, capped at both | 07-PROCESS/DECISIONS.md |
| D-088 | active | Load-dump TVS on both module supplies is mandatory**, not optional. | 07-PROCESS/DECISIONS.md |
| D-089 | active | Buy **three** Teensy 4.1, not two. A dead module mid-debug otherwise | 07-PROCESS/DECISIONS.md |
| D-090 | active | `[Q-043]` **No hardwired oil pressure lamp.** Oil pressure is shown | 07-PROCESS/DECISIONS.md |
| D-091 | active | `[A-009]` **Main feed upgraded to 2 AWG.** Sized for the LS, not the | 07-PROCESS/DECISIONS.md |
| D-092 | active | `[Q-033]` **Door connectors are a single DT06-08S per door.** Window | 07-PROCESS/DECISIONS.md |
| D-093 | active | `[Q-034]` **Mirrors: option B, independent wiring per side.** The | 07-PROCESS/DECISIONS.md |
| D-094 | active | `[Q-035]` Two MCUs, DCU and ICU separate. `[Q-036]` CAN2 at | 07-PROCESS/DECISIONS.md |
| D-095 | active | `[Q-038]` **Cigarette lighter deleted.** Frees 8–10 A on O10 and | 07-PROCESS/DECISIONS.md |
| D-096 | active | `[V-048]` **Radar is a custom subsystem, not a commercial unit. | 07-PROCESS/DECISIONS.md |
| D-097 | active | Confirmed **gone and not returning**, removed from all specs and | 07-PROCESS/DECISIONS.md |
| D-098 | active | `[V-034]` **The fuel-door solenoid never existed** — it is a new | 07-PROCESS/DECISIONS.md |
| D-099 | active | `[V-032]` A/C is **barely cool, probably low on charge.** Not an | 07-PROCESS/DECISIONS.md |
| D-100 | active | `[V-013]` Deutsch DTP size-12 confirmed adequate for the 25 A legs. | 07-PROCESS/DECISIONS.md |
| D-101 | superseded by D-140 | Bench kit **purchased**: UT210E clamp meter, 3 × Teensy 4.1 with | 07-PROCESS/DECISIONS.md |
| D-102 | active | Three Sicma housings on hand**, each with a full pin set: one from | 07-PROCESS/DECISIONS.md |
| D-103 | superseded by D-135 | Spare terminals deliberately not ordered** pending T-025. Counting | 07-PROCESS/DECISIONS.md |
| D-104 | superseded by D-105 | Housekeeping: **T-016 (diagnose K-008) had been dropped** from the | 07-PROCESS/DECISIONS.md |
| D-105 | active | `[K-008 / T-016]` **The blinker fault is not being fixed.** T-016 is | 07-PROCESS/DECISIONS.md |
| D-106 | active | `[Q-041 closed on the design side]` **CAN byte layouts finalised. | 07-PROCESS/DECISIONS.md |
| D-107 | active | Custom tail lights.** Thin LED strip per side, stock aperture and | 07-PROCESS/DECISIONS.md |
| D-108 | active | Project reorganised into numbered folders: `01-DESIGN` `02-HARNESS` | 07-PROCESS/DECISIONS.md |
| D-109 | active | `[Q-042]` **IMU fitted to the ICU carrier board.** ~$5 and a few | 07-PROCESS/DECISIONS.md |
| D-110 | active | `[Q-044]` **Pop-ups stay.** Not deleted. K1–K4, the four heavy | 07-PROCESS/DECISIONS.md |
| D-111 | active | `[Q-046]` **Tail light driver PCB per housing.** Takes tail, brake, | 07-PROCESS/DECISIONS.md |
| D-112 | active | `[A-007]` **Converted from an assumption to a task.** The pop-up | 07-PROCESS/DECISIONS.md |
| D-113 | active | `[Q-045]` **Rear disc conversion is still planned.** The July 2026 | 07-PROCESS/DECISIONS.md |
| D-114 | active | `[V-062 closed]` The reference PDF is the **TE Connectivity | 07-PROCESS/DECISIONS.md |
| D-115 | active | `[V-044 CONFIRMED]` **DTP is manufactured in 2-way and 4-way only. | 07-PROCESS/DECISIONS.md |
| D-116 | active | Wire sealing ranges confirmed from the catalogue: | 07-PROCESS/DECISIONS.md |
| D-117 | active | `C015` reduced-diameter seal modification exists** for wire with | 07-PROCESS/DECISIONS.md |
| D-118 | active | BOM gap found: secondary wedgelocks are sold separately** and are | 07-PROCESS/DECISIONS.md |
| D-119 | active | The car migrates and drives on stock incandescent bulbs.** Nothing | 07-PROCESS/DECISIONS.md |
| D-120 | active | Inrush tolerance must be configured on every lamp channel** before | 07-PROCESS/DECISIONS.md |
| D-121 | active | The stock dual-filament rear bulb is exactly what the two-channel | 07-PROCESS/DECISIONS.md |
| D-122 | active | Soft fuses must be re-set after any bulb change.** Values set | 07-PROCESS/DECISIONS.md |
| D-123 | active | Lighting split into its own project.** `02-PROJECTS/lighting-body/`. | 07-PROCESS/DECISIONS.md |
| D-124 | active | The electrical project's lighting baseline is stock incandescent. | 07-PROCESS/DECISIONS.md |
| D-125 | active | Four more faults found 2026-08: **defrost switch broken (K-020), | 07-PROCESS/DECISIONS.md |
| D-126 | active | O16 blower sizing comes from the replacement part's spec sheet, not | 07-PROCESS/DECISIONS.md |
| D-127 | active | The pop-up measurement and the limit-switch continuity test are one | 07-PROCESS/DECISIONS.md |
| D-128 | active | `[Q-053]` **Path 1: a CarPlay head unit.** The Pi minimap is not | 07-PROCESS/DECISIONS.md |
| D-129 | active | Audio is the head unit's job.** The hidden Bluetooth A2DP module | 07-PROCESS/DECISIONS.md |
| D-130 | active | The ICU keeps gauges only.** No map, no turn-by-turn strip, no BLE | 07-PROCESS/DECISIONS.md |
| D-131 | active | The windows are MANUAL.** This car has no power window motors, | 07-PROCESS/DECISIONS.md |
| D-132 | active | The sill node shrinks but stays.** Even with no window motors it | 07-PROCESS/DECISIONS.md |
| D-133 | active | O1 motor bus is pop-ups only for now.** Worst case drops from | 07-PROCESS/DECISIONS.md |
| D-134 | active | PMU-24 DL received. Connector cavity layout CONFIRMED in the hand. | 07-PROCESS/DECISIONS.md |
| D-135 | active | Terminal stock counted** `[T-025 closed]`. | 07-PROCESS/DECISIONS.md |
| D-136 | active | Physical orientation reference recorded.** With the PMU sitting | 07-PROCESS/DECISIONS.md |
| D-137 | active | Spare housings ordered from ECUmaster are expected to carry the same | 07-PROCESS/DECISIONS.md |
| D-138 | superseded by D-139 | `[V-068 provisionally answered]` **Pin 1 is top-left**, in the top | 07-PROCESS/DECISIONS.md |
| D-139 | active | `[V-068 CLOSED]` **Connector orientation confirmed** by visual | 07-PROCESS/DECISIONS.md |
| D-140 | active | Inventory correction.** These were previously recorded as purchased | 07-PROCESS/DECISIONS.md |
| D-141 | active | The full plywood bench mule is dropped.** Reduced to a | 07-PROCESS/DECISIONS.md |
| D-142 | active | Ladder ADC verification moves from bench to car**, during Phase 6, | 07-PROCESS/DECISIONS.md |
| D-143 | active | One bench item is non-negotiable: deliberately short an output and | 07-PROCESS/DECISIONS.md |
| D-144 | active | No bench power supply. Supersedes D-143. | 07-PROCESS/DECISIONS.md |
| D-145 | active | The $2 replacement: a 5 A fuse in the main feed for first | 07-PROCESS/DECISIONS.md |
| D-146 | active | Checklist 4.21–4.23 powered panel verification is dropped. | 07-PROCESS/DECISIONS.md |
| D-147 | active | Bench kit final: **~$110–165.** No PSU, no plywood, no pigtail, no | 07-PROCESS/DECISIONS.md |
| D-148 | active | `[A-005]` **Start relay K9 mounts high on the inner fender or | 07-PROCESS/DECISIONS.md |
| D-149 | active | `[Q-055]` **Head unit selection criteria set: | 07-PROCESS/DECISIONS.md |
| D-150 | active | `[Q-037]` **Cluster is ONE WIDE DISPLAY.** Not two round TFTs. | 07-PROCESS/DECISIONS.md |
| D-151 | active | Emerald `#009155` is the single lit colour.** RGB332 `0x11`. | 07-PROCESS/DECISIONS.md |
| D-152 | active | Imperial at the display layer only.** `VehicleState` stores metric | 07-PROCESS/DECISIONS.md |
| D-153 | active | A missing sensor must never render as a real zero. | 07-PROCESS/DECISIONS.md |
| D-154 | active | Bar segments are contiguous, gap 0.** Segment widths grew to hold | 07-PROCESS/DECISIONS.md |
| D-155 | active | Symbols, not words, for the gauge column.** Thermometer, oil can, | 07-PROCESS/DECISIONS.md |
| D-156 | active | Four named axes in the gauge column**, everything derives from | 07-PROCESS/DECISIONS.md |
| D-157 | active | The left column is THREE items, not four.** The G value is the | 07-PROCESS/DECISIONS.md |
| D-158 | active | Digit fields centre by repositioning slots.** `setCentre()` counts | 07-PROCESS/DECISIONS.md |
| D-159 | active | `[I-64]` **The display does NOT cross the harness.** It connects | 07-PROCESS/DECISIONS.md |
| D-160 | active | `[I-65]` **`stats.h` thresholds recorded and flagged. | 07-PROCESS/DECISIONS.md |
| D-161 | active | `[I-68]` **IMU specified.** MPU-6050 or ICM-20948 class, I²C, on the | 07-PROCESS/DECISIONS.md |
| D-162 | active | `[I-66]` **`stats.h` is volatile-only for now.** The `life[]` | 07-PROCESS/DECISIONS.md |
| D-163 | active | `[I-67]` **`stats.h` owns the automated figures; `LOGS.md` owns the | 07-PROCESS/DECISIONS.md |
| D-164 | active | The channel schedule is the measured-to-configured pipeline. | 07-PROCESS/DECISIONS.md |
| D-165 | active | An output with no measured figure stays disabled.** A guessed limit | 07-PROCESS/DECISIONS.md |
| D-166 | active | The entire PMU logic is enterable without any amp figures. | 07-PROCESS/DECISIONS.md |
| D-167 | active | A 100 kΩ bias resistor from +5 V on A15 and A16.** These are the | 07-PROCESS/DECISIONS.md |
| D-168 | active | `[I-117]` **The cluster display is driven over SPI with | 07-PROCESS/DECISIONS.md |
| D-169 | active | `[Q-058]` **Cluster pages cycle from a small dedicated momentary | 07-PROCESS/DECISIONS.md |
| D-170 | active | `[Q-059]` **Fit 8 MB PSRAM to the Teensy 4.1 pads before the ICU | 07-PROCESS/DECISIONS.md |
| D-171 | active | L1-S is two DT06-12S housings, L1-S1 and L1-S2, allocated as | 07-PROCESS/DECISIONS.md |
| D-172 | active | L3-S is allocated as generated: L3-S1 (ladders and switch | 07-PROCESS/DECISIONS.md |
| D-173 | active | Fuel pump soft fuse 4.0 A: measured steady 2.38 A × 1.5, | 07-PROCESS/DECISIONS.md |
| D-174 | active | `[Q-066]` **Suspect and unmeasured LIVE channels get INTERIM soft | 07-PROCESS/DECISIONS.md |
| D-175 | active | `[Q-067]` **Every non-measured LIVE channel's soft fuse sits at | 07-PROCESS/DECISIONS.md |

## I — Improvement items (audits)

| ID | Status | What | Lives in |
|---|---|---|---|
| I-71 | done | P1 | 07-PROCESS/AUDITS.md |
| I-72 | open | P1 | 07-PROCESS/AUDITS.md |
| I-73 | done | P3 | 07-PROCESS/AUDITS.md |
| I-74 | done | P2 | 07-PROCESS/AUDITS.md |
| I-75 | done | P1 | 07-PROCESS/AUDITS.md |
| I-76 | done | P1 | 07-PROCESS/AUDITS.md |
| I-77 | done | P2 | 07-PROCESS/AUDITS.md |
| I-78 | done | P2 | 07-PROCESS/AUDITS.md |
| I-79 | done | P2 | 07-PROCESS/AUDITS.md |
| I-80 | done | P4 | 07-PROCESS/AUDITS.md |
| I-81 | done | P4 | 07-PROCESS/AUDITS.md |
| I-82 | done | P4 | 07-PROCESS/AUDITS.md |
| I-83 | done | P1 | 07-PROCESS/AUDITS.md |
| I-84 | done | P1 | 07-PROCESS/AUDITS.md |
| I-85 | done | P1 | 07-PROCESS/AUDITS.md |
| I-86 | done | P2 | 07-PROCESS/AUDITS.md |
| I-87 | done | P2 | 07-PROCESS/AUDITS.md |
| I-88 | done | P2 | 07-PROCESS/AUDITS.md |
| I-89 | done | P2 | 07-PROCESS/AUDITS.md |
| I-90 | done | P2 | 07-PROCESS/AUDITS.md |
| I-91 | done | P2 | 07-PROCESS/AUDITS.md |
| I-92 | done | P2 | 07-PROCESS/AUDITS.md |
| I-93 | done | P2 | 07-PROCESS/AUDITS.md |
| I-94 | done | P2 | 07-PROCESS/AUDITS.md |
| I-95 | done | P1 | 07-PROCESS/AUDITS.md |
| I-96 | done | P1 | 07-PROCESS/AUDITS.md |
| I-97 | done | P1 | 07-PROCESS/AUDITS.md |
| I-98 | done | P1 | 07-PROCESS/AUDITS.md |
| I-99 | done | P1 | 07-PROCESS/AUDITS.md |
| I-100 | done | P1 | 07-PROCESS/AUDITS.md |
| I-101 | done | P1 | 07-PROCESS/AUDITS.md |
| I-102 | done | P1 | 07-PROCESS/AUDITS.md |
| I-103 | open | P2 | 07-PROCESS/AUDITS.md |
| I-104 | done | P1 | 07-PROCESS/AUDITS.md |
| I-105 | done | P1 | 07-PROCESS/AUDITS.md |
| I-106 | done | P1 | 07-PROCESS/AUDITS.md |
| I-107 | done | P2 | 07-PROCESS/AUDITS.md |
| I-108 | done | P2 | 07-PROCESS/AUDITS.md |
| I-109 | done | P2 | 07-PROCESS/AUDITS.md |
| I-110 | done | P2 | 07-PROCESS/AUDITS.md |
| I-111 | done | P4 | 07-PROCESS/AUDITS.md |
| I-112 | done | P1 | 07-PROCESS/AUDITS.md |
| I-113 | done | P1 | 07-PROCESS/AUDITS.md |
| I-114 | done | P1 | 07-PROCESS/AUDITS.md |
| I-115 | done | P1 | 07-PROCESS/AUDITS.md |
| I-116 | done | P1 | 07-PROCESS/AUDITS.md |
| I-117 | done | P1 | 07-PROCESS/AUDITS.md |
| I-118 | done | P1 | 07-PROCESS/AUDITS.md |
| I-119 | done | P2 | 07-PROCESS/AUDITS.md |
| I-120 | done | P2 | 07-PROCESS/AUDITS.md |
| I-121 | done | P2 | 07-PROCESS/AUDITS.md |
| I-122 | done | P2 | 07-PROCESS/AUDITS.md |
| I-123 | done | P2 | 07-PROCESS/AUDITS.md |
| I-124 | done | P4 | 07-PROCESS/AUDITS.md |
| I-125 | done | P1 | 07-PROCESS/AUDITS.md |
| I-126 | done | P2 | 07-PROCESS/AUDITS.md |
| I-127 | open | P2 | 07-PROCESS/AUDITS.md |
| I-128 | open | P2 | 07-PROCESS/AUDITS.md |
| I-129 | open | P2 | 07-PROCESS/AUDITS.md |
| I-130 | done | P4 | 07-PROCESS/AUDITS.md |
| I-131 | open | P4 | 07-PROCESS/AUDITS.md |
| I-132 | done | P2 | 07-PROCESS/AUDITS.md |
| I-133 | done | P2 | 07-PROCESS/AUDITS.md |
| I-134 | done | P2 | 07-PROCESS/AUDITS.md |
| I-135 | done | P2 | 07-PROCESS/AUDITS.md |
| I-136 | done | P3 | 07-PROCESS/AUDITS.md |
| I-137 | done | P3 | 07-PROCESS/AUDITS.md |
| I-138 | done | P4 | 07-PROCESS/AUDITS.md |
| I-139 | open | P4 | 07-PROCESS/AUDITS.md |
| I-140 | done | P4 | 07-PROCESS/AUDITS.md |
| I-141 | done | P4 | 07-PROCESS/AUDITS.md |
| I-142 | done | P1 | 07-PROCESS/AUDITS.md |
| I-143 | done | P1 | 07-PROCESS/AUDITS.md |
| I-144 | done | P3 | 07-PROCESS/AUDITS.md |
| I-145 | done | P3 | 07-PROCESS/AUDITS.md |
| I-146 | done | P3 | 07-PROCESS/AUDITS.md |
| I-147 | done | P3 | 07-PROCESS/AUDITS.md |
| I-148 | done | P3 | 07-PROCESS/AUDITS.md |
| I-149 | done | P3 | 07-PROCESS/AUDITS.md |
| I-150 | done | P3 | 07-PROCESS/AUDITS.md |
| I-151 | done | P4 | 07-PROCESS/AUDITS.md |
| I-152 | open | P4 | 07-PROCESS/AUDITS.md |
| I-153 | open | P1 | 07-PROCESS/AUDITS.md |
| I-154 | done | P1 | 07-PROCESS/AUDITS.md |
| I-155 | done | P2 | 07-PROCESS/AUDITS.md |
| I-156 | open | P2 | 07-PROCESS/AUDITS.md |
| I-157 | done | P2 | 07-PROCESS/AUDITS.md |
| I-158 | done | P3 | 07-PROCESS/AUDITS.md |
| I-159 | done | P4 | 07-PROCESS/AUDITS.md |
| I-160 | done | P4 | 07-PROCESS/AUDITS.md |
| I-161 | done | P3 | 07-PROCESS/AUDITS.md |
| I-162 | done | P3 | 07-PROCESS/AUDITS.md |
| I-163 | done | P3 | 07-PROCESS/AUDITS.md |
| I-164 | done | P3 | 07-PROCESS/AUDITS.md |
| I-165 | done | P4 | 07-PROCESS/AUDITS.md |

## K — Known issues

| ID | Status | What | Lives in |
|---|---|---|---|
| K-001 | Find and log — Checklist 0.13 (`T-019`) | Wideband O2 wiring tapped into the factory harness, location unknown | 00-CAR/known-issues.md |
| K-002 | Full harness photo survey — Checklist 0.12–0.13 (`T-018`, `T… | Previous-owner splices and hacks — extent unknown | 00-CAR/known-issues.md |
| K-003 | Planned deletion; the timer moves into PMU logic (Checklist … | Interval wiper control unit present | 00-CAR/known-issues.md |
| K-004 | Replacement being researched | Pre-1983 steering box: non-hardened sector shaft, known wear point | 00-CAR/known-issues.md |
| K-005 | Full bushing overhaul planned | Age-related rubber degradation throughout the suspension | 00-CAR/known-issues.md |
| K-006 | Procedure must be confirmed before attempting | Rear compliance link bushings — improper replacement risks chassis damage | 00-CAR/known-issues.md |
| K-007 | Not assessed; `lighting-body/` scope when it is | Rust — extent not surveyed | 00-CAR/known-issues.md |
| K-008 | Not being fixed — D-105. It lives in the factory harness's s… | Turn signals modulate other circuits — fuel pump and tach react to blinker pulses. Traced … | 00-CAR/known-issues.md |
| K-009 | Gone (D-097). Explicitly not wanted | Cruise control unit | 00-CAR/known-issues.md |
| K-010 | Gone (D-097) | Rear wiper and washer | 00-CAR/known-issues.md |
| K-011 | Gone (D-097) | Power antenna | 00-CAR/known-issues.md |
| K-012 | Gone (D-097) | Headlight cleaner | 00-CAR/known-issues.md |
| K-013 | Zero remain post-Weber (D-097) | Cold-start hardware — hot-start relay/motor, sub-zero motor/sensor, choke, carb heater | 00-CAR/known-issues.md |
| K-014 | Dead. New heated mirrors with digital control replace it (D-… | Power mirror control | 00-CAR/known-issues.md |
| K-015 | Not an electrical fault. Out of scope for the PMU project; d… | A/C barely cool — probably low on charge (D-099) | 00-CAR/known-issues.md |
| K-016 | Needs sourcing — Checklist 1.7 (`T-033`) | Hatch latch switch broken | 00-CAR/known-issues.md |
| K-017 | New addition, not a migration — Checklist 1.6 (`T-032`, D-09… | Fuel-door solenoid never existed | 00-CAR/known-issues.md |
| K-018 | Functional — D-040 holds, no software gesture needed to park… | Both retractor manual raise knobs | 00-CAR/known-issues.md |
| K-019 | Not urgent. A proper drain and refill at some point, and eye… | Coolant has never been fully drained or flushed. About half was lost and replaced during t… | 00-CAR/known-issues.md |
| K-020 | No rebuild impact — the switch is deleted; defog moves to th… | Rear defrost switch (G-24) broken | 00-CAR/known-issues.md |
| K-021 | No rebuild impact — deleted by D-038; pop-ups raise from the… | Headlamp retractor switch (E-02) broken — the dash switch, not the column combo switch | 00-CAR/known-issues.md |
| K-022 | Unknown until diagnosed — pump, wiring, or switch? (`T-040`) | Washer fluid pump (D-01) not working | 00-CAR/known-issues.md |
| K-023 | Confirmed dead, not dying — needs replacing (`T-038`, Checkl… | Blower motor (G-14) not working | 00-CAR/known-issues.md |

## L — Lighting-body decisions

| ID | Status | What | Lives in |
|---|---|---|---|
| L-001 | active | Q-047 → **Reverse section: 5 cm wide, 2.2 cm strip height. | lighting-body/DECISIONS.md |
| L-002 | active | Headlamps are not a custom-build item.** A strip of LEDs cannot | lighting-body/DECISIONS.md |
| L-003 | active | Soft fuses must be re-set after any bulb change.** Values set | lighting-body/DECISIONS.md |
| L-004 | active | Hard prerequisite: the electrical rebuild is finished and shaken | lighting-body/DECISIONS.md |

## M — Modifications

| ID | Status | What | Lives in |
|---|---|---|---|
| M-001 | done | Nov 2025 · Fuel · Weber 45 DCOE fitted — Pierce Manifolds K678 kit | 00-CAR/modifications.md |
| M-002 | done | Nov 2025 · Fuel · Carter P4070 fuel pump | 00-CAR/modifications.md |
| M-003 | done | Nov 2025 · Fuel · Fuel pressure regulator | 00-CAR/modifications.md |
| M-004 | done | unknown · Engine mgmt · Wideband O2 installed | 00-CAR/modifications.md |
| M-005 | done | Aug 2025 · Ignition · Coils ×2, cap, rotor, plug wires, plugs | 00-CAR/modifications.md |
| M-006 | done | Sep 2025 · Engine · Intake head gasket, carb gaskets | 00-CAR/modifications.md |
| M-007 | done | Sep 2025 · Service · Oil, pan gasket, drain plug gasket, filter | 00-CAR/modifications.md |
| M-008 | done | Sep 2025 · Belts · Alternator belt | 00-CAR/modifications.md |
| M-009 | done | Jul 2026** · Brakes · **Front overhaul** — rotor hubs, wheel bearings, seals, pads | 00-CAR/modifications.md |
| M-010 | done | Jul 2026** · Brakes · **Rear overhaul** — shoes, drums, wheel bearings, wheel cylinders | 00-CAR/modifications.md |
| M-011 | done | Jul 2026 · Belts · A/C belt fitted | 00-CAR/modifications.md |

## P — Planned modifications

| ID | Status | What | Lives in |
|---|---|---|---|
| P-001 | planned | Electrical · Full PMU-24 DL rewire — **PMU purchased** · [`../02-PROJECTS/electrical-pmu/`… | 00-CAR/modifications.md |
| P-002 | planned | Electrical · Ionic S9 heated lithium battery, rear mount — **purchased, not fitted** · [`B… | 00-CAR/modifications.md |
| P-003 | planned | Suspension · Full bushing + wear-point overhaul · not started | 00-CAR/modifications.md |
| P-004 | planned | Steering · Steering box replacement (sector shaft) · not started | 00-CAR/modifications.md |
| P-005 | planned | Brakes · Rear disc conversion from 84–85 axle · **Still planned** (Q-045 → D-113). The Jul… | 00-CAR/modifications.md |
| P-006 | planned | Drivetrain · LS + CD009 swap · not started — O13/O14 and the L1 sensor spares are reserved… | 00-CAR/modifications.md |

## Q — Questions

| ID | Status | What | Lives in |
|---|---|---|---|
| Q-001 | open | VIN | 07-PROCESS/OPEN.md |
| Q-010 | closed (no decision cites it) |  | — |
| Q-011 | closed by D-051 | `[Q-011]` Head unit is **double-DIN**. `[Q-016]` washer pump is | 07-PROCESS/DECISIONS.md |
| Q-012 | closed by D-074 | `[Q-012]` Seat products stay as **estimates** — 2 × 4 A heat elements, | 07-PROCESS/DECISIONS.md |
| Q-013 | closed by D-048 | `[Q-013]` **Cooled seats are in scope.** Adds fans and ducting to the | 07-PROCESS/DECISIONS.md |
| Q-014 | open | Dash panel envelope | 07-PROCESS/OPEN.md |
| Q-016 | closed by D-051 | `[Q-011]` Head unit is **double-DIN**. `[Q-016]` washer pump is | 07-PROCESS/DECISIONS.md |
| Q-018 | closed (no decision cites it) |  | — |
| Q-019 | closed by D-071 | `[Q-019]` **Inhibitor switch laddered onto one input** on the L1-S | 07-PROCESS/DECISIONS.md |
| Q-020 | closed (no decision cites it) |  | — |
| Q-021 | closed by D-050 | `[Q-021]` Seat belt warning and key reminder chime **dropped**. | 07-PROCESS/DECISIONS.md |
| Q-022 | closed by D-049 | `[Q-022]` **Remote mirror motors kept, plus heated mirrors.** This | 07-PROCESS/DECISIONS.md |
| Q-023 | closed (no decision cites it) |  | — |
| Q-024 | closed by D-069 | `[Q-024]` **Pop-up relays stay in the box.** Confirmed no. The nose | 07-PROCESS/DECISIONS.md |
| Q-025 | closed by D-065 | `[Q-025]` **Window H-bridge relays K5–K8 move to the sill.** Dry, | 07-PROCESS/DECISIONS.md |
| Q-026 | closed by D-072 | `[Q-026]` **Horn gets a dedicated wake diode to pin 7.** Sixth input | 07-PROCESS/DECISIONS.md |
| Q-027 | closed by D-052 | `[Q-027]` L3-S becomes **Deutsch DT-12s instead of AMPSEAL 35 | 07-PROCESS/DECISIONS.md |
| Q-028 | open | CAN wake latency | 07-PROCESS/OPEN.md |
| Q-029 | closed by D-047 | `[Q-029]` **Bulb-out detection dropped entirely.** Manual check is | 07-PROCESS/DECISIONS.md |
| Q-030 | closed by D-070 | `[Q-030]` L3-S is **2 × DT06-12S + 1 × DT06-8S** — 32 cavities, | 07-PROCESS/DECISIONS.md |
| Q-031 | closed by D-068 | `[Q-031]` **The doors get their own connector pair at the sill. | 07-PROCESS/DECISIONS.md |
| Q-032 | closed by D-058 | `[Q-032 provisional]` O15 comfort bus worst case is 17–26 A with | 07-PROCESS/DECISIONS.md |
| Q-033 | closed by D-092 | `[Q-033]` **Door connectors are a single DT06-08S per door.** Window | 07-PROCESS/DECISIONS.md |
| Q-034 | closed by D-093 | `[Q-034]` **Mirrors: option B, independent wiring per side.** The | 07-PROCESS/DECISIONS.md |
| Q-035 | closed by D-094 | `[Q-035]` Two MCUs, DCU and ICU separate. `[Q-036]` CAN2 at | 07-PROCESS/DECISIONS.md |
| Q-036 | closed by D-094 | `[Q-035]` Two MCUs, DCU and ICU separate. `[Q-036]` CAN2 at | 07-PROCESS/DECISIONS.md |
| Q-037 | closed by D-150 | `[Q-037]` **Cluster is ONE WIDE DISPLAY.** Not two round TFTs. | 07-PROCESS/DECISIONS.md |
| Q-038 | closed by D-095 | `[Q-038]` **Cigarette lighter deleted.** Frees 8–10 A on O10 and | 07-PROCESS/DECISIONS.md |
| Q-039 | closed (no decision cites it) |  | — |
| Q-041 | closed by D-106 | `[Q-041 closed on the design side]` **CAN byte layouts finalised. | 07-PROCESS/DECISIONS.md |
| Q-042 | closed by D-109 | `[Q-042]` **IMU fitted to the ICU carrier board.** ~$5 and a few | 07-PROCESS/DECISIONS.md |
| Q-043 | closed by D-090 | `[Q-043]` **No hardwired oil pressure lamp.** Oil pressure is shown | 07-PROCESS/DECISIONS.md |
| Q-044 | closed by D-110 | `[Q-044]` **Pop-ups stay.** Not deleted. K1–K4, the four heavy | 07-PROCESS/DECISIONS.md |
| Q-045 | closed by D-113 | `[Q-045]` **Rear disc conversion is still planned.** The July 2026 | 07-PROCESS/DECISIONS.md |
| Q-046 | closed by D-111 | `[Q-046]` **Tail light driver PCB per housing.** Takes tail, brake, | 07-PROCESS/DECISIONS.md |
| Q-047 | closed by L-001 | Q-047 → **Reverse section: 5 cm wide, 2.2 cm strip height. | 07-PROCESS/DECISIONS.md |
| Q-048 | open | Headlamp unit | lighting-body/OPEN.md |
| Q-049 | closed (no decision cites it) |  | — |
| Q-050 | closed (no decision cites it) |  | — |
| Q-051 | closed (no decision cites it) |  | — |
| Q-052 | closed (no decision cites it) |  | — |
| Q-053 | closed by D-128 | `[Q-053]` **Path 1: a CarPlay head unit.** The Pi minimap is not | 07-PROCESS/DECISIONS.md |
| Q-054 | closed (no decision cites it) |  | — |
| Q-055 | closed by D-149 | `[Q-055]` **Head unit selection criteria set: | 07-PROCESS/DECISIONS.md |
| Q-056 | closed (no decision cites it) |  | — |
| Q-057 | closed (no decision cites it) |  | — |
| Q-058 | closed by D-169 | `[Q-058]` **Cluster pages cycle from a small dedicated momentary | 07-PROCESS/DECISIONS.md |
| Q-059 | closed by D-170 | `[Q-059]` **Fit 8 MB PSRAM to the Teensy 4.1 pads before the ICU | 07-PROCESS/DECISIONS.md |
| Q-060 | open | Display panel selection **← next hardware decision | 07-PROCESS/OPEN.md |
| Q-061 | open | Spare fuse F13 and the two solenoids | 07-PROCESS/OPEN.md |
| Q-062 | open | Conductors from the dash to the sill | 07-PROCESS/OPEN.md |
| Q-063 | open | Four signals with no PMU pin | 07-PROCESS/OPEN.md |
| Q-064 | open | RPM-dependent PMU logic before the ICU exists | 07-PROCESS/OPEN.md |
| Q-065 | open | Dimmer and passing on A15 | 07-PROCESS/OPEN.md |
| Q-066 | closed by D-174 | `[Q-066]` **Suspect and unmeasured LIVE channels get INTERIM soft | 07-PROCESS/DECISIONS.md |
| Q-067 | closed by D-175 | `[Q-067]` **Every non-measured LIVE channel's soft fuse sits at | 07-PROCESS/DECISIONS.md |

## R — Standing rules

| ID | Status | What | Lives in |
|---|---|---|---|
| R1 | standing | Read a file before appending to it. | ASSISTANT.md |
| R2 | standing | A document must be correct top to bottom. | ASSISTANT.md |
| R3 | standing | One owner per fact | ASSISTANT.md |
| R4 | standing | Scope belongs to the project that owns the work | ASSISTANT.md |
| R5 | standing | Every file gets a header | ASSISTANT.md |
| R6 | standing | When code owns a fact, say so in the index | ASSISTANT.md |
| R7 | standing | Cite a closed ID with its closer | ASSISTANT.md |
| R8 | standing | Generated blocks are never edited by hand. | ASSISTANT.md |

## T — Camden's tasks

| ID | Status | What | Lives in |
|---|---|---|---|
| T-001 | done | Clamp DMM with DC current | 07-PROCESS/TASKS-CAMDEN.md |
| T-002 | done | Ionic S9 (heated) | 07-PROCESS/TASKS-CAMDEN.md |
| T-003 | done | PMU-24 DL | 07-PROCESS/TASKS-CAMDEN.md |
| T-004 | open | Alternator output rating off the case | 07-PROCESS/TASKS-CAMDEN.md |
| T-007 | open | Dash cavity envelope | 07-PROCESS/TASKS-CAMDEN.md |
| T-008 | open | Every harness route with string, +15 % | 07-PROCESS/TASKS-CAMDEN.md |
| T-009 | open | Confirm the coil / ignitor configuration matches twin coils + twin igniters | 07-PROCESS/TASKS-CAMDEN.md |
| T-010 | done | Inspection sweep | 07-PROCESS/TASKS-CAMDEN.md |
| T-012 | open | Fuel sender ohm range, empty → full | 07-PROCESS/TASKS-CAMDEN.md |
| T-013 | done | Sicma cavity geometry | 07-PROCESS/TASKS-CAMDEN.md |
| T-014 | open | Clamp every load, steady and stall — headlights lo/hi, wiper lo/hi/stall, defog cold, fuel… | 07-PROCESS/TASKS-CAMDEN.md |
| T-016 | done | Diagnose K-008 | 07-PROCESS/TASKS-CAMDEN.md |
| T-017 | open | Verify connector pin labels in `01-REFERENCE/factory-circuits/` against the scans | 07-PROCESS/TASKS-CAMDEN.md |
| T-018 | open | Photograph the entire harness — connectors, branches, grounds → `01-REFERENCE/photos/` | 07-PROCESS/TASKS-CAMDEN.md |
| T-019 | open | Find and log the wideband tap and every PO splice | 07-PROCESS/TASKS-CAMDEN.md |
| T-020 | done | Compare housing #1 to [`SPEC.md`](../01-DESIGN/SPEC.md) §11 | 07-PROCESS/TASKS-CAMDEN.md |
| T-021 | done | Inventory the PMU box | 07-PROCESS/TASKS-CAMDEN.md |
| T-022 | open | Check the Ionic's state of charge; keep it above BMS cutoff until fitted | 07-PROCESS/TASKS-CAMDEN.md |
| T-023 | open | Continuity-test which ignition outputs stay live in RUN and START | 07-PROCESS/TASKS-CAMDEN.md |
| T-024 | open | Cargo bin vs the Group 25 case. Mock in cardboard before cutting | 07-PROCESS/TASKS-CAMDEN.md |
| T-025 | done | Count terminal stock | 07-PROCESS/TASKS-CAMDEN.md |
| T-026 | done | Bench kit | 07-PROCESS/TASKS-CAMDEN.md |
| T-027 | done | Spare Sicma housings | 07-PROCESS/TASKS-CAMDEN.md |
| T-028 | open | Sill space behind the kick panel — 4 relays, 3 fuse positions, ground stud | 07-PROCESS/TASKS-CAMDEN.md |
| T-029 | open | Battery terminal type — SAE or 3/8 threaded. The battery is here; look at it | 07-PROCESS/TASKS-CAMDEN.md |
| T-030 | open | Rule on the five design packets `Q-061`–`Q-065` in [`OPEN.md`](OPEN.md), and `Q-014` | 07-PROCESS/TASKS-CAMDEN.md |
| T-031 | open | Source the new mirrors — larger, heated, digital control. Confirm the conductor count (`V-… | 07-PROCESS/TASKS-CAMDEN.md |
| T-032 | open | Source a fuel-door solenoid — never existed, this is new (D-098) | 07-PROCESS/TASKS-CAMDEN.md |
| T-033 | open | Source a hatch latch switch — the original is broken (D-098) | 07-PROCESS/TASKS-CAMDEN.md |
| T-034 | open | Measure the tail light aperture — width, height, depth, mounting | lighting-body/TASKS.md |
| T-035 | open | Confirm 7-inch round or rectangular sealed beams on this car, and what is actually fitted … | lighting-body/TASKS.md |
| T-036 | open | Answer `Q-048` — which headlamp unit | lighting-body/TASKS.md |
| T-037 | open | Source DOT/SAE LED modules with published candela, red and white | lighting-body/TASKS.md |
| T-038 | open | Source a blower motor. Confirmed dead (K-023) | 07-PROCESS/TASKS-CAMDEN.md |
| T-039 | open | Source a washer pump — only if T-040 says the pump is dead | 07-PROCESS/TASKS-CAMDEN.md |
| T-040 | open | Diagnose the washer pump (K-022) — pump, wiring, or switch? | 07-PROCESS/TASKS-CAMDEN.md |
| T-041 | open | Confirm the blower is the motor, not the feed — 12 V at the connector with the switch on? … | 07-PROCESS/TASKS-CAMDEN.md |
| T-042 | done | Establish which cavity is pin 1 | 07-PROCESS/TASKS-CAMDEN.md |
| T-043 | open | Mark the housing — paint pen dot beside cavity 1 | 07-PROCESS/TASKS-CAMDEN.md |
| T-044 | open | Order spare 1.5 mm terminals, 211CC2S2160P, ~15 minimum | 07-PROCESS/TASKS-CAMDEN.md |
| T-045 | open | Verify the two inbound housings arrive with terminals, not housing-only | 07-PROCESS/TASKS-CAMDEN.md |
| T-046 | done | Stage 4 — ladder decode | 07-PROCESS/TASKS-CAMDEN.md |
| T-047 | done | Stage 5 — tach measurement | 07-PROCESS/TASKS-CAMDEN.md |
| T-048 | open | Flash and label boards 2 and 3 | 07-PROCESS/TASKS-CAMDEN.md |
| T-049 | open | Record the VIN in `00-CAR/vehicle.md` | 07-PROCESS/TASKS-CAMDEN.md |

## V — Verify items

| ID | Status | What | Lives in |
|---|---|---|---|
| V-001 | open | Stock 12A coil / ignitor configuration — one coil per rotor, leading and trailing, as the factory diagram show… | 07-PROCESS/OPEN.md |
| V-002 | open | Alternator output rating | 07-PROCESS/OPEN.md |
| V-010 | closed by D-045 | `[V-010 RESOLVED]` Connector geometry confirmed from the CAD and the | 07-PROCESS/DECISIONS.md |
| V-013 | closed by D-100 | `[V-013]` Deutsch DTP size-12 confirmed adequate for the 25 A legs. | 07-PROCESS/DECISIONS.md |
| V-014 | open | DT size-16 contact current rating. Catalogue confirms size 20 = 7.5 A | 07-PROCESS/OPEN.md |
| V-016 | closed (no decision cites it) |  | — |
| V-017 | closed (no decision cites it) |  | — |
| V-018 | closed (no decision cites it) |  | — |
| V-019 | open | Can the 12A alternator carry the migrated load | 07-PROCESS/OPEN.md |
| V-021 | open | Horn current draw — estimate 4–8 A the pair; interim fuse 10.0 A set | 07-PROCESS/OPEN.md |
| V-022 | closed (no decision cites it) |  | — |
| V-023 | closed (no decision cites it) |  | — |
| V-024 | closed (no decision cites it) |  | — |
| V-025 | closed (no decision cites it) |  | — |
| V-026 | closed (no decision cites it) |  | — |
| V-027 | closed (no decision cites it) |  | — |
| V-028 | open | Is a one-touch (single wipe) function wanted in the wiper logic | 07-PROCESS/OPEN.md |
| V-029 | closed (no decision cites it) |  | — |
| V-030 | open | Pop-up motor internal limit pinout — drive vs limit pins | 07-PROCESS/OPEN.md |
| V-031 | closed (no decision cites it) |  | — |
| V-032 | closed by D-099 | `[V-032]` A/C is **barely cool, probably low on charge.** Not an | 07-PROCESS/DECISIONS.md |
| V-033 | open | Fuel-door and hatch solenoid channel allocation | 07-PROCESS/OPEN.md |
| V-034 | closed by D-098 | `[V-034]` **The fuel-door solenoid never existed** — it is a new | 07-PROCESS/DECISIONS.md |
| V-035 | closed (no decision cites it) |  | — |
| V-036 | closed (no decision cites it) |  | — |
| V-037 | open | Fuel sender ohm range, empty → full | 07-PROCESS/OPEN.md |
| V-038 | open | Coolant level unit and oscillator still fitted | 07-PROCESS/OPEN.md |
| V-039 | closed (no decision cites it) |  | — |
| V-040 | open | Aeromotive Phantom 340 draw at target pressure | 07-PROCESS/OPEN.md |
| V-041 | closed (no decision cites it) |  | — |
| V-044 | closed by D-115 | `[V-044 CONFIRMED]` **DTP is manufactured in 2-way and 4-way only. | 07-PROCESS/DECISIONS.md |
| V-047 | open | Shielded 16 AWG availability; single-end shield grounding | 07-PROCESS/OPEN.md |
| V-048 | closed by D-096 | `[V-048]` **Radar is a custom subsystem, not a commercial unit. | 07-PROCESS/DECISIONS.md |
| V-049 | closed (no decision cites it) |  | — |
| V-050 | open | Which ignition outputs stay live in RUN and START | 07-PROCESS/OPEN.md |
| V-051 | open | Ionic case dimensions before cutting the cargo bin | 07-PROCESS/OPEN.md |
| V-052 | open | Battery heater trigger and winter draw | 07-PROCESS/OPEN.md |
| V-053 | open | Battery terminal type — SAE or 3/8 threaded. The battery is in hand; **look at it** before the lug order (`T-0… | 07-PROCESS/OPEN.md |
| V-054 | closed (no decision cites it) |  | — |
| V-055 | open | Sill space behind the kick panel — 4 relays, 3 fuse positions, ground stud | 07-PROCESS/OPEN.md |
| V-056 | open | Does the DCU need a constant keep-alive for climate memory at all — or does it restore from SD on wake | 07-PROCESS/OPEN.md |
| V-057 | open | TCAN1042/1051 exact part suffix | 07-PROCESS/OPEN.md |
| V-058 | open | Display nit rating — 800–1000 minimum. | 07-PROCESS/OPEN.md |
| V-059 | open | Teensy 4.1 availability after the Adafruit → SparkFun distribution change | 07-PROCESS/OPEN.md |
| V-060 | open | New mirror conductor count and control protocol | 07-PROCESS/OPEN.md |
| V-061 | open | Radar sensor interface | 07-PROCESS/OPEN.md |
| V-062 | closed by D-114 | `[V-062 closed]` The reference PDF is the **TE Connectivity | 07-PROCESS/DECISIONS.md |
| V-063 | open | Stock tail light aperture — width, height, depth, mounting. The whole strip design is scaled from a nominal 30… | lighting-body/OPEN.md |
| V-064 | open | A DOT/SAE-compliant LED module source, red and white, with published candela | lighting-body/OPEN.md |
| V-065 | open | PMU's own CAN export format.** ECUMaster fixes it, we don't. Gates the PMU half of the message map | 07-PROCESS/OPEN.md |
| V-066 | open | 7-inch round or rectangular sealed beams on this car — and whether LED housings are already fitted ([`LOADS.md… | lighting-body/OPEN.md |
| V-067 | open | Tach pulses per revolution.** Assumed 2 for a 2-rotor off the leading coil. Wrong scales every RPM reading by … | 07-PROCESS/OPEN.md |
| V-068 | closed by D-138 | `[V-068 provisionally answered]` **Pin 1 is top-left**, in the top | 07-PROCESS/DECISIONS.md |
| V-069 | open | Open-barrel crimper die size.** Confirm against a real terminal before buying | 07-PROCESS/OPEN.md |
| V-070 | open | 12A redline.** `stats.h` assumes 7000 rpm, which also sets the tach red zone | 07-PROCESS/OPEN.md |
| V-071 | open | Minimum acceptable oil pressure for a 12A at idle. Assumed 1.0 bar | 07-PROCESS/OPEN.md |
| V-072 | open | FB fuel tank capacity. Assumed 15.9 gal | 07-PROCESS/OPEN.md |
| V-073 | open | IMU mounting orientation on the ICU PCB** must match the axis convention in D-161, or every axis needs a sign … | 07-PROCESS/OPEN.md |
| V-074 | open | Does O8 wiper braking need a park input?** If the PMU's braking feature only works against a park-sense signal… | 07-PROCESS/OPEN.md |
| V-075 | open | Does the PMU have a native shutdown delay** that makes the O22 self-hold latch unnecessary — freeing pin 8 and… | 07-PROCESS/OPEN.md |
| V-076 | closed (no decision cites it) |  | — |
| V-077 | open | Alternator health.** 2026-08 read 0.44 A idle / 0.09 A loaded — not physical (output must RISE with load), but… | 07-PROCESS/OPEN.md |
| V-078 | closed (no decision cites it) |  | — |
| V-079 | closed (no decision cites it) |  | — |
| V-080 | closed (no decision cites it) |  | — |

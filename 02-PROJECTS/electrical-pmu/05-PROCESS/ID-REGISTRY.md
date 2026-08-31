# ID REGISTRY — every permanent ID and its status

*Rev 2026-08-30 · owns: nothing — a generated view. Run `tools/registry.py` after editing DECISIONS, OPEN, TASKS, known-issues, modifications or AUDITS.*

IDs are permanent and never reused (D-043); a gap means something closed. **Cite a closed ID with its closer** — `Q-038 → D-095`, never bare `Q-038` — and `check.py` will stay quiet.

| Prefix | Total | Open / active |
|---|---|---|
| A — Assumptions | 11 | 4 |
| D — Decisions | 201 | 188 |
| I — Improvement items (audits) | 95 | 10 |
| K — Known issues | 23 | 0 |
| L — Lighting decisions (deferred scope) | 4 | 4 |
| M — Modifications | 11 | 0 |
| P — Planned modifications | 6 | 6 |
| Q — Questions | 60 | 4 |
| R — Standing rules | 8 | 8 |
| T — Camden's tasks | 36 | 29 |
| V — Verify items | 71 | 34 |

## A — Assumptions

| ID | Status | What | Lives in |
|---|---|---|---|
| A-001 | closed (no decision cites it) |  | — |
| A-002 | closed (no decision cites it) |  | — |
| A-003 | closed (no decision cites it) |  | — |
| A-004 | closed (no decision cites it) |  | — |
| A-005 | closed by D-148 | `[A-005]` **Start relay K9 mounts high on the inner fender or | 05-PROCESS/DECISIONS.md |
| A-007 | closed by D-112 | `[A-007]` **Converted from an assumption to a task.** The pop-up | 05-PROCESS/DECISIONS.md |
| A-009 | closed by D-091 | `[A-009]` **Main feed upgraded to 2 AWG.** Sized for the LS, not the | 05-PROCESS/DECISIONS.md |
| A-010 | open | Brake fluid level goes to the ICU on DP-ICU 12 via L1-S2 1. Coolant and oil level are optional, have no ICU ca… | 05-PROCESS/OPEN.md |
| A-011 | open | The wideband O2 signal (K-001) is carried to the dash on L1-S1 12 and capped. It is not an ICU input and has n… | 05-PROCESS/OPEN.md |
| A-012 | open | The luggage compartment switch joins the A6 door-pin ladder as a fourth state — re-run the ladder maths before… | 05-PROCESS/OPEN.md |
| A-013 | open | The CAN keypad is powered from the accessory bus O10 (DP-KEY 3), so it is dead when the car sleeps and cannot … | 05-PROCESS/OPEN.md |

## D — Decisions

| ID | Status | What | Lives in |
|---|---|---|---|
| D-001 | active | ECUMaster PMU-24 DL over a conventional relay/fuse box. | 05-PROCESS/DECISIONS.md |
| D-002 | active | Ionic S9 heated lithium battery, rear-mounted. Sold as "Ionic Lithium | 05-PROCESS/DECISIONS.md |
| D-003 | active | Two-tier connector architecture. The 39-pin Sicma is a *device | 05-PROCESS/DECISIONS.md |
| D-004 | active | All 39 cavities terminated at build time. Reserved channels get real | 05-PROCESS/DECISIONS.md |
| D-005 | active | Panel is a single removable aluminum backer plate in the dash, | 05-PROCESS/DECISIONS.md |
| D-006 | superseded by D-075 | DCU/MCU, digital gauge cluster, and electronic A/C controls are | 05-PROCESS/DECISIONS.md |
| D-007 | active | Baseline pinned for the current 12A / Weber configuration. Two 25 A | 05-PROCESS/DECISIONS.md |
| D-008 | superseded by D-030 | Relay bank uses 16 sockets, 10 populated. Six empty sockets are | 05-PROCESS/DECISIONS.md |
| D-009 | active | O1 (motor bus) and O16 (blower) carry the worst inductive loads, | 05-PROCESS/DECISIONS.md |
| D-010 | active | Wipers live on O8 and nothing else does. O8 is the only channel with | 05-PROCESS/DECISIONS.md |
| D-011 | active | O15 assigned as a 25 A comfort bus (heated/cooled seats, heated | 05-PROCESS/DECISIONS.md |
| D-012 | active | A/C compressor clutch stays on the factory switch, off the PMU. | 05-PROCESS/DECISIONS.md |
| D-013 | active | Turn signals flashed natively by the PMU. No flasher unit anywhere | 05-PROCESS/DECISIONS.md |
| D-014 | active | Interval wiper control unit deleted. Intermittent is a software | 05-PROCESS/DECISIONS.md |
| D-015 | active | Tail / park / side marker / plate is one circuit on O6, covering both | 05-PROCESS/DECISIONS.md |
| D-016 | active | Wire base color encodes channel class: RED = 25 A, ORN = 15 A, | 05-PROCESS/DECISIONS.md |
| D-017 | active | Grounds never cross a bulkhead connector. Local star node per zone. | 05-PROCESS/DECISIONS.md |
| D-018 | active | All switch inputs on A1–A8 wired to ground with the internal 10 kΩ | 05-PROCESS/DECISIONS.md |
| D-019 | active | Every multi-position switch gets a resistor ladder from day one | 05-PROCESS/DECISIONS.md |
| D-020 | active | A true-constant bus lives off the PMU entirely, fed from the busbar | 05-PROCESS/DECISIONS.md |
| D-021 | superseded by D-065 | Wink switches and window switches are hardwired to the relay bank, | 05-PROCESS/DECISIONS.md |
| D-022 | active | Housings bought at full cavity count; unused positions filled with a | 05-PROCESS/DECISIONS.md |
| D-023 | active | Parallel-system migration. Factory harness stays intact and powered | 05-PROCESS/DECISIONS.md |
| D-024 | active | Migration order runs least to most consequential, ending with | 05-PROCESS/DECISIONS.md |
| D-025 | active | Soft fuses are set from current measured live in the client during | 05-PROCESS/DECISIONS.md |
| D-026 | active | Working files are Markdown. HTML is generated on demand as a | 05-PROCESS/DECISIONS.md |
| D-027 | active | Signal wire changes from 18 AWG to **16 AWG** throughout. The PMU's | 05-PROCESS/DECISIONS.md |
| D-028 | active | Precision analog signals prefer the **A9–A16** bank over A1–A8. | 05-PROCESS/DECISIONS.md |
| D-029 | active | Four leg connectors replace the seven regional connectors. Legs are | 05-PROCESS/DECISIONS.md |
| D-030 | active | Relay bank defined at 11: eight H-bridge halves (two pop-ups, two | 05-PROCESS/DECISIONS.md |
| D-031 | active | Five dash buttons move to the CAN keypad — horn, parking brake sense, | 05-PROCESS/DECISIONS.md |
| D-032 | active | Power and signal get **separate housings** on every leg. Three | 05-PROCESS/DECISIONS.md |
| D-033 | active | Connector code scheme: `L<leg><class><index>` leg-side, | 05-PROCESS/DECISIONS.md |
| D-034 | superseded by D-052 | Series selection: **Deutsch DTP** (size 12) for all P, **Deutsch DT | 05-PROCESS/DECISIONS.md |
| D-035 | superseded by D-066 | 13 leg connectors total: L1 ×2, L2 ×4, L3 ×3, L4 ×4. L2 and L4 need | 05-PROCESS/DECISIONS.md |
| D-036 | superseded by D-070 | The dash post carries 2 lugs (DP-BAT, DP-GND), the sealed PMU device | 05-PROCESS/DECISIONS.md |
| D-037 | active | The diagnostic port and keypad grounds are the **only** grounds | 05-PROCESS/DECISIONS.md |
| D-038 | active | Retractable headlight switch (E-02) deleted.** Pop-ups raise | 05-PROCESS/DECISIONS.md |
| D-039 | active | Radar detector added.** Control module and minimalist LED display in | 05-PROCESS/DECISIONS.md |
| D-040 | active | No software gesture needed to park the lamps up.** Each retractor | 05-PROCESS/DECISIONS.md |
| D-041 | active | SPEC bumped to **Rev B**. Rev A's connector section, gauges, relay | 05-PROCESS/DECISIONS.md |
| D-042 | active | C1–C7 moved to `99-ARCHIVE/2026-08_superseded-C1-C7-connector-scheme.md` | 05-PROCESS/DECISIONS.md |
| D-043 | active | Task IDs in `TASKS-CAMDEN.md` renumbered T-001…T-019 and reordered | 05-PROCESS/DECISIONS.md |
| D-044 | active | Bulb-out detection confirmed viable on 7 A and 15 A channels | 05-PROCESS/DECISIONS.md |
| D-045 | active | `[V-010 RESOLVED]` Connector geometry confirmed from the CAD and the | 05-PROCESS/DECISIONS.md |
| D-046 | active | Consequence of D-045: every 15 A and 7 A output sits in a 1.5 mm | 05-PROCESS/DECISIONS.md |
| D-047 | active | `[Q-029]` **Bulb-out detection dropped entirely.** Manual check is | 05-PROCESS/DECISIONS.md |
| D-048 | active | `[Q-013]` **Cooled seats are in scope.** Adds fans and ducting to the | 05-PROCESS/DECISIONS.md |
| D-049 | active | `[Q-022]` **Remote mirror motors kept, plus heated mirrors.** This | 05-PROCESS/DECISIONS.md |
| D-050 | active | `[Q-021]` Seat belt warning and key reminder chime **dropped**. | 05-PROCESS/DECISIONS.md |
| D-051 | active | `[Q-011]` Head unit is **double-DIN**. `[Q-016]` washer pump is | 05-PROCESS/DECISIONS.md |
| D-052 | active | `[Q-027]` L3-S becomes **Deutsch DT-12s instead of AMPSEAL 35 | 05-PROCESS/DECISIONS.md |
| D-053 | active | Ladder design principle: **no valid switch position uses a dead | 05-PROCESS/DECISIONS.md |
| D-054 | active | Resistors mount **at the switch**, not at the PMU. One return wire | 05-PROCESS/DECISIONS.md |
| D-055 | active | The A16 key ladder is **not** a single-source ladder. ACC stays live | 05-PROCESS/DECISIONS.md |
| D-056 | active | Wake network uses **1N5819 Schottky** diodes, not 1N4007. The lower | 05-PROCESS/DECISIONS.md |
| D-057 | active | H-bridge relay pairs idle with **both motor legs grounded**, so a | 05-PROCESS/DECISIONS.md |
| D-058 | active | `[Q-032 provisional]` O15 comfort bus worst case is 17–26 A with | 05-PROCESS/DECISIONS.md |
| D-059 | active | PMU shipped **with the mating connector kit and the USB-to-CAN | 05-PROCESS/DECISIONS.md |
| D-060 | active | Battery is a **Group 25 case, ~9.1 × 6.9 × 8.9 in, 14.6 lb, SAE | 05-PROCESS/DECISIONS.md |
| D-061 | active | Starter feed and PMU feed are separate runs from the battery**, | 05-PROCESS/DECISIONS.md |
| D-062 | active | Main protection is **Class-T, not ANL or MIDI**. LiFePO4 delivers | 05-PROCESS/DECISIONS.md |
| D-063 | active | Battery mounts on a **backing plate**, not through sheet metal alone. | 05-PROCESS/DECISIONS.md |
| D-064 | active | A **pull string goes into the tunnel alongside the 4 AWG main feed | 05-PROCESS/DECISIONS.md |
| D-065 | active | `[Q-025]` **Window H-bridge relays K5–K8 move to the sill.** Dry, | 05-PROCESS/DECISIONS.md |
| D-066 | active | Cascade of D-065: **L4-P2 is deleted entirely.** The four 12 AWG | 05-PROCESS/DECISIONS.md |
| D-067 | active | Cascade of D-065: **the in-box relay count drops from 11 to 5. | 05-PROCESS/DECISIONS.md |
| D-068 | active | `[Q-031]` **The doors get their own connector pair at the sill. | 05-PROCESS/DECISIONS.md |
| D-069 | active | `[Q-024]` **Pop-up relays stay in the box.** Confirmed no. The nose | 05-PROCESS/DECISIONS.md |
| D-070 | active | `[Q-030]` L3-S is **2 × DT06-12S + 1 × DT06-8S** — 32 cavities, | 05-PROCESS/DECISIONS.md |
| D-071 | active | `[Q-019]` **Inhibitor switch laddered onto one input** on the L1-S | 05-PROCESS/DECISIONS.md |
| D-072 | active | `[Q-026]` **Horn gets a dedicated wake diode to pin 7.** Sixth input | 05-PROCESS/DECISIONS.md |
| D-073 | active | `[Q-032]` **Comfort bus management defers to the DCU/MCU**, alongside | 05-PROCESS/DECISIONS.md |
| D-074 | active | `[Q-012]` Seat products stay as **estimates** — 2 × 4 A heat elements, | 05-PROCESS/DECISIONS.md |
| D-075 | active | D-006 is SUPERSEDED.** The DCU and digital gauge cluster are in | 05-PROCESS/DECISIONS.md |
| D-076 | superseded by D-083 | The PMU has no spare analog inputs.** All 16 are allocated. Water | 05-PROCESS/DECISIONS.md |
| D-077 | superseded by D-083 | Two nodes, not one: DCU and ICU.** The DCU owns climate, comfort | 05-PROCESS/DECISIONS.md |
| D-078 | active | Single source of truth per signal.** If the PMU measures it, the ICU | 05-PROCESS/DECISIONS.md |
| D-079 | active | CAN2 becomes a **five-node bus**: PMU, keypad, DCU, ICU, future LS | 05-PROCESS/DECISIONS.md |
| D-080 | superseded by D-083 | Two new dash-post connectors: **DP-DCU** (DT06-12S, 11 used) and | 05-PROCESS/DECISIONS.md |
| D-081 | active | The sequencing rule.** The car drives fully on the PMU with dumb | 05-PROCESS/DECISIONS.md |
| D-082 | active | Tach signal gets **opto-isolation or a comparator** at the DCU. Coil | 05-PROCESS/DECISIONS.md |
| D-083 | active | CORRECTS D-076 and D-077.** Sensor acquisition moves from the DCU | 05-PROCESS/DECISIONS.md |
| D-084 | active | Teensy 4.1 for both DCU and ICU.** Same board in both boxes: one | 05-PROCESS/DECISIONS.md |
| D-085 | active | CAN transceivers are **TI TCAN1042 / TCAN1051**, automotive | 05-PROCESS/DECISIONS.md |
| D-086 | active | Vehicle bus is **500 kbps, CAN 2.0B, 11-bit IDs**. The PMU is CAN 2.0 | 05-PROCESS/DECISIONS.md |
| D-087 | active | A second twisted pair runs between DCU and ICU, capped at both | 05-PROCESS/DECISIONS.md |
| D-088 | active | Load-dump TVS on both module supplies is mandatory**, not optional. | 05-PROCESS/DECISIONS.md |
| D-089 | active | Buy **three** Teensy 4.1, not two. A dead module mid-debug otherwise | 05-PROCESS/DECISIONS.md |
| D-090 | active | `[Q-043]` **No hardwired oil pressure lamp.** Oil pressure is shown | 05-PROCESS/DECISIONS.md |
| D-091 | active | `[A-009]` **Main feed upgraded to 2 AWG.** Sized for the LS, not the | 05-PROCESS/DECISIONS.md |
| D-092 | active | `[Q-033]` **Door connectors are a single DT06-08S per door.** Window | 05-PROCESS/DECISIONS.md |
| D-093 | active | `[Q-034]` **Mirrors: option B, independent wiring per side.** The | 05-PROCESS/DECISIONS.md |
| D-094 | active | `[Q-035]` Two MCUs, DCU and ICU separate. `[Q-036]` CAN2 at | 05-PROCESS/DECISIONS.md |
| D-095 | active | `[Q-038]` **Cigarette lighter deleted.** Frees 8–10 A on O10 and | 05-PROCESS/DECISIONS.md |
| D-096 | active | `[V-048]` **Radar is a custom subsystem, not a commercial unit. | 05-PROCESS/DECISIONS.md |
| D-097 | active | Confirmed **gone and not returning**, removed from all specs and | 05-PROCESS/DECISIONS.md |
| D-098 | active | `[V-034]` **The fuel-door solenoid never existed** — it is a new | 05-PROCESS/DECISIONS.md |
| D-099 | active | `[V-032]` A/C is **barely cool, probably low on charge.** Not an | 05-PROCESS/DECISIONS.md |
| D-100 | active | `[V-013]` Deutsch DTP size-12 confirmed adequate for the 25 A legs. | 05-PROCESS/DECISIONS.md |
| D-101 | superseded by D-140 | Bench kit **purchased**: UT210E clamp meter, 3 × Teensy 4.1 with | 05-PROCESS/DECISIONS.md |
| D-102 | active | Three Sicma housings on hand**, each with a full pin set: one from | 05-PROCESS/DECISIONS.md |
| D-103 | superseded by D-135 | Spare terminals deliberately not ordered** pending T-025. Counting | 05-PROCESS/DECISIONS.md |
| D-104 | superseded by D-105 | Housekeeping: **T-016 (diagnose K-008) had been dropped** from the | 05-PROCESS/DECISIONS.md |
| D-105 | active | `[K-008 / T-016]` **The blinker fault is not being fixed.** T-016 is | 05-PROCESS/DECISIONS.md |
| D-106 | active | `[Q-041 closed on the design side]` **CAN byte layouts finalised. | 05-PROCESS/DECISIONS.md |
| D-107 | active | Custom tail lights.** Thin LED strip per side, stock aperture and | 05-PROCESS/DECISIONS.md |
| D-108 | active | Project reorganised into numbered folders: `01-DESIGN` `02-HARNESS` | 05-PROCESS/DECISIONS.md |
| D-109 | active | `[Q-042]` **IMU fitted to the ICU carrier board.** ~$5 and a few | 05-PROCESS/DECISIONS.md |
| D-110 | active | `[Q-044]` **Pop-ups stay.** Not deleted. K1–K4, the four heavy | 05-PROCESS/DECISIONS.md |
| D-111 | active | `[Q-046]` **Tail light driver PCB per housing.** Takes tail, brake, | 05-PROCESS/DECISIONS.md |
| D-112 | active | `[A-007]` **Converted from an assumption to a task.** The pop-up | 05-PROCESS/DECISIONS.md |
| D-113 | active | `[Q-045]` **Rear disc conversion is still planned.** The July 2026 | 05-PROCESS/DECISIONS.md |
| D-114 | active | `[V-062 closed]` The reference PDF is the **TE Connectivity | 05-PROCESS/DECISIONS.md |
| D-115 | active | `[V-044 CONFIRMED]` **DTP is manufactured in 2-way and 4-way only. | 05-PROCESS/DECISIONS.md |
| D-116 | active | Wire sealing ranges confirmed from the catalogue: | 05-PROCESS/DECISIONS.md |
| D-117 | active | `C015` reduced-diameter seal modification exists** for wire with | 05-PROCESS/DECISIONS.md |
| D-118 | active | BOM gap found: secondary wedgelocks are sold separately** and are | 05-PROCESS/DECISIONS.md |
| D-119 | active | The car migrates and drives on stock incandescent bulbs.** Nothing | 05-PROCESS/DECISIONS.md |
| D-120 | active | Inrush tolerance must be configured on every lamp channel** before | 05-PROCESS/DECISIONS.md |
| D-121 | active | The stock dual-filament rear bulb is exactly what the two-channel | 05-PROCESS/DECISIONS.md |
| D-122 | active | Soft fuses must be re-set after any bulb change.** Values set | 05-PROCESS/DECISIONS.md |
| D-123 | active | Lighting split into its own project.** `02-PROJECTS/lighting-body/`. | 05-PROCESS/DECISIONS.md |
| D-124 | active | The electrical project's lighting baseline is stock incandescent. | 05-PROCESS/DECISIONS.md |
| D-125 | active | Four more faults found 2026-08: **defrost switch broken (K-020), | 05-PROCESS/DECISIONS.md |
| D-126 | active | O16 blower sizing comes from the replacement part's spec sheet, not | 05-PROCESS/DECISIONS.md |
| D-127 | active | The pop-up measurement and the limit-switch continuity test are one | 05-PROCESS/DECISIONS.md |
| D-128 | active | `[Q-053]` **Path 1: a CarPlay head unit.** The Pi minimap is not | 05-PROCESS/DECISIONS.md |
| D-129 | active | Audio is the head unit's job.** The hidden Bluetooth A2DP module | 05-PROCESS/DECISIONS.md |
| D-130 | active | The ICU keeps gauges only.** No map, no turn-by-turn strip, no BLE | 05-PROCESS/DECISIONS.md |
| D-131 | active | The windows are MANUAL.** This car has no power window motors, | 05-PROCESS/DECISIONS.md |
| D-132 | active | The sill node shrinks but stays.** Even with no window motors it | 05-PROCESS/DECISIONS.md |
| D-133 | active | O1 motor bus is pop-ups only for now.** Worst case drops from | 05-PROCESS/DECISIONS.md |
| D-134 | active | PMU-24 DL received. Connector cavity layout CONFIRMED in the hand. | 05-PROCESS/DECISIONS.md |
| D-135 | active | Terminal stock counted** `[T-025 closed]`. | 05-PROCESS/DECISIONS.md |
| D-136 | active | Physical orientation reference recorded.** With the PMU sitting | 05-PROCESS/DECISIONS.md |
| D-137 | active | Spare housings ordered from ECUmaster are expected to carry the same | 05-PROCESS/DECISIONS.md |
| D-138 | superseded by D-139 | `[V-068 provisionally answered]` **Pin 1 is top-left**, in the top | 05-PROCESS/DECISIONS.md |
| D-139 | active | `[V-068 CLOSED]` **Connector orientation confirmed** by visual | 05-PROCESS/DECISIONS.md |
| D-140 | active | Inventory correction.** These were previously recorded as purchased | 05-PROCESS/DECISIONS.md |
| D-141 | active | The full plywood bench mule is dropped.** Reduced to a | 05-PROCESS/DECISIONS.md |
| D-142 | active | Ladder ADC verification moves from bench to car**, during Phase 6, | 05-PROCESS/DECISIONS.md |
| D-143 | active | One bench item is non-negotiable: deliberately short an output and | 05-PROCESS/DECISIONS.md |
| D-144 | active | No bench power supply. Supersedes D-143. | 05-PROCESS/DECISIONS.md |
| D-145 | active | The $2 replacement: a 5 A fuse in the main feed for first | 05-PROCESS/DECISIONS.md |
| D-146 | active | Checklist 4.21–4.23 powered panel verification is dropped. | 05-PROCESS/DECISIONS.md |
| D-147 | active | Bench kit final: **~$110–165.** No PSU, no plywood, no pigtail, no | 05-PROCESS/DECISIONS.md |
| D-148 | active | `[A-005]` **Start relay K9 mounts high on the inner fender or | 05-PROCESS/DECISIONS.md |
| D-149 | active | `[Q-055]` **Head unit selection criteria set: | 05-PROCESS/DECISIONS.md |
| D-150 | active | `[Q-037]` **Cluster is ONE WIDE DISPLAY.** Not two round TFTs. | 05-PROCESS/DECISIONS.md |
| D-151 | active | Emerald `#009155` is the single lit colour.** RGB332 `0x11`. | 05-PROCESS/DECISIONS.md |
| D-152 | active | Imperial at the display layer only.** `VehicleState` stores metric | 05-PROCESS/DECISIONS.md |
| D-153 | active | A missing sensor must never render as a real zero. | 05-PROCESS/DECISIONS.md |
| D-154 | active | Bar segments are contiguous, gap 0.** Segment widths grew to hold | 05-PROCESS/DECISIONS.md |
| D-155 | active | Symbols, not words, for the gauge column.** Thermometer, oil can, | 05-PROCESS/DECISIONS.md |
| D-156 | active | Four named axes in the gauge column**, everything derives from | 05-PROCESS/DECISIONS.md |
| D-157 | active | The left column is THREE items, not four.** The G value is the | 05-PROCESS/DECISIONS.md |
| D-158 | active | Digit fields centre by repositioning slots.** `setCentre()` counts | 05-PROCESS/DECISIONS.md |
| D-159 | active | `[I-64]` **The display does NOT cross the harness.** It connects | 05-PROCESS/DECISIONS.md |
| D-160 | active | `[I-65]` **`stats.h` thresholds recorded and flagged. | 05-PROCESS/DECISIONS.md |
| D-161 | active | `[I-68]` **IMU specified.** MPU-6050 or ICM-20948 class, I²C, on the | 05-PROCESS/DECISIONS.md |
| D-162 | active | `[I-66]` **`stats.h` is volatile-only for now.** The `life[]` | 05-PROCESS/DECISIONS.md |
| D-163 | active | `[I-67]` **`stats.h` owns the automated figures; `LOGS.md` owns the | 05-PROCESS/DECISIONS.md |
| D-164 | active | The channel schedule is the measured-to-configured pipeline. | 05-PROCESS/DECISIONS.md |
| D-165 | active | An output with no measured figure stays disabled.** A guessed limit | 05-PROCESS/DECISIONS.md |
| D-166 | active | The entire PMU logic is enterable without any amp figures. | 05-PROCESS/DECISIONS.md |
| D-167 | active | A 100 kΩ bias resistor from +5 V on A15 and A16.** These are the | 05-PROCESS/DECISIONS.md |
| D-168 | active | `[I-117]` **The cluster display is driven over SPI with | 05-PROCESS/DECISIONS.md |
| D-169 | active | `[Q-058]` **Cluster pages cycle from a small dedicated momentary | 05-PROCESS/DECISIONS.md |
| D-170 | active | `[Q-059]` **Fit 8 MB PSRAM to the Teensy 4.1 pads before the ICU | 05-PROCESS/DECISIONS.md |
| D-171 | active | L1-S is two DT06-12S housings, L1-S1 and L1-S2, allocated as | 05-PROCESS/DECISIONS.md |
| D-172 | active | L3-S is allocated as generated: L3-S1 (ladders and switch | 05-PROCESS/DECISIONS.md |
| D-173 | active | Fuel pump soft fuse 4.0 A: measured steady 2.38 A × 1.5, | 05-PROCESS/DECISIONS.md |
| D-174 | active | `[Q-066]` **Suspect and unmeasured LIVE channels get INTERIM soft | 05-PROCESS/DECISIONS.md |
| D-175 | active | `[Q-067]` **Every non-measured LIVE channel's soft fuse sits at | 05-PROCESS/DECISIONS.md |
| D-176 | active | Part replacement is a separate post-PMU project; the washer-pump | 05-PROCESS/DECISIONS.md |
| D-177 | active | `[V-030, T-011]` **The pop-up motor pinout comes from FSM sheet E | 05-PROCESS/DECISIONS.md |
| D-178 | active | `[V-050, T-023]` **The ignition-switch closure comes off FSM sheet | 05-PROCESS/DECISIONS.md |
| D-179 | active | The alternator is not charging: 11.39 V at the battery at idle, | 05-PROCESS/DECISIONS.md |
| D-180 | active | `[Q-061]` **Solenoids on O10 branches with their own fuses; keypad | 05-PROCESS/DECISIONS.md |
| D-181 | active | `[Q-062]` **L4-P 4 becomes the O15 → sill comfort feed** (mirror | 05-PROCESS/DECISIONS.md |
| D-182 | active | `[Q-063]` **Horn is read as the +12V SW pin's logic state, sharing | 05-PROCESS/DECISIONS.md |
| D-183 | active | `[Q-064]` **Interim rules until the ICU puts rpm on CAN 0x200: | 05-PROCESS/DECISIONS.md |
| D-184 | active | `[Q-065]` **A15 becomes a five-state summed ladder — the maths | 05-PROCESS/DECISIONS.md |
| D-185 | active | `[Q-068]` **Replace or rebuild the alternator now, before | 05-PROCESS/DECISIONS.md |
| D-186 | active | Pop-up drive is one run relay per side — K1 (LH), K2 (RH); the | 05-PROCESS/DECISIONS.md |
| D-187 | active | A4/A5 become 4-state transit-plus-inhibitor ladders (H-007 | 05-PROCESS/DECISIONS.md |
| D-188 | active | `[Q-069]` **Door-pin wake: a small PNP (or micro-relay) inverter | 05-PROCESS/DECISIONS.md |
| D-189 | active | `[Q-070]` **K1/K2 coils fed from O1 through steering diodes, each | 05-PROCESS/DECISIONS.md |
| D-190 | active | `[Q-071]` **The horn joins A8's hazard node through 12 kΩ; winks | 05-PROCESS/DECISIONS.md |
| D-191 | active | `[V-056]` **The DCU restores climate memory from SD on wake — no | 05-PROCESS/DECISIONS.md |
| D-192 | active | Instant-on is a hard requirement for the cluster: no OS, no | 05-PROCESS/DECISIONS.md |
| D-193 | active | `[Q-060]` **The cluster display is a 12.3″ bar panel on a | 05-PROCESS/DECISIONS.md |
| D-194 | active | Configure-in-car: the separate PMU bench phase is dropped; the | 05-PROCESS/DECISIONS.md |
| D-195 | active | Keep the old alternator for now; diagnose the excitation | 05-PROCESS/DECISIONS.md |
| D-196 | active | The BOM is rebuilt end to end in purchase/install order — wave | 05-PROCESS/DECISIONS.md |
| D-197 | active | `[V-037, T-012, T-014]` **Fuel sender measured: 6 Ω full · | 05-PROCESS/DECISIONS.md |
| D-198 | active | The alternator gets its factory-spec excitation circuit in the | 05-PROCESS/DECISIONS.md |
| D-199 | active | V-081 sharpened by sheet E, not closed.** The reference decode | 05-PROCESS/DECISIONS.md |
| D-200 | active | The tree is consolidated: five project folders, one money page, | 05-PROCESS/DECISIONS.md |
| D-201 | active | The lighting-body project is dissolved back into electrical-pmu | 05-PROCESS/DECISIONS.md |

## I — Improvement items (audits)

| ID | Status | What | Lives in |
|---|---|---|---|
| I-71 | done | P1 | 05-PROCESS/AUDITS.md |
| I-72 | open | P1 | 05-PROCESS/AUDITS.md |
| I-73 | done | P3 | 05-PROCESS/AUDITS.md |
| I-74 | done | P2 | 05-PROCESS/AUDITS.md |
| I-75 | done | P1 | 05-PROCESS/AUDITS.md |
| I-76 | done | P1 | 05-PROCESS/AUDITS.md |
| I-77 | done | P2 | 05-PROCESS/AUDITS.md |
| I-78 | done | P2 | 05-PROCESS/AUDITS.md |
| I-79 | done | P2 | 05-PROCESS/AUDITS.md |
| I-80 | done | P4 | 05-PROCESS/AUDITS.md |
| I-81 | done | P4 | 05-PROCESS/AUDITS.md |
| I-82 | done | P4 | 05-PROCESS/AUDITS.md |
| I-83 | done | P1 | 05-PROCESS/AUDITS.md |
| I-84 | done | P1 | 05-PROCESS/AUDITS.md |
| I-85 | done | P1 | 05-PROCESS/AUDITS.md |
| I-86 | done | P2 | 05-PROCESS/AUDITS.md |
| I-87 | done | P2 | 05-PROCESS/AUDITS.md |
| I-88 | done | P2 | 05-PROCESS/AUDITS.md |
| I-89 | done | P2 | 05-PROCESS/AUDITS.md |
| I-90 | done | P2 | 05-PROCESS/AUDITS.md |
| I-91 | done | P2 | 05-PROCESS/AUDITS.md |
| I-92 | done | P2 | 05-PROCESS/AUDITS.md |
| I-93 | done | P2 | 05-PROCESS/AUDITS.md |
| I-94 | done | P2 | 05-PROCESS/AUDITS.md |
| I-95 | done | P1 | 05-PROCESS/AUDITS.md |
| I-96 | done | P1 | 05-PROCESS/AUDITS.md |
| I-97 | done | P1 | 05-PROCESS/AUDITS.md |
| I-98 | done | P1 | 05-PROCESS/AUDITS.md |
| I-99 | done | P1 | 05-PROCESS/AUDITS.md |
| I-100 | done | P1 | 05-PROCESS/AUDITS.md |
| I-101 | done | P1 | 05-PROCESS/AUDITS.md |
| I-102 | done | P1 | 05-PROCESS/AUDITS.md |
| I-103 | open | P2 | 05-PROCESS/AUDITS.md |
| I-104 | done | P1 | 05-PROCESS/AUDITS.md |
| I-105 | done | P1 | 05-PROCESS/AUDITS.md |
| I-106 | done | P1 | 05-PROCESS/AUDITS.md |
| I-107 | done | P2 | 05-PROCESS/AUDITS.md |
| I-108 | done | P2 | 05-PROCESS/AUDITS.md |
| I-109 | done | P2 | 05-PROCESS/AUDITS.md |
| I-110 | done | P2 | 05-PROCESS/AUDITS.md |
| I-111 | done | P4 | 05-PROCESS/AUDITS.md |
| I-112 | done | P1 | 05-PROCESS/AUDITS.md |
| I-113 | done | P1 | 05-PROCESS/AUDITS.md |
| I-114 | done | P1 | 05-PROCESS/AUDITS.md |
| I-115 | done | P1 | 05-PROCESS/AUDITS.md |
| I-116 | done | P1 | 05-PROCESS/AUDITS.md |
| I-117 | done | P1 | 05-PROCESS/AUDITS.md |
| I-118 | done | P1 | 05-PROCESS/AUDITS.md |
| I-119 | done | P2 | 05-PROCESS/AUDITS.md |
| I-120 | done | P2 | 05-PROCESS/AUDITS.md |
| I-121 | done | P2 | 05-PROCESS/AUDITS.md |
| I-122 | done | P2 | 05-PROCESS/AUDITS.md |
| I-123 | done | P2 | 05-PROCESS/AUDITS.md |
| I-124 | done | P4 | 05-PROCESS/AUDITS.md |
| I-125 | done | P1 | 05-PROCESS/AUDITS.md |
| I-126 | done | P2 | 05-PROCESS/AUDITS.md |
| I-127 | open | P2 | 05-PROCESS/AUDITS.md |
| I-128 | open | P2 | 05-PROCESS/AUDITS.md |
| I-129 | open | P2 | 05-PROCESS/AUDITS.md |
| I-130 | done | P4 | 05-PROCESS/AUDITS.md |
| I-131 | open | P4 | 05-PROCESS/AUDITS.md |
| I-132 | done | P2 | 05-PROCESS/AUDITS.md |
| I-133 | done | P2 | 05-PROCESS/AUDITS.md |
| I-134 | done | P2 | 05-PROCESS/AUDITS.md |
| I-135 | done | P2 | 05-PROCESS/AUDITS.md |
| I-136 | done | P3 | 05-PROCESS/AUDITS.md |
| I-137 | done | P3 | 05-PROCESS/AUDITS.md |
| I-138 | done | P4 | 05-PROCESS/AUDITS.md |
| I-139 | open | P4 | 05-PROCESS/AUDITS.md |
| I-140 | done | P4 | 05-PROCESS/AUDITS.md |
| I-141 | done | P4 | 05-PROCESS/AUDITS.md |
| I-142 | done | P1 | 05-PROCESS/AUDITS.md |
| I-143 | done | P1 | 05-PROCESS/AUDITS.md |
| I-144 | done | P3 | 05-PROCESS/AUDITS.md |
| I-145 | done | P3 | 05-PROCESS/AUDITS.md |
| I-146 | done | P3 | 05-PROCESS/AUDITS.md |
| I-147 | done | P3 | 05-PROCESS/AUDITS.md |
| I-148 | done | P3 | 05-PROCESS/AUDITS.md |
| I-149 | done | P3 | 05-PROCESS/AUDITS.md |
| I-150 | done | P3 | 05-PROCESS/AUDITS.md |
| I-151 | done | P4 | 05-PROCESS/AUDITS.md |
| I-152 | open | P4 | 05-PROCESS/AUDITS.md |
| I-153 | open | P1 | 05-PROCESS/AUDITS.md |
| I-154 | done | P1 | 05-PROCESS/AUDITS.md |
| I-155 | done | P2 | 05-PROCESS/AUDITS.md |
| I-156 | open | P2 | 05-PROCESS/AUDITS.md |
| I-157 | done | P2 | 05-PROCESS/AUDITS.md |
| I-158 | done | P3 | 05-PROCESS/AUDITS.md |
| I-159 | done | P4 | 05-PROCESS/AUDITS.md |
| I-160 | done | P4 | 05-PROCESS/AUDITS.md |
| I-161 | done | P3 | 05-PROCESS/AUDITS.md |
| I-162 | done | P3 | 05-PROCESS/AUDITS.md |
| I-163 | done | P3 | 05-PROCESS/AUDITS.md |
| I-164 | done | P3 | 05-PROCESS/AUDITS.md |
| I-165 | done | P4 | 05-PROCESS/AUDITS.md |

## K — Known issues

| ID | Status | What | Lives in |
|---|---|---|---|
| K-001 | Find and log — Checklist 0.13 (`T-019`) | Wideband O2 wiring tapped into the factory harness, location unknown | 00-CAR/known-issues.md |
| K-002 | Full harness photo survey — Checklist 0.12–0.13 (`T-018`, `T… | Previous-owner splices and hacks — extent unknown | 00-CAR/known-issues.md |
| K-003 | Planned deletion; the timer moves into PMU logic (Checklist … | Interval wiper control unit present | 00-CAR/known-issues.md |
| K-004 | Replacement being researched | Pre-1983 steering box: non-hardened sector shaft, known wear point | 00-CAR/known-issues.md |
| K-005 | Full bushing overhaul planned | Age-related rubber degradation throughout the suspension | 00-CAR/known-issues.md |
| K-006 | Procedure must be confirmed before attempting | Rear compliance link bushings — improper replacement risks chassis damage | 00-CAR/known-issues.md |
| K-007 | Not assessed; the deferred lighting & body pass surveys it (… | Rust — extent not surveyed | 00-CAR/known-issues.md |
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

## L — Lighting decisions (deferred scope)

| ID | Status | What | Lives in |
|---|---|---|---|
| L-001 | active | Q-047 → **Reverse section: 5 cm wide, 2.2 cm strip height. | 05-PROCESS/DECISIONS.md §Lighting |
| L-002 | active | Headlamps are not a custom-build item.** A strip of LEDs cannot | 05-PROCESS/DECISIONS.md §Lighting |
| L-003 | active | Soft fuses must be re-set after any bulb change.** Values set | 05-PROCESS/DECISIONS.md §Lighting |
| L-004 | active | Hard prerequisite: the electrical rebuild is finished and | 05-PROCESS/DECISIONS.md §Lighting |

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
| Q-001 | open | VIN | 05-PROCESS/OPEN.md |
| Q-010 | closed (no decision cites it) |  | — |
| Q-011 | closed by D-051 | `[Q-011]` Head unit is **double-DIN**. `[Q-016]` washer pump is | 05-PROCESS/DECISIONS.md |
| Q-012 | closed by D-074 | `[Q-012]` Seat products stay as **estimates** — 2 × 4 A heat elements, | 05-PROCESS/DECISIONS.md |
| Q-013 | closed by D-048 | `[Q-013]` **Cooled seats are in scope.** Adds fans and ducting to the | 05-PROCESS/DECISIONS.md |
| Q-014 | open | Dash panel envelope | 05-PROCESS/OPEN.md |
| Q-016 | closed by D-051 | `[Q-011]` Head unit is **double-DIN**. `[Q-016]` washer pump is | 05-PROCESS/DECISIONS.md |
| Q-018 | closed (no decision cites it) |  | — |
| Q-019 | closed by D-071 | `[Q-019]` **Inhibitor switch laddered onto one input** on the L1-S | 05-PROCESS/DECISIONS.md |
| Q-020 | closed (no decision cites it) |  | — |
| Q-021 | closed by D-050 | `[Q-021]` Seat belt warning and key reminder chime **dropped**. | 05-PROCESS/DECISIONS.md |
| Q-022 | closed by D-049 | `[Q-022]` **Remote mirror motors kept, plus heated mirrors.** This | 05-PROCESS/DECISIONS.md |
| Q-023 | closed (no decision cites it) |  | — |
| Q-024 | closed by D-069 | `[Q-024]` **Pop-up relays stay in the box.** Confirmed no. The nose | 05-PROCESS/DECISIONS.md |
| Q-025 | closed by D-065 | `[Q-025]` **Window H-bridge relays K5–K8 move to the sill.** Dry, | 05-PROCESS/DECISIONS.md |
| Q-026 | closed by D-072 | `[Q-026]` **Horn gets a dedicated wake diode to pin 7.** Sixth input | 05-PROCESS/DECISIONS.md |
| Q-027 | closed by D-052 | `[Q-027]` L3-S becomes **Deutsch DT-12s instead of AMPSEAL 35 | 05-PROCESS/DECISIONS.md |
| Q-028 | open | CAN wake latency | 05-PROCESS/OPEN.md |
| Q-029 | closed by D-047 | `[Q-029]` **Bulb-out detection dropped entirely.** Manual check is | 05-PROCESS/DECISIONS.md |
| Q-030 | closed by D-070 | `[Q-030]` L3-S is **2 × DT06-12S + 1 × DT06-8S** — 32 cavities, | 05-PROCESS/DECISIONS.md |
| Q-031 | closed by D-068 | `[Q-031]` **The doors get their own connector pair at the sill. | 05-PROCESS/DECISIONS.md |
| Q-032 | closed by D-058 | `[Q-032 provisional]` O15 comfort bus worst case is 17–26 A with | 05-PROCESS/DECISIONS.md |
| Q-033 | closed by D-092 | `[Q-033]` **Door connectors are a single DT06-08S per door.** Window | 05-PROCESS/DECISIONS.md |
| Q-034 | closed by D-093 | `[Q-034]` **Mirrors: option B, independent wiring per side.** The | 05-PROCESS/DECISIONS.md |
| Q-035 | closed by D-094 | `[Q-035]` Two MCUs, DCU and ICU separate. `[Q-036]` CAN2 at | 05-PROCESS/DECISIONS.md |
| Q-036 | closed by D-094 | `[Q-035]` Two MCUs, DCU and ICU separate. `[Q-036]` CAN2 at | 05-PROCESS/DECISIONS.md |
| Q-037 | closed by D-150 | `[Q-037]` **Cluster is ONE WIDE DISPLAY.** Not two round TFTs. | 05-PROCESS/DECISIONS.md |
| Q-038 | closed by D-095 | `[Q-038]` **Cigarette lighter deleted.** Frees 8–10 A on O10 and | 05-PROCESS/DECISIONS.md |
| Q-039 | closed (no decision cites it) |  | — |
| Q-041 | closed by D-106 | `[Q-041 closed on the design side]` **CAN byte layouts finalised. | 05-PROCESS/DECISIONS.md |
| Q-042 | closed by D-109 | `[Q-042]` **IMU fitted to the ICU carrier board.** ~$5 and a few | 05-PROCESS/DECISIONS.md |
| Q-043 | closed by D-090 | `[Q-043]` **No hardwired oil pressure lamp.** Oil pressure is shown | 05-PROCESS/DECISIONS.md |
| Q-044 | closed by D-110 | `[Q-044]` **Pop-ups stay.** Not deleted. K1–K4, the four heavy | 05-PROCESS/DECISIONS.md |
| Q-045 | closed by D-113 | `[Q-045]` **Rear disc conversion is still planned.** The July 2026 | 05-PROCESS/DECISIONS.md |
| Q-046 | closed by D-111 | `[Q-046]` **Tail light driver PCB per housing.** Takes tail, brake, | 05-PROCESS/DECISIONS.md |
| Q-047 | closed by L-001 | Q-047 → **Reverse section: 5 cm wide, 2.2 cm strip height. | 05-PROCESS/DECISIONS.md |
| Q-048 | open | Headlamp unit | 05-PROCESS/OPEN.md |
| Q-049 | closed (no decision cites it) |  | — |
| Q-050 | closed (no decision cites it) |  | — |
| Q-051 | closed (no decision cites it) |  | — |
| Q-052 | closed (no decision cites it) |  | — |
| Q-053 | closed by D-128 | `[Q-053]` **Path 1: a CarPlay head unit.** The Pi minimap is not | 05-PROCESS/DECISIONS.md |
| Q-054 | closed (no decision cites it) |  | — |
| Q-055 | closed by D-149 | `[Q-055]` **Head unit selection criteria set: | 05-PROCESS/DECISIONS.md |
| Q-056 | closed (no decision cites it) |  | — |
| Q-057 | closed (no decision cites it) |  | — |
| Q-058 | closed by D-169 | `[Q-058]` **Cluster pages cycle from a small dedicated momentary | 05-PROCESS/DECISIONS.md |
| Q-059 | closed by D-170 | `[Q-059]` **Fit 8 MB PSRAM to the Teensy 4.1 pads before the ICU | 05-PROCESS/DECISIONS.md |
| Q-060 | closed by D-193 | `[Q-060]` **The cluster display is a 12.3″ bar panel on a | 05-PROCESS/DECISIONS.md |
| Q-061 | closed by D-180 | `[Q-061]` **Solenoids on O10 branches with their own fuses; keypad | 05-PROCESS/DECISIONS.md |
| Q-062 | closed by D-181 | `[Q-062]` **L4-P 4 becomes the O15 → sill comfort feed** (mirror | 05-PROCESS/DECISIONS.md |
| Q-063 | closed by D-182 | `[Q-063]` **Horn is read as the +12V SW pin's logic state, sharing | 05-PROCESS/DECISIONS.md |
| Q-064 | closed by D-183 | `[Q-064]` **Interim rules until the ICU puts rpm on CAN 0x200: | 05-PROCESS/DECISIONS.md |
| Q-065 | closed by D-184 | `[Q-065]` **A15 becomes a five-state summed ladder — the maths | 05-PROCESS/DECISIONS.md |
| Q-066 | closed by D-174 | `[Q-066]` **Suspect and unmeasured LIVE channels get INTERIM soft | 05-PROCESS/DECISIONS.md |
| Q-067 | closed by D-175 | `[Q-067]` **Every non-measured LIVE channel's soft fuse sits at | 05-PROCESS/DECISIONS.md |
| Q-068 | closed by D-185 | `[Q-068]` **Replace or rebuild the alternator now, before | 05-PROCESS/DECISIONS.md |
| Q-069 | closed by D-188 | `[Q-069]` **Door-pin wake: a small PNP (or micro-relay) inverter | 05-PROCESS/DECISIONS.md |
| Q-070 | closed by D-189 | `[Q-070]` **K1/K2 coils fed from O1 through steering diodes, each | 05-PROCESS/DECISIONS.md |
| Q-071 | closed by D-190 | `[Q-071]` **The horn joins A8's hazard node through 12 kΩ; winks | 05-PROCESS/DECISIONS.md |

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
| T-004 | open | Alternator rating from the FSM or the parts counter (case is unreadable) | 05-PROCESS/TASKS-CAMDEN.md |
| T-007 | open | Dash cavity envelope — W × H × D + 39-pin lever clearance, and how deep the cluster brow s… | 05-PROCESS/TASKS-CAMDEN.md |
| T-008 | open | Every harness route with string, +15 % | 05-PROCESS/TASKS-CAMDEN.md |
| T-009 | open | Confirm twin coils + twin igniters under the hood | 05-PROCESS/TASKS-CAMDEN.md |
| T-010 | done | Inspection sweep → D-097–D-100 | 05-PROCESS/TASKS-CAMDEN.md |
| T-012 | done | Fuel sender 6 / 31.5 / 80 Ω (`V-037` → D-197) — LADDERS §A7 | 05-PROCESS/TASKS-CAMDEN.md |
| T-014 | done | The measurement campaign, complete (D-175, D-197) | 05-PROCESS/TASKS-CAMDEN.md |
| T-016 | cancelled | Cancelled — K-008 dies with the harness (D-105) | 05-PROCESS/TASKS-CAMDEN.md |
| T-017 | open | Verify connector pin labels in `01-REFERENCE/factory-circuits/` against the scans | 05-PROCESS/TASKS-CAMDEN.md |
| T-018 | open | Photograph the entire harness — connectors, branches, grounds → `01-REFERENCE/photos/` | 05-PROCESS/TASKS-CAMDEN.md |
| T-019 | open | Find and log the wideband tap and every PO splice | 05-PROCESS/TASKS-CAMDEN.md |
| T-022 | open | Check the Ionic's state of charge; keep it above BMS cutoff | 05-PROCESS/TASKS-CAMDEN.md |
| T-023 | done | Ignition closure off FSM sheet F (`V-050` → D-178) | 05-PROCESS/TASKS-CAMDEN.md |
| T-024 | open | Cargo bin vs the Group 25 case. Mock in cardboard before cutting | 05-PROCESS/TASKS-CAMDEN.md |
| T-028 | open | Sill space behind the kick panel — 4 relays, 3 fuse positions, ground stud | 05-PROCESS/TASKS-CAMDEN.md |
| T-029 | open | Battery terminal type — SAE or 3/8 threaded. Look at it | 05-PROCESS/TASKS-CAMDEN.md |
| T-030 | done | The five 0.23 packets ruled (`Q-061` → D-180 … `Q-065` → D-184) | 05-PROCESS/TASKS-CAMDEN.md |
| T-031 | open | Mirrors — larger, heated, digital; confirm the conductor count (`V-060`; D1/D2 has zero sp… | 05-PROCESS/TASKS-CAMDEN.md |
| T-032 | open | Fuel-door solenoid — never existed (D-098); output ruled (`Q-061` → D-180) | 05-PROCESS/TASKS-CAMDEN.md |
| T-033 | open | Hatch latch switch — the original is broken (D-098) | 05-PROCESS/TASKS-CAMDEN.md |
| T-034 | open | Measure the tail light aperture — width, height, depth, mounting | 05-PROCESS/TASKS-CAMDEN.md |
| T-035 | open | Confirm 7-inch round or rectangular sealed beams on this car, and what is actually fitted … | 05-PROCESS/TASKS-CAMDEN.md |
| T-036 | open | Answer `Q-048` — which headlamp unit | 05-PROCESS/TASKS-CAMDEN.md |
| T-037 | open | Source DOT/SAE LED modules with published candela, red and white | 05-PROCESS/TASKS-CAMDEN.md |
| T-038 | open | Blower motor — confirmed dead (K-023); O16's fuse comes from its spec (D-126) | 05-PROCESS/TASKS-CAMDEN.md |
| T-039 | open | Washer pump — only if the post-PMU diagnosis (T-040, D-176) condemns it | 05-PROCESS/TASKS-CAMDEN.md |
| T-040 | open | Washer diagnosis — deferred post-PMU (D-176) | 05-PROCESS/TASKS-CAMDEN.md |
| T-041 | open | Confirm the blower is the motor, not the feed — 12 V at the connector with the switch on? … | 05-PROCESS/TASKS-CAMDEN.md |
| T-043 | open | Paint-pen dot beside cavity 1 (Wave 0 pen) | 05-PROCESS/TASKS-CAMDEN.md |
| T-044 | open | Order spare 1.5 mm terminals ×15 + 120 Ω ×4 — Wave 1 cart | 05-PROCESS/TASKS-CAMDEN.md |
| T-045 | open | Verify the two inbound housings arrive with terminals | 05-PROCESS/TASKS-CAMDEN.md |
| T-048 | open | Flash and label boards 2 and 3 (headers need the Phase-5 iron) | 05-PROCESS/TASKS-CAMDEN.md |
| T-049 | open | Record the VIN in `00-CAR/vehicle.md` | 05-PROCESS/TASKS-CAMDEN.md |
| T-050 | done | Superseded by D-198 — the factory-spec exciter is wired instead of pre-diagnosing; the alt… | 05-PROCESS/TASKS-CAMDEN.md |
| T-051 | open | BT817 eval board, then bridge + glass per `V-085` | 05-PROCESS/TASKS-CAMDEN.md |
| T-052 | open | Pop-up ohm check at E-03 (`V-081`, D-199) — unplugged, ohms R → case and RY → case at park… | 05-PROCESS/TASKS-CAMDEN.md |

## V — Verify items

| ID | Status | What | Lives in |
|---|---|---|---|
| V-001 | open | Stock 12A coil / ignitor configuration — one coil per rotor, leading and trailing, as the factory diagram show… | 05-PROCESS/OPEN.md |
| V-002 | open | Alternator output rating — the case says only 'B' / Mitsubishi (2026-08), no rating readable | 05-PROCESS/OPEN.md |
| V-010 | closed by D-045 | `[V-010 RESOLVED]` Connector geometry confirmed from the CAD and the | 05-PROCESS/DECISIONS.md |
| V-013 | closed by D-100 | `[V-013]` Deutsch DTP size-12 confirmed adequate for the 25 A legs. | 05-PROCESS/DECISIONS.md |
| V-014 | open | DT size-16 contact current rating. Catalogue confirms size 20 = 7.5 A | 05-PROCESS/OPEN.md |
| V-016 | closed (no decision cites it) |  | — |
| V-017 | closed (no decision cites it) |  | — |
| V-018 | closed (no decision cites it) |  | — |
| V-019 | open | Can a healthy stock-rating alternator carry the migrated load | 05-PROCESS/OPEN.md |
| V-021 | open | Horn current draw — estimate 4–8 A the pair; fuse at the 15.0 cap (D-175) | 05-PROCESS/OPEN.md |
| V-022 | closed (no decision cites it) |  | — |
| V-023 | closed (no decision cites it) |  | — |
| V-024 | closed (no decision cites it) |  | — |
| V-025 | closed (no decision cites it) |  | — |
| V-026 | closed (no decision cites it) |  | — |
| V-027 | closed (no decision cites it) |  | — |
| V-028 | open | Is a one-touch (single wipe) function wanted in the wiper logic | 05-PROCESS/OPEN.md |
| V-029 | closed (no decision cites it) |  | — |
| V-030 | closed by D-177 | `[V-030, T-011]` **The pop-up motor pinout comes from FSM sheet E | 05-PROCESS/DECISIONS.md |
| V-031 | closed (no decision cites it) |  | — |
| V-032 | closed by D-099 | `[V-032]` A/C is **barely cool, probably low on charge.** Not an | 05-PROCESS/DECISIONS.md |
| V-033 | closed (no decision cites it) |  | — |
| V-034 | closed by D-098 | `[V-034]` **The fuel-door solenoid never existed** — it is a new | 05-PROCESS/DECISIONS.md |
| V-035 | closed (no decision cites it) |  | — |
| V-036 | closed (no decision cites it) |  | — |
| V-037 | closed by D-197 | `[V-037, T-012, T-014]` **Fuel sender measured: 6 Ω full · | 05-PROCESS/DECISIONS.md |
| V-038 | open | Coolant level unit and oscillator still fitted | 05-PROCESS/OPEN.md |
| V-039 | closed (no decision cites it) |  | — |
| V-040 | open | Aeromotive Phantom 340 draw at target pressure | 05-PROCESS/OPEN.md |
| V-041 | closed (no decision cites it) |  | — |
| V-044 | closed by D-115 | `[V-044 CONFIRMED]` **DTP is manufactured in 2-way and 4-way only. | 05-PROCESS/DECISIONS.md |
| V-047 | open | Shielded 16 AWG availability; single-end shield grounding | 05-PROCESS/OPEN.md |
| V-048 | closed by D-096 | `[V-048]` **Radar is a custom subsystem, not a commercial unit. | 05-PROCESS/DECISIONS.md |
| V-049 | closed (no decision cites it) |  | — |
| V-050 | closed by D-178 | `[V-050, T-023]` **The ignition-switch closure comes off FSM sheet | 05-PROCESS/DECISIONS.md |
| V-051 | open | Ionic case dimensions before cutting the cargo bin | 05-PROCESS/OPEN.md |
| V-052 | open | Battery heater trigger and winter draw | 05-PROCESS/OPEN.md |
| V-053 | open | Battery terminal type — SAE or 3/8 threaded. The battery is in hand; **look at it** before the lug order (`T-0… | 05-PROCESS/OPEN.md |
| V-054 | closed (no decision cites it) |  | — |
| V-055 | open | Sill space behind the kick panel — 4 relays, 3 fuse positions, ground stud | 05-PROCESS/OPEN.md |
| V-056 | closed by D-191 | `[V-056]` **The DCU restores climate memory from SD on wake — no | 05-PROCESS/DECISIONS.md |
| V-057 | open | TCAN1042/1051 exact part suffix | 05-PROCESS/OPEN.md |
| V-058 | closed (no decision cites it) |  | — |
| V-059 | open | Teensy 4.1 availability after the Adafruit → SparkFun distribution change | 05-PROCESS/OPEN.md |
| V-060 | open | New mirror conductor count and control protocol | 05-PROCESS/OPEN.md |
| V-061 | open | Radar sensor interface | 05-PROCESS/OPEN.md |
| V-062 | closed by D-114 | `[V-062 closed]` The reference PDF is the **TE Connectivity | 05-PROCESS/DECISIONS.md |
| V-063 | open | Stock tail light aperture — width, height, depth, mounting. The whole strip design is scaled from a nominal 30… | 05-PROCESS/OPEN.md |
| V-064 | open | A DOT/SAE-compliant LED module source, red and white, with published candela | 05-PROCESS/OPEN.md |
| V-065 | open | PMU's own CAN export format.** ECUMaster fixes it, we don't. Gates the PMU half of the message map | 05-PROCESS/OPEN.md |
| V-066 | open | 7-inch round or rectangular sealed beams on this car — and whether LED housings are already fitted ([`../01-DE… | 05-PROCESS/OPEN.md |
| V-067 | open | Tach pulses per revolution.** Assumed 2 for a 2-rotor off the leading coil. Wrong scales every RPM reading by … | 05-PROCESS/OPEN.md |
| V-068 | closed by D-138 | `[V-068 provisionally answered]` **Pin 1 is top-left**, in the top | 05-PROCESS/DECISIONS.md |
| V-069 | open | Open-barrel crimper die size.** Confirm against a real terminal before buying | 05-PROCESS/OPEN.md |
| V-070 | open | 12A redline.** `stats.h` assumes 7000 rpm, which also sets the tach red zone | 05-PROCESS/OPEN.md |
| V-071 | open | Minimum acceptable oil pressure for a 12A at idle. Assumed 1.0 bar | 05-PROCESS/OPEN.md |
| V-072 | open | FB fuel tank capacity. Assumed 15.9 gal | 05-PROCESS/OPEN.md |
| V-073 | open | IMU mounting orientation on the ICU PCB** must match the axis convention in D-161, or every axis needs a sign … | 05-PROCESS/OPEN.md |
| V-074 | open | Does O8 wiper braking need a park input?** If the PMU's braking feature only works against a park-sense signal… | 05-PROCESS/OPEN.md |
| V-075 | open | Does the PMU have a native shutdown delay** that makes the O22 self-hold latch unnecessary — freeing pin 8 and… | 05-PROCESS/OPEN.md |
| V-076 | closed (no decision cites it) |  | — |
| V-077 | closed (no decision cites it) |  | — |
| V-078 | closed (no decision cites it) |  | — |
| V-079 | closed (no decision cites it) |  | — |
| V-080 | closed (no decision cites it) |  | — |
| V-081 | open | Pop-up drive conductors** (D-199): sheet E says WR = constant, R + RY = the two commands, YG = indicator — but… | 05-PROCESS/OPEN.md |
| V-082 | open | ICU carrier candidate parts — LMR33630-class buck, SMBJ33A TVS, BAT54S clamps, H11L1/LM393 tach front end ([`I… | 05-PROCESS/OPEN.md |
| V-083 | open | DCU carrier candidate parts — second buck for the servo rail, AOD4184-class FETs, INA180 shunt amp ([`DCU-CARR… | 05-PROCESS/OPEN.md |
| V-084 | open | BT817 output timing vs the chosen glass** (D-193): pixel clock, sync polarity, and the bridge — SN75LVDS83B se… | 05-PROCESS/OPEN.md |
| V-085 | open | Which glass** (D-193; absorbs `V-058`): LQ123K1LG03 measured at **330 cd/m²** — chain (i) only works if the bi… | 05-PROCESS/OPEN.md |
| V-086 | closed (no decision cites it) |  | — |

# Decision Log — Electrical / PMU

*Rev 2026-08-31 · owns: every decision, D-001 onward — the electrical D-series plus the merged lighting L-series (D-201) — append-only. Never edit or delete an entry. To reverse one, add a new decision and put a `> SUPERSEDED BY D-xxx` line under the old one. The registry of every ID is `ID-REGISTRY.md`.*

**Entry format:** `**D-nnn** — [closes Q/V/A/I-nnn, if any] **decision in bold.** Reasoning.`
Entries are grouped by the round in which they were made; the index below is
by topic. Later rounds are H2 sections in date order.

## Contents

Index by topic · Architecture · Channel allocation · Wiring rules · Build sequence · Update 2026-08 answers applied (D-065 →) · Round three (D-091 →) · Round four (D-109 →) · Cluster implementation (D-150 →) · Audit 4 (D-168 →) · Consolidation 2026-08-31 (D-200 →)

## Index by topic

| Topic | Decisions |
|---|---|
| **Core architecture** | D-001 PMU chosen · D-002 Ionic S9 · D-003 two-tier · D-004 all 39 cavities · D-005 removable panel · D-029 four legs · D-032 power/signal split |
| **Channel allocation** | D-009 flyback channels · D-010 wipers on O8 · D-011 comfort bus · D-012 A/C on factory switch · D-013 native flashers · D-015 one marker circuit · D-095 lighter deleted |
| **Wiring rules** | D-016 colour = class · D-017 grounds never cross a bulkhead · D-018 switch to ground · D-019 ladder everything · D-020 constant bus off the PMU · D-022 full cavity count · D-027 16 AWG signal · D-091 2 AWG main feed |
| **Connectors** | D-033 naming scheme · D-034 Deutsch only · D-035/070 housing counts · D-045 cavity geometry confirmed · D-046 terminal sizes · D-092 one housing per door |
| **Relays & sill** | D-030 eleven relays · D-057 H-bridges brake · D-065 windows to the sill · D-067 five in the box · D-068 door connectors |
| **Modules** | D-075 DCU in scope · D-077/083 ICU owns sensors · D-078 single source per signal · D-079 five-node bus · D-084 Teensy 4.1 · D-085 TCAN · D-086 500 kbps · D-087 private link · D-088 load-dump TVS |
| **Ladders & schematics** | D-053 no dead shorts · D-054 resistors at the switch · D-055 key ladder sums · D-056 Schottky wake diodes · D-072 horn wake diode |
| **Build sequence** | D-023 parallel migration · D-024 migration order · D-025 measured soft fuses · D-081 modules join a finished car |
| **Deletions** | D-038 retract switch · D-047 bulb-out dropped · D-050 chimes dropped · D-097 six subsystems gone · D-105 blinker fault not fixed |
| **Housekeeping** | D-026 markdown · D-041 Rev B · D-042 archive · D-043 ID permanence · D-101–104 purchases (→ D-135, D-140) · D-123 lighting split · D-141 bench mule dropped |
| **Measurement & config** | D-119 migrate on incandescent · D-120 inrush windows · D-122 re-set after LED · D-142 ladders verified in car · D-164 channel schedule · D-165 unmeasured stays disabled · D-166 logic before amps · D-167 A15/A16 bias |
| **Cluster & ICU** | D-150 one wide display · D-151–158 palette, units, faults, layout · D-159 display off the harness · D-160–163 `stats.h` · D-168 SPI dirty-rectangle · D-169 page button · D-170 PSRAM |
| **Harness allocations** | D-131 windows manual, bridge provisioned · D-132 sill kept · D-134/139 cavity geometry and pin 1 · D-148 K9 location · D-171 L1-S as generated · D-172 L3-S as generated |
| **Consolidation & lighting** | D-200 folder renumber, BUY-LIST absorbed · D-201 lighting fold-in (amends D-123) · L-001 … L-004 merged |
| **Expedited order (2026-08-31)** | D-202 one-teardown buy, wire margins · D-203 sourcing calls (Class-T 5007100/5114, independent ATC blocks, PT-E300, iCrimp pair, HM318, ECUKB8) |

---

## Architecture

**D-001** — ECUMaster PMU-24 DL over a conventional relay/fuse box.
Accepted ~$2,500 premium for per-channel current logging, soft fuses set from
measured draw, and logic without physical relays.

**D-002** — Ionic S9 heated lithium battery, rear-mounted. Sold as "Ionic Lithium
12V S9 — Car Post Starter Heater Battery"; some listings abbreviate the heated
car variant as *S9H*. Same product. **This project uses "S9".**

**D-003** — Two-tier connector architecture. The 39-pin Sicma is a *device*
connector on the panel; wires run 6–18 in to seven regional bulkhead connectors
on the panel edge. Harness segments plug into regions.

**D-004** — All 39 cavities terminated at build time. Reserved channels get real
wire routed to the correct bulkhead and capped there. The 39-pin is assembled
once and never reopened.

**D-005** — Panel is a single removable aluminum backer plate in the dash,
carrying PMU + 10 relays + 13 fuses. Interfaces to the car via 2 battery lugs
and 7 plugs.

**D-006** — DCU/MCU, digital gauge cluster, and electronic A/C controls are
deferred to separate later projects. The car must drive fully on dumb switches.

> SUPERSEDED BY D-075 — the DCU and ICU are in scope; D-081 keeps the dumb-switch rule.

**D-007** — Baseline pinned for the current 12A / Weber configuration. Two 25 A
channels (O13, O14) reserved for LS ECU/injectors and LS cooling fans.

**D-008** — Relay bank uses 16 sockets, 10 populated. Six empty sockets are
cheap future-proofing.

> SUPERSEDED BY D-030 (eleven relays) and D-067 (five on the plate, ten sockets).

## Channel allocation

**D-009** — O1 (motor bus) and O16 (blower) carry the worst inductive loads,
because those are the only two channels with integrated high-power flyback diodes.

**D-010** — Wipers live on O8 and nothing else does. O8 is the only channel with
wiper motor braking.

**D-011** — O15 assigned as a 25 A comfort bus (heated/cooled seats, heated
mirrors, washer nozzles, wiper park de-icer), fanned out downstream. Chosen over
holding it as a third LS reservation.

**D-012** — A/C compressor clutch stays on the factory switch, off the PMU.

**D-013** — Turn signals flashed natively by the PMU. No flasher unit anywhere
in the car.

**D-014** — Interval wiper control unit deleted. Intermittent is a software
timer on O8.

**D-015** — Tail / park / side marker / plate is one circuit on O6, covering both
PARK and HEAD positions of the 3-position headlight switch.

## Wiring rules

**D-016** — Wire base color encodes channel class: RED = 25 A, ORN = 15 A,
VIO = 7 A, GRY = analog input. Tracer encodes circuit.

**D-017** — Grounds never cross a bulkhead connector. Local star node per zone.
Pin 25 is the only ground on the panel and carries flyback return for every
inductive load.

**D-018** — All switch inputs on A1–A8 wired to ground with the internal 10 kΩ
pull-up. Never switched 12 V. Only A9–A16 read 12 V directly, which is why key
position and headlight switch live there.

**D-019** — Every multi-position switch gets a resistor ladder from day one —
turn stalk, wiper stalk, headlight switch, key, pop-up limits L/R, door pins.
Retrofitting a ladder onto point-to-point wiring is a re-pin.

**D-020** — A true-constant bus lives off the PMU entirely, fed from the busbar
through its own fuses. Head unit clock and diagnostic port. The PMU sleeps.

**D-021** — Wink switches and window switches are hardwired to the relay bank,
not routed through PMU inputs. Only motor legs cross into the doors and nose.

> SUPERSEDED BY D-065 (window switching moved to the sill) and D-131 (the windows are manual; the bridge is provisioned empty). Wink switches still go to the plate.

**D-022** — Housings bought at full cavity count; unused positions filled with a
capped wire, not a sealing plug.

## Build sequence

**D-023** — Parallel-system migration. Factory harness stays intact and powered
until each circuit's individual cutover. Never both connected to one load.

**D-024** — Migration order runs least to most consequential, ending with
ignition and start. The car drives home at the end of every session.

**D-025** — Soft fuses are set from current measured live in the client during
migration, never from an estimate.

**D-026** — Working files are Markdown. HTML is generated on demand as a
printable view only.

**D-027** — Signal wire changes from 18 AWG to **16 AWG** throughout. The PMU's
1.5 mm terminal (211CC2S2160P) is specified 13–17 AWG; 18 AWG sits below its
range and would crimp unreliably. Affects the cut list, the connector BOM, and
every input row in SPEC.

**D-028** — Precision analog signals prefer the **A9–A16** bank over A1–A8.
A9–A16 are 12-bit over 0–20 V; A1–A8 are 10-bit over 0–5 V. Key position and
headlight ladder already live there; any future sender wanting resolution should
too.

**D-029** — Four leg connectors replace the seven regional connectors. Legs are
cut by removal boundary, not connector convenience. C1–C7 in SPEC §4 are
superseded and need rebuilding against `legs/`.

**D-030** — Relay bank defined at 11: eight H-bridge halves (two pop-ups, two
windows), the start relay at the starter, the factory A/C clutch relay, and a
constant-bus master driven by the O22 keep-alive latch.

> SUPERSEDED IN PART BY D-067 (five on the plate), D-131 (K5–K8 provisioned empty) and D-148 (K9 on the inner fender, not at the starter). The count of eleven stands.

**D-031** — Five dash buttons move to the CAN keypad — horn, parking brake sense,
glove box, hatch release, fuel-door release. Resolves the homeless-input problem
without consuming PMU pins.

**D-032** — Power and signal get **separate housings** on every leg. Three
reasons: terminal size (size 12 vs size 16 in one shell wastes cavities and
doubles tooling), noise (ladder references and the tach pickup must route apart
from motor legs), and service (diagnosing a switch should not break a 25 A
circuit).

**D-033** — Connector code scheme: `L<leg><class><index>` leg-side,
`DP-<code>` box-side. Class P = 12 AWG power, M = 14–16 AWG medium, S = signal.
Leg side is always socket (`06-xS`), box side always pin (`04-xP`), so a leg
cannot be plugged into the wrong half.

**D-034** — Series selection: **Deutsch DTP** (size 12) for all P, **Deutsch DT**
(size 16) for all M and low-count S, **TE AMPSEAL** for high-count S,
**Deutsch DTM** for the diagnostic and keypad drops only.

> SUPERSEDED BY D-052 and D-070 — no AMPSEAL anywhere; every housing is Deutsch DT/DTP/DTM.

**D-035** — 13 leg connectors total: L1 ×2, L2 ×4, L3 ×3, L4 ×4. L2 and L4 need
two DTP shells each because DTP is only manufactured in 2-way and 4-way and the
pop-up and window motors need six and four heavy conductors respectively.

> SUPERSEDED BY D-066, D-070 and D-171 — 15 leg housings (L1-S is two DT06-12S); the generated table in `../02-HARNESS/CONNECTORS.md` is the count.

**D-036** — The dash post carries 2 lugs (DP-BAT, DP-GND), the sealed PMU device
connector (DP-PMU), 2 DTM drops (DP-DIAG, DP-KEY) and 13 leg receptacles.

> SUPERSEDED BY D-070 and D-080 — 15 leg receptacles and four drops (DP-DIAG, DP-KEY, DP-ICU, DP-DCU).

**D-037** — The diagnostic port and keypad grounds are the **only** grounds
permitted to cross a leg connector, because both are box-adjacent devices with no
zone of their own. Every other ground terminates at a local star node.

**D-038** — **Retractable headlight switch (E-02) deleted.** Pop-ups raise
automatically when the A15 headlight ladder reaches HEAD and lower when it leaves
it. The only pop-up controls in the cabin are the **two momentary wink switches**,
one per side. Software owns pop-up position; wink is a momentary override that
returns the lamp to whatever state the ladder commands. Frees two L3-S cavities
and removes a switch from the dash.

**D-039** — **Radar detector added.** Control module and minimalist LED display in
the dash, front sensor wired locally to the module (does not cross a leg
connector), rear sensor at the hatch. The rear link runs L3-S → box → L4-S as a
pass-through; the PMU does not touch the signal. Power is switched off O10
through fuse F13. `L4-S` upsized DT06-6S → **DT06-8S** to carry it.

**D-040** — **No software gesture needed to park the lamps up.** Each retractor
motor has a **manual raise knob** on the unit itself. That covers maintenance
access and the raised-lamp look without a switch, a cavity, or a config entry.
This closes the only real objection to deleting E-02 (D-038).

**D-041** — SPEC bumped to **Rev B**. Rev A's connector section, gauges, relay
count and current estimates had all drifted from the working design. Rev B is
reconciled against `LOADS.md`, `legs/`, and the pinout doc.

**D-042** — C1–C7 moved to `99-ARCHIVE/2026-08_superseded-C1-C7-connector-scheme.md`
with a condensed record of why it existed and the three specific failures that
killed it. Archive entries keep reasoning, not tables.

**D-043** — Task IDs in `TASKS-CAMDEN.md` renumbered T-001…T-019 and reordered
easiest → hardest. Q/V/A IDs are **not** renumbered — they are cross-referenced
from DECISIONS and the leg files, and permanence is worth more than tidiness
there. Stale T-references in `LOADS.md` and the circuit files are noted at the
bottom of TASKS-CAMDEN.

**D-044** — Bulb-out detection confirmed viable on 7 A and 15 A channels
(0.1 A and 0.2 A measurement floors) but **not** on 25 A channels (0.5 A floor).
Consequence: buy brighter LED bulbs deliberately, and the case for inline load
resistors weakens to flash-rate only — which this device handles in software.

**D-045** — `[V-010 RESOLVED]` Connector geometry confirmed from the CAD and the
pinout device view. **3 rows × 13, numbered left→right top→bottom as viewed at
the device.** The logical map used throughout was correct. Cavity sizes are
**not** uniform: each row is 2 large · 9 small · 2 large. The twelve large
(2.8 mm) cavities are pins 1, 2, 12, 13, 14, 15, 25, 26, 27, 28, 38, 39 — the ten
25 A outputs plus GND plus +5 V. **This unblocks termination.**

**D-046** — Consequence of D-045: every 15 A and 7 A output sits in a 1.5 mm
cavity limited to 13–17 AWG. 14 AWG remains correct on O6–O11 but there is **no
headroom to go heavier**. Pin 15 (+5 V) needs a 2.8 mm terminal (211CC3S2120,
14–16 AWG) despite carrying a small signal.

**D-047** — `[Q-029]` **Bulb-out detection dropped entirely.** Manual check is
easy and it costs no pins or config. Consequence: the long-running LED open
decision collapses — **no load resistors anywhere**, since they were only ever
needed for detection thresholds or flash rate, and flash rate is set in software.
Also removes the reason to buy higher-draw LED bulbs.

**D-048** — `[Q-013]` **Cooled seats are in scope.** Adds fans and ducting to the
comfort bus. O15 load estimate rises; needs re-checking against the 25 A ceiling.

**D-049** — `[Q-022]` **Remote mirror motors kept, plus heated mirrors.** This
makes V-035 real: the door branch needs 8 motor conductors plus 2 heat, and the
current allocation does not cover it. Door branch must grow.

**D-050** — `[Q-021]` Seat belt warning and key reminder chime **dropped**.

**D-051** — `[Q-011]` Head unit is **double-DIN**. `[Q-016]` washer pump is
PMU-driven. `[Q-020]` flash-to-pass is software off the A15 ladder, no pin.
`[Q-023]` doors stay inside the REAR CABIN leg.

**D-052** — `[Q-027]` L3-S becomes **Deutsch DT-12s instead of AMPSEAL 35** —
cheaper, easier to source, and a failure takes out part of the dash rather than
all of it. **But 29 signals do not fit in two DT-12s (24).** Needs three DT-12s,
or two DT-12s plus a DT-6. See `legs/CONNECTORS.md`.

**D-053** — Ladder design principle: **no valid switch position uses a dead
short.** Every state goes to ground through a finite resistor, so 0 counts means
"shorted wire" and full-scale means "open wire" — fault detection for the cost of
one resistor per ladder. All six ladders calculated in `LADDERS.md`.

**D-054** — Resistors mount **at the switch**, not at the PMU. One return wire
per ladder instead of one per position, which is the entire reason for laddering.

**D-055** — The A16 key ladder is **not** a single-source ladder. ACC stays live
in RUN and both ACC and IG stay live in START, so each ignition switch output
feeds the shared node through its own resistor and the design targets the
*combinations*. Getting this wrong reads a false key position.

**D-056** — Wake network uses **1N5819 Schottky** diodes, not 1N4007. The lower
forward drop matters at cold-crank voltage. Plus a 10 kΩ bleed to ground, without
which diode leakage can hold pin 7 above threshold and the PMU never sleeps.

**D-057** — H-bridge relay pairs idle with **both motor legs grounded**, so a
de-energised bridge brakes the motor rather than letting it coast. Applies to
both pop-ups and both windows.

**D-058** — `[Q-032 provisional]` O15 comfort bus worst case is 17–26 A with
cooled seats added, which tops out over the 25 A channel. Resolved by **software
interlock** — heat and cool are mutually exclusive by definition — backed by
downstream branch fuses. No second channel needed. Awaiting confirmation.

**D-059** — PMU shipped **with the mating connector kit and the USB-to-CAN
adapter**. Closes V-018, removes $169 from the BOM, and fully unblocks Phase 2 —
the bench mule now needs only a plywood board, a spare housing and a Windows
machine.

**D-060** — Battery is a **Group 25 case, ~9.1 × 6.9 × 8.9 in, 14.6 lb, SAE
posts, integrated heater, Bluetooth BMS**. The heater is the reason this model
was correct for Fort Collins — lithium must not be charged below freezing, and
the heater warms the cells so it can. Its winter draw belongs in the sleeping
budget.

**D-061** — **Starter feed and PMU feed are separate runs from the battery**,
sharing only the distribution post. Cranking pulls 300–500 A briefly; routing
that through a Class-T sized for the 4 AWG PMU feed would blow it. The master
disconnect sits in the **PMU leg**, so killing it isolates the electrical system
while the starter cable stays passive.

> AMENDED BY D-091 — the separate runs stand; the PMU feed is 2 AWG, not 4.

**D-062** — Main protection is **Class-T, not ANL or MIDI**. LiFePO4 delivers
enormous short-circuit current and Class-T is the only common holder with the
interrupt rating to break it. Mounted as close to battery positive as physically
possible — the cable between post and fuse is the one length that can never be
protected.

**D-063** — Battery mounts on a **backing plate**, not through sheet metal alone.
A 15 lb mass with live terminals becomes a projectile in a crash; the plate turns
a tearing load into a shear load.

**D-064** — A **pull string goes into the tunnel alongside the 4 AWG main feed**
during Phase 3. The L4 harness follows the same route in Phase 5, and adding it
later means dropping the console again. Costs nothing now.

> AMENDED BY D-091 — the pull string stands; the feed beside it is 2 AWG.

---

## UPDATE 2026-08 — answers applied

**D-065** — `[Q-025]` **Window H-bridge relays K5–K8 move to the sill.** Dry,
accessible, short motor legs. This is the largest structural change since the
leg rebuild — see D-066 through D-069 for the cascade.

**D-066** — Cascade of D-065: **L4-P2 is deleted entirely.** The four 12 AWG
window motor legs no longer run the tunnel; only one 12 AWG motor-bus feed goes
back to the sill, and it fits in an existing L4-P1 spare cavity. Four 16 AWG
window commands replace four 12 AWG power legs in the tunnel.

**D-067** — Cascade of D-065: **the in-box relay count drops from 11 to 5.**
K1–K4 (pop-ups) and K11 (constant master) stay on the plate. K5–K8 live at the
sill, K9 at the inner fender, K10 in the engine bay on the factory A/C circuit.
Total is still 11 relays; only five are inside the box. Fuse F8/F9 (window branch
protection) move to the sill with the relays.

**D-068** — `[Q-031]` **The doors get their own connector pair at the sill.**
Combined with D-065, the sill becomes a real secondary node — relays, branch
fuses, a local ground, and two door connectors — not just a pass-through.
Documented in `legs/sill-node.md`.

**D-069** — `[Q-024]` **Pop-up relays stay in the box.** Confirmed no. The nose
is the wettest, hottest, most vibration-exposed part of the car, and it saves
four wires on a run built once.

**D-070** — `[Q-030]` L3-S is **2 × DT06-12S + 1 × DT06-8S** — 32 cavities,
29 used, 3 spare.

**D-071** — `[Q-019]` **Inhibitor switch laddered onto one input** on the L1-S
engine leg. Both functions — crank permission and reverse command — on one pin,
two resistors at the switch. Ladder values to be added to `LADDERS.md`.

**D-072** — `[Q-026]` **Horn gets a dedicated wake diode to pin 7.** Sixth input
on the wake network terminal strip, which was already specced for eight. The horn
now works with the PMU asleep, same as the hazard switch.

**D-073** — `[Q-032]` **Comfort bus management defers to the DCU/MCU**, alongside
the A/C controls, in the next stage. O15 stays a dumb 25 A feed from the PMU; the
DCU does the switching and the heat/cool interlock downstream, probably over CAN.
No PMU-side interlock needed, no second channel.

**D-074** — `[Q-012]` Seat products stay as **estimates** — 2 × 4 A heat elements,
2 × 1.5–2.5 A fans. Seats are not a priority and will be chosen against whatever
budget remains. Nothing downstream depends on the exact part.

---

**D-075** — **D-006 is SUPERSEDED.** The DCU and digital gauge cluster are in
full scope. Four existing decisions already depended on the DCU existing
(D-073 comfort switching, D-012 A/C migration, D-031 CAN wake, D-006 itself),
so it was load-bearing while nominally deferred. Full scope in `DCU-CLUSTER.md`.

**D-076** — **The PMU has no spare analog inputs.** All 16 are allocated. Water
temp, oil pressure, oil temperature, VSS and tach therefore cannot be read by the
PMU at all. **The DCU is their reader.** The L1-S sensor spares route through the
dash post to the DCU, not to the PMU. This is the structural reason the DCU is
mandatory rather than optional once a digital cluster is wanted.

> SUPERSEDED BY D-083 — the ICU, not the DCU, reads the engine sensors. The 'no spare PMU input' finding stands.

**D-077** — **Two nodes, not one: DCU and ICU.** The DCU owns climate, comfort
switching and sensor acquisition; the ICU owns the instrument display. Separate
because the cluster is safety-visible and climate control is not — a blend-door
firmware bug must never blank the tachometer.

> SUPERSEDED BY D-083 — sensor acquisition belongs to the ICU. The two-node split stands.

**D-078** — **Single source of truth per signal.** If the PMU measures it, the ICU
reads it from CAN — fuel level, battery voltage, key state, output currents. Only
signals the PMU physically cannot see get a dedicated DCU input. No duplicated
sensors, no disagreeing gauges.

**D-079** — CAN2 becomes a **five-node bus**: PMU, keypad, DCU, ICU, future LS
ECU. 120 Ω at exactly two points — PMU software termination at one end, a
physical resistor at the engine-bay drop at the other. **Fit the far-end resistor
now**, capped, so the bus is electrically correct before the ECU exists.

**D-080** — Two new dash-post connectors: **DP-DCU** (DT06-12S, 11 used) and
**DP-ICU** (DT06-6S, 5 used). Both modules mount inches from the post, so neither
involves a leg.

> SUPERSEDED BY D-083 — the sensor drop is DP-ICU (DT06-12S, 12 used); DP-DCU is the DT06-6S (5 used).

**D-081** — **The sequencing rule.** The car drives fully on the PMU with dumb
switches, the factory harness comes out, and the build completes — *then* the DCU
and ICU join. They add capability to a finished car and are never a dependency for
it starting, running, or being legal.

**D-082** — Tach signal gets **opto-isolation or a comparator** at the DCU. Coil
primary spikes run well above 12 V; landing it raw on an ADC destroys the input.
Closes the open half of V-041.

**D-083** — **CORRECTS D-076 and D-077.** Sensor acquisition moves from the DCU
to the **ICU**.

The original split gave the DCU sensor acquisition while claiming the ICU was
failure-isolated from it. That was self-contradictory — a DCU fault would have
left a lit, working cluster with no data to show. Isolation on paper, shared
dependency in fact.

**Corrected principle: a gauge's sender wires into the box that draws the gauge.**
Sender → ADC → pixel. No bus hop, no second processor, no shared failure domain.

| Node | Owns | Fails how |
|---|---|---|
| ICU | Display **+ tach, water temp, oil pressure, oil temp, VSS, alternator sense** | Cluster dark, nothing else affected |
| DCU | Climate, HVAC servos, comfort switching | Climate stops, **gauges keep working** |

**The property this buys:** if CAN2 fails completely, the ICU still shows tach,
water temp, oil pressure, oil temp and speed from its own inputs. Only fuel level
and battery voltage degrade, and neither strands you. The gauges you need while
driving have **zero bus dependency**.

Connector consequence: **DP-ICU becomes the DT06-12S** carrying all sensor
inputs; **DP-DCU shrinks to a DT06-6S** carrying only power, ground and CAN. The
L1-S sensor spares route to the ICU.

D-078 (single source of truth per signal) is unchanged and still governs — the
ICU reads fuel level and voltage from CAN rather than duplicating sensors.

**D-084** — **Teensy 4.1 for both DCU and ICU.** Same board in both boxes: one
toolchain, one library set, shared CAN and sensor code, and a spare that fits
either node. Overkill for the DCU at ~$32 — buy the overkill.

Selected for three CAN controllers on-chip (CAN1, CAN2, CAN-FD on CAN3), 18
analog inputs, hardware input-capture timers for tach and VSS, a microSD slot
that gives a datalogger for free, and mature CAN and display libraries.

**Known weakness:** not automotive-qualified, commercial temperature part.
Mitigated by mounting behind the dash face rather than against the windscreen,
and by **socketing the Teensy on the carrier PCB** so a heat casualty is a $32
swap rather than an assembly rebuild.

**D-085** — CAN transceivers are **TI TCAN1042 / TCAN1051**, automotive
variants. Chosen for the VIO pin (3.3 V logic, 5 V bus) and bus fault protection
well beyond ±12 V. Rejected: SN65HVD230 (3.3 V only, weak fault protection),
MCP2551 (5 V logic, needs shifting), MCP2515 (redundant controller).

**D-086** — Vehicle bus is **500 kbps, CAN 2.0B, 11-bit IDs**. The PMU is CAN 2.0
only, so the shared bus cannot be FD regardless of Teensy capability. 500 k is
tolerant of the run length and leaves large headroom for five nodes at 10–50 Hz.

**D-087** — **A second twisted pair runs between DCU and ICU, capped at both
ends.** Both Teensys have spare CAN controllers; this gives a private CAN-FD
channel later without touching the vehicle bus or redesigning a board. Two
conductors inside the dash — cheap now, impossible later. Same philosophy as the
capped LS reservations.

**D-088** — **Load-dump TVS on both module supplies is mandatory**, not optional.
An alternator disconnect can put 60 V+ on the rail, and it is the single most
common way a hobbyist microcontroller dies in a car. Full chain: reverse-polarity
protection → TVS → filter → automotive buck → Teensy's onboard 3.3 V.

**D-089** — Buy **three** Teensy 4.1, not two. A dead module mid-debug otherwise
stops the project for a week.

**D-090** — `[Q-043]` **No hardwired oil pressure lamp.** Oil pressure is shown
by the ICU only. Rationale: the car is a cruiser, not a track or commuter car,
and Camden won't drive it with doubts about its condition.

Two things that already reduce the exposure, both free:

- The **safe-mode render path** (§15) draws RPM, water temp, oil pressure and
  speed from hardcoded layout even if the SD config is missing or corrupt. The
  ICU has to fail completely, not just badly, to lose the gauge.
- **The factory cluster stays in place during ICU development** per Q-039, which
  keeps the factory oil pressure gauge live through the entire firmware phase —
  exactly the window when the ICU is least trustworthy.

Reopen this if the car's use changes — a track day or a long trip is a different
risk profile than a Sunday drive.

---

## UPDATE 2026-08 — round three answers

**D-091** — `[A-009]` **Main feed upgraded to 2 AWG.** Sized for the LS, not the
12A. ~$40 more now versus pulling the tunnel a second time later. Matches the
intent already expressed by the reserved LS channels and CAN drop.

**D-092** — `[Q-033]` **Door connectors are a single DT06-08S per door.** Window
motor legs drop to 14 AWG, which is ample sill-to-door. Halves the housing count.

**D-093** — `[Q-034]` **Mirrors: option B, independent wiring per side.** The
factory multiplexing switch is dead (V-036) and Camden wants **slightly larger
mirrors with integrated heat and digital controls.** New mirrors, new switch, no
reason to inherit the factory shared-bus scheme.

Conductor budget per door, and it lands exactly at 8:

| D1 / D2 cavity | Circuit |
|---|---|
| 1–2 | Window motor legs A, B (14 AWG) |
| 3 | Door pin |
| 4–6 | Mirror motor — common, X axis, Y axis |
| 7 | Mirror heat feed |
| 8 | Ground → **sill node** |

**D-094** — `[Q-035]` Two MCUs, DCU and ICU separate. `[Q-036]` CAN2 at
**500 kbps**. `[Q-039]` **Factory cluster stays in** through ICU development.

**D-095** — `[Q-038]` **Cigarette lighter deleted.** Frees 8–10 A on O10 and
removes the only load that could trip the channel powering the instruments.
USB-C covers the function.

**D-096** — `[V-048]` **Radar is a custom subsystem, not a commercial unit.**
DCU-managed, displayed on the cluster, with concealed sensors front and rear.
This changes it from a pass-through link to a designed subsystem — the front
sensor now needs conductors in **L2**, not just the rear in L4.

## Deletions confirmed by inspection — these simplify the build

**D-097** — Confirmed **gone and not returning**, removed from all specs and
spare lists:

| Item | Was | Now |
|---|---|---|
| Cruise control unit | V-023 | Gone, explicitly unwanted |
| Rear wiper and washer | V-027 | Gone |
| Power antenna | V-031 | Gone |
| Headlight cleaner | V-029 | Gone |
| All cold-start hardware — hot start relay/motor, sub-zero motor/sensor, choke, carb heater | V-025 | **Zero remain post-Weber** |
| Stop light checker | V-024 | Not carried into the new harness |
| Power mirror control | V-036 | Dead, replaced by D-093 |

**D-098** — `[V-034]` **The fuel-door solenoid never existed** — it is a new
addition, not a migration. **The hatch latch switch is broken** and needs
replacing. Both now have to be sourced, not just wired.

**D-099** — `[V-032]` A/C is **barely cool, probably low on charge.** Not an
electrical problem and out of scope for this project, but it belongs in
`known-issues.md` so it isn't rediscovered as a wiring fault.

**D-100** — `[V-013]` Deutsch DTP size-12 confirmed adequate for the 25 A legs.
`[V-049]` Both retractor manual raise knobs confirmed working — D-040 holds.

**D-101** — Bench kit **purchased**: UT210E clamp meter, 3 × Teensy 4.1 with
pins, SN65HVD230 5-pack, micro-B cables, 120 Ω and E24 resistors, breadboards,
jumpers, board materials, practice rotary switch. **Gate 0 closed. Phase 2A and
2B are fully unblocked** — nothing missing for either.

> SUPERSEDED BY D-140 — resistors, breadboards, jumpers, board materials and the rotary switch were not in fact bought; one cable, not several.

**D-102** — **Three Sicma housings on hand**, each with a full pin set: one from
the PMU box, two purchased spares. Allocated:

| # | Role |
|---|---|
| 1 | **The car.** Terminated once, never reopened (D-004) |
| 2 | **Bench mule.** Test pigtail, Checklist 2.3 |
| 3 | **Spare.** Untouched until something goes wrong |

Three is the right number — build, bench, and one mistake.

**D-103** — **Spare terminals deliberately not ordered** pending T-025. Counting
three full sets first avoids buying terminals that are already in a bag. Per
housing the requirement is 12 large (2.8 mm) + 27 small (1.5 mm).

> SUPERSEDED BY D-135 — the count is done: zero small spares. Spares are ordered under T-044.

**D-104** — Housekeeping: **T-016 (diagnose K-008) had been dropped** from the
open task list during an earlier rewrite. Restored. It is one of only two
irreversible-window tasks in the project — the other is T-014 — and losing it
would have meant losing the only chance to find the fault before the harness
comes out.

> SUPERSEDED BY D-105 — K-008 was traced from the factory diagram (`01-REFERENCE/factory-circuits/FAULT-K008-analysis.md`) and is not being fixed; T-016 is closed by that analysis.

**D-105** — `[K-008 / T-016]` **The blinker fault is not being fixed.** T-016 is
cancelled.

**Reasoning, and it's sound.** The fault is shared-ground modulation across two
factory body studs — X-13 (flasher + cluster + emission unit) and X-15 (rear
lamps + fuel pump). D-017 gives every zone a local star node with no ground
crossing a bulkhead, and every conductor, ground and connector in the new harness
is new. **There is no mechanism for it to transfer.** The old harness comes out
intact and goes in the bin.

**Observed severity bounds it further:** the fuel pump changes note with the
blinker, the engine does not. The pump sees voltage ripple but delivery stays
above the regulator setpoint, so nothing downstream notices.

**The one narrow case — already covered.** The fault dies with the harness, but
reused *components* don't. A marginal ignition switch IG contact would produce
the same symptom on the supply side, and that switch becomes the A16 ladder
input. **T-023 already continuity-tests it** for other reasons. PO splices at a
device end are already logged by **T-019**. No extra work needed.

**This supersedes the earlier position in D-104**, which called T-016 an
irreversible-window task alongside T-014. That was wrong: T-014 captures data
that can never be recovered, while T-016 diagnoses a fault that is being
discarded. Only T-014 is genuinely irreversible.

`FAULT-K008-analysis.md` is **kept as reference, not as a work item** — it
documents why the ground architecture is the way it is, and it is a worked
example of reading the factory diagram.

**D-106** — `[Q-041 closed on the design side]` **CAN byte layouts finalised.**
All messages 8 bytes, little-endian, 11-bit IDs, with byte 7 as a rolling counter
on every message so a receiver can detect a stalled sender rather than showing
stale data as live.

Explicit **timeout behaviour per message**, and the rule that a receiver **blanks
a field rather than holding the last value**. A gauge frozen at its last reading
is worse than one showing a fault.

Bus load computed at **~7.7 kbit/s against 500 kbit/s — about 1.5%.** Enormous
headroom even before the LS ECU joins. No reason to raise the bit rate.

**One item remains** — `[V-065]` the PMU's own message structure is fixed by
ECUMaster, not by us. Messages 0x100–0x130 are intent; they must be reconciled
against the actual CAN export read out of the client. 0x200–0x400 are ours and
are final.

**D-107** — **Custom tail lights.** Thin LED strip per side, stock aperture and
width, white reverse section inboard, red for tail/brake/turn.

**Design driver:** FMVSS 108 requires 50 cm² minimum effective projected luminous
lens area for a stop lamp or rear turn signal. A 1 cm strip across a 30 cm
aperture is 30 cm² — 40% short. **~2 cm clears it with margin** and still reads
as a thin strip.

Camden is not federally bound by FMVSS as an owner modifying his own car, and
Colorado only requires working lamps — but the standard is built to anyway, for
the liability position and because it is the engineering baseline for being seen.

**Wiring unchanged** — five conductors per side, already carried by L4-M.

**D-108** — Project reorganised into numbered folders: `01-DESIGN` `02-HARNESS`
`03-MODULES` `04-SUBSYSTEMS` `04-BUILD` `06-PROCUREMENT` `05-PROCESS`. Grouped by
**when you need it**, not by document type. `legs/` became `02-HARNESS/`.
Root holds only `README.md` and `STATUS.md`.

---

## ROUND FOUR ANSWERS — 2026-08

**D-109** — `[Q-042]` **IMU fitted to the ICU carrier board.** ~$5 and a few
traces while the PCB is being laid out. Enables g-meter, lap timing and a level
display. Adding it after the board exists means a new revision.

**D-110** — `[Q-044]` **Pop-ups stay.** Not deleted. K1–K4, the four heavy
conductors in `L2-P1`/`L2-P2`, ladder inputs A4 and A5, the wink switches and the
whole retract mechanism all remain as specified. **No change to the pin plan.**

The headlamp itself becomes a **shorter rectangular unit inside the existing
bucket.** See `04-SUBSYSTEMS/TAIL-LIGHTS.md` §8 for why this must be a
DOT-compliant sealed unit rather than a custom strip.

**D-111** — `[Q-046]` **Tail light driver PCB per housing.** Takes tail, brake,
turn and reverse as logic inputs; handles the intensity ratio, constant-current
drive and turn-override locally. No backfeed between O6 and O7, and the
sequencing does not depend on the PMU getting it right.

**D-112** — `[A-007]` **Converted from an assumption to a task.** The pop-up
limit ladder is not a decision — it is resolved by continuity testing. Gated on
**T-011**. `LADDERS.md` A4/A5 values stay provisional until then.

**D-113** — `[Q-045]` **Rear disc conversion is still planned.** The July 2026
drum overhaul was done because the car had to be driven to Fort Collins, and it
buys time for the axle swap. Not a reversal — an interim. The intent is a
thoroughly sorted rear axle and engine that then last.

## Verified from the TE catalogue — `TS-ICT-T-C-CAT-2018.pdf`

**D-114** — `[V-062 closed]` The reference PDF is the **TE Connectivity
Industrial & Commercial Transportation Terminals and Connectors catalogue,
2018**, 256 pages. DT family pages 109–132, common contacts 169–180, tooling
181–190, CAN section 195–207.

**D-115** — `[V-044 CONFIRMED]` **DTP is manufactured in 2-way and 4-way only.**
The catalogue's DTP series configurations list exactly `DTP0*-2*` (2 × size 12)
and `DTP0*-4*` (4 × size 12), and the ordering table lists only those two
positions. **L2 keeps two DTP shells.** There is no 6-way to collapse them into.

**D-116** — Wire sealing ranges confirmed from the catalogue:

| Contact size | Seals wire |
|---|---|
| 20 (DTM) | 14–22 AWG |
| **16 (DT)** | **14–20 AWG** |
| **12 (DTP)** | **10–14 AWG** |

Both design choices sit inside range: **16 AWG on DT** and **12 AWG on DTP**.

**Worth knowing:** D-092 puts the door window motor legs at 14 AWG in a
DT06-08S. Size 16 seals 14–20 AWG, so **14 AWG is at the very top of the seal
range** — it fits, but there is no margin above it.

**D-117** — **`C015` reduced-diameter seal modification exists** for wire with
thin insulation. If 16 AWG GXL seals loosely in a standard size-16 cavity, the
C015 variant is the fix. Available on most DT and DTP part numbers.

**D-118** — **BOM gap found: secondary wedgelocks are sold separately** and are
required components on every DT-family connector. They were not in the connector
BOM. Added — see `05-PROCESS/BOM.md`.

**D-119** — **The car migrates and drives on stock incandescent bulbs.** Nothing
in the pin plan, gauge selection or channel allocation assumes LED — the original
estimates were worst-case incandescent and the LED conversion only made them
smaller. Every lamp channel has 40–74% headroom on filament bulbs.

**Consequence for sequencing:** the custom tail lights (D-107) and the headlamp
change (D-110) become a **separate later project**, not a dependency of the
rewire. Same reasoning as D-081 — finish the car, then add.

**D-120** — **Inrush tolerance must be configured on every lamp channel** before
migration. A cold filament pulls 8–12× steady for a few milliseconds; a soft fuse
set flat at 5 A trips on the first flash. The PMU supports a current limit with a
time characteristic — use it. Belongs in Checklist 2.14 with the flash logic.

Turn signals are the case to get right, since they cycle constantly. After the
first flash the filament stays warm and inrush drops sharply, but the first one
is real.

**D-121** — **The stock dual-filament rear bulb is exactly what the two-channel
design wants.** O6 feeds the tail filament, O7 the brake filament, shared ground.
No backfeed, no diodes, no driver board.

The backfeed problem behind `[Q-046]` and D-111 exists **only** for the custom
single-array LED strip. It is not a general property of the design.

**D-122** — **Soft fuses must be re-set after any bulb change.** Values set
against incandescent are far too generous for LED — a tail circuit set at 6 A
does not protect a 3 A LED load. Re-run the measure-and-set step on every lamp
circuit and log it as a second pass in `MIGRATION-LOG.md`.

---

**D-123** — **Lighting split into its own project.** `02-PROJECTS/lighting-body/`.

> AMENDED BY D-201 — the split is reversed 2026-08-31; lighting returns as deferred second-pass scope inside this project.

Custom tail lights, the headlamp change, and the full LED bulb conversion are
**out of the electrical rebuild's scope.** It was creeping onto the critical path
and adding fabrication, cost and open questions to something already at 500+
hours — and D-119 established that none of it is needed: the car migrates,
drives and shakes down on stock incandescent bulbs with 40–74% headroom on every
lamp channel.

It is a **bodywork and fabrication project that happens to involve wiring.**

**Moved out:** D-107 tail light design · D-110 headlamp unit · D-111 driver PCB ·
`[Q-048]` · `[V-063]` `[V-064]` `[V-066]` · ~$345–835 of BOM.

**Stayed in:** everything about how power reaches a lamp — channel allocation,
wire gauge, connectors, flash logic, soft fuses, and D-120 inrush configuration.
The electrical project delivers working lamp circuits with stock bulbs on them.

**Hard prerequisite for the lighting project:** electrical Phases 6, 7 and 8
complete, factory harness out, car driving on the PMU.

**D-124** — **The electrical project's lighting baseline is stock incandescent.**
Not LED. All estimates in `LOADS.md`, all soft-fuse starting points, and all
migration steps assume filament bulbs.

This reverses the working assumption carried since Rev A. The LED figures stay in
`LOADS.md` as a **future reference column**, clearly marked as belonging to the
lighting project, because they'll be needed for the second-pass fuse reset
(D-122).

**Note:** D-047 dropping bulb-out detection still holds and is unaffected. That
decision made incandescent *easier*, since filament draw was the one thing
detection thresholds would have complicated.

---

**D-125** — Four more faults found 2026-08: **defrost switch broken (K-020),
headlamp retractor switch broken (K-021), washer pump not working (K-022),
blower motor not working (K-023).**

**Three of the four cost nothing in redesign** — the defrost switch moves to the
CAN keypad, the retractor switch is deleted by D-038, and the blower was already
a death-date item. What they cost is **measurement access**: you cannot measure a
circuit by operating a switch that doesn't work.

**Workarounds, all in `04-BUILD/METER-SESSION.md` Part 3:**

| Fault | Workaround |
|---|---|
| Defog switch | Jumper Y to LG at the switch connector with a fused lead |
| Retractor switch | Drive the pop-up motors directly with fused 12 V. **Continuity-test the motor first** (T-011) to identify drive vs limit pins — backfeeding a limit switch can damage it |
| Washer pump | Diagnose before measuring — pump, wiring or switch |
| Blower motor | **Cannot be measured.** Size O16 from the replacement's spec |

**D-126** — **O16 blower sizing comes from the replacement part's spec sheet, not
from measurement.** The motor is dead. The channel stays 25 A with the integrated
flyback diode, which covers any plausible replacement, and the soft fuse gets set
at migration from whatever is actually fitted.

**D-127** — **The pop-up measurement and the limit-switch continuity test are one
job.** T-011 identifies which of WR/YG/R/RY are drive versus internal limits;
T-015 then drives the motor on those pins to read running and stall current.
Doing them separately means opening the same connector twice, and guessing at the
pinout risks the limit switches.

**Battery disconnected for the continuity test. Fused lead for the drive test.**

---

**D-128** — `[Q-053]` **Path 1: a CarPlay head unit.** The Pi minimap is not
being pursued.

**Reasoning:** the feature exists today, for $200–400, with zero development.
Paths 2 and 3 were 60–120 hours of firmware on top of a project already at
500–900, to produce something similar but offline. The offline advantage is real
and so is the aesthetic gain, but neither justifies the schedule risk of adding a
second display subsystem to the critical path.

**This also closes:**

| ID | Now |
|---|---|
| `[Q-050]` | Moot — the map picture is wanted, and the head unit provides it |
| `[Q-051]` | **Head unit stays.** Not deleted |
| `[Q-052]` | Moot — no Pi display to site |
| `[Q-054]` | Moot — no renderer to choose |
| `[Q-049]` | **Moot — no Bluetooth module needed.** The head unit handles audio |

**D-129** — **Audio is the head unit's job.** The hidden Bluetooth A2DP module
from `INFOTAINMENT.md` §1 is not needed. The head unit takes the iPhone, drives
the amp, and provides the few controls wanted.

**Reverts to the original plan:** double-DIN head unit (D-051), switched feed on
O10 via `L3-M 1`, fused constant keep-alive on `L3-M 2` off busbar F1. **No
wiring change** — that allocation was never removed.

**D-130** — **The ICU keeps gauges only.** No map, no turn-by-turn strip, no BLE
module. It stays what D-083 made it: display plus engine sensor acquisition, in
one failure domain, with zero dependency on anything else.

This is the version of the cluster that was already designed. Nothing to redo.

## What this preserves

| | |
|---|---|
| No Pi, no Linux in the car | Nothing safety-visible depends on an OS booting |
| No second display subsystem | One cluster, one head unit |
| No GPS module, no map data, no shutdown circuit | ~$140–385 not spent |
| ICU scope unchanged | Firmware estimate holds at 155–325 hrs |

## The trade being accepted

**A bright modern screen in a 1982 dash**, and a map that needs cell signal.
Both were considered and accepted.

`[Q-055]` — head unit selection. Worth choosing for: **wireless CarPlay**
(no cable to the phone), physical volume knob, and a bezel/finish that can be
integrated rather than obviously aftermarket. Double-DIN aperture already planned.

---

**D-131** — **The windows are MANUAL.** This car has no power window motors,
switches, regulators or wiring. The factory diagram's I-06, I-07, I-09 and I-11
describe an option this car doesn't have.

**Power windows are a deferred luxury item**, to be added later alongside heated
seats and the rest when budget allows.

## What changes now

**Nothing gets deleted. Everything gets capped.** This is exactly the case D-004
exists for — terminate every cavity now, cap the spares, and adding the feature
later is uncapping a wire rather than pulling a door and a sill.

| Item | Was | Now |
|---|---|---|
| K5–K8 window H-bridges | Populated at the sill | **Sockets fitted, relays not populated** |
| F8, F9 branch fuses | Fitted | **Positions provisioned, fuses not fitted** |
| `L4-P` cav 3 — motor bus feed to sill | Live | **Terminated and capped** |
| `L4-M` cav 9–12 — window commands | Live | **Terminated and capped** |
| `D1`/`D2` cav 1–2 — motor legs | Live | **Terminated and capped in the door** |
| `L3-S` ×4 — window switch inputs | Live | **Terminated and capped at the switch panel** |
| O1 motor bus | Pop-ups + windows | **Pop-ups only** for now |

**Wire is still run, still terminated, still in the door.** Adding motors later
is: fit the regulators, plug in, populate four relays, fit two fuses, enable the
logic. **No harness work.**

**D-132** — **The sill node shrinks but stays.** Even with no window motors it
still carries the door connectors D1/D2, the local ground stud for door returns,
and the mirror heat branch. The relay sockets and fuse positions are built now
and left empty.

Building the plate with empty sockets costs a few dollars. Adding a plate behind
a trim panel on a finished car costs an afternoon.

**D-133** — **O1 motor bus is pop-ups only for now.** Worst case drops from
~15 A steady / 40 A transient to roughly **8–12 A steady, 25–50 A transient** for
two pop-up motors. The 25 A channel and its flyback diode are unchanged — sized
for the eventual full load, not today's.

**No soft-fuse benefit to claim.** Set it for pop-ups at migration; raise it when
windows arrive.

---

**D-134** — **PMU-24 DL received. Connector cavity layout CONFIRMED in the hand.**
`[T-020 closed]`

The supplied housing has **12 large cavities and 27 small** — exactly matching
SPEC §11 and the CAD-derived map (D-045). The largest cavities sit **farthest
out** in each row, confirming the **2 large · 9 small · 2 large** per-row pattern.

**The pin plan is buildable as drawn.** This was the last physical unknown.

**D-135** — **Terminal stock counted** `[T-025 closed]`.

| Size | Marking | Supplied | Needed per housing | Spare |
|---|---|---|---|---|
| Large 2.8 mm | `FCI` | 16 | 12 | **4** |
| Small 1.5 mm | `FCI 125` | 27 | 27 | **0** |

**Zero spare small terminals.** With two more housings inbound at presumably the
same count, the totals become 81 small for 3 housings needing 81 — still zero
margin.

**Order spare 1.5 mm terminals (211CC2S2160P) before Phase 4.** D-103 estimated
~15; that is now a firm requirement, not a hypothetical. You will ruin some
learning to crimp, and a ruined terminal with no spare stops the build.

**D-136** — **Physical orientation reference recorded.** With the PMU sitting
flat and upright, connector face toward the viewer, **the purple lock is on the
right-hand side.**

> **This does NOT yet establish where pin 1 is.** The housing is symmetrical in
> cavity pattern, so the lock position is the only asymmetric feature — but which
> end of row 1 is pin 1 relative to that lock is **still unverified**.
>
> Getting this wrong mirrors all 39 wires. It is the single most expensive
> mistake available in this project. Logged as `[V-068]`, and it must be closed
> by positive identification, not inference.

**D-137** — Spare housings ordered from ECUmaster are expected to carry the same
terminal counts (16 large, 27 small). **Verify on arrival** rather than assume —
if they ship housing-only, the small-terminal shortfall is worse than it looks.

---

**D-138** — `[V-068 provisionally answered]` **Pin 1 is top-left**, in the top
row at the end **furthest from the purple lock**, viewed with the PMU flat and
upright and the connector face toward the viewer. Lock on the right, pin 1 on the
left.

Row 1 = pins 1–13 · row 2 = 14–26 · row 3 = 27–39, numbering left→right,
top→bottom. This matches the ECUmaster device view.

**Held as provisional, not closed**, until one positive test. The device view
establishes numbering but does not show the lock, so aligning drawing to physical
part relies on both being viewed from the same face. Very likely correct — and
exactly the assumption that, if wrong, mirrors all 39 wires without being
discovered until the housing is sealed.

**Confirmation, five minutes, once the PMU is on the bench:** force O2 (pin 39)
high in the client and meter the bottom-right cavity. 12 V confirms the entire
map. Then mark the housing (T-043).

**This is not scepticism about Camden's reading.** It is that D-004 makes the
39-pin a one-shot assembly — the cost of being wrong is a housing, a full
re-terminate and a weekend, against five minutes of confirmation.

> SUPERSEDED BY D-139 — pin 1 position confirmed on the physical part.

---

**D-139** — `[V-068 CLOSED]` **Connector orientation confirmed** by visual
comparison of the physical part against the ECUmaster manual. Positive
identification, not inference.

**Pin 1 is top-left**, top row, end furthest from the purple lock, with the PMU
flat and upright and the connector face toward the viewer. Lock on the right.
Row 1 = 1–13, row 2 = 14–26, row 3 = 27–39, left→right, top→bottom.

**This was the last physical unknown blocking Phase 4.** Every one of the 39
cavities now has a confirmed position, a confirmed size, and an allocated
circuit. Supersedes D-138's provisional status.

Remaining before the real housing is terminated: spare 1.5 mm terminals (T-044)
and the housing mark (T-043).

---

**D-140** — **Inventory correction.** These were previously recorded as purchased
and are **not in hand**: 120 Ω resistors, E24 resistor assortment, breadboards,
Dupont jumpers, plywood/ground bus/fuse holder, scrap rotary switch.

**Actually in hand:** 3 × Teensy 4.1, 5 × SN65HVD230, one micro-USB cable,
UT210E clamp meter, PMU-24 DL with connector and 39 terminals, 2 spare housings
inbound.

**D-141** — **The full plywood bench mule is dropped.** Reduced to a
current-limited PSU, the laptop, one bulb, a few switches and flying leads.
**~$140 saved.**

**Reasoning, and it corrects an overstatement of mine:**

"Learn the software with nothing at stake" was presented as the bench's main
value. But **nothing at stake is already true in the car** — that is exactly what
the parallel-system architecture provides (D-023). Every circuit stays on the
factory harness until its own cutover.

**The pin plan is not a bench output.** Channel allocation, gauge, ladder values
and connector assignments are fixed by design and by the factory decode. No bench
result changes any of them. The bench is a **learning exercise, not a design
input** — I framed it as more.

**And Checklist 6.3–6.4 already provide a safe config environment in the car**:
power up with all outputs disabled, validate the entire input layer before a
single load is connected.

**What survives the cut, and why:**

| Kept | Reason |
|---|---|
| **Current-limited PSU** | Checklist 2.9 deliberately shorts an output. Doing that first on vehicle wiring is a different proposition |
| 120 Ω × 4 | CAN1 has no internal termination — it will not connect without them |
| One bulb, a few switches, flying leads | Enough to exercise real logic |

**Dropped:** plywood board, mounted ground bus, and the 15-way test pigtail. The
pigtail alone would consume **15 of 27 small terminals with zero spares** — it
was a supply blocker for a convenience.

**D-142** — **Ladder ADC verification moves from bench to car**, during Phase 6,
when the switches are genuinely wired. That is when real resistances and real ADC
readings exist, and it removes a category of bench-to-car translation error.
E24 assortment and practice switch defer accordingly.

**D-143** — **One bench item is non-negotiable: deliberately short an output and
watch the soft fuse trip and retry** (Checklist 2.9).

It is the single behaviour that distinguishes this device from a fuse box, you
need to recognise it before it happens unexpectedly at speed, and it is genuinely
unpleasant to meet for the first time on vehicle wiring. A current-limited supply
makes it a five-minute experiment.

> AMENDED BY D-144 and D-145 — no bench PSU; a 5 A fuse in the feed stands in. The deliberate short itself stays and is `CHECKLIST.md` 2.8 on the desk, or 6.3 in the car.

---

**D-144** — **No bench power supply. Supersedes D-143.**

Camden challenged why the soft-fuse test needs a bench. It doesn't, and my
reasoning conflated two different things.

**The soft-fuse test moves to the car.** Panel installed, all outputs disabled,
set one channel's limit to **2 A**, enable only that channel, touch its bulkhead
pin to ground. The PMU is built for exactly this — solid-state per-channel
limiting is the product, it opens in milliseconds, and it isn't damaged by doing
its job. With a low limit the event is undramatic.

**What the PSU was actually protecting against was the first power-up of a
hand-built panel** — a pinched wire against the backer plate, a terminal one
cavity out, a busbar stud touching something. That is a **single moment**, not an
ongoing need.

**D-145** — **The $2 replacement: a 5 A fuse in the main feed for first
power-up.** Enough for the PMU to boot and talk over CAN; anything shorted blows
a 5 A fuse instead of melting 2 AWG. Verify, step to 15 A, verify, then fit the
Class-T for real operation.

Same protection as a current-limited supply, for the one moment it matters.

**D-146** — **Checklist 4.21–4.23 powered panel verification is dropped.**
Replaced by **4.18 continuity testing**, which needs no power at all and catches
wrong cavity, missed crimp, swapped pair and short-to-plate — the overwhelming
majority of build errors. Powered verification happens in the car at Checklist
6.3, where it was already scheduled.

**D-147** — Bench kit final: **~$110–165.** No PSU, no plywood, no pigtail, no
speculative test loads. Down from ~$300, and the terminal-supply blocker is gone
because the 15-way pigtail no longer exists.

**The pattern worth noting across D-141, D-144 and this one:** the bench kept
being justified by risks the parallel-system architecture had already eliminated.
Each time it was examined, less of it survived.

---

**D-148** — `[A-005]` **Start relay K9 mounts high on the inner fender or
firewall**, not at the starter. The relay keeps solenoid current off the PMU; it
does not need to be adjacent. Pull-in is 15–25 A and 12 AWG over three or four
feet loses almost nothing. Dry side, reachable, no ingress rating required.

**D-149** — `[Q-055]` **Head unit selection criteria set:**

| Requirement | Note |
|---|---|
| Double-DIN | Aperture already in the dash plan |
| **Physical buttons**, not touch-only | |
| **Variable LED button colour — set to green** | Matches the illumination scheme |
| **Wireless CarPlay** | No cable to the phone |
| **Full passthrough — critical** | Pre-outs, full-range, feeding the external amp. Not speaker-level, not relying on the head unit's internal amplifier |

**Passthrough is the hard requirement.** Many units advertise pre-outs but
band-limit them or apply fixed EQ. Confirm the signal reaching the amp is
full-range and unprocessed.

**D-150** — `[Q-037]` **Cluster is ONE WIDE DISPLAY.** Not two round TFTs.

**Hardware consequence — this is not a neutral choice.** A wide panel at
800×480 cannot be driven by plain SPI at a usable frame rate; a full redraw is
far too slow. Two options:

| Approach | Note |
|---|---|
| **Display controller with its own framebuffer** — RA8875 / RA8876 | SPI carries *commands*, not pixels. The controller holds the image. **Simplest path** |
| **Parallel interface** driven by the Teensy's FlexIO | Faster, more pins, more work |

**Recommended: a controller-based panel.** It removes the bandwidth problem
rather than engineering around it, and the Teensy 4.1 has ample headroom for
everything else the ICU does.

**Also decided by this:** one bezel aperture instead of two round openings, which
is easier to fabricate and seal.

`[V-058]` still applies — **800–1000 nits minimum.** A wide panel makes sunlight
readability more important, not less, because there is more area to wash out.

> SUPERSEDED IN PART BY D-168 — one wide display stands; the controller-panel recommendation does not. SPI with dirty-rectangle rendering from a RAM framebuffer is built and proven.

---

## CLUSTER IMPLEMENTATION — 2026-08

*These were all decided while building the ICU firmware and existed only in
`cluster_core.h`. Recorded here so the reasoning survives the code.*

**D-151** — **Emerald `#009155` is the single lit colour.** RGB332 `0x11`.

RGB332 gives 8 red levels, 8 green, only **4 blue** — and blue is what separates
emerald from plain green. `b=1` (85) is the one usable step.

**Every lit element is this exact shade**: labels, bar segments, all digits, the
compass suffix, the pitch angle, the G dot. `C_BRIGHT` and `C_GREEN` are both
defined as `C_MID`, so nothing can render lighter than anything else by
accident.

**Unlit is `0x04`, RGB(0, 36, 0)** — a 4:1 ratio against lit, so an unlit
segment reads as *off* rather than as a dim reading.

Dark tones drop blue to zero: at low luminance a fixed 85 blue dominates and the
hue turns teal.

**D-152** — **Imperial at the display layer only.** `VehicleState` stores metric
— °C, centibar — and `cluster_core.h` converts to °F and PSI when drawing.

**The CAN map, `stats.h` and every log therefore stay metric.** A metric display
mode is one flag away, and stored data never needs reinterpreting. Converting at
the sensor would have contaminated everything downstream.

**D-153** — **A missing sensor must never render as a real zero.**
`SensorStatus` accompanies every reading:

| State | Renders as |
|---|---|
| `SENSOR_OPEN` | **Amber dashes**, bar becomes a hollow outline |
| `SENSOR_SHORT` | **Red dashes**, hollow outline |
| `SENSOR_STALE` | Dim green dashes — CAN stopped, not a hardware fault |
| `SENSOR_RANGE` | Red — plausible but physically impossible |

Detection is free on resistive senders: a bounded ohm range means the extremes
are unambiguously faults. **Same principle as the resistor ladders (D-053).**

Zero oil pressure and a disconnected oil pressure sender are completely
different situations. A gauge that renders them identically is worse than no
gauge.

**D-154** — **Bar segments are contiguous, gap 0.** Segment widths grew to hold
the same span. Reads as a solid growing bar rather than a row of tiles.

**D-155** — **Symbols, not words, for the gauge column.** Thermometer, oil can,
oil can, fuel pump, battery — **and the unit distinguishes the two oils.**
`PSI` versus `F` is a stronger distinction than two similar silhouettes would be.

The oil can is a **side view** — handle left, body centre, spout rising right —
matching the warning-lamp symbol used since the 1960s. An earlier top-down
version was unreadable.

Icons reuse across the gauge column and the tell-tale row deliberately: the
thermometer means temperature in both places.

**D-156** — **Four named axes in the gauge column**, everything derives from
them: icon left edge 418, value centre 492, unit centre 544, bar 572–782. Values
and units are *centred*, not left-aligned, so `63` and `190`, `F` and `PSI`
share a vertical axis.

Each row computes one horizontal axis, `cy = row_y + BAR_SH/2`, and the icon,
value and unit all derive from it. Previously each had a hand-tuned offset that
happened to agree.

**D-157** — **The left column is THREE items, not four.** The G value is the
circle's label and stays tucked under it with its own small gap; the group
spaces as one unit against the compass and pitch.

Spacing is by **edge gap, not centre** — the G circle is 100 px tall against 30
for a readout, so even centre spacing looks wrong.

**D-158** — **Digit fields centre by repositioning slots.** `setCentre()` counts
significant digits, wipes the old footprint and re-lays the slots so a value
stays centred under its label as it crosses 10 and 100. Fields that show every
digit always occupy all N slots.

**D-159** — `[I-64]` **The display does NOT cross the harness.** It connects
directly to the Teensy inside the dash, on a short ribbon or flying leads.

`DP-ICU` is a DT06-12S carrying **power, ground, CAN2, illumination reference
and six engine sensor inputs — 11 conductors.** A panel needs SPI or parallel
data plus backlight power, which is well beyond that.

**Why this is the right split:** the display and the Teensy are inches apart
behind the same bezel and are removed together as one assembly. Routing a
high-speed SPI bus through a harness connector would add noise, cost cavities
and gain nothing.

**Consequence:** `DP-ICU` is correctly sized as-is. Anyone later reading the
cavity count must not conclude the display was forgotten.

**D-160** — `[I-65]` **`stats.h` thresholds recorded and flagged.**

| Constant | Value | Basis |
|---|---|---|
| `REDLINE_RPM` | 7000 | **Drives the tach red zone.** 12A redline `[V-070]` — confirm against the FSM |
| `HOT_WATER_C` | 105 | Above normal thermostat range, below boiling at pressure |
| `LOW_OIL_CBAR` | 100 (1.0 bar) | Rotaries want more than a piston engine at idle `[V-071]` |
| `RUNNING_RPM` | 400 | Above cranking, below idle |
| `COLD_START_C` | 40 | Below operating temperature |
| `TANK_GAL_X10` | 159 (15.9 gal) | FB nominal ~60 L `[V-072]` confirm |

**The redline figure matters most** — it sets `RPM_RED` on the tach and the
`revSeconds` accumulator. Getting it wrong means either a red zone that arrives
early or one that never warns.

**D-161** — `[I-68]` **IMU specified.** MPU-6050 or ICM-20948 class, I²C, on the
ICU carrier board (D-109).

**Orientation convention, which must be written down or it will be guessed
wrong:**

| Axis | Positive direction |
|---|---|
| Lateral `latGx100` | **Right** — turning left throws the dot right |
| Longitudinal `lonGx100` | **Acceleration.** Braking is negative |
| Pitch `pitchDeg` | **Nose up** — climbing positive, descending negative |

Full scale is ±1.0 g on the G circle and ±45° on pitch.

`[V-073]` — mounting orientation on the PCB must match, or every axis needs a
sign flip in firmware. Decide the board orientation before the PCB is laid out.

**D-162** — `[I-66]` **`stats.h` is volatile-only for now.** The `life[]`
accumulator is declared but nothing reads or writes SD yet. It resets at power
off.

Persistence needs the SD work in Stage 6 and a decision about write frequency —
writing every second wears the card; writing only at shutdown loses data on a
power cut. **Probable answer: write on key-off via the PMU's shutdown delay,
which already exists for exactly this kind of purpose (D-054).**

**D-163** — `[I-67]` **`stats.h` owns the automated figures; `LOGS.md` owns the
manual ones.** Max speed, max RPM, runtime, distance and peaks come from the
firmware. Config versions, firmware versions, the photo index and the session
log stay hand-written — nothing can generate those.

**D-164** — **The channel schedule is the measured-to-configured pipeline.**
`01-DESIGN/CHANNEL-SCHEDULE.md` holds one row per channel with an empty
**MEASURED** column. Filling it drives everything downstream: soft-fuse values,
the PMU config, `channels.h`, the simulator and the diagnostics page.

**Soft-fuse rule, by load type:**

| Type | Limit |
|---|---|
| Motors | measured **stall** × 1.10 |
| Filament lamps | measured steady × 1.35, **plus an inrush window** |
| Resistive (defog) | measured **cold** × 1.20 |
| Electronics | measured steady × 1.50 |
| **Unmeasured** | **output stays DISABLED** |

Round up to the nearest 0.5 A.

**The limit protects the wire, not the load.** A 14 AWG circuit carries far more
than any of these figures — the soft fuse exists to catch a short or a seizing
motor, not to police normal operation.

**D-165** — **An output with no measured figure stays disabled.** A guessed limit
is worse than an output that is off: it either nuisance-trips at the worst
moment or fails to protect at all, and in both cases it looks configured.

Three of 24 are measured today: **O7 brake 7.0 A, O17/O18 turn 3.4 A per side.**

**D-166** — **The entire PMU logic is enterable without any amp figures.**
Channel naming, all eight ladder decode tables, every output expression, the
interlocks, the wake network, flasher, wiper timing and pop-up logic have no
dependency on measurement.

**Consequence for sequencing:** Phase 2A splits cleanly. Steps 1–7 — the whole
vehicle logic — can be entered the day the PMU is on a desk. Soft-fuse limits
and output enabling happen per channel as each measurement arrives, which means
migration is never blocked waiting on the config.

**D-167** — **A 100 kΩ bias resistor from +5 V on A15 and A16.** These are the
12 V-side ladders, where OFF reads 0 counts — identical to a disconnected wire.
The bias lifts OFF to ~100 counts so the two are distinguishable.

Same principle as D-053: no valid state may sit at an extreme, because the
extremes are how faults announce themselves.

---

## AUDIT 4 — 2026-08-30

*Recorded while implementing `AUDITS.md` Audit 4. Each one either closes an
open ID or records a choice that previously lived only in a code comment or a
generated table.*

**D-168** — `[I-117]` **The cluster display is driven over SPI with
dirty-rectangle rendering from a 384 KB RGB332 framebuffer in the Teensy's
RAM.** Built and proven in `cluster_core.h`; only changed 16 × 16 tiles cross
the wire, a realistic frame is 2–5 ms, and the 415-assertion suite checks the
tile logic. Supersedes D-150's recommendation of a controller-based panel
(RA8875/76), which stays the fallback if a large analogue sweep is ever wanted.
`Q-060` selects the panel against this interface.

**D-169** — `[Q-058]` **Cluster pages cycle from a small dedicated momentary
button mounted by the display.** Camden's answer. Wired directly to the
Teensy, so it does not cross the harness (D-159) and DP-ICU stays at twelve.

**D-170** — `[Q-059]` **Fit 8 MB PSRAM to the Teensy 4.1 pads before the ICU
board is installed.** ~$8, and much easier on the bench than in the dash. Not
needed for the framebuffer, which fits in RAM; buys double-buffering and
logging headroom later.

**D-171** — **L1-S is two DT06-12S housings, L1-S1 and L1-S2, allocated as
`02-HARNESS/data/connectors.csv` generates them.** L1-S1: O21 start, the six
ICU engine sensors passing through the post to DP-ICU, +5 V, CAN2 pair, the
inhibitor (no pin until `Q-063`) and the capped wideband tap. L1-S2: brake
fluid level to DP-ICU 12 (`A-010`), coolant and oil level capped, three LS
spares. Replaces the three conflicting L1-S lists in the old PIN-MAP,
CONNECTORS and engine.md. 15 leg housings, 24 mated pairs.

**D-172** — **L3-S is allocated as generated: L3-S1 (ladders and switch
inputs), L3-S2 (wake sources, provisioned window commands, deferred radar
power), L3-S3 (deferred radar link and spares).** Every cavity carries a
status word from `SPEC.md` §12 — LIVE, PROVISIONED or DEFERRED — so a capped
wire is never mistaken for a spare. Replaces the D-070 cavity split, whose
count (2 × 12 + 8 = 32) stands.

**D-173** — **Fuel pump soft fuse 4.0 A: measured steady 2.38 A × 1.5,
electronics-style, because an in-line pump offers no practical stall reading.**
D-164's motor rule wants stall × 1.10, but dead-heading the Carter mid-campaign
risks more than it teaches. 4.0 A still catches a short or a seized pump, and
the value is re-set from the Aeromotive 340's spec at that swap (`V-040`).

**D-174** — `[Q-066]` **Suspect and unmeasured LIVE channels get INTERIM soft
fuses from healthy-expected values; the PMU's own per-channel telemetry on the
new harness is the real measurement, and its gap against healthy-expected is
the replacement list.** Camden's call. The degrading factory wiring makes
clamp readings through sick circuits unreliable — a slow wiper at low current
cannot be split into wiring drop vs a dying motor by current alone. The fuse
protects the wire, so a healthy-class value is safe protection. Interim
values, marked INTERIM in the CSV, re-set from telemetry in the first week
after migration: O1 25.0 (cap) · O2 4.5 · O3 5.5 · O8/O9 15.0 (cap) ·
O10 12.0 · O11 10.0 · O12 9.0 · O19 5.5 · O20 3.5 · O21/O22 0.5. Measured
figures stand (O5 O6 O7 O17 O18). Still to do on the old harness — only what
it alone can give: parasitic draw, defog cold (O4), voltage-drop tests,
continuity and ladder items, pop-up limit ID. Closes V-076, V-078, V-079,
V-080 (redos no longer required); V-021 and V-019 now resolve from telemetry;
V-077 (alternator health) stays open. Supersedes D-165's unmeasured-stays-
disabled rule for these channels; D-164's measured rule resumes per channel as
telemetry arrives.

> AMENDED BY D-175 — interim values raised to channel caps; the
> telemetry-first principle, closures and campaign scope stand.

**D-175** — `[Q-067]` **Every non-measured LIVE channel's soft fuse sits at
its channel cap — pure wire protection — until PMU telemetry on the new
harness supplies the real figure; then D-164 tightening applies per channel.**
Camden's call, amending D-174's healthy-expected interim values. Consequence,
accepted knowingly: soft fuses discriminate nothing during shakedown — a
partial fault (a seizing motor, a chafed strand) draws below the cap and shows
only in telemetry. **The protection burden moves entirely to harness design
and build verification:** continuity-test every conductor pin to pin, verify
every cavity against PIN-MAP.md before first power, and watch telemetry at
every cutover and through the first week. Caps set: O1 O2 O3 O4 O12 = 25.0 ·
O8 O9 O10 O11 = 15.0 · O19 O20 O21 O22 = 7.0. Measured channels keep their
values (O5 4.0 · O6 7.5 · O7 9.5 · O17/O18 4.5). O4's cold figure now comes
from telemetry on any cold morning. O13/O14 stay disabled (reserved), O15
until its loads exist, O16 until the replacement blower.

**D-176** — **Part replacement is a separate post-PMU project; the washer-pump
diagnosis and the volt-drop replace-or-keep tests leave the measurement
campaign.** Camden's call: parts get replaced after the PMU is in, when it is
as easy as installing a new part — not clutter inside the wiring project.
Underperformers are identified by PMU telemetry against healthy-expected draw
(D-174). METER-SESSION.md rewritten (explicit rewrite request) to hold only
the remaining work: parasitic, the `V-077` volt check, `T-011` pop-up limits,
`V-050` ignition continuity, `V-037` sender, door pins. Prior sittings'
procedure text lives in git history; the figures live in the CSV.

**D-177** — `[V-030, T-011]` **The pop-up motor pinout comes from FSM sheet E
(headlights & illumination), not a continuity session.** Camden's call: verify
off the official diagram. From the sheet: E-03 (LH) and E-04 (RH) are the
same 4-way — **YG top · WR left · RY right · R bottom**. Diagram-derived
reading, to be confirmed by behaviour at the first commissioning cycle: WR =
battery feed off the fusible link; R = second feed/run path; RY = command side
from the retractable headlight switch (E-02) / dimmer circuit; YG = the
retractor indicator line, driven by the internal cam/limit contacts — the
position-sense conductor the A4/A5 ladders read. The DOWN/UP cam contacts
route power internally and the assembly grounds locally, NOT through the
connector — which is why the all-four-wires clamp reading carried current
(retires the V-080 method doubt for good). Closes V-030 and T-011; T-015
(pop-up draw) closed with the 2026-08 stall readings. The aged limit contacts
get functional confirmation free at the first commissioning cycle; if that
misbehaves, the continuity procedure is in git history.

**D-178** — `[V-050, T-023]` **The ignition-switch closure comes off FSM sheet
F, not a continuity session.** Camden's call — the sheet's inset shows the
contact state per position (OFF · ACC · IG · ST, fed WR from the fusible
link). Recorded read: ACC live in ACC and RUN; IG live in RUN and START; ST in
START only. Whether ACC holds through START changes nothing downstream: the
A16 summed ladder reads 1743 counts with ACC held vs ~1673 with it dropped —
both are >400 counts from RUN — so the resistors can be soldered either way
and the Phase 6 in-car ADC read (D-142) writes the true value into the config
lookup. Sheet F also pins, for later use: stop-light switch F-11 (GW feed, W
out — the brake measurement point), horn relay F-16 (GY · GW · GL) with the
horn switch grounding GL (a ground-side switch — feeds the Q-063 horn-input
design), and the A/T inhibitor at A-06 (GY/RY crank path, RW back-up). Closes
V-050 and T-023.

**D-179** — **The alternator is not charging: 11.39 V at the battery at idle,
11.83 V under load (2026-08) — far below the 13.5–14.5 V charging band; the
car is running off the battery.** Closes `V-077` with the verdict FAILING and
explains the day-by-day electrical decay. `V-019` is unanswerable until a
healthy unit is fitted; the rating is still wanted from the FSM (`V-002`).
Replace-or-rebuild timing is `Q-068` — raised as its own packet because a
dead charging system threatens every remaining phase, not just comfort.

**D-180** — `[Q-061]` **Solenoids on O10 branches with their own fuses; keypad
→ PMU logic pulses them.** Camden: follow recommendations. L4-M 3 and 4 become
the hatch and fuel-door solenoid outputs, fed from the accessory bus. F13 is
no longer claimed by the solenoids — it goes to whichever of DCU climate
memory (`V-056`) and the radar feed (`V-061`) survives. Closes V-033's
allocation question; part choice stays `T-032`/`T-033`.

**D-181** — `[Q-062]` **L4-P 4 becomes the O15 → sill comfort feed** (mirror
heat, F14); mirror motor control waits on the mirror choice (`T-031`), using
L4-M spares when the count is known. Camden: follow recommendations.

**D-182** — `[Q-063]` **Horn is read as the +12V SW pin's logic state, sharing
the wake diode; the washer pump runs on a new relay K12 pulsed off the wiper
circuit; wiper park is mechanical at the motor (factory park contact) unless
`V-074` shows O8 braking needs a park-sense input; the inhibitor remains a
hard requirement and takes a ladder state on A4/A5 in the H-007 re-run.**
Camden: follow recommendations. K12 joins the plate (a spare socket); its
exact coil/contact circuit lands in `SCHEMATICS.md` with H-008. L2-S 3 (park
sense) stays capped pending `V-074`; L1-S1 11 (inhibitor) lands with H-007.

**D-183** — `[Q-064]` **Interim rules until the ICU puts rpm on CAN 0x200:
fuel pump = RUN with a 3 s prime and the inertia-switch cut, no rpm term;
start relay = key START (plus the inhibitor interlock), no rpm term.** The
final rpm-qualified expressions stand beside them in `PMU-CONFIG.md` and take
over when 0x200 is live. Camden: follow recommendations.

**D-184** — `[Q-065]` **A15 becomes a five-state summed ladder — the maths
clears the ≥60-count bar, so option (a) stands.** Sources into the node, with
the D-167 100 kΩ/+5 V bias retained: PARK contact through **33 kΩ**, HEAD
contact through **15 kΩ**, dimmer-HIGH contact through **8.2 kΩ fed from the
HEAD side** (so it only sums with headlights on), PASS momentary through
**3.3 kΩ fed direct** (flash works with lights off). Decode centres (12-bit,
0–20 V): OFF **93** · PARK **604** · HEAD+LO **1201** · HEAD+HI **1666** ·
PASS-active **≥1750** (1828–2045 depending on what else is live). Smallest
gap 162 counts. PASS is a **superstate**: while the reading is ≥1750 the
logic holds the previously decoded lighting states and forces high beam —
so the sub-60-count differences inside the PASS band never need decoding.
Values in `LADDERS.md`; decode table in `PMU-CONFIG.md` §1.

**D-185** — `[Q-068]` **Replace or rebuild the alternator now, before
commissioning.** Camden: follow recommendations. Bolt-on, independent of the
harness; keeps the car drivable and makes every commissioning reading honest.
Sequence: FSM rating first (`V-002`), then stock Mitsubishi or an uprated
drop-in. Raised as `T-050`. `V-019` is judged after it, from telemetry.

**D-186** — **Pop-up drive is one run relay per side — K1 (LH), K2 (RH); the
H-bridge dies and K3/K4's sockets go spare.** Camden confirmed the motors
spin in **one direction only** (crank flips the lamp each half-revolution;
the internal cam stops it at each end), and that the factory retractor
indicator lights **in transit and stays lit when a motor never reaches its
limit — something in the way**. So raise and lower are the same electrical
act: energise the relay until that side's YG transit contact opens again;
**4 s still-closed = obstruction fault** — exactly the factory indicator's
blocked signal, now read by software. Position is tracked from commanded
state; on a cold boot with unknown position the first command self-corrects.
87a-to-ground keeps dynamic braking for free. Which E-03/E-04 conductor is
the cam-interrupted run feed is `V-081`. The window H-bridges K5–K8 are
untouched — those motors do reverse. Supersedes the K1–K4 bridge in
`SCHEMATICS.md` §2 and D-057's both-off-braked table for the pop-ups.

**D-187** — **A4/A5 become 4-state transit-plus-inhibitor ladders (H-007
done).** Sources per node, resistors at the switch, 47 kΩ baseline to ground
at the connector so a broken wire still reads as a fault: YG transit contact
through **3.3 kΩ**; one inhibitor contact through **12 kΩ** — **P/N on A4**
(crank interlock) and **R on A5** (reverse lamps) — spliced onto the node at
the dash post. Counts: both 201 · transit 245 · inhibitor 500 · idle 843 ·
open 1023; tight pair 44 counts, window ±20 (A6's class). The inhibitor's R
contact needs its own conductor from the transmission: it **borrows the first
LS spare, L1-S2 4** — the A/T and this signal both disappear at the LS swap,
so the D-007 reservation is only ever lent. Caution flagged for Phase 6: the
YG cam contact spent its life switching a 3.4 W lamp; confirm it reads
cleanly at the ladder's 0.5 mA. Separately, Camden confirmed the shut-door
readings were **MΩ** (1.13 / 20.9) — clean opens, so the A6 table stands as
designed and the last meter-session caution closes.

> AMENDED same day — L1-S2 7, a plain spare, exists; the inhibitor R contact
> takes it and the D-007 LS reservation stays untouched.

**D-188** — `[Q-069]` **Door-pin wake: a small PNP (or micro-relay) inverter
at the sill node.** Camden: follow recommendations. Emitter on the F3 wake
supply, base sensing the existing A6 door-pin conductor through ~220 kΩ,
output into the door-pin wake diode. No new dash conductor. Adds ~54 µA to
the A6 node — a few counts; re-verify the A6 ladder at Phase 6.

**D-189** — `[Q-070]` **K1/K2 coils fed from O1 through steering diodes, each
in series with the *opposite* side's wink-switch NC pole; wink NO poles feed
the wake strip.** Camden: follow recommendations. Holding a wink blocks the
other side's coil, so when the PMU runs the half-cycle only the winked lamp
moves; O1 stays both supply and command, keeping pop-up telemetry.
**Discovered while drafting:** pin 7 is a diode-OR held high whenever the key
is in RUN, so a wink press — and D-182's horn press — is *unreadable while
driving*. Every momentary needs the hazard pattern: a wake diode for asleep
plus a 5 V-side ladder state for awake. Raised as `Q-071`, which finalises
both this decision's request sensing and D-182's horn input.

**D-190** — `[Q-071]` **The horn joins A8's hazard node through 12 kΩ; winks
stay pin-7-only.** Camden: follow recommendations. A8 becomes a two-switch
summed node — hazard 4.7 kΩ, horn 12 kΩ, resistors at the switch: 259
(hazard+horn) · 327 (hazard) · 558 (horn) · 1023 (released), worst gap 68
counts, window ±30. This finalises D-182's horn input and D-189's wink
sensing: the horn now reads correctly in every key position; a wink works
with the key out or in ACC — a parked greeting — and is simply unavailable in
RUN, a documented limitation. **The horn switch closes to ground** (it always
did — D-178), so its asleep wake uses the D-188 pattern: one PNP on the
plate, emitter on F3, base sensing the A8 node through ~220 kΩ, output into
the horn's wake diode. It incidentally wakes on hazard too, which is
harmless; whether that lets the hazard's dedicated wake conductor retire is
an X-002 note, not decided here. L3-S1 11 becomes the horn conductor,
splicing onto the A8 node at the post.

**D-191** — `[V-056]` **The DCU restores climate memory from SD on wake — no
constant keep-alive.** Settled by the F-001 skeleton (`firmware/dcu/`): load
at boot with CRC and safe defaults, save once on the key-off edge. By D-180's
survivor rule, **F13 therefore goes to the radar module feed** (D-039),
DEFERRED until `V-061` designs the subsystem — the F13 question that has
floated since Rev B is closed. Carrier candidate parts are `V-082` (ICU) and
`V-083` (DCU) until datasheet-verified.

**D-192** — **Instant-on is a hard requirement for the cluster: no OS, no
boot sequence — key on, display on.** Camden's call, stated as critical. Any
renderer path that cold-boots an operating system (the Pi/Linux option in
Q-060's 2026-08 fork) is rejected regardless of panel fit. This is how
factory clusters work too: bare-metal / RTOS cluster silicon painting
tell-tales in hundreds of milliseconds, or suspend-to-RAM behind a
keep-alive — never a desktop-style boot. Q-060's recommendation is rebuilt
around it.

**D-193** — `[Q-060]` **The cluster display is a 12.3″ bar panel on a
1280 × 480 canvas, driven by a BT817 EVE over QSPI from the Teensy —
instant-on, full aperture width.** Camden's call. Supersedes D-150's panel
recommendation and **amends D-168**: dirty-rectangle rendering survives
unchanged, but the tiles now blit into the BT817's 1 MB RAM_G over QSPI, the
framebuffer grows to 614 KB in PSRAM (D-170), and the canvas becomes
1280 × 480 (F-011 resizes the layout in the simulator first). D-159 stands —
nothing crosses the harness. `V-058` merges into `V-085`.
**Two bridge chains, decided by `V-085`:** (i) RGB → LVDS serializer
(SN75LVDS83B-class) into 1280 × 480 cluster glass — but the LQ123K1LG03 is
**330 cd/m²**, which only works if the binnacle brow provides real shade
(the factory cluster lived in the same shade — `T-007` judges the geometry);
(ii) RGB → HDMI encoder (TFP410-class) into the stock scaler board of a
**900–1000-nit 1920 × 720** bar panel — same 1280 × 480 canvas, cleanly
scaled 1.5×, every part still an instant-on ASIC. Chain (ii) is the default
if the brow doesn't convince. `V-084` verifies BT817 timing against
whichever glass; `T-051` raises the orders (BT817 eval board first — it
proves the whole chain on the bench).

**D-194** — **Configure-in-car: the separate PMU bench phase is dropped; the
car is the bench.** Camden's call, tutorial-informed, to save limited time
and funds. Risk assessed as acceptable because the design already works this
way: soft fuses sit at channel caps (D-175), telemetry is the measurement
instrument (D-174), migration is one circuit per sitting with the factory
harness still driving the car home — each cutover is its own commissioning.
Phase 2A's config entry (names, decodes, expressions, interlocks) happens
with the PMU mounted and powered from the new backbone, laptop over CAN1 in
the car, **before any circuit is migrated onto it**.
**Four bench-era rules survive as hard requirements:** (1) a 5 A fuse in the
feed for first power-up (D-145), stepped up only after CAN comes up clean;
(2) 120 Ω termination at both CAN1 ends or the client never connects; (3)
**spare 1.5 mm terminals ordered and three practice crimps pull-tested before
any real crimp** (T-044, Checklist 1.10) — the one severe risk in this plan
is a botched crimp with zero spares; (4) one circuit at a time, the car
drives home every day. **Purchases cut:** breadboards, pot, toggle switches,
bench bulb, hookup wire (~$40); soldering iron defers to the ladder-resistor
build (Phase 5) and the BT817 eval defers to the module era — boards 2/3
flashing (T-048) defers with it, board 1 carries all current firmware.

**D-195** — **Keep the old alternator for now; diagnose the excitation
circuit before any part is bought — and the BOM becomes the single purchase
ledger.** Camden's call: no local stock anyway, and the no-charge (D-179) may
be self-inflicted — the emissions-control delete rewired that area, and on
this Mitsubishi the exciter path runs through the dash CHARGE-lamp circuit; a
broken wire or dead bulb produces exactly the observed symptom. `V-086` is
the test: key ON engine OFF the CHARGE lamp must glow; engine running, a blip
to ~2,500 rpm that jumps battery volts confirms an excitation fault (free
fix). Only a condemned unit reverts T-050 to D-185's mail-order replacement.
**Consolidation:** purchases now live in exactly one place — `BOM.md` §11,
organised by wave. `BENCH-KIT.md` keeps procedure only; the one-day-old
`SHOPPING-WAVES.md` is absorbed and deleted.

> — applies to D-185 above: AMENDED BY D-195 — diagnose before buying.

**D-196** — **The BOM is rebuilt end to end in purchase/install order — wave
0 local, wave 1 the small cart, wave 2 the build in install sequence
(backbone → panel → legs → sill), wave 3 the module era, wave 4 deferred —
and it is the only shopping-styled page in the tree.** Camden's explicit
rewrite request: the old subsystem grouping had no relevance to timing, and
bench-phase language survived D-194. Tools now appear in the wave where they
are first used. `BUY-LIST.md` is repurposed as the part-number and source
reference (its stale what-was-not-bought section removed; the filename kept
so the audit trail's links stand). `BENCH-KIT.md` owns procedure and
inventory only.

**D-197** — `[V-037, T-012, T-014]` **Fuel sender measured: 6 Ω full ·
31.5 Ω mid · 80 Ω empty — and with it the old-harness measurement campaign
is COMPLETE.** The numbers force one design addition: against the PMU's
internal 10 kΩ pull-up the whole tank compresses into ~8 ADC counts inside
the fault window, so **A7 gets an external 100 Ω 1 % pull-up to the +5 V
reference, fitted at the sender connector** (1 W part — it dissipates
~0.25 W at full; or 2 × 200 Ω ½ W in parallel). Decode centres: FULL **58**
· MID **247** · EMPTY **457** · short <25 and open >900 are faults; the
sender is nonlinear, so the config uses the three-point lookup with
interpolation and the in-car read (D-142) trues it. ~47 mA from the 500 mA
+5 V budget at full tank, accepted. Closes V-037, T-012 and T-014; F-003's
last input exists; values live in LADDERS.md §A7, nowhere else.

**D-198** — **The alternator gets its factory-spec excitation circuit in the
new harness; the `V-086` diagnosis is skipped.** Camden's call: new wiring
must be built either way — wire it right, and replace the unit only if it
still refuses to charge on the correct circuit. Reading sheet A for this
exposed a latent design fault: the factory **BW wire is the field-excitation
FEED** (IG → 7.5 A fuse → alternator), but the rebuild plan had repurposed
that path as a passive ICU sense input — the new harness would never have
excited the alternator at all, ICU or no ICU. The fix, factory-faithful:
**O12 IGNITION branch → F15 (7.5 A, the fuse block's twelfth position) →
L1-S1 2 → alternator BW.** The WB charge-sense wire gets its own conductor,
**L1-S2 8 (was spare) → post → DP-ICU 11**, an ICU input at Phase 9; until
then the PMU's battery-voltage telemetry and the undervoltage interlock are
the charge indicator. `V-086` closes unrun — superseded by correct wiring;
`V-019` is judged at commissioning. This also names the prime suspect for
D-179's no-charge: the factory BW path ran through the emissions-era
connectors that the delete disturbed.

**D-199** — **V-081 sharpened by sheet E, not closed.** The reference decode
gives WR = constant feed, **R and RY = the two command inputs** from the
deleted E-02 switch, YG = indicator — but it also recorded the drive as
"reversible," which contradicts Camden's direct observation of the motor
(D-186: one direction only). The decisive check, at E-03 unplugged: ohms
**R → case and RY → case at parked, mid-travel and raised.** One winding
reached through different cam segments per position = single-direction
confirmed, and **K1/K2's contact drives R and RY bridged** (whichever cam
segment is closed takes the current; WR is capped). Two distinct windings =
genuinely reversible, and D-186 gets revisited before Phase 4 wires the
plate. The reference page's "Reversible" line now carries this conflict note.

---

## CONSOLIDATION — 2026-08-31

**D-200** — **The tree is consolidated: five project folders, one money page,
one process folder.** Camden's reorganisation, completed and made consistent
this session. `04-SUBSYSTEMS` and `06-PROCUREMENT` are retired:
`BATTERY-INSTALL.md` joined the build folder, `HEAD-UNIT.md`,
`PARTS-CHANGES.md` and `DEFERRED-FEATURES.md` moved to `99-ARCHIVE/` with
their live facts re-homed (battery → build; pre-wired status → the CSVs /
`CAVITY-STATE.md`; head-unit wiring was already in the pin plan). The
remaining folders renumbered to close the gaps: `05-BUILD` → `04-BUILD`,
`07-PROCESS` → `05-PROCESS` — every link, tool path and doc updated.
`BUY-LIST.md` (deleted in the reorganisation, reversing D-196's
keep-the-filename call) is absorbed as `BOM.md` §9, the re-order reference;
`METER-SESSION.md` is deleted outright — the campaign it described closed
(`T-014` → D-197) and its references now cite telemetry (D-174/D-175). BOM
sections lost in the shuffle (Wave 1, Wave 4, the deletions ledger) were
rebuilt from the git history.

**D-201** — **The lighting-body project is dissolved back into electrical-pmu
as deferred second-pass scope.** Camden's call; amends D-123 — the *split* is
reversed, but its substance stands: lighting still gates on nothing, costs
last money, and starts only after shakedown (L-004). The five process files
were duplicating the electrical project's process structure for four tasks,
one question and three verifies. Now: design in `01-DESIGN/TAIL-LIGHTS.md`,
decisions below (L-001 … L-004, IDs unchanged), open items in `OPEN.md` §8,
tasks in `TASKS-CAMDEN.md` §6, money as `BOM.md` Wave 5. The originals are
archived as `99-ARCHIVE/2026-08-31_lighting-body/`.

### Lighting decisions — merged from `lighting-body/DECISIONS.md` (D-201)

The lighting scope also inherits D-107 (custom tail lights), D-110 (pop-ups
stay) and D-111 (driver PCB per housing) — those entries are above, in the
round that made them.

**L-001** — Q-047 → **Reverse section: 5 cm wide, 2.2 cm strip height.**
Backup lamps have **no minimum lens area** federally. But brightness does not
substitute for area, because a reverse lamp's job is to *light the ground*,
not just be seen — shrinking the aperture and raising intensity gives a
hotspot and glare. At a nominal 30 cm aperture: 5 cm reverse leaves 25 cm of
red, which at 2.0 cm is exactly 50 cm². **2.2 cm gives 55 cm² — 10 % margin**,
so a measurement error in `V-063` doesn't put it under the line. Reasoning in
`../01-DESIGN/TAIL-LIGHTS.md` §8.

**L-002** — **Headlamps are not a custom-build item.** A strip of LEDs cannot
produce a beam cutoff, and no care in fabrication fixes that — the optic is
the problem. **Source a DOT-compliant sealed unit.** Tail lights are a
reasonable custom project because the requirement is *be seen*; headlamps
have to *illuminate the road without blinding oncoming traffic*, a beam
pattern measured across a grid of angles.

**L-003** — **Soft fuses must be re-set after any bulb change.** Values set
against incandescent are far too generous for LED — a tail circuit set at
6 A does not protect a 3 A LED load. The same rule is D-122 on the electrical
side; the second-pass table is waiting in
`../04-BUILD/MIGRATION-LOG.md`.

**L-004** — **Hard prerequisite: the electrical rebuild is finished and
shaken down.** Phases 6, 7 and 8 complete, factory harness out, car driving
on the PMU with stock bulbs and soft fuses set from measurement. Only then
does the lighting pass change bulbs.

---

## EXPEDITED ORDER — 2026-08-31

**D-202** — **One-teardown plan: everything is ordered now, before the tape
session; measurements confirm before cutting, not before buying.** Camden's
call. The interior comes apart once — teardown day 1 does every 0B
measurement (T-007/T-008/T-024/T-028/T-029, plus the lighting looks), and the
build proceeds with parts already in hand. Because routes and the dash
envelope are unmeasured at order time, **wire is bought with a 1.5× margin
and a 25 ft floor per colour** (~2,550 ft ordered vs ~1,150 ft calculated —
the full per-colour table is `BOM.md` §11c), and contacts/seals go to +30 %
spare. What T-007/T-008 gate MOVES: they no longer gate any purchase; they
still gate **cutting the backer plate** and **cutting wire to length**. The
drive-home rule survives — trim panels off is still a drivable car; the
factory harness stays live until each circuit migrates (D-023/D-024
unchanged). Waves 0, 1 and 2 merge into one buy (amends D-196's gating, not
its wave structure — the BOM keeps waves as install order).

**D-203** — **Sourcing calls for the expedited buy, balancing proven parts
against price without touching the safety-critical line.** Recorded so the
cart matches the design:
(a) **Class-T corrected:** the 150 A block is Blue Sea **5007100**
(110–200 A; the 5504 named earlier is the 225–400 A family's) with Blue Sea
**5114** 150 A Class-T fuses ×2 (one spare). Not economised — lithium
interrupt duty (D-062).
(b) **Plate fuse block is three 4-position independent-feed ATC blocks**
(OptiFuse BLR-I-504 class), not one 12-way bussed block — the 12 plate fuses
draw from six different sources (busbar, K11, O1, O12, O15, O20), which a
common-bus block cannot serve. 3 × 4 = 12 positions exactly; feeds jumpered
where shared. Sill keeps its own 3 holders.
(c) **Labels:** Brother **PT-E300** class printer with **HSe heat-shrink
tube cartridges** replaces the generic "label printer + sleeve" lines — one
tool prints directly onto shrink sleeve, which is the D-016/CUT-LIST label
spec.
(d) **Crimpers:** genuine HDT-48-00 is the gold standard; the buy is the
**iCrimp IWD-16 + IWD-12** pair (4-indent, solid and stamped contacts) with
the existing coupon/pull-test protocol (Checklist 1.10–1.11) as the
acceptance gate. Open-barrel FCI crimper still waits on the `V-069` die
check against a real terminal.
(e) **Battery box:** NOCO **HM318BKS** (Group 24–31) — the HM426 named
earlier is a dual-6 V box. `V-093` checks the Ionic's Group-25 case in it.
(f) **Keypad:** ECUMaster **ECUKB8** 8-position, $369, direct from
ECUMaster USA — Ballenger lists only the 6/12-button unit.
(g) **2 AWG:** fine-strand copper welding cable, loomed and grommeted per
SAFETY, over marine-tinned at ~2× the price; lugs stay closed-barrel tinned
copper, hydraulically crimped.
(h) **Wire:** GXL by the foot from WireBarn — solid AND striped combos, so
the D-016 base+tracer scheme survives without buying 60 spools; Crimpzone /
CE Auto are the fallbacks for any missing combo.
Vendors consolidate to five orders: WireBarn (wire) · DeutschConnector.com
(every Deutsch part, genuine) · Amazon (backbone, tools, consumables,
electronics) · Waytek (fuse blocks, relays, sockets) · Ballenger (FCI
terminals) + the one ECUMaster direct line. Every part number and price in
the manifest carries a `V-###` until it is in the cart at a live price.

**D-204** — **TAIL-LIGHTS.md leaves the active tree.** Camden's "simplify"
commits removed it; the design (FMVSS area maths, TL-1 … TL-19, the headlamp
sourcing rule) is preserved at
`99-ARCHIVE/2026-08-31_lighting-body/TAIL-LIGHTS.md` — recovered from git —
and every live reference now points there. The deferred lighting scope's
live surface is DECISIONS §Lighting, OPEN §8, TASKS-CAMDEN §6 and BOM
Wave 5; the archived file is the design reference to pull back out when the
second pass starts (L-004).

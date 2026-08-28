# Decision Log — Electrical / PMU

Append-only. Never edit or delete an entry. To reverse, add a new decision and
mark the old one `SUPERSEDED BY D-0xx`.

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
| **Housekeeping** | D-026 markdown · D-041 Rev B · D-042 archive · D-043 ID permanence · D-101–104 purchases |

---


Format: `ID | decision | one-line reason`

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

**D-007** — Baseline pinned for the current 12A / Weber configuration. Two 25 A
channels (O13, O14) reserved for LS ECU/injectors and LS cooling fans.

**D-008** — Relay bank uses 16 sockets, 10 populated. Six empty sockets are
cheap future-proofing.

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

**D-035** — 13 leg connectors total: L1 ×2, L2 ×4, L3 ×3, L4 ×4. L2 and L4 need
two DTP shells each because DTP is only manufactured in 2-way and 4-way and the
pop-up and window motors need six and four heavy conductors respectively.

**D-036** — The dash post carries 2 lugs (DP-BAT, DP-GND), the sealed PMU device
connector (DP-PMU), 2 DTM drops (DP-DIAG, DP-KEY) and 13 leg receptacles.

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

---

# UPDATE 2026-08 — answers applied

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

**D-077** — **Two nodes, not one: DCU and ICU.** The DCU owns climate, comfort
switching and sensor acquisition; the ICU owns the instrument display. Separate
because the cluster is safety-visible and climate control is not — a blend-door
firmware bug must never blank the tachometer.

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

# UPDATE 2026-08 — round three answers

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

**D-104** — Housekeeping: **T-016 (diagnose K-008) had been dropped** from the
open task list during an earlier rewrite. Restored. It is one of only two
irreversible-window tasks in the project — the other is T-014 — and losing it
would have meant losing the only chance to find the fault before the harness
comes out.

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
`03-MODULES` `04-SUBSYSTEMS` `05-BUILD` `06-PROCUREMENT` `07-PROCESS`. Grouped by
**when you need it**, not by document type. `legs/` became `02-HARNESS/`.
Root holds only `README.md` and `STATUS.md`.

---

# ROUND FOUR ANSWERS — 2026-08

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
BOM. Added — see `06-PROCUREMENT/BOM.md`.

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

**Workarounds, all in `05-BUILD/METER-SESSION.md` Part 3:**

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

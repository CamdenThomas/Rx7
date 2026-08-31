# Open Queue — Electrical / PMU

*Rev 2026-08-31 · owns: what is undecided (Q), unconfirmed (V) or assumed (A). Answered items move to [`DECISIONS.md`](DECISIONS.md) and leave this file; the ID stays permanent and is cited as `Q-038 → D-095` from then on. [`ID-REGISTRY.md`](ID-REGISTRY.md) lists every ID ever issued.*

**How to answer:** type under the `ANSWER:` quote, or say it in a session. The
agent records the D-entry and removes the packet here.

## Contents

1. Design packets — the five that gate Checklist 0.23 · 2. Other questions ·
3. Verify — flagged · 4. Verify — easy · 5. Verify — needs the car ·
6. Verify — blocked · 7. Assumptions in force · 8. Deferred — lighting (D-201)

---

## 1 · Design packets — ruled 2026-08 (Checklist 0.23)

All five packets were answered "follow recommendations":
`Q-061` → D-180 · `Q-062` → D-181 · `Q-063` → D-182 · `Q-064` → D-183 ·
`Q-065` → D-184. The connector order now waits only on `T-008`.

---

## 2 · Other questions

### Q-014 · Dash panel envelope
**Ask:** W × H × D behind the dash, plus clearance for the 39-pin lever.
*Preliminary 2026-08: the cluster aperture is ~10 cm tall × 26–30 cm wide
(Camden). Depth and lever clearance still wanted.*
**Blocks:** panel 1:1 drawing, panel parts order, Checklist 0.8, 0.20–0.21, all
of Phase 4. A tape measure — the panel is smaller than originally planned
(five relays on the plate, D-067).

**ANSWER:**
>
>

### Q-028 · CAN wake latency
**Ask:** If horn and wink ever move to CAN wake once the MCU exists, what
wake-to-horn latency is acceptable on a cold boot? Not live yet; recorded so it
isn't rediscovered.

**ANSWER:**
>
>

### Q-001 · VIN
**Ask:** Record the VIN in `00-CAR/vehicle.md` (`T-049`). Nothing blocks on it;
it is the one field a stranger would look for first.

**ANSWER:**
>
>

---

## 3 · Verify — flagged

| ID | Claim | Source |
|---|---|---|
| **V-070** | **12A redline.** `stats.h` assumes 7000 rpm, which also sets the tach red zone | FSM |
| V-071 | Minimum acceptable oil pressure for a 12A at idle. Assumed 1.0 bar | FSM / rotary reference |
| V-072 | FB fuel tank capacity. Assumed 15.9 gal | FSM |
| **V-073** | **IMU mounting orientation on the ICU PCB** must match the axis convention in D-161, or every axis needs a sign flip | Decide before PCB layout |
| **V-074** | **Does O8 wiper braking need a park input?** If the PMU's braking feature only works against a park-sense signal, `Q-063` option (c) is off the table | PMU manual |
| **V-075** | **Does the PMU have a native shutdown delay** that makes the O22 self-hold latch unnecessary — freeing pin 8 and K11's coil logic | PMU client — Checklist 2.15 |

## 4 · Verify — easy: one search, catalogue page, or a look

| ID | Claim | Source |
|---|---|---|
| V-053 | Battery terminal type — SAE or 3/8 threaded. The battery is in hand; **look at it** before the lug order (`T-029`) | The battery |
| V-051 | Ionic case dimensions before cutting the cargo bin | Tape measure |
| V-052 | Battery heater trigger and winter draw | Ionic docs / app |
| V-014 | DT size-16 contact current rating. Catalogue confirms size 20 = 7.5 A | TE catalogue pp. 169–180 |
| V-057 | TCAN1042/1051 exact part suffix | TI datasheet |
| V-047 | Shielded 16 AWG availability; single-end shield grounding | Wire supplier |
| V-069 | **Open-barrel crimper die size.** Confirm against a real terminal before buying | Measure the terminal |
| V-040 | Aeromotive Phantom 340 draw at target pressure | Aeromotive spec — future part |
| V-059 | Teensy 4.1 availability after the Adafruit → SparkFun distribution change | PJRC / SparkFun, before the carrier PCB commits |
| V-001 | Stock 12A coil / ignitor configuration — one coil per rotor, leading and trailing, as the factory diagram shows | Under the hood |
| **V-084** | **BT817 output timing vs the chosen glass** (D-193): pixel clock, sync polarity, and the bridge — SN75LVDS83B serializer (chain i) or TFP410-class HDMI encoder + scaler-board EDID handshake (chain ii) | Datasheets + one bench session with the BT817 eval board |
| **V-085** | **Which glass** (D-193; absorbs `V-058`): LQ123K1LG03 measured at **330 cd/m²** — chain (i) only works if the binnacle brow shades it like the factory cluster it came from (`T-007` judges); otherwise chain (ii), a 900–1000-nit 1920 × 720 bar panel behind its stock scaler board | `T-007` geometry + listings |
| **V-082** | ICU carrier candidate parts — LMR33630-class buck, SMBJ33A TVS, BAT54S clamps, H11L1/LM393 tach front end ([`ICU-CARRIER.md`](../03-MODULES/ICU-CARRIER.md)) | Datasheets before layout |
| **V-083** | DCU carrier candidate parts — second buck for the servo rail, AOD4184-class FETs, INA180 shunt amp ([`DCU-CARRIER.md`](../03-MODULES/DCU-CARRIER.md)) | Datasheets before layout |

### Verify — the expedited order (D-202, D-203; see BOM §11)

Every manifest part number and price is a placeholder until it sits in a
cart at a live price. The two dash-space items close on teardown day 1.

| ID | Claim | Via |
|---|---|---|
| **V-087** | **Centre-stack depth and clear width** behind the radio/ashtray/lighter region — the PMU (131 × 112 × 32.5 mm) is assumed to fit there flat with clearance; part of `T-007` | Tape measure, teardown day 1 |
| V-088 | The relocated amp's old position and the deleted cassette/ashtray/lighter free the space Camden expects; amp + battery + Class-T + disconnect all fit the rear cargo bins | Eyes on it at teardown |
| V-089 | WireBarn stocks every striped GXL combo in BOM §11c, by the foot, in 12/14/16 | Cart check; fallback Crimpzone / CE Auto |
| V-090 | DeutschConnector assembly-kit contents (contacts included, genuine), and `1027-003-1200` clip source | Cart check; clips fallback TE/Mouser |
| V-091 | OptiFuse BLR-I-504 is truly independent-feed, panel-mountable, ATO/ATC | Datasheet before ordering |
| V-092 | Brother HSe sleeve sizes: HSe-211 fits 16 AWG, HSe-221 fits 12–14 AWG finished OD | Brother compatibility chart |
| V-093 | NOCO HM318BKS interior fits the Ionic S9 Group-25 case + terminals + boots | Dims vs `V-051` measurement |
| V-094 | MRBF rating for the starter feed (200 A assumed) survives cranking without nuisance-blowing | Cranking-current data / Ionic docs |
| V-095 | Fine-strand welding cable is acceptable for the 2 AWG runs (loomed, grommeted) vs SGX/marine | Insulation temp rating on the chosen listing |
| V-096 | iCrimp IWD-16/IWD-12 crimps pass the coupon pull tests on genuine solid contacts | Checklist 1.10–1.11 — the acceptance gate |

## 5 · Verify — needs the car

| ID | Claim | Via |
|---|---|---|
| V-002 | Alternator output rating — the case says only 'B' / Mitsubishi (2026-08), no rating readable | FSM / Mitsubishi part lookup |
| V-055 | Sill space behind the kick panel — 4 relays, 3 fuse positions, ground stud | Tape measure — Checklist 0.10 |
| V-038 | Coolant level unit and oscillator still fitted | Inspect |
| **V-081** | **Pop-up drive conductors** (D-199): sheet E says WR = constant, R + RY = the two commands, YG = indicator — but it reads as reversible while Camden observed one direction (D-186). Decisive: at E-03 unplugged, **ohms R → case and RY → case at parked / mid / raised**. Same winding via different cam segments = single-direction confirmed, K1/K2 drive **R + RY bridged**, WR capped. Two windings = reversible — revisit D-186 before Phase 4 | Five minutes with the meter, before the L2 leg is pinned |
| V-067 | **Tach pulses per revolution.** Assumed 2 for a 2-rotor off the leading coil. Wrong scales every RPM reading by a constant | Meter session or FSM |
| V-021 | Horn current draw — estimate 4–8 A the pair; fuse at the 15.0 cap (D-175) | PMU telemetry after migration (D-174) |

## 6 · Verify — blocked on something else

| ID | Claim | Blocked by |
|---|---|---|
| V-065 | **PMU's own CAN export format.** ECUMaster fixes it, we don't. Gates the PMU half of the message map | The client — Checklist 2.5 |
| V-019 | Can a healthy stock-rating alternator carry the migrated load | After the `Q-068` ruling + PMU telemetry |
| V-060 | New mirror conductor count and control protocol | Pick the mirrors, `T-031` |
| V-028 | Is a one-touch (single wipe) function wanted in the wiper logic | Decide during Checklist 2.12 |
| V-061 | Radar sensor interface | Design the subsystem — Z-002 in [`FORWARD-WORK.md`](FORWARD-WORK.md) |

## 7 · Assumptions in force

Assumptions carry an `A-` ID so a wrong one can be found and unwound. Closed
ones are in [`DECISIONS.md`](DECISIONS.md) (A-005 → D-148, A-007 → D-112, A-009 → D-091).

| ID | Assumption | Where it bites |
|---|---|---|
| A-010 | Brake fluid level goes to the ICU on DP-ICU 12 via L1-S2 1. Coolant and oil level are optional, have no ICU cavity, and are capped in L1-S2 2–3 | `connectors.csv`, [`CAVITY-STATE.md`](../02-HARNESS/CAVITY-STATE.md) |
| A-011 | The wideband O2 signal (K-001) is carried to the dash on L1-S1 12 and capped. It is not an ICU input and has no display until the LS | `connectors.csv`, [`engine.md`](../02-HARNESS/engine.md) |
| A-012 | The luggage compartment switch joins the A6 door-pin ladder as a fourth state — re-run the ladder maths before it is added | [`LADDERS.md`](../01-DESIGN/LADDERS.md), L4-S 3 |
| A-013 | The CAN keypad is powered from the accessory bus O10 (DP-KEY 3), so it is dead when the car sleeps and cannot itself be a wake source | [`PIN-MAP.md`](../02-HARNESS/PIN-MAP.md) DP-KEY, [`SCHEMATICS.md`](../01-DESIGN/SCHEMATICS.md) wake network |

---

## 8 · Deferred — lighting & body (D-201; nothing here is urgent)

The lighting second pass does not start until the rebuild is shaken down
(L-004). The three verifies are ten-minute looks that ride along with the 0B
tape-measure session (`T-034`/`T-035`/`T-037` in [`TASKS-CAMDEN.md`](TASKS-CAMDEN.md) §6);
`Q-048` is a catalogue search. Design context: [`TAIL-LIGHTS.md` (archived)](../../../99-ARCHIVE/2026-08-31_lighting-body/TAIL-LIGHTS.md).

### Q-048 · Headlamp unit
**Ask:** Which DOT-compliant unit goes in the retained pop-up buckets (D-110,
L-002)?
**Options:** (a) 4×6 rectangular LED sealed beam + a flat adapter plate in the
round bucket; (b) 5×7 rectangular LED sealed beam — same, larger, less
"short"; (c) 7-inch round LED with a rectangular-appearing element — fits the
bucket directly, no fabrication.
**Recommendation:** (c) unless `V-066` finds the bucket is already
rectangular, in which case (a) with no plate.
**Blocks:** the headlamp order (`T-036`); nothing electrical — O2/O3 and
L2-P1 1/2 are unchanged whatever is chosen.

**ANSWER:**
>
>

### Verify — lighting

| ID | Claim | Via | Task |
|---|---|---|---|
| **V-063** | Stock tail light aperture — width, height, depth, mounting. The whole strip design is scaled from a nominal 30 cm | Tape measure | `T-034` |
| V-064 | A DOT/SAE-compliant LED module source, red and white, with published candela | Catalogue search | `T-037` |
| V-066 | 7-inch round or rectangular sealed beams on this car — and whether LED housings are already fitted ([`../01-DESIGN/LOADS.md`](../01-DESIGN/LOADS.md) says they are; [`TAIL-LIGHTS.md` (archived)](../../../99-ARCHIVE/2026-08-31_lighting-body/TAIL-LIGHTS.md) §8 assumed round sealed beams) | Look in the bucket | `T-035` |

**Body — not yet scoped.** Rust extent (K-007), paint, trim and seals. No IDs
until the survey happens.

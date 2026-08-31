# BOM — the money, in purchase order

*Rev 2026-08-31 (D-196, D-200) · owns: the money — every purchasable line, organised by wave in the order things are bought and installed. **This is the only shopping page in the tree.** Part numbers and sources for re-orders are §9's (`BUY-LIST.md` absorbed here, D-200); housing part numbers are [`../02-HARNESS/CONNECTORS.md`](../02-HARNESS/CONNECTORS.md)'s.*

All prices are estimates until checked against a live quote. Everything is
Deutsch DT/DTP/DTM — no AMPSEAL (D-070). There is no bench phase (D-194): the
car is the bench, and every tool or part appears in the wave where it is
actually used. Lighting is Wave 5, deferred until after shakedown (D-201,
L-004).

## Contents

1. Totals · 2. Bought · 3. Wave 0 local now · 4. Wave 1 small cart ·
5. Wave 2 the build · 6. Wave 3 module era · 7. Wave 4 deferred ·
8. Wave 5 lighting & body · 9. Re-order reference · 10. Deletions that saved
money · 11. **Order manifest — the expedited one-teardown buy (D-202)**

---

## 1 · Totals, by wave

| Wave | ~$ | Gate |
|---|---|---|
| Bought | **2,950–3,350** | — |
| 0 · local, now | ~30 | nothing |
| 1 · one small cart | 20–45 | nothing |
| 2 · the build (backbone → panel → legs) | 2,800–4,750 | **none for the order** (D-202) — the tape session now gates *cutting*, not buying |
| 3 · module era | 510–1,170 | `V-057`, carrier layouts, `V-084`/`V-085` |
| 4 · deferred / conditional | 210–550+ | their own designs |
| **Electrical remaining** | **~3,600–6,550** | |
| **ELECTRICAL PROJECT TOTAL** | **~6,550–9,900** | |
| 5 · lighting & body (second pass) | 400–980 + body unscoped | shakedown done (L-004) |

## 2 · Bought

| Item | ~$ | Closes |
|---|---|---|
| ECUMaster PMU-24 DL — includes the mating connector kit, 39 terminals and the USB-to-CAN adapter | 2,050–2,250 | closes V-016, V-018, T-021 |
| Ionic S9 heated lithium | 700–900 | closes V-017 |
| UNI-T UT210E clamp meter | 40–60 | closes T-001 |
| 3 × Teensy 4.1 (with pins) | ~96 | |
| 5 × SN65HVD230 CAN transceiver modules (desk use only — D-085) | ~15 | |
| 1 × micro-USB cable | ~5 | |
| Paint pen | 4 | `T-043` — mark cavity 1 on the housing |
| Electrical tape | 4 | |
| 2 × Sicma 39-pos spare housings with pin sets — inbound | ~25 | closes T-027; `T-045` on arrival |
| Blade fuse assortment incl. **5 A** | 0 | |

Part numbers, sources and the three-housing strategy: §9.

## 3 · Wave 0 — local, now · ~$30

| Item | ~$ | For |
|---|---|---|
| Inline ATO holder | 12 | First power-up protection (D-145) |
| 2 × microSD card | 10 | Firmware stage 6 now; the DCU later |
| 120 Ω ¼ W resistors ×4 | 2 | CAN termination — the client never connects without them |

## 4 · Wave 1 — one small cart · ~$20–45

Nothing gates it, and nothing is crimped before it lands (D-194).

| Item | ~$ | For |
|---|---|---|
| Spare 1.5 mm FCI terminals **211CC2S2160P** ×15 minimum | 15–40 | `T-044` — zero small spares exist; **three practice crimps are pull-tested before any real one** (D-194) |
| Coupon wire offcuts, 14–17 AWG | ~5 | The practice crimps |

## 5 · Wave 2 — the build, in install order · ~$2,800–4,750

Ordered up front with margins under the one-teardown plan (D-202) — the tape
session (`T-007` `T-008` `T-024` `T-028` `T-029`) happens on teardown day 1
and gates cutting, not buying. Every design question is ruled. Sub-waves are
the install order: backbone, then panel, then legs. **The shopping version of
this wave, by store, is §11.**

### 5a · Backbone first (Phase 3) · ~$580–960

| Item | Qty | ~$ | Note |
|---|---|---|---|
| Battery tray / box + hold-down + backing plate | 1 | 90–180 | `T-024` bin measurement |
| Class-T fuse block + 150 A fuse | 1 | 90–140 | |
| Master disconnect | 1 | 55–90 | |
| Distribution post | 1 | 25–40 | |
| MRBF terminal fuse + holder | 1 | 35–60 | |
| 2 AWG cable, ~25 ft (D-091) | — | 80–130 | |
| 1/0 or 2 AWG starter feed | — | 40–80 | |
| Lugs, boots, adhesive shrink, grommets, loom, studs, cavity wax | — | 125–160 | `T-029` post type before lugs |
| Hydraulic lug crimper | 1 | 40–80 | used this sub-wave |

### 5b · Panel build (Phase 4) · ~$820–1,400

| Item | Qty | ~$ | Note |
|---|---|---|---|
| Backer plate, standoffs, hardware | — | 60–120 | sized by `T-007` / `Q-014` |
| Micro relays, 30/40 A, with diode | 5 + 2 spare | 40–70 | K1, K2, K11, K12 on the plate (D-182, D-186); K9 in the engine bay (D-148) |
| Relay sockets, panel-mount | 10 | 50–90 | 4 populated, 6 spare (D-186) |
| Fuse blocks — 3 × 4-position **independent-feed** ATC (D-203b: the 12 plate fuses draw from six sources; a bussed 12-way cannot serve them) | 3 | 30–60 | 12 positions — full (F15 exciter, D-198); `V-091` |
| Fuses, assorted + spares | — | 15 | |
| Busbars — always-hot and ground | 2 | 90–140 | |
| Wake network: 8-pos terminal strip, 1N5819 ×8, 1N4007 ×5, 2 × PNP + 220 kΩ, 10 kΩ bleed, 100 kΩ bias ×2 | — | 40–70 | D-167, D-188, D-189, D-190 |
| E24 1 % resistor assortment | 1 kit | 15 | every ladder value (LADDERS.md) |
| Soldering iron + solder + heat-shrink | — | 30–70 | first used here |
| Wire strippers 10–22 AWG, flush cutters, needle-nose | — | 35–55 | |
| Label printer + heat gun | — | 40–90 | |
| 120 Ω terminator + DTM-04-4P diag port pair | — | 20 | wire DP-DIAG early (D-194 — the laptop lives in the car) |
| Open-barrel crimper, 1.5 + 2.8 mm dies | 1 | 60–150 | **`V-069` die check against a real terminal first** |
| CAN keypad, 8-key | 1 | 300–450 | |

### 5c · Harness legs (Phase 5) · ~$1,320–2,240

| Item | Qty | ~$ |
|---|---|---|
| GXL wire — 10/12/14/16 AWG, solid + striped per the D-016 colour scheme | ~2,550 ft ordered (1.5× margin, D-202 — per-colour table §11c) | 550–900 |
| Deutsch DTP housings, contacts, wedges | 5 pr + spare | 110–180 |
| Deutsch DT 12/8/6/2 housings, contacts, seals | 12 pr + spare | 220–350 |
| DTM-04-4P diag port | 1 pr | 15–25 |
| Secondary wedgelocks — W12, W8, W6, W2, WP-4, WP-2, WM-4 + 20 % spare | ~19 pr | ~110 |
| Mounting clips `1027-003-1200` | ~19 | 30–50 |
| Backshells 180°/90° with strain relief | ~8 | 60–120 |
| Boots | ~10 | 30–60 |
| Dust caps | ~6 | 15–25 |
| Adhesive-lined heat shrink assortment | — | 70–120 |
| Tesa 51608 cloth tape | 5 rolls | 50–80 |
| Abrasion loom / split conduit | — | 60–120 |
| Grommets, bulkhead pass-throughs, P-clips | — | 80–150 |
| Ring terminals, ferrules | — | 40–70 |
| Heat-shrink label sleeves + cartridges | — | 50–90 |
| Deutsch DT/DTP crimper + coupon stock | 1 | 80–250 |

The exact housing list — 15 leg housings, 2 door, 4 drops, 24 mated pairs —
is generated in [`../02-HARNESS/CONNECTORS.md`](../02-HARNESS/CONNECTORS.md).

### 5d · Sill node (with Phase 5) · ~$65–130

| Item | Qty | ~$ |
|---|---|---|
| Aluminium plate, kick-panel mount | 1 | 20–40 |
| Relay sockets K5–K8, fitted empty (D-131) | 4 | 20–40 |
| Fuse positions F8, F9 (empty), F14 | 3 | 15–30 |
| Ground stud, star washers, sealant | 1 | 10–20 |

## 6 · Wave 3 — module era · ~$510–1,170

The car drives on the PMU before any of this is needed (D-081). Order the
BT817 eval board first (`T-051`) — it proves the display chain on the desk
before glass money moves.

| Item | Qty | ~$ | Note |
|---|---|---|---|
| BT817 EVE evaluation board | 1 | 50–90 | `T-051`, proves `V-084` |
| Display bridge — SN75LVDS83B serializer **or** TFP410-class HDMI encoder | 1 | 10–30 | chain per `V-085` |
| 12.3″ bar glass (1280 × 480, or 1920 × 720 + its scaler board) | 1 | 60–250 | `V-085` brightness call — `T-007` brow depth decides |
| CAN transceivers, in-car — TCAN1042/1051 | 4 | 12 | D-085, `V-057` |
| Teensy socket headers (standard 0.1″ female) | 3 sets | 12 | |
| PSRAM chips, 8 MB | 2 | 10 | D-170 |
| Carrier PCBs, 2 revisions | 4 | 100–250 | H-001 / H-002; parts `V-082`/`V-083` |
| Automotive bucks 12 V → 5 V | 2–3 | 20–40 | second unit is the DCU servo rail |
| TVS (SMBJ33A), reverse protection, input filters | — | 16 | |
| ICU analog front end — dividers, RC, clamps, tach opto/comparator | — | 20–30 | |
| IMU | 1 | 5 | orientation `V-073` before layout |
| Bus hardware — far-end 120 Ω, private link pair | — | 7 | |
| Page button, momentary | 1 | 3 | D-169 |
| HVAC servos | 4 | 60–120 | after the heater-box teardown |
| Oil temperature sender + VSS sensor | 1 + 1 | 60–120 | thread and range on the engine |
| Enclosures + cluster bezel fabrication | — | 80–200 | |

## 7 · Wave 4 — deferred / conditional · ~$210–550+

Each waits on its own design or diagnosis; none blocks the build.

| Item | ~$ | Gate |
|---|---|---|
| Mirrors — larger, heated, digital control | 120–300 | `T-031`, `V-060` conductor count |
| Fuel-door release solenoid (never existed, D-098) | 40–120 | `T-032`; output ruled `Q-061` → D-180 |
| Hatch latch switch (broken, K-016) | 50–130 | `T-033` |
| Blower motor — conditional on nothing, the old one is dead (K-023) | from spec | `T-038`; sets O16's fuse (D-126) |
| Washer pump — only if the post-PMU diagnosis condemns it | — | `T-040` → `T-039` (D-176) |
| Aeromotive Phantom 340 in-tank pump — future | — | O5 already sized for it |
| Radar subsystem sensors | — | `V-061` / Z-002 design first |
| Window regulators, switches, relays — if power windows ever happen | 200–520 | bridge is provisioned (D-131); detail archived in `99-ARCHIVE/DEFERRED-FEATURES.md` |

## 8 · Wave 5 — lighting & body, the second pass · ~$400–980 + body

**Deferred until the electrical rebuild is shaken down (L-004, D-201).**
Design: [`TAIL-LIGHTS.md` (archived)](../../../99-ARCHIVE/2026-08-31_lighting-body/TAIL-LIGHTS.md). This was always last money; it no
longer competes with the wire order or the panel parts.

| Item | Qty | ~$ | Note |
|---|---|---|---|
| DOT/SAE LED modules, red and white | 2 sets | 80–200 | `V-064`, `T-037` |
| Tail light housings — fabrication, sealed, stock mounting | 2 | 60–150 | TL-6, TL-13 |
| Tail light driver PCBs, 2 + spares, two revisions likely | 2+ | 60–120 | D-111 |
| Headlamp units — DOT rectangular LED, or 7-inch round with a rectangular element | 2 | 120–300 | `Q-048` |
| Headlamp adapter plates | 2 | 20–60 | Only if a 4×6 goes in a round bucket |
| LED bulbs — park, marker, plate, interior, glovebox, luggage, illumination | ~20 | 60–150 | Unconstrained by bulb-out (D-047) — buy on light and colour |
| **Lighting subtotal** | | **~$400–980** | |
| Body — rust, paint, trim, seals | | **not scoped** | K-007 survey first |

Every wire, connector, channel and soft fuse is already in Waves 0–2 — the
lighting pass changes only what is *in* the socket, then re-sets the lamp
soft fuses from measurement (D-122, L-003;
[`../04-BUILD/MIGRATION-LOG.md`](../04-BUILD/MIGRATION-LOG.md) §Second pass).

## 9 · Re-order reference — part numbers and sources (was `BUY-LIST.md`, D-200)

The first order and what came of it is D-140. Prices move; the part numbers
are what matter. Links checked 2026-08.

**Clamp meter — UNI-T UT210E.** DC current at 2.000 A (1 mA resolution),
20.00 A and 100.00 A ranges, true RMS. The 1 mA resolution reads parasitic
draw directly; it will not read cranking current — the cranking check
(Checklist 3.17) is a voltage-drop test, so that does not matter.

**Teensy 4.1.** Adafruit announced January 2026 it is discontinuing Teensy
sales, SparkFun becoming the exclusive distributor — a distribution change,
not an end-of-life, but single-channel distribution is a real supply risk for
a 2027–28 project, which is why three were bought. `V-059` re-checks
availability before the carrier boards commit.
PJRC: https://www.pjrc.com/ · Amazon: https://www.amazon.com/PJRC-Teensy-4-1-with-Pins/dp/B08CTM3279
Buy **with pins**: breadboard-ready, all three CAN controllers on the outer
rows, and standard male headers plug into the carrier's 0.1″ female sockets
(D-084) without blocking the PSRAM pads (D-170). Use standard female headers
on the carrier — square pins damage machined round-pin sockets.

**CAN transceivers.** SN65HVD230 modules (5 in hand) are **desk parts** —
solder their header pins on first. D-085 specifies TCAN1042/1051 for the car:
automotive-qualified, VIO pin, bus-fault protection past ±12 V.
5-pack: https://www.amazon.com/AITRIP-SN65HVD230-Transceiver-Communication-Arduino/dp/B0GVD5LM42

**Sicma 39-position housing.** Ballenger Motorsports **CONN-101139**, 39-way
SICMA 1.5/2.8 for ECUMaster EMU & PMU, ~$12; FCI/Delphi **211PC399S0020**.
https://www.bmotorsports.com/shop/product_info.php/manufacturers_id/9/products_id/5168
The mixed 1.5/2.8 layout is what makes this the PMU part — a generic 39-pin
with uniform terminals is a different connector.

**Terminals** — ordered separately; Ballenger stocks all three. The pinout
doc v1.2/1.3 gives the 1.5 mm terminal 14–17 AWG (not v1.0's 13–17); it does
not change the 16 AWG signal-wire decision (D-027).

| Size | Part | Wire | Per housing |
|---|---|---|---|
| 1.5 mm | 211CC2S2160P | 14–17 AWG | 27 |
| 2.8 mm | 211CC3S2120 | 14–16 AWG | few |
| 2.8 mm large | 211CC3S3120 | 10–12 AWG | 12 |

**The three housings** (`T-025` → D-135): #1 from the PMU box — the car,
terminated once, never reopened (D-004) — with 12 of 16 large and 27 of 27
small terminals, **zero small spares**; #2 purchased — the diag/config
pigtail; #3 purchased — untouched spare. Three covers the build, the pigtail
and one mistake; the Wave 1 terminal order (`T-044`) lands before the real
housing is terminated.

**The CAN termination trap.** CAN1 on the PMU has **no internal
termination** — connect the USB-to-CAN adapter without 120 Ω at both ends
and the client will not see the device. CAN2 has software termination at the
PMU end; the far-end physical 120 Ω lives at the engine-bay drop (D-079).

## 10 · Deletions that saved money

| Removed | Saved | Decision |
|---|---|---|
| USB-to-CAN adapter — came with the PMU | 169 | V-018 → closed, in the box |
| Full plywood bench mule | ~140 | D-141 |
| Separate PMU bench phase — breadboards, pot, toggle switches, bench bulb, hookup wire | ~40 | D-194 |
| AMPSEAL housings and contacts — all Deutsch now | ~150 | D-052, D-070 |
| Load resistors for LED bulb-out — bulb-out dropped | ~80 | D-047 |
| 6 relay sockets — bank shrank 16 → 10 | ~40 | D-065, D-067 |
| Cruise, rear wiper, power antenna, headlight cleaner wiring | ~60 | D-097 |
| Cigarette lighter circuit | ~20 | D-095 |
| Window motors, switches and door harness — manual windows (bridge provisioned) | ~120 | D-131 |
| Lighting — deferred to Wave 5, not deleted | 400–980 | D-123 → D-201 |

## 11 · Order manifest — the expedited one-teardown buy (D-202, D-203)

Waves 0 + 1 + 2 as five carts, consolidated by store. Prices are estimates
from 2026-08 listings — **every line is a `V` until it sits in a cart at a
live price** (V-089 … V-096 in `OPEN.md`). Wave 3 stays parked (D-081/D-194);
its Digi-Key/Mouser order picks up the wake-network semiconductors' spares
later if any Amazon kit disappoints.

| # | Store | What | ~$ |
|---|---|---|---|
| 1 | [WireBarn](https://www.wirebarn.com/GXL-Wire-By-The-Foot_c_4.html) — GXL by the foot, solid **and striped** | All harness wire, per the §11c colour table | 550–900 |
| 2 | [DeutschConnector.com](https://www.deutschconnector.com/) — genuine Deutsch, per-housing assembly kits | Every housing (both halves), contacts +30 %, wedgelocks, dust caps, clips, boots | 450–650 |
| 3 | Amazon | Power backbone (Blue Sea), battery box, 2 AWG, crimpers, label system, tools, consumables, small electronics | 950–1,300 |
| 4 | [Waytek](https://www.waytekwire.com/) | Independent-feed ATC fuse blocks, relays + sockets, busbars, ring terminals/ferrules | 150–260 |
| 5 | [Ballenger](https://www.bmotorsports.com/) + [ECUMaster USA](https://ecumasterusa.com/products/8-position-can-keyboard) | FCI terminals (the §9 part numbers) · ECUKB8 keypad $369 | 410–450 |
| | **Expedited buy total** | Waves 0–2 in hand | **~2,500–3,550** |

Within the Wave 0–2 estimate (~$2,850–4,825). The wire line runs over its old
figure (margin + striped premium); the fuse-block and crimper lines run under.

### 11a · Order 1 — WireBarn (wire)

GXL by the foot so the D-016 base+tracer scheme is bought exactly, no
60-spool absurdity. Fallbacks for any missing combo: [Crimpzone striped GXL
packs](https://www.crimpzone.com/16-gxl-striped-wire/) ·
[CE Auto Electric 16 GXL solid, $0.32/ft](https://ceautoelectricsupply.com/product/16-awg-gxl-sold-by-the-foot/).
`V-089` — confirm each striped combo exists before substituting.

Also in this order: **10 AWG BLK 25 ft** (pin 25 + star-node drops) and, if
stocked, 15 ft 2-core shielded 16 AWG for the tach (`V-047` — else Amazon).

### 11b · Order 2 — DeutschConnector.com (every Deutsch part, genuine)

Per-housing **assembly kits** (housing + wedgelock + contacts in one line)
for the §9/`CONNECTORS.md` schedule: 15 leg housings ×2 halves, D1/D2 ×2,
DP-ICU, DP-DCU, DP-DIAG, DP-KEY ×2 halves — 24 mated pairs (e.g.
[DT06-12S kit](https://www.deutschconnector.com/products/deutsch_connectors/deutsch_dt_series_connectors/deutsch_dt_12-way_connectors/DT06-12SA-Assy/)).
Plus: solid contacts to **+30 % spare** (D-202, up from 20 %), size-16 and
size-12; dust caps ~8; mounting clips `1027-003-1200` ×19 (`V-090` — here or
TE/Mouser); 180°/90° backshells and boots where stocked; one spare DT-12 and
one spare DTP-4 pair against teardown surprises.
**Crimpers ride in Order 3:** iCrimp IWD-16 + IWD-12 pair (~$80 both), 4-way
indent for solid/stamped contacts — accepted only through the coupon
pull-test protocol, Checklist 1.10–1.11 (`V-096`). Genuine HDT-48-00 (~$300)
is the upgrade if coupons fail.

### 11c · The wire table — order these lengths (1.5× margin, 25 ft floor, D-202)

| AWG | Colour | Order ft | | AWG | Colour | Order ft |
|---|---|---|---|---|---|---|
| 12 | RED (solid) | 75 | | 16 | GRY (solid) | 250 |
| 12 | RED/WHT | 100 | | 16 | GRY/BRN | 100 |
| 12 | RED/BLK · /BLU · /BRN · /GRN · /GRY · /ORN · /PNK · /VIO · /YEL | 25 each (225) | | 16 | GRY/BLU · /ORN · /VIO | 75 each (225) |
| 14 | ORN/BLK · /BLU · /BRN · /GRN · /PNK · /RED · /VIO · /WHT · /YEL | 25 each (225) | | 16 | GRY/BLK · /GRN · /PNK · /WHT · /YEL | 50 each (250) |
| 14 | RED + RED/WHT | 25 + 25 | | 16 | GRY/RED | 25 |
| 10 | BLK | 25 | | 16 | BLU/BLK · /BRN · /ORN · /VIO | 50 each (200) |
| 2 | welding cable (Order 3) | ~40 | | 16 | BLU · /GRN · /PNK · /WHT · /YEL | 25 each (125) |
| | | | | 16 | PNK (solid) | 75 |
| | | | | 16 | BLK | 50 |
| | | | | 16 | YEL/BLK · GRN/BLK (CAN2 pair) | 50 each (100) |
| | | | | 16 | YEL · GRN (CAN1 pair) | 25 each (50) |
| | | | | 16 | VIO/GRN · /YEL · /WHT | 50 each (150) |
| | | | | 16 | VIO/BLK · /BLU · /RED · RED/VIO · ORN · ORN/BRN · ORN/GRY · ORN/YEL · RED | 25 each (225) |

**Totals: 12 AWG 400 ft · 14 AWG 275 ft · 16 AWG 1,825 ft · 10 AWG 25 ft ≈
2,525 ft.** Calculated from `connectors.csv` conductor-by-conductor with
route estimates (L1 8 ft · L2 10 ft · L3 5 ft · L4 14 ft · doors/drops 4 ft ·
in-box 1.5 ft); the margin absorbs the unmeasured routes. Cut nothing until
`T-008` strings the real routes.

### 11d · Order 3 — Amazon (backbone, tools, consumables)

**Power backbone — the not-economised lines (D-062, D-203a):**

| Item | Part | ~$ |
|---|---|---|
| Class-T fuse block, 110–200 A | **Blue Sea 5007100** ([product](https://www.bluesea.com/products/5007100/Class_T_Fuse_Block_with_Insulating_Cover_-_110_to_200A)) | 70–95 |
| Class-T fuse 150 A ×2 (one spare) | **Blue Sea 5114** ([product](https://www.bluesea.com/products/5114/)) | 80–110 |
| Master disconnect | Blue Sea 9003e m-Series | 55–80 |
| Distribution post | Blue Sea 2105 PowerPost | 25–40 |
| MRBF terminal fuse holder + fuse (starter feed) | Blue Sea 5191 + 200 A MRBF (`V-094` rating) | 35–55 |
| Battery box, Group 24–31 | **NOCO HM318BKS** (`V-093` — Ionic Group-25 case fit; the HM426 named earlier is a dual-6V box) | 40–55 |
| Hold-down, backing plate stock, M8 grade-8 hardware | generic | 50–90 |
| 2 AWG fine-strand welding cable, ~25 ft red + 15 ft black | EWCS / TEMCo class (`V-095`) | 90–130 |
| Tinned closed-barrel lugs 2 AWG (5/16 + 3/8) ×10 + boots | TEMCo/Selterm | 30–45 |
| Hydraulic lug crimper | TEMCo TH0006 class | 55–70 |

**Tools and the label system (D-203c/d):**

| Item | Part | ~$ |
|---|---|---|
| Deutsch 4-indent crimpers, size 16 + size 12 | iCrimp IWD-16 + IWD-12 (`V-096` — coupon pull-tests are the acceptance gate) | 75–95 |
| Open-barrel crimper for the FCI terminals | **hold for `V-069`** — die check against a real 211CC terminal first (candidates: Astro 9477, iCrimp open-barrel set) | 60–120 |
| Label printer, prints on heat-shrink | **Brother PT-E300VP** + HSe-211 (~6 mm) + HSe-221 (~9 mm) cartridges ×2 each (`V-092` sleeve-to-wire fit) + 1 TZe laminated for the plate | 170–230 |
| Heat gun | any 1500 W dual-temp | 25–35 |
| Wire strippers 10–22, flush cutters, needle-nose | Klein/Knipex-class | 60–90 |
| Soldering iron + solder | Pinecil/Hakko-class | 35–60 |

**Consumables and small electronics:**

| Item | ~$ |
|---|---|
| Adhesive-lined heat shrink assortment (3:1, incl heavy-wall for lugs) | 35–55 |
| Tesa 51608 ×5 rolls | 25–40 |
| Split loom / abrasion sleeve assortment + grommet kit + P-clips | 80–130 |
| Inline ATO holder (first power-up, D-145) + blade fuse spares | 20 |
| 8-position barrier terminal strip (wake network) ×2 | 15 |
| E24 1 % metal-film resistor kit · 120 Ω ¼ W ×10 · 1N5819 ×20 · 1N4007 ×20 · PNP (2N2907-class) ×5 | 35–50 |
| microSD ×2 · paint pen backup · cavity wax/corrosion spray | 30–45 |
| 3 mm (0.125″) aluminium sheet for backer + sill plates — Amazon or local metal supplier; cut only after `T-007` | 40–80 |

### 11e · Order 4 — Waytek (distribution hardware)

| Item | Part | ~$ |
|---|---|---|
| **Independent-feed ATC fuse blocks ×3** (12 plate positions, six sources — D-203b; a bussed 12-way cannot do this) | OptiFuse BLR-I-504 class (`V-091`) | 30–60 |
| Sill fuse holders F8/F9/F14 | 3 × sealed inline or 2-pos block | 15–25 |
| Mini ISO relays 40 A SPDT **with diode** ×7 (K1, K2, K11, K12 + 3 spare) | Song Chuan / Picker | 40–70 |
| Panel-mount relay sockets ×10 + sill sockets ×4, with terminals | matching series | 55–90 |
| Busbars — always-hot + ground (150 A class, covered) | Blue Sea 2301-class or Cole Hersee | 45–70 |
| Ring terminals, ferrules, misc assortment | | 25–40 |

### 11f · Order 5 — Ballenger + the ECUMaster direct line

| Item | Part | ~$ |
|---|---|---|
| Spare 1.5 mm FCI terminals ×20 (`T-044` — practice crimps before any real one, D-194) | 211CC2S2160P (§9) | 20–40 |
| Spare 2.8 mm terminals ×6 | 211CC3S2120 / 211CC3S3120 (§9) | 10–15 |
| CAN keypad, 8-position | **ECUMaster ECUKB8, $369, ECUMaster USA direct** — Ballenger stocks only the 6/12-button | 369 |

Place all five in one sitting (`T-053`). Anything out of stock: substitute
only within the same class — never on the Class-T, the contacts, or the
crimper acceptance tests.

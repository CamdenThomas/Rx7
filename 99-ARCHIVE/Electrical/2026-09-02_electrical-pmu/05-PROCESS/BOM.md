# BOM — the money, in purchase order

*Rev 2026-09-01 (D-196, D-200) · owns: the money — every purchasable line, organised by wave in the order things are bought and installed. **This is the only shopping page in the tree.** Part numbers and sources for re-orders are §9's (`BUY-LIST.md` absorbed here, D-200); housing part numbers are [`../02-HARNESS/CONNECTORS.md`](../02-HARNESS/CONNECTORS.md)'s.*

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
| 2 · the build (backbone → panel → legs) | 2,500–4,300 | **none for the order** (D-202) — the tape session now gates *cutting*, not buying |
| 3 · module era | 510–1,170 | `V-057`, carrier layouts, `V-084`/`V-085` |
| 4 · deferred / conditional | 210–550+ | their own designs |
| **Electrical remaining** | **~3,300–6,100** | |
| **ELECTRICAL PROJECT TOTAL** | **~6,250–9,450** | |
| 5 · lighting & body + the control panel (second pass) | 770–1,580 + body unscoped | shakedown done (L-004); panel per D-210 |

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

## 3 · Wave 0 — **folded into Order 3** (D-208)

Never bought locally. All three ride in the Amazon cart rather than waiting
on a hardware-store trip.

| Item | ~$ | For | Where |
|---|---|---|---|
| Inline ATO holder | 6 | First power-up protection (D-145) | Order 3 — 2-pack, carted |
| 2 × microSD card | 22 | Firmware stage 6 now; the DCU later | **add by hand** — the listing refused to cart |
| 120 Ω 1 % ¼ W resistors ×100 | 5 | CAN termination — the client never connects without them | Order 3 — carted |

## 4 · Wave 1 — one small cart · ~$20–45

Nothing gates it, and nothing is crimped before it lands (D-194).

| Item | ~$ | For |
|---|---|---|
| Spare 1.5 mm FCI terminals **211CC2S2160P** ×15 minimum | 15–40 | `T-044` — zero small spares exist; **three practice crimps are pull-tested before any real one** (D-194) |
| Coupon wire offcuts, 14–17 AWG | ~5 | The practice crimps |

## 5 · Wave 2 — the build, in install order · ~$2,500–4,300

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

### 5b · Panel build (Phase 4) · ~$520–950

| Item | Qty | ~$ | Note |
|---|---|---|---|
| Backer plate, standoffs, hardware | — | 60–120 | sized by `T-007` / `Q-014` |
| Micro relays, 30/40 A, with diode | 5 + 2 spare | 40–70 | K1, K2, K11, K12 on the plate (D-182, D-186); K9 in the engine bay (D-148) |
| Relay sockets, panel-mount | 10 | 50–90 | 4 populated, 6 spare (D-186) |
| Fuse blocks — **grouped by source** (D-206, `V-091 → D-206`): 1 × 4-pos + 3 × 2-pos bussed + 2 sealed inlines | 6 | 25–50 | **11 positions used** (F15 exciter, D-198; F4 deleted with the A/C, D-211); every block single-source |
| Fuses, assorted + spares | — | 15 | |
| Busbars — always-hot and ground | 2 | 90–140 | |
| Wake network: 8-pos terminal strip, 1N5819 ×8, 1N4007 ×5, 2 × PNP + 220 kΩ, 10 kΩ bleed, 100 kΩ bias ×2 | — | 40–70 | D-167, D-188, D-189, D-190 |
| E24 1 % resistor assortment | 1 kit | 15 | every ladder value (LADDERS.md) |
| Soldering iron + solder + heat-shrink | — | 30–70 | first used here |
| Wire strippers 10–22 AWG, flush cutters, needle-nose | — | 35–55 | |
| Label printer + heat gun | — | 40–90 | |
| 120 Ω terminator + DTM-04-4P diag port pair | — | 20 | wire DP-DIAG early (D-194 — the laptop lives in the car) |
| Open-barrel crimper, 1.5 + 2.8 mm dies | 1 | 60–150 | **`V-069` die check against a real terminal first** |
| ~~CAN keypad, 8-key~~ | — | **0** | **Deleted, D-210** — moves to Wave 5 with the custom A/C panel |

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
Design: [`TAIL-LIGHTS.md` (archived)](../../../99-ARCHIVE/Electrical/2026-08-31_lighting-body/TAIL-LIGHTS.md). This was always last money; it no
longer competes with the wire order or the panel parts.

| Item | Qty | ~$ | Note |
|---|---|---|---|
| DOT/SAE LED modules, red and white | 2 sets | 80–200 | `V-064`, `T-037` |
| Tail light housings — fabrication, sealed, stock mounting | 2 | 60–150 | TL-6, TL-13 |
| Tail light driver PCBs, 2 + spares, two revisions likely | 2+ | 60–120 | D-111 |
| Headlamp units — DOT rectangular LED, or 7-inch round with a rectangular element | 2 | 120–300 | `Q-048` |
| Headlamp adapter plates | 2 | 20–60 | Only if a 4×6 goes in a round bucket |
| LED bulbs — park, marker, plate, interior, glovebox, luggage, illumination | ~20 | 60–150 | Unconstrained by bulb-out (D-047) — buy on light and colour |
| **Custom A/C / control panel** — absorbs defog, hatch release and fuel-door release (D-210); the DP-KEY drop is already wired and capped | 1 | 370–600 | CAN keypad, DCU faceplate or custom board — the panel design decides |
| **Lighting + panel subtotal** | | **~$770–1,580** | |
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
| **A/C — the system, not just the wiring.** Electrically it saves almost nothing: one fuse (F4), one factory relay (K10) and a chain that never entered a leg. What it avoids is the **$470–1,150 R-12 recharge or $600–1,150 R-134a retrofit** that would have bought one partial summer on an engine with a swap date. Removal itself costs $50–120 for refrigerant recovery (`T-054`) | ~5 electrical · **$470–1,150 avoided** | D-012 → D-211 |

## 11 · Order manifest — the expedited one-teardown buy (D-202, D-203)

Waves 0 + 1 + 2 as four carts plus wire, consolidated by store. Prices are estimates
from 2026-08 listings — **every line is a `V` until it sits in a cart at a
live price** (V-089 … V-096 in `OPEN.md`). Wave 3 stays parked (D-081/D-194);
its Digi-Key/Mouser order picks up the wake-network semiconductors' spares
later if any Amazon kit disappoints.

**Carts loaded live 2026-09-01 (D-207).** Every figure below is a real cart
subtotal, not an estimate — the `V` lines close as each cart is paid.

| # | Store | What | Estimate | **Cart** |
|---|---|---|---|---|
| 1 | [WireBarn](https://www.wirebarn.com/GXL-Wire-By-The-Foot_c_4.html) — GXL by the foot, solid **and striped** | All harness wire, per the §11c colour table | 550–900 | **not built** — Cloudflare blocks the agent browser; Camden drives this one, or the Crimpzone / CE Auto fallbacks |
| 2 | [DeutschConnector.com](https://www.deutschconnector.com/) — genuine Deutsch, per-housing assembly kits | 34 lines / 212 pieces: every housing (both halves), solid contacts +30 %, wedgelocks, clips, removal tools, boots, caps · **D2 14 AWG pair added** (D-208) | 450–650 | **1,281.18** — over; see §11h |
| 3 | Amazon | 48 lines: power backbone (Blue Sea), battery box, 2 AWG, crimpers, label system, tools, consumables, electronics · Wave 0 folded in (D-208) · **switches** (D-209) | 1,000–1,500 | **1,560.95** |
| 4 | [Waytek](https://www.waytekwire.com/) | 7 lines: 4 × 4-pos fuse blocks (D-206), micro relays + sockets, 5 sealed inlines, busbars, **K9 sealed mini + weatherproof connector** (D-208) | 150–260 | **170.13** |
| 5 | [Ballenger](https://www.bmotorsports.com/) | 23 SICMA terminals. **ECUMaster cart emptied — ECUKB8 deleted (D-210)** | 410–450 | **11.37** |
| | **Four carts loaded** | wire + 2 microSD still to add | | **3,023.63** |
| | **Projected all-in** | + wire at estimate | ~2,550–3,750 | **~3,570–3,920** |

Within the Wave 0–2 estimate (~$2,500–4,300). The wire and Deutsch lines
run over their old figures (margin, striped premium, and assembly kits at
both halves); the fuse-block, crimper and keypad lines run under — the last
of those to zero (D-210).

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
TE/Mouser); **DT removal/wedge tools, size 16 + size 12, ×2 each** (Checklist
1.12 practises extraction; 8.11 keeps one in the car); 180°/90° backshells and
boots where stocked — out-of-stock boots do not hold the order; one spare DT-12 and
one spare DTP-4 pair against teardown surprises. **D2 gap fixed 2026-09-01
(D-208):** D1 *and* D2 each carry two 14 AWG window-motor legs, so the
14 AWG DT-8 kit is ×2, not ×1 — the first pass carted one.
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
| 2 | welding cable (Order 3) | ~55 | | 16 | BLU · /GRN · /PNK · /WHT · /YEL | 25 each (125) |
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
| LiFePO4-profile charger — the battery sits until winter, and a lead-acid charger can ruin it (BATTERY-INSTALL §7) | **Ionic 12 V 10 A** — skip this line if a lithium-profile charger is already owned | 0 or 90–130 |
| Hold-down, backing plate stock, M8 grade-8 hardware · **3⁄8 stainless ground studs + star washers** (BATTERY-INSTALL 3.8) · **PMU standoffs** (PANEL-LAYOUT §7 airflow) | generic | 65–110 |
| 2 AWG fine-strand welding cable, **~35 ft red + 20 ft black** — covers the dash feed *and* the rear→starter run BATTERY-INSTALL lists separately (its “length as measured” gates cutting, not buying — D-202) | EWCS / TEMCo class (`V-095`) | 120–170 |
| Tinned closed-barrel lugs 2 AWG (5/16 + 3/8 assorted) **×18** + boots — every cable end plus hydraulic practice crimps; `V-053`: eyeball the battery posts before finalising hole sizes | TEMCo/Selterm | 40–60 |
| Hydraulic lug crimper | TEMCo TH0006 class | 55–70 |

**Tools and the label system (D-203c/d):**

| Item | Part | ~$ |
|---|---|---|
| Deutsch 4-indent crimpers, size 16 + size 12 | iCrimp IWD-16 + IWD-12 (`V-096` — coupon pull-tests are the acceptance gate) | 75–95 |
| Pull-test scale — Checklist 1.11 says *record the force*; this records it (`V-096`) | any digital hanging scale, 0–50 kg | 15–25 |
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
| Split loom / abrasion sleeve assortment + grommet kit + P-clips · **pull string, 100 ft** (D-064 — goes in beside the tunnel run) | 85–140 |
| Inline ATO holder (first power-up, D-145) + ATO fuses **by explicit value** — **2 A ×4 and 7.5 A ×4** (F2 and F15; cheap assortments skip both) plus 5/10/15/30 A ×6 each | 25–35 |
| 8-position barrier terminal strip (wake network) ×2 | 15 |
| E24 1 % metal-film resistor kit · **100 Ω 1 % 1 W ×4** — the A7 fuel-sender pull-up (D-197; kits are ¼ W and do not cover it; alt 2 × 200 Ω ½ W in parallel per point) · 120 Ω ¼ W ×10 · 1N5819 ×20 · 1N4007 ×20 · PNP (2N2907-class) ×5 | 38–55 |
| microSD ×2 · paint pen backup · cavity wax/corrosion spray | 30–45 |
| **Switches (D-209 — everything but the column combination switch is replaced).** Wink L/R: mxuteuk 16 mm **SPDT momentary 1NO+1NC** ×5 (2 used, 3 spare) — the NC pole crosses into the opposite K1/K2 coil, the NO pole feeds the wake strip, so a plain pushbutton will not do · brake pedal switch, RX-7 1982 no-cruise · door-pin plunger switches ×6 (doors ×2, glove box lamp, luggage, hatch, spare) · power-window momentary rockers ×2 (D-131 provision, fitted whenever the motors come). Full schedule: [`../01-DESIGN/SWITCHES.md`](../01-DESIGN/SWITCHES.md) | 45 |
| 3 mm (0.125″) aluminium sheet for backer + sill plates — Amazon or local metal supplier; cut only after `T-007` | 40–80 |

### 11e · Order 4 — Waytek (distribution hardware)

| Item | Part | ~$ |
|---|---|---|
| **Fuse blocks — 4 × 4-position, one per source** (D-206, `V-091 → D-206`; carted at 4-pos rather than the 2-pos of D-206 — same money, **6 spare fused positions on live sources**, which is the luxury-package headroom, D-208) | OptiFuse **BLR-504**, Waytek 45643, $9.93 ea | 40 |
| Sealed inline ATO holders ×5 — F12 (O20) · F15 (O12) · sill F8/F9/F14 | Waytek **46047**, $7.17 ea | 36 |
| **ISO micro** relays 40 A SPDT **with diode** ×6 — K1, K2, K11, K12 + 2 spare (D-208: K9 is no longer on this line) | Song Chuan **871-1C-C-D1-12VDC**, Waytek 75725, $2.59 ea | 15 |
| **K9 start relay — SEALED mini ISO w/ diode ×2** (one spare). Engine bay, inner fender (D-148): micro has no weatherproof housing, mini does (D-208) | Picker **PC792E-1C-C-12S-DN-X**, Waytek 74858 | 12 |
| **K9 weatherproof connector ×2** | Chief **75340**, 5-pin harness mount | 10 |
| Panel-mount micro sockets ×10 + sill sockets ×4, with terminals | Waytek **75290**, $1.32 ea | 19 |
| Busbars — always-hot + ground | Blue Sea **2301** 10-gang 150 A, Waytek 78250, $24.48 ea | 49 |
| | | **cart 170.13** |

### 11f · Order 5 — Ballenger

| Item | Part | ~$ |
|---|---|---|
| Spare 1.5 mm FCI terminals ×20 (`T-044` — practice crimps before any real one, D-194) | SICMA 1.5 female, 16–14 AWG (§9: 211CC2S2160P) | 9.89 |
| Spare 2.8 mm terminals ×3 | SICMA 2.8 female, 16–14 AWG (§9) | 1.48 |
| | | **cart 11.37** |

**No ECUMaster line (D-210).** The ECUKB8 is deleted and its cart emptied —
defog, hatch release and fuel-door release wait and integrate into the
custom A/C panel. The `DP-KEY` drop is still built and capped, so that
panel is a plug-in whenever it is designed.

### 11i · The luxury-package line (D-208)

Digital A/C, LED lighting, heated seats and the rest move to a **separate
luxury-package project.** What that changes here — and, mostly, what it
does not:

| Thing | In this order? | Why |
|---|---|---|
| **HVAC servos ×4** | **No** — and never were | Wave 3, parked (D-081). Nothing A/C-actuating is in any cart |
| **CAN keypad (ECUKB8)** | **No — deleted (D-210)** | Camden: no ECUMaster button controls at all. Defog, hatch release and fuel-door release wait and integrate into the custom A/C panel. **The `DP-KEY` drop is still built and capped** — CAN2 + switched 12 V + ground — so the panel is a plug-in, not a rewire. −$369 |
| **DP-DCU connector pair** | Yes, ~$40 | The climate module's drop. Kept because it is a **dash-post drop** — adding it later is a panel-off job, but the CAN2 splice at the post is cut during Phase 4. Cheaper to land it now and cap it |
| **F10 / F11 comfort bus** | Position only | Already "LIVE position, loads deferred" (SPEC §3). The heated seats land on these when the luxury package starts |
| **F14 mirror heat, D1/D2 cav 4–7** | Provisioned, capped | Already DEFERRED (Q-062 → D-181). Wire and cavities exist; nothing is bought for them |
| **6 spare fused positions** | Yes | The 4 × 4-pos blocks leave 6 spare positions on **live sources** (K11, O1, O15) — that is where luxury-package loads plug in without touching the plate |

**Legs are NOT consolidated, and that is deliberate.** The legs run under
carpet, through the tunnel and behind panels; the box is in the dash. D-202
exists so the interior comes apart *once*. Trimming a DT-8 pair saves ~$50
and costs a weekend when the luxury package wants it back. **The box is
built out full and future-proof; the legs stay full-cavity.** Two findings
came out of checking this anyway:

- **`L2-P2` is a stale-premise shell.** D-115 kept two DTP-4s on L2 because
  reversible pop-ups needed 6 size-12 conductors. D-186 made them
  single-direction — L2-P1 (3 used) + L2-P2 (1 used) is now **4 live
  conductors, which fit one DTP-4.** *Do not collapse it yet:* `V-081` is
  open and a two-winding result puts the sixth conductor straight back.
  Both shells are carted. Revisit after the ohm check.
- **`L3-S3` is the one honest drop.** 8 cavities, 3 used, all three are
  DEFERRED radar links (`V-061` — the subsystem has no design and the
  conductor count is unconfirmed). If radar joins the luxury package, this
  whole housing pair leaves the order (~$50) and L4-S 5/6/7 simply become
  SPARE. The D-064 pull string makes a later radar run pullable without a
  teardown. **Camden's call — not taken.**

### 11h · What the live carts changed (D-207)

**The Deutsch cart is the overrun — $1,241 against a $450–650 estimate.**
The estimate under-counted: it priced housings but not *both halves of 24
mated pairs* at assembly-kit prices with **solid** contacts included, which
is what `CONNECTORS.md` §3 and D-202 actually specify. Nothing in the cart
is wrong; the old number was. Trims, in the order they cost least:

| Trim | Saves | What it gives up |
|---|---|---|
| Stamped contacts instead of solid on the **signal** housings only (DT 12/8/6-way, size 16) | ~250–350 | Stamped are genuine TE and rated the same 13 A; solid are more robust to repeated insertion. Power (DTP) and the diag/keypad drops stay solid |
| Drop the spare DT-12 and DTP-4 pairs | ~55 | The teardown-surprise buffer |
| Contacts at +20 % instead of +30 % (the pre-D-202 number) | ~40 | Margin on ruined crimps — the thing D-202 raised on purpose |
| Skip boots (6 × DT12S-BT-BK, 5 × DT8S) | ~45 | Cosmetic strain relief only |

**Substitutions made live, with reasons:**

| Line | Ordered | Why not the manifest part |
|---|---|---|
| Class-T block | Blue Sea **5007100**, $78.47 | as specced — no featured offer, bought from 4Wheel Online |
| Distribution post | Blue Sea **2003** 3/8, $15.72 | 2105 is not sold on Amazon; 2003 is the same PowerPost family at the 3/8 stud the lugs use |
| MRBF fuse | Blue Sea **5187** 200 A, $16.99 | the 5191 holder's matching fuse — `V-094` still owes the cranking check |
| Battery box | NOCO **BG27** (Group 27), $20.28 | HM318BKS is not listed; BG27 is the current Snap-Top for Group 27–31. **`V-093` now checks the S9 against BG27's interior** |
| Deutsch crimper | **IWISS** solid-contact 12/16/20, $138.99 | one tool covers all three sizes instead of the iCrimp IWD-16 + IWD-12 pair. `V-096`'s coupon pull-test is unchanged and still the gate |
| Label printer | Brother **PT-E310BT**, $166.92 | the PT-E300VP is discontinued; the E310BT is its replacement and takes the same HSe/TZe cartridges |
| HSe-221 | compatible, $23.59 ×2 | Brother genuine 221E is not stocked; the 211E **is** genuine and was bought that way |
| 2 AWG | TEMCo 25R+25B ($144.28) + 20 ft red ($68.53) = **45 red / 25 black** | sold in fixed lengths, not cut-to-order; this is the nearest split above the 35/20 the corrected D-205 figure needs |
| Fuse block | OptiFuse **BLR-504** ×4 (Waytek 45643), $9.93 ea | per D-206 — 4-pos bussed, one per source group |
| Relay | Song Chuan **871-1C-C-D1-12VDC** ×7 (75725), $2.59 ea | ISO micro, SPDT, integral diode — exactly SCHEMATICS §7 |
| Terminals | Ballenger **SICMA 1.5 16-14 AWG** ×20 + **2.8 16-14 AWG** ×3, $11.37 | Ballenger lists SICMA by size and wire range, not by the 211CC part number |

**Still not in any cart:** all harness wire (WireBarn, §11c) · the
open-barrel FCI crimper (held for `V-069`, the die check) · sill fuse
holders F8/F9/F14 (Waytek 46047 ×5 covers them and the two plate inlines) ·
battery hold-down and backing-plate stock (`T-024` sizes it on teardown day).

### 11g · Savings levers — your call, none taken yet (D-205)

| Lever | Saves | What it gives up |
|---|---|---|
| ~~Defer the ECUKB8~~ | — | **Taken and then some (D-210):** the keypad is deleted outright, not deferred. −$369 |
| Wire floors 25 → 15 ft on one-shot tracer colours | ~100–150 | Spare margin on colours used once — one bad cut means waiting on a re-order |
| Generic covered busbars instead of Blue Sea | ~25–40 | Brand pedigree only — hold the same ampacity and cover spec |
| Skip the charger line | 90–130 | Only valid if a lithium-profile charger is already owned |
| **Not on the table** | — | Class-T, MRBF, genuine Deutsch/FCI contacts, crimper acceptance tests (D-062, D-203) |

Place all five in one sitting (`T-053`). Anything out of stock: substitute
only within the same class — never on the Class-T, the contacts, or the
crimper acceptance tests.

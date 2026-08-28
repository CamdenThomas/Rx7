# BOM — Electrical / PMU

All prices are estimates and carry `[VERIFY]` status until checked against a
live quote. Nothing here is ordered.

**Total: $5,230–7,045** (materials only, tools separate)

## 1 · PCU / relay panel — $2,960–3,530

| Item                               | Qty | $           | Status    |
|------------------------------------|-----|-------------|-----------|
| ECUMaster PMU-24 DL                | 1   | 0           | Done      |
| USB-to-CAN adapter                 | 1   | 0           | Done      |
| CAN keypad (8 or 12 key)           | 1   | 300–450     | `[Q-010]` |
| Spare Sicma housing + terminals    | 2   | 60–120      | `[V-018]` |
| Relay sockets                      | 16  | 90–150      |           |
| Micro relays                       | 10  | incl. above |           |
| Fuse block + fuses/breakers        | 13  | 80–140      |           |
| Busbars (power + ground)           | 2   | 90–140      |           |
| Diodes, resistors, terminal strips | —   | 40–70       |           |
| Backer plate, standoffs, hardware  | —   | 60–120      | `[Q-014]` |
| 120 Ω terminators + DTM diag port  | —   | 20          |           |

## 2 · Battery & power backbone — $1,125–1,650

| Item                                     | Qty    | $       | Status |
|------------------------------------------|--------|---------|--------|
| Ionic S9 heated lithium                  | 1      | 0       | done   |
| Class-T fuse + ignition-protected holder | 1      | 110–160 |        |
| Master disconnect                        | 1      | 55–90   |        |
| Battery box / mount fabrication          | 1      | 80–200  |        |
| 4 AWG cable                              | ~25 ft | 90–150  |        |
| Lugs, boots, adhesive shrink             | —      | 60–100  |        |
| Ground studs, star washers, sealant      | —      | 30–50   |        |

## 3 · Harness materials — $1,145–1,865

| Item                                        | Qty          | $       |
|---------------------------------------------|--------------|---------|
| GXL/TXL wire — 12/14/16/18 AWG, 10 colors   | ~1,200 ft    | 380–560 |
| Deutsch DTP housings, contacts, wedges      | 5 pr + spare | 110–180 |
| Deutsch DT 12/8/6 housings, contacts, seals | 6 pr + spare | 220–350 |
| AMPSEAL 23-pos pair + contacts              | 1 pr         | 70–120  |
| DTM-04-4P diag port                         | 1 pr         | 15–25   |
| Adhesive-lined heat shrink assortment       | —            | 70–120  |
| Tesa 51608 cloth tape                       | 5 rolls      | 50–80   |
| Abrasion loom / split conduit               | —            | 60–120  |
| Grommets, bulkhead pass-throughs, P-clips   | —            | 80–150  |
| Ring terminals, ferrules                    | —            | 40–70   |
| Heat-shrink label sleeves + cartridges      | —            | 50–90   |

## 4 · Tools — $600–1,200 (separate, one-time)

Deutsch open-barrel crimper · AMPSEAL crimper · hydraulic lug crimper ·
DMM with DC clamp · label printer · heat gun · pick set

## Not in this BOM

DCU/MCU, digital cluster, A/C controller, LS swap hardware, audio components,
LED lamp conversion, heated seat elements `[Q-012]`.

---

## PURCHASED — 2026-08

| Item | Status |
|---|---|
| **ECUMaster PMU-24 DL** | **Bought** |
| **Ionic S9 lithium battery** | **Bought** |

Roughly **$2,750–3,150** of the estimate committed. Remaining materials budget
is approximately **$2,500–3,900**, plus tools if not already owned.

### What this changes

- **V-016 and V-017 close.** No more price uncertainty on the two biggest lines.
- **The PMU is in hand**, so T-020 (confirm cavity geometry against the real
  part) and T-021 (inventory the connector kit) are now possible and cheap.
- **The bench mule is unblocked.** Checklist Phase 2 — steps 036–062 — needs the
  PMU, a spare housing, a USB-to-CAN adapter and a plywood board. That is the
  entire configuration phase, 35–55 hours, and none of it requires the car, the
  shop, or the meter.

### Next spend, in order

| Priority | Item | ~$ | Unblocks |
|---|---|---|---|
| 1 | DMM with DC clamp | 40–60 | T-014, T-015, T-016 — everything measurement-based |
| 2 | USB-to-CAN adapter (if not in the PMU box) | 169 | Bench mule, Phase 2 |
| 3 | Spare Sicma housing + terminals | 60–120 | Bench mule — **never practise on the real housing** |
| 4 | Deutsch crimper + coupon stock | 80–250 | Checklist 031–033 |
| 5 | Connector and wire order | 1,150–1,900 | Phase 5 — hold until Q-030/Q-031 are answered |

Item 5 is the one to hold. The L3-S count and the door branch are both unresolved,
and ordering housings before those close means ordering the wrong ones.

---

## UPDATE 2026-08 — PMU box contents confirmed

**The PMU shipped with the mating connector kit AND the USB-to-CAN adapter.**

| Line | Was | Now |
|---|---|---|
| USB-to-CAN adapter | $169 | **$0 — included** |
| Mating connector + terminals | assumed included | **Confirmed included** |

`V-018` closed. `T-021` closed.

**Saves ~$169** and, more importantly, **the bench mule is fully unblocked** —
Phase 2 needs only a plywood board, a spare housing, and a Windows machine.

### Revised remaining spend

| Group | Remaining ~$ |
|---|---|
| PCU / relay panel — relays, sockets, fuse block, busbars, plate, keypad | 660–1,090 |
| Battery backbone — tray, Class-T, disconnect, cable, lugs | 520–830 |
| Harness materials — wire, Deutsch, shrink, loom, labels | 1,000–1,700 |
| Tools — crimpers, clamp DMM, label printer | 600–1,200 |
| **Total remaining** | **2,780–4,820** |

Already committed: PMU-24 DL + Ionic S9.

### Buy order — revised

| # | Item | ~$ | Unblocks | Hold until |
|---|---|---|---|---|
| 1 | **DMM with DC clamp** | 40–60 | T-014/15/16 — all measurement | — |
| 2 | **Spare Sicma housing + terminals** | 60–120 | Bench mule. Never practise on the real housing | — |
| 3 | Plywood, ground bus, fused feed for the bench board | 40 | Phase 2 | — |
| 4 | Battery mount hardware — tray, plate, hold-down | 90–180 | Phase 3 | Measure the bin first, T-024 |
| 5 | Class-T, disconnect, PowerPost, heavy cable, lugs | 430–650 | Phase 3 | — |
| 6 | Deutsch crimper + coupon stock | 80–250 | Checklist 031–033 | — |
| 7 | Relays, sockets, fuse block, busbars, backer plate | 360–640 | Phase 4 | Panel envelope, Q-014 |
| 8 | CAN keypad, 8-key | 300–450 | Phase 2 config | — |
| 9 | **Connector and wire order** | 1,000–1,700 | Phase 5 | **Q-030 and Q-031** |

Items 1–3 total under $220 and unblock the largest single phase of work.
Item 9 is the one that must wait — ordering housings before the dash signal
count and the door branch are settled means ordering the wrong ones.

---

## UPDATE 2026-08 — DCU and cluster added (D-075)

| Item | Qty | ~$ |
|---|---|---|
| Teensy 4.1 or STM32G4 dev board | 2 | 60–100 |
| CAN transceivers (TJA1051 / MCP2562) | 3–4 | 15–30 |
| Analog front end — dividers, RC filters, clamp diodes | — | 15–25 |
| Tach conditioning — opto or comparator | 1 | 5–15 |
| 12 V → 5 V automotive buck regulators | 2 | 20–40 |
| Cluster display(s) `[Q-037]` | 1–2 | 60–200 |
| HVAC servos | 4 | 60–120 |
| Oil temperature sender | 1 | 30–60 |
| VSS sensor | 1 | 30–60 |
| Custom PCBs, 2 revisions | 2 | 100–250 |
| Enclosures + cluster bezel fabrication | — | 80–200 |
| DP-DCU (DT06-12S) + DP-ICU (DT06-6S) pairs | 2 | 40–60 |
| 120 Ω CAN terminator, far end | 1 | 2 |
| **Subtotal** | | **517–1,162** |

### Revised project total

| Group | ~$ |
|---|---|
| Committed — PMU + Ionic | 2,750–3,150 |
| PCU / relay panel — now smaller (5 relays in box, 10 sockets) | 600–980 |
| Battery backbone | 520–830 |
| Harness materials — all Deutsch, no AMPSEAL | 1,000–1,700 |
| Sill node — plate, 4 sockets, 2 fuses, door connectors | 80–150 |
| **DCU + ICU** | **517–1,162** |
| Tools | 600–1,200 |
| **Total project** | **6,067–9,172** |

**Remaining to spend: roughly $3,300–6,000.**

### Two things got cheaper

- **AMPSEAL is gone entirely** — everything is Deutsch DT/DTP. One crimper, two
  contact sizes, one supplier.
- **The relay bank shrank** — 16 sockets to 10, five populated. K5–K8 moved to
  the sill, which needs a small plate but a much smaller box.

### Buy order — DCU additions slot in late

| # | Item | When |
|---|---|---|
| 1–3 | Clamp DMM, spare Sicma housing, bench board | **Now** |
| 4–5 | Battery mount, Class-T, disconnect, cable | Before Phase 3 |
| 6 | Deutsch crimper + coupons | Before Phase 4 |
| 7 | Relays, sockets, fuse block, busbars, plate | After Q-014 |
| 8 | CAN keypad | Phase 2a |
| 9 | Connector and wire order | After Q-033 |
| **10** | **MCUs, transceivers, passives** | **Phase 2b — can be bought early and cheaply, they're $100** |
| 11 | Display, servos, senders, PCBs | After the firmware proves out on breadboard |

**Item 10 is worth buying now.** Two dev boards and a handful of transceivers is
about $100, and it lets firmware start during a semester while the car sits.
Item 11 waits — do not order a display before you know what you're driving it with.

---

## MCU and CAN parts — specified 2026-08

Replaces the placeholder "Teensy or STM32" line above.

### Modules

| Item | Qty | Part | ~$ ea | ~$ |
|---|---|---|---|---|
| MCU board | **3** | Teensy 4.1 | 32 | 96 |
| CAN transceiver | 6 | TI TCAN1042 / TCAN1051 `[V-057]` | 3 | 18 |
| Carrier PCB, 2 revisions | 4 | Custom, socketed Teensy | — | 100–250 |
| Teensy socket headers | 3 sets | Machined pin, not stamped | 4 | 12 |

**Buy three boards, not two.** A spare is a spare for either node, and a dead
module mid-debug otherwise stops the project for a week.

### Power supply per module

| Item | Qty | Part | ~$ |
|---|---|---|---|
| Automotive buck 12 V → 5 V | 2 | TPS54331 or a sealed module | 20–40 |
| **TVS, load dump** | 2 | SMBJ33A | 2 |
| Reverse polarity protection | 2 | Schottky or ideal-diode IC | 6 |
| Input filter — inductor + bulk caps | 2 sets | — | 8 |

### ICU analog front end

| Item | Qty | Purpose | ~$ |
|---|---|---|---|
| Precision dividers, 1% | ~12 | Sender scaling | 4 |
| RC filters | 6 | Noise | 3 |
| Clamp diode pairs | 6 | **Every input protected** | 5 |
| Opto-isolator or comparator | 1 | **Tach conditioning** — coil spikes >12 V | 5–15 |
| Schmitt buffer | 1 | VSS pulse cleanup | 3 |

### Bus hardware

| Item | Qty | ~$ |
|---|---|---|
| 120 Ω terminator, engine-bay drop | 1 | 2 |
| Twisted pair, 16 AWG — vehicle bus | as needed | in wire order |
| Twisted pair — **private DCU↔ICU link, capped** | short | 5 |

### Still open

| Item | Blocked by |
|---|---|
| Display(s) | `[Q-037]` — round pair or single wide |
| HVAC servos ×4 | Heater box teardown |
| Oil temp sender, VSS | Sender thread and range |
| Enclosures, cluster bezel | Display choice |

### Module subtotal — revised

| | ~$ |
|---|---|
| MCUs, transceivers, sockets | 126 |
| Carrier PCBs | 100–250 |
| Power supplies + protection | 36–56 |
| ICU analog front end | 20–30 |
| Bus hardware | 7 |
| **Hard parts, specified** | **289–469** |
| Display, servos, senders, enclosures `[open]` | 230–500 |
| **Module total** | **519–969** |

### What to buy right now — $130

Three Teensy 4.1, six transceivers, sockets, and the protection passives.
That is the entire firmware development kit. It lets CAN bring-up, sensor
scaling and display work start on a breadboard during a semester, with no car,
no shop, and no clamp meter.

**Everything else in this section waits** until the firmware proves out what it
actually needs.

---

## SPENT / REMAINING — 2026-08

### Purchased

| Item | ~$ |
|---|---|
| ECUMaster PMU-24 DL — includes connector kit + USB-to-CAN | 2,050–2,250 |
| Ionic S9 heated lithium | 700–900 |
| Bench kit — clamp meter, 3× Teensy 4.1, transceivers, cables, resistors, breadboards, board materials | ~230 |
| 2 × Sicma 39-pos spare housings with pin sets | ~25 |
| **Committed** | **~3,005–3,405** |

### Remaining, in dependency order

| # | Item | ~$ | Waiting on |
|---|---|---|---|
| 1 | Spare terminals | 0–40 | **T-025 stock count** |
| 2 | Battery mount — tray, backing plate, hold-down | 90–180 | T-024 |
| 3 | Class-T, disconnect, PowerPost, **2 AWG** cable, lugs | 450–700 | T-029 terminal type |
| 4 | Deutsch crimper, hydraulic lug crimper, label printer | 220–470 | nothing |
| 5 | CAN keypad, 8-key | 300–450 | nothing |
| 6 | Relays ×11, 10 sockets, fuse block, busbars, backer plate | 350–620 | **T-007 dash envelope** |
| 7 | Sill plate, 4 sockets, 3 fuses, ground stud | 80–150 | T-028 sill space |
| 8 | **Wire and connector order** | 1,000–1,700 | **T-008 routes** |
| 9 | New mirrors — larger, heated, digital | 150–400 | T-031, V-060 |
| 10 | Fuel-door solenoid + hatch latch switch | 60–150 | T-032, T-033 |
| 11 | Module hard parts — carrier PCBs, power supplies, analog front end | 160–340 | firmware proves the design |
| 12 | Display, servos, senders, enclosures | 230–500 | Q-037, firmware |
| | **Remaining** | **3,090–5,700** | |

### Project total

**~$6,100–9,100.** About a third committed.

### Deletions that saved money

| Removed | Saved |
|---|---|
| USB-to-CAN adapter — came with the PMU | 169 |
| AMPSEAL housings and contacts — all Deutsch now | ~150 |
| Load resistors for LED bulb-out — bulb-out dropped | ~80 |
| 6 relay sockets — bank shrank 16 → 10 | ~40 |
| Cruise, rear wiper, power antenna, headlight cleaner wiring | ~60 |
| Cigarette lighter circuit | ~20 |

---

## UPDATE 2026-08 — wedgelocks, accessories, and new sourcing

### BOM GAP CLOSED — secondary wedgelocks

**These were missing and they are required.** Every DT-family connector needs one
per half, sold separately. A connector without one will not retain contacts.

| Item | Qty | ~$ |
|---|---|---|
| W12S / W12P — 12-way | 5 pr | 25 |
| W8S / W8P — 8-way | 5 pr | 22 |
| W6S / W6P — 6-way | 2 pr | 8 |
| W4S / W4P — 4-way | — | — |
| W2S / W2P — 2-way | 1 pr | 4 |
| WP-4S / WP-4P — DTP 4-way | 4 pr | 20 |
| WP-2S / WP-2P — DTP 2-way | 1 pr | 5 |
| WM-4S / WM-4P — DTM 4-way | 2 pr | 8 |
| **+20% spare** | | 18 |
| **Subtotal** | | **~110** |

### Accessories worth adding

| Item | Qty | ~$ | Why |
|---|---|---|---|
| **Mounting clips** `1027-003-1200` | ~16 | 30–50 | Panel-mount the receptacles at the dash post. The intended method |
| Backshells, 180° and 90°, with strain relief | ~8 | 60–120 | Tunnel and firewall runs where bend radius matters |
| Boots | ~10 | 30–60 | Strain relief and a finished look |
| Dust caps | ~6 | 15–25 | Capped spares and the unmated diagnostic port |
| `-C015` reduced-diameter seals | if needed | — | Only if 16 AWG seals loosely on the bench |

**Connector accessories subtotal: ~$245–365** on top of the housings and contacts.

### New line items from round four

| Item | Qty | ~$ | Note |
|---|---|---|---|
| **IMU** — accelerometer/gyro for the ICU board | 1 | 5 | D-109 |
| **Tail light driver PCB** | 2 + spares | 60–120 | D-111. Two revisions likely |
| **DOT LED modules** — red and white | 2 sets | 80–200 | `[V-064]` |
| **Tail light housings** — fabrication | 2 | 60–150 | Sealed, stock mounting |
| **Headlamp units** — DOT rectangular LED | 2 | 120–300 | `[Q-048]` |
| **Headlamp adapter plates** | 2 | 20–60 | Only if 4×6 in a round bucket |

**Round four additions: ~$345–835.**

### Revised project total

| Group | ~$ |
|---|---|
| Committed | 3,005–3,405 |
| Connector accessories — **newly identified** | 245–365 |
| Lighting — tail and head, **newly scoped** | 345–835 |
| Everything else remaining | 3,090–5,700 |
| **Project total** | **~6,700–10,300** |

The lighting and connector-accessory lines are the reason this moved. Neither
was in the earlier estimate.

---

# SCOPE CHANGE 2026-08 — lighting removed (D-123)

**~$345–835 of lighting moves to `02-PROJECTS/lighting-body/`:**
DOT LED modules · tail light housings · driver PCBs · headlamp units · adapter
plates · LED bulbs throughout.

**The IMU stays** — it's on the ICU carrier board, not a lighting item.

## Revised project total

| Group | ~$ |
|---|---|
| **Committed** — PMU, Ionic, bench kit, 2 housings | 3,005–3,405 |
| Battery backbone — tray, Class-T, disconnect, 2 AWG, lugs | 540–880 |
| Relay panel — 11 relays, 10 sockets, fuse block, busbars, plate | 350–620 |
| Sill node — plate, 4 sockets, 3 fuses, ground stud | 80–150 |
| Wire and connector order | 1,000–1,700 |
| **Connector accessories** — wedgelocks, clips, backshells, boots | 245–365 |
| CAN keypad | 300–450 |
| Tools — crimpers, label printer | 220–470 |
| Mirrors, fuel-door solenoid, hatch switch | 210–550 |
| DCU + ICU hard parts | 289–469 |
| Display, servos, senders, enclosures | 230–500 |
| **ELECTRICAL PROJECT TOTAL** | **~6,470–9,560** |
| Remaining after what's committed | **~3,465–6,155** |

## Lighting & body project — separate budget

| Group | ~$ |
|---|---|
| DOT LED modules, red and white | 80–200 |
| Tail light housings, fabrication | 60–150 |
| Driver PCBs ×2 + revisions | 60–120 |
| Headlamp units | 120–300 |
| Adapter plates | 20–60 |
| LED bulbs — park, marker, plate, interior, glovebox, luggage, illumination | 60–150 |
| **LIGHTING SUBTOTAL** | **~400–980** |
| Body — rust, paint, trim | **not scoped** |

## What this changes about sequencing

Nothing in the electrical buy order moves. Lighting was always last money; it is
now **a different project's** last money, and it no longer competes with the wire
order or the panel parts for the same budget window.

**Buy order, unchanged:**

| # | Item | Waiting on |
|---|---|---|
| 1 | Battery mount, Class-T, disconnect, 2 AWG | T-024, T-029 |
| 2 | Deutsch crimper, lug crimper, label printer | nothing |
| 3 | CAN keypad | nothing |
| 4 | Relays, sockets, fuse block, busbars, plate | **T-007** |
| 5 | **Wire and connector order + wedgelocks and accessories** | **T-008** |
| 6 | Mirrors, fuel-door solenoid, hatch switch | T-031/32/33 |
| 7 | Module hard parts | firmware proves the design |
| 8 | Display, servos, senders | Q-037 |

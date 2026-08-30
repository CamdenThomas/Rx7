# BOM — Electrical / PMU

*Rev 2026-08-30 · owns: the money — every line item, what is committed, what remains and the buy order. [`BUY-LIST.md`](BUY-LIST.md) is the record of what was actually bought; [`../05-BUILD/BENCH-KIT.md`](../05-BUILD/BENCH-KIT.md) details the bench items; [`../02-HARNESS/CONNECTORS.md`](../02-HARNESS/CONNECTORS.md) owns housing part numbers.*

All prices are estimates until checked against a live quote. Lighting is **not
in this BOM** — it moved to `../../lighting-body/BOM.md` (D-123). Everything
is Deutsch DT/DTP/DTM; there is no AMPSEAL anywhere in the design.

## Contents

1. Totals · 2. Committed · 3. PCU / relay panel · 4. Sill node · 5. Battery
and power backbone · 6. Harness materials · 7. Connector accessories ·
8. DCU + ICU modules · 9. Bench kit remainder · 10. Tools · 11. Buy order ·
12. Deletions that saved money

---

## 1 · Totals

| Group | ~$ |
|---|---|
| **Committed** — PMU, Ionic, bench kit as actually bought, 2 spare housings | **2,950–3,350** |
| Battery backbone — tray, Class-T, disconnect, 2 AWG, lugs | 540–880 |
| Relay panel — relays, sockets, fuse block, busbars, plate | 350–620 |
| Sill node — plate, 4 sockets, 3 fuse positions, ground stud | 80–150 |
| Wire and connector order | 1,000–1,700 |
| Connector accessories — wedgelocks, clips, backshells, boots | 245–365 |
| CAN keypad | 300–450 |
| Tools — crimpers, label printer | 220–470 |
| Mirrors, fuel-door solenoid, hatch switch | 210–550 |
| DCU + ICU hard parts still to buy | 180–360 |
| Display, servos, senders, enclosures | 230–500 |
| Bench kit remainder | 100–150 |
| **Remaining** | **~3,450–6,200** |
| **ELECTRICAL PROJECT TOTAL** | **~6,400–9,550** |

About a third is committed. Tools are one-time and partly owned already.

## 2 · Committed

| Item | ~$ | Closes |
|---|---|---|
| ECUMaster PMU-24 DL — **includes** the mating connector kit, 39 terminals and the USB-to-CAN adapter | 2,050–2,250 | closes V-016, V-018, T-021 |
| Ionic S9 heated lithium | 700–900 | closes V-017 |
| UNI-T UT210E clamp meter | 40–60 | closes T-001 |
| 3 × Teensy 4.1 | ~96 | |
| 5 × SN65HVD230 CAN transceiver modules (bench only — D-085) | ~15 | |
| 1 × micro-USB cable | ~5 | |
| 2 × Sicma 39-pos spare housings with pin sets — **inbound** | ~25 | closes T-027; `T-045` on arrival |
| **Committed** | **~2,950–3,350** | |

**Not bought**, despite an earlier record saying so (D-140): 120 Ω resistors,
resistor assortment, breadboards, Dupont jumpers, plywood/ground bus/fuse
holder. They are in §9.

## 3 · PCU / relay panel — $350–620 remaining

| Item | Qty | ~$ | Note |
|---|---|---|---|
| Micro relays, 30/40 A, with diode | 5 + 2 spare | 40–70 | K1–K4, K11 on the plate. K9 mounts in the engine bay (D-148). K5–K8 are provisioned sockets only (D-131) |
| Relay sockets, panel-mount | 10 | 50–90 | 5 populated, 5 spare positions |
| Fuse block, 12-position, ATO/ATC | 1 | 40–70 | F1–F7, F10–F13 on the plate — 11 used |
| Fuses, assorted + spares | — | 15 | |
| Busbars — always-hot and ground | 2 | 90–140 | |
| Diodes (wake OR strip), resistors, terminal strips | — | 40–70 | |
| Backer plate, standoffs, hardware | — | 60–120 | Waits on the dash envelope, `T-007` / `Q-014` |
| 120 Ω terminator + DTM-04-4P diag port pair | — | 20 | |
| CAN keypad, 8-key | 1 | 300–450 | Separate line in the totals. Q-010 → 8-key, [`SPEC.md`](../01-DESIGN/SPEC.md) §9 |

## 4 · Sill node — $80–150

| Item | Qty | ~$ |
|---|---|---|
| Aluminium plate, kick-panel mount | 1 | 20–40 |
| Relay sockets (K5–K8, fitted empty) | 4 | 20–40 |
| Fuse positions — F8, F9 (empty), F14 | 3 | 15–30 |
| Ground stud, star washers, sealant | 1 | 10–20 |
| DT06-08S door sub-connector pairs (D1, D2) | 2 | in the connector order |

## 5 · Battery and power backbone — $540–880

[`../04-SUBSYSTEMS/BATTERY-INSTALL.md`](../04-SUBSYSTEMS/BATTERY-INSTALL.md) §3 itemises this.

| Item | Qty | ~$ | Waits on |
|---|---|---|---|
| Battery tray / box + hold-down + backing plate | 1 | 90–180 | `T-024` bin measurement |
| Class-T fuse block + 150 A fuse | 1 | 90–140 | |
| Master disconnect | 1 | 55–90 | |
| Distribution post | 1 | 25–40 | |
| MRBF terminal fuse + holder (starter, if fused) | 1 | 35–60 | |
| **2 AWG** cable, ~25 ft (D-091) | — | 80–130 | |
| 1/0 or 2 AWG starter feed | — | 40–80 | |
| Lugs, boots, adhesive shrink, grommets, loom, studs, cavity wax | — | 125–160 | `T-029` post type before lugs |

## 6 · Harness materials — $1,000–1,700

Held until the routes are measured (`T-008`) — ordering housings before the
lengths are known means ordering the wrong wire.

| Item | Qty | ~$ |
|---|---|---|
| GXL/TXL wire — 12/14/16/18 AWG, 10 colours | ~1,200 ft | 380–560 |
| Deutsch DTP housings, contacts, wedges | 5 pr + spare | 110–180 |
| Deutsch DT 12/8/6/2 housings, contacts, seals | 12 pr + spare | 220–350 |
| DTM-04-4P diag port | 1 pr | 15–25 |
| Adhesive-lined heat shrink assortment | — | 70–120 |
| Tesa 51608 cloth tape | 5 rolls | 50–80 |
| Abrasion loom / split conduit | — | 60–120 |
| Grommets, bulkhead pass-throughs, P-clips | — | 80–150 |
| Ring terminals, ferrules | — | 40–70 |
| Heat-shrink label sleeves + cartridges | — | 50–90 |

The exact housing list — 15 leg housings, 2 door, 4 drops, 24 mated pairs — is
generated in [`../02-HARNESS/CONNECTORS.md`](../02-HARNESS/CONNECTORS.md) from `housings.csv`.

## 7 · Connector accessories — $245–365

**Secondary wedgelocks are required**, one per half, sold separately. A
DT-family connector without one will not retain its contacts.

| Item | Qty | ~$ |
|---|---|---|
| W12S / W12P — 12-way | 5 pr | 25 |
| W8S / W8P — 8-way | 5 pr | 22 |
| W6S / W6P — 6-way | 2 pr | 8 |
| W2S / W2P — 2-way | 1 pr | 4 |
| WP-4S / WP-4P — DTP 4-way | 4 pr | 20 |
| WP-2S / WP-2P — DTP 2-way | 1 pr | 5 |
| WM-4S / WM-4P — DTM 4-way | 2 pr | 8 |
| +20 % spare | | 18 |
| **Wedgelocks** | | **~110** |
| Mounting clips `1027-003-1200` — receptacles at the dash post | ~19 | 30–50 |
| Backshells, 180° and 90°, with strain relief | ~8 | 60–120 |
| Boots | ~10 | 30–60 |
| Dust caps — capped spares, the unmated diag port | ~6 | 15–25 |
| `-C015` reduced-diameter seals | if needed | — |

## 8 · DCU + ICU modules

Three Teensys and five bench transceivers are already in hand (§2). What is
left:

| Item | Qty | Part | ~$ |
|---|---|---|---|
| CAN transceiver, in-car | 4 | TI TCAN1042 / TCAN1051 (D-085, `V-057`) | 12 |
| Teensy socket headers | 3 sets | Machined pin | 12 |
| PSRAM chips for the Teensy pads | 2 | 8 MB (D-170) | 10 |
| Carrier PCB, 2 revisions | 4 | Custom, socketed Teensy | 100–250 |
| Automotive buck 12 V → 5 V | 2 | TPS54331 or a sealed module | 20–40 |
| TVS, load dump | 2 | SMBJ33A | 2 |
| Reverse polarity protection | 2 | Schottky or ideal-diode IC | 6 |
| Input filter — inductor + bulk caps | 2 sets | | 8 |
| ICU analog front end — 1 % dividers, RC filters, clamp diode pairs, opto/comparator for the tach, Schmitt buffer | — | | 20–30 |
| IMU on the ICU carrier | 1 | MPU-6050 / ICM-20948 class (D-109) | 5 |
| Bus hardware — 120 Ω far-end terminator, private link pair | — | | 7 |
| Page button, momentary (D-169) | 1 | | 3 |
| **Hard parts still to buy** | | | **~180–360** |
| Display panel, 800 × 480 (`Q-060`) | 1 | | 60–200 |
| HVAC servos | 4 | after the heater-box teardown | 60–120 |
| Oil temperature sender, VSS sensor | 1 + 1 | thread and range to confirm on the engine | 60–120 |
| Enclosures + cluster bezel fabrication | — | | 80–200 |
| DP-ICU (DT06-12S) + DP-DCU (DT06-6S) pairs | 2 | in the connector order | — |
| **Display, servos, senders, enclosures** | | | **230–500** |

Do not order a display before the firmware has proved the SPI dirty-rectangle
path on the bench — it has (D-168), so `Q-060` is now the gate.

## 9 · Bench kit remainder — $100–150

[`../05-BUILD/BENCH-KIT.md`](../05-BUILD/BENCH-KIT.md) itemises it: 120 Ω resistors, breadboards, Dupont
jumpers, soldering iron, hand tools, potentiometer, hookup wire, fuses, a
bulb and socket, toggle switches. **Items 1–4 (~$47) finish every remaining
firmware stage.**

## 10 · Tools — $220–470 remaining

| Tool | ~$ | Before |
|---|---|---|
| Open-barrel crimper with 1.5 mm and 2.8 mm dies for the FCI terminals (`V-069`) | 60–150 | Phase 2A termination |
| Deutsch DT/DTP crimper + coupon stock | 80–250 | Phase 5 |
| Hydraulic lug crimper | 40–80 | Phase 3 |
| Label printer + heat gun | 40–90 | Phase 4 |
| Clamp meter | **owned** | — |

## 11 · Buy order

| # | Item | ~$ | Waits on |
|---|---|---|---|
| 1 | Bench kit remainder — resistors, breadboards, jumpers, iron | 100–150 | nothing |
| 2 | Spare 1.5 mm FCI terminals, ~15 | 0–40 | T-025 → D-135 counted **zero small spares**; order is `T-044` |
| 3 | Battery mount, Class-T, disconnect, 2 AWG, lugs | 540–880 | `T-024`, `T-029` |
| 4 | Crimpers, lug crimper, label printer | 220–470 | nothing |
| 5 | CAN keypad | 300–450 | nothing |
| 6 | Relays, sockets, fuse block, busbars, plate | 350–620 | **`T-007` dash envelope** |
| 7 | Sill plate, sockets, fuse positions, stud | 80–150 | `T-028` |
| 8 | **Wire and connector order + wedgelocks and accessories** | 1,245–2,065 | **`T-008` routes**, and `Q-061`–`Q-063` so no housing is ordered short |
| 9 | Mirrors, fuel-door solenoid, hatch switch | 210–550 | `T-031`, `T-032`, `T-033` |
| 10 | Module hard parts | 180–360 | carrier PCB schematics (H-001, H-002) |
| 11 | Display, servos, senders, enclosures | 230–500 | `Q-060` |

Item 8 is the one that must wait. Four functions have no pin until Checklist
0.23 rules on the open packets; ordering housings before that means ordering
the wrong ones.

## 12 · Deletions that saved money

| Removed | Saved | Decision |
|---|---|---|
| USB-to-CAN adapter — came with the PMU | 169 | V-018 → closed, in the box |
| Full plywood bench mule | ~140 | D-141 |
| AMPSEAL housings and contacts — all Deutsch now | ~150 | D-052, D-070 |
| Load resistors for LED bulb-out — bulb-out dropped | ~80 | |
| 6 relay sockets — bank shrank 16 → 10 | ~40 | D-065, D-067 |
| Cruise, rear wiper, power antenna, headlight cleaner wiring | ~60 | |
| Cigarette lighter circuit | ~20 | D-095 |
| Window motors, switches and door harness — manual windows (bridge provisioned) | ~120 | D-131 |
| Lighting — moved, not deleted | 400–980 | D-123 |

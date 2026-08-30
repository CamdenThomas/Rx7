# BUY LIST — the bench-kit order, as it actually happened

*Rev 2026-08-30 · owns: the record of the first order — what was bought, what was not, where it came from, and the part numbers for re-orders. Remaining purchases are [`BOM.md`](BOM.md)'s; what the bench still needs is [`../05-BUILD/BENCH-KIT.md`](../05-BUILD/BENCH-KIT.md)'s.*

## Contents

1. What arrived · 2. What was not bought · 3. Sources and part numbers ·
4. The three housings and the terminal count · 5. Bench CAN, plainly ·
6. "With pins" or "without"

---

## 1 · What arrived (D-140)

| Item | Qty | ~$ | Closes |
|---|---|---|---|
| UNI-T UT210E clamp meter | 1 | 40 | closes T-001 |
| Teensy 4.1, with pins | 3 | 96–108 | D-089 |
| SN65HVD230 CAN transceiver modules | 5 | 12 | bench only, D-085 |
| USB micro-B cable | **1** | 5 | Teensy 4.1 is micro-B, not USB-C |
| Sicma 39-pos housing, Ballenger CONN-101139, each with a full pin set | 2 | 24 | closes T-027 — **inbound**, `T-045` on arrival |
| ECUMaster PMU-24 DL — with mating connector kit, 39 terminals, USB-to-CAN adapter | 1 | — | closes V-016, V-018, T-021 |
| Ionic S9 heated lithium | 1 | — | closes V-017 |

Gate 0 is closed for the bench: Phase 2A and 2B are both unblocked
([`../05-BUILD/CHECKLIST.md`](../05-BUILD/CHECKLIST.md) G0.1–G0.3, G0.5; G0.4 is the battery's charge).

## 2 · What was NOT bought

An earlier revision of this file recorded these as purchased. **They were
not** (D-140). They are still on [`BENCH-KIT.md`](../05-BUILD/BENCH-KIT.md) "To buy" and none of them
blocks anything except the last firmware stages:

| Item | Needed for | ~$ |
|---|---|---|
| 120 Ω ¼ W resistors ×4 | CAN termination — **CAN1 will not come up without them** | 2 |
| E24 1 % resistor assortment | The six ladders ([`../01-DESIGN/LADDERS.md`](../01-DESIGN/LADDERS.md)) | 15 |
| Solderless breadboards ×2 | One per Teensy | 12 |
| Dupont jumper assortment | | 8 |
| Plywood, ground bus, inline fuse holder | Dropped with the bench mule (D-141) — a current-limited PSU and flying leads instead | — |
| Scrap rotary switch | Ladder practice on the bench (Stage 4 used a potentiometer instead) | 8 |
| Spare 1.5 mm terminals | Held for the count — now known, see §4 | 0–40 |

## 3 · Sources and part numbers

Links checked 2026-08. Prices move; the part numbers are what matter.

**Clamp meter — UNI-T UT210E.** DC current at 2.000 A (1 mA resolution),
20.00 A (10 mA) and 100.00 A (100 mA); true RMS, auto-ranging. The 1 mA
resolution is why this one — it reads parasitic draw directly. 100 A maximum,
so it will not read cranking current; the cranking check (Checklist 3.17) is a
voltage-drop test, so that does not matter.
Amazon: https://www.amazon.com/UNI-T-UT210E-Capacitance-Multimeter-Resolution/dp/B075ZHDQFP

**Teensy 4.1.** Adafruit announced in January 2026 that it is discontinuing
Teensy sales, with SparkFun becoming the exclusive distributor. A distribution
change, not an end-of-life — Teensyduino 1.62 shipped June 2026 — but
single-channel distribution is a real supply risk for a 2027–28 project, which
is why three were bought. `V-059` re-checks availability before the final
carrier boards commit to the platform.
PJRC: https://www.pjrc.com/ · Micro Center: https://www.microcenter.com/brand/4294818527/pjrccom ·
eBay, authorised distributor in Fort Collins: https://www.ebay.com/itm/193462570002 ·
Amazon: https://www.amazon.com/PJRC-Teensy-4-1-with-Pins/dp/B08CTM3279

**CAN transceivers, bench.** SN65HVD230 modules — 3.3 V native, no level
shifting.
5-pack: https://www.amazon.com/AITRIP-SN65HVD230-Transceiver-Communication-Arduino/dp/B0GVD5LM42 ·
Waveshare single: https://www.amazon.com/SN65HVD230-CAN-Board-Communication-Development/dp/B00KM6XMXO
Purpose-built alternative with a switchable 120 Ω, on the CAN3 pins:
https://www.tindie.com/products/fusion/single-can-fd-adapter-for-teensy-41/
**These are bench parts.** D-085 specifies TCAN1042/1051 for the car —
automotive-qualified, VIO pin, bus-fault protection past ±12 V. The SN65HVD230
is fine on a desk and marginal in a vehicle.

**Sicma 39-position housing.** Ballenger Motorsports CONN-101139, 39-way black
SICMA 1.5/2.8 for ECUMaster EMU & PMU, $11.99:
https://www.bmotorsports.com/shop/product_info.php/manufacturers_id/9/products_id/5168
FCI/Delphi part number **211PC399S0020**. EU source:
https://www.dsgarage.it/store/en/ecu-connectors/300-fci-delphi-sicma-39-pin-black-connector-for-ecumaster-black.html

**Terminals**, ordered separately. Ballenger stocks all three.

| Size | Part | Wire | Per housing |
|---|---|---|---|
| 1.5 mm | 211CC2S2160P | 14–17 AWG | 27 |
| 2.8 mm | 211CC3S2120 | 14–16 AWG | few |
| 2.8 mm large | 211CC3S3120 | 10–12 AWG | 12 |

The pinout doc v1.2/1.3 revises the 1.5 mm terminal from 13–17 AWG to
**14–17 AWG**. It does not change the 16 AWG decision (D-027).

## 4 · The three housings and the terminal count

| # | Source | Terminals | Role |
|---|---|---|---|
| 1 | PMU box | 12 large of 16 supplied, 27 small of 27 (D-135) | **The car.** Terminated once, never reopened (D-004) |
| 2 | Purchased, inbound | Full set | **Bench pigtail** (Checklist 2.1) |
| 3 | Purchased, inbound | Full set | **Spare.** Untouched until something goes wrong |

Three housings covers the build, the bench and one mistake. The count
(`T-025` → D-135) found **zero small spares** in the PMU kit, so the order in
[`BOM.md`](BOM.md) §11 item 2 is ~15 × 211CC2S2160P (`T-044`, Checklist 1.8) before the
real housing is terminated. The mixed 1.5/2.8 layout is what makes this the PMU
part; a generic 39-pin with uniform terminals is a different connector.

## 5 · Bench CAN, plainly

**There is no "CAN bus" component to buy.** A CAN bus is two twisted wires and a
resistor at each end.

| Part | Qty | Why |
|---|---|---|
| CAN transceiver — SN65HVD230 module | 2 minimum (5 in hand) | The Teensy has the *controller* built in but no *transceiver* |
| 120 Ω resistors | 4 | Termination, one at each end of each bus — **not yet bought** |
| Twisted pair | 1 m | Any two wires twisted ~1 turn/inch is fine on a bench |

**The trap:** CAN1 on the PMU has **no internal termination**. Connect the
USB-to-CAN adapter without 120 Ω at both ends and the client will not see the
device. CAN2 has software-controlled termination — enable it at the PMU end in
the client and fit one physical 120 Ω at the far end of the bench backbone.

```
   [PMU CAN2]────────[Teensy A]────────[Teensy B]
    software           SN65HVD230        SN65HVD230
    term ON                                  │
                                          120 Ω
```

Develop the message map on the two Teensys alone first (done — Stages 2–3,
[`../03-MODULES/BENCH-BRINGUP.md`](../03-MODULES/BENCH-BRINGUP.md)). The PMU joins for the integration test.

## 6 · "With pins" or "without"?

**With pins**, which is what was bought. Breadboard-ready with no soldering;
all three CAN controllers are on the outer rows (CAN1 on 22/23, CAN2 on 0/1,
CAN3 on 30/31); and standard male headers plug straight into standard female
headers on the carrier PCB (D-084). The pins do not block the PSRAM/flash pads
underneath (D-170) or the SD slot. One caveat: square header pins can damage
machined round-pin sockets — use standard 0.1" female headers on the carrier.

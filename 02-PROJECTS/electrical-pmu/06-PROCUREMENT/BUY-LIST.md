# BUY LIST — the $290 unblocker order

Real links, checked 2026-08. Prices move; the **part numbers and specs** are what
matter, not the price shown.

---

## 1 · Clamp DMM — UNI-T UT210E · ~$40

**The critical spec is DC current.** Most cheap clamp meters measure AC amps
only and are useless for a car. The UT210E measures both.

| Spec       | Value                                                                                        |
|------------|----------------------------------------------------------------------------------------------|
| DC current | (cite index="63-1">2.000 A at 1 mA resolution · 20.00 A at 10 mA · 100.00 A at 100 mA</cite> |
| Type       | True RMS, auto-ranging, 2000 count                                                           |

**The 1 mA resolution is why this one.** It measures parasitic draw directly —
which is exactly what you need for the sleeping-draw budget (PMU standby, head
unit clock, battery heater). Most meters can't resolve below 100 mA.

- Amazon: https://www.amazon.com/UNI-T-UT210E-Capacitance-Multimeter-Resolution/dp/B075ZHDQFP
- Amazon alt listing: https://www.amazon.com/UNI-T-Multimeter-Voltmeter-Continuity-Capacitor/dp/B0BKFMRVHJ

**Limitation to know:** 100 A max. Fine for every load on the car. It will **not**
measure cranking current (300–500 A) — but T-016 is a *voltage-drop* test during
cranking, not a current measurement, so this doesn't matter.

---

## 2 · Teensy 4.1 × 3 · ~$32–36 each

**Supply-chain note, important.** Adafruit announced in January 2026 that
(cite index="86-1">they are discontinuing sale and support of Teensy after being informed that SparkFun is now the exclusive provider</cite>.
This is a **distribution change, not an end-of-life** — Teensyduino 1.62 shipped
June 2026 and the platform is active. But single-channel distribution is a real
supply risk for a 2027–28 project.

**It strengthens the case for buying three now.** `[V-059]` re-check availability
before committing to Teensy for the final boards.

- PJRC direct (manufacturer): https://www.pjrc.com/
- Micro Center, $31.99: https://www.microcenter.com/brand/4294818527/pjrccom
- eBay, authorised distributor **in Fort Collins**: https://www.ebay.com/itm/193462570002
- Walmart / 3DMakerWorld: https://www.walmart.com/ip/PJRC-Teensy-4-1-USB-Development-Board-with-Pins/707717946
- Adafruit, clearance while stock lasts: https://www.adafruit.com/product/4622

**Buy "with pins" for bench work** — solderless breadboard use. The final carrier
boards want machined sockets instead.

---

## 3 · CAN transceivers · ~$10–15 for a multipack

**For the bench, SN65HVD230 modules are fine and cheap.** They are 3.3 V native,
which matches the Teensy directly with no level shifting.

- 5-pack: https://www.amazon.com/AITRIP-SN65HVD230-Transceiver-Communication-Arduino/dp/B0GVD5LM42
- Waveshare single, better build: https://www.amazon.com/SN65HVD230-CAN-Board-Communication-Development/dp/B00KM6XMXO

**Purpose-built Teensy 4.1 option** — TCAN330G with a switchable onboard 120 Ω
terminator, designed for the CAN3 pins:
https://www.tindie.com/products/fusion/single-can-fd-adapter-for-teensy-41/

> **These are bench parts, not final parts.** D-085 specifies TCAN1042/1051 for
> the car — automotive-qualified, VIO pin, bus fault protection past ±12 V.
> The SN65HVD230 is fine on a desk and marginal in a vehicle. Buy the cheap
> modules now to learn on; buy the TCAN parts when the carrier PCB is laid out.

---

## 4 · Spare Sicma 39-position housing · $11.99

**Found it — and it's cheap enough to buy two.**

**Ballenger Motorsports CONN-101139** — 39 Way Black SICMA 1.5/2.8 for ECUMaster
EMU & PMU, $11.99:
https://www.bmotorsports.com/shop/product_info.php/manufacturers_id/9/products_id/5168

FCI/Delphi part number is **211PC399S0020** if you need to cross-reference.
EU source: https://www.dsgarage.it/store/en/ecu-connectors/300-fci-delphi-sicma-39-pin-black-connector-for-ecumaster-black.html

### Terminals — order separately

| Size         | Part         | Wire      | Need           |
|--------------|--------------|-----------|----------------|
| 1.5 mm       | 211CC2S2160P | 14–17 AWG | 27 + 20% spare |
| 2.8 mm       | 211CC3S2120  | 14–16 AWG | few            |
| 2.8 mm large | 211CC3S3120  | 10–12 AWG | 12 + 20% spare |

`[T-025]` **Count what came in the PMU box first.** You may only need spares.
Ballenger stocks these terminals — search the part numbers on their site.

**Note:** the pinout doc v1.2/1.3 revises the 1.5 mm terminal from 13–17 AWG to
**14–17 AWG**. Doesn't change the 16 AWG decision (D-027), but worth knowing.

---

## 5 · Bench board materials · ~$40

Nothing special, and nothing needs a link:

| Item                                | Note                                                 |
|-------------------------------------|------------------------------------------------------|
| Plywood, ~24 × 36 in                | Hardware store offcut                                |
| Small ground bus bar                | Or a brass strip with screws                         |
| Inline fuse holder + assorted fuses | Feeds the board from a bench supply or spare battery |
| Solderless breadboard × 2           | One per Teensy                                       |
| Dupont jumpers                      | Assorted                                             |
| Assorted resistors, E24 1%          | **For the ladder work** — see `LADDERS.md` values    |
| **2 × 120 Ω resistors**             | CAN termination. See below                           |

---

## Do you need the CAN bus for bench work?

**Yes — and it's about $5 of parts.**

You have three separate needs:

### A · PMU config over CAN1 — needed for Phase 2a
The USB-to-CAN adapter came with the PMU. But **CAN1 has no internal
termination** — the bus will not come up without external resistors.

**You need 2 × 120 Ω**, one at each end of even a 30 cm bench link. This is the
single most common "why won't it connect" problem with this device.

### B · Teensy-to-Teensy — needed for Phase 2b
Two SN65HVD230 modules, a twisted pair between them, 120 Ω at each end. That is
the whole rig. You can develop the entire message map on this before the PMU is
ever involved.

### C · All three together — the real integration test
PMU CAN2 + both Teensys on one bench backbone. CAN2 has **software-controlled**
termination, so enable it in the PMU client at one end and fit one physical
120 Ω at the far end.

**Bench CAN shopping list — $5**

| Item                                                               | Qty                 |
|--------------------------------------------------------------------|---------------------|
| 120 Ω ¼ W resistors                                                | 4 (2 spare)         |
| Twisted pair — any two wires twisted ~1 turn/inch works on a bench | 1 m                 |
| SN65HVD230 modules                                                 | in the 5-pack above |

---

## Order summary

| # | Item                                         | ~$            |
|---|----------------------------------------------|---------------|
| 1 | UNI-T UT210E clamp meter                     | 40            |
| 2 | Teensy 4.1 × 3, with pins                    | 96–108        |
| 3 | SN65HVD230 5-pack                            | 12            |
| 4 | Sicma 39-pos housing × 2                     | 24            |
| 5 | Terminals — **pending T-025 count**          | 0–40          |
| 6 | Bench board, breadboards, jumpers, resistors | 40            |
| 7 | 120 Ω resistors, twisted pair                | 5             |
|   | **Total**                                    | **~$217–269** |

Under budget, and it opens PMU config, firmware, and every measurement task at
once.

---

## RE-VERIFIED 2026-08 — complete bench stage kit

Everything needed for **Phase 2a (PMU config)** and **Phase 2b (firmware)**.
Nothing here waits on an open question.

### Already owned

| Item                             | Note                                           |
|----------------------------------|------------------------------------------------|
| ECUMaster PMU-24 DL              | Purchased                                      |
| **USB-to-CAN adapter**           | **Came in the PMU box** — no separate purchase |
| Mating connector kit + terminals | Came in the PMU box `[T-025]` count them       |
| Ionic S9 battery                 | Purchased — not needed for bench               |

### Still to buy

| #  | Item                                           | Qty | ~$     | Link                                                                                                                                                                                                                 |
|----|------------------------------------------------|-----|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1  | UNI-T UT210E clamp meter                       | 1   | 40     | [Amazon](https://www.amazon.com/UNI-T-UT210E-Capacitance-Multimeter-Resolution/dp/B075ZHDQFP)                                                                                                                        |
| 2  | **Teensy 4.1 — WITH PINS**                     | 3   | 96–108 | [Amazon](https://www.amazon.com/PJRC-Teensy-4-1-with-Pins/dp/B08CTM3279) · [Micro Center $31.99](https://www.microcenter.com/brand/4294818527/pjrccom) · [eBay, Fort Collins](https://www.ebay.com/itm/193462570002) |
| 3  | **SN65HVD230 CAN transceiver, 5-pack**         | 1   | 12     | [Amazon](https://www.amazon.com/AITRIP-SN65HVD230-Transceiver-Communication-Arduino/dp/B0GVD5LM42)                                                                                                                   |
| 4  | Sicma 39-pos housing, CONN-101139              | 2   | 24     | [Ballenger](https://www.bmotorsports.com/shop/product_info.php/manufacturers_id/9/products_id/5168)                                                                                                                  |
| 5  | **USB micro-B cables**                         | 2   | 10     | Any. **Teensy 4.1 uses micro-B, not USB-C**                                                                                                                                                                          |
| 6  | 120 Ω ¼ W resistors                            | 4   | 2      | Any electronics supplier                                                                                                                                                                                             |
| 7  | E24 1% resistor assortment                     | 1   | 15     | For the six ladders — see `LADDERS.md`                                                                                                                                                                               |
| 8  | Solderless breadboard                          | 2   | 12     |                                                                                                                                                                                                                      |
| 9  | Dupont jumper assortment                       | 1   | 8      |                                                                                                                                                                                                                      |
| 10 | Plywood ~24×36, ground bus, inline fuse holder | 1   | 40     | Hardware store                                                                                                                                                                                                       |
| 11 | Scrap multi-position rotary switch             | 1–2 | 8      | Ladder practice, Checklist 047                                                                                                                                                                                       |

**Total: ~$267–279.**

### Deliberately NOT needed yet

| Item                                  | Why not                                              |
|---------------------------------------|------------------------------------------------------|
| Deutsch crimper                       | Phase 4. Bench pigtail can use the PMU kit terminals |
| TCAN1042/1051 automotive transceivers | Phase 5. SN65HVD230 is fine on a desk (D-085)        |
| Display, servos, senders              | Wait until firmware proves what it needs             |
| Any connector or wire                 | **Q-014 and T-008 still open**                       |

---

## "With pins" or "without pins"?

**Buy with pins.** Three reasons:

1. **Breadboard-ready immediately.** No soldering before you can start.
2. **All three CAN buses are on the outer rows** — CAN1 on pins 22/23, CAN2 on
   0/1, CAN3 on 30/31. The pinned version breaks out all 42 edge I/O, so nothing
   you need is hidden.
3. **It doesn't cost you the carrier board later.** Standard male headers plug
   straight into standard female headers on a PCB, which is how you'd socket it
   anyway (D-084).

**What the pins do NOT block:** the two SMD memory footprints on the bottom
(PSRAM/flash) and the SD card slot are unaffected either way.

**One caveat if you later use machined round-pin sockets** rather than standard
female headers — square header pins can damage machined contacts. Use standard
0.1" female headers on the carrier and this never comes up.

---

## The CAN question, answered plainly

**There is no "CAN bus" component to buy.** A CAN bus is two twisted wires and a
resistor at each end. What you need is:

| Part                                    | Qty              | Why                                                                                                |
|-----------------------------------------|------------------|----------------------------------------------------------------------------------------------------|
| **CAN transceiver** — SN65HVD230 module | 2 minimum, buy 5 | The Teensy has the *controller* built in but no *transceiver*. It cannot drive the bus without one |
| **120 Ω resistors**                     | 4                | Termination. Two per bus, one at each end                                                          |
| Twisted pair                            | 1 m              | Any two wires twisted ~1 turn/inch is fine on a bench                                              |

**The trap:** CAN1 on the PMU has **no internal termination**. If you connect the
USB-to-CAN adapter without fitting 120 Ω at both ends, the bus will not come up
and the client will not see the device. This is the most common first-day problem
with this hardware.

CAN2 has software-controlled termination — enable it at the PMU end in the
client, and fit one physical 120 Ω at the far end of the bench backbone.

### Bench wiring, all three nodes

```
   [PMU CAN2]────────[Teensy A]────────[Teensy B]
    software           SN65HVD230        SN65HVD230
    term ON                                  │
                                          120 Ω
```

Develop the message map on the two Teensys alone first. The PMU only needs to
join once you're testing real integration.

---

# STATUS 2026-08 — bench kit PURCHASED

Everything below is bought and in hand. This file is now a record, not a
shopping list. Remaining purchases live in `BOM.md` and `TASKS-CAMDEN.md`.

| Item                                 | Status                                                |
|--------------------------------------|-------------------------------------------------------|
| UNI-T UT210E clamp meter             | **Bought**                                            |
| Teensy 4.1 × 3, with pins            | **Bought**                                            |
| SN65HVD230 5-pack                    | **Bought**                                            |
| USB micro-B cables × 2               | **Bought**                                            |
| 120 Ω resistors                      | **Bought**                                            |
| E24 1% resistor assortment           | **Bought**                                            |
| Breadboards × 2                      | **Bought**                                            |
| Dupont jumpers                       | **Bought**                                            |
| Bench board, ground bus, fuse holder | **Bought**                                            |
| Scrap rotary switch                  | **Bought**                                            |
| **Sicma 39-pos housings × 2**        | **Bought** — each with a full pin set                 |
| Spare terminals                      | **Deliberately held** — pending the T-025 stock count |

## Connector inventory — three housings

| # | Source    | Terminals | Role                                                 |
|---|-----------|-----------|------------------------------------------------------|
| 1 | PMU box   | Full set  | **The car.** Terminated once, never reopened (D-004) |
| 2 | Purchased | Full set  | **Bench mule.** Test pigtail, Checklist 2.3          |
| 3 | Purchased | Full set  | **Spare.** Untouched until something goes wrong      |

**This is the right amount.** Three housings covers the build, the bench, and one
mistake. The spare-terminal question is separate and comes down to the count.

### T-025 — what to count, and what "enough" looks like

Per housing you need **12 large (2.8 mm) + 27 small (1.5 mm)**.

| Finding                            | Action                                                                |
|------------------------------------|-----------------------------------------------------------------------|
| Each set has exactly 39, no spares | **Order ~8 large and ~15 small** as working spare. You will ruin some |
| Sets include extras                | Count the surplus, order only the shortfall                           |
| Sets are all one terminal size     | **Wrong housing** — see the cavity check in T-020                     |

That last row is the one to check first. A generic 39-pin with uniform terminals
is a different connector, and the mixed 1.5/2.8 layout is what makes it the PMU
part.

### Terminal part numbers, for when you do order

| Size         | Part         | Wire      |
|--------------|--------------|-----------|
| 1.5 mm       | 211CC2S2160P | 14–17 AWG |
| 2.8 mm       | 211CC3S2120  | 14–16 AWG |
| 2.8 mm large | 211CC3S3120  | 10–12 AWG |

Ballenger stocks all three — search the part numbers.

---

## Gate 0 is closed

Phase 2A and Phase 2B are both fully unblocked. Nothing is missing for either.

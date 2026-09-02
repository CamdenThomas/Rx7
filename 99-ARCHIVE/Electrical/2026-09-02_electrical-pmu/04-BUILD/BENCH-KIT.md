# BENCH KIT

*Rev 2026-08-31 (D-196) · owns: in-hand inventory and the in-car commissioning procedure (D-194). Purchases are [`../05-PROCESS/BOM.md`](../05-PROCESS/BOM.md)'s, by wave; part numbers are its §9 re-order reference.*

---

## In hand

| Item | Qty |
|---|---|
| Teensy 4.1 | 3 |
| SN65HVD230 CAN transceiver modules | 5 |
| Header pins, 0.1" male | ✓ **unsoldered** |
| micro-USB cable | 1 (D-140 — one was bought, not several) |
| UNI-T UT210E clamp meter | 1 |
| PMU-24 DL + connector + 39 terminals | 1 |
| Spare Sicma housings | 2 — **inbound**; `T-027` done, `T-045` checks them on arrival |

**Terminal stock:** 12 large `FCI` of 16 supplied · 27 small `FCI 125` of 27
supplied — **zero small spares**.

---

## Purchases

All purchasing lives in **[`BOM.md`](../05-PROCESS/BOM.md)** — one list,
organised by wave (D-195, D-196). This file owns procedure only.

## In-car commissioning setup (D-194)

**PMU mounted in the car**, powered from the new backbone, laptop over CAN1
through the diag pigtail (wire DP-DIAG early). Enter the whole PMU-CONFIG
before any circuit migrates; every function proves itself on its own real
load at cutover, one circuit per sitting.

**First power-up: 5 A fuse in the feed.** Enough for the PMU to boot and talk
over CAN; anything shorted blows a 5 A fuse instead of melting cable. Verify no
smoke and CAN comes up, step to 15 A, re-verify, then fit the Class-T for real
operation.

**Soft-fuse test:** set one channel's limit to **2 A**, enable only that channel,
touch its bulkhead pin to ground. Watch the trip, the retry count and the reset.
With a low limit the event is undramatic, and it is the behaviour that separates
this device from a fuse box.

---

## Tools

### Now

| Tool | ~$ |
|---|---|
| Wire strippers, 10–22 AWG | 15–30 |
| Flush cutters | 10–15 |
| Needle-nose pliers | 10 |
| Soldering iron + solder | 25–60 |

### Before Phase 4

**Open-barrel crimper for the FCI terminals** (`V-069`)

The Sicma/FCI terminals are **open-barrel**. You need ratcheting open-barrel dies
covering **1.5 mm (14–17 AWG)** and **2.8 mm (10–16 AWG)**.

> **Confirm the die against an actual terminal before buying**, and **order spare
> 1.5 mm terminals first (`T-044`, Checklist 1.8)**. You have zero small spares.
> Make three practice crimps and pull-test them (Checklist 1.10–1.11) before a
> real one.

### Later

| Tool | Phase |
|---|---|
| Deutsch DT/DTP crimper | 5 |
| Hydraulic lug crimper | 3 |
| Heat gun | 4–5 |
| Label printer | 4 |

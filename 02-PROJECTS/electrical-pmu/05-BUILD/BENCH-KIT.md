# BENCH KIT

*Rev 2026-08-30 · owns: materials and tools for Phase 2A and 2B — what is in hand, what is still to buy, and the bench setup. Harness materials are [`../06-PROCUREMENT/BOM.md`](../06-PROCUREMENT/BOM.md)'s and [`CUT-LIST.md`](CUT-LIST.md)'s; what was actually bought is [`../06-PROCUREMENT/BUY-LIST.md`](../06-PROCUREMENT/BUY-LIST.md)'s (D-140).*

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

## To buy — ~$98–153 · **none of this has been bought yet** (D-140)

| # | Item | ~$ | For |
|---|---|---|---|
| 1 | 120 Ω resistors ×4 | 2 | CAN termination. **CAN1 has no internal termination and will not connect without them** |
| 2 | Breadboards ×2 | 12 | |
| 3 | Dupont jumpers | 8 | |
| 4 | Soldering iron + solder | 25–60 | Transceiver headers |
| 5 | Wire strippers 10–22 AWG, flush cutters, needle-nose | 35–55 | |
| 6 | 10 kΩ potentiometer | 3 | Sweeps the full ladder range in Stage 4 |
| 7 | Hookup wire, solid core 22–24 AWG | 8 | Breadboard jumpers that stay put |
| 8 | Assorted fuses including **5 A** | 5 | First power-up protection |
| 9 | Headlight bulb + socket | 10 | One real load |
| 10 | Toggle switches ×4 | 8 | Input testing |

**Items 1–4 (~$47) finish every remaining firmware stage.**

---

## Bench setup

**PMU on a desk**, flying leads into a **spare** housing, laptop over CAN1, one
bulb, a few switches.

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

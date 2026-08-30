# SILL NODE — secondary distribution point

*Rev 2026-08-30 · owns: what the sill plate holds, the door connectors D1/D2, and the sill ground rule. Cavities are [`PIN-MAP.md`](PIN-MAP.md)'s.*

Created by D-065 (window relays at the sill) and D-068 (doors get their own
connector pair). The sill is a small distribution node — the only one outside
the dash post — and a sub-assembly of the REAR CABIN leg, not a fifth leg: it
has no independent removal boundary (D-132). Diagram: `diagrams/sill-doors.svg`.

---

## What the sill plate holds

| Item | Qty | State |
|---|---|---|
| Door connectors D1, D2 — `DT06-08S` each (D-092) | 2 | **LIVE** — door pin, mirror motors, mirror heat |
| Local ground stud | 1 | **LIVE** — every door return terminates here |
| Mirror heat branch fuse F14 | 1 | DEFERRED — position fitted; conductor from O15 is `Q-062` |
| Window H-bridge relay sockets K5–K8 | 4 | **PROVISIONED — fitted, empty** (D-131) |
| Window branch fuse positions F8, F9 | 2 | **PROVISIONED — fitted, empty** |
| Small backer plate behind the kick panel | 1 | Space to be measured — `V-055` / `T-028` |

**Build it complete. Populate it later.** Fitting four empty sockets and two
spare fuse positions to a plate on the bench costs a few dollars; adding a
plate behind a trim panel on a finished car costs an afternoon and means
pulling the sill again.

## Door connectors — D1 driver, D2 passenger

One `DT06-08S` per door (D-092), exactly eight cavities, zero spare (D-093).

| Cav | Circuit | AWG | Source | State |
|---|---|---|---|---|
| 1 | Window motor — leg A | 14 | K5/K6 (D1) · K7/K8 (D2) at the sill | PROVISIONED — **capped in the door** |
| 2 | Window motor — leg B | 14 | same | PROVISIONED — capped in the door |
| 3 | Door pin switch | 16 | A6 ladder via L4-S 2 | LIVE |
| 4 | Mirror motor — common | 16 | Mirror control — `Q-062` / `V-060` | DEFERRED |
| 5 | Mirror motor — X axis | 16 | same | DEFERRED |
| 6 | Mirror motor — Y axis | 16 | same | DEFERRED |
| 7 | Mirror heat feed | 16 | Sill fuse F14 ← O15 | DEFERRED |
| 8 | Ground → sill node | 16 | Sill ground stud | LIVE |

**The wire goes into the door now** whether or not a motor is on the end of it
(D-004). Pulling a door card once is fine; pulling it twice is a waste of a
weekend. 14 AWG is at the very top of the size-16 seal range — it fits, with
no margin above (D-116).

`V-060` — confirm the chosen mirrors need exactly three motor conductors before
ordering; some digital units use a serial interface, which would free two
cavities and change the DCU's job.

## What crosses the tunnel to the sill

| Conductor | Class | Path | State |
|---|---|---|---|
| Window motor bus feed | 12 AWG | O1 → L4-P 3 → K5–K8 commons | PROVISIONED, capped |
| Window commands ×4 | 16 AWG | L3-S2 3–6 → box → L4-M 9–12 → K5–K8 coils | PROVISIONED, capped |
| Door pin ladder | 16 AWG | D1 3 / D2 3 → L4-S 2 → A6 | LIVE |
| **O15 comfort feed for mirror heat** | — | **not yet allocated** | `Q-062` |
| **Mirror motor control from the dash** | — | **not yet allocated** — depends on `V-060` | `Q-062` |
| **Door-pin wake source** | — | **not yet allocated** | `Q-062` |

Before D-065 four 12 AWG motor legs crossed the tunnel; now one provisioned
feed and four 16 AWG commands do, and `L4-P2` disappeared entirely (D-066).

## Mirrors — option B (D-093)

The factory multiplexing mirror switch (I-01) is dead (`V-036` → D-097).
New mirrors — larger, heated, digital control (`T-031`) — are wired
independently per side. Nothing of the factory shared-bus scheme is inherited.

## Ground rule at the sill

**Door grounds terminate at the sill node, not inside the door.** A ground
crossing the door boot is a ground crossing a flex point, and door boots are
where harnesses die. Every return in D1 and D2 lands on the sill stud. The
sill node grounds to the chassis locally and does **not** return to the dash
post (D-017).

## Window H-bridge — provisioned (D-131)

Electrically identical to the pop-up bridge; drawn in
[`../01-DESIGN/SCHEMATICS.md`](../01-DESIGN/SCHEMATICS.md) §3. The car has no power windows today. Adding
them later ([`../04-SUBSYSTEMS/DEFERRED-FEATURES.md`](../04-SUBSYSTEMS/DEFERRED-FEATURES.md) §1):

1. Fit regulators with motors
2. Plug into the capped D1/D2 legs
3. Populate K5–K8
4. Fit F8, F9
5. Uncap the switch inputs at L3-S2, fit switches
6. Enable the outputs and the interlock logic in the PMU

**No harness work. No connector opened.**

## Build sequence impact

| [`CHECKLIST.md`](../05-BUILD/CHECKLIST.md) step | What the sill adds |
|---|---|
| 4.4 | Plate: 10 sockets, populate 5 — the other 4 sockets are here, empty |
| 5.11 | Fabricate the sill plate — 4 sockets, F8/F9/F14 positions, ground stud |
| 5.13 | Build D1 and D2 |
| 6.6 | Install the sill node with the L4 leg, before the doors are connected |

**The sill node is built and bench-tested with the L4 leg**, not separately.
It is part of that harness, not part of the panel.

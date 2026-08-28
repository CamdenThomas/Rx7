# SILL NODE — secondary distribution point

Created by D-065 (window relays at the sill) and D-068 (doors get their own
connector pair). The sill stops being a pass-through and becomes a small
distribution node — the only one outside the dash post.

---

## What lives here

| Item | Qty | Note |
|---|---|---|
| Window H-bridge relays K5–K8 | 4 | Driver up/down, passenger up/down |
| Branch fuses F8, F9 | 2 | 15 A each, one per window |
| Local ground node | 1 | Door returns terminate here, not in the door |
| Door connectors D1, D2 | 2 | One per door, through the boot |
| Small backer plate | 1 | Relays + fuses, mounted behind the kick panel or sill trim |

**Why this works better than the box:** the motor legs are now inches long
instead of running the tunnel, the environment is dry and heated, and the relays
are reachable by pulling one trim panel rather than dropping the dash.

**Why it is not a fifth leg:** it has no independent removal boundary. It comes
out with the REAR CABIN leg, as a sub-assembly of it.

---

## What crosses the tunnel now

**Before D-065** — four 12 AWG motor legs plus commands.
**After D-065** — one 12 AWG feed plus four 16 AWG commands.

| Conductor | Class | From | To |
|---|---|---|---|
| Window motor bus feed | 12 AWG | O1 via L4-P1 cav 3 | Sill relay commons |
| Window DRV up command | 16 AWG | Dash switch via L3-S → box → L4 | K5 coil |
| Window DRV down command | 16 AWG | " | K6 coil |
| Window PASS up command | 16 AWG | " | K7 coil |
| Window PASS down command | 16 AWG | " | K8 coil |

**Net effect on the tunnel:** three fewer 12 AWG runs, four more 16 AWG. Less
copper, less weight, less bend radius, and `L4-P2` disappears entirely.

---

## Door connectors

### D1 · Driver door

| Cav | Circuit | AWG | Source |
|---|---|---|---|
| 1 | Window motor — leg A | 12 | K5/K6 at the sill |
| 2 | Window motor — leg B | 12 | K5/K6 at the sill |
| 3 | Heated mirror | 16 | O15 comfort bus via F11 |
| 4 | Door pin switch | 16 | A6 ladder |
| 5 | Mirror motor — common | 16 | Dash mirror switch |
| 6 | Mirror motor — horizontal | 16 | Dash mirror switch |
| 7 | Mirror motor — vertical | 16 | Dash mirror switch |
| 8 | Ground | 16 | **Sill node, not the door** |

### D2 · Passenger door

Identical, on K7/K8.

**Housing:** DTP06-2S for the two motor legs + DT06-6S for the rest, per door.
Or a single DT06-08S if the motor legs drop to 14 AWG — `[Q-033]`.

---

## The mirror control problem

`[Q-034]` — **unresolved.** The factory mirror switch (I-01) does both selection
and direction: it picks which mirror, then which axis and polarity. That means
the wires from the dash switch to the mirrors are *shared* between both sides,
with the switch doing the multiplexing.

Two ways to handle it:

| Option | Conductors dash→sill | Note |
|---|---|---|
| **A** — Keep the factory shared-bus switch | 3 shared + 1 select | Fewest wires. Requires the original switch to be working |
| **B** — Independent wiring per mirror | 6 | Simpler to understand, more copper, needs a different switch |

Option A is what the factory did and it is genuinely efficient. It depends on
V-036 — whether the original switch and mirrors still work.

---

## Ground rule at the sill

**Door grounds terminate at the sill node, not inside the door.** A ground
crossing the door boot is a ground crossing a flex point, and door boots are
where harnesses die. Every return in D1 and D2 lands on the sill stud.

The sill node itself grounds to the chassis locally, and does **not** return to
the dash post.

---

## Build sequence impact

| Checklist step | Change |
|---|---|
| 080 | Mount 16 relay sockets → **10 sockets in the box**, populate 5 |
| — | **New:** fabricate and mount the sill plate, 4 sockets + 2 fuses |
| 086 | Relay bank wiring splits between the box and the sill |
| 101–110 | L4 leg now includes a sill sub-assembly stage |
| 115 | Sill node installs with the L4 leg, before the doors are connected |

**The sill node should be built and bench-tested with the L4 leg**, not
separately. It is part of that harness, not part of the panel.

---

## UPDATE 2026-08 — D-093 mirrors, D-092 door housings

### D1 / D2 · one DT06-08S per door

`[Q-033 answered]` Single housing per door. Window motor legs drop to **14 AWG** —
ample sill-to-door, and DT size-16 is rated 13 A against a 10–15 A stall.

`[Q-034 answered — option B]` The factory multiplexing mirror switch is dead
(V-036). New mirrors: **larger, heated, digital control**, wired independently
per side. No reason to inherit the factory shared-bus scheme.

**The budget lands exactly at 8 cavities:**

| Cav | Circuit | AWG |
|---|---|---|
| 1 | Window motor — leg A | 14 |
| 2 | Window motor — leg B | 14 |
| 3 | Door pin switch | 16 |
| 4 | Mirror motor — common | 16 |
| 5 | Mirror motor — X axis | 16 |
| 6 | Mirror motor — Y axis | 16 |
| 7 | Mirror heat feed | 16 |
| 8 | Ground → **sill node** | 16 |

**Zero spare cavities.** That's tight by design — the alternative was two
housings per door for one spare each. `[V-060]` confirm the chosen mirrors need
exactly three motor conductors before ordering; some digital units use a serial
interface instead, which would free two cavities and change the DCU's job.

### What this removes

Mirror motors no longer consume the L4-S spares. `V-035` (door branch
oversubscribed) is fully closed — the sill node plus a dedicated door housing
solved it.

### Sill node, revised

| Item | Qty |
|---|---|
| Window H-bridge relays K5–K8 | 4 |
| Branch fuses F8, F9 | 2 |
| **Mirror heat branch fuse** | 1 |
| Local ground stud | 1 |
| Door connectors D1, D2 | 2 × DT06-08S |

`[V-055]` still open — the sill needs room for 4 relays, 3 fuses and a ground
stud behind the kick panel. Measure before fabricating the plate.

# ARCHIVED — C1–C7 regional connector scheme

**Superseded 2026-08 by D-029.** Replaced by the four-leg design in
`02-PROJECTS/electrical-pmu/legs/`.

Kept because the reasoning is useful, not because the design is.

---

## What it was

Seven bulkhead connectors on the panel edge, cut by geographic region:

| Code | Region | Housing |
|---|---|---|
| C1 | Engine & cowl | DTP-04-4P + DT06-12S |
| C2 | Front end | DTP-04-4P ×2 + DT06-12S |
| C3 | Dash & controls | AMPSEAL 23 + DTP-04-2P |
| C4 | Rear body | DTP-04-4P + DT06-12S |
| C5 | Doors & interior | DTP-04-4P + DT06-08S |
| C6 | Audio & accessory | DT06-6S |
| C7 | CAN / diagnostic | DTM-04-4P |

## Why it was replaced

**It was cut by connector convenience, not by removal boundary.** Three specific
failures:

1. **C2 split the cowl from the nose.** A wiper motor job meant disturbing the
   headlight and pop-up bundle. The cowl belongs with the front chassis.
2. **C5 split the doors from the interior.** The sill run and the interior come
   out together; the door boot is a service point, not a removal boundary.
3. **C6 and C7 were not regions at all** — they were device drops. Audio rides
   inside the dash and cabin; the diagnostic port is box-adjacent hardware.

It also mixed power and signal in single housings, which cost cavity efficiency
(size 12 and size 16 contacts in one shell), forced ladder references to share
bundles with motor legs, and meant diagnosing a switch broke a 25 A circuit.

## What replaced it

Four legs cut by what comes out of the car as one piece — ENGINE, FRONT CHASSIS,
DASH, REAR CABIN — with power and signal in **separate housings** (D-032).
13 leg connectors, 13 mating halves at the dash post.

The trade: 13 connectors instead of 11 shells, in exchange for legs that never
disturb each other and bundles that route by noise class.

## What carried forward unchanged

- Deutsch DTP for 25 A legs, DT for 14–16 AWG, AMPSEAL for high-count signal
- Full cavity count on every housing, capped wires instead of sealing plugs
- Grounds never cross a bulkhead; local star node per zone
- Reserved LS channels capped at the engine-side bulkhead

# Vehicle

*Rev 2026-08-30 · owns: what the car is and what is fitted to it today. Permanent, reused by every project; update in place when the configuration changes.*

## Identity

| Field | Value  |
|---|--------|
| Year / model | 1982 Mazda RX-7 |
| Generation | FB (SA22C) |
| Trim | GS     |
| Color | Sunbeam Silver |
| VIN | not recorded — `Q-001` / `T-049` |
| Mileage | 153000 |

## Drivetrain — current

| Field | Value |
|---|---|
| Engine | 12A rotary |
| Induction | Weber 45 DCOE |
| Fuel pump | **Carter P4070** |
| Fuel pressure | Holley regulator |
| Transmission | Automatic |
| Ignition | Stock 12A, coils, cap, rotor, wires and plugs refreshed Aug 2025 (M-005) — `V-001` confirm the coil/ignitor configuration |

## Drivetrain — planned

| Field | Value | Status |
|---|---|---|
| Engine | LS swap | Reserved for in the electrical plan (O13, O14, CAN drop, L1-S2 spares), not started |
| Transmission | CD009 6-speed | Reserved for, not started |
| Fuel pump | Aeromotive Phantom 340 in-tank | Reserved for, not started |

## Electrical — current

| Field | Value |
|---|---|
| Battery | Factory location, lead-acid — **Ionic S9 purchased, not yet fitted** (Phase 3) |
| Harness | Original factory, unmodified except PO hacks |
| Alternator | Stock — `V-002` output rating unverified (Checklist 0.4) |
| PMU | **ECUMaster PMU-24 DL purchased**, with connector kit and USB-to-CAN adapter. Nothing installed |
| Windows | **Manual** — no motors, no wiring (D-131) |
| Headlamps | Currently LED housings per [`LOADS.md`](../02-PROJECTS/electrical-pmu/01-DESIGN/LOADS.md); sealed-beam type to confirm (`V-066`) |

## Electrical — planned

See [`../02-PROJECTS/electrical-pmu/01-DESIGN/SPEC.md`](../02-PROJECTS/electrical-pmu/01-DESIGN/SPEC.md); state in [`STATUS.md`](../02-PROJECTS/electrical-pmu/STATUS.md).

## Chassis notes

Faults and quirks are [`known-issues.md`](known-issues.md); these are facts about the type.

- Pre-1983 cars use a non-hardened steering box sector shaft — known failure point.
- Rear compliance link bushings need correct procedure; improper replacement
  risks chassis damage.
- Front calipers are the wedge-style unit.
- Rear disc conversion possible from an 84–85 axle.

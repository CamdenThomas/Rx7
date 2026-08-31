# Camden's Tasks — Electrical / PMU

*Rev 2026-08-31 · owns: physical work, measurements, purchases and sign-offs that only Camden can clear. Each task cites the Checklist step it satisfies; the Checklist owns the sequence, this file owns the list. Deferred lighting tasks are §6 (D-201). Done tasks live struck-through in §5 only — no duplicates (D-196).*

**Blocking** means downstream work stops. IDs are permanent.

## Contents

1. Do next · 2. The tape-measure session · 3. Remaining diagnostics ·
4. Sourcing, by wave · 5. Done · 6. Lighting — deferred

---

## 1 · Do next

| ID | Task | Why | Checklist |
|---|---|---|---|
| **T-053** | **Place the five expedited orders** — WireBarn wire (§11c table) · DeutschConnector kits · Amazon backbone/tools · Waytek distribution · Ballenger terminals + ECUKB8 direct ([`BOM.md`](BOM.md) §11) | D-202 — parts in hand for the one-teardown build; ~$2,500–3,550 | 1.1–1.8 |
| **T-052** | **Pop-up ohm check at E-03** (`V-081`, D-199) — unplugged, ohms **R → case and RY → case at parked / mid / raised**. One winding reached via different cam segments = single-direction confirmed, K1/K2 drive R + RY bridged, WR capped | Settles the pop-up drive conductors before the L2 leg is pinned. Five minutes with the meter | 0.6 |
| **T-007** | **Dash cavity envelope** — W × H × D + 39-pin lever clearance, centre-stack depth (`V-087`), **and how deep the cluster brow shades the aperture** (`V-085` glass call) | `Q-014`. Now gates *cutting the plate* and the glass call — not purchases (D-202). Teardown day 1 | 0.8 |
| **T-008** | **Every harness route with string, +15 %** | Now gates *cutting wire to length* — the wire is ordered with 1.5× margin (D-202). Teardown day 1 | 0.11 |
| T-043 | Paint-pen dot beside cavity 1 (Wave 0 pen) | Never re-asked mid-build (D-139) | G0.5 |
| T-044 | Order spare 1.5 mm terminals ×20 + 120 Ω — rides in `T-053` Order 5 | Zero small spares while learning to crimp (D-135, D-194) | 1.8 |
| T-022 | Check the Ionic's state of charge; keep it above BMS cutoff | A lithium left to self-discharge into cutoff is hard to recover | G0.4 |
| T-045 | Verify the two inbound housings arrive **with** terminals | If they ship bare, the shortfall is worse than it looks | G0.2 |
| **T-049** | Record the VIN in `00-CAR/vehicle.md` | `Q-001`. Two minutes | — |

**T-007 and T-008 still gate ~150–240 hours of build** — but as
measure-before-cut on teardown day 1, not as order gates (D-202). Neither
needs anything in the post.

## 2 · The tape-measure session (with T-007/T-008 above)

| ID | Task | Closes | Checklist |
|---|---|---|---|
| T-024 | Cargo bin vs the Group 25 case. Mock in cardboard before cutting | `V-051` | 0.9 |
| T-028 | Sill space behind the kick panel — 4 relays, 3 fuse positions, ground stud | `V-055` | 0.10 |
| T-018 | Photograph the entire harness — connectors, branches, grounds → `01-REFERENCE/photos/` | reference once the loom is gone | 0.12 |
| T-019 | Find and log the wideband tap and every PO splice | K-001, K-002 | 0.13 |
| T-029 | Battery terminal type — SAE or 3/8 threaded. **Look at it** | `V-053`, decides the lugs | 0.14 |

The three lighting measurements in §6 ride along with this session — same
tape measure, same afternoon.

## 3 · Remaining diagnostics — with the car, no parts

| ID | Task | Closes | Checklist |
|---|---|---|---|
| T-004 | Alternator rating from the FSM or the parts counter (case is unreadable) | `V-002`, `V-019` | 0.4 |
| T-009 | Confirm twin coils + twin igniters under the hood | `V-001` | — |
| T-041 | Confirm the blower is the motor, not the feed — 12 V at the connector with the switch on? (K-023) | sizes nothing; informs T-038 | — |
| T-017 | Verify connector pin labels in `01-REFERENCE/factory-circuits/` against the scans | pin letters are the weak link | before 0.13 |

## 4 · Sourcing, by wave ([`BOM.md`](BOM.md) is the ledger)

| ID | Task | Wave |
|---|---|---|
| T-031 | **Mirrors** — larger, heated, digital; confirm the conductor count (`V-060`; D1/D2 has zero spare cavities) | 4 |
| T-032 | **Fuel-door solenoid** — never existed (D-098); output ruled (`Q-061` → D-180) | 4 |
| T-033 | **Hatch latch switch** — the original is broken (D-098) | 4 |
| T-038 | **Blower motor** — confirmed dead (K-023); O16's fuse comes from its spec (D-126) | before Phase 6 |
| T-039 | Washer pump — only if the post-PMU diagnosis (T-040, D-176) condemns it | post-PMU |
| T-040 | Washer diagnosis — **deferred post-PMU** (D-176) | post-PMU |
| **T-051** | BT817 eval board, then bridge + glass per `V-085` | 3 (module era, D-194) |
| T-048 | Flash and label boards 2 and 3 (headers need the Phase-5 iron) | module era |

## 5 · Done

| ID | Result |
|---|---|
| ~~T-001 T-002 T-003~~ | Meter, Ionic, PMU — bought (`V-016`/`V-017`/`V-018` closed) |
| ~~T-010~~ | Inspection sweep → D-097–D-100 |
| ~~T-011 + T-015~~ | Pop-up pinout off sheet E (`V-030` → D-177); stalls L 12.8 / R 13.1 A |
| ~~T-012~~ | Fuel sender 6 / 31.5 / 80 Ω (`V-037` → D-197) — LADDERS §A7 |
| ~~T-013 T-020 T-042~~ | Sicma geometry confirmed in the hand (D-134, D-139) |
| ~~T-014~~ | **The measurement campaign, complete** (D-175, D-197) |
| ~~T-016~~ | Cancelled — K-008 dies with the harness (D-105) |
| ~~T-021 T-025 T-026 T-027~~ | PMU box inventoried; terminals counted (zero small spares — D-135); first order recorded ([`BOM.md`](BOM.md) §Re-order reference) |
| ~~T-023~~ | Ignition closure off FSM sheet F (`V-050` → D-178) |
| ~~T-030~~ | The five 0.23 packets ruled (`Q-061` → D-180 … `Q-065` → D-184) |
| ~~T-046 T-047~~ | Firmware stages 4–5 passed |
| ~~T-050~~ | Superseded by D-198 — the factory-spec exciter is wired instead of pre-diagnosing; the alternator is replaced only if it refuses on correct wiring |

## 6 · Lighting — deferred (D-201; starts after shakedown, L-004)

None of these blocks the electrical rebuild. The three measurements need only
a tape measure or a torch and ride along with the §2 session.

| ID | Task | Closes | Blocks |
|---|---|---|---|
| **T-034** | **Measure the tail light aperture** — width, height, depth, mounting | `V-063` | The entire tail light design (TL-1). The 5 cm reverse / 2.2 cm strip figures assume a 30 cm aperture |
| **T-035** | **Confirm 7-inch round or rectangular sealed beams** on this car, and what is actually fitted today | `V-066` | Whether the headlamp needs an adapter plate; settles the [`../01-DESIGN/LOADS.md`](../01-DESIGN/LOADS.md) vs [`TAIL-LIGHTS.md` (archived)](../../../99-ARCHIVE/2026-08-31_lighting-body/TAIL-LIGHTS.md) disagreement |
| T-036 | Answer `Q-048` — which headlamp unit | `Q-048` | The headlamp order |
| T-037 | Source **DOT/SAE LED modules** with published candela, red and white | `V-064` | The tail light build (TL-4). Photometry is the hard part, not area |

The build-phase steps (TL-1 … TL-19) are [`TAIL-LIGHTS.md` (archived)](../../../99-ARCHIVE/2026-08-31_lighting-body/TAIL-LIGHTS.md) §4.

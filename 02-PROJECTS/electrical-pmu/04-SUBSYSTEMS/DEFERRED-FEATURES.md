# DEFERRED FEATURES — pre-wired, waiting on budget

*Created 2026-08.*

Everything the harness is **built to accept but not yet fitted.** The point of
this file is that none of these require harness work later — the wire is run,
terminated and capped, and adding the feature is plug, populate, configure.

**This is D-004 paying off.** A capped spare costs a wire now. A re-pin costs a
housing, a teardown and a weekend.

---

## The rule

| Now | Later |
|---|---|
| Wire run, terminated, **capped at both ends** | Uncap |
| Cavity allocated in the housing | Already there |
| Relay socket fitted, **empty** | Populate |
| Fuse position provisioned, **empty** | Fit the fuse |
| PMU channel allocated, **output disabled** | Enable in config |
| Ladder/logic written but inactive | Turn on |

**No harness work. No connector opened. No panel removed.**

---

## 1 · Power windows `[D-131]`

**The windows are currently manual.** No motors, regulators, switches or factory
wiring.

### Pre-wired and capped

| Item | Location | State |
|---|---|---|
| Motor bus feed to the sill | `L4-P` cav 3, 12 AWG | Terminated, capped |
| Window commands ×4 | `L4-M` cav 9–12, 16 AWG | Terminated, capped |
| Motor legs, driver | `D1` cav 1–2, 14 AWG | Terminated, capped **in the door** |
| Motor legs, passenger | `D2` cav 1–2, 14 AWG | Terminated, capped in the door |
| Switch inputs ×4 | `L3-S`, 16 AWG | Terminated, capped at the switch panel |
| K5–K8 relay sockets | Sill node | **Fitted, empty** |
| F8, F9 fuse positions | Sill node | **Provisioned, empty** |

### To add later

| Item | ~$ |
|---|---|
| Window regulators with motors ×2 | 150–400 |
| Window switches ×2 or a 2-gang panel | 30–80 |
| ISO micro relays ×4 | 20–40 |
| Fuses ×2 | 2 |
| Door card modification if needed | — |

**Work:** fit regulators, plug in, populate four relays, fit two fuses, enable
the outputs and the interlock logic in the PMU. **An afternoon.**

**Interlock to enable at the same time:** never up and down on the same window;
never both windows plus both pop-ups simultaneously on O1.

---

## 2 · Heated seats

| Pre-wired | State |
|---|---|
| Comfort bus O15 → `L3-P` cav 2, 12 AWG | **Live** — the bus itself is built |
| F10 branch fuse position | Provisioned |
| DCU switching channel | Allocated, unpopulated |

**To add:** 2 × elements (~4 A each), fitted **during an upholstery pass**.

> **The one thing that isn't plug-and-play.** Elements go under the seat cover.
> If the seats ever come out for retrim, fit the elements then even if the
> switching isn't built — the wiring can wait, the upholstery can't.

---

## 3 · Cooled seats

Same comfort bus. 2 × fan modules, ~1.5–2.5 A each, plus ducting.

**Same upholstery-pass rule**, and more invasive than heat — the fan needs a
path through the cushion.

`[Q-013]` said in scope. Realistically this is the last thing to arrive.

---

## 4 · Heated mirrors

| Pre-wired | State |
|---|---|
| Mirror heat feed | `D1`/`D2` cav 7, 16 AWG, capped |
| Mirror heat branch fuse | Sill node, provisioned |

Bundled with the new mirrors `[T-031]` — larger, heated, digital control. The
door connector already carries three motor conductors plus heat, exactly 8
cavities with zero spare (D-092/093).

---

## 5 · Heated washer nozzles and wiper park de-icer

Comfort bus, F11 branch. ~1–2 A and ~2–3 A.

Cold-weather items. Low cost, low effort, high value in a Fort Collins winter.

---

## 6 · Radar subsystem

Concealed sensors front and rear, DCU-managed `[V-061]`. Front sensor conductors
in `L2`, rear in `L4`. Interface not yet designed.

---

## 7 · LS swap

| Reserved | Where |
|---|---|
| O13 — LS ECU + injectors, 25 A | `L1-P` cav 2, capped |
| O14 — LS cooling fans, 25 A | `L1-P` cav 3, capped |
| CAN2 drop for the ECU | `L1-S`, with the **120 Ω terminator fitted now** |
| Sensor spares ×6 | `L1-S`, capped |
| 2 AWG main feed | Sized for the LS, not the 12A (D-091) |

**The far-end CAN terminator goes in during Phase 5**, capped, so the bus is
electrically correct before the ECU exists (D-079).

---

## Summary — what the harness is already built for

| Feature | Harness ready | Hardware needed | Rough $ |
|---|---|---|---|
| Power windows | ✅ | Regulators, switches, 4 relays | 200–520 |
| Heated seats | ✅ | Elements ×2 | 60–150 |
| Cooled seats | ✅ | Fan modules ×2 | 150–400 |
| Heated mirrors | ✅ | Bundled with new mirrors | — |
| Heated nozzles, de-icer | ✅ | Nozzles, heater strip | 80–200 |
| Radar | ✅ conductors | Sensors, DCU integration | 150–400 |
| LS swap | ✅ | Engine, ECU, fans | — |

**Every one of these is an afternoon of fitting, not a harness job.** That is the
entire return on terminating all 39 cavities and running capped spares.

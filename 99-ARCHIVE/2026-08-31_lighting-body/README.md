# LIGHTING & BODY

*Rev 2026-08-30 · owns: the scope and status of the lighting and body project — created 2026-08 by splitting lighting out of the electrical project (D-123). Its decisions are [`DECISIONS.md`](DECISIONS.md)'s, its open items [`OPEN.md`](OPEN.md)'s, its tasks [`TASKS.md`](TASKS.md)'s, its money [`BOM.md`](BOM.md)'s.*

**Status: NOT STARTED. Deferred until the electrical rebuild is finished and
shaken down (L-004).** The only live work is four measurements Camden can take
any time ([`TASKS.md`](TASKS.md)).

---

## Why this is a separate project

The electrical rebuild does not need it. **The car migrates, drives and shakes
down entirely on stock incandescent bulbs** (D-119) — every lamp channel has
40–74% headroom on filament, wire gauge is set by voltage drop rather than
current, and the stock dual-filament rear bulb maps perfectly onto the two-channel
tail/brake design with no backfeed and no driver board.

Lighting was creeping into the electrical project's critical path and adding
scope, cost and fabrication to something that already runs to 500+ hours. It is a
**bodywork and fabrication project that happens to involve wiring**, not an
electrical project.

Same reasoning that keeps the DCU off the critical path (D-081): finish the car,
then add.

## What moved here

| From electrical | Now |
|---|---|
| Custom LED tail lights (D-107, D-111) | This project |
| Headlamp change to a rectangular unit (D-110) | This project |
| Full LED bulb conversion | This project |
| `Q-048` headlamp unit choice | [`OPEN.md`](OPEN.md) |
| `V-063` tail light aperture | [`OPEN.md`](OPEN.md), `T-034` |
| `V-064` DOT LED module sourcing | [`OPEN.md`](OPEN.md), `T-037` |
| `V-066` round vs rectangular sealed beams | [`OPEN.md`](OPEN.md), `T-035` |
| Tasks T-034 … T-037 | [`TASKS.md`](TASKS.md) |
| ~$400–980 of lighting BOM | [`BOM.md`](BOM.md) |

## What stayed in electrical

**Everything about how power reaches a lamp.** Channels, wire gauge, connectors,
soft fuses, flash logic. The electrical project delivers working lamp circuits
with stock bulbs on them.

| Stays | Why |
|---|---|
| O2, O3, O6, O7, O17, O18, O19, O20 allocation | Unchanged regardless of bulb |
| 14 and 16 AWG lamp wiring | Set by voltage drop, not current |
| L2-M, L4-M cavity assignments | Unchanged |
| Turn signal flash logic on the PMU | Works with either bulb type |
| Inrush configuration (D-120) | **Needed for incandescent** — filament inrush is the harder case |

## Scope

### Lighting
- [ ] Custom rear LED strip — thin, stock aperture, white reverse inboard. See [`TAIL-LIGHTS.md`](TAIL-LIGHTS.md)
- [ ] Headlamp units — shorter rectangular, DOT-compliant, inside the retained pop-up buckets
- [ ] LED conversion of every remaining lamp: park, marker, plate, interior, glovebox, luggage, illumination
- [ ] Driver PCB ×2 for the tail lights
- [ ] Re-set every lamp soft fuse after the change (D-122)

### Body — to be scoped
- [ ] Rust survey and repair (K-007)
- [ ] Paint
- [ ] Trim and seals
- [ ] Anything the lighting fabrication touches — bezels, apertures, mounting

## Dependencies

**Hard prerequisite: the electrical rebuild is finished and shaken down.**
Specifically Phases 6, 7 and 8 complete, factory harness out, car driving on the
PMU with stock bulbs and soft fuses set from measurement.

**Then** this project can change bulbs and re-set those fuses as a second pass.

## Files

| File | Holds |
|---|---|
| [`TAIL-LIGHTS.md`](TAIL-LIGHTS.md) | Custom LED strip design, FMVSS area math, reverse sizing, headlamp guidance, process TL-1 … TL-19 |
| [`DECISIONS.md`](DECISIONS.md) | Inherited D-107/110/111 and local L-001 … L-004 |
| [`OPEN.md`](OPEN.md) | Q-048, V-063, V-064, V-066 |
| [`TASKS.md`](TASKS.md) | T-034 … T-037 — the measurements that need nothing else |
| [`BOM.md`](BOM.md) | The lighting money, ~$400–980 |
| *(body files to come)* | |

## The two things to remember when this starts

**Soft fuses set against incandescent are far too generous for LED.** A tail
circuit set at 6 A does not protect a 3 A LED load. Every lamp circuit gets
re-measured (D-122, L-003). The second-pass table is already waiting in
[`../electrical-pmu/05-BUILD/MIGRATION-LOG.md`](../../02-PROJECTS/electrical-pmu/04-BUILD/MIGRATION-LOG.md).

**Headlamps are not a custom-build item.** A strip of LEDs cannot produce a beam
cutoff, and no care in fabrication fixes that — the optic is the problem. Source
a DOT-compliant sealed unit. Tail lights are a reasonable custom project;
headlamps are not.

---

## LED bulb conversion — the full list

Moved here from the electrical project 2026-08 (D-123). **Every one of these
stays stock incandescent until the electrical rebuild is finished.**

| Circuit | Now | Becoming |
|---|---|---|
| Tail / park / marker / plate | 8 W, 3.8 W, 6 W incandescent ×8 | LED |
| Brake | 27/8 W dual filament ×2 | **Custom strip** (D-107) |
| Turn front | 27 W ×2 | LED |
| Turn rear | 27 W ×2 | **Custom strip** |
| Turn indicators | 3.4 W ×2 | LED |
| Reverse | 27 W ×2 | **Custom strip, white section** |
| Interior + spot | 5 W | LED |
| Glove box | 3.4 W | LED |
| Luggage compartment | ~5 W | LED |
| Illumination bus | 3.4 / 1.4 W ×7 | LED |
| **Headlight LOW / HIGH** | `V-066` confirm what's fitted — [`LOADS.md`](../../02-PROJECTS/electrical-pmu/01-DESIGN/LOADS.md) says LED housings, [`TAIL-LIGHTS.md`](TAIL-LIGHTS.md) §8 says 7-inch sealed beams | **DOT rectangular LED unit** (L-002, `Q-048`) |

**Bulb selection is unconstrained.** Bulb-out detection was dropped (D-047), so
draw no longer matters for function. Buy on light output and colour.

### Expected current drop

| Circuit | Incandescent | LED |
|---|---|---|
| Tail bus, 8 lamps | ~4.4 A | ~3.0 A |
| Brake | ~3.9 A | ~0.6 A |
| Turn, per side | ~4.2 A | ~0.65 A |
| Reverse | ~3.9 A | ~0.6 A |
| Interior + illumination | ~2.5 A | ~1.0 A |

**Roughly 5–7× lower on most circuits**, which is exactly why L-003 exists — every
soft fuse set against filament has to be re-measured. The electrical project's
measured incandescent figures (brake 7.0 A, turn 3.4 A per side) are in
[`../electrical-pmu/01-DESIGN/CHANNEL-SCHEDULE.md`](../../02-PROJECTS/electrical-pmu/01-DESIGN/CHANNEL-SCHEDULE.md).

### What does NOT change

**No wiring, no connectors, no cavity assignments, no channel allocation.** Wire
gauge is set by voltage drop and mechanical robustness, not current (D-016). The
electrical project hands this one a complete, working lamp harness.

---

## Body scope — to be developed

| Item | Note |
|---|---|
| Rust survey | K-007 — extent unknown, never assessed |
| Paint | Sunbeam Silver |
| Trim and seals | |
| Tail light apertures and bezels | Where lighting and body meet |
| Pop-up bucket adaptation | If the headlamp unit needs an adapter plate |

**The lighting fabrication and the body work touch the same panels.** Doing them
in one pass is the reason this is one project rather than two.

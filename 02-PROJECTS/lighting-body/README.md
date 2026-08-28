# LIGHTING & BODY

*Created 2026-08 by splitting lighting out of the electrical project.*

**Status: NOT STARTED. Deferred until the electrical rebuild is finished.**

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
| `[Q-048]` headlamp unit choice | This project |
| `[V-063]` tail light aperture | This project |
| `[V-064]` DOT LED module sourcing | This project |
| `[V-066]` round vs rectangular sealed beams | This project |
| ~$345–835 of lighting BOM | This project |

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
- [ ] Custom rear LED strip — thin, stock aperture, white reverse inboard. See `TAIL-LIGHTS.md`
- [ ] Headlamp units — shorter rectangular, DOT-compliant, inside the retained pop-up buckets
- [ ] LED conversion of every remaining lamp: park, marker, plate, interior, glovebox, luggage, illumination
- [ ] Driver PCB ×2 for the tail lights
- [ ] Re-set every lamp soft fuse after the change (D-122)

### Body — to be scoped
- [ ] Rust survey and repair `[K-007]`
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
| `TAIL-LIGHTS.md` | Custom LED strip design, FMVSS area math, reverse sizing, headlamp guidance |
| *(body files to come)* | |

## The two things to remember when this starts

**Soft fuses set against incandescent are far too generous for LED.** A tail
circuit set at 6 A does not protect a 3 A LED load. Every lamp circuit gets
re-measured. The second-pass table is already waiting in
`../electrical-pmu/05-BUILD/MIGRATION-LOG.md`.

**Headlamps are not a custom-build item.** A strip of LEDs cannot produce a beam
cutoff, and no care in fabrication fixes that — the optic is the problem. Source
a DOT-compliant sealed unit. Tail lights are a reasonable custom project;
headlamps are not.

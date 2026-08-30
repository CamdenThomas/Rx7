# HEAD UNIT

*Rev 2026-08 · owns: audio, maps and the double-DIN install*

A double-DIN head unit with **wireless CarPlay**. Provides maps, the road-preview
minimap, iPhone audio and the controls.

---

## What it does

| Function | Source |
|---|---|
| Maps, road-preview minimap | CarPlay |
| Audio from iPhone | CarPlay / Bluetooth |
| Controls | Head unit, plus optional external buttons |
| Amp feed | Pre-outs |

## What it does NOT touch

| | |
|---|---|
| ICU | Gauges and engine sensor acquisition only (D-130). No map, no BLE module |
| DCU | Climate and comfort only. Audio is not its job |
| CAN2 | The head unit is not a bus node |
| Pin plan | **Unchanged** |

---

## Wiring — already allocated, never removed

| Circuit | Channel | Connector |
|---|---|---|
| Switched feed | O10 | `L3-M 1`, 14 AWG |
| Constant keep-alive | **Busbar F1, not the PMU** | `L3-M 2`, 14 AWG |
| Amp remote turn-on | O10 | Accessory branch |
| Speakers | — | Independent of the PMU entirely |

**Amp main power comes off the rear ANL block at the battery**, never through the
panel.

**The constant feed is off the busbar deliberately** (D-020). The PMU sleeps; a
head unit clock that loses time every night is worse than one fuse.

K11, the constant-bus master, can drop that feed on a long park so the clock
can't flatten the lithium.

---

## Selection criteria

| Requirement | Why |
|---|---|
| **Double-DIN** | Aperture already in the dash plan |
| **Physical buttons** | A touchscreen volume slider in a moving car is a mistake you notice every drive |
| **Variable LED button colour — set to green** | Matches the illumination scheme |
| **Wireless CarPlay** | No cable to the phone. Most of what makes an install look clean |
| **Full passthrough — critical** | Pre-outs, full-range, unprocessed, feeding the external amp |
| An integrable bezel | Rather than obviously aftermarket in a 1982 dash |

> **Passthrough is the hard requirement.** Many units advertise pre-outs but
> band-limit them or apply fixed EQ that can't be defeated. Confirm the signal
> reaching the amp is full-range and unprocessed before buying.

---

## Known limitation

The map needs cell signal. No coverage means no map, which matters in the canyons
west of town.

# HEAD UNIT

*Rev 2026-08 · owns: audio, maps and the double-DIN install*

**Decision: a double-DIN head unit with wireless CarPlay** (D-128).

It provides maps, the road-preview minimap, iPhone audio and the controls. The
ICU stays gauges-only.

---

## Why a head unit and not something custom

Three alternatives were designed out in detail and rejected:

| Rejected | Why |
|---|---|
| Hidden Bluetooth A2DP module + no screen | Gets audio, gets no map |
| Turn-by-turn text on the ICU via BLE | Gets instructions, not the road-preview picture that was the actual requirement |
| Raspberry Pi rendering an offline OSM minimap | 60–120 hrs of firmware, plus a second display subsystem on the critical path |

The full reasoning is archived at
`99-ARCHIVE/2026-08_infotainment-options-considered.md`. It stays available
because the Pi path is genuinely buildable later, on a finished car, if the
offline aspect ever becomes the thing that matters.

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

## Selection `[Q-055]`

Worth paying for:

| Feature | Why |
|---|---|
| **Wireless CarPlay** | No cable to the phone. Most of what makes an install look clean |
| **Physical volume knob** | A touchscreen volume slider in a moving car is a mistake you notice every drive |
| **Pre-outs**, not speaker-level only | Feeds the amp properly |
| External control input | If buttons are wanted on the keypad or column |
| An integrable bezel | Rather than obviously aftermarket in a 1982 dash |

**Double-DIN aperture** is already in the dash plan.

---

## The trade, stated plainly

A bright modern screen in a 1982 dash, and a map that needs cell signal — no
coverage means no map, which matters in the canyons west of town.

Both were considered and accepted in exchange for the feature existing this year
instead of in 2028.

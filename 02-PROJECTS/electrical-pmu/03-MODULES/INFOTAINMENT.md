# INFOTAINMENT — maps and audio without a head unit

*Added 2026-08. Answers: can the cluster display maps, and can a Teensy route
iPhone audio to the amp?*

**Short version: audio is easy and needs no microcontroller at all. Maps on a
Teensy are not possible, but there are three real paths to maps that preserve the
no-visible-head-unit aesthetic.**

---

## 1 · Audio — easier than you think

**This needs no MCU.** Not the DCU, not the ICU, nothing.

```
   iPhone ──Bluetooth A2DP──> receiver module ──line out──> amp ──> speakers
```

A Bluetooth A2DP receiver module is $15–40, hides anywhere, and does exactly what
you want: phone audio in, analogue line level out.

| What you get | How |
|---|---|
| Music from the phone | A2DP, automatic on pairing |
| Play / pause / next / previous | **AVRCP** — buttons on the keypad or steering wheel wired to the module |
| Volume | At the amp, or AVRCP |
| Call audio | HFP if the module supports it, plus a mic |

**Why not the Teensy:** the Teensy 4.1 has **no Bluetooth radio.** You would need
to add one anyway, at which point the module *is* the solution and the Teensy is
just a passenger. An ESP32 has Bluetooth Classic and can do A2DP sink, but you'd
be writing an audio stack to replicate a $20 part.

**Why not wired from the iPhone:** digital audio out of a Lightning or USB-C
iPhone to a non-Apple device requires an **MFi authentication chip**, and the MFi
programme is not open to individuals. Analogue via a headphone dongle works but
is a worse signal path than Bluetooth for a car.

`[Q-049]` — pick a module. Look for **aptX or AAC support** (iPhone uses AAC),
a clean line-level output, and AVRCP button inputs.

---

## 2 · Maps — the honest assessment

### What a Teensy 4.1 cannot do

**Render a map.** Not a limitation of skill or effort — it's the wrong class of
device.

| Requirement | Teensy 4.1 |
|---|---|
| Network for tiles | No radio |
| Tile storage and cache | 8 MB PSRAM max. A city is gigabytes |
| Vector map rendering | No GPU, no graphics stack |
| Route calculation | No |
| **CarPlay** | **Requires MFi certification. Not available to individuals** |
| **Android Auto** | Reverse-engineered implementations exist, but need Linux |

CarPlay is the one to be clearest about: **it is not obtainable.** Apple licenses
it to vehicle manufacturers and MFi-certified accessory makers. There is no
hobbyist path, legal or technical.

### What a Teensy 4.1 *can* do — turn-by-turn without a map

This is the part worth knowing. **You can get the navigation instruction without
the map picture.**

An iPhone broadcasts notifications over BLE via **ANCS** (Apple Notification
Center Service). A BLE-capable companion chip can subscribe and receive
navigation prompts — next manoeuvre, street name, distance.

```
   ┌──────────────────────────────┐
   │  ↰  Turn left                │
   │     Mulberry St              │
   │     0.3 mi                   │
   └──────────────────────────────┘
```

Rendered as a strip between the gauges, in the cluster's own typeface, at the
cluster's own brightness. **No map, no bright rectangle, no Google logo.**

For a lot of driving, that is genuinely all you use a map for.

**Cost:** one BLE module and firmware work. **Fits the existing ICU** with no
architectural change.

`[Q-050]` — is turn-by-turn text enough, or do you actually want the map picture?

---

## 3 · If you want the real map — three options

### Option A · Small dedicated map display, driven by a Pi

| | |
|---|---|
| Hardware | Raspberry Pi Zero 2 W or Pi 4, small TFT, its own power |
| Maps | Real. Navit, or a browser, or an Android Auto implementation |
| Boot | 20–30 seconds |
| Cluster | **Untouched.** Teensy ICU keeps every gauge |
| Aesthetic | A second small screen — sited low, in the console, or in a bezel |

**This is the option that preserves everything you already decided.** The Pi is
allowed to be slow and crash-prone because nothing safety-visible depends on it.

### Option B · Phone mirroring over HDMI

| | |
|---|---|
| Hardware | Apple Lightning/USB-C → HDMI adapter, HDMI display |
| Maps | Real — the phone renders, whatever app you like |
| Boot | Instant |
| Downside | **Mirrors the whole phone screen**, not a map region. Wrong aspect ratio, notifications visible |

Cheapest and simplest. Least elegant.

### Option C · Pi renders the entire cluster

**Do not do this.** Recorded so it's a decision, not an oversight.

It would put maps and gauges on one panel — exactly what you asked for. But it
means **the tachometer, coolant temperature and oil pressure depend on Linux
booting and staying up.** SD card corruption, a 25-second boot before you have a
tach, a kernel panic taking your gauges with it.

This is the same failure-domain argument that moved sensor acquisition into the
ICU (D-083). Having made that call deliberately, undoing it for a map would be
the single largest step backwards available in this project.

---

## 4 · Recommended architecture

```
   SAFETY-VISIBLE                    CONVENIENCE
   ┌────────────────────┐            ┌──────────────────┐
   │  ICU · Teensy 4.1  │            │  BT audio module │──> amp
   │  gauges + sensors  │            └──────────────────┘
   │  + turn-by-turn    │
   │    text strip      │            ┌──────────────────┐
   └────────┬───────────┘            │  Pi + small TFT  │  optional
            │ BLE                    │  real maps       │
            ▼                        └──────────────────┘
        iPhone (ANCS)
```

| Function | Device | Fails how |
|---|---|---|
| Gauges, sensors | Teensy ICU | Cluster dark. Nothing else affected |
| Turn-by-turn text | Teensy ICU + BLE | Text strip blank. Gauges fine |
| Audio | BT module | No music. Nothing else affected |
| Real maps | Pi, if fitted | Map screen blank. **Gauges completely unaffected** |
| Climate | Teensy DCU | Climate stops. Gauges fine |

**Four independent failure domains. Nothing that matters depends on anything that
doesn't.**

---

## 5 · What this changes in the existing plan

| Area | Change |
|---|---|
| Pin plan | **None** |
| Harness | **None** — audio already has O10 switched and a fused constant |
| ICU hardware | **Add a BLE module** if turn-by-turn is wanted. Small |
| DCU | **No change.** It stays a climate controller. Audio is not its job |
| Head unit | **Deleted from the plan** if this path is taken — see below |

### Deleting the head unit

If audio becomes a hidden BT module, the double-DIN head unit (D-051) is no
longer needed. That removes:

- The double-DIN aperture and its dash fabrication
- The switched feed and the fused constant keep-alive on L3-M
- ~$200–400 from the BOM
- A bright screen you said you didn't want

`[Q-051]` — delete the head unit and go hidden-module?

---

## 6 · Open questions

| ID | Question |
|---|---|
| Q-049 | Which Bluetooth A2DP module — AAC support, line out, AVRCP button inputs |
| **Q-050** | **Is turn-by-turn text enough, or do you want the map picture?** Decides whether a Pi enters the project at all |
| Q-051 | Delete the head unit in favour of a hidden BT module? |
| Q-052 | If a Pi is fitted — where does its display live so it isn't a bright rectangle? |

## 7 · The one-line answer

**Audio: yes, trivially, and it needs no processor.** **Maps in the cluster: not
on a Teensy — but turn-by-turn text is, and that may be all you actually use.**
If you want the map picture, it belongs on a separate device that is allowed to
fail without taking your tachometer with it.

---

# 8 · REVISED — the minimap use case

*2026-08. Supersedes §2's framing. The requirement is different from what I
assumed and the answer changes.*

## What you actually want

**Not navigation. Road preview.** A rolling, heading-up view of the road geometry
ahead so you can read the bends and plan a line — the Forza minimap, or what
luxury cars call predictive curve display.

**This is a much smaller problem than Google Maps**, and it changes the
recommendation.

| Google Maps needs | A minimap needs |
|---|---|
| Live network for tiles | **Nothing. Offline vector data** |
| Search, POI, traffic | No |
| Route calculation | No |
| Address geocoding | No |
| Turn-by-turn voice | No |
| | **Road centrelines, your position, your heading** |

That is genuinely renderable on modest hardware, offline, forever.

## Why offline is an advantage here, not a compromise

An OpenStreetMap vector extract for **Colorado is a few hundred megabytes.** The
whole US is ~10 GB. Either fits on a cheap SD card.

**No cell signal required.** In the canyons west of Fort Collins that is not a
minor point — it's the difference between a map that works where you actually
want it and one that greys out exactly when the road gets interesting.

CarPlay cannot do this. It needs the phone's data connection.

---

## The three real paths, re-ranked for this requirement

### Path 1 · CarPlay head unit — best effort-to-result ratio

Since you said you don't mind a central display: **a modern head unit with
wireless CarPlay does this today, for $200–400, with zero development.**

| | |
|---|---|
| Effort | Buy it, wire it |
| Result | Exactly the thing you've seen and liked |
| Downsides | Bright screen. Needs cell data. Aesthetically a modern unit in a 1982 dash |

**If the goal is to have the feature, this is the honest answer.** Everything
below is more work for a more integrated result.

### Path 2 · Pi minimap on its own display — the middle path

| | |
|---|---|
| Hardware | Pi Zero 2 W or Pi 4, small TFT, **GPS module (~$20)** |
| Map data | Offline OSM vector extract, road layers only |
| Render | Heading-up, roads only, cluster colours, no labels, no clutter |
| Boot | 10–25 s depending on image |
| **Cluster** | **Untouched. Teensy ICU keeps every gauge** |

**A roads-only renderer is genuinely tractable.** You're drawing polylines from
vector tiles with a rotation transform. That's not a mapping stack, it's a
drawing program with a spatial index. MapLibre GL Native will do it out of the
box, or a custom renderer gets you exactly the aesthetic you want.

You already have a CS background and 155–325 hours budgeted for firmware. This
is squarely inside that.

### Path 3 · Pi drives the whole cluster — reconsidered

I argued against this last time. **With mitigations it's more defensible than I
made it sound**, and it's the only path that puts the minimap *between* the
gauges on one panel, which is what you asked for.

**The risk is real:** gauges depend on Linux booting and staying up.

**The mitigations are also real:**

| Risk | Mitigation |
|---|---|
| SD corruption | **Read-only root filesystem** with overlayfs. The standard fix, and it works |
| Slow boot | Minimal image, no desktop, systemd tuned. **8–12 s is achievable** |
| Kernel panic / hang | **Hardware watchdog**, enabled by default on the Pi |
| Application crash | systemd auto-restart |
| **Total loss of gauges** | **The Teensy still acquires every sensor and publishes on CAN.** Add a small independent readout, or keep the factory cluster (Q-039 already says keep it) |

**The key structural point:** even in Path 3, the **ICU Teensy still owns sensor
acquisition** (D-083). The Pi is a *display client* reading CAN. If the Pi dies,
the data still exists — you've lost the screen, not the measurement. That is a
meaningfully better position than putting senders on the Pi.

**Boot behaviour matters more than crash behaviour.** You start the car and want
a tachometer immediately. A 10-second black cluster on every cold start is the
thing you'd actually live with, and it's why the factory cluster staying in place
during development is worth more than it looked.

---

## Recommended architecture — Path 2 or 3

```
   ┌──────────────────────┐        ┌────────────────────────┐
   │  ICU · Teensy 4.1    │  CAN2  │  Pi · minimap renderer │
   │  ─ all sensors       │───────>│  ─ offline OSM roads   │
   │  ─ publishes 0x200   │        │  ─ GPS heading-up      │
   │  ─ drives gauges     │        │  ─ optional: gauges too│
   └──────────────────────┘        └────────────────────────┘
            │                                │
        gauge TFTs                      map display
   
   Path 2: two displays, two bezels, gauges never depend on Linux
   Path 3: one panel, Pi draws everything, Teensy still owns the data
```

**Either way the Teensy keeps sensor acquisition.** That decision (D-083) survives
both paths and it's the one that matters.

## Hardware this adds

| Item | ~$ | Note |
|---|---|---|
| Raspberry Pi 4 (2 GB) or Zero 2 W | 15–55 | Pi 4 if it drives the whole cluster |
| **GPS module** — UART or USB | 15–25 | Position and heading. Heading is reliable above ~5 mph |
| microSD, endurance grade | 12–20 | **High-endurance card.** Ordinary cards die in cars |
| Display | 60–200 | Same `[Q-037]` decision as the cluster |
| CAN interface for the Pi | 10–25 | MCP2515 HAT, to read the ICU's 0x200 |
| 12 V → 5 V supply, automotive | 20–40 | Same protection chain as the Teensys (D-088) |
| **Graceful shutdown circuit** | 10–20 | **Do not just cut power to a Pi.** Supercap or delay circuit + shutdown signal |

**~$140–385.**

## The one thing people get wrong

**Never cut power to a running Pi.** That is what corrupts SD cards, and in a car
it happens every time you turn the key. Two fixes, use both:

1. **Read-only root filesystem.** Nothing to corrupt
2. **A shutdown signal and a hold-up capacitor.** The PMU can tell the Pi "key
   off" over CAN or on a discrete line; the Pi shuts down cleanly while a
   supercap holds the rail for ten seconds

The PMU already has the key state and a programmable shutdown delay (O22
keep-alive). **This is a config problem you've already solved for other reasons.**

---

## Open questions, revised

| ID | Question |
|---|---|
| **Q-053** | **Path 1, 2 or 3?** CarPlay head unit, Pi on its own display, or Pi drives the whole cluster |
| Q-050 | *(superseded — you want the map picture, not turn-by-turn text)* |
| Q-051 | Head unit still deleted? Path 1 brings it back |
| Q-054 | If Pi: which map renderer — MapLibre GL Native, or a custom roads-only renderer for the exact aesthetic |
| Q-052 | Display siting |

## Honest summary

**Path 1 gets you the feature this month for $300 and no work.**

**Path 2 gets you a better-integrated, offline, works-in-the-canyons version for
similar money and maybe 60–120 hours.**

**Path 3 gets you exactly the picture in your head — gauges and minimap on one
surface — at the cost of your cluster depending on Linux, which is manageable but
is a genuine step away from a principle you've otherwise held to.**

The offline aspect is the reason I'd lean Path 2 over Path 1 despite the effort.
A map that works where the cell signal doesn't is a better map for the driving
you're describing.

---

# 9 · DECIDED — head unit (D-128)

**Path 1. A CarPlay head unit. Everything below in §1–§8 is background.**

The Pi minimap is not being pursued. It was 60–120 hours of firmware on top of a
project already at 500–900, to produce something similar but offline.

## What's live

| Function | How |
|---|---|
| Maps, minimap road preview | **Head unit, CarPlay** |
| Audio from iPhone | **Head unit** |
| Controls | **Head unit** |
| Gauges, engine sensors | **ICU Teensy, unchanged** |
| Climate, comfort | **DCU Teensy, unchanged** |

## What's dead

- Hidden Bluetooth A2DP module — the head unit does audio
- Turn-by-turn text strip on the cluster — no BLE module on the ICU
- Raspberry Pi, GPS module, offline OSM data, graceful-shutdown circuit
- Any map function on the ICU

**The ICU is back to exactly what D-083 specified:** display plus engine sensor
acquisition, one failure domain, no dependencies.

## Wiring — no change

The head unit allocation was never removed from the plan:

| Circuit | Channel | Connector |
|---|---|---|
| Switched feed | O10 | `L3-M 1` |
| Constant keep-alive | Busbar **F1**, not the PMU | `L3-M 2` |
| Amp remote turn-on | O10 | via the accessory branch |
| Speakers | — | Independent of the PMU entirely |

**Amp main power comes off the rear ANL block at the battery**, never through the
panel.

## Selection — `[Q-055]`

Worth paying for:

| Feature | Why |
|---|---|
| **Wireless CarPlay** | No cable to the phone. The whole point of a clean install |
| **Physical volume knob** | A touchscreen volume slider in a car is a mistake |
| Steering-wheel / external control input | If buttons are wanted on the keypad or column |
| Pre-outs, not just speaker level | Feeds the amp properly |
| A bezel that can be integrated | Rather than obviously aftermarket in a 1982 dash |

**Double-DIN aperture** is already in the dash plan.

## The trade, stated plainly

A bright modern screen in a 1982 dash, and a map that needs cell signal. Both
considered, both accepted. If the offline aspect ever becomes the thing that
matters — a canyon road with no bars — §8 is still here and the Pi path is still
buildable later, on a finished car, as its own project.

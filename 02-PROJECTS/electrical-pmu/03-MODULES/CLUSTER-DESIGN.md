# CLUSTER DESIGN — forward scope

*Rev 2026-08 · owns: cluster features NOT yet built*

> **The driving cluster is built.** Layout, palette, widgets and rendering live
> in `firmware/icu/cluster_core.h`, which owns them. Design decisions are
> recorded as D-151 through D-158.
>
> **This file is what comes next** — the multi-page architecture, the diagnostics
> page, the trip page. None of it exists yet.

---

## The realisation that changes everything

**800 × 480 at 8 bpp is 384 KB. The Teensy 4.1 has 1 MB of RAM.**

**The framebuffer fits in RAM.**

That decouples two things I had been treating as one:

| | Cost | Constraint |
|---|---|---|
| **Composing** the image in RAM | CPU cycles at 600 MHz | Effectively free |
| **Transmitting** changed pixels over SPI | 6 MB/s | The only real limit |

So you can render **anything you like** into the buffer — gradients, blends,
sub-pixel positioning, complex curves, dithering — and still only send the
rectangles that changed.

**Complexity of drawing is free. Only motion costs.**

Add PSRAM to the 4.1's pads and you get 8 MB more, enough for double-buffering
and off-screen composition.

---

## The static layer is free forever

Drawn once at boot, never touched. **Boot time is the only cost, and 384 KB is
64 ms.** You could redraw the entire background ten times during startup and
nobody would notice.

**So make it elaborate.** Things that cost nothing after boot:

| Idea | Note |
|---|---|
| Fine engraved-looking scale, tick lengths varying by decade | Technical-instrument feel |
| Dim graph-paper grid behind the whole panel | Sets a tone in one pass |
| Corner brackets and registration marks, drafting style | |
| Custom pixel typography drawn as rectangles | No font library, total control |
| Concentric arcs, hairlines, dividers | |
| A dim `12A` or `SA22C` wordmark | Quiet, yours |
| Dithered fade at the panel edges | Costs nothing after boot |
| Fine bezel shading around each readout | Depth without gradients at runtime |

**Rule: anything that never moves can be as intricate as you like.**

---

## Multi-page architecture — the second unlock

**Pages you only read while stationary do not need 30 fps.**

A full-screen redraw is 64 ms. As a page *transition* that is imperceptible. So a
diagnostic page can redraw entirely on entry and then update lazily.

| Page | Refresh | Constraint |
|---|---|---|
| **1 · DRIVE** | 30 fps, dirty rects | The disciplined one |
| **2 · PERFORMANCE** | 30 fps, small moving elements | G-meter, incline |
| **3 · DIAGNOSTICS** | 2–5 fps, full redraw acceptable | Stationary use |
| **4 · TRIP / LOG** | 1 fps | Stationary use |

Page switching from the CAN keypad, or a long-press on a wink switch.

---

## Page 2 · Performance

The IMU is already specified (D-109), so this costs a $5 part and some maths.

### Lateral / longitudinal G

A dot moving inside a static circle. **Erase old position, draw new** — a 20×20
dot is 400 px per position, **800 px per frame total.** Trivial.

| Element | Static or moving |
|---|---|
| Circle, crosshair, 0.2 g rings, labels | **Static — free** |
| The dot | 800 px/frame |
| Peak-hold ghost dots | 400 px each, only on new peak |
| Numeric readouts | Digit-diff only |

**Peak-hold is nearly free and genuinely useful** — leave a dim marker at the
maximum reached, reset on a button.

### Incline — pitch and roll

Same IMU. A horizon line rotating, or two simple bars.

**A rotating horizon line is the one expensive element here** — it sweeps a wide
area. Cheaper: two independent bars, one for pitch, one for roll, each a
segmented bar like the tach. Or a small tilting rectangle rather than a full-width
line.

`[Q-057]` — rotating horizon, or two bars? The bars are far cheaper and arguably
more readable at a glance.

---

## Page 3 · Circuit diagnostics — the one nothing else can do

**The PMU publishes per-channel current on CAN (0x130, multiplexed).** No factory
car and very few aftermarket clusters can show you this.

```
  CH   CIRCUIT           CURRENT   LIMIT   STATE
  O1   MOTOR BUS         ▮▮▮░░░░░   0.0 A   OFF
  O2   HEADLIGHT LOW     ▮▮▮▮▮▮░░   9.8 A   ON
  O6   TAIL/PARK         ▮▮▮░░░░░   4.4 A   ON
  O8   WIPER LOW         ░░░░░░░░   0.0 A   OFF
  ...
  O16  BLOWER            ▮▮▮▮▮▮▮░  14.2 A   ON
```

**24 channels, one screen.** Live current, the soft-fuse setpoint, and channel
state — on, off, tripped, retrying.

| Why it matters | |
|---|---|
| **A tripped channel names itself** | No hunting for a blown fuse in the dark |
| **Watch a circuit degrade over months** | Rising draw on a motor means bearings |
| **Verify a migration on the spot** | Phase 6 gets faster |
| **Confirm what's actually asleep** | Parasitic draw, visible |

The multiplexed 0x130 message cycles all 24 channels in ~5 s at 5 Hz. **Perfect
for a page you read while parked.**

### Fault history

Log every soft-fuse trip to SD with a timestamp. A sub-page listing the last 20
faults turns "something tripped last week" into a specific channel and time.

---

## Page 4 · Trip and log

| Element | Source |
|---|---|
| Trip distance, avg/max speed | VSS |
| Peak G, lateral and longitudinal | IMU |
| Max RPM, max water temp, min oil pressure | ICU sensors |
| Runtime, battery voltage min/max | PMU |
| SD logging status | Local |

**Min oil pressure and max water temp are the two worth having.** They record the
worst moment of a drive whether or not you were looking.

---

## Is the Teensy the limitation?

**No.** Being specific about where the headroom actually is:

| Resource | Used | Available | Verdict |
|---|---|---|---|
| CPU | Rendering + CAN + 6 ADC + IMU + SD | 600 MHz M7 | **Barely working** |
| RAM | 384 KB framebuffer | 1 MB, plus 8 MB PSRAM optional | Fits |
| CAN | 1 bus used | 3 controllers | 2 spare |
| ADC | 6 sensors | 18 inputs | 12 spare |
| Timers | Tach + VSS capture | Many | Fine |
| **SPI to display** | **6 MB/s** | — | **The only constraint** |

**Nothing on this page is blocked by the Teensy.** G-meter, incline, 24-channel
diagnostics, trip logging and fault history all fit comfortably.

### What would justify moving up

| If you wanted | Then |
|---|---|
| Photographic or video content | A Linux SBC |
| Maps rendered on the cluster | Already answered — head unit (D-128) |
| 3D graphics | Different problem entirely |

None of those are in scope. **The Teensy is the right part.**

---

## The one discipline, restated

**Never clear the whole screen in a redraw path.**

With a RAM framebuffer, the rule becomes: compose freely, but **track which
rectangles changed and send only those.** Composition is free; transmission is not.

A full-screen push costs 64 ms. As a page transition, invisible. Inside a 30 fps
loop, fatal.

---

## Open

| ID | Question |
|---|---|
| Q-056 | Visual style — decided: flat green, digital, no analogue sweep |
| **Q-057** | Incline display — rotating horizon, or two segmented bars? |
| Q-058 | Page switching — CAN keypad button, or long-press on a wink switch? |
| Q-059 | Add PSRAM to the Teensy pads for double-buffering? ~$8, easier if done before the board is installed |

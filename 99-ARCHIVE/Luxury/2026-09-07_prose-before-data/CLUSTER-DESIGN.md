# CLUSTER DESIGN — forward scope

*Rev 2026-08-31 · owns: cluster features not yet finished — the performance page, fault history, persistence. What is built lives in `firmware/icu/cluster_core.h`.*

> **The driving cluster is built**, and so is the page framework: drive,
> diagnostics and trip pages exist in `cluster_core.h`, and `stats.h` feeds
> the trip page (STATUS §Firmware). Layout, palette, widgets and rendering are
> owned by the code; the decisions behind them are D-151 … D-158, D-168.
>
> **This file is what comes next** — the performance page, fault history to
> SD, persistence for `stats.h`, and the page-switch button (D-169). Sections
> describing built work are marked as such.

---

## Contents

The realisation · The static layer · Multi-page architecture · Page 2 performance · Page 3 circuit diagnostics · Page 4 trip and log · Is the Teensy the limitation · The one discipline · Settled and open

---

## The realisation that changes everything

**1280 × 480 at 8 bpp is 614 KB. It lives in the Teensy's 8 MB PSRAM
(D-170, as resized by D-193/F-011).**

**The framebuffer fits in memory the renderer owns.**

That decouples two things I had been treating as one:

| | Cost | Constraint |
|---|---|---|
| **Composing** the image in the framebuffer | CPU cycles at 600 MHz | Effectively free |
| **Transmitting** changed tiles over QSPI into the BT817's RAM_G (D-193) | link rate — `V-084` sets the clock | The only real limit |

So you can render **anything you like** into the buffer — gradients, blends,
sub-pixel positioning, complex curves, dithering — and still only send the
rectangles that changed.

**Complexity of drawing is free. Only motion costs.**

The PSRAM on the 4.1's pads (fitted before install, D-170) leaves room beyond
the framebuffer for double-buffering and off-screen composition.

---

## The static layer is free forever

Drawn once at boot, never touched. **Boot time is the only cost — a full
614 KB canvas push is on the order of 100 ms.** You could redraw the entire
background several times during startup and nobody would notice; instant-on
(D-192) still holds.

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

A full-screen redraw costs on the order of 100 ms. As a page *transition*
that is imperceptible. So a diagnostic page can redraw entirely on entry and
then update lazily.

| Page | Refresh | Constraint | State |
|---|---|---|---|
| **1 · DRIVE** | 30 fps, dirty rects | The disciplined one | **Built** |
| **2 · PERFORMANCE** | 30 fps, small moving elements | G-meter, incline | Not built |
| **3 · DIAGNOSTICS** | 2–5 fps, full redraw acceptable | Stationary use | **Built** — against the PMU simulator |
| **4 · TRIP / LOG** | 1 fps | Stationary use | **Built** — volatile until Stage 6 |

Page switching: a small dedicated momentary button by the display that cycles
pages (D-169). Wired directly to the Teensy — it does not cross the harness.

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

Neither, as built: pitch is a **numeric readout in the left column** under the
compass (D-157, D-161 — ±45°, nose-up positive). Q-057 → D-157 was settled by
building it. A rotating horizon remains the one expensive element to avoid.

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
| RAM | 614 KB framebuffer | 8 MB PSRAM, fitted (D-170) | Fits |
| CAN | 1 bus used | 3 controllers | 2 spare |
| ADC | 6 sensors | 18 inputs | 12 spare |
| Timers | Tach + VSS capture | Many | Fine |
| **QSPI to the BT817** | link rate, `V-084` | — | **The only constraint** |

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

A full-screen push costs on the order of 100 ms. As a page transition,
invisible. Inside a 30 fps loop, fatal.

---

## Settled and open

| ID | State |
|---|---|
| Q-056 → D-151 | Visual style — flat emerald, digital, no analogue sweep |
| Q-057 → D-157 | Incline — a numeric pitch readout in the left column, not a horizon |
| Q-058 → D-169 | Page switching — a dedicated small button by the display |
| Q-059 → D-170 | PSRAM — fit it before the board is installed |
| **Q-060 → D-193** | **Panel selection — the next hardware decision.** [`OPEN.md`](../05-PROCESS/OPEN.md) |
| F-007 | SD persistence for `stats.h` — write on key-off via the PMU shutdown delay (D-162) |

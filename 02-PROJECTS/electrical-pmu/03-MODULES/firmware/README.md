# FIRMWARE

*Rev 2026-08 · owns: cluster layout, palette, rendering, CAN structs*

**This folder is a source of truth.** `icu/cluster_core.h` defines the palette,
every layout constant, the icon set, unit conversions and sensor-fault
rendering. The prose documents describe *why*; this code defines *what*.

---

## Layout

```
firmware/
├── icu/                     THE REAL FIRMWARE
│   ├── cluster_core.h       renderer - portable C++, no Arduino headers
│   ├── stats.h              trip and lifetime accumulators
│   ├── can_map.h            shared CAN structs, both nodes include this
│   └── icu.ino              Teensy host
│
├── icu_sim/                 DESKTOP PREVIEW
│   ├── sim_win32.cpp        Win32 host, zero external libraries
│   ├── sim_main_sdl.cpp     SDL2 host, if you ever want cross-platform
│   └── build.bat
│
├── pmu_sim/                 PMU SIMULATOR — spare Teensy
│   ├── pmu_sim.ino          CAN TX + serial console + scripted drive
│   ├── vehicle_model.h      a 1982 RX-7 that behaves like one
│   └── channels.h           ** THE AMP TABLE. Edit after T-014 **
│
└── (validation sketches, superseded but kept)
    ├── can_map_test/        Stage 2 - struct packing, counter wrap
    ├── can_loopback_test/   Stage 3 - CAN with no transceiver
    ├── ladder_decode_test/  Stage 4 - ladder windows and fault bands
    └── tach_simulator/      Stage 5 - RPM capture, one jumper
```

**`sim_win32.cpp` includes `../icu/cluster_core.h` directly.** One source of
truth — edit a layout constant once and both the simulator and the Teensy
sketch change. There is no second copy to drift.

---

## Building the simulator

You need `g++`. **w64devkit** is the lowest-friction option on Windows — a
single zip, no installer.

```
1. Double-click  C:\Users\Camden Thomas\Downloads\w64devkit\w64devkit.exe
     (opens a shell with g++ already on PATH)

2. cd "/c/Users/Camden Thomas/Documents/Storage/Rx7/02-PROJECTS/electrical-pmu/03-MODULES/firmware/icu_sim"

3. g++ sim_win32.cpp -o sim.exe -std=c++17 -O2 -lgdi32 -luser32

4. ./sim.exe
```

That shell is Unix-style — forward slashes, `/c/` for the C: drive.

**Close the running sim before rebuilding**, or the compiler cannot overwrite
the file it is using.

**If Windows blocks the new exe**, that is SmartScreen reacting to a freshly
built unsigned binary. Launch it from Explorer and choose *More info → Run
anyway*.

### Simulator controls

| Key | |
|---|---|
| `Q` `A` | rpm |
| `W` `S` | speed |
| `E` `D` | water temp |
| `R` `F` | oil pressure |
| `T` `G` | oil temp |
| `Y` `H` | fuel |
| `U` `J` | volts |
| arrows | G meter, springs back to centre |
| `N` `M` | heading |
| `I` `K` | pitch |
| `1`–`5` | warning lamps |
| `Z X C V` | cycle sensor fault state — water, oil press, fuel, rpm |
| `SPACE` | sweep the tach |
| `L` | background grid |
| `+` `-` | window scale, 1× to 3× |
| `ESC` | quit |

The console prints dirty-pixel cost and trip statistics once a second.

---

## Building for the Teensy

Open `icu/icu.ino` in the Arduino IDE. Board: Teensy 4.1, CPU 600 MHz.

**Do not put the simulator sources in the sketch folder** — the Arduino IDE
compiles every `.cpp` it finds there and will try to build the Win32 host for
ARM.

`pushDirtyTiles()` in `icu.ino` is **the only display-dependent function in the
project.** Three `TODO` calls to fill in once a panel is chosen.

---

## What the renderer guarantees

**Compose freely, transmit sparingly.** The 384 KB framebuffer lives in RAM;
only changed 16×16 tiles go over the wire. A full-screen push is 64 ms — fine
as a page transition, fatal inside a 30 fps loop.

**Never call anything that clears the whole screen in a redraw path.** That
single discipline is what makes the design work.

**Every widget diffs its own state.** A digit redraws only the segments that
changed; a bar redraws only the segments that lit or unlit; an unchanged
element costs zero pixels.

---

## Superseded sketches

`can_map_test`, `can_loopback_test`, `ladder_decode_test` and `tach_simulator`
were the Stage 2–5 bring-up steps. **All passed.** The full ICU firmware has
absorbed their function.

They are kept because each is a working, isolated test rig — the tach simulator
in particular is still the fastest way to feed an RPM signal to a board with one
jumper wire.

---

## The bench mule — what three Teensys buy you

With the PMU simulator, the ICU can be developed and demonstrated **completely
without the car**:

```
   [Teensy 1: ICU]  <--- CAN2 ---  [Teensy 2: pmu_sim]
        |  ^                        fuel, volts, key state,
        |  |                        24 channels, faults
        |  +--- pulse in ---------  [Teensy 3: tach_simulator]
        |                           RPM, and VSS on a second channel
        |
        +--- analog in ---------->  potentiometer
                                    stands in for a sender
```

**What that covers:** the CAN receive path, message dispatch, timeout and
blanking, the diagnostics page, `stats.h` accumulation, the RPM capture path,
ladder decode, and the whole rendering layer.

**What it does not cover — and this is the important limit:**

The ICU's critical gauges are on **its own analog inputs, not CAN** (D-083).
RPM, water, oil pressure, oil temp and speed never travel over the bus. So the
PMU simulator exercises only the four things that genuinely come from the PMU:
**fuel level, battery voltage, key state, and channel telemetry.**

That is by design. It also means a CAN failure in testing should leave most of
the cluster working — **which is itself the test.** Pull the PMU sim's power and
watch: fuel and volts should blank, everything else should carry on. If the
whole cluster goes blank, the failure isolation that D-083 promises is not
actually there.

### What it unblocks

| Now possible | Was blocked on |
|---|---|
| ICU firmware against a live bus | having a bus |
| DCU development | something to talk to |
| Two-node CAN with real transceivers | a second sender |
| Judging the cluster on realistic data | plausible values |
| Comparing firmware revisions | repeatable input |
| Exercising trip / retry rendering | a fault source |

### What it is not

**It is not the PMU.** ECUMaster fixes the real message structure, and `V-065`
— reading the actual CAN export out of the client — still has to happen. When it
does, `can_map.h` gets reconciled and this simulator follows it.

**The amp numbers are estimates.** 22 of 24. The model is structurally right and
numerically provisional.

# FIRMWARE

*Rev 2026-08-30 · owns: cluster layout, palette, rendering, CAN structs and the automated trip figures — in code. This README is the folder map and the build instructions.*

**This folder is a source of truth** (R6). `icu/cluster_core.h` defines the
palette, every layout constant, the icon set, unit conversions and
sensor-fault rendering (D-151…D-158). `icu/stats.h` owns the automated trip
and lifetime figures (D-163). `icu/can_map.h` is the machine-readable CAN
map. The prose documents describe *why*; this code defines *what*.

**Version:** `ICU_FW_VERSION` in `icu/icu.ino`, printed at boot. Bump it on
any behaviour change, log it in `../../05-BUILD/LOGS.md`, tag the commit.

## Contents

1. Layout · 2. Building the simulator · 3. Running the tests · 4. Building
for the Teensy · 5. What the renderer guarantees · 6. Superseded sketches ·
7. The bench mule

---

## 1 · Layout

```
firmware/
├── icu/                     THE REAL FIRMWARE
│   ├── cluster_core.h       renderer — portable C++, no Arduino headers. OWNS the cluster layout
│   ├── stats.h              trip and lifetime accumulators. Volatile-only until Stage 6 (D-162)
│   ├── can_map.h            shared CAN structs — THE MASTER COPY; both nodes include it
│   └── icu.ino              Teensy host. ICU_FW_VERSION lives here
│
├── icu_sim/                 DESKTOP PREVIEW — runs the real firmware, not a mock
│   ├── sim_win32.cpp        Win32 host, zero external libraries
│   ├── sim_main_sdl.cpp     SDL2 host, if you ever want cross-platform
│   └── build.bat            builds sim.exe (the .exe itself is not versioned)
│
├── pmu_sim/                 PMU SIMULATOR — the spare Teensy
│   ├── pmu_sim.ino          CAN TX + serial console + scripted drive cycle
│   ├── vehicle_model.h      a 1982 RX-7 that behaves like one
│   └── channels.h           GENERATED from 02-HARNESS/data/pmu_pins.csv — never edit by hand
│
├── tests/                   REGRESSION SUITE — 415 assertions, 13 groups, found 4 real bugs
│   ├── test_suite.cpp       runs on the PC: packing, counter wrap, rendering, overlap, dirty tiles, stats
│   └── run.bat              build + run. Do this after any change to the headers above
│
└── superseded sketches, kept as isolated test rigs (all passed)
    ├── can_map_test/        Stage 2 — struct packing, counter wrap        (carries a copy of can_map.h)
    ├── can_loopback_test/   Stage 3 — CAN with no transceiver             (carries a copy of can_map.h)
    ├── ladder_decode_test/  Stage 4 — ladder windows and fault bands
    ├── tach_simulator/      Stage 5 — RPM capture, one jumper. Still the fastest RPM source
    └── cluster_render_test/ pre-cluster_core.h renderer with a counting mock canvas. Superseded
```

**`can_map.h` has three copies** because the Arduino IDE needs the header
beside each sketch. **`icu/can_map.h` is the master.** When it changes, copy
it over the two test sketches; `07-PROCESS/tools/check.py` fails if they
differ.

**`sim_win32.cpp` includes `../icu/cluster_core.h` directly** — one source of
truth, no second copy to drift. **`channels.h` is generated** from the same
CSV that produces [`PIN-MAP.md`](../../02-HARNESS/PIN-MAP.md) and [`CHANNEL-SCHEDULE.md`](../../01-DESIGN/CHANNEL-SCHEDULE.md); type measured
figures into the CSV and run `gen.py`.

## 2 · Building the simulator

You need `g++`. **w64devkit** is the lowest-friction option on Windows — a
single zip, no installer. Unzip it to `C:\w64devkit` (the path `build.bat`
assumes) and run `w64devkit.exe`, which opens a shell with g++ on PATH.

```
cd "/c/Users/Camden Thomas/Documents/Storage/Rx7/02-PROJECTS/electrical-pmu/03-MODULES/firmware/icu_sim"
./build.bat          # or: g++ sim_win32.cpp -o sim.exe -std=c++17 -O2 -lgdi32 -luser32
./sim.exe
```

That shell is Unix-style — forward slashes, `/c/` for the C: drive. **Close
the running sim before rebuilding**, or the compiler cannot overwrite the file
it is using. **If Windows blocks the new exe**, that is SmartScreen reacting to
a freshly built unsigned binary: *More info → Run anyway*.

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

## 3 · Running the tests

```
cd tests
./run.bat            # builds test.exe and runs it; exit code 0 = all passed
```

Run it after **any** change to `cluster_core.h`, `stats.h`, `can_map.h`,
`vehicle_model.h` or `channels.h`, and before flashing a Teensy. The suite
checks struct packing and CAN round-trip, counter wrap, unit conversions,
every digit glyph, centring, exhaustive widget overlap, off-screen drawing,
dirty-rectangle correctness, sensor-fault rendering, vehicle-model
invariants over a long drive, and stats accumulation.

## 4 · Building for the Teensy

Open `icu/icu.ino` in the Arduino IDE. Board: Teensy 4.1, CPU 600 MHz.
Library: **ACAN_T4**, not FlexCAN_T4 — only ACAN_T4 exposes loopback cleanly.

**Do not put the simulator sources in the sketch folder** — the Arduino IDE
compiles every `.cpp` it finds there and will try to build the Win32 host for
ARM.

`pushDirtyTiles()` in `icu.ino` is **the only display-dependent function in
the project.** Three `TODO` calls to fill in once a panel is chosen (`Q-060`).

## 5 · What the renderer guarantees

**Compose freely, transmit sparingly.** The 384 KB framebuffer lives in RAM;
only changed 16 × 16 tiles go over the wire (D-168). A full-screen push is
64 ms — fine as a page transition, fatal inside a 30 fps loop.

**Never call anything that clears the whole screen in a redraw path.** That
single discipline is what makes the design work.

**Every widget diffs its own state.** A digit redraws only the segments that
changed; a bar redraws only the segments that lit or unlit; an unchanged
element costs zero pixels.

**A missing sensor never renders as a real zero** (D-153). Open, short, stale
and out-of-range each have their own look.

## 6 · Superseded sketches

`can_map_test`, `can_loopback_test`, `ladder_decode_test` and `tach_simulator`
were the Stage 2–5 bring-up steps. **All passed.** The full ICU firmware has
absorbed their function. They are kept because each is a working, isolated
test rig — the tach simulator in particular is still the fastest way to feed
an RPM signal to a board with one jumper wire.

`cluster_render_test` is the first renderer, written against a counting mock
canvas before `cluster_core.h` existed. It is superseded and not maintained;
it stays only as the record of how the pixel budget was first measured.

## 7 · The bench mule — what three Teensys buy you

With the PMU simulator, the ICU can be developed and demonstrated
**completely without the car**:

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
ladder decode, and the whole rendering layer. Needs two SN65HVD230 modules
with their headers soldered, a twisted pair and 120 Ω × 2 —
`../../05-BUILD/BENCH-KIT.md`.

**What it does not cover — and this is the important limit:** the ICU's
critical gauges are on **its own analog inputs, not CAN** (D-083). The PMU
simulator exercises only the four things that genuinely come from the PMU:
fuel level, battery voltage, key state and channel telemetry. Pull the PMU
sim's power and watch: fuel and volts should blank, everything else should
carry on. **If the whole cluster goes blank, the failure isolation D-083
promises is not actually there.**

**It is not the PMU.** ECUMaster fixes the real message structure, and
`V-065` still has to happen. **The amp numbers are estimates** — 19 of 22
outputs at the last count; the simulator prints the number at boot.

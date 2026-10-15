# tests — the host suites and run.sh

*Rev 2026-10-13 (D-497) · owns: how every part's code is tested together on the PC. The fence, the
firmware's layout and rules, and the bench are in `../README.md`; this is only the suites. Paths
here are from this folder.*

## What is here

```
tests/                   REGRESSION SUITES — test_suite · test_bt817 · test_cu · test_radio · test_loglink · test_vectors
├── test_suite.cpp       runs on the PC: packing, counter wrap, rendering, overlap, dirty tiles, stats
├── test_bt817.cpp       the BT817 display driver, mocked SPI
├── test_cu.cpp         the DCU: climate, comfort, panel, windows, mirrors, pin map, expander
├── test_radio.cpp       the battery path: BMS decoder, C3 line protocol, 0x220 / 0x221 (F-015)
├── gen_vectors.py       can_vectors.h from the record's can_messages / can_fields (Y8; not versioned)
├── test_vectors.cpp     static_asserts can_map.h against those vectors - compiling is the test
├── gen_logic_vectors.py logic_vectors.h from the record's logic / ladders / rules / pins (Y8; not versioned):
│                        test_suite §14 holds pmu_sim's vehicle_model.h to every row, §15 the timers the
│                        generator lists as hand-tested; test_cu §18 the 0x400 terms
├── gen_log_vectors.py   log_vectors.h from log_channels / log_link / params (BT3; not versioned):
│                        test_loglink holds the record's widths, UUIDs, opcodes and codes to the headers
├── test_loglink.cpp     the framing, the CRCs, the thinned record, a pull through an in-memory card
└── run.sh               every suite, the sheets against the record (../tools/check.py), every sketch
                         compiled for its target. Do this after any change to the headers above
```

The suites include the parts' real headers, never copies: `../display-unit/firmware/du/`,
`../display-unit/firmware/du_radio/`, `../control-unit/firmware/cu/` and
`../pmu/firmware/pmu_sim/`. The generators read the record in `../../data/`.

**The can_map copies.** `run.sh` refuses to run the suites while a copy of `can_map.h`
(`../control-unit/firmware/cu/`, `../pmu/firmware/pmu_sim/`) differs from the master in
`../display-unit/firmware/du/` (plan P49, 2026-09-26): copy the master over it first.

## Running the tests

```
cd 02-PROJECTS/01-electrical/00-design/tests
./run.sh             # the five suites, the sheets against the record, every sketch for its
                     # target (Teensy 4.1, ESP32-C3); exit code 0 = all passed
```

Run it after **any** change to `cluster_core.h`, `stats.h`, `can_map.h`,
`vehicle_model.h` or `channels.h`, and before flashing a Teensy. The suite
checks struct packing and CAN round-trip, counter wrap, unit conversions,
every digit glyph, centring, exhaustive widget overlap, off-screen drawing,
dirty-rectangle correctness, sensor-fault rendering, vehicle-model
invariants over a long drive, stats accumulation, the PMU simulator against
every logic row the record can turn into vectors (§14), and the timed clauses
it cannot - the fuel-pump prime and oil gate, ignition's 200 ms off-delay, the
voltage shed, the illumination and the sleep timers (§15).

Needs g++, once - Fedora: `sudo dnf install gcc-c++` · Mac: `xcode-select --install`. The binaries
and the generated `*_vectors.h` are not versioned (`.gitignore`).

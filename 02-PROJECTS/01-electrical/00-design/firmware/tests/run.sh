#!/bin/sh
# Build and run ALL firmware test suites:
#   test_suite.cpp   - ICU renderer regression, and section 14: the PMU simulator held to the
#                      record's logic rows (logic_vectors.h, Y8)
#   test_bt817.cpp   - BT817 display driver, mocked SPI (35)
#   test_dcu.cpp     - DCU climate, comfort, panel, windows, mirrors, pin map, expander (F-017, D-452),
#                      and section 18: the logic rows' terms the DCU raises over 0x400 (Y8)
#   test_radio.cpp   - battery path: BMS decoder, C3 line protocol, 0x220/0x221 (F-015)
#   test_vectors.cpp - can_map.h against the record's CAN tables (Y8; compiling is the test)
# then the sheets against the record (cad/check.py) and every sketch against its target.
# Run after ANY change to cluster_core.h, stats.h, can_map.h,
# bt817.h, climate.h, panel.h, pins.h, tca9539.h, vehicle_model.h or channels.h.
#
# Needs g++, once - Fedora: sudo dnf install gcc-c++ · Mac: xcode-select --install
# Exit 0 = every suite passed. The binaries are not versioned (.gitignore).
cd "$(dirname "$0")" || exit 3
# Mac (D-454): a CLT 26.6 toolchain beside a MacOSX27.0 SDK cannot link - pin the SDK that
# matches, until the Command Line Tools are updated and the old SDK is gone. No-op elsewhere.
[ "$(uname)" = Darwin ] && [ -z "$SDKROOT" ] && [ -d /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk ] && export SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk
if ! command -v g++ >/dev/null 2>&1; then
  echo "g++ not found - Fedora: sudo dnf install gcc-c++ · Mac: xcode-select --install"
  exit 3
fi

# The master CAN map and the DCU's copy must be one file (plan P49): a drift here is a node
# that mis-reads every frame, and nothing else checks it.
for copy in ../dcu/can_map.h ../pmu_sim/can_map.h; do
  if ! cmp -s ../icu/can_map.h "$copy"; then
    echo "can_map.h drift: $copy differs from icu/can_map.h (the master) - copy the master over it first"
    exit 1
  fi
done

# The map held to the record (Y8): can_vectors.h is generated from can_messages.csv and
# can_fields.csv, and test_vectors.cpp static_asserts every id, timeout and bit against
# can_map.h - a field the record moved fails the build until the firmware follows.
python3 gen_vectors.py || { echo "*** gen_vectors.py FAILED - the record names a CAN field the firmware does not know ***"; exit 1; }

# The logic rows held to the record (Y8): logic_vectors.h is generated from logic.csv (with the
# ladders, rules and pins it reads) - every input-state combination and the output the record
# expects, inrush and retry as numbers, the prose it cannot read listed for hand-testing. It
# fails when a row names a state its ladder does not have; test_suite (the PMU simulator) and
# test_dcu (the 0x400 terms) then fail on any state or term the firmware does not know.
python3 gen_logic_vectors.py || { echo "*** gen_logic_vectors.py FAILED - a logic row names a state or a cell the record cannot back ***"; exit 1; }

# The three KiCad sheets against the record and the datasheets (cad/check.py, Y3): a Teensy pad,
# expander port, drop cavity or ribbon conductor that disagrees with icu_channels, dcu_channels
# or panel_ribbon fails the suite, as does a symbol pin that disagrees with its datasheet. It
# exits 3 when kicad-cli is absent (or a sheet is unreadable); the suite then goes on without it.
python3 ../../cad/check.py
cad_rc=$?
case $cad_rc in
  0) ;;
  3) echo "cad/check.py skipped - kicad-cli not found, so the schematics were not checked against the record" ;;
  *) echo "*** cad/check.py FAILED - a schematic disagrees with the record or a datasheet (the record is right) ***"; exit 1 ;;
esac

suite() {  # name, source, extra flags
  echo "Building $1 ..."
  g++ "$2" -o "$1" -std=c++17 -O2 $3 || { echo "BUILD FAILED: $2"; exit 1; }
  "./$1" || { echo; echo "*** TESTS FAILED in $1 - do not flash a Teensy until this is green ***"; exit 1; }
}

suite test       test_suite.cpp
suite test_bt817 test_bt817.cpp -I../icu
suite test_dcu   test_dcu.cpp   -I../dcu
suite test_radio test_radio.cpp
suite test_vectors test_vectors.cpp

# Every sketch compiles for its real target (Y8): the Teensy 4.1 sketches with the Teensy
# core, the radio co-processor with the ESP32 core. Skipped with a notice when arduino-cli or
# a core is missing (Fedora / Mac: brew or the arduino-cli release, then
# `arduino-cli core install teensy:avr esp32:esp32` with the PJRC and Espressif index URLs).
if command -v arduino-cli >/dev/null 2>&1; then
  if arduino-cli core list 2>/dev/null | grep -q '^teensy:avr'; then
    for sk in icu dcu pmu_sim tach_simulator ladder_decode_test; do
      echo "Compiling $sk for Teensy 4.1 ..."
      arduino-cli compile --fqbn teensy:avr:teensy41:speed=600 --build-path "/tmp/rx7-build-$sk" "../$sk" >/dev/null 2>"/tmp/rx7-build-$sk.log" \
        || { echo "*** $sk does not compile for the Teensy 4.1 - see /tmp/rx7-build-$sk.log ***"; exit 1; }
    done
  else
    echo "Teensy core not installed - the Teensy sketches were not compiled"
  fi
  if arduino-cli core list 2>/dev/null | grep -q '^esp32:esp32'; then
    echo "Compiling icu_radio for the XIAO ESP32C3 ..."
    arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32C3 --build-path /tmp/rx7-build-icu_radio ../icu_radio >/dev/null 2>/tmp/rx7-build-icu_radio.log \
      || { echo "*** icu_radio does not compile for the ESP32-C3 - see /tmp/rx7-build-icu_radio.log ***"; exit 1; }
  else
    echo "ESP32 core not installed - icu_radio was not compiled"
  fi
else
  echo "arduino-cli not found - no sketch was compiled for its target"
fi

echo
echo "All suites passed."

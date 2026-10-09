#!/bin/sh
# Build and run ALL firmware test suites:
#   test_suite.cpp  - ICU renderer regression (421 assertions)
#   test_bt817.cpp  - BT817 display driver, mocked SPI (35)
#   test_dcu.cpp    - DCU climate, comfort, panel, windows, mirrors (F-017)
#   test_radio.cpp  - battery path: BMS decoder, C3 line protocol, 0x220/0x221 (F-015)
# Run after ANY change to cluster_core.h, stats.h, can_map.h,
# bt817.h, climate.h, panel.h, vehicle_model.h or channels.h.
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
if ! cmp -s ../icu/can_map.h ../dcu/can_map.h; then
  echo "can_map.h drift: dcu/can_map.h differs from icu/can_map.h (the master) - copy the master over it first"
  exit 1
fi

# The three KiCad sheets against the record and the datasheets (cad/check.py, Y3): a Teensy pad,
# expander port, drop cavity or ribbon conductor that disagrees with icu_channels, dcu_channels
# or panel_ribbon fails the suite, as does a symbol pin that disagrees with its datasheet. It
# exits 3 when kicad-cli is absent (or a sheet is unreadable); the suite then goes on without it.
if python3 ../../cad/check.py; then
  :
elif [ "$?" -eq 3 ]; then
  echo "cad/check.py skipped - kicad-cli not found, so the schematics were not checked against the record"
else
  echo "*** cad/check.py FAILED - a schematic disagrees with the record or a datasheet (the record is right) ***"
  exit 1
fi

suite() {  # name, source, extra flags
  echo "Building $1 ..."
  g++ "$2" -o "$1" -std=c++17 -O2 $3 || { echo "BUILD FAILED: $2"; exit 1; }
  "./$1" || { echo; echo "*** TESTS FAILED in $1 - do not flash a Teensy until this is green ***"; exit 1; }
}

suite test       test_suite.cpp
suite test_bt817 test_bt817.cpp -I../icu
suite test_dcu   test_dcu.cpp   -I../dcu
suite test_radio test_radio.cpp

echo
echo "All suites passed."

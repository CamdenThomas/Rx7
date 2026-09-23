#!/bin/sh
# Build and run ALL firmware test suites:
#   test_suite.cpp  - ICU renderer regression (421 assertions)
#   test_bt817.cpp  - BT817 display driver, mocked SPI (35)
#   test_dcu.cpp    - DCU climate/comfort logic (38)
#   test_radio.cpp  - battery path: BMS decoder, C3 line protocol, 0x220/0x221 (F-015)
# Run after ANY change to cluster_core.h, stats.h, can_map.h,
# bt817.h, climate.h, vehicle_model.h or channels.h.
#
# Needs g++, once:  sudo dnf install gcc-c++
# Exit 0 = every suite passed. The binaries are not versioned (.gitignore).
cd "$(dirname "$0")" || exit 3
if ! command -v g++ >/dev/null 2>&1; then
  echo "g++ not found - install it once:  sudo dnf install gcc-c++"
  exit 3
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

#!/bin/sh
# Build the ICU simulator (sim_sdl.cpp) into ./sim.
# Needs, once:  sudo dnf install gcc-c++ SDL2-devel
# The binary itself is not versioned (.gitignore).
cd "$(dirname "$0")" || exit 3
if ! command -v g++ >/dev/null 2>&1; then
  echo "g++ not found - install it once:  sudo dnf install gcc-c++ SDL2-devel"
  exit 3
fi
if ! command -v sdl2-config >/dev/null 2>&1; then
  echo "SDL2 headers not found - install them once:  sudo dnf install SDL2-devel"
  exit 3
fi
echo "Building sim ..."
g++ sim_sdl.cpp -o sim -std=c++17 -O2 $(sdl2-config --cflags --libs) || { echo "BUILD FAILED"; exit 1; }
echo "Built sim   -   run it with:   ./sim"

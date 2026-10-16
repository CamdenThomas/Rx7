#!/bin/sh
# Build the ICU simulator (sim_sdl.cpp) into ./sim.
# Needs, once - Fedora: sudo dnf install gcc-c++ SDL2-devel · Mac: xcode-select --install && brew install sdl2
# The binary itself is not versioned (.gitignore).
cd "$(dirname "$0")" || exit 3
# Mac (D-454): a CLT 26.6 toolchain beside a MacOSX27.0 SDK cannot link - pin the SDK that
# matches, until the Command Line Tools are updated and the old SDK is gone. No-op elsewhere.
[ "$(uname)" = Darwin ] && [ -z "$SDKROOT" ] && [ -d /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk ] && export SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk
if ! command -v g++ >/dev/null 2>&1; then
  echo "g++ not found - Fedora: sudo dnf install gcc-c++ · Mac: xcode-select --install"
  exit 3
fi
if ! command -v sdl2-config >/dev/null 2>&1; then
  echo "SDL2 headers not found - Fedora: sudo dnf install SDL2-devel · Mac: brew install sdl2"
  exit 3
fi
echo "Building sim ..."
# -I<prefix>/include: the source says <SDL2/SDL.h>, and Homebrew's sdl2-config only gives the SDL2/ dir itself.
g++ sim_sdl.cpp -o sim -std=c++17 -O2 -I"$(sdl2-config --prefix)/include" $(sdl2-config --cflags --libs) || { echo "BUILD FAILED"; exit 1; }
echo "Built sim   -   run it with:   ./sim"

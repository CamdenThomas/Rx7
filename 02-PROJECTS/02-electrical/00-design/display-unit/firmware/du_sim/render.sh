#!/bin/sh
# Render every cluster page headless to PNG (work X-007): the real renderer,
# the simulator's demo state, no window. Needs g++ (Fedora: sudo dnf install gcc-c++ · Mac: xcode-select --install)
# and Python with Pillow for the PNGs. Output in ./renders/ (not versioned).
cd "$(dirname "$0")" || exit 3
# Mac (D-454): a CLT 26.6 toolchain beside a MacOSX27.0 SDK cannot link - pin the SDK that
# matches, until the Command Line Tools are updated and the old SDK is gone. No-op elsewhere.
[ "$(uname)" = Darwin ] && [ -z "$SDKROOT" ] && [ -d /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk ] && export SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk
command -v g++ >/dev/null 2>&1 || { echo "g++ not found - Fedora: sudo dnf install gcc-c++ · Mac: xcode-select --install"; exit 3; }
mkdir -p renders && cd renders || exit 3
g++ ../render_pages.cpp -o render_pages -std=c++17 -O2 || { echo "BUILD FAILED"; exit 1; }
./render_pages || exit 1
python3 -c "
import glob
from PIL import Image
for p in sorted(glob.glob('*.ppm')):
    Image.open(p).save(p[:-4] + '.png'); print('png', p[:-4] + '.png')
" && rm -f ./*.ppm render_pages

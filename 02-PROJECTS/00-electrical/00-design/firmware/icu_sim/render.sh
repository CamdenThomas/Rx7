#!/bin/sh
# Render every cluster page headless to PNG (work X-007): the real renderer,
# the simulator's demo state, no window. Needs g++ (sudo dnf install gcc-c++)
# and Python with Pillow for the PNGs. Output in ./renders/ (not versioned).
cd "$(dirname "$0")" || exit 3
command -v g++ >/dev/null 2>&1 || { echo "g++ not found - sudo dnf install gcc-c++"; exit 3; }
mkdir -p renders && cd renders || exit 3
g++ ../render_pages.cpp -o render_pages -std=c++17 -O2 || { echo "BUILD FAILED"; exit 1; }
./render_pages || exit 1
python3 -c "
import glob
from PIL import Image
for p in sorted(glob.glob('*.ppm')):
    Image.open(p).save(p[:-4] + '.png'); print('png', p[:-4] + '.png')
" && rm -f ./*.ppm render_pages

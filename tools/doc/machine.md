# One tree, any clone — the machines, and what is left of the old one (was CLAUDE.md §9)

**One tree, two desks and a phone, synced only through GitHub (D-454, 2026-10-08).** The
tree is a clone of `github.com/CamdenThomas/Rx7` (public) on each machine; nothing moves
between them any other way, which is why every run starts with `git pull --rebase` (§0) and
ends with a push. The remote is the backup and the phone app's way in (D-403). Any
instruction, script or path that assumes Windows (`C:\…`, `.bat`, `.ps1`, `.exe`,
w64devkit) is stale; so is "the one Fedora machine" — that was true from 2026-09-22 to
2026-10-08.

| | **The Mac** — most work, since 2026-10-08 | **The Fedora PC** — `/home/crash/docs/storage/Rx7` |
|---|---|---|
| Tree | `/Users/crash/dev/Rx7` (arm64, macOS 26) | `~/docs/storage/Rx7` |
| `rx7.py` | Apple's `python3` **3.9** — keep the tool 3.9-clean (CI runs 3.14) | `python3` 3.14 |
| Hook | `git config core.hooksPath .githooks` — set 2026-10-08 | set |
| KiCad | 10.0.6 (`/Applications/KiCad`, `kicad-cli` via Homebrew); global library tables copied from the app's template 2026-10-08 | 10.0.6 system-wide |
| ngspice | 47 (`brew install ngspice`) | `sudo dnf install ngspice` (D-453's setup line) |
| Firmware tests, `icu_sim` | Xcode CLT `g++`, `brew install sdl2`; the build scripts pin `SDKROOT` while CLT 26.6 sits beside a 27.0 SDK it cannot link against | `sudo dnf install gcc-c++ SDL2-devel` |
| Teensy upload | Teensyduino or `arduino-cli` with the Teensy core; no udev | the same, plus PJRC's udev rule (firmware README §4) |
| Diagrams | Pillow (`python3 -m pip install --user pillow`); the font is in the tree, `tools/fonts/` | Pillow (`python3-pillow`); same font |
| The Rx7 app | **not built yet** (work `F3`): needs `brew install rustup` + `rustup-init`, `npm install`; Node 24 via fnm is there. `tauri-driver` (the desktop e2e) is Linux/Windows only — the browser tests run | installed (RPM); Node 22, Rust in `~/.cargo`, the Tauri libraries, JDK 21 in `~/.local/jdk`, the Android SDK/NDK in `~/Android/Sdk` (app README) |
| Only here | — | the 3.4 GB model library (`01-REFERENCE/model`), the research downloads, the Android signing key — `P55` names their second home |
| Claude Code | `~/.local/bin/claude` | `~/.local/bin/claude` |

The car's diagnostic port `DP-DIAG` takes Camden's Windows laptop, which runs ECUMaster's PMU
client and nothing else for this project (D-376). It holds no clone.

**The v2 working tree is gone.** On 2026-09-12 the v3 record replaced it, after a
file-by-file check that nothing needed had been left behind: every open question carried
into a block, a work row or a decision; the firmware byte-identical; the v2 tools, the
eleven skills and `WORKFLOWS.md` preserved under `99-ARCHIVE/2026-09-11_v2-view-and-tools/`.
The only rows that vanished were `L2-NZL` and its two cavities, which is D-329 doing its
job. If you need to know how something used to read, the archive is where it lives now.
v2's rendered pages, its Stop hook that grepped its own output, and its picky answer regex
that once lost a whole answering session are why R3 and R9 read the way they do.

**The visual layer is the Rx7 app, `02-APP`** (D-399 → D-405; not a project since D-428). It is
a view and an input over the record that keeps no fact of its own. Nothing else grows a view.
The generated files are only the harness-leg drawings in
`02-PROJECTS/01-electrical/00-design/diagrams/` (D-385). The one hand-drawn exception is
`02-PROJECTS/01-electrical/00-design/cad/`: the KiCad projects for the ICU and DCU carriers and
the control panel — schematic, board layout and 3D model, with `PCB-AND-3D-GUIDE.md` as the
method — ruled in by Camden on 2026-09-12, widened on 2026-09-21 (layout, both boards, D-361),
and since D-453 drawn by the agent as well. It is not an area — no `data/`, so `rx7.py` cannot
see it — nothing in the record cites it, and if the record and a drawing ever disagree the
record is right. Its own README is the fence.

The Claude Project holds one pointer document and nothing else; nothing is ever queued
there. The account skill `rx7-system-v2` is stale and Camden deletes it (02-APP work P27).

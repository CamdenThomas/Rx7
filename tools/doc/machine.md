# One tree, one machine, and what is left of the old one (was CLAUDE.md §9)

**One machine: `/home/crash/docs/storage/Rx7` on Fedora.** Since 2026-09-22 this is the only
computer the project lives on — there is no laptop and no `crashs-pc` any more, and nothing
is synced between machines except through GitHub. It is a git clone of
`github.com/CamdenThomas/Rx7` (public); the remote is the backup and the phone app's way in
(D-403), not a second place to work. Any instruction, script or path that assumes Windows
(`C:\…`, `.bat`, `.ps1`, `.exe`, w64devkit) is stale.

The tools on this machine, and nothing else:

- `python3` (3.14) runs `tools/rx7.py`; the pre-commit hook is enabled
  (`git config core.hooksPath .githooks`, set once per clone) and checks the index.
- KiCad 10.0.6 system-wide: `kicad`, `kicad-cli` in `/usr/bin`.
- Firmware (`02-PROJECTS/01-electrical/00-design/firmware/`): `tests/run.sh` and
  `icu_sim/build.sh` need `sudo dnf install gcc-c++ SDL2-devel` once; flashing a Teensy needs
  PJRC's udev rule (its `README.md` §4). The car's diagnostic port `DP-DIAG` takes Camden's
  Windows laptop, which runs ECUMaster's PMU client and nothing else for this project (D-376).
  It holds no clone, and it is not a second home for the tree.
- The Rx7 app (`02-APP/app/`): Node 22 and npm (dnf), Rust through rustup in `~/.cargo`, the
  Tauri build libraries (dnf, listed in the app's README), JDK 21 in `~/.local/jdk`, and the
  Android SDK and NDK in `~/Android/Sdk`. The app's README says how to build, test and install
  both apps. Claude Code lives in `~/.local/bin/claude`.

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
`02-PROJECTS/01-electrical/00-design/cad/`: the KiCad projects for the ICU and DCU carriers —
schematic, board layout and 3D model, with `PCB-AND-3D-GUIDE.md` as the method — ruled in by
Camden on 2026-09-12 (the schematic) and widened on 2026-09-21 (layout, both boards, D-361). It
is not an area — no `data/`, so `rx7.py` cannot see it — nothing in the record cites it, and if
the record and a drawing ever disagree the record is right. Its own README is the fence.

The Claude Project holds one pointer document and nothing else; nothing is ever queued
there. The account skill `rx7-system-v2` is stale and Camden deletes it (02-APP work P27).

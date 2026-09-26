# Superseded firmware sketches (moved 2026-09-26, plan P54)

Three Arduino test rigs the firmware README listed as superseded: `can_map_test/` (Stage 2,
struct packing and counter wrap), `can_loopback_test/` (Stage 3, CAN with no transceiver) and
`cluster_render_test/` (the renderer before `cluster_core.h`). All passed when they were last
run. Each carried its own copy of `can_map.h`; with them here, the master `icu/can_map.h` has
one copy left to drift from (`dcu/`), and `tests/run.sh` now refuses when the two differ.
`ladder_decode_test/` and `tach_simulator/` stayed in the firmware folder: they are still the
bench's fastest ladder and RPM sources.

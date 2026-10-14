# 99-ARCHIVE

_Rev 2026-10-14 (plan P54; D-569, D-570). Nothing here is current. It is kept because the reasoning is
useful, and because ids derive from it: `rx7.py` reads every `decisions.csv`, `retired.csv`
and rendered `DECISIONS.md` under this folder so no decision or block number is ever handed
out twice._

| Folder | What it was | What replaced it |
| --- | --- | --- |
| `2026-09-03_data-migration/` | The first move from prose documents to `data/*.csv` | the v3 record, `tools/rx7.py` |
| `2026-09-08_system-v2/` | The system-v2 transition: the proposal as ruled, the one-time migration script, the old `CLAUDE.md`/`ASSISTANT.md` | `CLAUDE.md` v4 (2026-09-26) and `tools/doc/` |
| `2026-09-08_apply-script/` | `apply-rx7-changes.py`, the chat-authored script that carried two sweeps in while the device bridge was down; it reused spent ids | the 2026-09-08f repair; `rx7.py new` and `rx7.py block` derive every id |
| `2026-09-11_v2-view-and-tools/` | v2 whole: the rendered pages (`DECISIONS.md`, `QUESTIONS.md`, `BLOCKS.md` …), the eleven skills, `WORKFLOWS.md`, the v2 tools and templates, the WireViz sheets | the record + the Rx7 app (D-405); the harness drawings (D-385); the playbooks |
| `answers/` | Camden's typed answer files from the `ANSWERS.md` era | the app's `inbox` (D-405) |
| `Electrical/` | v1 and v2 electrical documents: the Rev A pin plan and checklist, the C1-C7 connector scheme, the audit lists, `HEAD-UNIT.md`, `PARTS-CHANGES.md`, `DEFERRED-FEATURES.md`, the lighting-body project, the hand-drawn SVGs | `02-PROJECTS/01-electrical/data/` (35 tables) and its decisions |
| `Luxury/` | The luxury package's prose designs before data, and the ICU-carrier template before the ICU moved to the electrical build | `02-PROJECTS/03-luxury/data/`; the ICU is `01-electrical`'s (D-374) |
| `2026-09-26_firmware-superseded-sketches/` | `can_map_test`, `can_loopback_test`, `cluster_render_test` - Arduino test rigs the firmware README called superseded, each with its own `can_map.h` copy | `firmware/icu/can_map.h` (master) + `dcu/`, checked equal by `tests/run.sh` |
| `2026-09-26_diagram-options/` | The four drawing approaches sampled before D-385 (A ladder, B route map, C ELK, D D2) and the code that drew them | `tools/diagrams.py` (A and B) |
| `2026-10-13_00-verify/` | The verify project's record, complete: every held-back Manual fact checked or marked not this car | its trim-code row carried to `04-beauty` (D-498) |
| `2026-10-13_01-REFERENCE/` | The reference's record once its tables had moved: the shell, an empty `blocks`, the `REF` retired row | `00-CAR` and `05-cad` hold its tables; the folder is `01-INTAKE` (D-519) |
| `2026-10-14_06-intake/` | The intake project's record, complete: every manual, catalogue, diagram and found model in the reference parsed into `00-CAR`'s tables and taken out of git (87 rows; the last three read from page images) | `00-CAR` (specs, procedures and their steps, intervals, terminals, circuits and circuit_paths, sources, catalogue, cad); the files in the ignored library (D-569) |
| `2026-10-14_04-beauty/` | The beauty project's shell once it merged into luxury: its project file, schema, empty blocks table and log | `03-luxury` holds its work rows (stage P), decisions and retired terms (D-570) |

Never load anything here into a Claude Project or a prompt as current knowledge. If the record
and an archived page disagree, the record is right; the page says how it used to read.

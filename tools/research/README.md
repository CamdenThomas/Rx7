# tools/research — the part-by-part research (D-429)

How the whole-car parts list was built and how each part is researched. The work rows that
say what is next live in `02-PROJECTS/00-verify` (stage R); this file is only the method.

| File | What it does |
| --- | --- |
| `merge_catalogue.py` | Stage 1: merges the catalogue readers' CSV chunks into `01-REFERENCE/data/catalogue.csv` |
| `merge_parts.py` | Stage 1b: merges the section agents' JSON into `00-CAR/data/parts.csv` (PT ids, parents) |
| `research-workflow.js` | Stage 2: the Workflow script. One research agent per batch writes `research/<batch>.json`, then a source checker re-opens a sample of the cited sources and drops anything unsupported |
| `merge_research.py` | Stage 2: merges `research/<batch>.json` into specs, terminals, sources, cad and parts |
| `batches.json` | The 58 research batches (about 947 parts), grouped by system and by the unit each part sits in |

The agents' raw output is kept IN the tree, in `01-REFERENCE/research/` (`catalogue/`, `parts1b/`,
`research/`, one JSON per batch, about 1.7 MB): it is agent output with no licence question, and
five wave-2 batches were lost while it lived only in a scratch folder (plan P48, 2026-09-26). The
merge is idempotent and refuses to write while it reports a problem (`--force` overrides).

## Waves

| Wave | Systems | Batches | State |
| --- | --- | --- | --- |
| 1 | electrical, lighting, ignition | 22 | merged 2026-09-25 |
| 2 | engine, fuel, cooling, climate, transmission | 18 | see 00-verify R1 |
| 3 | brakes, driveline, steering, suspension, wheels, body | 18 | see 00-verify R2, waits on Camden's R0 |

## Running a wave

1. Take the wave's batches from `batches.json`, e.g. every batch whose `system` is in the wave.
2. Run the Workflow tool with `scriptPath: tools/research/research-workflow.js` and
   `args: {"scratch": "<a scratch dir>", "batches": [ ...those batches... ]}`. Create
   `<scratch>/research/` first. Each agent writes `<scratch>/research/<batch>.json`.
3. Dry run, then write:
   `python3 tools/research/merge_research.py <scratch> <system prefixes...> [keep=PT0xx,...]`
   and again with `--write`. `keep=` lists the parts whose note may keep the word confirm.
   For every other part, a doubt about one detail is rewritten as "check", so it does not
   hide the part from the Manual.
4. Read what the merge added before committing:
   - Notes that newly carry confirm: they hide the part.
   - Anything citing a decision: `check` refuses that in 00-CAR (§6.6).
   - Optional equipment or gone hardware (issues K-009 to K-013): those parts stay held or replaced.
5. `python tools/rx7.py check`, copy the new `research/*.json` into the library folder, and
   commit.

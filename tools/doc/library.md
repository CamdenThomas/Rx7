# The library plan - every document read into the record, then no PDFs (D-574)

_Rev 2026-10-14. Project `02-PROJECTS/05-library`. This is the whole plan: what exists, who
does what, in what order, how an agent takes its next piece and marks it done, and when a phase
is finished. Workers read only their playbook (`rx7.py playbook parse` / `merge`); the
orchestrator reads this._

## The goal

Every fact in every document the record draws on - manuals, catalogues, bulletins, datasheets,
vendor sheets - lives as a row in a table, once, citing its source and page, cross-checked
against the car. Then the PDFs leave the tree. What stays: `00-CAR/data` (facts),
`00-CAR/photos`, 02-cad's models, and an offline copy of the PDFs outside the tree. The app's
Manual gets a References page linking every source and showing which rows each page became.

## Camden's rulings (D-574, all as recommended)

| | Ruling |
|---|---|
| A | An **offline copy** of every PDF outside the tree (an external drive or cloud folder) before any is deleted. |
| B | A figure becomes **rows plus a link to its page**; a small cropped image (kept like a photo) only where the picture is the information. |
| C | **Scope**: everything about this car, and other 1979-85 RX-7 years as held-back rows (`applies=other-car`); other models' pages are only **indexed** (kind and topic), taking a fact only where a part this car or a project uses is named. |
| D | **The same rule everywhere**: project and model-library PDFs are read into their owning project's tables and leave too. CAD files (STEP, GLB, STL) stay - they are models. |
| E | The 3D model library **stays in 02-cad** (D-573). |
| F | **Git history is left alone**; the repository goes private as D-524 already ruled - a GitHub setting only Camden can change. |

## What exists (phases 0 and 1, done 2026-10-14)

**Tables.**

| Table | Area | One row per | Key columns |
|---|---|---|---|
| `docs` | 00-CAR | PDF file (163) | source (S-), path, pages, md5, text (yes / ocr / no), owner area, tier 1-5, scope, file (on-disk / offline / gone), duplicate_of |
| `pages` | 00-CAR | page (4,116) | doc, n, printed, kind, topic, scope, status, rows (the home rows holding its facts) |
| `diagnosis` | 00-CAR | symptom-cause pair | system, symptom, cause, check, remedy, part, source, page, applies |
| `queue` | 05-library | small work item (1,229 now) | priority, kind, doc, pages, brief, after, state, agent, claimed, finished, result, rows |
| `facts` | 05-library | fact a worker read (staging) | page, kind, system, subject, item, value, unit, context, applies, quote, state, target |

**Page status** (`pages.status`): `open` unread - `cited` some rows cite it, not proven complete -
`parsed` every fact taken - `held` taken as another year's - `indexed` another model, described
only - `duplicate` - `empty`. Finished = parsed, held, indexed, duplicate or empty.

**Tools** (all in `02-PROJECTS/05-library/tools/`, each re-runnable, each taking rx7.py's write lock):

| Tool | Does |
|---|---|
| `inventory.py` | finds every PDF; a `docs` row each (a `sources` row too when none named it - 95 were added); a `pages` row per page with its printed number, kind and topic from the text layer or OCR; marks pages existing rows already cite as `cited`, listing those rows. Never lowers a status. |
| `build_queue.py` | turns unfinished pages into queue items (default), staged facts into merge items (`--merge`), failed items into review items (`--review`), and prices every item - model, predicted tokens and dollars, cap (`--reprice`). Never queues a page twice; never edits an item an agent touched. |
| `page.py` | a page or a few as text (`text DOC-062 12-14`) or as a PNG (`image DOC-048 27 [--dpi N] [--crop x,y,w,h]`). |
| `link.py` | adds home rows to a page's `rows` (merge). |
| `run_session.py` | the manager: a timed session of workers, each with its item's model and cap; writes their answers, finishes the items with tokens and dollars, commits (`--dry` forecasts). |

**rx7.py** (D-574): every writing command holds one tree-wide lock for its read-change-write,
so any number of agents can write at once; `add id=next` issues keys (an empty table starts from
its key column's note); `claim AREA [--kind K] [--agent N] [--stale MIN]` hands out the highest
priority open item whose `after` items are done, marks it claimed, and reclaims one abandoned
longer than `--stale` (90) minutes; `finish AREA Q-id [state=…] result= rows=` closes it; `dups`
lists specs holding one fact twice (36 today - phase 3 clears them). `check` now refuses: a page
naming a row that does not exist, a page id that is not `<doc>.<nnn>`, a doc marked `gone` with an
unfinished page or with its file still on disk, a claimed item with no agent or time, a done item
with no finish time.

**The inventory, 2026-10-14:** 163 docs, 4,116 pages; 687 pages already cited by the record,
393 pages in 13 duplicate files (one copy kept), 3,036 open. Queue: 1,229 items - 1,055 parse,
113 parts-catalogue, 28 troubleshooting, 21 drawing, 12 index-only.

## The priority (why the most valuable pages go first, across all PDFs)

`build_queue.py` scores every item; `claim` always hands out the highest:

    tier      1: 500  2: 350  3: 200  4: 100  5: 20     the document's worth to this car (docs.tier)
    status    open +60 (unread beats re-reading a cited page)
    scope     this-car +40, mixed / unknown +20, other-year 0, other-model -60
    kind      troubleshooting +80, a page with tables +40, drawings +20
    order     minus page / 25 (a document's front before its back)

Tiers (set by `inventory.py`'s RULES, owner in brackets): **1** - the 1982 wiring diagram and
technical data, the 1981-83 parts catalogue, the 1983 Mitchell manual, the 1985 workshop manual
sections, the 1985 Section 12, the 1980 body section [00-CAR]. **2** - the 1980 sections and
technical data, the bulletins, the body shop, training and emissions manuals, the A/C install, the
fitted parts' datasheets [00-CAR]; the PMU, display and simulation vendor sheets [01-electrical].
**3** - the replaced carburettor's manuals, the overhaul criteria, Yamamoto, the setup book,
brochures, the TE catalogue, the 1983 diagram (already read) [00-CAR / 01-electrical]; the model
library's electrical drawings [01-electrical]. **4** - the swap documents [03-engine], other
model-library sheets [02-cad]. **5** - model-kit print guides, index only [02-cad].

So the head of the queue is every troubleshooting table, then the 1981-83 data and the catalogue,
then the 1985 and 1983 manuals' unread tables, and so on - each document's best pages early, not
one document after another.

## Roles

- **The manager is a script**, `run_session.py` - it spends no tokens. It claims items, prepares
  each worker's prompt, launches the worker with the item's model and cap, writes what comes back,
  finishes the item with what it cost, and at the end checks, commits and pushes.
- **A worker is one `claude -p` call per item**, started in an empty folder under /tmp/rx7-work (so it
  loads no CLAUDE.md, no memory, and can touch nothing in the tree). Its prompt is the parse
  playbook's worker text, the item's brief, every page's text, and the names of the page images in
  its folder; its only tool is Read, for those images. It answers with two blocks - facts and pages -
  and nothing else; the manager does every write.
- **Models** (`build_queue.py`, `model_for`): **Haiku 5.5** for text and scanned prose - 1,093 items;
  **Sonnet 5.5** for drawings, the parts catalogue's figure pages, wiring diagrams, reviews of failed
  items and merges - 136 items now. No Opus: nothing in parsing needs it.
- **The orchestrating session** (Opus, in chat) only starts sessions, reads the ledger, spot-checks,
  tunes the cost model and raises blocks - it does not run the workers.

## Every item is mapped and priced before it runs

`build_queue.py` gives each item `model`, `est_in` / `est_out` (tokens), `est_usd` and `cap_usd`;
`--reprice` recomputes every open item after the cost model changes. The model, measured
2026-10-14 with one bare Haiku call:

| Constant | Value | What |
|---|---|---|
| fixed context | 22,000 read + 12,000 written per call | the worker's system prompt and tools; $0.0027 on Haiku before any page |
| instructions + brief | 1,800 tokens | the playbook's worker text |
| page text | characters / 4 | from the text layer or the OCR text |
| a page image | 1,600 tokens, one more turn | drawings, unknown pages, scans with no text, OCR tables |
| output | 45 tokens a fact, +80 % thinking, +250 a turn | facts estimated at text / 55 + 12 an image + 2 a page |
| prices | Haiku $0.10 / $0.50, Sonnet $2 / $10, Opus $4 / $20 per million in / out | reads 0.1x, writes 1.25x |
| **cap** | **3 x the prediction, floor $0.03 Haiku, $0.40 Sonnet** | `claude -p --max-budget-usd`: a worker reaches it only by going wrong (a loop) |

The forecast today (all 1,229 parse items): Haiku 73.1 M input tokens (nearly all cached reads),
3.3 M output, **$4.44 predicted**; Sonnet 17.5 M in, 0.7 M out, **$16.16**; together **$20.60**, with
every cap summing to $91.47 (the worst case if every single worker looped). The overhaul is priced when parsing is done (it depends on how many facts there are).

## A session

```
python3 02-PROJECTS/05-library/tools/run_session.py --dry                     # the next hour's items, predicted $ and worst case
python3 02-PROJECTS/05-library/tools/run_session.py --minutes 60 --workers 6  # run it
```

- For `--minutes` it keeps `--workers` workers running, most valuable item first. After that it starts
  nothing new; the running workers finish (each bounded by its own cap and a 20-minute timeout);
  then `check`, a commit, a push, a log row and the ledger (items, facts, dollars).
- `--max-usd N` also stops new starts once the actual spend plus the running workers' caps would pass N.
- `--kind K` / `--model haiku|sonnet` restrict a session (e.g. a cheap Haiku-only hour).
- A worker that hits its cap, crashes, or answers without the two blocks fails its item; `build_queue.py
  --review` makes a Sonnet review item of each failed one.
- Stop any time with Ctrl-C: claimed items open again after 90 minutes; nothing is half-written,
  because the manager writes an item only after its worker answered.
- Resume: run it again - the queue is the only state.

The dry forecast for 60 minutes with 6 workers: about 258 items, $12.30 predicted, $48.09 if every
cap were hit. The seconds per item (60 Haiku, 120 Sonnet) are guesses until the first session; its
ledger replaces them.

## After each session (the orchestrator, a few minutes)

1. Read the ledger and `rx7.py sql 02-PROJECTS/05-library "select model, count(*), sum(est_usd), sum(cost_usd), sum(tok_in), sum(tok_out) from queue where state in ('done','failed') group by model"`.
2. If actual cost runs above the prediction, raise the constants in `build_queue.py` and `--reprice`.
3. Spot-check three finished items: their pages against their facts. A pattern of misses or inventions
   is fixed in the parse playbook's worker text - the only lever on the workers.
4. `build_queue.py --review` for the failed items.

## The store until the overhaul (D-576)

Parsing only stores; nothing is merged while it runs. Everything a page says lives in 05-library's
`facts` table - one row per fact, citing its page, in plain text the app and any agent can read -
and the page's `kind`, `topic`, `scope` and `status` in 00-CAR's `pages`. That is the whole
non-PDF copy of the library. The overhaul (phase 3) reads only these tables, never a PDF, so it
can be planned, priced and run as one job with the full picture: duplicates across documents and
years are visible together, which a merge done item by item could not see. The PDFs stay on disk
until the overhaul and the app's References page are done (L6 waits on L3).

## Phases and when each is done

| Phase | Work rows | Done when |
|---|---|---|
| 0 Structure | L0 | tables, checks, tools, playbooks, this plan - **done 2026-10-14** |
| 1 Inventory | L1 | every PDF a docs row, every page a pages row, cited pages marked, the queue built - **done 2026-10-14** |
| 2 Parse | L2 | no parse / index / catalogue / diagnosis / figure / review item open, claimed or failed; every page parsed, held, indexed, duplicate or empty |
| 3 The overhaul | L3 | one separate task after every page is parsed (D-576), planned and priced then: every staged fact cross-referenced against the car and the other facts, combined, conflicts raised as blocks, merged into 00-CAR and the projects in one pass, each page linked to its home rows, `rx7.py dups` clean and made a refusal |
| 4 The app | L4 | the Manual's References page (every source: link, pages, coverage, the rows each page became), sources on part and system pages, a Diagnosis view; desktop rebuilt |
| 5 Remove | L5, L6 | the offline copy made and named in `docs.offline` (Camden: where); every finished doc's file deleted and marked `gone`; the OCR text and raw research folded or deleted; the 5 tracked vendor PDFs out of git; `check` clean with no PDF in the tree |

## Rules every phase keeps

- A fact cites its page: facts.page during staging; the home row's `source` and `page` after.
- `applies` - this car's figure is blank; another 1979-85 year's is `other-car` and held back from
  the Manual; another model's is not taken unless a part we use needs it.
- 00-CAR never cites a decision (CLAUDE.md §1); notes say what the car is.
- A measured or Camden-checked value is never overwritten by a page (R11): that is a conflict.
- Nothing is deleted from disk before phase 5, and nothing in phase 5 before the offline copy.

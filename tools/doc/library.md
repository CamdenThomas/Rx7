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
| `build_queue.py` | turns unfinished pages into queue items (default), staged facts into merge items (`--merge`), failed items into review items (`--review`). Never queues a page twice; never edits an item an agent touched. |
| `page.py` | a page or a few as text (`text DOC-062 12-14`) or as a PNG (`image DOC-048 27 [--dpi N] [--crop x,y,w,h]`). |
| `link.py` | adds home rows to a page's `rows` (merge). |

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

- **Orchestrator** - the main session (Opus). Runs the tools, launches and replaces workers,
  commits, raises blocks, reports to Camden. The only one that runs git.
- **Parse worker** - a small, cheap agent (Haiku) with no memory of anything else: one queue item
  per launch, following `rx7.py playbook parse` (about 2 pages of instructions) and nothing else.
  Kinds: parse, index, catalogue, diagnosis.
- **Figure / review worker** - the same playbook on a stronger model (Sonnet): kinds figure and
  review (a failed item retried).
- **Merge worker** - Sonnet or Opus, `rx7.py playbook merge`: kind merge. Needs judgement (one fact
  once, what conflicts).

## The worker loop (what every agent does - its whole world)

1. `python3 tools/rx7.py claim 02-PROJECTS/05-library --agent <name>` -> the item (rc 2: none; stop).
2. Read the pages: `page.py text`, and `page.py image` + Read for drawings and scrambled tables.
3. Write a rows file and `rx7.py add 02-PROJECTS/05-library facts --rows FILE state=new queue=Q-…`.
4. `rx7.py set 00-CAR pages DOC-….nnn kind= topic= scope= status=` for each page.
5. `rx7.py finish 02-PROJECTS/05-library Q-… result=… rows=…` (or `state=failed result=why`).
6. One line back, stop.

The item is marked `claimed` by step 1 and `done` / `failed` by step 5; nothing else marks it.
An agent that dies leaves its item claimed; after 90 minutes `claim` hands it to the next agent.
Workers never search the record, never commit, never ask Camden anything.

## Running it (the orchestrator)

1. `git pull --rebase`, `rx7.py check`, `python3 …/inventory.py` and `build_queue.py` (both add only
   what is new - safe to rerun after a pull).
2. Launch N workers in the background with the Agent tool, each prompt the same few lines:
   *"You are a parse worker for the Rx7 tree at ~/dev/Rx7. Run `python3 tools/rx7.py playbook
   parse` and follow it exactly for one queue item, with --agent w<k>. Then stop."* - model haiku
   for parse / index / catalogue / diagnosis, sonnet for `--kind figure` and `--kind review`.
   Start with 4, raise to 8-12 once results look right; the lock serialises writes, so more workers
   only queue at it (each write holds it 1-2 s).
3. As each worker reports, launch another while `claim` would still hand out work
   (`rx7.py sql 02-PROJECTS/05-library "select state,count(*) from queue group by state"`).
4. **Every ~25 finished items**: `rx7.py check`; then
   `git add 00-CAR/data 02-PROJECTS/05-library/data && git commit -m "Library: Q-a..Q-b parsed (D-574)"`,
   `git pull --rebase`, `git push`. A refused check is fixed before the commit (usually a worker's
   bad row - fix the row, note it in the item's result).
5. **Spot-check** every 50 items: open three random finished items' pages and compare with their
   facts. A worker that invents or skips gets its items reopened (`set state=open`) and the playbook
   tightened - the playbook is the only lever on cheap workers.
6. `build_queue.py --review` turns failed items into review items for the stronger model.
7. Pause any time: stop launching. Resume: step 1. Nothing is lost - claims time out.

## Phases and when each is done

| Phase | Work rows | Done when |
|---|---|---|
| 0 Structure | L0 | tables, checks, tools, playbooks, this plan - **done 2026-10-14** |
| 1 Inventory | L1 | every PDF a docs row, every page a pages row, cited pages marked, the queue built - **done 2026-10-14** |
| 2 Parse | L2 | no parse / index / catalogue / diagnosis / figure / review item open, claimed or failed; every page parsed, held, indexed, duplicate or empty |
| 3 Merge and cross-check | L3 | `build_queue.py --merge` emptied: every fact merged, duplicate, rejected or raised; every conflict a block; `rx7.py dups` clean (then made a refusal); every `confirm` that only a page could settle re-checked; each page's `rows` naming its home rows |
| 4 The app | L4 | the Manual's References page (every source: link, pages, coverage, the rows each page became), sources on part and system pages, a Diagnosis view; desktop rebuilt |
| 5 Remove | L5, L6 | the offline copy made and named in `docs.offline` (Camden: where); every finished doc's file deleted and marked `gone`; the OCR text and raw research folded or deleted; the 5 tracked vendor PDFs out of git; `check` clean with no PDF in the tree |

## Rules every phase keeps

- A fact cites its page: facts.page during staging; the home row's `source` and `page` after.
- `applies` - this car's figure is blank; another 1979-85 year's is `other-car` and held back from
  the Manual; another model's is not taken unless a part we use needs it.
- 00-CAR never cites a decision (CLAUDE.md §1); notes say what the car is.
- A measured or Camden-checked value is never overwritten by a page (R11): that is a conflict.
- Nothing is deleted from disk before phase 5, and nothing in phase 5 before the offline copy.

## Cost and time (estimate, 2026-10-14)

About 1,230 parse items at 2-5 pages, then roughly one merge item per 25 facts (30-50 thousand
facts likely: 1,200-2,000 merges). A Haiku worker item: roughly 15-40 thousand tokens (the
playbook, the page text, one or two images). A Sonnet merge item: 30-60 thousand. Wall clock with
8 workers: phase 2 in a few long sessions; phase 3 about as long again. Tier by tier: 1 - 482 items, 1,349 pages; 2 - 307, 976; 3 - 325, 877; 4 - 103, 415;
5 - 12, 106. Run tier 1 first and judge the quality before the rest.

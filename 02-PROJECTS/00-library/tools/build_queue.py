"""build_queue.py - turn the coverage map into the agents' queue (D-574, tools/doc/library.md).

    python3 02-PROJECTS/00-library/tools/build_queue.py [--dry]           parse items (phase 2)
    python3 02-PROJECTS/00-library/tools/build_queue.py --merge [--dry]   merge items (phase 3)
    python3 02-PROJECTS/00-library/tools/build_queue.py --review [--dry]  a review item per failed one
    python3 02-PROJECTS/00-library/tools/build_queue.py --reprice [--dry] predictions and caps of every open item
    python3 02-PROJECTS/00-library/tools/build_queue.py --sweep [--dry]   skip engine material, re-prioritise by tier (D-620)

Every page of 00-CAR `pages` that is not finished (open or cited) lands in exactly one queue
item: a few consecutive pages of one document that share a heading. Each item gets a kind, a
brief and a priority, so `rx7.py claim` hands out the most valuable pages of every document
first - not one document after another. Idempotent: a page already in a queue item (any state)
is never queued twice; only new or reopened pages make new items.

Owns: 00-library queue (adds items; never edits one an agent has touched). Reads: 00-CAR docs
and pages.

The priority (higher first), all in one place:
    tier      1: 500  2: 350  3: 200  4: 100  5: 20       - what the document is worth to this car
    status    open: +60   cited: +0                         - pages nothing has read beat re-reads
    scope     this-car +40, mixed/unknown +20, other-year 0, other-model -60
    kind      diagnosis +80, table +40, figure +20          - troubleshooting, then tables, then drawings
    order     - page position / 1000                         - within a document, its front first
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import rx7  # noqa: E402

CAR, LIB = ROOT / "00-CAR", ROOT / "02-PROJECTS" / "00-library"
DRY = "--dry" in sys.argv
TIER = {1: 500, 2: 350, 3: 200, 4: 100, 5: 20}
SCOPE = {"this-car": 40, "mixed": 20, "unknown": 20, "other-year": 0, "other-model": -60, "none": -60}
TROUBLE = re.compile(r"troubl|diagnos|symptom|possible cause|fault find", re.I)

# Engine material is skipped (D-620, 2026-10-16): the 12A never runs again and leaves with its
# automatic, its carburettor and fuel delivery, its emissions, ignition, charging and starting,
# cooling, exhaust, propeller shaft and A/C compressor; the LS swap's own documents stay. A whole
# document is skipped by its path; in a mixed one a page is skipped when its topic is engine
# material and nothing in it is a part that stays (KEEP wins). Parts-catalogue groups 1000A-2599A
# (engine to propeller shaft) are engine material.
ENGINE_DOCS = (
    "00-CAR/library/datasheets/PT006/", "00-CAR/library/datasheets/PT007/", "00-CAR/library/datasheets/PT008/",
    "00-CAR/library/datasheets/PT054/", "00-CAR/library/datasheets/PT230/",
    "00-CAR/library/docs/carburetor-manuals/", "00-CAR/library/docs/rotary-overhaul-criteria-1979/",
    "00-CAR/library/docs/book-yamamoto-rotary-1981/", "00-CAR/library/docs/emissions-check-1981/",
    "00-CAR/library/docs/ac-dealer-install/1980_ac_comp_repair",
    "00-CAR/library/docs/fsm-1980-sections/80RX7_1A_Emissions", "00-CAR/library/docs/fsm-1980-sections/80RX7_4_Fuel_Inlet_Exh",
    "00-CAR/library/docs/fsm-1980-sections/80RX7_5_Engine_Electric", "00-CAR/library/docs/fsm-1980-sections/80RX7_7A_Auto_Trans",
    "00-CAR/library/docs/fsm-1985-sections/1985_RX-7_Workshop_Manual_Section_1_Engine",
    "00-CAR/library/docs/fsm-1985-sections/1985_RX-7_Workshop_Manual_Section_2_Lubrication",
    "00-CAR/library/docs/fsm-1985-sections/1985_RX-7_Workshop_Manual_Section_3_Cooling",
    "00-CAR/library/docs/fsm-1985-sections/1985_RX-7_Workshop_Manual_Section_5_Engine_Electrical",
    "00-CAR/library/docs/fsm-1985-sections/1985_RX-7_Workshop_Manual_Section_7B_Automatic_Transmission",
    "00-CAR/library/docs/fsm-1985-sections/1985_RX-7_Workshop_Manual_Section_8_Propeller_Shaft",
)
ENGINE_TOPIC = re.compile(
    r"rotary|\brotor|apex|eccentric|carbur|choke|emission|air injection|secondary air|catalys|thermal reactor|"
    r"deceleration control|idle compensation|mixture control|throttle opener|shutter valve|tune-up|spark plug|"
    r"ignition (system|control|coil)|igniter|distributor|alternator|starter|charging|oil pump|metering oil|"
    r"lubrication|oil cooler|oil leak|stationary gear|radiator|water pump|thermostat|cooling|coolant|"
    r"\beng(ine)?\b|long block|\ba/t\b|automatic trans|torque converter|kick ?down|inhibitor|governor|"
    r"propeller|exhaust|muffler|intake|fuel pump|fuel filter|compression|compressor|"
    r"\b(1\d|2[0-5])\d\dA", re.I)
KEEP_TOPIC = re.compile(
    r"ignition switch|fuel tank|fuel line|fuel gauge|sender|wiring diagram|component locator|fuse|instrument|"
    r"wiper|washer|lamp|light|heat|blower|evaporator|condenser|receiver drier|body|door|window|seat|brake|"
    r"steer|suspension|wheel|tire|paint|rust|noise|audio|horn|clutch|m/t|manual trans|drive axle|pinion|"
    r"differential|jack|\ba/c\b(?![^/]*compressor)|refrigerant|air condition(?![^/]*compressor)", re.I)
SKIP_RESULT = "skipped: engine material that leaves with the 12A (D-620)"
# The LS swap's documents are reference only since the BP replaced it (D-629, D-632): the LS, its
# CD009 and 350Z gearbox, the T56, the Holley LS pan, the Ford axles. Skipped like the 12A's.
LS_DOCS = ("02-PROJECTS/03-cad/model/library/swap/",)
LS_RESULT = "skipped: the LS swap's documents, reference only since the BP (D-632)"
# The BP swap reads only the pages its engine and gearbox need (D-634). A whole Miata manual is
# read in these page ranges and nothing else (the automatic, axles, steering, brakes, suspension,
# body, body electrical, HVAC and body repair are the Miata's, not the swap's); a path mapped to
# () is skipped whole (the 1990 scan: the 1.6, and the 1994 manual covers its gearbox).
MIATA_KEEP = {
    "00-CAR/library/docs/miata-wm-1994/": ((1, 401), (582, 585), (1109, 1140), (1351, 1456)),
    "00-CAR/library/docs/miata-wm-1990/": (),
}
MIATA_RESULT = "skipped: not a page the BP swap needs (D-634)"
SKIPPED = (SKIP_RESULT, LS_RESULT, MIATA_RESULT)


def ls_doc(d):
    return (d.get("path") or "").startswith(LS_DOCS)


def miata_keep(d):
    path = d.get("path") or ""
    return next((v for k, v in MIATA_KEEP.items() if path.startswith(k)), None)


def skip_result(d):
    return LS_RESULT if ls_doc(d) else MIATA_RESULT if miata_keep(d) is not None else SKIP_RESULT


def engine_doc(d):
    return (d.get("path") or "").startswith(ENGINE_DOCS)


def engine_pages(d, run):
    """Whether these pages of one document are engine material: the whole document is, or every
    page with a topic names engine material and nothing that stays. The swap's own documents
    (owner 01-engine: the BP and its 5-speed, D-632) are never engine material - they are the engine;
    the LS swap's documents are skipped (LS_DOCS)."""
    if ls_doc(d):
        return True
    keep = miata_keep(d)
    if keep is not None:
        return not any(a <= int(p["n"]) <= b for p in run for a, b in keep)
    if (d.get("owner") or "") == "01-engine":
        return False
    if engine_doc(d):
        return True
    topics = [(p.get("topic") or "").strip() for p in run]
    named = [t for t in topics if t]
    return bool(named) and all(ENGINE_TOPIC.search(t) and not KEEP_TOPIC.search(t) for t in named)


BRIEF = {
    "parse": ("Read every page; put each fact as a facts row (spec, step, terminal, circuit, interval, part, "
              "dimension, issue) citing its page; set each page's kind, topic, scope and status."),
    "diagnosis": ("A troubleshooting table: one facts row (kind=diagnosis) per symptom-cause pair - item = symptom, "
                  "value = cause, context = the check and the remedy; then the other facts on the page."),
    "figure": ("Mostly drawings: render the page, decode what the drawing fixes (positions, orders, dimensions, "
               "connector faces, routing) into facts (kind=figure or dimension), each with the figure's id in context."),
    "catalogue": ("Parts-catalogue figure pages: tie each callout of the exploded view to its catalogue row "
                  "(facts kind=catalogue: subject = figure, item = callout, value = part number)."),
    "index": ("Another model's or a kit's pages: only describe each page (kind, topic, scope=other-model, "
              "status=indexed); take a fact only if it names a part this car or a project uses."),
}

# ------------------------------------------------------------------ the model and the cost of each item
#
# Measured 2026-10-14 (a bare `claude -p --model haiku` started outside the tree, then one real
# item end to end - Q-00001, 5 text pages, 70 facts, $0.0108 at --effort low): the worker's
# fixed context - system prompt and tools - is about 34,000 tokens, 22,000 of them read from the
# shared cache and 12,000 written on its first turn; it costs $0.0027 before reading anything.
# Calibrate these after the first session from the queue's tok_in / tok_out / cost_usd columns.

PRICE = {  # $ per million tokens: input, output (list prices, 2026-10-06)
    "haiku": (0.10, 0.50),
    "sonnet": (2.00, 10.00),
    "opus": (4.00, 20.00),
}
FIXED_READ, FIXED_WRITE = 22_000, 12_000   # the worker's fixed context, per call
INSTR = 1_800          # the worker's instructions and the item's brief
IMG = 1_600            # one page image at 110 dpi
TURN_OVERHEAD = 350    # a tool call and its framing
FACT_TOKENS = 110      # one facts row (76 measured 2026-10-14; raised after session s10171148, where Haiku cost 1.97x its estimate)
THINK = 2.0            # thinking, as a share of the written output (1.45 at --effort low on 2026-10-14; raised with FACT_TOKENS, s10171148)
CAP_X = 3.0            # the cap: this many times the prediction ...
CAP_FLOOR = {"haiku": 0.03, "sonnet": 0.40, "opus": 0.80}   # ... and never under this
SONNET_KINDS = {"figure", "catalogue", "review", "merge"}


def model_for(kind, doc):
    if kind in SONNET_KINDS or "wiring-" in (doc.get("path") or ""):
        return "sonnet"
    return "haiku"


def image_pages(pages, doc):
    """The pages a worker must look at, not just read: every page of a scan with no text, every
    drawing or unknown page, and the tables of an OCR text (OCR scrambles columns)."""
    out = []
    for p in pages:
        k = p.get("kind") or "unknown"
        if doc.get("text") == "no" or k in ("figure", "unknown", "photo", "mixed") or (doc.get("text") == "ocr" and k == "table"):
            out.append(p)
    return out


def predict(model, text_tokens, n_img, n_pages):
    """(input tokens, output tokens, $) for one worker: turn 1 reads the instructions and every
    page's text; each image is one more turn and stays in the context after it."""
    turns = 1 + n_img
    content = INSTR + text_tokens
    tin = turns * (FIXED_READ + FIXED_WRITE) + turns * content + IMG * n_img * (n_img + 1) // 2 + TURN_OVERHEAD * turns
    facts = text_tokens / 40 + 12 * n_img + 2 * n_pages   # Q-00001: about 2,900 text tokens gave 70 facts
    tout = int(facts * FACT_TOKENS * (1 + THINK) + 250 * turns)
    pin, pout = PRICE[model]
    # cached reads at a tenth of the input price, writes at 1.25 times; the fixed context is
    # mostly read, the pages are written once and read on every later turn
    read = turns * FIXED_READ + (turns - 1) * (FIXED_WRITE + content) + IMG * n_img * (n_img - 1) // 2 if turns > 1 else FIXED_READ
    write = FIXED_WRITE + content + IMG * n_img + TURN_OVERHEAD * turns
    usd = (read * pin * 0.1 + write * pin * 1.25 + tout * pout) / 1e6
    return int(tin), tout, round(usd, 4)


_TEXT = {}


def text_tokens(doc, page_ns):
    """The page text a worker is handed, in tokens (characters / 4)."""
    did = doc["id"]
    if did not in _TEXT:
        path = ROOT / (doc.get("path") or "")
        if doc.get("text") == "ocr" and doc.get("ocr"):
            pages = (ROOT / doc["ocr"]).read_text(errors="replace").split("\f")
        elif doc.get("text") == "yes" and path.exists():
            pages = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True,
                                   errors="replace").stdout.split("\f")
        else:
            pages = []
        _TEXT[did] = [len(re.sub(r"[ \t]{2,}", " ", t)) // 4 for t in pages]
    lens = _TEXT[did]
    return sum(lens[n - 1] for n in page_ns if n - 1 < len(lens))


def price_item(q, docs, pages_by_id):
    doc = docs.get(q.get("doc"), {})
    ns = pages_in(q.get("pages") or "")
    ps = [pages_by_id[f"{doc['id']}.{n:03d}"] for n in ns if doc and f"{doc['id']}.{n:03d}" in pages_by_id]
    model = model_for(q.get("kind"), doc)
    if q.get("kind") == "merge":
        n = len((q.get("rows") or "").split()) if ".." not in (q.get("rows") or "") else 25
        tin, tout = (FIXED_READ + FIXED_WRITE) * 12 + n * 400 * 12, n * 250
        pin, pout = PRICE[model]
        usd = round(((FIXED_READ + n * 400) * 12 * pin * 0.1 + (FIXED_WRITE + n * 400) * pin * 1.25 + tout * pout) / 1e6, 4)
    else:
        tin, tout, usd = predict(model, text_tokens(doc, ns) if doc else 0, len(image_pages(ps, doc)) if doc else 0, len(ns))
    cap = round(max(CAP_FLOOR[model], usd * CAP_X), 2)
    q.update({"model": model, "est_in": str(tin), "est_out": str(tout), "est_usd": f"{usd:.4f}", "cap_usd": f"{cap:.2f}"})


def reprice():
    """Predictions and caps for every item not yet claimed, from the cost model above."""
    rx7.take_write_lock()
    docs = {d["id"]: d for d in rx7.read_table(CAR, "docs")[1]}
    pages_by_id = {p["id"]: p for p in rx7.read_table(CAR, "pages")[1]}
    qh, queue = rx7.read_table(LIB, "queue")
    n = 0
    for q in queue:
        if q.get("state") == "open":
            price_item(q, docs, pages_by_id)
            n += 1
    report(queue)
    if not DRY:
        rx7.write_table(LIB, "queue", qh, queue)
    print(f"{n} open items priced")
    return 0


def report(queue):
    """The forecast: items, tokens and dollars by model, and by tier of the document."""
    by = {}
    for q in queue:
        if q.get("state") not in ("open", "claimed"):
            continue
        k = q.get("model") or "?"
        b = by.setdefault(k, [0, 0, 0, 0.0, 0.0])
        b[0] += 1; b[1] += int(q.get("est_in") or 0); b[2] += int(q.get("est_out") or 0)
        b[3] += float(q.get("est_usd") or 0); b[4] += float(q.get("cap_usd") or 0)
    tot = [0, 0, 0, 0.0, 0.0]
    print(f"{'model':7} {'items':>6} {'input tok':>12} {'output tok':>11} {'predicted $':>12} {'sum of caps $':>14}")
    for k, b in sorted(by.items()):
        print(f"{k:7} {b[0]:6d} {b[1]:12,d} {b[2]:11,d} {b[3]:12.2f} {b[4]:14.2f}")
        tot = [t + x for t, x in zip(tot, b)]
    print(f"{'all':7} {tot[0]:6d} {tot[1]:12,d} {tot[2]:11,d} {tot[3]:12.2f} {tot[4]:14.2f}")



def head_key(p):
    """A page's running header, reduced to its words: the section a page belongs to."""
    w = re.findall(r"[a-z]{3,}", (p.get("topic") or "").lower())
    return " ".join(sorted(set(w))[:3])


def sec_key(p):
    pr = p.get("printed") or ""
    return re.split(r"[-:]", pr)[0] if re.search(r"[-:]", pr) else ""


def chunks(pages, size):
    """Consecutive pages of one doc, at most `size`, broken where the section changes: the
    printed section number (4A in 4A-16) changes, or a new running header starts and holds
    on the next page too (one odd heading does not split a run)."""
    run = []
    for i, p in enumerate(pages):
        n = int(p["n"])
        if run:
            prev = run[-1]
            nxt = pages[i + 1] if i + 1 < len(pages) else None
            sec_change = sec_key(p) and sec_key(prev) and sec_key(p) != sec_key(prev)
            hk = head_key(p)
            head_change = hk and hk != head_key(prev) and nxt is not None and head_key(nxt) == hk
            if len(run) >= size or n != int(prev["n"]) + 1 or sec_change or head_change:
                yield run
                run = []
        run.append(p)
    if run:
        yield run


def span(nums):
    out, a = [], None
    for i, n in enumerate(nums):
        if a is None:
            a = n
        if i + 1 == len(nums) or nums[i + 1] != n + 1:
            out.append(f"{a}" if a == n else f"{a}-{n}")
            a = None
    return " ".join(out)


def merge_items():
    """Phase 3: every `new` fact not yet in a merge item, in batches of up to 25 that share a
    home area, a system and a kind - so one merge agent reads one narrow slice of one table."""
    rx7.take_write_lock()
    docs = {d["id"]: d for d in rx7.read_table(CAR, "docs")[1]}
    qh, queue = rx7.read_table(LIB, "queue")
    _, facts = rx7.read_table(LIB, "facts")
    taken = set()
    for q in queue:
        if q.get("kind") == "merge":
            for part in (q.get("rows") or "").split():
                a, _, b = part.partition("..")
                taken.update(f["id"] for f in facts if a <= f["id"] <= (b or a))
    groups = {}
    for f in facts:
        if f.get("state") == "new" and f["id"] not in taken:
            owner = docs.get(f["page"].rsplit(".", 1)[0], {}).get("owner") or "00-CAR"
            groups.setdefault((owner, f.get("system") or "-", f["kind"]), []).append(f["id"])
    new = []
    for (owner, system, kind), ids in sorted(groups.items()):
        ids.sort()
        for i in range(0, len(ids), 25):
            batch = ids[i:i + 25]
            new.append({"priority": "300", "kind": "merge", "doc": "", "pages": "", "section": f"{owner} {system} {kind}",
                        "brief": f"Merge {len(batch)} {kind} facts of {system} into {owner}'s tables, one fact once (playbook merge).",
                        "after": "", "state": "open", "rows": " ".join(batch) if len(batch) < 4 else f"{batch[0]}..{batch[-1]}"})
    ids = rx7.next_keys({q["id"] for q in queue} | {"Q-00000"}, len(new)) or []
    for r, i in zip(new, ids):
        r["id"] = i
    for r in new:
        price_item(r, docs, {})
    print(f"{len(new)} merge items for {sum(len(v) for v in groups.values())} facts")
    if not DRY and new:
        rx7.write_table(LIB, "queue", qh, queue + new)
    return 0


def review_items():
    """A `review` item for every failed item that has none: the same pages, for a stronger model."""
    rx7.take_write_lock()
    qh, queue = rx7.read_table(LIB, "queue")
    reviewed = {q.get("rows") for q in queue if q.get("kind") == "review"}
    new = []
    for q in queue:
        if q.get("state") == "failed" and q["id"] not in reviewed:
            new.append({"priority": str(int(q.get("priority") or 0) + 50), "kind": "review", "doc": q.get("doc", ""),
                        "pages": q.get("pages", ""), "section": q.get("section", ""),
                        "brief": f"{q['id']} failed: {q.get('result', '')}. Do it as its brief said: {q.get('brief', '')}",
                        "after": "", "state": "open", "rows": q["id"]})
    ids = rx7.next_keys({q["id"] for q in queue} | {"Q-00000"}, len(new)) or []
    for r, i in zip(new, ids):
        r["id"] = i
    docs = {d["id"]: d for d in rx7.read_table(CAR, "docs")[1]}
    pages_by_id = {p["id"]: p for p in rx7.read_table(CAR, "pages")[1]}
    for r in new:
        price_item(r, docs, pages_by_id)
    print(f"{len(new)} review items")
    if not DRY and new:
        rx7.write_table(LIB, "queue", qh, queue + new)
    return 0


def main():
    if "--merge" in sys.argv:
        return merge_items()
    if "--review" in sys.argv:
        return review_items()
    if "--reprice" in sys.argv:
        return reprice()
    if "--sweep" in sys.argv:
        return sweep()
    rx7.take_write_lock()
    docs = {d["id"]: d for d in rx7.read_table(CAR, "docs")[1]}
    pages = rx7.read_table(CAR, "pages")[1]
    qh, queue = rx7.read_table(LIB, "queue")
    queued = set()
    for q in queue:
        for n in pages_in(q.get("pages") or ""):
            queued.add(f"{q['doc']}.{n:03d}")
    todo = {}
    for p in pages:
        if p["status"] in ("open", "cited") and p["id"] not in queued and not docs[p["doc"]].get("duplicate_of"):
            todo.setdefault(p["doc"], []).append(p)
    new = []
    for did, ps in sorted(todo.items()):
        d = docs[did]
        tier = int(d.get("tier") or 3)
        ps.sort(key=lambda p: int(p["n"]))
        index_only = tier >= 5 or (d.get("scope") == "other-model" and d.get("owner") == "03-cad")
        catalogue = "parts-catalogue" in (d.get("path") or "")
        size = 10 if index_only else 5 if d.get("text") == "yes" else 3 if d.get("text") == "ocr" else 2
        for run in chunks(ps, size):
            topics = " ".join(p.get("topic") or "" for p in run)
            kinds = {p.get("kind") for p in run}
            if index_only:
                kind = "index"
            elif catalogue:
                kind = "catalogue"
            elif TROUBLE.search(topics):
                kind = "diagnosis"
            elif kinds <= {"figure", "unknown"} and d.get("text") != "no":
                kind = "figure"
            else:
                kind = "parse"
            scope = d.get("scope") if d.get("scope") != "mixed" else (run[0].get("scope") or "mixed")
            pr = TIER.get(tier, 200) + SCOPE.get(scope, 0)
            pr += 60 if any(p["status"] == "open" for p in run) else 0
            pr += {"diagnosis": 80, "figure": 20}.get(kind, 0) + (40 if "table" in kinds else 0)
            pr -= int(run[0]["n"]) // 25
            cited = [p["id"] for p in run if p["status"] == "cited"]
            brief = BRIEF[kind] + (f" Already cited by the record: {' '.join(cited)} - read them for what is still missing; "
                                   "the page's rows column lists what is held." if cited else "")
            brief += f" Facts go to {d.get('owner') or '00-CAR'} at the merge."
            if d.get("owner") == "01-engine" and "miata" in (d.get("path") or "").lower():
                brief += (" This is the swap's own engine and gearbox (the Miata BP 1.8 and its 5-speed going into this car, "
                          "D-632): take every fact as fully as for this car - specs, torques, clearances, steps - with "
                          "applies=other-model and context naming the Miata model year; status parsed, never indexed.")
            skip = engine_pages(d, run)
            new.append({"priority": str(pr), "kind": kind, "doc": did, "pages": span([int(p["n"]) for p in run]),
                        "section": (run[0].get("topic") or "")[:70], "brief": brief, "after": "",
                        "state": "skipped" if skip else "open", "result": skip_result(d) if skip else ""})
    pages_by_id = {p["id"]: p for p in pages}
    for r in new:
        price_item(r, docs, pages_by_id)
    new.sort(key=lambda r: (-int(r["priority"]), r["doc"], int(r["pages"].split("-")[0].split()[0])))
    ids = rx7.next_keys({q["id"] for q in queue} | {"Q-00000"}, len(new)) or []
    for r, i in zip(new, ids):
        r["id"] = i
    print(f"{len(new)} new items ({sum(1 for r in new if r['kind'] == 'index')} index-only); queue now {len(queue) + len(new)}")
    for k in ("parse", "diagnosis", "figure", "catalogue", "index"):
        print(f"  {k:10} {sum(1 for r in new if r['kind'] == k)}")
    if not DRY and new:
        rx7.write_table(LIB, "queue", qh, queue + new)
    return 0


def sweep():
    """Re-apply the rules to every open item already queued (D-620): engine material is skipped,
    and each item's priority is recomputed from its document's tier today (the swap's documents
    moved up when the engine project came first). Never touches an item an agent has claimed."""
    rx7.take_write_lock()
    docs = {d["id"]: d for d in rx7.read_table(CAR, "docs")[1]}
    pages_by_id = {p["id"]: p for p in rx7.read_table(CAR, "pages")[1]}
    qh, queue = rx7.read_table(LIB, "queue")
    skipped = moved = 0
    reopened = 0
    for q in queue:
        if not q.get("doc"):
            continue
        d = docs.get(q["doc"], {})
        run = [pages_by_id[f"{q['doc']}.{n:03d}"] for n in pages_in(q.get("pages") or "") if f"{q['doc']}.{n:03d}" in pages_by_id]
        if q.get("state") == "skipped" and q.get("result") in SKIPPED and not engine_pages(d, run):
            q["state"], q["result"] = "open", ""   # the rules no longer call it engine material
            reopened += 1
        if q.get("state") != "open":
            continue
        if engine_pages(d, run):
            q["state"], q["result"] = "skipped", skip_result(d)
            skipped += 1
            continue
        if not run:
            continue
        tier = int(d.get("tier") or 3)
        scope = d.get("scope") if d.get("scope") != "mixed" else (run[0].get("scope") or "mixed")
        kinds = {p.get("kind") for p in run}
        pr = TIER.get(tier, 200) + SCOPE.get(scope, 0)
        pr += 60 if any(p["status"] == "open" for p in run) else 0
        pr += {"diagnosis": 80, "figure": 20}.get(q.get("kind"), 0) + (40 if "table" in kinds else 0)
        pr -= int(run[0]["n"]) // 25
        if str(pr) != q.get("priority"):
            q["priority"] = str(pr)
            moved += 1
    print(f"sweep: {skipped} items skipped as engine material, {reopened} reopened, {moved} re-prioritised; "
          f"{sum(1 for q in queue if q.get('state') == 'open')} open")
    if not DRY:
        rx7.write_table(LIB, "queue", qh, queue)
    return 0


def pages_in(spec):
    out = []
    for part in spec.split():
        a, _, b = part.partition("-")
        if a.isdigit():
            out += list(range(int(a), int(b or a) + 1))
    return out


if __name__ == "__main__":
    sys.exit(main())

"""build_queue.py - turn the coverage map into the agents' queue (D-574, tools/doc/library.md).

    python3 02-PROJECTS/05-library/tools/build_queue.py [--dry]           parse items (phase 2)
    python3 02-PROJECTS/05-library/tools/build_queue.py --merge [--dry]   merge items (phase 3)
    python3 02-PROJECTS/05-library/tools/build_queue.py --review [--dry]  a review item per failed one

Every page of 00-CAR `pages` that is not finished (open or cited) lands in exactly one queue
item: a few consecutive pages of one document that share a heading. Each item gets a kind, a
brief and a priority, so `rx7.py claim` hands out the most valuable pages of every document
first - not one document after another. Idempotent: a page already in a queue item (any state)
is never queued twice; only new or reopened pages make new items.

Owns: 05-library queue (adds items; never edits one an agent has touched). Reads: 00-CAR docs
and pages.

The priority (higher first), all in one place:
    tier      1: 500  2: 350  3: 200  4: 100  5: 20       - what the document is worth to this car
    status    open: +60   cited: +0                         - pages nothing has read beat re-reads
    scope     this-car +40, mixed/unknown +20, other-year 0, other-model -60
    kind      diagnosis +80, table +40, figure +20          - troubleshooting, then tables, then drawings
    order     - page position / 1000                         - within a document, its front first
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import rx7  # noqa: E402

CAR, LIB = ROOT / "00-CAR", ROOT / "02-PROJECTS" / "05-library"
DRY = "--dry" in sys.argv
TIER = {1: 500, 2: 350, 3: 200, 4: 100, 5: 20}
SCOPE = {"this-car": 40, "mixed": 20, "unknown": 20, "other-year": 0, "other-model": -60, "none": -60}
TROUBLE = re.compile(r"troubl|diagnos|symptom|possible cause|fault find", re.I)

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
    print(f"{len(new)} review items")
    if not DRY and new:
        rx7.write_table(LIB, "queue", qh, queue + new)
    return 0


def main():
    if "--merge" in sys.argv:
        return merge_items()
    if "--review" in sys.argv:
        return review_items()
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
        index_only = tier >= 5 or (d.get("scope") == "other-model" and d.get("owner") == "02-cad")
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
            new.append({"priority": str(pr), "kind": kind, "doc": did, "pages": span([int(p["n"]) for p in run]),
                        "section": (run[0].get("topic") or "")[:70], "brief": brief, "after": "", "state": "open"})
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


def pages_in(spec):
    out = []
    for part in spec.split():
        a, _, b = part.partition("-")
        if a.isdigit():
            out += list(range(int(a), int(b or a) + 1))
    return out


if __name__ == "__main__":
    sys.exit(main())

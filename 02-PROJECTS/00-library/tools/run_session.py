"""run_session.py - the manager of a parsing session (D-574, tools/doc/library.md). A script, not
a model: it spends no tokens itself.

    python3 02-PROJECTS/00-library/tools/run_session.py [--minutes 60] [--workers 6]
            [--max-usd N] [--kind K] [--model haiku|sonnet] [--dry] [--no-git]
    python3 02-PROJECTS/00-library/tools/run_session.py --ingest Q-00042 ANSWER.txt   (a hand-run worker's answer)

For --minutes it keeps --workers workers running. Each one: claim the next item (most valuable
first), hand its pages' text and images to a fresh `claude -p` worker of the item's model with
the item's cap (`--max-budget-usd`), parse the answer, write the facts and the pages, finish the
item with the tokens and dollars it used. When the time is up it starts nothing new, lets the
running workers finish, then checks, commits, pushes, and prints the ledger. --max-usd stops
new starts once the actual spend plus the running workers' caps would pass it.

Owns: 00-library queue (claims, finishes, the tok_in / tok_out / cost_usd columns) and facts
(adds); 00-CAR pages (kind, topic, scope, status). Writes go through rx7.py, under its lock.
Workers run in an empty folder under /tmp/rx7-work, so they load no CLAUDE.md and no memory and
can touch nothing in the tree.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import rx7  # noqa: E402

LIB, CAR = ROOT / "02-PROJECTS" / "00-library", ROOT / "00-CAR"
RX7 = [sys.executable, str(ROOT / "tools" / "rx7.py")]
PAGE = [sys.executable, str(LIB / "tools" / "page.py")]
WORK = Path("/tmp/rx7-work")
CLAUDE = shutil.which("claude") or str(Path.home() / ".local/bin/claude")
MODELS = {"haiku": "haiku", "sonnet": "sonnet", "opus": "opus"}
EFFORT = {"haiku": "low", "sonnet": "medium", "opus": "medium"}   # extraction needs little thinking (D-575)
FACT_KINDS = {"spec", "step", "procedure", "terminal", "circuit", "diagnosis", "interval", "part",
              "catalogue", "dimension", "figure", "issue", "note"}
SYSTEMS = {"engine", "fuel", "ignition", "cooling", "electrical", "lighting", "transmission", "driveline",
           "brakes", "suspension", "steering", "wheels", "climate", "body"}
APPLIES = {"this-car", "other-year", "other-model", "unknown"}
PAGE_KINDS = {"text", "table", "figure", "photo", "mixed", "cover", "blank", "index"}
PAGE_STATUS = {"parsed", "indexed", "empty"}
SCOPES = {"this-car", "other-year", "other-model", "none"}
ITEM_TIMEOUT = 20 * 60


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, **kw)


def instructions():
    t = (ROOT / "tools/doc/playbooks/parse.md").read_text(encoding="utf-8")
    return t.split("\n---\n", 1)[1].strip()


def queue_row(qid):
    return next(q for q in rx7.read_table(LIB, "queue")[1] if q["id"] == qid)


def pages_in(spec):
    out = []
    for part in (spec or "").split():
        a, _, b = part.partition("-")
        if a.isdigit():
            out += list(range(int(a), int(b or a) + 1))
    return out


def claim(agent, kind=None, model=None):
    """Claim the next item, for one model or kind when the session is restricted to it."""
    cmd = RX7 + ["claim", "02-PROJECTS/00-library", "--agent", agent] + (["--kind", kind] if kind else []) + (["--model", model] if model else [])
    r = sh(cmd)
    if r.returncode != 0:
        return None
    return queue_row(re.search(r"^id\s+(Q-\d+)", r.stdout, re.M).group(1))


def prepare(q):
    """The worker's folder and prompt: instructions, the brief, every page's text, the images."""
    import build_queue as bq
    docs = {d["id"]: d for d in rx7.read_table(CAR, "docs")[1]}
    pages = {p["id"]: p for p in rx7.read_table(CAR, "pages")[1]}
    doc = docs[q["doc"]]
    ns = pages_in(q["pages"])
    d = WORK / q["id"]
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    text = sh(PAGE + ["text", doc["id"], q["pages"]]).stdout
    imgs = []
    for p in bq.image_pages([pages[f"{doc['id']}.{n:03d}"] for n in ns], doc):
        out = sh(PAGE + ["image", doc["id"], p["n"]]).stdout.strip()
        if out and Path(out).exists():
            dst = d / f"{p['id']}.png"
            shutil.copy(out, dst)
            imgs.append(dst.name)
    ids = " ".join(f"{doc['id']}.{n:03d}" for n in ns)
    prompt = (f"{instructions()}\n\n## Your item: {q['id']} ({q['kind']})\n\nDocument: {doc.get('title', '')} "
              f"(source {doc.get('source', '')}; whom it describes: {doc.get('scope', '')}).\n"
              f"Section: {q.get('section', '')}\nBrief: {q.get('brief', '')}\nYour pages: {ids}\n\n")
    if imgs:
        prompt += "Page images in your folder - Read each one: " + ", ".join(imgs) + "\n\n"
    prompt += "## The pages' text\n\n" + (text.strip() or "(none - read the images)") + "\n"
    (d / "prompt.md").write_text(prompt, encoding="utf-8")
    return d, prompt


def launch(q, d, prompt):
    m = q.get("model") or "haiku"
    cmd = [CLAUDE, "-p", prompt, "--model", MODELS[m], "--effort", EFFORT[m], "--max-budget-usd", q.get("cap_usd") or "0.05",
           "--output-format", "json", "--allowedTools", "Read"]
    out, err = open(d / "answer.json", "w"), open(d / "stderr.txt", "w")
    return subprocess.Popen(cmd, cwd=d, stdin=subprocess.DEVNULL, stdout=out, stderr=err, env=dict(os.environ))


def blocks(text, name):
    m = re.search(rf"```{name}\s*\n(.*?)```", text, re.S)
    return [l.strip() for l in m.group(1).splitlines() if l.strip()] if m else []


def clean(v):
    return v.replace("\n", " ").strip()


def realign(f):
    """A facts row as its 11 fields, even when the worker miscounted its empty ones: `applies` is
    the one field with a fixed vocabulary, so it anchors the row - five fields before the value
    (page kind system subject item), then value, unit, context, then applies, quote, note.
    A short head drops the unit (a diagnosis row: value = cause, context = remedy); a long one
    joins its extra into context; a long tail joins into note. None when no applies is found."""
    if len(f) == 11 and f[8] in APPLIES:
        return f
    idx = [i for i, x in enumerate(f) if x in APPLIES and i >= 5]
    if not idx:
        return f if len(f) == 11 else None
    i = idx[-1]
    head, tail = f[:i], f[i + 1:]
    if len(head) < 6:
        return None
    rest = head[5:]
    if len(rest) == 1:
        vuc = [rest[0], "", ""]
    elif len(rest) == 2:
        vuc = [rest[0], "", rest[1]]
    else:
        vuc = [rest[0], rest[1], " / ".join(x for x in rest[2:] if x)]
    tail = (tail + ["", ""])[:2] if len(tail) <= 2 else [tail[0], " / ".join(x for x in tail[1:] if x)]
    return head[:5] + vuc + [f[i]] + tail


def ingest(q, answer, usage):
    """Write a worker's answer: its facts, its pages, and the item's finish with what it cost."""
    qid, doc = q["id"], q["doc"]
    allowed = {f"{doc}.{n:03d}" for n in pages_in(q["pages"])}
    tok_in = sum(int(usage.get(k) or 0) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    acc = {"tok_in": str(tok_in), "tok_out": str(usage.get("output_tokens") or 0), "cost_usd": f"{usage.get('_cost', 0):.4f}"}
    if answer.strip().startswith("FAILED"):
        sh(RX7 + ["finish", "02-PROJECTS/00-library", qid, "state=failed", f"result={answer.strip()[:300]}"] + [f"{k}={v}" for k, v in acc.items()])
        return "failed", 0
    facts, dropped = [], 0
    for line in blocks(answer, "facts"):
        f = realign([clean(x) for x in line.split("|")])
        if not f or f[0] == "page" or f[0] not in allowed or not f[3] or not f[4]:
            dropped += 1 if f and f[0] != "page" else 0
            continue
        page, kind, system, subject, item, value, unit, context, applies, quote, note = f
        if kind not in FACT_KINDS:
            note, kind = (f"kind {kind}; " + note).strip("; "), "note"
        if system not in SYSTEMS:
            system = ""
        if applies not in APPLIES:
            applies = "unknown"
        facts.append(["next", page, kind, system, subject, item, value, unit, context, applies, quote, note])
    pages = []
    for line in blocks(answer, "pages"):
        f = [clean(x) for x in line.split("|")]
        if f[0] == "page" or len(f) != 5 or f[0] not in allowed:
            continue
        pid, kind, topic, scope, status = f
        pages.append((pid, kind if kind in PAGE_KINDS else "mixed", topic[:80], scope if scope in SCOPES else "", status if status in PAGE_STATUS else "parsed"))
    if not facts and not pages:
        sh(RX7 + ["finish", "02-PROJECTS/00-library", qid, "state=failed", "result=no facts or pages block in the answer"] + [f"{k}={v}" for k, v in acc.items()])
        return "failed", 0
    rng = ""
    if facts:
        rows = d_rows = WORK / qid / "facts.txt"
        d_rows.write_text("id|page|kind|system|subject|item|value|unit|context|applies|quote|note\n" +
                          "\n".join("|".join(x) for x in facts) + "\n", encoding="utf-8")
        r = sh(RX7 + ["add", "02-PROJECTS/00-library", "facts", "--rows", str(rows), "state=new", f"queue={qid}"])
        if r.returncode != 0:
            sh(RX7 + ["finish", "02-PROJECTS/00-library", qid, "state=failed", f"result=facts refused: {r.stdout.strip()[-200:]}"] + [f"{k}={v}" for k, v in acc.items()])
            return "failed", 0
        m = re.search(r"(F-\d+) to (F-\d+)", r.stdout) or re.search(r"facts:(F-\d+) added", r.stdout)
        rng = f"{m.group(1)}..{m.group(2)}" if m and m.lastindex == 2 else (m.group(1) if m else "")
    for pid, kind, topic, scope, status in pages:
        args = [f"kind={kind}", f"topic={topic}", f"status={status}"] + ([f"scope={scope}"] if scope else [])
        sh(RX7 + ["set", "00-CAR", "pages", pid] + args)
    result = f"{len(facts)} facts {rng}".strip() + (f"; {dropped} malformed rows dropped" if dropped else "") + \
             (f"; {len(allowed) - len(pages)} page(s) not reported" if len(pages) < len(allowed) else "")
    sh(RX7 + ["finish", "02-PROJECTS/00-library", qid, f"result={result}", f"rows={rng}"] + [f"{k}={v}" for k, v in acc.items()])
    return "done", len(facts)


def harvest(q, d):
    """Read a finished worker's JSON and ingest it; a capped or crashed worker fails its item."""
    try:
        raw = (d / "answer.json").read_text(encoding="utf-8")
        j = json.loads(raw[raw.index("{"):])   # anything printed before the JSON is not the answer
    except Exception:
        tail = (d / "answer.json").read_text(errors="replace")[-200:] if (d / "answer.json").exists() else "no output"
        sh(RX7 + ["finish", "02-PROJECTS/00-library", q["id"], "state=failed", f"result=worker crashed: {tail}"])
        return "failed", 0, 0.0
    usage = dict(j.get("usage") or {})
    usage["_cost"] = float(j.get("total_cost_usd") or 0)
    if j.get("is_error") or j.get("subtype") != "success":
        acc = [f"tok_out={usage.get('output_tokens') or 0}", f"cost_usd={usage['_cost']:.4f}"]
        sh(RX7 + ["finish", "02-PROJECTS/00-library", q["id"], "state=failed",
                  f"result=worker stopped: {j.get('subtype')} {str(j.get('result') or '')[:150]}"] + acc)
        return "failed", 0, usage["_cost"]
    st, n = ingest(q, j.get("result") or "", usage)
    return st, n, usage["_cost"]


def git_close(items):
    if sh(RX7 + ["check"]).returncode != 0:
        print("check refused - nothing committed; fix the rows it names, then commit by hand")
        return
    sh(["git", "add", "00-CAR/data", "02-PROJECTS/00-library/data"])
    if sh(["git", "diff", "--cached", "--quiet"]).returncode == 0:
        return
    ids = sorted(items)
    msg = (f"Library: {len(ids)} items parsed, {ids[0]}..{ids[-1]} (D-574)\n\nA run_session.py session; the ledger is in the "
           "queue's tok_in / tok_out / cost_usd columns.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    sh(["git", "commit", "-q", "-m", msg])
    if sh(["git", "pull", "--rebase", "-q"]).returncode == 0 and sh(RX7 + ["check"]).returncode == 0:
        print("pushed" if sh(["git", "push", "-q"]).returncode == 0 else "push failed - push next session")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=60)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--max-usd", type=float, default=0)
    ap.add_argument("--kind")
    ap.add_argument("--model", choices=sorted(MODELS))
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--ingest", nargs=2, metavar=("QID", "FILE"))
    a = ap.parse_args()
    sys.path.insert(0, str(LIB / "tools"))
    if a.ingest:
        q = queue_row(a.ingest[0])
        print(ingest(q, Path(a.ingest[1]).read_text(encoding="utf-8"), {}))
        return 0
    if a.dry:
        qs = [q for q in rx7.read_table(LIB, "queue")[1] if q.get("state") == "open"
              and (not a.kind or q.get("kind") == a.kind) and (not a.model or q.get("model") == a.model)]
        qs.sort(key=lambda q: -int(q.get("priority") or 0))
        per = {"haiku": 60, "sonnet": 120, "opus": 150}   # seconds per item, a guess until the first session
        t, spend, n = 0.0, 0.0, 0
        for q in qs:
            t += per.get(q.get("model"), 90) / a.workers
            if t > a.minutes * 60:
                break
            spend += float(q.get("est_usd") or 0)
            n += 1
        print(f"an {a.minutes:.0f}-minute session with {a.workers} workers would take about {n} items "
              f"({qs[0]['id'] if qs else '-'} onwards), predicted ${spend:.2f}; worst case (every cap) "
              f"${sum(float(q.get('cap_usd') or 0) for q in qs[:n]):.2f}")
        for q in qs[:12]:
            print(f"  {q['id']} {q['priority']:>4} {q['kind']:9} {q['model']:6} {q['doc']} p.{q['pages']:<8} est ${q['est_usd']} cap ${q['cap_usd']}  {q.get('section', '')[:40]}")
        return 0
    WORK.mkdir(exist_ok=True)
    stop_at = time.time() + a.minutes * 60
    session = time.strftime("s%m%d%H%M")
    running, done, spent, k = {}, [], 0.0, 0
    ledger = {"done": 0, "failed": 0, "facts": 0}
    while True:
        caps = sum(float(q.get("cap_usd") or 0) for q, _, _ in running.values())
        can_start = time.time() < stop_at and (not a.max_usd or spent + caps < a.max_usd)
        while can_start and len(running) < a.workers:
            k += 1
            q = claim(f"{session}-w{k}", a.kind, a.model)
            if not q:
                can_start = False
                break
            if a.max_usd and spent + caps + float(q.get("cap_usd") or 0) > a.max_usd:
                sh(RX7 + ["set", "02-PROJECTS/00-library", "queue", q["id"], "state=open", "agent=", "claimed="])
                can_start = False
                break
            d, prompt = prepare(q)
            running[q["id"]] = (q, d, (launch(q, d, prompt), time.time()))
            print(f"start  {q['id']} {q['kind']:9} {q['model']:6} {q['doc']} p.{q['pages']}  cap ${q['cap_usd']}", flush=True)
            caps += float(q.get("cap_usd") or 0)
        for qid in list(running):
            q, d, (proc, t0) = running[qid]
            if proc.poll() is None and time.time() - t0 < ITEM_TIMEOUT:
                continue
            if proc.poll() is None:
                proc.kill()
            st, n, cost = harvest(q, d)
            spent += cost
            ledger[st] = ledger.get(st, 0) + 1
            ledger["facts"] += n
            done.append(qid)
            del running[qid]
            print(f"{st:6} {qid} {n:3d} facts  ${cost:.4f}  (session ${spent:.2f})", flush=True)
        if not running and not can_start:
            break
        time.sleep(2)
    print(f"\nsession {session}: {ledger['done']} done, {ledger['failed']} failed, {ledger['facts']} facts, ${spent:.2f}")
    if done:
        sh(RX7 + ["log", "02-PROJECTS/00-library", "session",
                  f"run_session {session}: {ledger['done']} items done, {ledger['failed']} failed, {ledger['facts']} facts, ${spent:.2f}"] + sorted(done)[:1])
        if not a.no_git:
            git_close(done)
    return 0


if __name__ == "__main__":
    sys.exit(main())

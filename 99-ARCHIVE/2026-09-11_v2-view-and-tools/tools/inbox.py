# -*- coding: utf-8 -*-
"""inbox.py - ANSWERS.md, the one place Camden types.

   python tools/rx7.py ask [project]    write ANSWERS.md: every question waiting on him
   python tools/rx7.py take             move what he typed into data/questions/<id>.md

ANSWERS.md sits at the repo root and is a *transfer* file, never the record: `ask`
writes it, Camden types in it, `take` moves the text into the packets and files the
used copy under 99-ARCHIVE/answers/. Nothing here renders and nothing here is a
source of truth - the packets stay canonical.

Three rules keep typed text safe:
  - `ask` refuses to overwrite an ANSWERS.md that still holds unapplied answers.
  - `build` refuses to run while unapplied answers are sitting there (rx7.main).
  - `take` archives the file before clearing it, so a copy always survives.

Owns: the ANSWERS.md format and its parser. Tables: none (reads questions via rx7.DB)."""

import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rx7  # noqa: E402

INBOX = rx7.ROOT / "ANSWERS.md"
ARCHIVE = rx7.ROOT / "99-ARCHIVE" / "answers"

OPEN = ">>> ANSWER {id} >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
CLOSE = "<<< END {id} <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"

BLOCK = re.compile(r"^>>> ANSWER (\S+)[^\n]*\n(.*?)^<<< END \1[^\n]*$", re.M | re.S)
ANSWER_BLOCK = re.compile(r"\n*\*\*ANSWER:\*\*.*\Z", re.S)

HEAD = """# ANSWERS - {n} question{s} waiting on you

**Type your answer in the space between the `>>> ANSWER` and `<<< END` lines.**
Plain sentences are fine - no formatting, no `>` marks, no particular length.
A question you leave blank stays open and is asked again next time; there is no
cost to skipping one. Nothing else in this file is read, so scribble freely.

When you are done: save the file, then say **"I answered questions"** in a session
(or run `python tools/rx7.py take` yourself).

*Generated {when} by `tools/rx7.py ask`. Do not rename or delete the marker lines -
they are how each answer finds its question. This file is not the record: `take`
moves your text into `data/questions/<id>.md` and archives this copy.*

Waiting on you: {tally}

"""


# ------------------------------------------------------------------ parsing

def parse(text: str) -> dict[str, str]:
    """{id: answer text} for every marker pair in an ANSWERS.md. Blank answers included."""
    return {m.group(1): m.group(2).strip() for m in BLOCK.finditer(text)}


def pending(text: str | None = None) -> dict[str, str]:
    """{id: answer} for the answers typed into the inbox and not yet applied."""
    if text is None:
        if not INBOX.exists():
            return {}
        text = INBOX.read_text(encoding="utf-8")
    return {i: a for i, a in parse(text).items() if a.strip()}


def _orphans(text: str, known: set[str]) -> list[str]:
    """Marker ids in the file that no open question claims - a renamed or stale block."""
    return sorted(i for i in parse(text) if i not in known)


# ------------------------------------------------------------------ ask

def _live(phase: str, section: str) -> bool:
    """Is this section answerable in this phase? §1 is design (before the freeze);
    everything else is install validation and is asked when the plan reaches it (c_phase)."""
    if phase in ("PROPOSED", "PLANNING"):
        return section == "1"
    if phase in ("SOURCING", "BUILDING"):
        return section != "1"
    return False


def _waiting(everything: bool = False):
    """[(project_dir, row, body_without_answer_block)] per open question, in table order.
    By default only the ones this phase can actually answer - the rest are noise at the desk."""
    out, later = [], 0
    for d in rx7.all_projects():
        db = rx7.DB(d)
        if "questions" not in db.tables:
            continue
        phase = db.param("phase") or "PERMANENT"
        for q in db.rows("questions", "status = 'open'"):
            if rx7.answered(db.body("questions", q["id"])):
                continue  # already answered in the packet, waiting on /rx7-answers
            if not everything and not _live(phase, q.get("section") or ""):
                later += 1
                continue
            body = ANSWER_BLOCK.sub("", db.body("questions", q["id"])).strip()
            out.append((d, q, body))
    return out, later


def ask(project: str | None = None, force: bool = False, everything: bool = False) -> int:
    items, later = _waiting(everything)
    if project:
        want = rx7.find_project(project).name
        items = [i for i in items if i[0].name == want]

    if INBOX.exists() and not force:
        held = pending()
        if held:
            print(f"ANSWERS.md already holds {len(held)} typed answer(s): {', '.join(sorted(held))}")
            print("Apply them first (say \"I answered questions\", or run: python tools/rx7.py take).")
            print("To throw them away and start over: python tools/rx7.py ask --force")
            return 1

    if not items:
        print("Nothing is waiting on you - no open questions.")
        if INBOX.exists():
            INBOX.unlink()
            print("removed ANSWERS.md")
        return 0

    tally = {}
    for d, _, _ in items:
        tally[d.name] = tally.get(d.name, 0) + 1
    parts = []
    for k in sorted(tally, key=lambda k: -tally[k]):
        parts.append(f"{k} {tally[k]}")

    tail = ""
    if later:
        tail = (f"\n\n*{later} more question(s) are open but belong to a later phase - "
                f"install checks and measurements, asked when the plan reaches them. "
                f"`python tools/rx7.py ask --all` if you want them anyway.*")

    chunks = [HEAD.format(n=len(items), s="" if len(items) == 1 else "s",
                          when=datetime.now().strftime("%Y-%m-%d %H:%M"),
                          tally=" · ".join(parts) + tail)]
    for d, q, body in items:
        sec = q.get("section") or "?"
        head = f"---\n\n## {q['id']} · {q['title']}\n\n*{d.name} · §{sec}"
        if q.get("ask"):
            head += f" · wants: **{q['ask']}**"
        if q.get("opened"):
            head += f" · opened {q['opened']}"
        head += f" · packet `{d.name}/data/questions/{q['id']}.md`*\n"
        chunks.append(f"{head}\n{body}\n\n{OPEN.format(id=q['id'])}\n\n\n{CLOSE.format(id=q['id'])}\n")
    INBOX.write_text("\n".join(chunks), encoding="utf-8", newline="\n")

    print(f"wrote ANSWERS.md - {len(items)} question(s): " + " · ".join(parts)
          + (f"  ({later} held for a later phase)" if later else ""))
    print("Type between the >>> ANSWER and <<< END lines, then say \"I answered questions\".")
    return 0


# ------------------------------------------------------------------ take

def _apply(db: rx7.DB, qid: str, answer: str) -> None:
    """Write answer into the packet's **ANSWER:** block, as the quoted form the record uses."""
    p = db.data / "questions" / f"{qid}.md"
    body = p.read_text(encoding="utf-8")
    quoted = "\n".join("> " + l if l.strip() else ">" for l in answer.splitlines())
    block = f"**ANSWER:**\n{quoted}\n"
    if "**ANSWER:**" in body:
        # lambda, not a replacement string: his answer is arbitrary text and a
        # backslash in it (a Windows path, a \n he typed) would be read as an escape.
        body = ANSWER_BLOCK.sub(lambda m: "\n\n" + block, body)
    else:
        body = body.rstrip() + "\n\n" + block
    p.write_text(body, encoding="utf-8", newline="\n")


def take(quiet: bool = False) -> dict[str, str]:
    """Move every typed answer from ANSWERS.md into its packet. Returns {id: answer}."""
    if not INBOX.exists():
        return {}
    text = INBOX.read_text(encoding="utf-8")
    typed = pending(text)

    owner, known = {}, set()
    for d in rx7.all_projects():
        db = rx7.DB(d)
        if "questions" not in db.tables:
            continue
        for q in db.rows("questions"):
            known.add(q["id"])
            owner.setdefault(q["id"], db)

    lost = [i for i in typed if i not in owner]
    for i in _orphans(text, known):
        print(f"  ~ ANSWERS.md has a block for {i}, which is not a question in any project")
    if lost:
        print(f"  !! no packet for {', '.join(lost)} - their text is left in ANSWERS.md")

    applied = {}
    for qid, answer in typed.items():
        if qid in lost:
            continue
        _apply(owner[qid], qid, answer)
        applied[qid] = answer
        if not quiet:
            n = len(answer.splitlines())
            print(f"  {qid} <- {n} line(s), {len(answer)} chars")

    if applied and not lost:
        ARCHIVE.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        dest = ARCHIVE / f"ANSWERS-{stamp}.md"
        n = 2
        while dest.exists():
            dest = ARCHIVE / f"ANSWERS-{stamp}-{n}.md"; n += 1
        dest.write_text(text, encoding="utf-8", newline="\n")
        INBOX.unlink()
        if not quiet:
            print(f"  archived your copy -> {dest.relative_to(rx7.ROOT).as_posix()}")
    if not quiet:
        print(f"take: {len(applied)} answer(s) moved into the packets")
    return applied

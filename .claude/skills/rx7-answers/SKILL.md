---
name: rx7-answers
description: Apply every answer Camden wrote under **ANSWER:** in an Rx7 project's question packets — rule or sharpen each, carry it through data, templates, seams, decisions and the build. Trigger on "I answered questions". /rx7-answers [project|all].
---

# /rx7-answers `[project|all]`

Camden answers in place, in `data/questions/<id>.md` under `**ANSWER:**`, then says "I answered questions". This routine is the whole job — one pass, one script of edits, one build.

1. **Find every answer:** `python tools/answers.py`. Read them all before touching anything.
2. **Classify each.** A *ruling* (yes / no / a choice / "follow recommendations") → a decision. A *brief* (guidelines, a re-framing, "help me choose") → sharpen the packet: new options, one recommendation, a one-word ask; it stays open. A *question back* → answer it inside the packet body, above the ANSWER block, and leave it open. A *fact he learned* about the car → `00-CAR` rows (`issues`, `vehicle`, `specs`, `service`) and every project row it corrects.
3. **For each ruling, in this order:**
   (a) `python tools/rx7.py -p <project> new D "<title>" system="<section>" closes=<Q-id> supersedes=<D-ids> who="Camden's call"` — this reserves the number, writes the index row, closes the question and marks superseded decisions. Then write the body in `data/decisions/<id>.md`: the decision in bold, his words, the reasoning, what it supersedes by id, the consequences in the data. Set `questions.<id>.outcome` to the one-line outcome.
   (b) Every data row the ruling changes — `get` first, then `set` / `add` / `del`. Sweep the tables the ruling touches by name; a ruling that touches three projects is applied to all three in the same pass.
   (c) Every template that stated the old fact: `python tools/rx7.py -p <project> find "<old term>"` plus a grep of `templates/`, the other projects and `01-REFERENCE` (which must stay free of the new design). Add the retired term to `data/retired.csv` (`term, retired_by`) so the build refuses it from now on.
   (d) New questions the ruling raises → packets with a recommendation and a one-word ask, in the project that owns them; a question moved between projects keeps its number (`status=moved`, `closer=<destination>`) and is `new`-ed there under the same id only if the registry allows — otherwise it is cited, never re-created.
   (e) Work rows gated on the question: gate met → leave open for `/rx7-plan`; the ruling itself did the work → `state=done`.
4. **Seams, every time.** Luxury `provisions` against electrical cavity states, engine-swap `handover`, `00-CAR` `issues` and `planned` — the builds' cross-project checks catch what a ruling moved; run `python tools/rx7.py -a build`.
5. **Phase.** If the ruling is the design freeze, `set project phase value=SOURCING`; if it is a step in BUILDING, the shop assistant's rules apply.
6. **Build all, fix, build again.** A refusal names the row; fix the data, never the check.
7. **Log:** `python tools/rx7.py -p <project> log answers "<rulings by id, one line>" <ids>`.
8. **Report, in this order:** rulings by `D-` (one line each) · packets sharpened that now want one word · new packets · what left or joined the carts · what stays open. Never re-ask anything he answered; never restate a packet he can read.

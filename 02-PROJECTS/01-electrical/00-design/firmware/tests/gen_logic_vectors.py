#!/usr/bin/env python3
"""gen_logic_vectors.py - the PMU logic rows' test vectors, generated from the record (Y8, R2).

Reads 02-PROJECTS/01-electrical/data/logic.csv (one row per output: its expression, inrush and
retry), ladders.csv and inputs.csv (the states each A-input can read, and how it is decoded),
rules.csv (the terms a rule defines in-line, e.g. flasher's `hazard` = ...) and pins.csv (each
output's inrush_x / inrush_ms, the other home of the inrush figure), and writes logic_vectors.h
beside this script. The record is the master; that header is build output and not versioned.

What it parses, from the head of each `expression` cell:
  A<n> == STATE   A<n> != STATE   A<n> >= STATE (also <=, >, <)   A<n> not STATE
  ||  OR  &&  AND  !  ( ... )  and lower-case terms (flasher_phase, popup_cycle, ...)
`>=` and friends need an ordered ladder: a series ladder decoded by conductance (A15, A16),
ranked by the number of resistors in series (`bias only` = 0). `not STATE` reads "not reading
STATE alone or as part of a combined state" (A3 not PARKED is false at BRAKE+PARKED, as the
wiper-park rule releases the latch there); `!=` is exact. A term a rule defines in-line
(`hazard` = A8 == HAZARD || A8 == HAZ+HORN) is expanded. A leading `On when` is skipped, and a
bare `DISABLED` is an output held off. The parse stops at the first separator it cannot read
past (; — " - " ( . ,) and the rest of the cell is PROSE: emitted as a comment, listed here,
and carried in the header so the suites print it as hand-tested - never dropped. A row whose
parse fails inside a group keeps the disjuncts before the failure as sufficient conditions
(those vectors are all ON) and is flagged partial. `hold the previous state while X is active`
removes the X vectors to hand-testing. FAULT is not a ladder state: every FAULT clause is prose.

For each row: every combination of the referenced inputs' ladder states and the terms' 0/1, the
expected channel state, and the inrush (x10, ms) and retry (count, every ms, latch) as numbers.

Exit 1 when the record cannot be turned into vectors: an expression names a state its input's
ladder does not have, an input with no ladder, an order comparison on an unordered ladder, a
channel with no pins row, or an inrush / retry cell that is not readable. Disagreements inside
the record (logic.inrush vs pins.inrush_x/ms, logic.retry vs rules retry-class) are WARNINGS,
flagged in the header so the suites skip and list them. Stdlib only, Python 3.9.
"""
import csv
import itertools
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "data"
OUT = HERE / "logic_vectors.h"
MAXV = 4                                  # inputs / terms per vector, per kind


def read(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def clean(s):
    return (s or "").replace("\\|", "|").strip()


# ---------------------------------------------------------------- tokens
TOK = re.compile(r"""
    (?P<ws>\s+)
  | (?P<or>\|\||\bOR\b)
  | (?P<and>&&|\bAND\b)
  | (?P<cmp>==|!=|>=|<=|>|<|\bnot\b(?=\s+[A-Z]))
  | (?P<bang>!)
  | (?P<lp>\()
  | (?P<rp>\))
  | (?P<input>\bA\d+\b)
  | (?P<state>\b[A-Z][A-Z0-9_]*(?:\+[A-Z][A-Z0-9_]*)*)
  | (?P<term>\b[a-z][a-z0-9_]*\b)
""", re.X)
SEPARATOR = re.compile(r"(?:;|—|-\s|\(|\.|,|$)")   # a "-" counts only with a space before it


def tokens(s):
    out, i = [], 0
    while i < len(s):
        m = TOK.match(s, i)
        if not m:
            out.append(("stop", s[i:], i))
            break
        kind = m.lastgroup
        if kind != "ws":
            out.append((kind, m.group(), i))
        i = m.end()
    out.append(("end", "", len(s)))
    return out


class ParseError(Exception):
    pass


class Parser:
    """Recursive descent over the head of an expression. Nodes: ('or', [..]), ('and', [..]),
    ('not', n), ('cmp', input, op, state), ('term', name), ('const', 0|1)."""

    def __init__(self, text, defs, ladders):
        self.text, self.toks, self.i = text, tokens(text), 0
        self.defs, self.ladders = defs, ladders
        self.disjuncts = []                  # the top level's parsed disjuncts, for a partial

    def peek(self):
        return self.toks[self.i]

    def take(self):
        t = self.toks[self.i]
        self.i += 1
        return t

    def parse_top(self):
        node = self.parse_or(top=True)
        stop = self.peek()[2]
        spaced = stop > 0 and self.text[stop - 1].isspace()
        if not SEPARATOR.match(self.text, stop) or (self.text[stop:stop + 1] == "-" and not spaced):
            raise ParseError(f"no separator at '{self.text[stop:stop + 30]}'")
        return node, stop

    def parse_or(self, top=False):
        items = [self.parse_and()]
        if top:
            self.disjuncts = list(items)
        while self.peek()[0] == "or":
            self.take()
            items.append(self.parse_and())
            if top:
                self.disjuncts = list(items)
        return items[0] if len(items) == 1 else ("or", items)

    def parse_and(self):
        items = [self.parse_unary()]
        while self.peek()[0] == "and":
            self.take()
            items.append(self.parse_unary())
        return items[0] if len(items) == 1 else ("and", items)

    def parse_unary(self):
        kind, val, pos = self.peek()
        if kind == "bang":
            self.take()
            return ("not", self.parse_unary())
        if kind == "lp":
            self.take()
            n = self.parse_or()
            if self.peek()[0] != "rp":
                raise ParseError(f"unclosed group at '{self.text[self.peek()[2]:self.peek()[2] + 30]}'")
            self.take()
            return n
        if kind == "input":
            self.take()
            op = self.take()
            st = self.take()
            if op[0] != "cmp" or st[0] != "state":
                raise ParseError(f"'{val}' is not compared with a state at '{self.text[pos:pos + 30]}'")
            if val not in self.ladders:
                raise ParseError(f"{val} has no ladder")
            return ("cmp", val, op[1], st[1])
        if kind == "term":
            self.take()
            nxt = self.peek()[0]
            if nxt in ("cmp", "input", "state", "term"):
                raise ParseError(f"'{val}' is followed by '{self.text[self.peek()[2]:self.peek()[2] + 20]}'")
            if val in self.defs:
                return self.defs[val]
            return ("term", val)
        if kind == "state" and val == "DISABLED":
            self.take()
            return ("const", 0)
        raise ParseError(f"cannot read '{self.text[pos:pos + 30]}'")


def inputs_of(n, acc):
    k = n[0]
    if k in ("or", "and"):
        for c in n[1]:
            inputs_of(c, acc)
    elif k == "not":
        inputs_of(n[1], acc)
    elif k in ("cmp", "term"):
        bucket = acc.setdefault("in" if k == "cmp" else "term", [])
        if n[1] not in bucket:
            bucket.append(n[1])
    return acc


def evaluate(n, env, ladders):
    k = n[0]
    if k == "const":
        return n[1]
    if k == "or":
        return int(any(evaluate(c, env, ladders) for c in n[1]))
    if k == "and":
        return int(all(evaluate(c, env, ladders) for c in n[1]))
    if k == "not":
        return 1 - evaluate(n[1], env, ladders)
    if k == "term":
        return env[n[1]]
    _, inp, op, st = n
    cur = env[inp]
    if op == "==":
        return int(cur == st)
    if op == "!=":
        return int(cur != st)
    if op == "not":
        return int(st not in cur.split("+"))
    rank = {s: r for s, r in ladders[inp]}
    a, b = rank[cur], rank[st]
    return int({">=": a >= b, "<=": a <= b, ">": a > b, "<": a < b}[op])


def check_states(n, ladders, ranked, errors, rid):
    k = n[0]
    if k in ("or", "and"):
        for c in n[1]:
            check_states(c, ladders, ranked, errors, rid)
    elif k == "not":
        check_states(n[1], ladders, ranked, errors, rid)
    elif k == "cmp":
        _, inp, op, st = n
        names = [s for s, _ in ladders[inp]]
        if op == "not":
            if not any(st in s.split("+") for s in names):
                errors.append(f"{rid}: {inp} has no state containing {st} (ladders: {', '.join(names)})")
        elif st not in names:
            errors.append(f"{rid}: {inp} == {st} - {inp}'s ladder has no {st} (ladders: {', '.join(names)})")
        if op in (">=", "<=", ">", "<") and inp not in ranked:
            errors.append(f"{rid}: {inp} {op} {st} - {inp} is not an ordered (conductance) ladder")


def series_rank(r):
    r = (r or "").strip().lower()
    if r.startswith("bias"):
        return 0
    return len([p for p in r.split("+") if p.strip()])


def parse_inrush(cell):
    c = clean(cell)
    if c in ("", "—", "-"):
        return (0, 0)
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*×\s*for\s*(\d+(?:\.\d+)?)\s*(ms|s)", c)
    if not m:
        return None
    ms = float(m.group(2)) * (1000 if m.group(3) == "s" else 1)
    return (round(float(m.group(1)) * 10), round(ms))


def parse_retry(cell, cls):
    """(count, every_ms, latch) - latch 0 none, 1 latch and annunciate, 2 off until the key
    leaves RUN; None when unreadable; 'hand' for the conditional class (two policies)."""
    c = clean(cell)
    if cls == "conditional":
        return "hand"
    if c in ("", "—", "-"):
        return (0, 0, 0)
    found = re.findall(r"(\d+) at (\d+(?:\.\d+)?) s", c)
    if len(found) != 1:
        return None
    latch = 0 if "no latch" in c else 2 if "until the key leaves" in c else 1 if "latch" in c else None
    if latch is None:
        return None
    return (int(found[0][0]), round(float(found[0][1]) * 1000), latch)


def cstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> int:
    errors, warnings = [], []
    # ---- ladders: input -> [(state, rank)], in ladder order; ranked = conductance ladders
    inputs = {r["id"].strip(): r for r in read("inputs.csv")}
    ladders, ranked = {}, set()
    for r in read("ladders.csv"):
        ladders.setdefault(r["input"].strip(), []).append((r["state"].strip(), series_rank(r["r"])))
    for inp in ladders:
        if (inputs.get(inp, {}).get("decode") or "").strip() == "conductance":
            ladders[inp].sort(key=lambda sr: sr[1])
            ranks = [r for _, r in ladders[inp]]
            if len(set(ranks)) == len(ranks):
                ranked.add(inp)
            else:
                errors.append(f"{inp}: two states share a series position ({ranks}) - not orderable")
    # ---- the terms rules define in-line: `name` = expression.
    defs = {}
    for r in read("rules.csv"):
        for m in re.finditer(r"`([a-z_]+)`\s*=\s*", clean(r["definition"])):
            text = clean(r["definition"])[m.end():]
            try:
                node, _ = Parser(text, {}, ladders).parse_top()
                defs[m.group(1)] = node
            except ParseError as e:
                errors.append(f"rules {r['id']}: `{m.group(1)}` = ... unreadable ({e})")
    # ---- retry-class policy from rules retry-class ("lamp - 3 retries at 5 s")
    policy = {}
    for r in read("rules.csv"):
        if r["id"].strip() == "retry-class":
            for m in re.finditer(r"\b([a-z]+) - (\d+) retr(?:y|ies) at (\d+(?:\.\d+)?) s", r["definition"]):
                policy[m.group(1)] = (int(m.group(2)), round(float(m.group(3)) * 1000))
    pins = {r["name"].strip(): r for r in read("pins.csv") if (r.get("type") or "").strip() == "output"}

    states = [(inp, s, rk if inp in ranked else -1) for inp in sorted(ladders, key=lambda x: int(x[1:]))
              for s, rk in ladders[inp]]
    sidx = {(i, s): n for n, (i, s, _) in enumerate(states)}
    terms = []
    rows, vectors, report = [], [], []

    for lr in read("logic.csv"):
        rid = lr["id"].strip()
        expr = clean(lr["expression"])
        channels = [c.strip() for c in lr["channel"].split("·") if c.strip()]
        head = re.sub(r"^\s*on when\s+", "", expr, flags=re.I)
        lead = len(expr) - len(head)
        node, prose, partial = None, "", 0
        p = Parser(head, defs, ladders)
        try:
            node, stop = p.parse_top()
            prose = head[stop:].strip(" ;—-.,—")
            if expr[:lead].strip():
                prose = (expr[:lead].strip() + " ... " + prose).strip()
        except ParseError as e:
            if p.disjuncts and len(p.disjuncts) >= 1 and p.i > 0 and any(t[0] == "or" for t in p.toks[:p.i]):
                node = p.disjuncts[0] if len(p.disjuncts) == 1 else ("or", p.disjuncts)
                partial = 1
                prose = f"[unparsed: {e}] " + expr
            else:
                prose = f"[unparsed: {e}] " + expr
        disabled = 1 if re.search(r"\bDISABLED\b", expr) else 0
        for ch in channels:
            if ch not in pins:
                errors.append(f"{rid}: channel {ch} has no output row in pins")
        # inrush, against pins
        inr = parse_inrush(lr["inrush"])
        inr_conflict = 0
        if inr is None:
            errors.append(f"{rid}: inrush '{clean(lr['inrush'])}' is not 'N× for T ms' or '—'")
            inr = (0, 0)
        for ch in channels:
            pr = pins.get(ch)
            if not pr:
                continue
            px = pr.get("inrush_x", "").strip()
            pm = pr.get("inrush_ms", "").strip()
            pin_inr = (round(float(px) * 10), int(float(pm))) if px and pm else (0, 0)
            norm = lambda t: (0, 0) if t[1] == 0 else t  # a 0 ms window is no inrush
            if norm(pin_inr) != norm(inr):
                inr_conflict = 1
                warnings.append(f"{rid}: logic.inrush '{clean(lr['inrush'])}' vs pins {ch} inrush_x='{px}' "
                                f"inrush_ms='{pm}' - two homes disagree (R2)")
        # retry, against rules retry-class
        cls = (lr["retry_class"] or "").strip()
        ret = parse_retry(lr["retry"], cls)
        ret_conflict, ret_hand = 0, 0
        if ret is None:
            errors.append(f"{rid}: retry '{clean(lr['retry'])}' is not 'N at T s, ...' or '—'")
            ret = (0, 0, 0)
        elif ret == "hand":
            ret_hand, ret = 1, (-1, 0, -1)
        elif cls in policy and ret[:2] != policy[cls]:
            ret_conflict = 1
            warnings.append(f"{rid}: retry '{clean(lr['retry'])}' vs rules retry-class {cls} = {policy[cls]}")

        vec_rows, held = [], []
        if node is not None:
            check_states(node, ladders, ranked, errors, rid)
            acc = inputs_of(node, {})
            ins, tms = acc.get("in", []), acc.get("term", [])
            if len(ins) > MAXV or len(tms) > MAXV:
                errors.append(f"{rid}: more than {MAXV} inputs or terms")
                ins, tms = ins[:MAXV], tms[:MAXV]
            for t in tms:
                if t not in terms:
                    terms.append(t)
            holds = set(re.findall(r"hold the (?:previous|last) state while ([A-Z][A-Z0-9_+]*) is active", expr))
            domains = [[s for s, _ in ladders[i]] for i in ins] + [[0, 1]] * len(tms)
            if not errors or all(not e.startswith(rid + ":") for e in errors):
                for combo in itertools.product(*domains):
                    env = dict(zip(ins + tms, combo))
                    if any(env[i] in holds for i in ins):
                        held.append(" ".join(f"{k}={v}" for k, v in env.items()))
                        continue
                    want = evaluate(node, env, ladders)
                    if partial and not want:
                        continue                      # only the parsed disjuncts' ON is known
                    vec_rows.append(([sidx[(i, env[i])] for i in ins],
                                     [(terms.index(t), env[t]) for t in tms], want))
        first = len(vectors)
        for v in vec_rows:
            vectors.append((len(rows), v))
        hand = prose
        if held:
            hand = (hand + " | held, hand-tested: " + "; ".join(held)).strip(" |")
        if ret_hand:
            hand = (hand + " | retry: " + clean(lr["retry"])).strip(" |")
        rows.append(dict(id=rid, channels=channels, expr=expr, disabled=disabled, partial=partial,
                         inr=inr, inr_conflict=inr_conflict, cls=cls, ret=ret, ret_conflict=ret_conflict,
                         first=first, count=len(vec_rows), held=len(held), hand=hand))
        tag = "partial" if partial else ("unparsed" if node is None else "")
        report.append(f"  {rid:<16} {len(vec_rows):>3} vectors{(' (' + tag + ')') if tag else ''}"
                      f"{('  +' + str(len(held)) + ' held') if held else ''}"
                      f"{'  DISABLED this build' if disabled else ''}"
                      f"{'  hand: ' + hand[:90] if hand else ''}")

    # ---------------------------------------------------------------- write
    L = ["/* logic_vectors.h - generated by gen_logic_vectors.py from logic.csv, ladders.csv,",
         " * inputs.csv, rules.csv and pins.csv (the record is the master). Do not edit; run.sh",
         " * rewrites it. Vectors are steady state: the inputs held, every timer settled. */",
         "#ifndef LOGIC_VECTORS_H", "#define LOGIC_VECTORS_H", "#include <stdint.h>", "",
         f"#define LV_STATES  {len(states)}", f"#define LV_TERMS   {len(terms)}",
         f"#define LV_ROWS    {len(rows)}", f"#define LV_VECTORS {len(vectors)}", f"#define LV_MAXV    {MAXV}", "",
         "/* every ladder state; rank is the series position on an ordered ladder, else -1 */",
         "typedef struct { const char *input; const char *state; int8_t rank; } lv_state_t;",
         "static const lv_state_t LV_STATE[LV_STATES] = {"]
    L += [f"    {{ {cstr(i)}, {cstr(s)}, {rk} }}," for i, s, rk in states]
    L += ["};", "", "/* the free terms the expressions read (a term a rule defines is expanded) */",
          f"static const char *const LV_TERM[LV_TERMS ? LV_TERMS : 1] = {{ {', '.join(cstr(t) for t in terms) or '0'} }};", "",
          "/* latch: 0 none, 1 latch and annunciate, 2 off until the key leaves RUN; -1 hand (conditional) */",
          "typedef struct {",
          "    const char *id; const char *channel[2]; const char *expression;",
          "    uint8_t disabled;        /* the record says the output is DISABLED this build: held off */",
          "    uint8_t partial;         /* only the parsed disjuncts' ON vectors exist */",
          "    uint16_t inrush_x10, inrush_ms; uint8_t inrush_conflict;   /* conflict: logic vs pins */",
          "    const char *retry_class; int8_t retry_count; uint32_t retry_every_ms; int8_t latch; uint8_t retry_conflict;",
          "    uint16_t first, count;   /* into LV_VECTOR */",
          "    uint16_t held;           /* vectors moved to hand-testing by a hold clause */",
          "    const char *hand;        /* the prose the generator could not turn into vectors; \"\" none */",
          "} lv_row_t;", "",
          "static const lv_row_t LV_ROW[LV_ROWS] = {"]
    for r in rows:
        ch = r["channels"] + ["", ""]
        L.append(f"    /* {r['id']}: {r['expr'][:150].replace('*/', '* /')} */")
        L.append(f"    {{ {cstr(r['id'])}, {{ {cstr(ch[0])}, {cstr(ch[1]) if ch[1] else '0'} }}, {cstr(r['expr'])},")
        L.append(f"      {r['disabled']}, {r['partial']}, {r['inr'][0]}, {r['inr'][1]}, {r['inr_conflict']},")
        L.append(f"      {cstr(r['cls'])}, {r['ret'][0]}, {r['ret'][1]}, {r['ret'][2]}, {r['ret_conflict']},")
        L.append(f"      {r['first']}, {r['count']}, {r['held']}, {cstr(r['hand'])} }},")
    L += ["};", "",
          "/* in[]: LV_STATE indices, -1 ends; term[]: LV_TERM indices with tval[], -1 ends */",
          "typedef struct { uint8_t row; int16_t in[LV_MAXV]; int8_t term[LV_MAXV]; uint8_t tval[LV_MAXV]; uint8_t expect; } lv_vector_t;",
          "static const lv_vector_t LV_VECTOR[LV_VECTORS ? LV_VECTORS : 1] = {"]
    for ri, (ins, tms, want) in vectors:
        a = ins + [-1] * (MAXV - len(ins))
        t = [x for x, _ in tms] + [-1] * (MAXV - len(tms))
        tv = [v for _, v in tms] + [0] * (MAXV - len(tms))
        desc = " ".join([f"{states[i][0]}={states[i][1]}" for i in ins] + [f"{terms[x]}={v}" for x, v in tms])
        L.append(f"    {{ {ri}, {{ {', '.join(map(str, a))} }}, {{ {', '.join(map(str, t))} }}, "
                 f"{{ {', '.join(map(str, tv))} }}, {want} }},  /* {rows[ri]['id']}: {desc} -> {'ON' if want else 'off'} */")
    if not vectors:
        L.append("    { 0, {-1}, {-1}, {0}, 0 }")
    L += ["};", "", "#endif", ""]

    for w in warnings:
        print("gen_logic_vectors: WARNING", w)
    if errors:
        for e in errors:
            print("gen_logic_vectors:", e)
        return 1
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"gen_logic_vectors: {OUT.name} written - {len(rows)} rows, {len(vectors)} vectors, "
          f"{len(states)} ladder states, {len(terms)} terms ({', '.join(terms)})")
    for line in report:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Step 0 repair, 2026-09-08f — undo the ID collision left by apply-rx7-changes.py.

Runs against a tree root given as argv[1]. Every anchor is asserted: a miss stops the
script before anything is written (all edits are computed first, written last).
See PROPOSAL-system-v2.md Appendix A for what each edit is and why.
"""
import csv, io, sys, re
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
EB = ROOT / "02-PROJECTS" / "electrical-build"
pending = {}          # path -> new text

def rd(p):  return p.read_text(encoding="utf-8")
def stage(p, s): pending[p] = s

def swap(p, old, new, count=1):
    s = pending.get(p) or rd(p)
    n = s.count(old)
    assert n == count, f"{p.relative_to(ROOT)}: expected {count} of {old[:70]!r}, found {n}"
    stage(p, s.replace(old, new))

def csv_set(p, key, col, fn):
    s = pending.get(p) or rd(p)
    rows = list(csv.reader(io.StringIO(s)))
    hdr = rows[0]; ci = hdr.index(col)
    hit = [r for r in rows[1:] if r[0] == key]
    assert len(hit) == 1, f"{p.name}: key {key!r} matched {len(hit)}"
    hit[0][ci] = fn(hit[0][ci])
    out = io.StringIO(); w = csv.writer(out, lineterminator="\n"); w.writerows(rows)
    stage(p, out.getvalue())

def csv_add_after(p, after, row):
    s = pending.get(p) or rd(p)
    rows = list(csv.reader(io.StringIO(s)))
    assert len(row) == len(rows[0]), f"{p.name}: row has {len(row)} cols, header {len(rows[0])}"
    assert not any(r[0] == row[0] for r in rows[1:]), f"{p.name}: {row[0]} exists"
    i = [k for k, r in enumerate(rows) if r[0] == after]
    assert len(i) == 1, f"{p.name}: --after {after!r} not found"
    rows.insert(i[0] + 1, row)
    out = io.StringIO(); w = csv.writer(out, lineterminator="\n"); w.writerows(rows)
    stage(p, out.getvalue())

def cite(p, key, col, old, new):
    def fn(v):
        assert old in v, f"{p.name} {key}.{col}: {old!r} absent"
        return v.replace(old, new)
    csv_set(p, key, col, fn)

# ------------------------------------------------------------------ DECISIONS.md
DEC = EB / "DECISIONS.md"

D278 = """**D-278 — The brake wake comes from its own plunger switch on the pedal, not from a second pole of the stop-lamp switch. Supersedes D-247.** From the 2026-09-05 parts sweep; applied to the data on 2026-09-08 under a number that was already spent (D-249 is A7 → oil pressure) and written into the record on the 2026-09-08f repair. D-247 (Camden, 2026-09-04, answering `Q-108`) made the brake a wake source: pole 1 of a two-circuit stop-lamp switch on the `A3` ladder as before, pole 2 fed from the F3 switch supply branched off `L3-S2 2` in the leg and returning on `L3-S1 7` to wake strip input 6 through a sixth 1N5819 — so a sleeping car that is pushed, rolled or towed still lights its brake lamps. The sweep found that the switch D-247 assumed does not exist in the shape it needs: the non-cruise FB switch is NLA, and the with-cruise switch that *is* in stock (`H003-66-490A`, $47) carries **NO + NC**, not two NO poles — it can drive the ladder or the wake strip, not both.

The fix costs nothing and removes the dependency: **a spare P084 adjustable plunger switch on the brake pedal** is the wake contact — the 6-pack is already carted and only three are needed for the doors — fed from the F3 switch supply branched off `L3-S2 2` and returning on **`L3-S1 7`** to wake strip input 6, exactly as D-247 drew the conductor. The stop-lamp switch reverts to *any* 2-terminal part (P085), which is what the aftermarket sells. Nothing at the harness changes; `L3-S1 7`, `N63` and the sixth diode stay.

The failure mode falls the right way: a dead plunger costs the wake, not the brake lamps, because the lamps come from the real switch through `A3`. If a plunger will not mount cleanly at the pedal, the alternative is an optocoupler at the node driven by the wake line, pulling the `A3` 4.7 kΩ leg — also zero conductors.

"""

D279 = """**D-279 — Protection is configured as two decisions, not one, and the policy differs by fault type.** From the 2026-09-08 benchmark against MoTeC, TI and Infineon practice; applied to `rules` and the templates on 2026-09-08 under a spent number and written here on the 2026-09-08f repair. Four refinements to D-164 / D-165 / D-175, all configuration — no wire and no part:

*Sizing.* The flat current threshold comes from the load (**~1.15× measured steady state**); the **time / I²t curve comes from the conductor**. MoTeC states that setting a limit near the device's own draw *"is unlikely to be effective"* at protecting the device — the limit exists to protect the wire. D-232 already ties gauge to limit; this ties the curve to the gauge.

*Inrush rides on the time dimension, never on the flat threshold.* Raising the threshold to stop nuisance trips buys a hole in the protection. For motors prefer a **stall timer** over a current trip — a wiper or a pop-up at stall is a thermal event, not a short.

*The motor factor goes from 1.10 to 1.25 on measured stall.* 1.10 is tighter than TI's 1.15 on *nominal*, applied to a stall figure that rises with age and with falling voltage. The consequence config cannot fix: **O1 is already at the 25 A channel ceiling against a measured 26 A both-sides stall** (LD08), so the pop-up bus has no headroom and leans on the D-186 obstruction timeout instead. O8 / O9 are held at 13.0 A by the DT contact rating (D-223), so this factor changes no existing number — it governs every figure measured from here on.

*Retry and latch are split by fault type* (`rules` retry): a hard overcurrent gets bounded fast retries, then a latch, then a flag; open-load and thermal never latch; and **no safety channel latches silently** — a latched stop lamp or headlamp must annunciate, because a latched-off headlamp at night is worse than a flickering one.

*Bulb-out annunciation on O2, O3 and O7.* Per-channel undercurrent against an expected window says a stop or headlight bulb is dead. On ECUMaster undercurrent raises a fault flag and **does not disable the output**, which is exactly right — it is an annunciator, not protection, and no logic may be built on it. This is the affordable answer to both brake lamps sharing O7, since there is no spare 15 A channel to segment into (§0 G1 carries the rows).

"""

D280 = """**D-280 — The sleeping current is a budget and an acceptance test, not an assumption.** From the 2026-09-08 benchmark; applied to `loads` LD17 and install 3.11 on 2026-09-08 under a spent number and written here on the 2026-09-08f repair. LD17 assumed *PMU 150 mA, nothing else*. A bench measurement of an ECUMaster PMU reports **under 20 mA**, and ECUMaster publishes no sleep-current specification at all. On the 40 Ah pack that is the difference between roughly **11 days and 80 days** of parking before the BMS cuts off — and a LiFePO4 gives no slow-crank warning: it is fine, and then it is completely dead, sometimes needing a charger to wake the BMS.

**Measure total sleeping current at the dash node before the dash closes** (install 3.11). Target **≤ 30 mA**, accept **≤ 50 mA** — BMW's own closed-circuit figures for the E65, which logs anything above 80 mA as a violation. Budget the wake strip explicitly: the two NPN sense stages and the bleed resistor are each a permanent path, and no published figure exists for a stage of this design.

Already correct and worth not breaking: every CAN2 drop is fed from **O10**, which de-energises in sleep. Bus traffic is what prevents standby on every PDM in the reference set, and CAN keypads are named specifically — the accessory-bus feed closed that hole before it opened.

"""

D281 = """**D-281 — The factory ignition noise-suppression condenser is reproduced on the O12 branch at the coil bracket (P135).** From the 2026-09-08 benchmark; written on the 2026-09-08f repair (the 2026-09-08 script meant to add the part as P099, a number the Deutsch kits already held, so no part existed until now). The 1982 diagram carries a condenser (B-22) on the igniter and coil `BW` supply. Mazda fitted it because the leading and trailing igniters put measurable hash on the ignition bus — and this harness runs CAN2 and eight analog resistor ladders past those coils, which the factory one did not. Fit it on the `L1-P 1` branch at the coil bracket (install 3.7), or delete it only against a measurement showing it is unnecessary. Deleting it silently is the fault that gets misdiagnosed as a bad ladder six months later.

"""

D282 = """**D-282 — Two details that must not quietly drift.** Both surfaced in the 2026-09-08 benchmark as load-bearing with no obvious owner; written on the 2026-09-08f repair.

*F20's ignition feed is a requirement, not a convenience.* The wideband gauge (D-244) sits on O12 because **an un-powered oxygen sensor is quickly damaged if the engine runs with the sensor in the exhaust**. It must be live whenever the engine can run. Nobody may move it to the accessory bus.

*Field recovery from a dead output runs through the 25 A class only.* O13 / O14 (the swap's reserve) and O15 (comfort) are unallocated; **there is no spare 15 A or 7 A output**. A failed 15 A or 7 A channel therefore moves to a 25 A output with its enable-at re-set — the wire is unchanged and the 25 A channel is the more capable one. Written here because the alternative is working it out at the roadside (`Q-139` decides the limp-home strategy around it).

"""

swap(DEC, "\n---\n\n## 5 · Switches, ladders and inputs", "\n" + D279.rstrip("\n") + "\n\n" + D280.rstrip("\n") + "\n\n" + D282.rstrip("\n") + "\n\n---\n\n## 5 · Switches, ladders and inputs")
swap(DEC, "\n---\n\n## 6 · Legs, connectors and grounds", "\n" + D278.rstrip("\n") + "\n\n---\n\n## 6 · Legs, connectors and grounds")
swap(DEC, "\n---\n\n## 7 · Wire, labels and materials", "\n" + D281.rstrip("\n") + "\n\n---\n\n## 7 · Wire, labels and materials")
swap(DEC, "**D-277 the cart dialed; the Deutsch kits are data** (2026-09-08e).",
          "**D-277 the cart dialed; the Deutsch kits are data** (2026-09-08e) · **D-278 the brake wake is a plunger switch on the pedal (supersedes D-247) · D-279 protection is two decisions, retry by fault type · D-280 the sleeping current is an acceptance test · D-281 the ignition condenser stays (P135) · D-282 F20 is load-bearing; recovery runs through the 25 A class** (2026-09-08f).")

# ------------------------------------------------------------------ QUESTIONS.md
QUE = EB / "QUESTIONS.md"
q = rd(QUE)
# A1 — delete the duplicate open Q-112 packet
i = q.index("**Q-112 - The blower's speed control depends on two parts that no longer exist.**")
j = q.index("**Q-113 - Alternator sense and phase conductors")
assert 0 < j - i < 2000
q = q[:i] + q[j:]
stage(QUE, q)
# A2 — renumber the six benchmark packets
for old, new in [("Q-116", "Q-134"), ("Q-117", "Q-135"), ("Q-118", "Q-136"), ("Q-119", "Q-137"), ("Q-120", "Q-138"), ("Q-121", "Q-139")]:
    s = pending[QUE]
    heads = [m.start() for m in re.finditer(r"^\*\*" + old + r" - ", s, re.M)]
    assert len(heads) == 1, f"{old}: {len(heads)} open packet headings"
    s = s[:heads[0]] + "**" + new + " - " + s[heads[0] + len("**" + old + " - "):]
    stage(QUE, s)
swap(QUE, "Pair with `Q-119`.", "Pair with `Q-137`.")
swap(QUE, "Field recovery from a *single* dead output is separate and already possible (D-253).",
          "Field recovery from a *single* dead output is separate and already possible (D-282).")
# A3 / §0 — the audit is applied; A2 cite; A7 rewrite; C1 pin counts
swap(QUE, "the wake contact is a spare P084 plunger on the pedal instead (D-249).",
          "the wake contact is a spare P084 plunger on the pedal instead (D-278).")
a7_old_start = q.index("- [ ] **A7 · Apply the 2026-09-05 future-proofing audit**")
a7_old_end = q.index("\n", a7_old_start)
A7 = ("- [x] **A7 · The 2026-09-05 future-proofing audit and the 2026-09-08 benchmark are applied** (2026-09-08f). Their rulings: blower → D-253 · road speed → D-272 · the brake wake → D-278 (supersedes D-247) · protection policy → D-279 · sleeping-current test → D-280 · the ignition condenser → D-281 (P135, to add) · F20 and the recovery path → D-282. Their open packets: `Q-113`, `Q-114`, `Q-134`–`Q-139` in §1 and `Q-115` in §2a. Their spares list is the car's, not the carts': a used ignition switch, a used pop-up motor pair, and a used wiper motor if one surfaces cheap — all NLA new, all single points of failure; nothing in the harness depends on them.")
s = pending[QUE]; s = s.replace(q[a7_old_start:a7_old_end], A7, 1); assert A7 in s; stage(QUE, s)
swap(QUE, "M-6 cluster plug — and the gauge type, `Q-123` · M-7 photographs.",
          "M-6 cluster plug — and the gauge type, `Q-123` · M-7 photographs · **count the pins** on the wiper motor, both pop-up motors and the fuel sender while they are visible — every one is a used-only purchase, and the removed part is the buying spec.")
# §1 intro
old_intro_start = q.index("One desk check and three items.")
old_intro_end = q.index("\n", old_intro_start)
INTRO = ("One desk check and nine items. `T-017` has to be done before the design freezes. `Q-113`, `Q-114` and `Q-134`–`Q-139` come from the 2026-09-05 and 2026-09-08 sweeps; each carries a recommendation and wants one word — only `Q-137` (a switch part number, P049) and `Q-138` (a fuse rating, P052) touch a cart. `Q-128` wants a source and the nRF Connect look. `Q-133` is answered and waits for its answer cycle.")
s = pending[QUE]; s = s.replace(q[old_intro_start:old_intro_end], INTRO, 1); assert INTRO in s; stage(QUE, s)
# Q-110 and the §3 row
swap(QUE, "Horn, hazard, wink — and now the brake (D-247) — all work with the key out",
          "Horn, hazard, wink — and now the brake (D-247 → D-278) — all work with the key out")
swap(QUE, "| `Q-108` | D-247 | **Two-circuit brake switch**; pole 2 → `L3-S1 7` → wake strip input 6. A pushed or towed car lights its brake lamps |",
          "| `Q-108` | D-247 → D-278 | **The brake wakes the module** — pole 2 → `L3-S1 7` → wake strip input 6 as ruled; the contact became a plunger switch on the pedal when the two-circuit part proved NLA (D-278). A pushed or towed car lights its brake lamps |")
# the banner the script edited (2026-09-04b) restored to what it said; a new banner for the repair
swap(QUE, "**Ten questions are left before shopping** — `Q-107` and `Q-111`, plus `Q-112` … `Q-114` and `Q-116` … `Q-121` from the 2026-09-05 and 09-08 sweeps — and one desk check, `T-017`.",
          "**Two questions are left before shopping — `Q-107` and `Q-111`** — and one desk check, `T-017`.")
BANNER = ("> **2026-09-08f.** Repair. The 2026-09-08 apply script (written from the Claude-Project PENDING docs) reused D-249–D-253 and Q-112, Q-116–Q-121 — numbers this file had already spent. Fixed: the duplicate `Q-112` packet removed (ruled → D-253); the six benchmark packets renumbered `Q-134`–`Q-139`; the plunger ruling written as **D-278** (supersedes D-247) and the four benchmark rulings as **D-279**–**D-282**; every data cell and template that cited the wrong number re-pointed; the condenser part added as P135. Both PENDING docs are applied and deleted. Next question Q-140, next decision D-283 — see `PROPOSAL-system-v2.md` §5 step 0.\n\n")
swap(QUE, "> **2026-09-08e.**", BANNER + "> **2026-09-08e.**")

# ------------------------------------------------------------------ data
D = EB / "data"
cite(D / "cavities.csv", "L3-S1 7", "lands_on", "(D-249)", "(D-278)")
cite(D / "devices.csv", "DV25", "terminals", "(D-249)", "(D-278)")
cite(D / "parts.csv", "P085", "used_for", "(D-249)", "(D-278)")
csv_set(D / "parts.csv", "P084", "used_for", lambda v: "Door jambs ×2, glove box, luggage, the brake-pedal wake contact (D-278) + 1 spare")
csv_add_after(D / "rules.csv", "voltage",
    ["retry", "Retry and latch",
     "Split by fault type (D-279). Hard overcurrent: bounded fast retries, then latch, then flag. Open-load or thermal: no latch. NEVER a silent latch on a safety channel — a latched stop lamp or headlamp must annunciate, because a latched-off headlamp at night is worse than a flickering one. Motors trip on a stall timer, not a current spike"])
cite(D / "loads.csv", "LD17", "basis", "D-251:", "D-280:")
csv_set(D / "node_conductors.csv", "N63", "note", lambda v: "Brake wake — a spare P084 plunger switch on the pedal, fed from the F3 switch supply, wakes the module (D-278)")
cite(D / "pins.csv", "7", "circuit", "brake (D-247)", "brake (D-278)")
csv_add_after(D / "parts.csv", "P074",
    ["P135", "Amazon", "Dash node and electronics", "", "Ignition noise-suppression capacitor, automotive, ~0.47 µF 250 V, ring-lug case",
     "Reproduces the factory condenser B-22 on the coil / igniter supply", "2", "ea", "10", "est",
     "O12 branch at the coil bracket (L1-P 1) — this harness runs CAN2 and eight analog ladders past the igniters (D-281)", "to add", "", ""])
csv_set(ROOT / "00-CAR" / "data" / "issues.csv", "K-022", "status",
        lambda v: v + ". A genuine pump is in stock (~$48, 2026-09-05 sweep) — replacement closes it if the diagnosis lands on the pump")

# ------------------------------------------------------------------ templates
T = EB / "templates"
swap(T / "PMU-CONFIG-SHEET.md", "**brake** (D-247)", "**brake** (D-278)")
swap(T / "PMU-CONFIG-SHEET.md", "**Sizing is two decisions** (D-250)", "**Sizing is two decisions** (D-279)")
swap(T / "INSTALL.md", "the ignition suppression condenser P099 on the L1-P 1 branch at the coil bracket (D-252)",
                       "the ignition suppression condenser P135 on the L1-P 1 branch at the coil bracket (D-281)")
swap(T / "INSTALL.md", "**Sleeping-current acceptance test** (D-251)", "**Sleeping-current acceptance test** (D-280)")
swap(T / "DESIGN.md", "rather than on a raised threshold (D-250)", "rather than on a raised threshold (D-279)")
swap(T / "DESIGN.md", "Motors: measured stall × 1.25 (D-250)", "Motors: measured stall × 1.25 (D-279)")
swap(T / "DESIGN.md", "**a dedicated plunger switch on the brake pedal** (D-249, so", "**a dedicated plunger switch on the brake pedal** (D-278, so")
swap(T / "README.md", "**Next IDs:** decisions from D-278 · questions from Q-134 (Q-113–Q-115 are reserved by the 2026-09-05 future-proofing audit).",
                      "**Next IDs:** decisions from D-283 · questions from Q-140.")

# ------------------------------------------------------------------ root
CL = ROOT / "CLAUDE.md"
swap(CL, "Electrical questions from **Q-134** (Q-113–Q-115 are reserved by the unapplied 2026-09-05 future-proofing audit, queued in the Claude Project as `rx7/PENDING-2026-09-05-futureproofing.md`), luxury from **Q-311**.",
         "Electrical questions from **Q-140**, luxury from **Q-311**.")
swap(CL, "electrical decisions continue from **D-278**", "electrical decisions continue from **D-283**")
swap(CL, "- The attached Claude Project (`rx7/…`) holds a flattened snapshot of the dissolved `electrical-pmu` tree from 2026-08-31 / 09-01. Its `SOURCE-OF-TRUTH.md` says so. **Do not answer from it — read this tree.**",
         "- The attached Claude Project (`rx7/…`) holds a flattened snapshot of the dissolved `electrical-pmu` tree from 2026-08-31 / 09-01 and is being emptied (`PROPOSAL-system-v2.md` §5 step 10). **Do not answer from it, and never queue work there — read this tree.** The 2026-09-08 apply script that was queued there collided with this tree's numbering; the repair is logged in the electrical `QUESTIONS.md` banner 2026-09-08f and the script is in `99-ARCHIVE/2026-09-08_apply-script/`.")

AR = ROOT / "99-ARCHIVE" / "README.md"
swap(AR, "| [`2026-08_superseded-C1-C7-connector-scheme.md`]",
         "| [`2026-09-08_apply-script/`](Electrical/../2026-09-08_apply-script/) | `apply-rx7-changes.py` — the chat-authored script that carried the 2026-09-05 and 2026-09-08 sweeps into the tree while the device bridge was down; it reused spent IDs and its `patch()` skipped silently on them | The 2026-09-08f repair (electrical `QUESTIONS.md` banner); the rulings it meant to write are D-278–D-282 |\n| [`2026-08_superseded-C1-C7-connector-scheme.md`]")
ARD = ROOT / "99-ARCHIVE" / "2026-09-08_apply-script" / "README.md"
stage(ARD, """# 2026-09-08 apply script — archived

*Rev 2026-09-08 · owns: what `apply-rx7-changes.py` did and did not do. History; nothing here is current.*

Written in chat on 2026-09-05 / 2026-09-08 while the device bridge was down, numbered from the Claude Project's `SOURCE-OF-TRUTH.md` (D-249 / Q-112), and run on 2026-09-08 against a tree that had already spent D-249–D-253 and Q-112, Q-116–Q-121.

**What landed:** the data edits (`parts` P085, `devices` DV25, `cavities` L3-S1 7, `loads` LD17, `rules` retry), the question packets Q-112–Q-121 and luxury Q-303, the template edits (×1.25 motor factor, the plunger sentence, install 3.7 / 3.11, PMU-CONFIG §5), the removal of D-247, and the `Latest` line.

**What did not:** the five decisions (its `patch()` saw `**D-249` … `**D-253` already present and skipped), and the condenser part (`P099` already existed).

**Repair (2026-09-08f):** the plunger ruling written as D-278, the benchmark rulings as D-279–D-282, the six benchmark packets renumbered Q-134–Q-139, the duplicate Q-112 removed, every cite re-pointed, the condenser added as P135. Never run this script again; it stays for the reasoning in its docstrings.
""")

# ------------------------------------------------------------------ write
for p, s in pending.items():
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8", newline="\n")
    print("wrote", p.relative_to(ROOT))

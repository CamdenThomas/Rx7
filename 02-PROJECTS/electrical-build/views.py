"""electrical-build — named views and checks for tools/rx7.py.

Every view is  fn(db, arg) -> markdown string.  A template line `{{name}}` or
`{{name:arg}}` is replaced by the view's output.  Every check is
fn(db) -> list[str] of problems; a non-empty list refuses the build.

Derived facts live here, not in the CSVs: a pin's "Goes to", a housing's
"Used" count, a cavity's label, the Deutsch kit quantities, ADC centres,
totals, counts.  If a fact can be computed from other rows, it is.
"""
import re
from collections import OrderedDict, defaultdict

T = lambda h, r: rx7.md_table(h, r)  # noqa: E731  (rx7 is injected by the loader)

# ------------------------------------------------------------------ small helpers

def dash(v):
    return v if v not in ("", None) else "—"


def pin_of(db, ch):
    r = db.get("pins", f"ch={ch}") if ch else None
    return r["pin"] if r else ""


def fuse(db, fid):
    return db.get("fuses", fid)


def relay(db, rid):
    return db.get("relays", rid)


def housing(db, code):
    return db.get("housings", code)


def cav_rows(db, code):
    return db.rows("cavities", 'housing = ?', code)


TERMINAL = {"L": "2.8 mm large 211CC3S3120", "M": "2.8 mm 211CC3S2120", "S": "1.5 mm 211CC2S2160P", "stud": "stud"}
KIT = {  # housing type -> DeutschConnector kit part number
    "DT06-12S": "12SA-201-16141", "DT04-12P": "12PA-202-16141", "DT06-8S": "8SA-201-16141", "DT04-8P": "8PA-202-16141",
    "DT06-08S": "8SA-201-16141", "DT04-08P": "8PA-202-16141", "DT06-6S": "6SA-201-16141", "DT04-6P": "6PA-202-16141",
    "DT06-4S": "4SA-201-16141", "DT04-4P": "4PA-202-16141", "DT06-2S": "2SA-201-16141", "DT04-2P": "2PA-202-16141",
    "DTP06-4S": "P4S-203-12141", "DTP04-4P": "P4P-204-12141", "DTP06-2S": "P2S-203-12141", "DTP04-2P": "P2P-204-12141"}


def src_parts(src):
    """'L1-S2 1 + L3-S2 11' -> ['L1-S2 1', 'L3-S2 11']"""
    return [s.strip() for s in src.split("+") if s.strip()]


def is_cavity_ref(tok):
    return bool(re.fullmatch(r"(L\d-[PMS]\d?|D[12]|DP-[A-Z]+) \d+", tok))


def reverse_links(db, cav_id):
    """Cavities whose src names this cavity (a link through the dash post)."""
    out = []
    for r in db.rows("cavities"):
        if any(p == cav_id for p in src_parts(r["src"])):
            out.append(r)
    return out


def taps(db, cav_id):
    return [r for r in db.rows("cavities") if r["src"] == f"tap {cav_id}"]


def pin_taps(db, cav_id):
    return [p for p in db.rows("pins") if p["note"] == f"tap {cav_id}"]


def src_text(db, c):
    """The 'From (box side)' cell of a cavity, from its structured source."""
    s, note, state = c["src"], c["src_note"], c["state"]
    h = housing(db, c["housing"])
    if state == "PLUG":
        return "—"
    if s == "":
        links = reverse_links(db, c["id"])
        if links:
            tgt = links[0]["id"]
            extras = []
            if tgt.startswith("DP-"):
                extras.append("post splice")
            for t in taps(db, c["id"]) + [t for l in links for t in taps(db, l["id"])]:
                extras.append(f"{t['id']} tap{' capped' if t['state'] == 'CAPPED' else ''}")
            for p in pin_taps(db, c["id"]):
                extras.append(f"{p['ch']} tap")
            txt = "→ " + " + ".join(l["id"] for l in links)
            return txt + (f" ({'; '.join(extras)})" if extras else "")
        return "capped at the sill" if h and h["where"] == "Sill node" else "capped at the post"
    m = re.fullmatch(r"(O\d+)", s)
    if m:
        return f"{s} (pin {pin_of(db, s)})" + (" splice" if note == "splice" else (f", {note}" if note else ""))
    m = re.fullmatch(r"(A\d+)", s)
    if m:
        return f"{s} (pin {pin_of(db, s)})" + (f", {note}" if note else "")
    if re.fullmatch(r"CAN[12][HL]", s):
        return f"{s} (pin {pin_of(db, s)})"
    m = re.fullmatch(r"(F\d+)", s)
    if m:
        f = fuse(db, s)
        if not f:
            return s + " (?)"
        if f["state"] == "EMPTY":
            return f"{s} at the sill (labelled position, no holder)"
        fed = f["fed_from"].split()[0] if f["fed_from"] else ""
        arrow = f" ← {fed}" if fed and fed[0] in "OK" else ""
        return f"{s} ({f['rating']})" + arrow
    m = re.fullmatch(r"(K\d+) (87|85)", s)
    if m:
        k = relay(db, m.group(1))
        if m.group(2) == "87":
            feed = k["c30"].split()[0] if k and k["c30"] else "?"
            return f"{s} ← {feed}"
        return f"{s} (coil return)"
    m = re.fullmatch(r"WAKE (\d)", s)
    if m:
        return f"Wake strip input {m.group(1)}"
    if s == "GND":
        return "DP-GND"
    if s == "SILL-GND":
        return "Sill ground stud"
    if re.fullmatch(r"K\d/K\d", s):
        return f"{s} at the sill (empty socket)"
    m = re.fullmatch(r"tap (.+)", s)
    if m:
        return f"tap on {m.group(1)}" + (" node" if m.group(1).startswith("DP-") else "")
    if all(is_cavity_ref(p) for p in src_parts(s)):
        return "← " + s + (f" ({note})" if note else "")
    return s


def label_token(db, c):
    """What the dash-node end of a wire is labelled with (install plan, Appendix A)."""
    s = c["src"]
    if c["state"] == "PLUG":
        return ""
    if s == "":
        links = reverse_links(db, c["id"])
        return links[0]["housing"] if links else "SPARE"
    if re.fullmatch(r"K\d+ \d+a?", s):
        return s.replace(" ", "-")
    if s.startswith("WAKE"):
        return "WAKE"
    if s.startswith("tap "):
        return "TAP"
    if all(is_cavity_ref(p) for p in src_parts(s)):
        return src_parts(s)[0].split()[0]
    return s


def goes_to(db, p):
    """A pin's destinations, derived from cavities, relays and fuses."""
    if p["goes_to_fixed"]:
        return p["goes_to_fixed"]
    ch = p["ch"]
    if not ch:
        return "—"
    legs, drops, fuses_, relays_ = [], [], [], []
    for c in db.rows("cavities"):
        if c["src"] == ch:
            item = c["id"] + (" (capped)" if c["state"] == "CAPPED" else "")
            (drops if c["housing"].startswith("DP-") else legs).append(item)
    splice_note = any(c["src"] == ch and "splice" in c["src_note"] for c in db.rows("cavities"))
    for k in db.rows("relays"):
        if k["c30"].split()[:1] == [ch]:
            relays_.append(f"{k['id']} 30")
    for k in db.rows("relays"):
        if k["c86"].split()[:1] == [ch]:
            relays_.append(f"{k['id']} 86")
    for f in db.rows("fuses"):
        if f["fed_from"].split()[:1] == [ch] and f["state"] != "EMPTY":
            fed = [c["id"] for c in db.rows("cavities") if c["src"] == f["id"]]
            fuses_.append(f"{f['id']} → {fed[0]}" if len(fed) == 1 else f["id"])
    items = legs + relays_ + fuses_ + drops
    txt = " · ".join(items) if items else "—"
    if splice_note and len(legs) > 1:
        txt += " (spliced at the post)"
    return txt


def enable_txt(p):
    if p["state"] == "CAPPED" or not p["enable_a"]:
        return "—"
    v = f"{p['enable_a']} {p['enable_basis']}"
    return f"**{v}**" if p["enable_basis"] == "meas" else v


def inrush_txt(p):
    return f"{p['inrush_x']}× {p['inrush_ms']} ms" if p["inrush_x"] else "—"


# ------------------------------------------------------------------ DESIGN views

def v_counts(db, arg):
    pins = db.rows("pins")
    outs = [p for p in pins if p["type"] == "output"]
    ins = [p for p in pins if p["type"] == "input"]
    by_rating = defaultdict(int)
    for p in outs:
        n = int(p["ch"][1:])
        by_rating["25 A" if n <= 5 or 12 <= n <= 16 else "15 A" if n <= 11 else "7 A"] += 1
    reserved = [p["ch"] for p in outs if p["state"] == "CAPPED"]
    hs = db.rows("housings")
    legs = sorted({h["leg"].split()[0] for h in hs if h["leg"].startswith("L")})
    n_leg = sum(1 for h in hs if h["where"] == "Dash post" and h["class"] in ("Power", "Medium", "Signal"))
    n_door = sum(1 for h in hs if h["class"] == "Door")
    n_drop = sum(1 for h in hs if h["code"].startswith("DP-"))
    rl = db.rows("relays")
    fitted = [k["id"] for k in rl if k["state"] == "LIVE" and k["location"] == "Dash node"]
    other = [k["id"] for k in rl if k["state"] == "LIVE" and k["location"] != "Dash node"]
    empty_dash = sum(1 for k in rl if k["state"] == "SPARE" and k["location"] == "Dash node")
    empty_sill = sum(1 for k in rl if k["state"] == "SPARE" and k["location"] != "Dash node")
    fz = db.rows("fuses")
    f_dash = sum(1 for f in fz if f["state"] == "LIVE" and f["location"].startswith("Dash node"))
    f_eng = sum(1 for f in fz if f["state"] == "LIVE" and f["location"].startswith("Engine"))
    f_empty = [f["id"] for f in fz if f["state"] == "EMPTY"]
    blocks = defaultdict(int)
    for f in fz:
        if f["block"]:
            blocks[f["block"]] += 1
    spare_pos = sum(4 - n for n in blocks.values())
    rows = [
        ["PMU outputs used", f"{len(outs)} of 22 ({' · '.join(f'{n} × {r}' for r, n in by_rating.items())}) — {' / '.join(reserved)} reserved for the swap, disabled"],
        ["PMU analog inputs used", f"{len(ins)} — " + ", ".join(p["ch"] for p in ins if int(p["ch"][1:]) <= 8) .replace(", ", "–", 0)[:0] + f"A1–A8 dedicated, {' / '.join(p['ch'] for p in ins if int(p['ch'][1:]) > 8)} on the shared 7 A pins"],
        ["Harness legs", f"{len(legs)} — " + " · ".join(f"{l.split()[0]} {l.split()[1].lower()}" for l in sorted({h['leg'] for h in hs if h['leg'].startswith('L') and '(' not in h['leg']})) + " (with the sill sub-node)"],
        ["Leg housings", f"{n_leg} (L1-S is two housings) + {n_door} door + {n_drop} dash-post drops + 2 lugs + the PMU connector = **{n_leg + n_door + n_drop + 3} mated pairs**"],
        ["Relays", f"{len(fitted)} fitted on the dash node ({' '.join(fitted)}) + {' '.join(other)} in the engine bay · {empty_dash + empty_sill} empty sockets ({empty_dash} dash node, {empty_sill} sill)"],
        ["Fuses", f"{f_dash} fitted at the dash node + {f_eng} in the engine bay + Class-T + MRBF · {len(f_empty)} labelled empty positions ({' '.join(f_empty)}) + {spare_pos} spare block positions"],
        ["Ground nodes", "5 — engine block · front · dash node · rear · sill"],
    ]
    return T(["Element", "Count"], rows)


def v_backbone(db, arg):
    return T(["Run", "Cable", "Protection", "Why"], [[r["run"], r["cable"], r["protection"], r["why"]] for r in db.rows("backbone")])


def v_fuses(db, arg):
    return T(["Fuse", "Rating", "Where", "Feeds", "Fed from", "State"],
             [[f["id"], dash(f["rating"]), f["location"], f["feeds"], f["fed_from"], f["state"]] for f in db.rows("fuses")])


def v_fuse_blocks(db, arg):
    src = {"A": "Always-hot busbar", "B": "K11 87 (head-unit constant)"}
    rows = []
    for blk in ("A", "B"):
        cells = ["spare"] * 4
        for f in db.rows("fuses", "block = ?", blk):
            p = int(f["pos"]) - 1
            cells[p] = f"{f['id']} {f['rating']}" if f["state"] == "LIVE" else f"{f['id']} (empty)"
        rows.append([f"Block {blk}", src[blk]] + cells)
    return T(["Block", "Input", "Position 1", "Position 2", "Position 3", "Position 4"], rows)


def v_pins(db, arg):
    rows = []
    for p in db.rows("pins"):
        rows.append([p["pin"], p["cav_size"], dash(p["ch"]), f"`{p['name']}`", p["awg"], p["colour"], p["circuit"],
                     goes_to(db, p), dash(p["est_a"]), enable_txt(p), inrush_txt(p), p["state"]])
    return T(["Pin", "Cav", "Ch", "Name", "AWG", "Colour", "Circuit", "Goes to", "Est A", "Enable at", "Inrush", "State"], rows)


def v_colours(db, arg):
    return T(["Colour", "Family", "Gauges"], [[f"**{c['id']}**", c["family"], c["gauges"]] for c in db.rows("colours")])


def v_colours_gloss(db, arg):
    return T(["Colour", "Family"], [[f"**{c['id']}**", c["family"]] for c in db.rows("colours")])


def v_relays(db, arg):
    rows = []
    for k in db.rows("relays"):
        coil = f"86 ← {k['c86']} · 85 → {k['c85']}" if k["c86"] else "—"
        con = f"30 ← {k['c30']} · 87 → {k['c87']}" + (f" · 87a → {k['c87a']}" if k["c87a"] else "") if k["c30"] else "—"
        rows.append([k["id"], k["function"], dash(k["type"]), k["location"], coil, con, k["state"]])
    return T(["Relay", "Function", "Type", "Where", "Coil", "Contacts", "State"], rows)


def v_node_conductors(db, arg):
    return T(["From", "To", "AWG", "Colour", "Note"], [[n["src"], n["dst"], n["awg"], n["colour"], n["note"]] for n in db.rows("node_conductors")])


def v_series(db, arg):
    return T(["Series", "Contact", "Wire", "Rated", "Used for"], [[f"Deutsch {s['id']}", s["contact"], s["wire"], s["rated"], s["used_for"]] for s in db.rows("series")])


def used_count(db, code):
    return sum(1 for c in cav_rows(db, code) if c["state"] != "PLUG")


def v_housings(db, arg):
    rows = [[h["code"], h["leg"], h["class"], h["leg_side"], h["box_side"], h["cavs"], str(used_count(db, h["code"])),
             h["wedgelocks"], h["where"], h["note"]] for h in db.rows("housings")]
    return T(["Code", "Leg", "Class", "Leg side", "Box side", "Cav", "Used", "Wedgelocks", "Where", "Note"], rows)


def v_cavities(db, code):
    h = housing(db, code)
    if not h:
        raise SystemExit(f"cavities: no housing {code!r}")
    out = []
    if h["class"] == "Door":
        out.append(f"**{code}**\n")
    elif not code.startswith("DP-"):
        out.append(f"**{code}** · {h['leg_side']} → {h['box_side']} · {h['cavs']} cavities · {h['note']}\n")
    if code.startswith("DP-") or h["class"] == "Door":
        hdr = ["Cav", "Circuit", "From", "AWG", "Colour", "State", "Cluster plug" if code == "DP-CLU" else "Lands on"]
    else:
        hdr = ["Cav", "Circuit", "From (box side)", "AWG", "Colour", "State", "Lands on (device end)"]
    rows = []
    for c in cav_rows(db, code):
        circuit = c["circuit"] if c["state"] != "PLUG" else "— empty"
        rows.append([c["cav"], circuit, src_text(db, c), dash(c["awg"]), dash(c["colour"]), c["state"], c["lands_on"]])
    out.append(T(hdr, rows))
    return "\n".join(out)


# --- ladders: ADC centres are computed from the resistor expressions

def parallel(rs):
    return 1 / sum(1 / r for r in rs)


def r_val(tok):
    tok = tok.strip().replace("Ω", "")
    m = re.fullmatch(r"([\d.]+)\s*([kM]?)", tok)
    if not m:
        return None
    v = float(m.group(1)) * {"": 1, "k": 1e3, "M": 1e6}[m.group(2)]
    return v


def adc_ground(expr):
    """10-bit, 10 kΩ pull-up to 5 V. '4.7k ∥ 12k' = parallel; '1.8k + 1N5819' = series diode."""
    diode = "1N5819" in expr
    expr = expr.replace("+ 1N5819", "").strip()
    rs = [r_val(t) for t in expr.split("∥")]
    if any(r is None for r in rs):
        return None
    R = parallel(rs)
    if diode:
        v = 0.3 + 4.7 * R / (R + 10000)
        return round(v / 5 * 1023)
    return round(1023 * R / (R + 10000))


def node_12v(expr):
    """12-bit 0–20 V input, 10 kΩ pull-down, 100 kΩ bias from 5 V; each live contact feeds 12 V through its resistor."""
    if expr.strip() == "bias only":
        rs = []
    else:
        rs = [r_val(t) for t in expr.split("+")]
        if any(r is None for r in rs):
            return None, None
    num = sum(12 / r for r in rs) + 5 / 100000
    den = sum(1 / r for r in rs) + 1 / 100000 + 1 / 10000
    v = num / den
    return v, round(v / 20 * 4095)


def v_ladder(db, a):
    inp = db.get("inputs", a)
    p = db.get("pins", f"ch={a}")
    out = [f"**{a} · {inp['title']}** — window ± {inp['window']} counts · {inp['fault_rule']}\n"]
    rows = []
    for l in db.rows("ladders", "input = ?", a):
        if inp["kind"] == "ground":
            rows.append([l["state"], l["r"], str(adc_ground(l["r"]))])
        else:
            v, adc = node_12v(l["r"])
            rows.append([l["state"], l["r"], f"{v:.2f}", str(adc)])
    hdr = ["State", "Resistance to ground", "ADC"] if inp["kind"] == "ground" else ["State", "Live contacts (series R from +12 V)", "Node V", "ADC"]
    out.append(T(hdr, rows))
    return "\n".join(out)


def v_decode(db, a):
    """PMU-CONFIG §1 — the same ladder with the fill-in columns."""
    inp = db.get("inputs", a)
    p = db.get("pins", f"ch={a}")
    if inp["kind"] == "ground":
        out = [f"**{a} `{p['name']}`** — window ± {inp['window']} · FAULT below 50 and above 990\n"]
        rows = [[l["state"], l["r"], str(adc_ground(l["r"])), "____", "____"] for l in db.rows("ladders", "input = ?", a)]
        rows += [["OPEN / unplugged", "∞", "1023", "", "FAULT"], ["SHORT / chafe", "0", "0", "", "FAULT"]]
        out.append(T(["State", "Resistance to ground (bench check)", "ADC centre", "Live reading", "Window entered"], rows))
    else:
        out = [f"**{a} `{p['name']}`** — window ± {inp['window']} · 0 = disconnected = FAULT\n"]
        rows = []
        for l in db.rows("ladders", "input = ?", a):
            v, adc = node_12v(l["r"])
            rows.append([l["state"], l["r"], f"{v:.2f}", str(adc), "____", "____"])
        out.append(T(["State", "Contacts live", "Node V", "ADC centre", "Live reading", "Window entered"], rows))
    return "\n".join(out)


def v_logic(db, arg):
    return T(["Channel", "Expression", "Inrush window" if arg != "config" else "Inrush", "Retry"],
             [[l["channel"], l["expression"], l["inrush"], l["retry"]] for l in db.rows("logic")])


def v_rules(db, arg):
    return T(["Rule", "Definition"], [[r["rule"], r["definition"]] for r in db.rows("rules")])


def v_grounds(db, arg):
    return T(["Zone", "Return", "AWG", "Qty", "ft each"], [[g["zone"], g["return"], g["awg"], g["qty"], g["ft"]] for g in db.rows("grounds")])


def v_loads(db, arg):
    rows = [[l["circuit"], l["ch"], l["rated"], l["design_a"], f"**{l['measured_a']}**" if l["measured_a"] else "—", l["basis"]]
            for l in db.rows("loads")]
    return T(["Circuit", "Ch", "Rated", "Design A", "Measured A", "Basis"], rows)


def v_devices(db, arg):
    rows = [[d["zone"], f"**{d['device']}**" + (f" — {d['ident']}" if d["ident"] else ""), d["terminals"], dash(d["ground"])] for d in db.rows("devices")]
    return T(["Zone", "Device", "Terminal → lands on", "Ground"], rows)


# ------------------------------------------------------------------ WIRE-TABLES views

def v_pmu_connector(db, arg):
    rows = []
    for p in sorted(db.rows("pins", "pin != 'STUD'"), key=lambda p: int(p["pin"])):
        rows.append([p["pin"], TERMINAL[p["cav_size"]], p["ch"] or p["name"], p["awg"], p["colour"], goes_to(db, p), "☐"])
    return T(["Cav", "Terminal", "Ch", "AWG", "Colour", "Goes to", "✔"], rows)


def v_node_conductors_check(db, arg):
    return T(["From", "To", "AWG", "Colour", "Note", "✔"], [[n["src"], n["dst"], n["awg"], n["colour"], n["note"], "☐"] for n in db.rows("node_conductors")])


CUT_GROUPS = {"L1": ["L1-P", "L1-S1", "L1-S2"], "L2": ["L2-P", "L2-M", "L2-S"], "L3": ["L3-P", "L3-M", "L3-S1", "L3-S2", "L3-S3"],
              "L4": ["L4-P", "L4-M", "L4-S"], "Sill": ["D1", "D2"], "Drops": ["DP-CLU", "DP-DIAG", "DP-ICU", "DP-DCU", "DP-KEY"]}


def v_cut_list(db, group):
    rows = []
    for code in CUT_GROUPS[group]:
        for c in cav_rows(db, code):
            cid = c["id"]; dashed = cid.replace(" ", "-")
            if c["state"] == "PLUG":
                rows.append([cid, "— plug", "—", "—", "PLUG", "—", "—", "—", "sealing plug", "☐"])
                continue
            tok = label_token(db, c)
            near = f"`{tok} / {dashed}`"
            far = f"`{dashed} / {'CAPPED' if c['state'] == 'CAPPED' else tok}`"
            rows.append([cid, c["circuit"], c["awg"], c["colour"], c["state"], near, far, "____", c["lands_on"], "☐"])
    return T(["Cavity", "Circuit", "AWG", "Colour", "State", "Label, dash-node end", "Label, far end", "Length", "Far end lands on", "✔"], rows)


def v_grounds_check(db, arg):
    return T(["Zone", "Return", "AWG BLK", "Qty", "≈ ft each", "✔"], [[g["zone"], g["return"], g["awg"], g["qty"], g["ft"], "☐"] for g in db.rows("grounds")])


def v_cables(db, arg):
    return T(["Run", "AWG", "≈ ft", "Colour", "✔"], [[c["run"], c["awg"], c["ft"], c["colour"], "☐"] for c in db.rows("cables")])


# ------------------------------------------------------------------ PMU-CONFIG views

def v_channel_names(db, arg):
    rows = [[p["pin"], dash(p["ch"]), f"`{p['name']}`", p["type"]] for p in sorted(db.rows("pins", "pin != 'STUD'"), key=lambda p: int(p["pin"]))]
    return T(["Pin", "Ch", "Name", "Type"], rows)


def v_enable_at(db, arg):
    rows = []
    for p in db.rows("pins", "type = 'output'"):
        if p["state"] == "CAPPED":
            rows.append([p["ch"], f"`{p['name']}`", "DISABLED", "—", "—"])
        else:
            rows.append([p["ch"], f"`{p['name']}`", enable_txt(p).strip("*"), inrush_txt(p) if p["inrush_x"] else "—", "____"])
    return T(["Ch", "Name", "Enable at (A)", "Inrush window", "Final limit"], rows)


# ------------------------------------------------------------------ INSTALL views

def v_plan_labels(db, arg):
    rows = []
    for k in db.rows("relays", "location = 'Dash node' AND state = 'LIVE'"):
        rows.append([k["id"], k["label"]])
    spare = [k["id"] for k in db.rows("relays", "location = 'Dash node' AND state = 'SPARE'")]
    if spare:
        rows.append([", ".join(spare), "SPARE"])
    sill = db.rows("relays", "location = 'Sill node'")
    if sill:
        rows.append([f"{sill[0]['id']}–{sill[-1]['id']} (sill)", " · ".join(k["label"] for k in sill)])
    for blk, src in (("A", "BUSBAR"), ("B", "K11")):
        cells = ["—"] * 4
        for f in db.rows("fuses", "block = ?", blk):
            cells[int(f["pos"]) - 1] = f"{f['id']} {f['label']} {f['rating'].replace(' ', '')}" if f["state"] == "LIVE" else f"{f['id']} —"
        rows.append([f"Block {blk}", f"{src}: " + " · ".join(cells)])
    inl = [f for f in db.rows("fuses") if "inline" in f["location"]]
    rows.append(["Inlines", " · ".join(f"{f['id']} {f['label']} {f['rating'].replace(' ', '')}" for f in inl)])
    eng = [f for f in db.rows("fuses") if f["location"].startswith("Engine bay")]
    rows.append(["Engine bay", " · ".join(f"{f['id']} {f['label']} {f['rating'].replace(' ', '')}" for f in eng)])
    sillf = [f for f in db.rows("fuses") if f["location"].startswith("Sill")]
    rows.append(["Sill", " · ".join(f"{f['id']} —" for f in sillf) + " (positions only, no holders)"])
    return T(["Position", "Label"], rows)


def v_migration_log(db, arg):
    rows = []
    for m in db.rows("migration"):
        en = "—"
        first = m["ch"].split(" / ")[0]
        p = db.get("pins", f"ch={first}")
        if p and p["type"] == "output":
            en = enable_txt(p).strip("*")
        rows.append([m["seq"], m["circuit"], m["ch"], en, "", "", "", "", "☐", "☐"])
    return T(["#", "Circuit", "Ch", "Enable at (A)", "Date", "Measured A", "Limit set", "V-drop", "Factory end labelled", "✔"], rows)


# ------------------------------------------------------------------ SHOPPING views

def money(v):
    return f"${v:,.2f}"


def need(db, rule):
    """Design-derived quantity for a shopping line."""
    cavs = db.rows("cavities")
    hs = db.rows("housings")
    if rule == "plugs16":
        return 2 * sum(1 for c in cavs if c["state"] == "PLUG" and housing(db, c["housing"])["class"] != "Power")
    if rule == "plugs12":
        return 2 * sum(1 for c in cavs if c["state"] == "PLUG" and housing(db, c["housing"])["class"] == "Power")
    if rule == "contacts14":
        return sum(1 for c in cavs if c["awg"] == "14" and housing(db, c["housing"])["class"] != "Power")
    if rule == "clips":
        return len(hs)
    return None


def param(db, key, default=0.0):
    r = db.get("params", key)
    return float(r["value"]) if r else default


def v_shopping_totals(db, arg):
    rows, total, nlines = [], 0.0, 0
    for c in db.rows("carts"):
        n = int(c["lines_txt"].split()[0])
        rows.append([c["store"], str(n), money(float(c["total_usd"]))]); total += float(c["total_usd"]); nlines += n
    rows.append(["**Four carts**", f"**{nlines}**", f"**{money(total)}**"])
    gaps = db.rows("parts", "status IN ('to add','raise')")
    veh = db.rows("parts", "store = 'Vehicle parts'")
    est = lambda rs: sum(float(p["unit_usd"]) * qty_num(p["qty"]) for p in rs if p["unit_usd"])
    rows.append(["Still to add (§8)", f"~{len(gaps) + 1}", f"≈ ${param(db, 'gaps_est_usd'):.0f}"])
    rows.append(["Vehicle parts, not yet carted (§6)", str(len(veh)), f"≈ {money(est(veh)).split('.')[0]} est"])
    rows.append(["Hardware store, after the measurement day (§7)", "—", f"≈ ${param(db, 'hardware_est_usd'):.0f} est"])
    grand = total + param(db, "gaps_est_usd") + est(veh) + param(db, "hardware_est_usd")
    rows.append(["**Everything**", "", f"**≈ ${round(grand, -1):,.0f}**"])
    return T(["Store", "Lines", "Cart total (2026-09-02)"], rows)


def qty_num(q):
    m = re.match(r"([\d.]+)", q.replace(",", ""))
    return float(m.group(1)) if m else 0.0


def v_total_all(db, arg):
    total = sum(float(c["total_usd"]) for c in db.rows("carts"))
    veh = sum(float(p["unit_usd"]) * qty_num(p["qty"]) for p in db.rows("parts", "store = 'Vehicle parts'") if p["unit_usd"])
    return f"${round(total + param(db, 'gaps_est_usd') + veh + param(db, 'hardware_est_usd'), -2):,.0f}"


def v_cart_line(db, store):
    c = db.get("carts", store)
    extra = f" ({c['note']})" if c["note"] else ""
    return f"{c['url']} · **cart {money(float(c['total_usd']))}, {c['lines_txt']}**{extra}"


def v_parts(db, arg):
    """{{parts:Store}} or {{parts:Store/Section}} — the cart lines of one store section."""
    store, _, section = arg.partition("/")
    rows = db.rows("parts", "store = ?", store)
    if section:
        rows = [p for p in rows if p["section"] == section]
    if store == "Waytek":
        return T(["Waytek #", "Item", "Qty", "Used for"], [[p["sku"], p["item"], p["qty"], p["used_for"]] for p in rows if p["status"] == "cart"])
    if store == "WireBarn":
        cart = [p for p in rows if p["status"] == "cart"]
        return T(["AWG", "Colour", "Feet", "Used for"], [[*p["item"].replace("GXL ", "").replace(" AWG", "").split(" "), p["qty"], p["used_for"]] for p in cart])
    if store == "Hardware store":
        return T(["Item", "Note"], [[p["item"], p["used_for"]] for p in rows])
    return T(["Item", "Spec", "Qty", "≈ $", "Note"], [[p["item"], p["spec"], p["qty"], p["unit_usd"], p["used_for"]] for p in rows])


def v_parts_to_add(db, store):
    rows = db.rows("parts", "store = ? AND status = 'to add'", store)
    if store == "WireBarn":
        return T(["AWG", "Colour", "Feet", "Used for", "Status"], [[*p["item"].replace("GXL ", "").replace(" AWG", "").split(" "), p["qty"], p["used_for"], "**to add**"] for p in rows])
    return T(["Item", "Qty", "Why"], [[p["item"], p["qty"], p["used_for"]] for p in rows])


def v_deutsch_kits(db, arg):
    plug, recep = OrderedDict(), OrderedDict()
    for h in db.rows("housings"):
        plug.setdefault(h["leg_side"], []).append(h["code"])
        recep.setdefault(h["box_side"], []).append(h["code"])
    order = ["DT06-12S", "DT06-8S", "DT06-6S", "DT06-4S", "DT06-2S", "DTP06-4S", "DTP06-2S"]
    rows = []
    for t in order:
        codes = plug.get(t, []) + (plug.get(t.replace("-8S", "-08S"), []) if "-8S" in t else [])
        if not codes:
            continue
        rt = t.replace("06", "04").replace("S", "P")
        rcodes = recep.get(rt, []) + (recep.get(rt.replace("-8P", "-08P"), []) if "-8P" in rt else [])
        rows.append([f"{KIT[t]} · {t} plug kit", str(len(codes)), " · ".join(codes)])
        rows.append([f"{KIT[rt]} · {rt} receptacle kit", str(len(rcodes)), f"same {NUM[len(rcodes)]}" if len(rcodes) > 1 else rcodes[0]])
    return T(["Kit", "Qty", "Housings served"], rows)


NUM = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}


def v_deutsch_contacts(db, arg):
    rows = []
    for p in db.rows("parts", "store = 'DeutschConnector.com'"):
        n = need(db, p["need_rule"]) if p["need_rule"] else None
        u = p["used_for"]
        if n is not None:
            need_txt = f"**{n}** {u}" if p["status"] == "raise" else f"{n} — {u}"
        else:
            need_txt = u
        st = {"cart": "cart", "raise": f"**raise to {p['target']}**", "to add": "**to add**"}.get(p["status"], p["status"])
        rows.append([p["sku"], p["item"], p["qty"], need_txt, st])
    return T(["Part", "Item", "Qty in cart", "Design needs", "Status"], rows)


def v_gaps(db, arg):
    rows = []
    for p in db.rows("parts", "status IN ('to add','raise')"):
        item = f"{p['sku']} {p['item']}" if p["sku"] else p["item"]
        qty = f"{p['qty']} → {p['target']}" if p["status"] == "raise" else p["qty"]
        rows.append([p["store"], item, qty, p["used_for"]])
    rows.append(["Drawer or local", "Blade fuses by value — §9", "", ""])
    return T(["Store", "Item", "Qty", "Why"], rows)


def v_blade_fuses(db, arg):
    by = OrderedDict()
    for f in db.rows("fuses"):
        if f["state"] == "LIVE" and re.fullmatch(r"[\d.]+ A", f["rating"]) and ("Dash node" in f["location"]):
            by.setdefault(f["rating"], []).append(f["id"])
    rows = []
    for rating, ids in sorted(by.items(), key=lambda kv: float(kv[0].split()[0])):
        pos = ", ".join(ids)
        extra = " + the first-power-up guard" if rating == "5 A" else ""
        rows.append([rating, pos + extra, str(len(ids) + 1 + (1 if extra else 0))])
    return T(["Value", "Positions", "Qty"], rows)


def v_n_housings(db, arg):
    return str(len(db.rows("housings")))


def v_arrival(db, arg):
    c = {p["sku"]: p for p in db.rows("parts", "store = 'DeutschConnector.com'")}
    g = lambda sku: (c[sku]["target"] or c[sku]["qty"]) if sku in c else "?"
    return (f"Contacts: {g('0462-209-16141')} of each 14 AWG type, {g('0462-201-16141')} of each 16–18 AWG type, "
            f"{g('0462-203-12141')} of each size 12, {need(db, 'plugs16')} size-16 plugs, {need(db, 'plugs12')} size-12 plugs, "
            f"{need(db, 'clips')} clips, 3 dust caps")


VIEWS = {
    "counts": v_counts, "backbone": v_backbone, "fuses": v_fuses, "fuse_blocks": v_fuse_blocks, "pins": v_pins,
    "colours": v_colours, "colours_gloss": v_colours_gloss, "relays": v_relays, "node_conductors": v_node_conductors,
    "series": v_series, "housings": v_housings, "cavities": v_cavities, "ladder": v_ladder, "decode": v_decode,
    "logic": v_logic, "rules": v_rules, "grounds": v_grounds, "loads": v_loads, "devices": v_devices,
    "pmu_connector": v_pmu_connector, "node_conductors_check": v_node_conductors_check, "cut_list": v_cut_list,
    "grounds_check": v_grounds_check, "cables": v_cables, "channel_names": v_channel_names, "enable_at": v_enable_at,
    "plan_labels": v_plan_labels, "migration_log": v_migration_log,
    "shopping_totals": v_shopping_totals, "total_all": v_total_all, "cart_line": v_cart_line, "parts": v_parts,
    "parts_to_add": v_parts_to_add, "deutsch_kits": v_deutsch_kits, "deutsch_contacts": v_deutsch_contacts,
    "gaps": v_gaps, "blade_fuses": v_blade_fuses, "n_housings": v_n_housings, "arrival": v_arrival,
}


# ------------------------------------------------------------------ checks (DESIGN §13, automated)

def c_pins(db):
    out = []
    pins = db.rows("pins")
    nums = [p["pin"] for p in pins if p["pin"] != "STUD"]
    if sorted(map(int, nums)) != list(range(1, 40)):
        out.append(f"pins: expected pins 1–39 exactly once, got {len(nums)}")
    chs = [p["ch"] for p in pins if p["ch"]]
    if len(chs) != len(set(chs)):
        out.append("pins: a channel is allocated twice")
    return out


def c_cavities(db):
    out = []
    ids = {c["id"] for c in db.rows("cavities")}
    for h in db.rows("housings"):
        rows = cav_rows(db, h["code"])
        if len(rows) != int(h["cavs"]):
            out.append(f"housings: {h['code']} declares {h['cavs']} cavities, cavities.csv has {len(rows)}")
        if [c["cav"] for c in rows] != [str(i) for i in range(1, len(rows) + 1)]:
            out.append(f"cavities: {h['code']} cavities are not 1..n in order")
    for c in db.rows("cavities"):
        if c["state"] == "PLUG":
            if c["src"] or c["awg"] or c["colour"]:
                out.append(f"cavities: {c['id']} is PLUG but carries a source/gauge/colour")
            continue
        if not c["awg"] or not c["colour"]:
            out.append(f"cavities: {c['id']} ({c['state']}) has no gauge or colour")
        if not c["lands_on"]:
            out.append(f"cavities: {c['id']} has no far end")
        for tok in src_parts(c["src"]):
            if is_cavity_ref(tok) and tok not in ids:
                out.append(f"cavities: {c['id']} source names unknown cavity {tok!r}")
            if tok.startswith("tap ") and tok[4:] not in ids:
                out.append(f"cavities: {c['id']} taps unknown cavity {tok[4:]!r}")
            if re.fullmatch(r"[OA]\d+|CAN[12][HL]", tok) and not db.get("pins", f"ch={tok}"):
                out.append(f"cavities: {c['id']} source names unknown channel {tok!r}")
            if re.fullmatch(r"F\d+", tok) and not fuse(db, tok):
                out.append(f"cavities: {c['id']} source names unknown fuse {tok!r}")
            m = re.fullmatch(r"(K\d+) \d+a?", tok)
            if m and not relay(db, m.group(1)):
                out.append(f"cavities: {c['id']} source names unknown relay {m.group(1)!r}")
        if c["state"] == "LIVE" and not c["src"] and not reverse_links(db, c["id"]):
            out.append(f"cavities: {c['id']} is LIVE with no source and nothing linking to it")
        # the wire must survive what its protection lets through: 16 AWG to 13 A,
        # 14 AWG to 15 A, 12 AWG above that.  A noted 'tap' rides on a heavier feed.
        m = re.fullmatch(r"O(\d+)", c["src"])
        if m and c["awg"] and "tap" not in c["src_note"]:
            p = db.get("pins", f"ch={c['src']}")
            awg = int(re.match(r"\d+", c["awg"]).group())
            n = int(m.group(1))
            limit = float(p["enable_a"]) if p and p["enable_a"] else (25 if (n <= 5 or 12 <= n <= 16) else 15 if n <= 11 else 7)
            need_awg = 12 if limit > 15 else 14 if limit > 13 else 16
            if awg > need_awg:
                out.append(f"cavities: {c['id']} is {awg} AWG behind a {limit:g} A limit on {c['src']} (needs {need_awg} AWG, or note it as a tap)")
    # every output channel lands somewhere
    for p in db.rows("pins", "type = 'output' AND state = 'LIVE'"):
        if goes_to(db, p) == "—":
            out.append(f"pins: {p['ch']} {p['name']} goes nowhere")
    return out


def c_fuses_relays(db):
    out = []
    for f in db.rows("fuses"):
        if f["state"] == "LIVE" and not (f["feeds"] and f["fed_from"]):
            out.append(f"fuses: {f['id']} is LIVE without a source or a load")
        if f["block"] and not f["pos"]:
            out.append(f"fuses: {f['id']} is in block {f['block']} with no position")
    seen = defaultdict(list)
    for f in db.rows("fuses"):
        if f["block"]:
            seen[(f["block"], f["pos"])].append(f["id"])
    for k, v in seen.items():
        if len(v) > 1:
            out.append(f"fuses: block {k[0]} position {k[1]} holds {v}")
    for k in db.rows("relays"):
        if k["state"] == "LIVE" and not all((k["c86"], k["c85"], k["c30"], k["c87"])):
            out.append(f"relays: {k['id']} is LIVE but a terminal (86/85/30/87) is unassigned")
    return out


def c_names(db):
    out = []
    names = {p["name"] for p in db.rows("pins")}
    for l in db.rows("logic"):
        for ch in re.split(r"\s*·\s*", l["channel"]):
            if ch not in names:
                out.append(f"logic: channel {ch!r} is not a pin name")
    for m in db.rows("migration"):
        for ch in re.split(r"\s*/\s*", m["ch"]):
            if re.fullmatch(r"[OA]\d+", ch) and not db.get("pins", f"ch={ch}"):
                out.append(f"migration: {m['id']} names unknown channel {ch}")
            if re.fullmatch(r"F\d+", ch) and not fuse(db, ch):
                out.append(f"migration: {m['id']} names deleted fuse {ch}")
            if re.fullmatch(r"K\d+", ch) and not relay(db, ch):
                out.append(f"migration: {m['id']} names unknown relay {ch}")
    for l in db.rows("loads"):
        for ch in re.findall(r"\b[OA]\d+\b|\bF\d+\b|\bK\d+\b", l["ch"]):
            if ch.startswith(("O", "A")) and not db.get("pins", f"ch={ch}"):
                out.append(f"loads: {l['id']} names unknown channel {ch}")
            if ch.startswith("F") and not fuse(db, ch):
                out.append(f"loads: {l['id']} names deleted fuse {ch}")
    return out


def c_ladders(db):
    """Windows must not overlap, and every resistor named at a device must be in the ladder."""
    out = []
    for inp in db.rows("inputs"):
        rows = db.rows("ladders", "input = ?", inp["id"])
        centres = []
        for l in rows:
            v = adc_ground(l["r"]) if inp["kind"] == "ground" else node_12v(l["r"])[1]
            if v is None:
                out.append(f"ladders: cannot compute {l['id']} from {l['r']!r}")
            else:
                centres.append((v, l["state"]))
        w = int(inp["window"])
        centres.sort()
        for (a, sa), (b, sb) in zip(centres, centres[1:]):
            if b - a < 2 * w:
                out.append(f"ladders: {inp['id']} windows overlap — {sa} {a} and {sb} {b} are {b - a} apart, window ± {w}")
    # resistor values named in device terminations
    ladder_r = defaultdict(set)
    for l in db.rows("ladders"):
        for tok in re.split(r"∥|\+", l["r"]):
            tok = tok.strip()
            if re.fullmatch(r"[\d.]+k", tok):
                ladder_r[l["input"]].add(tok)
    cav_input = {}
    for c in db.rows("cavities"):
        if re.fullmatch(r"A\d+", c["src"]):
            cav_input[c["id"]] = c["src"]
    for d in db.rows("devices"):
        for r, cav in re.findall(r"([\d.]+) kΩ → (L\d-[PMS]\d? \d+)", d["terminals"]):
            inp = cav_input.get(cav)
            if inp and f"{r}k" not in ladder_r[inp]:
                out.append(f"devices: {d['device']} names {r} kΩ on {cav} ({inp}) but {inp}'s ladder has {sorted(ladder_r[inp])}")
    return out


def c_shopping(db):
    out = []
    for p in db.rows("parts"):
        if p["need_rule"]:
            n = need(db, p["need_rule"])
            q = qty_num(p["qty"])
            if n is not None and q < n and p["status"] == "cart":
                out.append(f"parts: {p['id']} {p['sku']} cart qty {q:g} is below the design's {n} — mark it 'raise' or raise it")
    stores = {c["store"] for c in db.rows("carts")}
    for p in db.rows("parts", "status IN ('cart','raise','to add')"):
        if p["store"] not in stores:
            out.append(f"parts: {p['id']} is in store {p['store']!r} which has no cart")
    return out


def c_ids_cited(db):
    """Anything named in prose or notes must exist: fuses, relays, cavities named in node conductors."""
    out = []
    ids = {c["id"] for c in db.rows("cavities")}
    for n in db.rows("node_conductors"):
        for cav in re.findall(r"(?:L\d-[PMS]\d?|DP-[A-Z]+) \d+", n["src"] + " " + n["dst"]):
            if cav not in ids:
                out.append(f"node_conductors: {n['id']} names unknown cavity {cav}")
        for f in re.findall(r"\bF\d+\b", n["src"] + " " + n["dst"]):
            if not fuse(db, f):
                out.append(f"node_conductors: {n['id']} names deleted fuse {f}")
    return out


def c_dangling(db):
    """Every fuse, relay, channel or cavity named in ANY text cell must exist —
    the check that catches a deleted part still mentioned in a note."""
    out = []
    ids = {c["id"] for c in db.rows("cavities")}
    fz = {f["id"] for f in db.rows("fuses")}
    kz = {k["id"] for k in db.rows("relays")}
    ch = {p["ch"] for p in db.rows("pins") if p["ch"]}
    pat = re.compile(r"\b(F\d{1,2}|K\d{1,2}|[OA]\d{1,2}|(?:L\d-[PMS]\d?|D[12]|DP-[A-Z]+) \d{1,2})\b")
    for t, cols in db.tables.items():
        for r in db.rows(t):
            for c in cols:
                for tok in pat.findall(str(r[c])):
                    if tok[0] == "F" and tok not in fz:
                        out.append(f"{t}:{r[cols[0]]} names fuse {tok}, which does not exist")
                    elif tok[0] == "K" and tok not in kz:
                        out.append(f"{t}:{r[cols[0]]} names relay {tok}, which does not exist")
                    elif tok[0] in "OA" and " " not in tok and tok not in ch:
                        out.append(f"{t}:{r[cols[0]]} names channel {tok}, which does not exist")
                    elif " " in tok and tok not in ids:
                        out.append(f"{t}:{r[cols[0]]} names cavity {tok}, which does not exist")
    return sorted(set(out))


CHECKS = [c_pins, c_cavities, c_fuses_relays, c_names, c_ladders, c_shopping, c_ids_cited, c_dangling]

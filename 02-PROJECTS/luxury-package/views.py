"""luxury-package — named views and checks for tools/rx7.py.

Every view is fn(db, arg) -> markdown; every check is fn(db) -> [problems].
What this file derives, and from where (R6):
  provisions  — joined LIVE to ../electrical-build/data (cavities, housings, pins, fuses, relays):
                the boundary table can never go stale, and c_provisions refuses the build if a
                cavity the luxury package counts on has changed state or vanished.
  CAN         — layouts, bus load, timeouts and the node table from can_messages / can_fields / modules;
                can_drift compares the map against firmware/icu/can_map.h and REPORTS (never refuses).
  channels.h  — firmware/pmu_sim/channels.h is rendered from the electrical pin table (D-311).
  money       — line and stage totals from parts.
"""
import hashlib, re
from pathlib import Path

T = lambda h, r: rx7.md_table(h, r)  # noqa: E731  (rx7 is injected by the loader)
HERE = Path(__file__).resolve().parent
EB = rx7.ROOT / "02-PROJECTS" / "electrical-build"
FW = HERE / "01-DESIGN" / "firmware"
_EDB = None


def edb():
    global _EDB
    if _EDB is None:
        _EDB = rx7.DB(EB)
    return _EDB


def dash(v):
    return v if v not in ("", None) else "—"


def stage_label(db, sid):
    r = db.get("stages", sid)
    return f"{sid} · {r['stage']}" if r else sid


def filt(rows, arg):
    """'col=value' filters; several separated by '|'."""
    for a in [a for a in arg.split("|") if "=" in a]:
        k, v = a.split("=", 1)
        rows = [r for r in rows if r.get(k.strip()) == v.strip()]
    return rows


# ------------------------------------------------------------------ the electrical join

def e_lookup(kind, ref):
    e = edb()
    if kind == "cavity":
        c = e.get("cavities", ref)
        return (c["circuit"] or "(sealing plug)", c["state"], c["lands_on"]) if c else None
    if kind == "housing":
        h = e.get("housings", ref)
        return (f"{h['leg_side']} / {h['box_side']}, {h['cavs']}-way", h["where"], h["note"]) if h else None
    if kind == "pin":
        r = e.get("pins", f"ch={ref}")
        return (f"{r['name']} — {r['circuit']}", r["state"], f"PMU pin {r['pin']}") if r else None
    if kind in ("fuse", "relay"):
        r = e.get("fuses" if kind == "fuse" else "relays", ref)
        if not r:
            return None
        cells = [f"{k}: {v}" for k, v in r.items() if k not in ("_n", "id") and v]
        return ("; ".join(cells[:3]), r.get("state", ""), "; ".join(cells[3:]))
    return None


def v_provisions(db, arg):
    rows = filt(db.rows("provisions"), arg)
    if "stage=" in arg:
        sid = [a.split("=", 1)[1] for a in arg.split("|") if a.startswith("stage=")][0]
        fts = {f["id"] for f in db.rows("features") if f["stage"] == sid}
        rows = [r for r in db.rows("provisions") if r["feature"] in fts]
    out = []
    for p in rows:
        got = e_lookup(p["kind"], p["ref"]) or ("**NOT IN THE ELECTRICAL DATA**", "?", "")
        f = db.get("features", p["feature"])
        out.append([f"`{p['ref']}`", p["kind"], got[0], got[1], p["role"], f"{p['feature']} {f['feature']}" if f else p["feature"]])
    return T(["Ref", "Kind", "The electrical build says", "State today", "This project's use", "Feature"], out)


def v_provision_counts(db, arg):
    rows = db.rows("provisions")
    by = {}
    for p in rows:
        by[p["kind"]] = by.get(p["kind"], 0) + 1
    return T(["Kind", "Count"], [[k, str(v)] for k, v in by.items()] + [["**total**", f"**{len(rows)}**"]])


# ------------------------------------------------------------------ modules, features, stages

def v_modules(db, arg):
    return T(["ID", "Module", "Board", "Where", "Logic power", "Heavy power", "Drops", "State", "Owns"],
             [[m["id"], m["module"], m["board"], m["location"], m["logic_power"], m["heavy_power"], m["drops"], m["state"], m["owns"]] for m in db.rows("modules")])


def v_features(db, arg):
    rows = filt(db.rows("features"), arg)
    return T(["ID", "Feature", "Group", "Stage", "State", "Decisions", "Note"],
             [[f["id"], f["feature"], f["group"], stage_label(db, f["stage"]) if f["stage"].startswith("S") else f["stage"], f["state"], f["decisions"], f["note"]] for f in rows])


def v_stages(db, arg):
    return T(["Stage", "What", "When", "Dash plastics", "Needs first", "Plugs into", "Outcome"],
             [[s["id"], s["stage"], s["when"], s["plastics"], s["prerequisites"], s["plugs_into"], s["outcome"]] for s in db.rows("stages")])


def v_stage_detail(db, sid):
    s = db.get("stages", sid)
    fts = [f for f in db.rows("features") if f["stage"] == sid]
    parts = [p for p in db.rows("parts") if p["stage"] == sid]
    lo, hi = money_sum(parts)
    lines = [f"**{s['id']} · {s['stage']}** — {s['when']}. Dash plastics: {s['plastics']}.", "",
             f"*Needs first:* {s['prerequisites']}  ", f"*Plugs into:* {s['plugs_into']}  ", f"*Outcome:* {s['outcome']}", ""]
    if fts:
        lines.append("Features: " + " · ".join(f"{f['id']} {f['feature']}" for f in fts))
        lines.append("")
    lines.append(f"Parts this stage: {len(parts)} lines, ~${lo:,.0f}–{hi:,.0f} (unpriced lines excluded)." if parts else "No parts lines yet.")
    return "\n".join(lines)


# ------------------------------------------------------------------ sensors

def v_sensors(db, arg):
    rows = filt(db.rows("sensors"), arg)
    return T(["ID", "Signal", "From", "What is on the wire", "Front end", "Pin", "Calibration", "CAN", "Note"],
             [[s["id"], s["signal"], s["source"], s["node"], s["front_end"], s["pin"], s["calibration"], s["can"], s["note"]] for s in rows])


# ------------------------------------------------------------------ CAN

RECEIVES = {  # who consumes what — a design fact kept here so the node table is one view (R6)
    "PMU": "ICU 0x200 / 0x218 and the AFR frame as logged telemetry only (electrical D-251); panel 0x400 for defog / hatch / fuel door",
    "ICU": "everything on the bus",
    "DCU": "ICU sensors, panel 0x400, PMU 0x100 for key state",
    "PANEL": "DCU 0x300 / 0x310 for key backlights",
    "WBO": "nothing",
}


def v_can_nodes(db, arg):
    msgs = db.rows("can_messages")
    out = []
    for m in db.rows("modules"):
        sends = ", ".join(x["id"] for x in msgs if x["sender"] == m["id"]) or "—"
        term = {"PMU": "**software, at the dash end**", "WBO": "—"}.get(m["id"], "—")
        out.append([m["module"], sends, RECEIVES.get(m["id"], "—"), term])
    out.append(["LS ECU (engine swap, future)", "0x500+", "—", "**physical 120 Ω at the engine-bay drop** (electrical D-079)"])
    return T(["Node", "Sends", "Receives", "Termination"], out)


def v_can_messages(db, arg):
    return T(["ID", "Message", "Sender", "Rate", "Timeout", "On timeout", "Status", "Note"],
             [[f"`{m['id']}`", m["name"], m["sender"], (m["rate_hz"] + " Hz") if m["rate_hz"].replace(".", "").isdigit() else dash(m["rate_hz"]),
               (m["timeout_ms"] + " ms") if m["timeout_ms"] else "—", m["on_timeout"], m["status"], m["note"]] for m in db.rows("can_messages")])


def v_can_layout(db, mid):
    rows = [f for f in db.rows("can_fields") if f["msg"] == mid]
    return T(["Byte", "Field", "Encoding", "Note"], [[f["bytes"], f["field"], f["encoding"], f["note"]] for f in rows])


def v_can_layouts(db, arg):
    out = []
    for m in db.rows("can_messages"):
        rate = (m["rate_hz"] + " Hz") if m["rate_hz"].replace(".", "").isdigit() else (m["rate_hz"] or "rate per AEM")
        out.append(f"### {m['id']} · {m['sender']} → all · {m['name']} · {rate}\n")
        if m["note"]:
            out.append(f"*{m['note']}*\n")
        out.append(v_can_layout(db, m["id"]) + "\n")
    return "\n".join(out)


def frame_bits(db, mid):
    key = "frame_bits_ext" if "ext" in mid else "frame_bits_std"
    p = db.get("params", key)
    return float(p["value"]) if p else 112.0


def v_can_busload(db, arg):
    out, total = [], 0.0
    for m in db.rows("can_messages"):
        if not m["rate_hz"].replace(".", "").isdigit():
            out.append([f"`{m['id']}`", "8", dash(m["rate_hz"]), "— (event or unknown rate, not counted)"])
            continue
        bps = float(m["rate_hz"]) * frame_bits(db, m["id"])
        total += bps
        out.append([f"`{m['id']}`", "8", m["rate_hz"], f"~{bps:,.0f}"])
    kbps = float(db.get("params", "can_bitrate")["value"])
    out.append(["**Total**", "", "", f"**~{total/1000:.1f} kbit/s — {100*total/(kbps*1000):.1f} % of {kbps:.0f} kbit/s**"])
    return T(["ID", "Bytes", "Hz", "bits/s"], out)


def v_can_timeouts(db, arg):
    return T(["Message", "Timeout", "Receiver does"], [[f"`{m['id']}`", (m["timeout_ms"] + " ms") if m["timeout_ms"] else "none", m["on_timeout"]] for m in db.rows("can_messages")])


def header_text():
    p = FW / "icu" / "can_map.h"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def v_can_drift(db, arg):
    """The map (data) against firmware/icu/can_map.h — reported, never refused (F-012 owns the fix)."""
    h = header_text()
    ids = {m.group(2).upper(): m.group(3).strip() for m in re.finditer(r"#define\s+ID_(\w+)\s+0x([0-9A-Fa-f]+)\s*/\*([^*]*)\*/", h)}
    rows = []
    for m in db.rows("can_messages"):
        if "ext" in m["id"]:
            rows.append([f"`{m['id']}`", "vendor frame, not in the header by design", "—", "n/a"])
            continue
        hexid = m["id"][2:].upper()
        if hexid not in ids:
            rows.append([f"`{m['id']}` {m['name']}", f"{m['rate_hz']} Hz", "**missing**", "**DRIFT**"])
            continue
        comment = ids[hexid]
        want = m["rate_hz"]
        ok = (want in comment) or (want == "on change" and "change" in comment)
        rows.append([f"`{m['id']}` {m['name']}", f"{want} Hz" if want.isdigit() else want, comment, "match" if ok else "**DRIFT**"])
    checks = [("0x120 bytes 0–1", "reserved (fuel moved)", "fuel_pct" not in h.split("pmu_outputs_t")[0].split("typedef struct")[-1] if "pmu_outputs_t" in h else True),
              ("0x300 byte 1", "blower duty %", "duty" in h),
              ("0x300 byte 5", "outside_c", "outside_c" in h),
              ("0x210 bit 5", "SENS_FUEL", "SENS_FUEL" in h),
              ("0x218 struct", "icu_body_t", "icu_body_t" in h)]
    for what, want, ok in checks:
        rows.append([what, want, "present" if ok else "**absent**", "match" if ok else "**DRIFT**"])
    n = sum(1 for r in rows if "DRIFT" in r[3])
    tail = f"\n\n**{n} drift item(s)** — the header is behind the map until F-012 lands. Nothing on the car depends on it yet." if n else "\n\n**No drift** — the header matches the map."
    return T(["Map says", "Value", "Header says", "State"], rows) + tail


# ------------------------------------------------------------------ money

def num(v):
    try:
        return float(str(v).replace(",", "").replace("$", ""))
    except ValueError:
        return None


def money_sum(rows):
    lo = sum(num(p["usd_low"]) or 0 for p in rows)
    hi = sum((num(p["usd_high"]) if num(p["usd_high"]) is not None else num(p["usd_low"])) or 0 for p in rows)
    return lo, hi


def v_parts(db, arg):
    rows = filt(db.rows("parts"), arg)
    return T(["ID", "Stage", "Item", "Spec", "Qty", "USD (line)", "Status", "Gate", "Note"],
             [[p["id"], p["stage"], p["item"], p["spec"], p["qty"], (f"{p['usd_low']}–{p['usd_high']}" if p["usd_high"] and p["usd_high"] != p["usd_low"] else dash(p["usd_low"])), p["status"], dash(p["gate"]), p["note"]] for p in rows])


def v_parts_totals(db, arg):
    out = []
    allp = db.rows("parts")
    for s in db.rows("stages"):
        rows = [p for p in allp if p["stage"] == s["id"]]
        lo, hi = money_sum(rows)
        unpriced = sum(1 for p in rows if num(p["usd_low"]) is None)
        out.append([f"{s['id']} · {s['stage']}", str(len(rows)), f"~${lo:,.0f}–{hi:,.0f}" + (f" + {unpriced} unpriced" if unpriced else "")])
    lo, hi = money_sum(allp)
    out.append(["**All stages**", f"**{len(allp)}**", f"**~${lo:,.0f}–{hi:,.0f}**"])
    return T(["Stage", "Lines", "Estimate"], out)


# ------------------------------------------------------------------ work, log, params, counts

def v_work_kind(db, arg):
    """{{work_kind:firmware}} — the work rows of one kind (block_title), as the bring-up record reads them."""
    rows = [w for w in db.rows("work") if w["block_title"] == arg.strip()]
    return T(["ID", "Item", "Owner", "State", "Gate", "Note"], [[w["id"], w["item"], w["owner"], w["state"], dash(w["gate"]), w["note"]] for w in rows])


def v_bringup_log(db, arg):
    return T(["Date", "Board", "Firmware", "Event"], [[r["date"], r["board"], r["firmware"], r["event"]] for r in db.rows("bringup_log")])


def v_params(db, arg):
    return T(["Key", "Value", "Unit", "Source", "Note"], [[p["key"], p["value"], p["unit"], p["source"], p["note"]] for p in db.rows("params")])


def v_counts(db, arg):
    f = db.rows("features"); st = {}
    for x in f:
        st[x["state"]] = st.get(x["state"], 0) + 1
    lo, hi = money_sum(db.rows("parts"))
    open_work = sum(1 for w in db.rows("work") if w["state"] in ("open", "blocked"))
    return T(["What", "Count"], [["Features", str(len(f))], ["— by state", " · ".join(f"{k} {v}" for k, v in sorted(st.items()))],
                                  ["Provisions consumed from the electrical build", str(len(db.rows("provisions")))],
                                  ["CAN messages / fields", f"{len(db.rows('can_messages'))} / {len(db.rows('can_fields'))}"],
                                  ["Sensor and output channels specified", str(len(db.rows("sensors")))],
                                  ["Parts lines / estimate", f"{len(db.rows('parts'))} / ~${lo:,.0f}–{hi:,.0f}"],
                                  ["Open work items (agent side)", str(open_work)]])


# ------------------------------------------------------------------ channels.h — rendered from the electrical pin table (D-311)

CH_ENUM = """/* Channel indices, so the model reads like the schedule rather than
 * like an array of magic numbers. O23/O24 are configured as inputs A15/A16. */
enum {
  O1_MOTOR, O2_HEAD_LO, O3_HEAD_HI, O4_DEFOG, O5_FUEL, O6_TAIL,
  O7_BRAKE, O8_WIPE_LO, O9_WIPE_HI, O10_ACC, O11_HORN, O12_IGN,
  O13_LS_ECU, O14_LS_FAN, O15_COMFORT, O16_BLOWER,
  O17_TURN_L, O18_TURN_R, O19_REVERSE, O20_INTERIOR,
  O21_START, O22_KEEPALIVE, O23_SPARE, O24_SPARE
};"""
RESERVED_LIMIT = {"O13": 1800, "O14": 2500}


def v_channels_h(db, arg):
    e = edb()
    pins = {p["ch"]: p for p in e.rows("pins")}
    lines = ["/*", " * channels.h — PMU channel table for the simulator", " *",
             " * ============================================================",
             " *  GENERATED by  python tools/rx7.py -p luxury-package build",
             " *  from 02-PROJECTS/electrical-build/data/pins.csv (est_a, enable_a,",
             " *  enable_basis, inrush_x, inrush_ms, state). Do not edit here: change",
             " *  the pin row in the electrical build and rebuild this project (D-311).",
             " * ============================================================", " *",
             " * Units: 0.01 A, matching CAN 0x130 and cluster_core.h.",
             " * inrush: multiplier x10 applied for inrushMs after switch-on.",
             " * limit:  the electrical build's enable-at value for the channel (its soft",
             " *         fuse — measured where enable_basis says so, else the cap). The real",
             " *         PMU output stays DISABLED until measured — this table only drives",
             " *         the simulator and the diagnostics page.", " */", "",
             "#ifndef CHANNELS_H", "#define CHANNELS_H", "", "#include <stdint.h>", "",
             "enum ChSrc : uint8_t { EST = 0, MEASURED = 1, DEAD = 2, RESERVED = 3 };", "",
             "struct ChannelSpec {", "    const char *name;", "    uint16_t    steady;      /* 0.01 A                        */",
             "    uint16_t    limit;       /* 0.01 A soft fuse, provisional */", "    uint8_t     inrushX10;   /* multiplier x10 -> 100 = 10.0x */",
             "    uint16_t    inrushMs;", "    ChSrc       src;", "};", "", "/* ---- O1..O24 ---- */",
             "static const ChannelSpec CH[24] = {", "/*  name            steady  limit  inX10   ms   source      */"]
    for n in range(1, 25):
        ch = f"O{n}"
        if n in (23, 24):
            a = "A15" if n == 23 else "A16"
            lines.append(f'  {{ "{a} IN",{"":13}0,    700,   10,    0, RESERVED }}, /* {a}  Occupies {ch} */')
            continue
        p = pins.get(ch)
        name = p["name"].replace("_", " ")
        est, en = num(p["est_a"]), num(p["enable_a"])
        ix, ims = num(p["inrush_x"]), num(p["inrush_ms"])
        if p["state"] == "CAPPED":
            src, steady, limit, ix, ims, cm = "RESERVED", 0, RESERVED_LIMIT.get(ch, 700), 1.0, 0, "electrical D-007"
        elif ch == "O16":
            src, steady, limit, cm = "DEAD", 0, int(round((en or 25) * 100)), "no motor until the luxury package (K-023, D-253)"
        elif p["enable_basis"] == "meas":
            src, steady, limit, cm = "MEASURED", int(round((est or 0) * 100)), int(round((en or 0) * 100)), "measured (electrical D-164/165)"
        else:
            src, steady, limit, cm = "EST", int(round((est or 0) * 100)), int(round((en or 20) * 100)), f"enable-at {en:g} A" if en else "no enable-at yet — 20 A placeholder"
        lines.append(f'  {{ "{name}",{" " * max(1, 18 - len(name))}{steady:5d}, {limit:6d}, {int(round((ix or 1) * 10)):4d}, {int(ims or 0):4d}, {src:<8} }}, /* {ch:<4} {cm} */')
    lines += ["};", "", CH_ENUM, "",
              "/* How many channel currents are still guesses. Printed at boot so the",
              " * number in front of you is never mistaken for measured data. */",
              "inline int estimatedChannelCount() {", "    int n = 0;",
              "    for (int i = 0; i < 24; i++) if (CH[i].src == EST) n++;", "    return n;", "}", "",
              "#endif /* CHANNELS_H */"]
    return "\n".join(lines)


VIEWS = {
    "modules": v_modules, "features": v_features, "stages": v_stages, "stage_detail": v_stage_detail,
    "provisions": v_provisions, "provision_counts": v_provision_counts, "sensors": v_sensors,
    "can_nodes": v_can_nodes, "can_messages": v_can_messages, "can_layout": v_can_layout, "can_layouts": v_can_layouts,
    "can_busload": v_can_busload, "can_timeouts": v_can_timeouts, "can_drift": v_can_drift,
    "parts": v_parts, "parts_totals": v_parts_totals, "work_kind": v_work_kind, "bringup_log": v_bringup_log,
    "params": v_params, "counts": v_counts, "channels_h": v_channels_h,
}

# ------------------------------------------------------------------ checks

CAV = re.compile(r"(L\d-(?:[PMS]\d?|BLW)|D[12]|DP-[A-Z]+(?:-[A-Z])?) \d+")


def c_provisions(db):
    out, feats = [], {f["id"] for f in db.rows("features")}
    for p in db.rows("provisions"):
        got = e_lookup(p["kind"], p["ref"])
        if got is None:
            out.append(f"provisions {p['id']}: {p['kind']} {p['ref']!r} is not in the electrical build's data — the boundary has moved")
            continue
        if p["expect"] and got[1] != p["expect"]:
            out.append(f"provisions {p['id']}: {p['ref']} is {got[1]} in the electrical data, this project expects {p['expect']}")
        if p["feature"] not in feats:
            out.append(f"provisions {p['id']}: feature {p['feature']} does not exist")
    return out


def c_features(db):
    out, stages = [], {s["id"] for s in db.rows("stages")}
    for f in db.rows("features"):
        if f["stage"] not in stages and f["stage"] not in ("—", "any"):
            out.append(f"features {f['id']}: stage {f['stage']!r} does not exist")
    return out


def c_sensors(db):
    out, mods = [], {m["id"] for m in db.rows("modules")}
    e = edb()
    for s in db.rows("sensors"):
        if s["module"] not in mods:
            out.append(f"sensors {s['id']}: module {s['module']} does not exist")
        m = CAV.search(s["source"])
        if m and not e.get("cavities", m.group(0)):
            out.append(f"sensors {s['id']}: source cavity {m.group(0)} is not in the electrical data")
    return out


def byte_range(b):
    b = b.replace("–", "-")
    if "-" in b:
        a, z = b.split("-", 1); return set(range(int(a), int(z) + 1))
    return {int(b)}


def c_can(db):
    out, msgs = [], {m["id"]: m for m in db.rows("can_messages")}
    mods = {m["id"] for m in db.rows("modules")}
    for m in msgs.values():
        if m["sender"] not in mods:
            out.append(f"can_messages {m['id']}: sender {m['sender']} is not a module")
        r = m["rate_hz"]
        if r and not (r.replace(".", "").isdigit() or r == "on change"):
            out.append(f"can_messages {m['id']}: rate {r!r} is neither a number nor 'on change'")
    seen = {}
    for f in db.rows("can_fields"):
        if f["msg"] not in msgs:
            out.append(f"can_fields {f['id']}: message {f['msg']} does not exist"); continue
        try:
            rng = byte_range(f["bytes"])
        except ValueError:
            out.append(f"can_fields {f['id']}: bytes {f['bytes']!r} unreadable"); continue
        if max(rng) > 7:
            out.append(f"can_fields {f['id']}: byte {max(rng)} is past the end of an 8-byte frame")
        used = seen.setdefault(f["msg"], set())
        if used & rng:
            out.append(f"can_fields {f['id']}: bytes {sorted(used & rng)} are used twice in {f['msg']}")
        used |= rng
    for mid, m in msgs.items():
        if "ext" in mid:
            continue
        fields = [f for f in db.rows("can_fields") if f["msg"] == mid]
        if not any(f["bytes"] == "7" and f["field"] == "counter" for f in fields):
            out.append(f"can_messages {mid}: byte 7 must be the rolling counter (D-106)")
        if seen.get(mid) != set(range(8)):
            out.append(f"can_messages {mid}: bytes {sorted(set(range(8)) - seen.get(mid, set()))} are not accounted for")
    return out


def c_can_copies(db):
    files = [FW / "icu" / "can_map.h", FW / "dcu" / "can_map.h", FW / "can_map_test" / "can_map.h", FW / "can_loopback_test" / "can_map.h"]
    hashes = {}
    for p in files:
        if p.exists():
            hashes[str(p.relative_to(HERE))] = hashlib.md5(p.read_bytes()).hexdigest()
    if len(set(hashes.values())) > 1:
        return ["can_map.h copies differ: " + "; ".join(f"{k} {v[:8]}" for k, v in hashes.items()) + " — icu/can_map.h is the master, copy it over the others"]
    return []


def c_parts(db):
    out, stages = [], {s["id"] for s in db.rows("stages")}
    for p in db.rows("parts"):
        if p["stage"] not in stages:
            out.append(f"parts {p['id']}: stage {p['stage']!r} does not exist")
        if p["usd_low"] and num(p["usd_low"]) is None:
            out.append(f"parts {p['id']}: usd_low {p['usd_low']!r} is not a number")
    return out


def c_work(db):
    ok = {"done", "open", "blocked", "dropped"}
    return [f"work {w['id']}: state {w['state']!r} not in {sorted(ok)}" for w in db.rows("work") if w["state"] not in ok]


CHECKS = [c_provisions, c_features, c_sensors, c_can, c_can_copies, c_parts, c_work]

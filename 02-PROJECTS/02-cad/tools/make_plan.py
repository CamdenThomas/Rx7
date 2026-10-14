#!/usr/bin/env python3
"""Draft of 02-cad A05: the parts plan. Reads 00-CAR parts, specs and cad (read only);
writes model_parts_planned.csv and plan_summary.csv beside this script. Run from anywhere."""
import collections
import csv
import re
import sys
from pathlib import Path

ROOT = Path("/Users/crash/dev/Rx7")
OUT = Path(__file__).resolve().parent


def rows(rel):
    with open(ROOT / rel, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


parts = rows("00-CAR/data/parts.csv")
P = {p["id"]: p for p in parts}
specs = rows("00-CAR/data/specs.csv")
cad = {c["id"]: c for c in rows("00-CAR/data/cad.csv")}
DIM_UNITS = {"mm", "in", "inch", "cm", "m", "mm (in)", "in (mm)", "deg", "°"}
dims = collections.defaultdict(list)
for s in specs:
    if s.get("part") and (s.get("unit") or "").strip().lower() in DIM_UNITS:
        dims[s["part"]].append(s["id"])

kids = collections.defaultdict(list)
for p in parts:
    if p["parent"]:
        kids[p["parent"]].append(p["id"])


def ancestors(i):
    seen = []
    while P[i]["parent"]:
        i = P[i]["parent"]
        if i in seen:
            break
        seen.append(i)
    return seen


# ---------------------------------------------------------------- what is skipped, and why
skip = {}
for p in parts:
    if p["applies"] in ("replaced", "not-fitted"):
        skip[p["id"]] = f"{p['applies']} - not on the car"
for p in parts:
    if p["id"] not in skip:
        for a in ancestors(p["id"]):
            if a in skip and skip[a].endswith("not on the car"):
                skip[p["id"]] = f"inside {a}, which is {P[a]['applies']}"
                break
KIT = re.compile(r"\b(gasket set|o-ring set|seal kit|boot kit|repair kit|parts set|parts kit|inner parts kit|shim kit|overhaul repair kit)\b", re.I)
for p in parts:
    i, n = p["id"], p["name"]
    if i in skip:
        continue
    if KIT.search(n):
        skip[i] = "consumable: a service kit, not one solid"
    elif re.search(r"\bbulb", n, re.I) and not re.search(r"socket", n, re.I):
        skip[i] = "consumable: bulb"
    elif re.match(r"Fuses?,", n):
        skip[i] = "consumable: fuse"
    elif re.search(r"blade refill", n, re.I):
        skip[i] = "consumable: wiper refill"
    elif re.search(r"\blabel\b", n, re.I):
        skip[i] = "document: a label"
for i, why in {
    "PT040": "a system grouping, not a part (its pieces are rows)",
    "PT705": "loose item: key set", "PT706": "loose item: keys",
    "PT965": "loose item: tool bag", "PT966": "loose item: tool set", "PT967": "loose item: wheel nut wrench",
    "PT029": "no separate box: S-001 draws the INT timer inside the CPU PT301 (its own note)",
}.items():
    skip.setdefault(i, why)

# ---------------------------------------------------------------- the unibody band (the other agent's, D-518)
UNIBODY = ["PT704", "PT778", "PT779", "PT781", "PT755", "PT780", "PT782", "PT783", "PT771", "PT784",
           "PT756", "PT757", "PT764", "PT762", "PT766", "PT770", "PT769", "PT754", "PT761", "PT753",
           "PT752", "PT767", "PT773", "PT774", "PT772", "PT768", "PT777", "PT775", "PT776"]

# ---------------------------------------------------------------- unit insides: modelled when the unit is opened (D-517)
INSIDE = set()
INSIDE |= {f"PT{n:03d}" for n in list(range(61, 74)) + list(range(79, 86)) + list(range(88, 100)) + list(range(104, 110))}
INSIDE |= {f"PT{n:03d}" for n in range(264, 275)}            # alternator
INSIDE |= {f"PT{n:03d}" for n in range(275, 288)}            # starter
INSIDE |= {"PT016", "PT256", "PT257", "PT258", "PT259", "PT261", "PT262", "PT263"}   # distributor
INSIDE |= {"PT185", "PT186", "PT187", "PT188", "PT192", "PT193"}                      # water pump, fan drive
INSIDE |= {f"PT{n:03d}" for n in range(231, 239)}            # A/C compressor
INSIDE |= {f"PT{n:03d}" for n in range(679, 684)}            # wiper motor
INSIDE |= {f"PT{n:03d}" for n in range(475, 483)} | {"PT485"}  # steering gear box
INSIDE |= {"PT563", "PT497", "PT451", "PT043", "PT044", "PT048", "PT431", "PT432", "PT433"}
INSIDE |= {f"PT{n:03d}" for n in range(436, 445)}            # differential carrier
INSIDE |= {"PT423", "PT424", "PT425", "PT199", "PT538", "PT302"}
INSIDE |= {"PT203", "PT204", "PT205", "PT207", "PT208", "PT222", "PT223", "PT227", "PT247", "PT248", "PT249", "PT251"}
INSIDE |= {f"PT{n:03d}" for n in range(615, 630)} - {"PT619", "PT622"}               # cluster
INSIDE |= {"PT503", "PT504", "PT515", "PT516", "PT490", "PT411", "PT413", "PT414"}
INSIDE |= {f"PT{n:03d}" for n in range(879, 891)} | {f"PT{n:03d}" for n in range(892, 904)}  # seats taken apart
INSIDE |= {"PT330", "PT331", "PT332", "PT333", "PT334", "PT335", "PT336", "PT340", "PT341", "PT342", "PT343", "PT344",
           "PT345", "PT348", "PT349", "PT350", "PT351", "PT352", "PT353", "PT356", "PT357"} | \
          {f"PT{n:03d}" for n in range(360, 410)}            # automatic transmission

# ---------------------------------------------------------------- removal steps named by a project row
# phase rank, step label, mode; a step given to a part passes to everything under it unless overridden
STEP = {
    "S1h": (1, "01-electrical S1 (1) if it comes easily, else 04-luxury I1", "off"),
    "S1a": (1, "01-electrical S1 (2) shrouds off", "off"),
    "S1i": (1, "01-electrical S1 (2) measured in place, shrouds off - CK17/CK18", "inplace"),
    "S1": (1, "01-electrical S1 (3) strip", "off"),
    "S1c": (1, "01-electrical S1 (3) strip - carpet and pads last", "off"),
    "E8": (2, "01-electrical E8 backbone weekend", "off"),
    "E30": (3, "01-electrical E30 factory harness out", "off"),
    "CP01": (4, "03-engine CP01 the 12A, automatic, Weber, exhaust out", "off"),
    "CP03": (5, "03-engine CP03 shifter opening", "off"),
    "CP05": (5, "03-engine CP05 manual pedal box", "off"),
    "CP09": (5, "03-engine CP09 pedal at the dash", "off"),
    "CP06": (6, "03-engine CP06 fuel system (the tank if it comes down - DS12)", "off"),
    "CP07": (6, "03-engine CP07 cooling", "off"),
    "CP08": (7, "03-engine CP08 rear axle and driveshaft (D-113)", "off"),
    "CP10": (7, "03-engine CP10 front springs - the struts out", "off"),
    "I3": (8, "04-luxury I3 new blower motor", "off"),
    "I12": (8, "04-luxury I12 / I13 door cards off, regulators out", "off"),
    "I15": (8, "04-luxury I15 lighting second pass", "off"),
    "E41": (8, "01-electrical E41 audio (rear trim off)", "off"),
}
ASSIGN = {}
for ids, s in [
    ("PT850 PT851 PT852", "S1a"),
    ("PT638", "S1i"),
    ("PT469 PT853 PT861 PT822 PT711 PT614 PT619 PT655 PT660 PT661 PT631 PT634 PT635 PT036 PT034 PT849 PT867 "
     "PT878 PT891 PT930 PT931 PT934 PT935 PT662 PT936 PT937 PT938 PT939 "
     "PT940 PT946 PT947 PT948 PT949 PT953 PT954", "S1"),
    ("PT215", "S1h"),
    ("PT941 PT942 PT943 PT944 PT945 PT558", "S1c"),
    ("PT024", "E8"),
    ("PT027 PT630 PT667 PT594", "E30"),
    ("PT001 PT054 PT006 PT058 PT121 PT012 PT537 PT539 PT540 PT541 PT543 PT230 PT228 PT229 PT041 PT244 "
     "PT210 PT211 PT212 PT213 PT622 PT337 PT358 PT420 PT198", "CP01"),
    ("PT410", "CP03"),
    ("PT553", "CP05"),
    ("PT164 PT643", "CP09"),
    ("PT007 PT008 PT009 PT010 PT011 PT167 PT176 PT177 PT178 PT179 PT180", "CP06"),
    ("PT020 PT195 PT293", "CP07"),
    ("PT422 PT055", "CP08"),
    ("PT056", "CP10"),
    ("PT039 PT224 PT225 PT226", "I3"),
    ("PT910 PT911 PT807 PT808", "I12"),
    ("PT601 PT035", "I15"),
    ("PT664", "E41"),
]:
    for i in ids.split():
        ASSIGN[i] = s
# stays on even though its parent goes
for i in ("PT512", "PT513", "PT487", "PT763", "PT975"):
    ASSIGN[i] = None


def where(i):
    """(phase rank, step label, mode, unit) for a kept part."""
    if i in UNIBODY:
        return 0, "unibody - D-518, measured in place as the strip bares it", "unibody", ""
    chain = [i] + ancestors(i)
    for j, a in enumerate(chain):
        if a in INSIDE:
            # the unit it is inside: the first ancestor above the inside run that is not itself inside
            last = max(k for k, b in enumerate(chain) if b in INSIDE)
            unit = chain[last + 1] if last + 1 < len(chain) else chain[-1]
            return 9, f"inside {unit} - when it is opened (D-517)", "bench", unit
        if a in ASSIGN:
            s = ASSIGN[a]
            if s is None:
                break
            rank, label, mode = STEP[s]
            return rank, label, mode, ""
    return 8.5, "stays on - measured in place", "inplace", ""


# ---------------------------------------------------------------- what each is made from
SHELL = "fb-rx7-1983-modified-3dwarehouse-zxt"
FOUND = {
    "PT001": "grabcad-full-12-a-rotary-engine", "PT006": "grabcad-weber-dcoe-carburetor-1",
    "PT014": "sketchfab-99115a3a", "PT025": "grabcad-mazda-wankel-engine-alternator-1",
    "PT035": "sealed-beam-par46-par56-grabcad-nicholas", "PT230": "grabcad-sanden-refrigerant-compressor",
    "PT266": "timken-6202-2rs-deep-groove-ball-bearing", "PT267": "timken-6201-2rs-deep-groove-ball-bearing",
    "PT595": "sa-fb-1157-side-marker-housing-a-thingiverse-not-a-penguin",
    "PT601": "fb-tail-light-housing-rh-scan-printables-giooig13", "PT641": "fb-turn-signal-canceler-bridge-printables-themagicd",
    "PT737": "rx7-emblem-printables-lovc", "PT738": "rx7-emblem-printables-lovc",
    "PT804": "rx7-door-opener-cup-printables-udopoerzgen", "PT822": "rx7-dash-scan-thingiverse-cabentley22",
    "PT875": "fb-s2-center-dash-vent-printables-jtso", "PT876": "fb-s2-center-dash-vent-printables-jtso",
    "PT509": "sa-fb-strut-top-cap-thingiverse-dongers", "PT949": "sa-fb-storage-bins-printables-grantd",
}
for i in ("PT061", "PT062", "PT063", "PT064", "PT071", "PT077", "PT079", "PT087", "PT088"):
    FOUND[i] = "grabcad-full-12-a-rotary-engine"
for i in ("PT744", "PT751", "PT714", "PT722", "PT720", "PT750", "PT729", "PT796", "PT819", "PT794", "PT795",
          "PT587", "PT032", "PT020", "PT598", "PT608", "PT733", "PT734", "PT037"):
    FOUND[i] = SHELL
FSM = "fb-rx7-1985-fsm-body-checking-dimensions"


def made(i):
    p = P[i]
    if i in UNIBODY:
        src = FSM + "; DT04-DT15"
        if i in ("PT774", "PT768", "PT777", "PT752", "PT775"):
            src += "; shape " + SHELL
        return "factory", src
    if i in FOUND and FOUND[i] in cad and cad[FOUND[i]]["fits"] in ("exact", "close"):
        src = FOUND[i]
        if i in dims:
            src += "; " + " ".join(dims[i][:3])
        return "found", src
    if i in dims:
        return "factory", " ".join(dims[i][:4])
    if p["catalogue"]:
        return "catalogue", p["catalogue"].split(" ")[0] + " " + " ".join(p["catalogue"].split(" ")[1:3])
    return "guess", ""


def needs(mf, mode):
    if mode == "unibody":
        return "nothing now - factory body dims; measure the datums in place as the strip bares them"
    if mode == "bench":
        return {"found": "found model fits - check it when the unit is open",
                "factory": "factory dimension page - check it when the unit is open"}.get(mf, "bench: open the unit")
    if mode == "inplace":
        return {"found": "found model fits - check 3 sizes in place",
                "factory": "nothing - factory dimension page; check in place"}.get(mf, "measure in place")
    return {"found": "found model fits - check 3 sizes when off",
            "factory": "nothing - factory dimension page; check when off"}.get(mf, "measure when off")


def zone(i):
    z = P[i]["zone"]
    for a in ancestors(i):
        if z:
            break
        z = P[a]["zone"]
    return z or "no zone"


def model_parent(i):
    for a in ancestors(i):
        if a not in skip:
            return a
    return "" if i == "PT704" else "PT704"


# ---------------------------------------------------------------- order
SYS_ORDER = {s: n for n, s in enumerate(["body", "steering", "electrical", "lighting", "climate", "transmission",
                                         "engine", "ignition", "fuel", "cooling", "brakes", "driveline",
                                         "suspension", "wheels"])}
ZONE_ORDER = {z: n for n, z in enumerate(["engine_bay", "front", "dash", "cabin", "doors", "cargo", "rear",
                                          "underbody", "corners", "no zone"])}
kept = [p["id"] for p in parts if p["id"] not in skip]
info = {i: where(i) for i in kept}
STEP_ORDER = {v[1]: n for n, v in enumerate(STEP.values())}


def depth(i):
    return len(ancestors(i))


def post_key(i):
    # children before parents for parts taken off at the car; parents first on the bench and in place
    chain = [i] + ancestors(i)
    return tuple(reversed(chain))


def sort_key(i):
    rank, label, mode, unit = info[i]
    sysk = SYS_ORDER.get(P[i]["system"], 99)
    z = ZONE_ORDER.get(zone(i), 99)
    if mode == "unibody":
        return (0, UNIBODY.index(i))
    if mode == "bench":
        ur, ul, um, _ = info.get(unit, (8.5, "", "", ""))
        return (rank, ur, STEP_ORDER.get(ul, 99), unit, sysk, z, post_key(i))
    if mode == "inplace" and rank == 8.5:
        return (rank, z, sysk, post_key(i))
    # off at the car: step order, then zone, then system, then children before parent
    if label.startswith("01-electrical S1 (3)"):
        z = {"cabin": 0, "dash": 1, "no zone": 2, "cargo": 3}.get(zone(i), 4)
    return (rank, STEP_ORDER.get(label, 99), z, sysk, -depth(i), post_key(i))


kept.sort(key=sort_key)
out = []
for n, i in enumerate(kept, 1):
    rank, label, mode, unit = info[i]
    mf, src = made(i)
    p = P[i]
    out.append({
        "id": i, "file": "", "made_from": mf, "source": src, "state": "planned",
        "parent": model_parent(i), "confirm": "all",
        "note": f"{p['system']} · {zone(i)} · {label}",
        "order": n, "needs": needs(mf, mode),
    })
cols = ["id", "file", "made_from", "source", "state", "parent", "confirm", "note", "order", "needs"]
with open(OUT / "model_parts_planned.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    w.writerows(out)

# ---------------------------------------------------------------- summary per (system, zone) group in order
def ranges(ns):
    ns = sorted(ns); out = []; a = b = ns[0]
    for n in ns[1:]:
        if n == b + 1:
            b = n
        else:
            out.append((a, b)); a = b = n
    out.append((a, b))
    return ", ".join(f"{x}" if x == y else f"{x}-{y}" for x, y in out)


groups = collections.OrderedDict()
for r in out:
    k = (P[r["id"]]["system"], zone(r["id"]))
    g = groups.setdefault(k, {"n": 0, "lo": r["order"], "hi": r["order"], "all": [], "found": 0, "needs": collections.Counter(), "steps": collections.Counter()})
    g["n"] += 1
    g["all"].append(r["order"])
    g["lo"] = min(g["lo"], r["order"])
    g["hi"] = max(g["hi"], r["order"])
    g["found"] += r["made_from"] == "found"
    g["needs"][r["needs"]] += 1
    g["steps"][info[r["id"]][1].split(" - ")[0] if info[r["id"]][2] != "bench" else "bench"] += 1
summ = []
for (s, z), g in sorted(groups.items(), key=lambda kv: kv[1]["lo"]):
    need = "; ".join(f"{c} {t}" for t, c in g["needs"].most_common(3))
    steps = ", ".join(f"{t} {c}" for t, c in g["steps"].most_common(4))
    summ.append({"system": s, "zone": z, "parts": g["n"], "orders": ranges(g["all"]), "found": g["found"],
                 "when": steps, "needs": need})
with open(OUT / "plan_summary.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(summ[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(summ)
blocks = []
for r in out:
    k = (P[r["id"]]["system"], zone(r["id"]), r["note"].split(" · ", 2)[2])
    if blocks and blocks[-1]["key"] == k:
        b = blocks[-1]; b["hi"] = r["order"]; b["parts"] += 1; b["found"] += r["made_from"] == "found"
    else:
        blocks.append({"key": k, "lo": r["order"], "hi": r["order"], "parts": 1, "found": int(r["made_from"] == "found")})
with open(OUT / "plan_blocks.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["orders", "system", "zone", "when", "parts", "found"])
    for b in blocks:
        w.writerow([f"{b['lo']}-{b['hi']}", b["key"][0], b["key"][1], b["key"][2], b["parts"], b["found"]])
print("blocks", len(blocks))
with open(OUT / "skipped.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["id", "name", "why"])
    for i in sorted(skip):
        w.writerow([i, P[i]["name"], skip[i]])

print("rows", len(out), "skipped", len(skip))
print("made_from", collections.Counter(r["made_from"] for r in out))
print("system", collections.Counter(P[r["id"]]["system"] for r in out))
print("mode", collections.Counter(info[r["id"]][2] for r in out))
print("skip", collections.Counter(v.split(":")[0].split(",")[0] if not v.startswith("inside") else "inside a not-on-car part" for v in skip.values()))
sys.exit(0)

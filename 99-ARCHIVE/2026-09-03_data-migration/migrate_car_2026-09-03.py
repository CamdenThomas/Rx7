#!/usr/bin/env python3
"""One-off, 2026-09-03: 00-CAR and 01-REFERENCE become data + templates projects.
Tables in modifications.md / known-issues.md / parts-history.md / vehicle.md move
to data/*.csv; the prose stays in templates/. specs.csv and sources.csv were
written by the research pass the same day."""
import csv, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAR = ROOT / "00-CAR"
REF = ROOT / "01-REFERENCE"
(CAR / "data").mkdir(exist_ok=True); (CAR / "templates").mkdir(exist_ok=True)
(REF / "data").mkdir(exist_ok=True); (REF / "templates").mkdir(exist_ok=True)


def read(p): return p.read_text(encoding="utf-8").splitlines()


def cells(line):
    line = line.strip().strip("|")
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def tables(lines):
    i = 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            hdr = cells(lines[i]); rows = []; j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append(cells(lines[j])); j += 1
            yield i, j, hdr, rows
            i = j
        else:
            i += 1


def heading_above(lines, i):
    for k in range(i - 1, -1, -1):
        m = re.match(r"^#{2,4}\s+(.*)$", lines[k])
        if m: return m.group(1).strip()
    return ""


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(header); w.writerows(rows)
    print(f"  {path.relative_to(ROOT)}  {len(rows)} rows")


def templatize(src, out_rel, regions, dest_dir):
    lines = read(src); out = [f"<!-- out: {out_rel} -->"]; i = 0
    for s, e, ph in sorted(regions):
        out.extend(lines[i:s]); out.append(ph); i = e
    out.extend(lines[i:])
    (dest_dir / "templates" / Path(out_rel).name).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"  templates/{Path(out_rel).name}  ({len(regions)} tables replaced)")


# ------------------------------------------------------------ modifications.md
L = read(CAR / "modifications.md"); regions = []
for s, e, hdr, rows in tables(L):
    h = heading_above(L, s)
    if hdr[0] == "#" and hdr[1] == "Date":
        write_csv(CAR / "data" / "mods.csv", ["id", "date", "area", "change", "notes"], rows); regions.append((s, e, "{{table:mods}}"))
    elif hdr[0] == "#" and hdr[1] == "Area":
        rows = [[r[0], r[1], r[2], r[3].replace("electrical-pmu/", "electrical-build/").replace("[`BATTERY-INSTALL.md`](../02-PROJECTS/electrical-build/04-BUILD/BATTERY-INSTALL.md)", "electrical-build install §2")] for r in rows]
        write_csv(CAR / "data" / "planned.csv", ["id", "area", "change", "project"], rows); regions.append((s, e, "{{table:planned}}"))
    elif hdr[0] == "Date":
        write_csv(CAR / "data" / "service.csv", ["id", "date", "mileage", "work", "notes"], [[f"SV{i:02d}", *r] for i, r in enumerate(rows, 1)]); regions.append((s, e, "{{table:service|-id}}"))
    elif hdr[0] == "Item" and hdr[1] == "Spec" and len(hdr) == 4:
        write_csv(CAR / "data" / "fluids.csv", ["id", "spec", "last_changed", "mileage"], rows); regions.append((s, e, "{{table:fluids}}"))
    elif hdr[0] == "Item" and hdr[1] == "Spec":
        regions.append((s, e, "{{table:specs|category=Torque|-category,source,page}}"))
templatize(CAR / "modifications.md", "modifications.md", regions, CAR)

# ------------------------------------------------------------ known-issues.md
L = read(CAR / "known-issues.md"); regions = []; issues = []
for s, e, hdr, rows in tables(L):
    sec = heading_above(L, s)
    for r in rows:
        r = r + [""] * (4 - len(r))
        issues.append([r[0], sec, r[1], r[2], r[3]])
    regions.append((s, e, "{{table:issues|section=" + sec + "|-section}}"))
write_csv(CAR / "data" / "issues.csv", ["id", "section", "issue", "status", "impact"], issues)
templatize(CAR / "known-issues.md", "known-issues.md", regions, CAR)

# ------------------------------------------------------------ parts-history.md
L = read(CAR / "parts-history.md"); regions = []; parts = []; n = 0
for s, e, hdr, rows in tables(L):
    grp = heading_above(L, s)
    # the group is "### date · area" or "#### sub" under it — combine the two levels
    lvl3 = ""; lvl4 = ""
    for k in range(s - 1, -1, -1):
        m = re.match(r"^(#{2,4})\s+(.*)$", L[k])
        if m:
            if len(m.group(1)) == 4 and not lvl4: lvl4 = m.group(2)
            elif len(m.group(1)) == 3: lvl3 = m.group(2); break
            elif len(m.group(1)) == 2: lvl3 = lvl3 or m.group(2); break
    group = lvl3 + (f" · {lvl4}" if lvl4 else "")
    if hdr == ["Part", "Source", "$", "Link"]:
        for r in rows:
            n += 1; parts.append([f"PH{n:03d}", "installed", group, r[0], r[1], r[2], r[3], ""])
    elif hdr == ["Part", "Source", "Link"]:
        for r in rows:
            n += 1; parts.append([f"PH{n:03d}", "not done", group, r[0], r[1], "", r[2], ""])
    elif hdr == ["Part", "Source", "Link", "Note"]:
        for r in rows:
            n += 1; parts.append([f"PH{n:03d}", "not done", group, r[0], r[1], "", r[2], r[3]])
    else:
        continue  # totals and cross-reference tables stay prose
    regions.append((s, e, "{{table:parts_history|group=" + group + "|-id,status,group}}"))
write_csv(CAR / "data" / "parts_history.csv", ["id", "status", "group", "part", "source", "usd", "link", "note"], parts)
templatize(CAR / "parts-history.md", "parts-history.md", regions, CAR)

# ------------------------------------------------------------ vehicle.md — prose with stale links fixed
v = (CAR / "vehicle.md").read_text(encoding="utf-8")
v = v.replace("Alternator | Stock — `V-002` output rating unverified (Checklist 0.4)",
              "Alternator | Stock Mitsubishi — 55 A class per the 1980 and 1985 workshop manuals (SP-078, SP-079); the 1982 rating is read off the case at `V-002`")
v = v.replace("Headlamps | Currently LED housings per [`LOADS.md`](../02-PROJECTS/electrical-pmu/01-DESIGN/LOADS.md); sealed-beam type to confirm (`V-066`)",
              "Headlamps | Currently LED housings (moved to the luxury package with `V-066`); the electrical build runs stock incandescent")
v = v.replace("See [`../02-PROJECTS/electrical-pmu/01-DESIGN/SPEC.md`](../02-PROJECTS/electrical-pmu/01-DESIGN/SPEC.md); state in [`STATUS.md`](../02-PROJECTS/electrical-pmu/STATUS.md).",
              "See [`../02-PROJECTS/electrical-build/01-DESIGN/DESIGN.md`](../02-PROJECTS/electrical-build/01-DESIGN/DESIGN.md); state in its [`QUESTIONS.md`](../02-PROJECTS/electrical-build/QUESTIONS.md) §0. Factory numbers are [`SPECS.md`](SPECS.md).")
v = v.replace("Ionic S9 purchased, not yet fitted** (Phase 3)", "Ionic S9 purchased, not yet fitted** (electrical build, install §2)")
(CAR / "templates" / "vehicle.md").write_text("<!-- out: vehicle.md -->\n" + v, encoding="utf-8", newline="\n")
print("  templates/vehicle.md")

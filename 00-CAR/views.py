"""00-CAR — the owner's manual's views and checks for tools/rx7.py.

What this file derives, and from where (R6):
  maintenance — for every interval row, the last service-log visit whose `items` names it
                (service.csv), and the next due date / mileage from the interval columns.
  as_fitted   — the systems table with a link to each system's chapter under systems/ when one exists.
  procedures  — the procedure index with each body inlined from data/procedures/<id>.md.
  diagrams    — every rendered sheet under systems/*/diagrams/, as a picture list.
Checks: a service visit may only name intervals that exist; every procedure has a body;
        every parts_history status is a known value.
"""
import re
from pathlib import Path

T = lambda h, r: rx7.md_table(h, r)  # noqa: E731
HERE = Path(__file__).resolve().parent


def _ym_add(ym, months):
    y, m = int(ym[:4]), int(ym[5:7])
    m += int(months)
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    return f"{y:04d}-{m:02d}"


def v_maintenance(db, arg):
    """{{maintenance}} — the schedule: item · every · spec · last done (from the service log) · next due."""
    visits = db.rows("service")
    rows = []
    for it in db.rows("intervals"):
        last = [v for v in visits if it["id"] in (v.get("items") or "").split()]
        last_v = last[-1] if last else None
        every = " / ".join(x for x in [f"{it['every_miles']} mi" if it["every_miles"] else "", f"{it['every_months']} mo" if it["every_months"] else ""] if x) or "—"
        due = "—"
        if last_v:
            parts = []
            if it["every_months"] and last_v["date"]:
                parts.append(_ym_add(last_v["date"], it["every_months"]))
            if it["every_miles"] and last_v["mileage"]:
                parts.append(f"{int(last_v['mileage']) + int(it['every_miles'])} mi")
            due = " / ".join(parts) or "—"
        elif it["every_months"] or it["every_miles"]:
            due = "never done — due"
        spec = it["spec"] + (f" ({it['source']})" if it["source"] else "")
        lastdone = (last_v["date"] + (f" · {last_v['mileage']} mi" if last_v["mileage"] else "") + f" · {last_v['id']}") if last_v else "—"
        rows.append([it["item"], every, spec, lastdone, due, it["note"]])
    return T(["Item", "Every", "Spec", "Last done", "Next due", "Note"], rows)


def v_service_log(db, arg):
    """{{service_log}} — the service log newest first, with the parts each visit used."""
    rows = []
    for v in reversed(db.rows("service")):
        parts = ", ".join(v.get("parts", "").split()) or "—"
        rows.append([v["date"], v["mileage"] or "—", v["work"], v.get("items", "").replace(" ", ", ") or "—", parts, v["notes"]])
    return T(["Date", "Mileage", "Work", "Schedule items", "Parts", "Notes"], rows)


def v_as_fitted(db, arg):
    rows = []
    for s in db.rows("as_fitted"):
        chap = s["chapter"]
        link = f"[{chap}](systems/{chap}/README.md)" if chap and (HERE / "systems" / chap).is_dir() else "—"
        rows.append([s["system"], s["state"], s["since"] or "—", link, s["note"]])
    return T(["System", "As fitted today", "Since", "Chapter", "Note"], rows)


def v_vehicle(db, section):
    rows = [[r["field"], r["value"], r["note"]] for r in db.rows("vehicle", "section = ?", section.strip())]
    return T(["Field", "Value", "Note"], rows)


def v_procedures(db, arg):
    out = []
    for p in db.rows("procedures"):
        body = (HERE / "data" / "procedures" / f"{p['id']}.md")
        text = body.read_text(encoding="utf-8").strip() if body.exists() else "*no body yet*"
        out.append(f"### {p['id']} · {p['title']}\n\n*{p['system']} · when: {p['when']} · tools: {p['tools'] or '—'}" + (f" · source: {p['source']}" if p["source"] else "") + f"*\n\n{text}\n")
    return "\n".join(out) if out else "*No procedures yet — they arrive when a project completes, or through `/rx7-log`.*"


def v_diagrams(db, arg):
    out = []
    for svg in sorted((HERE / "systems").glob("*/diagrams/*.svg")) if (HERE / "systems").is_dir() else []:
        rel = svg.relative_to(HERE).as_posix()
        out.append(f"### {svg.parent.parent.name} · {svg.stem}\n\n![{svg.stem}]({rel})\n")
    return "\n".join(out) if out else "*No system has completed yet, so no as-built sheet lives here. Project drawings stay with their project until then.*"


def v_systems(db, arg):
    rows = []
    for d in sorted((HERE / "systems").glob("*/")) if (HERE / "systems").is_dir() else []:
        if (d / "templates" / "README.md").exists():
            rows.append([f"[{d.name}](systems/{d.name}/README.md)"])
    return T(["System chapter"], rows) if rows else "*None yet.*"


VIEWS = {"maintenance": v_maintenance, "service_log": v_service_log, "as_fitted": v_as_fitted, "vehicle": v_vehicle,
         "procedures": v_procedures, "diagrams": v_diagrams, "systems": v_systems}


def c_service(db):
    ids = {i["id"] for i in db.rows("intervals")}
    ph = {p["id"] for p in db.rows("parts_history")}
    out = []
    for v in db.rows("service"):
        for it in (v.get("items") or "").split():
            if it not in ids:
                out.append(f"service:{v['id']} names interval {it!r}, which is not in intervals.csv")
        for p in (v.get("parts") or "").split():
            if p not in ph:
                out.append(f"service:{v['id']} names part {p}, which is not in parts_history.csv")
        if v["date"] and not re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", v["date"]):
            out.append(f"service:{v['id']} date {v['date']!r} is not ISO (YYYY-MM or YYYY-MM-DD)")
    return out


def c_procedures(db):
    return [f"procedures:{p['id']} has no body at data/procedures/{p['id']}.md" for p in db.rows("procedures")
            if not (HERE / "data" / "procedures" / f"{p['id']}.md").exists()]


def c_parts_history(db):
    ok = {"installed", "not done", "not needed", "bought", "returned"}
    return [f"parts_history:{p['id']} status {p['status']!r} not in {sorted(ok)}" for p in db.rows("parts_history") if p["status"] not in ok]


CHECKS = [c_service, c_procedures, c_parts_history]

"""frame.py - the model's frame and hard points, read from 05-cad `datums` through rx7.py (A02, D-418).

Owns no fact: every number comes from the datums table each run (R2, R6). The frame is D-418's:
millimetres, x to the car's right, y forward, z up, ground z 0, front axle y 0.

    datums()          {id: Datum} - every row, its numbers parsed, its raw text kept
    Datum.num(col)    the first number in x_mm / y_mm / z_mm / value, or None
    Datum.confirm     True when any coordinate says confirm (R11)

Runs under the system python and under FreeCAD's (no FreeCAD import here).
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RX7 = os.path.join(ROOT, "tools", "rx7.py")
PYTHON = os.environ.get("RX7_PYTHON", "/usr/bin/python3")


def sql(area, query):
    """Rows of `rx7.py sql AREA QUERY` as dicts. The tool prints a ' | ' table; a cell that holds
    ' | ' itself would break this, and no datums or parts cell does."""
    env = dict(os.environ, DEVELOPER_DIR=os.environ.get("DEVELOPER_DIR",
                                                        "/Library/Developer/CommandLineTools"))
    r = subprocess.run([PYTHON, RX7, "sql", area, query], capture_output=True, text=True,
                       cwd=ROOT, env=env)
    if r.returncode != 0:
        raise RuntimeError("rx7.py sql %s failed (rc %s): %s" % (area, r.returncode,
                                                                 (r.stderr or r.stdout)[-400:]))
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    if not lines or " | " not in lines[0]:
        return []
    head = [h.strip() for h in lines[0].split(" | ")]
    out = []
    for ln in lines[1:]:
        if re.match(r"^\(\d+ row", ln):
            break
        cells = [c.strip() for c in ln.split(" | ")]
        cells += [""] * (len(head) - len(cells))
        out.append(dict(zip(head, cells)))
    return out


NUM = re.compile(r"[-+]?\d+(?:\.\d+)?")


class Datum:
    def __init__(self, row):
        self.row = row
        self.id = row["id"]
        self.confirm = any("confirm" in (row.get(c) or "") for c in ("x_mm", "y_mm", "z_mm"))

    def num(self, col):
        m = NUM.search((self.row.get(col) or "").replace("±", ""))
        return float(m.group()) if m else None

    def above_datum(self, col="z_mm"):
        """'datum + 220' -> 220: a height given above the underbody datum line (DT09)."""
        m = re.search(r"datum\s*\+\s*([\d.]+)", self.row.get(col) or "")
        return float(m.group(1)) if m else None

    def __repr__(self):
        return "Datum(%s %s)" % (self.id, self.row.get("datum"))


def datums():
    return {r["id"]: Datum(r) for r in sql("05-cad", "select * from datums")}


if __name__ == "__main__":
    for k, d in datums().items():
        print(k, d.num("x_mm"), d.num("y_mm"), d.num("z_mm"), "confirm" if d.confirm else "")
    sys.exit(0)

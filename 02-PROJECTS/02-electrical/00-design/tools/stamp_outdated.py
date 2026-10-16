"""stamp_outdated.py - mark the CAD's drawings that the overhaul made outdated (D-612, D-613).

    python3 00-design/tools/stamp_outdated.py          stamp every drawing in STAMPS
    python3 00-design/tools/stamp_outdated.py --clear  take every stamp off again

A schematic, an assembly drawing or a mock-up view is exported from its CAD, and the CAD is not
redrawn until its CAD-pass row (Y70 to Y72). Until then each export carries a banner, added in new
space above the drawing so nothing of it is covered: what changed, which row redraws it, and which
plan sheet (`rx7.py diagrams`) shows the current plan. The original viewBox is kept on the root
element, so the stamp is replaced, never stacked, and comes off whole. Re-exporting the drawing
from its CAD drops the stamp by itself - that is the point: the export is then current.

Owns no facts: the reasons below repeat D-612's rulings for the reader of the drawing only.
"""
import glob
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import parts as layout  # noqa: E402

CU = ("OUTDATED (D-612) - redrawn at Y70", "The CU's connector is the DRC 64 with a DTP comfort inlet, the seats' heat and cool are its "
      "+ side switches, the radar receiver is inside it, the face is the eighth pass, the CUR is on four I2C wires.",
      "The current plan: control-unit/diagrams/cu-plan.svg")
CUR = ("OUTDATED (D-612) - redrawn at Y71",       # no longer used: the CUR was redrawn at Y71 (D-615) "The CUR is on one DRC 24 (DP-CUR) with an I/O expander and an ADC for its keys and stick; "
       "the left plate's two DT13s and its twelve-line cable are gone.",
       "The current plan: control-unit/control-unit-remote/diagrams/cur-plan.svg")
DU = ("OUTDATED (D-612) - redrawn at Y72", "The AEM wideband gauge goes inside the DU on DP-ICU 18 / 19, with a sealed gland for its sensor lead.",
      "The current plan: display-unit/diagrams/du-plan.svg")
DUC = ("RE-CHECK AT Y72 (D-612)", "DP-ICU 18 / 19 now carry the AEM gauge's own feed and ground inside the DU; the carrier's connector is unchanged.",
       "The current plan: display-unit/diagrams/du-plan.svg")
STAMPS = {
    ("cu", "cu-carrier*.svg"): CU, ("cu", "cu-face-board*.svg"): CU, ("cu", "cu-assembly-view-*.svg"): CU,
    ("du", "du-assembly-view-*.svg"): DU, ("du", "du-carrier*.svg"): DUC,
}
ROOT_RE = re.compile(r"<svg\b[^>]*>", re.S)
GROUP_RE = re.compile(r'\n?<g id="rx7-stamp">.*?</g><!-- rx7-stamp -->', re.S)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def attr(tag, name):
    m = re.search(rf'\s{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def set_attr(tag, name, value):
    if attr(tag, name) is None:
        return tag[:-1].rstrip("/") + f' {name}="{value}"' + ("/>" if tag.endswith("/>") else ">")
    return re.sub(rf'(\s{name}=")[^"]*(")', lambda m: m.group(1) + value + m.group(2), tag, count=1)


def unstamp(text):
    text = GROUP_RE.sub("", text)
    m = ROOT_RE.search(text)
    tag = m.group(0)
    keep = attr(tag, "data-rx7-viewbox")
    if keep:
        new = set_attr(tag, "viewBox", keep)
        for name in ("width", "height"):
            orig = attr(tag, f"data-rx7-{name}")
            if orig:
                new = set_attr(new, name, orig)
        new = re.sub(r'\sdata-rx7-(viewbox|width|height)="[^"]*"', "", new)
        text = text[:m.start()] + new + text[m.end():]
    return text


def stamp(text, title, why, plan):
    text = unstamp(text)
    m = ROOT_RE.search(text)
    tag = m.group(0)
    x, y, w, h = (float(v) for v in attr(tag, "viewBox").split())
    bh = max(w * 0.06, 9.0)                         # the banner: 6 % of the width, never under 9 units
    fs = bh * 0.24
    new = set_attr(tag, "data-rx7-viewbox", attr(tag, "viewBox"))
    new = set_attr(new, "viewBox", f"{x:g} {y - bh:g} {w:g} {h + bh:g}")
    for name in ("width", "height"):
        v = attr(tag, name)
        if v:
            new = set_attr(new, f"data-rx7-{name}", v)
            if name == "height":
                num, unit = re.match(r"([\d.]+)(\D*)", v).groups()
                new = set_attr(new, "height", f"{float(num) * (h + bh) / h:.4f}{unit}")
    pad = bh * 0.12
    g = (f'\n<g id="rx7-stamp"><rect x="{x:g}" y="{y - bh:g}" width="{w:g}" height="{bh * 0.94:g}" fill="#fff4e5" '
         f'stroke="#a84a06" stroke-width="{bh * 0.03:g}"/>'
         f'<text x="{x + pad:g}" y="{y - bh + pad + fs:g}" font-family="Noto Sans, Arial, sans-serif" font-size="{fs:g}" '
         f'font-weight="700" fill="#a84a06">{esc(title)}</text>'
         f'<text x="{x + pad:g}" y="{y - bh + pad + fs * 2.2:g}" font-family="Noto Sans, Arial, sans-serif" font-size="{fs * 0.62:g}" '
         f'fill="#3b2a1a">{esc(why)}</text>'
         f'<text x="{x + pad:g}" y="{y - bh + pad + fs * 3.1:g}" font-family="Noto Sans, Arial, sans-serif" font-size="{fs * 0.62:g}" '
         f'fill="#3b2a1a">{esc(plan)}</text></g><!-- rx7-stamp -->')
    return text[:m.start()] + new + g + text[m.end():]


def main():
    clear = "--clear" in sys.argv
    n = 0
    for (part, pattern), (title, why, plan) in STAMPS.items():
        for path in sorted(glob.glob(os.path.join(layout.diagrams_dir(part), pattern))):
            if path.endswith("-plan.svg"):
                continue
            with open(path, encoding="utf-8") as f:
                text = f.read()
            out = unstamp(text) if clear else stamp(text, title, why, plan)
            if out != text:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(out)
                n += 1
                print(("cleared " if clear else "stamped ") + os.path.relpath(path, layout.DESIGN))
    print("%d drawing(s) %s" % (n, "cleared" if clear else "stamped"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Shared sample data (a real slice of 01-electrical: housing L1-S1, routes RT01-RT05) and an SVG
builder that measures every label with the real font and refuses overlapping text."""
from PIL import ImageFont

FONT = "/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf"
_f = {}
def tw(s, size):
    if size not in _f:
        _f[size] = ImageFont.truetype(FONT, size)
    return _f[size].getlength(s)

INK = {"RED": "#d32f2f", "GRY": "#8d949e", "SHLD": "#6b7280", "BLK": "#111", "ORN": "#ef6c00"}

HOUSING = ("L1-S1", "DT06-12S", "Dash post, engine leg, signal")
# cav, circuit, src, colour, awg, device, device_id, terminal, route, inline
WIRES = [
    (1, "Start relay K9 coil", "O21", "RED", "16", "Start relay", "K9", "86", "RT05", ""),
    (2, "Alternator excitation", "F15", "RED", "16", "Alternator", "A-08", "BW", "RT03", ""),
    (3, "Water temp sender", "ICU", "GRY", "16", "Water temp sender", "C-02", "spade", "RT04", ""),
    (4, "Oil pressure sender", "ICU", "GRY", "16", "Oil pressure sender", "C-09", "spade", "RT04", ""),
    (6, "Tach pulse", "ICU", "SHLD", "16 sh", "Ignition coil T", "B-18", "neg (YG)", "RT02", ""),
    (11, "Inhibitor P/N (crank)", "A4", "GRY", "16", "Inhibitor switch", "A-06", "BY", "RT05", "8.2 kΩ"),
]
PLUGGED = [5, 7, 8, 9, 10, 12]
ROUTES = [  # id, from, to, via
    ("RT01", "Dash post", "Engine-bay junction", "firewall grommet, pass. side"),
    ("RT02", "junction", "Coils + igniters", "upper rear housing"),
    ("RT03", "junction", "Alternator", "down front of block"),
    ("RT04", "junction", "Temp + oil senders", "rear housing, gauge ports"),
    ("RT05", "junction", "Starter / K9 / inhibitor", "under the intake"),
]


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.parts, self.boxes, self.segs = w, h, [], [], []
        self.title = title

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=13, anchor="start", weight=400, fill="#1f2328", pad=2):
        w = tw(s, size)
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
        box = (x0 - pad, y - size * 0.8 - pad, x0 + w + pad, y + size * 0.25 + pad, s)
        for b in self.boxes:
            if box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3]:
                raise SystemExit(f"OVERLAP: {s!r} collides with {b[4]!r}")
        self.boxes.append(box)
        s = s.replace("&", "&amp;").replace("<", "&lt;")
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
                 f'font-weight="{weight}" fill="{fill}">{s}</text>')
        return w

    def wire(self, pts, colour, width=6):
        self.segs += [(a, b, width / 2 + 1) for a, b in zip(pts, pts[1:])]
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.add(f'<path d="{d}" fill="none" stroke="#1f2328" stroke-width="{width + 2}" stroke-linejoin="round"/>')
        self.add(f'<path d="{d}" fill="none" stroke="{INK[colour]}" stroke-width="{width}" stroke-linejoin="round"/>')
        if colour == "SHLD":  # braid shown as a dashed silver jacket over the core
            self.add(f'<path d="{d}" fill="none" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="3 3"/>')

    def save(self, path):
        for (ax, ay), (bx, by), r in self.segs:      # no label may sit on a wire
            n = max(1, int(max(abs(bx - ax), abs(by - ay)) / 2))
            for i in range(n + 1):
                x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
                for b in self.boxes:
                    if b[0] - r < x < b[2] + r and b[1] - r < y < b[3] + r:
                        raise SystemExit(f"OVERLAP: label {b[4]!r} sits on a wire at {x:.0f},{y:.0f}")
        with open(path, "w") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                    f'viewBox="0 0 {self.w} {self.h}" font-family="Noto Sans, sans-serif">'
                    f'<rect width="100%" height="100%" fill="#fff"/>' + "".join(self.parts) + "</svg>")
        print(path, "ok —", len(self.boxes), "labels, 0 overlaps")

"""Option C: ELK (Eclipse Layout Kernel) does the placement and orthogonal routing with ports pinned
in order; we draw the result ourselves and run the same overlap check. A richer slice than A/B —
the K9 start circuit and grounds join in — because a laid-out graph is where hand layout stops scaling."""
import json, subprocess, os
from common import *

C = {"RED": "RED", "GRY": "GRY", "SHLD": "SHLD", "BLK": "BLK"}
nodes = {  # id: (title, [ports on west], [ports on east])
    "L1-S1": ("L1-S1 · DT06-12S", [], ["1", "2", "3", "4", "6", "11"]),
    "F17": ("F17 · 30 A MIDI", [], ["out"]),
    "R1": ("8.2 kΩ", ["a"], ["b"]),
    "K9": ("K9 start relay", ["86", "30"], ["85", "87"]),
    "A-08": ("A-08 Alternator", ["BW"], []),
    "C-02": ("C-02 Water temp", ["spade"], []),
    "C-09": ("C-09 Oil pressure", ["spade"], []),
    "B-18": ("B-18 Coil T", ["neg"], []),
    "A-06": ("A-06 Inhibitor", ["BY"], ["BW"]),
    "A-01": ("A-01 Starter", ["S"], []),
    "GND": ("Block ground", ["g1", "g2"], []),
}
edges = [
    ("L1-S1", "1", "K9", "86", "RED", "16"), ("L1-S1", "2", "A-08", "BW", "RED", "16"),
    ("L1-S1", "3", "C-02", "spade", "GRY", "16"), ("L1-S1", "4", "C-09", "spade", "GRY", "16"),
    ("L1-S1", "6", "B-18", "neg", "SHLD", "16"), ("L1-S1", "11", "R1", "a", "GRY", "16"),
    ("R1", "b", "A-06", "BY", "GRY", "16"), ("F17", "out", "K9", "30", "RED", "10"),
    ("K9", "87", "A-01", "S", "RED", "10"), ("K9", "85", "GND", "g1", "BLK", "16"),
    ("A-06", "BW", "GND", "g2", "BLK", "16"),
]
PH, PW = 22, 14
def node(nid):
    title, west, east = nodes[nid]
    ports = []
    w = max(tw(title, 13) + 30, 130)
    for side, lst in (("WEST", west), ("EAST", east)):
        for i, p in enumerate(lst):
            ports.append({"id": f"{nid}:{p}", "width": 8, "height": 8,
                          "x": -4 if side == "WEST" else w - 4, "y": 34 + i * PH + PH / 2 - 4,
                          "layoutOptions": {"port.side": side, "port.index": str(i if side == "EAST" else len(lst) - 1 - i)},
                          "labels": [{"text": p, "width": tw(p, 11) + 4, "height": 14}]})
    h = 34 + PH * max(len(west), len(east), 1)
    return {"id": nid, "width": w, "height": h, "ports": ports,
            "labels": [{"text": title, "width": tw(title, 13), "height": 16}],
            "layoutOptions": {"portConstraints": "FIXED_POS", "portLabels.placement": "INSIDE",
                              "nodeLabels.placement": "[H_CENTER, V_TOP, INSIDE]"}}
graph = {
    "id": "root",
    "layoutOptions": {"elk.algorithm": "layered", "elk.direction": "RIGHT", "elk.edgeRouting": "ORTHOGONAL",
                      "elk.layered.spacing.nodeNodeBetweenLayers": "90", "elk.spacing.nodeNode": "30",
                      "elk.layered.spacing.edgeEdgeBetweenLayers": "14", "elk.spacing.edgeEdge": "14",
                      "elk.layered.crossingMinimization.strategy": "LAYER_SWEEP",
                      "elk.layered.considerModelOrder.strategy": "NODES_AND_EDGES",
                      "elk.edgeLabels.inline": "false", "elk.spacing.edgeLabel": "4"},
    "children": [node(n) for n in nodes],
    "edges": [{"id": f"e{i}", "sources": [f"{a}:{ap}"], "targets": [f"{b}:{bp}"],
               "labels": [{"text": f"{awg} {c if c != 'SHLD' else 'sh'}", "width": tw(f"{awg} {c}", 10) + 4, "height": 13,
                           "layoutOptions": {"edgeLabels.placement": "CENTER"}}]}
              for i, (a, ap, b, bp, c, awg) in enumerate(edges)],
}
json.dump(graph, open("elk_in.json", "w"))
env = dict(os.environ, PATH=os.path.abspath("node/bin") + ":" + os.environ["PATH"])
subprocess.run(["node", "-e", """
const ELK=require('./elk/node_modules/elkjs');const fs=require('fs');
new ELK().layout(JSON.parse(fs.readFileSync('elk_in.json'))).then(g=>fs.writeFileSync('elk_out.json',JSON.stringify(g)));
"""], check=True, env=env)
g = json.load(open("elk_out.json"))

OX, OY = 30, 90
s = Svg(int(g["width"]) + 60, int(g["height"]) + 150, "elk")
s.text(30, 36, "L1 ENGINE · start circuit · laid out by ELK", 20, weight=700)
s.text(30, 60, "Layered left-to-right, orthogonal wires, ports held in pin order; drawn and overlap-checked by us.", 13, fill="#57606a")
for i, e in enumerate(g["edges"]):
    sec = e["sections"][0]
    pts = [sec["startPoint"]] + sec.get("bendPoints", []) + [sec["endPoint"]]
    s.wire([(p["x"] + OX, p["y"] + OY) for p in pts], edges[i][4], width=5)
for n in g["children"]:
    x, y = n["x"] + OX, n["y"] + OY
    s.add(f'<rect x="{x}" y="{y}" width="{n["width"]}" height="{n["height"]}" rx="6" fill="#f6f8fa" stroke="#1f2328" stroke-width="1.5"/>')
    lb = n["labels"][0]
    s.text(x + n["width"] / 2, y + 20, lb["text"], 13, anchor="middle", weight=700)
    for p in n["ports"]:
        px, py = x + p["x"], y + p["y"]
        s.add(f'<rect x="{px}" y="{py}" width="8" height="8" fill="#1f2328"/>')
        east = p["layoutOptions"]["port.side"] == "EAST"
        t = p["labels"][0]["text"]
        s.text(px - 4 if east else px + 12, py + 8.5, t, 11, anchor="end" if east else "start", weight=600)
for i, e in enumerate(g["edges"]):
    for lb in e.get("labels", []):
        s.text(lb["x"] + OX + 2, lb["y"] + OY + 11, lb["text"], 10, fill="#57606a", pad=1)
ly = int(g["height"]) + OY + 40
x = 30
for c, name in (("RED", "RED power"), ("GRY", "GRY analog"), ("SHLD", "shielded"), ("BLK", "BLK ground")):
    s.wire([(x, ly), (x + 40, ly)], c)
    x += 50 + s.text(x + 50, ly + 5, name, 12) + 30
s.save("opt_elk.svg")

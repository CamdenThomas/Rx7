"""tryruns.py base.kicad_pcb prefix NETS pass,pass,.. : several freerouting rounds with different pass limits (the router
does not converge on this board; its last pass is not its best), report the open signal nets of each."""
import subprocess, sys, os, json
S = os.path.dirname(os.path.abspath(__file__))
base, prefix, nets = sys.argv[1:4]
for p in sys.argv[4].split(","):
    tag = "%s-%s" % (prefix, p)
    r = subprocess.run(["python3", S + "/frrun.py", base, tag, nets, p], capture_output=True, text=True)
    d = json.load(open(os.path.dirname(S) + "/w/dcu-carrier-drc.json"))
    unc = [u for u in d["unconnected_items"]]
    sig = [" / ".join(i["description"][:38] for i in u["items"]) for u in unc if "Zone" not in u["items"][0]["description"] or "Zone" not in u["items"][1]["description"]]
    bad = [v["type"] for v in d["violations"] if v["type"] not in ("via_dangling", "track_dangling")]
    print(tag, "unconnected", len(unc), "non-zone", len(sig), "other violations", bad, sig)

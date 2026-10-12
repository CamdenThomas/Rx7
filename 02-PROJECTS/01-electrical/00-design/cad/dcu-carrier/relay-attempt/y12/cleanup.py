"""cleanup.py work/dcu-carrier.kicad_pcb [rounds] : remove the tracks / vias the DRC calls dangling (matched by UUID),
refill, repeat until none are left (a stub's removal can leave the next one dangling). The board is rewritten in
place. One pcbnew load per process (pcbnew's track list breaks after a Remove), so each round is a child process."""
import sys, json, subprocess, os
brd = sys.argv[1]
if "--once" in sys.argv:
    import pcbnew
    T = pcbnew.ToMM
    out = os.path.splitext(brd)[0] + "-drc.json"
    d = json.load(open(out))
    ids = {v['items'][0]['uuid'] for v in d['violations'] if v['type'] in ('via_dangling', 'track_dangling')}
    b = pcbnew.LoadBoard(brd)
    rm = [t for t in b.GetTracks() if t.m_Uuid.AsString() in ids]
    for t in rm:
        p = t.GetPosition() if t.Type() == pcbnew.PCB_VIA_T else t.GetStart()
        q = p if t.Type() == pcbnew.PCB_VIA_T else t.GetEnd()
        print("  remove", "via" if t.Type() == pcbnew.PCB_VIA_T else "track", t.GetNetname(), "LOCKED" if t.IsLocked() else "",
              "%.2f,%.2f > %.2f,%.2f" % (T(p.x), T(p.y), T(q.x), T(q.y)))
    for t in rm: b.Remove(t)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(brd)
    sys.exit(0)
rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 8
KP = "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
for r in range(rounds):
    out = os.path.splitext(brd)[0] + "-drc.json"
    subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--schematic-parity", "--format", "json", "-o", out, brd], capture_output=True)
    d = json.load(open(out))
    n = sum(1 for v in d['violations'] if v['type'] in ('via_dangling', 'track_dangling'))
    if not n:
        print("round", r, "nothing dangling"); break
    res = subprocess.run([KP, os.path.abspath(__file__), brd, "--once"], capture_output=True, text=True)
    print("round", r, "dangling", n)
    print("\n".join(l for l in res.stdout.splitlines() if l.startswith("  remove")))

"""Y11 finish: the new parts' references off the silk (as Y5's), the board texts, refill.
argv: in.kicad_pcb out.kicad_pcb"""
import pcbnew, sys
MM = pcbnew.FromMM
b = pcbnew.LoadBoard(sys.argv[1])
NEW = {"U13", "U14", "U15", "U16", "J11", "J12"} | {"C%d" % i for i in range(38, 46)} | {"D%d" % i for i in range(9, 12)} | {"R%d" % i for i in range(59, 71)}
fps = list(b.GetFootprints())
n = 0
for f in fps:
    if f.GetReference() in NEW and f.Reference().IsVisible():
        f.Reference().SetVisible(False); n += 1
print("references hidden", n)
for d in list(b.GetDrawings()):
    if isinstance(d, pcbnew.PCB_TEXT):
        if d.GetText().startswith('DCU carrier H-002'):
            d.SetText('DCU carrier H-002 rev 0.03 (Y11)\\nPROVISIONAL OUTLINE 180 x 80 - confirm at V-102 (D-455)')
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[2])
print('ok')

import pcbnew
b=pcbnew.LoadBoard('w/src.kicad_pcb')
fps={f.GetReference(): f for f in b.GetFootprints()}
print(fps['U9'].GetCourtyard(pcbnew.F_CrtYd))
for tr in list(b.GetTracks())[:5]: b.Remove(tr)
f=fps['U9']; f.BuildCourtyardCaches()
print(f.GetCourtyard(pcbnew.F_CrtYd))

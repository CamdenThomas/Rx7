"""lock every track (remembering the ones already locked), export DSN and the non-GND pour outlines. argv: in.pcb out.dsn zones.txt locked.txt"""
import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1])
was=[t.m_Uuid.AsString() for t in b.GetTracks() if t.IsLocked()]
open(sys.argv[4],'w').write('\n'.join(was))
for t in b.GetTracks(): t.SetLocked(True)
print('export',pcbnew.ExportSpecctraDSN(b,sys.argv[2]))
with open(sys.argv[3],'w') as f:
  for z in b.Zones():
    if z.GetIsRuleArea() or z.GetNetname()=='GND': continue
    o=z.Outline(); pts=[(pcbnew.ToMM(o.CVertex(i).x),pcbnew.ToMM(o.CVertex(i).y)) for i in range(o.TotalVertices())]
    f.write(z.GetLayerName()+';'+z.GetNetname()+';'+' '.join('%.3f,%.3f'%p for p in pts)+'\n')
print(len(was),'were locked;',len(list(b.GetTracks())),'tracks')

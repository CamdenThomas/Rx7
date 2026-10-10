"""lock everything except unlocked tracks inside the box (they stay routable), export DSN; write a base board
without those tracks. argv: in.pcb out.dsn zones.txt base_out.pcb x0 y0 x1 y1"""
import pcbnew,sys
T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1]); x0,y0,x1,y1=map(float,sys.argv[5:9])
def inbox(t):
    pts=[t.GetPosition()] if t.Type()==pcbnew.PCB_VIA_T else [t.GetStart(),t.GetEnd()]
    return all(x0<=T(p.x)<=x1 and y0<=T(p.y)<=y1 for p in pts)
free=[t for t in b.GetTracks() if not t.IsLocked() and inbox(t) and t.GetNetname()!="GND"]
fid=set(t.m_Uuid.AsString() for t in free)
for t in b.GetTracks():
    if t.m_Uuid.AsString() not in fid: t.SetLocked(True)
print('export',pcbnew.ExportSpecctraDSN(b,sys.argv[2]),'routable',len(free))
with open(sys.argv[3],'w') as f:
  for z in b.Zones():
    if z.GetIsRuleArea() or z.GetNetname()=='GND': continue
    o=z.Outline(); pts=[(T(o.CVertex(i).x),T(o.CVertex(i).y)) for i in range(o.TotalVertices())]
    f.write(z.GetLayerName()+';'+z.GetNetname()+';'+' '.join('%.3f,%.3f'%p for p in pts)+'\n')
c=pcbnew.LoadBoard(sys.argv[1])
for t in list(c.GetTracks()):
    if t.m_Uuid.AsString() in fid: c.Remove(t)
pcbnew.ZONE_FILLER(c).Fill(c.Zones()); c.Save(sys.argv[4]); print('base saved')

"""Clean-up after the router: drop vias/tracks the DRC calls dangling, stitch every GND fill
fragment top-to-bottom, refill.  argv: in.kicad_pcb drc.json out.kicad_pcb"""
import pcbnew, sys, json, math
MM=pcbnew.FromMM; ToMM=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1]); d=json.load(open(sys.argv[2]))
dang=[(v['items'][0]['pos']['x'],v['items'][0]['pos']['y'],v['type']) for v in d['violations'] if v['type'] in ('via_dangling','track_dangling')]
rm=[]
for t in b.GetTracks():
    if t.IsLocked(): continue
    for x,y,k in dang:
        if k=='via_dangling' and t.Type()==pcbnew.PCB_VIA_T:
            p=t.GetPosition()
            if abs(ToMM(p.x)-x)<0.01 and abs(ToMM(p.y)-y)<0.01: rm.append(t)
        if k=='track_dangling' and t.Type()==pcbnew.PCB_TRACE_T:
            for p in (t.GetStart(),t.GetEnd()):
                if abs(ToMM(p.x)-x)<0.01 and abs(ToMM(p.y)-y)<0.01: rm.append(t)
u=[]
for t in rm:
    if not any(t is x or t.m_Uuid.AsString()==x.m_Uuid.AsString() for x in u): u.append(t)
for t in u: b.Remove(t)
print('removed dangling',len(u))
filler=pcbnew.ZONE_FILLER(b); filler.Fill(b.Zones())
gnd=b.FindNet('GND').GetNetCode()
fills={}
for z in b.Zones():
    if z.GetNetCode()==gnd and not z.GetIsRuleArea() and z.GetZoneName().startswith('GND pour'):
        L=z.GetFirstLayer(); fills[L]=z.GetFilledPolysList(L).CloneDropTriangulation()
F,B=fills[pcbnew.F_Cu],fills[pcbnew.B_Cu]
for s in (F,B): s.Deflate(MM(float(sys.argv[4]) if len(sys.argv)>4 else 0.55),pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS,MM(0.01))
I=F.CloneDropTriangulation(); I.BooleanIntersection(B)
holes=[]
for t in b.GetTracks():
    if t.Type()==pcbnew.PCB_VIA_T: holes.append((ToMM(t.GetPosition().x),ToMM(t.GetPosition().y),ToMM(t.GetDrillValue())/2))
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetDrillSize().x>0: holes.append((ToMM(p.GetPosition().x),ToMM(p.GetPosition().y),ToMM(max(p.GetDrillSize().x,p.GetDrillSize().y))/2))
added=0
gv=[t.GetPosition() for t in b.GetTracks() if t.Type()==pcbnew.PCB_VIA_T and t.GetNetCode()==gnd]
gv+=[p.GetPosition() for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode()==gnd and p.GetDrillSize().x>0]
for i in range(I.OutlineCount()):
    o=I.Outline(i)
    if any(o.PointInside(q) for q in gv): continue
    cand=[o.CPoint(k) for k in range(o.PointCount())]
    c=o.Centre() if hasattr(o,'Centre') else None
    if c is not None and I.Contains(c): cand=[c]+cand
    for q in cand:
        x,y=ToMM(q.x),ToMM(q.y)
        if all(math.hypot(x-hx,y-hy)>=hr+0.15+0.25+0.05 for hx,hy,hr in holes):
            v=pcbnew.PCB_VIA(b); v.SetPosition(q); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3))
            v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); v.SetNetCode(gnd); b.Add(v)
            holes.append((x,y,0.15)); added+=1; break
print('stitch vias',added,'of',I.OutlineCount(),'regions')
filler=pcbnew.ZONE_FILLER(b); filler.Fill(b.Zones())
b.Save(sys.argv[3])

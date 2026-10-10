"""For each isolated GND pad given, find via spots where one layer's fill is the pad's fragment and the other
layer's fill is the board's main GND fragment (both with room for a 0.6 via); add the via. argv: in out pad,pad..."""
import pcbnew,sys,math
MM=pcbnew.FromMM; T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1])
F,B=pcbnew.F_Cu,pcbnew.B_Cu
frag={F:[],B:[]}
for z in b.Zones():
    if z.GetNetname()!="GND": continue
    for L in (F,B):
        if not z.IsOnLayer(L): continue
        ps=z.GetFilledPolysList(L)
        for i in range(ps.OutlineCount()):
            full=pcbnew.SHAPE_POLY_SET(); full.AddOutline(ps.Outline(i))
            for h in range(ps.HoleCount(i)): full.AddHole(ps.Hole(i,h))
            outer=pcbnew.SHAPE_POLY_SET(); outer.AddOutline(ps.Outline(i))
            core=full.CloneDropTriangulation(); core.Inflate(-MM(0.32),pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS,MM(0.01))
            frag[L].append((outer.Area(),outer,core))
main={L:max(frag[L],key=lambda f:f[0]) for L in (F,B)}
padpos={}
for p in b.GetPads():
    if p.GetNetname()=="GND": padpos[p.GetParentFootprint().GetReference()+"."+p.GetNumber()]=p.GetPosition()
added=[]
def has_via_near(x,y,r=0.9):
    for v in added:
        if math.hypot(v[0]-x,v[1]-y)<r: return True
    return False
for name in sys.argv[3].split(","):
    pp=padpos[name]; best=None
    for L in (F,B):
        other=B if L==F else F
        mine=[f for f in frag[L] if f[1].Contains(pp)]
        if not mine: continue
        f0=mine[0]
        if f0 is main[L]: print(name,"already main on",L); best="main"; break
        # grid search inside the fragment's bbox
        bb=f0[1].BBox()
        x0,y0,x1,y1=T(bb.GetX()),T(bb.GetY()),T(bb.GetRight()),T(bb.GetBottom())
        cands=[]
        x=x0
        while x<=x1:
            y=y0
            while y<=y1:
                pt=pcbnew.VECTOR2I(MM(x),MM(y))
                if f0[2].Contains(pt) and main[other][2].Contains(pt):
                    cands.append((math.hypot(x-T(pp.x),y-T(pp.y)),x,y))
                y+=0.1
            x+=0.1
        if cands:
            cands.sort(); d,x,y=cands[0]; best=(x,y,L); break
    print(name,best)
    if best and best!="main":
        x,y,L=best
        v=pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(x),MM(y))); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3))
        v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(F,B); v.SetNet(b.FindNet("GND")); b.Add(v); added.append((x,y))
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2])

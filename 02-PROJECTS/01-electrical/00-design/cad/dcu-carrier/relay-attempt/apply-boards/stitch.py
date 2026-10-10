"""stitch every non-main GND fill fragment to the other layer's main fragment with one via, where both fills
have room for it. argv: in out"""
import pcbnew,sys,math
MM=pcbnew.FromMM; T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1]); F,B=pcbnew.F_Cu,pcbnew.B_Cu
def frags(L):
    out=[]
    for z in b.Zones():
        if z.GetNetname()!="GND" or not z.IsOnLayer(L): continue
        ps=z.GetFilledPolysList(L)
        for i in range(ps.OutlineCount()):
            full=pcbnew.SHAPE_POLY_SET(); full.AddOutline(ps.Outline(i))
            for h in range(ps.HoleCount(i)): full.AddHole(ps.Hole(i,h))
            core=full.CloneDropTriangulation(); core.Inflate(-MM(0.33),pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS,MM(0.01))
            out.append((full.Area(),full,core))
    return out
fr={F:frags(F),B:frags(B)}
main={L:max(fr[L],key=lambda f:f[0]) for L in (F,B)}
holes=[(T(p.GetPosition().x),T(p.GetPosition().y),T(p.GetDrillSize().x)/2) for p in b.GetPads() if p.GetDrillSize().x>0]
holes+=[(T(t.GetPosition().x),T(t.GetPosition().y),T(t.GetDrillValue())/2) for t in b.GetTracks() if t.Type()==pcbnew.PCB_VIA_T]
n=0
for L in (F,B):
    other=B if L==F else F
    for a,full,core in fr[L]:
        if full is main[L][1] or a<MM(1)*MM(1)*0.5: continue
        bb=full.BBox(); x0,y0,x1,y1=T(bb.GetX()),T(bb.GetY()),T(bb.GetRight()),T(bb.GetBottom())
        done=False; x=x0
        while x<=x1 and not done:
            y=y0
            while y<=y1:
                pt=pcbnew.VECTOR2I(MM(x),MM(y))
                if core.Contains(pt) and main[other][2].Contains(pt) and all(math.hypot(x-hx,y-hy)>hr+0.15+0.25+0.05 for hx,hy,hr in holes):
                    v=pcbnew.PCB_VIA(b); v.SetPosition(pt); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
                    v.SetLayerPair(F,B); v.SetNet(b.FindNet("GND")); b.Add(v); holes.append((x,y,0.15)); n+=1; done=True; break
                y+=0.1
            x+=0.1
        if not done: print("no spot for fragment",L,round(x0,1),round(y0,1),round(x1,1),round(y1,1),round(T(T(a)),2) if False else "")
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("stitched",n)

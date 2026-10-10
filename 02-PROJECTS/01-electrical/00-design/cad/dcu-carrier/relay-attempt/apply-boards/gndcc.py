"""GND connectivity through pours, vias, tracks and pads: print the fragments outside the biggest group."""
import pcbnew,sys
T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1])
F,B=pcbnew.F_Cu,pcbnew.B_Cu
items=[]   # (kind, layerset, shape-poly-set or item)
for z in b.Zones():
    if z.GetNetname()!="GND": continue
    for L in (F,B):
        if not z.IsOnLayer(L): continue
        ps=z.GetFilledPolysList(L)
        for i in range(ps.OutlineCount()):
            s=pcbnew.SHAPE_POLY_SET(); s.AddOutline(ps.Outline(i))
            bb=ps.Outline(i).BBox()
            items.append(("zone",{L},s,(T(bb.GetX()),T(bb.GetY()),T(bb.GetRight()),T(bb.GetBottom()))))
for t in b.GetTracks():
    if t.GetNetname()!="GND": continue
    Ls={F,B} if t.Type()==pcbnew.PCB_VIA_T else {t.GetLayer()}
    p=t.GetPosition(); items.append(("via" if t.Type()==pcbnew.PCB_VIA_T else "trk",Ls,t,(T(p.x),T(p.y))))
for p in b.GetPads():
    if p.GetNetname()!="GND": continue
    Ls={L for L in (F,B) if p.IsOnLayer(L)}
    items.append(("pad",Ls,p,(p.GetParentFootprint().GetReference()+"."+p.GetNumber(),round(T(p.GetPosition().x),2),round(T(p.GetPosition().y),2))))
n=len(items); par=list(range(n))
def f(i):
    while par[i]!=i: par[i]=par[par[i]]; i=par[i]
    return i
def shape(it,L):
    k,Ls,o,_=it
    if k=="zone": return None
    return o.GetEffectiveShape(L)
for i in range(n):
    for j in range(i+1,n):
        a,c=items[i],items[j]
        common=a[1]&c[1]
        if not common: continue
        hit=False
        for L in common:
            if a[0]=="zone" and c[0]=="zone": continue
            if a[0]=="zone" or c[0]=="zone":
                z,o=(a,c) if a[0]=="zone" else (c,a)
                sh=o[2].GetEffectiveShape(L)
                # point test on the item's anchor plus a collide
                pt=o[2].GetPosition()
                if z[2].Contains(pcbnew.VECTOR2I(pt.x,pt.y)): hit=True
                elif o[0]=="trk" and (z[2].Contains(o[2].GetStart()) or z[2].Contains(o[2].GetEnd())): hit=True
            else:
                try:
                    if a[2].GetEffectiveShape(L).Collide(c[2].GetEffectiveShape(L),0): hit=True
                except Exception: pass
            if hit: break
        if hit: par[f(i)]=f(j)
g={}
for i in range(n): g.setdefault(f(i),[]).append(i)
groups=sorted(g.values(),key=len,reverse=True)
print("groups",len(groups),"main",len(groups[0]))
for grp in groups[1:]:
    print([items[i][0]+":"+str(items[i][3]) for i in grp][:6])

"""D12 / D13 out; R71 / R72 / F1 on top in the corner left of J4; the three panel lines drawn by hand from
J4 22 / 24 / 26 over the header to them; the +5V branch that crossed the corner removed. argv: in out"""
import pcbnew,sys
MM=pcbnew.FromMM; T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1])
F,B=pcbnew.F_Cu,pcbnew.B_Cu
def V(x,y): return pcbnew.VECTOR2I(MM(x),MM(y))
DEL=[b.FindFootprintByReference(r) for r in ("D12","D13")]
def top(r,x,y,rot):
    f=b.FindFootprintByReference(r)
    if f.IsFlipped(): f.Flip(f.GetPosition(),pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(rot); f.SetPosition(V(x,y))
top("F1",2.9,4.0,0); top("R72",2.9,6.3,0); top("R71",2.9,8.9,0)
P={}
for r in ("F1","R71","R72"):
    for p in b.FindFootprintByReference(r).Pads(): P[(r,p.GetNetname())]=(T(p.GetPosition().x),T(p.GetPosition().y))
j4={p.GetNumber():(T(p.GetPosition().x),T(p.GetPosition().y)) for p in b.FindFootprintByReference("J4").Pads()}
print(P)
n=0
for tr in list(b.GetTracks()):
    if tr.IsLocked(): continue
    pts=[tr.GetPosition()] if tr.Type()==pcbnew.PCB_VIA_T else [tr.GetStart(),tr.GetEnd()]
    corner=any(T(p.x)<=12.3 and T(p.y)<=11.3 for p in pts)
    band=tr.Type()!=pcbnew.PCB_VIA_T and tr.GetLayer()==F and any(12<=T(p.x)<=42 and 1.6<=T(p.y)<=3.2 for p in pts)
    branch=tr.GetNetname()=="+5V" and any(9.0<=T(p.x)<=13.6 and T(p.y)<=10.6 for p in pts) and not (abs(T(pts[0].y)-1.33)<0.05 and len(pts)==2 and abs(T(pts[1].y)-1.33)<0.05)
    if corner or band or branch: b.Remove(tr); n+=1
print("ripped",n)
for f in DEL:
    if f: b.Remove(f)
def net(nm): return b.FindNet(nm)
def tr(nm,pts,w,layer=F):
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        t=pcbnew.PCB_TRACK(b); t.SetStart(V(x0,y0)); t.SetEnd(V(x1,y1)); t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(net(nm)); t.SetLocked(True); b.Add(t)
x,y=j4["26"]; tr("/+5V_PNL",[(x,y),(x,1.98),(6.0,1.98),(6.0,P[("F1","/+5V_PNL")][1]),P[("F1","/+5V_PNL")]],0.25)
x,y=j4["24"]; tr("/PNL_SCL",[(x,y),(x,2.42),(6.85,2.42),(6.85,P[("R72","/PNL_SCL")][1]),P[("R72","/PNL_SCL")]],0.2)
x,y=j4["22"]; tr("/PNL_SDA",[(x,y),(x,2.84),(7.7,2.84),(7.7,P[("R71","/PNL_SDA")][1]),P[("R71","/PNL_SDA")]],0.2)
fx,fy=P[("F1","+5V")]; tr("+5V",[(fx,fy),(0.95,fy),(0.95,1.33),(12.08,1.33)],0.6)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[2]); print("saved")

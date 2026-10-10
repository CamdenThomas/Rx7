"""J4's fan-out drawn by hand: odd pins down on F.Cu to lanes, even pins up on B.Cu to lanes and down into the
Teensy corridor; the panel lines to their parts on the bottom. Locked. argv: in out"""
import pcbnew,sys
MM=pcbnew.FromMM; T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1])
F,B=pcbnew.F_Cu,pcbnew.B_Cu
def V(x,y): return pcbnew.VECTOR2I(MM(x),MM(y))
def place(r,x,y,rot):
    f=b.FindFootprintByReference(r)
    if not f.IsFlipped(): f.Flip(f.GetPosition(),pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(rot); f.SetPosition(V(x,y)); return f
tp=place("TP1",43.7,5.4,0)
f1=place("F1",44.5,9.6,0)
pads={p.GetNetname():(T(p.GetPosition().x),T(p.GetPosition().y)) for p in b.FindFootprintByReference('F1').Pads()}
if pads["/+5V_PNL"][0]>pads["+5V"][0]:
    place("F1",44.5,9.6,180); pads={p.GetNetname():(T(p.GetPosition().x),T(p.GetPosition().y)) for p in b.FindFootprintByReference('F1').Pads()}
print("F1",pads)
j4={p.GetNumber():(T(p.GetPosition().x),T(p.GetPosition().y),p.GetNetname()) for p in b.FindFootprintByReference("J4").Pads()}
# rip what is in the fan-out area, keeping the +5V trunk on F.Cu at y 1.33 and the locked GND rail
n=0
for tr in list(b.GetTracks()):
    if tr.IsLocked(): continue
    pts=[tr.GetPosition()] if tr.Type()==pcbnew.PCB_VIA_T else [tr.GetStart(),tr.GetEnd()]
    if tr.GetNetname()=="+5V" and tr.Type()!=pcbnew.PCB_VIA_T and all(abs(T(p.y)-1.33)<0.3 for p in pts): continue
    if any(9.4<=T(p.x)<=49.4 and T(p.y)<=13.0 for p in pts): b.Remove(tr); n+=1
print("ripped",n)
def net(nm): return b.FindNet(nm)
def tr(nm,pts,w,layer):
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        t=pcbnew.PCB_TRACK(b); t.SetStart(V(x0,y0)); t.SetEnd(V(x1,y1)); t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(net(nm)); t.SetLocked(True); b.Add(t)
def via(nm,x,y):
    v=pcbnew.PCB_VIA(b); v.SetPosition(V(x,y)); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(F,B); v.SetNet(net(nm)); v.SetLocked(True); b.Add(v)
W=0.2
# odd signal pins 3..19: F.Cu down, pin 19 nearest lane (9.0), pin 3 farthest (12.2), out to x 44
for k,n in enumerate(range(19,2,-2)):
    x,y,nm=j4[str(n)]; ly=9.0+0.4*k
    tr(nm,[(x,y),(x,ly),(44.0,ly)],W,F)
# even signal pins 4..18: B.Cu up, pin 4 farthest lane (0.91), pin 18 nearest (3.85); then down into the corridor
for k,n in enumerate(range(18,3,-2)):
    x,y,nm=j4[str(n)]; ly=3.85-0.42*k; xt=45.6+0.42*k; sy=7.24-0.42*k
    tr(nm,[(x,y),(x,ly),(xt,ly),(xt,sy),(49.0,sy)],W,B)
# panel lines: jog between the odd pads and down
x,y,nm=j4["22"]; tr(nm,[(x,y),(37.67,y),(37.67,9.3)],W,B)
x,y,nm=j4["24"]; tr(nm,[(x,y),(40.21,y),(40.21,9.3)],W,B)
x,y,nm=j4["26"]; tr(nm,[(x,y),(43.7,5.4)],0.3,B)
x,y,nm=j4["25"]; tr(nm,[(x,y),pads["/+5V_PNL"]],0.6,B)
px,py=pads["+5V"]; tr("+5V",[(px,py),(47.6,8.3)],0.6,B); via("+5V",47.6,8.3); tr("+5V",[(47.6,8.3),(47.6,1.33)],0.6,F)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[2]); print("saved")

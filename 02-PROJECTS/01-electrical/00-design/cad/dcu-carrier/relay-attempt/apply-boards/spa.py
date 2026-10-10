"""ENC_SEAT_PASS_A by hand from J4 15 to the start of its old route at the via (8.05, 11.65), where the
GND rail ran; the rail goes (pins 2 / 20 / 21 / 23 reach GND through the pours). argv: in out"""
import pcbnew,sys
MM=pcbnew.FromMM; T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1])
F,B=pcbnew.F_Cu,pcbnew.B_Cu
def V(x,y): return pcbnew.VECTOR2I(MM(x),MM(y))
n=0
for tr in list(b.GetTracks()):
    pts=[tr.GetPosition()] if tr.Type()==pcbnew.PCB_VIA_T else [tr.GetStart(),tr.GetEnd()]
    nm=tr.GetNetname()
    if tr.IsLocked():
        if nm=="GND" and all(T(p.y)<5.2 and 10<T(p.x)<34 for p in pts): b.Remove(tr); n+=1
        continue
    if nm=="/ENC_SEAT_PASS_A" and any(T(p.y)<15 and T(p.x)<30 for p in pts): b.Remove(tr); n+=1; continue
    if any(T(p.x)<13.5 and T(p.y)<12.2 for p in pts): b.Remove(tr); n+=1; continue
    if tr.Type()!=pcbnew.PCB_VIA_T and tr.GetLayer()==F and any(8<T(p.x)<34 and 3.1<T(p.y)<4.0 for p in pts): b.Remove(tr); n+=1
print("ripped",n)
nt=b.FindNet("/ENC_SEAT_PASS_A")
def tr(pts,w,layer):
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        t=pcbnew.PCB_TRACK(b); t.SetStart(V(x0,y0)); t.SetEnd(V(x1,y1)); t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(nt); t.SetLocked(True); b.Add(t)
def via(x,y):
    v=pcbnew.PCB_VIA(b); v.SetPosition(V(x,y)); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(F,B); v.SetNet(nt); v.SetLocked(True); b.Add(v)
tr([(28.78,7.6),(27.51,6.33),(27.51,3.55)],0.2,B); via(27.51,3.55)
tr([(27.51,3.55),(8.6,3.55),(8.6,11.1),(8.05,11.65)],0.2,F); via(8.05,11.65)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[2]); print("saved")

"""move the panel-line parts to the bottom under J4's right end; rip the J4 bundle and that patch. argv: in out"""
import pcbnew,sys
MM=pcbnew.FromMM; T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1])
def V(x,y): return pcbnew.VECTOR2I(MM(x),MM(y))
POS={"R71":(36.0,14.6,90),"D12":(36.0,10.8,0),"R72":(40.0,14.6,90),"D13":(40.0,10.8,0),"F1":(45.2,9.9,0),"TP1":(44.6,13.6,0)}
for r,(x,y,rot) in POS.items():
    f=b.FindFootprintByReference(r)
    if not f.IsFlipped(): f.Flip(f.GetPosition(),pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(rot); f.SetPosition(V(x,y))
J4N=set("/"+n for n in "ROW1 ROW2 ROW3 COL1 COL2 COL3 ENC_FAN_A ENC_FAN_B ENC_TEMP_A ENC_TEMP_B ENC_SEAT_DRV_A ENC_SEAT_DRV_B ENC_SEAT_PASS_A ENC_SEAT_PASS_B JOY_X JOY_Y JOY_PRESS PNL_SDA PNL_SCL +5V_PNL SPARE".split())
n=0
for tr in list(b.GetTracks()):
    if tr.IsLocked(): continue
    pts=[tr.GetPosition()] if tr.Type()==pcbnew.PCB_VIA_T else [tr.GetStart(),tr.GetEnd(),(tr.GetStart()+tr.GetEnd())/2]
    if tr.GetNetname() in J4N or any(31.5<=T(p.x)<=48.6 and 8.0<=T(p.y)<=17.5 for p in pts):
        b.Remove(tr); n+=1
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[2]); print("ripped",n)

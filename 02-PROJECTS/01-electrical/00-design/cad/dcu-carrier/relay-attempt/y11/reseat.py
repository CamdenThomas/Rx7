"""The old SEAT_STATUS route from U12 pin 20 (to the via at 65.43,29.62) becomes AC_CLUTCH_CMD; its diagonal
to U8 goes; the switch-side remainder stays SEAT_STATUS. argv: in out"""
import pcbnew, sys
T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1])
ni=b.FindNet('/AC_CLUTCH_CMD')
items=[t for t in b.GetTracks() if t.GetNetname()=='/SEAT_STATUS']
info=[]
for t in items:
    if t.Type()==pcbnew.PCB_VIA_T: pts=[(T(t.GetPosition().x),T(t.GetPosition().y))]
    else: pts=[(T(t.GetStart().x),T(t.GetStart().y)),(T(t.GetEnd().x),T(t.GetEnd().y))]
    info.append((t,pts))
rn=0; rm=[]
for t,pts in info:
    if all(x<66 and y<30 for x,y in pts): t.SetNet(ni); rn+=1
    elif len(pts)==2 and any(abs(x-65.43)<0.02 and abs(y-29.62)<0.02 for x,y in pts) and any(abs(x-84.46)<0.02 for x,y in pts): rm.append(t)
for t in rm:
    t.SetNet(ni); t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(65.43),pcbnew.FromMM(29.62))); t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(72.0),pcbnew.FromMM(36.19)))
b.Save(sys.argv[2]); print('renetted',rn,'removed',len(rm))

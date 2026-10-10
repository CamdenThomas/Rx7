"""remove unlocked tracks/vias the DRC calls dangling. argv: in.kicad_pcb drc.json out.kicad_pcb"""
import pcbnew, sys, json
T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1]); d=json.load(open(sys.argv[2]))
dang=[(v['items'][0]['pos']['x'],v['items'][0]['pos']['y'],v['type']) for v in d['violations'] if v['type'] in ('via_dangling','track_dangling')]
items=list(b.GetTracks())
info=[(t, t.IsLocked(), t.Type()==pcbnew.PCB_VIA_T, (T(t.GetPosition().x),T(t.GetPosition().y)) if t.Type()==pcbnew.PCB_VIA_T else None,
       None if t.Type()==pcbnew.PCB_VIA_T else ((T(t.GetStart().x),T(t.GetStart().y)),(T(t.GetEnd().x),T(t.GetEnd().y)))) for t in items]
rm=[]
for t,lk,isv,pos,se in info:
    if lk: continue
    for x,y,k in dang:
        if k=='via_dangling' and isv and abs(pos[0]-x)<0.01 and abs(pos[1]-y)<0.01: rm.append(t); break
        if k=='track_dangling' and not isv and any(abs(p[0]-x)<0.01 and abs(p[1]-y)<0.01 for p in se): rm.append(t); break
for t in rm: b.Remove(t)
print('removed',len(rm))
b.Save(sys.argv[3])

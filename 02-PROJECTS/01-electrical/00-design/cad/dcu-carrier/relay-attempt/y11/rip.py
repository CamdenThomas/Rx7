"""rip unlocked non-GND copper near points. argv: in out x,y,r[;x,y,r...]  -> prints the nets ripped"""
import pcbnew, sys, math
T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1])
circ=[tuple(map(float,c.split(','))) for c in sys.argv[3].split(';')]
keep=set(sys.argv[4].split(',')) if len(sys.argv)>4 else set()
def dseg(px,py,ax,ay,bx,by):
    dx,dy=bx-ax,by-ay; L=dx*dx+dy*dy
    t=0 if L==0 else max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L))
    return math.hypot(px-ax-t*dx,py-ay-t*dy)
items=list(b.GetTracks()); rm=[]; nets=set()
for t in items:
    if t.IsLocked() or t.GetNetname() in ('GND',) or t.GetNetname() in keep: continue
    if t.Type()==pcbnew.PCB_VIA_T:
        p=t.GetPosition(); d=min(math.hypot(T(p.x)-x,T(p.y)-y)-r for x,y,r in circ)
    else:
        a,c=t.GetStart(),t.GetEnd(); d=min(dseg(x,y,T(a.x),T(a.y),T(c.x),T(c.y))-r for x,y,r in circ)
    if d<=0: rm.append(t); nets.add(t.GetNetname())
for t in rm: b.Remove(t)
b.Save(sys.argv[2]); open('ripped.txt','w').write(','.join(sorted(nets)))

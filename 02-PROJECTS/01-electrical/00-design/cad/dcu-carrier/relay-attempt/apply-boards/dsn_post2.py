"""Post-process the DSN: the project's clearances +0.05 mm (freerouting lands 0.03 under a rule),
plain class names, keepouts over the comfort pours, a 0.6 mm edge keepout, the GND plane on B.Cu."""
import re, sys
src,zones,dst=sys.argv[1:4]
t=open(src).read()
pass
t=re.sub(r'\(class ([^ ,()]+),Default ', r'(class \1 ', t)
def poly(layer,pts): return '(polygon %s 0 %s)'%(layer,' '.join('%d %d'%(round(x*1000),round(-y*1000)) for x,y in pts))
add=[]
for line in open(zones):
    layer,net,pts=line.strip().split(';')
    P=[tuple(map(float,p.split(','))) for p in pts.split()]
    add.append('    (keepout "" %s)'%poly(layer,P))
W,H,e=180.0,80.0,0.6
for L in ('F.Cu','B.Cu'):
    for P in ([(0,0),(W,0),(W,e),(0,e)],[(0,H-e),(W,H-e),(W,H),(0,H)],[(0,0),(e,0),(e,H),(0,H)],[(W-e,0),(W,0),(W,H),(W-e,H)]):
        add.append('    (keepout "" %s)'%poly(L,P))
add.append('    (plane GND %s)'%poly('B.Cu',[(0.5,0.5),(179.5,0.5),(179.5,79.5),(0.5,79.5)]))
i=t.index('    (via ')
t=t[:i]+'\n'.join(add)+'\n'+t[i:]
open(dst,'w').write(t)
print(len(add),'structure lines added')

import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1]);T=pcbnew.ToMM
g=0.5;N=360;M=160
occ=[[0]*N for _ in range(M)]
for f in b.GetFootprints():
    s=f.GetCourtyard(pcbnew.F_CrtYd)
    if not s.OutlineCount(): continue
    bb=s.BBox()
    x0,y0,x1,y1=T(bb.GetLeft()),T(bb.GetTop()),T(bb.GetRight()),T(bb.GetBottom())
    for j in range(max(0,int(y0/g)),min(M,int(y1/g)+1)):
        for i in range(max(0,int(x0/g)),min(N,int(x1/g)+1)): occ[j][i]=1
for j in range(0,M,2):
    print('%3d '%(j*g)+''.join('#' if occ[j][i] else '.' for i in range(0,N,2)))

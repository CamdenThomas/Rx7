"""Join each island of a net to its main copper with a small grid router (two layers + vias).
argv: in.kicad_pcb out.kicad_pcb [net]"""
import pcbnew, sys, math, heapq
exec(open(sys.argv[0].replace('maze.py','gndcc_lib.py')).read())
MM=pcbnew.FromMM; ToMM=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1]); netname=sys.argv[3] if len(sys.argv)>3 else 'GND'
net=b.FindNet(netname).GetNetCode()
TW=float(sys.argv[5]) if len(sys.argv)>5 else 0.2; VD=0.6; G=float(sys.argv[4]) if len(sys.argv)>4 else 0.2; VIACOST=4.0
LAY=(pcbnew.F_Cu,pcbnew.B_Cu)
def own_clr(it,L):
    try: return max(MM(0.2),it.GetOwnClearance(L))
    except Exception: return MM(0.2)
allob={L:[] for L in LAY}
for L in LAY:
    for t in b.GetTracks():
        if t.GetNetCode()!=net and t.IsOnLayer(L): allob[L].append((t.GetEffectiveShape(L),own_clr(t,L),t.GetBoundingBox()))
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.IsOnLayer(L) and p.GetNetCode()!=net: allob[L].append((p.GetEffectiveShape(L),own_clr(p,L),p.GetBoundingBox()))
    for z in b.Zones():
        if z.GetNetCode()!=net and not z.GetIsRuleArea() and z.IsOnLayer(L):
            allob[L].append((z.GetFilledPolysList(L),max(MM(0.2),z.GetLocalClearance() or 0),z.GetBoundingBox()))
holes=[(ToMM(t.GetPosition().x),ToMM(t.GetPosition().y),ToMM(t.GetDrillValue())/2) for t in b.GetTracks() if t.Type()==pcbnew.PCB_VIA_T]
holes+=[(ToMM(p.GetPosition().x),ToMM(p.GetPosition().y),ToMM(max(p.GetDrillSize().x,p.GetDrillSize().y))/2) for f in b.GetFootprints() for p in f.Pads() if p.GetDrillSize().x>0]
edge=b.GetBoardEdgesBoundingBox(); EX0,EY0,EX1,EY1=ToMM(edge.GetLeft()),ToMM(edge.GetTop()),ToMM(edge.GetRight()),ToMM(edge.GetBottom())
def clear(L,x,y,w,ob):
    if not (EX0+0.5+w/2<x<EX1-0.5-w/2 and EY0+0.5+w/2<y<EY1-0.5-w/2): return False
    p=pcbnew.VECTOR2I(MM(x),MM(y)); s=pcbnew.SHAPE_SEGMENT(p,p,MM(w))
    for sh,cl,bb in ob[L]:
        if isinstance(sh,pcbnew.SHAPE_POLY_SET):
            if sh.Collide(s,cl+MM(0.03)): return False
        elif s.Collide(sh,cl+MM(0.03)): return False
    return True
def seg_clear(L,a,c,w,ob):
    s=pcbnew.SHAPE_SEGMENT(pcbnew.VECTOR2I(MM(a[0]),MM(a[1])),pcbnew.VECTOR2I(MM(c[0]),MM(c[1])),MM(w))
    for sh,cl,bb in ob[L]:
        if isinstance(sh,pcbnew.SHAPE_POLY_SET):
            if sh.Collide(s,cl+MM(0.03)): return False
        elif s.Collide(sh,cl+MM(0.03)): return False
    return True
def via_clear(x,y,ob):
    for hx,hy,hr in holes:
        if math.hypot(x-hx,y-hy)<hr+0.15+0.25+0.02: return False
    return all(clear(L,x,y,VD,ob) for L in LAY)
added=0
for it_ in range(6):
    comps,frs,items=gnd_components(b,net)
    if len(comps)<2: break
    main=comps[0]; comp=comps[1]
    def fr_polys(c,L,shrink):
        out=[]
        for k in c:
            if k[0]=='Z' and k[2]==L:
                o=[o for l,o,kk in frs if kk==k][0]; ps=pcbnew.SHAPE_POLY_SET(); ps.AddOutline(o)
                ps.Deflate(MM(shrink),pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS,MM(0.01)); out.append(ps)
        return out
    def escapes(c,L):
        out=[]
        for k in c:
            if k[0]!='P': continue
            it=[it for kk,it in items if kk==k][0]
            if not it.IsOnLayer(L) or it.GetDrillSize().x>0: continue
            q=it.GetPosition(); cx_,cy_=ToMM(q.x),ToMM(q.y); bb=it.GetBoundingBox(); w_,h_=ToMM(bb.GetWidth()),ToMM(bb.GetHeight())
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                ext=(w_ if dx else h_)/2+0.35
                ex,ey=cx_+dx*ext,cy_+dy*ext
                if seg_clear(L,(cx_,cy_),(ex,ey),TW,ob): out.append(((cx_,cy_),(ex,ey)))
        return out
    def item_pts(c,L):
        r=[]
        for k in c:
            if k[0] in 'PV':
                it=[it for kk,it in items if kk==k][0]
                if it.IsOnLayer(L): q=it.GetPosition(); r.append((ToMM(q.x),ToMM(q.y)))
        return r
    # window
    xs=[];ys=[]
    for L in LAY:
        for x,y in item_pts(comp,L): xs.append(x); ys.append(y)
        for ps in fr_polys(comp,L,0):
            bb=ps.BBox(); xs+= [ToMM(bb.GetLeft()),ToMM(bb.GetRight())]; ys+=[ToMM(bb.GetTop()),ToMM(bb.GetBottom())]
    m=14; wx0,wx1,wy0,wy1=min(xs)-m,max(xs)+m,min(ys)-m,max(ys)+m
    ob={L:[o for o in allob[L] if not (ToMM(o[2].GetRight())<wx0-1 or ToMM(o[2].GetLeft())>wx1+1 or ToMM(o[2].GetBottom())<wy0-1 or ToMM(o[2].GetTop())>wy1+1)] for L in LAY}
    srcpoly={L:fr_polys(comp,L,0.2) for L in LAY}; dstpoly={L:fr_polys(main,L,0.2) for L in LAY}
    dstpts={L:item_pts(main,L) for L in LAY}
    def inpoly(polys,x,y):
        p=pcbnew.VECTOR2I(MM(x),MM(y)); return any(ps.Contains(p) for ps in polys)
    def is_dst(L,x,y): return inpoly(dstpoly[L],x,y) or any(math.hypot(x-a,y-c)<0.2 for a,c in dstpts[L])
    nx=int((wx1-wx0)/G); ny=int((wy1-wy0)/G)
    cache={}
    def ok(L,i,j):
        k=(L,i,j)
        if k not in cache: cache[k]=clear(L,wx0+i*G,wy0+j*G,TW+0.06,ob)
        return cache[k]
    pq=[]; dist={}; prev={}; pre={}
    for L in LAY:
        for (cxy,exy) in escapes(comp,L):
            i=round((exy[0]-wx0)/G); j=round((exy[1]-wy0)/G)
            if 0<=i<nx and 0<=j<ny and ok(L,i,j) and seg_clear(L,exy,(wx0+i*G,wy0+j*G),TW,ob):
                n=(L,i,j); dist[n]=0; pre[n]=[cxy,exy]; heapq.heappush(pq,(0,n))
    post={}
    for L in LAY:
        for (cxy,exy) in escapes(main,L):
            i=round((exy[0]-wx0)/G); j=round((exy[1]-wy0)/G)
            if 0<=i<nx and 0<=j<ny: post[(L,i,j)]=[exy,cxy]
    for L in LAY:
        for i in range(nx):
            for j in range(ny):
                x,y=wx0+i*G,wy0+j*G
                if inpoly(srcpoly[L],x,y) or any(math.hypot(x-a,y-c)<G*0.75 for a,c in item_pts(comp,L)):
                    dist[(L,i,j)]=0; heapq.heappush(pq,(0,(L,i,j)))
    found=None; nexp=0
    while pq:
        dd,n=heapq.heappop(pq)
        if dd>dist.get(n,1e9): continue
        L,i,j=n; x,y=wx0+i*G,wy0+j*G
        if dd>0 and (is_dst(L,x,y) or (n in post and seg_clear(L,(x,y),post[n][0],TW,ob))): found=n; break
        nexp+=1
        if nexp>150000: break
        for di,dj in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            ii,jj=i+di,j+dj
            if not (0<=ii<nx and 0<=jj<ny): continue
            m_=(L,ii,jj); c=dd+G*math.hypot(di,dj)
            if c<dist.get(m_,1e9) and ok(L,ii,jj) and (di==0 or dj==0 or seg_clear(L,(x,y),(wx0+ii*G,wy0+jj*G),TW,ob)): dist[m_]=c; prev[m_]=n; heapq.heappush(pq,(c,m_))
        O=LAY[1] if L==LAY[0] else LAY[0]; m_=(O,i,j); c=dd+VIACOST
        if c<dist.get(m_,1e9) and via_clear(x,y,ob): dist[m_]=c; prev[m_]=n; heapq.heappush(pq,(c,m_))
    if not found: print('island not joined:',[k[1:3] for k in comp if k[0]=='P'][:4],'expanded',nexp); break
    path=[found]
    while path[-1] in prev: path.append(prev[path[-1]])
    path.reverse()
    # emit: split by layer, merge collinear runs, verify
    runs=[];cur=[path[0]]
    for n in path[1:]:
        if n[0]!=cur[-1][0]: runs.append(cur); cur=[n]
        else: cur.append(n)
    runs.append(cur)
    for ri,r_ in enumerate(runs):
        L=r_[0][0]; pts=[(wx0+i*G,wy0+j*G) for _,i,j in r_]
        if ri==0 and path[0] in pre: pts=pre[path[0]]+pts
        if ri==len(runs)-1 and found in post and not is_dst(*found[:1],*(wx0+found[1]*G,wy0+found[2]*G)): pts=pts+post[found]
        simp=[pts[0]]
        for k in range(1,len(pts)):
            if k==len(pts)-1: simp.append(pts[k]); break
            cand=pts[k+1]
            if not seg_clear(L,simp[-1],cand,TW,ob): simp.append(pts[k])
        for a,c in zip(simp,simp[1:]):
            t=pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(MM(a[0]),MM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(c[0]),MM(c[1])))
            t.SetWidth(MM(TW)); t.SetLayer(L); t.SetNetCode(net); b.Add(t); added+=1
    for a,c in zip(runs,runs[1:]):
        _,i,j=c[0]; x,y=wx0+i*G,wy0+j*G
        v=pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(x),MM(y))); v.SetWidth(MM(VD)); v.SetDrill(MM(0.3))
        v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); v.SetNetCode(net); b.Add(v); holes.append((x,y,0.15))
    print('joined island',[k[1:3] for k in comp if k[0]=='P'][:3],'path',len(path),'vias',len(runs)-1,'expanded',nexp)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
print('segments',added)
b.Save(sys.argv[2])

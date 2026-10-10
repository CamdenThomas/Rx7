def gnd_components(b,gnd):
    par={}
    def f(a):
        par.setdefault(a,a)
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    def u(a,c): par[f(a)]=f(c)
    frs=[]
    for z in b.Zones():
        if z.GetNetCode()!=gnd: continue
        for L in z.GetLayerSet().Seq():
            s=z.GetFilledPolysList(L)
            for i in range(s.OutlineCount()): frs.append((L,s.Outline(i),('Z',z.GetZoneName(),L,i)))
    def frag_at(L,p): return [k for l,o,k in frs if l==L and o.PointInside(p)]
    items=[]
    for f_ in b.GetFootprints():
        for p in f_.Pads():
            if p.GetNetCode()!=gnd: continue
            k=('P',f_.GetReference(),p.GetNumber()); par.setdefault(k,k); items.append((k,p))
            for L in (pcbnew.F_Cu,pcbnew.B_Cu):
                if p.IsOnLayer(L):
                    for fr in frag_at(L,p.GetPosition()): u(k,fr)
    for t in b.GetTracks():
        if t.GetNetCode()!=gnd: continue
        if t.Type()==pcbnew.PCB_VIA_T:
            k=('V',t.m_Uuid.AsString()); par.setdefault(k,k); items.append((k,t))
            for L in (pcbnew.F_Cu,pcbnew.B_Cu):
                for fr in frag_at(L,t.GetPosition()): u(k,fr)
    for t in b.GetTracks():
        if t.GetNetCode()!=gnd or t.Type()!=pcbnew.PCB_TRACE_T: continue
        k=('T',t.m_Uuid.AsString()); par.setdefault(k,k)
        for e in (t.GetStart(),t.GetEnd()):
            for fr in frag_at(t.GetLayer(),e): u(k,fr)
            for kk,it in items:
                if it.IsOnLayer(t.GetLayer()) and it.HitTest(e): u(k,kk)
    for l,o,k in frs: par.setdefault(k,k)
    comp={}
    for k in par: comp.setdefault(f(k),[]).append(k)
    cs=sorted(comp.values(),key=len,reverse=True)
    return cs,frs,items

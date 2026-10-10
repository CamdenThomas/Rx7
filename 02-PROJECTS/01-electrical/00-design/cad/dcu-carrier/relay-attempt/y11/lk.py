import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1]);T=pcbnew.ToMM
x0,y0,x1,y1=map(float,sys.argv[2:6])
for t in b.GetTracks():
    p=t.GetPosition() if t.Type()==pcbnew.PCB_VIA_T else t.GetStart()
    q=p if t.Type()==pcbnew.PCB_VIA_T else t.GetEnd()
    if x0<=T(p.x)<=x1 and y0<=T(p.y)<=y1 or x0<=T(q.x)<=x1 and y0<=T(q.y)<=y1:
        if len(sys.argv)>6 or t.IsLocked():
            print('V' if t.Type()==pcbnew.PCB_VIA_T else 'T', t.GetNetname(), t.GetLayerName(), '%.3f,%.3f -> %.3f,%.3f w%.2f'%(T(p.x),T(p.y),T(q.x),T(q.y),T(t.GetWidth())), 'L' if t.IsLocked() else '')
f=b.FindFootprintByReference('U9')
for p in f.Pads(): print('U9',p.GetNumber(),'%.3f,%.3f'%(T(p.GetPosition().x),T(p.GetPosition().y)),'%.2fx%.2f'%(T(p.GetSize(pcbnew.F_Cu).x),T(p.GetSize(pcbnew.F_Cu).y)),p.GetNetname())

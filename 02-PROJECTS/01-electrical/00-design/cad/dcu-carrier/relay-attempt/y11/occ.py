import pcbnew,sys
from PIL import Image,ImageDraw
b=pcbnew.LoadBoard(sys.argv[1]);T=pcbnew.ToMM;sc=10
im=Image.new('RGB',(1800,800),'white');d=ImageDraw.Draw(im)
for t in b.GetTracks():
    if t.Type()==pcbnew.PCB_TRACE_T:
        c=(255,170,170) if t.GetLayer()==pcbnew.F_Cu else (170,170,255)
        d.line([(T(t.GetStart().x)*sc,T(t.GetStart().y)*sc),(T(t.GetEnd().x)*sc,T(t.GetEnd().y)*sc)],fill=c,width=max(1,int(T(t.GetWidth())*sc)))
for f in b.GetFootprints():
    for L,c in ((pcbnew.F_CrtYd,'black'),(pcbnew.B_CrtYd,'blue')):
        s=f.GetCourtyard(L)
        for i in range(s.OutlineCount()):
            o=s.Outline(i); pts=[(T(o.CPoint(k).x)*sc,T(o.CPoint(k).y)*sc) for k in range(o.PointCount())]
            if len(pts)>2: d.polygon(pts,outline=c)
    d.text((T(f.GetPosition().x)*sc,T(f.GetPosition().y)*sc),f.GetReference(),fill='black')
for x in range(0,181,5):
    d.line([(x*sc,0),(x*sc,8 if x%10 else 16)],fill='black'); 
    if x%10==0: d.text((x*sc+2,16),str(x),fill='black')
for y in range(0,81,5):
    d.line([(0,y*sc),(8 if y%10 else 16,y*sc)],fill='black')
    if y%10==0: d.text((18,y*sc),str(y),fill='black')
im.save(sys.argv[2])

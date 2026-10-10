import pcbnew, sys
from PIL import Image, ImageDraw
ToMM=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1]); x0,y0,wmm,hmm=map(float,sys.argv[2:6]); out=sys.argv[6]; sc=float(sys.argv[7]) if len(sys.argv)>7 else 40
W,H=int(wmm*sc),int(hmm*sc)
def P(x,y): return ((ToMM(x)-x0)*sc,(ToMM(y)-y0)*sc)
layers={}
for L,col in ((pcbnew.B_Cu,(60,90,220)),(pcbnew.F_Cu,(220,50,50))):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    for z in b.Zones():
        if z.GetIsRuleArea() or not z.IsOnLayer(L): continue
        s=z.GetFilledPolysList(L); g=z.GetNetname()=='GND'
        for i in range(s.OutlineCount()):
            o=s.Outline(i); pts=[P(o.CPoint(k).x,o.CPoint(k).y) for k in range(o.PointCount())]
            if len(pts)>2: d.polygon(pts,fill=col+((110,) if g else (60,)))
            for h in range(s.HoleCount(i)):
                hh=s.Hole(i,h); pts=[P(hh.CPoint(k).x,hh.CPoint(k).y) for k in range(hh.PointCount())]
                if len(pts)>2: d.polygon(pts,fill=(0,0,0,0))
    for t in b.GetTracks():
        if t.Type()==pcbnew.PCB_TRACE_T and t.GetLayer()==L:
            g=t.GetNetname()=='GND'
            d.line([P(t.GetStart().x,t.GetStart().y),P(t.GetEnd().x,t.GetEnd().y)],fill=col+(255,) if not g else (0,160,0,255),width=max(1,int(ToMM(t.GetWidth())*sc)))
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.IsOnLayer(L):
                bb=p.GetBoundingBox(); a=P(bb.GetLeft(),bb.GetTop()); c=P(bb.GetRight(),bb.GetBottom())
                g=p.GetNetname()=='GND'
                d.rectangle([a,c],outline=(0,0,0,255),fill=(0,160,0,200) if g else col+(200,))
    layers[L]=im
img=Image.new('RGBA',(W,H),(255,255,255,255))
only=sys.argv[8] if len(sys.argv)>8 else 'FB'
if 'B' in only: img=Image.alpha_composite(img,layers[pcbnew.B_Cu])
if 'F' in only: img=Image.alpha_composite(img,layers[pcbnew.F_Cu])
d=ImageDraw.Draw(img)
for t in b.GetTracks():
    if t.Type()==pcbnew.PCB_VIA_T:
        x,y=P(t.GetPosition().x,t.GetPosition().y); r=ToMM(t.GetWidth(pcbnew.F_Cu))/2*sc
        d.ellipse([x-r,y-r,x+r,y+r],fill=(0,160,0,255) if t.GetNetname()=='GND' else (120,120,120,255),outline='black')
for f in b.GetFootprints():
    x,y=P(f.GetPosition().x,f.GetPosition().y)
    if 0<x<W and 0<y<H: d.text((x,y),f.GetReference(),fill='black')
for mm in range(int(x0),int(x0+wmm)+1):
    x=(mm-x0)*sc; d.line([(x,0),(x,6 if mm%5 else 14)],fill='black')
    if mm%5==0: d.text((x+2,14),str(mm),fill='black')
for mm in range(int(y0),int(y0+hmm)+1):
    y=(mm-y0)*sc; d.line([(0,y),(6 if mm%5 else 14,y)],fill='black')
    if mm%5==0: d.text((16,y),str(mm),fill='black')
img.convert('RGB').save(out)

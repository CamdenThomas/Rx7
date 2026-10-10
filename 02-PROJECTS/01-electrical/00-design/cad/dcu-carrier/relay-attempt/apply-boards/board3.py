"""DCU board rev 0.04 (D-458, D-465): J4 2x13 three mm left of the 2x10 (pins on the same rows, pin n 3.0 mm left),
H1 down to (4, 15) to clear it, the six 0805s that sat there moved below it, the panel-line parts placed,
unlocked copper ripped where things moved. argv: src.kicad_pcb netlist out.kicad_pcb"""
import pcbnew, sys, re
MM=pcbnew.FromMM; T=pcbnew.ToMM
SRC,NET,OUT=sys.argv[1:4]
K="/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
F,B=pcbnew.F_Cu,pcbnew.B_Cu
def V(x,y): return pcbnew.VECTOR2I(MM(x),MM(y))
def parse(s):
    toks=re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+',s); st=[[]]
    for t in toks:
        if t=='(': st.append([])
        elif t==')': x=st.pop(); st[-1].append(x)
        else: st[-1].append(t[1:-1].replace('\\"','"') if t.startswith('"') else t)
    return st[0][0]
def find(n,k): return [c for c in n if isinstance(c,list) and c and c[0]==k]
def val(n,k):
    f=find(n,k); return f[0][1] if f and len(f[0])>1 else None
t=parse(open(NET).read())
comps={}
for c in find(find(t,'components')[0],'comp'):
    props={val(p,'name'):(val(p,'value') or "") for p in find(c,'property')}
    comps[val(c,'ref')]=dict(value=val(c,'value'),fp=val(c,'footprint'),uuid=val(c,'tstamps'),dnp='dnp' in props,note=props.get('Note'))
pinnet={}
for n in find(find(t,'nets')[0],'net'):
    for x in find(n,'node'): pinnet[(val(x,'ref'),val(x,'pin'))]=val(n,'name')
b=pcbnew.LoadBoard(SRC)
def net(name):
    ni=b.FindNet(name)
    if ni is None: ni=pcbnew.NETINFO_ITEM(b,name); b.Add(ni)
    return ni
fps={f.GetReference():f for f in b.GetFootprints()}
sheetname,sheetfile=fps["U12"].GetSheetname(),fps["U12"].GetSheetfile()
def load(fpid):
    lib,name=fpid.split(":")
    fp=pcbnew.FootprintLoad(K+lib+".pretty",name); assert fp is not None,fpid
    fp.SetFPID(pcbnew.LIB_ID(lib,name)); return fp
def make(ref):
    c=comps[ref]; fp=load(c["fp"])
    fp.SetReference(ref); fp.SetValue(c["value"]); fp.SetPath(pcbnew.KIID_PATH("/"+c["uuid"]))
    fp.SetSheetname(sheetname); fp.SetSheetfile(sheetfile); fp.SetDNP(c["dnp"])
    if c["note"]:
        fld=pcbnew.PCB_FIELD(fp,pcbnew.FIELD_T_USER,"Note"); fld.SetText(c["note"]); fld.SetVisible(False); fld.SetLayer(pcbnew.F_Fab); fp.Add(fld)
    b.Add(fp); return fp
# ---- J4: the 2x13 in the 2x10's orientation, pin 1 at (11.0, 7.6)
old=fps["J4"]; o_path=old.GetPath(); b.Remove(old)
j4=make("J4"); j4.SetOrientationDegrees(90); j4.SetPosition(V(11.0,7.6)); j4.SetPath(o_path)
j4.Reference().SetVisible(old.Reference().IsVisible())
fps["J4"]=j4
# ---- existing parts: nets from the sheet (R39 / R41 values too)
for ref,f in fps.items():
    if ref.startswith("H"): continue
    if ref in comps and f.GetValue()!=comps[ref]["value"]:
        print("value",ref,f.GetValue(),"->",comps[ref]["value"]); f.SetValue(comps[ref]["value"])
    for p in f.Pads():
        w=pinnet.get((ref,p.GetNumber()))
        if w and w!=p.GetNetname(): p.SetNet(net(w))
for ref in ("R39","R41"):
    c=comps[ref]; f=fps[ref]
    fld=pcbnew.PCB_FIELD(f,pcbnew.FIELD_T_USER,"Note"); fld.SetText(c["note"]); fld.SetVisible(False); fld.SetLayer(pcbnew.F_Fab); f.Add(fld)
# ---- H1 down, the six 0805s out of its way
fps["H1"].SetPosition(V(4.0,15.0))
moves={"R53":(2.495,20.98),"R54":(5.245,20.98),"C24":(2.525,24.98),"R51":(5.245,24.98),"R52":(8.645,14.225),"R3":(8.645,18.475)}
for r,(x,y) in moves.items(): fps[r].SetPosition(V(x,y))
# ---- the panel-line parts
new={}
def put(ref,x,y,rot=0,bottom=False):
    f=make(ref)
    f.SetPosition(V(x,y))
    if bottom: f.Flip(f.GetPosition(),pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(rot)
    for p in f.Pads():
        n=pinnet.get((ref,p.GetNumber()))
        if n: p.SetNet(net(n))
    f.Reference().SetVisible(False)
    new[ref]=f
put("R72",20.0,15.0,90); put("R71",22.6,15.0,90)
put("D13",26.5,15.2,0); put("D12",30.6,15.2,0)
put("F1",45.9,6.4,90,True); put("TP1",43.6,10.9,0,True)
# ---- copper: the locked GND rail of J4 2-20 moves with the pins; unlocked copper ripped where parts moved
moved_lock=0
for tr in list(b.GetTracks()):
    if tr.IsLocked() and tr.GetNetname()=="GND":
        p=tr.GetPosition() if tr.Type()==pcbnew.PCB_VIA_T else tr.GetStart()
        if T(p.x)<40 and T(p.y)<6:
            tr.Move(V(-3.0,0)); moved_lock+=1
# the header's fan-out moves with it: every unlocked track end and via in the zone shifts 3 mm left
ZX0,ZX1,ZY1=7.6,45.5,12.0
def inz(p): return ZX0<=T(p.x)<=ZX1 and T(p.y)<=ZY1
sh=0
for tr in list(b.GetTracks()):
    if tr.IsLocked(): continue
    if tr.Type()==pcbnew.PCB_VIA_T:
        if inz(tr.GetPosition()): tr.SetPosition(pcbnew.VECTOR2I(tr.GetPosition().x-MM(3.0),tr.GetPosition().y)); sh+=1
    else:
        s0,e0=tr.GetStart(),tr.GetEnd()
        if inz(s0): tr.SetStart(pcbnew.VECTOR2I(s0.x-MM(3.0),s0.y)); sh+=1
        if inz(e0): tr.SetEnd(pcbnew.VECTOR2I(e0.x-MM(3.0),e0.y)); sh+=1
RIP=[]
gone=0
for tr in list(b.GetTracks()):
    if tr.IsLocked(): continue
    pts=[tr.GetPosition()] if tr.Type()==pcbnew.PCB_VIA_T else [tr.GetStart(),tr.GetEnd(),(tr.GetStart()+tr.GetEnd())/2]
    if any(x0<=T(p.x)<=x1 and y0<=T(p.y)<=y1 for p in pts for (x0,y0,x1,y1) in RIP):
        b.Remove(tr); gone+=1
print("locked GND moved",moved_lock,"shifted ends",sh,"ripped",gone)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(OUT); print("saved",OUT)

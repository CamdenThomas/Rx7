"""DCU sheet rev 0.04 (D-458, D-465): J4 2x13 with the panel's I2C, +5V and spare; R39 / R41 firm pull-downs.
Restores from orig/ first, so it is safe to re-run (then repath the board)."""
import re, uuid, shutil
S="/private/tmp/claude-501/-Users-crash-dev-Rx7/8e1ab075-e500-475a-9e35-5ee237612812/scratchpad/apply-boards/"
P="/Users/crash/dev/Rx7/02-PROJECTS/01-electrical/00-design/cad/dcu-carrier/"
for f in ("dcu-carrier.kicad_sch","dcu-carrier.kicad_sym"): shutil.copy(S+"orig/dcu-carrier/"+f,P+f)
sch=open(P+"dcu-carrier.kicad_sch").read(); sym=open(P+"dcu-carrier.kicad_sym").read()
ROOT="9652d84f-b171-4144-b035-f61cf665afb4"
U=lambda: str(uuid.uuid4())
F='(effects (font (size 1.27 1.27)))'; FH='(effects (font (size 1.27 1.27)) (hide yes))'
ST='(stroke (width 0.254) (type default))'
def lib_block(text,name):
    m=re.search(r'\t\(symbol "%s"\n.*?\n\t\)\n'%re.escape(name),text,re.S); return m
# --- Conn_02x13 from Conn_02x10
m=lib_block(sym,"Conn_02x10"); c10=m.group(0)
pins=[]
for i in range(13):
    y=round(12.7-2.54*i,2)
    for side,x,a,n in (("L",-7.62,0,2*i+1),("R",7.62,180,2*i+2)):
        pins.append(f'\t\t\t(pin passive line (at {x} {y} {a}) (length 2.54) (name "{n}" {F}) (number "{n}" {F}))')
c13=c10.replace("Conn_02x10","Conn_02x13").replace("(end 5.08 -12.7)","(end 5.08 -20.32)").replace('(at 0 -13.97 0)','(at 0 -21.59 0)')
c13=re.sub(r'(\t\t\(symbol "Conn_02x13_1_1"\n).*?(\n\t\t\))',lambda mm: mm.group(1)+"\n".join(pins)+mm.group(2),c13,flags=re.S)
sym=sym.replace(c10,c13)
# --- Polyfuse from R (same pin geometry), TestPoint
r=lib_block(sym,"R").group(0)
pf=r.replace('(symbol "R"','(symbol "Polyfuse"').replace('"R_0_1"','"Polyfuse_0_1"').replace('"R_1_1"','"Polyfuse_1_1"')
pf=re.sub(r'\(property "Reference" "R"','(property "Reference" "F"',pf).replace('(property "Value" "R"','(property "Value" "Polyfuse"')
pf=re.sub(r'(\t\t\(symbol "Polyfuse_0_1"\n)',r'\1\t\t\t(polyline (pts (xy -1.524 -2.032) (xy -1.524 -1.016) (xy 1.524 1.016) (xy 1.524 2.032)) (stroke (width 0) (type default)) (fill (type none)))\n',pf)
pf=re.sub(r'\(property "Description" "[^"]*"','(property "Description" "Resettable fuse (PTC)"',pf)
tp=f'''	(symbol "TestPoint"
		(pin_names (offset 1.016) (hide yes))
		(exclude_from_sim no) (in_bom no) (on_board yes)
		(property "Reference" "TP" (at 0 6.35 0) {F})
		(property "Value" "TestPoint" (at 0 -2.54 0) {F})
		(property "Footprint" "" (at 0 0 0) {FH})
		(property "Datasheet" "" (at 0 0 0) {FH})
		(property "Description" "Test point: a bare pad" (at 0 0 0) {FH})
		(symbol "TestPoint_0_1"
			(circle (center 0 3.302) (radius 0.762) (stroke (width 0) (type default)) (fill (type none)))
		)
		(symbol "TestPoint_1_1"
			(pin passive line (at 0 0 90) (length 2.54) (name "1" {F}) (number "1" {F}))
		)
	)
'''
i=sym.rstrip().rfind(")"); sym=sym[:i]+pf+tp+sym[i:]
def emb(d,name):
    e="".join("\t"+l if l.strip() else l for l in d.splitlines(True))
    return e.replace('\t\t(symbol "%s"\n'%name,'\t\t(symbol "dcu-carrier:%s"\n'%name,1)
e10=re.search(r'\t\t\(symbol "dcu-carrier:Conn_02x10"\n.*?\n\t\t\)\n',sch,re.S).group(0)
sch=sch.replace(e10,emb(c13,"Conn_02x13"))
m=sch.find('\n\t)\n',sch.find('(lib_symbols')); 
# append after the last lib symbol: find the end of lib_symbols block
ls=sch.find('\t(lib_symbols'); depth=0; k=ls
while True:
    ch=sch[k]
    if ch=='(': depth+=1
    elif ch==')':
        depth-=1
        if depth==0: break
    elif ch=='"':
        k=sch.find('"',k+1)
    k+=1
end=sch.rfind('\n',0,k)+1     # start of the line holding the closing paren
sch=sch[:end]+emb(pf,"Polyfuse")+emb(tp,"TestPoint")+sch[end:]
# --- J4 to 2x13
blk=re.search(r'\t\(symbol \(lib_id "dcu-carrier:Conn_02x10"\).*?\n\t\)\n',sch,re.S); j=blk.group(0)
j=j.replace('dcu-carrier:Conn_02x10','dcu-carrier:Conn_02x13').replace('"panel ribbon 2x10 IDC" (at 406.4 351.79 0)','"panel ribbon 2x13 IDC, keyed" (at 406.4 361.95 0)')
j=j.replace('IDC-Header_2x10_P2.54mm_Vertical','IDC-Header_2x13_P2.54mm_Vertical')
j=j.replace('\t\t(instances','\t\t(property "Note" "D-458: 26-way, 2 x 13 shrouded box header, keyed; pin-out panel_ribbon (21 GND, 22 PNL_SDA, 23 GND, 24 PNL_SCL, 25 SPARE, 26 +5V_PNL)" (at 406.4 337.82 0) (effects (font (size 1.1 1.1)) (hide yes)))\n'+"".join(f'\t\t(pin "{n}" (uuid "{U()}"))\n' for n in range(21,27))+'\t\t(instances',1)
sch=sch.replace(blk.group(0),j)
out=[]
def wire(x0,y0,x1,y1): return f'\t(wire (pts (xy {x0:.2f} {y0:.2f}) (xy {x1:.2f} {y1:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))\n'
GLOBAL={"GND","+3V3","+5V"}
def lab(net,x,y,ang):
    just={0:"left",180:"right",90:"left",270:"right"}[ang]
    if net in GLOBAL:
        return f'\t(global_label "{net}" (shape passive) (at {x:.2f} {y:.2f} {ang}) (effects (font (size 1.27 1.27)) (justify {just})) (uuid "{U()}"))\n'
    return f'\t(label "{net}" (at {x:.2f} {y:.2f} {ang}) (effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid "{U()}"))\n'
RIB={21:"GND",22:"PNL_SDA",23:"GND",24:"PNL_SCL",25:"SPARE",26:"+5V_PNL"}
for n,net in RIB.items():
    row=(n-1)//2; y=round(325.12+2.54*row,2)
    if n%2: out.append(wire(398.78,y,396.24,y)+lab(net,396.24,y,180))
    else: out.append(wire(414.02,y,416.56,y)+lab(net,416.56,y,0))
def place(lib,ref,val,fp,x,y,pins,note,dnp=False,inbom=True):
    s=f'''	(symbol (lib_id "dcu-carrier:{lib}") (at {x:.2f} {y:.2f} 0) (unit 1) (body_style 1)
		(exclude_from_sim no) (in_bom {"yes" if inbom else "no"}) (on_board yes) (in_pos_files yes) (dnp {"yes" if dnp else "no"})
		(uuid "{U()}")
		(property "Reference" "{ref}" (at {x+3:.2f} {y-1.2:.2f} 0) (effects (font (size 1.1 1.1)) (justify left)))
		(property "Value" "{val}" (at {x+3:.2f} {y+1.6:.2f} 0) (effects (font (size 1.1 1.1)) (justify left)))
		(property "Footprint" "{fp}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.1 1.1)) (hide yes)))
		(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.1 1.1)) (hide yes)))
		(property "Note" "{note}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.1 1.1)) (hide yes)))
'''
    for p in pins: s+=f'\t\t(pin "{p[0]}" (uuid "{U()}"))\n'
    s+=f'\t\t(instances (project "dcu-carrier" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n\t)\n'
    for num,px,py,d,net in pins:
        if d=="U": s+=wire(px,py,px,py-2.54)+lab(net,px,py-2.54,90)
        elif d=="D": s+=wire(px,py,px,py+2.54)+lab(net,px,py+2.54,270)
        elif d=="L": s+=wire(px,py,px-2.54,py)+lab(net,px-2.54,py,180)
        elif d=="R": s+=wire(px,py,px+2.54,py)+lab(net,px+2.54,py,0)
        elif d=="T": s+=lab(net,px,py,0)
    out.append(s)
def text(t,x,y,size=1.5,bold=True):
    b=" (bold yes)" if bold else ""
    out.append(f'\t(text "{t}" (exclude_from_sim no) (at {x} {y} 0) (effects (font (size {size} {size}){b}) (justify left top)) (uuid "{U()}"))\n')
Y=race=None
y0=530.86
text("PANEL RIBBON LINES (D-458) - the panel's lights on the I2C bus, J4 21-26",584,497,3.0)
for k,tl in enumerate(["The LED driver on the panel (IS31FL3236A, 0x3C) shares the bus with U12 (0x74), U13 (0x75) and U15 (0x48): R51 / R52 pull it up to +3V3 here.",
    "Each ribbon line leaves through 100 R (R71 SDA, R72 SCL): a shorted or zapped ribbon conductor cannot drag the expanders' bus or a Teensy pin beyond what the",
    "resistor allows (the driver has 8 kV HBM on its pins, the Teensy its own clamps; no room for a BAT54S by J4 - confirm). Run this bus at 100 kHz (about 1 m of ribbon) - confirm.",
    "+5V_PNL: the logic +5V through F1, a 0.5 A-hold PTC, so a short on the panel trips F1 and never browns out the Teensy (VIN on +5V). SPARE (25) ends on TP1."]):
    text(tl,585,503.5+k*3.8,1.5,False)
place("R","R71","100R","Resistor_SMD:R_0805_2012Metric",600.71,y0,[("1",600.71,y0-3.81,"U","I2C_SDA"),("2",600.71,y0+3.81,"D","PNL_SDA")],
      "D-458: series resistor, the panel's SDA leaves the board through it")
place("R","R72","100R","Resistor_SMD:R_0805_2012Metric",651.51,y0,[("1",651.51,y0-3.81,"U","I2C_SCL"),("2",651.51,y0+3.81,"D","PNL_SCL")],
      "D-458: series resistor, the panel's SCL leaves the board through it")
place("Polyfuse","F1","PTC 0.5A hold 1206 - confirm","Fuse:Fuse_1206_3216Metric",702.31,y0,[("1",702.31,y0-3.81,"U","+5V"),("2",702.31,y0+3.81,"D","+5V_PNL")],
      "D-458: the panel's +5 V (35 LEDs at 7.6 mA max + U2, about 0.28 A): 1206L050 class, 0.5 A hold / 1.0 A trip, 6 V - confirm the part and its trip time")
place("TestPoint","TP1","ribbon spare","TestPoint:TestPoint_Pad_D1.0mm",722.63,y0+2.54,[("1",722.63,y0+2.54,"T","SPARE")],
      "D-458: ribbon pin 25, unused, wired end to end",inbom=False)
out.append(f'\t(rectangle (start 580 493) (end 1040 545) (stroke (width 0.2032) (type dash)) (fill (type none)) (uuid "{U()}"))\n')
# --- D-465: the release selects' gate pull-downs, 100k -> 10k
for ref in ("R39","R41"):
    m=re.search(r'\t\(symbol \(lib_id "dcu-carrier:R"\)[^\n]*\n(?:\t\t[^\n]*\n)*?\t\t\(property "Reference" "%s".*?\n\t\)\n'%ref,sch,re.S)
    b0=m.group(0); assert b0.count('(symbol (lib_id')==1, ref
    b1=b0.replace('(property "Value" "100k"','(property "Value" "10k"')
    b1=b1.replace('\t\t(pin "1"','\t\t(property "Note" "D-465: gate pull-down, 10k gate to source: holds the release select off while the Teensy pin floats (socket empty, reset, boot, unprogrammed) and against drain-to-gate coupling when the relay coil switches; 0.33 mA from a driven pin" (at 0 0 0) (effects (font (size 1.1 1.1)) (hide yes)))\n\t\t(pin "1"',1)
    assert b1!=b0; sch=sch.replace(b0,b1)
rep=[('(rev "0.03")','(rev "0.04")')]
for o,nw in rep:
    assert o in sch; sch=sch.replace(o,nw,1)
m=sch.rfind('\t(sheet_instances'); sch=sch[:m]+"".join(out)+sch[m:]
open(P+"dcu-carrier.kicad_sch","w").write(sch); open(P+"dcu-carrier.kicad_sym","w").write(sym)
print("ok")

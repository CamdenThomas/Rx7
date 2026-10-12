"""snap.py board out.png x0 y0 x1 y1 [dpi] [layers] : a window of the board, GND pours removed unless 'pours' in argv"""
import pcbnew, sys, subprocess, os, shutil
S = os.path.dirname(os.path.abspath(__file__)) + "/../snap"
os.makedirs(S, exist_ok=True)
src, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(float, sys.argv[3:7])
dpi = int(sys.argv[7]) if len(sys.argv) > 7 and sys.argv[7].isdigit() else 300
layers = "F.Cu,B.Cu,Edge.Cuts,F.Courtyard,B.Courtyard"
for a in sys.argv[7:]:
    if "." in a and "Cu" in a or "Edge" in a: layers = a
b = pcbnew.LoadBoard(src)
if "pours" not in sys.argv:
    for z in list(b.Zones()):
        if z.GetNetname() == "GND": b.Remove(z)
b.Save(S + "/snap.kicad_pcb")
pro = os.path.splitext(src)[0] + ".kicad_pro"
if os.path.exists(pro): shutil.copy(pro, S + "/snap.kicad_pro")
subprocess.run(["kicad-cli", "pcb", "export", "pdf", "--layers", layers, "--mode-single", "-o", S + "/snap.pdf", S + "/snap.kicad_pcb"],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# page origin: find the page size; board origin assumed at page origin (0,0)
k = dpi / 25.4
subprocess.run(["pdftoppm", "-r", str(dpi), "-x", str(int(x0 * k)), "-y", str(int(y0 * k)), "-W", str(int((x1 - x0) * k)), "-H", str(int((y1 - y0) * k)),
                "-png", S + "/snap.pdf", S + "/img"])
for f in os.listdir(S):
    if f.startswith("img") and f.endswith(".png"):
        shutil.move(S + "/" + f, out)
print("wrote", out)

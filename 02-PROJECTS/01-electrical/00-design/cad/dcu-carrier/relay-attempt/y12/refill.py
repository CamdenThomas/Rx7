"""refill.py dir/dcu-carrier.kicad_pcb : refill every zone with the PROJECT's net classes in force and save in place.
The board must sit beside its own dcu-carrier.kicad_pro: a board loaded under another name has no project, every net
is then class Default, and the GND pours are filled 0.3 mm from the COMFORT / PGND copper instead of 0.5 mm.
pcbnew rewrites the .kicad_pro on save, so the project file is copied aside first and put back afterwards."""
import pcbnew, sys, os, shutil, json
brd = sys.argv[1]
pro = os.path.splitext(brd)[0] + ".kicad_pro"
keep = pro + ".keep"
shutil.copy(pro, keep)
b = pcbnew.LoadBoard(brd)
ns = b.GetDesignSettings().m_NetSettings
cl = {n: pcbnew.ToMM(ns.GetEffectiveNetClass(n).GetClearance()) for n in ("GND", "PGND", "/CMF_RTN", "/V12C_RAW", "+5V", "/ROW1")}
print("clearances in force", cl)
assert cl["PGND"] > 0.45 and cl["/CMF_RTN"] > 0.45, "project net classes not loaded"
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(brd)
shutil.copy(keep, pro); os.remove(keep)
d = json.load(open(pro))
print("project classes after save", [c["name"] for c in d["net_settings"]["classes"]])

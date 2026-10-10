#!/bin/zsh
# snap.sh board.kicad_pcb out.png  : the top-left 63 x 35 mm, F.Cu red, B.Cu blue (pours hidden)
S=/private/tmp/claude-501/-Users-crash-dev-Rx7/8e1ab075-e500-475a-9e35-5ee237612812/scratchpad/apply-boards/dcu
P=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
$P -c "
import pcbnew,sys
b=pcbnew.LoadBoard('$1')
for z in list(b.Zones()):
    if z.GetNetname()=='GND': b.Remove(z)
b.Save('$S/snap.kicad_pcb')" 2>/dev/null
cp $S/w/b1.kicad_pro $S/snap.kicad_pro
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb export pdf --layers F.Cu,B.Cu,Edge.Cuts,F.Courtyard,B.Courtyard --mode-single -o $S/snap.pdf $S/snap.kicad_pcb >/dev/null 2>&1
pdftoppm -r 400 -x 0 -y 0 -W ${3:-1000} -H ${4:-560} -png $S/snap.pdf $S/snapimg
mv $S/snapimg-1.png $2

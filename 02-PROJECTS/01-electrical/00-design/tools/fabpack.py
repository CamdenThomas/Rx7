#!/usr/bin/env python3
"""fabpack.py BOARD.kicad_pcb  - plot one board's fab package (Y42, kept in the tree since Y44) into the fab/ folder beside it
(cad/<board>/fab/: only what the board house needs; the assembly drawings and the fab BOM are in the part's
diagrams/ and data/),
as bench revision A was plotted (Y17; the options were found by re-plotting the untouched upper
board and the panel until every file matched but its date lines), and write the zip whole.

  kicad-cli pcb export gerbers --no-x2 --no-netlist --subtract-soldermask
      --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,Edge.Cuts
  kicad-cli pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2
  <board>-revA-gerbers.zip = the fourteen files, flat
"""
import os
import shutil
import subprocess
import sys
import zipfile

CLI = os.environ.get("KICAD_CLI") or shutil.which("kicad-cli") or "/opt/homebrew/bin/kicad-cli"
LAYERS = "F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,Edge.Cuts"
FILES = ["-B_Cu.gbl", "-B_Mask.gbs", "-B_Paste.gbp", "-B_Silkscreen.gbo", "-Edge_Cuts.gm1", "-F_Cu.gtl",
         "-F_Mask.gts", "-F_Paste.gtp", "-F_Silkscreen.gto", "-NPTH-drl_map.gbr", "-PTH-drl_map.gbr",
         "-job.gbrjob", "-NPTH.drl", "-PTH.drl"]


def main():
    pcb = os.path.abspath(sys.argv[1])
    name = os.path.basename(pcb)[: -len(".kicad_pcb")]
    fab = os.path.join(os.path.dirname(pcb), "fab")
    assert os.path.isdir(fab), fab
    for cmd in ([CLI, "pcb", "export", "gerbers", "--no-x2", "--no-netlist", "--subtract-soldermask",
                 "--layers", LAYERS, "-o", fab + "/", pcb],
                [CLI, "pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th",
                 "--generate-map", "--map-format", "gerberx2", "-o", fab + "/", pcb]):
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert r.returncode == 0, (cmd, r.stderr[-400:])
    z = os.path.join(fab, name + "-revA-gerbers.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as out:
        for suffix in FILES:
            p = os.path.join(fab, name + suffix)
            assert os.path.getmtime(p) >= os.path.getmtime(pcb), p + " is older than the board"
            out.write(p, name + suffix)
    with zipfile.ZipFile(z) as chk:
        assert chk.testzip() is None and len(chk.namelist()) == len(FILES)
    print("%s: %d files, %d bytes" % (os.path.relpath(z), len(FILES), os.path.getsize(z)))


main()

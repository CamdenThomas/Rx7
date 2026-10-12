"""frrun.py base.kicad_pcb tag NET,NET.. [passes] : one freerouting round on `base` for the named nets.
DSN (dsn_prep.py) -> freerouting 2.5.0 headless -> the session's wires for those nets merged back onto `base`
(ses_merge.py) -> necks widened -> saved as <work>/dcu-carrier.kicad_pcb and <work>/<tag>.kicad_pcb -> DRC summary.
Paths: this file's folder holds the scripts; ../fr holds the jar and userdata; ../w is the work project folder."""
import subprocess, sys, os, shutil, re
S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(S)
KP = "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
JAVA = "/opt/homebrew/opt/openjdk/bin/java"
JAR = ROOT + "/fr/freerouting-2.5.0.jar"
UD = ROOT + "/fr/userdata"
W = ROOT + "/w"
base, tag, nets = sys.argv[1:4]
passes = sys.argv[4] if len(sys.argv) > 4 else "100"
d = ROOT + "/fr/" + tag
os.makedirs(d, exist_ok=True)


def run(cmd, quiet=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "assert" not in l and "memory leak" not in l)
    return r.returncode, out


rc, out = run([KP, S + "/dsn_prep.py", base, d + "/in.dsn", nets]); print(out)
rc, out = run([JAVA, "-Djava.awt.headless=true", "-jar", JAR, "--user_data_path=" + UD, "--gui.enabled=false", "-de", d + "/in.dsn", "-do", d + "/out.ses",
               "-mp", passes, "--router.fanout.enabled=false", "--router.optimizer.enabled=false"])
open(d + "/out.txt", "w").write(out)
for l in out.splitlines():
    if "unrouted connection" in l or "Auto-routing stage completed" in l:
        print(re.sub(r"^\S+ \S+ INFO\s+\[\S+\]\s*", "", l)[:150])
rc, out = run([KP, S + "/ses_merge.py", base, d + "/out.ses", W + "/" + tag + "-m.kicad_pcb", nets]); print(out)
rc, out = run([KP, S + "/widen.py", W + "/" + tag + "-m.kicad_pcb", W + "/" + tag + ".kicad_pcb", "0.25"]); print(out)
os.remove(W + "/" + tag + "-m.kicad_pcb")
shutil.copy(W + "/" + tag + ".kicad_pcb", W + "/dcu-carrier.kicad_pcb")
rc, out = run(["python3", S + "/drc.py", W + "/dcu-carrier.kicad_pcb", "-u"])
print("\n".join(l[:200] for l in out.splitlines() if "track_dangling |" not in l and "via_dangling |" not in l))

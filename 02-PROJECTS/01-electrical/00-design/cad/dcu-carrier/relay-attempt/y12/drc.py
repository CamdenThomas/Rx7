"""drc.py board.kicad_pcb [-u] [-q] : run kicad-cli DRC (all severities, parity), summarise. -u lists unconnected, -q hides violations."""
import json, subprocess, sys, collections, os
brd = sys.argv[1]
out = os.path.splitext(brd)[0] + "-drc.json"
r = subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--schematic-parity", "--format", "json", "-o", out, brd], capture_output=True, text=True)
d = json.load(open(out))
c = collections.Counter((v['type'], v['severity']) for v in d['violations'])
print("violations", len(d['violations']), dict(c))
print('unconnected', len(d['unconnected_items']), 'parity', len(d.get('schematic_parity', [])))
def desc(v):
    return ' || '.join(i['description'][:60] + ' @%.2f,%.2f' % (i['pos']['x'], i['pos']['y']) for i in v['items'])
if "-q" not in sys.argv:
    for v in d['violations']:
        print(' ', v['type'], '|', v['description'][:70], '|', desc(v))
for v in d.get('schematic_parity', []):
    print('  PARITY', v['description'][:150], '|', desc(v))
if "-u" in sys.argv:
    nets = collections.Counter()
    for v in d['unconnected_items']:
        print('  UNC', desc(v))

import csv, re, statistics, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import B, S, OUT, PARTS, T
import rows_node, rows_legs, rows_mod  # noqa: F401

IDS = ['E13', 'E14', 'E15', 'E16', 'E17', 'E18', 'E19', 'E20', 'E21', 'E22', 'E23', 'F3', 'F5', 'F6']
BH = ['id', 'goal', 'where', 'time', 'tools', 'parts', 'before', 'know', 'done_when', 'if_not', 'record']
SH = ['id', 'work', 'n', 'do', 'how', 'expect', 'caution']

with open(OUT + 'briefs.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, lineterminator='\n')
    w.writerow(BH)
    for i in IDS:
        b = B[i]
        w.writerow([i] + [b.get(k, '') for k in BH[1:]])
with open(OUT + 'steps.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, lineterminator='\n')
    w.writerow(SH)
    for i in IDS:
        for n, (do, how, expect, caution) in enumerate(S[i], 1):
            w.writerow(['%s.%02d' % (i, n), i, n, do, how, expect, caution])

# ---------------- validate, from the files as written
bad = []
br = list(csv.DictReader(open(OUT + 'briefs.csv', encoding='utf-8')))
st = list(csv.DictReader(open(OUT + 'steps.csv', encoding='utf-8')))
if [r['id'] for r in br] != IDS:
    bad.append('briefs ids differ from the list')
RETIRED = [r['term'] for r in T('retired')]
for r in br:
    for k in ('goal', 'done_when'):
        if not r[k].strip():
            bad.append('%s: empty %s' % (r['id'], k))
    for p in r['parts'].split():
        if p not in PARTS:
            bad.append('%s: part %s does not exist' % (r['id'], p))
    for ln in r['know'].split('\n'):
        if not re.search(r'\[[^\]]+\]$', ln.strip()):
            bad.append('%s: know line without a source: %s' % (r['id'], ln[:60]))
by = {}
for r in st:
    if r['work'] not in IDS:
        bad.append('step %s: work not in list' % r['id'])
    if not r['do'].strip():
        bad.append('step %s: empty do' % r['id'])
    by.setdefault(r['work'], []).append(r)
for i in IDS:
    rows = by.get(i, [])
    if [int(r['n']) for r in rows] != list(range(1, len(rows) + 1)):
        bad.append('%s: n has gaps' % i)
    for r in rows:
        if r['id'] != '%s.%02d' % (i, int(r['n'])):
            bad.append('%s: id mismatch' % r['id'])
    if not rows:
        bad.append('%s: no steps' % i)
for rows, name in ((br, 'briefs'), (st, 'steps')):
    for r in rows:
        for k, v in r.items():
            if re.search(r'(?<![\w-])cad/', v):
                bad.append('%s %s.%s: cites cad/' % (name, r['id'], k))
            for t in RETIRED:
                if t in v:
                    bad.append('%s %s.%s: retired term %r' % (name, r['id'], k, t))
            if '\r' in v:
                bad.append('%s %s.%s: CR' % (name, r['id'], k))
            for p in re.findall(r'\bP\d{3}\b', v):
                if p not in PARTS:
                    bad.append('%s %s.%s: names part %s which does not exist' % (name, r['id'], k, p))
counts = [len(by[i]) for i in IDS]
print('rows', len(br), 'steps', len(st), 'per row', dict(zip(IDS, counts)))
print('min / median / max', min(counts), statistics.median(counts), max(counts))
print('bytes', os.path.getsize(OUT + 'briefs.csv'), os.path.getsize(OUT + 'steps.csv'))
print('longest how', max(len(r['how']) for r in st), [r['id'] for r in st if len(r['how']) > 4000])
print('PROBLEMS', len(bad))
for b in bad:
    print(' ', b)
sys.exit(1 if bad else 0)

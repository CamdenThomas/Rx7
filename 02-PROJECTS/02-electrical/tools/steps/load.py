"""Load one group's draft briefs.csv / steps.csv into 02-electrical (replacing any rows for the same work ids), then check."""
import re, csv, subprocess, sys, os
S=sys.argv[1].rstrip('/')+'/'; g=S  # the folder holding the builder's briefs.csv and steps.csv
E='02-PROJECTS/02-electrical/data/'
BH=['id','goal','where','time','tools','parts','before','know','done_when','if_not','record']; SH=['id','work','n','do','how','expect','caution']
def rd(p): return list(csv.DictReader(open(p,newline='',encoding='utf-8')))
nb=rd(S+'briefs.csv'); ns=rd(S+'steps.csv')
assert list(nb[0].keys())==BH and list(ns[0].keys())==SH, (list(nb[0].keys()), list(ns[0].keys()))
work={r['id']:r for r in rd(E+'work.csv')}; parts={r['id'] for r in rd(E+'parts.csv')}
ids={r['id'] for r in nb}
bad=[i for i in ids if i not in work]; assert not bad, bad
for r in nb:
    r['parts']=' '.join(p for p in r['parts'].replace(',',' ').split())
    miss=[p for p in r['parts'].split() if p not in parts]; assert not miss,(r['id'],miss)
    assert r['goal'].strip() and r['done_when'].strip(), r['id']
for r in ns: assert r['work'] in ids and r['do'].strip(), r['id']
for t in nb+ns:
    for k,v in t.items(): assert not re.search(r'(?<!03-)cad/', v), (t['id'],k)   # an old cad/ path; 03-cad is the project (D-572)
ob=[r for r in rd(E+'briefs.csv') if r['id'] not in ids]; os_=[r for r in rd(E+'steps.csv') if r['work'] not in ids]
def wr(p,h,rows):
    with open(p,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=h,lineterminator='\n'); w.writeheader(); w.writerows(rows)
wr(E+'briefs.csv',BH,ob+nb); wr(E+'steps.csv',SH,os_+ns)
r=subprocess.run([sys.executable,'tools/rx7.py','check'],capture_output=True,text=True)
print(g,'briefs',len(nb),'steps',len(ns),'| check',r.returncode); print(r.stdout.strip()[-1200:])
sys.exit(r.returncode)

import json,re,sys
d=json.load(open(sys.argv[1])); out=[]
for u in d['unconnected_items']:
    for it in u['items']:
        m=re.search(r'\[([^\]]+)\]',it['description'])
        if m and m.group(1)!='GND' and m.group(1) not in out: out.append(m.group(1))
print(','.join(out))

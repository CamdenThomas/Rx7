import json,collections,sys
d=json.load(open(sys.argv[1]))
c=collections.Counter((v['type'],v['severity']) for v in d['violations'])
print(dict(c)); print('unconnected',len(d['unconnected_items']),'parity',len(d.get('schematic_parity',[])))
skip=set(sys.argv[2].split(',')) if len(sys.argv)>2 else set()
for v in d['violations']:
  if v['type'] in skip: continue
  print(' ',v['type'],v['description'][:90],'|',' || '.join(i['description'][:55]+' @%.2f,%.2f'%(i['pos']['x'],i['pos']['y']) for i in v['items']))

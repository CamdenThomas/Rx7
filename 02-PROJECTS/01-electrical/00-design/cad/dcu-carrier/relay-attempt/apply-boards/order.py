import json,re,sys
d=json.load(open(sys.argv[1])); out=[]
for u in d['unconnected_items']:
    for it in u['items']:
        m=re.search(r'\[([^\]]+)\]',it['description'])
        if m and m.group(1)!='GND' and m.group(1) not in out: out.append(m.group(1))
J4=["/ROW1","/ROW2","/ROW3","/COL1","/COL2","/COL3","/ENC_FAN_A","/ENC_FAN_B","/ENC_TEMP_A","/ENC_TEMP_B","/ENC_SEAT_DRV_A","/ENC_SEAT_DRV_B","/ENC_SEAT_PASS_A","/ENC_SEAT_PASS_B","/JOY_X","/JOY_Y","/JOY_PRESS"]
out=[n for n in J4 if n in out]+[n for n in out if n not in J4]
print(','.join(out))

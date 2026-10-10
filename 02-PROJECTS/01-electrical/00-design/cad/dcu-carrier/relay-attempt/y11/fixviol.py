"""remove unlocked tracks/vias named in DRC error violations. argv: in drc.json out [types]"""
import pcbnew, sys, json
b=pcbnew.LoadBoard(sys.argv[1]); d=json.load(open(sys.argv[2]))
types=set(sys.argv[4].split(',')) if len(sys.argv)>4 else {'shorting_items','clearance','tracks_crossing','hole_clearance','solder_mask_bridge','copper_edge_clearance','hole_to_hole'}
ids=set()
for v in d['violations']:
    if v['severity']=='error' and v['type'] in types:
        for it in v['items']:
            if it['description'].startswith(('Track','Via','Arc')): ids.add(it['uuid'])
rm=[t for t in list(b.GetTracks()) if not t.IsLocked() and t.m_Uuid.AsString() in ids]
for t in rm: b.Remove(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[3]); print('removed',len(rm))

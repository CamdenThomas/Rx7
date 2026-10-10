import pcbnew, sys
b=pcbnew.LoadBoard(sys.argv[1])
ok=pcbnew.ExportSpecctraDSN(b, sys.argv[2]); print('export',ok)
# the comfort pour outlines, for keepouts
with open(sys.argv[3],'w') as f:
  for z in b.Zones():
    if z.GetIsRuleArea(): continue
    o=z.Outline(); pts=[(pcbnew.ToMM(o.CVertex(i).x),pcbnew.ToMM(o.CVertex(i).y)) for i in range(o.TotalVertices())]
    f.write(z.GetLayerName()+';'+z.GetNetname()+';'+' '.join('%.3f,%.3f'%p for p in pts)+'\n')

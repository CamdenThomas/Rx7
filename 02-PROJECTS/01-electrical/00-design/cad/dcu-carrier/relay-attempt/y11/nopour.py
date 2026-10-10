import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1])
zs=[b.GetArea(i) for i in range(b.GetAreaCount())]
zs=[z for z in zs if not z.GetIsRuleArea() and z.GetNetname()=='GND']
for z in zs: b.Remove(z)
b.Save(sys.argv[2]); print('removed',len(zs))

import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1])
for z in b.Zones():
    if z.GetNetname()=="GND": print(z.GetZoneName(), z.GetIslandRemovalMode()); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2])

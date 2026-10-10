"""rip every unlocked track and via, and my own locked hand copper (kept: the Y11 locked power copper). argv: in out locked_uuids_file"""
import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1])
keep=set(open(sys.argv[3]).read().split())
n=k=0
for t in list(b.GetTracks()):
    if t.IsLocked() and t.m_Uuid.AsString() in keep: k+=1; continue
    b.Remove(t); n+=1
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("ripped",n,"kept",k)

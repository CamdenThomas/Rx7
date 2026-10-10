import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1]);T=pcbnew.ToMM
for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
    bb=f.GetCourtyard(pcbnew.F_CrtYd).BBox() if f.GetCourtyard(pcbnew.F_CrtYd).OutlineCount() else f.GetBoundingBox(False)
    print(f.GetReference(),f.GetFPID().GetLibItemName(),'%.2f,%.2f'%(T(f.GetPosition().x),T(f.GetPosition().y)),f.GetOrientationDegrees(),'L' if f.GetLayer()==pcbnew.F_Cu else 'B','bb %.1f %.1f %.1f %.1f'%(T(bb.GetLeft()),T(bb.GetTop()),T(bb.GetRight()),T(bb.GetBottom())), 'locked' if f.IsLocked() else '')
for z in b.Zones():
    bb=z.GetBoundingBox(); print('ZONE',z.GetZoneName(),z.GetNetname(),z.GetLayerName(),z.GetAssignedPriority(),'%.1f %.1f %.1f %.1f'%(T(bb.GetLeft()),T(bb.GetTop()),T(bb.GetRight()),T(bb.GetBottom())), z.GetIsRuleArea())
tr=[t for t in b.GetTracks()]
print('tracks',sum(1 for t in tr if t.Type()==pcbnew.PCB_TRACE_T),'vias',sum(1 for t in tr if t.Type()==pcbnew.PCB_VIA_T),'locked',sum(1 for t in tr if t.IsLocked()))
for r in ('J9','J2'):
    f=b.FindFootprintByReference(r)
    for p in f.Pads(): print(r,p.GetNumber(),'%.2f,%.2f'%(T(p.GetPosition().x),T(p.GetPosition().y)),p.GetNetname())
ns=b.GetNetClasses() if hasattr(b,'GetNetClasses') else None

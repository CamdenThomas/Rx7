import pcbnew
b=pcbnew.LoadBoard('w/src.kicad_pcb'); T=pcbnew.ToMM
for f in b.GetFootprints():
    r=f.Reference()
    if f.GetReference() in ('R26','R27','C24','R51','U12','D6','R58','C20','U9','R21','J3'):
        print(f.GetReference(), r.IsVisible(), r.GetLayerName(), '%.2f,%.2f'%(T(r.GetPosition().x)-T(f.GetPosition().x),T(r.GetPosition().y)-T(f.GetPosition().y)), T(r.GetTextHeight()), r.GetTextAngleDegrees())

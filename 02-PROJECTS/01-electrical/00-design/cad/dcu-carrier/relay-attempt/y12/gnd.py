"""gnd.py board [out.kicad_pcb] : the GND pours' connectivity. Every filled fragment of the two GND pours, every GND
pad, via and track is a node; nodes touch when they share a layer and overlap. Prints each group that is not part of
the biggest one (fragment bbox / area, the pads and vias in it). With an output name it also stitches: for every such
group it looks for a spot where one of the group's fragments and a main-group fragment on the OTHER layer both have
room for a 0.6 / 0.3 via (0.35 mm inside each fill, 0.6 mm from every hole) and adds the via there, refills, and
repeats until no group is left or nothing can be added. Exit 0 one group, 2 fragments left."""
import pcbnew, sys, math
MM = pcbnew.FromMM; T = pcbnew.ToMM
F, B = pcbnew.F_Cu, pcbnew.B_Cu
src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else None
K = int(sys.argv[3]) if len(sys.argv) > 3 else 1      # stitch vias per isolated group (spread at least 4 mm apart)
b = pcbnew.LoadBoard(src)
gnd = b.FindNet("GND").GetNetCode()


def analyse():
    nodes = []      # (kind, layers, obj, label)
    for z in b.Zones():
        if z.GetNetCode() != gnd or z.GetIsRuleArea(): continue
        for L in (F, B):
            if not z.IsOnLayer(L): continue
            ps = z.GetFilledPolysList(L)
            for i in range(ps.OutlineCount()):
                s = pcbnew.SHAPE_POLY_SET(); s.AddOutline(ps.Outline(i))
                for h in range(ps.HoleCount(i)): s.AddHole(ps.Hole(i, h))
                bb = ps.Outline(i).BBox()
                nodes.append(("zone", {L}, s, "%s %.1f,%.1f..%.1f,%.1f %.1f mm2" % ("F" if L == F else "B", T(bb.GetX()), T(bb.GetY()), T(bb.GetRight()), T(bb.GetBottom()), s.Area() / 1e12)))
    for t in b.GetTracks():
        if t.GetNetCode() != gnd: continue
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition(); nodes.append(("via", {F, B}, t, "via %.2f,%.2f" % (T(p.x), T(p.y))))
        else:
            p = t.GetStart(); nodes.append(("trk", {t.GetLayer()}, t, "trk %.2f,%.2f" % (T(p.x), T(p.y))))
    for p in b.GetPads():
        if p.GetNetCode() != gnd: continue
        Ls = {L for L in (F, B) if p.IsOnLayer(L)}
        q = p.GetPosition()
        nodes.append(("pad", Ls, p, "%s.%s %.2f,%.2f" % (p.GetParentFootprint().GetReference(), p.GetNumber(), T(q.x), T(q.y))))
    n = len(nodes); par = list(range(n))

    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    zi = [i for i in range(n) if nodes[i][0] == "zone"]
    oi = [i for i in range(n) if nodes[i][0] != "zone"]
    for i in oi:
        k, Ls, o, _ = nodes[i]
        for L in Ls:
            sh = o.GetEffectiveShape(L)
            for j in zi:
                if L not in nodes[j][1]: continue
                zs = nodes[j][2]
                bb = zs.BBox(); c = o.GetBoundingBox().GetCenter()
                if not bb.Contains(c) and not bb.Intersects(o.GetBoundingBox()): continue
                if zs.Collide(sh, 0): par[f(i)] = f(j)
    for a in range(len(oi)):
        for c in range(a + 1, len(oi)):
            i, j = oi[a], oi[c]
            if not nodes[i][2].GetBoundingBox().Intersects(nodes[j][2].GetBoundingBox()): continue
            for L in nodes[i][1] & nodes[j][1]:
                if nodes[i][2].GetEffectiveShape(L).Collide(nodes[j][2].GetEffectiveShape(L), 0):
                    par[f(i)] = f(j); break
    g = {}
    for i in range(n): g.setdefault(f(i), []).append(i)
    groups = sorted(g.values(), key=len, reverse=True)
    return nodes, groups


def holes():
    hs = [(T(p.GetPosition().x), T(p.GetPosition().y), T(max(p.GetDrillSize().x, p.GetDrillSize().y)) / 2) for p in b.GetPads() if p.GetDrillSize().x > 0]
    hs += [(T(t.GetPosition().x), T(t.GetPosition().y), T(t.GetDrillValue()) / 2) for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    return hs


for rnd in range(6):
    nodes, groups = analyse()
    main = set(groups[0])
    print("round", rnd, "groups", len(groups), "main", len(groups[0]))
    for grp in groups[1:]:
        print("  ISOLATED:", " | ".join(nodes[i][3] for i in grp)[:400])
    if len(groups) == 1 or not dst: break
    hs = holes()
    cores = {}
    for i in main:
        if nodes[i][0] == "zone":
            L = next(iter(nodes[i][1])); c = nodes[i][2].CloneDropTriangulation(); c.Inflate(-MM(0.35), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.01))
            cores.setdefault(L, []).append(c)
    added = 0
    for grp in groups[1:]:
        cand = []
        for i in grp:
            if nodes[i][0] != "zone": continue
            L = next(iter(nodes[i][1])); other = B if L == F else F
            core = nodes[i][2].CloneDropTriangulation(); core.Inflate(-MM(0.35), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.01))
            if core.OutlineCount() == 0: continue
            bb = core.BBox(); x0, y0, x1, y1 = T(bb.GetX()), T(bb.GetY()), T(bb.GetRight()), T(bb.GetBottom())
            y = y0
            while y <= y1:
                x = x0
                while x <= x1:
                    pt = pcbnew.VECTOR2I(MM(x), MM(y))
                    if core.Contains(pt) and any(c.Contains(pt) for c in cores.get(other, [])) and all(math.hypot(x - hx, y - hy) > hr + 0.15 + 0.3 + 0.05 for hx, hy, hr in hs):
                        cand.append((x, y))
                    x += 0.25
                y += 0.25
        chosen = []
        for x, y in cand:
            if len(chosen) >= K: break
            if all(math.hypot(x - cx, y - cy) >= 4.0 for cx, cy in chosen): chosen.append((x, y))
        for x, y in chosen:
            v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetLayerPair(F, B); v.SetNetCode(gnd); b.Add(v); hs.append((x, y, 0.15)); added += 1
            print("  stitch via at %.2f,%.2f" % (x, y))
        if not chosen: print("  no spot for group:", nodes[grp[0]][3])
    if not added: break
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
if dst:
    pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(dst)
nodes, groups = analyse()
print("final groups", len(groups))
sys.exit(0 if len(groups) == 1 else 2)

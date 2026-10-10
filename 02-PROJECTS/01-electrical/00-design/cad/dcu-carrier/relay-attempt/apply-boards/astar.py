"""Route the connections the autorouter left, net by net, with a raster A* on both layers.
argv: in.kicad_pcb out.kicad_pcb NET[,NET...] [width]
Obstacles: every pad, track, via and non-GND zone fill not on the net, inflated by the larger of the
two netclass clearances plus half the track width plus a margin; the GND pours are ignored (they are
refilled afterwards and give way). Each net's copper is split into islands; the smallest island is
joined to the rest, repeatedly, until one island is left or no path exists."""
import pcbnew, sys, math, heapq
from PIL import Image, ImageDraw, ImageFilter

MM = pcbnew.FromMM; T = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
NETS = sys.argv[3].split(",")
EXACT = len(sys.argv) > 4 and sys.argv[4].startswith('=')
TW0 = TW = float(sys.argv[4].lstrip('=')) if len(sys.argv) > 4 else 0.25
R = float(sys.argv[5]) if len(sys.argv) > 5 else 0.1   # grid, mm
W, H = 180.0, 80.0
NX, NY = int(W / R) + 1, int(H / R) + 1
LAY = (pcbnew.F_Cu, pcbnew.B_Cu)
MARGIN = float(sys.argv[6]) if len(sys.argv) > 6 else 1.3 * R
VIA_D, VIA_DR = 0.6, 0.3

ds = b.GetDesignSettings()


_clr = {}


def clr_of(item):
    n = item.GetNetname()
    if n not in _clr:
        try:
            _clr[n] = T(b.GetDesignSettings().m_NetSettings.GetEffectiveNetClass(n).GetClearance()) if n else 0.2
        except Exception:
            _clr[n] = 0.2
    return _clr[n]


def P(x, y):
    return (x / R, y / R)


tracks = list(b.GetTracks())
fps = list(b.GetFootprints())
pads = [p for f in fps for p in f.Pads()]
zones = [b.GetArea(i) for i in range(b.GetAreaCount())]


def poly_pts(o):
    return [P(T(o.CPoint(k).x), T(o.CPoint(k).y)) for k in range(o.PointCount())]


def draw_item(dr, it, L, infl):
    """draw an item's copper on layer L, grown by infl mm."""
    if isinstance(it, pcbnew.PAD):
        if not it.IsOnLayer(L) and it.GetDrillSize().x == 0:
            return
        if it.IsOnLayer(L):
            ps = it.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE).CloneDropTriangulation() if hasattr(it, "GetEffectivePolygon") else None
            if ps is not None:
                ps.Inflate(MM(infl), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.01))
                for i in range(ps.OutlineCount()):
                    dr.polygon(poly_pts(ps.Outline(i)), fill=255)
        d = it.GetDrillSize()
        if d.x > 0:                       # a hole blocks both layers
            x, y = T(it.GetPosition().x), T(it.GetPosition().y); r = T(max(d.x, d.y)) / 2 + infl
            dr.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=255)
    elif it.Type() == pcbnew.PCB_VIA_T:
        x, y = T(it.GetPosition().x), T(it.GetPosition().y); r = T(it.GetWidth(L)) / 2 + infl
        dr.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=255)
    else:
        if it.GetLayer() != L:
            return
        w = T(it.GetWidth()) + 2 * infl
        a, c = it.GetStart(), it.GetEnd()
        pa, pc = P(T(a.x), T(a.y)), P(T(c.x), T(c.y))
        dr.line([pa, pc], fill=255, width=max(1, int(round(w / R))))
        r = w / 2
        for q in (a, c):
            x, y = T(q.x), T(q.y)
            dr.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=255)


def lanes(dr, group, L):
    """escape lanes: each SMD pad of the group extended 0.8 mm outward along its long axis."""
    for it in group:
        if not isinstance(it, pcbnew.PAD) or not it.IsOnLayer(L) or it.GetDrillSize().x > 0:
            continue
        fp = it.GetParentFootprint(); fc = fp.GetPosition(); c = it.GetPosition()
        bb = it.GetBoundingBox(); w, hh = T(bb.GetWidth()), T(bb.GetHeight())
        cx, cy = T(c.x), T(c.y)
        if w >= hh:
            s = 1 if cx >= T(fc.x) else -1; ex, ey = cx + s * (w / 2 + 0.8), cy; lw = hh
        else:
            s = 1 if cy >= T(fc.y) else -1; ex, ey = cx, cy + s * (hh / 2 + 0.8); lw = w
        dr.line([P(cx, cy), P(ex, ey)], fill=255, width=1)
        if w >= hh:
            dr.line([P(cx - w / 2 + 0.05, cy), P(cx + w / 2 - 0.05, cy)], fill=255, width=1)
        else:
            dr.line([P(cx, cy - hh / 2 + 0.05), P(cx, cy + hh / 2 - 0.05)], fill=255, width=1)


def islands(netcode):
    items = [p for p in pads if p.GetNetCode() == netcode] + [t for t in tracks if t.GetNetCode() == netcode]
    n = len(items); par = list(range(n))

    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            a, c = items[i], items[j]
            for L in LAY:
                if a.IsOnLayer(L) and c.IsOnLayer(L):
                    try:
                        if a.GetEffectiveShape(L).Collide(c.GetEffectiveShape(L), 0):
                            par[f(i)] = f(j); break
                    except Exception:
                        pass
    groups = {}
    for i in range(n):
        groups.setdefault(f(i), []).append(items[i])
    return sorted(groups.values(), key=len)


def anchors(group):
    out = []
    for it in group:
        for L in LAY:
            if not it.IsOnLayer(L):
                continue
            if isinstance(it, pcbnew.PAD) or it.Type() == pcbnew.PCB_VIA_T:
                out.append((L, T(it.GetPosition().x), T(it.GetPosition().y)))
            else:
                a, c = it.GetStart(), it.GetEnd()
                for k in range(0, 11):
                    out.append((L, T(a.x) + (T(c.x) - T(a.x)) * k / 10, T(a.y) + (T(c.y) - T(a.y)) * k / 10))
    return out


total_added = 0
for name in NETS:
    ni = b.FindNet(name)
    if ni is None:
        print("no net", name); continue
    nc = ni.GetNetCode()
    myclr = 0.2
    for it in tracks + pads:
        if it.GetNetCode() == nc:
            myclr = max(myclr, clr_of(it))
            break
    try:
        ncl = b.GetDesignSettings().m_NetSettings.GetEffectiveNetClass(name)
        TW = TW0 if EXACT else max(TW0, T(ncl.GetTrackWidth())); myclr = max(myclr, T(ncl.GetClearance()))
    except Exception as e:
        print("netclass?", e); TW = TW0
    print(name, "width", TW, "clearance", myclr)
    for attempt in range(8):
        tracks = list(b.GetTracks())
        grp = islands(nc)
        if len(grp) < 2:
            print(name, "connected"); break
        src = grp[0]; dst = [it for g in grp[1:] for it in g]
        # obstacle rasters
        obs = {}; viaobs = {}; pobs = {}
        for L in LAY:
            imP = Image.new("L", (NX, NY), 0); drP = ImageDraw.Draw(imP)
            im = Image.new("L", (NX, NY), 0); dr = ImageDraw.Draw(im)
            for it in pads + tracks:
                if it.GetNetCode() == nc and it.GetNetCode() != 0:
                    continue
                infl = max(myclr, clr_of(it) if it.GetNetCode() else 0.2) + TW / 2 + MARGIN
                draw_item(drP if isinstance(it, pcbnew.PAD) else dr, it, L, infl)
            for z in zones:
                if z.GetIsRuleArea() or z.GetNetCode() == nc or not z.IsOnLayer(L) or z.GetNetname() == "GND":
                    continue
                ps = z.GetFilledPolysList(L).CloneDropTriangulation()
                ps.Inflate(MM(max(myclr, T(z.GetLocalClearance() or 0)) + TW / 2 + MARGIN), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.01))
                for i in range(ps.OutlineCount()):
                    dr.polygon(poly_pts(ps.Outline(i)), fill=255)
            e = 0.5 + TW / 2
            dr.rectangle([P(0, 0), P(W, e)], fill=255); dr.rectangle([P(0, H - e), P(W, H)], fill=255)
            dr.rectangle([P(0, 0), P(e, H)], fill=255); dr.rectangle([P(W - e, 0), P(W, H)], fill=255)
            obs[L] = im.tobytes(); pobs[L] = imP.tobytes()
            both = Image.new("L", (NX, NY), 0); both.paste(255, mask=im); both.paste(255, mask=imP)
            k = int(round((VIA_D / 2 - TW / 2) / R)) * 2 + 1
            viaobs[L] = both.filter(ImageFilter.MaxFilter(k)).tobytes() if k > 1 else both.tobytes()
        # drill-to-drill: every hole blocks a via within its radius + 0.25 + via drill radius
        im = Image.new("L", (NX, NY), 0); dr = ImageDraw.Draw(im)
        for it in tracks:
            if it.Type() == pcbnew.PCB_VIA_T:
                x, y = T(it.GetPosition().x), T(it.GetPosition().y); r = T(it.GetDrillValue()) / 2 + 0.25 + VIA_DR / 2 + 0.05
                dr.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=255)
        for p in pads:
            d = p.GetDrillSize()
            if d.x > 0:
                x, y = T(p.GetPosition().x), T(p.GetPosition().y); r = T(max(d.x, d.y)) / 2 + 0.25 + VIA_DR / 2 + 0.05
                dr.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=255)
        holes = im.tobytes()
        # target raster
        tgt = {}
        for L in LAY:
            im = Image.new("L", (NX, NY), 0); dr = ImageDraw.Draw(im)
            for it in dst:
                draw_item(dr, it, L, -0.05 if isinstance(it, pcbnew.PAD) else 0.0)
            tgt[L] = im.tobytes()
        srcr = {}
        for L in LAY:
            im = Image.new("L", (NX, NY), 0); dr = ImageDraw.Draw(im)
            for it in src:
                draw_item(dr, it, L, -(TW / 2 + 0.03) if isinstance(it, pcbnew.PAD) else 0.0)
            lanes(dr, src, L); lanes(dr, dst, L)
            srcr[L] = im.tobytes()
        tpts = [(x, y) for L, x, y in anchors(dst)]
        tx0, tx1 = min(x for x, _ in tpts), max(x for x, _ in tpts)
        ty0, ty1 = min(y for _, y in tpts), max(y for _, y in tpts)

        def h(i, j):
            x, y = i * R, j * R
            dx = max(tx0 - x, 0, x - tx1); dy = max(ty0 - y, 0, y - ty1)
            return math.hypot(dx, dy)
        start = []
        for L, x, y in anchors(src):
            i, j = int(round(x / R)), int(round(y / R))
            li = LAY.index(L)
            start.append((li, i, j))
        dist = {}; prev = {}; pq = []
        for s in start:
            dist[s] = 0.0; heapq.heappush(pq, (h(s[1], s[2]), 0.0, s))
        VIACOST = 3.0
        found = None; nexp = 0
        nb = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
        while pq:
            f_, g, n = heapq.heappop(pq)
            if g > dist.get(n, 1e18):
                continue
            li, i, j = n
            if g > 0 and tgt[LAY[li]][j * NX + i]:
                found = n; break
            nexp += 1
            if nexp > 4000000:
                break
            o = obs[LAY[li]]; po = pobs[LAY[li]]; tg = tgt[LAY[li]]; sr = srcr[LAY[li]]
            for di, dj, c in nb:
                ii, jj = i + di, j + dj
                if not (0 <= ii < NX and 0 <= jj < NY):
                    continue
                kk = jj * NX + ii
                if o[kk] or (po[kk] and not tg[kk] and not sr[kk]):
                    continue
                m = (li, ii, jj); ng = g + c * R
                if ng < dist.get(m, 1e18):
                    dist[m] = ng; prev[m] = n; heapq.heappush(pq, (ng + h(ii, jj), ng, m))
            ol = 1 - li
            if not viaobs[LAY[0]][j * NX + i] and not viaobs[LAY[1]][j * NX + i] and not holes[j * NX + i]:
                m = (ol, i, j); ng = g + VIACOST
                if ng < dist.get(m, 1e18):
                    dist[m] = ng; prev[m] = n; heapq.heappush(pq, (ng + h(i, j), ng, m))
        if not found:
            print(name, "no path from island of", len(src), "items; expanded", nexp); break
        path = [found]
        while path[-1] in prev:
            path.append(prev[path[-1]])
        path.reverse()
        # emit straight runs per layer, vias at layer changes
        runs = []; cur = [path[0]]
        for n in path[1:]:
            if n[0] != cur[-1][0]:
                runs.append(cur); cur = [n]
            else:
                cur.append(n)
        runs.append(cur)
        added = 0
        for r_ in runs:
            L = LAY[r_[0][0]]
            pts = [(i * R, j * R) for _, i, j in r_]
            o = obs[L]; po = pobs[L]; okr = (tgt[L], srcr[L])

            def free(x, y):
                i, j = int(round(x / R)), int(round(y / R))
                k = j * NX + i
                return not o[k] and (not po[k] or okr[0][k] or okr[1][k])

            def inpad(x, y):
                i, j = int(round(x / R)), int(round(y / R))
                return po[j * NX + i]

            def visible(a, c):
                d = math.hypot(c[0] - a[0], c[1] - a[1]); n = max(1, int(d / 0.02))
                axis = abs(c[0] - a[0]) < 1e-6 or abs(c[1] - a[1]) < 1e-6
                for s in range(n + 1):
                    x, y = a[0] + (c[0] - a[0]) * s / n, a[1] + (c[1] - a[1]) * s / n
                    if not free(x, y) or (not axis and inpad(x, y)):
                        return False
                return True
            simp = [pts[0]]; k = 0
            while k < len(pts) - 1:
                best = k + 1
                for m in range(len(pts) - 1, k, -1):
                    if visible(pts[k], pts[m]):
                        best = m; break
                simp.append(pts[best]); k = best
            for a, c in zip(simp, simp[1:]):
                if a == c:
                    continue
                t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
                t.SetWidth(MM(TW)); t.SetLayer(L); t.SetNetCode(nc); b.Add(t); added += 1
        for a, c in zip(runs, runs[1:]):
            _, i, j = c[0]
            v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(i * R), MM(j * R))); v.SetWidth(MM(VIA_D)); v.SetDrill(MM(VIA_DR))
            v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNetCode(nc); b.Add(v)
        total_added += added
        print(name, "joined an island:", len(path), "cells,", len(runs) - 1, "vias,", added, "segments, expanded", nexp)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[2])
print("segments added", total_added)

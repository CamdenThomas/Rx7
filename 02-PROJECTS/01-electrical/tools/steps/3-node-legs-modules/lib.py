"""Helpers for the g3 briefs/steps drafts: read the record's CSVs, format lists from them.
Nothing here writes under data/. Every list a step carries is built from the tables' own rows."""
import csv, re, os

D = os.path.dirname(os.path.abspath(__file__)).split('/02-PROJECTS/')[0] + '/02-PROJECTS/01-electrical/data/'
OUT = os.path.dirname(os.path.abspath(__file__)) + '/'


def T(name):
    return list(csv.DictReader(open(D + name + '.csv', encoding='utf-8')))


CAV = T('cavities'); HOU = {r['code']: r for r in T('housings')}; PINS = T('pins')
ROUTES = {r['id']: r for r in T('routes')}; DEV = T('devices'); GND = T('grounds')
NC = {r['id']: r for r in T('node_conductors')}; REL = T('relays'); FUS = T('fuses')
WS = T('wake_stages'); LAD = T('ladders'); PARTS = {r['id'] for r in T('parts')}
CH2PIN = {r['ch']: r['pin'] for r in PINS if r['ch']}

B = {}
S = {}


def brief(i, **kw):
    for k in ('tools', 'before', 'know'):
        if isinstance(kw.get(k), (list, tuple)):
            kw[k] = '\n'.join(kw[k])
    B[i] = kw


def step(i, do, how='', expect='', caution=''):
    if isinstance(how, (list, tuple)):
        how = '\n'.join(how)
    S.setdefault(i, []).append((do, how, expect, caution))


def short(s, n=170):
    s = s.replace('<br>', '; ').strip()
    if len(s) <= n:
        return s
    cut = s[:n]
    return cut[:cut.rfind(' ')] + ' …'


def wire(r):
    if r['colour'] == 'shielded':
        return 'shielded cable, 16 AWG core (P074)'
    return '%s %s AWG' % (r['colour'], r['awg'])


def cavs(h):
    return sorted([r for r in CAV if r['housing'] == h], key=lambda r: int(r['cav']))


def plugsize(h):
    return '12' if HOU[h]['leg_side'].startswith('DTP') else '16'


def leg_lines(h):
    """The leg-side plug of housing h, one cavity per line."""
    out = []
    for r in cavs(h):
        c = r['cav']
        if r['state'] == 'PLUG':
            out.append('%s · sealing plug, size %s' % (c, plugsize(h)))
        elif r['state'] == 'RESERVED' and HOU[h]['where'] == 'Dash post':
            out.append('%s · sealing plug, size %s, in this plug - RESERVED: %s is pinned on the receptacle only'
                       % (c, plugsize(h), r['circuit']))
        else:
            st = '' if r['state'] == 'LIVE' else ' · ' + r['state']
            out.append('%s · %s · %s%s → %s' % (c, r['circuit'], wire(r), st, short(r['lands_on'])))
    return out


NODE_SRC = {
    'L1-S1 2': 'F15 inline (7.5 A) off the O12 splice (N19)',
    'L1-S1 3': 'across the node to DP-ICU-B 1 (N46)',
    'L1-S1 4': 'across the node to DP-ICU-B 2, with the 100 Ω 1 W pull-up to pin 15 and the tap to pin 32, A7 (N47, N39, N45)',
    'L1-S1 6': 'shielded, across the node to DP-ICU-B 4; the shield to the GND bus at this end only (N48)',
    'L1-S1 11': 'PMU pin 17, A4',
    'L1-S2 1': 'across the node to DP-ICU-B 6, joined there with L3-S2 11 (N50)',
    'L1-S2 7': 'PMU pin 31, A5',
    'L1-S2 8': 'across the node to DP-ICU-B 5 (N49)',
    'L1-S2 9': 'fuse block B, the spare position F5, no fuse fitted (N68)',
    'L1-S2 11': 'across the node to DP-ICU-B 9 (N67)',
    'L2-P 3': 'the O1 splice, 12 AWG (N105)',
    'L2-P 4': 'K1 terminal 87a (N14)',
    'L2-M 4': 'K12 terminal 87 (N27)',
    'L2-M 8': 'fuse block A, position F13, no fuse (N79)',
    'L2-S 1': 'K1 terminal 87 (N12)',
    'L2-S 2': 'K2 terminal 87 (N13)',
    'L2-S 3': 'PMU pin 30, A3 - one splice with L3-S1 5 and L2-S 4 (N42)',
    'L2-S 4': 'PMU pin 30, A3 - the same splice as L2-S 3 (N42)',
    'L2-S 5': 'across the node to DP-DCU 2 (N77)',
    'L2-S 6': 'K2 terminal 87a (N15)',
    'L2-R 1': 'a capped, labelled tail at the node for the radar receiver (housings L2-R)',
    'L2-R 2': 'a capped, labelled tail at the node, as cavity 1',
    'L2-R 3': 'a capped, labelled tail at the node, as cavity 1',
    'L3-M 2': 'fuse block B, F1 (N31)',
    'L3-S1 5': 'PMU pin 30, A3 - one splice with L2-S 3 and L2-S 4 (N42)',
    'L3-S1 6': 'PMU pin 19, A8 - one splice with L3-S1 11, and the A8 wake stage (N43)',
    'L3-S1 7': 'wake strip input 6 (N63)',
    'L3-S1 8': 'PMU pin 34, O20 - one splice with DP-ICU-A 2 (N22)',
    'L3-S1 9': 'K2 terminal 85 (N11)',
    'L3-S1 10': 'K1 terminal 85 (N10)',
    'L3-S1 11': 'PMU pin 19, A8 - the same splice as L3-S1 6 (N43)',
    'L3-S1 12': 'wake strip input 1, ACC (N33)',
    'L3-S2 1': 'wake strip input 2, RUN (N34), with the branch to K13 terminal 86 (N71)',
    'L3-S2 2': 'fuse block A, F3 (N29)',
    'L3-S2 7': 'fuse block A, position F13, no fuse (N79)',
    'L3-S2 8': 'GND bus (N59)',
    'L3-S2 9': 'K12 terminal 85 (N25)',
    'L3-S2 10': 'fuse block A, F19 (N30)',
    'L3-S2 11': 'across the node to DP-ICU-B 6 (N50), with the capped tap for the head unit (N104)',
    'L3-S2 12': 'F21 inline (5 A) off the O12 splice (N78)',
    'L3-S3 1': 'linked at the post to L4-S 5 (N81)',
    'L3-S3 2': 'linked at the post to L4-S 6 (N81)',
    'L3-S3 3': 'linked at the post to L4-S 7 (N81)',
    'L3-S3 4': 'linked at the post to L4-S2 7 (N82)',
    'L4-P 2': 'K13 terminal 87 (N70)',
    'L4-P 3': 'the O1 splice (N16)',
    'L4-P 4': 'DP-DCU-B 9 on the DCU tail, 14 AWG RED into this size-12 pin (N84)',
    'L4-M 3': 'K3 terminal 87 (N88)',
    'L4-M 4': 'K4 terminal 87 (N89)',
    'L4-M 8': 'F12 inline (5 A) from the busbar (N21)',
    'L4-M 9': 'DP-DCU-B 1 on the DCU tail (N80)',
    'L4-M 10': 'DP-DCU-B 2 on the DCU tail (N80)',
    'L4-M 11': 'DP-DCU-B 3 on the DCU tail (N80)',
    'L4-M 12': 'DP-DCU-B 4 on the DCU tail (N80)',
    'L4-S 1': 'across the node to DP-ICU-B 3 (N64)',
    'L4-S 2': 'PMU pin 18, A6, and the door wake stage (N44)',
    'L4-S 3': 'across the node to DP-ICU-B 8 (N66)',
    'L4-S 4': 'the O10 tap, PMU pin 4 (N73)',
    'L4-S 5': 'linked at the post to L3-S3 1 (N81)',
    'L4-S 6': 'linked at the post to L3-S3 2 (N81)',
    'L4-S 7': 'linked at the post to L3-S3 3 (N81)',
    'L4-S 8': 'fuse block A, F19 (N30)',
    'L4-S2 1': 'DP-DCU-B 5 on the DCU tail (N83)',
    'L4-S2 2': 'DP-DCU-B 6 on the DCU tail (N83)',
    'L4-S2 3': 'DP-DCU-B 8 on the DCU tail, spliced to L4-S2 3 and 5 both (N83)',
    'L4-S2 4': 'DP-DCU-B 7 on the DCU tail (N83)',
    'L4-S2 5': 'DP-DCU-B 8, the same splice as L4-S2 3 (N83)',
    'L4-S2 7': 'linked at the post to L3-S3 4 (N82)',
}


def node_src(r):
    if r['id'] in NODE_SRC:
        return NODE_SRC[r['id']]
    s = r['src']
    if s in CH2PIN:
        return 'PMU pin %s, %s' % (CH2PIN[s], s)
    return s or 'see the node conductors'


def node_lines(h):
    """The node-side receptacle of post housing h, one cavity per line."""
    out = []
    for r in cavs(h):
        if r['state'] == 'PLUG':
            out.append('%s · sealing plug, size %s' % (r['cav'], plugsize(h)))
        else:
            st = '' if r['state'] == 'LIVE' else ' · ' + r['state']
            out.append('%s · %s · %s%s ← %s' % (r['cav'], r['circuit'], wire(r), st, node_src(r)))
    return out


# ---- routes: a cavity's run from the post -------------------------------------------------
CHAIN = {'Nose splice': 'RT06', 'Engine-bay junction': 'RT01', 'Rear node': 'RT15', 'Centre stack': 'RT11'}
CAVROUTE = {}
for r in CAV:
    if r['route']:
        CAVROUTE.setdefault(r['id'], set()).add(r['route'])
for d in DEV:
    if not d['route'] or not d['zone'].startswith('L'):
        continue
    for m in re.finditer(r'\b(L\d-[A-Z0-9]+) (\d+)', d['terminals']):
        if m.group(1).startswith(d['zone']):
            CAVROUTE.setdefault('%s %s' % (m.group(1), m.group(2)), set()).add(d['route'])


def chain(rt):
    r = ROUTES[rt]
    pre = CHAIN.get(r['from_node'])
    return ([pre] if pre and pre != rt else []) + [rt]


def route_text(rt):
    r = ROUTES[rt]
    if r['ft']:
        ln = 'measured %s ft, cut %.1f ft' % (r['ft'], 1.5 * float(r['ft']))
    elif r['model_ft']:
        ln = 'NOT measured - confirm (the 3D model guesses %s ft: planning only, never a cut length)' % r['model_ft']
    else:
        ln = 'NOT measured - confirm'
    return '%s %s → %s, %s: %s' % (rt, r['from_node'], r['to_node'], r['via'], ln)


def cut_groups(housings):
    """Cut list grouped by the run from the post: {chain tuple: [cavity lines]}; and the unmapped."""
    g, miss = {}, []
    for h in housings:
        for r in cavs(h):
            if r['state'] in ('PLUG',) or (r['state'] == 'RESERVED' and HOU[h]['where'] == 'Dash post'):
                continue
            rts = sorted(CAVROUTE.get(r['id'], []))
            if not rts:
                miss.append(r['id']); continue
            for rt in rts:
                g.setdefault(tuple(chain(rt)), []).append('%s %s · %s' % (r['id'], r['circuit'], wire(r)))
    return g, miss


def cut_lines(housings, extra_miss=''):
    g, miss = cut_groups(housings)
    out = []
    for ch in sorted(g):
        out.append('RUN ' + ' + '.join(ch) + ':')
        out += ['  ' + x for x in g[ch]]
    if miss:
        out.append('NO ROUTE IN THE RECORD for: ' + ', '.join(miss) + extra_miss)
    return out


def routes_used(housings):
    g, _ = cut_groups(housings)
    seen = []
    for ch in sorted(g):
        for rt in ch:
            if rt not in seen:
                seen.append(rt)
    return [route_text(rt) for rt in seen]


def ground_lines(zones, skip=()):
    out = []
    for r in GND:
        if r['zone'] in zones and r['id'] not in skip:
            out.append('%s · %s · %s AWG BLK · x%s · %s ft hand estimate - confirm' % (r['id'], r['return'], r['awg'], r['qty'], r['ft']))
    return out


def nc_lines(ids, note=False):
    out = []
    for i in ids:
        r = NC[i]
        ln = '%s · %s → %s · %s AWG %s' % (i, r['src'], r['dst'], r['awg'], r['colour'])
        if note and r['note']:
            ln += ' · ' + short(r['note'], 140)
        out.append(ln)
    return out


def relay_lines(loc):
    out = []
    for r in REL:
        if r['location'].startswith(loc):
            out.append('%s %s · 86 ← %s · 85 → %s · 30 ← %s · 87 → %s%s' % (
                r['id'], r['label'], short(r['c86'], 70), short(r['c85'], 60), short(r['c30'], 70), short(r['c87'], 70),
                (' · 87a → ' + short(r['c87a'], 60)) if r['c87a'] and r['c87a'] != '—' else ''))
    return out


def fuse_lines(pred):
    out = []
    for r in FUS:
        if pred(r):
            out.append('%s · %s · %s · %s · label %s' % (r['id'], r['rating'] or 'no fuse', short(r['location'], 80), r['state'], r['label']))
    return out


def ws_lines(side):
    return ['%s · %s%s · %s → %s' % (r['id'], r['part'], (' ' + r['value']) if r['value'] else '', r['from'], r['to']) for r in WS if r['side'] == side]


def ladder(inp):
    return ' · '.join('%s %s' % (r['state'], r['r']) for r in LAD if r['input'] == inp)

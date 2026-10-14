# -*- coding: utf-8 -*-
"""Builds g2/briefs.csv and g2/steps.csv (drafts for D-533 / Y31). Reads the record, writes only here."""
import csv, os, re, statistics, sys

DATA = os.path.dirname(os.path.abspath(__file__)).split('/02-PROJECTS/')[0] + '/02-PROJECTS/01-electrical/data'
OUT = os.path.dirname(os.path.abspath(__file__))
MINE = ['A0', 'A1', 'A2', 'A6', 'B1', 'C2', 'D1', 'D2', 'D3', 'D4', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10',
        'E11', 'E12', 'E42', 'E43', 'E44', 'E45', 'E46', 'E47']


def table(name):
    with open(os.path.join(DATA, name + '.csv'), encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


PARTS = {r['id']: r for r in table('parts')}
CARTS = {r['store']: r for r in table('carts')}
FUSES = table('fuses')
RELAYS = table('relays')
FOUR = ['Waytek', 'WireBarn', 'DeutschConnector.com', 'Amazon']


def L(*lines):
    return '\n'.join(lines)


def short(text, n=62):
    text = text.split(' — ')[0].strip()
    if len(text) <= n:
        return text
    return text[:n].rsplit(' ', 1)[0] + '...'


def q(r):
    return (r['qty'] + (' ' + r['unit'] if r['unit'] and r['unit'] != 'ea' else '')).strip()


def sku(r):
    s = r['sku']
    return ' (' + s + ')' if s and len(s) <= 22 and 'confirm' not in s else ''


def rows(store, statuses=None, section=None, ids=None):
    out = []
    for r in PARTS.values():
        if ids is not None:
            if r['id'] in ids:
                out.append(r)
            continue
        if r['store'] != store:
            continue
        if statuses and r['status'] not in statuses:
            continue
        if section and section not in r['section']:
            continue
        out.append(r)
    return sorted(out, key=lambda r: int(r['id'][1:]))


def gap(r):
    """One cart-gap line for A1, from the row's own qty, target and status."""
    head = r['id'] + ' ' + short(r['item']) + sku(r) + ': '
    st, qty, tgt = r['status'], r['qty'], r['target']
    if st == 'raise':
        return head + 'cart has ' + q(r) + ', target ' + tgt
    if st == 'hold':
        return head + 'on hold, qty ' + q(r)
    if qty in ('0', '') and tgt:
        return head + 'add ' + tgt
    if qty in ('0', '') and not tgt:
        return head + 'add - the row sets no quantity (its used_for reads: ' + short(r['used_for'], 40) + ')'
    if tgt and tgt != qty:
        return head + 'add - the row says ' + q(r) + ', the car needs ' + tgt
    return head + 'add ' + q(r)


def cnt(r):
    """One count line for D1."""
    none = r['qty'] in ('0', '') and not r['target']
    s = r['id'] + ' ' + short(r['item'], 54) + sku(r) + ': ' + ('quantity not set in the row' if none else q(r))
    if r['target'] and r['target'] != r['qty']:
        s += ' (target ' + r['target'] + ')'
    return s


def join(rs, f):
    return ' · '.join(f(r) for r in rs)


LIVE = ('cart', 'raise', 'to add', 'hold')
four_ids = [r['id'] for s in FOUR for r in rows(s, LIVE) if r['id'] != 'P188']
veh_ids = ['P085', 'P086', 'P113']
total = round(sum(float(CARTS[s]['total_usd']) for s in FOUR), 2)
nstat = {s: {st: len(rows(s, (st,))) for st in ('cart', 'raise', 'to add', 'hold')} for s in FOUR}
amazon_est = round(sum(float(r['qty'] or 0) * float(r['unit_usd'] or 0) for r in rows('Amazon', LIVE) if r['id'] != 'P188'), 2)
amazon_unpriced = [r['id'] for r in rows('Amazon', LIVE) if not r['unit_usd']]
veh_est = round(sum(float(PARTS[i]['qty'] or 0) * float(PARTS[i]['unit_usd'] or 0) for i in veh_ids), 2)

briefs, steps = [], []


def B(id, goal, where, time, tools, parts, before, know, done_when, if_not, record):
    briefs.append(dict(id=id, goal=goal, where=where, time=time, tools=tools, parts=parts, before=before,
                       know=know, done_when=done_when, if_not=if_not, record=record))


def S(work, *items):
    for n, it in enumerate(items, 1):
        it = tuple(it) + ('',) * (4 - len(it))
        steps.append(dict(id='%s.%02d' % (work, n), work=work, n=n, do=it[0], how=it[1], expect=it[2], caution=it[3]))


TODAY = '2026-10-13'
STRIP = ('Strip length: not in the record. Take it from the sheet that comes with the contact or the crimper, '
         'strip so the bare strands fill the barrel and no copper shows behind it, and write the length down.')

# ---------------------------------------------------------------- A1
B('A1',
  'Every line in the four carts matches its parts row: each "raise" line at its target, each "to add" line in '
  'its cart, each "confirm" part number read on the seller\'s page - and nothing is paid yet.',
  'desk', '2 to 3 h - confirm',
  L('Laptop with the four store carts open', 'The app\'s parts list beside it'),
  ' '.join(r['id'] for s in FOUR for r in rows(s, ('raise', 'to add', 'hold'))) + ' P190 P191',
  L('The freeze (Z2) is answered: the project is at SOURCING',
    'No block is open that changes a line in a cart',
    'The stud threads are measured (CK24, taken on the strip day) so the lug hole sizes are known'),
  L('Nothing is bought until the design is complete and you understand it; no store is paid while any block that changes a line is open [D-323]',
    'This row only edits the carts. Paying is A0, after A6 has checked the heavy cable [work A0]',
    'A row\'s status says what to do: cart = in the cart at the right quantity; raise = change the line to the row\'s target; to add = not in the cart yet; hold = read the part number on the seller\'s page first [parts status, target]',
    'Lines to change, counted from the rows on %s: Waytek %d raise; WireBarn %d raise and %d to add; DeutschConnector.com %d raise and %d to add; Amazon %d raise, %d to add and %d on hold [parts, counted by sql]' % (
        TODAY, nstat['Waytek']['raise'], nstat['WireBarn']['raise'], nstat['WireBarn']['to add'],
        nstat['DeutschConnector.com']['raise'], nstat['DeutschConnector.com']['to add'],
        nstat['Amazon']['raise'], nstat['Amazon']['to add'], nstat['Amazon']['hold']),
    'The gaps were once estimated at about 332 USD on top of the carts; rows added since make it larger - an estimate, confirm at the carts [params gaps_est_usd]',
    'WireBarn showed "Hello, Guest" at the review: sign in before checkout or the cart is lost [carts WireBarn]',
    'The DeutschConnector.com total must be re-read once the cart is edited [carts DeutschConnector.com]',
    'Lug hole sizes (P064, P065, P098) and the ring-terminal mix (P079) are confirm until CK24 has measured the studs [parts P064, P098, P079; checks CK24]',
    'Wire footage is a hand estimate until the routes are measured (M-2): the targets are 1.5 x the estimated runs [parts P009, P015; work G13]',
    'P188, the amplifier\'s MRBF fuse, stays on hold: it is bought with the amplifier pick, not now [parts P188]',
    'P034 and P035 (two dust caps) drop to 0; P083 is not bought; P137 is folded into P002 [parts P034, P035, P083, P137]',
    'The MAXI fuses (P190, P191) are a local purchase, not a cart line; the blade fuses are in your drawer [parts P190, P191, P141]'),
  'Each of the four carts shows every row of that store at its target quantity, every "confirm" part number has been read on the seller\'s page, the four new totals are written down, and nothing is paid.',
  'A part number that cannot be found, or a listing that does not match its row\'s spec: do not substitute. Leave the line out, raise it in the app as a note, and do not tick - that line holds A0.',
  'Tick the row. Put the four new cart totals in a note in the app: the carts table is re-read from them.')
S('A1',
  ('Open the parts list beside the four carts',
   'In the app open 01-electrical, Parts, grouped by store. Work one store at a time: Waytek, WireBarn, DeutschConnector.com, Amazon. In the lists below "cart has" is what the cart holds today and "target" is what the line must end at; "add" lines are not in the cart yet. Where an add line gives two numbers, buy what the car needs unless the row\'s own number is a pack size.',
   'Four carts open and signed in; the parts list beside them.',
   'Do not press checkout in any store: paying is A0.'),
  ('Waytek: change the three raise lines',
   join(rows('Waytek', ('raise',)), gap) + '. P002 is thirteen sealed inline fuse holders (F12, F15, F16, F20, F21, F22, F23, F24, F33, F37 at the dash node; F8, F9, F14 at the sill). P007 is two covered busbars, the always-hot bar and the ground bus: confirm Waytek\'s own number for the Blue Sea 2300 with cover. P009 stays one 500 ft spool: its extra 50 ft is P163 at WireBarn.',
   'Three lines changed; the other %d Waytek lines untouched.' % nstat['Waytek']['cart']),
  ('Waytek: read the two socket notes',
   'P005 (Chief 75340, the start relay K9\'s socket): its terminals 30 and 87 carry 10 AWG - confirm on the listing that the terminals take 10 AWG. P006 (75290 micro relay socket, 13 of them): K11\'s terminals 30 and 87 carry 10 AWG - confirm the gauge of the five terminals bundled with each socket; if they stop at 12 AWG add two 10-12 AWG terminals of the same series.',
   'Both listings read; any extra terminals added.'),
  ('WireBarn: sign in, then change and add lines',
   'Sign in first. ' + join(rows('WireBarn', ('raise', 'to add')), gap) + '. All GXL by the foot.',
   'Two lines raised and four added; the cart still there after signing in.',
   'A guest cart is lost at checkout: sign in before editing.'),
  ('DeutschConnector.com: set every kit line to its target',
   'A kit is one housing, its wedgelock (the coloured lock that holds the contacts in) and a solid contact per cavity. ' + join(rows('DeutschConnector.com', ('raise',), 'Assembly kits'), gap) + '. Plug kits are DT06 / DTP06 (the leg side), receptacle kits DT04 / DTP04 (the panel side).',
   'Every kit line equals its target; two lines go down (P126 to 5, P128 to 1).'),
  ('DeutschConnector.com: contacts, sealing plugs, clips and caps',
   join(rows('DeutschConnector.com', ('raise',), 'Contacts'), gap) + '. Then add: ' + join(rows('DeutschConnector.com', ('to add',)), gap) + '.',
   'P024 at 21 and P025 at 18 (the kit contacts do not take 14 AWG); P028 at 89; P030 at 18; P034 and P035 removed.',
   'P102, P125, P140, P162 and P205 carry "confirm" on their part number: read the listing against the row before adding.'),
  ('Amazon: heavy cable, lugs, terminals and boots',
   join(rows('Amazon', None, None, ('P061', 'P062', 'P063', 'P065', 'P066', 'P096', 'P097', 'P098', 'P094', 'P095')), gap) + '. The cart\'s 45 ft of 2 AWG red still counts a starter run that moved to 1/0: it goes DOWN to 30 ft.',
   'Four cable lines at 30 ft red 2 AWG, 10 ft black 2 AWG, 30 ft red 1/0, 35 ft black 1/0; 6 AWG at 10 ft.',
   'Lug hole sizes are confirm until CK24: check each lug line\'s hole against the stud sizes you measured.'),
  ('Amazon: read the three held part numbers',
   'P049 master disconnect: Blue Sea 9003e (e-Series, 350 A continuous, 1500 A cranking) - NOT the 9004e; confirm the part number and price. P052 MRBF fuse 250 A for the Blue Sea 5191 holder: confirm the part number. P188 (the amplifier\'s fuse): leave out, it waits for the amplifier.',
   'P049 and P052 in the cart with the part numbers read; P188 not in the cart.'),
  ('Amazon: add the remaining "to add" lines',
   join([r for r in rows('Amazon', ('to add',)) if r['id'] not in ('P096', 'P097', 'P098', 'P094', 'P095')], gap) + '. And raise: ' + gap(PARTS['P075']) + '.',
   'Every Amazon "to add" row has a line in the cart.',
   'P136 (the load-dump TVS), P158, P172 and P189 say confirm: read the row\'s spec against the listing before adding.'),
  ('Amazon: read the specs that say confirm on lines already carted',
   'P053 must be the Blue Sea 7720 MIDI / AMI block (NOT the 5006, a MAXI block). P054 is Blue Sea 5250, 30 A (the cart once held 5253, a 60 A). P055 is Blue Sea 5256, 100 A (the cart once held 5258, a 150 A). P074 shielded cable: the inner conductor\'s insulation must be 1.35 to 3.05 mm outside diameter to seal in a Deutsch size-16 cavity - read it on the product page.',
   'Four listings read and matching their rows.',
   'A 150 A MIDI on the 6 AWG alternator cable would not protect it: the 100 A (5256) is the one.'),
  ('Write the local list',
   'Not cart lines: ' + join(rows('Local', ('to add',)), cnt) + ' - from a parts store. Blade fuses (P141) are in your drawer.',
   'Two lines on a paper or phone list for the next parts-store trip.'),
  ('Write down each cart\'s new total and stop',
   'Read the total each store now shows. Do not pay. Put the four totals in a note in the app.',
   'Four totals noted; no order placed.'),
  ('Tick the row', 'Tick A1 in the app. A6 (the heavy-cable listing check) is next, then A0 pays.', 'A1 done; A6 ready.'))

# ---------------------------------------------------------------- A6
B('A6',
  'Every heavy-cable line in the Amazon cart, 2 AWG and 1/0 alike, states insulation rated 90 °C or higher and 100 % copper, or has been swapped for one that does.',
  'desk', '20 min',
  L('Laptop with the Amazon cart open'),
  'P061 P062 P096 P097',
  L('A1 is done: the cable lines are at their target lengths',
    'Nothing is paid yet'),
  L('The cable is accepted at the cart on two criteria: the listing must state 90 °C or higher insulation and 100 % copper [D-238]',
    'CCA - copper-clad aluminium - is refused at any price [D-238]',
    'If a listing does not state both, the line is swapped before payment, not after [D-238; work A6]',
    'The four lines: P061 2 AWG red, P062 2 AWG black, P096 1/0 red, P097 1/0 black - fine-strand welding cable, TEMCo class [parts P061, P062, P096, P097]',
    'What each carries: 2 AWG red is the PMU feed C03, the Class-T link C01 and the busbar link C10; 2 AWG black is the engine-to-chassis strap C06; 1/0 red is the starter feed C04 and the post-to-disconnect link C12; 1/0 black is the battery negative C05 and the cranking return C11 [parts P061, P062, P096, P097]',
    'The row names 2 AWG and 1/0 only; the 6 AWG alternator cable P063 is "any SGX / welding" and is outside its wording [work A6; parts P063]',
    'The wire table\'s bundle figures are a hand derating, to be checked against the insulation rating when the cable is chosen here [awg amp_bundle note]'),
  'All four listings state both 90 °C or higher and 100 % copper in their own text, at the lengths A1 set.',
  'A listing that is silent on either, or says CCA: remove it and add a listing that states both, same gauge, colour and length. If none can be found, raise it in the app as a note and do not tick.',
  'Tick the row. If a line was swapped, note the new listing in the app.')
S('A6',
  ('Open the Amazon cart at the four cable lines', 'Find P061, P062, P096 and P097 in the cart; open each product page in its own tab.', 'Four product pages open.'),
  ('Read the 2 AWG red listing (P061)', 'Look in the title, bullets and specification table for two statements: an insulation temperature of 90 °C or more (105 °C passes), and 100 % copper (or "pure copper"). Length 30 ft.', 'Both statements found in the listing\'s own text.', 'A listing that says CCA or "copper clad" fails whatever else it says.'),
  ('Read the 2 AWG black listing (P062)', 'Same two statements. Length 10 ft.', 'Both statements found.'),
  ('Read the 1/0 red listing (P096)', 'Same two statements. Length 30 ft.', 'Both statements found.'),
  ('Read the 1/0 black listing (P097)', 'Same two statements. Length 35 ft.', 'Both statements found.'),
  ('Swap any line that fails', 'Remove the failing line and add one that states both, same gauge, colour and length. Do it now, before A0 pays.', 'Four lines, each stating both criteria.'),
  ('Tick the row', 'Tick A6 in the app. A0 is ready when A1 and A6 are both ticked.', 'A6 done.'))

# ---------------------------------------------------------------- A0
B('A0',
  'The four carts - Waytek, WireBarn, DeutschConnector.com and Amazon - are paid, each matching the parts table line for line.',
  'desk', '1 h - confirm',
  L('Laptop with the four carts open', 'Payment card'),
  ' '.join(four_ids),
  L('A1 is ticked: every cart line is at its target',
    'A6 is ticked: the four heavy-cable listings state 90 °C or higher and 100 % copper',
    'No block is open that changes a line'),
  L('This is the single largest money step of the project [work A0]',
    'No store is paid while any block that changes a line is open [D-323]',
    'Store figures in the carts table on %s, taken before A1\'s changes: Waytek %s USD (%s) · WireBarn %s USD (%s) · DeutschConnector.com %s USD (%s) · Amazon %s USD (%s) [carts]' % (
        TODAY, CARTS['Waytek']['total_usd'], CARTS['Waytek']['lines_txt'], CARTS['WireBarn']['total_usd'],
        CARTS['WireBarn']['lines_txt'], CARTS['DeutschConnector.com']['total_usd'],
        CARTS['DeutschConnector.com']['lines_txt'], CARTS['Amazon']['total_usd'], CARTS['Amazon']['lines_txt']),
    'Those four figures add up to %.2f USD as of today\'s rows; A1 adds lines, so the paid total is higher - the old gap estimate of about 332 USD predates many added rows, so read each cart\'s own total before paying [carts, summed by sql; params gaps_est_usd]' % total,
    'Amazon\'s lines, priced from the parts rows as quantity x unit price on %s, come to %.2f USD with %s unpriced and the amplifier fuse P188 left out; that is an estimate at today\'s quantities and will not equal the store\'s figure until the cart is re-read [parts unit_usd, summed by sql; carts Amazon]' % (TODAY, amazon_est, ', '.join(amazon_unpriced)),
    'The Waytek, WireBarn and DeutschConnector.com rows carry no unit price, so only the store\'s own total exists for those three [parts unit_usd]',
    'WireBarn: sign in before checkout or the cart is lost [carts WireBarn]',
    'P049 (disconnect, Blue Sea 9003e) and P052 (MRBF 250 A) must have had their part numbers confirmed before the cart is paid [parts P049, P052]',
    'The vehicle parts (A2) and the hardware-store stock (C2) are separate rows, not in these carts [work A2, C2]',
    'D1 counts every box against the parts table when it arrives, before anything is opened [work D1]'),
  'Four order confirmations in hand, one per store, each listing the same lines and quantities as the parts table.',
  'A line out of stock or changed in price at checkout: do not substitute a different part. Pay the rest of that cart only if the missing line is not a long-lead Deutsch kit; note the missing line in the app so it is re-sourced. A total far from the noted one: stop and re-read the cart against the parts list before paying.',
  'Tick the row. Put the four paid totals and order numbers in a note in the app.')
S('A0',
  ('Check the two rows before it are ticked', 'In the app: A1 (cart gaps) and A6 (cable listings) both done, and the blocks list shows nothing open that changes a cart line.', 'A0 shows as ready.', 'This is the largest spend of the project: do not pay with a block open.'),
  ('Waytek: compare and pay', 'Compare the cart with the Waytek rows: %s. The store figure was %s USD (%s) before A1 raised three lines. Pay; save the confirmation.' % (join(rows('Waytek', LIVE), cnt), CARTS['Waytek']['total_usd'], CARTS['Waytek']['lines_txt']), 'Order confirmation with every Waytek row on it.'),
  ('WireBarn: sign in, compare and pay', 'Sign in first. Rows: %s. The store figure was %s USD (%s) before A1. Pay; save the confirmation.' % (join(rows('WireBarn', LIVE), cnt), CARTS['WireBarn']['total_usd'], CARTS['WireBarn']['lines_txt']), 'Order confirmation with every WireBarn row on it.', 'Checking out as a guest loses the cart.'),
  ('DeutschConnector.com: compare the kits and pay', 'Kits: %s. Then the loose lines: %s. The store figure was %s USD (%s) before A1; re-read the total now. Pay; save the confirmation.' % (join(rows('DeutschConnector.com', LIVE, 'Assembly kits'), cnt), join([r for r in rows('DeutschConnector.com', LIVE) if 'Assembly' not in r['section']], cnt), CARTS['DeutschConnector.com']['total_usd'], CARTS['DeutschConnector.com']['lines_txt']), 'Order confirmation; every kit at its target.'),
  ('Amazon: last look at the held lines', 'P049 is the Blue Sea 9003e; P052 is a 250 A MRBF fuse for the 5191 holder; P188 is NOT in the cart. P053 is the 7720 block, P054 the 5250 (30 A), P055 the 5256 (100 A).', 'Five lines right, one absent.'),
  ('Amazon: compare and pay', 'Compare the cart with the Amazon rows in the parts list above (%d rows). The store figure was %s USD (%s) at the 2026-09-28 review. Pay; save the confirmation.' % (len(rows('Amazon', LIVE)) - 1, CARTS['Amazon']['total_usd'], CARTS['Amazon']['lines_txt']), 'Order confirmation with every Amazon row on it.'),
  ('Note the totals and tick', 'Put the four paid totals and order numbers in a note in the app, then tick A0. Keep the confirmations: D1 counts the boxes against the parts table.', 'A0 done; D1 waits for the boxes.'))

# ---------------------------------------------------------------- A2
B('A2',
  'The three vehicle parts - the brake pedal switch, the ignition switch\'s electrical portion and the road-speed sensor - are ordered.',
  'desk', '45 min - confirm',
  L('Laptop: RockAuto, PartsGeek or a Mazda specialist'),
  'P085 P086 P113',
  L('The project is at SOURCING',
    'The measurement day\'s M-2 has read the transmission\'s speedometer-drive boss thread (needed for P113\'s adapter)'),
  L('Brake pedal switch (P085): any 2-terminal type without cruise, Standard SLS-52 class - confirm fit; about 20 USD [parts P085]',
    'It serves the brake ladder input A3 only; the brake wake contact is a spare P084 plunger switch on the pedal, not a second pole [D-278; parts P085]',
    'Ignition switch, electrical portion, 1981-83 RX-7 (P086): terminals B, ACC, IG, ST; search "81-83 RX-7 ignition switch electrical"; new old stock or a quality reproduction; about 45 USD [parts P086]',
    'The factory number for this car\'s serial is BA24-66-155A; it is no longer available at Atkins, and BA14-66-151A is suggested as a substitute - confirm before buying [00-CAR PT708]',
    'Road-speed sensor (P113): a sealed Hall pulse generator on the transmission\'s speedometer-drive boss, Dakota Digital SEN-01-4160 or AutoMeter 5291 class, 8 000 or 16 000 pulses per mile; about 105 USD [parts P113]',
    'P113\'s thread adapter comes from the boss measured at M-2, and the part is bought after that measurement [parts P113; work C1]',
    'The senders are not on this list: the ones that work stay [D-261; work A2]',
    'The three rows add to %.0f USD by their estimates on %s [parts unit_usd, summed by sql]' % (veh_est, TODAY)),
  'Three orders placed: a 2-terminal brake switch, the 1981-83 ignition switch electrical portion, and a pulse generator with the adapter for the boss thread you measured.',
  'No ignition switch listed new: do not buy a used one unseen - note it in the app (the row asks for new old stock or a quality reproduction). No adapter for the boss thread: buy the sensor only once the adapter is found.',
  'Tick the row. Note what was ordered and from whom in the app.')
S('A2',
  ('Have the boss thread in front of you', 'From the measurement day (C1, M-2): the speedometer-drive boss thread diameter and pitch on the transmission. Without it, order only the two switches now.', 'Thread written down.'),
  ('Order the brake pedal switch (P085)', 'A stop-lamp switch for a 1981-83 RX-7 without cruise control, two terminals. Standard SLS-52 is the class the row names - confirm the fitment on the seller\'s page.', 'One switch ordered, 2 terminals.'),
  ('Order the ignition switch electrical portion (P086)', 'Search "81-83 RX-7 ignition switch electrical". It must carry four terminals: B, ACC, IG, ST. Factory number for this car BA24-66-155A (BA14-66-151A suggested as a substitute - confirm).', 'One switch ordered, new old stock or a quality reproduction.', 'The factory number is no longer available at Atkins: read the listing\'s year range and count its terminals.'),
  ('Order the road-speed sensor (P113)', 'A sealed Hall pulse generator, 8 000 or 16 000 pulses per mile (Dakota Digital SEN-01-4160 or AutoMeter 5291 class), with the thread adapter for the boss you measured.', 'Sensor and adapter ordered.'),
  ('Note and tick', 'Note supplier and order number for each in the app; tick A2. D1 counts them in with the rest.', 'A2 done.'))

# ---------------------------------------------------------------- B1
B('B1',
  'The A/C compressor\'s clutch is unplugged with its lead taped back, and the compressor\'s own belt is off and boxed; nothing else of the A/C is touched.',
  'engine bay', '1 h - confirm',
  L('Spanners or sockets for the compressor\'s pivot and adjusting bolts - sizes not in the record for this car: note what you use',
    'Insulating tape and a cable tie', 'A label and a bag or box for the belt', 'Camera'),
  '',
  L('Engine off and cold, key out',
    'The project is at SOURCING (the row\'s gate)'),
  L('The refrigerant stays in the sealed system: no hose or fitting is opened, no shop is needed [D-474]',
    'The compressor stays bolted to the engine; only its clutch plug comes apart and its belt comes off [D-474]',
    'The compressor runs on its own belt: nothing else is driven by it, so no other belt is disturbed [D-228]',
    'The clutch (the factory diagram\'s magnet clutch, G-19) has one lead, coloured BW - black with a white tracer - confirm on the car [S-001 p.24]',
    'The clutch lead loops through an open hole in the compressor body so it cannot touch the pulley - from the dealer A/C instruction, year not stated: confirm on the car [00-CAR PT235]',
    'The compressor hangs on a pivot bolt at the bottom of its mount and two bolts in the adjusting slots at the top; the belt runs round the crankshaft pulley and the compressor clutch - dealer instruction, confirm on the car [00-CAR SP-731, SP-732]',
    'That instruction says the water-pump pulley must be turned to the right position to fit the belt; the same may apply taking it off - confirm [00-CAR SP-732]',
    'The belt may be Mazda 0000-47-5409-03 (Dayco 17385): which belt is on the car is not recorded [00-CAR PT041, SP-998]',
    'Left alone: the bracket, condenser, receiver/drier, lines, evaporator, the factory interlock parts (G-18, G-19, G-21, G-22, G-23, the dash A/C switch) and the blower, heater core, HVAC case, ducts and doors [work B1; D-474]',
    'The full strip comes back with the engine swap; the new harness carries no A/C circuit [D-474]'),
  'The clutch connector is apart with the harness side taped and tied clear of every belt; the compressor belt is off, labelled and in its box; the compressor is tight on its mount; the alternator and air-pump belts are as they were.',
  'If the belt will not come off without taking another belt or a hose off: stop. Never loosen a refrigerant fitting. Photograph it and raise it in the app as a note. If you moved the alternator belt, re-set it: 13 to 17 mm deflection at a 10 kg push midway [00-CAR SP-025].',
  'Tick the row. Note the number printed on the belt in the app - the car record asks which belt is fitted.')
S('B1',
  ('Make the car safe', 'Engine off and cold, key out of the switch, bonnet propped.', 'Nothing hot, nothing turning.', 'Fingers near belts only with the key out.'),
  ('Find the compressor and its clutch lead', 'The compressor is the belt-driven unit with two refrigerant hoses on it (their fittings point upward - dealer instruction, confirm). Its place in the bay is not in the record: note it. The clutch is the pulley on its nose; one lead (BW by the diagram) comes from it to a connector - where that connector sits is not in the record.', 'Compressor, its belt and the single clutch lead identified.'),
  ('Photograph before touching', 'The belt run round the crankshaft pulley and the compressor, the connector, and the mount bolts.', 'Three photos or more.'),
  ('Unplug the clutch connector', 'Part the connector on the clutch lead by its body, not by the wires. Nothing is cut.', 'Two connector halves apart.'),
  ('Tape the harness side back', 'Wrap the harness-side half in insulating tape, label it "A/C CLUTCH - UNPLUGGED" with the date, and tie it back clear of every belt and pulley. Leave the compressor-side lead through its hole in the compressor body.', 'Nothing can reach a pulley.'),
  ('Slacken the compressor on its mount', 'Loosen the two bolts in the top adjusting slots and the pivot bolt at the bottom just enough for the compressor to swing. Do not remove the bolts and do not touch the hoses.', 'The compressor swings toward the engine and the belt goes slack.', 'The hoses are under pressure: do not loosen a hose fitting, and do not let the compressor hang on its hoses.'),
  ('Take the belt off', 'Slip the belt off the compressor pulley, then off the crankshaft pulley. If it will not clear, turn the water-pump pulley by hand to the position that lets it pass. No other belt comes off.', 'Belt free in your hand.', 'If another belt must come off first, stop and note which one.'),
  ('Tighten the compressor back on its mount', 'Swing the compressor back to a neutral position and tighten the pivot bolt and both adjusting bolts. Torque is not in the record: tighten firmly and note the spanner sizes.', 'Compressor solid on its mount; hoses unstrained.'),
  ('Box the belt', 'Read the number printed on the belt, label it "A/C compressor belt, off (date)", and put it in the box with the car\'s kept parts.', 'Belt boxed; its number written down.'),
  ('Tick and note', 'Tick B1; enter the belt\'s number as a note in the app.', 'B1 done.'))

# ---------------------------------------------------------------- C2
B('C2',
  'The hardware-store stock is bought: the dash-node carrier panel, the sill-node panel, the battery backing plate, paint for any aluminium, and the binnacle plate.',
  'hardware store', '1 h plus the trip - confirm',
  L('The measurement day\'s numbers (M-1, M-4, M-5) and the cardboard mock-ups', 'Tape measure'),
  'P090 P091 P092 P093 P121',
  L('The measurement day (C1) is done: the dash spaces (M-1), the cargo bin mock-up (M-4) and the sill space (M-5) are measured',
    'The project is at SOURCING'),
  L('Carrier-panel stock for the dash node (P090): 3 mm aluminium or ABS sheet, one or several small pieces; sizes from M-1 and the bench layout (E13) [parts P090]',
    'Sill-node panel stock (P091): about 150 x 100 mm, from M-5 [parts P091]',
    'Battery backing plate stock (P092): 3 to 4 mm aluminium or steel, sized from the M-4 mock-up; it goes under the floor beneath the battery [parts P092]',
    'Paint or powder-coat (P093): never bare aluminium against a live stud [parts P093]',
    'Binnacle plate stock (P121): 3 mm black ABS or aluminium, one piece sized from M-1; the unit\'s face was mocked up at 335 x 136.5 mm - confirm against your measurement; about 15 USD [parts P121]',
    'No battery-cover stock: the terminals are covered by boots and nothing else [D-235; work C2]',
    'The trip was estimated at about 40 USD [params hardware_est_usd]',
    'P090 to P093 carry no quantity in the record: the sizes are your measurements [parts P090, P091, P092, P093]'),
  'Five items in hand: sheet for the dash-node panels, a piece at least 150 x 100 mm for the sill, plate 3 to 4 mm thick at least the size of the M-4 mock-up, paint, and the binnacle piece.',
  'A size you do not have yet (a measurement not taken): buy the rest and note the missing one in the app; do not guess a plate size.',
  'Tick the row. Note what each piece measures and cost in the app.')
S('C2',
  ('Write the sizes on one list', 'From the measurement day: the dash-node spaces (M-1), the sill space behind the driver kick panel (M-5), the backing-plate outline from the cargo-bin mock-up (M-4), and the binnacle aperture, taken off the instrument panel now that it is out of the car - it is no longer a measurement row of its own, the dash is rebuilt around the units.', 'One list with four sizes.'),
  ('Buy the dash-node panel stock (P090)', '3 mm aluminium or ABS sheet, enough for one or several small panels inside the M-1 spaces. E13 cuts them after a cardboard mock-up in the car.', 'Sheet bought.'),
  ('Buy the sill-node panel stock (P091)', 'A piece about 150 x 100 mm, 3 mm aluminium or ABS.', 'Piece bought.'),
  ('Buy the battery backing plate stock (P092)', '3 to 4 mm aluminium or steel, at least the size of the M-4 mock-up\'s plate.', 'Plate bought.', 'This plate is what holds the battery in a crash: do not go thinner than 3 mm.'),
  ('Buy paint for the aluminium (P093)', 'Paint or arrange powder-coat for every aluminium panel.', 'Paint bought.'),
  ('Buy the binnacle plate stock (P121)', '3 mm black ABS or aluminium, one piece larger than the binnacle face (mock-up 335 x 136.5 mm - confirm).', 'Piece bought.'),
  ('Tick and note', 'Tick C2; note sizes and cost in the app.', 'C2 done; E13 can lay out the dash node.'))

# ---------------------------------------------------------------- D1
d1_ids = four_ids + veh_ids
B('D1',
  'Every box that arrived is counted against the parts table, row by row, before anything is opened, and every heavy part\'s torque figure is read off its maker\'s sheet.',
  'bench', '2 h - confirm',
  L('The app\'s parts list (01-electrical, by store)', 'The four order confirmations', 'Tape measure for the cable and wire lengths', 'Marker and bags'),
  ' '.join(d1_ids),
  L('A0, A1 and A2 are done: the four carts and the vehicle parts are ordered',
    'Every shipment has arrived',
    'Sealed bags stay sealed until their row is counted'),
  L('Count quantity per row, before anything is opened [work D1]',
    'The quantity to count against is the one the app shows on each row; where a list below shows a target, A1 moved the order to that target [parts qty, target]',
    'The Deutsch crimper P038 is accepted only after its test crimps pass at D4: keep its box and receipt [parts P038]',
    'Wire by the foot (WireBarn) and the heavy cable are counted by length: read the label or measure [parts unit]',
    'P048 Class-T fuse is two: one fitted, one spare. P054 and P055 MIDI fuses are sold as pairs: one fitted, one spare each [parts P048, P054, P055]',
    'Every heavy connection is torqued to its maker\'s figure, read off the maker\'s sheet today and written into the record before E8; none is recorded yet [rules torque]',
    'The parts whose sheets carry those figures: Class-T block P047, MRBF holder P051, battery post clamps P095, busbar P007, PowerPost P050, MIDI holders P053, and the relay sockets [rules torque]',
    'The two spare 39-way PMU housings and their terminals are counted in their own row, D3 [work D3]',
    'Blade fuses are in your drawer and MAXI fuses are a local purchase: neither arrives in a box [parts P141, P190, P191]',
    'The amplifier\'s fuse P188 was not ordered [parts P188]'),
  'Every row of the four stores and the three vehicle parts has its quantity counted and matching, or its shortfall written down; the torque figures are noted; nothing is opened that was short or wrong.',
  'Short, wrong or damaged: do not open it. Photograph the label and the packing slip, note the row id and the count in the app, and contact the seller. A wrong Deutsch kit or fuse holder is cheaper to return sealed.',
  'Tick the row. Note any shortfall by row id, and enter each torque figure you read (part id, stud, figure, unit) as a note in the app.')
amazon_other = [r for r in rows('Amazon', LIVE) if r['id'] != 'P188' and not any(k in r['section'] for k in ('Tools', 'Power backbone', 'Dash node', 'Consumables'))]
S('D1',
  ('Sort the boxes by store', 'Four piles - Waytek, WireBarn, DeutschConnector.com, Amazon - and the vehicle parts. Put each order confirmation on its pile. Open the outer shipping boxes only.', 'Five piles.', 'Do not open any sealed bag yet.'),
  ('Count Waytek', join(rows('Waytek', LIVE), cnt) + '.', 'Every Waytek row matches.'),
  ('Count WireBarn', 'By the length on each label: ' + join(rows('WireBarn', LIVE), cnt) + '.', 'Every length matches.'),
  ('Count the DeutschConnector.com kits', 'Each kit bag is one housing with its wedgelock and contacts: ' + join(rows('DeutschConnector.com', LIVE, 'Assembly kits'), cnt) + '.', 'Every kit count matches; plug kits (DT06 / DTP06) and receptacle kits (DT04 / DTP04) not confused.'),
  ('Count the DeutschConnector.com loose lines', join([r for r in rows('DeutschConnector.com', LIVE) if 'Assembly' not in r['section']], cnt) + '.', 'Contacts, sealing plugs, clips, caps and the two removal tools match.'),
  ('Count the Amazon tools', join(rows('Amazon', LIVE, 'Tools'), cnt) + ' · ' + cnt(PARTS['P171']) + '.', 'Every tool present; the hydraulic crimper has its dies, the 1/0 pair included.'),
  ('Count the Amazon power backbone and battery parts', join([r for r in rows('Amazon', LIVE, 'Power backbone') if r['id'] != 'P188'], cnt) + '.', 'Every row matches; cable lengths read off the reels.', 'The fuses are easy to mis-ship: the Class-T reads 150 A, the MRBF 250 A, the MIDI fuses 30 A and 100 A.'),
  ('Count the Amazon dash-node and electronics parts', join(rows('Amazon', LIVE, 'Dash node'), cnt) + '.', 'Every row matches.'),
  ('Count the Amazon consumables and the rest', join(rows('Amazon', LIVE, 'Consumables'), cnt) + ' · ' + join([r for r in amazon_other if r['id'] != 'P171'], cnt) + '.', 'Every row matches.'),
  ('Count the vehicle parts', join(rows('', None, None, veh_ids), cnt) + '. The ignition switch must show four terminals (B, ACC, IG, ST); the brake switch two.', 'Three parts, right terminal counts.'),
  ('Read the torque sheets', 'From the leaflet in each box (or the maker\'s page): the stud torque of the Class-T block (P047), the MRBF holder (P051), the battery post clamps (P095), the busbar (P007), the PowerPost (P050), the MIDI holders (P053) and the relay sockets\' screws. Write part id, which stud, the figure and its unit.', 'One figure per stud, written down.', 'These figures are not in the record until you enter them: E8 to E11 torque to them.'),
  ('Set aside anything short or wrong', 'Leave it sealed; photograph label and packing slip; note the row id and the count; contact the seller.', 'A list of shortfalls, or none.'),
  ('Tick and note', 'Tick D1; enter shortfalls and the torque figures as notes in the app.', 'D1 done; D2, D3 and D4 can start.'))

# ---------------------------------------------------------------- D2
B('D2',
  'The battery hold-down, the two post terminals and the boots are proven to fit the Ionic on the bench, and each boot lifts off by hand with its terminal loaded.',
  'bench', '45 min - confirm',
  L('Spanners for the post-clamp bolts and the stud nuts - sizes not in the record: note them', 'Tape measure or calipers'),
  'P057 P094 P095 P098 P066',
  L('A1 is done and the parts have arrived (D1 counted them)',
    'Rings and watch off; the battery on a clear, non-metal bench',
    'One terminal covered whenever a tool is near the other'),
  L('The battery is the Ionic IC-12V40-S9H, a 12 V 40 Ah heated lithium (LiFePO4) pack [D-330; 00-CAR S-036]',
    'Its case measures 170 W x 230 L x 190 H mm; the terminals and boots stand above the 190 mm [params battery_case_mm; D-239]',
    'It has SAE tapered posts, so each connection is a brass post clamp with a 3/8 in stud take-off (P095), never a ring lug on the post [D-234; parts P095]',
    'The positive clamp\'s stud carries one lug only: the 1/0 cable C12 to the master disconnect. The fuse holder and the PMU feed sit on the disconnect, not here [parts P095; D-319]',
    'The negative clamp\'s stud carries the 1/0 cable C05 to the rear ground stud [cables C05]',
    'The clamp stud\'s thread is confirm until measured (CK24) [parts P095; checks CK24]',
    'The boots (P094) are the only cover over a live post: no box and no cover panel, so a boot must clear the loaded terminal and pull off by hand for a jump start [D-235; D-229; parts P094]',
    'The hold-down is a clamp with J-hooks on M8 grade-8 hardware, nyloc nuts and fender washers; in the car it bolts through the floor onto a backing plate, never sheet metal alone [parts P057; D-063]',
    'A dropped tool across a lithium battery\'s terminals welds [work E4]'),
  'Both clamps seat and tighten on their posts; each stud takes a 1/0 lug with its nut fully on; each boot covers its loaded terminal completely and lifts off with one hand; the hold-down grips the 170 x 230 mm footprint; the height over the boots is written down.',
  'A boot that will not cover the stack or will not lift by hand, a clamp that will not tighten, a hold-down that does not fit the case: change nothing on the battery. Photograph it and raise it in the app as a note - the part is exchanged before E8.',
  'Tick the row. Note the height from the bench to the top of the fitted boots, in mm (the cargo-bin mock-up is cut to the case plus the boot height).')
S('D2',
  ('Clear the bench and take metal off your hands', 'Battery on a wooden or plastic surface. Rings and watch off. Keep each post covered until its clamp goes on.', 'Nothing metal within reach of both posts at once.', 'Lithium: a tool across the two posts welds, it does not just spark.'),
  ('Fit the negative post clamp', 'One of the P095 pair onto the negative post; push it fully down the taper and tighten its pinch bolt.', 'Clamp cannot be turned by hand.'),
  ('Fit the positive post clamp', 'The other P095 clamp onto the positive post, fully down, pinch bolt tight. Cover the negative clamp with its boot while you do it.', 'Clamp cannot be turned by hand.'),
  ('Load each stud with a 1/0 lug', 'Put one P098 lug (3/8 in hole, uncrimped) on each clamp\'s 3/8 stud with its washer and nut, as C12 will sit on the positive and C05 on the negative.', 'Nut fully on with thread showing; the lug lies flat on the clamp.', 'If the 3/8 hole does not fit the stud, note the stud\'s size: the lug order is wrong, not the stud.'),
  ('Try the boots over the loaded terminals', 'Red boot on positive, black on negative (P094). Each must cover the clamp, the stud and the lug\'s barrel end.', 'No metal visible on either terminal.'),
  ('Lift each boot with one hand', 'Pull each boot off and push it back, one-handed, as you would at the roadside for a jump start.', 'Each lifts and re-seats without a tool.'),
  ('Try a lug boot on the 1/0 lug', 'Slide a P066 boot over a P098 lug\'s barrel as it will sit on the cable.', 'The boot covers the lug\'s barrel and stud end.'),
  ('Dry-fit the hold-down', 'Lay the P057 clamp across the case and hang the J-hooks or M8 bolts either side. Check it bears on the case, not on a terminal or a boot.', 'Clamp spans the 170 mm width or the 230 mm length cleanly; the boots are clear of it.'),
  ('Measure the height over the boots', 'Bench to the top of the fitted boots, in mm.', 'A figure above 190 mm.'),
  ('Strip it back, tick and note', 'Take the lugs off; leave the clamps on only if both boots stay on. Tick D2 and enter the height as a note.', 'D2 done.'))

# ---------------------------------------------------------------- D3
B('D3',
  'Both spare 39-way PMU housings are confirmed to carry a full terminal set - 16 large and 27 small each - and the terminals\' part numbers are read.',
  'bench', '20 min',
  L('A tray', 'Two labelled bags'),
  '',
  L('A1 is done (the row\'s gate)', 'Clean bench: the terminals are small and there are no others'),
  L('The two spare housings in hand hold 54 small and 32 large terminals between them: 27 small and 16 large each [D-135; work D3]',
    'They are the only spare terminals: none were ordered, and the car\'s own set has no spares [D-135]',
    'That is why the practice crimps at D4 use the spare sets first [D-135]',
    'The PMU\'s 39-way connector has 11 large cavities (pins 1, 2, 12, 13, 14, 25, 26, 27, 28, 38, 39), 27 small ones and one medium (pin 15, the +5 V output) [parts P039; pins cav_size]',
    'The medium terminal for pin 15 and its crimp die are not named anywhere in the record [parts P039]',
    'The large terminals crimp in the 2.8 mm die and the small in the 1.5 mm die of the open-barrel crimper P039 [parts P039]',
    'The three terminal part numbers are to be read off the spare housings and checked against the PMU pinout sheet [checks CK24; 00-CAR S-027]',
    'The counts are verified on arrival [D-127]'),
  'Two bags, each counted at 16 large and 27 small, labelled; the part numbers on the housings or bags written down; whether any medium terminal is present is noted.',
  'A short count: write the shortfall in the app before D4 uses a single terminal - these are the only replacements. No medium terminal found: note it; pin 15\'s terminal has to be identified before the connector is terminated (E16).',
  'Tick the row. Note the counts (large, small, medium) per set and the part numbers you read.')
S('D3',
  ('Open the first spare set over a tray', 'Tip the terminals of the first spare 39-way housing into the tray. Keep the two sets apart.', 'One set in the tray.'),
  ('Count the large terminals', 'The large ones fit the 2.8 mm die.', '16.'),
  ('Count the small terminals', 'The small ones fit the 1.5 mm die.', '27.'),
  ('Look for a third size', 'Pin 15 takes a medium terminal the record does not name. Note whether the set holds one that is neither large nor small.', 'Present or absent, written down.'),
  ('Read the part numbers', 'Off the housing, the bag or the terminals\' carrier strip: the housing\'s number and each terminal size\'s number.', 'Up to three terminal numbers and the housing number written down.'),
  ('Count the second set the same way', 'Large, small, any medium.', '16 and 27 again.'),
  ('Bag and label both sets', '"PMU SPARE SET 1" and "SET 2", with the counts on each bag.', 'Two labelled bags.'),
  ('Tick and note', 'Tick D3; enter counts and part numbers as a note in the app.', 'D3 done; D4 may use spare terminals for its test crimps.'))

# ---------------------------------------------------------------- D4
B('D4',
  'Each crimper has made three passing test crimps in a row on every terminal and wire size it will be used for, and the setting that passed is written down.',
  'bench', '3 h - confirm',
  L('Deutsch solid-contact 4-indent crimper, sizes 12 / 16 (P038)',
    'Open-barrel ratchet crimper, 1.5 mm and 2.8 mm dies (P039)',
    'Hydraulic lug crimper, 8 AWG to 1/0, with dies (P037)',
    'Digital hanging scale 0-50 kg (P040)',
    'Wire strippers 10-22 AWG and flush cutters (P043)',
    'A vice or locking pliers to hold the contact',
    'Eye protection'),
  'P037 P038 P039 P040 P022 P023 P024 P025 P026 P027 P064 P098 P065 P010 P012 P015 P017 P061 P096 P063',
  L('A1 is done and D1 has counted the parts in',
    'D3 has counted the two spare PMU terminal sets',
    'Eye protection on: a contact can let go under the pull'),
  L('A crimper is accepted only after three practice crimps pass the pull test: 16 AWG 20 lbf, 14 AWG 34 lbf, 12 AWG 45 lbf [D-203]',
    'On the kg scale those are 9.1 kg, 15.4 kg and 20.4 kg [arithmetic from D-203: 1 lbf = 0.4536 kg]',
    'The Deutsch crimper P038 is kept only if its test crimps pass [parts P038]',
    'A Deutsch size-16 contact carries 13 A and seals on 14-20 AWG wire; a size-12 carries 25 A and seals on 10-14 AWG [series DT, DTP]',
    'Spare size-16 contacts for 16-18 AWG: socket P022 (0462-201-16141), pin P023 (0460-202-16141) [parts P022, P023]',
    'Size-16 contacts for 14 AWG are a different part: socket P024 (0462-209-16141), pin P025 (0460-215-16141); the kit contacts do not take 14 AWG [parts P024, P025]',
    'Spare size-12 contacts: socket P026 (0462-203-12141), pin P027 (0460-204-12141), five of each [parts P026, P027]',
    'PMU terminals: the 2.8 mm die for the 11 large (12 AWG, and 10 AWG on pin 25), the 1.5 mm die for the 27 small (16 AWG, and 14 AWG on pins 3, 4, 5, 9, 10, 11); try the die on one spare terminal first [parts P039; pins cav_size, awg]',
    'PMU practice terminals come from the spare sets: the car\'s own set has none to spare [D-135]',
    'The hydraulic crimper does every 2 AWG, 1/0 and 6 AWG lug; the 1/0 dies are tested too, since two 1/0 runs were added [parts P037; work D4; D-246]',
    'Lugs bought beyond the cable ends are the practice stock: 2 AWG P064 is 18 for 8 ends, 1/0 P098 is 12 for 8 ends [parts P064, P098]',
    'The 6 AWG lug row\'s target is 4 and the alternator cable uses all four: test one only if more than four arrived [parts P065]',
    'Not in the record: the strip length for any terminal, the Deutsch crimper\'s selector and depth setting, which die fits which lug, and a pull figure for a lug or for 10 AWG - confirm'),
  'Three passes in a row, written down with the setting used, for: size 16 on 16 AWG, size 16 on 14 AWG, size 12 on 12 AWG, PMU small on 16 AWG and on 14 AWG, PMU large on 12 AWG, a 2 AWG lug and a 1/0 lug.',
  'A crimp that pulls out below its figure: change the setting (selector, depth, die) and start that set of three again. A crimper that cannot make three in a row pass is returned and replaced before any real crimp - do not use it on the car. A PMU die that does not fit the spare terminal: stop and note it in the app.',
  'Tick the row. Note for each combination the setting that passed and the load each held (kg), and the strip length you used.')
S('D4',
  ('Set up the pull test', 'Hang the scale (P040) from a fixed hook. You will clamp each crimped contact in the vice or locking pliers, tie or loop the wire to the scale\'s hook, and pull steadily until the scale reads the pass figure. Eye protection on.', 'Scale reads zero hanging free.', 'A contact can release suddenly: pull away from your face.'),
  ('Cut and strip three 16 AWG test wires', 'Three 150 mm lengths of 16 AWG GXL (grey P010, or any 16 AWG spool). Strip 6.3 to 7.9 mm (0.250-0.312 in), the length for a size-16 contact [rules crimp; 00-CAR S-502]: the bare strands fill the barrel and show in the inspection hole, and no copper shows behind it.', 'Clean strands, none cut or nicked.'),
  ('Set the Deutsch crimper for size 16 on 16 AWG', 'P038 is a four-indent crimper for solid contacts. Its selector position and depth for a size-16 contact on 16 AWG are not in the record: use the chart that comes with the tool, and write the setting down.', 'Setting written down.'),
  ('Crimp three size-16 contacts on 16 AWG', 'Use spares P022 (socket) or P023 (pin). Seat the contact in the crimper, push the stripped wire fully into the barrel, hold the wire in, and close the handles until the ratchet releases.', 'Four even indents round the barrel; no strand outside it; insulation right up to the barrel.'),
  ('Pull-test the three', 'Clamp the contact, hook the wire to the scale and pull steadily to 20 lbf (9.1 kg). Hold a moment.', 'All three hold at 20 lbf (9.1 kg) or more.', 'One failure restarts the set of three after a setting change.'),
  ('Size 16 on 14 AWG: crimp three and pull', 'Three 14 AWG wires (orange P012). Use the 14 AWG contacts P024 (socket) or P025 (pin), not the 16-18 AWG ones. Reset the crimper per its chart; crimp; pull to 34 lbf (15.4 kg).', 'All three hold at 34 lbf (15.4 kg).'),
  ('Size 12 on 12 AWG: crimp three and pull', 'Three 12 AWG wires (red P015). Contacts P026 (socket) or P027 (pin); there are five of each, so mix them. Strip 5.6 to 7.2 mm (0.222-0.284 in) for a size-12 contact [rules crimp]. Set the crimper for size 12; crimp; pull to 45 lbf (20.4 kg).', 'All three hold at 45 lbf (20.4 kg).'),
  ('Try the open-barrel dies on one spare PMU terminal', 'Lay a spare small terminal in the 1.5 mm die of P039 and a spare large one in the 2.8 mm die, without wire, and close gently to see the wings roll evenly.', 'Each terminal sits square in its die.', 'Spare terminals are the only replacements: one of each for this trial, no more.'),
  ('PMU small terminal on 16 AWG: crimp three and pull', 'Spare small terminals from D3\'s bags, 16 AWG wire, the 1.5 mm die. ' + STRIP + ' Pull to 20 lbf (9.1 kg).', 'All three hold at 20 lbf (9.1 kg); the wings are rolled into the strands, the rear wings grip the insulation.'),
  ('PMU small terminal on 14 AWG: crimp three and pull', 'Six PMU pins (3, 4, 5, 9, 10, 11) carry 14 AWG in a small cavity. Same die; pull to 34 lbf (15.4 kg).', 'All three hold at 34 lbf (15.4 kg).'),
  ('PMU large terminal on 12 AWG: crimp three and pull', 'Spare large terminals, 12 AWG wire, the 2.8 mm die. Pull to 45 lbf (20.4 kg). Pin 25 carries 10 AWG (black P017): crimp one on 10 AWG as well and note what it holds - the record gives no figure for 10 AWG.', 'Three at 45 lbf (20.4 kg) on 12 AWG; the 10 AWG figure noted.'),
  ('Leave pin 15\'s terminal alone', 'Pin 15 takes a medium terminal whose part and die the record does not name. Do not crimp it by guess: note what D3 found.', 'Nothing crimped; the gap noted.'),
  ('2 AWG lug: crimp three', 'Offcuts of 2 AWG cable (P061) and lugs P064. Fit the hydraulic crimper P037 with the die for 2 AWG - which die marking fits is not in the record: use the tool\'s chart and write it down. Strip to the depth of the lug\'s barrel, push the cable fully home, crimp.', 'The lug cannot be pulled or twisted off by hand (the record gives no pull figure for a lug - confirm); no strands outside the barrel.', 'Keep fingers out of the die: a hydraulic crimper does not stop.'),
  ('1/0 lug: crimp three with the 1/0 dies', 'Offcuts of 1/0 cable (P096) and lugs P098, the 1/0 die pair. Twelve lugs were bought for eight cable ends: three test crimps leave one spare.', 'The lug cannot be pulled or twisted off by hand; the die closes fully.'),
  ('6 AWG lug: only if one is spare', 'The alternator cable uses four 6 AWG lugs (P065) and the order\'s target is four. If more than four arrived, crimp one on a P063 offcut; if not, the first real one at E10 is made with the 2 AWG test\'s care.', 'One test lug, or none and a note.'),
  ('Write the settings on the tools', 'For each combination: selector or die, depth, strip length, and the load held. Tape the note inside each crimper\'s case. Keep the test pieces in a labelled bag.', 'One line per combination.'),
  ('Tick and note', 'Tick D4; enter the settings and loads as a note in the app. Any crimper that failed is boxed for return.', 'D4 done.'))

# ---------------------------------------------------------------- E4
B('E4',
  'You have read every safety rule of the build once, properly, and can say each one back before the first tool touches the car.',
  'desk', '30 min',
  '',
  '',
  L('D1 (parts counted), D4 (crimpers proven), C1 (the measurement day) and B1 (A/C clutch and belt) are done'),
  L('The battery is lithium: a dropped tool across its terminals welds [work E4]',
    'The master disconnect is a Blue Sea 9003e on the battery POSITIVE in the cargo bin; opening it removes supply from everything, the starter cable included [D-319; recovery RC01]',
    'The cable between the positive post and the disconnect (C12) is the one length no fuse protects: it is kept to inches [D-062; cables C12]',
    'The Class-T fuse is 150 A and feeds the whole PMU system; the MRBF fuse is 250 A and protects the starter cable [fuses Class-T, MRBF]',
    'A PMU output can fail live: its switch fails short, not open, so an output can be on with the key out. Only the master disconnect is certainly off [recovery RC01; checks CK07]',
    'The disconnect has no extra pole: shut the engine down before opening it [recovery RC01]',
    'The factory manual: the negative battery cable comes off first and goes on last [S-002 p.5-5]',
    'The fuel pump and tank sender wiring run under the rear floor to the tank [routes RT17]',
    'The dash node sits under the cowl seam and windscreen, where this car leaks [rules water-ingress]',
    'Every heavy connection is torqued to its maker\'s figure and paint-marked [rules torque]',
    'From E26 until E28 finishes the car does not start, and it is not driven until the interior is back at E35 [D-414; D-387]',
    'A fire extinguisher is not a parts row: have your own within reach [work E4]'),
  'You can say each of the rules in the steps without looking, and the extinguisher, jack stands, chocks and terminal boots are where you will work.',
  'A rule you do not understand, or one that seems to disagree with a step later in the list: ask in the app (Explain on the row) before touching the car.',
  'Tick the row.')
S('E4',
  ('Lithium: cover both terminals, metal off your hands', 'Whenever the battery is in the car and you are working, both terminals are booted or taped. Rings and watches off.', 'You can say why: a dropped tool across the posts welds.'),
  ('Open the master disconnect before touching four things', 'The 2 AWG feed, the starter cable, the tank sender, and anything in the pop-up headlamp buckets. Every time. The disconnect is on the POSITIVE side in the cargo bin, so opening it removes supply from everything, the starter cable included.', 'You can name the four.'),
  ('Before the disconnect is fitted, pull the negative lug', 'Until E9 has fitted the disconnect, the way to make the car dead is to take the negative cable off the battery. Negative comes off first and goes back on last.', 'You know which cable moves first.'),
  ('Shut the engine down before opening the disconnect', 'The switch has no pole to shut the alternator down first. Engine off, then the switch.', 'Order known: engine, then switch.', 'Opening it with the engine running sends the alternator\'s output into the wiring with no battery to absorb it.'),
  ('Treat every PMU output as possibly live', 'A PMU output\'s switch fails short, not open: an output can be live with the key out and the module asleep. The only thing that is certainly off is the master disconnect.', 'You reach for the disconnect, not the key.'),
  ('Keep the unfused cable to inches', 'The cable from the positive post to the disconnect cannot be protected by any fuse. The disconnect and the Class-T block sit as close to the positive post as physically possible.', 'You know which cable has no fuse.'),
  ('Leave the big fuses out while you build', 'The Class-T fuse (150 A) and the MRBF fuse (250 A) are not fitted until E11. The PMU\'s first power-up (E24) is through a 5 A fuse bridged across the Class-T block, so a short melts a 5 A fuse and not a 2 AWG cable.', 'You know when each fuse goes in.'),
  ('Jack stands always, wheels chocked', 'Never under the car on a jack alone. Chock the wheels: P on the automatic is not a parking brake.', 'Stands and chocks by the car.'),
  ('No sparks near the tank; extinguisher within reach', 'The pump and tank sender wiring run under the rear floor to the tank. No grinding, drilling or test sparks near it without looking first. The extinguisher is within reach, not in the next room.', 'Extinguisher placed.'),
  ('Engine running: clear of belt and fan, garage door open', 'Sleeves and leads clear of the belt, fan and pulleys. Door open: exhaust in a closed garage is carbon monoxide.', 'Door open before any start.'),
  ('Pop-up headlamps move fast', 'Fingers out of the buckets whenever the motors can be powered. A stalled motor pulls 15 to 25 A.', 'You open the disconnect before reaching into a bucket.'),
  ('Label the factory end of every migrated circuit', 'When a circuit moves to the new harness, its factory end is labelled MIGRATED with the date and taped back.', 'Labels and a pen in the kit.', 'An unlabelled live wire taped behind a dash is the next fault.'),
  ('Label every new wire at both ends the moment it is cut', 'Printed laminated tape, both ends, from / to. Never tape and marker.', 'You label before cutting the next wire.'),
  ('Torque every heavy connection and paint-mark it', 'Each heavy stud to its maker\'s figure (read at D1), marked with the paint pen after torquing.', 'Torque notes and paint pen in the kit.'),
  ('Keep water out of the new parts', 'Every conductor enters the PMU, the dash node and each panel from below or with a drip loop; nothing mounts in the lowest 50 mm of the footwell; the PMU\'s 39-way connector faces down or sideways, never up.', 'You can say the three.'),
  ('Never bare aluminium against a live stud; both busbars covered', 'Any aluminium panel is painted or coated; the always-hot busbar and the ground bus both carry covers.', 'Known.'),
  ('The car does not start, and is not driven, until the list says so', 'It runs at E12 on the new backbone, then does not start from E26 until E28 has moved the last circuit, and is not driven until the interior is back at E35.', 'Known.'),
  ('Tick the row', 'Tick E4 in the app.', 'E4 done; E5 ready.'))

# ---------------------------------------------------------------- E5
B('E5',
  'You can crimp, insert, lock, tug-test and remove a Deutsch contact, shrink an adhesive joint until the glue weeps at both ends, and finish one lug with heavy-wall shrink and a boot - all on scrap.',
  'bench', '1.5 h - confirm',
  L('Deutsch solid-contact 4-indent crimper, sizes 12 / 16 (P038), at the setting that passed at D4',
    'Contact removal tool, size 16 (P031 metal, P032 plastic)',
    'Heat gun, 1500 W, two temperatures (P042)',
    'Wire strippers and needle-nose pliers (P043)',
    'Hydraulic lug crimper, 8 AWG to 1/0 (P037)',
    'Eye protection'),
  'P022 P023 P124 P077 P078 P064 P066 P061 P010',
  L('E4 is done: the safety rules read',
    'D4 is done: the crimper settings that passed are written down',
    'Eye protection for crimping and the heat gun'),
  L('A Deutsch DT housing has two halves: the plug (DT06, socket contacts, the leg side) and the receptacle (DT04, pin contacts, the panel side) [housings leg_side, box_side]',
    'Each half has a wedgelock, the coloured piece that locks the contacts in: W4S in a 4-way plug, W4P in its receptacle [housings wedgelocks]',
    'The cavity number is the one moulded into the housing: read it off the part, never mirror it [rules cavity-numbers]',
    'A contact must click in and not back out under a firm tug [work E5]',
    'Insert and remove a contact ten times with the removal tool [work E5]',
    'The metal removal tool P031 stays in the toolbox; the plastic one P032 lives in the car [parts P031, P032]',
    'No spare housing is bought: every kit is counted to a housing in the car. The DT06-4S plugs for L3-RDR and L4-RDR wait on the shelf for parts not fitted this build [parts P124]',
    'Adhesive heat-shrink is done when the glue weeps evenly at both ends [work E5]',
    'Every lug gets heavy-wall adhesive shrink and a boot [work E9]',
    'How the removal tool releases a contact is not described in the record: follow the tool\'s own instructions [parts P031, P032]'),
  'One contact inserted and removed ten times without damage, clicking and holding a firm tug each time; one adhesive joint with glue showing evenly at both ends; one lug finished with heavy-wall shrink and a boot.',
  'A contact that will not click: it is not fully home or the wedgelock is in the way - take the wedgelock out and try again. A contact that backs out under a tug: do not use that housing in the car; note it in the app. Scorched shrink or wire: lower the heat and keep the gun moving.',
  'Tick the row.')
S('E5',
  ('Pick the practice housing', 'Use one DT06-4S plug kit (P124) that waits on the shelf for a part not fitted this build - L3-RDR\'s or L4-RDR\'s. It is the 4-way plug; its wedgelock is W4S. The record buys no spare housing, so treat it gently: it goes back in its bag.', 'One 4-way plug and its wedgelock on the bench.'),
  ('Crimp two practice contacts', 'Two 150 mm lengths of 16 AWG, spare socket contacts P022, crimper P038 at D4\'s passing setting. Tug each by hand.', 'Four even indents; neither pulls off by hand.'),
  ('Read the cavity numbers', 'Find the numbers 1 to 4 moulded into the rear (wire side) of the plug.', 'Cavity 1 found.'),
  ('Insert a contact', 'Take the wedgelock out. Push the contact into cavity 1 from the rear, through the seal, straight, until it clicks.', 'A click you can feel.', 'Pushing at an angle tears the rear seal.'),
  ('Tug it', 'Pull the wire firmly.', 'The contact does not back out.'),
  ('Fit the wedgelock', 'Push the wedgelock in from the mating face until it seats.', 'Wedgelock seated; the contact cannot move.'),
  ('Remove the wedgelock and the contact', 'Pull the wedgelock out with needle-nose pliers. Release the contact with the size-16 removal tool (P031 or P032) as the tool\'s instructions show, and draw the wire out of the rear.', 'Contact out undamaged; the seal intact.', 'Never pull a contact out by force without releasing it: the lock finger breaks.'),
  ('Repeat ten times', 'Insert, click, tug, wedgelock, remove - ten times in all, with both removal tools.', 'It clicks and holds on the tenth as on the first.'),
  ('Practise the adhesive heat-shrink', 'Join two 16 AWG offcuts with a heat-shrink butt splice (P078) or slide adhesive-lined shrink (P077) over a wire. Heat gun (P042) on its low setting, moving round the joint from the middle outward.', 'Glue weeps evenly at both ends; no scorching.'),
  ('Finish one lug', 'On a 2 AWG offcut (P061): slide a boot (P066) and a length of heavy-wall adhesive shrink (from P077) on first, crimp a P064 lug with the hydraulic crimper at D4\'s die, shrink the heavy-wall over the barrel and the first of the insulation, then slide the boot over.', 'Glue at both ends of the shrink; the boot covers the barrel.', 'Boot and shrink go on the cable BEFORE the lug: they do not pass over it afterwards.'),
  ('Put the plug kit back in its bag and tick', 'Wedgelock and plug back in the P124 bag, labelled. Tick E5.', 'E5 done; E6 ready.'))

# ---------------------------------------------------------------- E6
relay_labels = ' · '.join(r['id'] + ' ' + r['label'] for r in RELAYS)
fuse_labels = ' · '.join(r['id'] + ' ' + r['label'] for r in FUSES)
B('E6',
  'The label printer is set up, one test label has survived wrap, shrink and tug, and the node labels for every relay and fuse position are printed.',
  'bench', '1.5 h - confirm',
  L('Label printer, Brother PT-D220 (P041)', 'Heat gun (P042)', 'Scissors'),
  'P041 P075 P076 P008',
  L('E5 is done'),
  L('Every wire is labelled at both ends with printed laminated tape - Brother PT-D220, TZe-FX231 flexible-ID tape, 12 mm black on white - never tape and marker, the moment it is cut [rules label-format]',
    'Both ends carry the same pair read in opposite order, from / to: O8 / L2-M-1 at the PMU end and L2-M-1 / O8 at the other [rules label-format]',
    'Wrap about 45 mm with the text outside and rub it down; where a wrap would not read, fold it into a flag [rules label-format]',
    'Under loom, in the engine bay or through a grommet, clear heat-shrink goes over the label [rules label-format]',
    'Node labels go on the panel beside each relay socket and fuse position, empty ones included, from the label columns [rules label-format; work E14]',
    'There are %d relays and %d fuse positions in the tables today [relays; fuses]' % (len(RELAYS), len(FUSES)),
    'The build has about 582 wire ends to label, about 26 m of tape at 45 mm; a cartridge is 8 m, so four [params label_ends; parts P075]',
    'F13 has no label text (a dash) in the table: it is an empty position [fuses F13]'),
  'A TEST / L0-X0 label wrapped on a 16 AWG offcut, under clear shrink, that stays put when tugged; and one printed label for each relay and each fuse position, kept in order on a card.',
  'A label that slides or unwraps after shrinking: wrap it tighter with more overlap and rub it down before the shrink. Tape that is not TZe-FX231 (the flexible one) lifts off round wire: do not use it.',
  'Tick the row.')
S('E6',
  ('Load the tape', 'A TZe-FX231 cartridge (P075, 12 mm black on white, flexible-ID) into the PT-D220 (P041). Batteries or its adapter in.', 'The printer feeds and cuts.'),
  ('Print the test label', 'Type TEST / L0-X0 and print one.', 'A clean 12 mm label.'),
  ('Wrap it on a 16 AWG offcut', 'About 45 mm of label wrapped round the wire with the text outside; rub it down.', 'The text reads along the wire.'),
  ('Shrink clear tube over it', 'A piece of clear 3/16 in heat-shrink (P076) over the label; shrink with the heat gun (P042) on low.', 'Tube tight, text readable through it.'),
  ('Tug it', 'Pull the label along the wire with your fingers.', 'It does not move.'),
  ('Print the relay labels', 'One label each, the id is where it goes and the word is the label: ' + relay_labels + '. Whether the id is printed with the word is not in the record: printing both loses nothing.', '%d labels.' % len(RELAYS)),
  ('Print the fuse labels', fuse_labels + '.', '%d labels; F13\'s reads as an empty position.' % len(FUSES)),
  ('Keep them in order', 'Stick each on a card or backing sheet in table order, marked RELAYS and FUSES. They go on the dash node at E14 and at the sill and bay as each part is fitted.', 'One card, all labels on it.'),
  ('Tick the row', 'Tick E6.', 'E6 done; E7 ready.'))

# ---------------------------------------------------------------- E7
B('E7',
  'Every resistor and diode the switch ladders use is soldered to 4 in leads, heat-shrunk, measured, labelled with its switch and position, and bagged with its measured value written on the bag.',
  'bench', 'an evening, about 3 h - confirm',
  L('Soldering iron and solder (P044)', 'Multimeter on ohms (P045)', 'Heat gun (P042)', 'Wire strippers and flush cutters (P043)', 'Label printer (P041)', 'Small bags and a marker'),
  'P069 P161 P071 P197 P077 P010 P075',
  L('E6 is done: the label printer works',
    'The wake stages are designed (A10, done)',
    'Eye protection when cutting leads'),
  L('A ladder is a set of resistors on a switch so one PMU input wire can tell every switch position apart by its resistance [ladders]',
    'Resistors come from the 1 % metal-film kit P069 [parts P069]',
    'Each sub-assembly is checked again in the car: ohms at the plug against the table, within 2 % [work E20]',
    'Key switch, input A16 (wire L3-S1 1): ACC 33 kΩ · IG 15 kΩ · ST 6.8 kΩ, all onto one wire [cavities L3-S1 1; ladders A16]',
    'Light switch E-01, input A15 (L3-S1 2): PARK 33 kΩ · HEAD 15 kΩ · DIMMER-HI 8.2 kΩ · PASS 3.3 kΩ [cavities L3-S1 2; ladders A15]',
    'Turn stalk F-02, input A1 (L3-S1 3): LEFT 1.8 kΩ · RIGHT 10 kΩ · OFF 47 kΩ [cavities L3-S1 3; ladders A1]',
    'Wiper stalk D-03, input A2 (L3-S1 4): HIGH 4.7 kΩ · LOW 10 kΩ · INT 18 kΩ · OFF 47 kΩ [cavities L3-S1 4; ladders A2]',
    'Wiper WASH leg: 470 Ω + 1N4148, band toward the contact - the ladders, cavity and device rows agree [ladders A2 WASH; cavities L3-S1 4; parts P161]',
    'Brake pedal switch, input A3 (L3-S1 5): 4.7 kΩ. Wiper park, also A3 (L2-S 3): 12 kΩ at the motor\'s terminal L, and a 47 kΩ baseline to the front ground at the L2-S plug [cavities L3-S1 5, L2-S 3; ladders A3]',
    'Hazard switch, input A8 (L3-S1 6): 4.7 kΩ, and a 47 kΩ baseline to column ground at the switch. Horn pad (L3-S1 11): 8.2 kΩ [cavities L3-S1 6, L3-S1 11; ladders A8]',
    'The two wink resistors (18 kΩ, 33 kΩ) are on the wink plate\'s circuit board, not made here [cavities L3-S1 11; D-504]',
    'Gear selector (inhibitor) switch A-06: 8.2 kΩ in the lead to terminal BY (input A4, L1-S1 11) and 8.2 kΩ in the lead to GY (input A5, L1-S2 7), each with a 47 kΩ baseline to the block ground at the switch [cavities L1-S1 11, L1-S2 7; D-487]',
    'Door jamb switches, input A6 (L4-S 2): driver 24 kΩ + 1N4148, passenger 8.2 kΩ + 1N4148, diode anodes toward the splice; a 47 kΩ baseline from the sill splice to the sill ground [cavities L4-S 2; D-486]',
    'Two 1N4007 diodes (P197) go on the interior lamp\'s RY wire, one at each jamb switch, anode on RY [parts P197; D-486]',
    'The 47 kΩ baselines on A3, A6 and A8 are not fitted in the car until the wake stages have passed their bench test CK12 [work E7; checks CK12]',
    'The light switch\'s PASS contact is unproven: a 1980 table shows no separate contact. Make the 3.3 kΩ part, but its use waits on the switch measurement CK17 [checks CK17]'),
  'One labelled bag per switch position in the lists above, each with a resistor (and its diode where named) on two 4 in leads under heat-shrink, each measured within 1 % of its value and the reading written on the bag.',
  'A part that reads outside 1 % of its marked value: bin it and make another - the in-car check allows 2 % in all. A diode that reads open both ways or short both ways: bin it. The WASH leg: if the tables still disagree when you reach it, leave it unmade and raise it in the app as a note.',
  'Tick the row. Note any value you could not make (the WASH leg) in the app.')
S('E7',
  ('Lay out the kit and print the labels', 'Resistor kit P069, diodes 1N4148 (P161), 1N4007 (P197), 16 AWG grey offcuts (P010) cut into 4 in (100 mm) leads, adhesive shrink (P077). Print one label per part: the switch and the position, e.g. the key switch\'s three read A16 ACC, A16 IG, A16 ST.', 'Labels printed; leads cut.'),
  ('Make one part, the pattern for all', 'Measure the bare resistor first. Solder a 4 in lead to each end, slide heat-shrink over the whole resistor and both joints, shrink, and wrap the label on one lead.', 'A resistor with two insulated leads and a label.', 'Hot iron and molten solder: eye protection, and let the joint cool before the shrink.'),
  ('Measure it and bag it', 'Meter on ohms across the two lead ends. Write the reading on the bag with the label\'s text.', 'Within 1 % of the marked value.'),
  ('Key switch (A16): three parts', '33 kΩ labelled ACC · 15 kΩ labelled IG · 6.8 kΩ labelled ST.', 'Three bags.'),
  ('Light switch (A15): four parts', '33 kΩ PARK · 15 kΩ HEAD · 8.2 kΩ DIMMER-HI · 3.3 kΩ PASS.', 'Four bags; the PASS bag marked "waits on CK17".'),
  ('Turn stalk (A1): three parts', '1.8 kΩ LEFT · 10 kΩ RIGHT · 47 kΩ OFF.', 'Three bags.'),
  ('Wiper stalk (A2): four parts', '4.7 kΩ HIGH · 10 kΩ LOW · 18 kΩ INT · 47 kΩ OFF.', 'Four bags.'),
  ('Wiper WASH leg', '470 Ω in series with a 1N4148, band toward the contact (ladders A2 WASH; the cavity row says the same). Resistor and diode in series on one lead, under one piece of shrink, the diode\'s band end marked on the outside.', 'One bag.', 'A diode soldered the wrong way round reads as a switch never pressed.'),
  ('Brake and wiper park (A3): three parts', '4.7 kΩ BRAKE (pedal switch) · 12 kΩ PARKED (wiper motor terminal L) · 47 kΩ A3 BASELINE (front ground at the L2-S plug).', 'Three bags; the baseline bag marked "not before CK12".'),
  ('Hazard and horn (A8): three parts', '4.7 kΩ HAZARD · 47 kΩ A8 BASELINE (column ground at the hazard switch) · 8.2 kΩ HORN. The wink resistors are on the plate board: not made here.', 'Three bags; the baseline bag marked "not before CK12".'),
  ('Gear selector switch (A4, A5): four parts', '8.2 kΩ A4 P/N (lead to terminal BY) · 47 kΩ A4 BASELINE · 8.2 kΩ A5 REVERSE (lead to terminal GY) · 47 kΩ A5 BASELINE.', 'Four bags.'),
  ('Door jambs (A6): three parts', '24 kΩ + 1N4148 DRIVER · 8.2 kΩ + 1N4148 PASSENGER, each resistor and diode in series with the diode\'s anode (the end without the band) toward the splice · 47 kΩ A6 BASELINE (sill splice to sill ground).', 'Three bags; the baseline bag marked "not before CK12".', 'Mark the band end on the outside of the shrink.'),
  ('Interior lamp diodes: two parts', 'Two 1N4007 (P197), each on two leads under shrink, labelled RY DRIVER and RY PASSENGER, the anode end marked: the anode goes to the lamp\'s RY wire.', 'Two bags.'),
  ('Check each diode part with the meter', 'Meter on diode test: one way reads about 0.5 to 0.7 V, the other way open. Through a resistor-and-diode part use ohms both ways: one way the resistor\'s value or a little more, the other way open.', 'Every diode part conducts one way only.'),
  ('Count the bags against the list', 'Key 3 · light 4 · turn 3 · wiper 4 (+ WASH) · brake and park 3 · hazard and horn 3 · gear selector 4 · doors 3 · lamp diodes 2.', '29 bags, or 30 with the WASH leg.'),
  ('Tick and note', 'Tick E7. Note the WASH leg\'s state in the app if it was left.', 'E7 done; E8 ready.'))

# ---------------------------------------------------------------- E8
B('E8',
  'The factory battery and its two cables are out, and the Ionic battery sits in the cargo bin on its backing plate, held down so it cannot move, with both terminals booted and nothing connected.',
  'engine bay, then the passenger-side cargo bin and under the rear floor', 'a weekend',
  L('Spanners and sockets for the factory battery clamps, hold-down and the starter stud nut - sizes not in the record: note them',
    'Drill and bits for the M8 hold-down hardware', 'File or deburring tool, saw for the plate stock',
    'Jack stands and wheel chocks', 'Camera', 'Tape and labels', 'Eye protection'),
  'P057 P092 P093 P094',
  L('E7 is done',
    'The interior is stripped, the cargo-bin trim out (S1), and the M-4 cargo-bin mock-up exists (C1)',
    'D2 has fit-checked the hold-down, the post clamps and the boots',
    'Key out. Rings and watch off. Wheels chocked; jack stands if you go under the car',
    'Eye protection for drilling and cutting'),
  L('The factory battery is a lead-acid in the engine bay, in the factory location [00-CAR PT024]',
    'The negative cable comes off first and goes on last [S-002 p.5-5]',
    'The factory positive cable feeds the starting motor directly and, through the black 1.25 sq main fusible link at X-07, the car\'s constant supply [00-CAR PT289]',
    'The factory negative cable goes from the post to ground; whether that is the body or the engine is not drawn - look on the car [00-CAR PT290]',
    'Both factory battery cables come off with the battery and are not reused [work E8]',
    'The fusible links - one black main, two brown - stay on the car: E11 puts them on the new backbone. The 1985 manual places them at the front left suspension tower - confirm on the car [00-CAR SP-063, PT316, PT317]',
    'The Ionic goes in the passenger-side cargo bin, with the amplifier beside it later [devices DV60; cables C13]',
    'Its case is 170 W x 230 L x 190 H mm; terminals and boots stand above that [params battery_case_mm; D-239]',
    'The battery mounts on a backing plate under the floor, never through sheet metal alone: the plate turns a tearing load into a shear load in a crash [D-063]',
    'Hold-down: clamp and J-hooks, M8 grade-8 bolts, nyloc nuts, fender washers (P057); plate stock 3 to 4 mm aluminium or steel (P092) cut from the M-4 mock-up [parts P057, P092]',
    'Terminals are covered by boots and nothing else, and a hand must reach a post for a jump start with the boots on [D-235; work V-088]',
    'The fuel pump and tank sender wiring run under the rear floor to the tank [routes RT17]',
    'Not in the record: the hold-down\'s torque, the drill size, and what lies directly under the bin floor - look before drilling [work E8; parts P057]'),
  'The factory battery and both its cables are out and bagged; the fusible-link block is still on the car with its battery-side lead taped and labelled; the Ionic is clamped on its backing plate and does not move when pushed hard in every direction; both terminals are booted; nothing is connected to it.',
  'The battery moves under a hard push: do not go on - re-make the hold-down or the plate. Something is in the way under the floor (a line, the tank, a brace): do not drill; move the mock-up and note it in the app. The factory positive cable has branches you cannot identify: leave them connected at their far ends, tape and label the battery end, photograph, and note it for E11.',
  'Tick the row. Note in the app: where the factory negative cable was bolted, how the fusible-link block was joined to the positive cable, and the spanner sizes used.')
S('E8',
  ('Make the car safe', 'Key out, wheels chocked, car in P. Rings and watch off. If you go under for the starter cable, the car is on jack stands.', 'Car cannot roll; nothing switched on.', 'Never under the car on a jack alone.'),
  ('Photograph the factory battery and both cables', 'In the engine bay: the battery, each clamp, every lead on each clamp, the positive cable\'s run to the starter and to the fusible-link block, the negative cable to its ground bolt.', 'Each cable\'s two ends on a photo.'),
  ('Disconnect the negative cable first', 'Loosen the negative clamp and lift it off the post; tuck it where it cannot spring back.', 'Negative clamp off and clear.', 'Negative first: with it off, a spanner touching the body from the positive post makes no spark.'),
  ('Disconnect the positive cable and lift the battery out', 'Positive clamp off. Undo the factory hold-down and lift the battery out upright.', 'Battery on the floor, away from the car.', 'A lead-acid battery is heavy and holds acid: lift with both hands, keep it upright.'),
  ('Write down how the positive cable is built', 'The positive cable (Mazda 8872-67-250B, clips 1011-67-291A and 1011-67-293) goes to the starter\'s main stud and feeds the fusible-link block X-07. Note exactly how the link block gets its supply: a ring under the clamp bolt, a branch crimped into the cable, or a separate lead. Note its wire size if printed.', 'A sketch or photo and one sentence.', 'E11 lands this feed on the new backbone: without this note you will be guessing then.'),
  ('Write down where the negative cable went', 'Follow the negative cable (Mazda 8871-67-260A) to its bolt: body or engine, and any second small lead from the clamp to the body.', 'The ground point named and photographed.'),
  ('Remove the positive cable', 'Undo the nut on the starter\'s main B+ stud, lift the cable\'s ring off, and put the nut back finger-tight. The small wire on the starter\'s S terminal (factory BW) stays. Free the cable from its clips. Leave the fusible-link block and its three links on the car: tape and label its battery-side lead "MAIN FEED - TO POST (E11)".', 'Cable out; link block untouched; its feed lead insulated and labelled.', 'Do not cut a fusible link or its wire.'),
  ('Remove the negative cable', 'Unbolt it at its ground point and take it out. If a small body lead shared the clamp, tape and label it "FACTORY GROUND - TO FRONT STAR (E11)".', 'Cable out.'),
  ('Bag and label the factory parts', 'Battery cables, clamps and hold-down in a bag marked "factory battery cables - not reused".', 'One labelled bag.'),
  ('Boot the Ionic\'s terminals', 'Before the Ionic goes near the car: red and black boots (P094) on its posts or post clamps.', 'No metal showing on either terminal.', 'Lithium: a tool across the posts welds.'),
  ('Cut the backing plate', 'From the P092 stock (3 to 4 mm aluminium or steel), to the outline of the M-4 cardboard mock-up. Deburr every edge. If it is aluminium, paint it (P093).', 'A plate matching the mock-up, no sharp edges.'),
  ('Look under the floor, then mark the holes', 'Set the mock-up in the passenger-side cargo bin where M-4 put the battery. Go under the car and look at what is beneath that floor: the tank, the pump and sender wiring, brake and fuel lines. Mark the hold-down holes only where the plate sits flat and nothing is behind.', 'Hole positions marked with clear space under each.', 'Drilling into a fuel or brake line, or the tank, is the worst mistake of the weekend. No sparks near the tank.'),
  ('Drill and bolt the hold-down through floor and plate', 'Drill for the M8 hardware. From above: the hold-down\'s J-hooks or bolts (P057, M8 grade-8) through the floor; beneath: the backing plate, a fender washer and a nyloc nut on each. Torque is not in the record: tighten firmly and evenly, and note it.', 'Plate tight against the underside; bolts cannot turn.', 'Never through sheet metal alone: the plate must be under every bolt.'),
  ('Seat the battery', 'Lower the Ionic (170 x 230 x 190 mm) into place as mocked up, with a post reachable by hand for a jump start with the boots on.', 'Battery flat on the bin floor, posts reachable.'),
  ('Fit the hold-down clamp', 'Clamp over the case, clear of both terminals and boots; tighten its nuts evenly.', 'Clamp bears on the case only.'),
  ('Push it hard every way', 'Push and pull the battery forward, back, each side and up.', 'It does not move at all.', 'If it shifts, it is not done: a loose battery with live terminals is a projectile in a crash.'),
  ('Leave it unconnected, booted, and tick', 'Both boots on. No cable goes on the Ionic this weekend. Tick E8 and enter the notes from steps 5 and 6.', 'E8 done; E9 ready.'))

# ---------------------------------------------------------------- E9
B('E9',
  'The master disconnect and the Class-T fuse block are mounted beside the battery, the rear ground stud is made on bare metal, and the three short battery cables are cut, crimped, booted and bolted on - with the fuse out, the switch off and the negative lug still off the battery.',
  'passenger-side cargo bin', 'a weekend',
  L('Hydraulic lug crimper, 8 AWG to 1/0, with dies (P037), at the dies that passed at D4',
    'Heat gun (P042)', 'Torque wrench 1/4 in drive, 2-20 N·m (P046) - and a larger one if a maker\'s figure is above 20 N·m (none is in the parts table)',
    'Cable cutter or fine hacksaw for 1/0', 'Knife for stripping heavy cable', 'Grinder or abrasive for bare metal', 'Drill',
    'Multimeter on ohms (P045)', 'Label printer (P041)', 'Paint pen (from P082)', 'Eye protection'),
  'P049 P047 P048 P058 P059 P082 P095 P096 P097 P061 P098 P064 P066 P077 P075',
  L('E8 is done: the Ionic is held down, booted, unconnected',
    'The torque figures read at D1 are in front of you',
    'Rings and watch off; both battery terminals booted whenever you are not on them',
    'Eye protection for grinding and crimping',
    'The Class-T fuse stays OUT all weekend'),
  L('The master disconnect is a Blue Sea 9003e (350 A continuous, 1500 A cranking), on the battery POSITIVE, within reach from the hatch. It carries both the PMU leg and the starter leg, so opening it kills the whole car [parts P049; D-319; work E9]',
    'The Class-T block is a Blue Sea 5007100 with a 150 A fuse (Blue Sea 5114): the only common fuse that can break a lithium short. It mounts as close to the positive post as physically possible - inches [parts P047, P048; D-062]',
    'C12: battery + clamp stud to the disconnect\'s INPUT stud, 1/0 red, 1.0 ft - a hand estimate, confirm. It is the one cable no fuse protects: keep it to inches [cables C12; D-062]',
    'C01: the disconnect\'s OUTPUT stud to the Class-T block\'s input, 2 AWG red, 1.0 ft - a hand estimate, confirm. Its lug sits on the output stud UNDER the MRBF fuse holder that goes on at E10 [cables C01]',
    'C05: battery - clamp stud straight to the rear ground stud, 1/0 black, 3 ft - a hand estimate, confirm. The negative is never switched [cables C05; backbone B5]',
    'Lugs: 1/0 are P098 (3/8 in hole for the disconnect, the ground studs and the clamp studs; 5/16 for the MRBF holder), 2 AWG are P064 (5/16 and 3/8 holes) - the hole at each stud is confirm until the studs are measured [parts P098, P064, P095; checks CK24]',
    'Rear ground stud: bare metal, a 3/8 in stainless stud (P058), a star washer (P059), torqued, cavity wax (P082) over the joint [work E9; backbone B5]',
    'The same stud is the rear star: the table also holds a 10 AWG conductor from it to the chassis (G23, 2 ft, confirm) [grounds G23; cables C14; work E9]',
    'Every lug gets heavy-wall adhesive shrink and a boot [work E9; parts P066, P077]',
    'Every heavy connection is torqued to its maker\'s figure and paint-marked; none of the figures is in the record yet - use the ones you read at D1 [rules torque]',
    'The positions of the switch, the block and the stud come from the M-4 mock-up; none is in the record [work V-088]'),
  'Disconnect and Class-T block mounted; rear ground stud on bare metal, waxed; C12, C01 and C05 made with a lug, heavy-wall shrink and a boot at each end, labelled; C12 and C01 bolted and torqued; C05 bolted at the stud with its battery end off and insulated; switch OFF, Class-T fuse out; meter shows continuity through the switch ON and open with it OFF.',
  'A lug that turns on its cable or shows strands: cut it off and crimp a new one (the spares are for this). A hole that does not match its stud: stop, note the sizes, and do not drill a lug out. No continuity through the switch when ON: check each nut and the switch itself before going on.',
  'Tick the row. Note the three cables\' real cut lengths (C12, C01, C05) and the torque you used at each stud in the app.')
S('E9',
  ('Make the bin safe', 'Both battery terminals booted, nothing connected to the battery, rings and watch off. The disconnect, when fitted, stays OFF; the Class-T fuse stays in its box.', 'Battery isolated.', 'Lithium: one slip with a spanner across the posts welds.'),
  ('Mount the master disconnect', 'Blue Sea 9003e (P049), where the M-4 mock-up put it: within reach from the open hatch, inches from the positive post. Its fasteners are not in the record: note them. Turn it OFF.', 'Switch solid, reachable from the hatch, OFF.'),
  ('Mount the Class-T block', 'Blue Sea 5007100 (P047) beside the disconnect, as close to the positive post as physically possible. Leave the 150 A fuse (P048) out; keep its cover to hand.', 'Block solid, inches from the post, no fuse in it.'),
  ('Make the rear ground stud', 'On bare structural metal within reach of the negative post (C05 is estimated at 3 ft). Grind to bright metal. Fit a 3/8 in stainless stud (P058) with a star washer (P059) biting the bare metal; how the stud is fixed through the panel is not in the record: note it. Torque it, then cavity wax (P082) round the stud-to-body joint.', 'A solid stud on bright metal, waxed at its base.', 'Look behind the panel before drilling: the tank and its wiring are under the rear floor.'),
  ('Lay C12 in place and mark it', 'Hold the 1/0 red cable (P096) from the positive clamp\'s 3/8 stud to the disconnect\'s INPUT stud along the path it will take, with a gentle bend and no strain. Mark the cut. The table\'s 1.0 ft is an estimate: the length is what the two studs need, kept to inches.', 'A cut mark; the real length written down.', 'This cable has no fuse: shorter is safer, and nothing may chafe it.'),
  ('Make C12', 'Cut. Slide on a red boot (P066) and a length of heavy-wall shrink (from P077) for each end FIRST. Strip each end to the depth of the lug\'s barrel. Fit a 1/0 lug (P098, 3/8 in hole) fully home and crimp with the hydraulic crimper (P037) and the 1/0 dies as at D4. Shrink the heavy-wall over barrel and insulation until glue shows at both ends; slide the boots up. Label both ends C12, from / to.', 'Two lugs that cannot be twisted by hand; glue at both ends of each shrink; both lug faces lie flat on their studs with the cable relaxed.', 'Boot and shrink on before the second lug. Fingers out of the die.'),
  ('Make C01', '2 AWG red (P061) from the disconnect\'s OUTPUT stud to the Class-T block\'s input stud; table estimate 1.0 ft. Mark in place, cut, boots and shrink on, lugs P064 with the hole each stud needs, crimp with the 2 AWG die, shrink, label C01.', 'As C12.'),
  ('Make C05', '1/0 black (P097) from the negative clamp\'s 3/8 stud straight to the rear ground stud; table estimate 3 ft. Mark in place, cut, black boots and shrink on, P098 lugs (3/8 in hole), crimp, shrink, label C05.', 'As C12.'),
  ('Bolt C12 on', 'One end on the positive clamp\'s stud (lift the red boot, refit it over the stack), the other on the disconnect\'s INPUT stud. Torque each to the maker\'s figure you read at D1; paint-mark each nut.', 'Both nuts torqued and marked; the post boot back on over the lug.', 'The INPUT stud is now live. The switch stays OFF.'),
  ('Bolt C01 on', 'One lug on the disconnect\'s OUTPUT stud - snug only for now, because the MRBF holder stacks on top of it at E10 - and the other on the Class-T block\'s input stud, torqued to Blue Sea\'s figure and paint-marked.', 'C01 in place; the Class-T end torqued and marked.'),
  ('Bolt C05 at the stud only', 'C05\'s lug on the rear ground stud over a star washer, nut snug (the cranking return C11 joins it at E10). Leave its battery end OFF the negative clamp: boot it, tape it and tie it back.', 'Negative cable fixed at the stud, free and insulated at the battery.', 'The negative lug stays off until E11: that is what keeps the car dead.'),
  ('Check through the switch with the meter', 'Meter on ohms, one probe on the positive clamp\'s stud (under the boot), the other on the Class-T block\'s input stud. Switch ON, then OFF.', 'ON: continuity, under 1 ohm. OFF: open circuit.'),
  ('Leave it safe', 'Switch OFF. Class-T fuse out. Both post boots on. Tools out of the bin.', 'Nothing live beyond the disconnect\'s input stud.'),
  ('Tick and note', 'Tick E9; enter the three cut lengths and the torques used as a note in the app.', 'E9 done; E10 ready.'))

# ---------------------------------------------------------------- E10
B('E10',
  'The starter feed, the cranking return and the PMU feed run from the cargo bin through the tunnel to the engine bay and the dash; the front ground stud, the engine-to-chassis strap and the two MIDI fuse holders are fitted; everything is still dead, fuses out.',
  'cargo bin, the tunnel, under the car, engine bay and the dash-node position', 'a weekend',
  L('Hydraulic lug crimper, 8 AWG to 1/0, with dies (P037)',
    'Ratchet crimper for insulated and heat-shrink terminals, 22-10 AWG (P171)',
    'Heat gun (P042)', 'Torque wrench 1/4 in drive, 2-20 N·m (P046) and a larger one where a figure needs it',
    'Cable cutter, knife, string for laying routes', 'Grinder or abrasive for bare metal', 'Drill',
    'Jack stands and wheel chocks', 'Multimeter on ohms (P045)', 'Label printer (P041)', 'Paint pen (from P082)', 'Eye protection'),
  'P051 P052 P050 P053 P054 P055 P058 P059 P082 P081 P096 P097 P061 P062 P063 P098 P064 P065 P066 P077 P017 P079 P075',
  L('E9 is done: disconnect OFF, Class-T fuse out, the negative lug off the battery',
    'The console and tunnel trim are out (S1) and the tunnel was measured for three heavy cables (C1, M-2)',
    'Car on jack stands, wheels chocked, for the starter and the block',
    'Engine cold',
    'Eye protection for grinding and crimping'),
  L('The MRBF fuse holder is a Blue Sea 5191 (P051); it bolts on the master disconnect\'s OUTPUT stud, not on the battery post, with C01\'s lug under it. Its 250 A fuse (P052) is NOT fitted yet [fuses MRBF; cables C02; parts P051]',
    'C04, the starter feed: 1/0 red from the MRBF holder to the starter\'s main B+ stud, 18 ft - a hand estimate, confirm [cables C04; devices DV02]',
    'C11, the cranking return: 1/0 black from the rear ground stud to the engine block, 18 ft - a hand estimate, confirm; pulled beside the starter feed. Without it 400 A would cross the whole body shell [cables C11; backbone B7]',
    'C03, the PMU feed: 2 AWG red from the Class-T block to the dash post, 16 ft - a hand estimate, confirm [cables C03]',
    'All three go through the tunnel, loomed, P-clipped every 12 in, with a grommet at every pass-through [routes RT15; work E10]',
    'C03 ends for now on a temporary insulated post, a Blue Sea 2003 PowerPost with a 3/8 in stud (P050), mounted where the dash node will go [parts P050; work E10]',
    'A pull string goes in beside C03 before the console goes back [work E10; parts P081]',
    'Front star stud (G05): on the radiator support, bare metal, 3/8 stud, star washer, torque, wax; plus a 10 AWG black wire, 2 ft estimated, from the stud to a second body bolt [grounds G05; work E10]',
    'C06, the engine block to chassis strap: 2 AWG black, 2 ft estimated, 24 in or less. It is the bond, not the cranking return [cables C06; backbone B6]',
    'F17 (30 A) and F18 (100 A) are MIDI fuses in Blue Sea 7720 holders (P053, M6 mounting) beside the starter B+ stud [fuses F17, F18; parts P053, P054, P055]',
    'C07: alternator B+ to F18 to the starter B+ stud, 6 AWG red, 4 ft estimated, lugs P065 (5/16 hole, confirm) [cables C07; parts P065]',
    'F17 feeds the start relay K9 and stays unwired until K9 is wired at E27 [fuses F17; work E10, E27]',
    'Lugs: P098 for 1/0 (5/16 hole at the MRBF holder, 3/8 at the ground studs and the block), P064 for 2 AWG - holes confirm against the studs measured at CK24 [parts P098, P064; checks CK24]',
    'Not in the record: which bolt on the block and on the chassis each ground cable lands on, where exactly the MIDI holders mount, and whether the factory wire already on the alternator\'s B stud stays - note what you do [work E10; devices DV04]'),
  'C04, C11 and C03 lie loomed and clipped through the tunnel with every end lugged, shrunk, booted and labelled; C04 is on the starter stud and the MRBF holder; C11 and C05 share the rear ground stud, torqued and waxed; C03 is on the Class-T output and the temporary post; the front star stud and its 10 AWG wire, the block strap and both MIDI holders are fitted; the pull string is in; the meter shows the continuities in the steps; both big fuses are still out.',
  'A cable that comes up short: do not join heavy cable - re-run it from the reel (the order holds 1.5 x the estimates) and note the real length. A cable that cannot be clipped clear of the exhaust or a moving part: stop and re-route. No continuity where a step expects it: re-check that end\'s lug and nut before anything else.',
  'Tick the row. Note the real lengths of C03, C04, C11, C06 and C07, the bolts used for the block and chassis ends, and the torques, in the app.')
S('E10',
  ('Make it safe', 'Disconnect OFF, Class-T fuse out, C05\'s battery end still off and insulated, post boots on. Car on jack stands, wheels chocked, engine cold.', 'Car dead and solid on its stands.', 'Never under the car on a jack alone.'),
  ('Fit the MRBF holder on the disconnect\'s output stud', 'Blue Sea 5191 holder (P051) onto the OUTPUT stud, on top of C01\'s lug. Torque to Blue Sea\'s figure (read at D1); paint-mark. Do NOT fit the 250 A fuse (P052).', 'Holder solid on the stud with C01 under it; no fuse.', 'On the disconnect\'s output stud, never the battery post: the disconnect then kills the starter cable too.'),
  ('Lay the three tunnel routes with string', 'From the cargo bin forward through the tunnel: one string to the starter\'s main stud, one to the engine block, one to the dash-node position. Follow the path the cables will take, away from the exhaust, the propeller shaft and the shifter. Measure each string.', 'Three measured lengths written down - they replace the table\'s estimates of 18, 18 and 16 ft.', 'Heat and moving parts: nothing heavy may touch the exhaust or the shaft.'),
  ('Pull C04, the starter feed', '1/0 red (P096) off the reel along its string from the MRBF holder to the starter. Leave it long at both ends. Loom it (P081); a grommet wherever it passes through metal.', 'Red 1/0 from bin to starter, in loom, uncut at the starter end.'),
  ('Pull C11, the cranking return, beside it', '1/0 black (P097) from the rear ground stud to the engine block, in the same run as C04. Loom; grommets.', 'Black 1/0 beside the red, bin to block.'),
  ('Pull C03, the PMU feed, with its pull string', '2 AWG red (P061) from the Class-T block\'s output stud through the tunnel to the dash-node position. Loom its full length; grommets at every pass-through. Lay the pull string (from P081) beside it the whole way and tie off both ends.', 'Red 2 AWG from bin to dash, and a string beside it you can pull from either end.', 'The string must be in before the console goes back: it is how later wires get through.'),
  ('P-clip all three every 12 in', 'P-clips (P081) every 12 in along each cable, onto existing or new fixings; no cable hangs or can move against an edge.', 'A clip every 12 in; nothing sags.'),
  ('Terminate C04 at the bin and bolt it on', 'Cut to length at the MRBF holder. Boot and heavy-wall shrink on first; P098 lug with the 5/16 in hole; crimp (1/0 dies), shrink, label C04. Bolt it to the holder\'s fuse stud; torque; paint-mark.', 'C04 on the MRBF holder.'),
  ('Terminate C04 at the starter and bolt it on', 'Cut at the starter\'s main B+ stud. Boot and shrink on; a P098 lug whose hole matches the stud (measured at CK24); crimp, shrink, label. Fit it on the main stud where the factory cable was; nut torqued to the maker\'s figure - not in the record, confirm; paint-mark; boot over.', 'C04 on the starter\'s main stud; the small S-terminal wire untouched.', 'The starter stud is live whenever the disconnect is ON and the MRBF is in: boot it.'),
  ('Terminate C11 at both ends', 'Engine end: a P098 lug (3/8 in hole) on a clean, bare threaded boss on the block - which bolt is not in the record: note it. Bin end: a P098 lug onto the rear ground stud on top of C05\'s. Boots, shrink, labels as before.', 'C11 bolted to the block and to the rear stud.'),
  ('Torque and wax the rear ground stud', 'With C05 and C11 both on it: torque, paint-mark, cavity wax (P082) over the whole joint. The stud\'s own 10 AWG bond to a second body bolt (G23) goes on before the wax, with a P079 ring, if it was not fitted at E9.', 'Rear stud finished and waxed.'),
  ('Mount the temporary post and land C03', 'Blue Sea 2003 PowerPost (P050, 3/8 in stud, insulated) where the dash node will go (from M-1). Terminate C03 with P064 lugs: one on the Class-T block\'s OUTPUT stud, one on the post. Torque both to Blue Sea\'s figures; paint-mark; cover on the post.', 'C03 from Class-T output to the post; the post covered.'),
  ('Make the front star stud', 'On the radiator support: grind to bare metal, 3/8 in stainless stud (P058), star washer (P059), torque, cavity wax (P082).', 'Stud on bright metal, waxed.'),
  ('Run the front star\'s 10 AWG wire', '10 AWG black GXL (P017), about 2 ft, from the front star stud to a second bare-metal body bolt. A heat-shrink ring (P079, 12-10 AWG) at each end, crimped with P171, shrunk. Label G05.', 'Stud bonded to the body by a second path.'),
  ('Fit the engine block to chassis strap, C06', '2 AWG black (P062), 24 in or less, P064 lugs, from a bare boss on the block to bare metal on the chassis; which bolts is not in the record: note them. Boots and shrink; torque; wax the chassis end.', 'A short black strap, block to body, both ends on bright metal.'),
  ('Mount the two MIDI holders beside the starter stud', 'Two Blue Sea 7720 blocks (P053) on M6 fixings near the starter\'s main stud, covers to hand. Label them F17 START-RLY and F18 ALTERNATOR (labels from E6).', 'Two holders mounted and labelled.'),
  ('Make C07 through F18', '6 AWG red (P063) in two pieces with P065 lugs: starter main stud to F18\'s one stud, and F18\'s other stud to the alternator\'s B stud - about 4 ft in all. Fit the 100 A fuse (P055, Blue Sea 5256) in F18; cover on. The factory WR wire on the alternator\'s B stud: the row does not say to remove it and the factory harness is not migrated until E28 - leave it on the stud and note it.', 'Alternator B to F18 to starter stud in 6 AWG; 100 A fuse in; cover on.', 'A 150 A MIDI must not go here: 6 AWG needs the 100 A.'),
  ('Leave F17 unwired', 'F17\'s holder is fitted and empty of wires. Its 30 A fuse (P054, Blue Sea 5250) stays in its bag, taped to the holder, until K9 is wired at E27.', 'F17 holder mounted, nothing on it.'),
  ('Check with the meter, everything dead', 'Meter on ohms. Rear ground stud to engine block: continuity, under 1 ohm. Engine block to chassis: under 1 ohm. Class-T output stud to the temporary post: under 1 ohm. MRBF holder\'s fuse stud to the starter\'s main stud: under 1 ohm. The temporary post to chassis: open circuit.', 'Four continuities and one open.', 'An open post-to-chassis reading matters: anything else means C03 is chafed through somewhere.'),
  ('Tick and note', 'Disconnect still OFF, both big fuses still out. Tick E10; enter the lengths, bolts and torques as a note.', 'E10 done; E11 ready.'))

# ---------------------------------------------------------------- E11
B('E11',
  'The factory harness takes its supply from the temporary post through its own fusible links and its ground from the front star; the Class-T and MRBF fuses are in; the battery is connected; and the Ionic app shows the pack\'s voltage, charge and temperature.',
  'engine bay, the dash-node position and the cargo bin', 'a weekend',
  L('Spanners for the post, the stud nuts and the battery clamps', 'Torque wrench (P046)', 'Multimeter on DC volts (P045)',
    'Ratchet crimper for insulated terminals (P171) and heat gun (P042) if a ring is needed',
    'Phone with the Ionic app', 'Paint pen (from P082)'),
  'P048 P052 P050 P079 P094 P066',
  L('E10 is done and its meter checks passed',
    'Disconnect OFF, both big fuses out, the negative lug still off the battery, until the steps say otherwise',
    'Your E8 notes on the factory cables are in front of you',
    'Rings and watch off; extinguisher within reach'),
  L('The factory harness\'s main feed is the black 1.25 sq main fusible link (PT317) in block X-07, with a brown 0.3 sq link either side of it (PT316) for the headlight retractors and the headlights [00-CAR PT317, PT316]',
    'The 1985 manual places the fusible links at the front left suspension tower - 1985 manual, confirm on the car [00-CAR SP-063]',
    'The factory feed keeps its fusible links in series on the post: nothing of the factory protection is bypassed [work E11]',
    'The post is the Blue Sea 2003 PowerPost fitted at E10, fed by C03 from the 150 A Class-T [parts P050; cables C03]',
    'The factory harness\'s body grounds X-13 (left suspension tower and under the dash on the left), X-14 and X-15 stay bolted where they are [00-CAR PT027]',
    'The factory harness\'s main ground moves onto the front star stud made at E10 [work E11; grounds G05]',
    'Class-T fuse: 150 A, Blue Sea 5114, two bought - one fitted, one spare. MRBF fuse: 250 A in the 5191 holder [parts P048, P052; fuses Class-T, MRBF]',
    'The negative cable goes on last [S-002 p.5-5]',
    'The Ionic\'s output range is 8.0 to 14.6 V; it read 13.0 V, 3.25 V a cell, on 2026-09-08 [00-CAR SP-232; D-330]',
    'The pack\'s published operating range is -20 to 60 C [00-CAR SP-233]',
    'Never start a firmware update on the pack: that path can brick the battery that runs the car [D-330]',
    'The cluster is unplugged and the interior is out, so the car is not started today: that is E12 [work E12; D-387]',
    'Not in the record: what conductor joins the fusible-link block (in the bay) to the post (at the dash), and which factory wire is the "main ground" - use your E8 notes [work E11; 00-CAR PT290]'),
  'The fusible-link block\'s supply lead is on the temporary post with all three links in circuit; the factory ground lead is on the front star; both fuses are in with covers on; the battery is connected, negative last, boots on; with the disconnect ON the post reads the pack\'s voltage and the factory circuits wake as before; the app\'s three readings are entered in E45, E46 and E47.',
  'A spark or a blown fuse when the disconnect goes ON: switch OFF at once, pull the negative lug, and find the short before trying again - do not fit the spare fuse to see. The link block\'s lead does not reach the post: stop; do not extend it with whatever is to hand; note the distance and the lead\'s size and raise it in the app. The app does not find the pack: check the phone\'s Bluetooth, and enter nothing until it reads.',
  'Tick the row. Then enter the three readings in their own rows: E45 (V), E46 (%), E47 (C).')
S('E11',
  ('Check the car is still dead', 'Disconnect OFF; Class-T block and MRBF holder empty; C05\'s battery end off and insulated; post boots on.', 'Nothing live beyond the disconnect\'s input stud.'),
  ('Find the fusible-link block and its supply lead', 'Block X-07: one black link (the 1.25 sq MAIN) between two brown 0.3 sq links - by the 1985 manual at the front left suspension tower, confirm. Its battery-side lead is the one you taped and labelled "MAIN FEED - TO POST" at E8.', 'Block found; three links intact; the feed lead in your hand.', 'Do not bypass, shorten or replace a fusible link.'),
  ('Join the feed lead to the temporary post', 'The lead must reach the PowerPost\'s 3/8 in stud at the dash-node position with all three links still between the post and the factory harness. The record does not say what conductor covers that distance: if the lead reaches, fit a ring (P079, crimped with P171) and bolt it on the post; if it does not, stop here and raise it in the app with the distance and the lead\'s wire size.', 'The factory feed on the post, links in series - or a note raised and the row left open.', 'An unfused extension between the post and the links would be protected only by the 150 A Class-T: do not improvise one.'),
  ('Move the factory main ground to the front star', 'The lead you labelled "FACTORY GROUND - TO FRONT STAR" at E8 - the factory negative cable\'s connection to the body - lands on the front star stud with a ring over a star washer. If the factory negative went only to the engine and no body lead exists, note that: the block is already bonded by C06 and C11. Leave the harness\'s own ground bolts X-13, X-14 and X-15 where they are.', 'Factory ground on the front star, or a note that there is none.'),
  ('Go round every heavy joint once more', 'Every stud from the bin to the bay: nut torqued, paint mark present, boot or cover on. No tool left in the bin or the bay.', 'Every joint marked; nothing loose.'),
  ('Fit the Class-T fuse', 'One 150 A fuse (P048) into the Class-T block; nuts to Blue Sea\'s figure; cover on. The second fuse goes with the car\'s spares.', 'Fuse in, cover on.'),
  ('Fit the MRBF fuse', 'The 250 A MRBF (P052) into the 5191 holder on the disconnect\'s output stud, with C04\'s lug on the holder\'s fuse stud; torque; cover on.', 'Fuse in; the starter cable now fused.'),
  ('Connect the battery, negative last', 'Check the positive clamp, its stud nut and boot. Then put C05\'s lug on the negative clamp\'s stud, torque it, and boot it.', 'Both terminals connected and booted. No spark: the disconnect is OFF.', 'If anything sparks as the negative goes on, the disconnect is not OFF or something bypasses it: take the lug straight off.'),
  ('Turn the disconnect ON', 'Stand clear of the bin, switch ON, and watch and smell for ten seconds.', 'No spark, no smoke, no smell.', 'Hand on the switch: OFF at the first sign of anything.'),
  ('Read the post with the meter', 'Meter on DC volts: red on the temporary post\'s stud, black on the front star stud.', 'The pack\'s voltage, about 13 V - the same as the app will show.'),
  ('See the factory car wake', 'Key to ON (do not crank). The factory circuits that worked before work now: try the hazards, the horn, the lamps you can still reach. Key off.', 'Factory circuits live, as before, on the new backbone.', 'Do not start it today: the cluster is unplugged.'),
  ('Pair the Ionic app', 'On the phone, open the Ionic app and connect to the pack by Bluetooth. Do not accept or start any firmware update.', 'The pack appears with live readings.'),
  ('Take the three readings', 'From the app, with the disconnect ON and the key off: pack voltage (E45, in V), state of charge (E46, in %), pack temperature (E47, in C).', 'Three figures written down.'),
  ('Leave it safe and tick', 'Disconnect OFF if you are leaving the car. Tick E11, then enter the three readings in E45, E46 and E47.', 'E11 done; E12 ready.'))

# ---------------------------------------------------------------- E12
B('E12',
  'The engine starts and runs on the new backbone, the alternator charges the Ionic at or under 14.6 V, both cranking voltage drops are entered with every joint at 0.1 V or less (D-539), and every factory circuit works exactly as before.',
  'cargo bin and engine bay, the car stationary', 'a weekend',
  L('Multimeter on DC volts (P045), with min/max hold if it has it',
    'A long jumper lead to extend one meter probe from the cargo bin to the engine bay - not in the parts table: any light wire will do',
    'An assistant on the key', 'Wheel chocks', 'Extinguisher within reach'),
  '',
  L('E11 is done: fuses in, battery connected, the app reading',
    'Garage door open; belt and fan clear of leads, sleeves and tools',
    'Car in P, wheels chocked: the seats are out and it is not driven',
    'Extinguisher within reach'),
  L('The factory cluster was unplugged at the strip (S1): re-plug it so the meters read; the tachometer gives you 2,000 rpm [work E12]',
    'Charging voltage at the battery at 2,000 rpm: expect 13.8 to 14.6 V [work E12]',
    'The Ionic\'s maximum charge voltage is 14.6 +/- 0.1 V. Above about 14.7 V the fix is the alternator\'s regulator, never the battery [checks CK03; 00-CAR SP-231]',
    'The factory regulated band is 14.2 to 15.2 V, so a healthy factory alternator can be too high for this battery [00-CAR SP-081]',
    'The check asks for the reading with headlights off, then with headlights and blower on, engine warm [checks CK03]',
    'This car has shown no charge before: 11.4 V at idle. The new excitation circuit that should cure it comes at E28 (F15, migration step MG21) [D-198; work E12]',
    'Voltage drop while cranking, battery + post to starter stud, and battery - post to engine block: each under 0.5 V; near 0.5 V means a bad crimp [work E12]',
    'Cranking pulls 300 to 500 A briefly [backbone B2]',
    'By the wire table 18 ft of 1/0 is about 0.0018 ohm, which by itself drops 0.5 V at about 280 A: a hard crank can read a little over 0.5 V on the cable alone - record the figure either way [awg 1/0; cables C04, C11; arithmetic]',
    'Shut the engine down before opening the master disconnect [recovery RC01]',
    'No driving: the interior is out until E35 [D-387]'),
  'The engine starts and idles; the battery reads between 13.8 and 14.6 V at 2,000 rpm; each cranking drop is 1.0 V or under end to end with every joint 0.1 V or less; lamps, wipers, horn, blower and the other factory circuits work as they did; the three readings are entered in E42, E43 and E44.',
  'It does not crank: disconnect ON? MRBF in? C04 tight at both ends? It cranks but does not charge (battery voltage does not rise above the resting figure): stop running it - the alternator or its excitation is the cause, and E28 rebuilds the excitation; do not run long on the battery alone. Above 14.6 V: stop, note the figure, raise it in the app (the regulator). A drop of 0.5 V or more: find the warm or loose lug on that side and re-make it, then repeat.',
  'Tick the row. Then enter E42 (V, both readings), E43 (V) and E44 (V) in their own rows.')
S('E12',
  ('Make the garage safe to run an engine', 'Door open. Wheels chocked, car in P. Leads, rags and tools clear of the belt, fan and pulleys. Extinguisher within reach.', 'Fresh air and a clear engine bay.', 'A running engine in a closed garage is carbon monoxide.'),
  ('Re-plug the factory cluster', 'The cluster was unplugged at S1, not cut: plug its connectors back in and rest it where it cannot short on bare metal.', 'Cluster connected and supported.'),
  ('Switch on and look', 'Master disconnect ON. Key to ON: the cluster\'s warning lamps light.', 'Cluster alive.'),
  ('Rig the long meter lead', 'Clip the jumper lead to one meter probe so the meter can sit in the cargo bin with one probe on a battery post and the other reaching the starter stud and the engine block.', 'Meter reads the pack voltage, post to post, through the long lead.'),
  ('Start the engine', 'Assistant turns the key to START in P. Let it idle and warm.', 'It starts and idles.', 'Hands, hair and leads away from the belt and fan.'),
  ('Read the charging voltage at 2,000 rpm - this is E42', 'Engine warm. Meter on DC volts, red probe on the battery + post, black on the - post (lift the boots). Assistant holds 2,000 rpm on the tachometer. Read with the headlights off, then with headlights and blower on (if the blower cannot be switched with the dash out, take the headlights reading and note it).', '13.8 to 14.6 V, and never above 14.6 V.', 'Above 14.6 V: back to idle and stop - do not keep charging the lithium pack at that voltage.'),
  ('If it does not charge, stop here', 'A reading that stays at the resting pack voltage, or falls, means no charge. Shut down. The alternator or its excitation is at fault; excitation is rebuilt at E28. Enter the figure in E42 anyway and note it.', 'Either a charging figure, or the engine off and a note.'),
  ('Shut the engine down', 'Key off. Leave the disconnect ON for the next two tests.', 'Engine stopped.'),
  ('Cranking drop, positive side - this is E43', 'Red probe on the battery + POST itself (not the clamp), black probe on the starter\'s main B+ stud through the long lead. Assistant holds the key at START for about three seconds; read the meter while it cranks (use min/max hold if you have it).', 'End to end entered (E43), over 1.0 V fails; each single joint 0.1 V or less while cranking (D-539).', 'The engine may fire: stay clear of the belt and fan at the starter.'),
  ('Cranking drop, negative side - this is E44', 'Red probe on bare metal of the engine block, black probe on the battery - POST itself. Crank again for about three seconds and read.', 'End to end entered (E44), over 1.0 V fails; each single joint 0.1 V or less while cranking (D-539).'),
  ('Run it and try every factory circuit', 'Start again. Idle, then rev. Work each factory circuit: headlamps and pop-ups, park and tail lamps, turn signals and hazards, brake lamps, horn, wipers and washer, blower, rear defogger, the gauges.', 'Everything behaves exactly as it did before the backbone changed.', 'Fingers out of the pop-up buckets.'),
  ('Shut down, then switch off', 'Key off and engine stopped FIRST, then the master disconnect OFF.', 'Car dead.', 'Never open the disconnect with the engine running.'),
  ('Tick and enter the readings', 'Tick E12 with the charging voltage as its value. Enter E42, E43 and E44 in their rows.', 'E12 done: the car runs on the new backbone. No driving until E35.'))

# ---------------------------------------------------------------- E42-E47
B('E42',
  'The charging voltage at the battery at 2,000 rpm is measured and entered, and it is at or under 14.6 V.',
  'cargo bin, at the battery posts', '5 min, during E12',
  L('Multimeter on DC volts (P045)'),
  '',
  L('Taken at E12 step 6: engine warm, 2,000 rpm on the factory tachometer',
    'Garage door open; assistant at the pedal'),
  L('Probes go on the battery posts themselves, engine warm, 2,000 rpm: headlights off, then headlights and blower on [checks CK03]',
    'Expect 13.8 to 14.6 V [work E42]',
    'The Ionic\'s maximum charge voltage is 14.6 +/- 0.1 V; its float is 13.9 +/- 0.1 V [checks CK03; 00-CAR SP-231]',
    'The factory regulated band is 14.2 to 15.2 V: its top is above the pack\'s ceiling [00-CAR SP-081]',
    'Above about 14.7 V the fix is the alternator\'s regulator, never the battery [checks CK03]',
    'The row takes one figure and the check takes two: enter the higher, put both in a note [work E42; checks CK03]'),
  'One figure in volts entered, between 13.8 and 14.6.',
  'Under 13.8 V or not rising above the resting pack voltage: it is not charging - stop the engine, enter the figure, and see E12\'s "does not charge" step. Over 14.6 V: stop the engine, enter the figure, raise it in the app.',
  'Enter both readings in V: lights off first, then lights and blower on.')
S('E42',
  ('Set the meter at the battery', 'During E12 step 6. Meter on DC volts. Lift both post boots. Red probe on the + post, black on the - post.', 'The pack voltage with the engine idling.'),
  ('Read at 2,000 rpm, lights off', 'Assistant holds 2,000 rpm on the tachometer, headlights off. Wait for the figure to settle.', '13.8 to 14.6 V.', 'Above 14.6 V: back to idle and shut down.'),
  ('Read at 2,000 rpm with headlights and blower on', 'Same probes, headlights on and the blower on.', '13.8 to 14.6 V, at or a little under the first reading.'),
  ('Enter it', 'Boots back on. Enter the higher reading in E42, in V; note both.', 'E42 holds one figure.'))

B('E43',
  'The voltage drop from the battery + post to the starter stud while cranking is measured and entered, and each joint on the positive side reads 0.1 V or less (D-539).',
  'cargo bin and engine bay', '5 min, during E12',
  L('Multimeter on DC volts (P045), min/max hold if it has it', 'The long jumper lead from E12', 'An assistant on the key'),
  '',
  L('Taken at E12 step 9: engine stopped after the charging reading, disconnect ON',
    'Car in P, wheels chocked; clear of belt and fan'),
  L('Probes: battery + post to the starter\'s main B+ stud, read while the starter cranks [work E43]',
    'Pass (D-539): each single joint reads 0.1 V or less while cranking, meter across the joint - one lead on the cable\'s copper or lug barrel, the other on the stud it bolts to; this end-to-end figure is entered and fails by itself only above 1.0 V. The 0.1 V is a workshop rule, confirm [work E12; D-539]',
    'This reading covers C12, the disconnect, the MRBF fuse and C04 - every joint on the positive side [backbone B2]',
    'The starter feed C04 is 18 ft of 1/0, estimated [cables C04]',
    'By the wire table that cable alone drops 0.5 V at about 280 A, and cranking is put at 300 to 500 A: a figure a little over 0.5 V on a hard crank may be the cable - record it either way [awg 1/0; backbone B2; arithmetic]'),
  'One figure in volts entered, under 0.5.',
  'A joint over 0.1 V, or the end-to-end figure over 1.0 V: feel each positive-side lug and stud for warmth straight after a crank, re-make the joint that read high, and repeat. Still over: enter the figure and raise it in the app.',
  'Enter the value in V.')
S('E43',
  ('Place the probes', 'During E12 step 9. Red probe on the battery + POST itself, under the boot - not on the clamp. Black probe, through the long lead, on the starter\'s main B+ stud.', 'About 0 V with nothing cranking.'),
  ('Crank and read', 'Assistant holds the key at START for about three seconds. Read the meter while the starter turns (or its max hold afterwards).', 'Under 0.5 V.', 'Stay clear of the belt and fan: the engine may fire.'),
  ('Enter it', 'Enter the reading in E43, in V.', 'E43 holds one figure.'))

B('E44',
  'The voltage drop from the battery - post to the engine block while cranking is measured and entered, and each joint on the ground side reads 0.1 V or less (D-539).',
  'cargo bin and engine bay', '5 min, during E12',
  L('Multimeter on DC volts (P045), min/max hold if it has it', 'The long jumper lead from E12', 'An assistant on the key'),
  '',
  L('Taken at E12 step 10, straight after E43',
    'Car in P, wheels chocked; clear of belt and fan'),
  L('Probes: battery - post to the engine block, read while the starter cranks [work E44]',
    'Pass (D-539): each single joint reads 0.1 V or less while cranking, meter across the joint - one lead on the cable\'s copper or lug barrel, the other on the stud it bolts to; this end-to-end figure is entered and fails by itself only above 1.0 V. The 0.1 V is a workshop rule, confirm [work E12; D-539]',
    'This reading covers C05, the rear ground stud and the cranking return C11 to the block [backbone B5, B7]',
    'C11 is 18 ft of 1/0, estimated; the block-to-chassis strap C06 is only the bond [cables C11, C06]',
    'By the wire table that cable alone drops 0.5 V at about 280 A: record the figure either way [awg 1/0; arithmetic]'),
  'One figure in volts entered, under 0.5.',
  '0.5 V or more: check the rear ground stud\'s nut, C11\'s bolt on the block and both crimps for warmth or looseness; re-make and repeat. Still over: enter the figure and raise it in the app.',
  'Enter the value in V.')
S('E44',
  ('Place the probes', 'During E12 step 10. Black probe on the battery - POST itself, under the boot. Red probe, through the long lead, on bare metal of the engine block - not a bracket, not the strap.', 'About 0 V with nothing cranking.'),
  ('Crank and read', 'Assistant holds the key at START for about three seconds. Read while the starter turns.', 'Under 0.5 V.', 'Stay clear of the belt and fan.'),
  ('Enter it', 'Enter the reading in E44, in V.', 'E44 holds one figure.'))

B('E45',
  'The pack voltage the Ionic app shows after reconnection is entered.',
  'cargo bin, on the phone', '5 min, during E11',
  L('Phone with the Ionic app', 'Multimeter on DC volts (P045) to cross-check'),
  '',
  L('Taken at E11 step 13: fuses in, battery connected, disconnect ON, key off, app paired'),
  L('The reading is the app\'s pack voltage, not a meter reading [work E45]',
    'The pack\'s output range is 8.0 to 14.6 V; at 8.0 V its protection opens [00-CAR SP-232]',
    'It read 13.0 V, 3.25 V per cell, on 2026-09-08 [D-330]',
    'The record gives no pass band for the resting voltage: the figure is recorded, not judged [work E45]',
    'The meter at the temporary post (E11 step 10) should agree with the app [work E11]'),
  'One figure in volts entered, inside 8.0 to 14.6 and agreeing with the meter.',
  'App and meter disagree by more than a few tenths of a volt: enter the app\'s figure, note the meter\'s, and raise it in the app. No reading: re-pair; enter nothing until it reads.',
  'Enter the value in V.')
S('E45',
  ('Open the app at the pack', 'At E11 step 13, disconnect ON, key off. The app\'s main screen for the pack.', 'Live readings.'),
  ('Read the pack voltage', 'The total pack voltage, not a cell voltage.', 'A figure near 13 V.'),
  ('Enter it', 'Enter it in E45, in V.', 'E45 holds one figure.'))

B('E46',
  'The state of charge the Ionic app shows after reconnection is entered.',
  'cargo bin, on the phone', '5 min, during E11',
  L('Phone with the Ionic app'),
  '',
  L('Taken at E11 step 13, with E45'),
  L('The reading is the app\'s state of charge in per cent [work E46]',
    'The car\'s own electronics cannot read state of charge from the pack yet: the app is the only source [D-330]',
    'The record gives no pass band: the figure is recorded so the first start and charge (E12) have a starting point [work E46]',
    'A lithium pack gives no slow-crank warning: it is fine, then its protection opens [00-CAR SP-232]'),
  'One figure in per cent entered.',
  'A low figure before the first start: charge the pack with a lithium-profile charger first (a lead-acid charger can ruin it [parts P067]) and note it.',
  'Enter the value in %.')
S('E46',
  ('Read the state of charge', 'At E11 step 13, on the same screen as the voltage.', 'A percentage.'),
  ('Check it is enough to start on', 'The record sets no figure. If the app shows the pack low, charge it before E12.', 'Charged enough, or on charge.', 'Only a lithium (LiFePO4) profile charger.'),
  ('Enter it', 'Enter it in E46, in %.', 'E46 holds one figure.'))

B('E47',
  'The pack temperature the Ionic app shows after reconnection is entered.',
  'cargo bin, on the phone', '5 min, during E11',
  L('Phone with the Ionic app'),
  '',
  L('Taken at E11 step 13, with E45 and E46'),
  L('The reading is the app\'s pack temperature in degrees C [work E47]',
    'The pack\'s published operating range is -20 to 60 C [00-CAR SP-233]',
    'The pack is self-heating; packs of this class heat only from a charging source, in the cold - not published for this pack, confirm [00-CAR SP-233]',
    'The record gives no pass band beyond the operating range [work E47]'),
  'One figure in degrees C entered, inside -20 to 60.',
  'Outside -20 to 60 C: do not start or charge; note it in the app. If the app shows Fahrenheit, convert: C = (F - 32) x 5 / 9.',
  'Enter the value in C.')
S('E47',
  ('Read the pack temperature', 'At E11 step 13, on the app\'s pack screen.', 'A temperature near the garage\'s.'),
  ('Convert if needed', 'The row\'s unit is C. From Fahrenheit: subtract 32, multiply by 5, divide by 9.', 'A figure in C.'),
  ('Enter it', 'Enter it in E47, in C.', 'E47 holds one figure.'))

# ---------------------------------------------------------------- write
BH = ['id', 'goal', 'where', 'time', 'tools', 'parts', 'before', 'know', 'done_when', 'if_not', 'record']
SH = ['id', 'work', 'n', 'do', 'how', 'expect', 'caution']
briefs.sort(key=lambda b: MINE.index(b['id']))
steps.sort(key=lambda s: (MINE.index(s['work']), s['n']))
for name, head, data in (('briefs.csv', BH, briefs), ('steps.csv', SH, steps)):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=head, lineterminator='\n')
        w.writeheader()
        w.writerows(data)

# ---------------------------------------------------------------- validate
bad = []
bids = [b['id'] for b in briefs]
if sorted(bids) != sorted(MINE):
    bad.append('brief ids differ: %s' % (set(bids) ^ set(MINE)))
per = {}
for s in steps:
    if s['work'] not in MINE:
        bad.append('step for foreign row ' + s['id'])
    per.setdefault(s['work'], []).append(s)
    if not s['do'].strip():
        bad.append('empty do ' + s['id'])
for w in MINE:
    ss = per.get(w, [])
    if [s['n'] for s in ss] != list(range(1, len(ss) + 1)):
        bad.append('n gap in ' + w)
    for s in ss:
        if s['id'] != '%s.%02d' % (w, s['n']):
            bad.append('id mismatch ' + s['id'])
    if not ss:
        bad.append('no steps ' + w)
for b in briefs:
    if not b['goal'].strip() or not b['done_when'].strip():
        bad.append('empty goal/done_when ' + b['id'])
    for p in b['parts'].split():
        if p not in PARTS:
            bad.append('unknown part %s in %s' % (p, b['id']))
    for line in b['know'].split('\n'):
        if line and not (line.rstrip().endswith(']') or line.rstrip().endswith('confirm')):
            bad.append('know line without source in %s: %s' % (b['id'], line[:60]))
for row in briefs + steps:
    for k, v in row.items():
        if 'cad/' in str(v):
            bad.append('cad/ in %s %s' % (row['id'], k))
        if '\r' in str(v):
            bad.append('CR in %s %s' % (row['id'], k))
counts = [len(per[w]) for w in MINE]
print('briefs', len(briefs), 'steps', len(steps), 'min/median/max', min(counts), statistics.median(counts), max(counts))
print(' '.join('%s:%d' % (w, len(per[w])) for w in MINE))
print('problems:', len(bad))
for x in bad:
    print(' -', x)
sys.exit(1 if bad else 0)

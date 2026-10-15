from lib import *
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import plugs  # noqa: E402 - the plug of every part, from devices (D-543)

KIT = {'DT06-12S': 'P115', 'DT06-8S': 'P101', 'DT06-6S': 'P099', 'DT06-4S': 'P124', 'DT06-2S': 'P123', 'DTP06-4S': 'P131', 'DTP06-2S': 'P100',
       'DT04-12P': 'P126', 'DT04-8P': 'P127', 'DT04-6P': 'P128', 'DT04-4P': 'P129', 'DT04-2P': 'P130', 'DTP04-4P': 'P132', 'DTP04-2P': 'P133'}
WAYS = {'12': '12-way', '8': '8-way', '6': '6-way', '4': '4-way', '2': '2-way'}

LEG_TOOLS = ['Deutsch solid-contact 4-indent crimper, sizes 12 / 16 (P038)', 'Wire strippers 10-22 AWG, flush cutters (P043)',
             'Ratchet crimper for heat-shrink butt splices, rings and spades (P171)', 'Heat gun (P042)', 'Soldering iron and solder (P044)',
             'Multimeter: continuity beeper, ohms (P045)', 'Label printer with flexible-ID tape (P041)',
             'Contact removal tools, size 16 (P031, P032) and size 12 (P033)', 'Tape measure, and a board or floor long enough to lay the leg full-scale',
             'Paint pen (P082)']
LOOP = ['Cut length is 1.5 x the measured route; the margin is that factor, no extra loop is added [rules cut-list, D-202]',
        'Every wire is labelled at both ends the moment it is cut, printed tape, the same pair read in opposite order: O8 / L2-M-1 at one end, L2-M-1 / O8 at the other; a capped far end reads <cavity> / CAPPED [rules label-format]',
        'The leg side is the PLUG (DT06 / DTP06) and takes SOCKET contacts; a branch-end receptacle (DT04 / DTP04) takes PIN contacts [housings, work E20]',
        'A CAPPED wire is cut, labelled and terminated exactly like a LIVE one [work E20]',
        'Cavity numbers are the ones moulded into the housing: read them off the part [rules cavity-numbers]',
        'DT size-16 contacts take 14-20 AWG and carry 13 A; DTP size-12 contacts take 10-14 AWG and carry 25 A [series DT, DTP]',
        'Every run ends in the plug its part needs. The device rows name that plug and how the end is made - the factory plug spliced on at the migration, a new mating connector, a ring or spade, or one of our own Deutsch pairs - and each End step below repeats it [devices plug, leg_end; D-543]',
        'A device that keeps its factory plug: the plug is cut off the old harness in the car at E28, one circuit at a time, with 150 mm of its lead, and each lead is spliced to its new wire there with a sealed butt splice, staggered and sleeved. At the bench that end is left cut to length, labelled and insulated [D-537; rules device-end]',
        'No plug named here has been seen yet unless its line says seen: it is the 1982 diagram\'s wire count or a maker\'s sheet. Your looks at the car (S1, V-115, V-116) come first; an end that needs a connector bought is finished only once that connector is in hand [devices plug_seen; R11]']


def plug_head(h):
    r = HOU[h]
    ls = r['leg_side']
    n = ls.split('-')[1][:-1]
    con = 'size-12 socket contacts (P026)' if ls.startswith('DTP') else 'size-16 socket contacts: P022 for 16-18 AWG, P024 for 14 AWG'
    return '%s is a %s, the %s plug (kit %s): %s; wedgelock %s.' % (h, ls, WAYS[n], KIT[ls], con, r['wedgelocks'].split(' + ')[0])


def rec_head(h, where=None):
    r = HOU[h]
    bs = r['box_side']
    n = bs.split('-')[1][:-1]
    con = 'size-12 pin contacts (P027)' if bs.startswith('DTP') else 'size-16 pin contacts: P023 for 16-18 AWG, P025 for 14 AWG'
    return '%s is a %s, the %s receptacle (kit %s), placed: %s. %s; wedgelock %s.' % (h, bs, WAYS[n], KIT[bs], where or r['where'], con.capitalize(), r['wedgelocks'].split(' + ')[-1])


def plug_step(w, h, extra=(), caution=''):
    n = sum(1 for r in cavs(h) if r['state'] in ('PLUG', 'RESERVED'))
    step(w, 'Pin the %s plug' % h, [plug_head(h)] + leg_lines(h) + list(extra) + [
        'Each wire: strip, crimp the socket in the 4-indent crimper, push in from the wire side until it clicks, tug. Work in cavity order. Then the sealing plugs, then the wedgelock.'],
         'Every contact clicked and tugged; %s; the wedgelock snaps in flush; the code %s is on the shell.' % (('%d sealing plug%s fitted' % (n, '' if n == 1 else 's')) if n else 'no cavity left empty', h), caution)


def rec_step(w, hs, cap, extra=(), caution=''):
    how = []
    for h in hs:
        how.append(rec_head(h))
        for r in cavs(h):
            if r['state'] == 'PLUG':
                how.append('%s · sealing plug, size %s' % (r['cav'], plugsize(h)))
            else:
                how.append('%s · %s · %s · %s ← %s' % (r['cav'], r['circuit'], wire(r), r['state'], r['src']))
    step(w, 'Fit the branch-end receptacle%s %s' % ('s' if len(hs) > 1 else '', ' and '.join(hs)), how + list(extra) + ['Push the dust cap on (%s).' % cap],
         'Each receptacle pinned, plugged, wedge-locked, dust-capped and carrying its code.', caution)


def start_steps(w, housings, extra_cut=()):
    step(w, 'Lay the leg out full-scale',
         ['On the board or floor, mark the dash post at one end and each node and device along the measured runs:'] + routes_used(housings) + [
             'A run marked NOT measured has no cut length yet: that wire waits until C1\'s M-2 has measured it and G13 has derived the length. Do not cut from the 3D-model guess.',
             'The leg\'s pin ladder and route map are in the app\'s Diagrams.'],
         'Every run has a measured length written beside it on the board, or is marked WAIT.',
         'A wire cut short cannot be stretched: no measured route, no cut.')
    step(w, 'Cut and label every wire',
         ['Cut each wire to 1.5 x its run (add the runs joined by +). Print and wrap both labels before the next wire is cut.'] + cut_lines(housings) + list(extra_cut),
         'One labelled wire per line of the list, laid along its run on the board.')


def test_steps(w, ladder_how, ladder_expect, n_extra=''):
    step(w, 'Test: continuity end to end, every cavity',
         'Meter on the beeper. One probe on the socket in the plug cavity (use a spare pin contact as a probe tip, never a meter probe pushed into a socket), the other on the far end of that wire. Tick each cavity on the housing lists above. Through a resistor the beeper stays silent: read ohms instead.',
         'A beep for every LIVE and CAPPED cavity to its own far end, and to no other.' + n_extra,
         'A meter probe forced into a socket contact spreads it and the pin goes loose: probe with a mating pin.')
    step(w, 'Test: isolation',
         'Nothing plugged in at either end. Meter on its highest ohms range: each power cavity to its neighbours in the same plug, and every cavity to the ground wires of the leg.',
         'Open everywhere - the node test\'s mark is more than 1 MΩ (E18) - except where a resistor is fitted on purpose (the ladder and baseline resistors read their own value).',
         'Any other reading is a stray strand or a nicked wire: find it before the leg is bundled.')
    step(w, 'Test: the ladder check', ladder_how, ladder_expect)
    step(w, 'Tug, bundle, cap',
         'Tug every crimp once more. Tie the bundle every 150 mm with loose ties. Do NOT final-wrap: the cabin looms are wrapped at E35 and the engine-bay looms at E33. Dust caps on every branch-end receptacle; bag the plugs so no dirt gets in the sockets.',
         'A leg that lies flat on its layout, every end labelled, nothing taped.')


# ================================================================== E20 - L3 dash
L3H = ['L3-P', 'L3-M', 'L3-S1', 'L3-S2', 'L3-S3']
brief('E20',
      goal='Harness leg L3, the dash leg, is cut, labelled, pinned into its five plugs, ended at its switches and branch receptacles, and tested end to end.',
      where='bench - a board or floor long enough for the full-scale layout', time='a weekend - confirm',
      tools=LEG_TOOLS,
      parts='P115 P101 P123 P100 P133 P130 P129 P127 P022 P024 P026 P023 P027 P028 P029 P102 P125 P036 P002 P078 P079 P069 P071 P084 P085 P086 P015 P016 P012 P013 P009 P010 P011 P008 P019 P075 P076 P077',
      before=['E18 - the dash node passed continuity and isolation on the bench (it is first powered in the car, at E24)', 'G13 - the cut lengths are derived from the measured routes (C1, M-2)',
              'E7 - the ladder resistor sub-assemblies are built and bagged', 'CK10 read: the ignition switch IG contact holds through START - take it before this leg is crimped',
              'CK17 and CK18 read: the light switch and stalk contact tables - the ladders are built to what they found',
              'E5 - Deutsch practice done', 'Eye protection for crimping and clipping'],
      know=LOOP + [
          'L3 has five plugs at the post - L3-P, L3-M, L3-S1, L3-S2, L3-S3 - and five branch-end receptacles: L3-BLW at the HVAC case, L3-CMF behind the centre stack, L3-MOD, L3-RDR and L3-RCV behind the dash [housings]',
          'L3-S2 3 / 4 and L3-S3 5-7 carry the radar receiver\'s feed, ground and front sensor to L3-RCV, and L3-S2 5 / 6 the head unit\'s reverse and speed-pulse inputs; L3-S3 8 is a sealing plug. The window commands and mirror lines run in the Control Unit\'s tail from the node, not in this leg [cavities L3-S2 3-6, L3-S3 5-8; D-472, D-584]',
          'The seat receptacles and comfort-return harness (L3-SD, L3-SP, L3-SDM, L3-SPM) are E38 and the speaker runs are E41: not this row [work E38, E41]',
          'F24, 3 A sealed inline, sits in the leg behind the lower dash where the light-switch and brake-wake branch leaves the L3-S2 2 wire [fuses F24, D-412]',
          'The ignition switch is a new electrical portion (1981-83 type, P086); the light switch, both stalks and the horn pad are the car\'s own, kept [devices DV18, DV19, DV20, DV22, DV23]',
          'The wiper stalk WASH contact carries two wires: the ladder leg to L3-S1 4 and a plain wire to L3-S2 9, the washer relay coil return [devices DV22, work E20]',
          'WASH leg: 470 Ω + 1N4148, band toward the contact - the ladders, cavity and device rows agree. Build to the E7 sub-assembly [ladders A2 WASH, cavities L3-S1 4, devices DV22]',
          'Horn 8.2 kΩ and the two wink resistors (18 kΩ left, 33 kΩ right) all join onto the L3-S1 11 wire; the wink resistors are on the plate board, and the plate\'s 4-way header J2 gives pin 1 → L3-S1 9, pin 2 → L3-S1 10, pin 3 → L3-S1 11, pin 4 → dash ground [devices DV24, D-504]',
          'The hazard switch is on the CUR since D-586: L3-S1 6 runs in the wink lead to DP-CUR-B 5 and its 4.7 kΩ and 47 kΩ baseline are on the CUR\'s board; the column\'s F-02 hazard contact is left unconnected [cavities L3-S1 6, DP-CUR-B 5; D-368, D-586]',
          'The brake wake is a spare adjustable plunger switch (P084) on the pedal, fed through F24, not the brake lamp switch [cavities L3-S1 7, D-278]',
          'Ladder check: each state within 2 % of its table value at the leg-side cavity [work E20]',
          'Column and pedal fasteners, clip counts and the factory wire colours at the kept switches are not in this row\'s tables: the device rows give the terminal by function only [gap]'],
      done_when='Every L3 cavity is continuous to its own far end and to nothing else, isolation is open, each ladder state fitted so far reads within 2 % of its value, every end is labelled, branch receptacles are dust-capped, and the leg is bundled every 150 mm but not wrapped.',
      if_not='A contact in the wrong cavity: release it with the removal tool, never pull the wire. A ladder state off by more than 2 %: measure the resistor alone, then the joint. A length that comes up short on the layout: stop, re-measure the route, raise a note.',
      record='Tick the row.')
start_steps('E20', L3H, ['Also cut, to the same runs: the 12 AWG BLK blower return for L3-BLW 2 (RT14, G15), the F24 branch (16 AWG PNK, about the column, RT10), and the dash ground returns listed in the grounds step.'])
plug_step('E20', 'L3-P')
plug_step('E20', 'L3-M')
plug_step('E20', 'L3-S1', ['Cavity 4: the WASH value printed above is the cavity row\'s; the ladders table differs - see What to know.'], caution='Twelve wires, three colours: read the cavity number on the plug for every one.')
plug_step('E20', 'L3-S2')
plug_step('E20', 'L3-S3')
rec_step('E20', ['L3-BLW', 'L3-CMF'], 'P102', ['L3-BLW 2 is the 12 AWG BLK return to the dash ground (G15).'])
rec_step('E20', ['L3-MOD', 'L3-RDR', 'L3-RCV'], 'P125 on L3-MOD, P036 on L3-RDR, an 8-way cap on L3-RCV',
         ['L3-RCV 3, the radar alert, is not in this leg: it arrives from the Control Unit\'s branch (DP-DCU 48) and is pinned when that branch is laid; leave the cavity empty for it until then.'])
step('E20', 'Build the switch-supply branch and F24',
     ['The L3-S2 2 wire (16 AWG PNK, from F3) runs to the ignition switch B terminal.',
      'Behind the lower dash, butt-splice a branch off it into a sealed inline holder (P002) with a 3 A fuse: F24, label LIGHT-SW.',
      'After F24 the branch feeds two things: the light switch E-01 common, and the brake-wake plunger switch (whose other side is the L3-S1 7 wire).'],
     'L3-S2 2 beeps to the switch B end; through F24 (fuse in) it beeps to the light-switch common end and the plunger feed end.',
     'The key supply stays live with the key out: this branch must be fused where it leaves, not further along.')
step('E20', 'End the leg at the ignition switch',
     ['New switch (P086), four terminals by function:', 'B ← L3-S2 2 (PNK)', 'ACC → 33 kΩ → the L3-S1 1 wire (GRY); and ACC direct → L3-S1 12 (BLU)',
      'IG → 15 kΩ → the same L3-S1 1 wire; and IG direct → L3-S2 1 (BLU)', 'ST → 6.8 kΩ → the same L3-S1 1 wire',
      'The three resistors are the E7 sub-assemblies: solder, adhesive heat-shrink, all three summed onto the one GRY wire.',
      'Which blade of the new switch is B, ACC, IG and ST is not in the record: prove it with the meter and the key before joining.'],
     'Between the L3-S2 2 and L3-S1 1 cavities: OFF open · ACC 33 kΩ · RUN about 10.3 kΩ · START about 4.1 kΩ (about 4.7 kΩ if ACC drops out in START).',
     'If CK10 found that IG drops at START, a diode from ST into the K13 coil is needed (one 1N5819): stop and raise a note before finishing this end.')
step('E20', 'End the leg at the light switch',
     ['Switch E-01 on the column, kept. common ← the F24 branch', 'PARK contact → 33 kΩ → the L3-S1 2 wire (GRY)', 'HEAD contact → 15 kΩ → L3-S1 2',
      'DIMMER HI contact, fed from the HEAD contact side → 8.2 kΩ → L3-S1 2', 'PASS contact → 3.3 kΩ → L3-S1 2',
      'This switch keeps its factory plug: the joins are butt splices onto 150 mm of factory lead (see What to know for when).'],
     'From the F24 branch end to the L3-S1 2 cavity: OFF open · PARK 33 kΩ · HEAD low about 10.3 kΩ · HEAD high about 4.6 kΩ · PASS about 1.9 kΩ.',
     'CK17: the 1980 manual shows PASS closing the HIGH contact, not one of its own. Build to what CK17 measured on this car.')
step('E20', 'End the leg at the turn stalk and the hazard switch',
     ['Turn stalk F-02: LEFT → 1.8 kΩ → the L3-S1 3 wire · RIGHT → 10 kΩ → L3-S1 3 · OFF → 47 kΩ → L3-S1 3 · common → column ground, 16 AWG BLK.',
      'The hazard switch is not here any more (D-586): F-02\'s hazard contact stays unconnected - tape its wires back, labelled HAZARD - UNUSED. Its line, L3-S1 6, goes in the wink lead to the CUR (next steps).'],
     'L3-S1 3 to column ground: LEFT 1.8 kΩ · RIGHT 10 kΩ · OFF 47 kΩ. Nothing of F-02\'s hazard contact reaches the leg.',
     'CK18: the 1980 tables show no OFF contact to ground on the stalks. If CK18 found none, the 47 kΩ is a fixed baseline and the ladders table is what you build to.')
step('E20', 'End the leg at the wiper stalk',
     ['Stalk D-03: HIGH → 4.7 kΩ → the L3-S1 4 wire · LOW → 10 kΩ → L3-S1 4 · INT → 18 kΩ → L3-S1 4 · OFF → 47 kΩ → L3-S1 4.',
      'WASH contact → the WASH sub-assembly from E7 (resistor + diode, band toward the contact) → L3-S1 4; and the same WASH terminal direct → the L3-S2 9 wire (BLU).',
      'Common / contact returns → column ground.'],
     'L3-S1 4 to column ground: HIGH 4.7 kΩ · LOW 10 kΩ · INT 18 kΩ · OFF 47 kΩ. WASH pressed: L3-S2 9 beeps to column ground.',
     'The WASH leg has a diode: an ohmmeter will not read it true. Check the resistor alone, and the diode on diode test.')
step('E20', 'End the leg at the horn pad and the wink plate',
     ['Horn pad (steering wheel, returns to column ground through the slip ring): contact → 8.2 kΩ → the L3-S1 11 wire.',
      'The CUR\'s wink lead, 5 wires to its plug DP-CUR-B (the CUR is right of the wheel, high beside the DU, D-586): 1 ← L3-S1 9 (BLU, wink L NC) · 2 ← L3-S1 10 (BLU, wink R NC) · 3 ← L3-S1 11 (GRY) · 4 → dash ground, 16 AWG BLK · 5 ← L3-S1 6 (GRY, the hazard switch, D-586) · 6 a sealing plug.',
      'J2\'s housing and the plate\'s position are still confirm: leave this lead long, labelled, and unterminated at the plate end if the plate is not in hand.'],
     'L3-S1 11 to ground: horn pressed 8.2 kΩ; with the CUR fitted, wink L 18 kΩ, wink R 33 kΩ. L3-S1 9 and 10 beep to dash ground at rest and open when their wink is held. L3-S1 6 to ground with the CUR fitted: off 47 kΩ, hazard on about 4.27 kΩ.')
step('E20', 'End the leg at the pedal box',
     ['Brake pedal switch F-11 (new, P085): contact → 4.7 kΩ → the L3-S1 5 wire; other side → dash ground.',
      'Brake-wake plunger (P084) on the pedal: one side ← the F24 branch, other side → the L3-S1 7 wire (BLU).',
      'Kick-down switch B-32 at the throttle pedal (kept): one terminal ← L3-S2 12 (RED); the other → L3-S3 4 (RED).'],
     'L3-S1 5 to dash ground: pedal pressed 4.7 kΩ, released open. L3-S1 7 beeps to the F24 branch with the pedal pressed.')
step('E20', 'End the leg at the centre stack and glovebox',
     ['Head unit: red (ACC) ← L3-M 1 · yellow (BATT) ← L3-M 2 · orange (ILLUM) ← L3-S1 8 · black → dash ground, 14 AWG BLK. USB-C module: + ← a branch off L3-M 1 · − → dash ground, 16 AWG BLK.',
      'Dash illumination lamps E-06 heater panel, E-07 select lever, E-10 switch panel: RL ← the L3-S1 8 wire · B → dash ground.',
      'Glove box lamp H-01 + ← L3-S2 10; lamp − through the lid switch H-02 → dash ground.', 'Parking brake switch C-04: BR ← L3-S2 11; the switch grounds through the lever bracket.',
      'The head unit and USB-C module are fitted later: end those wires labelled and insulated.'],
     'Each wire reaches the end named and is labelled there.')
step('E20', 'Make the ground returns', ['To the dash ground star or the column ground, ring terminals (P079):'] + ground_lines(['L3'], skip=('G14', 'G36', 'G42')) + [
    'G14, the bus-to-chassis lead, is the node\'s (E17 / E24); G36 and G42 are E38\'s.'],
     'Every return listed has a labelled BLK wire with a ring on it.',
     'The lengths in the grounds table are hand estimates: cut each to the measured run, not to the table.')
test_steps('E20',
           ['With each switch that is already on the leg, work it through every position and read ohms at the leg-side cavity against the ladders table:',
            'A16 key (L3-S2 2 to L3-S1 1): ' + ladder('A16'), 'A15 lights (F24 branch to L3-S1 2): ' + ladder('A15'), 'A1 turn (L3-S1 3 to ground): ' + ladder('A1'),
            'A2 wiper (L3-S1 4 to ground): ' + ladder('A2'), 'A8 (L3-S1 6 and 11 to ground): ' + ladder('A8'), 'A3 brake only on this leg (L3-S1 5 to ground): 4.7k pressed',
            'In the table a + on A15 / A16 means both contacts closed at once, so the resistors are in parallel.',
            'On the leg the two A8 wires are still separate (the node splices them): L3-S1 6 alone reads 47k idle and 4.7k ∥ 47k with the hazard on; L3-S1 11 alone reads open idle, 8.2k horn, 18k wink L, 33k wink R.',
            'A kept switch that is not on the leg yet: check its resistor sub-assembly alone here, and repeat the switch-through check at E26.'],
           'Each state within 2 % of its value: 33 kΩ · 10.3 kΩ · 4.1 kΩ on the key; 33 kΩ · 10.3 kΩ · 4.6 kΩ · 1.9 kΩ on the lights; 1.8 k · 10 k · 47 k turn; 4.7 k · 10 k · 18 k · 47 k wiper; 4.27 kΩ hazard on its 47 k baseline.')

# ================================================================== E21 - L2 front
L2H = ['L2-P', 'L2-M', 'L2-S', 'L2-R']
brief('E21',
      goal='Harness leg L2, the front leg, is cut, labelled, pinned into its four plugs, spliced at the nose and ended at every front device, and tested.',
      where='bench - a board or floor long enough for the full-scale layout', time='a weekend - confirm',
      tools=LEG_TOOLS,
      parts='P131 P101 P099 P124 P129 P130 P022 P024 P026 P023 P028 P125 P036 P078 P079 P069 P015 P013 P012 P014 P009 P010 P008 P075 P076 P077',
      before=['E20 - leg L3 is built', 'CK08 read (C1, M-3): the pop-up motor matches the 1982 diagram - do NOT pin L2-P or the pop-up cavities of L2-S before that reading',
              'CK09 read: which wiper motor terminal is the park contact - before the wiper branch is crimped', 'CK23 read: which headlamp wire is low beam',
              'CK22: the washer pump runs on 12 V', 'G13 - the cut lengths are derived from the measured routes', 'Eye protection'],
      know=LOOP + [
          'L2 has four plugs at the post - L2-P, L2-M, L2-S, L2-R - and two branch-end receptacles at the nose: L2-OAT ahead of the radiator and L2-RDR behind the bumper [housings]',
          'The work row predates the radar front run: housings puts L2-R and L2-RDR on this leg, so they are built here, capped [housings L2-R, L2-RDR]',
          'Pop-ups, the factory way: one 12 AWG feed (WR) on L2-P 3 split at the nose to both motors; four command wires - up (R) on L2-S 1 left and L2-S 2 right, down (RY) on L2-P 4 left and L2-S 6 right; YG is capped at each motor [devices DV11, D-487, D-460]',
          'The motor terminals are R, RY, WR, YG by the 1982 diagram, and nobody has measured this car\'s motors until CK08 [checks CK08, 00-CAR SP-584]',
          'Headlamps: RY is low beam (L2-P 1), RL is high beam (L2-P 2), B to the front star - confirm at CK23 [cavities L2-P 1, 00-CAR PT035]',
          'One 47 kΩ baseline only, in the back of the L2-S plug on cavity 3, to a ground ring on the front star; the A4 / A5 baselines left this leg [work E21, cavities L2-S 3, D-487]',
          'Wiper motor D-02: LW low brush, LR high brush, L the park contact through 12 kΩ, LB left unconnected and capped, B to the front star [devices DV15]',
          'L2-S 4 is run to the wiper branch and left unpinned there for a future motor; L2-M 8 is its held park feed, capped [cavities L2-S 4, L2-M 8, D-317]',
          'Each horn gets a 14 AWG ground ring under a mounting bolt [devices DV14]',
          'Route L2-S apart from L2-P [housings L2-S]',
          'The front star is a new stud on the radiator support, 10 AWG to a bare-metal bolt [devices DV17, grounds G05]',
          'How the nose trim, lamps and buckets come apart is not in this row\'s tables [gap]'],
      done_when='Every L2 cavity is continuous to its own far end and nothing else, isolation is open, L2-S 3 reads 47 kΩ to its ground ring, the nose splices are sealed, branch receptacles are dust-capped, and the leg is bundled but not wrapped.',
      if_not='If CK08 did not match the diagram, stop: the pop-up cavities are redrawn first (raise a note). A splice that fails a tug: cut it out and redo it. A short length: stop and re-measure the route.',
      record='Tick the row.')
start_steps('E21', L2H, ['The nose splices fan out: the trunk wire is cut to RT06, each branch to its own run from the nose splice.',
                         'L2-OAT 1 is the far end of the L2-S 5 wire; L2-RDR 1-3 are the far ends of L2-R 1-3.'])
plug_step('E21', 'L2-P', caution='Do not pin cavities 3 and 4 until CK08 is read.')
plug_step('E21', 'L2-M')
plug_step('E21', 'L2-S', ['Cavity 3: before the contact goes in, join a 47 kΩ (E7 sub-assembly) onto the GRY wire right behind the plug; its other lead goes on 16 AWG BLK to a ring for the front star.',
                          'Cavity 4: the wire is pinned here at the plug, run to the wiper branch, and left cut, labelled and capped there.'],
          caution='Do not pin cavities 1, 2 and 6 until CK08 is read.')
plug_step('E21', 'L2-R')
step('E21', 'Make the nose splices',
     ['Sealed crimp butt splices with adhesive heat-shrink (P078), staggered so the bundle does not swell in one place:',
      'L2-P 1 (12 AWG) → a 14 AWG branch to each headlamp plug, terminal RY', 'L2-P 2 (12 AWG) → a 14 AWG branch to each headlamp plug, terminal RL',
      'L2-P 3 (12 AWG) → a 12 AWG branch to motor E-03 terminal WR and to motor E-04 terminal WR', 'L2-M 3 (14 AWG) → each horn\'s terminal GY',
      'L2-M 7 (14 AWG) → F-05 RG, F-06 RG, F-12 RG, F-13 RG'],
     'Each splice survives a firm tug; glue shows at both ends of the shrink.', 'The splice kit has three sizes (22-18, 16-14, 12-10); the record does not say which takes a trunk and two branches: make one on scrap and tug it first.')
step('E21', 'End the leg at the pop-up motors',
     ['Motor E-03 (left): WR ← the L2-P 3 branch · R (up) ← L2-S 1 · RY (down) ← L2-P 4 · YG capped at the motor.',
      'Motor E-04 (right): WR ← the L2-P 3 branch · R (up) ← L2-S 2 · RY (down) ← L2-S 6 · YG capped.',
      'Each bucket: a 14 AWG BLK strap to the front star (G07).', 'The motors keep their factory plugs (E-03 / E-04 connectors).'],
     'Each wire labelled with its motor terminal letter.', 'YG is +12 V while the motor runs: cap it sealed, never ground it.')
step('E21', 'End the leg at the headlamps', 'Each lamp E-08 (left), E-09 (right): RY ← its L2-P 1 branch · RL ← its L2-P 2 branch · B → front star, 14 AWG BLK (G06).',
     'Two lamps, three wires each.')
step('E21', 'End the leg at the wiper motor and washer pump',
     ['Wiper motor D-02: LW ← L2-M 1 · LR ← L2-M 2 · L → 12 kΩ → L2-S 3 · LB capped, unconnected · B → front star, 14 AWG BLK (G11).',
      'The L2-S 4 and L2-M 8 wires end here, cut, labelled CAPPED and sealed.', 'Washer pump D-01: LB (+) ← L2-M 4 · LY (−) → front star, 16 AWG BLK (G12).'],
     'L2-S 3 reads 12 kΩ to the motor L end.', 'CK09 may have changed which terminal is the park output: build to the cavity rows as they stand after CK09.')
step('E21', 'End the leg at the front lamps and horns',
     ['Front combo F-05 (left): GR ← L2-M 5 · RG ← the L2-M 7 splice · B → front star, 16 AWG BLK (G08). F-06 (right): GO ← L2-M 6 · RG · B.',
      'Side markers F-12 (left), F-13 (right): RG ← the L2-M 7 splice · B → front star (G09).',
      'Horns F-09, F-10: GY ← the L2-M 3 splice; a 14 AWG BLK ring under each horn\'s mounting bolt → front star (G10).'],
     'Each lamp and horn has its feed and its own ground wire.')
rec_step('E21', ['L2-OAT', 'L2-RDR'], 'P125 on L2-OAT, P036 on L2-RDR', ['The outside-air thermistor\'s other lead returns to the front star (G38) when it is fitted.'])
step('E21', 'Make the ground returns to the front star', ['Ring terminals (P079), each return its own wire to the star stud on the radiator support:'] + ground_lines(['L2'], skip=('G13',)) + [
    'G13 is the one baseline return, from L2-S 3: the pop-up baselines left the leg with D-487.'],
     'Every return has a labelled BLK wire with a ring.', 'Lengths in the table are hand estimates: cut to the measured run.')
test_steps('E21', ['L2-S 3 to its front-star ring: ' + ladder('A3') + '.', 'On this leg alone, with the wiper parked or not connected, cavity 3 shows the 47 kΩ baseline; through the park contact it shows 12 kΩ in parallel with it.'],
           '47 kΩ at rest; about 9.6 kΩ with the park contact closed to ground.')

# ================================================================== E22 - L4 rear + sill
L4H = ['L4-P', 'L4-M', 'L4-S', 'L4-S2']
SILL_REL = ['K5 WIN-D-UP · 86 ← L4-M 9 · 85 → sill ground · 30 → D1 1 · 87 ← F8 · 87a → sill ground',
            'K6 WIN-D-DN · 86 ← L4-M 10 · 85 → sill ground · 30 → D1 2 · 87 ← F8 · 87a → sill ground',
            'K7 WIN-P-UP · 86 ← L4-M 11 · 85 → sill ground · 30 → D2 1 · 87 ← F9 · 87a → sill ground',
            'K8 WIN-P-DN · 86 ← L4-M 12 · 85 → sill ground · 30 → D2 2 · 87 ← F9 · 87a → sill ground']


def door_lines(h):
    out = []
    for r in cavs(h):
        if r['state'] == 'PLUG':
            out.append('%s · sealing plug, size 16' % r['cav'])
        else:
            out.append('%s · %s · %s ← %s' % (r['cav'], r['circuit'], wire(r), r['src']))
    return out


brief('E22',
      goal='Harness leg L4, the rear leg, and the sill node are built: cut, labelled, pinned, the sill panel wired, every rear device end made, and tested.',
      where='bench for the leg and the sill panel', time='a weekend - confirm',
      tools=LEG_TOOLS + ['Open-barrel crimper for the relay socket terminals (P039)'],
      parts='P132 P131 P115 P101 P127 P129 P022 P024 P026 P023 P025 P028 P036 P162 P002 P003 P006 P058 P059 P091 P078 P079 P069 P161 P197 P084 P015 P016 P012 P013 P014 P009 P010 P011 P008 P075 P076 P077',
      before=['E21 - leg L2 is built', 'G13 - the cut lengths are derived from the measured routes', 'The sill space is measured (C1, M-5) and the sill panel stock (P091) is cut to it',
              'CK20 read: the hatch and fuel-door solenoid currents', 'E9 - the rear ground stud is in the cargo bin', 'Eye protection'],
      know=LOOP + [
          'L4 has four plugs at the post - L4-P, L4-M, L4-S, L4-S2 - the sill node behind the driver kick panel, and the branch-end receptacles L4-RDR at the rear node and L4-HRD in the hatch [housings, devices DV43]',
          'The fuel pump\'s return is its own 12 AWG to the rear star stud, never shared [devices DV34, grounds G26]',
          'Sill node: a small panel with relay sockets K5-K8, three sealed inline holders F8, F9, F14, a ground stud, and the door receptacles D1 (driver) and D2 (passenger) [devices DV43]',
          'K5-K8: the four window relays are fitted and wired at the sill this build [relays K5, D-451]',
          'F14 is 5 A and LIVE; F8 and F9 are rated 20 A and marked EMPTY: holders fitted, fuses out until the windows arrive [fuses F8, F9, F14]',
          'D1 / D2 are RESERVED: pinned on the node side of the receptacle, the door plug filled with sealing plugs. Nothing runs through the door boots this build [cavities D1 1, work E22]',
          'Door jamb ladder on L4-S 2: driver switch through 24 kΩ + 1N4148, passenger through 8.2 kΩ + 1N4148, anodes toward the splice, and a 47 kΩ baseline from the sill splice to sill ground. [cavities L4-S 2, devices DV41, D-486]',
          'The interior lamp\'s RY wire lands on the same jamb switch terminals through a 1N4007 each, anode on RY [devices DV39, DV41]',
          'The hatch and fuel-door solenoids are factory parts believed to work; each grounds through the body - prove it with the meter [devices DV48, DV49]',
          'The road-speed signal wire gets an 18 in service loop in the tunnel; the sensor is fitted later at the meters cutover [cavities L4-S 3, D-272]',
          'The tunnel also carries three heavy cables beside this bundle [routes RT15]',
          'The hinge loop is a flex point: its length is measured with the hatch open [routes RT18]',
          'The speaker receptacles on this leg (L4-SPR, L4-SUB) are E41: not this row [work E41]',
          'How the quarter trim, hatch trim and tank cover come off is not in this row\'s tables [gap]'],
      done_when='Every L4 cavity is continuous to its own far end and nothing else, isolation is open, the sill panel is wired and its relays and F14 are in, L4-S 2 reads 47 kΩ with both jamb switches open, each solenoid\'s ground is proved, and the leg is bundled but not wrapped.',
      if_not='A solenoid with no continuity to the body: do not add a ground wire on your own - raise a note with the reading. A jamb reading that is not 47 kΩ: check the baseline and the diode directions.',
      record='Tick the row.')
start_steps('E22', L4H, ['Sill panel wires are short and cut on the panel: see the sill steps.', 'The hatch-end run L4-RDR → L4-HRD is three 16 AWG GRY along RT18.'])
plug_step('E22', 'L4-P', caution='Cavity 2 is the fuel pump: its wire and its return are 12 AWG, nothing thinner.')
plug_step('E22', 'L4-M')
plug_step('E22', 'L4-S')
plug_step('E22', 'L4-S2')
step('E22', 'Build the sill panel',
     ['On the cut panel (P091): four relay sockets (P006) labelled WIN-D-UP, WIN-D-DN, WIN-P-UP, WIN-P-DN; three sealed inline holders (P002) labelled WIN-DRV (F8), WIN-PASS (F9), MIRROR-HEAT (F14); a 3/8 in ground stud (P058) with a star washer (P059); two 8-way receptacle clips (P162) for D1 and D2.',
      'Keep everything above the lowest 50 mm and let every wire enter from below or with a drip loop.'],
     'A panel that fits the measured sill space with every part reachable.', 'The sill is where water collects: nothing in the lowest 50 mm.')
step('E22', 'Wire the sill panel', nc_lines(['N90', 'N91', 'N92', 'N93', 'N94', 'N95']) + ['Relay sockets:'] + SILL_REL,
     'Each socket terminal beeps to what its line says; the four 87a and four 85 terminals all beep to the sill stud.',
     'An idle window relay grounds its motor leg through 87a: 87 is the feed, 30 the motor. Swapping 87 and 87a puts the fuse straight to ground.')
step('E22', 'Pin the D1 and D2 receptacles on the node side and plug the door plugs',
     ['D1 (driver), DT04-8P, size-16 pins (P025 for the 14 AWG, P023 for the 16 AWG), wedgelock W8P:'] + door_lines('D1') + ['D2 (passenger), the same:'] + door_lines('D2') + [
         'Mirror lines from the L4-S2 wires: cavity 1 is spliced to D1 4 and D2 4 both.',
         'Then fill a DT06-8S door plug for each with eight sealing plugs (P028) and its wedgelock, and mate it as the cover. The two door plug kits are counted in the door-harness row P166, which is bought later: if they are not in hand, cover each receptacle and raise a note.'],
     'Two receptacles pinned 1, 2, 4, 5, 6, 7, 8 with a sealing plug in 3; two all-plug door plugs mated.')
step('E22', 'Fit the sill relays and fuse', 'Four relays (P003) in K5-K8. A 5 A fuse in F14. F8 and F9 holders stay empty, capped.', 'K5-K8 in; F14 holds 5 A; F8 / F9 empty.')
step('E22', 'Make the door-jamb switch ends',
     ['New plunger switches (two from the 6-pack P084), one at each B-pillar; the switch body grounds in the jamb.',
      'Driver: switch terminal ← 1N4148 ← 24 kΩ ← the sill splice (the diode\'s anode toward the splice). Passenger: switch terminal ← 1N4148 ← 8.2 kΩ ← the sill splice.',
      'The sill splice is the end of the L4-S 2 wire (GRY). A 47 kΩ from the splice to the sill ground (G37).',
      'The interior lamp\'s RY wire: a 1N4007 at each switch, anode on RY, cathode on the same switch terminal.',
      'Resistor and both diodes sit inline at each switch, soldered and heat-shrunk.'],
     'L4-S 2 to sill ground: 47 kΩ with both switches open.', 'A diode the wrong way round makes that door invisible to the car, or puts battery voltage on the A6 line: check each on diode test before shrinking.')
step('E22', 'End the leg at the tank',
     ['Fuel pump (Carter P4070): + ← L4-P 2, 12 AWG RED · − → its OWN 12 AWG BLK to the rear star stud (G26).', 'Tank sender C-01: Y ← L4-S 1 (GRY) · B → rear star, 16 AWG BLK (G28). Route the sender wire apart from the pump feed.'],
     'Pump + and − are both 12 AWG and the − wire goes to the stud alone.', 'Fuel: the master disconnect is open and there is no spark or heat gun near the tank when this end is connected in the car.')
step('E22', 'End the leg at the rear lamps',
     ['Splices behind the rear trim (sealed butt splices):', 'L4-M 1 (14 AWG) → F-07 RG, F-08 RG, F-04 RG (x2), F-14 RG, F-15 RG', 'L4-M 2 (14 AWG) → F-07 G, F-08 G',
      'L4-M 5 → rear combo F-07 terminal GR · L4-M 6 → rear combo F-08 terminal GO', 'L4-M 7 → F-07 RW, F-08 RW',
      'Grounds: each combo lamp B, each licence lamp and rear marker B → rear star, 16 AWG BLK (G29, G30).'],
     'Each lamp terminal has its feed; each lamp has its own ground wire to the star.')
step('E22', 'End the leg at the hatch, the roof and the quarter',
     ['Defog grid G-25: LG ← L4-P 1, 12 AWG · B → rear star, 12 AWG BLK (G25).',
      'Interior / spot lamp H-06: LY (+) ← L4-M 8; the lamp\'s own switch: ON → roof-rail ground, 16 AWG BLK (G31); DOOR → RY down the C-pillar and along the sill to both jamb switches.',
      'Luggage lamp H-11: + ← L4-S 8; − through the lid switch H-12 → rear star (G32).',
      'Hatch-release solenoid: + ← L4-M 3, ring or spade, through the hinge loop with the tail-lamp wires. Fuel-door solenoid: + ← L4-M 4, behind the driver-side quarter trim.'],
     'With the meter: each solenoid\'s case or − terminal beeps to the body.', 'Leave slack across the hinge loop with the hatch fully open.')
step('E22', 'End the tunnel run', ['Road-speed sensor wires: signal L4-S 3 (GRY) with an 18 in service loop in the tunnel; supply L4-S 4 (RED); the sensor ground → rear star (G35). The sensor is fitted later: cap and label the three ends.',
                                 'Kick-down solenoid B-33 on the transmission: + ← L4-S2 7 (RED); it grounds through the case.'],
     'Three capped, labelled sensor wires and one solenoid feed.')
rec_step('E22', ['L4-RDR', 'L4-HRD'], 'P036', ['L4-RDR sits at the rear node; the three-wire hatch run plugs into it and ends at L4-HRD in the hatch, up the hinge loop.',
                                               'The hatch run\'s plug for L4-RDR is a DT06-4S (kit P124) with sockets on the same three wires.'])
step('E22', 'Make the ground returns', ['Rear star stud (cargo bin) and sill stud, ring terminals (P079):'] + ground_lines(['L4', 'Sill'], skip=('G41',)) + ['G41 is the amplifier\'s, E41.'],
     'Every return has a labelled BLK wire with a ring.', 'Lengths in the table are hand estimates: cut to the measured run.')
test_steps('E22', ['L4-S 2 to sill ground: ' + ladder('A6') + '.', 'The branches carry diodes, so an ohmmeter reads only the 47 kΩ baseline true; check each resistor alone and each diode on diode test, then press each plunger and see the reading fall.'],
           '47 kΩ with both doors\' switches open; lower with either pressed.')

# ================================================================== E23 - L1 engine
L1H = ['L1-P', 'L1-S1', 'L1-S2']
brief('E23',
      goal='Harness leg L1, the engine leg, is cut, labelled, pinned into its three plugs, ended at every engine-bay device, and tested.',
      where='bench - a board or floor long enough for the full-scale layout', time='a day - confirm',
      tools=LEG_TOOLS,
      parts='P131 P115 P022 P026 P028 P029 P074 P135 P004 P005 P078 P079 P069 P015 P018 P009 P010 P008 P075 P076 P077 P081',
      before=['E22 - leg L4 and the sill node are built', 'G13 - the cut lengths are derived from the measured routes', 'CK19 read: the oil-pressure sender\'s ohms', 'Eye protection'],
      know=LOOP + [
          'L1 has three plugs at the post: L1-P (power), L1-S1 and L1-S2 (signal). They leave the post together through the firewall grommet, passenger side [housings, routes RT01]',
          'Only ten wires run in this leg; every other cavity is a sealing plug [cavities L1-S1 5, L1-S2 2]',
          'The swap reserves are pinned at the post only: L1-P 2 and 3, L1-S2 9 and 11 carry sealing plugs in these plugs [cavities L1-P 2, D-271]',
          'L1-S1 9 / 10 are sealing plugs: CAN2 never enters the engine bay [cavities L1-S1 9, D-318]',
          'Tach: shielded cable (P074) from L1-S1 6 to coil T negative (factory wire YG). The shield is cut back and insulated at the coil end; it is grounded at the dash node only [cavities L1-S1 6, node_conductors N48]',
          'The tach cable crosses ignition leads at 90 degrees and never runs parallel to one within 50 mm [rules emc-routing]',
          'K9, the start relay, is a sealed relay (P004) in a weatherproof socket (P005) on the inner fender; its contact wires are 10 AWG from F17 (30 A, at the starter B+ stud) to the starter S terminal [relays K9, fuses F17]',
          'Alternator plug A-08: BW is excitation → L1-S1 2; WB is the charge-lamp sense → L1-S2 8 [devices DV04]',
          'The ignition suppression capacitor (P135) goes on the coil branch at the coil bracket [parts P135, D-281]',
          'Inhibitor switch A-06: 8.2 kΩ in each signal lead and a 47 kΩ baseline from each lead to block ground at the switch [cavities L1-S1 11, L1-S2 7, D-487]',
          'Water-temp sender C-02 (factory wire YW) is in the rear housing directly below the oil-pressure sender C-09 (BrY) [devices DV06, DV07]',
          'How the leg-side tach shield is carried across the L1-S1 connector is not in the record: cavity 5 stays a sealing plug [gap]',
          'K9 and F17 are fitted in the car at E27; here the K9 socket is wired onto the leg [work E27]'],
      done_when='Every L1 cavity is continuous to its own far end and nothing else, isolation is open, each inhibitor lead reads 47 kΩ to its ground end with the contact open, the tach shield is open to the core, and the leg is bundled but not wrapped.',
      if_not='Tach core shorted to its shield: the strip nicked the insulation - cut back and redo. An inhibitor reading off by more than 2 %: measure the resistor alone.',
      record='Tick the row.')
start_steps('E23', L1H, ['K9\'s two 10 AWG RED contact wires (F17 → K9 30, K9 87 → starter S) are cables C08 / C09: their lengths are hand estimates - cut to the measured run along RT05.'])
plug_step('E23', 'L1-P', caution='Cavities 2, 3 and 4 take size-12 sealing plugs (P029), not the size-16 ones.')
plug_step('E23', 'L1-S1', ['Cavity 6 is the shielded cable\'s core: strip the jacket back, fold the drain and shield back out of the way, crimp the core only.',
                           'How the drain is bonded at this plug is not in the record: leave 150 mm of drain here, insulated, and raise a note before trimming it.'],
          caution='A shield strand in the crimp shorts the tach to ground.')
plug_step('E23', 'L1-S2')
step('E23', 'Make the coil branch',
     ['L1-P 1 (12 AWG RED trunk) → a sealed splice at the coil bracket → 14 AWG branches to terminal BW of coil T (B-18), coil L (B-19), igniter T (B-20) and igniter L (B-21).',
      'The suppression capacitor (P135): its lead on the same splice, its ring-lug case under a bracket bolt.',
      'The YL (leading pulse) wire is not used.'],
     'L1-P 1 beeps to all four BW ends and to the capacitor lead.', 'This is the ignition feed: every joint here is a sealed crimp, tugged.')
step('E23', 'End the tach cable at the coil',
     ['Core → coil T (B-18) negative terminal, factory wire YG.', 'At this end cut the shield and drain back and seal the end with adhesive heat-shrink so no strand shows.',
      'Lay the cable so it crosses the coil and igniter leads at 90 degrees and is never within 50 mm parallel to one.'],
     'Core to shield reads open; the core beeps end to end.')
step('E23', 'Wire the K9 socket',
     ['Weatherproof 5-pin socket (P005):', '86 ← L1-S1 1 (16 AWG RED)', '85 → block ground, 16 AWG BLK (G02)', '30 ← F17, 10 AWG RED (from the MIDI holder at the starter B+ stud)',
      '87 → the starter S terminal (factory wire BW), 10 AWG RED', 'Confirm the socket\'s terminals accept 10 AWG before crimping.'],
     'Four wires in the socket, each tugged; the relay (P004) clicks into it.', 'The 30 wire is live from the battery whenever the master disconnect is closed: its far end stays insulated until E27.')
step('E23', 'End the leg at the alternator and the senders',
     ['Alternator plug A-08: BW ← L1-S1 2 (RED) · WB ← L1-S2 8 (GRY).', 'Water-temp sender C-02: spade ← L1-S1 3 (GRY). Oil-pressure sender C-09: spade ← L1-S1 4 (GRY). Both ground through their threads.',
      'Brake-fluid switch C-05: BR ← L1-S2 1 (GRY) · B → block ground, 16 AWG BLK (G04).'],
     'Each wire labelled with its device and terminal.')
step('E23', 'End the leg at the inhibitor switch',
     ['Switch A-06, 4-pin, on the transmission:', 'BY ← 8.2 kΩ ← L1-S1 11 (GRY) · BW → block ground, 16 AWG BLK', 'GY ← 8.2 kΩ ← L1-S2 7 (GRY) · RW → block ground, 16 AWG BLK',
      'A 47 kΩ baseline from each GRY lead to the block ground wire, at the switch.', 'Resistors are the E7 sub-assemblies, soldered and heat-shrunk.'],
     'Each GRY lead reads 47 kΩ to its ground wire with the contact open.')
step('E23', 'Make the ground returns', ['To the engine block, ring terminals (P079):'] + ground_lines(['L1'], skip=('G39',)) + ['G39 is the swap\'s fan return: not this build.'],
     'Every return has a labelled BLK wire with a ring.', 'Lengths in the table are hand estimates: cut to the measured run.')
test_steps('E23', ['L1-S1 11 to its block-ground wire: ' + ladder('A4') + '.', 'L1-S2 7 to its block-ground wire: ' + ladder('A5') + '.',
                   'With the switch on the leg, move the lever through P, R, N.'],
           '47 kΩ idle; about 6.98 kΩ with the contact closed (8.2 kΩ in parallel with 47 kΩ).',
           ' Tach core: open to its shield.')


# ================================================================== the plug each run ends in (D-543)
# The devices each End step reaches; the wording comes from devices.plug / leg_end through plugs.end().
ENDS = {
    ('E20', 'Fit the branch-end receptacles L3-BLW and L3-CMF'): ['DV27', 'DV55', 'DV56'],
    ('E20', 'End the leg at the ignition switch'): ['DV18'],
    ('E20', 'End the leg at the light switch'): ['DV19'],
    ('E20', 'End the leg at the turn stalk and the hazard switch'): ['DV20'],
    ('E20', 'End the leg at the wiper stalk'): ['DV22'],
    ('E20', 'End the leg at the horn pad and the wink plate'): ['DV23', 'DV24', 'DV21'],
    ('E20', 'End the leg at the pedal box'): ['DV25', 'DV50'],
    ('E20', 'End the leg at the centre stack and glovebox'): ['DV28', 'DV29', 'DV30', 'DV31', 'DV26'],
    ('E21', 'End the leg at the pop-up motors'): ['DV11'],
    ('E21', 'End the leg at the headlamps'): ['DV10'],
    ('E21', 'End the leg at the wiper motor and washer pump'): ['DV15', 'DV16'],
    ('E21', 'End the leg at the front lamps and horns'): ['DV12', 'DV13', 'DV14'],
    ('E21', 'Make the ground returns to the front star'): ['DV17'],
    ('E22', 'Build the sill panel'): ['DV43'],
    ('E22', 'Make the door-jamb switch ends'): ['DV41'],
    ('E22', 'End the leg at the tank'): ['DV34', 'DV36'],
    ('E22', 'End the leg at the rear lamps'): ['DV37', 'DV38'],
    ('E22', 'End the leg at the hatch, the roof and the quarter'): ['DV33', 'DV39', 'DV40', 'DV48', 'DV49'],
    ('E22', 'End the tunnel run'): ['DV47', 'DV51'],
    ('E22', 'Make the ground returns'): ['DV42'],
    ('E23', 'Make the coil branch'): ['DV01'],
    ('E23', 'Wire the K9 socket'): ['DV03', 'DV02'],
    ('E23', 'End the leg at the alternator and the senders'): ['DV04', 'DV06', 'DV07', 'DV08'],
    ('E23', 'End the leg at the inhibitor switch'): ['DV05'],
}
for (_w, _do), _ids in ENDS.items():
    _hit = [k for k, st in enumerate(S[_w]) if st[0] == _do]
    assert len(_hit) == 1, (_w, _do, len(_hit))
    _d, _how, _ex, _ca = S[_w][_hit[0]]
    S[_w][_hit[0]] = (_d, _how + '\n' + '\n'.join(['How each of these ends is made (D-543):'] + plugs.ends(_ids)), _ex, _ca)

from lib import *

POST = [h for h in HOU if HOU[h]['where'] == 'Dash post']
SRC_PIN = "S-028 p.11-12"

# pin -> where its wire goes at the node (pins.goes_to_fixed, node_conductors, cavities.src)
DEST = {
    '1': 'receptacle L1-P 2 - the swap reserve, pinned at the post and nothing in the L1 plug (D-271)',
    '2': 'the O12 splice: receptacle L1-P 1 (N18) and the four fused taps F15, F16, F20, F21 (N19, N20, N61, N78)',
    '3': 'receptacle L2-M 3 - horns',
    '4': 'receptacle L3-M 1 (N23) and the O10 taps: K12 86, DP-ICU-A 1 (N24), L4-S 4 (N73), F33 to K3 / K4 (N85), the capped radar tail (N103)',
    '5': 'receptacle L2-M 2 - wiper HIGH',
    '6': 'receptacles L2-M 5 and L4-M 5, with the tap to DP-ICU-B 10 (N51)',
    '7': 'the wake strip common rail (N38)',
    '8': 'wake strip input 5 (N37), K11 terminal 86 (N06) and the 10 kΩ to Q0 base (WS01)',
    '9': 'receptacle L2-M 1 and K12 terminal 30 (N26)',
    '10': 'receptacle L4-M 2 - brake lamps',
    '11': 'receptacles L2-M 7 and L4-M 1 (N54)',
    '12': 'K13 terminal 30 (N69); K13 87 goes on to receptacle L4-P 2 (N70)',
    '13': 'receptacle L4-P 1 - rear defog',
    '14': 'receptacle L1-P 3 - the swap reserve, pinned at the post (D-271)',
    '15': 'the two 100 kΩ bias resistors (to pins 35 and 22) and the 100 Ω 1 W oil-node pull-up (N39)',
    '16': 'receptacle L3-S1 4 (N97)',
    '17': 'receptacle L1-S1 11 - the inhibitor P/N contact',
    '18': 'receptacle L4-S 2 and the door wake stage (N44)',
    '19': 'receptacles L3-S1 6 and L3-S1 11, one splice, and the A8 wake stage (N43)',
    '20': 'receptacle L4-M 7 - reverse lamps',
    '21': 'receptacle L1-S1 1 - the K9 coil',
    '22': 'receptacle L3-S1 1 (N99), with the 100 kΩ bias from pin 15',
    '23': 'DP-DIAG 1, twisted with pin 36 (N56); 120 Ω across 23 / 36 at this connector',
    '24': 'the CAN2 splice at the node, twisted with pin 37 (N55)',
    '25': 'the GND bus, 6 in or less (N57)',
    '26': 'receptacle L2-P 2, a 16 AWG tap to DP-ICU-B 12 (N53) and one diode of the pop-up coil feed (N09)',
    '27': 'receptacle L3-P 2 (N17) and the tap to K14 / K15 terminal 86 (N110)',
    '28': 'receptacle L3-P 1 - blower, capped at L3-BLW',
    '29': 'receptacle L3-S1 3 (N96)',
    '30': 'receptacles L3-S1 5, L2-S 3 and L2-S 4, one splice (N42)',
    '31': 'receptacle L1-S2 7 - the inhibitor R contact',
    '32': 'a tap on the L1-S1 4 to DP-ICU-B 2 conductor (N45)',
    '33': 'receptacles L2-M 6 and L4-M 6, with the tap to DP-ICU-B 11 (N52)',
    '34': 'receptacle L3-S1 8 and DP-ICU-A 2 (N22)',
    '35': 'receptacle L3-S1 2 (N98), with the 100 kΩ bias from pin 15',
    '36': 'DP-DIAG 2, twisted with pin 23 (N56)',
    '37': 'the CAN2 splice at the node, twisted with pin 24 (N55)',
    '38': 'the O1 splice (N08): F37 to K1 / K2 terminal 30, receptacle L2-P 3 (N105), receptacle L4-P 3 (N16)',
    '39': 'receptacle L2-P 1 and one diode of the pop-up coil feed (N09)',
}
SIZE = {'L': 'LARGE, 2.8 mm die', 'S': 'small, 1.5 mm die', 'M': 'MEDIUM - terminal and die not named in the record'}
PIN = {r['pin']: r for r in PINS}


def pin_line(p):
    r = PIN[p]
    st = '' if r['state'] == 'LIVE' else ' · ' + r['state']
    nm = ('%s %s' % (r['ch'], r['name'])) if r['ch'] and r['ch'] != r['name'] else r['name']
    return '%s · %s · %s %s AWG%s → %s' % (p, nm, r['colour'], r['awg'], st, DEST[p])


def pins_where(f):
    return [pin_line(str(n)) for n in range(1, 40) if f(PIN[str(n)])]


RELAYS_NODE = [
    'K1 POPUP-L · 86 ← the two-diode lamps-up feed off O2 / O3 (N09) · 85 → receptacle L3-S1 10 (N10) · 30 ← F37, 5 A, from the O1 splice (N08) · 87 → receptacle L2-S 1 (N12) · 87a → receptacle L2-P 4 (N14)',
    'K2 POPUP-R · 86 ← the same two-diode feed (N09) · 85 → receptacle L3-S1 9 (N11) · 30 ← F37 (N08) · 87 → receptacle L2-S 2 (N13) · 87a → receptacle L2-S 6 (N15)',
    'K3 HATCH-REL · 86 and 30 ← F33, 10 A, off the O10 tap (N85) · 85 → DP-DCU-B 10 (N86) · 87 → receptacle L4-M 3 (N88) · 87a nothing',
    'K4 FUEL-REL · 86 and 30 ← F33 (N85) · 85 → DP-DCU-B 11 (N86) · 87 → receptacle L4-M 4 (N89) · 87a nothing',
    'K11 HEAD-UNIT · 86 ← PMU pin 8, O22, tapped at wake strip input 5 (N06) · 85 → GND bus (N07) · 30 ← busbar through F31, 40 A, 10 AWG (N04) · 87 → F32, 40 A, → fuse block B input, 10 AWG (N05)',
    'K12 WASHER · 86 ← the O10 tap (N24) · 85 → receptacle L3-S2 9 (N25) · 30 ← PMU pin 9, O8 (N26) · 87 → receptacle L2-M 4 (N27)',
    'K13 FUEL-PUMP · 86 ← the branch off receptacle L3-S2 1 (N71) · 85 → GND bus (N72) · 30 ← PMU pin 12, O5 (N69) · 87 → receptacle L4-P 2 (N70)',
    'K14 SEAT-D · 86 ← the O15 tap (N110) · 85 → GND bus (N111) · 30 ← busbar through F35, 25 A (N106) · 87 → the L3-SDM 1 tail (N108)',
    'K15 SEAT-P · 86 ← the O15 tap (N110) · 85 → GND bus (N111) · 30 ← busbar through F36, 25 A (N107) · 87 → the L3-SPM 1 tail (N109)',
]

# ------------------------------------------------------------------ E13
brief('E13',
      goal='The dash node is laid out with the real parts, proved in cardboard in the car, and its carrier panels are cut, deburred and painted.',
      where='bench, then the driver footwell and under the dash for the mock-up',
      time='a day - confirm',
      tools=['Cardboard, marker, craft knife, tape', 'Steel rule and square', 'Drill and bits, step bit', 'Jigsaw or hacksaw, files, deburring tool',
             'Centre punch', 'Phone camera'],
      parts='P090 P093 P060 P007 P001 P189 P002 P006 P068 P134 P030 P162 P126 P127 P128 P129 P130 P132 P133',
      before=['E12 - the car starts and charges on the new backbone', 'C2 - the panel stock (P090) and paint (P093) are bought',
              "C1's measurements in hand: the M-1 dash envelope and the wideband gauge's hiding place",
              'The interior is still out (S1), so the footwell and dash rail are open',
              'Master disconnect open while you reach around the temporary distribution post: the 2 AWG feed is live there (E10, E4)'],
      know=["The dash node is everything that hangs off the PMU in one place: the PMU-24, the always-hot busbar, the ground bus, fuse blocks A and B, the inline fuse holders, nine relay sockets, the wake strip, a perfboard and the wideband gauge [work E13]",
            'Nine relay sockets at the node, not seven: K1 K2 K3 K4 K11 K12 K13 and the two seat relays K14 K15 added by D-469 [relays K14, K15]',
            'Sixteen receptacles sit at the dash post: ' + ', '.join('%s %s' % (h, HOU[h]['box_side']) for h in POST) + ' [housings]',
            'Leave panel room beside L1-S1 / L1-S2 for four more DT04-12P receptacles for the engine swap - five if engine block 02.16 was answered (a) [work E13, engine D-443]',
            'Water runs down from the cowl seam and the windscreen corners: every wire enters the PMU and the node from below or with a drip loop, nothing mounts in the lowest 50 mm of the footwell, and the PMU 39-way faces down or sideways, never up [rules water-ingress]',
            'What CK04 found (where the water goes with the dash out) moves a bracket now for free [checks CK04]',
            'The PMU stands on three M6 x 12 mm stand-offs for airflow [parts P060]',
            'The busbar is the Blue Sea 2300, 10-gang 150 A with cover: one always-hot bar and one ground bus, both covered [parts P007]',
            'The DCU tail must reach the centre stack: the node has to sit close enough along RT11, which is measured at M-2 [routes RT11, housings DP-DCU-B]',
            'Receptacle clips: 1027-003-1200 fits the 2, 4, 6 and 12-way and every DTP; the 8-way receptacles take the 8-way clip - four of them are at the post (L2-M, L3-S3, L4-S, L4-S2), D1 and D2 are at the sill; both use an 11 mm hole - confirm on the clip in hand [parts P030, P162]',
            'Nothing here is measured by anyone but you: the cardboard in the car is the proof, not the drawing [R11]'],
      done_when='Every part has a place on painted panels that passed the cardboard mock-up in the car: the PMU lever swings its full arc, there is 60 mm clear behind every receptacle, both fuse blocks can be reached, and nothing sits in the lowest 50 mm.',
      if_not='If it does not all fit inside the M-1 space, do not thin the clearances: split it across more panels or move a panel, mock it again, and raise a note in the app with a photo. If RT11 is long for the DCU tail, raise a note before cutting metal.',
      record='Tick the row. Add a note with the photos of the cardboard mock-up in the car and the finished panels.')
step('E13', 'Gather the real parts and the M-1 numbers',
     ['On the bench: the PMU with its 39-way connector, the busbars (P007), fuse blocks A and B (P001), the five MAXI holders (P189), the ten inline holders for the node (P002), nine relay sockets (P006), the 8-position barrier strip (P068), the perfboard on its M3 standoffs (P134), the wideband gauge controller, and one of each receptacle shell with its clip.',
      "Write the M-1 space from C1 on a card: width, height, depth, and where the lowest 50 mm line is."],
     'Every part in the list is on the bench; nothing is laid out from a catalogue size.')
step('E13', 'Draw the M-1 space on cardboard',
     "Cut a cardboard outline the size of the space C1 measured behind the lower dash. Mark the floor side, the firewall side and a line 50 mm up from the lowest edge: nothing mounts below that line.",
     'A full-size outline you can lay parts on.')
step('E13', 'Place the PMU first',
     ['Low and close to the floor, but above the 50 mm line.', 'Connector facing down or sideways, never up.',
      'Swing the 39-way lever through its whole arc with the connector on: nothing may sit in the arc.',
      'Leave air under it: it stands on three M6 stand-offs (P060). Mark the three holes from the PMU itself.'],
     'The lever opens and closes fully on the cardboard with the connector fitted.',
     'Do not mark the holes from a drawing: the mounting pattern is not in the record, take it off the part.')
step('E13', 'Place the busbars, the fuse blocks and the fuse holders',
     ['Always-hot busbar beside the PMU +12 V stud, with its cover on: check the cover still fits with lugs on the studs.',
      'Ground bus beside PMU pin 25: its 10 AWG wire to the bus must be 6 in or shorter.',
      'Fuse blocks A and B where your hand reaches them with the dash in.',
      'Five MAXI holders at the busbar: F30 (block A), F31 (K11 terminal 30), F32 (K11 terminal 87 to block B), F35 and F36 (the seat feeds).',
      'Three inline holders right at the bar with their leads cut to about 50 mm: F12, F22, F23.',
      'Seven more inline holders near what they feed: F15, F16, F20, F21 (off O12), F33 (off O10), F37 (off the O1 splice).'],
     'Every holder can be opened and its fuse pulled without moving another part.',
     'The always-hot busbar is live whenever the master disconnect is closed: it must be covered and nothing metal may be able to fall across it.')
step('E13', 'Place the nine relay sockets, the wake strip, the perfboard and the gauge',
     ['Relay sockets (P006) in a row, in this order so the labels read left to right: K1 K2 K3 K4 K11 K12 K13 K14 K15.',
      'The 8-position barrier strip (P068) and the perfboard (P134) side by side: the wake parts on the board wire straight to the strip.',
      "The wideband gauge controller where C1 found it hides, with its fixed sensor lead reaching the firewall grommet: that lead is never cut or extended."],
     'Each relay can be pulled straight out; each strip screw can be reached with a screwdriver.')
step('E13', 'Place the receptacles along the panel edge, grouped by leg',
     ['One clip per receptacle, 60 mm of clear space behind every one for the wires.',
      'Groups: L1 (L1-P, L1-S1, L1-S2), L2 (L2-P, L2-M, L2-S, L2-R), L3 (L3-P, L3-M, L3-S1, L3-S2, L3-S3), L4 (L4-P, L4-M, L4-S, L4-S2).',
      'Beside L1-S1 / L1-S2 leave room for four more 12-way receptacles (five if engine block 02.16 was answered (a)).',
      'Keep L2-S apart from L2-P, and the signal receptacles away from the pop-up motor bus and blower wires by 50 mm where you can.'],
     'Sixteen clip positions marked, plus the spare room for the swap.',
     'A plug must be able to be pushed on and pulled off by hand with the dash in: try it with a mated pair on the cardboard.')
step('E13', 'Check the layout against the rules',
     ['Low and close to the floor · the PMU lever arc clear · 60 mm behind every receptacle · both fuse blocks reachable · the always-hot busbar covered · the PMU stood off for airflow · no bare aluminium against a live stud.',
      'Every wire can enter from below or with a drip loop.', 'Hold what CK04 found against the layout: nothing under a water path.'],
     'Every line is true on the cardboard.')
step('E13', 'Mock it up in the car',
     ['Tape the parts or their outlines to the cardboard and offer it up in the footwell where C1 measured.',
      'Fit the 39-way and swing the lever. Push a plug onto a receptacle at each end of the row. Reach each fuse block.',
      'Lay a tape from the node along the dash rail to the centre stack: that is the DCU tail, note the length.',
      'Photograph it from the driver seat side and from below.'],
     'It goes in and comes out by hand, and everything on it can be reached.',
     'The master disconnect is open while your arms are near the temporary distribution post.')
step('E13', 'Transfer the layout to the panel stock and cut',
     ['Lay the cardboard on the panel stock (P090), centre-punch every hole through it, and mark the panel edges.',
      'Cut the panels. Drill the PMU stand-off holes, the clip holes (11 mm - confirm on the clip in hand), the relay socket, block and strip holes to the parts themselves.'],
     'The parts drop onto their holes without forcing.', 'Eye protection for cutting and drilling.')
step('E13', 'Deburr and paint',
     'File every edge and hole until a rag does not catch. Paint or coat the panels (P093) and let them cure before anything is mounted.',
     'Smooth edges, an even coat, no bare aluminium where a live stud will sit.')

# ------------------------------------------------------------------ E14
NODE_FUSES = fuse_lines(lambda r: r['location'].startswith('Dash node'))
brief('E14',
      goal='Every part of the dash node is mounted on its panel and every relay socket and fuse position carries its label.',
      where='bench', time='half a day - confirm',
      tools=['Screwdrivers and small sockets', 'Torque wrench 1/4 in drive, 2-20 N·m (P046)', 'Wire strippers and flush cutters (P043)',
             'Label printer with the node labels from E6 (P041)', 'Paint pen (P082)'],
      parts='P060 P007 P001 P189 P190 P191 P002 P006 P068 P134 P030 P162 P075',
      before=['E13 - the panels are cut and painted', 'E6 - the node labels are printed', 'Nothing is connected to the car: this is bench work'],
      know=['The PMU stands on three M6 stand-offs [work E14, parts P060]',
            'Five 40 A-class MAXI holders (P189): F30 feeds block A, F31 feeds K11 terminal 30, F32 sits at K11 terminal 87 and feeds block B - 40 A fuses (P190); F35 and F36 feed the seat relays K14 / K15 - 25 A fuses (P191) [fuses F30, F31, F32, F35, F36, D-467, D-469]',
            'The fuse sits at the bar so the only wire protected by the Class-T alone is a short stub: each busbar-fed inline holder (F12, F22, F23) has its 14 AWG lead cut to about 50 mm, never more than 180 mm [node_conductors N75, N87]',
            'Block A is on the busbar: position 1 F2, 2 F3, 3 F19, 4 F13 (no fuse). Block B is behind K11: position 1 F1, 2 F5 (no fuse) [fuses]',
            'The 8-position strip is full: seven wake inputs and the common rail [parts P068]',
            'Labels come from the label columns: ' + ' · '.join('%s %s' % (r['id'], r['label']) for r in REL if r['location'] == 'Dash node') + ' [relays]',
            'Fuse labels at the node: ' + ' · '.join('%s %s' % (r['id'], r['label']) for r in FUS if r['location'].startswith('Dash node')) + ' [fuses]',
            'Torque figures for the busbar studs, the PMU stud and the relay socket screws are read off the makers\' sheets at D1 - none is in the record yet - confirm [rules torque]'],
      done_when='Every part is fixed and does not move when pushed, every relay socket and every fuse position has its printed label beside it (the empty ones too), and no fuse or relay is fitted yet.',
      if_not='A part that fouls another: stop, go back to the cardboard (E13) rather than bending a bracket. A missing label: print it from the relays / fuses label column, never hand-write it.',
      record='Tick the row.')
step('E14', 'Mount the PMU', ['Three M6 x 12 mm stand-offs (P060) to the panel, the PMU on them, connector facing down or sideways.',
                              'Fit the 39-way once and swing the lever through its arc.'],
     'The PMU is rigid on its stand-offs with air behind it; the lever arc is clear.',
     'Tightening torque for the PMU mounting is not in the record: snug, and note what the PMU manual gives.')
step('E14', 'Mount the two busbars',
     ['Always-hot bar beside the PMU +12 V stud. Ground bus beside pin 25, within 6 in of it.', 'Fit both covers to prove they close.'],
     'Both bars fixed, both covers on.', 'No bare aluminium panel may touch a live stud: check the gap under the always-hot bar.')
step('E14', 'Mount fuse blocks A and B', 'Block A nearest the always-hot bar, block B nearest the K11 socket. Mark A and B on the panel with the paint pen.',
     'Both blocks fixed, lids open freely.')
step('E14', 'Mount the five MAXI holders at the busbar',
     ['F30 - busbar to block A input. F31 - busbar to K11 terminal 30. F32 - K11 terminal 87 to block B input. F35 - busbar to K14 terminal 30. F36 - busbar to K15 terminal 30.',
      'Fix each holder body to the panel so its lead to the bar is as short as it will go. Do not fit the fuses.'],
     'Five holders fixed and labelled BLOCK-A-FEED, K11-FEED, BLOCK-B-FEED, SEAT-D, SEAT-P.')
step('E14', 'Mount the ten sealed inline holders',
     ['At the bar, each with its busbar-side 14 AWG lead cut to about 50 mm: F12 INTERIOR, F22 DCU-CONST, F23 WAKE.',
      'Near the O12 splice position: F15 ALT-EXCITE, F16 DISPLAY, F20 WIDEBAND, F21 KICK-DOWN.',
      'On the O10 release branch ahead of K3 / K4: F33 RELEASE. On the pop-up command branch ahead of K1 / K2: F37 POPUP-CMD.',
      'Tie each holder down so its cap opens upward or sideways. No fuses yet.'],
     'Ten holders fixed, each with its label.',
     'A busbar-fed lead longer than 180 mm is unprotected wire behind a 150 A fuse: cut it short.')
step('E14', 'Mount the nine relay sockets', 'In order K1 K2 K3 K4 K11 K12 K13 K14 K15. Do not plug the relays in.',
     'Nine sockets fixed in a row.')
step('E14', 'Mount the wake strip and the perfboard',
     'The 8-position barrier strip (P068) with position 1 at the end nearest the L3 receptacles; write 1 to 8 beside it with the paint pen: 1-7 are the wake inputs, 8 is the common rail. The perfboard (P134) beside it on its M3 standoffs.',
     'Strip and board fixed; positions numbered.')
step('E14', 'Fit the receptacle clips', 'One clip per receptacle along the panel edge, grouped L1, L2, L3, L4: the 12, 6, 4, 2-way and DTP clips (P030), the 8-way clips (P162) for L2-M, L3-S3, L4-S and L4-S2.',
     'Sixteen clips; an empty receptacle shell snaps into each.')
step('E14', 'Mount the wideband gauge controller', 'Where E13 placed it, its sensor lead routed toward the firewall grommet uncut.',
     'Controller fixed, lead not strained.')
step('E14', 'Stick every label',
     ['Beside each relay socket: ' + ' · '.join('%s %s' % (r['id'], r['label']) for r in REL if r['location'] == 'Dash node') + '.',
      'Beside each fuse position, the empty ones included:'] + NODE_FUSES,
     'Every socket and every fuse position reads its id and name from where you will stand to service it.')

# ------------------------------------------------------------------ E15
brief('E15',
      goal='The wake strip carries its seven diodes and bleed resistor, the two wake sense stages are built on the perfboard to the wake_stages table, the two bias resistors are fitted, and the bench check CK12 is read.',
      where='bench', time='half a day - confirm',
      tools=['Soldering iron and solder (P044)', 'Flush cutters, needle-nose pliers (P043)', 'Multimeter: ohms, diode test, DC volts (P045)',
             'Heat gun (P042)', 'A 12 V bench supply or the battery through a fused lead for CK12'],
      parts='P071 P072 P069 P158 P160 P161 P134 P068 P011 P019 P008',
      before=['E14 - the strip and perfboard are mounted', 'A10 - the stage values are in the record (they are: the wake_stages table)',
              'Eye protection while soldering and clipping leads'],
      know=['The PMU wakes when pin 7 (+12V SW) goes high. Seven sources are OR-ed onto it through one diode each, so no source can feed another [pins 7]',
            'Strip inputs: 1 ACC (L3-S1 12) · 2 RUN (L3-S2 1) · 3 door stage · 4 horn / hazard / wink stage · 5 O22 keep-alive (pin 8) · 6 brake plunger (L3-S1 7) · 7 DCU wake request (DP-DCU 6) [node_conductors N33-N37, N63, N76]',
            'Seven 1N5819, band (cathode) toward the common rail; the rail goes to pin 7; 10 kΩ from the rail to the GND bus [node_conductors N38, work E15]',
            'The two sense stages are a comparator design now: one LM2903 DIP-8 serves both, U1A the door line (A6, pin 18), U1B the horn / hazard / wink line (A8, pin 19) [wake_stages WS15, WS25; work E15]',
            'Both stages are fed from F23, 3 A, constant from the busbar [fuses F23, node_conductors N87]',
            'The base clamps are 1N4148, never a Schottky: a 1N5819 leaks hot and loses the pulse at 85 °C [wake_stages WS19]',
            'The edge capacitors are 2.2 µF film (P158); the value is still to be confirmed against the PMU boot time CK12 reads [wake_stages WS17]',
            'The threshold divider resistors WS14 / WS24 are 1 % parts [wake_stages WS14]',
            'Bias: 100 kΩ from pin 15 (+5 V) to pin 35 (A15) and 100 kΩ from pin 15 to pin 22 (A16), so a broken wire reads 0, not OFF [node_conductors N39]',
            'At rest the door and A8 lines sit at 0.166 x the F23 voltage (about 1.99 V at 12.0 V); the comparator threshold is 0.115 x [wake_stages WS12, WS13]',
            'LM2903 pin-out, 8 pins, pin 1 at the dot or the notch end: 1 OUT A · 2 IN- A · 3 IN+ A · 4 GND · 5 IN+ B · 6 IN- B · 7 OUT B · 8 V+ [parts P160; 00-CAR S-501]',
            '2N3904, flat face toward you and leads down: emitter · base · collector, left to right - the usual order, not read from the sheet of the parts bought: confirm on one with the diode test before soldering [parts P072]'],
      done_when='Seven diodes read forward toward the rail and blocked the other way; every resistor measured before fitting; CK12 read on the bench: at rest no wake, any door or A8 switch wakes, the three unknowns (i)-(iii) written down.',
      if_not='A stage that does not wake: check the comparator supply (F23) and the divider node (0.115 x F23), then the 2.2 µF and the follower. If the unpowered PMU pin reads under 200 kΩ to ground at CK12 (i), stop: WS12 may have to drop - raise a note with the reading. Do not put the node in the car on a failing CK12.',
      record='Tick the row. Enter the CK12 readings as a note: (i) ohms pin 18 and pin 19 to ground with the PMU unpowered, (ii) the lowest pin 7 voltage that switches the PMU on and its current at 12 V, (iii) seconds from pin 7 high to O22 on.')
step('E15', 'Measure and bag every part first',
     ['From the resistor kit (P069): 10 k x2 (WS01, the rail bleed), 100 k x5 (WS02, WS10, WS20 and the two bias), 220 k x2, 1 M x4, 130 k 1 % x2, 47 k x2.',
      'Measure each with the meter and lay them on a labelled card. 2N3904 x5 (P072), LM2903 x1 (P160), 2.2 µF film x2 (P158), 1N4148 x2 (P161), 100 nF x1, 1N5819 x7 (P071).'],
     'Every resistor reads within its tolerance of the marked value.', 'The 100 nF capacitor has no parts row: take it from stock and note it.')
step('E15', 'Fit the seven diodes to the strip',
     ['One 1N5819 per input position 1 to 7: the plain end under the input screw, the banded end (cathode) to the common rail at position 8.',
      'Join the seven banded ends to position 8 with a bare bus wire or a jumper comb; sleeve any lead that could touch its neighbour.'],
     'Diode test from each input screw to position 8: it conducts one way with a low forward reading (a Schottky) and is open the other way.',
     'A diode fitted backwards holds the car asleep on that input, or back-feeds a source: test all seven.')
step('E15', 'Fit the rail bleed', '10 kΩ from position 8 (the rail) to a ring on the GND bus, 16 AWG BLK.',
     '10 kΩ from position 8 to the GND bus.')
step('E15', 'Build the shared part of the stages on the perfboard', ws_lines('shared'),
     'With O22 off (asleep) Q0 is off; the 100 nF sits right at the LM2903 supply pin.')
step('E15', 'Build stage 1 - the door line, A6', ws_lines('door') + [
    'WS19, the base clamp: anode to ground, cathode to the Q31 base.',
    'U1A OUT is the open-collector output of the comparator, pin 1 of the LM2903, with WS16 as its pull-up.'],
     'Every joint shiny; no bridge between rows (check with the meter on ohms between neighbours).')
step('E15', 'Build stage 2 - the horn / hazard / wink line, A8', ws_lines('A8') + [
    'WS29, the base clamp: anode to ground, cathode to the Q32 base.',
    'As stage 1: U1B OUT is pin 7 of the LM2903, with WS26 as its pull-up.'],
     'As stage 1.')
step('E15', 'Bring the stage wires out to labelled flying leads',
     ['F23 supply in: 16 AWG PNK (N87). Ground: 16 AWG BLK to the GND bus.',
      'A6 line (to PMU pin 18, N44) and A8 line (to PMU pin 19, N43): 16 AWG GRY.',
      'O22 in (from pin 8, to WS01): 16 AWG RED. Stage 1 out to strip input 3 (N35) and stage 2 out to strip input 4 (N36): 16 AWG BLU - land these two on the strip now.',
      'Label every lead at both ends as it is cut.'],
     'Seven labelled leads; outputs landed on strip inputs 3 and 4.')
step('E15', 'Fit the two 100 kΩ bias resistors',
     'On the perfboard: one end of both to a common pad for the pin 15 wire (16 AWG PNK, N39); the other ends to two pads for the pin 35 (A15) and pin 22 (A16) wires. The wires themselves land at E17.',
     '100 kΩ from the pin 15 pad to each of the two input pads.')
step('E15', 'Bench check CK12, part 1: the three unknowns',
     ['CK12 needs the PMU connected on pins 7, 8, 18, 19, 25 and its supply. The record does not say how the PMU is wired for this before E16 terminates the 39-way: if you have no bench lead, take CK12 as soon as E17 has landed those pins - before E19 and before the node goes in the car.',
      '(i) PMU unpowered: ohms from pin 18 to ground and from pin 19 to ground.',
      '(ii) Raise the voltage on pin 7 slowly: the lowest voltage that switches the PMU on; then the current pin 7 draws at 12 V.',
      '(iii) The time from pin 7 going high to O22 coming on.'],
     '(i) 200 kΩ or more keeps the designed margin; (ii) and (iii) are simply recorded - no document gives them.',
     'The 39-way is terminated once and never reopened: do not push trial wires into it.')
step('E15', 'Bench check CK12, part 2: the stages',
     ['With the 47 kΩ baselines standing in for the car (47 kΩ from each line to ground): read the A6 and A8 line voltage at rest.',
      'Close a stand-in for each door switch (24 kΩ + 1N4148 driver, 8.2 kΩ + 1N4148 passenger, from the line to ground) and each A8 switch (4.7 k hazard, 8.2 k horn, 18 k wink L, 33 k wink R) and watch strip inputs 3 and 4.',
      'Do it asleep and awake.'],
     'At rest about 0.166 x the supply on each line (1.99 V at 12.0 V), no wake, and the PMU goes to sleep. Any door or A8 switch: a pulse of about 10 V on the strip input and the PMU wakes. Awake, the lines read about 4.1 V and the excitation is off.',
     'Bench the door stage with the interior lamp wire (RY at battery voltage through its 1N4007) on the switch stand-ins if you can: that is the case the diodes exist for.')

# ------------------------------------------------------------------ E16
brief('E16',
      goal='All 39 cavities of the PMU connector are terminated, locked and pull-tested, each on 18 in of labelled wire.',
      where='bench', time='half a day - confirm',
      tools=['Open-barrel ratchet crimper, 1.5 mm and 2.8 mm dies (P039)', 'Wire strippers and flush cutters (P043)', 'Paint pen (P082)',
             'Label printer (P041)', 'Heat gun for the label shrink (P042)', 'Good light and a magnifier'],
      parts='P015 P012 P009 P010 P011 P019 P020 P021 P017 P070 P075 P076',
      before=['E15 - the wake parts are built', 'CK24 read at M-1: the terminal part numbers on the spare PMU housings (1.5 mm and 2.8 mm) and which terminal pin 15 takes',
              'Practice crimps pulled on scrap with this crimper and these terminals', 'The connector is off the PMU and nothing is powered', 'Eye protection'],
      know=['The PMU-24 has one 39-way connector plus the +12 V stud. Every one of the 39 positions is used [rules spare-capacity]',
            'Three cavity sizes: 11 large (pins 1, 2, 12, 13, 14, 25, 26, 27, 28, 38, 39 - the 2.8 mm die), 27 small (the 1.5 mm die) and one medium, pin 15, whose terminal and die the record does not name - confirm from CK24 [parts P039, checks CK24]',
            'Cavity numbers are the numbers moulded into the connector itself: read them off the part, never mirror a drawing [rules cavity-numbers]',
            'Colours by family: RED power outputs, ORN the 15 A outputs on 14 AWG, GRY analog inputs, BLU wake, PNK the +5 V reference, YEL / GRN CAN high / low, BLK ground [colours]',
            'Large pins carry up to 25 A, the 14 AWG ORN pins 15 A, the 16 AWG RED output pins 7 A [pins hw_max_a]',
            'The +12 V stud is not in this connector: it takes the 2 AWG from the busbar at E17 / E24 [pins STUD]',
            'Pin 25, the ground, lands on the GND bus within 6 in: it is the one wire that will be cut shorter than 18 in when it lands [pins 25]',
            'The two CAN pairs are hand-twisted: 23 with 36 (CAN1), 24 with 37 (CAN2) [colours, pins 23, 24]',
            'It is terminated once and never reopened [work E16]',
            'The terminals of the PMU connector by part number: 1.5 mm 211CC2S2160P (13-17 AWG), 2.8 mm 211CC3S2120 (14-16 AWG) and 211CC3S3120 (10-12 AWG). Their strip length, die and extraction tool are not in the record yet (agent row Y36): use the terminals that came with the connector and the strip length your practice crimps proved [parts P039; 00-CAR S-027]'],
      done_when='39 wires, each labelled, each clicked in and pulled; the secondary lock is on; no wire moves under a firm pull; the lever latched once fully on the PMU with a clear arc.',
      if_not='A terminal that does not click or pulls out: do not force it and do not re-use it - cut it off, crimp a new one. A wire in the wrong cavity: stop, do not pick at it with a pin - raise a note; the record names no removal tool for this connector.',
      record='Tick the row.')
step('E16', 'Mark cavity 1 and lay out the wire',
     ['Find the moulded number 1 on the connector and mark it with the paint pen on the outside of the shell.',
      'Lay out the spools: 12 AWG RED (P015), 14 AWG ORN (P012), 16 AWG RED (P009), GRY (P010), BLU (P011), PNK (P019), YEL (P020), GRN (P021), 10 AWG BLK (P017).'],
     'Cavity 1 is marked where you will see it with wires in.')
step('E16', 'Learn the loop on one wire',
     ['Cut 18 in. Print both labels and wrap them before the next wire is cut (PMU end reads from / to, e.g. O8 / L2-M-1).',
      'Strip, crimp the terminal in the right die, tug it. Insert from the wire side until it clicks. Tug again.',
      'One wire at a time, in cavity order, the list on the screen ticked as you go.'],
     'A click you can feel, and the wire does not come back out.',
     'An open-barrel crimp that folds the wings into the insulation instead of the strands will pass a tug and fail in a year: look at every one under the magnifier.')
step('E16', 'Terminate the eleven large cavities (2.8 mm die)', pins_where(lambda r: r['cav_size'] == 'L'),
     'Eleven large terminals seated: ten 12 AWG RED and pin 25 in 10 AWG BLK.',
     'Pins 1 and 14 are the swap reserves: they are wired like the rest, labelled CAPPED.')
step('E16', 'Terminate the six 15 A output cavities (small, 14 AWG ORN)', pins_where(lambda r: r['cav_size'] == 'S' and r['awg'] == '14'),
     'Six ORN wires seated.', '14 AWG is the largest wire in a small cavity: check the insulation wings close around it, not through it.')
step('E16', 'Terminate the six 7 A output cavities (small, 16 AWG RED)', pins_where(lambda r: r['cav_size'] == 'S' and r['type'] == 'output' and r['awg'] == '16'),
     'Six RED wires seated.')
step('E16', 'Terminate the ten input cavities (small, 16 AWG GRY)', pins_where(lambda r: r['type'] == 'input'),
     'Ten GRY wires seated.')
step('E16', 'Terminate the wake pin and the +5 V pin',
     pins_where(lambda r: r['type'] in ('WAKE', 'REF')) + ['Pin 15 is the one MEDIUM cavity: use the terminal CK24 identified for it. If CK24 did not settle it, stop here and raise a note.'],
     'Pin 7 BLU and pin 15 PNK seated.')
step('E16', 'Terminate the two CAN pairs',
     pins_where(lambda r: r['type'] in ('CAN1', 'CAN2')) + [
         'Twist each pair by hand along its whole 18 in: 23 YEL with 36 GRN, 24 YEL with 37 GRN.',
         'CAN1 needs 120 Ω across pins 23 / 36 at this connector (N56): the record does not say how it is fitted here - solder a 120 Ω (P070) across the pair a short way back from the connector under heat-shrink, and note it.'],
     'Two twisted pairs; 120 Ω between the pin 23 and pin 36 wires.',
     'Keep the pairs twisted right up to the connector.')
step('E16', 'Fit the secondary lock', 'Count the wires: 39. Press the secondary lock home.', 'The lock seats flush; it will not seat over a terminal that is not fully in.',
     'A lock that will not close means a terminal is not seated: find it, do not force the lock.')
step('E16', 'Pull every wire', 'One at a time, a firm straight pull on each of the 39.', 'None moves.')
step('E16', 'Latch it on the PMU once', 'Offer the connector to the PMU on its panel and close the lever fully, then open it and take the connector off again.',
     'The lever closes without force and its arc is clear of every part on the panel.')
step('E16', 'Bundle the tails loosely', 'Group the wires by where they go (L1, L2, L3, L4, relays, strip) with loose ties. Do not tape.', 'A connector with 39 labelled 18 in tails, ready for E17.')

# ------------------------------------------------------------------ E17
DT_PIN = 'Receptacle contacts are PINS: size 16 for 16-18 AWG (P023), size 16 for 14 AWG (P025), size 12 for the DTP power receptacles (P027). Crimp in the Deutsch 4-indent crimper (P038), push in from the wire side until it clicks, tug.'
brief('E17',
      goal='Every node conductor is run, spliced and landed, every receptacle at the post is pinned, plugged and wedge-locked, and the ICU and DCU tails are made.',
      where='bench', time='two days - confirm',
      tools=['Deutsch solid-contact 4-indent crimper, sizes 12 / 16 (P038)', 'Ratchet crimper for heat-shrink terminals and butt splices (P171)',
             'Open-barrel crimper for the relay socket terminals (P039)', 'Wire strippers, flush cutters (P043)', 'Heat gun (P042)', 'Soldering iron (P044)',
             'Contact removal tools, size 16 (P031, P032)', 'Label printer (P041)', 'Multimeter on continuity (P045)', 'Torque wrench (P046)'],
      parts='P023 P025 P027 P028 P029 P126 P127 P128 P129 P130 P132 P133 P115 P099 P124 P078 P079 P071 P070 P114 P136 P140 P015 P013 P012 P009 P010 P011 P008 P019 P020 P021 P018 P017 P074 P075 P076 P077',
      before=['E16 - the 39-way is terminated', 'E15 - the wake strip and stages are built', 'CK08 (M-3, the pop-up motors) is read before the pop-up conductors N08-N15 and N105 are landed',
              'Nothing is powered; the 39-way is off the PMU', 'Eye protection for crimping'],
      know=['A receptacle is the box-side half (DT04 / DTP04, pin contacts); the leg plugs (DT06, socket contacts) are made at E20-E23 [housings]',
            'Every splice at the node is a sealed crimp butt splice with adhesive heat-shrink [work E17, parts P078]',
            'An unfused tap off an output is 14 AWG up to its fuse (the holder\'s own lead), 16 AWG after it [node_conductors N19, N85]',
            'CAN2 never leaves the dash: one twisted pair from pins 24 / 37 to a splice, pairs on to DP-ICU-A 4 / 5, DP-DCU 4 / 5 and the wideband gauge, and a 120 Ω resistor at the end of the run [node_conductors N55, N74, D-346]',
            'The A4 and A5 inputs carry the inhibitor switch alone since D-487: pin 17 goes to L1-S1 11 only and pin 31 to L1-S2 7 only. L2-S 1 / 2 are the pop-up up commands now [node_conductors N40, N41; cavities L2-S 1, L2-S 2; pins 17, 31]',
            'The DCU plugs in later (E26): its two tails end in DT06 plugs at the centre stack and are dust-capped until then [housings DP-DCU, DP-DCU-B, D-472]',
            'The ICU tails are 150 mm from the post [housings DP-ICU-A, D-270]',
            'The DCU tail length is the post to centre-stack run RT11 and the DP-DIAG tail is the run to the glovebox RT12: neither is measured - confirm [routes RT11, RT12]',
            'DT size-16 contacts seal on 14-20 AWG and carry 13 A; DTP size-12 contacts seal on 10-14 AWG and carry 25 A [series DT, DTP]',
            'The seat-feed tails (N108, N109, N112) and the comfort grounds (N102) are routed at E38: at this row their relays are wired and the tails left labelled [work E38]',
            'The load-dump TVS (P136) goes across the PMU main feed at the module; no row says which way round or on which studs - read its datasheet [parts P136, gap]'],
      done_when='Every row of node_conductors is in place and labelled at both ends, every receptacle cavity holds a pin or a sealing plug, every wedgelock is in, the two ICU tails and the two DCU tails end in plugs.',
      if_not='A contact in the wrong cavity: release it with the removal tool (P031 / P032), never pull the wire. A conductor with no home in the lists: stop and raise a note - do not improvise a splice.',
      record='Tick the row.')
step('E17', 'Main power and ground at the node',
     nc_lines(['N57', 'N58', 'N03', 'N04', 'N05', 'N106', 'N107']) + [
         'N01, the 2 AWG main feed onto the busbar stud, is landed in the car at E24: leave its stud free.',
         'N58, the GND bus to the dash star point, is also made in the car (bare metal, star washer, torque, cavity wax): make the 10 AWG lead with its ring now.',
         'Ring terminals with heat-shrink (P079); 10 AWG RED (P018) and BLK (P017).'],
     'Pin 25 beeps to the GND bus and its wire is 6 in or shorter.',
     'Stud torques are not in the record yet (rules torque): tighten to the maker\'s figure written at D1 and mark each nut with the paint pen.')
step('E17', 'The three busbar-fed inline fuses', nc_lines(['N21', 'N75', 'N87']),
     'Each holder\'s busbar-side lead is about 50 mm; each load-side wire is 16 AWG and labelled.')
step('E17', 'Fuse blocks A and B', nc_lines(['N28', 'N29', 'N30', 'N31', 'N68', 'N79']),
     'Block A outputs: F2 to DP-DIAG 3, F3 to L3-S2 2, F19 to L3-S2 10 and L4-S 8, F13 position to L3-S2 7 and L2-M 8. Block B: F1 to L3-M 2, F5 position to L1-S2 9.')
step('E17', 'K11 and the keep-alive', nc_lines(['N06', 'N07', 'N37']), 'Pin 8 reaches strip input 5 and K11 86; K11 85 reaches the GND bus.')
step('E17', 'The O1 pop-up group',
     nc_lines(['N08', 'N09', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15', 'N16', 'N105']) + [
         'F37 (5 A inline) sits between the O1 splice and K1 / K2 terminal 30.',
         'N09: one 1N5819 from the pin 39 (O2) wire and one from the pin 26 (O3) wire, anode to the output, the two banded ends joined to the 14 AWG RED that feeds K1 86 and K2 86.'],
     'Diode test: each output wire to K1 86 conducts one way only. Pin 38 reaches K1 30 and K2 30 only through F37\'s holder.',
     'Do not land these until CK08 has proved the motor matches the factory diagram: if it does not, the whole group is redrawn.')
step('E17', 'The O12 ignition group', nc_lines(['N18', 'N19', 'N20', 'N61', 'N62', 'N78']),
     'Pin 2 reaches L1-P 1 direct, and L1-S1 2, DP-ICU-A 6, the gauge +12 V and L3-S2 12 each through its own holder.')
step('E17', 'The O10 accessory group and the washer relay', nc_lines(['N23', 'N24', 'N73', 'N85', 'N86', 'N88', 'N89', 'N103', 'N25', 'N26', 'N27']),
     'Pin 4 reaches L3-M 1, K12 86, DP-ICU-A 1, L4-S 4 and, through F33, K3 and K4 terminals 30 and 86. The radar tail is capped and labelled.')
step('E17', 'The fuel pump back-stop relay K13', nc_lines(['N69', 'N70', 'N71', 'N72'], note=True),
     'Pin 12 reaches K13 30 and nothing else; K13 87 reaches L4-P 2.',
     'K13\'s coil is fed from the ignition switch wire, never from the PMU: that is what makes it a back-stop.')
step('E17', 'The O15 comfort group and the seat relays', nc_lines(['N17', 'N110', 'N111']) + [
    'K14 87 and K15 87 get their 12 AWG RED tails (N108, N109) at E38; label the two socket terminals now.'],
     'Pin 27 reaches L3-P 2 and both seat relay coils.')
step('E17', 'The lamp outputs and every remaining single output',
     nc_lines(['N22', 'N51', 'N52', 'N53', 'N54']) + [
         'Single conductors, no splice (N60): pin 39 O2 → L2-P 1 · pin 13 O4 → L4-P 1 · pin 10 O7 → L4-M 2 · pin 5 O9 → L2-M 2 · pin 3 O11 → L2-M 3 · pin 1 O13 → L1-P 2 · pin 14 O14 → L1-P 3 · pin 28 O16 → L3-P 1 · pin 20 O19 → L4-M 7 · pin 21 O21 → L1-S1 1.'],
     'Each output pin reaches the receptacle cavities listed and no other.')
step('E17', 'The ladder inputs and the +5 V bias',
     nc_lines(['N96', 'N97', 'N98', 'N99', 'N42', 'N43', 'N44', 'N45', 'N39']) + [
         'Pin 17 (A4) → receptacle L1-S1 11 · pin 31 (A5) → receptacle L1-S2 7, single conductors, no splice (N40, N41).',
         'The 100 Ω 1 W pull-up (P114) goes from the pin 15 wire to the oil-pressure node, the L1-S1 4 to DP-ICU-B 2 conductor.'],
     'Pin 15 to pin 35: 100 kΩ. Pin 15 to pin 22: 100 kΩ. Pin 15 to receptacle L1-S1 4: 100 Ω.')
step('E17', 'The wake strip', nc_lines(['N33', 'N34', 'N35', 'N36', 'N63', 'N76', 'N38']),
     'Strip inputs 1-7 each carry their wire; position 8 goes to pin 7.')
step('E17', 'The sender and lamp lines across the node to the ICU', nc_lines(['N46', 'N47', 'N48', 'N49', 'N50', 'N64', 'N66', 'N67', 'N104']),
     'Each receptacle cavity reaches its DP-ICU-B cavity. The tach shield reaches the GND bus and is insulated at the DP-ICU-B end.',
     'The tach is shielded cable (P074): ground the drain at the GND bus at this end only.')
step('E17', 'CAN1, CAN2 and the terminator', nc_lines(['N55', 'N56', 'N74']) + [
    'The wideband gauge: cut its AEMnet pigtail (it ends in a DTM 2-way) and butt-splice it onto the CAN2 pair; its 0-5 V output is not used; its sensor lead is never cut (devices DV44).'],
     '120 Ω across the CAN2 pair with nothing plugged in; the pairs stay twisted to each plug.',
     'Keep CAN2 50 mm from the blower, wiper and O1 pop-up wires.')
step('E17', 'The permitted ground crossings', nc_lines(['N59']), 'DP-DIAG 4, DP-ICU-A 3, DP-DCU 3 and L3-S2 8 each beep to the GND bus.')
step('E17', 'The post links and the DCU tail conductors', nc_lines(['N81', 'N82', 'N77', 'N80', 'N83', 'N84']),
     'L3-S3 1 / 2 / 3 reach L4-S 5 / 6 / 7; L3-S3 4 reaches L4-S2 7; the DCU tail conductors reach L4-M 9-12, L4-S2 1-5 and L4-P 4.')
step('E17', 'Pin the L1 receptacles', [DT_PIN, 'L1-P (DTP04-4P, wedge WP-4P):'] + node_lines('L1-P') + ['L1-S1 (DT04-12P, wedge W12P):'] + node_lines('L1-S1') + ['L1-S2 (DT04-12P, wedge W12P):'] + node_lines('L1-S2'),
     'Every cavity holds a pin or a sealing plug; the wedgelock snaps in.', 'L1-P 2 and 3 and L1-S2 9 and 11 are pinned here even though the L1 plug carries sealing plugs: they are the swap reserves.')
step('E17', 'Pin the L2 receptacles', ['L2-P (DTP04-4P, wedge WP-4P):'] + node_lines('L2-P') + ['L2-M (DT04-8P, wedge W8P):'] + node_lines('L2-M') + ['L2-S (DT04-6P, wedge W6P):'] + node_lines('L2-S') + ['L2-R (DT04-4P, wedge W4P):'] + node_lines('L2-R'),
     'Every cavity holds a pin or a sealing plug; wedgelocks in.', 'L2-S 1, 2 and 6 take 14 AWG pins (P025).')
step('E17', 'Pin the L3 receptacles', ['L3-P (DTP04-2P, wedge WP-2P):'] + node_lines('L3-P') + ['L3-M (DT04-2P, wedge W2P):'] + node_lines('L3-M') + ['L3-S1 (DT04-12P, wedge W12P):'] + node_lines('L3-S1') + ['L3-S2 (DT04-12P, wedge W12P):'] + node_lines('L3-S2') + ['L3-S3 (DT04-8P, wedge W8P):'] + node_lines('L3-S3'),
     'Every cavity holds a pin or a sealing plug; wedgelocks in.')
step('E17', 'Pin the L4 receptacles', ['L4-P (DTP04-4P, wedge WP-4P):'] + node_lines('L4-P') + ['L4-M (DT04-12P, wedge W12P):'] + node_lines('L4-M') + ['L4-S (DT04-8P, wedge W8P):'] + node_lines('L4-S') + ['L4-S2 (DT04-8P, wedge W8P):'] + node_lines('L4-S2'),
     'Every cavity holds a pin or a sealing plug; wedgelocks in.', 'L4-P 4 is a size-12 pin on 14 AWG: 16 AWG does not crimp in it.')
step('E17', 'Make the two ICU tails',
     ['150 mm from the post, each ending in a DT06 PLUG with socket contacts (P022): these mate the ICU\'s own DT13 receptacles.',
      'DP-ICU-A (DT06-6S, wedge W6S):'] + leg_lines('DP-ICU-A') + ['DP-ICU-B (DT06-12S, wedge W12S):'] + leg_lines('DP-ICU-B'),
     'Two plugs on 150 mm tails; DP-ICU-B 7 holds a sealing plug.')
step('E17', 'Make the two DCU tails',
     ['From the node toward the centre stack along RT11 - length not measured, confirm: cut them only once RT11 is measured (1.5 x the route). Each ends in a DT06 PLUG with socket contacts and gets a dust cap (P140) until E26.',
      'DP-DCU (DT06-6S, wedge W6S):'] + leg_lines('DP-DCU') + ['DP-DCU-B (DT06-12S, wedge W12S):'] + leg_lines('DP-DCU-B'),
     'Two capped plugs; DP-DCU-B 12 holds a sealing plug.', 'DP-DCU 1 is constant 12 V through F22 once the node is powered: keep the cap on.')
step('E17', 'Make the DP-DIAG laptop port tail',
     ['A DT04-4P receptacle for the glovebox on a tail along RT12 - length not measured, confirm.'] + node_lines('DP-DIAG') + ['120 Ω (P070) across cavities 1 / 2 inside the port (cavities DP-DIAG 1).'],
     'About 60 Ω between cavities 1 and 2: the 120 Ω here and the 120 Ω at the PMU connector in parallel on the one pair.')
step('E17', 'Fit the load-dump TVS', 'P136 across the PMU main feed at the module: between the +12 V side (the busbar / PMU stud) and the GND bus, on short leads with ring terminals. Its polarity is on its datasheet, not in the record.',
     'The TVS is fixed and its leads are short.', 'Fitted backwards it is a dead short across the main feed: check the datasheet marking twice.')
step('E17', 'Count the plugs and wedgelocks, label, tidy',
     'Walk every receptacle: a pin or a sealing plug in every cavity (size 16 P028, size 12 P029), wedgelock seated, the housing code on the shell. Every wire labelled at both ends. Bundle loosely with ties; no tape yet.',
     'No empty cavity anywhere; every label reads.')

# ------------------------------------------------------------------ E18
brief('E18',
      goal='The finished node is proved: every PMU cavity reaches what the tables say and nothing else, nothing leaks to ground, the relays and fuses are fitted, every wire is labelled and the panels are photographed.',
      where='bench', time='half a day - confirm',
      tools=['Multimeter with a continuity beeper and a megohm range (P045)', 'Two sharp probe leads and a back-probe pin that fits a DT pin without spreading a socket',
             'The pin list on the laptop or phone', 'Phone camera'],
      parts='P003 P190 P191',
      before=['E17 - every conductor is landed', 'The 39-way is off the PMU; no leg, relay or fuse is fitted; the node is not powered'],
      know=['Continuity is taken with the meter on its beeper [work E18]',
            'Isolation means open: more than 1 MΩ. Any lower reading is a stray strand [work E18]',
            'Nine relays at the node, all the same part (P003): K1 K2 K3 K4 K11 K12 K13 K14 K15. The work row lists five and calls K3 / K4 the luxury package\'s; the relays table has all nine fitted this build [relays, parts P003, D-451, D-469]',
            'Blade fuses come from the drawer, one of every rating in the fuses table [parts P141]',
            'Two blade positions stay empty and keep their labels: F13 (block A position 4) and F5 (block B position 2) [fuses F13, F5]',
            'Through a diode the beeper is one-way: the wake strip inputs and the O2 / O3 pop-up coil taps read as a diode, not as a short [node_conductors N09, N38]',
            'Pin 15 reaches pins 35 and 22 through 100 kΩ each and the oil node through 100 Ω: that is correct, not a fault [node_conductors N39]',
            'The CAN2 pair should read about 120 Ω with nothing plugged in: the one resistor at the node [node_conductors N74]'],
      done_when='All 39 cavities pass continuity and the three must-not-reach touches each; every power cavity reads open to its neighbours and to the ground bus; nine relays and every LIVE fuse are in; photos taken.',
      if_not='A missing continuity: find it now - a contact not seated or a splice not crimped. Any isolation reading under 1 MΩ: stop and find the strand before any power is applied. Do not go on to E19 with an open item.',
      record='Tick the row. Add the photos as a note.')
step('E18', 'Set up', 'The 39-way off the PMU and face-up on the bench, nothing plugged into any receptacle, no relay, no fuse. Meter on the beeper. Short the probes: it beeps.',
     'A beep with the probes together, silence apart.')
step('E18', 'Continuity: the large cavities', ['Touch the cavity at the 39-way, then each place it must reach:'] + pins_where(lambda r: r['cav_size'] == 'L'),
     'A beep at every place listed. Through an inline holder with no fuse there is no beep: bridge the holder with a fuse for the test, then take it out.')
step('E18', 'Continuity: the small output cavities', pins_where(lambda r: r['cav_size'] == 'S' and r['type'] == 'output'),
     'A beep at every place listed.')
step('E18', 'Continuity: the input cavities', pins_where(lambda r: r['type'] == 'input'),
     'A beep at every place listed; pins 35 and 22 also read 100 kΩ to pin 15.')
step('E18', 'Continuity: wake, +5 V and CAN', pins_where(lambda r: r['type'] in ('WAKE', 'REF', 'CAN1', 'CAN2')),
     'Pin 7 beeps to strip position 8. Diode test from each strip input 1-7 to position 8 conducts one way. CAN2 pair about 120 Ω.')
step('E18', 'For each cavity, touch three places it must NOT reach', 'After each continuity pass: the neighbouring cavity either side at the 39-way, the ground bus, and one cavity of a different receptacle.',
     'Silence every time.', 'A beep where there should be none is a crossed pair of wires: fix it before anything else.')
step('E18', 'Isolation', ['Meter on its highest ohms range.', 'Each power cavity (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 20, 21, 26, 27, 28, 33, 34, 38, 39) to its neighbours at the 39-way and to the ground bus.',
                         'The always-hot busbar to the ground bus.'],
     'Open, more than 1 MΩ, everywhere. Bar to ground bus: the TVS (P136) sits across this pair, so red probe on the bar reads open; with the probes reversed a diode-like reading is the TVS itself, not a strand.',
     'Any reading at all is a stray strand: find it now.')
step('E18', 'Check every relay socket before a relay goes in', ['With the meter, each socket terminal against its list:'] + RELAYS_NODE,
     'Each terminal reaches what its line says.')
step('E18', 'Fit the nine relays', 'One P003 in each socket: K1 K2 K3 K4 K11 K12 K13 K14 K15. Press until seated.', 'Nine relays in, each under its label.')
step('E18', 'Fit the fuses', ['By the fuses table:'] + NODE_FUSES + ['MAXI 40 A (P190) in F30, F31, F32; MAXI 25 A (P191) in F35, F36. F13 and F5 stay empty.'],
     'Every LIVE position holds its rating; the two EMPTY positions are empty and still carry their labels.',
     'Read the rating on each fuse as it goes in: a 30 in a 3 A position protects nothing.')
step('E18', 'Check every label and photograph', 'Every node wire labelled at both ends. Photograph the finished panels from every angle, close enough to read the labels.',
     'A set of photos that would let you find any wire without opening the dash.')

# ------------------------------------------------------------------ E19
brief('E19',
      goal='The sleeping current of the finished dash node is measured and is 50 mA or less.',
      where='bench', time='30 min - confirm',
      tools=['Multimeter with a fused 10 A range and a mA range (P045)', 'A 12 V supply for the node through a fused lead'],
      parts='',
      before=['E18 - the node passed continuity and isolation, relays and fuses fitted', 'CK12 read (E15)', 'No leg plugged in; the DCU tails capped'],
      know=['Target 30 mA or less; accept 50 mA or less [work E19, loads LD17, D-280]',
            'What should be drawing: the PMU asleep (no manual figure; a bench report says under 20 mA) and the wake stages (under 0.2 mA). K11 is open when asleep. The DCU is not plugged in yet [loads LD17]',
            'The PMU sleeps when nothing on the wake strip is high; with no key, door or A8 input the keep-alive drops 30 s after the last change [rules sleep]',
            'On a 40 Ah pack 150 mA is about 11 days and 20 mA about 80 days [checks CK02]',
            'This is the PMU\'s share; the whole-car figure is read later at E29 [checks CK02]',
            'It cannot be re-taken once the dash is closed without undoing the install [work E19]',
            'The record does not name the bench supply for this test, nor what configuration the PMU carries before E25: with pin 7 low it should be asleep - confirm [gap]'],
      done_when='A steady reading of 50 mA or less with the PMU asleep, entered in the app.',
      if_not='Above 50 mA: lift the wake-strip branches one at a time (inputs 1 to 7, then F23, F22, F12) and watch the reading to find the branch. Do not close the dash on a failing number: raise a note with the readings.',
      record='Enter the reading in mA (this row takes a value).')
step('E19', 'Connect the supply through the meter', ['Meter on its 10 A range first, in series in the main feed to the always-hot busbar; supply negative to the ground bus.',
                                                 'The record does not name the supply: a 12 V battery through a 5 A inline fuse is the pattern E24 uses for first power.'],
     'The PMU powers; the reading is small.', 'Never start on the mA range: the wake-up current can blow the meter\'s fuse.')
step('E19', 'Let it go to sleep', 'Nothing on strip inputs 1 to 7. Wait at least 30 s after the last change, then a minute more.', 'The reading falls and holds steady.')
step('E19', 'Read it', 'Drop the meter to the mA range once the reading is under its limit. Read for a full minute.', '30 mA or less is the target; 50 mA or less is accepted.')
step('E19', 'If it is high, find the branch', 'Lift one wake-strip input at a time, then pull F23, F22 and F12 one at a time, watching the meter. Put each back before the next.',
     'The reading drops when the offending branch is lifted.')
step('E19', 'Record and disconnect', 'Enter the mA figure in the app. Meter back to volts, leads out of the current sockets. Disconnect the supply.', 'The value is in the app.')

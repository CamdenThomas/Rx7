from lib import *

# The two units, built and run on the bench before the car is stripped (D-541): F3 the Display Unit, F5 and F6
# the Control Unit. No bench supply: USB power on the bench, the car's 12 V at the install (E26, E28, E36-E39).
RUN_SH = 'In a terminal on the Mac: go to the tests folder inside the electrical design folder (02-PROJECTS/01-electrical/00-design/tests) and run ./run.sh. It runs every host suite, checks the board sheets against the record and compiles every sketch for its target.'
FLASH = 'Arduino IDE (Teensyduino) on the Mac: Board Teensy 4.1, CPU 600 MHz, library ACAN_T4 (not FlexCAN_T4). Open the sketch, plug the Teensy in by USB, Upload.'
USB_RAIL = 'A Teensy 4.1 as PJRC ships it joins its USB power to its VIN pin, and VIN is the carrier\'s +5V rail, so the USB lead alone should lift the rail. That link is not written down for these boards: the meter says - confirm'
FIT = 'A part that does not sit on its pads: stop, photograph it against the calipers and raise a note in the app. Do not bend pins or file the board to suit.'

# ------------------------------------------------------------------ F3
brief('F3',
      goal='The Display Unit\'s carrier is built, flashed and proved on the bench on USB power: the Teensy boots and prints its version, the DRIVE page draws through the BT817 board, the gauges follow live bus and sensor inputs and the radio reads the battery. The real bar display and its bridge are lit once block 01.46 has chosen them.',
      where='bench', time='two weekends - confirm',
      tools=['Soldering iron with a fine tip, solder, flux, tweezers (P044)', 'Hot-air or a hot-plate for the small packages if you have one', 'Magnifier', 'Multimeter (P045)',
             'Digital calipers, 0.01 mm, for holding each part against its footprint', 'The Mac with the Arduino IDE (Teensyduino) and the tree',
             'USB leads for the Teensy and the XIAO: on the bench the unit runs from USB, no 12 V supply is used', 'A potentiometer and jumper wires'],
      parts='P103 P169 P104 P105 P106 P107 P109 P110 P159 P176 P203 P122 P116 P108 P142 P143 P117 P118 P119 P120 P151 P202 P070',
      before=['Y16 - the bench kit has arrived; the display (P118) and its bridge (P119) only once block 01.46 has chosen them',
              'Y18 - the ICU carrier boards and their parts have arrived', 'T-048 - bench Teensys 2 and 3 are flashed and labelled: the PMU simulator and the tach simulator',
              'The host suites pass on the Mac (run.sh, exit code 0)', 'An anti-static mat or at least a grounded bench', 'Eye protection while soldering'],
      know=['The Display Unit (ICU in the tables) is the instrument cluster: a Teensy 4.1 socketed on its carrier, a BT817 display bridge, a 12.3-inch bar display and an ESP32-C3 radio, all in one housing behind the binnacle [modules ICU, D-491]',
            'It is built and run on the bench before the car is stripped: the strip (S1) waits on this row and on the Control Unit (F6), and on nothing else of the design [D-541]',
            'Nothing is bought only to test, so there is no 12 V bench supply: on the bench the unit runs from the Teensy\'s USB lead, which proves everything on the board\'s 5 V and 3.3 V rails [D-541]',
            USB_RAIL + ' [ICU carrier README: the socket\'s VIN on +5V]',
            'What waits for the car\'s 12 V, all of it during E28: the 12 V to 5 V buck and its input protection when the unit first boots on O10 (MG02); the illumination reference on DP-ICU-A 2 (MG03); the turn and high-beam tell-tales on DP-ICU-B 10, 11, 12 (MG10, MG11, MG14); the backlight feed on DP-ICU-A 6 through F16 (MG21); the real senders and tach (MG22) [migration MG02, MG03, MG21, MG22; icu_channels IC12, IC13]',
            'It has two plugs: DP-ICU-A (6-way: 1 logic +12 V, 2 illumination, 3 ground, 4 CAN2 H, 5 CAN2 L, 6 backlight +12 V) and DP-ICU-B (12-way: senders, tach, lamp lines) [cavities DP-ICU-A 1, DP-ICU-B 1]',
            'Block 01.46 is open: no shop sells the 900 to 1000 nit bar and no ready-made bridge board exists, so the screen and its bridge are not chosen. Everything else is built and run here; the BT817 eval board (P117, in hand) stands in as the display [blocks 01.46; parts P117, P118, P119]',
            'Display wiring to the BT817 board, single-lane SPI: CS 10, MOSI 11, MISO 12, SCK 13, PD 9, INT 24 [icu_channels IC21]',
            'Each part is held against its footprint before it is soldered - this replaces the separate measurement pass. Expected: DT13 pin pitch 4.445 and 6.35 mm; flange face to pin field 18.675 mm; three flange holes, the 12-way\'s centre hole above all; Teensy header rows 15.24 mm apart; XIAO castellation rows 15.24 mm apart; each within 0.2 mm [checks CK25; D-542]',
            'The first fit check on paper found the 6-way receptacle\'s model 1.54 mm off its pin field, and the ICU and DCU boards placing the DT13 flange differently (on the board edge against 3.955 mm beyond it): one of the two is wrong, and the part in your hand says which [checks CK27]',
            'Every BAT54S clamp has one right way round: signal on COM, A to ground, K to +3V3. The first schematic had all twelve backwards [rules clamp-direction]',
            'Tach input: 2 pulses per revolution; tach_simulator on bench Teensy 3 is the source. Brake warning: low means warn [icu_channels IC04, IC06]',
            'The radio only ever reads the battery\'s BMS: scan always, connect to FFE1 for cell detail, never write, and never touch FFE7 or anything labelled DFU - that is the firmware-update path of the battery that runs the car [icu_channels IC24]',
            'The Teensy carries two PSRAM chips soldered under it, and on this bench revision the coin cell holder for the clock is a flying lead to the Teensy\'s VBAT pad [parts P108, P202]',
            'The odometer persisting through a power cycle is the agent\'s firmware row F-007 and is proved before the meters cutover (MG22). If the version you flash has it, prove it here; if not, say so - this row does not wait for it [work F-007, D-269, D-541]',
            'The firmware version prints at boot; the bench is at ICU 0.6.0-dev [bringup_log 2026-10-12]',
            'No assembly order, reflow profile or per-part test point list is in the record: the BOM csv and the board picture are the guide [work Y17]'],
      done_when='On the bench, on USB: about 5 V on the +5V rail and 3.3 V on +3V3, the Teensy boots and prints its version, the DRIVE page draws on the eval board, rpm / temperature / pressure / fuel follow the simulator and the potentiometer, pulling the PMU simulator blanks only the volts, the radio reports the battery, and the note says which of the real display, its bridge and the odometer proof were not done and why.',
      if_not='No 5 V on the rail from USB: unplug, look for a bridge at the buck and the socket before trying again, and note whether the Teensy itself ran. A blank screen with a booted Teensy: check the six display wires against the list. If the WHOLE cluster blanks when the PMU simulator is unplugged, the failure isolation is not there: raise a note. ' + FIT + ' Anything else unexpected: raise it in the app as a note with the serial output.',
      record='Tick the row. Add a note with the firmware version printed at boot, what was proved, any part that did not match its footprint, and what was left for later (the real display if block 01.46 is still open; the odometer proof if F-007 is not in the version flashed), so the agent can add the bring-up log row.')
step('F3', 'Check what arrived against the BOM', 'The ICU carrier BOM csv, line by line, against the bags. Boards: look at both sides for scratches.', 'Every line present.')
step('F3', 'Hold every part against its footprint before any solder',
     ['On a bare board, dry, one part at a time, with the calipers:',
      'DT13-06PA and DT13-12PA (P122): the pins drop into their holes without springing; pin pitch 4.445 and 6.35 mm; flange face to the centre of the pin field 18.675 mm; the three flange holes line up, the 12-way\'s centre hole above all; read the moulded cavity 1 against the board\'s mark. On the 6-way, note how far the housing sits off its pin field (the model says 1.54 mm).',
      'Teensy 4.1 on its headers (P142, P110): rows 15.24 mm apart; room under it for the two PSRAM chips when seated.',
      'XIAO ESP32C3 (P116): castellation rows 15.24 mm apart in its 2 x 7 socket; how far the antenna connector overhangs the edge.',
      'IMU breakout (P109): its two header rows, one of 6 and one of 5 holes.',
      'The BT817 eval board (P117): its host header (CN8 on the ME817EV) against the carrier\'s display header J4 - pitch, pin count, keying.',
      'Every other package against its pads by eye under the magnifier: the buck, the diodes, the capacitors\' can size.'],
     'Each within 0.2 mm of the figure and sitting flat on its pads; anything that is not is written down with its reading.', FIT)
step('F3', 'Run the host suites first', RUN_SH, 'Exit code 0, every suite green.', 'Never flash a Teensy on a red suite.')
step('F3', 'Solder the board, power parts first',
     ['Input protection and the 5 V buck first (the SS34 diodes, the SMBJ33A, the buck and its inductor and capacitors).',
      'Then the small parts by height: resistors, capacitors, the BAT54S clamps, the CAN transceiver, the FETs.', 'Then the sockets and headers: the Teensy socket, the XIAO and IMU sockets, the display header, the two DT13 receptacles last.',
      'R18 has no value yet: leave it out until a bench result picks one of the three bought (P203).'],
     'Every joint wetted; no bridges under the magnifier.', 'The buck is a 2 x 3 mm leadless package: it needs hot air or a hot plate, and its orientation mark matched to the board.')
step('F3', 'Check the power section with the meter, unpowered',
     ['Nothing connected. Meter on ohms: the Teensy socket\'s VIN pad to a ground pad; DP-ICU-A 1 to DP-ICU-A 3; DP-ICU-A 6 to DP-ICU-A 3. None may be a short (a reading that climbs as the capacitors charge is right).',
      'Meter on diode test across each SS34: it conducts from the 12 V pin toward the board and blocks the other way.',
      'The 12 V side is not powered on the bench: its first power is in the car, when the unit boots on O10 at MG02 in E28.'],
     'No short on either rail; both input diodes the right way round.', 'A reversed input diode or a bridged buck is found here with a meter, or in the car with a fuse: find it here.')
step('F3', 'Fit the PSRAM and socket the Teensy', 'Solder the two 8 MB PSRAM chips (P108) to the pads under the Teensy 4.1, then press the Teensy into its socket with the USB end where the board marks pad 1.',
     'Teensy seated square, USB end at the marked end.', 'A Teensy in backwards puts 5 V on a ground pin.')
step('F3', 'Power it from USB and read the rails', ['USB lead from the Mac to the Teensy: this is the bench supply.', 'Meter on DC volts: the socket\'s VIN pad to ground, then a 3V3 pin to ground.'],
     'About 5 V on VIN and the +5V rail, 3.3 V on +3V3; nothing warm.', 'If VIN reads nothing with the Teensy running, its USB-to-VIN link is open: stop and note it - do not bridge it without asking.')
step('F3', 'Flash the ICU firmware', [FLASH, 'The sketch is icu.ino in the display unit\'s firmware folder. Do not put the simulator sources in the sketch folder.'],
     'The serial monitor prints the firmware version at boot.')
step('F3', 'Flash the radio', 'The icu_radio sketch for the XIAO ESP32C3, over its own USB. Then seat the XIAO in its socket.', 'It uploads; the ICU later reports battery data from it.',
     'Never write to the BMS and never touch its FFE7 or DFU service.')
step('F3', 'Build the bench bus',
     ['Bench Teensy 2 running pmu_sim and Teensy 3 running tach_simulator (T-048), each on its own USB lead.', 'pmu_sim needs an SN65HVD230 module (P143) with its headers soldered; the carrier has its own transceiver.',
      'One twisted pair between them: CAN H to DP-ICU-A 4, CAN L to DP-ICU-A 5, with a 120 Ω resistor (P070) across the pair at each end.',
      'Receiving the PMU\'s frames is the agent\'s firmware row F14: if the version flashed does not have it yet, the diagnostics page shows nothing - note it and go on.'],
     'The ICU\'s diagnostics page shows frames arriving.')
step('F3', 'Connect the BT817 eval board', 'Six signal wires from the carrier\'s display header to the eval board: CS 10, MOSI 11, MISO 12, SCK 13, PD 9, INT 24, plus power and ground as the eval board\'s sheet shows.',
     'The eval board\'s screen lights and draws the DRIVE page.', 'The eval board\'s own supply pins are on its datasheet, not in the record: read it before applying power.')
step('F3', 'Feed it the signals that need no 12 V',
     ['A potentiometer from DP-ICU-B 1, then 2, then 3 to ground stands in for the water-temp, oil-pressure and fuel senders.', 'tach_simulator\'s pulse output into DP-ICU-B 4.',
      'DP-ICU-B 6 to ground for the brake warning.',
      'Left for the car, because each needs 12 V on its line: the left turn, right turn and high-beam tell-tales (DP-ICU-B 10, 11, 12), the illumination reference (DP-ICU-A 2) and the backlight feed (DP-ICU-A 6).'],
     'Each gauge follows its input; BRAKE shows with cavity 6 low.')
step('F3', 'Prove the failure isolation', 'Unplug the PMU simulator\'s USB lead.', 'Volts blanks; rpm, temperature, pressure and fuel carry on.',
     'If everything blanks, stop and raise a note: the gauges must not depend on the bus.')
step('F3', 'Zero the IMU and check the battery path', 'Board flat and still: zero the IMU. With the battery in range: the four cell counts summed agree with the advertised pack millivolts.', 'IMU reads zero at rest; cells sum to the pack figure.')
step('F3', 'Prove the odometer persists, if the firmware has it',
     'Only if the version flashed carries F-007. Run tach_simulator\'s speed channel into DP-ICU-B 8 until the odometer moves. Note the figure. Unplug the USB lead, wait, plug it in again. Then check the card (P151) holds it too.',
     'The same odometer figure after the power cycle, and on the card - or a line in the note that the firmware flashed does not have it yet.')
step('F3', 'Bring up the real bar display, once block 01.46 has chosen it',
     ['If block 01.46 is still open, or the panel (P118) and its bridge (P119) are not in hand: skip this step, say so in the note, and the row is still done.',
      'Otherwise connect the chain as the block\'s answer set it and run the timing check V-084: pixel clock and sync polarity against the panel. The panel\'s backlight needs its own supply: read its sheet first.'],
     'A stable full-width picture, no tearing or rolling - or a note that the display waits on block 01.46.', 'Do not buy a panel to finish this step: the block decides which one.')
step('F3', 'Record it', 'Note the version, what was proved, what did not match its footprint and what was left for later, in the app.', 'A note the agent can turn into a bring-up log row. With F6 done as well, the strip (S1) opens.')

# ------------------------------------------------------------------ F5
brief('F5',
      goal='The Control Unit\'s three boards - the DCU carrier, the upper connector board and the panel board - are built from Y18\'s order, every part held against its footprint before it was soldered, the power sections pass their unpowered checks, and the boards are joined ready for F6.',
      where='bench', time='two weekends - confirm',
      tools=['Soldering iron with a fine tip, solder, flux, tweezers (P044)', 'Hot-air or a hot-plate for the power packages', 'Magnifier', 'Multimeter (P045)',
             'Digital calipers, 0.01 mm, for holding each part against its footprint'],
      parts='P144 P170 P145 P146 P147 P148 P149 P150 P153 P157 P177 P178 P193 P175 P195 P194 P196 P155 P173 P192 P142',
      before=['Y18 - the boards and their parts have arrived. The order was placed there: nothing is ordered in this row',
              'An anti-static mat or at least a grounded bench', 'Eye protection while soldering'],
      know=['The Control Unit (DCU in the tables) is the dash and climate unit: a Teensy 4.1 socketed on its carrier, inside one box in the centre-stack opening with the control panel on its face [modules DCU, D-479]',
            'It is built on the bench before the car is stripped; F6 then runs it on USB power, and the strip (S1) waits on F6 and the Display Unit (F3) only [D-541]',
            'These are the boards as drawn and as ordered at Y18: the carrier at board rev 0.04, 180 x 80 mm, 2 layers, 1.6 mm, 1 oz. No board waits on a measurement of an opening - the dash is rebuilt around the unit [D-542; work Y18]',
            'Each part is held against its footprint before it is soldered - this replaces the separate measurement pass. Expected on the DT13-06PA, 08PA and 12PA: pin pitch 4.45 and 6.35 mm, the three flange holes on TE\'s pattern, the board edge on each flange\'s rear face [checks CK26; D-542]',
            'The first fit check on paper found the ICU and DCU boards placing the DT13 flange differently (on the board edge against 3.955 mm beyond it): one of the two is wrong, and the part in your hand says which [checks CK27]',
            'The sheets were corrected before the order where pricing found a part that did not match its footprint - a capacitor can size, a transistor\'s voltage rating; anything else that does not fit is a finding [work Y42]',
            'Some parts on the sheet are deliberately not fitted (28 on the bench revision): the BOM marks them [work Y17]',
            'The carrier has three harness receptacles on one edge - DP-DCU (6-way), DP-DCU-B (12-way), DP-DCU-C (8-way comfort) - and the upper board carries DP-DCU-D and DP-DCU-E above them [housings DP-DCU, DP-DCU-C, DP-DCU-D]',
            'Logic power in the car is constant 12 V on DP-DCU 1 (through F22, 3 A), ground on DP-DCU 3; the servo rail has its own 5 V buck fed from DP-DCU-C 5 [dcu_channels SN24, SN25, SN15, SN27]',
            'No bench supply is bought, so neither buck is powered here: both are checked with the meter, unpowered, and first run in the car - the logic buck when the unit is plugged in at E26, the servo buck when DP-DCU-C goes in at E38 [D-541; work E26, E38]',
            'The panel joins the carrier by a 26-way ribbon whose pin 26 is the carrier\'s +5 V through a 0.5 A self-resetting fuse; the panel has no processor and no 12 V of its own [DCU carrier README; panel README; D-458]',
            'No assembly order or reflow profile is in the record: the three BOM csv files and the board pictures are the guide [work Y17]'],
      done_when='All three boards are soldered with every not-fitted part left out; every part matched its footprint or its mismatch is noted; no power rail on the carrier reads as a short and both input diodes are the right way round; the Teensy is socketed and the boards are joined by the ribbon and the inside leads.',
      if_not=FIT + ' A rail that reads as a dead short: do not go on to F6 - find the bridge or the reversed part under the magnifier first. A part missing from the order: note the BOM line; do not substitute a different rating.',
      record='Tick the row when the three boards are built, checked and joined. Add a note with any part that did not match its footprint and any line missing from the order.')
step('F5', 'Check what arrived against the three BOMs', 'The DCU carrier, the upper connector board and the panel board: each BOM csv line by line against the bags, and each bare board against its picture.', 'Every line present; three kinds of board.')
step('F5', 'Hold every part against its footprint before any solder',
     ['On the bare boards, dry, one part at a time, with the calipers:',
      'The DT13 receptacles (P150, P153, P194): pins drop into their holes without springing; pin pitch 4.45 and 6.35 mm; the three flange holes line up; the flange\'s rear face sits on the board edge; the moulded cavity 1 against the board\'s mark.',
      'The Teensy 4.1 on its socket headers (P142, P148): rows 15.24 mm apart, USB end at the marked end, and whether a USB plug still reaches it with the ribbon header beside it.',
      'The 2 x 13 ribbon header and its cable (P157); the small headers (P178) and the inside leads (P196) between the carrier and the upper board.',
      'The power packages against their pads: the two bucks (P146) and the inductor (P177), the switches and the bridge driver of the comfort stage (P149), each capacitor\'s can against its outline.',
      'On the panel board: one key, one encoder and the LED driver (P155, P173, P192) against their pads.'],
     'Each sits flat on its pads and within 0.2 mm; anything that does not is written down with its reading.', FIT)
step('F5', 'Solder the carrier, power parts first', ['Input protection and the logic buck first, then the servo buck.', 'Then the small parts by height, the power switches and the bridge driver, then sockets, headers and the DT13 receptacles last.',
                                                    'Leave out every part the BOM marks not fitted.'],
     'Every joint wetted; no bridges under the magnifier.', 'The power switches have exposed pads underneath: they need hot air or a hot plate.')
step('F5', 'Check the carrier\'s power sections with the meter, unpowered',
     ['Nothing connected. Meter on ohms, none of these may be a short: DP-DCU 1 to DP-DCU 3 (logic 12 V); the Teensy socket\'s VIN pad to ground (the 5 V rail); DP-DCU-C 5 to DP-DCU-C 6 (comfort 12 V); the +5 V pin of a servo header to its ground pin (the servo rail).',
      'Meter on diode test across each input diode: it conducts from the connector pin toward the board and blocks the other way.',
      'Neither buck is powered on the bench: there is no 12 V source here by design.'],
     'Four rails, none shorted; the input diodes the right way round.', 'This is the only check these 12 V sections get before the car: do every reading.')
step('F5', 'Solder the upper connector board', 'The two DT13-12PA receptacles (DP-DCU-D and DP-DCU-E) and its headers, then the short inside leads (P196) that join it to the carrier\'s servo, blower and sensor headers.',
     'Upper board built; each inside lead beeps end to end.')
step('F5', 'Solder the panel board', 'Keys, encoders, the LED driver and its lights, the screen\'s header, and the 2 x 13 ribbon header. Small parts first, the keys and encoders last so they sit square to the faceplate side.',
     'Every key clicks and every encoder turns freely after soldering.')
step('F5', 'Socket the Teensy and join the boards', 'Press a Teensy 4.1 (P142) into the carrier\'s socket, USB end at the marked end. Ribbon (P157) between the carrier\'s header and the panel\'s, keyed one way. Inside leads between the carrier and the upper board.',
     'One assembly of three boards, nothing powered yet.', 'A Teensy in backwards puts 5 V on a ground pin.')
step('F5', 'Note it', 'Tick the row in the app with the footprint findings.', 'Ready for F6.')

# ------------------------------------------------------------------ F6
WAITS = ['first 12 V on the unit, every command off at power-up and through a reset, the window commands, the mirror-heat feed, the wake request and the sleeping current: E26',
         'the release selects, and the hatch and the fuel door opening from their keys: E36', 'the mirror motors and their clutch: E37', 'the seat heat and cool returns and the comfort supply: E38',
         'the servos, the servo rail and the blower duty: E39']
brief('F6',
      goal='The Control Unit is flashed and proved on the bench on USB power alone: it boots and prints its version, every panel key, both seat knobs, the centre knob and the thumbstick register, the screen and the lights work, it talks on the bench bus - and what waits for the car\'s 12 V is written down as a list.',
      where='bench', time='a day - confirm',
      tools=['The Mac with the Arduino IDE (Teensyduino) and the tree', 'A USB lead for the Teensy: it is the only supply', 'Multimeter (P045)',
             'A second Teensy with a transceiver module as the PMU simulator, on its own USB lead (P142, P143)', 'A thermometer'],
      parts='P144 P175 P195 P157 P156 P154 P142 P143 P070',
      before=['F5 - the three boards are built, checked and joined', 'F-017 - the DCU firmware is written (it is: DCU 0.6.0-dev)', 'The host suites pass on the Mac (run.sh, exit code 0)',
              'Nothing from the car and no 12 V source is connected: USB only'],
      know=['Nothing is bought only to test: no bench supply, no test lamps, no spare relay. On USB the unit proves everything that runs from the Teensy\'s 5 V and 3.3 V; every 12 V output is proven in the car, into its real load [D-541]',
            'What USB reaches on the carrier: the Teensy\'s VIN pin is the +5V rail, and +3V3 is the Teensy\'s own output for the light loads - the logic, the I2C bus and the inputs [DCU carrier README: net classes; dcu_channels SN24]',
            'What USB reaches on the panel: all of it. The panel board has no processor, no CAN node and no 12 V - the ribbon\'s +5 V (pin 26, behind a 0.5 A self-resetting fuse on the carrier) and its I2C pair feed the keys, the encoders, the lights and the screen [panel README; DCU carrier README; D-355, D-458]',
            USB_RAIL + ' [DCU carrier README]',
            'What USB cannot reach, because it hangs on the car\'s 12 V: the window commands on DP-DCU-B 1-4 and the mirror-heat feed on DP-DCU-B 9 (high-side switches on logic 12 V), the mirror driver on DP-DCU-B 5-8, the seat returns on DP-DCU-C 1-4 and the servo rail (comfort 12 V on DP-DCU-C 5), the wake request on DP-DCU 6, and both 5 V bucks [dcu_channels SN15, SN16, SN17, SN21, SN22, SN24, SN27; DCU carrier README]',
            'Where each of those is proven, in the car: ' + '; '.join(WAITS) + ' [work E26, E36, E37, E38, E39; D-541]',
            'Off at reset is designed in - pull-downs hold every command off while the Teensy is in reset, the two release select gates on 10 kΩ - and is proven on the real lines at E26, before any load hangs on them [DCU carrier README; D-465; dcu_channels SN23]',
            'The release keys are read here as keys only. The rules that refuse a release - car moving, key on - are the firmware\'s and are proven when the releases are wired, at E36 [D-465, D-484; work E36]',
            'Temperatures: 10 kΩ NTC sensors on DP-DCU-D 8 / 9 (cabin) and DP-DCU 2 (outside air); a one-point check against a thermometer [dcu_channels SN11, SN12]',
            'Asleep on its constant feed the unit should draw about 10 mA: that is read in the car at E26, on F22 [loads LD17; work E26]',
            'How the bench shows each key and encoder reading (serial print or bus frame 0x400) is not written down as a procedure: use the serial monitor, and note what you used [work F-017]'],
      done_when='On USB alone: about 5 V on the +5V rail and at the panel, the version printed at boot, every key, both seat knobs, the centre knob and the stick registering once each, the screen and every light working, frames passing on the bench bus, both temperatures sensible - and the note lists what was left for the car.',
      if_not='No 5 V at the panel with the carrier\'s rail alive: the ribbon is on backwards or the panel fuse has tripped on a short - unplug the ribbon and look. A key that does not read: check the ribbon seating first. A key that reads by itself, or two keys for one press: a bridge on the matrix - find it now. Anything else: note it in the app with the serial output.',
      record='Tick the row. Add a note with the firmware version, anything that did not behave, and the list of what waits for the car, so the agent can add the bring-up log row.')
step('F6', 'Run the host suites', RUN_SH, 'Exit code 0.', 'Never flash on a red suite.')
step('F6', 'Flash the DCU firmware', [FLASH, 'The sketch is dcu.ino in the control unit\'s firmware folder. The same USB lead powers the unit from here on.'], 'The serial monitor prints the DCU firmware version at boot.')
step('F6', 'Read the rails on USB', ['Meter on DC volts: the Teensy socket\'s VIN pad to ground; a 3V3 pin to ground; then, at the panel end of the ribbon, pin 26 to pin 21 or 23 (ground).'],
     'About 5 V on VIN and at the panel; 3.3 V on +3V3; nothing warm.', 'If VIN reads nothing with the Teensy running, its USB-to-VIN link is open: stop and note it - do not bridge it without asking.')
step('F6', 'Connect the bench bus', ['The PMU simulator Teensy with its transceiver module (P143), on its own USB lead: CAN H to DP-DCU 4, CAN L to DP-DCU 5, 120 Ω (P070) across the pair at each end.'],
     'The unit\'s frames show on the simulator: the panel-key frame 0x400 about twice a second.', 'If no frame passes on USB power, note it and go on: the bus is proven again in the car at E26.')
step('F6', 'Read every key', 'Press each panel key in turn: fan mode, recirculate, rear defog, mirror defog, the two window switches up and down, and the left plate\'s hatch and fuel-door keys if the plate is connected (DP-DCU-E).',
     'Each press and release registers once, on its own key. No output moves: none has 12 V.')
step('F6', 'Read the encoders and the thumbstick', 'Turn the centre knob and press it; turn each seat knob. Move the mirror stick in both axes and press it. Set the stick\'s centre and dead-band.',
     'Each click counts once in the right direction; the stick rests at centre and reads both ways on both axes.')
step('F6', 'Check the screen and the lights', 'The screen in its window lights and draws. Each lit key and symbol comes on with its function. With the left plate connected, its five symbols too.',
     'A readable screen; every light works, none stuck on.')
step('F6', 'Check the temperature inputs', 'A 10 kΩ NTC (P154) on DP-DCU-D 8 / 9 and one from DP-DCU 2 to ground: compare each reading with the thermometer.',
     'Both within a degree or two of the thermometer - confirm. If a reading is absurd on USB power, note it: it is read again in the car at E39.')
step('F6', 'Restart it a few times', 'Unplug and replug the USB lead three times, then upload the firmware once more, which restarts the Teensy.',
     'It comes back the same way each time: version printed, screen up, no key registering by itself.')
step('F6', 'Write down what waits for the car', ['Nothing below can be tried on USB; each is proven at the row named, into its real load:'] + WAITS,
     'The list is in the note, so nothing on it is taken as proven.')
step('F6', 'Record it', 'Note the version and any fault in the app.', 'A note the agent can turn into a bring-up log row. With F3 done as well, the strip (S1) opens; E26 plugs the unit into the car.')

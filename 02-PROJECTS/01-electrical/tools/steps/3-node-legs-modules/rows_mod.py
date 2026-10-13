from lib import *

RUN_SH = 'In a terminal on the Mac: go to the tests folder inside the electrical design folder (02-PROJECTS/01-electrical/00-design/tests) and run ./run.sh. It runs every host suite, checks the board sheets against the record and compiles every sketch for its target.'
FLASH = 'Arduino IDE (Teensyduino) on the Mac: Board Teensy 4.1, CPU 600 MHz, library ACAN_T4 (not FlexCAN_T4). Open the sketch, plug the Teensy in by USB, Upload.'

# ------------------------------------------------------------------ F11
brief('F11',
      goal='Every MEASURE part of the ICU carrier has been put under the calipers, the binnacle space is known, the footprints and models are corrected to the readings, and the board passes its design-rule check again.',
      where='desk, with the parts in hand', time='half a day of measuring - confirm; the redraw is the agent\'s',
      tools=['Digital calipers, 0.01 mm', 'Steel rule', 'Good light, a magnifier', 'Phone camera for each reading', 'The laptop with the app'],
      parts='P122 P142 P116 P109 P117 P110 P176 P202',
      before=['F10 - the provisional board is laid out with its 3D model', 'C4 - the space behind the binnacle is measured with the car apart',
              'The parts have arrived with the cart: the DT13 receptacles, a Teensy 4.1 on its headers, the XIAO radio, the IMU breakout, the BT817 eval board'],
      know=['The ICU carrier is the board the Teensy 4.1 plugs into behind the display. Its outline is 110 x 80 mm, provisional until this row [work F9, checks CK25]',
            'Every footprint for the DT13 receptacles was drawn from TE\'s drawings, never from a part in hand [checks CK25]',
            'Expected figures to hold the parts against: DT13 pin pitch 4.445 and 6.35 mm; flange face to pin field 18.675 mm; three flange holes, the 12-way\'s centre hole above all; Teensy header rows 15.24 mm apart; XIAO castellation rows 15.24 mm apart [checks CK25]',
            'Pass mark: each reading within 0.2 mm of the footprint; otherwise the footprint is redrawn and the design-rule check re-run to zero [checks CK25]',
            'Three things the first fit check found: the 6-way receptacle\'s model sits 1.54 mm off its pin field; the ICU and DCU boards place the DT13 flange differently (on the board edge against 3.955 mm beyond it) and one is wrong; the ICU board edge touches its connector plate and wants 0.3 mm of margin [checks CK27, work F11]',
            'The Teensy carries two PSRAM chips soldered under it: the socket must leave room under the board [work F11, parts P108]',
            'The board gains a CR2032 holder on the Teensy\'s VBAT pin for the clock: check the socket footprint brings VBAT out [parts P202, D-493]',
            'The mock-up wants about 331 mm wide x 133 mm tall and 204 mm deep behind the binnacle face with the plugs on - an estimate until C4 [work C4]',
            'The agent redraws the footprints, re-exports the board\'s 3D model and re-runs the enclosure fit check from your numbers; then F1 prints the enclosure and F12 orders the board [work F1, F12, D-453]',
            'Type the caliper readings as the words of this row; the agent files them in the value of check CK25 [checks CK25]'],
      done_when='Every reading in the steps is in the app as a note with a photo, the agent has redrawn what was out by more than 0.2 mm, and the board\'s design-rule check reports zero.',
      if_not='A part that is nothing like its footprint (wrong pitch, a missing flange hole): photograph it beside the calipers and raise a note - do not file the board or bend pins to suit.',
      record='Tick the row once the agent reports the board redrawn and clean. Enter every reading as a note in the app, one line per measurement, in mm.')
step('F11', 'Lay out the parts and zero the calipers', 'Close the jaws, zero, and check on something known (a drill shank). One part at a time on a white sheet; photograph each reading with the calipers in shot.', 'Calipers read 0.00 closed.')
step('F11', 'Measure the DT13-06PA and DT13-12PA (P122)',
     ['Pin pitch along the row and between rows (expect 4.445 and 6.35 mm).', 'Pin diameter (for the hole size).',
      'Flange face to the centre of the pin field (expect 18.675 mm).', 'The three flange holes: positions and diameter. On the 12-way, confirm the centre hole exists.',
      'How far the housing stands off the board, and which corner cavity 1 is (read the moulded number).',
      'On the 6-way: the housing\'s offset from its pin field (TE\'s model shows 1.54 mm).'],
     'Each within 0.2 mm of the figure, or written down as found.')
step('F11', 'Measure the Teensy 4.1 on its headers (P142, P110)', ['Row-to-row spacing (expect 15.24 mm).', 'Height of the Teensy\'s underside above the carrier when seated in the female headers - the PSRAM chips go under there.',
                                                                'Which pads the socket reaches: is VBAT one of them?'],
     'Row spacing within 0.2 mm; a clearance figure in mm; VBAT yes or no.')
step('F11', 'Measure the XIAO ESP32C3 (P116) and the IMU breakout (P109)', ['XIAO: castellation row spacing (expect 15.24 mm), board outline, and how far the u.FL antenna connector overhangs.',
                                                                           'IMU breakout: the two header rows (one of 6, one of 5 holes), their spacing and the outline.'],
     'Readings written down.')
step('F11', 'Measure the BT817 eval board\'s header (P117)', 'The header the carrier\'s display header J4 mates (CN8 on the ME817EV): pitch, pin count, keying, and its position on the eval board.', 'Readings written down.')
step('F11', 'Hold the outline against the binnacle space', 'From C4\'s numbers: the 110 x 80 mm outline, plus the enclosure wall and the mated plugs, inside the measured length, width and depth.',
     'It fits with room for the wall and the plugs, or the note says by how much it does not.')
step('F11', 'Enter the readings and hand over', 'Every reading as a note in the app. The agent then corrects the footprints and models, re-runs the design-rule check to zero, re-exports the 3D model of each board and re-runs the enclosure fit check.',
     'The agent\'s report: design-rule check zero, enclosure fit check clear.')

# ------------------------------------------------------------------ F12
brief('F12',
      goal='The final ICU carrier boards are ordered, after a printed enclosure has been test-fitted around the final board model.',
      where='desk', time='1 h - confirm',
      tools=['The laptop', 'A payment card'],
      parts='P103 P169',
      before=['F11 - the measurement pass is done and the board is redrawn', 'F1 - the enclosure is printed and test-fitted around a bare board (CK27 passed)',
              'The design is frozen (the build track is open)'],
      know=['This is the FINAL board. A bench revision (rev A) of the same board was already ordered at Y18 on the provisional outline, at risk of a re-spin [work F12, D-490]',
            'Two boards are needed, one fitted and one spare; a JLCPCB-class fab sells five [parts P103, work Y17]',
            'Board spec: 2 layers, 1.6 mm, 1 oz copper; the outline was 110 x 80 mm before F11 [work Y18, work F9]',
            'The fab package is the ICU carrier project\'s fab folder: the gerbers zip, the drill files and the BOM csv. The bench revision\'s were icu-carrier-revA-gerbers.zip and icu-carrier-revA-bom.csv; the final revision\'s are exported by the agent after F11 [work Y17]',
            'The BOM csv names each maker\'s part number and marks the unsure ones confirm; R18 has no value yet - three values are bought (P203) [work Y17, Y18]',
            'The cheapest true fit test is a printed enclosure and a bare board: every DT13 through its cut-out with 0.5 mm a side, the board on all four bosses unstressed, the lid closing at all four screws [checks CK27]',
            'It is money, so it is yours [work F12]'],
      done_when='The order for the final ICU carrier boards is placed and its confirmation is noted in the app.',
      if_not='If the fab\'s checker rejects the files or its preview does not look like the board picture, do not approve: raise a note with a screenshot.',
      record='Tick the row when ordered. Add the order number, the board count and the price as a note.')
step('F12', 'Confirm the two gates', 'F11 ticked with the agent\'s clean report; F1\'s printed enclosure closed around a bare board (CK27).', 'Both done.',
     'Ordering before the fit test risks a second re-spin.')
step('F12', 'Get the final fab package', 'Ask the agent (a plan run) for the final ICU carrier fab package: the gerbers zip and the BOM csv, exported after F11\'s changes.', 'A zip and a BOM whose revision is later than rev A.')
step('F12', 'Upload and set the options', 'At the board house: upload the zip. 2 layers, 1.6 mm, 1 oz copper, quantity the smallest batch (five). Check the outline size it reports against the board\'s size after F11.',
     'The preview shows the board\'s shape with the two DT13 footprints on one edge.')
step('F12', 'Check the BOM for parts not already in hand', 'Against what Y18 bought for the bench revision: order only what the final board changed or used up. Every line marked confirm in the BOM is checked on the distributor\'s page before buying.',
     'A short list, or nothing.')
step('F12', 'Order and record', 'Pay. Note the order number, count and price in the app.', 'Order confirmed.')

# ------------------------------------------------------------------ F3
brief('F3',
      goal='The ICU carrier is built, flashed and proved on the bench with its display chain: the screen draws the DRIVE page from live bus and sensor inputs, and the odometer survives a power cycle.',
      where='bench', time='two weekends - confirm',
      tools=['Soldering iron with a fine tip, solder, flux, tweezers (P044)', 'Hot-air or a hot-plate for the small packages if you have one', 'Magnifier', 'Multimeter (P045)',
             'A 12 V bench supply with a current limit', 'The Mac with the Arduino IDE (Teensyduino) and the tree', 'USB cables for the Teensy and the XIAO', 'A potentiometer and jumper wires'],
      parts='P103 P169 P104 P105 P106 P107 P109 P110 P159 P176 P203 P122 P116 P108 P142 P143 P117 P118 P119 P120 P151 P202 P070',
      before=['F2 - the BT817 eval board is in hand', 'F12 - the ICU carrier boards and their parts have arrived', 'The host suites pass on the Mac (run.sh, exit code 0)',
              'An anti-static mat or at least a grounded bench', 'Eye protection while soldering'],
      know=['The ICU is the instrument cluster unit: a Teensy 4.1 socketed on carrier H-001, a BT817 display bridge, a 12.3-inch bar display and an ESP32-C3 radio, all in one housing behind the binnacle [modules ICU, D-491]',
            'It has two plugs: DP-ICU-A (6-way: 1 logic +12 V, 2 illumination, 3 ground, 4 CAN2 H, 5 CAN2 L, 6 backlight +12 V) and DP-ICU-B (12-way: senders, tach, lamp lines) [cavities DP-ICU-A 1, DP-ICU-B 1]',
            'Logic power: 12 V in → 5 V buck → the Teensy\'s VIN; about 0.8 A peak [icu_channels IC12]',
            'The backlight has its own 12 V input on DP-ICU-A 6, never joined to the logic rail on the board; about 2.5 A at 12 V for the bar and its scaler [icu_channels IC13]',
            'Display wiring to the BT817 board, single-lane SPI: CS 10, MOSI 11, MISO 12, SCK 13, PD 9, INT 24 [icu_channels IC21]',
            'Every BAT54S clamp has one right way round: signal on COM, A to ground, K to +3V3. The first schematic had all twelve backwards [rules clamp-direction]',
            'Tach input: 2 pulses per revolution; tach_simulator on a spare Teensy is the bench source [icu_channels IC04]',
            'Brake warning: low means warn [icu_channels IC06]',
            'Bench order: the eval board and the DRIVE page first; the real bar panel (chain ii) only after M-1 sizes the aperture; then the timing check V-084 - pixel clock and sync polarity against the panel [work F3, icu_channels IC21]',
            'The radio only ever reads the battery\'s BMS: scan always, connect to FFE1 for cell detail, never write, and never touch FFE7 or anything labelled DFU - that is the firmware-update path of the battery that runs the car [icu_channels IC24]',
            'The odometer must persist in EEPROM and on the card [work F3, D-269]',
            'The firmware version prints at boot; the bench is at ICU 0.6.0-dev [bringup_log 2026-10-12]',
            'MG22, the meters cutover, waits for this box; nothing else does [work F3]',
            'No assembly order, reflow profile or per-part test point list is in the record: the BOM csv and the board picture are the guide [gap]'],
      done_when='On the bench: 5 V on the logic rail, the Teensy boots and prints its version, the DRIVE page draws on the display, rpm / temperature / fuel follow the simulator and the potentiometer, pulling the PMU simulator blanks only the volts, the backlight switches, and the odometer reads the same after power is cycled.',
      if_not='No 5 V: power off, check the input diode and the buck for a bridge before trying again. A blank screen with a booted Teensy: check the six display wires against the list. If the WHOLE cluster blanks when the PMU simulator is unplugged, the failure isolation is not there: raise a note. Anything else unexpected: raise it in the app as a note with the serial output.',
      record='Tick the row. Add a note with the firmware version printed at boot and what was proved, so the agent can add the bring-up log row.')
step('F3', 'Check what arrived against the BOM', 'The ICU carrier BOM csv, line by line, against the bags. Boards: look at both sides for scratches and check the outline against the DT13 receptacles.', 'Every line present.')
step('F3', 'Run the host suites first', RUN_SH, 'Exit code 0, every suite green.', 'Never flash a Teensy on a red suite.')
step('F3', 'Solder the board, power parts first',
     ['Input protection and the 5 V buck first (the SS34 diodes, the SMBJ33A, the buck and its inductor and capacitors), then stop and test (next step).',
      'Then the small parts by height: resistors, capacitors, the BAT54S clamps, the CAN transceiver, the FETs.', 'Then the sockets and headers: the Teensy socket, the XIAO and IMU sockets, the display header, the two DT13 receptacles last.',
      'R18 has no value yet: leave it out until a bench result picks one of the three bought.'],
     'Every joint wetted; no bridges under the magnifier.', 'The buck is a 2 x 3 mm leadless package: it needs hot air or a hot plate, and its orientation mark matched to the board.')
step('F3', 'Power the bare board, no Teensy', ['Bench supply at 12 V with its current limit set low (a few hundred mA - a bench setting, not a record figure). + to DP-ICU-A 1, − to DP-ICU-A 3.', 'Measure at the Teensy socket\'s VIN pad.'],
     '5 V on VIN; the supply shows a few mA, not the limit.', 'If the supply hits its limit, switch off at once: something is bridged or reversed.')
step('F3', 'Fit the PSRAM and socket the Teensy', 'Solder the two 8 MB PSRAM chips (P108) to the pads under the Teensy 4.1, then press the Teensy into its socket with the USB end where the board marks pad 1.',
     'Teensy seated square, USB end at the marked end.', 'A Teensy in backwards puts 5 V on a ground pin.')
step('F3', 'Flash the ICU firmware', [FLASH, 'The sketch is icu.ino in the display unit\'s firmware folder. Do not put the simulator sources in the sketch folder.'],
     'The serial monitor prints the firmware version at boot.')
step('F3', 'Flash the radio', 'The icu_radio sketch for the XIAO ESP32C3, over its own USB. Then seat the XIAO in its socket.', 'It uploads; the ICU later reports battery data from it.',
     'Never write to the BMS and never touch its FFE7 or DFU service.')
step('F3', 'Build the bench bus',
     ['A second Teensy running pmu_sim and a third running tach_simulator (P142).', 'pmu_sim needs an SN65HVD230 module (P143) with its headers soldered; the carrier has its own transceiver.',
      'One twisted pair between them: CAN H to DP-ICU-A 4, CAN L to DP-ICU-A 5, with a 120 Ω resistor (P070) across the pair at each end.'],
     'The ICU\'s diagnostics page shows frames arriving.')
step('F3', 'Connect the BT817 eval board', 'Six signal wires from the carrier\'s display header to the eval board: CS 10, MOSI 11, MISO 12, SCK 13, PD 9, INT 24, plus power and ground as the eval board\'s sheet shows.',
     'The eval board\'s screen lights and draws the DRIVE page.', 'The eval board\'s own supply pins are on its datasheet, not in the record: read it before applying power.')
step('F3', 'Feed it signals',
     ['A potentiometer from DP-ICU-B 1, then 2, then 3 to ground stands in for the water-temp, oil-pressure and fuel senders.', 'tach_simulator\'s pulse output into DP-ICU-B 4.',
      '12 V onto DP-ICU-B 10, 11 and 12 in turn for the left turn, right turn and high-beam tell-tales.', 'DP-ICU-B 6 to ground for the brake warning.', '12 V on DP-ICU-A 2 for the illumination reference.'],
     'Each gauge follows its input; each tell-tale lights with its line; BRAKE shows with cavity 6 low; the brightness of the display follows the voltage on cavity 2, its dimming reference.')
step('F3', 'Prove the failure isolation', 'Unplug the PMU simulator\'s power.', 'Volts blanks; rpm, temperature, pressure and fuel carry on.',
     'If everything blanks, stop and raise a note: the gauges must not depend on the bus.')
step('F3', 'Prove the backlight switch', '12 V through a 5 A fuse onto DP-ICU-A 6. Watch the backlight output switch with the firmware.', 'Backlight on with the unit awake, off when it is told off.')
step('F3', 'Bring up the real bar panel', ['Only after M-1 has sized the aperture and the panel (P118) and its bridge (P119) are in hand.', 'Connect chain (ii) and run the timing check V-084: pixel clock and sync polarity against the panel.'],
     'A stable full-width picture, no tearing or rolling.', 'Until then the eval board is the display: do not buy the glass early.')
step('F3', 'Prove the odometer persists', 'Run tach_simulator\'s speed channel into DP-ICU-B 8 until the odometer moves. Note the figure. Power off, wait, power on. Then check the card (P151) holds it too.',
     'The same odometer figure after the power cycle, and on the card.')
step('F3', 'Zero the IMU and check the battery path', 'Board flat and still: zero the IMU. With the battery in range: the four cell counts summed agree with the advertised pack millivolts.', 'IMU reads zero at rest; cells sum to the pack figure.')
step('F3', 'Record it', 'Note the version and what was proved in the app.', 'A note the agent can turn into a bring-up log row.')

# ------------------------------------------------------------------ F5
brief('F5',
      goal='The final DCU carrier, the panel board and the upper connector board are ordered with their parts, and the DCU carrier is built and powers up with a correct 5 V rail.',
      where='desk to order, bench to build', time='1 h to order, two weekends to build - confirm',
      tools=['The laptop and a payment card', 'Soldering iron with a fine tip, solder, flux, tweezers (P044)', 'Hot-air or a hot-plate for the power packages', 'Magnifier', 'Multimeter (P045)',
             'A 12 V bench supply with a current limit'],
      parts='P144 P170 P145 P146 P147 P148 P149 P150 P153 P157 P177 P178 P193 P175 P195 P194 P196 P155 P173 P192 P142',
      before=['H-002 - the DCU carrier layout is finished by the agent, which waits on the space behind the centre stack (V-102) and the mirror motor current (luxury W-332)',
              'The design is frozen (the build track is open)', 'Eye protection while soldering'],
      know=['The DCU is the dash / climate control unit: a Teensy 4.1 socketed on carrier H-002, inside the climate control unit in the centre-stack opening with the control panel on its face [modules DCU, D-479]',
            'This is the FINAL board. A bench revision (board rev 0.04) was ordered at Y18 on the provisional 180 x 80 mm outline [work F5, D-490]',
            'Board spec: 2 layers, 1.6 mm, 1 oz; two needed, a fab sells five [work Y18, parts P144]',
            'The panel board (P175) and the upper connector board (P195) are ordered with the DCU board [parts P175, P195, D-459]',
            'The DCU\'s parts were about $88 and the receptacles about $68 on the bench order; check Q3\'s 40 V rating before buying [work Y18]',
            'Some parts on the sheet are deliberately not fitted (28 on the bench revision): the BOM marks them [work Y17]',
            'It has five harness connectors: DP-DCU (6-way), DP-DCU-B (12-way), DP-DCU-C (8-way comfort), and DP-DCU-D / DP-DCU-E on the upper board [housings DP-DCU, DP-DCU-C, DP-DCU-D]',
            'Logic power is constant 12 V on DP-DCU 1 (through F22, 3 A, in the car), ground on DP-DCU 3 [dcu_channels SN24, SN25]',
            'The servo rail has its own 5 V buck fed from DP-DCU-C 5 [dcu_channels SN15, SN27]',
            'The enclosure (P152) is drawn around the laid-out board and V-102\'s measurement [work F5]',
            'No assembly order or reflow profile is in the record [gap]'],
      done_when='Order confirmations for the boards and parts are noted; the DCU carrier is soldered; with 12 V on DP-DCU 1 the Teensy socket\'s VIN pad reads 5 V and the supply current is a few mA.',
      if_not='The fab rejects the files: do not approve, raise a note. No 5 V or the supply hits its limit: power off and look for a bridge or a reversed part before trying again.',
      record='Tick the row when the board is built and its 5 V rail is right. Add the order numbers and prices as a note.')
step('F5', 'Confirm the layout is final', 'H-002 is done in the app and the agent reports the board redrawn to V-102\'s measurement with its design-rule check at zero (CK26).', 'A final board, not the provisional outline.')
step('F5', 'Get the final fab packages', 'Ask the agent for the final packages: the DCU carrier, the panel board and the upper connector board - each a gerbers zip and a BOM csv.', 'Three zips and three BOMs.')
step('F5', 'Order the boards', 'Upload each zip: 2 layers, 1.6 mm, 1 oz copper, the smallest batch. Check each reported outline against the board\'s size.', 'Three boards in one order, previews matching the board pictures.')
step('F5', 'Order the parts', ['From each BOM csv, only what the bench order did not leave in hand.', 'The lines: transceivers (P145), the two bucks (P146), protection (P147), Teensy socket headers (P148), the comfort stage (P149), the DT13 receptacles (P150, P153, P194), the ribbon and its headers (P157), the inductor (P177), the small headers (P178), the ribbon-line parts (P193), the panel\'s keys, encoders, lights and driver (P155, P173, P192), the inside leads (P196).',
                              'Check every line the BOM marks confirm on the distributor\'s page; check Q3\'s voltage rating.'],
     'An order whose lines tick off against the BOMs.')
step('F5', 'Solder the carrier, power parts first', ['Input protection and the logic buck first, then stop and test (next step).', 'Then the small parts by height, the power switches and the bridge driver, then sockets, headers and the DT13 receptacles last.',
                                                    'Leave out every part the BOM marks not fitted.'],
     'Every joint wetted; no bridges under the magnifier.', 'The power switches have exposed pads underneath: they need hot air or a hot plate.')
step('F5', 'Power the bare board, no Teensy', ['Bench supply 12 V with its current limit set low (a few hundred mA - a bench setting): + to DP-DCU 1, − to DP-DCU 3.', 'Measure the Teensy socket\'s VIN pad.'],
     '5 V on VIN; a few mA from the supply.', 'Switch off at once if the supply hits its limit.')
step('F5', 'Check the servo rail', '12 V, the same low limit, + to DP-DCU-C 5 and − to DP-DCU-C 6. Measure the +5 V pin of a servo header.', '5 V on the servo rail.')
step('F5', 'Socket the Teensy and note it', 'Press a Teensy 4.1 (P142) into its socket, USB end at the marked end. Note in the app that the board is built.', 'Ready for F6.')

# ------------------------------------------------------------------ F6
brief('F6',
      goal='The DCU is flashed and proved on the bench: every output is off at reset, every panel key, encoder and the thumbstick is read, and every output drives a lamp or a relay as commanded.',
      where='bench', time='a weekend - confirm',
      tools=['The Mac with the Arduino IDE (Teensyduino) and the tree', 'A 12 V bench supply with a current limit', 'Multimeter (P045)', 'Four or five 12 V test lamps (a few watts each) with clip leads',
             'One spare relay (P003) for the release select test', 'A second Teensy with a transceiver module as the PMU simulator (P142, P143)', 'A thermometer'],
      parts='P144 P175 P195 P157 P156 P154 P142 P143 P070 P003',
      before=['F5 - the DCU carrier is built and its 5 V rails are right', 'F-017 - the DCU firmware is written (it is: DCU 0.6.0-dev)', 'The host suites pass on the Mac (run.sh, exit code 0)',
              'Nothing from the car is connected: lamps and a relay stand in for every load'],
      know=['The loads the DCU drives belong to the luxury package and arrive later: windows, mirrors, seats, servos. On the bench each is a lamp or a relay [work F6, modules DCU]',
            'Off at reset is the first thing proved on every output: a floating pin at boot must never move a window or fire a release [dcu_channels SN16, SN23]',
            'Window commands: DP-DCU-B 1 driver up, 2 driver down, 3 passenger up, 4 passenger down. Each sources 12 V, 1 A per channel, into a relay coil; up and down of one side are never driven together [dcu_channels SN22]',
            'Release selects: DP-DCU-B 10 (hatch, K3) and 11 (fuel door, K4) pull a relay coil to ground. The firmware refuses a release unless the car is stopped, and drops the select after 1.5 s [dcu_channels SN23]',
            'On this bench the DCU refuses every release with the key on, because nothing sends the road-speed frame; with the PMU simulator reporting the key OFF it allows them [design README, D-465, D-484]',
            'Mirror drive: DP-DCU-B 5 motor common, 6 left motor, 7 right motor, 8 the clutch sink. The thumbstick picks direction; a press switches left / right [dcu_channels SN17, cavities DP-DCU-B 5]',
            'Comfort: DP-DCU-C 1-4 are low-side returns (seat heat driver, seat heat passenger, seat cool driver, seat cool passenger); DP-DCU-B 9 is the mirror-heat high side; DP-DCU-C 5 is the 12 V supply in, 6-8 power ground. Heat and cool of one seat are interlocked [dcu_channels SN16, cavities DP-DCU-C 1]',
            'Wake request: DP-DCU 6 goes to 12 V when a panel key is pressed with the car asleep [dcu_channels SN21]',
            'Blower duty: DP-DCU-D 6 / 7, 25 kHz, held off through a reset by a pull-down. Servos: DP-DCU-D 1-3 signals, 4 +5 V, 5 ground, one servo moved at a time [dcu_channels SN14, SN15]',
            'Temperatures: 10 kΩ NTC sensors on DP-DCU-D 8 / 9 (cabin) and DP-DCU 2 (outside air); one-point check against a thermometer [dcu_channels SN11, SN12]',
            'The comfort current shunt is zeroed at no load and checked with one known load [dcu_channels SN13]',
            'Asleep on its constant feed the DCU should draw about 10 mA - to be confirmed here [loads LD17]',
            'How the bench shows each key and encoder reading (serial print or bus frame 0x400) is not written down as a procedure [gap]'],
      done_when='With power applied and through a reset no lamp lights; every key, both seat knobs, the centre knob and the stick register; each output lights its lamp or clicks its relay when commanded and only then; the sleeping current on DP-DCU 1 is noted.',
      if_not='A lamp that lights at power-up or during reset: stop - that output would move something in the car; raise a note naming the cavity. A key that does not read: check the ribbon seating first. Anything else: note it in the app with the serial output.',
      record='Tick the row. Add a note with the firmware version, the sleeping current in mA and anything that did not behave, so the agent can add the bring-up log row.')
step('F6', 'Run the host suites', RUN_SH, 'Exit code 0.', 'Never flash on a red suite.')
step('F6', 'Flash the DCU firmware', [FLASH, 'The sketch is dcu.ino in the control unit\'s firmware folder.'], 'The serial monitor prints the DCU firmware version at boot.')
step('F6', 'Connect power and the bench bus', ['Bench supply 12 V: + through a 3 A fuse (F22\'s rating) to DP-DCU 1, − to DP-DCU 3.',
                                             'The PMU simulator Teensy with its transceiver: CAN H to DP-DCU 4, CAN L to DP-DCU 5, 120 Ω (P070) across the pair at each end.',
                                             'The panel board on its 26-way ribbon; the upper connector board on its inside leads.'],
     'The DCU boots; frames show on the simulator.')
step('F6', 'Prove every output is off at reset', ['A lamp from each of DP-DCU-B 1, 2, 3, 4, 9 and DP-DCU 6 to ground; a lamp from +12 V to each of DP-DCU-C 1, 2, 3, 4 and DP-DCU-B 10, 11.',
                                                '12 V to DP-DCU-C 5, ground to DP-DCU-C 6, 7, 8.', 'Power up; power-cycle three times; then upload the firmware once more with the lamps connected, which restarts the Teensy.'],
     'No lamp lights or flickers at any moment.', 'Any flicker is a fault to fix before this unit goes near the car.')
step('F6', 'Read every key', 'Press each panel key in turn: fan mode, recirculate, rear defog, mirror defog, the two window switches up and down, and the left plate\'s hatch and fuel-door keys if the plate is connected (DP-DCU-E).',
     'Each press and release registers once, on its own key.')
step('F6', 'Read the encoders and the thumbstick', 'Turn the centre knob and press it; turn each seat knob. Move the mirror stick in both axes and press it. Set the stick\'s centre and dead-band.',
     'Each click counts once in the right direction; the stick rests at centre and reads both ways on both axes.')
step('F6', 'Drive the window commands', 'Hold each window switch: watch the lamp on DP-DCU-B 1, 2, 3, 4 in turn. Try up and down of one side together.', 'One lamp per command; never both lamps of one side at once.')
step('F6', 'Drive the release selects', ['A relay coil from +12 V to DP-DCU-B 10, then 11. Set the PMU simulator\'s key to OFF. Press the hatch key, then the fuel-door key.', 'Then set the key to ON and press again.'],
     'Key OFF: the relay clicks and drops out again after about 1.5 s, key held or not. Key ON: nothing - the release is refused.', 'Never both selects at once.')
step('F6', 'Drive the mirror outputs', 'Lamps between DP-DCU-B 5 and 6 (left motor) and 5 and 7 (right motor), and from +12 V to 8 (clutch). Move the stick each way, then press to change sides.',
     'A lamp follows the stick on the selected side only.')
step('F6', 'Drive the comfort outputs', ['Turn each seat knob to heat, then to cool: lamps on DP-DCU-C 1-4.', 'Press the rear defog key, then the mirror-defog key: note which lights the mirror-heat lamp on DP-DCU-B 9 (the channel row says mirror heat follows the defogger, D-442; the panel has had its own mirror-defog key since D-492).',
                                        'Zero the comfort current reading with everything off, then check it with one known load.'],
     'Heat and cool of one seat never light together; the mirror-heat lamp lights from a defog key; the current reading is zero at no load.')
step('F6', 'Check the wake request', 'Let the unit go to sleep, then press a panel key. Lamp or meter on DP-DCU 6.', 'DP-DCU 6 goes to about 12 V on the press.')
step('F6', 'Check blower duty, servos and temperatures', ['Meter or scope on DP-DCU-D 6 against 7: duty follows the fan setting and is zero through a reset.', 'With a servo in hand on DP-DCU-D 1, 4, 5: it moves to each end; set the endpoints. One servo at a time.',
                                                        'A 10 kΩ NTC (P154) on DP-DCU-D 8 / 9 and one on DP-DCU 2 to ground: compare with the thermometer.'],
     'Duty 0-100 %; the servo holds each end without buzzing; both temperatures within a degree or two of the thermometer - confirm.')
step('F6', 'Measure the sleeping current', 'Meter in series in the DP-DCU 1 feed, 10 A range first then mA, unit asleep.', 'About 10 mA - confirm; write down what it is.')
step('F6', 'Record it', 'Note the version, the sleeping current and any fault in the app.', 'A note the agent can turn into a bring-up log row. E26 plugs the unit into the car.')

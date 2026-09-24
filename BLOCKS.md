# BLOCKS

_The one page Camden writes in._

Type your answer after `**SOLVE:**` - on that line or the lines under it. Plain
sentences, any length, no markers to keep. Blank means unanswered. Skipping one costs
nothing: it stays open and comes back.

Nothing here is ever regenerated, and nothing but you writes in it.

**This page holds only what is still open.** Once you answer a block, it is applied
through the record, becomes a decision whose `closes` names it, and is then deleted from
here — `DECISIONS.md` is where a settled question lives, with the reasoning and the
consequences. So a short page means a short queue, not a lost history: search
`DECISIONS.md` for a block's id and you will find the ruling it became.

**Block ids are `project.number`.** `00.01` was the first block ever raised for the
electrical project, `01.07` the seventh for the luxury package. Numbers are never reused,
so gaps are blocks that have already been answered. Each project has its own header
below. (Until 2026-09-21 blocks were `BLK-###`; every old id is still findable in its
project's `retired` table.)

An answered block that is not yet applied is advisory - it never refuses a commit.

## CAR · Car

_Nothing open._

## 00 · Electrical

### 00.29 · How the car runs during the migration weeks
**Ask** Between plugging in L3 (E26) and the last migration (E28), how does the car start and drive, when the key and column switches can only be wired to one harness at a time?
**Opened** 2026-09-23
**Why** At E26 the new ignition switch and the column switches are wired into the new L3 harness. The ignition switch then becomes a signal only: its B terminal is fed from the 5 A fuse F3 into the key ladder. The light, turn, wiper and hazard switches become resistor ladders. A switch contact cannot also feed a factory relay: the relay coil across the contact swamps the resistor, and the PMU reads nonsense. So from E26 the factory harness has no ignition switch and no light, turn or wiper switch. Yet E27 says "the car must start and drive on the factory harness", and E28 moves one load per sitting and drives the car every day. As written, the car cannot start from E26 until every circuit has migrated. Found in the 2026-09-23 risk review; nothing in the record says how this was meant to work. Since D-387 the interior is out from the measurement day until the end of the build, so the car cannot be driven during the migration either way. That takes away (b)'s main benefit.
**Options**
- (a) One cutover weekend. Plug in L3 and migrate every circuit in one go, running E26 to E28 back to back and keeping the migration table as the test order for the day. Nothing extra to buy. The car is off the road for that stretch and is driven only at the end, and a fault found late is found with everything already moved.
- (b) Loads first, switches last. The factory key and column switches keep running the factory harness while each load moves over. Every migrated output is tested from a temporary switch box: toggles plus the same ladder resistors, about $30, plugged into L3. The real switches move over in one final sitting. The car stays drivable on its unmigrated circuits, but once the lamps have moved they work only from the box, so it should not go on the road between those sittings.
**Recommend** (a), unless you need the car on the road during the migration weeks. It has fewer temporary wires to get wrong and costs nothing.
**Stops** The wording of E26 to E28 and the migration table. Nothing already bought changes; (b) adds about $30 of toggles and resistors.
**SOLVE:**

### 00.30 · One 5 A fuse can stop the engine and put the lights out
**Ask** Should F3 (the one 5 A fuse behind the key, the light switch, the brake wake and the K13 fuel back-stop) be split, and should ignition and the headlamps hold their state when their ladder reads open?
**Opened** 2026-09-23
**Why** F3 feeds four things: the ignition switch's B terminal, the light-switch common, the wake-stage pull-ups and the brake wake plunger. Through the ignition switch it also feeds the K13 fuel-pump back-stop coil. The PMU runs ignition as `A16 >= RUN` and the low beams as `A15 == HEAD_LO`, and nothing holds either output when its ladder reads open. So any of these turns off the ignition, the fuel pump and the headlamps together, at speed:
- F3 blows;
- the key-ladder wire breaks;
- a worn contact opens for a moment.

On top of that, ignition's retry is "1 at 2 s, then off until the key leaves RUN", so one glitch leaves the engine dead until you cycle the key. The factory car fed the coils straight from the key. Found in the 2026-09-23 risk review.
**Options**
- (a) Split F3 into two fuses, and hold state on a fault. One fuse feeds the key switch and the K13 coil; the other feeds the light switch and the wake stages, in a free block-B position or one more sealed inline holder (a few dollars). The PMU logic changes so that only a clean OFF reading turns ignition off (an open or fault reading holds RUN while the engine is turning), and the headlamps hold their last state while A15 reads a fault. Costs one fuse position and logic rows.
- (b) Hold state only. The logic change from (a) with nothing bought; F3 stays one fuse and remains a single point for the key, the lights and the fuel back-stop.
- (c) Leave it as designed.
**Recommend** (a). It is a safety call, which is why it is a block and not a silent change.
**Stops** `fuses` F3 and one new position, node conductor N29, the logic rows IGNITION, HEAD_LOW, HEAD_HIGH, TAIL_PARK and FUEL_PUMP, and the PMU configuration entered at E25.
**SOLVE:**

### 00.31 · Pull the old harness while the car is apart, or after a week of driving?
**Ask** With the interior out for the whole build, is the factory harness pulled while the car is still apart, or does the interior go back, the car drive a week on the new harness, and the dash come out a second time to pull it?
**Opened** 2026-09-23
**Why** You ruled that the build starts with the interior out and ends with it going back in (D-387). E30 was written for a car that could be driven during the install. It says to drive a week with the factory harness disconnected at both ends but still in the car, as a fallback, then pull it out intact. With the interior out, the car cannot be driven until the interior is back, and pulling the old harness needs the dash out. Both steps cannot happen with the interior out only once.
**Options**
- (a) Pull it while apart. After the full function check (E29), pull the factory harness intact, box it and keep it until after shakedown, then put the interior back. The dash comes out once, but the week of driving with the old harness still in the car is lost. If something fails in shakedown, the boxed harness is the fallback, and refitting it is a big job.
- (b) Drive a week, then pull it. Put the interior back after E29, drive a week with the old harness disconnected in the car, then take the dash out a second time to pull it. This keeps the fallback, but costs a second dash-out, a weekend.
**Recommend** (a). It matches "interior out once, back in once". E29 already proves every circuit with the car running, and the boxed harness stays kept until shakedown.
**Stops** E30's wording and where the interior-back step (E35) sits. Nothing bought changes.
**SOLVE:**

## 01 · Luxury

### 01.11 · Which hidden radar / laser detector, and what the cluster shows
**Ask** Which concealed radar and laser detector goes in the car, and how much of its alert should the cluster show?
**Opened** 2026-09-23
**Why** You ruled a speed-trap detector with nothing on the windshield, the sensors put where they work best and hidden, and only a warning on the cluster (D-383). Two kinds of product can do that, and they differ in cost and in what the cluster can show. A custom-install system (Escort's MAX Ci 360c / Redline Ci 360c class) comes as separate front and rear radar receivers and laser sensors made to hide behind the bumpers, about $2,000–4,000 and usually sold through installers. Its data link is not published, so the DCU could only read its alert output: the cluster could say RADAR or LASER, but not the band or the direction reliably. A Valentine One is the only detector with a published data link (its ESP bus: band, direction, strength, everything the cluster frame 0x320 carries), about $500, but it is one box with its antennas inside. Hiding it means mounting the whole unit behind a plastic panel with a view ahead. Radar passes through plain plastic, but its laser sensor needs a clear view, so laser detection would suffer. Some custom systems also sell laser "shifters" (jammers); those are illegal in many states and are not part of either option. Detectors themselves are illegal in Virginia and Washington DC.
**Options**
- (a) A custom-install concealed system (Escort MAX Ci 360c class): front and rear sensors hidden in the bumpers. The DCU reads its alert output, and the cluster shows the alert and whatever the output tells it (at least radar vs laser). About $2,000–4,000. Cluster detail is limited to what its outputs give.
- (b) A Valentine One hidden behind a panel with a forward view, on its published ESP link into the DCU. Full band, direction and strength on the cluster. About $500. Laser detection is weaker hidden, and it is one box, not separate sensors.
- (c) Decide later. Nothing is bought; the radar pass-throughs stay capped.
**Recommend** (a), because it is the only one that matches "sensors in useful places, nothing visible"; (b) if full detail on the cluster matters more than hidden laser sensors.
**Stops** The detector's design (Z-002) and its harness pass-through (L3-RDR / L4-RDR). Nothing else.
**SOLVE:**

## 02 · Engine

_Nothing open._

### 02.02 · How the bigger engine leg plugs in at the dash post
**Ask** The swap's engine leg needs 54–68 signal conductors, and the dash post has 24 signal cavities for it. How should the extra conductors connect at the post?
**Opened** 2026-09-23
**Why** Working backwards from every LS and CD009 part (D-394, tables `ls_devices` and `ls_wires`), the power side fits the leg's power plug L1-P exactly: coils on O12, injectors on O13, fan on O14, and the A/C clutch in its spare cavity. The signal side does not. With the ECU at the dash (D-325), every injector driver, coil trigger, crank, cam, knock, throttle and sensor wire runs down the leg. That is **54** signal conductors for what the engine must have, and **68** with every option kept (a MAF, narrowband O2s, VVT, purge, oil temperature, a neutral switch). The signal plugs L1-S1 and L1-S2 hold 24. No choice of ECU changes this, because every ECU drives the same wires. Handover row HO14 said "nothing at the dash node changes"; this is where that has to give.
**Options**
- (a) **More of the same connector.** L1-P stays as it is, and the signal side grows from two 12-way DT plugs to five (60 cavities) or six (72, room for every option). Same contacts, same crimper (P038) and removal tools already on the cart, same method as every other leg. Costs a few more DT housing pairs (confirm price), room on the dash post for 3–4 more receptacles (measured at M-1), and a bigger firewall grommet.
- (b) **One high-density plug for the signals.** One ECU-style connector (Deutsch DRC 50–70-way class) replaces L1-S1 and L1-S2. It is smaller at the post, but needs new size-20 crimp tooling and removal tools, and costs more per connector (confirm). It is the one connector in the car unlike all the others.
- (c) **DTM plugs for the small sensor signals, DT for the drivers.** DTM is the smaller Deutsch family (size 20), so it packs denser at the post. It needs a DTM crimper and removal tool on top of the DT kit.
**Recommend** (a) with six signal plugs. It is literally the same engine-leg connector at the same post, just more of it, and nothing new to buy in tools or to learn. Change to (b) only if the post has no room for four more receptacles.
**Stops** The swap's cavity plan (work J8), the dash-post layout for the leg at the swap, and the firewall grommet size. Nothing in today's build changes: the 12A's leg is built now and cut off at the swap (D-211).
**SOLVE:**

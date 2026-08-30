# OEM RECORD — 1982 RX-7 FB factory electrical, as built

*Rev 2026-08-30 · owns: the archival record of the factory harness. FROZEN — content is never edited to reflect design changes; this header and the task pointer below are the only deliberate exceptions (Audit 4, I-105).*

**FROZEN. Do not edit.** This is the archival record of the car as it left the
factory, decoded from `1982RX7WiringDiagram.pdf`. Design work happens in
`02-PROJECTS/`; corrections to this file only happen if the *diagram* was
misread, never to reflect a design change.

Pin labels were read from 170–300 dpi scans — verifying them against the scans is task `T-017` (the task IDs were renumbered by D-043; this line originally said T-016, which is now the cancelled K-008 diagnosis).
Wire colors: first letter base, second tracer. `GY` = green/yellow, not gray.

---

## Master component list

| Ref      | Component                                 | Zone       | Wires                     | Function                                          |
|----------|-------------------------------------------|------------|---------------------------|---------------------------------------------------|
| **A-01** | Starting motor                            | Engine     | BW (A/T)                  | Solenoid trigger                                  |
| **A-02** | Fusible link 0.5 sq                       | Engine     | LW                        | Ignition feed protection                          |
| **A-03** | Hot start relay                           | Engine     | LW, GR, LW, B             | Carb-era cold start                               |
| **A-04** | Hot start motor                           | Engine     | GR                        | Carb-era cold start                               |
| **A-05** | Sub-zero motor (non-CA)                   | Engine     | BW, Blg                   | Carb-era cold start                               |
| **A-06** | Inhibitor switch (A/T)                    | Engine     | BY, GY, BW, RW            | Park/neutral interlock + back-up                  |
| **A-07** | Sub-zero sensor (non-CA)                  | Engine     | Blg                       | Carb-era cold start                               |
| **A-08** | Alternator w/ regulator                   | Engine     | BW, WB                    | Charging                                          |
| **A-09** | Alternator B+                             | Engine     | WR                        | Charge output                                     |
| **B-01** | Emission control unit                     | Engine     | 20+                       | Carb emissions logic                              |
| **B-02** | Relief solenoid valve                     | Engine     | BrW, B                    | Emissions                                         |
| **B-03** | Throttle sensor                           | Engine     | O, BR, GR                 | Emissions                                         |
| **B-04** | Shutter valve solenoid                    | Engine     | LgY, B                    | Emissions                                         |
| **B-05** | Connector of check                        | Engine     | LgY, GY                   | Diagnostic                                        |
| **B-07** | Air-con solenoid valve                    | Engine     | GW, B                     | A/C idle-up                                       |
| **B-08** | Switching solenoid valve                  | Engine     | Lg, B                     | Emissions                                         |
| **B-10** | Vacuum control solenoid                   | Engine     | G, B                      | Emissions                                         |
| **B-11** | No.2 water temp switch (rad)              | Engine     | LB, LY                    | Emissions                                         |
| **B-12** | No.1 water temp switch (eng)              | Engine     | LB, LW                    | Emissions                                         |
| **B-13** | Heat hazard sensor                        | Engine     | LB                        | Emissions                                         |
| **B-14** | Choke switch & magnet                     | Engine     | BR, LR                    | Carb                                              |
| **B-15** | Choke and check relay                     | Engine     | BW, YL, BW, LR            | Carb                                              |
| **B-16** | Carburetor heater                         | Engine     | Br                        | Carb                                              |
| **B-17** | Air vent valve                            | Engine     | BW                        | Carb                                              |
| **B-18** | Ignition coil (T) trailing                | Engine     | YG, BW                    | Ignition                                          |
| **B-19** | Ignition coil (L) leading                 | Engine     | YL, BW                    | Ignition                                          |
| **B-20** | Igniter (T)                               | Engine     | YG, BW                    | Ignition                                          |
| **B-21** | Igniter (L)                               | Engine     | YL, BW                    | Ignition                                          |
| **B-22** | Condenser                                 | Engine     | BW                        | Ignition                                          |
| **B-24** | Fuel pump                                 | Rear       | BLg, B                    | Fuel                                              |
| **B-25** | Cruise control unit                       | Dash       | 14                        | Cruise                                            |
| **B-26** | Stop switch (cruise)                      | Dash       | Br, RY                    | Cruise cancel                                     |
| **B-27** | Clutch switch (cruise)                    | Dash       | Br, RY                    | Cruise cancel                                     |
| **B-28** | Actuator solenoid valve                   | Engine     | BrR, BrB                  | Cruise                                            |
| **B-29** | Vehicle speed switch                      | Dash       | BR                        | Cruise                                            |
| **B-32** | Kick down switch                          | Dash       | BR                        | A/T kickdown                                      |
| **B-33** | Kick down solenoid                        | Engine     | BR                        | A/T kickdown                                      |
| **C-01** | Fuel gauge tank unit                      | Rear       | B, Y                      | Resistive sender                                  |
| **C-02** | Water temp gauge unit                     | Engine     | YW                        | Resistive sender                                  |
| **C-03** | Brake warning light checker               | Dash       | BR, B                     | Warning logic                                     |
| **C-04** | Parking brake switch                      | Dash       | BR                        | Closure                                           |
| **C-05** | Brake fluid level sensor                  | Engine     | BR, B                     | Closure                                           |
| **C-06** | Oil level sensor                          | Engine     | BG                        | Closure                                           |
| **C-07** | Coolant level unit                        | Engine     | YB, YL, GY, Br, B         | Warning logic                                     |
| **C-08** | Coolant level sensor                      | Engine     | Br                        | Closure                                           |
| **C-09** | Oil pressure gauge unit                   | Engine     | BrY                       | Resistive sender                                  |
| **C-10** | Oscillator (chime)                        | Dash       | G, YB, LR, YR, B          | Warning audio                                     |
| **D-01** | Front washer motor                        | Front      | LY, LB                    | Pump                                              |
| **D-02** | Front wiper motor                         | Front/cowl | L, LB, B, LW, LR          | 2-speed + park                                    |
| **D-03** | Combination switch — wiper                | Dash       | B, LO, LY, LR, LG, LW     | 5-position + one-touch                            |
| **D-04** | Rear washer motor                         | Rear       | LB, L                     | Pump                                              |
| **D-05** | Rear wiper motor                          | Rear       | L, BG                     | Motor                                             |
| **D-06** | Rear wiper & washer switch                | Dash       | B, BG, LW                 | Switch                                            |
| **E-01** | Combination switch — light/dimmer/passing | Dash       | R, WG, RL, RY, RG, RW, GL | 3-position + dimmer                               |
| **E-02** | Retractable headlight switch              | Dash       | RW, WG, LY, RY, R, B      | Pop-up control                                    |
| **E-03** | Retractable headlight motor LH            | Front      | WR, YG, R, RY             | Motor + internal limits                           |
| **E-04** | Retractable headlight motor RH            | Front      | WR, YG, R, RY             | Motor + internal limits                           |
| **E-05** | Instrument panel light control            | Dash       | RL, RG, B                 | Rheostat dimmer                                   |
| **E-06** | Heater illumination light                 | Dash       | RL, B                     | 1.4 W                                             |
| **E-07** | Select lever illumination (A/T)           | Dash       | RL, B                     | 3.4 W                                             |
| **E-08** | Headlight LH                              | Front      | RY, RL, B                 | 50/40 W sealed beam                               |
| **E-09** | Headlight RH                              | Front      | RY, RL, B                 | 50/40 W sealed beam                               |
| **E-10** | Switch panel illumination                 | Dash       | RL, B                     | 3.4 W                                             |
| **E-11** | Headlight cleaner motor                   | Front      | R, LY                     | Pump                                              |
| **F-01** | Back-up light switch (M/T)                | Engine     | GY, RW                    | Not used — car is A/T                             |
| **F-02** | Combination switch — hazard/turn          | Dash       | WG, GW, GY, GR, GO, GB    | Turn + hazard                                     |
| **F-03** | Stop light checker                        | Rear       | W, GL, B, G               | Filament monitor                                  |
| **F-04** | License light                             | Rear       | RG, B                     | 6 W ×2                                            |
| **F-05** | Front turn & parking LH                   | Front      | RG, GR, B                 | 27 W + 8 W                                        |
| **F-06** | Front turn & parking RH                   | Front      | RG, GO, B                 | 27 W + 8 W                                        |
| **F-07** | Rear combination light LH                 | Rear       | GR, RW, G, RG, B          | Turn/backup/stop/tail                             |
| **F-08** | Rear combination light RH                 | Rear       | GO, RW, G, RG, B          | Turn/backup/stop/tail                             |
| **F-09** | Horn LH                                   | Front      | GY                        | Single wire, case ground                          |
| **F-10** | Horn RH                                   | Front      | GY                        | Single wire, case ground                          |
| **F-11** | Stop light switch                         | Dash       | GW, W                     | Pedal closure                                     |
| **F-12** | Front side marker LH                      | Front      | B, RG                     | 3.8 W                                             |
| **F-13** | Front side marker RH                      | Front      | B, RG                     | 3.8 W                                             |
| **F-14** | Rear side marker LH                       | Rear       | B, RG                     | 3.8 W                                             |
| **F-15** | Rear side marker RH                       | Rear       | B, RG                     | 3.8 W                                             |
| **F-16** | Horn relay                                | Front      | GY, GW, GL                | Ground-side triggered                             |
| —        | Control Processing Unit                   | Dash       | X-16, many                | Flasher + wiper INT + chime + belt + key reminder |
| **G-01** | Power antenna relay                       | Dash       | LR, R, LY, B, LG, L       | Antenna control                                   |
| **G-02** | Power antenna motor                       | Rear       | L, LY, R                  | Motor                                             |
| **G-03** | Stereo                                    | Dash       | LR, LgW, RG               | Head unit                                         |
| **G-04** | Radio                                     | Dash       | LW, LR, LgW, LG, LY, RG   | Head unit                                         |
| **G-05** | Front speaker LH                          | Dash       | LG, LW                    | Audio                                             |
| **G-06** | Front speaker RH                          | Dash       | LY, LR                    | Audio                                             |
| **G-08** | Main amp                                  | Dash       | LO, LB, LR, LW, L         | Audio                                             |
| **G-09** | Rear speaker LH                           | Rear       | LR, LO                    | Audio                                             |
| **G-10** | Rear speaker RH                           | Rear       | LW, LB                    | Audio                                             |
| **G-13** | Power antenna switch                      | Dash       | B, LG                     | Switch                                            |
| **G-14** | Blower motor & resistor                   | Dash       | LO, LR, LY, LW            | 3-speed via resistor                              |
| **G-15** | Blower motor switch                       | Dash       | LW, LY, LG, LR, LB        | OFF/LO/MI/HI                                      |
| **G-18** | No.1 A/C relay                            | Engine     | LB, LR, YL, BW            | Clutch control                                    |
| **G-19** | Magnet clutch                             | Engine     | BW                        | A/C compressor                                    |
| **G-21** | Refrigerant pressure switch               | Engine     | YL, YR                    | Safety interlock                                  |
| **G-22** | Frost warning temp switch                 | Engine     | LG, YR                    | Safety interlock                                  |
| **G-23** | Diode (A/C harness)                       | Engine     | LB, YL                    | Flyback                                           |
| **G-24** | Rear window defroster switch              | Dash       | Y, LG                     | Switch + 3.4 W indicator                          |
| **G-25** | Rear window defroster grid                | Rear       | LG, B                     | Resistance grid                                   |
| **H-01** | Glove box light                           | Dash       | LO, BL                    | 3.4 W                                             |
| **H-02** | Glove box light switch                    | Dash       | BL, B                     | Closure                                           |
| **H-03** | Ignition key reminder switch              | Dash       | G, LY                     | Closure                                           |
| **H-04** | Seat belt switch                          | Cabin      | Br, BrW                   | Closure                                           |
| **H-05** | Ignition switch light                     | Dash       | LY, GL                    | 3.4 W                                             |
| **H-06** | Interior & spot light                     | Cabin      | LY, RY                    | 5 W                                               |
| **H-07** | Door switch RH                            | Door       | RY                        | Switch to ground                                  |
| **H-08** | Door switch LH                            | Door       | RY                        | Switch to ground                                  |
| **H-09** | Cigarette lighter                         | Dash       | LY, RL, B                 | Heating element                                   |
| **H-10** | Auto clock                                | Dash       | B, RG, LY, GY             | Constant draw                                     |
| **H-11** | Luggage compartment light                 | Rear       | LY, RB                    | Lamp                                              |
| **H-12** | Luggage compartment light switch          | Rear       | RB                        | Closure                                           |
| **H-13** | Glass hatch release switch                | Dash       | LR, GR                    | Momentary                                         |
| **H-14** | Glass hatch release solenoid              | Rear       | GR, B                     | Solenoid                                          |
| **H-15** | Fuel-door release switch                  | Dash       | LR, GB                    | Momentary                                         |
| **H-16** | Fuel-door release solenoid                | Rear       | GB, B                     | Solenoid                                          |
| **I-01** | Remote control mirror switch              | Dash       | B, WG, LgR, Lg, LgB, LgY  | Select + direction                                |
| **I-03** | Remote control mirror LH                  | Door       | LgY, Lg, B, LgB           | 2 motors                                          |
| **I-05** | Remote control mirror RH                  | Door       | LgY, Lg, B, LgB           | 2 motors                                          |
| **I-06** | Power window switch LH                    | Door/dash  | RL, B, GL, BL             | DPDT reverser                                     |
| **I-07** | Power window switch RH                    | Door/dash  | R, B, G, BL               | DPDT reverser                                     |
| **I-09** | Power window motor LH                     | Door       | R, G                      | Reversible                                        |
| **I-11** | Power window motor RH                     | Door       | R, G                      | Reversible                                        |
| —        | Ignition switch                           | Dash       | WR, BY, BW, WR            | OFF/ACC/IG/ST                                     |
| —        | Battery                                   | Engine bay | —                         | Factory location                                  |
| —        | Fusible link 1.25 sq (X-07)               | Engine bay | WR                        | Main protection                                   |
| —        | Fuse block (X-04)                         | Dash       | —                         | 15 positions                                      |

---

## Fuse & bus map — as built

| Bus | Source                   | Fuse           | Feeds                                                     |
|-----|--------------------------|----------------|-----------------------------------------------------------|
| WR  | Battery via 1.25 sq link | —              | All constant                                              |
| —   | WR                       | 0.3 sq link ×2 | Headlights                                                |
| —   | WR                       | 0.5 sq link    | Ignition switch                                           |
| WG  | WR                       | 10 A           | Hazard flasher; remote mirrors                            |
| GW  | WR                       | 15 A           | **Horn + stop lights**                                    |
| R   | WR                       | 10 A           | Tail/park/marker/license via light switch                 |
| LY  | WR                       | 15 A           | Interior, spot, lighter, clock, luggage, ign switch light |
| LO  | WR                       | 20 A           | Glove box, seat belt warning                              |
| LR  | WR                       | 20 A           | Hatch release, fuel-door release, audio                   |
| GY  | IG                       | 10 A           | **Turn + back-up + instrument cluster**                   |
| BW  | IG                       | 7.5 A          | Alternator excitation                                     |
| BLg | IG                       | 10 A           | Fuel pump                                                 |
| LB  | IG                       | 10 A           | Front wiper & washer                                      |
| L   | IG                       | 10 A           | Rear wiper & washer                                       |
| LO  | IG                       | 20 A           | Blower                                                    |
| Y   | IG                       | 15 A           | Rear defroster                                            |
| BL  | IG                       | 30 A           | Power windows                                             |

## Ground node map — as built

| Node | Location     | Carries                                                                                          |
|------|--------------|--------------------------------------------------------------------------------------------------|
| X-13 | Front / dash | Cluster, CPU/flasher, emission control unit, front lamps, illumination, mirrors, windows, wipers |
| X-14 | Front RH     | RH headlight, RH front lamps                                                                     |
| X-15 | Rear         | Fuel pump, rear lamps, stop lamps, defroster, hatch + fuel-door solenoids                        |

X-13 is the busiest node in the car and the prime suspect for fault K-008.

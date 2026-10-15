# -*- coding: utf-8 -*-
"""Write the two cart files for the bench-revision order (work Y16 / Y18, parts round Y37, 2026-10-13;
Y42 the same day: five lines follow the sheets as corrected - the 68 uF 63 V capacitor, Q1 / Q2, Q3,
the 470 uF line and the one-way TVS diodes; Y44: the two gate dividers - 18 k for DCU R43, ICU R2 one
more 10 k, the 1 k line the DU's alone; the fix pass after the independent read: SQ2364EES, MMBT5551, SL310A,
the 15 V zener, 22 k for the three tell-tale dividers, 1 k for the brake-warning input, DCU C27 on the
100 nF 100 V line - D-549). Kept in the tree since Y44; it was a scratch file called bill.py.
Owns: the three cart files in 00-design/data/. Reads no table: each line's `rows` column names
the parts rows it buys for, and tools/fab_bom.py holds the lines to the boards' BOMs.
usage: bench_cart.py [folder]   -> 00-design/data/ (or the folder named): bench-revA-digikey-cart.csv,
       bench-revA-mouser-cart.csv, bench-revA-bridge-digikey-cart.csv"""
import csv, os, sys

OCT = "another distributor's price on Octopart 2026-10-13"
DKO = "Digi-Key's row on Octopart 2026-10-13"
MOO = "Mouser's row on Octopart 2026-10-13"
EST = "estimate"
MK = "maker's page 2026-10-13"

# group, qty, mpn, maker, what, refs, rows, est_unit_usd, price_source, sub
L = []
def a(*r): L.append(r)

G = "1 DU kit"
a(G, 2, "113991054", "Seeed Studio", "XIAO ESP32C3 radio module", "ICU U8 + one on the desk", "P116:2", 4.99, MK, "")
a(G, 2, "APS6404L-3SQR-SN", "AP Memory", "PSRAM 8 MB SOIC-8, soldered under the Teensy", "ICU Teensy pads", "P108:2", 1.50, EST, "")
a(G, 1, "BS-7", "MPD", "CR2032 holder, PC pins", "clock cell, flying lead to VBAT", "P202:1", 1.60, EST, "any 20 mm coin-cell holder with pins")
a(G, 1, "CR2032", "Panasonic", "CR2032 lithium coin cell", "clock cell", "P202:1", 0.50, EST, "any CR2032")

G = "2 DU carrier"
a(G, 1, "4517", "Adafruit", "LSM6DSOX + LIS3MDL motion sensor board", "ICU U7", "P109:1", 19.95, MK, "")
a(G, 1, "SQD50P06-15L_GE3", "Vishay", "P-FET 60 V TO-252, backlight switch", "ICU Q1", "P107:1", 3.59, OCT, "")
a(G, 2, "DMG3415U-7", "Diodes Inc", "P-FET 20 V SOT-23, radio VBUS switch", "ICU Q3", "P169:1", 0.52, DKO, "Diodes Inc DMP2045U-7: the maker marks DMG3415U not for new designs and names this one - the same SOT-23 pins, 20 V, 8 V gate")
a(G, 1, "LM393DR", "Texas Instruments", "dual comparator SOIC-8", "ICU U4", "P107:1", 0.35, EST, "")
a(G, 1, "SN74LVC1G17DBVR", "Texas Instruments", "Schmitt buffer SOT-23-5", "ICU U5", "P169:1", 0.35, EST, "")
a(G, 2, "BZX84C5V1LT1G", "onsemi", "5.1 V zener SOT-23", "ICU D20", "P107:1", 0.20, OCT, "")
a(G, 2, "0466004.NR", "Littelfuse", "4 A fast fuse 1206", "ICU F1", "P107:1", 1.19, MOO, "")
a(G, 2, "RC2512FK-07100RL", "Yageo", "100 R 1 W 2512", "ICU R6 R11", "P107:2", 0.35, EST, "")
a(G, 2, "RC1210FR-07100KL", "Yageo", "100 k 0.5 W 1210", "ICU R29 R30", "P107:2", 0.20, EST, "")
a(G, 10, "RC0805FR-0715KL", "Yageo", "15 k 1 % 0805", "ICU R7 R9 R12 R19", "P107:4", 0.03, EST, "")
a(G, 10, "RC0805FR-0747KL", "Yageo", "47 k 1 % 0805", "ICU R14 R27", "P107:2", 0.03, EST, "")
a(G, 10, "RC0805FR-0722KL", "Yageo", "22 k 1 % 0805", "ICU R21 R23 R25, the three tell-tale dividers", "P107:3", 0.03, EST, "any 22 k 1 % 0805")
a(G, 5, "MM3Z15VT1G", "onsemi", "15 V zener SOD-323, the backlight switch's gate clamp: the banded end toward F1", "ICU D27", "P107:1", 0.15, EST, "any 15 V 5 % zener in SOD-323 of 200 mW or more (BZT52C15S, MM3Z15VST1G)")
a(G, 10, "RC0805FR-0739KL", "Yageo", "39 k 1 % 0805", "ICU R31", "P107:1", 0.03, EST, "")
a(G, 10, "RC0805FR-0712KL", "Yageo", "12 k 1 % 0805", "ICU R32", "P107:1", 0.03, EST, "")
a(G, 10, "RC0805FR-071M2L", "Yageo", "1.2 M 1 % 0805", "ICU R33", "P107:1", 0.03, EST, "")
a(G, 10, "RC0805FR-071KL", "Yageo", "1 k 1 % 0805", "ICU R16 (the brake-warning input), and R18, first of its three values", "P107:1 P203:1", 0.03, EST, "")
a(G, 10, "RC0805FR-072K2L", "Yageo", "2.2 k 1 % 0805", "ICU R18, third of its three values", "P203:1", 0.03, EST, "")
a(G, 5, "QPC02SXGN-RC", "Sullins", "2.54 mm jumper shunt", "ICU JP1 JP2 and J8A or J8B", "P203:3", 0.10, DKO, "")
a(G, 1, "PPPC082LFBN-RC", "Sullins", "2 x 8 socket header", "ICU J4, the BT817 board's CN8", "P176:1", 0.97, DKO, "")
a(G, 1, "PPPC061LFBN-RC", "Sullins", "1 x 6 socket header", "ICU U7 socket", "P176:1", 0.48, DKO, "")
a(G, 1, "PPPC051LFBN-RC", "Sullins", "1 x 5 socket header", "ICU U7 socket", "P176:1", 0.45, DKO, "")
a(G, 2, "PPPC071LFBN-RC", "Sullins", "1 x 7 socket header", "ICU U8 socket", "P176:2", 0.55, DKO, "")

G = "3 CU carrier"
a(G, 1, "TPS54560BQDDARQ1", "Texas Instruments", "5 A buck HSOP-8, servo rail", "DCU U2", "P146:1", 5.50, EST, "")
a(G, 1, "INA180A1QDBVRQ1", "Texas Instruments", "current-sense amplifier SOT-23-5", "DCU U4", "P149:1", 0.90, EST, "")
a(G, 5, "BTS3011TEATMA1", "Infineon", "protected low-side switch TO-252-5", "DCU U5 U6 U7 U8, U17 the dash-light stage (Y49)", "P149:5", 2.90, EST, "")
a(G, 1, "BTT60501ERAXUMA1", "Infineon", "high-side switch TSDSO-14", "DCU U9", "P149:1", 2.60, EST, "")
a(G, 1, "BTT62004ESAXUMA1", "Infineon", "quad high-side switch TSDSO-24", "DCU U10", "P149:1", 4.80, EST, "")
a(G, 1, "DRV8962QDDWRQ1", "Texas Instruments", "quad half-bridge HTSSOP-44", "DCU U11", "P149:1", 7.50, EST, "")
a(G, 2, "TCA9539QPWRQ1", "Texas Instruments", "I2C expander TSSOP-24", "DCU U12 U13", "P149:2", 2.10, EST, "")
a(G, 2, "SQ2364EES-T1_GE3", "Vishay", "N-FET 60 V 2 A SOT-23, on-resistance given at 1.5 V on the gate, gate 1 source 2 drain 3", "DCU Q1 Q2", "P149:2", 0.60, EST, "only a 60 V SOT-23 N-FET whose on-resistance is given at 2.5 V or less: the gate is driven from 3.3 V, so not SQ2362CES or PMV37ENEA (given at 4.5 V and up)")
a(G, 1, "SQ2361ES-T1_GE3", "Vishay", "P-FET 60 V SOT-23, gate 1 source 2 drain 3", "DCU Q3", "P170:1", 0.80, EST, "nothing under 60 V: its rail is clamped at 53 V (D-273). Vishay SQ2361CES-T1_GE3 is the later version - confirm 60 V and SOT-23 on its page")
a(G, 2, "XAL7030-682MEC", "Coilcraft", "6.8 uH inductor 7 x 7 mm", "DCU L2, one fitted one spare", "P177:2", 3.60, EST, "")
a(G, 2, "B560C-13-F", "Diodes Inc", "60 V 5 A Schottky SMC", "DCU D3 D5", "P149:2", 0.80, OCT, "")
a(G, 2, "SMAJ40A", "Littelfuse", "40 V TVS SMA, one-way (not the CA): the banded end to the mark", "DCU D7 D8", "P170:2", 0.45, OCT, "")
a(G, 2, "1206L050YR", "Littelfuse", "0.5 A resettable fuse 1206", "DCU F1", "P193:1", 0.65, OCT, "")
a(G, 2, "CRA2512-FZ-R010ELF", "Bourns", "10 mOhm 1 % 3 W 2512 sense resistor", "DCU R15 R16", "P149:2", 0.75, EST, "any 10 mOhm 1 % 2512 of 2 W or more")
a(G, 3, "EEE-FK1C471P", "Panasonic", "470 uF 16 V aluminium 8 x 10.2", "DCU C31 C32 C33", "P170:3", 1.00, OCT, "")
a(G, 2, "GRM32ER71A476KE15L", "Murata", "47 uF 10 V X7R 1210", "DCU C14 C15", "P170:2", 0.95, OCT, "low stock on Octopart: Murata GRM32ER61A476KE20L (X5R)")
a(G, 5, "C0805C104K1RACTU", "KEMET", "100 nF 100 V X7R 0805", "DCU C25 C27 C30", "P170:3", 0.41, OCT, "")
a(G, 5, "C0805C103K1RACTU", "KEMET", "10 nF 100 V X7R 0805", "DCU C36 C37", "P170:2", 0.10, OCT, "")
a(G, 10, "CL21B472KBANNNC", "Samsung", "4.7 nF 50 V X7R 0805", "DCU C12", "P170:1", 0.03, EST, "")
a(G, 10, "CL21C470JBANNNC", "Samsung", "47 pF 50 V C0G 0805", "DCU C13", "P170:1", 0.04, EST, "")
a(G, 10, "RC0805FR-07243KL", "Yageo", "243 k 1 % 0805", "DCU R4", "P170:1", 0.03, EST, "")
a(G, 10, "RC0805FR-0752K3L", "Yageo", "52.3 k 1 % 0805", "DCU R5", "P170:1", 0.03, EST, "")
a(G, 10, "RC0805FR-0716K9L", "Yageo", "16.9 k 1 % 0805", "DCU R7", "P170:1", 0.03, EST, "")
a(G, 10, "RC0805FR-0718KL", "Yageo", "18 k 1 % 0805", "DCU R43, Q3's gate divider with R42", "P170:1", 0.03, EST, "any 18 k 1 % 0805")
a(G, 10, "RC0805FR-071K2L", "Yageo", "1.2 k 1 % 0805", "DCU R24 R33", "P170:2", 0.03, EST, "")
a(G, 10, "RC0805FR-0747RL", "Yageo", "47 R 1 % 0805", "DCU R25 R34", "P170:2", 0.03, EST, "")
a(G, 10, "RC0805FR-07100RL", "Yageo", "100 R 1 % 0805", "DCU R38 R40 R46 R71 R72 R73", "P149:4 P193:2", 0.03, EST, "")
a(G, 10, "RC0805FR-07330RL", "Yageo", "330 R 1 % 0805", "DCU R48 R49 R50", "P170:3", 0.03, EST, "")
a(G, 2, "SBH11-PBPC-D13-ST-BK", "Sullins", "2 x 13 shrouded box header, keyed", "DCU J4 and panel J1", "P157:2", 0.60, EST, "any 2 x 13 2.54 mm shrouded keyed header, straight")
a(G, 1, "H3CCS-2606G", "Assmann WSW", "26-way ribbon cable, a socket each end, 6 in", "DCU J4 to panel J1", "P157:1", 3.90, EST, "any 26-way 2.54 mm IDC socket-to-socket cable of 10 to 15 cm")

G = "4 both carriers"
a(G, 4, "TCAN1042HVDRQ1", "Texas Instruments", "CAN transceiver SOIC-8", "ICU U3, DCU U3, one spare each", "P104:2 P145:2", 2.23, DKO, "")
a(G, 2, "LMR36015FSCQRNXRQ1", "Texas Instruments", "1.5 A buck VQFN 2 x 3 mm, logic rail", "ICU U1, DCU U1", "P105:1 P146:1", 3.30, EST, "")
a(G, 2, "XAL4020-222MEC", "Coilcraft", "2.2 uH inductor 4 x 4 mm", "ICU L2, DCU L1", "P159:1 P170:1", 2.60, EST, "")
a(G, 15, "BAT54SLT1G", "onsemi", "dual Schottky clamp SOT-23", "ICU D1-D10 D21 D22, DCU D6", "P107:12 P170:1", 0.15, OCT, "")
a(G, 2, "MMBT3904LT1G", "onsemi", "NPN 40 V SOT-23, on the 5 V rail only", "ICU Q4", "P169:1", 0.14, OCT, "")
a(G, 4, "MMBT5551LT1G", "onsemi", "NPN 160 V SOT-23, the two P-FET gate drivers on the 12 V rails", "ICU Q2, DCU Q4", "P107:1 P170:1", 0.16, EST, "onsemi MMBTA06LT1G (80 V), the same pins; not a 40 V part (MMBT3904)")
a(G, 4, "SL310A-TP", "Micro Commercial (MCC)", "100 V 3 A Schottky, SMA, 0.60 V at 3 A", "ICU D23 D25, DCU D1", "P106:2 P147:1", 0.45, EST, "any 100 V 3 A Schottky in the SMA case with 0.70 V or less at 3 A; not a 40 V part (B340A, SS34): it stands ahead of the 53 V clamp")
a(G, 4, "SMBJ33A", "Littelfuse", "33 V load-dump TVS, SMB, one-way (not the CA): the banded end to the mark", "ICU D24 D26, DCU D2 D4", "P106:2 P147:2", 0.45, OCT, "")
a(G, 4, "EEE-FK1J680UP", "Panasonic", "68 uF 63 V aluminium, 8 x 10.2 mm", "ICU C1, DCU C1 C8 C29", "P106:1 P170:3", 1.27, EST, "Panasonic EEE-FK1J470P (47 uF 63 V, the same can). Not the 100 uF EEE-FK1J101P: a 10 mm can, it does not fit the boards")
a(G, 5, "CGA6M3X7S2A475K200AB", "TDK", "4.7 uF 100 V X7S 1210", "ICU C20, DCU C2 C9 C10", "P159:1 P170:3", 0.95, EST, "any 4.7 uF 100 V X7R or X7S 1210")
a(G, 5, "C0805C224K1RACTU", "KEMET", "220 nF 100 V X7R 0805", "ICU C21 C22, DCU C3", "P159:2 P170:1", 0.63, OCT, "")
a(G, 4, "CL31A226KOHNNNE", "Samsung", "22 uF 16 V X5R 1206", "ICU C2 C23, DCU C7", "P169:1 P159:1 P170:1", 0.45, EST, "an X7R 22 uF 16 V 1206 if the cart offers one")
a(G, 50, "CL21B104KBCNNNC", "Samsung", "100 nF 50 V X7R 0805", "ICU 17 places, DCU 14 places", "P169:16 P159:1 P170:14", 0.02, EST, "")
a(G, 10, "CL21B105KAFNNNE", "Samsung", "1 uF 25 V X7R 0805", "ICU C25, DCU C5 C26 C28", "P159:1 P170:3", 0.05, EST, "")
a(G, 10, "CL21C200JBANNNC", "Samsung", "20 pF 50 V C0G 0805", "ICU C26, DCU C6", "P159:1 P170:1", 0.04, EST, "")
a(G, 4, "CL21B106KOQNNNE", "Samsung", "10 uF 16 V X7R 0805", "ICU C19, panel C1", "P169:1 P192:1", 0.49, MOO, "")
a(G, 50, "RC0805FR-0710KL", "Yageo", "10 k 1 % 0805", "ICU 18 places, DCU 22 places", "P107:16 P169:2 P170:18 P149:4", 0.012, EST, "")
a(G, 20, "RC0805FR-074K7L", "Yageo", "4.7 k 1 % 0805", "ICU 5 places, DCU 11 places", "P107:5 P170:11", 0.02, EST, "")
a(G, 10, "RC0805FR-07100KL", "Yageo", "100 k 1 % 0805", "ICU R4 R41 R43, DCU R1 R3 R35 R45", "P107:1 P159:2 P170:4", 0.03, EST, "")
a(G, 10, "RC0805FR-071K5L", "Yageo", "1.5 k 1 % 0805", "ICU R18's second value, DCU R37 R55 R56 R57", "P203:1 P170:4", 0.03, EST, "")
a(G, 10, "RC0805FR-0724K9L", "Yageo", "24.9 k 1 % 0805", "ICU R42, DCU R2", "P159:1 P170:1", 0.03, EST, "")
a(G, 10, "RC0805JR-070RL", "Yageo", "0 R link 0805", "ICU R44 R45, DCU R9 R10", "P169:2 P170:2", 0.03, EST, "")
a(G, 6, "PPPC241LFBN-RC", "Sullins", "1 x 24 socket header, Teensy socket", "ICU J5, DCU J10, one spare pair", "P110:2 P148:4", 1.53, DKO, "")
a(G, 2, "PRPC040SAAN-RC", "Sullins", "1 x 40 pin strip, cut to length", "ICU J2 JP1-JP3 J8A J8B, DCU J6-J8, upper J3-J5, panel J2", "P169:12 P149:9 P196:9 P155:4", 1.23, DKO, "")
a(G, 6, "B2B-XH-A(LF)(SN)", "JST", "XH 2-way header", "ICU SW1, DCU J3 J5, upper J6 J7", "P169:1 P178:2 P196:2", 0.17, EST, "")
a(G, 5, "XHP-2", "JST", "XH 2-way plug housing", "the two inside leads (the page-button lead went with D-580)", "P178:2 P196:2", 0.10, EST, "")
a(G, 5, "ASXHSXH22K152", "JST", "XH lead, crimped both ends, 22 AWG 6 in", "four for the two inside leads, one spare (the page button's went with D-580)", "P196:4", 0.70, EST, "loose contacts SXH-001T-P0.6 need a small crimper that is in no parts row")

G = "5 CU panel and upper board"
a(G, 1, "IS31FL3236A-TQLS4-TR", "Lumissil", "36-channel LED driver eTQFP-48", "panel U2", "P192:1", 2.60, EST, "")
a(G, 2, "PEC11R-4220F-S0024", "Bourns", "encoder, detents, push, 20 mm shaft", "panel SW7 centre knob; the screen knob on its I2C board (P219, D-580)", "P155:1 P219:1", 1.90, EST, "")
# the screen knob (D-580, D-581, Y50): its I2C encoder board and its STEMMA QT lead, read by the DCU on the bench
a(G, 1, "4991", "Adafruit", "I2C QT rotary encoder board (seesaw, 0x36), STEMMA QT", "the screen knob's board, on the CUR (SN32)", "P219:1", 5.95, EST + ", not read - confirm", "")
a(G, 1, "4210", "Adafruit", "STEMMA QT / Qwiic JST-SH 4-pin cable, 100 mm", "the screen knob's lead to the CUR's J4", "P219:1", 0.95, EST + ", not read - confirm", "length set by the CUR mock-up (Y51) - a 200 mm (4401) if the board sits farther from J4")
a(G, 2, "PEC11R-4220F-N0024", "Bourns", "encoder, detents, no push, 20 mm shaft", "panel SW8 SW9 seat knobs", "P155:2", 1.60, EST, "")
a(G, 2, "B28AP", "NKK", "sprung DPDT toggle (ON)-OFF-(ON), PC pins", "panel SW5 SW6 window switches", "P155:2", 9.50, EST, "")
a(G, 5, "TS02-66-130-BK-160-LCR-D", "Same Sky (CUI)", "6 x 6 mm key, 13 mm tall", "panel SW1-SW4", "P155:4", 0.22, EST, "any 6 x 6 mm through-hole key 13 mm tall on 6.5 x 4.5 mm pins; TS02-66-120-BK-160-LCR-D (12 mm) if the cap's top is 1 mm thick; Omron B3F-1070 is 9.5 mm, not this")
a(G, 10, "1N4148W-7-F", "Diodes Inc", "matrix diode SOD-123", "panel D1-D8", "P155:8", 0.108, DKO, "")
a(G, 15, "LTST-C191TGKT", "Lite-On", "green LED 0603", "panel LED1-LED12", "P192:12", 0.30, EST, "")
a(G, 8, "LTST-C191TBKT", "Lite-On", "blue LED 0603", "panel seat cool LEDs, six", "P192:6", 0.30, EST, "")
a(G, 8, "LTST-C191KRKT", "Lite-On", "red LED 0603", "panel seat heat LEDs, six", "P192:6", 0.25, EST, "")
a(G, 10, "CL10B105KA8NNNC", "Samsung", "1 uF 25 V X7R 0603", "panel C2", "P192:1", 0.03, EST, "")
a(G, 10, "CL10B104KB8NNNC", "Samsung", "100 nF 50 V X7R 0603", "panel C3", "P192:1", 0.02, EST, "")
a(G, 10, "RC0603FR-0710KL", "Yageo", "10 k 1 % 0603", "panel R1", "P192:1", 0.02, EST, "")
a(G, 10, "RC0603FR-07100KL", "Yageo", "100 k 1 % 0603", "panel R2", "P192:1", 0.02, EST, "")
a(G, 1, "1950", "Adafruit", "20 jumper wires, a socket each end, 150 mm", "three 3-wire leads, upper J3-J5 to DCU J6-J8", "P196:1", 1.95, MK, "")

M = []
M.append(("6 sealed receptacles", 1, "DT13-06PA", "TE Deutsch", "6-way flanged board receptacle", "DCU J1", "P150:1", 7.50, EST, ""))
M.append(("6 sealed receptacles", 2, "DT13-12PA", "TE Deutsch", "12-way flanged board receptacle", "DCU J9, upper J1", "P150:1 P194:1", 8.74, "TTI's row on Octopart 2026-10-13", ""))
# D-587 / D-590 (Y63): the Display Unit's two DT13s are one DRC 24-way and its plug; no price was read (2026-10-14) - confirm in the cart
M.append(("6 sealed receptacles", 1, "DRC13-24PA", "TE Deutsch", "24-way 90-degree board receptacle, size 16, key A", "ICU J1", "P227:1", 25.00, EST + ", not read - confirm", ""))
M.append(("6 sealed receptacles", 1, "DRC16-24SA", "TE Deutsch", "24-way jackscrew plug, size 16, key A, for DRC13-24PA", "DP-ICU, the tail from the dash post", "P227:1", 20.00, EST + ", not read - confirm", ""))
M.append(("6 sealed receptacles", 1, "DT13-08PA", "TE Deutsch", "8-way flanged board receptacle", "DCU J2", "P153:1", 10.35, "Mouser's price in a search listing, undated", ""))

# The display bridge board (Y46, D-550, D-561): its own Digi-Key file, so Y18's steps keep their lines;
# loaded into the same cart when both are bought the same night
BR = []
G = "7 bridge board"
BR.append((G, 2, "TFP410PAP", "Texas Instruments", "DVI transmitter HTQFP-64", "bridge U1, one spare", "P119:2", 9.00, EST, "TFP410PAPR (the reel) is the same part"))
BR.append((G, 2, "FH12-50S-0.5SH(55)", "Hirose", "50-way 0.5 mm FPC connector, bottom contact", "bridge J1, one spare", "P119:2", 2.80, EST, "only a bottom-contact 50-way 0.5 mm FPC connector on the same footprint: J1's pin mapping assumes it"))
BR.append((G, 2, "0150200506", "Molex", "50-way 0.5 mm flat cable, contacts on the same side (type A), about 100 mm", "BT817 board CN1 to bridge J1", "P119:2", 3.50, EST, "any 50-way 0.5 mm FFC with contacts on the SAME side at both ends, 0.3 mm thick, long enough for the two boards' places - confirm the part number's type on its drawing"))
BR.append((G, 2, "2086581001", "Molex", "HDMI type A receptacle, horizontal", "bridge J2, one spare", "P119:2", 1.60, EST, ""))
BR.append((G, 2, "AP2112K-3.3TRG1", "Diodes Inc", "3.3 V 600 mA LDO SOT-23-5", "bridge U2, one spare", "P119:2", 0.40, EST, ""))
BR.append((G, 10, "CL10B104KB8NNNC", "Samsung", "100 nF 50 V X7R 0603", "bridge C3-C8", "P119:6", 0.02, EST, ""))
BR.append((G, 10, "CL10B105KA8NNNC", "Samsung", "1 uF 25 V X7R 0603", "bridge C1 C9", "P119:2", 0.03, EST, ""))
BR.append((G, 2, "CL21B106KOQNNNE", "Samsung", "10 uF 16 V X7R 0805", "bridge C2", "P119:1", 0.49, MOO, ""))
BR.append((G, 10, "RC0603FR-07510RL", "Yageo", "510 R 1 % 0603", "bridge R1 (TFADJ)", "P119:1", 0.02, EST, "any 510 R 1 % 0603"))
BR.append((G, 10, "RC0603FR-074K7L", "Yageo", "4.7 k 1 % 0603", "bridge R2", "P119:1", 0.02, EST, ""))
BR.append((G, 10, "RC0603FR-0710KL", "Yageo", "10 k 1 % 0603", "bridge R3 R4", "P119:2", 0.02, EST, ""))
BR.append((G, 2, "B2B-XH-A(LF)(SN)", "JST", "XH 2-way header", "bridge J3, one spare", "P119:1", 0.17, EST, ""))
BR.append((G, 2, "XHP-2", "JST", "XH 2-way plug housing", "the 5 V lead to J3", "P119:1", 0.10, EST, ""))
BR.append((G, 1, "ASXHSXH22K152", "JST", "XH lead, crimped both ends, 22 AWG 6 in", "the 5 V lead to J3", "P119:1", 0.70, EST, ""))

H = ["group", "qty", "mpn", "maker", "what", "refs", "rows", "est_unit_usd", "price_source", "substitute"]
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
for name, rows in (("bench-revA-digikey-cart.csv", L), ("bench-revA-mouser-cart.csv", M),
                   ("bench-revA-bridge-digikey-cart.csv", BR)):
    seen = set()
    for r in rows:
        assert r[2] not in seen, r[2]
        seen.add(r[2])
        assert len(r) == len(H), r
    with open(os.path.join(out, name), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(H)
        w.writerows(rows)
    print(name, len(rows), "lines", "%.2f" % sum(r[1] * r[7] for r in rows))

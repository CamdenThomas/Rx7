# ELECTRICAL BUILD — THE SHOPPING LIST

**Buy exactly what is listed, in the quantity listed, from the store shown.** Every line is a part number or an exact description, a quantity and a store. Nothing here needs to be understood.

**Where the numbers come from.** Four carts were built and reviewed live on 2026-09-02 (Waytek, WireBarn, DeutschConnector.com, Amazon); the cart totals below are those carts. A line marked **cart** is in a cart at that quantity. A line marked **to add** is needed by the design and is not in a cart yet — §8 gathers them. Unit prices marked *est* are estimates (±20 %); the cart total is the real figure. Shipping and tax are not included.

**Substitutions:** allowed only within the same class and rating (a different brand of 40 A SPDT micro relay with a diode is fine). **Never substitute** the Class-T fuse and block, the MRBF, genuine Deutsch contacts, or the SICMA terminals.

**What the parts are for:** every wire, connector, fuse and relay here is named in `../01-DESIGN/DESIGN.md`; the install plan says when each one is used.


## Totals

| Store | Lines | Cart total (2026-09-02) |
|---|---|---|
| Waytek | 11 | $455.04 |
| WireBarn | 8 | $382.68 |
| DeutschConnector.com | 26 | $944.08 |
| Amazon | 49 | $1,096.22 |
| **Four carts** | **94** | **$2,878.02** |
| Still to add (§8) | ~10 | ≈ $90 |
| Vehicle parts, not yet carted (§6) | 5 | ≈ $175 est |
| Hardware store, after the measurement day (§7) | — | ≈ $40 est |
| **Everything** | | **≈ $3,180** |

## Already in hand — do not buy

- ECUMaster PMU-24 DL with its 39-way connector, 39 terminals and the USB-to-CAN adapter
- Two spare SICMA 39-way housings, each with a full pin set — **these are the practice and spare terminals** (the car uses 27 small + 12 large; the two spare sets are 54 small + 32 large)
- Ionic S9 lithium battery, heated car-post version
- UNI-T UT210E clamp meter
- Blade fuses — check the drawer against §9 before buying any
- Electrical tape, paint pen

---

## 1 · Waytek — fuse blocks, relays, sockets, busbar, 16 AWG wire spools

https://www.waytekwire.com/ · **cart $455.04, 11 lines**

| Waytek # | Item | Qty | Used for |
|---|---|---|---|
| 45643 | OptiFuse BLR-504 ATC fuse block, 4-position, bussed input | 2 | Block A (busbar: F2, F3, F19, F13 empty) · Block B (K11: F1, F5, 2 spare) |
| 46047 | Sealed inline ATC fuse holder, 14 AWG leads | 3 | F12, F15, F16 at the dash node |
| 75725 | Song Chuan 871-1C-C-D1-12VDC — ISO micro relay 40 A SPDT, integral diode | 4 | K1, K2, K11, K12 (no spare) |
| 74858 | Picker PC792E-1C-C-12S-DN-X — sealed mini ISO relay SPDT, integral diode | 1 | K9, engine bay |
| 75340 | Chief weatherproof 5-pin mini relay connector | 1 | K9's socket |
| 75290 | Panel-mount micro relay socket with terminals | 10 | 6 at the dash node (K1–K4, K11, K12) + 4 at the sill (K5–K8, empty) |
| 78250 | Blue Sea 2301 busbar, 10-gang 150 A | 1 | **The ground bus.** The always-hot bar needs a cover — see §8 |
| WL16-0 | Prysmian GXL 16 AWG **BLACK**, 500 ft spool | 1 | Ground family — 230 ft needed |
| WL16-2 | Prysmian GXL 16 AWG **RED**, 500 ft spool | 1 | Power family at 16 AWG — 480 ft needed |
| WL16-8 | Prysmian GXL 16 AWG **GRAY**, 1000 ft spool | 1 | Analog-input family — 645 ft needed |
| WL16-6 | Prysmian GXL 16 AWG **BLUE**, 500 ft spool | 1 | Command family — 285 ft needed |

The four spools are about $355 of the cart. Every 16 AWG wire in the car except pink, the CAN pair and the shielded tach comes off these.

---

## 2 · WireBarn — 14, 12 and 10 AWG GXL by the foot

https://www.wirebarn.com/GXL-Wire-By-The-Foot_c_4.html · **cart $382.68, 8 lines** (the site showed "Hello, Guest" at review — sign in before checkout or the cart is lost)

| AWG | Colour | Feet | Used for |
|---|---|---|---|
| 14 | ORN | 250 | Every 15 A output run (O6–O11) and the washer feed — 190 ft calculated |
| 14 | RED | 100 | F1 head-unit constant, the capped window motor legs — 52 ft calculated |
| 14 | BLK | 50 | 14 AWG grounds — 42 ft calculated |
| 12 | RED | 250 + 100 | Every 25 A output and 12 AWG feed — 336 ft calculated |
| 12 | BLK | 25 | 12 AWG grounds — 20 ft calculated |
| 10 | BLK | 25 | Ground-bus and star-stud drops |
| 10 | RED | 25 | Busbar → block A, K11, block B |

**To add at WireBarn** (the three 16 AWG colours Waytek does not stock as spools):

| AWG | Colour | Feet | Used for | Status |
|---|---|---|---|---|
| 16 | PNK | 25 | F3 switch supply and the +5 V reference — 10 ft calculated | **to add** |
| 16 | YEL | 50 | CAN high, both buses — 33 ft calculated | **to add** |
| 16 | GRN | 50 | CAN low, both buses — 33 ft calculated | **to add** |

Calculated lengths carry a 1.5× margin because the routes are measured after the order lands (install plan M-2).

---

## 3 · DeutschConnector.com — every Deutsch part, genuine

https://www.deutschconnector.com/ · **cart $944.08, 26 lines, 188 pieces**

Assembly kits = housing + wedgelock + solid nickel contacts for every cavity. Order the **solid** (`-16141` / `-12141`) contact versions, never stamped.

### Housings — one plug (S, leg side) + one receptacle (P, dash-node side) per code

| Kit | Qty | Housings served |
|---|---|---|
| 12SA-201-16141 · DT06-12S plug kit | 7 | L1-S1 · L1-S2 · L3-S1 · L3-S2 · L4-M · DP-CLU · DP-ICU |
| 12PA-202-16141 · DT04-12P receptacle kit | 7 | same seven |
| 8SA-201-16141 · DT06-8S plug kit | 5 | L2-M · L3-S3 · L4-S · D1 · D2 |
| 8PA-202-16141 · DT04-8P receptacle kit | 5 | same five |
| 6SA-201-16141 · DT06-6S plug kit | 2 | L2-S · DP-DCU |
| 6PA-202-16141 · DT04-6P receptacle kit | 2 | same two |
| 4SA-201-16141 · DT06-4S plug kit | 2 | DP-DIAG · DP-KEY |
| 4PA-202-16141 · DT04-4P receptacle kit | 2 | same two |
| 2SA-201-16141 · DT06-2S plug kit | 1 | L3-M |
| 2PA-202-16141 · DT04-2P receptacle kit | 1 | L3-M |
| P4S-203-12141 · DTP06-4S plug kit | 3 | L1-P · L2-P · L4-P |
| P4P-204-12141 · DTP04-4P receptacle kit | 3 | same three |
| P2S-203-12141 · DTP06-2S plug kit | 1 | L3-P |
| P2P-204-12141 · DTP04-2P receptacle kit | 1 | L3-P |

No spare housing pairs are carted. A ruined housing is a one-week wait — keep the contacts spare instead (below) and never force a wedgelock.

### Contacts, plugs, clips, caps, tools

| Part | Item | Qty in cart | Design needs | Status |
|---|---|---|---|---|
| 0462-201-16141 | Socket contact, size 16, 16–18 AWG, solid | 16 | spares (kits cover the cavities) | cart |
| 0460-202-16141 | Pin contact, size 16, 16–18 AWG, solid | 16 | spares | cart |
| 0462-209-16141 | Socket contact, size 16, **14 AWG**, solid | 7 | **14 + spares = 18** (L2-M 1–4, L3-M 1–2, L4-M 1–4, D1 1–2, D2 1–2 — the kits' contacts do not take 14 AWG) | **raise to 18** |
| 0460-215-16141 | Pin contact, size 16, **14 AWG**, solid | 7 | **18** | **raise to 18** |
| 0462-203-12141 | Socket contact, size 12, solid | 5 | spares | cart |
| 0460-204-12141 | Pin contact, size 12, solid | 5 | spares | cart |
| 114017 | Sealing plug, size 16 cavity | 64 | 58 — every PLUG cavity, both halves (engine 20 + spare cavities 38) + 6 spare | cart |
| 0413-204-2005 | Sealing plug, size 12 cavity | 0 | 2 — L1-P cavity 4, both halves | **to add** |
| 1027-003-1200 | Mounting clip, DT / DTP receptacle | 22 | 21 — every receptacle at the dash node (19) and the sill (2) + 1 spare | cart |
| 0411-310-1605 | Contact removal tool, size 16 | 1 | toolbox | cart |
| 114010 | Contact removal tool, size 16 (plastic) | 1 | lives in the car | cart |
| 0411-310-1205 | Contact removal tool, size 12 | 0 | 1 — the DTP housings | **to add** |
| DT12P-DC | Dust cap, DT 12-way receptacle | 1 | DP-ICU | cart |
| DT6P-DC | Dust cap, DT 6-way receptacle | 1 | DP-DCU | cart |
| DT4P-DC | Dust cap, DT 4-way receptacle | 0 | 1 — DP-KEY (the site's bot check blocked the add) | **to add — click it yourself** |

---

## 4 · Amazon — backbone, cable, tools, consumables, electronics, switches

https://www.amazon.com/ · **cart $1,096.22, 49 lines / 55 items**. The cart was cleaned on 2026-09-02: everything below is in it or in *Saved for later*, and nothing else is. Unit prices here are estimates; the cart is the figure.

### Tools

| Item | Spec | Qty | ≈ $ | Note |
|---|---|---|---|---|
| Hydraulic lug crimper, 8 AWG – 1/0, with dies | TEMCo TH0006 class | 1 | 60 | Every 2 AWG / 1/0 / 6 AWG lug |
| Deutsch solid-contact 4-indent crimper, sizes 12 / 16 | IWISS solid-contact Deutsch crimper | 1 | 139 | Accepted only after the pull-test coupons pass (install §1.2) |
| Open-barrel ratchet crimper, 1.5 mm and 2.8 mm dies | Astro 9477 class | 1 | 80 | The PMU's SICMA terminals — check the die on one spare terminal first |
| Digital hanging scale 0–50 kg | any | 1 | 18 | Crimp pull tests |
| **Label printer** | **Brother PT-D220** (B0B1L3BL1G) | 1 | 40 | Prints the TZe-FX231 tape |
| Heat gun, 1500 W, two temperatures | any | 1 | 30 | |
| Wire strippers 10–22 AWG, flush cutters, needle-nose | Klein / Knipex class | 1 set | 70 | |
| Soldering iron + solder | Pinecil / Hakko class | 1 | 45 | Ladder resistors and diodes |
| Digital multimeter — ohms, DC volts, continuity beeper | any auto-ranging | 1 | 30 | The UT210E does current; a plain meter is faster for continuity |
| Torque wrench 1/4 in drive, 2–20 N·m | any | 1 | 40 | Battery lugs, busbar studs, PMU stud |

### Power backbone and battery

| Item | Spec | Qty | ≈ $ | Note |
|---|---|---|---|---|
| Class-T fuse block with cover, 110–200 A | Blue Sea 5007100 | 1 | 78 | The only fuse type with the interrupt rating for a lithium short |
| Class-T fuse 150 A | Blue Sea 5114 | 2 | 90 | One fitted, one spare |
| Master battery disconnect switch | Blue Sea 9003e (m-Series) | 1 | 62 | |
| Distribution post, 3/8 in stud, insulated | Blue Sea 2003 PowerPost | 1 | 16 | The temporary feed point in install §2; the factory harness feed lands here |
| MRBF terminal fuse holder | Blue Sea 5191 | 1 | 25 | On the battery + post |
| MRBF fuse 200 A | Blue Sea 5187 | 1 | 17 | |
| MIDI / AMI fuse holder, sealed, bolt-down | Blue Sea 5006 class | 2 | 28 | F17, F18 beside the starter B+ stud |
| MIDI fuse 30 A | Blue Sea 5253 class | 2 | 10 | F17, one spare |
| MIDI fuse 100 A | Blue Sea 5258 class | 2 | 10 | F18, one spare |
| Battery box, Snap-Top, Group 27–31 | NOCO BG27 | 1 | 20 | Confirm the Ionic S9 case + boots fit inside before fixing it down |
| Battery hold-down clamp + J-hooks, M8 grade-8 hardware, nyloc, fender washers | generic | 1 set | 40 | The backing-plate stock is §7 |
| Ground studs 3/8 in stainless | generic | 4 | 16 | Rear, front, dash, sill |
| Star washers, stainless, assorted | generic kit | 1 | 8 | Under every ground stud and lug |
| PMU stand-offs M6 × 12 mm, aluminium | generic | 3 | 5 | Airflow under the PMU |
| 2 AWG fine-strand welding cable RED | TEMCo, 25 ft + 20 ft | 45 ft | 213 | PMU feed through the tunnel, starter run, disconnect links |
| 2 AWG fine-strand welding cable BLACK | TEMCo, 25 ft | 25 ft | 72 | Battery negative, engine strap |
| 6 AWG cable RED, 5 ft | any SGX / welding | 1 | 15 | Alternator B+ |
| Tinned closed-barrel lugs 2 AWG, 5/16 and 3/8 holes | TEMCo / Selterm | 18 | 45 | Every 2 AWG cable end + practice crimps |
| Tinned lugs 6 AWG 5/16 (×4) and 1/0 3/8 (×4) | TEMCo / Selterm | 8 | 16 | |
| Terminal boots, red and black, 2 AWG / 1/0 | generic | 10 | 15 | |
| LiFePO4-profile charger 12 V 10 A — OPTIONAL | Ionic 12V 10A | 1 | 110 | A lead-acid charger can ruin the Ionic; skip if one is owned |

### Dash node and electronics

| Item | Spec | Qty | ≈ $ | Note |
|---|---|---|---|---|
| Barrier terminal strip, 8 position, 12 V rated | generic | 2 | 15 | Wake strip + one spare |
| Metal-film resistor kit, E24 1 %, 1/4 W | generic kit | 1 | 15 | Values used: 1.8k 3.3k 4.7k 6.8k 8.2k 10k 12k 15k 18k 33k 47k 100k 1M |
| 120 Ω 1 % 1/4 W resistors | generic | 10 | 1 | CAN terminators, 2 used |
| Schottky diode 1N5819 | 1N5819 | 20 | 3 | 5 wake strip + 1 WASH leg + spares |
| NPN transistor 2N3904 | 2N3904 | 10 | 1 | 2 wake sense stages + spares |
| Inline ATC fuse holder, 2-pack | generic | 1 | 6 | The 5 A first-power-up guard (install §5.2) |
| Shielded cable, 16–18 AWG single core with drain, 15 ft | any automotive shielded | 1 | 15 | Tach — L1-S1 6 → DP-CLU 4 |

### Consumables and labels

| Item | Spec | Qty | ≈ $ | Note |
|---|---|---|---|---|
| **Label tape** | **Brother TZe-FX231** flexible-ID, 12 mm black on white (B00X8GRTO8) | 3 | 45 | ≈ 260 wire ends at 45 mm each — three cartridges is the whole car plus mistakes |
| **Clear heat-shrink 3/16 in, 2:1** | generic | 3 | 20 | Over every label on the engine leg and under loom |
| Adhesive-lined heat-shrink assortment 3:1, incl. heavy-wall for lugs | generic | 1 kit | 40 | |
| Heat-shrink crimp butt splices — 22–18 (×50), 16–14 (×50), 12–10 (×25) | generic, tinned | 1 set | 25 | Every factory-pigtail joint (install §4) |
| Ring terminals, heat-shrink, assorted 16–14 and 12–10, #10 and 3/8 | generic | 1 kit | 20 | Ground rings and stud connections |
| Tesa 51608 cloth harness tape | Tesa 51608 | 5 rolls | 33 | |
| Split loom / braided sleeve assortment, grommet kit, P-clips, pull string 100 ft | generic | 1 set | 110 | |
| Cavity wax / corrosion inhibitor spray, paint pen | generic | 1 set | 20 | |

### Switches

| Item | Spec | Qty | ≈ $ | Note |
|---|---|---|---|---|
| **Momentary pushbutton, 1NO + 1NC, 2-pack** | **DMWD** (B09H29SZYS) | 1 pk | 12 | Wink L and wink R. MUST be changeover (NO + NC) — the NC pole is wired |
| Adjustable plunger pin switch, 6-pack | generic | 1 pk | 15 | Door jambs ×2, glove box, luggage + 2 spare |

**Not on Amazon any more, on purpose:** blade fuses (§9), aluminium sheet (§7).

---

## 5 · Nothing from Ballenger

The old list bought spare SICMA terminals here. The two spare housings in hand carry 54 small and 32 large terminals — more than enough spares. No order.

## 6 · Vehicle parts — not yet carted

RockAuto / PartsGeek / a Mazda specialist. Confirm fit for a **1982 RX-7 GS, FB, 12A, automatic** and keep the receipt.

| Item | Spec | Qty | ≈ $ | Note |
|---|---|---|---|---|
| Brake pedal (stop lamp) switch, without cruise | Standard SLS-52 class — confirm fit | 1 | 20 | F-11 — the pedal switch is wired into the A3 ladder |
| Ignition switch, electrical portion, 1981–83 RX-7 | search "81-83 RX-7 ignition switch electrical"; NOS or quality reproduction | 1 | 45 | Terminals B, ACC, IG, ST — feeds the A16 ladder and both wake sources |
| Heater blower motor, 1979–83 RX-7 | Four Seasons 35483 | 1 | 65 | The original is dead (K-023). Confirm fit against the HVAC case on arrival |
| Blower motor resistor pack, 1979–85 RX-7 | Four Seasons, vehicle fit | 1 | 25 | |
| Blower speed switch, 4-position rotary, 20 A, ground-side | OEM-type replacement | 1 | 20 | |

## 7 · Hardware store — after the measurement day

Bought with the parts in hand, once M-1 and M-4 in the install plan are filled in. Not before.

| Item | Note |
|---|---|
| Carrier-panel stock for the dash node — 3 mm aluminium or ABS sheet, one or several small pieces | Sizes from M-1 and the bench layout (install §3.1) |
| Sill-node panel stock, about 150 × 100 mm | M-5 |
| Battery backing plate stock, 3–4 mm aluminium or steel, sized from the M-4 mock-up | Under the floor, beneath the battery box |
| Paint or powder-coat for any aluminium panel | Never bare aluminium against a live stud |

## 8 · Still to add — the gap between the design and the carts

| Store | Item | Qty | Why |
|---|---|---|---|
| Waytek or Amazon | **Blue Sea 2300 — 10-gang 150 A busbar WITH cover** | 1 | The always-hot bar. The 2301 in the Waytek cart becomes the ground bus |
| WireBarn | 16 AWG GXL PNK 25 ft · YEL 50 ft · GRN 50 ft | 3 lines | §2 |
| DeutschConnector | 0462-209-16141 and 0460-215-16141 → 18 each | +11 each | 14 AWG contacts — §3 |
| DeutschConnector | 0413-204-2005 size-12 sealing plug | 2 | L1-P cavity 4 |
| DeutschConnector | 0411-310-1205 size-12 removal tool | 1 | |
| DeutschConnector | DT4P-DC dust cap | 1 | DP-KEY — add by hand; the scripted add was blocked |
| Drawer or local | Blade fuses by value — §9 | | |

## 9 · Blade fuses — check the drawer first

Cheap assortments skip 2 A, 3 A and 7.5 A. What the car needs, with one spare of each:

| Value | Positions | Qty |
|---|---|---|
| 2 A | F2 | 2 |
| 3 A | F19 | 2 |
| 5 A | F3, F12, F16 + the first-power-up guard | 5 |
| 7.5 A | F15 | 2 |
| 15 A | F1 | 2 |
| 30 A | F5 | 2 |

Plus the two MIDI fuses (F17 30 A, F18 100 A) and the Class-T and MRBF, which are on Amazon above.

## 10 · When it arrives

Count everything against this list before anything is opened. Housings: 21 codes, two halves each (§3). Wire: four spools + the WireBarn cuts + the three added 16 AWG colours. Contacts: 18 of each 14 AWG type, 16 of each 16–18 AWG type, 5 of each size 12, 64 size-16 plugs, 2 size-12 plugs, 22 clips, 3 dust caps. Report any shortfall before the build starts — a missing housing stops a leg.

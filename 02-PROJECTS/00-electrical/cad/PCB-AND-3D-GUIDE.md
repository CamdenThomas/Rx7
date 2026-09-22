# PCB and 3D model — the ICU carrier and the DCU carrier, step by step

*Rev 2026-09-21 · owns: the method for taking each carrier from schematic to a laid-out,
3D-checked KiCad board. Camden asked for it on 2026-09-21 (D-361). It sits inside the `cad/`
fence (`README.md`): it is a how-to for a drawing, and the record stays the design.*

**Read this first, because it decides what "perfect to the design" can mean.**

- **The record is the design.** `data/icu_channels.csv` (ICU) and `01-luxury/data/sensors.csv`,
  `modules.csv` and `parts.csv` (DCU) say what each board does. Every value in this guide
  names the row it came from. **If this guide and a row disagree, the row is right.** Re-read
  the row, don't trust the copy here. A fact the board settles, like a Teensy pin number, gets
  **promoted into the row**. It is never kept only in KiCad (`README.md`: "promoted, not linked").
- **A 3D model is only as true as the numbers put into it.** Nobody has measured a single
  part, cavity or clearance in this tree (R11). A board that passes DRC and a STEP file that
  looks right are *internally consistent*. They are not proven to fit. Every step below that
  needs a physical number says **MEASURE**: calipers on the actual part in your hand, never the
  datasheet alone and never this guide. The finished model is "factual" when every
  **MEASURE** in it has been done and written down. Until then it's a good drawing.
- **Laying out is free. Ordering boards is not.** Layout is bench time and reverses by editing
  the file. Ordering from JLCPCB or OSH Park is money with a lead time, and it is already
  your step: F2 for the ICU, luxury `LP07` for the DCU. Nothing here orders anything.
- **Menu names are KiCad 8/9 names, checked against KiCad 10 on first use.** KiCad 10.0.6 is
  on the laptop (`icu-carrier/README.md`), and it isn't installed on `crashs-pc`, so none of
  the menus or `kicad-cli` flags below were tested on this machine. Step 0.2 checks them.

---

## Part 0 · Once, for both boards

### 0.1 Pull and open

```
git pull
python tools/rx7.py status
```

Work on the laptop: KiCad 10.0.6 is installed at `C:\Program Files\KiCad\10.0`.

### 0.2 Confirm the tool matches this guide

```
"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" version
kicad-cli pcb --help
kicad-cli pcb drc --help
kicad-cli pcb export step --help
kicad-cli pcb render --help
```

The guide uses `pcb drc`, `pcb export step`, `pcb export gerbers`, `pcb export drill`,
`pcb export pos` and `pcb render`. If a flag named below is missing in `--help`, use the one
`--help` lists and fix this file in the same commit.

### 0.3 Keep every library inside the project

The ICU schematic already does this for symbols (`icu-carrier.kicad_sym` + `sym-lib-table`,
`CONVENTIONS.md §7`). Do the same for footprints and 3D models, so the board opens the same on
both machines and a KiCad upgrade can't quietly change a pad:

```
cad/<board>/
  <board>.pretty/          every footprint the board uses (copied or drawn here)
  fp-lib-table             points at <board>.pretty with ${KIPRJMOD}
  3d/                      every .step / .wrl model the footprints reference
```

In each footprint's **3D Models** tab, reference the model as
`${KIPRJMOD}/3d/<file>.step`, never an absolute path and never `${KICAD9_3DMODEL_DIR}`.

### 0.4 What gets committed

Commit `.kicad_pcb`, `.kicad_pro`, `.kicad_sch`, `.kicad_sym`, `fp-lib-table`,
`sym-lib-table`, `<board>.pretty/`, `3d/`, the **SVG of the schematic**, and one **PNG render
of each board side** (step 9). An S-expression diff can't be reviewed, and a picture can. The
repo `.gitignore` already drops `*.kicad_prl` and the backups. Add `*-drc.rpt`, `*.step` at the
board root (it is regenerated) and `fab/` (Gerbers are regenerated too).

---

## Part A · The ICU carrier, H-001

The schematic exists: `icu-carrier/icu-carrier.kicad_sch`, rev 0.02, ERC 0/0. The board
doesn't. Layout is F2 ("lay out carrier H-001 around the DT13 headers and order it"), and F1,
the enclosure, waits on the board outline this part produces.

### A0 · Before the first footprint: what must be true

Tick each one off. Every one is either a row in the record or something to measure.

| # | What | Where it stands | Why layout needs it |
|---|---|---|---|
| 1 | **BT817 eval board ordered** (P117) | F2 says order it *before* layout | the display header's pinout and mounting come off the real board |
| 2 | **Parts in hand to measure**: both DT13 receptacles (P122), a Teensy 4.1 (luxury LP01, in hand), the XIAO ESP32C3, the IMU module (P109), the buck | P122/P109 are `later` | footprints come from calipers, not drawings (R11) |
| 3 | **The space behind the binnacle** — length, width, depth available for the enclosure | not measured; the aperture is sized at M-1 (F3) | the board outline is the enclosure's inside minus its wall; F1 is drawn from it |
| 4 | **IMU orientation** | ruled in D-265: component side up, long edge across the car, connector edge toward the driver's door | fixes where U-IMU sits and which way it faces |
| 5 | **The display bus: SPI0 or SPI1?** | ⚠ **disagreement.** `icu_channels` IC21 says "SPI1 / QSPI pins". The firmware (`01-luxury/firmware/icu/bt817.h`) uses `BT817_PIN_CS 10` and `PDN 9`, and pin 10 is SPI0's CS | settle it at A2. The record row wins, so the firmware or the row changes in the same commit |
| 6 | **Teensy pin assignment** | the record assigns **none**. The `teensy_pin` column says "ADC", "digital, input capture", "CAN1 (FlexCAN)" | done at A2 and written into `icu_channels.teensy_pin` |
| 7 | **IC07 pull-up value** | Q-308, no oil-temp sender chosen: footprint only, J7 not fitted | lay out the footprint and leave it empty |

### A1 · Freeze the schematic against the record

1. `python tools/rx7.py sql 02-PROJECTS/00-electrical "select id, at_the_drop, carrier_stage, teensy_pin from icu_channels"`.
2. Walk `TARGET.md` §1–5 against that output, row by row. `TARGET.md` is a snapshot from
   2026-09-12, so the query wins if they differ.
3. Two things the record has changed since rev 0.02, to check on the sheet:
   - **No gauge drives.** D-268 removed IC17–IC20. D-265's layout brief still says "the gauge
     drives … leave on the other [edge]". That half of D-265 is moot, so nothing leaves the
     board except the display ribbon and the page button (D-270).
   - **Two connectors on one face** (D-270): `DP-ICU-A` (DT13-06PA) and `DP-ICU-B`
     (DT13-12PA) sit side by side on the connector face. The ribbon and the page-button lead
     leave through grommets in the **opposite** face.
4. Run ERC and the two netlist asserts (`CONVENTIONS.md §3, §5`). Zero errors and zero
   warnings before you go on.

### A2 · Assign the Teensy pins, and put them in the record

The sheet deliberately draws the Teensy as a socket, `J5`, with ordinal pin numbers
(`CONVENTIONS.md §2.9`). Layout needs real ones.

1. Open **PJRC's own pinout card for the Teensy 4.1** (pjrc.com, "Teensy 4.1 pinout"). Take every
   pin capability from that card, not from memory or this guide.
2. Assign by constraint, hardest first:
   - **CAN**: IC16 uses FlexCAN "CAN1" (`icu_channels`). Take the pins the card marks CAN1 TX/RX.
   - **Input capture**: IC04 (tach) and IC08 (road speed) need pins the card and the
     FreqMeasure / FreqMeasureMulti library documentation both list. Check the library's
     supported-pin list against the card. They must not collide with CAN1.
   - **Display bus**: settle A0 #5 first, then take that port's CS/SCK/MOSI/MISO, plus PDN.
   - **ADC**: IC01, IC02, IC03, IC05, IC07, IC14 need analog-capable pins (the card's `A` numbers).
   - **Digital reads**: IC06, IC09, IC10, IC11, IC22.
   - **I²C**: IC23 on the card's SDA/SCL (Wire), plus one GPIO for the IMU interrupt.
   - **Radio**: IC24 on "Serial2 + 2 GPIO" (`icu_channels`). Take Serial2's pins from the card.
3. **Promote each one**:
   `python tools/rx7.py set 02-PROJECTS/00-electrical icu_channels IC04 "teensy_pin=<n> — input capture"`
   and so on for every row, then `check`. Now the sheet can follow the record.
4. On the sheet, replace `J5`'s ordinal numbers with the real ones. Set `J5` to two 1×24
   female headers (P110: standard 0.1 in female, **not** machined, because square pins damage
   machined sockets). ERC again.

### A3 · Footprints — one per symbol, each one checked against the part

Only **2** of the sheet's symbols have a footprint today (the SOT-23 and the DO-41). Assign all of
them in **Tools → Assign Footprints**. The rule for each one is the same:

> Pick the footprint → open the part's datasheet land pattern → **MEASURE** the part you're
> holding → only then accept it. If the part isn't in hand yet, use the datasheet footprint and
> set the footprint's `Description` field to `confirm — not measured`.

| Symbol (value on the sheet) | Package / footprint to start from | 3D model source | MEASURE |
|---|---|---|---|
| Teensy 4.1 socket (`J5`) | 2 × `PinSocket_1x24_P2.54mm_Vertical`, row spacing from PJRC's dimension drawing | KiCad stock socket models; a separate Teensy 4.1 body model from PJRC or the maker (confirm source) placed on top for the 3D check | row-to-row spacing and the board's overhang past the headers, on the Teensy in hand |
| DT13-06PA / DT13-12PA | **draw it**: no stock footprint. From TE Connectivity's drawing for the exact part numbers ordered under P122 | TE publishes 3D models on te.com for Deutsch DT parts: download the one matching the ordered suffix | flange hole pitch, pin pitch, pin length through the board, the flange's standoff from the PCB |
| TCAN1042HVDRQ1 | `SOIC-8_3.9x4.9mm_P1.27mm` (the "D" package) | KiCad stock | — (standard package, but check the suffix on the reel) |
| LMR36015-Q1 class | from TI's datasheet for the exact package ordered (TI offers several). **Use the datasheet's recommended layout, not a generic one** | TI / Ultra Librarian | inductor footprint to the chosen inductor |
| SMBJ33A | `D_SMB` | KiCad stock | — |
| SS34 | `D_SMA` (or the package actually bought) | KiCad stock | package on the reel |
| BAT54S | `SOT-23` (already assigned once) | KiCad stock | — |
| LM393 / LM2903 | `SOIC-8` | KiCad stock | — |
| 74LVC1G17 | `SOT-23-5` (or SC-70-5: check what's ordered) | KiCad stock | package |
| MMBT3904 | `SOT-23` | KiCad stock | — |
| SQD50P06 class | `TO-252-2` (DPAK) | KiCad stock | — |
| VN5E class (DNP alternative) | per the chosen VN5E package | ST | — |
| 100 Ω 1 W, 100 kΩ ½ W | through-hole or 2512, **by wattage in the value field** (`CONVENTIONS.md §2.5`) | KiCad stock | body length |
| 10k / 15k / 47k / 4.7k / 100 nF | one size for all, e.g. `0805`. Pick once, write it in `CONVENTIONS.md` | KiCad stock | — |
| XIAO ESP32C3 | Seeed's published footprint (castellated or through-hole: pick one) | Seeed publishes KiCad models | module outline and **antenna position**: it has to face the RF window (D-270) |
| IMU (LSM6DSO / ICM-42688-P module, P109) | the breakout board actually bought, as a module footprint | the breakout vendor's model | breakout outline, pin pitch, mounting holes |
| BT817 header (IC21) | the header the P117 eval board expects: its pin count and pitch come **off the board** | the header's model | pitch and keying on the real eval board |
| Jumpers J1, J3, J7, J8A/B | `PinHeader_1x02` / `1x03` 2.54 mm | KiCad stock | — |
| Fuse (4 A, IC13) | the holder or SMD fuse chosen | KiCad stock | — |
| `L_Coupled` (DNP CM choke) | footprint for a choke you could fit later (D-079 → D-346: DNP) | KiCad stock | — |
| Page button (IC22) | a 2-pin header or JST to the button on the binnacle plate (luxury D-169) | stock | — |

Every DNP part keeps its footprint, and its reason stays in its field (`CONVENTIONS.md §2.7`).

### A4 · Board setup: stackup, rules, net classes

**File → Board Setup**:

- **Stackup**: 2 layers (P103), 1.6 mm FR-4, 1 oz (35 µm) copper both sides. These are the
  default cheap-fab values, so check the fab's page before ordering.
- **Design rules**: set the fab's minimums (track/space, drill, annular ring) from the chosen
  fab's capabilities page. Stay well above them: 0.2 mm track/space is a comfortable floor.
- **Net classes**: set track width from current. IPC-2221 outer-layer formula, 1 oz copper,
  10 °C rise (arithmetic, not a lookup):
  `A[mil²] = (I / (0.048 · ΔT^0.44))^(1/0.725)`, width = A / 1.378 mil.

  | Current | Width, 10 °C rise | Used for |
  |---|---|---|
  | 0.5 A | 0.12 mm → use **0.25 mm** | signal default |
  | 1.0 A | 0.30 mm | |
  | 1.5 A | 0.53 mm → use **0.6 mm** | `+12V_LOGIC`, `+5V` (~0.8 A peak, IC12) |
  | 4.0 A | **2.03 mm** → use **2.2 mm** or a pour | `+12V_BL`, `+12V_BL_SW` (~2.5 A, 4 A fuse, IC13, D-273): **size to the fuse, not the load** |

  Net classes: `Default` 0.25 mm · `PWR_LOGIC` 0.6 mm (`+12V_LOGIC`, `+5V`) · `PWR_BL` 2.2 mm
  (`+12V_BL`, `+12V_BL_SW`) · `TACH_HV`, the IC04 input from `DP-ICU-B 4` up to and including
  the two 100 kΩ resistors.

- **Clearance for `TACH_HV`**: the trailing coil's negative primary is "hundreds of volts of
  inductive kick" (IC04). Before the 100 kΩ resistors, that net needs clearance for the voltage,
  not the logic. For 301–500 V on uncoated outer layers, IPC-2221 table B2 gives **2.5 mm**.
  **Check that figure against the table itself before relying on it.** The kick voltage is
  unmeasured (T-017 / tach_simulator is the bench step), so use the 301–500 V row until a
  scope says otherwise. Set it as a netclass clearance, or a custom rule:
  `(rule tach_hv (constraint clearance (min 2.5mm)) (condition "A.NetClass == 'TACH_HV'"))`.

### A5 · The outline and the mechanical frame, before any placement

1. **The envelope**: A0 #3 (space behind the binnacle) minus the enclosure wall and a fit
   gap. The wall material is ASA or PETG, never PLA (D-270, P111). Wall thickness is F1's
   choice, so agree it with F1 before fixing the outline. Draw the outline on `Edge.Cuts`.
2. **The connector face**: both DT13s on **one edge**, flanges proud of the board edge by exactly
   the amount the enclosure wall needs (D-270: sealed through one face, flange gasket, printed
   bosses). **MEASURE** the flange-to-PCB standoff on the part in hand.
3. **The opposite face**: the display ribbon (IC21) and the page-button lead (IC22) leave
   through grommets there (D-270). Put their headers along that edge.
4. **The RF edge**: the XIAO's antenna end at a board edge, facing the enclosure's
   RF-transparent window (D-270). Keep copper, pours and tall parts out from under and around
   the antenna. Use the module maker's keep-out drawing, entered as a **rule area** (no copper,
   both layers).
5. **Mounting**: holes for the enclosure's bosses. Their position is F1's to agree, but place
   them now so F1 has something to design to (M3, with no copper within the screw head's radius).
6. **The IMU**: D-265's orientation (A0 #4). Place it away from the connectors' flex under a
   harness tug and away from the buck's inductor.

### A6 · Placement, in this order

Power sets the ground current paths, and everything else has to live with them.

1. **Power, at the connector.** Each 12 V input, `DP-ICU-A 1` (logic) and `DP-ICU-A 6`
   (backlight), gets its **SS34 → SMBJ33A** right at its pin, before anything else touches the
   net. Then the LMR36015 buck with its input capacitors, inductor and feedback divider **tight
   to the IC, as the datasheet layout shows**. Then the 4 A fuse and the high-side switch
   (SQD50P06 class) on the backlight path. **The two 12 V inputs never share a pad, a pour or
   a via** (`CONVENTIONS.md §2.3`, D-273).
2. **CAN**: TCAN1042HVDRQ1 close to `DP-ICU-A 4/5`, with the DNP choke footprint between them.
   **No termination on this board** (D-079 → D-346).
3. **Analog row along the connector edge**: one repeated cell per channel, laid out once and
   copied (**Place → Create/Apply Layout from Multi-Channel**, if KiCad 10 has it for this case;
   otherwise copy-paste and align). Each cell is divider → 100 nF → BAT54S, with the clamp
   **closest to the Teensy pin** so the clamp protects the pin, not the resistor.
   **BAT54S: pin A to GND, pin K to +3V3, every one** (`CONVENTIONS.md §2.10`: rev 0.01 had
   all of them backwards).
4. **Pulse inputs**: IC04's two 100 kΩ ½ W resistors, 5.1 V zener, BAT54S and the LM393 **on
   `+5V`** (§2.4). Keep the `TACH_HV` copper short and away from everything else. IC08's jumper
   block and Schmitt (74LVC1G17).
5. **The Teensy socket (`J5`)** in the middle, USB end reachable through the enclosure if you
   want to flash in place (F1's choice). Nothing tall under the Teensy's overhang: **MEASURE**
   the Teensy's underside clearance on the socket, because the PSRAM is soldered underneath
   (TARGET.md §5).
6. **XIAO** at the RF edge (A5.4), **IMU** per A5.6, **BT817 header** and **page-button header**
   on the grommet face.

### A7 · Routing

1. **Ground**: one pour on the bottom layer, tied at `DP-ICU-A 3` (IC15: "single pour,
   star-tied here"). Keep the buck's switching loop (input cap → IC → inductor → output cap)
   on the top layer and small. Put no analog trace under the inductor or the switch node.
2. **Power** at net-class width. Short, fat returns for the backlight path.
3. **Analog**: route away from the buck switch node and the backlight path. Vias to the ground
   pour next to each 100 nF.
4. **CAN**: CANH/CANL as a pair, same length, side by side, to the connector.
5. **Display bus**: short, and match lengths roughly on the QSPI/SPI lines to the BT817 header.
6. **Stitching vias** along the board edge and around the RF keep-out's border (outside it).
7. **Fill zones** (**Edit → Fill All Zones**, `B`).

### A8 · DRC to zero

```
kicad-cli pcb drc --severity-all --exit-code-violations -o icu-carrier-drc.rpt icu-carrier.kicad_pcb
```

Same standing as ERC and as `rx7.py check`: an error is an error. Also run DRC's
**schematic parity** (in the DRC dialog, "Test for parity between PCB and schematic"), which
catches a footprint that doesn't match its symbol. Zero errors and zero warnings, with nothing
excluded unless the exclusion comment says why.

### A9 · The 3D model — make it true, then prove it

1. **Every footprint has a model.** Open the 3D viewer (**View → 3D Viewer**, `Alt+3`). A part
   with no model shows as bare pads on the board. Go round the board until none are left. A
   missing model is a part the enclosure check can't see, and a board that "fits" with a
   missing capacitor doesn't fit.
2. **Every model sits where the part sits.** For each footprint, open **3D Models** and check
   offset, rotation and scale. Pin 1 of the model must land on pad 1. For the parts you
   **MEASURE**d (DT13s, Teensy, XIAO, IMU, BT817 header), overlay the caliper numbers: body
   height above the PCB and overhang past the pads. A model downloaded for a different suffix
   is a wrong model.
3. **Render both sides for the repo**:
   `kicad-cli pcb render --side top -o icu-carrier-top.png icu-carrier.kicad_pcb` (and `--side bottom`).
4. **Export the STEP**:
   `kicad-cli pcb export step --subst-models -o icu-carrier.step icu-carrier.kicad_pcb`
   (confirm the flags against `--help`, step 0.2).
5. **The fit test.** Open the STEP in FreeCAD. That's where F1, the enclosure, gets drawn around
   it: bosses under the mounting holes, the two DT13 cut-outs matched to the flanges with the
   gasket groove, grommets on the opposite face, the RF window in front of the antenna. Check:
   - **interference**: no solid of the board touches the enclosure (FreeCAD's Part → Check
     Geometry / an intersection of the two bodies must be empty)
   - **the harness side**: the DT06 plugs on their 150 mm tails (D-270) have room to mate and
     to bend without the enclosure fouling their latch
   - **the Teensy comes out**: the socketed Teensy lifts clear without removing the board
   - **the envelope**: the whole assembly fits the space measured at A0 #3, with room for the
     tails to leave

   If anything fails, fix the board or the enclosure and re-export. Don't nudge the model.
6. **Print one enclosure and test-fit the bare board** before anything is soldered. That's the
   cheapest true test of the 3D model there is.

### A10 · The last checks, then F2 is yours

1. The two netlist asserts from `CONVENTIONS.md §5`, re-run on the board's netlist.
2. **Parity with the record**: every `DP-ICU-A` / `DP-ICU-B` pin on the board is a cavity row
   in `data/cavities.csv` (`rx7.py sql 02-PROJECTS/00-electrical "select * from cavities where housing like 'DP-ICU%'"`),
   and no pin exists in one and not the other.
3. Fab outputs (Gerbers, drill, pick-and-place) come from `kicad-cli pcb export gerbers /
   drill / pos` into `fab/`. They are regenerated, never committed.
4. **Ordering is F2, your step.** Two boards (P103). Nothing in this guide orders anything.

---

## Part B · The DCU carrier, H-002

The DCU is the **luxury package's** board. Its spec is `01-luxury/data/sensors.csv`
(SN11–SN17), `modules.csv` (DCU, PANEL) and `parts.csv` (LP06–LP14). It has **no schematic
yet**, and it waits on more than the ICU did. Its layout item is luxury `H-002`, gated on
`V-083 D-359 W-332 D-360`.

### B0 · Before the first symbol: what must be true

| # | What | Where it stands |
|---|---|---|
| 1 | **The parts check, luxury `V-083`** | open, agent work: datasheet-verify the DCU's parts. The same D-273 findings apply (60 V bucks, not the LMR33630) |
| 2 | **The mirrors' currents, `W-332`** | open, yours: motor stall current and clutch coil current size SN17's four drivers (D-360) |
| 3 | **How the DCU plugs into the harness** | **ruled, luxury D-362 (like the ICU).** Three DT13 receptacles in a printed enclosure wall: `DP-DCU` DT13-06PA (power, OAT, CAN, wake), `DP-DCU-B` DT13-12PA (window commands `L3-S2 3–6`, mirror lines `L3-S3 5–8`, spares 9–12), and a comfort-return receptacle sized after `V-101` (`LP46`). Servos, blower, cabin sensor and the panel ribbon leave through grommets |
| 4 | **How the DCU drives the four window commands** | **settled, electrical D-363:** the command lands on K5–K8's terminal 86, 85 is grounded at the sill, so the DCU needs **four high-side outputs** sourcing 12 V into the coils (luxury `sensors` SN22). Up and down on one side are interlocked in firmware |
| 5 | **The comfort loads' currents** | **not in the record: luxury `V-101`.** SN16's five low-side FETs and SN13's 5 mΩ shunt carry the seat heat and cool and mirror-heat return current *through the carrier*. Their track widths come from those currents |
| 6 | **The panel ribbon** | PANEL is a concept: key matrix, rotary encoders and now the thumbstick (D-359) on a local ribbon (D-355). The ribbon's pin count and connector come from the panel design |
| 7 | **Teensy pin assignment** | none in the record, as for the ICU (A2). The DCU firmware (`01-luxury/firmware/dcu/`) is a skeleton and fixes no pins |

### B1 · Create the project

`cad/dcu-carrier/`, set up exactly like `icu-carrier/`: project-local `.kicad_sym`,
`sym-lib-table`, `.pretty`, `fp-lib-table`, `3d/`. Copy `CONVENTIONS.md` and change what differs.
Add a `README.md` saying what it may and may not claim (copy the ICU's), and a `TARGET.md` taken
from the query below. Add the row to `cad/README.md`'s table.

```
python tools/rx7.py sql 02-PROJECTS/01-luxury "select id, signal, source, front_end, pin, note from sensors"
python tools/rx7.py sql 02-PROJECTS/00-electrical "select id, circuit, src, lands_on from cavities where housing='DP-DCU' or id in ('L3-S2 3','L3-S2 4','L3-S2 5','L3-S2 6','L3-S3 5','L3-S3 6','L3-S3 7','L3-S3 8')"
```

### B2 · The schematic, block by block, from the record

Same conventions as the ICU: every power net carries its voltage domain, every analog input ends
in its clamp, values carry wattage, and no DNP or NC appears without a reason.

1. **Power.** `DP-DCU 1` is **constant** 12 V on F22 (luxury `modules` DCU, D-355: the panel has
   to work parked). SS34 → SMBJ33A → **two** LMR36015-Q1-class bucks (LP08, D-273): DCU logic
   5 V, and a separate 5 V servo rail (SN15: "own 5 V buck for the servo rail; 470 µF at the
   header"). `DP-DCU 3` ground. The comfort loads' power is O15 through the luxury fuse block
   (LP21), **not** through the DCU logic feed.
2. **CAN**: `DP-DCU 4/5` CAN2 → TCAN1042 (LP06: exact suffix per electrical V-057 → D-265).
   Termination only if the bus topology says this node is an end. The ICU's is none (D-346),
   so check the DCU's position on CAN2 before fitting anything.
3. **Wake**: `DP-DCU 6`, the DCU's wake request into the PMU's strip (WAKE 7). The drive
   polarity and part come from the PMU wake-strip design, so read that row first.
4. **Inputs**: SN11 cabin NTC (10 kΩ pull-up to 3V3, RC 10 kΩ / 100 nF); SN12 outside-air NTC
   on `DP-DCU 2` (same, plus BAT54S); SN13 INA180 across the 5 mΩ shunt; the **panel ribbon**:
   key matrix, encoders, and the **thumbstick** (two analog axes + push, D-359, LP35).
5. **Outputs**: SN14 blower PWM (≥ 20 kHz, 100 Ω series, 10 kΩ pull-down); SN15 servo PWM ×3
   (330 Ω, 470 µF at the header); **SN16 five** low-side AOD4184-class FETs: seat heat ×2, seat
   cool ×2, mirror heat (the nozzle and the de-icer are cancelled, D-329), each with 100 Ω gate
   and 10 kΩ pull-down, SS34 flyback footprints DNP; **SN17 mirror drive, four outputs** (D-360):
   three half-bridges (motor common, left motor, right motor) and **one** low-side driver for
   both clutch coils. Four high-side window-command outputs, SN22 (D-363).
6. **ERC to zero**, SVG exported and committed.

### B3 onwards: the same steps as the ICU

Follow A2 → A10 with these DCU differences:

- **A2 pins**: the CAN pins (Teensy CAN1 or CAN2, per the card), PWM-capable pins for SN14 and
  SN15 (the card marks them). The blower needs ≥ 20 kHz, so check the pin's timer can hold that
  frequency independently of the servo pins' 50 Hz. Analog pins for SN11–SN13 and the thumbstick
  axes. Promote each one into `sensors.pin`.
- **A3 footprints**: AOD4184 is `TO-252` (DPAK). INA180 is `SOT-23-5`. The half-bridges are
  whatever V-083 picks for W-332's current. Servo headers are `PinHeader_1x03`. The panel ribbon
  connector comes from B0 #6.
- **A4 net classes**: the comfort return through SN13's shunt and SN16's FETs is sized to
  **the comfort fuse block's fuses**, not a guess. That's the IPC table above at the fuse rating,
  and it's why B0 #5 has to be answered first. Above ~6 A, a pour beats a track (3.56 mm at 6 A,
  7.19 mm at 10 A, 1 oz, 10 °C rise). The shunt gets a **Kelvin** connection: two thin sense
  traces from the shunt's inner pad edges to the INA180, never tapped off the power track.
- **A5 outline**: "behind the centre stack, at the HVAC case" (modules DCU). The envelope is a
  measurement nobody has taken yet. Take it with the dash apart.
- **A6 placement**: power input → bucks → the high-current comfort section on its own corner
  with its return straight to the shunt and out → the servo headers at the edge the servos'
  leads arrive from → Teensy → panel ribbon on the face toward the panel ("inches behind it",
  D-355).
- **A9 3D**: the same proof: the enclosure (`LP47`) is drawn around the STEP with the three DT13 flanges in one wall, and the DT06 plug tails must have room to mate.

---

## What this guide does not decide

Every one of these is in the record as a block or a work row, and **none of them is answered by
drawing it**:

- ICU: the binnacle envelope (measure) · SPI0 vs SPI1 for the display (A0 #5) · Teensy pins
  (A2, promoted to `icu_channels`) · the tach kick voltage (bench) · IC07's pull-up (Q-308) ·
  V-084, the panel timing.
- DCU: `V-083` (parts) · `W-332` (mirror currents) ·
  `V-101` (comfort currents) · the panel ribbon · the DCU
  envelope (measure).

When one of them changes, the board follows the row, never the other way round.

# Your first board: the ICU carrier in KiCad, step by step

_Rev 2026-09-22 · written for a first-time KiCad user · KiCad 10.0.6 on the Fedora machine ·
owns: the method for taking the ICU carrier from schematic to a laid-out, 3D-checked board.
Every menu name below was checked against the KiCad installed here; hotkeys are KiCad's
defaults. It sits inside the `cad/` fence (`README.md`): a how-to for a drawing, never a view
of the record._

**Three rules, then you never need to think about them again:**

1. **The record is the design.** If this guide, the drawing and a row in `../../data/` disagree,
   the row wins: `python tools/rx7.py sql 02-PROJECTS/01-electrical "select * from icu_channels"`.
2. **A drawing is only a guess until you measure the part.** Anything you haven't put calipers
   on is marked `confirm - not measured`, and step 9 is where those get fixed (R11).
3. **Laying out is free; ordering is money.** You can redo anything in this guide as many times
   as you like. Nothing here buys anything. Ordering the board is work row F12.

**Where you are:** the schematic is finished and checked (0 errors, 0 warnings). The Teensy's
real pins are assigned (D-377), and the Teensy socket footprint is already made for you. Steps
1–8 need **no measurements**. Step 9 is the first one that does.

| Step | What                                  | Work row | Measurements?           |
| ---- | ------------------------------------- | -------- | ----------------------- |
| 1    | Open the project, learn the screens   | F8       | no                      |
| 2    | Give every symbol a footprint         | F8       | no                      |
| 3    | Make the board file and set the rules | F8       | no                      |
| 4    | Pull the parts onto the board         | F9       | no                      |
| 5    | A provisional outline                 | F9       | no (a guess on purpose) |
| 6    | Place the parts                       | F9       | no                      |
| 7    | Route the tracks, then DRC to zero    | F9       | no                      |
| 8    | 3D models and the 3D export           | F10      | no                      |
| 9    | The measurement pass                  | F11      | **yes**                 |
| 10   | The enclosure, the fit test, ordering | F1, F12  | yes                     |

---

## Words you'll meet

| Word            | What it means here                                                                           |
| --------------- | -------------------------------------------------------------------------------------------- |
| **Schematic**   | The circuit diagram, `icu-carrier.kicad_sch`: what connects to what, not where anything sits |
| **Symbol**      | A part on the schematic: a box or a resistor zig-zag with pins                               |
| **Footprint**   | The same part as copper on the board: the pads it is soldered to. Every symbol needs one     |
| **Net**         | One electrical connection: every pin that must be joined, e.g. `+5V` or `/CAN_TXD`           |
| **Ratsnest**    | The thin straight "rubber band" lines on the board showing connections not yet routed        |
| **Track**       | A copper wire on the board. **Via**: a plated hole taking a track to the other side          |
| **Zone** (pour) | A filled copper area, here the ground plane on the bottom side                               |
| **Edge.Cuts**   | The layer that holds the board's outline, the shape the factory cuts                         |
| **Courtyard**   | The keep-away box round each footprint; two courtyards must not overlap                      |
| **ERC / DRC**   | The checkers. ERC checks the schematic, DRC checks the board. **Zero errors is the rule**    |
| **STEP**        | A 3D file of the finished board, for fitting the enclosure in FreeCAD                        |

---

## Step 1 · Open the project (F8)

1. `cd ~/docs/storage/Rx7 && python tools/rx7.py status`, so you know the record is valid.
2. Start **KiCad** (from the app menu, or type `kicad` in a terminal).
3. **The very first time only**, KiCad asks about the global symbol and footprint library
   tables: choose **Copy default global … table (recommended)** both times. That's what makes the
   stock footprints in step 2 findable.
4. **File → Open Project…** → `02-PROJECTS/01-electrical/00-design/cad/icu-carrier/icu-carrier.kicad_pro`.
5. The project window lists the files. Double-click **icu-carrier.kicad_sch** to open the
   **Schematic Editor**.

**Moving around:** scroll wheel = zoom, hold the middle button and drag = pan, **Home** = zoom
to fit. Click a part and press **E** to see its properties. **Esc** always gets you out of a
tool.

**Look first:** the sheet has five areas: power, CAN, the nine sensor inputs, the pulse inputs
(tach and road speed), and the display and radio block, plus the 5 V buck drawn in full at the
bottom. J5 in the middle is the Teensy socket.
Its pins now carry the real Teensy pad numbers, and its six power pins (VIN, 3V3, GND) run along
its bottom edge.

**Check it:** **Inspect → Electrical Rules Checker** → **Run ERC**. You should see 0 errors
and 0 warnings. If you ever see one, stop and fix it before going on.

## Step 2 · Give every symbol a footprint (F8)

Every part needs a footprint before it can go on the board. Two groups already have one:
J5 (`icu-carrier:Teensy41_Socket`, made for you) and the whole 5 V buck at the bottom of the
sheet (U1, L2, C20–C26, R41–R43, drawn from TI's datasheet). Everything else is still blank.

1. **Tools → Assign Footprints…**. A three-column window opens: libraries on the left, the
   schematic's parts in the middle, and footprints on the right.
2. Click a part in the middle, find its footprint on the right (type in the filter box at the
   top), and **double-click** it to assign. Select several parts that share a footprint (Shift
   or Ctrl-click) and assign them all at once.
3. Work down this list. For each row: select those parts in the middle column, type the
   **filter** word into the box above the footprint list, and double-click the footprint it
   shows. Every footprint here exists in the KiCad on this machine.

| Select these parts (their Value) | Filter | Double-click |
| --- | --- | --- |
| every `100n`, the `10u` | `C_0805` | `C_0805_2012Metric` |
| every plain resistor: `10k` `15k` `47k` `4.7k` `1k` `12k` `39k` `100k` `1.2M`, and `1k - 2.2k 1% ?` | `R_0805` | `R_0805_2012Metric` |
| `22u 16V` | `C_1206` | `C_1206_3216Metric` |
| `100u 63V` | `CP_Elec_8x10` | `CP_Elec_8x10` (1) |
| `100R 1W` (×2) | `R_2512` | `R_2512_6332Metric` |
| `100k 0.5W` (×2) | `R_1210` | `R_1210_3225Metric` |
| every `BAT54S`, `BZX84C5V1`, `MMBT3904` | `SOT-23` | `SOT-23` |
| `74LVC1G17` | `SOT-23-5` | `SOT-23-5` (2) |
| `SMBJ33A` (×2) | `D_SMB` | `D_SMB` |
| `SS34` (×2) | `D_SMA` | `D_SMA` |
| `LM393`, `TCAN1042HVDRQ1` | `SOIC-8_3.9` | `SOIC-8_3.9x4.9mm_P1.27mm` |
| `SQD50P06 class` | `TO-252-2` | `TO-252-2` |
| `4 A` (the fuse) | `Fuse_1206` | `Fuse_1206_3216Metric` (1) |
| `common-mode choke - DNP` | `ACM2012` | `L_CommonModeChoke_Coilank_ACM2012` (3) |
| the jumpers `J1` `J3` `J7` `J8A` `J8B` | `PinHeader_1x02_P2.54` | `PinHeader_1x02_P2.54mm_Vertical` |
| `IC22` (page button), `backlight out` | `JST_XH_B2B-XH-A_1x02` | `JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical` (4) |
| `XIAO ESP32C3` | `Seeed_ESP32C3` | `MCU_Seeed_ESP32C3` |
| `BT817 EVE bridge header` (J4) | `PinHeader_1x10_P2.54` | `PinHeader_1x10_P2.54mm_Vertical` (P) |
| `LSM6DSO / ICM-42688-P` (the IMU) | `PinHeader_1x06_P2.54` | `PinHeader_1x06_P2.54mm_Vertical` (P) |
| `DT13-06PA` | `PinHeader_2x03_P2.54` | `PinHeader_2x03_P2.54mm_Vertical` (P) |
| `DT13-12PA` | `PinHeader_2x06_P2.54` | `PinHeader_2x06_P2.54mm_Vertical` (P) |
| `VN5E class - DNP` | — | leave it blank (5) |

   Notes on the numbered rows:

   - **(P) Placeholder.** The real footprint comes later: the BT817 header off the eval board
     (F2), the IMU when its breakout is chosen (P109), and the Deutsch connectors drawn from
     TE's drawing in step 9.
   - **(1)** Confirm against the part actually bought.
   - **(2)** Check the package on the reel.
   - **(3)** Not fitted, but the footprint keeps its place on the board.
   - **(4)** The backlight carries 2.5 A and an XH connector is rated 3 A: confirm.
   - **(5)** Picked along with the backlight switch; not fitted.

4. For every **placeholder**, open the part (**E**) and put `PLACEHOLDER - confirm` in a field, so you can't mistake it later.

5. Click **OK**, then **File → Save**, and run ERC again (0 / 0).

## Step 3 · Make the board file and set the rules (F8)

1. In the schematic editor: **Tools → Switch to PCB Editor** (or the PCB icon on the toolbar).
   KiCad creates `icu-carrier.kicad_pcb`, an empty board.
2. **File → Board Setup…**, and go down the list on the left:
   - **Board Stackup → Physical Stackup**: 2 copper layers, 1.6 mm board, 1 oz (0.035 mm)
     copper. These are the cheap default fab values.
   - **Design Rules → Constraints**: minimum clearance **0.2 mm**, minimum track width
     **0.2 mm**. Comfortably above any cheap fab's limits.
   - **Design Rules → Net Classes**: make these classes (**+** adds a row), then set each
     net's class in the lower table. The widths come from the IPC-2221 formula at a 10 °C rise,
     already worked out. Every power track is sized to its **fuse**, not its load:

| Class       | Track width | Clearance  | Nets                                                                          |
| ----------- | ----------- | ---------- | ----------------------------------------------------------------------------- |
| `Default`   | 0.25 mm     | 0.2 mm     | everything else                                                               |
| `PWR_LOGIC` | 0.6 mm      | 0.2 mm     | `+12V_LOGIC`, `+5V`                                                           |
| `PWR_BL`    | 2.2 mm      | 0.2 mm     | `+12V_BL`, `+12V_BL_SW` (4 A fuse)                                            |
| `TACH_HV`   | 0.25 mm     | **2.5 mm** | the tach input from `DP-ICU-B 4` up to and including its two 100 kΩ resistors |

The tach wire carries the coil's inductive kick, hundreds of volts, so its copper keeps
2.5 mm from everything (IPC-2221, 301–500 V on an uncoated outer layer; check the table
before you trust the figure). Nobody has measured the real kick yet (T-017).

3. **OK**, then **File → Save**.

## Step 4 · Pull the parts onto the board (F9)

1. In the PCB editor: **Tools → Update PCB from Schematic…** (**F8**) → **Update PCB**.
2. Every footprint lands in a pile, joined by ratsnest lines. A warning about the VN5E's blank
   footprint is expected (it's not fitted). Nothing else should warn.
3. Click on empty space to drop the pile.

## Step 5 · A provisional outline (F9)

The real outline comes from measuring the space behind the binnacle (**C4**). You haven't
measured it yet, so draw a **working guess** and expect to change it in step 9.

1. Pick the **Edge.Cuts** layer in the layer list on the right.
2. **Place → Draw Rectangle**, and draw about **100 × 70 mm** for a start: roomy enough to
   place everything without a fight. You'll shrink it later.
3. Decide the four sides now, because the enclosure (F1) is built around them:
   - **Connector edge**: both DT13 connectors side by side on one edge (D-270).
   - **Opposite edge**: the BT817 header and the page-button lead, which leave through grommets.
   - **Radio edge**: one short side, where the XIAO's antenna hangs toward the enclosure's
     plastic window.
   - **Mounting**: four M3 holes near the corners (**Place → Place Footprint**,
     `MountingHole:MountingHole_3.2mm_M3`).

## Step 6 · Place the parts (F9)

Keys: **M** move · **R** rotate · **F** flip to the back side · **Esc** drop the tool.
Place in this order, because power decides where ground current flows and everything else
lives with it:

1. **The two DT13 connectors** on the connector edge.
2. **Power, right at the connector.** Each 12 V input (logic `DP-ICU-A 1`, backlight
   `DP-ICU-A 6`) gets its SS34 and SMBJ33A right at its pin, before anything else touches the
   net. Then the fuse and the SQD50P06 on the backlight path. **The two 12 V inputs never
   share a pad, a pour or a via** (D-273). Then **the buck** (U1 and its parts): the input
   capacitors C20–C22 tight across U1's two VIN/PGND pin pairs, the inductor L2 right at SW,
   C24 from BOOT to SW, and the feedback parts (R41, R42, C26) right at FB. Keep the SW copper
   small. The note on the sheet repeats this.
3. **CAN**: the TCAN1042 close to `DP-ICU-A 4/5`, the DNP choke between them.
4. **The sensor row** along the connector edge, one little group per channel: divider →
   100 nF → BAT54S, with the BAT54S **nearest the Teensy pin**. Lay one group out neatly, then
   copy the pattern for the others.
5. **The pulse inputs**: the tach's two 100 kΩ resistors, zener, BAT54S and LM393. Keep the
   tach's high-voltage copper short and away from everything. Then road speed's jumpers and
   Schmitt chip.
6. **The Teensy socket (J5)** in the middle. The USB end faces where you might want to flash
   it through the enclosure. **Nothing tall under the Teensy**: its PSRAM sits underneath.
7. **The XIAO** at the radio edge, antenna end at the board edge, **IMU** away from the
   connectors and the buck, **BT817 header** and **page button** on the opposite edge.

Check as you go: **View → 3D Viewer** (**Alt+3**) shows it in 3D. Courtyards must not overlap.

## Step 7 · Route, then DRC to zero (F9)

Keys: **X** route a track (the **Route Single Track** tool, also on the right-hand toolbar) ·
**V** drop a via while routing ·
**/** flip the corner direction · **U** select a whole track · **Delete** removes it ·
**B** fill all zones (**Edit → Fill All Zones**).

1. **Ground plane first**: pick **B.Cu**, **Place → Draw Filled Zones**, click round the whole
   board, and choose net **GND**. Press **B** to fill. Now every GND pad on the bottom is
   already connected.
2. **Power**: route the 12 V inputs and `+5V`. The net classes set the widths for you.
3. **The analog lines**: away from the buck and the backlight path, with a via to ground next
   to each 100 nF capacitor.
4. **CAN**: CANH and CANL side by side, roughly the same length.
5. **The display lines** to the BT817 header: short.
6. **Everything else**, until the ratsnest is gone.
7. **Inspect → Design Rules Checker** → tick **Test for parity between PCB and schematic** →
   **Run DRC**. Fix every error until it reads **0 errors, 0 warnings**. Parity catches a
   footprint that doesn't match its symbol.
8. **File → Save**.

## Step 8 · 3D models and the 3D export (F10)

1. **View → 3D Viewer**. Any part showing as bare pads has no 3D model.
2. Most parts bring their model with them. Three need one downloaded:
   - **XIAO ESP32C3**: Seeed's own model (its KiCad footprint points at a model KiCad doesn't
     ship).
   - **DT13-06PA / DT13-12PA**: TE Connectivity publishes them on te.com: download the one for
     the exact part number you order.
   - **The IMU breakout**: from whoever sells it.
     Put each file in a `3d/` folder beside the project, then open the part (**E**) → **3D Models**
     tab → add the file. Check **pin 1 of the model sits on pad 1**.
3. Export, from a terminal in the project folder:

```
kicad-cli pcb render --side top -o icu-carrier-top.png icu-carrier.kicad_pcb
kicad-cli pcb render --side bottom -o icu-carrier-bottom.png icu-carrier.kicad_pcb
kicad-cli pcb export step --subst-models -o icu-carrier.step icu-carrier.kicad_pcb
kicad-cli pcb drc --severity-all --exit-code-violations -o icu-carrier-drc.rpt icu-carrier.kicad_pcb
```

The last one is DRC from the terminal: exit code 0 means clean. Every flag here was checked
against this KiCad.

**This is as far as you can go without measuring.** You'll have a complete, routed, DRC-clean
board with a 3D model. Everything after this corrects it against real numbers.

## Step 9 · The measurement pass (F11): the first step that needs hard numbers

It needs **C4** (the space behind the binnacle), plus the parts in your hand. Those come with
the cart at the shopping stage (D-323), except the eval board (F2), which is bought now.

| Measure                                               | On                          | Fixes                                                                   |
| ----------------------------------------------------- | --------------------------- | ----------------------------------------------------------------------- |
| Length, width, depth behind the binnacle              | the car (C4)                | the outline: space minus the enclosure wall and a fit gap               |
| Flange-to-board standoff, pin pitch, mounting holes   | the DT13s (P122)            | draw their real footprint from TE's drawing; replace the placeholder    |
| Row spacing and the underside clearance on its socket | a Teensy on its headers     | the socket footprint (it's from PJRC's 2.4 × 0.7 in and says `confirm`) |
| Header pitch, pin count, keying                       | the BT817 eval board (P117) | replace J4's placeholder                                                |
| Outline and antenna position                          | the XIAO                    | its placement at the radio edge                                         |
| Outline, pin pitch, holes                             | the IMU breakout (P109)     | replace the IMU placeholder                                             |

Then run DRC to zero again and re-export the STEP. Remove each `PLACEHOLDER` and `confirm` note
as you settle it.

## Step 10 · The enclosure, the fit test, ordering (F1, F12)

- **F1** (agent) draws the enclosure in FreeCAD around your STEP: the two DT13 cut-outs with a
  gasket, grommets on the opposite face, the plastic window at the antenna, and ASA or PETG,
  never PLA (D-270).
- **Print the enclosure and test-fit a bare board** before anything is soldered. It's the
  cheapest true test there is. If it fails, fix the board or the enclosure, never the model.
- **F12 is yours**: order two boards (P103).

## Saving your work

After each step: **File → Save**, then:

```
cd ~/docs/storage/Rx7
git add 02-PROJECTS/01-electrical/00-design/cad/icu-carrier
git commit -m "ICU carrier: step N"
```

`icu-carrier.svg` is the picture of the schematic that goes in the repo. Refresh it whenever the
schematic changes: `kicad-cli sch export svg --no-background-color -o . icu-carrier.kicad_sch`.
Renders, STEP files, DRC reports and backups stay out of git (`.gitignore`).

## When something goes wrong

| You see                      | It means                                       | Do                                                                                                                                              |
| ---------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| A part has no ratsnest lines | its footprint is blank or its pins don't match | step 2; check the footprint's pad numbers                                                                                                       |
| "Footprint not found"        | a library isn't in the table                   | **Preferences → Manage Footprint Libraries…**, **Project Specific Libraries** tab: `icu-carrier` must point at `${KIPRJMOD}/icu-carrier.pretty` |
| DRC "clearance violation"    | two things are too close                       | move the track; never loosen the rule to make it pass                                                                                           |
| DRC "parity" errors          | board and schematic disagree                   | **Tools → Update PCB from Schematic…** (**F8**)                                                                                                 |
| You can't click something    | it's on another layer, or locked               | pick its layer on the right; **E** to check "Locked"                                                                                            |
| Every part's number changed (R1, C1, U1…) | **Annotate Schematic** ran with *reset existing annotations* | Never reset: the guide and the record cite the numbers (J4, J5, U1, L2…). If KiCad asks to annotate, choose **Keep existing annotations** |
| ERC says *pin not connected* on parts that look wired | a wire runs *through* the part instead of *ending* at its pins | Delete that wire and redraw it to end exactly on each pin (a pin you hit shows a connection dot) |
| Anything strange             |                                                | **Ctrl+Z** undoes; git has every saved step                                                                                                     |

---

## Part B · The DCU carrier (H-002): later, the same way

The DCU is this build's board too (D-374), but it has no schematic yet, and it waits on the
agent's rows, not on a measurement: `V-083` (its parts), `V-101` (the comfort currents),
`H-007` (the panel). Its drawing checklist is `dcu-carrier/TARGET.md`, and its spec is
`../../data/dcu_channels.csv`. Once those rows land, the schematic is drawn, and then this same
guide applies to it: footprints, rules, layout, 3D, measure, fit, order (F5).

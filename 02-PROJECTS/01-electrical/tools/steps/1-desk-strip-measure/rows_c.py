# -*- coding: utf-8 -*-
# Orders and car-whole measurements: Y16, Y18, Y27, V-114
# Y16 and Y18 quote two files and four parts rows, read here so a rebuild follows them:
# the cart files in 00-design (bench-revA-digikey-cart.csv, bench-revA-mouser-cart.csv - one line
# per part bought: group, qty, mpn, maker, what, refs, rows, est_unit_usd, price_source, substitute)
# and parts P103, P144, P175, P195 (the four boards' fab lines).
import csv
import os

ROWS = []

DESIGN = "02-PROJECTS/01-electrical/00-design"
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
PRICED = "2026-10-13"   # the day the cart files' prices were read or estimated (work Y37)


def _csv(*path):
    with open(os.path.join(_ROOT, *path), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


DK = _csv("00-design", "bench-revA-digikey-cart.csv")
MO = _csv("00-design", "bench-revA-mouser-cart.csv")
_PARTS = {r["id"]: r for r in _csv("data", "parts.csv")}
BOARDS = [("P103", "icu-carrier", "110 x 80"), ("P144", "dcu-carrier", "180 x 80"),
          ("P175", "panel", "180 x 47.3"), ("P195", "upper-board", "130 x 36")]


def _usd(rows):
    return sum(float(r["qty"]) * float(r["est_unit_usd"]) for r in rows)


def _money(v):
    return "$%.2f" % v


def _each(v):
    v = float(v)
    return ("$%.3f" % v).rstrip("0") if v < 0.1 else "$%.2f" % v


def _group(rows, g):
    return [r for r in rows if r["group"] == g]


def _list(rows):
    return " · ".join("%s x %s, %s, %s each" % (r["qty"], r["mpn"], r["what"], _each(r["est_unit_usd"])) for r in rows)


def _subs(rows):
    return " · ".join("%s: %s" % (r["mpn"], r["substitute"]) for r in rows if r["substitute"])


def _fab_usd():
    return sum(float(_PARTS[p]["qty"]) * float(_PARTS[p]["unit_usd"]) for p, _, _ in BOARDS)


def _oshpark_usd():
    # OSH Park's public price: $5 a square inch for three copies of a 2-layer board
    return sum(5.0 * float(s.split(" x ")[0]) * float(s.split(" x ")[1]) / 645.16 for _, _, s in BOARDS)


def _src(word):
    return sum(1 for r in DK if r["price_source"].startswith(word))


def _chunks(rows, n):
    return [rows[i:i + n] for i in range(0, len(rows), n)]


KIT = _group(DK, "1 DU kit")
G2 = _group(DK, "2 DU carrier")
G3 = _group(DK, "3 CU carrier")
G4 = _group(DK, "4 both carriers")
G5 = _group(DK, "5 CU panel and upper board")
REST = [r for r in DK if r["group"] != "1 DU kit"]
assert len(KIT) + len(G2) + len(G3) + len(G4) + len(G5) == len(DK)

ROWS.append(dict(
    id="Y16",
    goal="The Display Unit's bench kit is ordered: two radio modules, two PSRAM chips, the clock's coin cell and its holder, two microSD cards and the display you ruled on; its bridge board when the agent has drawn it.",
    where="desk",
    time="30 min",
    tools=["a browser and a card"],
    parts="P116 P108 P202 P151 P118 P119",
    before=[
        "Nothing. You ruled on 2026-10-12 that this kit is bought before the freeze, and on 2026-10-13 that the PSRAM and the coin cell go with it",
        "Y18's Digi-Key cart is open: tonight's lines ride in it",
    ],
    know=[
        "Your order: buy the bench kit now, build the DU and the CU, and buy nothing only to test. The PSRAM chips and the coin cell are parts of the DU and are bought now. [D-541]",
        "Tonight's lines are group 1 of the Digi-Key cart file: %d lines, %s by the file's prices of %s. [the Digi-Key cart file bench-revA-digikey-cart.csv; parts P116, P108, P202]" % (len(KIT), _money(_usd(KIT)), PRICED),
        "No price or stock figure in the file was read on Digi-Key's own page: the site refuses automated readers. The cart shows the live price and the stock of every line before you pay. [work Y37]",
        "P116, the radio: Seeed part 113991054, the XIAO ESP32C3. $4.99 each and in stock on Seeed's own page on %s. One for the carrier, one for the desk. [parts P116; work Y37]" % PRICED,
        "P108, the PSRAM: two APS6404L-3SQR-SN chips, soldered to the pads under the DU's Teensy. P202: a CR2032 cell in a holder with pins, on a flying lead to the Teensy's VBAT pad. [parts P108, P202]",
        "The display (P118) is the HannStar HSD123KPW2-D10 panel, 1920 x 720, listed at 850 nit, in a VSDISPLAY kit with an HDMI driver board: your ruling of 2026-10-13, which lowered the 900 to 1000 nit floor to what is sold. [D-550; parts P118]",
        "Two listings of that kit were found by one search on 2026-10-13; neither seller's page was read, so both prices are as listed and est: Newegg's VSDISPLAY kit with the VS-56S2 board (HDMI, USB and SD in) at $237.99, and VSDISPLAY's own eBay listing at $171.88, whose title names an HD board. Your ruling expected about $110 to $250. [parts P118; D-550]",
        "The same panel is sold in kits with other boards - VGA and DVI only, or USB Type-C only. Those do not take the bridge's HDMI lead: the board in the kit must have an HDMI input. [parts P118; D-550]",
        "The bridge (P119) is not bought: it is a small board the agent draws - a TFP410 chip, the BT817 board's 50-pin RGB cable in, HDMI out - and you order it with the next boards, in a row of its own that follows the drawing. This row and the DU's build do not wait for it: the display is lit when that board is back, and until then the BT817 board's own screen stands in. [D-550; D-553; work Y46; parts P119; S-500 p.1]",
        "There is no page button any more: its job is the climate unit's screen knob, which rides in the panel's parts (Y18), not in this kit. [D-580; parts P120, P219]",
        "The BT817 evaluation board is ordered and the three Teensy 4.1 boards are in hand. [parts P117, P142]",
    ],
    done_when="The kit's lines and the display are paid for and the row is ticked. The bridge board is ordered later, in a row of its own.",
    if_not="The cart shows a line out of stock or does not know a part number: take the substitute this row's step names, and write it in the app. Neither display listing shows an HDMI input, or both are gone: do not buy another kit - say so in the app and the agent finds one.",
    record="Tick Y16 when the kit's lines and the display are ordered. In words: what you paid for each, which display listing you took, and the display's outline and thickness in mm and its supply voltage from the listing.",
    steps=[
        ("Check the kit's lines in the Digi-Key cart",
         "They load with Y18's cart file (its step 10). " + _list(KIT) + ".",
         "%d lines, %s by the file's prices of %s." % (len(KIT), _money(_usd(KIT)), PRICED),
         ""),
        ("Take a substitute where the cart has none",
         _subs(KIT) + ". The radio modules and the PSRAM chips have no substitute: if the cart has none, leave the line out and say so in the app.",
         "Every kit line in the cart shows stock.", ""),
        ("Add two microSD cards (P151)",
         "Two cards, where you buy cards. They are not in the Digi-Key file. The record gives no size; the full log is about 11 MB for an hour of driving, so any current card holds years of it.",
         "Two cards, about $%.0f by the row's estimate." % (float(_PARTS["P151"]["qty"]) * float(_PARTS["P151"]["unit_usd"])), ""),
        ("Order the display",
         "One HannStar HSD123KPW2-D10 kit whose driver board has an HDMI input: Newegg's VSDISPLAY kit with the VS-56S2 board ($237.99 as listed) or VSDISPLAY's own eBay listing ($171.88 as listed). Before paying, read on the listing: the panel is HSD123KPW2-D10, 1920 x 720, 850 nit; the board has an HDMI socket; what supply voltage it wants; the panel's outline and thickness.",
         "One display kit ordered; its outline, thickness and supply voltage noted.",
         "A kit whose board has only VGA, DVI or Type-C in is the wrong one. Over $250: stop and say so in the app - your ruling expected $110 to $250."),
        ("Leave the bridge out",
         "Nothing to buy for P119: the agent draws the bridge board and it is ordered with the next boards. The page button (P120) is gone (D-580): its job is the climate unit's screen knob. The carrier, the Teensy, the radio and the BT817 board are built and run without the bridge.",
         "No bridge and no button in any cart.", ""),
        ("Pay with Y18's cart",
         "The kit's lines are paid when you pay the Digi-Key cart in Y18.",
         "Order placed.", ""),
        ("Enter it",
         "Tick Y16. Write what you paid in the app, and the display's listing, size and supply.",
         "Y16 ticked, your note saved.", ""),
    ],
))

_G3 = _chunks(G3, 16)
_G4 = _chunks(G4, 14)
_fab = _fab_usd()
REBUILT = "2026-10-13"  # the day the fab zips were rebuilt: both carriers' after they were corrected (D-547), then the DU carrier's and the panel's again after the read (D-549)

# What a cart line must not be swapped for, said on the step that lists the line (D-547, D-273):
# the first sentence whose part number the step's lines hold.
_WATCH = [
    ("SQ2361", "Q3 is the 60 V SQ2361ES: its supply is clamped at 53 V, so take nothing rated under 60 V in its place."),
    ("SMAJ40A", "SMAJ40A is the one-way type. Never SMAJ40CA, the two-way type: the board is drawn for the one-way part, its banded end at the mark."),
    ("EEE-FK1J680UP", "The capacitor is 68 uF 63 V in the 8 mm can the boards draw. The 100 uF EEE-FK1J101P is a 10 mm can and does not fit; a 50 V part is not enough."),
    ("SMBJ33A", "SMBJ33A is the one-way type. Never SMBJ33CA, the two-way type: the board is drawn for the one-way part, its banded end at the mark."),
    ("SQ2364", "Q1 and Q2 are SQ2364EES: they are switched from 3.3 V, so take nothing whose on-resistance is given only at 4.5 V or more (SQ2362CES, PMV37ENEA)."),
    ("MMBT5551", "MMBT5551 is the 160 V transistor: its collector stands on a supply clamped at 53 V, so never the 40 V MMBT3904 in its place."),
    ("SL310A", "SL310A is the 100 V diode: it stands ahead of the 53 V clamp, so never a 40 V part such as B340A or SS34."),
]


def _watch(rows):
    return " ".join(s for key, s in _WATCH if any(r["mpn"].startswith(key) for r in rows))

ROWS.append(dict(
    id="Y18",
    goal="The four bench-revision circuit boards and the parts that go on them are ordered: the DU and CU carriers, the panel board and the upper connector board from the fab, their components from Digi-Key and the sealed receptacles from Mouser.",
    where="desk",
    time="1 h 30 min - confirm",
    tools=["a browser and a card"],
    parts="P103 P144 P175 P195 P122 P150 P153 P194 P196 P145 P146 P147 P148 P149 P157 P170 P177 P178 P193 P104 P105 P106 P107 P109 P110 P159 P169 P176 P203 P155 P192",
    before=[
        "Y17 (the fab package) and Y37 (the sellers) are done: the files are in the tree",
        "Pull the tree first so the zips and the cart files are the latest",
    ],
    know=[
        "Your ruling: the desk set-up is bought before the freeze, accepting that a measurement may later force a second board; and your order of 2026-10-13: build the DU and the CU first, buy nothing only to test, and not the printed case tonight. [D-490; D-541; D-542]",
        "Three carts. The fab: four boards, five of each, %s by the rows' estimates. Digi-Key: %d lines, %s by the cart file's prices (%s of it is Y16's kit). Mouser: %d lines, %s. About %s before shipping and tax; every figure dated %s. [parts P103, P144, P175, P195; the two cart files]" % (
            _money(_fab), len(DK), _money(_usd(DK)), _money(_usd(KIT)), len(MO), _money(_usd(MO)), _money(_fab + _usd(DK) + _usd(MO)), PRICED),
        "The fab is JLCPCB: five is the least it sells of a board. The other fab priced, OSH Park, is %s for three of each of the same four boards by its public price of $5 a square inch, made in the United States. [work Y37; parts P103]" % _money(_oshpark_usd()),
        "No live quote was read: the fab's quote page and Digi-Key's and Mouser's pages refuse automated readers. The fab prices are estimates, and the option names in the steps are JLCPCB's as last known - confirm on the page. Each cart shows its real total before you pay. [work Y37]",
        "The boards: %s. All four are 2 layers, 1.6 mm thick, with 0.2 mm tracks and gaps and a 0.3 mm smallest hole. None needs gold fingers, edge plating, castellated holes or controlled impedance. [parts P103, P144, P175, P195; the fab folders' job files]" % ", ".join("%s %s mm" % (n, s) for _, n, s in BOARDS),
        "Each board's fab folder under 00-design holds one zip of gerbers and one BOM: icu-carrier-revA-gerbers.zip, dcu-carrier-revA-gerbers.zip, panel-revA-gerbers.zip, upper-board-revA-gerbers.zip. [work Y17; the fab folders]",
        "Three zips were rebuilt on %s and kept their names: both carriers' after they were corrected, then the DU carrier's and the panel's again after the boards were read once more. Upload only the zips a fresh pull gives. A zip saved or uploaded before that builds a board that does not work. The upper board's zip did not change. [D-547; D-549; work Y42, Y44; the fab folders]" % REBUILT,
        "The cart file names every part bought by its maker's part number, with what it is, where it goes and the parts row it belongs to. Passives are bought in tens, the rest as the boards count them, for one DU and one CU. [the Digi-Key cart file bench-revA-digikey-cart.csv]",
        "Of the file's %d prices, %d are Digi-Key's or Mouser's own as Octopart listed them, %d are another distributor's, %d are the maker's page and %d are estimates. All are est until the cart shows them. [the Digi-Key cart file, price_source; work Y37]" % (
            len(DK), _src("Digi-Key's row") + _src("Mouser's row"), _src("another distributor"), _src("maker's page"), _src("estimate")),
        "The bulk capacitor at DU C1 and CU C1, C8 and C29 is 68 uF 63 V, Panasonic EEE-FK1J680UP, in the 8 mm can the boards draw. It sits across a diode that clamps at 53 V, so it must be a 63 V part. 100 uF 63 V comes only in a 10 mm can, which does not fit. If the cart has none, the 47 uF 63 V EEE-FK1J470P is the same can. [D-547; D-273; the Digi-Key cart file]",
        "CU transistor Q3 is the 60 V SQ2361ES-T1_GE3. Its supply is clamped at 53 V, so nothing rated under 60 V goes there. [D-547; D-273; the DCU carrier's BOM]",
        "CU transistors Q1 and Q2 are Vishay SQ2364EES-T1_GE3. They are switched from a 3.3 V pin, so only a part whose on-resistance is given at 2.5 V or less goes there: not SQ2362CES, not PMV37ENEA. [D-549; the DCU carrier's BOM]",
        "Two more kinds of part stand on a supply clamped at 53 V and are bought above it. The transistors DU Q2 and CU Q4 are the 160 V MMBT5551, never the 40 V MMBT3904 beside it in the cart (that one is DU Q4 alone, on 5 V). The input diodes DU D23, D25 and CU D1 are the 100 V SL310A, never a 40 V B340A or SS34. [D-549; D-273; the Digi-Key cart file]",
        "Each fab folder also holds two assembly drawings, front and back, that show every part's reference where it sits: the boards print none. They are for the build, not for the fab: upload only the zip. [D-549; the fab folders]",
        "The six TVS diodes are the one-way type: SMBJ33A at DU D24 and D26 and CU D2 and D4, SMAJ40A at CU D7 and D8. The part number ends in A with no C before it. The CA parts are two-way, sit beside them in any cart, and must not be taken: each board is drawn for the one-way part, its banded end at the silkscreen's mark. [D-547; the Digi-Key cart file]",
        "The window switches are NKK B28AP: its maker's drawing gives pins 2.54 mm apart and poles 5.08 mm apart, which is the pattern the panel board draws. The four keys must stand 13 mm tall; Omron's B3F-1070 is 9.5 mm and is not the part. [the panel board; work Y37]",
        "The panel's twelve symbol and ring lights are green, your word for them; the seat arcs are six blue and six red. [ideas I-001, I-004; parts P192]",
        "Not in this order: the printed cases and their hardware (P179 to P184), the panel's small screen (P201, not chosen), the left plate (P198 to P200, P204) and the parts on these boards that only serve the plate - the upper board's second 12-way receptacle J2, its header J8 and the panel's header J3. P173 buys nothing: the key lights are among P192's. [D-542; parts P179, P201, P198, P173]",
        "Building these boards needs solder paste, flux and hot air or a hot plate for the chips with a pad underneath (the two bucks, the motor driver, the high-side switches, the light driver). No parts row holds them; the one soldering row is the iron and solder in the Amazon cart. [the carrier and panel BOMs' footprints; parts P044; work Y37]",
    ],
    done_when="The fab order, the Digi-Key order and the Mouser order are placed and the row is ticked.",
    if_not="A cart shows a line out of stock or does not know a part number: take the substitute the step names; where it names none, leave the line out, pay for the rest and write the part number in the app. The fab's preview shows a wrong outline or missing layers: do not pay; tell the agent which zip.",
    record="Tick Y18 when the three orders are placed. In words: what each cart came to, any part you substituted or left out, and the delivery dates the carts gave.",
    steps=[
        ("Pull the tree and find the files",
         "git pull in ~/dev/Rx7. Under " + DESIGN + " each of the four board folders (icu-carrier, dcu-carrier, panel, upper-board) has a fab folder with one <board>-revA-gerbers.zip. Beside the README in " + DESIGN + " are bench-revA-digikey-cart.csv and bench-revA-mouser-cart.csv.",
         "Four zips and two cart files.",
         "Three zips (both carriers and the panel) were rebuilt on %s under the same names. Use only the ones this pull gives: delete any zip you saved or uploaded before." % REBUILT),
        ("Upload the first zip at the fab",
         "On jlcpcb.com open the quote page and add icu-carrier-revA-gerbers.zip. Let it read the file.",
         "A preview of the board, 110 x 80 mm, 2 layers.",
         "A preview with the wrong size or one copper layer means the wrong file: stop."),
        ("Set the quantity to 5",
         "PCB Qty 5. It is the least the fab sells; one is built, the rest are spares.",
         "Qty 5.", ""),
        ("Leave layers, thickness and copper as read",
         "Layers 2 · PCB Thickness 1.6 mm · Outer Copper Weight 1 oz. These are the defaults.",
         "2 layers, 1.6 mm, 1 oz.", ""),
        ("Leave the colour green",
         "PCB Color green. The record sets no colour; green is the fab's default.",
         "Green.", ""),
        ("Choose the surface finish",
         "Surface Finish HASL, the default. The record sets none. If your solder is lead-free, choose the lead-free HASL instead.",
         "HASL.", ""),
        ("Remove the order number",
         "Mark on PCB: Remove Mark, so the fab does not print its order number on the board. Leave everything else as it stands: no gold fingers, no castellated holes, no impedance control, one design, single boards.",
         "Remove Mark chosen, the rest default.",
         "If removing the mark costs extra, leave the mark: it is only print."),
        ("Save it and add the other three boards",
         "Save to cart. Then the same six settings for dcu-carrier-revA-gerbers.zip (180 x 80 mm), panel-revA-gerbers.zip (180 x 47.3 mm) and upper-board-revA-gerbers.zip (130 x 36 mm).",
         "Four boards in the fab's cart, five of each, each preview at its size.",
         "A preview with the wrong size means the wrong file: stop."),
        ("Choose the shipping and pay the fab",
         "By the rows' estimates the four boards are %s: %s. Shipping and any import duty are on top and were not read; the cart shows them. Take the cheaper shipping unless you want the boards sooner." % (
             _money(_fab), " · ".join("%s five for %s" % (n, _money(float(_PARTS[p]["qty"]) * float(_PARTS[p]["unit_usd"]))) for p, n, _ in BOARDS)),
         "Fab order placed. The cart gives the build time and the delivery date.",
         "If the boards alone come to more than twice the estimate, stop and say so in the app."),
        ("Start the Digi-Key cart from the file",
         "On digikey.com open the cart and use its list upload with bench-revA-digikey-cart.csv: the qty column is the quantity and the mpn column the manufacturer part number. If the cart takes no file, type each line's mpn and qty from the file.",
         "%d lines in the cart." % len(DK),
         "The upload's wording is Digi-Key's and was not read tonight."),
        ("Read the stock of every line",
         "Every line should show stock for the quantity asked. Y16's kit is the first %d lines. Where a line shows none, the next steps name its substitute." % len(KIT),
         "Each line in stock, or its substitute in its place.", ""),
        ("Check the DU carrier's own lines",
         _list(G2) + ".",
         "%d lines, %s." % (len(G2), _money(_usd(G2))), ""),
    ] + [
        ("Check the CU carrier's own lines, part %d of %d" % (i + 1, len(_G3)),
         _list(c) + ".",
         "%d lines, %s." % (len(c), _money(_usd(c))),
         _watch(c))
        for i, c in enumerate(_G3)
    ] + [
        ("Check the lines both carriers share, part %d of %d" % (i + 1, len(_G4)),
         _list(c) + ".",
         "%d lines, %s." % (len(c), _money(_usd(c))),
         _watch(c))
        for i, c in enumerate(_G4)
    ] + [
        ("Check the panel's and the upper board's lines",
         _list(G5) + ".",
         "%d lines, %s." % (len(G5), _money(_usd(G5))),
         "The keys must be 13 mm tall. A 9.5 mm key will not reach the faceplate."),
        ("Take the substitutes where the cart has none",
         _subs(REST) + ".",
         "No line left at zero stock without a substitute or a note.", ""),
        ("Pay Digi-Key",
         "The %d lines come to %s by the file's prices of %s (%s without Y16's kit). Shipping and tax are on top." % (len(DK), _money(_usd(DK)), PRICED, _money(_usd(REST))),
         "Digi-Key order placed. The cart gives the delivery date.",
         "If the cart's total is more than a third over the file's, look for a line whose quantity loaded wrong."),
        ("Order the sealed receptacles at Mouser",
         "On mouser.com: " + _list(MO) + ". These are the plain flanged board receptacles, key A. The flange's gasket is settled with the case.",
         "%d lines, %s by the file's prices. Mouser's page shows the stock." % (len(MO), _money(_usd(MO))),
         "If Mouser has none of one, TE's own store and TTI listed them; do not take a DTM13 or a DT15, they are other parts."),
        ("Enter it",
         "Tick Y18. Write what each cart came to, any substitute or line left out, and the delivery dates.",
         "Y18 ticked.", ""),
    ],
))

ROWS.append(dict(
    id="Y27",
    goal="TE's Deutsch connector model files are in the model library on this Mac, so the Design page's stand-in connectors are replaced by the real shapes at the next export.",
    where="desk",
    time="15 min if they are already there; 1 h to copy or re-save",
    tools=["the Mac's terminal", "a USB stick or the home network, if copying from the Fedora PC", "a browser"],
    parts="",
    before=["Nothing. This can be done today"],
    know=[
        "The model library is the folder 02-PROJECTS/02-cad/model/library in the tree. It is kept out of git because the models' licences vary and the repository is public, so GitHub does not carry it from one machine to the other. [work Y27]",
        "Each model has its own folder named after its row, for example 02-PROJECTS/02-cad/model/library/electrical/deutsch-dt04-2p-te, holding TE's STEP file and zip. [00-CAR cad deutsch-dt04-2p-te]",
        "An earlier ruling said TE's download needs a login. The model rows say it did not: obtained yes, login no. The files were simply on the other machine. [work Y27; D-514]",
        "TE's site refuses a scripted download but serves the same link to a normal browser. [00-CAR cad deutsch-dt04-2p-te]",
        "The Fedora PC's clone is ~/docs/storage/Rx7; the Mac's is ~/dev/Rx7. [CLAUDE.md]",
        "Three more models need a login only you have: Omron's G8HL micro-ISO relay, Seeed's own XIAO ESP32-C3 STEP on GrabCAD, and Blue Sea's 5028 fuse block and 2300 busbar, whose pages refused the tool. They are optional for this row. [work Y27; 00-CAR cad omron-g8hl-micro-iso-omron, xiao-esp32c3-grabcad-seeed, bluesea-5028-st-blade-6-bluesea]",
        "Until a connector's file is found the Design page draws a stand-in from the dimension table; every connector stays marked unconfirmed either way. [00-design README section 13]",
    ],
    done_when="The command in step 1 lists the DT04, DT06, DTP04 and DTP06 folders on the Mac and none is empty.",
    if_not="A folder is missing and the Fedora PC is not to hand: open that model row's link in a browser, save the STEP into a folder of the row's name under library/electrical, and carry on. A model you cannot get: say which in the app; its stand-in stays.",
    record="Tick Y27 when the connector files are on the Mac. In words, name any optional model you also saved.",
    steps=[
        ("Look first",
         "In the terminal: ls ~/dev/Rx7/02-PROJECTS/02-cad/model/library/electrical | grep deutsch . When this step was written (2026-10-13) this Mac already listed 53 such folders, none empty.",
         "A list of folders: deutsch-dt04-..., deutsch-dt06-..., deutsch-dtp04-..., deutsch-dtp06-... If they are all there, go to the last step.", ""),
        ("Copy from the Fedora PC if they are missing",
         "On the Fedora PC the folder is ~/docs/storage/Rx7/02-PROJECTS/02-cad/model/library/electrical. Copy every folder whose name begins deutsch- to the same path on the Mac, by USB stick or over the network.",
         "The same folders on the Mac.", ""),
        ("Or save them again from TE",
         "Each folder's model row holds TE's link (a 'Customer View Model, 3D STEP'). Open it in a browser, save the file, and put it in a folder of the row's name under library/electrical.",
         "A STEP file in each folder.", ""),
        ("Optional: the three models behind a login",
         "If you have the logins: Omron's G8HL relay model into omron-g8hl-micro-iso-omron, Seeed's XIAO ESP32-C3 STEP from GrabCAD into xiao-esp32c3-grabcad-seeed, Blue Sea's 5028 block into bluesea-5028-st-blade-6-bluesea - each a folder under library/electrical.",
         "Any you could get, saved.", ""),
        ("Enter it",
         "Tick Y27. The agent's next export swaps the stand-ins for the real models.",
         "Y27 ticked.", ""),
    ],
))

ROWS.append(dict(
    id="V-114",
    goal="The review's measurements are taken at the car and written down: CK19, CK20, CK21, CK22, CK23, CK24, CK08, CK09, CK10, then CK17 and CK18 with the column covers off.",
    where="engine bay, the nose, the hatch, and the steering column",
    time="a day - confirm",
    tools=[
        "multimeter: ohms, continuity, DC volts",
        "an ammeter good for 20 A, or the clamp meter",
        "a fused 12 V test lead and two jumper leads with clips",
        "calipers, and a thread gauge or a few known nuts",
        "screwdrivers for the column covers",
        "notepad, phone camera, masking tape and a marker",
        "wheel chocks",
    ],
    parts="",
    before=[
        "The car is whole and runs: these are taken before the interior comes out",
        "Lever in P, handbrake on, wheels chocked",
        "Battery negative off for every ohm reading and before touching a stud; back on for the powered tests",
        "Garage door open whenever the engine runs",
    ],
    know=[
        "Each check has its own row saying what to measure and why; nothing here needs the interior out. Three design rows wait on these numbers. [work V-114, R13, R14, R15]",
        "Pop-up motors (plugs E-03 left, E-04 right), four wires: WR motor feed, R the up command, RY the down command, YG the 'running' lamp line. The plug is cross-shaped: YG top, WR left, RY right, R bottom. [00-CAR PT033-WR, PT033-R, PT033-RY, PT033-YG]",
        "The diagram says each motor has its own relay and cam switch inside: 12 V on R drives it up and it stops itself, 12 V on RY drives it down, and YG is at 12 V while it runs. The new design follows that. If the motor does not behave so, the design is reopened. [00-CAR SP-584; D-460; checks CK08]",
        "Both manual raise knobs on the pop-up motors work. [00-CAR PT033]",
        "Wiper motor (plug D-02): L, LB, LW, LR on a four-way and B on a single plug. LW is the low brush, LR the high brush, B the ground; the diagram reads L as the fed common brush and LB as the park switch's output. The design had L and LB the other way round. [00-CAR PT678-L, PT678-LB, PT678-LW, PT678-LR, PT678-B; checks CK09]",
        "Headlamps (plugs E-08 left, E-09 right): RY low beam, RL high beam, B ground. LED units fitted by a previous owner sit in the factory buckets. [00-CAR PT035, PT035-RY, PT035-RL]",
        "Oil pressure sender C-09: the 1985 book gives open circuit at 0 psi, about 197 ohm at the gauge's first mark and 141 ohm at 60 psi. The 1982 gauge's scale is not recorded. [00-CAR SP-787; checks CK19]",
        "Release solenoids: hatch on wire GR, fuel door on wire GB, each fed from LR (20 A constant) through its dash switch and grounded at the rear. Nobody knows their current; the new branch fuse is 10 A. [00-CAR PT030-GR, PT031-GB, PT635-LR, SP-218; fuses F33; checks CK20]",
        "Rear defogger grid G-25: wire LG in, B to ground. Its dash switch is broken and the grid is peeling in places. The design assumes 10 to 13 A. [00-CAR K-020, K-026; loads LD10; checks CK21]",
        "Washer pump D-01: LB is its 12 V feed, LY its switched ground. It does not work today and nobody knows why. [00-CAR PT038-LB, PT038-LY, K-022]",
        "Ignition switch: WR battery in, L is ACC, BY is IG, and a second BY is START. [00-CAR PT708-C, PT708-E, PT708-D, PT708-A]",
        "Column switch plugs: lights E-01 (a 2-pin R, WG and a 6-pin RG, RW, R, RL, RY, GL), turn and hazard F-02 (WG, GY, GW, GB, GR, GO), wiper D-03 (B, LO, LY, LR, LG, LW). The contact tables in the record are the 1980 car's. [00-CAR PT639, PT640, SP-473, SP-474, SP-475]",
    ],
    done_when="Every one of the eleven checks has its readings written in the app.",
    if_not="A reading that contradicts the 'expect' is the point of the day: write it exactly, with the position the part was in, and go on. A motor that does not stop by itself, anything that smokes or a fuse that blows: take the 12 V off and write what happened. Do not repeat a powered test more than twice.",
    record="Tick V-114. Type the readings in the answer, one block per check, each starting with its number (CK08: ...). Photos go in 00-CAR/photos.",
    steps=[
        ("Get the car and the tools ready",
         "Lever in P, handbrake on, wheels chocked, bonnet up, engine cold. Make a page per check in the notepad.",
         "Tools laid out; notepad headed CK19 to CK18.", ""),
        ("CK19: oil sender, engine off",
         "At the engine's rear housing pull the push-on lead (wire BrY) off the oil pressure sender C-09 - it is the upper one; the water temperature sender is directly below. Meter on ohms, one probe on the sender's terminal, one on the engine block.",
         "Open circuit at 0 psi (the 1985 figure).", ""),
        ("CK19: oil sender, warm idle",
         "Leave the lead off the sender. Start the engine and let it warm. At idle, read ohms from the sender's terminal to the block. Then stop the engine and push the lead back on.",
         "A resistance that falls as pressure rises; the 1985 book gives about 197 ohm at the first mark and 141 ohm at 60 psi.",
         "Belt and fan are turning: sleeves and leads clear. Garage door open."),
        ("CK20: release solenoid current",
         "At the hatch release switch's plug on the dash (wires LR and GR) and the fuel-door switch's plug (LR and GB): unplug the switch and bridge LR to the other wire through the ammeter for half a second. LR is live with the key out. Or use the clamp meter round the GR or GB wire while you press the switch.",
         "The hatch pops, then the fuel door; a current for each in amps. Unknown: the factory fuse is 20 A.",
         "Use the 20 A range or the clamp, half a second only: an unknown current can blow a meter's 10 A fuse."),
        ("CK21: defogger grid",
         "At the hatch glass, part the grid's two connections (wire LG in, wire B to ground). Ohms across the grid. Then feed 12 V to the LG tab through the fused lead with the B tab on ground, put the meter's black probe on the B tab and slide the red probe along each line.",
         "About 1 ohm across the grid if the design's 10 to 13 A is right (arithmetic; nothing has been measured). Along a good line the volts fall evenly from 12 to 0; a jump marks a break.",
         "The grid is peeling: touch the lines lightly. Expect 10 to 13 A; fuse the lead at 15 A."),
        ("CK22: washer pump",
         "Fill the reservoir. At the pump's plug D-01, on the pump side: 12 V from the fused lead to the LB terminal, a jumper from the LY terminal to ground.",
         "It runs and sprays, or it does not. If it runs, the fault is in the car's circuit, not the pump.", ""),
        ("CK23: which wire is low beam",
         "Raise both lamps with the manual knobs on the motors. Unplug the left lamp (E-08: RY, RL, B). On the lamp side put the B terminal to ground, then 12 V from the fused lead on RY alone, then on RL alone. Note which beam lights each time. Repeat on the right lamp (E-09).",
         "RY lights low beam, RL lights high beam.", ""),
        ("CK24: stud threads",
         "Battery negative off. With calipers and a thread gauge (or a known nut) measure the thread of: the alternator's B stud, the starter's B and S terminals, any stud on the two battery clamps, and the PMU's stud (the manual says M6). Then read the part numbers on the spare PMU terminals in hand, the 1.5 mm and the 2.8 mm.",
         "A diameter and pitch for each stud; terminal numbers (the pinout lists 211CC2S2160P, 211CC3S2120 and 211CC3S3120).",
         "The alternator B stud and the starter B terminal are live until the battery negative is off."),
        ("CK08: ohm the left pop-up motor, parked",
         "Battery negative still off. Unplug the left motor's four-way plug E-03 (YG top, WR left, RY right, R bottom). On the motor side, with the lamp parked, read ohms for: WR to case, R to case, RY to case, YG to case, WR to R, WR to RY, R to RY.",
         "Seven readings. Write 'open' where the meter shows nothing.", ""),
        ("CK08: the same half-raised and raised",
         "Turn the motor's manual knob until the lamp is half up and take the seven readings again; then fully up, and again.",
         "Twenty-one readings for the left motor.", ""),
        ("CK08: ohm the right motor",
         "The same on plug E-04: seven readings parked, half-raised and raised.",
         "Twenty-one readings for the right motor.", ""),
        ("CK08: the powered test",
         "Battery negative back on. One motor at a time, on the motor side of its plug: 12 V from the fused lead to WR and a jumper from the motor's case to ground. Touch a second 12 V lead to R alone: note which way the lamp moves and whether it stops by itself. Take it off. Touch it to RY alone: note the same. While the motor runs, read the volts on YG.",
         "R raises the lamp and it stops at the top; RY lowers it and it stops at the bottom; YG shows about 12 V only while it moves.",
         "Hands and leads out of the bucket and the linkage. If the motor does not stop within a few seconds, take the 12 V off. The record gives no fuse size for this test: start with a small fuse and go up only if it blows on starting."),
        ("CK08: the two currents",
         "Put the ammeter in the WR feed. Read the current with the motor stopped on its cam and the same command still applied (12 V left on R with the lamp already up). Then read it while the lamp travels. Do both motors.",
         "Two figures per motor: stopped (idle) and travelling. They set the pop-up cycle's current threshold.", ""),
        ("CK09: ohm the wiper motor",
         "Battery negative off. Unplug the wiper motor's four-way D-02 and its single B plug. On the motor side, arms parked, read ohms: L to case, LB to case, L to LB, L to LW, L to LR, B to case. Then replug, battery on, run the wipers and switch the key off when the arms are mid-screen; battery negative off, unplug, and take the six readings again.",
         "Twelve readings. The record expects LB joined to L at park and to B away from park, and B joined to the case.", ""),
        ("CK09: power the wiper motor",
         "Arms lifted off the glass or the glass wet. On the motor side: 12 V from the fused lead on LW, and L to ground. Note whether it runs.",
         "It runs, or it does not - either is the answer.",
         "The arms sweep: keep clear."),
        ("CK10: does IG hold through START",
         "Plugs back on, battery on, lever in P. Meter on DC volts, black probe on a good ground, red probe on the ignition switch's IG wire. The diagram colours it BY, and the START wire may be BY as well: IG is the one that goes live at RUN. Turn the key OFF, ACC, RUN, then hold START. If the switch's wires cannot be reached with the column covers on, do this straight after the next step.",
         "About 12 V at RUN that stays there while the key is held at START.",
         "The engine cranks and may start. Lever in P, nobody in front of the car."),
        ("Take the column covers off",
         "The steering column's upper and lower covers. The screws are not in the record: bag and label them as you find them.",
         "The backs of the stalk switches and their plugs in view.", ""),
        ("CK17: the light switch's contact table",
         "Battery negative off. Unplug the light switch's two plugs E-01 (2-pin: R, WG; 6-pin: RG, RW, R, RL, RY, GL). On the switch side, with the meter on continuity, find every pair of terminals that is joined - in OFF, PARK, HEAD low and HEAD high, each once with the stalk released and once pulled to PASS.",
         "A table of joined pairs for eight cases. The 1980 table shows PASS closing the same contact as HIGH, not one of its own.",
         "R and WG are live with the key out until the battery is off."),
        ("CK18: the turn and hazard switch",
         "Unplug F-02 (WG, GY, GW, GB, GR, GO). On the switch side find every joined pair with the stalk LEFT, in neutral, RIGHT, and with the hazard switch ON.",
         "A table for four cases. The 1980 table shows no contact to ground at OFF and three terminals joined by the hazard switch.", ""),
        ("CK18: the wiper switch",
         "Unplug D-03 (B, LO, LY, LR, LG, LW). Find every joined pair in OFF, INT, LOW, HIGH, and with the washer pressed.",
         "A table for five cases.", ""),
        ("Put it back as it was",
         "Refit every plug until it latches. Battery negative on. Check the lights, the stalks and the wipers work as before. Leave the column covers off if the strip (S1) follows; bag their screws.",
         "The car works as it did this morning.", ""),
        ("Enter the readings",
         "Tick V-114 and type each check's readings, starting each block with its number.",
         "Eleven blocks of readings in the app.", ""),
    ],
))


# ------------------------------------------------------------------ Y48 (D-561): the display bridge board's order
BR = _csv("00-design", "bench-revA-bridge-digikey-cart.csv")
ROWS.append(dict(
    id="Y48",
    goal="The display bridge board and its parts are ordered: five boards from the fab and the fourteen lines of its Digi-Key file - in the same carts as Y18 if those are not paid yet.",
    where="desk",
    time="20 min",
    tools=["a browser and a card"],
    parts="P119",
    before=[
        "Y46 is done: the bridge board is drawn and its fab zip is in the tree",
        "Pull the tree first so the zip and the parts file are the latest",
    ],
    know=[
        "The bridge joins the BT817 board's flat-cable picture output to the HDMI input of the panel kit you chose: a TI TFP410 on a 62 x 46 mm two-layer board. [D-550; D-561; parts P119]",
        "Its fab zip is bridge-board-revA-gerbers.zip in the bridge board's fab folder under the design folder; its parts are bench-revA-bridge-digikey-cart.csv beside the design README: %d lines, %s by the file's estimates of %s. [D-561; the bridge's cart file]" % (len(BR), _money(_usd(BR)), PRICED),
        "Five boards is the least the fab sells; at this size they are about $5 before shipping, by estimate. [parts P119]",
        "The flat cable must have its contacts on the SAME side at both ends (type A). The other kind reverses every pin, and powering a reversed cable shorts the BT817 board's outputs. [D-561; the bridge README]",
        "The connector J1 must be the bottom-contact Hirose FH12-50S-0.5SH(55) or one with the same footprint and contact side: the pin mapping assumes it. [D-561]",
        "An HDMI lead from the bridge to the panel's driver board is not in the file: the panel kit may bring one; otherwise any short HDMI lead. [D-561; parts P118]",
    ],
    done_when="The fab order and the Digi-Key lines are paid for and the row is ticked.",
    if_not="A line out of stock: take the substitute the step names; where it names none, leave it out, pay for the rest and write the part number in the app. The fab's preview shows a wrong size or one copper layer: do not pay; tell the agent.",
    record="Tick Y48 when both are ordered. In words: what each came to, any substitute, and the delivery dates.",
    steps=[
        ("Pull the tree and find the two files",
         "git pull in ~/dev/Rx7. Under " + DESIGN + " the display unit's bridge-board folder has a fab folder with bridge-board-revA-gerbers.zip; beside the README in " + DESIGN + " is bench-revA-bridge-digikey-cart.csv.",
         "One zip and one parts file.", ""),
        ("Add the board at the fab",
         "On jlcpcb.com, in the same cart as Y18's boards if that order is not paid yet: add the zip, PCB Qty 5, 2 layers, 1.6 mm, 1 oz, green, HASL, Remove Mark - the same settings as the other four.",
         "A preview of a 62 x 46 mm board, 2 layers.",
         "A preview of another size means the wrong file: stop."),
        ("Load the parts at Digi-Key",
         "In the same cart as Y18's lines if it is not paid yet: upload bench-revA-bridge-digikey-cart.csv the same way (qty and mpn columns), or type each line: " + _list(BR) + ".",
         "%d lines, %s by the file's estimates." % (len(BR), _money(_usd(BR))),
         "The flat cable must be type A, contacts on the same side at both ends: read it on the listing before paying."),
        ("Take the substitutes where the cart has none",
         _subs(BR) + ".",
         "No line left at zero stock without a substitute or a note.", ""),
        ("Pay and enter it",
         "Pay both. Tick Y48 and write what each came to, any substitute and the delivery dates.",
         "Y48 ticked.", ""),
    ],
))

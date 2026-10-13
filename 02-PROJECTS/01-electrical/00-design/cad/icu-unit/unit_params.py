"""Every number of the ICU unit's mock-up (D-491, D-270, D-268; work row Y19). The ONE place numbers
live: `unit_lib.py` and `make_unit.py` hold no dimension of their own.

Each row of TABLE is (NAME, value, unit, what it is, confirm). `confirm` is empty for a number that
comes from a drawing or a ruling, and says why for a guess - which is most of them: nothing in the
car has been measured (R11), no display is chosen (P118), the eval board is not in hand (P117), so
every size here is provisional. Change a value, run

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd make_unit.py

and the whole unit rebuilds; a number that no longer fits comes back as a sentence naming the
parameter and which way to move it, never as a traceback.

Frame: X across the face (0 = the face's left edge seen from the driver's seat), Y = depth going back
from the bezel's front surface (Y = 0), Z up from the bezel's bottom edge. mm throughout.

What is NOT here, because it is read, never typed: the DT13 panel cut-outs (TE 114-151046, from
`../enclosure_lib.py` TE_CUTOUT), the carrier's outline, holes and connector positions
(`../icu-carrier/enclosure/board.json`), the DT13 bodies and every carrier part's 3D extent
(`probe.json` beside it, and the carrier's STEP when it is there).
"""

# The placing envelope: the binnacle aperture and the clear depth behind it (work rows C4 and
# M-1 / C1). None until Camden measures it; then a dict, and the build refuses a unit that does not
# go in:
#   {"OPENING_W": mm, "OPENING_H": mm, "DEPTH": mm clear straight back from the aperture's front}
ENVELOPE = None                      # C4, M-1 - confirm

# The display chain's other boards (chain ii, D-269; IC21): the BT817 eval board's RGB goes to a
# TFP410-class HDMI encoder (P119) and HDMI into the display's own scaler board (P118, "with its
# scaler board"), which drives the glass through its flex. They hang on the back of the display
# plate beside the BT817 board. No part is chosen: these are placeholder blocks, each
#   (name, what, w across, h up, depth back from the plate incl. mounts and plugs,
#    x0 = left edge from the inside of the left wall, z0 = bottom above the floor's inside or None
#    = as low as it goes clear of the carrier)
DRIVER_BOARDS = [
    ("HDMI bridge", "TFP410-class HDMI encoder (P119)", 50.0, 40.0, 20.0, 125.0, None),
    ("scaler", "the display's scaler board, HDMI in, flex out (P118)", 90.0, 60.0, 20.0, 181.0, None),
]

# The carrier's two DT13s, by reference, and the record's name for each (housings DP-ICU-A / -B).
CONNECTOR_NAMES = {"J1": "DP-ICU-A", "J3": "DP-ICU-B"}

TABLE = [
    # ----------------------------------------------------------------------- the face (bezel) --
    ("FACE_W", None, "mm", "bezel (face) width; None = derived: the display outline plus "
     "BEZEL_BORDER, or the body plus BEZEL_OVERLAP, or what the page button needs, per side",
     "the aperture is unmeasured (M-1 / C1)"),
    ("FACE_H", None, "mm", "bezel height; None = derived the same way. The unit is ONE height "
     "front to back and the face covers it, so it goes into the binnacle from the front",
     "the aperture is unmeasured (M-1 / C1)"),
    ("FACE_T", 3.0, "mm", "bezel plate thickness (P121, 3 mm black ABS or aluminium)",
     "P121 not bought; the luxury package's moulded bezel replaces it later (D-268)"),
    ("BEZEL_BORDER", 6.0, "mm", "least face beyond the display's outline, each side",
     "taste, and the aperture is unmeasured"),
    ("BEZEL_OVERLAP", 2.0, "mm", "how far the face stands proud of the body on every side, so it "
     "covers the aperture's edge like a head unit's bezel", "the aperture is unmeasured"),
    ("DISPLAY_CENTRED", False, "", "True = the display sits in the middle of the face (the face "
     "grows on both sides to match the wider one); False = each border is only what that side "
     "needs, so the page button's side is wider", "taste: his to say"),
    ("WINDOW_MARGIN", 0.5, "mm", "the bezel's window = the display's active area plus this, each "
     "side", "against the glass bought"),
    ("BEZEL_LEDGE", 1.0, "mm", "least the window stays inside the display's outline, each side: "
     "the bezel holds the glass by this ledge", "against the glass bought"),
    ("BEZEL_SCREWS_AT", [0.1, 0.5, 0.9], "", "the bezel's screws into the front frame: fractions "
     "along the frame's top and bottom bands (one screw at each, top and bottom)",
     "visible heads on the face: taste, and the luxury bezel may hide them"),
    ("BEZEL_SCREW_CLEAR", 2.4, "mm", "M2 clearance hole in the bezel", "screw not chosen"),
    ("BEZEL_PILOT", 1.8, "mm", "M2 thread-forming pilot into the frame's band", "screw not chosen"),
    ("BEZEL_PILOT_DEPTH", 6.0, "mm", "depth of that pilot", "screw not chosen"),
    ("BEZEL_SKIN", 0.5, "mm", "least plastic each side of a bezel pilot in the frame's band", ""),
    ("CONTROL_EDGE", 2.0, "mm", "least distance from the page button's head to the face's edge", ""),

    # --------------------------------------------------------------------- the display (P118) --
    ("DISP_W", 305.0, "mm", "display module outline, across (12.3-inch 1920 x 720 bar class)",
     "P118 not chosen (Y16)"),
    ("DISP_H", 122.0, "mm", "display module outline, up", "P118 not chosen (Y16)"),
    ("DISP_T", 8.0, "mm", "display module thickness, glass to back", "P118 not chosen (Y16)"),
    ("ACTIVE_W", 292.0, "mm", "active area across (1920 px at about 0.152 mm)",
     "P118 not chosen (Y16)"),
    ("ACTIVE_H", 109.5, "mm", "active area up (720 px)", "P118 not chosen (Y16)"),
    ("ACTIVE_DX", 0.0, "mm", "active area's centre right of the outline's centre",
     "P118 not chosen (Y16)"),
    ("ACTIVE_DZ", 1.0, "mm", "active area's centre above the outline's centre (the flex side's "
     "border carries the driver chips, so it is wider)", "P118 not chosen (Y16)"),
    ("DISP_CLEAR", 0.5, "mm", "play round the module in the front frame's pocket, each side", ""),
    ("DISP_TAPE", 0.5, "mm", "foam tape between the bezel's back and the glass", "tape not chosen"),
    ("DISP_BACK_CLEAR", 1.0, "mm", "display's back to the display plate (the front frame's back "
     "wall)", "the module's back is unmeasured"),
    ("FLEX_X", 0.0, "mm", "the display's flex: its centre right of the display's centre, on the "
     "bottom edge", "P118 not chosen (Y16)"),
    ("FLEX_W", 40.0, "mm", "the flex's width", "P118 not chosen (Y16)"),
    ("FLEX_ROOM", 3.0, "mm", "room under the display for the flex to turn back through the "
     "display plate", "P118 not chosen (Y16)"),
    ("FLEX_SLOT_CLEAR", 1.0, "mm", "the slot in the display plate: the flex plus this, each side", ""),
    ("FLEX_TO", "scaler", "", "the board the display's flex lands on: a DRIVER_BOARDS name, or "
     "'BT817' if the glass is driven from the eval board straight", "chain ii puts it on the "
     "scaler (D-269); the module bought decides"),

    # ---------------------------------------------- the display plate (the front frame's back) --
    ("BULKHEAD", 3.0, "mm", "the display plate: the front frame's back wall behind the display, "
     "which carries the BT817 board and the driver boards", ""),

    # ------------------------------------------------------------- the BT817 board (P117) --
    ("BT_W", 100.0, "mm", "BT817 eval board, across (Bridgetek ME817EV class)",
     "P117 not in hand"),
    ("BT_H", 76.0, "mm", "BT817 eval board, up", "P117 not in hand"),
    ("BT_T", 1.6, "mm", "its thickness", ""),
    ("BT_PARTS_H", 13.4, "mm", "its parts and connectors on the back (away from the display); "
     "board + parts = 15", "P117 not in hand"),
    ("BT_UNDER_H", 2.0, "mm", "its parts on the front, toward the display plate",
     "P117 not in hand"),
    ("BT_STANDOFF", 5.0, "mm", "display plate's back face to the board's front face", ""),
    ("BT_STANDOFF_D", 6.0, "mm", "standoff diameter (an M2.5 / M3 insert in each)", ""),
    ("BT_HOLE_INSET", 3.5, "mm", "its four corner holes, in from its corners", "P117 not in hand"),
    ("BT_X", None, "mm", "board centre from the inside of the left wall; None = CN8 straight over "
     "the carrier's J4 (the shortest ribbon), kept between the walls", ""),
    ("BT_Z", None, "mm", "board's bottom edge above the floor's inside; None = as low as it goes: "
     "GAP off the floor ('behind'), or GAP over the carrier's kept room ('below')", ""),
    ("BT_CN8", (0.0, 8.0), "mm", "CN8 (the 2 x 8 host header) centre from the board's "
     "bottom-centre: (right, up), on the back face", "CN8's place on the eval board (F11)"),
    ("CN8_W", 20.32, "mm", "CN8's footprint across (8 x 2.54)", ""),
    ("CN8_H", 5.08, "mm", "CN8's footprint up (2 x 2.54)", ""),
    ("CN8_T", 8.5, "mm", "CN8's height off the board", "P117 not in hand"),
    ("IDC_PLUG_H", 9.0, "mm", "a mated IDC plug on a header, beyond the header's top",
     "ribbon not bought"),
    ("IDC_GROW", 1.5, "mm", "the IDC plug's section = the header's plus this each side",
     "ribbon not bought"),

    # --------------------------------------------------------------------------- the carrier --
    ("CARRIER_LAYOUT", "behind", "", "'behind' = the carrier lies flat on the floor behind "
     "everything on the display plate; 'below' = it slides under the BT817 board, which then "
     "stands over its front part (shorter, taller inside)", "depth is C4's to say"),
    ("CARRIER_X", "left", "", "'left', 'centre', 'right' (against that wall with GAP; 'left' puts "
     "the XIAO's u.FL end at the left wall), or a number: the board's left edge from the inside of "
     "the left wall", ""),
    ("CARRIER_STEP", True, "", "use ../icu-carrier/icu-carrier.step when it is there; False = "
     "always the stand-in blocks from probe.json (faster, and what a clone without the STEP gets)",
     ""),
    ("CARRIER_FRONT_GAP", 4.0, "mm", "('behind') what is on the display plate to the carrier's "
     "front edge; ('below') the display plate to it. Never less than the lid's front beam needs "
     "for the carrier to drop in past it", ""),
    ("CARRIER_TOP_H", 20.0, "mm", "kept clear above the carrier (the Teensy on its socket 17.7, "
     "J4's mated IDC plug)", "the Teensy socket and the plug are not measured"),
    ("CARRIER_BOT_H", 3.0, "mm", "kept clear below the carrier (pin tails 1.8)", ""),
    ("BOSS_H", 5.0, "mm", "carrier bosses, floor to the carrier's underside", ""),
    ("BOSS_D", 8.0, "mm", "boss diameter", ""),

    # ---------------------------------------------------------------- the page button (P120) --
    ("BUTTON_X", None, "mm", "page button's centre right of the DISPLAY's centre (negative = "
     "left); None = just beside the display (BUTTON_GAP off its edge) on the carrier's side, "
     "for the shortest lead to SW1", "taste: his to place (IC22)"),
    ("BUTTON_Z", 0.0, "mm", "page button's centre above the display's centre",
     "taste: his to place (IC22)"),
    ("BUTTON_HOLE_D", 12.0, "mm", "its panel hole", "P120 not chosen (12 mm class)"),
    ("BUTTON_HEAD_D", 15.0, "mm", "its bezel ring on the face", "P120 not chosen"),
    ("BUTTON_PROUD", 2.5, "mm", "how far it stands in front of the face", "P120 not chosen"),
    ("BUTTON_BODY_D", 16.0, "mm", "the widest thing behind the face (its nut)", "P120 not chosen"),
    ("BUTTON_DEPTH", 30.0, "mm", "behind the bezel's back face: body, terminals and the lead's turn",
     "P120 not chosen"),
    ("BUTTON_GAP", 2.0, "mm", "least between the button (head or body) and the display's outline", ""),
    ("BUTTON_HOLE_CLEAR", 1.0, "mm", "round the button's body where it passes the display plate", ""),

    # ------------------------------------------------------------------------ the RF window --
    ("RF_REF", "U8", "", "the radio on the carrier (the XIAO ESP32-C3, IC24)", ""),
    ("RF_WINDOW_ON", "left", "", "the wall thinned to RF_WALL over the radio's span plus "
     "RF_KEEPOUT: 'left' / 'right' side wall, 'lid', 'floor' or 'rear' (plate). Its FPC antenna is "
     "stuck inside it", "where the binnacle leaves the radio a view (D-491)"),
    ("RF_KEEPOUT", 5.0, "mm", "the radio's keep-out: the window's margin, and no metal nearer the "
     "window than this (IC24)", ""),
    ("RF_WALL", 1.2, "mm", "the window's wall, printed 100 % solid (Y7)", ""),

    # ------------------------------------------------------------------------ the mated plugs --
    ("PLUG_L", 50.0, "mm", "a mated DT06 plug with its wedge and rear seal, from the rear plate's "
     "outer face", "no plug measured"),
    ("CABLE_BEND", 30.0, "mm", "room behind the plug for the 150 mm tail to turn",
     "no harness measured"),
    ("PLUG_GROW", 3.0, "mm", "the plug's section = TE's cut-out plus this on every side",
     "no plug measured"),
    ("PLUG_SIDE_CLEAR", 2.0, "mm", "least gap between two plugs side by side",
     "try it with the parts in hand"),

    # ------------------------------------------------------------------------------ the case --
    ("MATERIAL", "ASA", "", "the dash reaches 70 C (D-270); never PLA", ""),
    ("WALL", 3.0, "mm", "side walls and the front frame's ring", ""),
    ("FLOOR", 3.0, "mm", "floor", ""),
    ("LID", 3.0, "mm", "lid", ""),
    ("GAP", 1.0, "mm", "a board's or part's edge to the wall beside it", ""),
    ("TOP_GAP", 2.0, "mm", "tallest carrier part to the lid's underside", ""),
    ("RIM_H", 3.0, "mm", "the beam under the lid's front edge, straight behind the display plate", ""),
    ("PLATE", 3.0, "mm", "rear connector plate; TE allows 6.25 at most (114-151046 3.11)", ""),
    ("PLATE_LIP", 2.0, "mm", "floor and walls past the plate's outer face", ""),
    ("PLATE_EDGE", 3.0, "mm", "least plastic between a cut-out or screw hole and the plate's "
     "edge, or the next cut-out", ""),
    ("SLOT_DEPTH", 1.5, "mm", "the plate's channel into each side wall", ""),
    ("SLOT_CLEAR", 0.3, "mm", "play of the plate in its channel", ""),
    ("FLOOR_GROOVE", 1.0, "mm", "the plate's channel into the floor", ""),
    ("CUTOUT_CLEAR", 0.15, "mm", "added round TE's cut-out for the print, per side", ""),
    ("INSERT_BORE", 4.0, "mm", "bore for an M3 brass heat-set insert (Ruthex RX-M3x5.7 class)",
     "against the insert bought"),
    ("INSERT_DEPTH", 6.5, "mm", "depth of that bore", "against the insert bought"),
    ("INSERT_SKIN", 1.0, "mm", "least plastic left beyond the end of an insert bore", ""),
    ("SCREW_CLEAR", 3.4, "mm", "M3 clearance hole", ""),
    ("LUG_D", 9.0, "mm", "lid screw lugs, inside the side walls at the top", ""),
    ("LUG_EMBED", 1.5, "mm", "how far a lug's circle is sunk into its wall", ""),
    ("LUG_H", 10.0, "mm", "lug height below the lid", ""),
    ("LID_LUGS", [0.0, 1.0], "", "where the lugs stand along each side wall, as fractions of the "
     "run from the lid's front beam (0) to the rear plate (1)", ""),
    ("GASKET_GROOVE_W", 1.6, "mm", "lid's cord-gasket groove, width (as the other lids)", ""),
    ("GASKET_GROOVE_D", 1.2, "mm", "lid's cord-gasket groove, depth", ""),
    ("GASKET_R", 3.0, "mm", "gasket path's corner radius", ""),
    ("SIDE_SCREWS", [(30.0, 90.0), (80.0, 90.0)], "mm", "head-unit style side fixings: an insert "
     "boss inside each side wall at each (Y, Z) of the unit frame",
     "placeholders: what the unit fastens to in the binnacle is unmeasured (C4)"),
    ("SIDE_BOSS_D", 9.0, "mm", "side screw boss diameter", ""),
    ("SIDE_BOSS_L", 5.0, "mm", "how far a side screw boss stands in from the wall", ""),

    # ------------------------------------------------------------------- tolerances and slack --
    ("BOARD_JSON_EDGE", 0.05, "mm", "board.json's outline is the outside of KiCad's 0.1 mm "
     "Edge.Cuts line: half that width is taken off each side", ""),
    ("OUTLINE_TOL", 0.2, "mm", "a STEP solid no thicker than the board plus this is the board", ""),
    ("COURTYARD_MATCH", 0.5, "mm", "a STEP solid belongs to the footprint whose courtyard holds "
     "its centre, within this (as enclosure_lib.fit_check)", ""),
    ("SEAL_SQUEEZE_MAX", 0.6, "mm", "an overlap of a DT13 with the plate thinner than this is "
     "TE's flange seal being squeezed, which is what it is for", ""),
    ("DT13_FLANGE_T", 3.0, "mm", "a stand-in DT13's flange thickness (the stand-in only)", ""),
    ("VOLUME_EPS", 1e-4, "mm3", "an overlap smaller than this is numerical noise", ""),
    ("EPS", 1e-6, "mm", "slack when comparing two derived numbers", ""),
    ("OVERCUT", 1.0, "mm", "how far a cutting tool overshoots the face it cuts through", ""),
    ("VIEW_MARGIN", 8.0, "mm", "white space round the SVG views", ""),
    ("VIEW_STROKE", 0.25, "mm", "line width in the SVG views", ""),
    ("VIEW_DEFLECTION", 0.05, "mm", "how closely a curve is followed in the SVG views", ""),

    # ------------------------------------------------------------------------------ the tables --
    ("DRIVER_BOARDS", DRIVER_BOARDS, "mm", "the display chain's other boards (table above)",
     "chain ii's boards are not chosen (P118, P119)"),
    ("CONNECTOR_NAMES", CONNECTOR_NAMES, "", "the record's name for each DT13 (housings)", ""),
]

P = {name: value for (name, value, unit, what, confirm) in TABLE}
P["ENVELOPE"] = ENVELOPE
UNIT = {name: unit for (name, value, unit, what, confirm) in TABLE}
WHAT = {name: what for (name, value, unit, what, confirm) in TABLE}
CONFIRM = {name: confirm for (name, value, unit, what, confirm) in TABLE if confirm}
CONFIRM["ENVELOPE"] = "not measured (C4 depth, M-1 / C1 aperture)"

# The self-test (`freecadcmd selftest.py`): the default set and perturbed ones, each with the
# outcome it must have - "clear" (built, every check passes), "fails" (built, a check fails) or
# "refused" (a fit rule says no, in words). The self-test fails when an outcome differs, so an
# edit that changes what the model does is caught: if the change is meant, change the word here.
# Overrides replace whole values of P.
_TALL_BRIDGE = [("HDMI bridge", "TFP410-class HDMI encoder (P119)", 50.0, 40.0, 20.0, 30.0, 2.0),
                DRIVER_BOARDS[1]]
_LEFT_DRIVERS = [("HDMI bridge", "TFP410-class HDMI encoder (P119)", 50.0, 40.0, 20.0, 1.0, None),
                 ("scaler", "the display's scaler board, HDMI in, flex out (P118)", 90.0, 60.0,
                  20.0, 57.0, None)]
SELFTEST = [
    ("the defaults: carrier behind, one height, front install", {}, "clear"),
    ("a bigger display module, 320 x 130", {"DISP_W": 320.0, "DISP_H": 130.0}, "clear"),
    ("CARRIER_LAYOUT below: the carrier under the BT817 board", {"CARRIER_LAYOUT": "below"},
     "clear"),
    ("CARRIER_LAYOUT beside (not a choice)", {"CARRIER_LAYOUT": "beside"}, "refused"),
    ("WALL 2.5", {"WALL": 2.5}, "clear"),
    ("WALL 2.5, carrier below", {"WALL": 2.5, "CARRIER_LAYOUT": "below"}, "clear"),
    ("an aperture it slides into", {"ENVELOPE": {"OPENING_W": 335.0, "OPENING_H": 135.0,
                                                 "DEPTH": 220.0}}, "clear"),
    ("an aperture too shallow", {"ENVELOPE": {"OPENING_W": 335.0, "OPENING_H": 135.0,
                                              "DEPTH": 120.0}}, "refused"),
    ("a BT817 board 10 mm taller", {"BT_H": 86.0}, "clear"),
    ("a BT817 board 10 mm taller, carrier below", {"BT_H": 86.0, "CARRIER_LAYOUT": "below"},
     "clear"),
    ("the page button over the display", {"BUTTON_X": 100.0}, "refused"),
    ("the page button right of the display", {"BUTTON_X": 170.0}, "clear"),
    ("the page button under the display's right end, into the scaler",
     {"BUTTON_X": 120.0, "BUTTON_Z": -75.0}, "refused"),
    ("the page button above the display's right end", {"BUTTON_X": 120.0, "BUTTON_Z": 75.0},
     "clear"),
    ("the display centred on the face", {"DISPLAY_CENTRED": True}, "clear"),
    ("FACE_W 300, narrower than the display", {"FACE_W": 300.0}, "refused"),
    ("the carrier centred: the BT817 board follows J4 onto the driver boards",
     {"CARRIER_X": "centre"}, "refused"),
    ("the carrier hard right, the driver boards moved left: the button follows onto the BT817",
     {"CARRIER_X": "right", "DRIVER_BOARDS": _LEFT_DRIVERS}, "refused"),
    ("the carrier hard right, the driver boards moved left, the button left",
     {"CARRIER_X": "right", "DRIVER_BOARDS": _LEFT_DRIVERS, "BUTTON_X": -170.0}, "clear"),
    ("the RF window in the lid", {"RF_WINDOW_ON": "lid"}, "clear"),
    ("the RF window in the rear plate (DP-ICU-B stands in the way)", {"RF_WINDOW_ON": "rear"},
     "fails"),
    ("the RF window in the floor (the carrier's own copper in the way)",
     {"RF_WINDOW_ON": "floor"}, "fails"),
    ("a side screw boss in the RF window", {"SIDE_SCREWS": [(70.0, 20.0), (80.0, 90.0)]},
     "fails"),
    ("no driver boards: the brief's chain, the flex onto the BT817 board",
     {"DRIVER_BOARDS": [], "FLEX_TO": "BT817"}, "clear"),
    ("FLEX_TO a board that is not there", {"FLEX_TO": "decoder"}, "refused"),
    ("the HDMI bridge typed over the carrier, carrier below",
     {"CARRIER_LAYOUT": "below", "DRIVER_BOARDS": _TALL_BRIDGE}, "refused"),
    ("the drawn carrier without its STEP (stand-in blocks)", {"CARRIER_STEP": False}, "clear"),
    ("a nonsense value", {"WALL": -3.0}, "refused"),
]

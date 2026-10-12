"""Every number of the climate control unit's mock-up (D-479, D-480, work row Y14). The ONE place
numbers live: `unit_lib.py` and `make_unit.py` hold no dimension of their own.

Each row of TABLE is (NAME, value, unit, what it is, confirm). `confirm` is empty for a number that
comes from a drawing or a ruling, and says why for a guess - which is most of them: nothing in the
car has been measured (R11), so every size here is provisional. Change a value, run

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd make_unit.py

and the whole unit rebuilds; a number that no longer fits comes back as a sentence naming the
parameter and which way to move it, never as a traceback.

Frame: X across the face (0 = the face's left edge seen from the cabin), Y = depth going back from
the faceplate's front surface (Y = 0), Z up from the faceplate's bottom edge. mm throughout.

What is NOT here, because it is read, never typed: the DT13 panel cut-outs (TE 114-151046, from
`../enclosure_lib.py` TE_CUTOUT), the carrier's outline, holes and connector positions
(`../dcu-carrier/enclosure/board.json`) and the DT13 bodies' sizes (`probe.json` beside it, and the
carrier's STEP when it is there).
"""

# The placing envelope: the centre-stack opening and the room behind it (work rows V-113 / V-102).
# None until Camden measures it; then a dict, and the build refuses a unit that does not go in:
#   {"OPENING_W": mm, "OPENING_H": mm, "DEPTH": mm clear behind the opening's front edge,
#    "BEHIND_H": mm of height the box may have behind the dash, or None if unknown}
ENVELOPE = None                      # V-113 / V-102 - confirm

# The controls on the face, from the owner's sketch (ideas I-001 to I-006, a concept he is still
# playing with). The sketch is SKETCH_W x SKETCH_H = 180 x 60 with coordinates from its top-left;
# here x is from the face's centre line (sketch x - 90) and z is DOWN from the sketch's top edge.
# The 180 x 60 layout is kept whole, as one block, on whatever the face turns out to be: centred
# across it, and placed up and down it by CONTROLS_ANCHOR.
#   kind     what is cut in the faceplate          the placeholder solid
#   window   w x h opening                         a thin slab behind it (the display)
#   knob     KNOB_HOLE_D bushing hole              a cylinder d across, KNOB_PROUD in front
#   key      w x h + KEY_CLEAR a side              a cap w x h, KEY_PROUD in front
#   slot     w x h opening                         a paddle, PADDLE_PROUD in front
CONTROLS = [
    # name                 kind      x       z      size                       sketch (x, z)
    ("screen",            "window",   0.0, 15.0, {"w": 44.0, "h": 23.6}),   # top-left (68, 3.2)
    ("centre knob",       "knob",     0.0, 42.0, {"d": 20.0}),              # (90, 42)
    ("key upper left",    "key",    -22.3, 36.5, {"w": 13.0, "h": 8.0}),    # (67.7, 36.5)
    ("key upper right",   "key",     22.3, 36.5, {"w": 13.0, "h": 8.0}),    # (112.3, 36.5)
    ("key lower left",    "key",    -22.3, 47.5, {"w": 13.0, "h": 8.0}),    # (67.7, 47.5)
    ("key lower right",   "key",     22.3, 47.5, {"w": 13.0, "h": 8.0}),    # (112.3, 47.5)
    ("seat knob left",    "knob",   -50.0, 30.0, {"d": 22.0}),              # (40, 30)
    ("seat knob right",   "knob",    50.0, 30.0, {"d": 22.0}),              # (140, 30)
    ("window switch left",  "slot", -78.0, 30.0, {"w": 12.0, "h": 24.0}),   # (12, 30)
    ("window switch right", "slot",  78.0, 30.0, {"w": 12.0, "h": 24.0}),   # (168, 30)
]

# The upper connector row (D-480): (name, ways, fitted). The first stands directly above the lower
# connector UPPER_ABOVE; each next one steps toward the middle of the board. A position that is not
# fitted gets no cut-out - only a kept-clear zone inside and a scribed outline on the rear plate.
UPPER_CONNECTORS = [
    ("DP-DCU-D", 12, True),                    # the leads that used grommets (D-480, P194)
    ("left plate, idea I-002", 12, False),     # reserved: built only if he rules the plate
]

TABLE = [
    # ------------------------------------------------------------------------------ the face --
    ("SKETCH_W", 180.0, "mm", "width of the owner's sketch the control table was read from", ""),
    ("SKETCH_H", 60.0, "mm", "height of that sketch", ""),
    ("FACE_W", None, "mm", "faceplate width; None = derived, body width + 2 x BEZEL_OVERLAP. The "
     "sketch says 180, which the 180 mm carrier cannot go behind (see the width rule)",
     "the opening is unmeasured (V-113)"),
    ("FACE_H", None, "mm", "faceplate height; None = derived, the body's height + 2 x "
     "BEZEL_OVERLAP (or what the control block needs, if that is more), so the unit is ONE "
     "height front to back and goes into its opening from the front like a head unit (D-480: "
     "height is the dimension with room). A number lower than that builds the other unit: a "
     "front section the face's height and a step up behind it, which cannot go in from the "
     "front. The sketch says 60; the least the sketch's layout fits is 64 (at 60 the screen "
     "window's top 1.8 mm lies behind the box's roof)",
     "the opening is unmeasured (V-113); 60 in the sketch"),
    ("CONTROLS_ANCHOR", "centre", "", "where the sketch's control block sits on a taller face: "
     "'centre', 'top' or 'bottom'. Top and bottom put it as near that edge as the box's roof or "
     "floor behind the face allows", "taste: his to place"),
    ("FACE_T", 3.0, "mm", "faceplate thickness", "material and make not chosen (luxury LP20)"),
    ("BEZEL_OVERLAP", 2.0, "mm", "how far the faceplate stands proud of the body on every side, "
     "so it covers the edge of the dash opening like a head unit's bezel",
     "the opening is unmeasured (V-113)"),
    ("CONTROLS", CONTROLS, "mm", "the controls on the face (table above)",
     "a concept he is still changing (I-001 to I-006)"),
    ("KNOB_PROUD", 15.0, "mm", "how far a knob stands in front of the face", "no knob chosen"),
    ("KNOB_FLOAT", 0.5, "mm", "gap between the back of a knob and the face", "no knob chosen"),
    ("KNOB_HOLE_D", 9.5, "mm", "hole in the face for an encoder's bushing",
     "M9 bushing class (PEC11R); no part in hand"),
    ("KNOB_SHAFT_D", 6.0, "mm", "encoder shaft drawn through that hole", "no part in hand"),
    ("KEY_PROUD", 2.0, "mm", "how far a key cap stands in front of the face", "no key chosen"),
    ("KEY_CLEAR", 0.3, "mm", "gap around a key cap in its hole, per side", "no key chosen"),
    ("PADDLE_PROUD", 6.0, "mm", "how far a window switch paddle stands in front of the face",
     "no switch chosen"),
    ("PADDLE_CLEAR", 0.5, "mm", "gap around a paddle in its slot, per side", "no switch chosen"),
    ("SCREEN_T", 2.0, "mm", "thickness of the display slab drawn behind its window",
     "no display chosen"),
    ("SCREEN_BORDER", 0.0, "mm", "how far the display module reaches past its window, per side. "
     "0 = unknown: put the real border here and the fit rule says how much the face must grow",
     "no display chosen"),
    ("CONTROL_EDGE", 2.0, "mm", "least distance from a control to the edge of the face", ""),
    ("CONTROL_GAP", 1.0, "mm", "least distance between two controls", ""),
    ("CONTROL_BEHIND_CLEAR", 0.2, "mm", "least distance from a hole in the face to the inside "
     "of the box behind it (a hole over a wall is a hole onto plastic)", ""),

    # ----------------------------------------------------------------------- the panel board --
    ("PANEL_T", 1.6, "mm", "panel board thickness", ""),
    ("PANEL_GAP", 8.0, "mm", "faceplate's rear face to the panel board's front face",
     "set by the encoders and keys bought (the old tray used 7)"),
    ("PANEL_MARGIN", 6.0, "mm", "panel board outline = the face less this on every side. It "
     "cannot be less than BEZEL_OVERLAP + the wall + GAP, or the board is in the wall",
     "the board is redrawn to the face (panel/ is 200 x 70 today)"),
    ("PANEL_BACK_H", 16.0, "mm", "kept clear behind the panel board for its parts and the ribbon "
     "plug", "no placed board for this face yet"),
    ("PANEL_HOLE_INSET", 4.0, "mm", "panel board's four M3 holes, in from its corners", ""),
    ("PANEL_RIBBON_X", None, "mm", "ribbon header's centre on the panel board, X in the unit "
     "frame; None = straight in front of the carrier's J4", "no placed board for this face yet"),
    ("PANEL_RIBBON_Z", 16.0, "mm", "ribbon header's centre above the panel board's bottom edge",
     "no placed board for this face yet"),

    # --------------------------------------------------------------------------- the carrier --
    ("CARRIER_W", 180.0, "mm", "DCU carrier width. When this and CARRIER_D are the drawn board's "
     "(board.json) the real board and its STEP are used; any other value builds a plain slab "
     "with the three connectors kept at their spacing and centred on it",
     "provisional outline until V-102 (D-455)"),
    ("CARRIER_D", 80.0, "mm", "DCU carrier depth, front edge to connector edge",
     "provisional outline until V-102 (D-455)"),
    ("CARRIER_T", 1.6, "mm", "carrier thickness", ""),
    ("CARRIER_STEP", True, "", "use ../dcu-carrier/dcu-carrier.step when it is there and the "
     "carrier is the drawn board; False = always the stand-in blocks (faster, and what a clone "
     "without the STEP gets)", ""),
    ("CARRIER_FRONT_GAP", 4.0, "mm", "panel keep-out to the carrier's front edge, at the least. "
     "In the one-height unit the carrier stands further back if it must, to drop in behind the "
     "beam under the lid's front edge (the report says by how much)", ""),
    ("CARRIER_TOP_H", 18.0, "mm", "kept clear above the carrier (the socketed Teensy, the mated "
     "ribbon plug)", "the Teensy on its socket and the IDC plug are not measured"),
    ("CARRIER_BOT_H", 3.0, "mm", "kept clear below the carrier (pin tails, the bottom-side "
     "parts)", ""),
    ("CARRIER_HOLE_INSET", 4.0, "mm", "the four corner holes of a stand-in carrier (the drawn "
     "board's own holes are read from board.json)", ""),

    # ------------------------------------------------------------------------- the upper row --
    ("UPPER_CONNECTORS", UPPER_CONNECTORS, "", "the upper row's positions (table above)", ""),
    ("UPPER_ABOVE", "J9", "", "the lower connector the first upper position stands above", ""),
    ("UPPER_T", 1.6, "mm", "upper connector board thickness", ""),
    ("UPPER_W", 130.0, "mm", "upper connector board width", "not drawn yet (Y15)"),
    ("UPPER_D", 30.0, "mm", "upper connector board depth; its connector edge is flush with the "
     "carrier's", "not drawn yet (Y15)"),
    ("ROW_PITCH", 42.0, "mm", "upper board above the carrier, face to like face = connector row "
     "to connector row. The brief's 32 does not build: a DT13 stands 37.8 mm above its board's "
     "underside, so the upper board must be at least that plus UPPER_BOT_H up",
     "a mated DT06 plug in each row must clear the other row - try it with the parts in hand"),
    ("UPPER_BOT_H", 2.5, "mm", "kept clear under the upper board (its DT13's pin tails stand "
     "1.5 mm through)", "from TE's model, not a part"),
    ("UPPER_CONN_GAP", 2.0, "mm", "between two upper connectors' footprints, side by side", ""),
    ("UPPER_STANDOFFS", [(4.3, 3.3), (115.8, 3.3)], "mm", "the two standoffs that carry the "
     "upper board from the carrier: (along the upper board from its DP-DCU-D end, back from its "
     "front edge)", "the carrier rev 0.04 has no holes for them; these spots are clear of its "
     "parts but not of its tracks (Y15)"),
    ("UPPER_STANDOFF_D", 6.0, "mm", "standoff diameter", ""),

    # ------------------------------------------------------------------------ the mated plugs --
    ("PLUG_L", 50.0, "mm", "a mated DT06 plug with its wedge and rear seal, from the rear "
     "plate's outer face", "no plug measured"),
    ("CABLE_BEND", 30.0, "mm", "room behind the plug for 16 AWG to turn", "no harness measured"),
    ("PLUG_GROW", 3.0, "mm", "the plug's section = TE's cut-out plus this on every side",
     "no plug measured"),
    ("PLUG_ROW_CLEAR", 3.0, "mm", "least gap between a plug in one row and a plug in the other "
     "(a thumb on the latch)", "try it with the parts in hand"),
    ("PLUG_SIDE_CLEAR", 2.0, "mm", "least gap between two plugs side by side",
     "try it with the parts in hand"),

    # ------------------------------------------------------------------------------ the case --
    ("MATERIAL", "ASA", "", "as the other boxes: the dash reaches 70 C (D-270); never PLA", ""),
    ("WALL", 3.0, "mm", "side walls and the step wall", ""),
    ("FLOOR", 3.0, "mm", "floor", ""),
    ("LID", 3.0, "mm", "lid, and the front section's roof", ""),
    ("GAP", 1.0, "mm", "a board's edge to the wall beside it", ""),
    ("TOP_GAP", 2.0, "mm", "tallest part to the lid's underside", ""),
    ("BOSS_H", 5.0, "mm", "carrier bosses, floor to the carrier's underside", ""),
    ("BOSS_D", 8.0, "mm", "boss diameter", ""),
    ("FRONT_L", 25.0, "mm", "ONLY for the stepped unit (a typed FACE_H lower than the body): "
     "length of the low front section behind the faceplate, the part that sits in the dash "
     "opening. The one-height unit has no step wall and does not use it", "the opening's lip "
     "depth is unmeasured (V-113)"),
    ("FRAME_D", 6.0, "mm", "depth of the front frame's ring behind the faceplate", ""),
    ("RIM_H", 3.0, "mm", "height of the beam the lid's front edge lands on. In the one-height "
     "unit it hangs under the roof, straight behind the room kept for the panel board", ""),
    ("STANDOFF_D", 8.0, "mm", "front frame's standoffs, faceplate to panel board", ""),
    ("WEB", 4.0, "mm", "the webs that join those standoffs to the frame", ""),
    ("PLATE", 3.0, "mm", "rear connector plate; TE allows 6.25 at most (114-151046 3.11)", ""),
    ("PLATE_LIP", 2.0, "mm", "floor and walls past the plate's outer face", ""),
    ("PLATE_EDGE", 3.0, "mm", "least plastic between a cut-out or screw hole and the plate's "
     "edge, or the next cut-out", ""),
    ("SLOT_DEPTH", 1.5, "mm", "the plate's channel into each side wall", ""),
    ("SLOT_CLEAR", 0.3, "mm", "play of the plate in its channel", ""),
    ("FLOOR_GROOVE", 1.0, "mm", "the plate's channel into the floor", ""),
    ("CUTOUT_CLEAR", 0.15, "mm", "added round TE's cut-out for the print, per side", ""),
    ("RESERVED_MARK_W", 0.6, "mm", "width of the scribed outline of a reserved cut-out", ""),
    ("RESERVED_MARK_D", 0.4, "mm", "depth of that scribe", ""),
    ("INSERT_BORE", 4.0, "mm", "bore for an M3 brass heat-set insert (Ruthex RX-M3x5.7 class)",
     "against the insert bought"),
    ("INSERT_DEPTH", 6.5, "mm", "depth of that bore", "against the insert bought"),
    ("INSERT_SKIN", 1.0, "mm", "least plastic left beyond the end of an insert bore", ""),
    ("SCREW_CLEAR", 3.4, "mm", "M3 clearance hole", ""),
    ("LUG_D", 9.0, "mm", "lid screw lugs: diameter. They stand INSIDE the side walls at the top "
     "of the rear section, so nothing sticks out of the box's sides", ""),
    ("LUG_EMBED", 1.5, "mm", "how far a lug's circle is sunk into its wall", ""),
    ("LUG_H", 10.0, "mm", "lug height below the lid", ""),
    ("LID_LUGS", [0.0, 1.0], "", "where the lugs stand along each side wall, as fractions of the "
     "run from the step wall (0) to the rear plate (1)", ""),
    ("GASKET_GROOVE_W", 1.6, "mm", "lid's cord-gasket groove, width (as the other lids)", ""),
    ("GASKET_GROOVE_D", 1.2, "mm", "lid's cord-gasket groove, depth", ""),
    ("GASKET_R", 3.0, "mm", "gasket path's corner radius", ""),
    ("SIDE_SCREWS", [(50.0, 40.0), (100.0, 40.0)], "mm", "head-unit style side fixings: an "
     "insert boss inside each side wall at each (Y, Z) of the unit frame",
     "placeholders: what the unit fastens to is unmeasured (V-113, V-102)"),
    ("SIDE_BOSS_D", 9.0, "mm", "side screw boss diameter", ""),
    ("SIDE_BOSS_L", 5.0, "mm", "how far a side screw boss stands in from the wall", ""),

    # ------------------------------------------------------------------- tolerances and slack --
    ("OUTLINE_TOL", 0.2, "mm", "CARRIER_W / CARRIER_D within this of board.json = the drawn "
     "board", ""),
    ("BOARD_JSON_EDGE", 0.05, "mm", "board.json's outline is the outside of KiCad's 0.1 mm "
     "Edge.Cuts line: half that width is taken off each side", ""),
    ("COURTYARD_MATCH", 0.5, "mm", "a STEP solid belongs to the footprint whose courtyard holds "
     "its centre, within this (as enclosure_lib.fit_check)", ""),
    ("SEAL_SQUEEZE_MAX", 0.6, "mm", "an overlap of a DT13 with the plate thinner than this is "
     "TE's flange seal being squeezed, which is what it is for", ""),
    ("VOLUME_EPS", 1e-4, "mm3", "an overlap smaller than this is numerical noise", ""),
    ("EPS", 1e-6, "mm", "slack when comparing two derived numbers", ""),
    ("OVERCUT", 1.0, "mm", "how far a cutting tool overshoots the face it cuts through (no "
     "effect on the result)", ""),
    ("VIEW_MARGIN", 8.0, "mm", "white space round the SVG views", ""),
    ("VIEW_STROKE", 0.25, "mm", "line width in the SVG views", ""),
    ("VIEW_DEFLECTION", 0.05, "mm", "how closely a curve is followed in the SVG views", ""),
]

P = {name: value for (name, value, unit, what, confirm) in TABLE}
P["ENVELOPE"] = ENVELOPE
UNIT = {name: unit for (name, value, unit, what, confirm) in TABLE}
WHAT = {name: what for (name, value, unit, what, confirm) in TABLE}
CONFIRM = {name: confirm for (name, value, unit, what, confirm) in TABLE if confirm}
CONFIRM["ENVELOPE"] = "not measured (V-113, V-102)"

# The self-test (`freecadcmd selftest.py`): the default set and perturbed ones, each with the
# outcome it must have - "clear" (built, every check passes), "fails" (built, a check fails) or
# "refused" (a fit rule says no, in words). The self-test fails when an outcome differs, so an
# edit that changes what the model does is caught: if the change is meant, change the word here.
# Overrides replace whole values of P.
_BOTH = [("DP-DCU-D", 12, True), ("left plate, idea I-002", 12, True)]
SELFTEST = [
    ("the defaults: FACE_H None, one height, front install", {}, "clear"),
    ("FACE_W 180, the sketch's width", {"FACE_W": 180.0}, "refused"),
    ("FACE_W 200", {"FACE_W": 200.0}, "clear"),
    ("FACE_H 64: the stepped unit", {"FACE_H": 64.0}, "clear"),
    ("FACE_H 70: stepped", {"FACE_H": 70.0}, "clear"),
    ("FACE_H 60, the sketch's height", {"FACE_H": 60.0}, "refused"),
    ("FACE_H 50", {"FACE_H": 50.0}, "refused"),
    ("FACE_H 62 with the control block anchored top", {"FACE_H": 62.0, "CONTROLS_ANCHOR": "top"},
     "clear"),
    ("FACE_H 95: a step lower than the lid's beam", {"FACE_H": 95.0}, "refused"),
    ("FACE_H 100: taller than the body needs, one height", {"FACE_H": 100.0}, "clear"),
    ("CONTROLS_ANCHOR top", {"CONTROLS_ANCHOR": "top"}, "clear"),
    ("CONTROLS_ANCHOR bottom", {"CONTROLS_ANCHOR": "bottom"}, "clear"),
    ("CONTROLS_ANCHOR left (not a choice)", {"CONTROLS_ANCHOR": "left"}, "refused"),
    ("ROW_PITCH 28", {"ROW_PITCH": 28.0}, "refused"),
    ("ROW_PITCH 32, the brief's", {"ROW_PITCH": 32.0}, "refused"),
    ("ROW_PITCH 40", {"ROW_PITCH": 40.0}, "refused"),
    ("ROW_PITCH 50", {"ROW_PITCH": 50.0}, "clear"),
    ("the reserved upper connector fitted", {"UPPER_CONNECTORS": _BOTH}, "clear"),
    ("no upper row at all: the control block sets the face", {"UPPER_CONNECTORS": []}, "clear"),
    ("the drawn carrier without its STEP (stand-in blocks)", {"CARRIER_STEP": False}, "clear"),
    ("carrier 170 wide", {"CARRIER_W": 170.0}, "fails"),
    ("carrier 160 wide", {"CARRIER_W": 160.0}, "refused"),
    ("PANEL_GAP 12", {"PANEL_GAP": 12.0}, "clear"),
    ("PANEL_MARGIN 3, the brief's", {"PANEL_MARGIN": 3.0}, "refused"),
    ("FRONT_L 40 on the one-height unit (not used there)", {"FRONT_L": 40.0}, "clear"),
    ("FRONT_L 40 on the stepped unit", {"FACE_H": 64.0, "FRONT_L": 40.0}, "refused"),
    ("a side screw boss put where the carrier is", {"SIDE_SCREWS": [(50.0, 12.0), (100.0, 40.0)]},
     "fails"),
    ("an opening it slides into", {"ENVELOPE": {"OPENING_W": 190.0, "OPENING_H": 95.0,
                                                "DEPTH": 210.0, "BEHIND_H": None}}, "clear"),
    ("the stepped unit, height only behind the dash",
     {"FACE_H": 64.0, "ENVELOPE": {"OPENING_W": 190.0, "OPENING_H": 62.0, "DEPTH": 210.0,
                                   "BEHIND_H": 100.0}}, "clear"),
    ("an opening too shallow and too low", {"ENVELOPE": {"OPENING_W": 190.0, "OPENING_H": 62.0,
                                                         "DEPTH": 150.0, "BEHIND_H": None}},
     "refused"),
    ("a nonsense value", {"WALL": -3.0}, "refused"),
]

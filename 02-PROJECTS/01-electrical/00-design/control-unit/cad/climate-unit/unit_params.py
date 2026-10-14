"""Every number of the climate control unit's mock-up (D-479, D-480, work row Y14; the case toward
the head unit, D-542, work row Y40). The ONE place numbers live: `unit_lib.py` and `make_unit.py`
hold no dimension of their own.

Each row of TABLE is (NAME, value, unit, what it is, confirm). `confirm` is empty for a number that
comes from a drawing or a ruling, and says why for a guess - which is most of them: nothing in the
car has been measured (R11), so every size here is provisional. Change a value, run

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd make_unit.py

and the whole unit rebuilds; a number that no longer fits comes back as a sentence naming the
parameter and which way to move it, never as a traceback.

Frame: X across the face (0 = the face's left edge seen from the cabin), Y = depth going back from
the faceplate's front surface (Y = 0), Z up from the faceplate's bottom edge. mm throughout.

What is NOT here, because it is read, never typed: the DT13 panel cut-outs (TE 114-151046, from
`../../../tools/enclosure_lib.py` TE_CUTOUT), the carrier's outline, holes and connector positions
(`../dcu-carrier/enclosure/board.json`) and the DT13 bodies' sizes (`probe.json` beside it, and the
carrier's STEP when it is there). The panel board's outline IS typed (PANEL_W, PANEL_H) and held to
`../panel/panel.kicad_pcb`: the report says so when the two differ.
"""

# The placing envelope: an opening and the room behind it. D-542 dropped the measurements that
# would have filled it (V-113, V-102: the dash plastic is rebuilt round the units, so no opening
# is a gate). It stays None; a dict still makes the build refuse a unit that does not go in:
#   {"OPENING_W": mm, "OPENING_H": mm, "DEPTH": mm clear behind the opening's front edge,
#    "BEHIND_H": mm of height the box may have behind the dash, or None if unknown}
ENVELOPE = None                      # not a gate (D-542) - confirm

# The head unit this case is made like (D-542, work row Y40): luxury parts LP55, the Pioneer
# DMH-W4660NEX, double-DIN. Every figure is a PUBLISHED one, never the unit in hand (R11), so
# every row is confirm; what Pioneer does not publish is None until it is measured on the unit.
# The case rows below refer to these by name (_HU): a head-unit number is typed once, here.
_OPM = ("Pioneer's Operation Manual for DMH-WT8600NEX / WT7600NEX / WC6600NEX / W4660NEX / "
        "W4600NEX (<OPM_DMHWC6600NEXUC_EN_B>), p.137 Specifications, 'Dimensions (W x H x D)', "
        "the copy at customsounds.com/uploads/docs/6dad08ed81235bfb15502a0ddf10131925fedebb.pdf "
        "read 2026-10-13")
_PUBLISHED = "a published sheet, not the unit in hand: measure it when it is bought"
_UNPUBLISHED = ("not published: Pioneer's Installation Manual for this model was not found "
                "(2026-10-13) and its Operation Manual does not give it - measure on the unit")
HEAD_UNIT = [
    ("HEAD_UNIT_CHASSIS_W", 178.0, "mm", "head unit's chassis width: 'Chassis (D): 178 mm x "
     "100 mm x 87 mm (7 in. x 3-7/8 in. x 3-3/8 in.)' - " + _OPM, _PUBLISHED),
    ("HEAD_UNIT_CHASSIS_H", 100.0, "mm", "head unit's chassis height (the same line)", _PUBLISHED),
    ("HEAD_UNIT_CHASSIS_D", 87.0, "mm", "head unit's chassis depth, behind the nose (the same "
     "line)", _PUBLISHED),
    ("HEAD_UNIT_NOSE_W", 171.0, "mm", "head unit's nose (its face) width: 'Nose: 171 mm x 97 mm "
     "x 3 mm (6-3/4 in. x 3-7/8 in. x 1/8 in.)' - the same page. So the nose is set in from the "
     "chassis by 3.5 mm a side", _PUBLISHED),
    ("HEAD_UNIT_NOSE_H", 97.0, "mm", "head unit's nose height (the same line): set in 1.5 mm top "
     "and bottom", _PUBLISHED),
    ("HEAD_UNIT_NOSE_D", 3.0, "mm", "how far the nose stands in front of the chassis (the same "
     "line)", _PUBLISHED),
    ("HEAD_UNIT_NOSE_R", None, "mm", "corner radius of the nose; None = unknown, and the case "
     "uses FACE_R until it is given", _UNPUBLISHED),
    ("HEAD_UNIT_SIDE_SCREW_D", 5.0, "mm", "thread of the screws into the chassis's sides (ISO "
     "side mount): M5. Source is weak: a retailer's box list, 'Pan-head ISO screws (M5 x 9mm)', "
     "seen only as a web search's summary on 2026-10-13 (the page would not open), and Pioneer's "
     "installation manuals for its other receivers, which fasten the sides with 5 mm screws",
     "not from Pioneer's sheet for this model: try the screw in the unit"),
    ("HEAD_UNIT_SIDE_HOLES", None, "mm", "the side-mount holes one side of the chassis carries, "
     "as a list of (back from the chassis's front face, up from its underside); None = unknown, "
     "and the case uses SIDE_SCREWS until it is given", _UNPUBLISHED),
    ("HEAD_UNIT_SLEEVE", False, "", "does it mount in a DIN sleeve? False: fastened by its side "
     "screws. onlinecarstereo.com's box list for it (read 2026-10-13) has installation screws "
     "and no sleeve or trim ring", "a retailer's list, not Pioneer's Installation Manual"),
]
_HU = {row[0]: row[1] for row in HEAD_UNIT}

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
    ("DP-DCU-E", 12, True),                    # the left plate's link (D-492, P200) - fitted since he ruled the plate
]

TABLE = HEAD_UNIT + [
    # ------------------------------------------------------------------------------ the face --
    ("SKETCH_W", 180.0, "mm", "width of the owner's sketch the control table was read from", ""),
    ("SKETCH_H", 60.0, "mm", "height of that sketch", ""),
    ("FACE_W", None, "mm", "faceplate width; None = derived, body width + 2 x BEZEL_OVERLAP_X: "
     "181 = the 188 body less the head unit's 3.5 a side, 10 wider than its nose because the "
     "body is 10 wider than its chassis. The sketch says 180, which the 180 mm carrier and the "
     "180 mm panel board cannot go behind (see the width rule)",
     "follows the head unit's published sizes (D-542)"),
    ("FACE_H", _HU["HEAD_UNIT_NOSE_H"], "mm", "faceplate height = the head unit's nose "
     "(HEAD_UNIT_NOSE_H, D-542), so the two faces read as a pair. The body behind it is then "
     "FACE_H - 2 x BEZEL_OVERLAP_Z = 100, the head unit's chassis height: 7.24 more than the "
     "two rows need on bosses of 5, which BOSS_H shares out. None = derived, the body's height + 2 x BEZEL_OVERLAP_Z (or what the "
     "control block needs, if that is more). Either way the unit is ONE height front to back "
     "and goes in from the front like a head unit (D-480). A number lower than the body needs "
     "builds the other unit: a front section the face's height and a step up behind it, which "
     "cannot go in from the front. The sketch says 60; under a face standing 2 proud the least "
     "the sketch's layout fits is 64",
     "follows the head unit's published size (D-542); 60 in the sketch"),
    ("CONTROLS_ANCHOR", "centre", "", "where the sketch's control block sits on a taller face: "
     "'centre', 'top' or 'bottom'. Top and bottom put it as near that edge as the box's roof or "
     "floor behind the face allows", "taste: his to place"),
    ("FACE_T", _HU["HEAD_UNIT_NOSE_D"], "mm", "faceplate thickness = how far the head unit's "
     "nose stands in front of its chassis (HEAD_UNIT_NOSE_D), so the two faces are in one plane "
     "when the two bodies' fronts are", "follows the head unit's published size (D-542); "
     "material and make not chosen (luxury LP20)"),
    ("BEZEL_OVERLAP_X", (_HU["HEAD_UNIT_NOSE_W"] - _HU["HEAD_UNIT_CHASSIS_W"]) / 2.0, "mm",
     "how far the faceplate reaches past the body at each side. NEGATIVE = the face is set in "
     "from the body, as the head unit's nose is from its chassis: (HEAD_UNIT_NOSE_W - "
     "HEAD_UNIT_CHASSIS_W) / 2 = -3.5, so the dash plastic covers both units' edges the same "
     "way (D-542). Positive = the face stands proud and covers the opening's edge itself",
     "follows the head unit's published sizes (D-542)"),
    ("BEZEL_OVERLAP_Z", (_HU["HEAD_UNIT_NOSE_H"] - _HU["HEAD_UNIT_CHASSIS_H"]) / 2.0, "mm",
     "the same at the top and the bottom: (HEAD_UNIT_NOSE_H - HEAD_UNIT_CHASSIS_H) / 2 = -1.5",
     "follows the head unit's published sizes (D-542)"),
    ("FACE_R", 2.0, "mm", "faceplate's corner radius, used while HEAD_UNIT_NOSE_R is None; when "
     "that is measured it is used instead. 0 = square", "a guess: the head unit's is not "
     "published"),
    ("FRAME_LAND", 1.5, "mm", "least width of front frame behind the faceplate's edge, all "
     "round: what the faceplate's rim rests on. Where the face is set in further than the wall "
     "is thick (3.5 a side against WALL 3) the frame's opening is this much inside the face's "
     "edge instead of flush with the body's inside", ""),
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
    ("PANEL_W", 180.0, "mm", "panel board width AS DRAWN (../panel/panel.kicad_pcb, Edge.Cuts "
     "180 x 84.76; D-542: the boards stay as drawn). The board is centred on the face, and the "
     "sketch's control block on the board, so its switches meet their holes. None = a board not "
     "drawn yet: the face less PANEL_MARGIN a side", ""),
    ("PANEL_H", 84.76, "mm", "panel board height as drawn (the same outline). None = the face "
     "less PANEL_MARGIN top and bottom", ""),
    ("PANEL_MARGIN", 6.0, "mm", "ONLY while PANEL_W / PANEL_H are None: panel board outline = "
     "the face less this on every side. It cannot be less than the face's overlap + the wall + "
     "GAP, or the board is in the wall", "the drawn board was sized by this under a 192 x 96.76 "
     "face"),
    ("PANEL_BACK_H", 16.0, "mm", "kept clear behind the panel board for its parts and the ribbon "
     "plug", "no placed board for this face yet"),
    ("PANEL_HOLE_INSET", 4.0, "mm", "panel board's four M3 holes, in from its corners", ""),
    ("PANEL_RIBBON_X", None, "mm", "ribbon header's centre on the panel board, X in the unit "
     "frame; None = straight in front of the carrier's J4", "no placed board for this face yet"),
    ("PANEL_RIBBON_Z", 16.5, "mm", "ribbon header's centre above the panel board's bottom edge",
     "no placed board for this face yet"),

    # --------------------------------------------------------------------------- the carrier --
    ("CARRIER_W", 180.0, "mm", "DCU carrier width. When this and CARRIER_D are the drawn board's "
     "(board.json) the real board and its STEP are used; any other value builds a plain slab "
     "with the three connectors kept at their spacing and centred on it",
     "the outline as drawn (D-455), and the board stays as drawn (D-542); no part in hand"),
    ("CARRIER_D", 80.0, "mm", "DCU carrier depth, front edge to connector edge",
     "the outline as drawn (D-455), and the board stays as drawn (D-542); no part in hand"),
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
    ("UPPER_W", 130.0, "mm", "upper connector board width", "Y15's board: 130 x 36, upper-board/"),
    ("UPPER_D", 36.0, "mm", "upper connector board depth; its connector edge is flush with the "
     "carrier's", "Y15: 36, not the 30 first guessed - the headers need the room in front of the DT13 keep-out"),
    ("ROW_PITCH", 42.0, "mm", "upper board above the carrier, face to like face = connector row "
     "to connector row. The brief's 32 does not build: a DT13 stands 37.8 mm above its board's "
     "underside, so the upper board must be at least that plus UPPER_BOT_H up",
     "a mated DT06 plug in each row must clear the other row - try it with the parts in hand"),
    ("UPPER_BOT_H", 2.5, "mm", "kept clear under the upper board (its DT13's pin tails stand "
     "1.5 mm through)", "from TE's model, not a part"),
    ("UPPER_CONN_GAP", 2.0, "mm", "between two upper connectors' footprints, side by side", ""),
    ("UPPER_STANDOFFS", [(4.3, 8.5), (115.8, 8.5)], "mm", "the two standoffs that carry the "
     "upper board from the carrier: (along the upper board from its DP-DCU-D end, back from its "
     "front edge)", "Y15's H1 / H2; the carrier rev 0.04 has no holes for them - F11 adds them, the bench revision uses standoffs on its own holes"),
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
    ("BOSS_H", 8.6, "mm", "carrier bosses, floor to the carrier's underside. 5 is the least "
     "used before; 8.6 puts half of the 7.24 the head unit's height adds under the carrier and "
     "half over the upper row, so the carrier, the two rows and the ribbon keep their places "
     "against the panel board, which is centred on the face", ""),
    ("BOSS_D", 8.0, "mm", "boss diameter", ""),
    ("FRONT_L", 25.0, "mm", "ONLY for the stepped unit (a typed FACE_H lower than the body): "
     "length of the low front section behind the faceplate, the part that sits in the dash "
     "opening. The one-height unit has no step wall and does not use it", "no opening is "
     "measured: the dash is rebuilt round the units (D-542)"),
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
    ("SIDE_SCREWS", [(47.0, 42.0), (97.0, 42.0)], "mm", "head-unit style side fixings, used "
     "while HEAD_UNIT_SIDE_HOLES is None (when that is measured the bosses stand on the head "
     "unit's own pattern instead, so one pair of brackets or one cage carries both): an insert "
     "boss inside each side wall at each (back from the body's front face, up from its "
     "underside) - the frame the head unit's holes are measured in",
     "placeholders: the head unit's pattern is not published, and what the pair fastens to is "
     "built with the dash (D-542)"),
    ("SIDE_SCREW_D", _HU["HEAD_UNIT_SIDE_SCREW_D"], "mm", "side screw thread = the head unit's "
     "(HEAD_UNIT_SIDE_SCREW_D, M5), so the same screw holds both to one bracket",
     "follows the head unit's (D-542)"),
    ("SIDE_INSERT_BORE", 6.4, "mm", "bore for the side screw's brass heat-set insert (M5, Ruthex "
     "RX-M5x5.8 class)", "against the insert bought"),
    ("SIDE_INSERT_DEPTH", 8.0, "mm", "depth of that bore: the insert, and room for an M5 x 9 "
     "screw through a bracket 1 mm or more thick", "against the insert and the screw used"),
    ("SIDE_BOSS_D", 10.0, "mm", "side screw boss diameter", ""),
    ("SIDE_BOSS_L", 6.0, "mm", "how far a side screw boss stands in from the wall", ""),

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
CONFIRM["ENVELOPE"] = "not measured, and not a gate: the dash is rebuilt round the units (D-542)"

# The self-test (`freecadcmd selftest.py`): the default set and perturbed ones, each with the
# outcome it must have - "clear" (built, every check passes), "fails" (built, a check fails) or
# "refused" (a fit rule says no, in words). The self-test fails when an outcome differs, so an
# edit that changes what the model does is caught: if the change is meant, change the word here.
# Overrides replace whole values of P.
_BOTH = [("DP-DCU-D", 12, True), ("DP-DCU-E", 12, True)]
_ONE = [("DP-DCU-D", 12, True), ("DP-DCU-E", 12, False)]
# The case as it was before D-542 - a face standing 2 proud of a body only as tall as the rows
# need, a panel board cut to the face, M3 side screws: the sets written for it keep it, so each
# still tests the rule it was written for and comes out the size it did (_old merges a set on it).
_PROUD = {"FACE_H": None, "BEZEL_OVERLAP_X": 2.0, "BEZEL_OVERLAP_Z": 2.0, "FACE_R": 0.0,
          "PANEL_W": None, "PANEL_H": None, "BOSS_H": 5.0,
          "SIDE_SCREWS": [(47.0, 38.0), (97.0, 38.0)], "SIDE_SCREW_D": 3.0,
          "SIDE_INSERT_BORE": 4.0, "SIDE_INSERT_DEPTH": 6.5, "SIDE_BOSS_D": 9.0, "SIDE_BOSS_L": 5.0}


def _old(**over):
    return dict(_PROUD, **over)


_ENV = {"OPENING_W": 190.0, "OPENING_H": 102.0, "DEPTH": 210.0, "BEHIND_H": None}
SELFTEST = [
    # ---- the case toward the head unit (D-542): the defaults, and what its new numbers refuse
    ("the defaults: the head unit's face height and reveal, one height, front install", {},
     "clear"),
    ("the head unit's side holes measured (an invented pattern): the bosses follow it",
     {"HEAD_UNIT_SIDE_HOLES": [(40.0, 45.0), (90.0, 45.0)]}, "clear"),
    ("the head unit's side holes measured, one where the carrier is",
     {"HEAD_UNIT_SIDE_HOLES": [(60.0, 16.0), (90.0, 45.0)]}, "fails"),
    ("the head unit's side holes measured, one behind the rear plate",
     {"HEAD_UNIT_SIDE_HOLES": [(40.0, 45.0), (140.0, 45.0)]}, "refused"),
    ("the head unit's nose radius measured (an invented 4)", {"HEAD_UNIT_NOSE_R": 4.0}, "clear"),
    ("FACE_R 0: square corners", {"FACE_R": 0.0}, "clear"),
    ("FACE_R 8: the corner uncovers the frame's opening", {"FACE_R": 8.0}, "refused"),
    ("FACE_W 180, the sketch's width, under the head unit's reveal", {"FACE_W": 180.0},
     "refused"),
    ("FACE_H None under the head unit's reveal: the body only as tall as the rows need",
     {"FACE_H": None}, "clear"),
    ("FACE_H 80: lower than the drawn panel board", {"FACE_H": 80.0}, "refused"),
    ("FACE_H 64 with the drawn panel board: no stepped unit without a new one", {"FACE_H": 64.0},
     "refused"),
    ("FACE_H 64 and a panel board cut to the face's height: the stepped unit under the head "
     "unit's reveal", {"FACE_H": 64.0, "PANEL_H": None}, "clear"),
    ("the same with its width cut to the face too: the ribbon header is off a 169 board",
     {"FACE_H": 64.0, "PANEL_W": None, "PANEL_H": None}, "refused"),
    ("PANEL_W 184: a panel board wider than the body's inside", {"PANEL_W": 184.0}, "refused"),
    ("the face set in 6 a side: the panel board's screws are off it",
     {"BEZEL_OVERLAP_X": -6.0}, "refused"),
    ("M3 side screws in the new case", {"SIDE_SCREW_D": 3.0, "SIDE_INSERT_BORE": 4.0,
                                        "SIDE_INSERT_DEPTH": 6.5}, "clear"),
    ("SIDE_BOSS_L 4: too short for the M5 insert", {"SIDE_BOSS_L": 4.0}, "refused"),
    ("an opening the head-unit-like unit slides into (the face does not cover it: the dash does)",
     {"ENVELOPE": _ENV}, "clear"),
    # ---- the case before D-542: every set below is on _PROUD
    ("the old defaults: FACE_H None, a face 2 proud, one height, front install", _old(), "clear"),
    ("FACE_W 180, the sketch's width", _old(**{"FACE_W": 180.0}), "refused"),
    ("FACE_W 200", _old(**{"FACE_W": 200.0}), "clear"),
    ("FACE_H 64: the stepped unit", _old(**{"FACE_H": 64.0}), "clear"),
    ("FACE_H 70: stepped", _old(**{"FACE_H": 70.0}), "clear"),
    ("FACE_H 60, the sketch's height", _old(**{"FACE_H": 60.0}), "refused"),
    ("FACE_H 50", _old(**{"FACE_H": 50.0}), "refused"),
    ("FACE_H 62 with the control block anchored top", _old(**{"FACE_H": 62.0, "CONTROLS_ANCHOR": "top"}),
     "clear"),
    ("FACE_H 95: a step lower than the lid's beam", _old(**{"FACE_H": 95.0}), "refused"),
    ("FACE_H 100: taller than the body needs, one height", _old(**{"FACE_H": 100.0}), "clear"),
    ("CONTROLS_ANCHOR top", _old(**{"CONTROLS_ANCHOR": "top"}), "clear"),
    ("CONTROLS_ANCHOR bottom", _old(**{"CONTROLS_ANCHOR": "bottom"}), "clear"),
    ("CONTROLS_ANCHOR left (not a choice)", _old(**{"CONTROLS_ANCHOR": "left"}), "refused"),
    ("ROW_PITCH 28", _old(**{"ROW_PITCH": 28.0}), "refused"),
    ("ROW_PITCH 32, the brief's", _old(**{"ROW_PITCH": 32.0}), "refused"),
    ("ROW_PITCH 40", _old(**{"ROW_PITCH": 40.0}), "refused"),
    ("ROW_PITCH 50", _old(**{"ROW_PITCH": 50.0}), "clear"),
    ("both upper connectors fitted (the default since D-492)", _old(**{"UPPER_CONNECTORS": _BOTH}), "clear"),
    ("DP-DCU-E not fitted (the default before D-492)", _old(**{"UPPER_CONNECTORS": _ONE}), "clear"),
    ("no upper row at all: the control block sets the face", _old(**{"UPPER_CONNECTORS": []}), "clear"),
    ("the drawn carrier without its STEP (stand-in blocks)", _old(**{"CARRIER_STEP": False}), "clear"),
    ("carrier 170 wide", _old(**{"CARRIER_W": 170.0}), "fails"),
    ("carrier 160 wide", _old(**{"CARRIER_W": 160.0}), "refused"),
    ("PANEL_GAP 12", _old(**{"PANEL_GAP": 12.0}), "clear"),
    ("PANEL_MARGIN 3, the brief's", _old(**{"PANEL_MARGIN": 3.0}), "refused"),
    ("FRONT_L 40 on the one-height unit (not used there)", _old(**{"FRONT_L": 40.0}), "clear"),
    ("FRONT_L 40 on the stepped unit", _old(**{"FACE_H": 64.0, "FRONT_L": 40.0}), "refused"),
    ("a side screw boss put where the carrier is",
     _old(**{"SIDE_SCREWS": [(47.0, 10.0), (97.0, 38.0)]}), "fails"),
    ("an opening it slides into", _old(**{"ENVELOPE": {"OPENING_W": 190.0, "OPENING_H": 95.0,
                                                "DEPTH": 210.0, "BEHIND_H": None}}), "clear"),
    ("the stepped unit, height only behind the dash",
     _old(**{"FACE_H": 64.0, "ENVELOPE": {"OPENING_W": 190.0, "OPENING_H": 62.0, "DEPTH": 210.0,
                                   "BEHIND_H": 100.0}}), "clear"),
    ("an opening too shallow and too low", _old(**{"ENVELOPE": {"OPENING_W": 190.0, "OPENING_H": 62.0,
                                                         "DEPTH": 150.0, "BEHIND_H": None}}),
     "refused"),
    ("a nonsense value", _old(**{"WALL": -3.0}), "refused"),
]

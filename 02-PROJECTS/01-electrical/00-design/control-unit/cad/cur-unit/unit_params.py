"""Every number of the Control Unit Remote's mock-up (D-514, work row Y25). The ONE place numbers
live: `unit_lib.py` and `make_unit.py` hold no dimension of their own.

The CUR is the left plate made a unit (D-514): a small sealed box like the climate unit (D-479), the
plate's board (`../left-plate`, Y22) behind a faceplate whose openings come from the board, and the
board's two leads - J1 to DP-DCU-E (D-492) and J2 to the dash post (D-504) - leaving at the back by a
DT13 receptacle or a sealed grommet (block 01.41; the receptacle until he answers).

Each row of TABLE is (NAME, value, unit, what it is, confirm). `confirm` says why the number is a
guess. Nothing left of the steering wheel has been measured and no part of the CUR is in hand
(R11), so every dimension of the unit carries one; only the numerical slack at the end does not.
Change a value, run

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd make_unit.py

and the whole unit rebuilds; a number that no longer fits comes back as a sentence naming the
parameter and which way to move it, never as a traceback.

Frame (the climate unit's): X across the face (0 = the face's left edge seen from the driver's
seat), Y = depth going back from the faceplate's front surface (Y = 0), Z up from the faceplate's
bottom edge. mm throughout.

What is NOT here, because it is read, never typed:
- from `../left-plate/left-plate.kicad_pcb`: the board's outline, corner radius and thickness, its
  mounting holes, every footprint's place - the two winks (SW3 / SW4) and their 17 x 15 caps (the
  dashed F.Fab outline of the P204 placeholder), the hatch and fuel-door keys (SW1 / SW2, centred
  on their 6 x 6 bodies), the mirror stick (JS1: its body square and the 28 mm well on F.Fab), the
  five LEDs, the headers J1 / J2 and how many conductors each carries (their pads);
- from `../dcu-carrier/enclosure/probe.json` and `board.json`: a DT13's flange, housing section,
  flange seal and nose, as the DCU enclosure build read them from TE's models (the climate unit's
  stand-in, `_standin_dt13`, draws them);
- from `../../../tools/enclosure_lib.py`: TE's DT13 panel cut-outs (114-151046) and the 6.25 mm
  panel limit.
"""

# The placing envelope: the opening in the dash face left of the wheel and the room behind it.
# None until measured; then {"OPENING_W": mm, "OPENING_H": mm, "DEPTH": mm clear behind the face}.
ENVELOPE = None                      # nothing left of the wheel is measured - confirm

# The leads that leave the box (D-492, D-504): (the board header they start on, the lead's outside
# diameter where it passes a grommet, what it is). How many conductors each carries is read from
# the header's pads on the board, never typed.
LEADS = [
    ("J1", 7.0, "the cable to the climate unit's DP-DCU-E (P200, D-492)"),
    ("J2", 5.0, "the wink lead to the dash post, L3-S1 9-11 and dash ground G20 (D-504)"),
]

# The rear connection when REAR is "receptacle": (code, TE part, the headers whose lines it
# carries). Laid side by side across the rear plate, centred on REAR_DX / REAR_DZ. A lead in LEADS
# that no receptacle carries leaves by the grommet beside them. The default is two receptacles,
# the recommendation of block 01.41 (which waits on his answer): one DT13-12PA cannot carry J1's
# twelve lines and J2's four. The other answers are this same parameter:
#   one receptacle, the wink lead through a grommet beside it: [("DP-CUR", "DT13-12PA", ("J1",))]
#   no receptacle, both leads captive through a grommet:       REAR = "grommet"
# DP-CUR and DP-CUR-B are provisional codes: no housings row names them until 01.41 is answered.
RECEPTACLES = [
    ("DP-CUR", "DT13-12PA", ("J1",)),          # J1's twelve: the cable to DP-DCU-E (D-492)
    ("DP-CUR-B", "DT13-06PA", ("J2",)),        # J2's four wink lines (D-504), two ways spare
]

# The headers on the board's back, drawn as their courtyard and this height above the board's back
# face (the mated plug is the room HEADER_PLUG_H behind the tallest).
BACK_PARTS = {
    "J1": 9.1,       # 2 x 6 shrouded IDC box header, vertical (KiCad's model class)
    "J2": 7.0,       # JST XH 4-way vertical (B4B-XH-A class)
}

TABLE = [
    # ------------------------------------------------------------------------------ the face --
    ("FACE_W", None, "mm", "faceplate width; None = derived, the body's width + 2 x BEZEL_OVERLAP. "
     "A typed number must be at least that", "the opening left of the wheel is unmeasured"),
    ("FACE_H", None, "mm", "faceplate height; None = derived, the body's height + 2 x "
     "BEZEL_OVERLAP. A typed number must be at least that", "the opening is unmeasured"),
    ("FACE_T", 3.0, "mm", "faceplate thickness, as the climate unit's",
     "material and make not chosen (luxury LP20)"),
    ("BEZEL_OVERLAP", 2.0, "mm", "how far the faceplate stands proud of the body on every side, "
     "covering the edge of the dash opening", "the opening is unmeasured"),
    ("CAP_PROUD", 2.0, "mm", "how far a key cap (the four 17 x 15 caps) stands in front of the face",
     "no cap chosen (P204, LP20)"),
    ("CAP_L", 8.0, "mm", "a cap's depth, front to back: its back rests on its switch's plunger, "
     "behind the face", "no cap chosen (P204, LP20)"),
    ("CAP_CLEAR", 0.3, "mm", "gap round a cap in its opening, per side", "no cap chosen"),
    ("KEY_CAP_FROM", "SW3", "", "the footprint whose dashed F.Fab outline is the hatch and "
     "fuel-door keys' cap too: the sketch draws all four keys 17 x 15 (panel-concept.html "
     "plate()), and only the wink placeholder carries the cap on the board", "the sketch's"),
    ("WINK_SW_H", 13.0, "mm", "a wink switch (P204) from the board's front face to its plunger's "
     "top, drawn as its 12 x 12 body square that tall", "no P204 part chosen (C&K 8125 class)"),
    ("KEY_SW_H", 13.0, "mm", "a release key's 6 x 6 tactile switch from the board to its "
     "actuator's top (the left plate README: the 13 mm actuator), drawn as its 6 x 6 body",
     "SW_PUSH_6mm class, no part in hand"),
    ("STICK_BODY_H", 10.0, "mm", "the mirror stick's body above the board, its 26 x 26 square",
     "no P156 part chosen (ALPS RKJXV class)"),
    ("STICK_SHAFT_D", 4.0, "mm", "the stick's lever through the well", "no P156 part chosen"),
    ("STICK_KNOB_D", 16.0, "mm", "the stick's knob in front of the face (the sketch's 8 mm rim "
     "radius)", "the sketch's; no knob chosen"),
    ("STICK_PROUD", 12.0, "mm", "how far the stick's knob stands in front of the face",
     "no P156 part chosen"),
    ("STICK_FLOAT", 0.5, "mm", "gap between the back of the knob and the face", "no knob chosen"),
    ("LED_H", 0.8, "mm", "an 0603 LED's height on the board's front", "0603 class, no part chosen"),
    ("LED_LIT_REACH", 2.0, "mm", "an LED within this of a cap's opening or the stick's well (on "
     "the board, outside its edge) is lit through that opening and gets no window of its own; "
     "beyond it, a window LED_WINDOW_D across. LED1-LED4 sit inside their caps (D-499: no "
     "window); LED5, the mirror symbol, sits 1.5 mm outside the well's edge",
     "the symbols' look is LP20's; the mirror symbol's place is a part question (I-006)"),
    ("LED_WINDOW_D", 3.0, "mm", "a window in the face over an LED no opening lights", "LP20's look"),
    ("LED_PIPE_CLEAR", 0.2, "mm", "gap round a light pipe in its window, per side",
     "no light pipe chosen"),
    ("CONTROL_EDGE", 2.0, "mm", "least distance from an opening to the edge of the face",
     "as the climate unit's, a guess"),
    ("CONTROL_GAP", 1.0, "mm", "least plastic between two openings in the face",
     "as the climate unit's, a guess"),
    ("CONTROL_BEHIND_CLEAR", 0.2, "mm", "least distance from an opening to the inside of the box "
     "behind it", "as the climate unit's"),
    ("FRONT_CLEAR", 1.0, "mm", "least gap between the faceplate's back (or the front frame's ring) "
     "and anything on the board's front that is not a cap", "nothing in hand"),

    # ------------------------------------------------------------------------------ the board --
    ("BOARD_GAP", None, "mm", "faceplate's rear face to the board's front face; None = derived, "
     "the least that seats the tallest switch under a cap standing CAP_PROUD and keeps the stick's "
     "body and the board behind the front frame. A typed number must be at least that (the caps "
     "grow longer)", "set by the switches and caps bought"),
    ("BOARD_DX", 0.0, "mm", "the board's centre to the right of the body's centre (the box grows "
     "round it, so the face stays centred on the body)", "taste: his to place"),
    ("BOARD_DZ", 0.0, "mm", "the board's centre above the body's centre", "taste: his to place"),
    ("BOARD_BACK_H", None, "mm", "kept clear behind the board for its headers and the plugs mated "
     "on them; None = derived, the tallest of BACK_PARTS + HEADER_PLUG_H",
     "no header or plug in hand"),
    ("BACK_PARTS", BACK_PARTS, "mm", "the headers on the board's back and their heights (table "
     "above)", "KiCad's model classes, no part in hand"),
    ("HEADER_PLUG_H", 12.0, "mm", "a plug mated on a header and its lead turning, behind the "
     "header's top", "no IDC plug or XH housing in hand"),
    ("STANDOFF_D", 6.0, "mm", "the front frame's standoffs, faceplate to the board's M3 holes",
     "as the climate unit's 8, scaled to the board's 4 mm hole inset"),
    ("WEB", 4.0, "mm", "the webs joining those standoffs to the frame's ring", "as the climate unit's"),

    # ------------------------------------------------------------------------------- the rear --
    ("REAR", "receptacle", "", "how the leads leave the box (block 01.41): 'receptacle' = "
     "RECEPTACLES on the rear plate, a lead none carries through the grommet beside them; "
     "'grommet' = every lead through one sealed grommet, captive", "his answer to 01.41"),
    ("RECEPTACLES", RECEPTACLES, "", "the receptacles (table above). Default: two, DP-CUR "
     "(DT13-12PA, J1) and DP-CUR-B (DT13-06PA, J2), the recommendation of block 01.41 until he "
     "answers; [(DP-CUR, DT13-12PA, (J1,))] = one receptacle and the wink lead through a grommet; "
     "REAR 'grommet' = no receptacle", "his answer to block 01.41"),
    ("LEADS", LEADS, "mm", "the leads and their outside diameters (table above)",
     "no cable bought: P200 and the wink lead unmeasured"),
    ("REAR_DX", 0.0, "mm", "the rear row's centre to the right of the body's centre", "taste"),
    ("REAR_DZ", 0.0, "mm", "the rear row's centre above the body's centre", "taste"),
    ("REAR_GAP", 2.0, "mm", "between two neighbours in the rear row (flanges or a grommet's)",
     "as the climate unit's UPPER_CONN_GAP"),
    ("REC_BODY_L", 20.0, "mm", "a flange receptacle's housing behind its flange, inside the box "
     "(wire seal and contacts), drawn as its housing section", "TE's drawing of the flange "
     "receptacle not read; no part in hand"),
    ("REC_WIRE_L", 10.0, "mm", "room for the wires to turn into the receptacle's back, between it "
     "and the plugs on the board's headers", "no lead made"),
    ("SEAL_LAND", 1.0, "mm", "least flange seal left round the cut-out, per side",
     "TE's seal, as probed from its model"),
    ("GROMMET_BODY_D", 18.0, "mm", "the grommet's body, which fills its hole in the rear plate",
     "no grommet chosen"),
    ("GROMMET_FLANGE_D", 24.0, "mm", "the grommet's lips, inside and out", "no grommet chosen"),
    ("GROMMET_FLANGE_T", 2.0, "mm", "each lip's thickness", "no grommet chosen"),
    ("GROMMET_WEB", 1.5, "mm", "least rubber between a lead's bore and the body's edge or the next "
     "bore", "no grommet chosen"),
    ("LEAD_BEND_IN", 12.0, "mm", "room inside for the leads to turn from the board's headers to "
     "the grommet", "no lead made"),
    ("LEAD_STUB_L", 40.0, "mm", "how much of each captive lead is drawn outside the grommet",
     "a picture only"),
    ("PLUG_L", 50.0, "mm", "a mated DT06 plug with its wedge and rear seal, from the rear plate's "
     "outer face", "no plug measured (as the climate unit)"),
    ("CABLE_BEND", 30.0, "mm", "room behind the plug for the cable to turn", "no harness measured"),
    ("PLUG_GROW", 3.0, "mm", "the plug's section = TE's cut-out plus this on every side",
     "no plug measured"),

    # ------------------------------------------------------------------------------ the case --
    ("MATERIAL", "ASA", "", "as the other boxes: the dash reaches 70 C (D-270); never PLA", ""),
    ("WALL", 2.5, "mm", "side walls and the beam under the lid's front edge (the climate unit's 3, "
     "scaled to the smaller box)", "nothing printed yet"),
    ("FLOOR", 2.5, "mm", "floor", "nothing printed yet"),
    ("LID", 2.5, "mm", "lid, and the front section's roof", "nothing printed yet"),
    ("GAP", 1.0, "mm", "a board's or a flange's edge to the wall beside it", "as the climate unit's"),
    ("FRAME_D", 6.0, "mm", "depth of the front frame's ring behind the faceplate",
     "as the climate unit's"),
    ("RIM_H", 3.0, "mm", "height of the beam the lid's front edge lands on, hanging under the roof "
     "straight behind the room kept behind the board (0 = no beam)", "as the climate unit's"),
    ("PLATE", 3.0, "mm", "rear plate; TE allows 6.25 at most (114-151046 3.11)",
     "as the climate unit's"),
    ("PLATE_LIP", 2.0, "mm", "floor and walls past the plate's outer face", "as the climate unit's"),
    ("PLATE_EDGE", 3.0, "mm", "least plastic between a cut-out, a screw hole or a grommet's lip "
     "and the plate's edge", "as the climate unit's"),
    ("SLOT_DEPTH", 1.2, "mm", "the plate's channel into each side wall (the climate unit's 1.5 in "
     "a 3 mm wall)", "nothing printed yet"),
    ("SLOT_CLEAR", 0.3, "mm", "play of the plate in its channel", "nothing printed yet"),
    ("FLOOR_GROOVE", 1.0, "mm", "the plate's channel into the floor", "nothing printed yet"),
    ("CUTOUT_CLEAR", 0.15, "mm", "added round TE's cut-out for the print, per side",
     "nothing printed yet"),
    ("RESERVED_MARK_W", 0.6, "mm", "width of a scribed outline (the climate unit's rear plate draws "
     "one for a reserved cut-out; the CUR has none)", "nothing printed yet"),
    ("RESERVED_MARK_D", 0.4, "mm", "depth of that scribe", "nothing printed yet"),
    ("INSERT_BORE", 4.0, "mm", "bore for an M3 brass heat-set insert (Ruthex RX-M3x5.7 class)",
     "against the insert bought"),
    ("INSERT_DEPTH", 6.5, "mm", "depth of that bore", "against the insert bought"),
    ("INSERT_SKIN", 1.0, "mm", "least plastic left beyond an insert bore", "as the climate unit's"),
    ("SCREW_CLEAR", 3.4, "mm", "M3 clearance hole", "against the screw bought"),
    ("LUG_D", 9.0, "mm", "lid screw lugs: diameter; they stand inside the side walls", "as the CU's"),
    ("LUG_EMBED", 1.5, "mm", "how far a lug's circle is sunk into its wall", "as the climate unit's"),
    ("LUG_H", 10.0, "mm", "lug height below the lid", "as the climate unit's"),
    ("LID_LUGS", [0.0, 1.0], "", "where the lugs stand along each side wall, as fractions of the "
     "run from the beam (0) to the rear plate (1)", ""),
    ("GASKET_GROOVE_W", 1.6, "mm", "lid's cord-gasket groove, width (as the other lids)",
     "no cord bought"),
    ("GASKET_GROOVE_D", 1.2, "mm", "lid's cord-gasket groove, depth", "no cord bought"),
    ("GASKET_R", 3.0, "mm", "gasket path's corner radius", "as the climate unit's"),

    # ------------------------------------------------------------------------ mounting ears --
    ("EARS", ["left", "right"], "", "the mounting ears: a flat tab on each named side wall, its "
     "screw along Y into a bracket behind the dash skin (provisional: what the CUR fastens to "
     "left of the wheel is unmeasured). [] = none, and the box goes into its opening from the "
     "front", "what it fastens to is unmeasured"),
    ("EAR_Y", None, "mm", "the ears' front face, back from the face's front; None = the body's "
     "front, straight behind the front frame", "the dash skin's thickness is unmeasured"),
    ("EAR_Z", None, "mm", "the ears' centre height; None = the body's centre",
     "what it fastens to is unmeasured"),
    ("EAR_L", 10.0, "mm", "how far an ear stands out from its wall", "unmeasured"),
    ("EAR_W", 12.0, "mm", "an ear's height (along Z)", "unmeasured"),
    ("EAR_T", 3.0, "mm", "an ear's thickness (along Y)", "unmeasured"),

    # ------------------------------------------------------------------- tolerances and slack --
    ("OUTLINE_TOL", 0.2, "mm", "a probed DT13 body is read as the climate unit's build reads it", ""),
    ("BOARD_JSON_EDGE", 0.05, "mm", "board.json's outline is the outside of KiCad's 0.1 mm "
     "Edge.Cuts line: half that width is taken off each side", ""),
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
CONFIRM["ENVELOPE"] = "not measured (nothing left of the wheel is)"

# The self-test (`freecadcmd selftest.py`): the default set and perturbed ones, each with the
# outcome it must have - "clear" (built, every check passes), "fails" (built, a check fails) or
# "refused" (a fit rule says no, in words). The self-test fails when an outcome differs, so an
# edit that changes what the model does is caught: if the change is meant, change the word here.
# Overrides replace whole values of P.
_J1_ONLY = [("DP-CUR", "DT13-12PA", ("J1",))]
SELFTEST = [
    ("the defaults: DP-CUR (DT13-12PA) for J1, DP-CUR-B (DT13-06PA) for J2 (01.41's "
     "recommendation)", {}, "clear"),
    ("one DT13-12PA for J1's and J2's lines: 16 conductors on 12 ways",
     {"RECEPTACLES": [("DP-CUR", "DT13-12PA", ("J1", "J2"))]}, "fails"),
    ("DP-CUR carries J1's twelve, the wink lead through a grommet beside it",
     {"RECEPTACLES": _J1_ONLY}, "clear"),
    ("REAR grommet: both leads captive", {"REAR": "grommet"}, "clear"),
    ("REAR socket (not a choice)", {"REAR": "socket"}, "refused"),
    ("a receptacle carrying a header the board does not have",
     {"RECEPTACLES": [("DP-CUR", "DT13-12PA", ("J1", "J7"))]}, "refused"),
    ("a DT13-04PA (no TE cut-out or probe for it)",
     {"RECEPTACLES": [("DP-CUR", "DT13-04PA", ("J1", "J2"))]}, "refused"),
    ("a grommet too small for its two leads", {"REAR": "grommet", "GROMMET_BODY_D": 12.0},
     "refused"),
    ("FACE_W 100: narrower than the body", {"FACE_W": 100.0}, "refused"),
    ("FACE_W 130 x FACE_H 80: a larger face", {"RECEPTACLES": _J1_ONLY, "FACE_W": 130.0,
                                                "FACE_H": 80.0}, "clear"),
    ("BOARD_GAP 10: too shallow for the switches", {"BOARD_GAP": 10.0}, "refused"),
    ("BOARD_GAP 20: longer caps", {"RECEPTACLES": _J1_ONLY, "BOARD_GAP": 20.0}, "clear"),
    ("BOARD_DX 6: the board off centre, the box grows", {"RECEPTACLES": _J1_ONLY,
                                                         "BOARD_DX": 6.0}, "clear"),
    ("BOARD_BACK_H 15: less than the headers and plugs need", {"BOARD_BACK_H": 15.0}, "refused"),
    ("LED_LIT_REACH 0: LED5 gets a window, against the stick's well", {"LED_LIT_REACH": 0.0},
     "refused"),
    ("CONTROL_GAP 3: the caps' openings too close", {"CONTROL_GAP": 3.0}, "refused"),
    ("REAR_DZ 15: the rear row high, the box grows", {"RECEPTACLES": _J1_ONLY, "REAR_DZ": 15.0},
     "clear"),
    ("PLATE 7: thicker than TE allows", {"PLATE": 7.0}, "refused"),
    ("no ears: front install", {"RECEPTACLES": _J1_ONLY, "EARS": []}, "clear"),
    ("EAR_Y 200: off the body", {"EAR_Y": 200.0}, "refused"),
    ("EAR_L 4: no room round the ear's screw", {"EAR_L": 4.0}, "refused"),
    ("an opening it slides into", {"RECEPTACLES": _J1_ONLY, "EARS": [],
                                   "ENVELOPE": {"OPENING_W": 110.0, "OPENING_H": 66.0,
                                                "DEPTH": 220.0}}, "clear"),
    ("an opening too small", {"RECEPTACLES": _J1_ONLY,
                              "ENVELOPE": {"OPENING_W": 90.0, "OPENING_H": 50.0,
                                           "DEPTH": 100.0}}, "refused"),
    ("a nonsense value", {"WALL": -3.0}, "refused"),
]

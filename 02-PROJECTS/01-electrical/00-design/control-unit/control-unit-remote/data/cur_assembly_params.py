"""Every number of the Control Unit Remote's mock-up (Y71; D-597, D-602, D-604, D-615). The ONE place
numbers live: tools/cur_assembly.py holds no dimension of its own.

The CUR is a small sealed box behind the ruled face (D-602): the CUR board (cad/cur-board, drawn by
tools/cur_board_sch.py) right behind a faceplate whose openings come from the board's footprints, its
nine wires leaving on a sealed pigtail through a grommet in the rear cover to an inline DRC 24 (D-615).

    front shell   the faceplate and the four walls, one print; a ledge inside the walls that the board's
                  front rests on, at the depth the encoder's body sets (its bushing through the face, a nut
                  in front)
    rear cover    a plate with a lip that plugs into the shell, four posts that press the board's corners
                  forward, the grommet's hole, two ears that screw to a bracket behind the dash; held by two
                  M2 screws through the side walls into its lip
    caps          one per key, through the face with a flange behind it, resting on its switch

Each row of TABLE is (NAME, value, unit, what it is, confirm). `confirm` says why the number is a guess:
nothing right of the wheel is measured and no part of the CUR is in hand (R11). Change a value, run

    freecadcmd 00-design/tools/mockup.py --pass cur-assembly

and the whole unit rebuilds; a number that no longer fits comes back as a sentence naming the parameter
and which way to move it, never as a traceback.

Frame: X across the face (0 = the face's left edge seen from the driver), Y = depth back from the
faceplate's front (Y = 0), Z up from the face's bottom edge. mm throughout.

Read, never typed: from cad/cur-board/cur-board.kicad_pcb the board's outline and thickness and every
footprint - each cap (the dashed F.Fab rectangle on the wink and hazard footprints; the release keys take
KEY_CAP_FROM's), each switch body (the solid F.Fab rectangle), the mirror control's well (the dashed F.Fab
circle), the encoder's axis, the LEDs, and every part on the back by its courtyard. The face's own size
is the face's (cur_board_sch.py: FACE_W x FACE_H), the board sits at the face's (EDGE, EDGE).
"""

ENVELOPE = None                      # the dash opening right of the wheel - not measured, confirm

# the parts on the board's back: their height above the board's back face, by reference prefix
BACK_HEIGHTS = {
    "U1": 0.9,      # IS31FL3218, QFN-24 4 x 4
    "U2": 1.2,      # PCA9555PW, TSSOP-24
    "U3": 1.45,     # AP2112K, SOT-23-5
    "C": 0.9,       # 0603
    "R": 0.55,      # 0603
}

# the parts on the board's front that no cap rides on: height above the board's front face, by prefix
FRONT_HEIGHTS = {"LED": 0.8}

TABLE = [
    # --------------------------------------------------------------------------- the face --
    ("FACE_T", 2.5, "mm", "faceplate thickness", "material and print not chosen (luxury LP20)"),
    ("BEZEL_OVERLAP", 0.6, "mm", "how far the faceplate stands proud of the shell's walls on every side, "
     "covering the edge of the dash opening", "the opening is unmeasured"),
    ("CAP_PROUD", 1.5, "mm", "how far a key cap stands in front of the face", "no cap made (taste)"),
    ("CAP_CLEAR", 0.2, "mm", "gap round a cap in its opening, per side", "the print's tolerance"),
    ("CAP_FLANGE", 0.5, "mm", "a cap's retaining flange behind the face, past its opening per side "
     "(it keeps the cap from falling out the front)", "no cap made"),
    ("CAP_FLANGE_T", 0.8, "mm", "that flange's thickness", "no cap made"),
    ("CAP_TRAVEL", 0.4, "mm", "gap between a cap's flange and the face's back with the cap at rest - "
     "the key's travel before the flange stops it", "the switches' travel is about 0.25-0.5"),
    ("KEY_CAP_FROM", "SW3", "", "the footprint whose dashed F.Fab cap outline the release keys' caps "
     "take too: the face draws them all %s" % "11.1 x 7.9", "the face's (D-602)"),
    ("WINK_SW_H", 4.6, "mm", "a wink switch (P204) from the board's front to its plunger's top",
     "Omron D2FS class, no part chosen"),
    ("HAZ_SW_H", 4.6, "mm", "the hazard switch (P226) from the board to its plunger's top, latched in "
     "(a 5.8 mm self-locking switch, cut to this)", "no part chosen"),
    ("KEY_SW_H", 2.5, "mm", "a release key (TL3342 class) from the board to its actuator's top",
     "TL3342 class, no part chosen"),
    ("STICK_SW_H", 3.3, "mm", "the mirror control (SKRH class) from the board to its actuator's top",
     "ALPS SKRH class, no part chosen"),
    ("STICK_KNOB_D", 7.1, "mm", "the mirror control's knob, in its 12.7 mm well (the face's stickD)",
     "the face's (D-602)"),
    ("STICK_KNOB_PROUD", 4.0, "mm", "how far that knob stands in front of the face", "taste"),
    ("STICK_SHAFT_D", 3.0, "mm", "the knob's stem down to the switch's actuator", "no knob made"),
    ("ENC_BODY_H", 6.5, "mm", "the encoder's body from the board's front to its bushing's shoulder: "
     "the board's depth behind the face follows it", "PEC09 class drawing, confirm"),
    ("ENC_BUSHING_D", 7.0, "mm", "the encoder's threaded bushing (M7), through the face", "PEC09 class"),
    ("ENC_BUSHING_L", 5.0, "mm", "the bushing's length", "PEC09 class"),
    ("ENC_SHAFT_D", 6.0, "mm", "the encoder's shaft", "PEC09 class"),
    ("ENC_SHAFT_L", 12.0, "mm", "the shaft from the bushing's shoulder", "PEC09 class, 12 mm long version"),
    ("ENC_NUT_T", 1.6, "mm", "the bushing's nut, in front of the face, under the knob", "M7 thin nut"),
    ("ENC_NUT_AF", 9.0, "mm", "that nut across its corners (drawn round)", "M7 thin nut"),
    ("KNOB_HOLE_CLEAR", 0.25, "mm", "the face's hole round the bushing, per side", "the print's"),
    ("KNOB_D", 12.7, "mm", "the screen knob (the face's d)", "the face's (D-602)"),
    ("KNOB_PROUD", 9.0, "mm", "how far the screen knob stands in front of the face", "taste"),
    ("KNOB_FLOAT", 0.5, "mm", "gap between the knob's back and the nut", "no knob made"),
    ("LED_WINDOW", False, "", "no LED gets a window of its own: each shines through its cap or the "
     "control's well", "the face's (D-602)"),

    # ------------------------------------------------------------------------ the shell --
    ("WALL", 1.2, "mm", "the shell's side walls (with BEZEL_OVERLAP they must leave the face's 2.5 mm edge room for a cap's flange)", "nothing printed yet"),
    ("GAP", 0.3, "mm", "the board's edge to the wall beside it", "the print's"),
    ("LEDGE_W", 1.0, "mm", "the ledge the board's front rests on, from the wall inward", "nothing printed"),
    ("LEDGE_BEAR", 0.3, "mm", "least of the ledge under the board's edge", "nothing printed"),
    ("LEDGE_H", 1.0, "mm", "the ledge's depth in front of the board", "nothing printed"),
    ("SOLDER_JOINT_H", 3.0, "mm", "the pigtail's soldered ends and their insulation, behind the board's back face",
     "no pigtail made"),
    ("BACK_ROOM", 7.0, "mm", "room behind the board's back face for the pigtail's soldered ends and their "
     "turn to the grommet", "no pigtail made"),
    ("MATERIAL", "ASA", "", "as the other boxes: the dash reaches 70 C (D-270); never PLA", ""),

    # --------------------------------------------------------------------- the rear cover --
    ("COVER_T", 2.0, "mm", "the rear cover's plate", "nothing printed"),
    ("COVER_LIP", 3.0, "mm", "how deep the cover's lip goes into the shell", "nothing printed"),
    ("COVER_LIP_T", 1.4, "mm", "the lip's wall", "nothing printed"),
    ("COVER_CLEAR", 0.15, "mm", "the lip's play in the shell, per side", "the print's"),
    ("POST_D", 2.4, "mm", "the four posts pressing the board's corners", "nothing printed"),
    ("POST_INSET", 1.5, "mm", "a post's centre from the board's corner, along each edge", "nothing printed"),
    ("SCREW_D", 2.2, "mm", "M2 clearance hole through a side wall", "against the screw bought"),
    ("SCREW_PILOT_D", 1.6, "mm", "pilot hole in the lip for a self-tapping M2", "against the screw bought"),
    ("GROMMET_HOLE_D", 7.0, "mm", "the grommet's hole in the cover, for the nine-wire pigtail", "no cable chosen"),
    ("GROMMET_WEB", 0.5, "mm", "least rubber round the pigtail in the grommet's hole, per side", "no grommet chosen"),
    ("GROMMET_FLANGE_D", 11.0, "mm", "the grommet's lips, inside and out", "no grommet chosen"),
    ("GROMMET_FLANGE_T", 1.5, "mm", "each lip's thickness", "no grommet chosen"),
    ("PIGTAIL_D", 6.0, "mm", "the pigtail's jacket: nine 20 AWG conductors", "no cable chosen"),
    ("PIGTAIL_L", 40.0, "mm", "how much of the pigtail is drawn behind the cover (it runs about 150 mm to "
     "its DRC 24)", "a picture only"),
    ("EARS", ["left", "right"], "", "a flat tab on each named side of the cover, its screw along Y into a "
     "bracket behind the dash; [] = none", "what it fastens to is unmeasured"),
    ("EAR_L", 6.0, "mm", "how far an ear stands out from the shell's wall", "unmeasured"),
    ("EAR_W", 8.0, "mm", "an ear's height (along Z)", "unmeasured"),
    ("EAR_T", 2.0, "mm", "an ear's thickness (along Y)", "unmeasured"),
    ("EAR_HOLE_D", 2.4, "mm", "the ear's screw hole (M2)", "unmeasured"),

    # ----------------------------------------------------------------- tolerances and slack --
    ("VOLUME_EPS", 1e-4, "mm3", "an overlap smaller than this is numerical noise", ""),
    ("EPS", 1e-6, "mm", "slack when comparing two derived numbers", ""),
    ("OVERCUT", 1.0, "mm", "how far a cutting tool overshoots the face it cuts through (no effect)", ""),
    ("VIEW_MARGIN", 4.0, "mm", "white space round the SVG views", ""),
    ("VIEW_STROKE", 0.12, "mm", "line width in the SVG views", ""),
    ("VIEW_DEFLECTION", 0.02, "mm", "how closely a curve is followed in the SVG views", ""),
]

P = {name: value for (name, value, unit, what, confirm) in TABLE}
P["ENVELOPE"] = ENVELOPE
P["BACK_HEIGHTS"] = BACK_HEIGHTS
P["FRONT_HEIGHTS"] = FRONT_HEIGHTS
UNIT = {name: unit for (name, value, unit, what, confirm) in TABLE}
UNIT.update({"BACK_HEIGHTS": "mm", "FRONT_HEIGHTS": "mm"})
WHAT = {name: what for (name, value, unit, what, confirm) in TABLE}
CONFIRM = {name: confirm for (name, value, unit, what, confirm) in TABLE if confirm}
CONFIRM["ENVELOPE"] = "not measured (nothing right of the wheel is)"
CONFIRM["BACK_HEIGHTS"] = "package classes, no part in hand"

# The self-test (`freecadcmd tools/mockup_selftest.py --pass cur-assembly`): the defaults and perturbed
# sets, each with the outcome it must have - "clear", "fails" (built, a check fails) or "refused" (a fit
# rule says no, in words). Overrides replace whole values of P.
SELFTEST = [
    ("the defaults: the D-602 face, the pigtail through the rear grommet (D-615)", {}, "clear"),
    ("no ears", {"EARS": []}, "clear"),
    ("a deeper back room", {"BACK_ROOM": 12.0}, "clear"),
    ("ENC_BODY_H 2: the board too near the face for the winks' switches", {"ENC_BODY_H": 2.0}, "refused"),
    ("WALL 2.5: the shell's walls reach into the caps' openings", {"WALL": 2.5}, "refused"),
    ("LEDGE_W 3: the ledge under the board's switches", {"LEDGE_W": 3.0}, "refused"),
    ("GROMMET_FLANGE_D 40: wider than the cover", {"GROMMET_FLANGE_D": 40.0}, "refused"),
    ("PIGTAIL_D 8: the cable thicker than its grommet's hole", {"PIGTAIL_D": 8.0}, "refused"),
    ("BACK_ROOM 1: the back's chips into the cover's plate", {"BACK_ROOM": 1.0}, "refused"),
    ("CAP_FLANGE 1.2: two caps' flanges meet", {"CAP_FLANGE": 1.2}, "refused"),
    ("an opening it slides into", {"ENVELOPE": {"OPENING_W": 42.5, "OPENING_H": 31.5, "DEPTH": 60.0}}, "clear"),
    ("an opening too small", {"ENVELOPE": {"OPENING_W": 38.0, "OPENING_H": 28.0, "DEPTH": 60.0}}, "refused"),
    ("a nonsense value", {"WALL": -3.0}, "refused"),
]

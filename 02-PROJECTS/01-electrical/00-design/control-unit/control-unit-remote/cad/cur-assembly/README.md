# cur-assembly - the Control Unit Remote (CUR), mocked up

*Rev 2026-10-15 (Y71: D-597, D-602, D-604, D-615) · owns: what this folder is, what it may claim, and how to
rebuild it. Read `00-design/README.md` first: it is the fence. The design is the record's (box `CUR`,
housing `DP-CUR`, devices `DV21` / `DV24` / `DV62`, parts P156, P198-P200, P204, P219, P226, P249, P250);
this is a drawing of it.*

## What it is

The CUR whole: the board (`../cur-board`, rev 1.00) behind the face D-602 rules, in a two-part printed case.

- **The face** is the CUR face concept's second pass at 32 mm (`../../diagrams/cur-face-concept.html`):
  43.11 x 32.0 mm, 2.5 mm thick. The screen knob (12.7 mm) is over the mirror control's 12.7 mm well on the
  steering-wheel side, then the hazard across the top row (23.8 x 7.9) and the winks, fuel-door and hatch
  keys below it (11.1 x 7.9), one 1.6 mm gap everywhere. Every opening is read from the board's footprints,
  so the face follows the board.
- **The front shell** is the faceplate and four 1.2 mm walls in one print; the walls stand 0.6 mm inside the
  face's edge (the bezel covering the dash opening). A 1.0 mm ledge inside the walls carries the board's
  front edge, 9 mm behind the face's front - the encoder's body, whose M7 bushing passes through the face
  with a nut in front.
- **The caps** pass through the face, a 0.5 mm flange behind it holding each in, each resting on its switch
  with 0.4 mm of travel before the flange stops it.
- **The rear cover** plugs into the shell on a 3 mm lip, its four corner posts pressing the board onto the
  ledge; two M2 screws through the side walls into the lip hold it. The pigtail leaves through a grommet in
  its centre (D-615), and two ears screw to a bracket behind the dash.

The box is **41.91 x 30.8 mm behind a 43.11 x 32 face, 19.6 mm deep (30.7 with the knob)**, 7.7 cm3 of ASA,
fitted from the front through an opening its own size.

It is a **mock-up**: insides and case as one parametric FreeCAD build driven by one table of numbers
(`../../data/cur_assembly_params.py`) that rebuilds when a number changes and says in words what no longer
fits. **R11: nothing here is measured or bought** - the opening right of the wheel, the bracket behind, every
switch, the knobs, the caps, the grommet and the pigtail. Each number carries its `confirm`.

## Building it

    freecadcmd 00-design/tools/mockup.py --pass cur-assembly            the model, the STEPs, the views
    freecadcmd 00-design/tools/mockup_selftest.py --pass cur-assembly   13 parameter sets, each held to its outcome

`freecadcmd` on the Mac is `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd`. The geometry is
`00-design/tools/cur_assembly.py`; the board's position on the face is `cur_board_sch.py`'s.

What it checks: every inside part and the room kept for the pigtail's joints against both case parts (no
interference); every LED shining through its cap or the well; and, before anything is drawn, the fit rules:
the caps' flanges inside the walls and clear of each other, the board's depth enough for every switch
under its cap, the ledge under the board but clear of its parts, the back room for the joints and the
grommet, the grommet inside the cover, the cable through the grommet, and the dash opening when measured.

## Opening it

**FreeCAD 1.0**: File → Open → `cur-assembly.FCStd`. The tree has *Insides* (the board, every switch, cap
and knob, the grommet and pigtail; *Keepouts* hidden inside it) and *Case* (the front shell and the rear
cover). Each case part is also a STEP of its own for the slicer or any CAD (`cur-assembly-front_shell.step`,
`cur-assembly-rear_cover.step`), and `cur-assembly.step` is the whole unit.

## Files

`cur-assembly.FCStd` the model; `cur-assembly.step` the unit; `cur-assembly-front_shell.step`,
`cur-assembly-rear_cover.step` the two prints. The four views are `../../diagrams/cur-assembly-view-*.svg`,
the report `../../data/cur-assembly-report.json`.

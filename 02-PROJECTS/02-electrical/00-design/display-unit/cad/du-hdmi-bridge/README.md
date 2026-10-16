# Display bridge board — the KiCad project

*Rev 2026-10-13 (sheet and board rev 0.01, provisional - Y46, D-550, D-561) · owns: what this KiCad
project is for, what it may claim, and how to rebuild it. Its part is `P119` in
`../../../../data/parts.csv`. Read `../../../README.md` first: it is the fence.*

## What it is

The Display Unit's BT817 board (`P117`, Bridgetek ME817EV) gives its picture as 24-bit parallel RGB
on CN1, a 50-way 0.5 mm flat-cable connector. The 12.3-inch panel kit you chose (`P118`, D-550: the
850 nit HannStar HSD123KPW2-D10 with an HDMI driver board) takes HDMI. No ready-made board joins
the two, so this one does: a TI **TFP410** DVI transmitter, a 50-way connector for the flat cable,
an HDMI socket, and a 3.3 V regulator from a 5 V input. 62 x 46 mm, 2 layers, four M3 holes.

- **J1, from the BT817 board.** Hirose FH12-50S-0.5SH(55), bottom contact, like the ME817EV's CN1.
  The cable is a 50-way 0.5 mm FFC with its contacts on the **same side at both ends (type A)**,
  the two connectors mouth to mouth. Conductor n then lands on J1 pin 51 - n, so **J1 pin k carries
  CN1 pin 51 - k** and the sheet names every net by CN1's own pin (S-500 Table 3-3): R7-R0 on CN1
  28-35, G7-G0 on 20-27, B7-B0 on 12-19, DE 9, VS 10, HS 11, DCLK 37, DISP 44, ground 5 / 36 / 38 /
  48. CN1's backlight (LEDA / LEDK), DVDD, VCOM and gate rails are left open: nothing on this board
  draws from the BT817 board.
- **U1, the TFP410, set by its pins** (TI SLDS145D, Feb 2024): ISEL low (no I2C), BSEL high (24-bit
  single edge), VREF = DVDD (3.3 V CMOS inputs), DKEN low (no de-skew), EDGE high - data latched on
  the clock's **rising** edge. **JP1** closed makes it the falling edge, for when the BT817's
  `REG_PCLK_POL` is set that way. PD is pulled high (always on); **JP2** closed lets the BT817's DISP
  line power it down with the screen. DATA[23:16] red, [15:8] green, [7:0] blue (Table 6-2); IDCK+
  the clock, IDCK- to ground; RTFADJ 510 ohm 1 % (the DVI swing, 5.3).
- **J2, the HDMI socket** (Molex 2086581001). DVI on HDMI: the four TMDS pairs straight to the
  socket, DC-coupled (the panel's board terminates them); pins 2 / 5 / 8 / 11 / 17 and the shell to
  ground; +5V on pin 18 for the sink; HPD to TP3. **No DDC**: SCL, SDA and CEC are open - a source
  that sends one fixed mode reads no EDID.
- **J3, 5 V in** (JST XH 2-way), about 0.2 A with the HDMI pin's share. **Where the 5 V comes from in
  the Display Unit is not drawn yet** (the carrier has no 5 V outlet): confirm with the unit's
  layout. U2 (AP2112K-3.3) makes the TFP410's 3.3 V.

## Where it stands

**2026-10-13 (Y46): drawn and routed, rev 0.01.** ERC 0; DRC 0 violations, 0 unconnected, 0 parity.
`fab/du-hdmi-bridge-revA-gerbers.zip`, `display-unit/diagrams/du-hdmi-bridge-revA-assembly-{top,bottom}.svg`;
`display-unit/data/du-hdmi-bridge-bom.csv`; its parts are `../../../bench-revA-bridge-digikey-cart.csv` (14 lines).

- **Nothing here is measured (R11).** The board's place in the Display Unit's case, the cable's
  length and fold, and the panel kit's HDMI board are not known. The TFP410's footprint is KiCad's
  TI TQFP-64 with an 8 x 8 mm pad and nine 0.6 / 0.3 mm vias to the back pour - confirm against TI's
  PAP drawing.
- **The TMDS pairs are about 15.5 mm, matched within 0.2 mm,** on a 2-layer 1.6 mm board: not a
  controlled 100 ohm impedance. At 1920 x 720 and 60 Hz (about 100 MHz pixel clock, 1 Gbit/s a
  lane) a run this short works in practice; if the picture sparkles, a 4-layer revision is the fix.
- **Before power, every time:** with the cable fitted and nothing powered, meter J3 pin 2 (ground)
  to a ground pad of the BT817 board. Continuity says the cable is type A and fitted the right way
  round; no continuity means it is reversed, and powering it would short BT817 outputs.
- **The BT817 board's RGB port is rated to 1024 x 600 in its own datasheet** (S-500 p.1); the panel
  is 1920 x 720. Whether its pixel clock reaches about 100 MHz is V-084's bench check, before the
  panel is relied on.

## Rebuilding it

`tools/du_hdmi_bridge_sch.py` draws the sheet and the project; `tools/du_hdmi_bridge_pcb.py` places, routes and pours. Both
run with KiCad's own Python:

```
<kicad python> tools/du_hdmi_bridge_sch.py sch      the symbols, the sheet, the project
<kicad python> tools/du_hdmi_bridge_sch.py pcb      places, routes with freerouting, pours, runs DRC
```

The router is freerouting 1.9.0 (Java 17) at `~/.local/share/freerouting/freerouting.jar`, or named
in `FREEROUTING`; it opens its own window while it routes. Then, from `00-design`:
`python3 tools/fabpack.py <board>` and `<kicad python> tools/assembly.py <board>` for `fab/`, and
`kicad-cli sch export svg` / `sch export bom` (as above) for the picture and the BOM.

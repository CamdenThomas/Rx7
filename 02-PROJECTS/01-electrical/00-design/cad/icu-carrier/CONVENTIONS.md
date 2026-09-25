# Schematic conventions — ICU carrier

*Rev 2026-09-12 · owns: how this schematic is drawn. Short on purpose; §2 is the one that earns its keep.*

## 1 · Sheet structure

One root sheet, **A0**, with five blocked-out areas drawn as dashed boxes and titled, grouped the way
`icu_channels.csv` groups the channels, so a row and its drawing are easy to hold side by side:

| Block | Contains |
|---|---|
| **Power** | `DP-ICU-A 1` logic 12 V and `DP-ICU-A 6` backlight 12 V — **two inputs, never joined on the board** — each with its SS34 and SMBJ33A; the LMR36015-Q1-class 5 V buck; the backlight's 4 A fuse and high-side switch |
| **Bus** | `DP-ICU-A 4/5`, the TCAN1042HVDRQ1, its 3V3 IO, the DNP common-mode choke footprint. **No termination** (D-079 → D-346) |
| **Analog in** | IC01–IC03, IC05–IC07, IC09–IC11 and IC14 — the repeated divider / 100 nF / BAT54S stage, and the J1 / J3 / J7 pull-up jumpers |
| **Pulse in** | IC04 tach (2 × 100 kΩ ½ W, 5.1 V zener, BAT54S, LM393 **on the 5 V rail**) and IC08 road speed (jumper-selected pull-up or divider, Schmitt) |
| **Display and local** | IC21 QSPI header to the BT817 board, IC22 page button, the IMU and the ESP32-C3 |

Two more boxes carry no circuit and are there so the sheet cannot be read as claiming more than it
does: **the processor boundary** on the right, and **what this sheet does not know** at the top right.

There is no 3.3 V regulator on this board. `+3V3` is the Teensy's own output, arriving at the socket
behind a `PWR_FLAG` that says so — D-273 put the radio on the XIAO module's own LDO, so the carrier
never needed one.

## 2 · The rules that exist because of a specific way this board can kill something

1. **Annotate the voltage domain on every power net**: `+12V_LOGIC`, `+12V_BL`, `+12V_BL_SW`, `+5V`,
   `+3V3`. The Teensy 4.1 is **3.3 V only and not 5 V tolerant** — there is no clamp inside it and no
   over-voltage protection on the board. A net that is 5 V on the schematic and 3V3 in the layout is how
   a Teensy dies quietly with the dash already back together.
2. **Every analog input ends in the same three parts, drawn every time**: series or divider resistor,
   100 nF, BAT54S to 3V3 and ground. Do not abbreviate the repeated ones or hide them behind a symbol —
   the whole point of drawing this is that a missing clamp is visible.
3. **The two 12 V inputs never touch.** If a net tie or a shared symbol ever joins `+12V_LOGIC` and
   `+12V_BL`, that is not a drawing error to tidy up later; it is the error the two-diode design exists
   to prevent (D-273). The netlist check in §5 asserts it.
4. **The LM393 sits on 5 V, and the schematic must show that**, because its input range stops ~1.5 V under
   its supply — on 3.3 V the 5.1 V zener node clips. This is the kind of fact that is invisible in prose
   and obvious in a drawing, which is the argument for the drawing.
5. **Values are value fields, never comments.** 100 Ω 1 W is not the same part as 100 Ω 0.25 W at a
   shorted sender; the wattage belongs in the field.
6. **Every net crossing a block boundary is a named label**, not a wire. The netlist gets read by a human.
7. **No DNP or no-connect without a reason in its field.** The choke footprint is DNP *because D-079 →
   D-346 says no termination on this board* — write that. `U2`, the VN5E alternative, carries "fit U2
   **instead of** Q1/Q2/R1–R4, never both".
8. **Reference designators are KiCad's**, and the channel ids (`IC01`…`IC24`) go in a text field beside the
   block, never as the reference. The channel ids belong to `data/icu_channels.csv`; borrowing them as
   refdes would create a second home for them (R3) and they would drift the first time a row changes.
9. **Pin numbers come from the record, never from the sheet.** The Teensy socket `J5` carries the real
   Teensy 4.1 pad numbers because the record has them (`icu_channels.teensy_pin`, D-377); change a pin
   there first, then here. Module pin numbers (buck, transceiver, IMU, radio, BT817 header) are fixed
   against the actual parts at layout. A schematic that quietly picks an answer the record does not have
   is worse than one with a question mark on it.
10. **The BAT54S goes one way round, and it is not obvious.** It is a **series** pair — `A → COM → K` —
    so clamping a signal at `COM` needs **A on GROUND** (GND→COM catches a negative excursion) and
    **K on +3V3** (COM→+3V3 catches a positive one). Backwards it clamps nothing on either polarity and
    leaves a diode path from +3V3 to ground through the sender. Rev 0.01 of this sheet had all twelve of
    them backwards and the picture is what found it; §5's check now asserts it on every clamp.

## 3 · Green before it counts

```text
kicad-cli sch erc icu-carrier.kicad_sch --severity-all -o icu-carrier-erc.rpt
```

ERC violations are errors, not suggestions — the same standing as a `check` refusal. Floating inputs and
pin-type conflicts are exactly the class of mistake this drawing exists to surface, so silencing one is
only ever correct with a written reason in the schematic. **Rev 0.02 is 0 errors and 0 warnings**, and
nothing on it is suppressed or excluded.

Run with `--severity-all`, not just `--severity-error`. The warnings are where the real finds were: an
isolated label, a wire crossing another wire's endpoint, two labels landing on the same coordinate.

## 4 · The picture is part of the work

```text
kicad-cli sch export svg --no-background-color -o . icu-carrier.kicad_sch
```

Commit the SVG. An S-expression diff of coordinate tuples is unreadable, so without a picture a change to
this file cannot be reviewed at all — not by a partner, not by you in three weeks. A PDF reads better at a
desk (`kicad-cli sch export pdf`) but is **not** committed: one picture in the repo, not two.

## 5 · The two things worth checking mechanically, and they are cheap now

Export the netlist and assert them:

```text
kicad-cli sch export netlist --format kicadsexpr -o net.txt icu-carrier.kicad_sch
```

- **`+12V_LOGIC` and `+12V_BL` share no component pin.** That is §2.3, and it is the one error on this
  board that starts a fire rather than kills a chip.
- **Every BAT54S has pin 1 (A) on GND and pin 2 (K) on +3V3.** That is §2.10, and it is the error that
  was actually made.

Netlist *reconciliation against the record* — asserting that every `DP-ICU-A` / `DP-ICU-B` pin here
matches its cavity row and that no pin exists in one and not the other — is a real check and still
belongs **later**, if the carrier is ever fabricated. Today it would be enforcement machinery around a
drawing nothing depends on, and the tree does not need another moving part.

## 6 · What this tool cannot tell you

KiCad checks that a drawing is consistent with itself. It does not know the panel's pixel clock (`V-084`),
whether the LM393's hysteresis survives a trailing coil at 6000 rpm, whether the enclosure grommet clears
the ribbon, or which sender is actually in the car. Those are measurements (R11). A schematic that passes
ERC and a board that works are different claims, and only one of them has been checked here.

## 7 · The symbol library travels with the project

`icu-carrier.kicad_sym` holds every symbol the sheet uses — the stock ones flattened, and the functional
blocks drawn for this board — and `sym-lib-table` points KiCad at it. Nothing depends on which KiCad
libraries are installed, so the sheet opens the same after a reinstall, ERC has no
missing-library complaints, and a KiCad upgrade cannot silently change what a symbol means.

Add a symbol to that file, not to a global library.

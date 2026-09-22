# ICU carrier — the KiCad project

*Rev 2026-09-12 (rev 0.02 of the sheet) · owns: what this KiCad project is for, what it may
claim, and how to start. The board's design is `../../data/icu_channels.csv` — that is the
record; this is a drawing of it. Read `../README.md` first: it is the fence.*

## Where it stands

**The schematic is drawn, all five blocks, and ERC is clean at zero errors and zero
warnings.** Power, bus, the nine analog channels plus the illumination reference, both
pulse inputs, and the display-and-local block. About 200 symbols, 95 named nets.

**It has already earned its keep.** The first pass had **every BAT54S clamp wired
backwards** — anode to +3V3 and cathode to ground instead of the other way round. Drawn
that way the clamp catches nothing on either polarity and puts a diode path from +3V3 to
ground straight through the sender. The prose the record carries — *"→ 100 nF → BAT54S to
3V3 / GND"* — is completely correct and completely silent about direction, which is the
argument for the drawing made in `../README.md`, arriving on the first attempt. It is
fixed, it is checked mechanically now, and the sheet says out loud which way round it goes
and why.

## Why it exists

1. **To learn KiCad on something real.** A tutorial board teaches the keystrokes and
   nothing else. This one is already specified down to the resistor values, so the design
   work is done and the only thing left to learn is the tool. Whatever comes next that
   needs a PCB, the practice is already paid for.
2. **Because the analog front end cannot be reviewed as prose.** See `../README.md`.

## What it may and may not claim

**May:** how the parts on the carrier connect to each other — divider ratios, clamp
placement, the pull-up jumpers, the comparator's hysteresis network, decoupling, what
shares a rail, and what the ERC thinks of all of it.

**May not:** anything about the car, the harness, or the drops. `DP-ICU-A 1` and
`DP-ICU-B 4` appear here only as pins on the board edge; what is on the other side of them
belongs to `cavities.csv`. **If this schematic and the record disagree, the record is
right.**

**Two things this revision deliberately does not assert, and says so on the sheet:**

- **No Teensy pinout.** The record assigns no Teensy pin numbers anywhere — `icu_channels`
  says "ADC", "digital, input capture", "QSPI header", "I²C", "Serial2 + 2 GPIO" and
  stops. So the Teensy is drawn as the **socket** it plugs into (`J5`), with one named
  functional pin per net that crosses the boundary and ordinal numbers that mean nothing.
  Putting a pinout here would put facts on the sheet that the record does not have.
- **No module pin numbers.** The buck, the transceiver, the IMU, the radio and the BT817
  header are functional blocks. Their pin *names* are real; their pin *numbers* are fixed
  against the actual parts at layout (`F2`).

**And R11 applies with full force:** none of this has been measured. A schematic that
passes ERC is internally consistent, not correct. The panel timings, the tach comparator's
real noise margin, and every sender curve are still unmeasured — drawing them neatly does
not close them. The sheet carries its own "what this sheet does not know" panel, and
`TARGET.md §6` is the same list.

## Scope: schematic yes, PCB not yet — superseded 2026-09-21

> **Layout is now in scope** (D-361): Camden asked for the full layout and 3D guide, and ICU
> layout was already his step `F2`. Follow `../PCB-AND-3D-GUIDE.md` Part A. The paragraph below
> is kept for why it used to say no. Its last point still stands: **fabricating** (ordering
> boards) is money with a lead time, and it stays Camden's.

Capture the schematic. Do not lay out a board until there is a reason to, and "I have a
schematic" is not one. The carrier can be protoboard for bring-up, and fabricating one is
a decision with a lead time, a cost and a revision cycle attached — which makes it **big**
by §3, so it is a block before any time goes into `.kicad_pcb`, not an assumption because
the file exists. There is no `.kicad_pcb` in this folder on purpose.

## Opening it

KiCad 10.0.6 is installed at `C:\Program Files\KiCad\10.0`; `kicad-cli.exe` is in its
`bin\`. Open `icu-carrier.kicad_pro` and the sheet is there — A0, five blocked-out areas.

**Every symbol it uses is in `icu-carrier.kicad_sym`, beside the project**, with a
`sym-lib-table` pointing at it. Nothing depends on which KiCad libraries happen to be
installed, so the sheet opens identically on the laptop and on `crashs-pc`, and ERC has no
missing-library complaints to make.

## Checking it

```
kicad-cli sch erc icu-carrier.kicad_sch --severity-all -o icu-carrier-erc.rpt
kicad-cli sch export svg --no-background-color -o . icu-carrier.kicad_sch
```

ERC violations are errors, not suggestions — the same standing as a `check` refusal. The
report is gitignored; the **SVG is committed**, because an S-expression diff of coordinate
tuples cannot be reviewed by anyone, including you in three weeks. A PDF
(`kicad-cli sch export pdf`) is easier to read at a desk and is gitignored for the same
reason a second copy of any fact is: one picture in the repo, not two.

## Files

| File | What |
|---|---|
| `icu-carrier.kicad_pro` · `.kicad_sch` | the project and the schematic |
| `icu-carrier.kicad_sym` · `sym-lib-table` | every symbol used, kept with the project |
| `icu-carrier.svg` | the committed picture — the reviewable form of a change |
| `CONVENTIONS.md` | how to draw it so it stays reviewable |
| `TARGET.md` | what has to be on the sheet, from `icu_channels.csv` — a snapshot, not a link |

`.kicad_prl`, `*-backups/`, `*.kicad_sch-bak`, autosaves, the ERC report, the netlist and
the PDF are gitignored.

## What to draw next

Nothing, until something in the record changes or a bench result arrives. The open ends
are all measurements, not drawings:

- `Q-308` picks an oil-temperature sender and IC07's pull-up stops being a question mark.
- `V-084` settles the BT817's pixel clock and sync polarity against the real panel.
- `D-261`'s three-point sender reads make IC01 and IC03 curves rather than dividers.
- The tach front end is a bench result: LM393 or H11L1, and the hysteresis values on this
  sheet are a proposal derived here, not a fact from the record.
- `F2` lays out the carrier — and only then do module and socket pin numbers mean anything.

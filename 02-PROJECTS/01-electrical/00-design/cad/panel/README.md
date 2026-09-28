# Control panel — the KiCad project

*Rev 2026-09-28 (sheet rev 0.01) · owns: what this KiCad project is for and what it may claim. The
panel's design is `../../../data/panel_ribbon.csv` and `dcu_channels` SN18–SN20 (D-380). Read
`../README.md` first: it is the fence.*

## Where it stands

**The schematic is drawn and ERC is clean** (2026-09-28, D-452). It has nine keys on a 3 × 3
matrix, with one 1N4148W per key, anode toward the column. A row driven low pulls its column low
through the diode, so any combination reads true and a press with every row held low wakes the
DCU. It also has four detented encoders common to GND, the thumbstick (two pots across +3V3 and
its own AGND, a push to GND), and the 20-way IDC header, pinned as `panel_ribbon`. The panel has
no processor, no CAN node and no 12 V on the ribbon (D-355, D-380).

## What is not decided, and is not drawn

- **Lights:** block 01.14. The ribbon has no conductor for indicators today.
- **A board or hand-wired:** block 01.15. The schematic holds either way.
- **What the keys and knobs look like:** luxury block 03.14. That choice fixes the switch
  footprints and the backlighting.
- **Where everything sits:** the centre-stack opening, `V-113`, then the faceplate (luxury
  `LP20`).
- **The thumbstick:** `P156`, not chosen. It is drawn as a functional block.
- **Illumination:** its own lead from `L3-S1 8` (DV53). The input connector is on the sheet with
  both pins no-connect until the lamps are known.

`H-008` lays it out once those are in.

## Checking it

```
kicad-cli sch erc panel.kicad_sch --severity-all -o panel-erc.rpt
kicad-cli sch export svg --no-background-color -o . panel.kicad_sch
```

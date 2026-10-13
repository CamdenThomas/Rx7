# harness/cad/connectors — the DEUTSCH housings in 3D for the app

*Rev 2026-10-13 (D-514, D-515, Y24) · owns: how each connector variant the harness uses becomes
one glb for the Design page. Owns no dimension: they are 01-REFERENCE `connector_dims`, one row
per variant, each figure with where it was read or that it was estimated, every one confirm (R11).*

## What it is

`build_connectors.py` reads `connector_dims` through `rx7.py sql` and writes one glb per variant -
the five DT06 plugs, the five DT04 receptacles, the four DTP halves and the three DT13 headers the
`housings` name - and `manifest.json` beside them. A variant whose `cad` row points at a vendor
model on this machine, in a frame the builder knows (`FRAMES`), is converted from that model;
every other one is drawn as a stand-in from its row:

| Half | Drawn |
|---|---|
| plug (DT06, DTP06) | the body with its wire-seal end a little smaller behind it; the latch on top; the wedgelock set into the face; the cavities as dark holes in their rows |
| receptacle (DT04, DTP04) | the shroud in front of the origin with its latch ramp; the body and seal end behind; the wedgelock on the shroud's floor; the pins standing in it |
| DT13 header | the shroud (the nose), the flange with its two mounting holes, the body and the PCB tails behind it |

As built on the Mac (2026-10-13): the three DT13s are TE's own models (`cad`
`deutsch-dt13-6p-te`, `-08pa-te`, `-12pa-te`, in `01-REFERENCE/model/library`, out of git) - the
same files the DCU and ICU carriers' footprints and the unit mock-ups use, so the two agree by
construction. The DT and DTP models were downloaded on the PC (their `cad` rows) and have never
been opened here; until their frame is read and added to `FRAMES` (Y27) they are stand-ins.

## The convention (the scene's, `00-design/README.md` §13)

Millimetres, z up, the part's own frame. The mating face is centred on the origin - a plug's front
face, a receptacle's shroud floor, where the plug's front face lands - the mate is along +Y and the
wires leave along -Y, so a mated pair is the receptacle and the plug turned half a turn about Z.
Z up is the housing as it is read: the latch, the ramp, the DT13 flange's top (its PCB tails
point down). X runs along the cavity rows. Nodes: `body`, `latch` (plug) or `shroud`
(receptacle), `flange` (DT13), `cavities`, `wedgelock`; a converted model carries `body`,
`flange` and `shroud` only (TE's simplified models draw no pins). Colours are for telling the
families apart, not TE's: DT grey, DTP black, DT13 grey with a darker flange, the wedgelock orange.

`manifest.json`: `{variant: {glb, family, half, ways, size_mm {x, y, z} (the glb's box, measured),
bbox_mm, origin, confirm, source (the row's source, or the cad row for a model), standin, cad,
bytes, nodes, stamp}}`. It is committed; the glb files are not (`.gitignore`, as every glb under
`02-APP/app/public/design`).

## Rebuild

```
python3 02-PROJECTS/01-electrical/00-design/harness/cad/connectors/build_connectors.py               all (about 2 min)
python3 02-PROJECTS/01-electrical/00-design/harness/cad/connectors/build_connectors.py --only DT06-8S one, merged into the manifest
python3 02-PROJECTS/01-electrical/00-design/harness/cad/connectors/build_connectors.py --check        are the files current?
python3 02-PROJECTS/01-electrical/00-design/harness/cad/connectors/build_connectors.py --selftest     hold the files to the rows
```

From the tree's root (on the Mac, `env DEVELOPER_DIR=...` as every python3 call); `--out DIR` for
elsewhere, `FREECADCMD` for another FreeCAD. `build_all(out_dir, only=None)` returns the manifest
for the scene's export (Y26). Exit 0 built / current / passed; 1 a housings variant with no row, a
glb whose box is more than 1 mm off its row, or a stale file under `--check`; 2 under `--check`,
not built on this machine; 3 a usage error or a tool crash.

## What is confirm

Everything. The DT and DTP boxes are TE's models' bounding boxes as the `cad` rows record them
(whole millimetres), with width and height told apart by the cavity rows, unchecked. The contact
pattern is TE 114-151046's straight-header layouts (4.45 along a row, the 8-way's 5.46 middle gap,
rows 9.12 apart; the 2-way 5.46); the DTP pattern, the DTP shroud, the cavity sizes and every
latch, ramp, wall and seal-end proportion are estimated. A DT04's shroud depth is its DT13
sibling's, measured in the model (the same DT06 plug mates both). A part in hand or TE's own model
replaces every one of them.

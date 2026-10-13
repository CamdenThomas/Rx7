# harness/cad/devices — the devices at the legs' far ends, in 3D

*Rev 2026-10-13 (D-515, work row Y28) · owns: how the devices and the harness's common parts are
modelled for the app's Design page - which were found online, which are drawn here and from what
numbers, and the manifest the export reads. It owns no fact about the car: the record says what
each device is and where; this folder only draws it.*

## What it makes

```
python3 02-PROJECTS/01-electrical/00-design/harness/cad/devices/build_devices.py              build all (about 15 s)
python3 .../build_devices.py --only relay-micro-iso    one model, then the manifest
python3 .../build_devices.py --check                   are the glb files current?
python3 .../build_devices.py --selftest                hold the manifest to its contract
```

From the tree's root (on the Mac, `env DEVELOPER_DIR=/Library/Developer/CommandLineTools`
before each). It needs `freecadcmd` (FreeCAD 1.1; `FREECADCMD` overrides). It writes into
`02-APP/app/public/design/01-electrical/devices/` (`--out DIR` names the folder above it):

- `<model>.glb` - one per model, git-ignored like the other glb files; 47 models, about 8 MB.
- `manifest.json` - committed. One entry per device (`DV46`) or common part (`P003`; another
  area's qualified like a gate, `03-luxury:LP58`, `00-CAR:P-002`): `glb`, `name` (the record's
  words), `kind` (`device` or `module`), `node` (the scene.json part it sits at), `count` there
  and `also` (other nodes and counts), `size_mm` (the glb's box, measured), `origin`, `standin`,
  `cad` (the 01-REFERENCE cad row of a found model, else null), `confirm` (always true), `source`,
  and for a stand-in its `params`, each number with its source. `_meta` holds the version, the
  devices with no model and why (`none`), and each model's bytes, box and staleness stamp.

Exit 0 built / current / passed; 1 the manifest breaks its contract (a glb of other bytes, a
device with neither an entry nor a reason, a node the scene lacks, a found model whose cad row
is not in the record) or, under `--check`, a stale model; 2 under `--check`, not built here; 3 a
usage error or a crash (FreeCAD missing, a found model's file not on this machine).

## Found first (D-515)

A model is looked for before one is drawn: the vendor's CAD, then a community model whose
licence allows the use. What was kept, each a cad row with its licence, its file under
`01-REFERENCE/model/library/electrical/<cad id>/` (git-ignored: the licences vary and the
repository is public):

| Model | Stands for | From |
|---|---|---|
| `teensy41` | P142, on both carriers | XenGi's teensy.pretty STEP (MIT) |
| `xiao-esp32c3` | P116 | the generic XIAO STEP from the FrogPad repo (MIT); the C3's own model is behind GrabCAD's login |
| `display-12p3` | DV46 / P118 | Waveshare's 12.3inch HDMI LCD 3D file (free download) |
| `pololu-g2-24v21` | DV55 / luxury LP18 | Pololu's md31b STEP (free download) |
| `atc-block-4` | P001, blocks A and B | OptiFuse's BLR-504 STEP (free download) |

FreeCAD reads the STEP, `rot` in FOUND turns it z up, its box's base centre goes to the origin,
and each face is coloured as the STEP colours it (export_glb_fc.py's reader, borrowed from its
source so it is written once). One glTF node per top-level part, `part:<label>`.

## Drawn where nothing was found

Everything else is a stand-in: a recipe in STANDINS, its numbers in PARAMS with their sources -
a drawing read here (the Song Chuan 871's outline for the micro relay, the ME817EV's figure for
the BT817 board, FEETECH's spec sheet for the servo, D-239 for the battery, a retailer's listing
for the Blue Sea 5028) or `estimate` with its basis. Each keeps one recognisable feature: a
relay's tab row, a holder's cap and leads, a block's studs and clear cover, a speaker's cone, the
blower's flange and wheel. One glTF node per named primitive, `standin:<name>`. A found model
replaces a stand-in when it arrives: add it to FOUND, point the entry at it, rebuild.

## What has no model

`_meta.none` says why for each: a ground strap and the star studs are the harness's and the
scene's nodes; the horn pad is the wheel's; the dash lamps are bulbs in factory panels; the defog
grid is on the glass; the ICU, the DCU, the control panel and the left plate (the CUR) are the
units' and boards' own glb files, already in the scene; the wink switches are on the left
plate's board.

## The rules

Nothing here is measured (R11): every entry is `confirm`, every place a node's provisional spot,
every stand-in number a drawing's or a guess. A measured number beats every one of them, and
the row it belongs in is the record's, not this file's. The builder reads the record only
through `rx7.py export` (01-electrical devices, relays, fuses, parts; 01-REFERENCE cad) and
scene.json, and writes nothing to the record.

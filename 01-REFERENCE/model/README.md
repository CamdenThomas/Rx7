# The 3D models: the bought SA body (S-037) and the free CAD library (D-418)

A bought artist's model of a **1978 RX-7 (SA)**, not the FB. The body shell, glass, lamps
and wheels are right to within about 1 % overall. The bumpers, tail lamps, front lip and
dash differ from the FB, and there is no engine bay, underbody or chassis. Nothing about
the car is measured from it (CLAUDE.md R11).

**The model stays on this PC.** The repository is public and the model is a bought file,
so the zip and everything built from it are in `.gitignore`. To restore it, put
`1978-mazda-rx-7-mk1-sa.zip` back in this folder and build.

| File | In git | What it is |
| --- | --- | --- |
| `1978-mazda-rx-7-mk1-sa.zip` | no | the download, three zips deep, one OBJ inside |
| `build.py` | yes | Blender script: builds everything below |
| `rx7.glb` | no | a lighter copy (about 280k triangles, 5 MB) for the app's 3D view (D-415) |
| `landmarks.json` | no | each part's centre and size in mm, for `estimate.py` |
| `estimate.py` | yes | rough route lengths into `routes.model_ft` (D-416) |
| `10-gui/app/public/car/*.webp` | yes | the app's renders: pictures, not the model. Written by `blend.py` from the FB since D-420 (`build.py --renders` still makes the SA's) |

## Build

```
blender -b --factory-startup -P 01-REFERENCE/model/build.py     # about a minute
python3 01-REFERENCE/model/estimate.py --write                  # sets routes.model_ft
```

Run both from the tree root. Axes in `landmarks.json` and `estimate.py`: millimetres, x to
the car's right, y toward the front, z up, ground at z = 0. The car's centreline is x = 47.
The node positions in `estimate.py` are assumptions, one line each. When the car is apart
and a node is placed, correct its line and run the estimate again.

## The free CAD library and the combined FB model (D-418)

Every free model, scan and drawing found for the car and the projects' parts is a row in
`01-REFERENCE` table `cad` (what it is, where from, its licence, its size, whether it is here).
The files are in `library/<category>/` and, like the SA model, never go in git: the
licences vary and the repository is public. A row with `login=yes` needs an account to
download; its `url` is kept so it can be fetched by hand into `library/<category>/<id>/`.

| File | In git | What it is |
| --- | --- | --- |
| `library/` | no | the downloads, one folder per `cad` row, and each search's `manifest.jsonl` |
| `catalog.py` | yes | imports new manifest lines into `cad` (never overwrites a row) |
| `blend.py` | yes | Blender script: builds the one combined model |
| `out/rx7-fb.blend`, `.glb` | no | the combined model: one collection per `blend` row |
| `rx7-fb.glb` | no | the app's 3D view (D-420): the FB body, the SA's wheels and the tail-lamp scans, in cm, centred |
| `out/checks.json`, `*.png` | no | every check against the factory figures, and the renders |

```
python3 01-REFERENCE/model/catalog.py --write              # after a new search
blender -b --factory-startup -P 01-REFERENCE/model/blend.py  # about ten seconds
```

The combined model's frame: millimetres, x to the car's right, y forward, z up, ground at
z = 0, **the front axle at y = 0**, centreline x = 0 (not the SA model's x = 47). Each
piece, its source, how it was scaled and placed, and its error against the factory is a
`blend` row. The factory figures are 00-CAR specs, named beside each constant in
`blend.py`; every other number there is an assumption and says so. Nothing about the car
is measured from any model (R11).

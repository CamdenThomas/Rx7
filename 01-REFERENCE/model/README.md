# The 3D body model (S-037)

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
| `10-gui/app/public/car/*.webp` | yes | the app's renders: pictures, not the model |

## Build

```
blender -b --factory-startup -P 01-REFERENCE/model/build.py     # about a minute
python3 01-REFERENCE/model/estimate.py --write                  # sets routes.model_ft
```

Run both from the tree root. Axes in `landmarks.json` and `estimate.py`: millimetres, x to
the car's right, y toward the front, z up, ground at z = 0. The car's centreline is x = 47.
The node positions in `estimate.py` are assumptions, one line each. When the car is apart
and a node is placed, correct its line and run the estimate again.

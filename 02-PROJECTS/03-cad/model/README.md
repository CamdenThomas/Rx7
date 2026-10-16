# 03-cad/model - the scripts that build the car model

*Rev 2026-10-13 · owns: what this folder may hold, how the model is built, and the scene contract the
app's Manual model page is built against (C01's hand-over to 02-APP MG1). The project's design is
`../data/`; D-477 opened it, D-516 (through the app), D-517 (every part as it comes off) and D-518
(the unibody first) rule how it is built.*

Scripts only. The model files - the glb files, the STEP files, anything made from a found model -
stay out of git (D-477, D-418; 02-APP P55 is open on where they live): `out/` here is ignored, and so is every `.glb` under `02-APP/app/public/design/`. `scene.json`
is committed. The frame is D-418's: millimetres, x to the car's right, y forward, z up, ground z = 0,
front axle y = 0. **Nothing here is a source of facts about the car**: a measured number beats the
model, and every dimension nobody measured carries `confirm` (R11). Today that is every dimension.

## Contents

1. The files
2. Building it
3. The parts, and how they are named
4. scene.json - the contract (C01)
5. Where every number comes from
6. What is confirm, and what is missing

## 1 · The files

| File | What | Record rows |
|---|---|---|
| `coverage.py` | A01: what exists for every 00-CAR part - a model file, a placement in the combined model, a factory dimension, a found model by name (a hint), a catalogue figure, or nothing - derived from the tables each time, never typed back | 00-CAR `parts`, `specs`; 00-CAR `cad`, `blend` |
| `frame.py` | The frame and hard points: 03-cad `datums` read through `rx7.py sql` every build, numbers parsed, raw text kept | 03-cad `datums` |
| `partlib.py` | The shared half: `Dim` / `part` declarations (pure python); the solids (plate, sheet strips, loft, box sections, revolve, mirror), the tessellation and the glb and STEP writers (FreeCAD). The glb writer is 02-electrical's `export_glb.write_glb`, imported, not copied | - |
| `placing.py` | Places composed through parents into the car's frame (three.js Euler XYZ), the file names | - |
| `build.py` | The command: runs FreeCAD headless once per assembly, then the scene | reads `datums` |
| `fc_run.py` | FreeCAD's half of `build.py` (never by hand): one glb per part, one STEP per assembly, a meta JSON | - |
| `corner/params.py`, `corner/geometry.py` | A04, the tool-chain proof: the front-left corner - road wheel, tyre, hub with its disc, four wheel nuts | 00-CAR `specs` SP-113, SP-124, SP-126, SP-128, SP-1513, SP-1519, SP-1520; `datums` DT02 |
| `unibody/params.py` | B01's core: **the one table** of the unibody's governing dimensions, each with how it is known and its source; the panels, their places, mates and take-apart moves; the checks against the datums | `datums` DT02-DT14; `specs` SP-1280, SP-1281 |
| `unibody/geometry.py` | The panels as rough sheet solids, from `params.py` alone | - |
| `unibody/silhouette.py` | Re-derives the found shell's stations that `params.py` cites (read only) | 00-CAR `cad` |
| `skin/params.py`, `skin/build.py` | B01's second pass (D-563): the home page's FB model (`02-PROJECTS/03-cad/model/sa/rx7-fb.glb`, read only) cut by its materials and names into the skin, glass, trim, tail lamps and three wheels, put in the car's frame; pure python | `datums` DT02, DT03 |
| `skin/stations.py` | The found model sliced every 50 mm: the stations `unibody/params.py`'s `HOME` figures cite (read only) | - |
| `skin/fit_check.py` | Which unibody panels still stand outside the skin, and by how much (read only) | - |
| `skin/glbread.py` | A minimal glb reader for the two above | - |
| `export_scene.py` | `scene.json` for the app; the selftest; the record drafts (`--drafts`) | 00-CAR `parts`, `systems` |
| `found/` | The found models' scripts (moved from the reference, 06-intake T2): `build.py` and `blend.py` (Blender), `catalog.py`, `locate.py`, `estimate.py`, and `paths.py`, the one place the library's and the bought SA model's folders are named. Their own README is `found/README.md` | 00-CAR `cad`, `zones`, `parts`; 03-cad `blend`; 02-electrical `routes.model_ft` |
| `render_check.mjs` | Loads the scene and every glb with the app's three.js and rasterises five views (one exploded) to PNG - no WebGL | - |

## 2 · Building it

From the tree's root; on the Mac every python3 call is
`env DEVELOPER_DIR=/Library/Developer/CommandLineTools python3 …`.

```
python3 02-PROJECTS/03-cad/model/build.py                   every assembly and scene.json (seconds on the Mac)
python3 02-PROJECTS/03-cad/model/build.py --only unibody    one assembly (corner | unibody | skin), then scene.json
python3 02-PROJECTS/03-cad/model/build.py --only scene      scene.json alone, from the last build
python3 02-PROJECTS/03-cad/model/build.py --selftest        hold scene.json to the contract and the datums
python3 02-PROJECTS/03-cad/model/build.py --drafts DIR      also write model_parts / model_dims / model_mates
                                                            and 00-CAR parts drafts (CSV, exact columns) to DIR
node 02-PROJECTS/03-cad/model/render_check.mjs [DIR]        does it load in three.js; PNG views into DIR
python3 02-PROJECTS/03-cad/model/unibody/silhouette.py      the found shell's stations, re-derived
python3 02-PROJECTS/03-cad/model/skin/stations.py           the home-page model's stations
python3 02-PROJECTS/03-cad/model/skin/fit_check.py          panels standing outside the skin
```

The skin needs no FreeCAD, only the found model at `02-PROJECTS/03-cad/model/sa/rx7-fb.glb` (out of git, on
each machine as the home page's car); where it is absent the skin is skipped and the scene is the
other two assemblies.

Exit 0 built / holds; 1 an assembly refuses its parameters (`params.check`) or the scene breaks the
contract; 3 a usage error or a tool crash. It needs `freecadcmd` (FreeCAD 1.1, `FREECADCMD`
overrides) and, for the render check, node and `02-APP/app/node_modules` (three 0.186). It reads the
record only through `rx7.py` and writes nothing to it: the drafts are for a person or the overseer
to load. Each machine rebuilds the glb files before the app is built, as the electrical ones are.

**What it writes**: `02-APP/app/public/design/00-CAR/scene.json` (committed, ~120 KB),
`…/00-CAR/corner/*.glb` (4 files, 0.47 MB), `…/00-CAR/unibody/*.glb` (46 files, 0.33 MB) and
`…/00-CAR/skin/*.glb` (11 files, 5.1 MB) -
mm, z up, the part's own frame, the electrical writer's packing (`KHR_mesh_quantization`); and
`out/corner.step` (0.13 MB), `out/unibody.step` (1.35 MB) - each assembly's solids in the car's
frame, labelled by part id - with each assembly's `out/<assembly>.meta.json`.

## 3 · The parts, and how they are named

One solid per part as it comes off the car (D-517), named by its 00-CAR `parts` id. Where one
`parts` row covers a pair or a set, each piece is its own solid with a suffix (the record names the
row in the scene's `record`; the overseer declares the convention in the record):

- `-L` / `-R` - a left-right pair (`PT755-L`, `PT755-R`); left is x negative
- `-FL` - the corner (`PT525-FL`: the front-left road wheel; `PT526-FL`: its four nuts, one glb with
  four nodes `part:PT526-FL#1..4`)
- `-front` / `-rear` - the two roof headers (`PT773-front`, `PT773-rear`)
- `PT704-skin` / `PT704-trim` - the found model's painted body and its other surfaces, one solid each
  under the shell's row until the closures are parts of their own
- `NEW:<slug>` - a part with no 00-CAR row yet (`PT976-L/-R`, the B-pillar and sail);
  the draft `00-CAR_parts_new.csv` proposes the row, and the overseer replaces the placeholder
- `hp-…` - hard points as nodes (no solid): holes A, B, C, E, F, the fender nuts (DT14), the rear
  wheel centres (DT03), the right front wheel centre (DT02) and the overall length's two ends (DT04)

**The corner** (A04): `PT042-FL` front rotor hub and disc (its origin the wheel-mounting face, ET 20
outboard of DT02), `PT525-FL` road wheel (origin on DT02, the rim's centre plane), `PT530-FL` tyre
and `PT526-FL` nuts (children of the wheel, placed in its frame). The part frame is the axle: +x
outboard; a left wheel is turned `rz 180`. Mates: wheel bolted to hub (nuts PT526), tyre fits-in
wheel, nuts bolted to wheel; the hub has none yet (its knuckle is not modelled).

**The unibody** (B01, 46 solids under `PT704`, the shell, a node at the car's origin): front and
rear floor pans (PT778 with the tunnel, PT779), the floor cross members (PT781, three in one solid),
the front side frames (PT755-L/R, origin at hole A) and the rear side frames with the upper link
brackets (PT780-L/R, origin at hole B; the record has no row for the brackets), the torque boxes
(PT782), the outer and inner sills (PT771, PT783), the toe board and firewall (PT756) and the upper
dash panel (PT757), the plenum front (PT762) and the cowl under the windshield (PT764), the cowl
sides (PT766), the hinge pillars (PT769) and the windshield pillars (PT770), the centre pillars and
sails (NEW), the roof rails (PT767), the roof headers (PT773-front / -rear), the roof (PT774, its top
on DT06), the quarter panels with the rear arches (PT768, their arch lip on DT05's half-width), the
rear wheelhouses (PT777), the cargo side decks (PT784), the aprons with the strut towers (PT754),
the engine bay side panels (PT761), the rain rails - the hatch opening's side gutters (PT772), the
radiator support (PT753), the nose panel (PT752), the rear end panel (PT775) and the rear skirt
(PT776). The hatch aperture is its pieces: PT773-rear, PT772-L/R and PT775's top. Every panel is
welded; its `mate` names what it is welded to (the floor pan PT778 is the root) and the move that
takes it off.

**The skin** (B01's second pass, D-563; 11 meshes): `PT704-skin` the painted body (hood, fenders,
doors, hatch and bumpers in one piece, clipped to the shell, apart straight up), `PT729` all the
glass, `PT704-trim` the rubbers, garnishes, mirrors, seals and a rough cabin, `PT601-L/R` the tail
lamps, and the found model's FR, RL and RR wheels and tyres (`PT525-*`, `PT530-*`, their origins on
DT02 / DT03). The found model is already at factory size, so it is only turned into the car's frame
(X = 10x, Y = -10z - 1210, Z = 10y from its own units). The FL corner's meshes are left out: that
corner is the corner assembly's. The unibody's outline (`unibody/params.py` `HOME`, `HOME_FIT`) was
re-read off this model's stations so the panels sit inside it; `skin/fit_check.py` lists what still
stands out (the A-pillars by about 30 mm).

## 4 · scene.json - the contract (C01)

The electrical Design page's contract (02-electrical `00-design/README.md` §13), version 2, with the
car's fields. Only add fields; never change one.

```
{"version": 2, "built": "<iso>", "project": "00-CAR", "car": true,
 "frame": {"units":"mm","x":"right","y":"forward","z":"up","ruling":"D-418",
           "glb":"mm, z up, the part's own frame","rotation":"degrees, three.js Euler order XYZ"},
 "systems": [{"id":"<00-CAR systems id>","name":"…"}],
 "parts": [{"id":"<00-CAR parts id, suffixed per §3>","name":"…","kind":"body"|"part"|"node",
            "system":"<systems id>","zone":"<zones id>","glb":"<file>.glb"|null,"bytes":n,
            "parent":null|"<part id>",
            "place":{"x":..,"y":..,"z":..,"rx":0,"ry":0,"rz":0},
            "place_from":"datum DT10"|"FSM S-002 p.14-24"|"blueprint"|"found model <cad id>"|"guess",
            "confirm":true|false,"size_mm":{"x":..,"y":..,"z":..},"origin":"<one line>",
            "made_from":"measured|factory|found|catalogue|guess","state":"rough|dimensioned|confirmed",
            "mate":{"to":"<part id>","kind":"welded|bolted|clipped|pressed|pivot|sits-on|fits-in|slides",
                    "fasteners":["<00-CAR parts id>"],"apart":{"x":..,"y":..,"z":..}} | null,
            "children":[...],"source":"<script (params source)>",
            "record":"<00-CAR parts id>"|null,"record_name":"…","side":"L"|"R"|"FL"|null,
            "world":{"x":..,"y":..,"z":..,"rx":..,"ry":..,"rz":..},"nodes":["body:<id>"],
            "assembly":"corner"|"unibody","dims":[{"dim","value_mm","how","source"}],"note":"…"}],
 "links": [], "legs": [], "missing": [{"what","why"}], "notes": ["…"]}
```

- `place` is in the parent's frame, as in the electrical contract; `world` is the same place in the
  car's frame (added). The shell `PT704` sits at the car's origin unturned, so a panel's place is its
  world; the corner's tyre and nuts are placed in the wheel's frame.
- `mate.apart` is the move (car frame, mm) of a part away from `mate.to` when the car is taken
  apart; a chain adds them (the render check's exploded view does exactly that).
- Glb node names are `body:<id>` for a panel, `part:<id>` for the corner; three.js strips `:`, the
  written name is in `userData.name`.
- `--selftest` holds: ids unique; parents and children agree; every mate resolves and its kind is
  one of the eight; every glb present and its bytes the scene's; every body and part has a 00-CAR
  system and a zone; the shell's box on the datums - roof top on DT06 (1259.8), half-width on DT05
  (834.4), its lowest point above DT07 (144.8), `hp-front-end` to `hp-rear-end` on DT04 (4320.5),
  the front-left wheel on DT02 and the rear wheel centres on DT03.

**The numbers it holds today** (2026-10-13, D-563): 79 parts - 46 body, 15 part, 18 node; 64
unibody, 11 skin, 4 corner. The shell's box x -834.4 .. 834.4, y -3170 .. 730, z 149.6 .. 1260.2;
the skin with its bumpers takes y to about +928 and -3392 (`front_oh`, `rear_oh`); wheel centres on
DT02 / DT03 (wheelbase 2420).

## 5 · Where every number comes from

Each dimension's row in `unibody/params.py` (and `corner/params.py`) carries `how`
(measured | factory | found | catalogue | derived | guess), its source and a note; where the blueprint
and the found shell both speak to an outline dimension, the note says which won (`WON`). The sources:

- **03-cad `datums`** DT02-DT14 (the factory hard points, read each build) and 00-CAR `specs`
  SP-1280 (wheel centre to fender line, front 364), SP-1281 (section G-G 435).
- **The FSM body checking dimensions**, S-002 1985 FSM section 14 p.14-24 (also 00-CAR cad
  `fb-rx7-1985-fsm-body-checking-dimensions`). Hole A's place lengthwise, C, E and F lengthwise, and
  the heights 345 / 110 / 339.4 are read off its plan and side views - the drawing is not to scale,
  so an undimensioned point is interpolated between its dimensioned neighbours, and each says so.
  Readings that are judgement: A 580 forward of the front axle (the strut-tower circle over the
  axle); 345 is C's height, 110 E's, 339.4 F's (it may be E to F); b = 107 is the front rail's depth.
- **The blueprint**, 00-CAR cad `fb-rx7-blueprint-the-blueprints-83684`
  (`02-PROJECTS/03-cad/model/library/body/…/mazda-rx-7fb.png`, 2483 x 2546; free to view and download for
  modelling, the site's terms). Its views are not at one scale, so each axis is scaled to a factory
  figure: 1.816 mm/px lengthwise between the axles (DT03), 1.737 over the overhangs (DT04 less
  DT03), 1.750 in height (DT06), 1.762 across (DT05).
- **The found shell**, 00-CAR cad `fb-rx7-gsl-se-85-3dwarehouse-blastronaut` (quality 3; 3D
  Warehouse General Model License), from the model library. Scaled to the factory length it puts its
  axles 2430.6 apart, so it is scaled to DT03's wheelbase (0.9628) - at most 17 mm different at the
  ends - and lifted 59.5 mm (it is a lowered tuner) to put its roof on DT06. It checks the
  blueprint's greenhouse and sill (`unibody/silhouette.py`).
- **The corner**: 5-J x 13 (SP-1513), 185/70HR13 (SP-128), ET 20 (SP-1520, secondary), 4 x 110
  (SP-1519, secondary), M12 x 1.5 (SP-124), the 19 mm nut (PT526's note), the disc's 202 effective
  diameter and 18 thickness (SP-113); the J flange 17.5 is a catalogue figure.

## 6 · What is confirm, and what is missing

**Everything is confirm** - no dimension is measured. The guesses that move the most, the first to
measure as the strip proceeds (block 05.03 decides how): the underbody datum line's height above the
ground (60) and so the floor (210) and every hole's height; hole A's lengthwise place (580 forward of
the front axle) and so every hole along the car; the floor kick (-1950) and the rear floor (520);
the sill section (690 / 800 / 330); the tunnel (380 / 240 / 250); the rails' sections; the strut
tower (centre 510 across, radius 90, top 785); the radiator support (720 forward) and the rear end
panel (-3260); the windshield pillar's top (the blueprint's two views disagree); the rear wheelhouse
(560 / 375); every sheet thickness (1.0, rails 1.6). On the corner: the centre bore (60), the nut
height (22), the disc's outside diameter (228), the hub's flange, barrel and length - and which
wheel is on the car (5-J steel or 5.5-JJ alloy, PT525's note).

**Missing** (the scene's `missing`): the other three corners from factory figures (the found
model's stand in); the closures as parts of their own (hood, fenders, doors, the hatch panel and
glass - which have no 00-CAR row - bumpers: one skin today); the knuckle and strut
the hub turns on; the hatch aperture as one ring (drawn as its pieces); the rear upper link brackets
as their own part (drawn with PT780). Readings to confirm against the catalogue figures (S-005):
PT777 "rear fender panel" read as the inner wheelhouse, PT761 "engine bay side panel" read as the
panel between the apron and the core support, PT772 "rain rail" read as the hatch opening's gutter.

# 01-engine/cad - the swap's CAD files, unprocessed

Saved 2026-10-16 (D-625) for the swap's CAD model: the LS, the CD009, the accessories and the
FB they go into. Nothing here has been converted, measured or placed. Each folder is a copy of
a found model from `03-cad/model/library` (its source, licence and measured extents are in that
library's `manifest.jsonl` and in `00-CAR` table `cad`), except `clutch/`, downloaded from the maker.
The files are git-ignored like the library; this README is the only tracked file.

| Folder | What | Use in the model |
|---|---|---|
| `engine/ls3-engine-assembly-3dwarehouse-tom` | LS3 long-block envelope with bellhousing, 1:1 (557 x 635 x 832 mm), glb | the engine's first envelope - the best free one |
| `engine/ls3-block-thingiverse-a05c`, `ls3-block-and-rotating-assembly-…`, `ls3-cylinder-head-rh-…`, `ls3-crank-and-mains-assembly-…` | LS3 block, rotating assembly, right head, crank and mains, 1:1, stl | the block and heads to place the mounts, the pan rails and the header flanges on |
| `engine/ls-engine-block-3dwarehouse-shannon-s` | LS block, 1:1, glb | a second block to cross-check |
| `engine/gm-5-7-liter-v8-small-block-ls1-engine-3dwarehouse-matheus-monteiro` | LS1 with accessories, about 1:1, glb | an F-body-style front drive envelope |
| `engine/ls-engine-3dwarehouse-yantski` | LS with a transmission, about 1:1, glb | an engine-plus-gearbox length check |
| `engine/ls7-4l60e-rally-fighter-cad-github-localmotors` | Local Motors Rally Fighter LS7 and 4L60E, engineering CAD, sldprt / sldasm | the most exact LS geometry found (bellhousing face, crank centre, mount bosses) |
| `exhaust/gm-lsx-header-flange-for-snap-together-header-thingiverse-lsxwisher` | LS header flange, 1:1, stl + stp | the header ports, for the custom headers (DS03) |
| `exhaust/1-7-8-inch-ls3-through-ls7-header-mock-kit-printables-michael-rinkle` | 1-7/8 in header mock-up kit, 1:1, 3mf | mocking the header runs past the steering and the starter |
| `cooling/fb-rx7-efan-shroud-printables-adnanklink` | An electric-fan shroud made for the FB, 1:1 (579 x 443 mm), 3mf | the FB's radiator opening and a fan's place (DS04) |
| `cooling/automotive-radiator-3dwarehouse-jay` | A generic radiator, about 1:1, glb | a stand-in until CO01's radiator is chosen |
| `transmission/ls-cd009-adapter-docs-sikky-ict` | Sikky and ICT Billet LS-to-CD009 adapter install guides and catalogue (pdf) | the adapter stack and the starter's place |
| `transmission/nissan-350z-fsm-mt-cl-nicoclub` | 350Z workshop manual, clutch section (pdf) | the slave, fork and clutch geometry |
| `oil-pan/holley-ls-oil-pan-docs-holley` | Holley LS swap oil-pan instruction sheets with dimensions (pdf) | the pan's depth against the FB's centre link (DS02) |
| `docs/chevrolet-performance-ls-install-guides`, `docs/ls-dimension-webpages` | Chevrolet Performance LS install guides; saved LS dimension pages | envelope figures, the balancer and bellhousing positions |
| `ecu/ecumaster-emu-pro-cad-ecumaster` | ECUMaster EMU PRO 8 and 16, STEP / IGES / pdf | the ECU's place at the dash (D-325) |
| `clutch/wilwood-compact-master-drawings/fl554.pdf` | Wilwood compact remote master cylinder kit, dimensioned drawing | the clutch master on the FB firewall (CL03) |

**Looked for and not found free (2026-10-16):** the CD009 itself, a Ford 8.8 axle, the Sanden
SD7 compressor, a SPAL 16 in fan, an AD244 / CS130D alternator, the Sikky plate and the ICT Billet
drive. They are on GrabCAD or 3D CAD Browser behind an account, available from the maker on
request, or not published at all. Until one is found, each is modelled from its published
dimensions and then from the part in hand (R11).

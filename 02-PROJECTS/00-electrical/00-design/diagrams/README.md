# diagrams — two drawings of every harness leg

*Rev 2026-09-23 · owns: which drawings exist, how they are made, and the options held in
reserve. Ruled by Camden on 2026-09-23 (D-385).*

**Every sheet here is generated. Never edit one by hand.** Rebuild them all with:

```
python tools/rx7.py diagrams
```

They follow the same four rules as `DECISIONS.md` (CLAUDE.md §1):

- a **pure projection** of `data/`, adding no fact of its own
- **read-only**, with nowhere to type
- **rebuilt whole** by one command, run at the end of any run that changed `housings`,
  `cavities`, `devices` or `routes`
- **never checked before a commit**: `check` does not look at them, and a stale sheet is
  fixed by running the command

If a drawing and a row ever disagree, the row is right.

## What is in each leg folder

| Folder | `A-pin-ladder.svg` | `B-route-map.svg` |
|---|---|---|
| `L1-engine/` | L1-P, L1-S1, L1-S2 | Dash post → firewall grommet → engine-bay junction → RT02–RT05 |
| `L2-front/` | L2-P, L2-M, L2-S, L2-OAT | Dash post → nose splice → RT07–RT09 |
| `L3-dash/` | L3-P, L3-M, L3-BLW, L3-S1–S3, L3-CMF, L3-MOD, L3-RDR | Dash post → RT10–RT14 |
| `L4-rear/` | L4-P, L4-M, L4-S, L4-S2, L4-RDR, D1, D2 | Dash post → rear node / sill node / tunnel → RT15–RT21 |

**A · Pin ladder** is for the bench: pinning, crimping and metering. There is one block per
housing and one row per cavity, in pin order, including sealing plugs and reserved
cavities. Each wire runs as a straight line from its cavity to where it lands
(`cavities.lands_on`). The label on each wire gives its id, gauge, colour and route. A small
box on a wire is an inline resistor. A dashed wire is run and capped at the far end. Wires
cannot cross on this sheet by construction.

**B · Route map** is for laying out and taping the bundle, and it is the long-term record of
where each wire physically runs. It is drawn like a transit map. Every wire is its own line,
stacked in the order its branch leaves the bundle, so each wire peels off the outside and
nothing crosses. Bends are 45° only. A route's length appears once M-2 fills `routes.ft`.
Wires whose route the record does not state yet are gathered under **"No route in the record
yet"**, so the gap is visible and never guessed. Setting `devices.route` (or
`cavities.route`, for a wire with no device at its far end) moves them onto their branch.

## The overlap rule

Every label is measured with the real font (Noto Sans, Fedora's default) before it is
placed. A sheet is **refused and not written** if:

- two labels touch, or
- a label sits on a wire.

The command then prints the reason and exits with code 2. On sheet A wires never cross, and
on sheet B they never cross by construction. Nothing is written that has not passed.

Print from Firefox (Save as PDF) for the bench copy; that embeds the font.

## Where the facts come from

| Drawn | From |
|---|---|
| housings in a leg | `housings.leg`; sheet B starts only from housings `where` = Dash post |
| cavity rows, colour, gauge, state, far end | `cavities` |
| which device a cavity feeds | `devices.terminals` — `<terminal> → <housing> <cav>` |
| which branch a wire takes | `devices.route`; `cavities.route` only where no device is at the far end |
| the branches | `routes` — a route hangs under the one whose `to_node` its `from_node` begins |

The code is `tools/diagrams.py`. It needs Pillow (`python3-pillow`) for font metrics.

## The options held in reserve — `options/`

Four approaches were sampled on the same real slice (L1-S1 and routes RT01–RT05) before
A + B was chosen. They are kept here in case you switch:

| File | Option | Verdict when sampled |
|---|---|---|
| `options/A-pin-ladder.svg` | **A · Pin ladder** — fixed grid, no layout engine | **in use** |
| `options/B-route-map.svg` | **B · Route map** — transit-map style | **in use** |
| `options/C-elk-layout.svg` | **C · ELK** — the Eclipse Layout Kernel places boxes and routes right-angle wires with pins held in order; we draw its output and apply the same overlap rule | Good for sheets that aren't a straight run: the dash node, the ground tree, relay logic. Crossings are minimised, not banned. Needs Node + `elkjs` (~40 MB). |
| `options/D-d2.svg` | **D · D2** — an off-the-shelf diagram language with ELK layout | Cheapest to write, but it failed the rule: labels print on the wires and a title is clipped, and its output can't be checked. |

`options/source/` holds the exact code that drew each sample (`common.py` holds the shared
data and the first version of the overlap check). To run C again, install Node, run
`npm i elkjs` in a folder named `elk/` beside the script, and put `node/bin` on the PATH. To
run D, get the `d2` binary from github.com/d2lang/d2 and run
`d2 --layout elk opt_d2.d2 out.svg`.

Considered and not sampled:

- **KiCad schematic.** It has no automatic schematic layout, so it would still be A or C
  underneath.
- **RapidHarness, Zuken E3, Siemens Capital.** They cost money, you draw in them by hand, and
  they would hold a second copy of every wire (R2).
- **QElectroTech, draw.io, Inkscape.** Hand-drawn; that was the retired SVG set.
- **Mermaid.** It has no model of pins.

The WireViz sheets these replace, and the reason they failed (Graphviz's right-angle router
ignores pin positions, D-276), are in
`99-ARCHIVE/2026-09-11_v2-view-and-tools/02-PROJECTS/electrical-build/01-DESIGN/01-DESIGN/diagrams/`.

## Not yet drawn

The dash node itself (the PMU, fuse blocks, relays, and the drops to the ICU and DCU) and the
ground tree are not legs, so neither has a sheet. If one is wanted, option C is the
candidate.

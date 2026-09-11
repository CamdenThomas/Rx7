<!-- out: README.md -->
# Reference

*Rev 2026-09-03 · owns: the index of every source document — {{count:sources}} rows in `data/sources.csv`, {{count:sources|obtained=yes}} of them held in this tree. Binary files welcome; **index everything you drop in, in the same session** — an unindexed reference file is one nobody will find twice. Every number taken from a document cites its `S-###` in [`../00-CAR/SPECS.md`](../00-CAR/SPECS.md).*

Held documents live in [`factory-circuits/`](factory-circuits/README.md) (the 1982 harness decoded circuit by circuit), [`PMU_info/`](PMU_info/) (ECUMaster), [`manuals/`](manuals/) (the workshop manuals, parts fiche, training and bulletin scans obtained 2026-09-03) and the root of this folder. Mazda documents are Mazda's copyright and are held for private use.

## The sources

{{table:sources|-format}}

## Still wanted

| Need | For | Priority |
|---|---|---|
| A 1981–83 workshop manual, or its electrical and technical-data sections | The 1982-specific alternator rating (`V-002`), torque table and capacities — the 1980 and 1985 manuals bracket the car today | Medium |
| Ionic S9 manual / heater spec | `V-052` heater trigger and winter draw | Medium |
| TE Deutsch DT contact datasheet | Size-16 contact rating behind D-223 | Low |
| Aeromotive Phantom 340 spec | `V-040` — future part, engine-swap project | Low |

## Size note

The wiring diagram, the PMU manual, the STEP model, the TE catalogue and the 26 manual sections are together about 240 MB. They are tracked in git today; if the repository moves to a remote, move them to Git LFS (`.gitattributes` already marks them binary).

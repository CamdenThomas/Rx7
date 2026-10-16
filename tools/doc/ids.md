# How block ids were numbered, and renumbered

Blocks were `BLK-###` until 2026-09-21 (D-356 gave them `<project>.<number>`); each old id
is a `retired` row in its project naming the new one.

**The projects moved up one number on 2026-09-25** (D-427) to make room for `00-verify`:
electrical 00 → 01, luxury 01 → 02, engine 02 → 03, beauty 03 → 04; 10-gui kept 10. The same
day Camden swapped engine and luxury and took the app out of the projects (D-428): the tree
is now `00-verify`, `01-electrical`, `02-engine`, `03-luxury`, `04-beauty`, and `02-APP`
(was `02-PROJECTS/10-gui`, block prefix `APP`; engine's open `03.02` became `02.12` and
luxury's `02.11` became `03.12`). Open blocks were renumbered and their old ids retired.
Decisions and logs are never edited, so a block id in one written before that date keeps its
old project: `00.NN` there is electrical, `01.NN` luxury, `02.NN` engine, `03.NN` beauty.
Numbering is derived from every `closes` and retired id, so no new id repeats an old one.

On 2026-09-26 (plan P21) `00-verify` took the fixed prefix `VER`, so its blocks never share
`00` with electrical's history, and a block id issued from 2026-09-25 on is closed only by a
decision of the area whose prefix it carries; decisions dated before that close whatever id
they name.

On 2026-10-14 `04-beauty` merged into luxury (D-570), and the same day the projects took the
order Camden gave them (D-572): `05-cad` became `02-cad`, `02-engine` `03-engine`, `03-luxury`
`04-luxury`. No block was open in any of them, so no id changed: each closed block keeps its id,
and the project that closed it names the old prefix in its `_project` under `inherits_blocks`
(`02-cad` 05, `03-engine` 02, `04-luxury` 03 - and 04, its own now, for beauty's). A new block
takes the project's present number and is numbered past every id ever used, so `03.NN` from now
on is engine's and never repeats a luxury id.

On 2026-10-16 the projects took the order Camden gave for the engine swap (D-618): `05-library`
became `00-library`, `03-engine` `01-engine`, `01-electrical` `02-electrical`, `02-cad` `03-cad`;
`04-luxury` kept its number. The one open block, electrical's `01.61`, was closed the same day
(D-617), so no open id changed. Each project names the prefixes it carried before under
`inherits_blocks` (`00-library` 05, `01-engine` 03 and 02, `02-electrical` 01, `03-cad` 02 and 05,
`04-luxury` 03 and 04). A prefix an area owns today wins, so `01.NN` from now on is engine's,
`02.NN` electrical's and `03.NN` cad's; every new id is numbered past every id ever used, so
none repeats an old one (next: `01.62`, and so on). A block id in a decision or log written
before 2026-10-16 keeps the project it had then.

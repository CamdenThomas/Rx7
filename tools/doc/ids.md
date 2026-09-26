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

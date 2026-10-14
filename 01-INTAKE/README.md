# 01-INTAKE — bulk waiting to be read into the car

*Rev 2026-10-14 (D-519, D-569) · owns: nothing permanent. It was `01-REFERENCE`; it is
not an area, and no row names it as a home.*

Manuals, catalogues, datasheets and found models land here to be parsed into `00-CAR`'s tables,
then leave the tree. Everything here is git-ignored except this file and `manuals/fetch.sh` with
its list `DOWNLOADS.csv`, which fetch a source's file from its host. Every file that was here has
been parsed (06-intake, archived 2026-10-14); its source row's `local_path` says where on disk it
is kept, in `model/library/docs/`. A new file is parsed by a run in the project that wants it,
then moves there too.

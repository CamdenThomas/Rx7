<!-- out: MAINTENANCE.md -->
# MAINTENANCE — the schedule and the service log

*Rev 2026-09-08 · owns: what gets done to the car at what interval, when it was last done, and when it is next due; the log of every visit; the torque quick reference. Rendered from `data/intervals.csv`, `data/service.csv` and `data/specs.csv`. A visit is logged with `/rx7-log` (one `service` row; the schedule recomputes).*

## Schedule

Intervals with no figure are not yet set from a document — the 1985 workshop manual's §0 schedule (S-002) is the source to read them from; until then the interval is the owner's call and the log is the record.

{{maintenance}}

## Service log

Newest first. Mileage is the reading at the visit; blank means it was not recorded.

{{service_log}}

**Current mileage: {{cell:vehicle|mileage|value}}.**

### Maintenance philosophy

The July 2026 brake work was **deliberately early** — parts replaced before they were worn out, not after they failed. Assume brake and bearing components are near-new, not near end-of-life, and plan intervals from mileage since replacement rather than from "is it still working".

**A rotary lives or dies on oil.** Whatever the interval, log every change.

## Torque and spec quick reference

{{table:specs|category=Torque|-category,source,page}}

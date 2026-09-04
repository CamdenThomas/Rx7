<!-- out: README.md -->
# 00-CAR — the permanent record

*Rev 2026-09-03 · owns: the index of the car-level files. Everything here survives every project; projects cite these files and never own their facts.*

| File | Holds | Add to it when |
|---|---|---|
| [`vehicle.md`](vehicle.md) | Identity, drivetrain and electrical as fitted **today**, planned drivetrain, chassis notes | The configuration changes |
| [`SPECS.md`](SPECS.md) | Every factory number with its source — `data/specs.csv` | A number is found in a document |
| [`modifications.md`](modifications.md) | `M-###` changes made, `P-###` planned, service history, fluids, torque specs | Anything is fitted, serviced or planned |
| [`known-issues.md`](known-issues.md) | `K-###` faults, quirks and PO hacks, with their impact on the rebuild | Something is found wrong |
| [`parts-history.md`](parts-history.md) | Every part bought — source, price, link, date | A part is bought |

**Rules.** `M`, `P` and `K` IDs are permanent and never reused. A fault that
is fixed stays in [`known-issues.md`](known-issues.md) with its status updated; a planned item
that is done moves from `P` to a new `M` row. The factory car as it left the
line is [`../01-REFERENCE/`](../01-REFERENCE/README.md); the rebuild is
[`../02-PROJECTS/electrical-build/`](../02-PROJECTS/electrical-build/README.md).

**One fact a stranger looks for first and cannot find:** the VIN (`Q-001`,
`T-049`).

**How this folder is maintained.** The tables are rows in `data/` (`mods`, `planned`,
`service`, `fluids`, `issues`, `parts_history`, `specs`); the prose is in `templates/`;
`python tools/rx7.py -p 00-CAR build` renders these files. Every finished project
folds its fitted parts and learned numbers in here (ASSISTANT.md §8).

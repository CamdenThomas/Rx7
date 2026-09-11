<!-- out: README.md -->
# LUXURY PACKAGE — 1982 Mazda RX-7 (FB)

*Rev 2026-09-07 · owns: the map of this project. Facts are `data/`'s, prose is `templates/`', derivations are `views.py`'s; rendered by `tools/rx7.py -p luxury-package build` (D-309).*

Everything the car gets **after** it drives on the new harness: the bezel and dash plastics around the digital display (the display itself went in with the ICU — electrical D-268), the climate and comfort module (DCU) with its control panel, the blower, heated and cooled seats, mirrors, power windows, the lighting second pass, radar. **This project does no harness work.** Every conductor it needs was run by the [electrical build](../electrical-build/README.md) and ends in a dust-capped receptacle where it leaves its leg (electrical D-274); the boundary table in [`01-DESIGN/DESIGN.md`](01-DESIGN/DESIGN.md) §2 is read *live* from that project's data, so it cannot drift.

| Step | Folder | What it is |
|---|---|---|
| **1 · Understand** | [`01-DESIGN/`](01-DESIGN/DESIGN.md) | The design — modules, what the harness hands over, every sensor's front end, the CAN map, the cluster, climate and comfort, the failure-mode table. [`CAN-MESSAGES.md`](01-DESIGN/CAN-MESSAGES.md) and [`DCU-CARRIER.md`](01-DESIGN/DCU-CARRIER.md) are its detail pages; the ICU carrier is drawn in the [electrical build](../electrical-build/01-DESIGN/ICU-CARRIER.md). The firmware in [`01-DESIGN/firmware/`](01-DESIGN/firmware/README.md) is a source of truth in its own right (R6). |
| **2 · Buy** | [`02-SHOPPING/`](02-SHOPPING/SHOPPING-LIST.md) | Every part by stage, estimates until a cart exists. |
| **3 · Build** | [`03-INSTALL/`](03-INSTALL/INSTALL.md) | The stages in order — bench, (the ICU and its display — already in the car), climate, the display bezel, comfort, mirrors, windows, lighting, radar — and [`BRING-UP.md`](03-INSTALL/BRING-UP.md), the firmware record with the header-drift report. |

{{counts}}

**Next IDs:** decisions from {{next_id:D}} · questions from {{next_id:Q}} · phase **{{phase}}**.

Two files at this level are the project's memory: [`DECISIONS.md`](DECISIONS.md) (why, by system) and [`QUESTIONS.md`](QUESTIONS.md) (§0 is the finishing checklist — what the agent has already done alone and what only the owner can settle).

## The rules this project inherits

**Modules join a finished car (D-081)** — nothing here is a dependency for the car starting, running or being legal. **Wire is control, CAN is telemetry (electrical D-251)** — no PMU control rule ever depends on a frame from these modules; a CAN value admitted to one fails open. **A gauge's sender wires into the box that draws the gauge (D-083)** — the ICU's critical gauges survive a dead bus. **The display never crosses the harness (D-159).**

## Where it stands

The ICU firmware renders the full cluster on the desk against a PMU simulator; the DCU has a tested logic skeleton; the DCU carrier is not laid out (the ICU carrier is the electrical build's now, D-313). The car itself is still on its factory harness — the electrical build's carts are unpaid. What this project can do *now*, with no car, is in [`QUESTIONS.md`](QUESTIONS.md) §0 and the `S0` stage of the install plan.

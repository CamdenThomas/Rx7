# QUESTIONS — luxury package

*Rev 2026-09-08 · owns: what is still open in this project, and the finishing checklist. Rulings are [`DECISIONS.md`](DECISIONS.md)'s; facts are `data/`'s. IDs inherited from the electrical project keep their numbers; new ones run from Q-300.*

**None of this blocks the electrical build's carts.** The harness side of every feature here is run and capped; the boundary table in [`01-DESIGN/DESIGN.md`](01-DESIGN/DESIGN.md) §2 is read live from that project's data. The file is split by this project's own shopping event — the carrier boards and the glass.

| | §1 · BEFORE the boards and the glass | §2 · AFTER |
|---|---|---|
| **What it is** | Calls the owner makes, facts to confirm, measurements to take before a PCB is laid out or a panel is bought | Bring-up, validation and tuning |
| **Cost of a wrong answer** | A re-spun board, or glass that cannot be driven | A firmware revision |

The ICU's own questions — its layout, its senders, the wideband's frame — are the electrical build's now (D-313); they sit in its `QUESTIONS.md` §1 under their old numbers.

Three items ride along with the electrical build's measurement day — marked **[M-DAY]**. Miss that day and they wait for the next teardown.

---

## 0 · The finishing checklist

**A · Done by the agent alone, 2026-09-07** — nothing here needed an answer, only the current electrical data and the archived reasoning.

- [x] **A1 · The record is data** (D-309). `data/` holds modules, stages, features, provisions, sensors, CAN messages and fields, parts, work, params and the bring-up log; `templates/` the prose; `views.py` the derivations and seven checks; `build` renders README, DESIGN, CAN-MESSAGES, both carriers, SHOPPING-LIST, INSTALL, BRING-UP, `VIEW.html` — and `firmware/pmu_sim/channels.h` (D-311).
- [x] **A2 · The boundary cannot go stale.** Every provision this project counts on is joined live to `../electrical-build/data`; a cavity that changes state or vanishes there refuses this project's build.
- [x] **A3 · Every stale claim found and corrected** — fuel level "read by the PMU on A7 / 0x120" (now the ICU's, 0x218) · the single 12-way `DP-ICU` and its old pinout (now `DP-ICU-A` / `-B`) · sender inputs drawn as pull-up dividers that would have moved the factory needles (now high-Z observers, D-310) · the tach on the leading coil (trailing, D-304) · `DP-DCU 2` as an O15 tap (it is the outside-air sensor) · F10 / F11 branches (deleted; this project's block) · the CAN keypad (custom panel, D-210) · "five nodes" (six, with the wideband) · the private DCU ↔ ICU pair (not run) · "both modules on O10" (heavy loads on O15) · coolant / oil level "capped in L1-S2" (plugs) · "DCU firmware not started" (F-001 done) · the fuel-pump rpm rule (primary gate is A7, rpm secondary and fail-open) · 384 KB / 64 ms framebuffer figures (614 KB / ~100 ms) · every link into the dissolved `electrical-pmu` tree.
- [x] **A4 · ICU front end specified** for all nine inputs and the DCU's — values, pin class, calibration method, CAN field — in `data/sensors.csv` (D-310); the carrier documents are rendered from it.
- [x] **A5 · CAN map as data** — `0x218`, the `0x300` changes, the AEM vendor frame with its two exceptions, bus load and timeouts computed; the header-drift report in `BRING-UP.md` §1 shows exactly what `can_map.h` lacks.
- [x] **A6 · Failure-mode table** written (X-006) — DESIGN §9.
- [x] **A7 · Money by stage** — 44 lines from the archived Waves 3–5 plus everything ruled since (blower, final stage, senders, VSS, nozzles, mirrors, O15 block), each with its gating question.
- [x] **A8 · Install plan** — stages S0–S8 with what plugs into what, per-stage provisions printed from the electrical data (D-312).
- [x] **A9 · Backlog reconciled** — F-005 / F-006 / F-001 / F-011 marked done; X-003 / X-004 / H-004 / H-005 / Z-001 moved to their owners; H-003 and Z-003 closed; F-012 / F-013 opened with the exact header changes.
- [x] **A12 · The display handed to the electrical build too** (D-314, 2026-09-07i) — it goes in with the ICU on a plain plate; `T-051` / `V-084` / `V-085` and the glass parts moved with their numbers; `S3` is now the bezel (FT34, H-006, LP29); F-007 is a cutover gate for that project.
- [x] **A11 · The ICU handed to the electrical build** (D-313, 2026-09-07c) — its features, sensor rows, parts, work items, carrier template and six questions moved with their numbers; `S1` stays as the prerequisite that project delivers; `Q-301` closed as moot and `Q-302` on the F16 backlight feed.
- [x] **A10 · The tool learned the new names** — `DP-ICU-A`, `DP-ICU-B`, `L3-BLW`, `L4-S2` now cross-link in `VIEW.html` and pass the electrical cavity check.

**B · Still agent-side, gated on something other than the owner**

- [ ] **B1 · F-012 / F-013** — bump `can_map.h` and re-run the suites. Needs a machine with g++ (w64devkit); this one has neither g++ nor arduino-cli, so the change is specified, not made.
- [ ] **B2 · F-007 / F-010** — SD persistence and config-as-data. Needs a microSD card (LP04) in a board.
- [ ] **B3 · H-002 carrier layout** — everything is specified; the layout waits on `V-083` and `Q-305` below (H-001 is the electrical build's).
- [ ] **B4 · Z-002 radar design** — after `V-061`.

**C · The owner's calls** — §1 below, easiest first. Answer one by writing under it or saying it in a session.

---

# 1 · BEFORE the boards and the glass

**Q-306 · Stage order — climate before the display's bezel?** *(new, 2026-09-07)*
The plan puts `S2` (panel, DCU, blower — the centre-stack plastics) ahead of `S3` (the display's bezel — the binnacle plastics), because the car has no heater airflow until the blower returns (electrical D-253) and the display is already in the car on its plate (electrical D-268). **Recommend yes.** Flip it if the bare plate bothers you more than a winter without heat. Costs nothing either way — the two plastics events are independent.

**ANSWER:**
>
>

**Q-305 · Who moves the mirrors — a switch in the panel, or the DCU?** *(new, 2026-09-07, from electrical D-255)*
`L4-S2` carries the five command conductors to the sill either way. **(a)** A mechanical mirror switch (joystick + L/R selector) on the panel wired straight to `L4-S2` at the post: zero electronics, works with the DCU off, the DCU still does mirror heat. **(b)** The DCU drives them through six half-bridges and the panel sends the joystick over CAN: a knob-free panel, but bridges on H-002, firmware, and a mirror that cannot move if the DCU is down. **Recommend (a).** Flip it if the panel design has no room for a mechanical mirror control. Decides `SN17` before H-002 is laid out.

**ANSWER:**
>
>

**Q-307 · Tank capacity for the range calculation — 15.9 or 16.6 gal?** *(new, 2026-09-07)*
`stats.h` carries 15.9 gal (D-300 confirmed it "as assumed"). The 1982 brochure (S-004, primary) says **16.6 gal**; S-015 says 16.4; S-016 says the 1981-on tank is 16.5. **Recommend 16.6** from the primary document — one constant in `stats.h`. Flip it if the tank was ever replaced or you have measured a fill.

**ANSWER:**
>
>

**V-083 · DCU carrier parts** — second LMR33630 for the servo rail, AOD4184-class FETs ×7, INA180 + 5 mΩ, and — if `Q-305` says (b) — six half-bridges. Datasheet-verify before layout.

**ANSWER:**
>
>

**Q-303 · A heated washer nozzle (and park de-icer) that fits the FB cowl.** *(2026-09-07, from electrical D-256)*
The feed is run — `L2-S 6`, ending in the `L2-NZL` receptacle at the cowl (electrical D-274), a comfort-bus load the DCU switches. A nozzle with an integral PTC heater in the factory hole pattern and hose size, or a universal heated nozzle on an adapter plate, plus whether a wiper-park de-icer strip is wanted on the same feed; nozzles ground at the front star, not through the hood hinge. Your condition stands: it goes in only if one can be made to work; if none can, the receptacle stays capped and nothing is lost.

**ANSWER:**
>
>

**Q-300 · Which mirror?** D-305 settled the feature set — adjustment and heat only. The doors impose the part: a **conventional 3-wire motor pair** (common + X + Y) with a **resistive** heater on its own feed. A 5-wire, LIN-bus or module-driven mirror needs conductors the doors do not have and never will. Filter every candidate on its wiring diagram, not its photograph.

**ANSWER:**
>
>

**Q-048 / T-036 · Which DOT-compliant headlamp unit goes in the retained pop-up buckets?** (a) 4×6 rectangular LED on an adapter plate · (b) 5×7 · (c) 7-inch round LED with a rectangular-looking element, no plate. **Recommend (c)** unless `V-066` finds the bucket already rectangular. Nothing electrical changes either way.

**ANSWER:**
>
>

**V-064 / T-037 · A DOT/SAE LED module source, red and white, with published candela** for the tail-light strips. A module without published candela cannot be shown to meet FMVSS 108 and is not a candidate.

**ANSWER:**
>
>

**T-032 / T-033 · The release triggers, and the hatch latch switch (broken, K-016).** Both solenoids exist and are wired to — `L4-M 3 / 4` run all the way to them, their post ends capped (electrical D-274). What is left: the trigger per D-180 (the K3 / K4 sockets at the dash node are the slot) and the latch switch (LP24). Nothing to source for the solenoids themselves.

**ANSWER:**
>
>

**V-063 / T-034 · Tail-light aperture [M-DAY]** — width, height, depth, mounting. D-107's 55 cm² of red against FMVSS 108's 50 has no margin for a wrong assumption.

**ANSWER:**
>
>

**V-066 / T-035 · What headlamps are actually fitted today [M-DAY]** — round or rectangular, and whether LED housings are already in. Decides `Q-048`.

**ANSWER:**
>
>

---

# 2 · AFTER — bring-up, validation and tuning

**V-065 · The PMU's real CAN export format.** ECUMaster fixes it. `0x100`–`0x130` are intent until the client's export is read at the electrical install §5.5; every PMU-sourced field in the ICU is written against a guess until then. Read out at the same time whether each PMU **CAN input** carries its own timeout and default — electrical D-251 needs fail-open for anything near a control rule, and a logged fault for `0x218`.

**ANSWER:**
>
>

**T-048 · Flash and label boards 2 and 3** once a soldering iron is out. Opportunistic.

**ANSWER:**
>
>

**V-061 · Radar sensor interface.** Design the subsystem (Z-002) before the `L3-S3 ↔ L4-S` pass-through is uncapped. Custom build, no datasheet to shortcut it.

**ANSWER:**
>
>

**Q-028 · CAN wake latency.** If the horn or the winks ever move to a CAN-node wake, what wake-to-horn latency is acceptable cold? Recorded so it is not rediscovered; on the current design nothing depends on it.

**ANSWER:**
>
>

---

# 3 · Closed

**2026-09-07c — the ICU handed over:** D-313 (electrical D-258 / D-259 / D-260). `Q-301` → closed as moot — the ICU excites the senders, there is no observer and no hand-over · `Q-302` → D-313 — the display's backlight is the F16 aux on `DP-ICU-A 6`, through the ICU board; O10 never carries it. `V-073` `V-082` `V-057` `Q-304` `Q-308` `Q-309` → electrical `QUESTIONS.md` §1 (see §4).

**2026-09-07 — the data migration and the ICU / DCU session:** D-306 (the ICU joins early, headless; fuel level is its signal) · D-307 / D-308 (blower via the final stage; outside-air temp; nozzle feed) · D-309 (the record is data) · D-310 (observer front end; one BRAKE tell-tale) · D-311 (`channels.h` rendered from the electrical pins) · D-312 (stages S0–S8). Opened Q-303 – Q-309. `V-060` → D-305, `V-067` → D-304, `V-059` → D-303, `V-070`–`V-072` → D-300 as before.

**2026-09-03 — Camden's answers:** `V-070` `V-071` `V-072` → D-300 · `V-059` → D-303 · `V-067` → D-304 (2 ppr, **trailing** coil) · `V-060` / `T-031` → D-305 (adjustment and heat only) — opened `Q-300`.

---

# 4 · Moved out of this project

| ID | Went to | Because |
|---|---|---|
| V-084 V-085 T-051 | `../electrical-build/QUESTIONS.md` §1 | The display went in with the ICU (D-314, electrical D-268); the glass and the bridge are that project's bench items |
| V-073 V-082 V-057 Q-304 Q-308 Q-309 | `../electrical-build/QUESTIONS.md` §1 | The ICU is the electrical build's device (D-313, electrical D-259) — its carrier layout, its senders and the frame it decodes are that project's questions. Numbers kept |

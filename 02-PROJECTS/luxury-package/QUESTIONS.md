# QUESTIONS — luxury package

Everything open in this project. These arrived from the electrical project on 2026-09-02 (D-213) with their original IDs; new ones start at Q-300.

**None of this blocks the electrical build's carts.** The harness side of every feature here is already run and capped — see the boundary table in `DECISIONS.md`. This file uses the same two-category split as `../electrical-build/QUESTIONS.md`, but the shopping event it splits on is **this** project's own: the board, glass and hardware orders that happen once the car is driving on the PMU.

| | §1 · BEFORE SHOPPING | §2 · AFTER SHOPPING |
|---|---|---|
| **What it is** | Design questions — what gets ordered, and what a board is laid out against | Bring-up, validation and fine tuning |
| **Cost of a wrong answer** | A re-spun PCB, or glass that cannot be driven | A firmware revision |
| **Answer them** | Before the carrier PCBs and the display chain are committed | At bench bring-up, or with the PMU configured in the car |

> **Three of these ride along with the electrical build's measurement day** — the one afternoon the car is apart. They are ten-minute looks and they are marked **[M-DAY]**. Miss that day and they wait for the next teardown, which is the thing this whole project exists to avoid. See `../electrical-build/QUESTIONS.md` §0 box C3.

---

# 1 · BEFORE SHOPPING — design questions

## 1a · The display chain — the largest single spend in the project

**V-085 / V-084 / T-051 · Which glass, and the bridge to it.**
Chain (i): RGB → LVDS serializer into 1280 × 480 cluster glass (LQ123K1LG03, 330 cd/m²) — works **only** if the binnacle brow shades it, as the factory cluster it came from was shaded. Chain (ii): RGB → HDMI encoder into the scaler board of a 900–1000-nit 1920 × 720 bar panel — the default if the brow does not convince. `V-084` then verifies the BT817's pixel clock and sync polarity against whichever glass is chosen. `T-051` orders the BT817 eval board **first** — it proves the whole chain on the bench before any glass money moves, and it is the one order that should not wait for anything.
**[M-DAY]** — how deep the brow shades the cluster is judged at M-1, and it is the input that decides between the two chains.

**ANSWER:**
>
>

## 1b · Before a board is laid out

**V-073 · IMU mounting orientation on the ICU carrier** must match the axis convention in D-161 — lateral positive right, longitudinal positive under acceleration, pitch positive nose-up — or every axis needs a sign flip in firmware. Decide before layout, not after.

**ANSWER:**
>
>

**V-082 · ICU carrier candidate parts** — LMR33630-class buck, SMBJ33A TVS, BAT54S clamps, H11L1 / LM393 tach front end (`01-DESIGN/ICU-CARRIER.md`). Datasheet-verify before layout. **Note D-304:** the tach front end must now be specified against the **trailing** coil's negative primary — the inductive-kick side — not the clean input the document currently implies. That changes the clamp, not the topology.

**ANSWER:**
>
>

**Q-301 · How does the ICU read a sender the factory gauge is driving — and what happens if the cluster ever leaves?** *(new, 2026-09-04, from the electrical build's sensor review)*

Every analog sensor on `DP-ICU` is a **tap on a node the factory cluster drives**. The sender is a variable resistor to ground, the gauge supplies the excitation, and the signal is the node voltage. The harness gives the ICU a wire onto that node and nothing else, which sets two requirements for the carrier board.

**(a) The ICU is an observer, not a reader.** Its input has to be high-impedance enough that it does not load the divider and shift the gauge the driver is still looking at. The precedent is already in the electrical build: A7 watches the fuel node through a **1 MΩ pull-down** (D-215) and is calibrated as a **three-point lookup taken in the car** (D-197), never computed from a resistance table, because the node voltage depends on the cluster's own internal supply. Temp and oil get the same treatment — high-Z, clamped, calibrated in situ. **Confirm first** whether these gauges are fed through a *pulsing* constant-voltage regulator, as most Japanese clusters of this era were: if they are, every observer needs averaging in firmware and a single raw sample means nothing. One scope trace at the cluster plug settles it, and it rides along with the electrical build's `M-6`.

**(b) The cluster is the excitation source, so it cannot simply be unplugged.** If the ICU is ever meant to *replace* the factory cluster rather than sit beside it, pulling `DP-CLU` removes the drive and every sender node goes dead. The fix is local — the ICU supplies its own pull-up to its own reference — but it has to be on the board from the first layout, together with a way to disable it while the cluster is still fitted, because two drivers on one node is worse than none.

**Four signal types share the one 12-way drop:** two resistive sender nodes (temp, oil), one pulse train (tach — shielded, trailing coil, `V-082` / D-304), and two lamp-drive lines (charge, brake warning) that are effectively digital, pulled low by the alternator or a switch. Fuel level is **absent by design**: the PMU's A7 owns that node today. If the electrical build's `Q-107` re-points A7 at oil pressure, the fuel tap has to be added to `DP-ICU 8` while the harness is still on the bench — not after.
**Blocks:** the ICU carrier's analog front end, and `V-082`.

**ANSWER:**
>
>

**Q-302 · What feeds the ICU and its display, and does O10 have the headroom?** *(new, 2026-09-04)*

`DP-ICU 1`, `DP-DCU 1` and `DP-KEY 3` are all 16 AWG taps off **O10, the accessory bus** (D-215). O10 already carries the head unit, both USB-C ports and the K12 washer coil, and `LD15` puts that at **~10 A worst case** against a **13.0 A** enable-at cap (D-223). That leaves roughly **3 A for all three modules together** — and a 900–1000 nit bar panel (chain ii, `V-085`) plus its backlight can eat most of it on its own, before the Teensy, the BT817 and the DCU's servo rail are counted.

Note what is *not* in question: the **display never touches the harness** (D-159). It is powered and driven locally by the ICU behind the same bezel. The load being argued about is what the ICU board draws *including* whatever it passes on to the panel.

**Options: (a)** measure the real draw at bench bring-up and, if O10 is short, feed the ICU from the **O15 comfort bus** — 25 A, already run to `L3-P 2` and capped, fanned out by this project's own fuse block (D-011) — keeping `DP-ICU 1` as the logic and wake supply. **(b)** Put the ICU on O15 from the start and leave O10 to the head unit. **(c)** Accept O10 and let the display shed under the 11.5 V rule (D-248).
**Recommend (a).** It costs nothing now, it uses a bus that exists for exactly this, and the number that settles it does not exist until a board draws current. But the *question* has to be answered before layout, because where the board takes 12 V from changes its input protection and its connector.
**Blocks:** the ICU carrier's power input, and the O15 fuse block this project adds.

**ANSWER:**
>
>

**V-083 · DCU carrier candidate parts** — second buck for the servo rail, AOD4184-class FETs, INA180 shunt amp (`01-DESIGN/DCU-CARRIER.md`). Datasheet-verify before layout.

**ANSWER:**
>
>

**V-057 · TCAN1042 / TCAN1051 exact part suffix** for the 3.3 V-logic, 5 V-bus variant with the VIO pin. The last part-availability item ahead of layout, now that the Teensys are in hand (D-303).

**ANSWER:**
>
>

## 1c · Sourcing — what to buy, once the design says what it must be

**Q-300 · Which mirror?** *(new, from D-305)*
D-305 settled the feature set: **adjustment and heat only** — no fold, no repeaters, no puddle lamps, no blind-spot indicators, no memory. That closed `V-060` and confirmed the electrical build's DT-8 door housings are correct. What is left is picking a part, and there is one hard constraint the doors impose: it must be a **conventional 3-wire motor pair** — one common plus X and Y — with a **resistive** heat element on its own feed. A 5-wire mirror, a LIN-bus mirror, or anything with its own control module needs conductors D1/D2 do not have and never will, because the door boot is not opening twice. Filter every candidate on the wiring diagram, not the photograph.
**Blocks:** `T-031`, and nothing else — the harness is done either way.

**ANSWER:**
>
>

**Q-048 / T-036 · Which DOT-compliant headlamp unit goes in the retained pop-up buckets?**
(a) 4×6 rectangular LED sealed beam on a flat adapter plate · (b) 5×7 rectangular, larger · (c) 7-inch round LED with a rectangular-looking element, fits the bucket directly. **Recommend (c)** unless `V-066` finds the bucket is already rectangular, in which case (a) with no plate. Nothing electrical changes whatever is chosen — O2/O3 and L2-P are identical either way.

**ANSWER:**
>
>

**V-064 / T-037 · A DOT/SAE-compliant LED module source, red and white, with published candela** for the tail-light strips. Photometry is the hard part, not area — a module without published candela cannot be shown to meet FMVSS 108 and is not a candidate however good it looks.

**ANSWER:**
>
>

**T-032 / T-033 · Fuel-door solenoid (never existed on this car) and hatch latch switch (broken, K-016).** Both outputs are provisioned and capped on L4-M 3 / L4-M 4, so this is pure sourcing.

**ANSWER:**
>
>

## 1d · Rides along with the measurement day **[M-DAY]**

Ten-minute looks. They cost nothing on the day the interior is already apart and a great deal on any other day.

**V-063 / T-034 · Tail-light aperture** — width, height, depth, mounting. The whole strip design is scaled from a nominal 30 cm, and D-107's 55 cm² of red against FMVSS 108's 50 cm² minimum has no margin to absorb a wrong assumption.

**ANSWER:**
>
>

**V-066 / T-035 · What headlamps are actually fitted today** — 7-inch round or rectangular sealed beams, and whether LED housings are already in. Decides `Q-048` between (a) and (c).

**ANSWER:**
>
>

---

# 2 · AFTER SHOPPING — bring-up, validation and fine tuning

Nothing here can be answered early, because each one needs a thing that does not exist yet: a configured PMU, a running node, or a designed subsystem.

**V-065 · The PMU's own CAN export format.**
ECUMaster fixes it; we do not. Messages `0x100`–`0x130` in `01-DESIGN/CAN-MESSAGES.md` are *intent* and must be reconciled against the real export read out of the client once the PMU is configured in the car (electrical install §5.5). Until then every PMU-sourced field in the ICU is written against a guess. This is the single largest firmware unknown in the project, and it unblocks the moment the PMU is talking.

**ANSWER:**
>
>

**T-048 · Flash and label Teensy boards 2 and 3** once the soldering iron is out for the electrical build's ladder resistors. Three boards are in hand with headers (D-303); this is opportunistic, not scheduled.

**ANSWER:**
>
>

**V-061 · Radar sensor interface.**
Design the subsystem (`01-DESIGN/FORWARD-WORK.md` Z-002) before the L3-S3 ↔ L4-S pass-through is uncapped. Three conductors are run each way and nothing commits until the subsystem exists; D-096 says this is a custom build, not a commercial unit, so there is no datasheet to shortcut it.

**ANSWER:**
>
>

**Q-028 · CAN wake latency.**
If the horn or the winks ever move to a CAN-node wake, what wake-to-horn latency is acceptable on a cold boot? Recorded so it is not rediscovered. Nothing depends on it today, and on the current design nothing ever will — D-210 and the electrical build's D-189 make both hardwired for reasons that do not expire.

**ANSWER:**
>
>

---

# 3 · Closed

**2026-09-03 — Camden's answers parsed in:**

| ID | Closed by | Outcome |
|---|---|---|
| `V-070` `V-071` `V-072` | D-300 | All three confirmed as assumed — 7000 rpm redline, 1.0 bar minimum idle oil pressure, 15.9 gal tank. No firmware change |
| `V-059` | D-303 | Three Teensy 4.1 in hand with headers. Availability is not a risk; the carriers may commit to the part |
| `V-067` | D-304 | 2 pulses per revolution **confirmed** — but off the **negative of the trailing coil**, not the leading coil. Scaling unchanged; the ICU tach front end must be specified against an inductive-kick primary |
| `V-060` / `T-031` | D-305 | Mirrors do **adjustment and heat only**. Door conductor budget settled; electrical build unchanged, DT-8 housings stay. Sourcing → `Q-300` |

**Opened by those answers:** `Q-300` (which mirror, given the 3-wire constraint).

**Carried into `01-DESIGN/` as edits still to make:** `ICU-CARRIER.md` says the tach front end reads the **leading** coil — D-304 corrects that to the trailing coil's negative primary, and the clamp ahead of the opto has to be specified for it. The electrical build's conductor (L1-S1 6 → DP-CLU 4, tapped to DP-ICU 9) was always drawn from the trailing coil and needs no change.

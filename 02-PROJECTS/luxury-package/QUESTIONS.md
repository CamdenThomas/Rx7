# QUESTIONS — luxury package

Everything open in this project, easiest first. These arrived from the electrical project on 2026-09-02 (D-213) with their original IDs; new ones start at Q-300. None of them blocks the wiring build — the harness side of every feature here is already run and capped (`DECISIONS.md`, the boundary table).

## Desk — a search or a datasheet

**V-070 · 12A redline.** The cluster firmware assumes 7000 rpm, which sets the tach red zone and the over-rev counter. Confirm from the FSM.

**ANSWER:**
>

**V-071 · Minimum acceptable oil pressure at idle for a 12A.** Assumed 1.0 bar (rotaries want more than a piston engine at idle). Confirm.

**ANSWER:**
>

**V-072 · FB fuel tank capacity.** Assumed 15.9 gal (nominal ~60 L). Confirm.

**ANSWER:**
>

**V-057 · TCAN1042 / TCAN1051 exact part suffix** for the 3.3 V-logic, 5 V-bus variant with the VIO pin.

**ANSWER:**
>

**V-059 · Teensy 4.1 availability** after the Adafruit → SparkFun distribution change, before the carrier PCB commits to it.

**ANSWER:**
>

**V-082 · ICU carrier candidate parts** — LMR33630-class buck, SMBJ33A TVS, BAT54S clamps, H11L1 / LM393 tach front end. Datasheet-verify before layout (`01-DESIGN/ICU-CARRIER.md`).

**ANSWER:**
>

**V-083 · DCU carrier candidate parts** — second buck for the servo rail, AOD4184-class FETs, INA180 shunt amp. Datasheet-verify before layout (`01-DESIGN/DCU-CARRIER.md`).

**ANSWER:**
>

**V-064 / T-037 · A DOT/SAE-compliant LED module source, red and white, with published candela** for the tail-light strips. Photometry is the hard part, not area.

**ANSWER:**
>

**Q-048 / T-036 · Which DOT-compliant headlamp unit goes in the retained pop-up buckets?** (a) 4×6 rectangular LED sealed beam on a flat adapter plate · (b) 5×7 rectangular, larger · (c) 7-inch round LED with a rectangular-looking element — fits the bucket directly. **Recommend (c)** unless `V-066` finds the bucket is already rectangular, then (a). Nothing electrical changes whatever is chosen.

**ANSWER:**
>

**Q-028 · CAN wake latency.** If the horn or the winks ever move to a CAN-node wake, what wake-to-horn latency is acceptable on a cold boot? Recorded so it is not rediscovered; nothing depends on it today.

**ANSWER:**
>

## Decisions before a board is laid out

**V-073 · IMU mounting orientation on the ICU carrier** must match the axis convention in D-161, or every axis needs a sign flip in firmware. Decide before layout.

**ANSWER:**
>

**V-085 / V-084 / T-051 · Which glass, and the bridge to it.** Chain (i): RGB → LVDS serializer into 1280 × 480 cluster glass (LQ123K1LG03, 330 cd/m²) — works only if the binnacle brow shades it; the electrical build's measurement day (M-1) is the moment to judge the brow. Chain (ii): RGB → HDMI encoder into the scaler board of a 900–1000-nit 1920 × 720 bar panel — the default. `V-084` then verifies the BT817 timing against whichever glass; `T-051` orders the BT817 eval board first, which proves the whole chain on the bench.

**ANSWER:**
>

**V-065 · The PMU's own CAN export format.** ECUMaster fixes it; messages 0x100–0x130 in `01-DESIGN/CAN-MESSAGES.md` are intent and must be reconciled against the real export read out of the client once the PMU is configured in the car.

**ANSWER:**
>

**V-067 · Tach pulses per revolution.** Assumed 2 for a 2-rotor off the leading coil. Wrong scales every RPM reading by a constant. Meter session or FSM.

**ANSWER:**
>

## Sourcing

**T-031 / V-060 · Mirrors** — larger, heated, digital; confirm the conductor count fits the eight D1/D2 cavities (three motor, one heat, one ground are reserved).

**ANSWER:**
>

**T-032 / T-033 · Fuel-door solenoid (never existed on this car) and hatch latch switch (broken, K-016).** Outputs are provisioned on L4-M 3 / L4-M 4.

**ANSWER:**
>

**V-061 · Radar sensor interface** — design the subsystem (`01-DESIGN/FORWARD-WORK.md` Z-002) before the L3-S3 pass-through is uncapped.

**ANSWER:**
>

**T-048 · Flash and label Teensy boards 2 and 3** once the soldering iron is out for the electrical build's ladder resistors.

**ANSWER:**
>

## With the car — ride along with the electrical build's measurement day

**V-063 / T-034 · Tail-light aperture** — width, height, depth, mounting. The whole strip design is scaled from a nominal 30 cm.

**ANSWER:**
>

**V-066 / T-035 · What headlamps are actually fitted today** — 7-inch round or rectangular sealed beams, and whether LED housings are already in.

**ANSWER:**
>

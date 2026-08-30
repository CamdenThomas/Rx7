# Open Queue — Electrical / PMU

*Rev 2026-08 · owns: what is undecided or unconfirmed*

Answered items move to `DECISIONS.md` and leave this file. **IDs are permanent** —
gaps mean something closed.

Questions and verify items are each ordered **easiest to hardest**.

---

# QUESTIONS

## Q-014 · Dash panel envelope
**Ask:** W × H × D behind the dash, plus clearance for the 39-pin lever.
**Blocks:** panel 1:1 drawing, panel parts order, Checklist 0.20–0.21, all of
Phase 4.

A tape measure. The panel is smaller than originally planned — the relay bank
dropped from 16 sockets to 10 when the window relays moved to the sill.

**ANSWER:**
>
>

---

## Q-028 · CAN wake latency
**Ask:** If horn and wink ever move to CAN wake once the MCU exists, what
wake-to-horn latency is acceptable on a cold boot?

Not live yet. Recorded so it isn't rediscovered.

**ANSWER:**
>
>

---


---

# STILL OPEN — module and cluster

## Q-058 · Page switching
**Ask:** How do you change cluster pages — CAN keypad button, or a long-press on
a wink switch?
**Not live** until the multi-page architecture exists. The driving page is built;
diagnostics and trip pages are forward scope in `CLUSTER-DESIGN.md`.

**ANSWER:**
> unique toggle button closer to dash display just a small button that will cycle through
>

---

## Q-059 · PSRAM on the Teensy
**Ask:** Solder 8 MB PSRAM to the Teensy 4.1 pads?
**Cost:** ~$8, and **much easier before the board is installed.**
**Buys:** double-buffering, off-screen composition, room for map tiles or logging
buffers.
**Not needed today** — the 384 KB framebuffer fits in RAM without it.
**Recommendation:** fit it. It is the classic thing you regret not doing once the
board is in the dash.

**ANSWER:**
>
> follow recommendations

---

## Q-060 · Display panel selection **← next hardware decision**
**Ask:** Which 800×480 panel?
**Requirements, in order:**

| Must have                             | Why                                                                                                                        |
|---------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| **800–1000 nits minimum** `[V-058]`   | A wide panel has more area to wash out. **The spec most often omitted from listings — its absence usually means it's low** |
| **8-bit colour mode (RGB332)**        | Halves SPI traffic. Confirm the controller supports it                                                                     |
| SPI interface, ILI9488 / ST7796 class | Matches the dirty-rectangle design                                                                                         |
| Optically bonded or AR treated        | Not an air gap                                                                                                             |
| Backlight PWM input                   | For O20 illumination tracking                                                                                              |

**ANSWER:**
>
>

---

# VERIFY

| ID | Claim | Source |
|---|---|---|
| **V-070** | **12A redline.** `stats.h` assumes 7000 rpm, which also sets the tach red zone | FSM |
| V-071 | Minimum acceptable oil pressure for a 12A at idle. Assumed 1.0 bar | FSM / rotary reference |
| V-072 | FB fuel tank capacity. Assumed 15.9 gal | FSM |
| **V-073** | **IMU mounting orientation on the ICU PCB** must match the axis convention in D-161, or every axis needs a sign flip | Decide before PCB layout |

## Easy — one search, catalogue page, or a look

| ID | Claim | Source |
|---|---|---|
| V-053 | Battery terminal type — SAE or 3/8 threaded. Decides which lugs to buy | Look at it |
| V-051 | Ionic case dimensions before cutting the cargo bin | Tape measure |
| V-054 | Carter P4070 current draw | Carter spec |
| V-052 | Battery heater trigger and winter draw | Ionic docs / app |
| V-014 | DT size-16 contact current rating. Catalogue confirms size 20 = 7.5 A | TE catalogue pp. 169–180 |
| V-057 | TCAN1042/1051 exact part suffix | TI datasheet |
| V-047 | Shielded 16 AWG availability; single-end shield grounding | Wire supplier |
| V-058 | **Display nit rating — 800–1000 minimum.** A wide panel has more area to wash out | Vendor spec |
| V-069 | **Open-barrel crimper die size.** Confirm against a real terminal before buying | Measure the terminal |
| V-040 | Aeromotive Phantom 340 draw at target pressure | Aeromotive spec — future part |

## Medium — needs the car

| ID | Claim | Via |
|---|---|---|
| V-002 | Alternator output rating | Read the case |
| V-055 | Sill space behind the kick panel — 4 relays, 3 fuses, ground stud | Tape measure |
| V-038 | Coolant level unit and oscillator still fitted | Inspect |
| V-037 | Fuel sender ohm range, empty → full | Measure at the tank |
| V-050 | Which ignition outputs stay live in RUN and START | T-023 continuity test |
| V-030 | Pop-up motor internal limit pinout — drive vs limit pins | T-011 continuity test |
| V-067 | **Tach pulses per revolution.** Assumed 2 for a 2-rotor off the leading coil. Wrong scales every RPM reading by a constant | Meter session or FSM |

## Hard — blocked on something else

| ID | Claim | Blocked by |
|---|---|---|
| V-065 | **PMU's own CAN export format.** ECUMaster fixes it, we don't. Gates all firmware | The client — Checklist 2.5 |
| V-019 | Can the 12A alternator carry the migrated load | Measured draw, T-014 |
| V-060 | New mirror conductor count and control protocol | Pick the mirrors, T-031 |
| V-033 | Fuel-door and hatch solenoid channel allocation | Next SPEC pass |
| V-041 | Will the tach ever feed the PMU directly | Needs a scope |
| V-061 | Radar sensor interface | Design the subsystem |
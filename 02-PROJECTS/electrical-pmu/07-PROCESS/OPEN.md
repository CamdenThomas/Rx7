# Open Queue — Electrical / PMU

Questions have an **ANSWER** block. Answered items move to `DECISIONS.md` and
leave here. **IDs are permanent** — gaps mean something closed.

**2026-08:** lighting split into `02-PROJECTS/lighting-body/` (D-123). Q-048,
V-063, V-064, V-066 moved there.

---

# OPEN QUESTIONS

### Q-014 · Dash panel envelope
**Ask:** W × H × D behind the dash, plus 39-pin lever clearance.
**Blocks:** panel 1:1 drawing, panel parts order, Checklist 0.20–0.21.
**A tape measure, not a decision.** Needs nothing that's in the post.

**ANSWER:**
>
>

---

### Q-037 · Cluster display format
**Ask:** Two round TFTs in the factory binnacle shape, or one wide TFT?
**Rides on it:** bezel fabrication, MCU bandwidth, how much dash character
survives. Two round on SPI is the easy path; one wide needs a parallel interface
or display controller to feel smooth.
**Aesthetic — your call.** Gates the display order.
**Note:** this is the *instrument cluster*, not exterior lighting. Stays in this
project.

**ANSWER:**
>
>

---

### Q-028 · CAN wake latency
Not live until the MCU exists. Recorded so it isn't rediscovered.

**ANSWER:**
>
>

---

# ASSUMPTIONS

### A-005 · Start relay location
**Recommendation:** Not at the starter. Mount K9 **high on the inner fender or
firewall.** The relay keeps solenoid current off the PMU — it doesn't need to be
adjacent. Pull-in is 15–25 A and 12 AWG over three or four feet loses almost
nothing. Dry side, reachable, no ingress rating needed.

**ANSWER:**
> follow recommendations
>

---

# VERIFY — still open

### Easy

| ID    | Claim                                                                 | Source                           |
|-------|-----------------------------------------------------------------------|----------------------------------|
| V-014 | DT size-16 contact current rating. Catalogue confirms size 20 = 7.5 A | TE contacts section, pp. 169–180 |
| V-047 | Shielded 16 AWG availability; single-end shield grounding             | Wire supplier                    |
| V-040 | Aeromotive Phantom 340 draw at target pressure                        | Aeromotive spec                  |
| V-054 | Carter P4070 current draw                                             | Carter spec                      |
| V-051 | Ionic case dimensions before cutting the cargo bin                    | Tape measure                     |
| V-052 | Battery heater trigger and draw                                       | Ionic docs / app                 |
| V-053 | Battery terminal type — SAE or 3/8 threaded                           | Look at it                       |
| V-057 | TCAN1042/1051 exact part suffix                                       | TI datasheet                     |
| V-058 | Display nit rating — 800–1000 min                                     | Vendor spec                      |
| V-059 | Teensy availability                                                   | Re-check before final boards     |

### Medium — needs the car

| ID    | Claim                                                     |
|-------|-----------------------------------------------------------|
| V-002 | Alternator output rating                                  |
| V-050 | Which ignition outputs stay live in RUN and START — T-023 |
| V-037 | Fuel sender ohm range                                     |
| V-030 | Pop-up motor internal limit pinout — T-011                |
| V-055 | Sill space behind the kick panel                          |
| V-038 | Coolant level unit and oscillator still fitted            |

### Hard — blocked

| ID    | Claim                                                         | Blocked by                 |
|-------|---------------------------------------------------------------|----------------------------|
| V-065 | **PMU's own CAN export format.** ECUMaster fixes it, we don't | The client, once installed |
| V-019 | Can the 12A alternator carry the migrated load                | T-014                      |
| V-041 | Will the tach ever feed the PMU                               | Needs a scope              |
| V-033 | Fuel-door and hatch solenoid channel allocation               | Next SPEC pass             |
| V-060 | New mirror conductor count and control protocol               | Pick the mirrors           |
| V-061 | Radar sensor interface                                        | Design the subsystem       |

---

# MOVED TO `lighting-body`

| ID    | Was                                             |
|-------|-------------------------------------------------|
| Q-048 | Which headlamp unit — 4×6, 5×7, or 7-inch round |
| V-063 | Tail light aperture dimensions                  |
| V-064 | DOT/SAE LED module sourcing                     |
| V-066 | Round or rectangular sealed beams on this car   |

---

# RESOLVED

| ID             | Answer                                                                        |
|----------------|-------------------------------------------------------------------------------|
| **Q-044**      | **Pop-ups STAY.** Lamp change deferred to the lighting project (D-110, D-123) |
| Q-042          | IMU fitted to the ICU board (D-109)                                           |
| Q-041          | CAN message map finalised (D-106)                                             |
| Q-046          | Tail light driver PCB — **moved to lighting project** (D-111, D-123)          |
| Q-047          | Reverse section 5 cm, 2.2 cm strip — **moved to lighting project**            |
| Q-045          | Rear disc conversion still planned; drums were an interim (D-113)             |
| A-007          | Converted to task T-011 (D-112)                                               |
| V-044          | **DTP is 2-way and 4-way only** — confirmed from the TE catalogue (D-115)     |
| V-062          | TE ICT Terminals & Connectors 2018 (D-114)                                    |
| V-013          | DTP size-12 adequate for 25 A legs                                            |
| Earlier rounds | Q-010 through Q-039, A-009, V-023 through V-049 → D-065 through D-105         |

---

# CLOSED 2026-08 — infotainment

| ID        | Question                              | Answer                                |
|-----------|---------------------------------------|---------------------------------------|
| **Q-053** | Head unit, Pi minimap, or Pi cluster? | **Head unit** (D-128)                 |
| Q-049     | Which Bluetooth A2DP module           | **Moot** — head unit does audio       |
| Q-050     | Turn-by-turn text or map picture?     | **Moot** — head unit provides the map |
| Q-051     | Delete the head unit?                 | **No. It stays**                      |
| Q-052     | Where does a Pi display live?         | **Moot** — no Pi                      |
| Q-054     | Which map renderer?                   | **Moot** — no renderer                |

## Still open

### Q-055 · Head unit selection
**Worth paying for:** wireless CarPlay (no cable to the phone), a **physical
volume knob**, pre-outs rather than speaker-level only, an external control input
if you want buttons on the keypad or column, and a bezel that can be integrated
rather than looking obviously aftermarket in a 1982 dash.

Double-DIN aperture is already in the dash plan. Switched feed on O10 via
`L3-M 1`, constant keep-alive off busbar F1 via `L3-M 2` — **no wiring change**,
that allocation was never removed.

**ANSWER:**
>
>

---

### Q-037 · Cluster display format — unchanged and still open
Two round TFTs in the factory binnacle shape, or one wide TFT?

**The ICU is gauges only** (D-130). No map, no turn-by-turn strip, no BLE module.
That's back to exactly what D-083 specified — which means this question is
unaffected by the head unit decision and still needs answering before the display
order.

**ANSWER:**
>
>

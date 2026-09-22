# BLOCKS

*The one page Camden writes in.*

Type your answer after `**SOLVE:**` - on that line or the lines under it. Plain
sentences, any length, no markers to keep. Blank means unanswered. Skipping one costs
nothing: it stays open and comes back.

Nothing here is ever regenerated, and nothing but you writes in it.

**This page holds only what is still open.** Once you answer a block, it is applied
through the record, becomes a decision whose `closes` names it, and is then deleted from
here — `DECISIONS.md` is where a settled question lives, with the reasoning and the
consequences. So a short page means a short queue, not a lost history: search
`DECISIONS.md` for a block's id and you will find the ruling it became.

**Block ids are `project.number`.** `00.01` was the first block ever raised for the
electrical project, `01.07` the seventh for the luxury package. Numbers are never reused,
so gaps are blocks that have already been answered. Each project has its own header
below. (Until 2026-09-21 blocks were `BLK-###`; every old id is still findable in its
project's `retired` table.)

An answered block that is not yet applied is advisory - it never refuses a commit.

## CAR · Car

*Nothing open.*

## 00 · Electrical

### 00.26 · Door and hazard wake: a pulse, or held for as long as the switch is closed
**Ask** Should the door and A8 wake stages wake the PMU only at the moment a switch closes (a pulse), or for as long as it stays closed?
**Opened** 2026-09-21
**Why** With the PMU asleep, the door switches and the hazard / horn / wink switches can only wake it through two small transistor circuits on the dash node (the "wake stages"). Redoing them for D-368's 47 kΩ resistors (work A10) turned up three things. (1) The old v2 circuit could never have woken the PMU. Its output feeds the wake strip through 100 kΩ, and the strip has a 10 kΩ drain to ground, so it only reaches about 1.1 V on pin 7. (2) A working circuit is possible. It needs a transistor that switches the sensing current on only while the PMU sleeps, so the switch readings are untouched while it is awake, and a second transistor per side that is strong enough to drive pin 7. (3) The choice below. If a stage wakes the PMU for as long as a switch is closed, a door left ajar (or a stuck horn contact) keeps pin 7 high and the PMU stays on until the battery's BMS cuts off. That makes D-248's promise ("a stuck door cannot hold the car awake") false in hardware, whatever KEEP_ALIVE does. A pulse stage wakes the PMU once, and the PMU then decides from its own reading of the door and hazard lines whether to stay awake.
**Options**
- (a) Held (level) stages. Built only from parts already in the cart (seven of the ten 2N3904s, the E24 resistor kit), so $0. A door left ajar holds the PMU on (150 mA assumed, maybe under 20 mA, LD17) until the BMS cuts off. D-248 and the `sleep` rule get rewritten to say so. Forecloses nothing.
- (b) Pulse (edge) stages. The same transistors and resistors plus one small capacitor per side: 2 × about 1 µF film, about $1, one new cart line. D-248 stays true, and the hazard still flashes with the key out, because the pulse wakes the PMU and the `sleep` rule keeps it awake while A8 reads HAZARD. Risk: the pulse has to outlast the PMU's boot, and the manual does not give that time. CK12 measures it before anything is soldered.
**Recommend** (b), unless you would rather spend $0 now and accept that a door left ajar can flatten the battery.
**Stops** A10 (the stage values), and behind it E7 and E15 (building the resistor sub-assemblies and the wake network).
**SOLVE:**

## 01 · Luxury

*Nothing open.*

## 02 · Engine

*Nothing open.*

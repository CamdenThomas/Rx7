# SWITCH SCHEDULE — every control surface in the car

*Rev 2026-09-01 (D-209) · owns: the operator interface — every switch, where it lives, what it feeds, and whether it is bought. Cavity assignments are [`../02-HARNESS/PIN-MAP.md`](../02-HARNESS/PIN-MAP.md)'s; ladder values are [`LADDERS.md`](LADDERS.md)'s; the money is [`../05-PROCESS/BOM.md`](../05-PROCESS/BOM.md)'s.*

**The rule (D-209):** the **column combination switch stays** — it is the one
control Camden judged sound. **Everything else in the car is replaced**, broken
or not, because they are all at or near end of life on a 44-year-old car and
the dash is open exactly once (D-202).

## Contents

1. What stays · 2. Hardwired switches — bought · 3. The control-panel drop ·
4. Sense switches — lights and latches · 5. Deferred to the luxury package ·
6. Why wink is hardwired · 7. Open calls

---

## 1 · What stays — the column combination switch

Three factory assemblies on the steering column, all mechanically sound.
They feed **ladders**, so each is one conductor rather than five (D-019).

| OEM | Function | Signal | Cavity |
|---|---|---|---|
| E-01 LIGHT | Headlights — OFF / PARK / HEAD. Also commands the pop-ups (D-038) | A15 ladder, 12 V side | L3-S1 2 |
| E-01 DIMMER | Dimmer / passing flash | Software off A15 (D-051, Q-065 → D-184) | — |
| F-02 TURN | Turn stalk — L / off / R | A1 ladder to ground | L3-S1 3 |
| F-02 HAZARD | Hazard | A8 closure + separate wake conductor | L3-S1 6 · wake L3-S2 2 |
| D-03 | Wiper stalk — off / INT / LO / HI / WASH | A2 ladder to ground | L3-S1 4 |

**The horn stays on the steering pad** (D-209 confirms). It closes to ground
and joins the A8 node through 12 kΩ (D-190), so it reads in every key
position and wakes the car asleep through the plate PNP.

## 2 · Hardwired switches — bought in Order 3

Every one of these is a *hardwired* switch: it must work with the car asleep,
or it carries real current, or both. **None of them can live on a control
panel** — that is what makes them hardwired.

| # | Switch | Type | Feeds | Qty | Part |
|---|---|---|---|---|---|
| SW-1 | **Wink LEFT** | **SPDT momentary**, panel, illuminated | NC pole → K2 coil path · NO pole → wake strip (D-189) | 1 | mxuteuk CB16AY-11D 16 mm, 1NO+1NC, 5 A |
| SW-2 | **Wink RIGHT** | as above | NC pole → K1 coil path · NO pole → wake strip | 1 | same 5-pack |
| SW-3 | **Brake pedal** | Plunger, NO | A3 closure to ground via 4.7 kΩ (L3-S1 5) | 1 | RX-7 1982 replacement, no-cruise variant |
| SW-4 | **Window DRV** | Momentary rocker, 5-pin DPDT | K5/K6 coils via L3-S2 3–4 | 1 | weideer 5-pin 20 A |
| SW-5 | **Window PASS** | as above | K7/K8 coils via L3-S2 5–6 | 1 | same 2-pack |

**Wink wiring is not optional detail.** Each wink switch's NC pole sits in
series with the *opposite* side's K1/K2 coil, so holding a wink blocks the
other lamp and only the winked side moves when the PMU runs the half-cycle
(D-189). The NO pole feeds the diode-OR wake strip so a wink works key-out.
A plain pushbutton will not do this — it must be a **changeover** switch.

**Window switches are bought now and fitted whenever the motors arrive.**
L3-S2 3–6 are already run and capped (D-131); the switches are ~$9 and the
console is open during this build. Buying them now means the luxury package
never has to touch the dash harness.

## 3 · The control-panel drop — `DP-KEY`, wired and capped

**No ECUMaster keypad is bought (D-210).** Every button function waits and
is integrated into the **custom A/C panel** in the luxury package.

What gets built now is the *drop*, not the device — four conductors at the
dash post, terminated and capped:

| Cav | Conductor | Source |
|---|---|---|
| 1 | CAN2 H | pin 24 |
| 2 | CAN2 L | pin 37 |
| 3 | +12 V switched | O10 accessory bus |
| 4 | Ground | DP-GND (a permitted ground crossing, D-037) |

That is the universal set — CAN, switched power, ground. Whatever the panel
turns out to be (a CAN keypad after all, a DCU faceplate, or a custom
board), it plugs in. **This is what "no wiring in the luxury package" means
in practice.**

### The three functions that wait

| Function | Where it went | Consequence now |
|---|---|---|
| **Rear defog grid** | Custom panel | **No rear defogger this build.** O4 and the grid feed are wired, and the `DEFOG` channel stays configured *and disabled* (D-210) with its 15 min auto-off already written. Nothing commands it until the panel lands. **Winter driving: no defog.** |
| **Hatch release** | Custom panel | The solenoid branch (D-180) is unbuilt; the hatch opens on its key as it does today |
| **Fuel-door release** | Custom panel | Never existed from the factory (K-017) — nothing is lost |

**Interior-light override is deleted outright**, not deferred — `INTERIOR`
now reads `(A6 != CLOSED)` with no override term (D-209, D-210).

**If a defogger before the luxury package matters**, one hardwired switch on
a spare `L3-S2` cavity restores it for the cost of a switch and one
conductor. Not taken — raise it if a winter without a rear defogger sounds
worse than it does on paper.

## 4 · Sense switches — lights and latches

Simple closures. Bought as one type: adjustable plunger pin switches, 6 off.

| # | Switch | Feeds | Note |
|---|---|---|---|
| SW-6 | Door pin — driver | A6 ladder via D1 3 → L4-S 2 | Switches to ground |
| SW-7 | Door pin — passenger | A6 ladder via D2 3 → L4-S 2 | |
| SW-8 | **Glove box lamp** | O20 interior branch, local | Manual latch; the lamp lights only with the door open. **No PMU input** — the switch grounds the lamp directly |
| SW-9 | Luggage compartment | A6 ladder 4th state via L4-S 3 | `A-012` — re-run the ladder maths before fitting |
| SW-10 | Hatch ajar | A6 ladder / spare | Factory switch broken (K-016, `T-033`) |
| SW-11 | spare | — | |

## 5 · Deferred to the luxury package

Fabrication and installation only — **every conductor is run in this build.**

| Feature | Wiring state now | What the luxury package adds |
|---|---|---|
| **Digital A/C + the control panel** | DP-DCU landed and capped · **DP-KEY landed and capped** · O15 comfort bus live | The panel itself, DCU module, servos, faceplate — and defog / hatch / fuel-door controls fold into it (D-210) |
| Heated seats | F10 position live on the O15 block, 6 spare fused positions | Elements; controls join the custom panel |
| Heated mirrors + digital control | D1/D2 cav 4–7 run and capped · F14 at the sill | Mirrors (`T-031`, `V-060`) |
| Power windows | L3-S2 3–6 run · sill K5–K8 sockets fitted empty · **switches bought** | Motors, regulators |
| Radar | L3-S3 1–3 → L4-S 5–7 run as pass-through | Sensors, module (`V-061`) |
| LED lighting | Sockets and channels unchanged (D-119/D-122) | Bulbs, then re-set soft fuses |

## 6 · Why wink is hardwired and never a panel button

Asked and answered, 2026-09-01. Three independent reasons — and they apply
to the custom A/C panel exactly as they applied to the keypad:

1. **It must work asleep.** A wink is a parked greeting — key out or ACC
   (D-190). Anything on DP-KEY is powered from the accessory bus O10 and is
   dead when the car sleeps (`A-013`). It cannot send anything.
2. **It is a changeover, not a signal.** The NC pole physically interrupts
   the opposite side's relay coil (D-189). No CAN message can do that.
3. **The NO pole is a wake source.** It feeds the diode-OR strip directly —
   one of the eight inputs that gets the PMU out of sleep in the first place.

## 7 · Open calls

| Item | Question |
|---|---|
| **Ignition switch** | Column-mounted but *not* the combination switch — OFF/ACC/ON/START feeding the A16 ladder plus both wake contacts. Replace it too? It is the highest-cycle switch in the car and the one that strands you |
| **Parking brake sense** | D-031 parked it on a keypad that no longer exists, and a keypad could never sense anything anyway. It needs a real switch into a spare ladder state, or an explicit deletion |
| **Blower speed switch** | G-15 rides with the blower motor choice (K-023, `T-038`). Buy them together |
| **Hatch latch** | K-016 — the factory switch is broken and the replacement is unsourced (`T-033`) |

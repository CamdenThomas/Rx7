# SCHEMATICS — panel sub-circuits

*Rev 2026-08-31 · owns: the wake network, the H-bridges, the constant bus and the ground architecture — everything on the plate and at the sill that is not simply a wire from a PMU pin to a receptacle.*

Relay and fuse numbering is [`SPEC.md`](SPEC.md) §3's. Cavity numbers are
[`../02-HARNESS/PIN-MAP.md`](../02-HARNESS/PIN-MAP.md)'s. The one-page drawing of
everything here is [`panel-sheet.svg`](panel-sheet.svg) (X-002 — hand-drawn, not generated).

## Contents

1. Diode-OR wake network · 2. Pop-up H-bridges · 3. Window H-bridges
(provisioned) · 4. Constant bus · 5. Comfort bus · 6. Ground architecture ·
7. Parts summary

---

## 1 · Diode-OR wake network (D-056, D-072)

Pin 7 (+12 V SW) turns the PMU on. Anything that must wake the car feeds it
through a diode so the sources cannot backfeed each other. **Eight inputs —
the strip is full (D-189, D-190).**

```
   ACC (key)    ──|>|──┐     L3-S1 12
   RUN (key)    ──|>|──┤     L3-S2 1
   Hazard sw    ──|>|──┤     L3-S2 2
   Door pin     ──|>|──┼──── PIN 7  (+12V SW)      sill inverter (D-188)
   Horn (plate PNP off the A8 node — D-190)──┤ │
   O22 latch    ──|>|──┘     internal     └── 10 kΩ ── GND   (bleed, ensures clean off)
```

| Source | Why it wakes the car |
|---|---|
| ACC, RUN | Normal key-on |
| Hazard switch | Hazards must work with the key out — legally and practically |
| Door pin | Interior lighting and the theatre fade on entry |
| Horn switch | The horn sounds with the PMU asleep, same as the hazards (D-072) |
| **O22 self-latch** | Lets the PMU hold itself awake and shut down on its own timer |
| Wink L / R | A wink must work from asleep — the NO poles feed the strip; the request is pin-7-only, key out or ACC (D-189, `Q-071` → D-190) |

**Diodes:** 1N5819 Schottky, 1 A 40 V. Schottky for the low forward drop —
a 1N4007's 0.7 V eats into the wake threshold at cold-crank voltage.

**The bleed resistor matters.** Without it, leakage through eight diodes can hold
pin 7 above the turn-off threshold and the PMU never sleeps. 10 kΩ to ground.

**Build:** one 8-position terminal strip, all eight used (the wink NO poles
took the last two — D-189). Label every input on the
strip itself. Diodes soldered directly to the strip, band (cathode) toward pin
7. Supply for the switch-side sources is busbar F3 (5 A).

The door-pin wake runs through a small PNP inverter at the sill node —
emitter on the F3 supply, base sensing the A6 conductor through ~220 kΩ,
output into the door-pin wake diode (`Q-069` → D-188; adds ~54 µA to A6,
re-verify that ladder at Phase 6). One loose end, in [`OPEN.md`](../05-PROCESS/OPEN.md): the horn reads on
the A8 ladder in every key position (`Q-071` → D-190; its asleep wake is a
second plate PNP on the A8 node); winks are pin-7-only — key out or ACC. `V-075` asks whether the PMU's native shutdown delay
makes the O22 latch unnecessary.

---

## 2 · Pop-up run relays — K1 (LH), K2 (RH), on the plate (D-186)

The factory motors spin in **one direction only**: a crank flips the lamp
over-centre each half-revolution and the internal cam stops the motor at each
end. There is nothing to reverse — one SPDT relay per side; K3/K4's sockets
go spare.

```
              O1 MOTOR BUS (25 A, flyback)
                        │
          ┌─────────────┴──────────────┐
       F6 (LH) 10 A               F7 (RH) 10 A
      ┌───┴───┐                   ┌───┴───┐
      │  K1   │30              30 │  K2   │
      │       │87 ── run feed ──→ │       │87 ── run feed ──→ E-04
      │       │     E-03 (V-081)  │       │
      │  87a ─┴─ GND (brake)      │  87a ─┴─ GND (brake)
      └───┬───┘                   └───┬───┘
  coil: 85 ── GND              85 ── GND
        86 ── RUN LH cmd       86 ── RUN RH cmd
```

**Raise and lower are the same electrical act.** Energise the relay until
that side's YG transit contact opens again (limit reached); a **4 s timeout
with YG still closed = obstruction** — stop and fault, which is exactly what
the factory indicator signalled by staying lit. Position is tracked in
software ([`PMU-CONFIG.md`](PMU-CONFIG.md) §2); the wink switches (L3-S1 9/10) run one side a
single half-cycle. 87a-to-ground gives dynamic braking at rest for free.
Which E-03/E-04 conductor is the cam-interrupted run feed is `V-081`.

**Coils (D-189):** both fed from O1 through steering diodes, each in series
with the *opposite* side's wink-switch NC pole — holding a wink blocks the
other side, so only the winked lamp moves when the PMU runs the half-cycle.
The wink NO poles feed the wake strip so a wink works from asleep; the request is
pin-7-only, key out or ACC (`Q-071` → D-190).

**Flyback:** O1 has the integrated high-power diode. Relay *coils* still need
their own — a 1N4007 across each coil, band to +.

## 3 · Window H-bridges — K5–K8, at the sill — PROVISIONED

**This car has manual windows (D-131).** The bridge is designed and the
hardware is provisioned — sockets fitted, F8/F9 positions provisioned, every
conductor run and capped — so that fitting power windows later is an
afternoon, not a harness job. Nothing below is live.

Electrically identical to the pop-up bridge. K5/K6 driver, K7/K8 passenger,
on the sill plate (D-065), fed by one 12 AWG motor-bus conductor from O1
(L4-P 3) and commanded by four 16 AWG lines from the dash switches
(L3-S2 3–6 → L4-M 9–12).

```
   L4-P 3  ──── 12 AWG (capped) ────  SILL: K5–K8 commons
                                        │
   L3-S2 3 → L4-M  9 ── DRV up   ───── K5 coil
   L3-S2 4 → L4-M 10 ── DRV dn   ───── K6 coil
   L3-S2 5 → L4-M 11 ── PASS up  ───── K7 coil
   L3-S2 6 → L4-M 12 ── PASS dn  ───── K8 coil
                                        │
                                  F8 ───┴─── D1 1/2 motor legs (14 AWG, capped in the door)
                                  F9 ─────── D2 1/2 motor legs
```

**When windows arrive** (add-later detail archived in `99-ARCHIVE/DEFERRED-FEATURES.md` §1): populate
K5–K8, fit F8/F9, uncap, enable the outputs and the interlock — never UP and
DOWN on the same window, never both windows plus both pop-ups at once.

---

## 4 · Constant bus (D-020)

Everything that must survive a PMU shutdown. Fed from the busbar, **not** from
any PMU output.

```
   DP-BAT (2 AWG from the Class-T)
        │
        ├── busbar ──┬── K11 ──┬── F1  15 A ── Head unit constant keep-alive   L3-M 2
        │            │         └── F5  30 A ── Amp / audio constant
        │            ├── F2   2 A ── Diagnostic port +12 V                     DP-DIAG 3
        │            ├── F3   5 A ── Wake diode network supply
        │            ├── F4  10 A ── A/C factory circuit
        │            └── F13  —   ── radar module feed (D-191; deferred, V-061)
        │
        └── PMU STUD (150 A max)
```

**K11 constant-bus master** sits between the busbar and F1/F5, driven by the
O22 latch. It lets the box drop the true-constants on a long park so the audio
keep-alive cannot flatten the lithium. F2, F3 and F4 stay live always.

**Sleeping draw with K11 open:** PMU standby only, ~0.15 A. **With K11
closed:** plus the head unit clock, 10–20 mA.

---

## 5 · Comfort bus (D-011, D-073)

O15 is a **dumb 25 A feed** to L3-P 2. The DCU switches seat heat, seat cool,
nozzles and the de-icer downstream and enforces the heat/cool interlock; the
PMU carries no comfort logic. Until the DCU exists, F10 (10 A, seats) and F11
(5 A, nozzles and de-icer) are the only protection between the PMU and the
comfort loads — size them accordingly. The mirror-heat branch is F14 at the
sill; the conductor that carries O15 to the sill is `Q-062` → D-181.

---

## 6 · Ground architecture (D-017)

Not a schematic so much as a rule, but it belongs with these.

```
   PMU pin 25 ──(10 AWG, ≤6 in)── DP-GND bus ──── chassis, dash area

   Each zone:   devices ── local star node ── chassis
                (engine block / front / rear / sill)
```

**No ground crosses a leg connector** except the diagnostic port, keypad, ICU
and DCU returns (D-037), which are box-adjacent drops. Door grounds terminate
at the sill stud, never inside the door. The fuel pump gets its own return at
the rear node — the structural fix for K-008.

Pin 25 carries flyback return for every inductive load on the device. It is
the shortest and heaviest wire on the plate and the one to get right.

---

## 7 · Parts summary — plate and sill

| Item | Qty | Part |
|---|---|---|
| Wake diodes | 8 (8 used — D-189, D-190) | 1N5819 Schottky 1 A |
| Wake bleed resistor | 1 | 10 kΩ 1/4 W |
| A15/A16 bias resistors (D-167) | 2 | 100 kΩ 1/4 W |
| Relay coil flyback diodes | 4 fitted (+4 with windows) | 1N4007 |
| Terminal strip, wake network | 1 | 8-position |
| Relays, plate | 4 | ISO micro, SPDT (K1, K2, K11, K12) |
| Relay sockets, plate | 10 | ISO micro — 4 populated; K3/K4's freed as spares (D-186) |
| Relay sockets, sill | 4 | ISO micro — **empty** |
| Fuse blocks, plate | 12 positions — F1–F7, F10–F13, F15, as 3 × 4-pos **independent-feed** blocks (D-203b — six different sources) | ATO / ATC |
| Fuse positions, sill | 3 | F8, F9 (empty), F14 |
| Busbars | 2 | always-hot, ground |

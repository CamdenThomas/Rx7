# SCHEMATICS — panel sub-circuits

*Rev 2026-08-30 · owns: the wake network, the H-bridges, the constant bus and the ground architecture — everything on the plate and at the sill that is not simply a wire from a PMU pin to a receptacle.*

Relay and fuse numbering is [`SPEC.md`](SPEC.md) §3's. Cavity numbers are
[`../02-HARNESS/PIN-MAP.md`](../02-HARNESS/PIN-MAP.md)'s.

## Contents

1. Diode-OR wake network · 2. Pop-up H-bridges · 3. Window H-bridges
(provisioned) · 4. Constant bus · 5. Comfort bus · 6. Ground architecture ·
7. Parts summary

---

## 1 · Diode-OR wake network (D-056, D-072)

Pin 7 (+12 V SW) turns the PMU on. Anything that must wake the car feeds it
through a diode so the sources cannot backfeed each other. **Six inputs on an
eight-position strip.**

```
   ACC (key)    ──|>|──┐     L3-S1 12
   RUN (key)    ──|>|──┤     L3-S2 1
   Hazard sw    ──|>|──┤     L3-S2 2
   Door pin     ──|>|──┼──── PIN 7  (+12V SW)      conductor: Q-062
   Horn sw      ──|>|──┤     L3-S1 11     │
   O22 latch    ──|>|──┘     internal     └── 10 kΩ ── GND   (bleed, ensures clean off)
```

| Source | Why it wakes the car |
|---|---|
| ACC, RUN | Normal key-on |
| Hazard switch | Hazards must work with the key out — legally and practically |
| Door pin | Interior lighting and the theatre fade on entry |
| Horn switch | The horn sounds with the PMU asleep, same as the hazards (D-072) |
| **O22 self-latch** | Lets the PMU hold itself awake and shut down on its own timer |

**Diodes:** 1N5819 Schottky, 1 A 40 V. Schottky for the low forward drop —
a 1N4007's 0.7 V eats into the wake threshold at cold-crank voltage.

**The bleed resistor matters.** Without it, leakage through six diodes can hold
pin 7 above the turn-off threshold and the PMU never sleeps. 10 kΩ to ground.

**Build:** one 8-position terminal strip, six used. Label every input on the
strip itself. Diodes soldered directly to the strip, band (cathode) toward pin
7. Supply for the switch-side sources is busbar F3 (5 A).

Two loose ends, both in [`OPEN.md`](../07-PROCESS/OPEN.md): the door-pin wake needs a 12 V-side
conductor from the sill that is not yet allocated (`Q-062`), and the horn
switch needs a PMU *input* as well as a wake diode (`Q-063`). `V-075` asks
whether the PMU's own shutdown delay makes the O22 latch unnecessary.

---

## 2 · Pop-up H-bridges — K1–K4, on the plate

Two SPDT relays per side. This is the classic reversing pair: both relays idle
to ground, and energising one sends current through the motor in that direction.

```
              O1 MOTOR BUS (25 A, flyback)
                        │
          ┌─────────────┴─────────────┐
          │  F6 (LH) / F7 (RH) 10 A   │
      ┌───┴───┐                   ┌───┴───┐
      │  K1   │ 30            30  │  K2   │
      │       │                   │       │
   87a│   │87 │                87a│   │87 │
      │   │   │                   │   │   │
     GND  └───┼─── MOTOR A    B ───┘  GND
              │                   │
              └─── POP-UP LH ─────┘        L2-P1 3 / 4

   K1 coil: 85 ── GND      K2 coil: 85 ── GND
            86 ── RAISE cmd          86 ── LOWER cmd
```

| K1 | K2 | Result |
|---|---|---|
| off | off | Both motor legs grounded — **motor braked** (D-057) |
| **on** | off | A = +12, B = GND — motor runs UP |
| off | **on** | A = GND, B = +12 — motor runs DOWN |
| on | on | Both legs at +12 — no current, motor stopped |

**Both-off = braked** is the important property. The motor cannot coast past
its limit switch. **K3/K4 are identical** for the right side, on L2-P2 1/2.

**Limit switches are inside the motor** and interrupt drive at the end of
travel mechanically. The A4/A5 ladders read position so software knows where
the lamp is — they do not carry motor current. Pinout by continuity test
(`T-011`); the A4/A5 values in [`LADDERS.md`](LADDERS.md) are provisional until then.

**Command sources:** RAISE / LOWER from the A15 headlight ladder in software
(D-038); wink switches (L3-S1 9/10) drive one side's pair independently.

**Flyback:** O1 has the integrated high-power diode. Relay *coils* still need
their own — a 1N4007 across each coil, band to +.

---

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

**When windows arrive** ([`../04-SUBSYSTEMS/DEFERRED-FEATURES.md`](../04-SUBSYSTEMS/DEFERRED-FEATURES.md) §1): populate
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
        │            └── F13  —   ── spare — three claims, Q-061
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
sill; the conductor that carries O15 to the sill is `Q-062`.

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
| Wake diodes | 8 (6 used) | 1N5819 Schottky 1 A |
| Wake bleed resistor | 1 | 10 kΩ 1/4 W |
| A15/A16 bias resistors (D-167) | 2 | 100 kΩ 1/4 W |
| Relay coil flyback diodes | 5 fitted (+4 with windows) | 1N4007 |
| Terminal strip, wake network | 1 | 8-position |
| Relays, plate | 5 | ISO micro, SPDT (K1–K4, K11) |
| Relay sockets, plate | 10 | ISO micro — 5 populated |
| Relay sockets, sill | 4 | ISO micro — **empty** |
| Fuse block, plate | 13 positions | ATO / mini |
| Fuse positions, sill | 3 | F8, F9 (empty), F14 |
| Busbars | 2 | always-hot, ground |

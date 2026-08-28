# SCHEMATICS — panel sub-circuits

Closes Checklist steps 020–023. Everything on the backer plate that is not simply
a wire from a PMU pin to a bulkhead.

---

## 1 · Diode-OR wake network (step 020)

Pin 7 (+12V SW) turns the PMU on. Anything that must wake the car feeds it
through a diode so the sources cannot backfeed each other.

```
   ACC (key)  ──|>|──┐
   RUN (key)  ──|>|──┤
   Hazard sw  ──|>|──┤
   Door pin   ──|>|──┼──── PIN 7  (+12V SW)
   O22 latch  ──|>|──┘        │
                              └── 10 kΩ ── GND   (bleed, ensures clean off)
```

| Source | Why it wakes the car |
|---|---|
| ACC | Normal key-on |
| RUN | Normal key-on |
| Hazard switch | Hazards must work with the key out — legally and practically |
| Door pin | Interior lighting and the theatre fade on entry |
| **O22 self-latch** | Lets the PMU hold itself awake and shut down on its own timer |

**Diodes:** 1N5819 Schottky, 1 A 40 V. Schottky for the low forward drop —
a 1N4007's 0.7 V eats into the wake threshold at cold-crank voltage.

**The bleed resistor matters.** Without it, leakage through five diodes can hold
pin 7 above the turn-off threshold and the PMU never sleeps. 10 kΩ to ground.

**Build:** one 6-position terminal strip. Label every input on the strip itself.
Diodes soldered directly to the strip, band (cathode) toward pin 7.

`[Q-026]` — if the horn gets a wake diode, it becomes a sixth input here. One
more diode, one more strip position. Provision the strip for 8 either way.

---

## 2 · Pop-up H-bridge (step 021)

Two SPDT relays per side. This is the classic reversing pair: both relays idle to
ground, and energising one sends current through the motor in that direction.

```
              O1 MOTOR BUS (25 A, flyback)
                        │
          ┌─────────────┴─────────────┐
          │                           │
      ┌───┴───┐                   ┌───┴───┐
      │  K1   │ 30            30  │  K2   │
      │       │                   │       │
   87a│   │87 │                87a│   │87 │
      │   │   │                   │   │   │
     GND  └───┼─── MOTOR A    B ───┘  GND
              │                   │
              └─── POP-UP LH ─────┘
   
   K1 coil: 85 ── GND      K2 coil: 85 ── GND
            86 ── RAISE cmd          86 ── LOWER cmd
```

| K1 | K2 | Result |
|---|---|---|
| off | off | Both motor legs grounded — **motor braked** |
| **on** | off | A = +12, B = GND — motor runs UP |
| off | **on** | A = GND, B = +12 — motor runs DOWN |
| on | on | Both legs at +12 — no current, motor stopped |

**Both-off = braked** is the important property. The motor cannot coast past its
limit switch.

**K3/K4 are identical** for the right side.

**Limit switches are inside the motor** `[V-030]` and interrupt drive at the end
of travel mechanically. The A4/A5 ladders read position so software knows where
the lamp is — they do not carry motor current.

**Command sources:**
- RAISE / LOWER from the A15 headlight ladder in software (D-038)
- Wink switches drive one side's pair independently

**Flyback:** O1 has the integrated high-power diode. Relay *coils* still need
their own — use a 1N4007 across each coil, band to +.

---

## 3 · Window H-bridge (step 022)

Electrically identical to the pop-up bridge. K5/K6 driver, K7/K8 passenger.

```
   K5 coil 86 ── DRV UP   command
   K6 coil 86 ── DRV DOWN command
   K7 coil 86 ── PASS UP
   K8 coil 86 ── PASS DOWN
```

**Software interlock required:** never energise UP and DOWN on the same window
simultaneously, and never run both windows plus both pop-ups at once — see the
O1 worst-case note in `LOADS.md`.

`[Q-025]` — if these relays move to the sill, K5–K8 leave the box and the four
12 AWG legs in L4-P2 become two feeds plus four control wires.

---

## 4 · Constant bus (step 023)

Everything that must survive a PMU shutdown. Fed from the busbar, **not** from
any PMU output.

```
   DP-BAT (4 AWG from Class-T)
        │
        ├── busbar ────┬── F1  15 A ── Head unit constant keep-alive
        │              ├── F2   2 A ── Diagnostic port +12 V
        │              ├── F3   5 A ── Wake diode network supply
        │              ├── F4  10 A ── A/C factory circuit
        │              └── F5  30 A ── Amp / audio constant
        │
        └── PMU STUD (150 A max)
```

**K11 constant-bus master** sits between the busbar and F1/F5, driven by the O22
latch. It lets the box drop the true-constants on a long park so the audio
keep-alive cannot flatten the lithium. F2, F3 and F4 stay live always.

**Total sleeping draw with K11 open:** PMU standby only, ~0.15 A.
**With K11 closed:** plus head unit clock, ~20–40 mA.

---

## 5 · Ground architecture

Not a schematic so much as a rule, but it belongs with these.

```
   PMU pin 25 ──(10 AWG, ≤6 in)── DP-GND bus ──── chassis, dash area
   
   Each zone:   devices ── local star node ── chassis
                (engine block / front / rear / sill)
```

**No ground crosses a leg connector** except the diagnostic port and keypad
returns (D-037), which are box-adjacent.

Pin 25 carries flyback return for every inductive load on the device. It is the
shortest and heaviest wire on the plate and the one to get right.

---

## Parts summary

| Item | Qty | Part |
|---|---|---|
| Wake diodes | 8 (5 used) | 1N5819 Schottky 1 A |
| Wake bleed resistor | 1 | 10 kΩ 1/4 W |
| Relay coil flyback diodes | 11 | 1N4007 |
| Terminal strip, wake network | 1 | 8-position |
| Relays | 11 | ISO micro, SPDT |
| Relay sockets | 16 | ISO micro |
| Fuses | 13 | ATO / mini |

---

## UPDATE 2026-08 — relay bank split

`[D-065/067]` The eleven relays are no longer all on the plate.

| Relay | Function | Location |
|---|---|---|
| K1–K4 | Pop-up H-bridges | **Dash post plate** |
| K5–K8 | Window H-bridges | **Sill node** |
| K9 | Start relay | **Inner fender**, engine bay (A-005) |
| K10 | A/C compressor clutch | Engine bay, factory circuit |
| K11 | Constant-bus master | **Dash post plate** |

**Five relays in the box, not eleven.** Socket count drops from 16 to **10** —
five populated, five spare. The plate gets smaller, which matters against an
unmeasured dash envelope (Q-014).

Fuses F8 and F9 (window branch protection) move to the sill with K5–K8.

### Window bridge, revised

Electrically unchanged — the relays just live elsewhere. The commands now travel
as 16 AWG signal down the tunnel instead of the motor legs travelling as 12 AWG
power.

```
   L4-P cav 3  ──── 12 AWG ────  SILL: K5–K8 commons
                                    │
   L3-S ── DRV up  ──── 16 AWG ──── K5 coil
   L3-S ── DRV dn  ──── 16 AWG ──── K6 coil
   L3-S ── PASS up ──── 16 AWG ──── K7 coil
   L3-S ── PASS dn ──── 16 AWG ──── K8 coil
                                    │
                              F8 ───┴─── D1 motor legs A/B
                              F9 ─────── D2 motor legs A/B
```

Software interlock still required: never energise up and down on the same
window, and never both windows plus both pop-ups together.

### Wake network, revised

`[D-072]` The horn now gets a wake diode. Six inputs, strip specced for eight.

```
   ACC (key)   ──|>|──┐
   RUN (key)   ──|>|──┤
   Hazard sw   ──|>|──┤
   Door pin    ──|>|──┼──── PIN 7  (+12V SW)
   Horn sw     ──|>|──┤        │
   O22 latch   ──|>|──┘        └── 10 kΩ ── GND
```

The horn now sounds with the PMU asleep, same as the hazard flashers. That was
the whole objection to putting it on the keypad.

### Comfort bus, revised

`[D-073]` O15 is a **dumb 25 A feed**. The DCU/MCU handles seat heat, seat cool,
mirrors, nozzles and the de-icer downstream, alongside the A/C controls, in the
next project stage. No PMU-side interlock, no second channel, no software
mutual-exclusion on this device.

That also means O15's branch fuses (F10, F11) are the only protection between
the PMU and the comfort loads until the DCU exists. Size them accordingly.

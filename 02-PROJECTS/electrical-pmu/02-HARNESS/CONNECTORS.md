# CONNECTOR SCHEDULE — leg codes and the dash post

Every connector in the car, coded. Power and signal are deliberately split into
separate housings wherever the conductor classes differ enough to matter.

**Supersedes SPEC §4 (C1–C7).** Those were cut by connector convenience; these
are cut by removal boundary (D-029).

---

## Naming convention

```
L<leg><class><index>          leg-side connector
DP-<code>                     dash post, box side
```

| Class | Meaning       | Conductor         |
|-------|---------------|-------------------|
| **P** | Power, heavy  | 12 AWG, 25 A      |
| **M** | Power, medium | 14–16 AWG, 7–15 A |
| **S** | Signal        | 16 AWG, <1 A      |

## Why power and signal are split

Three independent reasons, all of which apply here:

1. **Terminal size.** A 12 AWG leg needs a size-12 contact; a signal needs
   size-16. Mixed housings exist but cost cavity efficiency and stock two
   crimp tools' worth of parts per connector.
2. **Noise.** The tach pickup and the ladder references share a bundle with pop-up
   motor legs if they share a housing. Separating the housing lets the bundles
   route apart.
3. **Service.** Unplugging the signal half to diagnose a switch shouldn't require
   breaking a 25 A motor circuit.

## Series selection

| Series          | Contact | Wire      | Amps  | Used for                         |
|-----------------|---------|-----------|-------|----------------------------------|
| **Deutsch DTP** | Size 12 | 10–12 AWG | 25 A  | All `P` connectors               |
| **Deutsch DT**  | Size 16 | 14–16 AWG | 13 A  | All `M` connectors               |
| **TE AMPSEAL**  | —       | 16–20 AWG | —     | High-count `S` connectors        |
| **Deutsch DT**  | Size 16 | 16 AWG    | —     | Low-count `S` connectors         |
| **Deutsch DTM** | Size 20 | 20–22 AWG | 7.5 A | Diagnostic and keypad drops only |

DTP is only made in 2-way and 4-way. Legs needing 6–8 heavy conductors take two
DTP housings, which is why L2 and L4 each have `P1` and `P2`.

---

## Master connector list

| Code      | Leg    | Class  | Housing (leg side) | Box side          | Cav | Used |
|-----------|--------|--------|--------------------|-------------------|-----|------|
| **L1-P**  | Engine | Power  | DTP06-4S           | DTP04-4P          | 4   | 4    |
| **L1-S**  | Engine | Signal | AMPSEAL 23 plug    | AMPSEAL 23 header | 23  | 16   |
| **L2-P1** | Front  | Power  | DTP06-4S           | DTP04-4P          | 4   | 4    |
| **L2-P2** | Front  | Power  | DTP06-4S           | DTP04-4P          | 4   | 4    |
| **L2-M**  | Front  | Medium | DT06-8S            | DT04-8P           | 8   | 7    |
| **L2-S**  | Front  | Signal | DT06-6S            | DT04-6P           | 6   | 4    |
| **L3-P**  | Dash   | Power  | DTP06-2S           | DTP04-2P          | 2   | 2    |
| **L3-M**  | Dash   | Medium | DT06-2S            | DT04-2P           | 2   | 2    |
| **L3-S**  | Dash   | Signal | AMPSEAL 35 plug    | AMPSEAL 35 header | 35  | 26   |
| **L4-P1** | Rear   | Power  | DTP06-4S           | DTP04-4P          | 4   | 3    |
| **L4-P2** | Rear   | Power  | DTP06-4S           | DTP04-4P          | 4   | 4    |
| **L4-M**  | Rear   | Medium | DT06-12S           | DT04-12P          | 12  | 10   |
| **L4-S**  | Rear   | Signal | DT06-6S            | DT04-6P           | 6   | 4    |

**13 leg connectors, 13 mating halves.**

## Dash post — the unified junction

Everything the legs plug into, plus what the box itself needs.

| Code                      | What                   | Type                | Notes                                   |
|---------------------------|------------------------|---------------------|-----------------------------------------|
| **DP-BAT**                | Main +12 V in          | M8 stud + ring lug  | 4 AWG from Class-T                      |
| **DP-GND**                | Ground bus             | Bus bar + ring lugs | Panel ground, pin 25 lands here         |
| **DP-PMU**                | PMU device connector   | Sicma 39-pos        | **Sealed once, never reopened** (D-004) |
| **DP-DIAG**               | Diagnostic / CAN1 port | DTM04-4P            | Glovebox. **120 Ω here + 120 Ω at PMU** |
| **DP-KEY**                | CAN keypad drop        | DTM04-4P            | CAN2 + power + ground                   |
| **DP-L1-P** … **DP-L4-S** | Leg receptacles ×13    | see table above     | Bracket-mounted on the panel edge       |

**Total at the dash post: 2 lugs, 1 device connector, 2 DTM drops, 13 leg
receptacles.**

## Housekeeping rules

- Every housing bought at **full cavity count**; unused positions get a capped
  wire, not a sealing plug (D-022).
- **Order 20% spare contacts** of every size. You will ruin some.
- Leg side is always the **socket** (`06-xS`), box side always the **pin**
  (`04-xP`). Consistent so a leg can never be plugged into the wrong half.
- Label both halves of every connector with its code before it leaves the bench.

---

## UPDATE 2026-08 — D-052, D-049

**L3-S is no longer an AMPSEAL 35.** Replaced by Deutsch DT-12s — cheaper, far
easier to source contacts for, and a connector failure takes out part of the dash
instead of all of it.

**But the arithmetic does not close.** L3-S carries 29 signals; two DT-12s give
24. Options, pending `[Q-030]`:

| Option                     | Cavities | Spare | Note                                      |
|----------------------------|----------|-------|-------------------------------------------|
| 3 × DT06-12S               | 36       | 7     | Most room, three housings to unplug       |
| 2 × DT06-12S + 1 × DT06-6S | 30       | 1     | Tight — violates the spare-capacity habit |
| 2 × DT06-12S + 1 × DT06-8S | 32       | 3     | Reasonable middle                         |

**Door branch must grow** (D-049). Remote mirror motors are staying, so the doors
need 8 motor conductors plus 2 heated-mirror feeds plus the door pin — 11
conductors, where the current L4 allocation assumes far fewer. Pending `[Q-031]`:
grow L4, or give the doors their own connector pair at the sill.

Giving the doors a sill connector is the cleaner answer and matches how the legs
were cut in the first place — it makes the door a serviceable sub-branch without
promoting it to a full leg.

### Revised connector count

| Leg       | Connectors                                | Change |
|-----------|-------------------------------------------|--------|
| L1 Engine | 2                                         | —      |
| L2 Front  | 4                                         | —      |
| L3 Dash   | 2 + **3 signal** = 5                      | was 3  |
| L4 Rear   | 4 (+2 at the sill if Q-031 goes that way) | was 4  |

**15 leg connectors**, up from 13. AMPSEAL is out of the BOM entirely — which
also closes `[V-043]` and `[V-046]`.

---

## UPDATE 2026-08 — final connector schedule

All Q-024/025/030/031 answered. This supersedes the counts above.

### Leg connectors

| Code      | Leg    | Class  | Housing (leg side) | Box side    | Cav | Used |
|-----------|--------|--------|--------------------|-------------|-----|------|
| **L1-P**  | Engine | Power  | DTP06-4S           | DTP04-4P    | 4   | 4    |
| **L1-S**  | Engine | Signal | DT06-12S ×2        | DT04-12P ×2 | 24  | 17   |
| **L2-P1** | Front  | Power  | DTP06-4S           | DTP04-4P    | 4   | 4    |
| **L2-P2** | Front  | Power  | DTP06-4S           | DTP04-4P    | 4   | 4    |
| **L2-M**  | Front  | Medium | DT06-8S            | DT04-8P     | 8   | 7    |
| **L2-S**  | Front  | Signal | DT06-6S            | DT04-6P     | 6   | 4    |
| **L3-P**  | Dash   | Power  | DTP06-2S           | DTP04-2P    | 2   | 2    |
| **L3-M**  | Dash   | Medium | DT06-2S            | DT04-2P     | 2   | 2    |
| **L3-S1** | Dash   | Signal | DT06-12S           | DT04-12P    | 12  | 12   |
| **L3-S2** | Dash   | Signal | DT06-12S           | DT04-12P    | 12  | 12   |
| **L3-S3** | Dash   | Signal | DT06-8S            | DT04-8P     | 8   | 5    |
| **L4-P**  | Rear   | Power  | DTP06-4S           | DTP04-4P    | 4   | 3    |
| **L4-M**  | Rear   | Medium | DT06-12S           | DT04-12P    | 12  | 10   |
| **L4-S**  | Rear   | Signal | DT06-8S            | DT04-8P     | 8   | 8    |

**14 leg connectors.** AMPSEAL is gone from the BOM entirely — everything is
Deutsch DT or DTP, which means **one crimper, two contact sizes, one supplier**.

### Sill sub-connectors — inside the L4 leg

| Code   | What           | Housing            | Cav   |
|--------|----------------|--------------------|-------|
| **D1** | Driver door    | DTP06-2S + DT06-6S | 2 + 6 |
| **D2** | Passenger door | DTP06-2S + DT06-6S | 2 + 6 |

See `sill-node.md`.

### What changed and why

| Change                            | Cause                                                    |
|-----------------------------------|----------------------------------------------------------|
| **L4-P2 deleted**                 | Window motor legs no longer cross the tunnel (D-065/066) |
| L4-P absorbs the window bus feed  | One 12 AWG into an existing spare                        |
| L4-M gains 4 window commands      | 16 AWG replacing 12 AWG power                            |
| L3-S split into three housings    | D-070 — 29 signals, 32 cavities                          |
| L1-S is now 2× DT-12, not AMPSEAL | Consistency — one connector family everywhere            |
| D1/D2 added at the sill           | D-068                                                    |

### Total housing count

| | Count |
|---|---|
| Leg connectors (pairs) | 14 |
| Door sub-connectors (pairs) | 4 |
| Dash post: lugs | 2 |
| Dash post: DTM drops | 2 |
| PMU device connector | 1 |
| **Total mated pairs** | **20** |

### Consolidation win

Dropping AMPSEAL means the entire car uses **Deutsch DT (size 16) and DTP
(size 12)** and nothing else. Two contact sizes, two crimp dies, one catalogue.
For a first harness that is worth more than the cavity efficiency AMPSEAL offered.

---

## VERIFIED 2026-08 — from the TE catalogue

`TS-ICT-T-C-CAT-2018.pdf` in `01-REFERENCE`. DT family pages 109–132.

### V-044 CONFIRMED — DTP is 2-way and 4-way only

The catalogue's DTP configurations list exactly two: `DTP0*-2*` (2 × size 12)
and `DTP0*-4*` (4 × size 12). The ordering table confirms it.

**There is no 6-way DTP.** L2 keeps two shells, `L2-P1` and `L2-P2`. That
question is closed.

### Wire sealing ranges — both our choices are in range

| Contact size | Series | Standard seal | Our wire |
|---|---|---|---|
| 20 | DTM | 14–22 AWG | 16 AWG diag/keypad drops — fine |
| **16** | **DT** | **14–20 AWG** | **16 AWG — comfortable** |
| **12** | **DTP** | **10–14 AWG** | **12 AWG — comfortable** |

**One tight spot:** D-092 puts the door window motor legs at 14 AWG in a
`DT06-08S`. Size 16 seals 14–20 AWG, so 14 AWG is **at the very top of the
range**. It fits, with no margin above.

### C015 modification — the fix if seals are loose

Reduced-diameter insert cavities, also called an "E" seal, for wire with thin
insulation. Available across DT and DTP as a `-C015` suffix.

**Buy standard first.** If 16 AWG GXL seals loosely on the bench, C015 is the
answer rather than switching wire.

---

## BOM GAP — secondary wedgelocks

**Wedgelocks are sold separately and are required on every DT-family connector.**
They were not in the connector BOM. Easy to miss, and a connector without one
will not retain contacts.

| Series | Plug wedgelock | Receptacle wedgelock |
|---|---|---|
| DT 2-way | W2S | W2P |
| DT 4-way | W4S | W4P |
| DT 6-way | W6S | W6P |
| DT 8-way | W8S | W8P |
| DT 12-way | W12S | W12P |
| **DTP 2-way** | **WP-2S** | **WP-2P** |
| **DTP 4-way** | **WP-4S** | **WP-4P** |
| DTM 4-way | WM-4S | WM-4P |

### Wedgelock count for this build

| Connector | Wedgelocks needed |
|---|---|
| L1-P (DTP-4) | WP-4S + WP-4P |
| L1-S ×2 (DT-12) | W12S ×2 + W12P ×2 |
| L2-P1, L2-P2 (DTP-4) | WP-4S ×2 + WP-4P ×2 |
| L2-M (DT-8) | W8S + W8P |
| L2-S (DT-6) | W6S + W6P |
| L3-P (DTP-2) | WP-2S + WP-2P |
| L3-M (DT-2) | W2S + W2P |
| L3-S1, S2 (DT-12) | W12S ×2 + W12P ×2 |
| L3-S3 (DT-8) | W8S + W8P |
| L4-P (DTP-4) | WP-4S + WP-4P |
| L4-M (DT-12) | W12S + W12P |
| L4-S (DT-8) | W8S + W8P |
| D1, D2 (DT-8) | W8S ×2 + W8P ×2 |
| DP-DIAG, DP-KEY (DTM-4) | WM-4S ×2 + WM-4P ×2 |
| DP-ICU (DT-12) | W12S + W12P |
| DP-DCU (DT-6) | W6S + W6P |

**Order 20% spare on every wedgelock too.** They are cheap and they break.

### Also available, worth considering

| Item | Why |
|---|---|
| **Boots** — DT2S-BT, DT4P-BT, DTP4S-BT etc. | Strain relief and a finished look at each housing |
| **Backshells** — 180° and 90°, with strain relief | For the tunnel and firewall runs where bend radius matters |
| **Dust caps** | For capped spares and the unmated diagnostic port |
| **Mounting clips** | Panel-mounting receptacles at the dash post. `1027-003-1200` fits DT 2/3/4/6/12 and all DTM/DTP |

The mounting clips matter — the dash post needs receptacles held to a plate, and
these are the intended way to do it.

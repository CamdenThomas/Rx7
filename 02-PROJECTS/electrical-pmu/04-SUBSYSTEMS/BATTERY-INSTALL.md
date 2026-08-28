# BATTERY & POWER BACKBONE — cargo bin install

Phase 3 of the build. **Factory harness untouched throughout** — the car is
better at the end of this weekend than it was at the start, and it drives home.

---

## 1 · The battery

**Ionic S9 (heated car-post version)** — `IC-12V40-S9` platform.

> **Naming note.** Ionic's own listings are inconsistent. The product is sold as
> **"Ionic Lithium 12V S9 — Car Post Starter Heater Battery"**, and some pages
> abbreviate the heated car variant as *S9H*. Both names refer to the same thing.
> **This project uses "S9" to match what Camden actually ordered.**
>
> The distinction that genuinely matters is **variant, not name**:
> the marine version has 3/8 threaded posts and **no heater**; the car version has
> **SAE automotive posts and the heater**. Camden's is heated, so it should have
> SAE posts — `[V-053]` confirm on arrival, because it decides which lugs to buy.

| Spec | Value |
|---|---|
| Capacity | 40 Ah |
| Cranking | <cite index="35-1">1,100 CCA / 1,400 peak CA</cite> |
| Group size | <cite index="35-1">Group 25</cite> |
| Weight | <cite index="35-1">14.6 lb</cite> |
| Terminals | <cite index="35-1">Standard automotive SAE posts</cite> |
| Heater | <cite index="35-1">Built-in, for cold-weather starts</cite> |
| Monitoring | Bluetooth, Ionic app — voltage, SoC, current, temperature |
| Reserve | 25% held back for emergency start |

Group 25 envelope is roughly **9.1 × 6.9 × 8.9 in (230 × 175 × 225 mm)**.
`[V-051]` measure the actual case before cutting anything.

**Why the heater matters here:** <cite index="43-1">Ionic batteries discharge down to −20 °F, but standard lithium must not be charged below 32 °F; the Heater models warm the cells so they can safely accept charge in freezing conditions.</cite>
In Fort Collins that is not a luxury — it is the reason this battery was the
right choice. It also means the heater draws power in winter, which belongs in
the sleeping-draw budget.

**14.6 lb replacing roughly 40 lb of lead**, moved from the nose to behind the
axle line. Small but real rearward weight shift on a car that wants it.

---

## 2 · Location

Cargo bin, behind the seats. Three constraints in order:

1. **Secured against real g-loading in every axis** — not just downward. A 15 lb
   mass that comes loose in a crash is a projectile, and the terminals are live.
2. **Serviceable** — you will want to reach the disconnect and the terminals.
3. **Short path to the rear ground stud**, and a clean tunnel run forward.

LiFePO4 does not outgas like lead-acid, so a sealed vented box is not required.
A **case is still wanted** for mechanical containment and to keep loose cargo off
the terminals.

---

## 3 · Parts to buy

### Mounting

| Item | Spec | ~$ |
|---|---|---|
| Battery tray / box, Group 24–27 | NOCO HM426 or equivalent | 30–60 |
| Hold-down frame | Billet clamp + J-hooks, or fabricated aluminum angle | 25–80 |
| Backing plate | 3–4 mm aluminum or steel, spreads load into the floor | 20–40 |
| Hardware | M8 / 5⁄16 grade 8, nyloc, large fender washers | 15 |

**Do not bolt through sheet metal alone.** A backing plate under the floor
turns a tearing load into a shear load.

### Protection & switching

| Item | Spec | ~$ |
|---|---|---|
| Class-T fuse block | Blue Sea 5504 or equivalent | 60–90 |
| Class-T fuse | 150 A, sized to the 4 AWG feed | 30–50 |
| Master disconnect | Blue Sea 9003e m-Series, or Longacre | 55–90 |
| MRBF terminal fuse + holder | For the starter feed, if fused | 35–60 |
| Distribution post | Blue Sea 2105 PowerPost, insulated | 25–40 |

**Class-T specifically, not ANL or MIDI.** LiFePO4 can deliver enormous
short-circuit current, and Class-T has the interrupt rating to actually break it.
This is the one fuse choice not to economise on.

### Cable & termination

| Item | Spec | ~$ |
|---|---|---|
| 4 AWG cable | ~25 ft, PMU feed + grounds | 60–90 |
| 1/0 or 2 AWG | Starter feed, length as measured | 40–80 |
| Lugs | Tinned copper, closed barrel, correct stud size | 30–50 |
| Adhesive heat shrink | 3:1, heavy wall | 20–35 |
| Terminal boots | Red/black, per lug | 10–15 |
| Grommets | Every pass-through | 15–25 |
| Abrasion loom | Full length of every heavy run | 25–40 |
| Ground studs | 3⁄8 stainless, star washers | 15 |
| Cavity wax | Seal every ground after torquing | 12 |

**Subtotal: roughly $520–830.**

---

## 4 · Power architecture at the battery

The starter and the PMU are **separate runs**. They do not share a fuse.

```
   BATTERY +
      │
      ├──── MRBF / unfused ──── 1/0 ──── STARTER solenoid
      │                                       (heavy, short, direct)
      │
      └──── MASTER DISCONNECT ──── CLASS-T 150 A ──── 4 AWG ──── DP-BAT
                                                                 (dash post)
   BATTERY −
      │
      └──── 4 AWG ──── REAR GROUND STUD ──── chassis
   
   ALTERNATOR B+ ──── back to the distribution post
```

**Why the split matters:** cranking pulls 300–500 A briefly. If that went through
the Class-T sized for the PMU feed, it would blow. The starter gets its own path
straight off the post.

**The disconnect goes in the PMU leg**, not the starter leg — so killing it
isolates the whole electrical system while the starter cable stays passive.

---

## 5 · Build sequence — Checklist 063–076

Woven with the wider build. Each step ends with the car still drivable.

| Step | Action | Note |
|---|---|---|
| 063 | Disconnect the factory battery | |
| **B1** | **Measure the cargo bin.** Confirm the Group 25 case fits with clearance for terminals, boots and the hold-down | New — `[T-024]` |
| **B2** | **Mock up in cardboard** before cutting or drilling | New |
| 064 | Fabricate and mount the tray + backing plate | |
| 065 | Mount the battery. Secure against g-loading in every axis | |
| 066 | Mount the master disconnect within reach | |
| 067 | Mount the Class-T holder **as close to battery positive as physically possible** | Unprotected cable between the post and the fuse is the one length that can never be protected |
| 068 | Cut and hydraulically crimp cables. Adhesive shrink and a boot on every lug | |
| 069 | Rear ground stud — grind to bare metal, star washer, torque, seal with cavity wax | |
| 070 | Run 4 AWG forward through the tunnel. Grommet every pass-through, loom the full length | |
| 071 | Terminate the forward end on a temporary insulated junction post | Becomes DP-BAT in Phase 4 |
| 072 | Install the front star ground node | |
| 073 | Reconnect the factory harness to the new feed and ground | |
| **B3** | **Pair the Ionic app.** Baseline voltage, SoC, temperature | New — this is your only battery instrumentation until the PMU is in |
| 074 | Start the car. Verify charging voltage at the battery | |
| 075 | Voltage-drop test while cranking — post to starter, and the ground return. Record both | Needs T-001 |
| 076 | **Drive it.** Should be identical to before, on an entirely new backbone | |

---

## 6 · How this feeds the rest of the build

| This phase produces | Used by |
|---|---|
| A live 4 AWG feed at the dash | Phase 4 — DP-BAT lands on it |
| The rear ground stud | L4 leg star node |
| The front star node | L2 leg star node |
| Cranking voltage-drop numbers | Validates A-009 (4 AWG adequate) |
| Ionic app baseline | Undervoltage/overvoltage warning thresholds, Checklist 058 |
| A proven tunnel route | L4 harness route measurement, T-008 |

**The tunnel is the thing to get right.** You will pull the L4 harness through the
same route later. Grommet generously, leave the loom oversized, and put a pull
string in beside the cable while it is open — it costs nothing now and saves
dropping the console again.

---

## 7 · Charging and storage

| Item | Note |
|---|---|
| Alternator charging | Fine as-is. The BMS manages acceptance |
| Bench charger | Ionic 12V 10A charges a 40 Ah in ~4–5 hrs |
| Trickle | Ionic 2A trickle is safe to leave connected; floats when full |
| **Storage before install** | Keep it above the BMS low-voltage cutoff. `[T-022]` |
| Cold charging | Heater handles it — but it needs the battery connected to work |

`[V-052]` Confirm the heater's trigger and draw. It may be autonomous off the
BMS, or it may want an enable signal. That changes whether it needs a PMU channel.

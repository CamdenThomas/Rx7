# BATTERY & POWER BACKBONE — cargo bin install

*Rev 2026-08-30 · owns: the battery, its mounting, the main feed and the Phase 3 procedure.*

Phase 3 of the build. **Factory harness untouched throughout** — the car is
better at the end of this weekend than it was at the start, and it drives home.

## Contents

1. The battery · 2. Location · 3. Parts to buy · 4. Power architecture ·
5. Build sequence · 6. How this feeds the rest of the build · 7. Charging and
storage

---

## 1 · The battery

**Ionic S9, heated car-post version** — `IC-12V40-S9` platform. **In hand**
(D-101; `T-002` done).

> **Naming note.** Ionic's own listings are inconsistent. The product is sold as
> "Ionic Lithium 12V S9 — Car Post Starter Heater Battery", and some pages
> abbreviate the heated car variant as *S9H*. Both names refer to the same
> thing. **This project uses "S9"** (D-002).
>
> The distinction that genuinely matters is **variant, not name**: the marine
> version has 3/8 threaded posts and **no heater**; the car version has SAE
> automotive posts and the heater. Camden's is heated, so it should have SAE
> posts — `V-053` / `T-029`: look at it before ordering lugs.

| Spec | Value |
|---|---|
| Capacity | 40 Ah |
| Cranking | 1,100 CCA / 1,400 peak CA |
| Group size | Group 25 |
| Weight | 14.6 lb |
| Terminals | Standard automotive SAE posts (to confirm, `V-053`) |
| Heater | Built-in, for cold-weather charging |
| Monitoring | Bluetooth, Ionic app — voltage, SoC, current, temperature |
| Reserve | 25 % held back for emergency start |

Group 25 envelope is roughly **9.1 × 6.9 × 8.9 in (230 × 175 × 225 mm)**.
`V-051` / `T-024`: measure the actual case before cutting anything.

**Why the heater matters here:** Ionic batteries discharge down to −20 °F, but
standard lithium must not be charged below 32 °F; the Heater models warm the
cells so they can safely accept charge in freezing conditions (D-060). In
Fort Collins that is not a luxury — it is the reason this battery was the right
choice. It also means the heater draws power in winter, which belongs in the
sleeping-draw budget (`V-052`).

**14.6 lb replacing roughly 40 lb of lead**, moved from the nose to behind the
axle line. Small but real rearward weight shift on a car that wants it.

## 2 · Location

Cargo bin, behind the seats. Three constraints in order:

1. **Secured against real g-loading in every axis** — not just downward. A 15 lb
   mass that comes loose in a crash is a projectile, and the terminals are live.
2. **Serviceable** — you will want to reach the disconnect and the terminals.
3. **Short path to the rear ground stud**, and a clean tunnel run forward.

LiFePO4 does not outgas like lead-acid, so a sealed vented box is not required.
A **case is still wanted** for mechanical containment and to keep loose cargo
off the terminals.

## 3 · Parts to buy

### Mounting

| Item | Spec | ~$ |
|---|---|---|
| Battery tray / box, Group 24–31 | **NOCO HM318BKS** (D-203e — the HM426 named earlier is a dual-6V box; fit check `V-093`) | 40–55 |
| Hold-down frame | Billet clamp + J-hooks, or fabricated aluminum angle | 25–80 |
| Backing plate | 3–4 mm aluminum or steel, spreads load into the floor (D-063) | 20–40 |
| Hardware | M8 / 5⁄16 grade 8, nyloc, large fender washers | 15 |

**Do not bolt through sheet metal alone.** A backing plate under the floor
turns a tearing load into a shear load.

### Protection & switching

| Item | Spec | ~$ |
|---|---|---|
| Class-T fuse block | **Blue Sea 5007100** — the 110–200 A block (D-203a; the 5502/5504 family starts at 225 A) | 70–95 |
| Class-T fuse ×2 (one spare) | **Blue Sea 5114**, 150 A — the PMU stud's maximum | 80–110 |
| Master disconnect | Blue Sea 9003e m-Series, or Longacre | 55–90 |
| MRBF terminal fuse + holder | For the starter feed, if fused | 35–60 |
| Distribution post | Blue Sea 2105 PowerPost, insulated | 25–40 |

**Class-T specifically, not ANL or MIDI** (D-062). LiFePO4 can deliver enormous
short-circuit current, and Class-T has the interrupt rating to actually break
it. This is the one fuse choice not to economise on.

### Cable & termination

| Item | Spec | ~$ |
|---|---|---|
| **2 AWG cable** | ~25 ft, PMU feed + grounds. Sized for the LS, not the 12A (D-091) | 80–130 |
| 1/0 or 2 AWG | Starter feed, length as measured | 40–80 |
| Lugs | Tinned copper, closed barrel, correct stud size | 30–50 |
| Adhesive heat shrink | 3:1, heavy wall | 20–35 |
| Terminal boots | Red/black, per lug | 10–15 |
| Grommets | Every pass-through | 15–25 |
| Abrasion loom | Full length of every heavy run | 25–40 |
| Ground studs | 3⁄8 stainless, star washers | 15 |
| Cavity wax | Seal every ground after torquing | 12 |

**Subtotal: roughly $540–880** ([`../05-PROCESS/BOM.md`](../05-PROCESS/BOM.md) owns the money).

## 4 · Power architecture at the battery

The starter and the PMU are **separate runs** (D-061). They do not share a fuse.

```
   BATTERY +
      │
      ├──── MRBF / unfused ──── 1/0 ──── STARTER solenoid
      │                                       (heavy, short, direct)
      │
      └──── MASTER DISCONNECT ──── CLASS-T 150 A ──── 2 AWG ──── DP-BAT
                                                                 (dash post)
   BATTERY −
      │
      └──── 2 AWG ──── REAR GROUND STUD ──── chassis

   ALTERNATOR B+ ──── back to the distribution post
```

**Why the split matters:** cranking pulls 300–500 A briefly. If that went
through the Class-T sized for the PMU feed, it would blow. The starter gets its
own path straight off the post.

**The disconnect goes in the PMU leg**, not the starter leg — so killing it
isolates the whole electrical system while the starter cable stays passive.

**Mount the Class-T as close to battery positive as physically possible** — the
cable between post and fuse is the one length that can never be protected.

## 5 · Build sequence — [`CHECKLIST.md`](CHECKLIST.md) Phase 3

Woven with the wider build. Each step ends with the car still drivable.

| Step | Action | Note |
|---|---|---|
| 3.1 | Disconnect the factory battery | |
| 3.2 | **Mock up in cardboard** before cutting or drilling. Confirm the Group 25 case fits with clearance for terminals, boots and the hold-down | `T-024`, `V-051` |
| 3.3 | Fabricate and mount the tray + backing plate | D-063 |
| 3.4 | Mount the battery. Secure against g-loading in every axis | |
| 3.5 | Mount the master disconnect within reach | |
| 3.6 | Mount the Class-T holder **as close to battery positive as physically possible** | |
| 3.7 | Cut and hydraulically crimp cables. Adhesive shrink and a boot on every lug | |
| 3.8 | Rear ground stud — grind to bare metal, star washer, torque, seal with cavity wax | |
| 3.9 | Run **2 AWG** forward through the tunnel | D-091 |
| 3.10 | **Put a pull string in beside it** | D-064 |
| 3.11 | Grommet every pass-through, loom the full length | |
| 3.12 | Terminate the forward end on a temporary insulated junction post | Becomes DP-BAT in Phase 4 |
| 3.13 | Install the front star ground node | |
| 3.14 | Reconnect the factory harness to the new feed and ground | |
| 3.15 | **Pair the Ionic app.** Baseline voltage, SoC, temperature | Your only battery instrumentation until the PMU is in |
| 3.16 | Start the car. Verify charging voltage at the battery | |
| 3.17 | Voltage-drop test while cranking — post to starter, and the ground return. Record both | Needs the meter (`T-001` done) |
| 3.18 | **Drive it.** Should be identical to before, on an entirely new backbone | |

## 6 · How this feeds the rest of the build

| This phase produces | Used by |
|---|---|
| A live 2 AWG feed at the dash | Phase 4 — DP-BAT lands on it |
| The rear ground stud | L4 leg star node |
| The front star node | L2 leg star node |
| Cranking voltage-drop numbers | Confirms the 2 AWG choice (D-091 closed `A-009`) |
| Ionic app baseline | Undervoltage/overvoltage warning thresholds, [`CHECKLIST.md`](CHECKLIST.md) 2.19 |
| A proven tunnel route | L4 harness route measurement, `T-008` |

**The tunnel is the thing to get right.** You will pull the L4 harness through
the same route later. Grommet generously, leave the loom oversized, and put a
pull string in beside the cable while it is open — it costs nothing now and
saves dropping the console again.

## 7 · Charging and storage

| Item | Note |
|---|---|
| Alternator charging | Fine as-is. The BMS manages acceptance |
| Bench charger | Ionic 12V 10A charges a 40 Ah in ~4–5 hrs |
| Trickle | Ionic 2A trickle is safe to leave connected; floats when full |
| **Storage before install** | Keep it above the BMS low-voltage cutoff. `T-022` |
| Cold charging | Heater handles it — but it needs the battery connected to work |

`V-052` — confirm the heater's trigger and draw. It may be autonomous off the
BMS, or it may want an enable signal. That changes whether it needs a PMU
channel.

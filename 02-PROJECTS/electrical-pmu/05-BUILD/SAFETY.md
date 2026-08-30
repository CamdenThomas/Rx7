# SAFETY

*Rev 2026-08-30 · owns: the hazards specific to this build. Read once, properly — these are the ways this project hurts people or burns cars.*

---

## Lithium — the one that's different from what you know

The Ionic S9 is LiFePO4. It behaves nothing like the lead-acid battery it
replaces.

**Short-circuit current is enormous.** A lead-acid battery sags under a dead
short. A lithium pack holds voltage and delivers everything it has. A dropped
spanner across the terminals doesn't spark — it welds, and the tool glows.

- **Class-T fuse, not ANL or MIDI.** It is the only common holder with the
  interrupt rating to actually break a lithium short. This is the one fuse not
  to economise on.
- **Mount it as close to battery positive as physically possible.** The cable
  between post and fuse can never be protected. Make it inches.
- **Cover terminals whenever the battery is in the car and you are working.**
  A rubber boot, or tape.
- **Remove rings and watches** before touching either terminal.

**Charging below freezing damages the cells.** The heater exists for this. It
needs the battery connected to work (`V-052`).

**Don't let it sit into BMS cutoff.** A deeply discharged pack can be difficult
or impossible to recover (`T-022`).

## 2 AWG and the tunnel run

The main feed is unprotected for its first few inches and carries the full
capability of the pack.

- **Disconnect the battery before working on the feed.** Every time.
- **Grommet every pass-through.** A 2 AWG cable chafing through a bulkhead
  against sheet metal is a fire, not a fault.
- **Loom the full length.** Not just where it looks vulnerable.
- Torque every lug and **re-torque after heat cycling** ([`CHECKLIST.md`](CHECKLIST.md) 8.7).

## Working under the car

The starter and its cable are under there, and so are you.

- **Jack stands, always.** Never a jack alone, never a floor jack plus optimism.
- Chock the wheels. It's an automatic — P is not a parking brake.
- **Battery disconnected** before anything near the starter or its cable.

## Fuel system

The Weber, the Carter pump, the tank sender and the future in-tank pump all sit
in this project's scope.

- **No sparks near the tank.** The fuel sender is inside it. Disconnect the
  battery before touching sender wiring.
- Depressurise before opening any line.
- A fire extinguisher within reach whenever fuel lines are open. **Not in the
  garage — within reach.**

## Pop-up headlights

- **Fingers out of the mechanism.** They move fast and don't care.
- **Battery disconnected** when working in the buckets.
- During bench testing, remember a stalled motor pulls 15–25 A and gets hot
  quickly. Two seconds is the limit ([`METER-SESSION.md`](METER-SESSION.md) Part 3.2).

## The meter session specifically

- **Engine running, moving parts nearby.** Belt, fan, pulleys. Sleeves rolled,
  nothing loose, hair tied.
- Exhaust — **ventilation or outside.** A rotary at idle in a closed garage is
  carbon monoxide.
- Hot exhaust, hot manifold. The engine bay is hot within a minute.
- **The clamp meter does not require breaking any circuit.** That is why it's the
  right tool — no probes into live connectors.

## Soldering and PCB work

- Ventilate. Flux fumes are genuinely unpleasant and cumulative.
- The Teensy boards run off USB while you develop. **Never connect a board to
  both USB and vehicle 12 V** without understanding the ground path.

## Things that will save you specifically

**Label the factory end of every migrated circuit** with `MIGRATED` and the date.
An unlabelled live wire taped back behind a dash is a future short.

**Never work on a cutover you can't finish before dark.** This is the build rule,
and it is also a safety rule — tired, rushing, in bad light, on a live system.

**The car drives home at the end of every session.** If it can't, you stopped in
the wrong place ([`MIGRATION-LOG.md`](MIGRATION-LOG.md) daily sign-off).

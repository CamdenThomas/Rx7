# Fault K-008 — blinker affecting fuel pump and tachometer

*Rev 2026-08-30 · owns: the trace of fault K-008 through the factory diagram. Conclusion: shared grounds X-13/X-15; not fixed in the factory harness (D-105), eliminated by the star-node architecture (D-017).*

> **NOT BEING FIXED — D-105.** This fault dies with the factory harness. It is a
> shared-ground problem in two body studs, and the new architecture gives every
> zone a local star node with no ground crossing a bulkhead (D-017). There is no
> mechanism for it to transfer.
>
> **This file is kept as reference, not as a work item.** It explains *why* the
> ground architecture is the way it is, and it is a worked example of reading the
> factory diagram. Do not spend shop time on it.

**Decoded from the factory diagram. This is a shared-ground fault, and the
diagram shows exactly where.**

---

## What the diagram says

| Circuit                               | Feed                      | Fuse | Ground point                              |
|---------------------------------------|---------------------------|------|-------------------------------------------|
| Turn signals                          | IG → BY → GY bus          | 10 A | Front lamps **X-13**, rear lamps **X-15** |
| Control Processing Unit (flasher)     | GW / GB from combo switch | —    | **X-13**                                  |
| Instrument panel incl. **tachometer** | IG → BY → GY bus          | 10 A | **X-13**                                  |
| **Fuel pump**                         | IG → BW → BLg             | 10 A | **X-15**                                  |
| Emission control unit                 | various                   | —    | **X-13**                                  |

## The mechanism

Two separate shared returns, and the blinker sits on both:

**X-13** carries the flasher's own ground, the instrument panel ground (tach
included), and the emission control unit ground. Every flash pulses ~4.5 A
through X-13. If that stud is corroded, each pulse lifts the local ground by a
few hundred millivolts — and the tach, which reads a low-level coil signal
referenced to that same ground, moves with it.

**X-15** carries the rear turn lamp grounds *and* the fuel pump ground. Same
mechanism, different stud: blinker current modulates the fuel pump's ground
reference.

The tach and fuel pump are not electrically related to each other. They're
related to the blinker through **ground**, which is why the symptom looks
mysterious and why chasing feed wires would waste your time.

## Also worth knowing

Turn signals and the instrument panel are both fed from the **GY** bus, which
originates at the same ignition switch IG terminal through two 10 A fuses. Even
with perfect grounds, a marginal IG contact in a 44-year-old ignition switch
would produce the same symptom on the supply side.

## Diagnosis order (T-016) — CANCELLED, kept for reference

> **Not being done.** Left here only so the method is on record if a similar
> symptom ever appears on the new harness.

1. **Voltage-drop test X-13 and X-15** with the blinker running. Meter from the
   stud to a known-good chassis point. Anything above ~0.1 V under load is your
   fault. Do this first — it is a five-minute test.
2. If the studs are clean, drop-test the **IG feed** at the ignition switch
   under blinker load.
3. Only then look for a PO splice (K-002) or a chafe.

## Why the rebuild fixes it permanently — and why that's enough

D-017 forbids grounds from crossing a bulkhead and gives every zone a local star
node. The rear lamps and the fuel pump ground at the rear star node on separate,
correctly-sized returns — not a shared 44-year-old body stud. The flasher
disappears entirely (D-013), so its ground current never exists.

**The fault has no path into the new harness.** Every conductor, every ground and
every connector is new. The old harness comes out intact and goes in the bin.

## Observed behaviour, 2026-08

The fuel pump changes note with the blinker; **engine running does not change.**
That is consistent with the ground-modulation theory and it bounds the severity:
the pump is seeing voltage ripple, but not enough to pull delivery below the
regulator setpoint. Nothing downstream of the regulator notices.

## The one narrow case where something could carry over

The fault dies with the harness — but **components being reused** don't.

| Reused item | Covered by |
|---|---|
| Ignition switch — a marginal IG contact would produce the same symptom on the supply side, and the switch becomes the A16 ladder input | **T-023** already continuity-tests which outputs stay live in RUN and START |
| Senders, motors, switches with PO splices at the device end | **T-019** already logs every PO splice |

Both are already on the task list for other reasons. No extra work is needed.

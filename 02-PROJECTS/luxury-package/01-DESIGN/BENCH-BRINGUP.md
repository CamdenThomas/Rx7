# BENCH BRING-UP — firmware development sequence

*Rev 2026-08-31 · owns: the firmware bring-up stages and what each one proved.*

**In hand:** 3 × Teensy 4.1 · 5 × SN65HVD230 transceivers · **PMU-24 DL** ·
one micro-USB cable (D-140). Still to buy: [`../04-BUILD/BENCH-KIT.md`](../04-BUILD/BENCH-KIT.md).

**Stages 1–5 complete.** The entire CAN software stack is proven and the
Stage 4–5 rigs have been absorbed into the ICU firmware, which the 415-assertion
regression suite (`firmware/tests/`) now covers. Stages 6–7 wait on a microSD
card.

## Contents

Before you plug anything in · Stages 1–7 · Now that the transceivers are here
· The PMU and V-065 · What is genuinely blocked · Next sessions

---

## Before you plug anything in

> **The Teensy 4.1 is 3.3 V only. It is NOT 5 V tolerant.**
> Putting 5 V on any GPIO kills the pin, often the chip. Every sensor input in
> this project needs a divider or a clamp before it touches a Teensy — that's
> why [`DCU-CLUSTER.md`](DCU-CLUSTER.md) specifies dividers and clamp diodes on all six ICU
> sensor inputs.
>
> On the bench, drive inputs from **3.3 V, never the 5 V rail.**

**One cable, one board at a time.** For two boards running simultaneously you
need a second cable or a powered hub. Do not try to power a second Teensy from
the first's 3.3 V pin — the regulator won't like it and you'll chase phantom
faults for an hour.

---

## Stage 1 · Toolchain — 30 minutes

- [x] Install **Arduino IDE 2.x**
- [x] Install **Teensyduino** — the add-on, not a separate IDE
- [x] Select board: Teensy 4.1. Set CPU to 600 MHz
- [x] Blink sketch to the onboard LED
- [ ] **Repeat on boards 2 and 3** (`T-048`). Verify each one before it becomes precious

**Label the boards physically.** `ICU`, `DCU`, `SPARE`. You will otherwise flash
the wrong one at 2 a.m.

## Stage 2 · Prove `can_map.h` ✅ **DONE 2026-08 — all checks passed**

Run by `firmware/can_map_test/can_map_test.ino`.

- [x] Compile it into a sketch
- [x] `static_assert(sizeof(...) == 8)` on every payload struct — **fires at
      compile time.** If it built, packing is correct
- [x] Round-trip: populate a struct, `memcpy` to `uint8_t[8]`, copy back, compare
- [x] Temperature encode/decode across the real range
- [x] `can_counter_advanced()` across the 255→0 wrap

### What each one proved

**Round-trip** — compilers insert invisible **padding** to align struct fields.
A struct you think is 8 bytes can silently be 12. `__attribute__((packed))`
prevents it; the `static_assert` proves it. The runtime half walks a message
through the exact journey CAN puts it through.

**Temperature** — the original design stored `c + 40` so a signed range fit in
unsigned bytes. **Removed.** `int8_t` covers −128 to +127 °C, every temperature
this car will see. The offset added arithmetic and a bug class for nothing.
*(The old line testing 215 °C only made sense with the offset — stale.)*

**Counter wrap** — the one that matters. Byte counters are unsigned; 255 + 1 = 0.
The naive check `now > prev` works 255 times out of 256, then declares a healthy
sender dead — at 20 Hz, a false fault every 13 seconds. The fix is
`(uint8_t)(now - prev) != 0`: unsigned subtraction wraps the same way the counter
does, so the wrap cancels itself out.

### A bug was found by doing this

The original `TEMP_ENCODE` / `TEMP_DECODE` macros were self-cancelling —
`((c)+40)-40` and `(int)(b)` — with a comment claiming an offset that wasn't
happening. Silently self-consistent, so it would have worked right up until
someone trusted the comment.

> **This is why Stage 2 exists.** A header nobody compiled is not a
> specification, it's a hope.

## Stage 3 · CAN internal loopback ✅ **DONE — all checks passed, 5 frames, 0 failures**

Sketch: `firmware/can_loopback_test/can_loopback_test.ino`

**Use ACAN_T4, not FlexCAN_T4.** ACAN_T4 exposes `mLoopBackMode` and
`mSelfReceptionMode`, which let a single chip test itself with no additional
hardware. FlexCAN_T4 doesn't expose loopback cleanly.

> **Why loopback is essential, not just convenient:** a real CAN node needs
> *another node* to acknowledge every frame. One Teensy alone on a bus
> transmits, gets no ACK, and retries forever. Loopback disables the ACK
> requirement so the controller can hear itself.

- [x] Library Manager → install **ACAN_T4** (Pierre Molinaro)
- [x] Copy `can_map.h` into the sketch folder
- [x] Upload, Serial Monitor at 115200
- [x] CAN1 starts — error code 0
- [x] Three message types round-trip, **payloads byte-identical**
- [x] Dispatch switch routed all three correctly
- [x] Decoded back: 6500 rpm · 92 °C water · 110 °C oil · 4.35 bar · 137 kph
- [x] Timeout detected after 350 ms silence

### What is now proven

**The entire CAN software stack.** Bring-up, bit rate, transmit, receive, ID
dispatch, payload integrity through the controller, struct encode/decode, and
timeout detection.

**Transceivers replace loopback with a wire. None of this gets rewritten.**
Tomorrow is debugging hardware against known-good software rather than both at
once — the difference between an hour and an evening.

### If it fails

| Symptom | Cause |
|---|---|
| `CAN1 FAILED to start` | ACAN_T4 not installed, or wrong board selected |
| Compiles but no frames return | `mSelfReceptionMode` not set — the chip sends but ignores itself |
| Payload mismatch | Go back to Stage 2. Something in `can_map.h` regressed |

## Stage 4 · Ladder decode ✅ **DONE — absorbed into the ICU firmware**

Sketch: `firmware/ladder_decode_test/` — kept as an isolated test rig.

Ran a full self-test with **no hardware at all** — synthetic ADC values against
every ladder in [`../01-DESIGN/LADDERS.md`](../01-DESIGN/LADDERS.md), including the fault bands.

- [x] Upload, Serial Monitor at 115200, all decode checks pass
- [x] Fault bands proven with a jumper on A0 to 3.3 V and GND
- [ ] Optional: sweep a 10 kΩ pot between 3.3 V and GND to watch every state appear with FAULT between them

**3.3 V only. The Teensy 4.1 is not 5 V tolerant.**

**Windows, not thresholds.** A reading between states reports FAULT rather than
snapping to the nearest — that is the design, not a bug.

> Ladder *verification against real resistors* now happens in the car during
> Phase 6, when the switches are genuinely wired (D-142). This stage proves the
> **decode logic**, which is the part that lives in firmware.

## Stage 5 · Tach measurement ✅ **DONE — absorbed into the ICU firmware**

Sketch: `firmware/tach_simulator/` — **kept, and still the fastest way to feed
an RPM signal to a board with one jumper wire.**

The same Teensy generates a simulated tach signal on **pin 3** and measures it on
**pin 4**. Jumper the two.

- [x] Jumper pin 3 → pin 4
- [x] Upload, Serial Monitor at 115200
- [x] Sweep 500–8000 rpm, measured tracks generated within 3 %
- [x] Step changes track
- [x] **Zero rpm reads 0**, not the last value

**No second board needed.** A single Teensy does both halves — which also means
it works with the one USB cable you have.

You end up with a validated RPM measurement path **and** a permanent signal
source for display work later.

> `V-067` — the sketch assumes **2 pulses per eccentric shaft revolution** for a
> 2-rotor fed from the leading coil. **Confirm against the real car.** Wrong, and
> every RPM reading is scaled by a constant — the gauge looks plausible and is
> simply wrong.

> Same technique covers **VSS** — a second frequency channel is the same code.

## Stage 6 · SD card — config-as-data

The 4.1 has a microSD slot, and [`DCU-CLUSTER.md`](DCU-CLUSTER.md) §5 specifies layout and
thresholds as a config file rather than code. This stage also unlocks
persistence for `stats.h` (D-162, F-007).

- [ ] `SD.begin(BUILTIN_SDCARD)`, list files
- [ ] Write a JSON or INI config, read and parse it
- [ ] **Build the safe-mode path**: config missing → hardcoded defaults, no crash
- [ ] Test with a deliberately corrupt file. **It must still boot**

A cluster that won't start because of a typo in a config file is worse than no
cluster.

## Stage 7 · Datalogging skeleton

- [ ] Timestamped CSV append to SD
- [ ] Test write throughput at your intended log rate
- [ ] Test **power-loss behaviour** — pull USB mid-write, confirm the card
      survives and the file is readable

---

## Now that the transceivers are here

| Step | Needs |
|---|---|
| Two Teensys on a real CAN bus | 2 transceivers, twisted pair, **2 × 120 Ω** (not yet bought) |
| Spare board simulates PMU messages 0x100–0x130 | The third board earns its keep |
| Second board consumes them as the ICU would | |
| Three-node bus once the PMU joins | 3rd transceiver |

**The spare Teensy is your PMU simulator** until the real one is configured,
which lets ICU display work proceed without touching the PMU at all.

> **Solder the header pins onto the SN65HVD230 modules first.** They ship
> unsoldered.
>
> **Blocked on one item:** 120 Ω resistors — not in hand (D-140). See
> [`../04-BUILD/BENCH-KIT.md`](../04-BUILD/BENCH-KIT.md).

## The PMU and `V-065`

**`V-065`:** read the PMU's actual CAN export format out of the client.
ECUMaster fixes that structure — messages 0x100–0x130 in `can_map.h` are
**intent** and must be reconciled against reality before anything depends on
them. Since D-194 dropped the separate bench phase, this happens at
Checklist 2.5 — the PMU powered in the car, laptop on DP-DIAG.

---

## What is genuinely blocked

| Blocked on | What |
|---|---|
| 120 Ω resistors | Real CAN between boards |
| Panel choice `Q-060` → D-193 | The three `pushDirtyTiles()` calls — everything else renders in the simulator today |
| microSD card | Stage 6, config-as-data, `stats.h` persistence |
| `V-065` | Reconciling `can_map.h` 0x100–0x130 against the PMU's real export |
| The car | Every real sensor value, and `V-067` pulses per rev |

---

## Next sessions

| Session | Do | Needs | Hours |
|---|---|---|---|
| ~~1–2~~ | ~~Stages 1–5~~ | — | **DONE** |
| **Next** | Flash and label boards 2 and 3 (`T-048`) | Nothing | 0.5 |
| Then | Real CAN between two boards, PMU simulator live | 120 Ω ×4, headers soldered | 2–3 |
| Then | PMU first power-up, `V-065` CAN export | 5 A fuse, flying leads | 3–4 |
| Then | Stages 6–7, SD config, logging, `stats.h` persistence | microSD card | 4–6 |
| Parallel | DCU firmware skeleton (F-001), conditioning schematics (F-003/F-004) | Nothing | see [`../05-PROCESS/FORWARD-WORK.md`](../05-PROCESS/FORWARD-WORK.md) |

Everything after `T-048` waits on about $10 of parts. By the end of those you
have a validated CAN stack, a live two-node bus, a config system and
persistent trip stats — **with no car, no wiring and no PMU dependency.**

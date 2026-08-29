# BENCH BRING-UP — what you can do tonight

*Rev 2026-08 · owns: firmware development sequence before the car exists*

**You have:** 3 × Teensy 4.1, one micro-USB cable.
**Tomorrow:** transceivers, PMU.

**More is possible tonight than you'd think.** The transceivers gate
*Teensy-to-Teensy CAN*, not CAN development.

---

## Before you plug anything in

> **The Teensy 4.1 is 3.3 V only. It is NOT 5 V tolerant.**
> Putting 5 V on any GPIO kills the pin, often the chip. Every sensor input in
> this project needs a divider or a clamp before it touches a Teensy — that's
> why `DCU-CLUSTER.md` specifies dividers and clamp diodes on all six ICU
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
- [ ] **Repeat on all three boards.** Verify each one before it becomes precious

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

## Stage 4 · Sensor scaling — a potentiometer is enough

- [ ] Wire a pot between **3.3 V and GND**, wiper to an analog pin
- [ ] Read `analogRead()`, confirm 0–1023 at 10-bit
- [ ] Switch to `analogReadResolution(12)`, confirm 0–4095
- [ ] Implement a **ladder decode lookup** from `01-DESIGN/LADDERS.md` — windows,
      not thresholds, with a FAULT band outside them
- [ ] Sweep the pot and confirm every state reports correctly, and that between
      states it reports FAULT rather than snapping to the nearest

**This validates the A1–A8 decode logic** before a single resistor is soldered.

## Stage 5 · The tach simulator — two boards, no car

This is the one worth doing properly.

- [ ] **Board A** generates a square wave on a PWM pin at a known frequency,
      swept 300–8000 rpm equivalent
- [ ] **Board B** captures it on a hardware timer input-capture pin
- [ ] Compute RPM, compare against what A is generating
- [ ] Test the edges: **zero rpm**, sudden step changes, noise between pulses

**Cross-connect with a single jumper and a common ground.** Both boards are
3.3 V so no level shifting.

You now have a validated RPM measurement path, and a permanent test rig for
firmware regressions later.

> Do the same trick for **VSS** — a second frequency channel is the same code.

## Stage 6 · SD card — config-as-data

The 4.1 has a microSD slot, and `DCU-CLUSTER.md` §15 specifies layout and
thresholds as a config file rather than code.

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

## Tomorrow, when the transceivers arrive

| Step | Needs |
|---|---|
| Two Teensys on a real CAN bus | 2 transceivers, twisted pair, **2 × 120 Ω** |
| Board A simulates PMU messages 0x100–0x130 | The spare board earns its keep |
| Board B consumes them as the ICU would | |
| Three-node bus once the PMU joins | 3rd transceiver |

**The spare Teensy is your PMU simulator** until the real one is configured. That
lets ICU display work proceed without touching the PMU at all.

## When the PMU arrives

**`V-065` is the first job:** read the PMU's actual CAN export format out of the
client. ECUMaster fixes that structure — messages 0x100–0x130 in `can_map.h` are
*intent* and must be reconciled against reality before anything depends on them.

---

## What is genuinely blocked

| Blocked on | What |
|---|---|
| Transceivers | Real CAN between boards |
| PMU | `V-065`, real PMU messages, soft-fuse behaviour |
| Display choice `[Q-037]` | Any rendering work |
| The car | Every real sensor value |

**Everything else on this page can start tonight.**

---

## Suggested order for the first three sessions

| Session | Do | Hours |
|---|---|---|
| **Tonight** | Stages 1–3. Toolchain, `can_map.h` validation, CAN loopback | 3–4 |
| **Tomorrow** | Stage 4–5, then real CAN once transceivers land | 4–5 |
| **Next** | Stage 6–7, PMU simulator on the spare board | 4–6 |

By the end of those you have a validated CAN stack, working sensor decode, a
tested RPM path and a config system — **with no car, no wiring and no PMU
dependency.**

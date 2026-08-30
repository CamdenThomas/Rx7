# CAN MESSAGE MAP

*Rev 2026-08-30 · owns: the CAN2 message IDs, byte layouts, rates and timeout behaviour. `firmware/icu/can_map.h` is the machine-readable copy; when this file changes, that header and both firmware versions bump together.*

**Bus:** CAN2 · 500 kbps · CAN 2.0B · 11-bit identifiers (D-086). The PMU is
CAN 2.0 only, so the shared bus cannot be FD regardless of what the Teensys
can do. **Priority:** lower ID = higher priority — safety and state first,
telemetry last.

**Status:** the ICU, DCU and keypad messages (0x200–0x400) are **final**
(D-106). The PMU messages (0x100–0x130) are **intent** until `V-065` — the
PMU's own export format is fixed by ECUMaster, not by us, and must be read out
of the client before anything depends on it.

## Contents

1. Nodes · 2. Message layouts · 3. Timeout behaviour · 4. Bus load ·
5. Design rules · 6. Before you code

---

## 1 · Nodes

| Node | Sends | Receives | Termination |
|---|---|---|---|
| PMU-24 DL | 0x100–0x13F | keypad, DCU requests | **Software, at the dash end** |
| CAN keypad | 0x400 | backlight state | — |
| ICU | 0x200–0x21F | everything | — |
| DCU | 0x300–0x31F | ICU sensors, keypad | — |
| LS ECU (future) | 0x500+ | — | **Physical 120 Ω at the engine-bay drop** (D-079) |

## 2 · Message layouts

All messages **8 bytes, little-endian**, standard 11-bit ID. **Byte 7 of every
message is a rolling counter**, incrementing 0–255, so a receiver can detect a
stalled sender instead of showing stale data as live. Counter comparison is
`(uint8_t)(now - prev) != 0` — unsigned subtraction wraps the same way the
counter does ([`BENCH-BRINGUP.md`](BENCH-BRINGUP.md) Stage 2).

### 0x100 · PMU → all · Vehicle state · 20 Hz

| Byte | Field | Encoding |
|---|---|---|
| 0 | Key position | 0 OFF · 1 ACC · 2 RUN · 3 START |
| 1 | Wake source | bitfield: b0 ACC, b1 RUN, b2 hazard, b3 door, b4 horn, b5 latch |
| 2 | Global fault | bitfield: b0 any soft-fuse trip, b1 undervolt, b2 overvolt, b3 overtemp |
| 3 | Headlight state | 0 OFF · 1 PARK · 2 HEAD |
| 4 | Turn state | 0 off · 1 left · 2 right · 3 hazard |
| 5 | Pop-up state | 0 down · 1 raising · 2 up · 3 lowering · 4 fault |
| 6 | reserved | |
| 7 | counter | |

### 0x110 · PMU → all · Power · 10 Hz

| Byte | Field | Encoding |
|---|---|---|
| 0–1 | Battery voltage | uint16, mV |
| 2–3 | Total current | uint16, 0.1 A |
| 4 | Alternator charging | 0 no · 1 yes |
| 5–6 | reserved | |
| 7 | counter | |

### 0x120 · PMU → all · Outputs · 5 Hz

| Byte | Field | Encoding |
|---|---|---|
| 0–1 | Fuel level | uint16, 0.1 % |
| 2–4 | Output on/off | 24 bits, one per channel O1–O24 |
| 5 | Trip state — channel index | 0–23, cycling |
| 6 | Trip state — that channel's status | 0 ok · 1 tripped · 2 retrying |
| 7 | counter | |

Trip flags need 24 bits but only 16 remained, so they are multiplexed: byte 5
= channel index, byte 6 = status. All 24 cycle in ~5 s at 5 Hz. Faults latch
until cleared, so a slow cycle is fine.

### 0x130 · PMU → all · Per-channel current · 5 Hz, multiplexed

| Byte | Field | Encoding |
|---|---|---|
| 0 | Channel index | 0–23 = O1–O24 |
| 1–2 | Measured current | uint16, 0.01 A |
| 3–4 | Soft-fuse setpoint | uint16, 0.01 A |
| 5 | Channel status | 0 off · 1 on · 2 tripped · 3 retrying |
| 6 | reserved | |
| 7 | counter | |

### 0x200 · ICU → all · Engine sensors · 20 Hz

**The ICU's own inputs.** This is the message that must not depend on
anything. Stored metric (D-152); the display converts.

| Byte | Field | Encoding |
|---|---|---|
| 0–1 | RPM | uint16, 1 rpm |
| 2 | Water temp | int8, °C |
| 3 | Oil temp | int8, °C |
| 4–5 | Oil pressure | uint16, 0.01 bar |
| 6 | Road speed | uint8, km/h |
| 7 | counter | |

The −40 offset in the first draft was removed — `int8_t` covers every
temperature this car will see, and the offset was a bug class for nothing
(Stage 2 found the macros self-cancelling).

### 0x210 · ICU → all · Sensor health · 2 Hz

| Byte | Field | Encoding |
|---|---|---|
| 0 | Sensor valid | bitfield: b0 RPM, b1 water, b2 oil temp, b3 oil press, b4 VSS |
| 1 | Sensor fault type | bitfield: b0 open, b1 short, b2 out of range, b3 implausible |
| 2 | CAN health | b0 PMU seen, b1 DCU seen, b2 keypad seen |
| 3–6 | reserved | |
| 7 | counter | |

### 0x300 · DCU → all · Climate · 5 Hz

| Byte | Field | Encoding |
|---|---|---|
| 0 | Mode | 0 off · 1 vent · 2 heat · 3 defrost · 4 A/C |
| 1 | Blower speed | 0–3 |
| 2 | Target temp | uint8, °C |
| 3 | Cabin temp | int8, °C |
| 4 | A/C request | 0 no · 1 yes |
| 5–6 | reserved | |
| 7 | counter | |

### 0x310 · DCU → all · Comfort bus · 2 Hz

| Byte | Field | Encoding |
|---|---|---|
| 0 | Seat heat | b0–1 driver level, b2–3 passenger level |
| 1 | Seat cool | b0–1 driver, b2–3 passenger |
| 2 | Mirror heat | b0 on |
| 3 | Nozzle heat / de-icer | b0 nozzles, b1 park de-icer |
| 4–5 | Comfort bus current | uint16, 0.01 A |
| 6 | reserved | |
| 7 | counter | |

### 0x320 · DCU → all · Radar · on change

| Byte | Field | Encoding |
|---|---|---|
| 0 | Alert level | 0 none · 1–5 |
| 1 | Band | bitfield: b0 X, b1 K, b2 Ka, b3 laser |
| 2 | Direction | 0 unknown · 1 front · 2 rear |
| 3–6 | reserved | |
| 7 | counter | |

### 0x400 · Keypad → all · Buttons · on change

| Byte | Field |
|---|---|
| 0 | Button states, bitfield, 8 keys |
| 1 | Button held ≥ 1 s, bitfield |
| 2–6 | reserved |
| 7 | counter |

## 3 · Timeout behaviour — define it once, obey it everywhere

| Message | Timeout | Receiver shows |
|---|---|---|
| 0x100 | 250 ms | Assume key OFF, warn |
| 0x110 | 500 ms | Blank voltage field, not last value |
| 0x120 / 0x130 | 1 s | Blank, not last value |
| 0x200 | 250 ms | **ICU only — this is its own message** |
| 0x300 / 0x310 | 2 s | Climate display shows "—" |
| 0x400 | none | Buttons are event-driven |

**A gauge frozen at its last value is worse than a gauge showing a fault.**
Blank or dash it, never hold. The ICU renders a stale CAN value as dim green
dashes, distinct from a hardware fault (D-153).

## 4 · Bus load

| ID | Bytes | Hz | bits/s |
|---|---|---|---|
| 0x100 | 8 | 20 | ~2,240 |
| 0x110 | 8 | 10 | ~1,120 |
| 0x120 | 8 | 5 | ~560 |
| 0x130 | 8 | 5 | ~560 |
| 0x200 | 8 | 20 | ~2,240 |
| 0x210 | 8 | 2 | ~224 |
| 0x300 | 8 | 5 | ~560 |
| 0x310 | 8 | 2 | ~224 |
| **Total** | | | **~7.7 kbit/s** |

Against 500 kbit/s that is roughly 1.5 % bus load. Enormous headroom, even
before the LS ECU joins. No reason to raise the bit rate or trim rates.

## 5 · Design rules

**Single source of truth per signal** (D-078). If the PMU measures it, the ICU
reads it from CAN — fuel level, battery voltage, key state, channel currents.
Never fit a second sender for something already measured.

**The ICU's critical gauges do not depend on this bus** (D-083). RPM, water
temp, oil pressure, oil temp and speed are all on ICU-local inputs. If CAN2
fails entirely, only fuel level and battery voltage go blank.

**Every message carries a rolling counter.** **Timeout behaviour is explicit.**

## 6 · Before you code against the PMU messages

- [ ] `V-065` — export the PMU CAN stream definition from the client
      (`CHECKLIST.md` 2.5)
- [ ] Reconcile 0x100–0x130 against it; update `can_map.h` and this file
      together
- [ ] Tag the header. When it changes, both firmware versions bump together

Stages 2 and 3 of [`BENCH-BRINGUP.md`](BENCH-BRINGUP.md) already proved packing, round-trip,
counter wrap and dispatch for every layout above.

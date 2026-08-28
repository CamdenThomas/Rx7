# CAN MESSAGE MAP

*Draft. Finalise before firmware starts — `[Q-041]`.*

**Bus:** CAN2 · 500 kbps · CAN 2.0B · 11-bit identifiers.
The PMU is CAN 2.0 only, so the shared bus cannot be FD regardless of what the
Teensys can do.

**Priority:** lower ID = higher priority. Safety and state first, telemetry last.

---

## Nodes

| Node | Sends | Receives | Termination |
|---|---|---|---|
| PMU-24 DL | 0x100–0x13F | keypad, DCU requests | **Software, at the dash end** |
| CAN keypad | 0x400 | backlight state | — |
| ICU | 0x200–0x21F | everything | — |
| DCU | 0x300–0x31F | ICU sensors, keypad | — |
| LS ECU (future) | 0x500+ | — | **Physical 120 Ω at the engine-bay drop** |

---

## Messages

### From the PMU

| ID | Contents | Rate |
|---|---|---|
| `0x100` | Key state, wake state, global fault flag | 20 Hz |
| `0x110` | Battery voltage, total current | 10 Hz |
| `0x120` | Fuel level, output on/off states | 5 Hz |
| `0x130` | Per-channel current, multiplexed | 5 Hz |

### From the ICU

| ID | Contents | Rate |
|---|---|---|
| `0x200` | RPM, water temp, oil pressure, oil temp, road speed | 20 Hz |
| `0x210` | Sensor fault flags — open circuit, out of range, implausible | 2 Hz |

### From the DCU

| ID | Contents | Rate |
|---|---|---|
| `0x300` | Climate state, blower request, A/C request | 5 Hz |
| `0x310` | Comfort bus states — seat heat, seat cool, mirrors, nozzles, de-icer | 2 Hz |
| `0x320` | Radar subsystem state and alerts | on change |

### From the keypad

| ID | Contents | Rate |
|---|---|---|
| `0x400` | Button states, bitfield | on change |

---

## Design rules

**Single source of truth per signal.** If the PMU measures it, the ICU reads it
from CAN — fuel level, battery voltage, key state, channel currents. Never fit a
second sender for something already measured (D-078).

**The ICU's critical gauges do not depend on this bus.** RPM, water temp, oil
pressure, oil temp and speed are all on ICU-local inputs. If CAN2 fails entirely,
only fuel level and battery voltage go blank (D-083).

**Every message carries a rolling counter**, so a receiver can detect a stalled
sender rather than displaying stale data as though it were live.

**Timeout behaviour must be explicit.** Define, per message, what the receiver
shows when it hasn't arrived in N cycles. A gauge frozen at its last value is
worse than a gauge showing a fault.

---

## The private link

A second twisted pair runs DCU ↔ ICU, **capped at both ends** (D-087). Both
Teensys have spare CAN controllers and one supports CAN-FD.

Not used yet. It exists so climate state, diagnostics or display handoff can move
off the vehicle bus later without touching either board. Two conductors inside
the dash — cheap now, impossible later.

---

## Before firmware starts

- [ ] Confirm byte layout and scaling for every message
- [ ] Confirm the PMU's own CAN export format from the client — **the PMU's
      message structure is fixed by ECUMaster, not by us.** Read it out of the
      software before designing around it
- [ ] Decide endianness and stick to it
- [ ] Write the map into a shared header both Teensys include

**Changing an ID on paper is free. Changing it across three codebases is not.**

---

# FINALISED MAP — byte layouts

*2026-08. Closes `[Q-041]` on the design side. One item remains — see §Before you code.*

All messages **8 bytes, little-endian**, standard 11-bit ID. Byte 7 of every
message is a **rolling counter**, incrementing 0–255, so a receiver can detect a
stalled sender instead of showing stale data as live.

---

## 0x100 · PMU → all · Vehicle state · 20 Hz

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

## 0x110 · PMU → all · Power · 10 Hz

| Byte | Field | Encoding |
|---|---|---|
| 0–1 | Battery voltage | uint16, mV |
| 2–3 | Total current | uint16, 0.1 A |
| 4 | Alternator charging | 0 no · 1 yes |
| 5–6 | reserved | |
| 7 | counter | |

## 0x120 · PMU → all · Outputs · 5 Hz

| Byte | Field | Encoding |
|---|---|---|
| 0–1 | Fuel level | uint16, 0.1% |
| 2–4 | Output on/off | 24 bits, one per channel O1–O24 |
| 5–6 | Soft-fuse tripped | 24 bits truncated — see note |
| 7 | counter | |

> Trip flags need 24 bits but only 16 remain. **Send trip state as a multiplexed
> byte instead**: byte 5 = channel index, byte 6 = that channel's status. Cycles
> through all 24 in ~5 s at 5 Hz. Faults latch until cleared, so a slow cycle is
> fine.

## 0x130 · PMU → all · Per-channel current · 5 Hz, multiplexed

| Byte | Field | Encoding |
|---|---|---|
| 0 | Channel index | 0–23 = O1–O24 |
| 1–2 | Measured current | uint16, 0.01 A |
| 3–4 | Soft-fuse setpoint | uint16, 0.01 A |
| 5 | Channel status | 0 off · 1 on · 2 tripped · 3 retrying |
| 6 | reserved | |
| 7 | counter | |

---

## 0x200 · ICU → all · Engine sensors · 20 Hz

**The ICU's own inputs.** This is the message that must not depend on anything.

| Byte | Field | Encoding |
|---|---|---|
| 0–1 | RPM | uint16, 1 rpm |
| 2 | Water temp | int8, °C, offset −40 |
| 3 | Oil temp | int8, °C, offset −40 |
| 4–5 | Oil pressure | uint16, 0.01 bar |
| 6 | Road speed | uint8, km/h |
| 7 | counter | |

## 0x210 · ICU → all · Sensor health · 2 Hz

| Byte | Field | Encoding |
|---|---|---|
| 0 | Sensor valid | bitfield: b0 RPM, b1 water, b2 oil temp, b3 oil press, b4 VSS |
| 1 | Sensor fault type | bitfield: b0 open, b1 short, b2 out of range, b3 implausible |
| 2 | CAN health | b0 PMU seen, b1 DCU seen, b2 keypad seen |
| 3–6 | reserved | |
| 7 | counter | |

---

## 0x300 · DCU → all · Climate · 5 Hz

| Byte | Field | Encoding |
|---|---|---|
| 0 | Mode | 0 off · 1 vent · 2 heat · 3 defrost · 4 A/C |
| 1 | Blower speed | 0–3 |
| 2 | Target temp | uint8, °C |
| 3 | Cabin temp | int8, °C, offset −40 |
| 4 | A/C request | 0 no · 1 yes |
| 5–6 | reserved | |
| 7 | counter | |

## 0x310 · DCU → all · Comfort bus · 2 Hz

| Byte | Field | Encoding |
|---|---|---|
| 0 | Seat heat | b0–1 driver level, b2–3 passenger level |
| 1 | Seat cool | b0–1 driver, b2–3 passenger |
| 2 | Mirror heat | b0 on |
| 3 | Nozzle heat / de-icer | b0 nozzles, b1 park de-icer |
| 4–5 | Comfort bus current | uint16, 0.01 A |
| 6 | reserved | |
| 7 | counter | |

## 0x320 · DCU → all · Radar · on change

| Byte | Field | Encoding |
|---|---|---|
| 0 | Alert level | 0 none · 1–5 |
| 1 | Band | bitfield: b0 X, b1 K, b2 Ka, b3 laser |
| 2 | Direction | 0 unknown · 1 front · 2 rear |
| 3–6 | reserved | |
| 7 | counter | |

---

## 0x400 · Keypad → all · Buttons · on change

| Byte | Field |
|---|---|
| 0 | Button states, bitfield, 8 keys |
| 1 | Button held ≥1 s, bitfield |
| 2–6 | reserved |
| 7 | counter |

---

## Timeout behaviour — define it once, obey it everywhere

| Message | Timeout | Receiver shows |
|---|---|---|
| 0x100 | 250 ms | Assume key OFF, warn |
| 0x110 | 500 ms | Blank voltage field, not last value |
| 0x120 / 0x130 | 1 s | Blank, not last value |
| 0x200 | 250 ms | **ICU only — this is its own message** |
| 0x300 / 0x310 | 2 s | Climate display shows "—" |
| 0x400 | none | Buttons are event-driven |

**A gauge frozen at its last value is worse than a gauge showing a fault.** Blank
or dash it, never hold.

---

## Bus load check

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

Against **500 kbit/s that is roughly 1.5% bus load.** Enormous headroom, even
before the LS ECU joins. No reason to raise the bit rate or trim rates.

---

## Before you code — the one open item

**Read the PMU's own CAN export format out of the client software first.**
ECUMaster fixes the PMU's message structure; we do not. Messages 0x100–0x130
above are the *intent* — the actual IDs and byte layouts must match whatever the
PMU is configured to transmit.

The ICU, DCU and keypad messages (0x200–0x400) are entirely ours and the layouts
above are final.

- [ ] Export the PMU CAN stream definition from the client
- [ ] Reconcile 0x100–0x130 against it
- [ ] Write the reconciled map into a shared `can_map.h` both Teensys include
- [ ] Tag that header. When it changes, both firmware versions bump together

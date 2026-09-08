<!-- out: 01-DESIGN/CAN-MESSAGES.md -->
# CAN MESSAGE MAP

*Rev 2026-09-07 · owns: nothing — rendered from `data/can_messages.csv`, `data/can_fields.csv` and `data/modules.csv`. `firmware/icu/can_map.h` is the machine copy; the drift report in [`../03-INSTALL/BRING-UP.md`](../03-INSTALL/BRING-UP.md) says how far behind it is.*

**Bus:** CAN2 · 500 kbps · CAN 2.0B · 11-bit identifiers (D-086) — the PMU is CAN 2.0 only, so the shared bus cannot be FD. **Priority:** lower ID = higher priority, and priority is *per frame*: oil pressure lives in `0x200`, fuel level in `0x218`, so oil pressure always wins arbitration. At this bus load that is worth a quarter of a millisecond; what actually protects the car is that **no PMU control rule reads any of these frames** (electrical D-251). **The AEM wideband is the one vendor node** — a 29-bit, big-endian frame at 100 Hz, confirmed from AEM's 30-0300 sheet (electrical D-266); the receive filter and the PMU's CAN input both make that one exception.

## Contents

1. Nodes · 2. Messages · 3. Layouts · 4. Timeouts · 5. Bus load · 6. Design rules · 7. Before you code

## 1 · Nodes

{{can_nodes}}

## 2 · Messages

{{can_messages}}

## 3 · Layouts

All of ours are **8 bytes, little-endian**, standard 11-bit ID, **byte 7 a rolling counter** 0–255 so a receiver can tell a stalled sender from a quiet one — compare with `(uint8_t)(now - prev) != 0`, which wraps the way the counter does.

{{can_layouts}}

## 4 · Timeout behaviour — define it once, obey it everywhere

**A gauge frozen at its last value is worse than a gauge showing a fault.** Blank or dash it, never hold. The ICU renders a stale CAN value as dim green dashes, distinct from a hardware fault (D-153).

{{can_timeouts}}

## 5 · Bus load

{{can_busload}}

Enormous headroom before the LS ECU joins. No reason to raise the bit rate or trim rates.

## 6 · Design rules

**Single source per signal** (D-078 → D-306). The PMU owns battery voltage, key state, output states and channel currents; the ICU owns rpm, water temp, oil temp, oil pressure, road speed and fuel level; the DCU owns climate and comfort state. The one deliberate double read is the oil-pressure node — the PMU excites it and reads it on A7, the ICU reads it and drives the old gauge from it (electrical D-258 / D-260) — a cross-check. **The ICU's critical gauges do not depend on this bus** (D-083): if CAN2 dies, only the PMU-published fields and AFR go blank. **Every frame of ours carries a counter; every timeout is explicit.** **Wire is control, CAN is telemetry** (electrical D-251).

## 7 · Before you code against the PMU messages

- [ ] `V-065` — export the PMU's real CAN stream definition from the client (electrical install §5.5) and reconcile `0x100`–`0x130`; update `can_map.h` and the data together
- [ ] `F-012` — bump `can_map.h` for `0x218`, the `0x120` reservation and the `0x300` byte changes; copy it over the three test-sketch folders; run `tests/run.bat`
- [x] electrical `Q-304` → D-266 — the AEMnet frame is confirmed; the PMU's CAN input for it is 29-bit, big-endian

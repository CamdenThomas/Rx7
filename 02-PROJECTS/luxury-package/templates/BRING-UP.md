<!-- out: 03-INSTALL/BRING-UP.md -->
# BRING-UP — firmware, boards and the header-drift report

*Rev 2026-09-07 · owns: nothing — rendered from `data/work.csv`, `data/bringup_log.csv` and the comparison of `data/can_messages.csv` against `firmware/icu/can_map.h`. How to build and test the firmware is [`../01-DESIGN/firmware/README.md`](../01-DESIGN/firmware/README.md)'s.*

> **The Teensy 4.1 is 3.3 V only. It is not 5 V tolerant.** Every sensor input gets a divider or a clamp before it touches a pin; on the bench, drive inputs from 3.3 V, never the 5 V rail. **One cable, one board at a time.** Label the boards `ICU`, `DCU`, `SPARE`.

## 1 · The header against the map

{{can_drift}}

## 2 · Work — bring-up stages and the agent-side backlog

{{work:kind=bring-up}}

{{work:kind=firmware}}

{{work:kind=hardware}}

{{work:kind=docs}}

{{work:kind=design}}

## 3 · The bench mule — what three Teensys buy you

```
   [Teensy 1: ICU]  <--- CAN2 ---  [Teensy 2: pmu_sim]     fuel? no — fuel is the ICU's now (0x218);
        |  ^                        volts, key state, 24 channels, faults
        |  +--- pulse in ---------  [Teensy 3: tach_simulator]   rpm, and road speed on a second channel
        +--- analog in ---------->  potentiometer, standing in for a sender node
```

The PMU simulator exercises only what genuinely comes from the PMU — battery voltage, key state and channel telemetry. Pull its power and watch: volts should blank; **everything else should carry on.** If the whole cluster goes blank, the isolation D-083 promises is not there. `pmu_sim/channels.h` is rendered by this project's build from the electrical pin table (D-311); the amp figures in it are the electrical build's enable-at values, and the simulator prints at boot how many are still estimates.

## 4 · Log

{{bringup_log}}

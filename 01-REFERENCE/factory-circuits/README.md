# Factory Circuits — decoded from the 1982 wiring diagram

> **Read this before using the "what this means for the rebuild" tables.**
> Every circuit file ends with a mapping to the new design. Those mapping tables
> were written against the **archived C1–C7 connector scheme** and reference
> connectors that no longer exist. **The factory decode above them is still
> accurate and still authoritative** — only the rebuild mapping is stale.
>
> For current connector assignments go to
> `02-PROJECTS/electrical-pmu/legs/PIN-MAP.md`.

One file per circuit. Each is the **functional definition** of what the circuit
is supposed to be, not a forensic trace of the scan. Every wire and connector is
being replaced, so these exist to capture *logic, devices, and feed topology* —
the things that survive a rewire.

Source: `01-REFERENCE/1982RX7WiringDiagram.pdf` (31 pages, scanned, no text layer).

**Current draw and signal types for every circuit here live in one place:**
`02-PROJECTS/electrical-pmu/LOADS.md`. Leg design needs all loads side by side,
so they are not duplicated into each circuit file.

## Section → page map

| Sec | Contents                                                                                  | Schematic pg | Harness routing pg |
|-----|-------------------------------------------------------------------------------------------|--------------|--------------------|
| —   | Component list                                                                            | 4–5          | —                  |
| O   | How to use / symbols                                                                      | 6–8          | —                  |
| W   | Electrical wiring schematic (whole car)                                                   | 9            | —                  |
| A   | Charging, starting                                                                        | 10           | 11                 |
| B   | Emission, ignition, cruise, kickdown, fuel pump                                           | 12–14        | 15                 |
| C   | Meters & warning lights                                                                   | 16           | 17                 |
| D   | Front + rear wiper & washer                                                               | 18           | 19                 |
| E   | Headlights, illumination, headlight cleaner                                               | 20           | 21                 |
| F   | Turn/hazard, back-up, stop, license, horn, side marker, front parking, tail               | 22           | 23                 |
| G   | Stereo, power antenna, heater & A/C, rear defroster                                       | 24           | 25                 |
| H   | Glove box, seat belt, lighter, key buzzer, interior/spot, clock, hatch release, fuel door | 26           | 27                 |
| I   | Remote mirror, power window                                                               | 28           | 29                 |
| X   | Common connector list                                                                     | 30           | —                  |

## Decode process (established, repeatable)

1. `pdftoppm -r 300 -f <pg> -l <pg> -png <pdf> out` — rasterize the one page.
2. Crop to the circuit block with Pillow, view.
3. Read the connector detail table at the bottom of the same page — it gives
   every connector's pin layout and wire color, which removes most guesswork.
4. Write the circuit file to this folder using the template in `horn.md`.

Rasterizing one page at 300 dpi and cropping twice is enough for any single
circuit on these sheets. Do not rasterize the whole document.

## Mazda wire color codes

First letter = base, second = tracer. `GY` on these sheets is **green/yellow**,
not gray — a real trap.

| Code | Color  | Code | Color       |
|------|--------|------|-------------|
| B    | Black  | Lg   | Light green |
| W    | White  | Gy   | Gray        |
| R    | Red    | Br   | Brown       |
| G    | Green  | O    | Orange      |
| Y    | Yellow | P    | Pink        |
| L    | Blue   | V    | Violet      |

## Status

| Circuit    | Section | File      | Status      |
|------------|---------|-----------|-------------|
| Horn       | F       | `horn.md` | Done        |
| All others | —       | —         | Not started |

*(superseded — see the full status table at the end of this file)*

---

## Master fuse & bus map (all sections)

Every protected bus in the factory car, decoded. This is the sheet to check
before assuming a circuit is independent — several are not.

| Bus     | Source                           | Fuse           | Feeds                                                     |
|---------|----------------------------------|----------------|-----------------------------------------------------------|
| **WR**  | Battery via 1.25 sq fusible link | —              | Everything constant                                       |
| —       | WR                               | 0.3 sq link ×2 | Headlights                                                |
| —       | WR                               | 0.5 sq link    | Ignition switch feed                                      |
| **WG**  | WR                               | 10 A           | Hazard flasher; remote mirrors                            |
| **GW**  | WR                               | 15 A           | **Horn + stop lights** (shared)                           |
| **R**   | WR                               | 10 A           | Tail / park / marker / license (via light switch)         |
| **LY**  | WR                               | 15 A           | Interior, spot, lighter, clock, luggage, ign switch light |
| **LO**  | WR                               | 20 A           | Glove box light, seat belt warning                        |
| **LR**  | WR                               | 20 A           | Hatch release, fuel-door release; audio                   |
| **GY**  | IG                               | 10 A           | **Turn signals + back-up + instrument cluster** (shared)  |
| **BW**  | IG                               | 7.5 A          | Alternator excitation                                     |
| **BLg** | IG                               | 10 A           | **Fuel pump**                                             |
| **LB**  | IG                               | 10 A           | Front wiper & washer                                      |
| **L**   | IG                               | 10 A           | Rear wiper & washer                                       |
| **LO**  | IG                               | 20 A           | Blower motor                                              |
| **Y**   | IG                               | 15 A           | Rear window defroster                                     |
| **BL**  | IG                               | 30 A           | Power windows                                             |

### Shared-fuse pairs worth knowing

- **Horn and stop lights** share one 15 A. A shorted horn kills your brake lights.
- **Turn signals, back-up lights and the whole instrument cluster** share one
  10 A. This is half of fault K-008.

## Ground point map

| Node     | Location          | Carries                                                                                                                           |
|----------|-------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| **X-13** | Front / dash area | Instrument cluster, flasher & control processing unit, emission control unit, front lamps, illumination, mirrors, windows, wipers |
| **X-14** | Front RH          | RH headlight, RH front lamps                                                                                                      |
| **X-15** | Rear              | **Fuel pump**, rear lamps, stop lamps, defroster, hatch and fuel-door solenoids                                                   |

X-13 is doing far too much. It is the single busiest node in the car and the
prime suspect for K-008. See `FAULT-K008-analysis.md`.

## Status

| Circuit                           | Section | File                                | Status                                       |
|-----------------------------------|---------|-------------------------------------|----------------------------------------------|
| Horn                              | F       | `horn.md`                           | Done                                         |
| Turn signals & hazard             | F       | `turn-hazard.md`                    | Done                                         |
| Stop / tail / marker / back-up    | F       | `stop-tail-marker-backup.md`        | Done                                         |
| Charging & starting               | A       | `charging-starting.md`              | Done                                         |
| Meters, ignition, fuel pump       | B, C    | `meters-ignition-fuelpump.md`       | Done                                         |
| Wipers & washers                  | D       | `wipers-washers.md`                 | Done                                         |
| Headlights, pop-ups, illumination | E       | `headlights-popups-illumination.md` | Done                                         |
| Blower, A/C, defroster, audio     | G       | `blower-ac-defroster-audio.md`      | Done                                         |
| Interior, hatch, accessories      | H       | `interior-hatch-accessories.md`     | Done                                         |
| Windows & mirrors                 | I       | `windows-mirrors.md`                | Done                                         |
| **Fault K-008 analysis**          | B, C, F | `FAULT-K008-analysis.md`            | Done                                         |
| Emission control detail           | B       | —                                   | Not decoded — mostly obsolete with the Weber |
| Cruise control detail             | B       | —                                   | Not decoded — pending V-023                  |

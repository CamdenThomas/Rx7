# Decision Log — Lighting & Body

*Rev 2026-08-30 · owns: this project's decisions — inherited D-107/110/111 and local L-001 … L-004. Append-only; never edit or delete an entry. Open items are `OPEN.md`'s.*

This project inherited three decisions from the electrical rebuild when lighting
was split out (D-123). They keep their original electrical-project IDs so
cross-references stay valid.

---

## Inherited from `electrical-pmu`

**D-107** — **Custom tail lights.** Thin LED strip per side, stock aperture and
width, white reverse section inboard, red for tail/brake/turn.

Design driver: FMVSS 108 requires **50 cm² minimum effective projected luminous
lens area** for a stop lamp or rear turn signal. A 1 cm strip across a 30 cm
aperture is 30 cm² — 40% short. **~2 cm clears it with margin** and still reads
as a thin strip.

Camden is not federally bound by FMVSS as an owner modifying his own car, and
Colorado only requires working lamps — but the standard is built to anyway, for
the liability position and because it is the engineering baseline for being seen.

**D-110** — **Pop-ups stay.** Not deleted. K1–K4, the four heavy conductors in
`L2-P1`/`L2-P2`, ladder inputs A4/A5, the wink switches and the retract mechanism
all remain. The headlamp becomes a **shorter rectangular unit inside the existing
bucket.**

**D-111** — **Tail light driver PCB per housing.** Takes tail, brake, turn and
reverse as logic inputs; handles the intensity ratio, constant-current drive and
turn-override locally. No backfeed between O6 and O7.

> Note: this is only needed for the **custom LED strip**, where one array serves
> both tail and brake. On stock dual-filament bulbs, O6 feeds the tail filament
> and O7 the brake filament with no backfeed and no driver board (D-121).

---

## Local decisions

**L-001** — Q-047 → **Reverse section: 5 cm wide, 2.2 cm strip height.**

Backup lamps have **no minimum lens area** federally. But brightness does not
substitute for area, because a reverse lamp's job is to *light the ground*, not
just be seen. Shrinking the aperture and raising intensity gives a hotspot
instead of a wash, plus glare.

At a nominal 30 cm aperture: 5 cm reverse leaves 25 cm of red, which at 2.0 cm
is exactly 50 cm². **2.2 cm gives 55 cm² — 10% margin**, so a measurement error
in `V-063` doesn't put it under the line. Reasoning in `TAIL-LIGHTS.md` §8.

**L-002** — **Headlamps are not a custom-build item.** A strip of LEDs cannot
produce a beam cutoff, and no care in fabrication fixes that — the optic is the
problem. **Source a DOT-compliant sealed unit.**

Tail lights are a reasonable custom project because the requirement is *be seen*.
Headlamps have to *illuminate the road without blinding oncoming traffic*, which
is a beam pattern measured across a grid of angles.

**L-003** — **Soft fuses must be re-set after any bulb change.** Values set
against incandescent are far too generous for LED — a tail circuit set at 6 A
does not protect a 3 A LED load. The same rule is D-122 on the electrical side;
the second-pass table is already waiting in
[`../electrical-pmu/05-BUILD/MIGRATION-LOG.md`](../../../02-PROJECTS/electrical-pmu/04-BUILD/MIGRATION-LOG.md).

**L-004** — **Hard prerequisite: the electrical rebuild is finished and shaken
down.** Phases 6, 7 and 8 complete, factory harness out, car driving on the PMU
with stock bulbs and soft fuses set from measurement. Only then does this project
change bulbs.

---

## Open

Moved to [`OPEN.md`](OPEN.md) — Q-048, V-063, V-064, V-066. (V-058, the
display nit rating, was listed here by mistake; it belongs to the ICU and lives
in the electrical project's `OPEN.md`.)

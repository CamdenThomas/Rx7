# sim — the circuits proved by number before anything is soldered

_Rev 2026-10-09 (Y2) · owns: the ngspice decks and their pass/fail limits. It lives beside
`firmware/` and `cad/` and, like them, is not part of the record: `rx7.py` never reads it, and
when a deck and a row disagree the row is the design and the deck is stale (`cad/README.md`'s
fence applies here word for word)._

**Why.** `rx7.py check` reads the harness as electricity (Y1), but it cannot tell whether a
transistor saturates or a pulse outlasts a boot. The 2026-09-28 review found two stages that
could not work as drawn (R12), and nothing in the record could have caught them. Each deck
here is one such question, with its limits written into the deck, swept over supply,
temperature and the one or two facts no document gives.

## Run it

```sh
sh run.sh          # every deck; exit 0 all pass, 1 a corner failed (printed), 3 no ngspice
```

`run.sh` branches on each deck's exit code only (R9). A deck prints one `INFO` line per
corner, `FAIL deck corner measure=value` for each limit it breaks, and `PASS deck` at the end.

## The decks

| Deck | Proves | Sweeps | Record rows |
| --- | --- | --- | --- |
| `wake_door.cir` | The door wake stage: the comparator keeps ≥ 0.1 V of margin both ways, one door opening makes one pulse of ≥ 0.6 × the rail into the strip for ≥ 0.3 s above 4 V, releasing makes nothing, the clamp holds Q3's base above −2 V, and a door does nothing while the PMU is awake | F23 9 / 12 / 16 V · −30 / 25 / 85 °C · the unpowered PMU pin 200 k / 1 M / open to ground (100 k and 10 k printed, not judged) | `wake_stages` WS00–WS1A, `ladders` A6 |
| `wake_a8.cir` | The same stage on the A8 ladder, for its smallest press (WINK_R, 33 k) and its largest (HAZARD, 4.7 k) | as above | `wake_stages` WS20–WS2A, `ladders` A8 |

What the first runs found, and changed in the record: the 1N5819 base clamp leaked the pulse
capacitor away at 85 °C (the whole pulse vanished) — the clamps are 1N4148 now; the 1 µF /
470 k / 100 k pulse stage gave 0.2 s at 12 V — it is 2.2 µF / 1 M / 47 k; and the comparator's
threshold only holds while the PMU's unpowered input reads ≥ 200 kΩ to ground, which is CK12
(i)'s reading.

## Models

`models/generic.lib` holds the textbook parameter sets (every one `confirm` against the
vendor's file). `run.sh` writes `models/active.lib`, which the decks include: the vendor models
under `01-REFERENCE/model/library/spice/<part>/*.lib` when that folder exists on the machine
(it is gitignored — vendor licences), then `generic.lib` for whatever is left. The LM2903
comparator is an ideal open-collector switch with 3 mV of hysteresis; its real offset (≤ 7 mV)
and bias (25 nA) sit far below every margin a deck tests.

## Adding a deck

One question per deck. Put every limit in the `.control` block as a `FAIL` test, sweep what
is uncertain with `foreach`, print an `INFO` line per corner, end with `quit 1` on any failure
and `PASS` + `quit 0` otherwise. Name the record rows the deck proves in its header, and when a
run changes a value, change the row first and cite the deck in its note.

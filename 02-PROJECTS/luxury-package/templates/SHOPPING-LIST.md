<!-- out: 02-SHOPPING/SHOPPING-LIST.md -->
# SHOPPING LIST — the luxury package

*Rev 2026-09-07 · owns: nothing — rendered from `data/parts.csv` and `data/stages.csv`. Every figure is an estimate until a cart exists; `status` says how firm each line is and `gate` names the question that has to close before it is bought.*

Nothing on this list is needed for the car to drive. Buy by stage, in the install plan's order; the bench stage (S0) can start today.

## 1 · Totals by stage

{{parts_totals}}

## 2 · In hand

{{parts:status=in hand}}

## 3 · Bench and boards — S0

{{parts:stage=S0}}

## 4 · The ICU — S1 · nothing to buy here

The ICU carrier, its parts and its senders are the electrical build's (its shopping list §6 and §6b, D-259 / D-313). This project's cluster spend is the display chain — the BT817 eval board in §3 and the glass in §6.

## 5 · Climate — S2

{{parts:stage=S2}}

## 6 · Display bezel — S3

{{parts:stage=S3}}

## 7 · Comfort — S4

{{parts:stage=S4}}

## 8 · Mirrors and windows — S5, S6

{{parts:stage=S5}}

{{parts:stage=S6}}

## 9 · Lighting — S7

{{parts:stage=S7}}

## 10 · Radar — S8

{{parts:stage=S8}}

## 11 · Rules for buying

The bench parts (`S0`) and the BT817 eval board can be bought now — nothing gates them. Every line marked *verify* has a question in front of it in [`../QUESTIONS.md`](../QUESTIONS.md); do not buy past its gate. Mirrors must be 3-wire motors with a resistive heater (D-305). The blower final stage must carry its own freewheel diode, switch at ≥ 20 kHz and be rated ≥ 25 A (D-308). Any part that touches the harness — there are none by design — would be the electrical build's, not this project's.

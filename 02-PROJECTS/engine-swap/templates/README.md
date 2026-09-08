<!-- out: README.md -->
# ENGINE SWAP — 1982 Mazda RX-7 (FB)

*Rev 2026-09-07 · owns: what the swap inherits from the electrical build and what it must give back. Facts are `data/`'s, prose is `templates/`', rendered by `tools/rx7.py -p engine-swap build`. Nothing is decided about the engine yet (this project's own numbers run from {{next_id:D}} and {{next_id:Q}}).*

The car drives on the new harness first; the swap comes after, on a finished car. The electrical build was drawn so that the swap touches **one leg**: the engine leg `L1` is cut at the firewall grommet and rebuilt from scratch around whatever the engine is (D-211(d)), while the 39-way connector, the dash node and every other leg stay as they are. The table below is the whole interface — every wire the swap will find waiting, what it carries today, and what it has to carry afterwards. The cavity states are the electrical build's (`python tools/rx7.py -p electrical-build get cavities "L1-S2 4"`); only the requirement is this project's.

## The hand-over

{{table:handover|-id}}

**Three rules carry across (electrical D-251, D-262, D-211(d)).** Anything the car *acts on* stays on a wire — oil pressure into the PMU's A7 and the tach into the ICU are hardwired from the new engine, never taken from the ECU's CAN frames; the ICU's other channels are jumpers and config files and most of them go quiet in favour of the ECU's frames; and the bay stays stripped — no conductor is run for a sensor that does not exist yet beyond the reserves above.

## The rest of this project

[`DECISIONS.md`](DECISIONS.md) holds the decisions inherited from the electrical build that shape the swap; [`QUESTIONS.md`](QUESTIONS.md) is what is open. The engine choice, the transmission, the fuel system (Aeromotive Phantom 340), the rear axle and the A/C are the research recorded under `00-CAR/` and in this project's questions.

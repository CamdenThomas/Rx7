# 2026-09-08 apply script — archived

*Rev 2026-09-08 · owns: what `apply-rx7-changes.py` did and did not do. History; nothing here is current.*

Written in chat on 2026-09-05 / 2026-09-08 while the device bridge was down, numbered from the Claude Project's `SOURCE-OF-TRUTH.md` (D-249 / Q-112), and run on 2026-09-08 against a tree that had already spent D-249–D-253 and Q-112, Q-116–Q-121.

**What landed:** the data edits (`parts` P085, `devices` DV25, `cavities` L3-S1 7, `loads` LD17, `rules` retry), the question packets Q-112–Q-121 and luxury Q-303, the template edits (×1.25 motor factor, the plunger sentence, install 3.7 / 3.11, PMU-CONFIG §5), the removal of D-247, and the `Latest` line.

**What did not:** the five decisions (its `patch()` saw `**D-249` … `**D-253` already present and skipped), and the condenser part (`P099` already existed).

**Repair (2026-09-08f):** the plunger ruling written as D-278, the benchmark rulings as D-279–D-282, the six benchmark packets renumbered Q-134–Q-139, the duplicate Q-112 removed, every cite re-pointed, the condenser added as P135. Never run this script again; it stays for the reasoning in its docstrings.

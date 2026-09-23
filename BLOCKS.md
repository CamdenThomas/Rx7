# BLOCKS

_The one page Camden writes in._

Type your answer after `**SOLVE:**` - on that line or the lines under it. Plain
sentences, any length, no markers to keep. Blank means unanswered. Skipping one costs
nothing: it stays open and comes back.

Nothing here is ever regenerated, and nothing but you writes in it.

**This page holds only what is still open.** Once you answer a block, it is applied
through the record, becomes a decision whose `closes` names it, and is then deleted from
here — `DECISIONS.md` is where a settled question lives, with the reasoning and the
consequences. So a short page means a short queue, not a lost history: search
`DECISIONS.md` for a block's id and you will find the ruling it became.

**Block ids are `project.number`.** `00.01` was the first block ever raised for the
electrical project, `01.07` the seventh for the luxury package. Numbers are never reused,
so gaps are blocks that have already been answered. Each project has its own header
below. (Until 2026-09-21 blocks were `BLK-###`; every old id is still findable in its
project's `retired` table.)

An answered block that is not yet applied is advisory - it never refuses a commit.

## CAR · Car

_Nothing open._

## 00 · Electrical

*Nothing open.*

## 01 · Luxury

### 01.11 · Which hidden radar / laser detector, and what the cluster shows
**Ask** Which concealed radar and laser detector goes in the car, and how much of its alert should the cluster show?
**Opened** 2026-09-23
**Why** You ruled a speed-trap detector with nothing on the windshield, the sensors put where they work best and hidden, and only a warning on the cluster (D-383). Two kinds of product can do that, and they differ in cost and in what the cluster can show. A custom-install system (Escort's MAX Ci 360c / Redline Ci 360c class) comes as separate front and rear radar receivers and laser sensors made to hide behind the bumpers, about $2,000–4,000 and usually sold through installers. Its data link is not published, so the DCU could only read its alert output: the cluster could say RADAR or LASER, but not the band or the direction reliably. A Valentine One is the only detector with a published data link (its ESP bus: band, direction, strength, everything the cluster frame 0x320 carries), about $500, but it is one box with its antennas inside. Hiding it means mounting the whole unit behind a plastic panel with a view ahead. Radar passes through plain plastic, but its laser sensor needs a clear view, so laser detection would suffer. Some custom systems also sell laser "shifters" (jammers); those are illegal in many states and are not part of either option. Detectors themselves are illegal in Virginia and Washington DC.
**Options**
- (a) A custom-install concealed system (Escort MAX Ci 360c class): front and rear sensors hidden in the bumpers. The DCU reads its alert output, and the cluster shows the alert and whatever the output tells it (at least radar vs laser). About $2,000–4,000. Cluster detail is limited to what its outputs give.
- (b) A Valentine One hidden behind a panel with a forward view, on its published ESP link into the DCU. Full band, direction and strength on the cluster. About $500. Laser detection is weaker hidden, and it is one box, not separate sensors.
- (c) Decide later. Nothing is bought; the radar pass-throughs stay capped.
**Recommend** (a), because it is the only one that matches "sensors in useful places, nothing visible"; (b) if full detail on the cluster matters more than hidden laser sensors.
**Stops** The detector's design (Z-002) and its harness pass-through (L3-RDR / L4-RDR). Nothing else.
**SOLVE:**

## 02 · Engine

_Nothing open._

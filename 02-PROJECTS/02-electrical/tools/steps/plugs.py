# -*- coding: utf-8 -*-
"""The plug of every part (D-543), worded for the step writers of every phase.

Reads 02-electrical `devices` and nothing else: `plug` (the connector the part takes), `plug_from`
(how that is known), `leg_end` (how the harness end is made), `plug_note`, and `plug_seen` /
`plug_seen_on` (what Camden found at the car, and when). devices is the home of all six; this
module only turns a row into a line of a step. Rebuild a phase after any of them changes."""
import csv
import os

_D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "devices.csv")
DEV = {r["id"]: r for r in csv.DictReader(open(_D, encoding="utf-8", newline=""))}

FROM = {"diagram": "the 1982 wiring diagram", "catalogue": "the parts catalogue", "maker": "the maker's sheet",
        "record": "our own design", "look": "your own look at the car", "unknown": "no source at all", "": "nothing yet"}
END = {
    "factory-plug": "keeps its factory plug: the harness half is cut off the old harness with 150 mm of lead when this circuit "
                    "moves (E28) and spliced onto the new wires, colour to colour (D-537)",
    "new-connector": "ends in a new mating connector, bought for it (D-543)",
    "ring-or-spade": "ends in a heat-shrink ring or spade on the part's own stud, screw or tab",
    "our-deutsch": "ends in one of our own Deutsch pairs",
    "no-leg": "has no harness end of its own",
    "": "has no leg end written yet",
}


def name(i):
    """DV19 Light switch - the device's name cut at its first bracket or dash."""
    n = DEV[i]["device"]
    for cut in (" (", " - ", " — "):
        if cut in n:
            n = n.split(cut)[0]
    return "%s %s" % (i, n.strip())


def seen(i):
    return bool(DEV[i].get("plug_seen", "").strip())


def plug(i):
    """What the part takes: his look once there is one, else the record's line (which says confirm)."""
    d = DEV[i]
    if seen(i):
        return "%s (seen %s)" % (d["plug_seen"].strip(), d.get("plug_seen_on", "").strip() or "date not noted")
    return d.get("plug", "").strip() or "nothing in the record - confirm"


def look(ids):
    """One line per device for a look step: what the record expects, and where that came from."""
    out = []
    for i in ids:
        d = DEV[i]
        if seen(i):
            out.append("%s: already seen - %s" % (name(i), plug(i)))
        else:
            out.append("%s: the record has, from %s - %s" % (name(i), FROM[d.get("plug_from", "")], plug(i)))
    return out


def end(i):
    """One line for a leg end: the device, how its end is made, and the plug it takes."""
    d = DEV[i]
    return "%s %s. Its plug: %s" % (name(i), END[d.get("leg_end", "")], plug(i))


def ends(ids):
    return [end(i) for i in ids]


def by_end(kind, ids=None):
    return [i for i in (ids or DEV) if DEV[i].get("leg_end", "") == kind]


LOOK = ("At each: with the two halves apart - or as it sits, if it will not part - count the cavities and the wires, "
        "note the housing's colour and any maker's name or number moulded into it, and say which half is on the part "
        "(bare pins or blades on the part, or a housing on a pigtail). Photograph the face square-on with the ruler "
        "beside it, and once from the side.")
ANSWER = ("one line per device id - ways, colour, any mark, which half is on the part, the photo's name, and whether the "
          "plug is sound or cracked")

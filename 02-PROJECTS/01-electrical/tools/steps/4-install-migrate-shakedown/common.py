"""Helpers for the g4 briefs and steps drafts (01-electrical work rows E24..E48)."""
B = []
S = []

CLIENT = "Camden's Windows laptop with ECUMaster's PMU client (D-376)"
CANCABLE = "USB-to-CAN interface cable (P138)"
METER = "multimeter: DC volts, ohms, continuity beeper (P045)"


def brief(id, goal, where, time, tools, parts, before, know, done_when, if_not, record):
    B.append(dict(id=id, goal=goal, where=where, time=time, tools="\n".join(tools),
                  parts=parts, before="\n".join(before), know="\n".join(know),
                  done_when=done_when, if_not=if_not, record=record))


def steps(work, rows):
    for n, r in enumerate(rows, 1):
        r = list(r) + ["", "", ""]
        S.append(dict(id="%s.%02d" % (work, n), work=work, n=n, do=r[0], how=r[1],
                      expect=r[2], caution=r[3]))

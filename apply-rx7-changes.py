# -*- coding: utf-8 -*-
"""
Rx7 - apply the queued work from 2026-09-05 (future-proofing sweep) and
2026-09-08 (comparative design review) THROUGH THE WHOLE PROJECT.

    python apply-rx7-changes.py --dry      # writes nothing, shows the plan
    python apply-rx7-changes.py            # applies, then runs the build
    python apply-rx7-changes.py --root "C:\\Users\\Camden Thomas\\Documents\\Storage\\Rx7"

v3 - runs from anywhere. Finds the repo, handles CRLF line endings from a
fresh Windows clone, and forces UTF-8 so a cp1252 console cannot kill it
part-way through.

Safe to run twice, and safe to run after v1 or v2 - every change checks
whether it is already present and skips. Anything whose anchor cannot be
found is reported as MISS and left alone; the summary lists what to do by
hand. Nothing hardware-affecting is decided: the contested items go in as
Q- packets. Five small policy/config decisions log as D-249..D-253.
"""
import io, os, subprocess, sys

# --- make Windows consoles safe for the em-dashes and middots below --------
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

DRY = "--dry" in sys.argv

# --- find the repo ---------------------------------------------------------
def find_root():
    if "--root" in sys.argv:
        return os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
    here = os.path.abspath(os.path.dirname(__file__) or ".")
    home = os.path.expanduser("~")
    cands = [here, os.getcwd(),
             os.path.join(home, "Documents", "Storage", "Rx7"),
             r"C:\Users\Camden Thomas\Documents\Storage\Rx7",
             r"C:\Users\USER\Documents\Storage\Rx7"]
    # also walk up from the script and the cwd, in case we sit in a subfolder
    for start in (here, os.getcwd()):
        p = start
        for _ in range(6):
            cands.append(p)
            p = os.path.dirname(p) or p
    for c in cands:
        if c and os.path.exists(os.path.join(c, "tools", "rx7.py")):
            return c
    print("Could not find the Rx7 repo. Looked in:")
    for c in dict.fromkeys(cands): print("   " + c)
    print('\nRe-run with:  python apply-rx7-changes.py --root "<path to Rx7>"')
    sys.exit(1)

ROOT = find_root()
TOOL = os.path.join(ROOT, "tools", "rx7.py")
EB   = os.path.join(ROOT, "02-PROJECTS", "electrical-build")
LUX  = os.path.join(ROOT, "02-PROJECTS", "luxury-package")
T    = os.path.join(EB, "templates")
DEC, QUE, LQUE = os.path.join(EB, "DECISIONS.md"), os.path.join(EB, "QUESTIONS.md"), os.path.join(LUX, "QUESTIONS.md")
TDES, TINS, TCFG = os.path.join(T, "DESIGN.md"), os.path.join(T, "INSTALL.md"), os.path.join(T, "PMU-CONFIG-SHEET.md")

ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
log = []
def rec(k, w): log.append((k, w)); print(f"{k:6} {w}")

# --- read/write that survives CRLF and a BOM -------------------------------
def read(path):
    raw = io.open(path, encoding="utf-8-sig", newline="").read()
    return raw.replace("\r\n", "\n"), ("\r\n" in raw)

def write(path, s, crlf):
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace("\n", "\r\n") if crlf else s)

def patch(path, anchor, insert, marker, mode="before"):
    name = os.path.relpath(path, ROOT)
    if not os.path.exists(path): return rec("MISS", f"{name} - file not found")
    s, crlf = read(path)
    if marker in s: return rec("SKIP", f"{name} - {marker[:46]} present")
    if anchor not in s: return rec("MISS", f"{name} - anchor not found: {anchor[:56]!r}")
    i = s.index(anchor)
    s = (s[:i] + insert + s[i:]) if mode == "before" else (s[:i+len(anchor)] + insert + s[i+len(anchor):])
    if not DRY: write(path, s, crlf)
    rec("OK", f"{name} - inserted {marker[:46]}")

def swap(path, old, new, marker):
    name = os.path.relpath(path, ROOT)
    if not os.path.exists(path): return rec("MISS", f"{name} - file not found")
    s, crlf = read(path)
    if marker in s: return rec("SKIP", f"{name} - {marker[:46]} present")
    if old not in s: return rec("MISS", f"{name} - text not found: {old[:56]!r}")
    if not DRY: write(path, s.replace(old, new, 1), crlf)
    rec("OK", f"{name} - replaced {old[:44]!r}")

# ================================================================= DATA ====
DATA = [
    ["set", "parts", "P085",
     "item=Brake pedal (stop lamp) switch, without cruise - any 2-terminal type",
     "used_for=The A3 ladder only. The wake contact is a spare P084 plunger on the pedal (D-249)"],
    ["set", "devices", "DV25", "ident=F-11 (new)",
     "terminals=Contact -> 4.7 kOhm -> L3-S1 5 (the A3 ladder)<br>Other side -> dash ground<br>"
     "Wake is NOT taken from this switch - a spare P084 plunger on the pedal feeds L3-S1 7 (D-249)"],
    ["set", "cavities", "L3-S1 7",
     "lands_on=Spare P084 adjustable plunger switch on the brake pedal, fed from the F3 switch supply "
     "branched off L3-S2 2 in the leg (D-249)"],
    ["set", "loads", "LD17",
     "design_a=VERIFY - assumed PMU 150 mA; a bench measurement of an ECUMaster PMU reports under 20 mA",
     "basis=D-251: measured at the dash node before the dash closes. Target <=30 mA, accept <=50 mA"],
    ["add", "parts", "id=P099", "store=Amazon", "section=Dash node and electronics",
     "item=Ignition noise-suppression capacitor, automotive, ~0.47 uF 250 V, ring-lug case",
     "spec=Reproduces the factory condenser B-22 on the coil/igniter supply",
     "qty=2", "unit_usd=10", "basis=est",
     "used_for=O12 branch at the coil bracket - this harness runs CAN and eight analog ladders past "
     "the leading/trailing igniters (D-252)", "status=to add", "--after", "P074"],
    ["set", "rules", "retry", "rule=Retry and latch",
     "definition=Split by fault type (D-250). Hard overcurrent: bounded fast retries, then latch, then "
     "flag. Open-load or thermal: no latch. NEVER a silent latch on a safety channel - a latched stop "
     "lamp or headlamp must annunciate, because a latched-off headlamp at night is worse than a "
     "flickering one"],
]

# ============================================================ DECISIONS ====
D249 = """**D-249 - The brake wake comes from its own plunger switch, not from a two-circuit stop-lamp switch.** Supersedes D-247. The 2026-09-05 parts sweep found that the switch D-247 assumed does not exist in the shape it needs: the non-cruise FB switch is NLA, and the with-cruise switch that *is* in stock (`H003-66-490A`, $47) carries **NO + NC**, not two NO poles. It can drive the A3 ladder or the wake strip, not both.

The fix costs nothing and removes the dependency entirely: **a spare P084 adjustable plunger switch on the brake pedal** provides the wake contact - the 6-pack is already carted and only three are needed for the doors - fed from the F3 switch supply branched off `L3-S2 2` and returning on **`L3-S1 7`** to wake strip input 6, exactly as D-247 drew it. The stop-lamp switch then reverts to *any* 2-terminal part, which is what the aftermarket actually sells.

The failure mode falls the right way: a dead plunger costs the wake, not the brake lamps, because the lamps come from the real switch through A3. If a plunger will not mount cleanly at the pedal, the alternative is an optocoupler at the node driven by the wake line, pulling the A3 4.7 kOhm leg - also zero conductors.

"""
D250 = """**D-250 - Protection is configured as two decisions, not one, and the policy differs by fault type.** From the 2026-09-08 benchmark against MoTeC, TI and Infineon practice. Four refinements to D-164/D-165/D-175, all configuration, no wire and no part:

*Sizing.* The flat current threshold comes from the load (**~1.15x measured steady state**); the **time / I2t curve comes from the conductor**. MoTeC states that setting a limit near the device's own draw *"is unlikely to be effective"* at protecting the device - the limit exists to protect the wire. D-232 already ties gauge to limit; this ties the curve to the gauge.

*Inrush rides on the time dimension, never on the flat threshold.* Raising the threshold to stop nuisance trips buys a hole in the protection. For motors prefer a **stall timer** over a current trip - a wiper or a pop-up at stall is a thermal event, not a short.

*The motor factor goes from 1.10 to 1.25 on measured stall.* 1.10 is tighter than TI's 1.15 on *nominal*, applied to a stall figure that rises with age and with falling voltage. Note the consequence that config cannot fix: **O1 is already at the 25 A channel ceiling against a measured 26 A both-sides stall** (LD08), so the pop-up bus has no headroom and leans on the D-186 obstruction timeout instead. O8/O9 are held at 13.0 A by the DT contact rating (D-223), so this factor changes no existing number - it governs every figure measured from here on.

*Bulb-out annunciation on O2, O3 and O7.* Per-channel undercurrent against an expected window says a stop or headlight bulb is dead. On ECUMaster undercurrent raises a fault flag and **does not disable the output**, which is exactly right - it is an annunciator, not protection, and no logic may be built on it. This is the affordable answer to both brake lamps sharing O7, since there is no spare 15 A channel to segment into.

"""
D251 = """**D-251 - The sleeping current is a budget and an acceptance test, not an assumption.** LD17 assumed *PMU 150 mA, nothing else*. A bench measurement of an ECUMaster PMU reports **under 20 mA**, and ECUMaster publishes no sleep-current specification at all. On the 40 Ah pack that is the difference between roughly **11 days and 80 days** of parking before the BMS cuts off - and a LiFePO4 gives no slow-crank warning. It is fine, and then it is completely dead, sometimes needing a charger to wake the BMS.

**Measure total sleeping current at the dash node before the dash closes** (install 3.11). Target **<= 30 mA**, accept **<= 50 mA** - BMW's own published closed-circuit figures for the E65, which logs anything above 80 mA as a violation. Budget the wake strip explicitly: the two NPN sense stages and the bleed resistor are each a permanent path, and no published figure exists for a stage of this design.

Already correct and worth not breaking: every CAN2 drop is fed from **O10**, which de-energises in sleep. Bus traffic is what prevents standby on every PDM in the reference set, and CAN keypads are named specifically - the accessory-bus feed closed that hole before it opened.

"""
D252 = """**D-252 - The factory ignition noise-suppression condenser is reproduced on the O12 branch.** The 1982 diagram carries a condenser (B-22) on the igniter and coil `BW` supply. Mazda fitted it because the leading and trailing igniters put measurable hash on the ignition bus - and this harness runs CAN2 and eight analog resistor ladders past those coils, which the factory one did not. Fit it at the coil bracket on the L1-P 1 branch (P099), or delete it only against a measurement showing it is unnecessary. Deleting it silently is the fault that gets misdiagnosed as a bad ladder six months later.

"""
D253 = """**D-253 - Two details that must not quietly drift.** Both surfaced in the 2026-09-08 review as load-bearing with no obvious owner.

*F20's ignition feed is a requirement, not a convenience.* The wideband gauge (D-244) sits on O12 because **an un-powered oxygen sensor is quickly damaged if the engine runs with the sensor in the exhaust**. It must be live whenever the engine can run. Nobody may move it to the accessory bus.

*Field recovery from a dead output runs through the 25 A class only.* O13/O14 (LS reserve) and O15 (comfort) are unallocated; **there is no spare 15 A or 7 A output**. A failed 15 A or 7 A channel therefore moves to a 25 A output with its enable-at re-set - the wire is unchanged and the 25 A channel is the more capable one. Written here because the alternative is working it out at the roadside.

"""

# ============================================================= QUESTIONS ====
QPACK = """**Q-112 - The blower's speed control depends on two parts that no longer exist.** *(2026-09-05 sweep)*
The 79-83 resistor pack (P088) and the 4-position speed switch (P089) are both **NLA** - no aftermarket direct fit, the parts that surface are the FC's, used heater panels only. `A2` cannot be completed as written. The deeper problem is topological: with tap selection in the dash, **the tap conductors carry full motor current, 5-20 A**, up to the dash and back, which is what makes two dead parts load-bearing.
**Options: (a)** keep the switching **at the HVAC case** and run **3 small dash-to-blower conductors** (control/PWM, signal ground, switched +12) - serves a resistor pack driven by relays, a solid-state controller, or the DCU later. **(b)** **PWM the blower directly from O16**, one of only two channels with an integrated high-power flyback diode (D-009): no pack, no controller, no switch, infinitely variable, zero extra conductors. **(c)** Hunt a used pack and panel.
**Recommend (b), with (a) as the fallback** - confirm first that ECUMaster sanctions PWM on a 25 A channel for a brushed motor. If (b) holds, P088 and P089 leave the vehicle-parts list and K-023 stops depending on a switch nobody sells.

**ANSWER:**
>
>

**Q-113 - Alternator sense and phase conductors, run now and capped.** *(2026-09-05 sweep)*
The FB is an **LR** system: `BW` is the R terminal (ignition-switched regulator wake, under 0.5 A) and `WB` is L (lamp sink). The lamp is decorative - R does the exciting, and O12 -> F15 -> L1-S1 2 is correct for it. The **'86-88 FC 70 A alternator is a bolt-in with the identical two-terminal interface**, ~$120, and the single narrow V-belt caps realistic output around 70-90 A anyway - so that is the sensible ceiling and it needs no wiring change.
What cannot be fitted today is anything **LS-type** - FD 100 A, GM CS-series, Denso 3-wire - because they need a **sense** wire and use the **lamp as the excitation path**. Two 16 AWG conductors into free `L1-S1` cavities (5, 7, 8, 12 are all sealing plugs) cover it: **S**, whose dash end lands on the **busbar** through a 3-5 A fuse rather than at the alternator stud, and **P** (phase/FR, milliamps, free insurance).
*Note against D-198:* once the ICU replaces the cluster there is no bulb, so an LS-type unit needs a **100 Ohm 5 W resistor in parallel** on the L line or it may never start charging.
**Blocks:** L1-S1's final cavity state.

**ANSWER:**
>
>

**Q-114 - The wiper park sense is the one place a replacement motor will not fit.** *(2026-09-05 sweep)*
Replacement two-speed motors sort into five families. The fitted one (Japanese OE pattern) brings the cam out as a **dry SPDT** - what the A3 ladder assumes, and correct. But the most common universal on the shelf today is the **Bosch/SWF/Valeo DIN 72552 family**, which is self-parking: the cam's common is the **low-brush node**, `53a` wants a permanent +12, `53e` is the brake throw, and reading either would put battery volts and brush spikes onto A3.
**Recommend:** promote **`L2-S 4`** (sealing plug) to a capped `WIPER_PARK_RET` conductor, hold **`L2-M 8`** as a fused park feed, and specify the A3 wiper-park leg as **clamped and 12 V tolerant** at the resistor sub-assembly. Two cavities, and the whole replacement population fits.

**ANSWER:**
>
>

**Q-116 - Does CAN2 go to the rear?** *(2026-09-08)*
CAN2 reaches the engine bay (`L1-S1 9/10`) and the dash drops. **There is no CAN in L4.** A rear node is not hypothetical - the Ionic's BLE telemetry gateway, a reversing camera, tyre pressure, a hatch module - and `L4-S 3` and `4` sit as sealing plugs, exactly a twisted pair, with the YEL/GRN already carted.
**Recommend:** run the pair now and make the bus a proper line - **engine bay <- dash node -> rear**, 120 Ohm at both physical ends, the PMU's software termination **OFF** so it becomes a short stub rather than an end. A 16 ft unterminated stub off a 500 kbps bus cannot be bolted on later.
**Flip it if:** the gateway will live behind the dash and BLE reaches the cargo bin reliably - test with a phone before deciding.
**Costs:** two contacts, carted wire, one 120 Ohm resistor (P070 carries ten), one config change.

**ANSWER:**
>
>

**Q-117 - Should the master disconnect go back to the positive side?** *(2026-09-08 - supersedes D-245 if answered)*
D-245 put the switch in the battery negative, and its reasoning held as far as it went: with the negative open, a positive-to-chassis fault has no return path. The benchmark found three arguments the other way that were not considered.
**(1) Convention.** ABYC E-9.10.c puts the switch in the cranking-motor supply. NHRA requires the positive side verbatim. NEC 404.2(B) states the general principle - do not switch the grounded conductor. Anyone who works on this car, a first responder included, will expect a positive-side kill.
**(2) The negative leg is unfused by definition.** Any parallel negative bond - a shunt, a battery monitor sense lead, the pack's BMS or heater return, a trickle charger left connected - silently becomes the return path for the whole system.
**(3)** With the switch open and the engine running, the battery negative post floats at (Vsys - Vbat) above chassis and sits near spike potential during a load dump.
**Recommend:** **one positive-side switch at the battery carrying both branches** - the Class-T/PMU leg and the MRBF/starter leg - so opening it genuinely kills the car, on the side everyone expects. Keep post-to-switch-to-fuses in inches, as D-062 already demands. Pair with `Q-119`.
**Costs:** none - the switch is carted; cable lengths shift by a foot.

**ANSWER:**
>
>

**Q-118 - Kick-down: reproduce, delete deliberately, or defer?** *(2026-09-08)*
The 1982 component list carries a **kick-down switch (B-32)** at the throttle pedal and a **kick-down solenoid (B-33)** on the transmission - two wires, automatic-only. It appears in no cavity, no device row and no decision, and it is **not** on D-097's deliberate-deletion list. Without it the transmission will not force a downshift at wide-open throttle.
**Options: (a)** reproduce it - one dash-local conductor to the pedal box, one down the tunnel; **(b)** delete it deliberately and log it beside D-097; **(c)** run and cap the tunnel conductor now, decide later.
**Recommend (c) at minimum** - the tunnel is open once. **Blocks:** the L4 cut list.

**ANSWER:**
>
>

**Q-119 - The alternator has no disconnect path, and lithium makes a load dump worse.** *(2026-09-08)*
ISO 7637-2 pulse **5a** - an unsuppressed load dump on a 12 V system - is **65-87 V for 40-400 ms**. Reports on lithium BMS disconnects run **120 V+**. Two triggers, and the second needs no mistake and never goes away: **opening the master with the engine running** (Blue Sea: *"the voltage will increase due to the sudden elimination of the load. This will burn the diodes out in the rectifier quickly"*), and **the BMS opening while driving** on over-current, cell fault or over-temperature. Lead-acid degrades gracefully and stays in circuit; a BMS opens in milliseconds at full charge current.
**Two fixes, both cheap. (a)** Swap **P049 from the Blue Sea 9003e to the 9004e** - same single-circuit e-Series switch, same 350 A continuous / 1200 A cranking, but carrying an **Alternator Field Disconnect** pole whose contacts open *slightly before* the main contacts, so the field is dead before the main path breaks. **(b)** Fit a **high-joule TVS across the PMU main feed at the module** - the only thing covering the BMS case.
**Depends on `V-002`:** AFD only works on an **externally regulated** alternator, and the 1982 diagram draws the regulator inside the alternator envelope. If internal, the aux pole must instead kill the `BW` excitation - which O12 -> F15 already controls, so the PMU can do it in logic given a switch-position input. **Resolve V-002 before ordering.**
Also ask ECUMaster directly whether the PMU's *"immunity to transients according to ISO 7637"* covers pulse **5a** (unclamped) or only **5b**. Fit the TVS either way.

**ANSWER:**
>
>

**Q-120 - The MRBF rating was ruled against a cable that has since changed.** *(2026-09-08 - supersedes D-237 if answered)*
D-237 fixed the starter fuse at 200 A, correct **when the cable was 2 AWG** (~210 A). D-246 then took it to **1/0 (285 A)** and nobody re-opened the fuse. A fuse protects the cable, not the load, so at 1/0 the 200 A is sized to the load - conservative in the wrong direction - and the Bussmann MRBF curve is unforgiving of a long crank: **200 % (400 A) opens in max 60 s**, 135 % (270 A) in max 900 s. A hot rotary that cranks long walks up that curve.
**Recommend 250 A** (same 5191 holder, ~$17), then close `V-094` with a clamp meter on the starter cable during a hot start rather than from published curves.

**ANSWER:**
>
>

**Q-121 - Pick a limp-home strategy and write it into the install plan.** *(2026-09-08)*
No PDM vendor documents a bypass, backup module or manual override, and the corpus treats it as accepted risk - *"in the unlikely event that a PDM fails, you are pretty much done, whereas a fuse is always changeable."* The professional mitigation is carrying a spare configured unit. But that is a **racing** answer, and this is a street-registered car where brake lamps, ignition and fuel pump are all software-defined on one module that is not automotive-qualified and lives in a 44-year-old dash.
**Options, ascending: (a)** keep the config file and a USB-to-CAN cable in the car; **(b)** a one-page written emergency procedure for feeding fuel pump, ignition and brake lamps directly from the busbar; **(c)** carry a pre-configured spare PMU.
**Recommend (a) + (b)** - together they cost a cable and an afternoon. The design currently has none of the three. Field recovery from a *single* dead output is separate and already possible (D-253).

**ANSWER:**
>
>

"""
Q115 = """**Q-115 - Road speed: the car may already have a signal, at the dash.** *(2026-09-08)*
The speedometer is cable-driven and there is no electronic speed signal in the design - a digital cluster needs one. But the 1982 component list carries a **vehicle speed switch (B-29)**: a reed switch **inside the speedometer head** that pulses to ground on a single `BR` wire. It fed cruise control, which D-097 deleted, so it is sitting there unused and **terminating behind the dash**.
**Check at M-6**, with the cluster out anyway: find the `BR` wire at the speedometer head, confirm it pulses to ground as the cable turns, and count pulses per wheel revolution. If it checks out, road speed costs **one conductor** into a free `L3-S2 12` or `L3-S3` cavity and the tunnel run is deleted from the plan.
If it does not, the fallback is an inline pass-through sensor at the transmission (3-wire Hall, 12 V square wave, keeps the mechanical speedo alive) on a **4-core 20 AWG overall-shielded cable** - switched +12 fused 2 A, sensor ground, signal, spare - shield grounded at the **dash end only**, to a sealed 4-way at the transmission with an 18 in service loop. Measure the speedo drive thread at both ends before ordering: US sensors are 7/8"-18, Japanese drives are usually metric.

**ANSWER:**
>
>

"""
V081 = """
> **Expected values, and the branch each selects (2026-09-08).** A 450 dpi read of the factory diagram shows each motor as a self-contained assembly with an internal relay and a diode in series with each command input - on that reading `WR` is the motor's power path and `R`/`RY` are *relay-coil commands*. `LD08`'s measured 12.8/13.1 A stall says otherwise, if it was taken by feeding `R` or `RY`. This measurement settles it:
> - **under ~2 Ohm** - a motor winding. The current design is correct; proceed as drawn.
> - **30-120 Ohm** - a relay coil. Feed `WR` from O1, command `R`/`RY` on 16 AWG signal wire, keep `YG` as travel feedback - and **K1/K2 become unnecessary, freeing two size-12 cavities in L2-P**.
>
> **Do not cut or pin the L2 leg before this reading exists.**

"""
LUX303 = """**Q-303 - The battery's BLE telemetry, and where the gateway lives.** *(2026-09-08)*
The Ionic advertises as `IC-12V40-S9H` and exposes a Telink-class transparent-serial profile: **`FFE0`/`FFE1`** (Read, Write, Write Without Response, Notify - one characteristic both directions) plus the standard **Battery Service `180F`/`2A19`**, with `FEE7` advertised but absent from the connected GATT (an OTA/DFU service that appears only in bootloader mode - **leave it alone**).
A plain read of `FFE1` returned `7E 01 08 | E4 08 E4 08 E3 08 E3 08 | FC 0D` - start of frame, message type, length 8, then **four little-endian uint16s (2276, 2276, 2275, 2275)**, checksum, CR. Four near-identical values is a balanced 4S pack. The counts sum to 9102; the advertisement's manufacturer data begins `CC 32`, little-endian **13004**, i.e. **13.004 V** - two independent readings agreeing on pack voltage, and a scale of about **1.43 mV per count**.
**Two things follow.** If pack voltage and state of charge are in the **advertisement**, the gateway never has to connect: it scans passively, so no pairing, no command protocol to reverse, and no single-connection lockout of the phone app. And the ICU cannot host this - **a Teensy 4.1 has no radio**. The right shape is a small **ESP32 BLE-to-CAN gateway** publishing pack voltage, SoC, cell deltas and temperature onto CAN2, exactly the pattern D-244 set with the wideband: the device publishes, the PMU logs it as a received channel, the ICU displays it, and a hung BLE stack cannot take the cluster down.
**Open:** confirm the scale against the app (pack mV / the sum of the four counts); find the message types carrying current, temperature and SoC; and decide where the gateway sits, which is `Q-116`'s question.

**ANSWER:**
>
>

"""

def cut_d247():
    if not os.path.exists(DEC): return rec("MISS", "DECISIONS.md - file not found")
    s, crlf = read(DEC)
    if "**D-247" not in s: return rec("SKIP", "DECISIONS.md - D-247 already removed")
    end = "\n---\n\n## 4 · Outputs, soft fuses and logic"
    if end not in s: return rec("MISS", "DECISIONS.md - end of section 3 not found; remove D-247 by hand")
    i, j = s.index("**D-247"), s.index(end)
    if j < i: return rec("MISS", "DECISIONS.md - D-247 not where expected; remove by hand")
    if not DRY: write(DEC, s[:i] + s[j+1:], crlf)
    rec("OK", "DECISIONS.md - D-247 removed (superseded by D-249)")

print(f"Rx7 apply v3\nroot = {ROOT}\nmode = {'DRY RUN' if DRY else 'WRITING'}\n" + "="*74)

print("-- data")
for a in DATA:
    if DRY: rec("DRY", "rx7 " + " ".join(a[:3])); continue
    r = subprocess.run([sys.executable, TOOL, "-p", "electrical-build"] + a,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    out = ((r.stdout or "") + (r.stderr or "")).strip().replace("\n", " ")
    rec("OK" if r.returncode == 0 else "SKIP", f"rx7 {' '.join(a[:3])} | {out[:92]}")

print("-- decisions")
cut_d247()
patch(DEC, "\n---\n\n## 4 · Outputs, soft fuses and logic", D249, "**D-249")
patch(DEC, "\n---\n\n## 5 · Switches, ladders and inputs", D250 + D251 + D253, "**D-250")
patch(DEC, "\n---\n\n## 3 · The dash node", D252, "**D-252")
swap(DEC, "D-243 O2/O3 at 13 A** (2026-09-04).",
     "D-243 O2/O3 at 13 A** (2026-09-04) · **D-249 the brake wake gets its own plunger (supersedes "
     "D-247) · D-250 protection is two decisions · D-251 the sleeping current is an acceptance test · "
     "D-252 the ignition condenser stays · D-253 two details that must not drift** (2026-09-08).",
     "D-249 the brake wake gets its own plunger")

print("-- questions")
patch(QUE, "**T-017 · Verify the connector pin letters", QPACK, "**Q-112")
patch(QUE, "**V-055 · Sill space**", Q115, "**Q-115")
patch(QUE, "\n**ANSWER:**\n>\n>\n\n**V-055 · Sill space**", V081, "Do not cut or pin the L2 leg")
swap(QUE, "Two questions and one desk check.", "Ten questions and one desk check.",
     "Ten questions and one desk check.")
swap(QUE, "The brake pedal switch must be a **two-circuit** switch (D-247); a single-circuit one cannot "
          "be fixed later without pulling the pedal box apart again.",
     "The brake pedal switch can be **any 2-terminal type** - the wake contact is a spare P084 plunger "
     "on the pedal instead (D-249).", "any 2-terminal type")
swap(QUE, "**Two questions are left before shopping — `Q-107` and `Q-111`** — and one desk check, `T-017`.",
     "**Ten questions are left before shopping** — `Q-107` and `Q-111`, plus `Q-112` … `Q-114` and "
     "`Q-116` … `Q-121` from the 2026-09-05 and 09-08 sweeps — and one desk check, `T-017`.",
     "Ten questions are left before shopping")
patch(LQUE, "**V-083 · DCU carrier candidate parts**", LUX303, "**Q-303")

print("-- templates")
swap(TDES, "Motors: measured stall × 1.10.", "Motors: measured stall × 1.25 (D-250).", "× 1.25 (D-250)")
swap(TDES, "**the brake pedal switch's second pole** (D-247, so a pushed or towed car still lights its brake lamps)",
     "**a dedicated plunger switch on the brake pedal** (D-249, so a pushed or towed car still lights its "
     "brake lamps; the stop-lamp switch itself stays a plain 2-terminal part)",
     "a dedicated plunger switch on the brake pedal")
patch(TDES, "\n{{fuses}}",
      "\nThe flat limit comes from the load, the time curve from the conductor, and inrush rides on the "
      "time dimension rather than on a raised threshold (D-250). Retry and latch are split by fault type, "
      "and no safety channel latches silently.\n", "the time curve from the conductor")
swap(TINS, "Write the decision here: ☐ bridge R + RY ☐ R only. Repeat on E-04 (RH) → L2-P 4.",
     "Write the decision here: ☐ bridge R + RY ☐ R only. Repeat on E-04 (RH) → L2-P 4. "
     "**Expected values (D-186 vs the factory diagram): under ~2 Ω is a motor winding and the design "
     "stands; 30–120 Ω is a relay coil, meaning `WR` is the motor feed and `R`/`RY` are commands — in "
     "which case K1/K2 are deleted and L2-P is redrawn. DO NOT CUT OR PIN THE L2 LEG BEFORE THIS READING.**",
     "DO NOT CUT OR PIN THE L2 LEG")
swap(TINS, "the O12 taps through F15, F16 and F20",
     "the ignition suppression condenser P099 on the L1-P 1 branch at the coil bracket (D-252) · "
     "the O12 taps through F15, F16 and F20", "condenser P099 on the L1-P 1 branch")
patch(TINS, "\n---\n\n## 4 ",
      "- [ ] **3.11** **Sleeping-current acceptance test** (D-251). With the node built and the PMU "
      "asleep, break the main feed and read total current with the meter in series: ____ mA. "
      "**Target ≤ 30 mA, accept ≤ 50 mA.** Above that, pull the wake-strip branches one at a time to "
      "find it. Do not close the dash on a failing number — this is the one measurement that cannot be "
      "taken again without undoing the install.\n", "**3.11** **Sleeping-current acceptance test**")
swap(TCFG, "The software limit typed in before each output is first enabled.",
     "The software limit typed in before each output is first enabled. **Sizing is two decisions** "
     "(D-250): the flat threshold from the load at ~1.15× measured steady state, the time/I²t curve from "
     "the conductor. Inrush is absorbed by the time dimension, never by raising the threshold; motors "
     "prefer a stall timer. **Retry and latch split by fault type** — bounded retries then latch on a "
     "hard overcurrent, no latch on open-load or thermal, and never a silent latch on a safety channel. "
     "**Bulb-out annunciation on O2, O3 and O7** from per-channel undercurrent, which flags without "
     "disabling.", "Sizing is two decisions")

print("="*74)
if DRY:
    print("DRY RUN - nothing written. Re-run without --dry to apply.")
else:
    r = subprocess.run([sys.executable, TOOL, "-a", "build"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    print((r.stdout or "") + (r.stderr or ""))

miss = [w for k, w in log if k == "MISS"]
print("="*74)
print(f"applied {sum(1 for k,_ in log if k=='OK')}   skipped {sum(1 for k,_ in log if k=='SKIP')}   "
      f"missed {len(miss)}")
if miss:
    print("\nCould not place these - do them by hand from the PENDING docs in the Claude Project:")
    for m in miss: print("   - " + m)
print("\nNext IDs after this: decisions from D-254, electrical questions from Q-122, luxury from Q-304.")
print("Then delete the two PENDING docs from the project, and git commit.")

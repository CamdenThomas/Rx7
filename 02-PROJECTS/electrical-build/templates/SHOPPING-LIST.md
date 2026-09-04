<!-- out: 02-SHOPPING/SHOPPING-LIST.md -->
# ELECTRICAL BUILD — THE SHOPPING LIST

**Buy exactly what is listed, in the quantity listed, from the store shown.** Every line is a part number or an exact description, a quantity and a store. Nothing here needs to be understood.

**Where the numbers come from.** Four carts were built and reviewed live on 2026-09-02 (Waytek, WireBarn, DeutschConnector.com, Amazon); the cart totals below are those carts. A line marked **cart** is in a cart at that quantity. A line marked **to add** is needed by the design and is not in a cart yet — §8 gathers them. Unit prices marked *est* are estimates (±20 %); the cart total is the real figure. Shipping and tax are not included.

**Substitutions:** allowed only within the same class and rating (a different brand of 40 A SPDT micro relay with a diode is fine). **Never substitute** the Class-T fuse and block, the MRBF, genuine Deutsch contacts, or the SICMA terminals.

**What the parts are for:** every wire, connector, fuse and relay here is named in `../01-DESIGN/DESIGN.md`; the install plan says when each one is used.


## Totals

{{shopping_totals}}

## Already in hand — do not buy

- ECUMaster PMU-24 DL with its 39-way connector, 39 terminals and the USB-to-CAN adapter
- Two spare SICMA 39-way housings, each with a full pin set — **these are the practice and spare terminals** (the car uses 27 small + 12 large; the two spare sets are 54 small + 32 large)
- Ionic S9 lithium battery, heated car-post version
- UNI-T UT210E clamp meter
- Blade fuses — check the drawer against §9 before buying any
- Electrical tape, paint pen

---

## 1 · Waytek — fuse blocks, relays, sockets, busbar, 16 AWG wire spools

{{cart_line:Waytek}}

{{parts:Waytek}}

The four spools are about $355 of the cart. Every 16 AWG wire in the car except pink, the CAN pair and the shielded tach comes off these.

---

## 2 · WireBarn — 14, 12 and 10 AWG GXL by the foot

{{cart_line:WireBarn}}

{{parts:WireBarn}}

**To add at WireBarn** (the three 16 AWG colours Waytek does not stock as spools):

{{parts_to_add:WireBarn}}

Calculated lengths carry a 1.5× margin because the routes are measured after the order lands (install plan M-2).

---

## 3 · DeutschConnector.com — every Deutsch part, genuine

{{cart_line:DeutschConnector.com}}

Assembly kits = housing + wedgelock + solid nickel contacts for every cavity. Order the **solid** (`-16141` / `-12141`) contact versions, never stamped.

### Housings — one plug (S, leg side) + one receptacle (P, dash-node side) per code

{{deutsch_kits}}

No spare housing pairs are carted. A ruined housing is a one-week wait — keep the contacts spare instead (below) and never force a wedgelock.

### Contacts, plugs, clips, caps, tools

{{deutsch_contacts}}

---

## 4 · Amazon — backbone, cable, tools, consumables, electronics, switches

{{cart_line:Amazon}}. The cart was cleaned on 2026-09-02: everything below is in it or in *Saved for later*, and nothing else is. Unit prices here are estimates; the cart is the figure.

### Tools

{{parts:Amazon/Tools}}

### Power backbone and battery

{{parts:Amazon/Power backbone and battery}}

### Dash node and electronics

{{parts:Amazon/Dash node and electronics}}

### Consumables and labels

{{parts:Amazon/Consumables and labels}}

### Switches

{{parts:Amazon/Switches}}

**Not on Amazon any more, on purpose:** blade fuses (§9), aluminium sheet (§7).

---

## 5 · Nothing from Ballenger

The old list bought spare SICMA terminals here. The two spare housings in hand carry 54 small and 32 large terminals — more than enough spares. No order.

## 6 · Vehicle parts — not yet carted

RockAuto / PartsGeek / a Mazda specialist. Confirm fit for a **1982 RX-7 GS, FB, 12A, automatic** and keep the receipt.

{{parts:Vehicle parts}}

## 7 · Hardware store — after the measurement day

Bought with the parts in hand, once M-1 and M-4 in the install plan are filled in. Not before.

{{parts:Hardware store}}

## 8 · Still to add — the gap between the design and the carts

{{gaps}}

## 9 · Blade fuses — check the drawer first

Cheap assortments skip 2 A, 3 A and 7.5 A. What the car needs, with one spare of each:

{{blade_fuses}}

Plus the two MIDI fuses (F17 30 A, F18 100 A) and the Class-T and MRBF, which are on Amazon above.

## 10 · When it arrives

Count everything against this list before anything is opened. Housings: {{n_housings}} codes, two halves each (§3). Wire: four spools + the WireBarn cuts + the three added 16 AWG colours. {{arrival}}. Report any shortfall before the build starts — a missing housing stops a leg.

<!-- out: 03-INSTALL/WIRE-TABLES.md -->
# WIRE TABLES

Work sheets for the build, printed from the design (`../01-DESIGN/DESIGN.md`). **The design is the record** — if a row here ever disagrees with it, this sheet is wrong. §A the PMU connector, in termination order · §B the dash node · §C the legs, sill and drops (the cut list) · §D grounds · §E heavy cables. What a wire lands on at the device is the design's §12; what joins what at the dash node is the design's §5.3; which fuses and relays to fit is the design's §3 and §5.1.


## A · The 39-way PMU connector — terminate in this order

{{pmu_connector}}

The stud: 4 AWG RED ring lug from the busbar, torqued.


## B · Dash-node conductors

{{node_conductors_check}}

## C · Cut list — legs, sill, drops

One row per cavity. **Length** = the M-2 route for that leg + 15 % + 150 mm service loop; write it in before cutting. Cut CAPPED wires exactly like LIVE ones; PLUG cavities get a sealing plug in both halves and no wire.


### L1 Engine

{{cut_list:L1}}

### L2 Front

{{cut_list:L2}}

### L3 Dash

{{cut_list:L3}}

### L4 Rear

{{cut_list:L4}}

### Sill — doors

{{cut_list:Sill}}

### Drops

{{cut_list:Drops}}

## D · Ground wires

{{grounds_check}}

## E · Heavy cables

{{cables}}

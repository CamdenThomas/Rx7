export const meta = {
  name: 'rx7-part-research',
  description: 'Research every part in a set of batches: specs, datasheets, internal wiring, terminals, CAD, links - each batch then source-checked',
  phases: [
    { title: 'Research', detail: 'one agent per batch of parts writes a JSON of findings' },
    { title: 'Source check', detail: 'a second agent re-opens a sample of the cited sources and drops anything unsupported' },
  ],
}

const S = args.scratch
// The findings go straight into the tree (01-REFERENCE/research), never only a scratch folder:
// five wave-2 batches were lost that way (plan P48).
const OUT = `${T}/01-REFERENCE/research/research`
const T = '/home/crash/docs/storage/Rx7'

const RULES = `You research the parts of one real car for its owner's manual: a 1982 US Mazda RX-7 GS (FB), 12A rotary, 3-speed automatic, Sunbeam Silver, (the odometer is in rx7.py export, manual.odometer). Work in ${T}. The owner asked: "find as much information about every part: the spec sheet, diagrams, CAD, anything, internal wire diagrams, every detail, every layer".

READ FIRST (with rx7.py, never whole files):
- Your parts: python tools/rx7.py sql 00-CAR "select * from parts where id in (IDS)"  (parent = the part it sits in; catalogue = its factory catalogue figure and rows; note = what is known; 'confirm' in a note means nobody has checked it on the car).
- What is already known: python tools/rx7.py sql 00-CAR "select * from specs where part in (IDS)" and python tools/rx7.py sql 00-CAR "select * from terminals where part in (IDS)". Never duplicate a spec that is already there.
- The sources that exist: python tools/rx7.py sql 01-REFERENCE "select id,title,url,local_path from sources". Reuse an S- id whenever your fact comes from one of them.
- CAD already found: python tools/rx7.py sql 01-REFERENCE "select id,title,subject,fits,url,local_path from cad where subject like '%<word>%' or title like '%<word>%'".

SOURCES, best first:
1. This car's year: S-038 1982 Technical Data (${T}/01-REFERENCE/model/library/docs/fsm-technical-data-81-83/1982_RX7_Technical_Data.pdf), S-001 the 1982 wiring diagram (${T}/01-REFERENCE/factory-circuits/1982RX7WiringDiagram.pdf) and its decoded write-ups (${T}/01-REFERENCE/factory-circuits/*.md, OEM-RECORD.md), S-005 the parts catalogue (figure pages in ${T}/01-REFERENCE/manuals/1981-83_RX-7_Parts_Catalog_*.pdf), S-004/S-042 brochures, S-006 1981 training manual.
2. Other years' factory manuals: S-002 1985 workshop manual sections (${T}/01-REFERENCE/manuals/1985_RX-7_Workshop_Manual_*.pdf - Section 5 Engine Electrical, 15 Body Electrical, 50 Wiring, 1 Engine, 3 Cooling, 4A Fuel, 7B Automatic, 11 Braking, 13 Suspension, 10A Steering, 9 Axles, 14 Body), S-045 1980 sections (${T}/01-REFERENCE/model/library/docs/fsm-1980-sections/), S-039/S-040 1981/1983 technical data, S-043 carburettor manual, S-047 body shop manual. Read PDFs with the Read tool's pages parameter, a few pages at a time; use the section's index pages to find the right page.
3. The web (WebSearch, WebFetch): maker datasheets for the factory part or its direct replacement (Hitachi, Mitsubishi, Nippondenso, NGK, Koito, Stanley, Bosch, Standard Motor Products, Denso, Aisin, Tokico, Kayaba...), bulb datasheets by trade number (1157, 194, 1156...), rotary specialists (Atkins Rotary, Mazdatrix, Rotary Resurrection, Racing Beat), RockAuto listings that carry specifications, rx7club technical threads, free CAD (GrabCAD, Printables, Thingiverse, TraceParts, 3D ContentCentral, maker CAD pages).

WHAT TO FIND, per part - effort where it pays:
- ELECTRICAL parts (alternator and its brushes/rectifier/regulator, starter and solenoid, relays, switches, sensors, senders, motors, gauges, meters, lamps and bulbs, fuses/fusible links, coils, distributor, horn, wiper/washer, radio): ratings (volts, amps, watts, ohms, bulb trade number and base), resistances and test values from the factory manual, the INTERNAL wiring (what each terminal connects to inside: windings, regulator, contacts, filaments; for a switch, which terminals it joins in each position), and every TERMINAL with the factory wire colour on it and where that wire goes (S-001 and the write-ups). Replacement part numbers that cross-reference the Mazda number. Datasheets: download free PDFs.
- SERVICE and MECHANICAL parts: every factory spec - dimensions, wear limits, clearances, torques, capacities, pressures, adjustment values - from S-038 first, then the workshop manuals; replacement cross-references; where to buy (a live listing link); CAD if any.
- BODY, TRIM, GLASS, PANELS, UPHOLSTERY: the catalogue figure reference is its diagram; add dimensions only where a source gives them; whether new, reproduction or used is available and where (one link); do not spend more than two web searches per such part.

RULES OF THE RECORD:
- Never invent. Every value must be read from a source you actually opened; cite it (S- id or your new source key) and the page.
- A figure from a 1982 source applies to this car (applies blank). A figure only found in another year's manual (1980, 1981, 1983, 1985) gets applies=other-car unless a 1982 source gives the same figure - say which in the note.
- A datasheet for a replacement part describes that replacement, not necessarily the part on the car: put it as a spec whose item starts "Replacement <maker> <number>: ..." with confidence secondary.
- R11: nobody has seen the car. A terminal letter, wire colour or dimension that has not been measured on the car keeps the word confirm in its note (e.g. "from S-001; confirm on the car").
- Units in the unit column; numbers in value.
- 00-CAR states what the car IS: never cite a decision (D-###) or a block id in any row or note you write. Project decisions (e.g. D-097's list of what the NEW harness leaves out) say nothing about what is on the car today.
- The word confirm in a part's note_add hides the whole part from the Manual: use it only when it is uncertain whether the part is on this car at all, or which part it is. For a doubt about one detail (a trade number, a size, a colour) write "check".
- Optional equipment whose fitment is not recorded (rear wiper and washer, power antenna, cruise control, headlamp cleaner) and the cold-start hardware gone since the Weber conversion are already marked in the parts list: do not research them further.
- Downloads: free, no-login PDFs, datasheets, drawings and CAD only, each under 25 MB, into ${T}/01-REFERENCE/model/library/datasheets/<part id>/ (make the folder; curl -L -o). That folder is out of git; record local_path relative to the tree root. Never download anything behind a login or paywall - record its URL with login yes.

OUTPUT: write ONE JSON object to the file given, exactly this shape (empty arrays are fine):
{
 "parts": [ { "id": "PT0xx", "link": "a live page to buy or look it up, or empty", "support": "maker's support line/page if found, or empty", "cad": "a local CAD path or a cad row id, or empty", "note_add": "one or two sentences worth adding to the part's note, or empty" } ],
 "specs": [ { "part": "PT0xx", "category": "Electrical|Engine|Fuel|Cooling|Ignition|Charging|Lighting|Body|Brakes|...", "item": "", "value": "", "unit": "", "source": "S-0xx or your source key", "page": "", "confidence": "primary|secondary|unverified", "applies": "" or "other-car", "note": "" } ],
 "terminals": [ { "part": "PT0xx", "terminal": "B", "function": "", "inside": "", "wire": "BW", "to": "", "source": "S-001", "page": "", "note": "from S-001; confirm on the car" } ],
 "sources": [ { "key": "src-<short>", "title": "", "kind": "datasheet|manual|web|catalogue|forum|video", "covers": "", "url": "", "format": "html|pdf|pdf+step|pdf-scan|web-viewer|obj|json|jpg", "credibility": "primary|secondary|tertiary", "obtained": "yes|no", "local_path": "", "note": "" } ],
 "cad": [ { "id": "kebab-slug", "category": "parts|electrical|rotary|body", "title": "", "subject": "", "fits": "exact|close|different", "site": "", "url": "", "author": "", "licence": "", "format": "", "obtained": "yes|no", "login": "yes|no", "local_path": "", "detail": "", "note": "", "part": "PT0xx" } ]
}
Then return the structured summary.`

const SUMMARY = {
  type: 'object',
  properties: {
    path: { type: 'string' }, parts_covered: { type: 'integer' }, specs: { type: 'integer' }, terminals: { type: 'integer' },
    sources_new: { type: 'integer' }, cad: { type: 'integer' }, downloads: { type: 'integer' },
    nothing_found: { type: 'array', items: { type: 'string' }, description: 'part ids where no source had anything beyond the catalogue' },
  },
  required: ['path', 'parts_covered', 'specs', 'terminals', 'sources_new', 'cad', 'downloads', 'nothing_found'],
}
const CHECK = {
  type: 'object',
  properties: { checked: { type: 'integer' }, dropped: { type: 'integer' }, fixed: { type: 'integer' }, notes: { type: 'array', items: { type: 'string' } } },
  required: ['checked', 'dropped', 'fixed', 'notes'],
}

const res = await pipeline(
  args.batches,
  (b) => {
    const ids = b.parts.map((x) => `'${x}'`).join(',')
    return agent(`${RULES.split('IDS').join(ids)}\n\nYOUR BATCH: ${b.id} (system ${b.system}), parts ${b.parts.join(', ')}.\nWRITE TO: ${OUT}/${b.id}.json`,
      { label: `research ${b.id}`, phase: 'Research', schema: SUMMARY })
  },
  (sum, b, i) => sum && agent(`You check another agent's research for a car's owner's manual before it enters the permanent record. Work in ${T}. The findings are in ${OUT}/${b.id}.json (keys parts, specs, terminals, sources, cad). Pick 8 rows spread across specs and terminals (take every ${Math.max(1, 3 + (i % 4))}th, plus any that look surprising), open the exact source and page each cites (local PDFs with the Read tool's pages parameter; web sources with WebFetch; source keys are defined in the file's sources array, S- ids in: python tools/rx7.py sql 01-REFERENCE "select id,title,url,local_path from sources where id='S-0xx'"), and confirm the value is really there. Also confirm each new source URL loads and says what its row claims, and that every downloaded local_path exists. Rules the research had to follow: never invent; a 1982-source figure has applies blank, another year's figure alone has applies=other-car; unmeasured terminals/dimensions carry confirm in the note. Drop any row a source does not support, fix any wrong value/page/applies, and write the file back whole. If more than 2 of your 8 were wrong, check 8 more. Return what you did.`,
    { label: `check ${b.id}`, phase: 'Source check', schema: CHECK }).then((c) => ({ id: b.id, sum, c })),
)
return res.filter(Boolean).map((r) => ({ id: r.id, specs: r.sum.specs, terminals: r.sum.terminals, sources: r.sum.sources_new, cad: r.sum.cad, downloads: r.sum.downloads, empty: r.sum.nothing_found.length, checked: r.c && r.c.checked, dropped: r.c && r.c.dropped, fixed: r.c && r.c.fixed }))

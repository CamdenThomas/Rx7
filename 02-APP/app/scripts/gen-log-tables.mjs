// The log link's tables for the app, generated from the record (02-APP BL2, BL3; R2).
//
//   node scripts/gen-log-tables.mjs                 export the record and write the file
//   node scripts/gen-log-tables.mjs --from F.json   use an export already made (rx7.py export --out)
//   node scripts/gen-log-tables.mjs --check         rc 1 when the checked-in file is stale
//
// Reads, through `rx7.py export` (the app's one way to the record): 01-electrical
// log_channels (the 137-byte thinned record, LC01-LC53), log_link (the service, its UUIDs,
// the six opcodes and every payload the app reads or writes, LL01-LL10, LL18's err 7),
// log_files (the 32-byte header LF02 and the record sizes LF03-LF05) and params
// (log_thin_bytes_per_s). The summary's and the full record's layout strings are the
// firmware's (icu/log_store.h, LOG_SUMMARY_LAYOUT and LOG_FULL_LAYOUT): LF03 names that file as
// the summary's home "until it is rows", and the header's layout CRC is the CRC-32 of exactly
// those strings. Writes src/lib/logs/layout.generated.ts, checked in, so the app builds without
// Python; tests/logs.test.ts holds the decoder to it. The firmware's tests/gen_log_vectors.py
// reads the same rows the same way.
//
// Anything the record says that this script cannot read is an error (exit 1), never a guess.
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const app = join(here, '..');
const tree = join(app, '..', '..');
const OUT = join(app, 'src', 'lib', 'logs', 'layout.generated.ts');
const STORE_H = join(tree, '02-PROJECTS', '01-electrical', '00-design', 'firmware', 'icu', 'log_store.h');

const args = process.argv.slice(2);
const check = args.includes('--check');
const fromAt = args.indexOf('--from');
const errors = [];

function exportRecord() {
  if (fromAt >= 0) return JSON.parse(readFileSync(args[fromAt + 1], 'utf8'));
  const out = join(mkdtempSync(join(tmpdir(), 'rx7-gen-')), 'export.json');
  try {
    execFileSync('python3', [join(tree, 'tools', 'rx7.py'), 'export', '--out', out], { stdio: ['ignore', 'ignore', 'inherit'] });
  } catch (e) {
    if (e.status !== 1) throw e; // an invalid record still exports
  }
  return JSON.parse(readFileSync(out, 'utf8'));
}

const snap = exportRecord();
function table(name) {
  const t = snap.tables.find((x) => x.area === '01-electrical' && x.table === name);
  if (!t) throw new Error(`01-electrical has no ${name} table in the export`);
  return t.rows.map((r) => Object.fromEntries(t.columns.map((c, i) => [c, r[i] ?? ''])));
}
const byId = (rows) => Object.fromEntries(rows.map((r) => [r.id ?? r.key, r]));

const SIZE = { u8: 1, i8: 1, u16: 2, i16: 2, u32: 4, i32: 4 };
const snake = (s) =>
  s.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');

// ---------------------------------------------------------------- log_channels (LC01-LC53)
const UNITS = ['mile', 'mV', 'ms', 'A', 'λ', 'bar', 'km/h', '°C', '%', 'g'];
const unitRe = new RegExp(`^\\s*(?:(\\d+(?:\\.\\d+)?)\\s+)?(${UNITS.map((u) => u.replace('/', '\\/')).join('|')})(?=[\\s,(:;]|$)`);

function channel(r, i) {
  const id = `LC${String(i + 1).padStart(2, '0')}`;
  if (r.id !== id) errors.push(`log_channels: expected ${id}, found ${r.id} - the record skips or repeats a row`);
  const bytes = Number(r.bytes);
  if (!Number.isInteger(bytes) || bytes < 1) errors.push(`${r.id}: bytes '${r.bytes}' is not a whole number`);
  const enc = r.encoding.trim();
  let type, count, scale = 1, unit = '';
  const m = enc.match(/^(u?int)(8|16|32)(?:\s*×\s*(\d+))?/);
  if (m) {
    type = `${m[1] === 'uint' ? 'u' : 'i'}${m[2]}`;
    count = bytes / SIZE[type];
    if (!Number.isInteger(count)) errors.push(`${r.id}: ${bytes} bytes is not a whole number of ${type}`);
    if (m[3] && Number(m[3]) !== count) errors.push(`${r.id}: '× ${m[3]}' disagrees with ${bytes} bytes of ${type}`);
    const rest = enc.slice(m[0].length).replace(/^\s*,/, '');
    const u = rest.match(unitRe);
    if (u) {
      scale = u[1] ? Number(u[1]) : 1;
      unit = u[2] === 'mile' ? 'mi' : u[2];
    }
  } else if (/bitfield/.test(enc) && bytes === 2) {
    type = 'u16'; count = 1; // a 16-bit key bitfield (LC48, LC49)
  } else {
    type = 'u8'; count = bytes; // "as the frame": the frame's bytes as they are
  }
  const kind = /bitfield/.test(enc) ? 'bitfield' : m ? 'value' : 'state';
  // LF04: a temperature unseen in the second logs TEMP_INVALID (-128)
  const blank = type === 'i8' && unit === '°C' ? -128 : null;
  return { id: r.id, name: r.channel, bytes, type, count, scale, unit, kind, blank };
}

const channels = table('log_channels').sort((a, b) => a.id.localeCompare(b.id)).map(channel);
const thinLen = channels.reduce((s, c) => s + c.bytes, 0);
const params = byId(table('params'));
const thinParam = Number(params.log_thin_bytes_per_s?.value);
if (thinParam !== thinLen) errors.push(`params log_thin_bytes_per_s is ${thinParam}, log_channels sums to ${thinLen}`);

// ---------------------------------------------------------------- log_link
const ll = byId(table('log_link'));
const svc = ll.LL01?.payload.match(/([0-9a-f]{8})-([0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/);
const name = ll.LL01?.payload.match(/Name (\S+?);/);
if (!svc || !name) errors.push('LL01: no service UUID or device name');
const uuid = {};
for (const [row, key] of [['LL03', 'info'], ['LL04', 'drives'], ['LL05', 'control'], ['LL09', 'data'], ['LL10', 'status']]) {
  const m = ll[row]?.note.match(/([0-9a-f]{8})-\.\.\./);
  if (!m || !svc) errors.push(`${row}: no characteristic UUID in the note`);
  else uuid[key] = `${m[1]}-${svc[2]}`;
}

/** "a u32 · b u8 (…) · c u16" -> [[a, u32], …]; the words of a field become its snake_case key */
function fields(text, row) {
  const out = [];
  for (const part of text.split(' · ')) {
    const m = part.trim().match(/^(.+?) ([ui](?:8|16|32))\b/);
    if (!m) {
      errors.push(`${row}: cannot read the field '${part.trim()}'`);
      continue;
    }
    out.push([snake(m[1]), m[2]]);
  }
  return out;
}

const info = fields(ll.LL03?.payload ?? '', 'LL03');
const item = fields((ll.LL04?.payload ?? '').replace(/^[^:]*:\s*/, '').replace(/;.*$/, ''), 'LL04');
const status = fields(ll.LL10?.payload ?? '', 'LL10');
const dataHead = fields((ll.LL09?.payload ?? '').split(' · ')[0], 'LL09');

const ops = {};
const opFields = {};
for (const row of ['LL06', 'LL07', 'LL08']) {
  const named = [...(ll[row]?.item ?? '').matchAll(/\b([A-Z][A-Z_]+) 0x([0-9A-Fa-f]{2})\b/g)];
  if (!named.length) errors.push(`${row}: no opcode in the item`);
  for (const [, op, hex] of named) {
    ops[op] = parseInt(hex, 16);
    const p = ll[row].payload;
    if (named.length === 1) opFields[op] = fields(p, row);
    else {
      const m = p.match(new RegExp(`\\b${op}: (none|.+?)(?: - |\\. |\\.$|$)`));
      if (!m) errors.push(`${row}: no payload for ${op}`);
      else opFields[op] = m[1] === 'none' ? [] : fields(m[1], row);
    }
  }
}
if (Object.keys(ops).length !== 6) errors.push(`LL06-LL08 name ${Object.keys(ops).length} opcodes, LL05 says six`);

function codes(text, field, row) {
  const m = text.match(new RegExp(`${field} u8 \\(([^)]*)\\)`));
  if (!m) {
    errors.push(`${row}: no '${field} u8 (...)' list`);
    return {};
  }
  return Object.fromEntries(
    m[1].split(',').map((x) => {
      const [, n, w] = x.trim().match(/^(\d+) (.+)$/) ?? [];
      if (n === undefined) errors.push(`${row}: cannot read the ${field} code '${x.trim()}'`);
      return [Number(n), (w ?? '').trim()];
    }),
  );
}
const tiers = codes(ll.LL07?.payload ?? '', 'tier', 'LL07');
const states = codes(ll.LL10?.payload ?? '', 'state', 'LL10');
const errs = codes(ll.LL10?.payload ?? '', 'err', 'LL10');
for (const [, n, w] of (ll.LL18?.payload ?? '').matchAll(/\berr (\d+) = ([^.]+)/g)) errs[Number(n)] = w.trim();

const num = (row, col, re, label) => {
  const m = (ll[row]?.[col] ?? '').match(re);
  if (!m) errors.push(`${row}: cannot read ${label}`);
  return m ? Number(m[1]) : 0;
};
const protocol = num('LL03', 'payload', /protocol u8 \((\d+)\)/, 'the protocol');
const mtu = num('LL09', 'note', /MTU (\d+) or more/, 'the MTU');
const timeSlack = num('LL08', 'payload', /more than (\d+) s/, 'the SET_TIME slack');

// ---------------------------------------------------------------- log_files and log_store.h
const lf = byId(table('log_files'));
const headerLen = Number((lf.LF02?.file ?? '').match(/The (\d+)-byte header/)?.[1] ?? NaN);
const header = [];
for (const part of (lf.LF02?.layout ?? '').split(' · ')) {
  const p = part.trim();
  let m;
  if ((m = p.match(/^magic "(\w+)" @(\d+)/))) header.push({ key: 'magic', type: 'magic', at: Number(m[2]), value: m[1] });
  else if ((m = p.match(/^(.+?) ([ui](?:8|16|32)) @(\d+)/))) header.push({ key: snake(m[1]), type: m[2], at: Number(m[3]) });
  else if ((m = p.match(/^(\d+) reserved$/))) header.push({ key: 'reserved', type: 'pad', at: -1, bytes: Number(m[1]) });
  else errors.push(`LF02: cannot read '${p}'`);
}
{
  let at = 0;
  for (const f of header) {
    const len = f.type === 'magic' ? f.value.length : f.type === 'pad' ? f.bytes : SIZE[f.type];
    if (f.at === -1) f.at = at;
    if (f.at !== at) errors.push(`LF02: ${f.key} is at ${f.at}, the fields before it end at ${at}`);
    at = f.at + len;
  }
  if (at !== headerLen) errors.push(`LF02: the fields end at ${at}, the header is ${headerLen} bytes`);
}
for (const k of ['magic', 'version', 'tier', 'sequence', 'start_odometer', 'uptime_at_start', 'unix_time_at_start', 'record_length', 'layout_crc_32'])
  if (!header.some((f) => f.key === k)) errors.push(`LF02: no ${k} field (the decoder reads it by that name)`);

const storeH = readFileSync(STORE_H, 'utf8');
function cstring(macro) {
  const m = storeH.match(new RegExp(`#define ${macro}\\s*\\\\?\\s*((?:"[^"]*"\\s*\\\\?\\s*)+)`));
  if (!m) {
    errors.push(`log_store.h: no ${macro}`);
    return '';
  }
  return [...m[1].matchAll(/"([^"]*)"/g)].map((x) => x[1]).join('');
}
const summaryLayout = cstring('LOG_SUMMARY_LAYOUT');
const fullLayout = cstring('LOG_FULL_LAYOUT');
const version = Number(storeH.match(/#define LOG_FORMAT_VERSION\s+(\d+)/)?.[1] ?? NaN);
if (!Number.isInteger(version)) errors.push('log_store.h: no LOG_FORMAT_VERSION');

const layoutBytes = (s) =>
  s.split(';').filter(Boolean).reduce((n, g) => {
    const [names, t] = g.split(':');
    const [, ty, x] = t.match(/^([ui]\d+)(?:x(\d+))?$/) ?? [];
    return n + names.split(',').length * SIZE[ty] * Number(x ?? 1);
  }, 0);
const summaryLen = Number((lf.LF03?.layout ?? '').match(/of (\d+) bytes/)?.[1] ?? NaN);
const fullLen = Number((lf.LF05?.layout ?? '').match(/(\d+)-byte records/)?.[1] ?? NaN);
const thinRow = Number((lf.LF04?.layout ?? '').match(/one (\d+)-byte record/)?.[1] ?? NaN);
if (layoutBytes(summaryLayout) !== summaryLen) errors.push(`LF03 says ${summaryLen} bytes, LOG_SUMMARY_LAYOUT lays out ${layoutBytes(summaryLayout)}`);
if (layoutBytes(fullLayout) !== fullLen) errors.push(`LF05 says ${fullLen} bytes, LOG_FULL_LAYOUT lays out ${layoutBytes(fullLayout)}`);
if (thinRow !== thinLen) errors.push(`LF04 says ${thinRow}-byte records, log_channels sums to ${thinLen}`);

if (errors.length) {
  for (const e of errors) console.error('gen-log-tables:', e);
  process.exit(1);
}

// ---------------------------------------------------------------- the file
const j = (x) => JSON.stringify(x);
const text = `// GENERATED by scripts/gen-log-tables.mjs - do not edit. \`npm run gen:logs\` rewrites it from the
// record (rx7.py export: 01-electrical log_channels, log_link, log_files, params) and the
// firmware's icu/log_store.h (LOG_SUMMARY_LAYOUT, LOG_FULL_LAYOUT, LOG_FORMAT_VERSION);
// \`npm run gen:logs -- --check\` fails when it is stale.

export type Int = 'u8' | 'i8' | 'u16' | 'i16' | 'u32' | 'i32';

/** One log_channels row: its bytes are \`count\` values of \`type\`, little-endian (LF04). */
export interface Channel {
  id: string;
  name: string;
  bytes: number;
  type: Int;
  count: number;
  /** the value of one count, in \`unit\` */
  scale: number;
  unit: string;
  /** value: a number; state: a code as the frame; bitfield: bits as the frame */
  kind: 'value' | 'state' | 'bitfield';
  /** the raw value meaning "not seen in this second" (LF04), or null */
  blank: number | null;
}

export const CHANNELS: readonly Channel[] = [
${channels.map((c) => `  ${j(c)},`).join('\n')}
];

/** params log_thin_bytes_per_s, and log_channels summed (they agree, or this file is not written) */
export const THIN_LEN = ${thinLen};

/** log_link LL01-LL10, LL18 */
export const LINK = {
  name: ${j(name[1])},
  protocol: ${protocol},
  mtu: ${mtu},
  timeSlackS: ${timeSlack},
  uuid: ${j({ service: svc[0], ...uuid })},
  /** the six opcodes the control characteristic takes (LL05-LL08), and nothing else */
  op: ${j(ops)},
  opFields: ${j(opFields)},
  info: ${j(info)},
  item: ${j(item)},
  status: ${j(status)},
  dataHead: ${j(dataHead)},
  tier: ${j(tiers)},
  state: ${j(states)},
  err: ${j(errs)},
} as const;

/** log_files LF02-LF05 and log_store.h */
export const FILES = {
  version: ${version},
  headerLen: ${headerLen},
  header: ${j(header)},
  summaryLen: ${summaryLen},
  fullLen: ${fullLen},
  summaryLayout: ${j(summaryLayout)},
  fullLayout: ${j(fullLayout)},
} as const;
`;

if (check) {
  let now = '';
  try {
    now = readFileSync(OUT, 'utf8');
  } catch {
    /* absent counts as stale */
  }
  if (now !== text) {
    console.error(`gen-log-tables: ${OUT} is stale - run npm run gen:logs`);
    process.exit(1);
  }
  console.log('gen-log-tables: up to date');
} else {
  writeFileSync(OUT, text);
  console.log(`gen-log-tables: ${OUT} written - ${channels.length} channels, ${thinLen} bytes a record`);
}

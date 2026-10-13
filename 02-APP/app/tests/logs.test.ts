// Connect and log (02-APP BL2) and the log pipeline (BL3): the decoder against the record's
// layouts and against files the ICU firmware itself wrote, the one write, and the pull
// against a stand-in ICU - resume at an offset, a bad CRC never acknowledged, a protocol it
// does not know refused.
import { describe, expect, it } from 'vitest';
import summaryBin from './fixtures/icu-drive/00000001/summary.bin?inline';
import thinBin from './fixtures/icu-drive/00000001/thin.bin?inline';
import fullBin from './fixtures/icu-drive/00000001/full.bin?inline';
import { CHANNELS, FILES, LINK, THIN_LEN } from '../src/lib/logs/layout.generated';
import { crc32, crc32Text, fieldsLen } from '../src/lib/logs/bytes';
import {
  COLUMNS, LogFormatError, SUMMARY_FIELDS, decodeFull, decodeHeader, decodeSummary, decodeThin, layoutCrc, thinLayoutString, value,
} from '../src/lib/logs/format';
import * as P from '../src/lib/logs/protocol';
import { guardControl, RefusedWrite } from '../src/lib/logs/transport';
import { packMv, mfrHex } from '../src/lib/logs/ionic';
import * as synth from '../src/lib/logs/synth';
import { FakeIcu, type FakeDrive } from '../src/lib/logs/fake';
import { memoryFiles } from '../src/lib/logs/files';
import { memoryState } from '../src/lib/logs/state';
import { connectAndLog, PullError } from '../src/lib/logs/pull';
import { digest, driveAnswer, fileDrives, type DriveAnswer } from '../src/lib/logs/pipeline';

// the firmware's files, as data: URLs (Vite's ?inline)
const BIN: Record<string, string> = { 'summary.bin': summaryBin, 'thin.bin': thinBin, 'full.bin': fullBin };
const fixture = (name: string) => Uint8Array.from(atob(BIN[name].split(',')[1]), (c) => c.charCodeAt(0));

describe('the tables generated from the record', () => {
  it('lays out the thinned record as log_channels says', () => {
    expect(CHANNELS).toHaveLength(53);
    expect(CHANNELS.map((c) => c.id)).toEqual(Array.from({ length: 53 }, (_, i) => `LC${String(i + 1).padStart(2, '0')}`));
    expect(THIN_LEN).toBe(137);
    expect(COLUMNS.at(-1)!.at + 1).toBe(137);
    expect(thinLayoutString().startsWith('LC01:4;LC02:4;LC03:1;')).toBe(true);
    expect(thinLayoutString().endsWith('LC52:1;LC53:1;')).toBe(true);
  });
  it('matches the firmware struct sizes (log_link.h static_asserts)', () => {
    expect(P.INFO_LEN).toBe(23);
    expect(P.ITEM_LEN).toBe(27);
    expect(P.STATUS_LEN).toBe(19);
    expect(fieldsLen(LINK.opFields.OPEN)).toBe(9);
    expect(fieldsLen(LINK.opFields.ACK)).toBe(9);
    expect(fieldsLen(SUMMARY_FIELDS)).toBe(105);
    expect(FILES.headerLen).toBe(32);
    expect(FILES.fullLen).toBe(15);
  });
  it('names the six opcodes and nothing else', () => {
    expect(LINK.op).toEqual({ LIST: 0x01, OPEN: 0x02, ACK: 0x03, ABORT: 0x04, SET_TIME: 0x10, PING: 0x7f });
    expect(LINK.uuid.control).toBe('7a1e0004-5b2c-4d3e-9f10-8a7b6c5d4e3f');
    expect(LINK.protocol).toBe(1);
  });
});

describe('CRC-32', () => {
  it('is zlib CRC-32, as ll_crc32', () => {
    expect(crc32Text('123456789')).toBe(0xcbf43926);
    expect(crc32(new Uint8Array(0))).toBe(0);
  });
});

describe('the files the ICU firmware wrote (scripts/icu-drive.cpp, LogStore)', () => {
  it('reads the header and refuses nothing it wrote', () => {
    for (const [name, tier] of [['summary.bin', 0], ['thin.bin', 1], ['full.bin', 2]] as const) {
      const h = decodeHeader(fixture(name), tier);
      expect(h.seq).toBe(1);
      expect(h.startOdoX10).toBe(1534567);
      expect(h.uptimeStart).toBe(4200);
      expect(h.unixStart).toBe(0);
      expect(h.layoutCrc).toBe(layoutCrc(tier));
    }
  });
  it('reads log_summary_t field for field', () => {
    const { summary: s } = decodeSummary(fixture('summary.bin'));
    expect(s).toMatchObject({
      seq: 1, start_odo: 1534567, end_odo: 1534576, duration_s: 90, unix_start: 0, uptime_start: 4200,
      time_set_unix: 1791820800, time_set_uptime: 34200, time_set_prev: 0,
      max_rpm: 3519, max_mph: 30, max_water_c: 90, max_oil_temp_c: 92, max_oil_cbar: 340, min_oil_cbar: 251,
      max_volts_x10: 138, min_volts_x10: 138, max_lat_g: 25, max_accel_g: 30, max_brake_g: 40,
      max_pitch_up: 3, max_pitch_down: -2, runtime_s: 90, idle_s: 9, distance_x10: 9, rev_s: 0, hot_s: 0, low_oil_s: 0,
      cold_starts: 1, fuel_pct_start: 62, fuel_pct_now: 61, dist_at_fuel_mark: 0, fuse_trips: 2, last_trip_ch: 5,
      last_trip_s: 61, sensor_faults: 0, can_timeouts: 3,
    });
  });
  it('reads the thinned record as LogThinAccum filled it', () => {
    const { records, tail } = decodeThin(fixture('thin.bin'));
    expect(records).toHaveLength(90);
    expect(tail).toBe(0);
    const r = records[0];
    expect(r.LC01).toBe(5200);
    expect(r.LC02).toBe(1534567);
    expect(records[89].LC02).toBe(1534576);
    expect(r.LC18).toBe(839); // the mean of 830..849
    expect(r.LC19).toBe(849); // the peak
    expect(r.LC10).toBe(13801);
    expect(r.LC11).toBe(251);
    expect(r.LC20).toBe(60);
    expect(r.LC22).toBe(251);
    const cabin = COLUMNS.find((c) => c.key === 'LC40')!;
    expect(value(cabin, r.LC40)).toBeNull(); // 0x300 never seen: TEMP_INVALID, a blank
    expect([r['LC50.0'], r['LC50.1'], r['LC50.2']]).toEqual([-15, 30, 98]);
    expect([r['LC51.0'], r['LC51.1'], r['LC51.2']]).toEqual([15, 30, 0]);
    expect(r.LC52).toBe(40);
    expect(r.LC53).toBe(2);
  });
  it('reads the full log', () => {
    const { records } = decodeFull(fixture('full.bin'));
    expect(records).toHaveLength(1800);
    expect(records[0]).toMatchObject({ ms: 4200, id: 0x200, dlc: 8, extended: false, imu: false });
    expect(records[0].data[0] | (records[0].data[1] << 8)).toBe(830);
  });
  it('refuses a header it was not built for', () => {
    const f = fixture('thin.bin');
    const crc = f.slice();
    crc[24] ^= 1;
    expect(() => decodeHeader(crc)).toThrow(LogFormatError);
    expect(() => decodeHeader(crc)).toThrow(/layout CRC/);
    const magic = f.slice();
    magic[0] = 0;
    expect(() => decodeHeader(magic)).toThrow(/magic/);
    const ver = f.slice();
    ver[4] = 9;
    expect(() => decodeHeader(ver)).toThrow(/version/);
    expect(() => decodeHeader(f, 0)).toThrow(/thin header/);
    expect(() => decodeHeader(f.subarray(0, 10))).toThrow(/shorter/);
  });
});

describe('a synthetic drive written to the same layouts', () => {
  const d: synth.SynthDrive = { seq: 7, seconds: 600, startOdoX10: 1534000, unixStart: 0, uptimeStart: 3000, speedX10PerS: 0.05 };
  it('round-trips', () => {
    const { header, records } = decodeThin(synth.thin(d));
    expect(header.seq).toBe(7);
    expect(records).toHaveLength(600);
    expect(records[599].LC02).toBe(1534030);
    expect(decodeSummary(synth.summary(d)).summary.distance_x10).toBe(30);
    expect(decodeFull(synth.full(d)).records[9].imu).toBe(true);
  });
  it('digests every channel and files one drives row', () => {
    const g = digest(synth.thin(d), synth.summary(d), { seq: 7, item: {} as P.Item, held: [0, 0, 0], acked: [null, null, null] }, 1_791_900_000, 1_791_999_999)!;
    expect(g.miles).toBe(3);
    expect(g.endOdoX10).toBe(1534030);
    expect(g.durationS).toBe(600);
    expect(g.approx).toBe(true);
    expect(g.startUnix).toBe(1_791_900_000 - 600);
    expect(g.columns.LC20).toMatchObject({ unit: '°C', min: 41, max: 88 });
    expect(g.columns.LC40).toMatchObject({ n: 0, blanks: 600, mean: null });
    expect(g.columns.LC10.mean).toBeCloseTo(13903, 0);
    expect(g.columns['LC31.3']).toMatchObject({ name: 'Cell voltages 1-4 [4]', min: 3314, max: 3314 });
    const a = driveAnswer(g) as DriveAnswer;
    expect(a.kind).toBe('drive');
    expect(a.area).toBe('00-CAR');
    expect(a.choice).toBe('153403');
    expect(a.target).toMatch(/^drive-\d{8}T\d{6}$/);
    expect(a.text).toMatch(/3\.0 mi in 10 min/);
    expect(a.text).toMatch(/Date approximate/);
  });
  it('files nothing for a key turned on to pull', () => {
    const still = { ...d, speedX10PerS: 0 };
    const g = digest(synth.thin(still), synth.summary(still), { seq: 7, item: {} as P.Item, held: [0, 0, 0], acked: [null, null, null] }, null, 1_791_999_999)!;
    expect(driveAnswer(g)).toHaveProperty('skip');
  });
});

describe('the one write', () => {
  it('encodes each request byte for byte', () => {
    expect([...P.open(5, 1, 1000)]).toEqual([0x02, 5, 0, 0, 0, 1, 0xe8, 3, 0, 0]);
    expect([...P.ack(5, 1, 0xcbf43926)]).toEqual([0x03, 5, 0, 0, 0, 1, 0x26, 0x39, 0xf4, 0xcb]);
    expect([...P.list(0)]).toEqual([0x01, 0, 0, 0, 0]);
    expect([...P.setTime(0x6a000000)]).toEqual([0x10, 0, 0, 0, 0x6a]);
    expect([...P.abort()]).toEqual([0x04]);
    expect([...P.ping()]).toEqual([0x7f]);
  });
  it('refuses anything but the six with their fields', () => {
    expect(() => guardControl(new Uint8Array([0x20, 0, 4]))).toThrow(RefusedWrite); // CREDIT is the C3's
    expect(() => guardControl(new Uint8Array([0x21, 0, 0, 0, 0, 0, 0]))).toThrow(RefusedWrite);
    expect(() => guardControl(new Uint8Array([0x01, 0, 0, 0]))).toThrow(RefusedWrite); // short
    expect(() => guardControl(new Uint8Array([0x02, 1, 0, 0, 0, 3, 0, 0, 0, 0]))).toThrow(RefusedWrite); // tier 3
    expect(() => guardControl(new Uint8Array([]))).toThrow(RefusedWrite);
    expect(guardControl(P.ping())).toEqual(P.ping());
  });
  it('sets the clock only when it is unset or off', () => {
    const info = P.decodeInfo(new Uint8Array(23));
    expect(P.timeWanted(info, 1_791_820_800)).toBe(true);
    expect(P.timeWanted({ ...info, rtc_set: 1, unix_time: 1_791_820_799 }, 1_791_820_800)).toBe(false);
    expect(P.timeWanted({ ...info, rtc_set: 1, unix_time: 1_791_820_790 }, 1_791_820_800)).toBe(true);
  });
});

describe("the Ionic battery's advertisement (D-330, BL5)", () => {
  it('reads pack millivolts from the company-ID slot, as ionic_adv_pack_mv', () => {
    expect(packMv({ 13012: [0x11, 0x22] })).toEqual({ mv: 13012, rest: [0x11, 0x22] });
    expect(packMv({ 76: [1, 2, 3] })).toBeNull(); // Apple's company id is not a voltage
    expect(packMv({ 16001: [] })).toBeNull();
    expect(packMv(undefined)).toBeNull();
    expect(mfrHex({ 13012: [0x11] })).toEqual(['d4 32 11']);
  });
});

// ------------------------------------------------------------------------------- the pull
function drives(): FakeDrive[] {
  const a: synth.SynthDrive = { seq: 3, seconds: 400, startOdoX10: 1534000, unixStart: 1_791_800_000, uptimeStart: 3000, speedX10PerS: 0.05 };
  const b: synth.SynthDrive = { seq: 4, seconds: 300, startOdoX10: 1534020, unixStart: 0, uptimeStart: 2500, speedX10PerS: 0.04 };
  return [a, b].map((s) => ({ seq: s.seq, files: synth.files(s), startOdoX10: s.startOdoX10, startUnix: s.unixStart }));
}
const fast = { silenceMs: 300, ackMs: 40, scanMs: 100, flushBytes: 4096, now: () => 1_791_820_800_000 };
const opsOf = (w: Uint8Array[]) => w.map((b) => b[0]);
/** OPEN or ACK writes as { seq, tier, offset-or-crc } */
const fields = (w: Uint8Array[], op: number) =>
  w.filter((b) => b[0] === op).map((b) => {
    const v = new DataView(b.buffer, b.byteOffset, b.byteLength);
    return { seq: v.getUint32(1, true), tier: b[5], n: v.getUint32(6, true) };
  });

describe('the pull, against a stand-in ICU', () => {
  it('pulls the summary and thin of every drive, checks the CRC, acknowledges, and never the full log', async () => {
    const icu = new FakeIcu({ drives: drives(), uptimeMs: 330_000 });
    const files = memoryFiles();
    const state = memoryState();
    const r = await connectAndLog({ transport: icu, files, state, ...fast });
    expect(r.problems).toEqual([]);
    expect(r.acked).toEqual(['3 summary', '3 thin', '4 summary', '4 thin']);
    for (const d of icu.o.drives) {
      expect(await files.read(d.seq, 'summary.bin')).toEqual(d.files[0]);
      expect(await files.read(d.seq, 'thin.bin')).toEqual(d.files[1]);
      expect(await files.size(d.seq, 'full.bin')).toBe(0);
      expect(d.pulled![1]).toEqual({ len: d.files[1].length, crc: crc32(d.files[1]) });
      expect(d.pulled![2]).toBeNull();
    }
    // SET_TIME first (the clock was unset), then LIST, then OPEN / ACK pairs - nothing else
    expect(opsOf(icu.writes)).toEqual([0x10, 0x01, 0x02, 0x03, 0x02, 0x03, 0x02, 0x03, 0x02, 0x03]);
    expect(icu.writes.every((w) => P.controlCheck(w) >= 0)).toBe(true);
    expect(icu.unixTime).toBe(1_791_820_800);
    expect(state.now.drives[4].openAt?.uptimeMs).toBe(330_000);
    // a second press finds nothing new
    const again = await connectAndLog({ transport: icu, files, state, ...fast });
    expect(again.drives).toEqual([]);
  });

  it('carries a cut pull on from the last byte held (D-483)', async () => {
    const ds = drives();
    const files = memoryFiles();
    const state = memoryState();
    const cut = new FakeIcu({ drives: ds, rtcSet: true, unixTime: 1_791_820_800, cutAfter: 2000 });
    await expect(connectAndLog({ transport: cut, files, state, ...fast })).rejects.toMatchObject({ kind: 'link' });
    const held = await files.size(3, 'thin.bin');
    expect(held).toBeGreaterThan(0);
    expect(held).toBeLessThan(ds[0].files[1].length);
    expect(state.now.drives[3].held[1]).toBe(held);
    expect(ds[0].pulled![1]).toBeNull(); // nothing acknowledged on a part

    const next = new FakeIcu({ drives: ds, rtcSet: true, unixTime: 1_791_820_800 });
    const r = await connectAndLog({ transport: next, files, state, ...fast });
    expect(fields(next.writes, 0x02)).toContainEqual({ seq: 3, tier: 1, n: held }); // opened where it stopped
    expect(opsOf(next.writes)[0]).toBe(0x01); // the clock was set: no SET_TIME
    expect(await files.read(3, 'thin.bin')).toEqual(ds[0].files[1]);
    expect(r.acked).toContain('3 thin');
  });

  it('re-asks for a chunk that went missing', async () => {
    const ds = drives();
    const files = memoryFiles();
    const icu = new FakeIcu({ drives: ds, rtcSet: true, unixTime: 1_791_820_800, dropAt: 5000 });
    const r = await connectAndLog({ transport: icu, files, state: memoryState(), ...fast });
    expect(r.problems).toEqual([]);
    expect(await files.read(3, 'thin.bin')).toEqual(ds[0].files[1]);
    expect(icu.writes.filter((w) => w[0] === 0x02).length).toBeGreaterThan(4);
  });

  it('never acknowledges a CRC that does not match, and starts that tier again', async () => {
    const ds = drives();
    const files = memoryFiles();
    const icu = new FakeIcu({ drives: ds, rtcSet: true, unixTime: 1_791_820_800, badCrc: { seq: 3, tier: 1, times: 1 } });
    const r = await connectAndLog({ transport: icu, files, state: memoryState(), ...fast });
    const acks = fields(icu.writes, 0x03);
    expect(acks).toHaveLength(4);
    expect(acks.every((a) => a.n === crc32(ds.find((d) => d.seq === a.seq)!.files[a.tier]))).toBe(true);
    expect(r.problems.join(' ')).toMatch(/not acknowledged, pulled again/);
    expect(ds[0].pulled![1]).toEqual({ len: ds[0].files[1].length, crc: crc32(ds[0].files[1]) });
  });

  it('leaves a tier unacknowledged when the CRC keeps failing', async () => {
    const ds = drives();
    const icu = new FakeIcu({ drives: ds, rtcSet: true, unixTime: 1_791_820_800, badCrc: { seq: 3, tier: 1, times: 9 } });
    const r = await connectAndLog({ transport: icu, files: memoryFiles(), state: memoryState(), ...fast });
    expect(ds[0].pulled![1]).toBeNull();
    expect(fields(icu.writes, 0x03).some((a) => a.seq === 3 && a.tier === 1)).toBe(false);
    expect(r.acked).toContain('4 thin');
  });

  it('refuses an ICU speaking another protocol, before writing anything', async () => {
    const icu = new FakeIcu({ drives: drives(), protocol: 2 });
    await expect(connectAndLog({ transport: icu, files: memoryFiles(), state: memoryState(), ...fast })).rejects.toMatchObject({ kind: 'protocol' });
    expect(icu.writes).toEqual([]);
    expect(icu.connected).toBe(false);
  });

  it('says the key has to be on when the ICU is not found', async () => {
    const icu = new FakeIcu({ drives: drives(), asleep: true });
    const e = await connectAndLog({ transport: icu, files: memoryFiles(), state: memoryState(), ...fast }).catch((x) => x);
    expect(e).toBeInstanceOf(PullError);
    expect(e.kind).toBe('not-found');
    expect(e.message).toMatch(/ACC or RUN/);
  });

  it('pulls the full log only when asked, drive by drive', async () => {
    const ds = drives();
    const files = memoryFiles();
    const state = memoryState();
    const icu = new FakeIcu({ drives: ds, rtcSet: true, unixTime: 1_791_820_800 });
    await connectAndLog({ transport: icu, files, state, ...fast });
    const r = await connectAndLog({ transport: icu, files, state, ...fast, full: [3], thin: false });
    expect(r.acked).toEqual(['3 full']);
    expect(await files.read(3, 'full.bin')).toEqual(ds[0].files[2]);
    expect(await files.size(4, 'full.bin')).toBe(0);
  });
});

describe('the pipeline after a pull', () => {
  it('writes one kind=drive inbox row per drive, once', async () => {
    const ds = drives();
    const files = memoryFiles();
    const state = memoryState();
    const icu = new FakeIcu({ drives: ds, uptimeMs: 330_000 });
    await connectAndLog({ transport: icu, files, state, ...fast });
    const saved: DriveAnswer[] = [];
    const out = await fileDrives({ files, state, known: new Set(), save: async (a) => (saved.push(a), true) });
    expect(out.problems).toEqual([]);
    expect(saved).toHaveLength(2);
    const [a, b] = saved;
    expect(a.choice).toBe('153402'); // 1534000 + 400 s × 0.05 = 1534020 (0.1 mi)
    expect(a.at.slice(0, 19)).toBe(localNoOffset(1_791_800_000 + 400));
    expect(a.text).not.toMatch(/approximate/);
    expect(b.choice).toBe('153403');
    expect(b.text).toMatch(/approximate/); // drive 4 had no clock: dated from the pull and the uptime
    // drive 4 was the open one at the pull: it started 330 s - 2.5 s before the pull's moment
    expect(state.now.drives[4].brief?.start.slice(0, 19)).toBe(localNoOffset(Math.round(1_791_820_800 - (330_000 - 2500) / 1000)));
    expect(new TextDecoder().decode(await files.read(3, 'digest.json'))).toMatch(/"LC18"/);
    const again = await fileDrives({ files, state, known: new Set(saved.map((x) => x.target)), save: async (x) => (saved.push(x), true) });
    expect(again.written).toEqual([]);
    expect(saved).toHaveLength(2);
  });
});

function localNoOffset(unix: number) {
  const d = new Date(unix * 1000);
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

import { describe, expect, it } from 'vitest';
import { base64, wanted } from '../src/lib/platform/github';
import { overlay, settled, type Outgoing, type Sent } from '../src/lib/platform/phone';
import type { Answer, Snapshot } from '../src/lib/model';

const answer = (target: string, extra: Partial<Answer> = {}): Answer => ({
  area: '02-electrical', id: `${target}~phone`, target, kind: 'block', choice: 'a', text: '', context: '', device: 'phone', at: '2026-09-24T20:00:00-06:00', ...extra,
});
const snap = (inbox: Answer[]): Snapshot => ({
  version: 1, generated: '', record: { valid: true, problems: [] }, areas: [], picks: [], work: [], decisions: [], log: [], tables: [], photos: [],
  inbox, blocks: ['01.29', '01.30'].map((id) => ({ area: '02-electrical', id, answered: false }) as Snapshot['blocks'][number]),
});

describe('the phone lays its unsent answers over the record', () => {
  it('an unsent answer shows as answered, marked pending', () => {
    const out: Outgoing[] = [{ op: 'put', path: 'x', answer: answer('01.29'), body: '' }];
    const s = overlay(snap([]), out);
    expect(s.inbox).toHaveLength(1);
    expect(s.inbox[0].pending).toBe(true);
    expect(s.blocks.find((b) => b.id === '01.29')?.answered).toBe(true);
    expect(s.blocks.find((b) => b.id === '01.30')?.answered).toBe(false);
  });
  it('a withdrawal not yet sent hides the answer', () => {
    const s = overlay(snap([answer('01.30')]), [{ op: 'delete', path: 'x', answer: answer('01.30') }]);
    expect(s.inbox).toHaveLength(0);
    expect(s.blocks.every((b) => !b.answered)).toBe(true);
  });
  it('a newer answer from this phone replaces the one on GitHub', () => {
    const s = overlay(snap([answer('01.29', { choice: 'b' })]), [{ op: 'put', path: 'x', answer: answer('01.29', { choice: 'a' }) }]);
    expect(s.inbox.map((a) => a.choice)).toEqual(['a']);
  });
});

describe('a sent answer stays in view until the published export holds it (D-511)', () => {
  const sent = (target: string, extra: Partial<Sent> = {}): Sent => ({
    op: 'put', answer: answer(target, { pending: false }), commit: 'c1', date: '2026-10-13T12:00:00Z', ...extra,
  });
  it('is shown, as sent, while the export does not hold it yet', () => {
    const s = overlay(snap([]), [], [sent('01.29')]);
    expect(s.inbox.map((a) => [a.target, a.pending])).toEqual([['01.29', false]]);
    expect(s.blocks.find((b) => b.id === '01.29')?.answered).toBe(true);
  });
  it('a sent withdrawal hides the answer the export still holds', () => {
    expect(overlay(snap([answer('01.30')]), [], [sent('01.30', { op: 'delete' })]).inbox).toHaveLength(0);
  });
  it('is let go once the export is of its commit or a later one', () => {
    const now = Date.parse('2026-10-13T12:30:00Z');
    expect(settled(sent('01.29'), undefined, now)).toBe(false);
    expect(settled(sent('01.29'), { sha: 'c0', date: '2026-10-13T11:59:00Z', built: '' }, now)).toBe(false);
    expect(settled(sent('01.29'), { sha: 'c1', date: '2026-10-13T12:00:00Z', built: '' }, now)).toBe(true);
    expect(settled(sent('01.29'), { sha: 'c2', date: '2026-10-13T12:05:00Z', built: '' }, now)).toBe(true);
    expect(settled(sent('01.29'), undefined, Date.parse('2026-10-16T00:00:00Z'))).toBe(true);
  });
});

describe('what the phone fetches', () => {
  it('fetches rx7.py, every table and inbox file, and only the archive ids it needs', () => {
    expect(wanted('tools/rx7.py')).toBe('text');
    expect(wanted('02-PROJECTS/02-electrical/data/work.csv')).toBe('text');
    expect(wanted('02-APP/data/work.csv')).toBe('text');
    expect(wanted('02-APP/app/src/main.ts')).toBeNull();
    expect(wanted('02-PROJECTS/02-electrical/data/inbox/01.29~phone.csv')).toBe('text');
    expect(wanted('00-CAR/data/vehicle.csv')).toBe('text');
    expect(wanted('99-ARCHIVE/Electrical/data/decisions.csv')).toBe('text');
    expect(wanted('99-ARCHIVE/x/D-123.md')).toBe('name');
    expect(wanted('00-CAR/library/docs/big.pdf')).toBeNull();
    expect(wanted('02-PROJECTS/02-electrical/00-design/firmware/main.cpp')).toBeNull();
  });
  it('sends his words as UTF-8, whatever they hold', () => {
    const words = 'µ ✓ “quotes” — 55.2 mm 🚗';
    expect(new TextDecoder().decode(Uint8Array.from(atob(base64(words)), (c) => c.charCodeAt(0)))).toBe(words);
  });
});

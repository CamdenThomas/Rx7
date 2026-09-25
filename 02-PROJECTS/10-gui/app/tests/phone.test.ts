import { describe, expect, it } from 'vitest';
import { base64, wanted } from '../src/lib/platform/github';
import { overlay, type Outgoing } from '../src/lib/platform/phone';
import type { Answer, Snapshot } from '../src/lib/model';

const answer = (target: string, extra: Partial<Answer> = {}): Answer => ({
  area: '00-electrical', id: `${target}~phone`, target, kind: 'block', choice: 'a', text: '', context: '', device: 'phone', at: '2026-09-24T20:00:00-06:00', ...extra,
});
const snap = (inbox: Answer[]): Snapshot => ({
  version: 1, generated: '', record: { valid: true, problems: [] }, areas: [], picks: [], work: [], decisions: [], log: [], tables: [], photos: [], next: {},
  inbox, blocks: ['00.29', '00.30'].map((id) => ({ area: '00-electrical', id, answered: false }) as Snapshot['blocks'][number]),
});

describe('the phone lays its unsent answers over the record', () => {
  it('an unsent answer shows as answered, marked pending', () => {
    const out: Outgoing[] = [{ op: 'put', path: 'x', answer: answer('00.29'), body: '' }];
    const s = overlay(snap([]), out);
    expect(s.inbox).toHaveLength(1);
    expect(s.inbox[0].pending).toBe(true);
    expect(s.blocks.find((b) => b.id === '00.29')?.answered).toBe(true);
    expect(s.blocks.find((b) => b.id === '00.30')?.answered).toBe(false);
  });
  it('a withdrawal not yet sent hides the answer', () => {
    const s = overlay(snap([answer('00.30')]), [{ op: 'delete', path: 'x', answer: answer('00.30') }]);
    expect(s.inbox).toHaveLength(0);
    expect(s.blocks.every((b) => !b.answered)).toBe(true);
  });
  it('a newer answer from this phone replaces the one on GitHub', () => {
    const s = overlay(snap([answer('00.29', { choice: 'b' })]), [{ op: 'put', path: 'x', answer: answer('00.29', { choice: 'a' }) }]);
    expect(s.inbox.map((a) => a.choice)).toEqual(['a']);
  });
});

describe('what the phone fetches', () => {
  it('fetches rx7.py, every table and inbox file, and only the archive ids it needs', () => {
    expect(wanted('tools/rx7.py')).toBe('text');
    expect(wanted('02-PROJECTS/00-electrical/data/work.csv')).toBe('text');
    expect(wanted('02-PROJECTS/00-electrical/data/inbox/00.29~phone.csv')).toBe('text');
    expect(wanted('00-CAR/data/vehicle.csv')).toBe('text');
    expect(wanted('99-ARCHIVE/Electrical/data/decisions.csv')).toBe('text');
    expect(wanted('99-ARCHIVE/x/D-123.md')).toBe('name');
    expect(wanted('01-REFERENCE/manuals/big.pdf')).toBeNull();
    expect(wanted('02-PROJECTS/00-electrical/00-design/firmware/main.cpp')).toBeNull();
  });
  it('sends his words as UTF-8, whatever they hold', () => {
    const words = 'µ ✓ “quotes” — 55.2 mm 🚗';
    expect(new TextDecoder().decode(Uint8Array.from(atob(base64(words)), (c) => c.charCodeAt(0)))).toBe(words);
  });
});

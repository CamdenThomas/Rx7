import { describe, expect, it } from 'vitest';
import { day, miles, pieces, value } from '../src/lib/manual';

describe('the Manual formats what rx7.py hands it', () => {
  it('writes a unit once', () => {
    expect(value({ value: '9.4:1', unit: '' })).toBe('9.4:1');
    expect(value({ value: '202', unit: 'mm' })).toBe('202 mm');
    expect(value({ value: '50.80 (2.0) mm', unit: 'mm (in)' })).toBe('50.80 (2.0) mm');
    expect(value({ value: '100 @ 6000', unit: 'hp @ rpm' })).toBe('100 hp @ 6000 rpm');
  });
  it('reads miles and dates', () => {
    expect(miles(157200)).toBe('157,200 mi');
    expect(miles('')).toBe('');
    expect(day('2026-07')).toBe('Jul 2026');
    expect(day('2026-07-14')).toBe('14 Jul 2026');
  });
  it('cuts a cell at its web addresses', () => {
    expect(pieces('Atkins 360 (https://www.atkinsrotary.com/contact-us/)')).toEqual([
      { text: 'Atkins 360 (' },
      { text: 'atkinsrotary.com/contact-us', url: 'https://www.atkinsrotary.com/contact-us/' },
      { text: ')' },
    ]);
  });
});

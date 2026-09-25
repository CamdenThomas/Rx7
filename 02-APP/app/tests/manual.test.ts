import { describe, expect, it } from 'vitest';
import { boxes, day, hull, miles, pieces, places, project, value } from '../src/lib/manual';

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

describe('the car view', () => {
  it('reads boxes and places', () => {
    expect(boxes('0 1 0 1 0 1')[0]).toHaveLength(8);
    expect(boxes('0 1 0 1 0 1; 2 3 2 3 2 3')).toHaveLength(2);
    expect(boxes('')).toEqual([]);
    expect(places('1 2 3; 4 5 6')).toEqual([[1, 2, 3], [4, 5, 6]]);
  });
  it('projects through the camera and wraps a hull', () => {
    const flat = { width: 200, height: 100, matrix: [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]] };
    expect(project(flat, [0, 0, 0])).toEqual([100, 50]);
    expect(project(flat, [1, 1, 0])).toEqual([200, 0]);
    const h = hull([[0, 0], [2, 0], [1, 1], [2, 2], [0, 2]]);
    expect(h).toHaveLength(4);
    expect(h).not.toContainEqual([1, 1]);
  });
});

// Lookups over the Manual as rx7.py exports it (D-417). Nothing here decides a fact: each
// function finds a row the export already holds, or formats one of its numbers.

import { app } from './app.svelte';
import type { Manual, ManualPart, ManualSpec, ManualSystem } from './model';

export const manual = (): Manual | undefined => app.snapshot?.manual;

export const part = (id: string): ManualPart | undefined => manual()?.parts.find((p) => p.id === id);
export const system = (id: string): ManualSystem | undefined => manual()?.systems.find((s) => s.id === id);
export const spec = (id: string): ManualSpec | undefined => manual()?.specs.find((s) => s.id === id);

/** 157200 → "157,200 mi" */
export function miles(n: number | string | null | undefined): string {
  const v = typeof n === 'string' ? Number(n) : n;
  return v === null || v === undefined || Number.isNaN(v) || (typeof n === 'string' && !n.trim()) ? '' : `${v.toLocaleString('en-US')} mi`;
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** "2026-07" → "Jul 2026", "2026-07-14" → "14 Jul 2026" */
export function day(iso: string): string {
  const m = (iso ?? '').match(/^(\d{4})-(\d{2})(?:-(\d{2}))?/);
  if (!m) return iso ?? '';
  const mon = MONTHS[Number(m[2]) - 1] ?? m[2];
  return m[3] ? `${Number(m[3])} ${mon} ${m[1]}` : `${mon} ${m[1]}`;
}

/** A spec's value with its unit, when the unit is not already written into the value. */
export function value(s: { value: string; unit: string }): string {
  // A unit written as "mm (in)" is already in a value that reads "50.80 (2.0) mm".
  const head = s.unit.split(/[\s(]/)[0];
  // "100 @ 6000" in "hp @ rpm" reads "100 hp @ 6000 rpm".
  const vs = s.value.split(' @ ');
  const us = s.unit.split(' @ ');
  if (vs.length > 1 && vs.length === us.length) return vs.map((v, i) => `${v} ${us[i]}`).join(' @ ');
  return s.unit && !s.value.includes(s.unit) && !(head && s.value.includes(head)) ? `${s.value} ${s.unit}` : s.value;
}

/** The source ids of a spec (S-002,S-003) with their titles, for a tooltip or a list. */
export function sources(cell: string): { id: string; title: string; url: string }[] {
  const m = manual();
  return (cell ?? '')
    .split(/[\s,;]+/)
    .filter((x) => /^S-\d+$/.test(x))
    .map((id) => ({ id, title: m?.sources[id]?.title ?? '', url: m?.sources[id]?.url ?? '' }));
}

/** A cell cut at its web addresses, so each can be shown as a link: "Atkins (https://…)". */
export function pieces(text: string): { text: string; url?: string }[] {
  const out: { text: string; url?: string }[] = [];
  let at = 0;
  for (const m of (text ?? '').matchAll(/https?:\/\/[^\s)]+/g)) {
    if (m.index > at) out.push({ text: text.slice(at, m.index) });
    out.push({ text: m[0].replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, ''), url: m[0] });
    at = m.index + m[0].length;
  }
  if (at < (text ?? '').length) out.push({ text: text.slice(at) });
  return out;
}

// ---- The car view (D-421): the renders carry their cameras in public/car/views.json.

export interface View {
  width: number;
  height: number;
  matrix: number[][];
}

/** A point on the model, in mm, to a pixel on the render: clip = matrix · [x y z 1]. */
export function project(v: View, [x, y, z]: number[]): [number, number] {
  const c = v.matrix.map((r) => r[0] * x + r[1] * y + r[2] * z + r[3]);
  return [((c[0] / c[3] + 1) / 2) * v.width, ((1 - c[1] / c[3]) / 2) * v.height];
}

/** "x0 x1 y0 y1 z0 z1; …" → the eight corners of each box. */
export function boxes(cell: string): number[][][] {
  return (cell ?? '')
    .split(';')
    .map((b) => b.trim().split(/\s+/).map(Number))
    .filter((n) => n.length === 6 && n.every(Number.isFinite))
    .map(([x0, x1, y0, y1, z0, z1]) => [x0, x1].flatMap((x) => [y0, y1].flatMap((y) => [z0, z1].map((z) => [x, y, z]))));
}

/** "x y z; …" → each place. */
export function places(cell: string): number[][] {
  return (cell ?? '')
    .split(';')
    .map((b) => b.trim().split(/\s+/).map(Number))
    .filter((n) => n.length === 3 && n.every(Number.isFinite));
}

/** The convex hull of some points, in order around it (monotone chain). */
export function hull(points: [number, number][]): [number, number][] {
  const p = [...points].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  if (p.length < 3) return p;
  const cross = (o: number[], a: number[], b: number[]) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const half = (pts: [number, number][]) => {
    const out: [number, number][] = [];
    for (const q of pts) {
      while (out.length >= 2 && cross(out[out.length - 2], out[out.length - 1], q) <= 0) out.pop();
      out.push(q);
    }
    return out.slice(0, -1);
  };
  return [...half(p), ...half([...p].reverse())];
}

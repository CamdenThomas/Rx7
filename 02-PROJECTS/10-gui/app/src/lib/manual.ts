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
  return s.unit && !s.value.includes(s.unit) ? `${s.value} ${s.unit}` : s.value;
}

/** The source ids of a spec (S-002,S-003) with their titles, for a tooltip or a list. */
export function sources(cell: string): { id: string; title: string; url: string }[] {
  const m = manual();
  return (cell ?? '')
    .split(/[\s,;]+/)
    .filter((x) => /^S-\d+$/.test(x))
    .map((id) => ({ id, title: m?.sources[id]?.title ?? '', url: m?.sources[id]?.url ?? '' }));
}

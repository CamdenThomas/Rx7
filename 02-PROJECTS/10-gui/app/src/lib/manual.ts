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

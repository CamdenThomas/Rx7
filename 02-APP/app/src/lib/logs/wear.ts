// Wear against the service intervals (02-APP BL4; electrical D-478): for each 00-CAR intervals
// row that applies, the miles and the engine hours run since the service visit that last did
// it. "Last done" is rx7.py's: the Manual's intervals carry `due.last` - the newest service
// visit whose `items` names the interval (interval_due) - and its due status, which is kept as
// it is; this file only adds what the record alone cannot know: the hours, from the pulled
// logs' runtime (the summary's runtime_s, stats.h: seconds with the engine running), and the
// miles where the visit has no mileage, from the odometer readings around it. Worked out at
// view time; nothing is stored.

import type { Due, ManualDrive, ManualInterval, ManualService, Odometer } from '../model';
import type { Digest } from './pipeline';
import { driveDate } from './trends';

/** rx7.py DUE_SOON_MILES: the Service page's own "due soon" margin, applied the same way here. */
export const DUE_SOON_MILES = 1000;
/** Hours left at which an interval kept in hours is due soon (confirm: no record row sets it). */
export const DUE_SOON_HOURS = 10;

/** A record date (YYYY-MM or YYYY-MM-DD) as a day; a month is its first day (rx7.py _as_date). */
export const asDay = (d: string) => (/^\d{4}-\d{2}$/.test(d ?? '') ? `${d}-01` : (d ?? '').slice(0, 10));

export interface Reading {
  date: string;
  miles: number;
  /** where it was read: a drives row, a service visit, or a pulled log */
  from: string;
}

/** Every odometer reading the record and the pulled logs hold, oldest first. */
export function readings(drives: ManualDrive[], service: ManualService[], digests: Digest[]): Reading[] {
  const out: Reading[] = [];
  for (const d of drives) if (d.odometer && Number.isFinite(Number(d.odometer)) && d.date) out.push({ date: asDay(d.date), miles: Number(d.odometer), from: `drives ${d.id}` });
  for (const s of service) if (s.mileage && Number.isFinite(Number(s.mileage)) && s.date) out.push({ date: asDay(s.date), miles: Number(s.mileage), from: `service ${s.id}` });
  for (const g of digests) if (g.endOdoX10 > 0) out.push({ date: driveDate(g), miles: Math.floor(g.endOdoX10 / 10), from: `pulled drive ${g.seq}` });
  return out.sort((a, b) => a.date.localeCompare(b.date) || a.miles - b.miles);
}

/** The newest reading: the record's odometer, or a pulled drive that ended further on. */
export function odometerNow(odo: Odometer | undefined, digests: Digest[]): Reading | null {
  let best: Reading | null = odo?.miles != null ? { date: odo.date, miles: odo.miles, from: odo.source ? `the record (${odo.source})` : 'the record' } : null;
  for (const g of digests) {
    const m = Math.floor(g.endOdoX10 / 10);
    if (g.endOdoX10 > 0 && (!best || m > best.miles)) best = { date: driveDate(g), miles: m, from: `pulled drive ${g.seq}` };
  }
  return best;
}

export interface MilesSince {
  miles: number;
  /**
   * service: the visit's own mileage to the newest reading - exact.
   * reading: the visit has no mileage; from the newest reading on or before its date - at most.
   * logged: no reading before it either; the pulled drives' distance since - at least.
   */
  basis: 'service' | 'reading' | 'logged';
  from: string;
}

export interface HoursSince {
  hours: number;
  drives: number;
  /** false when the logs start after the visit, so the hours are a floor */
  complete: boolean;
  /** drives with no summary, counted by their whole duration (key-on time, not engine time) */
  byDuration: number;
}

export interface Wear {
  id: string;
  item: string;
  every_miles: number | null;
  every_months: number | null;
  /** an `every_hours` column, when the record gains one; none today */
  every_hours: number | null;
  due: Due;
  milesSince: MilesSince | null;
  hoursSince: HoursSince | null;
  milesLeft: number | null;
  hoursLeft: number | null;
  /** rx7.py's status, raised (never lowered) by the hours or by miles the record could not work out */
  status: Due['status'];
  /** what to say about it, in one line */
  detail: string;
}

const num = (v: unknown) => {
  const n = Number(v);
  return v !== undefined && v !== null && String(v).trim() !== '' && Number.isFinite(n) ? n : null;
};

const RANK: Record<Due['status'], number> = { overdue: 0, soon: 1, ok: 2, never: 3, each: 4 };

/** Miles since the visit (see MilesSince), or null when nothing places it. */
export function milesSince(last: Due['last'], now: Reading | null, all: Reading[], digests: Digest[]): MilesSince | null {
  if (!last) return null;
  if (last.miles != null && now) return { miles: Math.max(0, now.miles - last.miles), basis: 'service', from: `${last.service} at ${last.miles}` };
  const day = asDay(last.date);
  const before = all.filter((r) => r.date <= day).at(-1);
  if (before && now) return { miles: Math.max(0, now.miles - before.miles), basis: 'reading', from: `${before.from}, ${before.date}` };
  const after = digests.filter((g) => driveDate(g) >= day);
  if (after.length) return { miles: Math.round(after.reduce((a, g) => a + g.miles, 0) * 10) / 10, basis: 'logged', from: `${after.length} pulled drive${after.length === 1 ? '' : 's'}` };
  return null;
}

/** Engine hours since a day (all logged hours when there is none), from the pulled drives. */
export function hoursSince(sinceDay: string | null, digests: Digest[]): HoursSince | null {
  if (!digests.length) return null;
  const after = sinceDay ? digests.filter((g) => driveDate(g) >= sinceDay) : digests;
  let s = 0;
  let byDuration = 0;
  for (const g of after) {
    if (g.summary && Number.isFinite(g.summary.runtime_s)) s += g.summary.runtime_s;
    else {
      s += g.durationS;
      byDuration++;
    }
  }
  const first = digests.map(driveDate).sort()[0];
  return { hours: Math.round((s / 3600) * 10) / 10, drives: after.length, complete: !!sinceDay && first < sinceDay, byDuration };
}

/** Wear for every interval that has one (an every-fill item such as premix has none). */
export function wear(intervals: ManualInterval[], odo: Odometer | undefined, drives: ManualDrive[], service: ManualService[], digests: Digest[]): Wear[] {
  const all = readings(drives, service, digests);
  const now = odometerNow(odo, digests);
  const out: Wear[] = [];
  for (const i of intervals) {
    const every_miles = num(i.every_miles);
    const every_months = num(i.every_months);
    const every_hours = num((i as unknown as Record<string, unknown>).every_hours);
    if (!every_miles && !every_months && !every_hours) continue;
    const last = i.due.last;
    const ms = milesSince(last, now, all, digests);
    const hs = hoursSince(last ? asDay(last.date) : null, digests);
    let status = i.due.status;
    const raise = (s: Due['status']) => {
      if (RANK[s] < RANK[status]) status = s;
    };
    // Miles left: from the miles since, so a pulled drive that ran the odometer past the
    // record's newest reading counts (the record's own figure stands when there are none).
    // They move the status when exact (service) or a floor (logged); a ceiling (reading,
    // taken before the visit) is shown but could call an interval overdue that is not.
    const derived = every_miles && ms ? Math.round(every_miles - ms.miles) : null;
    const milesLeft = derived !== null && (ms!.basis !== 'reading' || i.due.miles_left == null) ? derived : (i.due.miles_left ?? null);
    if (last && derived !== null && ms!.basis !== 'reading') raise(derived <= 0 ? 'overdue' : derived <= DUE_SOON_MILES ? 'soon' : 'ok');
    const hoursLeft = last && every_hours && hs ? Math.round((every_hours - hs.hours) * 10) / 10 : null;
    if (hoursLeft !== null) raise(hoursLeft <= 0 ? 'overdue' : hoursLeft <= DUE_SOON_HOURS ? 'soon' : 'ok');
    const detail = !last
      ? 'No service visit has done it yet, so there is nothing to count from.'
      : [
          ms
            ? `${ms.basis === 'reading' ? 'at most ' : ms.basis === 'logged' ? 'at least ' : ''}${Math.round(ms.miles).toLocaleString('en-US')} mi since`
            : 'miles since: no odometer reading places the visit',
          hs ? `${hs.complete ? '' : 'at least '}${hs.hours} h of engine running` : 'hours: no drive pulled yet',
        ].join(' · ');
    out.push({ id: i.id, item: i.item, every_miles, every_months, every_hours, due: i.due, milesSince: ms, hoursSince: hs, milesLeft, hoursLeft, status, detail });
  }
  return out.sort((a, b) => RANK[a.status] - RANK[b.status]);
}

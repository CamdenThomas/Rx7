<!--
  Trends (02-APP BL4; electrical D-478): the car's state read from its own logs. Each logged
  channel across the drives this device has pulled, a drift mark when the newest drives step
  away from the ones before, what was out of range in each drive, and wear against the service
  intervals by the miles and engine hours actually run. Worked out here, when the page opens,
  from the drives' digests (lib/logs/trends.ts, wear.ts) and the record - the limits are
  electrical params, the intervals and when each was last done are 00-CAR's through rx7.py.
  Nothing is stored; digest.json beside each drive's files is a cache, rebuilt when missing.
-->
<script lang="ts">
  import { BluetoothSearching, TrendingDown, TrendingUp } from '@lucide/svelte';
  import type { Manual } from '../../lib/model';
  import { app } from '../../lib/app.svelte';
  import { logLink } from '../../lib/logs/link.svelte';
  import type { Digest } from '../../lib/logs/pipeline';
  import { driveDate, driveFlags, limitsFrom, lookAt, spark, trends, type Group, type Spark, type Trend } from '../../lib/logs/trends';
  import { odometerNow, readings, wear } from '../../lib/logs/wear';
  import { day, miles } from '../../lib/manual';
  import { href } from '../../lib/router.svelte';
  import DueChip from './DueChip.svelte';

  let { m }: { m: Manual } = $props();

  $effect(() => {
    void logLink.loadDigests();
  });

  const digests = $derived<Digest[]>(logLink.digests ?? []);
  const limits = $derived(limitsFrom(app.snapshot?.tables));
  const ts = $derived(trends(digests));
  const groups = $derived(
    (['Engine', 'Fuel', 'Electrical', 'Battery', 'Motion'] as Group[])
      .map((g) => ({ g, ts: ts.filter((t) => t.spec.group === g) }))
      .filter((x) => x.ts.length),
  );
  const ws = $derived(wear(m.intervals, m.odometer, m.drives, m.service, digests));
  const looks = $derived(lookAt(digests, limits, ts, ws));
  const newest = $derived([...digests].sort((a, b) => b.seq - a.seq));
  const odoPoints = $derived(readings(m.drives, m.service, digests));
  const odoNow = $derived(odometerNow(m.odometer, digests));
  const odoSpark = $derived(spark(odoPoints.map((r) => ({ min: r.miles, max: r.miles, value: r.miles })), 220, 44));

  const fmt = (v: number | null | undefined, digits: number) => (v === null || v === undefined ? '-' : v.toLocaleString('en-US', { minimumFractionDigits: digits, maximumFractionDigits: digits }));
  const unit = (t: Trend) => (t.unit ? ` ${t.unit}` : '');
  const foot = (t: Trend) =>
    [t.latest && `range ${fmt(t.latest.min, t.spec.digits)} to ${fmt(t.latest.max, t.spec.digits)}${unit(t)}`, `${t.points.length} drive${t.points.length === 1 ? '' : 's'}`]
      .filter(Boolean)
      .join(' · ');
  const hours = (g: Digest) => (g.summary ? g.summary.runtime_s / 3600 : null);
  const every = (w: { every_miles: number | null; every_months: number | null; every_hours: number | null }) =>
    [w.every_miles && `every ${miles(w.every_miles)}`, w.every_months && `${w.every_months} months`, w.every_hours && `${w.every_hours} h`].filter(Boolean).join(' or ');
  const LOOK: Record<string, string> = { flag: 'Out of range', drift: 'Drift', wear: 'Wear' };
</script>

{#snippet chart(s: Spark, label: string)}
  <svg class="spark" viewBox="0 0 {s.w} {s.h}" width={s.w} height={s.h} role="img" aria-label={label}>
    {#each s.bars as b, i (i)}<line class="bar" x1={b.x} x2={b.x} y1={b.y1} y2={Math.max(b.y2, b.y1 + 1)} />{/each}
    {#each s.paths as d, i (i)}<path class="line" {d} />{/each}
    {#if s.last}<circle class="dot" cx={s.last.x} cy={s.last.y} r="2.6" />{/if}
  </svg>
{/snippet}

<section>
  <h2>What to look at</h2>
  <div class="panel rows">
    {#if !looks.length}
      <p class="muted empty">
        {digests.length ? `Nothing stands out across ${digests.length} drive${digests.length === 1 ? '' : 's'}, and nothing is due.` : 'Nothing is due. No drive has been pulled on this device yet, so nothing is read from the logs.'}
      </p>
    {/if}
    {#each looks as l, i (i)}
      <div class="row look">
        <div class="what">
          <span class="item">{l.text}</span>
          <span class="note">{l.detail}</span>
        </div>
        <span class="chip {l.kind === 'drift' ? 'cool' : 'accent'}">{LOOK[l.kind]}</span>
      </div>
    {/each}
  </div>
</section>

{#if !digests.length}
  <section class="intro">
    <p class="muted">
      The trends come from the drives the car's ICU logs. After a drive, Connect and log pulls them to this device; each
      channel then shows here, drive by drive.
    </p>
    <a class="btn small" href={href({ name: 'manual', page: 'connect' })}><BluetoothSearching size={14} /> Connect and log</a>
  </section>
{:else}
  {#each groups as { g, ts: list } (g)}
    <section>
      <h2>{g}</h2>
      <div class="cards">
        {#each list as t (t.spec.key)}
          <article class="panel card" title={t.spec.drift?.why ?? `No drift rule: ${t.spec.why ?? ''}`}>
            <header>
              <span class="name">{t.name}</span>
              {#if t.drift}
                <span class="chip cool" title="{t.spec.drift?.why} - confirm">
                  {#if t.drift.dir === 'up'}<TrendingUp size={12} />{:else}<TrendingDown size={12} />{/if}
                  {t.drift.dir === 'up' ? '+' : '−'}{fmt(Math.abs(t.drift.by), t.spec.digits)}{unit(t)}
                </span>
              {/if}
            </header>
            <div class="val">
              <strong class="num">{fmt(t.latest?.value, t.spec.digits)}</strong><span class="faint">{unit(t)}</span>
              <span class="faint small">{t.spec.stat === 'max' ? 'peak' : 'mean'}, last drive</span>
            </div>
            {@render chart(spark(t.points), `${t.name} over ${t.points.length} drives`)}
            <span class="faint small num">{foot(t)}</span>
          </article>
        {/each}
      </div>
    </section>
  {/each}

  <section>
    <h2>Drives</h2>
    <div class="panel rows">
      {#each newest as g (g.seq)}
        {@const fl = driveFlags(g, limits)}
        <div class="row">
          <div class="what">
            <span class="item">Drive {g.seq} <span class="faint">· {day(driveDate(g))}{g.approx ? ' (approximate)' : ''}</span></span>
            <span class="sub">
              {g.miles.toFixed(1)} mi · {Math.max(1, Math.round(g.durationS / 60))} min{hours(g) !== null ? ` · ${fmt(hours(g), 2)} h running` : ''}{g.endOdoX10 ? ` · ended at ${miles(Math.floor(g.endOdoX10 / 10))}` : ''}
            </span>
            {#each fl as f (f.code)}<span class="flag">{f.text}</span>{/each}
          </div>
          <span class="chip {fl.length ? 'accent' : 'quiet'}">{fl.length ? `${fl.length} flag${fl.length === 1 ? '' : 's'}` : 'In range'}</span>
        </div>
      {/each}
    </div>
    {#each logLink.digestProblems as p, i (i)}<p class="warn small">{p}</p>{/each}
  </section>
{/if}

<section>
  <h2>Wear</h2>
  <div class="panel odo">
    <div class="what">
      <span class="label">Odometer</span>
      <strong class="num">{odoNow ? miles(odoNow.miles) : 'No reading yet'}</strong>
      {#if odoNow}<span class="faint small">{odoNow.date ? day(odoNow.date) : 'date not recorded'} · from {odoNow.from}</span>{/if}
    </div>
    {#if odoPoints.length > 1}{@render chart(odoSpark, `the odometer over ${odoPoints.length} readings`)}{/if}
  </div>
  <div class="panel rows">
    {#each ws as w (w.id)}
      <div class="row">
        <div class="what">
          <span class="item">{w.item}</span>
          <span class="sub">{every(w)}{w.due.last ? ` · last ${day(w.due.last.date)}${w.due.last.miles != null ? ` at ${miles(w.due.last.miles)}` : ''} (${w.due.last.service})` : ''}</span>
          <span class="note">{w.detail}</span>
        </div>
        <div class="due">
          <DueChip due={{ ...w.due, status: w.status, miles_left: w.milesLeft }} />
          {#if w.milesLeft !== null && w.due.last}
            {@const bound = w.milesSince?.basis === 'reading' ? 'at least ' : w.milesSince?.basis === 'logged' ? 'at most ' : ''}
            <span class="faint small">{w.milesLeft > 0 ? `${bound}${miles(w.milesLeft)} left` : `${miles(-w.milesLeft)} over`}</span>
          {/if}
          {#if w.hoursLeft !== null}<span class="faint small">{w.hoursLeft > 0 ? `${w.hoursLeft} h left` : `${-w.hoursLeft} h over`}</span>{/if}
        </div>
      </div>
    {/each}
  </div>
  <p class="faint small foot">
    Worked out when this page opens, from the drives pulled to this device and the record: limits from electrical params, intervals and
    the last visit for each from the service log. Engine hours are the ICU's running time; miles marked "at most" count from a reading
    taken before the visit, "at least" only the pulled drives. Drift margins are a first guess (confirm).
  </p>
</section>

<style>
  section {
    margin-bottom: 24px;
  }
  h2 {
    font-size: 15px;
    margin: 0 0 8px;
  }
  .intro p {
    max-width: 68ch;
    margin: 0 0 10px;
  }
  .rows {
    padding: 0 16px;
  }
  .empty {
    padding: 12px 0;
    margin: 0;
  }
  .row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 6px 16px;
    align-items: start;
    padding: 11px 0;
    border-top: 1px solid var(--line-soft);
  }
  .row:first-child {
    border-top: 0;
  }
  .what {
    display: flex;
    flex-direction: column;
    gap: 3px;
    min-width: 0;
  }
  .item {
    font-weight: 560;
    font-size: 14px;
  }
  .sub {
    color: var(--text-2);
    font-size: 13px;
  }
  .note {
    color: var(--text-3);
    font-size: 12.5px;
    line-height: 1.45;
  }
  .flag,
  .warn {
    color: var(--accent-2);
    font-size: 12.5px;
  }
  .small {
    font-size: 12.5px;
  }
  .due {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
    text-align: right;
  }
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 10px;
  }
  .card {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 12px 14px;
    min-width: 0;
  }
  .card header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }
  .name {
    font-weight: 560;
    font-size: 13.5px;
    color: var(--text-2);
  }
  .val {
    display: flex;
    align-items: baseline;
    gap: 4px;
    flex-wrap: wrap;
  }
  .val strong {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.01em;
  }
  .val .small {
    flex-basis: 100%;
  }
  .spark {
    display: block;
    width: 100%;
    max-width: 320px;
    height: auto;
    overflow: visible;
  }
  .spark .bar {
    stroke: var(--steel);
    stroke-width: 3;
    stroke-linecap: round;
  }
  .spark .line {
    fill: none;
    stroke: var(--sky);
    stroke-width: 1.6;
    stroke-linejoin: round;
  }
  .spark .dot {
    fill: var(--ember);
  }
  .odo {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    padding: 12px 16px;
    margin-bottom: 10px;
  }
  .odo strong {
    font-size: 20px;
    font-weight: 700;
  }
  .foot {
    max-width: 80ch;
    margin: 10px 0 0;
    line-height: 1.5;
  }
  @media (max-width: 759px) {
    .row:not(.look) {
      grid-template-columns: 1fr;
    }
    .due {
      align-items: flex-start;
      text-align: left;
    }
    .cards {
      grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    }
  }
</style>

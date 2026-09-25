<!--
  Service (D-417): the intervals and where each stands, the service log (the Manual's one
  history, his 5.6), the drives he logged, and the procedures. Every due date and the odometer
  are rx7.py's; this page only lays them out.
-->
<script lang="ts">
  import type { Manual } from '../../lib/model';
  import { day, miles, part } from '../../lib/manual';
  import Prose from '../../components/Prose.svelte';
  import DueChip from './DueChip.svelte';
  import Held from './Held.svelte';

  let { m }: { m: Manual } = $props();

  const ORDER = { overdue: 0, soon: 1, never: 2, ok: 3, each: 4 } as const;
  const intervals = $derived([...m.intervals].sort((a, b) => ORDER[a.due.status] - ORDER[b.due.status]));
  const visits = $derived([...m.service].sort((a, b) => b.date.localeCompare(a.date)));
  const drives = $derived([...m.drives].sort((a, b) => b.date.localeCompare(a.date)));
  const held = $derived(m.held.filter((h) => h.table !== 'specs'));

  function every(i: { every_miles: string; every_months: string }) {
    return [i.every_miles && `every ${miles(i.every_miles)}`, i.every_months && `${i.every_months} months`].filter(Boolean).join(' or ');
  }
</script>

<section>
  <h2>Intervals</h2>
  <div class="panel rows">
    {#each intervals as i (i.id)}
      <div class="row">
        <div class="what">
          <span class="item">{i.item}</span>
          <span class="sub">{every(i) || 'each time it is done'}{i.spec ? ` · ${i.spec}` : ''}</span>
          {#if i.note}<span class="note">{i.note}</span>{/if}
        </div>
        <div class="due">
          <DueChip due={i.due} />
          <span class="faint small">
            {#if i.due.last}last {day(i.due.last.date)}{i.due.last.miles != null ? ` at ${miles(i.due.last.miles)}` : ''}{/if}
            {#if i.due.next_miles != null || i.due.next_date}
              <br />next {[i.due.next_miles != null && miles(i.due.next_miles), i.due.next_date && day(i.due.next_date)].filter(Boolean).join(' or ')}
            {/if}
          </span>
        </div>
      </div>
    {/each}
  </div>
</section>

<section>
  <h2>Service log</h2>
  {#if !visits.length}<p class="muted">No service recorded.</p>{/if}
  <ol class="log">
    {#each visits as s (s.id)}
      <li class="panel visit">
        <header>
          <strong>{s.work}</strong>
          <span class="faint small">{day(s.date)}{s.mileage ? ` · ${miles(s.mileage)}` : ''}</span>
        </header>
        {#if s.notes}<p class="note">{s.notes}</p>{/if}
        {#if s.fitted.length}
          <p class="fitted">
            <span class="label">Fitted</span>
            {#each s.fitted as id, n (id)}{n ? ', ' : ''}{part(id)?.name ?? id}{/each}
          </p>
        {/if}
      </li>
    {/each}
  </ol>
</section>

<section>
  <h2>Drives</h2>
  {#if !drives.length}
    <p class="muted">No drive logged yet. Log drive and Set odo, at the top of the Manual, add them here.</p>
  {:else}
    <div class="panel rows">
      {#each drives as d (d.id)}
        <div class="row">
          <div class="what">
            <span class="item">{d.kind === 'set' ? 'Odometer set' : [d.from, d.to].filter(Boolean).join(' → ') || 'Drive'}</span>
            {#if d.note}<span class="note">{d.note}</span>{/if}
          </div>
          <div class="due">
            <span class="num">{miles(d.odometer)}</span>
            <span class="faint small">{day(d.date)}{d.miles != null && d.kind !== 'set' ? ` · ${miles(d.miles)}` : ''}</span>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</section>

{#if m.procedures.length}
  <section>
    <h2>Procedures</h2>
    {#each m.procedures as p (p.id)}
      <details class="panel proc">
        <summary>
          <strong>{p.title}</strong>
          <span class="faint small">{[p.system, p.when].filter(Boolean).join(' · ')}</span>
        </summary>
        {#if p.tools}<p class="small"><span class="label">Tools</span> {p.tools}</p>{/if}
        <Prose text={p.body} compact />
      </details>
    {/each}
  </section>
{/if}

<Held rows={held} what="other facts" />

<style>
  section {
    margin-bottom: 26px;
  }
  h2 {
    font-size: 15px;
    margin: 0 0 8px;
  }
  .rows {
    padding: 0 16px;
  }
  .row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(150px, auto);
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
    margin: 0;
  }
  .due {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
    text-align: right;
  }
  .small {
    font-size: 12.5px;
  }
  .log {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .visit {
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .visit header {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
  }
  .fitted {
    margin: 0;
    font-size: 13px;
    color: var(--text-2);
  }
  .fitted .label {
    margin-right: 6px;
  }
  .proc {
    padding: 12px 16px;
    margin-bottom: 8px;
  }
  .proc summary {
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  @media (max-width: 759px) {
    .row {
      grid-template-columns: 1fr;
    }
    .due {
      align-items: flex-start;
      text-align: left;
    }
  }
</style>

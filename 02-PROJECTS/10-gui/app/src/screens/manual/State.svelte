<!--
  Car state, the Manual's front page (his 5.1 default): what is due, the known faults, then each
  system as it is now. Only rows rx7.py lets through: nothing unchecked, nothing past or planned.
-->
<script lang="ts">
  import { ChevronRight } from '@lucide/svelte';
  import type { Manual } from '../../lib/model';
  import { day, miles } from '../../lib/manual';
  import { href } from '../../lib/router.svelte';
  import DueChip from './DueChip.svelte';

  let { m }: { m: Manual } = $props();

  const due = $derived(m.intervals.filter((i) => ['overdue', 'soon', 'never'].includes(i.due.status)));
  const top = $derived(m.systems.filter((s) => !s.parent));
  const faults = $derived(m.issues);
</script>

<div class="grid2">
  <section class="panel block">
    <header>
      <h2>Due</h2>
      <a class="more" href={href({ name: 'manual', page: 'service' })}>Service <ChevronRight size={14} /></a>
    </header>
    {#if !due.length}
      <p class="muted">Nothing is due.</p>
    {:else}
      <ul class="list">
        {#each due as i (i.id)}
          <li>
            <div class="line">
              <strong>{i.item}</strong>
              <DueChip due={i.due} />
            </div>
            <span class="faint small">
              {#if i.due.status === 'never'}
                No service visit has done it yet
              {:else}
                {[i.due.next_miles != null && `by ${miles(i.due.next_miles)}`, i.due.next_date && `by ${day(i.due.next_date)}`].filter(Boolean).join(' or ')}
              {/if}
            </span>
          </li>
        {/each}
      </ul>
    {/if}
  </section>

  <section class="panel block">
    <header><h2>Known faults</h2><span class="faint small">{faults.length}</span></header>
    <ul class="list faults">
      {#each faults as k (k.id)}
        <li>
          <strong>{k.issue}</strong>
          {#if k.status}<span class="muted small">{k.status}</span>{/if}
        </li>
      {/each}
    </ul>
  </section>
</div>

<h2 class="section">Systems</h2>
<div class="systems">
  {#each top as s (s.id)}
    <a class="sys panel" href={href({ name: 'manual', page: 'systems', id: s.id })}>
      <span class="name">{s.name}</span>
      <span class="state">{s.state || 'Nothing recorded yet.'}</span>
      <span class="meta faint">
        {s.parts.length + s.children.reduce((n, c) => n + (m.systems.find((x) => x.id === c)?.parts.length ?? 0), 0)} parts
        {#if s.since}· since {day(s.since)}{/if}
      </span>
    </a>
  {/each}
</div>

<style>
  .grid2 {
    display: grid;
    grid-template-columns: 1fr 1.3fr;
    gap: 16px;
    align-items: start;
  }
  .block {
    padding: 14px 16px;
  }
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  h2 {
    font-size: 16px;
    margin: 0;
  }
  h2.section {
    margin: 28px 0 12px;
  }
  .more {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    font-size: 13px;
    color: var(--text-3);
  }
  .list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
  }
  .list li {
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 9px 0;
    border-top: 1px solid var(--line-soft);
  }
  .list li:first-child {
    border-top: 0;
  }
  .faults {
    max-height: 420px;
    overflow-y: auto;
  }
  .faults strong {
    font-weight: 560;
    font-size: 14px;
  }
  .line {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
  }
  .small {
    font-size: 13px;
  }
  .systems {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 12px;
  }
  .sys {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 14px 16px;
    color: var(--text);
    transition:
      border-color var(--t-fast),
      background var(--t-fast);
  }
  .sys:hover {
    border-color: var(--line);
    background: var(--surface-2);
  }
  .name {
    font-weight: 650;
    font-size: 15px;
  }
  .state {
    color: var(--text-2);
    font-size: 13.5px;
    line-height: 1.5;
  }
  .meta {
    font-size: 12.5px;
    margin-top: auto;
  }
  @media (max-width: 859px) {
    .grid2 {
      grid-template-columns: 1fr;
    }
  }
</style>

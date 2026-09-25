<!-- The project's parts table, dense, filterable, every row openable (D-406 6.3). -->
<script lang="ts">
  import { Search } from '@lucide/svelte';
  import { app } from '../../lib/app.svelte';
  import { router } from '../../lib/router.svelte';

  let { area }: { area: string } = $props();
  let q = $state('');

  const table = $derived(app.snapshot?.tables.find((t) => t.area === area && t.table === 'parts'));
  const meta = $derived(app.area(area)?.tables.find((t) => t.name === 'parts'));
  // What a part is and what it costs first; where it comes from and why after.
  const FIRST = ['item', 'spec', 'qty', 'unit', 'unit_usd', 'status'];
  const cols = $derived.by(() => {
    if (!table) return [];
    const [k, ...rest] = table.columns.filter((c) => c !== 'note');
    const lead = FIRST.filter((c) => rest.includes(c));
    return [k, ...lead, ...rest.filter((c) => !lead.includes(c))];
  });
  const rows = $derived.by(() => {
    if (!table) return [];
    const t = q.trim().toLowerCase();
    return t ? table.rows.filter((r) => r.join(' ').toLowerCase().includes(t)) : table.rows;
  });
  const key = $derived(Math.max(0, table?.columns.indexOf(meta?.key ?? 'id') ?? 0));
  const idx = (c: string) => table!.columns.indexOf(c);
  // One line per part: prose columns are clipped (the whole text is on hover and on the
  // part's own page) and numbers line up on the right.
  const type = (c: string) => meta?.columns.find((x) => x.column === c)?.type ?? 'str';
  const prose = (c: string) => type(c) === 'text';
  const number = (c: string) => type(c) === 'int' || type(c) === 'float' || c === 'qty';
  const label = (c: string) => (c === 'unit_usd' ? 'unit $' : c.replaceAll('_', ' '));
</script>

{#if !table}
  <p class="muted">This project keeps no parts table.</p>
{:else}
  <div class="tools">
    <label class="find"><Search size={15} /><input bind:value={q} placeholder="Filter {table.rows.length} parts" aria-label="Filter parts" /></label>
    <span class="faint">{rows.length} shown · {meta?.purpose}</span>
  </div>
  <div class="wrap">
    <table class="grid">
      <thead><tr>{#each cols as c (c)}<th class:num={number(c)}>{label(c)}</th>{/each}</tr></thead>
      <tbody>
        {#each rows as r (r[key])}
          <tr onclick={() => router.go({ name: 'row', area, table: 'parts', key: r[key] })}>
            {#each cols as c (c)}
              <td
                class:mono={c === 'id' || c === meta?.key}
                class:id={c === meta?.key}
                class:prose={prose(c)}
                class:num={number(c)}
                title={r[idx(c)] || undefined}
              >{r[idx(c)]}</td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
  <ul class="cards">
    {#each rows as r (r[key])}
      <li>
        <button onclick={() => router.go({ name: 'row', area, table: 'parts', key: r[key] })}>
          <span class="id">{r[key]}</span>
          <strong>{r[idx('item')] ?? ''}</strong>
          {#if idx('status') >= 0 && r[idx('status')]}<span class="chip quiet">{r[idx('status')]}</span>{/if}
          {#if idx('spec') >= 0}<span class="spec">{r[idx('spec')]}</span>{/if}
        </button>
      </li>
    {/each}
  </ul>
{/if}

<style>
  .tools {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 14px;
    font-size: 13px;
    flex-wrap: wrap;
  }
  .find {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 12px;
    height: 36px;
    width: 300px;
    border-radius: var(--r-2);
    border: 1px solid var(--line);
    background: var(--bg-raise);
    color: var(--text-3);
  }
  .find input {
    flex: 1;
    background: none;
    border: 0;
    outline: 0;
    color: var(--text);
  }
  .wrap {
    overflow: auto;
    max-height: calc(100dvh - 260px);
    border: 1px solid var(--line-soft);
    border-radius: var(--r-3);
    background: var(--surface);
  }
  td {
    color: var(--text-2);
    white-space: nowrap;
  }
  td {
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  td.prose {
    max-width: 320px;
  }
  .num {
    text-align: right;
    font-variant-numeric: tabular-nums;
  }
  /* The part's id stays in view while the row scrolls sideways. */
  th:first-child,
  td:first-child {
    position: sticky;
    left: 0;
  }
  th:first-child {
    z-index: 3;
  }
  td:first-child {
    z-index: 1;
    background: var(--surface);
  }
  tr:hover td:first-child {
    background: color-mix(in oklab, var(--surface-2) 70%, var(--surface));
  }
  .cards {
    display: none;
    list-style: none;
    margin: 0;
    padding: 0;
    flex-direction: column;
    gap: 8px;
  }
  .cards button {
    width: 100%;
    text-align: left;
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 6px 10px;
    padding: 12px 14px;
    border-radius: var(--r-2);
    border: 1px solid var(--line-soft);
    background: var(--surface);
    color: var(--text);
  }
  .spec {
    flex-basis: 100%;
    font-size: 13px;
    color: var(--text-3);
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  @media (max-width: 759px) {
    .wrap {
      display: none;
    }
    .cards {
      display: flex;
    }
    .find {
      width: 100%;
    }
  }
  td:first-child {
    color: var(--sky);
  }
</style>

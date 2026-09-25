<!--
  Specs (D-417): every number the Manual lets through, by category, with where it came from.
  What is held back (unchecked, unverified, another car's) is listed underneath with the reason
  rx7.py gave, so a missing figure is never a silent gap.
-->
<script lang="ts">
  import { Search } from '@lucide/svelte';
  import type { Manual, ManualSpec } from '../../lib/model';
  import { sources, system, value } from '../../lib/manual';
  import { app } from '../../lib/app.svelte';
  import Held from './Held.svelte';

  let { m }: { m: Manual } = $props();

  let q = $state('');
  let cat = $state('');

  const cats = $derived([...new Set(m.specs.map((s) => s.category))].sort());
  const words = $derived(q.toLowerCase().split(/\s+/).filter(Boolean));
  const hay = (s: ManualSpec) => [s.item, s.value, s.unit, s.category, s.note, system(s.system)?.name ?? ''].join(' ').toLowerCase();
  const shown = $derived(m.specs.filter((s) => (!cat || s.category === cat) && words.every((w) => hay(s).includes(w))));
  const groups = $derived(
    [...new Set(shown.map((s) => s.category))].sort().map((c) => ({ name: c, rows: shown.filter((s) => s.category === c) })),
  );
  const held = $derived(m.held.filter((h) => h.table === 'specs'));

  function open(e: MouseEvent, url: string) {
    if (!url) return;
    e.preventDefault();
    app.platform?.open(url);
  }
</script>

<div class="bar">
  <label class="find">
    <Search size={15} />
    <input class="input" type="search" placeholder="Find a spec" bind:value={q} aria-label="Find a spec" />
  </label>
  <div class="cats" role="group" aria-label="Category">
    <button class="chip" class:solid={!cat} onclick={() => (cat = '')}>All {m.specs.length}</button>
    {#each cats as c (c)}
      <button class="chip" class:solid={cat === c} onclick={() => (cat = cat === c ? '' : c)}>{c}</button>
    {/each}
  </div>
</div>

{#if !groups.length}
  <p class="muted">No spec matches.</p>
{/if}

{#each groups as g (g.name)}
  <section class="group">
    <h2>{g.name} <span class="faint">{g.rows.length}</span></h2>
    <div class="panel rows">
      {#each g.rows as s (s.id)}
        <div class="row">
          <div class="what">
            <span class="item">{s.item}</span>
            {#if s.note}<span class="note">{s.note}</span>{/if}
          </div>
          <span class="v num">{value(s)}</span>
          <span class="src">
            {#each sources(s.source) as x (x.id)}
              <a class="id" href={x.url || undefined} title={[x.title, s.page].filter(Boolean).join(' · ')} onclick={(e) => open(e, x.url)}>{x.id}</a>
            {/each}
            {#if s.confidence && s.confidence !== 'primary'}<span class="chip quiet">{s.confidence}</span>{/if}
          </span>
        </div>
      {/each}
    </div>
  </section>
{/each}

<Held rows={held} what="specs" />

<style>
  .bar {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 18px;
  }
  .find {
    position: relative;
    display: flex;
    align-items: center;
    max-width: 420px;
    color: var(--text-3);
  }
  .find :global(svg) {
    position: absolute;
    left: 11px;
  }
  .find .input {
    width: 100%;
    padding-left: 34px;
  }
  .cats {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .cats .chip {
    cursor: pointer;
  }
  .group {
    margin-bottom: 22px;
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
    grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) 150px;
    gap: 6px 16px;
    align-items: baseline;
    padding: 10px 0;
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
  .note {
    color: var(--text-3);
    font-size: 12.5px;
    line-height: 1.45;
  }
  .v {
    font-size: 14px;
    overflow-wrap: anywhere;
  }
  .src {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 6px;
  }
  @media (max-width: 759px) {
    .row {
      grid-template-columns: 1fr;
    }
    .src {
      justify-content: flex-start;
    }
  }
</style>

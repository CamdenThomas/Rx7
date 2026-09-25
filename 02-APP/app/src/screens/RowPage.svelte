<!--
  Any row of any table, readable: each column by name, what the column means, and a link
  wherever the value names a row in another table.
-->
<script lang="ts">
  import Prose from '../components/Prose.svelte';
  import { app } from '../lib/app.svelte';
  import { href, type Route } from '../lib/router.svelte';
  import { projectLabel } from '../lib/ui.svelte';

  let { area, table, key }: { area: string; table: string; key: string } = $props();

  const a = $derived(app.area(area));
  const meta = $derived(a?.tables.find((t) => t.name === table));
  const row = $derived.by((): Record<string, string> | undefined => {
    if (table === 'picks') {
      const p = app.snapshot?.picks.find((x) => x.area === area && x.id === key);
      return p ? (p as unknown as Record<string, string>) : undefined;
    }
    const t = app.snapshot?.tables.find((x) => x.area === area && x.table === table);
    const ki = t ? Math.max(0, t.columns.indexOf(meta?.key ?? t.columns[0])) : 0;
    const r = t?.rows.find((x) => x[ki] === key);
    return t && r ? Object.fromEntries(t.columns.map((c, i) => [c, r[i]])) : undefined;
  });

  function refRoute(ref: string, value: string): Route | null {
    if (!ref || !value) return null;
    const [aname, rest] = ref.includes(':') ? ref.split(':') : [area, ref];
    const tname = rest.split('.')[0];
    if (tname === 'work') return { name: 'todo', area: aname, id: value };
    return { name: 'row', area: aname, table: tname, key: value };
  }
</script>

<div class="page narrow">
  <p class="label">{a?.kind === 'project' ? projectLabel(area) : area} · {table}</p>
  <h1 class="mono">{key}</h1>
  {#if meta?.purpose}<p class="muted purpose">{meta.purpose}</p>{/if}

  {#if !row}
    <p class="muted">There is no row {key} in {table}.</p>
  {:else}
    <dl class="card">
      {#each meta?.columns ?? Object.keys(row).map((c) => ({ column: c, type: '', ref: '', note: '', required: '' })) as c (c.column)}
        {@const v = row[c.column] ?? ''}
        {#if v}
          {@const to = refRoute(c.ref, v)}
          <div class="f">
            <dt title={c.note}>{c.column}{#if c.note}<span class="note">{c.note}</span>{/if}</dt>
            <dd>
              {#if to}<a class="mono" href={href(to)}>{v}</a>
              {:else if c.type === 'text' || v.length > 80}<Prose text={v} compact />
              {:else}<span class:mono={c.type === 'key' || c.type === 'num' || c.type === 'int'}>{v}</span>{/if}
            </dd>
          </div>
        {/if}
      {/each}
    </dl>
  {/if}
</div>

<style>
  h1 {
    font-size: 26px;
    margin: 6px 0 8px;
    color: var(--sky);
  }
  .purpose {
    margin-bottom: 20px;
    font-size: 14px;
  }
  dl {
    margin: 0;
    padding: 6px 20px;
  }
  .f {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 16px;
    padding: 12px 0;
    border-bottom: 1px solid var(--line-soft);
  }
  .f:last-child {
    border-bottom: 0;
  }
  dt {
    font-weight: 600;
    font-size: 13px;
    color: var(--text-2);
    display: flex;
    flex-direction: column;
    gap: 3px;
  }
  .note {
    font-weight: 400;
    font-size: 11.5px;
    color: var(--text-4);
    line-height: 1.4;
  }
  dd {
    margin: 0;
    min-width: 0;
    overflow-wrap: anywhere;
  }
  @media (max-width: 759px) {
    .f {
      grid-template-columns: 1fr;
      gap: 4px;
    }
    .note {
      display: none;
    }
  }
</style>

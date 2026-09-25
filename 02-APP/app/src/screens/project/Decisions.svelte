<!--
  Every ruling in the project (D-406 8.3), searchable and grouped by the system it touches,
  newest first inside each group. Superseded ones are kept, marked, so every id can be found.
-->
<script lang="ts">
  import { ChevronDown, Search } from '@lucide/svelte';
  import DecisionView from '../../components/DecisionView.svelte';
  import { app } from '../../lib/app.svelte';
  import { href } from '../../lib/router.svelte';
  import { plain } from '../../lib/text';

  let { area, id }: { area: string; id?: string } = $props();

  let q = $state('');
  let showAll = $state(false);
  let shut = $state<Record<string, boolean>>({});

  const all = $derived(app.decisions(area));
  const current = $derived(id ? all.find((d) => d.id === id) ?? app.decision(id) : undefined);
  const num = (id: string) => Number(id.replace(/\D/g, ''));

  const groups = $derived.by(() => {
    const t = q.trim().toLowerCase();
    const shown = all.filter(
      (d) => (showAll || d.status === 'standing' || d.status === 'inherited') &&
        (!t || `${d.id} ${d.title} ${d.system} ${plain(d.body)}`.toLowerCase().includes(t)),
    );
    const m = new Map<string, typeof shown>();
    for (const d of shown) {
      const k = d.system || 'Uncategorised';
      m.set(k, [...(m.get(k) ?? []), d]);
    }
    return [...m.entries()].map(([system, list]) => ({ system, list: list.sort((a, b) => num(b.id) - num(a.id)) })).sort((a, b) => num(b.list[0].id) - num(a.list[0].id));
  });
  const shownDetail = $derived(current ?? groups[0]?.list[0]);
  const count = $derived(groups.reduce((n, g) => n + g.list.length, 0));
</script>

<div class="dpage" class:has={!!current}>
  <div class="index">
    <div class="tools">
      <label class="find"><Search size={15} /><input bind:value={q} placeholder="Search {all.length} decisions" aria-label="Search decisions" /></label>
      <label class="toggle"><input type="checkbox" bind:checked={showAll} /> Include superseded</label>
    </div>
    <p class="faint small">{count} shown</p>
    {#each groups as g (g.system)}
      <section class="group">
        <button class="gh" onclick={() => (shut = { ...shut, [g.system]: !shut[g.system] })} aria-expanded={!shut[g.system]}>
          <ChevronDown size={15} class={shut[g.system] ? 'rot' : ''} />
          <span>{g.system}</span><span class="n">{g.list.length}</span>
        </button>
        {#if !shut[g.system]}
          <ul>
            {#each g.list as d (d.area + d.id)}
              <li>
                <a class:on={shownDetail?.id === d.id && shownDetail?.area === d.area} class:dead={d.status === 'superseded' || d.status === 'withdrawn'} href={href({ name: 'decisions', area, id: d.id })}>
                  <span class="id">{d.id}</span>
                  <span class="t">{d.title}</span>
                </a>
              </li>
            {/each}
          </ul>
        {/if}
      </section>
    {/each}
  </div>
  <div class="detail">
    {#if shownDetail}
      <a class="back btn small ghost" href={href({ name: 'decisions', area })}>← All decisions</a>
      {#key shownDetail.id}<DecisionView d={shownDetail} />{/key}
    {:else}
      <div class="pick faint">Choose a decision to read it.</div>
    {/if}
  </div>
</div>

<style>
  .dpage {
    display: grid;
    grid-template-columns: minmax(300px, 420px) 1fr;
    gap: 28px;
    align-items: start;
  }
  .index {
    position: sticky;
    top: 110px;
    max-height: calc(100dvh - 130px);
    overflow-y: auto;
    padding-right: 6px;
  }
  .tools {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 6px;
  }
  .find {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 12px;
    height: 38px;
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
    font-size: 14px;
  }
  .toggle {
    display: inline-flex;
    gap: 8px;
    align-items: center;
    font-size: 13px;
    color: var(--text-2);
  }
  .small {
    font-size: 12px;
    margin: 4px 0 8px;
  }
  .gh {
    display: flex;
    align-items: center;
    gap: 6px;
    width: 100%;
    padding: 8px 4px;
    background: none;
    border: 0;
    color: var(--text-2);
    font-weight: 620;
    font-size: 13px;
    text-align: left;
  }
  .gh span:nth-child(2) {
    flex: 1;
  }
  .n {
    color: var(--text-4);
    font-weight: 500;
  }
  .gh :global(.rot) {
    transform: rotate(-90deg);
  }
  ul {
    list-style: none;
    margin: 0 0 6px;
    padding: 0;
  }
  li a {
    display: grid;
    grid-template-columns: 52px 1fr;
    gap: 8px;
    padding: 6px 8px;
    border-radius: var(--r-1);
    color: var(--text-2);
    font-size: 13px;
    line-height: 1.4;
  }
  li a:hover {
    background: var(--surface-2);
    color: var(--foam);
  }
  li a.on {
    background: var(--surface-3);
    color: var(--foam);
  }
  li a.dead .t {
    text-decoration: line-through;
    text-decoration-color: var(--text-4);
    color: var(--text-3);
  }
  .t {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .detail {
    min-width: 0;
  }
  .back {
    display: none;
    margin-bottom: 10px;
  }
  .pick {
    padding: 80px 0;
    text-align: center;
  }
  @media (max-width: 900px) {
    .dpage {
      grid-template-columns: 1fr;
    }
    .index {
      position: static;
      max-height: none;
    }
    .dpage.has .index {
      display: none;
    }
    .dpage:not(.has) .detail {
      display: none;
    }
    .back {
      display: inline-flex;
    }
    .detail {
      padding-bottom: calc(40px + var(--tabbar));
    }
  }
</style>

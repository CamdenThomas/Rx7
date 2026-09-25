<!--
  Diagrams (D-417): the factory circuits, filed under the system 01-REFERENCE's `circuits`
  table names first, and the wiring diagram they were decoded from. With an id, that circuit's
  write-up in full.
-->
<script lang="ts">
  import { FileText } from '@lucide/svelte';
  import type { Circuit, Manual } from '../../lib/model';
  import { sources } from '../../lib/manual';
  import { href } from '../../lib/router.svelte';
  import { app } from '../../lib/app.svelte';
  import Prose from '../../components/Prose.svelte';

  let { m, id }: { m: Manual; id?: string } = $props();

  const key = (c: Circuit) => c.file.replace(/\.[^.]+$/, '');
  const one = $derived(id ? m.circuits.find((c) => key(c) === id) : undefined);
  const groups = $derived(
    [...m.systems.map((s) => ({ id: s.id, name: s.name })), { id: '', name: 'Other' }]
      .map((s) => ({
        ...s,
        rows: m.circuits.filter((c) => (s.id ? c.systems[0] === s.id : !m.systems.some((x) => x.id === c.systems[0]))),
      }))
      .filter((g) => g.rows.length),
  );
  const also = (c: Circuit) => c.systems.slice(1).map((x) => m.systems.find((s) => s.id === x)?.name ?? x);

  function openSource(c: Circuit) {
    const url = sources(c.source)[0]?.url;
    if (url) app.platform?.open(url);
  }
</script>

{#if id && !one}
  <p class="muted">No circuit {id}. <a href={href({ name: 'manual', page: 'diagrams' })}>Every diagram</a></p>
{:else if one}
  <article class="one">
    <header>
      <h2>{one.title}</h2>
      <p class="faint small">
        {[m.systems.find((s) => s.id === one.systems[0])?.name, ...also(one)].filter(Boolean).join(' · ')}
        {#each sources(one.source) as x (x.id)} · decoded from <span class="id" title={x.title}>{x.id}</span>{/each}
      </p>
    </header>
    {#if one.body}
      <div class="panel body"><Prose text={one.body} /></div>
    {:else}
      <p><button class="btn" onclick={() => openSource(one)}><FileText size={15} /> Open the scan</button></p>
    {/if}
  </article>
{:else}
  {#each groups as g (g.id)}
    <section>
      <h2>{g.name}</h2>
      <div class="cards">
        {#each g.rows as c (c.file)}
          {#if c.body}
            <a class="panel card" href={href({ name: 'manual', page: 'diagrams', id: key(c) })}>
              <strong>{c.title}</strong>
              {#if also(c).length}<span class="faint small">also {also(c).join(', ')}</span>{/if}
              {#if c.note}<span class="muted small">{c.note}</span>{/if}
            </a>
          {:else}
            <button class="panel card" onclick={() => openSource(c)}>
              <strong><FileText size={14} /> {c.title}</strong>
              {#if c.note}<span class="muted small">{c.note}</span>{/if}
            </button>
          {/if}
        {/each}
      </div>
    </section>
  {/each}
  {#if !groups.length}<p class="muted">No diagram is filed yet.</p>{/if}
{/if}

<style>
  section {
    margin-bottom: 22px;
  }
  h2 {
    font-size: 15px;
    margin: 0 0 8px;
  }
  .one h2 {
    font-size: 22px;
  }
  .one header {
    margin-bottom: 14px;
  }
  .one header p {
    margin: 4px 0 0;
  }
  .small {
    font-size: 13px;
  }
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 10px;
  }
  .card {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 12px 16px;
    color: var(--text);
    text-align: left;
    font: inherit;
    cursor: pointer;
    transition:
      border-color var(--t-fast),
      background var(--t-fast);
  }
  .card:hover {
    border-color: var(--line);
    background: var(--surface-2);
  }
  .card strong {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-weight: 600;
    font-size: 14.5px;
  }
  .body {
    padding: 8px 20px;
    overflow-x: auto;
  }
</style>

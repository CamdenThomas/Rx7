<!--
  Systems (D-417): the tree of the car's systems, each with its state now. Without an id, every
  system and the parts in it; with one, that system's page - its state, its parts by zone, its
  specs and its procedures.
-->
<script lang="ts">
  import type { Manual, ManualSystem } from '../../lib/model';
  import { day, value } from '../../lib/manual';
  import { href } from '../../lib/router.svelte';
  import PartLink from '../../components/PartLink.svelte';
  import Prose from '../../components/Prose.svelte';

  let { m, id }: { m: Manual; id?: string } = $props();

  const byOrder = (a: ManualSystem, b: ManualSystem) => Number(a.order) - Number(b.order);
  const top = $derived(m.systems.filter((s) => !s.parent).sort(byOrder));
  const kids = (s: ManualSystem) => m.systems.filter((x) => x.parent === s.id).sort(byOrder);
  const zoneName = (z: string) => m.zones.find((x) => x.id === z)?.name ?? (z || 'Not placed');

  const sys = $derived(id ? m.systems.find((s) => s.id === id) : undefined);
  const parent = $derived(sys?.parent ? m.systems.find((s) => s.id === sys.parent) : undefined);
  const family = $derived(sys ? [sys, ...kids(sys)] : []);
  const parts = $derived(m.parts.filter((p) => family.some((s) => s.id === p.system)));
  const byZone = $derived(
    [...new Set(parts.map((p) => p.zone))]
      .sort((a, b) => Number(m.zones.find((z) => z.id === a)?.order ?? 99) - Number(m.zones.find((z) => z.id === b)?.order ?? 99))
      .map((z) => ({ zone: z, parts: parts.filter((p) => p.zone === z) })),
  );
  const specs = $derived(m.specs.filter((s) => family.some((f) => f.id === s.system)));
  const procs = $derived(m.procedures.filter((p) => sys && [sys.id, sys.name].some((x) => p.system.toLowerCase() === x.toLowerCase())));
</script>

{#if id && !sys}
  <p class="muted">No system {id} in the Manual. <a href={href({ name: 'manual', page: 'systems' })}>Every system</a></p>
{:else if sys}
  <article class="one">
    <header>
      {#if parent}<a class="faint small" href={href({ name: 'manual', page: 'systems', id: parent.id })}>{parent.name}</a>{/if}
      <h2>{sys.name}</h2>
      <p class="state">{sys.state || 'Nothing recorded yet.'}</p>
      {#if sys.since}<p class="faint small">As it is since {day(sys.since)}</p>{/if}
      {#if sys.note}<p class="muted small">{sys.note}</p>{/if}
    </header>

    {#if kids(sys).length}
      <div class="chips">
        {#each kids(sys) as k (k.id)}<a class="chip cool" href={href({ name: 'manual', page: 'systems', id: k.id })}>{k.name}</a>{/each}
      </div>
    {/if}

    <section>
      <h3>Parts <span class="faint">{parts.length}</span></h3>
      {#if !parts.length}<p class="muted">No part of this system is in the Manual yet.</p>{/if}
      {#each byZone as g (g.zone)}
        <div class="zone">
          <span class="label">{zoneName(g.zone)}</span>
          <ul class="parts">
            {#each g.parts as p (p.id)}
              <li>
                <PartLink id={p.id} />
                <span class="faint small">{[p.maker, p.part_no || p.oem_no].filter(Boolean).join(' ')}</span>
              </li>
            {/each}
          </ul>
        </div>
      {/each}
    </section>

    {#if specs.length}
      <section>
        <h3>Specs <span class="faint">{specs.length}</span></h3>
        <div class="panel specs">
          {#each specs as s (s.id)}
            <div class="spec">
              <span>{s.item}{#if s.part}<span class="faint">&nbsp;· <PartLink id={s.part} /></span>{/if}</span>
              <span class="num">{value(s)}</span>
            </div>
          {/each}
        </div>
      </section>
    {/if}

    {#if procs.length}
      <section>
        <h3>Procedures</h3>
        {#each procs as p (p.id)}
          <details class="panel proc">
            <summary><strong>{p.title}</strong> <span class="faint small">{p.when}</span></summary>
            <Prose text={p.body} compact />
          </details>
        {/each}
      </section>
    {/if}
  </article>
{:else}
  <div class="tree">
    {#each top as s (s.id)}
      <section class="panel sys">
        <a class="name" href={href({ name: 'manual', page: 'systems', id: s.id })}>{s.name}</a>
        <p class="state small">{s.state || 'Nothing recorded yet.'}</p>
        {#each kids(s) as k (k.id)}
          <a class="kid" href={href({ name: 'manual', page: 'systems', id: k.id })}>{k.name}</a>
        {/each}
        <p class="list small">
          {#each m.parts.filter((p) => p.system === s.id) as p, n (p.id)}{n ? ' · ' : ''}<PartLink id={p.id} />{/each}
        </p>
      </section>
    {/each}
  </div>
{/if}

<style>
  .small {
    font-size: 13px;
  }
  .one header {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 14px;
  }
  h2 {
    font-size: 22px;
    margin: 0;
  }
  h3 {
    font-size: 15px;
    margin: 0 0 8px;
  }
  .state {
    color: var(--text-2);
    line-height: 1.55;
    margin: 0;
    max-width: 75ch;
  }
  header p {
    margin: 0;
  }
  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 16px;
  }
  section {
    margin-bottom: 24px;
  }
  .zone {
    margin-bottom: 12px;
  }
  .parts {
    list-style: none;
    margin: 6px 0 0;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 6px 18px;
  }
  .parts li {
    display: flex;
    flex-direction: column;
    gap: 1px;
    font-size: 14px;
  }
  .specs {
    padding: 0 16px;
  }
  .spec {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    padding: 9px 0;
    border-top: 1px solid var(--line-soft);
    font-size: 14px;
  }
  .spec:first-child {
    border-top: 0;
  }
  .spec .num {
    text-align: right;
    max-width: 50%;
  }
  .proc {
    padding: 12px 16px;
    margin-bottom: 8px;
  }
  .proc summary {
    cursor: pointer;
  }
  .tree {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 12px;
    align-items: start;
  }
  .sys {
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .name {
    font-weight: 650;
    font-size: 15.5px;
    color: var(--text);
  }
  .kid {
    font-size: 13.5px;
    font-weight: 560;
    color: var(--sky);
  }
  .sys .state,
  .list {
    margin: 0;
    line-height: 1.55;
  }
  .list {
    color: var(--text-3);
  }
  @media (max-width: 759px) {
    .tree {
      grid-template-columns: 1fr;
    }
  }
</style>

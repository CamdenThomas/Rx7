<!--
  A part's page (D-417): the Manual's basic unit. What it is and who makes it, where it sits,
  when it was fitted (read from the service visit, never typed), its specs, the service that
  touched it, what was bought for it, and who to call about it.
-->
<script lang="ts">
  import type { Manual } from '../../lib/model';
  import { day, miles, sources, system, value } from '../../lib/manual';
  import { href } from '../../lib/router.svelte';
  import { app } from '../../lib/app.svelte';
  import Linked from '../../components/Linked.svelte';

  let { m, id }: { m: Manual; id: string } = $props();

  const p = $derived(m.parts.find((x) => x.id === id));
  const sys = $derived(p ? system(p.system) : undefined);
  const zone = $derived(p ? m.zones.find((z) => z.id === p.zone) : undefined);
  const specs = $derived(m.specs.filter((s) => p?.specs.includes(s.id)));
  const visits = $derived(m.service.filter((s) => p?.service.includes(s.id)).sort((a, b) => b.date.localeCompare(a.date)));

  const facts = $derived(
    p
      ? [
          ['Maker', p.maker || (p.factory === 'yes' ? 'Mazda (factory)' : '')],
          ['Part number', p.part_no],
          ['Mazda number', p.oem_no],
          ['Factory code', p.factory_code],
          ['Catalogue', p.catalogue],
          ['Fitted', p.fitted ? `${day(p.fitted.date)}${p.fitted.miles != null ? ` at ${miles(p.fitted.miles)}` : ''}` : p.factory === 'yes' ? 'From the factory' : ''],
        ].filter(([, v]) => v)
      : [],
  );

  function go(e: MouseEvent, url: string) {
    e.preventDefault();
    app.platform?.open(url);
  }
</script>

{#if !p}
  <p class="muted">No part {id} in the Manual: it may be held back until it is checked. <a href={href({ name: 'manual', page: 'systems' })}>Every system</a></p>
{:else}
  <article>
    <header>
      <h2>{p.name}</h2>
      <p class="where">
        {#if sys}<a href={href({ name: 'manual', page: 'systems', id: sys.id })}>{sys.name}</a>{/if}
        {#if zone}<span>{zone.name}</span>{/if}
        <span class="id">{p.id}</span>
      </p>
      {#if p.note}<p class="note">{p.note}</p>{/if}
    </header>

    <div class="cols">
      <section class="panel facts">
        {#each facts as [k, v] (k)}
          <div class="fact"><span class="label">{k}</span><span>{v}</span></div>
        {/each}
        {#if p.link}
          <div class="fact"><span class="label">Where to buy</span><span><Linked text={p.link} /></span></div>
        {/if}
        {#if p.support}
          <div class="fact"><span class="label">Who to call</span><span><Linked text={p.support} /></span></div>
        {/if}
        {#if p.cad}
          <div class="fact"><span class="label">CAD</span><span><Linked text={p.cad} /></span></div>
        {/if}
      </section>

      <div class="side">
        {#if specs.length}
          <section>
            <h3>Specs</h3>
            <div class="panel list">
              {#each specs as s (s.id)}
                <div class="spec">
                  <span>{s.item}</span>
                  <span class="num">{value(s)}</span>
                  <span class="src">
                    {#each sources(s.source) as x (x.id)}
                      <a class="id" href={x.url || undefined} title={x.title} onclick={(e) => x.url && go(e, x.url)}>{x.id}</a>
                    {/each}
                  </span>
                </div>
              {/each}
            </div>
          </section>
        {/if}

        {#if visits.length}
          <section>
            <h3>Service</h3>
            <div class="panel list">
              {#each visits as s (s.id)}
                <div class="visit">
                  <strong>{s.work}</strong>
                  <span class="faint small">{day(s.date)}{s.mileage ? ` · ${miles(s.mileage)}` : ''}</span>
                </div>
              {/each}
            </div>
          </section>
        {/if}

        {#if p.bought.length}
          <section>
            <h3>Bought</h3>
            <ul class="bought">
              {#each p.bought as b (b.id)}<li>{b.part}{b.source ? ` · ${b.source}` : ''}</li>{/each}
            </ul>
          </section>
        {/if}
      </div>
    </div>
  </article>
{/if}

<style>
  header {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 16px;
  }
  h2 {
    font-size: 24px;
    margin: 0;
  }
  h3 {
    font-size: 15px;
    margin: 0 0 8px;
  }
  .where {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px 14px;
    margin: 0;
    color: var(--text-2);
    font-size: 14px;
  }
  .note {
    margin: 0;
    color: var(--text-2);
    max-width: 75ch;
    line-height: 1.55;
  }
  .cols {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.3fr);
    gap: 16px;
    align-items: start;
  }
  .facts {
    padding: 4px 16px;
  }
  .fact {
    display: flex;
    flex-direction: column;
    gap: 3px;
    padding: 10px 0;
    border-top: 1px solid var(--line-soft);
    font-size: 14px;
    overflow-wrap: anywhere;
  }
  .fact:first-child {
    border-top: 0;
  }
  .side section {
    margin-bottom: 18px;
  }
  .list {
    padding: 0 16px;
  }
  .spec {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) auto;
    gap: 12px;
    padding: 9px 0;
    border-top: 1px solid var(--line-soft);
    font-size: 14px;
  }
  .visit {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 9px 0;
    border-top: 1px solid var(--line-soft);
    font-size: 14px;
  }
  .spec:first-child,
  .visit:first-child {
    border-top: 0;
  }
  .src {
    display: flex;
    gap: 6px;
  }
  .small {
    font-size: 12.5px;
  }
  .bought {
    margin: 0;
    padding-left: 18px;
    color: var(--text-2);
    font-size: 14px;
  }
  @media (max-width: 859px) {
    .cols {
      grid-template-columns: 1fr;
    }
    .spec {
      grid-template-columns: 1fr auto;
    }
    .src {
      display: none;
    }
  }
</style>

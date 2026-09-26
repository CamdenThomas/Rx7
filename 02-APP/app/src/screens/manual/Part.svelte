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
  import PartLink from '../../components/PartLink.svelte';

  let { m, id }: { m: Manual; id: string } = $props();

  const p = $derived(m.parts.find((x) => x.id === id));
  const sys = $derived(p ? system(p.system) : undefined);
  const zone = $derived(p ? m.zones.find((z) => z.id === p.zone) : undefined);
  const specs = $derived(m.specs.filter((s) => p?.specs.includes(s.id)));
  // Its layers (D-429): the chain of parts it sits in, and what sits in it.
  const chain = $derived.by(() => {
    const out = [];
    let x = p ? m.parts.find((q) => q.id === p.parent) : undefined;
    while (x && out.length < 12) {
      out.unshift(x);
      x = m.parts.find((q) => q.id === x?.parent);
    }
    return out;
  });
  const visits = $derived(m.service.filter((s) => p?.service.includes(s.id)).sort((a, b) => b.date.localeCompare(a.date)));

  const facts = $derived(
    p
      ? [
          ['Maker', p.maker || (p.factory === 'yes' ? 'Mazda (factory)' : '')],
          ['Part number', p.part_no],
          ['Mazda number', p.oem_no],
          ['Factory code', p.factory_code],
          ['Fitted', p.fitted ? `${day(p.fitted.date)}${p.fitted.miles != null ? ` at ${miles(p.fitted.miles)}` : ''}` : p.factory === 'yes' ? 'From the factory' : ''],
        ].filter(([, v]) => v)
      : [],
  );

  function go(e: MouseEvent, url: string) {
    e.preventDefault();
    app.platform?.open(url);
  }

  /** A held-back part still gets a page (plan P40): its row from 00-CAR, greyed, with the
   *  reason the Manual holds it and the verify row that would settle it. */
  const heldPart = $derived.by(() => {
    if (p) return null;
    const t = app.snapshot?.tables.find((x) => x.area === '00-CAR' && x.table === 'parts');
    const r = t?.rows.find((x) => x[t.columns.indexOf('id')] === id);
    if (!t || !r) return null;
    const col = (c: string) => r[t.columns.indexOf(c)] ?? '';
    const held = m.held.find((h) => h.table === 'parts' && h.key === id);
    const verify = (app.snapshot?.work ?? []).find((w) => w.area === '00-verify' && w.owner === 'camden' && w.status !== 'done' && new RegExp(`\\b${id}\\b`).test(w.item));
    return { name: col('name'), maker: col('maker'), part_no: col('part_no') || col('oem_no'), system: col('system'), zone: col('zone'), note: col('note'), applies: col('applies'), why: held?.why ?? '', verify };
  });
  const catalogueRows = $derived((p?.catalogue ?? '').split(/\s+/).filter(Boolean));
</script>

{#if !p && heldPart}
  <article class="held">
    <header>
      <h2>{heldPart.name} <span class="chip quiet">{heldPart.applies || 'held back'}</span></h2>
      <p class="where"><span>{heldPart.system}</span>{#if heldPart.zone}<span>{heldPart.zone}</span>{/if}<span class="id">{id}</span></p>
      <p class="muted">{heldPart.applies ? `Not a fact about the car now (${heldPart.applies}).` : `The Manual holds this part back: ${heldPart.why || 'not yet checked on the car'}.`}
        {#if heldPart.verify}It is your row <a href={href({ name: 'todo', area: '00-verify', id: heldPart.verify.id })}>{heldPart.verify.id}</a> in Verify.{/if}</p>
      {#if heldPart.note}<p class="note">{heldPart.note}</p>{/if}
      <p class="faint small">{[heldPart.maker, heldPart.part_no].filter(Boolean).join(' · ')}</p>
    </header>
  </article>
{:else if !p}
  <p class="muted">No part {id} in the record. <a href={href({ name: 'manual', page: 'systems' })}>Every system</a></p>
{:else}
  <article>
    <header>
      <h2>{p.name}</h2>
      <p class="where">
        {#if sys}<a href={href({ name: 'manual', page: 'systems', id: sys.id })}>{sys.name}</a>{/if}
        {#if zone}<span>{zone.name}</span>{/if}
        <span class="id">{p.id}</span>
      </p>
      {#if chain.length}
        <p class="chain">Part of {#each chain as c, i (c.id)}{i ? ' › ' : ''}<PartLink id={c.id} />{/each}</p>
      {/if}
      {#if p.note}<p class="note">{p.note}</p>{/if}
    </header>

    <div class="cols">
      <section class="panel facts">
        {#each facts as [k, v] (k)}
          <div class="fact"><span class="label">{k}</span><span>{v}</span></div>
        {/each}
        {#if catalogueRows.length}
          <div class="fact"><span class="label">Catalogue</span><span>{#each catalogueRows as c, i (c)}{i ? ' ' : ''}<a class="id" href={href({ name: 'row', area: '01-REFERENCE', table: 'catalogue', key: c })}>{c}</a>{/each}</span></div>
        {/if}
        {#if p.photo}
          <div class="fact photo"><img src={app.platform?.photo(p.photo)} alt={p.name} /></div>
        {/if}
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
        {#if p.children.length}
          <section>
            <h3>Inside it <span class="faint">{p.children.length}</span></h3>
            <ul class="inside">
              {#each p.children as c (c)}<li><PartLink id={c} />{#if m.parts.find((q) => q.id === c)?.children.length}<span class="faint">&nbsp;· {m.parts.find((q) => q.id === c)?.children.length} inside</span>{/if}</li>{/each}
            </ul>
          </section>
        {/if}

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

        {#if p.terminals_held}
          <p class="faint small held">Factory wiring: {p.terminals_held} terminal{p.terminals_held === 1 ? '' : 's'} recorded from the 1982 diagram, held back until checked on the car.</p>
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
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 130px;
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
  .chain {
    margin: 0;
    font-size: 13.5px;
    color: var(--text-3);
  }
  .inside {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 6px 16px;
    font-size: 14px;
  }
  .held {
    margin: 0 0 18px;
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

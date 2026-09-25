<!--
  The Manual (D-417): the car as it is now, verified facts only, and every page a different
  query over the same rows. Car state is its front page; Systems, The car, Specs, Service and
  Diagrams are the presets he asked for (his 4.2), and each part has a page of its own. All of it
  is `manual` in rx7.py's export - nothing on these pages is worked out here.
-->
<script lang="ts">
  import { Gauge, Route as RouteIcon } from '@lucide/svelte';
  import DriveDialog from '../components/DriveDialog.svelte';
  import State from './manual/State.svelte';
  import Specs from './manual/Specs.svelte';
  import Service from './manual/Service.svelte';
  import { app } from '../lib/app.svelte';
  import { day, miles } from '../lib/manual';
  import { href, type ManualPage } from '../lib/router.svelte';
  import { MANUAL_TITLE, ui } from '../lib/ui.svelte';

  let { page = 'state', id }: { page?: ManualPage; id?: string } = $props();

  const m = $derived(app.snapshot?.manual);
  const v = $derived(Object.fromEntries((m?.vehicle ?? []).map((r) => [r.key, r.value])));
  const odo = $derived(m?.odometer);
  // A drive saved and not yet filed: the reading he gave is the newest thing he knows.
  const pending = $derived(
    (app.snapshot?.inbox ?? []).filter((a) => a.area === '00-CAR' && a.kind === 'drive').sort((a, b) => b.at.localeCompare(a.at))[0],
  );
  const ODO_FROM: Record<string, string> = { drive: 'a logged drive', set: 'a Set odo', service: 'the service log', vehicle: 'an undated note' };

  let dialog = $state<'drive' | 'odo' | null>(null);

  const TABS: ManualPage[] = ['state', 'specs', 'service'];
  const on = (t: ManualPage) => (page === 'part' ? t === 'systems' : page === t);

  $effect(() => {
    ui.context = `the Manual, ${MANUAL_TITLE[page]}${id ? ` ${id}` : ''}`;
    return () => (ui.context = '');
  });
</script>

{#if !m}
  <div class="page narrow"><p class="muted">This copy of the record was made before the Manual existed. Refresh to read it again.</p></div>
{:else}
  <div class="page manual">
    <header class="head">
      <div class="who">
        <p class="label">Manual</p>
        <h1>{[v.year_model, v.trim].filter(Boolean).join(' ')}</h1>
        <p class="ident">
          {#each [v.generation && `${v.generation} chassis`, v.colour, v.engine, v.transmission].filter(Boolean) as x, i (i)}
            <span>{x}</span>
          {/each}
        </p>
      </div>
      <div class="odo panel">
        <span class="label">Odometer</span>
        {#if pending}
          <strong class="num">{miles(Number(pending.choice))}</strong>
          <span class="faint small">you saved this {day(pending.at.slice(0, 10))} · waiting to be filed</span>
        {:else if odo?.miles != null}
          <strong class="num">{miles(odo.miles)}</strong>
          <span class="faint small">{odo.date ? day(odo.date) : 'date not recorded'} · from {ODO_FROM[odo.source] ?? odo.source}</span>
        {:else}
          <strong class="faint">No reading yet</strong>
        {/if}
        <div class="acts">
          <button class="btn small" onclick={() => (dialog = 'drive')}><RouteIcon size={14} /> Log drive</button>
          <button class="btn small ghost" onclick={() => (dialog = 'odo')}><Gauge size={14} /> Set odo</button>
        </div>
      </div>
    </header>

    <nav class="tabs" aria-label="Manual pages">
      {#each TABS as t (t)}
        <a href={href({ name: 'manual', page: t })} class:on={on(t)} aria-current={on(t) ? 'page' : undefined}>{MANUAL_TITLE[t]}</a>
      {/each}
    </nav>

    <div class="content">
      {#if page === 'state'}
        <State {m} />
      {:else if page === 'specs'}
        <Specs {m} />
      {:else if page === 'service'}
        <Service {m} />
      {/if}
    </div>
  </div>
  {#if dialog}<DriveDialog mode={dialog} onclose={() => (dialog = null)} />{/if}
{/if}

<style>
  .manual {
    padding-top: 14px;
  }
  .head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 20px;
    flex-wrap: wrap;
    margin-bottom: 18px;
  }
  h1 {
    font-size: clamp(26px, 3.2vw, 36px);
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 6px 0 6px;
  }
  .ident {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 14px;
    color: var(--text-2);
    font-size: 14px;
    margin: 0;
  }
  .ident span + span::before {
    content: '·';
    margin-right: 14px;
    color: var(--text-4);
  }
  .odo {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2px;
    padding: 12px 16px;
    min-width: 260px;
  }
  .odo strong {
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.01em;
  }
  .small {
    font-size: 12.5px;
  }
  .acts {
    display: flex;
    gap: 6px;
    margin-top: 8px;
  }
  .tabs {
    display: flex;
    gap: 2px;
    border-bottom: 1px solid var(--line-soft);
    margin-bottom: 20px;
    overflow-x: auto;
    scrollbar-width: none;
  }
  .tabs::-webkit-scrollbar {
    display: none;
  }
  .tabs a {
    position: relative;
    padding: 10px 14px 12px;
    color: var(--text-3);
    font-weight: 560;
    font-size: 14.5px;
    white-space: nowrap;
  }
  .tabs a:hover {
    color: var(--text);
  }
  .tabs a.on {
    color: var(--foam);
  }
  .tabs a.on::after {
    content: '';
    position: absolute;
    left: 10px;
    right: 10px;
    bottom: -1px;
    height: 2px;
    border-radius: 2px;
    background: var(--ember);
  }
  @media (max-width: 759px) {
    .odo {
      width: 100%;
    }
    .tabs {
      margin: 0 calc(-1 * var(--gutter)) 16px;
      padding: 0 var(--gutter);
    }
    .tabs a {
      padding: 10px 10px 12px;
    }
  }
</style>

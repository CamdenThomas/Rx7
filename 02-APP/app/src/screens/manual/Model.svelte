<!--
  The car as a model (05-cad D-477, D-518; 02-APP MG1): the whole car part by part, every
  part a solid of its own - taken apart and put back together with a slider, filtered by
  system and zone, any part isolated or looked at alone with what holds it. It reads
  public/design/00-CAR/scene.json (the same contract as a project's Design page, plus the
  car's systems, zones and mates) and the harness's scene as a layer. A view only: nothing
  is measured, moved or edited here (R11; blocks 05.03 and 01.39 are open).
-->
<script lang="ts">
  import { onMount } from 'svelte';
  import { ArrowLeft, ChevronRight, Expand, Maximize, Tags } from '@lucide/svelte';
  import DesignCanvas from '../../components/DesignCanvas.svelte';
  import {
    builtLabel,
    bySystemZone,
    carScene,
    CAR_BASE,
    defaultToggles,
    fetchScene,
    filteredOut,
    KIND_LABEL,
    listedChildren,
    mergeScenes,
    partById,
    systemOf,
    tap,
    zoneOf,
    type Load,
    type Part,
    type Scene,
    type Selection,
    type Toggles,
  } from '../../lib/design';
  import type { LoadState, Mode } from '../../lib/designView';
  import { href } from '../../lib/router.svelte';

  let { id, alone = false }: { id?: string; alone?: boolean } = $props();

  const HARNESS_BASE = '/design/01-electrical/';
  let load = $state<Load>({ state: 'loading' });
  let harness = $state<Scene | null>(null); // the electrical scene, when it is exported
  let harnessOn = $state(false);

  onMount(async () => {
    load = await carScene();
    const h = await fetchScene(HARNESS_BASE);
    harness = h.state === 'ok' ? h.scene : null;
  });

  const car = $derived(load.state === 'ok' ? load.scene : null);
  const scene = $derived(
    car && harness && harnessOn ? mergeScenes(car, harness, 'harness:', HARNESS_BASE, { id: 'harness', name: 'Harness' }) : car,
  );
  const part = $derived(scene && id ? partById(scene, id) : undefined);
  const mode = $derived<Mode>(alone && id ? (part?.kind === 'pcb' ? { kind: 'board', id } : { kind: 'part', id }) : { kind: 'assembly' });
  const modeKey = $derived(`${mode.kind === 'assembly' ? 'assembly' : `${mode.kind}:${mode.id}`}:${harnessOn && harness ? 'h' : ''}`);

  let selection = $state<Selection>(null);
  let chosen = $state(new Set<string>());
  let zone = $state('');
  let apart = $state(0);
  let hidden = $state(new Set<string>());
  let found = $state<{ case: boolean; inside: boolean } | null>(null);
  let status = $state<Record<string, LoadState>>({});
  let canvas = $state<ReturnType<typeof DesignCanvas>>();
  let viewEl = $state<HTMLElement>();
  let toggles = $state<Toggles>({ legs: true, links: false, connectors: true, labels: true });
  let toggledFor: Scene | null = null;
  $effect(() => {
    if (scene && scene !== toggledFor) {
      toggledFor = scene;
      toggles = { ...defaultToggles(scene), labels: toggles.labels };
    }
  });

  // #/manual/model/<id> opens the model with that part isolated (the part page's link).
  $effect(() => {
    if (!alone) selection = id ? { kind: 'part', id } : null;
    hidden = new Set();
    found = null;
  });

  const dimmed = $derived(scene ? filteredOut(scene, chosen, zone) : new Set<string>());
  const groups = $derived(scene ? bySystemZone(scene) : []);
  const zones = $derived(scene ? [...new Set(scene.parts.map((p) => zoneOf(scene, p.id)).filter(Boolean))].sort() : []);
  const systems = $derived(scene ? scene.systems : []);
  const selPart = $derived(scene && selection?.kind === 'part' ? partById(scene, selection.id) : undefined);
  const failed = $derived(scene ? scene.parts.filter((p) => status[p.id]?.state === 'failed') : []);

  const name = (pid: string) => (scene && partById(scene, pid)?.name) || pid;
  const sysName = (sid: string) => systems.find((x) => x.id === sid)?.name ?? (sid || 'no system');
  const heldBy = (pid: string) => scene?.parts.filter((p) => p.joint?.to === pid) ?? [];
  const xyz = (v: { x: number; y: number; z: number }) => `x ${v.x} · y ${v.y} · z ${v.z} mm`;

  function choose(next: Selection) {
    selection = tap(selection, next);
  }
  function chooseFromList(next: Selection) {
    choose(next);
    viewEl?.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }
  function pickSystem(sid: string | null) {
    if (sid === null) chosen = new Set();
    else {
      const c = new Set(chosen);
      if (c.has(sid)) c.delete(sid);
      else c.add(sid);
      chosen = c;
    }
  }
  function toggle(key: string) {
    const h = new Set(hidden);
    if (h.has(key)) h.delete(key);
    else h.add(key);
    hidden = h;
  }
</script>

{#snippet stateChip(p: Part)}
  {#if p.state}<span class="chip" class:accent={p.state === 'rough'} class:cool={p.state === 'confirmed'}>{p.state}</span>{/if}
{/snippet}

{#snippet facts(p: Part)}
  <dl class="facts">
    {#if p.origin}<dt>What it is</dt><dd>{p.origin}</dd>{/if}
    <dt>System</dt>
    <dd>{sysName(systemOf(scene!, p.id))}{zoneOf(scene!, p.id) ? ` · ${zoneOf(scene!, p.id)}` : ''}</dd>
    <dt>Known from</dt>
    <dd>{p.made_from || 'not said'}{p.state ? ` · ${p.state}` : ''}</dd>
    {#if p.joint}
      <dt>Held</dt>
      <dd>
        {p.joint.kind || 'held'} to {name(p.joint.to)}
        {#if p.joint.fasteners.length}<br /><span class="faint">with</span> {p.joint.fasteners.join(', ')}{/if}
      </dd>
      {#if p.joint.apart}<dt>Comes apart</dt><dd>{xyz(p.joint.apart)}</dd>{/if}
    {/if}
    {#if p.size_mm}<dt>Size</dt><dd>{p.size_mm.x} × {p.size_mm.y} × {p.size_mm.z} mm</dd>{/if}
    <dt>Place from</dt>
    <dd>{p.place_from || 'not said'}{#if p.confirm}<span class="warn">{' - '}not confirmed; nothing here is measured</span>{/if}</dd>
    {#if p.source}<dt>Design file</dt><dd class="mono small">{p.source}</dd>{/if}
  </dl>
{/snippet}

{#if load.state === 'loading'}
  <p class="muted">Reading the model…</p>
{:else if load.state === 'none'}
  <div class="empty panel" data-testid="model-state">
    <p><strong>No model of the car exported yet.</strong></p>
    <p class="faint small">This page shows what the car's model export writes to <span class="mono">{CAR_BASE.slice(1)}scene.json</span>; until then <a href={href({ name: 'manual', page: 'car' })}>The car</a> has the pictures.</p>
  </div>
{:else if load.state === 'error'}
  <div class="empty panel" data-testid="model-state"><p><strong>The model's scene file could not be read:</strong> {load.reason}.</p></div>
{:else if scene}
  <p class="meta faint small">Exported {builtLabel(scene.built)} · {groups.reduce((n, g) => n + g.zones.reduce((m, z) => m + z.parts.length, 0), 0)} parts · a picture of the design, nothing measured from it</p>
  {#if failed.length}
    <div class="alert" role="status">
      <p>Could not load {failed.map((p) => p.name).join(', ')}. A box of each one's size stands in; the rest is shown.</p>
    </div>
  {/if}

  {#if id && alone && !part}
    <div class="empty panel">
      <p>There is no part <span class="mono">{id}</span> in the model.</p>
      <a class="btn small" href={href({ name: 'manual', page: 'model' })}><ArrowLeft size={15} /> The whole car</a>
    </div>
  {:else if alone && part}
    <div class="head-row">
      <a class="btn small ghost back" href={href({ name: 'manual', page: 'model', id: part.id })}><ArrowLeft size={15} /> The car</a>
      <h2>{part.name}</h2>
      <span class="chip">{KIND_LABEL[part.kind]}</span>
      {@render stateChip(part)}
    </div>
    <div class="layout">
      <div class="view">
        {#key modeKey}
          <DesignCanvas bind:this={canvas} {scene} base={CAR_BASE} {mode} {hidden} {toggles} onstatus={(pid, s) => (status = { ...status, [pid]: s })} onnodes={(f) => (found = f)} />
        {/key}
        <div class="controls" role="group" aria-label="View controls">
          {#if part.nodes.case.length}
            <button class="btn" aria-pressed={!hidden.has('case')} class:cool={!hidden.has('case')} disabled={found?.case === false} onclick={() => toggle('case')}>Case</button>
          {/if}
          {#if part.nodes.inside.length}
            <button class="btn" aria-pressed={!hidden.has('inside')} class:cool={!hidden.has('inside')} disabled={found?.inside === false} onclick={() => toggle('inside')}>Insides</button>
          {/if}
          {#each listedChildren(scene, part.id) as c (c.id)}
            <button class="btn" aria-pressed={!hidden.has(c.id)} class:cool={!hidden.has(c.id)} onclick={() => toggle(c.id)}>{c.name}</button>
          {/each}
          <button class="btn icon" aria-pressed={toggles.labels} class:cool={toggles.labels} aria-label="Labels" title="Labels" onclick={() => (toggles = { ...toggles, labels: !toggles.labels })}><Tags size={17} /></button>
          <button class="btn icon" aria-label="Fit to view" title="Fit to view" onclick={() => canvas?.fit()}><Maximize size={17} /></button>
        </div>
      </div>
      <aside class="side">
        <details open><summary>About</summary>{@render facts(part)}</details>
        {#if listedChildren(scene, part.id).length}
          <details open>
            <summary>On it <span class="n">{listedChildren(scene, part.id).length}</span></summary>
            <ul class="list">
              {#each listedChildren(scene, part.id) as c (c.id)}
                <li><a class="item" href={href({ name: 'manual', page: 'model-part', id: c.id })}><span class="row-main">{c.name}{@render stateChip(c)}<ChevronRight size={16} class="go" /></span></a></li>
              {/each}
            </ul>
          </details>
        {/if}
        {#if heldBy(part.id).length}
          <details open>
            <summary>Held to it <span class="n">{heldBy(part.id).length}</span></summary>
            <ul class="list">
              {#each heldBy(part.id) as c (c.id)}
                <li>
                  <a class="item" href={href({ name: 'manual', page: 'model-part', id: c.id })}>
                    <span class="row-main">{c.name}<span class="faint small">{c.joint?.kind}</span><ChevronRight size={16} class="go" /></span>
                    {#if c.joint?.fasteners.length}<span class="row-sub faint">{c.joint.fasteners.join(', ')}</span>{/if}
                  </a>
                </li>
              {/each}
            </ul>
          </details>
        {/if}
      </aside>
    </div>
  {:else}
    <div class="layout">
      <div class="view" bind:this={viewEl}>
        {#key modeKey}
          <DesignCanvas
            bind:this={canvas}
            {scene}
            base={CAR_BASE}
            {mode}
            {selection}
            {toggles}
            {apart}
            {dimmed}
            onpick={choose}
            onstatus={(pid, s) => (status = { ...status, [pid]: s })}
          />
        {/key}
        <div class="controls" role="group" aria-label="View controls">
          {#if selection}
            <button class="btn primary" onclick={() => (selection = null)}><ArrowLeft size={16} /> Show everything</button>
            <span class="muted small sel">{selPart?.name ?? ''}</span>
          {:else}
            <span class="faint small sel">Tap a part to isolate it.</span>
          {/if}
          <button class="btn icon" aria-pressed={toggles.labels} class:cool={toggles.labels} aria-label="Labels" title="Labels" onclick={() => (toggles = { ...toggles, labels: !toggles.labels })}><Tags size={17} /></button>
          <button class="btn icon" aria-label="Fit to view" title="Fit to view" onclick={() => canvas?.fit()}><Maximize size={17} /></button>
          <button class="btn icon" aria-label="Fit everything, far ends included" title="Fit everything, far ends included" onclick={() => canvas?.fit(true)}><Expand size={17} /></button>
        </div>
        <label class="apart">
          <span class="small">Taken apart</span>
          <input type="range" min="0" max="1" step="0.01" bind:value={apart} aria-label="Taken apart" />
          <span class="faint small num">{Math.round(apart * 100)}%</span>
        </label>
        <div class="controls" role="group" aria-label="Systems">
          <button class="btn" aria-pressed={!chosen.size} class:cool={!chosen.size} onclick={() => pickSystem(null)}>All</button>
          {#each systems as x (x.id)}
            <button class="btn" aria-pressed={chosen.has(x.id)} class:cool={chosen.has(x.id)} onclick={() => pickSystem(x.id)}>{x.name}</button>
          {/each}
          {#if harness}
            <button class="btn" aria-pressed={harnessOn} class:cool={harnessOn} onclick={() => (harnessOn = !harnessOn)}>Harness</button>
          {/if}
          {#if zones.length > 1}
            <select class="select zone" bind:value={zone} aria-label="Zone">
              <option value="">Every zone</option>
              {#each zones as z (z)}<option value={z}>{z}</option>{/each}
            </select>
          {/if}
        </div>
      </div>

      <aside class="side">
        {#if selPart}
          <section class="panel picked" aria-label="Isolated part">
            <div class="row-main"><strong>{selPart.name}</strong><span class="chip">{KIND_LABEL[selPart.kind]}</span>{@render stateChip(selPart)}</div>
            {@render facts(selPart)}
            <a class="btn cool" href={href({ name: 'manual', page: 'model-part', id: selPart.id })}>This part alone <ChevronRight size={16} /></a>
          </section>
        {/if}
        {#each groups as g (g.system)}
          <details open>
            <summary>{g.name} <span class="n">{g.zones.reduce((n, z) => n + z.parts.length, 0)}</span></summary>
            {#each g.zones as z (z.zone)}
              {#if z.zone}<p class="zone-head label">{z.zone}</p>{/if}
              <ul class="list">
                {#each z.parts as p (p.id)}
                  <li>
                    <div class="pair">
                      <button class="item" class:on={selection?.kind === 'part' && selection.id === p.id} aria-pressed={selection?.kind === 'part' && selection.id === p.id} onclick={() => chooseFromList({ kind: 'part', id: p.id })}>
                        <span class="row-main">{p.name}{@render stateChip(p)}</span>
                        <span class="row-sub faint">{KIND_LABEL[p.kind]}{p.made_from ? ` · ${p.made_from}` : ''}{p.joint ? ` · ${p.joint.kind} to ${name(p.joint.to)}` : ''}</span>
                      </button>
                      <a class="btn ghost icon open" href={href({ name: 'manual', page: 'model-part', id: p.id })} aria-label="{p.name} alone"><ChevronRight size={18} /></a>
                    </div>
                  </li>
                {/each}
              </ul>
            {/each}
          </details>
        {/each}
        {#if scene.notes.length}
          <details>
            <summary>Notes <span class="n">{scene.notes.length}</span></summary>
            <ul class="list">{#each scene.notes as n, i (i)}<li class="item static"><span class="row-sub">{n}</span></li>{/each}</ul>
          </details>
        {/if}
        {#if load.problems.length}
          <details>
            <summary>Read with problems <span class="n">{load.problems.length}</span></summary>
            <ul class="list">{#each load.problems as pr, i (i)}<li class="item static"><span class="row-sub">{pr}</span></li>{/each}</ul>
          </details>
        {/if}
      </aside>
    </div>
  {/if}
{/if}

<style>
  .empty {
    padding: 22px;
    display: grid;
    gap: 10px;
    justify-items: start;
  }
  .meta {
    margin: 0 0 12px;
  }
  .alert {
    margin-bottom: 12px;
    padding: 10px 14px;
    border-radius: var(--r-2);
    border: 1px solid var(--accent-line);
    background: var(--accent-soft);
    color: var(--accent-2);
    font-size: 13.5px;
  }
  .head-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
  }
  .head-row h2 {
    font-size: 19px;
  }
  .back {
    min-height: var(--tap);
  }
  .layout {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(300px, 380px);
    gap: 18px;
    align-items: start;
  }
  .view {
    position: sticky;
    top: calc(var(--topbar) + 12px);
    scroll-margin-top: calc(var(--topbar) + 12px);
    display: grid;
    gap: 10px;
  }
  .view > :global(.stage) {
    height: clamp(340px, calc(100dvh - var(--topbar) - 300px), 720px);
  }
  .controls {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }
  .controls .btn {
    min-height: var(--tap);
  }
  .controls .btn.icon {
    width: var(--tap);
  }
  .sel {
    flex: 1;
    min-width: 0;
  }
  .apart {
    display: flex;
    align-items: center;
    gap: 12px;
    min-height: var(--tap);
  }
  .apart input {
    flex: 1;
    accent-color: var(--ember);
    min-height: 32px;
  }
  .zone {
    width: auto;
    min-height: var(--tap);
  }
  .side {
    display: grid;
    gap: 12px;
    min-width: 0;
  }
  details {
    border: 1px solid var(--line-soft);
    border-radius: var(--r-3);
    background: var(--surface);
  }
  summary {
    display: flex;
    align-items: center;
    gap: 8px;
    min-height: var(--tap);
    padding: 0 14px;
    font-weight: 620;
    cursor: pointer;
    list-style: none;
  }
  summary::-webkit-details-marker {
    display: none;
  }
  .n {
    font-size: 12px;
    color: var(--text-3);
    font-weight: 560;
  }
  .zone-head {
    margin: 6px 16px 2px;
  }
  .list {
    list-style: none;
    padding: 0 6px 8px;
    margin: 0;
    display: grid;
    gap: 2px;
  }
  .pair {
    display: flex;
    align-items: stretch;
    gap: 2px;
  }
  .pair .item {
    flex: 1;
  }
  .open {
    min-height: var(--tap);
    width: var(--tap);
    align-self: center;
  }
  .item {
    display: grid;
    gap: 3px;
    width: 100%;
    min-height: var(--tap);
    padding: 8px 10px;
    border: 1px solid transparent;
    border-radius: var(--r-2);
    background: none;
    color: var(--text);
    text-align: left;
    font: inherit;
    cursor: pointer;
  }
  a.item {
    text-decoration: none;
  }
  .item.static {
    cursor: default;
  }
  .item.on {
    background: var(--accent-soft);
    border-color: var(--accent-line);
  }
  .row-main {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px 8px;
    font-size: 14.5px;
    font-weight: 560;
  }
  .row-main :global(.go) {
    margin-left: auto;
    color: var(--text-3);
  }
  .row-sub {
    font-size: 13px;
    color: var(--text-2);
    overflow-wrap: anywhere;
  }
  .warn {
    color: var(--accent-2);
  }
  .picked {
    padding: 14px;
    display: grid;
    gap: 10px;
    justify-items: start;
  }
  .facts {
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: 6px 12px;
    padding: 0 14px 12px;
    margin: 0;
    font-size: 13.5px;
  }
  .picked .facts {
    padding: 0;
  }
  .facts dt {
    color: var(--text-3);
  }
  .facts dd {
    margin: 0;
    overflow-wrap: anywhere;
  }
  @media (max-width: 899px) {
    .layout {
      grid-template-columns: minmax(0, 1fr);
    }
    .view {
      position: static;
    }
    .view > :global(.stage) {
      height: min(58dvh, 440px);
      min-height: 280px;
    }
    .facts {
      grid-template-columns: minmax(0, 1fr);
      gap: 2px;
    }
    .facts dd {
      margin-bottom: 6px;
    }
  }
</style>

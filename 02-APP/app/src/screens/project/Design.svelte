<!--
  The project's design in 3D (D-505, work row M3D1): the assembly with its labelled
  connector-to-connector links, any part isolated by a tap; each part's own view with its
  insides toggled; each board top and bottom. At scene version 2 (01-electrical D-514, M3D2)
  the harness too: the legs as tubes, every connector at its place, a Connectors list by leg
  that opens a housing's cavities, and toggles for each layer. Everything comes from
  public/design/<project>/scene.json and its models, exported from the design by
  01-electrical Y23 - a view of the design, never a source of facts (R11), and nothing on it
  is typed back into the record.
-->
<script lang="ts">
  import { onMount } from 'svelte';
  import { ArrowLeft, ChevronRight, Expand, Maximize, Tags } from '@lucide/svelte';
  import DesignCanvas from '../../components/DesignCanvas.svelte';
  import {
    builtLabel,
    byLeg,
    bytesLabel,
    childrenOf,
    defaultToggles,
    drawnIds,
    family,
    housingsOf,
    isConnector,
    KIND_LABEL,
    legColourCss,
    legRadius,
    listedChildren,
    listedTop,
    looksAbsent,
    parseScene,
    partById,
    tap,
    type Housing,
    type Part,
    type Scene,
    type Selection,
    type Toggles,
  } from '../../lib/design';
  import type { LoadState, Mode } from '../../lib/designView';
  import { href } from '../../lib/router.svelte';

  let { area, id }: { area: string; id?: string } = $props();

  type Load = { state: 'loading' } | { state: 'none' } | { state: 'error'; reason: string } | { state: 'ok'; scene: Scene; problems: string[] };
  let load = $state<Load>({ state: 'loading' });
  const base = $derived(`/design/${encodeURIComponent(area)}/`);

  onMount(async () => {
    try {
      const res = await fetch(`${base}scene.json`, { cache: 'no-cache' });
      const body = await res.text();
      if (!res.ok || looksAbsent(res.status, body)) {
        load = { state: 'none' };
        return;
      }
      let raw: unknown;
      try {
        raw = JSON.parse(body);
      } catch (e) {
        load = { state: 'error', reason: `it is not JSON (${e instanceof Error ? e.message : e})` };
        return;
      }
      const p = parseScene(raw);
      load = p.ok ? { state: 'ok', scene: p.scene, problems: p.problems } : { state: 'error', reason: p.reason };
    } catch {
      // A packaged app that has no such file fails the fetch itself.
      load = { state: 'none' };
    }
  });

  const scene = $derived(load.state === 'ok' ? load.scene : null);
  const part = $derived(scene && id ? partById(scene, id) : undefined);
  const mode = $derived<Mode>(!id ? { kind: 'assembly' } : part?.kind === 'pcb' ? { kind: 'board', id } : { kind: 'part', id: id });
  const modeKey = $derived(mode.kind === 'assembly' ? 'assembly' : `${mode.kind}:${mode.id}`);

  let selection = $state<Selection>(null);
  let hidden = $state(new Set<string>());
  let side = $state<'top' | 'bottom'>('top');
  // the assembly's layers; a new scene starts from its own defaults (legs on, links off)
  let toggles = $state<Toggles>({ legs: false, links: true, connectors: true, labels: true });
  let toggledFor: Scene | null = null;
  $effect(() => {
    if (scene && scene !== toggledFor) {
      toggledFor = scene;
      toggles = defaultToggles(scene);
    }
  });
  const flip = (k: keyof Toggles) => (toggles = { ...toggles, [k]: !toggles[k] });
  let found = $state<{ case: boolean; inside: boolean } | null>(null);
  let status = $state<Record<string, LoadState>>({});
  let canvas = $state<ReturnType<typeof DesignCanvas>>();

  // A new part view starts with everything shown, from the top.
  $effect(() => {
    void id;
    hidden = new Set();
    side = 'top';
    found = null;
  });

  const name = (pid: string) => (scene && partById(scene, pid)?.name) || pid || '(none)';
  // The models this view draws: the assembly's parts and connectors, or one part and what is inside it.
  const shown = $derived(new Set(scene ? (id ? [...family(scene, id)] : drawnIds(scene)) : []));
  // A model that does not load, once per file however many parts share it (a connector family).
  const failed = $derived.by(() => {
    const out = new Map<string, { names: string[]; why: string }>();
    for (const p of scene?.parts ?? []) {
      const st = status[p.id];
      if (!shown.has(p.id) || st?.state !== 'failed') continue;
      const f = out.get(p.glb ?? p.id) ?? { names: [], why: st.why };
      f.names.push(p.name);
      out.set(p.glb ?? p.id, f);
    }
    return [...out].map(([glb, f]) => ({ glb, ...f }));
  });
  const housings = $derived(scene ? housingsOf(scene) : []);
  const groups = $derived(scene ? byLeg(scene, housings) : []);
  const partCount = $derived(scene ? scene.parts.filter((p) => !isConnector(p)).length : 0);
  const selHousing = $derived(selection?.kind === 'housing' ? housings.find((h) => h.code === selection!.id) : undefined);
  const selLeg = $derived(scene && selection?.kind === 'leg' ? scene.legs.find((l) => l.id === selection!.id) : undefined);
  const selPart = $derived(scene && selection?.kind === 'part' ? partById(scene, selection.id) : undefined);
  const selLink = $derived(scene && selection?.kind === 'link' ? scene.links.find((l) => l.id === selection!.id) : undefined);

  let viewEl = $state<HTMLElement>();
  function choose(next: Selection) {
    selection = tap(selection, next);
  }
  // From the lists, bring the view back on screen (on a phone the lists are below it).
  function chooseFromList(next: Selection) {
    choose(next);
    viewEl?.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }
  function toggle(key: string) {
    const h = new Set(hidden);
    if (h.has(key)) h.delete(key);
    else h.add(key);
    hidden = h;
  }
  function where(p: Part): string {
    const { x, y, z, rx, ry, rz } = p.place;
    const turn = [rx && `x ${rx}°`, ry && `y ${ry}°`, rz && `z ${rz}°`].filter(Boolean).join(', ');
    return `x ${x} · y ${y} · z ${z} mm${turn ? `, turned ${turn}` : ''}${p.parent ? ` in ${name(p.parent)}` : ''}`;
  }
  const size = (p: Part) => (p.size_mm ? `${p.size_mm.x} × ${p.size_mm.y} × ${p.size_mm.z} mm` : '');
  const stateWord = (pid: string) => {
    const s = status[pid];
    if (!s) return '';
    return s.state === 'loading' ? 'loading' : s.state === 'failed' ? 'did not load' : '';
  };
  const linksOf = (pid: string) => scene?.links.filter((l) => l.from.part === pid || l.to.part === pid) ?? [];
  const missingOf = (pid: string) => scene?.missing.filter((m) => m.part === pid) ?? [];
  const ownHousings = (pid: string) => {
    const codes = new Set(scene ? [...family(scene, pid)].map((x) => partById(scene, x)).filter(isConnector).map((c) => c!.housing) : []);
    return housings.filter((h) => codes.has(h.code));
  };
</script>

{#snippet confirmChip(on: boolean)}
  {#if on}<span class="chip accent">to confirm</span>{/if}
{/snippet}

{#snippet partFacts(p: Part)}
  <dl class="facts">
    {#if p.origin}<dt>What it is</dt><dd>{p.origin}</dd>{/if}
    <dt>Placed</dt>
    <dd>{where(p)}</dd>
    <dt>Place from</dt>
    <dd>
      {p.place_from || 'not said'}
      {#if p.confirm}<span class="warn">{' - '}not confirmed; the dash is not measured yet</span>{/if}
    </dd>
    {#if size(p)}<dt>Size</dt><dd>{size(p)}</dd>{/if}
    <dt>Model</dt>
    <dd>
      {#if p.glb}<span class="mono">{p.glb}</span> {bytesLabel(p.bytes)}{:else}none{p.kind === 'node' ? ' (a place, not a part)' : ''}{/if}
      {#if status[p.id]?.state === 'failed'}<span class="warn">{' - '}did not load: {(status[p.id] as { why: string }).why}</span>{/if}
    </dd>
    {#if p.source}<dt>Design file</dt><dd class="mono small">{p.source}</dd>{/if}
  </dl>
{/snippet}

{#snippet cavityTable(h: Housing)}
  {#if h.cavities.length}
    <div class="cav-wrap">
      <table class="cav">
        <thead><tr><th>Cav</th><th>Circuit</th><th>AWG</th><th>Colour</th><th>State</th></tr></thead>
        <tbody>
          {#each h.cavities as c, i (i)}
            <tr class:idle={!!c.state && c.state !== 'LIVE'}>
              <td class="mono">{c.cav}</td>
              <td>{c.circuit || '-'}</td>
              <td class="num">{c.awg}</td>
              <td>{c.colour}</td>
              <td>{c.state.toLowerCase()}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {:else}
    <p class="faint small">No cavities in the scene for this housing.</p>
  {/if}
{/snippet}

{#snippet housingFacts(h: Housing)}
  <dl class="facts">
    <dt>Family</dt>
    <dd class="mono">{h.family || 'not said'}{h.ways != null ? ` · ${h.ways} ways` : ''}</dd>
    <dt>Where</dt>
    <dd>{h.where || 'not said'}</dd>
    {#if h.leg}<dt>Leg</dt><dd>{h.leg}</dd>{/if}
    <dt>Halves</dt>
    <dd>{h.plug ? 'plug' : 'no plug'} · {h.receptacle ? 'receptacle' : 'no receptacle'}{h.receptacle?.parent ? ` on ${name(h.receptacle.parent)}` : ''}</dd>
    {#if h.confirm}<dt>Place</dt><dd class="warn">provisional - not confirmed until the car is measured</dd>{/if}
  </dl>
{/snippet}

{#snippet linkRow(l: NonNullable<typeof scene>['links'][number])}
  <span class="row-main">
    <span class="mono code">{l.code}</span>
    {@render confirmChip(l.confirm)}
  </span>
  <span class="row-sub">{l.label}</span>
  <span class="row-sub faint">{name(l.from.part)}{l.from.connector ? ` (${l.from.connector})` : ''} → {name(l.to.part)}{l.to.connector ? ` (${l.to.connector})` : ''}</span>
  {#if l.ways != null || l.carries.length}
    <span class="row-sub faint">{l.ways != null ? `${l.ways} way${l.ways === 1 ? '' : 's'}` : ''}{l.ways != null && l.carries.length ? ' · ' : ''}{l.carries.join(', ')}</span>
  {/if}
{/snippet}

{#if load.state === 'loading'}
  <p class="muted" data-testid="design-state">Reading the design…</p>
{:else if load.state === 'none'}
  <div class="empty panel" data-testid="design-state">
    <p><strong>No design exported for this project yet.</strong></p>
    <p class="faint small">The page shows what the design's export script writes to <span class="mono">design/{area}/scene.json</span>.</p>
  </div>
{:else if load.state === 'error'}
  <div class="empty panel" data-testid="design-state">
    <p><strong>The design's scene file could not be read:</strong> {load.reason}.</p>
  </div>
{:else if scene}
  <p class="meta faint small">
    Exported {builtLabel(scene.built)} · {partCount} parts · {scene.links.length} links
    {#if housings.length}· {housings.length} housings{/if}
    {#if scene.legs.length}· {scene.legs.length} legs{/if}
    {#if scene.frame.ruling}· car frame {scene.frame.ruling}{/if}
  </p>

  {#if failed.length}
    <div class="alert" role="status">
      {#each failed as f (f.glb)}
        <p>
          Could not load <strong>{f.names[0]}</strong>{f.names.length > 1 ? ` and ${f.names.length - 1} more using it` : ''}
          (<span class="mono">{f.glb}</span>): {f.why}. A box of its size stands in; the rest is shown.
        </p>
      {/each}
    </div>
  {/if}

  {#if id && !part}
    <div class="empty panel">
      <p>There is no part named <span class="mono">{id}</span> in this design.</p>
      <a class="btn small" href={href({ name: 'design', area })}><ArrowLeft size={15} /> The assembly</a>
    </div>
  {:else if part}
    <!-- one part, or one board -->
    <div class="head-row">
      <a class="btn small ghost back" href={href({ name: 'design', area })}><ArrowLeft size={15} /> Assembly</a>
      <h2>{part.name}</h2>
      <span class="chip">{KIND_LABEL[part.kind]}</span>
      {@render confirmChip(part.confirm)}
    </div>
    <div class="layout">
      <div class="view">
        {#key modeKey}
          <DesignCanvas
            bind:this={canvas}
            {scene}
            {base}
            {mode}
            {hidden}
            {side}
            {toggles}
            onstatus={(pid, s) => (status = { ...status, [pid]: s })}
            onnodes={(f) => (found = f)}
          />
        {/key}
        <div class="controls" role="group" aria-label="View controls">
          {#if mode.kind === 'board'}
            <button class="btn" aria-pressed={side === 'top'} class:cool={side === 'top'} onclick={() => (side = 'top')}>Top</button>
            <button class="btn" aria-pressed={side === 'bottom'} class:cool={side === 'bottom'} onclick={() => (side = 'bottom')}>Bottom</button>
          {/if}
          {#if part.nodes.case.length}
            <button class="btn" aria-pressed={!hidden.has('case')} class:cool={!hidden.has('case')} disabled={found?.case === false} onclick={() => toggle('case')}>
              Case{found?.case === false ? ' (not in the model)' : ''}
            </button>
          {/if}
          {#if part.nodes.inside.length}
            <button class="btn" aria-pressed={!hidden.has('inside')} class:cool={!hidden.has('inside')} disabled={found?.inside === false} onclick={() => toggle('inside')}>
              Insides{found?.inside === false ? ' (not in the model)' : ''}
            </button>
          {/if}
          {#each listedChildren(scene, part.id) as c (c.id)}
            <button class="btn" aria-pressed={!hidden.has(c.id)} class:cool={!hidden.has(c.id)} onclick={() => toggle(c.id)}>{c.name}</button>
          {/each}
          {#if ownHousings(part.id).length && !isConnector(part)}
            <button class="btn" aria-pressed={!hidden.has('connectors')} class:cool={!hidden.has('connectors')} onclick={() => toggle('connectors')}>Connectors</button>
          {/if}
          <button class="btn icon" aria-pressed={toggles.labels} class:cool={toggles.labels} aria-label="Labels" title="Labels" onclick={() => flip('labels')}><Tags size={17} /></button>
          <button class="btn icon" aria-label="Fit to view" title="Fit to view" onclick={() => canvas?.fit()}><Maximize size={17} /></button>
        </div>
        <p class="faint small hint">Drag to turn it, pinch or scroll to zoom, two fingers to move it.</p>
      </div>

      <aside class="side">
        <details open>
          <summary>About</summary>
          {@render partFacts(part)}
        </details>
        <details open>
          <summary>Connectors <span class="n">{part.connectors.length}</span></summary>
          {#if part.connectors.length}
            <ul class="list">
              {#each part.connectors as c (c.code)}
                <li class="item static">
                  <span class="row-main"><span class="mono code">{c.code}</span>{#if c.face}<span class="chip quiet">{c.face}</span>{/if}</span>
                  {#if !c.at}<span class="row-sub warn">where it sits on the part is not in the scene</span>{/if}
                  {#if c.note}<span class="row-sub faint">{c.note}</span>{/if}
                </li>
              {/each}
            </ul>
          {:else}
            <p class="faint small pad">None in the scene.</p>
          {/if}
        </details>
        {#if ownHousings(part.id).length}
          <details open>
            <summary>Housings <span class="n">{ownHousings(part.id).length}</span></summary>
            <ul class="list">
              {#each ownHousings(part.id) as h (h.code)}
                <li>
                  <details class="housing">
                    <summary class="item"><span class="row-main"><span class="mono code">{h.code}</span><span class="faint small">{h.family}{h.ways != null ? ` · ${h.ways} ways` : ''}</span></span></summary>
                    <div class="pad">{@render cavityTable(h)}</div>
                  </details>
                </li>
              {/each}
            </ul>
          </details>
        {/if}
        {#if listedChildren(scene, part.id).length}
          <details open>
            <summary>Inside it <span class="n">{listedChildren(scene, part.id).length}</span></summary>
            <ul class="list">
              {#each listedChildren(scene, part.id) as c (c.id)}
                <li>
                  <a class="item" href={href({ name: 'design', area, id: c.id })}>
                    <span class="row-main">{c.name}<span class="chip">{KIND_LABEL[c.kind]}</span>{@render confirmChip(c.confirm)}<ChevronRight size={16} class="go" /></span>
                  </a>
                </li>
              {/each}
            </ul>
          </details>
        {/if}
        {#if linksOf(part.id).length}
          <details open>
            <summary>Links <span class="n">{linksOf(part.id).length}</span></summary>
            <ul class="list">
              {#each linksOf(part.id) as l (l.id)}<li class="item static">{@render linkRow(l)}</li>{/each}
            </ul>
          </details>
        {/if}
        {#if missingOf(part.id).length}
          <details open>
            <summary>Missing <span class="n">{missingOf(part.id).length}</span></summary>
            <ul class="list">
              {#each missingOf(part.id) as m, i (i)}
                <li class="item static"><span class="row-main">{m.what}</span>{#if m.why}<span class="row-sub faint">{m.why}</span>{/if}</li>
              {/each}
            </ul>
          </details>
        {/if}
      </aside>
    </div>
  {:else}
    <!-- the assembly -->
    <div class="layout">
      <div class="view" bind:this={viewEl}>
        {#key modeKey}
          <DesignCanvas
            bind:this={canvas}
            {scene}
            {base}
            {mode}
            {selection}
            {toggles}
            onpick={choose}
            onstatus={(pid, s) => (status = { ...status, [pid]: s })}
          />
        {/key}
        <div class="controls" role="group" aria-label="View controls">
          {#if selection}
            <button class="btn primary" onclick={() => (selection = null)}><ArrowLeft size={16} /> Show everything</button>
            <span class="muted small sel">{selPart?.name ?? selLink?.code ?? selHousing?.code ?? selLeg?.name ?? ''}</span>
          {:else}
            <span class="faint small sel">Tap a part, a link{scene.legs.length ? ', a leg' : ''}{housings.length ? ' or a connector' : ''} to isolate it.</span>
          {/if}
          <button class="btn icon" aria-pressed={toggles.labels} class:cool={toggles.labels} aria-label="Labels" title="Labels" onclick={() => flip('labels')}><Tags size={17} /></button>
          <button class="btn icon" aria-label="Fit to view" title="Fit to view" onclick={() => canvas?.fit()}><Maximize size={17} /></button>
          <button class="btn icon" aria-label="Fit everything, far ends included" title="Fit everything, far ends included" onclick={() => canvas?.fit(true)}><Expand size={17} /></button>
        </div>
        {#if scene.legs.length || housings.length}
          <div class="controls layers" role="group" aria-label="Layers">
            {#if scene.legs.length}
              <button class="btn" aria-pressed={toggles.legs} class:cool={toggles.legs} onclick={() => flip('legs')}>Legs</button>
            {/if}
            {#if scene.links.length}
              <button class="btn" aria-pressed={toggles.links} class:cool={toggles.links} onclick={() => flip('links')}>Links</button>
            {/if}
            {#if housings.length}
              <button class="btn" aria-pressed={toggles.connectors} class:cool={toggles.connectors} onclick={() => flip('connectors')}>Connectors</button>
            {/if}
          </div>
        {/if}
      </div>

      <aside class="side">
        {#if selPart}
          <section class="panel picked" aria-label="Isolated part">
            <div class="row-main"><strong>{selPart.name}</strong><span class="chip">{KIND_LABEL[selPart.kind]}</span>{@render confirmChip(selPart.confirm)}</div>
            {@render partFacts(selPart)}
            <a class="btn cool" href={href({ name: 'design', area, id: selPart.id })}>{selPart.kind === 'pcb' ? 'The board alone' : 'This part alone'} <ChevronRight size={16} /></a>
          </section>
        {:else if selLink}
          <section class="panel picked" aria-label="Isolated link">
            {@render linkRow(selLink)}
            <p class="faint small">A straight line from plug to plug - not the wire's run or length (the harness drawings are).</p>
          </section>
        {:else if selHousing}
          <section class="panel picked" aria-label="Isolated housing">
            <div class="row-main"><strong class="mono">{selHousing.code}</strong>{@render confirmChip(selHousing.confirm)}</div>
            {@render housingFacts(selHousing)}
            {@render cavityTable(selHousing)}
          </section>
        {:else if selLeg}
          <section class="panel picked" aria-label="Isolated leg">
            <div class="row-main"><span class="swatch" style="--leg: {legColourCss(scene, selLeg.id)}"></span><strong>{selLeg.name}</strong>{@render confirmChip(selLeg.confirm)}</div>
            <dl class="facts">
              {#if selLeg.conductors != null}<dt>Conductors</dt><dd>{selLeg.conductors}</dd>{/if}
              <dt>Drawn as</dt>
              <dd>a tube {legRadius(selLeg)} mm in radius{selLeg.radius_mm ? '' : ' (from its conductors)'}</dd>
              <dt>Housings</dt>
              <dd>{selLeg.housings.length ? selLeg.housings.join(', ') : 'none named'}</dd>
              {#if selLeg.routes.length}<dt>Routes</dt><dd class="mono">{selLeg.routes.join(', ')}</dd>{/if}
              <dt>Path from</dt>
              <dd>{selLeg.place_from || 'not said'}{#if selLeg.confirm}<span class="warn">{' - '}provisional; nothing here is measured</span>{/if}</dd>
            </dl>
          </section>
        {/if}

        <details open>
          <summary>Parts <span class="n">{partCount}</span></summary>
          <ul class="list">
            {#each listedTop(scene) as p (p.id)}
              <li>
                <div class="pair">
                  <button class="item" class:on={selection?.kind === 'part' && selection.id === p.id} aria-pressed={selection?.kind === 'part' && selection.id === p.id} onclick={() => chooseFromList({ kind: 'part', id: p.id })}>
                    <span class="row-main">{p.name}<span class="chip">{KIND_LABEL[p.kind]}</span>{@render confirmChip(p.confirm)}</span>
                    {#if stateWord(p.id) || (!p.glb && p.kind !== 'node')}
                      <span class="row-sub" class:warn={status[p.id]?.state === 'failed' || !p.glb}>{stateWord(p.id) || 'no model exported'}</span>
                    {/if}
                  </button>
                  <a class="btn ghost icon open" href={href({ name: 'design', area, id: p.id })} aria-label="{p.name} alone"><ChevronRight size={18} /></a>
                </div>
                {#if listedChildren(scene, p.id).length}
                  <ul class="list sub">
                    {#each listedChildren(scene, p.id) as c (c.id)}
                      <li>
                        <a class="item" href={href({ name: 'design', area, id: c.id })}>
                          <span class="row-main">{c.name}<span class="chip">{KIND_LABEL[c.kind]}</span>{@render confirmChip(c.confirm)}<ChevronRight size={16} class="go" /></span>
                        </a>
                      </li>
                    {/each}
                  </ul>
                {/if}
              </li>
            {/each}
          </ul>
        </details>

        <details open>
          <summary>Links <span class="n">{scene.links.length}</span></summary>
          {#if scene.links.length}
            <ul class="list">
              {#each scene.links as l (l.id)}
                <li>
                  <button class="item" class:on={selection?.kind === 'link' && selection.id === l.id} aria-pressed={selection?.kind === 'link' && selection.id === l.id} onclick={() => chooseFromList({ kind: 'link', id: l.id })}>
                    {@render linkRow(l)}
                  </button>
                </li>
              {/each}
            </ul>
          {:else}
            <p class="faint small pad">No links in the scene.</p>
          {/if}
        </details>

        {#if housings.length}
          <details open>
            <summary>Connectors <span class="n">{housings.length}</span></summary>
            {#each groups as g (g.leg)}
              <div class="leg-group">
                {#if g.legId}
                  <button class="item leg-head" class:on={selection?.kind === 'leg' && selection.id === g.legId} aria-pressed={selection?.kind === 'leg' && selection.id === g.legId} onclick={() => chooseFromList({ kind: 'leg', id: g.legId! })}>
                    <span class="row-main"><span class="swatch" style="--leg: {legColourCss(scene, g.legId)}"></span>{g.leg}<span class="faint small">{g.housings.length}</span></span>
                  </button>
                {:else}
                  <p class="leg-head static label">{g.leg} <span class="faint">{g.housings.length}</span></p>
                {/if}
                <ul class="list sub">
                  {#each g.housings as h (h.code)}
                    <li>
                      <button class="item" class:on={selection?.kind === 'housing' && selection.id === h.code} aria-pressed={selection?.kind === 'housing' && selection.id === h.code} onclick={() => chooseFromList({ kind: 'housing', id: h.code })}>
                        <span class="row-main"><span class="mono code">{h.code}</span>{@render confirmChip(h.confirm)}</span>
                        <span class="row-sub faint">{h.family}{h.ways != null ? ` · ${h.ways} ways` : ''}{h.where ? ` · ${h.where}` : ''}</span>
                      </button>
                    </li>
                  {/each}
                </ul>
              </div>
            {/each}
          </details>
        {/if}

        {#if scene.missing.length}
          <details open>
            <summary>Missing <span class="n">{scene.missing.length}</span></summary>
            <ul class="list">
              {#each scene.missing as m, i (i)}
                <li class="item static">
                  <span class="row-main">{m.part ? `${name(m.part)}: ` : ''}{m.what}</span>
                  {#if m.why}<span class="row-sub faint">{m.why}</span>{/if}
                </li>
              {/each}
            </ul>
          </details>
        {/if}

        {#if scene.notes.length}
          <details open>
            <summary>Notes <span class="n">{scene.notes.length}</span></summary>
            <ul class="list">
              {#each scene.notes as n, i (i)}<li class="item static"><span class="row-sub">{n}</span></li>{/each}
            </ul>
          </details>
        {/if}

        {#if load.problems.length}
          <details>
            <summary>Read with problems <span class="n">{load.problems.length}</span></summary>
            <ul class="list">
              {#each load.problems as pr, i (i)}<li class="item static"><span class="row-sub">{pr}</span></li>{/each}
            </ul>
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
    margin: -6px 0 12px;
  }
  .alert {
    margin-bottom: 12px;
    padding: 10px 14px;
    border-radius: var(--r-2);
    border: 1px solid var(--accent-line);
    background: var(--accent-soft);
    color: var(--accent-2);
    font-size: 13.5px;
    display: grid;
    gap: 4px;
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
    scroll-margin-top: calc(var(--topbar) + 12px);
    top: calc(var(--topbar) + 12px);
    display: grid;
    gap: 10px;
  }
  .view > :global(.stage) {
    height: clamp(360px, calc(100dvh - var(--topbar) - 230px), 760px);
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
  .hint {
    margin: 0;
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
  summary::after {
    content: '';
    margin-left: auto;
    width: 7px;
    height: 7px;
    border-right: 2px solid var(--text-3);
    border-bottom: 2px solid var(--text-3);
    transform: rotate(45deg);
    transition: transform var(--t-fast);
  }
  details[open] > summary::after {
    transform: rotate(-135deg);
  }
  .n {
    font-size: 12px;
    color: var(--text-3);
    font-weight: 560;
  }
  .list {
    list-style: none;
    padding: 0 6px 8px;
    margin: 0;
    display: grid;
    gap: 2px;
  }
  .list.sub {
    padding: 0 0 4px 18px;
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
  button.item:active,
  a.item:active {
    background: var(--surface-2);
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
  .code {
    color: var(--sky);
  }
  .warn {
    color: var(--accent-2);
  }
  .pad {
    padding: 0 14px 12px;
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
  .layers {
    margin-top: -2px;
  }
  .swatch {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--leg);
    flex: none;
  }
  .leg-group + .leg-group {
    margin-top: 4px;
  }
  .leg-head {
    padding-left: 12px;
  }
  p.leg-head {
    margin: 6px 14px 2px;
  }
  .cav-wrap {
    width: 100%;
    overflow-x: auto;
  }
  .cav {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }
  .cav th {
    text-align: left;
    font-weight: 600;
    color: var(--text-3);
    padding: 4px 8px 6px 0;
    border-bottom: 1px solid var(--line-soft);
  }
  .cav td {
    padding: 5px 8px 5px 0;
    border-bottom: 1px solid var(--line-soft);
    vertical-align: top;
  }
  .cav tr.idle td {
    color: var(--text-3);
  }
  details.housing {
    border: none;
    background: none;
  }
  details.housing > summary {
    padding: 8px 10px;
  }
  details.housing > summary::after {
    display: none;
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
      height: min(62dvh, 460px);
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

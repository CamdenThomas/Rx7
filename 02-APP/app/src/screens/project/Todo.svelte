<!--
  The project's work, in working order (D-406 8.2): what can start today, then every row
  after what it waits on. Tracks and parts follow the record (D-386, D-387 → D-405). His
  rows are answered right here, each the way its kind needs.

  A project whose rows carry briefs (02-electrical D-533) reads as the manual's contents: his
  rows numbered as one sequence from the first to the last, each with its goal, where, how
  long and how many of its steps are ticked on this device, and Start here on the first row
  he can do now. A project without briefs reads as it always has.
-->
<script lang="ts">
  import { CircleCheck, CirclePlay, CircleX, Clock, Hourglass, MapPin, Play } from '@lucide/svelte';
  import ApplyBar from '../../components/ApplyBar.svelte';
  import WorkAnswer from '../../components/WorkAnswer.svelte';
  import TodoFocus from './TodoFocus.svelte';
  import { app } from '../../lib/app.svelte';
  import { progress, startHere } from '../../lib/briefs';
  import type { Blocker, WorkRow } from '../../lib/model';
  import { href, router } from '../../lib/router.svelte';
  import { manuals, ticks } from '../../lib/steps.svelte';
  import { inlineMd, plain, plural } from '../../lib/text';
  import { mine as myRows, todoView, visible, type Who } from './todoView.svelte';

  let { area, id }: { area: string; id?: string } = $props();

  const all = $derived(app.work(area));
  const f = $derived(todoView.get(area));
  const tracks = $derived([...new Set(all.map((w) => w.track).filter(Boolean))].sort((a, b) => (a === 'design' ? -1 : b === 'design' ? 1 : a.localeCompare(b))));
  const rows = $derived(visible(area, f));
  const current = $derived(id ? all.find((w) => w.id === id) : undefined);
  const project = $derived(app.area(area)?.project ?? {});

  // The manual (D-533): indexed once per snapshot, looked up per row.
  const manual = $derived(manuals.of(area));
  const guided = $derived(manuals.has(area));
  const his = $derived(guided ? myRows(area) : []);
  /** Each of his open rows' place in the one sequence, whatever the filter shows. */
  const numbers = $derived(new Map(his.map((w, i) => [w.id, i + 1])));
  const first = $derived(guided ? startHere(his, (id) => !!app.answer(area, id)) : undefined);

  function start() {
    if (!first) return;
    // The one-at-a-time view steps through the list he is looking at: make sure the row is in it.
    if (!rows.some((r) => r.id === first.id)) todoView.set(area, { track: '', who: 'camden', readyOnly: false });
    router.go({ name: 'todo', area, id: first.id });
  }

  const PART: Record<number, string> = {
    1: 'Part 1 · The car whole — desk, bench and the car as it stands',
    2: 'Part 2 · The interior out — and everything that needs it out',
    3: 'Part 3 · The car apart',
    4: 'Part 4 · The interior back in — and the first drives',
  };
  const partNote = (p: number) => {
    const row = p === 2 ? project.car_apart : p === 4 ? project.car_back : '';
    const w = row ? all.find((x) => x.id === row) : undefined;
    return w ? `Starts at ${w.id}: ${w.item}` : '';
  };

  interface Group {
    key: string;
    part: number;
    stage: string;
    title: string;
    rows: WorkRow[];
    closed: WorkRow[];
  }

  const groups = $derived.by(() => {
    const out: Group[] = [];
    const closedAll = all.filter((w) => (!f.track || w.track === f.track) && (f.who === 'all' || w.owner === f.who) && (w.status === 'done' || w.status === 'dropped'));
    // The design track reads as one checklist per part; everything else stage by stage.
    const byStage = (w: WorkRow) => w.track !== 'design';
    const keyOf = (w: WorkRow) => `${w.part}/${byStage(w) ? w.stage : ''}`;
    const at = new Map<string, Group>();
    for (const w of rows) {
      const key = keyOf(w);
      let g = at.get(key);
      if (!g) {
        g = { key, part: w.part, stage: byStage(w) ? w.stage : '', title: byStage(w) ? w.stage_title : '', rows: [], closed: [] };
        at.set(key, g);
        out.push(g);
      }
      g.rows.push(w);
    }
    for (const w of closedAll) at.get(keyOf(w))?.closed.push(w);
    return out;
  });

  const readyMine = $derived(all.filter((w) => w.owner === 'camden' && w.status === 'ready' && (!f.track || w.track === f.track)).length);

  function waits(b: Blocker): string {
    switch (b.kind) {
      case 'work':
        return `${b.ref}${b.owner === 'camden' ? ' (yours)' : ''}`;
      case 'block':
        return `block ${b.ref}${b.answered ? ' (answered)' : ''}`;
      case 'phase':
        return b.freeze ? 'the design freeze' : b.label;
      case 'area-work':
        return b.ref;
      default:
        return b.label;
    }
  }

  function target(b: Blocker) {
    if (b.kind === 'work') return href({ name: 'todo', area, id: b.ref });
    if (b.kind === 'block') return href({ name: 'blocks', area: app.blocks().find((x) => x.id === b.ref)?.area ?? area, id: b.ref });
    if (b.kind === 'area-work') return href({ name: 'todo', area: b.area ?? area, id: b.ref.split(':')[1] });
    if (b.kind === 'decision') return href({ name: 'decision', id: b.ref });
    return '';
  }

  const WHO: { id: Who; label: string }[] = [
    { id: 'all', label: 'Everything' },
    { id: 'camden', label: 'Yours' },
    { id: 'agent', label: "Claude's" },
  ];
</script>

{#if id}
  {#if current}
    {#key current.id}
      <TodoFocus row={current} ids={rows.some((r) => r.id === current.id) ? rows.map((r) => r.id) : [current.id]} />
    {/key}
  {:else}
    <p class="muted">There is no work row {id} in this project.</p>
  {/if}
{:else}
  <ApplyBar {area} kinds={['work']} noun="TODO" />

  {#if guided}
    <div class="start">
      {#if first}
        <button class="btn primary big" onclick={start}><Play size={16} /> Start here</button>
        <p class="startrow"><span class="no num">{numbers.get(first.id)}</span><span class="id">{first.id}</span><span class="what">{plain(first.item)}</span></p>
      {:else}
        <p class="faint">Nothing of yours can start right now: every open row of yours is answered or waits on something.</p>
      {/if}
    </div>
  {/if}

  <div class="controls">
    {#if tracks.length > 1}
      <div class="seg" role="tablist" aria-label="Track">
        {#if guided}<button role="tab" aria-selected={f.track === ''} class:on={f.track === ''} onclick={() => todoView.set(area, { track: '' })}>Whole list</button>{/if}
        {#each tracks as t (t)}
          <button role="tab" aria-selected={f.track === t} class:on={f.track === t} onclick={() => todoView.set(area, { track: t })}>{t === 'design' ? 'Design' : t === 'build' ? 'Build' : t}</button>
        {/each}
      </div>
    {/if}
    {#if guided}
      <label class="toggle"><input type="checkbox" checked={f.who === 'camden'} onchange={(e) => todoView.set(area, { who: (e.target as HTMLInputElement).checked ? 'camden' : 'all' })} /> Mine only</label>
    {:else}
      <div class="seg" role="tablist" aria-label="Whose">
        {#each WHO as w (w.id)}
          <button role="tab" aria-selected={f.who === w.id} class:on={f.who === w.id} onclick={() => todoView.set(area, { who: w.id })}>{w.label}</button>
        {/each}
      </div>
    {/if}
    <label class="toggle"><input type="checkbox" checked={f.readyOnly} onchange={(e) => todoView.set(area, { readyOnly: (e.target as HTMLInputElement).checked })} /> Only what can start now</label>
    <span class="count faint">{plural(rows.length, 'row')} open{readyMine ? ` · ${readyMine} yours to start` : ''}</span>
  </div>

  {#if f.track === 'build'}
    <p class="note faint">Nothing here starts until the design is verified and frozen — every row waits on the design freeze as well as what it names.</p>
  {/if}

  {#if !rows.length}
    <div class="empty"><h3>Nothing open here.</h3><p class="muted">Every row this filter shows is done.</p></div>
  {/if}

  {#each groups as g, gi (g.key)}
    {#if g.part && (gi === 0 || groups[gi - 1].part !== g.part)}
      <h2 class="part">{PART[g.part]}</h2>
      {#if partNote(g.part)}<p class="partnote faint">{partNote(g.part)}</p>{/if}
    {/if}
    {#if g.stage}
      <h3 class="stage"><span class="mono">Stage {g.stage}</span> · {g.title}</h3>
    {/if}
    <ul class="rows">
      {#each g.rows as w (w.id)}
        {@const m = manual?.rows.get(w.id)}
        {@const pr = m?.steps.length ? progress(m.steps, ticks.of(area, w.id)) : null}
        <li class="wrow {w.status}" class:mine={w.owner === 'camden'} class:numbered={guided}>
          <button class="hit" onclick={() => router.go({ name: 'todo', area, id: w.id })} aria-label="Open {w.id}"></button>
          <span class="st" title={w.status === 'ready' ? 'Can start now' : 'Waiting'}>
            {#if w.status === 'ready'}<CirclePlay size={17} />{:else}<Hourglass size={16} />{/if}
          </span>
          {#if guided}<span class="no num">{numbers.get(w.id) ?? ''}</span>{/if}
          <span class="id">{w.id}</span>
          <div class="body">
            <!-- eslint-disable-next-line svelte/no-at-html-tags — inlineMd() escapes every character first -->
            <p class="item">{@html inlineMd(w.item)}</p>
            {#if m?.brief?.goal}<p class="goal">{plain(m.brief.goal)}</p>{/if}
            {#if m?.brief?.where || m?.brief?.time || pr}
              <p class="meta">
                {#if m?.brief?.where}<span class="chip quiet where"><MapPin size={11} /><span>{m.brief.where}</span></span>{/if}
                {#if m?.brief?.time}<span class="chip quiet"><Clock size={11} />{m.brief.time}</span>{/if}
                {#if pr}<span class="chip num {pr.done === pr.total ? 'cool' : 'quiet'}">{pr.done} / {pr.total} steps</span>{/if}
              </p>
            {/if}
            {#if w.blockers.length}
              <p class="waits">
                waits on
                {#each w.blockers.slice(0, 4) as b, i (b.ref + i)}
                  {#if i}, {/if}{#if target(b)}<a href={target(b)} class="wref">{waits(b)}</a>{:else}<span>{waits(b)}</span>{/if}
                {/each}
                {#if w.blockers.length > 4} and {w.blockers.length - 4} more{/if}
              </p>
            {/if}
          </div>
          <span class="who chip {w.owner === 'camden' ? 'accent' : 'quiet'}">{w.owner === 'camden' ? 'you' : 'Claude'}</span>
          <WorkAnswer row={w} />
        </li>
      {/each}
    </ul>
    {#if g.closed.length && (gi === groups.length - 1 || groups[gi + 1].key !== g.key)}
      <p class="closed faint">
        Closed:
        {#each g.closed as c, i (c.id)}{#if i}{' '}{/if}<a href={href({ name: 'todo', area, id: c.id })} class="cl {c.status}">{#if c.status === 'done'}<CircleCheck size={12} />{:else}<CircleX size={12} />{/if}{c.id}</a>{/each}
      </p>
    {/if}
  {/each}
{/if}

<style>
  .controls {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px 14px;
    margin-bottom: 18px;
  }
  .seg {
    display: inline-flex;
    padding: 3px;
    border-radius: var(--r-2);
    background: var(--bg-raise);
    border: 1px solid var(--line-soft);
  }
  .seg button {
    border: 0;
    background: transparent;
    color: var(--text-3);
    padding: 6px 12px;
    border-radius: 7px;
    font-size: 13.5px;
    font-weight: 560;
  }
  .seg button.on {
    background: var(--surface-3);
    color: var(--foam);
    box-shadow: var(--shadow-1);
  }
  .toggle {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 13.5px;
    color: var(--text-2);
  }
  .count {
    margin-left: auto;
    font-size: 13px;
  }
  .note {
    font-size: 13px;
    margin: -6px 0 16px;
  }
  .part {
    font-size: 16px;
    margin: 26px 0 4px;
    color: var(--foam);
  }
  .partnote {
    font-size: 13px;
    margin-bottom: 10px;
  }
  .stage {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-2);
    margin: 18px 0 6px;
    display: flex;
    gap: 8px;
    align-items: baseline;
  }
  .stage .mono {
    color: var(--sky);
  }
  .rows {
    list-style: none;
    margin: 0;
    padding: 0;
    border: 1px solid var(--line-soft);
    border-radius: var(--r-3);
    background: var(--surface);
    overflow: hidden;
  }
  .wrow {
    position: relative;
    display: grid;
    grid-template-columns: 22px 64px 1fr auto auto;
    align-items: start;
    gap: 10px;
    padding: 9px 14px;
    border-bottom: 1px solid var(--line-soft);
    font-size: 13.5px;
  }
  .wrow:last-child {
    border-bottom: 0;
  }
  .wrow:hover {
    background: color-mix(in oklab, var(--surface-2) 60%, transparent);
  }
  .hit {
    position: absolute;
    inset: 0;
    border: 0;
    background: transparent;
    z-index: 0;
  }
  .wrow > :not(.hit) {
    position: relative;
    z-index: 1;
    pointer-events: none;
  }
  li.wrow > :global(.wa) {
    position: relative;
    z-index: 1;
  }
  li.wrow a {
    pointer-events: auto;
  }
  .st {
    padding-top: 1px;
    color: var(--text-4);
  }
  .ready .st {
    color: var(--sky);
  }
  .ready.mine .st {
    color: var(--ember);
  }
  .wrow .id {
    padding-top: 1px;
  }
  /* ------------------------------------------------ the list as the manual's contents */
  .start {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px 16px;
    margin-bottom: 18px;
  }
  .startrow {
    display: flex;
    align-items: baseline;
    gap: 8px;
    min-width: 0;
    flex: 1 1 240px;
    font-size: 14px;
    color: var(--text-2);
  }
  .startrow .what {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .no {
    font-family: var(--mono);
    font-size: 12.5px;
    font-weight: 600;
    color: var(--text-3);
    text-align: right;
  }
  .wrow.numbered {
    grid-template-columns: 22px 26px 64px 1fr auto auto;
  }
  .wrow .no {
    padding-top: 1px;
  }
  .wrow.mine.ready .no {
    color: var(--text);
  }
  .body {
    min-width: 0;
  }
  .goal {
    margin-top: 2px;
    font-size: 13px;
    line-height: 1.45;
    color: var(--text-2);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .meta {
    display: flex;
    flex-wrap: wrap;
    gap: 5px 6px;
    margin-top: 6px;
  }
  .meta .chip {
    max-width: 100%;
  }
  .meta .where span {
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .item {
    color: var(--text);
    line-height: 1.45;
  }
  .waiting .item {
    color: var(--text-2);
  }
  .waits {
    margin-top: 3px;
    font-size: 12.5px;
    color: var(--text-3);
  }
  .wref {
    color: var(--text-2);
    border-bottom: 1px dotted var(--line);
  }
  .wref:hover {
    color: var(--foam);
  }
  .who {
    margin-top: 1px;
  }
  .closed {
    font-size: 12.5px;
    margin: 8px 2px 0;
    display: flex;
    flex-wrap: wrap;
    gap: 4px 10px;
    align-items: center;
  }
  .cl {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-family: var(--mono);
    font-size: 12px;
    color: var(--text-3);
  }
  .cl.done :global(svg) {
    color: var(--sky);
  }
  .empty {
    padding: 40px 8px;
    text-align: center;
  }
  @media (max-width: 759px) {
    .wrow {
      grid-template-columns: 20px 1fr auto;
      grid-template-areas: 'st id who' 'st body body' 'st ans ans';
      gap: 4px 10px;
      padding: 12px 12px;
    }
    .wrow.numbered {
      grid-template-columns: 20px auto 1fr auto;
      grid-template-areas: 'st no id who' 'st body body body' 'st ans ans ans';
    }
    .wrow .no {
      grid-area: no;
      min-width: 1.4em;
    }
    /* a line is not enough on a phone: the goal takes two */
    .goal {
      white-space: normal;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      line-clamp: 2;
    }
    .toggle {
      min-height: var(--tap);
    }
    .start .btn {
      flex: 1 1 100%;
    }
    .st {
      grid-area: st;
    }
    .wrow .id {
      grid-area: id;
    }
    .body {
      grid-area: body;
    }
    .who {
      grid-area: who;
    }
    .wrow :global(.wa) {
      grid-area: ans;
      margin-top: 6px;
    }
    .count {
      margin-left: 0;
      flex-basis: 100%;
    }
  }
</style>

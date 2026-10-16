<!--
  One work row: what it is, what it waits on, its note, and — if it is his — his answer.

  A row that carries a brief (02-electrical D-533) opens as a page of the manual instead: the
  goal, where and how long, what must be true first, the tools, the parts by name, what to
  know with where each fact comes from, the numbered steps, how he knows it is done, and
  what to record — with his answer below it all, through the same control as ever. A step's
  tick is kept on this device (steps.svelte.ts) and is never his answer.
-->
<script lang="ts">
  import { ArrowDown, CircleCheck, CirclePlay, CircleX, Clock, Hourglass, ListChecks, ListOrdered, MapPin, RotateCcw, TriangleAlert } from '@lucide/svelte';
  import FocusNav from '../../components/FocusNav.svelte';
  import Prose from '../../components/Prose.svelte';
  import WorkAnswer from '../../components/WorkAnswer.svelte';
  import { app } from '../../lib/app.svelte';
  import { nextUnticked, progress, rich } from '../../lib/briefs';
  import { drafts } from '../../lib/drafts.svelte';
  import type { WorkRow } from '../../lib/model';
  import { href, router } from '../../lib/router.svelte';
  import { manuals, ticks } from '../../lib/steps.svelte';
  import { inlineMd } from '../../lib/text';
  import { ui } from '../../lib/ui.svelte';
  import { mine as myRows } from './todoView.svelte';

  let { row, ids }: { row: WorkRow; ids: string[] } = $props();

  const area = $derived(row.area);
  const draft = $derived(drafts.get(area, row.id));
  const answer = $derived(app.answer(area, row.id));
  const mine = $derived(row.owner === 'camden' && (row.status === 'ready' || row.status === 'waiting'));
  const STATUS = { ready: 'Can start now', waiting: 'Waiting', done: 'Done', dropped: 'Dropped' } as const;

  // The manual's page for this row, when the project has one (briefs.ts reads the tables).
  const manual = $derived(manuals.of(area));
  const guide = $derived(manual?.rows.get(row.id));
  const brief = $derived(guide?.brief ?? null);
  const steps = $derived(guide?.steps ?? []);
  const guided = $derived(!!brief || steps.length > 0);
  const ticked = $derived(ticks.of(area, row.id));
  const prog = $derived(progress(steps, ticked));
  const next = $derived(nextUnticked(steps, ticked));
  /** Where the row sits among his open rows, first to last. */
  const place = $derived.by(() => {
    const list = myRows(area);
    const i = list.findIndex((w) => w.id === row.id);
    return i < 0 ? null : { n: i + 1, of: list.length };
  });
  const html = (t: string) => rich(t, manual?.partHref);
  /** A step's number as written; one whose n is not a number takes its place in the list. */
  const stepNo = (n: number, i: number) => (n < 100_000 ? String(n) : String(i + 1));

  // The steps' own bar sticks under the app's top bar, whose height depends on the page
  // (crumbs, a banner): measured, never assumed.
  let top = $state(0);
  $effect(() => {
    const bar = document.querySelector<HTMLElement>('header.topbar');
    if (!bar || typeof ResizeObserver === 'undefined') return;
    const ro = new ResizeObserver(() => (top = Math.round(bar.getBoundingClientRect().height)));
    ro.observe(bar);
    return () => ro.disconnect();
  });

  function toNext() {
    if (!next) return;
    const calm = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
    document.getElementById(`step-${next.id}`)?.scrollIntoView({ block: 'start', behavior: calm ? 'auto' : 'smooth' });
  }

  /** A web address in the brief opens outside the app, as it does in every other prose. */
  function external(e: MouseEvent) {
    const a = (e.target as HTMLElement).closest('a[data-external]') as HTMLAnchorElement | null;
    if (a) {
      e.preventDefault();
      app.platform?.open(a.href);
    }
  }

  /** The parts the row names (PT ids in its item or note), from 00-CAR, so the question is
   *  answerable from this screen (plan P30). */
  const partCards = $derived.by(() => {
    const t = app.snapshot?.tables.find((x) => x.area === '00-CAR' && x.table === 'parts');
    if (!t) return [];
    const ids = [...new Set(`${row.item} ${row.note}`.match(/\bPT\d{3,4}\b/g) ?? [])];
    const col = (r: string[], c: string) => r[t.columns.indexOf(c)] ?? '';
    return ids.flatMap((pid) => {
      const r = t.rows.find((x) => col(x, 'id') === pid);
      if (!r) return [];
      return [{
        id: pid, name: col(r, 'name'), maker: col(r, 'maker'), part_no: col(r, 'part_no') || col(r, 'oem_no'),
        zone: col(r, 'zone'), system: col(r, 'system'), catalogue: col(r, 'catalogue'), applies: col(r, 'applies'),
        note: col(r, 'note').replace(/\s+/g, ' ').slice(0, 260),
      }];
    });
  });

  function unanswered(id: string) {
    const w = app.work(area).find((x) => x.id === id);
    return !!w && w.owner === 'camden' && w.status === 'ready' && !app.answer(area, id);
  }

  /** After a save, straight to the next row he has not answered (plan P31). */
  function advance() {
    const i = ids.indexOf(row.id);
    for (let k = 1; k <= ids.length; k++) {
      const id = ids[(i + k) % ids.length];
      if (id !== row.id && unanswered(id)) {
        router.go({ name: 'todo', area, id });
        return;
      }
    }
  }

  $effect(() => {
    ui.context = `work row ${row.id}: ${row.item}`;
    return () => (ui.context = '');
  });

  function link(ref: string, kind: string, refArea?: string) {
    if (kind === 'work') return href({ name: 'todo', area, id: ref });
    if (kind === 'block') return href({ name: 'blocks', area: app.blocks().find((b) => b.id === ref)?.area ?? area, id: ref });
    if (kind === 'area-work') return href({ name: 'todo', area: refArea ?? area, id: ref.split(':')[1] });
    if (kind === 'decision') return href({ name: 'decision', id: ref });
    return '';
  }
</script>

<FocusNav {ids} at={row.id} open={(id) => ({ name: 'todo', area, id })} list={{ name: 'todo', area }} {unanswered} />

{#snippet answerCard()}
  {#if mine}
    <section class="answer card">
      <h3 class="label">{row.reply === 'value' ? `Your measurement${row.unit ? ` (${row.unit})` : ''}` : row.reply === 'choice' ? 'Your choice' : 'When it is done'}</h3>
      {#if !answer}
        <textarea class="textarea" rows="2" value={draft.text} oninput={(e) => drafts.set(area, row.id, { text: (e.target as HTMLTextAreaElement).value })}
          placeholder="Anything to add — what you found, what you used (optional)."></textarea>
      {:else if answer.text}
        <p class="his">{answer.text}</p>
      {/if}
      <WorkAnswer {row} big words={draft.text} onSaved={advance} />
      {#if row.status === 'waiting' && !answer}<p class="faint small">This row still waits on what is listed below — you can still say it is done if it is.</p>{/if}
    </section>
  {/if}
{/snippet}

{#snippet waitsOn()}
  {#if row.blockers.length}
    <section>
      <h3 class="label">Waits on</h3>
      <ul class="blockers">
        {#each row.blockers as b, i (b.ref + i)}
          {@const to = link(b.ref, b.kind, b.area)}
          <li>
            {#if to}<a href={to} class="id">{b.ref}</a>{:else}<span class="id">{b.ref || '—'}</span>{/if}
            <span>{b.kind === 'phase' && b.freeze ? 'The design freeze — the review and your ruling' : b.label}</span>
            {#if b.kind === 'block'}<span class="chip {b.answered ? 'cool' : 'accent'}">{b.answered ? 'answered' : 'waiting for you'}</span>{/if}
            {#if b.owner === 'camden'}<span class="chip accent">yours</span>{/if}
          </li>
        {/each}
      </ul>
    </section>
  {/if}
{/snippet}

<article class="focus" class:guided style:--top={top ? `${top}px` : null}>
  <header>
    <span class="status {row.status}">
      {#if row.status === 'ready'}<CirclePlay size={16} />{:else if row.status === 'waiting'}<Hourglass size={15} />{:else if row.status === 'done'}<CircleCheck size={16} />{:else}<CircleX size={16} />{/if}
      {STATUS[row.status]}
    </span>
    <span class="id big">{row.id}</span>
    <span class="chip {row.owner === 'camden' ? 'accent' : 'quiet'}">{row.owner === 'camden' ? 'yours' : "Claude's"}</span>
    {#if row.track}<span class="chip quiet">{row.track}{row.part ? ` · part ${row.part}` : ''}</span>{/if}
  </header>
  <!-- eslint-disable-next-line svelte/no-at-html-tags — inlineMd() escapes every character first -->
  <h2>{@html inlineMd(row.item)}</h2>
  <!-- eslint-disable-next-line svelte/no-at-html-tags — rich() escapes every character first -->
  {#if brief?.goal}<p class="goal">{@html html(brief.goal)}</p>{/if}
  {#if row.stage_title}<p class="stage faint">Stage {row.stage} · {row.stage_title}</p>{/if}

  {#if guided}
    <div class="strip" aria-label="At a glance">
      {#if brief?.where}<span class="fact"><MapPin size={15} /> <span class="visually-hidden">Where:</span>{brief.where}</span>{/if}
      {#if brief?.time}<span class="fact"><Clock size={15} /> <span class="visually-hidden">Time:</span>{brief.time}</span>{/if}
      {#if place}<span class="fact place"><ListOrdered size={15} /> <span>No. <strong class="num">{place.n}</strong> of {place.of} in the list</span></span>{/if}
      {#if steps.length}<span class="fact"><ListChecks size={15} /> <span class="num">{steps.length} {steps.length === 1 ? 'step' : 'steps'}</span></span>{/if}
    </div>
  {/if}

  {#if partCards.length}
    <section class="parts">
      {#each partCards as p (p.id)}
        <div class="pcard card">
          <div class="ptop">
            <a class="id" href={href({ name: 'row', area: '00-CAR', table: 'parts', key: p.id })}>{p.id}</a>
            <strong>{p.name}</strong>
            {#if p.applies}<span class="chip quiet">{p.applies}</span>{/if}
          </div>
          <p class="sub faint">{[p.maker, p.part_no].filter(Boolean).join(' · ')}{p.zone ? ` · ${p.zone}` : ''}{p.system ? ` · ${p.system}` : ''}{p.catalogue ? ` · catalogue ${p.catalogue}` : ''}</p>
          {#if p.note}<p class="pnote">{p.note}</p>{/if}
        </div>
      {/each}
    </section>
  {/if}

  {#if guided}
    {@render waitsOn()}

    <!-- eslint-disable svelte/no-at-html-tags — rich() escapes every character of the record's text first -->
    <div class="guide" onclick={external} role="presentation">
      {#if brief?.before.length}
        <section data-part="before">
          <h3 class="label">Before you start</h3>
          <ul class="checks">
            {#each brief.before as b, i (i)}
              {@const key = `before:${i + 1}`}
              <li class:on={ticked.includes(key)}>
                <label>
                  <input type="checkbox" checked={ticked.includes(key)} onchange={(e) => ticks.set(area, row.id, key, e.currentTarget.checked)} />
                  <span>{@html html(b)}</span>
                </label>
              </li>
            {/each}
          </ul>
        </section>
      {/if}

      {#if brief?.tools.length}
        <section data-part="tools">
          <h3 class="label">Tools</h3>
          <ul class="tools">
            {#each brief.tools as t, i (i)}<li>{@html html(t)}</li>{/each}
          </ul>
        </section>
      {/if}

      {#if brief?.parts.length}
        <section data-part="parts">
          <h3 class="label">Parts</h3>
          <ul class="plist">
            {#each brief.parts as p (p.id)}
              <li>
                {#if p.found}
                  <a class="prow" href={p.href}>
                    <span class="id">{p.id}</span>
                    <span class="pmain"><span class="pname">{p.name || p.id}</span>{#if p.spec}<span class="pspec faint">{p.spec}</span>{/if}</span>
                    {#if p.qty}<span class="pqty num">{p.qty}{p.unit ? ` ${p.unit}` : ''}</span>{/if}
                    {#if p.supplier || p.partNo}<span class="psup faint">{[p.supplier, p.partNo].filter(Boolean).join(' · ')}</span>{/if}
                  </a>
                {:else}
                  <span class="prow bare"><span class="id">{p.id}</span></span>
                {/if}
              </li>
            {/each}
          </ul>
        </section>
      {/if}

      {#if brief?.know.length}
        <section data-part="know">
          <h3 class="label">What to know</h3>
          <ul class="facts">
            {#each brief.know as f, i (i)}
              <li>
                <span class="ftext">{@html html(f.text)}</span>
                {#if f.confirm || f.sources.length}
                  <span class="srcs">
                    {#if f.confirm}<span class="src confirm">confirm</span>{/if}
                    {#each f.sources as s, j (j)}
                      {#if s.href}<a class="src" href={s.href}>{s.text}</a>{:else}<span class="src">{s.text}</span>{/if}
                    {/each}
                  </span>
                {/if}
              </li>
            {/each}
          </ul>
        </section>
      {/if}

      {#if steps.length}
        <section data-part="steps" class="stepsec">
          <div class="sbar">
            <h3 class="label">The steps</h3>
            <span class="count num" class:all={prog.done === prog.total}><strong>{prog.done}</strong> of {prog.total} steps</span>
            <span class="meter" aria-hidden="true"><i style:width="{prog.total ? (100 * prog.done) / prog.total : 0}%"></i></span>
            {#if prog.done || ticked.length}
              <button class="btn small ghost untick" onclick={() => ticks.clear(area, row.id)} title="Untick every step of this row" aria-label="Untick all"><RotateCcw size={14} /> <span class="t">Untick all</span></button>
            {/if}
            <button class="btn small cool nextstep" disabled={!next} onclick={toNext}><ArrowDown size={15} /> Next unticked step</button>
          </div>
          <ol class="steps">
            {#each steps as s, i (s.id)}
              {@const on = ticked.includes(s.id)}
              <li class="step card" class:on id="step-{s.id}" data-step={s.id}>
                <label class="shead">
                  <input type="checkbox" checked={on} onchange={(e) => ticks.set(area, row.id, s.id, e.currentTarget.checked)} aria-label="Step {stepNo(s.n, i)} done" />
                  <span class="sn num">{stepNo(s.n, i)}</span>
                  <span class="sdo">{@html html(s.do)}</span>
                </label>
                {#if s.how.length || s.expect || s.caution}
                  <div class="sbody">
                    {#each s.how as h, k (k)}
                      {#if h.kind === 'text'}
                        <p class="how">{@html html(h.text)}</p>
                      {:else}
                        <ul class="clist">
                          {#each h.items as it, x (x)}
                            <li>{#if it.n}<span class="cn">{it.n}</span>{/if}<span class="ct" class:wide={!it.n}>{@html html(it.text)}</span></li>
                          {/each}
                        </ul>
                      {/if}
                    {/each}
                    {#if s.expect}
                      <div class="expect">
                        <span class="label">You should see</span>
                        <p>{@html html(s.expect)}</p>
                      </div>
                    {/if}
                    {#if s.caution}
                      <div class="caution" role="note">
                        <TriangleAlert size={17} />
                        <p><span class="visually-hidden">Caution:</span> {@html html(s.caution)}</p>
                      </div>
                    {/if}
                  </div>
                {/if}
              </li>
            {/each}
          </ol>
        </section>
      {/if}

      {#if row.note}
        <details class="rnote">
          <summary>The row's note</summary>
          <Prose text={row.note} compact />
        </details>
      {/if}

      {#if brief?.done_when}
        <section data-part="done">
          <h3 class="label">Done when</h3>
          <p class="para">{@html html(brief.done_when)}</p>
        </section>
      {/if}
      {#if brief?.if_not}
        <section data-part="ifnot">
          <h3 class="label">If it is not</h3>
          <p class="para">{@html html(brief.if_not)}</p>
        </section>
      {/if}
      {#if brief?.record}
        <section data-part="record">
          <h3 class="label">What to record</h3>
          <p class="para">{@html html(brief.record)}</p>
        </section>
      {/if}
    </div>
    <!-- eslint-enable svelte/no-at-html-tags -->

    {#if mine && steps.length}<p class="faint small ticknote">Step ticks stay on this device. The row is done when you answer it below.</p>{/if}
    {@render answerCard()}
  {:else}
    {@render answerCard()}
    {@render waitsOn()}

    {#if row.note}
      <section>
        <h3 class="label">Note</h3>
        <Prose text={row.note} compact />
      </section>
    {/if}
  {/if}
</article>

<style>
  .focus {
    max-width: 860px;
    display: flex;
    flex-direction: column;
    gap: 18px;
    padding-bottom: calc(80px + var(--tabbar));
  }
  header {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  .status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-3);
  }
  .status.ready {
    color: var(--sky);
  }
  .id.big {
    font-size: 15px;
  }
  h2 {
    font-size: 22px;
    line-height: 1.3;
  }
  .stage {
    margin-top: -10px;
    font-size: 13px;
  }
  .parts {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .pcard {
    padding: 10px 14px;
    display: flex;
    flex-direction: column;
    gap: 3px;
    font-size: 13.5px;
  }
  .ptop {
    display: flex;
    align-items: baseline;
    gap: 10px;
    flex-wrap: wrap;
  }
  .sub {
    font-size: 12.5px;
  }
  .pnote {
    color: var(--text-2);
    font-size: 13px;
    line-height: 1.45;
  }
  .label {
    display: block;
    margin-bottom: 8px;
  }
  .answer {
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  .answer .textarea {
    min-height: 64px;
  }
  .his {
    white-space: pre-wrap;
    padding-left: 12px;
    border-left: 2px solid var(--steel);
  }
  .small {
    font-size: 12.5px;
  }
  .blockers {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
    font-size: 14px;
  }
  .blockers li {
    display: flex;
    gap: 10px;
    align-items: baseline;
    flex-wrap: wrap;
  }

  /* ------------------------------------------------ the row as a page of the manual */
  .goal {
    margin-top: -8px;
    font-size: 16px;
    line-height: 1.5;
    color: var(--text-2);
  }
  .guided .stage {
    margin-top: -12px;
  }
  .strip {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 18px;
    padding: 10px 14px;
    border: 1px solid var(--line-soft);
    border-radius: var(--r-2);
    background: var(--bg-raise);
    font-size: 13.5px;
    color: var(--text-2);
  }
  .fact {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    min-width: 0;
  }
  .fact :global(svg) {
    flex: none;
    color: var(--sky);
  }
  .fact strong {
    color: var(--text);
    font-weight: 600;
  }
  .guide {
    display: flex;
    flex-direction: column;
    gap: 22px;
    min-width: 0;
  }
  .guide :global(a.cite) {
    font-family: var(--mono);
    font-size: 0.9em;
    color: var(--sky);
    border-bottom: 1px dotted color-mix(in oklab, var(--sky) 50%, transparent);
  }
  .guide :global(code) {
    font-family: var(--mono);
    font-size: 0.88em;
    color: var(--sky);
  }
  .guide :global(a[data-external]) {
    color: var(--sky);
    text-decoration: underline;
    text-underline-offset: 3px;
  }
  .para {
    font-size: 15px;
    line-height: 1.6;
    white-space: pre-line;
    overflow-wrap: anywhere;
  }

  .checks,
  .tools,
  .plist,
  .facts,
  .steps,
  .clist {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .checks,
  .plist,
  .facts {
    border: 1px solid var(--line-soft);
    border-radius: var(--r-3);
    background: var(--surface);
    overflow: hidden;
  }
  .checks li + li,
  .plist li + li,
  .facts li + li {
    border-top: 1px solid var(--line-soft);
  }
  .checks label {
    display: grid;
    grid-template-columns: 24px 1fr;
    gap: 12px;
    align-items: center;
    min-height: var(--tap);
    padding: 8px 14px;
    font-size: 14.5px;
    line-height: 1.45;
    cursor: pointer;
  }
  .checks input,
  .shead input {
    width: 22px;
    height: 22px;
    margin: 0;
    cursor: pointer;
  }
  .checks li.on span {
    color: var(--text-3);
  }
  .tools {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding-left: 2px;
    font-size: 14.5px;
    line-height: 1.45;
  }
  .tools li {
    position: relative;
    padding-left: 16px;
    overflow-wrap: anywhere;
  }
  .tools li::before {
    content: '';
    position: absolute;
    left: 2px;
    top: 0.62em;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--text-4);
  }
  .prow {
    display: grid;
    grid-template-columns: 56px 1fr auto;
    grid-template-areas: 'id main qty' 'id sup sup';
    gap: 1px 12px;
    align-items: baseline;
    min-height: var(--tap);
    padding: 9px 14px;
    font-size: 14px;
    color: var(--text);
  }
  a.prow:hover {
    background: color-mix(in oklab, var(--surface-2) 60%, transparent);
  }
  .prow .id {
    grid-area: id;
  }
  .prow.bare {
    align-items: center;
  }
  .pmain {
    grid-area: main;
    display: flex;
    flex-direction: column;
    min-width: 0;
    overflow-wrap: anywhere;
  }
  .pspec {
    font-size: 12.5px;
  }
  .pqty {
    grid-area: qty;
    font-family: var(--mono);
    font-size: 13px;
    color: var(--text-2);
    white-space: nowrap;
  }
  .psup {
    grid-area: sup;
    font-size: 12.5px;
    overflow-wrap: anywhere;
  }
  .facts li {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 6px 10px;
    padding: 10px 14px;
    font-size: 14.5px;
    line-height: 1.5;
  }
  .ftext {
    flex: 1 1 320px;
    min-width: 0;
    overflow-wrap: anywhere;
  }
  .srcs {
    display: inline-flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .src {
    position: relative;
    display: inline-flex;
    align-items: center;
    min-height: 22px;
    padding: 1px 8px;
    border: 1px solid var(--line-soft);
    border-radius: 999px;
    font-family: var(--mono);
    font-size: 11.5px;
    line-height: 1.3;
    color: var(--text-3);
    overflow-wrap: anywhere;
  }
  a.src {
    color: var(--sky);
    border-color: color-mix(in oklab, var(--sky) 30%, var(--ink));
  }
  /* a chip stays small to the eye and still takes a thumb */
  a.src::after {
    content: '';
    position: absolute;
    inset: -11px -3px;
  }
  .src.confirm {
    font-family: var(--font);
    font-weight: 600;
    color: var(--accent-2);
    border-color: var(--accent-line);
    background: var(--accent-soft);
  }

  .stepsec {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .sbar {
    position: sticky;
    top: var(--top, var(--topbar));
    z-index: 5;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    background: color-mix(in oklab, var(--bg) 94%, transparent);
    backdrop-filter: blur(12px);
  }
  .sbar .label {
    margin: 0;
  }
  .count {
    font-size: 13.5px;
    color: var(--text-2);
    white-space: nowrap;
  }
  .count strong {
    color: var(--text);
    font-weight: 600;
  }
  .count.all,
  .count.all strong {
    color: var(--sky);
  }
  .meter {
    flex: 1;
    min-width: 24px;
    height: 4px;
    border-radius: 4px;
    background: var(--line-soft);
    overflow: hidden;
  }
  .meter i {
    display: block;
    height: 100%;
    background: var(--sky);
    border-radius: 4px;
    transition: width var(--t) var(--ease);
  }
  .steps {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .step {
    padding: 4px 16px 14px;
    scroll-margin-top: calc(var(--top, var(--topbar)) + 58px);
    box-shadow: var(--shadow-1);
  }
  .shead {
    display: grid;
    grid-template-columns: 24px auto 1fr;
    gap: 12px;
    align-items: center;
    min-height: var(--tap);
    padding: 8px 0;
    cursor: pointer;
  }
  .sn {
    font-family: var(--mono);
    font-size: 13px;
    font-weight: 600;
    color: var(--sky);
    min-width: 1.4em;
    text-align: right;
  }
  .sdo {
    font-size: 16px;
    font-weight: 620;
    line-height: 1.35;
    color: var(--foam);
    overflow-wrap: anywhere;
  }
  .sbody {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding-left: 36px;
    min-width: 0;
  }
  .how {
    font-size: 14.5px;
    line-height: 1.6;
    white-space: pre-line;
    overflow-wrap: anywhere;
  }
  .clist {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 5px 12px;
    padding: 10px 12px;
    border: 1px solid var(--line-soft);
    border-radius: var(--r-2);
    background: var(--bg-raise);
    font-family: var(--mono);
    font-size: 13px;
    line-height: 1.5;
  }
  .clist li {
    display: contents;
  }
  .cn {
    color: var(--sky);
    font-weight: 600;
    text-align: right;
  }
  .ct {
    min-width: 0;
    overflow-wrap: anywhere;
  }
  .ct.wide {
    grid-column: 1 / -1;
  }
  .expect {
    padding: 2px 0 2px 12px;
    border-left: 2px solid var(--sky);
    font-size: 14.5px;
    line-height: 1.5;
  }
  .expect .label {
    margin-bottom: 2px;
  }
  .expect p,
  .caution p {
    white-space: pre-line;
    overflow-wrap: anywhere;
  }
  .caution {
    display: grid;
    grid-template-columns: 18px 1fr;
    gap: 10px;
    align-items: start;
    padding: 10px 12px;
    border: 1px solid var(--accent-line);
    border-radius: var(--r-2);
    background: var(--accent-soft);
    color: var(--accent-2);
    font-size: 14.5px;
    line-height: 1.5;
  }
  .caution :global(svg) {
    margin-top: 2px;
  }
  .step.on .sdo {
    color: var(--text-3);
    font-weight: 560;
  }
  .step.on .sbody {
    opacity: 0.55;
  }
  .rnote {
    border: 1px solid var(--line-soft);
    border-radius: var(--r-2);
    padding: 0 14px;
  }
  .rnote summary {
    display: flex;
    align-items: center;
    min-height: var(--tap);
    font-size: 13.5px;
    font-weight: 600;
    color: var(--text-2);
    cursor: pointer;
  }
  .rnote[open] {
    padding-bottom: 12px;
  }
  .ticknote {
    margin-bottom: -8px;
  }

  @media (max-width: 759px) {
    .strip {
      gap: 8px 16px;
    }
    .sbar {
      flex-wrap: wrap;
      gap: 6px 10px;
      margin: 0 calc(-1 * var(--gutter));
      padding: 8px var(--gutter);
      border-bottom: 1px solid var(--line-soft);
    }
    .sbar .label {
      display: none;
    }
    .sbar :global(.btn) {
      min-height: var(--tap);
    }
    .untick {
      width: var(--tap);
      padding: 0;
    }
    .untick .t {
      display: none;
    }
    .nextstep {
      margin-left: auto;
    }
    .step {
      padding: 2px 14px 14px;
      scroll-margin-top: calc(var(--top, var(--topbar)) + 72px);
    }
    /* the card's whole width goes to the words */
    .sbody {
      padding-left: 0;
    }
    .prow {
      grid-template-columns: auto 1fr auto;
    }
    .srcs {
      flex-basis: 100%;
      gap: 8px;
    }
    .src {
      min-height: 26px;
    }
  }
</style>

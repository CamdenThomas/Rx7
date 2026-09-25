<!-- One work row: what it is, what it waits on, its note, and — if it is his — his answer. -->
<script lang="ts">
  import { CircleCheck, CirclePlay, CircleX, Hourglass } from '@lucide/svelte';
  import FocusNav from '../../components/FocusNav.svelte';
  import Prose from '../../components/Prose.svelte';
  import WorkAnswer from '../../components/WorkAnswer.svelte';
  import { app } from '../../lib/app.svelte';
  import { drafts } from '../../lib/drafts.svelte';
  import type { WorkRow } from '../../lib/model';
  import { href } from '../../lib/router.svelte';
  import { ui } from '../../lib/ui.svelte';

  let { row, ids }: { row: WorkRow; ids: string[] } = $props();

  const area = $derived(row.area);
  const draft = $derived(drafts.get(area, row.id));
  const answer = $derived(app.answer(area, row.id));
  const mine = $derived(row.owner === 'camden' && (row.status === 'ready' || row.status === 'waiting'));
  const STATUS = { ready: 'Can start now', waiting: 'Waiting', done: 'Done', dropped: 'Dropped' } as const;

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

<FocusNav {ids} at={row.id} open={(id) => ({ name: 'todo', area, id })} list={{ name: 'todo', area }}
  unanswered={(id) => { const w = app.work(area).find((x) => x.id === id); return !!w && w.owner === 'camden' && w.status === 'ready' && !app.answer(area, id); }} />

<article class="focus">
  <header>
    <span class="status {row.status}">
      {#if row.status === 'ready'}<CirclePlay size={16} />{:else if row.status === 'waiting'}<Hourglass size={15} />{:else if row.status === 'done'}<CircleCheck size={16} />{:else}<CircleX size={16} />{/if}
      {STATUS[row.status]}
    </span>
    <span class="id big">{row.id}</span>
    <span class="chip {row.owner === 'camden' ? 'accent' : 'quiet'}">{row.owner === 'camden' ? 'yours' : "Claude's"}</span>
    {#if row.track}<span class="chip quiet">{row.track}{row.part ? ` · part ${row.part}` : ''}</span>{/if}
  </header>
  <h2>{row.item}</h2>
  {#if row.stage_title}<p class="stage faint">Stage {row.stage} · {row.stage_title}</p>{/if}

  {#if mine}
    <section class="answer card">
      <h3 class="label">{row.reply === 'value' ? `Your measurement${row.unit ? ` (${row.unit})` : ''}` : row.reply === 'choice' ? 'Your choice' : 'When it is done'}</h3>
      {#if !answer}
        <textarea class="textarea" rows="2" value={draft.text} oninput={(e) => drafts.set(area, row.id, { text: (e.target as HTMLTextAreaElement).value })}
          placeholder="Anything to add — what you found, what you used (optional)."></textarea>
      {:else if answer.text}
        <p class="his">{answer.text}</p>
      {/if}
      <WorkAnswer {row} big words={draft.text} />
      {#if row.status === 'waiting' && !answer}<p class="faint small">This row still waits on what is listed below — you can still say it is done if it is.</p>{/if}
    </section>
  {/if}

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

  {#if row.note}
    <section>
      <h3 class="label">Note</h3>
      <Prose text={row.note} compact />
    </section>
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
</style>

<!-- Where the project stands: what waits for him, what Claude can do next, what just happened. -->
<script lang="ts">
  import { ArrowRight, CirclePlay } from '@lucide/svelte';
  import WorkAnswer from '../../components/WorkAnswer.svelte';
  import { app } from '../../lib/app.svelte';
  import type { Commit } from '../../lib/model';
  import { href } from '../../lib/router.svelte';
  import { ago, plural } from '../../lib/text';

  let { area }: { area: string } = $props();

  const blocks = $derived(app.blocks(area).filter((b) => !app.answer(area, b.id)));
  const picks = $derived(app.picks(area).filter((p) => !app.answer(area, p.id)));
  const mine = $derived(app.myReady(area));
  const agent = $derived(app.work(area).filter((w) => w.owner === 'agent' && w.status === 'ready'));
  const log = $derived((app.snapshot?.log ?? []).filter((l) => l.area === area).slice(-6).reverse());
  let commits = $state<Commit[]>([]);

  $effect(() => {
    const path = app.area(area)?.path;
    if (path) void app.platform?.commits(path, 6).then((c) => (commits = c));
  });
</script>

<div class="ov">
  <div class="col">
    <section class="card box">
      <header><h3>Waiting for you</h3></header>
      {#if !blocks.length && !picks.length && !mine.length}
        <p class="faint">Nothing. Every question here is answered.</p>
      {/if}
      {#if blocks.length}
        <p class="label">Blocks · {blocks.length}</p>
        <ul class="items">
          {#each blocks as b (b.id)}
            <li><a href={href({ name: 'blocks', area, id: b.id })}><span class="id">{b.id}</span><span>{b.title}</span><ArrowRight size={15} class="go" /></a></li>
          {/each}
        </ul>
      {/if}
      {#if picks.length}
        <a class="bigline" href={href({ name: 'picks', area })}>
          <span><strong>{plural(picks.length, 'part suggestion')}</strong> to say yes or no to</span><ArrowRight size={15} />
        </a>
      {/if}
      {#if mine.length}
        <p class="label">Steps you can do now · {mine.length}</p>
        <ul class="items steps">
          {#each mine.slice(0, 8) as w (w.id)}
            <li>
              <a href={href({ name: 'todo', area, id: w.id })}><CirclePlay size={15} class="play" /><span class="id">{w.id}</span><span class="it">{w.item}</span></a>
              <WorkAnswer row={w} />
            </li>
          {/each}
        </ul>
        {#if mine.length > 8}<a class="more" href={href({ name: 'todo', area })}>All {mine.length} in the TODO</a>{/if}
      {/if}
    </section>

    <section class="card box">
      <header><h3>Ready for Claude</h3><a class="btn small" href={href({ name: 'run', area })}>Run</a></header>
      {#if !agent.length}<p class="faint">Nothing Claude can start — its rows wait on you or on other rows.</p>{/if}
      <ul class="items">
        {#each agent.slice(0, 6) as w (w.id)}
          <li><a href={href({ name: 'todo', area, id: w.id })}><span class="id">{w.id}</span><span class="it">{w.item}</span></a></li>
        {/each}
      </ul>
    </section>
  </div>

  <div class="col">
    <section class="card box">
      <header><h3>Latest</h3></header>
      <ul class="log">
        {#each log as l (l.id)}
          <li><span class="when faint">{ago(l.date)}</span><p>{l.summary}</p></li>
        {/each}
      </ul>
    </section>
    <section class="card box">
      <header><h3>Commits</h3></header>
      {#if !commits.length}<p class="faint">None to show.</p>{/if}
      <ul class="commits">
        {#each commits as c (c.hash)}
          <li><span class="mono hash">{c.hash}</span><span class="subj">{c.subject}</span><span class="faint when">{ago(c.date)}</span></li>
        {/each}
      </ul>
    </section>
  </div>
</div>

<style>
  .ov {
    display: grid;
    grid-template-columns: 1.3fr 1fr;
    gap: 20px;
    align-items: start;
    padding-bottom: calc(40px + var(--tabbar));
  }
  .col {
    display: flex;
    flex-direction: column;
    gap: 20px;
    min-width: 0;
  }
  .box {
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .box header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .box h3 {
    font-size: 16px;
  }
  .label {
    margin-top: 6px;
  }
  .items {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .items li {
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid var(--line-soft);
  }
  .items li:last-child {
    border-bottom: 0;
  }
  .items a {
    flex: 1;
    min-width: 0;
    display: flex;
    align-items: baseline;
    gap: 10px;
    padding: 9px 2px;
    color: var(--text);
    font-size: 14px;
  }
  .items a:hover {
    color: var(--foam);
  }
  .items :global(.go) {
    margin-left: auto;
    color: var(--text-4);
    align-self: center;
  }
  .items :global(.play) {
    color: var(--ember);
    align-self: center;
    flex: none;
  }
  .it {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--text-2);
  }
  .bigline {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 14px;
    border-radius: var(--r-2);
    background: var(--accent-soft);
    border: 1px solid var(--accent-line);
    color: var(--text);
    font-size: 14px;
  }
  .more {
    font-size: 13px;
  }
  .log,
  .commits {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
  }
  .log li {
    padding: 8px 0;
    border-bottom: 1px solid var(--line-soft);
    font-size: 13.5px;
  }
  .log li:last-child {
    border-bottom: 0;
  }
  .log p {
    color: var(--text-2);
    display: -webkit-box;
    -webkit-line-clamp: 3;
    line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .when {
    font-size: 12px;
  }
  .commits li {
    display: grid;
    grid-template-columns: 62px 1fr auto;
    gap: 8px;
    padding: 6px 0;
    font-size: 13px;
    color: var(--text-2);
    border-bottom: 1px solid var(--line-soft);
  }
  .hash {
    color: var(--sky);
    font-size: 12px;
  }
  .subj {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  @media (max-width: 900px) {
    .ov {
      grid-template-columns: 1fr;
    }
  }
</style>

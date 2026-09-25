<!--
  Handing work to Claude (D-406 8.4, CLAUDE.md §6.11): the runs that belong to no one page —
  plan, review, a parts round — and every run's live feed and report. Apply lives at the top
  of Blocks, Picks and TODO.
-->
<script lang="ts">
  import { ChevronDown, GitCommitHorizontal, Play, Square } from '@lucide/svelte';
  import Feed from '../../components/Feed.svelte';
  import { app } from '../../lib/app.svelte';
  import { runs, WORKFLOW_TITLE, type Workflow } from '../../lib/claude.svelte';
  import type { Commit } from '../../lib/model';
  import { ago } from '../../lib/text';

  let { area }: { area: string } = $props();

  const a = $derived(app.area(area));
  const hasPicks = $derived(!!a?.tables.some((t) => t.name === 'picks'));
  const agentReady = $derived(app.work(area).filter((w) => w.owner === 'agent' && w.status === 'ready').length);
  const current = $derived(runs.current && runs.current.record.area === area ? runs.current : null);
  const answers = $derived((app.snapshot?.inbox ?? []).filter((x) => x.area === area && ['block', 'pick', 'work'].includes(x.kind)).length);
  const history = $derived(runs.history.filter((r) => r.area === area));
  let feedOpen = $state(true);
  let commits = $state<Commit[]>([]);

  $effect(() => {
    const path = a?.path;
    if (path) void app.platform?.commits(path, 12).then((c) => (commits = c));
  });

  const OFFERS = $derived(
    [
      { w: 'plan', what: `Take Claude's ready rows (${agentReady} now) and work them through the record until none is left.`, long: true },
      { w: 'review', what: 'Four independent readers check the design; findings come back as work rows or blocks. Changes nothing else.', long: true },
      ...(hasPicks ? [{ w: 'parts', what: 'Search for products for the parts whose spec is settled, and propose a pick and a runner-up for each.', long: true }] : []),
      { w: 'apply', what: 'Apply every answer of yours waiting in this project, from any page.', long: false },
    ] as { w: Workflow; what: string; long: boolean }[],
  );

  async function request(w: Workflow) {
    await app.save({ area, target: w, kind: 'run', choice: w, text: '', context: '' });
  }
</script>

<div class="run">
  <section class="offers">
    {#each OFFERS as o (o.w)}
      <div class="offer card">
        <div>
          <h3>{WORKFLOW_TITLE[o.w]}</h3>
          <p class="muted">{o.what}</p>
          {#if o.long}<p class="faint small">Usually several minutes — you can keep using the app.</p>{/if}
        </div>
        {#if app.platform?.canClaude}
          <button class="btn {o.w === 'apply' ? 'primary' : 'cool'}" disabled={runs.busy || (o.w === 'apply' && !answers)} onclick={() => runs.start(o.w, area)}><Play size={15} /> Run</button>
        {:else}
          <button class="btn" onclick={() => request(o.w)}>Request</button>
        {/if}
      </div>
    {/each}
    {#if !app.platform?.canClaude}
      <p class="faint small">Runs happen on the desktop. A request is saved in the record and runs the next time the desktop app opens.</p>
    {/if}
  </section>

  {#if current}
    <section class="live card">
      <header>
        <span class="dot {current.stream.status}"></span>
        <strong>{current.record.title}</strong>
        <span class="faint">{current.stream.status === 'running' || current.stream.status === 'starting' ? 'running' : current.stream.status}</span>
        <span class="spacer"></span>
        <button class="btn small ghost" onclick={() => (feedOpen = !feedOpen)}><ChevronDown size={15} class={feedOpen ? '' : 'rot'} /> {feedOpen ? 'Hide' : 'Show'} the feed</button>
        {#if runs.busy}<button class="btn small" onclick={() => current.stream.stop()}><Square size={13} /> Stop</button>{/if}
      </header>
      {#if feedOpen}<div class="feed"><Feed stream={current.stream} /></div>{/if}
      {#if current.stream.result}
        <pre class="report mono">{current.stream.result}</pre>
      {/if}
    </section>
  {/if}

  <div class="cols">
    <section>
      <h3 class="label">Earlier runs</h3>
      {#if !history.length}<p class="faint small">None yet from this device.</p>{/if}
      {#each history as h (h.id)}
        <details class="past">
          <summary><span class="dot {h.status}"></span> {h.title} <span class="faint">· {ago(h.started)}</span></summary>
          {#if h.result}<pre class="report mono">{h.result}</pre>{:else}<p class="faint small">It ended with no report ({h.status}).</p>{/if}
        </details>
      {/each}
    </section>
    <section>
      <h3 class="label">Recent commits</h3>
      {#if !commits.length}<p class="faint small">None to show.</p>{/if}
      <ul class="commits">
        {#each commits as c (c.hash)}
          <li><GitCommitHorizontal size={14} /><span class="mono hash">{c.hash}</span><span class="subj">{c.subject}</span><span class="faint when">{ago(c.date)}</span></li>
        {/each}
      </ul>
    </section>
  </div>
</div>

<style>
  .run {
    display: flex;
    flex-direction: column;
    gap: 22px;
    padding-bottom: calc(40px + var(--tabbar));
  }
  .offers {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 14px;
  }
  .offer {
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 14px;
  }
  .offer h3 {
    font-size: 16px;
    margin-bottom: 4px;
  }
  .offer p {
    font-size: 13.5px;
  }
  .offer .btn {
    align-self: flex-start;
  }
  .small {
    font-size: 12.5px;
  }
  .live {
    padding: 0;
    overflow: hidden;
  }
  .live header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--line-soft);
  }
  .spacer {
    flex: 1;
  }
  .feed {
    max-height: 420px;
    overflow-y: auto;
    padding: 14px 16px;
  }
  .report {
    margin: 0;
    padding: 14px 16px;
    font-size: 12.5px;
    line-height: 1.6;
    white-space: pre-wrap;
    background: var(--bg-raise);
    border-top: 1px solid var(--line-soft);
    color: var(--foam);
  }
  .dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    display: inline-block;
    background: var(--text-4);
    flex: none;
  }
  .dot.running,
  .dot.starting {
    background: var(--ember);
    animation: pulse 1s ease-in-out infinite alternate;
  }
  .dot.done {
    background: var(--sky);
  }
  .dot.failed {
    background: var(--ember);
  }
  .cols {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 28px;
  }
  .label {
    display: block;
    margin-bottom: 10px;
  }
  .past {
    border: 1px solid var(--line-soft);
    border-radius: var(--r-2);
    margin-bottom: 8px;
    background: var(--surface);
    overflow: hidden;
  }
  .past summary {
    padding: 10px 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
  }
  .commits {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .commits li {
    display: grid;
    grid-template-columns: 16px 64px 1fr auto;
    gap: 8px;
    align-items: baseline;
    padding: 6px 0;
    border-bottom: 1px solid var(--line-soft);
    font-size: 13px;
    color: var(--text-2);
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
  .when {
    font-size: 12px;
  }
  :global(.rot) {
    transform: rotate(-90deg);
  }
  @keyframes pulse {
    to {
      opacity: 0.35;
    }
  }
  @media (max-width: 900px) {
    .cols {
      grid-template-columns: 1fr;
    }
  }
</style>

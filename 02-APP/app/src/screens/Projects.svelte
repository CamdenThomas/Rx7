<!--
  The project hub (D-406 6.1, 6.4): one card per project — its id, name and icon, its phase,
  how far it has got, what waits for him, and when it last moved.
-->
<script lang="ts">
  import { Plus } from '@lucide/svelte';
  import ProjectIcon from '../components/ProjectIcon.svelte';
  import Progress from '../components/Progress.svelte';
  import { app, type ProjectSummary } from '../lib/app.svelte';
  import { href } from '../lib/router.svelte';
  import { ago, plural } from '../lib/text';

  const live = $derived(app.summaries.filter((s) => s.phase !== 'COMPLETE'));
  const finished = $derived(app.summaries.filter((s) => s.phase === 'COMPLETE'));
  // The app keeps its own work in 02-APP, which is not a project (D-428).
  const own = $derived(app.areas.find((a) => a.kind === 'app'));

  function waitingText(s: ProjectSummary) {
    const w = s.waiting;
    const parts = [w.blocks && plural(w.blocks, 'block'), w.picks && plural(w.picks, 'pick'), w.work && plural(w.work, 'step')].filter(Boolean);
    return parts.join(' · ');
  }
</script>

<div class="page">
  <header class="head">
    <div>
      <p class="label">Projects</p>
      <h1>What is being done to the car</h1>
    </div>
    <a class="btn primary big" href={href({ name: 'new-project' })}><Plus size={18} /> New project</a>
  </header>

  <div class="grid-cards">
    {#each live as s, i (s.name)}
      <a class="pcard card rise" style:animation-delay="{i * 40}ms" href={href({ name: 'project', area: s.name })}>
        <div class="top">
          <span class="icon"><ProjectIcon name={s.icon} size={22} /></span>
          <div class="name">
            <span class="id">{s.area.prefix}</span>
            <h2>{s.title}</h2>
          </div>
          <span class="chip phase">{s.phase.toLowerCase()}</span>
        </div>
        <p class="goal">{s.goal}</p>
        <Progress done={s.done} total={s.total} />
        <div class="foot">
          {#if s.waiting.total}
            <span class="wait"><span class="pip"></span>{waitingText(s)} waiting for you</span>
          {:else}
            <span class="faint">Nothing waiting for you</span>
          {/if}
          {#if s.answered}<span class="chip cool">{plural(s.answered, 'answer')} to apply</span>{/if}
        </div>
        {#if s.last}
          <p class="last"><span class="when">{ago(s.last.date)}</span> {s.last.summary}</p>
        {/if}
      </a>
    {/each}
  </div>

  {#if finished.length}
    <details class="finished">
      <summary><span class="label">Finished · {finished.length}</span></summary>
      <div class="grid-cards">
        {#each finished as s (s.name)}
          <a class="pcard card" href={href({ name: 'project', area: s.name })}>
            <div class="top">
              <span class="icon"><ProjectIcon name={s.icon} size={22} /></span>
              <div class="name"><span class="id">{s.area.prefix}</span><h2>{s.title}</h2></div>
            </div>
          </a>
        {/each}
      </div>
    </details>
  {/if}
  {#if own}
    <p class="own faint">The app's own work list: <a href={href({ name: 'todo', area: own.name })}>{own.name}</a></p>
  {/if}
</div>

<style>
  .own {
    margin-top: 28px;
    font-size: 13.5px;
  }
  .head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    margin: 12px 0 24px;
  }
  h1 {
    font-size: clamp(26px, 3vw, 34px);
    margin-top: 6px;
  }
  .grid-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
    gap: 18px;
  }
  .pcard {
    display: flex;
    flex-direction: column;
    gap: 14px;
    padding: 20px;
    color: var(--text);
    transition:
      transform var(--t) var(--ease),
      border-color var(--t);
  }
  .pcard:hover {
    transform: translateY(-2px);
    border-color: var(--line);
    color: var(--text);
  }
  .top {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .icon {
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: linear-gradient(145deg, var(--steel), color-mix(in oklab, var(--steel) 50%, var(--ink)));
    color: var(--foam);
    box-shadow: var(--shadow-1);
    flex: none;
  }
  .name {
    flex: 1;
    min-width: 0;
  }
  .name h2 {
    font-size: 19px;
  }
  .phase {
    text-transform: capitalize;
  }
  .goal {
    color: var(--text-2);
    font-size: 14px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .foot {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    font-size: 13.5px;
  }
  .wait {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: var(--accent-2);
    font-weight: 580;
  }
  .pip {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--ember);
    box-shadow: 0 0 0 3px var(--accent-soft);
  }
  .last {
    font-size: 12.5px;
    color: var(--text-3);
    border-top: 1px solid var(--line-soft);
    padding-top: 12px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .when {
    color: var(--text-2);
    margin-right: 4px;
  }
  .finished {
    margin-top: 32px;
  }
  .finished summary {
    cursor: pointer;
    margin-bottom: 14px;
  }
  @media (max-width: 759px) {
    .head {
      flex-direction: column;
      align-items: stretch;
    }
    .grid-cards {
      grid-template-columns: 1fr;
    }
  }
</style>

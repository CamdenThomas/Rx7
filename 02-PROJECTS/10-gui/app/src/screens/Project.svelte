<!--
  One project (D-406 6.3): where it stands, then its pages — Blocks, Picks, TODO, Decisions,
  Parts and Run. Each count on a tab is what waits for him there.
-->
<script lang="ts">
  import ProjectIcon from '../components/ProjectIcon.svelte';
  import Progress from '../components/Progress.svelte';
  import Overview from './project/Overview.svelte';
  import Blocks from './project/Blocks.svelte';
  import Picks from './project/Picks.svelte';
  import Todo from './project/Todo.svelte';
  import Decisions from './project/Decisions.svelte';
  import Parts from './project/Parts.svelte';
  import Run from './project/Run.svelte';
  import { app } from '../lib/app.svelte';
  import { href, type Route } from '../lib/router.svelte';

  type ProjectRoute = Extract<Route, { area: string }>;
  let { route }: { route: ProjectRoute } = $props();

  const area = $derived(route.area);
  const a = $derived(app.area(area));
  const s = $derived(a ? app.summarise(a) : null);
  const focused = $derived('id' in route && !!route.id);

  const tabs = $derived.by(() => {
    const has = (t: string) => !!a?.tables.some((x) => x.name === t);
    const picks = app.picks(area);
    return [
      { name: 'project', label: 'Overview', count: 0 },
      { name: 'blocks', label: 'Blocks', count: s?.waiting.blocks ?? 0, total: app.blocks(area).length },
      ...(has('picks') ? [{ name: 'picks', label: 'Picks', count: s?.waiting.picks ?? 0, total: picks.length }] : []),
      { name: 'todo', label: 'TODO', count: s?.waiting.work ?? 0 },
      { name: 'decisions', label: 'Decisions', count: 0, total: app.decisions(area).filter((d) => d.status === 'standing').length },
      ...(has('parts') ? [{ name: 'parts', label: 'Parts', count: 0 }] : []),
      { name: 'run', label: 'Run', count: 0 },
    ] as { name: Route['name']; label: string; count: number; total?: number }[];
  });
</script>

{#if !a || !s}
  <div class="page"><p class="muted">There is no project named {area}.</p></div>
{:else}
  <div class="page project">
    <header class="head" class:compact={focused}>
      <span class="icon"><ProjectIcon name={s.icon} size={focused ? 18 : 24} /></span>
      <div class="titles">
        <div class="t1">
          <span class="id">{a.prefix}</span>
          <h1>{s.title}</h1>
          <span class="chip phase">{s.phase.toLowerCase()}</span>
        </div>
        {#if !focused}<p class="goal">{s.goal}</p>{/if}
      </div>
      {#if !focused}
        <div class="meter"><Progress done={s.done} total={s.total} /><span class="faint">work rows done</span></div>
      {/if}
    </header>

    <nav class="tabs" aria-label="Project pages">
      {#each tabs as t (t.name)}
        <a
          href={href(t.name === 'project' ? { name: 'project', area } : ({ name: t.name, area } as Route))}
          class:on={route.name === t.name}
          aria-current={route.name === t.name ? 'page' : undefined}
        >
          {t.label}
          {#if t.count}<span class="count hot">{t.count}</span>{:else if t.total}<span class="count">{t.total}</span>{/if}
        </a>
      {/each}
    </nav>

    <div class="content">
      {#if route.name === 'project'}
        <Overview {area} />
      {:else if route.name === 'blocks'}
        <Blocks {area} id={route.id} />
      {:else if route.name === 'picks'}
        <Picks {area} id={route.id} />
      {:else if route.name === 'todo'}
        <Todo {area} id={route.id} />
      {:else if route.name === 'decisions'}
        <Decisions {area} id={route.id} />
      {:else if route.name === 'parts'}
        <Parts {area} />
      {:else if route.name === 'run'}
        <Run {area} />
      {/if}
    </div>
  </div>
{/if}

<style>
  .project {
    padding-top: 14px;
  }
  .head {
    display: grid;
    grid-template-columns: auto 1fr minmax(220px, 300px);
    gap: 16px;
    align-items: center;
    margin-bottom: 18px;
  }
  .head.compact {
    grid-template-columns: auto 1fr;
    margin-bottom: 12px;
  }
  .icon {
    display: grid;
    place-items: center;
    width: 52px;
    height: 52px;
    border-radius: 14px;
    background: linear-gradient(145deg, var(--steel), color-mix(in oklab, var(--steel) 50%, var(--ink)));
    color: var(--foam);
    box-shadow: var(--shadow-1);
  }
  .compact .icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
  }
  .titles {
    min-width: 0;
  }
  .t1 {
    display: flex;
    align-items: baseline;
    gap: 10px;
    flex-wrap: wrap;
  }
  .t1 .id {
    font-size: 15px;
  }
  h1 {
    font-size: 26px;
  }
  .compact h1 {
    font-size: 19px;
  }
  .phase {
    text-transform: capitalize;
    align-self: center;
  }
  .goal {
    margin-top: 6px;
    color: var(--text-2);
    font-size: 14px;
    max-width: 760px;
  }
  .meter {
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 12px;
  }
  .tabs {
    display: flex;
    gap: 2px;
    border-bottom: 1px solid var(--line-soft);
    margin-bottom: 20px;
    overflow-x: auto;
    scrollbar-width: none;
  }
  .tabs a {
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 7px;
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
  .count {
    font-size: 11.5px;
    font-weight: 650;
    min-width: 20px;
    height: 20px;
    padding: 0 6px;
    display: inline-grid;
    place-items: center;
    border-radius: 999px;
    background: var(--surface-2);
    color: var(--text-3);
  }
  .count.hot {
    background: var(--ember);
    color: #1f1714;
  }
  @media (max-width: 759px) {
    .head {
      grid-template-columns: auto 1fr;
      row-gap: 10px;
    }
    .icon {
      width: 40px;
      height: 40px;
      border-radius: 11px;
    }
    h1 {
      font-size: 22px;
    }
    .titles {
      display: contents;
    }
    .t1 {
      align-self: center;
    }
    .goal {
      grid-column: 1 / -1;
      margin-top: 0;
    }
    .meter {
      grid-column: 1 / -1;
    }
    .tabs {
      margin: 0 calc(-1 * var(--gutter)) 16px;
      padding: 0 var(--gutter);
    }
  }
</style>

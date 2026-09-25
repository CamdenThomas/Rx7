<!--
  One decision in full (D-406 8.3): its text, what it replaced and what replaced it, the
  block it closed, and every decision and row that cites it.
-->
<script lang="ts">
  import { ArrowRight } from '@lucide/svelte';
  import Prose from './Prose.svelte';
  import { app } from '../lib/app.svelte';
  import type { Decision } from '../lib/model';
  import { href } from '../lib/router.svelte';
  import { day } from '../lib/text';
  import { projectLabel, ui } from '../lib/ui.svelte';

  let { d }: { d: Decision } = $props();

  const STATUS: Record<string, string> = { standing: 'standing', superseded: 'superseded', withdrawn: 'withdrawn', inherited: 'owned by another project' };
  const title = (id: string) => app.decision(id)?.title ?? '';

  $effect(() => {
    ui.context = `decision ${d.id}: ${d.title}`;
    return () => (ui.context = '');
  });
</script>

<article class="dec">
  <header>
    <div class="meta">
      <span class="id big">{d.id}</span>
      <span class="chip {d.status === 'standing' ? 'cool' : d.status === 'superseded' ? 'accent' : 'quiet'}">{STATUS[d.status] ?? d.status}</span>
      {#if d.date}<span class="faint">{day(d.date)}</span>{/if}
      {#if d.system}<span class="faint">· {d.system}</span>{/if}
      <span class="faint">· {projectLabel(d.area)}</span>
    </div>
    <h2>{d.title}</h2>
  </header>

  {#if d.superseded_by}
    <a class="replaced card" href={href({ name: 'decision', id: d.superseded_by })}>
      <span class="label">Replaced by</span>
      <span><span class="id">{d.superseded_by}</span> {title(d.superseded_by)}</span>
      <ArrowRight size={16} />
    </a>
  {/if}

  {#if d.supersedes.length || d.closes.length}
    <div class="links">
      {#if d.supersedes.length}
        <div><span class="label">It replaced</span>
          {#each d.supersedes as s (s)}<a class="chip" href={href({ name: 'decision', id: s })} title={title(s)}>{s}</a>{/each}</div>
      {/if}
      {#if d.closes.length}
        <div><span class="label">It answered</span>{#each d.closes as c (c)}<span class="chip quiet mono">{c}</span>{/each}</div>
      {/if}
    </div>
  {/if}

  {#if d.body}
    <Prose text={d.body.replace(/^#\s[^\n]*\n+/, '')} />
  {:else}
    <p class="muted">This decision keeps only its title — its reasoning lives in the decision that replaced it.</p>
  {/if}

  {#if d.cited_by.length || d.cited_in.length}
    <footer>
      {#if d.cited_by.length}
        <div><span class="label">Cited by {d.cited_by.length} decisions</span>
          <div class="chips">{#each d.cited_by as c (c)}<a class="chip" href={href({ name: 'decision', id: c })} title={title(c)}>{c}</a>{/each}</div></div>
      {/if}
      {#if d.cited_in.length}
        <div><span class="label">Cited in {d.cited_in.length} rows</span>
          <div class="chips">
            {#each d.cited_in.slice(0, 40) as r, i (i)}
              <a class="chip quiet" href={r.table === 'work' ? href({ name: 'todo', area: r.area, id: r.key }) : href({ name: 'row', area: r.area, table: r.table, key: r.key })}>{r.table} {r.key}</a>
            {/each}
          </div></div>
      {/if}
    </footer>
  {/if}
</article>

<style>
  .dec {
    display: flex;
    flex-direction: column;
    gap: 18px;
    max-width: 820px;
  }
  .meta {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    font-size: 13px;
  }
  .id.big {
    font-size: 16px;
  }
  h2 {
    margin-top: 10px;
    font-size: clamp(20px, 2vw, 24px);
    line-height: 1.3;
  }
  .replaced {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    color: var(--text);
    border-color: var(--accent-line);
  }
  .replaced span:nth-child(2) {
    flex: 1;
  }
  .links {
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
  }
  .links > div,
  footer > div {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }
  .links .label {
    margin-right: 4px;
  }
  .chip {
    font-family: var(--mono);
  }
  a.chip:hover {
    color: var(--foam);
    border-color: var(--sky);
  }
  footer {
    display: flex;
    flex-direction: column;
    gap: 14px;
    border-top: 1px solid var(--line-soft);
    padding-top: 16px;
  }
  footer > div {
    flex-direction: column;
    align-items: flex-start;
  }
  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
</style>

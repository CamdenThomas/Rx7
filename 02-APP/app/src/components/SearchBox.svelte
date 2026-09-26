<!--
  Search everything (D-406 3.4). The same box is the overlay on the desktop (Ctrl K) and the
  Search tab on the phone. Arrow keys move, Enter opens, results say what kind of thing
  each one is and where it lives.
-->
<script lang="ts">
  import { Search, X } from '@lucide/svelte';
  import { app } from '../lib/app.svelte';
  import { router } from '../lib/router.svelte';
  import { buildIndex, search, type Doc, type Hit, type HitKind } from '../lib/search';
  import { projectLabel } from '../lib/ui.svelte';

  let { query = $bindable(''), onpick, autofocus = true }: { query?: string; onpick?: () => void; autofocus?: boolean } = $props();

  let docs: Doc[] = [];
  let built: unknown = null;
  let active = $state(0);
  let input: HTMLInputElement | undefined = $state();

  const hits = $derived.by(() => {
    if (built !== app.snapshot && app.snapshot) {
      docs = buildIndex(app.snapshot);
      built = app.snapshot;
    }
    return search(docs, query);
  });

  const LABEL: Record<HitKind, string> = { project: 'Project', block: 'Block', decision: 'Decision', work: 'Work', pick: 'Pick', part: 'Manual', row: 'Row' };

  $effect(() => {
    if (autofocus) input?.focus();
  });
  $effect(() => {
    void query;
    active = 0;
  });

  function open(h: Hit) {
    router.go(h.route);
    onpick?.();
  }

  function keydown(e: KeyboardEvent) {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      active = Math.min(active + 1, hits.length - 1);
      document.getElementById(`hit-${active}`)?.scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      active = Math.max(active - 1, 0);
      document.getElementById(`hit-${active}`)?.scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'Enter' && hits[active]) {
      open(hits[active]);
    }
  }

  function where(h: Hit) {
    const a = app.area(h.area);
    const place = a?.kind === 'project' ? projectLabel(h.area) : h.area;
    return h.kind === 'row' ? `${place} · ${h.sub}` : h.sub ? `${place} · ${h.sub}` : place;
  }
</script>

<div class="box">
  <label class="field">
    <Search size={18} />
    <input
      bind:this={input}
      bind:value={query}
      onkeydown={keydown}
      placeholder="A part number, a wire colour, a decision, a torque, a date…"
      aria-label="Search everything"
      spellcheck="false"
      autocomplete="off"
    />
    {#if query}<button class="clear" onclick={() => (query = '')} aria-label="Clear"><X size={16} /></button>{/if}
  </label>

  <div class="results" role="listbox">
    {#if query.trim() && !hits.length}
      <p class="none">Nothing in the record matches “{query}”.</p>
    {:else if !query.trim()}
      <p class="none">Everything is searchable: every block, decision, work row, pick, and every row of every table.</p>
    {/if}
    {#each hits as h, i (h.kind + h.area + h.id + i)}
      <button id="hit-{i}" class="hit" class:on={i === active} role="option" aria-selected={i === active} onmouseenter={() => (active = i)} onclick={() => open(h)}>
        <span class="kind {h.kind}">{LABEL[h.kind]}</span>
        <span class="main">
          <span class="line"><span class="id">{h.id}</span> <span class="title">{h.title}</span></span>
          <span class="snip">{h.snippet}</span>
        </span>
        <span class="where">{where(h)}</span>
      </button>
    {/each}
  </div>
</div>

<style>
  .box {
    display: flex;
    flex-direction: column;
    min-height: 0;
    height: 100%;
  }
  .field {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 14px;
    height: 54px;
    border-bottom: 1px solid var(--line-soft);
    color: var(--text-3);
    flex: none;
  }
  input {
    flex: 1;
    min-width: 0;
    background: none;
    border: 0;
    outline: none;
    font-size: 16px;
    color: var(--text);
  }
  input::placeholder {
    color: var(--text-4);
  }
  .clear {
    background: none;
    border: 0;
    color: var(--text-3);
    display: inline-flex;
    padding: 6px;
  }
  .results {
    overflow-y: auto;
    padding: 6px;
    min-height: 0;
    flex: 1;
  }
  .none {
    padding: 22px 14px;
    color: var(--text-3);
    font-size: 14px;
  }
  .hit {
    display: grid;
    grid-template-columns: 76px 1fr auto;
    gap: 12px;
    align-items: start;
    width: 100%;
    text-align: left;
    padding: 10px 10px;
    border: 0;
    border-radius: var(--r-2);
    background: transparent;
    color: inherit;
  }
  .hit.on {
    background: var(--surface-2);
  }
  .kind {
    font-size: 11px;
    font-weight: 650;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-3);
    padding-top: 3px;
  }
  .kind.block {
    color: var(--ember);
  }
  .kind.decision {
    color: var(--sky);
  }
  .main {
    display: flex;
    flex-direction: column;
    gap: 3px;
    min-width: 0;
  }
  .line {
    display: flex;
    gap: 8px;
    align-items: baseline;
    min-width: 0;
  }
  .title {
    font-weight: 560;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 14px;
  }
  .snip {
    font-size: 12.5px;
    color: var(--text-3);
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  .where {
    font-size: 12px;
    color: var(--text-4);
    white-space: nowrap;
    padding-top: 2px;
  }
  @media (max-width: 759px) {
    .hit {
      grid-template-columns: 1fr;
      gap: 4px;
    }
    .where {
      order: -1;
    }
    .kind {
      display: none;
    }
  }
</style>

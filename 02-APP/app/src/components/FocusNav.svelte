<!--
  Moving through a list one item at a time (D-406 8.4): back or forward, straight to the next
  one he has not answered, or back to the whole list. Keys: ← → , N for next unanswered,
  Esc for the list.
-->
<script lang="ts">
  import { ArrowLeft, ArrowRight, List, SkipForward } from '@lucide/svelte';
  import { router, type Route } from '../lib/router.svelte';

  let {
    ids,
    at,
    open,
    list,
    unanswered,
  }: {
    ids: string[];
    at: string;
    open: (id: string) => Route;
    list: Route;
    unanswered: (id: string) => boolean;
  } = $props();

  const i = $derived(ids.indexOf(at));
  const prev = $derived(i > 0 ? ids[i - 1] : null);
  const next = $derived(i >= 0 && i < ids.length - 1 ? ids[i + 1] : null);
  const nextOpen = $derived.by(() => {
    for (let k = 1; k <= ids.length; k++) {
      const id = ids[(i + k) % ids.length];
      if (id !== at && unanswered(id)) return id;
    }
    return null;
  });

  function keydown(e: KeyboardEvent) {
    if ((e.target as HTMLElement)?.closest('input, textarea, select, [contenteditable]') || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key === 'ArrowLeft' && prev) router.go(open(prev));
    else if (e.key === 'ArrowRight' && next) router.go(open(next));
    else if ((e.key === 'n' || e.key === 'N') && nextOpen) router.go(open(nextOpen));
    else if (e.key === 'Escape') router.go(list);
  }
</script>

<svelte:window onkeydown={keydown} />

<div class="focusnav">
  <button class="btn small" onclick={() => router.go(list)} title="Back to the list (Esc)" aria-label="List"><List size={15} /> <span class="t">List</span></button>
  <span class="pos num"><strong>{i + 1}</strong> of {ids.length}</span>
  <div class="steps">
    <button class="btn small icon" disabled={!prev} onclick={() => prev && router.go(open(prev))} aria-label="Previous" title="Previous (←)"><ArrowLeft size={16} /></button>
    <button class="btn small icon" disabled={!next} onclick={() => next && router.go(open(next))} aria-label="Next" title="Next (→)"><ArrowRight size={16} /></button>
    <button class="btn small" disabled={!nextOpen} onclick={() => nextOpen && router.go(open(nextOpen))} title="Next unanswered (N)" aria-label="Next unanswered">
      <SkipForward size={15} /> <span class="t">Next unanswered</span>
    </button>
  </div>
</div>

<style>
  .focusnav {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 14px;
  }
  .pos {
    font-size: 13px;
    color: var(--text-3);
  }
  .pos strong {
    color: var(--text);
    font-weight: 600;
  }
  .steps {
    display: flex;
    gap: 6px;
    margin-left: auto;
  }
  @media (max-width: 759px) {
    .focusnav {
      position: fixed;
      z-index: 25;
      left: 0;
      right: 0;
      bottom: var(--tabbar);
      padding: 8px var(--gutter);
      background: color-mix(in oklab, var(--bg) 92%, transparent);
      backdrop-filter: blur(14px);
      border-top: 1px solid var(--line-soft);
    }
    .focusnav :global(.btn) {
      min-height: 40px;
    }
    .focusnav :global(.btn.icon) {
      width: 40px;
    }
    .t {
      display: none;
    }
  }
</style>

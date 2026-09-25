<!--
  Select any words in the Manual and two buttons appear beside them (D-417, D-426): Note keeps
  his note on exactly those words with where he saw them, on every device; Ask opens the chat
  about them, only where Claude can be reached (the desktop, D-403).
-->
<script lang="ts">
  import { MessageSquare, StickyNote } from '@lucide/svelte';
  import { app } from '../lib/app.svelte';
  import { crumbs, ui } from '../lib/ui.svelte';
  import { router } from '../lib/router.svelte';
  import type { Where } from '../lib/manual';
  import NoteDialog from './NoteDialog.svelte';

  let { within }: { within: HTMLElement | undefined } = $props();

  let at = $state<{ x: number; y: number } | null>(null);
  let noting = $state<Where | null>(null);
  let text = '';

  const page = () => crumbs(router.route).map((c) => c.label).join(' › ');

  function update() {
    if (noting) return;
    const sel = window.getSelection();
    const t = sel?.toString().replace(/\s+/g, ' ').trim() ?? '';
    if (!sel || !t || t.length > 600 || !within || !sel.rangeCount || !within.contains(sel.getRangeAt(0).commonAncestorContainer)) {
      at = null;
      return;
    }
    const r = sel.getRangeAt(0).getBoundingClientRect();
    text = t;
    at = { x: Math.min(Math.max(r.left + r.width / 2, 110), window.innerWidth - 110), y: r.top };
  }

  function ask() {
    ui.ask(text, page());
    window.getSelection()?.removeAllRanges();
    at = null;
  }

  function note() {
    noting = { where: location.hash || '#/manual', page: page(), selected: text };
    window.getSelection()?.removeAllRanges();
    at = null;
  }
</script>

<svelte:document onselectionchange={update} />
<svelte:window onscroll={() => (at = null)} />

{#if at}
  <div class="bar" style="left: {at.x}px; top: {at.y}px">
    <button class="btn small" onmousedown={(e) => e.preventDefault()} onclick={note}><StickyNote size={14} /> Note</button>
    {#if app.platform?.canClaude}
      <button class="btn small cool" onmousedown={(e) => e.preventDefault()} onclick={ask}><MessageSquare size={14} /> Ask about this</button>
    {/if}
  </div>
{/if}
{#if noting}<NoteDialog at={noting} onclose={() => (noting = null)} />{/if}

<style>
  .bar {
    position: fixed;
    z-index: 35;
    display: flex;
    gap: 6px;
    transform: translate(-50%, calc(-100% - 8px));
    animation: fade var(--t-fast) both;
  }
  .bar :global(.btn) {
    box-shadow: var(--shadow-2);
  }
</style>

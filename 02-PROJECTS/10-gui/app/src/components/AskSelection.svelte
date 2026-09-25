<!--
  Ask about exactly this (D-417, his 4.1): select any words in the Manual and a button appears
  beside them; it opens the chat with those words as the thing he is asking about. Only where
  Claude can be reached (the desktop, D-403).
-->
<script lang="ts">
  import { MessageSquare } from '@lucide/svelte';
  import { app } from '../lib/app.svelte';
  import { crumbs, ui } from '../lib/ui.svelte';
  import { router } from '../lib/router.svelte';

  let { within }: { within: HTMLElement | undefined } = $props();

  let at = $state<{ x: number; y: number } | null>(null);
  let text = '';

  function update() {
    const sel = window.getSelection();
    const t = sel?.toString().replace(/\s+/g, ' ').trim() ?? '';
    if (!sel || !t || t.length > 600 || !within || !sel.rangeCount || !within.contains(sel.getRangeAt(0).commonAncestorContainer)) {
      at = null;
      return;
    }
    const r = sel.getRangeAt(0).getBoundingClientRect();
    text = t;
    at = { x: Math.min(Math.max(r.left + r.width / 2, 70), window.innerWidth - 70), y: r.top };
  }

  function ask() {
    ui.ask(text, crumbs(router.route).map((c) => c.label).join(' › '));
    window.getSelection()?.removeAllRanges();
    at = null;
  }
</script>

<svelte:document onselectionchange={update} />
<svelte:window onscroll={() => (at = null)} />

{#if at && app.platform?.canClaude}
  <button class="ask btn small cool" style="left: {at.x}px; top: {at.y}px" onmousedown={(e) => e.preventDefault()} onclick={ask}>
    <MessageSquare size={14} /> Ask about this
  </button>
{/if}

<style>
  .ask {
    position: fixed;
    z-index: 35;
    transform: translate(-50%, calc(-100% - 8px));
    box-shadow: var(--shadow-2);
    animation: fade var(--t-fast) both;
  }
</style>

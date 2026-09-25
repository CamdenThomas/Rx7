<!-- The chat on every page (D-406 7.7): it knows which page he is on. -->
<script lang="ts">
  import { RotateCcw, X } from '@lucide/svelte';
  import Chat from './Chat.svelte';
  import { Conversation } from '../lib/claude.svelte';
  import { crumbs, ui } from '../lib/ui.svelte';
  import { router } from '../lib/router.svelte';

  let convo = $state(new Conversation('Camden opened the chat panel in the Rx7 app.'));

  const where = $derived(crumbs(router.route).map((c) => c.label).join(' › '));
  const prefix = () => `[He is looking at: ${where}${ui.context ? ` — ${ui.context}` : ''}]`;

  function keydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && ui.chatOpen && !ui.searchOpen) ui.chatOpen = false;
  }
</script>

<svelte:window onkeydown={keydown} />

<aside class="panel-chat" aria-label="Ask Claude">
  <header>
    <div>
      <strong>Ask Claude</strong>
      <span class="where">{where}</span>
    </div>
    <button class="btn icon ghost small" onclick={() => (convo = new Conversation('Camden opened the chat panel in the Rx7 app.'))} title="New conversation" aria-label="New conversation"><RotateCcw size={15} /></button>
    <button class="btn icon ghost small" onclick={() => (ui.chatOpen = false)} aria-label="Close"><X size={16} /></button>
  </header>
  <Chat {convo} {prefix} empty="Claude reads the record to answer. It can explain anything on this page, but it never changes the record from here." />
</aside>

<style>
  .panel-chat {
    position: fixed;
    z-index: 40;
    top: 0;
    right: 0;
    bottom: 0;
    width: min(420px, 100vw);
    display: flex;
    flex-direction: column;
    background: var(--surface);
    border-left: 1px solid var(--line);
    box-shadow: var(--shadow-3);
    animation: slide var(--t) var(--ease);
  }
  header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 12px 10px 12px 16px;
    border-bottom: 1px solid var(--line-soft);
  }
  header div {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
  }
  .where {
    font-size: 12px;
    color: var(--text-3);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  @keyframes slide {
    from {
      transform: translateX(24px);
      opacity: 0;
    }
  }
</style>

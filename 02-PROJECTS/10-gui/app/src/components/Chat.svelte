<!--
  A conversation with Claude: his questions, Claude's answers streaming in. Used by the chat
  panel on every page and by Discuss beside a block. Read-only (D-406, CLAUDE.md §6.11).
-->
<script lang="ts">
  import { ArrowUp, Square } from '@lucide/svelte';
  import type { Conversation } from '../lib/claude.svelte';
  import Feed from './Feed.svelte';
  import Prose from './Prose.svelte';

  let {
    convo,
    placeholder = 'Ask anything about the car…',
    prefix = () => '',
    empty = '',
  }: { convo: Conversation; placeholder?: string; prefix?: () => string; empty?: string } = $props();

  let text = $state('');

  async function send() {
    const q = text.trim();
    if (!q || convo.busy) return;
    text = '';
    const p = prefix();
    await convo.ask(p ? `${p}\n\n${q}` : q);
  }

  function keydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  }

  const shown = (t: string) => t.replace(/^\[He is looking at:[^\]]*\]\s*/, '');
</script>

<div class="chat">
  <div class="log">
    {#if !convo.messages.length && !convo.live && empty}
      <p class="empty">{empty}</p>
    {/if}
    {#each convo.messages as m, i (i)}
      <div class="msg {m.who}">
        {#if m.who === 'claude'}<Prose text={m.text} compact />{:else}<p>{shown(m.text)}</p>{/if}
      </div>
    {/each}
    {#if convo.live}
      <div class="msg claude"><Feed stream={convo.live} tools={false} /></div>
    {/if}
  </div>
  <div class="compose">
    <textarea bind:value={text} onkeydown={keydown} rows="2" {placeholder} aria-label="Your question"></textarea>
    {#if convo.busy}
      <button class="btn icon" onclick={() => convo.stop()} aria-label="Stop"><Square size={15} /></button>
    {:else}
      <button class="btn icon primary" onclick={send} disabled={!text.trim()} aria-label="Send"><ArrowUp size={17} /></button>
    {/if}
  </div>
</div>

<style>
  .chat {
    display: flex;
    flex-direction: column;
    min-height: 0;
    height: 100%;
  }
  .log {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 14px;
  }
  .empty {
    color: var(--text-3);
    font-size: 14px;
  }
  .msg {
    max-width: 94%;
  }
  .msg.you {
    align-self: flex-end;
    background: var(--steel);
    padding: 9px 13px;
    border-radius: 14px 14px 4px 14px;
    font-size: 14px;
    white-space: pre-wrap;
  }
  .msg.claude {
    align-self: flex-start;
  }
  .compose {
    display: flex;
    gap: 8px;
    align-items: flex-end;
    padding: 10px;
    border-top: 1px solid var(--line-soft);
  }
  textarea {
    flex: 1;
    resize: none;
    background: var(--bg-raise);
    border: 1px solid var(--line);
    border-radius: var(--r-2);
    padding: 9px 12px;
    font-size: 14px;
    line-height: 1.45;
    color: var(--text);
    max-height: 160px;
  }
  textarea:focus {
    outline: none;
    border-color: var(--sky);
  }
</style>

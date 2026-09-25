<!-- What Claude is doing, as it does it: its words, and one line per tool it uses. -->
<script lang="ts">
  import { Terminal, FileText, CircleAlert } from '@lucide/svelte';
  import type { Stream } from '../lib/claude.svelte';
  import Prose from './Prose.svelte';

  let { stream, tools = true }: { stream: Stream; tools?: boolean } = $props();
  let end: HTMLDivElement | undefined = $state();

  $effect(() => {
    void stream.items.length;
    void stream.partial;
    end?.scrollIntoView({ block: 'nearest' });
  });
</script>

<div class="feed">
  {#each stream.items as it, i (i)}
    {#if it.kind === 'text'}
      <div class="text"><Prose text={it.text} compact /></div>
    {:else if it.kind === 'tool' && tools}
      <div class="tool mono">
        {#if it.text.startsWith('$')}<Terminal size={13} />{:else}<FileText size={13} />{/if}
        <span>{it.text}</span>
      </div>
    {:else if it.kind === 'error'}
      <div class="error"><CircleAlert size={15} /> {it.text}</div>
    {:else if it.kind === 'note' && stream.status === 'failed'}
      <div class="note mono">{it.text}</div>
    {/if}
  {/each}
  {#if stream.partial}
    <div class="text live"><Prose text={stream.partial} compact /><span class="caret"></span></div>
  {:else if stream.status === 'starting' || stream.status === 'running'}
    <div class="thinking"><span></span><span></span><span></span></div>
  {/if}
  <div bind:this={end}></div>
</div>

<style>
  .feed {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .tool {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-3);
    padding: 4px 10px;
    border-left: 2px solid var(--line);
    overflow: hidden;
    white-space: nowrap;
  }
  .tool span {
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .error {
    display: flex;
    gap: 8px;
    align-items: center;
    color: var(--accent-2);
    font-size: 14px;
  }
  .note {
    font-size: 12px;
    color: var(--text-3);
  }
  .live {
    position: relative;
  }
  .caret {
    display: inline-block;
    width: 7px;
    height: 15px;
    background: var(--ember);
    vertical-align: text-bottom;
    animation: blink 1s steps(2) infinite;
  }
  .thinking {
    display: flex;
    gap: 5px;
    padding: 6px 2px;
  }
  .thinking span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--sky);
    animation: bob 1s ease-in-out infinite;
  }
  .thinking span:nth-child(2) {
    animation-delay: 0.15s;
  }
  .thinking span:nth-child(3) {
    animation-delay: 0.3s;
  }
  @keyframes blink {
    50% {
      opacity: 0;
    }
  }
  @keyframes bob {
    50% {
      transform: translateY(-4px);
      opacity: 0.5;
    }
  }
</style>

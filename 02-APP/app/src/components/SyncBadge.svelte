<!-- Where this device stands with the record: fresh, sending, or waiting for a signal. -->
<script lang="ts">
  import { RefreshCw } from '@lucide/svelte';
  import { app } from '../lib/app.svelte';
  import { ago, plural } from '../lib/text';

  let { compact = false }: { compact?: boolean } = $props();

  const s = $derived(app.sync);
  const phone = $derived(app.platform?.kind === 'phone');
  const tone = $derived(s.busy ? 'busy' : !s.online ? 'off' : s.error ? 'warn' : s.waiting ? 'wait' : 'ok');
  const text = $derived.by(() => {
    if (s.busy) return phone ? 'Syncing…' : 'Syncing with GitHub…';
    if (!s.online) return s.waiting ? `Offline · ${plural(s.waiting, 'answer')} to send` : 'Offline · reading your copy';
    if (s.error) return s.error;
    if (s.waiting) return phone ? `${plural(s.waiting, 'answer')} to send` : `${plural(s.waiting, 'commit')} to push`;
    return s.asOf ? `Up to date · ${ago(s.asOf)}` : 'Up to date';
  });
  let tick = $state(0);
  $effect(() => {
    const t = setInterval(() => tick++, 30_000);
    return () => clearInterval(t);
  });
</script>

<button
  class="sync {tone}"
  class:compact
  onclick={() => app.refresh(true)}
  disabled={s.busy}
  title="{text} — sync now"
  aria-label="{text}. Sync now"
>
  <span class="dot"></span>
  {#if !compact}{#key tick}<span class="text">{text}</span>{/key}{/if}
  <span class="spin" class:on={s.busy}><RefreshCw size={14} /></span>
</button>

<style>
  .sync {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    height: 32px;
    padding: 0 10px;
    border-radius: 999px;
    border: 1px solid var(--line-soft);
    background: transparent;
    color: var(--text-3);
    font-size: 12.5px;
    max-width: 280px;
  }
  .sync:hover:not(:disabled) {
    background: var(--surface-2);
    color: var(--text-2);
  }
  .text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex: none;
    background: var(--sky);
    box-shadow: 0 0 0 3px color-mix(in oklab, var(--sky) 18%, transparent);
  }
  .off .dot {
    background: var(--text-4);
    box-shadow: none;
  }
  .wait .dot,
  .warn .dot {
    background: var(--ember);
    box-shadow: 0 0 0 3px var(--accent-soft);
  }
  .warn {
    color: var(--accent-2);
  }
  .busy .dot {
    animation: pulse 1s ease-in-out infinite alternate;
  }
  .spin {
    display: inline-flex;
    opacity: 0.6;
  }
  .spin.on {
    animation: spin 1s linear infinite;
  }
  .compact {
    padding: 0 8px;
  }
  @keyframes pulse {
    to {
      opacity: 0.3;
    }
  }
</style>

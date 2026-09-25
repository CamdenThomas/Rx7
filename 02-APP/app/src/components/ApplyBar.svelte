<!--
  The Apply button at the top of every page with answers (D-406 7.6, 8.4). His answers wait
  until he presses it; then Claude applies them through the record (CLAUDE.md §6.2). With
  auto-apply on (D-413) the desktop presses it for him once he has been quiet a while. From
  the phone the press is saved as a request, and the desktop runs it when it next syncs.
-->
<script lang="ts">
  import { Play, LoaderCircle } from '@lucide/svelte';
  import { app } from '../lib/app.svelte';
  import { runs } from '../lib/claude.svelte';
  import { href } from '../lib/router.svelte';
  import { plural } from '../lib/text';

  let { area, kinds, noun }: { area: string; kinds: string[]; noun: string } = $props();

  const waiting = $derived((app.snapshot?.inbox ?? []).filter((a) => a.area === area && kinds.includes(a.kind)));
  const requested = $derived((app.snapshot?.inbox ?? []).some((a) => a.area === area && a.kind === 'run' && a.target === 'apply'));
  const running = $derived(runs.busy && runs.current?.record.area === area);
  let confirming = $state(false);

  async function apply() {
    if (app.platform?.canClaude) {
      if (waiting.length >= 4 && !confirming) {
        confirming = true;
        return;
      }
      confirming = false;
      runs.start('apply', area, `He pressed Apply on the ${noun} page: ${plural(waiting.length, 'answer')} of his wait in the inbox.`);
    } else {
      await app.save({ area, target: 'apply', kind: 'run', choice: 'apply', text: '', context: '' });
    }
  }
</script>

<div class="apply" class:hot={waiting.length > 0}>
  <p>
    {#if running}
      <LoaderCircle size={16} class="spinning" /> Claude is applying your answers.
      <a href={href({ name: 'run', area })}>Watch it</a>
    {:else if waiting.length}
      <strong>{plural(waiting.length, 'answer')}</strong> saved, waiting to be applied.
      {#if app.autoApply}<span class="faint">Claude starts on its own a minute and a half after your last one.</span>{/if}
      {#if confirming}<span class="warn">That is a longer run — a few minutes. Apply now?</span>{/if}
    {:else if requested}
      Apply is requested. The desktop runs it the next time it syncs.
    {:else}
      {app.autoApply ? 'Answers you save are applied on their own.' : 'Answers you save wait here until you apply them.'}
    {/if}
  </p>
  {#if confirming}
    <button class="btn small ghost" onclick={() => (confirming = false)}>Not now</button>
  {/if}
  <button class="btn primary" disabled={!waiting.length || running || (requested && !app.platform?.canClaude)} onclick={apply}>
    <Play size={15} /> {app.platform?.canClaude ? 'Apply' : 'Request Apply'}
  </button>
</div>

<style>
  .apply {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 10px 10px 16px;
    margin-bottom: 18px;
    border-radius: var(--r-3);
    background: var(--surface);
    border: 1px solid var(--line-soft);
    font-size: 14px;
    color: var(--text-2);
  }
  .apply.hot {
    border-color: var(--accent-line);
    background: linear-gradient(90deg, var(--accent-soft), var(--surface) 60%);
  }
  p {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }
  strong {
    color: var(--foam);
  }
  .warn {
    color: var(--accent-2);
  }
  :global(.spinning) {
    animation: spin 1s linear infinite;
  }
</style>

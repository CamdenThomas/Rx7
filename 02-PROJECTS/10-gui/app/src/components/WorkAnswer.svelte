<!--
  How he answers one of his own work rows, case by case (D-406 8.2): a check for a step
  done, a value with its unit for a measurement, or one choice from a list.
-->
<script lang="ts">
  import { Check, Undo2 } from '@lucide/svelte';
  import { app } from '../lib/app.svelte';
  import { drafts } from '../lib/drafts.svelte';
  import type { WorkRow } from '../lib/model';

  let { row, big = false, words = '' }: { row: WorkRow; big?: boolean; words?: string } = $props();

  const answer = $derived(app.answer(row.area, row.id));
  const draft = $derived(drafts.get(row.area, row.id));
  let saving = $state(false);

  async function save(choice: string) {
    if (saving || !choice.trim()) return;
    saving = true;
    const out = await app.save({ area: row.area, target: row.id, kind: 'work', choice: choice.trim(), text: words, context: '' });
    if (out) drafts.clear(row.area, row.id);
    saving = false;
  }

  const shown = $derived(
    !answer ? '' : answer.choice === 'done' ? 'Done' : answer.choice === 'not done' ? 'Not done' : `${answer.choice}${row.reply === 'value' && row.unit ? ` ${row.unit}` : ''}`,
  );
</script>

{#if row.owner === 'camden' && row.status !== 'done' && row.status !== 'dropped'}
  <div class="wa" class:big role="group" aria-label="Your answer for {row.id}">
    {#if answer}
      <span class="staged" title="Waits for Apply"><Check size={14} /> {shown}{answer.pending ? ' · on this phone' : ''}</span>
      <button class="btn small ghost icon" onclick={() => app.withdraw(answer)} aria-label="Withdraw" title="Withdraw"><Undo2 size={14} /></button>
    {:else if row.reply === 'value'}
      <input
        class="input val"
        inputmode="decimal"
        value={draft.choice}
        oninput={(e) => drafts.set(row.area, row.id, { choice: (e.target as HTMLInputElement).value })}
        onkeydown={(e) => e.key === 'Enter' && save(draft.choice)}
        placeholder="Value"
        aria-label="Measured value"
      />
      {#if row.unit}<span class="unit">{row.unit}</span>{/if}
      <button class="btn small cool" disabled={!draft.choice.trim() || saving} onclick={() => save(draft.choice)}>Save</button>
    {:else if row.reply === 'choice'}
      <select class="select sel" value={draft.choice} onchange={(e) => drafts.set(row.area, row.id, { choice: (e.target as HTMLSelectElement).value })} aria-label="Choose">
        <option value="">Choose…</option>
        {#each row.choices as c (c)}<option value={c}>{c}</option>{/each}
      </select>
      <button class="btn small cool" disabled={!draft.choice || saving} onclick={() => save(draft.choice)}>Save</button>
    {:else}
      <button class="btn small done" disabled={saving} onclick={() => save('done')}><Check size={14} /> Done</button>
    {/if}
  </div>
{/if}

<style>
  .wa {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    flex: none;
  }
  .staged {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    height: 28px;
    padding: 0 10px;
    border-radius: 999px;
    background: var(--cool-soft);
    color: var(--sky);
    font-size: 12.5px;
    font-weight: 600;
    border: 1px solid color-mix(in oklab, var(--sky) 30%, var(--ink));
  }
  .val {
    width: 96px;
    padding: 5px 9px;
    font-family: var(--mono);
    font-size: 13px;
  }
  .unit {
    color: var(--text-3);
    font-size: 12.5px;
  }
  .sel {
    width: auto;
    min-width: 140px;
    padding: 5px 30px 5px 9px;
    font-size: 13px;
  }
  .done:hover:not(:disabled) {
    border-color: var(--sky);
    color: var(--sky);
  }
  .big .val {
    width: 140px;
    padding: 9px 12px;
    font-size: 15px;
  }
  .big :global(.btn.small) {
    min-height: 40px;
    padding: 0 16px;
    font-size: 14px;
  }
  .big .sel {
    padding: 9px 34px 9px 12px;
    font-size: 15px;
  }
</style>

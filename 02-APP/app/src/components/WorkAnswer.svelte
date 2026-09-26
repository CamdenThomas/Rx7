<!--
  How he answers one of his own work rows, case by case (D-406 8.2): a check for a step
  done, a value with its unit for a measurement, or one choice from a list. Up to four
  choices are buttons that save on the tap; longer lists keep the select (plan P31). The
  last choice he made in this project is offered again as "same as last".
-->
<script lang="ts">
  import { Check, Undo2, Repeat } from '@lucide/svelte';
  import { app } from '../lib/app.svelte';
  import { drafts } from '../lib/drafts.svelte';
  import type { WorkRow } from '../lib/model';
  import { toast } from '../lib/toast.svelte';

  let { row, big = false, words = '', onSaved }: { row: WorkRow; big?: boolean; words?: string; onSaved?: () => void } = $props();

  const answer = $derived(app.answer(row.area, row.id));
  const draft = $derived(drafts.get(row.area, row.id));
  let saving = $state(false);

  /** His last choice per project, so a run of the same answer is one tap each. */
  const lastChoice = $state<Record<string, string>>({});

  async function save(choice: string) {
    if (saving || !choice.trim()) return;
    saving = true;
    // The words typed on the focus page ride along even when he answers from the list (R3).
    const text = words || draft.text;
    const out = await app.save({ area: row.area, target: row.id, kind: 'work', choice: choice.trim(), text, context: '' });
    if (out) {
      drafts.clear(row.area, row.id);
      if (row.reply === 'choice') lastChoice[row.area] = choice.trim();
      onSaved?.();
    }
    saving = false;
  }

  const shown = $derived(
    !answer ? '' : answer.choice === 'done' ? 'Done' : answer.choice === 'not done' ? 'Not done' : `${answer.choice}${row.reply === 'value' && row.unit ? ` ${row.unit}` : ''}`,
  );
  const same = $derived(row.reply === 'choice' && row.choices.length > 4 ? lastChoice[row.area] : '');

  async function withdraw() {
    if (!answer) return;
    // His words come back into the draft before the answer goes, so a mis-tap loses nothing.
    drafts.set(row.area, row.id, { choice: answer.choice, text: answer.text });
    await app.withdraw(answer);
    toast('Withdrawn. Your words are back in the box.', 'info');
  }
</script>

{#if row.owner === 'camden' && row.status !== 'done' && row.status !== 'dropped'}
  <div class="wa" class:big role="group" aria-label="Your answer for {row.id}">
    {#if answer}
      <span class="staged" title="Waits for Apply"><Check size={14} /> {shown}{answer.pending ? ' · on this phone' : ''}</span>
      <button class="btn small ghost icon" onclick={withdraw} aria-label="Withdraw" title="Withdraw"><Undo2 size={14} /></button>
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
    {:else if row.reply === 'choice' && row.choices.length <= 4}
      <div class="choices" role="group" aria-label="Choose one">
        {#each row.choices as c (c)}
          <button class="btn small choice" class:last={lastChoice[row.area] === c} disabled={saving} onclick={() => save(c)}>{c}</button>
        {/each}
      </div>
    {:else if row.reply === 'choice'}
      <select class="select sel" value={draft.choice} onchange={(e) => drafts.set(row.area, row.id, { choice: (e.target as HTMLSelectElement).value })} aria-label="Choose">
        <option value="">Choose…</option>
        {#each row.choices as c (c)}<option value={c}>{c}</option>{/each}
      </select>
      <button class="btn small cool" disabled={!draft.choice || saving} onclick={() => save(draft.choice)}>Save</button>
      {#if same && row.choices.includes(same)}<button class="btn small ghost" disabled={saving} onclick={() => save(same)} title="Same as your last answer here"><Repeat size={13} /> {same}</button>{/if}
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
    flex-wrap: wrap;
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
  .choices {
    display: inline-flex;
    gap: 4px;
    flex-wrap: wrap;
  }
  .choice.last {
    border-color: var(--sky);
  }
  .done:hover:not(:disabled),
  .choice:hover:not(:disabled) {
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
  @media (max-width: 759px) {
    .wa :global(.btn.small),
    .wa .sel,
    .wa .val {
      min-height: var(--tap);
    }
    .wa :global(.btn.small.icon) {
      min-width: var(--tap);
    }
  }
</style>

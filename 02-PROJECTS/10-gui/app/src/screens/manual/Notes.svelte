<!--
  Notes (D-426): his notes on the Manual, newest first, each with the words he selected and a
  link back to where he saw them. They are a log while the Manual is being dialled in: no run
  applies them, and each stays until he deletes it.
-->
<script lang="ts">
  import { Trash2 } from '@lucide/svelte';
  import { app } from '../../lib/app.svelte';
  import { day, readWhere } from '../../lib/manual';

  const notes = $derived(
    (app.snapshot?.inbox ?? [])
      .filter((a) => a.area === '00-CAR' && a.kind === 'note')
      .sort((a, b) => b.at.localeCompare(a.at))
      .map((a) => ({ a, w: readWhere(a.context) })),
  );

  let confirming = $state('');
</script>

<p class="lead muted">
  Select any words in the Manual and press <strong>Note</strong>. Each note is kept here with where you saw it, until you
  delete it. Nothing in the Manual is changed from a note.
</p>

{#if !notes.length}
  <p class="muted">No notes yet.</p>
{:else}
  <ol class="notes">
    {#each notes as { a, w } (a.id)}
      <li class="panel note">
        {#if w.selected}<blockquote>{w.selected}</blockquote>{/if}
        <p class="words">{a.text}</p>
        <footer>
          <span class="faint small">
            {#if w.where}<a href={w.where}>{w.page || w.where}</a> ·{/if}
            {day(a.at.slice(0, 10))} · {a.device}{a.pending ? ' · not sent yet' : ''}
          </span>
          {#if confirming === a.id}
            <span class="acts">
              <button class="btn small ghost" onclick={() => (confirming = '')}>Keep</button>
              <button class="btn small" onclick={() => app.withdraw(a)}>Delete</button>
            </span>
          {:else}
            <button class="btn icon ghost small" onclick={() => (confirming = a.id)} aria-label="Delete note" title="Delete note"><Trash2 size={14} /></button>
          {/if}
        </footer>
      </li>
    {/each}
  </ol>
{/if}

<style>
  .lead {
    max-width: 70ch;
    font-size: 14px;
    margin: 0 0 16px;
  }
  .notes {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .note {
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  blockquote {
    margin: 0;
    padding: 4px 10px;
    border-left: 3px solid var(--sky);
    color: var(--text-3);
    font-size: 13.5px;
  }
  .words {
    margin: 0;
    white-space: pre-wrap;
    font-size: 14.5px;
    line-height: 1.5;
  }
  footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
  }
  .acts {
    display: flex;
    gap: 6px;
  }
  .small {
    font-size: 12.5px;
  }
</style>

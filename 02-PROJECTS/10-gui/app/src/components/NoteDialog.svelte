<!--
  A note on words he selected in the Manual (D-426): what he thinks is wrong, missing or worth
  checking, kept with where he saw it. Saved into 00-CAR's inbox as kind=note - a log, never
  applied - and listed on the Manual's Notes page until he deletes it.
-->
<script lang="ts">
  import { X } from '@lucide/svelte';
  import { app } from '../lib/app.svelte';
  import { noteContext, stamp, type Where } from '../lib/manual';

  let { at, onclose }: { at: Where; onclose: () => void } = $props();

  let text = $state('');
  let saving = $state(false);

  async function save() {
    if (!text.trim() || saving) return;
    saving = true;
    const out = await app.save({ area: '00-CAR', target: `note-${stamp()}`, kind: 'note', choice: '', text, context: noteContext(at) });
    saving = false;
    if (out) onclose();
  }

  function keydown(e: KeyboardEvent) {
    if (e.key === 'Escape') onclose();
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) save();
  }
</script>

<svelte:window onkeydown={keydown} />

<div class="scrim" onclick={onclose} role="presentation"></div>
<div class="sheet card" role="dialog" aria-modal="true" aria-label="Add a note">
  <form onsubmit={(e) => (e.preventDefault(), save())}>
    <header>
      <h2>Add a note</h2>
      <button type="button" class="btn icon ghost small" onclick={onclose} aria-label="Close"><X size={16} /></button>
    </header>
    <blockquote>{at.selected}</blockquote>
    <p class="faint small">{at.page}</p>
    <label class="field">
      <span class="label">Your note</span>
      <!-- svelte-ignore a11y_autofocus -->
      <textarea class="textarea" rows="4" autofocus bind:value={text} placeholder="Wrong, missing, or worth checking…"></textarea>
    </label>
    <p class="faint small">Kept in the Manual's Notes with where you saw it. Nothing is changed from it.</p>
    <footer>
      <button type="button" class="btn ghost" onclick={onclose}>Cancel</button>
      <button type="submit" class="btn primary" disabled={!text.trim() || saving}>{saving ? 'Saving…' : 'Save note'}</button>
    </footer>
  </form>
</div>

<style>
  .scrim {
    position: fixed;
    inset: 0;
    z-index: 50;
    background: rgb(10 14 20 / 0.55);
    backdrop-filter: blur(3px);
    animation: fade var(--t) both;
  }
  .sheet {
    position: fixed;
    z-index: 51;
    top: 12vh;
    left: 0;
    right: 0;
    margin-inline: auto;
    width: min(500px, calc(100vw - 32px));
    max-height: 80vh;
    overflow-y: auto;
    padding: 18px 20px 16px;
    box-shadow: var(--shadow-3);
    animation: rise var(--t) var(--ease) both;
  }
  form {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  h2 {
    font-size: 18px;
    margin: 0;
  }
  blockquote {
    margin: 0;
    padding: 8px 12px;
    border-left: 3px solid var(--sky);
    background: var(--surface-2);
    border-radius: 0 var(--r-1) var(--r-1) 0;
    color: var(--text-2);
    font-size: 14px;
    max-height: 120px;
    overflow-y: auto;
  }
  .small {
    font-size: 12.5px;
    margin: 0;
  }
  .field {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
</style>

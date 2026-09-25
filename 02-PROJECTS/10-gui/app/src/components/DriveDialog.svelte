<!--
  Log drive and Set odo (D-417, his 5.2). Both are answers into 00-CAR's inbox, kind=drive: the
  odometer is the choice and his words the text. Set odo is a drive with only the reading, so a
  drive he forgot to log still shows as miles nobody accounted for. The agent files each one as
  a `drives` row; nothing here writes the record.
-->
<script lang="ts">
  import { X } from '@lucide/svelte';
  import { app } from '../lib/app.svelte';
  import { miles } from '../lib/manual';

  let { mode, onclose }: { mode: 'drive' | 'odo'; onclose: () => void } = $props();

  const last = $derived(app.snapshot?.manual?.odometer);
  let reading = $state('');
  let from = $state('');
  let to = $state('');
  let note = $state('');
  let saving = $state(false);

  const n = $derived(/^\d{1,7}$/.test(reading.trim()) ? Number(reading.trim()) : null);
  const lower = $derived(n !== null && last?.miles != null && n < last.miles);
  const since = $derived(n !== null && last?.miles != null && n >= last.miles ? n - last.miles : null);

  function stamp(d = new Date()) {
    const p = (x: number) => String(x).padStart(2, '0');
    return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}T${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
  }

  async function save() {
    if (n === null || n < 1 || saving) return;
    saving = true;
    const lines = mode === 'drive' ? [from.trim() && `From: ${from.trim()}`, to.trim() && `To: ${to.trim()}`, note.trim()] : [note.trim()];
    const out = await app.save({
      area: '00-CAR',
      target: `${mode}-${stamp()}`,
      kind: 'drive',
      choice: String(n),
      text: lines.filter(Boolean).join('\n'),
      context: '',
    });
    saving = false;
    if (out) onclose();
  }

  function keydown(e: KeyboardEvent) {
    if (e.key === 'Escape') onclose();
  }
</script>

<svelte:window onkeydown={keydown} />

<div class="scrim" onclick={onclose} role="presentation"></div>
<div class="sheet card" role="dialog" aria-modal="true" aria-label={mode === 'drive' ? 'Log drive' : 'Set odo'}>
<form onsubmit={(e) => (e.preventDefault(), save())}>
  <header>
    <h2>{mode === 'drive' ? 'Log a drive' : 'Set the odometer'}</h2>
    <button type="button" class="btn icon ghost small" onclick={onclose} aria-label="Close"><X size={16} /></button>
  </header>
  <p class="muted lead">
    {#if mode === 'drive'}
      The odometer at the end of the drive, and anything worth keeping about it.
    {:else}
      Only the reading. Any miles since the last one are kept as a drive nobody logged.
    {/if}
  </p>

  <label class="field">
    <span class="label">Odometer, miles</span>
    <!-- svelte-ignore a11y_autofocus -->
    <input class="input num big" inputmode="numeric" pattern="[0-9]*" autofocus bind:value={reading} placeholder={last?.miles != null ? String(last.miles) : ''} />
  </label>
  <p class="hint" class:warn={lower}>
    {#if lower}
      Lower than the last reading ({miles(last?.miles)}). It will be saved and checked, not written over.
    {:else if since !== null}
      {miles(since)} since the last reading.
    {:else if last?.miles != null}
      Last reading {miles(last.miles)}.
    {/if}
  </p>

  {#if mode === 'drive'}
    <div class="pair">
      <label class="field"><span class="label">From</span><input class="input" bind:value={from} /></label>
      <label class="field"><span class="label">To</span><input class="input" bind:value={to} /></label>
    </div>
  {/if}
  <label class="field">
    <span class="label">Note</span>
    <textarea class="textarea" rows="3" bind:value={note} placeholder={mode === 'drive' ? 'How it ran, anything found' : ''}></textarea>
  </label>

  <footer>
    <button type="button" class="btn ghost" onclick={onclose}>Cancel</button>
    <button type="submit" class="btn primary" disabled={n === null || n < 1 || saving}>{saving ? 'Saving…' : 'Save'}</button>
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
    width: min(460px, calc(100vw - 32px));
    max-height: 80vh;
    overflow-y: auto;
    padding: 18px 20px 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    box-shadow: var(--shadow-3);
    animation: rise var(--t) var(--ease) both;
  }
  form {
    display: contents;
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
  .lead {
    margin: -4px 0 2px;
    font-size: 14px;
  }
  .field {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .input.big {
    font-size: 22px;
    font-weight: 600;
    letter-spacing: 0.01em;
  }
  .hint {
    margin: -6px 0 0;
    min-height: 1.2em;
    font-size: 13px;
    color: var(--text-3);
  }
  .hint.warn {
    color: var(--accent-2);
  }
  .pair {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .textarea {
    min-height: 72px;
  }
  footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 4px;
  }
</style>

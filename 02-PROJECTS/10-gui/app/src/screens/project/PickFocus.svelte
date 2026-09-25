<!--
  One product suggestion (D-406 8.1): what the part has to be, what this one is, why, its
  drawbacks and what to confirm, where to buy it, and the runner-up if he says no. He answers
  yes, no with a reason (it steers the next search), or a question.
-->
<script lang="ts">
  import { Check, ExternalLink, HelpCircle, Pencil, ThumbsDown, ThumbsUp, Undo2, SkipForward, Columns2 } from '@lucide/svelte';
  import FocusNav from '../../components/FocusNav.svelte';
  import Prose from '../../components/Prose.svelte';
  import { app } from '../../lib/app.svelte';
  import { drafts } from '../../lib/drafts.svelte';
  import type { Pick } from '../../lib/model';
  import { href } from '../../lib/router.svelte';
  import { ago, money } from '../../lib/text';
  import { ui } from '../../lib/ui.svelte';

  let { pick, ids }: { pick: Pick; ids: string[] } = $props();

  const area = $derived(pick.area);
  const answer = $derived(app.answer(area, pick.id));
  const draft = $derived(drafts.get(area, pick.id));
  const runnerUp = $derived((app.snapshot?.picks ?? []).find((p) => p.area === area && p.part === pick.part && p.verdict === 'reserve'));
  const nextOpen = $derived.by(() => {
    const i = ids.indexOf(pick.id);
    for (let k = 1; k < ids.length; k++) {
      const id = ids[(i + k) % ids.length];
      if (!app.answer(area, id)) return id;
    }
    return null;
  });

  let editing = $state(false);
  let saving = $state(false);
  let compare = $state(false);
  const open = $derived(!answer || editing);
  const needsWords = $derived(draft.choice === 'no' || draft.choice === 'question');

  $effect(() => {
    ui.context = `pick ${pick.id} (${pick.product}) for ${pick.part} ${pick.part_item}`;
    return () => (ui.context = '');
  });

  const CHOICES = [
    { id: 'yes', label: 'Yes, buy it', icon: ThumbsUp },
    { id: 'no', label: 'No', icon: ThumbsDown },
    { id: 'question', label: 'Question', icon: HelpCircle },
  ];

  async function save() {
    if (saving || !draft.choice || (needsWords && !draft.text.trim())) return;
    saving = true;
    const out = await app.save({ area, target: pick.id, kind: 'pick', choice: draft.choice, text: draft.text, context: '' });
    if (out) {
      drafts.clear(area, pick.id);
      editing = false;
    }
    saving = false;
  }

  function change() {
    if (answer && !drafts.has(area, pick.id)) drafts.set(area, pick.id, { choice: answer.choice, text: answer.text });
    editing = true;
  }

  const sections = $derived(
    [
      ['It has to be', pick.part_spec],
      ['What meets it', pick.meets],
      ['Why this one', pick.why],
      ['Drawbacks', pick.drawbacks],
    ].filter(([, t]) => t) as [string, string][],
  );
</script>

<FocusNav {ids} at={pick.id} open={(id) => ({ name: 'picks', area, id })} list={{ name: 'picks', area }} unanswered={(id) => !app.answer(area, id)} />

<article class="focus">
  <div class="main">
    <p class="label"><span class="id">{pick.part}</span> · {pick.part_item}</p>
    <h2>{pick.product}</h2>
    <div class="facts">
      <span class="price num">{money(pick.usd, pick.qty)}</span>
      {#if pick.maker_pn}<span class="mono faint">{pick.maker_pn}</span>{/if}
      {#if pick.confidence}<span class="chip {pick.confidence === 'high' ? 'cool' : pick.confidence === 'low' ? 'accent' : ''}">{pick.confidence} confidence</span>{/if}
      <span class="faint">round {pick.round}</span>
    </div>
    {#if pick.url}
      <button class="btn cool buy" onclick={() => app.platform?.open(pick.url)}>
        <ExternalLink size={15} /> {pick.vendor ? `Open at ${pick.vendor}` : 'Open the listing'}
      </button>
    {/if}

    {#each sections as [title, text] (title)}
      <section>
        <h3 class="label">{title}</h3>
        <Prose {text} compact />
      </section>
    {/each}
    {#if pick.confirm}
      <section class="confirm">
        <h3 class="label">Confirm before buying</h3>
        <Prose text={pick.confirm} compact />
      </section>
    {/if}
    <section>
      <h3 class="label">Recommendation</h3>
      <p>{pick.recommend || 'Yes, unless the drawbacks outweigh it for you.'}</p>
    </section>
  </div>

  <aside class="side">
    <div class="answer card">
      {#if !open && answer}
        <div class="saved-top"><Check size={18} /><strong>{answer.choice === 'yes' ? 'Yes' : answer.choice === 'no' ? 'No' : 'Question'}</strong>
          <span class="faint">{answer.pending ? 'on this phone' : `saved ${ago(answer.at)}`} · waits for Apply</span></div>
        {#if answer.text}<p class="his">{answer.text}</p>{/if}
        <div class="row-actions">
          <button class="btn small" onclick={change}><Pencil size={14} /> Change</button>
          <button class="btn small ghost" onclick={() => app.withdraw(answer)}><Undo2 size={14} /> Withdraw</button>
        </div>
        {#if nextOpen}<a class="btn primary" href={href({ name: 'picks', area, id: nextOpen })}>Next unanswered <SkipForward size={15} /></a>{/if}
      {:else}
        <h3 class="label">Your verdict</h3>
        <div class="seg" role="radiogroup" aria-label="Your verdict">
          {#each CHOICES as c (c.id)}
            <button class="segbtn {c.id}" class:on={draft.choice === c.id} role="radio" aria-checked={draft.choice === c.id}
              onclick={() => drafts.set(area, pick.id, { choice: draft.choice === c.id ? '' : c.id })}>
              <c.icon size={16} /> {c.label}
            </button>
          {/each}
        </div>
        <textarea class="textarea" rows="4" value={draft.text} oninput={(e) => drafts.set(area, pick.id, { text: (e.target as HTMLTextAreaElement).value })}
          placeholder={draft.choice === 'no' ? 'Why not? Your reason steers the next search.' : draft.choice === 'question' ? 'What do you want to know?' : 'Anything to add (optional).'}></textarea>
        <button class="btn primary big" onclick={save} disabled={saving || !draft.choice || (needsWords && !draft.text.trim())}>
          <Check size={16} /> {saving ? 'Saving…' : 'Save'}
        </button>
        {#if editing}<button class="btn ghost" onclick={() => (editing = false)}>Cancel</button>{/if}
      {/if}
    </div>

    {#if runnerUp}
      <div class="runner card">
        <div class="runner-head">
          <span class="label">If you say no</span>
          <button class="btn small ghost" onclick={() => (compare = !compare)}><Columns2 size={14} /> {compare ? 'Hide' : 'Compare'}</button>
        </div>
        <h4>{runnerUp.product}</h4>
        <p class="faint num">{money(runnerUp.usd, runnerUp.qty)}{runnerUp.vendor ? ` · ${runnerUp.vendor}` : ''}</p>
        <Prose text={runnerUp.why} compact />
        {#if compare}
          <div class="cmp">
            {#each [['What meets it', pick.meets, runnerUp.meets], ['Drawbacks', pick.drawbacks, runnerUp.drawbacks], ['Confidence', pick.confidence, runnerUp.confidence]] as [label, a, b] (label)}
              <div class="cmp-row"><span class="label">{label}</span><div class="pair"><p>{a || '—'}</p><p>{b || '—'}</p></div></div>
            {/each}
          </div>
        {/if}
        {#if runnerUp.url}<button class="btn small" onclick={() => app.platform?.open(runnerUp.url)}><ExternalLink size={14} /> Listing</button>{/if}
      </div>
    {/if}
  </aside>
</article>

<style>
  .focus {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(300px, 380px);
    gap: 32px;
    align-items: start;
    padding-bottom: 40px;
  }
  .main {
    display: flex;
    flex-direction: column;
    gap: 18px;
  }
  h2 {
    font-size: clamp(22px, 2.4vw, 28px);
    margin-top: -8px;
  }
  .facts {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px 14px;
    margin-top: -6px;
  }
  .price {
    font-size: 22px;
    font-weight: 700;
    color: var(--foam);
  }
  .buy {
    align-self: flex-start;
  }
  .label {
    display: block;
    margin-bottom: 6px;
  }
  .confirm {
    padding: 12px 14px;
    border-radius: var(--r-2);
    border: 1px dashed var(--accent-line);
    background: var(--accent-soft);
  }
  .side {
    position: sticky;
    top: 110px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .answer {
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .seg {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 6px;
  }
  .segbtn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 12px 6px;
    border-radius: var(--r-2);
    border: 1px solid var(--line);
    background: var(--bg-raise);
    color: var(--text-2);
    font-size: 13px;
    font-weight: 580;
    min-height: 64px;
  }
  .segbtn:hover {
    border-color: var(--sky);
    color: var(--text);
  }
  .segbtn.on.yes {
    border-color: var(--sky);
    background: var(--cool-soft);
    color: var(--foam);
  }
  .segbtn.on.no {
    border-color: var(--ember);
    background: var(--accent-soft);
    color: var(--foam);
  }
  .segbtn.on.question {
    border-color: var(--steel);
    background: var(--steel-soft);
    color: var(--foam);
  }
  .saved-top {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    color: var(--sky);
  }
  .saved-top strong {
    color: var(--foam);
  }
  .his {
    white-space: pre-wrap;
    padding-left: 12px;
    border-left: 2px solid var(--steel);
  }
  .row-actions {
    display: flex;
    gap: 8px;
  }
  .runner {
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .runner-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .runner h4 {
    font-size: 15px;
  }
  .cmp {
    display: flex;
    flex-direction: column;
    gap: 10px;
    border-top: 1px solid var(--line-soft);
    padding-top: 10px;
    font-size: 13px;
  }
  .pair {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .pair p:first-child {
    color: var(--text);
  }
  .pair p:last-child {
    color: var(--text-2);
  }
  @media (max-width: 980px) {
    .focus {
      grid-template-columns: 1fr;
      padding-bottom: calc(80px + var(--tabbar));
    }
    .side {
      position: static;
    }
  }
</style>

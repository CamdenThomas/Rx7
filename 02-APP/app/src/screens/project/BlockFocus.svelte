<!--
  One block, laid out for reading and answering (D-406 7.2–7.5). He answers with an option,
  with "follow the recommendation" in one tap, in his own words, or both; or skips to the
  next. Explain and Discuss ask Claude, read-only; the discussion's key points travel with
  his answer.
-->
<script lang="ts">
  import { Check, CornerDownRight, MessageSquare, Sparkles, SkipForward, Undo2, Pencil } from '@lucide/svelte';
  import Chat from '../../components/Chat.svelte';
  import Feed from '../../components/Feed.svelte';
  import FocusNav from '../../components/FocusNav.svelte';
  import Prose from '../../components/Prose.svelte';
  import { app } from '../../lib/app.svelte';
  import { blockText, Conversation, explainPrompt, Stream } from '../../lib/claude.svelte';
  import { drafts } from '../../lib/drafts.svelte';
  import type { Block } from '../../lib/model';
  import { href, router } from '../../lib/router.svelte';
  import { ago, plural } from '../../lib/text';
  import { projectLabel, ui } from '../../lib/ui.svelte';
  import { talks, explained } from './conversations';

  let { block, ids }: { block: Block; ids: string[] } = $props();

  const area = $derived(block.area);
  const key = $derived(`${block.area}/${block.id}`);
  const answer = $derived(app.answer(area, block.id));
  const draft = $derived(drafts.get(area, block.id));
  const rec = $derived(block.options.find((o) => o.letter === block.recommended));
  const nextOpen = $derived.by(() => {
    const i = ids.indexOf(block.id);
    for (let k = 1; k < ids.length; k++) {
      const id = ids[(i + k) % ids.length];
      if (!app.answer(area, id)) return id;
    }
    return null;
  });

  let editing = $state(false);
  let saving = $state(false);
  let talk = $derived(talks.get(key));
  let explainer = $derived(explained.get(key));

  $effect(() => {
    ui.context = `block ${block.id} of ${projectLabel(area)}: ${block.title}`;
    return () => (ui.context = '');
  });

  const open = $derived(!answer || editing);

  function pick(letter: string) {
    drafts.set(area, block.id, { choice: draft.choice === letter ? '' : letter });
  }

  function words(e: Event) {
    drafts.set(area, block.id, { text: (e.target as HTMLTextAreaElement).value });
  }

  async function save(choice = draft.choice) {
    if (saving || (!choice && !draft.text.trim())) return;
    saving = true;
    const context = talk?.messages.length ? await talk.keyPoints() : '';
    const out = await app.save({ area, target: block.id, kind: 'block', choice, text: draft.text, context });
    if (out) {
      drafts.clear(area, block.id);
      talks.delete(key);
      talk = undefined;
      editing = false;
    }
    saving = false;
  }

  function change() {
    if (answer && !drafts.has(area, block.id)) drafts.set(area, block.id, { choice: answer.choice, text: answer.text });
    editing = true;
  }

  function explain() {
    if (!explained.has(key)) {
      const c = new Conversation(blockText(block));
      explained.set(key, c);
      void c.ask(explainPrompt(block), true).then((reply) => {
        c.messages = [{ who: 'claude', text: reply || 'Claude could not explain this one — try again in a moment.' }];
      });
    }
    explainer = explained.get(key);
  }

  function discuss() {
    if (!talks.has(key)) talks.set(key, new Conversation(`He opened Discuss on this block, to talk it through before answering.\n\n${blockText(block)}`));
    talk = talks.get(key);
  }

  function keydown(e: KeyboardEvent) {
    const typing = (e.target as HTMLElement)?.closest('input, textarea, select');
    if (typing || e.metaKey || e.altKey || !open) {
      if (typing && e.key === 'Enter' && (e.ctrlKey || e.metaKey)) void save();
      return;
    }
    if (!e.ctrlKey && block.options.some((o) => o.letter === e.key)) pick(e.key);
  }

  const explainText = $derived(explainer?.live ?? null);
  const explanation = $derived(explainer ? (explainer.messages.at(-1)?.text ?? '') : '');
  const liveExplain = $derived(explainer?.live ?? new Stream());
</script>

<svelte:window onkeydown={keydown} />

<FocusNav
  {ids}
  at={block.id}
  open={(id) => ({ name: 'blocks', area, id })}
  list={{ name: 'blocks', area }}
  unanswered={(id) => !app.answer(area, id)}
/>

<article class="focus">
  <header class="title">
    <span class="id">{block.id}</span>
    <h2>{block.title}</h2>
    <span class="faint when">{block.age !== null ? `open ${block.age ? plural(block.age, 'day') : 'since today'}` : ''}</span>
  </header>

  <section class="ask">
    <p>{block.ask}</p>
  </section>

  <section class="why">
    <h3 class="label">Why it matters</h3>
    <Prose text={block.why} compact />
  </section>

  <section class="options">
    <h3 class="label">Options</h3>
    <div class="opts" role="radiogroup" aria-label="Options">
      {#each block.options as o (o.letter)}
        {@const chosen = open ? draft.choice === o.letter : answer?.choice === o.letter}
        <button class="opt" class:chosen class:rec={o.letter === block.recommended} role="radio" aria-checked={chosen} disabled={!open} onclick={() => pick(o.letter)}>
          <span class="letter">{o.letter}</span>
          <span class="otext"><Prose text={o.text} compact /></span>
          {#if o.letter === block.recommended}<span class="chip cool rtag">Recommended</span>{/if}
        </button>
      {/each}
    </div>
  </section>

  <section class="recommend">
    <h3 class="label">Recommendation</h3>
    <Prose text={block.recommend} compact />
  </section>

  <section class="answer">
    {#if !open && answer}
      <div class="saved card">
        <div class="saved-top">
          <Check size={18} />
          <strong>Your answer{answer.choice ? ` — (${answer.choice})` : ''}</strong>
          <span class="faint">{answer.pending ? 'on this phone, sent at the next connection' : `saved ${ago(answer.at)} from the ${answer.device}`} · waits for Apply</span>
        </div>
        {#if answer.text}<p class="his">{answer.text}</p>{/if}
        {#if answer.context}<div class="ctx"><span class="label">From the discussion</span><Prose text={answer.context} compact /></div>{/if}
        <div class="row-actions">
          <button class="btn small" onclick={change}><Pencil size={14} /> Change</button>
          <button class="btn small ghost" onclick={() => app.withdraw(answer)}><Undo2 size={14} /> Withdraw</button>
          {#if nextOpen}
            <a class="btn small primary push" href={href({ name: 'blocks', area, id: nextOpen })}>Next unanswered <SkipForward size={14} /></a>
          {/if}
        </div>
      </div>
    {:else}
      <h3 class="label">Your answer</h3>
      <textarea
        class="textarea"
        value={draft.text}
        oninput={words}
        rows="3"
        placeholder={draft.choice ? `Anything to add to (${draft.choice})? Optional.` : 'Pick an option above, or answer in your own words.'}
      ></textarea>
      <div class="answer-actions">
        {#if rec}
          <button class="btn cool big" onclick={() => save(rec.letter)} disabled={saving}>
            <CornerDownRight size={16} /> Follow the recommendation ({rec.letter})
          </button>
        {/if}
        <button class="btn primary big" onclick={() => save()} disabled={saving || (!draft.choice && !draft.text.trim())}>
          <Check size={16} /> {saving ? 'Saving…' : 'Save answer'}
        </button>
        <span class="spacer"></span>
        {#if editing}
          <button class="btn ghost" onclick={() => (editing = false)}>Cancel</button>
        {:else if nextOpen}
          <button class="btn ghost" onclick={() => router.go({ name: 'blocks', area, id: nextOpen })}><SkipForward size={15} /> Skip</button>
        {/if}
      </div>
      <p class="hint faint">Saved answers wait for Apply. Nothing you type here is lost — it is kept as a draft until you save.</p>
    {/if}
  </section>

  <aside class="context">
    <section class="why-side">
      <h3 class="label">Why it matters</h3>
      <Prose text={block.why} compact />
    </section>
    <section>
      <h3 class="label">What it stops</h3>
      <Prose text={block.stops} compact />
    </section>
    {#if block.unblocks.length}
      <section>
        <h3 class="label">Unblocks · {block.unblocks.length}</h3>
        <ul class="links">
          {#each block.unblocks as u (u.area + u.id)}
            <li><a href={href({ name: 'todo', area: u.area, id: u.id })}><span class="id">{u.id}</span> {u.item}</a></li>
          {/each}
        </ul>
      </section>
    {/if}
    {#if block.touches.length}
      <section>
        <h3 class="label">Decisions it touches</h3>
        <div class="chips">
          {#each block.touches as d (d)}
            <a class="chip" href={href({ name: 'decision', id: d })} title={app.decision(d)?.title}>{d}</a>
          {/each}
        </div>
      </section>
    {/if}

    {#if app.platform?.canClaude}
      <section class="claude">
        <div class="claude-btns">
          <button class="btn" onclick={explain} disabled={explainer?.busy}><Sparkles size={15} /> Explain</button>
          <button class="btn" class:lit={!!talk} onclick={discuss}><MessageSquare size={15} /> Discuss</button>
        </div>
        {#if explainer}
          <div class="explain card">
            <span class="label">In plain words</span>
            {#if explainText}
              <Feed stream={liveExplain} tools={false} />
            {:else}
              <Prose text={explanation} compact />
            {/if}
          </div>
        {/if}
        {#if talk}
          <div class="discuss card">
            <Chat convo={talk} placeholder="Ask about this block…" empty="Ask anything about this block before you answer. When you save, the key points go with your answer." />
          </div>
        {/if}
      </section>
    {:else}
      <p class="faint small">Explain and Discuss ask Claude, which runs on the desktop.</p>
    {/if}
    <p class="faint small">In {projectLabel(area)}</p>
  </aside>
</article>

<style>
  .focus {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(300px, 380px);
    grid-template-areas:
      'title title'
      'ask context'
      'options context'
      'recommend context'
      'answer context';
    column-gap: 32px;
    row-gap: 20px;
    align-items: start;
    padding-bottom: 40px;
  }
  .title {
    grid-area: title;
    display: flex;
    align-items: baseline;
    gap: 12px;
    flex-wrap: wrap;
  }
  .title .id {
    font-size: 14px;
  }
  .title h2 {
    font-size: 22px;
  }
  .when {
    font-size: 13px;
  }
  .ask {
    grid-area: ask;
    font-size: clamp(18px, 1.6vw, 21px);
    line-height: 1.45;
    font-weight: 540;
    color: var(--foam);
    padding: 18px 20px;
    border-radius: var(--r-3);
    background: linear-gradient(135deg, color-mix(in oklab, var(--steel) 45%, var(--surface)), var(--surface));
    border: 1px solid var(--line-soft);
  }
  .why {
    grid-area: why;
    display: none;
  }
  .options {
    grid-area: options;
  }
  .recommend {
    grid-area: recommend;
  }
  .answer {
    grid-area: answer;
  }
  .context {
    grid-area: context;
    position: sticky;
    top: 110px;
    display: flex;
    flex-direction: column;
    gap: 18px;
    max-height: calc(100dvh - 130px);
    overflow-y: auto;
    padding-right: 4px;
  }
  .label {
    margin-bottom: 8px;
    display: block;
  }
  .opts {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .opt {
    display: grid;
    grid-template-columns: 34px 1fr;
    gap: 12px;
    align-items: start;
    text-align: left;
    padding: 14px 16px;
    border-radius: var(--r-3);
    border: 1px solid var(--line);
    background: var(--surface);
    color: var(--text);
    position: relative;
    transition:
      border-color var(--t-fast),
      background var(--t-fast),
      transform var(--t-fast);
    min-height: var(--tap);
  }
  .opt:hover:not(:disabled) {
    border-color: var(--sky);
    background: color-mix(in oklab, var(--surface) 80%, var(--steel));
  }
  .opt:disabled {
    cursor: default;
    opacity: 0.75;
  }
  .opt.chosen {
    border-color: var(--ember);
    background: linear-gradient(135deg, var(--accent-soft), var(--surface) 70%);
    opacity: 1;
  }
  .letter {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-family: var(--mono);
    font-weight: 650;
    font-size: 14px;
    background: var(--surface-2);
    border: 1px solid var(--line);
    color: var(--sky);
  }
  .chosen .letter {
    background: var(--ember);
    border-color: var(--ember);
    color: #1f1714;
  }
  .rtag {
    position: absolute;
    top: -10px;
    right: 14px;
    background: var(--surface-2);
  }
  .answer .textarea {
    font-size: 15px;
  }
  .answer-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    align-items: center;
    margin-top: 12px;
  }
  .spacer {
    flex: 1;
  }
  .hint {
    font-size: 12.5px;
    margin-top: 10px;
  }
  .saved {
    padding: 16px 18px;
    border-color: color-mix(in oklab, var(--sky) 35%, var(--ink));
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .saved-top {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    color: var(--sky);
  }
  .saved-top strong {
    color: var(--foam);
  }
  .saved-top .faint {
    font-size: 13px;
  }
  .his {
    white-space: pre-wrap;
    padding-left: 12px;
    border-left: 2px solid var(--steel);
  }
  .ctx {
    font-size: 13px;
  }
  .row-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .push {
    margin-left: auto;
  }
  .links {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 13.5px;
  }
  .links a {
    color: var(--text-2);
    display: block;
  }
  .links a:hover {
    color: var(--foam);
  }
  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .chips .chip {
    font-family: var(--mono);
  }
  .chips .chip:hover {
    color: var(--foam);
    border-color: var(--sky);
  }
  .claude-btns {
    display: flex;
    gap: 8px;
  }
  .lit {
    border-color: var(--ember) !important;
  }
  .explain {
    margin-top: 12px;
    padding: 14px 16px;
  }
  .discuss {
    margin-top: 12px;
    height: 420px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  .small {
    font-size: 12.5px;
  }

  @media (max-width: 980px) {
    .focus {
      grid-template-columns: 1fr;
      grid-template-areas: 'title' 'ask' 'why' 'options' 'recommend' 'answer' 'context';
      padding-bottom: calc(80px + var(--tabbar));
    }
    .why {
      display: block;
    }
    .why-side {
      display: none;
    }
    .context {
      position: static;
      max-height: none;
      overflow: visible;
    }
    .answer-actions :global(.btn.big) {
      flex: 1 1 100%;
    }
  }
</style>

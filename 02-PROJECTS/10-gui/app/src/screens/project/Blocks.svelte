<!-- A project's open blocks: the list, or one at a time (D-406 7.2–7.6, 8.4). -->
<script lang="ts">
  import { ChevronRight } from '@lucide/svelte';
  import ApplyBar from '../../components/ApplyBar.svelte';
  import BlockFocus from './BlockFocus.svelte';
  import { app } from '../../lib/app.svelte';
  import { drafts } from '../../lib/drafts.svelte';
  import { href } from '../../lib/router.svelte';
  import { plural } from '../../lib/text';

  let { area, id }: { area: string; id?: string } = $props();

  const blocks = $derived(app.blocks(area));
  const current = $derived(id ? blocks.find((b) => b.id === id) : undefined);
</script>

{#if id}
  {#if current}
    {#key current.id}
      <BlockFocus block={current} ids={blocks.map((b) => b.id)} />
    {/key}
  {:else}
    <div class="gone card">
      <p>Block <span class="id">{id}</span> is not open any more — its answer has been applied.</p>
      <a class="btn" href={href({ name: 'blocks', area })}>Back to the blocks</a>
      {#if app.decisions().some((d) => d.closes.includes(id))}
        <a class="btn cool" href={href({ name: 'decision', id: app.decisions().find((d) => d.closes.includes(id))!.id })}>Read the decision it became</a>
      {/if}
    </div>
  {/if}
{:else}
  <ApplyBar {area} kinds={['block']} noun="Blocks" />
  {#if !blocks.length}
    <div class="empty">
      <h3>Nothing open.</h3>
      <p class="muted">No question in this project is waiting on you.</p>
    </div>
  {:else}
    <ul class="list">
      {#each blocks as b, i (b.id)}
        {@const answer = app.answer(area, b.id)}
        <li class="rise" style:animation-delay="{i * 30}ms">
          <a class="row" href={href({ name: 'blocks', area, id: b.id })}>
            <div class="main">
              <div class="top">
                <span class="id">{b.id}</span>
                <h3>{b.title}</h3>
              </div>
              <p class="ask">{b.ask}</p>
              <div class="meta">
                {#if answer}
                  <span class="chip cool">Answered{answer.choice ? ` · (${answer.choice})` : ''}{answer.pending ? ' · on this phone' : ''}</span>
                {:else if drafts.has(area, b.id)}
                  <span class="chip quiet">Draft</span>
                {:else}
                  <span class="chip accent">Waiting for you</span>
                {/if}
                {#if b.age !== null}<span class="faint">open {b.age ? plural(b.age, 'day') : 'since today'}</span>{/if}
                {#if b.unblocks.length}<span class="faint">· unblocks {plural(b.unblocks.length, 'row')}</span>{/if}
              </div>
            </div>
            <ChevronRight size={18} class="go" />
          </a>
        </li>
      {/each}
    </ul>
  {/if}
{/if}

<style>
  .list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .row {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 18px;
    background: var(--surface);
    border: 1px solid var(--line-soft);
    border-radius: var(--r-3);
    color: var(--text);
    transition:
      border-color var(--t-fast),
      background var(--t-fast);
  }
  .row:hover {
    border-color: var(--line);
    background: color-mix(in oklab, var(--surface) 70%, var(--surface-2));
    color: var(--text);
  }
  .main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .top {
    display: flex;
    gap: 10px;
    align-items: baseline;
  }
  h3 {
    font-size: 16px;
    font-weight: 620;
  }
  .ask {
    color: var(--text-2);
    font-size: 14px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .meta {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    font-size: 12.5px;
    margin-top: 2px;
  }
  .row :global(.go) {
    color: var(--text-4);
    flex: none;
  }
  .empty {
    padding: 48px 8px;
    text-align: center;
  }
  .empty h3 {
    font-size: 20px;
    margin-bottom: 6px;
  }
  .gone {
    padding: 22px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    align-items: flex-start;
  }
</style>

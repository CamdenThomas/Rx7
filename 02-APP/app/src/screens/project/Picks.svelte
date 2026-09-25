<!-- The parts Claude suggests for this project: the list, or one at a time (D-406 8.1). -->
<script lang="ts">
  import { ChevronRight } from '@lucide/svelte';
  import ApplyBar from '../../components/ApplyBar.svelte';
  import PickFocus from './PickFocus.svelte';
  import { app } from '../../lib/app.svelte';
  import { href } from '../../lib/router.svelte';
  import { money } from '../../lib/text';

  let { area, id }: { area: string; id?: string } = $props();

  const picks = $derived(app.picks(area));
  const current = $derived(id ? picks.find((p) => p.id === id) : undefined);
  const settled = $derived((app.snapshot?.picks ?? []).filter((p) => p.area === area && ['accepted', 'vetoed'].includes(p.verdict)));
  const VERDICT: Record<string, string> = { yes: 'Yes', no: 'No', question: 'Question' };
</script>

{#if id}
  {#if current}
    {#key current.id}
      <PickFocus pick={current} ids={picks.map((p) => p.id)} />
    {/key}
  {:else}
    <div class="card gone">
      <p>Pick <span class="id">{id}</span> is not waiting for you any more.</p>
      <a class="btn" href={href({ name: 'picks', area })}>Back to the picks</a>
    </div>
  {/if}
{:else}
  <ApplyBar {area} kinds={['pick']} noun="Picks" />
  {#if !picks.length}
    <div class="empty"><h3>No suggestions waiting.</h3><p class="muted">When Claude runs a parts round, each product it suggests shows up here.</p></div>
  {:else}
    <ul class="list">
      {#each picks as p, i (p.id)}
        {@const a = app.answer(area, p.id)}
        <li class="rise" style:animation-delay="{i * 30}ms">
          <a class="row" href={href({ name: 'picks', area, id: p.id })}>
            <span class="price num">{money(p.usd, p.qty)}</span>
            <div class="main">
              <div class="top"><span class="id">{p.id}</span><h3>{p.product}</h3></div>
              <p class="part"><span class="id">{p.part}</span> {p.part_item}</p>
            </div>
            <div class="state">
              {#if a}
                <span class="chip {a.choice === 'yes' ? 'cool' : a.choice === 'no' ? 'accent' : 'solid'}">{VERDICT[a.choice] ?? 'Answered'}</span>
              {:else}
                <span class="chip accent">Waiting</span>
              {/if}
              {#if p.confidence}<span class="faint conf">{p.confidence} confidence</span>{/if}
            </div>
            <ChevronRight size={18} class="go" />
          </a>
        </li>
      {/each}
    </ul>
  {/if}
  {#if settled.length}
    <details class="settled">
      <summary class="label">Already decided · {settled.length}</summary>
      <ul class="list small">
        {#each settled as p (p.id)}
          <li>
            <a class="row" href={href({ name: 'row', area, table: 'picks', key: p.id })}>
              <span class="chip {p.verdict === 'accepted' ? 'cool' : 'accent'}">{p.verdict === 'accepted' ? 'Chosen' : 'Vetoed'}</span>
              <div class="main"><div class="top"><span class="id">{p.part}</span><h3>{p.product}</h3></div>
                {#if p.said}<p class="part">“{p.said}”</p>{/if}</div>
            </a>
          </li>
        {/each}
      </ul>
    </details>
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
    gap: 16px;
    padding: 14px 18px;
    background: var(--surface);
    border: 1px solid var(--line-soft);
    border-radius: var(--r-3);
    color: var(--text);
  }
  .row:hover {
    border-color: var(--line);
    color: var(--text);
  }
  .price {
    min-width: 92px;
    font-weight: 650;
    font-size: 15px;
    color: var(--foam);
  }
  .main {
    flex: 1;
    min-width: 0;
  }
  .top {
    display: flex;
    gap: 10px;
    align-items: baseline;
  }
  h3 {
    font-size: 15.5px;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .part {
    color: var(--text-3);
    font-size: 13px;
    margin-top: 3px;
  }
  .state {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
  }
  .conf {
    font-size: 12px;
  }
  .row :global(.go) {
    color: var(--text-4);
    flex: none;
  }
  .empty {
    padding: 48px 8px;
    text-align: center;
  }
  .settled {
    margin-top: 28px;
  }
  .settled summary {
    cursor: pointer;
    margin-bottom: 12px;
  }
  .small .row {
    padding: 10px 14px;
  }
  .gone {
    padding: 22px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    align-items: flex-start;
  }
  @media (max-width: 759px) {
    .row {
      flex-wrap: wrap;
      gap: 8px 12px;
    }
    .price {
      min-width: 0;
      order: 2;
    }
    .main {
      flex-basis: 100%;
    }
    .state {
      order: 3;
      flex-direction: row;
      margin-left: auto;
    }
    .row :global(.go) {
      display: none;
    }
  }
</style>

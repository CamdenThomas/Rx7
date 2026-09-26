<!--
  Everything that waits for him, across every project, on one page (plan P41): the open
  blocks, the proposed picks and the steps he can start now, newest first within each project,
  each opening its own focus page. Nothing here is stored: it is the same rows the project
  pages show, gathered.
-->
<script lang="ts">
  import { CirclePlay, HelpCircle, ShoppingCart } from '@lucide/svelte';
  import { app } from '../lib/app.svelte';
  import { href } from '../lib/router.svelte';
  import { plural } from '../lib/text';

  const groups = $derived(
    app.areas
      .filter((a) => a.kind === 'project' || a.kind === 'app' || a.kind === 'car')
      .map((a) => ({
        area: a,
        title: app.title(a.name),
        blocks: app.blocks(a.name).filter((b) => !app.answer(a.name, b.id)),
        picks: app.picks(a.name).filter((p) => p.verdict === 'proposed' && !app.answer(a.name, p.id)),
        work: app.myReady(a.name).filter((w) => !app.answer(a.name, w.id)),
      }))
      .filter((g) => g.blocks.length || g.picks.length || g.work.length),
  );
  const total = $derived(groups.reduce((n, g) => n + g.blocks.length + g.picks.length + g.work.length, 0));
</script>

<div class="page narrow">
  <p class="label">Waiting for you</p>
  <h1>{total ? plural(total, 'thing') : 'Nothing'} across {plural(groups.length, 'project')}</h1>
  {#if !total}<p class="muted">Every block is answered, every pick has a verdict, every step you can start is done or saved.</p>{/if}

  {#each groups as g (g.area.name)}
    <section class="card box">
      <h2><a href={href({ name: 'project', area: g.area.name })}>{g.title}</a> <span class="faint">{g.area.prefix}</span></h2>
      <ul>
        {#each g.blocks as b (b.id)}
          <li><HelpCircle size={15} class="ico" /><a href={href({ name: 'blocks', area: g.area.name, id: b.id })}><span class="id">{b.id}</span> {b.title}</a><span class="chip accent">block</span></li>
        {/each}
        {#each g.picks as p (p.id)}
          <li><ShoppingCart size={15} class="ico" /><a href={href({ name: 'picks', area: g.area.name, id: p.id })}><span class="id">{p.id}</span> {p.product}</a><span class="chip cool">pick</span></li>
        {/each}
        {#each g.work.slice(0, 12) as w (w.id)}
          <li><CirclePlay size={15} class="ico" /><a href={href({ name: 'todo', area: g.area.name, id: w.id })}><span class="id">{w.id}</span> {w.item}</a><span class="chip quiet">step</span></li>
        {/each}
        {#if g.work.length > 12}
          <li class="more"><a href={href({ name: 'todo', area: g.area.name })}>and {g.work.length - 12} more steps</a></li>
        {/if}
      </ul>
    </section>
  {/each}
</div>

<style>
  h1 {
    font-size: 28px;
    margin: 6px 0 22px;
  }
  .box {
    padding: 16px 20px;
    margin-bottom: 14px;
  }
  h2 {
    font-size: 16px;
    margin: 0 0 8px;
    display: flex;
    gap: 8px;
    align-items: baseline;
  }
  ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  li {
    display: flex;
    align-items: baseline;
    gap: 10px;
    font-size: 14px;
    line-height: 1.4;
  }
  li a {
    flex: 1;
    color: var(--text);
  }
  li :global(.ico) {
    flex: none;
    color: var(--text-3);
    position: relative;
    top: 2px;
  }
  .more {
    font-size: 13px;
  }
</style>

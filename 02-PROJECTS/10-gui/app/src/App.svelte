<script lang="ts">
  import Shell from './components/Shell.svelte';
  import Toasts from './components/Toasts.svelte';
  import SearchOverlay from './components/SearchOverlay.svelte';
  import ChatPanel from './components/ChatPanel.svelte';
  import Mark from './components/Mark.svelte';
  import Home from './screens/Home.svelte';
  import Manual from './screens/Manual.svelte';
  import Projects from './screens/Projects.svelte';
  import NewProject from './screens/NewProject.svelte';
  import Project from './screens/Project.svelte';
  import DecisionPage from './screens/DecisionPage.svelte';
  import RowPage from './screens/RowPage.svelte';
  import SearchPage from './screens/SearchPage.svelte';
  import Settings from './screens/Settings.svelte';
  import { app } from './lib/app.svelte';
  import { drafts } from './lib/drafts.svelte';
  import { runs } from './lib/claude.svelte';
  import { router } from './lib/router.svelte';
  import { ui } from './lib/ui.svelte';

  let started = false;
  $effect(() => {
    if (started) return;
    started = true;
    void app.start().then(async () => {
      await Promise.all([drafts.load(), runs.load()]);
      runs.startRequested();
    });
  });

  const r = $derived(router.route);
</script>

{#if !app.snapshot}
  <div class="boot">
    <Mark size={56} />
    {#if app.error}
      <p class="err">{app.error}</p>
      <button class="btn" onclick={() => app.start()}>Try again</button>
    {:else}
      <p class="faint">Reading the record…</p>
    {/if}
  </div>
{:else}
  <Shell>
    {#key r.name === 'blocks' || r.name === 'picks' || r.name === 'todo' || r.name === 'decisions' || r.name === 'parts' || r.name === 'run' || r.name === 'project' ? `p:${r.area}` : r.name}
      {#if r.name === 'home'}
        <Home />
      {:else if r.name === 'manual'}
        <Manual />
      {:else if r.name === 'projects'}
        <Projects />
      {:else if r.name === 'new-project'}
        <NewProject />
      {:else if r.name === 'decision'}
        <DecisionPage id={r.id} />
      {:else if r.name === 'row'}
        <RowPage area={r.area} table={r.table} key={r.key} />
      {:else if r.name === 'search'}
        <SearchPage q={r.q} />
      {:else if r.name === 'settings'}
        <Settings />
      {:else}
        <Project route={r} />
      {/if}
    {/key}
  </Shell>
  {#if ui.searchOpen}<SearchOverlay />{/if}
  {#if ui.chatOpen && app.platform?.canClaude}<ChatPanel />{/if}
{/if}
<Toasts />

<style>
  .boot {
    min-height: 100dvh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 18px;
    padding: 24px;
    text-align: center;
  }
  .err {
    max-width: 460px;
    color: var(--accent-2);
  }
</style>

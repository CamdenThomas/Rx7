<!--
  The frame around every screen (D-406 3.3): a menu bar always on screen, breadcrumbs under
  it, and on the phone a tab bar at the bottom where the thumb is.
-->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { ChevronLeft, ChevronRight, FolderKanban, House, BookOpen, MessageSquare, Search, Settings } from '@lucide/svelte';
  import Mark from './Mark.svelte';
  import SyncBadge from './SyncBadge.svelte';
  import { app } from '../lib/app.svelte';
  import { href, router, type Route } from '../lib/router.svelte';
  import { crumbs, ui } from '../lib/ui.svelte';

  let { children }: { children: Snippet } = $props();

  const trail = $derived(crumbs(router.route));
  const section = $derived.by(() => {
    const n = router.route.name;
    if (n === 'home') return 'home';
    if (n === 'manual') return 'manual';
    if (n === 'search') return 'search';
    if (n === 'settings') return 'settings';
    return 'projects';
  });
  const up = $derived(trail.length > 1 ? [...trail].reverse().find((c) => c.route)?.route : undefined);
  const isMac = typeof navigator !== 'undefined' && /Mac/.test(navigator.platform);

  const nav: { id: string; label: string; route: Route; icon: typeof House }[] = [
    { id: 'home', label: 'Home', route: { name: 'home' }, icon: House },
    { id: 'manual', label: 'Manual', route: { name: 'manual' }, icon: BookOpen },
    { id: 'projects', label: 'Projects', route: { name: 'projects' }, icon: FolderKanban },
  ];

  function keydown(e: KeyboardEvent) {
    const typing = (e.target as HTMLElement)?.closest('input, textarea, select, [contenteditable]');
    if ((e.key === 'k' && (e.ctrlKey || e.metaKey)) || (e.key === '/' && !typing)) {
      e.preventDefault();
      ui.searchOpen = true;
    }
  }
</script>

<svelte:window onkeydown={keydown} />

<header class="topbar" class:home={section === 'home'}>
  <div class="bar">
    {#if up}
      <a class="back phone-only" href={href(up)} aria-label="Back"><ChevronLeft size={22} /></a>
    {/if}
    <a class="brand" href={href({ name: 'home' })} aria-label="Rx7 home">
      <Mark size={26} />
      <span class="word">Rx7</span>
    </a>
    <nav class="menu desk-only" aria-label="Main">
      {#each nav as n (n.id)}
        <a href={href(n.route)} class:on={section === n.id} aria-current={section === n.id ? 'page' : undefined}>{n.label}</a>
      {/each}
    </nav>
    <span class="phone-title phone-only">{trail.at(-1)?.label ?? ''}</span>
    <div class="right">
      <button class="find desk-only" onclick={() => (ui.searchOpen = true)}>
        <Search size={15} />
        <span>Search everything</span>
        <kbd>{isMac ? '⌘' : 'Ctrl'} K</kbd>
      </button>
      <span class="desk-only"><SyncBadge /></span>
      <span class="phone-only"><SyncBadge compact /></span>
      {#if app.platform?.canClaude}
        <button class="btn icon ghost" class:lit={ui.chatOpen} onclick={() => (ui.chatOpen = !ui.chatOpen)} aria-label="Ask Claude" title="Ask Claude about what is on screen">
          <MessageSquare size={18} />
        </button>
      {/if}
      <a class="btn icon ghost desk-only" href={href({ name: 'settings' })} aria-label="Settings" title="Settings"><Settings size={18} /></a>
    </div>
  </div>
  {#if trail.length > 1}
    <nav class="crumbs" aria-label="Breadcrumb">
      {#each trail as c, i (i)}
        {#if i}<ChevronRight size={13} class="sep" />{/if}
        {#if c.route && i < trail.length - 1}
          <a href={href(c.route)}>{c.label}</a>
        {:else}
          <span aria-current="page">{c.label}</span>
        {/if}
      {/each}
    </nav>
  {/if}
</header>

<main class:with-chat={ui.chatOpen}>
  {@render children()}
</main>

<nav class="tabbar phone-only" aria-label="Main">
  {#each nav as n (n.id)}
    <a href={href(n.route)} class:on={section === n.id}><n.icon size={22} strokeWidth={1.8} /><span>{n.label}</span></a>
  {/each}
  <a href={href({ name: 'search', q: '' })} class:on={section === 'search'}><Search size={22} strokeWidth={1.8} /><span>Search</span></a>
  <a href={href({ name: 'settings' })} class:on={section === 'settings'}><Settings size={22} strokeWidth={1.8} /><span>Settings</span></a>
</nav>

<style>
  .topbar {
    position: sticky;
    top: 0;
    z-index: 30;
    background: color-mix(in oklab, var(--bg) 82%, transparent);
    backdrop-filter: saturate(1.4) blur(14px);
    border-bottom: 1px solid var(--line-soft);
    padding-top: env(safe-area-inset-top);
  }
  .topbar.home {
    background: color-mix(in oklab, var(--bg) 40%, transparent);
    border-bottom-color: transparent;
  }
  .bar {
    display: flex;
    align-items: center;
    gap: 18px;
    height: 56px;
    max-width: var(--page);
    margin: 0 auto;
    padding: 0 var(--gutter);
  }
  .brand {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    color: var(--foam);
  }
  .word {
    font-weight: 720;
    font-size: 18px;
    letter-spacing: 0.01em;
  }
  .menu {
    display: flex;
    gap: 4px;
    margin-left: 8px;
  }
  .menu a {
    position: relative;
    padding: 8px 12px;
    border-radius: var(--r-2);
    color: var(--text-2);
    font-weight: 540;
    font-size: 14.5px;
  }
  .menu a:hover {
    color: var(--foam);
    background: var(--surface-2);
  }
  .menu a.on {
    color: var(--foam);
  }
  .menu a.on::after {
    content: '';
    position: absolute;
    left: 12px;
    right: 12px;
    bottom: -9px;
    height: 2px;
    border-radius: 2px;
    background: var(--ember);
  }
  .right {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .find {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    height: 34px;
    width: 280px;
    padding: 0 8px 0 12px;
    border-radius: var(--r-2);
    border: 1px solid var(--line);
    background: var(--bg-raise);
    color: var(--text-3);
    font-size: 13.5px;
  }
  .find:hover {
    border-color: var(--sky);
    color: var(--text-2);
  }
  .find span {
    flex: 1;
    text-align: left;
  }
  kbd {
    font-family: var(--mono);
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 5px;
    border: 1px solid var(--line);
    color: var(--text-3);
  }
  .lit {
    color: var(--ember) !important;
    background: var(--accent-soft) !important;
  }
  .crumbs {
    display: flex;
    align-items: center;
    gap: 4px;
    max-width: var(--page);
    margin: 0 auto;
    padding: 0 var(--gutter) 10px;
    font-size: 13px;
    color: var(--text-3);
    white-space: nowrap;
    overflow-x: auto;
    scrollbar-width: none;
  }
  .crumbs a {
    color: var(--text-3);
  }
  .crumbs a:hover {
    color: var(--foam);
  }
  .crumbs [aria-current] {
    color: var(--text-2);
  }
  .crumbs :global(.sep) {
    color: var(--text-4);
    flex: none;
  }
  main {
    min-height: calc(100dvh - var(--topbar));
    transition: padding-right var(--t) var(--ease);
  }
  @media (min-width: 1100px) {
    main.with-chat {
      padding-right: 420px;
    }
  }

  .tabbar {
    position: fixed;
    z-index: 30;
    left: 0;
    right: 0;
    bottom: 0;
    height: var(--tabbar);
    padding-bottom: env(safe-area-inset-bottom);
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    background: color-mix(in oklab, var(--bg) 88%, transparent);
    backdrop-filter: blur(16px);
    border-top: 1px solid var(--line-soft);
  }
  .tabbar a {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 3px;
    color: var(--text-3);
    font-size: 11px;
    font-weight: 560;
  }
  .tabbar a.on {
    color: var(--foam);
  }
  .tabbar a.on :global(svg) {
    color: var(--ember);
  }
  .back {
    display: inline-flex;
    margin-left: -8px;
    color: var(--text-2);
    padding: 6px;
  }
  .phone-title {
    flex: 1;
    min-width: 0;
    font-weight: 620;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .phone-only {
    display: none;
  }
  @media (max-width: 759px) {
    .desk-only {
      display: none !important;
    }
    .phone-only {
      display: revert;
    }
    .tabbar.phone-only {
      display: grid;
    }
    .bar {
      gap: 10px;
      height: 52px;
    }
    .brand .word {
      display: none;
    }
    .topbar:not(.home) .brand {
      display: none;
    }
    .crumbs {
      padding-bottom: 8px;
      font-size: 12px;
    }
    .right {
      gap: 4px;
    }
  }
</style>

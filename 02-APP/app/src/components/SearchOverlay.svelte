<script lang="ts">
  import SearchBox from './SearchBox.svelte';
  import { ui } from '../lib/ui.svelte';

  let query = $state('');

  function keydown(e: KeyboardEvent) {
    if (e.key === 'Escape') ui.searchOpen = false;
  }
</script>

<svelte:window onkeydown={keydown} />

<div class="scrim" onclick={() => (ui.searchOpen = false)} role="presentation"></div>
<div class="sheet card" role="dialog" aria-modal="true" aria-label="Search">
  <SearchBox bind:query onpick={() => (ui.searchOpen = false)} />
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
    top: 9vh;
    left: 50%;
    transform: translateX(-50%);
    width: min(760px, calc(100vw - 32px));
    height: min(620px, 78vh);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--surface);
    box-shadow: var(--shadow-3);
    animation: rise var(--t) var(--ease);
  }
</style>

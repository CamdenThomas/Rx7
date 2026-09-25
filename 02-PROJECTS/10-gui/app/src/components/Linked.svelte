<!-- A cell's text with each web address a link, opened outside the app (manual.ts pieces). -->
<script lang="ts">
  import { app } from '../lib/app.svelte';
  import { pieces } from '../lib/manual';

  let { text }: { text: string } = $props();

  function go(e: MouseEvent, url: string) {
    e.preventDefault();
    app.platform?.open(url);
  }
</script>

{#each pieces(text) as p, i (i)}{#if p.url}<a href={p.url} onclick={(e) => go(e, p.url ?? '')}>{p.text}</a>{:else}{p.text}{/if}{/each}
